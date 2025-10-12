"""
Search endpoint for querying prediction market events
"""

import numpy as np
import structlog
from fastapi import APIRouter, Depends, HTTPException
from openai import AsyncOpenAI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api.models import EventResult, SearchRequest, SearchResponse, SearchType
from api.reranker import rerank_results
from shared.config import settings
from shared.database import get_db
from shared.entities import Platform

router = APIRouter(tags=["search"])
logger = structlog.get_logger()

# Initialize OpenAI client for semantic search
openai_client = AsyncOpenAI(api_key=settings.openai_api_key)


async def _search_bm25(query: str, limit: int, db: AsyncSession) -> list[EventResult]:
    """
    Perform BM25 full-text search using ParadeDB.

    Returns results ranked by keyword relevance.
    """
    query_sql = text("""
        SELECT
            platform,
            platform_id,
            search_text,
            paradedb.score(id) as rank
        FROM event
        WHERE search_text @@@ :query
        ORDER BY rank DESC
        LIMIT :limit
    """)

    result = await db.execute(query_sql, {"query": query, "limit": limit})
    rows = result.fetchall()

    return [
        EventResult(
            platform=Platform(row.platform),
            platform_id=row.platform_id,
            search_text=row.search_text,
            confidence=float(row.rank),
        )
        for row in rows
    ]


async def _search_semantic(
    query: str, limit: int, db: AsyncSession
) -> list[EventResult]:
    """
    Perform semantic search using pgai embeddings and pgvector.

    Returns results ranked by semantic similarity (cosine distance).
    Requires the pgai vectorizer to be running and embeddings to be generated.
    """
    # Generate embedding for the query using OpenAI
    # Using 512 dimensions for better cost/performance (only ~1% accuracy drop vs 1536)
    try:
        response = await openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=query,
            encoding_format="float",
            dimensions=512,
        )
        embedding = np.array(response.data[0].embedding)
    except Exception as e:
        logger.error("Failed to generate query embedding", error=str(e))
        raise HTTPException(
            status_code=500, detail="Failed to generate query embedding"
        ) from e

    # Query the event_embedding view created by pgai vectorizer
    # Using cosine distance operator (<=>) from pgvector
    # Format embedding as PostgreSQL vector literal string for asyncpg
    embedding_str = "[" + ",".join(str(x) for x in embedding.tolist()) + "]"

    # Get best chunk per event, sorted by relevance, limited to requested amount
    query_sql = text(f"""
        WITH ranked_chunks AS (
            SELECT DISTINCT ON (e.id)
                e.platform,
                e.platform_id,
                e.search_text,
                ee.embedding <=> '{embedding_str}'::vector as rank
            FROM event_embedding ee
            JOIN event e ON e.id = ee.id
            ORDER BY e.id, ee.embedding <=> '{embedding_str}'::vector ASC
        )
        SELECT platform, platform_id, search_text, rank
        FROM ranked_chunks
        ORDER BY rank ASC
        LIMIT :limit
    """)

    result = await db.execute(query_sql, {"limit": limit})
    rows = result.fetchall()

    return [
        EventResult(
            platform=Platform(row.platform),
            platform_id=row.platform_id,
            search_text=row.search_text,
            confidence=float(row.rank),
        )
        for row in rows
    ]


async def _search_hybrid(query: str, limit: int, db: AsyncSession) -> list[EventResult]:
    """
    Perform hybrid search combining BM25 and semantic results.

    Returns limit results from each method (total 2x limit) for re-ranking.
    Marks each result with its source for transparency.
    """
    # Execute both searches concurrently
    import asyncio

    results = await asyncio.gather(
        _search_bm25(query, limit, db),
        _search_semantic(query, limit, db),
        return_exceptions=True,
    )

    # Handle errors from either search
    bm25_results: list[EventResult] = []
    semantic_results: list[EventResult] = []

    if isinstance(results[0], Exception):
        logger.warning("BM25 search failed in hybrid mode", error=str(results[0]))
    elif isinstance(results[0], list):
        bm25_results = results[0]

    if isinstance(results[1], Exception):
        logger.warning("Semantic search failed in hybrid mode", error=str(results[1]))
    elif isinstance(results[1], list):
        semantic_results = results[1]

    # Combine results (syntactic first, then semantic)
    return bm25_results + semantic_results


@router.post("/search", response_model=SearchResponse)
async def search_events(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),
) -> SearchResponse:
    """
    Search prediction market events.

    - **syntactic**: Keyword-based search (fast, exact matching)
    - **semantic**: AI-powered meaning-based search
    - **hybrid**: Best of both worlds (default, recommended)

    All results are automatically re-ranked using AI confidence scoring.
    Only high-confidence matches (>= 50%) are returned, so you may receive
    fewer results than requested.

    Returns events ranked by confidence score (0.0-1.0).
    """
    try:
        # Route to appropriate search implementation
        if request.search_type == SearchType.SYNTACTIC:
            results = await _search_bm25(request.query, request.limit, db)
        elif request.search_type == SearchType.SEMANTIC:
            results = await _search_semantic(request.query, request.limit, db)
        elif request.search_type == SearchType.HYBRID:
            results = await _search_hybrid(request.query, request.limit, db)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown search type: {request.search_type}",
            )

        # Apply LLM reranking to filter low-confidence results
        if len(results) >= 1:
            reranked_results = await rerank_results(
                query=request.query,
                results=results,
                min_score=0.5,  # Only keep results with >= 50% confidence
            )
            final_results = reranked_results[: request.limit]
        else:
            final_results = results

        logger.info(
            "Search completed",
            query=request.query,
            search_type=request.search_type,
            initial_results=len(results),
            final_results=len(final_results),
        )

        return SearchResponse(
            query=request.query,
            results=final_results,
            total=len(final_results),
            search_type=request.search_type.value,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Search failed", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Search failed") from e

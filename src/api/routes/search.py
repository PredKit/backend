"""
Search endpoint for querying prediction market events
"""

import structlog
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api.models import EventResult, SearchRequest, SearchResponse
from shared.database import get_db
from shared.entities import Platform

router = APIRouter(tags=["search"])
logger = structlog.get_logger()


@router.post("/search", response_model=SearchResponse)
async def search_events(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),
) -> SearchResponse:
    """
    Search prediction market events using BM25 full-text search.

    Returns events ranked by relevance to the query.
    """
    try:
        # BM25 search query using pg_search
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

        result = await db.execute(
            query_sql,
            {"query": request.query, "limit": request.limit},
        )
        rows = result.fetchall()

        # Convert to response models
        results = [
            EventResult(
                platform=Platform(row.platform),
                platform_id=row.platform_id,
                search_text=row.search_text,
                rank=float(row.rank),
            )
            for row in rows
        ]

        logger.info(
            "Search completed",
            query=request.query,
            results_count=len(results),
        )

        return SearchResponse(
            query=request.query,
            results=results,
            total=len(results),
        )

    except Exception as e:
        logger.error("Search failed", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Search failed") from e

"""
Request and response models for API endpoints
"""

from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field

from shared.entities import Platform


class SearchType(str, Enum):
    """Search algorithm type"""

    BM25 = "bm25"  # Full-text search using ParadeDB BM25
    SEMANTIC = "semantic"  # Vector similarity using pgai embeddings
    HYBRID = "hybrid"  # Both BM25 and semantic (for re-ranking)


class SearchRequest(BaseModel):
    """Search request payload"""

    query: Annotated[
        str,
        Field(
            min_length=1,
            max_length=500,
            description="Search query text",
            examples=["Trump election"],
        ),
    ]
    limit: Annotated[
        int,
        Field(
            ge=1,
            le=100,
            description="Maximum number of results to return",
        ),
    ] = 10
    search_type: Annotated[
        SearchType,
        Field(
            description=(
                "Search algorithm: 'bm25' for keyword search, 'semantic' "
                "for meaning-based search, 'hybrid' for both (returns 2x "
                "limit for re-ranking)"
            ),
        ),
    ] = SearchType.BM25


class EventResult(BaseModel):
    """Single event search result"""

    platform: Annotated[Platform, Field(description="Platform (kalshi or polymarket)")]
    platform_id: Annotated[str, Field(description="Unique ID on the platform")]
    search_text: Annotated[str, Field(description="Searchable text content")]
    rank: Annotated[
        float,
        Field(
            description=(
                "Relevance score (BM25 rank for keyword search, or cosine "
                "distance for semantic search)"
            )
        ),
    ]
    source: Annotated[
        str | None,
        Field(
            description="Result source: 'bm25' or 'semantic' (only for hybrid search)",
            default=None,
        ),
    ] = None


class SearchResponse(BaseModel):
    """Search response with results"""

    query: Annotated[str, Field(description="Original search query")]
    results: Annotated[list[EventResult], Field(description="Search results")]
    total: Annotated[int, Field(description="Total number of results returned")]
    search_type: Annotated[
        str, Field(description="Search type used: bm25, semantic, or hybrid")
    ]


class HealthResponse(BaseModel):
    """Health check response"""

    status: Annotated[str, Field(description="Service status")]
    version: Annotated[str, Field(description="API version")]

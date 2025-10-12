"""
Request and response models for API endpoints
"""

from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field

from shared.entities import Platform


class SearchType(str, Enum):
    """Search algorithm type"""

    SYNTACTIC = "syntactic"  # Keyword-based search
    SEMANTIC = "semantic"  # Meaning-based search using AI embeddings
    HYBRID = "hybrid"  # Both syntactic and semantic combined


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
            le=10,
            description="Maximum number of results to return",
        ),
    ] = 10
    search_type: Annotated[
        SearchType,
        Field(
            description=(
                "Search type: 'syntactic' for keyword matching, 'semantic' "
                "for meaning-based search, 'hybrid' for best results (default)"
            ),
        ),
    ] = SearchType.HYBRID


class EventResult(BaseModel):
    """Single event search result"""

    platform: Annotated[Platform, Field(description="Platform (kalshi or polymarket)")]
    platform_id: Annotated[str, Field(description="Unique ID on the platform")]
    search_text: Annotated[str, Field(description="Searchable text content")]
    rank: Annotated[
        float,
        Field(
            description="Relevance confidence score (0.0-1.0, higher is more relevant)"
        ),
    ]


class SearchResponse(BaseModel):
    """Search response with results"""

    query: Annotated[str, Field(description="Original search query")]
    results: Annotated[list[EventResult], Field(description="Search results")]
    total: Annotated[int, Field(description="Total number of results returned")]
    search_type: Annotated[
        str, Field(description="Search type used: syntactic, semantic, or hybrid")
    ]


class HealthResponse(BaseModel):
    """Health check response"""

    status: Annotated[str, Field(description="Service status")]
    version: Annotated[str, Field(description="API version")]

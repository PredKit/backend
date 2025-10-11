"""
Discovery endpoints for LLMs and crawlers

Implements llms.txt standard and other discovery mechanisms:
- /llms.txt: LLM-friendly discovery (llmstxt.org standard)
- /robots.txt: Crawler control
- /ai.txt: Alternative AI discovery format
- /: API metadata

These endpoints are hidden from API docs since they're metadata/discovery,
not part of the core API functionality.
"""

from fastapi import APIRouter, Response

router = APIRouter(tags=["discovery"], include_in_schema=False)


@router.get("/")
async def root():
    """
    API information and documentation links.

    This API allows searching prediction markets across multiple platforms
    including Polymarket and Kalshi. Use the /v0/search endpoint to query
    events by natural language search terms.
    """
    return {
        "name": "PredKit API",
        "version": "0.1.0",
        "status": "beta",
        "description": "Search prediction markets across platforms (Polymarket, Kalshi)",
        "purpose": "Provides programmatic access to search prediction market events using natural language queries with BM25 full-text search",
        "documentation": {
            "interactive": "https://api.predkit.com/docs",
            "alternative": "https://api.predkit.com/redoc",
            "openapi_schema": "https://api.predkit.com/openapi.json",
            "llms": "https://api.predkit.com/llms.txt",
        },
        "endpoints": {
            "health": {
                "path": "/health",
                "method": "GET",
                "description": "Health check endpoint",
            },
            "search": {
                "path": "/v0/search",
                "method": "POST",
                "description": "Search prediction market events by query text",
                "example": {
                    "query": "Trump election",
                    "limit": 10,
                },
            },
        },
        "usage_for_llms": "Use POST /v0/search with JSON body containing 'query' (string) and optional 'limit' (integer, max 100) to search prediction markets. Returns ranked results with platform, platform_id, search_text, and relevance rank.",
    }


@router.get("/llms.txt", response_class=Response)
async def llms_txt():
    """
    LLM discovery file following llmstxt.org standard.

    Provides structured information for LLMs to understand and use the API.
    """
    content = """# PredKit API

> A REST API for searching prediction markets across multiple platforms (Polymarket, Kalshi) using natural language queries with BM25 full-text search ranking.

## Key Information

- **Base URL**: https://api.predkit.com
- **API Version**: v0 (beta)
- **Authentication**: None required (public API)
- **Rate Limits**: 10 requests/second per IP (burst: 20)
- **CORS**: Enabled for all origins
- **Response Format**: JSON

## How to Use

The primary endpoint is `POST /v0/search` which accepts:
- `query` (string, required): Natural language search query (e.g., "Trump election 2024")
- `limit` (integer, optional): Max results to return (default: 10, max: 100)

Returns ranked results with:
- `platform`: Source platform (polymarket, kalshi)
- `platform_id`: Unique event ID on that platform
- `search_text`: Searchable description of the event
- `rank`: BM25 relevance score (higher = more relevant)

## API Documentation

- [OpenAPI Schema](https://api.predkit.com/openapi.json): Complete API specification
- [Interactive Docs](https://api.predkit.com/docs): Swagger UI for testing
- [ReDoc](https://api.predkit.com/redoc): Alternative documentation view

## Examples

**Basic Search:**
```bash
curl -X POST https://api.predkit.com/v0/search \\
  -H "Content-Type: application/json" \\
  -d '{"query": "Trump election 2024", "limit": 10}'
```

**Response Structure:**
```json
{
  "query": "Trump election 2024",
  "total": 10,
  "results": [
    {
      "platform": "polymarket",
      "platform_id": "abc123",
      "search_text": "Will Trump win the 2024 election?",
      "rank": 8.5
    }
  ]
}
```

## Optional

- [Health Endpoint](https://api.predkit.com/health): Simple health check for monitoring
- [Robots.txt](https://api.predkit.com/robots.txt): Crawler policies
"""
    return Response(content=content, media_type="text/plain")


@router.get("/robots.txt", response_class=Response)
async def robots_txt():
    """
    Block traditional web crawlers but allow AI crawlers.
    """
    content = """# PredKit API - Crawler Rules

# Block traditional web crawlers (save bandwidth, prevent indexing)
User-agent: *
Disallow: /

# Allow AI/LLM crawlers for API discovery
User-agent: GPTBot
Allow: /
Allow: /llms.txt
Allow: /docs
Allow: /openapi.json

User-agent: ChatGPT-User
Allow: /
Allow: /llms.txt
Allow: /docs
Allow: /openapi.json

User-agent: Claude-Web
Allow: /
Allow: /llms.txt
Allow: /docs
Allow: /openapi.json

User-agent: anthropic-ai
Allow: /
Allow: /llms.txt
Allow: /docs
Allow: /openapi.json

User-agent: cohere-ai
Allow: /
Allow: /llms.txt
Allow: /docs
Allow: /openapi.json

User-agent: PerplexityBot
Allow: /
Allow: /llms.txt
Allow: /docs
Allow: /openapi.json

User-agent: GoogleOther
Allow: /
Allow: /llms.txt
Allow: /docs
Allow: /openapi.json

User-agent: Google-Extended
Allow: /
Allow: /llms.txt
Allow: /docs
Allow: /openapi.json
"""
    return Response(content=content, media_type="text/plain")


@router.get("/ai.txt", response_class=Response)
async def ai_txt():
    """
    Alternative AI discovery file format.
    """
    content = """# PredKit API - AI Discovery

This API provides search capabilities for prediction markets across Polymarket and Kalshi.

## Primary Endpoint

POST /v0/search
- Parameters: 
  - query (string, required): Natural language search query
  - limit (integer, optional): Max results (default: 10, max: 100)
- Returns: Ranked search results with platform, platform_id, search_text, and BM25 rank score

## Documentation

- OpenAPI: https://api.predkit.com/openapi.json
- Interactive Docs: https://api.predkit.com/docs
- LLM-friendly: https://api.predkit.com/llms.txt

## Usage Guidelines

- Rate limit: 10 requests/second per IP (burst: 20)
- CORS: Enabled for all origins
- Authentication: Not required (public API)
- Response format: JSON

## Example

POST /v0/search
Content-Type: application/json

{
  "query": "Trump election 2024",
  "limit": 10
}

Response:
{
  "query": "Trump election 2024",
  "total": 10,
  "results": [
    {
      "platform": "polymarket",
      "platform_id": "abc123",
      "search_text": "Will Trump win the 2024 election?",
      "rank": 8.5
    }
  ]
}
"""
    return Response(content=content, media_type="text/plain")

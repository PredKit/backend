"""
FastAPI application for PredKit search API
"""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import discovery, health, search

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
    """Lifespan context manager for startup/shutdown events"""
    logger.info("Starting PredKit API")
    yield
    logger.info("Shutting down PredKit API")


# Create FastAPI app
app = FastAPI(
    title="PredKit API",
    description="""
    Search prediction markets across multiple platforms using natural language queries.
    
    ## Features
    - **Full-text search** using BM25 ranking algorithm
    - **Multi-platform** coverage (Polymarket, Kalshi)
    - **Fast & simple** REST API
    - **No authentication** required
    
    ## For LLMs
    This API is designed to be LLM-friendly. Use the `/v0/search` endpoint with natural 
    language queries to find prediction market events. The API returns ranked results 
    with platform information and relevance scores.
    
    ## Rate Limits
    - 10 requests/second per IP
    - Burst: 20 requests
    
    ## Example Usage
    ```bash
    curl -X POST https://api.predkit.com/v0/search \\
      -H "Content-Type: application/json" \\
      -d '{"query": "Trump election 2024", "limit": 10}'
    ```
    """,
    version="0.1.0",
    lifespan=lifespan,
    # Additional metadata for LLM discovery
    contact={
        "name": "PredKit",
        "url": "https://api.predkit.com",
    },
    license_info={
        "name": "Public API",
    },
    servers=[
        {
            "url": "https://api.predkit.com",
            "description": "Production server",
        }
    ],
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for public API
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
# Discovery endpoints (/, /llms.txt, /robots.txt, /ai.txt)
app.include_router(discovery.router)

# Health endpoint (unversioned for monitoring)
app.include_router(health.router)

# API v0 routes (versioned endpoints)
app.include_router(search.router, prefix="/v0")

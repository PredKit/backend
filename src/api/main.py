"""
FastAPI application for PredKit search API
"""

from contextlib import asynccontextmanager

import structlog
from alembic.config import Config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from alembic import command

from .routes import discovery, health, search

logger = structlog.get_logger()


def run_migrations() -> None:
    """Run database migrations using Alembic"""
    logger.info("Running database migrations...")
    alembic_cfg = Config("alembic.ini")
    # Don't set URL here - let alembic/env.py handle it to avoid ConfigParser issues
    alembic_cfg.attributes["configure_logger"] = False  # Use our logger
    command.upgrade(alembic_cfg, "head")
    logger.info("Database migrations completed")


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
    """Lifespan context manager for startup/shutdown events"""
    logger.info("Starting PredKit API")

    # Run migrations on startup
    try:
        run_migrations()
    except Exception as e:
        logger.error("Failed to run migrations", error=str(e), exc_info=True)
        raise

    yield
    logger.info("Shutting down PredKit API")


# Create FastAPI app
app = FastAPI(
    title="PredKit API",
    description="""
    Search prediction markets across multiple platforms using natural language queries.
    
    ## Features
    - **Search** with syntactic, semantic, and hybrid modes
    - **Multi-platform** coverage (Polymarket, Kalshi)
    - **Confidence scoring** with automatic result filtering
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

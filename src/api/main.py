"""
FastAPI application for PredKit search API
"""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import health, search

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
    description="Search prediction markets across platforms",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware (adjust origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(health.router)
app.include_router(search.router)

"""
Cloud Function entry point for market indexing

Triggered on a schedule (e.g., hourly) via Cloud Scheduler HTTP target.
"""

import asyncio
from typing import Any

import functions_framework
import structlog
from flask import Request

from shared.entities import Platform

from .indexer import ALL_PAGES, index_events

logger = structlog.get_logger()


@functions_framework.http  # type: ignore[misc]
def index_markets_function(request: Request) -> tuple[dict[str, Any], int]:
    """
    HTTP Cloud Function entry point for indexing markets.

    Triggered by Cloud Scheduler via HTTP.

    Args:
        request: Flask request object (unused, triggered by scheduler)

    Returns:
        Tuple of (response dict, status code)
    """
    logger.info("Starting market indexing (triggered by scheduler)")

    try:
        # Run indexer - fetch all pages from all platforms
        all_platforms = [Platform.KALSHI, Platform.POLYMARKET]
        results = asyncio.run(
            index_events(platforms=all_platforms, max_pages=ALL_PAGES)
        )

        # Calculate summary
        total_inserted = sum(stats.inserted for stats in results.values())
        total_updated = sum(stats.updated for stats in results.values())
        total_errors = sum(stats.errors for stats in results.values())

        logger.info(
            "Market indexing completed",
            total_inserted=total_inserted,
            total_updated=total_updated,
            total_errors=total_errors,
        )

        # Return success response (convert Platform enum to string for JSON)
        return {
            "status": "success",
            "total_inserted": total_inserted,
            "total_updated": total_updated,
            "total_errors": total_errors,
            "platforms": {
                platform.value: stats.model_dump()
                for platform, stats in results.items()
            },
        }, 200

    except Exception as e:
        logger.error("Market indexing failed", error=str(e), exc_info=True)
        return {
            "status": "error",
            "error": str(e),
        }, 500

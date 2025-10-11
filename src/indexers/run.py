#!/usr/bin/env python3
"""
Production indexer entrypoint for Cloud Run Jobs
Runs hourly to collect new events from all platforms
"""

import asyncio
import sys
from pathlib import Path

import structlog

# Add src to path (go up two levels from src/indexers/run.py to get to backend/)
sys.path.insert(0, str(Path(__file__).parent.parent))

from indexers.indexer import ALL_PAGES, index_events
from shared.entities import Platform

logger = structlog.get_logger()


async def main():
    """Run indexer for all platforms (production mode)"""
    logger.info("Starting production indexer")

    try:
        # Index all platforms, all pages
        # The indexer will automatically stop when it encounters existing events
        # due to the logic in indexer.py lines 115-123
        results = await index_events(
            platforms=[Platform.KALSHI, Platform.POLYMARKET],
            max_pages=ALL_PAGES,  # Fetch all new events until we hit existing ones
        )

        # Log results
        total_inserted = sum(stats.inserted for stats in results.values())
        total_updated = sum(stats.updated for stats in results.values())
        total_errors = sum(stats.errors for stats in results.values())

        logger.info(
            "Indexer completed",
            total_inserted=total_inserted,
            total_updated=total_updated,
            total_errors=total_errors,
        )

        for platform, stats in results.items():
            logger.info(
                "Platform results",
                platform=platform.value,
                inserted=stats.inserted,
                updated=stats.updated,
                errors=stats.errors,
            )

        # Exit with error code if there were errors
        if total_errors > 0:
            sys.exit(1)

    except Exception as e:
        logger.error("Indexer failed", error=str(e), exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

"""Event indexer - Collects events from platforms and stores them in database"""

import asyncio

import structlog
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import AsyncSessionLocal
from shared.entities import Event as EventEntity
from shared.entities import Platform
from shared.models.event import Event as EventModel

from .kalshi.collector import KalshiCollector
from .polymarket.collector import PolymarketCollector

logger = structlog.get_logger()

ALL_PAGES = -1


class IndexStats(BaseModel):
    """Statistics from indexing operation"""

    inserted: int
    updated: int
    errors: int


class EventIndexer:
    """Indexes events from all platforms into the database"""

    def __init__(self):
        self.collectors = {
            Platform.KALSHI: KalshiCollector,
            Platform.POLYMARKET: PolymarketCollector,
        }

    async def index_all_platforms(
        self,
        platforms: list[Platform],
        max_pages: int = 1,
    ) -> dict[Platform, IndexStats]:
        """Index markets from specified platforms concurrently"""
        valid_platforms = [p for p in platforms if p in self.collectors]
        if len(valid_platforms) < len(platforms):
            unknown = [p for p in platforms if p not in self.collectors]
            for p in unknown:
                logger.warning(f"Unknown platform: {p.value}", platform=p.value)

        tasks = [self._index_platform_safe(p, max_pages) for p in valid_platforms]
        results_list = await asyncio.gather(*tasks)

        return dict(zip(valid_platforms, results_list, strict=False))

    async def _index_platform_safe(
        self, platform: Platform, max_pages: int
    ) -> IndexStats:
        """Wrapper around index_platform that catches exceptions"""
        logger.info("Starting indexing for platform", platform=platform.value)

        try:
            stats = await self.index_platform(platform, max_pages)
            logger.info(
                "Completed indexing for platform",
                platform=platform.value,
                inserted=stats.inserted,
                updated=stats.updated,
                errors=stats.errors,
            )
            return stats
        except Exception as e:
            logger.error(
                "Failed to index platform",
                platform=platform.value,
                error=str(e),
                exc_info=True,
            )
            return IndexStats(inserted=0, updated=0, errors=1)

    async def index_platform(
        self, platform: Platform, max_pages: int = 1
    ) -> IndexStats:
        """Index markets from a single platform with per-page batching"""
        collector_class = self.collectors[platform]

        total_inserted = 0
        total_updated = 0
        total_errors = 0
        page_num = 0

        async with collector_class() as collector:
            async for events_page in collector.collect_events_paginated(
                max_pages=max_pages
            ):
                page_num += 1

                async with AsyncSessionLocal() as session:
                    page_stats = await self._insert_new_events(session, events_page)
                    await session.commit()

                total_inserted += page_stats.inserted
                total_updated += page_stats.updated
                total_errors += page_stats.errors

                logger.info(
                    "Indexed page",
                    platform=platform.value,
                    page=page_num,
                    inserted=page_stats.inserted,
                    updated=page_stats.updated,
                )

                # Stop if we encountered any existing events
                # Assumes API returns newest-first, so rest are also existing
                if page_stats.updated > 0:
                    logger.info(
                        "Encountered existing events, stopping",
                        platform=platform.value,
                        updated=page_stats.updated,
                    )
                    break

        logger.info(
            "Completed indexing",
            platform=platform.value,
            pages=page_num,
            inserted=total_inserted,
            updated=total_updated,
        )

        return IndexStats(
            inserted=total_inserted, updated=total_updated, errors=total_errors
        )

    async def _insert_new_events(
        self, session: AsyncSession, events: list[EventEntity]
    ) -> IndexStats:
        """Insert only new events (skip existing ones to avoid re-embedding)"""
        if not events:
            return IndexStats(inserted=0, updated=0, errors=0)

        from sqlalchemy import tuple_

        # Fetch only the keys of existing events (not full objects)
        event_keys = [(e.platform.value, e.platform_id) for e in events]

        chunk_size = 1000
        existing_keys: set[tuple[str, str]] = set()

        for i in range(0, len(event_keys), chunk_size):
            chunk = event_keys[i : i + chunk_size]
            stmt = select(EventModel.platform, EventModel.platform_id).where(
                tuple_(EventModel.platform, EventModel.platform_id).in_(chunk)
            )
            result = await session.execute(stmt)
            existing_keys.update(tuple(row) for row in result.all())

        # Only insert events that don't exist yet
        to_insert = [
            EventModel(
                platform=e.platform.value,
                platform_id=e.platform_id,
                search_text=e.search_text,
                raw_data=e.raw_data,
            )
            for e in events
            if (e.platform.value, e.platform_id) not in existing_keys
        ]

        if to_insert:
            session.add_all(to_insert)

        return IndexStats(
            inserted=len(to_insert),
            updated=0,  # Never update
            errors=0,
        )


async def index_events(
    platforms: list[Platform], max_pages: int = 1
) -> dict[Platform, IndexStats]:
    """Convenience function to index events from specified platforms"""
    indexer = EventIndexer()
    return await indexer.index_all_platforms(platforms=platforms, max_pages=max_pages)

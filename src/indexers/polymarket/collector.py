"""Polymarket collector"""

from collections.abc import AsyncIterator

import structlog

from indexers.base import BaseCollector
from shared.entities import Event, Platform

from .api import PolymarketAPI
from .schemas import PolymarketEvent

logger = structlog.get_logger()  # pyright: ignore[reportAny]


class PolymarketCollector(BaseCollector):
    """Collect and normalize events from Polymarket"""

    def __init__(self):
        self.api = PolymarketAPI()

    async def collect_events_paginated(
        self, max_pages: int = 1
    ) -> AsyncIterator[list[Event]]:
        """Fetch events page by page, ordered newest-first for incremental indexing"""
        logger.info("Collecting Polymarket events", max_pages=max_pages)

        offset = 0
        limit = 100  # Polymarket events endpoint
        page = 0

        try:
            while True:
                # IMPORTANT: Order by createdAt descending (newest first)
                # This enables incremental indexing - stop when we hit existing
                page_events = await self.api.get_events(
                    limit=limit,
                    offset=offset,
                    order="createdAt",
                    ascending=False,
                )
                page += 1

                unified_events = [self._normalize_event(e) for e in page_events]

                if unified_events:
                    yield unified_events

                if len(page_events) == 0 or len(page_events) < limit:
                    break
                if max_pages > 0 and page >= max_pages:
                    break

                offset += limit

        except Exception as e:
            logger.error("Failed to collect Polymarket events", error=str(e), page=page)

    def _normalize_event(self, event: PolymarketEvent) -> Event:
        """Convert Polymarket event to unified format"""
        search_text = self._build_search_text(event)
        return Event(
            platform=Platform.POLYMARKET,
            platform_id=event.id,
            search_text=search_text,
            raw_data=event.model_dump(mode="json"),
        )

    @staticmethod
    def _build_search_text(event: PolymarketEvent) -> str:
        """Build search text from event data"""
        parts: list[str] = []

        # Event fields
        if event.title:
            parts.append(f"title: {event.title}")
        if event.subtitle:
            parts.append(f"subtitle: {event.subtitle}")
        if event.description:
            parts.append(f"description: {event.description}")
        if event.category:
            parts.append(f"category: {event.category}")
        if event.subcategory:
            parts.append(f"subcategory: {event.subcategory}")

        # Markets within the event
        for market in event.markets:
            if market.question:
                parts.append(f"market: {market.question}")
            if market.description:
                parts.append(f"market_description: {market.description}")
            if market.outcomes:
                parts.append(f"outcomes: {market.outcomes}")
            if market.short_outcomes:
                parts.append(f"short_outcomes: {market.short_outcomes}")
            if market.category:
                parts.append(f"market_category: {market.category}")
            if market.market_type:
                parts.append(f"market_type: {market.market_type}")
            if market.sports_market_type:
                parts.append(f"sports_type: {market.sports_market_type}")
            if market.group_item_title:
                parts.append(f"group: {market.group_item_title}")
            if market.sponsor_name:
                parts.append(f"sponsor: {market.sponsor_name}")

        # Series context
        for series in event.series:
            if series.title:
                parts.append(f"series: {series.title}")
            if series.subtitle:
                parts.append(f"series_subtitle: {series.subtitle}")
            if series.description:
                parts.append(f"series_description: {series.description}")
            if series.series_type:
                parts.append(f"series_type: {series.series_type}")
            # Series tags
            for tag in series.tags:
                if tag.label:
                    parts.append(f"series_tag: {tag.label}")
            # Series categories
            for category in series.categories:
                if category.label:
                    parts.append(f"series_category: {category.label}")

        # Event tags and categories
        for tag in event.tags:
            if tag.label:
                parts.append(f"tag: {tag.label}")
        for category in event.categories:
            if category.label:
                parts.append(f"category: {category.label}")

        return "\n".join(parts).strip()

    async def close(self):
        await self.api.close()

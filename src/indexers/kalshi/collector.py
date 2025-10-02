"""Kalshi collector"""

from collections.abc import AsyncIterator

import structlog

from indexers.base import BaseCollector
from shared.entities import Event, Platform

from .api import KalshiAPI
from .schemas import KalshiEvent, KalshiSeries

logger = structlog.get_logger()  # pyright: ignore[reportAny]


class KalshiCollector(BaseCollector):
    """Collect and normalize events from Kalshi"""

    def __init__(self):
        self.api = KalshiAPI()
        self._series_cache: dict[str, KalshiSeries] = {}

    async def collect_events_paginated(
        self, max_pages: int = 1
    ) -> AsyncIterator[list[Event]]:
        """Fetch events page by page with nested markets"""
        logger.info("Collecting Kalshi events", max_pages=max_pages)

        # Fetch all series upfront to avoid rate limiting
        await self._fetch_all_series()

        cursor: str | None = None
        page = 0
        limit = 200  # Kalshi events endpoint supports max 200

        try:
            while True:
                # IMPORTANT: Kalshi /events returns newest-first by default
                # This enables incremental indexing - stop when we hit existing
                events, cursor = await self.api.get_events(
                    limit=limit, cursor=cursor, with_nested_markets=True
                )
                page += 1

                if events:
                    # Enrich this page of events with series data
                    unified_events = await self._enrich_events(events)
                    yield unified_events

                if len(events) == 0 or len(events) < limit or not cursor:
                    break
                if max_pages > 0 and page >= max_pages:
                    break

        except Exception as e:
            logger.error("Failed to collect Kalshi events", error=str(e), exc_info=True)

    async def _fetch_all_series(self) -> None:
        """Fetch all series upfront and cache them to avoid rate limiting"""
        logger.info("Fetching all Kalshi series")
        cursor: str | None = None
        total_series = 0

        try:
            while True:
                series_list, cursor = await self.api.get_series(
                    limit=1000, cursor=cursor
                )

                # Cache all series by ticker
                for series in series_list:
                    if series.ticker:
                        self._series_cache[series.ticker] = series

                total_series += len(series_list)

                if not cursor or len(series_list) == 0:
                    break

            logger.info("Cached all series", count=total_series)
        except Exception as e:
            logger.error("Failed to fetch all series", error=str(e), exc_info=True)

    async def _enrich_events(self, events: list[KalshiEvent]) -> list[Event]:
        """Enrich events with series data from cache"""
        unified_events: list[Event] = []
        for event in events:
            series_obj = None
            if event.series_ticker:
                series_obj = self._series_cache.get(event.series_ticker)

            unified_event = self._normalize_event(event, series_obj)
            unified_events.append(unified_event)

        return unified_events

    def _normalize_event(
        self,
        event: KalshiEvent,
        series: KalshiSeries | None = None,
    ) -> Event:
        """Convert Kalshi event to unified format"""
        search_text = self._build_search_text(event, series)
        return Event(
            platform=Platform.KALSHI,
            platform_id=event.event_ticker or "",
            search_text=search_text,
            raw_data=event.model_dump(mode="json"),
        )

    @staticmethod
    def _build_search_text(
        event: KalshiEvent,
        series: KalshiSeries | None = None,
    ) -> str:
        """Build search text from event, markets, and series data"""
        parts: list[str] = []

        # Event fields
        if event.title:
            parts.append(f"title: {event.title}")
        if event.sub_title:
            parts.append(f"subtitle: {event.sub_title}")
        if event.category:
            parts.append(f"category: {event.category}")

        # Markets within the event
        for market in event.markets or []:
            if market.title:
                parts.append(f"market: {market.title}")
            if market.subtitle:
                parts.append(f"market_subtitle: {market.subtitle}")
            if market.yes_sub_title:
                parts.append(f"yes: {market.yes_sub_title}")
            if market.no_sub_title:
                parts.append(f"no: {market.no_sub_title}")
            if market.rules_primary:
                parts.append(f"rules: {market.rules_primary}")
            if market.rules_secondary:
                parts.append(f"rules_secondary: {market.rules_secondary}")
            if market.market_type:
                parts.append(f"market_type: {market.market_type}")
            if market.ticker:
                parts.append(f"ticker: {market.ticker}")

        # Series context
        if series:
            if series.title:
                parts.append(f"series: {series.title}")
            if series.category:
                parts.append(f"series_category: {series.category}")
            if series.tags:
                parts.append(f"tags: {' '.join(series.tags)}")

        return "\n".join(parts).strip()

    async def close(self):
        await self.api.close()

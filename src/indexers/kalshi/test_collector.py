"""
Tests for Kalshi collector
"""

import random

import pytest

from shared.entities import Event, Platform

from .collector import KalshiCollector


@pytest.mark.asyncio
async def test_collect_events():
    """Test collecting unified events from Kalshi API (1 page)"""
    async with KalshiCollector() as collector:
        # Collect first page of events
        all_events: list[Event] = []
        async for events_page in collector.collect_events_paginated(max_pages=1):
            all_events.extend(events_page)  # pyright: ignore[reportUnknownMemberType]

        # Assertions
        assert isinstance(all_events, list)
        assert len(all_events) > 0, "Should collect at least 1 event"
        assert len(all_events) <= 200, "Should collect at most 200 events (1 page)"

        # Check event structure (Pydantic already validated types)
        event = random.choice(all_events)
        assert event.platform == Platform.KALSHI
        assert event.platform_id, "Event should have a platform_id"
        assert event.search_text, "Event should have non-empty search_text"
        assert event.raw_data, "Event should have raw_data"

        # Print for manual inspection
        print(f"\n✅ Collected {len(all_events)} unified events\n")
        print(f"Platform: {event.platform.value} | ID: {event.platform_id}\n")
        print("SEARCH TEXT:")
        print(event.search_text[:500])  # First 500 chars

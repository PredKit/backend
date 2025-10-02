"""
Tests for Polymarket collector
"""

import random

import pytest

from shared.entities import Event, Platform

from .collector import PolymarketCollector


@pytest.mark.asyncio
async def test_collect_events():
    """Test collecting unified events from Polymarket API (1 page)"""
    async with PolymarketCollector() as collector:
        # Collect first page of events
        all_events: list[Event] = []
        async for events_page in collector.collect_events_paginated(max_pages=1):
            all_events.extend(events_page)  # pyright: ignore[reportUnknownMemberType]

        # Assertions
        assert isinstance(all_events, list)
        assert len(all_events) > 0, "Should collect at least 1 event"
        assert len(all_events) <= 100, "Should collect at most 100 events (1 page)"

        # Check event structure (Pydantic already validated types)
        event = random.choice(all_events)
        assert event.platform == Platform.POLYMARKET
        assert event.platform_id, "Event should have a platform_id"
        assert event.search_text, "Event should have non-empty search_text"
        assert event.raw_data, "Event should have raw_data"

        # Print for manual inspection
        print(f"\n✅ Collected {len(all_events)} unified events\n")
        print(f"Platform: {event.platform.value} | ID: {event.platform_id}\n")
        print("SEARCH TEXT:")
        print(event.search_text[:500])  # First 500 chars

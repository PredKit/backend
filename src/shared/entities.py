"""
Unified event entity for cross-platform search
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel


class Platform(str, Enum):
    """Source platform"""

    POLYMARKET = "polymarket"
    KALSHI = "kalshi"


class Event(BaseModel):
    """
    Search-optimized event entity.

    An event represents a real-world occurrence that can be traded on
    (e.g., "Who will win the championship?"). Markets are the specific
    betting options within an event (e.g., "Team A wins - Yes/No").

    Design principles:
    - Platform + event_id allow fetching full details from source
    - search_text aggregates ALL textual context for maximum searchability
    - raw_data preserves original API response including all markets
    - Temporal filters (status, dates) applied post-search
    """

    # Identity (immutable)
    platform: Platform
    platform_id: str  # Platform-specific event ID

    # Aggregated search context (includes event + markets + series + metadata)
    search_text: str

    # Raw data from API (stored as JSONB in DB)
    # Includes the event and all its markets
    raw_data: dict[str, Any]

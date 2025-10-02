"""
Event database model for storing prediction market events from all platforms
"""

from typing import Any

from sqlalchemy import Index, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class Event(Base, TimestampMixin):
    """
    Unified event model for cross-platform search.

    An event represents a real-world occurrence (e.g., election, sports game)
    with multiple markets (betting options). Events are the primary search entity.

    Optimized for full-text search using ParadeDB's BM25 indexing.
    """

    __tablename__ = "event"

    # Primary key (used as BM25 key_field)
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Platform + platform_id uniquely identifies each event
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    platform_id: Mapped[str] = mapped_column(String(255), nullable=False)

    # Aggregated search text (includes event + all markets + metadata)
    search_text: Mapped[str] = mapped_column(Text, nullable=False)

    # Raw data from API (stored as JSONB for flexibility)
    raw_data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    # Constraints and indexes
    __table_args__ = (
        # Ensure (platform, platform_id) is unique
        UniqueConstraint("platform", "platform_id", name="uq_event_platform_id"),
        # Index on created_at for sorting recent events
        Index("ix_event_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        platform_str = self.platform
        platform_id_str = self.platform_id
        return f"<Event(id={self.id}, platform={platform_str}, platform_id={platform_id_str})>"  # noqa: E501

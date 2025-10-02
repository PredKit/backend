"""
Polymarket API client (thin wrapper around GAMMA API)

GAMMA API Rate Limits:
┌────────────────────────────────┬────────────────────┬──────────────────────────────────────────────────┐
│ Endpoint                       │ Limit              │ Notes                                            │
├────────────────────────────────┼────────────────────┼──────────────────────────────────────────────────┤
│ GAMMA (General)                │ 750 requests / 10s │ Throttle requests over the maximum configured    │
│                                │                    │ rate                                             │
├────────────────────────────────┼────────────────────┼──────────────────────────────────────────────────┤
│ GAMMA /markets                 │ 100 requests / 10s │ Throttle requests over the maximum configured    │
│                                │                    │ rate                                             │
└────────────────────────────────┴────────────────────┴──────────────────────────────────────────────────┘

See: https://docs.polymarket.com/quickstart/introduction/rate-limits#gamma-api-rate-limits
"""  # noqa: E501

from typing import ClassVar, Self

import httpx
import structlog

from .schemas import (
    PolymarketEvent,
    PolymarketEventsParams,
    PolymarketMarket,
    PolymarketMarketsParams,
)

logger = structlog.get_logger()  # pyright: ignore[reportAny]


class PolymarketAPI:
    """Low-level Polymarket API client"""

    BASE_URL: ClassVar[str] = "https://gamma-api.polymarket.com"

    def __init__(self):
        self.client: httpx.AsyncClient = httpx.AsyncClient(timeout=30.0)

    async def get_markets(
        self,
        limit: int = 100,
        offset: int | None = None,
        order: str | None = None,
        ascending: bool | None = None,
    ) -> list[PolymarketMarket]:
        """
        Fetch markets from /markets endpoint.

        IMPORTANT: Results should be ordered newest-first (descending by createdAt)
        to support incremental indexing. This allows us to stop pagination when
        we encounter existing markets.

        Args:
            limit: Number of markets per request (default 100)
            offset: Offset for pagination (optional)
            order: Field to order by (e.g., "createdAt")
            ascending: Sort ascending (True) or descending (False, default)

        Returns:
            List of PolymarketMarket objects (newest first)
        """
        params = PolymarketMarketsParams(
            limit=limit, offset=offset, order=order, ascending=ascending
        )

        response = await self.client.get(
            f"{self.BASE_URL}/markets",
            params=params.model_dump(exclude_none=True),
        )
        response.raise_for_status()
        raw_markets = response.json()

        return [PolymarketMarket.model_validate(m) for m in raw_markets]

    async def get_events(
        self,
        limit: int = 100,
        offset: int | None = None,
        order: str | None = None,
        ascending: bool | None = None,
    ) -> list[PolymarketEvent]:
        """
        Fetch events from /events/pagination endpoint.

        IMPORTANT: Results should be ordered newest-first (descending by createdAt)
        to support incremental indexing. This allows us to stop pagination when
        we encounter existing events.

        Args:
            limit: Number of events per request (default 100)
            offset: Offset for pagination (optional)
            order: Field to order by (e.g., "createdAt")
            ascending: Sort ascending (True) or descending (False, default)

        Returns:
            List of PolymarketEvent objects (newest first)
        """
        params = PolymarketEventsParams(
            limit=limit, offset=offset, order=order, ascending=ascending
        )

        response = await self.client.get(
            f"{self.BASE_URL}/events/pagination",
            params=params.model_dump(exclude_none=True),
        )
        response.raise_for_status()
        data = response.json()

        # The response has { "data": [...], "pagination": {...} }
        events_data = data.get("data", [])
        return [PolymarketEvent.model_validate(e) for e in events_data]

    async def close(self):
        """Cleanup"""
        await self.client.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        await self.close()

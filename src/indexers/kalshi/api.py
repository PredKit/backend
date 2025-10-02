"""
Kalshi API client (thin wrapper around Trade API v2)
"""

from typing import ClassVar, Self

import httpx
import structlog

from .schemas import (
    KalshiEvent,
    KalshiEventsParams,
    KalshiMarket,
    KalshiMarketsParams,
    KalshiSeries,
    KalshiSeriesParams,
)

logger = structlog.get_logger()  # pyright: ignore[reportAny]


class KalshiAPI:
    """Low-level Kalshi API client"""

    BASE_URL: ClassVar[str] = "https://api.elections.kalshi.com/trade-api/v2"

    def __init__(self):
        self.client: httpx.AsyncClient = httpx.AsyncClient(
            timeout=30.0, follow_redirects=True
        )

    async def get_markets(
        self, limit: int = 100, cursor: str | None = None
    ) -> tuple[list[KalshiMarket], str | None]:
        """
        Fetch markets from /markets endpoint.

        Args:
            limit: Number of markets per request (default 100)
            cursor: Cursor for pagination (optional)

        Returns:
            Tuple of (markets, next_cursor)
        """
        params = KalshiMarketsParams(limit=limit, cursor=cursor)

        response = await self.client.get(
            f"{self.BASE_URL}/markets",
            params=params.model_dump(exclude_none=True),
        )
        response.raise_for_status()
        data = response.json()

        markets = [KalshiMarket.model_validate(m) for m in data.get("markets", [])]
        next_cursor = data.get("cursor")

        return markets, next_cursor

    async def get_events(
        self,
        limit: int = 100,
        cursor: str | None = None,
        with_nested_markets: bool = False,
    ) -> tuple[list[KalshiEvent], str | None]:
        """
        Fetch events from /events endpoint.

        Args:
            limit: Number of events per request (default 100)
            cursor: Cursor for pagination (optional)
            with_nested_markets: Include nested markets in response (default False)

        Returns:
            Tuple of (events, next_cursor)
        """
        params = KalshiEventsParams(
            limit=limit, cursor=cursor, with_nested_markets=with_nested_markets
        )

        response = await self.client.get(
            f"{self.BASE_URL}/events",
            params=params.model_dump(exclude_none=True),
        )
        response.raise_for_status()
        data = response.json()

        events = [KalshiEvent.model_validate(e) for e in data.get("events", [])]
        next_cursor = data.get("cursor")

        return events, next_cursor

    async def get_series(
        self, limit: int = 100, cursor: str | None = None
    ) -> tuple[list[KalshiSeries], str | None]:
        """
        Fetch series from /series endpoint.

        Args:
            limit: Number of series per request (default 100)
            cursor: Cursor for pagination (optional)

        Returns:
            Tuple of (series, next_cursor)
        """
        params = KalshiSeriesParams(limit=limit, cursor=cursor)

        response = await self.client.get(
            f"{self.BASE_URL}/series",
            params=params.model_dump(exclude_none=True),
        )
        response.raise_for_status()
        data = response.json()

        series = [KalshiSeries.model_validate(s) for s in data.get("series", [])]
        next_cursor = data.get("cursor")

        return series, next_cursor

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

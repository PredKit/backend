"""Base collector interface for all prediction market platforms"""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from shared.entities import Event


class BaseCollector(ABC):
    """Abstract base class for event collectors"""

    @abstractmethod
    async def collect_events_paginated(
        self, max_pages: int = 1
    ) -> AsyncIterator[list[Event]]:
        """
        Collect events page by page.

        Args:
            max_pages: Maximum number of pages to fetch (default 1, use -1 for all)

        Yields:
            Pages of normalized Event entities
        """
        if False:  # pragma: no cover
            yield []

    @abstractmethod
    async def close(self):
        """Cleanup resources"""
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        await self.close()

"""
Market collectors
"""

from .base import BaseCollector
from .kalshi import KalshiCollector
from .polymarket import PolymarketCollector

# Registry of all collectors
ALL_COLLECTORS: list[type[BaseCollector]] = [
    PolymarketCollector,
    KalshiCollector,
]

__all__ = ["BaseCollector", "PolymarketCollector", "KalshiCollector", "ALL_COLLECTORS"]

#!/usr/bin/env python3
"""Test indexer - backfills all platforms like prod"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from indexers.indexer import ALL_PAGES, index_events
from shared.entities import Platform


async def main():
    print("Starting full backfill (all platforms, all pages)...")

    results = await index_events(
        platforms=[Platform.KALSHI, Platform.POLYMARKET], max_pages=ALL_PAGES
    )

    print("\nResults:")
    for platform, stats in results.items():
        print(f"  {platform.value}: inserted={stats.inserted}, updated={stats.updated}")


if __name__ == "__main__":
    asyncio.run(main())

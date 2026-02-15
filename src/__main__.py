"""Entry point for running the Actor."""

import asyncio

from src.tiktok_trend_hunter.main import main

if __name__ == "__main__":
    asyncio.run(main())

"""Dedicated orchestration runner entrypoint.

Run this module as a separate process from API workers:
`python -m app.orchestrator_main`
"""

from __future__ import annotations

import asyncio

from app.core.log_config import configure_logging, get_logger
from app.services.orchestration.runtime import runtime

logger = get_logger("orchestrator.main")


async def main() -> None:
    """Start dedicated orchestration reconcile loop."""
    configure_logging()
    logger.info("Orchestrator runtime starting")
    await runtime.run_forever(interval_seconds=1.0)


if __name__ == "__main__":
    asyncio.run(main())


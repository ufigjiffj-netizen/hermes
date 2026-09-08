import asyncio
import logging
from typing import Any

logger = logging.getLogger(__name__)


class BumpManager:
    """
    Manages periodic auto-bumping of active lots.
    """

    def __init__(self, bump_interval: float, client: Any):
        self.bump_interval = bump_interval
        self.client = client
        self._running = False
        self._task: asyncio.Task[Any] | None = None

    async def start(self) -> None:
        """Starts the background task for bumping lots."""
        self._running = True
        self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        """Stops the background task."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _loop(self) -> None:
        """Internal loop that runs while running."""
        while self._running:
            try:
                lots = await self.client.get_active_lots()
                for lot in lots:
                    if lot.get("active"):
                        await self.client.bump_lot(lot["id"])
            except (
                ConnectionError,
                TimeoutError,
                ValueError,
                RuntimeError,
                TypeError,
            ) as e:
                logger.error("Error bumping lots: %s", e)
            except Exception as e:
                # We log and re-raise to satisfy BLE001 if we must catch Exception
                logger.error("Unexpected error bumping lots: %s", e)
                raise
            await asyncio.sleep(self.bump_interval)

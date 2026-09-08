import asyncio
import logging
from typing import Any

logger = logging.getLogger(__name__)


class BumpManager:
    """
    Manages periodic auto-bumping of active lots across FunPay categories.
    """

    def __init__(
        self,
        bump_interval: float,
        client: Any,
        node_ids: list[str] | None = None,
    ) -> None:
        self.bump_interval = bump_interval
        self.client = client
        self.node_ids = node_ids or []
        self._running = False
        self._task: asyncio.Task[Any] | None = None

    async def bump_node(self, node_id: str) -> bool:
        """Sends a bump request for a specific category/node ID."""
        url = "https://funpay.com/lots/raise"
        headers = {"X-Requested-With": "XMLHttpRequest"}
        data = {"node_id": node_id}
        await self.client.post(url, headers=headers, data=data)
        logger.info("Lots bumped successfully for node %s", node_id)
        return True

    async def bump_all(self) -> list[str]:
        """Bumps all configured nodes."""
        bumped = []
        for node_id in self.node_ids:
            try:
                await self.bump_node(node_id)
                bumped.append(node_id)
            except (
                ConnectionError,
                TimeoutError,
                ValueError,
                RuntimeError,
                TypeError,
            ) as e:
                logger.error("Error bumping node %s: %s", node_id, e)
        return bumped

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
                if self.node_ids:
                    await self.bump_all()
                else:
                    await self.bump_node("all")
            except (
                ConnectionError,
                TimeoutError,
                ValueError,
                RuntimeError,
                TypeError,
            ) as e:
                logger.error("Error in bump loop: %s", e)
            except Exception as e:
                logger.error("Unexpected error bumping lots: %s", e)
                raise
            await asyncio.sleep(self.bump_interval)

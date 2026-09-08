import asyncio
import logging
from typing import Any

import aiohttp

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
        try:
            await self.client.post(url, headers=headers, data=data)
            logger.info("Lots bumped successfully for node %s", node_id)
            return True
        except aiohttp.ClientResponseError as e:
            if e.status == 428:
                logger.warning(
                    "Lots for node %s cannot be bumped yet (cooldown active / HTTP 428)",
                    node_id,
                )
                return False
            logger.error("HTTP error bumping lots for node %s: %s", node_id, e)
            raise

    async def bump_all(self) -> list[str]:
        """Bumps all configured nodes."""
        bumped = []
        for node_id in self.node_ids:
            try:
                success = await self.bump_node(node_id)
                if success:
                    bumped.append(node_id)
            except (
                ConnectionError,
                TimeoutError,
                ValueError,
                RuntimeError,
                TypeError,
                aiohttp.ClientError,
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
            except (
                ConnectionError,
                TimeoutError,
                ValueError,
                RuntimeError,
                TypeError,
                aiohttp.ClientError,
            ) as e:
                logger.debug("Bumper task error during stop: %s", e)
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
                aiohttp.ClientError,
            ) as e:
                logger.error("Error in bump loop: %s", e)
            except asyncio.CancelledError:
                break
            await asyncio.sleep(self.bump_interval)

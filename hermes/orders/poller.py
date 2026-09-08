import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Any

import aiohttp

from hermes.core.network import HttpClient
from hermes.orders.repository import OrderRepository

logger = logging.getLogger(__name__)


class OrderPoller:
    def __init__(
        self,
        client: HttpClient,
        repo: OrderRepository,
        url: str,
        interval: float = 10.0,
        on_new_order: Callable[[dict[str, Any]], Awaitable[None]] | None = None,
    ) -> None:
        self.client = client
        self.repo = repo
        self.url = url
        self.interval = interval
        self.on_new_order = on_new_order
        self._running = False

    async def poll_once(self) -> list[dict[str, Any]]:
        """Polls the API once and returns a list of new orders."""
        response = await self.client.get(self.url)
        # Assume response has an "orders" key list
        raw_orders = response.get("orders", [])

        new_orders = []
        for order in raw_orders:
            order_id = order.get("id")
            if not order_id:
                continue

            is_processed = await self.repo.is_order_processed(order_id)
            if not is_processed:
                # We save it only after acknowledging it's new
                await self.repo.save_order(order_id)
                new_orders.append(order)

        return new_orders

    async def run(self) -> None:
        """Runs the poller in an async loop."""
        self._running = True
        while self._running:
            try:
                new_orders = await self.poll_once()
                if self.on_new_order and new_orders:
                    for order in new_orders:
                        try:
                            await self.on_new_order(order)
                        except (
                            ConnectionError,
                            TimeoutError,
                            ValueError,
                            RuntimeError,
                            TypeError,
                            KeyError,
                        ) as e:
                            logger.error(
                                "Error processing order %s: %s", order.get("id"), e
                            )
            except (
                ConnectionError,
                TimeoutError,
                ValueError,
                RuntimeError,
                TypeError,
                KeyError,
                aiohttp.ClientError,
            ) as e:
                logger.error("Error polling orders from %s: %s", self.url, e)
            except asyncio.CancelledError:
                break

            await asyncio.sleep(self.interval)

    def stop(self) -> None:
        """Stops the poller."""
        self._running = False

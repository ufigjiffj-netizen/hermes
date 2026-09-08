import asyncio
from typing import Any

from hermes.core.network import HttpClient
from hermes.orders.repository import OrderRepository


class OrderPoller:
    def __init__(
        self,
        client: HttpClient,
        repo: OrderRepository,
        url: str,
        interval: float = 10.0,
    ) -> None:
        self.client = client
        self.repo = repo
        self.url = url
        self.interval = interval
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
            await self.poll_once()
            await asyncio.sleep(self.interval)

    def stop(self) -> None:
        """Stops the poller."""
        self._running = False

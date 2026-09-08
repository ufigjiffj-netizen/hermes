import argparse
import asyncio
import logging
import os
import signal
import sys
from collections.abc import Callable

from hermes.core.auth import Authenticator
from hermes.core.config import load_config
from hermes.core.network import HttpClient
from hermes.core.rate_limit import RateLimiter
from hermes.core.storage import DatabaseManager
from hermes.lots.bump import BumpManager
from hermes.orders.delivery import DeliveryManager
from hermes.orders.poller import OrderPoller
from hermes.orders.repository import OrderRepository

logger = logging.getLogger(__name__)


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Hermes CLI")
    parser.add_argument(
        "--config", help="Path to config file", required=False, default=None
    )
    return parser.parse_args(args)


async def shutdown(
    loop: asyncio.AbstractEventLoop, signal: signal.Signals | None = None
) -> None:
    """Cleanup tasks tied to the service's shutdown."""
    if signal:
        logger.info("Received exit signal %s...", signal.name)

    tasks = [t for t in asyncio.all_tasks(loop) if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()

    logger.info("Cancelling %d outstanding tasks", len(tasks))
    await asyncio.gather(*tasks, return_exceptions=True)


async def run_app(args: argparse.Namespace) -> None:
    """Main async entrypoint."""
    config_path = args.config
    if config_path is None and os.path.exists("config.yaml"):
        config_path = "config.yaml"

    logger.info("Starting Hermes with config: %s", config_path)
    config = load_config(config_path)

    db_path = config.get("storage", {}).get("db_path", "hermes.db")
    golden_key = config.get("funpay", {}).get("golden_key", "")
    proxy = config.get("funpay", {}).get("proxy")
    bump_interval = config.get("lots", {}).get("bump_interval", 10.0)
    bump_node_ids = config.get("lots", {}).get("node_ids", [])
    poll_interval = config.get("orders", {}).get("poll_interval", 10.0)
    orders_url = config.get("orders", {}).get(
        "orders_url", "https://funpay.com/api/orders"
    )
    send_url = config.get("delivery", {}).get("send_url", "https://funpay.com/chat/")
    auto_reply_text = config.get("delivery", {}).get("auto_reply_text", "")
    rate_limit_rps = float(config.get("network", {}).get("rate_limit_rps", 5.0))

    db = DatabaseManager(db_path)
    poller = None
    bumper = None
    poller_task = None

    try:
        await db.connect()
        await db.initialize(
            "CREATE TABLE IF NOT EXISTS processed_orders (order_id TEXT PRIMARY KEY);"
        )

        repo = OrderRepository(db)
        authenticator = Authenticator(golden_key=golden_key)
        rate_limiter = RateLimiter(rps=rate_limit_rps)

        async with HttpClient(
            proxy=proxy,
            rate_limiter=rate_limiter,
            authenticator=authenticator,
        ) as client:
            delivery = DeliveryManager(client=client, send_url=send_url)
            if auto_reply_text:
                delivery.set_auto_reply(auto_reply_text)

            poller = OrderPoller(
                client=client,
                repo=repo,
                url=orders_url,
                interval=poll_interval,
                on_new_order=delivery.auto_reply if auto_reply_text else None,
            )
            bumper = BumpManager(
                bump_interval=bump_interval, client=client, node_ids=bump_node_ids
            )

            logger.info("Starting poller and bumper...")
            await bumper.start()
            poller_task = asyncio.create_task(poller.run())

            while True:
                await asyncio.sleep(3600)
    except asyncio.CancelledError:
        logger.info("Shutting down components...")
    finally:
        if poller:
            poller.stop()
        if bumper:
            await bumper.stop()
        if poller_task:
            poller_task.cancel()
            await asyncio.gather(poller_task, return_exceptions=True)
        await db.shutdown()


def main() -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    args = parse_args(sys.argv[1:])
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    app_task: asyncio.Task[None] | None = None

    def handle_signal(sig: signal.Signals) -> None:
        logger.info("Received exit signal %s...", sig.name)
        if app_task and not app_task.done():
            app_task.cancel()

    def make_handler(sig: signal.Signals) -> Callable[[], None]:
        return lambda: handle_signal(sig)

    signals = (
        (getattr(signal, "SIGHUP", signal.SIGTERM), signal.SIGTERM, signal.SIGINT)
        if sys.platform != "win32"
        else (signal.SIGINT, signal.SIGTERM)
    )
    for s in signals:
        try:
            loop.add_signal_handler(s, make_handler(s))
        except NotImplementedError:
            # add_signal_handler is not implemented on Windows for ProactorEventLoop
            pass

    try:
        app_task = loop.create_task(run_app(args))
        loop.run_until_complete(app_task)
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("Received KeyboardInterrupt")
        if app_task and not app_task.done():
            app_task.cancel()
        loop.run_until_complete(shutdown(loop))
    finally:
        pending = [t for t in asyncio.all_tasks(loop) if not t.done()]
        if pending:
            for t in pending:
                t.cancel()
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        loop.close()
        logger.info("Successfully shutdown Hermes")


if __name__ == "__main__":
    main()

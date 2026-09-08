import argparse
import asyncio
import logging
import signal
import sys

from hermes.core.auth import Authenticator
from hermes.core.config import load_config
from hermes.core.network import HttpClient
from hermes.core.storage import DatabaseManager
from hermes.lots.bump import BumpManager
from hermes.orders.poller import OrderPoller
from hermes.orders.repository import OrderRepository

logger = logging.getLogger(__name__)


def parse_args(args=None):
    parser = argparse.ArgumentParser(description="Hermes CLI")
    parser.add_argument("--config", help="Path to config file", required=False)
    return parser.parse_args(args)


async def shutdown(loop: asyncio.AbstractEventLoop, signal=None):
    """Cleanup tasks tied to the service's shutdown."""
    if signal:
        logger.info(f"Received exit signal {signal.name}...")

    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]

    logger.info(f"Cancelling {len(tasks)} outstanding tasks")
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()


async def run_app(args):
    """Main async entrypoint."""
    logger.info(f"Starting Hermes with config: {args.config}")
    config = load_config(args.config)

    db_path = config.get("storage", {}).get("db_path", "hermes.db")
    golden_key = config.get("funpay", {}).get("golden_key", "")
    proxy = config.get("funpay", {}).get("proxy")
    bump_interval = config.get("lots", {}).get("bump_interval", 10.0)
    poll_interval = config.get("orders", {}).get("poll_interval", 10.0)

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
        authenticator = Authenticator(golden_key)

        async with HttpClient(proxy=proxy) as client:
            if client._session:
                await authenticator.apply(client._session)

            poller = OrderPoller(
                client=client,
                repo=repo,
                url="https://funpay.com/api/orders",  # Dummy URL for now
                interval=poll_interval,
            )
            bumper = BumpManager(bump_interval=bump_interval, client=client)

            logger.info("Starting poller and bumper...")
            await bumper.start()
            poller_task = asyncio.create_task(poller.run())

            while True:
                await asyncio.sleep(3600)
    except asyncio.CancelledError:
        logger.info("Shutting down components...")
        if poller:
            poller.stop()
        if bumper:
            await bumper.stop()
        if poller_task:
            await poller_task
    finally:
        await db.shutdown()


def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    args = parse_args(sys.argv[1:])
    # If no command‑line arguments are supplied, show a short usage annotation.
    if len(sys.argv) <= 1:
        # Simple guidance for users invoking hermes without any flags.
        print("Usage: hermes [--config <path>]\n\nRun 'hermes -h' for full options.")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Setup signal handlers
    signals = (
        (getattr(signal, "SIGHUP", signal.SIGTERM), signal.SIGTERM, signal.SIGINT)
        if sys.platform != "win32"
        else (signal.SIGINT, signal.SIGTERM)
    )
    for s in signals:
        try:
            loop.add_signal_handler(
                s, lambda s=s: asyncio.create_task(shutdown(loop, signal=s))
            )
        except NotImplementedError:
            # add_signal_handler is not implemented on Windows for ProactorEventLoop
            pass

    try:
        loop.run_until_complete(run_app(args))
    except KeyboardInterrupt:
        logger.info("Received KeyboardInterrupt")
        loop.run_until_complete(shutdown(loop))
    finally:
        loop.close()
        logger.info("Successfully shutdown Hermes")


if __name__ == "__main__":
    main()

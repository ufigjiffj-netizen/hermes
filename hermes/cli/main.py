import argparse
import asyncio
import logging
import signal
import sys

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
    # Initialize components here (Config, Storage, Auth, Poller, BumpManager)
    # For MVP, we just sleep/wait
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        pass


def main():
    args = parse_args(sys.argv[1:])

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

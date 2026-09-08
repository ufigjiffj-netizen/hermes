import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.mark.asyncio
async def test_debug():
    from hermes.cli.main import parse_args, run_app

    logging.basicConfig(level=logging.INFO)
    args = parse_args(["--config", "dummy.yaml"])
    with (
        patch("hermes.cli.main.load_config", return_value={}),
        patch("hermes.cli.main.DatabaseManager", new_callable=MagicMock) as mock_db,
        patch("hermes.cli.main.OrderRepository"),
        patch("hermes.cli.main.Authenticator"),
        patch("hermes.cli.main.RateLimiter"),
        patch("hermes.cli.main.DeliveryManager"),
        patch("hermes.cli.main.HttpClient") as mock_client_class,
        patch("hermes.cli.main.OrderPoller") as mock_poller_class,
        patch("hermes.cli.main.BumpManager") as mock_bumper_class,
    ):
        mock_db.return_value.connect = AsyncMock()
        mock_db.return_value.initialize = AsyncMock()
        mock_db.return_value.shutdown = AsyncMock()

        mock_poller_class.return_value.run = AsyncMock()
        mock_bumper_class.return_value.start = AsyncMock()
        mock_bumper_class.return_value.stop = AsyncMock()

        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client

        task = asyncio.create_task(run_app(args))
        await asyncio.sleep(0.01)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

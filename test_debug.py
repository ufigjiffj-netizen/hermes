import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import pytest

@pytest.mark.asyncio
async def test_debug():
    from hermes.cli.main import run_app, parse_args
    import logging
    logging.basicConfig(level=logging.INFO)
    args = parse_args(["--config", "dummy.yaml"])
    with (
        patch("hermes.cli.main.load_config", return_value={}),
        patch("hermes.cli.main.DatabaseManager", new_callable=MagicMock) as mock_db,
        patch("hermes.cli.main.OrderRepository"),
        patch("hermes.cli.main.Authenticator"),
        patch("hermes.cli.main.HttpClient") as mock_client_class,
        patch("hermes.cli.main.OrderPoller"),
        patch("hermes.cli.main.BumpManager"),
    ):
        mock_db.return_value.connect = AsyncMock()
        mock_db.return_value.initialize = AsyncMock()
        mock_db.return_value.shutdown = AsyncMock()
        
        mock_client = AsyncMock()
        mock_client.aenter.return_value = mock_client
        mock_client._session = MagicMock()
        
        mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_class.return_value.__aexit__ = AsyncMock()
        
        task = asyncio.create_task(run_app(args))
        await asyncio.sleep(0.01)
        task.cancel()
        try:
            await task
        except BaseException as e:
            print("ERROR", repr(e))

asyncio.run(test_debug())

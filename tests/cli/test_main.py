import asyncio
import signal
import warnings
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from hermes.cli.main import main, parse_args, run_app, shutdown


def test_parse_args():
    args = parse_args(["--config", "config.yaml"])
    assert args.config == "config.yaml"


@pytest.mark.asyncio
async def test_shutdown_with_signal():
    loop = asyncio.get_running_loop()
    # Mock a task
    mock_task = MagicMock(spec=asyncio.Task)
    mock_task.cancel = MagicMock()
    with (
        patch("asyncio.all_tasks", return_value={mock_task}),
        patch("asyncio.current_task", return_value=None),
        patch("asyncio.gather", new_callable=AsyncMock) as mock_gather,
    ):
        await shutdown(loop, signal=signal.SIGINT)
        mock_task.cancel.assert_called_once()
        mock_gather.assert_called_once()


@pytest.mark.asyncio
async def test_run_app_cancelled():
    args = parse_args(["--config", "dummy.yaml"])
    dummy_config = {
        "delivery": {"auto_reply_text": "Auto delivered!", "send_url": "http://chat"},
        "lots": {"node_ids": ["81"]},
    }
    with (
        patch("hermes.cli.main.load_config", return_value=dummy_config),
        patch("hermes.cli.main.DatabaseManager", new_callable=MagicMock) as mock_db,
        patch("hermes.cli.main.OrderRepository"),
        patch("hermes.cli.main.Authenticator"),
        patch("hermes.cli.main.RateLimiter"),
        patch("hermes.cli.main.DeliveryManager") as mock_delivery_class,
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
        # Let the task yield and reach the while True loop
        for _ in range(10):
            await asyncio.sleep(0.01)
        task.cancel()
        # Should not raise
        await task

        mock_delivery_class.return_value.set_auto_reply.assert_called_once_with(
            "Auto delivered!"
        )


async def _dummy_run_app(args):
    pass


def test_main_normal():
    with patch("hermes.cli.main.parse_args") as mock_parse:
        mock_parse.return_value.config = "dummy.yaml"
        with (
            patch(
                "hermes.cli.main.run_app", side_effect=_dummy_run_app
            ) as mock_run_app,
            patch("sys.argv", ["hermes", "--config", "dummy.yaml"]),
        ):
            main()
            mock_run_app.assert_called_once()


def test_main_normal_linux():
    with patch("hermes.cli.main.parse_args") as mock_parse:
        mock_parse.return_value.config = "dummy.yaml"
        with (
            patch(
                "hermes.cli.main.run_app", side_effect=_dummy_run_app
            ) as mock_run_app,
            patch("sys.argv", ["hermes", "--config", "dummy.yaml"]),
            patch("sys.platform", "linux"),
        ):
            main()
            mock_run_app.assert_called_once()


def test_main_normal_win32():
    with patch("hermes.cli.main.parse_args") as mock_parse:
        mock_parse.return_value.config = "dummy.yaml"
        with (
            patch(
                "hermes.cli.main.run_app", side_effect=_dummy_run_app
            ) as mock_run_app,
            patch("sys.argv", ["hermes", "--config", "dummy.yaml"]),
            patch("sys.platform", "win32"),
        ):
            main()
            mock_run_app.assert_called_once()


def test_main_keyboard_interrupt():
    with patch("hermes.cli.main.parse_args") as mock_parse:
        mock_parse.return_value.config = "dummy.yaml"

        loop_mock = MagicMock()
        calls: list[object] = []

        def _side_effect(coro: object) -> None:
            if asyncio.iscoroutine(coro):
                coro.close()
            calls.append(coro)
            if len(calls) == 1:
                raise KeyboardInterrupt()

        loop_mock.run_until_complete.side_effect = _side_effect

        # Patch run_app and shutdown so they don't produce unawaited coroutines
        with (
            patch("asyncio.new_event_loop", return_value=loop_mock),
            patch("asyncio.set_event_loop"),
            patch("sys.argv", ["hermes", "--config", "dummy.yaml"]),
            patch("hermes.cli.main.run_app", side_effect=_dummy_run_app),
            patch("hermes.cli.main.shutdown", side_effect=_dummy_run_app),
        ):
            main()
            assert loop_mock.run_until_complete.call_count == 2
            loop_mock.close.assert_called_once()


def test_main_signal_not_implemented():
    # Simulate NotImplementedError on add_signal_handler
    with patch("hermes.cli.main.parse_args") as mock_parse:
        mock_parse.return_value.config = "dummy.yaml"

        loop_mock = MagicMock()
        loop_mock.add_signal_handler.side_effect = NotImplementedError()

        def _clean_complete(coro):
            if asyncio.iscoroutine(coro):
                coro.close()

        loop_mock.run_until_complete.side_effect = _clean_complete

        with (
            patch("asyncio.new_event_loop", return_value=loop_mock),
            patch("asyncio.set_event_loop"),
            patch("sys.argv", ["hermes", "--config", "dummy.yaml"]),
            patch("hermes.cli.main.run_app", side_effect=_dummy_run_app),
        ):
            main()
            assert loop_mock.run_until_complete.call_count == 1


def test_main_no_args():
    with (
        patch("hermes.cli.main.run_app", side_effect=_dummy_run_app) as mock_run_app,
        patch("sys.argv", ["hermes"]),
    ):
        main()
        mock_run_app.assert_called_once()


@pytest.mark.asyncio
async def test_run_app_detects_default_config_yaml(tmp_path, monkeypatch):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("storage:\n  db_path: custom.db\n")

    monkeypatch.chdir(tmp_path)
    args = parse_args([])
    assert args.config is None

    with (
        patch("hermes.cli.main.load_config") as mock_load,
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

        mock_load.return_value = {}
        task = asyncio.create_task(run_app(args))
        for _ in range(10):
            await asyncio.sleep(0.01)
        task.cancel()
        await task

        mock_load.assert_called_once_with("config.yaml")


def test_module_execution():
    with (
        patch("sys.argv", ["hermes", "--help"]),
        warnings.catch_warnings(),
    ):
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        import runpy

        try:
            runpy.run_module("hermes.cli.main", run_name="__main__")
        except SystemExit as e:
            assert e.code == 0

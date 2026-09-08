import asyncio
import signal
import sys
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
    args = parse_args([])
    task = asyncio.create_task(run_app(args))
    await asyncio.sleep(0.01)
    task.cancel()
    # Should not raise
    await task


def test_main_normal():
    with patch("hermes.cli.main.parse_args") as mock_parse:
        mock_parse.return_value.config = "dummy.yaml"
        with (
            patch("hermes.cli.main.run_app", new_callable=AsyncMock) as mock_run_app,
            patch("sys.argv", ["hermes", "--config", "dummy.yaml"]),
        ):
            main()
            mock_run_app.assert_called_once()


def test_main_keyboard_interrupt():
    with patch("hermes.cli.main.parse_args") as mock_parse:
        mock_parse.return_value.config = "dummy.yaml"

        loop_mock = MagicMock()
        loop_mock.run_until_complete.side_effect = [KeyboardInterrupt(), None]

        # Patch run_app and shutdown so they don't produce unawaited coroutines
        with (
            patch("asyncio.new_event_loop", return_value=loop_mock),
            patch("asyncio.set_event_loop"),
            patch("sys.argv", ["hermes"]),
            patch("hermes.cli.main.run_app"),
            patch("hermes.cli.main.shutdown"),
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
        loop_mock.run_until_complete = MagicMock()

        with (
            patch("asyncio.new_event_loop", return_value=loop_mock),
            patch("asyncio.set_event_loop"),
            patch("sys.argv", ["hermes"]),
            patch("hermes.cli.main.run_app"),
        ):
            main()
            loop_mock.run_until_complete.assert_called_once()


def test_module_execution():
    with patch("sys.modules", sys.modules), patch("sys.argv", ["hermes", "--help"]):
        import runpy

        try:
            runpy.run_module("hermes.cli.main", run_name="__main__")
        except SystemExit as e:
            assert e.code == 0

import asyncio
from unittest.mock import AsyncMock

import pytest

from hermes.lots.bump import BumpManager


@pytest.mark.asyncio
async def test_bump_manager_starts_and_stops():
    mock_client = AsyncMock()
    mock_client.get_active_lots.return_value = []

    manager = BumpManager(bump_interval=0.01, client=mock_client)

    await manager.start()
    assert manager._running is True

    await asyncio.sleep(0.02)

    await manager.stop()
    assert manager._running is False
    mock_client.get_active_lots.assert_called()


@pytest.mark.asyncio
async def test_bump_manager_bumps_active_lots():
    mock_client = AsyncMock()
    mock_client.get_active_lots.return_value = [
        {"id": "1", "active": True},
        {"id": "2", "active": False},
        {"id": "3", "active": True},
    ]

    manager = BumpManager(bump_interval=0.01, client=mock_client)

    await manager.start()
    await asyncio.sleep(0.02)
    await manager.stop()

    assert mock_client.bump_lot.call_count >= 2
    mock_client.bump_lot.assert_any_call("1")
    mock_client.bump_lot.assert_any_call("3")


@pytest.mark.asyncio
async def test_bump_manager_exception_handling():
    mock_client = AsyncMock()
    mock_client.get_active_lots.side_effect = RuntimeError("Test exception")

    manager = BumpManager(bump_interval=0.01, client=mock_client)

    await manager.start()
    # Let it run and hit the exception
    await asyncio.sleep(0.02)
    await manager.stop()

    # It should not have crashed, meaning it ran and stopped normally
    assert mock_client.get_active_lots.call_count >= 1


@pytest.mark.asyncio
async def test_bump_manager_unhandled_exception():
    mock_client = AsyncMock()
    # KeyError is not in the handled exceptions tuple
    mock_client.get_active_lots.side_effect = KeyError("Unhandled")

    manager = BumpManager(bump_interval=0.01, client=mock_client)

    await manager.start()
    await asyncio.sleep(0.02)
    # It should crash the task, and stop() will re-raise the task's exception
    with pytest.raises(KeyError):
        await manager.stop()

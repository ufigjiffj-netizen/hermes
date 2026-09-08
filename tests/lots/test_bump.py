import asyncio
from unittest.mock import AsyncMock

import pytest

from hermes.lots.bump import BumpManager


@pytest.mark.asyncio
async def test_bump_manager_starts_and_stops():
    mock_client = AsyncMock()
    mock_client.post.return_value = {"status": "ok"}

    manager = BumpManager(bump_interval=0.01, client=mock_client)

    await manager.start()
    assert manager._running is True

    await asyncio.sleep(0.02)

    await manager.stop()
    assert manager._running is False
    mock_client.post.assert_called()


@pytest.mark.asyncio
async def test_bump_manager_bumps_active_lots_with_nodes():
    mock_client = AsyncMock()
    mock_client.post.return_value = {"status": "ok"}

    manager = BumpManager(bump_interval=0.01, client=mock_client, node_ids=["81", "82"])

    await manager.start()
    await asyncio.sleep(0.02)
    await manager.stop()

    assert mock_client.post.call_count >= 2


@pytest.mark.asyncio
async def test_bump_manager_exception_handling():
    mock_client = AsyncMock()
    mock_client.post.side_effect = RuntimeError("Test exception")

    manager = BumpManager(bump_interval=0.01, client=mock_client)

    await manager.start()
    await asyncio.sleep(0.02)
    await manager.stop()

    assert mock_client.post.call_count >= 1


@pytest.mark.asyncio
async def test_bump_all_node_exception():
    mock_client = AsyncMock()
    # First call fails with ConnectionError, second succeeds
    mock_client.post.side_effect = [ConnectionError("Fail"), {"status": "ok"}]

    manager = BumpManager(bump_interval=0.01, client=mock_client, node_ids=["81", "82"])
    bumped = await manager.bump_all()
    assert bumped == ["82"]


import aiohttp
from aiohttp import RequestInfo
from multidict import CIMultiDict, CIMultiDictProxy
from yarl import URL


@pytest.mark.asyncio
async def test_bump_node_428_cooldown():
    mock_client = AsyncMock()
    request_info = RequestInfo(
        url=URL("https://funpay.com/lots/raise"),
        method="POST",
        headers=CIMultiDictProxy(CIMultiDict()),
        real_url=URL("https://funpay.com/lots/raise"),
    )
    mock_client.post.side_effect = aiohttp.ClientResponseError(
        request_info=request_info,
        history=(),
        status=428,
        message="Precondition Required",
    )
    manager = BumpManager(bump_interval=0.01, client=mock_client)
    success = await manager.bump_node("81")
    assert success is False


@pytest.mark.asyncio
async def test_bump_node_other_client_response_error():
    mock_client = AsyncMock()
    request_info = RequestInfo(
        url=URL("https://funpay.com/lots/raise"),
        method="POST",
        headers=CIMultiDictProxy(CIMultiDict()),
        real_url=URL("https://funpay.com/lots/raise"),
    )
    mock_client.post.side_effect = aiohttp.ClientResponseError(
        request_info=request_info,
        history=(),
        status=500,
        message="Server Error",
    )
    manager = BumpManager(bump_interval=0.01, client=mock_client)
    with pytest.raises(aiohttp.ClientResponseError):
        await manager.bump_node("81")


@pytest.mark.asyncio
async def test_bump_manager_stop_suppresses_task_error():
    mock_client = AsyncMock()
    mock_client.post.side_effect = ConnectionError("Task failed")

    manager = BumpManager(bump_interval=0.01, client=mock_client, node_ids=["81"])
    # Force _loop to fail with ConnectionError outside bump_all
    with pytest.raises(ConnectionError):
        # Directly calling bump_node when mock raises
        await manager.bump_node("81")

    # Now run loop where an uncaught exception occurred in task
    async def failing_loop():
        raise ConnectionError("Failing loop")

    manager._running = True
    manager._task = asyncio.create_task(failing_loop())
    await asyncio.sleep(0.01)
    # Stopping should catch ConnectionError at line 87 without raising
    await manager.stop()
    assert manager._task is None


@pytest.mark.asyncio
async def test_bump_manager_unhandled_exception():
    mock_client = AsyncMock()
    mock_client.post.side_effect = KeyError("Unhandled")

    manager = BumpManager(bump_interval=0.01, client=mock_client)

    await manager.start()
    await asyncio.sleep(0.02)
    with pytest.raises(KeyError):
        await manager.stop()


@pytest.mark.asyncio
async def test_bump_manager_loop_cancelled():
    mock_client = AsyncMock()
    mock_client.post.side_effect = asyncio.CancelledError()
    manager = BumpManager(bump_interval=0.01, client=mock_client)
    manager._running = True
    await manager._loop()

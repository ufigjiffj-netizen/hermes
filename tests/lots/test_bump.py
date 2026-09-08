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


@pytest.mark.asyncio
async def test_bump_manager_unhandled_exception():
    mock_client = AsyncMock()
    mock_client.post.side_effect = KeyError("Unhandled")

    manager = BumpManager(bump_interval=0.01, client=mock_client)

    await manager.start()
    await asyncio.sleep(0.02)
    with pytest.raises(KeyError):
        await manager.stop()

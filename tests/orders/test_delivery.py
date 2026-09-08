from unittest.mock import AsyncMock

import pytest

from hermes.core.network import HttpClient
from hermes.orders.delivery import DeliveryManager


@pytest.fixture
def mock_client() -> AsyncMock:
    client = AsyncMock(spec=HttpClient)
    return client


@pytest.mark.asyncio
async def test_delivery_manager_send_message(mock_client: AsyncMock) -> None:
    manager = DeliveryManager(
        client=mock_client, send_url="http://test.funpay.com/message"
    )

    await manager.send_message(chat_id="chat123", text="Hello there!")

    mock_client.post.assert_called_once_with(
        "http://test.funpay.com/message",
        json={"chat_id": "chat123", "text": "Hello there!"},
    )


@pytest.mark.asyncio
async def test_delivery_manager_auto_reply(mock_client: AsyncMock) -> None:
    manager = DeliveryManager(
        client=mock_client, send_url="http://test.funpay.com/message"
    )
    manager.set_auto_reply("Auto-reply template")

    await manager.auto_reply(order={"chat_id": "chat123"})

    mock_client.post.assert_called_once_with(
        "http://test.funpay.com/message",
        json={"chat_id": "chat123", "text": "Auto-reply template"},
    )


@pytest.mark.asyncio
async def test_delivery_manager_auto_reply_no_chat_id(mock_client: AsyncMock) -> None:
    manager = DeliveryManager(
        client=mock_client, send_url="http://test.funpay.com/message"
    )
    manager.set_auto_reply("Auto-reply template")

    with pytest.raises(ValueError, match="Order does not contain a chat_id"):
        await manager.auto_reply(order={"id": "ord123"})

    mock_client.post.assert_not_called()


@pytest.mark.asyncio
async def test_delivery_manager_auto_reply_not_set(mock_client: AsyncMock) -> None:
    manager = DeliveryManager(
        client=mock_client, send_url="http://test.funpay.com/message"
    )

    with pytest.raises(ValueError, match="Auto-reply text is not set"):
        await manager.auto_reply(order={"chat_id": "chat123"})

    mock_client.post.assert_not_called()

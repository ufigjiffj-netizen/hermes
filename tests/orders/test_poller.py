import asyncio
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from hermes.orders.poller import OrderPoller
from hermes.orders.repository import OrderRepository
from hermes.core.network import HttpClient


@pytest.fixture
def mock_repo() -> AsyncMock:
    repo = AsyncMock(spec=OrderRepository)
    repo.is_order_processed.return_value = False
    return repo


@pytest.fixture
def mock_client() -> AsyncMock:
    client = AsyncMock(spec=HttpClient)
    # mock get to return a dummy order
    client.get.return_value = {"orders": [{"id": "ord123", "buyer": "test_user"}]}
    return client


@pytest.mark.asyncio
async def test_order_poller_poll_once(
    mock_repo: AsyncMock, mock_client: AsyncMock
) -> None:
    poller = OrderPoller(
        client=mock_client, repo=mock_repo, url="http://test.funpay.com", interval=1.0
    )

    orders = await poller.poll_once()
    assert len(orders) == 1
    assert orders[0]["id"] == "ord123"

    mock_client.get.assert_called_once_with("http://test.funpay.com")
    mock_repo.is_order_processed.assert_called_once_with("ord123")
    mock_repo.save_order.assert_called_once_with("ord123")


@pytest.mark.asyncio
async def test_order_poller_skips_processed(
    mock_repo: AsyncMock, mock_client: AsyncMock
) -> None:
    mock_repo.is_order_processed.return_value = True
    poller = OrderPoller(
        client=mock_client, repo=mock_repo, url="http://test.funpay.com", interval=1.0
    )

    orders = await poller.poll_once()
    assert len(orders) == 0

    mock_repo.is_order_processed.assert_called_once_with("ord123")
    mock_repo.save_order.assert_not_called()


@pytest.mark.asyncio
@patch("asyncio.sleep", new_callable=AsyncMock)
async def test_order_poller_run_loop(
    mock_sleep: AsyncMock, mock_repo: AsyncMock, mock_client: AsyncMock
) -> None:
    poller = OrderPoller(
        client=mock_client, repo=mock_repo, url="http://test.funpay.com", interval=5.0
    )

    # We will stop the loop after one iteration by side-effecting sleep
    def side_effect(*args, **kwargs):
        poller.stop()
        return asyncio.Future()  # this is ignored because we just want to stop

    mock_sleep.side_effect = lambda x: poller.stop()

    await poller.run()

    mock_sleep.assert_called_once_with(5.0)
    mock_client.get.assert_called_once()


@pytest.mark.asyncio
async def test_order_poller_missing_id(
    mock_repo: AsyncMock, mock_client: AsyncMock
) -> None:
    mock_client.get.return_value = {"orders": [{"buyer": "test"}]}
    poller = OrderPoller(
        client=mock_client, repo=mock_repo, url="http://test.funpay.com", interval=1.0
    )
    orders = await poller.poll_once()
    assert len(orders) == 0
    mock_repo.is_order_processed.assert_not_called()

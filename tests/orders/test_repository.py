import pytest
import pytest_asyncio
from typing import AsyncGenerator
from hermes.core.storage import DatabaseManager
from hermes.orders.repository import OrderRepository


@pytest_asyncio.fixture
async def db_manager() -> AsyncGenerator[DatabaseManager, None]:
    db = DatabaseManager(":memory:")
    await db.connect()

    # Initialize the orders schema
    schema = """
    CREATE TABLE IF NOT EXISTS processed_orders (
        order_id TEXT PRIMARY KEY
    );
    """
    await db.initialize(schema)
    yield db
    await db.shutdown()


@pytest.mark.asyncio
async def test_order_repository_save_and_check(db_manager: DatabaseManager) -> None:
    repo = OrderRepository(db_manager)

    # Check if a non-existent order is processed
    is_processed = await repo.is_order_processed("12345")
    assert not is_processed

    # Save the order
    await repo.save_order("12345")

    # Check again
    is_processed = await repo.is_order_processed("12345")
    assert is_processed

    # Save the same order again shouldn't fail (idempotent)
    await repo.save_order("12345")
    is_processed = await repo.is_order_processed("12345")
    assert is_processed


@pytest.mark.asyncio
async def test_order_repository_no_connection() -> None:
    db = DatabaseManager(":memory:")
    repo = OrderRepository(db)
    with pytest.raises(RuntimeError, match="Database connection not established"):
        await repo.is_order_processed("123")
    with pytest.raises(RuntimeError, match="Database connection not established"):
        await repo.save_order("123")

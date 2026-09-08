import aiosqlite
import pytest

from hermes.core.storage import DatabaseManager


@pytest.mark.asyncio
async def test_database_manager_lifecycle() -> None:
    db = DatabaseManager(":memory:")
    assert db.get_connection() is None

    # Connect to the database
    await db.connect()
    conn = db.get_connection()
    assert isinstance(conn, aiosqlite.Connection)

    # Calling connect again should keep the same connection
    await db.connect()
    assert db.get_connection() is conn

    # Initialize schema
    schema = """
    CREATE TABLE IF NOT EXISTS test_table (
        id INTEGER PRIMARY KEY,
        value TEXT
    );
    """
    await db.initialize(schema)

    # Verify schema initialization
    async with conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='test_table'"
    ) as cursor:
        result = await cursor.fetchone()
        assert result is not None
        assert result[0] == "test_table"

    # Shutdown the database connection
    await db.shutdown()
    assert db.get_connection() is None

    # Shutdown again should be safe
    await db.shutdown()


@pytest.mark.asyncio
async def test_database_manager_uninitialized_error() -> None:
    db = DatabaseManager(":memory:")

    with pytest.raises(RuntimeError, match="Database connection not established."):
        await db.initialize("CREATE TABLE test (id INT);")

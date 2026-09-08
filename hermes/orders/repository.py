from hermes.core.storage import DatabaseManager


class OrderRepository:
    def __init__(self, db_manager: DatabaseManager) -> None:
        self._db = db_manager

    async def is_order_processed(self, order_id: str) -> bool:
        conn = self._db.get_connection()
        if conn is None:
            raise RuntimeError("Database connection not established.")

        async with conn.execute(
            "SELECT 1 FROM processed_orders WHERE order_id = ?", (order_id,)
        ) as cursor:
            result = await cursor.fetchone()
            return result is not None

    async def save_order(self, order_id: str) -> None:
        conn = self._db.get_connection()
        if conn is None:
            raise RuntimeError("Database connection not established.")

        await conn.execute(
            "INSERT OR IGNORE INTO processed_orders (order_id) VALUES (?)", (order_id,)
        )
        await conn.commit()

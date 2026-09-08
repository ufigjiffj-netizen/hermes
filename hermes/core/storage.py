import aiosqlite


class DatabaseManager:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._conn: aiosqlite.Connection | None = None

    def get_connection(self) -> aiosqlite.Connection | None:
        return self._conn

    async def connect(self) -> None:
        if self._conn is None:
            self._conn = await aiosqlite.connect(self.db_path)

    async def initialize(self, schema_script: str) -> None:
        if self._conn is None:
            raise RuntimeError("Database connection not established.")
        await self._conn.executescript(schema_script)
        await self._conn.commit()

    async def shutdown(self) -> None:
        if self._conn is not None:
            await self._conn.close()
            self._conn = None

import json

from hermes.core.storage import DatabaseManager

from .models import Message


class ChatStorage:
    def __init__(self, db: DatabaseManager):
        self.db = db

    async def init_db(self) -> None:
        await self.db.initialize("""
            CREATE TABLE IF NOT EXISTS chat_history (
                node_id TEXT PRIMARY KEY,
                messages TEXT
            );
        """)

    async def save_messages(self, node_id: str, messages: list[Message]) -> None:
        conn = self.db.get_connection()
        if not conn:
            raise RuntimeError("DB connection not established")
        json_data = json.dumps([m.__dict__ for m in messages])
        await conn.execute(
            "REPLACE INTO chat_history (node_id, messages) VALUES (?, ?)",
            (node_id, json_data),
        )
        await conn.commit()

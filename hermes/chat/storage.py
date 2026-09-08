import json
import logging

from hermes.core.storage import DatabaseManager

from .models import Message

logger = logging.getLogger(__name__)


class ChatStorage:
    def __init__(self, db: DatabaseManager):
        self.db = db

    async def init_db(self) -> None:
        await self.db.initialize("""
            CREATE TABLE IF NOT EXISTS chat_history (
                node_id TEXT PRIMARY KEY,
                messages TEXT
            );
            CREATE TABLE IF NOT EXISTS chat_messages (
                id TEXT PRIMARY KEY,
                node_id TEXT NOT NULL,
                author TEXT,
                text TEXT,
                timestamp TEXT,
                raw_json TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_chat_messages_node_id ON chat_messages(node_id);
        """)

    async def save_messages(self, node_id: str, messages: list[Message]) -> None:
        conn = self.db.get_connection()
        if not conn:
            raise RuntimeError("DB connection not established")

        for m in messages:
            json_str = json.dumps(m.__dict__)
            await conn.execute(
                """
                INSERT OR REPLACE INTO chat_messages (id, node_id, author, text, timestamp, raw_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (m.id, node_id, m.author, m.text, m.timestamp, json_str),
            )

        # Merge and update chat_history so it contains all accumulated messages
        all_messages = await self.get_messages(node_id)
        history_json = json.dumps([m.__dict__ for m in all_messages])
        await conn.execute(
            "INSERT OR REPLACE INTO chat_history (node_id, messages) VALUES (?, ?)",
            (node_id, history_json),
        )
        await conn.commit()

    async def get_messages(self, node_id: str) -> list[Message]:
        conn = self.db.get_connection()
        if not conn:
            raise RuntimeError("DB connection not established")
        async with conn.execute(
            "SELECT id, node_id, author, text, timestamp FROM chat_messages WHERE node_id = ? ORDER BY timestamp ASC, id ASC",
            (node_id,),
        ) as cursor:
            rows = await cursor.fetchall()
            return [
                Message(
                    id=row[0],
                    node_id=row[1],
                    author=row[2],
                    text=row[3],
                    timestamp=row[4],
                )
                for row in rows
            ]

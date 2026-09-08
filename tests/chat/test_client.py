import pytest
import pytest_asyncio
from aiohttp import ClientError
from aioresponses import aioresponses

from hermes.chat.client import ChatClient
from hermes.chat.storage import ChatStorage
from hermes.core.network import HttpClient
from hermes.core.storage import DatabaseManager


@pytest_asyncio.fixture
async def db_manager(tmp_path):
    db_file = tmp_path / "test.db"
    manager = DatabaseManager(str(db_file))
    await manager.connect()
    yield manager
    await manager.shutdown()


@pytest.mark.asyncio
async def test_get_dialogs(db_manager):
    async with HttpClient() as http_client:
        storage = ChatStorage(db_manager)
        client = ChatClient(http_client, storage)
        with aioresponses() as m:
            m.get(
                "https://funpay.com/chat/",
                payload={
                    "dialogs": [
                        {"node_id": "n1", "name": "User", "last_message": "hello"}
                    ]
                },
            )
            dialogs = await client.get_dialogs()
            assert len(dialogs) == 1
            assert dialogs[0].node_id == "n1"


@pytest.mark.asyncio
async def test_get_messages(db_manager):
    storage = ChatStorage(db_manager)
    await storage.init_db()
    async with HttpClient() as http_client:
        client = ChatClient(http_client, storage)
        with aioresponses() as m:
            m.get(
                "https://funpay.com/chat/n1/",
                payload={
                    "messages": [
                        {"id": "m1", "author": "me", "text": "hi", "timestamp": "now"}
                    ]
                },
            )
            msgs = await client.get_messages("n1")
            assert len(msgs) == 1
            assert msgs[0].id == "m1"

            conn = db_manager.get_connection()
            async with conn.execute(
                "SELECT messages FROM chat_history WHERE node_id = 'n1'"
            ) as cursor:
                row = await cursor.fetchone()
                assert "hi" in row[0]


@pytest.mark.asyncio
async def test_send_message_success(db_manager):
    async with HttpClient() as http_client:
        storage = ChatStorage(db_manager)
        client = ChatClient(http_client, storage)
        with aioresponses() as m:
            m.post("https://funpay.com/chat/n1/", payload={"status": "ok"})
            res = await client.send_message("n1", "hello")
            assert res is True


@pytest.mark.asyncio
async def test_send_message_error(db_manager):
    async with HttpClient() as http_client:
        storage = ChatStorage(db_manager)
        client = ChatClient(http_client, storage)
        with aioresponses() as m:
            m.post("https://funpay.com/chat/n1/", exception=ClientError("Error"))
            res = await client.send_message("n1", "hello")
            assert res is False


@pytest.mark.asyncio
async def test_save_messages_no_db(tmp_path):
    manager = DatabaseManager(str(tmp_path / "non.db"))
    storage = ChatStorage(manager)
    with pytest.raises(RuntimeError):
        await storage.save_messages("n1", [])

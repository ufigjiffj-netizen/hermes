import aiohttp

from hermes.core.network import HttpClient

from .models import Dialog, Message
from .storage import ChatStorage


class ChatClient:
    def __init__(self, http_client: HttpClient, storage: ChatStorage):
        self.http_client = http_client
        self.storage = storage

    async def get_dialogs(self) -> list[Dialog]:
        response = await self.http_client.get("https://funpay.com/chat/")
        dialogs = []
        for d in response.get("dialogs", []):
            dialogs.append(
                Dialog(
                    node_id=d.get("node_id", ""),
                    name=d.get("name", ""),
                    last_message=d.get("last_message", ""),
                )
            )
        return dialogs

    async def get_messages(self, node_id: str) -> list[Message]:
        url = f"https://funpay.com/chat/{node_id}/"
        response = await self.http_client.get(url)
        messages = []
        for m in response.get("messages", []):
            messages.append(
                Message(
                    id=m.get("id", ""),
                    node_id=node_id,
                    author=m.get("author", ""),
                    text=m.get("text", ""),
                    timestamp=m.get("timestamp", ""),
                )
            )
        await self.storage.save_messages(node_id, messages)
        return messages

    async def send_message(self, node_id: str, text: str) -> bool:
        url = f"https://funpay.com/chat/{node_id}/"
        data = {"message": text}
        try:
            await self.http_client.post(url, json=data)
            return True
        except aiohttp.ClientError:
            return False

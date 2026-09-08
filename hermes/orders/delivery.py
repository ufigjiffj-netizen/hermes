from typing import Any

from hermes.core.network import HttpClient


class DeliveryManager:
    def __init__(self, client: HttpClient, send_url: str) -> None:
        self.client = client
        self.send_url = send_url
        self._auto_reply_text: str | None = None

    def set_auto_reply(self, text: str) -> None:
        """Sets the auto-reply text template."""
        self._auto_reply_text = text

    async def send_message(self, chat_id: str, text: str) -> None:
        """Sends a text message to a specific chat."""
        payload = {"chat_id": chat_id, "text": text}
        await self.client.post(self.send_url, json=payload)

    async def auto_reply(self, order: dict[str, Any]) -> None:
        """Automatically replies to the buyer based on the order info."""
        if not self._auto_reply_text:
            raise ValueError("Auto-reply text is not set.")

        chat_id = order.get("chat_id")
        if not chat_id:
            raise ValueError("Order does not contain a chat_id.")

        await self.send_message(chat_id, self._auto_reply_text)

from hermes.core.network import HttpClient

from .models import Ticket, TicketMessage
from .parsers import parse_csrf_token, parse_ticket_messages, parse_tickets


class SupportClient:
    def __init__(self, http_client: HttpClient):
        self.http_client = http_client

    async def get_tickets(self) -> list[Ticket]:
        html = await self.http_client.get(
            "https://funpay.com/support/", return_text=True
        )
        return parse_tickets(html)

    async def get_ticket_messages(self, ticket_id: str) -> list[TicketMessage]:
        url = f"https://funpay.com/support/{ticket_id}/"
        html = await self.http_client.get(url, return_text=True)
        return parse_ticket_messages(html)

    async def reply_to_ticket(self, ticket_id: str, message: str) -> bool:
        url = f"https://funpay.com/support/{ticket_id}/"
        html = await self.http_client.get(url, return_text=True)
        csrf_token = parse_csrf_token(html)

        data = {"csrf_token": csrf_token, "message": message}
        await self.http_client.post(url, data=data, return_text=True)
        return True

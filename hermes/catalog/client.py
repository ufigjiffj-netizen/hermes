from hermes.core.network import HttpClient

from .models import Category, CommissionInfo, Listing
from .parsers import parse_categories, parse_commission, parse_listings


class CatalogClient:
    def __init__(self, http_client: HttpClient):
        self.http_client = http_client

    async def get_categories(self) -> list[Category]:
        html = await self.http_client.get("https://funpay.com/", return_text=True)
        return parse_categories(html)

    async def get_listings(self, category_id: str) -> list[Listing]:
        url = f"https://funpay.com/lots/{category_id}/"
        html = await self.http_client.get(url, return_text=True)
        return parse_listings(html)

    async def get_commission(self) -> CommissionInfo:
        url = "https://funpay.com/trade/info/"
        html = await self.http_client.get(url, return_text=True)
        return parse_commission(html)

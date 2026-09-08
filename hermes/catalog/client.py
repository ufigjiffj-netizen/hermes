from hermes.core.network import HttpClient

from .models import Category, CommissionInfo, Listing, ListingDetails
from .parsers import (
    parse_categories,
    parse_commission_calc_response,
    parse_listing_details,
    parse_listings,
)


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

    async def get_commission(
        self, node_id: str | int = "81", price: float = 100.0
    ) -> CommissionInfo:
        url = "https://funpay.com/lots/calc"
        headers = {"X-Requested-With": "XMLHttpRequest"}
        data = {"nodeId": str(node_id), "price": str(price)}
        response = await self.http_client.post(url, headers=headers, data=data)
        if isinstance(response, dict):
            return parse_commission_calc_response(response, seller_price=price)
        return CommissionInfo(rate=0.0)

    async def get_listing_details(self, url: str) -> ListingDetails:
        html = await self.http_client.get(url, return_text=True)
        return parse_listing_details(html)

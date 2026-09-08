import pytest
from aioresponses import aioresponses

from hermes.catalog.client import CatalogClient
from hermes.core.network import HttpClient


@pytest.mark.asyncio
async def test_get_categories():
    async with HttpClient() as http_client:
        client = CatalogClient(http_client)
        with aioresponses() as m:
            m.get(
                "https://funpay.com/",
                body='<html><body><div class="game-item"><a href="/games/wow/"><div class="game-title">WoW</div></a></div></body></html>',
            )
            cats = await client.get_categories()
            assert len(cats) == 1
            assert cats[0].id == "wow"


@pytest.mark.asyncio
async def test_get_listings():
    async with HttpClient() as http_client:
        client = CatalogClient(http_client)
        with aioresponses() as m:
            m.get(
                "https://funpay.com/lots/123/",
                body='<html><body><a class="tc-item" href="/lots/999/"><div class="tc-server">EU</div><div class="tc-price">10.5 $</div></a></body></html>',
            )
            listings = await client.get_listings("123")
            assert len(listings) == 1
            assert listings[0].id == "999"
            assert listings[0].price == 10.5


@pytest.mark.asyncio
async def test_get_commission():
    async with HttpClient() as http_client:
        client = CatalogClient(http_client)
        with aioresponses() as m:
            m.get(
                "https://funpay.com/trade/info/",
                body='<html><body><span class="commission-rate">5.5%</span></body></html>',
            )
            info = await client.get_commission()
            assert info.rate == 5.5

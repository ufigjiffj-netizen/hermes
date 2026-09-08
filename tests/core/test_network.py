import pytest
from aioresponses import aioresponses

from hermes.core.network import HttpClient


@pytest.mark.asyncio
async def test_http_client_get():
    with aioresponses() as m:
        m.get("http://test.com", payload={"foo": "bar"})

        async with HttpClient() as client:
            resp = await client.get("http://test.com")
            assert resp["foo"] == "bar"


@pytest.mark.asyncio
async def test_http_client_post():
    with aioresponses() as m:
        m.post("http://test.com", payload={"success": True})

        async with HttpClient() as client:
            resp = await client.post("http://test.com", json={"data": 1})
            assert resp["success"] is True


@pytest.mark.asyncio
async def test_http_client_proxy():
    # To test proxy we just verify it gets passed to the session
    async with HttpClient(proxy="http://localhost:8080") as client:
        assert client.proxy == "http://localhost:8080"

        # Test kwargs proxy injection
        with aioresponses() as m:
            m.get("http://test.com", payload={})
            await client.get("http://test.com")

            m.post("http://test.com", payload={})
            await client.post("http://test.com")


@pytest.mark.asyncio
async def test_http_client_not_initialized():
    client = HttpClient()
    with pytest.raises(AssertionError):
        await client.get("http://test.com")
    with pytest.raises(AssertionError):
        await client.post("http://test.com")

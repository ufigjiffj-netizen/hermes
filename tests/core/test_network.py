from unittest.mock import AsyncMock, MagicMock

import pytest
from aioresponses import aioresponses

from hermes.core.auth import Authenticator
from hermes.core.network import HttpClient
from hermes.core.rate_limit import RateLimiter


@pytest.mark.asyncio
async def test_http_client_get():
    with aioresponses() as m:
        m.get("http://test.com", payload={"foo": "bar"})
        m.get("http://test.com/text", body="plain text response")

        async with HttpClient() as client:
            resp = await client.get("http://test.com")
            assert resp["foo"] == "bar"

            text_resp = await client.get("http://test.com/text", return_text=True)
            assert text_resp == "plain text response"


@pytest.mark.asyncio
async def test_http_client_post():
    with aioresponses() as m:
        m.post("http://test.com", payload={"success": True})
        m.post("http://test.com/text", body="posted text")

        async with HttpClient() as client:
            resp = await client.post("http://test.com", json={"data": 1})
            assert resp["success"] is True

            text_resp = await client.post(
                "http://test.com/text", json={"data": 1}, return_text=True
            )
            assert text_resp == "posted text"


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


@pytest.mark.asyncio
async def test_http_client_with_rate_limiter(monkeypatch: pytest.MonkeyPatch):
    rate_limiter = RateLimiter(rps=100.0, burst=1)
    mock_acquire = AsyncMock()
    monkeypatch.setattr(rate_limiter, "acquire", mock_acquire)
    with aioresponses() as m:
        m.get("http://test.com", payload={"ok": True})
        m.post("http://test.com", payload={"ok": True})

        async with HttpClient(rate_limiter=rate_limiter) as client:
            await client.get("http://test.com")
            await client.post("http://test.com")

        assert mock_acquire.call_count == 2


@pytest.mark.asyncio
async def test_http_client_with_authenticator():
    auth = MagicMock(spec=Authenticator)
    auth.apply = AsyncMock()

    async with HttpClient(authenticator=auth):
        pass

    auth.apply.assert_called_once()

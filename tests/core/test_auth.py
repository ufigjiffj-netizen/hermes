import pytest
from aiohttp import ClientSession

from hermes.core.auth import Authenticator


@pytest.mark.asyncio
async def test_authenticator_injects_golden_key():
    golden_key = "test_golden_key_123"
    authenticator = Authenticator(golden_key)

    async with ClientSession() as session:
        cookies = session.cookie_jar.filter_cookies("https://funpay.com")
        assert "golden_key" not in cookies

        await authenticator.apply(session)

        cookies = session.cookie_jar.filter_cookies("https://funpay.com")
        assert "golden_key" in cookies
        assert cookies["golden_key"].value == golden_key

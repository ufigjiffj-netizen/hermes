import pytest
from aiohttp import ClientSession

from hermes.core.auth import Authenticator
from hermes.core.secrets import SecretStore, _global_store


@pytest.mark.asyncio
async def test_authenticator_injects_golden_key():
    golden_key = "test_golden_key_123"
    authenticator = Authenticator(golden_key)
    assert authenticator.golden_key == golden_key

    async with ClientSession() as session:
        cookies = session.cookie_jar.filter_cookies("https://funpay.com")
        assert "golden_key" not in cookies

        await authenticator.apply(session)

        cookies = session.cookie_jar.filter_cookies("https://funpay.com")
        assert "golden_key" in cookies
        assert cookies["golden_key"].value == golden_key


@pytest.mark.asyncio
async def test_authenticator_with_secret_store():
    store = SecretStore()
    store.set("custom_key", "secret_abc_456")
    authenticator = Authenticator(secret_store=store, key_name="custom_key")
    assert authenticator.golden_key == "secret_abc_456"


@pytest.mark.asyncio
async def test_authenticator_with_global_secret_store():
    _global_store.set("golden_key", "dummy_key")
    authenticator = Authenticator()
    assert authenticator.golden_key == "dummy_key"

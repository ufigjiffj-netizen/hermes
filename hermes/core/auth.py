from aiohttp import ClientSession
from yarl import URL


class Authenticator:
    """Provides authentication functionality for FunPay using the golden_key."""

    def __init__(self, golden_key: str) -> None:
        """Initializes the authenticator with the golden_key.

        Args:
            golden_key: The FunPay golden_key session token.
        """
        self._golden_key = golden_key

    async def apply(self, session: ClientSession) -> None:
        """Injects the golden_key into the given aiohttp session.

        Args:
            session: The aiohttp client session to authenticate.
        """
        session.cookie_jar.update_cookies(
            {"golden_key": self._golden_key},
            response_url=URL("https://funpay.com"),
        )

from aiohttp import ClientSession
from yarl import URL

from hermes.core.secrets import SecretStore, get_secret


class Authenticator:
    """Provides authentication functionality for FunPay using the golden_key."""

    def __init__(
        self,
        golden_key: str | None = None,
        secret_store: SecretStore | None = None,
        key_name: str = "golden_key",
    ) -> None:
        """Initializes the authenticator with the golden_key or a SecretStore.

        Args:
            golden_key: The FunPay golden_key session token.
            secret_store: Optional SecretStore to retrieve the golden_key from.
            key_name: Key name to lookup in secret_store.
        """
        if golden_key is not None:
            self._golden_key = golden_key
        elif secret_store is not None:
            self._golden_key = str(secret_store.get(key_name, "") or "")
        else:
            self._golden_key = str(get_secret(key_name, "") or "")

    @property
    def golden_key(self) -> str:
        return self._golden_key

    async def apply(self, session: ClientSession) -> None:
        """Injects the golden_key into the given aiohttp session.

        Args:
            session: The aiohttp client session to authenticate.
        """
        session.cookie_jar.update_cookies(
            {"golden_key": self._golden_key},
            response_url=URL("https://funpay.com"),
        )

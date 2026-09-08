from typing import Any


class SecretStore:
    """A store for holding secrets securely in memory."""

    def __init__(self) -> None:
        self._secrets: dict[str, str] = {}

    def set(self, key: str, value: str) -> None:
        """Store a secret value."""
        self._secrets[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a secret value."""
        return self._secrets.get(key, default)


_global_store = SecretStore()


def get_secret(key: str, default: Any = None) -> Any:
    """Retrieve a secret from the global store."""
    return _global_store.get(key, default)

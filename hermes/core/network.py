from types import TracebackType
from typing import Any, Self

import aiohttp


class HttpClient:
    """Async HTTP Client with connection pooling and proxy support."""

    def __init__(self, proxy: str | None = None, pool_size: int = 100) -> None:
        self.proxy = proxy
        self._connector = aiohttp.TCPConnector(limit=pool_size)
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> Self:
        self._session = aiohttp.ClientSession(connector=self._connector)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self._session:
            await self._session.close()

    async def get(self, url: str, **kwargs: Any) -> Any:
        assert self._session is not None, (
            "HttpClient must be used as an async context manager"
        )
        if self.proxy and "proxy" not in kwargs:
            kwargs["proxy"] = self.proxy

        async with self._session.get(url, **kwargs) as response:
            response.raise_for_status()
            return await response.json()

    async def post(self, url: str, **kwargs: Any) -> Any:
        assert self._session is not None, (
            "HttpClient must be used as an async context manager"
        )
        if self.proxy and "proxy" not in kwargs:
            kwargs["proxy"] = self.proxy

        async with self._session.post(url, **kwargs) as response:
            response.raise_for_status()
            return await response.json()

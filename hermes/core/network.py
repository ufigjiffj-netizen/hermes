from types import TracebackType
from typing import Any, Self

import aiohttp

from hermes.core.auth import Authenticator
from hermes.core.rate_limit import RateLimiter


class HttpClient:
    """Async HTTP Client with connection pooling, rate limiting, and proxy support."""

    def __init__(
        self,
        proxy: str | None = None,
        pool_size: int = 100,
        rate_limiter: RateLimiter | None = None,
        authenticator: Authenticator | None = None,
    ) -> None:
        self.proxy = proxy
        self.rate_limiter = rate_limiter
        self.authenticator = authenticator
        self._connector = aiohttp.TCPConnector(limit=pool_size)
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> Self:
        self._session = aiohttp.ClientSession(connector=self._connector)
        if self.authenticator:
            await self.authenticator.apply(self._session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self._session:
            await self._session.close()

    async def get(self, url: str, return_text: bool = False, **kwargs: Any) -> Any:
        assert self._session is not None, (
            "HttpClient must be used as an async context manager"
        )
        if self.rate_limiter:
            await self.rate_limiter.acquire()
        if self.proxy and "proxy" not in kwargs:
            kwargs["proxy"] = self.proxy

        async with self._session.get(url, **kwargs) as response:
            response.raise_for_status()
            if return_text:
                return await response.text()
            return await response.json()

    async def post(self, url: str, return_text: bool = False, **kwargs: Any) -> Any:
        assert self._session is not None, (
            "HttpClient must be used as an async context manager"
        )
        if self.rate_limiter:
            await self.rate_limiter.acquire()
        if self.proxy and "proxy" not in kwargs:
            kwargs["proxy"] = self.proxy

        async with self._session.post(url, **kwargs) as response:
            response.raise_for_status()
            if return_text:
                return await response.text()
            return await response.json()

import time
from unittest.mock import patch

import pytest

from hermes.core.rate_limit import RateLimiter


@pytest.mark.asyncio
async def test_rate_limiter_burst():
    limiter = RateLimiter(rps=10, burst=2)
    # Should acquire 2 tokens immediately
    start = time.monotonic()
    await limiter.acquire()
    await limiter.acquire()
    end = time.monotonic()
    assert end - start < 0.1


@pytest.mark.asyncio
async def test_rate_limiter_replenish():
    with patch(
        "hermes.core.rate_limit.time.monotonic", side_effect=[0.0, 0.0, 0.0, 0.1, 0.1]
    ):
        limiter = RateLimiter(rps=10, burst=1)
        await limiter.acquire()
        assert limiter._tokens == 0.0


@pytest.mark.asyncio
async def test_rate_limiter_real_time():
    limiter = RateLimiter(rps=10, burst=1)  # 1 token every 0.1s
    await limiter.acquire()  # bursts

    start = time.monotonic()
    await limiter.acquire()  # needs to wait ~0.1s
    end = time.monotonic()

    assert end - start >= 0.09

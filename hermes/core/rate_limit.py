import asyncio
import time


class RateLimiter:
    """Async Rate Limiter using Token Bucket algorithm."""

    def __init__(self, rps: float, burst: int = 1) -> None:
        self.rps = rps
        self.burst = burst
        self._tokens = float(burst)
        self._last_update = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Acquire a token, waiting if necessary."""
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_update
            self._tokens += elapsed * self.rps
            if self._tokens > self.burst:
                self._tokens = float(self.burst)

            if self._tokens < 1.0:
                wait_time = (1.0 - self._tokens) / self.rps
                self._tokens = 0.0
                self._last_update = now + wait_time
            else:
                self._tokens -= 1.0
                self._last_update = now
                wait_time = 0.0

        if wait_time > 0:
            await asyncio.sleep(wait_time)

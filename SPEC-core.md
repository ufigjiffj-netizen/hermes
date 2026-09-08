# SPEC: Core (Config, Secrets & Network)

## 1. Goals & Business Logic
- Provide a unified, hierarchical YAML configuration system with sensible built-in defaults.
- Securely load and provide access to secrets (e.g., `golden key`, proxy credentials) via a Secret Store.
- Provide a robust async HTTP client wrapper for FunPay using `aiohttp`.
- Implement `RateLimiter` (requests-per-second, burst, backpressure) and HTTP Connection Pooling.
- Support HTTP/SOCKS proxies for outgoing traffic.

## 2. Boundaries & Scope
- **ALWAYS**: Use `asyncio` for HTTP requests. Parse YAML configs strictly.
- **NEVER**: Hardcode secrets. Expose proxy passwords in logs. Block the main event loop with synchronous network calls.
- **ASK**: If a new built-in default needs to be changed significantly from standard behavior.

## 3. Test & Build Commands
- Run linting: `ruff check . && ruff format --check . && mypy .`
- Run tests: `pytest tests/core/ --cov=hermes.core --cov-fail-under=100`

## 4. Success Criteria
- [ ] Config loader successfully parses hierarchical YAML and merges with built-in defaults.
- [ ] Secrets loader correctly retrieves fake golden keys in tests without printing them.
- [ ] Async HTTP client can perform GET/POST requests and handles timeouts gracefully.
- [ ] RateLimiter properly delays requests when the RPS limit is exceeded (verified by timing in tests).
- [ ] Proxy support is cleanly toggled via `enabled: true/false`.
- [ ] Test coverage for the `hermes.core` package is precisely 100%.

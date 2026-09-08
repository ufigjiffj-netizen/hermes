# Hermes Codebase — Unresolved Issues & Audit Backlog

> **Original Review:** September 8, 2026  
> **Scope:** Remaining architectural, spec compliance, parser, and testing gaps across Hermes  
> **Method:** Manual line-by-line code review, spec comparison, automated tooling (`ruff`, `mypy`, `pytest --cov`)  
> **Status:** Updated to exclude the 7 critical findings already resolved in commit `0d8d8c3` (Lots bump logic, Order delivery pipeline, Chat storage message preservation, Chat error propagation, Commission calculator endpoint, Core module wiring, CLI default execution).

---

## Current Automated Check Status

| Check | Result | Notes |
|-------|--------|-------|
| `ruff check .` | ✅ All checks passed | Zero lint errors |
| `ruff format --check .` | ✅ 67 files formatted | Code is properly formatted |
| `mypy .` | ✅ No issues in 51 files | Zero type errors |
| `pytest --cov` | ✅ 73 passed, 100% coverage | All lines covered across all modules |

> [!NOTE]
> The initial 7 critical blockers have been completely resolved and tested. The remaining items below represent secondary bugs, missing specification capabilities, test realism improvements, and operational resilience tasks.

---

## Unresolved Issues by Module

### 1. `hermes/core/` — Infrastructure Layer

| File | Lines | Unresolved Issues & Assessment |
|------|-------|-------------------------------|
| [auth.py](file:///c:/Users/bobik/OneDrive/Documents/hermes/hermes/core/auth.py) | 15 | Hardcodes domain (`funpay.com`), lacks input validation on cookie strings, missing `__repr__` secret masking. |
| [config.py](file:///c:/Users/bobik/OneDrive/Documents/hermes/hermes/core/config.py) | 24 | `DEFAULT_CONFIG` is minimal and lacks comprehensive defaults for all sub-modules. Lacks strict schema validation and YAML error wrapping. |
| [network.py](file:///c:/Users/bobik/OneDrive/Documents/hermes/hermes/core/network.py) | 42 | Uses `assert self._session is not None` instead of raising `RuntimeError` (assertions are stripped when running Python with `-O`). Missing configurable request timeouts (`aiohttp.ClientTimeout`), automatic retry with backoff, and browser User-Agent headers to reduce bot detection risk. |
| [rate_limit.py](file:///c:/Users/bobik/OneDrive/Documents/hermes/hermes/core/rate_limit.py) | 25 | Does not validate `rps > 0` (risks `ZeroDivisionError` if initialized with 0). Lacks backpressure controls. |
| [secrets.py](file:///c:/Users/bobik/OneDrive/Documents/hermes/hermes/core/secrets.py) | 11 | In-memory dictionary wrapper only. Missing file persistence, encryption at rest, and direct environment variable fallback loading. Missing `__repr__` secret masking. |
| [storage.py](file:///c:/Users/bobik/OneDrive/Documents/hermes/hermes/core/storage.py) | 19 | Minimal SQLite connection wrapper. Missing WAL mode (`PRAGMA journal_mode=WAL`), busy timeout (`PRAGMA busy_timeout=5000`), foreign key enforcement (`PRAGMA foreign_keys=ON`), transaction management helpers, and repository abstractions required by `SPEC-storage.md`. |

---

### 2. `hermes/catalog/` — Catalog & Listings

| File | Lines | Unresolved Issues & Assessment |
|------|-------|-------------------------------|
| [models.py](file:///c:/Users/bobik/OneDrive/Documents/hermes/hermes/catalog/models.py) | 9 | Uses `float` for prices (precision/rounding risk in financial math; should consider `Decimal`). Missing `frozen=True` on data models. |
| [parsers.py](file:///c:/Users/bobik/OneDrive/Documents/hermes/hermes/catalog/parsers.py) | 78 | **DOM mutation bug** in `parse_listing_details`: `clone = param` followed by `clone.h5.decompose()` mutates the live caller DOM tree. Needs `copy.copy(param)` or deepcopy. **Price parsing bug**: European number format (e.g. `10,50` with comma as decimal separator) parses incorrectly as `1050.0`. Uses hardcoded Russian strings for label matching. |
| [client.py](file:///c:/Users/bobik/OneDrive/Documents/hermes/hermes/catalog/client.py) | 24 | Hardcoded URLs. Lacks error recovery or domain-specific exceptions for HTML parsing failures and upstream network errors. |

---

### 3. `hermes/chat/` — Chat & Messaging

| File | Lines | Unresolved Issues & Assessment |
|------|-------|-------------------------------|
| [models.py](file:///c:/Users/bobik/OneDrive/Documents/hermes/hermes/chat/models.py) | 5 | Stores `timestamp` as raw string without ISO 8601 validation or timezone awareness. |
| [client.py](file:///c:/Users/bobik/OneDrive/Documents/hermes/hermes/chat/client.py) | 33 | Assumes REST JSON endpoints (`https://funpay.com/chat/...`) which may differ from FunPay's live websocket/long-polling runner. Missing background incoming chat poller/listener. |

---

### 4. `hermes/orders/` — Order Processing

| File | Lines | Unresolved Issues & Assessment |
|------|-------|-------------------------------|
| [repository.py](file:///c:/Users/bobik/OneDrive/Documents/hermes/hermes/orders/repository.py) | 17 | Missing an explicit `init_db()` method (schema creation DDL is currently handled externally). |
| [poller.py](file:///c:/Users/bobik/OneDrive/Documents/hermes/hermes/orders/poller.py) | 41 | No exponential backoff or retry logic on transient network failures during long-running poll iterations. |
| [delivery.py](file:///c:/Users/bobik/OneDrive/Documents/hermes/hermes/orders/delivery.py) | 19 | Delivery auto-reply text is a static string; lacks template substitution (e.g., `{buyer_username}`, `{order_id}`, `{lot_title}`). |

---

### 5. `hermes/support/` — Support Tickets

| File | Lines | Unresolved Issues & Assessment |
|------|-------|-------------------------------|
| [parsers.py](file:///c:/Users/bobik/OneDrive/Documents/hermes/hermes/support/parsers.py) | 40 | CSS selectors are synthetic and unverified against real FunPay support portal HTML. `parse_csrf_token` contains a branch for `isinstance(val, list)` that is only triggered by test mocks. |
| [client.py](file:///c:/Users/bobik/OneDrive/Documents/hermes/hermes/support/client.py) | 20 | Missing `create_ticket()` method (required by `SPEC-support.md`). `reply_to_ticket()` returns `True` even if the retrieved CSRF token is empty. No pre-check for authentication state before attempting support operations. |

---

### 6. `hermes/cli/` — CLI Entry Point

| File | Lines | Unresolved Issues & Assessment |
|------|-------|-------------------------------|
| [main.py](file:///c:/Users/bobik/OneDrive/Documents/hermes/hermes/cli/main.py) | 98 | Hardcodes SQL table DDL directly inside the application runner instead of delegating to repository `init_db()` methods. Missing `hermes/__main__.py` entry point (`python -m hermes` fails). Does not yet wire or expose CLI commands for Chat, Catalog, Support, or Secret management. |

---

## Test Quality & Realism Gaps

> [!WARNING]
> While statement coverage is 100.00%, the test suite still relies on synthetic fixtures and lacks negative scenario testing.

### Remaining Patterns of Concern

1. **Synthetic HTML Fixtures:** HTML parser tests in `tests/catalog/` and `tests/support/` rely on minimal 1-line HTML strings created specifically to match selectors. They do not test against realistic FunPay HTML snapshots, Cloudflare challenge pages, or malformed/truncated documents.
2. **Missing Negative & Edge Tests:** Lacks explicit tests for HTTP 401 Unauthorized, 403 Forbidden, 429 Too Many Requests, 500/502/503 upstream errors, socket timeouts, SQLite database locks under concurrent access, and expired sessions.
3. **Leftover Debug File:** `test_debug.py` remains in the repository root and should be deleted or relocated.

---

## Spec vs. Implementation Gap Analysis (Remaining Unimplemented Features)

| Spec Requirement | Status | Details |
|-----------------|--------|---------|
| `hermes -t` config validation | ❌ **Missing** | CLI flag to validate configuration syntax without running |
| `hermes -T` effective config | ❌ **Missing** | CLI flag to print resolved configuration values |
| `hermes -s reload` hot reload | ❌ **Missing** | Signal/command to reload configuration during execution |
| `hermes secrets` CLI commands | ❌ **Missing** | Command suite to manage, set, and view secrets |
| `hermes account auth test` | ❌ **Missing** | CLI command to verify golden_key validity against FunPay |
| Missing `hermes/__main__.py` | ❌ **Missing** | Running `python -m hermes` is not supported |
| SQLite WAL mode / busy timeout | ❌ **Missing** | Pragmas not set; risks `database is locked` under concurrent writes |
| Event Bus (`order.created`, etc.) | ❌ **Missing** | Decoupled event publish/subscribe system |
| Incoming message monitoring | ❌ **Missing** | Background long-polling or websocket listener for incoming customer messages |
| New ticket submission (`create_ticket`) | ❌ **Missing** | Spec requires creating tickets; only `reply_to_ticket` exists |
| PostgreSQL backend support | ❌ **Missing** | No abstraction layer for `asyncpg` / PostgreSQL |
| Strict config schema validation | ❌ **Missing** | Missing Pydantic / dataclass validation schema for YAML config |
| Encrypted secret vault | ❌ **Missing** | Sensitive keys stored only in plaintext memory |
| Browser User-Agent headers | ❌ **Missing** | Default aiohttp user agent header risks anti-bot flagging |
| Auth pre-verification in support | ❌ **Missing** | Support operations do not check auth state before sending requests |

---

## Prioritized Action Plan for Remaining Items

### P0 — Functional Bugs & Integrity
1. **Fix `parse_listing_details` DOM mutation bug:** Use `copy.copy(param)` instead of `clone = param` before calling `.decompose()` in [hermes/catalog/parsers.py](file:///c:/Users/bobik/OneDrive/Documents/hermes/hermes/catalog/parsers.py).
2. **Fix European price parsing:** Support comma decimal delimiters (`10,50` -> `10.50`) in [hermes/catalog/parsers.py](file:///c:/Users/bobik/OneDrive/Documents/hermes/hermes/catalog/parsers.py).
3. **Replace assertions in `HttpClient`:** Replace `assert self._session is not None` with explicit `RuntimeError("HttpClient session not started. Use 'async with client:'")` in [hermes/core/network.py](file:///c:/Users/bobik/OneDrive/Documents/hermes/hermes/core/network.py).

### P1 — Spec Compliance & Architecture
4. **Add `hermes/__main__.py`:** Enable execution via `python -m hermes`.
5. **Encapsulate DDL in repositories:** Move SQLite table initialization into `OrderRepository.init_db()` and `ChatStorage.init_db()` rather than running raw DDL in `main.py`.
6. **Configure SQLite production pragmas:** Enable `PRAGMA journal_mode=WAL;`, `PRAGMA busy_timeout=5000;`, and `PRAGMA foreign_keys=ON;` in [hermes/core/storage.py](file:///c:/Users/bobik/OneDrive/Documents/hermes/hermes/core/storage.py).
7. **Implement `create_ticket()` in `SupportClient`:** Add ticket creation endpoint and parser as specified in `SPEC-support.md`.

### P2 — Robustness, Security & Test Realism
8. **Add timeouts and headers to `HttpClient`:** Set realistic `aiohttp.ClientTimeout` defaults and default browser `User-Agent` headers.
9. **Poller exponential backoff:** Add transient error catching with backoff delays to `OrderPoller.run()`.
10. **Add input validation to `RateLimiter`:** Raise `ValueError` if `rps <= 0`.
11. **Secret masking:** Add `__repr__` methods to `Authenticator` and `SecretStore` to prevent token leakage in debug logs.
12. **Clean up project root:** Remove `test_debug.py`.
13. **Realistic HTML fixtures:** Capture and store realistic FunPay HTML samples in `tests/fixtures/` and test parsers against real structures.
14. **Negative integration tests:** Add test cases for network disconnects, timeouts, 4xx/5xx HTTP errors, and malformed HTML responses.

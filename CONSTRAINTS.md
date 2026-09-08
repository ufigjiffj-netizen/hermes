# Constraints

Last reviewed: 2026-09-08

## Floor (always enforced, no setup required)

- No new suppression comments: `# type: ignore`, `# noqa`
- No unimplemented stubs: `raise NotImplementedError`, `pass` in empty blocks without explanation
- No skipped or deleted tests without a reason in the commit message
- No secrets in source
- This file does not get weakened to make a change pass

## Enforced with numbers

| Dimension | Rule | Checked by | Runs at |
|-----------|------|-----------|---------|
| Types | Zero type errors | `mypy .` | every edit |
| Lint | Zero errors from our config | `ruff check .` | every edit |
| Format | Code formatted | `ruff format --check .` | every edit |
| Secrets | No secrets in source | `gitleaks detect --redact` | CI |
| Coverage | **100%** test coverage | `pytest --cov=. --cov-fail-under=100` | task end, CI |
| Security: deps | Nothing at high or above | `pip-audit` or `safety` | CI |

## Architecture & Boundaries

- **Async First**: All I/O operations (HTTP, DB) must use `async`/`await`.
- **Database**: SQLite via `aiosqlite` (or SQLAlchemy async). Optional Postgres via `asyncpg`.
- **No Heavy Queues**: Do not use Redis, RabbitMQ, Kafka, Celery. Use `asyncio.Queue` or similar built-ins.
- **Config**: YAML based configuration. Boolean directives must use `enabled: true/false`.
- **Plugins**: Must be separate from Core (`hermes/core` vs `hermes/plugins`).
- **Language**: All code comments and variables MUST be in English.
- **Git & Versioning**: Follow Git Flow (`develop`, `feature/*`). Branch names must be conventional. Use Semantic Versioning. Commit messages and PR descriptions must be concise and short.

## Lifecycle Scripts (to be added to pyproject.toml / Makefile)

- `check:fast`: `ruff check . && ruff format --check . && mypy .`
- `check:task`: `make check:fast && pytest --cov=. --cov-fail-under=100`

## Exceptions

| ID | Rule | Path | Reason | Owner | Expires |
|----|------|------|--------|-------|---------|
| None | | | | | |

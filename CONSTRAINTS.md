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
- **Language**: All specs, code comments, and variable names MUST be in English.
- **Git Flow & Versioning**:
  - Always branch off `dev` for new features (e.g., `feat/feature-name`).
  - Open a PR to `dev`, test, review, and squash-merge it.
  - Delete feature branches immediately after merging into `dev`.
  - Commits must use Conventional Commits (e.g., `feat: ...`, `fix: ...`) and be short and concise.
  - Create a PR from `dev` to `main` for releases. Tag the release on `main` using Semantic Versioning (e.g., `v1.2.0`), which will automatically trigger the Release workflow and generate a Changelog.

## Lifecycle Scripts (to be added to pyproject.toml / Makefile)

- `check:fast`: `ruff check . && ruff format --check . && mypy .`
- `check:task`: `make check:fast && pytest --cov=. --cov-fail-under=100`

## Exceptions

| ID | Rule | Path | Reason | Owner | Expires |
|----|------|------|--------|-------|---------|
| None | | | | | |

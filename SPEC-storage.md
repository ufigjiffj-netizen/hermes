# SPEC: Core Storage

## 1. Goals & Business Logic
- Provide an async interface to SQLite using `aiosqlite`.
- Ensure connection reliability and proper closure on shutdown.
- Support basic database initialization (table creation/migrations).
- Hide SQL complexity behind simple async repository/DAO patterns.
- Do NOT use Redis, Postgres (unless explicitly configured), or external queues. Keep it simple and local.

## 2. Boundaries & Scope
- **ALWAYS**: Use `async`/`await` for all database interactions. Close connections cleanly.
- **NEVER**: Use synchronous `sqlite3` calls. Block the event loop with large queries.
- **ASK**: If a complex migration tool (like `alembic`) is needed instead of simple schema scripts.

## 3. Test & Build Commands
- Run linting: `make check:fast`
- Run tests: `pytest tests/core/test_storage.py --cov=hermes.core.storage --cov-fail-under=100`

## 4. Success Criteria
- [ ] Database connection manager can establish and gracefully close an `aiosqlite` connection.
- [ ] Basic table creation (schema initialization) executes without errors.
- [ ] Test coverage for `hermes.core.storage` is precisely 100%.
- [ ] No typing or linting errors.

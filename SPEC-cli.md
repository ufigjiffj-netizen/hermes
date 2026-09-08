# SPEC: Command Line Interface (CLI)

## 1. Goals & Business Logic
- Provide a simple entry point (`__main__.py` or similar) to start Hermes.
- Assemble all components (Config, Storage, Auth, Poller, BumpManager).
- Provide basic CLI arguments (e.g., `--config`).

## 2. Boundaries & Scope
- **ALWAYS**: Ensure a graceful shutdown via `asyncio` signals when the user presses `Ctrl+C`.
- **NEVER**: Add heavy CLI frameworks like `click` or `typer` if standard `argparse` suffices for an MVP.
- **ASK**: N/A

## 3. Test & Build Commands
- Run linting: `make check:fast`
- Run tests: `pytest tests/cli/ --cov=hermes.cli --cov-fail-under=100`

## 4. Success Criteria
- [ ] `hermes.cli` module with an entry point.
- [ ] Graceful shutdown logic implemented.
- [ ] Test coverage for `hermes.cli` is 100%.

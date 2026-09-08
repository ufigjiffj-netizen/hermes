# Changelog

All notable changes to this project will be documented in this file.

## [v1.0.0] - 2026-09-08
### Added
* `hermes.cli`: Added CLI entrypoint with graceful shutdown (`feat: add cli entrypoint`)
* `hermes.lots`: Added async lots bump manager (`feat: add async lots bump manager`)
* `hermes.orders`: Added async orders poller and delivery manager (`feat: add async orders poller and delivery manager`)

### Fixed
* CI: Added `types-PyYAML` to fix mypy in CI.
* Tests: Removed unused dead code to restore 100% test coverage.
* CI: Fixed `pip` cache dependency path.

## [v0.1.0] - 2026-09-08

### Added
* `hermes.core.auth`: Added async authenticator (`feat: add async authenticator`)
* `hermes.core.storage`: Added async SQLite storage manager (`feat: add async sqlite storage manager`)
* `hermes.core.network`: Added async HTTP client and rate limiter (`feat: add async http client`, `feat: add async rate limiter`)
* `hermes.core.config`: Added YAML config loader (`feat: add yaml config loader`)
* `hermes.core.secrets`: Added secure secret store (`feat: add secret store`)
* `CI/CD`: GitHub Actions workflow with 100% coverage gating, linting, and secret scanning.

### Fixed
* CI: Ignored spec files in gitleaks to fix pipeline.
* Build: Pinned `aiohttp` version for `aioresponses` compatibility.

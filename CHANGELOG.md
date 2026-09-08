# Changelog

All notable changes to this project will be documented in this file.

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

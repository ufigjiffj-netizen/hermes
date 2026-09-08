# SPEC: Lots Auto-Bump

## 1. Goals & Business Logic
- Automate the process of "bumping" (поднятие) lots on FunPay.
- Periodically check if lots can be bumped and send the required request.
- Manage intervals and logic for auto-bumping cleanly.

## 2. Boundaries & Scope
- **ALWAYS**: Use async delays between bumps. Respect rate limits.
- **NEVER**: Send bump requests for deactivated lots.
- **ASK**: If there is a specific FunPay API endpoint for bumping, or if it requires HTML parsing.

## 3. Test & Build Commands
- Run linting: `make check:fast`
- Run tests: `pytest tests/lots/ --cov=hermes.lots --cov-fail-under=100`

## 4. Success Criteria
- [ ] `BumpManager` component that async-loops to bump lots.
- [ ] Test coverage for `hermes.lots` is 100%.

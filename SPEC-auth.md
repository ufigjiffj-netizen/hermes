# SPEC: Core Auth

## 1. Goals & Business Logic
- Provide authentication functionality for FunPay using the `golden_key`.
- Maintain session cookies to ensure requests appear authorized.
- Integrate with `hermes.core.secrets` to retrieve the key, and `hermes.core.network` to apply it.

## 2. Boundaries & Scope
- **ALWAYS**: Use secure secret extraction.
- **NEVER**: Hardcode the `golden_key` anywhere.
- **ASK**: If FunPay requires additional login steps beyond just providing the `golden_key` cookie.

## 3. Test & Build Commands
- Run linting: `make check:fast`
- Run tests: `pytest tests/core/test_auth.py --cov=hermes.core.auth --cov-fail-under=100`

## 4. Success Criteria
- [ ] Implement `Authenticator` that correctly sets the `golden_key` cookie on an `aiohttp` session.
- [ ] Test coverage for `hermes.core.auth` is 100%.
- [ ] No typing or linting errors.

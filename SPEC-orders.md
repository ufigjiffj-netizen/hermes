# SPEC: Orders Polling & Delivery

## 1. Goals & Business Logic
- Periodically poll the FunPay API or parse pages to detect new orders/purchases.
- Maintain state of processed orders in the local SQLite database to prevent double-delivery.
- Integrate with `hermes.core.network` to execute requests.
- Provide a clear interface for auto-delivery (sending messages/items to the buyer).

## 2. Boundaries & Scope
- **ALWAYS**: Acknowledge orders only after successful database recording. Use async delays (`asyncio.sleep`) between polls.
- **NEVER**: Use tight `while True` loops without yielding/sleeping. Don't process orders synchronously.
- **ASK**: How often should polling occur (interval defaults)? Does auto-delivery support attachments?

## 3. Test & Build Commands
- Run linting: `make check:fast`
- Run tests: `pytest tests/orders/test_polling.py --cov=hermes.orders --cov-fail-under=100`

## 4. Success Criteria
- [ ] `OrderPoller` component that async-loops to fetch new orders.
- [ ] `OrderRepository` component that tracks processed order IDs in the DB.
- [ ] `DeliveryManager` component to send text responses back to the chat.
- [ ] Test coverage for `hermes.orders` is 100%.

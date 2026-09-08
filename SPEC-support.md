# SPEC: Support (Helpdesk & Tickets)

## 1. Goals & Business Logic
- Interface with the FunPay Technical Support system to retrieve existing support tickets and view responses.
- Allow submission of new support tickets or replies to existing threads.
- Utilize the async network client and session authentication (Golden Key).

## 2. Boundaries & Scope
- **ALWAYS**: Ensure requests include the correct CSRF tokens and session cookies. Validate that the user is authenticated before attempting support actions.
- **NEVER**: Delete tickets (unless explicitly supported and requested by the user, though FunPay typically doesn't allow ticket deletion).
- **ASK**: Does ticket submission require solving any specific in-page challenges, or is it a standard POST request?

## 3. Test & Build Commands
- Run linting: `ruff check . && ruff format --check . && mypy .`
- Run tests: `pytest tests/support/ --cov=hermes.support --cov-fail-under=100`

## 4. Success Criteria
- [ ] `SupportClient.get_tickets()` fetches a list of the user's active/closed tickets.
- [ ] `SupportClient.get_ticket_messages(ticket_id)` extracts the chat history for a specific ticket.
- [ ] `SupportClient.reply_to_ticket(ticket_id, message)` successfully sends a reply.
- [ ] Test coverage for the `hermes.support` package is 100%, using mocked HTTP responses.

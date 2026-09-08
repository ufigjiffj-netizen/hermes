# SPEC: Chat (Messages & Conversations)

## 1. Goals & Business Logic
- Provide tools to fetch chat histories, send messages, and monitor incoming messages on FunPay.
- Implement an async `ChatClient` that uses `hermes.core.network.Client`.
- Save chat histories in JSON format (via `hermes.core.storage`) while keeping the design flexible enough for a future Postgres migration.

## 2. Boundaries & Scope
- **ALWAYS**: Use async operations. Store data using the storage manager interface.
- **NEVER**: Lose messages. Ignore network errors during chat sending.
- **ASK**: Does FunPay use WebSockets for real-time chat, or is it strictly long-polling/periodic HTTP requests?

## 3. Test & Build Commands
- Run linting: `ruff check . && ruff format --check . && mypy .`
- Run tests: `pytest tests/chat/ --cov=hermes.chat --cov-fail-under=100`

## 4. Success Criteria
- [ ] `ChatClient.get_dialogs()` fetches recent active conversations.
- [ ] `ChatClient.get_messages(node_id)` fetches the chat history for a specific conversation.
- [ ] `ChatClient.send_message(node_id, text)` successfully sends a message.
- [ ] Chat histories are correctly persisted using the JSON storage implementation.
- [ ] Test coverage for `hermes.chat` is 100%.

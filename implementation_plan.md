# Implementation Plan

## Goal Description
Expand the existing `hermes` FunPay wrapper by adding three new core modules: `catalog`, `support`, and `chat`. These modules will enable parsing of listings and categories, handling technical support tickets, and managing chat histories, respectively. `beautifulsoup4` will be integrated for HTML parsing.

## User Review Required
- Please review the file structure below. We are separating models (dataclasses), parsers (BS4 logic), and the async client into different files for maintainability.

## Proposed Changes

### Dependencies
#### [MODIFY] [requirements.txt](file:///c:/Users/bobik/OneDrive/Documents/hermes/requirements.txt)
- Add `beautifulsoup4`
#### [MODIFY] [requirements-dev.txt](file:///c:/Users/bobik/OneDrive/Documents/hermes/requirements-dev.txt)
- Ensure types for beautifulsoup are present if necessary (e.g., `types-beautifulsoup4`).

---

### Catalog Component
#### [NEW] [hermes/catalog/__init__.py](file:///c:/Users/bobik/OneDrive/Documents/hermes/hermes/catalog/__init__.py)
#### [NEW] [hermes/catalog/models.py](file:///c:/Users/bobik/OneDrive/Documents/hermes/hermes/catalog/models.py)
- Dataclasses/Pydantic models for `Category`, `Listing`, `CommissionInfo`.
#### [NEW] [hermes/catalog/parsers.py](file:///c:/Users/bobik/OneDrive/Documents/hermes/hermes/catalog/parsers.py)
- Pure functions taking raw HTML and returning models using `beautifulsoup4`.
#### [NEW] [hermes/catalog/client.py](file:///c:/Users/bobik/OneDrive/Documents/hermes/hermes/catalog/client.py)
- `CatalogClient` for making HTTP requests and calling parsers.
#### [NEW] [tests/catalog/test_parsers.py](file:///c:/Users/bobik/OneDrive/Documents/hermes/tests/catalog/test_parsers.py)
#### [NEW] [tests/catalog/test_client.py](file:///c:/Users/bobik/OneDrive/Documents/hermes/tests/catalog/test_client.py)

---

### Support Component
#### [NEW] [hermes/support/__init__.py](file:///c:/Users/bobik/OneDrive/Documents/hermes/hermes/support/__init__.py)
#### [NEW] [hermes/support/models.py](file:///c:/Users/bobik/OneDrive/Documents/hermes/hermes/support/models.py)
- Models for `Ticket`, `TicketMessage`.
#### [NEW] [hermes/support/client.py](file:///c:/Users/bobik/OneDrive/Documents/hermes/hermes/support/client.py)
- `SupportClient` for fetching and replying to tickets.
#### [NEW] [tests/support/test_client.py](file:///c:/Users/bobik/OneDrive/Documents/hermes/tests/support/test_client.py)

---

### Chat Component
#### [NEW] [hermes/chat/__init__.py](file:///c:/Users/bobik/OneDrive/Documents/hermes/hermes/chat/__init__.py)
#### [NEW] [hermes/chat/models.py](file:///c:/Users/bobik/OneDrive/Documents/hermes/hermes/chat/models.py)
- Models for `ConversationNode`, `ChatMessage`.
#### [NEW] [hermes/chat/client.py](file:///c:/Users/bobik/OneDrive/Documents/hermes/hermes/chat/client.py)
- `ChatClient` to interact with FunPay messages.
#### [NEW] [tests/chat/test_client.py](file:///c:/Users/bobik/OneDrive/Documents/hermes/tests/chat/test_client.py)

## Verification Plan
### Automated Tests
- `pytest tests/catalog/ --cov=hermes.catalog --cov-fail-under=100`
- `pytest tests/support/ --cov=hermes.support --cov-fail-under=100`
- `pytest tests/chat/ --cov=hermes.chat --cov-fail-under=100`

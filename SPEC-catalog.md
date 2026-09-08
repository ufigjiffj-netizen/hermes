# SPEC: Catalog (Categories, Listings & Parsers)

## 1. Goals & Business Logic
- Provide tools to fetch and parse public categories, listings, product titles, descriptions, prices, and commission rates from FunPay.
- Use `beautifulsoup4` for HTML parsing, ensuring resilient extraction.
- Implement an async `CatalogClient` that relies on the existing `hermes.core.network.Client`.
- Expose typed Python dataclasses/Pydantic models (e.g., `Category`, `Listing`, `CommissionInfo`) rather than raw dictionaries.

## 2. Boundaries & Scope
- **ALWAYS**: Use the existing async HTTP client (`hermes.core.network.Client`) to benefit from rate limits and proxy settings. Handle HTML parsing exceptions gracefully.
- **NEVER**: Use synchronous requests (`requests` module). Scrape authenticated-only data in this module (that belongs to orders/auth).
- **ASK**: If FunPay radically changes its HTML structure, should we fallback to returning raw HTML or raise a specific `ParsingError`?

## 3. Test & Build Commands
- Run linting: `ruff check . && ruff format --check . && mypy .`
- Run tests: `pytest tests/catalog/ --cov=hermes.catalog --cov-fail-under=100`

## 4. Success Criteria
- [ ] `BeautifulSoup4` is added to `requirements.txt` and `requirements-dev.txt`.
- [ ] `CatalogClient.get_categories()` successfully parses the main page and returns a list of categories.
- [ ] `CatalogClient.get_listings(category_id)` fetches listings with correct titles, descriptions, and prices.
- [ ] Commission rates are accurately extracted from the appropriate page.
- [ ] Test coverage for the `hermes.catalog` package is 100%, using mocked HTML files via `pytest` fixtures.

# FunPay API & Scraping Notes

This document contains useful information discovered about FunPay's undocumented APIs and web scraping patterns for future reference or tool development.

## 1. Scraping Detailed Lot Descriptions
- **Context:** The public catalog pages (e.g. `https://funpay.com/lots/81/`) only contain the "short description" snippet inside `<div class="tc-desc">`.
- **Method:** To get the full detailed description of an offer, you must fetch the individual lot page URL directly (e.g., `https://funpay.com/lots/offer?id=76632397`).
- **Parsing:** On the individual lot page, the descriptions are contained within `<div class="param-item">` blocks. 
  - Look for an `<h5>` containing `"Подробное описание"` (Detailed Description) or `"Краткое описание"` (Short Description).
  - The actual text is either inside a nested `<div>` or directly within the `param-item` node. 
- **Implementation Status:** Supported natively by `CatalogClient.get_listing_details(url)` via `parse_listing_details()`.

## 2. Scraping Specific User's Lots
- **Context:** If you need to view all active lots belonging to a specific seller across all categories.
- **Method:** Fetch the user's public profile page: `https://funpay.com/users/{user_id}/`.
- **Parsing:** The user profile page uses the exact same listing HTML structure as standard catalog pages. You can use the standard catalog `parse_listings(html)` function to extract all lots (`<a class="tc-item">`).
- **Implementation Status:** You can pass the user profile HTML to the existing `parse_listings` method out of the box.

## 3. Retrieving Section Commission Rates
- **Context:** FunPay charges a category-specific commission, but the rate is not statically displayed in the HTML of the category page.
- **Historical Note:** `https://funpay.com/trade/info/` is deprecated and returns a 404 Not Found.
- **Method:** FunPay calculates the commission and buyer price dynamically via an internal API endpoint when a user types a price in the "Create Offer" page.
- **API Endpoint:** `POST https://funpay.com/lots/calc`
- **Request Format:** 
  - Must use an authenticated session (requires `golden_key`).
  - Requires the `X-Requested-With: XMLHttpRequest` header to simulate an AJAX request.
  - Form Data Payload: 
    - `nodeId`: The category/section ID (e.g., `81` for WoW).
    - `price`: The seller's base price in numbers (e.g., `100`).
- **Response:** The server returns a JSON object containing the calculated buyer prices, from which you can easily deduce the commission percentage for that specific `nodeId`.

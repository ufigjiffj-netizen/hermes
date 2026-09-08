from bs4 import BeautifulSoup

from .models import Category, CommissionInfo, Listing, ListingDetails


class ParsingError(Exception):
    """Exception raised for errors in the parsing HTML."""


def parse_categories(html: str) -> list[Category]:
    soup = BeautifulSoup(html, "html.parser")
    categories = []
    for elem in soup.find_all("div", class_="game-item"):
        a_tag = elem.find("a")
        if a_tag and "href" in a_tag.attrs:
            url = a_tag["href"]
            name_div = elem.find("div", class_="game-title")
            name = name_div.text.strip() if name_div else "Unknown"
            cat_id = url.strip("/").split("/")[-1] if url else ""
            categories.append(Category(id=cat_id, name=name, url=url))

    return categories


def parse_listings(html: str) -> list[Listing]:
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    for elem in soup.find_all("a", class_="tc-item"):
        url = elem.get("href", "")
        list_id = url.strip("/").split("/")[-1] if url else ""

        title_div = elem.find("div", class_="tc-server")
        title = title_div.text.strip() if title_div else ""

        desc_div = elem.find("div", class_="tc-desc")
        description = desc_div.text.strip() if desc_div else ""

        price_div = elem.find("div", class_="tc-price")
        price_text = price_div.text.strip() if price_div else "0"
        try:
            price = float("".join(c for c in price_text if c.isdigit() or c == "."))
        except ValueError:
            price = 0.0

        seller_div = elem.find("div", class_="media-user-name")
        seller_name = seller_div.text.strip() if seller_div else "Unknown"

        listings.append(
            Listing(
                id=list_id,
                title=title,
                description=description,
                price=price,
                seller_name=seller_name,
                url=url,
            )
        )
    return listings


def parse_commission(html: str) -> CommissionInfo:
    soup = BeautifulSoup(html, "html.parser")
    comm_div = soup.find("span", class_="commission-rate")
    if comm_div:
        text = comm_div.text.strip().replace("%", "")
        try:
            return CommissionInfo(rate=float(text))
        except ValueError:
            raise ParsingError("Invalid commission format")
    return CommissionInfo(rate=0.0)


def parse_listing_details(html: str) -> ListingDetails:
    soup = BeautifulSoup(html, "html.parser")
    detailed = ""
    short = ""
    for param in soup.find_all("div", class_="param-item"):
        h5 = param.find("h5")
        if not h5:
            continue
        text_div = param.find("div")
        text = text_div.text.strip() if text_div else ""
        title = h5.text.strip()
        if title == "Подробное описание":
            detailed = text
        elif title == "Краткое описание":
            short = text
            
        # FunPay sometimes puts text directly in param-item when there is no div inside
        if not text_div:
            # We can extract text excluding h5
            clone = param
            clone.h5.decompose()
            text = clone.text.strip()
            if title == "Подробное описание":
                detailed = text
            elif title == "Краткое описание":
                short = text
                
    return ListingDetails(detailed_description=detailed, short_description=short)

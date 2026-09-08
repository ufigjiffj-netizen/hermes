import pytest

from hermes.catalog.parsers import (
    ParsingError,
    parse_categories,
    parse_commission,
    parse_listings,
)


def test_parse_categories():
    html = """
    <html><body>
        <div class="game-item">
            <a href="/games/wow/">
                <div class="game-title">World of Warcraft</div>
            </a>
        </div>
        <div class="game-item">
            <a href="/games/csgo/">
                <div class="game-title">CS:GO</div>
            </a>
        </div>
        <div class="game-item">
            <a href="/games/no-title/">
            </a>
        </div>
    </body></html>
    """
    categories = parse_categories(html)
    assert len(categories) == 3
    assert categories[0].name == "World of Warcraft"
    assert categories[0].id == "wow"
    assert categories[0].url == "/games/wow/"
    assert categories[1].name == "CS:GO"
    assert categories[2].name == "Unknown"


def test_parse_listings():
    html = """
    <html><body>
        <a class="tc-item" href="/lots/123/">
            <div class="tc-server">EU Server</div>
            <div class="tc-desc">Gold 1M</div>
            <div class="tc-price">10.50 $</div>
            <div class="media-user-name">ProSeller</div>
        </a>
        <a class="tc-item" href="/lots/456/">
            <div class="tc-server">US Server</div>
            <div class="tc-price">invalid</div>
        </a>
    </body></html>
    """
    listings = parse_listings(html)
    assert len(listings) == 2
    assert listings[0].id == "123"
    assert listings[0].title == "EU Server"
    assert listings[0].description == "Gold 1M"
    assert listings[0].price == 10.50
    assert listings[0].seller_name == "ProSeller"

    assert listings[1].id == "456"
    assert listings[1].title == "US Server"
    assert listings[1].price == 0.0


def test_parse_commission():
    html_valid = "<html><body><span class='commission-rate'>5.5%</span></body></html>"
    info = parse_commission(html_valid)
    assert info.rate == 5.5

    html_invalid = (
        "<html><body><span class='commission-rate'>invalid</span></body></html>"
    )
    with pytest.raises(ParsingError):
        parse_commission(html_invalid)

    html_empty = "<html><body></body></html>"
    info_empty = parse_commission(html_empty)
    assert info_empty.rate == 0.0

from unittest.mock import patch

import pytest
from aioresponses import aioresponses

from hermes.core.network import HttpClient
from hermes.support.client import SupportClient
from hermes.support.parsers import parse_csrf_token


@pytest.mark.asyncio
async def test_get_tickets():
    async with HttpClient() as http_client:
        client = SupportClient(http_client)
        with aioresponses() as m:
            html = """
            <div class="ticket-item">
                <a href="/support/123/">
                    <div class="ticket-subject">Help me</div>
                    <div class="ticket-status">Open</div>
                </a>
            </div>
            """
            m.get("https://funpay.com/support/", body=html)
            tickets = await client.get_tickets()
            assert len(tickets) == 1
            assert tickets[0].id == "123"
            assert tickets[0].subject == "Help me"
            assert tickets[0].status == "Open"


@pytest.mark.asyncio
async def test_get_ticket_messages():
    async with HttpClient() as http_client:
        client = SupportClient(http_client)
        with aioresponses() as m:
            html = """
            <div class="message-item" data-id="m1">
                <div class="message-author">User1</div>
                <div class="message-text">My issue</div>
                <div class="message-timestamp">12:00</div>
            </div>
            """
            m.get("https://funpay.com/support/123/", body=html)
            msgs = await client.get_ticket_messages("123")
            assert len(msgs) == 1
            assert msgs[0].id == "m1"
            assert msgs[0].author == "User1"
            assert msgs[0].text == "My issue"


@pytest.mark.asyncio
async def test_reply_to_ticket():
    async with HttpClient() as http_client:
        client = SupportClient(http_client)
        with aioresponses() as m:
            html = '<input name="csrf_token" value="abc123token" />'
            m.get("https://funpay.com/support/123/", body=html)
            m.post("https://funpay.com/support/123/", body="ok")
            res = await client.reply_to_ticket("123", "Here is my reply")
            assert res is True


def test_parse_csrf_token_missing():
    assert parse_csrf_token("<html></html>") == ""


def test_parse_tickets_missing():
    html = """
    <div class="ticket-item">
        <div>No link here</div>
    </div>
    """
    from hermes.support.parsers import parse_tickets

    tickets = parse_tickets(html)
    assert len(tickets) == 0


def test_parse_csrf_token_list():
    from bs4 import BeautifulSoup

    html = '<input name="csrf_token" value="abc" />'
    soup = BeautifulSoup(html, "html.parser")
    tag = soup.find("input")

    with (
        patch.object(tag, "get", return_value=["token1", "token2"]),
        patch("bs4.BeautifulSoup.find", return_value=tag),
    ):
        assert parse_csrf_token(html) == "token1"

    with (
        patch.object(tag, "get", return_value=[]),
        patch("bs4.BeautifulSoup.find", return_value=tag),
    ):
        assert parse_csrf_token(html) == ""

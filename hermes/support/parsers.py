from bs4 import BeautifulSoup, Tag

from .models import Ticket, TicketMessage


def parse_tickets(html: str) -> list[Ticket]:
    soup = BeautifulSoup(html, "html.parser")
    tickets = []
    for row in soup.find_all("div", class_="ticket-item"):
        a_tag = row.find("a")
        if not a_tag:
            continue
        url = str(a_tag.get("href") or "")
        t_id = url.strip("/").split("/")[-1] if url else ""

        subj_div = row.find("div", class_="ticket-subject")
        subject = subj_div.text.strip() if subj_div else "No Subject"

        stat_div = row.find("div", class_="ticket-status")
        status = stat_div.text.strip() if stat_div else "Unknown"

        tickets.append(Ticket(id=t_id, subject=subject, status=status, url=url))
    return tickets


def parse_ticket_messages(html: str) -> list[TicketMessage]:
    soup = BeautifulSoup(html, "html.parser")
    messages = []
    for msg in soup.find_all("div", class_="message-item"):
        m_id = str(msg.get("data-id") or "")

        auth_div = msg.find("div", class_="message-author")
        author = auth_div.text.strip() if auth_div else "Unknown"

        text_div = msg.find("div", class_="message-text")
        text = text_div.text.strip() if text_div else ""

        time_div = msg.find("div", class_="message-timestamp")
        timestamp = time_div.text.strip() if time_div else ""

        messages.append(
            TicketMessage(id=m_id, author=author, text=text, timestamp=timestamp)
        )
    return messages


def parse_csrf_token(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    csrf_input = soup.find("input", {"name": "csrf_token"})
    if isinstance(csrf_input, Tag):
        val = csrf_input.get("value", "")
        if isinstance(val, str):
            return val
        if isinstance(val, list) and val:
            return str(val[0])
    return ""

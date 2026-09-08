from dataclasses import dataclass


@dataclass
class Ticket:
    id: str
    subject: str
    status: str
    url: str


@dataclass
class TicketMessage:
    id: str
    author: str
    text: str
    timestamp: str

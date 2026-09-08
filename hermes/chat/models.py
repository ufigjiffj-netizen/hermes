from dataclasses import dataclass


@dataclass
class Dialog:
    node_id: str
    name: str
    last_message: str


@dataclass
class Message:
    id: str
    node_id: str
    author: str
    text: str
    timestamp: str

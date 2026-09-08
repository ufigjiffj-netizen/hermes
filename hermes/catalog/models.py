from dataclasses import dataclass


@dataclass
class Category:
    id: str
    name: str
    url: str


@dataclass
class Listing:
    id: str
    title: str
    description: str
    price: float
    seller_name: str
    url: str


@dataclass
class CommissionInfo:
    rate: float


@dataclass
class ListingDetails:
    detailed_description: str
    short_description: str


@dataclass
class ListingDetails:
    detailed_description: str
    short_description: str

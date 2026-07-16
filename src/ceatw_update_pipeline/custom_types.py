from typing import TypedDict, NotRequired
from enum import StrEnum

class ExaPayload(TypedDict):
    query: str
    includeDomains: NotRequired[list[str]]

class SearchStrategy(StrEnum):
    NATIVE = "native_prompt"
    ENGLISH = "english_prompt"
    
class Source(TypedDict):
    country: str
    search_strategy: str
    url: str
    title: str | None
    published_date: str | None
    highlights: list[str] | None
"""Custom data types for the pipeline data. Note this does NOT include database types."""
from __future__ import annotations

from enum import StrEnum
from typing import Annotated

import pycountry
from pydantic import AfterValidator, BaseModel, computed_field


class ExaPayload(BaseModel):
    query: str
    include_domains: list[str]

class SearchStrategy(StrEnum):
    NATIVE = "native_prompt"
    ENGLISH = "english_prompt"
    
def check_valid_country_code(country_code: str) -> str:
    """Checks if a two letter country code is in the ISO 3166-1 standard (as of 2026-07-23).

    Args:
        country_code (str): A two letter country code.

    Raises:
        ValueError: The country code is not in the ISO 3166-1 standard.

    Returns:
        str: The country_code argument.
    """
    if pycountry.countries.get(alpha_2=country_code) is None:
        raise ValueError(f"Not a valid 2 letter country code: {country_code}")
    return country_code

def to_upper(x: str) -> str:
    return x.upper()
    
# Note this is just a type hint, and the AfterValidators only run once 
# the Country class is instantiated.
CountryCode = Annotated[str, AfterValidator(to_upper),
                             AfterValidator(check_valid_country_code)]

class Country(BaseModel):
    country_code: CountryCode
    
    @computed_field # type: ignore[prop-decorator]
    @property
    def name(self) -> str:
        country_object = pycountry.countries.get(alpha_2=self.country_code)
        if (country_object is None):
            raise ValueError(f"The country code isn't associated with a name. "
                             f"Country code: {self.country_code}")
        return country_object.name.lower()

class SourceData(BaseModel):
    country: Country
    search_strategy: SearchStrategy
    url: str
    title: str | None = None
    published_date: str | None = None
    highlights: list[str] | None = None
    
class Status(StrEnum):
    UNVETTED = "UNVETTED"
    REJECTED = "REJECTED"
    ACCEPTED = "ACCEPTED"
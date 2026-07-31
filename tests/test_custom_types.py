import ceatw_update_pipeline.custom_types as CT
from pydantic import ValidationError
import pytest

@pytest.mark.parametrize(("country_code,comments"), [
    ("CAN", "too long"),
    ("ZX", "fake code"),
])
def test_country_bad(country_code: str, comments: str):
    with pytest.raises(ValidationError):
        CT.Country(country_code=country_code)
        

@pytest.mark.parametrize(("country_code,comments"), [
    ("CN", "canada"),
    ("ZW", "zimbabwe"),
    ("gb", "UK but uncapitalised"),
    ("eS", "spain")
])
def test_country_good(country_code: str, comments: str):
    country = CT.Country(country_code=country_code)
    assert isinstance(country.name, str), "Country name is not a string"
    assert country.country_code.isupper(), "Country code not uppercase"
    
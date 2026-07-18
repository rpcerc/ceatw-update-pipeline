import validators
import asyncio
from ceatw_update_pipeline.gather_sources import get_exa_sources
from ceatw_update_pipeline.configuration import settings
from ceatw_update_pipeline.custom_types import SearchStrategy

COUNTRIES = [
    "Japan",
    "Germany",
    "Zimbabwe",
]

def test_get_prompt_return_structure():
    for country in COUNTRIES[:1]:  # Test only the first country
        print(f"Testing {country} ---")
        result = [x.model_dump() for x in asyncio.run(get_exa_sources(country))]
        
        assert isinstance(result, list), f"List expected, got {type(result)}."
        assert 0 < len(result) <= 2 * settings.MAX_URL_COUNT, f"Expected 1-{2 * settings.MAX_URL_COUNT} URLs, got {len(result)}."
        
        # Validate the TypedDict shape and URL formatting manually
        for item in result:
            assert isinstance(item, dict), f"Expected dict, got {type(item)}"
            
            # Core data checks
            assert "url" in item and isinstance(item["url"], str), "Missing or invalid 'url'"
            assert "title" in item and isinstance(item["title"], str), "Missing or invalid 'title'"
            
            # Nullable keys checks
            assert "published_date" in item, "Missing 'published_date' key"
            assert isinstance(item["published_date"], (str, type(None))), "Invalid 'published_date' type"
            
            assert "highlights" in item, "Missing 'highlights' key"
            assert isinstance(item["highlights"], (list, type(None))), "Invalid 'highlights' type"
            
            # Metadata checks (New additions)
            assert "country" in item and isinstance(item["country"], str), "Missing or invalid 'country'"
            assert item["country"] == country, f"Expected country '{country}', got '{item['country']}'"
            
            assert "search_strategy" in item, "Missing 'search_strategy' key"
            assert item["search_strategy"] in SearchStrategy, f"Invalid search_strategy: {item.get('search_strategy')}"
            
            # URL Validation
            assert validators.url(item["url"]), f"Malformed URL: {item['url']}"

def check_result():
    print(asyncio.run(get_exa_sources("france")).model_dump())

if __name__ == "__main__":
    assert "native_prompt" in SearchStrategy
    check_result()
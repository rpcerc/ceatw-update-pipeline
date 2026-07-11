import validators
from dotenv import load_dotenv
from ceatw_update_pipeline.gather_sources import get_exa_sources
from ceatw_update_pipeline.configuration import MAX_URL_COUNT

COUNTRIES = [
    "Japan",
    "Germany",
    "Zimbabwe",
]

def test_get_prompt_return_structure():
    load_dotenv()
    for country in COUNTRIES[:1]:  # Test only the first country
        print(f"Testing {country} ---")
        result = get_exa_sources(country)
        
        assert isinstance(result, list), f"List expected, got {type(result)}."
        assert 0 < len(result) <= MAX_URL_COUNT, f"Expected 1-{MAX_URL_COUNT} URLs, got {len(result)}."
        
        # Validate the TypedDict shape and URL formatting manually
        for item in result:
            assert isinstance(item, dict), f"Expected dict, got {type(item)}"
            
            assert "url" in item and isinstance(item["url"], str), "Missing or invalid 'url'"
            assert "title" in item and isinstance(item["title"], str), "Missing or invalid 'title'"
            
            # Check nullable keys (published_date, highlights)
            assert "published_date" in item, "Missing 'published_date' key"
            assert isinstance(item["published_date"], (str, type(None))), "Invalid 'published_date' type"
            
            assert "highlights" in item, "Missing 'highlights' key"
            assert isinstance(item["highlights"], (list, type(None))), "Invalid 'highlights' type"
            
            assert validators.url(item["url"]), f"Malformed URL: {item['url']}"

def check_result():
    load_dotenv()
    print(get_exa_sources("france"))

if __name__ == "__main__":
    check_result()
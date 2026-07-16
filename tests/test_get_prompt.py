from ceatw_update_pipeline.get_prompt import generate_exa_payload
from dotenv import load_dotenv

COUNTRIES = [
    "Japan",
    "Germany",
    "Zimbabwe",
]

def test_get_prompt():
    load_dotenv()
    for country in COUNTRIES[:1]:  # Test only the first country
        result = generate_exa_payload(f"Find official primary school, kindergarten, and high school computing or computer science curricula for {country}. Restrict to official government/education domains if possible.")
        assert isinstance(result, dict), "Not valid JSON."
        assert "query" in result, "Missing 'query' key in the JSON payload."
        
        
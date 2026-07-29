from ceatw_update_pipeline.get_prompt import generate_exa_payload
import asyncio

COUNTRIES = [
    "Japan",
    "Germany",
    "Zimbabwe",
]

def test_get_prompt():
    for country in COUNTRIES[:1]:  # Test only the first country
        result = asyncio.run(generate_exa_payload(f"Find official primary school, kindergarten, and high school computing or computer science curricula for {country}. Restrict to official government/education domains if possible.")).model_dump()
        assert isinstance(result, dict), "Not valid JSON."
        assert "query" in result, "Missing 'query' key in the JSON payload."
        
        
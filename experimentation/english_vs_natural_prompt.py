import json
from exa_py import Exa
from dotenv import load_dotenv

# Import your existing functions
from ceatw_update_pipeline.filter import is_valid_url
from ceatw_update_pipeline.gather_sources import create_source
from ceatw_update_pipeline.configuration import MAX_URL_COUNT, SEARCH_TYPE

# Import the Gemini generator function
from ceatw_update_pipeline.get_prompt import generate_exa_payload

def compare_raw_vs_gemini():
    load_dotenv()
    
    try:
        exa = Exa()
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Exa client: {e}")

    # ==========================================
    # Define Your Raw English Test Prompts
    # ==========================================
    # The static English template
    base_template = "Official national curriculum, syllabus, or learning standards for Computer Science, ICT, and Computing in {country} schools"
    # The 4 countries to test
    test_countries = [
        "India",
        "Mexico",
        "Estonia",
        "United Arab Erimates"
    ]

    # Generate the dictionary using the template
    raw_prompts = {country: base_template.format(country=country) for country in test_countries}
    
    # We will use "deep" since it performed best for finding specific curriculum documents

    for country, raw_intent in raw_prompts.items():
        payload = generate_exa_payload(raw_intent)
        print(f"\n{'='*80}")
        print(f"TESTING {country.upper()}")
        print(f"RAW INTENT: {raw_intent}")
        print(f"{'='*80}")
        
        # ---------------------------------------------------------
        # TEST 1: Raw English Prompt directly into Exa
        # ---------------------------------------------------------
        print("\n--- TEST 1: RAW ENGLISH PROMPT ---")
        try:
            response_raw = exa.search(
                query=raw_intent,
                type=SEARCH_TYPE,
                num_results=MAX_URL_COUNT,
                include_domains=payload.get("includeDomains", None),
                contents={"highlights": True}
            )
            
            valid_sources_raw = []
            for result in response_raw.results:
                valid_sources_raw.append(create_source(result))
            
            print(f"Found {len(valid_sources_raw)} valid URLs using raw English.\n")
            for i, source in enumerate(valid_sources_raw, 1):
                print(f"Result {i} Title: {source['title']}")
                print(f"Result {i} URL:   {source['url']}\n")
                
        except Exception as e:
            print(f"Error running raw English prompt: {e}")

        # ---------------------------------------------------------
        # TEST 2: Gemini-Generated Payload
        # ---------------------------------------------------------
        print("--- TEST 2: GEMINI GENERATED PAYLOAD ---")
        try:
            print("Generating payload via Gemini...")
            # Get payload from your function
            generated_query = payload.get("query")
            include_domains = payload.get("includeDomains", [])
            
            print(f"Gemini Query:   '{generated_query}'")
            print(f"Gemini Domains: {include_domains}\n")
            
            # Setup kwargs for Exa SDK
            search_kwargs = {
                "query": generated_query,
                "type": SEARCH_TYPE,
                "num_results": MAX_URL_COUNT,
                "contents": {"highlights": True}
            }
            if include_domains:
                search_kwargs["include_domains"] = include_domains

            # Run Exa search with Gemini output
            response_gemini = exa.search(**search_kwargs)
            
            valid_sources_gemini = []
            for result in response_gemini.results:
                valid_sources_gemini.append(create_source(result))
            
            print(f"Found {len(valid_sources_gemini)} valid URLs using Gemini payload.\n")
            for i, source in enumerate(valid_sources_gemini, 1):
                print(f"Result {i} Title: {source['title']}")
                print(f"Result {i} URL:   {source['url']}\n")
                
        except Exception as e:
            print(f"Error running Gemini payload: {e}")

if __name__ == "__main__":
    compare_raw_vs_gemini()
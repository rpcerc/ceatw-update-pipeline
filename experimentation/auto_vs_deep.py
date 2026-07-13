import json
from exa_py import Exa
from dotenv import load_dotenv

# Import your existing functions
from ceatw_update_pipeline.filter import is_valid_url
from ceatw_update_pipeline.gather_sources import create_source
from ceatw_update_pipeline.configuration import MAX_URL_COUNT

def compare_search_types():
    load_dotenv()
    
    try:
        exa = Exa()
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Exa client: {e}")

    # ==========================================
    # Define Your Test Prompts Here
    # ==========================================
    # Germany is highly decentralized. Finding curriculum documents requires bypassing 
    # generic news and finding state-level (Länder) or KMK (Kultusministerkonferenz) frameworks.
    
    prompts = {
        "English": "Official computer science and computing curriculum standards for high schools in Germany site:de",
        "Target Language (German)": "Offizielle Lehrpläne und Bildungsstandards für Informatik an Gymnasien in Deutschland site:de"
    }
    
    # The different Exa search modes we want to compare
    search_types = ["auto", "deep", "deep-reasoning"]

    # ==========================================
    # Run the Test
    # ==========================================
    for language, query in prompts.items():
        for search_type in search_types:
            print(f"\n{'='*80}")
            print(f"TESTING {language.upper()} PROMPT | TYPE: '{search_type}'")
            print(f"Query: {query}")
            print(f"{'='*80}")
            
            try:
                # We pass the search_type variable into the Exa call
                response = exa.search(
                    query=query,
                    type=search_type,
                    num_results=MAX_URL_COUNT,
                    contents={"highlights": True}
                )
                
                valid_sources = []
                for result in response.results:
                    if is_valid_url(result.url):
                        valid_sources.append(create_source(result))
                
                # Print the results cleanly
                print(f"Found {len(valid_sources)} valid URLs.\n")
                
                for i, source in enumerate(valid_sources, 1):
                    print(f"--- Result {i} ---")
                    print(f"Title: {source['title']}")
                    print(f"URL:   {source['url']}")
                    
                    # Print just the first highlight snippet to keep terminal output readable
                    if source.get('highlights'):
                        # Clean up newlines for cleaner terminal output
                        snippet = source['highlights'][0].replace('\n', ' ')
                        print(f"Snippet: {snippet[:150]}...\n")
                    else:
                        print("Snippet: None\n")
                        
            except Exception as e:
                print(f"Error running {language} prompt with type '{search_type}': {e}")

if __name__ == "__main__":
    compare_search_types()
import json
import time
import os
from dotenv import load_dotenv
from ceatw_update_pipeline.keyword_filter import generate_filter_keywords
from ceatw_update_pipeline.configuration import KEYWORDS_FILE, COUNTRIES
# Configuration
DELAY_SECONDS = 4.5  # 60 seconds / 15 requests = 4s. Using 4.5s for a safe buffer.

# Import your COUNTRIES list here, or define it directly

def build_keyword_cache():
    """Generates and locally caches keywords for all countries slowly."""
    
    # 1. Load existing progress to allow for safe pausing/resuming
    if os.path.exists(KEYWORDS_FILE):
        with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
            try:
                keyword_cache = json.load(f)
            except json.JSONDecodeError:
                print("Warning: existing JSON is corrupted. Starting fresh.")
                keyword_cache = {}
    else:
        keyword_cache = {}

    print(f"Loaded {len(keyword_cache)} existing countries from cache.")

    # 2. Iterate through your target countries
    for country in COUNTRIES:
        if country in keyword_cache:
            print(f"Skipping {country} - already in cache.")
            continue
        
        print(f"Generating keywords for {country}...")
        try:
            keywords = generate_filter_keywords(country)
            keyword_cache[country] = keywords
            
            # 3. Save immediately to disk so progress is never lost
            with open(KEYWORDS_FILE, "w", encoding="utf-8") as f:
                json.dump(keyword_cache, f, indent=4, ensure_ascii=False)
                
            print(f"Success! Saved {country}. Sleeping for {DELAY_SECONDS} seconds...")
            time.sleep(DELAY_SECONDS)
            
        except Exception as e:
            print(f"Error generating for {country}: {e}")
            print("Sleeping for 10 seconds before trying the next country...")
            time.sleep(10)
            
    print("\nAll countries have been processed and cached!")

if __name__ == "__main__":
    load_dotenv()
    build_keyword_cache()
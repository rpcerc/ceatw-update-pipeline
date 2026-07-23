"""Custom tests that shouldn't be caught with pytest."""

import json

if __name__ == "__main__":
    with open("gemini_prompts.json", "r") as f:
        prompts = json.load(f)
        
    
    print(prompts["AZ"])
import json
from google import genai
# Assuming you want to add this system instruction to your configuration file
from ceatw_update_pipeline.configuration import SYSTEM_INSTRUCTION_KEYWORDS 

def generate_filter_keywords(country: str, custom_system_instruction: str = SYSTEM_INSTRUCTION_KEYWORDS) -> dict[str, list[str]]:
    """Uses Gemini to generate localized keyword filters for a target country.

    Args:
        country (str): The target country (e.g., "Mexico", "Estonia", "India").
        custom_system_instruction (str): Instructions telling Gemini how to build the keyword sets.

    Raises:
        RuntimeError: Gemini API error, unexpected error during interaction with Gemini,
                     or unexpected error during JSON parsing.
        ValueError: No response received from the model, or the response is not valid JSON.

    Returns:
        dict[str, list[str]]: A dictionary containing 'tech_keywords' and 'edu_keywords'.
    """
    
    # Context-building prompt for the model
    user_intent = f"Generate localized computing and curriculum filter keywords for the country: {country}"
    
    try:
        client = genai.Client()

        interaction: genai.interactions.Interaction = client.interactions.create(
            system_instruction=custom_system_instruction,
            model="gemini-3.1-flash-lite",
            input=user_intent,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": {
                    "type": "object",
                    "properties": {
                        "tech_keywords": {
                            "type": "array",
                            "description": "Keywords representing computing, ICT, tech, computer science, and digital competencies in English and the local language.",
                            "items": {
                                "type": "string"
                            }
                        },
                        "edu_keywords": {
                            "type": "array",
                            "description": "Keywords representing curriculum, syllabus, course of study, and academic standards in English and the local language.",
                            "items": {
                                "type": "string"
                            }
                        }
                    },
                    "required": [
                        "tech_keywords",
                        "edu_keywords"
                    ]
                },
            },
        )
    except genai.errors.APIError as e:
        raise RuntimeError(f"Gemini API error: {e}") from e
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred while interacting with Gemini: {e}") from e   
    
    # Parse the response and ensure it is valid JSON
    try:
        response = interaction.output_text
        if response is None:
            raise ValueError("generate_filter_keywords - No response received from the model.")
        
        keywords_payload = json.loads(response)
        
        # Normalize everything to lowercase immediately to guarantee safe lookups later
        return {
            "tech_keywords": [k.lower() for k in keywords_payload.get("tech_keywords", [])],
            "edu_keywords": [k.lower() for k in keywords_payload.get("edu_keywords", [])]
        }
    
    except json.JSONDecodeError as e:
        raise ValueError(f"generate_filter_keywords - Response is not valid JSON: {response}") from e
    except Exception as e:
        raise RuntimeError(f"generate_filter_keywords - An unexpected error occurred: {e}") from e
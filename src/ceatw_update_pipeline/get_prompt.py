"""Generate a prompt for use with the Exa API."""

import json
from google import genai
from ceatw_update_pipeline.configuration import SYSTEM_INSTRUCTION_EXA
from ceatw_update_pipeline.custom_types import ExaPayload

def generate_exa_payload(user_intent: str) -> ExaPayload:
    """Uses Gemini to generate a JSON payload for Exa AI.

    Args:
        user_intent (str): The user's intent/query for Gemini.

    Raises:
        RuntimeError: Gemini API error, unexpected error during interaction with Gemini,
                      or unexpected error during JSON parsing.
        ValueError: No response received from the model, or the response is not valid JSON.

    Returns:
        dict[str, str | list[str]]: JSON (a dictionary) representing the Exa API payload,
                        with schema ResponseSchema. 
    """
    
    # Note, this expects the environment variable GEMINI_API_KEY to be set.
    try:
        client = genai.Client()

        interaction: genai.interactions.Interaction = client.interactions.create(
            system_instruction=SYSTEM_INSTRUCTION_EXA,
            model="gemini-3.1-flash-lite",
            input=user_intent,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                # https://json-schema.org/docs
                "schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string"
                        },
                        "includeDomains": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        }
                    },
                    "required": [
                        "query"
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
            raise ValueError("get_prompt - No response received from the model.")
        
        payload: ExaPayload = json.loads(response)
        return payload
    
    except json.JSONDecodeError as e:
        raise ValueError(f"get_prompt - Response is not valid JSON: {response}") from e
    except Exception as e:
        raise RuntimeError(f"get_prompt - An unexpected error occurred: {e}") from e

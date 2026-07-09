"""Generate a prompt for use with the Exa API."""

import json
from google import genai
from ceatw_update_pipeline.configuration import SYSTEM_INSTRUCTION_EXA

def generate_exa_payload(user_intent: str) -> dict[str, str]:
    """Uses Gemini to generate a JSON payload for Exa AI.

    Args:
        user_intent (str): The user's intent/query.

    Returns:
        dict[str, str]: JSON (a dictionary) representing the Exa API payload. 
            Has key "query".
    """
    
    client: genai.Client = genai.Client()
    
    interaction: genai.interactions.Interaction = client.interactions.create(
        system_instruction=SYSTEM_INSTRUCTION_EXA,
        model="gemini-3.1-flash-lite",
        input=user_intent,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": {
                "type": "object",
                "properties": {
                    "urls": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            }
        }
    )
    
    try:
        response: str | None = interaction.output_text
        if response is None:
            raise ValueError("No response received from the model.")
        
        payload: dict[str, str] = json.loads(response)
        return payload
    except json.JSONDecodeError:
        raise ValueError(f"Response is not valid JSON: {response}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {e}")


    
"""Generate a prompt for use with the Exa API."""

import json
from google import genai
from ceatw_update_pipeline.configuration import SYSTEM_INSTRUCTION_EXA, settings
from ceatw_update_pipeline.custom_types import ExaPayload
from pydantic import ValidationError

async def generate_exa_payload(country: str, custom_system_instruction: str = SYSTEM_INSTRUCTION_EXA) -> ExaPayload:
    """Uses Gemini to generate a JSON payload for Exa AI for a country, containing a native language prompt.

    Args:
        country (str): The country name for which to generate the payload for.
        custom_system_instruction (str, optional): A system instruction for the payload.
            Defaults to SYSTEM_INSTRUCTION_EXA.

    Raises:
        RuntimeError: Gemini API error, unexpected error during interaction with Gemini,
                      or unexpected error during JSON parsing.
        ValueError: No response received from the model, or the response is not valid JSON.

    Returns:
        ExaPayload: JSON (a dictionary) representing the Exa API payload,
                        with schema ExaPayload. 
    """
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        user_intent = ("Find official primary school, kindergarten, and high school "
                      f"computing or computer science curricula for {country}. ")
        
        interaction = await client.aio.interactions.create(
            system_instruction=custom_system_instruction,
            model="gemini-3.1-flash-lite",
            input=user_intent,
            generation_config={
                "thinking_level": "high"
            },
            response_format={
                "type": "text",
                "mime_type": "application/json",
                # https://json-schema.org/docs
                "schema": ExaPayload.model_json_schema()
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
        
        return ExaPayload.model_validate_json(response)
    
    except (json.JSONDecodeError, ValidationError) as e:
        raise ValueError(f"get_prompt - Response is not valid JSON: {response}") from e
    except Exception as e:
        raise RuntimeError(f"get_prompt - An unexpected error occurred: {e}") from e

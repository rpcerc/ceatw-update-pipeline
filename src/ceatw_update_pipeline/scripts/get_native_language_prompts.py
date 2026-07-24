from ceatw_update_pipeline.main import load_native_prompts_cache
from ceatw_update_pipeline.custom_types import CountryCode, ExaPayload
from ceatw_update_pipeline.configuration import settings
from ceatw_update_pipeline.get_prompt import generate_exa_payload
import pycountry
import logging
import asyncio
import json

logging.basicConfig(filename="devlogs.log", level=logging.INFO)

logger = logging.getLogger(__name__)

async def get_gemini_prompts() -> dict[CountryCode, ExaPayload]:
    """Precompute the native language prompts, and store them in a file.

    Returns:
        dict[CountryCode, ExaPayload]: A dictionary mapping country codes to native-language exa payloads.
    """
    prompts = load_native_prompts_cache()
    
    for country in pycountry.countries:
        if country.alpha_2 in prompts:
            logger.info("Native prompt already cached for country: %s", country.name)
            continue
        
        prompts[country.alpha_2] = await generate_exa_payload(country.name)
        with open(settings.NATIVE_LANGUAGE_PROMPTS_FILE, "w") as f:
            # This is to ensure type safety across mypy.
            # It is a lot of overhead, but it is negligible compared to generate_exa_payload.
            # Also, while I could write everything at once, this function has the possibility of breaking mid-execution.
            data_to_write = {}
            for code, payload in prompts.items():
                data_to_write[code] = payload.model_dump(mode='json')
            json.dump(data_to_write, f, indent=4, ensure_ascii=False)
            
        logger.info("Saved: %s", country.name)
        
    return prompts

if __name__ == "__main__":
    asyncio.run(get_gemini_prompts())
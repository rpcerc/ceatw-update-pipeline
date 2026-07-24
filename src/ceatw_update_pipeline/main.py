"""The main entry point for the pipeline."""

from ceatw_update_pipeline.database.database import init_db, kill_engine, get_session
from ceatw_update_pipeline.database import query
from ceatw_update_pipeline.database.schemas import SourceCreate
from ceatw_update_pipeline.gather_sources import get_exa_sources
from ceatw_update_pipeline.get_prompt import generate_exa_payload
from ceatw_update_pipeline.custom_types import Country, ExaPayload, CountryCode
from ceatw_update_pipeline.configuration import settings
from pydantic import ValidationError
import pycountry
import json
import logging
from sqlalchemy.exc import IntegrityError
import asyncio

logging.basicConfig(filename="devlogs.log", level=logging.INFO)

logger = logging.getLogger(__name__)
    
async def insert_urls_for_one_country(country_code: CountryCode, native_prompt_cache: dict[str, ExaPayload]) -> None:
    """Gather the source urls for a country, then store them in a database.

    Args:
        country_code (CountryCode): A two letter country code.
        native_prompt_cache (dict[str, ExaPayload]): 
    """
    country = Country(country_code=country_code)
    results = await get_exa_sources(country.country_code, native_prompt_cache)
    with get_session() as session:
        for result in results:
            try:
                with session.begin_nested():
                    query.insert_source(session, 
                        SourceCreate(
                            source_url=result.url,
                            country=country.name,
                            country_code=country.country_code,
                            content_hash="fake_hash"
                        ))
            except IntegrityError:
                logger.info("Record skipped, duplicate URL: %s", result.url[:50])
        
    logger.info("All URLs inserted for %s", country.name)
    
async def insert_countries(country_codes: list[CountryCode], native_prompt_cache: dict[CountryCode, ExaPayload]) -> None:
    """Insert the sources for the given country codes into the database.

    Args:
        country_codes (list[CountryCode]): A list of country codes.
        native_prompt_cache (dict[CountryCode, ExaPayload]): The native prompts cache.
    """
    
    n = len(country_codes)
    for i in range(0, n, settings.BATCH_SIZE):
        # Rate limit of 10 calls per second as of 2026/07/24, hence do it in batches of BATCH_SIZE (5).
        tasks = [insert_urls_for_one_country(code, native_prompt_cache) 
                 for code in country_codes[i:i+settings.BATCH_SIZE]]
        await asyncio.gather(*tasks)
        await asyncio.sleep(1)
    
    logger.info("%d countries inserted successfully", n) 

    
    
def load_native_prompts_cache() -> dict[CountryCode, ExaPayload]:
    """Read the prompts cache from the file path given in the configuration file.

    Returns:
        dict[CountryCode, ExaPayload]: The native prompts cache.
    """
    prompts_cache: dict[CountryCode, ExaPayload] = {}
    try:
        with open(settings.NATIVE_LANGUAGE_PROMPTS_FILE, "r") as f:
            raw_json = json.load(f)
            for country_code, payload_dict in raw_json.items():
                prompts_cache[country_code] = ExaPayload.model_validate(payload_dict)
                
    except (json.JSONDecodeError, FileNotFoundError, ValidationError):
        logger.exception("Cache failed to load:")
    
    return prompts_cache
    
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

async def run_pipeline() -> None:
    # Get rid of antarctica
    init_db()
    valid_country_codes = [c.alpha_2 for c in pycountry.countries if c.alpha_2 != "AQ"]
    native_prompts_cache = load_native_prompts_cache()
    await insert_countries(valid_country_codes, native_prompts_cache)
    kill_engine()
    
    
if __name__ == "__main__":
    asyncio.run(run_pipeline())
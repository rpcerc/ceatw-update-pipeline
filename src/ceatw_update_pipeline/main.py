"""The main entry point for the pipeline."""

from ceatw_update_pipeline.database.database import init_db, kill_engine, get_session
from ceatw_update_pipeline.database import query
from ceatw_update_pipeline.database.schemas import SourceCreate
from ceatw_update_pipeline.gather_sources import get_exa_sources
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
    
async def insert_urls_for_one_country(country_code: CountryCode, native_prompts_cache: dict[str, ExaPayload]) -> None:
    """Gather the source urls for a country, then store them in a database.

    Args:
        country_code (CountryCode): A two letter country code.
        native_prompts_cache (dict[str, ExaPayload]): 
    """
    country = Country(country_code=country_code)
    results = await get_exa_sources(country.country_code, native_prompts_cache)
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
    
async def insert_countries(country_codes: list[CountryCode], native_prompts_cache: dict[CountryCode, ExaPayload]) -> None:
    """Insert the sources for the given country codes into the database.

    Args:
        country_codes (list[CountryCode]): A list of country codes.
        native_prompts_cache (dict[CountryCode, ExaPayload]): The native prompts cache.
    """

    batch_size = int((settings.EXA_API_LIMIT-1)/2)
    logger.info("Inserting %d countries in batches of %d...", len(country_codes), batch_size)
    
    for i in range(0, len(country_codes), batch_size):
        current_batch = country_codes[i:i+batch_size]
        tasks = [insert_urls_for_one_country(cc, native_prompts_cache)
                 for cc in current_batch]
        
        # This is quite prone to breaking, due to API rate limits seemingly being lower than written.
        await asyncio.gather(*tasks)
        logger.info("Batch finished, sleeping for 1s")
        
        await asyncio.sleep(1)
        
    logger.info("%d countries inserted successfully", len(country_codes)) 

    
    
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

async def run_pipeline() -> None:
    # Get rid of antarctica
    init_db()
    valid_country_codes = [c.alpha_2 for c in pycountry.countries if c.alpha_2 != "AQ"]
    native_prompts_cache = load_native_prompts_cache()
    await insert_countries(valid_country_codes, native_prompts_cache)
    kill_engine()
    
    
if __name__ == "__main__":
    asyncio.run(run_pipeline())
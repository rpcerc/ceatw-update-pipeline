"""Uses Exa.ai API to generate possible source URLs for computing curricula."""

import asyncio
from ceatw_update_pipeline.configuration import settings
from ceatw_update_pipeline.get_prompt import generate_exa_payload
from ceatw_update_pipeline.custom_types import (
        SourceData, ExaPayload, SearchStrategy, Country)
from exa_py import AsyncExa
from exa_py.api import Result
import logging

logger = logging.Logger(__name__)

def create_source(exa_result: Result, country: Country, search_strategy: SearchStrategy) -> SourceData:
    """Takes a singular exa_result, and returns a Source object.

    Args:
        exa_result (Result): One result from an exa.ai call.
        country (str): The country associated with the source.
        search_strategy (SearchStrategy): The type of exa_api call executed to give the result.

    Returns:
        Source: The result in a Source object form.
    """
    
    return SourceData(
        country=country,
        search_strategy=search_strategy, 
        url=exa_result.url,
        title=exa_result.title,
        published_date=getattr(exa_result, "published_date", None),
        highlights=getattr(exa_result, "highlights", None)
    )

async def get_exa_sources(country_code_alpha_2: str, native_prompt_cache: dict[str, ExaPayload]) -> list[SourceData]:
    """Returns a list of Sources returned by Exa.ai for a given country.

    Args:
        country (str): A country to find sources for.

    Raises:
        RuntimeError: Exa API failure, or Gemini API failure.
        ValueError: JSON error when generating native prompt, or Gemini didn't respond.

    Returns:
        list[Source]: A list of potential computing curricula sources.
    """
    
    try:
        exa = AsyncExa(api_key=settings.EXA_API_KEY)
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Exa client: {e}")
        
    country = Country(country_code=country_code_alpha_2)
    
    try:
        payload = native_prompt_cache[country_code_alpha_2]
    except KeyError:
        logger.warning("Not in country code cache: %s", country_code_alpha_2)
        payload = await generate_exa_payload(country.name)
        
    english_query = (
        f"Official national curriculum, syllabus, or learning standards "
        f"for Computer Science, ICT, and Computing in {country.name} schools"
    )
    
    try:
        # Note both queires use the TLD domain restrictions found by the Gemini call.
        gemini_response, english_response = await asyncio.gather(
            exa.search(
                query=payload.query,
                type=settings.EXA_SEARCH_TYPE,
                num_results=settings.MAX_URL_COUNT,
                include_domains=payload.includeDomains,
                contents={"highlights": True},
            ),
            exa.search(
                query=english_query,
                type=settings.EXA_SEARCH_TYPE,
                num_results=settings.MAX_URL_COUNT,
                include_domains=payload.includeDomains,
                contents={"highlights": True},
            )
        )
        
        gemini_sources = [
            create_source(result, country, SearchStrategy.NATIVE) 
            for result in gemini_response.results
        ]
    
        english_sources = [
            create_source(result, country, SearchStrategy.ENGLISH) 
            for result in english_response.results
        ]
        
        return gemini_sources + english_sources
    
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve URLs from Exa: {e}")
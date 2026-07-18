"""Uses Exa.ai API to generate possible source URLs for computing curricula."""

from ceatw_update_pipeline.configuration import settings
from ceatw_update_pipeline.get_prompt import generate_exa_payload
from ceatw_update_pipeline.custom_types import Source, SearchStrategy
from exa_py import Exa
from exa_py.api import Result

def create_source(exa_result: Result, country: str, search_strategy: SearchStrategy) -> Source:
    """Takes a singular exa_result, and returns a Source object.

    Args:
        exa_result (Result): One result from an exa.ai call.
        country (str): The country associated with the source.
        search_strategy (SearchStrategy): The type of exa_api call executed to give the result.

    Returns:
        Source: The result in a Source object form.
    """
    
    highlights = getattr(exa_result, "highlights", None)
    
    return {
        "country": country,
        "search_strategy": search_strategy,
        "url": exa_result.url,
        "title": exa_result.title,
        "published_date": getattr(exa_result, "published_date", None),
        "highlights": highlights
    }

def get_exa_sources(country: str) -> list[Source]:
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
        exa = Exa()
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Exa client: {e}")
        
    intent = ("Find official primary school, kindergarten, and high school "
              f"computing or computer science curricula for {country}. ")
    
    payload = generate_exa_payload(intent)
    english_query = "Official national curriculum, syllabus, or learning standards for Computer Science, ICT, and Computing in {country} schools"
    try:
        gemini_response = exa.search(
            query=payload["query"],
            type=settings.EXA_SEARCH_TYPE,
            num_results=settings.MAX_URL_COUNT,
            include_domains=payload.get("includeDomains"),
            contents={
                "highlights": True,
            },
        )
        
        english_response = exa.search(
            query=english_query,
            type=settings.EXA_SEARCH_TYPE,
            num_results=settings.MAX_URL_COUNT,
            include_domains=payload.get("includeDomains"),
            contents={
                "highlights": True,
            },
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
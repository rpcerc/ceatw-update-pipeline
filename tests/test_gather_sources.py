import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from ceatw_update_pipeline.gather_sources import get_exa_sources, get_relevant_tlds, get_prompt_from_cache
from ceatw_update_pipeline.configuration import settings, GENERIC_TLD_DOMAINS
from ceatw_update_pipeline.custom_types import ExaPayload, Country

COUNTRIES = [
    "JP",
    "DE",
    "ZW",
]

def test_get_relevant_tlds():
    assert (set(get_relevant_tlds([".fake", ".fake", ".testtld"])) 
            == set(GENERIC_TLD_DOMAINS + [".fake", ".testtld"]))

@pytest.mark.asyncio
@patch('ceatw_update_pipeline.gather_sources.AsyncExa')
async def test_retry_logic(mock_exa):
    mock_exa.return_value.search = AsyncMock()
    mock_search = mock_exa.return_value.search
    
    # Reach max retry limit
    mock_search.side_effect = RuntimeError("API search error")
    with pytest.raises(RuntimeError):
        await get_exa_sources("GB", {"GB": ExaPayload(query="", include_domains=[".gov.uk"])})
    assert mock_search.call_count == settings.MAX_RETRIES, f"Should attempt to search {settings.MAX_RETRIES} times."

    # Succeed on last retry
    mock_result_item = MagicMock()
    mock_result_item.title = "Official UK Government Website"
    mock_result_item.url = "https://www.gov.uk/example"
    
    mock_success_response = MagicMock()
    mock_success_response.return_value.results = [mock_result_item]
    
    mock_search.reset_mock()
    mock_search.side_effect = ([RuntimeError("API Rate limit") for i in range(settings.MAX_RETRIES-1)] 
                            + [mock_success_response, mock_success_response])
    
    await get_exa_sources("GB", {"GB": ExaPayload(query="", include_domains=[".gov.uk"])})
    
    # Four, because two calls are made to Exa.api for the english and natural prompt.
    assert mock_search.call_count == 4, "Should have failed twice and succeeded on the third attempt."

@pytest.mark.asyncio
@patch('ceatw_update_pipeline.gather_sources.generate_exa_payload', new_callable=AsyncMock)
async def test_cache(mock_generate):
    cached_result = ExaPayload(query="a", include_domains=[])
    non_cached_result = ExaPayload(query="b", include_domains=[])
    mock_generate.return_value = non_cached_result
    
    # In cache
    first_result = await get_prompt_from_cache(Country(country_code="GB"),
                                         {"GB": cached_result})
    
    assert first_result == cached_result, "Did not pull exa payload from cache"
    assert mock_generate.call_count == 0, "Called generate despite pulling from cache"
    
    # Not in cache
    second_result = await get_prompt_from_cache(Country(country_code="GB"),
                                         {"GD": cached_result})
    
    assert second_result == non_cached_result, "Should have generated the exa payload"
    mock_generate.assert_called_once()


@pytest.mark.asyncio
async def test_get_prompt_return_structure():
    # I'm not too sure about this test - it takes an API call to run
    for cc in COUNTRIES[:1]:
        print(f"Testing {cc} ---")
        
        result = await get_exa_sources(cc, {})
        
        # Check the logic for the return length
        assert isinstance(result, list), f"List expected, got {type(result)}."
        assert 0 < len(result) <= 2 * settings.MAX_URL_COUNT, (
            f"Expected 1-{2 * settings.MAX_URL_COUNT} URLs, got {len(result)}).")
        
        # Check the logic for correct data mapping
        for item in result:
            assert item.country.country_code == cc, (
                f"Wrong country code - expected: {cc}, got: {item.country.country_code}")
            assert item.search_strategy is not None
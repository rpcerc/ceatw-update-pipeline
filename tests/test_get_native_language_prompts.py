import pytest
import pycountry
from unittest.mock import mock_open, patch
from ceatw_update_pipeline.custom_types import ExaPayload
from ceatw_update_pipeline.scripts.get_native_language_prompts import get_gemini_prompts

@pytest.mark.anyio
@patch("builtins.open", new_callable=mock_open)
@patch("ceatw_update_pipeline.scripts.get_native_language_prompts.generate_exa_payload")
@patch("json.dump")
@patch("ceatw_update_pipeline.scripts.get_native_language_prompts.logger.info")
@patch("ceatw_update_pipeline.scripts.get_native_language_prompts.load_native_prompts_cache")
@patch("pycountry.countries", [
    pycountry.countries.get(alpha_2="GB"), 
    pycountry.countries.get(alpha_2="DE")
])
async def test_get_gemini_prompts(mock_cache, mock_logger, mock_write, mock_generate, mock_file):
    mock_cache.return_value = {"GB": ExaPayload(query="fake-query", include_domains=["gov.uk"])}
    mock_generate.return_value = ExaPayload(query="germany", include_domains=[".de"])
    
    result = await get_gemini_prompts()
    
    # Should skip writing for GB
    mock_logger.assert_any_call("Native prompt already cached for country: %s",
                                "United Kingdom")
    mock_write.assert_called_once()
    
    # New result added
    assert "DE" in result
    assert result["DE"].query is not None
    assert len(result["DE"].include_domains) == 1 and result["DE"].include_domains[0] == ".de"
    
    # Cached result still there
    assert "GB" in result
    assert result["GB"] == mock_cache.return_value["GB"]
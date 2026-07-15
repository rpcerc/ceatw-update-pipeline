import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from bs4 import BeautifulSoup
import requests

from ceatw_update_pipeline.education_profiles.get_education_profiles import (
    get_technology_page_urls,
    is_relevant_link,
    extract_content_links,
    get_content_links
)

# Note - I haven't tested some functions, like save_json_to_file.
# This is because they are e.g. taken straight from the official documentation of an API, etc.

# ==========================================
# Tests for is_relevant_link
# ==========================================
@pytest.mark.parametrize("href, expected", [
    ("https://example.com", True),
    ("/internal/path", True),
    ("#section", False),
    ("javascript:void(0)", False),
    ("mailto:test@example.com", False),
    ("tel:1234567890", False),
    ("", False),
    (None, False)
])
def test_is_relevant_link(href, expected):
    """Tests that the link validator correctly filters anchor jumps and scripts."""
    assert is_relevant_link(href) is expected


# ==========================================
# Tests for extract_content_links
# ==========================================
@patch("ceatw_update_pipeline.education_profiles.get_education_profiles.requests.get")
def test_extract_content_links_with_main_content(mock_get):
    """Tests extraction when the #block-mainpagecontent div exists."""
    dummy_html = """
    <html>
        <body>
            <div id="block-mainpagecontent">
                <a href="https://valid.com">Valid</a>
                <a href="#jump">Invalid Jump</a>
                <a href="https://valid.com">Duplicate</a>
            </div>
            <a href="https://ignored.com">Outside Content</a>
        </body>
    </html>
    """
    mock_response = MagicMock()
    mock_response.text = dummy_html
    mock_get.return_value = mock_response

    links = extract_content_links("https://fake-url.com")
    
    # Should only return the valid link, removing duplicates and ignoring outside content
    assert links == ["https://valid.com"]
    mock_get.assert_called_once_with("https://fake-url.com", timeout=5)

@patch("ceatw_update_pipeline.education_profiles.get_education_profiles.requests.get")
def test_extract_content_links_fallback_to_body(mock_get):
    """Tests fallback to body when main block is missing."""
    dummy_html = """
    <html>
        <body>
            <a href="https://fallback.com">Fallback</a>
        </body>
    </html>
    """
    mock_response = MagicMock()
    mock_response.text = dummy_html
    mock_get.return_value = mock_response

    links = extract_content_links("https://fake-url.com")
    
    assert links == ["https://fallback.com"]

@patch("ceatw_update_pipeline.education_profiles.get_education_profiles.requests.get")
def test_extract_content_links_request_exception(mock_get):
    """Tests safe failure when the network request fails."""
    mock_get.side_effect = requests.RequestException("Network Error")
    
    links = extract_content_links("https://fake-url.com")
    assert links == []


# ==========================================
# Tests for get_content_links
# ==========================================
@patch("ceatw_update_pipeline.education_profiles.get_education_profiles.save_json_to_file")
@patch("ceatw_update_pipeline.education_profiles.get_education_profiles.extract_content_links")
@patch("builtins.open", new_callable=mock_open, read_data='{"france": "https://test.com/france"}')
@patch("ceatw_update_pipeline.education_profiles.get_education_profiles.EDUCATION_PROFILES_OUTPUT_FOLDER", "mock_folder")
@patch("ceatw_update_pipeline.education_profiles.get_education_profiles.EDUCATION_PROFILES_TECH_URL_FILE", "mock_tech.json")
@patch("ceatw_update_pipeline.education_profiles.get_education_profiles.EDUCATION_PROFILES_CONTENT_URL_FILE", "mock_content.json")
def test_get_content_links_loads_existing_file(mock_file, mock_extract, mock_save):
    """Tests the happy path where the URLs JSON file already exists."""
    mock_extract.return_value = ["https://extracted.com"]
    
    result = get_content_links()
    
    # Verify extraction was called for France
    
    assert mock_extract.call_args.args == ("https://test.com/france",), f"failed, expected {mock_extract.call_args.args}"

    
    # Verify the final dictionary
    assert result == {"france": ["https://extracted.com"]}
    
    # Verify it attempted to save the results
    mock_file.assert_called_once_with(Path("mock_folder/mock_tech.json"), "r")
    mock_save.assert_called_once()
    assert "mock_content.json" in str(mock_save.call_args[0][1])

@patch("ceatw_update_pipeline.education_profiles.get_education_profiles.save_json_to_file")
@patch("ceatw_update_pipeline.education_profiles.get_education_profiles.extract_content_links")
@patch("ceatw_update_pipeline.education_profiles.get_education_profiles.get_technology_page_urls")
@patch("builtins.open")
def test_get_content_links_fetches_if_json_invalid(mock_open_file, mock_get_tech_urls, mock_extract, mock_save):
    """Tests fallback to fetching URLs if the JSON file is missing or invalid."""
    # Simulate an invalid JSON file
    mock_open_file.side_effect = json.JSONDecodeError("Expecting value", "", 0)
    
    # Fake the fallback function return
    mock_get_tech_urls.return_value = {"japan": "https://test.com/japan"}
    mock_extract.return_value = ["https://japan-data.com"]
    
    result = get_content_links()
    
    mock_get_tech_urls.assert_called_once()
    assert result == {"japan": ["https://japan-data.com"]}


# ==========================================
# Tests for get_technology_page_urls
# ==========================================
@patch("ceatw_update_pipeline.education_profiles.get_education_profiles.save_json_to_file")
@patch("ceatw_update_pipeline.education_profiles.get_education_profiles.is_valid_url")
@patch("ceatw_update_pipeline.education_profiles.get_education_profiles.get_education_profiles_homepage")
def test_get_technology_page_urls(mock_get_homepage, mock_is_valid_url, mock_save):
    """Tests URL generation, validation, and saving mechanics."""
    dummy_html = """
    <html><body>
        <div class="cs-countries">
            <div class="country-template"><a class="country-name-flag" style="background-image: url('/sites/default/files/2019-09/Afghanistan_0.png');" href="/central-and-southern-asia/afghanistan/~afghanistan">Afghanistan</a><span><a href="/central-and-southern-asia/afghanistan/~afghanistan">En</a><a class="cursor-default">Fr</a><a class="cursor-default">Es</a></span></div>
            <div class="country-template"><a class="country-name-flag" style="background-image: url('/sites/default/files/2024-12/Flag_of_Andorra.svg_.png');" href="/europe-and-northern-america/andorra/~andorra">Andorra</a><span><a href="/europe-and-northern-america/andorra/~andorra">En</a><a class="cursor-default">Fr</a><a class="cursor-default">Es</a></span></div>
            <div class="country-template"><a class="country-name-flag" style="background-image: url('/sites/default/files/2020-03/2560px-Flag_of_Anguilla.svg_.png');" href="/latin-america-and-the-caribbean/anguilla/~anguilla">Anguilla</a><span><a href="/latin-america-and-the-caribbean/anguilla/~anguilla">En</a><a class="cursor-default">Fr</a><a class="cursor-default">Es</a></span></div>
        </div>
    </body></html>
    """
    mock_get_homepage.return_value = BeautifulSoup(dummy_html, "html.parser")
    
    # France passes, Japan fails
    def mock_valid_url_behavior(url):
        return "afghanistan" in url
        
    mock_is_valid_url.side_effect = mock_valid_url_behavior
    
    result = get_technology_page_urls()
    
    # Assert return value
    expected_dict = {"afghanistan": "https://education-profiles.org/central-and-southern-asia/afghanistan/~technology"}
    assert result == expected_dict
    
    # Assert saving behavior (should be called twice: once for successes, once for failures)
    assert mock_save.call_count == 2
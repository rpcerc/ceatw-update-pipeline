from ceatw_update_pipeline.filter import is_valid_url
from ceatw_update_pipeline.configuration import (
EDUCATION_PROFILES_OUTPUT_FOLDER,
EDUCATION_PROFILES_TECH_URL_FILE,
EDUCATION_PROFILES_FAILED_TECH_URL_FILE,
EDUCATION_PROFILES_CONTENT_URL_FILE)
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from typing import Any
from pathlib import Path
import requests
import re
import json

def get_education_profiles_homepage() -> BeautifulSoup:
    """Returns the education profiles homepage.

    Returns:
        BeautifulSoup: An object representing the HTML of the home page.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://education-profiles.org", wait_until="networkidle") 
        html_content = page.content()
        browser.close()
        
        soup = BeautifulSoup(html_content, "html.parser")
        return soup
    
def save_json_to_file(data: list | dict[str, Any], output_path: Path | str):
    """Saves json data to a given output folder path.

    Args:
        data (list | dict[str, Any]): The json to save.
        output_path (Path | str): The output file location.
    """
    output_path = Path(output_path)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def get_technology_page_urls() -> dict[str, str]:
    """Writes the list of technology page urls for each country to a file, 
       as well as a list of countries with no technology page urls.

    Returns:
        dict[str, str]: the JSON object representing the technology page urls.
    """
    soup = get_education_profiles_homepage()
    technology_urls = {}
    failed_countries = []
    country_divs = soup.select('div.country-template')
    
    for div in country_divs:
        a_tag = div.select_one('span a')
        
        if a_tag and a_tag.get('href'):
            # Very specific - relies on href links being of form '/.../.../~[a country]'
            href = a_tag['href']
            country = re.search(r"~.+", href).group(0)[1:]
            tech_url = "https://education-profiles.org" + re.sub(r"~.+", "~technology", href)
         
            if not is_valid_url(tech_url):
                print(f"No technology page for: {country}")
                failed_countries.append(country)
                continue
            technology_urls[country] = tech_url
            
    save_json_to_file(technology_urls, Path(EDUCATION_PROFILES_OUTPUT_FOLDER) / 
                      Path(EDUCATION_PROFILES_TECH_URL_FILE))
    
    save_json_to_file(failed_countries, Path(EDUCATION_PROFILES_OUTPUT_FOLDER) / 
                       Path(EDUCATION_PROFILES_FAILED_TECH_URL_FILE))
    
    return technology_urls

def is_relevant_link(href: str) -> bool:
    """Checks if a link links to a potentially relevant page/website.

    Args:
        href (str): The link to check.

    Returns:
        bool: True if the link leads somewhere else.
    """
    if not href:
        return False
        
    # Ignore anchor jumps and scripts
    if href.startswith(("#", "javascript:", "mailto:", "tel:")):
        return False
        
    return True

def extract_content_links(url: str) -> list[str]:
    """Extracts the relevant links from the main content of an 
       education profiles technology link.

    Args:
        url (str): A url to an education profiles technology page for a country.

    Returns:
        list[str]: A list of potentially releveant links.
    """
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        content_area = soup.find('div', id="block-mainpagecontent")
        # If we still can't find a content area, fallback to the whole remaining body
        if not content_area:
            print("Didnt find main content, using body.")
            content_area = soup.body

        relevant_links = set()  # Use a set to prevent duplicates
        
        for a_tag in content_area.find_all('a', href=True):
            href = a_tag['href'].strip()
            
            if is_relevant_link(href):
                relevant_links.add(href)
                
        return list(relevant_links)
    except requests.RequestException:
        return []
    
def get_content_links() -> dict[str, list[str]]:
    """Get the education profile links for each country with a technology page.

    Returns:
        dict[str, list[str]]: The list of content links for each country.
    """
    try:
        with open(Path(EDUCATION_PROFILES_OUTPUT_FOLDER) / 
                      Path(EDUCATION_PROFILES_TECH_URL_FILE), "r") as f:
            tech_page_urls = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
       tech_page_urls = get_technology_page_urls()
    
    content_urls = {}
    
    for country, url in tech_page_urls.items():
        content_urls[country] = extract_content_links(url)
    
    save_json_to_file(content_urls, Path(EDUCATION_PROFILES_OUTPUT_FOLDER) / 
                      Path(EDUCATION_PROFILES_CONTENT_URL_FILE))

    return content_urls
        
    

if __name__ == "__main__":
    get_content_links()
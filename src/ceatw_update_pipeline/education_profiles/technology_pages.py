from ceatw_update_pipeline.filter import is_valid_url
import requests
from bs4 import BeautifulSoup
import re
import json

def get_technology_pages():
    with open("education_profiles.html") as file:
        soup = BeautifulSoup(file.read(), 'html.parser')
    technology_urls = {}
    country_divs = soup.select('div.country-template')

    for div in country_divs:
        # For each div, grab the first 'a' tag that is inside a 'span'
        a_tag = div.select_one('span a')
        
        if a_tag and a_tag.get('href'):
            href = a_tag['href']
            # Switch the profile type from country to technology
            country = re.search(r"~.+", href).group(0)[1:]
            tech_url = "https://education-profiles.org" + re.sub(r"~.+", "~technology", href)
            
            if not is_valid_url(tech_url):
                print(f"Not okay, {tech_url}")
                
            technology_urls[country] = tech_url
            
def is_relevant_link(href: str) -> bool:
    """Checks if a single link is likely a content link rather than navigation."""
    if not href:
        return False
        
    # Ignore anchor jumps and scripts
    if href.startswith(("#", "javascript:", "mailto:", "tel:")):
        return False
        
    return True

def extract_content_links(url: str) -> list[str]:
    """Extracts relevant links from the main content of a webpage."""
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        content_area = soup.find('div', id="block-mainpagecontent")
        
        # If we still can't find a content area, fallback to the whole remaining body
        if not content_area:
            print("Didnt find main content, using body.")
            content_area = soup.body

        # 3. Extract and filter links
        relevant_links = set()  # Use a set to prevent duplicates
        
        for a_tag in content_area.find_all('a', href=True):
            href = a_tag['href'].strip()
            
            if is_relevant_link(href):
                relevant_links.add(href)
                
        return list(relevant_links)
    except requests.RequestException:
        return []
    
            
def get_content_urls():
    try:
        with open("technology_urls.json", "r") as content_url_file:
            country_urls = json.load(content_url_file)
    except json.JSONDecodeError:
        country_urls = {}
            
    with open("technology_pages.json", "r") as file:
        country_dict = json.load(file)
        for country, url in country_dict.items():
            if country in country_urls:
                print(f"{country} already cached")
                continue
            country_urls[country] = extract_content_links(url)
            
            with open("technology_urls.json", "w") as writefile:
                json.dump(country_urls, writefile, indent=4)
            
            print("finished " + country)
            
if __name__ == "__main__":
    get_content_urls()
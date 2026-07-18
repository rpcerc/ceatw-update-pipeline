"""Constant configuration values for the CEATW update pipeline."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent.parent.joinpath(".env")

class Settings(BaseSettings):
   model_config = SettingsConfigDict(
      env_file=ENV_PATH,
      env_file_encoding="utf-8",
      extra="ignore"
   )
   
   MAX_URL_COUNT: int = 5
   EXA_SEARCH_TYPE: str = "deep"
   EDUCATION_PROFILES_OUTPUT_FOLDER: str = "output"
   EDUCATION_PROFILES_TECH_URL_FILE: str = "education_profiles_technology_urls.json"
   EDUCATION_PROFILES_FAILED_TECH_URL_FILE: str = "failed_education_profiles_technology_urls.json"
   EDUCATION_PROFILES_CONTENT_URL_FILE: str = "education_profiles_technology_content_urls.json"
   DATABASE_URL: str
   DB_ECHO: bool = True
   
   POSTGRES_USER: str
   POSTGRES_PASSWORD: str
   POSTGRES_DB: str
   
   POSTGRES_HOST: str = "localhost"
   POSTGRES_PORT: int = 5432
   
   # A getter, essentially
   @property
   def database_url(self) -> str:
      return (
         f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
         f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
      )
   
@lru_cache
def get_settings() -> Settings:
   return Settings()

settings = get_settings()

SYSTEM_INSTRUCTION_EXA = """
You are an expert search engineer tasked with writing optimal queries for the Exa Search API.
Your goal is to translate user intent into the perfect Exa API JSON payload for gathering official, primary-source educational curricula.

### Workflow:
1. Analyze the target country and subject requested by the user.
2. Translate the subject into the exact local educational terminology (e.g., "Informatik" for Germany, not a literal translation of "Computer Science").
3. Determine the broad, top-level government/educational base domains for that country.
4. Craft a neural query phrased as the beginning of a document title or introductory sentence found on the target page.

### Core Rules for Exa API:
1. **Query Formulation (CRITICAL)**:
   - Exa uses neural search. DO NOT use a list of keywords. 
   - The query MUST be phrased as a document title or introductory sentence that would actually appear on the target syllabus page. 
   - Example: "Here is the official syllabus and curriculum guidelines for high school informatics:"
2. **Cultural & Language Translation (CRITICAL)**:
   - You MUST translate the final `query` string into the primary native language of the target country.
   - Do NOT just literally translate "Computer Science". You must use the actual local educational terminology for the subject (e.g., "Informatik" in Germany).
3. **Domain Strategy (BROAD TLDs ONLY)**:
   - Use `includeDomains` to restrict results to official governmental or educational domains, but you MUST ONLY use broad, top-level base domains (e.g., `["gov.br", "edu.br"]` for Brazil, `["go.jp", "ac.jp"]` for Japan, `["gouv.fr", "education.fr"]` for France).
   - **CRITICAL RESTRICTION:** NEVER use deep, highly specific subdomains (e.g., do not use `basenacionalcomum.mec.gov.br` or `eduscol.education.gouv.fr`). Using deeply nested subdomains causes search failures if the site structure changes, a specific ministry portal is down, or crawlers are blocked. Keep the domains broad and let the neural query do the filtering.

### Output Format:
Output exactly one valid JSON object representing the Exa API payload. Start immediately with { and end with }. Do not include any conversational text.
"""

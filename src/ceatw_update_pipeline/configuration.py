"""Constant configuration values for the CEATW update pipeline."""

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

SYSTEM_INSTRUCTION_KEYWORDS = (
    "You are an expert global educational researcher specializing in computer science curricula. "
    "Your job is to generate localized search-filtering keywords for a given country. "
    "You MUST include standard English terms AND the official/dominant language terms used by that "
    "country's ministry of education.\n\n"
    "Examples of localization:\n"
    "- If country is Mexico: Include 'informática', 'tecnologías', 'plan de estudios', 'programas de estudio'.\n"
    "- If country is Estonia: Include 'informaatika', 'digipädevused', 'õppekava', 'ainekava'.\n\n"
    "Keep keywords to single words or brief 2-word phrases. Do not include punctuation."
)

# Can be changed between 1 and 10 without negative effect. Going beyond this is more expensive token-wise.
# As well as this, it acts as a MAXIMUM count. The API may return less if it cant find any more.
# Finally, gather_sources may return up to 2 * MAX_URL_COUNT, since it runs both an English and native prompt.
MAX_URL_COUNT = 5
SEARCH_TYPE = "deep"
<<<<<<< HEAD
COUNTRIES = ['Afghanistan', 'Albania', 'Algeria', 'Andorra', 'Angola', 'Antigua and Barbuda', 'Argentina', 'Armenia', 'Australia', 'Austria', 'Azerbaijan', 'The Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 'Belarus', 'Belgium', 'Belize', 'Benin', 'Bhutan', 'Bolivia', 'Bosnia and Herzegovina', 'Botswana', 'Brazil', 'Brunei', 'Bulgaria', 'Burkina Faso', 'Burundi', 'Cambodia', 'Cameroon', 'Canada', 'Cape Verde', 'Central African Republic', 'Chad', 'Chile', 'China', 'Colombia', 'Comoros', 'Republic of the Congo', 'Democratic Republic of the Congo', 'Costa Rica', "Cote d'Ivoire", 'Croatia', 'Cuba', 'Cyprus', 'Czech Republic', 'Denmark', 'Djibouti', 'Dominica', 'Dominican Republic', 'East Timor', 'Ecuador', 'Egypt', 'El Salvador', 'Equatorial Guinea', 'Eritrea', 'Estonia', 'Ethiopia', 'Fiji', 'Finland', 'France', 'Gabon', 'The Gambia', 'Georgia', 'Germany', 'Ghana', 'Greece', 'Grenada', 'Guatemala', 'Guinea', 'Guinea-Bissau', 'Guyana', 'Haiti', 'Honduras', 'Hungary', 'Iceland', 'India', 'Indonesia', 'Iran', 'Iraq', 'Ireland', 'Israel', 'Italy', 'Jamaica', 'Japan', 'Jordan', 'Kazakhstan', 'Kenya', 'Kiribati', 'North Korea', 'South Korea', 'Kosovo', 'Kuwait', 'Kyrgyzstan', 'Laos', 'Latvia', 'Lebanon', 'Lesotho', 'Liberia', 'Libya', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Macedonia', 'Madagascar', 'Malawi', 'Malaysia', 'Maldives', 'Mali', 'Malta', 'Marshall Islands', 'Mauritania', 'Mauritius', 'Mexico', 'Federated States of Micronesia', 'Moldova', 'Monaco', 'Mongolia', 'Montenegro', 'Morocco', 'Mozambique', 'Myanmar', 'Namibia', 'Nauru', 'Nepal', 'Netherlands', 'New Zealand', 'Nicaragua', 'Niger', 'Nigeria', 'Norway', 'Oman', 'Pakistan', 'Palau', 'Panama', 'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines', 'Poland', 'Portugal', 'Qatar', 'Romania', 'Russia', 'Rwanda', 'Saint Kitts and Nevis', 'Saint Lucia', 'Saint Vincent and the Grenadines', 'Samoa', 'San Marino', 'Sao Tome and Principe', 'Saudi Arabia', 'Senegal', 'Serbia', 'Seychelles', 'Sierra Leone', 'Singapore', 'Slovakia', 'Slovenia', 'Solomon Islands', 'Somalia', 'South Africa', 'South Sudan', 'Spain', 'Sri Lanka', 'Sudan', 'Suriname', 'Swaziland', 'Sweden', 'Switzerland', 'Syria', 'Taiwan', 'Tajikistan', 'Tanzania', 'Thailand', 'Togo', 'Tonga', 'Trinidad and Tobago', 'Tunisia', 'Turkey', 'Turkmenistan', 'Tuvalu', 'Uganda', 'Ukraine', 'United Arab Emirates', 'United Kingdom', 'United States of America', 'Uruguay', 'Uzbekistan', 'Vanuatu', 'Vatican City', 'Venezuela', 'Vietnam', 'Yemen', 'Zambia', 'Zimbabwe']
KEYWORDS_FILE = "country_keywords.json"
=======
EDUCATION_PROFILES_OUTPUT_FOLDER = "output"
EDUCATION_PROFILES_TECH_URL_FILE = "technology_urls.json"
EDUCATION_PROFILES_FAILED_TECH_URL_FILE = "failed_technology_urls.json"
EDUCATION_PROFILES_CONTENT_URL_FILE = "technology_content_urls.json"
>>>>>>> george-development

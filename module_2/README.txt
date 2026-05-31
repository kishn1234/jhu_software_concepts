Kishore Narayanan
JHED ID: knaraya8@jh.edu

Module 2 Assignment: Web Scraping
Due 5/31/2026

Robots.txt compliance:
Checked https://www.thegradcafe.com/robots.txt initially. 
The robots.txt file includes "User-agent: *" and "Allow: /", indicating that the pages 
are allowing access to general crawlers.
This project scrapes only publicly available GradCafe survey result pages and does not 
bypass restrictions.

Scraping:
GradCafe survey results - https://www.thegradcafe.com/survey
pagination format - https://www.thegradcafe.com/survey?page=2
~20 entries per page
To collect 30,000 entries, the scraper will collect ~1500 pages and use 
polite delays between requests.

    Approach:
    This project uses urllib to retrieve survey pages from GradCafe.
    BeautifulSoup is used to parse HTML content and extract applicant info from the survey 
    result table.
    Regex is used to extract structured values (ex. term, GPA).
    Scraper follows robots.txt guidance and uses delays between requests to avoid excessive
    traffic.
    Data is saved to applicant_data.json
    clean.py loads scraped data, cleans the data, and saves records to 
    llm_extend_applicant_data.json.

After Testing: 
Provided llm_hosting package was tested successfully using sample_data.json. 
The local LLM generated standardized program/university names while preserving the original 
scraped data.

Known Bugs:
During scraping, the GradCafe website occasionally returns HTTP 500 responses, which are 
responded to by the scraper waiting 30 seconds and retrying the request.
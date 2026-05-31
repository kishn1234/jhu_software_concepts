Robots.txt compliance:
Checked https://www.thegradcafe.com/robots.txt initially. 
The robots.txt file includes "User-agent: *" and "Allow: /", indicating 
that the pages are allowing access to general crawlers.
This project scrapes only publicly available GradCafe survery result pages
and does not bypass restrictions.

Scraping:
GradCafe survey results - https://www.thegradcafe.com/survey
pagination format - https://www.thegradcafe.com/survey?page=2
~20 entries per page
To collect 30,000 entries, the scraper will collect ~1500 pages and use 
polite delays between requests.
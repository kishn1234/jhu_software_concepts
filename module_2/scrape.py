import json
import re
import ssl
import time
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup


BASE_URL = "https://www.thegradcafe.com"
SURVEY_URL = "https://www.thegradcafe.com/survey?page={page}"


def fetch_page(page):
    """Fetch one GradCafe survey page using urllib."""
    url = SURVEY_URL.format(page=page)
    context = ssl._create_unverified_context()
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=30, context=context) as response:
        return response.read().decode("utf-8", errors="ignore")


def scrape_data(max_pages=1):
    """Pull applicant data from GradCafe."""
    records = []

    for page in range(1, max_pages + 1):
        html = fetch_page(page)
        soup = BeautifulSoup(html, "html.parser")
        rows = soup.find_all("tr")

        print(f"Page {page}: found {len(rows)} table rows")

        time.sleep(1)

    return records


if __name__ == "__main__":
    data = scrape_data(max_pages=1)
    print(f"Scraped {len(data)} records")
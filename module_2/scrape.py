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


def _clean_text(value):
    """Normalize whitespace in scraped text."""
    if not value:
        return ""
    return " ".join(value.split())


def _extract_record(main_row, detail_row):
    """Extract one applicant record from a main row and detail row."""
    cells = main_row.find_all("td")

    link = main_row.find("a", href=True)
    relative_url = link["href"] if link else ""

    detail_text = _clean_text(detail_row.get_text(" ", strip=True)) if detail_row else ""

    return {
        "university": _clean_text(cells[0].get_text(" ", strip=True)) if len(cells) > 0 else "",
        "program": _clean_text(cells[1].find_all("span")[0].get_text(" ", strip=True)) if len(cells) > 1 and cells[1].find_all("span") else "",
        "degree": _clean_text(cells[1].find_all("span")[-1].get_text(" ", strip=True)) if len(cells) > 1 and cells[1].find_all("span") else "",
        "date_added": _clean_text(cells[2].get_text(" ", strip=True)) if len(cells) > 2 else "",
        "status": _clean_text(cells[3].get_text(" ", strip=True)) if len(cells) > 3 else "",
        "url": urljoin(BASE_URL, relative_url),
        "raw_main_text": _clean_text(main_row.get_text(" ", strip=True)),
        "raw_detail_text": detail_text,
    }


def scrape_data(max_pages=1):
    """Pull applicant data from GradCafe."""
    records = []

    for page in range(1, max_pages + 1):
        html = fetch_page(page)
        soup = BeautifulSoup(html, "html.parser")
        rows = soup.find_all("tr")

        for i, row in enumerate(rows):
            if "/result/" in str(row):
                detail_row = rows[i + 1] if i + 1 < len(rows) else None
                records.append(_extract_record(row, detail_row))

        print(f"Page {page}: scraped {len(records)} total records")

        time.sleep(1)

    return records


if __name__ == "__main__":
    data = scrape_data(max_pages=1)
    print(f"Scraped {len(data)} records")
    print(data[:2])
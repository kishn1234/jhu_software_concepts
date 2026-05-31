import json
import re
import ssl
import time
from urllib.parse import urljoin
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from bs4 import BeautifulSoup


BASE_URL = "https://www.thegradcafe.com"
SURVEY_URL = "https://www.thegradcafe.com/survey?page={page}"
OUTPUT_FILE = "applicant_data.json"
TARGET_RECORDS = 30000
DELAY_SECONDS = 2


def fetch_page(page):
    """Fetch one GradCafe survey page using urllib."""
    url = SURVEY_URL.format(page=page)

    context = ssl._create_unverified_context()

    req = Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urlopen(req, timeout=30, context=context) as response:
        return response.read().decode("utf-8", errors="ignore")


def clean_text(value):
    if not value:
        return ""
    return " ".join(value.split())


def extract_gpa(detail_text):
    match = re.search(r"GPA\s+([0-9.]+)", detail_text)
    return match.group(1) if match else ""


def extract_term(detail_text):
    match = re.search(r"(Fall|Spring|Summer|Winter)\s+\d{4}", detail_text)
    return match.group(0) if match else ""


def extract_applicant_type(detail_text):
    if "International" in detail_text:
        return "International"

    if "American" in detail_text:
        return "American"

    return ""


def extract_record(main_row, detail_row):
    cells = main_row.find_all("td")

    spans = cells[1].find_all("span") if len(cells) > 1 else []

    link = main_row.find("a", href=True)
    relative_url = link["href"] if link else ""

    detail_text = (
        clean_text(detail_row.get_text(" ", strip=True))
        if detail_row
        else ""
    )

    return {
        "university": clean_text(cells[0].get_text(" ", strip=True))
        if len(cells) > 0 else "",

        "program": clean_text(spans[0].get_text(" ", strip=True))
        if len(spans) > 0 else "",

        "degree": clean_text(spans[-1].get_text(" ", strip=True))
        if len(spans) > 0 else "",

        "date_added": clean_text(cells[2].get_text(" ", strip=True))
        if len(cells) > 2 else "",

        "status": clean_text(cells[3].get_text(" ", strip=True))
        if len(cells) > 3 else "",

        "term": extract_term(detail_text),

        "applicant_type": extract_applicant_type(detail_text),

        "gpa": extract_gpa(detail_text),

        "url": urljoin(BASE_URL, relative_url),

        "raw_main_text": clean_text(
            main_row.get_text(" ", strip=True)
        ),

        "raw_detail_text": detail_text
    }


def save_json(records, output_file=OUTPUT_FILE):
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(
            records,
            file,
            indent=2,
            ensure_ascii=False
        )


def scrape_data(target_records=TARGET_RECORDS):
    records = []
    page = 1

    while len(records) < target_records:

        try:
            html = fetch_page(page)

        except HTTPError as error:

            print(f"Page {page}: HTTP Error {error.code}")

            if error.code == 500:
                print("Waiting 30 seconds and retrying...")
                time.sleep(30)
                continue

            raise

        soup = BeautifulSoup(html, "html.parser")

        rows = soup.find_all("tr")

        page_count = 0

        for i, row in enumerate(rows):

            if "/result/" in str(row):

                detail_row = (
                    rows[i + 1]
                    if i + 1 < len(rows)
                    else None
                )

                records.append(
                    extract_record(row, detail_row)
                )

                page_count += 1

                if len(records) >= target_records:
                    break

        print(
            f"Page {page}: added {page_count} records; "
            f"total = {len(records)}"
        )

        if page % 100 == 0:
            save_json(records)
            print(f"Checkpoint saved at page {page}")

        page += 1

        time.sleep(DELAY_SECONDS)

    return records


if __name__ == "__main__":

    applicant_records = scrape_data()

    save_json(applicant_records)

    print(
        f"Saved {len(applicant_records)} records "
        f"to {OUTPUT_FILE}"
    )

import json


INPUT_FILE = "applicant_data.json"
OUTPUT_FILE = "llm_extend_applicant_data.json"


def load_data(input_file=INPUT_FILE):
    """Load scraped applicant data from a JSON file."""
    with open(input_file, "r", encoding="utf-8") as file:
        return json.load(file)


def _clean_text(value):
    """Clean text fields and remove leftover whitespace."""
    if value is None:
        return ""
    return " ".join(str(value).split())


def clean_data(records):
    """Convert scraped data into a cleaner structured format."""
    cleaned_records = []

    for record in records:
        cleaned_record = {
            "program": _clean_text(record.get("program", "")),
            "university": _clean_text(record.get("university", "")),
            "comments": _clean_text(record.get("comments", "")),
            "date_added": _clean_text(record.get("date_added", "")),
            "url": _clean_text(record.get("url", "")),
            "status": _clean_text(record.get("status", "")),
            "term": _clean_text(record.get("term", "")),
            "US/International": _clean_text(record.get("applicant_type", "")),
            "Degree": _clean_text(record.get("degree", "")),
            "GPA": _clean_text(record.get("gpa", "")),
            "raw_main_text": _clean_text(record.get("raw_main_text", "")),
            "raw_detail_text": _clean_text(record.get("raw_detail_text", "")),
        }

        cleaned_records.append(cleaned_record)

    return cleaned_records


def save_data(records, output_file=OUTPUT_FILE):
    """Save cleaned applicant data to a JSON file."""
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    applicant_data = load_data()
    cleaned_data = clean_data(applicant_data)
    save_data(cleaned_data)
    print(f"Cleaned {len(cleaned_data)} records")
    print(f"Saved cleaned data to {OUTPUT_FILE}")
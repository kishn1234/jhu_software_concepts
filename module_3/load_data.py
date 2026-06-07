import json
import psycopg
from datetime import datetime
from pathlib import Path


DB_NAME = "gradcafe"
DATA_FILE = Path("../module_2/applicant_data.json")
LLM_FILE = Path("../module_2/llm_extend_applicant_data.json")


def clean_float(value):
    if value is None:
        return None

    value = str(value).strip()

    if value == "":
        return None

    try:
        return float(value)
    except ValueError:
        return None


def clean_gpa(value):
    number = clean_float(value)

    if number is not None and 0 <= number <= 4.3:
        return number

    return None


def clean_gre(value):
    number = clean_float(value)

    if number is not None and 130 <= number <= 170:
        return number

    return None


def clean_gre_aw(value):
    number = clean_float(value)

    if number is not None and 0 <= number <= 6:
        return number

    return None


def clean_date(value):
    if value is None:
        return None

    value = str(value).strip()

    if value == "":
        return None

    try:
        date_value = datetime.strptime(value, "%b %d, %Y")
        return date_value.strftime("%Y-%m-%d")
    except ValueError:
        return None


def find_value_after_label(text, label):
    if text is None:
        return None

    words = text.split()

    for i in range(len(words)):
        if words[i] == label and i + 1 < len(words):
            return words[i + 1]

    return None


def find_gre_v(text):
    if text is None:
        return None

    words = text.split()

    for i in range(len(words) - 1):
        if words[i] == "GRE" and words[i + 1] == "V" and i + 2 < len(words):
            return words[i + 2]

    return None


def find_gre_aw(text):
    if text is None:
        return None

    words = text.split()

    for i in range(len(words) - 1):
        if words[i] == "GRE" and words[i + 1] == "AW" and i + 2 < len(words):
            return words[i + 2]

    return None


def find_gre(text):
    if text is None:
        return None

    words = text.split()

    for i in range(len(words)):
        if words[i] == "GRE":
            if i + 1 < len(words):
                if words[i + 1] != "V" and words[i + 1] != "AW":
                    return words[i + 1]

    return None


def load_llm_data():
    llm_lookup = {}

    if not LLM_FILE.exists():
        return llm_lookup

    with open(LLM_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    for index, row in enumerate(data, start=1):
        llm_lookup[index] = row

    return llm_lookup


conn = psycopg.connect("dbname=gradcafe")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS applicants (
    p_id INTEGER PRIMARY KEY,
    program TEXT,
    university TEXT,
    comments TEXT,
    date_added DATE,
    url TEXT UNIQUE,
    status TEXT,
    term TEXT,
    us_or_international TEXT,
    gpa FLOAT,
    degree TEXT,
    gre FLOAT,
    gre_v FLOAT,
    gre_aw FLOAT,
    llm_generated_program TEXT,
    llm_generated_university TEXT
);
""")

with open(DATA_FILE, "r", encoding="utf-8") as file:
    applicant_data = json.load(file)

llm_data = load_llm_data()

cur.execute("SELECT COALESCE(MAX(p_id), 0) FROM applicants;")
max_p_id = cur.fetchone()[0]

inserted_count = 0
skipped_count = 0

for row in applicant_data:
    url = row.get("url")

    cur.execute("SELECT COUNT(*) FROM applicants WHERE url = %s;", (url,))
    existing_count = cur.fetchone()[0]

    if existing_count > 0:
        skipped_count = skipped_count + 1
    else:
        inserted_count = inserted_count + 1
        p_id = max_p_id + inserted_count

        program = row.get("program")
        university = row.get("university")
        comments = row.get("comments")
        date_added = clean_date(row.get("date_added"))
        status = row.get("status")
        term = row.get("term")
        us_or_international = row.get("applicant_type")
        degree = row.get("degree")
        raw_detail_text = row.get("raw_detail_text")

        gpa = clean_gpa(row.get("gpa"))
        if gpa is None:
            gpa = clean_gpa(find_value_after_label(raw_detail_text, "GPA"))

        gre = clean_gre(row.get("gre"))
        if gre is None:
            gre = clean_gre(find_gre(raw_detail_text))

        gre_v = clean_gre(row.get("gre_v"))
        if gre_v is None:
            gre_v = clean_gre(find_gre_v(raw_detail_text))

        gre_aw = clean_gre_aw(row.get("gre_aw"))
        if gre_aw is None:
            gre_aw = clean_gre_aw(find_gre_aw(raw_detail_text))

        llm_row = llm_data.get(inserted_count)

        if llm_row is not None:
            llm_generated_program = llm_row.get("llm_generated_program")
            llm_generated_university = llm_row.get("llm_generated_university")
        else:
            llm_generated_program = program
            llm_generated_university = university

        if llm_generated_program is None:
            llm_generated_program = program

        if llm_generated_university is None:
            llm_generated_university = university

        cur.execute("""
        INSERT INTO applicants (
            p_id,
            program,
            university,
            comments,
            date_added,
            url,
            status,
            term,
            us_or_international,
            gpa,
            degree,
            gre,
            gre_v,
            gre_aw,
            llm_generated_program,
            llm_generated_university
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, (
            p_id,
            program,
            university,
            comments,
            date_added,
            url,
            status,
            term,
            us_or_international,
            gpa,
            degree,
            gre,
            gre_v,
            gre_aw,
            llm_generated_program,
            llm_generated_university
        ))

conn.commit()
cur.close()
conn.close()

print("Data loading completed.")
print("New rows inserted:", inserted_count)
print("Existing rows skipped:", skipped_count)
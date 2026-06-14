import json
import psycopg
from datetime import datetime
from pathlib import Path


DB_NAME = "gradcafe"
DATA_FILE = Path("applicant_data.json")
LLM_FILE = Path("llm_extend_applicant_data.json")


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


def get_field(row, *names):
    for name in names:
        if name in row:
            return row.get(name)
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


def load_json_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_llm_data(file_path=LLM_FILE):
    llm_lookup = {}

    if not Path(file_path).exists():
        return llm_lookup

    data = load_json_file(file_path)

    for index, row in enumerate(data, start=1):
        llm_lookup[index] = row

    return llm_lookup


def create_table(cur):
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


def build_applicant_record(row, p_id, llm_row=None):
    raw_detail_text = get_field(row, "raw_detail_text", "Raw Detail Text")

    gpa = clean_gpa(get_field(row, "gpa", "GPA"))
    if gpa is None:
        gpa = clean_gpa(find_value_after_label(raw_detail_text, "GPA"))

    gre = clean_gre(get_field(row, "gre", "GRE"))
    if gre is None:
        gre = clean_gre(find_gre(raw_detail_text))

    gre_v = clean_gre(get_field(row, "gre_v", "GRE_V", "GRE V"))
    if gre_v is None:
        gre_v = clean_gre(find_gre_v(raw_detail_text))

    gre_aw = clean_gre_aw(get_field(row, "gre_aw", "GRE_AW", "GRE AW"))
    if gre_aw is None:
        gre_aw = clean_gre_aw(find_gre_aw(raw_detail_text))

    program = get_field(row, "program", "Program")
    university = get_field(row, "university", "University")

    if llm_row is not None:
        llm_generated_program = get_field(llm_row, "llm_generated_program", "LLM Generated Program")
        llm_generated_university = get_field(llm_row, "llm_generated_university", "LLM Generated University")
    else:
        llm_generated_program = program
        llm_generated_university = university

    if llm_generated_program is None:
        llm_generated_program = program

    if llm_generated_university is None:
        llm_generated_university = university

    return (
        p_id,
        program,
        university,
        get_field(row, "comments", "Comments"),
        clean_date(get_field(row, "date_added", "Date Added")),
        get_field(row, "url", "URL"),
        get_field(row, "status", "Status"),
        get_field(row, "term", "Term"),
        get_field(row, "applicant_type", "US/International"),
        gpa,
        get_field(row, "degree", "Degree"),
        gre,
        gre_v,
        gre_aw,
        llm_generated_program,
        llm_generated_university
    )


def insert_applicants(cur, applicant_data, llm_data):
    cur.execute("SELECT COALESCE(MAX(p_id), 0) FROM applicants;")
    max_p_id = cur.fetchone()[0]

    inserted_count = 0
    skipped_count = 0

    for row in applicant_data:
        url = get_field(row, "url", "URL")

        cur.execute("SELECT COUNT(*) FROM applicants WHERE url = %s;", (url,))
        existing_count = cur.fetchone()[0]

        if existing_count > 0:
            skipped_count = skipped_count + 1
        else:
            inserted_count = inserted_count + 1
            p_id = max_p_id + inserted_count
            llm_row = llm_data.get(inserted_count)

            applicant_record = build_applicant_record(row, p_id, llm_row)

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
            """, applicant_record)

    return inserted_count, skipped_count


def load_data(data_file=DATA_FILE, llm_file=LLM_FILE, db_name=DB_NAME):
    applicant_data = load_json_file(data_file)
    llm_data = load_llm_data(llm_file)

    conn = psycopg.connect(f"dbname={db_name}")
    cur = conn.cursor()

    create_table(cur)
    inserted_count, skipped_count = insert_applicants(cur, applicant_data, llm_data)

    conn.commit()
    cur.close()
    conn.close()

    return inserted_count, skipped_count


def main():
    inserted_count, skipped_count = load_data()

    print("Data loading completed.")
    print("New rows inserted:", inserted_count)
    print("Existing rows skipped:", skipped_count)


if __name__ == "__main__":  # pragma: no cover
    main()
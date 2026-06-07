import json
import re

import psycopg


INPUT_FILE = "llm_extend_applicant_data.json"


def clean_text(value):
    if value is None:
        return None
    text = " ".join(str(value).split())
    return text if text else None


def extract_gre_value(raw_text, label):
    if not raw_text:
        return None

    match = re.search(rf"{label}\s+([0-9.]+)", raw_text)
    return match.group(1) if match else None


def create_table(conn):
    with conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS applicants;")
        cur.execute("""
            CREATE TABLE applicants (
                id SERIAL PRIMARY KEY,
                program TEXT,
                university TEXT,
                comments TEXT,
                date_added TEXT,
                url TEXT,
                status TEXT,
                term TEXT,
                applicant_type TEXT,
                gpa TEXT,
                degree TEXT,
                gre TEXT,
                gre_v TEXT,
                gre_aw TEXT,
                llm_generated_program TEXT,
                llm_generated_university TEXT
            );
        """)
    conn.commit()


def load_records(conn, records):
    with conn.cursor() as cur:
        for record in records:
            raw_detail = record.get("raw_detail_text", "")

            cur.execute("""
                INSERT INTO applicants (
                    program,
                    university,
                    comments,
                    date_added,
                    url,
                    status,
                    term,
                    applicant_type,
                    gpa,
                    degree,
                    gre,
                    gre_v,
                    gre_aw,
                    llm_generated_program,
                    llm_generated_university
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                );
            """, (
                clean_text(record.get("program")),
                clean_text(record.get("university")),
                clean_text(record.get("comments")),
                clean_text(record.get("date_added")),
                clean_text(record.get("url")),
                clean_text(record.get("status")),
                clean_text(record.get("term")),
                clean_text(record.get("US/International")),
                clean_text(record.get("GPA")),
                clean_text(record.get("Degree")),
                extract_gre_value(raw_detail, "GRE"),
                extract_gre_value(raw_detail, "GRE V"),
                extract_gre_value(raw_detail, "GRE AW"),
                clean_text(record.get("llm-generated-program", record.get("program"))),
                clean_text(record.get("llm-generated-university", record.get("university"))),
            ))

    conn.commit()


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        records = json.load(file)

    conn = psycopg.connect(
        dbname="gradcafe",
        user="kishore.narayanan"
    )

    create_table(conn)
    load_records(conn, records)

    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM applicants;")
        count = cur.fetchone()[0]

    conn.close()

    print(f"Loaded {count} applicant records into PostgreSQL.")


if __name__ == "__main__":
    main()
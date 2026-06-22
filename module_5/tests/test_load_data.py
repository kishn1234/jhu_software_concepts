import pytest

from src.load_data import (
    clean_float,
    clean_gpa,
    clean_gre,
    clean_gre_aw,
    clean_date,
    find_value_after_label,
    find_gre,
    find_gre_v,
    find_gre_aw,
    get_field,
)

@pytest.mark.db
@pytest.mark.parametrize("value, expected", [
    ("3.5", 3.5),
    ("", None),
    (None, None),
    ("abc", None),
])
def test_clean_float(value, expected):
    assert clean_float(value) == expected

@pytest.mark.db
@pytest.mark.parametrize("value, expected", [
    ("3.8", 3.8),
    ("4.5", None),
    ("bad", None),
])
def test_clean_gpa(value, expected):
    assert clean_gpa(value) == expected

@pytest.mark.db
@pytest.mark.parametrize("value, expected", [
    ("165", 165.0),
    ("100", None),
    ("200", None),
])
def test_clean_gre(value, expected):
    assert clean_gre(value) == expected

@pytest.mark.db
@pytest.mark.parametrize("value, expected", [
    ("4.0", 4.0),
    ("7.0", None),
    ("bad", None),
])
def test_clean_gre_aw(value, expected):
    assert clean_gre_aw(value) == expected

@pytest.mark.db
def test_clean_date_valid():
    assert clean_date("May 31, 2026") == "2026-05-31"

@pytest.mark.db
def test_clean_date_invalid():
    assert clean_date("bad date") is None

@pytest.mark.db
def test_find_value_after_label():
    text = "Accepted Fall 2026 GPA 3.78"
    assert find_value_after_label(text, "GPA") == "3.78"

@pytest.mark.db
def test_find_gre_values():
    text = "International GRE 159 GRE V 170 GRE AW 3.50 GPA 3.78"

    assert find_gre(text) == "159"
    assert find_gre_v(text) == "170"
    assert find_gre_aw(text) == "3.50"

@pytest.mark.db
def test_get_field():
    row = {"Degree": "Masters"}

    assert get_field(row, "degree", "Degree") == "Masters"

@pytest.mark.db
def test_build_applicant_record_with_direct_fields():
    from src.load_data import build_applicant_record

    row = {
        "program": "Computer Science",
        "university": "Johns Hopkins University",
        "comments": "Good result",
        "date_added": "May 31, 2026",
        "url": "https://example.com/result/1",
        "status": "Accepted on May 31",
        "term": "Fall 2026",
        "applicant_type": "American",
        "gpa": "3.90",
        "degree": "Masters",
        "gre": "165",
        "gre_v": "160",
        "gre_aw": "4.5",
    }

    record = build_applicant_record(row, 1)

    assert record[0] == 1
    assert record[1] == "Computer Science"
    assert record[2] == "Johns Hopkins University"
    assert record[4] == "2026-05-31"
    assert record[8] == "American"
    assert record[9] == 3.90
    assert record[10] == "Masters"
    assert record[11] == 165.0
    assert record[12] == 160.0
    assert record[13] == 4.5

@pytest.mark.db
def test_build_applicant_record_with_rubric_style_fields():
    from src.load_data import build_applicant_record

    row = {
        "Program": "Data Science",
        "University": "Stanford University",
        "Comments": "No comments",
        "Date Added": "May 31, 2026",
        "URL": "https://example.com/result/2",
        "Status": "Rejected on May 31",
        "Term": "Fall 2026",
        "US/International": "International",
        "GPA": "3.78",
        "Degree": "PhD",
        "GRE": "168",
        "GRE V": "164",
        "GRE AW": "4.0",
    }

    llm_row = {
        "LLM Generated Program": "Computer Science",
        "LLM Generated University": "Stanford University",
    }

    record = build_applicant_record(row, 2, llm_row)

    assert record[0] == 2
    assert record[1] == "Data Science"
    assert record[2] == "Stanford University"
    assert record[8] == "International"
    assert record[10] == "PhD"
    assert record[14] == "Computer Science"
    assert record[15] == "Stanford University"

@pytest.mark.db
def test_build_applicant_record_extracts_scores_from_raw_text():
    from src.load_data import build_applicant_record

    row = {
        "program": "Statistics",
        "university": "MIT",
        "date_added": "May 31, 2026",
        "url": "https://example.com/result/3",
        "status": "Accepted on May 31",
        "term": "Fall 2026",
        "applicant_type": "International",
        "degree": "PhD",
        "raw_detail_text": "Accepted Fall 2026 International GRE 159 GRE V 170 GRE AW 3.50 GPA 3.78",
    }

    record = build_applicant_record(row, 3)

    assert record[9] == 3.78
    assert record[11] == 159.0
    assert record[12] == 170.0
    assert record[13] == 3.50

from pathlib import Path
from src import load_data

@pytest.mark.db
def test_find_helpers_return_none_for_missing_values():
    assert load_data.find_value_after_label(None, "GPA") is None
    assert load_data.find_value_after_label("No GPA here", "GPA") == "here"
    assert load_data.find_gre(None) is None
    assert load_data.find_gre("No score here") is None
    assert load_data.find_gre_v(None) is None
    assert load_data.find_gre_v("GRE 160 only") is None
    assert load_data.find_gre_aw(None) is None
    assert load_data.find_gre_aw("GRE V 160 only") is None

@pytest.mark.db
def test_load_llm_data_missing_file(tmp_path):
    missing_file = tmp_path / "missing.json"

    result = load_data.load_llm_data(missing_file)

    assert result == {}

@pytest.mark.db
def test_load_json_file(tmp_path):
    test_file = tmp_path / "sample.json"
    test_file.write_text('[{"name": "test"}]', encoding="utf-8")

    result = load_data.load_json_file(test_file)

    assert result == [{"name": "test"}]

@pytest.mark.db
def test_create_table_calls_execute():
    class FakeCursor:
        def __init__(self):
            self.called = False

        def execute(self, sql):
            self.called = True
            assert "CREATE TABLE IF NOT EXISTS applicants" in sql

    cursor = FakeCursor()

    load_data.create_table(cursor)

    assert cursor.called is True

@pytest.mark.db
def test_insert_applicants_inserts_and_skips_records():
    class FakeCursor:
        def __init__(self):
            self.results = [10, 0, 1]
            self.insert_called = False

        def execute(self, sql, params=None):
            if "INSERT INTO applicants" in sql:
                self.insert_called = True

        def fetchone(self):
            return (self.results.pop(0),)

    cursor = FakeCursor()

    applicant_data = [
        {
            "program": "Computer Science",
            "university": "JHU",
            "date_added": "May 31, 2026",
            "url": "url-1",
            "status": "Accepted",
            "term": "Fall 2026",
            "applicant_type": "American",
            "degree": "Masters",
        },
        {
            "program": "Data Science",
            "university": "MIT",
            "date_added": "May 31, 2026",
            "url": "url-2",
            "status": "Rejected",
            "term": "Fall 2026",
            "applicant_type": "International",
            "degree": "PhD",
        },
    ]

    inserted, skipped = load_data.insert_applicants(cursor, applicant_data, {})

    assert inserted == 1
    assert skipped == 1
    assert cursor.insert_called is True

@pytest.mark.db
def test_load_data_calls_database_functions(monkeypatch, tmp_path):
    test_file = tmp_path / "applicant_data.json"
    test_file.write_text("[]", encoding="utf-8")

    llm_file = tmp_path / "llm.json"
    llm_file.write_text("[]", encoding="utf-8")

    class FakeCursor:
        def execute(self, sql, params=None):
            pass

        def fetchone(self):
            return (0,)

        def close(self):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

    class FakeConnection:
        def cursor(self):
            return FakeCursor()

        def commit(self):
            pass

        def close(self):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

    def fake_connect(*args, **kwargs):
        return FakeConnection()

    monkeypatch.setattr(load_data.psycopg, "connect", fake_connect)

    inserted, skipped = load_data.load_data(
        test_file,
        llm_file,
        "fake_db",
    )

    assert inserted == 0
    assert skipped == 0

@pytest.mark.db
def test_clean_date_none_and_blank():
    assert load_data.clean_date(None) is None
    assert load_data.clean_date("") is None

@pytest.mark.db
def test_find_value_after_label_not_found():
    assert load_data.find_value_after_label("Accepted Fall 2026", "GPA") is None

@pytest.mark.db
def test_load_llm_data_existing_file(tmp_path):
    llm_file = tmp_path / "llm.json"
    llm_file.write_text('[{"program": "Computer Science"}]', encoding="utf-8")

    result = load_data.load_llm_data(llm_file)

    assert result == {1: {"program": "Computer Science"}}

@pytest.mark.db
def test_build_applicant_record_llm_values_fallback_to_program_university():
    row = {
        "program": "Computer Science",
        "university": "JHU",
        "date_added": "May 31, 2026",
        "url": "url-4",
        "status": "Accepted",
        "term": "Fall 2026",
        "applicant_type": "American",
        "degree": "Masters",
    }

    llm_row = {
        "llm_generated_program": None,
        "llm_generated_university": None,
    }

    record = load_data.build_applicant_record(row, 4, llm_row)

    assert record[14] == "Computer Science"
    assert record[15] == "JHU"

@pytest.mark.db
def test_main_prints_counts(monkeypatch, capsys):
    def fake_load_data():
        return 2, 3

    monkeypatch.setattr(load_data, "load_data", fake_load_data)

    load_data.main()

    captured = capsys.readouterr()

    assert "Data loading completed." in captured.out
    assert "New rows inserted: 2" in captured.out
    assert "Existing rows skipped: 3" in captured.out
import pytest

from src.worker.etl import query_data


@pytest.mark.analysis
def test_get_connection_calls_psycopg(monkeypatch):
    def fake_connect(**kwargs):
        return "fake connection"

    monkeypatch.setattr(query_data.psycopg, "connect", fake_connect)

    result = query_data.get_connection()

    assert result == "fake connection"


@pytest.mark.analysis
def test_get_analysis_results(monkeypatch):
    class FakeCursor:
        def execute(self, sql):
            pass

        def fetchall(self):
            return [(1,)]

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    class FakeConnection:
        def cursor(self):
            return FakeCursor()

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    def fake_get_connection():
        return FakeConnection()

    monkeypatch.setattr(query_data, "get_connection", fake_get_connection)

    results = query_data.get_analysis_results()

    assert len(results) == 11
    assert results[0]["number"] == "Q1"
    assert results[0]["rows"] == [(1,)]


@pytest.mark.analysis
def test_query_data_main_prints_results(monkeypatch, capsys):
    fake_results = [
        {
            "number": "Q1",
            "question": "Test question?",
            "rows": [(123,)]
        }
    ]

    def fake_get_analysis_results():
        return fake_results

    monkeypatch.setattr(query_data, "get_analysis_results", fake_get_analysis_results)

    query_data.main()

    captured = capsys.readouterr()

    assert "Q1 Test question?" in captured.out
    assert "(123,)" in captured.out

@pytest.mark.db
def test_clamp_query_limit_handles_valid_and_invalid_values():
    assert query_data.clamp_query_limit(25) == 25
    assert query_data.clamp_query_limit(0) == query_data.MIN_QUERY_LIMIT
    assert query_data.clamp_query_limit(500) == query_data.MAX_QUERY_LIMIT
    assert query_data.clamp_query_limit("bad") == query_data.DEFAULT_QUERY_LIMIT
    assert query_data.clamp_query_limit(None) == query_data.DEFAULT_QUERY_LIMIT


@pytest.mark.db
def test_build_safe_select_query_uses_identifier_and_limit_params():
    statement, params = query_data.build_safe_select_query(
        "applicants",
        "university",
        10,
    )

    assert params == (10,)
    assert statement is not None


@pytest.mark.db
def test_build_safe_select_query_clamps_malicious_limit():
    statement, params = query_data.build_safe_select_query(
        "applicants",
        "university",
        "1; DROP TABLE applicants;",
    )

    assert statement is not None
    assert params == (query_data.DEFAULT_QUERY_LIMIT,)


@pytest.mark.db
def test_run_safe_select_query_uses_parameterized_execution():
    class FakeCursor:
        def __init__(self):
            self.executed_statement = None
            self.executed_params = None

        def execute(self, statement, params=None):
            self.executed_statement = statement
            self.executed_params = params

        def fetchall(self):
            return [("Johns Hopkins University",)]

    cursor = FakeCursor()

    rows = query_data.run_safe_select_query(
        cursor,
        "applicants",
        "university",
        5,
    )

    assert rows == [("Johns Hopkins University",)]
    assert cursor.executed_statement is not None
    assert cursor.executed_params == (5,)

@pytest.mark.analysis
def test_get_connection_uses_database_url(monkeypatch):
    captured = {}

    def fake_connect(connection_string):
        captured["connection_string"] = connection_string
        return "fake connection"

    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
    monkeypatch.setattr(query_data.psycopg, "connect", fake_connect)

    result = query_data.get_connection()

    assert result == "fake connection"
    assert captured["connection_string"] == "postgresql://user:pass@localhost/db"
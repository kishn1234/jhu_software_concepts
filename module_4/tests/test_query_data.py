import pytest

from src import query_data


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
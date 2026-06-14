import pytest

from src import query_data


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
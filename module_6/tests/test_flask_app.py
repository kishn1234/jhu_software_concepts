import subprocess
import pytest

from src.web.app.flask_app import create_app


@pytest.fixture
def client():
    app = create_app({"TESTING": True})

    with app.test_client() as client:
        yield client


@pytest.mark.web
def test_create_app():
    app = create_app()

    assert app is not None
    assert app.config is not None


@pytest.mark.web
def test_analysis_page_loads(client, monkeypatch):
    from src.web.app import flask_app

    def fake_get_analysis_results():
        return [
            {
                "number": "Q1",
                "question": "How many entries are Fall 2026 entries?",
                "rows": [(29608,)]
            }
        ]

    monkeypatch.setattr(flask_app, "get_analysis_results", fake_get_analysis_results)

    response = client.get("/analysis")

    assert response.status_code == 200
    assert b"Q1" in response.data
    assert b"Answer" in response.data


@pytest.mark.buttons
def test_update_analysis_redirects(client):
    response = client.post("/update-analysis")

    assert response.status_code == 302


@pytest.mark.buttons
def test_pull_data_redirects(client):
    response = client.post("/pull-data")

    assert response.status_code == 302


@pytest.mark.buttons
def test_pull_data_success(client, monkeypatch):
    def fake_run(*args, **kwargs):
        return None

    monkeypatch.setattr(subprocess, "run", fake_run)

    response = client.post("/pull-data")

    assert response.status_code == 302


@pytest.mark.buttons
def test_pull_data_failure(client, monkeypatch):
    def fake_run(*args, **kwargs):
        raise subprocess.CalledProcessError(1, "load_data.py")

    monkeypatch.setattr(subprocess, "run", fake_run)

    response = client.post("/pull-data")

    assert response.status_code == 302


@pytest.mark.buttons
def test_pull_data_already_running(client, monkeypatch):
    from src.web.app import flask_app

    monkeypatch.setitem(
    flask_app.DATA_REFRESH_STATE,
    "running",
    True
)

    response = client.post("/pull-data")

    assert response.status_code == 302


@pytest.mark.buttons
def test_update_analysis_during_data_refresh(client, monkeypatch):
    from src.web.app import flask_app

    monkeypatch.setitem(
    flask_app.DATA_REFRESH_STATE,
    "running",
    True
)

    response = client.post("/update-analysis")

    assert response.status_code == 302

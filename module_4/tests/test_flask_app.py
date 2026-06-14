import pytest

from src.flask_app import create_app


@pytest.fixture
def client():
    app = create_app({"TESTING": True})

    with app.test_client() as client:
        yield client


def test_create_app():
    app = create_app()

    assert app is not None
    assert app.config is not None


def test_analysis_page_loads(client):
    response = client.get("/analysis")

    assert response.status_code == 200

def test_update_analysis_redirects(client):
    response = client.post("/update-analysis")

    assert response.status_code == 302


def test_pull_data_redirects(client):
    response = client.post("/pull-data")

    assert response.status_code == 302
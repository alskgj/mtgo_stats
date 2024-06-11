import httpx
import pytest
from fastapi.testclient import TestClient

from rest import app
from service_layer.dependencies import get_repo


@pytest.fixture
def client(repo):
    client = TestClient(app)
    app.dependency_overrides[get_repo] = lambda: repo
    yield client


def test_stats(client: httpx.Client):
    response = client.get('/stats/decks', params={'max_days': 10000})
    print(response)
    assert response.status_code == 200
    assert 'Izzet Phoenix' in [deck['name'] for deck in response.json()]

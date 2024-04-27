from fastapi.testclient import TestClient
import pytest
from rest import app
import httpx


@pytest.fixture(scope='module')
def client():
    client = TestClient(app)
    # app.dependency_overrides[get_repo] = fake
    yield client


# todo - add mongorepo as a dependency, and then override it
def test_stats(client: httpx.Client):
    response = client.get('/stats')
    assert response.status_code == 200

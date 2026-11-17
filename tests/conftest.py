import os
from uuid import uuid4

import pytest
import requests

from models import User


BASE_URL = os.environ.get("EVENTS_API_BASE_URL", "http://localhost:5000").rstrip("/")


@pytest.fixture
def current_user():
    return User(username="Bernd")


@pytest.fixture
def api():
    with requests.Session() as session:
        def request(method, path, **kwargs):
            return session.request(method, f"{BASE_URL}{path}", timeout=5, **kwargs)

        yield request


@pytest.fixture
def credentials():
    return {"username": f"pytest-{uuid4().hex}", "password": "test-password-123"}


@pytest.fixture
def registered_credentials(api, credentials):
    response = api("POST", "/api/auth/register", json=credentials)
    assert response.status_code == 201, response.text
    return credentials


@pytest.fixture
def auth_headers(api, registered_credentials):
    response = api("POST", "/api/auth/login", json=registered_credentials)
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def event_payload():
    return {
        "title": "Pytest Meetup",
        "date": "2030-01-15T18:00:00",
        "location": "Room 101",
        "is_public": True,
    }

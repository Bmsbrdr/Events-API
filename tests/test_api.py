def test_health_endpoint_returns_healthy(api):
    response = api("GET", "/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_register_user_creates_new_user(api, credentials):
    response = api("POST", "/api/auth/register", json=credentials)

    assert response.status_code == 201, response.text
    assert response.json()["user"]["username"] == credentials["username"]


def test_login_returns_jwt_token(api, registered_credentials):
    response = api("POST", "/api/auth/login", json=registered_credentials)

    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    assert isinstance(token, str) and token


def test_create_public_event_succeeds_with_token(api, auth_headers, event_payload):
    response = api("POST", "/api/events", headers=auth_headers, json=event_payload)

    assert response.status_code == 201, response.text
    event = response.json()
    for field, value in event_payload.items():
        assert event[field] == value


def test_public_event_accepts_rsvp_without_token(api, auth_headers, event_payload):
    event = api("POST", "/api/events", headers=auth_headers, json=event_payload)
    assert event.status_code == 201, event.text
    event_id = event.json()["id"]

    response = api("POST", f"/api/rsvps/event/{event_id}", json={"attending": True})

    assert response.status_code == 201, response.text
    rsvp = response.json()
    assert rsvp["event_id"] == event_id
    assert rsvp["attending"] is True
    assert rsvp["user_id"] is None


def test_duplicate_registration_returns_400(api, registered_credentials):
    response = api("POST", "/api/auth/register", json=registered_credentials)

    assert response.status_code == 400, response.text
    assert response.json()["error"] == "Username already exists"


def test_create_event_without_token_returns_401(api, event_payload):
    response = api("POST", "/api/events", json=event_payload)

    assert response.status_code == 401, response.text


def test_private_event_rejects_rsvp_without_token(api, auth_headers, event_payload):
    event_payload["is_public"] = False
    event = api("POST", "/api/events", headers=auth_headers, json=event_payload)
    assert event.status_code == 201, event.text
    event_id = event.json()["id"]

    response = api("POST", f"/api/rsvps/event/{event_id}", json={"attending": True})

    assert response.status_code == 401, response.text
    assert response.json()["error"] == "Authentication required for this event"

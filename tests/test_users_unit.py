import json
from datetime import datetime
from types import SimpleNamespace

import pytest
from src.api.users import crud


def test_add_user(test_app, monkeypatch):
    def mock_get_user_by_email(email):
        return None

    def mock_add_user(username, email):
        return True

    monkeypatch.setattr(crud, "get_user_by_email", mock_get_user_by_email)
    monkeypatch.setattr(crud, "add_user", mock_add_user)

    client = test_app.test_client()
    data = json.dumps({"username": "michael", "email": "michael@testdriven.io"})
    resp = client.post("/users", data=data, content_type="application/json")
    data = resp.get_json()

    assert resp.status_code == 201
    assert data["message"] == "michael@testdriven.io was added!"


def test_add_user_invalid_json(test_app):
    client = test_app.test_client()
    data = json.dumps({})
    resp = client.post("/users", data=data, content_type="application/json")
    data = resp.get_json()

    assert resp.status_code == 400
    assert data["message"] == "Input payload validation failed"


def test_add_user_invalid_json_keys(test_app):
    client = test_app.test_client()
    data = json.dumps({"email": "michael@testdriven.io"})
    resp = client.post("/users", data=data, content_type="application/json")
    data = resp.get_json()

    assert resp.status_code == 400
    assert data["message"] == "Input payload validation failed"


def test_add_user_duplicate_email(test_app, monkeypatch):
    def mock_get_user_by_email(email):
        return True

    def mock_add_user(username, email):
        return True

    monkeypatch.setattr(crud, "get_user_by_email", mock_get_user_by_email)
    monkeypatch.setattr(crud, "add_user", mock_add_user)

    client = test_app.test_client()
    data = json.dumps({"username": "michael", "email": "michael@testdriven.io"})
    client.post("/users", data=data, content_type="application/json")
    resp = client.post("/users", data=data, content_type="application/json")
    data = resp.get_json()

    assert resp.status_code == 400
    assert data["message"] == "Sorry. That email already exists."


def test_single_user(test_app, monkeypatch):
    def mock_get_user_by_id(user_id):
        return {
            "id": 1,
            "username": "jeffrey",
            "email": "jeffrey@testdriven.io",
            "created_date": datetime.now(),
        }

    monkeypatch.setattr(crud, "get_user_by_id", mock_get_user_by_id)

    client = test_app.test_client()
    resp = client.get("/users/1")
    data = resp.get_json()

    assert resp.status_code == 200
    assert data["username"] == "jeffrey"
    assert data["email"] == "jeffrey@testdriven.io"


def test_single_user_incorrect_id(test_app, monkeypatch):
    def mock_get_user_by_id(user_id):
        return None

    monkeypatch.setattr(crud, "get_user_by_id", mock_get_user_by_id)

    client = test_app.test_client()
    resp = client.get("/users/1000")
    data = resp.get_json()

    assert resp.status_code == 404
    assert "User 1000 does not exist" in data["message"]


def test_all_users(test_app, monkeypatch):
    def mock_get_all_users():
        return [
            {
                "id": 1,
                "username": "jeffrey",
                "email": "jeffrey@testdriven.io",
                "created_date": datetime.now(),
            },
            {
                "id": 2,
                "username": "fletcher",
                "email": "fletcher@notreal.com",
                "created_date": datetime.now(),
            },
        ]

    monkeypatch.setattr(crud, "get_all_users", mock_get_all_users)

    client = test_app.test_client()
    resp = client.get("/users")
    data = resp.get_json()

    assert resp.status_code == 200
    assert len(data) == 2

    assert data[0]["username"] == "jeffrey"
    assert data[0]["email"] == "jeffrey@testdriven.io"

    assert data[1]["username"] == "fletcher"
    assert data[1]["email"] == "fletcher@notreal.com"


def test_remove_user(test_app, monkeypatch):
    def mock_get_user_by_id(user_id):
        d = SimpleNamespace(
            id=1, username="user-to-be-removed", email="remove-me@testdriven.io"
        )
        return d

    def mock_delete_user(user):
        return True

    monkeypatch.setattr(crud, "get_user_by_id", mock_get_user_by_id)
    monkeypatch.setattr(crud, "delete_user", mock_delete_user)

    client = test_app.test_client()
    resp = client.delete("users/1")
    data = resp.get_json()

    assert resp.status_code == 200
    assert data["message"] == "remove-me@testdriven.io was removed!"


def test_remove_user_incorrect_id(test_app, monkeypatch, add_user):
    def mock_get_user_by_id(user_id):
        return None

    monkeypatch.setattr(crud, "get_user_by_id", mock_get_user_by_id)

    client = test_app.test_client()
    resp = client.delete("users/999")
    data = resp.get_json()

    assert resp.status_code == 404
    assert "User 999 does not exist" in data["message"]


def test_update_user(test_app, monkeypatch):
    def mock_get_user_by_id(user_id):
        d = SimpleNamespace(
            id=1,
            username="me",
            email="me@testdriven.io",
        )
        return d

    def mock_update_user(user, username, email):
        return True

    def mock_get_user_by_email(email):
        return None

    monkeypatch.setattr(crud, "get_user_by_id", mock_get_user_by_id)
    monkeypatch.setattr(crud, "update_user", mock_update_user)
    monkeypatch.setattr(crud, "get_user_by_email", mock_get_user_by_email)

    client = test_app.test_client()
    resp = client.put(
        "/users/1",
        data=json.dumps({"username": "me", "email": "me@testdriven.io"}),
        content_type="application/json",
    )
    data = resp.get_json()

    assert resp.status_code == 200
    assert "1 was updated!" in data["message"]

    resp_two = client.get("/users/1")
    data = resp_two.get_json()

    assert resp_two.status_code == 200
    assert "me" in data["username"]
    assert "me@testdriven.io" in data["email"]


update_user_invalid_cases = [
    [1, {}, 400, "Input payload validation failed"],
    [1, {"email": "me@testdriven.io"}, 400, "Input payload validation failed"],
    [
        999,
        {"username": "me", "email": "me@testdriven.io"},
        404,
        "User 999 does not exist",
    ],
]


@pytest.mark.parametrize(
    "user_id, payload, status_code, message", update_user_invalid_cases
)
def test_update_user_invalid(
    test_app, monkeypatch, user_id, payload, status_code, message
):
    def mock_get_user_by_id(user_id):
        return None

    monkeypatch.setattr(crud, "get_user_by_id", mock_get_user_by_id)

    client = test_app.test_client()
    resp = client.put(
        f"/users/{user_id}", data=json.dumps(payload), content_type="application/json"
    )
    data = resp.get_json()

    assert resp.status_code == status_code
    assert message in data["message"]


def test_update_user_duplicate_email(test_app, monkeypatch):
    def mock_get_user_by_id(user_id):
        d = SimpleNamespace(
            id=1,
            username="me",
            email="me@testdriven.io",
        )
        return d

    def mock_update_user(user, username, email):
        return True

    def mock_get_user_by_email(email):
        return True

    monkeypatch.setattr(crud, "get_user_by_id", mock_get_user_by_id)
    monkeypatch.setattr(crud, "get_user_by_email", mock_get_user_by_email)
    monkeypatch.setattr(crud, "update_user", mock_update_user)

    client = test_app.test_client()
    resp = client.put(
        "/users/1",
        data=json.dumps({"username": "me", "email": "me@testdriven.io"}),
        content_type="application/json",
    )
    data = resp.get_json()

    assert resp.status_code == 400
    assert "Sorry. That email already exists." in data["message"]

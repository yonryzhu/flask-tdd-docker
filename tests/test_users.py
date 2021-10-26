import json

import pytest
from src.api.users.models import User


def test_add_user(test_app, test_database):
    client = test_app.test_client()
    data = json.dumps({"username": "michael", "email": "michael@testdriven.io"})
    resp = client.post("/users", data=data, content_type="application/json")
    data = resp.get_json()

    assert resp.status_code == 201
    assert data["message"] == "michael@testdriven.io was added!"


def test_add_user_invalid_json(test_app, test_database):
    client = test_app.test_client()
    data = json.dumps({})
    resp = client.post("/users", data=data, content_type="application/json")
    data = resp.get_json()

    assert resp.status_code == 400
    assert data["message"] == "Input payload validation failed"


def test_add_user_invalid_json_keys(test_app, test_database):
    client = test_app.test_client()
    data = json.dumps({"email": "michael@testdriven.io"})
    resp = client.post("/users", data=data, content_type="application/json")
    data = resp.get_json()

    assert resp.status_code == 400
    assert data["message"] == "Input payload validation failed"


def test_add_user_duplicate_email(test_app, test_database):
    client = test_app.test_client()
    data = json.dumps({"username": "michael", "email": "michael@testdriven.io"})
    client.post("/users", data=data, content_type="application/json")
    resp = client.post("/users", data=data, content_type="application/json")
    data = resp.get_json()

    assert resp.status_code == 400
    assert data["message"] == "Sorry. That email already exists."


def test_single_user(test_app, test_database, add_user):
    user = add_user("jeffrey", "jeffrey@testdriven.io")
    client = test_app.test_client()
    resp = client.get(f"/users/{user.id}")
    data = resp.get_json()

    assert resp.status_code == 200
    assert data["username"] == "jeffrey"
    assert data["email"] == "jeffrey@testdriven.io"


def test_single_user_incorrect_id(test_app, test_database):
    client = test_app.test_client()
    resp = client.get("/users/1000")
    data = resp.get_json()

    assert resp.status_code == 404
    assert "User 1000 does not exist" in data["message"]


def test_all_users(test_app, test_database, add_user):
    test_database.session.query(User).delete()
    add_user("jeffrey", "jeffrey@testdriven.io")
    add_user("fletcher", "fletcher@notreal.com")
    client = test_app.test_client()
    resp = client.get("/users")
    data = resp.get_json()

    assert resp.status_code == 200
    assert len(data) == 2

    assert data[0]["username"] == "jeffrey"
    assert data[0]["email"] == "jeffrey@testdriven.io"

    assert data[1]["username"] == "fletcher"
    assert data[1]["email"] == "fletcher@notreal.com"


def test_remove_user(test_app, test_database, add_user):
    test_database.session.query(User).delete()
    user = add_user("user-to-be-removed", "remove-me@testdriven.io")
    client = test_app.test_client()
    resp = client.get("/users")
    data = resp.get_json()

    assert resp.status_code == 200
    assert len(data) == 1

    resp_two = client.delete(f"users/{user.id}")
    data = resp_two.get_json()

    assert resp_two.status_code == 200
    assert data["message"] == "remove-me@testdriven.io was removed!"

    resp_three = client.get("/users")
    data = resp_three.get_json()

    assert resp_three.status_code == 200
    assert len(data) == 0


def test_remove_user_incorrect_id(test_app, test_database, add_user):
    client = test_app.test_client()
    resp = client.delete("users/999")
    data = resp.get_json()

    assert resp.status_code == 404
    assert "User 999 does not exist" in data["message"]


def test_update_user(test_app, test_database, add_user):
    user = add_user("user-to-be-updated", "update-me@testdriven/io")
    client = test_app.test_client()
    resp = client.put(
        f"/users/{user.id}",
        data=json.dumps({"username": "me", "email": "me@testdriven.io"}),
        content_type="application/json",
    )
    data = resp.get_json()

    assert resp.status_code == 200
    assert f"{user.id} was updated!" in data["message"]

    resp_two = client.get(f"/users/{user.id}")
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
    test_app, test_database, user_id, payload, status_code, message
):
    client = test_app.test_client()
    resp = client.put(
        f"/users/{user_id}", data=json.dumps(payload), content_type="application/json"
    )
    data = resp.get_json()

    assert resp.status_code == status_code
    assert message in data["message"]


def test_update_user_duplicate_email(test_app, test_database, add_user):
    add_user("hajek", "rob@hajek.org")
    user = add_user("rob", "rob@notreal.com")

    client = test_app.test_client()
    resp = client.put(
        f"/users/{user.id}",
        data=json.dumps({"username": "rob", "email": "rob@notreal.com"}),
        content_type="application/json",
    )
    data = resp.get_json()

    assert resp.status_code == 400
    assert "Sorry. That email already exists." in data["message"]

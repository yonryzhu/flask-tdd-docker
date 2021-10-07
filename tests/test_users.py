import json

from src.api.models import User


def test_add_user(test_app, test_database):
    client = test_app.test_client()
    data = json.dumps({"username": "michael", "email": "michael@testdriven.io"})
    resp = client.post("/users", data=data, content_type="application/json")
    result = resp.get_json()

    assert resp.status_code == 201
    assert result["message"] == "michael@testdriven.io was added!"


def test_add_user_invalid_json(test_app, test_database):
    client = test_app.test_client()
    data = json.dumps({})
    resp = client.post("/users", data=data, content_type="application/json")
    result = resp.get_json()

    assert resp.status_code == 400
    assert result["message"] == "Input payload validation failed"


def test_add_user_invalid_json_keys(test_app, test_database):
    client = test_app.test_client()
    data = json.dumps({"email": "michael@testdriven.io"})
    resp = client.post("/users", data=data, content_type="application/json")
    result = resp.get_json()

    assert resp.status_code == 400
    assert result["message"] == "Input payload validation failed"


def test_add_user_duplicate_email(test_app, test_database):
    client = test_app.test_client()
    data = json.dumps({"username": "michael", "email": "michael@testdriven.io"})
    client.post("/users", data=data, content_type="application/json")
    resp = client.post("/users", data=data, content_type="application/json")
    result = resp.get_json()

    assert resp.status_code == 400
    assert result["message"] == "Sorry. That email already exists."


def test_single_user(test_app, test_database, add_user):
    user = add_user("jeffrey", "jeffrey@testdriven.io")
    client = test_app.test_client()
    resp = client.get(f"/users/{user.id}")
    result = resp.get_json()

    assert resp.status_code == 200
    assert result["username"] == "jeffrey"
    assert result["email"] == "jeffrey@testdriven.io"


def test_single_user_incorrect_id(test_app, test_database):
    client = test_app.test_client()
    resp = client.get("/users/1000")
    result = resp.get_json()

    assert resp.status_code == 404
    assert "User 1000 does not exist" in result["message"]


def test_all_users(test_app, test_database, add_user):
    test_database.session.query(User).delete()
    add_user("jeffrey", "jeffrey@testdriven.io")
    add_user("fletcher", "fletcher@notreal.com")
    client = test_app.test_client()
    resp = client.get("/users")
    result = resp.get_json()

    assert resp.status_code == 200
    assert len(result) == 2

    assert result[0]["username"] == "jeffrey"
    assert result[0]["email"] == "jeffrey@testdriven.io"

    assert result[1]["username"] == "fletcher"
    assert result[1]["email"] == "fletcher@notreal.com"

def test_ping(test_app):
    client = test_app.test_client()
    resp = client.get("/ping")
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["message"] == "pong"
    assert data["status"] == "success"

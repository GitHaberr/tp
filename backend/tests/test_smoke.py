def test_health(client):
    assert client.get("/health").status_code == 200

def test_login_boss(client):
    r = client.post("/auth/login", json={"email": "boss@firma.ru", "password": "1234"})
    assert r.status_code == 200

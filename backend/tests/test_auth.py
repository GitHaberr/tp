def test_login_success(client):
    r = client.post("/auth/login", json={"email": "boss@firma.ru", "password": "1234"})
    assert r.status_code == 200
    assert "access_token" in r.json()

def test_login_wrong_password(client):
    r = client.post("/auth/login", json={"email": "boss@firma.ru", "password": "wrong"})
    assert r.status_code == 401
    assert r.json()["detail"] == "Неверный логин или пароль"

def test_login_unknown_email(client):
    r = client.post("/auth/login", json={"email": "no@firma.ru", "password": "1234"})
    assert r.status_code == 401
    assert r.json()["detail"] == "Неверный логин или пароль"

def test_me_without_token(client):
    r = client.get("/me")
    # В инструкции сказано: 401 или 403 "Not authenticated". Фиксируем факт.
    assert r.status_code in (401, 403) 

def test_me_with_broken_token(client):
    r = client.get("/me", headers={"Authorization": "Bearer broken_token_123"})
    assert r.status_code == 401

def test_me_with_valid_token(client, boss_token):
    r = client.get("/me", headers={"Authorization": f"Bearer {boss_token}"})
    assert r.status_code == 200
    assert r.json()["email"] == "boss@firma.ru"

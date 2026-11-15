import re

def test_forgot_unknown_email(client):
    r = client.post("/auth/forgot", json={"email": "no@firma.ru"})
    assert r.status_code == 404
    assert r.json()["detail"] == "Пользователь с таким email не найден"

def test_reset_short_password(client, capsys):
    client.post("/auth/forgot", json={"email": "petrov@firma.ru"})
    

    captured = capsys.readouterr()
    match = re.search(r"token=([a-zA-Z0-9\-_]+)", captured.out)
    assert match is not None, "Токен не найден в консоли"
    token = match.group(1)
    

    r = client.post("/auth/reset", json={"token": token, "new_password": "12"})
    assert r.status_code == 400
    assert r.json()["detail"] == "Пароль должен быть не короче 4 символов"

def test_reset_token_reuse(client, capsys):
    client.post("/auth/forgot", json={"email": "sidorova@firma.ru"})
    
    captured = capsys.readouterr()
    match = re.search(r"token=([a-zA-Z0-9\-_]+)", captured.out)
    token = match.group(1)
    

    r1 = client.post("/auth/reset", json={"token": token, "new_password": "newpass"})
    assert r1.status_code == 200
    

    r2 = client.post("/auth/reset", json={"token": token, "new_password": "newpass2"})
    assert r2.status_code == 400
    assert r2.json()["detail"] == "Ссылка недействительна или устарела"

def test_restore_password_back_to_1234(client, capsys):

    client.post("/auth/forgot", json={"email": "sidorova@firma.ru"})
    captured = capsys.readouterr()
    match = re.search(r"token=([a-zA-Z0-9\-_]+)", captured.out)
    token = match.group(1)
    
    r = client.post("/auth/reset", json={"token": token, "new_password": "1234"})
    assert r.status_code == 200

from datetime import date, timedelta

def test_create_empty_title(client, boss_token):
    r = client.post("/tasks", json={
        "title": "", "assignee_id": 2, "deadline": "2026-12-01"
    }, headers={"Authorization": f"Bearer {boss_token}"})
    assert r.status_code == 400
    assert r.json()["detail"] == "Введите название поручения"

def test_create_foreign_assignee(client, boss_token):
    r = client.post("/tasks", json={
        "title": "Задача", "assignee_id": 999, "deadline": "2026-12-01"
    }, headers={"Authorization": f"Bearer {boss_token}"})
    assert r.status_code == 400
    assert r.json()["detail"] == "Выберите исполнителя из своих подчинённых"

def test_create_by_employee_forbidden(client, petrov_token):
    r = client.post("/tasks", json={
        "title": "Задача", "assignee_id": 3, "deadline": "2026-12-01"
    }, headers={"Authorization": f"Bearer {petrov_token}"})
    assert r.status_code == 403
    assert r.json()["detail"] == "Создавать поручения может только начальник"

def test_create_deadline_yesterday(client, boss_token):
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    r = client.post("/tasks", json={
        "title": "Задача", "assignee_id": 2, "deadline": yesterday
    }, headers={"Authorization": f"Bearer {boss_token}"})
    assert r.status_code == 400
    assert r.json()["detail"] == "Срок не может быть раньше сегодняшней даты"

def test_create_deadline_today_ok(client, boss_token):
    today = date.today().isoformat()
    r = client.post("/tasks", json={
        "title": "Задача на сегодня", "assignee_id": 2, "deadline": today
    }, headers={"Authorization": f"Bearer {boss_token}"})
    assert r.status_code == 200

def test_create_deadline_tomorrow_ok(client, boss_token):
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    r = client.post("/tasks", json={
        "title": "Задача на завтра", "assignee_id": 2, "deadline": tomorrow
    }, headers={"Authorization": f"Bearer {boss_token}"})
    assert r.status_code == 200

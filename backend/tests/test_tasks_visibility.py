def test_boss_sees_own_tasks(client, boss_token, task_by_boss):
    r = client.get("/tasks", headers={"Authorization": f"Bearer {boss_token}"})
    assert r.status_code == 200
    assert len(r.json()) >= 1
    assert any(t["id"] == task_by_boss["id"] for t in r.json())

def test_employee_sees_own_tasks(client, petrov_token, task_by_boss):
    r = client.get("/tasks?scope=mine", headers={"Authorization": f"Bearer {petrov_token}"})
    assert r.status_code == 200
    assert any(t["id"] == task_by_boss["id"] for t in r.json())

def test_other_employee_does_not_see_task(client, sidorova_token, task_by_boss):
    r = client.get("/tasks", headers={"Authorization": f"Bearer {sidorova_token}"})
    assert r.status_code == 200
    assert not any(t["id"] == task_by_boss["id"] for t in r.json())

def test_unknown_scope(client, boss_token):
    r = client.get("/tasks?scope=bad_scope", headers={"Authorization": f"Bearer {boss_token}"})
    assert r.status_code == 400
    assert r.json()["detail"] == "Неизвестный раздел списка"

def test_unknown_status(client, boss_token):
    r = client.get("/tasks?status=bad_status", headers={"Authorization": f"Bearer {boss_token}"})
    assert r.status_code == 400
    assert r.json()["detail"] == "Неизвестный статус"

def test_filters_by_status(client, boss_token, task_by_boss):
    r = client.get("/tasks?status=in_progress", headers={"Authorization": f"Bearer {boss_token}"})
    assert r.status_code == 200
    assert len(r.json()) == 0

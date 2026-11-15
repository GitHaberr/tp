def test_card_author_ok(client, boss_token, task_by_boss):
    r = client.get(f"/tasks/{task_by_boss['id']}", headers={"Authorization": f"Bearer {boss_token}"})
    assert r.status_code == 200
    assert r.json()["id"] == task_by_boss["id"]

def test_card_assignee_ok(client, petrov_token, task_by_boss):
    r = client.get(f"/tasks/{task_by_boss['id']}", headers={"Authorization": f"Bearer {petrov_token}"})
    assert r.status_code == 200
    assert r.json()["id"] == task_by_boss["id"]

def test_card_stranger_forbidden(client, sidorova_token, task_by_boss):
    # Сидорова не автор и не исполнитель
    r = client.get(f"/tasks/{task_by_boss['id']}", headers={"Authorization": f"Bearer {sidorova_token}"})
    assert r.status_code == 403
    assert r.json()["detail"] == "Нет доступа к этому поручению"

def test_card_not_found(client, boss_token):
    r = client.get("/tasks/99999", headers={"Authorization": f"Bearer {boss_token}"})
    assert r.status_code == 404
    assert r.json()["detail"] == "Поручение не найдено"

def test_history_new_task_has_create_record(client, boss_token, task_by_boss):
    r = client.get(f"/tasks/{task_by_boss['id']}/history", headers={"Authorization": f"Bearer {boss_token}"})
    assert r.status_code == 200
    history = r.json()
    
    assert len(history) == 1
    # Теперь проверяем поле action_label, как оно приходит в реальном ответе
    assert history[0]["action"] == "created"
    assert history[0]["action_label"] == "Создал поручение"

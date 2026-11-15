def test_boss_sees_subordinates(client, boss_token):
    r = client.get("/users/subordinates", headers={"Authorization": f"Bearer {boss_token}"})
    assert r.status_code == 200
    subordinates = r.json()
    assert len(subordinates) == 2
    
    names = [u["full_name"] for u in subordinates]
    assert "Петров Алексей" in names
    assert "Сидорова Мария" in names

def test_employee_forbidden_to_see_subordinates(client, petrov_token):
    r = client.get("/users/subordinates", headers={"Authorization": f"Bearer {petrov_token}"})
    assert r.status_code == 403
    assert r.json()["detail"] == "Список подчинённых доступен только начальнику"

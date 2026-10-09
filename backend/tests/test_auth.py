import pytest


def test_employee_login(client, employee_token):
    
    assert employee_token is not None
    assert len(employee_token) > 0


def test_manager_login(client, manager_token):
    
    assert manager_token is not None
    assert len(manager_token) > 0


def test_superadmin_login(client, superadmin_token):
    assert superadmin_token is not None
    assert len(superadmin_token) > 0


def test_invalid_login(client):
    payload = {"email": "invalid@example.com", "password": "wrongpass", "role": "employee"}
    response = client.post("/api/login", json=payload)
    assert response.status_code in [400, 401, 404]

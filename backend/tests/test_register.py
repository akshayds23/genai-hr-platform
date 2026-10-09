import pytest
import random
import string


def generate_random_email():
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"test_{random_string}@example.com"


def generate_random_username():
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"user_{random_string}"


class TestEmployeeRegistration:

    def test_register_employee_basic(self, client):
        payload = {
            "email": generate_random_email(),
            "password": "TestPassword123!",
            "role": "employee"
        }
        
        response = client.post("/api/register", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "User created successfully"
        assert "user" in data
        assert data["user"]["email"] == payload["email"]
        assert data["user"]["employment_role"] == "employee"

    def test_register_employee_auto_username(self, client):
        payload = {
            "email": generate_random_email(),
            "password": "TestPassword123!",
            "role": "employee",
            "first_name": "Akshay",
            "last_name": "Kumar"
        }
        
        response = client.post("/api/register", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "User created successfully"
        assert data["user"]["username"] is not None
        assert len(data["user"]["username"]) > 0

    def test_register_employee_missing_email(self, client):
        payload = {
            "password": "TestPassword123!",
            "role": "employee"
        }
        
        response = client.post("/api/register", json=payload)
        assert response.status_code == 400
        assert "error" in response.json()

    def test_register_employee_missing_password(self, client):
        payload = {
            "email": generate_random_email(),
            "role": "employee"
        }
        
        response = client.post("/api/register", json=payload)
        assert response.status_code == 400
        assert "error" in response.json()

    def test_register_employee_duplicate_email(self, client):
        email = generate_random_email()
        payload = {
            "email": email,
            "password": "TestPassword123!",
            "role": "employee"
        }
        
        response1 = client.post("/api/register", json=payload)
        assert response1.status_code == 200
        
        response2 = client.post("/api/register", json=payload)
        assert response2.status_code == 400
        assert "already registered" in response2.json().get("error", "").lower()

    def test_register_employee_invalid_date_format(self, client):
        payload = {
            "email": generate_random_email(),
            "password": "TestPassword123!",
            "role": "employee",
            "hire_date": "15-01-2025"  # Invalid format
        }
        
        response = client.post("/api/register", json=payload)
        assert response.status_code == 400
        assert "error" in response.json()


class TestManagerRegistration:

    def test_register_manager_basic(self, client):
        payload = {
            "email": generate_random_email(),
            "password": "TestPassword123!",
            "role": "manager"
        }
        
        response = client.post("/api/register", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "User created successfully"
        assert "user" in data
        assert data["user"]["email"] == payload["email"]
        assert data["user"]["employment_role"] == "manager"

    def test_register_manager_auto_username(self, client):
        payload = {
            "email": generate_random_email(),
            "password": "TestPassword123!",
            "role": "manager",
            "first_name": "Bob",
            "last_name": "Boss"
        }
        
        response = client.post("/api/register", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "User created successfully"
        assert data["user"]["username"] is not None
        assert len(data["user"]["username"]) > 0


class TestRegistrationValidation:

    def test_register_invalid_role(self, client):
        payload = {
            "email": generate_random_email(),
            "password": "TestPassword123!",
            "role": "super_admin"  # Not allowed in registration
        }
        
        response = client.post("/api/register", json=payload)
        assert response.status_code == 400
        assert "invalid role" in response.json().get("error", "").lower()

    def test_register_no_payload(self, client):
        response = client.post("/api/register", json={})
        assert response.status_code == 400
        assert "error" in response.json()

    def test_register_empty_email(self, client):
        payload = {
            "email": "",
            "password": "TestPassword123!",
            "role": "employee"
        }
        
        response = client.post("/api/register", json=payload)
        assert response.status_code == 400
        assert "error" in response.json()

    def test_register_empty_password(self, client):
        payload = {
            "email": generate_random_email(),
            "password": "",
            "role": "employee"
        }
        
        response = client.post("/api/register", json=payload)
        assert response.status_code == 400
        assert "error" in response.json()

    def test_register_with_birth_date_only(self, client):
        payload = {
            "email": generate_random_email(),
            "password": "TestPassword123!",
            "role": "employee",
            "birth_date": "1995-08-10"
        }
        
        response = client.post("/api/register", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "User created successfully"

    def test_register_with_hire_date_only(self, client):
        payload = {
            "email": generate_random_email(),
            "password": "TestPassword123!",
            "role": "employee",
            "hire_date": "2025-01-01"
        }
        
        response = client.post("/api/register", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "User created successfully"


class TestRegistrationLoginFlow:

    def test_register_and_login_employee(self, client):
        email = generate_random_email()
        password = "TestPassword123!"
        
        register_payload = {
            "email": email,
            "password": password,
            "role": "employee"
        }
        
        register_response = client.post("/api/register", json=register_payload)
        assert register_response.status_code == 200
        
        login_payload = {
            "email": email,
            "password": password,
            "role": "employee"
        }
        
        login_response = client.post("/api/login", json=login_payload)
        assert login_response.status_code == 200
        
        login_data = login_response.json()
        assert "token" in login_data
        assert login_data["message"] == "Login successful"

    def test_register_and_login_manager(self, client):
        email = generate_random_email()
        password = "ManagerPass123!"
        
        register_payload = {
            "email": email,
            "password": password,
            "role": "manager"
        }
        
        register_response = client.post("/api/register", json=register_payload)
        assert register_response.status_code == 200
        
        login_payload = {
            "email": email,
            "password": password,
            "role": "manager"
        }
        
        login_response = client.post("/api/login", json=login_payload)
        assert login_response.status_code == 200
        
        login_data = login_response.json()
        assert "token" in login_data
        assert login_data["message"] == "Login successful"

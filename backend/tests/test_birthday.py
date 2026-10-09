import pytest


class TestBirthdayTracker:

    def test_get_birthday_tracker_success(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/birthday-tracker", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_get_birthday_tracker_unauthorized(self, client):
        response = client.get("/api/birthday-tracker")
        assert response.status_code in [302, 401, 403]

    def test_get_birthday_tracker_as_manager(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        response = client.get("/api/birthday-tracker", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_get_birthday_tracker_as_superadmin(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/birthday-tracker", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_birthday_tracker_structure(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/birthday-tracker", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, dict)

    def test_birthday_tracker_with_date_range(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/birthday-tracker?month=12", headers=headers)
        
        assert response.status_code == 200

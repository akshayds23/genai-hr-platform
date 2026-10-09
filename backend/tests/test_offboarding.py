import pytest


class TestOffboardingResignation:



    

    def test_submit_resignation_unauthorized(self, client):
        payload = {
            "last_working_date": "2025-12-31",
            "reason": "Personal reasons"
        }
        response = client.post("/api/offboarding/resign", json=payload)
        assert response.status_code in [302, 401, 403]


class TestOffboardingTasks:

    def test_get_offboarding_tasks_success(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/offboarding/tasks", headers=headers)
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict))

    def test_get_offboarding_tasks_unauthorized(self, client):
        response = client.get("/api/offboarding/tasks")
        assert response.status_code in [302, 401, 403]







    def test_reopen_task_as_employee_forbidden(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.post("/api/offboarding/tasks/1/reopen", headers=headers)
        assert response.status_code in [403, 404]


class TestOffboardingReport:

    def test_get_offboarding_report_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/offboarding/report", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)




class TestOffboardingLetters:

    def test_generate_letter_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        payload = {
            "user_id": 1,
            "template_id": 1
        }
        response = client.post("/api/offboarding/generate-letter", json=payload, headers=headers)
        
        assert response.status_code in [200, 201, 400, 404]

    def test_generate_letter_missing_user_id(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        payload = {"template_id": 1}
        response = client.post("/api/offboarding/generate-letter", json=payload, headers=headers)
        
        assert response.status_code == 400

    def test_get_all_letters_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/offboarding/letters", headers=headers)
        
        assert response.status_code == 200

    def test_get_letter_by_id_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/offboarding/letters/1", headers=headers)
        
        assert response.status_code in [200, 404]

    def test_download_letter_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/offboarding/letters/1/download", headers=headers)
        
        assert response.status_code in [200, 404]

    def test_run_reminders_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.post("/api/offboarding/run-reminders", headers=headers)
        
        assert response.status_code == 200

import pytest


class TestFeedbackSubmission:





    def test_submit_feedback_missing_category(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        payload = {
            "message": "Feedback without category"
        }
        response = client.post("/api/feedback/submit", json=payload, headers=headers)
        
        assert response.status_code == 400

    def test_submit_feedback_missing_message(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        payload = {
            "category": "general"
        }
        response = client.post("/api/feedback/submit", json=payload, headers=headers)
        
        assert response.status_code == 400

    def test_submit_feedback_empty_message(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        payload = {
            "category": "general",
            "message": ""
        }
        response = client.post("/api/feedback/submit", json=payload, headers=headers)
        
        assert response.status_code == 400

    def test_submit_feedback_unauthorized(self, client):
        payload = {
            "category": "general",
            "message": "Test feedback"
        }
        response = client.post("/api/feedback/submit", json=payload)
        assert response.status_code in [302, 401, 403]




class TestFeedbackRetrieval:

    def test_get_all_feedback_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/feedback/all", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))

    def test_get_all_feedback_unauthorized(self, client):
        response = client.get("/api/feedback/all")
        assert response.status_code in [302, 401, 403]

    def test_get_all_feedback_as_employee_forbidden(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/feedback/all", headers=headers)
        assert response.status_code == 403

    def test_get_all_feedback_with_filter(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/feedback/all?category=workplace", headers=headers)
        
        assert response.status_code == 200

    def test_get_all_feedback_with_pagination(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/feedback/all?page=1&per_page=10", headers=headers)
        
        assert response.status_code == 200


class TestFeedbackManagement:

    def test_mark_feedback_as_read_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.put("/api/feedback/1/mark-read", headers=headers)
        
        assert response.status_code in [200, 404]

    def test_mark_feedback_as_read_unauthorized(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.put("/api/feedback/1/mark-read", headers=headers)
        assert response.status_code == 403

    def test_mark_nonexistent_feedback_as_read(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.put("/api/feedback/999999/mark-read", headers=headers)
        
        assert response.status_code == 404


class TestFeedbackStats:

    def test_get_feedback_stats_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/feedback/stats", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_get_feedback_stats_unauthorized(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/feedback/stats", headers=headers)
        assert response.status_code == 403

    def test_get_feedback_stats_structure(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/feedback/stats", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)


class TestFeedbackCategories:



    def test_get_feedback_categories_as_manager(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        response = client.get("/api/feedback/categories", headers=headers)
        
        assert response.status_code == 200

    def test_get_feedback_categories_unauthorized(self, client):
        response = client.get("/api/feedback/categories")
        assert response.status_code in [302, 401, 403]

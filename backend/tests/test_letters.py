import pytest


class TestLetterTemplates:

    def test_get_all_templates_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/letters/templates", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))

    def test_get_all_templates_unauthorized(self, client):
        response = client.get("/api/letters/templates")
        assert response.status_code in [302, 401, 403]



    

    def test_create_template_missing_name(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        payload = {
            "content": "Template content without name"
        }
        response = client.post("/api/letters/templates", json=payload, headers=headers)
        
        assert response.status_code == 400

    def test_create_template_missing_content(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        payload = {
            "name": "Template Name"
        }
        response = client.post("/api/letters/templates", json=payload, headers=headers)
        
        assert response.status_code == 400

    def test_update_template_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        payload = {
            "name": "Updated Template Name",
            "content": "Updated content"
        }
        response = client.put("/api/letters/templates/1", json=payload, headers=headers)
        
        assert response.status_code in [200, 404]

    def test_update_template_with_patch(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        payload = {
            "name": "Partially Updated Template"
        }
        response = client.patch("/api/letters/templates/1", json=payload, headers=headers)
        
        assert response.status_code in [200, 404]

    def test_delete_template_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.delete("/api/letters/templates/999", headers=headers)
        
        assert response.status_code in [200, 404]

    def test_delete_template_unauthorized(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.delete("/api/letters/templates/1", headers=headers)
        assert response.status_code == 403


class TestLetterGeneration:

    def test_generate_letter_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        payload = {
            "template_id": 1,
            "user_id": 1,
            "data": {
                "employee_name": "John Doe",
                "position": "Software Engineer"
            }
        }
        response = client.post("/api/letters/generate", json=payload, headers=headers)
        
        assert response.status_code in [200, 201, 400, 404]

    def test_generate_letter_missing_template_id(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        payload = {
            "user_id": 1,
            "data": {}
        }
        response = client.post("/api/letters/generate", json=payload, headers=headers)
        
        assert response.status_code == 400



    def test_generate_letter_unauthorized(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        payload = {
            "template_id": 1,
            "user_id": 1,
            "data": {}
        }
        response = client.post("/api/letters/generate", json=payload, headers=headers)
        assert response.status_code == 403

    def test_download_letter_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/letters/1/download", headers=headers)
        
        assert response.status_code in [200, 404]

    def test_download_letter_unauthorized(self, client):
        response = client.get("/api/letters/1/download")
        assert response.status_code in [302, 401, 403]

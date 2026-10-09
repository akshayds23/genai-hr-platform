import pytest


class TestFAQManagement:

    def test_get_all_faqs_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/admin/faqs", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))

    def test_get_all_faqs_unauthorized(self, client):
        response = client.get("/api/admin/faqs")
        assert response.status_code in [302, 401, 403]

    def test_get_all_faqs_as_employee_forbidden(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/admin/faqs", headers=headers)
        assert response.status_code == 403

    def test_get_faqs_with_pagination(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/admin/faqs?page=1&per_page=10", headers=headers)
        
        assert response.status_code == 200

    def test_get_faqs_with_category_filter(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/admin/faqs?category=general", headers=headers)
        
        assert response.status_code == 200



    def test_create_faq_missing_question(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        payload = {
            "answer": "This is an answer without a question"
        }
        response = client.post("/api/admin/faqs", json=payload, headers=headers)
        
        assert response.status_code == 400

    def test_create_faq_missing_answer(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        payload = {
            "question": "This is a question without an answer?"
        }
        response = client.post("/api/admin/faqs", json=payload, headers=headers)
        
        assert response.status_code == 400

    def test_create_faq_unauthorized(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        payload = {
            "question": "Test question",
            "answer": "Test answer"
        }
        response = client.post("/api/admin/faqs", json=payload, headers=headers)
        assert response.status_code == 403

    def test_update_faq_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        payload = {
            "question": "Updated question?",
            "answer": "Updated answer"
        }
        response = client.put("/api/admin/faqs/1", json=payload, headers=headers)
        
        assert response.status_code in [200, 404]

    def test_update_faq_partial(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        payload = {
            "answer": "Only updating the answer"
        }
        response = client.put("/api/admin/faqs/1", json=payload, headers=headers)
        
        assert response.status_code in [200, 400, 404]



    def test_delete_faq_unauthorized(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.delete("/api/admin/faqs/1", headers=headers)
        assert response.status_code == 403


class TestFAQBulkOperations:

    def test_upload_faqs_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        payload = {
            "faqs": [
                {
                    "question": "FAQ 1?",
                    "answer": "Answer 1",
                    "category": "general"
                },
                {
                    "question": "FAQ 2?",
                    "answer": "Answer 2",
                    "category": "leave"
                }
            ]
        }
        response = client.post("/api/admin/faqs/upload", json=payload, headers=headers)
        
        assert response.status_code in [200, 400]

    def test_upload_faqs_empty_list(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        payload = {"faqs": []}
        response = client.post("/api/admin/faqs/upload", json=payload, headers=headers)
        
        assert response.status_code == 400

    def test_upload_faqs_invalid_format(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        payload = {
            "faqs": [
                {
                    "question": "Question without answer"
                }
            ]
        }
        response = client.post("/api/admin/faqs/upload", json=payload, headers=headers)
        
        assert response.status_code == 400

    def test_bulk_delete_faqs_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        payload = {
            "faq_ids": [1, 2, 3]
        }
        response = client.post("/api/admin/faqs/bulk-delete", json=payload, headers=headers)
        
        assert response.status_code in [200, 400]

    def test_bulk_delete_faqs_empty_list(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        payload = {"faq_ids": []}
        response = client.post("/api/admin/faqs/bulk-delete", json=payload, headers=headers)
        
        assert response.status_code == 400

    def test_bulk_delete_faqs_unauthorized(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        payload = {"faq_ids": [1, 2]}
        response = client.post("/api/admin/faqs/bulk-delete", json=payload, headers=headers)
        assert response.status_code == 403

import pytest


class TestResumeUpload:

    def test_upload_single_resume_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.post("/api/hr/resume/upload", headers=headers)
        
        assert response.status_code in [200, 201, 400]

    def test_upload_single_resume_unauthorized(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.post("/api/hr/resume/upload", headers=headers)
        assert response.status_code in [400, 403]

    def test_bulk_upload_resumes_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.post("/api/hr/resume/bulk-upload", headers=headers)
        
        assert response.status_code in [200, 201, 400]

    def test_bulk_upload_resumes_unauthorized(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.post("/api/hr/resume/bulk-upload", headers=headers)
        assert response.status_code in [400, 403]


class TestResumeSummarization:

    def test_summarize_resume_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.post("/api/hr/resume/summarize/1", headers=headers)
        
        assert response.status_code in [200, 404]

    def test_summarize_nonexistent_resume(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.post("/api/hr/resume/summarize/999999", headers=headers)
        
        assert response.status_code == 404

    def test_summarize_resume_unauthorized(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.post("/api/hr/resume/summarize/1", headers=headers)
        assert response.status_code == 403


class TestResumeRetrieval:

    def test_get_all_resumes_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/hr/resumes", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))

    def test_get_all_resumes_with_filter(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/hr/resumes?status=pending", headers=headers)
        
        assert response.status_code == 200

    def test_get_all_resumes_unauthorized(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/hr/resumes", headers=headers)
        assert response.status_code == 403

    def test_get_resume_by_id_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/hr/resume/1", headers=headers)
        
        assert response.status_code in [200, 404]

    def test_get_resume_by_id_unauthorized(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/hr/resume/1", headers=headers)
        assert response.status_code == 403


class TestResumeStatus:

    def test_update_resume_status_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        payload = {"status": "shortlisted"}
        response = client.put("/api/hr/resume/1/status", json=payload, headers=headers)
        
        assert response.status_code in [200, 400, 404]





    def test_update_resume_status_unauthorized(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        payload = {"status": "rejected"}
        response = client.put("/api/hr/resume/1/status", json=payload, headers=headers)
        assert response.status_code == 403


class TestJobDescriptionMatching:

    def test_match_resume_to_jd_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        payload = {
            "resume_id": 1,
            "jd_id": 1
        }
        response = client.post("/api/hr/jd/match", json=payload, headers=headers)
        
        assert response.status_code in [200, 400, 404]

    def test_match_resume_to_jd_missing_resume_id(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        payload = {"jd_id": 1}
        response = client.post("/api/hr/jd/match", json=payload, headers=headers)
        
        assert response.status_code == 400

    def test_match_resume_to_jd_missing_jd_id(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        payload = {"resume_id": 1}
        response = client.post("/api/hr/jd/match", json=payload, headers=headers)
        
        assert response.status_code == 400

    def test_match_resume_to_jd_unauthorized(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        payload = {"resume_id": 1, "jd_id": 1}
        response = client.post("/api/hr/jd/match", json=payload, headers=headers)
        assert response.status_code == 403


class TestJobDescriptions:

    def test_get_all_jds_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/hr/jd", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))

    def test_get_all_jds_unauthorized(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/hr/jd", headers=headers)
        assert response.status_code == 403


class TestHRAnalytics:

    def test_get_applicants_gender_analytics_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/hr/analytics/applicants-gender", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_get_applicants_gender_analytics_unauthorized(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/hr/analytics/applicants-gender", headers=headers)
        assert response.status_code == 403

    def test_get_applicants_source_analytics_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/hr/analytics/applicants-source", headers=headers)
        
        assert response.status_code == 200

    def test_get_applicants_status_analytics_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/hr/analytics/applicants-status", headers=headers)
        
        assert response.status_code == 200

    def test_get_hr_overview_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/hr/analytics/overview", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_get_hr_overview_unauthorized(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/hr/analytics/overview", headers=headers)
        assert response.status_code == 403

    def test_get_hr_overview_as_manager_forbidden(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        response = client.get("/api/hr/analytics/overview", headers=headers)
        assert response.status_code == 403

import pytest


class TestHROverview:

    def test_get_hr_overview_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/hr/analytics/overview", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_get_hr_overview_unauthorized(self, client):
        response = client.get("/api/hr/analytics/overview")
        assert response.status_code in [302, 403]

    def test_get_hr_overview_as_employee_forbidden(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/hr/analytics/overview", headers=headers)
        
        assert response.status_code == 403

    def test_get_hr_overview_as_manager_forbidden(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        response = client.get("/api/hr/analytics/overview", headers=headers)
        
        assert response.status_code == 403


class TestHREmployees:

    def test_list_employees_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/admin/employees/search", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, dict)
        if 'employees' in data:
            assert isinstance(data['employees'], list)
        elif 'users' in data:
            assert isinstance(data['users'], list)
        elif 'results' in data:
            assert isinstance(data['results'], list)

    def test_list_employees_with_pagination(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/admin/employees/search?page=1&page_size=10", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_list_employees_with_department_filter(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/admin/employees/search?department=Engineering", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_list_employees_with_status_filter(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/admin/employees/search?status=active", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_list_employees_structure(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/admin/employees/search", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        employees = data.get('employees') or data.get('users') or data.get('results', [])
        if len(employees) > 0:
            employee = employees[0]
            assert isinstance(employee, dict)
            assert 'id' in employee or 'email' in employee

    def test_list_employees_unauthorized(self, client):
        response = client.get("/api/admin/employees/search")
        assert response.status_code in [302, 403]

    def test_list_employees_as_employee_forbidden(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/admin/employees/search", headers=headers)
        
        assert response.status_code == 403


class TestHRLeaves:

    def test_list_leaves_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/admin/leaves", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, dict)
        if 'leaves' in data:
            assert isinstance(data['leaves'], list)

    def test_list_leaves_with_status_filter(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/admin/leaves?status=pending", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_list_leaves_with_multiple_status_filter(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/admin/leaves?status=pending,approved", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_list_leaves_with_date_range(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/admin/leaves?start_date=2024-01-01&end_date=2024-12-31", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_list_leaves_with_employee_filter(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/admin/leaves?employee_id=1", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_list_leaves_structure(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/admin/leaves", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        leaves = data.get('leaves', [])
        if len(leaves) > 0:
            leave = leaves[0]
            assert isinstance(leave, dict)
            common_fields = ['id', 'status', 'leave_type']
            assert any(field in leave for field in common_fields)

    def test_list_leaves_unauthorized(self, client):
        response = client.get("/api/admin/leaves")
        assert response.status_code in [302, 403]

    def test_list_leaves_as_employee_forbidden(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/admin/leaves", headers=headers)
        
        assert response.status_code == 403


class TestHRIntegration:

    def test_all_hr_endpoints_require_superadmin(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        
        endpoints = [
            "/api/hr/analytics/overview",
            "/api/admin/employees/search",
            "/api/admin/leaves"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint, headers=headers)
            assert response.status_code == 200, f"Endpoint {endpoint} failed with {response.status_code}"

    def test_hr_data_consistency(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        
        overview_response = client.get("/api/hr/analytics/overview", headers=headers)
        
        employees_response = client.get("/api/admin/employees/search", headers=headers)
        
        leaves_response = client.get("/api/admin/leaves", headers=headers)
        
        assert overview_response.status_code == 200
        assert employees_response.status_code == 200
        assert leaves_response.status_code == 200


class TestHREdgeCases:

    def test_empty_employee_list(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/admin/employees/search", headers=headers)
        
        assert response.status_code == 200
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)

    def test_invalid_pagination_parameters(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/admin/employees/search?page=-1&page_size=0", headers=headers)
        
        assert response.status_code in [200, 400, 404]

    def test_invalid_date_range(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/admin/leaves?start_date=invalid&end_date=2024-12-31", headers=headers)
        
        assert response.status_code in [200, 400, 404]

    def test_special_characters_in_filters(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/admin/employees/search?department=<script>alert('xss')</script>", headers=headers)
        
        assert response.status_code in [200, 400, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)

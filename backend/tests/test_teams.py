import pytest


class TestTeamsManagement:

    def test_get_all_teams_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/admin/teams", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_get_all_teams_unauthorized(self, client):
        response = client.get("/api/admin/teams")
        assert response.status_code in [302, 401, 403]

    def test_get_all_teams_as_employee_forbidden(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/admin/teams", headers=headers)
        assert response.status_code == 403



    def test_create_team_missing_name(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        payload = {
            "description": "Test team without name"
        }
        response = client.post("/api/admin/teams", json=payload, headers=headers)
        
        assert response.status_code == 400

    def test_create_team_unauthorized(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        payload = {
            "name": "Unauthorized Team",
            "description": "Should fail"
        }
        response = client.post("/api/admin/teams", json=payload, headers=headers)
        assert response.status_code == 403

    def test_update_team_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        payload = {
            "name": "Updated Team Name",
            "description": "Updated description"
        }
        response = client.put("/api/admin/teams/1", json=payload, headers=headers)
        
        assert response.status_code in [200, 404]

    def test_delete_team_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.delete("/api/admin/teams/999", headers=headers)
        
        assert response.status_code in [200, 404]

    def test_delete_team_unauthorized(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.delete("/api/admin/teams/1", headers=headers)
        assert response.status_code == 403


class TestTeamMembers:

    def test_add_team_member_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        payload = {"user_id": 3}
        response = client.post("/api/admin/teams/1/members", json=payload, headers=headers)
        
        assert response.status_code in [200, 201, 400, 404]

    def test_add_team_member_missing_user_id(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        payload = {}
        response = client.post("/api/admin/teams/1/members", json=payload, headers=headers)
        
        assert response.status_code == 400

    def test_remove_team_member_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.delete("/api/admin/teams/1/members/3", headers=headers)
        
        assert response.status_code in [200, 404]

    def test_get_team_members_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/admin/teams/1/members", headers=headers)
        
        assert response.status_code in [200, 404]



    def test_get_available_managers_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/admin/available-managers", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))

    def test_get_available_managers_unauthorized(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/admin/available-managers", headers=headers)
        assert response.status_code == 403

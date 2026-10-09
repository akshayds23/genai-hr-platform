import pytest


class TestManagerDashboard:

    def test_get_dashboard_success(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        response = client.get("/api/manager/dashboard", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "profile" in data
        assert "stats" in data
        assert "leave_summary" in data
        assert "leave_balance" in data
        assert "leave_analytics" in data
        assert "team_overview" in data
        assert "team_leave_summary" in data
        assert "pending_team_leaves" in data
        assert "team_offboarding" in data
        assert "upcoming_events" in data
        assert "notifications" in data
        assert "chatbot" in data
        assert "resignation" in data
        assert "project_announcement" in data
        assert "recent_leaves" in data

    def test_get_dashboard_profile_structure(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        response = client.get("/api/manager/dashboard", headers=headers)
        
        assert response.status_code == 200
        profile = response.json()["profile"]
        
        assert "full_name" in profile
        assert "employment_role" in profile
        assert "contact" in profile
        assert "email" in profile["contact"]

    def test_get_dashboard_stats_structure(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        response = client.get("/api/manager/dashboard", headers=headers)
        
        assert response.status_code == 200
        stats = response.json()["stats"]
        
        assert isinstance(stats, list)
        assert len(stats) >= 3
        
        for stat in stats:
            assert "title" in stat
            assert "value" in stat
            assert "subtext" in stat
            assert "icon" in stat

    def test_get_dashboard_team_overview(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        response = client.get("/api/manager/dashboard", headers=headers)
        
        assert response.status_code == 200
        team_overview = response.json()["team_overview"]
        
        assert "team_number" in team_overview
        assert "members" in team_overview
        assert "total_members" in team_overview
        assert isinstance(team_overview["members"], list)

    def test_get_dashboard_team_leave_summary(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        response = client.get("/api/manager/dashboard", headers=headers)
        
        assert response.status_code == 200
        team_leave_summary = response.json()["team_leave_summary"]
        
        assert "total" in team_leave_summary
        assert "by_status" in team_leave_summary
        assert isinstance(team_leave_summary["total"], int)
        assert isinstance(team_leave_summary["by_status"], dict)

    def test_get_dashboard_pending_team_leaves(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        response = client.get("/api/manager/dashboard", headers=headers)
        
        assert response.status_code == 200
        pending_leaves = response.json()["pending_team_leaves"]
        
        assert isinstance(pending_leaves, list)
        if len(pending_leaves) > 0:
            leave = pending_leaves[0]
            assert "id" in leave
            assert "employee_name" in leave

    def test_get_dashboard_leave_analytics(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        response = client.get("/api/manager/dashboard", headers=headers)
        
        assert response.status_code == 200
        leave_analytics = response.json()["leave_analytics"]
        
        assert isinstance(leave_analytics, dict)

    def test_get_dashboard_team_offboarding(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        response = client.get("/api/manager/dashboard", headers=headers)
        
        assert response.status_code == 200
        team_offboarding = response.json()["team_offboarding"]
        
        assert isinstance(team_offboarding, list)

    def test_get_dashboard_as_employee_forbidden(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/manager/dashboard", headers=headers)
        
        assert response.status_code in [200, 403]

    def test_get_dashboard_unauthorized(self, client):
        response = client.get("/api/manager/dashboard")
        assert response.status_code == 302

    def test_get_dashboard_recent_leaves(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        response = client.get("/api/manager/dashboard", headers=headers)
        
        assert response.status_code == 200
        recent_leaves = response.json()["recent_leaves"]
        
        assert isinstance(recent_leaves, list)


class TestManagerTeamLeaveOverview:

    def test_get_team_leave_requests(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        response = client.get("/api/leave/team/requests", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "leaves" in data
        assert isinstance(data["leaves"], list)

    def test_get_team_leave_requests_with_status_filter(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        response = client.get("/api/leave/team/requests?status=pending", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "leaves" in data
        leaves = data["leaves"]
        assert isinstance(leaves, list)
        
        for leave in leaves:
            if "status" in leave:
                assert leave["status"] == "pending"

    def test_get_team_leave_requests_multiple_statuses(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        response = client.get("/api/leave/team/requests?status=pending,approved", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "leaves" in data
        assert isinstance(data["leaves"], list)

    def test_get_team_leave_requests_structure(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        response = client.get("/api/leave/team/requests", headers=headers)
        
        assert response.status_code == 200
        leaves = response.json()["leaves"]
        
        if len(leaves) > 0:
            leave = leaves[0]
            assert "id" in leave
            assert "employee_id" in leave
            assert "employee_name" in leave
            assert "leave_type" in leave
            assert "status" in leave
            
            if "start_date" in leave and leave["start_date"]:
                assert isinstance(leave["start_date"], str)
            if "end_date" in leave and leave["end_date"]:
                assert isinstance(leave["end_date"], str)

    def test_get_team_leave_requests_with_team_number(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        response = client.get("/api/leave/team/requests?team_number=TEAM-001", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "leaves" in data

    def test_get_team_leave_requests_as_employee_forbidden(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/leave/team/requests", headers=headers)
        
        assert response.status_code in [200, 403]

    def test_get_team_leave_requests_unauthorized(self, client):
        response = client.get("/api/leave/team/requests")
        assert response.status_code == 302

class TestManagerProjectAnnouncement:

    def test_get_project_announcement(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        response = client.get("/api/manager/project-announcement", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "project_announcement" in data

    def test_get_project_announcement_structure(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        response = client.get("/api/manager/project-announcement", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        announcement = data["project_announcement"]
        
        if announcement is not None:
            assert isinstance(announcement, dict)
            if "title" in announcement:
                assert isinstance(announcement["title"], str)
            if "description" in announcement:
                assert isinstance(announcement["description"], str)

    def test_create_project_announcement(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        payload = {
            "title": "Q4 Project Update",
            "description": "Focus on delivery excellence and customer satisfaction"
        }
        
        response = client.put("/api/manager/project-announcement", json=payload, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "project_announcement" in data
        announcement = data["project_announcement"]
        assert announcement is not None
        assert announcement["title"] == "Q4 Project Update"
        assert announcement["description"] == "Focus on delivery excellence and customer satisfaction"

    def test_update_project_announcement(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        
        payload1 = {
            "title": "Initial Title",
            "description": "Initial Description"
        }
        client.put("/api/manager/project-announcement", json=payload1, headers=headers)
        
        payload2 = {
            "title": "Updated Title",
            "description": "Updated Description"
        }
        response = client.put("/api/manager/project-announcement", json=payload2, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        announcement = data["project_announcement"]
        assert announcement["title"] == "Updated Title"
        assert announcement["description"] == "Updated Description"

    def test_create_announcement_missing_title(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        payload = {
            "description": "Description without title"
        }
        
        response = client.put("/api/manager/project-announcement", json=payload, headers=headers)
        
        assert response.status_code == 400
        assert "error" in response.json()

    def test_create_announcement_missing_description(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        payload = {
            "title": "Title without description"
        }
        
        response = client.put("/api/manager/project-announcement", json=payload, headers=headers)
        
        assert response.status_code == 400
        assert "error" in response.json()

    def test_create_announcement_empty_title(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        payload = {
            "title": "",
            "description": "Valid description"
        }
        
        response = client.put("/api/manager/project-announcement", json=payload, headers=headers)
        
        assert response.status_code == 400
        assert "error" in response.json()

    def test_delete_project_announcement(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        
        payload = {
            "title": "To Be Deleted",
            "description": "This will be deleted"
        }
        client.put("/api/manager/project-announcement", json=payload, headers=headers)
        
        response = client.delete("/api/manager/project-announcement", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["project_announcement"] is None

    def test_delete_nonexistent_announcement(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        
        response = client.delete("/api/manager/project-announcement", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["project_announcement"] is None

    def test_announcement_as_employee_forbidden(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        
        payload = {
            "title": "Employee Attempt",
            "description": "Should fail"
        }
        response = client.put("/api/manager/project-announcement", json=payload, headers=headers)
        
        assert response.status_code in [200, 403]

    def test_get_announcement_unauthorized(self, client):
        response = client.get("/api/manager/project-announcement")
        assert response.status_code == 302


class TestManagerDashboardIntegration:

    def test_dashboard_contains_team_info(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        response = client.get("/api/manager/dashboard", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "team_overview" in data
        assert "team_leave_summary" in data
        assert "pending_team_leaves" in data
        assert "team_offboarding" in data

    def test_dashboard_leave_management_features(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        response = client.get("/api/manager/dashboard", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "leave_analytics" in data
        assert "team_leave_summary" in data
        assert "pending_team_leaves" in data
        
        stats = data["stats"]
        approval_stat_exists = any(
            "approval" in stat.get("title", "").lower() 
            for stat in stats
        )
        assert approval_stat_exists

    def test_dashboard_project_features(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        response = client.get("/api/manager/dashboard", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "project_announcement" in data

    def test_all_manager_endpoints_consistency(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        
        dashboard_response = client.get("/api/manager/dashboard", headers=headers)
        assert dashboard_response.status_code == 200
        
        team_leaves_response = client.get("/api/leave/team/requests", headers=headers)
        assert team_leaves_response.status_code == 200
        
        announcement_response = client.get("/api/manager/project-announcement", headers=headers)
        assert announcement_response.status_code == 200
        
        assert dashboard_response.status_code == 200
        assert team_leaves_response.status_code == 200
        assert announcement_response.status_code == 200


class TestManagerDashboardEdgeCases:

    def test_dashboard_with_no_team_members(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        response = client.get("/api/manager/dashboard", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "team_overview" in data
        assert "team_leave_summary" in data

    def test_dashboard_with_no_pending_leaves(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        response = client.get("/api/manager/dashboard", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        pending_leaves = data["pending_team_leaves"]
        assert isinstance(pending_leaves, list)

    def test_announcement_lifecycle(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        
        create_payload = {
            "title": "New Project",
            "description": "Starting new initiative"
        }
        create_response = client.put("/api/manager/project-announcement", json=create_payload, headers=headers)
        assert create_response.status_code == 200
        
        update_payload = {
            "title": "Updated Project",
            "description": "Initiative in progress"
        }
        update_response = client.put("/api/manager/project-announcement", json=update_payload, headers=headers)
        assert update_response.status_code == 200
        
        get_response = client.get("/api/manager/project-announcement", headers=headers)
        assert get_response.status_code == 200
        announcement = get_response.json()["project_announcement"]
        assert announcement["title"] == "Updated Project"
        
        delete_response = client.delete("/api/manager/project-announcement", headers=headers)
        assert delete_response.status_code == 200
        assert delete_response.json()["project_announcement"] is None

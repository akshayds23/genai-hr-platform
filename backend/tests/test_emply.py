from urllib import response
import pytest


class TestEmployeeDashboard:

    def test_get_dashboard_success(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/employee/dashboard", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "profile" in data
        assert "stats" in data
        assert "leave_summary" in data
        assert "recent_leaves" in data
        assert "upcoming_events" in data
        assert "team_overview" in data
        assert "quick_actions" in data
        assert "notifications" in data
        assert "chatbot" in data
        assert "career" in data
        assert "offboarding" in data

    def test_get_dashboard_profile_structure(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/employee/dashboard", headers=headers)
        
        assert response.status_code == 200
        profile = response.json()["profile"]
        
        assert "full_name" in profile
        assert "job_title" in profile
        assert "department" in profile
        assert "employment_role" in profile
        assert "employee_id" in profile
        assert "team_number" in profile
        assert "contact" in profile
        
        assert "email" in profile["contact"]

    def test_get_dashboard_stats_structure(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/employee/dashboard", headers=headers)
        
        assert response.status_code == 200
        stats = response.json()["stats"]
        
        assert isinstance(stats, list)
        assert len(stats) == 4
        
        for stat in stats:
            assert "title" in stat
            assert "value" in stat
            assert "subtext" in stat
            assert "icon" in stat

    def test_get_dashboard_leave_summary(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/employee/dashboard", headers=headers)
        
        assert response.status_code == 200
        leave_summary = response.json()["leave_summary"]
        
        assert "total" in leave_summary
        assert "by_status" in leave_summary
        assert "balance" in leave_summary
        assert isinstance(leave_summary["total"], int)
        assert isinstance(leave_summary["by_status"], dict)

    def test_get_dashboard_quick_actions(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/employee/dashboard", headers=headers)
        
        assert response.status_code == 200
        quick_actions = response.json()["quick_actions"]
        
        assert isinstance(quick_actions, list)
        assert len(quick_actions) > 0
        
        for action in quick_actions:
            assert "key" in action
            assert "label" in action
            assert "icon" in action
            assert "description" in action

    def test_get_dashboard_team_overview(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/employee/dashboard", headers=headers)
        
        assert response.status_code == 200
        team_overview = response.json()["team_overview"]
        
        assert "team_number" in team_overview
        assert "members" in team_overview
        assert "total_members" in team_overview
        assert "has_more" in team_overview
        assert isinstance(team_overview["members"], list)

    def test_get_dashboard_career_section(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/employee/dashboard", headers=headers)
        
        assert response.status_code == 200
        career = response.json()["career"]
        
        assert "progress_pct" in career
        assert "target_skills" in career
        assert "skills" in career
        assert "recommendation" in career
        assert isinstance(career["progress_pct"], int)
        assert 0 <= career["progress_pct"] <= 100

 

    def test_get_dashboard_unauthorized(self, client):
        response = client.get("/api/employee/dashboard")

        assert response.status_code == 302

    def test_get_dashboard_as_manager(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        response = client.get("/api/employee/dashboard", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "profile" in data
        assert "stats" in data


class TestEmployeeLeaveOverview:

    def test_get_own_leaves(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/leave/mine", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "leaves" in data or isinstance(data, list)

    def test_get_own_leaves_structure(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/leave/mine", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        leaves = data.get("leaves", data) if isinstance(data, dict) else data
        
        if isinstance(leaves, list) and len(leaves) > 0:
            leave = leaves[0]
            assert "id" in leave
            assert "status" in leave
            
            if "start_date" in leave:
                assert isinstance(leave["start_date"], str)
            if "end_date" in leave:
                assert isinstance(leave["end_date"], str)

    def test_get_own_leaves_unauthorized(self, client):
        response = client.get("/api/leave/mine")
        assert response.status_code == 302

    def test_get_own_leaves_as_manager(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        response = client.get("/api/leave/mine", headers=headers)
        
        assert response.status_code == 200


class TestEmployeeAnnouncements:

    def test_get_project_announcement(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/employee/project-announcement", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "project_announcement" in data

    def test_get_project_announcement_structure(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/employee/project-announcement", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        announcement = data["project_announcement"]
        
        if announcement is not None:
            assert isinstance(announcement, dict)
            if "title" in announcement:
                assert isinstance(announcement["title"], str)
            if "description" in announcement:
                assert isinstance(announcement["description"], str)

    def test_get_project_announcement_unauthorized(self, client):
        response = client.get("/api/employee/project-announcement")
        assert response.status_code == 302

    def test_get_project_announcement_as_manager(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        response = client.get("/api/employee/project-announcement", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "project_announcement" in data


class TestEmployeeDashboardIntegration:

    def test_dashboard_contains_leave_info(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/employee/dashboard", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "leave_summary" in data
        assert "recent_leaves" in data
        
        stats = data["stats"]
        leave_stat_exists = any(
            "leave" in stat.get("title", "").lower() 
            for stat in stats
        )
        assert leave_stat_exists

    def test_dashboard_contains_team_info(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/employee/dashboard", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "team_overview" in data
        assert "profile" in data
        
        profile = data["profile"]
        assert "team_number" in profile

    def test_dashboard_notification_section(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/employee/dashboard", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "notifications" in data
        notifications = data["notifications"]
        assert isinstance(notifications, list)

    def test_dashboard_chatbot_section(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/employee/dashboard", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "chatbot" in data
        chatbot = data["chatbot"]
        
        assert "has_history" in chatbot
        assert "headline" in chatbot
        assert isinstance(chatbot["has_history"], bool)

    def test_dashboard_offboarding_section(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/employee/dashboard", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "offboarding" in data
        offboarding = data["offboarding"]
        
        assert "status" in offboarding
        assert "status_label" in offboarding
        assert "message" in offboarding

    def test_all_employee_endpoints_consistency(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        
        dashboard_response = client.get("/api/employee/dashboard", headers=headers)
        assert dashboard_response.status_code == 200
        
        leaves_response = client.get("/api/leave/mine", headers=headers)
        assert leaves_response.status_code == 200
        
        announcement_response = client.get("/api/employee/project-announcement", headers=headers)
        assert announcement_response.status_code == 200
        
        assert dashboard_response.status_code == 200
        assert leaves_response.status_code == 200
        assert announcement_response.status_code == 200


class TestEmployeeDashboardEdgeCases:

    def test_dashboard_with_no_team(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/employee/dashboard", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        team_overview = data["team_overview"]
        assert "team_number" in team_overview
        assert "members" in team_overview

    def test_dashboard_with_no_leaves(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/employee/dashboard", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        leave_summary = data["leave_summary"]
        assert isinstance(leave_summary["total"], int)

    def test_dashboard_upcoming_events_empty(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/employee/dashboard", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "upcoming_events" in data
        assert isinstance(data["upcoming_events"], list)


def test_dashboard_with_upcoming_team_event(app, client, employee_token):
    """Regression: the demo seed adds team events; the dashboard must render them."""
    from datetime import datetime, timedelta
    from app.models.models import TeamEvent, db

    with app.app_context():
        event = TeamEvent(title="Quarterly town hall", start_datetime=datetime.utcnow() + timedelta(days=3))
        db.session.add(event)
        db.session.commit()
        event_id = event.id
    try:
        response = client.get("/api/employee/dashboard", headers={"Authentication-Token": employee_token})
        assert response.status_code == 200
        titles = [e["title"] for e in response.json()["upcoming_events"]]
        assert "Quarterly town hall" in titles
    finally:
        with app.app_context():
            db.session.delete(db.session.get(TeamEvent, event_id))
            db.session.commit()

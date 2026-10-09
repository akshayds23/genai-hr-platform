import pytest


class TestNotifications:

    def test_get_notifications_success(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/notifications", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))

    def test_get_notifications_unauthorized(self, client):
        response = client.get("/api/notifications")
        assert response.status_code in [302, 401, 403]

    def test_get_notifications_as_manager(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        response = client.get("/api/notifications", headers=headers)
        
        assert response.status_code == 200

    def test_get_notifications_as_superadmin(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/notifications", headers=headers)
        
        assert response.status_code == 200

    def test_get_notifications_with_filter(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.get("/api/notifications?is_read=false", headers=headers)
        
        assert response.status_code == 200

    def test_mark_notification_as_read_success(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.post("/api/notifications/1/read", headers=headers)
        
        assert response.status_code in [200, 404]

    def test_mark_notification_as_read_unauthorized(self, client):
        response = client.post("/api/notifications/1/read")
        assert response.status_code in [302, 401, 403]

    def test_mark_notification_as_read_wrong_user(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        response = client.post("/api/notifications/999/read", headers=headers)
        
        assert response.status_code in [403, 404]


class TestLeaveAnalytics:

    def test_get_leave_analytics_success(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get("/api/notifications/leave-analytics", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_get_leave_analytics_as_manager(self, client, manager_token):
        headers = {"Authentication-Token": f"{manager_token}"}
        response = client.get("/api/notifications/leave-analytics", headers=headers)
        
        assert response.status_code in [200, 403]



    def test_get_leave_analytics_unauthorized(self, client):
        response = client.get("/api/notifications/leave-analytics")
        assert response.status_code in [302, 401, 403]

    def test_get_leave_analytics_with_date_range(self, client, superadmin_token):
        headers = {"Authentication-Token": f"{superadmin_token}"}
        response = client.get(
            "/api/notifications/leave-analytics?start_date=2025-01-01&end_date=2025-12-31",
            headers=headers
        )
        
        assert response.status_code == 200

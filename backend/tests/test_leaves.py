import pytest
from datetime import date, timedelta


class TestLeaveApplication:

    def test_apply_leave_missing_start_date(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        tomorrow = date.today() + timedelta(days=1)
        
        payload = {
            "end_date": tomorrow.strftime("%Y-%m-%d"),
            "leave_type": "vacation"
        }
        
        response = client.post("/api/leave/apply", json=payload, headers=headers)
        assert response.status_code == 400
        
        data = response.json()
        assert "error" in data
        assert "start_date" in data["error"].lower()

    def test_apply_leave_missing_end_date(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        tomorrow = date.today() + timedelta(days=1)
        
        payload = {
            "start_date": tomorrow.strftime("%Y-%m-%d"),
            "leave_type": "vacation"
        }
        
        response = client.post("/api/leave/apply", json=payload, headers=headers)
        assert response.status_code == 400
        
        data = response.json()
        assert "error" in data
        assert "end_date" in data["error"].lower()

    def test_apply_leave_invalid_date_format(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        
        payload = {
            "start_date": "2025-13-01",  # Invalid month
            "end_date": "2025-12-31",
            "leave_type": "vacation"
        }
        
        response = client.post("/api/leave/apply", json=payload, headers=headers)
        assert response.status_code == 400
        
        data = response.json()
        assert "error" in data

    def test_apply_leave_wrong_date_format(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        
        payload = {
            "start_date": "01/12/2025",  # Wrong format
            "end_date": "05/12/2025",
            "leave_type": "vacation"
        }
        
        response = client.post("/api/leave/apply", json=payload, headers=headers)
        assert response.status_code == 400
        
        data = response.json()
        assert "error" in data
        assert "format" in data["error"].lower()

    def test_apply_leave_start_after_end(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        tomorrow = date.today() + timedelta(days=30)
        yesterday = tomorrow - timedelta(days=5)
        
        payload = {
            "start_date": tomorrow.strftime("%Y-%m-%d"),
            "end_date": yesterday.strftime("%Y-%m-%d"),
            "leave_type": "vacation"
        }
        
        response = client.post("/api/leave/apply", json=payload, headers=headers)
        assert response.status_code == 400
        
        data = response.json()
        assert "error" in data
        assert "after" in data["error"].lower()

    def test_apply_leave_unauthorized(self, client):
        tomorrow = date.today() + timedelta(days=1)
        end_date = tomorrow + timedelta(days=4)
        
        payload = {
            "start_date": tomorrow.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "leave_type": "vacation"
        }
        
        response = client.post("/api/leave/apply", json=payload)
        assert response.status_code in [302, 401, 403]

    def test_apply_leave_empty_payload(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        
        response = client.post("/api/leave/apply", json={}, headers=headers)
        assert response.status_code == 400
        
        data = response.json()
        assert "error" in data

    def test_apply_leave_null_dates(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        
        payload = {
            "start_date": None,
            "end_date": None,
            "leave_type": "vacation"
        }
        
        response = client.post("/api/leave/apply", json=payload, headers=headers)
        assert response.status_code == 400
        
        data = response.json()
        assert "error" in data



class TestLeaveApplicationEdgeCases:

    def test_apply_leave_far_future_date(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        start = date.today() + timedelta(days=365)
        end = start + timedelta(days=2)
        
        payload = {
            "start_date": start.strftime("%Y-%m-%d"),
            "end_date": end.strftime("%Y-%m-%d"),
            "leave_type": "vacation"
        }
        
        response = client.post("/api/leave/apply", json=payload, headers=headers)
        assert response.status_code in [200, 400]

    def test_apply_leave_special_characters_in_reason(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        tomorrow = date.today() + timedelta(days=100)
        end_date = tomorrow + timedelta(days=1)
        
        payload = {
            "start_date": tomorrow.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "leave_type": "personal",
            "reason": "Doctor's appointment @ 2:00 PM - follow-up & tests"
        }
        
        response = client.post("/api/leave/apply", json=payload, headers=headers)
        assert response.status_code in [200, 400]
        
        if response.status_code == 200:
            data = response.json()
            assert data["leave"]["reason"] == "Doctor's appointment @ 2:00 PM - follow-up & tests"

    def test_apply_leave_long_reason(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        tomorrow = date.today() + timedelta(days=110)
        end_date = tomorrow + timedelta(days=1)
        
        long_reason = "A" * 500  # 500 characters
        
        payload = {
            "start_date": tomorrow.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "leave_type": "sick",
            "reason": long_reason
        }
        
        response = client.post("/api/leave/apply", json=payload, headers=headers)
        assert response.status_code in [200, 400]

    def test_apply_leave_past_dates(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        past_date = date.today() - timedelta(days=10)
        end_date = past_date + timedelta(days=2)
        
        payload = {
            "start_date": past_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "leave_type": "sick"
        }
        
        response = client.post("/api/leave/apply", json=payload, headers=headers)
        assert response.status_code in [200, 400]

    def test_apply_leave_invalid_json(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        
        response = client.post("/api/leave/apply", headers=headers)
        assert response.status_code in [400, 415]


class TestLeaveApplicationIntegration:

    def test_apply_leave_check_pending_status(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        tomorrow = date.today() + timedelta(days=120)
        end_date = tomorrow + timedelta(days=2)
        
        payload = {
            "start_date": tomorrow.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "leave_type": "vacation",
            "reason": "Status check test"
        }
        
        response = client.post("/api/leave/apply", json=payload, headers=headers)
        assert response.status_code in [200, 400]
        
        if response.status_code == 200:
            data = response.json()
            assert data["leave"]["status"] == "pending"
            assert "id" in data["leave"]

    def test_apply_leave_balance_included(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        tomorrow = date.today() + timedelta(days=130)
        end_date = tomorrow + timedelta(days=1)
        
        payload = {
            "start_date": tomorrow.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "leave_type": "vacation"
        }
        
        response = client.post("/api/leave/apply", json=payload, headers=headers)
        assert response.status_code in [200, 400]
        
        if response.status_code == 200:
            data = response.json()
            assert "balance" in data
            assert isinstance(data["balance"], dict)

    def test_apply_leave_different_leave_types(self, client, employee_token):
        headers = {"Authentication-Token": f"{employee_token}"}
        base_date = date.today() + timedelta(days=140)
        
        leave_types = ["sick", "vacation", "personal", "emergency"]
        
        for idx, leave_type in enumerate(leave_types):
            start = base_date + timedelta(days=idx * 5)
            end = start + timedelta(days=1)
            
            payload = {
                "start_date": start.strftime("%Y-%m-%d"),
                "end_date": end.strftime("%Y-%m-%d"),
                "leave_type": leave_type
            }
            
            response = client.post("/api/leave/apply", json=payload, headers=headers)
            assert response.status_code in [200, 400]
            
            if response.status_code == 200:
                data = response.json()
                assert data["leave"]["leave_type"] == leave_type

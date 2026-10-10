def test_ai_daily_limit_reached(app, client, employee_token, monkeypatch):
    """Test that exceeding the daily AI limit returns 429 with expected message."""
    monkeypatch.setenv("DEMO_MODE", "true")
    monkeypatch.setenv("AI_DAILY_LIMIT", "2")

    headers = {"Authentication-Token": employee_token}

    # Calls 1 and 2 should succeed
    for i in range(2):
        resp = client.post(
            "/api/genai/careerpath",
            json={
                "current_role": "Junior Developer",
                "target_role": "Senior Developer",
                "strengths": f"Python {i}",
            },
            headers=headers,
        )
        assert resp.status_code == 200, f"Call {i+1} failed with status {resp.status_code}"

    # Call 3 (exceeding limit 2) should return 429
    resp = client.post(
        "/api/genai/careerpath",
        json={
            "current_role": "Junior Developer",
            "target_role": "Senior Developer",
            "strengths": "Python 3",
        },
        headers=headers,
    )
    assert resp.status_code == 429
    data = resp.get_json()
    assert "Daily AI limit reached for this demo account. Try again tomorrow." in data["error"]


def test_demo_mode_blocks_destructive_actions(app, client, hr_token, monkeypatch):
    """Test that destructive operations are blocked with 403 in demo mode."""
    monkeypatch.setenv("DEMO_MODE", "true")
    headers = {"Authentication-Token": hr_token}

    # Try to delete user
    resp = client.delete("/api/super-admin/users/1", headers=headers)
    assert resp.status_code == 403
    assert "disabled in demo mode" in resp.get_json()["error"]

    # Try to delete FAQ
    resp = client.delete("/api/admin/faqs/1", headers=headers)
    assert resp.status_code == 403
    assert "disabled in demo mode" in resp.get_json()["error"]


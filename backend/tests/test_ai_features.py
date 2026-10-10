import json
import pytest
from app.services.ai import AIUnavailableError
from app.models.models import db, JobDescription, CandidateResume, HRKnowledge


def test_chatbot_success(client, employee_token, app):
    with app.app_context():
        if not HRKnowledge.query.filter_by(question="What is the company leave policy?").first():
            faq = HRKnowledge(
                question="What is the company leave policy?",
                answer="Employees get 20 days of annual leave and 10 days of sick leave.",
                source="handbook",
            )
            db.session.add(faq)
            db.session.commit()

    headers = {"Authentication-Token": employee_token}
    payload = {"message": "What is the company leave policy?"}
    response = client.post("/api/genai/chat", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "status" in data
    assert "conversation_id" in data
    assert isinstance(data["response"], str)
    assert len(data["response"]) > 0


def test_chatbot_ai_unavailable(client, employee_token, app, monkeypatch):
    with app.app_context():
        if not HRKnowledge.query.filter_by(question="What is the company leave policy?").first():
            faq = HRKnowledge(
                question="What is the company leave policy?",
                answer="Employees get 20 days of annual leave and 10 days of sick leave.",
                source="handbook",
            )
            db.session.add(faq)
            db.session.commit()

    def raise_unavailable(*args, **kwargs):
        raise AIUnavailableError("Service unavailable")

    monkeypatch.setattr("app.services.ai.generate_text", raise_unavailable)
    monkeypatch.setattr("app.services.ai.embed_texts", raise_unavailable)

    headers = {"Authentication-Token": employee_token}
    payload = {"message": "What is the company leave policy?"}
    response = client.post("/api/genai/chat", json=payload, headers=headers)

    assert response.status_code == 503
    data = response.json()
    assert "error" in data
    assert "AI service is not available" in data["error"]


def test_jd_generate_success(client, hr_token):
    headers = {"Authentication-Token": hr_token}
    payload = {
        "title": "Senior Python Backend Engineer",
        "department": "Engineering",
        "experience": "5+ years",
        "skills": "Python, Flask, PostgreSQL",
    }
    response = client.post("/api/genai/jd/generate", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert "description" in data
    assert "requirements" in data
    assert "skills_required" in data
    assert "experience_required" in data
    assert isinstance(data["description"], str)


def test_jd_generate_ai_unavailable(client, hr_token, monkeypatch):
    def raise_unavailable(*args, **kwargs):
        raise AIUnavailableError("Service unavailable")

    monkeypatch.setattr("app.services.ai.generate_text", raise_unavailable)

    headers = {"Authentication-Token": hr_token}
    payload = {"title": "Data Scientist"}
    response = client.post("/api/genai/jd/generate", json=payload, headers=headers)

    assert response.status_code == 503
    data = response.json()
    assert "error" in data
    assert "AI service is not available" in data["error"]


def test_careerpath_success(client, employee_token):
    headers = {"Authentication-Token": employee_token}
    payload = {
        "current_role": "Junior Backend Developer",
        "target_role": "Lead Architect",
        "strengths": "Python, Problem solving",
        "focus_areas": "System design, Cloud",
        "learning_style": "Hands-on projects",
        "timeline": "2 years",
    }
    response = client.post("/api/genai/careerpath", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert "recommendation" in data
    assert "pdf_endpoint" in data
    assert isinstance(data["recommendation"], str)


def test_careerpath_ai_unavailable(client, employee_token, monkeypatch):
    def raise_unavailable(*args, **kwargs):
        raise AIUnavailableError("Service unavailable")

    monkeypatch.setattr("app.services.ai.generate_text", raise_unavailable)

    headers = {"Authentication-Token": employee_token}
    payload = {
        "current_role": "Junior Developer",
        "target_role": "Senior Developer",
    }
    response = client.post("/api/genai/careerpath", json=payload, headers=headers)

    assert response.status_code == 503
    data = response.json()
    assert "error" in data
    assert "AI service is not available" in data["error"]


def test_resume_match_success(client, hr_token, app):
    with app.app_context():
        jd = JobDescription(
            title="Full Stack Engineer",
            department="Engineering",
            requirements=json.dumps(["Python", "Vue"]),
            skills_required=json.dumps(["Python", "JavaScript"]),
            experience_required=3.0,
            description="Build scalable web applications",
        )
        cand = CandidateResume(
            filename="candidate.pdf",
            name="Jane Doe",
            email="jane.doe@example.com",
            skills=json.dumps(["Python", "Vue", "SQL"]),
            experience=json.dumps([{"role": "Developer", "duration": "3 years"}]),
            education=json.dumps([{"degree": "B.S. CS"}]),
            total_experience=3.0,
            current_role="Developer",
            summary="Experienced web engineer",
            resume_text="Experienced full stack web developer with 3 years building web apps in Python and Vue.",
        )
        db.session.add(jd)
        db.session.add(cand)
        db.session.commit()
        jd_id = jd.id

    headers = {"Authentication-Token": hr_token}
    payload = {"job_description_id": jd_id}
    response = client.post("/api/hr/jd/match", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert "job_description" in data
    assert "message" in data


def test_resume_match_ai_unavailable(client, hr_token, app, monkeypatch):
    with app.app_context():
        jd = JobDescription(
            title="DevOps Engineer",
            department="Infrastructure",
            requirements=json.dumps(["Docker", "K8s"]),
            skills_required=json.dumps(["Docker"]),
            experience_required=2.0,
            description="Manage cloud deployments",
        )
        cand = CandidateResume(
            filename="candidate2.pdf",
            name="Bob Builder",
            email="bob.builder@example.com",
            skills=json.dumps(["Docker"]),
            experience=json.dumps([]),
            education=json.dumps([]),
            total_experience=2.0,
            current_role="DevOps",
            summary="DevOps specialist",
            resume_text="DevOps engineer skilled in Docker and Kubernetes cloud deployments.",
        )
        db.session.add(jd)
        db.session.add(cand)
        db.session.commit()
        jd_id = jd.id

    def raise_unavailable(*args, **kwargs):
        raise AIUnavailableError("Service unavailable")

    monkeypatch.setattr("app.services.ai.generate_text", raise_unavailable)

    headers = {"Authentication-Token": hr_token}
    payload = {"job_description_id": jd_id}
    response = client.post("/api/hr/jd/match", json=payload, headers=headers)

    assert response.status_code == 503
    data = response.json()
    assert "error" in data
    assert "AI service is not available" in data["error"]

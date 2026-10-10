import json
import os
import sys
from pathlib import Path
from urllib.parse import urlencode, urlparse
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestResponseWrapper:
    def __init__(self, response):
        self._resp = response

    @property
    def status_code(self):
        return self._resp.status_code

    @property
    def text(self):
        return self._resp.get_data(as_text=True)

    @property
    def content(self):
        return self._resp.get_data()

    @property
    def headers(self):
        return self._resp.headers

    def json(self):
        return self._resp.get_json()

    def raise_for_status(self):
        if 400 <= self._resp.status_code < 600:
            raise Exception(f"HTTP Error {self._resp.status_code}: {self.text}")
        return self

    def __getattr__(self, name):
        return getattr(self._resp, name)


class TestClientWrapper:
    def __init__(self, flask_client):
        self._client = flask_client

    def _fix_url(self, url):
        if url.startswith("http://") or url.startswith("https://"):
            parsed = urlparse(url)
            url = parsed.path
            if parsed.query:
                url += "?" + parsed.query
        return url

    def get(self, url, **kwargs):
        url = self._fix_url(url)
        params = kwargs.pop("params", None)
        if params:
            query = urlencode(params)
            url = f"{url}?{query}" if "?" not in url else f"{url}&{query}"
        return TestResponseWrapper(self._client.get(url, **kwargs))

    def post(self, url, **kwargs):
        url = self._fix_url(url)
        return TestResponseWrapper(self._client.post(url, **kwargs))

    def put(self, url, **kwargs):
        url = self._fix_url(url)
        return TestResponseWrapper(self._client.put(url, **kwargs))

    def patch(self, url, **kwargs):
        url = self._fix_url(url)
        return TestResponseWrapper(self._client.patch(url, **kwargs))

    def delete(self, url, **kwargs):
        url = self._fix_url(url)
        return TestResponseWrapper(self._client.delete(url, **kwargs))

    def __getattr__(self, name):
        return getattr(self._client, name)


@pytest.fixture(scope="session")
def app(tmp_path_factory):
    db_file = tmp_path_factory.mktemp("db") / "test.db"
    os.environ["TESTING"] = "true"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_file}"
    os.environ["ENABLE_SCHEDULER"] = "false"
    os.environ["SECRET_KEY"] = "test-secret-key-32-chars-minimum!!"
    os.environ["SECURITY_PASSWORD_SALT"] = "test-security-salt"
    os.environ["HR_EMAIL"] = "hr@example.com"
    os.environ["HR_PASSWORD"] = "hr123"
    os.environ["HR_USERNAME"] = "hr"
    os.environ["MANAGER_EMAIL"] = "manager@example.com"
    os.environ["MANAGER_PASSWORD"] = "manager123"
    os.environ["MANAGER_USERNAME"] = "manager"
    os.environ["EMPLOYEE_EMAIL"] = "employee@example.com"
    os.environ["EMPLOYEE_PASSWORD"] = "employee123"
    os.environ["EMPLOYEE_USERNAME"] = "employee"
    os.environ["SECURITY_REGISTERABLE"] = "true"

    from app import create_app
    test_app = create_app()
    test_app.config["TESTING"] = True
    test_app.config["SECURITY_REGISTERABLE"] = True
    yield test_app


@pytest.fixture(scope="session")
def base_url():
    return ""


@pytest.fixture(scope="function")
def client(app):
    with app.test_client() as c:
        yield TestClientWrapper(c)


@pytest.fixture(scope="session")
def employee_token(app):
    with app.test_client() as c:
        resp = c.post("/api/login", json={"email": "employee@example.com", "password": "employee123", "role": "employee"})
        return resp.get_json()["token"]


@pytest.fixture(scope="session")
def manager_token(app):
    with app.test_client() as c:
        resp = c.post("/api/login", json={"email": "manager@example.com", "password": "manager123", "role": "manager"})
        return resp.get_json()["token"]


@pytest.fixture(scope="session")
def superadmin_token(app):
    with app.test_client() as c:
        resp = c.post("/api/login", json={"email": "hr@example.com", "password": "hr123", "role": "hr"})
        return resp.get_json()["token"]


@pytest.fixture(scope="session")
def hr_token(superadmin_token):
    return superadmin_token


@pytest.fixture(autouse=True)
def mock_ai(monkeypatch):
    def fake_generate_text(prompt: str, *, system=None, json_output=False, max_tokens=1024) -> str:
        prompt_lower = prompt.lower()
        if json_output or "return only valid json" in prompt_lower or "return only a json object" in prompt_lower:
            if "match_score" in prompt_lower:
                return '{"match_score": 88.0, "reasoning": "Strong match with relevant experience."}'
            if "requirements" in prompt_lower and "extract structured data" in prompt_lower:
                return json.dumps({
                    "requirements": ["3+ years Python experience", "Bachelor degree in CS or equivalent"],
                    "skills_required": ["Python", "Flask", "PostgreSQL"],
                    "experience_required": 3,
                })
            if "skills" in prompt_lower or "total_experience" in prompt_lower:
                return json.dumps({
                    "name": "Alex Smith",
                    "email": "alex.smith@example.com",
                    "phone": "555-0100",
                    "skills": ["Python", "Flask", "SQL"],
                    "experience": [
                        {
                            "company": "Acme Inc",
                            "role": "Software Engineer",
                            "duration": "3 years",
                            "responsibilities": "Building web APIs and backend services"
                        }
                    ],
                    "education": [
                        {
                            "institution": "Tech Institute",
                            "degree": "B.Tech",
                            "field": "CS",
                            "year": "2020"
                        }
                    ],
                    "summary": "Experienced software engineer with backend focus.",
                    "total_experience": 3.0,
                    "current_role": "Software Engineer",
                    "current_company": "Acme Inc",
                    "gender": "Other"
                })
            return '{"status": "ok"}'

        if "career" in prompt_lower or "target role" in prompt_lower:
            return "**Summary:**\nCareer growth path is achievable.\n\n**Recommended Actions:**\n1. Deepen domain knowledge.\n2. Gain leadership skills."
        if "rate how similar" in prompt_lower:
            return "0.85"
        if "classify the employee question" in prompt_lower:
            return "HR"
        return "This is a deterministic AI-generated response for tests."

    def fake_embed_texts(texts: list[str]) -> list[list[float]]:
        return [[0.05 * (i % 7) for i in range(768)] for _ in texts]

    monkeypatch.setattr("app.services.ai.generate_text", fake_generate_text)
    monkeypatch.setattr("app.services.ai.embed_texts", fake_embed_texts)

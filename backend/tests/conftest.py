import pytest
import httpx
import yaml
from pathlib import Path


@pytest.fixture(scope="session")
def base_url():
    """
    Extract the base URL from openapi.yaml servers section.
    """
    openapi_path = Path(__file__).parents[1] / "app" / "static" / "openapi.yaml"
    with open(openapi_path, "r") as f:
        spec = yaml.safe_load(f)

    servers = spec.get("servers", [])
    if not servers:
        raise ValueError("No 'servers' defined in openapi.yaml")

    # Use the first server URL
    return servers[0]["url"].rstrip("/")


@pytest.fixture(scope="function")
def client(base_url):
    
    with httpx.Client(base_url=base_url, timeout=30.0, follow_redirects=False) as c:
        yield c


@pytest.fixture(scope="session")
def employee_token(base_url):
    
    with httpx.Client(base_url=base_url, timeout=30.0) as temp_client:
        payload = {"email": "employee@example.com", "password": "employee123", "role": "employee"}
        response = temp_client.post("/api/login", json=payload)
        response.raise_for_status()
        return response.json().get("token")


@pytest.fixture(scope="session")
def manager_token(base_url):
    
    with httpx.Client(base_url=base_url, timeout=30.0) as temp_client:
        payload = {"email": "manager@example.com", "password": "manager123", "role": "manager"}
        response = temp_client.post("/api/login", json=payload)
        response.raise_for_status()
        return response.json().get("token")


@pytest.fixture(scope="session")
def superadmin_token(base_url):
    
    with httpx.Client(base_url=base_url, timeout=30.0) as temp_client:
        payload = {"email": "hr@example.com", "password": "hr123", "role": "hr"}
        response = temp_client.post("/api/login", json=payload)
        response.raise_for_status()
        return response.json().get("token")

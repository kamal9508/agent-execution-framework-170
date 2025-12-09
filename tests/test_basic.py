"""Basic tests for the FastAPI application."""
from fastapi.testclient import TestClient

from app.main import app


def test_root_returns_welcome_message():
    """Test root endpoint returns welcome message."""
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Agent Workflow Engine API"
    assert "version" in data
    assert "docs" in data


def test_health_check():
    """Test health check endpoint."""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data






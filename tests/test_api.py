import pytest
from fastapi.testclient import TestClient
from app import app
import json

client = TestClient(app)

@pytest.fixture
def mock_llm(mocker):
    """Mocks the LLM services in similarity_check."""
    mocker.patch("app.get_embedding", return_value=[0.1] * 1536)
    structured_analysis = (
        "STATUS: PASSED\n"
        "SUMMARY: The prompt is excellent.\n"
        "WORKFLOW: 1. Do something.\n2. Do something else."
    )
    mocker.patch("app.analyze_requirements", return_value=structured_analysis)

def test_get_info():
    response = client.get("/api/info")
    assert response.status_code == 200
    data = response.json()
    assert data['version'] == "0.6.3"
    assert data['status'] == "healthy"

def test_get_projects(db):
    db.create_project("p1", "req1")
    response = client.get("/api/projects")
    assert response.status_code == 200
    data = response.json()
    assert any(p['name'] == "p1" for p in data)

def test_create_project_and_env(db):
    # Create Project (Verify mandatory requirements)
    response = client.post("/api/projects", json={"name": "new_project"})
    assert response.status_code == 422 # Pydantic validation error for missing field
    
    response = client.post("/api/projects", json={"name": "new_project", "requirements": "r1", "project_focus": "f1"})
    assert response.status_code == 200
    
    # Verify focus persistence
    response = client.get("/api/projects")
    project = next(p for p in response.json() if p['name'] == "new_project")
    assert project['project_focus'] == "f1"

    # Test PATCH
    response = client.patch("/api/projects/new_project", json={"project_focus": "f2"})
    assert response.status_code == 200
    response = client.get("/api/projects")
    project = next(p for p in response.json() if p['name'] == "new_project")
    assert project['project_focus'] == "f2"
    
    # Create Env
    response = client.post("/api/environments", json={"project_name": "new_project", "name": "staging"})
    assert response.status_code == 200

def test_check_prompt_flow(db, mock_llm):
    db.create_project("p1", "some requirements")
    db.create_environment("p1", "dev")
    
    payload = {
        "project": "p1",
        "environment": "dev",
        "prompt": "Test prompt",
        "threshold": 0.85,
        "url": "http://localhost:1234/v1"
    }
    
    # First check (should auto-save since mock_llm ensures no similarity)
    response = client.post("/api/check", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data['was_saved'] is True
    assert "STATUS: PASSED" in data['requirement_analysis']
    assert "SUMMARY:" in data['requirement_analysis']
    assert "WORKFLOW:" in data['requirement_analysis']

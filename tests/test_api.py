import pytest
from fastapi.testclient import TestClient
from app import app
import json

client = TestClient(app)

@pytest.fixture
def mock_llm(mocker):
    """Mocks the LLM services in similarity_check."""
    mocker.patch("app.get_embedding", return_value=[0.1] * 1536)
    mocker.patch("app.analyze_requirements", return_value="NO ISSUES")

def test_get_projects(db):
    db.create_project("p1", "req1")
    response = client.get("/api/projects")
    assert response.status_code == 200
    data = response.json()
    assert any(p['name'] == "p1" for p in data)

def test_create_project_and_env(db):
    # Create Project
    response = client.post("/api/projects", json={"name": "new_project", "requirements": "r1"})
    assert response.status_code == 200
    
    # Create Env
    response = client.post("/api/environments", json={"project_name": "new_project", "name": "staging"})
    assert response.status_code == 200
    
    # Verify via GET
    response = client.get("/api/projects/new_project/environments")
    assert response.status_code == 200
    assert any(e['name'] == "staging" for e in response.json())

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
    assert data['requirement_analysis'] == "NO ISSUES"

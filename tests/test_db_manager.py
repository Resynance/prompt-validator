import pytest
from db_manager import DBManager

def test_project_lifecycle(db):
    # Create project
    project_id = db.create_project("test_project", "Test Requirements", "Test Focus")
    assert project_id is not None
    
    # Get project
    project = db.get_project("test_project")
    assert project['name'] == "test_project"
    assert project['requirements'] == "Test Requirements"
    assert project['project_focus'] == "Test Focus"
    
    # Update project via create_project (UPSERT)
    db.create_project("test_project", "Updated Requirements", "Updated Focus")
    project = db.get_project("test_project")
    assert project['requirements'] == "Updated Requirements"
    assert project['project_focus'] == "Updated Focus"

    # Test partial update via update_project
    db.update_project("test_project", project_focus="Partial Focus")
    project = db.get_project("test_project")
    assert project['requirements'] == "Updated Requirements"
    assert project['project_focus'] == "Partial Focus"
    
    # Delete project
    db.delete_project("test_project")
    project = db.get_project("test_project")
    assert project is None

def test_environment_lifecycle(db):
    db.create_project("p1", "req1")
    
    # Create environment
    env_id = db.create_environment("p1", "staging")
    assert env_id is not None
    
    # Get environment
    env = db.get_environment_by_name("p1", "staging")
    assert env['name'] == "staging"
    assert env['project_name'] == "p1"
    
    # Delete environment
    db.delete_environment("p1", "staging")
    env = db.get_environment_by_name("p1", "staging")
    assert env is None

def test_prompt_persistence_and_similarity(db):
    db.create_project("p1", "req1")
    env_id = db.create_environment("p1", "prod")
    
    # Save a prompt (using distinct embedding)
    embedding = [0.1] * 1536
    embedding[0] = 0.9  # Make it distinct
    prompt_id = db.save_prompt(env_id, "Hello world", embedding)
    assert prompt_id is not None
    
    # Find similar
    similar = db.find_similar(env_id, embedding, threshold=0.99)
    assert len(similar) == 1
    
    # Find different (orthogonal or very distant)
    diff_embedding = [0.0] * 1536
    diff_embedding[100] = 1.0
    similar = db.find_similar(env_id, diff_embedding, threshold=0.8)
    assert len(similar) == 0

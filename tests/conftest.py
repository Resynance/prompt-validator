import pytest
import os
from db_manager import DBManager

@pytest.fixture(scope="session")
def db_config():
    """Provides configuration for the test database."""
    return {
        "dbname": "prompt_similarity_test",
        "user": "promptmanager",
        "password": "password",
        "host": "localhost",
        "port": "5432"
    }

@pytest.fixture(scope="function")
def db(db_config, mocker):
    """Provides a fresh database connection and patches the app to use it."""
    # Ensure the app uses a fresh DB connection for each check
    # We patch the DBManager class so that whenever the app instantiates it, it gets our test config.
    mocker.patch("app.DBManager", side_effect=lambda *args, **kwargs: DBManager(**db_config))
    
    manager = DBManager(**db_config)
    manager._ensure_schema()
    yield manager
    
    # Cleanup after each test
    with manager.conn.cursor() as cur:
        cur.execute("TRUNCATE projects, environments, prompts CASCADE;")
    manager.close()

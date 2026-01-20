# Testing Guide

The Prompt Similarity Detector uses `pytest` for automated testing. The suite covers both the database management layer and the REST API endpoints.

## 1. Test Architecture

The testing suite is designed to be fast, isolated, and reliable:
*   **Database Isolation**: All tests run against a separate `prompt_similarity_test` database to ensure production data is never modified.
*   **Mocking**: External calls to LM Studio are mocked using `pytest-mock`. This allows tests to run without an active LM Studio server or internet connection.
*   **Transactional Cleanliness**: After each test, the test database is truncated to ensure a fresh state for the next test.

## 2. Prerequisites

Before running tests, ensure you have created the test database:

```bash
psql -U promptmanager -d postgres -c "CREATE DATABASE prompt_similarity_test OWNER promptmanager;"
psql -U promptmanager -d prompt_similarity_test -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

## 3. Running Tests

To run the entire suite from the project root:

```bash
source venv/bin/activate
export PYTHONPATH=$PYTHONPATH:.
pytest tests/
```

### Useful Pytest Flags
*   `pytest -v`: Verbose output.
*   `pytest -s`: Show print statements during testing.
*   `pytest tests/test_api.py`: Run only API integration tests.

## 4. Test Files

*   **`tests/conftest.py`**: Contains shared fixtures, including the database connection manager and app patching logic.
*   **`tests/test_db_manager.py`**: Unit tests for the `DBManager` class (CRUD for projects, environments, and prompts).
*   **`tests/test_api.py`**: Integration tests for FastAPI endpoints using `TestClient`.

## 5. Adding New Tests

When adding API tests, use the `mock_llm` fixture defined in `tests/test_api.py` to avoid making real requests to LM Studio:

```python
def test_new_feature(db, mock_llm):
    # Your test logic here
    pass
```

# Tests Documentation

This directory contains the test suite for the Mergington High School Activities API.

## Overview

The tests are organized into two main modules:

- **`test_api_endpoints.py`** — Integration tests for all API endpoints (GET /, GET /activities, POST signup, DELETE unregister)
- **`test_app_logic.py`** — Unit tests for core business logic (participant management, validation, capacity tracking)

Supporting files:
- **`conftest.py`** — Pytest configuration and reusable fixtures
- **`__init__.py`** — Package marker

## Running Tests

### Run all tests
```bash
pytest
```

### Run tests with verbose output
```bash
pytest -v
```

### Run tests with coverage report
```bash
pytest --cov=src --cov-report=html
```

### Run a specific test file
```bash
pytest tests/test_api_endpoints.py
pytest tests/test_app_logic.py
```

### Run tests matching a pattern
```bash
pytest -k "signup"
pytest -k "unregister"
```

## Test Structure

### Integration Tests (`test_api_endpoints.py`)

Tests are organized by endpoint:

- **`TestRootEndpoint`** — GET / redirect behavior
- **`TestGetActivitiesEndpoint`** — GET /activities response structure and data
- **`TestSignupEndpoint`** — POST /activities/{activity_name}/signup success and error cases
- **`TestUnregisterEndpoint`** — DELETE /activities/{activity_name}/unregister success and error cases
- **`TestEndToEndScenarios`** — Complete user workflows

### Unit Tests (`test_app_logic.py`)

Tests focus on business logic:

- **`TestActivityLookup`** — Activity validation and lookup
- **`TestParticipantManagement`** — Adding/removing participants
- **`TestDuplicateSignupPrevention`** — Duplicate signup detection
- **`TestActivityCapacity`** — Capacity and availability calculations
- **`TestEmailValidation`** — Email format handling
- **`TestParticipantListIntegrity`** — Data structure integrity

## Fixtures

Reusable fixtures are defined in `conftest.py`:

- **`client`** — TestClient instance for making API requests
- **`sample_activities`** — Dictionary of test activities with varying participant counts (0, 1, 2+)
- **`test_email`** — Standard test email (`test@example.com`)
- **`another_test_email`** — Second test email for multi-user scenarios (`another@example.com`)
- **`test_activity_name`** — Standard test activity name (`Test Activity One`)

### Using Fixtures

Fixtures are automatically injected into test functions:

```python
def test_signup_success(self, client, test_email):
    """Test successful signup for an activity."""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": test_email}
    )
    assert response.status_code == 200
```

## Test Coverage

Current coverage targets:
- **Line coverage**: ≥80% of `src/app.py`
- **Branch coverage**: Key validation paths and error scenarios

Generate a coverage report:
```bash
pytest --cov=src --cov-report=term-missing
```

## Adding New Tests

1. **For new endpoints**: Add test class to `test_api_endpoints.py`
2. **For new business logic**: Add test class to `test_app_logic.py`
3. **For new fixtures**: Add to `conftest.py`

Example test structure:
```python
class TestNewFeature:
    """Tests for new feature."""
    
    def test_happy_path(self, client, test_email):
        """Test successful scenario."""
        response = client.post("/endpoint", params={"email": test_email})
        assert response.status_code == 200
    
    def test_error_case(self, client):
        """Test error handling."""
        response = client.post("/endpoint", params={"email": ""})
        assert response.status_code == 400
```

## Debugging Tests

### Run a specific test with print statements
```bash
pytest tests/test_api_endpoints.py::TestSignupEndpoint::test_signup_success -v -s
```

The `-s` flag shows print output.

### Run with pdb debugger
```bash
pytest tests/test_api_endpoints.py::TestSignupEndpoint::test_signup_success --pdb
```

### Show test names without running
```bash
pytest --collect-only
```

## Common Issues

### Import Errors
Ensure `pytest.ini` is configured correctly and `src/app.py` is importable:
```bash
python -c "from src.app import app"
```

### Fixture Conflicts
Fixtures are scoped at module level. Use specific fixture names to avoid conflicts.

### Test Isolation
Each test modifies the in-memory `activities` dictionary. Tests may affect each other if the dictionary isn't properly reset. This is by design for integration tests to verify real behavior.

To isolate tests, use fixtures that create fresh copies of test data.

## Performance

- All tests should complete in < 1 second (in-memory operations)
- If tests are slow, check for unintended I/O or network calls

## CI/CD Integration

Run tests before committing:
```bash
pytest --cov=src && pytest --cov-fail-under=80
```

This ensures coverage is maintained above 80%.

## References

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/advanced/testing-dependencies/)
- [TestClient Documentation](https://fastapi.tiangolo.com/tutorial/testing/)

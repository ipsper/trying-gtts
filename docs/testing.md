# Testing Guide

Comprehensive testing guide for the gTTS FastAPI application using pytest in Docker containers.

## Table of Contents
- [Overview](#overview)
- [Quick Start](#quick-start)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Categories](#test-categories)
- [Writing Tests](#writing-tests)
- [CI/CD Integration](#cicd-integration)

## Overview

The testing framework uses **pytest** to run automated tests against the production web server. Tests run in isolated Docker containers to ensure consistency and reproducibility.

### Key Features

- ✅ **Docker-based** - Tests run in containers for consistency
- ✅ **Comprehensive coverage** - 50+ tests across all endpoints
- ✅ **Multiple test categories** - Smoke, API, validation, error handling, integration
- ✅ **HTML reports** - Beautiful test reports with pytest-html
- ✅ **Fast execution** - Parallel test execution support
- ✅ **Easy to extend** - Simple structure for adding new tests

## Quick Start

### Run All Tests (Docker)

```bash
# From project root
cd testing
./run_tests.sh
```

This will:
1. Build the API container
2. Build the test container
3. Wait for API to be healthy
4. Run all tests
5. Generate HTML report
6. Clean up containers

### Run Specific Test Categories

```bash
# Smoke tests only (quick sanity checks)
./run_tests.sh --smoke

# Integration tests only
./run_tests.sh --integration

# With coverage report
./run_tests.sh --coverage
```

### Run Tests Locally

```bash
# Start the API first
cd ..
./scripts/start.sh

# Run tests against running API
cd testing
./run_tests.sh --local
```

## Test Structure

```
testing/
├── Dockerfile                  # Test runner container
├── docker-compose.test.yml     # Orchestrates API + tests
├── pytest.ini                  # Pytest configuration
├── conftest.py                 # Fixtures and test setup
├── requirements.txt            # Test dependencies
├── run_tests.sh               # Main test runner script
├── reports/                    # Generated test reports
│   └── test-report.html
└── tests/                      # Test modules
    ├── __init__.py
    ├── test_health.py         # Health endpoint tests
    ├── test_root_endpoint.py  # Root API tests
    ├── test_languages.py      # Languages endpoint tests
    ├── test_tts_endpoint.py   # TTS endpoint tests
    ├── test_validation.py     # Input validation tests
    ├── test_error_handling.py # Error handling tests
    └── test_integration.py    # Integration workflows
```

## Running Tests

### Docker Mode (Recommended)

```bash
# All tests
./run_tests.sh

# Smoke tests (fast)
./run_tests.sh --smoke

# Integration tests
./run_tests.sh --integration

# With coverage
./run_tests.sh --coverage
```

### Local Mode

Requires API to be running on localhost:8088:

```bash
# Start API
cd ..
./scripts/start.sh

# Run tests
cd testing
./run_tests.sh --local
```

### Direct pytest Commands

Inside the testing directory:

```bash
# Activate virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set API location
export API_HOST=localhost
export API_PORT=8088

# Run tests
pytest -v

# Run specific test file
pytest tests/test_health.py -v

# Run specific test
pytest tests/test_health.py::TestHealthEndpoint::test_health_check_returns_200 -v

# Run with markers
pytest -m smoke -v
pytest -m "api and not slow" -v
```

## Test Categories

Tests are organized by markers for easy filtering:

### Smoke Tests (`@pytest.mark.smoke`)

Quick sanity checks to verify basic functionality.

```bash
./run_tests.sh --smoke
```

**Tests:**
- Health check responds
- API is accessible
- Basic endpoints return expected status codes

### API Tests (`@pytest.mark.api`)

Test all API endpoints and their functionality.

```bash
pytest -m api -v
```

**Tests:**
- All endpoints return correct status codes
- Response structures are correct
- Content types are correct
- Data validation

### Validation Tests (`@pytest.mark.validation`)

Test input validation and boundary conditions.

```bash
pytest -m validation -v
```

**Tests:**
- Empty/whitespace text validation
- Text length boundaries (min/max)
- Missing required fields
- Invalid JSON handling

### Error Handling Tests (`@pytest.mark.error`)

Test error responses and edge cases.

```bash
pytest -m error -v
```

**Tests:**
- Invalid language codes
- Wrong HTTP methods
- Wrong content types
- 404 for non-existent endpoints

### Integration Tests (`@pytest.mark.integration`)

Test complete workflows and multiple operations.

```bash
./run_tests.sh --integration
```

**Tests:**
- Complete TTS workflow
- Multiple sequential requests
- API documentation accessibility
- Error recovery

### Slow Tests (`@pytest.mark.slow`)

Tests that take longer to execute.

```bash
# Skip slow tests
pytest -m "not slow" -v

# Run only slow tests
pytest -m slow -v
```

## Writing Tests

### Basic Test Structure

```python
import pytest
import requests


@pytest.mark.api
class TestMyFeature:
    """Test suite for my feature"""
    
    def test_feature_works(
        self, 
        api_client: requests.Session,
        tts_endpoint: str
    ):
        """Test that feature works correctly"""
        # Arrange
        payload = {"text": "test", "lang": "en"}
        
        # Act
        response = api_client.post(tts_endpoint, json=payload)
        
        # Assert
        assert response.status_code == 200
```

### Available Fixtures

#### Session Fixtures

- `api_base_url` - Base URL for API (e.g., "http://api:8000")
- `api_client` - Configured requests.Session with automatic API wait

#### Endpoint Fixtures

- `tts_endpoint` - TTS endpoint URL
- `languages_endpoint` - Languages endpoint URL
- `health_endpoint` - Health check endpoint URL
- `root_endpoint` - Root API endpoint URL

#### Payload Fixtures

- `valid_tts_payload` - Valid English TTS payload
- `valid_swedish_payload` - Valid Swedish TTS payload
- `multiline_payload` - Valid multi-line text payload

### Adding New Tests

1. Create test file in `tests/` directory:

```bash
cd testing/tests
touch test_new_feature.py
```

2. Write tests using pytest conventions:

```python
"""
New feature tests
"""
import pytest
import requests


@pytest.mark.api  # Add appropriate marker
class TestNewFeature:
    """Test suite for new feature"""
    
    def test_new_feature(
        self, 
        api_client: requests.Session,
        api_base_url: str
    ):
        """Test description"""
        response = api_client.get(f"{api_base_url}/new-endpoint")
        assert response.status_code == 200
```

3. Run your tests:

```bash
pytest tests/test_new_feature.py -v
```

### Custom Fixtures

Add custom fixtures to `conftest.py`:

```python
@pytest.fixture
def custom_payload() -> dict:
    """Custom test payload"""
    return {
        "text": "Custom test text",
        "lang": "en",
        "extra_field": "value"
    }
```

## Test Reports

### HTML Report

After running tests, view the HTML report:

```bash
# Report location
testing/reports/test-report.html

# Open in browser (macOS)
open testing/reports/test-report.html

# Open in browser (Linux)
xdg-open testing/reports/test-report.html
```

### Coverage Report

Generate coverage report:

```bash
./run_tests.sh --coverage

# View coverage report
open testing/htmlcov/index.html
```

### Console Output

Pytest provides detailed console output:

```
================================ test session starts =================================
platform darwin -- Python 3.11.0, pytest-7.4.3
rootdir: /app/testing
configfile: pytest.ini
testpaths: tests
plugins: asyncio-0.21.1, cov-4.1.0, html-4.1.1, timeout-2.2.0
collected 45 items

tests/test_health.py::TestHealthEndpoint::test_health_check_returns_200 PASSED  [  2%]
tests/test_health.py::TestHealthEndpoint::test_health_check_response_structure PASSED  [  4%]
...
================================ 45 passed in 12.34s =================================
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: API Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Build and run tests
        run: |
          cd testing
          chmod +x run_tests.sh
          ./run_tests.sh
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-reports
          path: testing/reports/
```

### GitLab CI Example

```yaml
test:
  stage: test
  image: docker:latest
  services:
    - docker:dind
  script:
    - cd testing
    - chmod +x run_tests.sh
    - ./run_tests.sh
  artifacts:
    when: always
    paths:
      - testing/reports/
    reports:
      junit: testing/reports/junit.xml
```

## Cleanup

Remove test containers and reports:

```bash
./run_tests.sh --clean
```

This removes:
- Docker containers
- Docker volumes
- Test reports
- Pytest cache

## Troubleshooting

### API Not Ready

If tests fail with connection errors:

```bash
# Check if API is running
docker ps | grep gtts

# View API logs
docker logs gtts-api-test

# Increase healthcheck retries in docker-compose.test.yml
```

### Tests Timing Out

If tests timeout:

```bash
# Increase timeout in pytest.ini
timeout = 60

# Or skip slow tests
pytest -m "not slow" -v
```

### Port Already in Use

If port 8088 is in use:

```bash
# Stop existing API
cd ..
./scripts/stop.sh

# Or change port in docker-compose.test.yml
```

### Permission Errors

If you get permission errors:

```bash
# Make script executable
chmod +x run_tests.sh

# Fix reports directory permissions
chmod -R 755 reports/
```

## Best Practices

1. **Use appropriate markers** - Tag tests with @pytest.mark.smoke, @pytest.mark.api, etc.
2. **Keep tests independent** - Each test should be able to run standalone
3. **Use descriptive names** - test_tts_with_empty_text_returns_422
4. **Test one thing** - Each test should verify one specific behavior
5. **Use fixtures** - Reuse common setup with pytest fixtures
6. **Document tests** - Add docstrings explaining what is being tested
7. **Clean up** - Tests should not leave artifacts
8. **Fast feedback** - Run smoke tests frequently, full suite before commits

## Performance

### Parallel Execution

Run tests in parallel for faster execution:

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run with 4 workers
pytest -n 4 -v
```

### Test Execution Times

- Smoke tests: ~5 seconds
- All tests (sequential): ~30 seconds
- All tests (parallel): ~15 seconds
- Integration tests: ~20 seconds

## Next Steps

- [API Reference](api-reference.md) - Understand what's being tested
- [Examples](examples.md) - See how to use the API
- [Troubleshooting](troubleshooting.md) - Common issues
- [Configuration](configuration.md) - Customize test environment


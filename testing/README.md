# gTTS API Testing

Automated testing framework using pytest in Docker containers.

## Quick Start

```bash
# Run all tests
./run_tests.sh

# Run smoke tests only
./run_tests.sh --smoke

# Run with coverage
./run_tests.sh --coverage

# Clean up
./run_tests.sh --clean
```

## Test Structure

- `tests/` - Test modules organized by feature
- `conftest.py` - Pytest fixtures and configuration
- `pytest.ini` - Pytest settings
- `Dockerfile` - Test runner container
- `docker-compose.test.yml` - Orchestrates API + test containers
- `run_tests.sh` - Main test runner script

## Available Commands

```bash
./run_tests.sh              # Run tests, stop on first failure (default)
./run_tests.sh --run-to-done # Run all tests to completion
./run_tests.sh --docker     # Run in Docker (default)
./run_tests.sh --local      # Run against local API
./run_tests.sh --smoke      # Quick smoke tests
./run_tests.sh --integration # Integration tests
./run_tests.sh --coverage   # With coverage report
./run_tests.sh --clean      # Clean up everything
./run_tests.sh --help       # Show help
```

**Important:** By default, tests **stop at the first failure** for faster feedback. Use `--run-to-done` to run all tests regardless of failures.

## Test Categories

- **Smoke** (`@pytest.mark.smoke`) - Quick sanity checks
- **API** (`@pytest.mark.api`) - API endpoint tests
- **Validation** (`@pytest.mark.validation`) - Input validation
- **Error** (`@pytest.mark.error`) - Error handling
- **Integration** (`@pytest.mark.integration`) - Complete workflows
- **Slow** (`@pytest.mark.slow`) - Long-running tests

## Test Coverage

### Endpoints Tested

- ✅ `GET /health` - Health check
- ✅ `GET /api/v1/` - Root endpoint
- ✅ `GET /api/v1/languages` - Languages list
- ✅ `POST /api/v1/tts` - Text-to-speech generation

### Test Cases

- 50+ test cases covering:
  - All API endpoints
  - Input validation (empty, whitespace, length limits)
  - Error handling (invalid language, wrong methods, etc.)
  - Multi-line text
  - Special characters and Unicode
  - Integration workflows
  - API documentation accessibility

## Reports

After running tests, check:

- `reports/test-report.html` - HTML test report
- `htmlcov/index.html` - Coverage report (if --coverage used)

```bash
# Open HTML report (macOS)
open reports/test-report.html

# Open HTML report (Linux)
xdg-open reports/test-report.html
```

## Writing New Tests

1. Create test file in `tests/` directory:

```python
# tests/test_new_feature.py
import pytest
import requests

@pytest.mark.api
class TestNewFeature:
    def test_feature_works(
        self,
        api_client: requests.Session,
        tts_endpoint: str
    ):
        """Test that feature works"""
        response = api_client.post(tts_endpoint, json={"text": "test", "lang": "en"})
        assert response.status_code == 200
```

2. Run the new tests:

```bash
pytest tests/test_new_feature.py -v
```

## CI/CD Integration

### GitHub Actions

```yaml
- name: Run tests
  run: |
    cd testing
    ./run_tests.sh
```

### GitLab CI

```yaml
test:
  script:
    - cd testing
    - ./run_tests.sh
```

## Requirements

- Docker
- Docker Compose
- Or: Python 3.11+ for local testing

## Documentation

For detailed documentation, see [docs/testing.md](../docs/testing.md)

## Troubleshooting

### API Not Ready

If tests fail immediately with connection errors:

```bash
# Check logs
docker logs gtts-api-test

# Increase retries in docker-compose.test.yml
```

### Port Conflicts

If port 8088 is in use:

```bash
# Stop existing containers
cd ..
./scripts/stop.sh
```

### Clean Start

For a fresh start:

```bash
./run_tests.sh --clean
docker-compose -f docker-compose.test.yml down -v
./run_tests.sh
```

## License

Same as main project (MIT)


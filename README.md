# gTTS FastAPI Docker Container

A FastAPI application that uses Google Text-to-Speech (gTTS) to convert text to speech, packaged in a Docker container with comprehensive validation and error handling.

## Features

- **FastAPI** with APIRouter for structured API design
- **gTTS** (Google Text-to-Speech) integration
- **Docker** multi-stage containerized application
- **Robust input validation** - All text input is validated and sanitized
- **JSON-safe** - Ensures all input can be properly serialized
- **Port configuration** - Configurable via environment variables (default: 8088)
- **Auto-build** - Management scripts automatically build if needed
- **Port checking** - Detects and reports port conflicts
- Support for 13+ languages

## Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd trying-gtts

# Start the container (automatically builds if needed)
./scripts/start.sh

# The API will be available at:
# - http://localhost:8088/docs (Swagger UI)
# - http://localhost:8088/redoc (ReDoc)
# - http://localhost:8088/health (Health check)
```

## Basic Usage

### Generate Speech

```bash
# English
curl -X POST "http://localhost:8088/api/v1/tts" \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello world!", "lang":"en"}' \
  --output hello.mp3

# Swedish
curl -X POST "http://localhost:8088/api/v1/tts" \
  -H "Content-Type: application/json" \
  -d '{"text":"Hej världen!", "lang":"sv"}' \
  --output hej.mp3

# Multi-line text (use \n for newlines)
curl -X POST "http://localhost:8088/api/v1/tts" \
  -H "Content-Type: application/json" \
  -d '{"text":"Line 1.\nLine 2.\nLine 3.", "lang":"en"}' \
  --output multiline.mp3
```

### List Available Languages

```bash
curl http://localhost:8088/api/v1/languages
```

## Management Commands

```bash
# Start container (auto-builds if needed)
./scripts/start.sh

# Stop container
./scripts/stop.sh

# View logs
./scripts/manage.sh logs

# Check status
./scripts/manage.sh status

# Clean up everything
./scripts/clean.sh

# Full rebuild
./scripts/manage.sh rebuild

# Show help
./scripts/manage.sh help
```

## Port Configuration

Default port is **8088**. Change it using the `GTTS_PORT` environment variable:

```bash
# Use a different port
GTTS_PORT=9000 ./scripts/start.sh

# Or export it
export GTTS_PORT=9000
./scripts/start.sh
```

## Documentation

### 📖 Complete Documentation

- **[Installation Guide](docs/installation.md)** - Detailed setup instructions for Docker, Docker Compose, and local development
- **[Configuration Guide](docs/configuration.md)** - Port settings, environment variables, Docker configs, and performance tuning
- **[API Reference](docs/api-reference.md)** - Complete API endpoint documentation with examples
- **[Examples](docs/examples.md)** - Usage examples in cURL, Python, JavaScript/Node.js
- **[Testing Guide](docs/testing.md)** - Comprehensive pytest testing framework and guide
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions

### 🚀 Quick Links

| Topic | Description |
|-------|-------------|
| [Getting Started](docs/installation.md#quick-start) | Fastest way to run the application |
| [Docker Setup](docs/installation.md#using-docker-recommended) | Using Docker and Docker Compose |
| [Local Development](docs/installation.md#local-development-setup) | Running without Docker (with venv) |
| [Port Configuration](docs/configuration.md#port-configuration) | Changing default port |
| [API Endpoints](docs/api-reference.md#endpoints) | Complete endpoint reference |
| [Error Handling](docs/api-reference.md#error-responses) | Understanding error responses |
| [Common Issues](docs/troubleshooting.md) | Solutions to common problems |
| [Python Examples](docs/examples.md#python-examples) | Using the API with Python |
| [Multi-line Text](docs/troubleshooting.md#json-decode-error-with-multi-line-text) | Handling newlines correctly |
| [Testing](docs/testing.md) | Running automated tests |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/` | GET | API information and welcome message |
| `/api/v1/tts` | POST | Convert text to speech (returns MP3) |
| `/api/v1/languages` | GET | List supported languages |
| `/health` | GET | Health check endpoint |

See [API Reference](docs/api-reference.md) for detailed documentation.

## Supported Languages

The API supports many languages including:

- `sv` - Swedish (**not** `se`)
- `en` - English
- `es` - Spanish
- `fr` - French
- `de` - German
- `it` - Italian
- `pt` - Portuguese
- `ru` - Russian
- `ja` - Japanese
- `zh-CN` - Chinese (Simplified)
- `ar` - Arabic
- `hi` - Hindi
- `ko` - Korean

**Note:** Use ISO 639-1 language codes. Common mistakes: `se` → `sv`, `dk` → `da`, `no` → `nb`

See [API Reference](docs/api-reference.md#language-codes-reference) for complete list.

## Technology Stack

- **Python 3.11** - Modern Python version
- **FastAPI** - High-performance web framework
- **gTTS** - Google Text-to-Speech library
- **Uvicorn** - ASGI server
- **Docker** - Multi-stage containerization
- **Pydantic** - Data validation

## Project Structure

```
.
├── Dockerfile              # Multi-stage Docker configuration
├── docker-compose.yml      # Docker Compose configuration
├── .dockerignore          # Docker build exclusions
├── .gitignore             # Git exclusions
├── requirements.txt       # Python dependencies
├── main.py               # FastAPI application
├── README.md             # This file (overview)
├── test_multiline.sh     # Test script for multi-line text
├── docs/                 # Documentation
│   ├── installation.md   # Installation guide
│   ├── configuration.md  # Configuration guide
│   ├── api-reference.md  # API documentation
│   ├── examples.md       # Usage examples
│   ├── testing.md        # Testing guide
│   └── troubleshooting.md # Troubleshooting guide
├── scripts/              # Management scripts
│   ├── manage.sh         # Main management script
│   ├── build.sh          # Quick build
│   ├── start.sh          # Quick start
│   ├── stop.sh           # Quick stop
│   └── clean.sh          # Quick cleanup
└── testing/              # Pytest test suite
    ├── Dockerfile        # Test runner container
    ├── docker-compose.test.yml  # Test orchestration
    ├── pytest.ini        # Pytest configuration
    ├── conftest.py       # Test fixtures
    ├── requirements.txt  # Test dependencies
    ├── run_tests.sh      # Test runner script
    ├── reports/          # Test reports (generated)
    └── tests/            # Test modules
        ├── test_health.py
        ├── test_root_endpoint.py
        ├── test_languages.py
        ├── test_tts_endpoint.py
        ├── test_validation.py
        ├── test_error_handling.py
        └── test_integration.py
```

## Interactive Documentation

When the application is running, access the interactive documentation:

- **Swagger UI**: http://localhost:8088/docs
- **ReDoc**: http://localhost:8088/redoc
- **OpenAPI JSON**: http://localhost:8088/openapi.json

## Requirements

### Docker (Recommended)
- Docker 20.10+
- Docker Compose 2.0+ (optional)

### Local Development
- Python 3.11+
- pip
- Virtual environment (venv)

See [Installation Guide](docs/installation.md#requirements) for details.

## Common Issues

### Multi-line Text in JSON

❌ **Wrong:** Actual newlines break JSON
```bash
curl -d '{
  "text": "Line 1
Line 2"
}'
```

✅ **Correct:** Use `\n` escape sequences
```bash
curl -d '{"text":"Line 1\nLine 2", "lang":"en"}'
```

### Invalid Language Code

❌ **Wrong:** `se` is not a valid code
```bash
curl -d '{"text":"Hej!", "lang":"se"}'
```

✅ **Correct:** Use `sv` for Swedish
```bash
curl -d '{"text":"Hej!", "lang":"sv"}'
```

### Port Already in Use

```bash
# Check what's using the port
./scripts/manage.sh status

# Use a different port
GTTS_PORT=9000 ./scripts/start.sh
```

See [Troubleshooting Guide](docs/troubleshooting.md) for more solutions.

## Development

### Local Setup (with venv)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

See [Installation Guide](docs/installation.md#local-development-setup) for detailed instructions.

## Docker Multi-Stage Build

This project uses multi-stage Docker builds for optimized images:

- **Stage 1 (builder)**: Installs build dependencies and compiles packages
- **Stage 2 (runtime)**: Contains only runtime dependencies

**Benefits:**
- Smaller final image size
- No build tools in production
- Better security (reduced attack surface)
- Faster deployments

See [Configuration Guide](docs/configuration.md#docker-configuration) for details.

## Management Script Features

The `scripts/manage.sh` provides:

- ✅ **Auto-build** - Builds image if not found
- ✅ **Port checking** - Detects port conflicts
- ✅ **Conflict detection** - Shows what's using ports
- ✅ **Color-coded output** - Easy-to-read messages
- ✅ **Comprehensive cleanup** - Removes all traces
- ✅ **Status monitoring** - Check container/image/port status
- ✅ **Log viewing** - Real-time log following

## Testing

### Automated Testing with pytest

The project includes a comprehensive pytest test suite that runs in Docker containers.

```bash
# Run all tests
cd testing
./run_tests.sh

# Run smoke tests (quick)
./run_tests.sh --smoke

# Run with coverage report
./run_tests.sh --coverage

# Clean up
./run_tests.sh --clean
```

**Test Categories:**
- 🔥 Smoke tests - Quick sanity checks
- 🌐 API tests - All endpoint functionality  
- ✅ Validation tests - Input validation
- ❌ Error handling tests - Error responses
- 🔄 Integration tests - Complete workflows

See [Testing Guide](docs/testing.md) for detailed documentation.

### Manual Testing

```bash
# Test multi-line text handling
./test_multiline.sh

# Manual API test
curl -X POST "http://localhost:8088/api/v1/tts" \
  -H "Content-Type: application/json" \
  -d '{"text":"Test message", "lang":"en"}' \
  --output test.mp3

# Verify health
curl http://localhost:8088/health
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT license.

## Support

- 📚 [Complete Documentation](docs/)
- 🐛 [Troubleshooting Guide](docs/troubleshooting.md)
- 💡 [Examples](docs/examples.md)
- 🔧 [Configuration](docs/configuration.md)

## Version

**Version:** 1.0.0

## Author

Your Name

---

**Made with ❤️ using FastAPI and gTTS**

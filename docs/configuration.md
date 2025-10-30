# Configuration Guide

This document covers all configuration options for the gTTS FastAPI application.

## Table of Contents
- [Port Configuration](#port-configuration)
- [Docker Configuration](#docker-configuration)
- [Environment Variables](#environment-variables)
- [Docker Compose Configuration](#docker-compose-configuration)
- [Application Configuration](#application-configuration)

## Port Configuration

### Default Port

The application runs on port **8088** by default (host) and maps to port **8000** inside the container.

### Changing the Port

#### Using Environment Variable

```bash
# Set the GTTS_PORT environment variable
export GTTS_PORT=9000

# Start the application
./scripts/start.sh
```

#### One-line Command

```bash
# For management script
GTTS_PORT=9000 ./scripts/manage.sh start

# For Docker Compose
GTTS_PORT=9000 docker-compose up -d
```

#### Manual Docker Command

```bash
# Map to a different host port
docker run -d -p 9000:8000 --name gtts-fastapi gtts-fastapi
```

### Checking Port Configuration

```bash
# View current configuration
./scripts/manage.sh help

# Check port status
./scripts/manage.sh status
```

## Docker Configuration

### Dockerfile Configuration

The application uses a multi-stage Dockerfile:

**Stage 1: Builder**
- Base image: `python:3.11-slim`
- Installs build dependencies (gcc)
- Compiles Python packages

**Stage 2: Runtime**
- Base image: `python:3.11-slim`
- Copies only runtime dependencies
- Runs as non-root user (`appuser`)

### Build Arguments

Currently, the Dockerfile doesn't use build arguments, but you can modify it to accept them:

```dockerfile
ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim as builder
```

Then build with:

```bash
docker build --build-arg PYTHON_VERSION=3.12 -t gtts-fastapi .
```

## Environment Variables

### Available Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GTTS_PORT` | `8088` | Host port to bind to |

### Setting Environment Variables

#### In Shell

```bash
export GTTS_PORT=9000
./scripts/start.sh
```

#### In Docker Compose

Edit `docker-compose.yml`:

```yaml
services:
  gtts-api:
    environment:
      - GTTS_PORT=9000
```

Or use a `.env` file (create it in project root):

```bash
# .env file
GTTS_PORT=9000
```

Then:

```bash
docker-compose up -d
```

## Docker Compose Configuration

### Default Configuration

The `docker-compose.yml` file contains:

```yaml
version: '3.8'

services:
  gtts-api:
    build: .
    container_name: gtts-fastapi
    ports:
      - "${GTTS_PORT:-8088}:8000"
    restart: unless-stopped
    environment:
      - PORT=8000
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Customizing Docker Compose

#### Change Restart Policy

```yaml
services:
  gtts-api:
    restart: always  # or 'no', 'on-failure', 'unless-stopped'
```

#### Add Volume for Logs

```yaml
services:
  gtts-api:
    volumes:
      - ./logs:/app/logs
```

#### Resource Limits

```yaml
services:
  gtts-api:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

## Application Configuration

### FastAPI Configuration

The application is configured in `main.py`:

```python
app = FastAPI(
    title="gTTS API",
    version="1.0.0"
)
```

You can modify these settings:

```python
app = FastAPI(
    title="gTTS API",
    version="1.0.0",
    description="Text-to-Speech API using Google TTS",
    docs_url="/docs",      # Swagger UI path
    redoc_url="/redoc",    # ReDoc path
    openapi_url="/openapi.json"
)
```

### Text Validation Limits

Configured in the `TextToSpeechRequest` model:

```python
class TextToSpeechRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    lang: str = Field(default="en")
```

To change limits, edit `main.py`:

```python
text: str = Field(..., min_length=1, max_length=10000)  # Increase to 10k
```

### Default Language

Change the default language:

```python
lang: str = Field(default="sv")  # Default to Swedish instead of English
```

### CORS Configuration

To enable CORS (for web applications), add to `main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Management Script Configuration

The `scripts/manage.sh` script has these configurable variables at the top:

```bash
# Container and image configuration
CONTAINER_NAME="gtts-fastapi"
IMAGE_NAME="gtts-fastapi"
IMAGE_TAG="latest"
PORT="${GTTS_PORT:-8088}"
```

You can modify these directly in the script or override with environment variables.

## Security Considerations

### Running as Non-Root

The Docker container runs as a non-root user (`appuser`) by default. This is configured in the Dockerfile:

```dockerfile
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser
```

### Network Security

For production:

1. Use HTTPS (reverse proxy like nginx)
2. Enable CORS only for specific origins
3. Use firewall rules to restrict access
4. Consider using Docker secrets for sensitive data

### Example with Nginx Reverse Proxy

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8088;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Logging Configuration

### View Logs

```bash
# With management script
./scripts/manage.sh logs

# With Docker directly
docker logs -f gtts-fastapi

# With Docker Compose
docker-compose logs -f
```

### Custom Logging

To add custom logging to the application, edit `main.py`:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@router.post("/tts")
async def text_to_speech(request: TextToSpeechRequest):
    logger.info(f"TTS request: lang={request.lang}, text_length={len(request.text)}")
    # ... rest of the code
```

## Performance Tuning

### Uvicorn Workers

For production, increase the number of workers in the Dockerfile:

```dockerfile
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Docker Resource Limits

Limit resource usage in `docker-compose.yml`:

```yaml
services:
  gtts-api:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 1G
```

## Next Steps

- See [installation.md](installation.md) for setup instructions
- See [examples.md](examples.md) for usage examples
- See [api-reference.md](api-reference.md) for API documentation


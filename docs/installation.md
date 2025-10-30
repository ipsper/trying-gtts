# Installation Guide

This guide covers different ways to install and run the gTTS FastAPI application.

## Table of Contents
- [Using Docker (Recommended)](#using-docker-recommended)
- [Using Docker Compose](#using-docker-compose)
- [Local Development Setup](#local-development-setup)
- [Requirements](#requirements)

## Using Docker (Recommended)

The easiest way to get started is using the provided management scripts.

### Quick Start

```bash
# Start the container (automatically builds if needed)
./scripts/start.sh

# The API will be available at:
# - http://localhost:8088/docs (Swagger UI)
# - http://localhost:8088/redoc (ReDoc)
```

### Management Commands

```bash
# Start container (auto-builds image if not found)
./scripts/manage.sh start

# Stop container
./scripts/manage.sh stop

# Restart container
./scripts/manage.sh restart

# View logs (follow mode)
./scripts/manage.sh logs

# Check status
./scripts/manage.sh status

# Complete cleanup (removes everything)
./scripts/manage.sh clean

# Rebuild from scratch
./scripts/manage.sh rebuild

# Show help
./scripts/manage.sh help
```

### Manual Docker Commands

If you prefer to use Docker directly:

```bash
# Build the image
docker build -t gtts-fastapi .

# Run the container (default port 8088)
docker run -d -p 8088:8000 --name gtts-fastapi gtts-fastapi

# Run on a different port
docker run -d -p 9000:8000 --name gtts-fastapi gtts-fastapi

# Stop the container
docker stop gtts-fastapi

# Remove the container
docker rm gtts-fastapi

# View logs
docker logs -f gtts-fastapi
```

## Using Docker Compose

Docker Compose provides an easy way to manage the application.

```bash
# Start with default port (8088)
docker-compose up -d

# Start with custom port
GTTS_PORT=9000 docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Local Development Setup

For local development without Docker, use a virtual environment to keep your system clean.

### Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
# Make sure venv is activated
source venv/bin/activate

# Run with Python directly
python main.py

# Or run with uvicorn (with auto-reload for development)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Deactivate Virtual Environment

When you're done:

```bash
deactivate
```

### Quick Development Workflow

```bash
# One-time setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Daily workflow
source venv/bin/activate        # Activate venv
uvicorn main:app --reload       # Start dev server
# ... do your work ...
deactivate                      # Deactivate when done
```

## Requirements

### For Docker Deployment

- Docker (version 20.10 or later)
- Docker Compose (version 2.0 or later) - optional

### For Local Development

- Python 3.11 or later
- pip (Python package manager)
- Virtual environment support (venv)

### Dependencies

The application requires the following Python packages (defined in `requirements.txt`):

- `fastapi==0.104.1` - Web framework
- `uvicorn[standard]==0.24.0` - ASGI server
- `gTTS==2.5.0` - Google Text-to-Speech
- `python-multipart==0.0.6` - Form data support

## Port Configuration

The default port is **8088**. You can change it using the `GTTS_PORT` environment variable:

```bash
# Using management scripts
export GTTS_PORT=9000
./scripts/start.sh

# Or in a single command
GTTS_PORT=9000 ./scripts/manage.sh start

# With Docker Compose
GTTS_PORT=9000 docker-compose up -d

# Check current port configuration
./scripts/manage.sh help
```

## Verifying Installation

After starting the application, verify it's working:

```bash
# Health check
curl http://localhost:8088/health

# Expected response:
# {"status":"healthy","service":"gTTS API","version":"1.0.0"}

# View API documentation
# Open in browser: http://localhost:8088/docs
```

## Troubleshooting

### Port Already in Use

If you get a "port already in use" error:

```bash
# Check what's using the port
./scripts/manage.sh status

# The script will show you the process ID (PID) and provide kill commands
```

### Docker Image Build Fails

If the Docker build fails:

```bash
# Clean up and try again
./scripts/manage.sh clean
./scripts/manage.sh rebuild
```

### Cannot Connect to Docker Daemon

Make sure Docker is running:

```bash
# On macOS/Linux
docker info

# Start Docker Desktop if not running
```

## Next Steps

- See [examples.md](examples.md) for usage examples
- See [configuration.md](configuration.md) for advanced configuration
- See [api-reference.md](api-reference.md) for API documentation


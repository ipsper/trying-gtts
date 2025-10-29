# Troubleshooting Guide

Common issues and their solutions when working with the gTTS FastAPI application.

## Table of Contents
- [API Errors](#api-errors)
- [Docker Issues](#docker-issues)
- [Port Conflicts](#port-conflicts)
- [Installation Problems](#installation-problems)
- [Runtime Errors](#runtime-errors)
- [Performance Issues](#performance-issues)

## API Errors

### JSON Decode Error with Multi-line Text

**Problem:**
```bash
curl -d '{
  "text": "Line 1
Line 2"
}'
# Error: JSON decode error - Invalid control character
```

**Cause:** JSON doesn't allow actual newlines in strings.

**Solution:** Use `\n` escape sequences:
```bash
curl -d '{"text":"Line 1\nLine 2", "lang":"en"}'
```

---

### Invalid Language Code Error

**Problem:**
```bash
curl -d '{"text":"Hej!", "lang":"se"}'
# Error: Failed to generate speech
```

**Cause:** Invalid language code. `se` is not a valid ISO 639-1 code.

**Solution:** Use correct language codes:
- ✅ `sv` for Swedish (not `se`)
- ✅ `da` for Danish (not `dk`)
- ✅ `nb` for Norwegian Bokmål (not `no`)

Check available languages:
```bash
curl http://localhost:8088/api/v1/languages
```

---

### Text Too Long Error

**Problem:**
```json
{
  "detail": [
    {
      "msg": "String should have at most 5000 characters"
    }
  ]
}
```

**Cause:** Text exceeds 5000 character limit.

**Solution:** 
1. Split text into multiple requests
2. Reduce text length
3. Or modify the limit in `main.py` (see [configuration.md](configuration.md))

---

### Empty Text Error

**Problem:**
```json
{
  "detail": [
    {
      "msg": "Text cannot be empty or only whitespace"
    }
  ]
}
```

**Cause:** Text field is empty or contains only whitespace.

**Solution:** Provide non-empty text:
```bash
curl -d '{"text":"Hello world!", "lang":"en"}'
```

## Docker Issues

### Cannot Connect to Docker Daemon

**Problem:**
```
Error: Cannot connect to the Docker daemon
```

**Cause:** Docker is not running.

**Solution:**
1. Start Docker Desktop (macOS/Windows)
2. Or start Docker service (Linux):
   ```bash
   sudo systemctl start docker
   ```

---

### Docker Build Fails

**Problem:**
```
Error building Docker image
```

**Possible Causes:**
1. Network issues downloading packages
2. Insufficient disk space
3. Corrupted build cache

**Solutions:**

**Clear Docker cache and rebuild:**
```bash
./scripts/manage.sh clean
docker system prune -a
./scripts/manage.sh rebuild
```

**Check disk space:**
```bash
df -h
docker system df
```

**Build without cache:**
```bash
docker build --no-cache -t gtts-fastapi .
```

---

### Container Won't Start

**Problem:**
```
Container exits immediately after starting
```

**Diagnosis:**
```bash
# Check container status
docker ps -a

# View logs
docker logs gtts-fastapi

# Or use management script
./scripts/manage.sh logs
```

**Common Causes:**
1. Port already in use
2. Missing dependencies
3. Application crashes on startup

**Solution:**
```bash
# Check detailed logs
./scripts/manage.sh logs

# Try rebuilding
./scripts/manage.sh rebuild
```

## Port Conflicts

### Port Already in Use

**Problem:**
```
[ERROR] Port 8088 is already in use by another process!
```

**Diagnosis:**
```bash
# Check what's using the port
./scripts/manage.sh status

# Or manually:
lsof -i :8088
```

**Solutions:**

**Option 1: Stop the conflicting process**
```bash
# Find process ID
lsof -i :8088

# Kill the process
kill <PID>

# Or force kill
kill -9 <PID>
```

**Option 2: Use a different port**
```bash
# Change port and start
GTTS_PORT=9000 ./scripts/start.sh
```

**Option 3: Stop our own container**
```bash
# If it's our container
./scripts/stop.sh
```

---

### Cannot Access Application on Configured Port

**Problem:** Container is running but cannot access http://localhost:8088

**Diagnosis:**
```bash
# Check container is running
docker ps | grep gtts-fastapi

# Check port mapping
docker port gtts-fastapi

# Test from inside container
docker exec gtts-fastapi curl http://localhost:8000/health
```

**Solutions:**

**Check firewall:**
```bash
# macOS
sudo pfctl -s all | grep 8088

# Linux
sudo iptables -L | grep 8088
```

**Check port binding:**
```bash
# Container should show: 0.0.0.0:8088->8000/tcp
docker ps
```

**Try localhost alternatives:**
```bash
curl http://127.0.0.1:8088/health
curl http://0.0.0.0:8088/health
```

## Installation Problems

### Python Version Mismatch

**Problem:**
```
Python 3.11 or later is required
```

**Solution:**
```bash
# Check Python version
python3 --version

# Install Python 3.11+ or use Docker instead
./scripts/start.sh
```

---

### pip Install Fails

**Problem:**
```
ERROR: Could not install packages
```

**Solutions:**

**Update pip:**
```bash
pip install --upgrade pip
```

**Install in virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Install with verbose output:**
```bash
pip install -r requirements.txt -v
```

---

### Missing System Dependencies

**Problem:** Build fails with gcc or compilation errors.

**Solution (Linux):**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install build-essential python3-dev

# CentOS/RHEL
sudo yum install gcc python3-devel
```

**Solution (macOS):**
```bash
xcode-select --install
```

**Or use Docker:**
```bash
# Docker handles all dependencies
./scripts/start.sh
```

## Runtime Errors

### File System Permission Errors

**Problem:**
```
Permission denied: /app/...
```

**Cause:** Container trying to write to read-only location.

**Solution:** The container already runs as non-root user. Check volume mounts if you added any:

```yaml
# In docker-compose.yml
volumes:
  - ./logs:/app/logs:rw  # Ensure read-write access
```

---

### Out of Memory

**Problem:**
```
Container killed (OOMKilled)
```

**Diagnosis:**
```bash
# Check container status
docker inspect gtts-fastapi | grep OOMKilled
```

**Solution:** Increase Docker memory limit:

**Docker Desktop:**
1. Settings → Resources → Memory
2. Increase to at least 2GB

**Docker Compose:**
```yaml
services:
  gtts-api:
    deploy:
      resources:
        limits:
          memory: 1G
```

---

### Temp File Cleanup Issues

**Problem:** Disk fills up with temporary MP3 files.

**Cause:** Background file cleanup not working.

**Diagnosis:**
```bash
# Check temp directory size
docker exec gtts-fastapi du -sh /tmp
```

**Solution:** The app automatically cleans up temp files. If issues persist:

```bash
# Restart container
./scripts/restart.sh

# Or manually clean temp files
docker exec gtts-fastapi find /tmp -name "*.mp3" -delete
```

## Performance Issues

### Slow Response Times

**Problem:** TTS generation takes too long.

**Possible Causes:**
1. Network latency to Google TTS
2. Container resource constraints
3. Very long text

**Solutions:**

**Check container resources:**
```bash
docker stats gtts-fastapi
```

**Increase resources (docker-compose.yml):**
```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 1G
```

**Use shorter text:**
- Split long texts into smaller chunks
- Maximum recommended: 1000-2000 characters per request

---

### High CPU Usage

**Problem:** Container using 100% CPU.

**Diagnosis:**
```bash
docker stats gtts-fastapi
```

**Solutions:**

**Limit CPU usage:**
```yaml
# docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '1.0'
```

**Check for loops or hangs:**
```bash
./scripts/manage.sh logs
```

## Getting More Help

### Enable Debug Logging

Add to `main.py`:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

Rebuild and check logs:
```bash
./scripts/rebuild.sh
./scripts/manage.sh logs
```

### Collect Diagnostic Information

```bash
# System info
uname -a
docker --version
docker-compose --version

# Container status
./scripts/manage.sh status

# Recent logs
./scripts/manage.sh logs | tail -100

# Docker info
docker info
docker ps -a
docker images
```

### Report Issues

When reporting issues, include:

1. Operating system and version
2. Docker version
3. How you're running the app (script, docker-compose, etc.)
4. Full error message
5. Relevant logs
6. Steps to reproduce

### Additional Resources

- [API Reference](api-reference.md)
- [Examples](examples.md)
- [Configuration](configuration.md)
- [Installation Guide](installation.md)
- Interactive API docs: http://localhost:8088/docs

## Quick Fixes Checklist

Before asking for help, try these:

- [ ] Restart the container: `./scripts/restart.sh`
- [ ] Check logs: `./scripts/manage.sh logs`
- [ ] Verify port isn't in use: `./scripts/manage.sh status`
- [ ] Clean rebuild: `./scripts/manage.sh rebuild`
- [ ] Check Docker is running: `docker ps`
- [ ] Verify correct language codes
- [ ] Ensure text uses `\n` for newlines in JSON
- [ ] Check text length (1-5000 chars)
- [ ] Try the interactive docs: http://localhost:8088/docs


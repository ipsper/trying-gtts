# Dockerfile for pytest test runner
FROM python:3.11-slim

# Set working directory
WORKDIR /app/testing

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create directories for mounted volumes
# Note: Test files (tests/, conftest.py, pytest.ini) are mounted as volumes
# This allows faster iteration without rebuilding the image
RUN mkdir -p reports tests

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTEST_ADDOPTS="--color=yes"

# Default command runs all tests
CMD ["pytest", "-v"]


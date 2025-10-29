# Dockerfile for pytest test runner
FROM python:3.11-slim

# Set working directory
WORKDIR /app/testing

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy test files
COPY pytest.ini .
COPY conftest.py .
COPY tests/ tests/

# Create reports directory
RUN mkdir -p reports

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTEST_ADDOPTS="--color=yes"

# Default command runs all tests
CMD ["pytest", "-v"]


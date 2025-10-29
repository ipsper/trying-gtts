#!/bin/bash
# Script to run pytest tests against the gTTS API

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Function to print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show help
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Run pytest tests against the gTTS API"
    echo ""
    echo "Options:"
    echo "  --docker          Run tests in Docker containers (default)"
    echo "  --local           Run tests locally (requires API to be running)"
    echo "  --smoke           Run only smoke tests"
    echo "  --integration     Run only integration tests"
    echo "  --coverage        Generate coverage report"
    echo "  --run-to-done     Continue running all tests even if some fail (default: stop on first failure)"
    echo "  --clean           Clean up test containers and reports"
    echo "  --help            Show this help message"
    echo ""
    echo "Test Behavior:"
    echo "  By default, tests STOP at the first failure for faster feedback."
    echo "  Use --run-to-done to run all tests regardless of failures."
    echo ""
    echo "Examples:"
    echo "  $0                    # Run tests, stop on first failure"
    echo "  $0 --run-to-done      # Run all tests to completion"
    echo "  $0 --smoke            # Run smoke tests only"
    echo "  $0 --local            # Run tests against local API"
    echo "  $0 --clean            # Clean up"
}

# Function to clean up
cleanup() {
    print_info "Cleaning up test environment..."
    
    cd "$SCRIPT_DIR"
    
    # Stop and remove containers
    docker-compose -f docker-compose.test.yml down -v 2>/dev/null || true
    
    # Remove test reports
    if [ -d "reports" ]; then
        rm -rf reports/*
        print_info "Removed test reports"
    fi
    
    # Remove pytest cache
    if [ -d ".pytest_cache" ]; then
        rm -rf .pytest_cache
        print_info "Removed pytest cache"
    fi
    
    print_success "Cleanup complete"
}

# Function to run tests in Docker
run_docker_tests() {
    local pytest_args="$1"
    
    print_info "Running tests in Docker containers..."
    
    # Check if host API is running
    if curl -s http://localhost:8088/health > /dev/null 2>&1; then
        print_success "Found API running on host (localhost:8088)"
        print_info "Tests will run against the host API"
        print_info "Building test container..."
    else
        print_warning "No API found on host:8088"
        print_info "Starting API container as well..."
        export COMPOSE_PROFILES=with-api
    fi
    
    cd "$SCRIPT_DIR"
    
    # Set pytest command with arguments
    export PYTEST_ARGS="$pytest_args"
    
    # Build and start services
    docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit --exit-code-from tests
    
    local exit_code=$?
    
    # Clean up containers
    print_info "Stopping containers..."
    docker-compose -f docker-compose.test.yml down
    
    if [ $exit_code -eq 0 ]; then
        print_success "All tests passed!"
        if [ -f "reports/test-report.html" ]; then
            print_info "Test report: $SCRIPT_DIR/reports/test-report.html"
        fi
    else
        print_error "Tests failed with exit code $exit_code"
    fi
    
    return $exit_code
}

# Function to run tests locally
run_local_tests() {
    local pytest_args="$1"
    
    print_info "Running tests locally..."
    
    # Check if API is running
    if ! curl -s http://localhost:8088/health > /dev/null 2>&1; then
        print_error "API is not running at http://localhost:8088"
        print_info "Start the API first with: ./scripts/start.sh"
        exit 1
    fi
    
    print_success "API is running"
    
    cd "$SCRIPT_DIR"
    
    # Check if venv exists
    if [ ! -d "venv" ]; then
        print_warning "Virtual environment not found, creating..."
        python3 -m venv venv
    fi
    
    # Activate venv and install dependencies
    source venv/bin/activate
    pip install -q -r requirements.txt
    
    # Set environment variables for local testing
    export API_HOST=localhost
    export API_PORT=8088
    
    # Run pytest
    mkdir -p reports
    pytest $test_args
    
    local exit_code=$?
    
    deactivate
    
    if [ $exit_code -eq 0 ]; then
        print_success "All tests passed!"
    else
        print_error "Tests failed"
    fi
    
    return $exit_code
}

# Parse command line arguments
MODE="docker"
PYTEST_ARGS="-v"
STOP_ON_FAILURE=true

while [[ $# -gt 0 ]]; do
    case $1 in
        --docker)
            MODE="docker"
            shift
            ;;
        --local)
            MODE="local"
            shift
            ;;
        --smoke)
            PYTEST_ARGS="$PYTEST_ARGS -m smoke"
            shift
            ;;
        --integration)
            PYTEST_ARGS="$PYTEST_ARGS -m integration"
            shift
            ;;
        --coverage)
            PYTEST_ARGS="$PYTEST_ARGS --cov --cov-report=html"
            shift
            ;;
        --run-to-done)
            STOP_ON_FAILURE=false
            print_info "Will run all tests to completion (ignoring -x flag)"
            shift
            ;;
        --clean)
            cleanup
            exit 0
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Override pytest.ini's -x flag if --run-to-done was specified
if [ "$STOP_ON_FAILURE" = false ]; then
    PYTEST_ARGS="$PYTEST_ARGS --override-ini=addopts=-v"
fi

# Print header
echo ""
echo "========================================"
echo "  gTTS API Test Suite"
echo "========================================"
echo "Mode: $MODE"
if [ "$STOP_ON_FAILURE" = true ]; then
    echo "Behavior: Stop on first failure"
else
    echo "Behavior: Run all tests to completion"
fi
echo "========================================"
echo ""

# Run tests based on mode
if [ "$MODE" = "docker" ]; then
    run_docker_tests "$PYTEST_ARGS"
else
    run_local_tests "$PYTEST_ARGS"
fi

exit $?


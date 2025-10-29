#!/bin/bash

# Container and image configuration
CONTAINER_NAME="gtts-fastapi"
IMAGE_NAME="gtts-fastapi"
IMAGE_TAG="latest"
# Port can be configured via environment variable or defaults to 8088
PORT="${GTTS_PORT:-8088}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Function to check if a port is in use
check_port() {
    local port=$1
    
    # Check if the port is in use
    if lsof -Pi :${port} -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to show what's using a port
show_port_usage() {
    local port=$1
    
    print_info "Checking what is using port ${port}:"
    echo ""
    lsof -Pi :${port} -sTCP:LISTEN
    echo ""
    
    # Get the process details
    local pid=$(lsof -Pi :${port} -sTCP:LISTEN -t 2>/dev/null | head -1)
    if [ -n "$pid" ]; then
        print_info "Process ID: ${pid}"
        print_info "To kill this process, run: kill ${pid}"
        print_info "Or to force kill: kill -9 ${pid}"
    fi
}

# Function to build the Docker image
build() {
    print_info "Building Docker image: ${IMAGE_NAME}:${IMAGE_TAG}"
    
    cd "$(dirname "$0")/.." || exit 1
    
    if docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" .; then
        print_success "Docker image built successfully!"
        docker images | grep "${IMAGE_NAME}"
    else
        print_error "Failed to build Docker image"
        exit 1
    fi
}

# Function to start the container
start() {
    print_info "Starting container: ${CONTAINER_NAME}"
    
    # Check if the Docker image exists, if not, build it
    if ! docker images --format '{{.Repository}}:{{.Tag}}' | grep -q "^${IMAGE_NAME}:${IMAGE_TAG}$"; then
        print_warning "Docker image ${IMAGE_NAME}:${IMAGE_TAG} not found"
        print_info "Building image first..."
        echo ""
        build
        echo ""
        print_info "Continuing with container startup..."
    fi
    
    # Check if port is already in use (unless it's our own container)
    if check_port ${PORT}; then
        # Check if it's our container using the port
        local container_using_port=$(docker ps --filter "publish=${PORT}" --format "{{.Names}}" 2>/dev/null | grep "^${CONTAINER_NAME}$")
        
        if [ "$container_using_port" == "${CONTAINER_NAME}" ]; then
            print_warning "Container ${CONTAINER_NAME} is already running on port ${PORT}"
            docker ps | grep "${CONTAINER_NAME}"
            return 0
        else
            print_error "Port ${PORT} is already in use by another process!"
            echo ""
            show_port_usage ${PORT}
            echo ""
            print_error "Please free up port ${PORT} before starting the container"
            print_info "Options:"
            print_info "  1. Stop the process using the port"
            print_info "  2. Change the PORT variable in this script"
            print_info "  3. Use: docker run -p <different-port>:8000 ..."
            exit 1
        fi
    fi
    
    # Check if container already exists
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        print_warning "Container ${CONTAINER_NAME} already exists"
        
        # Check if it's running
        if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
            print_warning "Container is already running"
            docker ps | grep "${CONTAINER_NAME}"
            return 0
        else
            print_info "Starting existing container"
            docker start "${CONTAINER_NAME}"
        fi
    else
        print_info "Creating and starting new container"
        docker run -d \
            --name "${CONTAINER_NAME}" \
            -p "${PORT}:8000" \
            --restart unless-stopped \
            "${IMAGE_NAME}:${IMAGE_TAG}"
    fi
    
    if [ $? -eq 0 ]; then
        print_success "Container started successfully!"
        print_info "Container is running at http://localhost:${PORT}"
        print_info "API docs available at http://localhost:${PORT}/docs"
        echo ""
        docker ps | grep "${CONTAINER_NAME}"
    else
        print_error "Failed to start container"
        exit 1
    fi
}

# Function to stop the container
stop() {
    print_info "Stopping container: ${CONTAINER_NAME}"
    
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        docker stop "${CONTAINER_NAME}"
        print_success "Container stopped successfully!"
    else
        print_warning "Container ${CONTAINER_NAME} is not running"
    fi
}

# Function to view container logs
logs() {
    print_info "Showing logs for container: ${CONTAINER_NAME}"
    
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        docker logs -f "${CONTAINER_NAME}"
    else
        print_error "Container ${CONTAINER_NAME} does not exist"
        exit 1
    fi
}

# Function to restart the container
restart() {
    print_info "Restarting container: ${CONTAINER_NAME}"
    stop
    start
}

# Function to completely clean up everything
clean() {
    print_warning "This will remove ALL traces of the container and image!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Clean cancelled"
        return 0
    fi
    
    print_info "Starting cleanup..."
    
    # Stop container if running
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        print_info "Stopping container..."
        docker stop "${CONTAINER_NAME}"
    fi
    
    # Remove container
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        print_info "Removing container..."
        docker rm "${CONTAINER_NAME}"
        print_success "Container removed"
    fi
    
    # Remove image
    if docker images --format '{{.Repository}}:{{.Tag}}' | grep -q "^${IMAGE_NAME}:${IMAGE_TAG}$"; then
        print_info "Removing image..."
        docker rmi "${IMAGE_NAME}:${IMAGE_TAG}"
        print_success "Image removed"
    fi
    
    # Remove dangling images
    print_info "Removing dangling images..."
    docker image prune -f
    
    # Remove unused volumes
    print_info "Removing unused volumes..."
    docker volume prune -f
    
    print_success "Cleanup complete! All traces removed."
}

# Function to show container status
status() {
    print_info "Container status:"
    echo ""
    
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        docker ps -a | grep "${CONTAINER_NAME}" || true
        echo ""
        
        if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
            print_success "Container is RUNNING"
            print_info "Accessible at http://localhost:${PORT}"
        else
            print_warning "Container exists but is NOT running"
        fi
    else
        print_warning "Container does not exist"
    fi
    
    echo ""
    print_info "Image status:"
    docker images | grep "${IMAGE_NAME}" || print_warning "Image does not exist"
    
    echo ""
    print_info "Port status:"
    if check_port ${PORT}; then
        print_warning "Port ${PORT} is IN USE"
        show_port_usage ${PORT}
    else
        print_success "Port ${PORT} is FREE"
    fi
}

# Function to rebuild (clean build)
rebuild() {
    print_info "Rebuilding container from scratch..."
    clean
    build
    start
}

# Function to show help
show_help() {
    echo "Usage: $0 {build|start|stop|restart|logs|status|clean|rebuild}"
    echo ""
    echo "Commands:"
    echo "  build    - Build the Docker image"
    echo "  start    - Start the container (auto-builds image if not found)"
    echo "  stop     - Stop the container"
    echo "  restart  - Restart the container"
    echo "  logs     - Show container logs (follow mode)"
    echo "  status   - Show container and image status"
    echo "  clean    - Remove ALL traces (container, image, volumes)"
    echo "  rebuild  - Clean, build, and start from scratch"
    echo ""
    echo "Configuration:"
    echo "  Default port: ${PORT}"
    echo "  To change port: export GTTS_PORT=<port> before running this script"
    echo ""
    echo "Examples:"
    echo "  $0 build                    # Build the image"
    echo "  $0 start                    # Start on default port (${PORT})"
    echo "  GTTS_PORT=9000 $0 start     # Start on port 9000"
    echo "  $0 logs                     # View logs"
    echo "  $0 clean                    # Complete cleanup"
}

# Main script logic
case "$1" in
    build)
        build
        ;;
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    logs)
        logs
        ;;
    status)
        status
        ;;
    clean)
        clean
        ;;
    rebuild)
        rebuild
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Invalid command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac


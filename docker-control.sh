#!/bin/bash

# Docker Control Script for P2P Sandbox
# Provides easy management of the containerized application

PROJECT_ROOT="/mnt/d/Projects/P2P-V2"
LOG_DIR="$PROJECT_ROOT/logs"
ENV_FILE="$PROJECT_ROOT/.env.docker"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_status "$RED" "❌ Docker is not running. Please start Docker Desktop."
        exit 1
    fi
}

# Function to stop any local services that might conflict
stop_local_services() {
    print_status "$YELLOW" "🛑 Stopping any local services on conflicting ports..."
    
    # Kill processes on common ports
    for port in 5173 8000 5432 27017 3567; do
        PID=$(lsof -ti :$port 2>/dev/null)
        if [ ! -z "$PID" ]; then
            kill $PID 2>/dev/null
            print_status "$GREEN" "  ✅ Stopped process on port $port"
        fi
    done
}

# Function to start all services
start_services() {
    print_status "$BLUE" "🚀 Starting P2P Sandbox..."
    
    check_docker
    stop_local_services
    
    # Load environment variables
    if [ -f "$ENV_FILE" ]; then
        print_status "$GREEN" "📋 Loading environment from .env.docker"
        export $(cat "$ENV_FILE" | grep -v '^#' | xargs)
    else
        print_status "$YELLOW" "⚠️  No .env.docker file found, using defaults"
    fi
    
    # Change to project root
    cd "$PROJECT_ROOT"
    
    # Start services with docker-compose
    print_status "$BLUE" "🔧 Building and starting containers..."
    docker-compose up -d --build
    
    # Wait for services to be ready
    print_status "$YELLOW" "⏳ Waiting for services to initialize..."
    sleep 10
    
    # Check service health
    print_status "$BLUE" "🔍 Checking service status..."
    echo ""
    
    # Check each service
    for service in postgres mongodb supertokens backend frontend; do
        if docker-compose ps | grep -q "${service}.*Up"; then
            print_status "$GREEN" "  ✅ $service is running"
        else
            print_status "$RED" "  ❌ $service failed to start"
            echo "     Logs:"
            docker-compose logs --tail=10 $service 2>&1 | sed 's/^/       /'
        fi
    done
    
    echo ""
    
    # Test endpoints
    print_status "$BLUE" "🧪 Testing endpoints..."
    
    # Test backend health
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_status "$GREEN" "  ✅ Backend API is healthy"
    else
        print_status "$YELLOW" "  ⏳ Backend API is starting up..."
    fi
    
    # Test frontend
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        print_status "$GREEN" "  ✅ Frontend is accessible"
    else
        print_status "$YELLOW" "  ⏳ Frontend is starting up..."
    fi
    
    echo ""
    print_status "$GREEN" "🎉 P2P Sandbox is ready!"
    print_status "$BLUE" "   Frontend: http://localhost:5173"
    print_status "$BLUE" "   Backend API: http://localhost:8000"
    print_status "$BLUE" "   API Documentation: http://localhost:8000/docs"
    echo ""
    print_status "$YELLOW" "💡 Tip: Use './docker-control.sh logs' to view logs"
}

# Function to stop all services
stop_services() {
    print_status "$YELLOW" "🛑 Stopping P2P Sandbox..."
    
    cd "$PROJECT_ROOT"
    docker-compose down
    
    print_status "$GREEN" "✅ All services stopped"
}

# Function to restart services
restart_services() {
    stop_services
    echo ""
    sleep 2
    start_services
}

# Function to show service status
status_services() {
    print_status "$BLUE" "📊 P2P Sandbox Status"
    echo ""
    
    cd "$PROJECT_ROOT"
    docker-compose ps
    
    echo ""
    print_status "$BLUE" "🔌 Port Status:"
    echo "  Frontend: http://localhost:5173"
    echo "  Backend: http://localhost:8000"
    echo "  PostgreSQL: localhost:5432"
    echo "  MongoDB: localhost:27017"
      echo "  SuperTokens: localhost:3567"
}

# Function to show logs
logs_services() {
    local service=$1
    
    cd "$PROJECT_ROOT"
    
    if [ -z "$service" ]; then
        print_status "$BLUE" "📜 Showing logs for all services (Ctrl+C to exit)..."
        docker-compose logs -f --tail=100
    else
        print_status "$BLUE" "📜 Showing logs for $service (Ctrl+C to exit)..."
        docker-compose logs -f --tail=100 $service
    fi
}

# Function to clean up everything
clean_all() {
    print_status "$RED" "🧹 Cleaning up P2P Sandbox..."
    print_status "$YELLOW" "⚠️  This will remove all containers, volumes, and networks!"
    
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd "$PROJECT_ROOT"
        docker-compose down -v --remove-orphans
        print_status "$GREEN" "✅ Cleanup complete"
    else
        print_status "$YELLOW" "❌ Cleanup cancelled"
    fi
}

# Function to run commands in a container
exec_service() {
    local service=$1
    shift
    local command=$@
    
    if [ -z "$service" ]; then
        print_status "$RED" "❌ Please specify a service name"
        echo "Usage: $0 exec <service> <command>"
        echo "Example: $0 exec backend python -m pytest"
        exit 1
    fi
    
    cd "$PROJECT_ROOT"
    docker-compose exec $service $command
}

# Function to rebuild a specific service
rebuild_service() {
    local service=$1
    
    if [ -z "$service" ]; then
        print_status "$YELLOW" "🔨 Rebuilding all services..."
        cd "$PROJECT_ROOT"
        docker-compose build --no-cache
    else
        print_status "$YELLOW" "🔨 Rebuilding $service..."
        cd "$PROJECT_ROOT"
        docker-compose build --no-cache $service
    fi
    
    print_status "$GREEN" "✅ Rebuild complete"
}

# Main command handler
case "$1" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        status_services
        ;;
    logs)
        logs_services $2
        ;;
    clean)
        clean_all
        ;;
    exec)
        shift
        exec_service $@
        ;;
    rebuild)
        rebuild_service $2
        ;;
    *)
        print_status "$BLUE" "P2P Sandbox Docker Control"
        echo ""
        echo "Usage: $0 {start|stop|restart|status|logs|clean|exec|rebuild}"
        echo ""
        echo "Commands:"
        echo "  start          - Start all services"
        echo "  stop           - Stop all services"
        echo "  restart        - Restart all services"
        echo "  status         - Show service status"
        echo "  logs [service] - Show logs (all services or specific)"
        echo "  clean          - Remove all containers and volumes"
        echo "  exec <service> <cmd> - Run command in a container"
        echo "  rebuild [service]    - Rebuild services (all or specific)"
        echo ""
        echo "Examples:"
        echo "  $0 start"
        echo "  $0 logs backend"
        echo "  $0 exec backend python -m pytest"
        echo "  $0 rebuild frontend"
        exit 1
        ;;
esac
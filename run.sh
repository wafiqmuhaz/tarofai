#!/bin/bash

# ========================================
# Tarofa - Run Script
# Islamic AI Search Engine Orchestrator
# ========================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# PID files
PID_DIR="$PROJECT_ROOT/.pids"
BACKEND_PID="$PID_DIR/backend.pid"
AGENT_PID="$PID_DIR/agent.pid"
FRONTEND_PID="$PID_DIR/frontend.pid"

# Log files
LOG_DIR="$PROJECT_ROOT/logs"

# Print colored message
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Print banner
print_banner() {
    echo ""
    print_message $CYAN "╔═══════════════════════════════════════════╗"
    print_message $CYAN "║           🕌 TAROFA 🕌                    ║"
    print_message $CYAN "║    Islamic AI Search Engine               ║"
    print_message $CYAN "╚═══════════════════════════════════════════╝"
    echo ""
}

# Create directories
setup_dirs() {
    mkdir -p "$PID_DIR"
    mkdir -p "$LOG_DIR"
    mkdir -p "$PROJECT_ROOT/serverData/cache"
    mkdir -p "$PROJECT_ROOT/serverData/scraped"
}

# Check if command exists
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_message $RED "Error: $1 is not installed"
        exit 1
    fi
}

# Copy env file if not exists
setup_env() {
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        if [ -f "$PROJECT_ROOT/.env.example" ]; then
            cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
            print_message $YELLOW "Created .env from .env.example"
        fi
    fi
}

# Create virtual environment if needed
setup_venv() {
    local dir=$1
    local venv_path="$dir/venv"
    
    if [ ! -d "$venv_path" ]; then
        print_message $YELLOW "Creating virtual environment in $dir..."
        python3 -m venv "$venv_path"
    fi
    
    # Install dependencies
    if [ -f "$dir/requirements.txt" ]; then
        print_message $BLUE "Installing dependencies for $(basename $dir)..."
        source "$venv_path/bin/activate"
        pip install -q -r "$dir/requirements.txt"
        deactivate
    fi
}

# Setup Node.js dependencies
setup_node() {
    local dir=$1
    
    if [ -f "$dir/package.json" ]; then
        if [ ! -d "$dir/node_modules" ]; then
            print_message $BLUE "Installing npm dependencies for $(basename $dir)..."
            cd "$dir"
            npm install --silent
            cd "$PROJECT_ROOT"
        fi
    fi
}

# Prefix output with service name
prefix_output() {
    local prefix=$1
    local color=$2
    while IFS= read -r line; do
        echo -e "${color}[${prefix}]${NC} $line"
    done
}

# Stop a service by PID file
stop_service() {
    local pid_file=$1
    local name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            kill $pid 2>/dev/null || true
            print_message $YELLOW "Stopped $name (PID: $pid)"
        fi
        rm -f "$pid_file"
    fi
}

# Stop all services
stop_all() {
    print_message $YELLOW "Stopping all services..."
    
    stop_service "$FRONTEND_PID" "Frontend"
    stop_service "$AGENT_PID" "AI Agent"
    stop_service "$BACKEND_PID" "Backend"
    
    # Kill any remaining processes on our ports
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    pkill -f "uvicorn agent.main:app" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    
    print_message $GREEN "All services stopped"
}

# Cleanup on exit
cleanup() {
    echo ""
    print_message $YELLOW "Shutting down..."
    stop_all
    exit 0
}

# Full startup with realtime logs
startup_realtime() {
    print_banner
    
    print_message $BLUE "Setting up environment..."
    setup_dirs
    setup_env
    
    # Check requirements
    check_command python3
    check_command npm
    
    # Setup virtual environments
    setup_venv "$PROJECT_ROOT/backend"
    setup_venv "$PROJECT_ROOT/ai-agent"
    
    # Setup Node.js
    setup_node "$PROJECT_ROOT/frontend"
    
    echo ""
    print_message $GREEN "═══════════════════════════════════════════"
    print_message $GREEN "  Starting all services with realtime logs"
    print_message $GREEN "═══════════════════════════════════════════"
    print_message $CYAN "  Frontend:  http://localhost:5173"
    print_message $CYAN "  Backend:   http://localhost:8000"
    print_message $CYAN "  AI Agent:  http://localhost:3001"
    print_message $CYAN "  API Docs:  http://localhost:8000/docs"
    echo ""
    print_message $YELLOW "  Press Ctrl+C to stop all services"
    echo ""
    print_message $BLUE "═══════════════════════════════════════════"
    echo ""
    
    # Set trap for cleanup
    trap cleanup SIGINT SIGTERM
    
    # Export env vars
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
    
    # Start Backend
    (
        cd "$PROJECT_ROOT/backend"
        source venv/bin/activate
        python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload 2>&1 | prefix_output "BACKEND" "$GREEN"
    ) &
    BACKEND_PROC=$!
    echo $BACKEND_PROC > "$BACKEND_PID"
    
    # Start AI Agent
    (
        cd "$PROJECT_ROOT/ai-agent"
        source venv/bin/activate
        python -m uvicorn agent.main:app --host 0.0.0.0 --port 3001 --reload 2>&1 | prefix_output "AGENT" "$MAGENTA"
    ) &
    AGENT_PROC=$!
    echo $AGENT_PROC > "$AGENT_PID"
    
    # Start Frontend
    (
        cd "$PROJECT_ROOT/frontend"
        npm run dev 2>&1 | prefix_output "FRONTEND" "$CYAN"
    ) &
    FRONTEND_PROC=$!
    echo $FRONTEND_PROC > "$FRONTEND_PID"
    
    # Wait for all processes
    wait
}

# Background startup (original mode)
startup_background() {
    print_banner
    
    print_message $BLUE "Setting up environment..."
    setup_dirs
    setup_env
    
    # Check requirements
    check_command python3
    check_command npm
    check_command curl
    
    # Setup virtual environments
    setup_venv "$PROJECT_ROOT/backend"
    setup_venv "$PROJECT_ROOT/ai-agent"
    
    # Setup Node.js
    setup_node "$PROJECT_ROOT/frontend"
    
    echo ""
    print_message $BLUE "Starting services in background..."
    echo ""
    
    # Export env vars
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
    
    # Start Backend
    print_message $GREEN "Starting Backend (port 8000)..."
    cd "$PROJECT_ROOT/backend"
    source venv/bin/activate
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > "$LOG_DIR/backend.log" 2>&1 &
    echo $! > "$BACKEND_PID"
    deactivate
    cd "$PROJECT_ROOT"
    print_message $GREEN "✓ Backend started (PID: $(cat $BACKEND_PID))"
    
    # Start AI Agent
    print_message $GREEN "Starting AI Agent (port 3001)..."
    cd "$PROJECT_ROOT/ai-agent"
    source venv/bin/activate
    python -m uvicorn agent.main:app --host 0.0.0.0 --port 3001 > "$LOG_DIR/agent.log" 2>&1 &
    echo $! > "$AGENT_PID"
    deactivate
    cd "$PROJECT_ROOT"
    print_message $GREEN "✓ AI Agent started (PID: $(cat $AGENT_PID))"
    
    # Start Frontend
    print_message $GREEN "Starting Frontend (port 5173)..."
    cd "$PROJECT_ROOT/frontend"
    npm run dev > "$LOG_DIR/frontend.log" 2>&1 &
    echo $! > "$FRONTEND_PID"
    cd "$PROJECT_ROOT"
    print_message $GREEN "✓ Frontend started (PID: $(cat $FRONTEND_PID))"
    
    # Health check with longer wait
    echo ""
    print_message $BLUE "Waiting for services to start..."
    sleep 5
    
    print_message $BLUE "Checking service health..."
    
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_message $GREEN "✓ Backend: OK"
    else
        print_message $RED "✗ Backend: Starting... (check logs/backend.log)"
    fi
    
    if curl -s http://localhost:3001/health > /dev/null 2>&1; then
        print_message $GREEN "✓ AI Agent: OK"
    else
        print_message $RED "✗ AI Agent: Starting... (check logs/agent.log)"
    fi
    
    if [ -f "$FRONTEND_PID" ] && ps -p $(cat "$FRONTEND_PID") > /dev/null 2>&1; then
        print_message $GREEN "✓ Frontend: Running"
    else
        print_message $RED "✗ Frontend: FAILED"
    fi
    
    echo ""
    print_message $GREEN "═══════════════════════════════════════════"
    print_message $GREEN "  Tarofa is running!"
    print_message $GREEN "═══════════════════════════════════════════"
    print_message $CYAN "  Frontend:  http://localhost:5173"
    print_message $CYAN "  Backend:   http://localhost:8000"
    print_message $CYAN "  AI Agent:  http://localhost:3001"
    print_message $CYAN "  API Docs:  http://localhost:8000/docs"
    echo ""
    print_message $YELLOW "  Use './run.sh down' to stop all services"
    print_message $YELLOW "  Use './run.sh logs' to view logs"
    echo ""
}

# View logs
view_logs() {
    local service=$1
    
    case $service in
        backend)
            tail -f "$LOG_DIR/backend.log"
            ;;
        agent)
            tail -f "$LOG_DIR/agent.log"
            ;;
        frontend)
            tail -f "$LOG_DIR/frontend.log"
            ;;
        *)
            tail -f "$LOG_DIR/backend.log" "$LOG_DIR/agent.log" "$LOG_DIR/frontend.log"
            ;;
    esac
}

# Main command handler
case "${1:-up}" in
    up|start)
        startup_realtime
        ;;
    bg|background)
        startup_background
        ;;
    down|stop)
        print_banner
        stop_all
        ;;
    restart)
        print_banner
        stop_all
        sleep 2
        startup_realtime
        ;;
    logs)
        view_logs "${2:-all}"
        ;;
    status|health)
        print_banner
        print_message $BLUE "Checking service health..."
        
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            print_message $GREEN "✓ Backend: OK"
        else
            print_message $RED "✗ Backend: NOT RUNNING"
        fi
        
        if curl -s http://localhost:3001/health > /dev/null 2>&1; then
            print_message $GREEN "✓ AI Agent: OK"
        else
            print_message $RED "✗ AI Agent: NOT RUNNING"
        fi
        
        if [ -f "$FRONTEND_PID" ] && ps -p $(cat "$FRONTEND_PID") > /dev/null 2>&1; then
            print_message $GREEN "✓ Frontend: Running"
        else
            print_message $RED "✗ Frontend: NOT RUNNING"
        fi
        ;;
    *)
        echo "Usage: ./run.sh [command]"
        echo ""
        echo "Commands:"
        echo "  up, start    Start all services with realtime logs (default)"
        echo "  bg           Start all services in background"
        echo "  down, stop   Stop all services"
        echo "  restart      Restart all services"
        echo "  logs [svc]   View logs (backend|agent|frontend|all)"
        echo "  status       Check service health"
        ;;
esac

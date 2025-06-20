#!/bin/bash
# Development and deployment helper script for Binance Futures Testnet Bot
# Usage: ./dev.sh [command]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Helper functions
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Commands
setup() {
    print_header "Setting up development environment"
    
    # Check if uv is installed
    if ! command -v uv &> /dev/null; then
        print_warning "uv not found. Installing with pip..."
        pip install uv
    fi
    
    # Install dependencies
    echo "Installing dependencies with uv..."
    uv sync
    
    # Create logs directory
    mkdir -p logs
    
    # Check for .env file
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from example..."
        cp .env.example .env
        print_warning "Please edit .env with your testnet credentials"
    fi
    
    print_success "Setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Edit .env with your Binance Testnet credentials"
    echo "2. Run: ./dev.sh demo  # Test initialization"
    echo "3. Run: ./dev.sh test  # Run tests"
    echo "4. Run: ./dev.sh start # Start the bot"
}

demo() {
    print_header "Running initialization demo"
    uv run python demo_initialization.py
}

test() {
    print_header "Running tests"
    
    # Unit tests
    echo "Running unit tests..."
    uv run python -m pytest tests/ -v
    
    # Component integration tests
    echo ""
    echo "Running component integration tests..."
    uv run python test_bot_components.py
}

start() {
    print_header "Starting bot in demo mode"
    uv run python main.py --mode demo
}

start_live() {
    print_header "Starting bot in live mode (TESTNET)"
    print_warning "This will connect to Binance Testnet and place actual orders!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        uv run python main.py --mode live
    else
        print_warning "Cancelled by user"
    fi
}

backtest() {
    print_header "Running backtest"
    uv run python run_backtest.py
}

analyze() {
    print_header "Analyzing results"
    uv run python analyze_results.py
}

clean() {
    print_header "Cleaning up"
    
    # Remove cache
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    # Remove old logs (older than 7 days)
    if [ -d "logs" ]; then
        find logs/ -name "*.log" -mtime +7 -delete 2>/dev/null || true
    fi
    
    print_success "Cleanup complete"
}

logs() {
    print_header "Viewing recent logs"
    
    if [ -d "logs" ]; then
        latest_log=$(find logs/ -name "*.log" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2)
        if [ -n "$latest_log" ]; then
            echo "Showing: $latest_log"
            echo "================================"
            tail -n 50 "$latest_log"
        else
            print_warning "No log files found"
        fi
    else
        print_warning "Logs directory not found"
    fi
}

docker_build() {
    print_header "Building Docker image"
    
    # Navigate to project root (where Dockerfile should be)
    cd ../../../
    
    docker build -t nautilus-binance-testnet -f Dockerfile .
    
    print_success "Docker image built successfully"
}

docker_run() {
    print_header "Running bot in Docker"
    
    # Check if image exists
    if ! docker image inspect nautilus-binance-testnet &> /dev/null; then
        print_warning "Docker image not found. Building..."
        docker_build
    fi
    
    docker run -it --rm \
        -v "$(pwd):/workspace/bots/binance/testnet" \
        -w /workspace/bots/binance/testnet \
        nautilus-binance-testnet \
        bash -c "uv run python main.py --mode demo"
}

help() {
    echo "Binance Futures Testnet Bot - Development Helper"
    echo ""
    echo "Usage: ./dev.sh [command]"
    echo ""
    echo "Commands:"
    echo "  setup         Setup development environment"
    echo "  demo          Run initialization demo"
    echo "  test          Run all tests"
    echo "  start         Start bot in demo mode"
    echo "  start-live    Start bot in live mode (testnet)"
    echo "  backtest      Run backtest"
    echo "  analyze       Analyze results"
    echo "  clean         Clean up cache and old logs"
    echo "  logs          View recent logs"
    echo "  docker-build  Build Docker image"
    echo "  docker-run    Run bot in Docker"
    echo "  help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./dev.sh setup     # First time setup"
    echo "  ./dev.sh demo      # Test configuration"
    echo "  ./dev.sh test      # Run all tests"
    echo "  ./dev.sh start     # Start trading (demo mode)"
}

# Main script logic
case "$1" in
    setup)
        setup
        ;;
    demo)
        demo
        ;;
    test)
        test
        ;;
    start)
        start
        ;;
    start-live)
        start_live
        ;;
    backtest)
        backtest
        ;;
    analyze)
        analyze
        ;;
    clean)
        clean
        ;;
    logs)
        logs
        ;;
    docker-build)
        docker_build
        ;;
    docker-run)
        docker_run
        ;;
    help|"")
        help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        help
        exit 1
        ;;
esac

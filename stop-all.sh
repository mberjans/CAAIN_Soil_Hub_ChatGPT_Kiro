#!/bin/bash

# AFAS Services Stop Script
# Stops all running microservices

echo "🛑 Stopping AFAS Development Environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Kill all service processes
if [ -f .pids ]; then
    while read pid; do
        if kill $pid 2>/dev/null; then
            echo "Stopped process $pid"
        else
            echo "Process $pid was not running"
        fi
    done < .pids
    rm .pids
    print_success "All AFAS services stopped"
else
    print_error "No PID file found. Services may not be running."
fi

# Optional: Stop databases (uncomment if you want to stop them too)
# if [[ "$OSTYPE" == "darwin"* ]]; then
#     brew services stop postgresql@15
#     brew services stop mongodb-community@7.0
#     brew services stop redis
#     print_success "Database services stopped"
# fi

echo "✅ AFAS development environment stopped"
#!/bin/bash

# AFAS Services Start Script
# Starts all microservices for local development

set -e

echo "🚀 Starting AFAS Development Environment..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Check if databases are running
print_status "Checking database services..."

# Start databases if not running (macOS with Homebrew)
if [[ "$OSTYPE" == "darwin"* ]]; then
    brew services start postgresql@15 2>/dev/null || true
    brew services start mongodb-community@7.0 2>/dev/null || true
    brew services start redis 2>/dev/null || true
fi

# Wait for databases to start
sleep 3

# Start services in background
print_status "Starting AFAS microservices..."

# Question Router (Python)
cd services/question-router
source venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload &
QUESTION_ROUTER_PID=$!
print_status "Question Router started on port 8000 (PID: $QUESTION_ROUTER_PID)"
deactivate

# Recommendation Engine (Python)
cd ../recommendation-engine
source venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload &
RECOMMENDATION_ENGINE_PID=$!
print_status "Recommendation Engine started on port 8001 (PID: $RECOMMENDATION_ENGINE_PID)"
deactivate

# AI Agent (Python)
cd ../ai-agent
source venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 8002 --reload &
AI_AGENT_PID=$!
print_status "AI Agent started on port 8002 (PID: $AI_AGENT_PID)"
deactivate

# Data Integration (Python)
cd ../data-integration
source venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 8003 --reload &
DATA_INTEGRATION_PID=$!
print_status "Data Integration started on port 8003 (PID: $DATA_INTEGRATION_PID)"
deactivate

# Image Analysis (Python)
cd ../image-analysis
source venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 8004 --reload &
IMAGE_ANALYSIS_PID=$!
print_status "Image Analysis started on port 8004 (PID: $IMAGE_ANALYSIS_PID)"
deactivate

# User Management (Python)
cd ../user-management
source venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 8005 --reload &
USER_MANAGEMENT_PID=$!
print_status "User Management started on port 8005 (PID: $USER_MANAGEMENT_PID)"
deactivate

# Cover Crop Selection (Python)
cd ../cover-crop-selection
source venv/bin/activate 2>/dev/null || python -m venv venv && source venv/bin/activate
pip install -r requirements.txt >/dev/null 2>&1 || true
uvicorn src.main:app --host 0.0.0.0 --port 8006 --reload &
COVER_CROP_PID=$!
print_status "Cover Crop Selection started on port 8006 (PID: $COVER_CROP_PID)"
deactivate

# Frontend (Python)
cd ../frontend
source venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 3000 --reload &
FRONTEND_PID=$!
print_status "Frontend started on port 3000 (PID: $FRONTEND_PID)"
deactivate

cd ../..

# Save PIDs for cleanup
echo $QUESTION_ROUTER_PID > .pids
echo $RECOMMENDATION_ENGINE_PID >> .pids
echo $AI_AGENT_PID >> .pids
echo $DATA_INTEGRATION_PID >> .pids
echo $IMAGE_ANALYSIS_PID >> .pids
echo $USER_MANAGEMENT_PID >> .pids
echo $COVER_CROP_PID >> .pids
echo $FRONTEND_PID >> .pids

print_success "🎉 All AFAS services are running!"
echo ""
echo "📍 Service Endpoints:"
echo "  • Question Router:      http://localhost:8000/health"
echo "  • Recommendation Engine: http://localhost:8001/health"
echo "  • AI Agent:             http://localhost:8002/health"
echo "  • Data Integration:     http://localhost:8003/health"
echo "  • Image Analysis:       http://localhost:8004/health"
echo "  • User Management:      http://localhost:8005/health"
echo "  • Cover Crop Selection:  http://localhost:8006/health"
echo "  • Frontend:             http://localhost:3000"
echo ""
echo "🛑 To stop all services, run: ./stop-all.sh"
echo "📊 To check service status: curl http://localhost:8000/health"
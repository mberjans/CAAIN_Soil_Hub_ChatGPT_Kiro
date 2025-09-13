#!/bin/bash

# AFAS Services Setup Script
# This script initializes all microservices with their dependencies and basic structure

set -e  # Exit on any error

echo "🔧 Setting up AFAS Microservices..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
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

# All services will be Python-based for consistency

# Setup Python services
setup_python_service() {
    local service_name=$1
    local service_port=$2
    local service_description=$3
    
    print_status "Setting up $service_name..."
    cd services/$service_name
    
    # Create virtual environment if it doesn't exist
    if [ ! -d venv ]; then
        python3.11 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Create requirements.txt
    cat > requirements.txt << EOF
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-dotenv==1.0.0
httpx==0.25.2
aiohttp==3.9.1
redis==5.0.1
psycopg2-binary==2.9.9
sqlalchemy==2.0.23
alembic==1.13.1
pymongo==4.6.0
structlog==23.2.0
prometheus-client==0.19.0
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
EOF
    
    # Install base dependencies
    pip install -r requirements.txt
    
    # Create directory structure
    mkdir -p src/{api,models,services,utils}
    mkdir -p tests/{unit,integration}
    
    # Create main.py
    if [ ! -f src/main.py ]; then
        # Convert service name to uppercase for environment variable
        service_env_name=$(echo "$service_name" | tr '[:lower:]' '[:upper:]' | tr '-' '_')
        
        cat > src/main.py << EOF
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="AFAS $service_name",
    description="$service_description",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {
        "service": "$service_name",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    return {"message": "AFAS $service_name is running"}

if __name__ == "__main__":
    port = int(os.getenv("${service_env_name}_PORT", $service_port))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
EOF
    fi
    
    # Create __init__.py files
    touch src/__init__.py
    touch src/api/__init__.py
    touch src/models/__init__.py
    touch src/services/__init__.py
    touch src/utils/__init__.py
    
    deactivate
    cd ../..
    print_success "$service_name setup completed"
}

# Setup all Python services (including Question Router)
setup_python_service "question-router" 8000 "Routes farmer questions to appropriate processing pipelines"
setup_python_service "recommendation-engine" 8001 "Core agricultural recommendation processing service"
setup_python_service "ai-agent" 8002 "Natural language processing and AI explanation service"
setup_python_service "data-integration" 8003 "External data source integration and management service"
setup_python_service "image-analysis" 8004 "Computer vision for crop deficiency detection service"
setup_python_service "user-management" 8005 "User authentication and profile management service"

# Add specific dependencies for Question Router service
print_status "Adding NLP dependencies to Question Router service..."
cd services/question-router
source venv/bin/activate
pip install spacy nltk scikit-learn
deactivate
cd ../..

# Add specific dependencies for AI Agent service
print_status "Adding OpenRouter integration to AI Agent service..."
cd services/ai-agent
source venv/bin/activate
pip install openai langchain tiktoken
deactivate
cd ../..

# Add specific dependencies for Image Analysis service
print_status "Adding computer vision dependencies to Image Analysis service..."
cd services/image-analysis
source venv/bin/activate
pip install tensorflow torch torchvision opencv-python pillow scikit-image
deactivate
cd ../..

# Add specific dependencies for Recommendation Engine
print_status "Adding ML dependencies to Recommendation Engine service..."
cd services/recommendation-engine
source venv/bin/activate
pip install scikit-learn numpy pandas scipy ortools
deactivate
cd ../..

print_success "🎉 All AFAS microservices have been set up successfully!"
print_status "Services configured:"
echo "  • Question Router (Node.js) - Port 3001"
echo "  • Recommendation Engine (Python) - Port 8001"
echo "  • AI Agent (Python) - Port 8002"
echo "  • Data Integration (Python) - Port 8003"
echo "  • Image Analysis (Python) - Port 8004"
echo "  • User Management (Python) - Port 8005"
# Setup 
Frontend Service (Python with Streamlit or FastAPI + Jinja2)
print_status "Setting up Frontend service with Python..."
cd services/frontend

# Create virtual environment if it doesn't exist
if [ ! -d venv ]; then
    python3.11 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Create requirements.txt for frontend
cat > requirements.txt << EOF
fastapi==0.104.1
uvicorn[standard]==0.24.0
jinja2==3.1.2
python-multipart==0.0.6
aiofiles==23.2.1
streamlit==1.28.1
plotly==5.17.0
pandas==2.1.3
requests==2.31.0
python-dotenv==1.0.0
EOF

# Install dependencies
pip install -r requirements.txt

# Create directory structure
mkdir -p src/{templates,static/{css,js,images},components}
mkdir -p tests

# Create main.py for FastAPI + Jinja2 option
if [ ! -f src/main.py ]; then
    cat > src/main.py << EOF
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="AFAS Frontend",
    description="Autonomous Farm Advisory System Web Interface",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# Templates
templates = Jinja2Templates(directory="src/templates")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/health")
async def health_check():
    return {
        "service": "frontend",
        "status": "healthy",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    port = int(os.getenv("FRONTEND_PORT", 3000))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
EOF
fi

# Create streamlit_app.py for Streamlit option
if [ ! -f src/streamlit_app.py ]; then
    cat > src/streamlit_app.py << EOF
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="AFAS - Farm Advisory System",
    page_icon="🌱",
    layout="wide"
)

# Main dashboard
st.title("🌱 Autonomous Farm Advisory System")
st.markdown("Get personalized agricultural recommendations based on your farm data")

# Sidebar for farm information
with st.sidebar:
    st.header("Farm Information")
    farm_name = st.text_input("Farm Name")
    location = st.text_input("Location (City, State)")
    farm_size = st.number_input("Farm Size (acres)", min_value=1, value=100)

# Main content area
col1, col2 = st.columns(2)

with col1:
    st.subheader("Ask a Question")
    question = st.text_area("What would you like to know about your farm?")
    if st.button("Get Recommendation"):
        if question:
            # TODO: Call question router API
            st.success("Question submitted! Processing...")
        else:
            st.error("Please enter a question")

with col2:
    st.subheader("Recent Recommendations")
    # TODO: Display recent recommendations
    st.info("No recent recommendations")

# Farm data input section
st.subheader("Soil Test Data")
col1, col2, col3 = st.columns(3)

with col1:
    ph = st.number_input("Soil pH", min_value=0.0, max_value=14.0, value=6.5, step=0.1)
    
with col2:
    organic_matter = st.number_input("Organic Matter (%)", min_value=0.0, max_value=20.0, value=3.0, step=0.1)
    
with col3:
    phosphorus = st.number_input("Phosphorus (ppm)", min_value=0, value=25)

if st.button("Save Soil Data"):
    st.success("Soil data saved successfully!")
EOF
fi

# Create basic HTML template
mkdir -p src/templates
if [ ! -f src/templates/dashboard.html ]; then
    cat > src/templates/dashboard.html << EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AFAS - Farm Advisory System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-success">
        <div class="container">
            <a class="navbar-brand" href="#">🌱 AFAS</a>
        </div>
    </nav>
    
    <div class="container mt-4">
        <h1>Autonomous Farm Advisory System</h1>
        <p class="lead">Get personalized agricultural recommendations for your farm</p>
        
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Ask a Question</h5>
                    </div>
                    <div class="card-body">
                        <form>
                            <div class="mb-3">
                                <textarea class="form-control" rows="3" placeholder="What would you like to know about your farm?"></textarea>
                            </div>
                            <button type="submit" class="btn btn-success">Get Recommendation</button>
                        </form>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Farm Information</h5>
                    </div>
                    <div class="card-body">
                        <form>
                            <div class="mb-3">
                                <input type="text" class="form-control" placeholder="Farm Name">
                            </div>
                            <div class="mb-3">
                                <input type="text" class="form-control" placeholder="Location">
                            </div>
                            <div class="mb-3">
                                <input type="number" class="form-control" placeholder="Farm Size (acres)">
                            </div>
                            <button type="submit" class="btn btn-primary">Save Information</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
EOF
fi

# Create __init__.py files
touch src/__init__.py

deactivate
cd ../..
print_success "Frontend service setup completed"

print_success "🎉 All AFAS services have been set up with Python!"
print_status "Services configured:"
echo "  • Question Router (Python) - Port 8000"
echo "  • Recommendation Engine (Python) - Port 8001"
echo "  • AI Agent (Python) - Port 8002"
echo "  • Data Integration (Python) - Port 8003"
echo "  • Image Analysis (Python) - Port 8004"
echo "  • User Management (Python) - Port 8005"
echo "  • Frontend (Python) - Port 3000"
echo ""
echo "Frontend Options:"
echo "  • FastAPI + Jinja2: python src/main.py"
echo "  • Streamlit: streamlit run src/streamlit_app.py --server.port 3000"
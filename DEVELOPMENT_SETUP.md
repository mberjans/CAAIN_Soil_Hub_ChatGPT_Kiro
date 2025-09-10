# AFAS Native Development Environment Setup

This guide will help you set up the Autonomous Farm Advisory System (AFAS) for local development without Docker or Kubernetes.

## Prerequisites

### System Requirements
- **Operating System:** macOS, Linux, or Windows with WSL2
- **Memory:** Minimum 16GB RAM (32GB recommended)
- **Storage:** 50GB+ available disk space
- **Network:** Stable internet connection for API integrations

### Required Software

#### 1. Python 3.11+ (Primary Language)
```bash
# macOS with Homebrew
brew install python@3.11

# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv

# Create virtual environment
python3.11 -m venv afas-env
source afas-env/bin/activate  # On Windows: afas-env\Scripts\activate
```

#### 2. PostgreSQL
```bash
# macOS with Homebrew
brew install postgresql@15
brew services start postgresql@15

# Ubuntu/Debian
sudo apt install postgresql-15 postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create AFAS database
sudo -u postgres createuser -s afas_user
sudo -u postgres createdb afas_db -O afas_user
sudo -u postgres psql -c "ALTER USER afas_user PASSWORD 'afas_password';"
```

#### 3. MongoDB
```bash
# macOS with Homebrew
brew tap mongodb/brew
brew install mongodb-community@7.0
brew services start mongodb-community@7.0

# Ubuntu/Debian
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt update
sudo apt install mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod
```

#### 4. Redis
```bash
# macOS with Homebrew
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

# Note: NGINX not needed for local development
# Frontend development server will handle routing via proxy configuration

## Project Structure Setup

### 1. Clone and Initialize Project
```bash
git clone <repository-url> afas
cd afas

# Create directory structure
mkdir -p {services,databases,frontend,infrastructure,logs,config}
mkdir -p services/{question-router,recommendation-engine,ai-agent,data-integration,image-analysis,user-management}
```

### 2. Environment Configuration
```bash
# Create main environment file (if not exists)
# Note: .env already exists with API keys configured
```

### Environment Variables (.env)
```bash
# Database Configuration
DATABASE_URL=postgresql://afas_user:afas_password@localhost:5432/afas_db
MONGODB_URL=mongodb://localhost:27017/afas
REDIS_URL=redis://localhost:6379

# Service Ports (All Python/FastAPI)
QUESTION_ROUTER_PORT=8000
RECOMMENDATION_ENGINE_PORT=8001
AI_AGENT_PORT=8002
DATA_INTEGRATION_PORT=8003
IMAGE_ANALYSIS_PORT=8004
USER_MANAGEMENT_PORT=8005
FRONTEND_PORT=3000

# LLM Integration (OpenRouter - obtain from OpenRouter dashboard)
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_DEFAULT_MODEL=anthropic/claude-3-sonnet

# External API Keys (obtain from respective providers)
WEATHER_API_KEY=your_weather_api_key_here
USDA_API_KEY=your_usda_api_key_here
NOAA_API_KEY=your_noaa_api_key_here

# Security
JWT_SECRET=your_jwt_secret_key_here
ENCRYPTION_KEY=your_encryption_key_here

# Development Settings
NODE_ENV=development
PYTHON_ENV=development
LOG_LEVEL=debug
```

## OpenRouter Configuration

### Setting up OpenRouter for LLM Integration

OpenRouter provides unified access to multiple LLM providers (OpenAI, Anthropic, Meta, etc.) through a single API. This approach offers:

- **Model Flexibility**: Switch between different LLM providers without code changes
- **Cost Optimization**: Choose the most cost-effective model for each use case
- **Fallback Options**: Automatic failover to alternative models if primary is unavailable
- **Rate Limit Management**: Built-in rate limiting and quota management

#### 1. Get OpenRouter API Key
1. Visit [OpenRouter.ai](https://openrouter.ai)
2. Sign up for an account
3. Navigate to the API Keys section
4. Generate a new API key
5. Add the key to your `.env` file

#### 2. Configure Environment Variables
```bash
# Required OpenRouter configuration
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_DEFAULT_MODEL=anthropic/claude-3-sonnet

# Optional: Model preferences for different use cases
OPENROUTER_EXPLANATION_MODEL=anthropic/claude-3-sonnet
OPENROUTER_CLASSIFICATION_MODEL=openai/gpt-4-turbo
OPENROUTER_FALLBACK_MODEL=meta-llama/llama-3-8b-instruct
```

#### 3. Model Selection Guidelines
- **Agricultural Explanations**: `anthropic/claude-3-sonnet` (excellent reasoning)
- **Question Classification**: `openai/gpt-4-turbo` (fast and accurate)
- **Cost-Effective Option**: `meta-llama/llama-3-8b-instruct` (good performance, lower cost)
- **High-Volume Tasks**: `openai/gpt-3.5-turbo` (fast and economical)

## Service Setup

### 1. Question Router Service (Python/FastAPI)
```bash
cd services/question-router

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn psycopg2-binary sqlalchemy redis spacy nltk scikit-learn pydantic httpx structlog pytest python-dotenv

# Create basic structure
mkdir -p src/{api,models,services,utils}
touch src/main.py src/__init__.py
```

### 2. Recommendation Engine (Python)
```bash
cd services/recommendation-engine

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn psycopg2-binary sqlalchemy alembic pymongo redis scikit-learn numpy pandas scipy ortools pydantic httpx aiohttp structlog prometheus-client pytest pytest-asyncio pytest-cov python-dotenv

# Create basic structure
mkdir -p src/{models,services,utils,api}
touch src/main.py src/__init__.py
```

### 3. AI Agent Service (Python)
```bash
cd services/ai-agent

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies (using OpenRouter for LLM access)
pip install fastapi uvicorn openai langchain tiktoken qdrant-client redis numpy pandas pydantic httpx aiohttp structlog prometheus-client pytest pytest-asyncio pytest-cov python-dotenv

# Create basic structure
mkdir -p src/{agents,memory,utils,api}
touch src/main.py src/__init__.py
```

### 4. Data Integration Service (Python)
```bash
cd services/data-integration

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn psycopg2-binary sqlalchemy pymongo redis httpx aiohttp requests beautifulsoup4 pandas numpy structlog prometheus-client pytest pytest-asyncio pytest-cov python-dotenv

# Create basic structure
mkdir -p src/{integrations,processors,utils,api}
touch src/main.py src/__init__.py
```

### 5. Image Analysis Service (Python)
```bash
cd services/image-analysis

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn tensorflow torch torchvision opencv-python pillow numpy pandas scikit-image structlog prometheus-client pytest pytest-asyncio pytest-cov python-dotenv

# Create basic structure
mkdir -p src/{models,processors,utils,api}
touch src/main.py src/__init__.py
```

### 6. User Management Service (Python)
```bash
cd services/user-management

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn psycopg2-binary sqlalchemy alembic redis bcrypt pyjwt pydantic email-validator httpx structlog prometheus-client pytest pytest-asyncio pytest-cov python-dotenv

# Create basic structure
mkdir -p src/{auth,models,utils,api}
touch src/main.py src/__init__.py
```

## Database Setup

### 1. PostgreSQL Schema
```bash
# Connect to PostgreSQL
psql -U afas_user -d afas_db

# Create initial schema (run in psql)
```

```sql
-- Create initial tables
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Farms table
CREATE TABLE farms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    location JSONB,
    total_acres DECIMAL(10,2),
    soil_type VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fields table
CREATE TABLE fields (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    farm_id UUID REFERENCES farms(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    acres DECIMAL(10,2),
    soil_data JSONB,
    crop_history JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Recommendations table
CREATE TABLE recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    farm_id UUID REFERENCES farms(id) ON DELETE CASCADE,
    question_type VARCHAR(100) NOT NULL,
    input_data JSONB,
    recommendations JSONB,
    confidence_score DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Soil tests table
CREATE TABLE soil_tests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    field_id UUID REFERENCES fields(id) ON DELETE CASCADE,
    test_date DATE NOT NULL,
    ph DECIMAL(3,1),
    organic_matter_percent DECIMAL(4,2),
    phosphorus_ppm DECIMAL(6,2),
    potassium_ppm DECIMAL(6,2),
    nitrogen_ppm DECIMAL(6,2),
    lab_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_farms_user_id ON farms(user_id);
CREATE INDEX idx_fields_farm_id ON fields(farm_id);
CREATE INDEX idx_recommendations_user_id ON recommendations(user_id);
CREATE INDEX idx_recommendations_question_type ON recommendations(question_type);
CREATE INDEX idx_soil_tests_field_id ON soil_tests(field_id);
```

### 2. MongoDB Collections
```bash
# Connect to MongoDB
mongosh

# Switch to AFAS database
use afas

# Create collections with validation
db.createCollection("question_responses", {
   validator: {
      $jsonSchema: {
         bsonType: "object",
         required: ["user_id", "question_type", "timestamp"],
         properties: {
            user_id: { bsonType: "string" },
            question_type: { bsonType: "string" },
            input_data: { bsonType: "object" },
            recommendations: { bsonType: "array" },
            ai_explanation: { bsonType: "string" },
            timestamp: { bsonType: "date" }
         }
      }
   }
})

db.createCollection("external_data_cache", {
   validator: {
      $jsonSchema: {
         bsonType: "object",
         required: ["source", "data", "expires_at"],
         properties: {
            source: { bsonType: "string" },
            location: { bsonType: "object" },
            data: { bsonType: "object" },
            expires_at: { bsonType: "date" }
         }
      }
   }
})
```

## Process Management

### 1. Create Start Scripts
```bash
# Create start-all.sh script
cat > start-all.sh << 'EOF'
#!/bin/bash

# Start databases
echo "Starting databases..."
brew services start postgresql@15
brew services start mongodb-community@7.0
brew services start redis

# Wait for databases to start
sleep 5

# Start services
echo "Starting AFAS services..."

# Question Router
cd services/question-router && npm run dev &
QUESTION_ROUTER_PID=$!

# Recommendation Engine
cd services/recommendation-engine && source venv/bin/activate && uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload &
RECOMMENDATION_ENGINE_PID=$!

# AI Agent
cd services/ai-agent && source venv/bin/activate && uvicorn src.main:app --host 0.0.0.0 --port 8002 --reload &
AI_AGENT_PID=$!

# Data Integration
cd services/data-integration && source venv/bin/activate && uvicorn src.main:app --host 0.0.0.0 --port 8003 --reload &
DATA_INTEGRATION_PID=$!

# Image Analysis
cd services/image-analysis && source venv/bin/activate && uvicorn src.main:app --host 0.0.0.0 --port 8004 --reload &
IMAGE_ANALYSIS_PID=$!

# User Management
cd services/user-management && source venv/bin/activate && uvicorn src.main:app --host 0.0.0.0 --port 8005 --reload &
USER_MANAGEMENT_PID=$!

echo "All services started!"
echo "Question Router: http://localhost:3001"
echo "Recommendation Engine: http://localhost:8001"
echo "AI Agent: http://localhost:8002"
echo "Data Integration: http://localhost:8003"
echo "Image Analysis: http://localhost:8004"
echo "User Management: http://localhost:8005"

# Save PIDs for cleanup
echo $QUESTION_ROUTER_PID > .pids
echo $RECOMMENDATION_ENGINE_PID >> .pids
echo $AI_AGENT_PID >> .pids
echo $DATA_INTEGRATION_PID >> .pids
echo $IMAGE_ANALYSIS_PID >> .pids
echo $USER_MANAGEMENT_PID >> .pids
EOF

chmod +x start-all.sh
```

### 2. Create Stop Script
```bash
# Create stop-all.sh script
cat > stop-all.sh << 'EOF'
#!/bin/bash

echo "Stopping AFAS services..."

# Kill all service processes
if [ -f .pids ]; then
    while read pid; do
        kill $pid 2>/dev/null
    done < .pids
    rm .pids
fi

# Stop databases (optional - comment out if you want to keep them running)
# brew services stop postgresql@15
# brew services stop mongodb-community@7.0
# brew services stop redis

echo "All services stopped!"
EOF

chmod +x stop-all.sh
```

## NGINX Configuration

### 1. Local Reverse Proxy Setup
```bash
# Create NGINX configuration
sudo mkdir -p /usr/local/etc/nginx/sites-available
sudo mkdir -p /usr/local/etc/nginx/sites-enabled

# Create AFAS site configuration
sudo tee /usr/local/etc/nginx/sites-available/afas << 'EOF'
upstream question_router {
    server localhost:3001;
}

upstream recommendation_engine {
    server localhost:8001;
}

upstream ai_agent {
    server localhost:8002;
}

upstream data_integration {
    server localhost:8003;
}

upstream image_analysis {
    server localhost:8004;
}

upstream user_management {
    server localhost:8005;
}

server {
    listen 80;
    server_name localhost afas.local;

    # API Gateway routing
    location /api/v1/questions/ {
        proxy_pass http://question_router;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /api/v1/recommendations/ {
        proxy_pass http://recommendation_engine;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /api/v1/ai/ {
        proxy_pass http://ai_agent;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /api/v1/data/ {
        proxy_pass http://data_integration;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /api/v1/images/ {
        proxy_pass http://image_analysis;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /api/v1/users/ {
        proxy_pass http://user_management;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Frontend (when implemented)
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF

# Enable the site
sudo ln -sf /usr/local/etc/nginx/sites-available/afas /usr/local/etc/nginx/sites-enabled/

# Test and start NGINX
sudo nginx -t
sudo nginx -s reload
```

## Development Workflow

### 1. Daily Development
```bash
# Start all services
./start-all.sh

# Work on individual services
cd services/recommendation-engine
source venv/bin/activate
# Make changes and test

# Stop all services when done
./stop-all.sh
```

### 2. Testing
```bash
# Run tests for individual services
cd services/recommendation-engine
source venv/bin/activate
pytest

# Run integration tests
cd tests/integration
python run_integration_tests.py
```

### 3. Monitoring
```bash
# Check service status
curl http://localhost:3001/health  # Question Router
curl http://localhost:8001/health  # Recommendation Engine
curl http://localhost:8002/health  # AI Agent
curl http://localhost:8003/health  # Data Integration
curl http://localhost:8004/health  # Image Analysis
curl http://localhost:8005/health  # User Management

# Check logs
tail -f logs/question-router.log
tail -f logs/recommendation-engine.log
```

## Troubleshooting

### Common Issues

1. **Port conflicts**: Check if ports are already in use
   ```bash
   lsof -i :3001  # Check specific port
   ```

2. **Database connection issues**: Verify databases are running
   ```bash
   pg_isready -h localhost -p 5432
   mongosh --eval "db.adminCommand('ismaster')"
   redis-cli ping
   ```

3. **Python virtual environment issues**: Recreate virtual environments
   ```bash
   rm -rf venv
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **NGINX configuration issues**: Test configuration
   ```bash
   sudo nginx -t
   ```

This setup provides a complete native development environment for AFAS without requiring Docker or Kubernetes, while maintaining the microservices architecture and development workflow.
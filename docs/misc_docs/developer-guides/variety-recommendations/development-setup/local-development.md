# Local Development Setup Guide

## Overview

This guide covers setting up a local development environment for the crop variety recommendations system, including prerequisites, installation steps, and development workflows.

## Prerequisites

### System Requirements

- **Operating System**: macOS, Linux, or Windows 10+
- **Python**: 3.11 or higher
- **Node.js**: 18.x or higher (for frontend development)
- **PostgreSQL**: 13+ with PostGIS extension
- **Redis**: 6.0+ (for caching)
- **Git**: Latest version

### Development Tools

- **IDE**: VS Code, PyCharm, or similar
- **Database Client**: pgAdmin, DBeaver, or similar
- **API Testing**: Postman, Insomnia, or similar
- **Container Runtime**: Docker and Docker Compose (optional)

## Installation Steps

### 1. Clone the Repository

```bash
# Clone the main repository
git clone https://github.com/your-org/caain-soil-hub.git
cd caain-soil-hub

# Navigate to the variety recommendations service
cd services/crop-taxonomy
```

### 2. Python Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Setup

#### PostgreSQL Installation

**macOS (using Homebrew):**
```bash
brew install postgresql postgis
brew services start postgresql
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib postgis
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**Windows:**
Download and install from [PostgreSQL official website](https://www.postgresql.org/download/windows/)

#### Database Configuration

```bash
# Create database user
sudo -u postgres createuser --interactive
# Enter username: variety_dev
# Enter role: y (superuser)

# Create database
sudo -u postgres createdb variety_recommendations_dev

# Connect to database and enable PostGIS
sudo -u postgres psql variety_recommendations_dev
```

```sql
-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create database schema
\i database/schema.sql

-- Exit psql
\q
```

### 4. Redis Setup

**macOS (using Homebrew):**
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian:**
```bash
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

**Windows:**
Download and install from [Redis official website](https://redis.io/download)

### 5. Environment Configuration

Create environment files:

```bash
# Create environment file
cp .env.example .env
```

Edit `.env` file:

```bash
# Database Configuration
DATABASE_URL=postgresql://variety_dev:password@localhost:5432/variety_recommendations_dev
DB_HOST=localhost
DB_PORT=5432
DB_NAME=variety_recommendations_dev
DB_USER=variety_dev
DB_PASSWORD=password

# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# API Configuration
API_HOST=0.0.0.0
API_PORT=8001
API_KEY=dev-api-key-12345

# External Services
CLIMATE_SERVICE_URL=http://localhost:8003
SOIL_SERVICE_URL=http://localhost:8004
MARKET_SERVICE_URL=http://localhost:8005

# Development Settings
DEBUG=True
LOG_LEVEL=DEBUG
ENVIRONMENT=development

# CORS Settings
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Rate Limiting
RATE_LIMIT_PER_MINUTE=1000
RATE_LIMIT_BURST=2000
```

### 6. Database Migrations

```bash
# Run database migrations
alembic upgrade head

# Seed initial data
python scripts/seed_data.py
```

### 7. Start Development Server

```bash
# Start the development server
python -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload

# Or use the start script
python start_service.py
```

## Development Workflow

### 1. Code Structure

```
services/crop-taxonomy/
├── src/
│   ├── main.py                 # FastAPI application entry point
│   ├── api/                    # API routes
│   │   ├── variety_routes.py
│   │   ├── comparison_routes.py
│   │   └── filter_routes.py
│   ├── models/                 # Pydantic models
│   │   ├── crop_variety_models.py
│   │   └── service_models.py
│   ├── services/               # Business logic
│   │   ├── variety_recommendation_service.py
│   │   └── variety_comparison_service.py
│   ├── database/              # Database operations
│   │   ├── crop_taxonomy_db.py
│   │   └── recommendation_management_db.py
│   └── utils/                 # Utility functions
│       ├── validators.py
│       └── formatters.py
├── tests/                     # Test files
│   ├── test_variety_service.py
│   └── test_api_endpoints.py
├── migrations/                # Database migrations
├── scripts/                   # Utility scripts
├── docs/                      # Documentation
├── requirements.txt           # Python dependencies
├── alembic.ini               # Alembic configuration
├── .env                      # Environment variables
└── start_service.py          # Service startup script
```

### 2. Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=src --cov-report=html

# Run linting
flake8 src/
black src/
isort src/

# Run type checking
mypy src/

# Start development server
python start_service.py

# Run database migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Seed test data
python scripts/seed_data.py

# Clear cache
python scripts/clear_cache.py
```

### 3. API Development

#### Adding New Endpoints

1. **Create route file** (if new):
```python
# src/api/new_feature_routes.py
from fastapi import APIRouter, HTTPException
from typing import List
from ..models.new_feature_models import NewFeatureRequest, NewFeatureResponse

router = APIRouter(prefix="/api/v1/new-feature", tags=["new-feature"])

@router.post("/", response_model=NewFeatureResponse)
async def create_new_feature(request: NewFeatureRequest):
    """Create a new feature."""
    try:
        # Implementation here
        pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

2. **Add to main application**:
```python
# src/main.py
from .api import new_feature_routes

app.include_router(new_feature_routes.router)
```

3. **Create models**:
```python
# src/models/new_feature_models.py
from pydantic import BaseModel, Field
from typing import Optional

class NewFeatureRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None

class NewFeatureResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    created_at: datetime
```

#### Testing New Endpoints

```bash
# Test with curl
curl -X POST "http://localhost:8001/api/v1/new-feature/" \
  -H "Authorization: Bearer dev-api-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Feature", "description": "Test Description"}'

# Test with Python requests
python -c "
import requests
response = requests.post(
    'http://localhost:8001/api/v1/new-feature/',
    headers={'Authorization': 'Bearer dev-api-key-12345'},
    json={'name': 'Test Feature', 'description': 'Test Description'}
)
print(response.json())
"
```

### 4. Database Development

#### Adding New Tables

1. **Create model**:
```python
# src/models/new_table_models.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class NewTable(Base):
    __tablename__ = 'new_table'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

2. **Create migration**:
```bash
alembic revision --autogenerate -m "Add new_table"
```

3. **Apply migration**:
```bash
alembic upgrade head
```

#### Database Seeding

```python
# scripts/seed_data.py
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.crop_variety_models import CropVarietyDB

async def seed_varieties():
    engine = create_engine("postgresql://variety_dev:password@localhost:5432/variety_recommendations_dev")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as session:
        # Add seed data
        varieties = [
            CropVarietyDB(
                variety_name="Pioneer P1197AM",
                crop_id=1,
                company="Pioneer",
                maturity_days=105,
                yield_potential_min=180,
                yield_potential_max=200,
                yield_unit="bu/acre",
                climate_zones=["6a", "6b"],
                soil_ph_min=6.0,
                soil_ph_max=7.0,
                soil_types=["clay_loam", "silt_loam"]
            ),
            # Add more varieties...
        ]
        
        for variety in varieties:
            session.add(variety)
        
        session.commit()
        print(f"Seeded {len(varieties)} varieties")

if __name__ == "__main__":
    asyncio.run(seed_varieties())
```

### 5. Testing Development

#### Unit Tests

```python
# tests/test_variety_service.py
import pytest
from unittest.mock import Mock, patch
from src.services.variety_recommendation_service import VarietyRecommendationService

class TestVarietyRecommendationService:
    @pytest.fixture
    def service(self):
        return VarietyRecommendationService()
    
    @pytest.mark.asyncio
    async def test_get_recommendations(self, service):
        """Test getting variety recommendations."""
        # Mock database response
        with patch.object(service.db, 'get_varieties') as mock_get_varieties:
            mock_get_varieties.return_value = [
                {
                    'id': 'test-variety',
                    'name': 'Test Variety',
                    'company': 'Test Company',
                    'yield_potential': '180 bu/acre',
                    'maturity_days': 105,
                    'confidence': 0.9
                }
            ]
            
            result = await service.get_recommendations({
                'crop_id': 'corn',
                'farm_data': {
                    'location': {'latitude': 40.7128, 'longitude': -74.0060},
                    'soil_data': {'ph': 6.5, 'organic_matter_percent': 3.2}
                }
            })
            
            assert len(result) == 1
            assert result[0]['name'] == 'Test Variety'
```

#### Integration Tests

```python
# tests/test_api_integration.py
import pytest
import httpx
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

class TestVarietyAPI:
    def test_get_recommendations(self):
        """Test variety recommendations endpoint."""
        response = client.post(
            "/api/v1/varieties/recommend",
            headers={"Authorization": "Bearer dev-api-key-12345"},
            json={
                "crop_id": "corn",
                "farm_data": {
                    "location": {"latitude": 40.7128, "longitude": -74.0060},
                    "soil_data": {"ph": 6.5, "organic_matter_percent": 3.2}
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
```

#### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_variety_service.py

# Run tests with coverage
pytest tests/ --cov=src --cov-report=html

# Run tests in parallel
pytest tests/ -n auto

# Run tests with verbose output
pytest tests/ -v

# Run tests matching pattern
pytest tests/ -k "test_recommendations"
```

### 6. Debugging

#### Debug Configuration (VS Code)

Create `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/src/main.py",
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/src"
            },
            "args": ["--reload"]
        },
        {
            "name": "Python: Tests",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["tests/", "-v"],
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/src"
            }
        }
    ]
}
```

#### Logging Configuration

```python
# src/utils/logging_config.py
import logging
import sys
from pathlib import Path

def setup_logging(level: str = "DEBUG"):
    """Setup logging configuration."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_dir / "variety_service.log")
        ]
    )
    
    # Set specific loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
```

#### Debugging Tips

1. **Use breakpoints**: Set breakpoints in your IDE to pause execution
2. **Print debugging**: Use `print()` statements for quick debugging
3. **Logging**: Use proper logging instead of print statements
4. **Database queries**: Log SQL queries to debug database issues
5. **API testing**: Use tools like Postman or curl to test endpoints

### 7. Performance Monitoring

#### Development Metrics

```python
# src/utils/performance_monitor.py
import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def monitor_performance(func):
    """Decorator to monitor function performance."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} executed in {execution_time:.3f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.3f}s: {e}")
            raise
    return wrapper

# Usage
@monitor_performance
async def get_variety_recommendations(request):
    # Implementation here
    pass
```

#### Database Query Monitoring

```python
# src/database/query_monitor.py
import logging
from sqlalchemy import event
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - context._query_start_time
    if total > 1.0:  # Log slow queries
        logger.warning(f"Slow query ({total:.3f}s): {statement}")
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Issues

**Error**: `psycopg2.OperationalError: could not connect to server`

**Solutions**:
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL
sudo systemctl start postgresql

# Check connection
psql -h localhost -U variety_dev -d variety_recommendations_dev
```

#### 2. Redis Connection Issues

**Error**: `redis.exceptions.ConnectionError: Error connecting to Redis`

**Solutions**:
```bash
# Check if Redis is running
redis-cli ping

# Start Redis
sudo systemctl start redis-server

# Check Redis configuration
redis-cli config get "*"
```

#### 3. Import Errors

**Error**: `ModuleNotFoundError: No module named 'src'`

**Solutions**:
```bash
# Add src to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Or use relative imports
from .models import CropVariety
```

#### 4. Port Already in Use

**Error**: `OSError: [Errno 98] Address already in use`

**Solutions**:
```bash
# Find process using port 8001
lsof -i :8001

# Kill the process
kill -9 <PID>

# Or use a different port
python -m uvicorn src.main:app --port 8002
```

#### 5. Migration Issues

**Error**: `alembic.util.exc.CommandError: Can't locate revision identified by 'head'`

**Solutions**:
```bash
# Check current revision
alembic current

# Show migration history
alembic history

# Reset to base
alembic downgrade base
alembic upgrade head
```

### Debugging Commands

```bash
# Check service status
curl http://localhost:8001/health

# Check database connection
python -c "from src.database.crop_taxonomy_db import CropTaxonomyDatabase; db = CropTaxonomyDatabase(); print(db.test_connection())"

# Check Redis connection
python -c "import redis; r = redis.Redis(); print(r.ping())"

# View logs
tail -f logs/variety_service.log

# Check environment variables
python -c "import os; print([k for k in os.environ.keys() if 'DB' in k])"
```

## Best Practices

### 1. Code Organization

- Follow PEP 8 style guidelines
- Use type hints for all functions
- Write comprehensive docstrings
- Organize code into logical modules
- Use dependency injection

### 2. Testing

- Write tests for all new functionality
- Aim for >80% code coverage
- Use fixtures for test data
- Mock external dependencies
- Test error scenarios

### 3. Database

- Use migrations for schema changes
- Validate data at the model level
- Use transactions for data consistency
- Index frequently queried columns
- Monitor query performance

### 4. API Development

- Follow RESTful conventions
- Use proper HTTP status codes
- Implement proper error handling
- Document all endpoints
- Use request/response models

### 5. Security

- Never commit secrets to version control
- Use environment variables for configuration
- Implement proper authentication
- Validate all input data
- Use HTTPS in production

### 6. Performance

- Use async/await for I/O operations
- Implement proper caching
- Monitor response times
- Use connection pooling
- Optimize database queries
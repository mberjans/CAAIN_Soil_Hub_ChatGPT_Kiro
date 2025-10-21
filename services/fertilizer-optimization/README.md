# Fertilizer Optimization Service

## Project Overview and Purpose

The Fertilizer Optimization Service is a comprehensive microservices-based system designed to provide intelligent fertilizer planning and timing recommendations for agricultural operations. It is part of the larger CAAIN Soil Hub ecosystem, which aims to deliver data-driven insights for sustainable farming practices.

### Key Features

- **Fertilizer Strategy Optimization**: Recommends optimal fertilizer types, rates, and application methods based on soil conditions, crop requirements, and economic factors.
- **Timing Optimization**: Provides precise application timing recommendations considering weather forecasts, crop growth stages, and operational constraints.
- **Integrated Workflows**: Combines strategy and timing for complete fertilizer planning from soil test to harvest.
- **Real-time Alerts**: Generates notifications for optimal application windows.
- **Historical Analysis**: Tracks application history and performance for continuous improvement.

### Purpose

This service helps farmers:
- Maximize crop yields through optimized nutrient management
- Minimize environmental impact by reducing over-fertilization
- Reduce operational costs through efficient timing and resource allocation
- Comply with agricultural regulations and sustainability goals

## Architecture and Components

The service consists of two main microservices:

### 1. Fertilizer Strategy Service (`fertilizer-strategy`)
- **Port**: 8009 (configurable via `FERTILIZER_STRATEGY_PORT`)
- **Framework**: FastAPI with async/await patterns
- **Database**: PostgreSQL for price tracking and application history
- **Responsibilities**:
  - Fertilizer type selection and rate calculation
  - Economic optimization (ROI analysis)
  - Equipment compatibility checking
  - Price tracking and market intelligence

### 2. Fertilizer Timing Service (`fertilizer-timing`)
- **Port**: 8010 (configurable via `FERTILIZER_TIMING_SERVICE_PORT`)
- **Framework**: FastAPI with async/await patterns
- **Database**: SQLite for timing results and alerts
- **Responsibilities**:
  - Weather window analysis
  - Crop stage forecasting
  - Split application planning
  - Seasonal calendar generation
  - Application alert management

### Integration Architecture

The services communicate via REST APIs with resilience patterns:

- **Circuit Breaker**: Prevents cascading failures
- **Retry Logic**: Exponential backoff for transient failures
- **Health Checks**: Service availability monitoring
- **Configuration Management**: Environment-based service discovery

### Data Flow

```
User Request → Strategy Service → Timing Service → Integrated Response
     ↓              ↓              ↓              ↓
   Validation   Optimization   Weather/Soil   Unified Plan
                Calculation    Integration
```

## API Endpoints and Usage

### Base URLs
- Fertilizer Strategy: `http://localhost:8009`
- Fertilizer Timing: `http://localhost:8010`

### Core Endpoints

#### Fertilizer Strategy Service

**POST /api/v1/strategy/optimize**
- **Purpose**: Optimize fertilizer strategy based on requirements
- **Request Body**:
  ```json
  {
    "crop_type": "corn",
    "field_size": 160,
    "location": {"latitude": 42.5, "longitude": -95.0},
    "soil_characteristics": {"pH": 6.5, "N": 20, "P": 30, "K": 150},
    "nutrient_requirements": {"N": 180, "P": 60, "K": 40},
    "budget": 8000
  }
  ```
- **Response**: Optimized fertilizer recommendations with costs and ROI

**GET /api/v1/strategy/prices/current**
- **Purpose**: Get current fertilizer prices
- **Query Parameters**: `fertilizer_type`, `location`
- **Response**: Price data with sources and timestamps

#### Fertilizer Timing Service

**POST /api/v1/fertilizer-timing/optimize**
- **Purpose**: Generate timing recommendations
- **Request Body**:
  ```json
  {
    "crop_type": "corn",
    "planting_date": "2024-05-15",
    "location": {"latitude": 42.5, "longitude": -95.0},
    "soil_characteristics": {"pH": 6.5, "organic_matter": 3.2},
    "constraints": {"equipment_availability": ["spreader_001"]}
  }
  ```
- **Response**: Timing plan with application windows and confidence scores

**POST /api/v1/fertilizer-calendar/generate**
- **Purpose**: Create seasonal fertilizer calendar
- **Request Body**: Optimization parameters
- **Response**: Calendar entries with dates and recommendations

#### Integrated Endpoints

**POST /api/v1/integrated/strategy-with-timing**
- **Purpose**: Combined strategy and timing optimization
- **Request Body**: Full planning parameters
- **Response**: Complete plan with strategy, timing, and pricing

**POST /api/v1/integrated/complete-fertilizer-plan**
- **Purpose**: End-to-end fertilizer planning workflow
- **Request Body**: Soil test data and requirements
- **Response**: Comprehensive plan with implementation guidance

### Health Checks

- **GET /health** (both services): Service status and feature availability

## Installation and Setup Instructions

### Prerequisites

- Python 3.10+
- PostgreSQL (for fertilizer-strategy)
- Redis (optional, for caching)
- Git

### 1. Clone the Repository

```bash
git clone <repository-url>
cd caain-soil-hub/services/fertilizer-optimization
```

### 2. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Core dependencies
pip install -r requirements.txt

# Development dependencies (optional)
pip install -r requirements-dev.txt
```

### 4. Configure Environment Variables

Create `.env` files for each service:

**fertilizer-strategy/.env**
```ini
FERTILIZER_STRATEGY_PORT=8009
FERTILIZER_TIMING_URL=http://localhost:8010
DATABASE_URL=postgresql://user:password@localhost/fertilizer_strategy
INTEGRATION_MODE=rest_api
ENABLE_CIRCUIT_BREAKER=true
ENABLE_RETRY=true
```

**fertilizer-timing/.env**
```ini
FERTILIZER_TIMING_SERVICE_PORT=8010
FERTILIZER_STRATEGY_URL=http://localhost:8009
DATABASE_URL=sqlite:///timing.db
INTEGRATION_MODE=rest_api
ENABLE_CIRCUIT_BREAKER=true
ENABLE_RETRY=true
```

### 5. Set Up Databases

#### PostgreSQL (Fertilizer Strategy)
```bash
# Create database
createdb fertilizer_strategy

# Run migrations (if using Alembic)
cd services/fertilizer-strategy
alembic upgrade head
```

#### SQLite (Fertilizer Timing)
The database file will be created automatically on first run.

### 6. Start Services

#### Development Mode
```bash
# Terminal 1: Start fertilizer-strategy
cd services/fertilizer-strategy/src
uvicorn main:app --port 8009 --reload

# Terminal 2: Start fertilizer-timing
cd services/fertilizer-timing/src
uvicorn main:app --port 8010 --reload
```

#### Production Mode
```bash
# Using Docker (recommended)
docker-compose up -d

# Or with uvicorn
uvicorn main:app --host 0.0.0.0 --port 8009
```

### 7. Verify Installation

```bash
# Check health endpoints
curl http://localhost:8009/health
curl http://localhost:8010/health

# Test basic functionality
curl -X POST http://localhost:8009/api/v1/strategy/optimize \
  -H "Content-Type: application/json" \
  -d '{"crop_type": "corn", "field_size": 100}'
```

## Testing Procedures

### Unit Tests

Run tests for individual components:

```bash
# Fertilizer Strategy tests
cd services/fertilizer-strategy
pytest src/tests/ -v

# Fertilizer Timing tests
cd services/fertilizer-timing
pytest src/tests/ -v
```

### Integration Tests

Test service interactions:

```bash
# Start both services first
# Then run integration tests
pytest tests/integration/ -v
```

### End-to-End Tests

Test complete workflows:

```bash
# Example: Test complete fertilizer plan
pytest tests/e2e/test_complete_plan.py -v
```

### Performance Tests

```bash
# Load testing
pytest tests/performance/ -v

# Stress testing with locust
locust -f tests/performance/locustfile.py
```

### Test Coverage

Generate coverage reports:

```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

## Configuration Options

### Environment Variables

| Variable | Service | Description | Default |
|----------|---------|-------------|---------|
| `FERTILIZER_STRATEGY_PORT` | Strategy | Service port | 8009 |
| `FERTILIZER_TIMING_SERVICE_PORT` | Timing | Service port | 8010 |
| `DATABASE_URL` | Both | Database connection string | - |
| `INTEGRATION_MODE` | Both | Integration method (`rest_api`, `direct_import`) | `rest_api` |
| `ENABLE_CIRCUIT_BREAKER` | Both | Enable circuit breaker | `true` |
| `ENABLE_RETRY` | Both | Enable retry logic | `true` |
| `CIRCUIT_BREAKER_THRESHOLD` | Both | Failure threshold for circuit breaker | 5 |
| `RETRY_MAX_ATTEMPTS` | Both | Maximum retry attempts | 3 |

### Configuration Files

- **fertilizer-strategy/src/config/integration_config.py**: Integration settings
- **fertilizer-timing/src/config/integration_config.py**: Integration settings
- **logging.conf**: Logging configuration

## Contributing Guidelines

### Development Workflow

1. **Fork the Repository**
   ```bash
   git clone <your-fork-url>
   cd caain-soil-hub
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes**
   - Follow PEP 8 style guidelines
   - Add tests for new functionality
   - Update documentation as needed

4. **Run Tests**
   ```bash
   pytest tests/ -v
   ```

5. **Commit Changes**
   ```bash
   git add .
   git commit -m "Add your descriptive commit message"
   ```

6. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   # Create PR via GitHub interface
   ```

### Code Standards

- **Language**: Python 3.10+
- **Framework**: FastAPI for APIs
- **Linting**: Black, Flake8, mypy
- **Testing**: pytest with coverage
- **Documentation**: Google-style docstrings

### Adding New Features

1. **API Changes**: Update OpenAPI schema and documentation
2. **Database Changes**: Create migrations for schema updates
3. **Integration**: Ensure compatibility with existing services
4. **Testing**: Add unit and integration tests

### Reporting Issues

- Use GitHub Issues for bug reports and feature requests
- Include detailed steps to reproduce issues
- Provide environment information and logs

### Code Review Process

- All submissions require review
- Ensure CI/CD checks pass
- Maintain backward compatibility where possible

## Support and Documentation

- **API Documentation**: Available at `/docs` endpoint when services are running
- **Architecture Docs**: See `docs/` directory for detailed design documents
- **Integration Guide**: Refer to `fertilizer_timing_integration_analysis.md`
- **Implementation Reports**: Check `TICKET-006_fertilizer-timing-optimization-14.1_IMPLEMENTATION_COMPLETE.md`

## License

This project is part of the CAAIN Soil Hub and follows the project's licensing terms.

---

**Version**: 1.0.0
**Last Updated**: 2025-10-21
**Contact**: CAAIN Development Team
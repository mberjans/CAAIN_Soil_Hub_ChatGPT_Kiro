# AFAS Drought Management Service

A comprehensive microservice for agricultural drought assessment, moisture conservation, and water management. This service provides farmers with intelligent drought risk assessment, conservation practice recommendations, and real-time monitoring capabilities.

## Overview

The Drought Management Service is part of the Autonomous Farm Advisory System (AFAS) and addresses critical water management challenges in agriculture. It integrates weather data, soil conditions, and crop requirements to provide actionable drought management recommendations.

## Features

### 🌡️ Drought Risk Assessment
- **Real-time Risk Analysis**: Assess drought risk based on soil moisture, weather patterns, and crop conditions
- **Multi-factor Analysis**: Considers temperature, precipitation, humidity, and historical data
- **Confidence Scoring**: Provides confidence levels for all assessments
- **Risk Level Classification**: Categorizes risk as Low, Moderate, High, Severe, or Extreme

### 💧 Moisture Conservation
- **Practice Recommendations**: Suggests conservation practices tailored to field conditions
- **Cost-Benefit Analysis**: Calculates ROI and payback periods for conservation investments
- **Implementation Planning**: Provides detailed implementation timelines and resource requirements
- **Effectiveness Tracking**: Monitors practice effectiveness over time

### 📊 Water Savings Calculator
- **Savings Quantification**: Calculates potential water savings from conservation practices
- **Economic Analysis**: Provides detailed cost-benefit analysis including energy savings
- **Environmental Impact**: Assesses environmental benefits of water conservation
- **Historical Tracking**: Tracks water savings performance over time

### 🔍 Drought Monitoring
- **Real-time Monitoring**: Continuous monitoring of soil moisture and weather conditions
- **Alert System**: Configurable alerts for drought risk indicators
- **Data Collection**: Automated data collection from sensors and weather stations
- **Trend Analysis**: Identifies patterns and trends in drought conditions

## Architecture

### Service Structure
```
services/drought-management/
├── src/
│   ├── api/
│   │   └── routes.py              # FastAPI routes and endpoints
│   ├── services/
│   │   ├── drought_assessment_service.py      # Core drought assessment logic
│   │   ├── moisture_conservation_service.py   # Conservation practice management
│   │   ├── drought_monitoring_service.py      # Monitoring and alerting
│   │   └── water_savings_calculator.py        # Water savings calculations
│   ├── models/
│   │   └── drought_models.py      # Pydantic data models
│   ├── database/
│   │   └── drought_db.py          # SQLAlchemy models and database operations
│   └── main.py                    # FastAPI application entry point
├── tests/
│   └── test_drought_assessment_service.py  # Comprehensive test suite
├── requirements.txt               # Python dependencies
├── start_service.py              # Service startup script
└── README.md                     # This documentation
```

### Technology Stack
- **Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Data Validation**: Pydantic 2.5.0
- **Async Support**: asyncio and aiohttp
- **Testing**: pytest with async support
- **Scientific Computing**: NumPy, Pandas, SciPy
- **Machine Learning**: scikit-learn for drought modeling

## API Endpoints

### Drought Assessment
- `POST /api/v1/drought/assess` - Comprehensive drought risk assessment
- `GET /api/v1/drought/risk-assessment/{farm_location_id}` - Get current drought risk
- `GET /api/v1/drought/soil-moisture/{field_id}` - Get soil moisture status

### Moisture Conservation
- `POST /api/v1/drought/conservation/recommendations` - Get conservation practice recommendations
- `POST /api/v1/drought/conservation/calculate-benefits` - Calculate conservation benefits

### Drought Monitoring
- `POST /api/v1/drought/monitor/setup` - Set up drought monitoring
- `GET /api/v1/drought/monitor/status/{farm_location_id}` - Get monitoring status
- `GET /api/v1/drought/alerts/{farm_location_id}` - Get active drought alerts

### Water Savings
- `POST /api/v1/drought/water-savings/calculate` - Calculate water savings potential
- `GET /api/v1/drought/water-savings/history/{field_id}` - Get water savings history

### Utility Endpoints
- `GET /api/v1/drought/practices` - Get available conservation practices
- `GET /health` - Service health check
- `GET /` - Service information and documentation

## Installation and Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 13+
- Redis (optional, for caching)

### Environment Variables
```bash
# Required
DROUGHT_MANAGEMENT_PORT=8007
DATABASE_URL=postgresql://user:password@localhost:5432/afas_drought
WEATHER_API_KEY=your_weather_api_key

# Optional
DROUGHT_MANAGEMENT_HOST=0.0.0.0
REDIS_URL=redis://localhost:6379
LOG_LEVEL=INFO
```

### Installation Steps

1. **Clone and Navigate**
   ```bash
   cd services/drought-management
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Environment Variables**
   ```bash
   export DROUGHT_MANAGEMENT_PORT=8007
   export DATABASE_URL="postgresql://localhost:5432/afas_drought"
   export WEATHER_API_KEY="your_api_key"
   ```

5. **Initialize Database**
   ```bash
   # The service will create tables automatically on first run
   python start_service.py
   ```

6. **Start Service**
   ```bash
   python start_service.py
   ```

## Usage Examples

### Drought Risk Assessment

```python
import httpx
import asyncio

async def assess_drought_risk():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8007/api/v1/drought/assess",
            json={
                "farm_location_id": "123e4567-e89b-12d3-a456-426614174000",
                "crop_type": "corn",
                "growth_stage": "V6",
                "soil_type": "clay_loam",
                "irrigation_available": True,
                "include_forecast": True,
                "assessment_depth_days": 30
            }
        )
        return response.json()

# Run assessment
result = asyncio.run(assess_drought_risk())
print(f"Drought Risk Level: {result['assessment']['drought_risk_level']}")
print(f"Recommendations: {len(result['recommendations'])}")
```

### Conservation Practice Recommendations

```python
async def get_conservation_recommendations():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8007/api/v1/drought/conservation/recommendations",
            json={
                "field_id": "123e4567-e89b-12d3-a456-426614174001",
                "soil_type": "clay_loam",
                "slope_percent": 2.5,
                "drainage_class": "moderate",
                "current_practices": [],
                "available_equipment": ["tractor", "planter"],
                "budget_constraint": 100.00,
                "implementation_timeline": "immediate"
            }
        )
        return response.json()

# Get recommendations
recommendations = asyncio.run(get_conservation_recommendations())
for rec in recommendations:
    print(f"Practice: {rec['practice']['practice_name']}")
    print(f"Water Savings: {rec['practice']['water_savings_percent']}%")
    print(f"ROI: {rec['cost_benefit_analysis']['roi_percentage']:.1f}%")
```

### Water Savings Calculation

```python
async def calculate_water_savings():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8007/api/v1/drought/water-savings/calculate",
            json={
                "field_id": "123e4567-e89b-12d3-a456-426614174001",
                "current_water_usage": 12500.0,
                "proposed_practices": [
                    {
                        "practice_name": "Cover Crops",
                        "practice_type": "cover_crops",
                        "water_savings_percent": 20.0,
                        "implementation_cost": 35.00,
                        "maintenance_cost_per_year": 10.00
                    }
                ],
                "implementation_timeline": "seasonal",
                "effectiveness_assumptions": {
                    "cover_crops": 0.9
                }
            }
        )
        return response.json()

# Calculate savings
savings = asyncio.run(calculate_water_savings())
print(f"Water Savings: {savings['projected_savings']:.0f} gallons")
print(f"Savings Percentage: {savings['savings_percentage']:.1f}%")
print(f"Payback Period: {savings['cost_benefit_analysis']['payback_period_years']:.1f} years")
```

## Data Models

### Core Models

#### DroughtAssessment
```python
{
    "assessment_id": "uuid",
    "farm_location_id": "uuid",
    "assessment_date": "datetime",
    "drought_risk_level": "low|moderate|high|severe|extreme",
    "soil_moisture_status": {
        "surface_moisture_percent": 45.0,
        "deep_moisture_percent": 60.0,
        "available_water_capacity": 2.5,
        "moisture_level": "adequate",
        "irrigation_recommendation": "Monitor closely"
    },
    "weather_forecast_impact": {
        "temperature_impact": "Above average temperatures expected",
        "precipitation_impact": "Below average precipitation forecast",
        "forecast_confidence": 0.75,
        "risk_factors": ["High temperature", "Low precipitation"]
    },
    "confidence_score": 0.85
}
```

#### ConservationPractice
```python
{
    "practice_id": "uuid",
    "practice_name": "Cover Crops",
    "practice_type": "cover_crops",
    "water_savings_percent": 20.0,
    "implementation_cost": 35.00,
    "soil_health_impact": "highly_positive",
    "effectiveness_rating": 8.0,
    "implementation_time_days": 7
}
```

## Testing

### Running Tests
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_drought_assessment_service.py -v
```

### Test Coverage
The test suite includes:
- **Unit Tests**: Individual service method testing
- **Integration Tests**: End-to-end workflow testing
- **Mock Testing**: External service integration testing
- **Error Handling**: Exception and edge case testing
- **Data Validation**: Model validation testing

## Monitoring and Health Checks

### Health Check Endpoint
```bash
curl http://localhost:8007/health
```

Response:
```json
{
    "service": "drought-management",
    "status": "healthy",
    "version": "1.0.0",
    "components": {
        "drought_assessment": "healthy",
        "moisture_conservation": "healthy",
        "drought_monitoring": "healthy"
    },
    "integration": {
        "weather_data": "available",
        "soil_data": "available",
        "crop_data": "available"
    }
}
```

### Service Metrics
- Response time monitoring
- Error rate tracking
- Database connection health
- External service availability
- Memory and CPU usage

## Integration with Other Services

### Required Service Integrations
- **Weather Service**: Real-time weather data and forecasts
- **Soil Service**: Soil characteristics and moisture data
- **Crop Service**: Crop water requirements and growth stages
- **Location Service**: Farm and field location data

### Optional Integrations
- **Notification Service**: Alert delivery
- **Analytics Service**: Performance tracking
- **User Management**: Authentication and authorization

## Configuration

### Service Configuration
```python
# src/config.py
class Settings:
    DROUGHT_MANAGEMENT_PORT: int = 8007
    DATABASE_URL: str
    WEATHER_API_KEY: str
    REDIS_URL: str = "redis://localhost:6379"
    LOG_LEVEL: str = "INFO"
    MAX_CONNECTIONS: int = 100
    REQUEST_TIMEOUT: int = 30
```

### Database Configuration
```python
# Database connection settings
DATABASE_CONFIG = {
    "pool_size": 20,
    "max_overflow": 30,
    "pool_pre_ping": True,
    "pool_recycle": 300,
    "echo": False
}
```

## Deployment

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
EXPOSE 8007

CMD ["python", "src/main.py"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  drought-management:
    build: .
    ports:
      - "8007:8007"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/afas_drought
      - WEATHER_API_KEY=${WEATHER_API_KEY}
    depends_on:
      - db
      - redis

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=afas_drought
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## Performance Considerations

### Optimization Strategies
- **Database Indexing**: Optimized queries for large datasets
- **Caching**: Redis caching for frequently accessed data
- **Connection Pooling**: Efficient database connection management
- **Async Operations**: Non-blocking I/O for better performance
- **Data Pagination**: Efficient handling of large result sets

### Performance Metrics
- **Response Time**: < 2 seconds for assessment requests
- **Throughput**: 100+ concurrent requests
- **Availability**: 99.5% uptime target
- **Memory Usage**: < 512MB under normal load

## Security Considerations

### Data Protection
- **Input Validation**: Comprehensive input sanitization
- **SQL Injection Prevention**: Parameterized queries
- **Authentication**: JWT token validation
- **Authorization**: Role-based access control
- **Data Encryption**: Sensitive data encryption at rest

### API Security
- **Rate Limiting**: Request rate limiting
- **CORS Configuration**: Proper cross-origin resource sharing
- **HTTPS**: SSL/TLS encryption for all communications
- **API Keys**: Secure API key management

## Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check environment variables
echo $DATABASE_URL
echo $WEATHER_API_KEY

# Check port availability
netstat -tulpn | grep 8007

# Check logs
tail -f service.log
```

#### Database Connection Issues
```bash
# Test database connection
psql $DATABASE_URL -c "SELECT 1;"

# Check database tables
psql $DATABASE_URL -c "\dt"
```

#### High Memory Usage
```bash
# Monitor memory usage
htop

# Check for memory leaks
python -m memory_profiler src/main.py
```

### Log Analysis
```bash
# Filter error logs
grep "ERROR" service.log

# Monitor real-time logs
tail -f service.log | grep "drought"
```

## Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Install development dependencies
4. Run tests before committing
5. Submit a pull request

### Code Standards
- Follow PEP 8 style guidelines
- Use type hints for all functions
- Write comprehensive docstrings
- Maintain >80% test coverage
- Use async/await for I/O operations

### Testing Requirements
- All new features must have tests
- Integration tests for API endpoints
- Unit tests for business logic
- Performance tests for critical paths

## License

This project is part of the AFAS (Autonomous Farm Advisory System) and is licensed under the MIT License.

## Support

For support and questions:
- **Documentation**: Check this README and API docs
- **Issues**: Report bugs via GitHub issues
- **Discussions**: Join our community discussions
- **Email**: support@afas.agriculture

## Changelog

### Version 1.0.0 (Current)
- Initial release of drought management service
- Comprehensive drought risk assessment
- Conservation practice recommendations
- Water savings calculations
- Real-time monitoring capabilities
- Full API documentation
- Comprehensive test suite

---

**Note**: This service is designed to work as part of the larger AFAS ecosystem. For standalone usage, ensure all required external services are properly configured and accessible.
# Crop Variety Recommendations - Developer Guide

## Overview

The Crop Variety Recommendations system is a comprehensive agricultural decision support platform that provides intelligent crop variety selection based on regional conditions, soil characteristics, and farmer preferences. This developer guide provides complete documentation for integrating with and extending the variety recommendations service.

## Table of Contents

- [Architecture Overview](./architecture/)
  - [System Design](./architecture/system-design.md)
  - [Data Models](./architecture/data-models.md)
  - [Service Components](./architecture/service-components.md)
- [API Reference](./api-reference/)
  - [Authentication](./api-reference/authentication.md)
  - [Variety Recommendation API](./api-reference/variety-recommendation-api.md)
  - [Comparison API](./api-reference/comparison-api.md)
  - [Filtering API](./api-reference/filtering-api.md)
- [Development Setup](./development-setup/)
  - [Local Development](./development-setup/local-development.md)
  - [Environment Configuration](./development-setup/environment-configuration.md)
  - [Database Setup](./development-setup/database-setup.md)
- [Integration Guides](./integration-guides/)
  - [Frontend Integration](./integration-guides/frontend-integration.md)
  - [Service Integration](./integration-guides/service-integration.md)
  - [Database Integration](./integration-guides/database-integration.md)
- [Testing](./testing/)
  - [Unit Testing](./testing/unit-testing.md)
  - [Integration Testing](./testing/integration-testing.md)
  - [Performance Testing](./testing/performance-testing.md)
- [Deployment](./deployment/)
  - [Production Deployment](./deployment/production-deployment.md)
  - [Docker Configuration](./deployment/docker-configuration.md)
  - [Monitoring Setup](./deployment/monitoring-setup.md)
- [Performance Optimization](./performance/)
  - [Caching Strategies](./performance/caching-strategies.md)
  - [Database Optimization](./performance/database-optimization.md)
  - [API Performance](./performance/api-performance.md)
- [Troubleshooting](./troubleshooting/)
  - [Common Issues](./troubleshooting/common-issues.md)
  - [Debugging Guide](./troubleshooting/debugging-guide.md)
  - [Error Handling](./troubleshooting/error-handling.md)

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- Docker (optional)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd CAAIN_Soil_Hub_ChatGPT_Kiro

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start the service
uvicorn services.crop-taxonomy.src.main:app --host 0.0.0.0 --port 8001
```

### Basic Usage

```python
import httpx

# Get variety recommendations
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8001/api/v1/varieties/recommend",
        headers={"Authorization": "Bearer your-api-key"},
        json={
            "crop_id": "corn",
            "farm_data": {
                "location": {
                    "latitude": 40.7128,
                    "longitude": -74.0060
                },
                "soil_data": {
                    "ph": 6.5,
                    "organic_matter_percent": 3.2
                }
            }
        }
    )
    
    recommendations = response.json()
    print(f"Found {len(recommendations)} variety recommendations")
```

## Key Features

### 1. Intelligent Variety Selection
- Multi-criteria ranking based on yield potential, disease resistance, and regional adaptation
- Confidence scoring for recommendation reliability
- Economic analysis including ROI and break-even calculations

### 2. Regional Adaptation
- Climate zone integration for location-specific recommendations
- Soil type compatibility analysis
- Regional performance data integration

### 3. Advanced Filtering
- Filter by maturity, yield potential, disease resistance, and traits
- Price range filtering with market data integration
- Custom criteria support

### 4. Comparison Tools
- Side-by-side variety comparison
- Performance metrics analysis
- Economic impact assessment

### 5. Performance Optimization
- Response time <2 seconds
- Caching with >60% hit rate
- Database query optimization
- Parallel processing support

## Service Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Variety Recommendations                       │
│                         Service                                 │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │   Crop      │  │   Climate   │  │    Soil     │  │ Market  │ │
│  │ Taxonomy    │  │    Zone     │  │   Data      │  │ Price   │ │
│  │  Service    │  │  Service    │  │  Service    │  │Service  │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/varieties/recommend` | POST | Get variety recommendations |
| `/api/v1/varieties/compare` | POST | Compare multiple varieties |
| `/api/v1/varieties/{id}/details` | GET | Get variety details |
| `/api/v1/varieties/filter` | POST | Filter varieties by criteria |
| `/api/v1/varieties/search` | GET | Search varieties by name/traits |

## Data Models

### Core Models

- **VarietyRecommendation**: Main recommendation response
- **FarmData**: Farm and field characteristics
- **UserPreferences**: Farmer preferences and priorities
- **RegionalContext**: Location and climate data
- **EconomicAnalysis**: Cost and ROI calculations

### Database Schema

- **crops**: Crop type definitions
- **crop_varieties**: Variety characteristics and performance data
- **variety_recommendations**: Recommendation history and outcomes
- **farm_data**: Farm and field information
- **market_prices**: Current and historical price data

## Performance Requirements

- **Response Time**: <2 seconds for variety recommendations
- **Availability**: 99.5% uptime
- **Throughput**: 1000+ requests per minute
- **Cache Hit Rate**: >60% for frequently accessed data
- **Database Queries**: Optimized with proper indexing

## Security

- **Authentication**: JWT tokens and API keys
- **Authorization**: Role-based access control
- **Data Validation**: Input validation and sanitization
- **Rate Limiting**: 100 requests per minute per API key
- **HTTPS**: All communications encrypted

## Monitoring

- **Health Checks**: Service availability monitoring
- **Metrics**: Response times, error rates, throughput
- **Logging**: Structured logging with correlation IDs
- **Alerting**: Automated alerts for system issues
- **Dashboards**: Real-time system health monitoring

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

- **Documentation**: This guide and API reference
- **Issues**: GitHub issues for bug reports
- **Discussions**: GitHub discussions for questions
- **Email**: support@caain-soil-hub.com

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### Version 1.2.0 (Current)
- Added economic analysis to recommendations
- Enhanced regional performance data
- Improved filtering capabilities
- Added comprehensive developer documentation

### Version 1.1.0
- Added variety comparison endpoint
- Enhanced trait information
- Improved disease resistance data

### Version 1.0.0
- Initial release
- Basic variety recommendations
- Core filtering functionality
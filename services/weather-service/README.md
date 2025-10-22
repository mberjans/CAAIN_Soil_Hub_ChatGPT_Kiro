# Weather Impact Analysis Service

A microservice for analyzing weather data and its impact on agricultural operations, built with FastAPI and TimescaleDB.

## Overview

This service provides weather data fetching, analysis, and impact assessment for agricultural decision-making. It integrates with multiple weather data providers and offers APIs for:

- Current weather data retrieval
- Weather forecasting
- Agricultural impact analysis
- Historical pattern analysis

## Features

- **Multi-provider Weather Data**: Fetches weather data from multiple sources with automatic fallback
- **Real-time Analysis**: Provides immediate weather impact assessments for planting decisions
- **Historical Patterns**: Analyzes long-term weather trends using TimescaleDB continuous aggregates
- **Agricultural Focus**: Tailored algorithms for crop-specific weather impact analysis
- **RESTful API**: Clean, well-documented API endpoints for easy integration

## API Endpoints

### Health Check
- `GET /health` - Service health status

### Weather Data
- `GET /api/v1/weather/current` - Get current weather for a location
- `GET /api/v1/weather/forecast` - Get weather forecast for a location

### Impact Analysis
- `POST /api/v1/weather/analyze-planting` - Analyze planting conditions for specific crops

### Parameters
- **latitude**: Decimal degrees (-90 to 90)
- **longitude**: Decimal degrees (-180 to 180)
- **crop_type**: Supported crops (corn, soybean, wheat)

## Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Service

```bash
# Start the service
uvicorn src.main:app --port 8010 --reload
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_weather_models.py -v
```

## Database Schema

The service uses TimescaleDB for time-series weather data storage with:

- Hypertables for efficient time-series data storage
- Continuous aggregates for pre-computed analytics
- Standard relational tables for reference data

## Supported Crops

- **Corn**: Optimized planting condition analysis
- **Soybean**: Crop-specific weather thresholds
- **Wheat**: Variety-specific growth requirements

## Development

This service follows Test-Driven Development (TDD) principles with comprehensive test coverage.

## License

Proprietary - CAAIN Soil Hub Project
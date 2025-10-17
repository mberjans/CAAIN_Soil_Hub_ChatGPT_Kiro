# AFAS Fertilizer Strategy Optimization Service

A comprehensive fertilizer price tracking and market analysis service for the Autonomous Farm Advisory System (AFAS). This service provides real-time fertilizer pricing, historical trend analysis, and market intelligence to support agricultural decision-making.

## Features

### Real-Time Price Tracking
- **Multi-Source Data Integration**: USDA NASS, CME Group, manufacturer APIs, regional dealers
- **Product Coverage**: Nitrogen (urea, anhydrous ammonia), phosphorus (DAP, MAP), potassium (muriate of potash)
- **Regional Variations**: Price tracking across different geographic regions
- **Update Frequency**: 15-minute intervals with 24-hour data retention

### Market Analysis
- **Price Trend Analysis**: 7-day, 30-day, and 90-day trend calculations
- **Volatility Metrics**: Price volatility assessment for risk management
- **Market Intelligence**: Comprehensive market reports and outlook
- **Seasonal Analysis**: Seasonal price factor identification

### Performance & Reliability
- **Caching Layer**: Redis-based caching for sub-second response times
- **Fallback Mechanisms**: Graceful degradation with static fallback prices
- **Data Validation**: Agricultural domain validation for price accuracy
- **Error Handling**: Comprehensive error handling and logging

## API Endpoints

### Price Queries
- `GET /api/v1/fertilizer-prices/current/{product}` - Get current price for specific product
- `GET /api/v1/fertilizer-prices/current` - Get current prices for multiple products
- `POST /api/v1/fertilizer-prices/query` - Comprehensive price query with filters

### Trend Analysis
- `GET /api/v1/fertilizer-prices/trend/{product}` - Get price trend analysis
- `POST /api/v1/fertilizer-prices/update/{product}` - Update price data
- `POST /api/v1/fertilizer-prices/update-all` - Bulk price updates

### Reference Data
- `GET /api/v1/fertilizer-prices/products` - Available fertilizer products
- `GET /api/v1/fertilizer-prices/types` - Fertilizer type categories
- `GET /api/v1/fertilizer-prices/sources` - Data source information

## Installation

### Prerequisites
- Python 3.11+
- PostgreSQL with TimescaleDB extension
- Redis server
- Docker (optional)

### Setup
```bash
# Clone the repository
cd services/fertilizer-strategy

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database and Redis configuration

# Run database migrations
python -m alembic upgrade head

# Start the service
python src/main.py
```

### Docker Setup
```bash
# Build and run with Docker Compose
docker-compose up -d
```

## Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/fertilizer_strategy

# Redis
REDIS_URL=redis://localhost:6379

# Service
FERTILIZER_STRATEGY_PORT=8009

# External APIs (optional)
USDA_NASS_API_KEY=your_api_key
CME_GROUP_API_KEY=your_api_key
```

### Data Sources
The service integrates with multiple data sources:

1. **USDA NASS**: Official agricultural statistics and pricing
2. **CME Group**: Commodity futures and market data
3. **Manufacturer APIs**: Direct pricing from fertilizer manufacturers
4. **Regional Dealers**: Local dealer network pricing
5. **Fallback**: Static pricing for system resilience

## Usage Examples

### Get Current Urea Price
```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.get(
        "http://localhost:8009/api/v1/fertilizer-prices/current/urea",
        params={"region": "US"}
    )
    price_data = response.json()
    print(f"Urea price: ${price_data['price_per_unit']} per {price_data['unit']}")
```

### Get Price Trend Analysis
```python
async with httpx.AsyncClient() as client:
    response = await client.get(
        "http://localhost:8009/api/v1/fertilizer-prices/trend/urea",
        params={"region": "US", "days": 30}
    )
    trend = response.json()
    print(f"Trend: {trend['trend_direction']} ({trend['trend_strength']})")
    print(f"7-day change: {trend['trend_7d_percent']:.2f}%")
```

### Comprehensive Price Query
```python
query_request = {
    "fertilizer_types": ["nitrogen"],
    "regions": ["US", "CA"],
    "include_trend_analysis": True,
    "max_age_hours": 12
}

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8009/api/v1/fertilizer-prices/query",
        json=query_request
    )
    results = response.json()
    print(f"Found {results['total_results']} price records")
```

## Testing

### Run Tests
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test categories
pytest tests/ -m "not performance"  # Skip performance tests
pytest tests/ -m "agricultural"     # Only agricultural validation tests
```

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing
- **Performance Tests**: Response time and concurrency testing
- **Agricultural Validation**: Domain-specific accuracy testing

## Data Models

### FertilizerPriceData
```python
{
    "product_id": "urea_001",
    "product_name": "Urea",
    "fertilizer_type": "nitrogen",
    "specific_product": "urea",
    "price_per_unit": 450.0,
    "unit": "ton",
    "currency": "USD",
    "region": "US",
    "source": "usda_nass",
    "price_date": "2024-01-15",
    "confidence": 0.85,
    "volatility": 0.15,
    "market_conditions": {...},
    "seasonal_factors": {...}
}
```

### PriceTrendAnalysis
```python
{
    "product_id": "urea_001",
    "product_name": "Urea",
    "region": "US",
    "current_price": 450.0,
    "trend_7d_percent": 2.5,
    "trend_30d_percent": 5.0,
    "trend_direction": "up",
    "trend_strength": "moderate",
    "volatility_30d": 0.15,
    "data_points_used": 30
}
```

## Agricultural Use Cases

### Fertilizer Cost Analysis
- Real-time pricing for application planning
- Cost comparison across fertilizer types
- Regional price optimization

### Market Timing
- Price trend analysis for purchasing decisions
- Volatility assessment for risk management
- Seasonal price pattern identification

### Budget Planning
- Historical price analysis for budgeting
- Price forecasting for financial planning
- Cost-benefit analysis across products

### Strategic Planning
- Market intelligence for strategic decisions
- Multi-region price comparison
- Supply chain optimization

## Performance Metrics

### Response Times
- Current price queries: < 1 second
- Trend analysis: < 2 seconds
- Bulk updates: < 5 seconds

### Reliability
- 99.5% uptime target
- Graceful degradation with fallback prices
- Comprehensive error handling

### Data Quality
- Multi-source validation
- Agricultural domain validation
- Confidence scoring for all data

## Contributing

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install

# Run linting
flake8 src/
black src/
```

### Code Standards
- Type hints required for all functions
- Comprehensive docstrings
- Unit test coverage > 80%
- Agricultural domain validation

## License

This project is part of the AFAS (Autonomous Farm Advisory System) and follows the project's licensing terms.

## Support

For issues and questions:
- Create an issue in the project repository
- Contact the AFAS development team
- Check the documentation at `/docs` endpoint
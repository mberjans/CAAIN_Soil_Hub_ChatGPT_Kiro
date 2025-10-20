# Fertilizer Timing & Strategy Services - Integration Layer

## Overview

This integration layer enables REST API-based communication between the fertilizer-timing and fertilizer-strategy services, replacing direct Python imports with HTTP-based microservices architecture.

## Architecture

### Components Created

1. **Configuration Layer** (`fertilizer-timing/src/config/integration_config.py`)
   - Service endpoint configuration
   - Integration mode selection (direct_import, rest_api, hybrid)
   - Timeout and retry settings
   - Circuit breaker configuration

2. **HTTP Client Infrastructure** (`fertilizer-timing/src/clients/`)
   - `base_http_client.py` - Base HTTP client with resilience patterns
   - `fertilizer_strategy_client.py` - Fertilizer-strategy specific client
   - Circuit breaker implementation
   - Exponential backoff retry logic
   - Request/response logging

3. **REST API Endpoints** (`fertilizer-strategy/src/api/strategy_integration_routes.py`)
   - `POST /api/v1/strategy/timing-recommendations` - Timing optimization
   - `POST /api/v1/strategy/equipment-compatibility` - Equipment checks
   - `GET /api/v1/strategy/pricing-data` - Current fertilizer prices
   - `POST /api/v1/strategy/type-selection` - Fertilizer recommendations

4. **HTTP Adapter** (`fertilizer-timing/src/timing_services/timing_service_http.py`)
   - HTTP-based timing optimization adapter
   - Backward compatibility with direct import mode
   - Hybrid mode with automatic fallback

## Integration Modes

### 1. REST API Mode (Recommended for Production)
```bash
INTEGRATION_MODE=rest_api
```
- Uses HTTP REST APIs exclusively
- Full service decoupling
- No fallback to direct imports
- Best for production microservices deployment

### 2. Hybrid Mode (Recommended for Migration)
```bash
INTEGRATION_MODE=hybrid
```
- Tries REST API first
- Falls back to direct imports on failure
- Ideal for gradual migration
- Provides resilience during transition

### 3. Direct Import Mode (Legacy)
```bash
INTEGRATION_MODE=direct_import
```
- Uses Python module imports
- Tight coupling between services
- Legacy mode for backward compatibility

## Setup and Configuration

### 1. Environment Variables

Copy the example configuration:
```bash
cd services/fertilizer-timing
cp .env.example .env
```

Edit `.env` to configure your environment:
```bash
# Choose integration mode
INTEGRATION_MODE=hybrid

# Configure service URLs
FERTILIZER_STRATEGY_URL=http://localhost:8007
WEATHER_SERVICE_URL=http://localhost:8001
SOIL_SERVICE_URL=http://localhost:8002
CROP_SERVICE_URL=http://localhost:8003

# Enable features
ENABLE_CIRCUIT_BREAKER=true
ENABLE_RETRY=true
ENABLE_REQUEST_LOGGING=true
```

### 2. Install Dependencies

Add httpx to requirements.txt:
```bash
# In services/fertilizer-timing/
echo "httpx>=0.24.0" >> requirements.txt
pip install -r requirements.txt
```

### 3. Start Services

Start fertilizer-strategy service first:
```bash
cd services/fertilizer-strategy
python -m src.main
# Service runs on port 8007
```

Start fertilizer-timing service:
```bash
cd services/fertilizer-timing
python -m src.main
# Service runs on port 8009
```

## Usage Examples

### Using the HTTP Adapter

```python
from timing_services.timing_service_http import TimingOptimizationHTTPAdapter
from models import TimingOptimizationRequest, LocationData

# Create adapter (automatically uses configured mode)
adapter = TimingOptimizationHTTPAdapter()

# Create request
request = TimingOptimizationRequest(
    crop_type="corn",
    location=LocationData(latitude=42.5, longitude=-92.5),
    planting_date=date(2024, 5, 15),
    fertilizer_types=["urea", "MAP"],
    target_yield=180.0
)

# Get optimization results
result = await adapter.optimize(request)

# Clean up resources
await adapter.close()
```

### Direct Client Usage

```python
from clients.fertilizer_strategy_client import FertilizerStrategyClient

client = FertilizerStrategyClient()

# Get timing recommendations
result = await client.optimize_timing(request)

# Check equipment compatibility
compatibility = await client.check_equipment_compatibility(
    fertilizer_type="urea",
    application_method="broadcast",
    available_equipment=["spreader_001", "spreader_002"]
)

# Get current prices
prices = await client.get_current_prices(
    fertilizer_type="urea",
    location={"latitude": 42.5, "longitude": -92.5}
)

await client.close()
```

## Resilience Features

### Circuit Breaker Pattern

The circuit breaker prevents cascading failures:

```
CLOSED (normal) → OPEN (failures) → HALF_OPEN (testing) → CLOSED
```

Configuration:
```bash
FERTILIZER_STRATEGY_CIRCUIT_BREAKER_THRESHOLD=5  # Failures before opening
FERTILIZER_STRATEGY_CIRCUIT_BREAKER_TIMEOUT=60   # Seconds before testing recovery
```

### Retry Logic with Exponential Backoff

Automatic retries with increasing delays:
- Attempt 1: Immediate
- Attempt 2: 1.0s delay
- Attempt 3: 2.0s delay
- Attempt 4: 4.0s delay

Configuration:
```bash
FERTILIZER_STRATEGY_MAX_RETRIES=3
FERTILIZER_STRATEGY_RETRY_DELAY=1.0
```

### Request Timeouts

Prevent hanging requests:
```bash
FERTILIZER_STRATEGY_TIMEOUT=30  # seconds
```

## API Endpoints

### Timing Recommendations

**Endpoint:** `POST /api/v1/strategy/timing-recommendations`

**Request Body:**
```json
{
  "crop_type": "corn",
  "location": {
    "latitude": 42.5,
    "longitude": -92.5
  },
  "planting_date": "2024-05-15",
  "fertilizer_types": ["urea", "MAP"],
  "application_methods": ["broadcast"],
  "target_yield": 180.0
}
```

**Response:**
```json
{
  "optimal_timings": [
    {
      "fertilizer_type": "urea",
      "application_method": "broadcast",
      "recommended_date": "2024-06-10",
      "application_rate": 150.0,
      "confidence_score": 0.92
    }
  ],
  "confidence_score": 0.92,
  "optimization_notes": "Optimal timing based on crop stage and weather"
}
```

### Equipment Compatibility

**Endpoint:** `POST /api/v1/strategy/equipment-compatibility`

**Request Body:**
```json
{
  "fertilizer_type": "urea",
  "application_method": "broadcast",
  "equipment_list": ["spreader_001", "spreader_002", "injector_001"]
}
```

**Response:**
```json
{
  "compatible_equipment": ["spreader_001", "spreader_002"],
  "incompatible_equipment": ["injector_001"],
  "compatibility_details": {
    "spreader_001": {
      "compatible": true,
      "reason": "Compatible with broadcast application"
    }
  }
}
```

### Pricing Data

**Endpoint:** `GET /api/v1/strategy/pricing-data`

**Query Parameters:**
- `fertilizer_type` (optional): Specific fertilizer type
- `latitude` (optional): Location latitude
- `longitude` (optional): Location longitude

**Response:**
```json
{
  "prices": {
    "urea": {
      "price_per_unit": 450.0,
      "currency": "USD",
      "unit": "ton",
      "last_updated": "2024-01-15T10:30:00Z"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Type Selection

**Endpoint:** `POST /api/v1/strategy/type-selection`

**Request Body:**
```json
{
  "nutrient_requirements": {
    "N": 150,
    "P": 50,
    "K": 40
  },
  "soil_characteristics": {
    "pH": 6.5,
    "organic_matter": 3.2
  },
  "crop_type": "corn"
}
```

**Response:**
```json
{
  "recommended_types": [
    {
      "fertilizer_type": "Urea",
      "compatibility_score": 0.9,
      "nutrient_content": {"N": 46.0, "P": 0, "K": 0},
      "pros": ["High nitrogen content", "Cost-effective"],
      "cons": ["Volatilization risk"]
    }
  ]
}
```

## Testing

### Unit Tests

Run all integration layer tests:
```bash
cd services/fertilizer-timing
pytest tests/test_http_client.py -v
pytest tests/test_fertilizer_strategy_client.py -v
pytest tests/test_timing_service_http.py -v
```

### Test Coverage

The test suite includes:
- Circuit breaker functionality
- Retry logic with exponential backoff
- Error handling scenarios
- Hybrid mode fallback behavior
- Resource cleanup
- API endpoint contracts

### Integration Testing

Test with live services:
```bash
# Terminal 1: Start fertilizer-strategy
cd services/fertilizer-strategy
python -m src.main

# Terminal 2: Start fertilizer-timing
cd services/fertilizer-timing
INTEGRATION_MODE=rest_api python -m src.main

# Terminal 3: Run integration tests
cd services/fertilizer-timing
pytest tests/ -v -k integration
```

## Monitoring and Debugging

### Request Logging

Enable detailed request/response logging:
```bash
ENABLE_REQUEST_LOGGING=true
```

Logs include:
- Request method and URL
- Request parameters and body
- Response status and data
- Retry attempts
- Circuit breaker state changes

### Health Checks

Check service health:
```bash
# Fertilizer-strategy service
curl http://localhost:8007/health

# Fertilizer-timing service
curl http://localhost:8009/health
```

### Circuit Breaker Status

Monitor circuit breaker state in logs:
```
INFO - Circuit breaker: Closed (normal operation)
WARNING - Circuit breaker: Opening after 5 failures
INFO - Circuit breaker: Entering half-open state
INFO - Circuit breaker: Closing after successful recovery
```

## Migration Guide

### Phase 1: Deploy Integration Layer
1. Add new HTTP client code to fertilizer-timing
2. Deploy new REST API endpoints to fertilizer-strategy
3. Configure `INTEGRATION_MODE=hybrid`
4. Monitor for errors and fallback usage

### Phase 2: Validate REST API
1. Verify all API endpoints working correctly
2. Check circuit breaker and retry logic
3. Monitor performance and latency
4. Address any issues found

### Phase 3: Switch to REST API Mode
1. Set `INTEGRATION_MODE=rest_api`
2. Monitor for several days
3. Verify no fallback to direct imports needed
4. Document any edge cases

### Phase 4: Clean Up (Optional)
1. Remove direct import fallback code
2. Update documentation
3. Archive legacy integration code

## Performance Considerations

### HTTP Overhead
- Typical latency: 10-50ms added per request
- Mitigated by connection pooling
- Consider caching for frequently accessed data

### Connection Pooling
- HTTP client reuses connections
- Reduces connection establishment overhead
- Configurable via httpx settings

### Caching Strategies
- Cache pricing data (update hourly)
- Cache crop metadata (update daily)
- Cache equipment compatibility rules

## Troubleshooting

### Common Issues

**Issue:** Connection refused errors
```
ServiceError: Failed to communicate with fertilizer-strategy
```
**Solution:** Verify fertilizer-strategy service is running on configured port

**Issue:** Circuit breaker opens frequently
```
WARNING - Circuit breaker: Opening after 5 failures
```
**Solution:**
- Check fertilizer-strategy service health
- Increase circuit breaker threshold
- Increase timeout values

**Issue:** Slow response times
```
Request took 5.2s to complete
```
**Solution:**
- Check network latency between services
- Consider caching frequently accessed data
- Increase timeout if processing is legitimately slow

## Files Created

### Fertilizer-Timing Service
```
services/fertilizer-timing/
├── src/
│   ├── config/
│   │   └── integration_config.py          # Configuration management
│   ├── clients/
│   │   ├── __init__.py
│   │   ├── base_http_client.py           # Base HTTP client
│   │   └── fertilizer_strategy_client.py  # Strategy service client
│   └── timing_services/
│       └── timing_service_http.py         # HTTP-based adapter
├── tests/
│   ├── test_http_client.py               # HTTP client tests
│   ├── test_fertilizer_strategy_client.py # Strategy client tests
│   └── test_timing_service_http.py       # HTTP adapter tests
└── .env.example                           # Configuration template
```

### Fertilizer-Strategy Service
```
services/fertilizer-strategy/
└── src/
    └── api/
        └── strategy_integration_routes.py  # REST API endpoints
```

## Next Steps

1. **Deploy to Development Environment**
   - Test with hybrid mode
   - Monitor performance and errors
   - Validate all endpoints

2. **Performance Testing**
   - Load testing with concurrent requests
   - Latency measurements
   - Circuit breaker stress testing

3. **Production Deployment**
   - Deploy to staging environment
   - Gradual rollout with monitoring
   - Switch to rest_api mode

4. **Documentation**
   - API documentation (OpenAPI/Swagger)
   - Runbooks for operations team
   - Architecture diagrams

## Support

For questions or issues:
1. Check logs for detailed error messages
2. Verify service configurations
3. Test health check endpoints
4. Review circuit breaker states

## License

Part of CAAIN Soil Hub project.

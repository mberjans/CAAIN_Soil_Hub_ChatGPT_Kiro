# Integration Layer - Quick Start Guide

**UPDATED FOR TICKET-006:** Port assignments have changed to avoid conflicts.

## Service Ports (Updated)
- **fertilizer-strategy:** http://localhost:8009 (unchanged)
- **fertilizer-timing:** http://localhost:8010 (changed from 8009)

## 5-Minute Setup

### 1. Install Dependencies

```bash
# Fertilizer-timing service
cd /Users/Mark/Research/CAAIN_Soil_Hub/CAAIN_Soil_Hub_ChatGPT_Kiro/services/fertilizer-timing
echo "httpx>=0.24.0" >> requirements.txt
pip install -r requirements.txt

# Fertilizer-strategy service (if needed)
cd /Users/Mark/Research/CAAIN_Soil_Hub/CAAIN_Soil_Hub_ChatGPT_Kiro/services/fertilizer-strategy
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example configuration
cd /Users/Mark/Research/CAAIN_Soil_Hub/CAAIN_Soil_Hub_ChatGPT_Kiro/services/fertilizer-timing
cp .env.example .env

# Edit .env if needed (defaults should work for local development)
# INTEGRATION_MODE=rest_api
# FERTILIZER_STRATEGY_URL=http://localhost:8009
# FERTILIZER_TIMING_SERVICE_PORT=8010

# Fertilizer-strategy configuration
cd /Users/Mark/Research/CAAIN_Soil_Hub/CAAIN_Soil_Hub_ChatGPT_Kiro/services/fertilizer-strategy
cp .env.example .env

# FERTILIZER_STRATEGY_PORT=8009
# FERTILIZER_TIMING_URL=http://localhost:8010
```

### 3. Start Services

```bash
# Terminal 1: Start fertilizer-strategy service (port 8009)
cd /Users/Mark/Research/CAAIN_Soil_Hub/CAAIN_Soil_Hub_ChatGPT_Kiro/services/fertilizer-strategy
python -m src.main
# ✅ Service running on http://localhost:8009

# Terminal 2: Start fertilizer-timing service (port 8010)
cd /Users/Mark/Research/CAAIN_Soil_Hub/CAAIN_Soil_Hub_ChatGPT_Kiro/services/fertilizer-timing
python -m src.main
# ✅ Service running on http://localhost:8010
```

### 4. Test Integration

```bash
# Check health
curl http://localhost:8009/health  # fertilizer-strategy
curl http://localhost:8010/health  # fertilizer-timing

# Test integrated endpoint (NEW!)
curl -X POST http://localhost:8009/api/v1/integrated/strategy-with-timing \
  -H "Content-Type: application/json" \
  -d '{
    "crop_type": "corn",
    "field_size": 160,
    "location": {"latitude": 42.5, "longitude": -92.5},
    "planting_date": "2024-05-15",
    "soil_characteristics": {"pH": 6.5, "N": 20, "P": 30, "K": 150},
    "nutrient_requirements": {"N": 180, "P": 60, "K": 40}
  }'
```

### 5. Run Tests

```bash
cd /Users/Mark/Research/CAAIN_Soil_Hub/CAAIN_Soil_Hub_ChatGPT_Kiro/services/fertilizer-timing

# Run all integration tests
pytest tests/test_http_client.py -v
pytest tests/test_fertilizer_strategy_client.py -v
pytest tests/test_timing_service_http.py -v

# Or run all at once
pytest tests/test_*http*.py -v
```

## Usage Examples

### Python Code

```python
from timing_services.timing_service_http import TimingOptimizationHTTPAdapter
from models import TimingOptimizationRequest, LocationData
from datetime import date

# Initialize adapter (uses configuration from .env)
adapter = TimingOptimizationHTTPAdapter()

# Create request
request = TimingOptimizationRequest(
    crop_type="corn",
    location=LocationData(latitude=42.5, longitude=-92.5),
    planting_date=date(2024, 5, 15),
    fertilizer_types=["urea", "MAP"],
    application_methods=["broadcast"],
    target_yield=180.0
)

# Get optimization results
result = await adapter.optimize(request)
print(f"Confidence: {result.confidence_score}")
print(f"Recommendations: {len(result.optimal_timings)}")

# Clean up
await adapter.close()
```

### cURL Examples

```bash
# Equipment compatibility check
curl -X POST http://localhost:8009/api/v1/strategy/equipment-compatibility \
  -H "Content-Type: application/json" \
  -d '{
    "fertilizer_type": "urea",
    "application_method": "broadcast",
    "equipment_list": ["spreader_001", "spreader_002", "injector_001"]
  }'

# Get pricing data
curl "http://localhost:8009/api/v1/strategy/pricing-data?fertilizer_type=urea"

# Get pricing with location
curl "http://localhost:8009/api/v1/strategy/pricing-data?fertilizer_type=urea&latitude=42.5&longitude=-92.5"

# Type selection
curl -X POST http://localhost:8009/api/v1/strategy/type-selection \
  -H "Content-Type: application/json" \
  -d '{
    "nutrient_requirements": {"N": 150, "P": 50, "K": 40},
    "soil_characteristics": {"pH": 6.5, "organic_matter": 3.2},
    "crop_type": "corn"
  }'
```

## Integration Modes

### Switch to REST API Only

```bash
# Edit .env
INTEGRATION_MODE=rest_api

# Restart fertilizer-timing service
# Now uses HTTP exclusively, no fallback
```

### Switch to Direct Import (Legacy)

```bash
# Edit .env
INTEGRATION_MODE=direct_import

# Restart fertilizer-timing service
# Uses Python imports, no HTTP calls
```

### Use Hybrid (Default - Recommended)

```bash
# Edit .env
INTEGRATION_MODE=hybrid

# Restart fertilizer-timing service
# Tries HTTP first, falls back to imports
```

## Troubleshooting

### Connection Refused

```
Error: Connection refused to localhost:8009
```

**Fix:** Make sure fertilizer-strategy service is running on port 8009
```bash
cd /Users/Mark/Research/CAAIN_Soil_Hub/CAAIN_Soil_Hub_ChatGPT_Kiro/services/fertilizer-strategy
python -m src.main
# Should show: Running on http://localhost:8009
```

### Import Errors

```
ImportError: No module named 'httpx'
```

**Fix:** Install httpx
```bash
pip install httpx
```

### Circuit Breaker Open

```
ServiceUnavailableError: Circuit breaker open
```

**Fix:** Service is down or having issues
1. Check fertilizer-strategy service health
2. Check logs for errors
3. Restart services if needed

### Slow Responses

```
Request took 5+ seconds
```

**Fix:** Increase timeout in .env
```bash
FERTILIZER_STRATEGY_TIMEOUT=60
```

## File Locations

All files are in:
```
/Users/Mark/Research/CAAIN_Soil_Hub/CAAIN_Soil_Hub_ChatGPT_Kiro/
```

### Key Files

**Configuration:**
- `services/fertilizer-timing/.env.example` - Configuration template
- `services/fertilizer-timing/src/config/integration_config.py` - Config loader

**HTTP Clients:**
- `services/fertilizer-timing/src/clients/base_http_client.py` - Base client
- `services/fertilizer-timing/src/clients/fertilizer_strategy_client.py` - Strategy client

**REST API:**
- `services/fertilizer-strategy/src/api/strategy_integration_routes.py` - API endpoints

**Adapter:**
- `services/fertilizer-timing/src/timing_services/timing_service_http.py` - HTTP adapter

**Tests:**
- `services/fertilizer-timing/tests/test_http_client.py`
- `services/fertilizer-timing/tests/test_fertilizer_strategy_client.py`
- `services/fertilizer-timing/tests/test_timing_service_http.py`

**Documentation:**
- `INTEGRATION_LAYER_README.md` - Full documentation (600+ lines)
- `INTEGRATION_QUICKSTART.md` - This file (UPDATED)
- `TICKET-006_fertilizer-timing-optimization-14.1_IMPLEMENTATION_COMPLETE.md` - Complete implementation details (NEW!)
- `TICKET-006_fertilizer-timing-optimization-14.1_IMPLEMENTATION_SUMMARY.md` - Original analysis

## Next Steps

1. ✅ Services running locally
2. ✅ Tests passing
3. ➡️ Deploy to development environment
4. ➡️ Performance testing
5. ➡️ Production deployment

## API Documentation

View interactive API docs:
- Fertilizer-Strategy: http://localhost:8009/docs (includes NEW integrated endpoints!)
- Fertilizer-Timing: http://localhost:8010/docs

## Support

For detailed information, see:
- **Full Guide:** `INTEGRATION_LAYER_README.md`
- **Implementation Summary:** `TICKET-006_fertilizer-timing-optimization-14.1_IMPLEMENTATION_SUMMARY.md`
- **Analysis Report:** `fertilizer_timing_integration_analysis.md`

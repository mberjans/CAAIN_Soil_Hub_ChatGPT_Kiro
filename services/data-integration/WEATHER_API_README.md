# Weather API Integration - AFAS Data Integration Service

## Overview

The Weather API integration provides comprehensive weather data for agricultural decision making through the AFAS (Autonomous Farm Advisory System). This implementation integrates with multiple weather services including NOAA and OpenWeatherMap with robust fallback mechanisms.

## Features

### 🌤️ Multi-Source Weather Data
- **NOAA National Weather Service** (Primary, free)
- **OpenWeatherMap** (Fallback, requires API key)
- **Graceful degradation** to default values when all services fail

### 🌡️ Current Weather Data
- Temperature, humidity, precipitation
- Wind speed and direction
- Atmospheric pressure and visibility
- UV index (when available)
- Real-time conditions

### 📅 Weather Forecasting
- Up to 14-day forecasts
- Daily high/low temperatures
- Precipitation probability and amounts
- Wind and humidity forecasts
- Agricultural planning support

### 🌾 Agricultural Weather Metrics
- **Growing Degree Days (GDD)** calculation
- **Accumulated precipitation** tracking
- **Days since rain** monitoring
- **Soil temperature** estimation
- **Evapotranspiration** estimates
- **Agricultural recommendations** based on conditions

## API Endpoints

### Current Weather
```http
POST /api/v1/weather/current
Content-Type: application/json

{
  "latitude": 42.0308,
  "longitude": -93.6319
}
```

**Response:**
```json
{
  "temperature_f": 72.5,
  "humidity_percent": 65.0,
  "precipitation_inches": 0.1,
  "wind_speed_mph": 8.5,
  "wind_direction": "SW",
  "conditions": "Partly Cloudy",
  "pressure_mb": 1013.25,
  "visibility_miles": 10.0,
  "uv_index": 5.0,
  "timestamp": "2024-12-09T15:30:00Z",
  "source": "NOAA/OpenWeatherMap"
}
```

### Weather Forecast
```http
POST /api/v1/weather/forecast?days=7
Content-Type: application/json

{
  "latitude": 42.0308,
  "longitude": -93.6319
}
```

**Response:**
```json
[
  {
    "date": "2024-12-09",
    "high_temp_f": 75.0,
    "low_temp_f": 55.0,
    "precipitation_chance": 20.0,
    "precipitation_amount": 0.0,
    "conditions": "Sunny",
    "wind_speed_mph": 8.0,
    "humidity_percent": 60.0
  }
]
```

### Agricultural Weather Metrics
```http
POST /api/v1/weather/agricultural-metrics?base_temp_f=50.0
Content-Type: application/json

{
  "latitude": 42.0308,
  "longitude": -93.6319
}
```

**Response:**
```json
{
  "growing_degree_days": 22.5,
  "accumulated_precipitation": 0.8,
  "days_since_rain": 3,
  "soil_temperature_f": 67.5,
  "evapotranspiration_inches": 0.15,
  "recommendations": [
    "Consider irrigation - extended dry period detected",
    "Monitor crop development closely due to high GDD accumulation"
  ]
}
```

## Configuration

### Environment Variables

Create a `.env` file in the service directory:

```bash
# Service Configuration
DATA_INTEGRATION_PORT=8003
LOG_LEVEL=INFO

# Weather API Keys
OPENWEATHER_API_KEY=your_api_key_here

# Optional: Rate limiting and caching
WEATHER_API_RATE_LIMIT=1000
WEATHER_CACHE_TTL=300
```

### API Key Setup

1. **NOAA**: No API key required (free public API)
2. **OpenWeatherMap**: 
   - Sign up at https://openweathermap.org/api
   - Get free API key (1000 calls/day)
   - Set `OPENWEATHER_API_KEY` environment variable

## Installation & Setup

### 1. Install Dependencies
```bash
cd services/data-integration
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Start Service
```bash
# Option 1: Direct startup
python start_service.py

# Option 2: Using uvicorn
source venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 8003 --reload
```

### 4. Verify Installation
```bash
# Test weather service functionality
python test_weather_manual.py

# Test API endpoints (requires service running)
python test_api_endpoints.py
```

## Testing

### Unit Tests
```bash
source venv/bin/activate
python -m pytest tests/test_weather_service.py -v
```

### Integration Tests
```bash
# Test with real APIs (requires API keys)
python -m pytest tests/test_weather_service.py::TestWeatherAPIIntegration -v
```

### Manual Testing
```bash
# Test weather service directly
python test_weather_manual.py

# Test API endpoints
curl -X POST "http://localhost:8003/api/v1/weather/current" \
     -H "Content-Type: application/json" \
     -d '{"latitude": 42.0308, "longitude": -93.6319}'
```

## Agricultural Use Cases

### 1. Crop Planning
- **Growing Degree Days**: Track heat accumulation for crop development
- **Frost Risk**: Monitor temperature forecasts for planting timing
- **Precipitation**: Plan irrigation and field operations

### 2. Field Operations
- **Spray Conditions**: Check wind speed and precipitation for pesticide application
- **Harvest Timing**: Monitor weather windows for harvest operations
- **Soil Conditions**: Estimate soil moisture and trafficability

### 3. Risk Management
- **Drought Monitoring**: Track days without rain and precipitation deficits
- **Disease Pressure**: Monitor humidity and precipitation for disease risk
- **Stress Conditions**: Identify heat stress and extreme weather events

## Error Handling & Reliability

### Fallback Strategy
1. **Primary**: NOAA National Weather Service (free, reliable)
2. **Secondary**: OpenWeatherMap (requires API key)
3. **Fallback**: Default/historical values with clear warnings

### Error Types
- **API Unavailable**: Service temporarily down
- **Rate Limited**: Too many requests
- **Invalid Location**: Coordinates outside service area
- **Network Issues**: Connection problems

### Monitoring
- Structured logging with agricultural context
- Performance metrics and response times
- API success/failure rates
- Agricultural recommendation accuracy

## Agricultural Accuracy

### Data Sources
- **NOAA**: Official US weather data, high accuracy
- **OpenWeatherMap**: Global coverage, good accuracy
- **Agricultural Calibration**: Metrics tuned for farming applications

### Validation
- Cross-reference multiple weather sources
- Agricultural expert review of calculations
- Field validation with actual farm conditions
- Continuous improvement based on farmer feedback

## Performance

### Response Times
- **Current Weather**: < 2 seconds
- **7-day Forecast**: < 3 seconds
- **Agricultural Metrics**: < 1 second (calculated locally)

### Caching
- Weather data cached for 5 minutes
- Forecast data cached for 1 hour
- Agricultural metrics calculated on-demand

### Rate Limits
- NOAA: No official limits (reasonable use)
- OpenWeatherMap: 1000 calls/day (free tier)
- Internal rate limiting to prevent abuse

## Future Enhancements

### Planned Features
- **Historical Weather Data**: Long-term climate analysis
- **Weather Alerts**: Severe weather notifications
- **Microclimate Modeling**: Field-specific weather estimates
- **Satellite Data Integration**: Precipitation radar and imagery

### Agricultural Enhancements
- **Crop-Specific GDD**: Different base temperatures by crop
- **Pest/Disease Models**: Weather-based risk calculations
- **Irrigation Scheduling**: ET-based water management
- **Yield Forecasting**: Weather impact on crop yields

## Support

### Documentation
- API documentation: `http://localhost:8003/docs`
- Health check: `http://localhost:8003/health`
- This README: Complete setup and usage guide

### Troubleshooting
1. **Service won't start**: Check Python dependencies and port availability
2. **API errors**: Verify API keys and network connectivity
3. **Inaccurate data**: Check coordinate validity and service status
4. **Performance issues**: Monitor API rate limits and caching

### Contact
- Technical issues: Check logs and error messages
- Agricultural accuracy: Consult with agricultural experts
- Feature requests: Submit through project management system

---

**Status**: ✅ **COMPLETED** - Weather API integration fully implemented and tested
**Last Updated**: December 9, 2024
**Version**: 1.0.0
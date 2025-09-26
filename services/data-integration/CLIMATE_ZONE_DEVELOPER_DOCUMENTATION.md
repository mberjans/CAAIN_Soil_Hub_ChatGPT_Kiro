# Climate Zone Detection - Developer Documentation

## 🏗️ Architecture Overview

The Climate Zone Detection system is built as a modular, scalable service within the CAAIN Soil Hub platform. It provides comprehensive climate zone analysis for agricultural applications through multiple complementary approaches.

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Climate Zone Detection                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   API Layer     │  │  Service Layer  │  │  Data Layer  │ │
│  │                 │  │                 │  │              │ │
│  │ • climate_routes│  │ • climate_zone_ │  │ • USDA API   │ │
│  │   .py           │  │   service.py    │  │ • Weather    │ │
│  │                 │  │ • koppen_       │  │   APIs       │ │
│  │                 │  │   climate_      │  │ • Cache      │ │
│  │                 │  │   service.py    │  │   Store      │ │
│  │                 │  │ • coordinate_   │  │              │ │
│  │                 │  │   climate_      │  │              │ │
│  │                 │  │   detector.py   │  │              │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                   Integration Layer                     │ │
│  │                                                         │ │
│  │ • weather_climate_inference.py                          │ │
│  │ • address_climate_lookup.py                             │ │
│  │ • usda_zone_api.py                                      │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Core Services

### 1. Climate Zone Service (`climate_zone_service.py`)

The main orchestration service that coordinates climate zone detection through multiple methods.

#### Key Classes

```python
class ClimateZoneService:
    """Main climate zone detection service"""
    
    def __init__(self, weather_service: WeatherService, cache_service: CacheService):
        self.weather_service = weather_service
        self.cache_service = cache_service
        self.coordinate_detector = CoordinateClimateDetector()
        self.koppen_service = KoppenClimateService()
        self.usda_api = USDAZoneAPI()
    
    async def detect_zone(self, latitude: float, longitude: float) -> ClimateZoneResult:
        """Primary detection method with multi-source validation"""
        
    async def get_zone_characteristics(self, zone: str) -> ZoneCharacteristics:
        """Get detailed characteristics for a climate zone"""
        
    async def validate_zone_for_location(self, zone: str, lat: float, lon: float) -> ValidationResult:
        """Validate if a climate zone is appropriate for given coordinates"""
```

#### Detection Flow

```python
# 1. Cache Check
cache_key = f"climate_zone:{latitude}:{longitude}"
cached_result = await self.cache_service.get(cache_key)

# 2. Multi-Source Detection
usda_result = await self.usda_api.get_zone(latitude, longitude)
koppen_result = await self.koppen_service.classify_climate(weather_data)
coordinate_result = await self.coordinate_detector.detect_zone(latitude, longitude)

# 3. Consensus Algorithm
final_result = self._build_consensus([usda_result, koppen_result, coordinate_result])

# 4. Cache & Return
await self.cache_service.set(cache_key, final_result, ttl=86400)  # 24 hours
return final_result
```

### 2. Köppen Climate Service (`koppen_climate_service.py`)

Implements the Köppen climate classification system with agricultural context.

#### Climate Types Supported

```python
KOPPEN_TYPES = {
    # Tropical (A)
    'Af': 'Tropical Rainforest',
    'Am': 'Tropical Monsoon',
    'Aw': 'Tropical Savanna',
    
    # Arid (B)
    'BWh': 'Hot Desert',
    'BWk': 'Cold Desert',
    'BSh': 'Hot Semi-Arid',
    'BSk': 'Cold Semi-Arid',
    
    # Temperate (C)
    'Cfa': 'Humid Subtropical',
    'Cfb': 'Temperate Oceanic',
    'Cfc': 'Subpolar Oceanic',
    'Csa': 'Mediterranean Hot Summer',
    'Csb': 'Mediterranean Warm Summer',
    'Csc': 'Mediterranean Cool Summer',
    'Cwa': 'Monsoon Subtropical',
    'Cwb': 'Subtropical Highland',
    'Cwc': 'Cool Subtropical Highland',
    
    # Continental (D)
    'Dfa': 'Hot Summer Humid Continental',
    'Dfb': 'Warm Summer Humid Continental',
    'Dfc': 'Subarctic',
    'Dfd': 'Extremely Cold Subarctic',
    'Dsa': 'Mediterranean Continental',
    'Dsb': 'Continental Mediterranean',
    'Dsc': 'Continental Subarctic',
    'Dsd': 'Extremely Cold Continental',
    'Dwa': 'Monsoon Continental',
    'Dwb': 'Continental Monsoon',
    'Dwc': 'Continental Subarctic Monsoon',
    'Dwd': 'Extremely Cold Continental Monsoon',
    
    # Polar (E)
    'ET': 'Tundra',
    'EF': 'Ice Cap'
}
```

#### Agricultural Suitability Mapping

```python
async def get_agricultural_suitability(self, koppen_type: str) -> AgricultureSuitability:
    """Get agricultural suitability for Köppen climate type"""
    
    suitability_map = {
        'Cfa': {  # Humid Subtropical
            'suitable_crops': ['corn', 'soybeans', 'cotton', 'rice'],
            'growing_season_days': 200,
            'frost_risk': 'low',
            'water_availability': 'good',
            'farming_intensity': 'high'
        },
        'Dfb': {  # Warm Summer Humid Continental
            'suitable_crops': ['wheat', 'corn', 'soybeans', 'barley'],
            'growing_season_days': 150,
            'frost_risk': 'moderate',
            'water_availability': 'moderate',
            'farming_intensity': 'moderate'
        },
        # ... additional mappings
    }
    
    return suitability_map.get(koppen_type, self._get_default_suitability())
```

### 3. Coordinate Climate Detector (`coordinate_climate_detector.py`)

Provides direct climate zone detection from GPS coordinates with elevation and microclimate adjustments.

#### Detection Algorithm

```python
class CoordinateClimateDetector:
    def __init__(self):
        self.elevation_service = ElevationService()
        self.microclimate_analyzer = MicroclimatAnalyzer()
    
    async def detect_zone(self, latitude: float, longitude: float) -> CoordinateZoneResult:
        """Detect climate zone from coordinates"""
        
        # 1. Base zone calculation from lat/lon
        base_zone = self._calculate_base_zone(latitude, longitude)
        
        # 2. Elevation adjustment
        elevation = await self.elevation_service.get_elevation(latitude, longitude)
        adjusted_zone = self._adjust_for_elevation(base_zone, elevation)
        
        # 3. Microclimate analysis
        microclimate_factors = await self.microclimate_analyzer.analyze(
            latitude, longitude, elevation
        )
        final_zone = self._apply_microclimate_adjustments(
            adjusted_zone, microclimate_factors
        )
        
        return CoordinateZoneResult(
            zone=final_zone,
            confidence=self._calculate_confidence(base_zone, adjusted_zone, final_zone),
            factors=microclimate_factors
        )
```

#### Elevation Adjustments

```python
def _adjust_for_elevation(self, base_zone: str, elevation_ft: float) -> str:
    """Adjust climate zone for elevation effects"""
    
    # Temperature lapse rate: -3.5°F per 1000 feet
    temp_adjustment = -3.5 * (elevation_ft / 1000.0)
    
    # Convert zone to temperature range
    zone_temp = self._zone_to_temp_range(base_zone)
    adjusted_temp = zone_temp + temp_adjustment
    
    # Convert back to zone
    return self._temp_range_to_zone(adjusted_temp)
```

### 4. Weather Climate Inference (`weather_climate_inference.py`)

Analyzes historical weather data to infer climate zones and agricultural indicators.

#### Growing Degree Days Calculation

```python
class WeatherClimateInference:
    async def calculate_growing_degree_days(
        self, 
        weather_data: List[DailyWeather], 
        base_temp: float = 50.0
    ) -> GDDResult:
        """Calculate Growing Degree Days for crop planning"""
        
        total_gdd = 0
        daily_gdd = []
        
        for day in weather_data:
            daily_avg = (day.temp_max + day.temp_min) / 2.0
            gdd = max(0, daily_avg - base_temp)
            total_gdd += gdd
            daily_gdd.append(gdd)
        
        return GDDResult(
            total_gdd=total_gdd,
            daily_gdd=daily_gdd,
            base_temperature=base_temp,
            calculation_period=len(weather_data)
        )
```

#### Frost Date Analysis

```python
async def calculate_frost_dates(
    self, 
    historical_data: List[YearlyWeather]
) -> FrostDates:
    """Calculate average first and last frost dates"""
    
    last_spring_frosts = []
    first_fall_frosts = []
    
    for year_data in historical_data:
        # Find last spring frost (temperature <= 32°F)
        last_spring = self._find_last_spring_frost(year_data.spring_data)
        if last_spring:
            last_spring_frosts.append(last_spring)
        
        # Find first fall frost
        first_fall = self._find_first_fall_frost(year_data.fall_data)
        if first_fall:
            first_fall_frosts.append(first_fall)
    
    return FrostDates(
        average_last_spring_frost=self._calculate_average_date(last_spring_frosts),
        average_first_fall_frost=self._calculate_average_date(first_fall_frosts),
        growing_season_length=self._calculate_growing_season_length(
            last_spring_frosts, first_fall_frosts
        )
    )
```

## 🔄 API Integration

### REST API Endpoints

#### `/api/climate-zone/detect`
Detect climate zone from coordinates.

```python
@router.post("/detect")
async def detect_climate_zone(request: ClimateZoneRequest) -> ClimateZoneResponse:
    """
    Detect climate zone from latitude/longitude coordinates.
    
    Request:
    {
        "latitude": 42.0308,
        "longitude": -93.6319,
        "include_characteristics": true,
        "include_agricultural_info": true
    }
    
    Response:
    {
        "climate_zone": "5b",
        "koppen_classification": "Dfa",
        "confidence_score": 0.92,
        "characteristics": {
            "avg_min_temp_winter": -15.0,
            "avg_max_temp_summer": 85.2,
            "annual_precipitation": 34.2,
            "growing_season_days": 165
        },
        "agricultural_info": {
            "suitable_crops": ["corn", "soybeans", "wheat"],
            "frost_dates": {
                "last_spring": "2024-04-20",
                "first_fall": "2024-10-15"
            },
            "growing_degree_days_annual": 2850
        }
    }
    """
```

#### `/api/climate-zone/batch-detect`
Batch climate zone detection for multiple locations.

```python
@router.post("/batch-detect")
async def batch_detect_climate_zones(
    request: BatchClimateZoneRequest
) -> BatchClimateZoneResponse:
    """
    Detect climate zones for multiple locations in a single request.
    
    Request:
    {
        "locations": [
            {"latitude": 42.0308, "longitude": -93.6319, "id": "farm_1"},
            {"latitude": 39.7391, "longitude": -104.9847, "id": "farm_2"}
        ],
        "include_characteristics": true
    }
    
    Response:
    {
        "results": [
            {
                "id": "farm_1",
                "climate_zone": "5b",
                "confidence_score": 0.92,
                "characteristics": {...}
            },
            {
                "id": "farm_2", 
                "climate_zone": "6a",
                "confidence_score": 0.88,
                "characteristics": {...}
            }
        ],
        "processing_time_ms": 1250
    }
    """
```

#### `/api/climate-zone/characteristics/{zone}`
Get detailed characteristics for a specific climate zone.

```python
@router.get("/characteristics/{zone}")
async def get_zone_characteristics(zone: str) -> ZoneCharacteristicsResponse:
    """
    Get detailed characteristics for a climate zone.
    
    Response:
    {
        "zone": "5b",
        "temperature_ranges": {
            "min_winter": -15.0,
            "max_winter": -10.0,
            "min_summer": 65.0,
            "max_summer": 85.0
        },
        "precipitation": {
            "annual_average": 34.2,
            "summer_percentage": 60,
            "winter_percentage": 40
        },
        "growing_conditions": {
            "growing_season_days": 165,
            "frost_free_days": 140,
            "suitable_plants": ["corn", "soybeans", "apple_trees"]
        },
        "agricultural_considerations": {
            "soil_freeze_depth": 24,
            "heating_degree_days": 4200,
            "cooling_degree_days": 850
        }
    }
    """
```

### Service Integration

#### Integration with Recommendation Engine

```python
# In recommendation-engine service
class CropRecommendationService:
    def __init__(self):
        self.climate_client = ClimateZoneClient(base_url="http://data-integration:8000")
    
    async def get_crop_recommendations(
        self, 
        latitude: float, 
        longitude: float,
        soil_data: SoilData
    ) -> CropRecommendations:
        
        # Get climate zone information
        climate_info = await self.climate_client.detect_climate_zone(
            latitude, longitude, include_agricultural_info=True
        )
        
        # Filter crops by climate suitability
        suitable_crops = self._filter_crops_by_climate(
            climate_info.agricultural_info.suitable_crops,
            climate_info.characteristics
        )
        
        # Combine with soil suitability
        final_recommendations = self._combine_climate_soil_suitability(
            suitable_crops, soil_data, climate_info
        )
        
        return final_recommendations
```

## 📊 Data Models

### Core Data Structures

```python
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import date

class ClimateZoneResult(BaseModel):
    """Primary climate zone detection result"""
    climate_zone: str
    koppen_classification: Optional[str]
    confidence_score: float
    detection_method: str
    characteristics: Optional['ZoneCharacteristics']
    agricultural_info: Optional['AgriculturalInfo']

class ZoneCharacteristics(BaseModel):
    """Detailed climate zone characteristics"""
    avg_min_temp_winter: float
    avg_max_temp_summer: float
    annual_precipitation: float
    growing_season_days: int
    frost_free_days: int
    heating_degree_days: int
    cooling_degree_days: int

class AgriculturalInfo(BaseModel):
    """Agricultural information for climate zone"""
    suitable_crops: List[str]
    frost_dates: 'FrostDates'
    growing_degree_days_annual: int
    water_requirements: str
    soil_considerations: List[str]

class FrostDates(BaseModel):
    """Frost date information"""
    last_spring_frost: Optional[date]
    first_fall_frost: Optional[date]
    growing_season_length: int
    frost_probability_10_percent: Optional[date]
    frost_probability_90_percent: Optional[date]
```

## 🚀 Performance Optimization

### Caching Strategy

```python
class ClimateZoneCacheManager:
    """Intelligent caching for climate zone data"""
    
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.default_ttl = 86400  # 24 hours
    
    async def get_climate_zone(self, latitude: float, longitude: float) -> Optional[ClimateZoneResult]:
        """Get cached climate zone with coordinate rounding for cache efficiency"""
        
        # Round coordinates to reasonable precision for caching
        rounded_lat = round(latitude, 3)  # ~100m precision
        rounded_lon = round(longitude, 3)
        
        cache_key = f"climate_zone:{rounded_lat}:{rounded_lon}"
        cached_data = await self.redis.get(cache_key)
        
        if cached_data:
            return ClimateZoneResult.parse_raw(cached_data)
        return None
    
    async def set_climate_zone(
        self, 
        latitude: float, 
        longitude: float, 
        result: ClimateZoneResult
    ):
        """Cache climate zone result with intelligent TTL"""
        
        rounded_lat = round(latitude, 3)
        rounded_lon = round(longitude, 3)
        cache_key = f"climate_zone:{rounded_lat}:{rounded_lon}"
        
        # Longer TTL for high-confidence results
        ttl = self.default_ttl if result.confidence_score < 0.9 else self.default_ttl * 7
        
        await self.redis.setex(
            cache_key, 
            ttl, 
            result.json()
        )
```

### Database Schema

```sql
-- Climate zone cache table
CREATE TABLE climate_zone_cache (
    id SERIAL PRIMARY KEY,
    latitude DECIMAL(10, 6) NOT NULL,
    longitude DECIMAL(11, 6) NOT NULL,
    climate_zone VARCHAR(10) NOT NULL,
    koppen_classification VARCHAR(10),
    confidence_score DECIMAL(4, 3) NOT NULL,
    characteristics JSONB,
    agricultural_info JSONB,
    detection_method VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    
    -- Indexes for efficient lookups
    INDEX idx_coordinates (latitude, longitude),
    INDEX idx_zone (climate_zone),
    INDEX idx_expires (expires_at)
);

-- Zone characteristics reference table
CREATE TABLE climate_zone_characteristics (
    zone VARCHAR(10) PRIMARY KEY,
    zone_type VARCHAR(20) NOT NULL, -- 'usda', 'koppen', 'agricultural'
    min_temp_winter DECIMAL(5, 2),
    max_temp_summer DECIMAL(5, 2),
    annual_precipitation DECIMAL(6, 2),
    growing_season_days INTEGER,
    frost_free_days INTEGER,
    suitable_crops TEXT[], -- PostgreSQL array
    agricultural_notes TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🧪 Testing Framework

### Unit Tests

```python
class TestClimateZoneService:
    """Unit tests for climate zone service"""
    
    @pytest.fixture
    def climate_service(self):
        return ClimateZoneService(
            weather_service=MagicMock(),
            cache_service=MagicMock()
        )
    
    @pytest.mark.asyncio
    async def test_detect_zone_iowa_corn_belt(self, climate_service):
        """Test detection for Iowa corn belt location"""
        result = await climate_service.detect_zone(42.0308, -93.6319)
        
        assert result.climate_zone == "5b"
        assert result.confidence_score >= 0.8
        assert "corn" in result.agricultural_info.suitable_crops
    
    @pytest.mark.asyncio
    async def test_elevation_adjustment(self, climate_service):
        """Test elevation-based zone adjustment"""
        # Low elevation result
        low_result = await climate_service.detect_zone(39.7392, -104.9847)  # Denver area
        
        # High elevation result (should be cooler zone)
        high_result = await climate_service.detect_zone(39.7392, -105.8178)  # Mountains
        
        assert int(high_result.climate_zone[0]) < int(low_result.climate_zone[0])
```

### Integration Tests

```python
class TestClimateZoneIntegration:
    """Integration tests for complete workflow"""
    
    @pytest.mark.asyncio
    async def test_complete_detection_workflow(self):
        """Test complete detection workflow from API to database"""
        
        # API request
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/climate-zone/detect", json={
                "latitude": 42.0308,
                "longitude": -93.6319,
                "include_characteristics": True,
                "include_agricultural_info": True
            })
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "climate_zone" in data
        assert "confidence_score" in data
        assert data["confidence_score"] >= 0.7
        
        # Validate cache was populated
        cache_key = "climate_zone:42.031:-93.632"
        cached_result = await redis_client.get(cache_key)
        assert cached_result is not None
```

### Performance Tests

```python
class TestClimateZonePerformance:
    """Performance tests for climate zone detection"""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_detection_response_time(self):
        """Test detection completes within 2 seconds"""
        
        start_time = time.time()
        result = await climate_service.detect_zone(42.0308, -93.6319)
        end_time = time.time()
        
        assert (end_time - start_time) < 2.0
        assert result.confidence_score >= 0.7
    
    @pytest.mark.performance
    def test_concurrent_requests(self):
        """Test handling of 50 concurrent requests"""
        
        def make_request(coords):
            return climate_service.detect_zone(coords[0], coords[1])
        
        coordinates = [(40.0 + i, -95.0 + i) for i in range(50)]
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(make_request, coordinates))
        
        # All requests should succeed
        assert len(results) == 50
        assert all(r.confidence_score >= 0.7 for r in results)
```

## 🔒 Security Considerations

### Input Validation

```python
from pydantic import BaseModel, validator

class ClimateZoneRequest(BaseModel):
    latitude: float
    longitude: float
    include_characteristics: bool = False
    include_agricultural_info: bool = False
    
    @validator('latitude')
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError('Latitude must be between -90 and 90')
        return v
    
    @validator('longitude')
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError('Longitude must be between -180 and 180')
        return v
```

### Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/detect")
@limiter.limit("100/hour")  # 100 requests per hour per IP
async def detect_climate_zone(
    request: Request,
    climate_request: ClimateZoneRequest
) -> ClimateZoneResponse:
    """Rate-limited climate zone detection"""
    return await climate_service.detect_zone(
        climate_request.latitude, 
        climate_request.longitude
    )
```

## 📚 Error Handling

### Exception Hierarchy

```python
class ClimateZoneError(Exception):
    """Base exception for climate zone operations"""
    pass

class InvalidCoordinatesError(ClimateZoneError):
    """Raised when coordinates are invalid"""
    pass

class ExternalServiceError(ClimateZoneError):  
    """Raised when external services fail"""
    pass

class CacheError(ClimateZoneError):
    """Raised when cache operations fail"""
    pass

class LowConfidenceError(ClimateZoneError):
    """Raised when detection confidence is too low"""
    pass
```

### Error Response Format

```python
class ErrorResponse(BaseModel):
    error_code: str
    error_message: str
    details: Optional[Dict[str, Any]]
    timestamp: datetime
    request_id: str

@app.exception_handler(ClimateZoneError)
async def climate_zone_error_handler(request: Request, exc: ClimateZoneError):
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            error_code=exc.__class__.__name__,
            error_message=str(exc),
            timestamp=datetime.utcnow(),
            request_id=str(uuid.uuid4())
        ).dict()
    )
```

## 🔧 Configuration

### Environment Variables

```bash
# External API Keys
USDA_API_KEY=your_usda_api_key_here
WEATHER_API_KEY=your_weather_api_key_here

# Cache Configuration
REDIS_URL=redis://localhost:6379/0
CACHE_DEFAULT_TTL=86400  # 24 hours

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/climate_zones

# Service Configuration
CLIMATE_ZONE_SERVICE_PORT=8000
LOG_LEVEL=INFO
MAX_CONCURRENT_REQUESTS=100

# Detection Thresholds
MIN_CONFIDENCE_THRESHOLD=0.7
ENABLE_ELEVATION_ADJUSTMENT=true
ENABLE_MICROCLIMATE_ANALYSIS=true
```

### Configuration Classes

```python
from pydantic import BaseSettings

class ClimateZoneSettings(BaseSettings):
    """Configuration settings for climate zone service"""
    
    # API Keys
    usda_api_key: Optional[str] = None
    weather_api_key: Optional[str] = None
    
    # Cache Settings
    redis_url: str = "redis://localhost:6379/0"
    cache_default_ttl: int = 86400
    
    # Detection Settings
    min_confidence_threshold: float = 0.7
    enable_elevation_adjustment: bool = True
    enable_microclimate_analysis: bool = True
    
    # Performance Settings
    max_concurrent_requests: int = 100
    request_timeout_seconds: int = 30
    
    class Config:
        env_file = ".env"
        env_prefix = "CLIMATE_ZONE_"

settings = ClimateZoneSettings()
```

## 🚀 Deployment

### Docker Configuration

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY start_service.py .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["python", "start_service.py"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: climate-zone-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: climate-zone-service
  template:
    metadata:
      labels:
        app: climate-zone-service
    spec:
      containers:
      - name: climate-zone-service
        image: caain/climate-zone-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_URL
          value: "redis://redis-service:6379/0"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: climate-zone-secrets
              key: database-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi" 
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

## 📈 Monitoring & Observability

### Metrics Collection

```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Metrics
DETECTION_REQUESTS = Counter('climate_zone_detections_total', 'Total climate zone detections', ['method', 'result'])
DETECTION_DURATION = Histogram('climate_zone_detection_duration_seconds', 'Detection duration')
CACHE_HIT_RATE = Gauge('climate_zone_cache_hit_rate', 'Cache hit rate')
CONFIDENCE_SCORES = Histogram('climate_zone_confidence_scores', 'Distribution of confidence scores')

class MetricsMiddleware:
    async def __call__(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        # Record metrics
        duration = time.time() - start_time
        DETECTION_DURATION.observe(duration)
        
        if request.url.path.startswith('/api/climate-zone/'):
            DETECTION_REQUESTS.labels(
                method=request.method,
                result='success' if response.status_code < 400 else 'error'
            ).inc()
        
        return response
```

### Logging Configuration

```python
import logging
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Usage in service
async def detect_zone(self, latitude: float, longitude: float) -> ClimateZoneResult:
    logger.info(
        "Starting climate zone detection",
        latitude=latitude,
        longitude=longitude,
        request_id=self.request_id
    )
    
    try:
        result = await self._detect_zone_internal(latitude, longitude)
        
        logger.info(
            "Climate zone detection completed",
            latitude=latitude,
            longitude=longitude,
            climate_zone=result.climate_zone,
            confidence=result.confidence_score,
            request_id=self.request_id
        )
        
        return result
    
    except Exception as e:
        logger.error(
            "Climate zone detection failed",
            latitude=latitude,
            longitude=longitude,
            error=str(e),
            error_type=type(e).__name__,
            request_id=self.request_id
        )
        raise
```

This developer documentation provides comprehensive guidance for working with the Climate Zone Detection system, covering architecture, implementation details, API usage, testing, security, and deployment considerations.
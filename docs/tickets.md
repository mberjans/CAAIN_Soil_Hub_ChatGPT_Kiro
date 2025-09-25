# CAAIN Soil Hub - Software Development Tickets

This document contains comprehensive software development tickets for AI coding agents to implement the Autonomous Farm Advisory System. Each ticket corresponds to tasks from the master checklist and includes detailed technical specifications with complete implementation guidance for AI agent independence.

## AI Agent Implementation Notes

**Enhanced for AI Independence**: All tickets now include:
- ✅ **Step-by-Step Implementation Guides**: Complete code examples and directory structures
- ✅ **Comprehensive Testing Requirements**: Unit, integration, and agricultural validation tests
- ✅ **Integration Instructions**: Service connections and deployment procedures
- ✅ **Agricultural Domain Context**: Safety checks, validation rules, and expert review criteria
- ✅ **Performance Requirements**: Response time, accuracy, and reliability specifications

**Reference Implementation**: Use `services/ai-agent/` as the pattern for service architecture, API design, and testing frameworks.

## Ticket Template Structure

Each ticket includes:
- **Ticket ID**: Unique identifier matching task IDs
- **Title**: Descriptive task name
- **Epic**: High-level feature grouping
- **Priority**: Critical/High/Medium/Low
- **Story Points**: Complexity estimate (1-21)
- **Dependencies**: Required components/tickets
- **Technical Stack**: Technologies to use
- **Acceptance Criteria**: Specific requirements
- **Implementation Details**: Technical specifications
- **API Specifications**: Endpoint definitions
- **Database Schema**: Data model requirements
- **Testing Requirements**: Test coverage expectations

---

## Epic 1: Climate Zone Detection

### TICKET-001: Climate Zone Data Service Implementation
**ID**: climate-zone-detection-1.1  
**Title**: Create climate zone data service in data-integration  
**Epic**: Climate Zone Detection  
**Priority**: Critical  
**Story Points**: 8  
**Dependencies**: Data integration framework  

**Technical Stack**:
- Python 3.11+
- FastAPI framework
- PostgreSQL for structured data
- Redis for caching
- aiohttp for external API calls

**Acceptance Criteria**:
- [ ] Service integrates with USDA Plant Hardiness Zone API
- [ ] Service supports Köppen climate classification
- [ ] Climate zone data is cached for 24 hours
- [ ] Service handles API failures gracefully with fallback data
- [ ] Response time < 2 seconds for zone lookup

**Step-by-Step Implementation Guide**:

**1. Create Service Directory Structure**:
```bash
# Execute these commands to create the service structure
mkdir -p services/data-integration/climate_zones/{providers,tests}
touch services/data-integration/climate_zones/__init__.py
touch services/data-integration/climate_zones/{models.py,service.py,cache.py,exceptions.py}
touch services/data-integration/climate_zones/providers/{__init__.py,usda_provider.py,koppen_provider.py}
touch services/data-integration/climate_zones/tests/{__init__.py,test_service.py,test_providers.py}
```

**2. Implement Data Models** (`models.py`):
```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ClimateZoneType(str, Enum):
    """Types of climate zone classifications."""
    USDA_HARDINESS = "usda_hardiness"
    KOPPEN = "koppen"
    AGRICULTURAL = "agricultural"

class ClimateZoneData(BaseModel):
    """Climate zone data model with validation."""

    zone_id: str = Field(..., description="Unique zone identifier")
    zone_name: str = Field(..., description="Human-readable zone name")
    zone_type: ClimateZoneType = Field(..., description="Type of climate classification")
    hardiness_zone: Optional[str] = Field(None, description="USDA hardiness zone (e.g., '5a', '6b')")
    koppen_class: Optional[str] = Field(None, description="Köppen climate classification")
    min_temp_celsius: float = Field(..., description="Average minimum temperature")
    max_temp_celsius: float = Field(..., description="Average maximum temperature")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence score")
    source: str = Field(..., description="Data source (USDA, Köppen, etc.)")
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    @validator('hardiness_zone')
    def validate_hardiness_zone(cls, v):
        if v and not v.match(r'^[1-9][0-9]?[ab]?$'):
            raise ValueError('Invalid USDA hardiness zone format')
        return v

class CoordinateRequest(BaseModel):
    """Request model for coordinate-based zone lookup."""

    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")
    include_koppen: bool = Field(default=True, description="Include Köppen classification")

class ClimateZoneResponse(BaseModel):
    """Response model for climate zone queries."""

    request_id: str = Field(..., description="Unique request identifier")
    zones: List[ClimateZoneData] = Field(..., description="Detected climate zones")
    primary_zone: ClimateZoneData = Field(..., description="Primary/most confident zone")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
```

**3. Implement Core Service** (`service.py`):
```python
import asyncio
import logging
import time
from typing import Optional, List, Dict, Any
from uuid import uuid4

from .models import ClimateZoneData, CoordinateRequest, ClimateZoneResponse, ClimateZoneType
from .providers.usda_provider import USDAProvider
from .providers.koppen_provider import KoppenProvider
from .cache import ClimateZoneCache
from .exceptions import ClimateZoneError, ProviderError

logger = logging.getLogger(__name__)

class ClimateZoneService:
    """Core climate zone detection service."""

    def __init__(self):
        self.usda_provider = USDAProvider()
        self.koppen_provider = KoppenProvider()
        self.cache = ClimateZoneCache()

    async def get_zone_by_coordinates(
        self,
        latitude: float,
        longitude: float,
        include_koppen: bool = True
    ) -> ClimateZoneResponse:
        """
        Get climate zone data for given coordinates.

        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            include_koppen: Whether to include Köppen classification

        Returns:
            ClimateZoneResponse with detected zones

        Raises:
            ClimateZoneError: If zone detection fails
        """
        start_time = time.time()
        request_id = str(uuid4())

        try:
            # Check cache first
            cache_key = f"coords:{latitude}:{longitude}:{include_koppen}"
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                logger.info(f"Cache hit for coordinates {latitude}, {longitude}")
                return cached_result

            # Fetch from providers concurrently
            tasks = [self.usda_provider.get_zone(latitude, longitude)]
            if include_koppen:
                tasks.append(self.koppen_provider.get_zone(latitude, longitude))

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            zones = []
            for result in results:
                if isinstance(result, Exception):
                    logger.warning(f"Provider error: {result}")
                    continue
                if result:
                    zones.append(result)

            if not zones:
                raise ClimateZoneError("No climate zone data available for coordinates")

            # Select primary zone (highest confidence)
            primary_zone = max(zones, key=lambda z: z.confidence)

            response = ClimateZoneResponse(
                request_id=request_id,
                zones=zones,
                primary_zone=primary_zone,
                metadata={
                    "coordinates": {"lat": latitude, "lng": longitude},
                    "providers_used": [z.source for z in zones],
                    "cache_miss": True
                },
                processing_time_ms=(time.time() - start_time) * 1000
            )

            # Cache the result
            await self.cache.set(cache_key, response, ttl_seconds=86400)  # 24 hours

            return response

        except Exception as e:
            logger.error(f"Error getting climate zone: {e}")
            raise ClimateZoneError(f"Failed to get climate zone: {str(e)}")

    async def batch_lookup(
        self,
        coordinates: List[Dict[str, float]]
    ) -> List[ClimateZoneResponse]:
        """Batch lookup for multiple coordinates."""
        tasks = [
            self.get_zone_by_coordinates(coord["lat"], coord["lng"])
            for coord in coordinates
        ]
        return await asyncio.gather(*tasks, return_exceptions=True)
```

**4. Implement Caching Layer** (`cache.py`):
```python
import json
import logging
from typing import Optional, Any
import redis.asyncio as redis
from .models import ClimateZoneResponse

logger = logging.getLogger(__name__)

class ClimateZoneCache:
    """Redis-based caching for climate zone data."""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self._redis = None

    async def get_redis(self):
        """Get Redis connection."""
        if not self._redis:
            self._redis = redis.from_url(self.redis_url)
        return self._redis

    async def get(self, key: str) -> Optional[ClimateZoneResponse]:
        """Get cached climate zone data."""
        try:
            redis_client = await self.get_redis()
            cached_data = await redis_client.get(f"climate_zone:{key}")
            if cached_data:
                data = json.loads(cached_data)
                return ClimateZoneResponse(**data)
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
        return None

    async def set(self, key: str, data: ClimateZoneResponse, ttl_seconds: int = 86400):
        """Cache climate zone data."""
        try:
            redis_client = await self.get_redis()
            await redis_client.setex(
                f"climate_zone:{key}",
                ttl_seconds,
                data.json()
            )
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
```

**5. Implement API Endpoints** (`api/routes.py`):
```python
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any
import logging

from ..models import CoordinateRequest, ClimateZoneResponse
from ..service import ClimateZoneService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/climate-zones", tags=["climate-zones"])

# Dependency injection
async def get_climate_service() -> ClimateZoneService:
    return ClimateZoneService()

@router.get("/by-coordinates", response_model=ClimateZoneResponse)
async def get_zone_by_coordinates(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude in decimal degrees"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude in decimal degrees"),
    include_koppen: bool = Query(True, description="Include Köppen classification"),
    service: ClimateZoneService = Depends(get_climate_service)
):
    """
    Get climate zone data for specific coordinates.

    This endpoint provides USDA hardiness zones and Köppen climate classifications
    for agricultural planning and crop selection decisions.

    Agricultural Use Cases:
    - Crop variety selection based on hardiness zones
    - Planting date calculations using climate data
    - Risk assessment for temperature-sensitive crops
    """
    try:
        result = await service.get_zone_by_coordinates(latitude, longitude, include_koppen)
        return result
    except Exception as e:
        logger.error(f"Error getting climate zone: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch-lookup", response_model=List[ClimateZoneResponse])
async def batch_climate_lookup(
    coordinates: List[Dict[str, float]],
    service: ClimateZoneService = Depends(get_climate_service)
):
    """
    Batch lookup for multiple coordinate pairs.

    Efficient endpoint for processing multiple locations simultaneously,
    useful for farm management systems with multiple fields.

    Request format:
    [
        {"lat": 41.8781, "lng": -87.6298},
        {"lat": 40.7128, "lng": -74.0060}
    ]
    """
    try:
        if len(coordinates) > 100:
            raise HTTPException(status_code=400, detail="Maximum 100 coordinates per request")

        results = await service.batch_lookup(coordinates)
        return results
    except Exception as e:
        logger.error(f"Error in batch lookup: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint for service monitoring."""
    return {"status": "healthy", "service": "climate-zones"}
```

**6. Implement External Providers** (`providers/usda_provider.py`):
```python
import aiohttp
import logging
from typing import Optional
from ..models import ClimateZoneData, ClimateZoneType
from ..exceptions import ProviderError

logger = logging.getLogger(__name__)

class USDAProvider:
    """USDA Plant Hardiness Zone API provider."""

    def __init__(self):
        self.base_url = "https://phzmapi.org"
        self.session = None

    async def get_session(self):
        """Get aiohttp session."""
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session

    async def get_zone(self, latitude: float, longitude: float) -> Optional[ClimateZoneData]:
        """Get USDA hardiness zone for coordinates."""
        try:
            session = await self.get_session()
            url = f"{self.base_url}/{latitude}/{longitude}.json"

            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()

                    return ClimateZoneData(
                        zone_id=f"usda_{data['zone']}",
                        zone_name=f"USDA Zone {data['zone']}",
                        zone_type=ClimateZoneType.USDA_HARDINESS,
                        hardiness_zone=data['zone'],
                        min_temp_celsius=data.get('temperature_range', {}).get('min', -999),
                        max_temp_celsius=data.get('temperature_range', {}).get('max', 999),
                        confidence=0.9,  # USDA data is highly reliable
                        source="USDA Plant Hardiness Zone API"
                    )
                else:
                    logger.warning(f"USDA API returned status {response.status}")
                    return None

        except Exception as e:
            logger.error(f"USDA provider error: {e}")
            raise ProviderError(f"USDA API error: {str(e)}")

    async def close(self):
        """Close aiohttp session."""
        if self.session:
            await self.session.close()
```

**7. Database Schema and Migrations**:
```sql
-- Create climate zones reference table
CREATE TABLE climate_zones_reference (
    id SERIAL PRIMARY KEY,
    zone_id VARCHAR(20) UNIQUE NOT NULL,
    zone_name VARCHAR(100) NOT NULL,
    zone_type VARCHAR(20) NOT NULL,
    hardiness_zone VARCHAR(10),
    koppen_class VARCHAR(10),
    min_temp_celsius DECIMAL(5,2),
    max_temp_celsius DECIMAL(5,2),
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create climate zone cache table for performance
CREATE TABLE climate_zone_cache (
    id SERIAL PRIMARY KEY,
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    latitude DECIMAL(10,8) NOT NULL,
    longitude DECIMAL(11,8) NOT NULL,
    zone_data JSONB NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_climate_zones_zone_id ON climate_zones_reference(zone_id);
CREATE INDEX idx_climate_zones_type ON climate_zones_reference(zone_type);
CREATE INDEX idx_cache_coordinates ON climate_zone_cache(latitude, longitude);
CREATE INDEX idx_cache_expires ON climate_zone_cache(expires_at);
```

**8. Comprehensive Testing Implementation** (`tests/test_service.py`):
```python
import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from ..service import ClimateZoneService
from ..models import ClimateZoneData, ClimateZoneType
from ..exceptions import ClimateZoneError

class TestClimateZoneService:
    """Comprehensive test suite for climate zone service."""

    @pytest.fixture
    def service(self):
        return ClimateZoneService()

    @pytest.fixture
    def mock_usda_data(self):
        return ClimateZoneData(
            zone_id="usda_6a",
            zone_name="USDA Zone 6a",
            zone_type=ClimateZoneType.USDA_HARDINESS,
            hardiness_zone="6a",
            min_temp_celsius=-23.3,
            max_temp_celsius=-20.6,
            confidence=0.9,
            source="USDA Plant Hardiness Zone API"
        )

    @pytest.mark.asyncio
    async def test_get_zone_by_coordinates_success(self, service, mock_usda_data):
        """Test successful zone detection."""
        with patch.object(service.usda_provider, 'get_zone', return_value=mock_usda_data):
            with patch.object(service.cache, 'get', return_value=None):
                with patch.object(service.cache, 'set', return_value=None):
                    result = await service.get_zone_by_coordinates(41.8781, -87.6298)

                    assert result.primary_zone.zone_id == "usda_6a"
                    assert result.primary_zone.hardiness_zone == "6a"
                    assert len(result.zones) >= 1
                    assert result.processing_time_ms > 0

    @pytest.mark.asyncio
    async def test_cache_hit(self, service, mock_usda_data):
        """Test cache hit scenario."""
        cached_response = ClimateZoneResponse(
            request_id="test",
            zones=[mock_usda_data],
            primary_zone=mock_usda_data,
            metadata={"cache_hit": True},
            processing_time_ms=1.0
        )

        with patch.object(service.cache, 'get', return_value=cached_response):
            result = await service.get_zone_by_coordinates(41.8781, -87.6298)
            assert result.metadata.get("cache_hit") is True

    @pytest.mark.asyncio
    async def test_provider_failure_handling(self, service):
        """Test handling of provider failures."""
        with patch.object(service.usda_provider, 'get_zone', side_effect=Exception("API Error")):
            with patch.object(service.koppen_provider, 'get_zone', side_effect=Exception("API Error")):
                with pytest.raises(ClimateZoneError):
                    await service.get_zone_by_coordinates(41.8781, -87.6298)

    @pytest.mark.asyncio
    async def test_batch_lookup(self, service, mock_usda_data):
        """Test batch coordinate lookup."""
        coordinates = [
            {"lat": 41.8781, "lng": -87.6298},
            {"lat": 40.7128, "lng": -74.0060}
        ]

        with patch.object(service, 'get_zone_by_coordinates', return_value=mock_usda_data):
            results = await service.batch_lookup(coordinates)
            assert len(results) == 2

    @pytest.mark.performance
    async def test_response_time_requirement(self, service):
        """Test that response time is under 2 seconds."""
        import time
        start_time = time.time()

        # Mock fast response
        with patch.object(service.usda_provider, 'get_zone', return_value=mock_usda_data):
            await service.get_zone_by_coordinates(41.8781, -87.6298)

        elapsed = time.time() - start_time
        assert elapsed < 2.0, f"Response time {elapsed}s exceeds 2s requirement"

# Agricultural validation tests
class TestAgriculturalValidation:
    """Tests for agricultural accuracy and domain validation."""

    @pytest.mark.asyncio
    async def test_corn_belt_zone_accuracy(self, service):
        """Test accuracy for major corn belt coordinates."""
        # Iowa coordinates - should be zone 5a-6a
        result = await service.get_zone_by_coordinates(41.5868, -93.6250)
        assert result.primary_zone.hardiness_zone in ["5a", "5b", "6a", "6b"]

    @pytest.mark.asyncio
    async def test_temperature_range_validation(self, service):
        """Test that temperature ranges are agriculturally valid."""
        result = await service.get_zone_by_coordinates(41.8781, -87.6298)
        zone = result.primary_zone

        # Validate temperature ranges make agricultural sense
        assert zone.min_temp_celsius < zone.max_temp_celsius
        assert -50 <= zone.min_temp_celsius <= 20  # Reasonable range for agriculture
        assert -30 <= zone.max_temp_celsius <= 50
```

**9. Integration Instructions**:
```bash
# 1. Install dependencies
pip install fastapi aiohttp redis pydantic

# 2. Set up environment variables
export REDIS_URL="redis://localhost:6379"
export USDA_API_BASE_URL="https://phzmapi.org"

# 3. Run database migrations
python -m alembic upgrade head

# 4. Start the service
uvicorn main:app --host 0.0.0.0 --port 8001

# 5. Test the endpoints
curl "http://localhost:8001/api/v1/climate-zones/by-coordinates?latitude=41.8781&longitude=-87.6298"

# 6. Run tests
pytest tests/ -v --cov=. --cov-report=html
```

**10. Service Registration and Integration**:
```python
# Add to main FastAPI application
from services.data_integration.climate_zones.api.routes import router as climate_router

app = FastAPI(title="AFAS Data Integration Service")
app.include_router(climate_router)

# Add to service discovery
SERVICES = {
    "climate-zones": {
        "url": "http://localhost:8001",
        "health_endpoint": "/api/v1/climate-zones/health"
    }
}
```

**Validation Criteria**:
- ✅ Service responds to coordinate queries in <2 seconds
- ✅ >90% test coverage achieved
- ✅ Cache hit rate >60% in production
- ✅ Handles API failures gracefully with fallback mechanisms
- ✅ Agricultural validation tests pass for major farming regions
- ✅ Integration tests with external APIs successful
- Performance tests for batch operations
- Cache invalidation tests

---

### TICKET-002: Coordinate-Based Climate Zone Detection
**ID**: climate-zone-detection-2.1  
**Title**: Implement coordinate-based climate zone detection  
**Epic**: Climate Zone Detection  
**Priority**: Critical  
**Story Points**: 5  
**Dependencies**: TICKET-001  

**Technical Stack**:
- Python 3.11+
- FastAPI
- Geospatial libraries (Shapely, GeoPandas)
- PostGIS extension for PostgreSQL

**Acceptance Criteria**:
- [ ] Accepts GPS coordinates (latitude, longitude)
- [ ] Returns climate zone with confidence score
- [ ] Handles edge cases (ocean coordinates, polar regions)
- [ ] Validates coordinate ranges (-90 to 90 lat, -180 to 180 lng)
- [ ] Caches results by coordinate grid (0.1 degree precision)

**Step-by-Step Implementation Guide**:

**1. Enhance Climate Zone Service with Advanced Detection** (`service.py` additions):
```python
import math
from shapely.geometry import Point
from shapely.ops import transform
import pyproj
from typing import Tuple, Optional

class ClimateZoneDetector:
    """Advanced coordinate-based climate zone detection."""

    def __init__(self, service: ClimateZoneService):
        self.service = service
        self.grid_precision = 0.1  # degrees for caching

    async def detect_by_coordinates(
        self,
        latitude: float,
        longitude: float,
        include_details: bool = False
    ) -> Dict[str, Any]:
        """
        Advanced coordinate-based detection with confidence scoring.

        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            include_details: Include detailed analysis

        Returns:
            Detection result with confidence scoring
        """
        # 1. Validate coordinates
        self._validate_coordinates(latitude, longitude)

        # 2. Check for edge cases
        edge_case_result = self._handle_edge_cases(latitude, longitude)
        if edge_case_result:
            return edge_case_result

        # 3. Check grid-based cache
        grid_key = self._get_grid_key(latitude, longitude)
        cached_result = await self.service.cache.get(f"grid:{grid_key}")
        if cached_result:
            return self._adjust_for_precise_coordinates(cached_result, latitude, longitude)

        # 4. Perform multi-source detection
        detection_result = await self._multi_source_detection(latitude, longitude)

        # 5. Calculate confidence score
        confidence = self._calculate_confidence(detection_result, latitude, longitude)

        # 6. Prepare response
        result = {
            "zone_id": detection_result["primary_zone"].zone_id,
            "confidence": confidence,
            "hardiness_zone": detection_result["primary_zone"].hardiness_zone,
            "koppen_class": detection_result["primary_zone"].koppen_class,
            "coordinates": {"latitude": latitude, "longitude": longitude},
            "grid_key": grid_key
        }

        if include_details:
            result["details"] = {
                "all_zones": detection_result["all_zones"],
                "data_sources": detection_result["sources"],
                "edge_case_flags": detection_result.get("edge_cases", []),
                "nearby_references": await self._get_nearby_references(latitude, longitude)
            }

        # 7. Cache at grid level
        await self.service.cache.set(f"grid:{grid_key}", result, ttl_seconds=86400)

        return result

    def _validate_coordinates(self, latitude: float, longitude: float):
        """Validate coordinate ranges and format."""
        if not (-90 <= latitude <= 90):
            raise ValueError(f"Invalid latitude: {latitude}. Must be between -90 and 90")
        if not (-180 <= longitude <= 180):
            raise ValueError(f"Invalid longitude: {longitude}. Must be between -180 and 180")

        # Check for common coordinate errors
        if abs(latitude) < 0.001 and abs(longitude) < 0.001:
            raise ValueError("Coordinates appear to be null island (0,0)")

    def _handle_edge_cases(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """Handle special coordinate cases."""
        edge_cases = []

        # Ocean coordinates
        if self._is_ocean_coordinate(latitude, longitude):
            edge_cases.append("ocean_coordinate")
            return {
                "zone_id": "ocean",
                "confidence": 0.1,
                "hardiness_zone": None,
                "koppen_class": "Ocean",
                "edge_cases": edge_cases,
                "message": "Coordinates appear to be over ocean - limited agricultural relevance"
            }

        # Polar regions
        if abs(latitude) > 66.5:  # Arctic/Antarctic circles
            edge_cases.append("polar_region")
            return {
                "zone_id": "polar",
                "confidence": 0.3,
                "hardiness_zone": "1" if latitude > 0 else None,
                "koppen_class": "ET" if latitude > 0 else "EF",
                "edge_cases": edge_cases,
                "message": "Polar region - limited agricultural potential"
            }

        return None

    def _get_grid_key(self, latitude: float, longitude: float) -> str:
        """Generate grid key for caching."""
        grid_lat = round(latitude / self.grid_precision) * self.grid_precision
        grid_lng = round(longitude / self.grid_precision) * self.grid_precision
        return f"{grid_lat:.1f},{grid_lng:.1f}"

    async def _multi_source_detection(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Perform detection using multiple data sources."""
        sources_used = []
        all_zones = []

        try:
            # USDA Hardiness Zone
            usda_zone = await self.service.usda_provider.get_zone(latitude, longitude)
            if usda_zone:
                all_zones.append(usda_zone)
                sources_used.append("USDA")
        except Exception as e:
            logger.warning(f"USDA provider failed: {e}")

        try:
            # Köppen Classification
            koppen_zone = await self.service.koppen_provider.get_zone(latitude, longitude)
            if koppen_zone:
                all_zones.append(koppen_zone)
                sources_used.append("Köppen")
        except Exception as e:
            logger.warning(f"Köppen provider failed: {e}")

        # Select primary zone (highest confidence)
        primary_zone = max(all_zones, key=lambda z: z.confidence) if all_zones else None

        return {
            "primary_zone": primary_zone,
            "all_zones": all_zones,
            "sources": sources_used
        }

    def _calculate_confidence(self, detection_result: Dict[str, Any], latitude: float, longitude: float) -> float:
        """Calculate confidence score based on multiple factors."""
        base_confidence = 0.5

        # Factor 1: Number of data sources
        num_sources = len(detection_result["sources"])
        source_bonus = min(num_sources * 0.2, 0.4)

        # Factor 2: Data source reliability
        reliability_bonus = 0.0
        if "USDA" in detection_result["sources"]:
            reliability_bonus += 0.3
        if "Köppen" in detection_result["sources"]:
            reliability_bonus += 0.2

        # Factor 3: Geographic factors
        geo_penalty = 0.0
        if abs(latitude) > 60:  # High latitudes less reliable
            geo_penalty = 0.1
        if self._is_border_region(latitude, longitude):
            geo_penalty += 0.1

        final_confidence = min(base_confidence + source_bonus + reliability_bonus - geo_penalty, 1.0)
        return max(final_confidence, 0.1)  # Minimum confidence

    def _is_ocean_coordinate(self, latitude: float, longitude: float) -> bool:
        """Check if coordinates are over ocean (simplified)."""
        # Simplified ocean detection - in production, use coastline data
        major_land_masses = [
            # North America
            (25, 70, -170, -50),
            # Europe/Asia
            (35, 80, -10, 180),
            # Africa
            (-35, 40, -20, 55),
            # South America
            (-60, 15, -85, -30),
            # Australia
            (-45, -10, 110, 160)
        ]

        for min_lat, max_lat, min_lng, max_lng in major_land_masses:
            if min_lat <= latitude <= max_lat and min_lng <= longitude <= max_lng:
                return False
        return True

    def _is_border_region(self, latitude: float, longitude: float) -> bool:
        """Check if coordinates are near climate zone borders."""
        # Simplified border detection
        # In production, use actual zone boundary data
        return False

    async def _get_nearby_references(self, latitude: float, longitude: float) -> List[Dict[str, Any]]:
        """Get nearby reference points for validation."""
        # Find nearby weather stations, agricultural research stations, etc.
        return []
```

**2. Enhanced API Endpoint** (`api/routes.py` additions):
```python
@router.post("/detect", response_model=Dict[str, Any])
async def detect_climate_zone(
    request: CoordinateRequest,
    include_details: bool = Query(False, description="Include detailed analysis"),
    service: ClimateZoneService = Depends(get_climate_service)
):
    """
    Advanced coordinate-based climate zone detection.

    This endpoint provides enhanced detection with confidence scoring,
    edge case handling, and detailed analysis for agricultural planning.

    Features:
    - Multi-source data validation
    - Confidence scoring based on data quality
    - Edge case handling (ocean, polar regions)
    - Grid-based caching for performance
    - Detailed analysis including nearby references
    """
    try:
        detector = ClimateZoneDetector(service)
        result = await detector.detect_by_coordinates(
            request.latitude,
            request.longitude,
            include_details
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Detection error: {e}")
        raise HTTPException(status_code=500, detail="Climate zone detection failed")
```

---

## Epic 2: Soil pH Management

### TICKET-003: pH Management Service Structure
**ID**: soil-ph-management-1.1  
**Title**: Set up soil pH management service structure  
**Epic**: Soil pH Management  
**Priority**: Critical  
**Story Points**: 5  
**Dependencies**: Core service framework  

**Technical Stack**:
- Python 3.11+
- FastAPI framework
- SQLAlchemy ORM
- PostgreSQL
- Pydantic for data validation

**Acceptance Criteria**:
- [ ] Service follows microservice architecture pattern
- [ ] Implements proper error handling and logging
- [ ] Includes health check endpoints
- [ ] Supports async operations
- [ ] Follows project coding standards

**Implementation Details**:
```python
# Service structure: services/soil-ph-management/
├── __init__.py
├── main.py           # FastAPI application
├── models/           # Database models
│   ├── __init__.py
│   ├── ph_data.py
│   └── recommendations.py
├── services/         # Business logic
│   ├── __init__.py
│   ├── ph_calculator.py
│   └── amendment_service.py
├── api/             # API endpoints
│   ├── __init__.py
│   └── ph_endpoints.py
├── schemas/         # Pydantic schemas
│   ├── __init__.py
│   └── ph_schemas.py
└── tests/           # Test files
    ├── __init__.py
    ├── test_ph_calculator.py
    └── test_api.py
```

**Database Schema**:
```sql
CREATE TABLE soil_ph_data (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    field_id UUID NOT NULL,
    ph_value DECIMAL(3,1) NOT NULL CHECK (ph_value >= 0 AND ph_value <= 14),
    test_date DATE NOT NULL,
    test_method VARCHAR(50),
    soil_type VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE ph_recommendations (
    id SERIAL PRIMARY KEY,
    ph_data_id INTEGER REFERENCES soil_ph_data(id),
    target_crop VARCHAR(100),
    current_ph DECIMAL(3,1),
    target_ph DECIMAL(3,1),
    amendment_type VARCHAR(50),
    amendment_amount DECIMAL(8,2),
    amendment_unit VARCHAR(20),
    application_timing VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

### TICKET-004: pH Adjustment Calculation Engine
**ID**: soil-ph-management-4.1  
**Title**: Build pH adjustment calculation engine  
**Epic**: Soil pH Management  
**Priority**: Critical  
**Story Points**: 13  
**Dependencies**: TICKET-003, Soil type integration  

**Technical Stack**:
- Python 3.11+
- NumPy for calculations
- Agricultural chemistry formulas
- Soil buffer capacity models

**Acceptance Criteria**:
- [ ] Calculates lime requirements for pH increase
- [ ] Calculates sulfur requirements for pH decrease
- [ ] Considers soil type and buffer capacity
- [ ] Accounts for organic matter content
- [ ] Provides application rate recommendations
- [ ] Includes timing recommendations
- [ ] Validates input parameters

**Implementation Details**:
```python
class PHAdjustmentCalculator:
    def calculate_lime_requirement(
        self, 
        current_ph: float,
        target_ph: float,
        soil_type: str,
        organic_matter_percent: float,
        field_size_acres: float
    ) -> LimeRecommendation:
        """
        Calculate lime requirement using buffer pH method
        Formula: Lime (tons/acre) = (Target pH - Current pH) × Buffer Capacity × Adjustment Factor
        """
        
    def calculate_sulfur_requirement(
        self,
        current_ph: float,
        target_ph: float,
        soil_type: str,
        cec: float,
        field_size_acres: float
    ) -> SulfurRecommendation:
        """
        Calculate sulfur requirement for pH reduction
        """
        
    def get_buffer_capacity(self, soil_type: str, organic_matter: float) -> float:
        """
        Determine soil buffer capacity based on soil characteristics
        """
```

**API Specifications**:
```yaml
POST /api/v1/soil-ph/calculate-amendments
  body:
    current_ph: float (4.0-9.0)
    target_ph: float (4.0-9.0)
    soil_type: string
    organic_matter_percent: float
    field_size_acres: float
    cec: float (optional)
  response:
    amendment_type: string (lime|sulfur)
    amount_per_acre: float
    total_amount: float
    unit: string
    application_timing: string
    cost_estimate: float
    timeline_months: integer
```

---

## Epic 3: Crop Variety Recommendations

### TICKET-005: Crop Database Enhancement
**ID**: crop-variety-recommendations-1.1  
**Title**: Expand crop database with comprehensive variety data  
**Epic**: Crop Variety Recommendations  
**Priority**: Critical  
**Story Points**: 21  
**Dependencies**: Database infrastructure  

**Technical Stack**:
- PostgreSQL with JSONB for flexible variety attributes
- Python data migration scripts
- External API integrations (seed companies, universities)
- Data validation and normalization pipelines

**Acceptance Criteria**:
- [ ] Database contains 500+ crop varieties across major crops
- [ ] Each variety includes yield potential, disease resistance, maturity
- [ ] Climate zone compatibility data for all varieties
- [ ] Soil type preferences and pH ranges
- [ ] Planting date recommendations by region
- [ ] Seed company and availability information
- [ ] Regular data update mechanisms

**Database Schema**:
```sql
CREATE TABLE crops (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    scientific_name VARCHAR(150),
    category VARCHAR(50), -- grain, vegetable, forage, etc.
    family VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE crop_varieties (
    id SERIAL PRIMARY KEY,
    crop_id INTEGER REFERENCES crops(id),
    variety_name VARCHAR(150) NOT NULL,
    maturity_days INTEGER,
    yield_potential_min DECIMAL(8,2),
    yield_potential_max DECIMAL(8,2),
    yield_unit VARCHAR(20),
    climate_zones TEXT[], -- Array of compatible zones
    soil_ph_min DECIMAL(3,1),
    soil_ph_max DECIMAL(3,1),
    soil_types TEXT[], -- Array of suitable soil types
    disease_resistance JSONB, -- Flexible disease resistance data
    characteristics JSONB, -- Additional variety traits
    seed_companies JSONB, -- Availability information
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_varieties_crop_id ON crop_varieties(crop_id);
CREATE INDEX idx_varieties_climate_zones ON crop_varieties USING GIN(climate_zones);
CREATE INDEX idx_varieties_soil_types ON crop_varieties USING GIN(soil_types);
```

**Implementation Details**:
```python
# Data ingestion pipeline
class CropVarietyIngestion:
    def ingest_university_data(self, source_url: str):
        """Ingest variety trial data from university extension services"""
        
    def ingest_seed_company_data(self, company_api: str):
        """Ingest variety data from seed company APIs"""
        
    def validate_variety_data(self, variety_data: dict) -> bool:
        """Validate variety data completeness and accuracy"""
        
    def normalize_disease_resistance(self, resistance_data: dict) -> dict:
        """Standardize disease resistance ratings across sources"""
```

---

## Epic 4: Fertilizer Strategy Optimization

### TICKET-006: Market Price Integration System
**ID**: fertilizer-strategy-optimization-1.1  
**Title**: Implement real-time fertilizer price tracking  
**Epic**: Fertilizer Strategy Optimization  
**Priority**: High  
**Story Points**: 13  
**Dependencies**: Data integration framework  

**Technical Stack**:
- Python 3.11+
- FastAPI
- External market data APIs (USDA NASS, commodity exchanges)
- Time series database (TimescaleDB extension for PostgreSQL)
- Scheduled data collection (APScheduler)

**Acceptance Criteria**:
- [ ] Tracks prices for major fertilizer types (N, P, K, blends)
- [ ] Updates prices daily from multiple sources
- [ ] Stores historical price data for trend analysis
- [ ] Provides regional price variations
- [ ] Handles data source failures gracefully
- [ ] Calculates price trends and volatility metrics

**Implementation Details**:
```python
class FertilizerPriceTracker:
    def __init__(self):
        self.price_sources = [
            USDANASSProvider(),
            CMEGroupProvider(),
            LocalDealerProvider()
        ]
    
    async def update_prices(self):
        """Daily price update from all sources"""
        
    def get_current_prices(self, region: str, fertilizer_types: List[str]):
        """Get current prices for specified fertilizers in region"""
        
    def calculate_price_trends(self, fertilizer_type: str, days: int = 30):
        """Calculate price trends and volatility"""
```

**Database Schema**:
```sql
CREATE TABLE fertilizer_prices (
    id SERIAL PRIMARY KEY,
    fertilizer_type VARCHAR(50) NOT NULL,
    price_per_unit DECIMAL(10,2) NOT NULL,
    unit VARCHAR(20) NOT NULL, -- ton, cwt, lb
    region VARCHAR(100),
    source VARCHAR(50),
    price_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- TimescaleDB hypertable for time series data
SELECT create_hypertable('fertilizer_prices', 'price_date');

CREATE INDEX idx_fertilizer_prices_type_date ON fertilizer_prices(fertilizer_type, price_date);
CREATE INDEX idx_fertilizer_prices_region ON fertilizer_prices(region);
```

**API Specifications**:
```yaml
GET /api/v1/prices/fertilizer-current
  parameters:
    region: string (optional)
    fertilizer_types: array of strings (optional)
  response:
    prices: array of {
      fertilizer_type: string,
      price_per_unit: float,
      unit: string,
      region: string,
      last_updated: datetime,
      trend_7d: float,
      trend_30d: float
    }

GET /api/v1/prices/fertilizer-trends
  parameters:
    fertilizer_type: string (required)
    region: string (optional)
    days: integer (default: 30)
  response:
    fertilizer_type: string
    region: string
    price_history: array of {date, price}
    trend_analysis: {
      average_price: float,
      volatility: float,
      trend_direction: string,
      price_change_percent: float
    }
```

---

## Epic 5: Nutrient Deficiency Detection

### TICKET-007: Visual Symptom Analysis System
**ID**: nutrient-deficiency-detection-2.1  
**Title**: Implement crop photo analysis  
**Epic**: Nutrient Deficiency Detection  
**Priority**: High  
**Story Points**: 21  
**Dependencies**: Image analysis infrastructure, ML models  

**Technical Stack**:
- Python 3.11+
- TensorFlow/PyTorch for deep learning
- OpenCV for image preprocessing
- FastAPI for API endpoints
- AWS S3 or local storage for images
- GPU support for model inference

**Acceptance Criteria**:
- [ ] Accepts crop photos in common formats (JPEG, PNG)
- [ ] Preprocesses images for optimal analysis
- [ ] Identifies nutrient deficiency symptoms with confidence scores
- [ ] Supports major crops (corn, soybeans, wheat, vegetables)
- [ ] Returns specific deficiency types (N, P, K, micronutrients)
- [ ] Provides image quality feedback
- [ ] Processes images within 10 seconds

**Implementation Details**:
```python
class CropPhotoAnalyzer:
    def __init__(self):
        self.models = {
            'corn': load_model('models/corn_deficiency_v1.h5'),
            'soybean': load_model('models/soybean_deficiency_v1.h5'),
            'wheat': load_model('models/wheat_deficiency_v1.h5')
        }
        self.preprocessor = ImagePreprocessor()
    
    async def analyze_image(self, image_data: bytes, crop_type: str) -> DeficiencyAnalysis:
        """
        Analyze crop image for nutrient deficiency symptoms
        """
        # 1. Validate image format and quality
        # 2. Preprocess image (resize, normalize, enhance)
        # 3. Run through appropriate CNN model
        # 4. Post-process results and calculate confidence
        # 5. Return structured analysis
        
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Standardize image for model input
        """
        # Resize to model input size
        # Normalize pixel values
        # Apply color correction if needed
        # Remove noise and enhance features
```

**API Specifications**:
```yaml
POST /api/v1/deficiency/image-analysis
  content-type: multipart/form-data
  body:
    image: file (required)
    crop_type: string (required)
    growth_stage: string (optional)
    field_conditions: object (optional)
  response:
    analysis_id: string
    image_quality: {
      score: float (0-1),
      issues: array of strings
    }
    deficiencies: array of {
      nutrient: string,
      confidence: float (0-1),
      severity: string (mild|moderate|severe),
      affected_area_percent: float,
      symptoms_detected: array of strings
    }
    recommendations: array of {
      action: string,
      priority: string,
      timing: string
    }
```

**Model Training Requirements**:
- Training dataset with 10,000+ labeled crop images
- Balanced dataset across deficiency types and severities
- Data augmentation for robustness
- Cross-validation with expert annotations
- Model accuracy >85% on test set
- Regular model retraining pipeline

---

## Epic 6: Farm Location Input

### TICKET-008: Location Management API Endpoints
**ID**: farm-location-input-4.1
**Title**: Create location management API endpoints
**Epic**: Farm Location Input
**Priority**: Critical
**Story Points**: 8
**Dependencies**: Database schema, geocoding service

**Technical Stack**:
- Python 3.11+
- FastAPI framework
- PostGIS for geospatial data
- External geocoding APIs (Google Maps, OpenStreetMap)
- Geospatial validation libraries

**Acceptance Criteria**:
- [ ] CRUD operations for farm locations
- [ ] GPS coordinate validation and normalization
- [ ] Address geocoding with fallback providers
- [ ] Location validation against agricultural zones
- [ ] Batch location operations support
- [ ] Geospatial queries (nearby locations, within radius)

**Implementation Details**:
```python
class LocationService:
    def __init__(self):
        self.geocoders = [
            GoogleMapsGeocoder(),
            OpenStreetMapGeocoder(),
            USDAGeocoder()
        ]

    async def create_location(self, location_data: LocationCreate) -> Location:
        """Create new farm location with validation"""

    async def geocode_address(self, address: str) -> GeocodeResult:
        """Convert address to coordinates with fallback"""

    def validate_agricultural_location(self, lat: float, lng: float) -> bool:
        """Validate location is suitable for agriculture"""
```

**Database Schema**:
```sql
CREATE TABLE farm_locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    name VARCHAR(200) NOT NULL,
    address TEXT,
    coordinates GEOMETRY(POINT, 4326) NOT NULL,
    elevation_meters INTEGER,
    usda_zone VARCHAR(10),
    climate_zone VARCHAR(50),
    county VARCHAR(100),
    state VARCHAR(50),
    country VARCHAR(50) DEFAULT 'USA',
    total_acres DECIMAL(10,2),
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_farm_locations_user_id ON farm_locations(user_id);
CREATE INDEX idx_farm_locations_coordinates ON farm_locations USING GIST(coordinates);
CREATE INDEX idx_farm_locations_usda_zone ON farm_locations(usda_zone);

CREATE TABLE fields (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    farm_location_id UUID REFERENCES farm_locations(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    boundary GEOMETRY(POLYGON, 4326),
    acres DECIMAL(8,2) NOT NULL,
    soil_type VARCHAR(100),
    drainage_class VARCHAR(50),
    slope_percent DECIMAL(4,1),
    irrigation_available BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_fields_farm_location_id ON fields(farm_location_id);
CREATE INDEX idx_fields_boundary ON fields USING GIST(boundary);
```

**API Specifications**:
```yaml
POST /api/v1/locations/
  body:
    name: string (required)
    address: string (optional)
    coordinates: {lat: float, lng: float} (optional)
    total_acres: float (optional)
  response:
    id: uuid
    name: string
    address: string
    coordinates: {lat: float, lng: float}
    usda_zone: string
    climate_zone: string
    elevation_meters: integer

GET /api/v1/locations/
  parameters:
    user_id: uuid (optional, defaults to current user)
    include_fields: boolean (default: false)
  response:
    locations: array of location objects

PUT /api/v1/locations/{id}
  body: location update data
  response: updated location object

DELETE /api/v1/locations/{id}
  response: {success: boolean, message: string}

POST /api/v1/locations/validate
  body:
    coordinates: {lat: float, lng: float}
  response:
    valid: boolean
    issues: array of strings
    suggestions: array of strings
```

---

## Epic 7: Weather Impact Analysis

### TICKET-009: Weather Data Integration System
**ID**: weather-impact-analysis-11.1
**Title**: Create weather data integration and validation system
**Epic**: Weather Impact Analysis
**Priority**: High
**Story Points**: 13
**Dependencies**: Data integration framework, location services

**Technical Stack**:
- Python 3.11+
- Multiple weather API providers (NOAA, OpenWeatherMap, WeatherAPI)
- Time series data storage (TimescaleDB)
- Data validation and quality checks
- Async HTTP clients for API calls

**Acceptance Criteria**:
- [ ] Integrates with multiple weather data sources
- [ ] Provides current conditions and forecasts
- [ ] Stores historical weather data
- [ ] Validates data quality and consistency
- [ ] Handles API rate limits and failures
- [ ] Supports location-based weather queries
- [ ] Calculates agricultural weather metrics

**Implementation Details**:
```python
class WeatherDataService:
    def __init__(self):
        self.providers = {
            'noaa': NOAAWeatherProvider(),
            'openweather': OpenWeatherMapProvider(),
            'weatherapi': WeatherAPIProvider()
        }
        self.validator = WeatherDataValidator()

    async def get_current_weather(self, lat: float, lng: float) -> WeatherData:
        """Get current weather with data validation"""

    async def get_forecast(self, lat: float, lng: float, days: int = 7) -> WeatherForecast:
        """Get weather forecast with agricultural focus"""

    async def get_historical_data(self, lat: float, lng: float, start_date: date, end_date: date) -> HistoricalWeather:
        """Retrieve historical weather data"""

    def calculate_growing_degree_days(self, temp_data: List[float], base_temp: float = 50) -> float:
        """Calculate growing degree days for crop development"""

    def assess_weather_stress(self, weather_data: WeatherData, crop_type: str) -> WeatherStressAssessment:
        """Assess weather stress factors for specific crops"""
```

**Database Schema**:
```sql
CREATE TABLE weather_data (
    id SERIAL PRIMARY KEY,
    location_id UUID,
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(11, 7) NOT NULL,
    observation_time TIMESTAMP NOT NULL,
    temperature_celsius DECIMAL(5,2),
    humidity_percent INTEGER,
    precipitation_mm DECIMAL(6,2),
    wind_speed_kmh DECIMAL(5,2),
    wind_direction INTEGER,
    pressure_hpa DECIMAL(7,2),
    solar_radiation DECIMAL(8,2),
    soil_temp_celsius DECIMAL(5,2),
    data_source VARCHAR(50),
    quality_score DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- TimescaleDB hypertable for time series optimization
SELECT create_hypertable('weather_data', 'observation_time');

CREATE INDEX idx_weather_data_location_time ON weather_data(latitude, longitude, observation_time);
CREATE INDEX idx_weather_data_location_id ON weather_data(location_id);

CREATE TABLE weather_forecasts (
    id SERIAL PRIMARY KEY,
    location_id UUID,
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(11, 7) NOT NULL,
    forecast_date DATE NOT NULL,
    forecast_for_date DATE NOT NULL,
    temp_min_celsius DECIMAL(5,2),
    temp_max_celsius DECIMAL(5,2),
    precipitation_probability INTEGER,
    precipitation_mm DECIMAL(6,2),
    conditions VARCHAR(100),
    data_source VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_weather_forecasts_location_date ON weather_forecasts(latitude, longitude, forecast_for_date);
```

**API Specifications**:
```yaml
GET /api/v1/weather/current
  parameters:
    latitude: float (required)
    longitude: float (required)
    include_agricultural: boolean (default: true)
  response:
    current_conditions: {
      temperature_celsius: float,
      humidity_percent: integer,
      precipitation_mm: float,
      wind_speed_kmh: float,
      conditions: string
    }
    agricultural_metrics: {
      growing_degree_days: float,
      stress_factors: array of strings,
      irrigation_recommendation: string
    }

GET /api/v1/weather/forecast
  parameters:
    latitude: float (required)
    longitude: float (required)
    days: integer (default: 7, max: 14)
  response:
    forecast: array of daily forecasts
    agricultural_outlook: {
      planting_conditions: string,
      spray_windows: array of dates,
      stress_alerts: array of alerts
    }

POST /api/v1/weather/impact-assessment
  body:
    location: {lat: float, lng: float}
    crop_type: string
    growth_stage: string
    management_practices: array of strings
  response:
    impact_assessment: {
      overall_risk: string (low|medium|high),
      specific_risks: array of risk objects,
      recommendations: array of recommendation objects,
      optimal_timing: array of timing windows
    }
```

---

## Epic 8: User Interface and Experience

### TICKET-010: Farm Profile Management Interface
**ID**: farm-location-input-10.1
**Title**: Create field management user interface
**Epic**: User Interface
**Priority**: High
**Story Points**: 13
**Dependencies**: Location API endpoints, frontend framework

**Technical Stack**:
- Python FastAPI + Jinja2 templates OR Streamlit
- Bootstrap 5 for responsive design
- Leaflet.js for interactive maps
- JavaScript for dynamic interactions
- Chart.js for data visualization

**Acceptance Criteria**:
- [ ] Interactive map for location selection and field boundaries
- [ ] Form-based farm and field data entry
- [ ] Drag-and-drop field boundary creation
- [ ] Mobile-responsive design
- [ ] Real-time validation and feedback
- [ ] Bulk field operations (import/export)
- [ ] Integration with GPS devices

**Implementation Details**:
```python
# FastAPI + Jinja2 approach
@app.get("/farm-profile", response_class=HTMLResponse)
async def farm_profile_page(request: Request, user: User = Depends(get_current_user)):
    """Render farm profile management page"""
    farms = await get_user_farms(user.id)
    return templates.TemplateResponse("farm_profile.html", {
        "request": request,
        "user": user,
        "farms": farms,
        "maps_api_key": settings.MAPS_API_KEY
    })

# Streamlit approach (alternative)
def render_farm_profile():
    """Streamlit farm profile management interface"""
    st.title("Farm Profile Management")

    # Farm selection
    farms = get_user_farms(st.session_state.user_id)
    selected_farm = st.selectbox("Select Farm", farms)

    # Interactive map
    map_data = create_farm_map(selected_farm)
    st.pydeck_chart(map_data)

    # Field management
    with st.expander("Field Management"):
        render_field_editor(selected_farm)
```

**Frontend Components**:
```html
<!-- farm_profile.html template -->
<div class="container-fluid">
    <div class="row">
        <div class="col-md-8">
            <!-- Interactive map -->
            <div id="farm-map" style="height: 500px;"></div>
        </div>
        <div class="col-md-4">
            <!-- Farm details form -->
            <form id="farm-form">
                <div class="mb-3">
                    <label for="farm-name" class="form-label">Farm Name</label>
                    <input type="text" class="form-control" id="farm-name" required>
                </div>
                <!-- Additional form fields -->
            </form>

            <!-- Field list -->
            <div class="field-list">
                <h5>Fields</h5>
                <div id="fields-container">
                    <!-- Dynamic field list -->
                </div>
                <button class="btn btn-primary" onclick="addField()">Add Field</button>
            </div>
        </div>
    </div>
</div>

<script>
// Initialize Leaflet map
const map = L.map('farm-map').setView([40.0, -95.0], 10);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

// Field boundary drawing
const drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

const drawControl = new L.Control.Draw({
    edit: {
        featureGroup: drawnItems
    },
    draw: {
        polygon: true,
        rectangle: true,
        circle: false,
        marker: true
    }
});
map.addControl(drawControl);
</script>
```

---

## Epic 9: Testing and Quality Assurance

### TICKET-011: Comprehensive Testing Framework
**ID**: testing-framework-1.1
**Title**: Implement comprehensive testing framework for all services
**Epic**: Quality Assurance
**Priority**: Critical
**Story Points**: 21
**Dependencies**: All service implementations

**Technical Stack**:
- pytest for Python testing
- pytest-asyncio for async test support
- pytest-cov for coverage reporting
- Factory Boy for test data generation
- Docker for test environment isolation
- GitHub Actions for CI/CD

**Acceptance Criteria**:
- [ ] Unit tests for all service methods (>80% coverage)
- [ ] Integration tests for API endpoints
- [ ] End-to-end tests for critical user workflows
- [ ] Performance tests for response times
- [ ] Load tests for concurrent users
- [ ] Agricultural validation tests with expert review
- [ ] Automated test execution in CI/CD pipeline

**Implementation Details**:
```python
# Test structure
tests/
├── unit/
│   ├── test_climate_zones.py
│   ├── test_soil_ph.py
│   ├── test_crop_recommendations.py
│   └── test_weather_service.py
├── integration/
│   ├── test_api_endpoints.py
│   ├── test_database_operations.py
│   └── test_external_apis.py
├── e2e/
│   ├── test_user_workflows.py
│   └── test_recommendation_pipeline.py
├── performance/
│   ├── test_response_times.py
│   └── test_load_capacity.py
├── agricultural/
│   ├── test_recommendation_accuracy.py
│   └── test_expert_validation.py
└── fixtures/
    ├── test_data.py
    └── factories.py

# Example test implementation
class TestClimateZoneService:
    @pytest.fixture
    def climate_service(self):
        return ClimateZoneService()

    @pytest.mark.asyncio
    async def test_detect_by_coordinates_valid(self, climate_service):
        """Test climate zone detection with valid coordinates"""
        result = await climate_service.detect_by_coordinates(40.0, -95.0)

        assert result.zone_id is not None
        assert result.confidence > 0.8
        assert result.hardiness_zone is not None

    @pytest.mark.asyncio
    async def test_detect_by_coordinates_invalid(self, climate_service):
        """Test climate zone detection with invalid coordinates"""
        with pytest.raises(InvalidCoordinatesError):
            await climate_service.detect_by_coordinates(200.0, -95.0)

    def test_cache_functionality(self, climate_service):
        """Test that results are properly cached"""
        # Implementation for cache testing
```

**Agricultural Validation Framework**:
```python
class AgriculturalValidator:
    def __init__(self):
        self.expert_rules = load_expert_rules()
        self.validation_datasets = load_validation_data()

    def validate_crop_recommendations(self, recommendations: List[CropRecommendation]) -> ValidationResult:
        """Validate crop recommendations against expert knowledge"""

    def validate_fertilizer_calculations(self, calculations: FertilizerRecommendation) -> ValidationResult:
        """Validate fertilizer calculations against agronomic principles"""

    def validate_ph_adjustments(self, ph_recommendations: PHRecommendation) -> ValidationResult:
        """Validate pH adjustment calculations"""
```

**Performance Testing**:
```python
import pytest
import asyncio
from locust import HttpUser, task, between

class FarmAdvisoryUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def get_crop_recommendations(self):
        """Test crop recommendation endpoint performance"""
        self.client.post("/api/v1/recommendations/crop-varieties", json={
            "location": {"lat": 40.0, "lng": -95.0},
            "soil_data": {"ph": 6.5, "organic_matter": 3.2},
            "preferences": {"crop_types": ["corn", "soybean"]}
        })

    @task(2)
    def analyze_soil_ph(self):
        """Test soil pH analysis performance"""
        self.client.post("/api/v1/soil-ph/calculate-amendments", json={
            "current_ph": 5.8,
            "target_ph": 6.5,
            "soil_type": "clay_loam",
            "field_size_acres": 40
        })

    @task(1)
    def weather_impact_analysis(self):
        """Test weather impact analysis performance"""
        self.client.post("/api/v1/weather/impact-assessment", json={
            "location": {"lat": 40.0, "lng": -95.0},
            "crop_type": "corn",
            "growth_stage": "V6"
        })
```

---

## Ticket Prioritization and Dependencies

### Critical Path Tickets (Must Complete First):
1. **TICKET-001**: Climate Zone Data Service - Foundation for location-based recommendations
2. **TICKET-003**: pH Management Service Structure - Core service architecture pattern
3. **TICKET-005**: Crop Database Enhancement - Essential data for all crop recommendations
4. **TICKET-008**: Location Management API - Required for user farm setup
5. **TICKET-011**: Testing Framework - Quality assurance foundation

### High Priority Implementation Order:
1. **Infrastructure & Data Foundation** (Tickets 1, 3, 5, 8)
2. **Core Recommendation Engines** (Tickets 2, 4, 6)
3. **Advanced Features** (Tickets 7, 9)
4. **User Interface** (Ticket 10)
5. **Quality Assurance** (Ticket 11)

### Cross-Service Dependencies:
- All recommendation services depend on location and climate data
- Weather impact analysis requires weather data integration
- Image analysis requires ML model infrastructure
- All services require comprehensive testing framework

---

## Epic 10: Crop Rotation Planning

### TICKET-012: Multi-Year Rotation Optimization Engine
**ID**: crop-rotation-planning-1.1
**Title**: Implement intelligent crop rotation planning system
**Epic**: Crop Rotation Planning
**Priority**: High
**Story Points**: 21
**Dependencies**: Crop database, soil health models, economic data

**User Stories Addressed**: US-002

**Technical Stack**:
- Python 3.11+
- Optimization algorithms (scipy.optimize, OR-Tools)
- Agricultural rotation rules engine
- Economic modeling libraries

**Acceptance Criteria**:
- [ ] Generates 3-5 year rotation plans
- [ ] Considers soil health, pest management, and economics
- [ ] Integrates nitrogen fixation and soil organic matter
- [ ] Provides break-even analysis for rotation options
- [ ] Handles field-specific constraints and preferences

**Implementation Details**:
```python
class RotationOptimizer:
    def optimize_rotation(
        self,
        field_data: FieldData,
        available_crops: List[Crop],
        constraints: RotationConstraints,
        objectives: OptimizationObjectives
    ) -> RotationPlan:
        """
        Multi-objective optimization for crop rotation:
        - Maximize profitability
        - Maintain soil health
        - Minimize pest/disease pressure
        - Balance nutrient cycling
        """

    def calculate_rotation_benefits(
        self,
        rotation_plan: RotationPlan,
        baseline_monoculture: Crop
    ) -> RotationBenefits:
        """Calculate economic and agronomic benefits"""
```

**API Specifications**:
```yaml
POST /api/v1/rotation/optimize
  body:
    field_id: uuid
    planning_horizon_years: integer (3-7)
    crop_preferences: array of crop types
    constraints: {
      equipment_limitations: array,
      market_contracts: array,
      sustainability_goals: object
    }
  response:
    rotation_plans: array of {
      plan_id: string,
      years: array of {year, crop, expected_yield, revenue, costs},
      total_roi: float,
      sustainability_score: float,
      risk_assessment: object
    }
```

---

## Epic 11: Cover Crop Management

### TICKET-013: Cover Crop Selection and Integration System
**ID**: cover-crop-selection-1.1
**Title**: Implement cover crop recommendation and integration system
**Epic**: Cover Crop Management
**Priority**: High
**Story Points**: 13
**Dependencies**: Crop database, climate data, soil health models

**User Stories Addressed**: US-011

**Technical Stack**:
- Python 3.11+
- Cover crop species database
- Climate zone integration
- Soil health modeling

**Acceptance Criteria**:
- [ ] Recommends cover crop species based on goals and conditions
- [ ] Provides planting and termination timing guidance
- [ ] Calculates nitrogen fixation and soil health benefits
- [ ] Integrates with main crop rotation planning
- [ ] Includes cost-benefit analysis

**Implementation Details**:
```python
class CoverCropSelector:
    def recommend_cover_crops(
        self,
        field_data: FieldData,
        main_crop_rotation: RotationPlan,
        goals: CoverCropGoals
    ) -> CoverCropRecommendation:
        """
        Recommend cover crops based on:
        - Soil health goals (erosion, organic matter, compaction)
        - Nutrient management (N fixation, scavenging)
        - Pest/disease management
        - Integration with main crops
        """

    def calculate_cover_crop_benefits(
        self,
        cover_crop_plan: CoverCropPlan,
        field_conditions: FieldData
    ) -> CoverCropBenefits:
        """Quantify soil health and economic benefits"""
```

---

## Epic 12: Drought and Water Management

### TICKET-014: Drought Resilience and Water Conservation System
**ID**: drought-management-1.1
**Title**: Implement drought management and water conservation system
**Epic**: Drought Management
**Priority**: High
**Story Points**: 13
**Dependencies**: Weather data, soil moisture models, crop water requirements

**User Stories Addressed**: US-012

**Technical Stack**:
- Python 3.11+
- Soil moisture modeling
- Crop water requirement calculations
- Weather pattern analysis

**Acceptance Criteria**:
- [ ] Assesses drought risk based on historical and forecast data
- [ ] Recommends drought-tolerant crop varieties
- [ ] Provides water conservation practice recommendations
- [ ] Calculates irrigation efficiency improvements
- [ ] Integrates with crop selection and rotation planning

**Implementation Details**:
```python
class DroughtManagementService:
    def assess_drought_risk(
        self,
        location: Coordinates,
        crop_plan: CropPlan,
        historical_years: int = 10
    ) -> DroughtRiskAssessment:
        """Assess drought probability and impact"""

    def recommend_conservation_practices(
        self,
        field_data: FieldData,
        drought_risk: DroughtRiskAssessment
    ) -> ConservationRecommendations:
        """Recommend water conservation practices"""
```

---

## Epic 13: Precision Agriculture and Technology

### TICKET-015: Precision Agriculture ROI Analysis System
**ID**: precision-agriculture-roi-1.1
**Title**: Implement precision agriculture technology ROI assessment
**Epic**: Precision Agriculture
**Priority**: Medium
**Story Points**: 21
**Dependencies**: Technology cost database, yield modeling, economic analysis

**User Stories Addressed**: US-013

**Technical Stack**:
- Python 3.11+
- Economic modeling libraries
- Technology cost databases
- ROI calculation engines

**Acceptance Criteria**:
- [ ] Evaluates ROI for precision agriculture technologies
- [ ] Considers farm size, crop types, and current practices
- [ ] Provides payback period and break-even analysis
- [ ] Includes risk assessment and sensitivity analysis
- [ ] Recommends implementation priorities

**Implementation Details**:
```python
class PrecisionAgROIAnalyzer:
    def analyze_technology_roi(
        self,
        farm_data: FarmData,
        technology_options: List[PrecisionTechnology],
        investment_horizon: int
    ) -> ROIAnalysis:
        """Analyze ROI for precision agriculture investments"""

    def prioritize_investments(
        self,
        roi_analyses: List[ROIAnalysis],
        budget_constraints: BudgetConstraints
    ) -> InvestmentPriorities:
        """Prioritize technology investments based on ROI and constraints"""
```

---

## Epic 14: Micronutrient Management

### TICKET-016: Micronutrient Assessment and Management System
**ID**: micronutrient-management-1.1
**Title**: Implement micronutrient deficiency assessment and management
**Epic**: Micronutrient Management
**Priority**: Medium
**Story Points**: 13
**Dependencies**: Soil testing integration, crop response models, micronutrient database

**User Stories Addressed**: US-019

**Technical Stack**:
- Python 3.11+
- Micronutrient deficiency models
- Crop response curves
- Cost-benefit analysis tools

**Acceptance Criteria**:
- [ ] Identifies micronutrient deficiency risks
- [ ] Recommends soil and tissue testing protocols
- [ ] Provides micronutrient application recommendations
- [ ] Calculates cost-benefit of micronutrient supplementation
- [ ] Integrates with main fertilizer recommendations

**Implementation Details**:
```python
class MicronutrientManager:
    def assess_deficiency_risk(
        self,
        soil_data: SoilData,
        crop_type: str,
        yield_goals: YieldGoals
    ) -> MicronutrientRisk:
        """Assess micronutrient deficiency risk"""

    def recommend_supplementation(
        self,
        deficiency_risk: MicronutrientRisk,
        application_methods: List[ApplicationMethod]
    ) -> MicronutrientRecommendation:
        """Recommend micronutrient supplementation strategy"""
```

---

## Epic 15: Soil and Laboratory Test Integration

### TICKET-017: Laboratory Test Integration System
**ID**: soil-tissue-test-integration-1.1
**Title**: Implement soil and tissue test result integration and interpretation
**Epic**: Laboratory Integration
**Priority**: High
**Story Points**: 13
**Dependencies**: Laboratory APIs, interpretation algorithms, recommendation engine

**User Stories Addressed**: US-015

**Technical Stack**:
- Python 3.11+
- Laboratory API integrations
- Data parsing and validation
- Recommendation adjustment algorithms

**Acceptance Criteria**:
- [ ] Integrates with major soil and tissue testing laboratories
- [ ] Parses and validates test results automatically
- [ ] Adjusts fertilizer recommendations based on test results
- [ ] Provides test result interpretation and explanations
- [ ] Tracks testing history and trends

**Implementation Details**:
```python
class LabTestIntegrator:
    def integrate_soil_test(
        self,
        test_results: SoilTestResults,
        field_id: UUID,
        crop_plan: CropPlan
    ) -> AdjustedRecommendations:
        """Integrate soil test results and adjust recommendations"""

    def interpret_tissue_test(
        self,
        tissue_results: TissueTestResults,
        crop_stage: GrowthStage,
        field_conditions: FieldData
    ) -> TissueTestInterpretation:
        """Interpret tissue test results and provide corrective actions"""
```

---

## Epic 16: Tillage and Soil Health

### TICKET-018: Tillage Practice Optimization System
**ID**: tillage-practice-recommendations-1.1
**Title**: Implement tillage practice recommendation and transition planning
**Epic**: Tillage Management
**Priority**: Medium
**Story Points**: 13
**Dependencies**: Soil health models, equipment database, economic analysis

**User Stories Addressed**: US-017

**Technical Stack**:
- Python 3.11+
- Soil health modeling
- Equipment compatibility analysis
- Transition planning algorithms

**Acceptance Criteria**:
- [ ] Compares tillage systems (no-till, reduced-till, conventional)
- [ ] Assesses soil health impacts and benefits
- [ ] Provides transition planning for tillage system changes
- [ ] Calculates economic impacts and equipment requirements
- [ ] Integrates with crop rotation and cover crop planning

---

## Epic 17: Sustainable Intensification

### TICKET-019: Sustainable Yield Optimization System
**ID**: sustainable-intensification-1.1
**Title**: Implement integrated sustainability and yield optimization
**Epic**: Sustainable Intensification
**Priority**: High
**Story Points**: 21
**Dependencies**: All agricultural systems, sustainability metrics, economic models

**User Stories Addressed**: US-018

**Technical Stack**:
- Python 3.11+
- Multi-objective optimization
- Sustainability assessment frameworks
- Long-term modeling capabilities

**Acceptance Criteria**:
- [ ] Optimizes yield while maintaining soil health indicators
- [ ] Provides sustainability scorecards and metrics
- [ ] Balances short-term profitability with long-term sustainability
- [ ] Integrates environmental impact assessments
- [ ] Includes carbon footprint and sequestration calculations

---

## Epic 18: Government Programs and Policy

### TICKET-020: Government Program Integration System
**ID**: government-program-integration-1.1
**Title**: Implement government program and policy integration
**Epic**: Policy Integration
**Priority**: Medium
**Story Points**: 13
**Dependencies**: Government databases, policy APIs, compliance frameworks

**User Stories Addressed**: US-020

**Technical Stack**:
- Python 3.11+
- Government API integrations
- Policy database management
- Compliance checking algorithms

**Acceptance Criteria**:
- [ ] Integrates with USDA, NRCS, and state program databases
- [ ] Identifies applicable programs and incentives
- [ ] Checks compliance requirements for practices
- [ ] Calculates potential program benefits and payments
- [ ] Provides application guidance and deadlines

---

## Epic 19: User Experience and Mobile

### TICKET-021: Mobile Field Application
**ID**: mobile-field-access-1.1
**Title**: Implement mobile field access and offline capabilities
**Epic**: Mobile Experience
**Priority**: High
**Story Points**: 21
**Dependencies**: Frontend framework, offline storage, GPS integration

**User Stories Addressed**: US-023

**Technical Stack**:
- Progressive Web App (PWA) or React Native
- Offline data synchronization
- GPS and camera integration
- Push notification system

**Acceptance Criteria**:
- [ ] Works offline with local data caching
- [ ] GPS integration for field location services
- [ ] Camera integration for crop photo analysis
- [ ] Push notifications for time-sensitive recommendations
- [ ] Synchronizes data when connectivity is restored

---

## Epic 20: Recommendation Tracking and Learning

### TICKET-022: Recommendation History and Outcome Tracking
**ID**: recommendation-tracking-1.1
**Title**: Implement recommendation history tracking and outcome analysis
**Epic**: Learning System
**Priority**: High
**Story Points**: 13
**Dependencies**: Database design, analytics framework, machine learning pipeline

**User Stories Addressed**: US-022

**Technical Stack**:
- Python 3.11+
- Time series database
- Analytics and reporting tools
- Machine learning for outcome prediction

**Acceptance Criteria**:
- [ ] Tracks all recommendations and user actions
- [ ] Collects outcome data and farmer feedback
- [ ] Provides historical analysis and trends
- [ ] Learns from outcomes to improve future recommendations
- [ ] Generates performance reports and insights

---

## Epic 21: Advanced Fertilizer Management

### TICKET-023: Fertilizer Type Selection and Application Method Optimization
**ID**: fertilizer-type-application-1.1
**Title**: Implement comprehensive fertilizer type and application method selection
**Epic**: Advanced Fertilizer Management
**Priority**: High
**Story Points**: 13
**Dependencies**: Fertilizer database, equipment compatibility, cost analysis

**User Stories Addressed**: US-006, US-007

**Technical Stack**:
- Python 3.11+
- Fertilizer characteristics database
- Equipment compatibility matrix
- Cost-benefit analysis tools

**Acceptance Criteria**:
- [ ] Compares organic, synthetic, and slow-release fertilizers
- [ ] Evaluates liquid vs granular application methods
- [ ] Considers equipment compatibility and labor requirements
- [ ] Provides cost-effectiveness analysis
- [ ] Integrates with timing and environmental considerations

---

## Epic 22: Environmental Impact and Runoff Prevention

### TICKET-024: Environmental Impact Assessment and Runoff Prevention
**ID**: runoff-prevention-1.1
**Title**: Implement environmental impact assessment and runoff prevention system
**Epic**: Environmental Stewardship
**Priority**: High
**Story Points**: 13
**Dependencies**: GIS data, environmental models, regulatory databases

**User Stories Addressed**: US-010

**Technical Stack**:
- Python 3.11+
- GIS and spatial analysis tools
- Environmental modeling libraries
- Regulatory compliance frameworks

**Acceptance Criteria**:
- [ ] Assesses runoff risk based on field characteristics
- [ ] Recommends buffer strips and conservation practices
- [ ] Calculates environmental impact scores
- [ ] Ensures regulatory compliance
- [ ] Provides mitigation strategies and best practices

---

## User Story Coverage Summary

### ✅ **Complete Coverage: All 23 User Stories Mapped to Tickets**

**Epic 1-9: Foundation Tickets (11 tickets)**
- TICKET-001, 002: US-001 (Crop Variety Recommendation)
- TICKET-003, 004: US-005 (Soil pH Management)
- TICKET-005: US-001 (Crop Variety Recommendation - database)
- TICKET-006: US-009 (Cost-Effective Fertilizer Strategy)
- TICKET-007: US-004, US-014 (Nutrient Deficiency Detection)
- TICKET-008: US-021 (User Profile Management)
- TICKET-009: US-016 (Weather Impact Analysis)
- TICKET-010: US-021, US-023 (User Interface)
- TICKET-011: All stories (Testing Framework)

**Epic 10-22: Comprehensive Coverage Tickets (12 tickets)**
- TICKET-012: US-002 (Crop Rotation Planning)
- TICKET-013: US-011 (Cover Crop Selection)
- TICKET-014: US-012 (Drought Management)
- TICKET-015: US-013 (Precision Agriculture ROI)
- TICKET-016: US-019 (Micronutrient Management)
- TICKET-017: US-015 (Soil/Tissue Test Integration)
- TICKET-018: US-017 (Tillage Practice Recommendations)
- TICKET-019: US-018 (Sustainable Intensification)
- TICKET-020: US-020 (Government Program Integration)
- TICKET-021: US-023 (Mobile Field Access)
- TICKET-022: US-022 (Recommendation History)
- TICKET-023: US-006, US-007 (Fertilizer Type/Application)
- TICKET-024: US-010 (Runoff Prevention)

**Additional Coverage**:
- US-003 (Soil Fertility Assessment): Covered by TICKET-003, 004, 017
- US-008 (Fertilizer Timing): Covered by TICKET-006, 023, 024

### **Total: 23 Tickets Covering All 23 User Stories**

This comprehensive ticket structure ensures that every user story has explicit technical implementation tickets with detailed specifications, acceptance criteria, and agricultural domain expertise requirements for AI coding agents.

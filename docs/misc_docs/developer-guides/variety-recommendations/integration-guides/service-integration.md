# Service Integration Guide

## Overview

This guide covers integrating the crop variety recommendations system with other services in the CAAIN Soil Hub ecosystem, including the recommendation engine, climate zone detection, and data integration services.

## Service Architecture

### Service Dependencies

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

### Service Endpoints

| Service | Base URL | Port | Purpose |
|---------|----------|------|---------|
| Variety Recommendations | `http://localhost:8001` | 8001 | Core variety recommendations |
| Recommendation Engine | `http://localhost:8002` | 8002 | Agricultural recommendations |
| Climate Zone Detection | `http://localhost:8003` | 8003 | Climate zone data |
| Data Integration | `http://localhost:8004` | 8004 | External data sources |
| Market Price Service | `http://localhost:8005` | 8005 | Market price data |

## Integration Patterns

### 1. Synchronous Service Calls

Direct HTTP calls to other services for real-time data.

```python
import httpx
from typing import Dict, Any

class ServiceIntegration:
    def __init__(self):
        self.climate_service_url = "http://localhost:8003"
        self.soil_service_url = "http://localhost:8004"
        self.market_service_url = "http://localhost:8005"
    
    async def get_climate_zone(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Get climate zone data from climate service."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.climate_service_url}/api/v1/climate-zones/by-coordinates",
                params={"latitude": latitude, "longitude": longitude}
            )
            return response.json()
    
    async def get_soil_data(self, field_id: str) -> Dict[str, Any]:
        """Get soil data from soil service."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.soil_service_url}/api/v1/soil-data/{field_id}"
            )
            return response.json()
    
    async def get_market_prices(self, crop_type: str) -> Dict[str, Any]:
        """Get market prices from market service."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.market_service_url}/api/v1/prices/{crop_type}"
            )
            return response.json()
```

### 2. Asynchronous Service Calls

Parallel service calls for improved performance.

```python
import asyncio
import httpx
from typing import List, Dict, Any

class AsyncServiceIntegration:
    def __init__(self):
        self.services = {
            "climate": "http://localhost:8003",
            "soil": "http://localhost:8004",
            "market": "http://localhost:8005"
        }
    
    async def get_all_data(self, latitude: float, longitude: float, field_id: str, crop_type: str) -> Dict[str, Any]:
        """Get data from all services in parallel."""
        async with httpx.AsyncClient() as client:
            tasks = [
                self._get_climate_data(client, latitude, longitude),
                self._get_soil_data(client, field_id),
                self._get_market_data(client, crop_type)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            return {
                "climate_data": results[0] if not isinstance(results[0], Exception) else None,
                "soil_data": results[1] if not isinstance(results[1], Exception) else None,
                "market_data": results[2] if not isinstance(results[2], Exception) else None
            }
    
    async def _get_climate_data(self, client: httpx.AsyncClient, latitude: float, longitude: float) -> Dict[str, Any]:
        response = await client.get(
            f"{self.services['climate']}/api/v1/climate-zones/by-coordinates",
            params={"latitude": latitude, "longitude": longitude}
        )
        return response.json()
    
    async def _get_soil_data(self, client: httpx.AsyncClient, field_id: str) -> Dict[str, Any]:
        response = await client.get(
            f"{self.services['soil']}/api/v1/soil-data/{field_id}"
        )
        return response.json()
    
    async def _get_market_data(self, client: httpx.AsyncClient, crop_type: str) -> Dict[str, Any]:
        response = await client.get(
            f"{self.services['market']}/api/v1/prices/{crop_type}"
        )
        return response.json()
```

### 3. Service Discovery

Dynamic service discovery for microservices architecture.

```python
import httpx
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class ServiceDiscovery:
    def __init__(self, discovery_service_url: str = "http://localhost:8500"):
        self.discovery_service_url = discovery_service_url
        self.service_cache: Dict[str, str] = {}
    
    async def get_service_url(self, service_name: str) -> Optional[str]:
        """Get service URL from service discovery."""
        if service_name in self.service_cache:
            return self.service_cache[service_name]
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.discovery_service_url}/api/v1/services/{service_name}"
                )
                if response.status_code == 200:
                    service_info = response.json()
                    service_url = service_info["url"]
                    self.service_cache[service_name] = service_url
                    return service_url
        except Exception as e:
            logger.error(f"Service discovery error for {service_name}: {e}")
        
        return None
    
    async def call_service(self, service_name: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Call a service using service discovery."""
        service_url = await self.get_service_url(service_name)
        if not service_url:
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{service_url}{endpoint}", **kwargs)
                return response.json()
        except Exception as e:
            logger.error(f"Service call error for {service_name}: {e}")
            return None
```

## Service-Specific Integrations

### 1. Recommendation Engine Integration

Integrate with the core recommendation engine for agricultural recommendations.

```python
class RecommendationEngineIntegration:
    def __init__(self, recommendation_service_url: str = "http://localhost:8002"):
        self.recommendation_service_url = recommendation_service_url
    
    async def get_crop_recommendations(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get crop recommendations from recommendation engine."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.recommendation_service_url}/api/v1/recommendations/crop-selection",
                json=request_data
            )
            return response.json()
    
    async def get_fertilizer_recommendations(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get fertilizer recommendations from recommendation engine."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.recommendation_service_url}/api/v1/recommendations/fertilizer-type",
                json=request_data
            )
            return response.json()
```

### 2. Climate Zone Service Integration

Integrate with climate zone detection for location-based recommendations.

```python
class ClimateZoneIntegration:
    def __init__(self, climate_service_url: str = "http://localhost:8003"):
        self.climate_service_url = climate_service_url
    
    async def detect_climate_zone(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Detect climate zone for coordinates."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.climate_service_url}/api/v1/climate-zones/detect",
                json={
                    "latitude": latitude,
                    "longitude": longitude,
                    "include_details": True
                }
            )
            return response.json()
    
    async def get_climate_data(self, climate_zone: str) -> Dict[str, Any]:
        """Get climate data for a specific zone."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.climate_service_url}/api/v1/climate-zones/{climate_zone}/data"
            )
            return response.json()
```

### 3. Data Integration Service

Integrate with data integration service for external data sources.

```python
class DataIntegrationService:
    def __init__(self, data_service_url: str = "http://localhost:8004"):
        self.data_service_url = data_service_url
    
    async def get_soil_data(self, field_id: str) -> Dict[str, Any]:
        """Get soil data from data integration service."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.data_service_url}/api/v1/soil-data/{field_id}"
            )
            return response.json()
    
    async def get_weather_data(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Get weather data from data integration service."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.data_service_url}/api/v1/weather/current",
                params={"latitude": latitude, "longitude": longitude}
            )
            return response.json()
```

## Error Handling and Resilience

### 1. Circuit Breaker Pattern

Implement circuit breaker for service calls.

```python
import asyncio
from enum import Enum
from typing import Callable, Any
import time

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Call function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
            
            raise e
```

### 2. Retry Logic

Implement retry logic for failed service calls.

```python
import asyncio
from typing import Callable, Any
import random

class RetryHandler:
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
    
    async def retry(self, func: Callable, *args, **kwargs) -> Any:
        """Retry function call with exponential backoff."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    delay = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
                    await asyncio.sleep(delay)
                else:
                    break
        
        raise last_exception
```

### 3. Fallback Mechanisms

Implement fallback mechanisms for service failures.

```python
class ServiceFallback:
    def __init__(self):
        self.fallback_data = {
            "climate_zones": {
                "6a": {"min_temp": -23.3, "max_temp": -20.6},
                "6b": {"min_temp": -20.6, "max_temp": -17.8}
            },
            "soil_types": {
                "clay_loam": {"ph_range": [6.0, 7.5], "drainage": "moderate"}
            }
        }
    
    async def get_climate_zone_fallback(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Fallback climate zone data."""
        # Simple fallback based on latitude
        if latitude > 45:
            return {"zone": "6a", "confidence": 0.5, "source": "fallback"}
        elif latitude > 40:
            return {"zone": "6b", "confidence": 0.5, "source": "fallback"}
        else:
            return {"zone": "7a", "confidence": 0.5, "source": "fallback"}
    
    async def get_soil_data_fallback(self, field_id: str) -> Dict[str, Any]:
        """Fallback soil data."""
        return {
            "ph": 6.5,
            "organic_matter_percent": 3.0,
            "drainage": "well_drained",
            "soil_type": "clay_loam",
            "source": "fallback"
        }
```

## Configuration Management

### 1. Service Configuration

```python
from pydantic import BaseSettings

class ServiceConfig(BaseSettings):
    # Service URLs
    variety_service_url: str = "http://localhost:8001"
    recommendation_service_url: str = "http://localhost:8002"
    climate_service_url: str = "http://localhost:8003"
    data_service_url: str = "http://localhost:8004"
    market_service_url: str = "http://localhost:8005"
    
    # Timeouts
    request_timeout: int = 30
    connection_timeout: int = 10
    
    # Retry settings
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Circuit breaker settings
    failure_threshold: int = 5
    circuit_timeout: int = 60
    
    class Config:
        env_file = ".env"
```

### 2. Environment Variables

```bash
# Service URLs
VARIETY_SERVICE_URL=http://localhost:8001
RECOMMENDATION_SERVICE_URL=http://localhost:8002
CLIMATE_SERVICE_URL=http://localhost:8003
DATA_SERVICE_URL=http://localhost:8004
MARKET_SERVICE_URL=http://localhost:8005

# Timeouts
REQUEST_TIMEOUT=30
CONNECTION_TIMEOUT=10

# Retry settings
MAX_RETRIES=3
RETRY_DELAY=1.0

# Circuit breaker settings
FAILURE_THRESHOLD=5
CIRCUIT_TIMEOUT=60
```

## Testing Integration

### 1. Unit Tests

```python
import pytest
from unittest.mock import AsyncMock, patch
from your_module import ServiceIntegration

class TestServiceIntegration:
    @pytest.fixture
    def service_integration(self):
        return ServiceIntegration()
    
    @pytest.mark.asyncio
    async def test_get_climate_zone_success(self, service_integration):
        """Test successful climate zone retrieval."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.json.return_value = {"zone": "6a", "confidence": 0.9}
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            result = await service_integration.get_climate_zone(40.7128, -74.0060)
            
            assert result["zone"] == "6a"
            assert result["confidence"] == 0.9
    
    @pytest.mark.asyncio
    async def test_get_climate_zone_failure(self, service_integration):
        """Test climate zone retrieval failure."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = Exception("Service unavailable")
            
            with pytest.raises(Exception):
                await service_integration.get_climate_zone(40.7128, -74.0060)
```

### 2. Integration Tests

```python
import pytest
import httpx
from your_module import ServiceIntegration

class TestServiceIntegrationE2E:
    @pytest.mark.asyncio
    async def test_end_to_end_integration(self):
        """Test end-to-end service integration."""
        service_integration = ServiceIntegration()
        
        # Test with real services (requires running services)
        try:
            result = await service_integration.get_climate_zone(40.7128, -74.0060)
            assert "zone" in result
            assert "confidence" in result
        except httpx.ConnectError:
            pytest.skip("Services not running")
```

## Monitoring and Observability

### 1. Service Health Checks

```python
class ServiceHealthChecker:
    def __init__(self, services: Dict[str, str]):
        self.services = services
    
    async def check_all_services(self) -> Dict[str, bool]:
        """Check health of all services."""
        health_status = {}
        
        for service_name, service_url in self.services.items():
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{service_url}/health", timeout=5)
                    health_status[service_name] = response.status_code == 200
            except Exception:
                health_status[service_name] = False
        
        return health_status
```

### 2. Metrics Collection

```python
from prometheus_client import Counter, Histogram, Gauge

# Metrics
service_calls_total = Counter('service_calls_total', 'Total service calls', ['service', 'status'])
service_call_duration = Histogram('service_call_duration_seconds', 'Service call duration', ['service'])
service_availability = Gauge('service_availability', 'Service availability', ['service'])

class MetricsCollector:
    @staticmethod
    def record_service_call(service_name: str, status: str, duration: float):
        """Record service call metrics."""
        service_calls_total.labels(service=service_name, status=status).inc()
        service_call_duration.labels(service=service_name).observe(duration)
    
    @staticmethod
    def update_service_availability(service_name: str, is_available: bool):
        """Update service availability metric."""
        service_availability.labels(service=service_name).set(1 if is_available else 0)
```

## Best Practices

### 1. Service Communication

- Use async/await for non-blocking calls
- Implement proper timeout handling
- Use connection pooling for HTTP clients
- Implement retry logic with exponential backoff
- Use circuit breakers for fault tolerance

### 2. Error Handling

- Handle service unavailability gracefully
- Implement fallback mechanisms
- Log service call failures
- Monitor service health
- Use structured logging

### 3. Performance

- Use parallel service calls where possible
- Implement caching for frequently accessed data
- Use connection pooling
- Monitor service response times
- Implement rate limiting

### 4. Security

- Use HTTPS for all service calls
- Implement proper authentication
- Validate all service responses
- Use secure configuration management
- Implement access controls

## Troubleshooting

### Common Issues

1. **Service Unavailable**
   - Check service health endpoints
   - Verify service URLs and ports
   - Check network connectivity
   - Review service logs

2. **Timeout Errors**
   - Increase timeout values
   - Check service performance
   - Implement retry logic
   - Use circuit breakers

3. **Authentication Failures**
   - Verify API keys and tokens
   - Check permission levels
   - Review authentication headers
   - Test with different credentials

4. **Data Inconsistencies**
   - Validate service responses
   - Check data formats
   - Review service versions
   - Implement data validation

### Debugging Tools

```python
import logging
import json

class ServiceDebugger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def log_service_call(self, service_name: str, endpoint: str, request_data: Dict[str, Any], response_data: Dict[str, Any]):
        """Log service call details."""
        self.logger.info(f"Service call: {service_name}{endpoint}")
        self.logger.debug(f"Request: {json.dumps(request_data, indent=2)}")
        self.logger.debug(f"Response: {json.dumps(response_data, indent=2)}")
    
    def log_service_error(self, service_name: str, endpoint: str, error: Exception):
        """Log service call error."""
        self.logger.error(f"Service call failed: {service_name}{endpoint}")
        self.logger.error(f"Error: {str(error)}")
```
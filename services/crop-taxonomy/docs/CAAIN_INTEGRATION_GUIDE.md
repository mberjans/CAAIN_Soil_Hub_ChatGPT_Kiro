# CAAIN Soil Hub Integration Guide

## Overview

This document provides comprehensive guidance for integrating the crop-taxonomy service with other CAAIN Soil Hub services. The integration service enables seamless communication, data synchronization, and cross-service functionality across the entire CAAIN ecosystem.

## Architecture

### Integration Service Components

```
┌─────────────────────────────────────────────────────────────┐
│                CAAIN Integration Service                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ Service Clients  │  │ Health Monitor   │  │ Data Sync    │ │
│  │                 │  │                 │  │              │ │
│  │ • HTTP Clients  │  │ • Status Checks  │  │ • Cache      │ │
│  │ • Retry Logic   │  │ • Performance    │  │ • Validation │ │
│  │ • Error Handle  │  │ • Metrics        │  │ • Consistency│ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                  CAAIN Services                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │Recommendation│ │Data Integration│ │AI Agent      │        │
│  │Engine        │ │Service        │ │Service       │        │
│  └──────────────┘ └──────────────┘ └──────────────┘        │
│                                                             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │Question      │ │Cover Crop    │ │User          │        │
│  │Router        │ │Selection     │ │Management    │        │
│  └──────────────┘ └──────────────┘ └──────────────┘        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Service Configuration

### Integrated Services

The integration service connects with the following CAAIN services:

#### Critical Services (Required for Core Functionality)
- **recommendation-engine** (Port 8001): Core agricultural recommendations
- **data-integration** (Port 8003): Soil, climate, and weather data
- **question-router** (Port 8000): Question routing and intent classification

#### Optional Services (Enhanced Functionality)
- **ai-agent** (Port 8002): AI-powered explanations and context management
- **cover-crop-selection** (Port 8006): Cover crop recommendations
- **user-management** (Port 8005): User profiles and farm management
- **image-analysis** (Port 8004): Crop image analysis and deficiency detection

### Service Configuration Format

```python
{
    "service_name": {
        "base_url": "http://localhost:port",
        "endpoints": {
            "health": "/health",
            "primary_endpoint": "/api/v1/endpoint"
        },
        "timeout": 30,
        "retry_attempts": 3,
        "critical": True/False
    }
}
```

## API Endpoints

### Integration Management

#### Health Check
```http
GET /api/v1/integration/health
```
Returns overall integration service health status.

#### Service Status
```http
GET /api/v1/integration/services/status
```
Returns comprehensive status of all integrated services.

#### Health Checks
```http
POST /api/v1/integration/services/health-check
```
Performs health checks on all services and returns results.

### Data Integration

#### Soil Data Retrieval
```http
GET /api/v1/integration/data/soil/{latitude}/{longitude}
```
Retrieves soil characteristics for a specific location.

#### Climate Data Retrieval
```http
GET /api/v1/integration/data/climate/{latitude}/{longitude}
```
Retrieves climate zone data for a specific location.

#### Crop Data Synchronization
```http
POST /api/v1/integration/data/sync-crop-data
Content-Type: application/json

{
    "variety_id": "corn_variety_123",
    "crop_name": "Corn",
    "variety_name": "Pioneer P1234",
    "characteristics": {
        "yield_potential": "high",
        "disease_resistance": ["rust", "blight"],
        "maturity_days": 110
    }
}
```

#### Data Consistency Validation
```http
POST /api/v1/integration/data/validate-consistency
Content-Type: application/json

{
    "data_type": "crop_variety",
    "data": {
        "variety_id": "corn_variety_123",
        "crop_name": "Corn",
        "variety_name": "Pioneer P1234"
    }
}
```

### AI Integration

#### Recommendation Explanation
```http
POST /api/v1/integration/ai/explain-recommendation
Content-Type: application/json

{
    "variety_id": "corn_variety_123",
    "confidence_score": 0.85,
    "recommendation_reason": "High yield potential for your soil type",
    "location": {
        "latitude": 40.7128,
        "longitude": -74.0060
    }
}
```

### Service Management

#### Individual Service Status
```http
GET /api/v1/integration/services/{service_name}/status
```
Returns detailed status for a specific service.

#### Direct Service Call
```http
POST /api/v1/integration/services/{service_name}/call
Content-Type: application/json

{
    "endpoint": "/api/v1/endpoint",
    "method": "GET",
    "data": {...},
    "params": {...}
}
```

### Monitoring

#### Integration Metrics
```http
GET /api/v1/integration/monitoring/metrics
```
Returns performance metrics and monitoring data.

## Usage Examples

### Python Client Usage

```python
import asyncio
from src.services.caain_integration_service import get_integration_service

async def example_usage():
    # Get integration service instance
    integration_service = get_integration_service()
    
    # Check all services health
    health_status = await integration_service.health_check_all_services()
    print(f"Services health: {health_status}")
    
    # Get soil data for a location
    soil_data = await integration_service.get_soil_data_for_location(
        latitude=40.7128,
        longitude=-74.0060
    )
    print(f"Soil data: {soil_data}")
    
    # Sync crop variety data
    crop_data = {
        "variety_id": "corn_123",
        "crop_name": "Corn",
        "variety_name": "Test Variety"
    }
    sync_result = await integration_service.sync_crop_data_with_recommendation_engine(crop_data)
    print(f"Sync result: {sync_result}")
    
    # Get AI explanation
    recommendation_data = {
        "variety_id": "corn_123",
        "confidence_score": 0.85
    }
    explanation = await integration_service.get_ai_explanation_for_recommendation(recommendation_data)
    print(f"AI explanation: {explanation}")

# Run the example
asyncio.run(example_usage())
```

### HTTP Client Usage

```python
import requests

# Check integration health
response = requests.get("http://localhost:8000/api/v1/integration/health")
print(response.json())

# Get soil data
response = requests.get("http://localhost:8000/api/v1/integration/data/soil/40.7128/-74.0060")
soil_data = response.json()
print(f"Soil data: {soil_data}")

# Sync crop data
crop_data = {
    "variety_id": "corn_123",
    "crop_name": "Corn",
    "variety_name": "Test Variety"
}
response = requests.post(
    "http://localhost:8000/api/v1/integration/data/sync-crop-data",
    json=crop_data
)
sync_result = response.json()
print(f"Sync result: {sync_result}")
```

## Error Handling

### Service Client Errors

The integration service handles various error scenarios:

#### Service Unavailable
```python
try:
    result = await integration_service.get_service_data("service-name", "/endpoint")
except ServiceClientError as e:
    print(f"Service call failed: {e}")
    # Handle service unavailable
```

#### Timeout Errors
```python
try:
    result = await integration_service.get_service_data("service-name", "/endpoint")
except ServiceTimeoutError as e:
    print(f"Service timeout: {e}")
    # Handle timeout
```

#### Connection Errors
```python
try:
    result = await integration_service.get_service_data("service-name", "/endpoint")
except ServiceUnavailableError as e:
    print(f"Service unavailable: {e}")
    # Handle connection error
```

### Health Check Responses

#### Healthy Service
```json
{
    "status": "healthy",
    "response_time": 0.5,
    "last_check": "2024-01-15T10:30:00Z",
    "critical": true
}
```

#### Unhealthy Service
```json
{
    "status": "unhealthy",
    "response_time": null,
    "last_check": "2024-01-15T10:30:00Z",
    "critical": true,
    "error": "Connection timeout"
}
```

## Performance Considerations

### Caching Strategy

The integration service implements multi-level caching:

1. **Service Response Cache**: Caches responses from external services
2. **Health Check Cache**: Caches health check results for 30 seconds
3. **Data Sync Cache**: Caches synchronization results

### Timeout Configuration

- **Critical Services**: 30-second timeout
- **AI Services**: 45-second timeout (longer processing time)
- **Standard Services**: 20-second timeout

### Retry Logic

- **Maximum Retries**: 3 attempts
- **Retry Delay**: Exponential backoff (1s, 2s, 4s)
- **Retry Conditions**: Network errors, timeouts, 5xx status codes

## Monitoring and Metrics

### Key Metrics

- **Service Health**: Overall health percentage
- **Response Times**: Average response time per service
- **Error Rates**: Error count per service
- **Cache Hit Rate**: Cache effectiveness
- **Sync Success Rate**: Data synchronization success

### Monitoring Endpoints

```http
GET /api/v1/integration/monitoring/metrics
```

Returns:
```json
{
    "timestamp": "2024-01-15T10:30:00Z",
    "metrics": {
        "total_services": 7,
        "healthy_services": 6,
        "unhealthy_services": 1,
        "health_percentage": 85.7,
        "average_response_time": 0.8,
        "total_errors": 3,
        "cache_size": 150
    },
    "service_details": {
        "recommendation-engine": {
            "status": "healthy",
            "response_time": 0.5,
            "error_count": 0,
            "last_check": "2024-01-15T10:30:00Z"
        }
    }
}
```

## Troubleshooting

### Common Issues

#### Service Not Responding
1. Check service health: `GET /api/v1/integration/services/{service_name}/status`
2. Verify service is running on correct port
3. Check network connectivity
4. Review service logs

#### Data Synchronization Failures
1. Validate data format against service requirements
2. Check service endpoint availability
3. Verify authentication if required
4. Review error logs for specific failure reasons

#### Performance Issues
1. Monitor response times via metrics endpoint
2. Check for service overload
3. Review timeout configurations
4. Consider caching strategies

### Debug Mode

Enable debug logging:

```python
import logging
logging.getLogger("src.services.caain_integration_service").setLevel(logging.DEBUG)
```

### Health Check Failures

If health checks fail:

1. **Check Service Status**: Verify all services are running
2. **Network Issues**: Test connectivity between services
3. **Configuration**: Verify service URLs and endpoints
4. **Dependencies**: Check if services have required dependencies

## Security Considerations

### Service Communication

- All service communication uses HTTP/HTTPS
- No sensitive data in URL parameters
- Request/response logging excludes sensitive information
- Service authentication can be added as needed

### Data Validation

- All incoming data is validated before processing
- Service responses are validated for expected format
- Error messages don't expose internal system details

## Future Enhancements

### Planned Features

1. **Service Discovery**: Automatic service discovery and registration
2. **Load Balancing**: Distribute requests across multiple service instances
3. **Circuit Breaker**: Automatic service isolation on failures
4. **Metrics Dashboard**: Real-time monitoring dashboard
5. **Authentication**: Service-to-service authentication
6. **Rate Limiting**: Prevent service overload

### Integration Points

- **Message Queues**: Asynchronous communication via Redis/RabbitMQ
- **Event Streaming**: Real-time data updates via Kafka
- **Service Mesh**: Advanced service communication patterns
- **API Gateway**: Centralized API management

## Support

For integration issues or questions:

1. **Documentation**: Check this guide and API documentation
2. **Logs**: Review service logs for error details
3. **Health Checks**: Use monitoring endpoints to diagnose issues
4. **Development Team**: Contact CAAIN Soil Hub development team

---

**Version**: 1.0.0  
**Last Updated**: January 2024  
**Maintained By**: CAAIN Soil Hub Development Team
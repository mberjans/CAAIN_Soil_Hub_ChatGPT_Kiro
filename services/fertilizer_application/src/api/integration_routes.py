"""
Integration API Routes for CAAIN Soil Hub Fertilizer Application Service

Provides endpoints for cross-service communication, health monitoring,
data synchronization, and system integration.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ..services.caain_integration_service import CAAINFertilizerIntegrationService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/integration", tags=["integration"])

# Dependency injection
async def get_integration_service() -> CAAINFertilizerIntegrationService:
    """Get CAAIN integration service instance."""
    return CAAINFertilizerIntegrationService()

# Request/Response Models
class ServiceHealthRequest(BaseModel):
    """Request model for service health check."""
    service_name: Optional[str] = Field(None, description="Specific service to check")

class DataSyncRequest(BaseModel):
    """Request model for data synchronization."""
    field_id: str = Field(..., description="Field identifier")
    user_id: str = Field(..., description="User identifier")
    force_sync: bool = Field(False, description="Force sync even if recently synced")

class RecommendationValidationRequest(BaseModel):
    """Request model for recommendation validation."""
    recommendation: Dict[str, Any] = Field(..., description="Recommendation data to validate")

class FertilizerDataRequest(BaseModel):
    """Request model for fertilizer data requests."""
    fertilizer_types: List[str] = Field(..., description="Types of fertilizers")
    region: Optional[str] = Field(None, description="Geographic region")
    user_id: Optional[str] = Field(None, description="User identifier")

# Health Management Endpoints
@router.get("/health")
async def integration_health_check(
    service: CAAINFertilizerIntegrationService = Depends(get_integration_service)
):
    """
    Check health status of CAAIN integration service and all connected services.
    
    Returns comprehensive health information for all integrated services.
    """
    try:
        health_report = await service.check_all_services_health()
        status_summary = service.get_service_status_summary()
        
        return {
            "service": "fertilizer-application-integration",
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "connected_services": health_report,
            "summary": status_summary
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health/{service_name}")
async def service_health_check(
    service_name: str,
    service: CAAINFertilizerIntegrationService = Depends(get_integration_service)
):
    """
    Check health status of a specific CAAIN service.
    
    Args:
        service_name: Name of the service to check
    """
    try:
        health_status = await service.check_service_health(service_name)
        return {
            "service": service_name,
            "timestamp": datetime.utcnow().isoformat(),
            **health_status
        }
    except Exception as e:
        logger.error(f"Health check failed for {service_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def integration_status(
    service: CAAINFertilizerIntegrationService = Depends(get_integration_service)
):
    """
    Get overall integration status and service summary.
    """
    try:
        status_summary = service.get_service_status_summary()
        return status_summary
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Data Integration Endpoints
@router.get("/soil-data")
async def get_soil_data(
    field_id: str = Query(..., description="Field identifier"),
    user_id: str = Query(..., description="User identifier"),
    service: CAAINFertilizerIntegrationService = Depends(get_integration_service)
):
    """
    Get soil data from data-integration service for fertilizer application planning.
    """
    try:
        soil_data = await service.get_soil_data(field_id, user_id)
        return {
            "field_id": field_id,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "soil_data": soil_data
        }
    except Exception as e:
        logger.error(f"Failed to get soil data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/weather-data")
async def get_weather_data(
    latitude: float = Query(..., description="Latitude coordinate"),
    longitude: float = Query(..., description="Longitude coordinate"),
    service: CAAINFertilizerIntegrationService = Depends(get_integration_service)
):
    """
    Get current weather data for fertilizer application timing decisions.
    """
    try:
        weather_data = await service.get_weather_data(latitude, longitude)
        return {
            "location": {"latitude": latitude, "longitude": longitude},
            "timestamp": datetime.utcnow().isoformat(),
            "weather_data": weather_data
        }
    except Exception as e:
        logger.error(f"Failed to get weather data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fertilizer-prices")
async def get_fertilizer_prices(
    request: FertilizerDataRequest,
    service: CAAINFertilizerIntegrationService = Depends(get_integration_service)
):
    """
    Get current fertilizer prices for cost analysis and optimization.
    """
    try:
        prices = await service.get_fertilizer_prices(
            request.fertilizer_types,
            request.region
        )
        return {
            "fertilizer_types": request.fertilizer_types,
            "region": request.region,
            "timestamp": datetime.utcnow().isoformat(),
            "prices": prices
        }
    except Exception as e:
        logger.error(f"Failed to get fertilizer prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/crop-recommendations")
async def get_crop_recommendations(
    location_data: Dict[str, Any] = Body(..., description="Location data"),
    soil_data: Dict[str, Any] = Body(..., description="Soil data"),
    service: CAAINFertilizerIntegrationService = Depends(get_integration_service)
):
    """
    Get crop recommendations from recommendation-engine service.
    """
    try:
        recommendations = await service.get_crop_recommendations(location_data, soil_data)
        return {
            "location": location_data,
            "soil_data": soil_data,
            "timestamp": datetime.utcnow().isoformat(),
            "recommendations": recommendations
        }
    except Exception as e:
        logger.error(f"Failed to get crop recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# AI Integration Endpoints
@router.post("/ai-explanation")
async def get_ai_explanation(
    recommendation_data: Dict[str, Any] = Body(..., description="Recommendation data"),
    user_context: Dict[str, Any] = Body(..., description="User context"),
    service: CAAINFertilizerIntegrationService = Depends(get_integration_service)
):
    """
    Get AI-powered explanation for fertilizer application recommendations.
    """
    try:
        explanation = await service.explain_fertilizer_recommendation(
            recommendation_data, user_context
        )
        return {
            "recommendation_id": recommendation_data.get("id"),
            "timestamp": datetime.utcnow().isoformat(),
            "explanation": explanation
        }
    except Exception as e:
        logger.error(f"Failed to get AI explanation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Data Synchronization Endpoints
@router.post("/sync-fertilizer-data")
async def sync_fertilizer_data(
    request: DataSyncRequest,
    service: CAAINFertilizerIntegrationService = Depends(get_integration_service)
):
    """
    Synchronize fertilizer application data across all CAAIN services.
    """
    try:
        sync_data = await service.sync_fertilizer_data(
            request.field_id, request.user_id
        )
        return {
            "field_id": request.field_id,
            "user_id": request.user_id,
            "sync_data": sync_data
        }
    except Exception as e:
        logger.error(f"Failed to sync fertilizer data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate-recommendation")
async def validate_recommendation(
    request: RecommendationValidationRequest,
    service: CAAINFertilizerIntegrationService = Depends(get_integration_service)
):
    """
    Validate fertilizer recommendation against multiple data sources.
    """
    try:
        validation_results = await service.validate_fertilizer_recommendation(
            request.recommendation
        )
        return validation_results
    except Exception as e:
        logger.error(f"Failed to validate recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Service Management Endpoints
@router.get("/services")
async def list_connected_services(
    service: CAAINFertilizerIntegrationService = Depends(get_integration_service)
):
    """
    List all connected CAAIN services and their configuration.
    """
    try:
        services_info = {}
        for service_name, config in service.integration_config.items():
            services_info[service_name] = {
                "base_url": config["base_url"],
                "timeout": config["timeout"],
                "retry_attempts": config["retry_attempts"],
                "critical": config.get("critical", False),
                "endpoints": list(config["endpoints"].keys()),
                "status": service.service_status.get(service_name, {}).get("status", "unknown")
            }
        
        return {
            "connected_services": services_info,
            "total_services": len(services_info),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to list services: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/services/{service_name}/test")
async def test_service_connection(
    service_name: str,
    service: CAAINFertilizerIntegrationService = Depends(get_integration_service)
):
    """
    Test connection to a specific CAAIN service.
    """
    try:
        health_status = await service.check_service_health(service_name)
        return {
            "service": service_name,
            "test_result": health_status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Service test failed for {service_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Monitoring and Analytics Endpoints
@router.get("/metrics")
async def get_integration_metrics(
    service: CAAINFertilizerIntegrationService = Depends(get_integration_service)
):
    """
    Get integration performance metrics and statistics.
    """
    try:
        metrics = {
            "service_status": service.service_status,
            "cache_stats": {
                "cached_items": len(service.data_sync_cache),
                "last_sync_times": len(service.last_sync_times)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        return metrics
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cache/clear")
async def clear_integration_cache(
    service: CAAINFertilizerIntegrationService = Depends(get_integration_service)
):
    """
    Clear integration data cache.
    """
    try:
        cache_size = len(service.data_sync_cache)
        service.data_sync_cache.clear()
        service.last_sync_times.clear()
        
        return {
            "message": "Integration cache cleared successfully",
            "cleared_items": cache_size,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Error Handling and Fallback Endpoints
@router.get("/fallback-data")
async def get_fallback_data(
    data_type: str = Query(..., description="Type of fallback data needed"),
    service: CAAINFertilizerIntegrationService = Depends(get_integration_service)
):
    """
    Get fallback data when primary services are unavailable.
    """
    try:
        # Implement fallback data logic based on data_type
        fallback_data = {
            "data_type": data_type,
            "source": "fallback",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {}  # Implement specific fallback data based on type
        }
        
        return fallback_data
    except Exception as e:
        logger.error(f"Failed to get fallback data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
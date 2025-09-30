"""
CAAIN Integration API Routes for Drought Management

API endpoints for integrating drought management with other CAAIN Soil Hub services.
"""

import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

from ..services.caain_integration_service import get_caain_integration_service, CAAINDroughtIntegrationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/integration", tags=["integration"])


# Request/Response Models
class ServiceHealthRequest(BaseModel):
    """Request model for service health check."""
    service_name: Optional[str] = Field(None, description="Specific service to check")


class ServiceHealthResponse(BaseModel):
    """Response model for service health status."""
    service_name: str
    status: str
    response_time: Optional[float]
    last_check: datetime
    critical: bool
    error_count: int
    details: Optional[Dict[str, Any]] = None


class DataSyncRequest(BaseModel):
    """Request model for data synchronization."""
    field_id: Optional[UUID] = Field(None, description="Field ID for soil data sync")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude for weather data sync")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude for weather data sync")
    sync_type: str = Field(..., description="Type of data to sync")


class DroughtRecommendationRequest(BaseModel):
    """Request model for drought recommendation integration."""
    field_data: Dict[str, Any] = Field(..., description="Field data for recommendations")
    location_data: Dict[str, Any] = Field(..., description="Location data")
    user_preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences")


class IntegrationStatusResponse(BaseModel):
    """Response model for integration status."""
    total_services: int
    healthy_services: int
    critical_services_healthy: bool
    last_sync: Optional[datetime]
    services_status: Dict[str, ServiceHealthResponse]


# Health Management Endpoints
@router.get("/health", response_model=Dict[str, Any])
async def integration_health(
    integration_service: CAAINDroughtIntegrationService = Depends(get_caain_integration_service)
):
    """
    Get health status of CAAIN integration service.
    
    Returns overall health status and service connectivity information.
    """
    try:
        all_status = await integration_service.get_all_services_status()
        
        healthy_count = sum(1 for status in all_status.values() if status["status"] == "healthy")
        total_count = len(all_status)
        critical_healthy = all(
            status["status"] == "healthy" 
            for status in all_status.values() 
            if status.get("critical", False)
        )
        
        return {
            "status": "healthy" if critical_healthy else "degraded",
            "total_services": total_count,
            "healthy_services": healthy_count,
            "critical_services_healthy": critical_healthy,
            "services": all_status,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error checking integration health: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Integration health check failed: {str(e)}")


@router.get("/services/health", response_model=Dict[str, ServiceHealthResponse])
async def all_services_health(
    integration_service: CAAINDroughtIntegrationService = Depends(get_caain_integration_service)
):
    """
    Get health status of all CAAIN services.
    
    Returns detailed health information for each service.
    """
    try:
        all_status = await integration_service.get_all_services_status()
        
        response = {}
        for service_name, status in all_status.items():
            response[service_name] = ServiceHealthResponse(
                service_name=service_name,
                status=status["status"],
                response_time=status.get("response_time"),
                last_check=status["last_check"],
                critical=status.get("critical", False),
                error_count=status.get("error_count", 0),
                details=status.get("details")
            )
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting all services health: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get services health: {str(e)}")


@router.get("/services/{service_name}/health", response_model=ServiceHealthResponse)
async def service_health(
    service_name: str,
    integration_service: CAAINDroughtIntegrationService = Depends(get_caain_integration_service)
):
    """
    Get health status of a specific CAAIN service.
    
    Returns detailed health information for the specified service.
    """
    try:
        status = await integration_service.get_service_status(service_name)
        
        return ServiceHealthResponse(
            service_name=service_name,
            status=status["status"],
            response_time=status.get("response_time"),
            last_check=status["last_check"],
            critical=status.get("critical", False),
            error_count=status.get("error_count", 0),
            details=status.get("details")
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting service health for {service_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get service health: {str(e)}")


# Data Integration Endpoints
@router.post("/data/sync", response_model=Dict[str, Any])
async def sync_data(
    request: DataSyncRequest,
    background_tasks: BackgroundTasks,
    integration_service: CAAINDroughtIntegrationService = Depends(get_caain_integration_service)
):
    """
    Synchronize data with other CAAIN services.
    
    Supports syncing soil data, weather data, and other service-specific data.
    """
    try:
        if request.sync_type == "soil_data" and request.field_id:
            data = await integration_service.sync_soil_data(request.field_id)
            return {
                "sync_type": "soil_data",
                "field_id": str(request.field_id),
                "data": data,
                "timestamp": datetime.utcnow()
            }
        
        elif request.sync_type == "weather_data" and request.latitude and request.longitude:
            data = await integration_service.sync_weather_data(request.latitude, request.longitude)
            return {
                "sync_type": "weather_data",
                "latitude": request.latitude,
                "longitude": request.longitude,
                "data": data,
                "timestamp": datetime.utcnow()
            }
        
        else:
            raise HTTPException(
                status_code=400, 
                detail="Invalid sync request. Provide field_id for soil_data or latitude/longitude for weather_data"
            )
        
    except Exception as e:
        logger.error(f"Error syncing data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Data sync failed: {str(e)}")


@router.get("/data/soil/{field_id}", response_model=Dict[str, Any])
async def get_soil_data(
    field_id: UUID,
    integration_service: CAAINDroughtIntegrationService = Depends(get_caain_integration_service)
):
    """
    Get soil data for a specific field from data-integration service.
    
    Returns comprehensive soil data including moisture, texture, and fertility.
    """
    try:
        data = await integration_service.sync_soil_data(field_id)
        return {
            "field_id": str(field_id),
            "soil_data": data,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error getting soil data for field {field_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get soil data: {str(e)}")


@router.get("/data/weather", response_model=Dict[str, Any])
async def get_weather_data(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude"),
    integration_service: CAAINDroughtIntegrationService = Depends(get_caain_integration_service)
):
    """
    Get weather data for specific coordinates from data-integration service.
    
    Returns current weather conditions and agricultural metrics.
    """
    try:
        data = await integration_service.sync_weather_data(latitude, longitude)
        return {
            "latitude": latitude,
            "longitude": longitude,
            "weather_data": data,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error getting weather data for {latitude}, {longitude}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get weather data: {str(e)}")


# Crop Integration Endpoints
@router.post("/crops/drought-resilient", response_model=Dict[str, Any])
async def get_drought_resilient_crops(
    request: DroughtRecommendationRequest,
    integration_service: CAAINDroughtIntegrationService = Depends(get_caain_integration_service)
):
    """
    Get drought-resilient crop recommendations from crop-taxonomy service.
    
    Returns crop varieties suitable for drought conditions.
    """
    try:
        crops = await integration_service.get_drought_resilient_crops(request.location_data)
        return {
            "location_data": request.location_data,
            "drought_resilient_crops": crops,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error getting drought-resilient crops: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get drought-resilient crops: {str(e)}")


@router.post("/cover-crops/recommendations", response_model=Dict[str, Any])
async def get_cover_crop_recommendations(
    request: DroughtRecommendationRequest,
    integration_service: CAAINDroughtIntegrationService = Depends(get_caain_integration_service)
):
    """
    Get cover crop recommendations for moisture conservation from cover-crop-selection service.
    
    Returns cover crops that help conserve soil moisture.
    """
    try:
        recommendations = await integration_service.get_cover_crop_recommendations(request.field_data)
        return {
            "field_data": request.field_data,
            "cover_crop_recommendations": recommendations,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error getting cover crop recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get cover crop recommendations: {str(e)}")


# AI Integration Endpoints
@router.post("/ai/explain", response_model=Dict[str, Any])
async def explain_drought_recommendation(
    request: DroughtRecommendationRequest,
    integration_service: CAAINDroughtIntegrationService = Depends(get_caain_integration_service)
):
    """
    Get AI explanation for drought management recommendations from ai-agent service.
    
    Returns detailed explanations of drought management practices and their benefits.
    """
    try:
        explanation = await integration_service.explain_drought_recommendation(request.field_data)
        return {
            "field_data": request.field_data,
            "ai_explanation": explanation,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error getting AI explanation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get AI explanation: {str(e)}")


# Question Routing Endpoints
@router.post("/questions/route", response_model=Dict[str, Any])
async def route_drought_question(
    request: DroughtRecommendationRequest,
    integration_service: CAAINDroughtIntegrationService = Depends(get_caain_integration_service)
):
    """
    Route drought-related questions through question-router service.
    
    Routes questions to appropriate services for comprehensive answers.
    """
    try:
        response = await integration_service.route_drought_question(request.field_data)
        return {
            "question_data": request.field_data,
            "routing_response": response,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error routing drought question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to route question: {str(e)}")


# Service Management Endpoints
@router.get("/status", response_model=IntegrationStatusResponse)
async def get_integration_status(
    integration_service: CAAINDroughtIntegrationService = Depends(get_caain_integration_service)
):
    """
    Get comprehensive integration status.
    
    Returns overall integration health, service status, and sync information.
    """
    try:
        all_status = await integration_service.get_all_services_status()
        
        healthy_count = sum(1 for status in all_status.values() if status["status"] == "healthy")
        total_count = len(all_status)
        critical_healthy = all(
            status["status"] == "healthy" 
            for status in all_status.values() 
            if status.get("critical", False)
        )
        
        # Convert to response format
        services_status = {}
        for service_name, status in all_status.items():
            services_status[service_name] = ServiceHealthResponse(
                service_name=service_name,
                status=status["status"],
                response_time=status.get("response_time"),
                last_check=status["last_check"],
                critical=status.get("critical", False),
                error_count=status.get("error_count", 0),
                details=status.get("details")
            )
        
        return IntegrationStatusResponse(
            total_services=total_count,
            healthy_services=healthy_count,
            critical_services_healthy=critical_healthy,
            last_sync=datetime.utcnow(),
            services_status=services_status
        )
        
    except Exception as e:
        logger.error(f"Error getting integration status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get integration status: {str(e)}")


@router.post("/services/refresh", response_model=Dict[str, Any])
async def refresh_service_connections(
    background_tasks: BackgroundTasks,
    integration_service: CAAINDroughtIntegrationService = Depends(get_caain_integration_service)
):
    """
    Refresh connections to all CAAIN services.
    
    Performs fresh health checks and updates service status.
    """
    try:
        # Perform health checks in background
        background_tasks.add_task(integration_service.check_all_services_health)
        
        return {
            "message": "Service refresh initiated",
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error refreshing service connections: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to refresh connections: {str(e)}")
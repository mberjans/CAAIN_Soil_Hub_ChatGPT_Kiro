"""
Integration API Routes

API endpoints for CAAIN Soil Hub service integration, providing
cross-service communication, data synchronization, and system monitoring.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from ..services.caain_integration_service import (
    CAAINIntegrationService, 
    get_integration_service,
    cleanup_integration_service
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/integration", tags=["integration"])


@router.get("/health")
async def integration_health_check():
    """
    Health check for integration service.
    
    Returns:
        Integration service health status
    """
    try:
        integration_service = get_integration_service()
        status = await integration_service.get_integration_status()
        
        return {
            "service": "crop-taxonomy-integration",
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "integration_status": status
        }
    except Exception as e:
        logger.error(f"Integration health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/services/status")
async def get_all_services_status():
    """
    Get status of all integrated CAAIN services.
    
    Returns:
        Comprehensive status of all services
    """
    try:
        integration_service = get_integration_service()
        status = await integration_service.get_integration_status()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "integration_summary": status,
            "services": status["service_details"]
        }
    except Exception as e:
        logger.error(f"Failed to get services status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/services/health-check")
async def perform_health_checks(background_tasks: BackgroundTasks):
    """
    Perform health checks on all integrated services.
    
    Returns:
        Health check results for all services
    """
    try:
        integration_service = get_integration_service()
        
        # Perform health checks
        health_results = await integration_service.health_check_all_services()
        
        # Schedule background cleanup if needed
        background_tasks.add_task(_cleanup_if_needed, health_results)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "health_checks": health_results,
            "summary": {
                "total_services": len(health_results),
                "healthy_services": sum(1 for s in health_results.values() 
                                      if s.get("status") == "healthy"),
                "unhealthy_services": sum(1 for s in health_results.values() 
                                         if s.get("status") == "unhealthy"),
                "error_services": sum(1 for s in health_results.values() 
                                     if s.get("status") == "error")
            }
        }
    except Exception as e:
        logger.error(f"Health checks failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/data/sync-crop-data")
async def sync_crop_data_with_services(crop_data: Dict[str, Any]):
    """
    Synchronize crop variety data with other CAAIN services.
    
    Args:
        crop_data: Crop variety data to synchronize
        
    Returns:
        Synchronization results
    """
    try:
        integration_service = get_integration_service()
        
        # Sync with recommendation engine
        rec_result = await integration_service.sync_crop_data_with_recommendation_engine(crop_data)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "sync_results": {
                "recommendation_engine": rec_result
            },
            "status": "completed"
        }
    except Exception as e:
        logger.error(f"Crop data sync failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/data/validate-consistency")
async def validate_data_consistency(
    data_type: str,
    data: Dict[str, Any]
):
    """
    Validate data consistency across services.
    
    Args:
        data_type: Type of data to validate (crop_variety, soil_data, etc.)
        data: Data to validate
        
    Returns:
        Validation results
    """
    try:
        integration_service = get_integration_service()
        
        validation_result = await integration_service.validate_data_consistency(data_type, data)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "validation_result": validation_result
        }
    except Exception as e:
        logger.error(f"Data consistency validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data/soil/{latitude}/{longitude}")
async def get_soil_data_for_location(latitude: float, longitude: float):
    """
    Get soil data for a specific location from data-integration service.
    
    Args:
        latitude: Location latitude
        longitude: Location longitude
        
    Returns:
        Soil characteristics data
    """
    try:
        integration_service = get_integration_service()
        
        soil_data = await integration_service.get_soil_data_for_location(latitude, longitude)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "location": {"latitude": latitude, "longitude": longitude},
            "soil_data": soil_data
        }
    except Exception as e:
        logger.error(f"Failed to get soil data for {latitude}, {longitude}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data/climate/{latitude}/{longitude}")
async def get_climate_data_for_location(latitude: float, longitude: float):
    """
    Get climate zone data for a specific location.
    
    Args:
        latitude: Location latitude
        longitude: Location longitude
        
    Returns:
        Climate zone data
    """
    try:
        integration_service = get_integration_service()
        
        climate_data = await integration_service.get_climate_data_for_location(latitude, longitude)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "location": {"latitude": latitude, "longitude": longitude},
            "climate_data": climate_data
        }
    except Exception as e:
        logger.error(f"Failed to get climate data for {latitude}, {longitude}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai/explain-recommendation")
async def get_ai_explanation_for_recommendation(recommendation_data: Dict[str, Any]):
    """
    Get AI-powered explanation for a variety recommendation.
    
    Args:
        recommendation_data: Recommendation data to explain
        
    Returns:
        AI explanation
    """
    try:
        integration_service = get_integration_service()
        
        explanation = await integration_service.get_ai_explanation_for_recommendation(recommendation_data)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "explanation": explanation
        }
    except Exception as e:
        logger.error(f"Failed to get AI explanation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/services/{service_name}/status")
async def get_service_status(service_name: str):
    """
    Get detailed status for a specific service.
    
    Args:
        service_name: Name of the service
        
    Returns:
        Detailed service status
    """
    try:
        integration_service = get_integration_service()
        
        if service_name not in integration_service.service_clients:
            raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
        
        # Get health check for this specific service
        health_results = await integration_service.health_check_all_services()
        service_status = health_results.get(service_name, {})
        
        return {
            "timestamp": datetime.now().isoformat(),
            "service_name": service_name,
            "status": service_status,
            "configuration": integration_service.integration_config.get(service_name, {})
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get status for service {service_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/services/{service_name}/call")
async def call_service_endpoint(
    service_name: str,
    endpoint: str,
    method: str = "GET",
    data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None
):
    """
    Make a direct call to a service endpoint.
    
    Args:
        service_name: Name of the target service
        endpoint: API endpoint to call
        method: HTTP method (GET, POST, PUT, DELETE)
        data: Request body data
        params: Query parameters
        
    Returns:
        Service response
    """
    try:
        integration_service = get_integration_service()
        
        if service_name not in integration_service.service_clients:
            raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
        
        # Validate method
        if method.upper() not in ["GET", "POST", "PUT", "DELETE"]:
            raise HTTPException(status_code=400, detail="Invalid HTTP method")
        
        # Make the service call
        response = await integration_service.get_service_data(
            service_name=service_name,
            endpoint=endpoint,
            params=params if method.upper() == "GET" else None,
            data=data if method.upper() in ["POST", "PUT"] else None
        )
        
        return {
            "timestamp": datetime.now().isoformat(),
            "service": service_name,
            "endpoint": endpoint,
            "method": method.upper(),
            "response": response
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Service call failed for {service_name}/{endpoint}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monitoring/metrics")
async def get_integration_metrics():
    """
    Get integration service metrics and performance data.
    
    Returns:
        Integration metrics
    """
    try:
        integration_service = get_integration_service()
        
        # Calculate metrics from service status
        total_services = len(integration_service.service_clients)
        healthy_services = sum(1 for status in integration_service.service_status.values() 
                             if status.get("status") == "healthy")
        
        # Calculate average response times
        response_times = [status.get("response_time") for status in integration_service.service_status.values() 
                         if status.get("response_time") is not None]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Count errors
        total_errors = sum(status.get("error_count", 0) for status in integration_service.service_status.values())
        
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "total_services": total_services,
                "healthy_services": healthy_services,
                "unhealthy_services": total_services - healthy_services,
                "health_percentage": (healthy_services / total_services * 100) if total_services > 0 else 0,
                "average_response_time": avg_response_time,
                "total_errors": total_errors,
                "cache_size": len(integration_service.data_sync_cache)
            },
            "service_details": {
                name: {
                    "status": status.get("status"),
                    "response_time": status.get("response_time"),
                    "error_count": status.get("error_count"),
                    "last_check": status.get("last_check").isoformat() if status.get("last_check") else None
                }
                for name, status in integration_service.service_status.items()
            }
        }
    except Exception as e:
        logger.error(f"Failed to get integration metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _cleanup_if_needed(health_results: Dict[str, Any]):
    """Background task to cleanup resources if services are unhealthy."""
    try:
        # Check if any critical services are down
        critical_services_down = any(
            result.get("status") != "healthy" and result.get("critical", False)
            for result in health_results.values()
        )
        
        if critical_services_down:
            logger.warning("Critical services are down, performing cleanup")
            # Add any cleanup logic here if needed
    except Exception as e:
        logger.error(f"Cleanup task failed: {e}")


# Cleanup on shutdown
@router.on_event("shutdown")
async def shutdown_integration():
    """Cleanup integration service on shutdown."""
    try:
        await cleanup_integration_service()
        logger.info("Integration service cleaned up on shutdown")
    except Exception as e:
        logger.error(f"Error during integration service cleanup: {e}")
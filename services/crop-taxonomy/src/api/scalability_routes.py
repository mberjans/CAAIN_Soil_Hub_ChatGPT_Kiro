"""
Scalability Infrastructure API Routes

This module provides REST API endpoints for managing and monitoring
the scalability infrastructure components.

TICKET-005_crop-variety-recommendations-14.2: Add comprehensive scalability improvements and infrastructure
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ..infrastructure.scalability_infrastructure import (
    get_scalability_infrastructure,
    ScalabilityInfrastructure,
    submit_variety_recommendation_job,
    submit_batch_variety_search_job,
    cache_variety_data,
    get_cached_variety_data,
    invalidate_variety_cache,
    get_system_status,
    create_system_backup,
    generate_capacity_report
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/scalability", tags=["scalability"])


# Pydantic models for API requests/responses
class ServiceInstanceRequest(BaseModel):
    instance_id: str = Field(..., description="Unique instance identifier")
    host: str = Field(..., description="Instance host address")
    port: int = Field(..., ge=1, le=65535, description="Instance port number")
    health_endpoint: str = Field(default="/health", description="Health check endpoint")
    weight: int = Field(default=1, ge=1, le=10, description="Load balancer weight")


class BackgroundJobRequest(BaseModel):
    job_type: str = Field(..., description="Type of job to submit")
    payload: Dict[str, Any] = Field(..., description="Job payload data")
    priority: str = Field(default="normal", description="Job priority (low, normal, high, critical)")


class CacheRequest(BaseModel):
    key: str = Field(..., description="Cache key")
    value: Any = Field(..., description="Cache value")
    ttl: int = Field(default=3600, ge=1, description="Time to live in seconds")
    data_type: str = Field(default="general", description="Data type for partitioning")
    tags: List[str] = Field(default=[], description="Cache tags for invalidation")


class CapacityPlanningRequest(BaseModel):
    planning_horizon_months: int = Field(default=6, ge=1, le=24, description="Planning horizon in months")
    current_users: int = Field(default=1000, ge=1, description="Current number of users")


# Dependency injection
async def get_infrastructure() -> ScalabilityInfrastructure:
    """Get scalability infrastructure instance."""
    return await get_scalability_infrastructure()


# System Status and Health Endpoints
@router.get("/status", response_model=Dict[str, Any])
async def get_scalability_status(infrastructure: ScalabilityInfrastructure = Depends(get_infrastructure)):
    """
    Get comprehensive scalability infrastructure status.
    
    Returns status of all scalability components including:
    - Load balancer and service instances
    - Distributed cache performance
    - Async processor queue status
    - Capacity planning metrics
    - Fault tolerance health
    """
    try:
        status = await infrastructure.get_scalability_metrics()
        return status
    except Exception as e:
        logger.error(f"Failed to get scalability status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=Dict[str, Any])
async def get_system_health(infrastructure: ScalabilityInfrastructure = Depends(get_infrastructure)):
    """
    Get system health status.
    
    Returns detailed health information including:
    - Service health checks
    - Circuit breaker states
    - Recent failures
    - Overall system health
    """
    try:
        health = await infrastructure.get_system_health()
        return health
    except Exception as e:
        logger.error(f"Failed to get system health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Load Balancing Endpoints
@router.post("/instances", response_model=Dict[str, str])
async def add_service_instance(
    request: ServiceInstanceRequest,
    infrastructure: ScalabilityInfrastructure = Depends(get_infrastructure)
):
    """
    Add a service instance to the load balancer.
    
    This endpoint allows adding new service instances to the load balancer
    for horizontal scaling and high availability.
    """
    try:
        await infrastructure.add_service_instance(
            instance_id=request.instance_id,
            host=request.host,
            port=request.port,
            health_endpoint=request.health_endpoint,
            weight=request.weight
        )
        
        return {
            "status": "success",
            "message": f"Service instance {request.instance_id} added successfully"
        }
    except Exception as e:
        logger.error(f"Failed to add service instance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/instances/{instance_id}", response_model=Dict[str, str])
async def remove_service_instance(
    instance_id: str,
    infrastructure: ScalabilityInfrastructure = Depends(get_infrastructure)
):
    """
    Remove a service instance from the load balancer.
    
    This endpoint allows removing service instances from the load balancer
    for maintenance or scaling down operations.
    """
    try:
        if infrastructure.scalability_manager:
            await infrastructure.scalability_manager.load_balancer.remove_instance(instance_id)
            return {
                "status": "success",
                "message": f"Service instance {instance_id} removed successfully"
            }
        else:
            raise HTTPException(status_code=503, detail="Scalability manager not available")
    except Exception as e:
        logger.error(f"Failed to remove service instance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Background Job Management Endpoints
@router.post("/jobs", response_model=Dict[str, str])
async def submit_background_job(
    request: BackgroundJobRequest,
    infrastructure: ScalabilityInfrastructure = Depends(get_infrastructure)
):
    """
    Submit a job for background processing.
    
    This endpoint allows submitting jobs for asynchronous processing,
    which helps with scalability by offloading heavy operations.
    """
    try:
        job_id = await infrastructure.submit_background_job(
            job_type=request.job_type,
            payload=request.payload,
            priority=request.priority
        )
        
        return {
            "status": "success",
            "job_id": job_id,
            "message": "Job submitted successfully"
        }
    except Exception as e:
        logger.error(f"Failed to submit background job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/{job_id}", response_model=Dict[str, Any])
async def get_job_status(
    job_id: str,
    infrastructure: ScalabilityInfrastructure = Depends(get_infrastructure)
):
    """
    Get the status of a background job.
    
    Returns detailed information about a specific job including:
    - Current status
    - Progress percentage
    - Start/completion times
    - Error messages if failed
    """
    try:
        job_status = await infrastructure.get_job_status(job_id)
        if job_status:
            return job_status
        else:
            raise HTTPException(status_code=404, detail="Job not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/jobs/{job_id}", response_model=Dict[str, str])
async def cancel_job(
    job_id: str,
    infrastructure: ScalabilityInfrastructure = Depends(get_infrastructure)
):
    """
    Cancel a pending background job.
    
    This endpoint allows cancelling jobs that are still in the queue
    and haven't started processing yet.
    """
    try:
        if infrastructure.async_processor:
            success = await infrastructure.async_processor.cancel_job(job_id)
            if success:
                return {
                    "status": "success",
                    "message": f"Job {job_id} cancelled successfully"
                }
            else:
                raise HTTPException(status_code=404, detail="Job not found or already processing")
        else:
            raise HTTPException(status_code=503, detail="Async processor not available")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Distributed Cache Endpoints
@router.post("/cache", response_model=Dict[str, str])
async def set_cache_value(
    request: CacheRequest,
    infrastructure: ScalabilityInfrastructure = Depends(get_infrastructure)
):
    """
    Set a value in the distributed cache.
    
    This endpoint allows storing data in the distributed cache system
    for improved performance and scalability.
    """
    try:
        await infrastructure.cache_set(
            key=request.key,
            value=request.value,
            ttl=request.ttl,
            data_type=request.data_type,
            tags=request.tags
        )
        
        return {
            "status": "success",
            "message": f"Value cached successfully with key: {request.key}"
        }
    except Exception as e:
        logger.error(f"Failed to set cache value: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cache/{key}", response_model=Dict[str, Any])
async def get_cache_value(
    key: str,
    data_type: str = Query(default="general", description="Data type for cache lookup"),
    infrastructure: ScalabilityInfrastructure = Depends(get_infrastructure)
):
    """
    Get a value from the distributed cache.
    
    Returns cached data if available, or null if not found or expired.
    """
    try:
        value = await infrastructure.cache_get(key, data_type)
        return {
            "key": key,
            "value": value,
            "found": value is not None
        }
    except Exception as e:
        logger.error(f"Failed to get cache value: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cache/{key}", response_model=Dict[str, str])
async def delete_cache_value(
    key: str,
    data_type: str = Query(default="general", description="Data type for cache lookup"),
    infrastructure: ScalabilityInfrastructure = Depends(get_infrastructure)
):
    """
    Delete a value from the distributed cache.
    
    Removes the specified key from all cache levels.
    """
    try:
        if infrastructure.distributed_cache:
            await infrastructure.distributed_cache.delete(key, data_type)
            return {
                "status": "success",
                "message": f"Cache key {key} deleted successfully"
            }
        else:
            raise HTTPException(status_code=503, detail="Distributed cache not available")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete cache value: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache/invalidate", response_model=Dict[str, str])
async def invalidate_cache_by_tags(
    tags: List[str],
    infrastructure: ScalabilityInfrastructure = Depends(get_infrastructure)
):
    """
    Invalidate cache entries by tags.
    
    This endpoint allows bulk invalidation of cache entries
    that match any of the specified tags.
    """
    try:
        await infrastructure.cache_invalidate(tags)
        return {
            "status": "success",
            "message": f"Cache invalidated for tags: {', '.join(tags)}"
        }
    except Exception as e:
        logger.error(f"Failed to invalidate cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Capacity Planning Endpoints
@router.post("/capacity-planning", response_model=Dict[str, Any])
async def generate_capacity_plan(
    request: CapacityPlanningRequest,
    background_tasks: BackgroundTasks,
    infrastructure: ScalabilityInfrastructure = Depends(get_infrastructure)
):
    """
    Generate a comprehensive capacity planning report.
    
    This endpoint analyzes current system usage and generates recommendations
    for scaling resources based on projected growth.
    """
    try:
        # Run capacity planning in background for large reports
        if request.planning_horizon_months > 12:
            background_tasks.add_task(
                infrastructure.generate_capacity_plan,
                request.planning_horizon_months,
                request.current_users
            )
            return {
                "status": "processing",
                "message": "Capacity planning report generation started in background"
            }
        else:
            report = await infrastructure.generate_capacity_plan(
                request.planning_horizon_months,
                request.current_users
            )
            return report
    except Exception as e:
        logger.error(f"Failed to generate capacity plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/capacity-planning/recommendations", response_model=Dict[str, Any])
async def get_capacity_recommendations(
    infrastructure: ScalabilityInfrastructure = Depends(get_infrastructure)
):
    """
    Get current capacity recommendations.
    
    Returns the latest capacity planning recommendations
    without generating a new report.
    """
    try:
        # This would typically fetch cached recommendations
        # For now, return a placeholder
        return {
            "status": "success",
            "recommendations": [],
            "message": "Capacity recommendations endpoint not yet implemented"
        }
    except Exception as e:
        logger.error(f"Failed to get capacity recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Backup and Recovery Endpoints
@router.post("/backup", response_model=Dict[str, str])
async def create_backup(
    backup_type: str = Query(default="redis_data", description="Type of backup to create"),
    infrastructure: ScalabilityInfrastructure = Depends(get_infrastructure)
):
    """
    Create a system backup.
    
    This endpoint creates a backup of critical system data
    for disaster recovery purposes.
    """
    try:
        backup_id = await infrastructure.create_backup(backup_type)
        return {
            "status": "success",
            "backup_id": backup_id,
            "message": f"Backup created successfully: {backup_id}"
        }
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Convenience Endpoints for Variety Recommendations
@router.post("/variety-recommendations", response_model=Dict[str, str])
async def submit_variety_recommendation_job_endpoint(
    crop_id: str = Query(..., description="Crop ID for recommendations"),
    latitude: float = Query(..., ge=-90, le=90, description="Location latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Location longitude"),
    soil_data: Dict[str, Any] = Query(default={}, description="Soil data parameters"),
    preferences: Dict[str, Any] = Query(default={}, description="User preferences")
):
    """
    Submit a variety recommendation job for background processing.
    
    This endpoint submits variety recommendation requests for asynchronous
    processing, improving system scalability and responsiveness.
    """
    try:
        location = {"latitude": latitude, "longitude": longitude}
        job_id = await submit_variety_recommendation_job(
            crop_id=crop_id,
            location=location,
            soil_data=soil_data,
            preferences=preferences
        )
        
        return {
            "status": "success",
            "job_id": job_id,
            "message": "Variety recommendation job submitted successfully"
        }
    except Exception as e:
        logger.error(f"Failed to submit variety recommendation job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-variety-search", response_model=Dict[str, str])
async def submit_batch_variety_search_job_endpoint(
    queries: List[str] = Query(..., description="List of search queries"),
    filters: Dict[str, Any] = Query(default={}, description="Search filters"),
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum results per query")
):
    """
    Submit a batch variety search job for background processing.
    
    This endpoint allows processing multiple variety search queries
    in parallel for improved efficiency.
    """
    try:
        job_id = await submit_batch_variety_search_job(
            queries=queries,
            filters=filters,
            limit=limit
        )
        
        return {
            "status": "success",
            "job_id": job_id,
            "message": "Batch variety search job submitted successfully"
        }
    except Exception as e:
        logger.error(f"Failed to submit batch variety search job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache/variety-data", response_model=Dict[str, str])
async def cache_variety_data_endpoint(
    variety_id: str = Query(..., description="Variety ID to cache"),
    variety_data: Dict[str, Any] = Query(..., description="Variety data to cache"),
    ttl: int = Query(default=3600, ge=1, description="Cache TTL in seconds")
):
    """
    Cache variety data in the distributed cache.
    
    This endpoint stores variety data in the distributed cache
    for improved performance and reduced database load.
    """
    try:
        await cache_variety_data(
            variety_id=variety_id,
            variety_data=variety_data,
            ttl=ttl
        )
        
        return {
            "status": "success",
            "message": f"Variety data cached successfully for variety: {variety_id}"
        }
    except Exception as e:
        logger.error(f"Failed to cache variety data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cache/variety-data/{variety_id}", response_model=Dict[str, Any])
async def get_cached_variety_data_endpoint(
    variety_id: str
):
    """
    Get cached variety data.
    
    Returns cached variety data if available, or null if not found.
    """
    try:
        variety_data = await get_cached_variety_data(variety_id)
        return {
            "variety_id": variety_id,
            "data": variety_data,
            "found": variety_data is not None
        }
    except Exception as e:
        logger.error(f"Failed to get cached variety data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache/variety-data/invalidate", response_model=Dict[str, str])
async def invalidate_variety_cache_endpoint():
    """
    Invalidate all variety-related cache entries.
    
    This endpoint clears all variety and crop data from the cache,
    useful when data has been updated.
    """
    try:
        await invalidate_variety_cache()
        return {
            "status": "success",
            "message": "Variety cache invalidated successfully"
        }
    except Exception as e:
        logger.error(f"Failed to invalidate variety cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# System Management Endpoints
@router.get("/metrics", response_model=Dict[str, Any])
async def get_scalability_metrics(
    infrastructure: ScalabilityInfrastructure = Depends(get_infrastructure)
):
    """
    Get detailed scalability metrics.
    
    Returns comprehensive metrics from all scalability components
    for monitoring and analysis purposes.
    """
    try:
        metrics = await infrastructure.get_scalability_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Failed to get scalability metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/shutdown", response_model=Dict[str, str])
async def shutdown_scalability_infrastructure(
    infrastructure: ScalabilityInfrastructure = Depends(get_infrastructure)
):
    """
    Shutdown the scalability infrastructure.
    
    This endpoint gracefully shuts down all scalability components.
    Use with caution in production environments.
    """
    try:
        await infrastructure.shutdown()
        return {
            "status": "success",
            "message": "Scalability infrastructure shutdown complete"
        }
    except Exception as e:
        logger.error(f"Failed to shutdown scalability infrastructure: {e}")
        raise HTTPException(status_code=500, detail=str(e))
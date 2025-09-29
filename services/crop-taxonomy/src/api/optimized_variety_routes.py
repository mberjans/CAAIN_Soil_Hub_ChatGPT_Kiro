"""
Optimized Variety Recommendation API Routes

This module provides optimized API endpoints for variety recommendations with:
- Response compression and pagination
- Performance monitoring and metrics
- Caching integration
- Error handling and logging

TICKET-005_crop-variety-recommendations-14.1: Implement comprehensive variety recommendation performance optimization
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Depends, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Import optimized services
from ..services.optimized_variety_recommendation_service import (
    OptimizedVarietyRecommendationService,
    get_optimized_variety_service
)
from ..services.performance_optimization_service import OptimizationConfig
from ..services.performance_monitor import performance_monitor

# Import models
try:
    from ..models.crop_variety_models import (
        VarietyRecommendation,
        VarietyComparisonRequest,
        VarietyComparisonResponse
    )
    from ..models.crop_taxonomy_models import ComprehensiveCropData
except ImportError:
    from models.crop_variety_models import (
        VarietyRecommendation,
        VarietyComparisonRequest,
        VarietyComparisonResponse
    )
    from models.crop_taxonomy_models import ComprehensiveCropData

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/optimized", tags=["optimized-variety-recommendations"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class OptimizedRecommendationRequest(BaseModel):
    """Request model for optimized variety recommendations."""
    crop_id: UUID = Field(..., description="ID of the crop to get recommendations for")
    regional_context: Dict[str, Any] = Field(..., description="Regional growing conditions and constraints")
    farmer_preferences: Optional[Dict[str, Any]] = Field(None, description="Farmer-specific preferences and priorities")
    limit: int = Field(20, ge=1, le=100, description="Maximum number of recommendations to return")


class OptimizedSearchRequest(BaseModel):
    """Request model for optimized variety search."""
    search_text: Optional[str] = Field(None, description="Text to search in variety names and companies")
    crop_id: Optional[UUID] = Field(None, description="Optional crop ID to filter by")
    traits: Optional[List[str]] = Field(None, description="Optional list of traits to filter by")
    limit: int = Field(20, ge=1, le=100, description="Maximum number of results to return")


class OptimizedResponse(BaseModel):
    """Base response model for optimized endpoints."""
    success: bool = Field(True, description="Whether the request was successful")
    execution_time_ms: float = Field(..., description="Request execution time in milliseconds")
    cache_hit: bool = Field(False, description="Whether the result was served from cache")
    performance_target_met: bool = Field(..., description="Whether performance targets were met")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class OptimizedRecommendationResponse(OptimizedResponse):
    """Response model for optimized variety recommendations."""
    recommendations: List[VarietyRecommendation] = Field(..., description="Ranked list of variety recommendations")
    total_count: int = Field(..., description="Total number of recommendations returned")


class OptimizedSearchResponse(OptimizedResponse):
    """Response model for optimized variety search."""
    varieties: List[Dict[str, Any]] = Field(..., description="List of matching varieties")
    total_count: int = Field(..., description="Total number of varieties found")
    search_params: Dict[str, Any] = Field(..., description="Search parameters used")


class OptimizedDetailsResponse(OptimizedResponse):
    """Response model for optimized variety details."""
    variety_details: Dict[str, Any] = Field(..., description="Detailed variety information")


class PerformanceMetricsResponse(BaseModel):
    """Response model for performance metrics."""
    service_uptime_seconds: float = Field(..., description="Service uptime in seconds")
    operation_counts: Dict[str, int] = Field(..., description="Count of operations performed")
    performance_targets: Dict[str, int] = Field(..., description="Performance targets in milliseconds")
    optimization_metrics: Dict[str, Any] = Field(..., description="Detailed optimization metrics")


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

async def get_optimized_service() -> OptimizedVarietyRecommendationService:
    """Dependency to get the optimized variety recommendation service."""
    return get_optimized_variety_service()


async def get_optimization_config() -> OptimizationConfig:
    """Dependency to get the optimization configuration."""
    return OptimizationConfig()


# ============================================================================
# OPTIMIZED VARIETY RECOMMENDATION ENDPOINTS
# ============================================================================

@router.post("/recommendations", response_model=OptimizedRecommendationResponse)
async def get_optimized_variety_recommendations(
    request: OptimizedRecommendationRequest,
    service: OptimizedVarietyRecommendationService = Depends(get_optimized_service),
    response: Response = None
):
    """
    Get optimized variety recommendations with performance target <2s.
    
    This endpoint provides ranked variety recommendations with comprehensive
    performance optimization including caching, database query optimization,
    and response compression.
    
    Performance Targets:
    - Response time: <2 seconds
    - Cache hit rate: >60%
    - Database queries: Optimized with indexes
    """
    start_time = time.time()
    
    try:
        # Create crop data object
        crop_data = ComprehensiveCropData(
            id=request.crop_id,
            crop_name="",  # Will be populated by service
            scientific_name="",
            category="",
            crop_status="active"
        )
        
        # Get optimized recommendations
        recommendations = await service.get_optimized_variety_recommendations(
            crop_data=crop_data,
            regional_context=request.regional_context,
            farmer_preferences=request.farmer_preferences,
            limit=request.limit
        )
        
        # Calculate execution time
        execution_time = (time.time() - start_time) * 1000
        
        # Check performance target
        config = OptimizationConfig()
        performance_target_met = execution_time <= config.target_recommendation_time_ms
        
        # Create response
        response_data = OptimizedRecommendationResponse(
            recommendations=recommendations,
            total_count=len(recommendations),
            execution_time_ms=execution_time,
            cache_hit=False,  # Will be updated by service
            performance_target_met=performance_target_met
        )
        
        # Apply response optimization
        if response:
            response.headers["X-Execution-Time"] = f"{execution_time:.2f}ms"
            response.headers["X-Performance-Target-Met"] = str(performance_target_met)
            response.headers["X-Cache-Status"] = "miss"  # Will be updated by service
        
        return response_data
        
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        logger.error(f"Optimized variety recommendations failed: {e}")
        
        performance_monitor.record_operation(
            operation="optimized_recommendations_error",
            execution_time_ms=execution_time,
            cache_hit=False,
            additional_data={"error": str(e)}
        )
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get optimized variety recommendations: {str(e)}"
        )


@router.post("/search", response_model=OptimizedSearchResponse)
async def search_varieties_optimized(
    request: OptimizedSearchRequest,
    service: OptimizedVarietyRecommendationService = Depends(get_optimized_service),
    response: Response = None
):
    """
    Search varieties with optimization and performance target <1s.
    
    This endpoint provides fast variety search with full-text search capabilities,
    trait filtering, and comprehensive caching.
    
    Performance Targets:
    - Response time: <1 second
    - Cache hit rate: >70%
    - Search relevance: Optimized with PostgreSQL full-text search
    """
    start_time = time.time()
    
    try:
        # Get optimized search results
        search_results = await service.search_varieties_optimized(
            search_text=request.search_text,
            crop_id=request.crop_id,
            traits=request.traits,
            limit=request.limit
        )
        
        # Calculate execution time
        execution_time = (time.time() - start_time) * 1000
        
        # Check performance target
        config = OptimizationConfig()
        performance_target_met = execution_time <= config.target_variety_search_time_ms
        
        # Create response
        response_data = OptimizedSearchResponse(
            varieties=search_results.get("varieties", []),
            total_count=search_results.get("total_count", 0),
            search_params=search_results.get("search_params", {}),
            execution_time_ms=execution_time,
            cache_hit=search_results.get("cache_hit", False),
            performance_target_met=performance_target_met
        )
        
        # Apply response optimization
        if response:
            response.headers["X-Execution-Time"] = f"{execution_time:.2f}ms"
            response.headers["X-Performance-Target-Met"] = str(performance_target_met)
            response.headers["X-Cache-Status"] = "hit" if search_results.get("cache_hit") else "miss"
        
        return response_data
        
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        logger.error(f"Optimized variety search failed: {e}")
        
        performance_monitor.record_operation(
            operation="optimized_search_error",
            execution_time_ms=execution_time,
            cache_hit=False,
            additional_data={"error": str(e)}
        )
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search varieties: {str(e)}"
        )


@router.get("/varieties/{variety_id}/details", response_model=OptimizedDetailsResponse)
async def get_variety_details_optimized(
    variety_id: UUID,
    service: OptimizedVarietyRecommendationService = Depends(get_optimized_service),
    response: Response = None
):
    """
    Get optimized variety details with performance target <500ms.
    
    This endpoint provides comprehensive variety details with caching
    and optimized database queries.
    
    Performance Targets:
    - Response time: <500 milliseconds
    - Cache hit rate: >80%
    - Data completeness: Full variety information
    """
    start_time = time.time()
    
    try:
        # Get optimized variety details
        variety_details = await service.get_variety_details_optimized(variety_id)
        
        if not variety_details:
            raise HTTPException(
                status_code=404,
                detail=f"Variety with ID {variety_id} not found"
            )
        
        # Calculate execution time
        execution_time = (time.time() - start_time) * 1000
        
        # Check performance target
        config = OptimizationConfig()
        performance_target_met = execution_time <= config.target_variety_details_time_ms
        
        # Create response
        response_data = OptimizedDetailsResponse(
            variety_details=variety_details,
            execution_time_ms=execution_time,
            cache_hit=False,  # Will be updated by service
            performance_target_met=performance_target_met
        )
        
        # Apply response optimization
        if response:
            response.headers["X-Execution-Time"] = f"{execution_time:.2f}ms"
            response.headers["X-Performance-Target-Met"] = str(performance_target_met)
            response.headers["X-Cache-Status"] = "miss"  # Will be updated by service
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        logger.error(f"Optimized variety details failed: {e}")
        
        performance_monitor.record_operation(
            operation="optimized_details_error",
            execution_time_ms=execution_time,
            cache_hit=False,
            additional_data={"error": str(e)}
        )
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get variety details: {str(e)}"
        )


# ============================================================================
# PERFORMANCE MONITORING ENDPOINTS
# ============================================================================

@router.get("/metrics", response_model=PerformanceMetricsResponse)
async def get_performance_metrics(
    service: OptimizedVarietyRecommendationService = Depends(get_optimized_service)
):
    """
    Get comprehensive performance metrics for the optimized service.
    
    This endpoint provides detailed performance metrics including:
    - Service uptime and operation counts
    - Performance target compliance
    - Cache hit rates and database metrics
    - Optimization service status
    """
    try:
        metrics = await service.get_performance_metrics()
        
        return PerformanceMetricsResponse(
            service_uptime_seconds=metrics["service_uptime_seconds"],
            operation_counts=metrics["operation_counts"],
            performance_targets=metrics["performance_targets"],
            optimization_metrics=metrics["optimization_metrics"]
        )
        
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get performance metrics: {str(e)}"
        )


@router.get("/health")
async def health_check(
    service: OptimizedVarietyRecommendationService = Depends(get_optimized_service)
):
    """
    Perform health check on the optimized service.
    
    This endpoint checks the health of all optimization components including:
    - Base variety recommendation service
    - Database optimization service
    - Cache service (Redis)
    - Performance monitoring
    """
    try:
        health_status = await service.health_check()
        
        # Set appropriate HTTP status code
        status_code = 200 if health_status["overall_status"] == "healthy" else 503
        
        return JSONResponse(
            content=health_status,
            status_code=status_code
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            content={
                "overall_status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            },
            status_code=503
        )


# ============================================================================
# CACHE MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/cache/invalidate")
async def invalidate_cache(
    pattern: Optional[str] = Query(None, description="Cache pattern to invalidate"),
    service: OptimizedVarietyRecommendationService = Depends(get_optimized_service)
):
    """
    Invalidate cache entries.
    
    This endpoint allows manual cache invalidation for:
    - Specific cache patterns
    - All variety-related caches
    - Performance optimization caches
    """
    try:
        invalidated_count = await service.invalidate_cache(pattern)
        
        return {
            "success": True,
            "invalidated_count": invalidated_count,
            "pattern": pattern or "all_variety_caches",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Cache invalidation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to invalidate cache: {str(e)}"
        )


# ============================================================================
# COMPARISON ENDPOINTS (OPTIMIZED)
# ============================================================================

@router.post("/compare", response_model=VarietyComparisonResponse)
async def compare_varieties_optimized(
    request: VarietyComparisonRequest,
    service: OptimizedVarietyRecommendationService = Depends(get_optimized_service),
    response: Response = None
):
    """
    Compare varieties with optimization.
    
    This endpoint provides optimized variety comparison with:
    - Cached comparison results
    - Performance monitoring
    - Response optimization
    """
    start_time = time.time()
    
    try:
        # Use base service for comparison (it's already optimized)
        comparison_result = await service.base_service.compare_varieties(request)
        
        # Calculate execution time
        execution_time = (time.time() - start_time) * 1000
        
        # Apply response optimization
        if response:
            response.headers["X-Execution-Time"] = f"{execution_time:.2f}ms"
        
        return comparison_result
        
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        logger.error(f"Optimized variety comparison failed: {e}")
        
        performance_monitor.record_operation(
            operation="optimized_comparison_error",
            execution_time_ms=execution_time,
            cache_hit=False,
            additional_data={"error": str(e)}
        )
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compare varieties: {str(e)}"
        )


# ============================================================================
# BATCH OPERATIONS (OPTIMIZED)
# ============================================================================

@router.post("/batch/recommendations")
async def get_batch_recommendations(
    requests: List[OptimizedRecommendationRequest],
    service: OptimizedVarietyRecommendationService = Depends(get_optimized_service),
    response: Response = None
):
    """
    Get batch variety recommendations with optimization.
    
    This endpoint processes multiple recommendation requests in parallel
    with comprehensive optimization and performance monitoring.
    """
    start_time = time.time()
    
    try:
        # Limit batch size
        if len(requests) > 10:
            raise HTTPException(
                status_code=400,
                detail="Batch size cannot exceed 10 requests"
            )
        
        # Process requests in parallel
        tasks = []
        for req in requests:
            crop_data = ComprehensiveCropData(
                id=req.crop_id,
                crop_name="",
                scientific_name="",
                category="",
                crop_status="active"
            )
            
            task = service.get_optimized_variety_recommendations(
                crop_data=crop_data,
                regional_context=req.regional_context,
                farmer_preferences=req.farmer_preferences,
                limit=req.limit
            )
            tasks.append(task)
        
        # Execute all tasks in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful_results = []
        errors = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                errors.append({
                    "request_index": i,
                    "error": str(result)
                })
            else:
                successful_results.append({
                    "request_index": i,
                    "recommendations": result,
                    "count": len(result)
                })
        
        # Calculate execution time
        execution_time = (time.time() - start_time) * 1000
        
        # Apply response optimization
        if response:
            response.headers["X-Execution-Time"] = f"{execution_time:.2f}ms"
            response.headers["X-Batch-Size"] = str(len(requests))
            response.headers["X-Successful-Requests"] = str(len(successful_results))
            response.headers["X-Failed-Requests"] = str(len(errors))
        
        return {
            "success": True,
            "execution_time_ms": execution_time,
            "total_requests": len(requests),
            "successful_requests": len(successful_results),
            "failed_requests": len(errors),
            "results": successful_results,
            "errors": errors,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        logger.error(f"Batch recommendations failed: {e}")
        
        performance_monitor.record_operation(
            operation="batch_recommendations_error",
            execution_time_ms=execution_time,
            cache_hit=False,
            additional_data={"error": str(e), "batch_size": len(requests)}
        )
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process batch recommendations: {str(e)}"
        )
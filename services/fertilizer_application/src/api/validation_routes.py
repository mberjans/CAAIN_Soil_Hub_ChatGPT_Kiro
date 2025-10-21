"""
API routes for algorithm validation and improvement system.

This module provides REST API endpoints for:
- Algorithm validation (cross-validation, field validation, expert validation, outcome validation)
- Performance tracking and monitoring
- Continuous improvement management
- Validation result retrieval and analysis
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel, Field

from src.services.algorithm_validation_service import (
    AlgorithmValidationService, ValidationType, ValidationResult,
    PerformanceMetrics, ImprovementRecommendation
)
from src.services.sophisticated_method_selection_service import (
    SophisticatedMethodSelectionService, OptimizationObjective, OptimizationResult
)
from src.models.application_models import ApplicationRequest

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/validation", tags=["algorithm-validation"])

# Dependency injection
async def get_validation_service() -> AlgorithmValidationService:
    return AlgorithmValidationService()

async def get_sophisticated_service() -> SophisticatedMethodSelectionService:
    return SophisticatedMethodSelectionService()


# Request/Response Models
class ValidationRequest(BaseModel):
    """Request model for algorithm validation."""
    algorithm_name: str = Field(..., description="Name of the algorithm to validate")
    test_data: List[Dict[str, Any]] = Field(..., description="Test dataset for validation")
    validation_types: List[str] = Field(
        default=["cross_validation", "statistical_validation", "performance_validation"],
        description="Types of validation to perform"
    )


class PerformanceTrackingRequest(BaseModel):
    """Request model for performance tracking."""
    algorithm_name: str = Field(..., description="Name of the algorithm")
    request_data: Dict[str, Any] = Field(..., description="Request data")
    result_data: Dict[str, Any] = Field(..., description="Result data")
    user_feedback: Optional[Dict[str, Any]] = Field(None, description="User feedback data")


class ImprovementImplementationRequest(BaseModel):
    """Request model for implementing improvements."""
    recommendation_id: str = Field(..., description="ID of the improvement recommendation")
    implementation_details: Optional[Dict[str, Any]] = Field(None, description="Implementation details")


class ValidationSummaryResponse(BaseModel):
    """Response model for validation summary."""
    algorithm_name: str
    period_days: int
    total_validations: int
    validation_types: List[str]
    overall_status: str
    avg_validation_score: float
    total_performance_records: int
    avg_accuracy: float
    avg_response_time_ms: float
    avg_user_satisfaction: float
    improvement_recommendations_count: int
    timestamp: datetime


# API Endpoints

@router.post("/validate-algorithm", response_model=List[Dict[str, Any]])
async def validate_algorithm(
    request: ValidationRequest,
    validation_service: AlgorithmValidationService = Depends(get_validation_service)
):
    """
    Perform comprehensive validation of an algorithm.
    
    This endpoint validates algorithms using multiple validation types:
    - Cross-validation: Statistical validation using k-fold cross-validation
    - Field validation: Real-world validation with field data
    - Expert validation: Validation by agricultural professionals
    - Outcome validation: Validation based on farmer feedback and results
    - Statistical validation: Comprehensive statistical metrics
    - Performance validation: Response time and throughput validation
    
    Args:
        request: Validation request with algorithm name, test data, and validation types
        
    Returns:
        List of validation results with scores, metrics, and recommendations
    """
    try:
        # Convert string validation types to enum
        validation_types = []
        for vt in request.validation_types:
            try:
                validation_types.append(ValidationType(vt))
            except ValueError:
                logger.warning(f"Invalid validation type: {vt}")
                continue
        
        if not validation_types:
            raise HTTPException(status_code=400, detail="No valid validation types provided")
        
        # Perform validation
        validation_results = await validation_service.validate_algorithm_comprehensive(
            request.algorithm_name,
            request.test_data,
            validation_types
        )
        
        # Convert results to response format
        response = []
        for result in validation_results:
            response.append({
                "validation_id": result.validation_id,
                "validation_type": result.validation_type.value,
                "algorithm_name": result.algorithm_name,
                "status": result.status.value,
                "score": result.score,
                "confidence_interval": result.confidence_interval,
                "metrics": result.metrics,
                "recommendations": result.recommendations,
                "validation_time_ms": result.validation_time_ms,
                "timestamp": result.timestamp.isoformat(),
                "details": result.details
            })
        
        logger.info(f"Algorithm validation completed for {request.algorithm_name}")
        return response
        
    except Exception as e:
        logger.error(f"Error in algorithm validation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/track-performance", response_model=Dict[str, Any])
async def track_performance(
    request: PerformanceTrackingRequest,
    validation_service: AlgorithmValidationService = Depends(get_validation_service),
    sophisticated_service: SophisticatedMethodSelectionService = Depends(get_sophisticated_service)
):
    """
    Track performance metrics for an algorithm.
    
    This endpoint tracks various performance metrics including:
    - Accuracy scores
    - Response times
    - Throughput
    - Error rates
    - User satisfaction scores
    
    Args:
        request: Performance tracking request with algorithm name, request data, result data, and user feedback
        
    Returns:
        Performance metrics with timestamps and analysis
    """
    try:
        # Create ApplicationRequest from request data
        request_data = request.request_data
        app_request = ApplicationRequest(
            field_conditions=request_data.get('field_conditions'),
            crop_requirements=request_data.get('crop_requirements'),
            fertilizer_specification=request_data.get('fertilizer_specification'),
            available_equipment=request_data.get('available_equipment', [])
        )
        
        # Create OptimizationResult from result data
        result_data = request.result_data
        opt_result = OptimizationResult(
            optimal_method=result_data.get('optimal_method'),
            objective_value=result_data.get('objective_value', 0.0),
            confidence_score=result_data.get('confidence_score', 0.0),
            alternative_solutions=result_data.get('alternative_solutions', []),
            optimization_time_ms=result_data.get('optimization_time_ms', 0.0),
            algorithm_used=result_data.get('algorithm_used', 'unknown'),
            convergence_info=result_data.get('convergence_info', {})
        )
        
        # Track performance metrics
        performance_metrics = await validation_service.track_performance_metrics(
            request.algorithm_name,
            app_request,
            opt_result,
            request.user_feedback
        )
        
        # Convert to response format
        response = {
            "algorithm_name": performance_metrics.algorithm_name,
            "accuracy_score": performance_metrics.accuracy_score,
            "precision_score": performance_metrics.precision_score,
            "recall_score": performance_metrics.recall_score,
            "f1_score": performance_metrics.f1_score,
            "response_time_ms": performance_metrics.response_time_ms,
            "throughput_per_second": performance_metrics.throughput_per_second,
            "error_rate": performance_metrics.error_rate,
            "user_satisfaction_score": performance_metrics.user_satisfaction_score,
            "timestamp": performance_metrics.timestamp.isoformat(),
            "sample_size": performance_metrics.sample_size
        }
        
        logger.info(f"Performance metrics tracked for {request.algorithm_name}")
        return response
        
    except Exception as e:
        logger.error(f"Error tracking performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/validation-summary/{algorithm_name}", response_model=ValidationSummaryResponse)
async def get_validation_summary(
    algorithm_name: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to include in summary"),
    validation_service: AlgorithmValidationService = Depends(get_validation_service)
):
    """
    Get validation summary for an algorithm.
    
    This endpoint provides a comprehensive summary of validation results and performance
    metrics for a specific algorithm over a specified time period.
    
    Args:
        algorithm_name: Name of the algorithm
        days: Number of days to include in the summary (1-365)
        
    Returns:
        Validation summary with statistics and trends
    """
    try:
        summary = await validation_service.get_validation_summary(algorithm_name, days)
        
        response = ValidationSummaryResponse(
            algorithm_name=summary['algorithm_name'],
            period_days=summary['period_days'],
            total_validations=summary['total_validations'],
            validation_types=summary['validation_types'],
            overall_status=summary['overall_status'],
            avg_validation_score=summary['avg_validation_score'],
            total_performance_records=summary['total_performance_records'],
            avg_accuracy=summary['avg_accuracy'],
            avg_response_time_ms=summary['avg_response_time_ms'],
            avg_user_satisfaction=summary['avg_user_satisfaction'],
            improvement_recommendations_count=summary['improvement_recommendations_count'],
            timestamp=summary['timestamp']
        )
        
        logger.info(f"Validation summary retrieved for {algorithm_name}")
        return response
        
    except Exception as e:
        logger.error(f"Error getting validation summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/improvement-recommendations/{algorithm_name}", response_model=List[Dict[str, Any]])
async def get_improvement_recommendations(
    algorithm_name: str,
    validation_service: AlgorithmValidationService = Depends(get_validation_service)
):
    """
    Get improvement recommendations for an algorithm.
    
    This endpoint retrieves improvement recommendations based on validation results
    and performance analysis.
    
    Args:
        algorithm_name: Name of the algorithm
        
    Returns:
        List of improvement recommendations with priorities and implementation details
    """
    try:
        # Get recent validation results for the algorithm
        recent_validations = [
            v for v in validation_service.validation_results
            if v.algorithm_name == algorithm_name
        ]
        
        # Get recent performance history
        recent_performance = [
            p for p in validation_service.performance_history
            if p.algorithm_name == algorithm_name
        ]
        
        # Generate recommendations
        recommendations = await validation_service.generate_improvement_recommendations(
            algorithm_name,
            recent_validations,
            recent_performance
        )
        
        # Convert to response format
        response = []
        for rec in recommendations:
            response.append({
                "recommendation_id": rec.recommendation_id,
                "algorithm_name": rec.algorithm_name,
                "improvement_type": rec.improvement_type,
                "priority": rec.priority,
                "description": rec.description,
                "expected_impact": rec.expected_impact,
                "implementation_effort": rec.implementation_effort,
                "validation_required": rec.validation_required,
                "timestamp": rec.timestamp.isoformat()
            })
        
        logger.info(f"Retrieved {len(recommendations)} improvement recommendations for {algorithm_name}")
        return response
        
    except Exception as e:
        logger.error(f"Error getting improvement recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/implement-improvement", response_model=Dict[str, Any])
async def implement_improvement(
    request: ImprovementImplementationRequest,
    validation_service: AlgorithmValidationService = Depends(get_validation_service)
):
    """
    Implement an algorithm improvement based on recommendation.
    
    This endpoint implements algorithm improvements such as:
    - Model retraining with new data
    - Performance optimization
    - Algorithm enhancement
    - Parameter tuning
    
    Args:
        request: Improvement implementation request with recommendation ID and details
        
    Returns:
        Implementation result with status and details
    """
    try:
        # Find the recommendation
        recommendation = None
        for rec in validation_service.improvement_recommendations:
            if rec.recommendation_id == request.recommendation_id:
                recommendation = rec
                break
        
        if not recommendation:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        
        # Implement the improvement
        implementation_result = await validation_service.implement_algorithm_improvement(
            recommendation
        )
        
        logger.info(f"Improvement implementation completed: {request.recommendation_id}")
        return implementation_result
        
    except Exception as e:
        logger.error(f"Error implementing improvement: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/validation-results/{algorithm_name}", response_model=List[Dict[str, Any]])
async def get_validation_results(
    algorithm_name: str,
    validation_type: Optional[str] = Query(None, description="Filter by validation type"),
    days: int = Query(30, ge=1, le=365, description="Number of days to include"),
    validation_service: AlgorithmValidationService = Depends(get_validation_service)
):
    """
    Get validation results for an algorithm.
    
    This endpoint retrieves historical validation results with optional filtering
    by validation type and time period.
    
    Args:
        algorithm_name: Name of the algorithm
        validation_type: Optional filter by validation type
        days: Number of days to include in results
        
    Returns:
        List of validation results with detailed metrics
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Filter validation results
        filtered_results = [
            v for v in validation_service.validation_results
            if v.algorithm_name == algorithm_name and v.timestamp >= cutoff_date
        ]
        
        # Apply validation type filter if specified
        if validation_type:
            try:
                validation_type_enum = ValidationType(validation_type)
                filtered_results = [
                    v for v in filtered_results
                    if v.validation_type == validation_type_enum
                ]
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid validation type: {validation_type}")
        
        # Convert to response format
        response = []
        for result in filtered_results:
            response.append({
                "validation_id": result.validation_id,
                "validation_type": result.validation_type.value,
                "algorithm_name": result.algorithm_name,
                "status": result.status.value,
                "score": result.score,
                "confidence_interval": result.confidence_interval,
                "metrics": result.metrics,
                "recommendations": result.recommendations,
                "validation_time_ms": result.validation_time_ms,
                "timestamp": result.timestamp.isoformat(),
                "details": result.details
            })
        
        logger.info(f"Retrieved {len(response)} validation results for {algorithm_name}")
        return response
        
    except Exception as e:
        logger.error(f"Error getting validation results: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance-history/{algorithm_name}", response_model=List[Dict[str, Any]])
async def get_performance_history(
    algorithm_name: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to include"),
    validation_service: AlgorithmValidationService = Depends(get_validation_service)
):
    """
    Get performance history for an algorithm.
    
    This endpoint retrieves historical performance metrics including accuracy,
    response times, throughput, and user satisfaction scores.
    
    Args:
        algorithm_name: Name of the algorithm
        days: Number of days to include in history
        
    Returns:
        List of performance metrics with timestamps
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Filter performance history
        filtered_performance = [
            p for p in validation_service.performance_history
            if p.algorithm_name == algorithm_name and p.timestamp >= cutoff_date
        ]
        
        # Convert to response format
        response = []
        for perf in filtered_performance:
            response.append({
                "algorithm_name": perf.algorithm_name,
                "accuracy_score": perf.accuracy_score,
                "precision_score": perf.precision_score,
                "recall_score": perf.recall_score,
                "f1_score": perf.f1_score,
                "response_time_ms": perf.response_time_ms,
                "throughput_per_second": perf.throughput_per_second,
                "error_rate": perf.error_rate,
                "user_satisfaction_score": perf.user_satisfaction_score,
                "timestamp": perf.timestamp.isoformat(),
                "sample_size": perf.sample_size
            })
        
        logger.info(f"Retrieved {len(response)} performance records for {algorithm_name}")
        return response
        
    except Exception as e:
        logger.error(f"Error getting performance history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint for validation service."""
    return {
        "status": "healthy",
        "service": "algorithm-validation",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/validation-types")
async def get_validation_types():
    """Get available validation types."""
    return {
        "validation_types": [
            {
                "type": vt.value,
                "description": _get_validation_type_description(vt)
            }
            for vt in ValidationType
        ]
    }


def _get_validation_type_description(validation_type: ValidationType) -> str:
    """Get description for validation type."""
    descriptions = {
        ValidationType.CROSS_VALIDATION: "Statistical validation using k-fold cross-validation",
        ValidationType.FIELD_VALIDATION: "Real-world validation with field data and farmer feedback",
        ValidationType.EXPERT_VALIDATION: "Validation by agricultural professionals and experts",
        ValidationType.OUTCOME_VALIDATION: "Validation based on actual outcomes and farmer results",
        ValidationType.STATISTICAL_VALIDATION: "Comprehensive statistical metrics and analysis",
        ValidationType.PERFORMANCE_VALIDATION: "Response time, throughput, and performance validation"
    }
    return descriptions.get(validation_type, "Unknown validation type")
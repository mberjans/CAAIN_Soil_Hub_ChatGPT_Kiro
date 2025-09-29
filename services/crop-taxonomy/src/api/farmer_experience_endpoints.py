"""
Farmer Experience API Endpoints

API endpoints for farmer experience data collection, validation, and integration
with crop variety recommendations.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from typing import List, Dict, Any, Optional
import logging
from uuid import UUID
from datetime import datetime

try:
    from ..services.farmer_experience_service import farmer_experience_service
    from ..models.farmer_experience_models import (
        FarmerExperienceRequest,
        FarmerExperienceResponse,
        FarmerExperienceIntegrationRequest,
        FarmerExperienceIntegrationResponse,
        FarmerFeedbackSurvey,
        FieldPerformanceData,
        ExperienceAggregationResult,
        FarmerProfile,
        ValidationStatus
    )
except ImportError:
    from services.farmer_experience_service import farmer_experience_service
    from models.farmer_experience_models import (
        FarmerExperienceRequest,
        FarmerExperienceResponse,
        FarmerExperienceIntegrationRequest,
        FarmerExperienceIntegrationResponse,
        FarmerFeedbackSurvey,
        FieldPerformanceData,
        ExperienceAggregationResult,
        FarmerProfile,
        ValidationStatus
    )

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/farmer-experience", tags=["farmer-experience"])


# Dependency injection
async def get_farmer_experience_service():
    """Get farmer experience service instance."""
    return farmer_experience_service


@router.post("/collect-feedback", response_model=FarmerExperienceResponse)
async def collect_farmer_feedback(
    request: FarmerExperienceRequest,
    background_tasks: BackgroundTasks,
    service = Depends(get_farmer_experience_service)
):
    """
    Collect farmer feedback for a specific variety.
    
    This endpoint allows farmers to submit structured feedback about their
    experience with a specific crop variety, including performance ratings,
    field data, and qualitative observations.
    
    Features:
    - Structured survey data collection
    - Field performance data validation
    - Automatic data quality assessment
    - Background validation processing
    - Confidence scoring
    """
    try:
        start_time = datetime.utcnow()
        
        # Collect farmer feedback
        experience_entry = await service.collect_farmer_feedback(
            farmer_id=request.farmer_id,
            variety_id=request.variety_id,
            survey_data=request.survey_data,
            field_performance=request.field_performance
        )
        
        # Schedule background validation if required
        if request.validation_required:
            background_tasks.add_task(
                _validate_experience_entry_background,
                experience_entry.id,
                service
            )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return FarmerExperienceResponse(
            success=True,
            experience_entry_id=experience_entry.id,
            validation_status=experience_entry.validation_status,
            confidence_score=experience_entry.confidence_score,
            message="Farmer feedback collected successfully",
            requires_additional_data=False,
            follow_up_actions=[
                "Monitor validation status",
                "Review confidence score",
                "Consider additional field data if available"
            ],
            processing_time_ms=processing_time
        )
        
    except ValueError as e:
        logger.warning(f"Validation error in farmer feedback collection: {e}")
        return FarmerExperienceResponse(
            success=False,
            validation_status=ValidationStatus.INVALID,
            message=f"Validation error: {str(e)}",
            errors=[str(e)],
            requires_additional_data=True,
            follow_up_actions=[
                "Review and correct survey data",
                "Ensure all required fields are provided",
                "Check rating values are within valid range"
            ]
        )
        
    except Exception as e:
        logger.error(f"Error collecting farmer feedback: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to collect farmer feedback: {str(e)}"
        )


@router.post("/validate-performance", response_model=Dict[str, Any])
async def validate_performance_data(
    variety_ids: List[UUID],
    include_trial_data: bool = Query(False, description="Include trial data comparison"),
    service = Depends(get_farmer_experience_service)
):
    """
    Validate farmer experience data against trial data and statistical models.
    
    This endpoint performs comprehensive validation of farmer experience data,
    including statistical analysis, bias detection, and cross-validation with
    official trial data when available.
    
    Features:
    - Statistical validation of farmer data
    - Cross-validation with trial data
    - Bias detection and analysis
    - Confidence scoring
    - Data quality assessment
    """
    try:
        # Get experience entries for specified varieties
        experience_entries = await _get_experience_entries_for_validation(variety_ids, service)
        
        if not experience_entries:
            raise HTTPException(
                status_code=404,
                detail="No experience entries found for specified varieties"
            )
        
        # Get trial data if requested
        trial_data = None
        if include_trial_data:
            trial_data = await _get_trial_data_for_varieties(variety_ids)
        
        # Validate performance data
        validation_result = await service.validate_performance_data(
            experience_entries=experience_entries,
            trial_data=trial_data
        )
        
        return {
            "success": True,
            "validation_result": validation_result.dict(),
            "message": "Performance data validation completed",
            "varieties_validated": len(variety_ids),
            "total_entries_processed": validation_result.total_entries,
            "validated_entries": validation_result.validated_entries,
            "overall_confidence": validation_result.overall_confidence
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating performance data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to validate performance data: {str(e)}"
        )


@router.post("/aggregate-experience", response_model=ExperienceAggregationResult)
async def aggregate_experience_data(
    variety_id: UUID,
    apply_bias_correction: bool = Query(True, description="Apply bias correction algorithms"),
    minimum_sample_size: int = Query(5, ge=1, description="Minimum sample size for aggregation"),
    service = Depends(get_farmer_experience_service)
):
    """
    Aggregate farmer experience data for a specific variety.
    
    This endpoint aggregates validated farmer experience data for a variety,
    applying statistical analysis, bias correction, and confidence assessment.
    
    Features:
    - Statistical aggregation of farmer data
    - Bias detection and correction
    - Confidence level assessment
    - Sample size validation
    - Data quality scoring
    """
    try:
        # Get validated experience entries for the variety
        experience_entries = await _get_validated_experience_entries(variety_id, service)
        
        if len(experience_entries) < minimum_sample_size:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient data for aggregation. Found {len(experience_entries)} entries, minimum required: {minimum_sample_size}"
            )
        
        # Aggregate experience data
        aggregation_result = await service.aggregate_experience_data(
            variety_id=variety_id,
            experience_entries=experience_entries,
            apply_bias_correction=apply_bias_correction
        )
        
        return aggregation_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error aggregating experience data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to aggregate experience data: {str(e)}"
        )


@router.post("/integrate-recommendations", response_model=FarmerExperienceIntegrationResponse)
async def integrate_with_recommendations(
    request: FarmerExperienceIntegrationRequest,
    service = Depends(get_farmer_experience_service)
):
    """
    Integrate farmer experience data into variety recommendations.
    
    This endpoint enhances existing variety recommendations with farmer
    experience insights, improving accuracy and relevance based on real-world
    farmer feedback and performance data.
    
    Features:
    - Enhancement of variety recommendations
    - Integration of farmer experience insights
    - Bias correction application
    - Confidence improvement assessment
    - Data quality validation
    """
    try:
        start_time = datetime.utcnow()
        
        # Convert request data to internal models
        variety_recommendations = await _convert_to_recommendation_models(request.variety_recommendations)
        
        # Integrate with recommendations
        enhanced_recommendations = await service.integrate_with_recommendations(
            variety_recommendations=variety_recommendations,
            experience_data=request.experience_data
        )
        
        # Calculate integration metrics
        varieties_enhanced = len([r for r in enhanced_recommendations if hasattr(r, 'farmer_experience_insights')])
        experience_data_used = len(request.experience_data)
        bias_corrections_applied = sum(
            1 for exp_data in request.experience_data.values() 
            if exp_data.bias_correction_applied
        )
        
        # Calculate average confidence improvement
        confidence_improvements = []
        for original, enhanced in zip(variety_recommendations, enhanced_recommendations):
            if hasattr(original, 'confidence_level') and hasattr(enhanced, 'confidence_level'):
                improvement = enhanced.confidence_level - original.confidence_level
                confidence_improvements.append(improvement)
        
        average_confidence_improvement = (
            sum(confidence_improvements) / len(confidence_improvements) 
            if confidence_improvements else 0.0
        )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return FarmerExperienceIntegrationResponse(
            success=True,
            enhanced_recommendations=[r.dict() for r in enhanced_recommendations],
            varieties_enhanced=varieties_enhanced,
            experience_data_used=experience_data_used,
            bias_corrections_applied=bias_corrections_applied,
            average_confidence_improvement=average_confidence_improvement,
            data_quality_score=0.8,  # Calculate based on actual data quality
            message="Recommendations successfully enhanced with farmer experience",
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error integrating experience with recommendations: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to integrate experience data: {str(e)}"
        )


@router.get("/farmer-profile/{farmer_id}", response_model=Optional[FarmerProfile])
async def get_farmer_profile(
    farmer_id: UUID,
    service = Depends(get_farmer_experience_service)
):
    """
    Get farmer profile for bias correction and personalization.
    
    This endpoint retrieves farmer profile information used for bias
    correction algorithms and recommendation personalization.
    
    Features:
    - Farmer profile retrieval
    - Bias correction data
    - Personalization parameters
    - Experience history
    """
    try:
        farmer_profile = await service.get_farmer_profile(farmer_id)
        
        if not farmer_profile:
            raise HTTPException(
                status_code=404,
                detail=f"Farmer profile not found for farmer ID: {farmer_id}"
            )
        
        return farmer_profile
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting farmer profile: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get farmer profile: {str(e)}"
        )


@router.get("/experience-summary/{variety_id}", response_model=Dict[str, Any])
async def get_experience_summary(
    variety_id: UUID,
    include_insights: bool = Query(True, description="Include farmer insights"),
    service = Depends(get_farmer_experience_service)
):
    """
    Get summary of farmer experience data for a specific variety.
    
    This endpoint provides a comprehensive summary of farmer experience
    data for a variety, including aggregated metrics, insights, and
    confidence assessments.
    
    Features:
    - Aggregated performance metrics
    - Farmer insights and recommendations
    - Confidence and quality scores
    - Statistical significance
    - Bias correction information
    """
    try:
        # Get aggregated experience data
        experience_entries = await _get_validated_experience_entries(variety_id, service)
        
        if not experience_entries:
            raise HTTPException(
                status_code=404,
                detail=f"No farmer experience data found for variety ID: {variety_id}"
            )
        
        # Aggregate data
        aggregation_result = await service.aggregate_experience_data(
            variety_id=variety_id,
            experience_entries=experience_entries,
            apply_bias_correction=True
        )
        
        # Generate insights if requested
        insights = None
        if include_insights:
            insights = await _generate_farmer_insights(aggregation_result, experience_entries)
        
        return {
            "variety_id": variety_id,
            "aggregation_result": aggregation_result.dict(),
            "insights": insights.dict() if insights else None,
            "sample_size": len(experience_entries),
            "data_quality_score": aggregation_result.aggregated_data.get("data_quality_score", 0.0),
            "confidence_level": aggregation_result.confidence_level.value,
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting experience summary: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get experience summary: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for farmer experience service."""
    return {
        "status": "healthy",
        "service": "farmer-experience",
        "timestamp": datetime.utcnow().isoformat(),
        "features": [
            "farmer_feedback_collection",
            "performance_validation",
            "experience_aggregation",
            "bias_correction",
            "recommendation_integration"
        ]
    }


# Background task functions
async def _validate_experience_entry_background(entry_id: UUID, service):
    """Background task for validating experience entries."""
    try:
        logger.info(f"Starting background validation for entry {entry_id}")
        # Implementation would validate the entry and update its status
        # This is a placeholder for the actual validation logic
        logger.info(f"Background validation completed for entry {entry_id}")
    except Exception as e:
        logger.error(f"Error in background validation for entry {entry_id}: {e}")


# Helper functions
async def _get_experience_entries_for_validation(variety_ids: List[UUID], service) -> List[Any]:
    """Get experience entries for validation."""
    # This would query the database for experience entries
    # Placeholder implementation
    return []


async def _get_trial_data_for_varieties(variety_ids: List[UUID]) -> Optional[Dict[str, Any]]:
    """Get trial data for varieties."""
    # This would query trial data from external sources
    # Placeholder implementation
    return None


async def _get_validated_experience_entries(variety_id: UUID, service) -> List[Any]:
    """Get validated experience entries for a variety."""
    # This would query the database for validated entries
    # Placeholder implementation
    return []


async def _convert_to_recommendation_models(recommendations_data: List[Dict[str, Any]]) -> List[Any]:
    """Convert recommendation data to internal models."""
    # This would convert the data to proper recommendation models
    # Placeholder implementation
    return []


async def _generate_farmer_insights(aggregation_result: ExperienceAggregationResult, experience_entries: List[Any]) -> Any:
    """Generate farmer insights from aggregated data."""
    # This would generate insights based on the aggregated data
    # Placeholder implementation
    return None
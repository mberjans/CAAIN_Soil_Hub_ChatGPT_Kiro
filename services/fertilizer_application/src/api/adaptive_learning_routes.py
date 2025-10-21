"""
API routes for the adaptive learning service.

This module provides REST API endpoints for:
- Tracking recommendation outcomes
- Integrating farmer feedback
- Generating ML-improved recommendations
- Accessing learning metrics and adaptation profiles
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, Optional, List
import logging
from uuid import uuid4

from src.services.adaptive_learning_service import (
    AdaptiveLearningService, FeedbackType, RecommendationOutcome,
    LearningMetrics, AdaptationProfile
)
from src.models.application_models import (
    ApplicationRequest, ApplicationResponse, ApplicationMethodType,
    FieldConditions, CropRequirements, FertilizerSpecification
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/adaptive-learning", tags=["adaptive-learning"])

# Dependency injection
async def get_adaptive_learning_service() -> AdaptiveLearningService:
    return AdaptiveLearningService()


@router.post("/track-outcome", response_model=RecommendationOutcome)
async def track_recommendation_outcome(
    recommendation_id: str,
    farmer_id: str,
    field_id: str,
    method_type: ApplicationMethodType,
    field_conditions: FieldConditions,
    crop_requirements: CropRequirements,
    fertilizer_specification: FertilizerSpecification,
    outcome_data: Dict[str, Any],
    service: AdaptiveLearningService = Depends(get_adaptive_learning_service)
):
    """
    Track the outcome of a fertilizer application recommendation.
    
    This endpoint allows farmers and agricultural consultants to report
    the actual results of fertilizer application recommendations, enabling
    the learning system to improve future recommendations.
    
    **Agricultural Context:**
    - Tracks yield outcomes, cost effectiveness, and farmer satisfaction
    - Monitors environmental impact and equipment performance
    - Enables continuous improvement of recommendation algorithms
    - Supports regional and farm-specific adaptation
    
    **Required Data:**
    - Recommendation ID and farmer/field identifiers
    - Application method used and field conditions
    - Actual outcomes (yield, cost, labor hours, etc.)
    - Farmer feedback and satisfaction ratings
    """
    try:
        logger.info(f"Tracking outcome for recommendation {recommendation_id}")
        
        outcome = await service.track_recommendation_outcome(
            recommendation_id=recommendation_id,
            farmer_id=farmer_id,
            field_id=field_id,
            method_type=method_type,
            field_conditions=field_conditions,
            crop_requirements=crop_requirements,
            fertilizer_specification=fertilizer_specification,
            outcome_data=outcome_data
        )
        
        logger.info(f"Successfully tracked outcome for recommendation {recommendation_id}")
        return outcome
        
    except Exception as e:
        logger.error(f"Error tracking recommendation outcome: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to track outcome: {str(e)}")


@router.post("/feedback")
async def integrate_farmer_feedback(
    recommendation_id: str,
    feedback_type: FeedbackType,
    feedback_value: Any,
    comments: Optional[str] = None,
    service: AdaptiveLearningService = Depends(get_adaptive_learning_service)
):
    """
    Integrate farmer feedback into the learning system.
    
    This endpoint allows farmers to provide feedback on fertilizer application
    recommendations, including yield outcomes, cost effectiveness, labor efficiency,
    environmental impact, and overall satisfaction.
    
    **Feedback Types:**
    - Yield Outcome: Actual vs predicted yield
    - Cost Effectiveness: Actual vs predicted costs
    - Labor Efficiency: Hours spent on application
    - Environmental Impact: Runoff incidents, nutrient loss
    - Equipment Performance: Equipment issues encountered
    - Overall Satisfaction: 1-5 rating scale
    
    **Learning Integration:**
    - Feedback is used to improve ML models
    - Enables farm-specific adaptation
    - Supports regional pattern recognition
    - Triggers model retraining when sufficient data is available
    """
    try:
        logger.info(f"Integrating farmer feedback for recommendation {recommendation_id}")
        
        success = await service.integrate_farmer_feedback(
            recommendation_id=recommendation_id,
            feedback_type=feedback_type,
            feedback_value=feedback_value,
            comments=comments
        )
        
        if success:
            logger.info(f"Successfully integrated farmer feedback for recommendation {recommendation_id}")
            return {"success": True, "message": "Feedback integrated successfully"}
        else:
            logger.warning(f"Failed to integrate farmer feedback for recommendation {recommendation_id}")
            raise HTTPException(status_code=404, detail="Recommendation not found")
        
    except Exception as e:
        logger.error(f"Error integrating farmer feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to integrate feedback: {str(e)}")


@router.post("/improve-recommendations", response_model=ApplicationResponse)
async def improve_recommendations(
    request: ApplicationRequest,
    farmer_id: str,
    field_id: str,
    service: AdaptiveLearningService = Depends(get_adaptive_learning_service)
):
    """
    Generate ML-improved fertilizer application recommendations.
    
    This endpoint uses machine learning insights, regional adaptation,
    farm-specific patterns, and seasonal adjustments to provide enhanced
    fertilizer application method recommendations.
    
    **ML Enhancement Features:**
    - Outcome prediction using trained models
    - Regional adaptation based on local patterns
    - Farm-specific learning from historical data
    - Seasonal adjustment factors
    - Multi-objective optimization with ML insights
    
    **Adaptation Mechanisms:**
    - Regional soil type preferences
    - Crop success patterns by farm
    - Seasonal application timing optimization
    - Equipment efficiency considerations
    - Cost sensitivity analysis
    
    **Response includes:**
    - ML-enhanced method recommendations
    - Confidence scores with adaptation factors
    - Learning metrics and model performance
    - Regional and farm-specific insights
    """
    try:
        logger.info(f"Generating ML-improved recommendations for farmer {farmer_id}")
        
        response = await service.improve_recommendations(
            request=request,
            farmer_id=farmer_id,
            field_id=field_id
        )
        
        logger.info(f"Successfully generated ML-improved recommendations")
        return response
        
    except Exception as e:
        logger.error(f"Error improving recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to improve recommendations: {str(e)}")


@router.get("/learning-metrics", response_model=LearningMetrics)
async def get_learning_metrics(
    service: AdaptiveLearningService = Depends(get_adaptive_learning_service)
):
    """
    Get current learning system performance metrics.
    
    This endpoint provides insights into the adaptive learning system's
    performance, including model accuracy, feedback integration rates,
    adaptation effectiveness, and regional coverage.
    
    **Metrics Provided:**
    - Model Accuracy: R² score for ML predictions
    - Prediction Error: Mean squared error
    - Feedback Integration Rate: Percentage of recommendations with feedback
    - Adaptation Effectiveness: Farm-specific adaptation coverage
    - Seasonal Adjustment Accuracy: Seasonal factor performance
    - Regional Adaptation Score: Geographic coverage effectiveness
    - Last Updated: Timestamp of last metrics update
    
    **Use Cases:**
    - Monitor learning system performance
    - Identify areas for improvement
    - Track farmer engagement
    - Assess regional coverage
    """
    try:
        logger.info("Retrieving learning system metrics")
        
        metrics = await service.get_learning_metrics()
        
        logger.info("Successfully retrieved learning system metrics")
        return metrics
        
    except Exception as e:
        logger.error(f"Error retrieving learning metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve metrics: {str(e)}")


@router.get("/adaptation-profile", response_model=Optional[AdaptationProfile])
async def get_adaptation_profile(
    farmer_id: str,
    field_id: str,
    service: AdaptiveLearningService = Depends(get_adaptive_learning_service)
):
    """
    Get adaptation profile for a specific farmer and field.
    
    This endpoint provides the current adaptation profile for a farmer-field
    combination, including soil type preferences, crop success patterns,
    seasonal factors, and farm-specific characteristics.
    
    **Profile Components:**
    - Soil Type Preferences: Success rates by soil type
    - Crop Success Patterns: Historical crop performance
    - Seasonal Factors: Seasonal application preferences
    - Equipment Efficiency: Equipment performance data
    - Cost Sensitivity: Farm-specific cost considerations
    - Labor Preferences: Labor efficiency patterns
    - Environmental Priorities: Environmental focus areas
    
    **Use Cases:**
    - Understand farm-specific adaptation
    - Review learning progress
    - Identify optimization opportunities
    - Support agricultural consulting
    """
    try:
        logger.info(f"Retrieving adaptation profile for farmer {farmer_id}, field {field_id}")
        
        profile = await service.get_adaptation_profile(farmer_id, field_id)
        
        logger.info(f"Successfully retrieved adaptation profile")
        return profile
        
    except Exception as e:
        logger.error(f"Error retrieving adaptation profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve profile: {str(e)}")


@router.get("/export-learning-data")
async def export_learning_data(
    service: AdaptiveLearningService = Depends(get_adaptive_learning_service)
):
    """
    Export learning data for analysis and research.
    
    This endpoint provides access to the learning system's data for
    analysis, research, and system improvement purposes.
    
    **Data Exported:**
    - Recommendation Outcomes: All tracked outcomes
    - Farmer Feedback: All feedback received
    - Adaptation Profiles: Farm-specific profiles
    - Learning Metrics: System performance data
    
    **Use Cases:**
    - Agricultural research and analysis
    - System performance evaluation
    - Model improvement research
    - Regional pattern analysis
    - Farmer engagement assessment
    
    **Privacy Note:**
    - Data is anonymized for research purposes
    - Personal identifiers are removed
    - Agricultural data is aggregated
    """
    try:
        logger.info("Exporting learning data for analysis")
        
        data = await service.export_learning_data()
        
        logger.info("Successfully exported learning data")
        return data
        
    except Exception as e:
        logger.error(f"Error exporting learning data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export data: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for the adaptive learning service."""
    return {
        "status": "healthy",
        "service": "adaptive-learning",
        "features": [
            "outcome_tracking",
            "farmer_feedback_integration",
            "ml_recommendation_improvement",
            "regional_adaptation",
            "farm_specific_learning",
            "seasonal_adjustments",
            "model_retraining"
        ]
    }

"""
Personalization API Routes

API endpoints for advanced recommendation personalization and learning features.
"""

import logging
from typing import Dict, List, Optional, Any
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel, Field

try:
    from ..services.personalization_service import (
        PersonalizationService,
        UserProfile,
        FarmCharacteristics,
        personalization_service
    )
    from ..models.preference_models import (
        PreferenceProfile,
        PreferenceLearningRequest,
        RiskTolerance,
        ManagementStyle
    )
    from ..models.crop_variety_models import VarietyRecommendation
    from ..models.service_models import VarietyRecommendationRequest
except ImportError:
    from services.personalization_service import (
        PersonalizationService,
        UserProfile,
        FarmCharacteristics,
        personalization_service
    )
    from models.preference_models import (
        PreferenceProfile,
        PreferenceLearningRequest,
        RiskTolerance,
        ManagementStyle
    )
    from models.crop_variety_models import VarietyRecommendation
    from models.service_models import VarietyRecommendationRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/personalization", tags=["personalization"])


# Request/Response Models
class FarmCharacteristicsRequest(BaseModel):
    """Request model for farm characteristics."""
    farm_size_acres: float = Field(..., ge=0.1, le=10000, description="Farm size in acres")
    soil_type: str = Field(..., description="Primary soil type")
    climate_zone: str = Field(..., description="Climate zone")
    irrigation_available: bool = Field(default=False, description="Irrigation availability")
    equipment_level: str = Field(default="basic", description="Equipment level")
    labor_availability: str = Field(default="moderate", description="Labor availability")
    market_access: str = Field(default="local", description="Market access level")
    organic_certification: bool = Field(default=False, description="Organic certification")
    sustainability_focus: float = Field(default=0.5, ge=0.0, le=1.0, description="Sustainability focus")
    technology_adoption: float = Field(default=0.5, ge=0.0, le=1.0, description="Technology adoption")


class UserProfileRequest(BaseModel):
    """Request model for user profile."""
    user_id: UUID = Field(..., description="User identifier")
    farm_characteristics: FarmCharacteristicsRequest = Field(..., description="Farm characteristics")
    management_style: ManagementStyle = Field(..., description="Management style")
    risk_tolerance: RiskTolerance = Field(..., description="Risk tolerance")
    economic_goals: Dict[str, float] = Field(default_factory=dict, description="Economic goals")
    experience_level: str = Field(default="intermediate", description="Experience level")
    crop_preferences: List[str] = Field(default_factory=list, description="Crop preferences")
    sustainability_priorities: List[str] = Field(default_factory=list, description="Sustainability priorities")
    market_preferences: List[str] = Field(default_factory=list, description="Market preferences")


class PersonalizedRecommendationRequest(BaseModel):
    """Request model for personalized recommendations."""
    user_profile: UserProfileRequest = Field(..., description="User profile")
    base_recommendation_request: VarietyRecommendationRequest = Field(..., description="Base recommendation request")
    include_learning_insights: bool = Field(default=True, description="Include learning insights")


class FeedbackRequest(BaseModel):
    """Request model for user feedback."""
    user_id: UUID = Field(..., description="User identifier")
    recommendation_id: UUID = Field(..., description="Recommendation identifier")
    feedback_type: str = Field(..., description="Type of feedback")
    feedback_value: Any = Field(..., description="Feedback value")
    feedback_text: Optional[str] = Field(None, description="Optional feedback text")


class PersonalizationInsightsResponse(BaseModel):
    """Response model for personalization insights."""
    user_id: str = Field(..., description="User identifier")
    learning_insights: Dict[str, Any] = Field(..., description="Learning insights")
    personalization_stats: Dict[str, Any] = Field(..., description="Personalization statistics")
    recommendation_adaptation: Dict[str, Any] = Field(..., description="Adaptation status")
    generated_at: str = Field(..., description="Generation timestamp")


# Dependency injection
async def get_personalization_service() -> PersonalizationService:
    """Get personalization service instance."""
    return personalization_service


@router.post("/recommendations", response_model=List[VarietyRecommendation])
async def get_personalized_recommendations(
    request: PersonalizedRecommendationRequest,
    service: PersonalizationService = Depends(get_personalization_service)
):
    """
    Get personalized variety recommendations based on user profile and learning.
    
    This endpoint provides advanced personalization using:
    - Collaborative filtering for similar farmer recommendations
    - Content-based filtering for crop characteristics matching
    - Hybrid recommendation systems
    - User preference learning and adaptation
    - Farm characteristics integration
    - Management style and risk tolerance adaptation
    - Economic goals optimization
    """
    try:
        # Convert request to internal models
        farm_chars = FarmCharacteristics(
            farm_size_acres=request.user_profile.farm_characteristics.farm_size_acres,
            soil_type=request.user_profile.farm_characteristics.soil_type,
            climate_zone=request.user_profile.farm_characteristics.climate_zone,
            irrigation_available=request.user_profile.farm_characteristics.irrigation_available,
            equipment_level=request.user_profile.farm_characteristics.equipment_level,
            labor_availability=request.user_profile.farm_characteristics.labor_availability,
            market_access=request.user_profile.farm_characteristics.market_access,
            organic_certification=request.user_profile.farm_characteristics.organic_certification,
            sustainability_focus=request.user_profile.farm_characteristics.sustainability_focus,
            technology_adoption=request.user_profile.farm_characteristics.technology_adoption
        )
        
        user_profile = UserProfile(
            user_id=request.user_profile.user_id,
            farm_characteristics=farm_chars,
            management_style=request.user_profile.management_style,
            risk_tolerance=request.user_profile.risk_tolerance,
            economic_goals=request.user_profile.economic_goals,
            experience_level=request.user_profile.experience_level,
            crop_preferences=request.user_profile.crop_preferences,
            sustainability_priorities=request.user_profile.sustainability_priorities,
            market_preferences=request.user_profile.market_preferences
        )
        
        # Get base recommendations from variety service
        from ..services.variety_recommendation_service import VarietyRecommendationService
        variety_service = VarietyRecommendationService()
        
        # Convert request to internal format
        crop_data = {
            'id': request.base_recommendation_request.crop_id,
            'name': request.base_recommendation_request.crop_name
        }
        
        regional_context = {
            'location_data': request.base_recommendation_request.location_data,
            'soil_conditions': request.base_recommendation_request.soil_conditions
        }
        
        farmer_preferences = {
            'farming_objectives': request.base_recommendation_request.farming_objectives,
            'production_system': request.base_recommendation_request.production_system,
            'available_equipment': request.base_recommendation_request.available_equipment,
            'yield_priority_weight': request.base_recommendation_request.yield_priority_weight,
            'quality_priority_weight': request.base_recommendation_request.quality_priority_weight,
            'risk_management_weight': request.base_recommendation_request.risk_management_weight
        }
        
        base_recommendations = await variety_service.recommend_varieties(
            crop_data, regional_context, farmer_preferences
        )
        
        # Apply personalization
        personalized_recommendations = await service.personalize_recommendations(
            user_profile, base_recommendations
        )
        
        logger.info(f"Generated {len(personalized_recommendations)} personalized recommendations for user {user_profile.user_id}")
        return personalized_recommendations
        
    except Exception as e:
        logger.error(f"Error generating personalized recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate personalized recommendations: {str(e)}")


@router.post("/feedback", response_model=Dict[str, Any])
async def submit_feedback(
    request: FeedbackRequest,
    service: PersonalizationService = Depends(get_personalization_service)
):
    """
    Submit user feedback for learning and recommendation improvement.
    
    This endpoint allows users to provide feedback on recommendations,
    which is used to improve future personalized recommendations through
    machine learning algorithms.
    """
    try:
        success = await service.learn_from_feedback(
            user_id=request.user_id,
            recommendation_id=request.recommendation_id,
            feedback_type=request.feedback_type,
            feedback_value=request.feedback_value,
            feedback_text=request.feedback_text
        )
        
        if success:
            return {
                "success": True,
                "message": "Feedback recorded successfully",
                "user_id": str(request.user_id),
                "recommendation_id": str(request.recommendation_id),
                "feedback_type": request.feedback_type,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to record feedback")
            
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")


@router.get("/insights/{user_id}", response_model=PersonalizationInsightsResponse)
async def get_personalization_insights(
    user_id: UUID,
    service: PersonalizationService = Depends(get_personalization_service)
):
    """
    Get personalization and learning insights for a user.
    
    This endpoint provides insights about:
    - User learning progress and confidence
    - Personalization algorithm status
    - Recommendation adaptation capabilities
    - Interaction patterns and preferences
    """
    try:
        insights = await service.get_personalization_insights(user_id)
        
        if not insights:
            raise HTTPException(status_code=404, detail="No insights found for user")
        
        return PersonalizationInsightsResponse(**insights)
        
    except Exception as e:
        logger.error(f"Error getting personalization insights: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get insights: {str(e)}")


@router.post("/learn", response_model=Dict[str, Any])
async def trigger_preference_learning(
    request: PreferenceLearningRequest,
    service: PersonalizationService = Depends(get_personalization_service)
):
    """
    Trigger preference learning from user signals.
    
    This endpoint allows manual triggering of preference learning
    based on user interaction signals for immediate adaptation.
    """
    try:
        # Convert signals to interactions
        interactions = []
        for signal in request.signals:
            interaction = {
                'user_id': request.user_id,
                'interaction_type': signal.signal_type,
                'crop_id': str(signal.crop_id),
                'interaction_data': signal.context or {},
                'timestamp': datetime.now()
            }
            interactions.append(interaction)
        
        # Trigger learning
        from ..services.preference_learning_service import UserInteraction
        for interaction_data in interactions:
            interaction = UserInteraction(**interaction_data)
            await service.preference_learning_service.track_user_interaction(interaction)
        
        return {
            "success": True,
            "message": "Preference learning triggered successfully",
            "user_id": str(request.user_id),
            "signals_processed": len(request.signals),
            "learning_rate": request.learning_rate,
            "decay_factor": request.decay_factor,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error triggering preference learning: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to trigger learning: {str(e)}")


@router.get("/status/{user_id}")
async def get_personalization_status(
    user_id: UUID,
    service: PersonalizationService = Depends(get_personalization_service)
):
    """
    Get personalization status and readiness for a user.
    
    This endpoint provides information about:
    - Whether personalization is ready for the user
    - Which algorithms are active
    - Learning progress and confidence levels
    """
    try:
        insights = await service.get_personalization_insights(user_id)
        
        if not insights:
            return {
                "user_id": str(user_id),
                "personalization_ready": False,
                "message": "Insufficient data for personalization",
                "required_interactions": service.min_interactions_for_personalization,
                "current_interactions": 0
            }
        
        personalization_stats = insights.get('personalization_stats', {})
        recommendation_adaptation = insights.get('recommendation_adaptation', {})
        
        return {
            "user_id": str(user_id),
            "personalization_ready": personalization_stats.get('personalization_ready', False),
            "current_interactions": personalization_stats.get('total_interactions', 0),
            "required_interactions": service.min_interactions_for_personalization,
            "active_algorithms": {
                "collaborative_filtering": recommendation_adaptation.get('collaborative_filtering_active', False),
                "content_based_filtering": recommendation_adaptation.get('content_based_filtering_active', False),
                "preference_learning": recommendation_adaptation.get('preference_learning_active', False),
                "farm_characteristics": recommendation_adaptation.get('farm_characteristics_active', False)
            },
            "learning_confidence": personalization_stats.get('learning_confidence', 0.0),
            "learned_preferences": insights.get('learning_insights', {}).get('learned_preferences_count', 0),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting personalization status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for personalization service."""
    return {
        "status": "healthy",
        "service": "personalization",
        "timestamp": datetime.now().isoformat(),
        "features": [
            "collaborative_filtering",
            "content_based_filtering", 
            "hybrid_recommendations",
            "preference_learning",
            "farm_characteristics_matching",
            "feedback_integration"
        ]
    }
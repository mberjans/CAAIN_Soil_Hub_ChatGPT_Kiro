"""
API routes for crop response and application method optimization.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
import logging

from ..models.application_models import (
    ApplicationMethodType, CropRequirements, FieldConditions
)
from ..services.crop_integration_service import CropType, GrowthStage
from ..services.crop_response_service import (
    CropResponseService, MethodEffectivenessRanking, YieldImpactPrediction
)
from ..services.application_method_service import ApplicationMethodService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/crop-response", tags=["crop-response"])


# Dependency injection
async def get_crop_response_service() -> CropResponseService:
    return CropResponseService()


async def get_application_method_service() -> ApplicationMethodService:
    return ApplicationMethodService()


@router.post("/optimize-methods", response_model=List[Dict[str, Any]])
async def optimize_application_methods(
    crop_type: str = Query(..., description="Type of crop"),
    available_methods: List[str] = Query(..., description="Available application methods"),
    field_conditions: Dict[str, Any] = Query(..., description="Field and environmental conditions"),
    crop_requirements: Dict[str, Any] = Query(..., description="Crop-specific requirements"),
    service: CropResponseService = Depends(get_crop_response_service)
):
    """
    Optimize application methods based on crop response analysis.
    
    This endpoint analyzes crop response for different fertilizer application methods
    and ranks them by effectiveness for specific field conditions and crop requirements.
    
    Agricultural Use Cases:
    - Method selection for maximum yield response
    - Efficiency optimization for nutrient use
    - Cost-effectiveness analysis for application methods
    - Environmental impact assessment
    """
    try:
        # Convert string inputs to enums
        crop_enum = CropType(crop_type.lower())
        method_enums = [ApplicationMethodType(method.lower()) for method in available_methods]
        
        # Create crop requirements object
        crop_req = CropRequirements(
            crop_type=crop_type,
            growth_stage=crop_requirements.get("growth_stage", "V6"),
            target_yield=crop_requirements.get("target_yield"),
            nutrient_requirements=crop_requirements.get("nutrient_requirements", {}),
            application_timing_preferences=crop_requirements.get("application_timing_preferences", [])
        )
        
        # Get method effectiveness rankings
        rankings = await service.rank_method_effectiveness(
            crop_enum, method_enums, field_conditions, crop_req
        )
        
        # Convert to response format
        response = []
        for ranking in rankings:
            response.append({
                "method": ranking.method_type.value,
                "overall_score": ranking.overall_score,
                "yield_impact": ranking.yield_impact,
                "efficiency_score": ranking.efficiency_score,
                "cost_effectiveness": ranking.cost_effectiveness,
                "environmental_score": ranking.environmental_score,
                "labor_efficiency": ranking.labor_efficiency,
                "advantages": ranking.advantages,
                "limitations": ranking.limitations,
                "optimal_conditions": ranking.optimal_conditions,
                "application_guidance": ranking.application_guidance
            })
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        logger.error(f"Error optimizing application methods: {e}")
        raise HTTPException(status_code=500, detail="Failed to optimize application methods")


@router.post("/predict-yield-impact", response_model=Dict[str, Any])
async def predict_yield_impact(
    crop_type: str = Query(..., description="Type of crop"),
    method_type: str = Query(..., description="Application method type"),
    baseline_yield: float = Query(..., description="Baseline yield without fertilizer"),
    application_rate: float = Query(..., description="Application rate"),
    field_conditions: Dict[str, Any] = Query(..., description="Field and environmental conditions"),
    service: CropResponseService = Depends(get_crop_response_service)
):
    """
    Predict yield impact for a specific application method.
    
    This endpoint predicts the yield impact of using a specific fertilizer application
    method, including yield increase, revenue impact, and risk factors.
    
    Agricultural Use Cases:
    - Yield prediction for method selection
    - Economic impact assessment
    - Risk factor identification
    - ROI calculation for fertilizer investment
    """
    try:
        # Convert string inputs to enums
        crop_enum = CropType(crop_type.lower())
        method_enum = ApplicationMethodType(method_type.lower())
        
        # Get yield impact prediction
        prediction = await service.predict_yield_impact(
            crop_enum, method_enum, baseline_yield, application_rate, field_conditions
        )
        
        # Convert to response format
        response = {
            "method": prediction.method_type.value,
            "crop_type": prediction.crop_type.value,
            "baseline_yield": prediction.baseline_yield,
            "predicted_yield": prediction.predicted_yield,
            "yield_increase_percent": prediction.yield_increase_percent,
            "yield_range": prediction.yield_range,
            "confidence": prediction.confidence,
            "contributing_factors": prediction.contributing_factors,
            "risk_factors": prediction.risk_factors,
            "revenue_impact_per_acre": prediction.revenue_impact_per_acre,
            "cost_per_unit_yield": prediction.cost_per_unit_yield
        }
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        logger.error(f"Error predicting yield impact: {e}")
        raise HTTPException(status_code=500, detail="Failed to predict yield impact")


@router.post("/compare-methods", response_model=Dict[str, Any])
async def compare_method_effectiveness(
    crop_type: str = Query(..., description="Type of crop"),
    methods_to_compare: List[str] = Query(..., description="Methods to compare"),
    field_conditions: Dict[str, Any] = Query(..., description="Field and environmental conditions"),
    crop_requirements: Dict[str, Any] = Query(..., description="Crop-specific requirements"),
    service: ApplicationMethodService = Depends(get_application_method_service)
):
    """
    Compare effectiveness of multiple application methods.
    
    This endpoint provides a comprehensive comparison of multiple fertilizer application
    methods, including rankings, yield predictions, and recommendations.
    
    Agricultural Use Cases:
    - Side-by-side method comparison
    - Decision support for method selection
    - Trade-off analysis between different approaches
    - Comprehensive effectiveness assessment
    """
    try:
        # Convert string inputs to enums
        crop_enum = CropType(crop_type.lower())
        method_enums = [ApplicationMethodType(method.lower()) for method in methods_to_compare]
        
        # Create crop requirements object
        crop_req = CropRequirements(
            crop_type=crop_type,
            growth_stage=crop_requirements.get("growth_stage", "V6"),
            target_yield=crop_requirements.get("target_yield"),
            nutrient_requirements=crop_requirements.get("nutrient_requirements", {}),
            application_timing_preferences=crop_requirements.get("application_timing_preferences", [])
        )
        
        # Get method effectiveness comparison
        comparison = await service.get_method_effectiveness_comparison(
            crop_enum, method_enums, field_conditions, crop_req
        )
        
        return comparison
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        logger.error(f"Error comparing method effectiveness: {e}")
        raise HTTPException(status_code=500, detail="Failed to compare method effectiveness")


@router.get("/crop-response-data/{crop_type}")
async def get_crop_response_data(
    crop_type: str,
    method_type: Optional[str] = Query(None, description="Specific method type to retrieve"),
    service: CropResponseService = Depends(get_crop_response_service)
):
    """
    Get crop response data for specific crop and method combinations.
    
    This endpoint provides access to the underlying crop response database,
    showing how different crops respond to various application methods.
    
    Agricultural Use Cases:
    - Research and analysis of crop responses
    - Method suitability assessment
    - Educational purposes
    - Data validation and verification
    """
    try:
        crop_enum = CropType(crop_type.lower())
        
        if method_type:
            # Return data for specific method
            method_enum = ApplicationMethodType(method_type.lower())
            response_data = service._get_base_response_data(crop_enum, method_enum)
            
            if not response_data:
                raise HTTPException(status_code=404, detail=f"No response data for {crop_type} with {method_type}")
            
            return {
                "crop_type": response_data.crop_type.value,
                "method_type": response_data.method_type.value,
                "growth_stage": response_data.growth_stage.value,
                "yield_response": response_data.yield_response,
                "nutrient_efficiency": response_data.nutrient_efficiency,
                "growth_rate_response": response_data.growth_rate_response,
                "stress_tolerance": response_data.stress_tolerance,
                "quality_improvement": response_data.quality_improvement,
                "confidence_score": response_data.confidence_score,
                "data_sources": response_data.data_sources
            }
        else:
            # Return all methods for crop
            crop_data = service.response_database.get(crop_enum, {})
            response = {}
            
            for method, data in crop_data.items():
                response[method.value] = {
                    "yield_response": data.yield_response,
                    "nutrient_efficiency": data.nutrient_efficiency,
                    "growth_rate_response": data.growth_rate_response,
                    "stress_tolerance": data.stress_tolerance,
                    "quality_improvement": data.quality_improvement,
                    "confidence_score": data.confidence_score,
                    "data_sources": data.data_sources
                }
            
            return {
                "crop_type": crop_type,
                "available_methods": list(response.keys()),
                "response_data": response
            }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        logger.error(f"Error getting crop response data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get crop response data")


@router.get("/health")
async def health_check():
    """Health check endpoint for crop response service."""
    return {"status": "healthy", "service": "crop-response-optimization"}
"""
Fertilizer Type Selection API Routes

FastAPI routes for fertilizer type selection recommendations.
Implements US-006: Fertilizer Type Selection functionality.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

try:
    from ..models.fertilizer_models import (
        FertilizerTypeSelectionRequest,
        FertilizerTypeSelectionResponse,
        FertilizerComparisonRequest,
        FertilizerComparisonResponse,
        FertilizerProduct,
        FertilizerRecommendation
    )
    from ..services.fertilizer_type_selection_service import FertilizerTypeSelectionService
except ImportError:
    from models.fertilizer_models import (
        FertilizerTypeSelectionRequest,
        FertilizerTypeSelectionResponse,
        FertilizerComparisonRequest,
        FertilizerComparisonResponse,
        FertilizerProduct,
        FertilizerRecommendation
    )
    from services.fertilizer_type_selection_service import FertilizerTypeSelectionService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/fertilizer", tags=["fertilizer-type-selection"])

# Initialize fertilizer type selection service
fertilizer_service = FertilizerTypeSelectionService()


@router.post("/type-selection", response_model=FertilizerTypeSelectionResponse)
async def get_fertilizer_type_recommendations(request: FertilizerTypeSelectionRequest):
    """
    Get fertilizer type selection recommendations based on farmer priorities and constraints.
    
    This endpoint implements US-006: Fertilizer Type Selection
    "Should I invest in organic, synthetic, or slow-release fertilizers?"
    
    Agricultural Logic:
    - Analyzes farmer priorities (cost, soil health, quick results)
    - Considers budget constraints and farm size
    - Evaluates equipment compatibility
    - Compares organic, synthetic, and slow-release options
    - Provides cost-effectiveness analysis
    - Includes environmental impact assessment
    
    Args:
        request: Fertilizer type selection request with priorities and constraints
        
    Returns:
        Detailed fertilizer type recommendations with comparisons
    """
    try:
        logger.info(f"Processing fertilizer type selection request: {request.request_id}")
        
        # Generate fertilizer type recommendations
        recommendations = await fertilizer_service.get_fertilizer_type_recommendations(
            priorities=request.priorities,
            constraints=request.constraints,
            soil_data=request.soil_data,
            crop_data=request.crop_data,
            farm_profile=request.farm_profile
        )
        
        # Create response
        response = FertilizerTypeSelectionResponse(
            request_id=request.request_id,
            generated_at=datetime.utcnow(),
            recommendations=recommendations,
            confidence_score=fertilizer_service.calculate_overall_confidence(recommendations),
            comparison_summary=fertilizer_service.generate_comparison_summary(recommendations),
            cost_analysis=fertilizer_service.generate_cost_analysis(recommendations, request.constraints),
            environmental_impact=fertilizer_service.assess_environmental_impact(recommendations),
            implementation_guidance=fertilizer_service.generate_implementation_guidance(recommendations)
        )
        
        logger.info(f"Generated {len(recommendations)} fertilizer type recommendations")
        return response
        
    except Exception as e:
        logger.error(f"Error generating fertilizer type recommendations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating fertilizer type recommendations: {str(e)}"
        )


@router.get("/types", response_model=List[FertilizerProduct])
async def get_available_fertilizer_types(
    fertilizer_type: Optional[str] = None,
    organic_only: Optional[bool] = False,
    max_cost_per_unit: Optional[float] = None
):
    """
    Get list of available fertilizer types with filtering options.
    
    Args:
        fertilizer_type: Filter by fertilizer type (organic, synthetic, slow_release)
        organic_only: Return only organic-certified fertilizers
        max_cost_per_unit: Maximum cost per unit filter
        
    Returns:
        List of available fertilizer products
    """
    try:
        logger.info(f"Retrieving fertilizer types with filters: type={fertilizer_type}, organic={organic_only}")
        
        fertilizer_types = await fertilizer_service.get_available_fertilizer_types(
            fertilizer_type=fertilizer_type,
            organic_only=organic_only,
            max_cost_per_unit=max_cost_per_unit
        )
        
        logger.info(f"Retrieved {len(fertilizer_types)} fertilizer types")
        return fertilizer_types
        
    except Exception as e:
        logger.error(f"Error retrieving fertilizer types: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving fertilizer types: {str(e)}"
        )


@router.post("/comparison", response_model=FertilizerComparisonResponse)
async def compare_fertilizer_options(request: FertilizerComparisonRequest):
    """
    Compare specific fertilizer options side-by-side.
    
    Args:
        request: Comparison request with specific fertilizer products to compare
        
    Returns:
        Detailed comparison of fertilizer options
    """
    try:
        logger.info(f"Processing fertilizer comparison request: {request.request_id}")
        
        comparison = await fertilizer_service.compare_fertilizer_options(
            fertilizer_ids=request.fertilizer_ids,
            comparison_criteria=request.comparison_criteria,
            farm_context=request.farm_context
        )
        
        response = FertilizerComparisonResponse(
            request_id=request.request_id,
            generated_at=datetime.utcnow(),
            comparison_results=comparison,
            recommendation=fertilizer_service.get_comparison_recommendation(comparison),
            decision_factors=fertilizer_service.identify_decision_factors(comparison)
        )
        
        logger.info(f"Generated comparison for {len(request.fertilizer_ids)} fertilizer options")
        return response
        
    except Exception as e:
        logger.error(f"Error generating fertilizer comparison: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating fertilizer comparison: {str(e)}"
        )


@router.get("/equipment-compatibility/{equipment_type}")
async def get_equipment_compatibility(equipment_type: str):
    """
    Get fertilizer compatibility information for specific equipment.
    
    Args:
        equipment_type: Type of equipment (spreader, sprayer, drill, etc.)
        
    Returns:
        Equipment compatibility information
    """
    try:
        logger.info(f"Retrieving equipment compatibility for: {equipment_type}")
        
        compatibility = await fertilizer_service.get_equipment_compatibility(equipment_type)
        
        return {
            "equipment_type": equipment_type,
            "compatible_fertilizers": compatibility["compatible_fertilizers"],
            "application_methods": compatibility["application_methods"],
            "limitations": compatibility["limitations"],
            "recommendations": compatibility["recommendations"]
        }
        
    except Exception as e:
        logger.error(f"Error retrieving equipment compatibility: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving equipment compatibility: {str(e)}"
        )


@router.post("/cost-analysis")
async def analyze_fertilizer_costs(
    fertilizer_ids: List[str],
    farm_size_acres: float,
    application_rates: Dict[str, float],
    current_prices: Optional[Dict[str, float]] = None
):
    """
    Analyze costs for specific fertilizer options.
    
    Args:
        fertilizer_ids: List of fertilizer product IDs to analyze
        farm_size_acres: Farm size for total cost calculation
        application_rates: Application rates for each fertilizer (lbs/acre)
        current_prices: Current local prices (optional)
        
    Returns:
        Detailed cost analysis
    """
    try:
        logger.info(f"Analyzing costs for {len(fertilizer_ids)} fertilizer options")
        
        cost_analysis = await fertilizer_service.analyze_fertilizer_costs(
            fertilizer_ids=fertilizer_ids,
            farm_size_acres=farm_size_acres,
            application_rates=application_rates,
            current_prices=current_prices
        )
        
        return {
            "total_costs": cost_analysis["total_costs"],
            "cost_per_acre": cost_analysis["cost_per_acre"],
            "cost_per_nutrient_unit": cost_analysis["cost_per_nutrient_unit"],
            "roi_analysis": cost_analysis["roi_analysis"],
            "cost_comparison": cost_analysis["cost_comparison"],
            "recommendations": cost_analysis["recommendations"]
        }
        
    except Exception as e:
        logger.error(f"Error analyzing fertilizer costs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing fertilizer costs: {str(e)}"
        )


@router.get("/environmental-impact/{fertilizer_id}")
async def get_environmental_impact(fertilizer_id: str):
    """
    Get environmental impact assessment for a specific fertilizer.
    
    Args:
        fertilizer_id: Fertilizer product ID
        
    Returns:
        Environmental impact assessment
    """
    try:
        logger.info(f"Retrieving environmental impact for fertilizer: {fertilizer_id}")
        
        impact_assessment = await fertilizer_service.get_environmental_impact(fertilizer_id)
        
        return {
            "fertilizer_id": fertilizer_id,
            "carbon_footprint": impact_assessment["carbon_footprint"],
            "water_quality_impact": impact_assessment["water_quality_impact"],
            "soil_health_impact": impact_assessment["soil_health_impact"],
            "biodiversity_impact": impact_assessment["biodiversity_impact"],
            "sustainability_score": impact_assessment["sustainability_score"],
            "mitigation_strategies": impact_assessment["mitigation_strategies"]
        }
        
    except Exception as e:
        logger.error(f"Error retrieving environmental impact: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving environmental impact: {str(e)}"
        )
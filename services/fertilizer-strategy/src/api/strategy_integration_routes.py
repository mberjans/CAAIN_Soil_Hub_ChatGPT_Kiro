"""
REST API routes for fertilizer-strategy service integration.

This module provides REST API endpoints that enable other services (particularly
fertilizer-timing) to access fertilizer-strategy functionality via HTTP rather
than direct Python imports.

Endpoints:
- POST /api/v1/strategy/timing-recommendations - Get timing recommendations
- POST /api/v1/strategy/equipment-compatibility - Check equipment compatibility
- GET  /api/v1/strategy/pricing-data - Get current fertilizer prices
- POST /api/v1/strategy/type-selection - Get fertilizer type recommendations
"""

import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from models.timing_optimization_models import (
    TimingOptimizationRequest,
    TimingOptimizationResult,
)
from services.timing_optimization_service import FertilizerTimingOptimizer
from services.price_tracking_service import PriceTrackingService
from services.type_selection_service import FertilizerTypeSelector
from services.integrated_workflow_service import IntegratedWorkflowService

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize service instances
timing_optimizer = FertilizerTimingOptimizer()
price_tracker = PriceTrackingService()
integrated_workflow = IntegratedWorkflowService()


# Request/Response Models for Equipment Compatibility
class EquipmentCompatibilityRequest(BaseModel):
    """Request model for equipment compatibility check."""
    fertilizer_type: str = Field(..., description="Type of fertilizer")
    application_method: str = Field(..., description="Application method")
    equipment_list: List[str] = Field(..., description="List of available equipment IDs")


class EquipmentCompatibilityResponse(BaseModel):
    """Response model for equipment compatibility."""
    compatible_equipment: List[str] = Field(default_factory=list)
    incompatible_equipment: List[str] = Field(default_factory=list)
    compatibility_details: Dict[str, Dict[str, any]] = Field(default_factory=dict)


# Request/Response Models for Type Selection
class FertilizerTypeSelectionRequest(BaseModel):
    """Request model for fertilizer type selection."""
    nutrient_requirements: Dict[str, float] = Field(
        ..., description="Required nutrients (N, P, K, S, etc.)"
    )
    soil_characteristics: Dict[str, any] = Field(
        ..., description="Soil properties and conditions"
    )
    crop_type: str = Field(..., description="Type of crop being grown")


class FertilizerRecommendation(BaseModel):
    """Individual fertilizer recommendation."""
    fertilizer_type: str
    compatibility_score: float = Field(ge=0, le=1)
    nutrient_content: Dict[str, float]
    application_rate: Optional[float] = None
    estimated_cost: Optional[float] = None
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)


class FertilizerTypeSelectionResponse(BaseModel):
    """Response model for type selection."""
    recommended_types: List[FertilizerRecommendation]
    ranking_criteria: List[str] = Field(default_factory=list)


# Pricing Data Models
class PriceDataResponse(BaseModel):
    """Response model for pricing data."""
    prices: Dict[str, Dict[str, any]] = Field(
        default_factory=dict,
        description="Fertilizer prices by type"
    )
    data_source: str = Field(default="internal")
    timestamp: str = Field(..., description="ISO timestamp of price data")
    regional_availability: Optional[Dict[str, bool]] = None


@router.post(
    "/api/v1/strategy/timing-recommendations",
    response_model=TimingOptimizationResult,
    summary="Get timing recommendations",
    description="Request optimal fertilizer timing recommendations based on crop, weather, and soil conditions"
)
async def get_timing_recommendations(
    request: TimingOptimizationRequest
) -> TimingOptimizationResult:
    """
    Get timing recommendations for fertilizer applications.

    This endpoint processes timing optimization requests and returns comprehensive
    recommendations including optimal application dates, weather windows, and
    split application plans.

    Args:
        request: Timing optimization request parameters

    Returns:
        TimingOptimizationResult: Comprehensive timing recommendations

    Raises:
        HTTPException: On processing errors
    """
    try:
        logger.info(
            f"Processing timing recommendation request for crop {request.crop_type} "
            f"at location ({request.location.latitude}, {request.location.longitude})"
        )

        # Execute timing optimization
        result = await timing_optimizer.optimize_timing(request)

        logger.info(
            f"Generated {len(result.optimal_timings)} timing recommendations "
            f"with confidence {result.confidence_score:.2f}"
        )

        return result

    except ValueError as e:
        logger.warning(f"Invalid request parameters: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Timing optimization failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process timing optimization: {str(e)}"
        )


@router.post(
    "/api/v1/strategy/equipment-compatibility",
    response_model=EquipmentCompatibilityResponse,
    summary="Check equipment compatibility",
    description="Verify which equipment is compatible with specified fertilizer and application method"
)
async def check_equipment_compatibility(
    request: EquipmentCompatibilityRequest
) -> EquipmentCompatibilityResponse:
    """
    Check equipment compatibility for fertilizer application.

    Determines which equipment from the provided list is compatible with the
    specified fertilizer type and application method.

    Args:
        request: Equipment compatibility check parameters

    Returns:
        EquipmentCompatibilityResponse: Compatible and incompatible equipment lists

    Raises:
        HTTPException: On processing errors
    """
    try:
        logger.debug(
            f"Checking equipment compatibility for {request.fertilizer_type} "
            f"using {request.application_method}"
        )

        # Equipment compatibility logic
        # This is a simplified implementation - expand based on actual equipment database
        compatible = []
        incompatible = []
        details = {}

        # Define compatibility rules
        compatibility_matrix = {
            "broadcast": ["spreader", "broadcast_spreader", "spinner_spreader"],
            "band": ["bander", "sidedress_applicator", "row_applicator"],
            "injection": ["injector", "knife_applicator", "coulter_applicator"],
            "foliar": ["sprayer", "boom_sprayer", "aerial_sprayer"],
        }

        compatible_equipment_types = compatibility_matrix.get(
            request.application_method.lower(), []
        )

        for equipment_id in request.equipment_list:
            # Simple check - in real implementation, query equipment database
            equipment_type = equipment_id.split("_")[0].lower()
            is_compatible = equipment_type in compatible_equipment_types

            if is_compatible:
                compatible.append(equipment_id)
                details[equipment_id] = {
                    "compatible": True,
                    "reason": f"Compatible with {request.application_method} application"
                }
            else:
                incompatible.append(equipment_id)
                details[equipment_id] = {
                    "compatible": False,
                    "reason": f"Not designed for {request.application_method} application"
                }

        return EquipmentCompatibilityResponse(
            compatible_equipment=compatible,
            incompatible_equipment=incompatible,
            compatibility_details=details
        )

    except Exception as e:
        logger.error(f"Equipment compatibility check failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Equipment compatibility check failed: {str(e)}"
        )


@router.get(
    "/api/v1/strategy/pricing-data",
    response_model=PriceDataResponse,
    summary="Get current fertilizer prices",
    description="Retrieve current fertilizer pricing data, optionally filtered by type and location"
)
async def get_pricing_data(
    fertilizer_type: Optional[str] = Query(None, description="Specific fertilizer type"),
    latitude: Optional[float] = Query(None, description="Location latitude for regional pricing"),
    longitude: Optional[float] = Query(None, description="Location longitude for regional pricing")
) -> PriceDataResponse:
    """
    Get current fertilizer pricing data.

    Retrieves up-to-date fertilizer prices, optionally filtered by type and
    location for regional pricing variations.

    Args:
        fertilizer_type: Optional filter for specific fertilizer
        latitude: Optional location latitude
        longitude: Optional location longitude

    Returns:
        PriceDataResponse: Current pricing data

    Raises:
        HTTPException: On data retrieval errors
    """
    try:
        from datetime import datetime

        logger.debug(f"Fetching pricing data for type={fertilizer_type}, location=({latitude}, {longitude})")

        # Get current prices from price tracking service
        # This is a simplified implementation - integrate with actual price service
        prices = {}

        # Default price data structure
        fertilizer_types = ["urea", "MAP", "DAP", "potash", "AMS"] if not fertilizer_type else [fertilizer_type]

        for fert_type in fertilizer_types:
            # Placeholder pricing logic - replace with actual price service integration
            base_prices = {
                "urea": 450.0,
                "MAP": 620.0,
                "DAP": 680.0,
                "potash": 520.0,
                "AMS": 380.0,
            }

            price = base_prices.get(fert_type.upper(), 500.0)

            # Regional adjustment if location provided
            if latitude is not None and longitude is not None:
                # Simple regional factor - expand with actual regional pricing
                regional_factor = 1.0 + (abs(latitude) / 1000.0)
                price *= regional_factor

            prices[fert_type] = {
                "price_per_unit": round(price, 2),
                "currency": "USD",
                "unit": "ton",
                "data_source": "internal",
                "last_updated": datetime.utcnow().isoformat(),
            }

        return PriceDataResponse(
            prices=prices,
            data_source="internal",
            timestamp=datetime.utcnow().isoformat(),
        )

    except Exception as e:
        logger.error(f"Failed to retrieve pricing data: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Pricing data retrieval failed: {str(e)}"
        )


@router.post(
    "/api/v1/strategy/type-selection",
    response_model=FertilizerTypeSelectionResponse,
    summary="Get fertilizer type recommendations",
    description="Recommend optimal fertilizer types based on nutrient requirements and soil conditions"
)
async def recommend_fertilizer_type(
    request: FertilizerTypeSelectionRequest
) -> FertilizerTypeSelectionResponse:
    """
    Recommend optimal fertilizer types.

    Analyzes nutrient requirements, soil characteristics, and crop type to
    recommend the most suitable fertilizer types.

    Args:
        request: Type selection request parameters

    Returns:
        FertilizerTypeSelectionResponse: Ranked fertilizer recommendations

    Raises:
        HTTPException: On processing errors
    """
    try:
        logger.debug(f"Generating fertilizer type recommendations for {request.crop_type}")

        # Simplified recommendation logic - expand with actual type selection service
        recommendations = []

        # Extract nutrient needs
        n_need = request.nutrient_requirements.get("N", 0)
        p_need = request.nutrient_requirements.get("P", 0)
        k_need = request.nutrient_requirements.get("K", 0)

        # Recommendation logic based on nutrient ratios
        if n_need > 0:
            recommendations.append(FertilizerRecommendation(
                fertilizer_type="Urea",
                compatibility_score=0.9,
                nutrient_content={"N": 46.0, "P": 0, "K": 0},
                pros=["High nitrogen content", "Cost-effective", "Widely available"],
                cons=["Volatilization risk", "Requires incorporation"]
            ))

        if p_need > 0:
            recommendations.append(FertilizerRecommendation(
                fertilizer_type="MAP",
                compatibility_score=0.85,
                nutrient_content={"N": 11.0, "P": 52.0, "K": 0},
                pros=["Good P source", "Provides some N", "Low salt index"],
                cons=["Higher cost per lb P", "Can acidify soil"]
            ))

        if k_need > 0:
            recommendations.append(FertilizerRecommendation(
                fertilizer_type="Potash",
                compatibility_score=0.88,
                nutrient_content={"N": 0, "P": 0, "K": 60.0},
                pros=["High K content", "Improves crop quality"],
                cons=["Can cause salt stress", "Moderately expensive"]
            ))

        # Sort by compatibility score
        recommendations.sort(key=lambda x: x.compatibility_score, reverse=True)

        return FertilizerTypeSelectionResponse(
            recommended_types=recommendations,
            ranking_criteria=["nutrient_match", "cost_effectiveness", "soil_compatibility"]
        )

    except Exception as e:
        logger.error(f"Fertilizer type recommendation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Type selection failed: {str(e)}"
        )


# Integrated Workflow Request/Response Models
class IntegratedStrategyTimingRequest(BaseModel):
    """Request model for integrated strategy and timing optimization."""
    crop_type: str = Field(..., description="Type of crop being grown")
    field_size: float = Field(..., gt=0, description="Field size in acres")
    location: Dict[str, float] = Field(..., description="Location coordinates (latitude, longitude)")
    planting_date: str = Field(..., description="ISO format planting date")
    soil_characteristics: Dict[str, any] = Field(..., description="Soil properties")
    nutrient_requirements: Dict[str, float] = Field(..., description="Required nutrients")
    budget: Optional[float] = Field(None, description="Budget constraint")
    available_equipment: Optional[List[str]] = Field(None, description="Available equipment IDs")
    labor_availability: Optional[Dict[str, any]] = None
    environmental_constraints: Optional[Dict[str, any]] = None


class CompleteFertilizerPlanRequest(BaseModel):
    """Request model for complete fertilizer plan creation."""
    crop_type: str = Field(..., description="Type of crop")
    field_size: float = Field(..., gt=0, description="Field size in acres")
    location: Dict[str, float] = Field(..., description="Location coordinates")
    planting_date: str = Field(..., description="ISO format planting date")
    harvest_date: str = Field(..., description="ISO format harvest date")
    soil_test_results: Dict[str, any] = Field(..., description="Soil test data")
    yield_goal: float = Field(..., gt=0, description="Target yield")
    budget: Optional[float] = None
    risk_tolerance: str = Field(default="moderate", description="Risk tolerance: low, moderate, high")


class OptimizeAndScheduleRequest(BaseModel):
    """Request model for optimize and schedule workflow."""
    crop_type: str = Field(..., description="Type of crop")
    field_size: float = Field(..., gt=0, description="Field size in acres")
    location: Dict[str, float] = Field(..., description="Location coordinates")
    planting_date: str = Field(..., description="ISO format planting date")
    soil_characteristics: Dict[str, any] = Field(..., description="Soil properties")
    nutrient_requirements: Dict[str, float] = Field(..., description="Required nutrients")
    scheduling_constraints: Optional[Dict[str, any]] = None


@router.post(
    "/api/v1/integrated/strategy-with-timing",
    summary="Get optimized strategy with timing recommendations",
    description="Integrate fertilizer strategy optimization with timing recommendations"
)
async def get_integrated_strategy_with_timing(
    request: IntegratedStrategyTimingRequest
) -> Dict[str, any]:
    """
    Get optimized fertilizer strategy with integrated timing recommendations.

    This endpoint combines:
    - Strategy optimization (fertilizer selection, rates, costs)
    - Timing optimization (application windows, weather considerations)
    - Seasonal calendar generation
    - Price analysis and cost projections

    Args:
        request: Integrated optimization request parameters

    Returns:
        Dict containing integrated strategy and timing results

    Raises:
        HTTPException: On processing errors
    """
    try:
        logger.info(
            f"Processing integrated strategy/timing request for {request.crop_type}"
        )

        result = await integrated_workflow.optimize_strategy_with_timing(
            crop_type=request.crop_type,
            field_size=request.field_size,
            location=request.location,
            planting_date=request.planting_date,
            soil_characteristics=request.soil_characteristics,
            nutrient_requirements=request.nutrient_requirements,
            budget=request.budget,
            available_equipment=request.available_equipment,
            labor_availability=request.labor_availability,
            environmental_constraints=request.environmental_constraints,
        )

        logger.info(
            f"Integrated optimization complete: "
            f"{result['summary']['application_count']} applications"
        )

        return result

    except ValueError as e:
        logger.warning(f"Invalid request parameters: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Integrated optimization failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process integrated optimization: {str(e)}"
        )


@router.post(
    "/api/v1/integrated/complete-fertilizer-plan",
    summary="Create complete fertilizer plan",
    description="Generate comprehensive fertilizer plan from soil test to harvest"
)
async def create_complete_fertilizer_plan(
    request: CompleteFertilizerPlanRequest
) -> Dict[str, any]:
    """
    Create complete fertilizer plan with strategy, timing, alerts, and monitoring.

    This comprehensive endpoint provides:
    - Nutrient requirement calculations
    - Optimized fertilizer strategy
    - Timing plan for all applications
    - Seasonal calendar
    - Alert setup for timing windows
    - Implementation guidance
    - Monitoring plan

    Args:
        request: Complete plan request parameters

    Returns:
        Dict containing complete fertilizer plan

    Raises:
        HTTPException: On processing errors
    """
    try:
        logger.info(
            f"Creating complete fertilizer plan for {request.crop_type}, "
            f"yield goal: {request.yield_goal}"
        )

        result = await integrated_workflow.create_complete_fertilizer_plan(
            crop_type=request.crop_type,
            field_size=request.field_size,
            location=request.location,
            planting_date=request.planting_date,
            harvest_date=request.harvest_date,
            soil_test_results=request.soil_test_results,
            yield_goal=request.yield_goal,
            budget=request.budget,
            risk_tolerance=request.risk_tolerance,
        )

        logger.info(
            f"Complete fertilizer plan created: "
            f"total cost ${result['cost_summary']['total_fertilizer_cost']:.2f}"
        )

        return result

    except ValueError as e:
        logger.warning(f"Invalid request parameters: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Complete plan creation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create complete fertilizer plan: {str(e)}"
        )


@router.post(
    "/api/v1/integrated/workflow/optimize-and-schedule",
    summary="Optimize and schedule workflow",
    description="Single workflow for fertilizer optimization and scheduling"
)
async def optimize_and_schedule_workflow(
    request: OptimizeAndScheduleRequest
) -> Dict[str, any]:
    """
    Execute integrated optimize and schedule workflow.

    This simplified workflow:
    - Optimizes fertilizer strategy
    - Schedules applications with constraints
    - Validates scheduling feasibility

    Args:
        request: Optimize and schedule request parameters

    Returns:
        Dict containing optimized and scheduled plan

    Raises:
        HTTPException: On processing errors
    """
    try:
        logger.info(
            f"Processing optimize and schedule workflow for {request.crop_type}"
        )

        result = await integrated_workflow.optimize_and_schedule_workflow(
            crop_type=request.crop_type,
            field_size=request.field_size,
            location=request.location,
            planting_date=request.planting_date,
            soil_characteristics=request.soil_characteristics,
            nutrient_requirements=request.nutrient_requirements,
            scheduling_constraints=request.scheduling_constraints,
        )

        logger.info("Optimize and schedule workflow completed successfully")

        return result

    except ValueError as e:
        logger.warning(f"Invalid request parameters: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Workflow failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Optimize and schedule workflow failed: {str(e)}"
        )


__all__ = ["router"]

"""
API routes for multi-nutrient optimization service.

This module provides REST API endpoints for:
- Multi-nutrient optimization requests
- Optimization result retrieval
- Alternative strategy analysis
- Nutrient interaction analysis
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import logging
from uuid import UUID
from datetime import datetime

from ..services.nutrient_optimizer import (
    MultiNutrientOptimizer, 
    NutrientOptimizationRequest, 
    NutrientOptimizationResult,
    NutrientType,
    SoilTestData,
    CropRequirement,
    EnvironmentalLimit
)
from ..models.nutrient_optimization_models import (
    OptimizationRequestModel,
    OptimizationResponseModel,
    AlternativeStrategyModel,
    InteractionAnalysisModel
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/nutrient-optimization", tags=["nutrient-optimization"])

# Initialize optimizer service
optimizer_service = MultiNutrientOptimizer()


@router.post("/optimize", response_model=OptimizationResponseModel)
async def optimize_nutrients(
    request: OptimizationRequestModel,
    background_tasks: BackgroundTasks
) -> OptimizationResponseModel:
    """
    Perform comprehensive multi-nutrient optimization.
    
    This endpoint optimizes fertilizer application rates for multiple nutrients
    considering soil test levels, crop requirements, environmental limits,
    and nutrient interactions.
    
    Args:
        request: Optimization request with field data and constraints
        background_tasks: Background task handler for logging
        
    Returns:
        OptimizationResponseModel with optimal rates and analysis
        
    Raises:
        HTTPException: If optimization fails or invalid data provided
    """
    try:
        logger.info(f"Received nutrient optimization request for field {request.field_id}")
        
        # Convert request model to service model
        optimization_request = NutrientOptimizationRequest(
            field_id=request.field_id,
            crop_type=request.crop_type,
            target_yield=request.target_yield,
            yield_unit=request.yield_unit,
            soil_tests=[
                SoilTestData(
                    nutrient=NutrientType(test.nutrient),
                    test_value=test.test_value,
                    test_unit=test.test_unit,
                    test_method=test.test_method,
                    test_date=test.test_date,
                    confidence_level=test.confidence_level
                )
                for test in request.soil_tests
            ],
            crop_requirements=[
                CropRequirement(
                    nutrient=NutrientType(req.nutrient),
                    minimum_requirement=req.minimum_requirement,
                    optimal_range_min=req.optimal_range_min,
                    optimal_range_max=req.optimal_range_max,
                    maximum_tolerance=req.maximum_tolerance,
                    uptake_efficiency=req.uptake_efficiency,
                    critical_stage=req.critical_stage
                )
                for req in request.crop_requirements
            ],
            environmental_limits=[
                EnvironmentalLimit(
                    nutrient=NutrientType(limit.nutrient),
                    max_application_rate=limit.max_application_rate,
                    application_unit=limit.application_unit,
                    environmental_risk=limit.environmental_risk,
                    regulatory_limit=limit.regulatory_limit,
                    seasonal_limit=limit.seasonal_limit
                )
                for limit in request.environmental_limits
            ],
            optimization_objective=request.optimization_objective,
            budget_constraint=request.budget_constraint,
            risk_tolerance=request.risk_tolerance,
            field_size_acres=request.field_size_acres,
            soil_type=request.soil_type,
            ph_level=request.ph_level,
            organic_matter_percent=request.organic_matter_percent,
            include_interactions=request.include_interactions,
            interaction_model=request.interaction_model
        )
        
        # Perform optimization
        result = await optimizer_service.optimize_nutrients(optimization_request)
        
        # Log optimization completion
        background_tasks.add_task(
            log_optimization_completion,
            result.optimization_id,
            request.field_id,
            result.optimization_time_seconds
        )
        
        # Convert result to response model
        response = OptimizationResponseModel(
            optimization_id=result.optimization_id,
            field_id=result.field_id,
            crop_type=result.crop_type,
            optimal_nutrient_rates=result.optimal_nutrient_rates,
            expected_yield=result.expected_yield,
            yield_confidence=result.yield_confidence,
            total_cost=result.total_cost,
            expected_revenue=result.expected_revenue,
            net_profit=result.net_profit,
            roi_percentage=result.roi_percentage,
            optimization_method=result.optimization_method,
            convergence_status=result.convergence_status,
            iterations_required=result.iterations_required,
            optimization_time_seconds=result.optimization_time_seconds,
            nutrient_interactions=[
                {
                    "nutrient1": interaction.nutrient1.value,
                    "nutrient2": interaction.nutrient2.value,
                    "interaction_type": interaction.interaction_type.value,
                    "interaction_strength": interaction.interaction_strength,
                    "interaction_coefficient": interaction.interaction_coefficient
                }
                for interaction in result.nutrient_interactions
            ],
            interaction_effects=result.interaction_effects,
            risk_factors=result.risk_factors,
            risk_score=result.risk_score,
            recommendations=result.recommendations,
            alternative_strategies=[
                AlternativeStrategyModel(
                    strategy=strategy["strategy"],
                    description=strategy["description"],
                    rates=strategy["rates"],
                    expected_yield=strategy["expected_yield"],
                    cost=strategy["cost"]
                )
                for strategy in result.alternative_strategies
            ],
            created_at=result.created_at,
            model_version=result.model_version
        )
        
        logger.info(f"Nutrient optimization completed for field {request.field_id}")
        return response
        
    except ValueError as e:
        logger.error(f"Validation error in nutrient optimization: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in nutrient optimization: {str(e)}")
        raise HTTPException(status_code=500, detail="Nutrient optimization failed")


@router.post("/quick-optimize", response_model=OptimizationResponseModel)
async def quick_optimize_nutrients(
    request: OptimizationRequestModel
) -> OptimizationResponseModel:
    """
    Perform quick multi-nutrient optimization using simplified models.
    
    This endpoint provides faster optimization using linear models
    for scenarios where speed is prioritized over accuracy.
    
    Args:
        request: Optimization request with field data
        
    Returns:
        OptimizationResponseModel with optimal rates
        
    Raises:
        HTTPException: If optimization fails
    """
    try:
        logger.info(f"Received quick nutrient optimization request for field {request.field_id}")
        
        # Override interaction model for quick optimization
        request.interaction_model = "linear"
        
        # Convert and optimize
        optimization_request = NutrientOptimizationRequest(
            field_id=request.field_id,
            crop_type=request.crop_type,
            target_yield=request.target_yield,
            yield_unit=request.yield_unit,
            soil_tests=[
                SoilTestData(
                    nutrient=NutrientType(test.nutrient),
                    test_value=test.test_value,
                    test_unit=test.test_unit,
                    test_method=test.test_method,
                    test_date=test.test_date,
                    confidence_level=test.confidence_level
                )
                for test in request.soil_tests
            ],
            crop_requirements=[
                CropRequirement(
                    nutrient=NutrientType(req.nutrient),
                    minimum_requirement=req.minimum_requirement,
                    optimal_range_min=req.optimal_range_min,
                    optimal_range_max=req.optimal_range_max,
                    maximum_tolerance=req.maximum_tolerance,
                    uptake_efficiency=req.uptake_efficiency,
                    critical_stage=req.critical_stage
                )
                for req in request.crop_requirements
            ],
            environmental_limits=[
                EnvironmentalLimit(
                    nutrient=NutrientType(limit.nutrient),
                    max_application_rate=limit.max_application_rate,
                    application_unit=limit.application_unit,
                    environmental_risk=limit.environmental_risk,
                    regulatory_limit=limit.regulatory_limit,
                    seasonal_limit=limit.seasonal_limit
                )
                for limit in request.environmental_limits
            ],
            optimization_objective=request.optimization_objective,
            budget_constraint=request.budget_constraint,
            risk_tolerance=request.risk_tolerance,
            field_size_acres=request.field_size_acres,
            soil_type=request.soil_type,
            ph_level=request.ph_level,
            organic_matter_percent=request.organic_matter_percent,
            include_interactions=False,  # Disable interactions for speed
            interaction_model="linear"
        )
        
        # Perform quick optimization
        result = await optimizer_service.optimize_nutrients(optimization_request)
        
        # Convert to response model
        response = OptimizationResponseModel(
            optimization_id=result.optimization_id,
            field_id=result.field_id,
            crop_type=result.crop_type,
            optimal_nutrient_rates=result.optimal_nutrient_rates,
            expected_yield=result.expected_yield,
            yield_confidence=result.yield_confidence,
            total_cost=result.total_cost,
            expected_revenue=result.expected_revenue,
            net_profit=result.net_profit,
            roi_percentage=result.roi_percentage,
            optimization_method=result.optimization_method,
            convergence_status=result.convergence_status,
            iterations_required=result.iterations_required,
            optimization_time_seconds=result.optimization_time_seconds,
            nutrient_interactions=[],
            interaction_effects={},
            risk_factors=result.risk_factors,
            risk_score=result.risk_score,
            recommendations=result.recommendations,
            alternative_strategies=[],
            created_at=result.created_at,
            model_version=result.model_version
        )
        
        logger.info(f"Quick nutrient optimization completed for field {request.field_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error in quick nutrient optimization: {str(e)}")
        raise HTTPException(status_code=500, detail="Quick nutrient optimization failed")


@router.get("/interactions", response_model=InteractionAnalysisModel)
async def analyze_nutrient_interactions(
    crop_type: str,
    soil_ph: float,
    soil_type: str = "loam"
) -> InteractionAnalysisModel:
    """
    Analyze nutrient interactions for specific conditions.
    
    This endpoint provides analysis of nutrient interactions
    based on crop type, soil pH, and soil type.
    
    Args:
        crop_type: Type of crop
        soil_ph: Soil pH level
        soil_type: Soil type classification
        
    Returns:
        InteractionAnalysisModel with interaction analysis
        
    Raises:
        HTTPException: If analysis fails
    """
    try:
        logger.info(f"Analyzing nutrient interactions for {crop_type} at pH {soil_ph}")
        
        # Get relevant interactions
        relevant_interactions = []
        for interaction in optimizer_service.nutrient_interactions:
            conditions_met = True
            
            # Check pH conditions
            if "ph_range" in interaction.conditions:
                ph_min, ph_max = interaction.conditions["ph_range"]
                if not (ph_min <= soil_ph <= ph_max):
                    conditions_met = False
            
            # Check soil type conditions
            if "soil_type" in interaction.conditions:
                if interaction.conditions["soil_type"] != soil_type:
                    conditions_met = False
            
            if conditions_met:
                relevant_interactions.append({
                    "nutrient1": interaction.nutrient1.value,
                    "nutrient2": interaction.nutrient2.value,
                    "interaction_type": interaction.interaction_type.value,
                    "interaction_strength": interaction.interaction_strength,
                    "interaction_coefficient": interaction.interaction_coefficient,
                    "conditions": interaction.conditions
                })
        
        # Generate recommendations
        recommendations = []
        if soil_ph < 6.0:
            recommendations.append("Low pH may reduce phosphorus availability")
            recommendations.append("Consider lime application to improve nutrient availability")
        elif soil_ph > 7.5:
            recommendations.append("High pH may reduce micronutrient availability")
            recommendations.append("Monitor iron, zinc, and manganese levels")
        
        if soil_type == "clay":
            recommendations.append("Clay soils may have higher nutrient holding capacity")
        elif soil_type == "sandy":
            recommendations.append("Sandy soils may require more frequent nutrient applications")
        
        response = InteractionAnalysisModel(
            crop_type=crop_type,
            soil_ph=soil_ph,
            soil_type=soil_type,
            relevant_interactions=relevant_interactions,
            recommendations=recommendations,
            analysis_timestamp=datetime.utcnow()
        )
        
        logger.info(f"Nutrient interaction analysis completed for {crop_type}")
        return response
        
    except Exception as e:
        logger.error(f"Error in nutrient interaction analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Nutrient interaction analysis failed")


@router.get("/nutrients", response_model=List[Dict[str, Any]])
async def get_available_nutrients() -> List[Dict[str, Any]]:
    """
    Get list of available nutrients for optimization.
    
    Returns:
        List of available nutrients with descriptions
    """
    nutrients = [
        {
            "nutrient": "nitrogen",
            "description": "Primary macronutrient for vegetative growth",
            "typical_range": "50-200 lbs/acre",
            "critical_stages": ["vegetative", "reproductive"]
        },
        {
            "nutrient": "phosphorus",
            "description": "Essential for root development and energy transfer",
            "typical_range": "20-100 lbs/acre",
            "critical_stages": ["early_vegetative", "reproductive"]
        },
        {
            "nutrient": "potassium",
            "description": "Important for water regulation and disease resistance",
            "typical_range": "30-150 lbs/acre",
            "critical_stages": ["vegetative", "reproductive"]
        },
        {
            "nutrient": "calcium",
            "description": "Essential for cell wall structure and root development",
            "typical_range": "500-2000 lbs/acre",
            "critical_stages": ["early_vegetative"]
        },
        {
            "nutrient": "magnesium",
            "description": "Central component of chlorophyll",
            "typical_range": "50-200 lbs/acre",
            "critical_stages": ["vegetative"]
        },
        {
            "nutrient": "sulfur",
            "description": "Essential for protein synthesis",
            "typical_range": "10-50 lbs/acre",
            "critical_stages": ["vegetative", "reproductive"]
        },
        {
            "nutrient": "zinc",
            "description": "Important for enzyme function and growth regulation",
            "typical_range": "0.5-5 lbs/acre",
            "critical_stages": ["early_vegetative"]
        },
        {
            "nutrient": "iron",
            "description": "Essential for chlorophyll synthesis",
            "typical_range": "1-10 lbs/acre",
            "critical_stages": ["vegetative"]
        },
        {
            "nutrient": "manganese",
            "description": "Important for photosynthesis and nitrogen metabolism",
            "typical_range": "1-10 lbs/acre",
            "critical_stages": ["vegetative"]
        },
        {
            "nutrient": "copper",
            "description": "Essential for enzyme function and disease resistance",
            "typical_range": "0.1-2 lbs/acre",
            "critical_stages": ["vegetative"]
        },
        {
            "nutrient": "boron",
            "description": "Important for cell wall formation and reproduction",
            "typical_range": "0.1-2 lbs/acre",
            "critical_stages": ["reproductive"]
        },
        {
            "nutrient": "molybdenum",
            "description": "Essential for nitrogen fixation and nitrate reduction",
            "typical_range": "0.01-0.1 lbs/acre",
            "critical_stages": ["vegetative"]
        }
    ]
    
    return nutrients


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for nutrient optimization service.
    
    Returns:
        Service health status
    """
    return {
        "status": "healthy",
        "service": "nutrient-optimization",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "features": [
            "multi_nutrient_optimization",
            "nutrient_interactions",
            "response_surface_modeling",
            "machine_learning_optimization",
            "economic_analysis",
            "risk_assessment"
        ]
    }


async def log_optimization_completion(
    optimization_id: str,
    field_id: UUID,
    processing_time: float
):
    """Background task to log optimization completion."""
    logger.info(
        f"Optimization {optimization_id} completed for field {field_id} "
        f"in {processing_time:.2f} seconds"
    )
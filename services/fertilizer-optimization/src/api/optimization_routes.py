from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List
from ..services.economic_optimizer import EconomicOptimizer
from ..schemas.optimization_schemas import OptimizationRequest, OptimizationResponse, FertilizerRecommendation
import logging

logger = logging.getLogger(__name__)

# Create the router
router = APIRouter()

# Dependency to get the economic optimizer service
def get_economic_optimizer() -> EconomicOptimizer:
    """
    Dependency to provide the EconomicOptimizer instance.
    """
    return EconomicOptimizer()

@router.post("/optimize", response_model=OptimizationResponse)
async def optimize_fertilizer(
    request: OptimizationRequest,
    optimizer: EconomicOptimizer = Depends(get_economic_optimizer)
):
    """
    Optimize fertilizer application strategy.

    - **request**: OptimizationRequest containing field details, nutrient requirements, and available fertilizers.
    - **Returns**: OptimizationResponse with recommendations, total cost, expected yield, and ROI.
    - **Raises**: HTTPException if optimization fails.
    """
    try:
        # Prepare data for optimizer (convert to per acre)
        field_requirements = {k: v / request.field_acres for k, v in request.nutrient_requirements.items()}
        available_fertilizers = [
            {
                'name': f.name,
                'nutrients': f.nutrients,
                'cost_per_unit': f.price_per_ton  # Assuming per ton
            }
            for f in request.available_fertilizers
        ]
        budget_per_acre = request.budget_per_acre

        # Call optimizer
        recommendations_dict = optimizer.optimize_fertilizer_strategy(
            field_requirements, available_fertilizers, budget_per_acre
        )

        # Calculate total cost and prepare recommendations (multiply by field_acres)
        recommendations = []
        total_cost = 0.0
        for fert in request.available_fertilizers:
            amount_per_acre = recommendations_dict.get(fert.name, 0.0)
            if amount_per_acre > 0:
                amount = amount_per_acre * request.field_acres
                cost = amount * fert.price_per_ton
                nutrients_applied = {k: v * amount for k, v in fert.nutrients.items()}
                rec = FertilizerRecommendation(
                    fertilizer_name=fert.name,
                    application_rate=amount,
                    cost=cost,
                    nutrients_applied=nutrients_applied
                )
                recommendations.append(rec)
                total_cost += cost

        # Calculate expected yield (based on yield goal per acre * field acres)
        expected_yield = request.yield_goal_bu_acre * request.field_acres

        # Calculate ROI
        field_data = {
            'yield_bu_per_acre': request.yield_goal_bu_acre,
            'total_fertilizer_cost': total_cost
        }
        roi = optimizer.calculate_roi(recommendations_dict, field_data, request.crop_price_per_bu)

        return OptimizationResponse(
            recommendations=recommendations,
            total_cost=total_cost,
            expected_yield=expected_yield,
            roi=roi
        )

    except ValueError as e:
        logger.error(f"Optimization error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Optimization failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in optimization: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during optimization")
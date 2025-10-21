from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from uuid import UUID

from ..models.micronutrient_models import MicronutrientPrice, ApplicationCost, MicronutrientBudgetAnalysisResult
from ..services.micronutrient_cost_service import MicronutrientCostService

router = APIRouter()

async def get_micronutrient_cost_service() -> MicronutrientCostService:
    return MicronutrientCostService()

@router.post("/analyze-budget", response_model=MicronutrientBudgetAnalysisResult)
async def analyze_micronutrient_budget_endpoint(
    farm_id: UUID,
    field_id: UUID,
    micronutrient_recommendations: List[Dict[str, Any]],
    micronutrient_prices: List[MicronutrientPrice],
    application_costs: List[ApplicationCost],
    field_area_hectares: float,
    notes: Optional[str] = None,
    service: MicronutrientCostService = Depends(get_micronutrient_cost_service)
):
    """
    Analyzes the comprehensive budget and cost for micronutrient application.

    Args:
        farm_id: ID of the farm.
        field_id: ID of the field.
        micronutrient_recommendations: List of recommended micronutrients and their rates.
                                       Each dict should contain 'name', 'rate', and 'unit'.
        micronutrient_prices: List of available micronutrient product prices.
        application_costs: List of costs associated with application (labor, equipment, etc.).
        field_area_hectares: Area of the field in hectares.
        notes: Optional notes for the analysis.

    Returns:
        A MicronutrientBudgetAnalysisResult object containing the detailed cost breakdown.
    """
    try:
        result = await service.analyze_micronutrient_budget(
            farm_id=farm_id,
            field_id=field_id,
            micronutrient_recommendations=micronutrient_recommendations,
            micronutrient_prices=micronutrient_prices,
            application_costs=application_costs,
            field_area_hectares=field_area_hectares,
            notes=notes
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

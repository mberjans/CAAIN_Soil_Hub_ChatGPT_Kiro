from typing import List, Dict, Any
from uuid import UUID
from datetime import datetime

from ..models.micronutrient_models import MicronutrientPrice, ApplicationCost, MicronutrientBudgetAnalysisResult

class MicronutrientCostService:
    """Service for comprehensive micronutrient budget and cost analysis."""

    def __init__(self):
        pass

    async def analyze_micronutrient_budget(
        self,
        farm_id: UUID,
        field_id: UUID,
        micronutrient_recommendations: List[Dict[str, Any]],
        micronutrient_prices: List[MicronutrientPrice],
        application_costs: List[ApplicationCost],
        field_area_hectares: float,
        notes: Optional[str] = None
    ) -> MicronutrientBudgetAnalysisResult:
        """
        Performs a comprehensive budget and cost analysis for micronutrients.

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

        total_micronutrient_cost = 0.0
        for rec in micronutrient_recommendations:
            rec_name = rec['name']
            rec_rate = rec['rate']
            rec_unit = rec['unit']

            # Find matching price for the recommended micronutrient
            # This is a simplified matching. In a real scenario, you'd match by product, concentration, etc.
            matching_price = next(
                (mp for mp in micronutrient_prices if mp.micronutrient_name.lower() == rec_name.lower()),
                None
            )

            if matching_price:
                # Assuming rec_unit and matching_price.unit are compatible or can be converted
                # For simplicity, assuming direct compatibility or that rate is per field area
                # and price is per unit of active ingredient or product.
                # A more robust system would need conversion factors.
                cost_for_rec = (rec_rate * field_area_hectares) * matching_price.price_per_unit
                total_micronutrient_cost += cost_for_rec
            else:
                # Handle cases where no price is found (e.g., log a warning, add to notes)
                print(f"Warning: No price found for micronutrient {rec_name}")

        total_application_cost = sum(ac.total_cost for ac in application_costs)
        overall_total_cost = total_micronutrient_cost + total_application_cost
        cost_per_hectare = overall_total_cost / field_area_hectares if field_area_hectares > 0 else 0.0

        return MicronutrientBudgetAnalysisResult(
            farm_id=str(farm_id),
            field_id=str(field_id),
            micronutrient_recommendations=micronutrient_recommendations,
            micronutrient_product_costs=micronutrient_prices,
            application_costs=application_costs,
            total_micronutrient_cost=total_micronutrient_cost,
            total_application_cost=total_application_cost,
            overall_total_cost=overall_total_cost,
            cost_per_hectare=cost_per_hectare,
            analysis_date=datetime.utcnow(),
            notes=notes
        )

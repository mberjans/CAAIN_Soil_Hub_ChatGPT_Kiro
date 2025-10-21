from typing import List

from services.recommendation_engine.src.models.micronutrient_models import (
    MicronutrientApplication,
    MicronutrientYieldResponse,
    YieldEconomicPredictionRequest,
    EconomicReturnPrediction
)

class EconomicReturnCalculationService:
    def calculate_economic_returns(
        self,
        request: YieldEconomicPredictionRequest,
        yield_responses: List[MicronutrientYieldResponse]
    ) -> List[EconomicReturnPrediction]:
        economic_predictions: List[EconomicReturnPrediction] = []
        unit_price_per_kg = request.crop_yield_data.unit_price_per_kg
        area_ha = request.area_ha

        # Create a dictionary for quick lookup of yield responses by micronutrient type
        yield_response_map = {yr.micronutrient_type: yr for yr in yield_responses}

        for app in request.micronutrient_applications:
            total_application_cost = app.application_rate_kg_ha * app.cost_per_kg * area_ha
            additional_revenue_from_yield_increase = 0.0

            yield_response = yield_response_map.get(app.micronutrient_type)
            if yield_response:
                additional_revenue_from_yield_increase = (
                    yield_response.predicted_yield_increase_kg_ha * unit_price_per_kg * area_ha
                )

            net_economic_return = additional_revenue_from_yield_increase - total_application_cost

            roi_percentage = 0.0
            if total_application_cost > 0:
                roi_percentage = (net_economic_return / total_application_cost) * 100
            elif net_economic_return > 0: # Cost is 0 but there's revenue, implies infinite ROI
                roi_percentage = float('inf')
            else: # Cost is 0 and no net return
                roi_percentage = 0.0

            economic_predictions.append(
                EconomicReturnPrediction(
                    micronutrient_type=app.micronutrient_type,
                    total_application_cost=total_application_cost,
                    additional_revenue_from_yield_increase=additional_revenue_from_yield_increase,
                    net_economic_return=net_economic_return,
                    roi_percentage=roi_percentage,
                    currency="CAD" # Corrected: Use default or explicit currency string
                )
            )
        return economic_predictions
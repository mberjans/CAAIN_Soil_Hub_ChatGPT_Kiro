
from typing import List

from services.recommendation_engine.src.models.micronutrient_models import (
    MicronutrientType,
    SoilTestResult,
    MicronutrientApplication,
    CropYieldData,
    MicronutrientYieldResponse,
    YieldEconomicPredictionRequest
)

class MicronutrientYieldPredictionService:
    def predict_yield_response(self, request: YieldEconomicPredictionRequest) -> List[MicronutrientYieldResponse]:
        responses: List[MicronutrientYieldResponse] = []
        baseline_yield = request.crop_yield_data.expected_yield_baseline_kg_ha

        for app in request.micronutrient_applications:
            soil_test_for_micronutrient = next(
                (st for st in request.soil_test_results if st.micronutrient_type == app.micronutrient_type),
                None
            )

            predicted_yield_increase = 0.0
            confidence_score = 0.2  # Default low confidence if no soil test or unknown scenario

            if soil_test_for_micronutrient:
                if soil_test_for_micronutrient.level_ppm < soil_test_for_micronutrient.sufficiency_range_min_ppm:
                    # Deficient
                    # Simplified logic: 100 kg/ha yield increase per 1 ppm deficiency below min sufficiency
                    deficiency_amount = soil_test_for_micronutrient.sufficiency_range_min_ppm - soil_test_for_micronutrient.level_ppm
                    predicted_yield_increase = deficiency_amount * 100.0  # Placeholder constant
                    confidence_score = 0.8
                else:
                    # Sufficient or above
                    predicted_yield_increase = 0.0
                    confidence_score = 0.9
            else:
                # No soil test result for this micronutrient, assume no confirmed deficiency for prediction
                predicted_yield_increase = 0.0
                confidence_score = 0.2 # Low confidence due to missing data

            predicted_total_yield = baseline_yield + predicted_yield_increase

            responses.append(
                MicronutrientYieldResponse(
                    micronutrient_type=app.micronutrient_type,
                    predicted_yield_increase_kg_ha=predicted_yield_increase,
                    predicted_total_yield_kg_ha=predicted_total_yield,
                    confidence_score=confidence_score
                )
            )
        return responses

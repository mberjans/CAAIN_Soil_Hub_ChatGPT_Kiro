import logging
from typing import List, Dict, Any, Optional
from ..models.micronutrient_models import (
    MicronutrientApplicationRequest,
    MicronutrientApplicationResponse,
    MicronutrientApplication,
    ApplicationMethod,
    TimingStage
)

logger = logging.getLogger(__name__)

class MicronutrientApplicationService:
    """Service for providing micronutrient application method and timing recommendations."""

    def __init__(self):
        # Placeholder for a more sophisticated knowledge base or rule engine
        self.crop_micronutrient_rules = self._load_crop_rules()

    def _load_crop_rules(self) -> Dict[str, Any]:
        """Loads predefined rules for micronutrient application based on crop type."""
        # In a real application, this would load from a database or configuration files
        return {
            "Corn": {
                "Boron": {
                    "deficiency_threshold": 0.5,
                    "target_level": 1.0,
                    "methods": {
                        ApplicationMethod.FOLIAR: {
                            "efficiency": 0.8,
                            "timing": [TimingStage.VEGETATIVE, TimingStage.FLOWERING],
                            "rate_per_unit": 0.1, # kg/ha per ppm deficiency
                            "unit": "kg/ha"
                        },
                        ApplicationMethod.SOIL_BROADCAST: {
                            "efficiency": 0.6,
                            "timing": [TimingStage.PRE_PLANT, TimingStage.PLANTING],
                            "rate_per_unit": 0.5, # kg/ha per ppm deficiency
                            "unit": "kg/ha"
                        }
                    }
                },
                "Zinc": {
                    "deficiency_threshold": 1.2,
                    "target_level": 2.0,
                    "methods": {
                        ApplicationMethod.FOLIAR: {
                            "efficiency": 0.7,
                            "timing": [TimingStage.VEGETATIVE],
                            "rate_per_unit": 0.2, # kg/ha per ppm deficiency
                            "unit": "kg/ha"
                        },
                        ApplicationMethod.SOIL_BANDED: {
                            "efficiency": 0.9,
                            "timing": [TimingStage.PLANTING],
                            "rate_per_unit": 1.0, # kg/ha per ppm deficiency
                            "unit": "kg/ha"
                        },
                        ApplicationMethod.SEED_TREATMENT: {
                            "efficiency": 0.85,
                            "timing": [TimingStage.PRE_PLANT],
                            "rate_per_unit": 0.05, # kg/100kg seed
                            "unit": "kg/100kg seed"
                        }
                    }
                }
            },
            "Soybean": {
                "Manganese": {
                    "deficiency_threshold": 20.0,
                    "target_level": 30.0,
                    "methods": {
                        ApplicationMethod.FOLIAR: {
                            "efficiency": 0.85,
                            "timing": [TimingStage.VEGETATIVE, TimingStage.FLOWERING],
                            "rate_per_unit": 0.5, # kg/ha per ppm deficiency
                            "unit": "kg/ha"
                        }
                    }
                }
            }
        }

    async def get_application_recommendations(
        self,
        request: MicronutrientApplicationRequest
    ) -> MicronutrientApplicationResponse:
        """Generates comprehensive micronutrient application recommendations."""
        logger.info(f"Received request for {request.crop_type} at {request.growth_stage}")

        recommendations: List[MicronutrientApplication] = []
        overall_efficiency_sum = 0.0
        num_recommendations = 0
        notes: List[str] = []

        crop_rules = self.crop_micronutrient_rules.get(request.crop_type)
        if not crop_rules:
            notes.append(f"No specific rules found for crop type: {request.crop_type}")
            return MicronutrientApplicationResponse(recommendations=[], notes=". ".join(notes))

        for micro, current_level in request.current_micronutrient_levels.items():
            micro_rules = crop_rules.get(micro)
            if not micro_rules:
                notes.append(f"No specific rules found for micronutrient {micro} for {request.crop_type}")
                continue

            deficiency_threshold = micro_rules.get("deficiency_threshold", 0)
            target_level = micro_rules.get("target_level", current_level)

            if current_level < deficiency_threshold:
                deficiency_amount = target_level - current_level
                logger.info(f"Deficiency detected for {micro}: current={current_level}, target={target_level}")

                best_method: Optional[ApplicationMethod] = None
                best_efficiency = -1.0
                best_timing: Optional[TimingStage] = None

                # Filter methods by available equipment first
                available_methods_for_micro = []
                for method, method_data in micro_rules["methods"].items():
                    if request.equipment_available is not None and method not in request.equipment_available:
                        continue
                    available_methods_for_micro.append((method, method_data))

                if not available_methods_for_micro:
                    notes.append(f"No suitable equipment available for {micro}.")
                    continue

                for method, method_data in available_methods_for_micro:
                    # Check if timing is appropriate for current growth stage
                    if request.growth_stage not in method_data["timing"]:
                        continue

                    # Simple efficiency scoring for now, can be expanded
                    efficiency = method_data["efficiency"]

                    # Prioritize methods based on efficiency (assuming maximize_yield implies higher efficiency)
                    if efficiency > best_efficiency:
                        best_efficiency = efficiency
                        best_method = method
                        best_timing = request.growth_stage # Or select best timing from method_data["timing"]
                    # Add more complex goal-based prioritization here if needed (e.g., minimize_cost)
                    # For now, if multiple methods have same max efficiency, the first one encountered is chosen.


                if best_method and best_timing:
                    rate = deficiency_amount * micro_rules["methods"][best_method]["rate_per_unit"]
                    unit = micro_rules["methods"][best_method]["unit"]
                    recommendations.append(
                        MicronutrientApplication(
                            micronutrient=micro,
                            method=best_method,
                            timing=best_timing,
                            rate=rate,
                            unit=unit,
                            efficiency_score=best_efficiency
                        )
                    )
                    overall_efficiency_sum += best_efficiency
                    num_recommendations += 1
                else:
                    notes.append(f"Could not find suitable application method/timing for {micro} given constraints.")

        overall_efficiency = overall_efficiency_sum / num_recommendations if num_recommendations > 0 else None

        return MicronutrientApplicationResponse(
            recommendations=recommendations,
            overall_efficiency=overall_efficiency,
            notes=". ".join(notes) if notes else None
        )

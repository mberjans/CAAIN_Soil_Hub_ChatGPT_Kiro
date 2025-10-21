import logging
from uuid import UUID, uuid4
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..models.tissue_test_models import (
    TissueTestRequest,
    TissueTestAnalysisResponse,
    NutrientDeficiency,
    DeficiencySeverity,
    Nutrient,
    TissueTestResult
)

logger = logging.getLogger(__name__)

class TissueTestService:
    """Service for processing and analyzing tissue test results."""

    def __init__(self):
        # Hardcoded optimal ranges for demonstration. In a real app, this would come from a DB.
        self.optimal_ranges: Dict[str, Dict[str, Dict[Nutrient, Dict[str, float]]]] = {
            "corn": {
                "V6": {
                    Nutrient.NITROGEN: {"optimal_min": 3.0, "optimal_max": 4.0, "critical_low": 2.5, "critical_high": 4.5},
                    Nutrient.PHOSPHORUS: {"optimal_min": 0.3, "optimal_max": 0.5, "critical_low": 0.25, "critical_high": 0.6},
                    Nutrient.POTASSIUM: {"optimal_min": 2.0, "optimal_max": 3.0, "critical_low": 1.5, "critical_high": 3.5},
                    Nutrient.ZINC: {"optimal_min": 20.0, "optimal_max": 60.0, "critical_low": 15.0, "critical_high": 70.0},
                },
                "R1": {
                    Nutrient.NITROGEN: {"optimal_min": 2.75, "optimal_max": 3.75, "critical_low": 2.25, "critical_high": 4.25},
                    Nutrient.PHOSPHORUS: {"optimal_min": 0.25, "optimal_max": 0.45, "critical_low": 0.2, "critical_high": 0.55},
                    Nutrient.POTASSIUM: {"optimal_min": 1.75, "optimal_max": 2.75, "critical_low": 1.25, "critical_high": 3.25},
                    Nutrient.ZINC: {"optimal_min": 18.0, "optimal_max": 55.0, "critical_low": 13.0, "critical_high": 65.0},
                },
            },
            "soybean": {
                "V3": {
                    Nutrient.NITROGEN: {"optimal_min": 4.0, "optimal_max": 5.0, "critical_low": 3.5, "critical_high": 5.5},
                    Nutrient.PHOSPHORUS: {"optimal_min": 0.3, "optimal_max": 0.5, "critical_low": 0.25, "critical_high": 0.6},
                    Nutrient.POTASSIUM: {"optimal_min": 1.7, "optimal_max": 2.5, "critical_low": 1.2, "critical_high": 3.0},
                    Nutrient.IRON: {"optimal_min": 50.0, "optimal_max": 200.0, "critical_low": 40.0, "critical_high": 250.0},
                },
                "R2": {
                    Nutrient.NITROGEN: {"optimal_min": 4.5, "optimal_max": 5.5, "critical_low": 4.0, "critical_high": 6.0},
                    Nutrient.PHOSPHORUS: {"optimal_min": 0.25, "optimal_max": 0.45, "critical_low": 0.2, "critical_high": 0.55},
                    Nutrient.POTASSIUM: {"optimal_min": 1.5, "optimal_max": 2.3, "critical_low": 1.0, "critical_high": 2.8},
                    Nutrient.IRON: {"optimal_min": 45.0, "optimal_max": 180.0, "critical_low": 35.0, "critical_high": 220.0},
                },
            },
        }

    async def analyze_tissue_test(self, request: TissueTestRequest) -> TissueTestAnalysisResponse:
        """Analyzes a tissue test request and returns a detailed analysis."""
        deficiencies: List[NutrientDeficiency] = []
        overall_status = "Healthy"
        recommendations_summary_list: List[str] = []

        crop_optimal_ranges = self.optimal_ranges.get(request.crop_type.lower())
        if not crop_optimal_ranges:
            logger.warning(f"Optimal ranges not found for crop type: {request.crop_type}")
            overall_status = "Analysis Incomplete: Crop type not supported for detailed analysis."
            return TissueTestAnalysisResponse(
                analysis_id=uuid4(),
                farm_id=request.farm_id,
                field_id=request.field_id,
                crop_type=request.crop_type,
                growth_stage=request.growth_stage,
                test_date=request.test_date,
                deficiencies=[],
                overall_status=overall_status,
                recommendations_summary=overall_status,
                raw_results=request.results
            )

        growth_stage_ranges = crop_optimal_ranges.get(request.growth_stage.upper())
        if not growth_stage_ranges:
            logger.warning(f"Optimal ranges not found for growth stage: {request.growth_stage} of {request.crop_type}")
            overall_status = "Analysis Incomplete: Growth stage not supported for detailed analysis."
            return TissueTestAnalysisResponse(
                analysis_id=uuid4(),
                farm_id=request.farm_id,
                field_id=request.field_id,
                crop_type=request.crop_type,
                growth_stage=request.growth_stage,
                test_date=request.test_date,
                deficiencies=[],
                overall_status=overall_status,
                recommendations_summary=overall_status,
                raw_results=request.results
            )

        for result in request.results:
            nutrient_ranges = growth_stage_ranges.get(result.nutrient)
            if not nutrient_ranges:
                logger.info(f"No optimal range defined for {result.nutrient} at {request.growth_stage} for {request.crop_type}")
                continue

            optimal_min = nutrient_ranges.get("optimal_min", -float('inf'))
            optimal_max = nutrient_ranges.get("optimal_max", float('inf'))
            critical_low = nutrient_ranges.get("critical_low", -float('inf'))
            critical_high = nutrient_ranges.get("critical_high", float('inf'))

            severity = DeficiencySeverity.NONE
            recommendation = None

            if result.value < critical_low:
                severity = DeficiencySeverity.SEVERE
                recommendation = f"Severe deficiency of {result.nutrient}. Immediate action required. Consider foliar application or targeted soil amendment."
            elif result.value < optimal_min:
                severity = DeficiencySeverity.MODERATE
                recommendation = f"Moderate deficiency of {result.nutrient}. Consider soil or foliar application based on crop needs."
            elif result.value > critical_high:
                severity = DeficiencySeverity.SEVERE
                recommendation = f"Excess of {result.nutrient}. This can lead to toxicity or interfere with other nutrient uptake. Investigate source."
            elif result.value > optimal_max:
                severity = DeficiencySeverity.MILD
                recommendation = f"Slightly high level of {result.nutrient}. Monitor and ensure balanced fertilization."

            if severity != DeficiencySeverity.NONE:
                deficiencies.append(
                    NutrientDeficiency(
                        nutrient=result.nutrient,
                        severity=severity,
                        measured_value=result.value,
                        optimal_range={
                            "optimal_min": optimal_min,
                            "optimal_max": optimal_max,
                            "critical_low": critical_low,
                            "critical_high": critical_high
                        },
                        recommendation=recommendation
                    )
                )
                recommendations_summary_list.append(f"{result.nutrient} ({severity.value}): {recommendation}")

        if deficiencies:
            overall_status = "Deficiencies Detected"
        
        recommendations_summary = " ".join(recommendations_summary_list) if recommendations_summary_list else "No specific recommendations based on current data."

        return TissueTestAnalysisResponse(
            analysis_id=uuid4(),
            farm_id=request.farm_id,
            field_id=request.field_id,
            crop_type=request.crop_type,
            growth_stage=request.growth_stage,
            test_date=request.test_date,
            deficiencies=deficiencies,
            overall_status=overall_status,
            recommendations_summary=recommendations_summary,
            raw_results=request.results
        )

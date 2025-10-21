import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..schemas.micronutrient_schemas import (
    MicronutrientRecommendationRequest,
    MicronutrientRecommendationResponse,
    MicronutrientRecommendation,
    MicronutrientType,
    RecommendationPriority,
    MicronutrientLevel,
)
from ..models.micronutrient_models import MicronutrientCropThresholdsModel

class MicronutrientRecommendationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_crop_thresholds(self, crop_type: str, nutrient_type: MicronutrientType) -> Optional[MicronutrientCropThresholdsModel]:
        result = await self.db.execute(
            select(MicronutrientCropThresholdsModel)
            .filter(
                MicronutrientCropThresholdsModel.crop_type == crop_type,
                MicronutrientCropThresholdsModel.nutrient_type == nutrient_type
            )
        )
        return result.scalars().first()

    async def generate_recommendations(
        self, request: MicronutrientRecommendationRequest
    ) -> MicronutrientRecommendationResponse:
        recommendations: List[MicronutrientRecommendation] = []
        overall_status_messages: List[str] = []
        warnings: List[str] = []

        for current_level in request.current_micronutrient_levels:
            thresholds = await self.get_crop_thresholds(request.crop_type, current_level.nutrient_type)

            if not thresholds:
                warnings.append(f"No specific thresholds found for {request.crop_type} and {current_level.nutrient_type}. Using general guidelines.")
                # Fallback to general guidelines or skip if no general guidelines are available
                continue

            nutrient_recommendation: Optional[MicronutrientRecommendation] = None
            justification = ""
            priority = RecommendationPriority.OPTIMAL
            recommended_amount: Optional[float] = None
            unit: Optional[str] = None
            application_method: Optional[str] = None
            crop_impact: Optional[str] = None

            # Adjust thresholds based on soil pH and type (simplified for now)
            adjusted_min_optimal = thresholds.min_optimal_ppm
            adjusted_max_optimal = thresholds.max_optimal_ppm
            adjusted_deficiency_threshold = thresholds.deficiency_threshold_ppm
            adjusted_toxicity_threshold = thresholds.toxicity_threshold_ppm

            # pH impact on availability (simplified example)
            if current_level.nutrient_type == MicronutrientType.IRON and request.soil_ph > 7.0:
                justification += "Iron availability decreases in high pH soils. "
                adjusted_deficiency_threshold *= 1.1 # Slightly higher threshold for deficiency
            elif current_level.nutrient_type == MicronutrientType.MANGANESE and request.soil_ph > 6.5:
                justification += "Manganese availability decreases in high pH soils. "
                adjusted_deficiency_threshold *= 1.1
            elif current_level.nutrient_type == MicronutrientType.MOLYBDENUM and request.soil_ph < 6.0:
                justification += "Molybdenum availability decreases in low pH soils. "
                adjusted_deficiency_threshold *= 1.1

            if current_level.level_ppm < adjusted_deficiency_threshold:
                priority = RecommendationPriority.CRITICAL
                justification += f"Current {current_level.nutrient_type} level ({current_level.level_ppm} {current_level.unit}) is critically deficient for {request.crop_type}. "
                # Placeholder for calculation: aim for mid-optimal range
                recommended_amount = (adjusted_min_optimal + adjusted_max_optimal) / 2 - current_level.level_ppm
                unit = "kg/ha"
                application_method = "Soil application or foliar spray"
                crop_impact = "Severe yield loss and poor crop quality."
                overall_status_messages.append(f"{current_level.nutrient_type}: Deficient")
            elif current_level.level_ppm < adjusted_min_optimal:
                priority = RecommendationPriority.HIGH
                justification += f"Current {current_level.nutrient_type} level ({current_level.level_ppm} {current_level.unit}) is below optimal for {request.crop_type}. "
                recommended_amount = adjusted_min_optimal - current_level.level_ppm
                unit = "kg/ha"
                application_method = "Soil application or foliar spray"
                crop_impact = "Potential yield reduction and reduced crop vigor."
                overall_status_messages.append(f"{current_level.nutrient_type}: Low")
            elif current_level.level_ppm > adjusted_toxicity_threshold:
                priority = RecommendationPriority.CRITICAL
                justification += f"Current {current_level.nutrient_type} level ({current_level.level_ppm} {current_level.unit}) is at toxic levels for {request.crop_type}. "
                crop_impact = "Severe crop damage and potential plant death."
                overall_status_messages.append(f"{current_level.nutrient_type}: Toxic")
                warnings.append(f"High {current_level.nutrient_type} levels detected. Investigate source of excess.")
            elif current_level.level_ppm > adjusted_max_optimal:
                priority = RecommendationPriority.MEDIUM
                justification += f"Current {current_level.nutrient_type} level ({current_level.level_ppm} {current_level.unit}) is above optimal, approaching excess for {request.crop_type}. "
                crop_impact = "No immediate impact, but monitor for potential issues."
                overall_status_messages.append(f"{current_level.nutrient_type}: High")
            else:
                priority = RecommendationPriority.OPTIMAL
                justification += f"Current {current_level.nutrient_type} level ({current_level.level_ppm} {current_level.unit}) is optimal for {request.crop_type}. "
                crop_impact = "Expected healthy growth and yield."
                overall_status_messages.append(f"{current_level.nutrient_type}: Optimal")

            nutrient_recommendation = MicronutrientRecommendation(
                nutrient_type=current_level.nutrient_type,
                priority=priority,
                recommended_amount=recommended_amount if recommended_amount and recommended_amount > 0 else None,
                unit=unit,
                application_method=application_method,
                justification=justification.strip(),
                crop_impact=crop_impact,
            )
            recommendations.append(nutrient_recommendation)

        overall_status = "Optimal" if all(p == RecommendationPriority.OPTIMAL for p in [r.priority for r in recommendations]) else "Action Required"
        if any(p == RecommendationPriority.CRITICAL for p in [r.priority for r in recommendations]):
            overall_status = "Critical Deficiencies/Excesses Detected"

        return MicronutrientRecommendationResponse(
            request_id=str(uuid.uuid4()),
            recommendations=recommendations,
            overall_status=overall_status,
            warnings=warnings,
            metadata={
                "soil_ph": request.soil_ph,
                "soil_type": request.soil_type,
                "organic_matter_percent": request.organic_matter_percent,
                "crop_type": request.crop_type,
            },
        )

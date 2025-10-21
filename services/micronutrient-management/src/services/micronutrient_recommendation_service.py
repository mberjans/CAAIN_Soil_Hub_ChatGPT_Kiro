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

    def _calculate_recommended_amount(self, current_level_ppm: float, target_level_ppm: float, soil_type: str, organic_matter_percent: float) -> float:
        """
        Calculates a more realistic recommended amount.
        This is a simplified model and would ideally be replaced by a more complex agronomic model.
        Factors considered:
        - Difference between current and target levels
        - Soil type (e.g., sandy soils might require more frequent, smaller applications)
        - Organic matter (higher OM can chelate micronutrients, affecting availability)
        """
        difference = target_level_ppm - current_level_ppm
        if difference <= 0:
            return 0.0

        # Adjustments based on soil properties (simplified factors)
        soil_factor = 1.0
        if "sandy" in soil_type.lower():
            soil_factor = 1.2  # Sandy soils may need slightly more due to leaching
        elif "clay" in soil_type.lower():
            soil_factor = 0.8  # Clay soils might retain more, but also fix some nutrients

        om_factor = 1.0
        if organic_matter_percent > 5.0:
            om_factor = 0.9  # High OM can improve availability, or chelate
        elif organic_matter_percent < 1.0:
            om_factor = 1.1  # Low OM might need more

        # A base application rate per ppm difference, scaled
        base_rate_per_ppm = 0.5 # kg/ha per ppm difference (example value)

        recommended_amount = difference * base_rate_per_ppm * soil_factor * om_factor
        return round(recommended_amount, 2)

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
            # priority = RecommendationPriority.OPTIMAL # Base priority will be determined first
            recommended_amount: Optional[float] = None
            unit: Optional[str] = "kg/ha" # Default unit
            application_method: Optional[str] = "Soil application" # Default method
            crop_impact: Optional[str] = None

            # Adjust thresholds based on soil pH and type
            adjusted_min_optimal = thresholds.min_optimal_ppm
            adjusted_max_optimal = thresholds.max_optimal_ppm
            adjusted_deficiency_threshold = thresholds.deficiency_threshold_ppm
            adjusted_toxicity_threshold = thresholds.toxicity_threshold_ppm

            # pH impact on availability (modifies thresholds)
            if request.soil_ph < thresholds.soil_ph_min:
                justification += f"Low soil pH ({request.soil_ph}) may reduce {current_level.nutrient_type.value} availability. "
                if current_level.nutrient_type == MicronutrientType.MOLYBDENUM:
                    adjusted_deficiency_threshold *= 1.1 # Harder to get, so deficiency threshold effectively higher
                elif current_level.nutrient_type in [MicronutrientType.IRON, MicronutrientType.MANGANESE, MicronutrientType.ZINC]:
                    adjusted_toxicity_threshold *= 0.9 # Easier to get, so toxicity threshold effectively lower
            elif request.soil_ph > thresholds.soil_ph_max:
                justification += f"High soil pH ({request.soil_ph}) may reduce {current_level.nutrient_type.value} availability. "
                if current_level.nutrient_type in [MicronutrientType.IRON, MicronutrientType.MANGANESE, MicronutrientType.ZINC]:
                    adjusted_deficiency_threshold *= 1.1
                elif current_level.nutrient_type == MicronutrientType.MOLYBDENUM:
                    adjusted_toxicity_threshold *= 0.9

            # Determine BASE priority and impact based on current levels and adjusted thresholds
            base_priority = RecommendationPriority.OPTIMAL
            if current_level.level_ppm < adjusted_deficiency_threshold:
                base_priority = RecommendationPriority.CRITICAL
                justification += f"Current {current_level.nutrient_type.value} level ({current_level.level_ppm} {current_level.unit}) is critically deficient for {request.crop_type}. "
                crop_impact = "Severe yield loss, stunted growth, and poor crop quality. Immediate action required."
                overall_status_messages.append(f"{current_level.nutrient_type.value}: Critically Deficient")
            elif current_level.level_ppm < adjusted_min_optimal:
                base_priority = RecommendationPriority.HIGH
                justification += f"Current {current_level.nutrient_type.value} level ({current_level.level_ppm} {current_level.unit}) is below optimal for {request.crop_type}. "
                crop_impact = "Potential yield reduction and reduced crop vigor."
                overall_status_messages.append(f"{current_level.nutrient_type.value}: Low")
            elif current_level.level_ppm > adjusted_toxicity_threshold:
                base_priority = RecommendationPriority.CRITICAL
                justification += f"Current {current_level.nutrient_type.value} level ({current_level.level_ppm} {current_level.unit}) is at toxic levels for {request.crop_type}. "
                crop_impact = "Severe crop damage, reduced growth, nutrient imbalances, and potential plant death. Immediate action required."
                overall_status_messages.append(f"{current_level.nutrient_type.value}: Toxic")
                warnings.append(f"High {current_level.nutrient_type.value} levels detected. Investigate source of excess and consider remediation strategies.")
            elif current_level.level_ppm > adjusted_max_optimal:
                base_priority = RecommendationPriority.MEDIUM
                justification += f"Current {current_level.nutrient_type.value} level ({current_level.level_ppm} {current_level.unit}) is above optimal, approaching excess for {request.crop_type}. "
                crop_impact = "No immediate negative impact expected, but monitor for potential issues or nutrient imbalances."
                overall_status_messages.append(f"{current_level.nutrient_type.value}: High (Above Optimal)")
            else:
                base_priority = RecommendationPriority.OPTIMAL
                justification += f"Current {current_level.nutrient_type.value} level ({current_level.level_ppm} {current_level.unit}) is optimal for {request.crop_type}. "
                crop_impact = "Expected healthy growth and optimal yield potential."
                overall_status_messages.append(f"{current_level.nutrient_type.value}: Optimal")

            # Now, apply contextual factors to potentially ELEVATE priority (but not downgrade)
            final_priority = base_priority
            final_justification = justification
            final_crop_impact = crop_impact
            final_application_method = "Soil application" # Default

            # Growth stage impact
            if request.growth_stage and thresholds.growth_stage_impact:
                stage_impact = thresholds.growth_stage_impact.get(request.growth_stage)
                if stage_impact == "critical_uptake" and final_priority.value < RecommendationPriority.CRITICAL.value:
                    final_priority = RecommendationPriority.CRITICAL
                    final_justification += f"Current growth stage ({request.growth_stage}) is critical for {current_level.nutrient_type.value} uptake. "
                    final_application_method = "Foliar spray for rapid uptake"
                elif stage_impact == "high_demand" and final_priority.value < RecommendationPriority.HIGH.value:
                    final_priority = RecommendationPriority.HIGH
                    final_justification += f"Current growth stage ({request.growth_stage}) has high demand for {current_level.nutrient_type.value}. "

            # Determine recommended amount and application method based on final priority
            recommended_amount = None
            unit = "kg/ha"

            if final_priority == RecommendationPriority.CRITICAL:
                if current_level.level_ppm < adjusted_deficiency_threshold: # Only apply if deficient
                    target_level = (adjusted_min_optimal + adjusted_max_optimal) / 2
                    recommended_amount = self._calculate_recommended_amount(current_level.level_ppm, target_level, request.soil_type, request.organic_matter_percent)
                    final_application_method = "Foliar spray for rapid correction, followed by soil application if needed."
                else: # Critical due to toxicity
                    recommended_amount = 0.0
                    final_application_method = "No application. Focus on remediation (e.g., flushing, pH adjustment, organic matter addition)."
            elif final_priority == RecommendationPriority.HIGH:
                target_level = adjusted_min_optimal
                recommended_amount = self._calculate_recommended_amount(current_level.level_ppm, target_level, request.soil_type, request.organic_matter_percent)
                final_application_method = "Soil application or foliar spray, depending on urgency and growth stage."
            elif final_priority == RecommendationPriority.MEDIUM:
                final_application_method = "Monitor levels; no application recommended at this time."
            elif final_priority == RecommendationPriority.OPTIMAL:
                final_application_method = "Maintain current management practices; re-test next season."

            nutrient_recommendation = MicronutrientRecommendation(
                nutrient_type=current_level.nutrient_type,
                priority=final_priority,
                recommended_amount=recommended_amount if recommended_amount is not None and recommended_amount > 0 else (0.0 if recommended_amount == 0.0 else None),
                unit=unit,
                application_method=final_application_method,
                justification=final_justification.strip(),
                crop_impact=final_crop_impact,
            )
            recommendations.append(nutrient_recommendation)

        overall_status = "Optimal"
        has_critical = False
        has_high = False

        for rec in recommendations:
            if rec.priority.value == RecommendationPriority.CRITICAL.value:
                has_critical = True
                break # No need to check further if critical is found
            if rec.priority.value == RecommendationPriority.HIGH.value:
                has_high = True

        if has_critical:
            overall_status = "Critical Deficiencies/Excesses Detected"
        elif has_high:
            overall_status = "Action Required"
        elif not all(r.priority.value == RecommendationPriority.OPTIMAL.value for r in recommendations):
            # If not all are optimal, but no critical/high, it's still action required (e.g., Medium priority)
            overall_status = "Action Required"
        # Else, it remains "Optimal"

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

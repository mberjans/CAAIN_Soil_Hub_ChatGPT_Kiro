import logging
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime

from ..models.micronutrient_models import (
    MicronutrientName,
    MicronutrientLevel,
    DeficiencySymptom,
    DeficiencySeverity,
    MicronutrientDeficiencyAssessment,
    MicronutrientSource
)

logger = logging.getLogger(__name__)

class MicronutrientAssessmentService:
    """Service for assessing micronutrient deficiencies."""

    def __init__(self):
        # This could be loaded from a database or configuration file
        self.optimal_ranges = self._load_optimal_ranges()
        self.symptom_database = self._load_symptom_database()

    def _load_optimal_ranges(self) -> Dict[str, Dict[str, Any]]:
        """Loads optimal micronutrient ranges for different crops/soil types."""
        # Placeholder for a more complex data loading mechanism
        # In a real application, this would query a database based on crop_type and soil_type
        return {
            "CORN": {
                MicronutrientName.ZINC: {"soil_min": 1.0, "soil_max": 5.0, "tissue_min": 20.0, "tissue_max": 70.0},
                MicronutrientName.IRON: {"soil_min": 2.5, "soil_max": 20.0, "tissue_min": 50.0, "tissue_max": 250.0},
                MicronutrientName.BORON: {"soil_min": 0.5, "soil_max": 2.0, "tissue_min": 5.0, "tissue_max": 25.0},
            },
            "SOYBEAN": {
                MicronutrientName.ZINC: {"soil_min": 0.8, "soil_max": 4.0, "tissue_min": 20.0, "tissue_max": 50.0},
                MicronutrientName.IRON: {"soil_min": 2.0, "soil_max": 15.0, "tissue_min": 50.0, "tissue_max": 200.0},
                MicronutrientName.MANGANESE: {"soil_min": 5.0, "soil_max": 30.0, "tissue_min": 20.0, "tissue_max": 100.0},
            },
            # Add more crops and micronutrients
        }

    def _load_symptom_database(self) -> Dict[MicronutrientName, List[Dict[str, str]]]:
        """Loads a database of visual symptoms for micronutrient deficiencies."""
        # Placeholder for a more complex data loading mechanism
        return {
            MicronutrientName.ZINC: [
                {"description": "Stunted growth, interveinal chlorosis on new leaves", "severity": DeficiencySeverity.MODERATE.value, "location": "new leaves"},
                {"description": "White to yellow bands on either side of the midrib on young leaves", "severity": DeficiencySeverity.MILD.value, "location": "young leaves"},
            ],
            MicronutrientName.IRON: [
                {"description": "Severe interveinal chlorosis (yellowing) on young leaves, veins remain green", "severity": DeficiencySeverity.SEVERE.value, "location": "young leaves"},
                {"description": "Overall pale green to yellow appearance on new growth", "severity": DeficiencySeverity.MILD.value, "location": "new growth"},
            ],
            MicronutrientName.BORON: [
                {"description": "Stunted growth, brittle young leaves, poor fruit/seed set", "severity": DeficiencySeverity.SEVERE.value, "location": "growing points"},
                {"description": "Thickened, cracked stems and petioles", "severity": DeficiencySeverity.MODERATE.value, "location": "stems"},
            ],
            # Add more symptoms for other micronutrients
        }

    async def assess_deficiencies(
        self,
        farm_id: UUID,
        field_id: UUID,
        crop_type: str,
        growth_stage: str,
        soil_type: str,
        micronutrient_levels: List[MicronutrientLevel],
        visual_symptoms: Optional[List[DeficiencySymptom]] = None,
    ) -> MicronutrientDeficiencyAssessment:
        """Assesses micronutrient deficiencies based on provided data."""
        identified_deficiencies: List[MicronutrientName] = []
        overall_severity = DeficiencySeverity.NONE
        confidence_score = 0.0

        crop_optimal_ranges = self.optimal_ranges.get(crop_type.upper(), {})

        for level in micronutrient_levels:
            optimal_data = crop_optimal_ranges.get(level.micronutrient, {})
            min_val = None
            max_val = None

            if level.source == MicronutrientSource.SOIL_TEST:
                min_val = optimal_data.get("soil_min")
                max_val = optimal_data.get("soil_max")
            elif level.source == MicronutrientSource.TISSUE_TEST:
                min_val = optimal_data.get("tissue_min")
                max_val = optimal_data.get("tissue_max")

            if min_val is not None and level.value < min_val:
                identified_deficiencies.append(level.micronutrient)
                # Simple severity assignment for now
                if level.value < min_val * 0.5: # Arbitrary threshold for severe
                    overall_severity = self._get_higher_severity(overall_severity, DeficiencySeverity.SEVERE)
                else:
                    overall_severity = self._get_higher_severity(overall_severity, DeficiencySeverity.MODERATE)
            elif max_val is not None and level.value > max_val:
                logger.warning(f"Micronutrient {level.micronutrient} is above optimal range for {crop_type}.")
                # This could trigger a toxicity warning system

        # Incorporate visual symptoms
        if visual_symptoms:
            for symptom in visual_symptoms:
                if symptom.micronutrient not in identified_deficiencies:
                    identified_deficiencies.append(symptom.micronutrient)
                overall_severity = self._get_higher_severity(overall_severity, symptom.severity)

        # Calculate confidence score (simple heuristic for now)
        if micronutrient_levels and identified_deficiencies:
            confidence_score = 0.8 # High confidence if both data and deficiency found
        elif micronutrient_levels:
            confidence_score = 0.6 # Moderate if only data, no deficiency
        elif visual_symptoms:
            confidence_score = 0.7 # Moderate if only visual symptoms
        else:
            confidence_score = 0.3 # Low if no clear data

        return MicronutrientDeficiencyAssessment(
            farm_id=farm_id,
            field_id=field_id,
            crop_type=crop_type,
            growth_stage=growth_stage,
            soil_type=soil_type,
            assessed_micronutrients=micronutrient_levels,
            identified_deficiencies=list(set(identified_deficiencies)), # Remove duplicates
            visual_symptoms=visual_symptoms if visual_symptoms else [],
            overall_severity=overall_severity,
            confidence_score=confidence_score,
            assessment_date=datetime.now().isoformat().split("T")[0],
        )

    def _get_higher_severity(self, current: DeficiencySeverity, new: DeficiencySeverity) -> DeficiencySeverity:
        """Returns the higher of two deficiency severities."""
        severity_order = {DeficiencySeverity.NONE: 0, DeficiencySeverity.MILD: 1, DeficiencySeverity.MODERATE: 2, DeficiencySeverity.SEVERE: 3}
        if severity_order[new] > severity_order[current]:
            return new
        return current

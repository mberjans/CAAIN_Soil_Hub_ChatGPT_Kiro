from typing import List, Dict
from ..models.micronutrient_models import (
    Micronutrient,
    MicronutrientData,
    MicronutrientThresholds,
    ToxicityRiskLevel,
    ToxicityRiskAssessment,
    OverApplicationWarning,
    OverApplicationAssessment,
    MicronutrientRecommendation,
)

class MicronutrientService:
    """Service for micronutrient toxicity risk and over-application warnings."""

    def __init__(self):
        self.thresholds: Dict[Micronutrient, MicronutrientThresholds] = self._load_default_thresholds()

    def _load_default_thresholds(self) -> Dict[Micronutrient, MicronutrientThresholds]:
        """Loads default micronutrient thresholds (optimal, toxicity, over-application)."""
        # These thresholds are illustrative and should be replaced with scientifically validated data
        # based on crop type, soil type, and regional agricultural guidelines.
        return {
            Micronutrient.BORON: MicronutrientThresholds(
                micronutrient=Micronutrient.BORON, optimal_min_ppm=0.5, optimal_max_ppm=2.0,
                toxicity_threshold_ppm=5.0, over_application_threshold_ppm=3.0
            ),
            Micronutrient.CHLORINE: MicronutrientThresholds(
                micronutrient=Micronutrient.CHLORINE, optimal_min_ppm=20.0, optimal_max_ppm=200.0,
                toxicity_threshold_ppm=500.0, over_application_threshold_ppm=300.0
            ),
            Micronutrient.COPPER: MicronutrientThresholds(
                micronutrient=Micronutrient.COPPER, optimal_min_ppm=0.2, optimal_max_ppm=1.0,
                toxicity_threshold_ppm=5.0, over_application_threshold_ppm=2.0
            ),
            Micronutrient.IRON: MicronutrientThresholds(
                micronutrient=Micronutrient.IRON, optimal_min_ppm=2.5, optimal_max_ppm=10.0,
                toxicity_threshold_ppm=20.0, over_application_threshold_ppm=15.0
            ),
            Micronutrient.MANGANESE: MicronutrientThresholds(
                micronutrient=Micronutrient.MANGANESE, optimal_min_ppm=1.0, optimal_max_ppm=5.0,
                toxicity_threshold_ppm=15.0, over_application_threshold_ppm=10.0
            ),
            Micronutrient.MOLYBDENUM: MicronutrientThresholds(
                micronutrient=Micronutrient.MOLYBDENUM, optimal_min_ppm=0.01, optimal_max_ppm=0.1,
                toxicity_threshold_ppm=0.5, over_application_threshold_ppm=0.2
            ),
            Micronutrient.ZINC: MicronutrientThresholds(
                micronutrient=Micronutrient.ZINC, optimal_min_ppm=0.5, optimal_max_ppm=2.0,
                toxicity_threshold_ppm=10.0, over_application_threshold_ppm=5.0
            ),
            Micronutrient.NICKEL: MicronutrientThresholds(
                micronutrient=Micronutrient.NICKEL, optimal_min_ppm=0.1, optimal_max_ppm=0.5,
                toxicity_threshold_ppm=2.0, over_application_threshold_ppm=1.0
            ),
        }

    def get_thresholds_for_micronutrient(self, micronutrient: Micronutrient) -> MicronutrientThresholds:
        """Retrieves thresholds for a specific micronutrient."""
        if micronutrient not in self.thresholds:
            raise ValueError(f"Thresholds for {micronutrient.value} not found.")
        return self.thresholds[micronutrient]

    def assess_toxicity_risk(
        self, micronutrient_data: MicronutrientData
    ) -> ToxicityRiskAssessment:
        """Assesses the toxicity risk for a given micronutrient concentration."""
        thresholds = self.get_thresholds_for_micronutrient(micronutrient_data.micronutrient)
        concentration = micronutrient_data.concentration

        risk_level = ToxicityRiskLevel.LOW
        message = f"Current {micronutrient_data.micronutrient.value} concentration ({concentration}{micronutrient_data.unit}) is within safe limits."

        if concentration >= thresholds.toxicity_threshold_ppm:
            risk_level = ToxicityRiskLevel.CRITICAL
            message = f"CRITICAL: {micronutrient_data.micronutrient.value} concentration ({concentration}{micronutrient_data.unit}) is at or above toxicity threshold ({thresholds.toxicity_threshold_ppm}{thresholds.unit}). Immediate action required."
        elif concentration >= thresholds.over_application_threshold_ppm * 1.5: # Example: 1.5x over-application threshold
            risk_level = ToxicityRiskLevel.HIGH
            message = f"HIGH RISK: {micronutrient_data.micronutrient.value} concentration ({concentration}{micronutrient_data.unit}) is significantly above optimal range and approaching toxicity levels."
        elif concentration > thresholds.optimal_max_ppm:
            risk_level = ToxicityRiskLevel.MEDIUM
            message = f"MEDIUM RISK: {micronutrient_data.micronutrient.value} concentration ({concentration}{micronutrient_data.unit}) is above optimal range. Monitor closely."

        return ToxicityRiskAssessment(
            micronutrient=micronutrient_data.micronutrient,
            current_concentration=concentration,
            toxicity_threshold=thresholds.toxicity_threshold_ppm,
            risk_level=risk_level,
            message=message,
        )

    def assess_over_application_warning(
        self, micronutrient_data: MicronutrientData
    ) -> OverApplicationAssessment:
        """Assesses the warning level for potential over-application."""
        thresholds = self.get_thresholds_for_micronutrient(micronutrient_data.micronutrient)
        concentration = micronutrient_data.concentration

        warning_level = OverApplicationWarning.NONE
        message = f"Current {micronutrient_data.micronutrient.value} concentration ({concentration}{micronutrient_data.unit}) does not indicate over-application."
        recommended_action = None

        if concentration >= thresholds.toxicity_threshold_ppm:
            warning_level = OverApplicationWarning.CRITICAL
            message = f"CRITICAL: {micronutrient_data.micronutrient.value} concentration ({concentration}{micronutrient_data.unit}) is at toxicity levels. Stop all applications."
            recommended_action = "Immediately cease all applications containing this micronutrient and consult an agronomist."
        elif concentration >= thresholds.over_application_threshold_ppm:
            warning_level = OverApplicationWarning.WARNING
            message = f"WARNING: {micronutrient_data.micronutrient.value} concentration ({concentration}{micronutrient_data.unit}) is above the over-application threshold ({thresholds.over_application_threshold_ppm}{thresholds.unit}). Reduce or cease applications."
            recommended_action = "Review recent application rates and consider reducing or temporarily stopping applications."
        elif concentration > thresholds.optimal_max_ppm:
            warning_level = OverApplicationWarning.CAUTION
            message = f"CAUTION: {micronutrient_data.micronutrient.value} concentration ({concentration}{micronutrient_data.unit}) is above optimal. Monitor future applications."
            recommended_action = "Monitor soil/tissue levels closely and adjust future application plans."

        return OverApplicationAssessment(
            micronutrient=micronutrient_data.micronutrient,
            current_concentration=concentration,
            over_application_threshold=thresholds.over_application_threshold_ppm,
            warning_level=warning_level,
            message=message,
            recommended_action=recommended_action,
        )

    def get_micronutrient_recommendation(
        self, micronutrient_data: MicronutrientData, crop_type: str = "general"
    ) -> MicronutrientRecommendation:
        """Provides a general recommendation for micronutrient application based on current levels.
        This is a placeholder and needs to be expanded with crop-specific logic.
        """
        thresholds = self.get_thresholds_for_micronutrient(micronutrient_data.micronutrient)
        concentration = micronutrient_data.concentration

        if concentration < thresholds.optimal_min_ppm:
            required_amount = thresholds.optimal_min_ppm - concentration
            return MicronutrientRecommendation(
                micronutrient=micronutrient_data.micronutrient,
                required_amount=required_amount,
                unit="ppm (to reach optimal min)",
                notes=f"Current level is below optimal for {crop_type}. Consider application."
            )
        elif concentration > thresholds.optimal_max_ppm:
            return MicronutrientRecommendation(
                micronutrient=micronutrient_data.micronutrient,
                required_amount=0.0,
                unit="ppm",
                notes=f"Current level is above optimal for {crop_type}. No application recommended."
            )
        else:
            return MicronutrientRecommendation(
                micronutrient=micronutrient_data.micronutrient,
                required_amount=0.0,
                unit="ppm",
                notes=f"Current level is within optimal range for {crop_type}. No application needed."
            )

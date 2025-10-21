from typing import List, Dict, Any
from uuid import UUID

from ..models.micronutrient_models import (
    MicronutrientName,
    MicronutrientDeficiencyAssessment,
    Recommendation,
    DeficiencySeverity
)

class MicronutrientRecommendationService:
    """Service for generating micronutrient recommendations."""

    def __init__(self):
        self.recommendation_database = self._load_recommendation_database()

    def _load_recommendation_database(self) -> Dict[MicronutrientName, Dict[DeficiencySeverity, Dict[str, Any]]]:
        """Loads a database of recommendations for different micronutrients and severities."""
        # Placeholder for a more complex data loading mechanism
        return {
            MicronutrientName.ZINC: {
                DeficiencySeverity.MILD: {
                    "action": "Foliar application",
                    "product": "Zinc Sulfate (35% Zn)",
                    "rate": "0.5-1.0 kg/ha",
                    "unit": "kg/ha",
                    "timing": "Early vegetative stage",
                    "method": "Foliar spray",
                    "notes": "Apply when plants are actively growing. Repeat if symptoms persist.",
                    "cost_estimate": 15.0,
                },
                DeficiencySeverity.MODERATE: {
                    "action": "Soil amendment / Foliar application",
                    "product": "Zinc Sulfate (35% Zn)",
                    "rate": "2.0-5.0 kg/ha (soil) / 1.0-2.0 kg/ha (foliar)",
                    "unit": "kg/ha",
                    "timing": "Pre-plant or early vegetative stage",
                    "method": "Broadcast (soil) / Foliar spray",
                    "notes": "Consider soil application if deficiency is persistent. Follow up with foliar if needed.",
                    "cost_estimate": 30.0,
                },
                DeficiencySeverity.SEVERE: {
                    "action": "Soil amendment + Foliar application",
                    "product": "Zinc Sulfate (35% Zn)",
                    "rate": "5.0-10.0 kg/ha (soil) / 2.0-3.0 kg/ha (foliar)",
                    "unit": "kg/ha",
                    "timing": "Pre-plant and early vegetative stage",
                    "method": "Broadcast (soil) / Foliar spray",
                    "notes": "Severe deficiencies require aggressive treatment. Soil test after harvest to confirm improvement.",
                    "cost_estimate": 50.0,
                },
            },
            MicronutrientName.IRON: {
                DeficiencySeverity.MILD: {
                    "action": "Foliar application",
                    "product": "Chelated Iron (e.g., Fe-EDDHA)",
                    "rate": "0.2-0.5 kg/ha",
                    "unit": "kg/ha",
                    "timing": "Early vegetative stage",
                    "method": "Foliar spray",
                    "notes": "Iron deficiencies are often pH-induced. Address soil pH if possible.",
                    "cost_estimate": 20.0,
                },
                DeficiencySeverity.MODERATE: {
                    "action": "Foliar application",
                    "product": "Chelated Iron (e.g., Fe-EDDHA)",
                    "rate": "0.5-1.0 kg/ha",
                    "unit": "kg/ha",
                    "timing": "Early vegetative stage, repeat as needed",
                    "method": "Foliar spray",
                    "notes": "Multiple applications may be necessary. Monitor new growth.",
                    "cost_estimate": 40.0,
                },
                DeficiencySeverity.SEVERE: {
                    "action": "Foliar application",
                    "product": "Chelated Iron (e.g., Fe-EDDHA)",
                    "rate": "1.0-2.0 kg/ha",
                    "unit": "kg/ha",
                    "timing": "Immediate, repeat every 7-10 days",
                    "method": "Foliar spray",
                    "notes": "Critical situation. Ensure good spray coverage. Consider soil pH adjustment for long-term solution.",
                    "cost_estimate": 60.0,
                },
            },
            MicronutrientName.BORON: {
                DeficiencySeverity.MILD: {
                    "action": "Foliar application",
                    "product": "Solubor (20.5% B)",
                    "rate": "0.5-1.0 kg/ha",
                    "unit": "kg/ha",
                    "timing": "Pre-bloom or early vegetative stage",
                    "method": "Foliar spray",
                    "notes": "Boron is crucial for flowering and fruit set.",
                    "cost_estimate": 10.0,
                },
                DeficiencySeverity.MODERATE: {
                    "action": "Soil amendment / Foliar application",
                    "product": "Granular Boron (10-15% B) / Solubor",
                    "rate": "1.0-2.0 kg/ha (soil) / 1.0-1.5 kg/ha (foliar)",
                    "unit": "kg/ha",
                    "timing": "Pre-plant (soil) or pre-bloom (foliar)",
                    "method": "Broadcast (soil) / Foliar spray",
                    "notes": "Boron has a narrow range between deficiency and toxicity. Apply carefully.",
                    "cost_estimate": 25.0,
                },
                DeficiencySeverity.SEVERE: {
                    "action": "Soil amendment + Foliar application",
                    "product": "Granular Boron (10-15% B) / Solubor",
                    "rate": "2.0-4.0 kg/ha (soil) / 1.5-2.0 kg/ha (foliar)",
                    "unit": "kg/ha",
                    "timing": "Pre-plant (soil) and pre-bloom (foliar)",
                    "method": "Broadcast (soil) / Foliar spray",
                    "notes": "Avoid over-application to prevent toxicity. Ensure even distribution.",
                    "cost_estimate": 40.0,
                },
            },
            MicronutrientName.MANGANESE: {
                DeficiencySeverity.MILD: {
                    "action": "Foliar application",
                    "product": "Manganese Sulfate (32% Mn)",
                    "rate": "0.5-1.0 kg/ha",
                    "unit": "kg/ha",
                    "timing": "Early vegetative stage",
                    "method": "Foliar spray",
                    "notes": "Often seen in high pH soils. Ensure good spray coverage.",
                    "cost_estimate": 12.0,
                },
                DeficiencySeverity.MODERATE: {
                    "action": "Foliar application",
                    "product": "Manganese Sulfate (32% Mn)",
                    "rate": "1.0-2.0 kg/ha",
                    "unit": "kg/ha",
                    "timing": "Early vegetative stage, repeat as needed",
                    "method": "Foliar spray",
                    "notes": "Multiple applications may be necessary. Soil pH adjustment can help long-term.",
                    "cost_estimate": 25.0,
                },
                DeficiencySeverity.SEVERE: {
                    "action": "Foliar application",
                    "product": "Manganese Sulfate (32% Mn)",
                    "rate": "2.0-3.0 kg/ha",
                    "unit": "kg/ha",
                    "timing": "Immediate, repeat every 7-10 days",
                    "method": "Foliar spray",
                    "notes": "Critical situation. Consider soil application if foliar is not effective.",
                    "cost_estimate": 40.0,
                },
            },
            # Add more recommendations for other micronutrients
        }

    async def get_recommendations(
        self,
        assessment: MicronutrientDeficiencyAssessment,
    ) -> List[Recommendation]:
        """Generates recommendations based on a deficiency assessment."""
        recommendations: List[Recommendation] = []

        for deficient_micro in assessment.identified_deficiencies:
            micro_recs = self.recommendation_database.get(deficient_micro)
            if micro_recs:
                # Prioritize recommendations based on overall severity or specific micronutrient severity
                # For simplicity, use overall_severity for now
                severity_rec = micro_recs.get(assessment.overall_severity)
                if not severity_rec:
                    # Fallback to a general recommendation if specific severity not found
                    severity_rec = micro_recs.get(DeficiencySeverity.MODERATE) or list(micro_recs.values())[0]

                if severity_rec:
                    recommendations.append(Recommendation(
                        assessment_id=assessment.assessment_id,
                        micronutrient=deficient_micro,
                        action=severity_rec["action"],
                        product=severity_rec["product"],
                        rate=severity_rec["rate"],
                        unit=severity_rec["unit"],
                        timing=severity_rec["timing"],
                        method=severity_rec["method"],
                        notes=severity_rec.get("notes"),
                        expected_response="Improved crop health and yield",
                        cost_estimate=severity_rec.get("cost_estimate"),
                        environmental_impact="Minimal with proper application",
                    ))
        return recommendations

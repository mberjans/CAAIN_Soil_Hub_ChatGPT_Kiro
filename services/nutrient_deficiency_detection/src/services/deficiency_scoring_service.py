from typing import List, Dict, Tuple
from collections import defaultdict

from services.nutrient_deficiency_detection.src.models.deficiency_models import (
    Nutrient, Severity, DetectedDeficiency, NutrientDeficiencyScore
)

class NutrientDeficiencyScoringService:
    def __init__(self):
        # Weights for different factors contributing to the score
        self.confidence_weight = 0.4
        self.severity_weight = 0.3
        self.affected_area_weight = 0.2
        self.symptom_count_weight = 0.1

        # Mapping severity to a numerical value for scoring
        self.severity_values = {
            Severity.MILD: 20,
            Severity.MODERATE: 50,
            Severity.SEVERE: 80,
            Severity.CRITICAL: 100,
        }

    def calculate_deficiency_score(
        self, detected_deficiencies: List[DetectedDeficiency]
    ) -> NutrientDeficiencyScore:
        """
        Calculates an overall nutrient deficiency score and individual nutrient scores.

        Args:
            detected_deficiencies: A list of DetectedDeficiency objects.

        Returns:
            A NutrientDeficiencyScore object containing overall and individual scores.
        """
        if not detected_deficiencies:
            return NutrientDeficiencyScore(
                overall_score=0.0,
                nutrient_scores={},
                highest_priority_nutrient=None,
                recommendation_priority=Severity.MILD,
                detailed_analysis="No deficiencies detected.",
            )

        nutrient_raw_scores = defaultdict(float)
        nutrient_detection_counts = defaultdict(int)

        for detection in detected_deficiencies:
            # Convert severity to a numerical value
            severity_score = self.severity_values.get(detection.severity, 0)

            # Calculate a weighted score for each detection
            weighted_score = (
                detection.confidence * self.confidence_weight * 100
                + severity_score * self.severity_weight
                + detection.affected_area_percent * (self.affected_area_weight / 100) * 100
                + len(detection.symptoms) * self.symptom_count_weight * 10
            )
            # Normalize weighted score to a 0-100 range, assuming max symptom count of 10 for simplicity
            # Max possible score: 100*0.4 + 100*0.3 + 100*0.2 + 10*0.1*10 = 40 + 30 + 20 + 10 = 100

            nutrient_raw_scores[detection.nutrient] += weighted_score
            nutrient_detection_counts[detection.nutrient] += 1

        nutrient_scores = {}
        for nutrient, raw_score in nutrient_raw_scores.items():
            # Average the scores if multiple detections for the same nutrient
            nutrient_scores[nutrient] = round(raw_score / nutrient_detection_counts[nutrient], 2)

        overall_score, highest_priority_nutrient, recommendation_priority = self._determine_overall_priority(
            nutrient_scores
        )

        detailed_analysis = self._generate_detailed_analysis(nutrient_scores, highest_priority_nutrient)

        return NutrientDeficiencyScore(
            overall_score=overall_score,
            nutrient_scores=nutrient_scores,
            highest_priority_nutrient=highest_priority_nutrient,
            recommendation_priority=recommendation_priority,
            detailed_analysis=detailed_analysis,
        )

    def _determine_overall_priority(
        self, nutrient_scores: Dict[Nutrient, float]
    ) -> Tuple[float, Optional[Nutrient], Severity]:
        """
        Determines the overall score, highest priority nutrient, and recommendation priority.
        """
        if not nutrient_scores:
            return 0.0, None, Severity.MILD

        max_score = 0.0
        highest_priority_nutrient = None

        for nutrient, score in nutrient_scores.items():
            if score > max_score:
                max_score = score
                highest_priority_nutrient = nutrient

        # Map the highest score back to a Severity level
        if max_score >= 90:
            recommendation_priority = Severity.CRITICAL
        elif max_score >= 70:
            recommendation_priority = Severity.SEVERE
        elif max_score >= 40:
            recommendation_priority = Severity.MODERATE
        elif max_score >= 10:
            recommendation_priority = Severity.MILD
        else:
            recommendation_priority = Severity.MILD # Default for very low scores

        # Overall score could be the max score or an average, let's use max for now to highlight critical issues
        overall_score = round(max_score, 2)

        return overall_score, highest_priority_nutrient, recommendation_priority

    def _generate_detailed_analysis(
        self, nutrient_scores: Dict[Nutrient, float], highest_priority_nutrient: Optional[Nutrient]
    ) -> str:
        """
        Generates a detailed analysis string based on the scores.
        """
        if not nutrient_scores:
            return "No nutrient deficiencies detected."

        analysis_parts = []
        if highest_priority_nutrient:
            analysis_parts.append(
                f"The most critical deficiency appears to be {highest_priority_nutrient.value.capitalize()} "
                f"with a score of {nutrient_scores[highest_priority_nutrient]}."
            )

        sorted_nutrients = sorted(nutrient_scores.items(), key=lambda item: item[1], reverse=True)
        other_deficiencies = [
            f"{nutrient.value.capitalize()}: {score}"
            for nutrient, score in sorted_nutrients
            if nutrient != highest_priority_nutrient
        ]

        if other_deficiencies:
            analysis_parts.append("Other detected deficiencies include: " + "; ".join(other_deficiencies) + ".")

        return " ".join(analysis_parts).strip()

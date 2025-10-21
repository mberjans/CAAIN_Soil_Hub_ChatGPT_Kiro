import pytest
from datetime import datetime

from services.nutrient_deficiency_detection.src.models.deficiency_models import (
    Nutrient, Severity, Symptom, DetectedDeficiency, NutrientDeficiencyScore
)
from services.nutrient_deficiency_detection.src.services.deficiency_scoring_service import NutrientDeficiencyScoringService

class TestNutrientDeficiencyScoringService:

    @pytest.fixture
    def scoring_service(self):
        return NutrientDeficiencyScoringService()

    @pytest.fixture
    def mild_nitrogen_deficiency(self):
        return DetectedDeficiency(
            nutrient=Nutrient.NITROGEN,
            confidence=0.7,
            severity=Severity.MILD,
            affected_area_percent=10.0,
            symptoms=[
                Symptom(name="chlorosis", location="older leaves"),
            ],
            source="image_analysis",
        )

    @pytest.fixture
    def moderate_phosphorus_deficiency(self):
        return DetectedDeficiency(
            nutrient=Nutrient.PHOSPHORUS,
            confidence=0.8,
            severity=Severity.MODERATE,
            affected_area_percent=30.0,
            symptoms=[
                Symptom(name="purpling", location="leaf margins"),
                Symptom(name="stunted growth", location="entire plant"),
            ],
            source="manual_input",
        )

    @pytest.fixture
    def severe_potassium_deficiency(self):
        return DetectedDeficiency(
            nutrient=Nutrient.POTASSIUM,
            confidence=0.9,
            severity=Severity.SEVERE,
            affected_area_percent=60.0,
            symptoms=[
                Symptom(name="scorching", location="leaf tips"),
                Symptom(name="weak stems", location="entire plant"),
                Symptom(name="poor fruit development", location="fruit"),
            ],
            source="image_analysis",
        )

    @pytest.fixture
    def critical_iron_deficiency(self):
        return DetectedDeficiency(
            nutrient=Nutrient.IRON,
            confidence=0.95,
            severity=Severity.CRITICAL,
            affected_area_percent=90.0,
            symptoms=[
                Symptom(name="interveinal chlorosis", location="new growth"),
                Symptom(name="stunted growth", location="entire plant"),
                Symptom(name="necrosis", location="new growth"),
                Symptom(name="yellowing", location="new growth"),
            ],
            source="image_analysis",
        )

    def test_calculate_deficiency_score_no_deficiencies(self, scoring_service):
        score = scoring_service.calculate_deficiency_score([])
        assert score.overall_score == 0.0
        assert not score.nutrient_scores
        assert score.highest_priority_nutrient is None
        assert score.recommendation_priority == Severity.MILD
        assert score.detailed_analysis == "No deficiencies detected."

    def test_calculate_deficiency_score_mild_nitrogen(self, scoring_service, mild_nitrogen_deficiency):
        score = scoring_service.calculate_deficiency_score([mild_nitrogen_deficiency])
        assert score.overall_score > 0
        assert Nutrient.NITROGEN in score.nutrient_scores
        assert score.highest_priority_nutrient == Nutrient.NITROGEN
        assert score.recommendation_priority == Severity.MILD
        assert "nitrogen" in score.detailed_analysis.lower()

    def test_calculate_deficiency_score_moderate_phosphorus(self, scoring_service, moderate_phosphorus_deficiency):
        score = scoring_service.calculate_deficiency_score([moderate_phosphorus_deficiency])
        assert score.overall_score > scoring_service.severity_values[Severity.MILD]
        assert Nutrient.PHOSPHORUS in score.nutrient_scores
        assert score.highest_priority_nutrient == Nutrient.PHOSPHORUS
        assert score.recommendation_priority == Severity.MODERATE
        assert "phosphorus" in score.detailed_analysis.lower()

    def test_calculate_deficiency_score_severe_potassium(self, scoring_service, severe_potassium_deficiency):
        score = scoring_service.calculate_deficiency_score([severe_potassium_deficiency])
        assert score.overall_score > scoring_service.severity_values[Severity.MODERATE]
        assert Nutrient.POTASSIUM in score.nutrient_scores
        assert score.highest_priority_nutrient == Nutrient.POTASSIUM
        assert score.recommendation_priority == Severity.SEVERE
        assert "potassium" in score.detailed_analysis.lower()

    def test_calculate_deficiency_score_critical_iron(self, scoring_service, critical_iron_deficiency):
        score = scoring_service.calculate_deficiency_score([critical_iron_deficiency])
        assert score.overall_score > scoring_service.severity_values[Severity.SEVERE]
        assert Nutrient.IRON in score.nutrient_scores
        assert score.highest_priority_nutrient == Nutrient.IRON
        assert score.recommendation_priority == Severity.CRITICAL
        assert "iron" in score.detailed_analysis.lower()

    def test_calculate_deficiency_score_multiple_deficiencies(self, scoring_service, mild_nitrogen_deficiency, moderate_phosphorus_deficiency, severe_potassium_deficiency):
        deficiencies = [mild_nitrogen_deficiency, moderate_phosphorus_deficiency, severe_potassium_deficiency]
        score = scoring_service.calculate_deficiency_score(deficiencies)

        assert score.overall_score == pytest.approx(score.nutrient_scores[Nutrient.POTASSIUM], rel=0.01)
        assert score.highest_priority_nutrient == Nutrient.POTASSIUM
        assert score.recommendation_priority == Severity.SEVERE
        assert Nutrient.NITROGEN in score.nutrient_scores
        assert Nutrient.PHOSPHORUS in score.nutrient_scores
        assert Nutrient.POTASSIUM in score.nutrient_scores
        assert "potassium" in score.detailed_analysis.lower()
        assert "nitrogen" in score.detailed_analysis.lower()
        assert "phosphorus" in score.detailed_analysis.lower()

    def test_calculate_deficiency_score_multiple_detections_same_nutrient(self, scoring_service, mild_nitrogen_deficiency):
        # Simulate two detections for Nitrogen, one mild, one slightly more severe
        mild_nitrogen_deficiency_2 = DetectedDeficiency(
            nutrient=Nutrient.NITROGEN,
            confidence=0.8,
            severity=Severity.MODERATE,
            affected_area_percent=15.0,
            symptoms=[
                Symptom(name="chlorosis", location="older leaves"),
                Symptom(name="stunted growth", location="entire plant"),
            ],
            source="manual_input",
        )
        deficiencies = [mild_nitrogen_deficiency, mild_nitrogen_deficiency_2]
        score = scoring_service.calculate_deficiency_score(deficiencies)

        assert Nutrient.NITROGEN in score.nutrient_scores
        # The score should be an average or weighted average of the two detections
        # Let's check if it's within a reasonable range, not just one of the two
        assert score.nutrient_scores[Nutrient.NITROGEN] > scoring_service.severity_values[Severity.MILD]
        assert score.nutrient_scores[Nutrient.NITROGEN] < scoring_service.severity_values[Severity.SEVERE]
        assert score.highest_priority_nutrient == Nutrient.NITROGEN

    def test_detailed_analysis_generation(self, scoring_service, mild_nitrogen_deficiency, severe_potassium_deficiency):
        deficiencies = [mild_nitrogen_deficiency, severe_potassium_deficiency]
        score = scoring_service.calculate_deficiency_score(deficiencies)
        analysis = score.detailed_analysis

        assert "potassium" in analysis.lower()
        assert "nitrogen" in analysis.lower()
        assert "most critical deficiency appears to be potassium" in analysis.lower()
        assert "other detected deficiencies include" in analysis.lower()

    def test_severity_mapping(self, scoring_service):
        assert scoring_service.severity_values[Severity.MILD] == 20
        assert scoring_service.severity_values[Severity.MODERATE] == 50
        assert scoring_service.severity_values[Severity.SEVERE] == 80
        assert scoring_service.severity_values[Severity.CRITICAL] == 100

    def test_overall_score_calculation_logic(self, scoring_service, mild_nitrogen_deficiency, critical_iron_deficiency):
        deficiencies = [mild_nitrogen_deficiency, critical_iron_deficiency]
        score = scoring_service.calculate_deficiency_score(deficiencies)

        # Overall score should reflect the highest priority, which is critical iron
        assert score.overall_score == pytest.approx(score.nutrient_scores[Nutrient.IRON], rel=0.01)
        assert score.highest_priority_nutrient == Nutrient.IRON
        assert score.recommendation_priority == Severity.CRITICAL

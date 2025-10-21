import pytest
from unittest.mock import MagicMock

from src.services.micronutrient_service import MicronutrientService
from src.models.micronutrient_models import (
    Micronutrient,
    MicronutrientData,
    ToxicityRiskLevel,
    OverApplicationWarning,
    MicronutrientThresholds
)

@pytest.fixture
def micronutrient_service():
    return MicronutrientService()

@pytest.fixture
def mock_thresholds():
    return {
        Micronutrient.BORON: MicronutrientThresholds(
            micronutrient=Micronutrient.BORON, optimal_min_ppm=0.5, optimal_max_ppm=2.0,
            toxicity_threshold_ppm=5.0, over_application_threshold_ppm=3.0
        ),
        Micronutrient.ZINC: MicronutrientThresholds(
            micronutrient=Micronutrient.ZINC, optimal_min_ppm=0.5, optimal_max_ppm=2.0,
            toxicity_threshold_ppm=10.0, over_application_threshold_ppm=5.0
        ),
    }

def test_load_default_thresholds(micronutrient_service):
    assert len(micronutrient_service.thresholds) == 8
    assert Micronutrient.BORON in micronutrient_service.thresholds
    assert micronutrient_service.thresholds[Micronutrient.BORON].optimal_max_ppm == 2.0

def test_get_thresholds_for_micronutrient_success(micronutrient_service):
    thresholds = micronutrient_service.get_thresholds_for_micronutrient(Micronutrient.COPPER)
    assert thresholds.micronutrient == Micronutrient.COPPER
    assert thresholds.toxicity_threshold_ppm == 5.0

def test_get_thresholds_for_micronutrient_not_found(micronutrient_service):
    with pytest.raises(ValueError, match="not a valid Micronutrient"):
        micronutrient_service.get_thresholds_for_micronutrient(Micronutrient("NonExistent"))

# --- Toxicity Risk Assessment Tests ---

def test_assess_toxicity_risk_low(micronutrient_service):
    data = MicronutrientData(micronutrient=Micronutrient.BORON, concentration=1.0)
    assessment = micronutrient_service.assess_toxicity_risk(data)
    assert assessment.risk_level == ToxicityRiskLevel.LOW
    assert "within safe limits" in assessment.message

def test_assess_toxicity_risk_medium(micronutrient_service):
    data = MicronutrientData(micronutrient=Micronutrient.BORON, concentration=2.5) # Above optimal_max (2.0)
    assessment = micronutrient_service.assess_toxicity_risk(data)
    assert assessment.risk_level == ToxicityRiskLevel.MEDIUM
    assert "above optimal range" in assessment.message

def test_assess_toxicity_risk_high(micronutrient_service):
    data = MicronutrientData(micronutrient=Micronutrient.BORON, concentration=4.6) # Above 1.5x over_application (3.0 * 1.5 = 4.5)
    assessment = micronutrient_service.assess_toxicity_risk(data)
    assert assessment.risk_level == ToxicityRiskLevel.HIGH
    assert "approaching toxicity levels" in assessment.message

def test_assess_toxicity_risk_critical(micronutrient_service):
    data = MicronutrientData(micronutrient=Micronutrient.BORON, concentration=5.5) # Above toxicity (5.0)
    assessment = micronutrient_service.assess_toxicity_risk(data)
    assert assessment.risk_level == ToxicityRiskLevel.CRITICAL
    assert "CRITICAL" in assessment.message

# --- Over-Application Warning Tests ---

def test_assess_over_application_none(micronutrient_service):
    data = MicronutrientData(micronutrient=Micronutrient.ZINC, concentration=1.5)
    assessment = micronutrient_service.assess_over_application_warning(data)
    assert assessment.warning_level == OverApplicationWarning.NONE
    assert "does not indicate over-application" in assessment.message
    assert assessment.recommended_action is None

def test_assess_over_application_caution(micronutrient_service):
    data = MicronutrientData(micronutrient=Micronutrient.ZINC, concentration=3.0) # Above optimal_max (2.0)
    assessment = micronutrient_service.assess_over_application_warning(data)
    assert assessment.warning_level == OverApplicationWarning.CAUTION
    assert "above optimal" in assessment.message
    assert "Monitor soil/tissue levels" in assessment.recommended_action

def test_assess_over_application_warning_level(micronutrient_service):
    data = MicronutrientData(micronutrient=Micronutrient.ZINC, concentration=6.0) # Above over_application_threshold (5.0)
    assessment = micronutrient_service.assess_over_application_warning(data)
    assert assessment.warning_level == OverApplicationWarning.WARNING
    assert "above the over-application threshold" in assessment.message
    assert "Review recent application rates" in assessment.recommended_action

def test_assess_over_application_critical(micronutrient_service):
    data = MicronutrientData(micronutrient=Micronutrient.ZINC, concentration=10.5) # Above toxicity (10.0)
    assessment = micronutrient_service.assess_over_application_warning(data)
    assert assessment.warning_level == OverApplicationWarning.CRITICAL
    assert "toxicity levels" in assessment.message
    assert "Immediately cease all applications" in assessment.recommended_action

# --- Micronutrient Recommendation Tests ---

def test_get_micronutrient_recommendation_deficient(micronutrient_service):
    data = MicronutrientData(micronutrient=Micronutrient.COPPER, concentration=0.1) # Below optimal_min (0.2)
    recommendation = micronutrient_service.get_micronutrient_recommendation(data)
    assert recommendation.required_amount > 0
    assert "below optimal" in recommendation.notes

def test_get_micronutrient_recommendation_optimal(micronutrient_service):
    data = MicronutrientData(micronutrient=Micronutrient.COPPER, concentration=0.5) # Within optimal range
    recommendation = micronutrient_service.get_micronutrient_recommendation(data)
    assert recommendation.required_amount == 0.0
    assert "within optimal range" in recommendation.notes

def test_get_micronutrient_recommendation_excess(micronutrient_service):
    data = MicronutrientData(micronutrient=Micronutrient.COPPER, concentration=1.5) # Above optimal_max (1.0)
    recommendation = micronutrient_service.get_micronutrient_recommendation(data)
    assert recommendation.required_amount == 0.0
    assert "above optimal" in recommendation.notes

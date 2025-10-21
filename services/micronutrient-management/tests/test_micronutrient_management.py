import pytest
from uuid import UUID
from datetime import datetime

from src.models.micronutrient_models import (
    MicronutrientName,
    MicronutrientSource,
    DeficiencySeverity,
    MicronutrientLevel,
    DeficiencySymptom,
    MicronutrientDeficiencyAssessment,
    Recommendation
)
from src.services.micronutrient_assessment_service import MicronutrientAssessmentService
from src.services.micronutrient_recommendation_service import MicronutrientRecommendationService

# --- Test Data Models ---

def test_micronutrient_level_model():
    level = MicronutrientLevel(
        micronutrient=MicronutrientName.ZINC,
        value=0.8,
        unit="ppm",
        source=MicronutrientSource.SOIL_TEST,
        optimal_min=1.0,
        optimal_max=5.0
    )
    assert level.micronutrient == MicronutrientName.ZINC
    assert level.value == 0.8

def test_deficiency_symptom_model():
    symptom = DeficiencySymptom(
        micronutrient=MicronutrientName.IRON,
        description="Interveinal chlorosis on young leaves",
        severity=DeficiencySeverity.MODERATE,
        location_on_plant="young leaves"
    )
    assert symptom.micronutrient == MicronutrientName.IRON
    assert symptom.severity == DeficiencySeverity.MODERATE

def test_micronutrient_deficiency_assessment_model():
    assessment = MicronutrientDeficiencyAssessment(
        farm_id=UUID('a1b2c3d4-e5f6-7890-1234-567890abcdef'),
        field_id=UUID('f1e2d3c4-b5a6-0987-6543-210fedcba987'),
        crop_type="Corn",
        growth_stage="V6",
        soil_type="Loam",
        assessed_micronutrients=[],
        identified_deficiencies=[MicronutrientName.ZINC],
        overall_severity=DeficiencySeverity.MILD,
        confidence_score=0.7,
        assessment_date=datetime.now().isoformat().split("T")[0]
    )
    assert assessment.crop_type == "Corn"
    assert MicronutrientName.ZINC in assessment.identified_deficiencies

def test_recommendation_model():
    recommendation = Recommendation(
        assessment_id=UUID('a1b2c3d4-e5f6-7890-1234-567890abcdef'),
        micronutrient=MicronutrientName.ZINC,
        action="Foliar application",
        product="Zinc Sulfate",
        rate="1 kg/ha",
        unit="kg/ha",
        timing="Early vegetative stage",
        method="Foliar spray"
    )
    assert recommendation.micronutrient == MicronutrientName.ZINC
    assert recommendation.rate == "1 kg/ha"

# --- Test MicronutrientAssessmentService ---

@pytest.fixture
def assessment_service():
    return MicronutrientAssessmentService()

@pytest.mark.asyncio
async def test_assess_deficiencies_no_deficiency(assessment_service):
    farm_id = UUID('a1b2c3d4-e5f6-7890-1234-567890abcdef')
    field_id = UUID('f1e2d3c4-b5a6-0987-6543-210fedcba987')
    micronutrient_levels = [
        MicronutrientLevel(
            micronutrient=MicronutrientName.ZINC,
            value=2.0,
            unit="ppm",
            source=MicronutrientSource.SOIL_TEST,
            optimal_min=1.0,
            optimal_max=5.0
        )
    ]
    assessment = await assessment_service.assess_deficiencies(
        farm_id=farm_id,
        field_id=field_id,
        crop_type="Corn",
        growth_stage="V6",
        soil_type="Loam",
        micronutrient_levels=micronutrient_levels
    )
    assert not assessment.identified_deficiencies
    assert assessment.overall_severity == DeficiencySeverity.NONE
    assert assessment.confidence_score == 0.6

@pytest.mark.asyncio
async def test_assess_deficiencies_with_soil_deficiency(assessment_service):
    farm_id = UUID('a1b2c3d4-e5f6-7890-1234-567890abcdef')
    field_id = UUID('f1e2d3c4-b5a6-0987-6543-210fedcba987')
    micronutrient_levels = [
        MicronutrientLevel(
            micronutrient=MicronutrientName.ZINC,
            value=0.5,
            unit="ppm",
            source=MicronutrientSource.SOIL_TEST,
            optimal_min=1.0,
            optimal_max=5.0
        )
    ]
    assessment = await assessment_service.assess_deficiencies(
        farm_id=farm_id,
        field_id=field_id,
        crop_type="Corn",
        growth_stage="V6",
        soil_type="Loam",
        micronutrient_levels=micronutrient_levels
    )
    assert MicronutrientName.ZINC in assessment.identified_deficiencies
    assert assessment.overall_severity == DeficiencySeverity.MODERATE
    assert assessment.confidence_score == 0.8

@pytest.mark.asyncio
async def test_assess_deficiencies_with_visual_symptoms(assessment_service):
    farm_id = UUID('a1b2c3d4-e5f6-7890-1234-567890abcdef')
    field_id = UUID('f1e2d3c4-b5a6-0987-6543-210fedcba987')
    micronutrient_levels = [
        MicronutrientLevel(
            micronutrient=MicronutrientName.ZINC,
            value=2.0,
            unit="ppm",
            source=MicronutrientSource.SOIL_TEST,
            optimal_min=1.0,
            optimal_max=5.0
        )
    ]
    visual_symptoms = [
        DeficiencySymptom(
            micronutrient=MicronutrientName.ZINC,
            description="Stunted growth",
            severity=DeficiencySeverity.SEVERE,
            location_on_plant="whole plant"
        )
    ]
    assessment = await assessment_service.assess_deficiencies(
        farm_id=farm_id,
        field_id=field_id,
        crop_type="Corn",
        growth_stage="V6",
        soil_type="Loam",
        micronutrient_levels=micronutrient_levels,
        visual_symptoms=visual_symptoms
    )
    assert MicronutrientName.ZINC in assessment.identified_deficiencies
    assert assessment.overall_severity == DeficiencySeverity.SEVERE
    assert assessment.confidence_score == 0.8

# --- Test MicronutrientRecommendationService ---

@pytest.fixture
def recommendation_service():
    return MicronutrientRecommendationService()

@pytest.mark.asyncio
async def test_get_recommendations_for_zinc_deficiency(recommendation_service):
    assessment = MicronutrientDeficiencyAssessment(
        farm_id=UUID('a1b2c3d4-e5f6-7890-1234-567890abcdef'),
        field_id=UUID('f1e2d3c4-b5a6-0987-6543-210fedcba987'),
        crop_type="Corn",
        growth_stage="V6",
        soil_type="Loam",
        assessed_micronutrients=[],
        identified_deficiencies=[MicronutrientName.ZINC],
        overall_severity=DeficiencySeverity.MODERATE,
        confidence_score=0.8,
        assessment_date=datetime.now().isoformat().split("T")[0]
    )
    recommendations = await recommendation_service.get_recommendations(assessment)
    assert len(recommendations) == 1
    assert recommendations[0].micronutrient == MicronutrientName.ZINC
    assert "Zinc Sulfate" in recommendations[0].product

@pytest.mark.asyncio
async def test_get_recommendations_no_deficiency(recommendation_service):
    assessment = MicronutrientDeficiencyAssessment(
        farm_id=UUID('a1b2c3d4-e5f6-7890-1234-567890abcdef'),
        field_id=UUID('f1e2d3c4-b5a6-0987-6543-210fedcba987'),
        crop_type="Corn",
        growth_stage="V6",
        soil_type="Loam",
        assessed_micronutrients=[],
        identified_deficiencies=[],
        overall_severity=DeficiencySeverity.NONE,
        confidence_score=0.6,
        assessment_date=datetime.now().isoformat().split("T")[0]
    )
    recommendations = await recommendation_service.get_recommendations(assessment)
    assert not recommendations

@pytest.mark.asyncio
async def test_get_recommendations_multiple_deficiencies(recommendation_service):
    assessment = MicronutrientDeficiencyAssessment(
        farm_id=UUID('a1b2c3d4-e5f6-7890-1234-567890abcdef'),
        field_id=UUID('f1e2d3c4-b5a6-0987-6543-210fedcba987'),
        crop_type="Soybean",
        growth_stage="V3",
        soil_type="Clay",
        assessed_micronutrients=[],
        identified_deficiencies=[MicronutrientName.IRON, MicronutrientName.MANGANESE],
        overall_severity=DeficiencySeverity.SEVERE,
        confidence_score=0.9,
        assessment_date=datetime.now().isoformat().split("T")[0]
    )
    recommendations = await recommendation_service.get_recommendations(assessment)
    assert len(recommendations) == 2
    micronutrients_in_recs = {rec.micronutrient for rec in recommendations}
    assert MicronutrientName.IRON in micronutrients_in_recs
    assert MicronutrientName.MANGANESE in micronutrients_in_recs

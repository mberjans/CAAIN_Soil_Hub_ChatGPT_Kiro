import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.micronutrient_schemas import (
    MicronutrientRecommendationRequest,
    MicronutrientLevel,
    MicronutrientType,
    RecommendationPriority,
)
from src.services.micronutrient_recommendation_service import MicronutrientRecommendationService
from src.models.micronutrient_models import MicronutrientCropThresholdsModel

@pytest.fixture
def mock_db_session():
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def sample_request():
    return MicronutrientRecommendationRequest(
        farm_location_id="test-farm-123",
        crop_type="Corn",
        soil_type="Loam",
        soil_ph=6.5,
        organic_matter_percent=3.0,
        current_micronutrient_levels=[
            MicronutrientLevel(nutrient_type=MicronutrientType.ZINC, level_ppm=0.5),
            MicronutrientLevel(nutrient_type=MicronutrientType.BORON, level_ppm=0.2),
            MicronutrientLevel(nutrient_type=MicronutrientType.IRON, level_ppm=15.0),
        ],
        yield_goal_bushels_per_acre=200.0,
    )

@pytest.fixture
def mock_thresholds():
    # Mock thresholds for Corn
    zinc_threshold = MicronutrientCropThresholdsModel(
        crop_type="Corn",
        nutrient_type=MicronutrientType.ZINC,
        min_optimal_ppm=1.0,
        max_optimal_ppm=3.0,
        deficiency_threshold_ppm=0.7,
        toxicity_threshold_ppm=5.0,
        soil_ph_min=6.0,
        soil_ph_max=7.5,
    )
    boron_threshold = MicronutrientCropThresholdsModel(
        crop_type="Corn",
        nutrient_type=MicronutrientType.BORON,
        min_optimal_ppm=0.5,
        max_optimal_ppm=1.5,
        deficiency_threshold_ppm=0.3,
        toxicity_threshold_ppm=2.0,
        soil_ph_min=5.5,
        soil_ph_max=7.0,
    )
    iron_threshold = MicronutrientCropThresholdsModel(
        crop_type="Corn",
        nutrient_type=MicronutrientType.IRON,
        min_optimal_ppm=10.0,
        max_optimal_ppm=25.0,
        deficiency_threshold_ppm=8.0,
        toxicity_threshold_ppm=50.0,
        soil_ph_min=6.0,
        soil_ph_max=7.5,
    )
    return {
        MicronutrientType.ZINC: zinc_threshold,
        MicronutrientType.BORON: boron_threshold,
        MicronutrientType.IRON: iron_threshold,
    }

@pytest.mark.asyncio
async def test_generate_recommendations_deficiency(mock_db_session, sample_request, mock_thresholds):
    # Mock the get_crop_thresholds method to return predefined thresholds
    async def mock_get_crop_thresholds(crop_type, nutrient_type):
        return mock_thresholds.get(nutrient_type)

    service = MicronutrientRecommendationService(mock_db_session)
    service.get_crop_thresholds = AsyncMock(side_effect=mock_get_crop_thresholds)

    response = await service.generate_recommendations(sample_request)

    assert response.overall_status == "Critical Deficiencies/Excesses Detected"
    assert len(response.recommendations) == 3

    zinc_rec = next(r for r in response.recommendations if r.nutrient_type == MicronutrientType.ZINC)
    assert zinc_rec.priority == RecommendationPriority.CRITICAL
    assert "critically deficient" in zinc_rec.justification
    assert zinc_rec.recommended_amount is not None

    boron_rec = next(r for r in response.recommendations if r.nutrient_type == MicronutrientType.BORON)
    assert boron_rec.priority == RecommendationPriority.CRITICAL
    assert "critically deficient" in boron_rec.justification
    assert boron_rec.recommended_amount is not None

    iron_rec = next(r for r in response.recommendations if r.nutrient_type == MicronutrientType.IRON)
    assert iron_rec.priority == RecommendationPriority.OPTIMAL
    assert "optimal" in iron_rec.justification
    assert iron_rec.recommended_amount is None

@pytest.mark.asyncio
async def test_generate_recommendations_optimal(mock_db_session, mock_thresholds):
    optimal_request = MicronutrientRecommendationRequest(
        farm_location_id="test-farm-456",
        crop_type="Corn",
        soil_type="Loam",
        soil_ph=6.5,
        organic_matter_percent=3.0,
        current_micronutrient_levels=[
            MicronutrientLevel(nutrient_type=MicronutrientType.ZINC, level_ppm=1.5),
            MicronutrientLevel(nutrient_type=MicronutrientType.BORON, level_ppm=0.8),
            MicronutrientLevel(nutrient_type=MicronutrientType.IRON, level_ppm=18.0),
        ],
    )

    async def mock_get_crop_thresholds(crop_type, nutrient_type):
        return mock_thresholds.get(nutrient_type)

    service = MicronutrientRecommendationService(mock_db_session)
    service.get_crop_thresholds = AsyncMock(side_effect=mock_get_crop_thresholds)

    response = await service.generate_recommendations(optimal_request)

    assert response.overall_status == "Optimal"
    for rec in response.recommendations:
        assert rec.priority == RecommendationPriority.OPTIMAL
        assert "optimal" in rec.justification
        assert rec.recommended_amount is None

@pytest.mark.asyncio
async def test_generate_recommendations_no_thresholds(mock_db_session, sample_request):
    service = MicronutrientRecommendationService(mock_db_session)
    service.get_crop_thresholds = AsyncMock(return_value=None) # No thresholds found

    response = await service.generate_recommendations(sample_request)

    assert response.overall_status == "Optimal" # No recommendations means optimal by default
    assert len(response.recommendations) == 0 # No recommendations generated
    assert len(response.warnings) == len(sample_request.current_micronutrient_levels)

@pytest.fixture
def mock_thresholds_with_growth_stage():
    # Mock thresholds for Corn with growth stage impact
    zinc_threshold = MicronutrientCropThresholdsModel(
        crop_type="Corn",
        nutrient_type=MicronutrientType.ZINC,
        min_optimal_ppm=1.0,
        max_optimal_ppm=3.0,
        deficiency_threshold_ppm=0.7,
        toxicity_threshold_ppm=5.0,
        soil_ph_min=6.0,
        soil_ph_max=7.5,
        growth_stage_impact={"V6": "high_demand", "R1": "critical_uptake"}
    )
    boron_threshold = MicronutrientCropThresholdsModel(
        crop_type="Corn",
        nutrient_type=MicronutrientType.BORON,
        min_optimal_ppm=0.5,
        max_optimal_ppm=1.5,
        deficiency_threshold_ppm=0.3,
        toxicity_threshold_ppm=2.0,
        soil_ph_min=5.5,
        soil_ph_max=7.0,
        growth_stage_impact={"V6": "normal", "R1": "high_demand"}
    )
    iron_threshold = MicronutrientCropThresholdsModel(
        crop_type="Corn",
        nutrient_type=MicronutrientType.IRON,
        min_optimal_ppm=10.0,
        max_optimal_ppm=25.0,
        deficiency_threshold_ppm=8.0,
        toxicity_threshold_ppm=50.0,
        soil_ph_min=6.0,
        soil_ph_max=7.5,
        growth_stage_impact={"V6": "normal", "R1": "normal"}
    )
    molybdenum_threshold = MicronutrientCropThresholdsModel(
        crop_type="Corn",
        nutrient_type=MicronutrientType.MOLYBDENUM,
        min_optimal_ppm=0.1,
        max_optimal_ppm=0.5,
        deficiency_threshold_ppm=0.05,
        toxicity_threshold_ppm=1.0,
        soil_ph_min=6.5, # Molybdenum availability increases with pH
        soil_ph_max=8.0,
        growth_stage_impact={"V6": "normal", "R1": "normal"}
    )
    return {
        MicronutrientType.ZINC: zinc_threshold,
        MicronutrientType.BORON: boron_threshold,
        MicronutrientType.IRON: iron_threshold,
        MicronutrientType.MOLYBDENUM: molybdenum_threshold,
    }

@pytest.mark.asyncio
async def test_generate_recommendations_high_ph_iron_deficiency(mock_db_session, mock_thresholds_with_growth_stage):
    request = MicronutrientRecommendationRequest(
        farm_location_id="test-farm-789",
        crop_type="Corn",
        soil_type="Clay Loam",
        soil_ph=7.8, # High pH
        organic_matter_percent=3.5,
        current_micronutrient_levels=[
            MicronutrientLevel(nutrient_type=MicronutrientType.IRON, level_ppm=9.0), # Borderline deficient
        ],
        yield_goal_bushels_per_acre=220.0,
        growth_stage="V6"
    )

    async def mock_get_crop_thresholds(crop_type, nutrient_type):
        return mock_thresholds_with_growth_stage.get(nutrient_type)

    service = MicronutrientRecommendationService(mock_db_session)
    service.get_crop_thresholds = AsyncMock(side_effect=mock_get_crop_thresholds)

    response = await service.generate_recommendations(request)

    assert response.overall_status == "Critical Deficiencies/Excesses Detected"
    iron_rec = next(r for r in response.recommendations if r.nutrient_type == MicronutrientType.IRON)
    assert iron_rec.priority == RecommendationPriority.CRITICAL # Should be critical due to high pH adjustment
    assert "High soil pH (7.8) may reduce Iron availability." in iron_rec.justification
    assert "critically deficient" in iron_rec.justification
    assert iron_rec.recommended_amount is not None
    assert iron_rec.application_method == "Foliar spray for rapid correction, followed by soil application if needed."


@pytest.mark.asyncio
async def test_generate_recommendations_low_ph_molybdenum_deficiency(mock_db_session, mock_thresholds_with_growth_stage):
    request = MicronutrientRecommendationRequest(
        farm_location_id="test-farm-101",
        crop_type="Corn",
        soil_type="Sandy Loam",
        soil_ph=5.5, # Low pH
        organic_matter_percent=2.0,
        current_micronutrient_levels=[
            MicronutrientLevel(nutrient_type=MicronutrientType.MOLYBDENUM, level_ppm=0.06), # Borderline deficient
        ],
        yield_goal_bushels_per_acre=180.0,
        growth_stage="V6"
    )

    async def mock_get_crop_thresholds(crop_type, nutrient_type):
        return mock_thresholds_with_growth_stage.get(nutrient_type)

    service = MicronutrientRecommendationService(mock_db_session)
    service.get_crop_thresholds = AsyncMock(side_effect=mock_get_crop_thresholds)

    response = await service.generate_recommendations(request)

    assert response.overall_status == "Critical Deficiencies/Excesses Detected"
    molybdenum_rec = next(r for r in response.recommendations if r.nutrient_type == MicronutrientType.MOLYBDENUM)
    assert molybdenum_rec.priority == RecommendationPriority.CRITICAL # Should be critical due to low pH adjustment
    assert "Low soil pH (5.5) may reduce Molybdenum availability." in molybdenum_rec.justification
    assert "critically deficient" in molybdenum_rec.justification
    assert molybdenum_rec.recommended_amount is not None
    assert molybdenum_rec.application_method == "Foliar spray for rapid correction, followed by soil application if needed."


@pytest.mark.asyncio
async def test_generate_recommendations_critical_growth_stage_deficiency(mock_db_session, mock_thresholds_with_growth_stage):
    request = MicronutrientRecommendationRequest(
        farm_location_id="test-farm-202",
        crop_type="Corn",
        soil_type="Loam",
        soil_ph=6.8,
        organic_matter_percent=3.0,
        current_micronutrient_levels=[
            MicronutrientLevel(nutrient_type=MicronutrientType.ZINC, level_ppm=0.8), # Low, but not critical initially
        ],
        yield_goal_bushels_per_acre=210.0,
        growth_stage="R1" # Critical uptake stage for Zinc
    )

    async def mock_get_crop_thresholds(crop_type, nutrient_type):
        return mock_thresholds_with_growth_stage.get(nutrient_type)

    service = MicronutrientRecommendationService(mock_db_session)
    service.get_crop_thresholds = AsyncMock(side_effect=mock_get_crop_thresholds)

    response = await service.generate_recommendations(request)

    assert response.overall_status == "Critical Deficiencies/Excesses Detected"
    zinc_rec = next(r for r in response.recommendations if r.nutrient_type == MicronutrientType.ZINC)
    assert zinc_rec.priority == RecommendationPriority.CRITICAL # Should be elevated to critical
    assert "Current growth stage (R1) is critical for Zinc uptake." in zinc_rec.justification
    assert zinc_rec.application_method == "Foliar spray for rapid uptake"


@pytest.mark.asyncio
async def test_generate_recommendations_toxic_level(mock_db_session, mock_thresholds_with_growth_stage):
    request = MicronutrientRecommendationRequest(
        farm_location_id="test-farm-303",
        crop_type="Corn",
        soil_type="Loam",
        soil_ph=6.5,
        organic_matter_percent=3.0,
        current_micronutrient_levels=[
            MicronutrientLevel(nutrient_type=MicronutrientType.ZINC, level_ppm=6.0), # Above toxicity threshold
        ],
        yield_goal_bushels_per_acre=200.0,
        growth_stage="V6"
    )

    async def mock_get_crop_thresholds(crop_type, nutrient_type):
        return mock_thresholds_with_growth_stage.get(nutrient_type)

    service = MicronutrientRecommendationService(mock_db_session)
    service.get_crop_thresholds = AsyncMock(side_effect=mock_get_crop_thresholds)

    response = await service.generate_recommendations(request)

    assert response.overall_status == "Critical Deficiencies/Excesses Detected"
    zinc_rec = next(r for r in response.recommendations if r.nutrient_type == MicronutrientType.ZINC)
    assert zinc_rec.priority == RecommendationPriority.CRITICAL
    assert "toxic levels" in zinc_rec.justification
    assert zinc_rec.recommended_amount == 0.0
    assert "High Zinc levels detected. Investigate source of excess and consider remediation strategies." in response.warnings
    assert zinc_rec.application_method == "No application. Focus on remediation (e.g., flushing, pH adjustment, organic matter addition)."


@pytest.mark.asyncio
async def test_generate_recommendations_above_optimal_level(mock_db_session, mock_thresholds_with_growth_stage):
    request = MicronutrientRecommendationRequest(
        farm_location_id="test-farm-404",
        crop_type="Corn",
        soil_type="Loam",
        soil_ph=6.5,
        organic_matter_percent=3.0,
        current_micronutrient_levels=[
            MicronutrientLevel(nutrient_type=MicronutrientType.BORON, level_ppm=1.8), # Above max optimal, but below toxicity
        ],
        yield_goal_bushels_per_acre=200.0,
        growth_stage="V6"
    )

    async def mock_get_crop_thresholds(crop_type, nutrient_type):
        return mock_thresholds_with_growth_stage.get(nutrient_type)

    service = MicronutrientRecommendationService(mock_db_session)
    service.get_crop_thresholds = AsyncMock(side_effect=mock_get_crop_thresholds)

    response = await service.generate_recommendations(request)

    assert response.overall_status == "Action Required"
    boron_rec = next(r for r in response.recommendations if r.nutrient_type == MicronutrientType.BORON)
    assert boron_rec.priority == RecommendationPriority.MEDIUM
    assert "above optimal, approaching excess" in boron_rec.justification
    assert boron_rec.recommended_amount is None
    assert boron_rec.application_method == "Monitor levels; no application recommended at this time."


@pytest.mark.asyncio
async def test_calculate_recommended_amount_logic(mock_db_session, mock_thresholds_with_growth_stage):
    # Test with a specific scenario to check the calculation logic
    request = MicronutrientRecommendationRequest(
        farm_location_id="test-farm-505",
        crop_type="Corn",
        soil_type="Sandy", # Should increase recommended amount
        soil_ph=6.5,
        organic_matter_percent=0.5, # Should increase recommended amount
        current_micronutrient_levels=[
            MicronutrientLevel(nutrient_type=MicronutrientType.ZINC, level_ppm=0.5), # Critically deficient
        ],
        yield_goal_bushels_per_acre=200.0,
        growth_stage="V6"
    )

    async def mock_get_crop_thresholds(crop_type, nutrient_type):
        return mock_thresholds_with_growth_stage.get(nutrient_type)

    service = MicronutrientRecommendationService(mock_db_session)
    service.get_crop_thresholds = AsyncMock(side_effect=mock_get_crop_thresholds)

    response = await service.generate_recommendations(request)
    zinc_rec = next(r for r in response.recommendations if r.nutrient_type == MicronutrientType.ZINC)

    # Expected target for Zinc is (1.0 + 3.0) / 2 = 2.0 ppm
    # Difference = 2.0 - 0.5 = 1.5 ppm
    # Base rate per ppm = 0.5 kg/ha
    # Soil factor for Sandy = 1.2
    # OM factor for 0.5% = 1.1
    # Expected recommended_amount = 1.5 * 0.5 * 1.2 * 1.1 = 0.99 kg/ha
    assert zinc_rec.recommended_amount == pytest.approx(0.99, abs=0.01)
    assert zinc_rec.unit == "kg/ha"

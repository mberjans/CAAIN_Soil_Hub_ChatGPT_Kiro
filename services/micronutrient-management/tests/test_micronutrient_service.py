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
    assert "No specific thresholds found" in response.warnings[0]

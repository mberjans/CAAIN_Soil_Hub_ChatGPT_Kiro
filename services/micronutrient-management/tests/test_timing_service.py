import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.micronutrient_schemas import (
    TimingRecommendationRequest,
    TimingRecommendationType,
    ApplicationMethod,
    WeatherCondition,
    FieldCondition,
    MicronutrientType
)
from src.services.timing_service import TimingService


@pytest.fixture
def mock_db_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def sample_field_conditions():
    return FieldCondition(
        moisture="adequate",
        temperature=70.0,
        weather_forecast=[],
        soil_compaction=False
    )


@pytest.fixture
def sample_timing_request(sample_field_conditions):
    return TimingRecommendationRequest(
        crop_type="Corn",
        growth_stage="Vegetative",
        nutrient_uptake_pattern="High demand during vegetative growth",
        weather_conditions=WeatherCondition.CLEAR,
        nutrient_type=MicronutrientType.ZINC,
        application_method=ApplicationMethod.FOLIAR_APPLICATION,
        field_conditions=sample_field_conditions
    )


@pytest.mark.asyncio
async def test_get_optimal_timing_short_term_during_critical_growth(
    mock_db_session, 
    sample_field_conditions
):
    request = TimingRecommendationRequest(
        crop_type="Corn",
        growth_stage="Flowering",  # Critical growth stage
        nutrient_uptake_pattern="Critical uptake during flowering",
        weather_conditions=WeatherCondition.CLEAR,
        nutrient_type=MicronutrientType.BORON,
        application_method=ApplicationMethod.FOLIAR_APPLICATION,
        field_conditions=sample_field_conditions
    )
    
    service = TimingService(mock_db_session)
    recommendation = await service.get_optimal_timing(request)
    
    assert recommendation.timing == TimingRecommendationType.SHORT_TERM
    assert "flowering" in recommendation.reason.lower()
    assert recommendation.expected_efficacy > 0.7


@pytest.mark.asyncio
async def test_get_optimal_timing_immediate_for_critical_deficiency(
    mock_db_session, 
    sample_field_conditions
):
    request = TimingRecommendationRequest(
        crop_type="Soybean",
        growth_stage="Vegetative",
        nutrient_uptake_pattern="Critical deficiency requiring immediate action",
        weather_conditions=WeatherCondition.CLEAR,
        nutrient_type=MicronutrientType.IRON,
        application_method=ApplicationMethod.FOLIAR_APPLICATION,
        field_conditions=sample_field_conditions
    )
    
    service = TimingService(mock_db_session)
    recommendation = await service.get_optimal_timing(request)
    
    assert recommendation.timing == TimingRecommendationType.IMMEDIATE
    assert "critical" in recommendation.reason.lower()


@pytest.mark.asyncio
async def test_get_optimal_timing_weather_considerations_foliar(
    mock_db_session, 
    sample_field_conditions
):
    request = TimingRecommendationRequest(
        crop_type="Corn",
        growth_stage="Vegetative",
        nutrient_uptake_pattern="High demand during vegetative growth",
        weather_conditions=WeatherCondition.RAIN,
        nutrient_type=MicronutrientType.ZINC,
        application_method=ApplicationMethod.FOLIAR_APPLICATION,
        field_conditions=sample_field_conditions
    )
    
    service = TimingService(mock_db_session)
    recommendation = await service.get_optimal_timing(request)
    
    assert "foliar spray will be washed off" in " ".join(recommendation.weather_considerations).lower()


@pytest.mark.asyncio
async def test_get_optimal_timing_weather_considerations_fertigation(
    mock_db_session, 
    sample_field_conditions
):
    request = TimingRecommendationRequest(
        crop_type="Corn",
        growth_stage="Vegetative",
        nutrient_uptake_pattern="High demand during vegetative growth",
        weather_conditions=WeatherCondition.CLEAR,
        nutrient_type=MicronutrientType.ZINC,
        application_method=ApplicationMethod.FERTIGATION,
        field_conditions=sample_field_conditions
    )
    
    service = TimingService(mock_db_session)
    recommendation = await service.get_optimal_timing(request)
    
    # Should have positive weather consideration for fertigation in clear conditions
    assert len(recommendation.weather_considerations) > 0


@pytest.mark.asyncio
async def test_get_optimal_timing_compatibility_notes(
    mock_db_session, 
    sample_field_conditions
):
    request = TimingRecommendationRequest(
        crop_type="Corn",
        growth_stage="Flowering",
        nutrient_uptake_pattern="Critical uptake during flowering",
        weather_conditions=WeatherCondition.CLEAR,
        nutrient_type=MicronutrientType.ZINC,
        application_method=ApplicationMethod.FOLIAR_APPLICATION,
        field_conditions=sample_field_conditions
    )
    
    service = TimingService(mock_db_session)
    recommendation = await service.get_optimal_timing(request)
    
    # Should have compatibility notes about flowering
    has_pollinator_note = any("pollinators" in note.lower() for note in recommendation.compatibility_notes)
    assert has_pollinator_note


@pytest.mark.asyncio
async def test_get_optimal_timing_compatibility_notes_nutrient_interactions(
    mock_db_session, 
    sample_field_conditions
):
    request = TimingRecommendationRequest(
        crop_type="Soybean",
        growth_stage="Vegetative",
        nutrient_uptake_pattern="High demand during vegetative growth",
        weather_conditions=WeatherCondition.CLEAR,
        nutrient_type=MicronutrientType.IRON,
        application_method=ApplicationMethod.SOIL_APPLICATION,
        field_conditions=sample_field_conditions
    )
    
    service = TimingService(mock_db_session)
    recommendation = await service.get_optimal_timing(request)
    
    # Should have compatibility notes about phosphorus interaction
    has_phosphorus_note = any("phosphorus" in note.lower() for note in recommendation.compatibility_notes)
    assert has_phosphorus_note


@pytest.mark.asyncio
async def test_get_optimal_timing_early_season_longer_term(
    mock_db_session, 
    sample_field_conditions
):
    request = TimingRecommendationRequest(
        crop_type="Corn",
        growth_stage="Seedling",
        nutrient_uptake_pattern="Establishment phase",
        weather_conditions=WeatherCondition.CLEAR,
        nutrient_type=MicronutrientType.ZINC,
        application_method=ApplicationMethod.SOIL_APPLICATION,
        field_conditions=sample_field_conditions
    )
    
    service = TimingService(mock_db_session)
    recommendation = await service.get_optimal_timing(request)
    
    # Early season should have medium-term timing
    assert recommendation.timing in [TimingRecommendationType.MEDIUM_TERM, TimingRecommendationType.LONG_TERM]


@pytest.mark.asyncio
async def test_get_optimal_timing_calculate_expected_efficacy_weather_impact(
    mock_db_session, 
    sample_field_conditions
):
    # Test with poor weather conditions
    request_poor = TimingRecommendationRequest(
        crop_type="Corn",
        growth_stage="Vegetative",
        nutrient_uptake_pattern="High demand during vegetative growth",
        weather_conditions=WeatherCondition.RAIN,  # Poor weather for application
        nutrient_type=MicronutrientType.ZINC,
        application_method=ApplicationMethod.FOLIAR_APPLICATION,
        field_conditions=sample_field_conditions
    )
    
    request_good = TimingRecommendationRequest(
        crop_type="Corn",
        growth_stage="Vegetative",
        nutrient_uptake_pattern="High demand during vegetative growth",
        weather_conditions=WeatherCondition.CLEAR,  # Good weather
        nutrient_type=MicronutrientType.ZINC,
        application_method=ApplicationMethod.FOLIAR_APPLICATION,
        field_conditions=sample_field_conditions
    )
    
    service = TimingService(mock_db_session)
    recommendation_poor = await service.get_optimal_timing(request_poor)
    recommendation_good = await service.get_optimal_timing(request_good)
    
    # Good weather should have higher efficacy than poor weather
    assert recommendation_good.expected_efficacy >= recommendation_poor.expected_efficacy


@pytest.mark.asyncio
async def test_get_optimal_timing_field_conditions_impact(
    mock_db_session, 
    sample_field_conditions
):
    # Test with dry field conditions
    dry_conditions = FieldCondition(
        moisture="dry",
        temperature=70.0,
        weather_forecast=[],
        soil_compaction=False
    )
    
    request = TimingRecommendationRequest(
        crop_type="Corn",
        growth_stage="Vegetative",
        nutrient_uptake_pattern="High demand during vegetative growth",
        weather_conditions=WeatherCondition.CLEAR,
        nutrient_type=MicronutrientType.ZINC,
        application_method=ApplicationMethod.SOIL_APPLICATION,
        field_conditions=dry_conditions
    )
    
    service = TimingService(mock_db_session)
    recommendation = await service.get_optimal_timing(request)
    
    # Should have weather considerations about dry conditions
    has_dry_note = any("dry" in note.lower() for note in recommendation.weather_considerations)
    assert has_dry_note


@pytest.mark.asyncio
async def test_get_seasonal_timing_recommendations(
    mock_db_session
):
    service = TimingService(mock_db_session)
    
    # Test corn and zinc combination
    seasonal_recs = await service.get_seasonal_timing_recommendations("Corn", MicronutrientType.ZINC)
    
    # Should have multiple recommendations
    assert len(seasonal_recs) > 0
    
    # Check that recommendations have expected structure
    for rec in seasonal_recs:
        assert "timing" in rec
        assert "application_method" in rec
        assert "growth_stage" in rec
        assert "reason" in rec


@pytest.mark.asyncio
async def test_get_optimal_timing_window_calculation(
    mock_db_session, 
    sample_field_conditions
):
    request = TimingRecommendationRequest(
        crop_type="Corn",
        growth_stage="Flowering",  # Should trigger short-term timing
        nutrient_uptake_pattern="Critical uptake during flowering",
        weather_conditions=WeatherCondition.CLEAR,
        nutrient_type=MicronutrientType.BORON,
        application_method=ApplicationMethod.FOLIAR_APPLICATION,
        field_conditions=sample_field_conditions
    )
    
    service = TimingService(mock_db_session)
    recommendation = await service.get_optimal_timing(request)
    
    # Verify that timing windows are properly calculated
    assert recommendation.optimal_window_start is not None
    assert recommendation.optimal_window_end is not None
    assert recommendation.optimal_window_end > recommendation.optimal_window_start
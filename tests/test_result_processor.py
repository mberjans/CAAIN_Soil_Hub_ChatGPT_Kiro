import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from uuid import UUID

from services.crop_taxonomy.src.services.result_processor import FilterResultProcessor
from services.crop_taxonomy.src.models.crop_taxonomy_models import CropCategory, LifeCycle
from services.crop_taxonomy.src.models.crop_variety_models import (
    EnhancedCropVariety, YieldPotential, DiseaseResistanceProfile, AbioticStressTolerances,
    MarketAttributes, QualityAttributes, PestResistanceProfile, VarietyCharacteristics
)

@pytest.fixture
def mock_variety_recommendation_service():
    """Fixture for a mocked VarietyRecommendationService."""
    mock_service = AsyncMock()
    mock_service._score_variety_for_context.return_value = {"overall_score": 0.85}
    return mock_service

@pytest.fixture
def mock_crop_search_service():
    """Fixture for a mocked CropSearchService."""
    mock_service = AsyncMock()
    mock_service.search_crops.return_value = [
        {"id": str(UUID('a0000000-0000-0000-0000-000000000001')), "name": "Alternative Corn", "agricultural_classification": {"primary_category": CropCategory.GRAIN.value}},
        {"id": str(UUID('a0000000-0000-0000-0000-000000000002')), "name": "Alternative Soybean", "agricultural_classification": {"primary_category": CropCategory.LEGUME.value}}
    ]
    return mock_service

@pytest.fixture
def filter_result_processor(mock_variety_recommendation_service, mock_crop_search_service):
    """Fixture for FilterResultProcessor with mocked dependencies."""
    processor = FilterResultProcessor()
    processor.variety_recommendation_service = mock_variety_recommendation_service
    processor.crop_search_service = mock_crop_search_service
    return processor

@pytest.fixture
def sample_crops():
    """Sample crop data for testing."""
    return [
        {
            "id": str(UUID('12345678-1234-5678-9abc-000000000001')),
            "variety_name": "Corn Hybrid A",
            "name": "Corn Hybrid A",
            "parent_crop_id": str(UUID('12345678-1234-5678-9abc-00000000000a')),
            "agricultural_classification": {"primary_category": CropCategory.GRAIN.value},
            "life_cycle": LifeCycle.ANNUAL.value,
            "primary_use": "feed",
            "climate_zones": ["5a", "5b"],
            "soil_ph_min": 6.0,
            "soil_ph_max": 7.0,
            "yield_potential": {"average_yield_range": [150, 200], "yield_stability_rating": 4.0},
            "disease_resistance": {"rust_resistance": {"common_rust": 4}},
            "abiotic_stress_tolerances": {"drought_tolerance": 3},
            "market_attributes": {"premium_potential": 3.0}
        },
        {
            "id": str(UUID('12345678-1234-5678-9abc-000000000002')),
            "variety_name": "Soybean Variety B",
            "name": "Soybean Variety B",
            "parent_crop_id": str(UUID('12345678-1234-5678-9abc-00000000000b')),
            "agricultural_classification": {"primary_category": CropCategory.LEGUME.value},
            "life_cycle": LifeCycle.ANNUAL.value,
            "primary_use": "oil",
            "climate_zones": ["6a", "6b"],
            "soil_ph_min": 6.5,
            "soil_ph_max": 7.5,
            "yield_potential": {"average_yield_range": [50, 70], "yield_stability_rating": 5.0},
            "disease_resistance": {"rust_resistance": {"soybean_rust": 5}},
            "abiotic_stress_tolerances": {"drought_tolerance": 4},
            "market_attributes": {"premium_potential": 4.0}
        },
        {
            "id": str(UUID('12345678-1234-5678-9abc-000000000003')),
            "variety_name": "Wheat Winter C",
            "name": "Wheat Winter C",
            "parent_crop_id": str(UUID('12345678-1234-5678-9abc-00000000000c')),
            "agricultural_classification": {"primary_category": CropCategory.GRAIN.value},
            "life_cycle": LifeCycle.ANNUAL.value,
            "primary_use": "food",
            "climate_zones": ["4a", "5a"],
            "soil_ph_min": 5.5,
            "soil_ph_max": 6.5,
            "yield_potential": {"average_yield_range": [70, 90], "yield_stability_rating": 3.0},
            "disease_resistance": {"rust_resistance": {"stripe_rust": 3}},
            "abiotic_stress_tolerances": {"drought_tolerance": 2},
            "market_attributes": {"premium_potential": 2.0}
        }
    ]

@pytest.fixture
def sample_filtering_criteria():
    """Sample filtering criteria for testing."""
    return {
        "filters": {
            "climate_zones": ["5a"],
            "soil_ph_range": {"min": 6.0, "max": 7.0}
        },
        "location": {"latitude": 40.0, "longitude": -95.0},
        "user_preferences": {"yield_priority": 0.8}
    }

@pytest.mark.asyncio
async def test_process_results_with_crops(filter_result_processor, sample_crops, sample_filtering_criteria):
    """Test processing results when crops are found."""
    result = await filter_result_processor.process_results(sample_crops, sample_filtering_criteria)

    assert "ranked_results" in result
    assert len(result["ranked_results"]) == len(sample_crops)
    assert result["ranked_results"][0]["relevance_score"] == 0.85 # Mocked score
    assert result["ranked_results"][0]["variety_name"] == "Soybean Variety B" # Assuming Soybean gets highest score

    assert "clustered_results" in result
    assert "Grain - ANNUAL - feed" in result["clustered_results"]
    assert "Legume - ANNUAL - oil" in result["clustered_results"]

    assert "visualization_data" in result
    assert "category_distribution" in result["visualization_data"]["chart_data"]
    assert result["visualization_data"]["chart_data"]["category_distribution"]["Grain"] == 2
    assert result["visualization_data"]["chart_data"]["category_distribution"]["Legume"] == 1

    assert "alternatives" in result
    assert len(result["alternatives"]) == 0 # No alternatives when crops are found
    assert "message" in result
    assert "crops found matching criteria" in result["message"]

@pytest.mark.asyncio
async def test_process_results_no_crops(filter_result_processor, sample_filtering_criteria):
    """Test processing results when no crops are found, expecting alternatives."""
    result = await filter_result_processor.process_results([], sample_filtering_criteria)

    assert "ranked_results" in result
    assert len(result["ranked_results"]) == 0

    assert "alternatives" in result
    assert len(result["alternatives"]) > 0
    assert result["alternatives"][0]["name"] == "Alternative Corn"
    assert "message" in result
    assert "No crops matched the criteria. Here are some alternatives." in result["message"]

@pytest.mark.asyncio
async def test_calculate_relevance_score(filter_result_processor, sample_crops, sample_filtering_criteria, mock_variety_recommendation_service):
    """Test relevance score calculation using the mocked service."""
    crop = sample_crops[0] # Corn Hybrid A
    score = await filter_result_processor._calculate_relevance_score(crop, sample_filtering_criteria)
    assert score == 0.85 # Expecting the mocked score
    mock_variety_recommendation_service._score_variety_for_context.assert_called_once()

@pytest.mark.asyncio
async def test_cluster_results(filter_result_processor, sample_crops):
    """Test clustering of results."""
    clustered = await filter_result_processor._cluster_results(sample_crops)

    assert "Grain - ANNUAL - feed" in clustered
    assert len(clustered["Grain - ANNUAL - feed"]) == 1 # Corn Hybrid A
    assert clustered["Grain - ANNUAL - feed"][0]["variety_name"] == "Corn Hybrid A"

    assert "Legume - ANNUAL - oil" in clustered
    assert len(clustered["Legume - ANNUAL - oil"]) == 1 # Soybean Variety B

    # Test for Wheat Winter C, which also falls under Grain - ANNUAL - food
    assert "Grain - ANNUAL - food" in clustered
    assert len(clustered["Grain - ANNUAL - food"]) == 1
    assert clustered["Grain - ANNUAL - food"][0]["variety_name"] == "Wheat Winter C"

@pytest.mark.asyncio
async def test_suggest_alternatives_relax_climate(filter_result_processor, mock_crop_search_service):
    """Test alternative suggestions by relaxing climate filter."""
    filtering_criteria = {
        "filters": {"climate_zones": ["1a"]},
        "location": {"latitude": 40.0, "longitude": -95.0}
    }
    alternatives = await filter_result_processor._suggest_alternatives(filtering_criteria)

    assert len(alternatives) > 0
    assert alternatives[0]["name"] == "Alternative Corn"
    assert alternatives[0]["reason"] == "Relaxed climate zone filter"
    mock_crop_search_service.search_crops.assert_called_once()

@pytest.mark.asyncio
async def test_prepare_visualization_data(filter_result_processor, sample_crops):
    """Test preparation of visualization data."""
    # Add relevance score to sample crops for visualization data
    for crop in sample_crops:
        crop["relevance_score"] = 0.85 # Assign a dummy score for testing visualization

    visualization_data = await filter_result_processor._prepare_visualization_data(sample_crops)

    assert "chart_data" in visualization_data
    assert "category_distribution" in visualization_data["chart_data"]
    assert visualization_data["chart_data"]["category_distribution"]["Grain"] == 2
    assert visualization_data["chart_data"]["category_distribution"]["Legume"] == 1

    assert "relevance_score_distribution" in visualization_data["chart_data"]
    assert "0.8-0.9" in visualization_data["chart_data"]["relevance_score_distribution"]
    assert visualization_data["chart_data"]["relevance_score_distribution"]["0.8-0.9"] == 3

    assert "comparison_table_data" in visualization_data
    assert len(visualization_data["comparison_table_data"]) == len(sample_crops)
    assert visualization_data["comparison_table_data"][0]["name"] == "Corn Hybrid A"
    assert visualization_data["comparison_table_data"][0]["relevance_score"] == 0.85

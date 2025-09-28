
import pytest
from typing import List, Dict, Any
from uuid import uuid4

from services.crop_taxonomy.src.services.result_processor import FilterResultProcessor
from services.crop_taxonomy.src.models.crop_taxonomy_models import ComprehensiveCropData, CropAgriculturalClassification, CropCategory, GrowthHabit, PlantType
from services.crop_taxonomy.src.models.crop_variety_models import EnhancedCropVariety


@pytest.fixture
def result_processor() -> FilterResultProcessor:
    """Returns a FilterResultProcessor instance for testing."""
    return FilterResultProcessor()


@pytest.fixture
def sample_crops() -> List[Dict[str, Any]]:
    """Returns a list of sample crops for testing."""
    return [
        {
            "id": uuid4(),
            "name": "Crop A",
            "agricultural_classification": {
                "primary_category": CropCategory.GRAIN,
                "growth_habit": GrowthHabit.ANNUAL,
                "plant_type": PlantType.GRASS,
            },
            "climate_adaptations": {
                "hardiness_zones": ["5a", "5b"]
            },
            "soil_requirements": {
                "optimal_ph_min": 6.0,
                "optimal_ph_max": 7.0
            }
        },
        {
            "id": uuid4(),
            "name": "Crop B",
            "agricultural_classification": {
                "primary_category": CropCategory.LEGUME,
                "growth_habit": GrowthHabit.ANNUAL,
                "plant_type": PlantType.FORB,
            },
            "climate_adaptations": {
                "hardiness_zones": ["6a", "6b"]
            },
            "soil_requirements": {
                "optimal_ph_min": 6.5,
                "optimal_ph_max": 7.5
            }
        },
    ]


@pytest.mark.asyncio
async def test_process_results_empty(result_processor: FilterResultProcessor):
    """Tests that process_results returns an empty result when no crops are provided."""
    result = await result_processor.process_results([], {})
    assert result["ranked_results"] == []
    assert result["clustered_results"] == {}
    assert result["visualization_data"] == {}
    assert result["alternatives"] != []


@pytest.mark.asyncio
async def test_apply_relevance_scoring(result_processor: FilterResultProcessor, sample_crops: List[Dict[str, Any]]):
    """Tests that apply_relevance_scoring returns a list of scored crops sorted by relevance score."""
    filtering_criteria = {
        "filters": {
            "climate_zones": ["5a"],
            "soil_ph_range": {"min": 6.0, "max": 6.5}
        }
    }
    scored_crops = await result_processor._apply_relevance_scoring(sample_crops, filtering_criteria)
    assert len(scored_crops) == 2
    assert "relevance_score" in scored_crops[0]
    assert scored_crops[0]["relevance_score"] >= scored_crops[1]["relevance_score"]


@pytest.mark.asyncio
async def test_cluster_results(result_processor: FilterResultProcessor, sample_crops: List[Dict[str, Any]]):
    """Tests that cluster_results returns a dictionary of clustered crops."""
    clustered_results = await result_processor._cluster_results(sample_crops)
    assert "GRAIN - ANNUAL - GRASS" in clustered_results
    assert "LEGUME - ANNUAL - FORB" in clustered_results


@pytest.mark.asyncio
async def test_prepare_visualization_data(result_processor: FilterResultProcessor, sample_crops: List[Dict[str, Any]]):
    """Tests that prepare_visualization_data returns a dictionary of visualization data."""
    visualization_data = await result_processor._prepare_visualization_data(sample_crops)
    assert "chart_data" in visualization_data
    assert "comparison_table_data" in visualization_data
    assert "category_distribution" in visualization_data["chart_data"]
    assert "growth_habit_distribution" in visualization_data["chart_data"]
    assert "plant_type_distribution" in visualization_data["chart_data"]
    assert len(visualization_data["comparison_table_data"]) == 2

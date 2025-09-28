import pytest
import sys
import os

# Add the src directory to the path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from services.result_processor import FilterResultProcessor
except ImportError:
    from src.services.result_processor import FilterResultProcessor


@pytest.fixture
def processor():
    """Returns a FilterResultProcessor instance."""
    return FilterResultProcessor()

@pytest.fixture
def mock_results():
    """Returns a list of mock crop results."""
    return [
        {
            "variety_name": "Variety A",
            "family": "Brassicaceae",
            "yield_potential": {"yield_stability_rating": 4.0},
            "disease_resistance": {"rust_resistance": {"stripe_rust": 4}},
            "abiotic_stress_tolerances": {"drought_tolerance": 4},
            "market_attributes": {"premium_potential": 4.0, "market_class": "organic"},
            "quality_attributes": {"protein_content_range": [12, 14]},
        },
        {
            "variety_name": "Variety B",
            "family": "Fabaceae",
            "yield_potential": {"yield_stability_rating": 3.0},
            "disease_resistance": {"rust_resistance": {"stripe_rust": 3}},
            "abiotic_stress_tolerances": {"drought_tolerance": 3},
            "market_attributes": {"premium_potential": 3.0, "market_class": "conventional"},
            "quality_attributes": {"protein_content_range": [10, 12]},
        },
        {
            "variety_name": "Variety C",
            "family": "Brassicaceae",
            "yield_potential": {"yield_stability_rating": 5.0},
            "disease_resistance": {"rust_resistance": {"stripe_rust": 5}},
            "abiotic_stress_tolerances": {"drought_tolerance": 5},
            "market_attributes": {"premium_potential": 5.0, "market_class": "organic"},
            "quality_attributes": {"protein_content_range": [14, 16]},
        },
    ]

def test_process_results_empty(processor):
    """Test processing of empty results."""
    results = processor.process_results([])
    assert results["ranked_results"] == []
    assert results["clustered_results"] == {}
    assert len(results["alternative_suggestions"]) > 0
    assert results["summary"] == "No results found. Consider broadening your filter criteria."

def test_rank_results(processor, mock_results):
    """Test the ranking of results."""
    ranked_results = processor.rank_results(mock_results, {})
    assert len(ranked_results) == 3
    assert ranked_results[0]["variety_name"] == "Variety C"
    assert ranked_results[1]["variety_name"] == "Variety A"
    assert ranked_results[2]["variety_name"] == "Variety B"

def test_cluster_results(processor, mock_results):
    """Test the clustering of results."""
    clustered_results = processor.cluster_results(mock_results)
    assert "Brassicaceae" in clustered_results
    assert "Fabaceae" in clustered_results
    assert len(clustered_results["Brassicaceae"]) == 2
    assert len(clustered_results["Fabaceae"]) == 1

def test_scoring_logic(processor):
    """Test the individual scoring methods."""
    # Test yield potential
    assert processor._score_yield_potential({"yield_potential": {"yield_stability_rating": 5.0}}, {}) > processor._score_yield_potential({"yield_potential": {"yield_stability_rating": 3.0}}, {})

    # Test disease resistance
    assert processor._score_disease_resistance({"disease_resistance": {"rust_resistance": {"stripe_rust": 5}}}, {}) > processor._score_disease_resistance({"disease_resistance": {"rust_resistance": {"stripe_rust": 2}}}, {})

    # Test climate adaptation
    assert processor._score_climate_adaptation({"abiotic_stress_tolerances": {"drought_tolerance": 5}}, {"climate_risks": {"drought_risk": 0.8}}) > processor._score_climate_adaptation({"abiotic_stress_tolerances": {"drought_tolerance": 2}}, {"climate_risks": {"drought_risk": 0.8}})

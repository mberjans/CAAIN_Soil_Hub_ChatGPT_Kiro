"""Unit tests for variety-aware crop recommendation enhancements."""

from datetime import date
import importlib.util
import os
import sys

import pytest


TEST_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(TEST_DIR, '..', '..', 'src'))


def _load_module(module_name: str, relative_path: str):
    """Load Python module directly from file path."""
    module_path = os.path.join(SRC_DIR, relative_path)
    if SRC_DIR not in sys.path:
        sys.path.insert(0, SRC_DIR)
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    if spec.loader is not None:
        spec.loader.exec_module(module)
    return module


crop_module = _load_module('crop_recommendation_service', 'services/crop_recommendation_service.py')
model_module = _load_module('agricultural_models', 'models/agricultural_models.py')

CropRecommendationService = crop_module.CropRecommendationService
RecommendationRequest = model_module.RecommendationRequest
LocationData = model_module.LocationData
SoilTestData = model_module.SoilTestData
FarmProfile = model_module.FarmProfile


def _build_sample_request() -> RecommendationRequest:
    """Create representative recommendation request for testing."""
    location = LocationData(
        latitude=41.8781,
        longitude=-93.0977,
        state="Iowa",
        county="Story",
        climate_zone="5a",
        climate_zone_name="Northern Iowa",
        climate_zone_description="Upper Midwest",
        temperature_range_f={"min": -15.0, "max": 90.0}
    )

    soil_sample = SoilTestData(
        ph=6.4,
        organic_matter_percent=4.2,
        phosphorus_ppm=28.0,
        potassium_ppm=190.0,
        nitrogen_ppm=18.0,
        cec_meq_per_100g=18.0,
        soil_texture="silt loam",
        drainage_class="well_drained",
        test_date=date.today()
    )

    farm_profile = FarmProfile(
        farm_id="TEST-FARM-001",
        farm_size_acres=480.0,
        primary_crops=["corn", "soybean"],
        equipment_available=["planter", "combine"],
        irrigation_available=False,
        organic_certified=False
    )

    request = RecommendationRequest(
        request_id="VARIETY-REQ-001",
        question_type="crop_selection",
        location=location,
        soil_data=soil_sample,
        farm_profile=farm_profile
    )

    return request


@pytest.mark.asyncio
async def test_variety_aware_recommendations_structure():
    """Variety-aware recommendations should include enriched analytics."""
    service = CropRecommendationService()
    service.market_price_service = None

    request = _build_sample_request()

    result = await service.get_variety_aware_recommendations(request)

    assert 'variety_recommendations' in result
    assert result['variety_recommendations']

    for crop_entry in result['variety_recommendations']:
        assert 'variety_candidates' in crop_entry
        candidates = crop_entry['variety_candidates']
        assert candidates

        for candidate in candidates:
            assert 'roi' in candidate
            assert 'risk' in candidate
            roi_info = candidate['roi']
            assert 'roi_percent' in roi_info
            risk_info = candidate['risk']
            assert 'risk_level' in risk_info


@pytest.mark.asyncio
async def test_variety_summary_steps_added():
    """Implementation steps should highlight primary variety guidance."""
    service = CropRecommendationService()
    service.market_price_service = None

    request = _build_sample_request()

    result = await service.get_variety_aware_recommendations(request)

    summary_found = False
    for recommendation in result['crop_recommendations']:
        for step in recommendation.implementation_steps:
            if isinstance(step, str) and step.startswith("Variety focus:"):
                summary_found = True
                break
        if summary_found:
            break

    assert summary_found, "Expected a variety focus step in implementation guidance"

    risk_note_found = False
    for recommendation in result['crop_recommendations']:
        for outcome in recommendation.expected_outcomes:
            if isinstance(outcome, str) and outcome.startswith("Primary variety risk profile"):
                risk_note_found = True
                break
        if risk_note_found:
            break

    assert risk_note_found, "Expected risk profile note in expected outcomes"

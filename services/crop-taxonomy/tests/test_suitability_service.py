"""Tests for CropSuitabilityMatrixService."""

import os
import sys

import pytest

_TEST_DIR = os.path.dirname(__file__)
_SRC_PARENT = os.path.abspath(os.path.join(_TEST_DIR, '..'))
_SRC_DIR = os.path.join(_SRC_PARENT, 'src')

if _SRC_PARENT not in sys.path:
    sys.path.insert(0, _SRC_PARENT)
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from src.services.suitability_service import CropSuitabilityMatrixService  # type: ignore
from models.suitability_models import SuitabilityMatrixRequest  # type: ignore


@pytest.fixture(scope="module")
def suitability_service():
    return CropSuitabilityMatrixService()


@pytest.mark.asyncio
async def test_generate_matrix_for_corn_ideal_conditions(suitability_service):
    request = SuitabilityMatrixRequest(
        crop_name="Corn",
        climate_zone="5",
        soil_conditions={
            'ph': 6.4,
            'texture': 'loam',
            'drainage_class': 'well_drained',
            'fertility': 'high'
        },
        weather_patterns={
            'average_temp_f': 72.0,
            'annual_precip_inches': 34.0,
            'average_humidity_percent': 65.0,
            'wind_risk': 'moderate'
        },
        pest_pressure={'pest': 'low', 'disease': 'moderate', 'weed': 'moderate'},
        management_capabilities={
            'irrigation': 'available',
            'fertility_program': 'advanced',
            'equipment': 'modern',
            'labor': 'abundant',
            'market_access': 'national'
        },
        market_conditions={'market_price_index': 1.1, 'profit_margin_index': 1.15},
        cost_structure={'seed_cost_index': 0.95, 'input_cost_index': 1.0, 'labor_cost_index': 1.05}
    )

    response = await suitability_service.generate_suitability_matrices(request)
    assert response.total_crops_evaluated == 1
    assert len(response.matrices) == 1
    matrix = response.matrices[0]
    assert matrix.crop_name.lower() == "corn"
    assert matrix.overall_suitability_score >= 0.78
    assert matrix.risk_level.value in ("very_low", "low")
    assert "precomputed_reference" in response.data_sources_used or "real_time_context" in response.data_sources_used


@pytest.mark.asyncio
async def test_generate_matrix_challenging_conditions(suitability_service):
    request = SuitabilityMatrixRequest(
        crop_name="Corn",
        climate_zone="3",
        soil_conditions={
            'ph': 5.0,
            'texture': 'clay',
            'drainage_class': 'poorly_drained',
            'fertility': 'low',
            'salinity': 'high'
        },
        weather_patterns={
            'average_temp_f': 52.0,
            'annual_precip_inches': 18.0,
            'average_humidity_percent': 40.0,
            'wind_risk': 'high'
        },
        pest_pressure={'pest': 'high', 'disease': 'high', 'weed': 'high'},
        management_capabilities={
            'irrigation': 'rainfed',
            'fertility_program': 'limited',
            'equipment': 'basic',
            'labor': 'limited',
            'market_access': 'local',
            'transportation': 'poor',
            'storage': 'limited',
            'processing': 'none'
        },
        market_conditions={'market_price_index': 0.75, 'profit_margin_index': 0.7},
        cost_structure={'seed_cost_index': 1.4, 'input_cost_index': 1.35, 'labor_cost_index': 1.5}
    )

    response = await suitability_service.generate_suitability_matrices(request)
    matrix = response.matrices[0]
    assert matrix.overall_suitability_score <= 0.6
    assert matrix.risk_level.value in ("high", "very_high")
    warnings = []
    for warning in response.risk_warnings:
        warnings.append(warning)
    assert len(warnings) > 0


@pytest.mark.asyncio
async def test_caching_reuse(suitability_service):
    request = SuitabilityMatrixRequest(
        crop_name="Soybean",
        climate_zone="6",
        soil_conditions={'ph': 6.6, 'texture': 'loam', 'drainage_class': 'well_drained'},
        weather_patterns={'average_temp_f': 70.0, 'annual_precip_inches': 30.0}
    )

    response_first = await suitability_service.generate_suitability_matrices(request)
    key_count_before = len(suitability_service.precomputed_matrices)
    response_second = await suitability_service.generate_suitability_matrices(request)
    key_count_after = len(suitability_service.precomputed_matrices)
    assert key_count_after >= key_count_before
    assert response_first.matrices[0].overall_suitability_score == pytest.approx(
        response_second.matrices[0].overall_suitability_score,
        rel=0.001
    )

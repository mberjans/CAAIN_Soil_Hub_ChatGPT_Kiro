"""Tests for VarietyComparisonService."""

import importlib.util
import os
import sys
from typing import List, Optional
from uuid import uuid4

import pytest

_TEST_DIR = os.path.dirname(__file__)
_SRC_PARENT = os.path.abspath(os.path.join(_TEST_DIR, '..'))
_SRC_DIR = os.path.join(_SRC_PARENT, 'src')
_REPO_ROOT = os.path.abspath(os.path.join(_SRC_PARENT, '..', '..'))
_DB_MODELS_DIR = os.path.join(_REPO_ROOT, 'databases', 'python')

if _SRC_PARENT not in sys.path:
    sys.path.insert(0, _SRC_PARENT)
if _DB_MODELS_DIR not in sys.path:
    sys.path.insert(0, _DB_MODELS_DIR)
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

_SERVICE_PATH = os.path.join(_SRC_DIR, 'services', 'variety_comparison_service.py')
_SPEC = importlib.util.spec_from_file_location('variety_comparison_service', _SERVICE_PATH)
assert _SPEC is not None and _SPEC.loader is not None
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
VarietyComparisonService = _MODULE.VarietyComparisonService


class StubVariety:
    """Simple stand-in for EnhancedCropVariety."""

    def __init__(
        self,
        name: str,
        yield_percentile: int,
        resistance_level: str,
        maturity: int,
        market_score: float,
        seed_cost: str = "moderate",
        availability: str = "in_stock",
        management_note: str = ""
    ) -> None:
        self.variety_id = uuid4()
        self.crop_id = uuid4()
        self.variety_name = name
        self.yield_potential_percentile = yield_percentile
        self.yield_stability_rating = 7.5
        self.disease_resistances = []
        disease_entry = {
            "disease_name": "rust",
            "resistance_level": resistance_level
        }
        self.disease_resistances.append(disease_entry)
        self.herbicide_tolerances = []
        self.herbicide_tolerances.append("glyphosate")
        self.stress_tolerances = []
        self.special_management_notes = management_note or None
        self.relative_maturity = maturity
        self.market_acceptance_score = market_score
        self.relative_seed_cost = seed_cost
        self.seed_availability_status = availability
        self.is_active = True


class StubComparisonRequest:
    """Simple stand-in for VarietyComparisonRequest."""

    def __init__(
        self,
        request_id: str,
        varieties: List[StubVariety],
        context: Optional[dict] = None,
        prioritized: Optional[List[str]] = None
    ) -> None:
        self.request_id = request_id
        self.variety_ids = []
        for variety in varieties:
            self.variety_ids.append(variety.variety_id)
        self.provided_varieties = varieties
        self.comparison_context = context or {}
        self.prioritized_factors = prioritized or []
        self.include_trade_offs = True
        self.include_management_analysis = True
        self.include_economic_analysis = True


def _build_variety(
    name: str,
    yield_percentile: int,
    resistance_level: str,
    maturity: int,
    market_score: float,
    seed_cost: str = "moderate",
    availability: str = "in_stock",
    management_note: str = ""
) -> StubVariety:
    """Helper to build a sample variety for testing."""
    return StubVariety(
        name=name,
        yield_percentile=yield_percentile,
        resistance_level=resistance_level,
        maturity=maturity,
        market_score=market_score,
        seed_cost=seed_cost,
        availability=availability,
        management_note=management_note
    )


@pytest.mark.asyncio
async def test_compare_varieties_generates_comprehensive_response() -> None:
    service = VarietyComparisonService()

    variety_list = []
    variety_list.append(_build_variety("Alpha Yield", 92, "resistant", 96, 4.2, seed_cost="moderate", availability="in_stock"))
    variety_list.append(_build_variety("Bravo Guard", 84, "tolerant", 102, 3.6, seed_cost="high", availability="limited", management_note="Requires careful scouting"))

    context = {
        "farmer_preferences": {
            "weight_overrides": {
                "yield_potential": 0.35,
                "disease_resilience": 0.3
            }
        },
        "target_relative_maturity": 95,
        "climate_focus": "short_season"
    }

    request = StubComparisonRequest(
        request_id="unit-test",
        varieties=variety_list,
        context=context,
        prioritized=["yield_potential", "disease_resilience"]
    )

    response = await service.compare_varieties(request)

    assert response.success is True
    assert response.comparison_matrix is not None
    assert len(response.detailed_results) == 2
    assert response.summary is not None
    assert response.summary.best_overall_variety in {variety_list[0].variety_name, variety_list[1].variety_name}
    assert len(response.trade_offs) >= 1
    assert response.data_sources


@pytest.mark.asyncio
async def test_compare_varieties_requires_multiple_varieties() -> None:
    service = VarietyComparisonService()

    single_variety_list = []
    single_variety_list.append(_build_variety("Solo", 80, "moderately_resistant", 100, 3.8))

    request = StubComparisonRequest(
        request_id="single-test",
        varieties=single_variety_list
    )

    response = await service.compare_varieties(request)

    assert response.success is False
    assert response.message is not None

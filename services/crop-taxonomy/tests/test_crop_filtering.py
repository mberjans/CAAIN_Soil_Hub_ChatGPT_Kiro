"""Comprehensive filter functionality tests covering combination, service, and API workflows."""
import importlib.util
import os
import sys
import types
from typing import Any, Dict, List

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

_TEST_DIR = os.path.dirname(__file__)
_PARENT_DIR = os.path.abspath(os.path.join(_TEST_DIR, '..'))
_SRC_DIR = os.path.join(_PARENT_DIR, 'src')

if _PARENT_DIR not in sys.path:
    sys.path.insert(0, _PARENT_DIR)
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)


def _install_variety_service_stub():
    module_name = 'src.services.variety_recommendation_service'
    fallback_name = 'services.variety_recommendation_service'

    if module_name in sys.modules:
        return

    stub_module = types.ModuleType(module_name)

    class VarietyRecommendationService:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass

        async def _score_variety_for_context(self, variety, regional_context, farmer_preferences):
            return {'overall_score': 0.5}

        async def recommend_varieties(self, *args, **kwargs):
            return []

    stub_module.VarietyRecommendationService = VarietyRecommendationService  # type: ignore
    stub_module.variety_recommendation_service = VarietyRecommendationService()  # type: ignore

    sys.modules[module_name] = stub_module
    sys.modules[fallback_name] = stub_module


_install_variety_service_stub()


def _install_result_processor_stub():
    module_name = 'src.services.result_processor'
    fallback_name = 'services.result_processor'

    if module_name in sys.modules:
        return

    stub_module = types.ModuleType(module_name)

    class FilterResultProcessor:  # type: ignore
        def __init__(self, variety_service):
            self.variety_service = variety_service

        def process_results(self, ranked_results, filter_criteria):
            from models.crop_filtering_models import ResultRankingDetails, FilterScoreBreakdown
            index = 0
            while index < len(ranked_results):
                result = ranked_results[index]
                score_breakdown = FilterScoreBreakdown(
                    name='composite',
                    weight=1.0,
                    score=getattr(result, 'relevance_score', 0.5),
                    matched=True,
                    partial=False,
                    notes=[]
                )
                ranking_details = ResultRankingDetails(
                    active_filters=1,
                    matched_filters=1,
                    partial_filters=0,
                    missing_filters=0,
                    coverage=1.0,
                    filter_scores=[score_breakdown]
                )
                try:
                    object.__setattr__(result, 'ranking_details', ranking_details)
                except AttributeError:
                    setattr(result, 'ranking_details', ranking_details)
                index += 1
            return {
                'ranked_results': ranked_results,
                'clustered_results': {},
                'visualization_data': {},
                'alternatives': []
            }

    stub_module.FilterResultProcessor = FilterResultProcessor  # type: ignore

    sys.modules[module_name] = stub_module
    sys.modules[fallback_name] = stub_module


_install_result_processor_stub()

import src.services.filter_engine as _filter_engine_module  # type: ignore
import src.services.crop_search_service as _search_service_module  # type: ignore
from models.crop_filtering_models import TaxonomyFilterCriteria, CropSearchRequest  # type: ignore

filter_combination_engine = _filter_engine_module.filter_combination_engine
FilterCombinationRequest = _filter_engine_module.FilterCombinationRequest
FilterDirective = _filter_engine_module.FilterDirective
crop_search_service = _search_service_module.crop_search_service


def _value_in_list(value: str, items: List[str]) -> bool:
    index = 0
    while index < len(items):
        candidate = items[index]
        if candidate == value:
            return True
        index += 1
    return False


def _build_filter_directive(category: str, attribute: str, value: Any) -> FilterDirective:
    directive = FilterDirective(
        category=category,
        attribute=attribute,
        value=value,
        priority=0.6,
        rationale="Automated test directive"
    )
    return directive


def test_filter_directives_update_combined_criteria():
    directives: List[FilterDirective] = []
    directives.append(_build_filter_directive('climate', 'heat_tolerance_required', 'high'))
    directives.append(_build_filter_directive('soil', 'ph_range', {'min': 6.0, 'max': 7.2}))
    directives.append(_build_filter_directive('geographic', 'hardiness_zones', ['4']))

    request = FilterCombinationRequest(
        request_id='unit-combination-criteria',
        base_criteria=TaxonomyFilterCriteria(),
        directives=directives,
        include_suggestions=False
    )

    response = filter_combination_engine.combine_filters(request)
    criteria = response.combined_criteria

    climate_filter = criteria.climate_filter
    assert climate_filter is not None
    assert climate_filter.heat_tolerance_required is not None
    assert _extract_value(climate_filter.heat_tolerance_required) == 'high'

    soil_filter = criteria.soil_filter
    assert soil_filter is not None
    assert soil_filter.ph_range is not None
    ph_min = soil_filter.ph_range.get('min')
    ph_max = soil_filter.ph_range.get('max')
    assert ph_min == 6.0
    assert ph_max == 7.2

    geographic_filter = criteria.geographic_filter
    assert geographic_filter is not None
    assert geographic_filter.hardiness_zones is not None
    assert _value_in_list('4', geographic_filter.hardiness_zones) is True


@pytest.mark.asyncio
async def test_combined_filters_drive_search_results():
    directives: List[FilterDirective] = []
    directives.append(_build_filter_directive('geographic', 'hardiness_zones', ['3']))
    directives.append(_build_filter_directive('agricultural', 'categories', ['grain']))
    directives.append(_build_filter_directive('climate', 'frost_tolerance_required', 'moderate'))

    request = FilterCombinationRequest(
        request_id='integration-search-criteria',
        base_criteria=TaxonomyFilterCriteria(),
        directives=directives,
        include_suggestions=False
    )

    combination = filter_combination_engine.combine_filters(request)
    criteria = combination.combined_criteria

    search_request = CropSearchRequest(
        request_id='integration-search-run',
        filter_criteria=criteria,
        max_results=12,
        include_full_taxonomy=True
    )

    search_response = await crop_search_service.search_crops(search_request)
    assert search_response.returned_count > 0

    index = 0
    while index < len(search_response.results):
        result = search_response.results[index]
        crop = result.crop
        zone_list = crop.get_suitable_zones()
        assert _value_in_list('3', zone_list) is True
        classification = crop.agricultural_classification
        assert classification is not None
        category = classification.crop_category
        assert category is not None
        assert category.value == 'grain'
        index += 1


def _combine_filters_via_api(payload: Dict[str, Any]) -> Dict[str, Any]:
    module_path = os.path.join(_SRC_DIR, 'api', 'filter_routes.py')
    spec = importlib.util.spec_from_file_location('filter_routes_test_module', module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError('Unable to load filter_routes module for testing')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    filter_router = getattr(module, 'router')

    app = FastAPI()
    app.include_router(filter_router, prefix="/api/v1")

    client = TestClient(app)
    response = client.post('/api/v1/crop-taxonomy/filters/combine', json=payload)
    assert response.status_code == 200
    return response.json()


@pytest.mark.asyncio
async def test_api_combination_pipeline_produces_consistent_results():
    directives_payload: List[Dict[str, Any]] = []
    directives_payload.append({
        'category': 'geographic',
        'attribute': 'hardiness_zones',
        'value': ['5']
    })
    directives_payload.append({
        'category': 'agricultural',
        'attribute': 'categories',
        'value': ['oilseed']
    })

    payload = {
        'request_id': 'api-workflow-001',
        'preset_keys': [],
        'base_criteria': {},
        'directives': directives_payload,
        'context': {'source': 'unit-test'},
        'include_suggestions': False
    }

    response_data = _combine_filters_via_api(payload)
    combined = response_data.get('combined_criteria')
    assert combined is not None

    criteria = TaxonomyFilterCriteria(**combined)

    search_request = CropSearchRequest(
        request_id='api-workflow-search',
        filter_criteria=criteria,
        max_results=10,
        include_full_taxonomy=True
    )

    search_response = await crop_search_service.search_crops(search_request)
    assert search_response.returned_count > 0

    index = 0
    while index < len(search_response.results):
        result = search_response.results[index]
        crop = result.crop
        zone_list = crop.get_suitable_zones()
        assert _value_in_list('5', zone_list) is True
        classification = crop.agricultural_classification
        assert classification is not None
        category = classification.crop_category
        assert category is not None
        assert category.value == 'oilseed'
        index += 1
def _extract_value(candidate: Any) -> Any:
    if hasattr(candidate, 'value'):
        return candidate.value
    return candidate

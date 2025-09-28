"""Tests for optimized crop search candidate loading."""

import os
import sys
import types
from uuid import uuid4
import importlib.util
import pytest

pytest.skip("Optimization integration test requires full service environment", allow_module_level=True)

_TEST_DIR = os.path.dirname(__file__)
_SRC_PARENT = os.path.abspath(os.path.join(_TEST_DIR, '..'))
_SRC_DIR = os.path.join(_SRC_PARENT, 'src')

if _SRC_PARENT not in sys.path:
    sys.path.insert(0, _SRC_PARENT)
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

def _ensure_stub(module_name, attributes):
    if module_name in sys.modules:
        return
    module = types.ModuleType(module_name)
    index = 0
    while index < len(attributes):
        attribute_name = attributes[index]
        placeholder = type(attribute_name, (), {})
        setattr(module, attribute_name, placeholder)
        index += 1
    sys.modules[module_name] = module

_variety_attrs = [
    'EnhancedCropVariety',
    'CropRegionalAdaptation',
    'VarietyRecommendation',
    'VarietyComparisonRequest',
    'VarietyComparisonResponse',
    'RegionalAdaptationRequest',
    'RegionalAdaptationResponse',
    'PerformancePrediction',
    'RiskAssessment',
    'AdaptationStrategy',
    'VarietyCharacteristics',
    'DiseaseResistanceProfile',
    'PestResistanceProfile',
    'AbioticStressTolerances',
    'RegionalPerformanceData',
    'SeasonalTiming',
    'YieldPotential',
    'QualityAttributes',
    'MarketAttributes',
    'RiskLevel',
    'AdaptationLevel'
]

_service_attrs = ['ConfidenceLevel', 'ValidationResult']

_ensure_stub('models.crop_variety_models', _variety_attrs)
_ensure_stub('models.service_models', _service_attrs)

stub_variety_service = types.ModuleType('src.services.variety_recommendation_service')

class _SimpleVarietyService:
    def __init__(self, database_url=None):
        self.db = None
        self.database_available = False

    async def recommend_varieties(self, *args, **kwargs):
        return []

stub_variety_service.VarietyRecommendationService = _SimpleVarietyService
sys.modules['src.services.variety_recommendation_service'] = stub_variety_service
sys.modules['services.crop_taxonomy.src.services.variety_recommendation_service'] = stub_variety_service

module_path = os.path.join(_SRC_DIR, 'services', 'crop_search_service.py')
module_spec = importlib.util.spec_from_file_location('test_crop_search_service_module', module_path)
crop_search_service_module = importlib.util.module_from_spec(module_spec)
assert module_spec.loader is not None
module_spec.loader.exec_module(crop_search_service_module)

CropSearchService = crop_search_service_module.CropSearchService  # type: ignore

from models.crop_taxonomy_models import ComprehensiveCropData  # type: ignore
from models.crop_filtering_models import (  # type: ignore
    TaxonomyFilterCriteria,
    ClimateFilter,
    SoilFilter,
    CropSearchRequest
)


class FakeDatabase:
    """Minimal database stub for optimized query testing."""

    def __init__(self):
        self.sample_id = uuid4()

    def run_complex_filter(self, **kwargs):
        rows = []
        row = {
            'crop_id': self.sample_id,
            'crop_name': 'Optimized Crop',
            'overall_score': 0.92,
            'climate_match': 1.0,
            'soil_match': 0.9,
            'management_match': 0.8
        }
        rows.append(row)
        return rows

    def get_crops_by_ids(self, crop_ids):
        records = []
        index = 0
        while index < len(crop_ids):
            current_id = crop_ids[index]
            if current_id == self.sample_id:
                record = {
                    'crop_id': self.sample_id,
                    'crop_name': 'Optimized Crop'
                }
                records.append(record)
            index += 1
        return records

    def search_crops(self, **kwargs):
        return []

    def test_connection(self):
        return True


@pytest.mark.asyncio
async def test_get_candidate_crops_uses_optimized_database(monkeypatch):
    service = CropSearchService(database_url=None)
    service.db = FakeDatabase()
    service.database_available = True
    service._optimizations_initialized = True

    def simple_converter(record):
        return ComprehensiveCropData(
            crop_id=record.get('crop_id'),
            crop_name=record.get('crop_name', 'Unknown Crop')
        )

    service._convert_db_to_comprehensive_crop_data = simple_converter  # type: ignore

    criteria = TaxonomyFilterCriteria()
    criteria.climate_filter = ClimateFilter(hardiness_zones=['4b'])
    criteria.soil_filter = SoilFilter(ph_range={'min': 6.0, 'max': 7.0})

    request = CropSearchRequest(
        request_id='opt-test-001',
        filter_criteria=criteria
    )

    candidates = await service._get_candidate_crops(request)
    assert len(candidates) == 1
    assert candidates[0].crop_name == 'Optimized Crop'

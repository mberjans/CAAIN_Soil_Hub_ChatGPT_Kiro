"""Tests for advanced confidence calculation service."""

from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict
import importlib.util
import sys


def _load_confidence_module() -> Any:
    """Load the confidence calculation service module dynamically."""
    current_file = Path(__file__).resolve()
    services_dir = current_file.parent.parent / "services"
    module_path = services_dir / "confidence_calculation_service.py"
    spec = importlib.util.spec_from_file_location("confidence_calculation_service", module_path)
    if spec is None or spec.loader is None:
        raise ImportError("Unable to load confidence calculation service module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


confidence_module = _load_confidence_module()
ConfidenceCalculationService = confidence_module.ConfidenceCalculationService


class StubRegionalEntry:
    """Simple stub for regional performance data entries."""

    def __init__(self, region_name: str, climate_zone: str, trials_count: int) -> None:
        self.region_name = region_name
        self.climate_zone = climate_zone
        self.trials_count = trials_count


class StubSeedCompany:
    """Stub seed company entry with last updated timestamp."""

    def __init__(self, last_updated: datetime) -> None:
        self.last_updated = last_updated


def _build_high_quality_variety() -> SimpleNamespace:
    """Construct a high quality variety stub with comprehensive data."""
    variety = SimpleNamespace()
    variety.yield_potential = SimpleNamespace(average_yield_range=(4.5, 6.0), yield_stability_rating=4.2)
    variety.disease_resistance = {"rust_resistance": {"leaf_rust": 4}}
    variety.abiotic_stress_tolerances = SimpleNamespace(drought_tolerance=4, heat_tolerance=4)
    variety.market_attributes = SimpleNamespace(premium_potential=4, market_class="food")
    variety.regional_performance_data = []
    entry_one = StubRegionalEntry("prairie", "zone_3", 6)
    entry_two = StubRegionalEntry("central", "zone_4", 5)
    variety.regional_performance_data.append(entry_one)
    variety.regional_performance_data.append(entry_two)
    variety.seed_companies = []
    company_one = StubSeedCompany(datetime.now(UTC) - timedelta(days=120))
    company_two = StubSeedCompany(datetime.now(UTC) - timedelta(days=240))
    variety.seed_companies.append(company_one)
    variety.seed_companies.append(company_two)
    variety.quality_attributes = ["high protein"]
    variety.breeder_company = "Trusted Genetics"
    variety.data_quality = "high"
    variety.updated_at = datetime.now(UTC) - timedelta(days=90)
    variety.variety_name = "Premium 2025"
    variety.variety_code = "PRM-2025"
    variety.id = "variety-001"
    variety.validation_notes = "Validated across regional trials."
    return variety


def _build_low_quality_variety() -> SimpleNamespace:
    """Construct a variety stub with minimal supporting data."""
    variety = SimpleNamespace()
    variety.yield_potential = None
    variety.disease_resistance = {}
    variety.abiotic_stress_tolerances = None
    variety.market_attributes = None
    variety.regional_performance_data = []
    variety.seed_companies = []
    variety.quality_attributes = []
    variety.breeder_company = None
    variety.data_quality = "low"
    variety.updated_at = datetime.now(UTC) - timedelta(days=1500)
    variety.variety_name = "Unknown"
    variety.variety_code = "UNK-1"
    return variety


def _build_score_data(values: Dict[str, float]) -> Dict[str, float]:
    """Helper to build score data dictionary without comprehensions."""
    score_data: Dict[str, float] = {}
    for key, value in values.items():
        score_data[key] = value
    return score_data


def test_confidence_assessment_high_data_quality():
    """High data quality should yield strong confidence with low uncertainty."""
    service = ConfidenceCalculationService()
    variety = _build_high_quality_variety()

    score_data: Dict[str, Any] = {}
    individual_scores = {"yield_potential": 0.85, "disease_resistance": 0.8, "climate_adaptation": 0.78}
    weighted = {"yield_potential": 0.21, "disease_resistance": 0.16, "climate_adaptation": 0.14}
    score_data["individual_scores"] = _build_score_data(individual_scores)
    score_data["weighted_contributions"] = _build_score_data(weighted)
    score_data["score_details"] = {"yield_potential": "Strong trial results"}
    score_data["overall_score"] = 0.78

    performance_prediction = {
        "predicted_yield_range": (5.0, 6.2),
        "yield_confidence": 0.8,
        "quality_prediction": {"protein_content": "high"},
        "performance_factors": ["Validated trials", "Favorable conditions"]
    }
    risk_assessment = {"overall_risk_level": "low", "specific_risks": [], "mitigation_strategies": []}

    regional_context = {"region": "prairie", "climate_zone": "zone_3"}

    assessment = service.calculate(
        variety=variety,
        score_data=score_data,
        regional_context=regional_context,
        performance_prediction=performance_prediction,
        risk_assessment=risk_assessment
    )

    assert assessment.overall_confidence > 0.65
    assert assessment.confidence_interval[0] < assessment.confidence_interval[1]
    assert assessment.confidence_interval[1] <= 1.0
    assert assessment.data_quality_score > 0.7
    assert assessment.uncertainty_score < 0.5
    assert len(assessment.factor_breakdown) >= 5
    assert len(assessment.explanations) > 0


def test_confidence_assessment_low_data_increases_uncertainty():
    """Sparse data should trigger higher uncertainty and lower confidence."""
    service = ConfidenceCalculationService()

    high_variety = _build_high_quality_variety()
    low_variety = _build_low_quality_variety()

    base_scores = {"yield_potential": 0.6, "disease_resistance": 0.5}
    score_data_high: Dict[str, Any] = {}
    score_data_high["individual_scores"] = _build_score_data(base_scores)
    score_data_high["overall_score"] = 0.7

    score_data_low: Dict[str, Any] = {}
    score_data_low["individual_scores"] = {"yield_potential": 0.4}
    score_data_low["overall_score"] = 0.4

    context = {"region": "prairie"}

    high_assessment = service.calculate(high_variety, score_data_high, context)
    low_assessment = service.calculate(low_variety, score_data_low, context)

    assert high_assessment.overall_confidence > low_assessment.overall_confidence
    assert low_assessment.uncertainty_score >= high_assessment.uncertainty_score
    assert low_assessment.data_quality_score < high_assessment.data_quality_score

"""Tests for the fertilizer program analysis service."""

import sys
import types
from datetime import date, datetime
from pathlib import Path
from typing import List

import pytest


_SRC_DIR = Path(__file__).resolve().parents[1] / "src"
_SRC_PATH = str(_SRC_DIR)
if _SRC_PATH not in sys.path:
    sys.path.insert(0, _SRC_PATH)

_SERVICES_DIR = _SRC_DIR / "services"
_SERVICES_PATH = str(_SERVICES_DIR)
if _SERVICES_PATH not in sys.path:
    sys.path.insert(0, _SERVICES_PATH)

if "timing_services" not in sys.modules:
    timing_pkg = types.ModuleType("timing_services")
    timing_pkg.__path__ = []
    sys.modules["timing_services"] = timing_pkg

if "timing_services.timing_service" not in sys.modules:
    stub_module = types.ModuleType("timing_services.timing_service")

    class _PlaceholderAdapter:
        async def optimize(self, request):  # noqa: D401
            """Placeholder requiring override within tests."""
            raise RuntimeError("TimingOptimizationAdapter should be replaced in tests")

    stub_module.TimingOptimizationAdapter = _PlaceholderAdapter
    sys.modules["timing_services.timing_service"] = stub_module

from models import (  # pylint: disable=import-error
    ApplicationMethod,
    ApplicationTiming,
    FertilizerApplicationRecord,
    ImprovementRecommendation,
    LossRiskAssessment,
    NutrientSynchronizationAssessment,
    ProgramAnalysisContext,
    ProgramAnalysisRequest,
    ProgramAssessmentReport,
    SoilTestResult,
    TimingAssessment,
    WeatherWindow,
    YieldRecord,
)
from models import WeatherCondition  # pylint: disable=import-error
from program_analysis_service import FertilizerProgramAnalysisService  # pylint: disable=import-error
from models import CropGrowthStage, TimingOptimizationResult  # pylint: disable=import-error


class _StubTimingAdapter:
    """Stub timing adapter returning predefined optimization output."""

    def __init__(self) -> None:
        self._result = self._build_result()

    async def optimize(self, request):  # noqa: D401
        """Return predefined optimization result."""
        return self._result

    def _build_result(self) -> TimingOptimizationResult:
        weather_window = WeatherWindow(
            start_date=date(2024, 5, 5),
            end_date=date(2024, 5, 12),
            condition=WeatherCondition.OPTIMAL,
            temperature_f=65.0,
            precipitation_probability=0.2,
            wind_speed_mph=8.0,
            soil_moisture=0.55,
            suitability_score=0.85,
        )

        timing_entries: List[ApplicationTiming] = []
        nitrogen_timing = ApplicationTiming(
            fertilizer_type="nitrogen",
            application_method=ApplicationMethod.SIDE_DRESS,
            recommended_date=date(2024, 5, 10),
            application_window=weather_window,
            crop_stage=CropGrowthStage.V6,
            amount_lbs_per_acre=120.0,
            timing_score=0.88,
            weather_score=0.80,
            crop_score=0.90,
            soil_score=0.75,
            weather_risk=0.2,
            timing_risk=0.15,
            equipment_risk=0.1,
            estimated_cost_per_acre=75.0,
            yield_impact_percent=8.0,
            alternative_dates=[],
            backup_window=None,
        )
        timing_entries.append(nitrogen_timing)

        phosphorus_timing = ApplicationTiming(
            fertilizer_type="phosphorus",
            application_method=ApplicationMethod.BROADCAST,
            recommended_date=date(2024, 4, 20),
            application_window=weather_window,
            crop_stage=CropGrowthStage.V4,
            amount_lbs_per_acre=60.0,
            timing_score=0.82,
            weather_score=0.75,
            crop_score=0.85,
            soil_score=0.78,
            weather_risk=0.25,
            timing_risk=0.20,
            equipment_risk=0.1,
            estimated_cost_per_acre=55.0,
            yield_impact_percent=4.0,
            alternative_dates=[],
            backup_window=None,
        )
        timing_entries.append(phosphorus_timing)

        recommendations: List[str] = []
        recommendations.append("Follow nitrogen sidedress window")
        recommendations.append("Synchronize phosphorus broadcast with planting")

        result = TimingOptimizationResult(
            request_id="stub-request",
            optimal_timings=timing_entries,
            split_plans=[],
            weather_windows=[weather_window],
            weather_forecast_days=14,
            overall_timing_score=0.85,
            weather_suitability_score=0.78,
            crop_stage_alignment_score=0.82,
            risk_score=0.3,
            total_estimated_cost=13000.0,
            cost_per_acre=95.0,
            expected_yield_impact=5.0,
            roi_estimate=0.22,
            recommendations=recommendations,
            risk_mitigation_strategies=[],
            alternative_strategies=[],
            optimization_method="multi_objective",
            confidence_score=0.7,
            processing_time_ms=250.0,
            created_at=datetime.utcnow(),
        )
        return result


def _build_sample_request() -> ProgramAnalysisRequest:
    context = ProgramAnalysisContext(
        field_id="field-1",
        crop_name="corn",
        planting_date=date(2024, 4, 15),
        expected_harvest_date=date(2024, 10, 1),
        fertilizer_requirements={"nitrogen": 180.0, "phosphorus": 60.0},
        soil_type="silty clay loam",
        soil_moisture_capacity=0.58,
        drainage_class="moderate",
        slope_percent=5.0,
        location={"lat": 41.0, "lng": -93.0},
    )

    program_entries: List[FertilizerApplicationRecord] = []
    nitrogen_application = FertilizerApplicationRecord(
        application_id="app-1",
        fertilizer_type="nitrogen",
        application_method="side dress",
        applied_date=date(2024, 5, 9),
        amount_lbs_per_acre=125.0,
        target_nutrient="nitrogen",
        crop_stage="v6",
        weather_condition="clear",
        field_condition="good",
        efficiency_estimate=0.82,
        notes="Timely sidedress with optimal moisture",
    )
    program_entries.append(nitrogen_application)

    phosphorus_application = FertilizerApplicationRecord(
        application_id="app-2",
        fertilizer_type="phosphorus",
        application_method="broadcast",
        applied_date=date(2024, 4, 25),
        amount_lbs_per_acre=55.0,
        target_nutrient="phosphorus",
        crop_stage="v4",
        weather_condition="cloudy",
        field_condition="firm",
        efficiency_estimate=0.76,
        notes="Applied during light rain forecast",
    )
    program_entries.append(phosphorus_application)

    soil_tests: List[SoilTestResult] = []
    soil_tests.append(
        SoilTestResult(
            sample_date=date(2024, 3, 1),
            lab_name="Midwest Lab",
            ph=6.4,
            organic_matter_percent=3.1,
            cation_exchange_capacity=18.5,
            nutrient_levels={"nitrogen": 18.0, "phosphorus": 22.0, "potassium": 140.0},
            texture_class="silty clay loam",
        )
    )

    yields: List[YieldRecord] = []
    yields.append(YieldRecord(season="2023", harvested_acres=150.0, yield_per_acre=190.0, target_yield_per_acre=200.0))
    yields.append(YieldRecord(season="2024", harvested_acres=150.0, yield_per_acre=195.0, target_yield_per_acre=205.0))

    request = ProgramAnalysisRequest(
        context=context,
        current_program=program_entries,
        soil_tests=soil_tests,
        yield_history=yields,
        operational_notes=["Monitored soil temps", "Dry spell after phosphorus"],
        environmental_incidents=["Minor runoff in May"],
    )
    return request


@pytest.mark.asyncio
async def test_analyze_program_generates_report() -> None:
    service = FertilizerProgramAnalysisService()
    service._timing_adapter = _StubTimingAdapter()  # type: ignore[attr-defined]

    request = _build_sample_request()
    report = await service.analyze_program(request)

    assert isinstance(report, ProgramAssessmentReport)
    assert isinstance(report.timing_assessment, TimingAssessment)
    assert report.timing_assessment.on_time_percentage >= 0.5
    assert isinstance(report.nutrient_assessment, NutrientSynchronizationAssessment)
    assert report.nutrient_assessment.synchronization_score > 0
    assert isinstance(report.loss_assessment, LossRiskAssessment)
    assert isinstance(report.recommendations, list)
    assert isinstance(report.recommendations[0], ImprovementRecommendation)


@pytest.mark.asyncio
async def test_analysis_handles_empty_program() -> None:
    service = FertilizerProgramAnalysisService()

    context = ProgramAnalysisContext(
        field_id="field-empty",
        crop_name="soybean",
        planting_date=date(2024, 5, 1),
        expected_harvest_date=None,
        fertilizer_requirements={"nitrogen": 40.0},
        soil_type="loam",
        soil_moisture_capacity=0.45,
        drainage_class="well",
        slope_percent=2.0,
        location={"lat": 40.0, "lng": -90.0},
    )

    request = ProgramAnalysisRequest(
        context=context,
        current_program=[],
        soil_tests=[],
        yield_history=[],
        operational_notes=[],
        environmental_incidents=[],
    )

    report = await service.analyze_program(request)

    assert isinstance(report, ProgramAssessmentReport)
    assert report.timing_assessment.average_deviation_days == 0.0
    assert report.timing_assessment.on_time_percentage == 1.0
    assert len(report.recommendations) == 1

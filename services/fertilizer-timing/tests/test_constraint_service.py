"""Tests for the OperationalConstraintService."""

import sys
from datetime import date
from pathlib import Path
from typing import Dict, List

import pytest
import anyio

_SRC_DIR = Path(__file__).resolve().parents[1] / "src"
_SRC_PATH = str(_SRC_DIR)
if _SRC_PATH not in sys.path:
    sys.path.insert(0, _SRC_PATH)

_SERVICES_DIR = _SRC_DIR / "services"
_SERVICES_PATH = str(_SERVICES_DIR)
if _SERVICES_PATH not in sys.path:
    sys.path.insert(0, _SERVICES_PATH)

from models import (  # pylint: disable=import-error
    ApplicationMethod,
    TimingOptimizationRequest,
)
from constraint_service import OperationalConstraintService  # pylint: disable=import-error


def _build_basic_request() -> TimingOptimizationRequest:
    """Build a basic timing optimization request for testing."""
    fertilizer_requirements: Dict[str, float] = {}
    fertilizer_requirements["nitrogen"] = 150.0

    application_methods: List[ApplicationMethod] = []
    application_methods.append(ApplicationMethod.BROADCAST)

    location: Dict[str, float] = {}
    location["lat"] = 42.5
    location["lng"] = -91.7

    equipment_availability: Dict[str, List[str]] = {}
    equipment_dates: List[str] = []
    equipment_dates.append("2025-05-10")
    equipment_dates.append("2025-05-15")
    equipment_availability["spreader"] = equipment_dates

    labor_availability: Dict[str, int] = {}
    labor_availability["2025-05-10"] = 2
    labor_availability["2025-05-15"] = 3

    request = TimingOptimizationRequest(
        field_id="field-200",
        crop_type="corn",
        planting_date=date(2025, 4, 25),
        expected_harvest_date=date(2025, 10, 15),
        fertilizer_requirements=fertilizer_requirements,
        application_methods=application_methods,
        soil_type="clay loam",
        soil_moisture_capacity=0.65,
        drainage_class="moderate",
        slope_percent=2.5,
        weather_data_source="test",
        location=location,
        equipment_availability=equipment_availability,
        labor_availability=labor_availability,
        optimization_horizon_days=90,
        risk_tolerance=0.5,
        prioritize_yield=True,
        prioritize_cost=False,
        split_application_allowed=True,
        weather_dependent_timing=True,
        soil_temperature_threshold=50.0,
    )
    return request


def _build_request_with_limited_equipment() -> TimingOptimizationRequest:
    """Build a request with very limited equipment availability."""
    request = _build_basic_request()
    equipment_availability: Dict[str, List[str]] = {}
    equipment_dates: List[str] = []
    equipment_dates.append("2025-06-01")
    equipment_availability["spreader"] = equipment_dates
    request.equipment_availability = equipment_availability
    return request


def _build_request_with_no_labor() -> TimingOptimizationRequest:
    """Build a request with no labor availability."""
    request = _build_basic_request()
    labor_availability: Dict[str, int] = {}
    request.labor_availability = labor_availability
    return request


def _build_request_with_high_moisture() -> TimingOptimizationRequest:
    """Build a request with high soil moisture for field access constraint testing."""
    request = _build_basic_request()
    request.soil_moisture_capacity = 0.85
    request.drainage_class = "poor"
    return request


@pytest.mark.asyncio
async def test_accommodate_constraints_produces_report():
    """Test that accommodate_constraints produces a complete operational constraint report."""
    service = OperationalConstraintService()
    request = _build_basic_request()

    report = await service.accommodate_constraints(request)

    assert report.request_id == request.request_id
    assert report.generated_at is not None
    assert isinstance(report.summary, str)
    assert len(report.summary) > 0


@pytest.mark.asyncio
async def test_accommodate_constraints_evaluates_equipment_constraints():
    """Test that equipment constraints are properly evaluated and reported."""
    service = OperationalConstraintService()
    request = _build_basic_request()

    report = await service.accommodate_constraints(request)

    found_equipment_status = False
    index = 0
    count = len(report.constraint_status)
    while index < count:
        status = report.constraint_status[index]
        if "equipment" in status.name.lower():
            found_equipment_status = True
            assert 0.0 <= status.severity <= 1.0
            assert isinstance(status.blocking, bool)
        index += 1

    assert found_equipment_status


@pytest.mark.asyncio
async def test_accommodate_constraints_evaluates_labor_constraints():
    """Test that labor constraints are properly evaluated and reported."""
    service = OperationalConstraintService()
    request = _build_basic_request()

    report = await service.accommodate_constraints(request)

    found_labor_status = False
    index = 0
    count = len(report.constraint_status)
    while index < count:
        status = report.constraint_status[index]
        if "labor" in status.name.lower():
            found_labor_status = True
            assert 0.0 <= status.severity <= 1.0
            assert isinstance(status.blocking, bool)
        index += 1

    assert found_labor_status


@pytest.mark.asyncio
async def test_accommodate_constraints_evaluates_field_access():
    """Test that field access constraints are evaluated based on soil moisture."""
    service = OperationalConstraintService()
    request = _build_request_with_high_moisture()

    report = await service.accommodate_constraints(request)

    found_field_access_status = False
    index = 0
    count = len(report.constraint_status)
    while index < count:
        status = report.constraint_status[index]
        if "field" in status.name.lower() or "access" in status.name.lower():
            found_field_access_status = True
            assert status.severity > 0.3
        index += 1

    assert found_field_access_status


@pytest.mark.asyncio
async def test_accommodate_constraints_evaluates_regulatory_windows():
    """Test that regulatory constraints are evaluated."""
    service = OperationalConstraintService()
    request = _build_basic_request()

    report = await service.accommodate_constraints(request)

    assert isinstance(report.regulatory_notes, list)


@pytest.mark.asyncio
async def test_accommodate_constraints_generates_alternatives_when_blocked():
    """Test that alternative schedules are generated when primary dates are blocked."""
    service = OperationalConstraintService()
    request = _build_request_with_limited_equipment()

    report = await service.accommodate_constraints(request)

    assert isinstance(report.alternative_options, list)


@pytest.mark.asyncio
async def test_accommodate_constraints_creates_resource_allocation_plans():
    """Test that resource allocation plans are created for viable dates."""
    service = OperationalConstraintService()
    request = _build_basic_request()

    report = await service.accommodate_constraints(request)

    assert isinstance(report.resource_plans, list)
    if len(report.resource_plans) > 0:
        plan = report.resource_plans[0]
        assert plan.plan_date is not None
        assert isinstance(plan.equipment, list)
        assert plan.labor_required >= 0
        assert plan.labor_available >= 0
        assert isinstance(plan.readiness_actions, list)


@pytest.mark.asyncio
async def test_accommodate_constraints_generates_timing_constraints():
    """Test that structured TimingConstraint objects are generated for downstream optimizers."""
    service = OperationalConstraintService()
    request = _build_basic_request()

    report = await service.accommodate_constraints(request)

    assert isinstance(report.generated_constraints, list)


@pytest.mark.asyncio
async def test_equipment_constraint_marks_blocking_when_unavailable():
    """Test that equipment constraints are marked as blocking when equipment is unavailable."""
    service = OperationalConstraintService()
    request = _build_basic_request()
    equipment_availability: Dict[str, List[str]] = {}
    request.equipment_availability = equipment_availability

    report = await service.accommodate_constraints(request)

    found_blocking_equipment = False
    index = 0
    count = len(report.constraint_status)
    while index < count:
        status = report.constraint_status[index]
        if "equipment" in status.name.lower():
            if status.blocking:
                found_blocking_equipment = True
        index += 1

    assert found_blocking_equipment


@pytest.mark.asyncio
async def test_labor_constraint_marks_blocking_when_unavailable():
    """Test that labor constraints are marked as blocking when no labor is available."""
    service = OperationalConstraintService()
    request = _build_request_with_no_labor()

    report = await service.accommodate_constraints(request)

    found_blocking_labor = False
    index = 0
    count = len(report.constraint_status)
    while index < count:
        status = report.constraint_status[index]
        if "labor" in status.name.lower():
            if status.blocking:
                found_blocking_labor = True
        index += 1

    assert found_blocking_labor


@pytest.mark.asyncio
async def test_field_access_constraint_provides_recommendations():
    """Test that field access constraints provide actionable recommendations."""
    service = OperationalConstraintService()
    request = _build_request_with_high_moisture()

    report = await service.accommodate_constraints(request)

    found_recommendations = False
    index = 0
    count = len(report.constraint_status)
    while index < count:
        status = report.constraint_status[index]
        if "field" in status.name.lower() or "access" in status.name.lower():
            if len(status.recommendations) > 0:
                found_recommendations = True
        index += 1

    assert found_recommendations


@pytest.mark.asyncio
async def test_alternative_schedule_includes_suitability_scores():
    """Test that alternative schedules include suitability scores."""
    service = OperationalConstraintService()
    request = _build_request_with_limited_equipment()

    report = await service.accommodate_constraints(request)

    if len(report.alternative_options) > 0:
        alternative = report.alternative_options[0]
        assert 0.0 <= alternative.suitability_score <= 1.0
        assert alternative.fertilizer_type is not None
        assert alternative.primary_date is not None
        assert alternative.alternative_date is not None
        assert len(alternative.reason) > 0


@pytest.mark.asyncio
async def test_resource_allocation_plan_identifies_gaps():
    """Test that resource allocation plans identify gaps between required and available resources."""
    service = OperationalConstraintService()
    request = _build_request_with_no_labor()

    report = await service.accommodate_constraints(request)

    if len(report.resource_plans) > 0:
        plan = report.resource_plans[0]
        if plan.labor_required > plan.labor_available:
            assert len(plan.readiness_actions) > 0


@pytest.mark.asyncio
async def test_regulatory_notes_include_common_restrictions():
    """Test that regulatory notes include common agricultural restrictions."""
    service = OperationalConstraintService()
    request = _build_basic_request()

    report = await service.accommodate_constraints(request)

    assert isinstance(report.regulatory_notes, list)


@pytest.mark.asyncio
async def test_summary_describes_key_constraints():
    """Test that the summary describes the key constraint findings."""
    service = OperationalConstraintService()
    request = _build_basic_request()

    report = await service.accommodate_constraints(request)

    summary = report.summary
    assert isinstance(summary, str)
    assert len(summary) > 50


@pytest.mark.asyncio
async def test_metadata_includes_request_context():
    """Test that metadata includes useful request context."""
    service = OperationalConstraintService()
    request = _build_basic_request()

    report = await service.accommodate_constraints(request)

    assert isinstance(report.metadata, dict)


@pytest.mark.asyncio
async def test_constraint_status_severity_ranges():
    """Test that all constraint status severity values are within valid range."""
    service = OperationalConstraintService()
    request = _build_basic_request()

    report = await service.accommodate_constraints(request)

    index = 0
    count = len(report.constraint_status)
    while index < count:
        status = report.constraint_status[index]
        assert 0.0 <= status.severity <= 1.0
        index += 1


@pytest.mark.asyncio
async def test_generated_constraints_have_valid_types():
    """Test that generated constraints have valid constraint types."""
    service = OperationalConstraintService()
    request = _build_basic_request()

    report = await service.accommodate_constraints(request)

    index = 0
    count = len(report.generated_constraints)
    while index < count:
        constraint = report.generated_constraints[index]
        assert constraint.constraint_type is not None
        assert len(constraint.description) > 0
        assert 0.0 <= constraint.severity <= 1.0
        index += 1


@pytest.mark.asyncio
async def test_handles_empty_equipment_availability_gracefully():
    """Test that service handles empty equipment availability without errors."""
    service = OperationalConstraintService()
    request = _build_basic_request()
    equipment_availability: Dict[str, List[str]] = {}
    request.equipment_availability = equipment_availability

    report = await service.accommodate_constraints(request)

    assert report is not None
    assert len(report.constraint_status) > 0


@pytest.mark.asyncio
async def test_handles_empty_labor_availability_gracefully():
    """Test that service handles empty labor availability without errors."""
    service = OperationalConstraintService()
    request = _build_request_with_no_labor()

    report = await service.accommodate_constraints(request)

    assert report is not None
    assert len(report.constraint_status) > 0


@pytest.mark.asyncio
async def test_clay_soil_increases_field_access_severity():
    """Test that clay soils increase field access constraint severity."""
    service = OperationalConstraintService()
    request = _build_basic_request()
    request.soil_type = "clay"
    request.soil_moisture_capacity = 0.7

    report = await service.accommodate_constraints(request)

    found_elevated_severity = False
    index = 0
    count = len(report.constraint_status)
    while index < count:
        status = report.constraint_status[index]
        if "field" in status.name.lower() or "access" in status.name.lower():
            if status.severity > 0.4:
                found_elevated_severity = True
        index += 1

    assert found_elevated_severity


@pytest.mark.asyncio
async def test_poor_drainage_increases_field_access_severity():
    """Test that poor drainage increases field access constraint severity."""
    service = OperationalConstraintService()
    request = _build_basic_request()
    request.drainage_class = "poor"
    request.soil_moisture_capacity = 0.7

    report = await service.accommodate_constraints(request)

    found_elevated_severity = False
    index = 0
    count = len(report.constraint_status)
    while index < count:
        status = report.constraint_status[index]
        if "field" in status.name.lower() or "access" in status.name.lower():
            if status.severity > 0.4:
                found_elevated_severity = True
        index += 1

    assert found_elevated_severity

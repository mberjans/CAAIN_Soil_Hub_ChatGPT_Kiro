import pytest
from datetime import datetime
from uuid import uuid4

from services.micronutrient_management.src.models.micronutrient_models import MicronutrientPrice, ApplicationCost, MicronutrientBudgetAnalysisResult
from services.micronutrient_management.src.services.micronutrient_cost_service import MicronutrientCostService

@pytest.fixture
def micronutrient_cost_service():
    return MicronutrientCostService()

@pytest.fixture
def sample_farm_id():
    return uuid4()

@pytest.fixture
def sample_field_id():
    return uuid4()

@pytest.fixture
def sample_micronutrient_recommendations():
    return [
        {"name": "Boron", "rate": 0.5, "unit": "kg/ha"},
        {"name": "Zinc", "rate": 1.0, "unit": "kg/ha"},
    ]

@pytest.fixture
def sample_micronutrient_prices():
    return [
        MicronutrientPrice(micronutrient_name="Boron", price_per_unit=10.0, unit="kg", currency="USD"),
        MicronutrientPrice(micronutrient_name="Zinc", price_per_unit=15.0, unit="kg", currency="USD"),
        MicronutrientPrice(micronutrient_name="Manganese", price_per_unit=12.0, unit="kg", currency="USD"),
    ]

@pytest.fixture
def sample_application_costs():
    return [
        ApplicationCost(description="Labor", cost_per_unit=20.0, unit="hour", quantity=5.0, total_cost=100.0),
        ApplicationCost(description="Equipment Rental", cost_per_unit=50.0, unit="day", quantity=1.0, total_cost=50.0),
    ]

@pytest.mark.asyncio
async def test_analyze_micronutrient_budget_success(
    micronutrient_cost_service,
    sample_farm_id,
    sample_field_id,
    sample_micronutrient_recommendations,
    sample_micronutrient_prices,
    sample_application_costs
):
    field_area_hectares = 10.0
    result = await micronutrient_cost_service.analyze_micronutrient_budget(
        farm_id=sample_farm_id,
        field_id=sample_field_id,
        micronutrient_recommendations=sample_micronutrient_recommendations,
        micronutrient_prices=sample_micronutrient_prices,
        application_costs=sample_application_costs,
        field_area_hectares=field_area_hectares
    )

    assert isinstance(result, MicronutrientBudgetAnalysisResult)
    assert result.farm_id == str(sample_farm_id)
    assert result.field_id == str(sample_field_id)
    assert result.total_micronutrient_cost == (0.5 * 10.0 * 10.0) + (1.0 * 10.0 * 15.0)  # Boron + Zinc
    assert result.total_application_cost == 150.0
    assert result.overall_total_cost == result.total_micronutrient_cost + result.total_application_cost
    assert result.cost_per_hectare == result.overall_total_cost / field_area_hectares

@pytest.mark.asyncio
async def test_analyze_micronutrient_budget_no_matching_price(
    micronutrient_cost_service,
    sample_farm_id,
    sample_field_id,
    sample_application_costs
):
    micronutrient_recommendations = [
        {"name": "Molybdenum", "rate": 0.1, "unit": "kg/ha"},
    ]
    micronutrient_prices = [
        MicronutrientPrice(micronutrient_name="Boron", price_per_unit=10.0, unit="kg", currency="USD"),
    ]
    field_area_hectares = 5.0

    result = await micronutrient_cost_service.analyze_micronutrient_budget(
        farm_id=sample_farm_id,
        field_id=sample_field_id,
        micronutrient_recommendations=micronutrient_recommendations,
        micronutrient_prices=micronutrient_prices,
        application_costs=sample_application_costs,
        field_area_hectares=field_area_hectares
    )

    assert result.total_micronutrient_cost == 0.0  # No matching price, so cost is 0
    assert result.total_application_cost == 150.0
    assert result.overall_total_cost == 150.0

@pytest.mark.asyncio
async def test_analyze_micronutrient_budget_zero_field_area(
    micronutrient_cost_service,
    sample_farm_id,
    sample_field_id,
    sample_micronutrient_recommendations,
    sample_micronutrient_prices,
    sample_application_costs
):
    field_area_hectares = 0.0
    result = await micronutrient_cost_service.analyze_micronutrient_budget(
        farm_id=sample_farm_id,
        field_id=sample_field_id,
        micronutrient_recommendations=sample_micronutrient_recommendations,
        micronutrient_prices=sample_micronutrient_prices,
        application_costs=sample_application_costs,
        field_area_hectares=field_area_hectares
    )

    assert result.total_micronutrient_cost == 0.0
    assert result.total_application_cost == 150.0
    assert result.overall_total_cost == 150.0
    assert result.cost_per_hectare == 0.0

@pytest.mark.asyncio
async def test_analyze_micronutrient_budget_empty_recommendations(
    micronutrient_cost_service,
    sample_farm_id,
    sample_field_id,
    sample_micronutrient_prices,
    sample_application_costs
):
    field_area_hectares = 10.0
    result = await micronutrient_cost_service.analyze_micronutrient_budget(
        farm_id=sample_farm_id,
        field_id=sample_field_id,
        micronutrient_recommendations=[],
        micronutrient_prices=sample_micronutrient_prices,
        application_costs=sample_application_costs,
        field_area_hectares=field_area_hectares
    )

    assert result.total_micronutrient_cost == 0.0
    assert result.total_application_cost == 150.0
    assert result.overall_total_cost == 150.0
    assert result.cost_per_hectare == 15.0

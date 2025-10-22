import pytest
from services.fertilizer_application.schemas.optimization_schemas import OptimizationRequest


def test_optimization_request_valid():
    """Test creating a valid OptimizationRequest instance and verifying its attributes."""
    # Sample data for the OptimizationRequest
    field_acres = 100.0
    nutrient_requirements = {'N': 50, 'P': 30, 'K': 20}
    yield_goal_bu_acre = 200.0
    available_fertilizers = ['Urea', 'DAP', 'Potash']

    # Create an instance of OptimizationRequest
    request = OptimizationRequest(
        field_acres=field_acres,
        nutrient_requirements=nutrient_requirements,
        yield_goal_bu_acre=yield_goal_bu_acre,
        available_fertilizers=available_fertilizers
    )

    # Verify the attributes
    assert request.field_acres == field_acres
    assert request.nutrient_requirements == nutrient_requirements
    assert request.yield_goal_bu_acre == yield_goal_bu_acre
    assert request.available_fertilizers == available_fertilizers
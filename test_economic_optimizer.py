import pytest
from services.fertilizer_application.src.services.economic_optimization_service import (
    EconomicOptimizationService,
    OptimizationObjective,
    OptimizationAlgorithm,
    ApplicationMethod,
    FieldConditions,
    CropRequirements,
    FertilizerSpecification,
    EquipmentSpecification,
    OptimizationConstraint
)


def test_roi_calculation():
    """
    Test ROI calculation for EconomicOptimizationService.

    This test creates an EconomicOptimizationService instance and verifies
    that it can calculate ROI based on fertilizer costs and expected yield improvements.
    """
    # Create an instance of EconomicOptimizationService
    optimizer = EconomicOptimizationService()

    # Create sample application methods
    method1 = ApplicationMethod(
        method_id="method1",
        name="Broadcast Spreading",
        description="Broadcast fertilizer spreading",
        application_rate=100.0,
        efficiency=0.8,
        cost_per_unit=50.0,
        equipment_required=["spreader"]
    )
    method2 = ApplicationMethod(
        method_id="method2",
        name="Precision Application",
        description="Precision fertilizer application",
        application_rate=80.0,
        efficiency=0.9,
        cost_per_unit=70.0,
        equipment_required=["precision_applicator"]
    )
    application_methods = [method1, method2]

    # Create sample field conditions
    field_conditions = FieldConditions(
        field_size_acres=100.0,
        soil_type="clay",
        topography="flat",
        current_weather="dry",
        accessibility="good"
    )

    # Create sample crop requirements
    crop_requirements = CropRequirements(
        crop_type="corn",
        growth_stage="vegetative",
        nutrient_needs={"nitrogen": 150.0, "phosphorus": 50.0},
        yield_goal=200.0,
        planting_date="2023-04-01",
        harvest_date="2023-10-01"
    )

    # Create sample fertilizer specification
    fertilizer_specification = FertilizerSpecification(
        fertilizer_type="urea",
        nutrient_content={"nitrogen": 46.0, "phosphorus": 0.0},
        application_rate=100.0,
        cost_per_ton=400.0,
        availability=0.95
    )

    # Create sample equipment
    equipment1 = EquipmentSpecification(
        equipment_id="spreader",
        name="Broadcast Spreader",
        capacity=1000.0,
        efficiency=0.8,
        operating_cost_per_hour=50.0,
        fuel_consumption=10.0
    )
    equipment2 = EquipmentSpecification(
        equipment_id="precision_applicator",
        name="Precision Applicator",
        capacity=500.0,
        efficiency=0.9,
        operating_cost_per_hour=70.0,
        fuel_consumption=8.0
    )
    available_equipment = [equipment1, equipment2]

    # Define optimization objective for ROI maximization
    objective = OptimizationObjective.MAXIMIZE_ROI

    # Run optimization
    result = optimizer.optimize_application_methods(
        application_methods=application_methods,
        field_conditions=field_conditions,
        crop_requirements=crop_requirements,
        fertilizer_specification=fertilizer_specification,
        available_equipment=available_equipment,
        objective=objective,
        algorithm=OptimizationAlgorithm.LINEAR_PROGRAMMING
    )

    # Assertions
    assert result is not None
    assert len(result.optimal_methods) > 0
    assert result.objective_value is not None
    assert result.algorithm_used == OptimizationAlgorithm.LINEAR_PROGRAMMING.value
    assert result.optimization_time_ms >= 0

    # Verify that ROI is being maximized (objective value should be negative for maximization in linprog)
    # Since we're maximizing ROI, the objective_value should be the negative of the best ROI
    # We can check that it's a finite number and makes sense in context
    assert isinstance(result.objective_value, (int, float))
    assert result.objective_value != float('inf')

    # Additional check: Ensure at least one method is selected
    selected_methods = [method for method in result.optimal_methods if method.get("selection_weight", 0) > 0.5]
    assert len(selected_methods) >= 1
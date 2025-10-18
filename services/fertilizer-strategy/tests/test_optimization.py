"""
Accuracy and performance tests for fertilizer optimization algorithms.

These tests focus on verifying that the fertilizer ROI optimization
logic produces financially accurate results and meets performance
expectations under concurrent workloads.
"""

import asyncio
import sys
import time
from pathlib import Path

import numpy as np
import pytest


CURRENT_FILE = Path(__file__).resolve()
BASE_DIR = CURRENT_FILE.parents[1]

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.models.roi_models import (  # noqa: E402
    FieldData,
    FertilizerProduct,
    OptimizationConstraints,
    OptimizationGoals,
    OptimizationMethod,
    ROIOptimizationRequest,
    RiskTolerance
)
from src.services.roi_optimizer import FertilizerROIOptimizer  # noqa: E402


def _build_accuracy_request() -> ROIOptimizationRequest:
    """
    Build a deterministic request tailored for accuracy validation.

    Returns:
        ROIOptimizationRequest configured for linear programming validation.
    """
    field = FieldData(
        field_id="accuracy_field_1",
        acres=50.0,
        soil_tests={"N": 35.0, "P": 40.0, "K": 120.0, "pH": 6.4},
        crop_plan={"crop": "corn", "variety": "deterministic"},
        target_yield=180.0,
        crop_price=5.25
    )

    product = FertilizerProduct(
        product_id="urea_accuracy",
        product_name="Urea 46-0-0",
        nutrient_content={"N": 46.0},
        price_per_unit=50.0,
        unit="ton",
        application_method="broadcast"
    )

    constraints = OptimizationConstraints(
        max_nitrogen_rate=120.0,
        max_per_acre_cost=120.0,
        budget_limit=6000.0
    )

    goals = OptimizationGoals(
        primary_goal="profit_maximization",
        yield_priority=0.8,
        cost_priority=0.6,
        environmental_priority=0.4,
        risk_tolerance=RiskTolerance.MODERATE
    )

    request = ROIOptimizationRequest(
        farm_context={"farm_id": "accuracy_validation_farm"},
        fields=[field],
        fertilizer_products=[product],
        constraints=constraints,
        goals=goals,
        optimization_method=OptimizationMethod.LINEAR_PROGRAMMING,
        include_sensitivity_analysis=False,
        include_risk_assessment=False
    )

    return request


def _build_performance_request(
    field_count: int,
    include_analysis: bool
) -> ROIOptimizationRequest:
    """
    Build a request used for performance and concurrency validation.

    Args:
        field_count: Number of fields to include.
        include_analysis: Whether to execute risk and sensitivity analysis.

    Returns:
        ROIOptimizationRequest configured for performance testing.
    """
    fields = []
    for index in range(field_count):
        acres_value = 55.0 + float(index) * 5.0
        soil_n = 28.0 + float(index) * 2.0
        field = FieldData(
            field_id=f"performance_field_{index}",
            acres=acres_value,
            soil_tests={"N": soil_n, "P": 35.0, "K": 140.0, "pH": 6.3},
            crop_plan={"crop": "corn", "phase": "grain"},
            target_yield=175.0 + float(index) * 2.0,
            crop_price=5.10 + float(index) * 0.05
        )
        fields.append(field)

    products = []
    nitrogen_product = FertilizerProduct(
        product_id="urea_performance",
        product_name="Urea 46-0-0",
        nutrient_content={"N": 46.0},
        price_per_unit=55.0,
        unit="ton",
        application_method="broadcast"
    )
    products.append(nitrogen_product)

    phosphorus_product = FertilizerProduct(
        product_id="map_performance",
        product_name="MAP 11-52-0",
        nutrient_content={"N": 11.0, "P": 52.0},
        price_per_unit=61.0,
        unit="ton",
        application_method="broadcast"
    )
    products.append(phosphorus_product)

    constraints = OptimizationConstraints(
        max_nitrogen_rate=160.0,
        max_phosphorus_rate=110.0,
        max_per_acre_cost=145.0,
        budget_limit=8200.0,
        environmental_limits={"buffer_zones": True},
        equipment_limitations=["broadcast_spreader"]
    )

    goals = OptimizationGoals(
        primary_goal="profit_maximization",
        yield_priority=0.75,
        cost_priority=0.65,
        environmental_priority=0.55,
        risk_tolerance=RiskTolerance.MODERATE
    )

    request = ROIOptimizationRequest(
        farm_context={"farm_id": "performance_validation_farm"},
        fields=fields,
        fertilizer_products=products,
        constraints=constraints,
        goals=goals,
        optimization_method=OptimizationMethod.LINEAR_PROGRAMMING,
        include_sensitivity_analysis=include_analysis,
        include_risk_assessment=include_analysis
    )

    return request


def _find_field(fields, field_id: str):
    """Locate a field by identifier."""
    for candidate in fields:
        if candidate.field_id == field_id:
            return candidate
    return None


def _find_product(products, product_id: str):
    """Locate a fertilizer product by identifier."""
    for candidate in products:
        if candidate.product_id == product_id:
            return candidate
    return None


def _collect_manual_financials(
    result,
    request: ROIOptimizationRequest,
    optimizer: FertilizerROIOptimizer
):
    """
    Compute manual financial metrics from the optimization result.

    Args:
        result: OptimizationResult produced by the optimizer.
        request: Source optimization request.
        optimizer: Optimizer instance (used for yield response helper).

    Returns:
        Dictionary with revenue and cost totals.
    """
    totals = {"revenue": 0.0, "cost": 0.0}
    processed_pairs = {}

    for recommendation in result.nutrient_recommendations:
        for product_info in recommendation.product_recommendations:
            key = recommendation.field_id + "__" + product_info["product_id"]
            if key in processed_pairs:
                continue
            processed_pairs[key] = product_info["rate"]

            field_data = _find_field(request.fields, recommendation.field_id)
            product_data = _find_product(request.fertilizer_products, product_info["product_id"])

            assert field_data is not None
            assert product_data is not None

            rate_value = float(product_info["rate"])
            yield_response = optimizer._calculate_yield_response(field_data, product_data)
            revenue = rate_value * yield_response * field_data.crop_price * field_data.acres
            cost = rate_value * product_data.price_per_unit * field_data.acres

            totals["revenue"] += revenue
            totals["cost"] += cost

    return totals


@pytest.mark.asyncio
async def test_linear_programming_accuracy_matches_manual_calculation():
    """
    Ensure the linear programming solver matches manual financial metrics.
    """
    optimizer = FertilizerROIOptimizer()
    request = _build_accuracy_request()

    result = await optimizer._linear_programming_optimization(request)
    manual_totals = _collect_manual_financials(result, request, optimizer)

    assert manual_totals["revenue"] == pytest.approx(result.total_expected_revenue, rel=0.01)
    assert manual_totals["cost"] == pytest.approx(result.total_fertilizer_cost, rel=0.01)

    manual_profit = manual_totals["revenue"] - manual_totals["cost"]
    manual_roi = 0.0
    if manual_totals["cost"] > 0:
        manual_roi = manual_profit / manual_totals["cost"] * 100.0

    assert manual_roi >= 95.0
    assert result.roi_percentage == pytest.approx(manual_roi, rel=0.01)
    assert result.net_profit == pytest.approx(manual_profit, rel=0.01)


@pytest.mark.asyncio
async def test_optimize_roi_processing_time_within_target():
    """
    Validate end-to-end optimization runtime stays within performance target.
    """
    optimizer = FertilizerROIOptimizer()
    request = _build_performance_request(field_count=3, include_analysis=True)

    np.random.seed(42)
    start_time = time.perf_counter()
    response = await optimizer.optimize_fertilizer_roi(request)
    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    assert response.optimization_result.roi_percentage >= 95.0
    assert response.optimization_result.total_expected_revenue > response.optimization_result.total_fertilizer_cost
    assert response.processing_time_ms < 5000.0
    assert elapsed_ms < 5000.0
    assert response.processing_time_ms <= elapsed_ms + 1.0


@pytest.mark.asyncio
async def test_optimize_roi_concurrent_requests_consistent_results():
    """
    Ensure concurrent optimization requests remain consistent and performant.
    """
    optimizer = FertilizerROIOptimizer()
    request = _build_performance_request(field_count=2, include_analysis=False)

    np.random.seed(7)
    tasks = []
    total_requests = 5
    for _ in range(total_requests):
        task = optimizer.optimize_fertilizer_roi(request)
        tasks.append(task)

    start_time = time.perf_counter()
    responses = await asyncio.gather(*tasks)
    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    assert len(responses) == total_requests
    assert elapsed_ms < 6000.0

    baseline_roi = responses[0].optimization_result.roi_percentage
    for response in responses:
        assert response.processing_time_ms < 4000.0
        assert response.optimization_result.roi_percentage == pytest.approx(baseline_roi, rel=0.05)
        assert response.optimization_result.total_expected_revenue > response.optimization_result.total_fertilizer_cost

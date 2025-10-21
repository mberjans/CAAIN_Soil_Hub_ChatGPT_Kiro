import pytest
from src.services.economic_optimizer import EconomicOptimizer


def test_optimization_algorithm():
    """Test EconomicOptimizer can optimize fertilizer recommendations."""
    optimizer = EconomicOptimizer()
    
    # Sample field requirements (nutrients only)
    field_requirements = {
        "N": 150,
        "P": 60,
        "K": 40
    }
    
    # Sample available fertilizers (with cost_per_unit for optimizer)
    available_fertilizers = [
        {"name": "Urea 46-0-0", "cost_per_unit": 0.45, "nutrients": {"N": 46}},
        {"name": "DAP 18-46-0", "cost_per_unit": 0.55, "nutrients": {"P": 46, "N": 18}},
        {"name": "Potash 0-0-60", "cost_per_unit": 0.40, "nutrients": {"K": 60}}
    ]
    
    # Run optimization
    result = optimizer.optimize_fertilizer_strategy(
        field_requirements=field_requirements,
        available_fertilizers=available_fertilizers,
        budget_per_acre=200
    )
    
    # Verify result structure (dict of fertilizer names to amounts)
    assert isinstance(result, dict)
    assert len(result) > 0

    # Verify all recommendations are non-negative
    for fertilizer_name, amount in result.items():
        assert amount >= 0
        assert fertilizer_name in [f["name"] for f in available_fertilizers]

    # Verify budget constraint (total cost should be <= budget)
    total_cost = sum(amount * f.get('cost_per_unit', 0) for fertilizer_name, amount in result.items() for f in available_fertilizers if f["name"] == fertilizer_name)
    assert total_cost <= 200  # budget_per_acre

    # Verify nutrient requirements are met (with some tolerance)
    total_nutrients = {"N": 0, "P": 0, "K": 0}
    for fertilizer_name, amount in result.items():
        for f in available_fertilizers:
            if f["name"] == fertilizer_name:
                for nutrient, nutrient_amount in f["nutrients"].items():
                    total_nutrients[nutrient] += amount * nutrient_amount
                break

    assert total_nutrients["N"] >= 150 * 0.9  # 90% of requirement
    assert total_nutrients["P"] >= 60 * 0.9
    assert total_nutrients["K"] >= 40 * 0.9


def test_roi_calculation():
    """Test EconomicOptimizer can calculate ROI for fertilizer recommendations."""
    optimizer = EconomicOptimizer()
    
    # Sample fertilizer recommendations (dict format)
    recommendations = {
        "Urea 46-0-0": 200,  # lbs per acre
        "DAP 18-46-0": 150   # lbs per acre
    }
    
    # Sample field data (dict format)
    field_data = {
        "yield_bu_per_acre": 50,  # expected yield improvement (higher for positive ROI)
        "total_fertilizer_cost": 210.0  # total cost from recommendations
    }

    # Sample crop price
    crop_price_per_bu = 5.50

    # Calculate ROI
    roi = optimizer.calculate_roi(
        recommendations=recommendations,
        field_data=field_data,
        crop_price_per_bu=crop_price_per_bu
    )

    # Verify ROI calculation
    total_cost = 210.0  # from field_data
    expected_revenue_increase = 50 * 5.50  # yield_improvement * crop_price_per_bu
    expected_roi = (expected_revenue_increase - total_cost) / total_cost  # Decimal ROI, not percentage

    assert abs(roi - expected_roi) < 0.01  # Allow for small floating point differences
    assert roi > 0  # Should be positive ROI
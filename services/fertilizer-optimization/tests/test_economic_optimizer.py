import pytest
from src.services.economic_optimizer import EconomicOptimizer


def test_optimization_algorithm():
    """Test EconomicOptimizer can optimize fertilizer recommendations."""
    optimizer = EconomicOptimizer()
    
    # Sample field requirements
    field_requirements = {
        "field_acres": 100,
        "nutrient_requirements": {"N": 150, "P": 60, "K": 40},
        "yield_goal_bu_acre": 180
    }
    
    # Sample available fertilizers
    available_fertilizers = [
        {"name": "Urea 46-0-0", "price_per_ton": 450, "nutrients": {"N": 46}},
        {"name": "DAP 18-46-0", "price_per_ton": 550, "nutrients": {"P": 46, "N": 18}},
        {"name": "Potash 0-0-60", "price_per_ton": 400, "nutrients": {"K": 60}}
    ]
    
    # Run optimization
    result = optimizer.optimize_fertilizer_strategy(
        field_requirements=field_requirements,
        available_fertilizers=available_fertilizers,
        budget_per_acre=200
    )
    
    # Verify result structure
    assert "recommendations" in result
    assert "total_cost" in result
    assert "expected_yield" in result
    assert "roi" in result
    
    # Verify recommendations
    recommendations = result["recommendations"]
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0
    
    for rec in recommendations:
        assert "fertilizer_name" in rec
        assert "application_rate" in rec
        assert "cost" in rec
        assert "nutrients_provided" in rec
        assert rec["application_rate"] > 0
        assert rec["cost"] > 0
    
    # Verify budget constraint
    assert result["total_cost"] <= 200 * 100  # budget_per_acre * field_acres
    
    # Verify nutrient requirements are met (with some tolerance)
    total_nutrients = {"N": 0, "P": 0, "K": 0}
    for rec in recommendations:
        for nutrient, amount in rec["nutrients_provided"].items():
            total_nutrients[nutrient] += amount
    
    assert total_nutrients["N"] >= 150 * 0.9  # 90% of requirement
    assert total_nutrients["P"] >= 60 * 0.9
    assert total_nutrients["K"] >= 40 * 0.9


def test_roi_calculation():
    """Test EconomicOptimizer can calculate ROI for fertilizer recommendations."""
    optimizer = EconomicOptimizer()
    
    # Sample fertilizer recommendations
    recommendations = [
        {
            "fertilizer_name": "Urea 46-0-0",
            "application_rate": 200,  # lbs per acre
            "cost": 90.0,  # $ per acre
            "nutrients_provided": {"N": 92}
        },
        {
            "fertilizer_name": "DAP 18-46-0",
            "application_rate": 150,  # lbs per acre
            "cost": 120.0,  # $ per acre
            "nutrients_provided": {"P": 69, "N": 27}
        }
    ]
    
    # Sample field data
    field_data = {
        "field_acres": 100,
        "current_yield": 160,  # bu/acre
        "expected_yield_improvement": 20  # bu/acre
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
    total_cost = sum(rec["cost"] for rec in recommendations)
    expected_revenue_increase = field_data["expected_yield_improvement"] * crop_price_per_bu * field_data["field_acres"]
    expected_roi = (expected_revenue_increase - total_cost) / total_cost * 100
    
    assert abs(roi - expected_roi) < 0.01  # Allow for small floating point differences
    assert roi > 0  # Should be positive ROI
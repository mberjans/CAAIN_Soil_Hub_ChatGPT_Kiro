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
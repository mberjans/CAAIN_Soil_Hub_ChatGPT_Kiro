import pytest
from fastapi.testclient import TestClient
from src.main import app


def test_end_to_end_optimization():
    """Test complete end-to-end optimization workflow from request to response."""
    client = TestClient(app)

    # Complete optimization request
    request_data = {
        "field_acres": 100,
        "nutrient_requirements": {"N": 150, "P": 60, "K": 40},
        "yield_goal_bu_acre": 180,
        "available_fertilizers": [
            {"name": "Urea 46-0-0", "price_per_ton": 450, "nutrients": {"N": 46}},
            {"name": "DAP 18-46-0", "price_per_ton": 550, "nutrients": {"P": 46, "N": 18}},
            {"name": "Potash 0-0-60", "price_per_ton": 400, "nutrients": {"K": 60}}
        ],
        "budget_per_acre": 200,
        "crop_price_per_bu": 5.50
    }

    # Make optimization request
    response = client.post("/optimize", json=request_data)

    # Verify response
    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "recommendations" in data
    assert "total_cost" in data
    assert "expected_yield" in data
    assert "roi" in data

    # Verify recommendations are reasonable
    recommendations = data["recommendations"]
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0

    total_nutrients = {"N": 0, "P": 0, "K": 0}
    for rec in recommendations:
        assert "fertilizer_name" in rec
        assert "application_rate" in rec
        assert "cost" in rec
        assert "nutrients_applied" in rec

        # Verify application rates are reasonable (0-500 lbs/acre)
        assert 0 <= rec["application_rate"] <= 500

        # Verify costs are reasonable
        assert rec["cost"] >= 0

        # Accumulate nutrients for verification
        for nutrient, amount in rec["nutrients_applied"].items():
            total_nutrients[nutrient] += amount

    # Verify nutrient requirements are met (with tolerance)
    assert total_nutrients["N"] >= 150 * 0.9  # 90% of requirement
    assert total_nutrients["P"] >= 60 * 0.9
    assert total_nutrients["K"] >= 40 * 0.9

    # Verify budget constraint
    assert data["total_cost"] <= 200 * 100  # budget_per_acre * field_acres

    # Verify financial calculations
    assert data["expected_yield"] > 0
    assert isinstance(data["roi"], (int, float))
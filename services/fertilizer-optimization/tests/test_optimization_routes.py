import pytest
from fastapi.testclient import TestClient
from src.main import app


def test_optimize_fertilizer():
    """Test POST /optimize endpoint returns fertilizer optimization results."""
    client = TestClient(app)
    
    # Sample optimization request
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
    
    response = client.post("/optimize", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "recommendations" in data
    assert "total_cost" in data
    assert "expected_yield" in data
    assert "roi" in data
    
    # Verify recommendations
    recommendations = data["recommendations"]
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0
    
    for rec in recommendations:
        assert "fertilizer_name" in rec
        assert "application_rate" in rec
        assert "cost" in rec
        assert rec["application_rate"] > 0
        assert rec["cost"] > 0
    
    # Verify financial calculations
    assert data["total_cost"] > 0
    assert data["expected_yield"] > 0
    assert isinstance(data["roi"], (int, float))
import pytest
from datetime import datetime
from src.schemas.optimization_schemas import OptimizationRequest


def test_optimization_request_valid():
    """Test creating a valid OptimizationRequest instance."""
    request_data = {
        "field_acres": 100,
        "nutrient_requirements": {"N": 150, "P": 60, "K": 40},
        "yield_goal_bu_acre": 180,
        "available_fertilizers": [
            {"name": "Urea 46-0-0", "price_per_ton": 450, "nutrients": {"N": 46}},
            {"name": "DAP 18-46-0", "price_per_ton": 550, "nutrients": {"P": 46, "N": 18}}
        ]
    }
    
    request = OptimizationRequest(**request_data)
    
    assert request.field_acres == 100
    assert request.nutrient_requirements == {"N": 150, "P": 60, "K": 40}
    assert request.yield_goal_bu_acre == 180
    assert len(request.available_fertilizers) == 2
    assert request.available_fertilizers[0].name == "Urea 46-0-0"
    assert request.available_fertilizers[1].name == "DAP 18-46-0"
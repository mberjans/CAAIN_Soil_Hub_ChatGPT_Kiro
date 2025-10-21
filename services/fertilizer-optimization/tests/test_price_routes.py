import pytest
from fastapi.testclient import TestClient
from src.main import app

def test_get_fertilizer_current_prices():
    """Test GET /prices/fertilizer-current endpoint returns current fertilizer prices."""
    client = TestClient(app)
    response = client.get("/prices/fertilizer-current")
    assert response.status_code == 200
    data = response.json()
    assert "prices" in data
    assert isinstance(data["prices"], dict)
    assert len(data["prices"]) > 0  # Assuming at least one price entry
    for fertilizer_name, price_data in data["prices"].items():
        assert "fertilizer_name" in price_data
        assert "price" in price_data
        assert "date" in price_data
        assert "source" in price_data
        assert isinstance(price_data["price"], (int, float))
        assert price_data["price"] > 0
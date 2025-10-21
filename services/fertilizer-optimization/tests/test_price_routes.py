import pytest
from fastapi.testclient import TestClient
from services.fertilizer_application.main import app

def test_get_fertilizer_current_prices():
    """Test GET /prices/fertilizer-current endpoint returns current fertilizer prices."""
    client = TestClient(app)
    response = client.get("/prices/fertilizer-current")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0  # Assuming at least one price entry
    for item in data:
        assert "fertilizer_type" in item
        assert "price" in item
        assert "unit" in item
        assert isinstance(item["price"], (int, float))
        assert item["price"] > 0
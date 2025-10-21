import pytest
from fastapi.testclient import TestClient
from src.main import app


def test_health_endpoint():
    """Test the health endpoint returns 200 status."""
    client = TestClient(app)
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "fertilizer-optimization"}
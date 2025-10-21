import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test that the health endpoint returns correct response"""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "image-analysis"


def test_app_creation():
    """Test that FastAPI app is created correctly"""
    assert app.title == "Image Analysis Service"
    assert app.description == "Service for analyzing crop photos for nutrient deficiencies."
    assert app.version == "1.0.0"


def test_router_inclusion():
    """Test that image analysis router is included"""
    # Check if the router is included by checking if the routes are registered
    routes = [route.path for route in app.routes]
    # The health endpoint should be present
    assert "/health" in routes

import pytest
from fastapi.testclient import TestClient
from services.frontend.src.main import app

client = TestClient(app)

def test_fertilizer_selection_page():
    response = client.get("/fertilizer-selection")
    assert response.status_code == 200
    assert "<h1>Fertilizer Selection</h1>" in response.text

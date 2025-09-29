
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.main import app
from src.services.personalization_service import PersonalizationService

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def personalization_service():
    return PersonalizationService()

def test_personalization_service_instantiation(personalization_service):
    """Test that the PersonalizationService can be instantiated."""
    assert personalization_service is not None

@pytest.mark.asyncio
async def test_learn_user_preferences_endpoint(client):
    """Test the /personalization/learn endpoint."""
    response = client.post("/api/v1/personalization/learn?user_id=test_user", json={"farm_size": 100})
    assert response.status_code == 200
    assert response.json() == {"status": "preferences learned", "user_id": "test_user"}

@pytest.mark.asyncio
async def test_adapt_recommendations_endpoint(client):
    """Test the /personalization/adapt endpoint."""
    recommendations = [{"crop": "corn"}]
    preferences = {"risk_averse": True}
    response = client.post("/api/v1/personalization/adapt", json={"recommendations": recommendations, "user_preferences": preferences})
    assert response.status_code == 200
    assert response.json() == recommendations

@pytest.mark.asyncio
async def test_integrate_feedback_endpoint(client):
    """Test the /personalization/feedback endpoint."""
    feedback = {"recommendation_id": "123", "rating": 5}
    response = client.post("/api/v1/personalization/feedback", json=feedback)
    assert response.status_code == 200
    assert response.json() == {"status": "feedback integrated"}

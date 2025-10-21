import pytest
from services.micronutrient-management.src.services.micronutrient_recommendation_service import MicronutrientRecommendationService
from services.micronutrient-management.src.models.micronutrient_models import MicronutrientRecommendation

def test_get_recommendations():
    service = MicronutrientRecommendationService()
    recommendations = service.get_recommendations()

    assert isinstance(recommendations, list)
    assert len(recommendations) > 0
    assert isinstance(recommendations[0], MicronutrientRecommendation)
    assert recommendations[0].nutrient == "Boron"

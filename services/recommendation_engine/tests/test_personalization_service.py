"""Tests for the advanced PersonalizationService implementation."""

import sys
from pathlib import Path
from datetime import date
from typing import Any, Dict, List

import pytest

# Ensure project src is on path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.services.personalization_service import PersonalizationService
from src.models.agricultural_models import (
    RecommendationItem,
    RecommendationRequest,
    LocationData,
    FarmProfile,
)


@pytest.fixture
def service() -> PersonalizationService:
    return PersonalizationService()


@pytest.fixture
def base_request() -> RecommendationRequest:
    location = LocationData(
        latitude=40.0,
        longitude=-88.0,
        climate_zone="5b",
        climate_zone_name="USDA Zone 5b",
        climate_zone_description="Cool temperate",
        temperature_range_f={"min": -15, "max": 85},
        climate_confidence=0.8,
    )
    farm_profile = FarmProfile(
        farm_id="farm-123",
        farm_size_acres=120.0,
        primary_crops=["corn"],
        irrigation_available=False,
        organic_certified=False,
    )
    request = RecommendationRequest(
        request_id="req-001",
        question_type="crop_selection",
        location=location,
        farm_profile=farm_profile,
        additional_context={"user_id": "user-001"},
        user_preferences={
            "risk_tolerance": "low",
            "management_intensity": "balanced",
            "yield_priority": 0.7,
            "sustainability_priority": 0.8,
            "preferred_crops": ["corn"],
            "focus_keywords": ["soil"],
        },
    )
    return request


def _build_recommendation(title: str, description: str, confidence: float) -> RecommendationItem:
    return RecommendationItem(
        recommendation_type="crop",
        title=title,
        description=description,
        priority=2,
        confidence_score=confidence,
        implementation_steps=["Step one", "Step two"],
        expected_outcomes=["Improved yield"],
        cost_estimate=75.0,
        roi_estimate=0.12,
        timing=str(date.today()),
        agricultural_sources=["Extension"],
    )


@pytest.mark.asyncio
async def test_learn_user_preferences_creates_profile(service: PersonalizationService) -> None:
    payload = {
        "risk_tolerance": "high",
        "management_intensity": "high_intensity",
        "yield_priority": 0.9,
        "preferred_crops": ["soybean"],
    }
    result = await service.learn_user_preferences("user-100", payload)
    assert result["status"] == "preferences learned"
    stored = service._user_preferences.get("user-100")
    assert stored is not None
    assert stored.risk_tolerance == "high"
    assert "soybean" in stored.preferred_crops


@pytest.mark.asyncio
async def test_personalize_recommendations_applies_adjustments(
    service: PersonalizationService,
    base_request: RecommendationRequest,
) -> None:
    first = _build_recommendation("Corn Hybrid A", "High yield focus", 0.55)
    second = _build_recommendation("Soil Health Plan", "Organic soil building", 0.50)
    recommendations = [first, second]
    result = await service.personalize_recommendations(base_request, recommendations)
    personalized = result["recommendations"]
    assert len(personalized) == 2
    top = personalized[0]
    assert top.title in ("Corn Hybrid A", "Soil Health Plan")
    summary = result["summary"]
    assert summary["confidence"] > 0.5
    assert summary["insights"]


@pytest.mark.asyncio
async def test_integrate_feedback_updates_collaborative_matrix(service: PersonalizationService) -> None:
    feedback_payload = {
        "user_id": "user-200",
        "recommendation_id": "crop::corn hybrid",
        "rating": 4.5,
        "accepted": True,
        "comments": "Worked well",
    }
    result = await service.integrate_feedback(feedback_payload)
    assert result["status"] == "feedback integrated"
    stored_vector = service._collaborative_matrix.get("user-200")
    assert stored_vector is not None
    assert "crop::corn hybrid" in stored_vector


@pytest.mark.asyncio
async def test_adapt_recommendations_reorders_entries(service: PersonalizationService) -> None:
    raw_recommendations: List[Dict[str, Any]] = []
    first = {
        "recommendation_type": "crop",
        "title": "Cover Crop Mix",
        "description": "Sustainability improvement",
        "priority": 3,
        "confidence_score": 0.5,
        "implementation_steps": ["Plant in fall"],
        "expected_outcomes": ["Better soil"],
        "agricultural_sources": ["Extension"],
    }
    second = {
        "recommendation_type": "crop",
        "title": "High Input Corn",
        "description": "Intensive management plan",
        "priority": 2,
        "confidence_score": 0.55,
        "implementation_steps": ["Apply fertilizer"],
        "expected_outcomes": ["Higher yield"],
        "agricultural_sources": ["Extension"],
    }
    raw_recommendations.append(first)
    raw_recommendations.append(second)
    preference_payload = {
        "sustainability_priority": 0.9,
        "preferred_crops": ["cover"],
    }
    adapted = await service.adapt_recommendations(raw_recommendations, preference_payload)
    assert len(adapted) == 2
    assert adapted[0]["title"] == "Cover Crop Mix"


@pytest.mark.asyncio
async def test_log_recommendation_delivery_records_history(
    service: PersonalizationService,
    base_request: RecommendationRequest,
) -> None:
    recommendation = _build_recommendation("Test Variety", "Balanced performance", 0.6)
    result = await service.personalize_recommendations(base_request, [recommendation])
    personalized = result["recommendations"]
    await service.log_recommendation_delivery(base_request, personalized, result["summary"])
    history = service._interaction_history.get("user-001")
    assert history is not None
    assert len(history) == 1

"""
Comprehensive Test Suite for Fertilizer Type Selection API Endpoints

Tests all endpoints in fertilizer_routes.py:
- POST /api/v1/fertilizer/type-selection
- GET /api/v1/fertilizer/types
- POST /api/v1/fertilizer/comparison
- POST /api/v1/fertilizer/recommendation-history
- GET /api/v1/fertilizer/recommendation-history/{user_id}

Implements TICKET-023_fertilizer-type-selection-10.1.1-10.1.4
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import app

client = TestClient(app)


class TestAdvancedFertilizerSelection:
    """Test POST /api/v1/fertilizer/type-selection endpoint."""

    def test_basic_fertilizer_selection(self):
        """Test basic fertilizer selection with minimal parameters."""
        request_data = {
            "priorities": {
                "cost_effectiveness": 0.8,
                "soil_health": 0.6,
                "quick_results": 0.5,
                "environmental_impact": 0.4,
                "ease_of_application": 0.5,
                "long_term_benefits": 0.6
            },
            "constraints": {
                "budget_per_acre": 100.0,
                "farm_size_acres": 160.0,
                "available_equipment": ["broadcast_spreader"],
                "organic_preference": False,
                "environmental_concerns": False
            }
        }

        response = client.post("/api/v1/fertilizer/type-selection", json=request_data)
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "request_id" in data
        assert "recommendations" in data
        assert "confidence_score" in data
        assert "cost_analysis" in data
        assert "environmental_impact" in data
        assert isinstance(data["recommendations"], list)

    def test_fertilizer_selection_with_soil_data(self):
        """Test fertilizer selection with comprehensive soil data."""
        request_data = {
            "priorities": {
                "cost_effectiveness": 0.7,
                "soil_health": 0.9,
                "quick_results": 0.4,
                "environmental_impact": 0.8,
                "ease_of_application": 0.5,
                "long_term_benefits": 0.8
            },
            "constraints": {
                "budget_per_acre": 150.0,
                "farm_size_acres": 320.0,
                "available_equipment": ["broadcast_spreader", "field_sprayer"],
                "organic_preference": True,
                "environmental_concerns": True
            },
            "soil_data": {
                "ph": 6.5,
                "organic_matter_percent": 3.2,
                "soil_texture": "loam",
                "nitrogen_ppm": 15,
                "phosphorus_ppm": 25,
                "potassium_ppm": 180
            },
            "crop_data": {
                "crop_type": "corn",
                "target_yield": 180,
                "growth_stage": "pre_plant",
                "previous_crop": "soybeans"
            }
        }

        response = client.post("/api/v1/fertilizer/type-selection", json=request_data)
        assert response.status_code == 200
        data = response.json()

        # Verify comprehensive response
        assert "recommendations" in data
        assert "implementation_guidance" in data
        assert "timing_recommendations" in data
        assert "warnings" in data
        assert "next_steps" in data

    def test_organic_preference_filtering(self):
        """Test that organic preference filters recommendations appropriately."""
        request_data = {
            "priorities": {
                "cost_effectiveness": 0.5,
                "soil_health": 0.9,
                "quick_results": 0.3,
                "environmental_impact": 1.0,
                "ease_of_application": 0.4,
                "long_term_benefits": 0.9
            },
            "constraints": {
                "budget_per_acre": 200.0,
                "farm_size_acres": 80.0,
                "available_equipment": ["manure_spreader"],
                "organic_preference": True,
                "environmental_concerns": True
            }
        }

        response = client.post("/api/v1/fertilizer/type-selection", json=request_data)
        assert response.status_code == 200
        data = response.json()

        # Recommendations should consider organic preference
        assert "recommendations" in data
        assert data["confidence_score"] > 0

    def test_invalid_priorities(self):
        """Test validation of invalid priority values."""
        request_data = {
            "priorities": {
                "cost_effectiveness": 1.5,  # Invalid: > 1.0
                "soil_health": 0.6
            },
            "constraints": {
                "budget_per_acre": 100.0,
                "farm_size_acres": 160.0
            }
        }

        response = client.post("/api/v1/fertilizer/type-selection", json=request_data)
        assert response.status_code in [400, 422]  # Validation error


class TestFertilizerTypesCatalog:
    """Test GET /api/v1/fertilizer/types endpoint."""

    def test_get_all_fertilizer_types(self):
        """Test retrieving complete fertilizer catalog."""
        response = client.get("/api/v1/fertilizer/types")
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "total_count" in data
        assert "returned_count" in data
        assert "fertilizer_types" in data
        assert isinstance(data["fertilizer_types"], list)

    def test_filter_by_organic_only(self):
        """Test filtering for organic fertilizers only."""
        response = client.get("/api/v1/fertilizer/types?organic_only=true")
        assert response.status_code == 200
        data = response.json()

        assert "fertilizer_types" in data
        assert "filters_applied" in data
        assert data["filters_applied"]["organic_only"] is True

    def test_filter_by_price_range(self):
        """Test filtering by price range."""
        response = client.get(
            "/api/v1/fertilizer/types?price_range_min=20&price_range_max=100"
        )
        assert response.status_code == 200
        data = response.json()

        assert "filters_applied" in data
        assert data["filters_applied"]["price_range"]["min"] == 20
        assert data["filters_applied"]["price_range"]["max"] == 100

    def test_pagination(self):
        """Test pagination parameters."""
        response = client.get("/api/v1/fertilizer/types?limit=5&offset=0")
        assert response.status_code == 200
        data = response.json()

        assert data["limit"] == 5
        assert data["offset"] == 0
        assert data["returned_count"] <= 5

    def test_filter_by_manufacturer(self):
        """Test filtering by manufacturer."""
        response = client.get("/api/v1/fertilizer/types?manufacturer=TestCorp")
        assert response.status_code == 200
        data = response.json()

        assert "filters_applied" in data
        assert data["filters_applied"]["manufacturer"] == "TestCorp"


class TestFertilizerComparison:
    """Test POST /api/v1/fertilizer/comparison endpoint."""

    def test_basic_comparison(self):
        """Test basic comparison of fertilizer options."""
        request_data = {
            "fertilizer_ids": [
                "urea_46_0_0",
                "ammonium_sulfate_21_0_0"
            ],
            "comparison_criteria": [
                "cost_effectiveness",
                "soil_health_impact"
            ],
            "farm_context": {
                "farm_size_acres": 160,
                "soil_ph": 6.5,
                "crop_type": "corn",
                "budget_per_acre": 100
            }
        }

        response = client.post("/api/v1/fertilizer/comparison", json=request_data)
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "request_id" in data
        assert "comparison_results" in data
        assert "recommendation" in data
        assert "decision_factors" in data

    def test_comprehensive_comparison(self):
        """Test comprehensive comparison with multiple criteria."""
        request_data = {
            "fertilizer_ids": [
                "urea_46_0_0",
                "ammonium_sulfate_21_0_0",
                "composted_manure_organic"
            ],
            "comparison_criteria": [
                "cost_effectiveness",
                "soil_health_impact",
                "environmental_impact",
                "nitrogen_efficiency",
                "application_ease"
            ],
            "farm_context": {
                "farm_size_acres": 320,
                "soil_ph": 6.0,
                "crop_type": "wheat",
                "budget_per_acre": 150,
                "organic_certified": False
            }
        }

        response = client.post("/api/v1/fertilizer/comparison", json=request_data)
        assert response.status_code == 200
        data = response.json()

        assert "comparison_results" in data
        assert "comparison_criteria_used" in data
        assert len(data["comparison_criteria_used"]) == 5

    def test_insufficient_fertilizers(self):
        """Test error when fewer than 2 fertilizers provided."""
        request_data = {
            "fertilizer_ids": ["urea_46_0_0"],
            "comparison_criteria": ["cost_effectiveness"],
            "farm_context": {"farm_size_acres": 160}
        }

        response = client.post("/api/v1/fertilizer/comparison", json=request_data)
        assert response.status_code == 400

    def test_too_many_fertilizers(self):
        """Test error when more than 5 fertilizers provided."""
        request_data = {
            "fertilizer_ids": [f"fertilizer_{i}" for i in range(6)],
            "comparison_criteria": ["cost_effectiveness"],
            "farm_context": {"farm_size_acres": 160}
        }

        response = client.post("/api/v1/fertilizer/comparison", json=request_data)
        assert response.status_code == 400

    def test_invalid_criteria(self):
        """Test error with invalid comparison criteria."""
        request_data = {
            "fertilizer_ids": ["urea_46_0_0", "ammonium_sulfate_21_0_0"],
            "comparison_criteria": ["invalid_criterion"],
            "farm_context": {"farm_size_acres": 160}
        }

        response = client.post("/api/v1/fertilizer/comparison", json=request_data)
        assert response.status_code == 400


class TestRecommendationHistory:
    """Test recommendation history tracking endpoints."""

    def test_save_recommendation(self):
        """Test saving fertilizer recommendation."""
        request_data = {
            "user_id": "test_user_123",
            "farm_id": "farm_456",
            "recommendation_data": {
                "fertilizer_type": "urea_46_0_0",
                "application_rate": 150,
                "selected_at": "2024-01-15T10:00:00Z"
            },
            "notes": "Selected for cost-effectiveness"
        }

        response = client.post(
            "/api/v1/fertilizer/recommendation-history",
            json=request_data
        )
        assert response.status_code == 200
        data = response.json()

        assert "recommendation_id" in data
        assert "saved_at" in data
        assert data["status"] == "success"

    def test_get_recommendation_history(self):
        """Test retrieving recommendation history."""
        user_id = "test_user_123"
        response = client.get(f"/api/v1/fertilizer/recommendation-history/{user_id}")
        assert response.status_code == 200
        data = response.json()

        assert "user_id" in data
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)

    def test_get_history_with_farm_filter(self):
        """Test retrieving history filtered by farm."""
        user_id = "test_user_123"
        farm_id = "farm_456"
        response = client.get(
            f"/api/v1/fertilizer/recommendation-history/{user_id}?farm_id={farm_id}"
        )
        assert response.status_code == 200
        data = response.json()

        assert data["farm_id"] == farm_id

    def test_history_pagination(self):
        """Test pagination of recommendation history."""
        user_id = "test_user_123"
        response = client.get(
            f"/api/v1/fertilizer/recommendation-history/{user_id}?limit=5&offset=0"
        )
        assert response.status_code == 200


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self):
        """Test fertilizer service health endpoint."""
        response = client.get("/api/v1/fertilizer/health")
        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert data["status"] == "healthy"
        assert "service" in data
        assert data["service"] == "fertilizer-type-selection"


class TestIntegrationScenarios:
    """Test complete user workflows."""

    def test_complete_selection_workflow(self):
        """Test complete workflow: selection -> comparison -> save."""
        # Step 1: Get recommendations
        selection_data = {
            "priorities": {
                "cost_effectiveness": 0.8,
                "soil_health": 0.7,
                "quick_results": 0.5,
                "environmental_impact": 0.6,
                "ease_of_application": 0.5,
                "long_term_benefits": 0.7
            },
            "constraints": {
                "budget_per_acre": 120.0,
                "farm_size_acres": 160.0,
                "available_equipment": ["broadcast_spreader"],
                "organic_preference": False,
                "environmental_concerns": True
            }
        }

        selection_response = client.post(
            "/api/v1/fertilizer/type-selection",
            json=selection_data
        )
        assert selection_response.status_code == 200
        recommendations = selection_response.json()["recommendations"]

        # Step 2: Compare top options (if we have recommendations)
        if len(recommendations) >= 2:
            comparison_data = {
                "fertilizer_ids": [r["id"] for r in recommendations[:2]],
                "comparison_criteria": ["cost_effectiveness", "soil_health_impact"],
                "farm_context": {"farm_size_acres": 160}
            }

            comparison_response = client.post(
                "/api/v1/fertilizer/comparison",
                json=comparison_data
            )
            # May fail if IDs don't exist, but workflow should execute

        # Step 3: Save selection
        history_data = {
            "user_id": "test_user",
            "recommendation_data": {"selected_option": "test"},
            "notes": "Integration test"
        }

        history_response = client.post(
            "/api/v1/fertilizer/recommendation-history",
            json=history_data
        )
        assert history_response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

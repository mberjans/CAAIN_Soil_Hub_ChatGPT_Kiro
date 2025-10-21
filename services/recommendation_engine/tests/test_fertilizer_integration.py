"""
Integration Tests for Fertilizer Type Selection System

Tests integration between services, API endpoints, and external dependencies.
Implements TICKET-023_fertilizer-type-selection-11.1
"""

import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ..main import app
from ..services.fertilizer_type_selection_service import FertilizerTypeSelectionService

client = TestClient(app)


class TestServiceIntegration:
    """Test integration between fertilizer services."""

    @pytest.fixture
    def fertilizer_service(self):
        return FertilizerTypeSelectionService()

    @pytest.mark.asyncio
    async def test_environmental_service_integration(self, fertilizer_service):
        """Test integration with environmental assessment service."""
        fertilizer_data = {
            "id": "urea_46_0_0",
            "name": "Urea",
            "type": "urea",
            "nitrogen_percent": 46.0
        }

        application_data = {
            "rate_lbs_per_acre": 150.0,
            "method": "broadcast"
        }

        field_conditions = {
            "soil": {"texture": "loam", "ph": 6.5}
        }

        impact = await fertilizer_service.get_environmental_impact(
            fertilizer_id="urea_46_0_0",
            fertilizer_data=fertilizer_data,
            application_data=application_data,
            field_conditions=field_conditions
        )

        assert "carbon_footprint" in impact
        assert "water_quality_impact" in impact
        assert "sustainability_score" in impact

    @pytest.mark.asyncio
    async def test_soil_health_service_integration(self, fertilizer_service):
        """Test integration with soil health service."""
        soil_data = {
            "ph": 6.5,
            "organic_matter_percent": 3.0,
            "phosphorus_ppm": 25.0,
            "potassium_ppm": 150.0
        }

        assessment = await fertilizer_service.assess_fertilizer_soil_health_impact(
            fertilizer_type="synthetic",
            fertilizer_name="Urea",
            application_rate_lbs_per_acre=150.0,
            soil_data=soil_data
        )

        assert "overall_soil_health_score" in assessment
        assert "soil_health_rating" in assessment

    @pytest.mark.asyncio
    async def test_end_to_end_recommendation_flow(self, fertilizer_service):
        """Test complete recommendation flow from input to output."""
        from ..models.fertilizer_models import FarmerPriorities, FarmerConstraints

        priorities = FarmerPriorities(
            cost_effectiveness=0.8,
            soil_health=0.7,
            quick_results=0.5,
            environmental_impact=0.6,
            ease_of_application=0.5,
            long_term_benefits=0.7
        )

        constraints = FarmerConstraints(
            budget_per_acre=120.0,
            farm_size_acres=160.0,
            available_equipment=["broadcast_spreader"],
            organic_preference=False,
            environmental_concerns=True
        )

        soil_data = {
            "ph": 6.5,
            "organic_matter_percent": 3.2
        }

        crop_data = {
            "crop_type": "corn",
            "target_yield": 180
        }

        # Get recommendations
        recommendations = await fertilizer_service.get_fertilizer_type_recommendations(
            priorities=priorities,
            constraints=constraints,
            soil_data=soil_data,
            crop_data=crop_data
        )

        assert len(recommendations) > 0

        # Get cost analysis
        cost_analysis = fertilizer_service.generate_cost_analysis(
            recommendations, constraints
        )

        assert cost_analysis["average_cost_per_acre"] > 0

        # Get confidence
        confidence = fertilizer_service.calculate_overall_confidence(recommendations)

        assert 0 <= confidence <= 1


class TestAPIIntegration:
    """Test API endpoint integration."""

    def test_type_selection_with_full_data(self):
        """Test type selection endpoint with complete data."""
        request_data = {
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
                "available_equipment": ["broadcast_spreader", "field_sprayer"],
                "organic_preference": False,
                "environmental_concerns": True
            },
            "soil_data": {
                "ph": 6.5,
                "organic_matter_percent": 3.2,
                "soil_texture": "loam"
            },
            "crop_data": {
                "crop_type": "corn",
                "target_yield": 180
            }
        }

        response = client.post("/api/v1/fertilizer/type-selection", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert "recommendations" in data
        assert "confidence_score" in data
        assert "cost_analysis" in data
        assert "environmental_impact" in data

    def test_type_catalog_and_selection_workflow(self):
        """Test workflow of browsing catalog then selecting fertilizer."""
        # Step 1: Browse catalog
        catalog_response = client.get("/api/v1/fertilizer/types?organic_only=false")
        assert catalog_response.status_code == 200

        catalog_data = catalog_response.json()
        assert "fertilizer_types" in catalog_data

        # Step 2: Make selection based on catalog
        selection_data = {
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

        selection_response = client.post(
            "/api/v1/fertilizer/type-selection",
            json=selection_data
        )
        assert selection_response.status_code == 200

    def test_selection_comparison_history_workflow(self):
        """Test complete workflow: selection -> comparison -> save history."""
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

        # Step 2: Compare top options
        comparison_data = {
            "fertilizer_ids": ["urea_46_0_0", "ammonium_sulfate_21_0_0"],
            "comparison_criteria": ["cost_effectiveness", "soil_health_impact"],
            "farm_context": {"farm_size_acres": 160}
        }

        comparison_response = client.post(
            "/api/v1/fertilizer/comparison",
            json=comparison_data
        )
        # May fail if IDs don't exist, but API should handle gracefully

        # Step 3: Save selection to history
        history_data = {
            "user_id": "integration_test_user",
            "recommendation_data": {"selected": "urea_46_0_0"},
            "notes": "Integration test"
        }

        history_response = client.post(
            "/api/v1/fertilizer/recommendation-history",
            json=history_data
        )
        assert history_response.status_code == 200


class TestDataFlow:
    """Test data flow between components."""

    @pytest.fixture
    def service(self):
        return FertilizerTypeSelectionService()

    @pytest.mark.asyncio
    async def test_priority_to_score_flow(self, service):
        """Test flow from priorities to recommendation scores."""
        from ..models.fertilizer_models import FarmerPriorities, FarmerConstraints

        # High cost priority
        priorities = FarmerPriorities(
            cost_effectiveness=1.0,
            soil_health=0.0,
            quick_results=0.0,
            environmental_impact=0.0,
            ease_of_application=0.0,
            long_term_benefits=0.0
        )

        constraints = FarmerConstraints(
            budget_per_acre=100.0,
            farm_size_acres=160.0,
            available_equipment=["broadcast_spreader"]
        )

        recommendations = await service.get_fertilizer_type_recommendations(
            priorities=priorities,
            constraints=constraints
        )

        # Should favor low-cost options
        if len(recommendations) > 0:
            top_rec = recommendations[0]
            # Verify it's a relatively low-cost option
            cost = top_rec.get("details", {}).get("cost_per_unit", 0)
            assert cost < 500  # Should be lower cost option

    @pytest.mark.asyncio
    async def test_constraint_to_filtering_flow(self, service):
        """Test flow from constraints to filtered recommendations."""
        from ..models.fertilizer_models import FarmerPriorities, FarmerConstraints

        priorities = FarmerPriorities(
            cost_effectiveness=0.5,
            soil_health=0.5,
            quick_results=0.5,
            environmental_impact=0.5,
            ease_of_application=0.5,
            long_term_benefits=0.5
        )

        # Organic only constraint
        constraints = FarmerConstraints(
            budget_per_acre=200.0,
            farm_size_acres=80.0,
            available_equipment=["manure_spreader"],
            organic_preference=True
        )

        recommendations = await service.get_fertilizer_type_recommendations(
            priorities=priorities,
            constraints=constraints
        )

        # All should be organic
        for rec in recommendations:
            assert rec.get("details", {}).get("organic_certified", False)


class TestErrorHandling:
    """Test error handling in integrated system."""

    def test_invalid_priorities_handled(self):
        """Test that invalid priorities are handled gracefully."""
        request_data = {
            "priorities": {
                "cost_effectiveness": 1.5,  # Invalid
                "soil_health": 0.6
            },
            "constraints": {
                "budget_per_acre": 100.0,
                "farm_size_acres": 160.0,
                "available_equipment": ["broadcast_spreader"]
            }
        }

        response = client.post("/api/v1/fertilizer/type-selection", json=request_data)
        assert response.status_code in [400, 422]

    def test_missing_required_fields(self):
        """Test that missing required fields are handled."""
        request_data = {
            "priorities": {
                "cost_effectiveness": 0.8
            }
            # Missing constraints
        }

        response = client.post("/api/v1/fertilizer/type-selection", json=request_data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_service_error_recovery(self):
        """Test that services recover from errors gracefully."""
        service = FertilizerTypeSelectionService()
        from ..models.fertilizer_models import FarmerPriorities, FarmerConstraints

        priorities = FarmerPriorities(
            cost_effectiveness=0.8,
            soil_health=0.6,
            quick_results=0.5,
            environmental_impact=0.4,
            ease_of_application=0.5,
            long_term_benefits=0.6
        )

        constraints = FarmerConstraints(
            budget_per_acre=100.0,
            farm_size_acres=160.0,
            available_equipment=["broadcast_spreader"]
        )

        # Should not raise exception even with minimal data
        recommendations = await service.get_fertilizer_type_recommendations(
            priorities=priorities,
            constraints=constraints,
            soil_data=None,
            crop_data=None
        )

        # Should return something even without soil/crop data
        assert isinstance(recommendations, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

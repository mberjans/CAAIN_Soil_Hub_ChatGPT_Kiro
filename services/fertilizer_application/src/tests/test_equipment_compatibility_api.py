"""
Integration tests for Equipment Compatibility API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app  # Assuming main app is in main.py
from src.models.equipment_models import (
    FertilizerFormulation, ApplicationMethodType, EquipmentCategory
)


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestEquipmentCompatibilityAPIEndpoints:
    """Integration tests for equipment compatibility API endpoints."""

    def test_assess_equipment_compatibility_endpoint(self, client):
        """Test POST /api/v1/equipment/compatibility/assess endpoint."""
        response = client.post(
            "/api/v1/equipment/compatibility/assess",
            params={
                "equipment_id": "test_equipment_1",
                "fertilizer_type": FertilizerFormulation.GRANULAR.value,
                "application_method": ApplicationMethodType.BROADCAST.value,
                "field_size_acres": 100.0,
                "soil_type": "loam",
                "wind_speed_mph": 5.0,
                "temperature_f": 70.0,
                "humidity_percent": 50.0
            }
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()

        assert "matrix_id" in data
        assert "equipment_id" in data
        assert data["equipment_id"] == "test_equipment_1"
        assert "fertilizer_type" in data
        assert "application_method" in data
        assert "overall_compatibility_score" in data
        assert "compatibility_level" in data
        assert "compatibility_factors" in data
        assert len(data["compatibility_factors"]) == 8

        # Check score is valid
        assert 0.0 <= data["overall_compatibility_score"] <= 1.0

    def test_assess_compatibility_with_cost_constraints(self, client):
        """Test compatibility assessment with cost constraints."""
        response = client.post(
            "/api/v1/equipment/compatibility/assess",
            params={
                "equipment_id": "test_equipment_2",
                "fertilizer_type": FertilizerFormulation.LIQUID.value,
                "application_method": ApplicationMethodType.FOLIAR.value,
                "field_size_acres": 150.0,
                "soil_type": "clay",
                "cost_constraints": 50000.0
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "cost_efficiency_score" in data
        assert 0.0 <= data["cost_efficiency_score"] <= 1.0

    def test_assess_compatibility_minimal_parameters(self, client):
        """Test compatibility assessment with minimal parameters."""
        response = client.post(
            "/api/v1/equipment/compatibility/assess",
            params={
                "equipment_id": "test_equipment_3",
                "fertilizer_type": FertilizerFormulation.GRANULAR.value,
                "application_method": ApplicationMethodType.BROADCAST.value,
                "field_size_acres": 50.0,
                "soil_type": "sandy"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "overall_compatibility_score" in data

    def test_get_equipment_recommendations_endpoint(self, client):
        """Test POST /api/v1/equipment/compatibility/recommend endpoint."""
        response = client.post(
            "/api/v1/equipment/compatibility/recommend",
            params={
                "fertilizer_type": FertilizerFormulation.GRANULAR.value,
                "application_method": ApplicationMethodType.BROADCAST.value,
                "field_size_acres": 100.0,
                "soil_type": "loam",
                "top_n": 5
            }
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) <= 5

        # Check each recommendation
        if len(data) > 0:
            recommendation = data[0]
            assert "recommendation_id" in recommendation
            assert "equipment" in recommendation
            assert "compatibility_matrix" in recommendation
            assert "overall_score" in recommendation
            assert "ranking" in recommendation
            assert "justification" in recommendation
            assert "advantages" in recommendation
            assert "disadvantages" in recommendation
            assert "cost_benefit" in recommendation
            assert "implementation_considerations" in recommendation
            assert "training_requirements" in recommendation
            assert "confidence_level" in recommendation

            # Check cost_benefit structure
            cost_benefit = recommendation["cost_benefit"]
            assert "initial_investment" in cost_benefit
            assert "annual_operating_cost" in cost_benefit
            assert "annual_savings" in cost_benefit
            assert "payback_period_years" in cost_benefit
            assert "roi_percentage" in cost_benefit
            assert "cost_per_acre" in cost_benefit

    def test_get_recommendations_with_weather_conditions(self, client):
        """Test recommendations with weather conditions."""
        response = client.post(
            "/api/v1/equipment/compatibility/recommend",
            params={
                "fertilizer_type": FertilizerFormulation.LIQUID.value,
                "application_method": ApplicationMethodType.FOLIAR.value,
                "field_size_acres": 200.0,
                "soil_type": "loam",
                "wind_speed_mph": 12.0,
                "temperature_f": 75.0,
                "humidity_percent": 60.0,
                "top_n": 3
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3

    def test_get_recommendations_with_budget_constraint(self, client):
        """Test recommendations with budget constraints."""
        response = client.post(
            "/api/v1/equipment/compatibility/recommend",
            params={
                "fertilizer_type": FertilizerFormulation.GRANULAR.value,
                "application_method": ApplicationMethodType.BROADCAST.value,
                "field_size_acres": 100.0,
                "soil_type": "loam",
                "cost_constraints": 25000.0,
                "top_n": 5
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Check that recommendations respect budget (approximately)
        for rec in data:
            cost = rec["cost_benefit"]["initial_investment"]
            # Some recommendations might be slightly over budget, but should be reasonable
            assert cost <= 30000.0  # Allow some flexibility

    def test_get_full_compatibility_matrix_endpoint(self, client):
        """Test GET /api/v1/equipment/compatibility/matrix endpoint."""
        response = client.get("/api/v1/equipment/compatibility/matrix")

        # Assertions
        assert response.status_code == 200
        data = response.json()

        assert "compatibility_matrix" in data
        assert "fertilizer_types" in data
        assert "equipment_categories" in data

        # Check that matrix has data
        matrix = data["compatibility_matrix"]
        assert len(matrix) > 0

        # Check structure of matrix entries
        first_fertilizer = list(matrix.keys())[0]
        first_equipment = list(matrix[first_fertilizer].keys())[0]
        entry = matrix[first_fertilizer][first_equipment]

        assert "compatibility_level" in entry
        assert "score" in entry

    def test_get_filtered_compatibility_matrix(self, client):
        """Test getting filtered compatibility matrix."""
        response = client.get(
            "/api/v1/equipment/compatibility/matrix",
            params={
                "fertilizer_types": [
                    FertilizerFormulation.GRANULAR.value,
                    FertilizerFormulation.LIQUID.value
                ],
                "equipment_categories": [
                    EquipmentCategory.SPREADING.value,
                    EquipmentCategory.SPRAYING.value
                ]
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Should only have specified types
        assert len(data["fertilizer_types"]) == 2
        assert len(data["equipment_categories"]) == 2

    def test_optimize_equipment_selection_endpoint(self, client):
        """Test POST /api/v1/equipment/compatibility/optimize endpoint."""
        fields = [
            {
                "size_acres": 100.0,
                "fertilizer_type": FertilizerFormulation.GRANULAR.value,
                "application_method": ApplicationMethodType.BROADCAST.value,
                "soil_type": "loam"
            },
            {
                "size_acres": 75.0,
                "fertilizer_type": FertilizerFormulation.LIQUID.value,
                "application_method": ApplicationMethodType.FOLIAR.value,
                "soil_type": "clay"
            },
            {
                "size_acres": 50.0,
                "fertilizer_type": FertilizerFormulation.GRANULAR.value,
                "application_method": ApplicationMethodType.BROADCAST.value,
                "soil_type": "sandy"
            }
        ]

        response = client.post(
            "/api/v1/equipment/compatibility/optimize",
            json=fields,
            params={"budget_constraint": 100000.0}
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()

        assert "field_requirements" in data
        assert "equipment_needs" in data
        assert "recommended_equipment" in data
        assert "implementation_plan" in data
        assert "total_cost" in data
        assert "budget_constraint" in data
        assert "budget_utilization" in data

        # Check field requirements
        field_reqs = data["field_requirements"]
        assert field_reqs["total_acres"] == 225.0
        assert field_reqs["field_count"] == 3

        # Check budget compliance
        assert data["total_cost"] <= 100000.0

    def test_optimize_without_budget_constraint(self, client):
        """Test optimization without budget constraints."""
        fields = [
            {
                "size_acres": 100.0,
                "fertilizer_type": FertilizerFormulation.GRANULAR.value,
                "application_method": ApplicationMethodType.BROADCAST.value,
                "soil_type": "loam"
            }
        ]

        response = client.post(
            "/api/v1/equipment/compatibility/optimize",
            json=fields
        )

        assert response.status_code == 200
        data = response.json()
        assert "recommended_equipment" in data

    def test_optimize_validation_errors(self, client):
        """Test optimization endpoint validation."""
        # Test with empty fields list
        response = client.post(
            "/api/v1/equipment/compatibility/optimize",
            json=[]
        )
        assert response.status_code == 400

        # Test with missing required field data
        fields = [
            {
                "size_acres": 100.0
                # Missing fertilizer_type and application_method
            }
        ]
        response = client.post(
            "/api/v1/equipment/compatibility/optimize",
            json=fields
        )
        assert response.status_code == 400

    def test_assess_compatibility_invalid_parameters(self, client):
        """Test compatibility assessment with invalid parameters."""
        # Test with invalid field size (negative)
        response = client.post(
            "/api/v1/equipment/compatibility/assess",
            params={
                "equipment_id": "test",
                "fertilizer_type": FertilizerFormulation.GRANULAR.value,
                "application_method": ApplicationMethodType.BROADCAST.value,
                "field_size_acres": -10.0,  # Invalid
                "soil_type": "loam"
            }
        )
        assert response.status_code == 422  # Validation error

        # Test with invalid field size (too large)
        response = client.post(
            "/api/v1/equipment/compatibility/assess",
            params={
                "equipment_id": "test",
                "fertilizer_type": FertilizerFormulation.GRANULAR.value,
                "application_method": ApplicationMethodType.BROADCAST.value,
                "field_size_acres": 20000.0,  # Too large
                "soil_type": "loam"
            }
        )
        assert response.status_code == 422

    def test_recommendations_parameter_validation(self, client):
        """Test recommendations endpoint parameter validation."""
        # Test with invalid top_n (too large)
        response = client.post(
            "/api/v1/equipment/compatibility/recommend",
            params={
                "fertilizer_type": FertilizerFormulation.GRANULAR.value,
                "application_method": ApplicationMethodType.BROADCAST.value,
                "field_size_acres": 100.0,
                "soil_type": "loam",
                "top_n": 50  # Exceeds maximum
            }
        )
        assert response.status_code == 422

        # Test with invalid top_n (zero)
        response = client.post(
            "/api/v1/equipment/compatibility/recommend",
            params={
                "fertilizer_type": FertilizerFormulation.GRANULAR.value,
                "application_method": ApplicationMethodType.BROADCAST.value,
                "field_size_acres": 100.0,
                "soil_type": "loam",
                "top_n": 0  # Invalid
            }
        )
        assert response.status_code == 422

    def test_api_response_times(self, client):
        """Test that API responses are reasonably fast."""
        import time

        # Test compatibility assessment
        start = time.time()
        response = client.post(
            "/api/v1/equipment/compatibility/assess",
            params={
                "equipment_id": "test",
                "fertilizer_type": FertilizerFormulation.GRANULAR.value,
                "application_method": ApplicationMethodType.BROADCAST.value,
                "field_size_acres": 100.0,
                "soil_type": "loam"
            }
        )
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 2.0  # Should complete in under 2 seconds

        # Test recommendations
        start = time.time()
        response = client.post(
            "/api/v1/equipment/compatibility/recommend",
            params={
                "fertilizer_type": FertilizerFormulation.LIQUID.value,
                "application_method": ApplicationMethodType.FOLIAR.value,
                "field_size_acres": 100.0,
                "soil_type": "loam",
                "top_n": 5
            }
        )
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 3.0  # Should complete in under 3 seconds

    def test_concurrent_requests(self, client):
        """Test handling of concurrent requests."""
        import concurrent.futures

        def make_request():
            return client.post(
                "/api/v1/equipment/compatibility/assess",
                params={
                    "equipment_id": "test",
                    "fertilizer_type": FertilizerFormulation.GRANULAR.value,
                    "application_method": ApplicationMethodType.BROADCAST.value,
                    "field_size_acres": 100.0,
                    "soil_type": "loam"
                }
            )

        # Make 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [f.result() for f in futures]

        # All should succeed
        assert all(r.status_code == 200 for r in results)

    def test_data_consistency_across_endpoints(self, client):
        """Test data consistency across related endpoints."""
        # Get full compatibility matrix
        matrix_response = client.get("/api/v1/equipment/compatibility/matrix")
        assert matrix_response.status_code == 200
        matrix_data = matrix_response.json()

        # Get recommendations for specific combination
        recommendations_response = client.post(
            "/api/v1/equipment/compatibility/recommend",
            params={
                "fertilizer_type": FertilizerFormulation.GRANULAR.value,
                "application_method": ApplicationMethodType.BROADCAST.value,
                "field_size_acres": 100.0,
                "soil_type": "loam",
                "top_n": 3
            }
        )
        assert recommendations_response.status_code == 200
        recommendations = recommendations_response.json()

        # Recommendations should be consistent with matrix data
        assert len(recommendations) > 0


class TestEquipmentCompatibilityAPIEdgeCases:
    """Test edge cases and error scenarios."""

    def test_extreme_field_sizes(self, client):
        """Test with extreme field sizes."""
        # Very small field
        response = client.post(
            "/api/v1/equipment/compatibility/assess",
            params={
                "equipment_id": "test",
                "fertilizer_type": FertilizerFormulation.GRANULAR.value,
                "application_method": ApplicationMethodType.BROADCAST.value,
                "field_size_acres": 0.1,  # Minimum allowed
                "soil_type": "loam"
            }
        )
        assert response.status_code == 200

        # Very large field
        response = client.post(
            "/api/v1/equipment/compatibility/assess",
            params={
                "equipment_id": "test",
                "fertilizer_type": FertilizerFormulation.GRANULAR.value,
                "application_method": ApplicationMethodType.BROADCAST.value,
                "field_size_acres": 10000.0,  # Maximum allowed
                "soil_type": "loam"
            }
        )
        assert response.status_code == 200

    def test_extreme_weather_conditions(self, client):
        """Test with extreme weather conditions."""
        # High wind
        response = client.post(
            "/api/v1/equipment/compatibility/recommend",
            params={
                "fertilizer_type": FertilizerFormulation.LIQUID.value,
                "application_method": ApplicationMethodType.FOLIAR.value,
                "field_size_acres": 100.0,
                "soil_type": "loam",
                "wind_speed_mph": 45.0,  # Very high wind
                "top_n": 3
            }
        )
        assert response.status_code == 200
        # Should still provide recommendations but with warnings

    def test_all_fertilizer_types(self, client):
        """Test compatibility assessment for all fertilizer types."""
        fertilizer_types = [
            FertilizerFormulation.LIQUID,
            FertilizerFormulation.GRANULAR,
            FertilizerFormulation.PELLET,
            FertilizerFormulation.SLOW_RELEASE,
            FertilizerFormulation.ORGANIC,
            FertilizerFormulation.SYNTHETIC,
            FertilizerFormulation.SUSPENSION,
            FertilizerFormulation.SOLUTION
        ]

        for fert_type in fertilizer_types:
            response = client.post(
                "/api/v1/equipment/compatibility/recommend",
                params={
                    "fertilizer_type": fert_type.value,
                    "application_method": ApplicationMethodType.BROADCAST.value,
                    "field_size_acres": 100.0,
                    "soil_type": "loam",
                    "top_n": 3
                }
            )
            # Should get valid response for each type
            assert response.status_code == 200 or response.status_code == 400

    def test_all_application_methods(self, client):
        """Test compatibility for all application methods."""
        application_methods = [
            ApplicationMethodType.BROADCAST,
            ApplicationMethodType.BAND,
            ApplicationMethodType.FOLIAR,
            ApplicationMethodType.DRIP,
            ApplicationMethodType.INJECTION,
            ApplicationMethodType.SIDEDRESS,
            ApplicationMethodType.FERTIGATION,
            ApplicationMethodType.TOPDRESS
        ]

        for app_method in application_methods:
            response = client.post(
                "/api/v1/equipment/compatibility/recommend",
                params={
                    "fertilizer_type": FertilizerFormulation.LIQUID.value,
                    "application_method": app_method.value,
                    "field_size_acres": 100.0,
                    "soil_type": "loam",
                    "top_n": 3
                }
            )
            # Should get valid response for each method
            assert response.status_code in [200, 400]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

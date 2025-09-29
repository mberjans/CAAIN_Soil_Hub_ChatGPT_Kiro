"""
Unit tests for crop rotation plan update endpoint.
Tests the PUT /api/v1/rotations/{plan_id} endpoint functionality.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI
import json
from datetime import datetime

# Import the modules to test
try:
    from services.recommendation_engine.src.api.rotation_routes import router
    from services.recommendation_engine.src.models.rotation_models import (
        CropRotationPlan, RotationPlanUpdateRequest
    )
except ImportError:
    # Fallback for testing
    from src.api.rotation_routes import router
    from src.models.rotation_models import CropRotationPlan, RotationPlanUpdateRequest


class TestRotationPlanUpdateEndpoint:
    """Test class for rotation plan update endpoint."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)
    
    @pytest.fixture
    def sample_rotation_plan(self):
        """Create sample rotation plan for testing."""
        return CropRotationPlan(
            plan_id="test-plan-123",
            field_id="field-456",
            farm_id="farm-789",
            plan_name="Test Rotation Plan",
            created_date=datetime.utcnow(),
            rotation_years={2024: "corn", 2025: "soybean", 2026: "wheat"},
            rotation_details={
                2024: {"crop": "corn", "variety": "pioneer", "notes": "high yield variety"},
                2025: {"crop": "soybean", "variety": "roundup ready", "notes": "nitrogen fixing"},
                2026: {"crop": "wheat", "variety": "winter wheat", "notes": "erosion control"}
            },
            overall_score=8.5,
            benefit_scores={"soil_health": 9.0, "profitability": 8.0},
            economic_projections={"net_profit": 15000, "break_even": 12000}
        )
    
    @pytest.fixture
    def valid_update_request(self):
        """Create valid update request."""
        return {
            "plan_name": "Updated Test Plan",
            "overall_score": 9.0,
            "rotation_years": {2024: "corn", 2025: "soybean", 2026: "oats"},
            "benefit_scores": {"soil_health": 9.5, "profitability": 8.5}
        }
    
    @patch('src.api.rotation_routes.rotation_storage_service')
    async def test_update_plan_success(self, mock_storage_service, client, sample_rotation_plan, valid_update_request):
        """Test successful plan update."""
        # Setup mock
        updated_plan = sample_rotation_plan
        updated_plan.plan_name = "Updated Test Plan"
        updated_plan.overall_score = 9.0
        mock_storage_service.update_plan = AsyncMock(return_value=updated_plan)
        
        # Make request
        response = client.put("/api/v1/rotations/plans/test-plan-123", json=valid_update_request)
        
        # Assertions
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["plan_id"] == "test-plan-123"
        assert response_data["plan_name"] == "Updated Test Plan"
        assert response_data["overall_score"] == 9.0
        
        # Verify storage service was called
        mock_storage_service.update_plan.assert_called_once()
    
    @patch('src.api.rotation_routes.rotation_storage_service')
    async def test_update_plan_not_found(self, mock_storage_service, client, valid_update_request):
        """Test update of non-existent plan."""
        # Setup mock to return None (plan not found)
        mock_storage_service.update_plan = AsyncMock(return_value=None)
        
        # Make request
        response = client.put("/api/v1/rotations/plans/nonexistent-plan", json=valid_update_request)
        
        # Assertions
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    async def test_update_plan_empty_id(self, client, valid_update_request):
        """Test update with empty plan ID."""
        # Make request with empty plan ID
        response = client.put("/api/v1/rotations/plans/", json=valid_update_request)
        
        # Should get 404 for missing path parameter
        assert response.status_code == 404
    
    async def test_update_plan_whitespace_id(self, client, valid_update_request):
        """Test update with whitespace-only plan ID."""
        # Make request with whitespace plan ID
        response = client.put("/api/v1/rotations/plans/   ", json=valid_update_request)
        
        # Should get 400 for invalid plan ID
        assert response.status_code == 400
        assert "cannot be empty" in response.json()["detail"].lower()
    
    async def test_update_plan_invalid_json(self, client):
        """Test update with invalid JSON."""
        # Make request with invalid JSON
        response = client.put(
            "/api/v1/rotations/plans/test-plan-123",
            data="invalid json",
            headers={"content-type": "application/json"}
        )
        
        # Should get 422 for invalid JSON
        assert response.status_code == 422
    
    @patch('src.api.rotation_routes.rotation_storage_service')
    async def test_update_plan_partial_update(self, mock_storage_service, client, sample_rotation_plan):
        """Test partial plan update (only some fields)."""
        # Setup mock
        updated_plan = sample_rotation_plan
        updated_plan.plan_name = "Partially Updated Plan"
        mock_storage_service.update_plan = AsyncMock(return_value=updated_plan)
        
        # Make request with only plan_name update
        partial_update = {"plan_name": "Partially Updated Plan"}
        response = client.put("/api/v1/rotations/plans/test-plan-123", json=partial_update)
        
        # Assertions
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["plan_name"] == "Partially Updated Plan"
        
        # Verify storage service was called
        mock_storage_service.update_plan.assert_called_once()
    
    @patch('src.api.rotation_routes.rotation_storage_service')
    async def test_update_plan_validation_error(self, mock_storage_service, client):
        """Test update with validation error."""
        # Setup mock to raise ValueError
        mock_storage_service.update_plan = AsyncMock(side_effect=ValueError("Invalid crop rotation"))
        
        # Make request
        update_request = {"plan_name": "Test Plan"}
        response = client.put("/api/v1/rotations/plans/test-plan-123", json=update_request)
        
        # Assertions
        assert response.status_code == 400
        assert "Invalid crop rotation" in response.json()["detail"]
    
    @patch('src.api.rotation_routes.rotation_storage_service')
    async def test_update_plan_server_error(self, mock_storage_service, client):
        """Test update with server error."""
        # Setup mock to raise generic Exception
        mock_storage_service.update_plan = AsyncMock(side_effect=Exception("Database connection failed"))
        
        # Make request
        update_request = {"plan_name": "Test Plan"}
        response = client.put("/api/v1/rotations/plans/test-plan-123", json=update_request)
        
        # Assertions
        assert response.status_code == 500
        assert "Failed to update rotation plan" in response.json()["detail"]
    
    async def test_update_plan_invalid_goal_weights(self, client):
        """Test update with invalid goal weights."""
        # Create update with invalid goal weights (sum != 1.0)
        invalid_update = {
            "goals": [
                {
                    "goal_type": "soil_health",
                    "priority": 5,
                    "weight": 0.7,  # These weights sum to 1.1, not 1.0
                    "description": "Improve soil health"
                },
                {
                    "goal_type": "profit_maximization", 
                    "priority": 4,
                    "weight": 0.4,
                    "description": "Maximize profit"
                }
            ]
        }
        
        # Make request
        response = client.put("/api/v1/rotations/plans/test-plan-123", json=invalid_update)
        
        # Should get validation error
        assert response.status_code == 422
    
    async def test_update_plan_invalid_year_range(self, client):
        """Test update with invalid year in rotation."""
        # Create update with invalid year
        invalid_update = {
            "rotation_years": {
                1990: "corn",  # Year too old
                2060: "soybean"  # Year too far in future
            }
        }
        
        # Make request
        response = client.put("/api/v1/rotations/plans/test-plan-123", json=invalid_update)
        
        # Should get validation error
        assert response.status_code == 422


@pytest.mark.asyncio
class TestRotationPlanUpdateIntegration:
    """Integration tests for rotation plan updates."""
    
    async def test_update_plan_end_to_end(self):
        """Test complete update workflow."""
        # This would test the complete flow if we had a test database
        # For now, we'll mark it as a placeholder for future implementation
        pass


if __name__ == "__main__":
    pytest.main([__file__])
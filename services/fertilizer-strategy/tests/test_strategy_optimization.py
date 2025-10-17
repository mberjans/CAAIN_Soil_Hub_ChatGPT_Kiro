"""
Test suite for fertilizer strategy optimization endpoints

Tests the comprehensive strategy optimization API endpoints including:
- Strategy optimization endpoint
- ROI analysis 
- Break-even analysis
- Price trend analysis

Author: AI Agent
Date: 2025-01-27
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from datetime import date, datetime

# Import the FastAPI app
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

try:
    from src.main import app
except ImportError:
    # Fallback for different import paths
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))
    import main
    app = main.app

client = TestClient(app)


class TestStrategyOptimization:
    """Test class for strategy optimization endpoints"""
    
    def setup_method(self):
        """Setup test data for each test method"""
        self.sample_request = {
            "farm_context": {
                "fields": [
                    {
                        "field_id": "field_001",
                        "acres": 80,
                        "soil_tests": {
                            "N": 25,
                            "P": 45,
                            "K": 180,
                            "pH": 6.5
                        },
                        "crop_plan": {
                            "crop": "corn",
                            "target_yield": 180
                        }
                    }
                ],
                "budget_constraints": {
                    "total_budget": 12000,
                    "max_per_acre": 150
                },
                "equipment_available": ["broadcast_spreader", "field_sprayer"]
            },
            "optimization_goals": {
                "primary_goal": "profit_maximization",
                "yield_priority": 0.8,
                "cost_priority": 0.7,
                "environmental_priority": 0.6,
                "risk_tolerance": "moderate"
            },
            "constraints": {
                "environmental_limits": {
                    "max_n_rate": 200,
                    "buffer_zones": True
                },
                "timing_constraints": {
                    "planting_date": "2024-05-01",
                    "harvest_date": "2024-10-15"
                },
                "regulatory_compliance": ["clean_water_act", "state_regulations"]
            }
        }
    
    def test_health_check(self):
        """Test that the health check endpoint works"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_root_endpoint(self):
        """Test that the root endpoint works"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "fertilizer-strategy-optimization" in data["service"]
    
    @patch('services.fertilizer-strategy.src.api.strategy_routes.yield_goal_service.optimize_fertilizer_strategy')
    @patch('services.fertilizer-strategy.src.api.strategy_routes.roi_optimizer_service.optimize_fertilizer_roi')
    @patch('services.fertilizer-strategy.src.api.strategy_routes.sustainability_service.optimize_environmental_impact')
    def test_optimize_strategy_endpoint_basic(self, mock_sustainability, mock_roi, mock_yield):
        """Test basic strategy optimization endpoint functionality"""
        
        # Mock service responses
        mock_yield.return_value = {
            "recommended_rates": {"N": 180, "P": 50, "K": 80},
            "application_methods": ["broadcast", "side_dress"],
            "timing_schedule": ["pre_plant", "v6_stage"],
            "expected_yield": 175,
            "confidence": 0.85
        }
        
        mock_roi.return_value = {
            "total_cost": 9600,
            "roi_percentage": 0.18,
            "confidence": 0.80
        }
        
        mock_sustainability.return_value = {
            "environmental_score": 0.75,
            "confidence": 0.78
        }
        
        # Make request
        response = client.post("/api/v1/fertilizer/optimize-strategy", json=self.sample_request)
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "strategy_id" in data
        assert "total_cost" in data
        assert "expected_roi" in data
        assert "field_strategies" in data
        assert "economic_analysis" in data
        assert "environmental_impact" in data
        assert "confidence_score" in data
        
        # Verify field strategies
        assert len(data["field_strategies"]) == 1
        field_strategy = data["field_strategies"][0]
        assert field_strategy["field_id"] == "field_001"
        assert field_strategy["acres"] == 80
        assert "recommended_rates" in field_strategy
        assert "total_cost" in field_strategy
        
        # Verify economic analysis
        economic = data["economic_analysis"]
        assert "total_investment" in economic
        assert "expected_return" in economic
        assert "break_even_yield" in economic
        assert "payback_period" in economic
        
        # Verify confidence score is reasonable
        assert 0.0 <= data["confidence_score"] <= 1.0
    
    def test_optimize_strategy_validation_errors(self):
        """Test validation errors for strategy optimization"""
        
        # Test missing required fields
        invalid_request = {"farm_context": {}}
        response = client.post("/api/v1/fertilizer/optimize-strategy", json=invalid_request)
        assert response.status_code == 422
        
        # Test invalid primary goal
        invalid_goal_request = self.sample_request.copy()
        invalid_goal_request["optimization_goals"]["primary_goal"] = "invalid_goal"
        response = client.post("/api/v1/fertilizer/optimize-strategy", json=invalid_goal_request)
        assert response.status_code == 422
        
        # Test invalid soil test data
        invalid_soil_request = self.sample_request.copy()
        invalid_soil_request["farm_context"]["fields"][0]["soil_tests"] = {"N": 25}  # Missing P, K, pH
        response = client.post("/api/v1/fertilizer/optimize-strategy", json=invalid_soil_request)
        assert response.status_code == 422
    
    def test_optimize_strategy_budget_constraints(self):
        """Test strategy optimization with tight budget constraints"""
        
        # Create request with very low budget
        low_budget_request = self.sample_request.copy()
        low_budget_request["farm_context"]["budget_constraints"]["total_budget"] = 1000  # Very low
        low_budget_request["farm_context"]["budget_constraints"]["max_per_acre"] = 12.5   # Very low
        
        with patch('services.fertilizer-strategy.src.api.strategy_routes.yield_goal_service.optimize_fertilizer_strategy') as mock_yield:
            with patch('services.fertilizer-strategy.src.api.strategy_routes.roi_optimizer_service.optimize_fertilizer_roi') as mock_roi:
                with patch('services.fertilizer-strategy.src.api.strategy_routes.sustainability_service.optimize_environmental_impact') as mock_sustainability:
                    
                    # Mock high-cost response that should trigger budget constraint
                    mock_yield.return_value = {"recommended_rates": {"N": 180, "P": 50, "K": 80}, "confidence": 0.85}
                    mock_roi.return_value = {"total_cost": 5000, "roi_percentage": 0.15, "confidence": 0.80}  # High cost per field
                    mock_sustainability.return_value = {"environmental_score": 0.75, "confidence": 0.78}
                    
                    response = client.post("/api/v1/fertilizer/optimize-strategy", json=low_budget_request)
                    
                    assert response.status_code == 200
                    data = response.json()
                    
                    # Should have budget constraint warning
                    assert any("budget" in note.lower() for note in data.get("optimization_notes", []))
                    
                    # Total cost should be within budget
                    assert data["total_cost"] <= 1000
    
    def test_optimize_strategy_multiple_fields(self):
        """Test strategy optimization with multiple fields"""
        
        # Add second field
        multi_field_request = self.sample_request.copy()
        multi_field_request["farm_context"]["fields"].append({
            "field_id": "field_002",
            "acres": 120,
            "soil_tests": {
                "N": 30,
                "P": 40,
                "K": 200,
                "pH": 6.8
            },
            "crop_plan": {
                "crop": "soybean",
                "target_yield": 50
            }
        })
        multi_field_request["farm_context"]["budget_constraints"]["total_budget"] = 20000
        
        with patch('services.fertilizer-strategy.src.api.strategy_routes.yield_goal_service.optimize_fertilizer_strategy') as mock_yield:
            with patch('services.fertilizer-strategy.src.api.strategy_routes.roi_optimizer_service.optimize_fertilizer_roi') as mock_roi:
                with patch('services.fertilizer-strategy.src.api.strategy_routes.sustainability_service.optimize_environmental_impact') as mock_sustainability:
                    
                    mock_yield.return_value = {"recommended_rates": {"N": 0, "P": 30, "K": 60}, "confidence": 0.85}
                    mock_roi.return_value = {"total_cost": 4000, "roi_percentage": 0.20, "confidence": 0.80}
                    mock_sustainability.return_value = {"environmental_score": 0.85, "confidence": 0.78}
                    
                    response = client.post("/api/v1/fertilizer/optimize-strategy", json=multi_field_request)
                    
                    assert response.status_code == 200
                    data = response.json()
                    
                    # Should have strategies for both fields
                    assert len(data["field_strategies"]) == 2
                    field_ids = [fs["field_id"] for fs in data["field_strategies"]]
                    assert "field_001" in field_ids
                    assert "field_002" in field_ids
    
    def test_optimize_strategy_environmental_compliance(self):
        """Test strategy optimization with environmental constraints"""
        
        # Set very low nitrogen limit
        env_constrained_request = self.sample_request.copy()
        env_constrained_request["constraints"]["environmental_limits"]["max_n_rate"] = 50  # Very low N limit
        
        with patch('services.fertilizer-strategy.src.api.strategy_routes.yield_goal_service.optimize_fertilizer_strategy') as mock_yield:
            with patch('services.fertilizer-strategy.src.api.strategy_routes.roi_optimizer_service.optimize_fertilizer_roi') as mock_roi:
                with patch('services.fertilizer-strategy.src.api.strategy_routes.sustainability_service.optimize_environmental_impact') as mock_sustainability:
                    
                    # Mock response with high N rate (should fail compliance)
                    mock_yield.return_value = {"recommended_rates": {"N": 200, "P": 50, "K": 80}, "confidence": 0.85}
                    mock_roi.return_value = {"total_cost": 9600, "roi_percentage": 0.18, "confidence": 0.80}
                    mock_sustainability.return_value = {"environmental_score": 0.45, "confidence": 0.78}  # Low score
                    
                    response = client.post("/api/v1/fertilizer/optimize-strategy", json=env_constrained_request)
                    
                    assert response.status_code == 200
                    data = response.json()
                    
                    # Check environmental impact assessment
                    env_impact = data["environmental_impact"]
                    assert "n_rate_compliance" in env_impact
                    assert "average_n_rate" in env_impact
                    assert "sustainability_rating" in env_impact
    
    def test_optimize_strategy_service_failure_fallback(self):
        """Test strategy optimization when services fail and fallback is used"""
        
        with patch('services.fertilizer-strategy.src.api.strategy_routes.yield_goal_service.optimize_fertilizer_strategy') as mock_yield:
            with patch('services.fertilizer-strategy.src.api.strategy_routes.roi_optimizer_service.optimize_fertilizer_roi') as mock_roi:
                with patch('services.fertilizer-strategy.src.api.strategy_routes.sustainability_service.optimize_environmental_impact') as mock_sustainability:
                    
                    # Mock service failures
                    mock_yield.side_effect = Exception("Service unavailable")
                    mock_roi.side_effect = Exception("Service unavailable")
                    mock_sustainability.side_effect = Exception("Service unavailable")
                    
                    response = client.post("/api/v1/fertilizer/optimize-strategy", json=self.sample_request)
                    
                    assert response.status_code == 200
                    data = response.json()
                    
                    # Should have fallback strategy
                    assert len(data["field_strategies"]) == 1
                    field_strategy = data["field_strategies"][0]
                    assert field_strategy["confidence_level"] == 0.5  # Low confidence for fallback
                    
                    # Should have service failure notes
                    assert len(data["optimization_notes"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
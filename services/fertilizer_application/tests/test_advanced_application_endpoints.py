"""
Comprehensive tests for advanced application management endpoints.
Tests TICKET-023_fertilizer-application-method-10.2 implementation.
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from datetime import datetime, date, timedelta
from uuid import uuid4

from src.main import app
from src.models.application_models import (
    ApplicationPlanRequest, ApplicationPlanResponse, ApplicationPlan,
    ApplicationMonitorRequest, ApplicationMonitorResponse, ApplicationStatus,
    OptimizationRequest, OptimizationResponse, OptimizationRecommendation,
    ApplicationMethodType
)

client = TestClient(app)


class TestAdvancedApplicationEndpoints:
    """Test suite for advanced application management endpoints."""

    def test_create_application_plan_success(self):
        """Test successful application plan creation."""
        request_data = {
            "user_id": "user_123",
            "farm_id": "farm_456",
            "fields": [
                {
                    "field_id": "field_1",
                    "field_name": "North Field",
                    "crop_type": "corn",
                    "acres": 50.0
                },
                {
                    "field_id": "field_2",
                    "field_name": "South Field",
                    "crop_type": "soybean",
                    "acres": 30.0
                }
            ],
            "season": "spring",
            "planning_horizon_days": 90,
            "objectives": ["yield_optimization", "cost_optimization"],
            "constraints": {
                "budget_limit": 10000.0,
                "equipment_availability": ["tractor", "broadcast_spreader"]
            },
            "preferences": {
                "prefer_organic": False,
                "environmental_focus": True
            }
        }
        
        response = client.post("/api/v1/fertilizer/application/plan", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "request_id" in data
        assert "plan_id" in data
        assert "farm_name" in data
        assert "season" in data
        assert "planning_horizon_days" in data
        assert "total_fields" in data
        assert "application_plans" in data
        assert "resource_summary" in data
        assert "cost_summary" in data
        assert "timeline" in data
        assert "optimization_recommendations" in data
        assert "processing_time_ms" in data
        
        # Validate specific values
        assert data["season"] == "spring"
        assert data["planning_horizon_days"] == 90
        assert data["total_fields"] == 2
        assert len(data["application_plans"]) == 2
        assert data["resource_summary"]["total_cost"] > 0
        assert len(data["timeline"]) == 2

    def test_monitor_applications_success(self):
        """Test successful application monitoring."""
        params = {
            "user_id": "user_123",
            "farm_id": "farm_456",
            "include_historical": True,
            "time_range_days": 30
        }
        
        response = client.get("/api/v1/fertilizer/application/monitor", params=params)
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "request_id" in data
        assert "farm_name" in data
        assert "monitoring_timestamp" in data
        assert "total_fields" in data
        assert "active_applications" in data
        assert "completed_applications" in data
        assert "field_statuses" in data
        assert "farm_summary" in data
        assert "alerts_summary" in data
        assert "recommendations" in data
        assert "processing_time_ms" in data
        
        # Validate specific values
        assert data["total_fields"] >= 0
        assert data["active_applications"] >= 0
        assert data["completed_applications"] >= 0
        assert isinstance(data["field_statuses"], list)
        assert isinstance(data["farm_summary"], dict)
        assert isinstance(data["alerts_summary"], dict)
        assert isinstance(data["recommendations"], list)

    def test_optimize_application_success(self):
        """Test successful application optimization."""
        request_data = {
            "user_id": "user_123",
            "farm_id": "farm_456",
            "field_id": "field_1",
            "current_conditions": {
                "soil_moisture": "optimal",
                "temperature": 75,
                "wind_speed": 5,
                "crop_health": "good",
                "nutrient_levels": "adequate"
            },
            "weather_update": {
                "temperature": 78,
                "humidity": 65,
                "wind_speed": 8,
                "precipitation_probability": 0.2
            },
            "equipment_status": {
                "status": "operational",
                "last_maintenance": "2024-01-15",
                "calibration_status": "current"
            },
            "optimization_goals": ["efficiency", "cost_optimization"],
            "constraints": {
                "budget_limit": 5000.0,
                "time_constraint": "immediate"
            }
        }
        
        response = client.post("/api/v1/fertilizer/application/optimize", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "request_id" in data
        assert "field_id" in data
        assert "field_name" in data
        assert "optimization_timestamp" in data
        assert "current_conditions_summary" in data
        assert "optimization_score" in data
        assert "recommendations" in data
        assert "performance_predictions" in data
        assert "risk_assessment" in data
        assert "next_optimization_due" in data
        assert "processing_time_ms" in data
        
        # Validate specific values
        assert data["field_id"] == "field_1"
        assert 0 <= data["optimization_score"] <= 100
        assert isinstance(data["recommendations"], list)
        assert isinstance(data["performance_predictions"], dict)
        assert isinstance(data["risk_assessment"], dict)

    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/api/v1/fertilizer/application/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["service"] == "advanced-application-management"
        assert data["status"] == "healthy"
        assert "features" in data
        assert "endpoints" in data
        assert "version" in data
        
        # Validate features
        expected_features = [
            "application_planning",
            "real_time_monitoring",
            "dynamic_optimization",
            "resource_optimization",
            "cost_analysis",
            "performance_prediction",
            "risk_assessment"
        ]
        for feature in expected_features:
            assert feature in data["features"]
        
        # Validate endpoints
        expected_endpoints = [
            "POST /fertilizer/application/plan",
            "GET /fertilizer/application/monitor",
            "POST /fertilizer/application/optimize"
        ]
        for endpoint in expected_endpoints:
            assert endpoint in data["endpoints"]

    def test_planning_templates(self):
        """Test planning templates endpoint."""
        response = client.get("/api/v1/fertilizer/application/planning-templates")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "templates" in data
        assert isinstance(data["templates"], list)
        assert len(data["templates"]) > 0
        
        # Validate template structure
        for template in data["templates"]:
            assert "template_id" in template
            assert "name" in template
            assert "description" in template
            assert "season" in template
            assert "crop_type" in template
            assert "default_objectives" in template
            assert "typical_fields" in template
            assert "planning_horizon_days" in template

    def test_optimization_metrics(self):
        """Test optimization metrics endpoint."""
        response = client.get("/api/v1/fertilizer/application/optimization-metrics")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "metrics" in data
        assert isinstance(data["metrics"], list)
        assert len(data["metrics"]) > 0
        
        # Validate metric structure
        for metric in data["metrics"]:
            assert "metric_id" in metric
            assert "name" in metric
            assert "description" in metric
            assert "unit" in metric
            assert "target_range" in metric

    def test_status_types(self):
        """Test status types endpoint."""
        response = client.get("/api/v1/fertilizer/application/status-types")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status_types" in data
        assert isinstance(data["status_types"], list)
        assert len(data["status_types"]) > 0
        
        # Validate status type structure
        for status_type in data["status_types"]:
            assert "status" in status_type
            assert "description" in status_type
            assert "color" in status_type
            assert "icon" in status_type

    def test_performance_requirements(self):
        """Test that endpoints meet performance requirements."""
        import time
        
        # Test plan creation performance
        request_data = {
            "user_id": "user_123",
            "farm_id": "farm_456",
            "fields": [
                {
                    "field_id": "field_1",
                    "field_name": "Test Field",
                    "crop_type": "corn",
                    "acres": 100.0
                }
            ],
            "season": "spring",
            "planning_horizon_days": 90,
            "objectives": ["yield_optimization"]
        }
        
        start_time = time.time()
        response = client.post("/api/v1/fertilizer/application/plan", json=request_data)
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 3.0  # Should respond within 3 seconds
        
        # Test monitoring performance
        start_time = time.time()
        response = client.get("/api/v1/fertilizer/application/monitor", params={
            "user_id": "user_123",
            "farm_id": "farm_456"
        })
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 2.0  # Should respond within 2 seconds
        
        # Test optimization performance
        request_data = {
            "user_id": "user_123",
            "farm_id": "farm_456",
            "field_id": "field_1",
            "current_conditions": {"soil_moisture": "optimal", "temperature": 70}
        }
        
        start_time = time.time()
        response = client.post("/api/v1/fertilizer/application/optimize", json=request_data)
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 2.0  # Should respond within 2 seconds


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

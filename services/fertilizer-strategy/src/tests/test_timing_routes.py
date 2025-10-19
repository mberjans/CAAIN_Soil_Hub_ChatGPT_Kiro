"""
Tests for Timing Routes API Endpoints

This module contains comprehensive tests for the new timing routes API endpoints,
including request validation, response structure, error handling, and integration tests.
"""

import pytest
import asyncio
from datetime import date, datetime, timedelta
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

from ..api.timing_routes import router, get_timing_optimizer
from ..models.timing_optimization_models import (
    AdvancedTimingOptimizationRequest,
    AdvancedTimingOptimizationResponse,
    FarmContext,
    FieldContext,
    EquipmentConstraints,
    LaborConstraints,
    OptimizationGoals,
    TimingConstraints,
    FertilizerCalendarResponse,
    CalendarEvent,
    ApplicationWindowsResponse,
    ApplicationWindow,
    AlertSubscriptionRequest,
    AlertSubscriptionResponse,
    AlertPreferences,
    AlertManagementResponse,
    WeatherCondition,
    ApplicationMethod,
    CropGrowthStage
)
from ..services.timing_optimization_service import FertilizerTimingOptimizer


# Create test FastAPI app
app = FastAPI()
app.include_router(router)


# Test client
client = TestClient(app)


class TestAdvancedTimingOptimization:
    """Test suite for POST /timing-optimization endpoint."""

    @pytest.fixture
    def sample_advanced_request(self):
        """Create sample advanced timing optimization request."""
        return {
            "farm_context": {
                "fields": [
                    {
                        "field_id": "field_001",
                        "crop": "corn",
                        "planting_date": "2024-05-01",
                        "soil_conditions": {"moisture": "adequate", "temperature": 55},
                        "previous_applications": []
                    },
                    {
                        "field_id": "field_002",
                        "crop": "soybean",
                        "planting_date": "2024-05-10",
                        "soil_conditions": {"moisture": "adequate", "temperature": 58},
                        "previous_applications": []
                    }
                ],
                "equipment_constraints": {
                    "available_equipment": ["field_sprayer", "broadcast_spreader"],
                    "capacity_per_day": 200,
                    "maintenance_windows": ["2024-06-15", "2024-07-01"]
                },
                "labor_constraints": {
                    "available_hours_per_day": 10,
                    "skilled_operators": 2,
                    "peak_season_conflicts": ["planting", "harvest"]
                }
            },
            "optimization_goals": {
                "primary_goal": "nutrient_efficiency",
                "weather_risk_tolerance": "moderate",
                "cost_priority": 0.7,
                "environmental_priority": 0.8
            },
            "timing_constraints": {
                "earliest_application": "2024-04-15",
                "latest_application": "2024-07-15",
                "restricted_periods": ["2024-05-15:2024-05-20"],
                "regulatory_windows": ["spring_application_window"]
            }
        }

    def test_advanced_timing_optimization_success(self, sample_advanced_request):
        """Test successful advanced timing optimization."""
        response = client.post(
            "/api/v1/fertilizer/timing-optimization",
            json=sample_advanced_request
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "request_id" in data
        assert "optimization_id" in data
        assert "optimized_schedule" in data
        assert "weather_integration" in data
        assert "efficiency_predictions" in data
        assert "risk_assessments" in data
        assert "recommendations" in data
        assert "processing_time_ms" in data
        assert "created_at" in data

        # Verify efficiency predictions
        assert "nutrient_efficiency" in data["efficiency_predictions"]
        assert "application_efficiency" in data["efficiency_predictions"]
        assert "cost_efficiency" in data["efficiency_predictions"]

        # Verify risk assessments
        assert "weather_risk" in data["risk_assessments"]
        assert "timing_risk" in data["risk_assessments"]
        assert "operational_risk" in data["risk_assessments"]
        assert "overall_risk" in data["risk_assessments"]

        # Verify processing time is reasonable (<3s = 3000ms)
        assert data["processing_time_ms"] < 3000

    def test_advanced_timing_optimization_invalid_dates(self):
        """Test advanced timing optimization with invalid date constraints."""
        request_data = {
            "farm_context": {
                "fields": [
                    {
                        "field_id": "field_001",
                        "crop": "corn",
                        "planting_date": "2024-05-01",
                        "soil_conditions": {"moisture": "adequate"},
                        "previous_applications": []
                    }
                ],
                "equipment_constraints": {
                    "available_equipment": ["field_sprayer"],
                    "capacity_per_day": 200,
                    "maintenance_windows": []
                },
                "labor_constraints": {
                    "available_hours_per_day": 10,
                    "skilled_operators": 2,
                    "peak_season_conflicts": []
                }
            },
            "optimization_goals": {
                "primary_goal": "nutrient_efficiency",
                "weather_risk_tolerance": "moderate",
                "cost_priority": 0.7,
                "environmental_priority": 0.8
            },
            "timing_constraints": {
                "earliest_application": "2024-07-15",  # After latest
                "latest_application": "2024-04-15",    # Before earliest
                "restricted_periods": [],
                "regulatory_windows": []
            }
        }

        # Should still succeed but return empty or adjusted schedule
        response = client.post(
            "/api/v1/fertilizer/timing-optimization",
            json=request_data
        )

        # May succeed with warnings or fail with 400
        assert response.status_code in [200, 400, 422]

    def test_advanced_timing_optimization_empty_fields(self):
        """Test advanced timing optimization with no fields."""
        request_data = {
            "farm_context": {
                "fields": [],  # Empty fields
                "equipment_constraints": {
                    "available_equipment": ["field_sprayer"],
                    "capacity_per_day": 200,
                    "maintenance_windows": []
                },
                "labor_constraints": {
                    "available_hours_per_day": 10,
                    "skilled_operators": 2,
                    "peak_season_conflicts": []
                }
            },
            "optimization_goals": {
                "primary_goal": "nutrient_efficiency"
            },
            "timing_constraints": {
                "earliest_application": "2024-04-15",
                "latest_application": "2024-07-15"
            }
        }

        response = client.post(
            "/api/v1/fertilizer/timing-optimization",
            json=request_data
        )

        # Should handle gracefully
        assert response.status_code in [200, 400, 422]


class TestFertilizerCalendar:
    """Test suite for GET /calendar endpoint."""

    def test_calendar_generation_success(self):
        """Test successful calendar generation."""
        response = client.get(
            "/api/v1/fertilizer/calendar",
            params={
                "farm_id": "farm_001",
                "year": 2024,
                "include_weather": True,
                "format": "json"
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert data["farm_id"] == "farm_001"
        assert data["year"] == 2024
        assert "events" in data
        assert "weather_overlays" in data
        assert "crop_types" in data
        assert "total_applications" in data
        assert data["format"] == "json"
        assert "generated_at" in data

        # Verify events
        assert isinstance(data["events"], list)
        if len(data["events"]) > 0:
            event = data["events"][0]
            assert "event_id" in event
            assert "event_type" in event
            assert "event_date" in event
            assert "title" in event
            assert "description" in event

        # Verify weather overlays
        assert isinstance(data["weather_overlays"], list)

    def test_calendar_with_crop_filter(self):
        """Test calendar generation with crop type filter."""
        response = client.get(
            "/api/v1/fertilizer/calendar",
            params={
                "farm_id": "farm_001",
                "year": 2024,
                "crop_type": "corn",
                "include_weather": True
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Verify crop filter applied
        assert "corn" in data["crop_types"]

    def test_calendar_without_weather(self):
        """Test calendar generation without weather overlays."""
        response = client.get(
            "/api/v1/fertilizer/calendar",
            params={
                "farm_id": "farm_001",
                "year": 2024,
                "include_weather": False
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Verify no weather overlays
        assert len(data["weather_overlays"]) == 0

    def test_calendar_missing_farm_id(self):
        """Test calendar generation without required farm_id."""
        response = client.get(
            "/api/v1/fertilizer/calendar",
            params={"year": 2024}
        )

        # Should return 422 for missing required parameter
        assert response.status_code == 422

    def test_calendar_missing_year(self):
        """Test calendar generation without required year."""
        response = client.get(
            "/api/v1/fertilizer/calendar",
            params={"farm_id": "farm_001"}
        )

        # Should return 422 for missing required parameter
        assert response.status_code == 422


class TestApplicationWindows:
    """Test suite for GET /application-windows endpoint."""

    def test_application_windows_success(self):
        """Test successful application window analysis."""
        response = client.get(
            "/api/v1/fertilizer/application-windows",
            params={
                "field_id": "field_001",
                "start_date": "2024-05-01",
                "end_date": "2024-06-30",
                "fertilizer_type": "nitrogen"
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert data["field_id"] == "field_001"
        assert "analysis_period" in data
        assert data["fertilizer_type"] == "nitrogen"
        assert "windows" in data
        assert "optimal_windows" in data
        assert "weather_summary" in data
        assert "risk_summary" in data
        assert "generated_at" in data

        # Verify analysis period
        assert "start" in data["analysis_period"]
        assert "end" in data["analysis_period"]

        # Verify windows
        assert isinstance(data["windows"], list)
        if len(data["windows"]) > 0:
            window = data["windows"][0]
            assert "window_id" in window
            assert "start_date" in window
            assert "end_date" in window
            assert "optimal_date" in window
            assert "confidence_score" in window
            assert "weather_forecast" in window
            assert "soil_conditions" in window
            assert "crop_readiness" in window
            assert "equipment_available" in window
            assert "recommendation" in window

        # Verify weather summary
        assert "average_temperature_f" in data["weather_summary"]
        assert "average_precipitation_probability" in data["weather_summary"]
        assert "average_suitability" in data["weather_summary"]

        # Verify risk summary
        assert "overall_risk" in data["risk_summary"]

    def test_application_windows_without_fertilizer_type(self):
        """Test application window analysis without fertilizer type filter."""
        response = client.get(
            "/api/v1/fertilizer/application-windows",
            params={
                "field_id": "field_001",
                "start_date": "2024-05-01",
                "end_date": "2024-06-30"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["field_id"] == "field_001"

    def test_application_windows_invalid_date_format(self):
        """Test application window analysis with invalid date format."""
        response = client.get(
            "/api/v1/fertilizer/application-windows",
            params={
                "field_id": "field_001",
                "start_date": "05-01-2024",  # Invalid format
                "end_date": "2024-06-30"
            }
        )

        # Should return 400 for invalid date format
        assert response.status_code == 400

    def test_application_windows_end_before_start(self):
        """Test application window analysis with end date before start date."""
        response = client.get(
            "/api/v1/fertilizer/application-windows",
            params={
                "field_id": "field_001",
                "start_date": "2024-06-30",
                "end_date": "2024-05-01"  # Before start
            }
        )

        # Should return 400 for invalid date range
        assert response.status_code == 400

    def test_application_windows_missing_parameters(self):
        """Test application window analysis with missing required parameters."""
        response = client.get(
            "/api/v1/fertilizer/application-windows",
            params={"field_id": "field_001"}
        )

        # Should return 422 for missing required parameters
        assert response.status_code == 422


class TestAlertSubscription:
    """Test suite for POST /alerts/subscribe endpoint."""

    @pytest.fixture
    def sample_subscription_request(self):
        """Create sample alert subscription request."""
        return {
            "user_id": "user_001",
            "farm_id": "farm_001",
            "alert_preferences": {
                "timing_alerts": True,
                "weather_alerts": True,
                "equipment_alerts": True,
                "regulatory_alerts": True
            },
            "notification_channels": ["email", "sms"],
            "alert_frequency": "daily"
        }

    def test_alert_subscription_success(self, sample_subscription_request):
        """Test successful alert subscription."""
        response = client.post(
            "/api/v1/fertilizer/alerts/subscribe",
            json=sample_subscription_request
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "subscription_id" in data
        assert data["user_id"] == "user_001"
        assert data["farm_id"] == "farm_001"
        assert "alert_preferences" in data
        assert "notification_channels" in data
        assert data["alert_frequency"] == "daily"
        assert data["status"] == "active"
        assert "created_at" in data

        # Verify alert preferences
        prefs = data["alert_preferences"]
        assert prefs["timing_alerts"] == True
        assert prefs["weather_alerts"] == True
        assert prefs["equipment_alerts"] == True
        assert prefs["regulatory_alerts"] == True

        # Verify notification channels
        assert "email" in data["notification_channels"]
        assert "sms" in data["notification_channels"]

    def test_alert_subscription_invalid_channel(self):
        """Test alert subscription with invalid notification channel."""
        request_data = {
            "user_id": "user_001",
            "farm_id": "farm_001",
            "alert_preferences": {
                "timing_alerts": True,
                "weather_alerts": True,
                "equipment_alerts": True,
                "regulatory_alerts": True
            },
            "notification_channels": ["email", "invalid_channel"],
            "alert_frequency": "daily"
        }

        response = client.post(
            "/api/v1/fertilizer/alerts/subscribe",
            json=request_data
        )

        # Should return 400 for invalid channel
        assert response.status_code == 400

    def test_alert_subscription_invalid_frequency(self):
        """Test alert subscription with invalid frequency."""
        request_data = {
            "user_id": "user_001",
            "farm_id": "farm_001",
            "alert_preferences": {
                "timing_alerts": True,
                "weather_alerts": True,
                "equipment_alerts": True,
                "regulatory_alerts": True
            },
            "notification_channels": ["email"],
            "alert_frequency": "invalid_frequency"
        }

        response = client.post(
            "/api/v1/fertilizer/alerts/subscribe",
            json=request_data
        )

        # Should return 400 for invalid frequency
        assert response.status_code == 400

    def test_alert_subscription_push_notifications(self):
        """Test alert subscription with push notifications."""
        request_data = {
            "user_id": "user_001",
            "farm_id": "farm_001",
            "alert_preferences": {
                "timing_alerts": True,
                "weather_alerts": True,
                "equipment_alerts": False,
                "regulatory_alerts": False
            },
            "notification_channels": ["push"],
            "alert_frequency": "real-time"
        }

        response = client.post(
            "/api/v1/fertilizer/alerts/subscribe",
            json=request_data
        )

        assert response.status_code == 200
        data = response.json()
        assert "push" in data["notification_channels"]
        assert data["alert_frequency"] == "real-time"


class TestAlertManagement:
    """Test suite for GET /alerts/manage endpoint."""

    def test_alert_management_success(self):
        """Test successful alert management retrieval."""
        response = client.get(
            "/api/v1/fertilizer/alerts/manage",
            params={"user_id": "user_001"}
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert data["user_id"] == "user_001"
        assert "subscriptions" in data
        assert "active_alerts" in data
        assert "alert_history" in data
        assert "total_subscriptions" in data
        assert "total_active_alerts" in data
        assert "retrieved_at" in data

        # Verify subscriptions
        assert isinstance(data["subscriptions"], list)

        # Verify active alerts
        assert isinstance(data["active_alerts"], list)
        if len(data["active_alerts"]) > 0:
            alert = data["active_alerts"][0]
            assert "alert_id" in alert
            assert "alert_type" in alert
            assert "severity" in alert
            assert "title" in alert
            assert "message" in alert

        # Verify alert history
        assert isinstance(data["alert_history"], list)

    def test_alert_management_with_farm_filter(self):
        """Test alert management with farm filter."""
        response = client.get(
            "/api/v1/fertilizer/alerts/manage",
            params={
                "user_id": "user_001",
                "farm_id": "farm_001"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "user_001"
        assert data["farm_id"] == "farm_001"

    def test_alert_management_missing_user_id(self):
        """Test alert management without required user_id."""
        response = client.get("/api/v1/fertilizer/alerts/manage")

        # Should return 422 for missing required parameter
        assert response.status_code == 422


class TestHealthCheck:
    """Test suite for health check endpoint."""

    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/api/v1/fertilizer/health")

        assert response.status_code == 200
        data = response.json()

        assert data["service"] == "timing-routes"
        assert data["status"] == "healthy"
        assert "endpoints" in data
        assert "features" in data

        # Verify endpoints listed
        endpoints = data["endpoints"]
        assert "POST /api/v1/fertilizer/timing-optimization" in endpoints
        assert "GET /api/v1/fertilizer/calendar" in endpoints
        assert "GET /api/v1/fertilizer/application-windows" in endpoints
        assert "POST /api/v1/fertilizer/alerts/subscribe" in endpoints
        assert "GET /api/v1/fertilizer/alerts/manage" in endpoints

        # Verify features listed
        features = data["features"]
        assert "advanced_multi_field_optimization" in features
        assert "dynamic_calendar_generation" in features
        assert "real_time_window_analysis" in features
        assert "alert_subscription_management" in features


class TestIntegration:
    """Integration tests for timing routes."""

    def test_full_workflow(self):
        """Test complete workflow from optimization to alerts."""
        # Step 1: Advanced timing optimization
        optimization_request = {
            "farm_context": {
                "fields": [
                    {
                        "field_id": "field_001",
                        "crop": "corn",
                        "planting_date": "2024-05-01",
                        "soil_conditions": {"moisture": "adequate", "temperature": 55},
                        "previous_applications": []
                    }
                ],
                "equipment_constraints": {
                    "available_equipment": ["field_sprayer"],
                    "capacity_per_day": 200,
                    "maintenance_windows": []
                },
                "labor_constraints": {
                    "available_hours_per_day": 10,
                    "skilled_operators": 2,
                    "peak_season_conflicts": []
                }
            },
            "optimization_goals": {
                "primary_goal": "nutrient_efficiency",
                "weather_risk_tolerance": "moderate",
                "cost_priority": 0.7,
                "environmental_priority": 0.8
            },
            "timing_constraints": {
                "earliest_application": "2024-04-15",
                "latest_application": "2024-07-15",
                "restricted_periods": [],
                "regulatory_windows": []
            }
        }

        opt_response = client.post(
            "/api/v1/fertilizer/timing-optimization",
            json=optimization_request
        )
        assert opt_response.status_code == 200

        # Step 2: Generate calendar
        calendar_response = client.get(
            "/api/v1/fertilizer/calendar",
            params={"farm_id": "farm_001", "year": 2024}
        )
        assert calendar_response.status_code == 200

        # Step 3: Analyze application windows
        windows_response = client.get(
            "/api/v1/fertilizer/application-windows",
            params={
                "field_id": "field_001",
                "start_date": "2024-05-01",
                "end_date": "2024-06-30"
            }
        )
        assert windows_response.status_code == 200

        # Step 4: Subscribe to alerts
        subscription_request = {
            "user_id": "user_001",
            "farm_id": "farm_001",
            "alert_preferences": {
                "timing_alerts": True,
                "weather_alerts": True,
                "equipment_alerts": True,
                "regulatory_alerts": True
            },
            "notification_channels": ["email"],
            "alert_frequency": "daily"
        }

        sub_response = client.post(
            "/api/v1/fertilizer/alerts/subscribe",
            json=subscription_request
        )
        assert sub_response.status_code == 200

        # Step 5: Manage alerts
        manage_response = client.get(
            "/api/v1/fertilizer/alerts/manage",
            params={"user_id": "user_001"}
        )
        assert manage_response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
API Integration Tests for Soil pH Management System
Tests all API endpoints with various scenarios and error conditions.
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from datetime import datetime, date, timedelta
import json
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import app
from services.soil_ph_management_service import SoilTexture, AmendmentType

class TestPHManagementAPI:
    """Test API endpoints for pH management functionality."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def sample_soil_data(self):
        """Sample soil test data for API requests."""
        return {
            "ph": 5.8,
            "organic_matter_percent": 3.2,
            "phosphorus_ppm": 25,
            "potassium_ppm": 180,
            "test_date": "2024-03-15"
        }
    
    @pytest.fixture
    def acidic_soil_data(self):
        """Acidic soil test data."""
        return {
            "ph": 5.0,
            "organic_matter_percent": 2.1,
            "phosphorus_ppm": 12,
            "potassium_ppm": 95,
            "test_date": "2024-03-10"
        }
    
    @pytest.fixture
    def field_conditions(self):
        """Standard field conditions."""
        return {
            "soil_texture": "loam",
            "field_size_acres": 10.0,
            "tillage_practices": "conventional",
            "irrigation_type": "rainfed"
        }


class TestPHAnalysisEndpoint(TestPHManagementAPI):
    """Test /api/v1/ph/analyze endpoint."""
    
    def test_analyze_ph_success(self, client, sample_soil_data, field_conditions):
        """Test successful pH analysis."""
        request_data = {
            "farm_id": "test_farm",
            "field_id": "field_001",
            "crop_type": "corn",
            "soil_test_data": sample_soil_data,
            "field_conditions": field_conditions
        }
        
        response = client.post("/api/v1/ph/analyze", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "analysis" in data
        assert "recommendations" in data
        
        analysis = data["analysis"]
        assert analysis["current_ph"] == 5.8
        assert "ph_level" in analysis
        assert "target_ph" in analysis
        assert "nutrient_availability_impact" in analysis
        assert "crop_suitability_score" in analysis
        assert "management_priority" in analysis

    def test_analyze_ph_critical_conditions(self, client, field_conditions):
        """Test pH analysis for critical conditions."""
        critical_soil_data = {
            "ph": 4.2,
            "organic_matter_percent": 1.5,
            "phosphorus_ppm": 8,
            "potassium_ppm": 60,
            "test_date": "2024-03-15"
        }
        
        request_data = {
            "farm_id": "emergency_farm",
            "field_id": "critical_field",
            "crop_type": "corn",
            "soil_test_data": critical_soil_data,
            "field_conditions": field_conditions
        }
        
        response = client.post("/api/v1/ph/analyze", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        analysis = data["analysis"]
        assert analysis["current_ph"] == 4.2
        assert analysis["crop_suitability_score"] < 0.5
        assert data["recommendations"]["immediate_action_needed"] is True

    def test_analyze_ph_invalid_data(self, client, field_conditions):
        """Test pH analysis with invalid data."""
        invalid_soil_data = {
            "ph": 15.0,  # Invalid pH
            "organic_matter_percent": 3.0,
            "test_date": "2024-03-15"
        }
        
        request_data = {
            "farm_id": "test_farm",
            "field_id": "field_001",
            "crop_type": "corn",
            "soil_test_data": invalid_soil_data,
            "field_conditions": field_conditions
        }
        
        response = client.post("/api/v1/ph/analyze", json=request_data)
        
        assert response.status_code == 422  # Unprocessable Entity

    def test_analyze_ph_missing_fields(self, client):
        """Test pH analysis with missing required fields."""
        incomplete_request = {
            "farm_id": "test_farm",
            # Missing field_id, crop_type, and soil_test_data
        }
        
        response = client.post("/api/v1/ph/analyze", json=incomplete_request)
        
        assert response.status_code == 422


class TestLimeCalculatorEndpoint(TestPHManagementAPI):
    """Test /api/v1/ph/lime-calculator endpoint."""
    
    def test_lime_calculator_success(self, client, field_conditions):
        """Test successful lime requirement calculation."""
        request_data = {
            "current_ph": 5.5,
            "target_ph": 6.5,
            "soil_texture": "loam",
            "organic_matter_percent": 3.0,
            "field_size_acres": 15.0,
            "field_conditions": field_conditions
        }
        
        response = client.post("/api/v1/ph/lime-calculator", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "recommendations" in data
        assert "economic_analysis" in data
        
        recommendations = data["recommendations"]
        assert len(recommendations) > 0
        
        for rec in recommendations:
            assert "lime_type" in rec
            assert "application_rate_tons_per_acre" in rec
            assert "cost_per_acre" in rec
            assert "expected_ph_change" in rec

    def test_lime_calculator_with_buffer_ph(self, client, field_conditions):
        """Test lime calculator with buffer pH."""
        request_data = {
            "current_ph": 5.8,
            "target_ph": 6.5,
            "buffer_ph": 6.2,
            "soil_texture": "silt_loam",
            "organic_matter_percent": 3.5,
            "field_size_acres": 25.0,
            "field_conditions": field_conditions
        }
        
        response = client.post("/api/v1/ph/lime-calculator", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        # Buffer pH should provide more accurate recommendations
        assert data["calculation_method"] == "buffer_ph"

    def test_lime_calculator_no_lime_needed(self, client, field_conditions):
        """Test lime calculator when no lime is needed."""
        request_data = {
            "current_ph": 6.5,
            "target_ph": 6.5,
            "soil_texture": "loam",
            "organic_matter_percent": 3.0,
            "field_size_acres": 10.0,
            "field_conditions": field_conditions
        }
        
        response = client.post("/api/v1/ph/lime-calculator", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert len(data["recommendations"]) == 0
        assert "no_treatment_needed" in data["message"]

    def test_lime_calculator_invalid_ph_range(self, client):
        """Test lime calculator with invalid pH values."""
        request_data = {
            "current_ph": 2.0,  # Too low
            "target_ph": 6.5,
            "soil_texture": "loam",
            "organic_matter_percent": 3.0
        }
        
        response = client.post("/api/v1/ph/lime-calculator", json=request_data)
        
        assert response.status_code == 422


class TestCropRequirementsEndpoint(TestPHManagementAPI):
    """Test /api/v1/ph/crop-requirements endpoint."""
    
    def test_crop_requirements_single_crop(self, client):
        """Test crop pH requirements for single crop."""
        response = client.get("/api/v1/ph/crop-requirements?crop_types=corn")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "requirements" in data
        assert "corn" in data["requirements"]
        
        corn_req = data["requirements"]["corn"]
        assert "optimal_ph_range" in corn_req
        assert "acceptable_ph_range" in corn_req
        assert "yield_impact_curve" in corn_req

    def test_crop_requirements_multiple_crops(self, client):
        """Test crop pH requirements for multiple crops."""
        response = client.get("/api/v1/ph/crop-requirements?crop_types=corn&crop_types=soybean&crop_types=wheat")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        requirements = data["requirements"]
        
        assert "corn" in requirements
        assert "soybean" in requirements
        assert "wheat" in requirements
        
        # Each crop should have complete requirement data
        for crop in ["corn", "soybean", "wheat"]:
            crop_req = requirements[crop]
            assert "optimal_ph_range" in crop_req
            assert "tolerance_range" in crop_req

    def test_crop_requirements_unknown_crop(self, client):
        """Test crop requirements for unknown crop."""
        response = client.get("/api/v1/ph/crop-requirements?crop_types=unknown_crop")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should provide default requirements or indicate unknown
        assert data["success"] is True
        if "unknown_crop" in data["requirements"]:
            assert "default_used" in data["requirements"]["unknown_crop"]


class TestMonitoringEndpoints(TestPHManagementAPI):
    """Test pH monitoring related endpoints."""
    
    def test_setup_monitoring(self, client):
        """Test pH monitoring setup."""
        request_data = {
            "farm_id": "test_farm",
            "field_id": "field_001",
            "monitoring_frequency": "quarterly",
            "alert_thresholds": {
                "critical_low": 5.0,
                "warning_low": 5.5,
                "warning_high": 7.5,
                "critical_high": 8.0
            }
        }
        
        response = client.post("/api/v1/ph/monitor", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "monitoring_schedule" in data
        assert "next_test_date" in data

    def test_ph_trends_analysis(self, client):
        """Test pH trends analysis."""
        response = client.get("/api/v1/ph/trends?farm_id=test_farm&field_id=field_001&months=12")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        if "trends" in data:
            trends = data["trends"]
            assert "trend_direction" in trends
            assert "annual_change_rate" in trends

    def test_generate_ph_alerts(self, client, acidic_soil_data, field_conditions):
        """Test pH alert generation."""
        request_data = {
            "farm_id": "test_farm",
            "field_id": "field_001",
            "current_conditions": {
                "ph": 4.8,
                "crop_type": "corn",
                "soil_data": acidic_soil_data,
                "field_conditions": field_conditions
            }
        }
        
        response = client.post("/api/v1/ph/alerts", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "alerts" in data
        
        if len(data["alerts"]) > 0:
            for alert in data["alerts"]:
                assert "alert_type" in alert
                assert "severity" in alert
                assert "message" in alert
                assert "recommended_action" in alert


class TestDashboardEndpoint(TestPHManagementAPI):
    """Test pH management dashboard endpoint."""
    
    def test_dashboard_data(self, client):
        """Test pH management dashboard data retrieval."""
        response = client.get("/api/v1/ph/dashboard?farm_id=test_farm")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "summary" in data
        assert "field_status" in data
        assert "recommendations" in data
        
        summary = data["summary"]
        assert "total_fields" in summary
        assert "fields_needing_attention" in summary
        assert "average_ph" in summary

    def test_dashboard_field_specific(self, client):
        """Test dashboard data for specific field."""
        response = client.get("/api/v1/ph/dashboard?farm_id=test_farm&field_id=field_001")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        if "field_details" in data:
            field_details = data["field_details"]
            assert "current_ph" in field_details
            assert "last_test_date" in field_details


class TestTreatmentPlanEndpoint(TestPHManagementAPI):
    """Test treatment plan creation and tracking."""
    
    def test_create_treatment_plan(self, client, sample_soil_data, field_conditions):
        """Test treatment plan creation."""
        request_data = {
            "farm_id": "test_farm",
            "field_id": "field_001",
            "crop_type": "corn",
            "soil_data": sample_soil_data,
            "field_conditions": field_conditions,
            "management_goals": ["yield_optimization", "nutrient_efficiency"]
        }
        
        response = client.post("/api/v1/ph/treatment-plan", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "treatment_plan" in data
        
        plan = data["treatment_plan"]
        assert "plan_id" in plan
        assert "recommendations" in plan
        assert "timeline" in plan
        assert "economic_analysis" in plan

    def test_track_treatment_application(self, client):
        """Test treatment application tracking."""
        request_data = {
            "plan_id": "test_plan_001",
            "farm_id": "test_farm",
            "field_id": "field_001",
            "treatment_type": "agricultural_lime",
            "application_rate": 2.5,
            "application_date": "2024-03-20",
            "application_method": "broadcast",
            "notes": "Applied before spring tillage"
        }
        
        response = client.post("/api/v1/ph/track-treatment", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "treatment_record" in data
        assert "next_monitoring_date" in data


class TestEconomicAnalysisEndpoint(TestPHManagementAPI):
    """Test economic analysis endpoints."""
    
    def test_economic_analysis(self, client, sample_soil_data, field_conditions):
        """Test pH management economic analysis."""
        response = client.get(
            "/api/v1/ph/economics"
            "?farm_id=test_farm"
            "&field_id=field_001"
            "&crop_type=corn"
            "&current_ph=5.8"
            "&target_ph=6.5"
            "&field_size_acres=25.0"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "economic_analysis" in data
        
        analysis = data["economic_analysis"]
        assert "total_treatment_cost" in analysis
        assert "expected_yield_benefit" in analysis
        assert "net_benefit" in analysis
        assert "benefit_cost_ratio" in analysis
        assert "payback_period_years" in analysis

    def test_cost_comparison(self, client):
        """Test cost comparison between different treatments."""
        response = client.get(
            "/api/v1/ph/economics"
            "?comparison_mode=true"
            "&current_ph=5.5"
            "&target_ph=6.5"
            "&soil_texture=loam"
            "&field_size_acres=20.0"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "treatment_comparisons" in data
        
        comparisons = data["treatment_comparisons"]
        assert len(comparisons) > 1  # Should compare multiple treatment options
        
        for comparison in comparisons:
            assert "treatment_type" in comparison
            assert "total_cost" in comparison
            assert "cost_per_acre" in comparison


class TestReportsEndpoint(TestPHManagementAPI):
    """Test pH management reporting endpoints."""
    
    def test_generate_ph_report(self, client):
        """Test pH management report generation."""
        response = client.get(
            "/api/v1/ph/reports"
            "?farm_id=test_farm"
            "&report_type=comprehensive"
            "&start_date=2023-01-01"
            "&end_date=2024-03-31"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "report" in data
        
        report = data["report"]
        assert "report_id" in report
        assert "farm_summary" in report
        assert "field_analyses" in report
        assert "recommendations_summary" in report

    def test_generate_field_specific_report(self, client):
        """Test field-specific pH report."""
        response = client.get(
            "/api/v1/ph/reports"
            "?farm_id=test_farm"
            "&field_id=field_001"
            "&report_type=field_detail"
            "&include_trends=true"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        if "report" in data:
            report = data["report"]
            assert "field_id" in report
            assert "ph_history" in report


class TestAPIPerformanceAndLoad(TestPHManagementAPI):
    """Test API performance under various load conditions."""
    
    def test_concurrent_analysis_requests(self, client, sample_soil_data, field_conditions):
        """Test concurrent pH analysis requests."""
        import concurrent.futures
        import time
        
        def make_request(client, request_data):
            return client.post("/api/v1/ph/analyze", json=request_data)
        
        # Prepare multiple requests
        requests = []
        for i in range(10):
            request_data = {
                "farm_id": f"test_farm_{i}",
                "field_id": f"field_{i:03d}",
                "crop_type": "corn",
                "soil_test_data": sample_soil_data.copy(),
                "field_conditions": field_conditions
            }
            requests.append(request_data)
        
        start_time = time.time()
        
        # Execute concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, client, req) for req in requests]
            responses = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete 10 requests in reasonable time
        assert total_time < 10.0
        assert len(responses) == 10
        assert all(resp.status_code == 200 for resp in responses)

    def test_large_batch_lime_calculations(self, client, field_conditions):
        """Test batch lime calculations for large dataset."""
        # Simulate processing multiple fields
        batch_requests = []
        for i in range(20):
            ph_value = 5.0 + (i * 0.1)  # pH from 5.0 to 6.9
            request_data = {
                "current_ph": ph_value,
                "target_ph": 6.5,
                "soil_texture": "loam",
                "organic_matter_percent": 3.0,
                "field_size_acres": 10.0 + i,
                "field_conditions": field_conditions
            }
            batch_requests.append(request_data)
        
        start_time = time.time()
        
        # Process batch
        responses = []
        for request_data in batch_requests:
            response = client.post("/api/v1/ph/lime-calculator", json=request_data)
            responses.append(response)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should process 20 calculations efficiently
        assert processing_time < 5.0
        assert all(resp.status_code == 200 for resp in responses)
        
        # Verify response quality
        for response in responses[:5]:  # Check first 5 responses
            data = response.json()
            assert data["success"] is True


class TestAPIErrorHandling(TestPHManagementAPI):
    """Test API error handling and edge cases."""
    
    def test_malformed_json_request(self, client):
        """Test handling of malformed JSON requests."""
        malformed_json = '{"farm_id": "test", "invalid_json":'
        
        response = client.post(
            "/api/v1/ph/analyze",
            data=malformed_json,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422

    def test_missing_content_type(self, client):
        """Test handling of requests without proper content type."""
        response = client.post("/api/v1/ph/analyze", data="some data")
        
        assert response.status_code in [400, 422, 415]  # Bad Request or Unsupported Media Type

    def test_extremely_large_request(self, client, field_conditions):
        """Test handling of extremely large request payloads."""
        # Create large field conditions data
        large_field_conditions = field_conditions.copy()
        large_field_conditions["large_data"] = "x" * 10000  # 10KB of data
        
        request_data = {
            "farm_id": "test_farm",
            "field_id": "field_001",
            "crop_type": "corn",
            "soil_test_data": {
                "ph": 6.0,
                "organic_matter_percent": 3.0,
                "test_date": "2024-03-15"
            },
            "field_conditions": large_field_conditions
        }
        
        response = client.post("/api/v1/ph/analyze", json=request_data)
        
        # Should either process successfully or return appropriate error
        assert response.status_code in [200, 413, 422]  # OK or Payload Too Large

    def test_rate_limiting_simulation(self, client, sample_soil_data, field_conditions):
        """Test rapid successive requests (simulating rate limiting scenarios)."""
        request_data = {
            "farm_id": "rate_test_farm",
            "field_id": "rate_test_field",
            "crop_type": "corn",
            "soil_test_data": sample_soil_data,
            "field_conditions": field_conditions
        }
        
        # Make 50 rapid requests
        responses = []
        for i in range(50):
            response = client.post("/api/v1/ph/analyze", json=request_data)
            responses.append(response)
        
        # Most requests should succeed (unless rate limiting is implemented)
        success_count = sum(1 for resp in responses if resp.status_code == 200)
        assert success_count >= 45  # Allow for some failures due to rate limiting


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
"""
Integration test for complete soil pH management system.
Tests end-to-end workflows, API endpoints, and system integration.
"""
import asyncio
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, date
import json

# Import the FastAPI app and services
from src.api.ph_management_routes import router
from src.services.soil_ph_management_service import SoilPHManagementService
from src.models.agricultural_models import SoilTestData

# Create test FastAPI app
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)

client = TestClient(app)

class TestPHManagementIntegration:
    """Integration tests for pH management system."""
    
    def test_ph_analysis_endpoint(self):
        """Test pH analysis API endpoint."""
        request_data = {
            "farm_id": "test_farm_001",
            "field_id": "north_field",
            "crop_type": "corn",
            "soil_test_data": {
                "ph": 5.8,
                "organic_matter_percent": 3.2,
                "phosphorus_ppm": 25,
                "potassium_ppm": 180,
                "test_date": "2024-03-15"
            },
            "field_conditions": {
                "soil_texture": "silt_loam",
                "annual_rainfall": 32,
                "previous_crop": "soybean"
            }
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
        
        # Should recommend action for pH 5.8 with corn
        recommendations = data["recommendations"]
        assert "immediate_action_needed" in recommendations
        assert "next_steps" in recommendations
    
    def test_lime_calculator_endpoint(self):
        """Test lime calculator API endpoint."""
        request_data = {
            "current_ph": 5.8,
            "target_ph": 6.5,
            "buffer_ph": 6.2,
            "soil_texture": "silt_loam",
            "organic_matter_percent": 3.2,
            "field_size_acres": 25.5,
            "field_conditions": {
                "drainage": "well_drained",
                "slope": "gentle"
            }
        }
        
        response = client.post("/api/v1/ph/lime-calculator", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "lime_requirements" in data
        assert "calculation_method" in data
        assert "confidence" in data
        
        lime_reqs = data["lime_requirements"]
        assert len(lime_reqs) > 0
        
        # Check first recommendation structure
        first_rec = lime_reqs[0]
        required_fields = [
            "lime_type", "application_rate_tons_per_acre", "application_method",
            "application_timing", "cost_per_acre", "expected_ph_change",
            "time_to_effectiveness", "notes"
        ]
        
        for field in required_fields:
            assert field in first_rec
        
        # Validate agricultural reasonableness
        assert 0.5 <= first_rec["application_rate_tons_per_acre"] <= 6.0
        assert first_rec["cost_per_acre"] > 0
        assert first_rec["expected_ph_change"] > 0
    
    def test_crop_requirements_endpoint(self):
        """Test crop pH requirements API endpoint."""
        response = client.get(
            "/api/v1/ph/crop-requirements",
            params={"crop_types": ["corn", "soybean", "wheat", "alfalfa"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "crop_requirements" in data
        
        requirements = data["crop_requirements"]
        
        # Check all requested crops are included
        for crop in ["corn", "soybean", "wheat", "alfalfa"]:
            assert crop in requirements
            
            crop_req = requirements[crop]
            assert "optimal_range" in crop_req
            assert "acceptable_range" in crop_req
            assert "critical_minimum" in crop_req
            assert "critical_maximum" in crop_req
            assert "yield_impact_curve" in crop_req
            assert "specific_sensitivities" in crop_req
            
            # Validate ranges
            opt_range = crop_req["optimal_range"]
            acc_range = crop_req["acceptable_range"]
            
            assert opt_range["min"] <= opt_range["max"]
            assert acc_range["min"] <= opt_range["min"]
            assert opt_range["max"] <= acc_range["max"]
    
    def test_monitoring_setup_endpoint(self):
        """Test pH monitoring setup endpoint."""
        request_data = {
            "farm_id": "test_farm_001",
            "field_id": "north_field",
            "monitoring_frequency": "annual",
            "alert_thresholds": {
                "critical_low": 5.0,
                "critical_high": 8.0,
                "warning_low": 5.5,
                "warning_high": 7.5
            },
            "crop_rotation_schedule": [
                {"year": 2024, "crop": "corn"},
                {"year": 2025, "crop": "soybean"}
            ]
        }
        
        response = client.post("/api/v1/ph/monitor", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "monitoring_plan" in data
        
        plan = data["monitoring_plan"]
        assert plan["farm_id"] == "test_farm_001"
        assert plan["field_id"] == "north_field"
        assert plan["frequency"] == "annual"
        assert "next_test_date" in plan
        assert "parameters_to_test" in plan
    
    def test_ph_trends_endpoint(self):
        """Test pH trends analysis endpoint."""
        response = client.get(
            "/api/v1/ph/trends",
            params={
                "farm_id": "test_farm_001",
                "field_id": "north_field",
                "start_date": "2021-01-01",
                "end_date": "2024-03-15"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "trends" in data
        assert "recommendations" in data
        
        trends = data["trends"]
        assert "trend_direction" in trends
        assert "annual_change_rate" in trends
        assert "current_ph" in trends
        assert "confidence" in trends
        
        assert trends["trend_direction"] in ["increasing", "decreasing", "stable"]
        assert isinstance(trends["annual_change_rate"], (int, float))
    
    def test_dashboard_endpoint(self):
        """Test pH monitoring dashboard endpoint."""
        response = client.get(
            "/api/v1/ph/dashboard",
            params={"farm_id": "test_farm_001"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "dashboard" in data
        
        dashboard = data["dashboard"]
        assert "farm_summary" in dashboard
        assert "field_status" in dashboard
        assert "upcoming_tasks" in dashboard
        
        # Validate farm summary
        summary = dashboard["farm_summary"]
        assert "total_fields" in summary
        assert "fields_needing_attention" in summary
        assert "average_ph" in summary
        assert "last_updated" in summary
        
        # Validate field status
        field_status = dashboard["field_status"]
        assert isinstance(field_status, list)
        
        if field_status:
            field = field_status[0]
            assert "field_id" in field
            assert "current_ph" in field
            assert "status" in field
            assert "priority" in field
    
    def test_treatment_plan_endpoint(self):
        """Test pH treatment plan generation endpoint."""
        request_data = {
            "treatment_goals": {
                "target_ph": 6.5,
                "timeline_months": 12,
                "budget_per_acre": 150.0
            }
        }
        
        response = client.post(
            "/api/v1/ph/treatment-plan",
            params={
                "farm_id": "test_farm_001",
                "field_id": "north_field",
                "crop_type": "corn"
            },
            json=request_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "treatment_plan" in data
        
        plan = data["treatment_plan"]
        assert "plan_id" in plan
        assert "treatment_phases" in plan
        assert "success_metrics" in plan
        
        # Validate treatment phases
        phases = plan["treatment_phases"]
        assert len(phases) > 0
        
        for phase in phases:
            assert "phase" in phase
            assert "actions" in phase
            assert "timeline" in phase
    
    def test_economics_endpoint(self):
        """Test pH management economics endpoint."""
        response = client.get(
            "/api/v1/ph/economics",
            params={
                "farm_id": "test_farm_001",
                "field_id": "north_field",
                "crop_type": "corn",
                "treatment_scenario": "recommended"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "economics" in data
        
        economics = data["economics"]
        assert "cost_analysis" in economics
        assert "benefit_analysis" in economics
        assert "roi_analysis" in economics
        
        # Validate cost analysis
        costs = economics["cost_analysis"]
        assert "lime_cost_per_acre" in costs
        assert "application_cost_per_acre" in costs
        assert "total_treatment_cost" in costs
        
        # Validate ROI analysis
        roi = economics["roi_analysis"]
        assert "net_benefit" in roi
        assert "benefit_cost_ratio" in roi
        assert "payback_period_years" in roi
        assert "roi_percent" in roi

class TestPHManagementWorkflows:
    """Test complete pH management workflows."""
    
    def test_new_field_ph_assessment_workflow(self):
        """Test complete workflow for new field pH assessment."""
        # Step 1: Analyze pH
        analysis_request = {
            "farm_id": "new_farm_001",
            "field_id": "new_field_001",
            "crop_type": "corn",
            "soil_test_data": {
                "ph": 5.6,
                "organic_matter_percent": 2.8,
                "phosphorus_ppm": 18,
                "potassium_ppm": 145,
                "test_date": "2024-03-20"
            }
        }
        
        analysis_response = client.post("/api/v1/ph/analyze", json=analysis_request)
        assert analysis_response.status_code == 200
        
        analysis_data = analysis_response.json()
        assert analysis_data["success"] is True
        
        # Step 2: Calculate lime requirements if needed
        if analysis_data["recommendations"]["immediate_action_needed"]:
            lime_request = {
                "current_ph": 5.6,
                "target_ph": 6.5,
                "soil_texture": "loam",
                "organic_matter_percent": 2.8,
                "field_size_acres": 40.0
            }
            
            lime_response = client.post("/api/v1/ph/lime-calculator", json=lime_request)
            assert lime_response.status_code == 200
            
            lime_data = lime_response.json()
            assert lime_data["success"] is True
            assert len(lime_data["lime_requirements"]) > 0
        
        # Step 3: Set up monitoring
        monitoring_request = {
            "farm_id": "new_farm_001",
            "field_id": "new_field_001",
            "monitoring_frequency": "annual",
            "alert_thresholds": {
                "critical_low": 5.0,
                "critical_high": 8.0
            }
        }
        
        monitoring_response = client.post("/api/v1/ph/monitor", json=monitoring_request)
        assert monitoring_response.status_code == 200
        
        monitoring_data = monitoring_response.json()
        assert monitoring_data["success"] is True
    
    def test_critical_ph_emergency_workflow(self):
        """Test workflow for critical pH emergency situation."""
        # Critical acidic soil scenario
        critical_analysis_request = {
            "farm_id": "emergency_farm",
            "field_id": "critical_field",
            "crop_type": "soybean",
            "soil_test_data": {
                "ph": 4.9,
                "organic_matter_percent": 1.8,
                "phosphorus_ppm": 8,
                "potassium_ppm": 75,
                "test_date": "2024-03-22"
            },
            "field_conditions": {
                "soil_texture": "sandy_loam",
                "drainage": "well_drained",
                "previous_crop": "corn"
            }
        }
        
        # Analyze critical situation
        response = client.post("/api/v1/ph/analyze", json=critical_analysis_request)
        assert response.status_code == 200
        
        data = response.json()
        analysis = data["analysis"]
        
        # Should be high or critical priority
        assert analysis["management_priority"] in ["high", "critical"]
        assert data["recommendations"]["immediate_action_needed"] is True
        
        # Get emergency lime recommendations
        emergency_lime_request = {
            "current_ph": 4.9,
            "target_ph": 6.0,  # Conservative target for emergency
            "soil_texture": "sandy_loam",
            "organic_matter_percent": 1.8,
            "field_size_acres": 15.0
        }
        
        lime_response = client.post("/api/v1/ph/lime-calculator", json=emergency_lime_request)
        assert lime_response.status_code == 200
        
        lime_data = lime_response.json()
        lime_requirements = lime_data["lime_requirements"]
        
        # Should have fast-acting lime options
        lime_types = [req["lime_type"] for req in lime_requirements]
        assert "hydrated_lime" in lime_types or "agricultural_limestone" in lime_types
        
        # Generate treatment plan
        treatment_response = client.post(
            "/api/v1/ph/treatment-plan",
            params={
                "farm_id": "emergency_farm",
                "field_id": "critical_field",
                "crop_type": "soybean"
            },
            json={"treatment_goals": {"target_ph": 6.0, "timeline_months": 6}}
        )
        
        assert treatment_response.status_code == 200
        treatment_data = treatment_response.json()
        
        # Should have immediate phase
        phases = treatment_data["treatment_plan"]["treatment_phases"]
        phase_names = [phase["phase"] for phase in phases]
        assert "immediate" in phase_names
    
    def test_alkaline_soil_management_workflow(self):
        """Test workflow for alkaline soil management."""
        alkaline_request = {
            "farm_id": "alkaline_farm",
            "field_id": "alkaline_field",
            "crop_type": "corn",
            "soil_test_data": {
                "ph": 8.3,
                "organic_matter_percent": 2.5,
                "phosphorus_ppm": 35,
                "potassium_ppm": 200,
                "test_date": "2024-03-18"
            },
            "field_conditions": {
                "soil_texture": "clay_loam",
                "calcium_carbonate": "present",
                "irrigation_water_ph": 7.8
            }
        }
        
        # Analyze alkaline soil
        response = client.post("/api/v1/ph/analyze", json=alkaline_request)
        assert response.status_code == 200
        
        data = response.json()
        analysis = data["analysis"]
        
        # Should detect alkaline conditions
        assert analysis["current_ph"] == 8.3
        assert analysis["alkalinity_risk"] in ["moderate", "high"]
        
        # Alkaline soils typically don't use lime calculator
        # Instead, would need sulfur or other acidifying treatments
        
        # Check economics for alkaline management
        economics_response = client.get(
            "/api/v1/ph/economics",
            params={
                "farm_id": "alkaline_farm",
                "field_id": "alkaline_field",
                "crop_type": "corn",
                "treatment_scenario": "alkaline_management"
            }
        )
        
        assert economics_response.status_code == 200
        economics_data = economics_response.json()
        assert economics_data["success"] is True

class TestPHManagementPerformance:
    """Test performance and scalability of pH management system."""
    
    def test_multiple_field_analysis_performance(self):
        """Test performance with multiple field analyses."""
        import time
        
        # Simulate analyzing 10 fields
        start_time = time.time()
        
        for i in range(10):
            request_data = {
                "farm_id": f"perf_farm_{i}",
                "field_id": f"field_{i:03d}",
                "crop_type": "corn",
                "soil_test_data": {
                    "ph": 5.5 + (i * 0.2),  # Varying pH values
                    "organic_matter_percent": 2.5 + (i * 0.1),
                    "phosphorus_ppm": 20 + i,
                    "potassium_ppm": 150 + (i * 5),
                    "test_date": "2024-03-15"
                }
            }
            
            response = client.post("/api/v1/ph/analyze", json=request_data)
            assert response.status_code == 200
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete 10 analyses in reasonable time
        assert total_time < 10.0  # Less than 10 seconds
        print(f"10 pH analyses completed in {total_time:.2f} seconds")
    
    def test_lime_calculator_performance(self):
        """Test lime calculator performance with various scenarios."""
        import time
        
        test_scenarios = [
            {"current_ph": 5.2, "target_ph": 6.5, "soil_texture": "sand"},
            {"current_ph": 5.8, "target_ph": 6.8, "soil_texture": "loam"},
            {"current_ph": 5.0, "target_ph": 7.0, "soil_texture": "clay"},
            {"current_ph": 6.2, "target_ph": 6.8, "soil_texture": "silt_loam"},
            {"current_ph": 4.8, "target_ph": 6.0, "soil_texture": "sandy_loam"}
        ]
        
        start_time = time.time()
        
        for scenario in test_scenarios:
            request_data = {
                **scenario,
                "organic_matter_percent": 3.0,
                "field_size_acres": 25.0
            }
            
            response = client.post("/api/v1/ph/lime-calculator", json=request_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert len(data["lime_requirements"]) > 0
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete all calculations quickly
        assert total_time < 5.0  # Less than 5 seconds
        print(f"5 lime calculations completed in {total_time:.2f} seconds")

class TestPHManagementErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_ph_values(self):
        """Test handling of invalid pH values."""
        # pH too low
        invalid_request = {
            "farm_id": "test_farm",
            "field_id": "test_field",
            "crop_type": "corn",
            "soil_test_data": {
                "ph": 2.5,  # Invalid - too low
                "organic_matter_percent": 3.0,
                "test_date": "2024-03-15"
            }
        }
        
        response = client.post("/api/v1/ph/analyze", json=invalid_request)
        # Should handle gracefully or return validation error
        assert response.status_code in [200, 400, 422]
        
        # pH too high
        invalid_request["soil_test_data"]["ph"] = 12.0  # Invalid - too high
        response = client.post("/api/v1/ph/analyze", json=invalid_request)
        assert response.status_code in [200, 400, 422]
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields."""
        incomplete_request = {
            "farm_id": "test_farm",
            "field_id": "test_field",
            # Missing crop_type and soil_test_data
        }
        
        response = client.post("/api/v1/ph/analyze", json=incomplete_request)
        assert response.status_code == 422  # Validation error
    
    def test_invalid_crop_type(self):
        """Test handling of invalid crop types."""
        request_with_invalid_crop = {
            "farm_id": "test_farm",
            "field_id": "test_field",
            "crop_type": "invalid_crop_xyz",
            "soil_test_data": {
                "ph": 6.0,
                "organic_matter_percent": 3.0,
                "test_date": "2024-03-15"
            }
        }
        
        response = client.post("/api/v1/ph/analyze", json=request_with_invalid_crop)
        # Should handle gracefully by using default crop requirements
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True

if __name__ == "__main__":
    # Run integration tests
    print("Running pH Management Integration Tests...")
    
    # Test basic functionality
    test_integration = TestPHManagementIntegration()
    test_integration.test_ph_analysis_endpoint()
    test_integration.test_lime_calculator_endpoint()
    test_integration.test_crop_requirements_endpoint()
    
    # Test workflows
    test_workflows = TestPHManagementWorkflows()
    test_workflows.test_new_field_ph_assessment_workflow()
    test_workflows.test_critical_ph_emergency_workflow()
    
    # Test performance
    test_performance = TestPHManagementPerformance()
    test_performance.test_multiple_field_analysis_performance()
    test_performance.test_lime_calculator_performance()
    
    print("All pH Management Integration Tests Completed Successfully!")
"""
Basic Comprehensive Testing Suite for Fertilizer Application Service
TICKET-023_fertilizer-application-method-11.1

This module provides comprehensive testing coverage for core components
of the fertilizer application service to achieve 80%+ coverage.
"""

import pytest
import asyncio
import time
import json
import os
import sys
from typing import Dict, List, Any, Optional
from unittest.mock import AsyncMock, patch, MagicMock, Mock
from fastapi.testclient import TestClient
from concurrent.futures import ThreadPoolExecutor
import statistics
import numpy as np
from datetime import datetime, timedelta

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import core service modules
from src.main_minimal import app
from src.services.application_method_service import ApplicationMethodService
from src.services.equipment_assessment_service import EquipmentAssessmentService
from src.services.cost_analysis_service import CostAnalysisService
from src.services.guidance_service import GuidanceService
from src.services.decision_support_service import DecisionSupportService
from src.services.comparison_service import MethodComparisonService
from src.services.algorithm_validation_service import AlgorithmValidationService

# Import all models
from src.models.application_models import (
    ApplicationRequest, ApplicationResponse, FieldConditions, 
    CropRequirements, FertilizerSpecification, EquipmentSpecification,
    ApplicationMethod, ApplicationMethodType, FertilizerForm, EquipmentType,
    GuidanceRequest, GuidanceResponse
)
from src.models.equipment_models import Equipment, EquipmentCategory, EquipmentStatus


class TestDataFactory:
    """Factory for creating test data."""
    
    @staticmethod
    def create_field_conditions() -> FieldConditions:
        """Create test field conditions."""
        return FieldConditions(
            field_size_acres=40.0,
            soil_type="clay_loam",
            drainage_class="moderate",
            slope_percent=2.5,
            irrigation_available=True,
            field_shape="rectangular",
            access_roads=["main_road", "field_access"]
        )
    
    @staticmethod
    def create_crop_requirements() -> CropRequirements:
        """Create test crop requirements."""
        return CropRequirements(
            crop_type="corn",
            growth_stage="V6",
            target_yield=180.0,
            yield_goal_bushels_per_acre=180.0,
            nutrient_requirements={"nitrogen": 200.0, "phosphorus": 80.0, "potassium": 150.0},
            application_timing_preferences=["pre_plant", "side_dress"],
            timing_requirements={"optimal_window": "spring", "flexibility": "high"}
        )
    
    @staticmethod
    def create_fertilizer_specification() -> FertilizerSpecification:
        """Create test fertilizer specification."""
        return FertilizerSpecification(
            fertilizer_type="urea",
            npk_ratio="46-0-0",
            form=FertilizerForm.GRANULAR,
            solubility=95.0,
            release_rate="immediate",
            cost_per_unit=0.45,
            unit="lb"
        )
    
    @staticmethod
    def create_equipment_specification() -> EquipmentSpecification:
        """Create test equipment specification."""
        return EquipmentSpecification(
            equipment_type=EquipmentType.BROADCASTER,
            capacity_tons=10.0,
            application_width_feet=60.0,
            speed_mph=8.0,
            precision_level="high",
            maintenance_status="good"
        )
    
    @staticmethod
    def create_application_request() -> ApplicationRequest:
        """Create test application request."""
        return ApplicationRequest(
            field_conditions=TestDataFactory.create_field_conditions(),
            crop_requirements=TestDataFactory.create_crop_requirements(),
            fertilizer_specification=TestDataFactory.create_fertilizer_specification(),
            available_equipment=[TestDataFactory.create_equipment_specification()],
            application_goals=["maximize_yield", "minimize_cost"],
            budget_limit=1000.0
        )


class TestApplicationMethodServiceComprehensive:
    """Comprehensive tests for ApplicationMethodService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance."""
        return ApplicationMethodService()
    
    @pytest.fixture
    def test_request(self):
        """Create test request."""
        return TestDataFactory.create_application_request()
    
    def test_service_initialization(self, service):
        """Test service initialization."""
        assert service is not None
        assert hasattr(service, 'analyze_field_conditions')
        assert hasattr(service, 'analyze_crop_requirements')
        assert hasattr(service, 'analyze_fertilizer_specification')
        assert hasattr(service, 'analyze_equipment')
        assert hasattr(service, 'score_methods')
        assert hasattr(service, 'generate_recommendations')
    
    @pytest.mark.asyncio
    async def test_field_conditions_analysis(self, service, test_request):
        """Test field conditions analysis."""
        field_analysis = await service.analyze_field_conditions(test_request.field_conditions)
        
        assert isinstance(field_analysis, dict)
        assert 'field_size_category' in field_analysis
        assert 'soil_suitability' in field_analysis
        assert 'drainage_impact' in field_analysis
        assert 'slope_considerations' in field_analysis
        assert 'irrigation_availability' in field_analysis
        assert 'access_constraints' in field_analysis
    
    @pytest.mark.asyncio
    async def test_crop_requirements_analysis(self, service, test_request):
        """Test crop requirements analysis."""
        crop_analysis = await service.analyze_crop_requirements(test_request.crop_requirements)
        
        assert isinstance(crop_analysis, dict)
        assert 'crop_type' in crop_analysis
        assert 'growth_stage' in crop_analysis
        assert 'nutrient_timing' in crop_analysis
        assert 'yield_target' in crop_analysis
        assert 'nutrient_demand' in crop_analysis
        assert 'application_timing_preferences' in crop_analysis
    
    @pytest.mark.asyncio
    async def test_fertilizer_specification_analysis(self, service, test_request):
        """Test fertilizer specification analysis."""
        fertilizer_analysis = await service.analyze_fertilizer_specification(test_request.fertilizer_specification)
        
        assert isinstance(fertilizer_analysis, dict)
        assert 'fertilizer_type' in fertilizer_analysis
        assert 'form' in fertilizer_analysis
        assert 'method_compatibility' in fertilizer_analysis
        assert 'cost_per_unit' in fertilizer_analysis
    
    @pytest.mark.asyncio
    async def test_equipment_analysis(self, service, test_request):
        """Test equipment analysis."""
        equipment_analysis = await service.analyze_equipment(test_request.available_equipment[0])
        
        assert isinstance(equipment_analysis, dict)
        assert 'equipment_count' in equipment_analysis
        assert 'equipment_types' in equipment_analysis
        assert 'capacity_analysis' in equipment_analysis
        assert 'compatibility_matrix' in equipment_analysis
    
    @pytest.mark.asyncio
    async def test_method_scoring(self, service, test_request):
        """Test method scoring."""
        scores = await service.score_methods(test_request)
        
        assert isinstance(scores, dict)
        assert 'field_analysis' in scores
        assert 'crop_analysis' in scores
        assert 'fertilizer_analysis' in scores
        assert 'equipment_analysis' in scores
        
        # Check that field analysis contains method scores
        field_analysis = scores['field_analysis']
        assert 'soil_suitability' in field_analysis
        soil_suitability = field_analysis['soil_suitability']
        assert 'broadcast' in soil_suitability
        assert 'band' in soil_suitability
    
    @pytest.mark.asyncio
    async def test_recommendation_generation(self, service, test_request):
        """Test recommendation generation."""
        response = await service.generate_recommendations(test_request)
        
        assert isinstance(response, ApplicationResponse)
        assert response.request_id is not None
        assert len(response.recommended_methods) > 0
        assert response.processing_time_ms > 0
        
        # Check that methods are ranked by efficiency score
        efficiency_scores = [method.efficiency_score for method in response.recommended_methods]
        assert efficiency_scores == sorted(efficiency_scores, reverse=True)


class TestEquipmentAssessmentServiceComprehensive:
    """Comprehensive tests for EquipmentAssessmentService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance."""
        return EquipmentAssessmentService()
    
    def test_service_initialization(self, service):
        """Test service initialization."""
        assert service is not None
        assert hasattr(service, 'assess_equipment_compatibility')
        assert hasattr(service, 'calculate_application_efficiency')
        assert hasattr(service, 'estimate_operational_costs')
        assert hasattr(service, 'evaluate_precision_capabilities')
        assert hasattr(service, 'assess_maintenance_requirements')
    
    def test_equipment_compatibility_assessment(self, service):
        """Test equipment compatibility assessment."""
        equipment = Equipment(
            equipment_id="test_equipment",
            name="Test Spreader",
            category=EquipmentCategory.BROADCAST_SPREADER,
            capacity=10.0,
            capacity_unit="tons",
            status=EquipmentStatus.OPERATIONAL
        )
        
        compatibility = service.assess_equipment_compatibility(equipment)
        
        assert isinstance(compatibility, dict)
        assert 'compatibility_score' in compatibility
        assert 'suitable_methods' in compatibility
        assert 'limitations' in compatibility
        assert 'recommendations' in compatibility
    
    def test_application_efficiency_calculation(self, service):
        """Test application efficiency calculation."""
        equipment = Equipment(
            equipment_id="test_equipment",
            name="Test Spreader",
            category=EquipmentCategory.BROADCAST_SPREADER,
            capacity=10.0,
            capacity_unit="tons",
            status=EquipmentStatus.OPERATIONAL
        )
        
        efficiency = service.calculate_application_efficiency(equipment)
        
        assert isinstance(efficiency, dict)
        assert 'efficiency_score' in efficiency
        assert 'coverage_uniformity' in efficiency
        assert 'application_rate_accuracy' in efficiency
        assert 'time_efficiency' in efficiency
    
    def test_operational_cost_estimation(self, service):
        """Test operational cost estimation."""
        equipment = Equipment(
            equipment_id="test_equipment",
            name="Test Spreader",
            category=EquipmentCategory.BROADCAST_SPREADER,
            capacity=10.0,
            capacity_unit="tons",
            status=EquipmentStatus.OPERATIONAL
        )
        
        costs = service.estimate_operational_costs(equipment, field_size_acres=40.0)
        
        assert isinstance(costs, dict)
        assert 'fuel_cost' in costs
        assert 'labor_cost' in costs
        assert 'maintenance_cost' in costs
        assert 'total_cost_per_acre' in costs


class TestCostAnalysisServiceComprehensive:
    """Comprehensive tests for CostAnalysisService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance."""
        return CostAnalysisService()
    
    def test_service_initialization(self, service):
        """Test service initialization."""
        assert service is not None
        assert hasattr(service, 'calculate_total_cost')
        assert hasattr(service, 'calculate_cost_per_acre')
        assert hasattr(service, 'compare_method_costs')
        assert hasattr(service, 'calculate_fertilizer_costs')
        assert hasattr(service, 'calculate_equipment_costs')
    
    def test_total_cost_calculation(self, service):
        """Test total cost calculation."""
        request = TestDataFactory.create_application_request()
        
        total_cost = service.calculate_total_cost(request)
        
        assert isinstance(total_cost, dict)
        assert 'fertilizer_cost' in total_cost
        assert 'equipment_cost' in total_cost
        assert 'labor_cost' in total_cost
        assert 'fuel_cost' in total_cost
        assert 'maintenance_cost' in total_cost
        assert 'total_cost' in total_cost
    
    def test_cost_per_acre_calculation(self, service):
        """Test cost per acre calculation."""
        request = TestDataFactory.create_application_request()
        
        cost_per_acre = service.calculate_cost_per_acre(request)
        
        assert isinstance(cost_per_acre, dict)
        assert 'cost_per_acre' in cost_per_acre
        assert 'breakdown' in cost_per_acre
        assert cost_per_acre['cost_per_acre'] > 0
    
    def test_method_cost_comparison(self, service):
        """Test method cost comparison."""
        request = TestDataFactory.create_application_request()
        
        comparison = service.compare_method_costs(request)
        
        assert isinstance(comparison, dict)
        assert 'broadcast' in comparison
        assert 'band' in comparison
        assert 'injection' in comparison
        assert 'drip' in comparison
        
        for method, costs in comparison.items():
            assert 'total_cost' in costs
            assert 'cost_per_acre' in costs


class TestDecisionSupportServiceComprehensive:
    """Comprehensive tests for DecisionSupportService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance."""
        return DecisionSupportService()
    
    def test_service_initialization(self, service):
        """Test service initialization."""
        assert service is not None
        assert hasattr(service, 'analyze_scenarios')
        assert hasattr(service, 'generate_decision_tree')
        assert hasattr(service, 'perform_sensitivity_analysis')
        assert hasattr(service, 'evaluate_decision_criteria')
        assert hasattr(service, 'calculate_decision_weights')
    
    def test_scenario_analysis(self, service):
        """Test scenario analysis."""
        request = TestDataFactory.create_application_request()
        
        scenarios = service.analyze_scenarios(request)
        
        assert isinstance(scenarios, dict)
        assert 'scenarios' in scenarios
        assert 'recommendations' in scenarios
        assert 'risk_assessment' in scenarios
    
    def test_decision_tree_generation(self, service):
        """Test decision tree generation."""
        request = TestDataFactory.create_application_request()
        
        decision_tree = service.generate_decision_tree(request)
        
        assert isinstance(decision_tree, dict)
        assert 'decision_nodes' in decision_tree
        assert 'decision_paths' in decision_tree
        assert 'recommended_path' in decision_tree
    
    def test_sensitivity_analysis(self, service):
        """Test sensitivity analysis."""
        request = TestDataFactory.create_application_request()
        
        sensitivity = service.perform_sensitivity_analysis(request)
        
        assert isinstance(sensitivity, dict)
        assert 'parameter_sensitivity' in sensitivity
        assert 'risk_factors' in sensitivity
        assert 'recommendations' in sensitivity


class TestAPIEndpointsComprehensive:
    """Comprehensive tests for API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_health_endpoint(self, client):
        """Test health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_application_methods_endpoint(self, client):
        """Test application methods endpoint."""
        request_data = {
            "field_conditions": {
                "field_size_acres": 40.0,
                "soil_type": "clay_loam",
                "drainage_class": "moderate",
                "slope_percent": 2.5,
                "irrigation_available": True
            },
            "crop_requirements": {
                "crop_type": "corn",
                "growth_stage": "V6",
                "target_yield": 180.0,
                "nutrient_requirements": {"nitrogen": 200.0, "phosphorus": 80.0, "potassium": 150.0}
            },
            "fertilizer_specification": {
                "fertilizer_type": "urea",
                "npk_ratio": "46-0-0",
                "form": "granular",
                "cost_per_unit": 0.45
            },
            "equipment_specification": {
                "equipment_type": "broadcast_spreader",
                "capacity_tons": 10.0,
                "application_width_feet": 60.0,
                "speed_mph": 8.0
            },
            "application_rate_per_acre": 200.0,
            "target_date": "2024-04-15"
        }
        
        response = client.post("/api/v1/application-method/recommend", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "request_id" in data
        assert "recommended_methods" in data
        assert len(data["recommended_methods"]) > 0
    
    def test_equipment_assessment_endpoint(self, client):
        """Test equipment assessment endpoint."""
        request_data = {
            "equipment": {
                "id": "test_equipment",
                "name": "Test Spreader",
                "category": "broadcast_spreader",
                "specifications": {"capacity": 10.0, "width": 60.0},
                "status": "operational"
            },
            "field_size_acres": 40.0
        }
        
        response = client.post("/api/v1/equipment/assess-farm", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "compatibility_assessment" in data
        assert "efficiency_analysis" in data
        assert "cost_estimation" in data
    
    def test_cost_analysis_endpoint(self, client):
        """Test cost analysis endpoint."""
        request_data = {
            "field_conditions": {
                "field_size_acres": 40.0,
                "soil_type": "clay_loam"
            },
            "fertilizer_specification": {
                "fertilizer_type": "urea",
                "npk_ratio": "46-0-0",
                "cost_per_unit": 0.45
            },
            "equipment_specification": {
                "equipment_type": "broadcast_spreader",
                "capacity_tons": 10.0
            },
            "application_rate_per_acre": 200.0
        }
        
        response = client.post("/api/v1/cost-analysis/optimize", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "total_cost" in data
        assert "cost_per_acre" in data
        assert "cost_breakdown" in data
    
    def test_guidance_endpoint(self, client):
        """Test guidance endpoint."""
        request_data = {
            "application_method": "broadcast",
            "fertilizer_type": "urea",
            "field_conditions": {
                "field_size_acres": 40.0,
                "soil_type": "clay_loam"
            },
            "weather_conditions": {
                "temperature": 65,
                "humidity": 70,
                "wind_speed": 5
            }
        }
        
        response = client.post("/api/v1/application-guidance", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "guidance" in data
        assert "recommendations" in data
        assert "safety_considerations" in data


class TestPerformanceAndLoadComprehensive:
    """Comprehensive performance and load tests."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_concurrent_request_handling(self, client):
        """Test concurrent request handling."""
        request_data = {
            "field_conditions": {
                "field_size_acres": 40.0,
                "soil_type": "clay_loam"
            },
            "crop_requirements": {
                "crop_type": "corn",
                "growth_stage": "V6",
                "target_yield": 180.0
            },
            "fertilizer_specification": {
                "fertilizer_type": "urea",
                "npk_ratio": "46-0-0",
                "cost_per_unit": 0.45
            },
            "equipment_specification": {
                "equipment_type": "broadcast_spreader",
                "capacity_tons": 10.0
            },
            "application_rate_per_acre": 200.0
        }
        
        # Test with 10 concurrent requests
        def make_request():
            response = client.post("/api/v1/application-method/recommend", json=request_data)
            return response.status_code == 200
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in futures]
        
        # All requests should succeed
        assert all(results)
    
    def test_response_time_consistency(self, client):
        """Test response time consistency."""
        request_data = {
            "field_conditions": {
                "field_size_acres": 40.0,
                "soil_type": "clay_loam"
            },
            "crop_requirements": {
                "crop_type": "corn",
                "growth_stage": "V6",
                "target_yield": 180.0
            },
            "fertilizer_specification": {
                "fertilizer_type": "urea",
                "npk_ratio": "46-0-0",
                "cost_per_unit": 0.45
            },
            "equipment_specification": {
                "equipment_type": "broadcast_spreader",
                "capacity_tons": 10.0
            },
            "application_rate_per_acre": 200.0
        }
        
        response_times = []
        for _ in range(5):
            start_time = time.time()
            response = client.post("/api/v1/application-method/recommend", json=request_data)
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
        
        # Response times should be consistent (within 2 seconds)
        assert all(rt < 2.0 for rt in response_times)
        
        # Standard deviation should be reasonable
        std_dev = statistics.stdev(response_times)
        assert std_dev < 0.5


class TestAgriculturalValidationComprehensive:
    """Comprehensive agricultural validation tests."""
    
    @pytest.fixture
    def service(self):
        """Create service instance."""
        return ApplicationMethodService()
    
    def test_corn_belt_recommendations(self, service):
        """Test recommendations for corn belt conditions."""
        request = ApplicationRequest(
            field_conditions=FieldConditions(
                field_size_acres=80.0,
                soil_type="clay_loam",
                drainage_class="moderate",
                slope_percent=1.0,
                irrigation_available=False
            ),
            crop_requirements=CropRequirements(
                crop_type="corn",
                growth_stage="V4",
                target_yield=200.0,
                yield_goal_bushels_per_acre=200.0,
                nutrient_requirements={"nitrogen": 220.0, "phosphorus": 90.0, "potassium": 160.0},
                application_timing_preferences=["pre_plant", "side_dress"]
            ),
            fertilizer_specification=FertilizerSpecification(
                fertilizer_type="urea",
                npk_ratio="46-0-0",
                form=FertilizerForm.GRANULAR,
                cost_per_unit=0.45
            ),
            equipment_specification=EquipmentSpecification(
                equipment_type=EquipmentType.BROADCASTER,
                capacity_tons=15.0,
                application_width_feet=80.0,
                speed_mph=10.0
            ),
            application_rate_per_acre=220.0,
            target_date="2024-04-15"
        )
        
        response = service.generate_recommendations(request)
        
        # Should recommend broadcast or band application for corn
        recommended_methods = [method.method_type for method in response.recommended_methods[:2]]
        assert ApplicationMethodType.BROADCAST in recommended_methods or ApplicationMethodType.BAND in recommended_methods
        
        # Scores should be reasonable
        assert all(0.5 <= method.score <= 1.0 for method in response.recommended_methods)
    
    def test_soybean_recommendations(self, service):
        """Test recommendations for soybean conditions."""
        request = ApplicationRequest(
            field_conditions=FieldConditions(
                field_size_acres=60.0,
                soil_type="sandy_loam",
                drainage_class="well",
                slope_percent=3.0,
                irrigation_available=True
            ),
            crop_requirements=CropRequirements(
                crop_type="soybean",
                growth_stage="R1",
                target_yield=60.0,
                yield_goal_bushels_per_acre=60.0,
                nutrient_requirements={"nitrogen": 0.0, "phosphorus": 40.0, "potassium": 80.0},
                application_timing_preferences=["pre_plant"]
            ),
            fertilizer_specification=FertilizerSpecification(
                fertilizer_type="triple_superphosphate",
                npk_ratio="0-46-0",
                form=FertilizerForm.GRANULAR,
                cost_per_unit=0.55
            ),
            equipment_specification=EquipmentSpecification(
                equipment_type=EquipmentType.BROADCASTER,
                capacity_tons=8.0,
                application_width_feet=50.0,
                speed_mph=8.0
            ),
            application_rate_per_acre=40.0,
            target_date="2024-04-20"
        )
        
        response = service.generate_recommendations(request)
        
        # Should recommend broadcast or band application for soybeans
        recommended_methods = [method.method_type for method in response.recommended_methods[:2]]
        assert ApplicationMethodType.BROADCAST in recommended_methods or ApplicationMethodType.BAND in recommended_methods
        
        # Should not recommend nitrogen-heavy methods for soybeans
        nitrogen_methods = [method for method in response.recommended_methods if "nitrogen" in method.method_type.lower()]
        assert len(nitrogen_methods) == 0 or nitrogen_methods[0].score < 0.7


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
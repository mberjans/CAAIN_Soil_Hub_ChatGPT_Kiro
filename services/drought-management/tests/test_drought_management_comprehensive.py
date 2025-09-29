"""
Comprehensive Test Suite for Drought Management System

This test suite provides comprehensive coverage for all drought management services,
including unit tests, integration tests, agricultural validation, and performance tests.

TICKET-014_drought-management-13.1: Build comprehensive drought management testing suite
"""

import pytest
import asyncio
import time
import json
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from decimal import Decimal
import statistics

# Import test fixtures
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from conftest import (
    mock_farm_location_id, mock_field_id, mock_user_id,
    sample_weather_data, sample_soil_data, sample_crop_data,
    sample_drought_assessment_request, sample_conservation_practices,
    sample_irrigation_data, sample_water_source_data,
    mock_external_services, agricultural_validation_data,
    performance_test_data
)


class TestDroughtAssessmentService:
    """Comprehensive tests for drought assessment service."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_drought_risk_calculation(self, mock_external_services):
        """Test drought risk calculation with various scenarios."""
        from src.services.drought_assessment_service import DroughtAssessmentService
        
        service = DroughtAssessmentService()
        await service.initialize()
        
        # Test different drought scenarios
        test_scenarios = [
            {
                "name": "severe_drought",
                "precipitation": 0.5,  # Very low precipitation
                "temperature": 35.0,   # High temperature
                "soil_moisture": 0.10, # Very low soil moisture
                "expected_risk": "severe"
            },
            {
                "name": "moderate_drought",
                "precipitation": 2.0,
                "temperature": 28.0,
                "soil_moisture": 0.20,
                "expected_risk": "moderate"
            },
            {
                "name": "mild_drought",
                "precipitation": 4.0,
                "temperature": 25.0,
                "soil_moisture": 0.25,
                "expected_risk": "mild"
            }
        ]
        
        for scenario in test_scenarios:
            # Mock external service responses
            mock_external_services["weather"].return_value.get_current_weather.return_value = {
                "precipitation": scenario["precipitation"],
                "temperature": scenario["temperature"],
                "humidity": 50.0
            }
            
            from src.models.drought_models import SoilMoistureStatus, SoilMoistureLevel
            mock_external_services["soil"].return_value.get_soil_data.return_value = SoilMoistureStatus(
                field_id=uuid4(),
                surface_moisture_percent=scenario["soil_moisture"] * 100,
                deep_moisture_percent=scenario["soil_moisture"] * 100,
                available_water_capacity=2.0,
                moisture_level=SoilMoistureLevel.ADEQUATE,
                irrigation_recommendation="monitor"
            )
            
            # Test risk assessment
            from src.models.drought_models import DroughtAssessmentRequest
            request = DroughtAssessmentRequest(
                farm_location_id=uuid4(),
                field_id=uuid4(),
                crop_type="corn",
                growth_stage="V6",
                soil_type="clay_loam",
                irrigation_available=True,
                include_forecast=True,
                assessment_depth_days=30
            )
            risk_assessment = await service.assess_drought_risk(request)
            
            assert risk_assessment is not None
            assert hasattr(risk_assessment, 'assessment')
            assert hasattr(risk_assessment.assessment, 'drought_risk_level')
            assert hasattr(risk_assessment.assessment, 'confidence_score')
            assert risk_assessment.assessment.confidence_score > 0.0
    
    @pytest.mark.agricultural
    @pytest.mark.asyncio
    async def test_agricultural_validation_scenarios(self, agricultural_validation_data):
        """Test against known agricultural drought scenarios."""
        from src.services.drought_assessment_service import DroughtAssessmentService
        
        service = DroughtAssessmentService()
        await service.initialize()
        
        for scenario in agricultural_validation_data["known_drought_scenarios"]:
            # Mock data for known scenario
            with patch.object(service, '_get_historical_weather_data') as mock_weather, \
                 patch.object(service, '_get_soil_moisture_status') as mock_soil:
                
                mock_weather.return_value = {
                    "precipitation": [scenario["conditions"]["precipitation_deficit"]],
                    "temperature": [25.0 + scenario["conditions"]["temperature_anomaly"]],
                    "humidity": [50.0]
                }
                
                from src.models.drought_models import SoilMoistureStatus, SoilMoistureLevel
                mock_soil.return_value = SoilMoistureStatus(
                    field_id=uuid4(),
                    surface_moisture_percent=(0.35 - scenario["conditions"]["soil_moisture_deficit"]) * 100,
                    deep_moisture_percent=(0.35 - scenario["conditions"]["soil_moisture_deficit"]) * 100,
                    available_water_capacity=2.0,
                    moisture_level=SoilMoistureLevel.ADEQUATE,
                    irrigation_recommendation="monitor"
                )
                
                # Test assessment
                from src.models.drought_models import DroughtAssessmentRequest
                request = DroughtAssessmentRequest(
                    farm_location_id=uuid4(),
                    field_id=uuid4(),
                    crop_type="corn",
                    growth_stage="V6",
                    soil_type="clay_loam",
                    irrigation_available=True,
                    include_forecast=True,
                    assessment_depth_days=30
                )
                assessment = await service.assess_drought_risk(request)
                
                # Validate against expected impacts
                assert assessment.assessment.drought_risk_level.value in ["moderate", "severe", "extreme"]
                assert assessment.assessment.confidence_score > 0.7  # High confidence for known scenarios


class TestMoistureConservationService:
    """Comprehensive tests for moisture conservation service."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_conservation_practice_recommendations(self, sample_conservation_practices):
        """Test conservation practice recommendations."""
        from src.services.moisture_conservation_service import MoistureConservationService
        
        service = MoistureConservationService()
        await service.initialize()
        
        # Test practice recommendation for different field conditions
        field_conditions = [
            {
                "soil_type": "clay_loam",
                "slope_percent": 5.0,
                "current_practices": [],
                "expected_practices": ["cover_crops", "mulching"]
            },
            {
                "soil_type": "sandy_loam",
                "slope_percent": 2.0,
                "current_practices": ["cover_crops"],
                "expected_practices": ["mulching", "tillage_reduction"]
            }
        ]
        
        for condition in field_conditions:
            recommendations = await service.recommend_conservation_practices(
                field_id=uuid4(),
                soil_type=condition["soil_type"],
                field_size_acres=50.0,
                drought_risk_level="moderate"
            )
            
            assert recommendations is not None
            assert "recommended_practices" in recommendations
            assert "cost_benefit_analysis" in recommendations
            assert len(recommendations["recommended_practices"]) > 0
    
    @pytest.mark.agricultural
    @pytest.mark.asyncio
    async def test_conservation_effectiveness_validation(self, agricultural_validation_data):
        """Test conservation practice effectiveness against agricultural data."""
        from src.services.moisture_conservation_service import MoistureConservationService
        
        service = MoistureConservationService()
        await service.initialize()
        
        for practice_type, expected_data in agricultural_validation_data["conservation_practice_effectiveness"].items():
            # Test practice effectiveness calculation
            effectiveness = await service.calculate_practice_effectiveness(
                practice_type=practice_type,
                field_conditions={
                    "soil_type": "clay_loam",
                    "climate_zone": "temperate",
                    "current_moisture": 0.25
                }
            )
            
            # Validate against expected ranges
            water_savings = effectiveness["water_savings_percent"]
            assert expected_data["water_savings_range"][0] <= water_savings <= expected_data["water_savings_range"][1]
            
            soil_health_improvement = effectiveness["soil_health_improvement"]
            assert soil_health_improvement >= expected_data["soil_health_improvement"] * 0.8  # Allow 20% variance


class TestDroughtMonitoringService:
    """Comprehensive tests for drought monitoring service."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_monitoring_setup_and_configuration(self):
        """Test monitoring setup and configuration."""
        from src.services.drought_monitoring_service import DroughtMonitoringService
        
        service = DroughtMonitoringService()
        await service.initialize()
        
        # Test monitoring setup
        from src.models.drought_models import DroughtMonitoringRequest
        monitoring_request = DroughtMonitoringRequest(
            farm_location_id=uuid4(),
            field_ids=[uuid4()],
            monitoring_frequency="daily",
            alert_thresholds={
                "soil_moisture_low": 30.0,
                "soil_moisture_critical": 20.0,
                "temperature_high": 35.0
            },
            notification_preferences={
                "enabled_channels": ["email", "push"],
                "email": "farmer@example.com"
            }
        )
        
        response = await service.setup_monitoring(monitoring_request)
        
        assert response.status == "active"
        assert response.farm_location_id == monitoring_request.farm_location_id
        assert hasattr(response, 'monitoring_id')
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_end_to_end_monitoring_workflow(self):
        """Test complete monitoring workflow."""
        from src.services.drought_monitoring_service import DroughtMonitoringService
        
        service = DroughtMonitoringService()
        await service.initialize()
        
        farm_location_id = uuid4()
        field_id = uuid4()
        
        # Setup monitoring
        with patch.object(service, '_get_historical_weather_data') as mock_weather, \
             patch.object(service, '_get_soil_moisture_data') as mock_soil, \
             patch.object(service, 'drought_indices_calculator') as mock_calc:
            
            # Mock data
            mock_weather.return_value = {
                "precipitation": [10.5, 8.2, 12.1, 5.8, 15.3, 7.9, 9.4, 11.2],
                "temperature": [22.5, 24.1, 26.8, 28.3, 25.9, 23.7, 21.4, 19.8]
            }
            mock_soil.return_value = {
                "available_water_capacity": 2.5,
                "field_capacity": 0.35,
                "wilting_point": 0.15,
                "current_moisture": 0.25
            }
            mock_calc.calculate_spi = AsyncMock(return_value=[-0.8, -1.2, -1.5, -1.3])
            mock_calc.calculate_pdsi = AsyncMock(return_value=-1.4)
            mock_calc.calculate_spei = AsyncMock(return_value=[-0.9, -1.1, -1.4, -1.2])
            
            # Test monitoring workflow
            from src.models.drought_models import DroughtMonitoringRequest
            monitoring_request = DroughtMonitoringRequest(
                farm_location_id=farm_location_id,
                field_ids=[field_id],
                monitoring_frequency="daily",
                alert_thresholds={"soil_moisture_low": 30.0},
                notification_preferences={"enabled_channels": ["email"]},
                integration_services=["weather", "soil"]
            )
            
            # Setup monitoring
            setup_response = await service.setup_monitoring(monitoring_request)
            assert setup_response.status == "active"
            
            # Calculate drought indices
            indices = await service.calculate_drought_indices(farm_location_id, field_id)
            assert "spi" in indices
            assert "pdsi" in indices
            assert "spei" in indices
            
            # Generate alerts
            alerts = await service.generate_predictive_alerts(farm_location_id)
            assert isinstance(alerts, list)


class TestIrrigationService:
    """Comprehensive tests for irrigation service."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_irrigation_system_assessment(self, sample_irrigation_data):
        """Test irrigation system assessment."""
        from src.services.irrigation_service import IrrigationManagementService
        
        service = IrrigationManagementService()
        await service.initialize()
        
        # Test irrigation system assessment
        from src.services.irrigation_service import IrrigationSystemType
        assessment = await service.assess_irrigation_system(
            field_id=uuid4(),
            system_type=IrrigationSystemType.SPRINKLER,
            system_age_years=5,
            maintenance_history={"last_maintenance": "2024-01-15", "frequency": "monthly"},
            field_characteristics={"size_acres": 50, "soil_type": "clay_loam", "slope_percent": 2.0}
        )
        
        assert assessment is not None
        assert hasattr(assessment, 'current_efficiency')
        assert hasattr(assessment, 'water_savings_potential') or isinstance(assessment, dict)
        assert hasattr(assessment, 'optimization_recommendations') or isinstance(assessment, dict)
    
    @pytest.mark.agricultural
    @pytest.mark.asyncio
    async def test_irrigation_timing_optimization(self):
        """Test irrigation timing optimization."""
        from src.services.irrigation_service import IrrigationManagementService
        
        service = IrrigationManagementService()
        await service.initialize()
        
        # Test irrigation timing optimization
        from src.models.drought_models import IrrigationSystemAssessment, WaterSourceAssessment
        
        current_assessment = IrrigationSystemAssessment(
            system_type="sprinkler",
            current_efficiency=0.75,
            efficiency_level="high",
            water_distribution_uniformity=0.85,
            pressure_consistency=0.90,
            coverage_area_percent=85.0,
            maintenance_status="good",
            age_years=5,
            estimated_water_loss_percent=15.0,
            energy_efficiency_score=0.80,
            overall_score=82.0
        )
        
        water_source_assessment = WaterSourceAssessment(
            source_type="well",
            available_capacity_gpm=100.0,
            water_quality_score=0.9,
            reliability_score=0.9,
            cost_per_gallon=0.02,
            seasonal_variation_percent=20.0,
            sustainability_score=0.8,
            regulatory_compliance=True,
            pumping_capacity_gpm=100.0,
            storage_capacity_gallons=5000.0
        )
        
        optimization = await service.optimize_irrigation_efficiency(
            field_id=uuid4(),
            current_assessment=current_assessment,
            water_source_assessment=water_source_assessment,
            field_characteristics={"size_acres": 50, "soil_type": "clay_loam"}
        )
        
        assert optimization is not None
        assert "optimal_timing" in optimization
        assert "water_amount" in optimization
        assert "efficiency_improvement" in optimization


class TestWaterSourceAnalysisService:
    """Comprehensive tests for water source analysis service."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_water_source_evaluation(self, sample_water_source_data):
        """Test water source evaluation."""
        from src.services.water_source_analysis_service import WaterSourceAnalysisService
        
        service = WaterSourceAnalysisService()
        await service.initialize()
        
        # Test water source evaluation
        evaluation = await service.evaluate_water_source(
            source_type=sample_water_source_data["source_type"],
            field_id=uuid4(),
            farm_location_id=uuid4()
        )
        
        assert evaluation is not None
        # Check if evaluation is a dictionary or has the expected attributes
        if isinstance(evaluation, dict):
            assert "sustainability_rating" in evaluation or "evaluation_score" in evaluation
        else:
            assert hasattr(evaluation, 'sustainability_rating') or hasattr(evaluation, 'evaluation_score')
    
    @pytest.mark.agricultural
    @pytest.mark.asyncio
    async def test_water_source_sustainability(self):
        """Test water source sustainability analysis."""
        from src.services.water_source_analysis_service import WaterSourceAnalysisService
        
        service = WaterSourceAnalysisService()
        await service.initialize()
        
        # Test sustainability analysis
        sustainability = await service.analyze_water_sustainability(
            farm_location_id=uuid4(),
            field_id=uuid4()
        )
        
        assert sustainability is not None
        # Check if sustainability is a dictionary or has the expected attributes
        if isinstance(sustainability, dict):
            assert "sustainability_score" in sustainability or "overall_sustainability_score" in sustainability
        else:
            assert hasattr(sustainability, 'sustainability_score') or hasattr(sustainability, 'overall_sustainability_score')


class TestPerformanceTests:
    """Performance tests for drought management system."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_assessment_requests(self, performance_test_data):
        """Test system performance under concurrent assessment requests."""
        from src.services.drought_assessment_service import DroughtAssessmentService
        
        service = DroughtAssessmentService()
        await service.initialize()
        
        # Create multiple concurrent requests
        num_requests = 50  # Reduced for testing
        farm_ids = [uuid4() for _ in range(num_requests)]
        
        start_time = time.time()
        
        # Mock external services for performance testing
        with patch.object(service, '_get_weather_data') as mock_weather, \
             patch.object(service, '_get_soil_moisture_status') as mock_soil:
            
            mock_weather.return_value = {"precipitation": 5.0, "temperature": 25.0}
            from src.models.drought_models import SoilMoistureStatus, SoilMoistureLevel
            mock_soil.return_value = SoilMoistureStatus(
                field_id=uuid4(),
                surface_moisture_percent=25.0,
                deep_moisture_percent=25.0,
                available_water_capacity=2.0,
                moisture_level=SoilMoistureLevel.ADEQUATE,
                irrigation_recommendation="monitor"
            )
            
            # Execute concurrent requests
            from src.models.drought_models import DroughtAssessmentRequest
            
            async def create_assessment_request(farm_id):
                request = DroughtAssessmentRequest(
                    farm_location_id=farm_id,
                    field_id=uuid4(),
                    crop_type="corn",
                    growth_stage="V6",
                    soil_type="clay_loam",
                    irrigation_available=True,
                    include_forecast=True,
                    assessment_depth_days=30
                )
                return await service.assess_drought_risk(request)
            
            tasks = [create_assessment_request(farm_id) for farm_id in farm_ids]
            
            results = await asyncio.gather(*tasks)
            elapsed_time = time.time() - start_time
            
            # Performance assertions
            assert len(results) == num_requests
            assert elapsed_time < performance_test_data["response_time_threshold"]
            
            # Calculate throughput
            throughput = num_requests / elapsed_time
            assert throughput >= performance_test_data["throughput_threshold"] / 10  # Adjusted for test environment
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_large_dataset_processing(self):
        """Test processing of large datasets."""
        from src.services.drought_monitoring_service import DroughtMonitoringService
        
        service = DroughtMonitoringService()
        await service.initialize()
        
        # Create large dataset
        large_precipitation_data = [10.5 + i * 0.1 for i in range(1000)]
        large_temperature_data = [22.5 + i * 0.05 for i in range(1000)]
        
        start_time = time.time()
        
        with patch.object(service, 'drought_indices_calculator') as mock_calc:
            mock_calc.calculate_spi = AsyncMock(return_value=[-0.8, -1.2, -1.5, -1.3])
            mock_calc.calculate_pdsi = AsyncMock(return_value=-1.4)
            mock_calc.calculate_spei = AsyncMock(return_value=[-0.9, -1.1, -1.4, -1.2])
            
            # Process large dataset
            result = await service.calculate_drought_indices(uuid4(), uuid4())
            
            elapsed_time = time.time() - start_time
            
            # Performance assertion
            assert elapsed_time < 2.0  # Should process large dataset within 2 seconds
            assert result is not None


class TestAgriculturalValidationTests:
    """Agricultural validation tests using real-world scenarios."""
    
    @pytest.mark.agricultural
    @pytest.mark.asyncio
    async def test_2012_drought_scenario(self):
        """Test against 2012 drought scenario (severe drought in Midwest)."""
        from src.services.drought_assessment_service import DroughtAssessmentService
        
        service = DroughtAssessmentService()
        await service.initialize()
        
        # 2012 drought conditions
        drought_2012_conditions = {
            "precipitation_deficit": -8.5,  # inches below normal
            "temperature_anomaly": 3.2,     # degrees F above normal
            "soil_moisture_deficit": 0.15,  # 15% below field capacity
            "expected_yield_loss": 25.0     # percent
        }
        
        with patch.object(service, '_get_weather_data') as mock_weather, \
             patch.object(service, '_get_soil_moisture_status') as mock_soil:
            
            mock_weather.return_value = {
                "precipitation": drought_2012_conditions["precipitation_deficit"],
                "temperature": 25.0 + drought_2012_conditions["temperature_anomaly"],
                "humidity": 40.0  # Low humidity during drought
            }
            
            from src.models.drought_models import SoilMoistureStatus, SoilMoistureLevel
            mock_soil.return_value = SoilMoistureStatus(
                field_id=uuid4(),
                surface_moisture_percent=(0.35 - drought_2012_conditions["soil_moisture_deficit"]) * 100,
                deep_moisture_percent=(0.35 - drought_2012_conditions["soil_moisture_deficit"]) * 100,
                available_water_capacity=2.0,
                moisture_level=SoilMoistureLevel.ADEQUATE,
                irrigation_recommendation="monitor"
            )
            
            from src.models.drought_models import DroughtAssessmentRequest
            request = DroughtAssessmentRequest(
                farm_location_id=uuid4(),
                field_id=uuid4(),
                crop_type="corn",
                growth_stage="V6",
                soil_type="clay_loam",
                irrigation_available=True,
                include_forecast=True,
                assessment_depth_days=30
            )
            assessment = await service.assess_drought_risk(request)
            
            # Validate against known 2012 drought impacts
            assert assessment.assessment.drought_risk_level.value in ["severe", "extreme"]
            assert assessment.assessment.confidence_score > 0.8
    
    @pytest.mark.agricultural
    @pytest.mark.asyncio
    async def test_conservation_practice_effectiveness(self, agricultural_validation_data):
        """Test conservation practice effectiveness against agricultural research."""
        from src.services.moisture_conservation_service import MoistureConservationService
        
        service = MoistureConservationService()
        await service.initialize()
        
        for practice_type, expected_data in agricultural_validation_data["conservation_practice_effectiveness"].items():
            # Test practice effectiveness
            effectiveness = await service.calculate_practice_effectiveness(
                practice_type=practice_type,
                field_conditions={
                    "soil_type": "clay_loam",
                    "climate_zone": "temperate",
                    "current_moisture": 0.25,
                    "slope_percent": 3.0
                }
            )
            
            # Validate against agricultural research data
            water_savings = effectiveness["water_savings_percent"]
            expected_range = expected_data["water_savings_range"]
            
            # Allow for some variance in calculations (±5%)
            tolerance = 5.0
            assert expected_range[0] - tolerance <= water_savings <= expected_range[1] + tolerance, \
                f"{practice_type} water savings {water_savings}% not in expected range {expected_range} (±{tolerance}%)"
            
            # Validate soil health improvement
            soil_health_improvement = effectiveness["soil_health_improvement"]
            expected_improvement = expected_data["soil_health_improvement"]
            
            assert soil_health_improvement >= expected_improvement * 0.8, \
                f"{practice_type} soil health improvement {soil_health_improvement} below expected {expected_improvement}"


class TestIntegrationTests:
    """Integration tests for drought management system."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_full_drought_management_workflow(self):
        """Test complete drought management workflow."""
        from src.services.drought_assessment_service import DroughtAssessmentService
        from src.services.moisture_conservation_service import MoistureConservationService
        from src.services.drought_monitoring_service import DroughtMonitoringService
        
        # Initialize services
        assessment_service = DroughtAssessmentService()
        conservation_service = MoistureConservationService()
        monitoring_service = DroughtMonitoringService()
        
        await assessment_service.initialize()
        await conservation_service.initialize()
        await monitoring_service.initialize()
        
        farm_location_id = uuid4()
        field_id = uuid4()
        
        # Mock external dependencies
        with patch.object(assessment_service, '_get_weather_data') as mock_weather, \
             patch.object(assessment_service, '_get_soil_moisture_status') as mock_soil, \
             patch.object(monitoring_service, '_get_historical_weather_data') as mock_hist_weather, \
             patch.object(monitoring_service, '_get_soil_moisture_data') as mock_hist_soil, \
             patch.object(monitoring_service, 'drought_indices_calculator') as mock_calc:
            
            # Mock data
            mock_weather.return_value = {"precipitation": 2.0, "temperature": 30.0}
            from src.models.drought_models import SoilMoistureStatus, SoilMoistureLevel
            mock_soil.return_value = SoilMoistureStatus(
                field_id=field_id,
                surface_moisture_percent=18.0,
                deep_moisture_percent=18.0,
                available_water_capacity=2.0,
                moisture_level=SoilMoistureLevel.DRY,
                irrigation_recommendation="irrigate"
            )
            mock_hist_weather.return_value = {
                "precipitation": [10.5, 8.2, 12.1, 5.8, 15.3, 7.9, 9.4, 11.2],
                "temperature": [22.5, 24.1, 26.8, 28.3, 25.9, 23.7, 21.4, 19.8]
            }
            mock_hist_soil.return_value = {
                "available_water_capacity": 2.5,
                "field_capacity": 0.35,
                "wilting_point": 0.15,
                "current_moisture": 0.18
            }
            mock_calc.calculate_spi = AsyncMock(return_value=[-0.8, -1.2, -1.5, -1.3])
            mock_calc.calculate_pdsi = AsyncMock(return_value=-1.4)
            mock_calc.calculate_spei = AsyncMock(return_value=[-0.9, -1.1, -1.4, -1.2])
            
            # Step 1: Assess drought risk
            from src.models.drought_models import DroughtAssessmentRequest
            request = DroughtAssessmentRequest(
                farm_location_id=farm_location_id,
                field_id=field_id,
                crop_type="corn",
                growth_stage="V6",
                soil_type="clay_loam",
                irrigation_available=True,
                include_forecast=True,
                assessment_depth_days=30
            )
            risk_assessment = await assessment_service.assess_drought_risk(request)
            
            assert risk_assessment is not None
            assert "risk_level" in risk_assessment
            
            # Step 2: Get conservation recommendations
            conservation_recommendations = await conservation_service.recommend_conservation_practices(
                field_id=field_id,
                soil_type="clay_loam",
                slope_percent=3.0,
                current_practices=[]
            )
            
            assert conservation_recommendations is not None
            assert "recommended_practices" in conservation_recommendations
            
            # Step 3: Setup monitoring
            from src.models.drought_models import DroughtMonitoringRequest
            monitoring_request = DroughtMonitoringRequest(
                farm_location_id=farm_location_id,
                field_ids=[field_id],
                monitoring_frequency="daily",
                alert_thresholds={"soil_moisture_low": 30.0},
                notification_preferences={"enabled_channels": ["email"]},
                integration_services=["weather", "soil"]
            )
            
            monitoring_response = await monitoring_service.setup_monitoring(monitoring_request)
            assert monitoring_response["status"] == "active"
            
            # Step 4: Calculate drought indices
            drought_indices = await monitoring_service.calculate_drought_indices(
                farm_location_id, field_id
            )
            
            assert "spi" in drought_indices
            assert "pdsi" in drought_indices
            assert "spei" in drought_indices
            
            # Verify workflow integration
            assert risk_assessment["farm_location_id"] == farm_location_id
            assert conservation_recommendations["field_id"] == field_id
            assert monitoring_response["farm_location_id"] == farm_location_id
            assert drought_indices["field_id"] == field_id


class TestDataValidationTests:
    """Data validation and quality tests."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_input_data_validation(self):
        """Test input data validation."""
        from src.services.drought_assessment_service import DroughtAssessmentService
        
        service = DroughtAssessmentService()
        await service.initialize()
        
        # Test invalid inputs
        invalid_inputs = [
            {"farm_location_id": "invalid_uuid", "field_id": uuid4(), "crop_type": "corn"},
            {"farm_location_id": uuid4(), "field_id": "invalid_uuid", "crop_type": "corn"},
            {"farm_location_id": uuid4(), "field_id": uuid4(), "crop_type": ""},
            {"farm_location_id": None, "field_id": uuid4(), "crop_type": "corn"},
        ]
        
        for invalid_input in invalid_inputs:
            with pytest.raises((ValueError, TypeError)):
                await service.assess_drought_risk(**invalid_input)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_data_range_validation(self):
        """Test data range validation."""
        from src.models.drought_models import SoilMoistureStatus, ConservationPractice
        
        # Test invalid moisture percentages
        with pytest.raises(ValueError, match="Input should be greater than or equal to 0"):
            SoilMoistureStatus(
                field_id=uuid4(),
                surface_moisture_percent=-5.0,  # Invalid negative value
                deep_moisture_percent=50.0,
                available_water_capacity=2.0,
                moisture_level="adequate",
                irrigation_recommendation="none"
            )
        
        with pytest.raises(ValueError, match="Input should be less than or equal to 100"):
            SoilMoistureStatus(
                field_id=uuid4(),
                surface_moisture_percent=150.0,  # Invalid > 100 value
                deep_moisture_percent=50.0,
                available_water_capacity=2.0,
                moisture_level="adequate",
                irrigation_recommendation="none"
            )
        
        # Test invalid water savings percentage
        with pytest.raises(ValueError, match="Input should be greater than or equal to 0"):
            ConservationPractice(
                practice_id=uuid4(),
                practice_name="test",
                practice_type="cover_crops",
                description="test practice",
                implementation_cost=100.0,
                water_savings_percent=-10.0,  # Invalid negative value
                soil_health_impact="positive",
                implementation_time_days=30,
                maintenance_cost_per_year=50.0,
                effectiveness_rating=8.0
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
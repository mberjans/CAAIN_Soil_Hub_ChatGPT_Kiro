"""
Tests for Drought Assessment Service

Comprehensive test suite for drought risk assessment and management functionality.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, date, timedelta
from uuid import UUID
from decimal import Decimal

from src.services.drought_assessment_service import DroughtAssessmentService
from src.models.drought_models import (
    DroughtAssessmentRequest,
    DroughtRiskLevel,
    SoilMoistureLevel,
    WeatherImpact,
    RecommendedAction
)

class TestDroughtAssessmentService:
    """Test suite for DroughtAssessmentService."""
    
    @pytest.fixture
    async def service(self):
        """Create service instance for testing."""
        service = DroughtAssessmentService()
        await service.initialize()
        yield service
        await service.cleanup()
    
    @pytest.fixture
    def sample_request(self):
        """Create sample assessment request."""
        return DroughtAssessmentRequest(
            farm_location_id=UUID(),
            field_id=UUID(),
            crop_type="corn",
            growth_stage="V6",
            soil_type="clay_loam",
            irrigation_available=True,
            include_forecast=True,
            assessment_depth_days=30
        )
    
    @pytest.mark.asyncio
    async def test_initialize_service(self):
        """Test service initialization."""
        service = DroughtAssessmentService()
        await service.initialize()
        
        assert service.initialized is True
        assert service.weather_service is not None
        assert service.soil_service is not None
        assert service.crop_service is not None
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_assess_drought_risk_success(self, service, sample_request):
        """Test successful drought risk assessment."""
        with patch.object(service, '_get_soil_moisture_status') as mock_soil, \
             patch.object(service, '_assess_weather_impact') as mock_weather, \
             patch.object(service, '_calculate_drought_risk_level') as mock_risk, \
             patch.object(service, '_get_current_practices') as mock_practices, \
             patch.object(service, '_generate_recommendations') as mock_recommendations, \
             patch.object(service, '_calculate_water_savings_potential') as mock_savings:
            
            # Mock return values
            mock_soil.return_value = MagicMock()
            mock_weather.return_value = MagicMock()
            mock_risk.return_value = DroughtRiskLevel.MODERATE
            mock_practices.return_value = []
            mock_recommendations.return_value = []
            mock_savings.return_value = MagicMock()
            
            # Execute test
            result = await service.assess_drought_risk(sample_request)
            
            # Assertions
            assert result is not None
            assert result.assessment is not None
            assert result.assessment.farm_location_id == sample_request.farm_location_id
            assert result.assessment.drought_risk_level == DroughtRiskLevel.MODERATE
            assert result.recommendations is not None
            assert result.next_steps is not None
            assert result.monitoring_schedule is not None
    
    @pytest.mark.asyncio
    async def test_assess_drought_risk_error_handling(self, service, sample_request):
        """Test error handling in drought risk assessment."""
        with patch.object(service, '_get_soil_moisture_status', side_effect=Exception("Soil service error")):
            with pytest.raises(Exception) as exc_info:
                await service.assess_drought_risk(sample_request)
            
            assert "Soil service error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_current_drought_risk(self, service):
        """Test getting current drought risk assessment."""
        farm_location_id = UUID()
        
        with patch.object(service, '_get_soil_moisture_status') as mock_soil, \
             patch.object(service, '_get_recent_weather_data') as mock_weather, \
             patch.object(service, '_calculate_risk_from_data') as mock_risk, \
             patch.object(service, '_identify_risk_factors') as mock_factors, \
             patch.object(service, '_generate_mitigation_strategies') as mock_strategies, \
             patch.object(service, '_generate_monitoring_recommendations') as mock_monitoring:
            
            # Mock return values
            mock_soil.return_value = MagicMock()
            mock_weather.return_value = {"temperature": {"avg": 25.0}, "precipitation": {"total": 10.0}}
            mock_risk.return_value = DroughtRiskLevel.LOW
            mock_factors.return_value = ["Low precipitation"]
            mock_strategies.return_value = ["Implement irrigation"]
            mock_monitoring.return_value = ["Monitor soil moisture weekly"]
            
            # Execute test
            result = await service.get_current_drought_risk(farm_location_id)
            
            # Assertions
            assert result is not None
            assert result.farm_location_id == farm_location_id
            assert result.risk_level == DroughtRiskLevel.LOW
            assert len(result.risk_factors) > 0
            assert len(result.mitigation_strategies) > 0
            assert len(result.monitoring_recommendations) > 0
            assert result.next_assessment_date > result.assessment_date
    
    @pytest.mark.asyncio
    async def test_get_soil_moisture_status(self, service):
        """Test soil moisture status retrieval."""
        field_id = UUID()
        
        with patch.object(service, '_get_field_characteristics') as mock_field, \
             patch.object(service, '_get_recent_weather_data') as mock_weather, \
             patch.object(service, '_calculate_surface_moisture') as mock_surface, \
             patch.object(service, '_calculate_deep_moisture') as mock_deep, \
             patch.object(service, '_calculate_available_water_capacity') as mock_capacity, \
             patch.object(service, '_determine_moisture_level') as mock_level, \
             patch.object(service, '_generate_irrigation_recommendation') as mock_irrigation, \
             patch.object(service, '_calculate_days_until_critical') as mock_days:
            
            # Mock return values
            mock_field.return_value = {"soil_type": "clay_loam", "field_size_acres": 40.0}
            mock_weather.return_value = {"precipitation": {"total": 5.0}, "temperature": {"avg": 25.0}}
            mock_surface.return_value = 45.0
            mock_deep.return_value = 60.0
            mock_capacity.return_value = 2.5
            mock_level.return_value = SoilMoistureLevel.ADEQUATE
            mock_irrigation.return_value = "Monitor closely"
            mock_days.return_value = 7
            
            # Execute test
            result = await service.get_soil_moisture_status(field_id)
            
            # Assertions
            assert result is not None
            assert result.field_id == field_id
            assert result.surface_moisture_percent == 45.0
            assert result.deep_moisture_percent == 60.0
            assert result.available_water_capacity == 2.5
            assert result.moisture_level == SoilMoistureLevel.ADEQUATE
            assert result.irrigation_recommendation == "Monitor closely"
            assert result.days_until_critical == 7
    
    @pytest.mark.asyncio
    async def test_calculate_drought_risk_level(self, service):
        """Test drought risk level calculation."""
        # Create mock objects
        soil_moisture = MagicMock()
        soil_moisture.moisture_level = SoilMoistureLevel.DRY
        
        weather_impact = MagicMock()
        weather_impact.risk_factors = ["High temperature", "Low precipitation"]
        
        # Test high risk scenario
        result = await service._calculate_drought_risk_level(
            soil_moisture, weather_impact, "corn", "V6"
        )
        assert result == DroughtRiskLevel.HIGH
        
        # Test moderate risk scenario
        soil_moisture.moisture_level = SoilMoistureLevel.DRY
        weather_impact.risk_factors = ["Low precipitation"]
        
        result = await service._calculate_drought_risk_level(
            soil_moisture, weather_impact, "corn", "V6"
        )
        assert result == DroughtRiskLevel.MODERATE
        
        # Test low risk scenario
        soil_moisture.moisture_level = SoilMoistureLevel.ADEQUATE
        weather_impact.risk_factors = []
        
        result = await service._calculate_drought_risk_level(
            soil_moisture, weather_impact, "corn", "V6"
        )
        assert result == DroughtRiskLevel.LOW
    
    @pytest.mark.asyncio
    async def test_generate_recommendations(self, service, sample_request):
        """Test recommendation generation."""
        soil_moisture = MagicMock()
        soil_moisture.moisture_level = SoilMoistureLevel.DRY
        
        weather_impact = MagicMock()
        weather_impact.risk_factors = ["High temperature"]
        
        # Execute test
        recommendations = await service._generate_recommendations(
            DroughtRiskLevel.HIGH, soil_moisture, weather_impact, sample_request
        )
        
        # Assertions
        assert len(recommendations) > 0
        assert all(isinstance(rec, RecommendedAction) for rec in recommendations)
        
        # Check for high priority recommendations
        high_priority = [rec for rec in recommendations if rec.priority == "high"]
        assert len(high_priority) > 0
    
    @pytest.mark.asyncio
    async def test_calculate_water_savings_potential(self, service):
        """Test water savings potential calculation."""
        field_id = UUID()
        recommendations = [
            RecommendedAction(
                action_id=UUID(),
                action_type="Irrigation",
                priority="high",
                description="Test action",
                implementation_timeline="immediate",
                expected_benefit="Water savings",
                cost_estimate=Decimal("50.00"),
                resources_required=["Water"]
            )
        ]
        
        result = await service._calculate_water_savings_potential(field_id, recommendations)
        
        assert result is not None
        assert result.current_water_usage > 0
        assert result.potential_savings > 0
        assert result.savings_percentage > 0
        assert result.cost_savings_per_year > 0
        assert result.implementation_cost > 0
        assert result.payback_period_years > 0
    
    @pytest.mark.asyncio
    async def test_generate_next_steps(self, service):
        """Test next steps generation."""
        # Test high risk scenario
        next_steps = service._generate_next_steps(DroughtRiskLevel.HIGH, [])
        assert "Implement immediate drought mitigation measures" in next_steps
        assert "Increase monitoring frequency" in next_steps
        
        # Test low risk scenario
        next_steps = service._generate_next_steps(DroughtRiskLevel.LOW, [])
        assert "Review and implement conservation practices" in next_steps
        assert "Schedule follow-up assessment" in next_steps
    
    @pytest.mark.asyncio
    async def test_create_monitoring_schedule(self, service):
        """Test monitoring schedule creation."""
        # Test high risk schedule
        schedule = service._create_monitoring_schedule(DroughtRiskLevel.HIGH)
        assert schedule["frequency"] == "daily"
        assert schedule["soil_moisture_checks"] == "twice_daily"
        
        # Test moderate risk schedule
        schedule = service._create_monitoring_schedule(DroughtRiskLevel.MODERATE)
        assert schedule["frequency"] == "every_other_day"
        assert schedule["soil_moisture_checks"] == "daily"
        
        # Test low risk schedule
        schedule = service._create_monitoring_schedule(DroughtRiskLevel.LOW)
        assert schedule["frequency"] == "weekly"
        assert schedule["soil_moisture_checks"] == "weekly"
    
    @pytest.mark.asyncio
    async def test_calculate_surface_moisture(self, service):
        """Test surface moisture calculation."""
        weather_data = {
            "precipitation": {"total": 10.0},
            "temperature": {"avg": 25.0}
        }
        field_data = {"soil_type": "clay_loam"}
        
        result = await service._calculate_surface_moisture(weather_data, field_data)
        
        assert isinstance(result, float)
        assert 0 <= result <= 100
    
    @pytest.mark.asyncio
    async def test_calculate_deep_moisture(self, service):
        """Test deep moisture calculation."""
        weather_data = {
            "precipitation": {"total": 10.0},
            "temperature": {"avg": 25.0}
        }
        field_data = {"soil_type": "clay_loam"}
        
        result = await service._calculate_deep_moisture(weather_data, field_data, 30)
        
        assert isinstance(result, float)
        assert 0 <= result <= 100
    
    @pytest.mark.asyncio
    async def test_calculate_available_water_capacity(self, service):
        """Test available water capacity calculation."""
        surface_moisture = 45.0
        deep_moisture = 60.0
        field_data = {"soil_type": "clay_loam"}
        
        result = await service._calculate_available_water_capacity(
            surface_moisture, deep_moisture, field_data
        )
        
        assert isinstance(result, float)
        assert result > 0
    
    def test_determine_moisture_level(self, service):
        """Test moisture level determination."""
        # Test very dry
        result = service._determine_moisture_level(15.0, 20.0)
        assert result == SoilMoistureLevel.VERY_DRY
        
        # Test dry
        result = service._determine_moisture_level(30.0, 35.0)
        assert result == SoilMoistureLevel.DRY
        
        # Test adequate
        result = service._determine_moisture_level(50.0, 60.0)
        assert result == SoilMoistureLevel.ADEQUATE
        
        # Test moist
        result = service._determine_moisture_level(75.0, 80.0)
        assert result == SoilMoistureLevel.MOIST
        
        # Test saturated
        result = service._determine_moisture_level(95.0, 100.0)
        assert result == SoilMoistureLevel.SATURATED
    
    @pytest.mark.asyncio
    async def test_generate_irrigation_recommendation(self, service):
        """Test irrigation recommendation generation."""
        field_data = {"soil_type": "clay_loam"}
        
        # Test very dry recommendation
        result = await service._generate_irrigation_recommendation(
            SoilMoistureLevel.VERY_DRY, 1.0, field_data
        )
        assert "Immediate irrigation" in result
        
        # Test adequate recommendation
        result = await service._generate_irrigation_recommendation(
            SoilMoistureLevel.ADEQUATE, 2.5, field_data
        )
        assert "Monitor closely" in result
        
        # Test moist recommendation
        result = await service._generate_irrigation_recommendation(
            SoilMoistureLevel.MOIST, 3.0, field_data
        )
        assert "No irrigation needed" in result
    
    @pytest.mark.asyncio
    async def test_calculate_days_until_critical(self, service):
        """Test days until critical calculation."""
        weather_data = {
            "precipitation": {"total": 5.0},
            "temperature": {"avg": 25.0}
        }
        field_data = {"soil_type": "clay_loam"}
        
        # Test very dry (critical now)
        result = await service._calculate_days_until_critical(
            SoilMoistureLevel.VERY_DRY, weather_data, field_data
        )
        assert result == 1
        
        # Test dry (critical now)
        result = await service._calculate_days_until_critical(
            SoilMoistureLevel.DRY, weather_data, field_data
        )
        assert result == 1
        
        # Test adequate
        result = await service._calculate_days_until_critical(
            SoilMoistureLevel.ADEQUATE, weather_data, field_data
        )
        assert result is not None
        assert result > 0
    
    def test_get_assessment_frequency(self, service):
        """Test assessment frequency calculation."""
        # Test high risk frequency
        result = service._get_assessment_frequency(DroughtRiskLevel.HIGH)
        assert result == 3
        
        # Test moderate risk frequency
        result = service._get_assessment_frequency(DroughtRiskLevel.MODERATE)
        assert result == 7
        
        # Test low risk frequency
        result = service._get_assessment_frequency(DroughtRiskLevel.LOW)
        assert result == 14


class TestDroughtAssessmentIntegration:
    """Integration tests for drought assessment service."""
    
    @pytest.mark.asyncio
    async def test_full_assessment_workflow(self):
        """Test complete drought assessment workflow."""
        service = DroughtAssessmentService()
        await service.initialize()
        
        try:
            request = DroughtAssessmentRequest(
                farm_location_id=UUID(),
                crop_type="corn",
                growth_stage="V6",
                soil_type="clay_loam",
                irrigation_available=True
            )
            
            # This would normally make actual service calls
            # For integration testing, we'd use real data sources
            with patch.object(service, '_get_soil_moisture_status') as mock_soil, \
                 patch.object(service, '_assess_weather_impact') as mock_weather:
                
                mock_soil.return_value = MagicMock()
                mock_weather.return_value = MagicMock()
                
                result = await service.assess_drought_risk(request)
                
                assert result is not None
                assert result.assessment is not None
                assert result.recommendations is not None
        
        finally:
            await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_service_health_check(self):
        """Test service health check functionality."""
        service = DroughtAssessmentService()
        
        # Test before initialization
        assert service.initialized is False
        
        # Test after initialization
        await service.initialize()
        assert service.initialized is True
        
        # Test cleanup
        await service.cleanup()
        assert service.initialized is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
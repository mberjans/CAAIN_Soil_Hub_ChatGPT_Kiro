"""
Tests for Water Source Analysis Service

Comprehensive test suite for water source and availability analysis functionality.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from uuid import uuid4
from decimal import Decimal

from src.services.water_source_analysis_service import WaterSourceAnalysisService
from src.models.drought_models import WaterSourceType, WaterSourceAssessment
from src.models.water_source_models import (
    WaterSourceAnalysisRequest,
    WaterSourceAnalysisResponse,
    WaterAvailabilityForecast,
    WaterBudgetPlan,
    DroughtContingencyPlan,
    AlternativeWaterSource,
    WaterUsageOptimization
)

class TestWaterSourceAnalysisService:
    """Test suite for WaterSourceAnalysisService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return WaterSourceAnalysisService()
    
    @pytest.fixture
    def sample_farm_location_id(self):
        """Sample farm location ID for testing."""
        return uuid4()
    
    @pytest.fixture
    def sample_field_id(self):
        """Sample field ID for testing."""
        return uuid4()
    
    @pytest.fixture
    def sample_water_sources(self):
        """Sample water source data for testing."""
        return [
            {
                "source_type": "well",
                "capacity_gpm": 150,
                "quality_data": {
                    "ph": 7.2,
                    "salinity_ppm": 500,
                    "nitrates_ppm": 5,
                    "pathogens": False,
                    "iron_ppm": 0.2
                },
                "reliability_history": {
                    "uptime_percent": 95
                },
                "cost_data": {
                    "energy_cost_per_gallon": 0.001,
                    "treatment_cost_per_gallon": 0.0005,
                    "maintenance_cost_per_gallon": 0.0002
                }
            },
            {
                "source_type": "surface_water",
                "capacity_gpm": 200,
                "quality_data": {
                    "ph": 6.8,
                    "salinity_ppm": 200,
                    "nitrates_ppm": 3,
                    "pathogens": False,
                    "iron_ppm": 0.1
                },
                "reliability_history": {
                    "uptime_percent": 85
                },
                "cost_data": {
                    "energy_cost_per_gallon": 0.0008,
                    "treatment_cost_per_gallon": 0.001,
                    "maintenance_cost_per_gallon": 0.0003
                }
            }
        ]
    
    @pytest.fixture
    def sample_water_requirements(self):
        """Sample water requirements for testing."""
        return {
            "daily_requirement_gallons": 15000,
            "peak_demand_gpm": 200,
            "irrigation_schedule": "daily",
            "crop_types": ["corn", "soybean"]
        }
    
    @pytest.fixture
    def sample_field_characteristics(self):
        """Sample field characteristics for testing."""
        return {
            "field_size_acres": 50,
            "soil_type": "clay_loam",
            "slope_percent": 2.5,
            "drainage_class": "moderate",
            "irrigation_available": True
        }
    
    @pytest.fixture
    def sample_analysis_request(self, sample_farm_location_id, sample_field_id, 
                               sample_water_sources, sample_water_requirements, 
                               sample_field_characteristics):
        """Sample analysis request for testing."""
        return WaterSourceAnalysisRequest(
            farm_location_id=sample_farm_location_id,
            field_id=sample_field_id,
            water_sources=sample_water_sources,
            water_requirements=sample_water_requirements,
            field_characteristics=sample_field_characteristics,
            forecast_days=30,
            analysis_depth="comprehensive"
        )
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, service):
        """Test service initialization and cleanup."""
        await service.initialize()
        assert service.initialized is True
        
        await service.cleanup()
        assert service.initialized is False
    
    @pytest.mark.asyncio
    async def test_water_source_database_initialization(self, service):
        """Test water source database initialization."""
        database = service.water_source_database
        
        # Check that all expected source types are present
        expected_sources = ["well", "surface_water", "municipal", "recycled", "rainwater", "spring"]
        for source_type in expected_sources:
            assert source_type in database
            assert "description" in database[source_type]
            assert "sustainability_score" in database[source_type]
            assert "drought_resilience" in database[source_type]
    
    @pytest.mark.asyncio
    async def test_analyze_water_sources_success(self, service, sample_analysis_request):
        """Test successful water source analysis."""
        await service.initialize()
        
        try:
            response = await service.analyze_water_sources(sample_analysis_request)
            
            # Verify response structure
            assert isinstance(response, WaterSourceAnalysisResponse)
            assert response.farm_location_id == sample_analysis_request.farm_location_id
            assert response.field_id == sample_analysis_request.field_id
            assert response.analysis_date is not None
            
            # Verify source assessments
            assert len(response.source_assessments) == 2
            for assessment in response.source_assessments:
                assert isinstance(assessment, WaterSourceAssessment)
                assert assessment.available_capacity_gpm > 0
                assert 0 <= assessment.water_quality_score <= 1
                assert 0 <= assessment.reliability_score <= 1
                assert assessment.cost_per_gallon > 0
            
            # Verify availability forecast
            assert isinstance(response.availability_forecast, WaterAvailabilityForecast)
            assert response.availability_forecast.forecast_period_days == 30
            assert len(response.availability_forecast.forecast_data) == 30
            
            # Verify water budget plan
            assert isinstance(response.water_budget_plan, WaterBudgetPlan)
            assert response.water_budget_plan.total_available_capacity_gpm > 0
            assert response.water_budget_plan.daily_requirement_gallons == 15000
            
            # Verify drought contingency plan
            assert isinstance(response.drought_contingency_plan, DroughtContingencyPlan)
            assert len(response.drought_contingency_plan.contingency_scenarios) == 3
            
            # Verify alternative sources
            assert isinstance(response.alternative_sources, list)
            for alt_source in response.alternative_sources:
                assert isinstance(alt_source, AlternativeWaterSource)
                assert 0 <= alt_source.feasibility_score <= 1
            
            # Verify usage optimization
            assert isinstance(response.usage_optimization, WaterUsageOptimization)
            assert len(response.usage_optimization.optimization_plan) > 0
            
            # Verify recommendations
            assert isinstance(response.recommendations, list)
            assert len(response.recommendations) > 0
            
        finally:
            await service.cleanup()


if __name__ == "__main__":
    pytest.main([__file__])

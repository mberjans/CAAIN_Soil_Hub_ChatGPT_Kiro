"""
Tests for Irrigation Management Service

Comprehensive test suite for irrigation assessment, optimization,
and scheduling functionality.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4
from decimal import Decimal
from datetime import datetime, timedelta

from src.services.irrigation_service import (
    IrrigationManagementService,
    IrrigationSystemType,
    WaterSourceType,
    IrrigationEfficiencyLevel,
    IrrigationSystemAssessment,
    WaterSourceAssessment,
    IrrigationConstraint,
    IrrigationOptimization
)
from src.models.drought_models import (
    IrrigationAssessmentRequest,
    IrrigationScheduleRequest,
    IrrigationOptimizationRequest
)

class TestIrrigationManagementService:
    """Test suite for IrrigationManagementService."""

    @pytest.fixture
    def service(self):
        """Create irrigation management service instance."""
        return IrrigationManagementService()

    @pytest.fixture
    def sample_field_id(self):
        """Sample field ID for testing."""
        return uuid4()

    @pytest.fixture
    def sample_field_characteristics(self):
        """Sample field characteristics for testing."""
        return {
            "size_acres": 100,
            "slope_percent": 5.0,
            "soil_type": "clay_loam",
            "elevation_variation_feet": 10,
            "required_capacity_gpm": 150,
            "required_storage_gallons": 50000
        }

    @pytest.fixture
    def sample_maintenance_history(self):
        """Sample maintenance history for testing."""
        return {
            "score": 0.8,
            "frequency_score": 0.7,
            "last_maintenance_days_ago": 30,
            "frequency_days": 60
        }

    @pytest.fixture
    def sample_water_quality_data(self):
        """Sample water quality data for testing."""
        return {
            "ph": 7.2,
            "tds_ppm": 400,
            "salinity_ppm": 150
        }

    @pytest.fixture
    def sample_reliability_history(self):
        """Sample reliability history for testing."""
        return {
            "uptime_percent": 95,
            "failures_per_year": 1
        }

    @pytest.fixture
    def sample_cost_data(self):
        """Sample cost data for testing."""
        return {
            "energy_cost_per_gallon": Decimal("0.001"),
            "maintenance_cost_per_gallon": Decimal("0.0005")
        }

    @pytest.fixture
    def sample_weather_forecast(self):
        """Sample weather forecast for testing."""
        return [
            {"temperature_celsius": 25, "precipitation_mm": 0, "wind_speed_kmh": 10},
            {"temperature_celsius": 28, "precipitation_mm": 2, "wind_speed_kmh": 15},
            {"temperature_celsius": 30, "precipitation_mm": 0, "wind_speed_kmh": 8},
            {"temperature_celsius": 26, "precipitation_mm": 5, "wind_speed_kmh": 12},
            {"temperature_celsius": 24, "precipitation_mm": 0, "wind_speed_kmh": 6},
            {"temperature_celsius": 27, "precipitation_mm": 1, "wind_speed_kmh": 9},
            {"temperature_celsius": 29, "precipitation_mm": 0, "wind_speed_kmh": 7}
        ]

    @pytest.fixture
    def sample_soil_moisture_data(self):
        """Sample soil moisture data for testing."""
        return {
            "current_moisture_percent": 45,
            "field_capacity_percent": 80,
            "wilting_point_percent": 25
        }

    @pytest.mark.asyncio
    async def test_assess_irrigation_system_success(self, service, sample_field_id, sample_field_characteristics, sample_maintenance_history):
        """Test successful irrigation system assessment."""
        assessment = await service.assess_irrigation_system(
            field_id=sample_field_id,
            system_type=IrrigationSystemType.CENTER_PIVOT,
            system_age_years=5,
            maintenance_history=sample_maintenance_history,
            field_characteristics=sample_field_characteristics
        )

        assert isinstance(assessment, IrrigationSystemAssessment)
        assert assessment.system_type == IrrigationSystemType.CENTER_PIVOT
        assert 0 <= assessment.current_efficiency <= 1
        assert assessment.efficiency_level in IrrigationEfficiencyLevel
        assert 0 <= assessment.water_distribution_uniformity <= 1
        assert 0 <= assessment.pressure_consistency <= 1
        assert 0 <= assessment.coverage_area_percent <= 100
        assert assessment.age_years == 5
        assert 0 <= assessment.estimated_water_loss_percent <= 100
        assert 0 <= assessment.energy_efficiency_score <= 1
        assert 0 <= assessment.overall_score <= 100

    @pytest.mark.asyncio
    async def test_assess_irrigation_system_different_types(self, service, sample_field_id, sample_field_characteristics):
        """Test irrigation system assessment for different system types."""
        system_types = [
            IrrigationSystemType.SPRINKLER,
            IrrigationSystemType.DRIP,
            IrrigationSystemType.FLOOD,
            IrrigationSystemType.CENTER_PIVOT
        ]

        for system_type in system_types:
            assessment = await service.assess_irrigation_system(
                field_id=sample_field_id,
                system_type=system_type,
                system_age_years=3,
                maintenance_history={},
                field_characteristics=sample_field_characteristics
            )

            assert assessment.system_type == system_type
            assert assessment.current_efficiency > 0
            assert assessment.overall_score > 0

    @pytest.mark.asyncio
    async def test_evaluate_water_source_success(self, service, sample_field_id, sample_water_quality_data, sample_reliability_history, sample_cost_data):
        """Test successful water source evaluation."""
        assessment = await service.evaluate_water_source(
            field_id=sample_field_id,
            source_type=WaterSourceType.WELL,
            source_capacity_gpm=200,
            water_quality_data=sample_water_quality_data,
            reliability_history=sample_reliability_history,
            cost_data=sample_cost_data
        )

        assert isinstance(assessment, WaterSourceAssessment)
        assert assessment.source_type == WaterSourceType.WELL
        assert assessment.available_capacity_gpm == 200
        assert 0 <= assessment.water_quality_score <= 1
        assert 0 <= assessment.reliability_score <= 1
        assert assessment.cost_per_gallon > 0
        assert 0 <= assessment.seasonal_variation_percent <= 100
        assert 0 <= assessment.sustainability_score <= 1
        assert isinstance(assessment.regulatory_compliance, bool)
        assert assessment.pumping_capacity_gpm > 0
        assert assessment.storage_capacity_gallons > 0

    @pytest.mark.asyncio
    async def test_evaluate_water_source_different_types(self, service, sample_field_id, sample_water_quality_data, sample_reliability_history, sample_cost_data):
        """Test water source evaluation for different source types."""
        source_types = [
            WaterSourceType.WELL,
            WaterSourceType.SURFACE_WATER,
            WaterSourceType.MUNICIPAL,
            WaterSourceType.RECYCLED
        ]

        for source_type in source_types:
            assessment = await service.evaluate_water_source(
                field_id=sample_field_id,
                source_type=source_type,
                source_capacity_gpm=150,
                water_quality_data=sample_water_quality_data,
                reliability_history=sample_reliability_history,
                cost_data=sample_cost_data
            )

            assert assessment.source_type == source_type
            assert assessment.available_capacity_gpm == 150
            assert assessment.water_quality_score > 0
            assert assessment.reliability_score > 0

    @pytest.mark.asyncio
    async def test_optimize_irrigation_efficiency_success(self, service, sample_field_id, sample_field_characteristics):
        """Test successful irrigation efficiency optimization."""
        # Create sample assessments
        system_assessment = IrrigationSystemAssessment(
            system_type=IrrigationSystemType.CENTER_PIVOT,
            current_efficiency=0.75,
            efficiency_level=IrrigationEfficiencyLevel.MODERATE,
            water_distribution_uniformity=0.85,
            pressure_consistency=0.80,
            coverage_area_percent=95,
            maintenance_status="fair",
            age_years=8,
            estimated_water_loss_percent=25,
            energy_efficiency_score=0.70,
            overall_score=75
        )

        water_source_assessment = WaterSourceAssessment(
            source_type=WaterSourceType.WELL,
            available_capacity_gpm=200,
            water_quality_score=0.90,
            reliability_score=0.85,
            cost_per_gallon=Decimal("0.003"),
            seasonal_variation_percent=15,
            sustainability_score=0.80,
            regulatory_compliance=True,
            pumping_capacity_gpm=190,
            storage_capacity_gallons=50000
        )

        optimizations = await service.optimize_irrigation_efficiency(
            field_id=sample_field_id,
            current_assessment=system_assessment,
            water_source_assessment=water_source_assessment,
            field_characteristics=sample_field_characteristics,
            budget_constraints=Decimal("5000")
        )

        assert isinstance(optimizations, list)
        assert len(optimizations) > 0

        for optimization in optimizations:
            assert isinstance(optimization, IrrigationOptimization)
            assert optimization.optimization_type
            assert optimization.description
            assert 0 <= optimization.potential_water_savings_percent <= 100
            assert optimization.potential_cost_savings_per_year >= 0
            assert optimization.implementation_cost >= 0
            assert optimization.payback_period_years >= 0
            assert optimization.implementation_timeline_days >= 0
            assert optimization.priority_level in ["high", "medium", "low"]

    @pytest.mark.asyncio
    async def test_assess_irrigation_constraints_success(self, service, sample_field_id, sample_field_characteristics):
        """Test successful irrigation constraint assessment."""
        # Create sample assessments
        system_assessment = IrrigationSystemAssessment(
            system_type=IrrigationSystemType.SPRINKLER,
            current_efficiency=0.65,
            efficiency_level=IrrigationEfficiencyLevel.MODERATE,
            water_distribution_uniformity=0.75,
            pressure_consistency=0.70,
            coverage_area_percent=90,
            maintenance_status="poor",
            age_years=12,
            estimated_water_loss_percent=35,
            energy_efficiency_score=0.60,
            overall_score=65
        )

        water_source_assessment = WaterSourceAssessment(
            source_type=WaterSourceType.SURFACE_WATER,
            available_capacity_gpm=100,
            water_quality_score=0.75,
            reliability_score=0.80,
            cost_per_gallon=Decimal("0.002"),
            seasonal_variation_percent=30,
            sustainability_score=0.70,
            regulatory_compliance=True,
            pumping_capacity_gpm=90,
            storage_capacity_gallons=30000
        )

        constraints = await service.assess_irrigation_constraints(
            field_id=sample_field_id,
            irrigation_system=system_assessment,
            water_source=water_source_assessment,
            field_characteristics=sample_field_characteristics,
            operational_constraints={}
        )

        assert isinstance(constraints, list)
        assert len(constraints) > 0

        for constraint in constraints:
            assert isinstance(constraint, IrrigationConstraint)
            assert constraint.constraint_type
            assert constraint.description
            assert constraint.impact_level in ["low", "medium", "high", "critical"]
            assert len(constraint.mitigation_options) > 0
            assert constraint.cost_impact >= 0
            assert constraint.timeline_impact_days >= 0

    @pytest.mark.asyncio
    async def test_generate_irrigation_schedule_success(self, service, sample_field_id, sample_weather_forecast, sample_soil_moisture_data):
        """Test successful irrigation schedule generation."""
        # Create sample assessments
        system_assessment = IrrigationSystemAssessment(
            system_type=IrrigationSystemType.CENTER_PIVOT,
            current_efficiency=0.85,
            efficiency_level=IrrigationEfficiencyLevel.HIGH,
            water_distribution_uniformity=0.90,
            pressure_consistency=0.85,
            coverage_area_percent=95,
            maintenance_status="good",
            age_years=5,
            estimated_water_loss_percent=15,
            energy_efficiency_score=0.80,
            overall_score=85
        )

        water_source_assessment = WaterSourceAssessment(
            source_type=WaterSourceType.WELL,
            available_capacity_gpm=250,
            water_quality_score=0.95,
            reliability_score=0.95,
            cost_per_gallon=Decimal("0.002"),
            seasonal_variation_percent=10,
            sustainability_score=0.85,
            regulatory_compliance=True,
            pumping_capacity_gpm=240,
            storage_capacity_gallons=60000
        )

        schedule = await service.generate_irrigation_schedule(
            field_id=sample_field_id,
            crop_type="corn",
            growth_stage="reproductive",
            soil_moisture_data=sample_soil_moisture_data,
            weather_forecast=sample_weather_forecast,
            irrigation_system=system_assessment,
            water_source=water_source_assessment
        )

        assert isinstance(schedule, dict)
        assert "field_id" in schedule
        assert "crop_type" in schedule
        assert "growth_stage" in schedule
        assert "schedule_period_days" in schedule
        assert "irrigation_events" in schedule
        assert "water_amounts" in schedule
        assert "total_water_requirement" in schedule
        assert "system_efficiency_factor" in schedule
        assert "water_source_capacity" in schedule
        assert "generated_at" in schedule
        assert "recommendations" in schedule

        assert schedule["field_id"] == str(sample_field_id)
        assert schedule["crop_type"] == "corn"
        assert schedule["growth_stage"] == "reproductive"
        assert schedule["schedule_period_days"] == 14
        assert isinstance(schedule["irrigation_events"], list)
        assert isinstance(schedule["water_amounts"], dict)
        assert isinstance(schedule["recommendations"], list)

    @pytest.mark.asyncio
    async def test_generate_irrigation_schedule_different_crops(self, service, sample_field_id, sample_weather_forecast, sample_soil_moisture_data):
        """Test irrigation schedule generation for different crop types."""
        crops = ["corn", "soybeans", "wheat"]
        
        # Create sample assessments
        system_assessment = IrrigationSystemAssessment(
            system_type=IrrigationSystemType.SPRINKLER,
            current_efficiency=0.80,
            efficiency_level=IrrigationEfficiencyLevel.HIGH,
            water_distribution_uniformity=0.85,
            pressure_consistency=0.80,
            coverage_area_percent=90,
            maintenance_status="good",
            age_years=6,
            estimated_water_loss_percent=20,
            energy_efficiency_score=0.75,
            overall_score=80
        )

        water_source_assessment = WaterSourceAssessment(
            source_type=WaterSourceType.WELL,
            available_capacity_gpm=200,
            water_quality_score=0.90,
            reliability_score=0.90,
            cost_per_gallon=Decimal("0.002"),
            seasonal_variation_percent=15,
            sustainability_score=0.80,
            regulatory_compliance=True,
            pumping_capacity_gpm=190,
            storage_capacity_gallons=50000
        )

        for crop in crops:
            schedule = await service.generate_irrigation_schedule(
                field_id=sample_field_id,
                crop_type=crop,
                growth_stage="vegetative",
                soil_moisture_data=sample_soil_moisture_data,
                weather_forecast=sample_weather_forecast,
                irrigation_system=system_assessment,
                water_source=water_source_assessment
            )

            assert schedule["crop_type"] == crop
            assert schedule["total_water_requirement"] > 0

    def test_calculate_maintenance_factor(self, service):
        """Test maintenance factor calculation."""
        # Test with good maintenance history
        good_maintenance = {"score": 0.9, "frequency_score": 0.8}
        factor = service._calculate_maintenance_factor(good_maintenance)
        assert 0 <= factor <= 1
        assert factor > 0.8

        # Test with poor maintenance history
        poor_maintenance = {"score": 0.5, "frequency_score": 0.4}
        factor = service._calculate_maintenance_factor(poor_maintenance)
        assert 0 <= factor <= 1
        assert factor < 0.6

        # Test with empty maintenance history
        factor = service._calculate_maintenance_factor({})
        assert factor == 0.8  # Default value

    def test_assess_pressure_consistency(self, service):
        """Test pressure consistency assessment."""
        # Test with small field and low elevation variation
        small_field = {"size_acres": 50, "elevation_variation_feet": 5}
        consistency = service._assess_pressure_consistency(small_field)
        assert 0 <= consistency <= 1
        assert consistency > 0.8

        # Test with large field and high elevation variation
        large_field = {"size_acres": 500, "elevation_variation_feet": 50}
        consistency = service._assess_pressure_consistency(large_field)
        assert 0 <= consistency <= 1
        assert consistency < 0.8

    def test_calculate_coverage_area(self, service):
        """Test coverage area calculation."""
        field_characteristics = {"size_acres": 100}
        
        # Test different system types
        coverage = service._calculate_coverage_area(field_characteristics, IrrigationSystemType.CENTER_PIVOT)
        assert 0 <= coverage <= 100
        assert coverage > 90  # Center pivot should have high coverage

        coverage = service._calculate_coverage_area(field_characteristics, IrrigationSystemType.DRIP)
        assert 0 <= coverage <= 100
        assert coverage > 95  # Drip should have very high coverage

    def test_assess_maintenance_status(self, service):
        """Test maintenance status assessment."""
        # Test good maintenance
        good_history = {"last_maintenance_days_ago": 30, "frequency_days": 60}
        status = service._assess_maintenance_status(good_history, 5)
        assert status in ["good", "fair", "poor"]

        # Test poor maintenance
        poor_history = {"last_maintenance_days_ago": 180, "frequency_days": 60}
        status = service._assess_maintenance_status(poor_history, 10)
        assert status in ["good", "fair", "poor"]

        # Test unknown maintenance
        status = service._assess_maintenance_status({}, 5)
        assert status == "unknown"

    def test_calculate_energy_efficiency(self, service):
        """Test energy efficiency calculation."""
        # Test different system types
        efficiency = service._calculate_energy_efficiency(IrrigationSystemType.DRIP, 0.9)
        assert 0 <= efficiency <= 1
        assert efficiency > 0.8  # Drip should be energy efficient

        efficiency = service._calculate_energy_efficiency(IrrigationSystemType.CENTER_PIVOT, 0.8)
        assert 0 <= efficiency <= 1
        assert efficiency < 0.8  # Center pivot should be less energy efficient

    def test_calculate_water_quality_score(self, service):
        """Test water quality score calculation."""
        # Test good water quality
        good_quality = {"ph": 7.0, "tds_ppm": 300, "salinity_ppm": 100}
        score = service._calculate_water_quality_score(good_quality)
        assert 0 <= score <= 1
        assert score > 0.8

        # Test poor water quality
        poor_quality = {"ph": 9.5, "tds_ppm": 2000, "salinity_ppm": 1000}
        score = service._calculate_water_quality_score(poor_quality)
        assert 0 <= score <= 1
        assert score <= 0.71  # Allow for floating point precision

    def test_calculate_reliability_score(self, service):
        """Test reliability score calculation."""
        source_data = {"typical_reliability": 0.9}
        
        # Test good reliability history
        good_history = {"uptime_percent": 98, "failures_per_year": 0}
        score = service._calculate_reliability_score(good_history, source_data)
        assert 0 <= score <= 1
        assert score > 0.8

        # Test poor reliability history
        poor_history = {"uptime_percent": 80, "failures_per_year": 5}
        score = service._calculate_reliability_score(poor_history, source_data)
        assert 0 <= score <= 1
        assert score < 0.7

    def test_calculate_cost_per_gallon(self, service):
        """Test cost per gallon calculation."""
        source_data = {"cost_per_gallon": Decimal("0.002")}
        cost_data = {
            "energy_cost_per_gallon": Decimal("0.001"),
            "maintenance_cost_per_gallon": Decimal("0.0005")
        }
        
        cost = service._calculate_cost_per_gallon(cost_data, source_data)
        assert cost > Decimal("0.002")  # Should include operational costs
        assert cost == Decimal("0.0035")  # 0.002 + 0.001 + 0.0005

    def test_assess_regulatory_compliance(self, service):
        """Test regulatory compliance assessment."""
        # Test compliant water quality
        compliant_quality = {"ph": 7.2, "tds_ppm": 800}
        compliance = service._assess_regulatory_compliance(WaterSourceType.WELL, compliant_quality)
        assert compliance is True

        # Test non-compliant water quality
        non_compliant_quality = {"ph": 9.5, "tds_ppm": 2500}
        compliance = service._assess_regulatory_compliance(WaterSourceType.WELL, non_compliant_quality)
        assert compliance is False

    def test_calculate_pumping_capacity(self, service):
        """Test pumping capacity calculation."""
        # Test different source types
        capacity = service._calculate_pumping_capacity(200, WaterSourceType.WELL)
        assert capacity > 180  # Wells should have high pumping efficiency

        capacity = service._calculate_pumping_capacity(200, WaterSourceType.SURFACE_WATER)
        assert capacity > 160  # Surface water should have moderate pumping efficiency

    def test_estimate_storage_capacity(self, service):
        """Test storage capacity estimation."""
        # Test different source types
        storage = service._estimate_storage_capacity(200, WaterSourceType.WELL)
        assert storage > 0
        assert storage == 200 * 60 * 24  # 24 hours for wells

        storage = service._estimate_storage_capacity(200, WaterSourceType.SURFACE_WATER)
        assert storage > 0
        assert storage == 200 * 60 * 48  # 48 hours for surface water

    def test_calculate_crop_water_requirement(self, service):
        """Test crop water requirement calculation."""
        weather_forecast = [
            {"temperature_celsius": 25},
            {"temperature_celsius": 30},
            {"temperature_celsius": 28}
        ]
        
        # Test different crops and growth stages
        requirement = service._calculate_crop_water_requirement("corn", "reproductive", weather_forecast)
        assert requirement > 0

        requirement = service._calculate_crop_water_requirement("soybeans", "vegetative", weather_forecast)
        assert requirement > 0

        requirement = service._calculate_crop_water_requirement("wheat", "maturity", weather_forecast)
        assert requirement > 0

    def test_calculate_soil_moisture_deficit(self, service):
        """Test soil moisture deficit calculation."""
        soil_moisture_data = {
            "current_moisture_percent": 40,
            "field_capacity_percent": 80
        }
        
        deficit = service._calculate_soil_moisture_deficit(soil_moisture_data, 0.3)
        assert deficit >= 0

        # Test with adequate moisture
        soil_moisture_data["current_moisture_percent"] = 70
        deficit = service._calculate_soil_moisture_deficit(soil_moisture_data, 0.3)
        assert deficit >= 0

    def test_determine_irrigation_timing(self, service):
        """Test irrigation timing determination."""
        weather_forecast = [
            {"precipitation_mm": 0, "wind_speed_kmh": 10},
            {"precipitation_mm": 5, "wind_speed_kmh": 15},
            {"precipitation_mm": 0, "wind_speed_kmh": 8}
        ]
        
        system_assessment = IrrigationSystemAssessment(
            system_type=IrrigationSystemType.SPRINKLER,
            current_efficiency=0.8,
            efficiency_level=IrrigationEfficiencyLevel.HIGH,
            water_distribution_uniformity=0.85,
            pressure_consistency=0.80,
            coverage_area_percent=90,
            maintenance_status="good",
            age_years=5,
            estimated_water_loss_percent=20,
            energy_efficiency_score=0.75,
            overall_score=80
        )
        
        timing = service._determine_irrigation_timing(0.2, weather_forecast, system_assessment)
        assert isinstance(timing, list)

    def test_calculate_irrigation_amounts(self, service):
        """Test irrigation amount calculations."""
        system_assessment = IrrigationSystemAssessment(
            system_type=IrrigationSystemType.CENTER_PIVOT,
            current_efficiency=0.85,
            efficiency_level=IrrigationEfficiencyLevel.HIGH,
            water_distribution_uniformity=0.90,
            pressure_consistency=0.85,
            coverage_area_percent=95,
            maintenance_status="good",
            age_years=5,
            estimated_water_loss_percent=15,
            energy_efficiency_score=0.80,
            overall_score=85
        )

        water_source_assessment = WaterSourceAssessment(
            source_type=WaterSourceType.WELL,
            available_capacity_gpm=250,
            water_quality_score=0.95,
            reliability_score=0.95,
            cost_per_gallon=Decimal("0.002"),
            seasonal_variation_percent=10,
            sustainability_score=0.85,
            regulatory_compliance=True,
            pumping_capacity_gpm=240,
            storage_capacity_gallons=60000
        )
        
        amounts = service._calculate_irrigation_amounts(0.3, system_assessment, water_source_assessment)
        assert isinstance(amounts, dict)
        assert "required_amount_inches" in amounts
        assert "actual_amount_inches" in amounts
        assert "gallons_per_acre" in amounts
        assert "irrigation_duration_hours" in amounts
        assert "efficiency_adjustment" in amounts

    def test_generate_schedule_recommendations(self, service):
        """Test schedule recommendation generation."""
        irrigation_timing = [{"day": 1, "recommended": True}]
        irrigation_amounts = {"irrigation_duration_hours": 6}
        
        system_assessment = IrrigationSystemAssessment(
            system_type=IrrigationSystemType.SPRINKLER,
            current_efficiency=0.75,
            efficiency_level=IrrigationEfficiencyLevel.MODERATE,
            water_distribution_uniformity=0.80,
            pressure_consistency=0.75,
            coverage_area_percent=90,
            maintenance_status="fair",
            age_years=8,
            estimated_water_loss_percent=25,
            energy_efficiency_score=0.70,
            overall_score=75
        )
        
        recommendations = service._generate_schedule_recommendations(irrigation_timing, irrigation_amounts, system_assessment)
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

    @pytest.mark.asyncio
    async def test_error_handling_assess_irrigation_system(self, service):
        """Test error handling in irrigation system assessment."""
        with pytest.raises(Exception):
            await service.assess_irrigation_system(
                field_id=uuid4(),
                system_type=None,  # Invalid system type
                system_age_years=5,
                maintenance_history={},
                field_characteristics={}
            )

    @pytest.mark.asyncio
    async def test_error_handling_evaluate_water_source(self, service):
        """Test error handling in water source evaluation."""
        with pytest.raises(Exception):
            await service.evaluate_water_source(
                field_id=uuid4(),
                source_type=None,  # Invalid source type
                source_capacity_gpm=200,
                water_quality_data={},
                reliability_history={},
                cost_data={}
            )

    @pytest.mark.asyncio
    async def test_error_handling_optimize_irrigation_efficiency(self, service):
        """Test error handling in irrigation optimization."""
        with pytest.raises(Exception):
            await service.optimize_irrigation_efficiency(
                field_id=uuid4(),
                current_assessment=None,  # Invalid assessment
                water_source_assessment=None,  # Invalid assessment
                field_characteristics={},
                budget_constraints=None
            )

    @pytest.mark.asyncio
    async def test_error_handling_generate_irrigation_schedule(self, service):
        """Test error handling in irrigation schedule generation."""
        with pytest.raises(Exception):
            await service.generate_irrigation_schedule(
                field_id=uuid4(),
                crop_type="corn",
                growth_stage="vegetative",
                soil_moisture_data={},
                weather_forecast=[],  # Empty forecast
                irrigation_system=None,  # Invalid system
                water_source=None  # Invalid source
            )

    def test_irrigation_system_database_initialization(self, service):
        """Test irrigation system database initialization."""
        assert isinstance(service.irrigation_system_database, dict)
        assert len(service.irrigation_system_database) > 0
        
        # Check that all system types have required fields
        for system_type, characteristics in service.irrigation_system_database.items():
            assert "typical_efficiency" in characteristics
            assert "water_distribution_uniformity" in characteristics
            assert "energy_requirements" in characteristics
            assert "maintenance_frequency" in characteristics
            assert "suitable_crops" in characteristics
            assert "field_size_range" in characteristics
            assert "cost_per_acre" in characteristics

    def test_water_source_database_initialization(self, service):
        """Test water source database initialization."""
        assert isinstance(service.water_source_database, dict)
        assert len(service.water_source_database) > 0
        
        # Check that all source types have required fields
        for source_type, characteristics in service.water_source_database.items():
            assert "typical_reliability" in characteristics
            assert "cost_per_gallon" in characteristics
            assert "seasonal_variation" in characteristics
            assert "sustainability_score" in characteristics
            assert "pumping_requirements" in characteristics
            assert "water_quality" in characteristics

    def test_optimization_algorithms_initialization(self, service):
        """Test optimization algorithms initialization."""
        assert isinstance(service.optimization_algorithms, dict)
        assert len(service.optimization_algorithms) > 0
        
        # Check that optimization categories exist
        assert "efficiency_improvement" in service.optimization_algorithms
        assert "scheduling_optimization" in service.optimization_algorithms
        assert "water_source_optimization" in service.optimization_algorithms

    @pytest.mark.asyncio
    async def test_integration_assessment_to_optimization(self, service, sample_field_id, sample_field_characteristics):
        """Test integration from assessment to optimization."""
        # First, assess the irrigation system
        system_assessment = await service.assess_irrigation_system(
            field_id=sample_field_id,
            system_type=IrrigationSystemType.CENTER_PIVOT,
            system_age_years=8,
            maintenance_history={"score": 0.6, "frequency_score": 0.5},
            field_characteristics=sample_field_characteristics
        )

        # Then, evaluate water source
        water_source_assessment = await service.evaluate_water_source(
            field_id=sample_field_id,
            source_type=WaterSourceType.WELL,
            source_capacity_gpm=180,
            water_quality_data={"ph": 7.1, "tds_ppm": 350, "salinity_ppm": 120},
            reliability_history={"uptime_percent": 92, "failures_per_year": 2},
            cost_data={"energy_cost_per_gallon": Decimal("0.001"), "maintenance_cost_per_gallon": Decimal("0.0005")}
        )

        # Finally, optimize based on assessments
        optimizations = await service.optimize_irrigation_efficiency(
            field_id=sample_field_id,
            current_assessment=system_assessment,
            water_source_assessment=water_source_assessment,
            field_characteristics=sample_field_characteristics,
            budget_constraints=Decimal("3000")
        )

        # Verify the integration works
        assert len(optimizations) > 0
        assert all(isinstance(opt, IrrigationOptimization) for opt in optimizations)
        
        # Check that optimizations are relevant to the assessments
        optimization_types = [opt.optimization_type for opt in optimizations]
        # Check for any optimization types that indicate system improvements
        relevant_optimizations = [
            "pressure_optimization",
            "system_maintenance", 
            "weather_based_scheduling",
            "soil_moisture_scheduling",
            "storage_optimization"
        ]
        assert any(opt_type in optimization_types for opt_type in relevant_optimizations)
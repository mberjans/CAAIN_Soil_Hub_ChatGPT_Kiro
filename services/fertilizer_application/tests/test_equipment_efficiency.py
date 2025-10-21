"""
Comprehensive tests for equipment efficiency and optimization service.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta

from src.services.equipment_efficiency_service import (
    EquipmentEfficiencyService, EfficiencyAnalysisRequest, EfficiencyAnalysisResponse,
    OptimizationType, EfficiencyMetric, TimingOptimization, RouteOptimization,
    MaintenanceOptimization
)
from src.models.equipment_models import (
    Equipment, EquipmentCategory, EquipmentStatus, MaintenanceLevel
)


class TestEquipmentEfficiencyService:
    """Test suite for equipment efficiency service."""
    
    @pytest.fixture
    def service(self):
        return EquipmentEfficiencyService()
    
    @pytest.fixture
    def sample_equipment(self):
        return Equipment(
            equipment_id="test_equipment_001",
            name="Test Spreader",
            category=EquipmentCategory.SPREADING,
            manufacturer="Test Manufacturer",
            model="Test Model",
            year=2020,
            capacity=1000,
            capacity_unit="cubic_feet",
            status=EquipmentStatus.OPERATIONAL,
            maintenance_level=MaintenanceLevel.INTERMEDIATE
        )
    
    @pytest.fixture
    def sample_request(self):
        return EfficiencyAnalysisRequest(
            equipment_id="test_equipment_001",
            farm_id="test_farm_001",
            field_conditions={
                "field_size_acres": 100,
                "soil_type": "loam",
                "topography": "flat",
                "field_shape": "rectangular"
            },
            weather_conditions={
                "wind_speed_mph": 5,
                "temperature_f": 75,
                "humidity_percent": 60
            },
            analysis_types=[OptimizationType.APPLICATION_EFFICIENCY],
            time_horizon_days=30
        )
    
    @pytest.mark.asyncio
    async def test_analyze_equipment_efficiency_success(self, service, sample_equipment, sample_request):
        """Test successful equipment efficiency analysis."""
        response = await service.analyze_equipment_efficiency(sample_request, sample_equipment)
        
        assert isinstance(response, EfficiencyAnalysisResponse)
        assert response.equipment_id == sample_request.equipment_id
        assert response.farm_id == sample_request.farm_id
        assert response.analysis_id is not None
        assert response.processing_time_ms > 0
        
        # Check efficiency metrics
        assert "application_accuracy" in response.efficiency_metrics
        assert "coverage_uniformity" in response.efficiency_metrics
        assert "speed_efficiency" in response.efficiency_metrics
        assert "fuel_efficiency" in response.efficiency_metrics
        assert "labor_efficiency" in response.efficiency_metrics
        assert "maintenance_efficiency" in response.efficiency_metrics
        assert "overall_efficiency" in response.efficiency_metrics
        
        # Check that all metrics are between 0 and 1
        for metric, value in response.efficiency_metrics.items():
            assert 0 <= value <= 1, f"Metric {metric} value {value} is not between 0 and 1"
        
        # Check optimization recommendations
        assert isinstance(response.optimization_recommendations, list)
        
        # Check performance predictions
        assert "time_horizon_days" in response.performance_predictions
        assert "predicted_efficiency_trend" in response.performance_predictions
        assert "maintenance_needs" in response.performance_predictions
        
        # Check maintenance schedule
        assert "equipment_id" in response.maintenance_schedule
        assert "maintenance_items" in response.maintenance_schedule
        
        # Check cost-benefit analysis
        assert "total_investment" in response.cost_benefit_analysis
        assert "total_benefits" in response.cost_benefit_analysis
        assert "roi_percentage" in response.cost_benefit_analysis
    
    @pytest.mark.asyncio
    async def test_calculate_application_accuracy(self, service, sample_equipment):
        """Test application accuracy calculation."""
        field_conditions = {
            "field_size_acres": 100,
            "soil_type": "loam",
            "topography": "flat"
        }
        
        accuracy = await service._calculate_application_accuracy(sample_equipment, field_conditions)
        
        assert 0 <= accuracy <= 1
        assert isinstance(accuracy, float)
        
        # Test with different field conditions
        small_field_conditions = field_conditions.copy()
        small_field_conditions["field_size_acres"] = 25
        
        small_accuracy = await service._calculate_application_accuracy(sample_equipment, small_field_conditions)
        assert small_accuracy < accuracy  # Smaller fields should have lower accuracy
    
    @pytest.mark.asyncio
    async def test_calculate_coverage_uniformity(self, service, sample_equipment):
        """Test coverage uniformity calculation."""
        field_conditions = {
            "field_size_acres": 100,
            "soil_type": "loam",
            "topography": "flat"
        }
        
        uniformity = await service._calculate_coverage_uniformity(sample_equipment, field_conditions)
        
        assert 0 <= uniformity <= 1
        assert isinstance(uniformity, float)
        
        # Test with different topography
        hilly_conditions = field_conditions.copy()
        hilly_conditions["topography"] = "hilly"
        
        hilly_uniformity = await service._calculate_coverage_uniformity(sample_equipment, hilly_conditions)
        assert hilly_uniformity < uniformity  # Hilly terrain should have lower uniformity
    
    @pytest.mark.asyncio
    async def test_calculate_speed_efficiency(self, service, sample_equipment):
        """Test speed efficiency calculation."""
        field_conditions = {
            "field_size_acres": 100,
            "soil_type": "loam",
            "topography": "flat"
        }
        
        weather_conditions = {
            "wind_speed_mph": 5,
            "temperature_f": 75
        }
        
        speed_eff = await service._calculate_speed_efficiency(sample_equipment, field_conditions, weather_conditions)
        
        assert 0 <= speed_eff <= 1
        assert isinstance(speed_eff, float)
        
        # Test with high wind conditions
        high_wind_conditions = weather_conditions.copy()
        high_wind_conditions["wind_speed_mph"] = 20
        
        high_wind_speed_eff = await service._calculate_speed_efficiency(sample_equipment, field_conditions, high_wind_conditions)
        assert high_wind_speed_eff < speed_eff  # High winds should reduce speed efficiency
    
    @pytest.mark.asyncio
    async def test_calculate_fuel_efficiency(self, service, sample_equipment):
        """Test fuel efficiency calculation."""
        field_conditions = {
            "field_size_acres": 100,
            "soil_type": "loam",
            "topography": "flat"
        }
        
        fuel_eff = await service._calculate_fuel_efficiency(sample_equipment, field_conditions)
        
        assert 0 <= fuel_eff <= 1
        assert isinstance(fuel_eff, float)
        
        # Test with different field sizes
        large_field_conditions = field_conditions.copy()
        large_field_conditions["field_size_acres"] = 500
        
        large_fuel_eff = await service._calculate_fuel_efficiency(sample_equipment, large_field_conditions)
        assert large_fuel_eff > fuel_eff  # Larger fields should have better fuel efficiency
    
    @pytest.mark.asyncio
    async def test_calculate_labor_efficiency(self, service, sample_equipment):
        """Test labor efficiency calculation."""
        field_conditions = {
            "field_size_acres": 100,
            "soil_type": "loam",
            "topography": "flat"
        }
        
        labor_eff = await service._calculate_labor_efficiency(sample_equipment, field_conditions)
        
        assert 0 <= labor_eff <= 1
        assert isinstance(labor_eff, float)
        
        # Test with different maintenance levels
        basic_maintenance_equipment = sample_equipment.model_copy()
        basic_maintenance_equipment.maintenance_level = MaintenanceLevel.BASIC
        
        basic_labor_eff = await service._calculate_labor_efficiency(basic_maintenance_equipment, field_conditions)
        assert basic_labor_eff > labor_eff  # Basic maintenance should have higher labor efficiency
    
    @pytest.mark.asyncio
    async def test_calculate_maintenance_efficiency(self, service, sample_equipment):
        """Test maintenance efficiency calculation."""
        maintenance_eff = await service._calculate_maintenance_efficiency(sample_equipment)
        
        assert 0 <= maintenance_eff <= 1
        assert isinstance(maintenance_eff, float)
        
        # Test with older equipment
        old_equipment = sample_equipment.model_copy()
        old_equipment.year = 2010
        
        old_maintenance_eff = await service._calculate_maintenance_efficiency(old_equipment)
        assert old_maintenance_eff < maintenance_eff  # Older equipment should have lower maintenance efficiency
    
    @pytest.mark.asyncio
    async def test_generate_optimization_recommendations(self, service, sample_equipment, sample_request):
        """Test optimization recommendations generation."""
        efficiency_metrics = {
            "application_accuracy": 0.7,
            "coverage_uniformity": 0.6,
            "speed_efficiency": 0.8,
            "fuel_efficiency": 0.65,
            "labor_efficiency": 0.75,
            "maintenance_efficiency": 0.8,
            "overall_efficiency": 0.72
        }
        
        recommendations = await service._generate_optimization_recommendations(
            sample_equipment, sample_request, efficiency_metrics
        )
        
        assert isinstance(recommendations, list)
        
        # Should have recommendations for low efficiency metrics
        recommendation_types = [rec["type"] for rec in recommendations]
        assert "application_accuracy" in recommendation_types
        assert "coverage_uniformity" in recommendation_types
        assert "fuel_efficiency" in recommendation_types
        
        # Check recommendation structure
        for rec in recommendations:
            assert "type" in rec
            assert "priority" in rec
            assert "description" in rec
            assert "actions" in rec
            assert "expected_improvement" in rec
            assert "estimated_cost" in rec
    
    @pytest.mark.asyncio
    async def test_create_performance_predictions(self, service, sample_equipment):
        """Test performance predictions creation."""
        efficiency_metrics = {
            "application_accuracy": 0.8,
            "coverage_uniformity": 0.75,
            "speed_efficiency": 0.7,
            "fuel_efficiency": 0.8,
            "labor_efficiency": 0.75,
            "maintenance_efficiency": 0.7
        }
        
        predictions = await service._create_performance_predictions(sample_equipment, efficiency_metrics, 30)
        
        assert "time_horizon_days" in predictions
        assert "predicted_efficiency_trend" in predictions
        assert "maintenance_needs" in predictions
        
        assert predictions["time_horizon_days"] == 30
        
        # Check predicted efficiency trend
        trend = predictions["predicted_efficiency_trend"]
        for metric in efficiency_metrics:
            assert metric in trend
            trend_data = trend[metric]
            assert "current_value" in trend_data
            assert "predicted_value" in trend_data
            assert "degradation_rate" in trend_data
            assert "confidence" in trend_data
            
            # Predicted value should be lower than current value
            assert trend_data["predicted_value"] <= trend_data["current_value"]
    
    @pytest.mark.asyncio
    async def test_generate_maintenance_schedule(self, service, sample_equipment):
        """Test maintenance schedule generation."""
        efficiency_metrics = {
            "application_accuracy": 0.7,
            "coverage_uniformity": 0.6,
            "speed_efficiency": 0.8,
            "fuel_efficiency": 0.65,
            "labor_efficiency": 0.75,
            "maintenance_efficiency": 0.8
        }
        
        schedule = await service._generate_maintenance_schedule(sample_equipment, efficiency_metrics)
        
        assert "equipment_id" in schedule
        assert "schedule_type" in schedule
        assert "maintenance_items" in schedule
        assert "total_estimated_cost" in schedule
        assert "total_downtime_hours" in schedule
        
        assert schedule["equipment_id"] == sample_equipment.equipment_id
        assert schedule["schedule_type"] == "preventive"
        
        # Should have maintenance items for low efficiency metrics
        maintenance_types = [item["type"] for item in schedule["maintenance_items"]]
        assert "calibration" in maintenance_types  # For low application accuracy
        assert "nozzle_inspection" in maintenance_types  # For low coverage uniformity
        assert "engine_service" in maintenance_types  # For low fuel efficiency
    
    @pytest.mark.asyncio
    async def test_perform_cost_benefit_analysis(self, service, sample_equipment):
        """Test cost-benefit analysis."""
        optimization_recommendations = [
            {
                "type": "application_accuracy",
                "estimated_cost": 500,
                "expected_improvement": 0.1
            },
            {
                "type": "fuel_efficiency",
                "estimated_cost": 800,
                "expected_improvement": 0.15
            }
        ]
        
        analysis = await service._perform_cost_benefit_analysis(optimization_recommendations, sample_equipment)
        
        assert "total_investment" in analysis
        assert "total_benefits" in analysis
        assert "roi_percentage" in analysis
        assert "payback_period_months" in analysis
        assert "recommendations" in analysis
        
        assert analysis["total_investment"] == 1300  # 500 + 800
        assert analysis["total_benefits"] > 0
        assert analysis["roi_percentage"] > 0
        assert analysis["payback_period_months"] > 0
        
        # Check individual recommendations
        assert len(analysis["recommendations"]) == 2
        for rec in analysis["recommendations"]:
            assert "type" in rec
            assert "investment" in rec
            assert "annual_benefits" in rec
            assert "roi" in rec
    
    @pytest.mark.asyncio
    async def test_optimize_timing(self, service, sample_equipment):
        """Test timing optimization."""
        field_conditions = {
            "field_size_acres": 100,
            "soil_type": "loam",
            "topography": "flat"
        }
        
        weather_conditions = {
            "wind_speed_mph": 5,
            "temperature_f": 75,
            "humidity_percent": 60
        }
        
        timing_opt = await service._optimize_timing(sample_equipment, field_conditions, weather_conditions)
        
        assert isinstance(timing_opt, TimingOptimization)
        assert timing_opt.optimal_start_time is not None
        assert timing_opt.optimal_end_time is not None
        assert isinstance(timing_opt.weather_windows, list)
        assert isinstance(timing_opt.efficiency_gains, float)
        assert isinstance(timing_opt.risk_factors, list)
        assert isinstance(timing_opt.recommendations, list)
        
        assert 0 <= timing_opt.efficiency_gains <= 1
    
    @pytest.mark.asyncio
    async def test_optimize_route(self, service, sample_equipment):
        """Test route optimization."""
        field_conditions = {
            "field_size_acres": 100,
            "soil_type": "loam",
            "topography": "flat",
            "field_shape": "rectangular"
        }
        
        route_opt = await service._optimize_route(sample_equipment, field_conditions)
        
        assert isinstance(route_opt, RouteOptimization)
        assert isinstance(route_opt.optimal_route, list)
        assert isinstance(route_opt.total_distance, float)
        assert isinstance(route_opt.estimated_time, float)
        assert isinstance(route_opt.fuel_savings, float)
        assert isinstance(route_opt.efficiency_improvement, float)
        assert isinstance(route_opt.turning_points, list)
        
        assert route_opt.total_distance > 0
        assert route_opt.estimated_time > 0
        assert route_opt.fuel_savings >= 0
        assert 0 <= route_opt.efficiency_improvement <= 1
    
    @pytest.mark.asyncio
    async def test_optimize_maintenance(self, service, sample_equipment):
        """Test maintenance optimization."""
        efficiency_metrics = {
            "application_accuracy": 0.6,  # Low efficiency to trigger maintenance
            "coverage_uniformity": 0.7,
            "speed_efficiency": 0.8,
            "fuel_efficiency": 0.75,
            "labor_efficiency": 0.8,
            "maintenance_efficiency": 0.7
        }
        
        maintenance_opt = await service._optimize_maintenance(sample_equipment, efficiency_metrics)
        
        assert isinstance(maintenance_opt, MaintenanceOptimization)
        assert maintenance_opt.next_maintenance_date is not None
        assert maintenance_opt.maintenance_type is not None
        assert isinstance(maintenance_opt.estimated_cost, float)
        assert isinstance(maintenance_opt.downtime_hours, float)
        assert isinstance(maintenance_opt.efficiency_impact, float)
        assert isinstance(maintenance_opt.preventive_actions, list)
        
        assert maintenance_opt.estimated_cost > 0
        assert maintenance_opt.downtime_hours > 0
        assert 0 <= maintenance_opt.efficiency_impact <= 1
    
    @pytest.mark.asyncio
    async def test_optimize_fuel_usage(self, service, sample_equipment):
        """Test fuel usage optimization."""
        field_conditions = {
            "field_size_acres": 100,
            "soil_type": "loam",
            "topography": "flat"
        }
        
        fuel_opt = await service._optimize_fuel_usage(sample_equipment, field_conditions)
        
        assert isinstance(fuel_opt, dict)
        assert "current_fuel_usage" in fuel_opt
        assert "optimized_fuel_usage" in fuel_opt
        assert "fuel_savings" in fuel_opt
        assert "cost_savings" in fuel_opt
        assert "optimization_actions" in fuel_opt
        
        assert fuel_opt["current_fuel_usage"] > 0
        assert fuel_opt["optimized_fuel_usage"] > 0
        assert fuel_opt["fuel_savings"] >= 0
        assert fuel_opt["cost_savings"] >= 0
        assert isinstance(fuel_opt["optimization_actions"], list)
    
    @pytest.mark.asyncio
    async def test_optimize_labor_usage(self, service, sample_equipment):
        """Test labor usage optimization."""
        field_conditions = {
            "field_size_acres": 100,
            "soil_type": "loam",
            "topography": "flat"
        }
        
        labor_opt = await service._optimize_labor_usage(sample_equipment, field_conditions)
        
        assert isinstance(labor_opt, dict)
        assert "current_labor_hours" in labor_opt
        assert "optimized_labor_hours" in labor_opt
        assert "labor_savings" in labor_opt
        assert "cost_savings" in labor_opt
        assert "optimization_actions" in labor_opt
        
        assert labor_opt["current_labor_hours"] > 0
        assert labor_opt["optimized_labor_hours"] > 0
        assert labor_opt["labor_savings"] >= 0
        assert labor_opt["cost_savings"] >= 0
        assert isinstance(labor_opt["optimization_actions"], list)
    
    def test_efficiency_benchmarks_initialization(self, service):
        """Test that efficiency benchmarks are properly initialized."""
        benchmarks = service.efficiency_benchmarks
        
        assert EquipmentCategory.SPREADING in benchmarks
        assert EquipmentCategory.SPRAYING in benchmarks
        assert EquipmentCategory.INJECTION in benchmarks
        assert EquipmentCategory.IRRIGATION in benchmarks
        
        # Check benchmark structure
        for category, category_benchmarks in benchmarks.items():
            assert "application_accuracy" in category_benchmarks
            assert "coverage_uniformity" in category_benchmarks
            assert "speed_efficiency" in category_benchmarks
            assert "fuel_efficiency" in category_benchmarks
            
            # Check benchmark levels
            for metric, levels in category_benchmarks.items():
                assert "excellent" in levels
                assert "good" in levels
                assert "acceptable" in levels
                assert "poor" in levels
                
                # Check that values are in descending order
                assert levels["excellent"] >= levels["good"]
                assert levels["good"] >= levels["acceptable"]
                assert levels["acceptable"] >= levels["poor"]
    
    def test_optimization_algorithms_initialization(self, service):
        """Test that optimization algorithms are properly initialized."""
        algorithms = service.optimization_algorithms
        
        assert "timing_optimization" in algorithms
        assert "route_optimization" in algorithms
        assert "maintenance_optimization" in algorithms
        assert "fuel_optimization" in algorithms
        assert "labor_optimization" in algorithms
        
        # Check that all algorithms are callable
        for algorithm_name, algorithm_func in algorithms.items():
            assert callable(algorithm_func), f"Algorithm {algorithm_name} is not callable"
    
    @pytest.mark.asyncio
    async def test_error_handling(self, service):
        """Test error handling in efficiency analysis."""
        # Test with invalid equipment
        invalid_equipment = None
        
        request = EfficiencyAnalysisRequest(
            equipment_id="invalid",
            farm_id="test_farm",
            field_conditions={},
            analysis_types=[OptimizationType.APPLICATION_EFFICIENCY],
            time_horizon_days=30
        )
        
        with pytest.raises(Exception):
            await service.analyze_equipment_efficiency(request, invalid_equipment)
    
    @pytest.mark.asyncio
    async def test_performance_requirements(self, service, sample_equipment, sample_request):
        """Test that analysis meets performance requirements."""
        import time
        
        start_time = time.time()
        response = await service.analyze_equipment_efficiency(sample_request, sample_equipment)
        elapsed_time = time.time() - start_time
        
        # Should complete within reasonable time (less than 5 seconds)
        assert elapsed_time < 5.0, f"Analysis took {elapsed_time:.2f}s, exceeds 5s requirement"
        
        # Response should include processing time
        assert response.processing_time_ms > 0
        assert response.processing_time_ms < 5000  # Less than 5 seconds in milliseconds


class TestEfficiencyAnalysisRequest:
    """Test suite for efficiency analysis request model."""
    
    def test_request_creation(self):
        """Test efficiency analysis request creation."""
        request = EfficiencyAnalysisRequest(
            equipment_id="test_equipment",
            farm_id="test_farm",
            field_conditions={"field_size_acres": 100},
            analysis_types=[OptimizationType.APPLICATION_EFFICIENCY],
            time_horizon_days=30
        )
        
        assert request.equipment_id == "test_equipment"
        assert request.farm_id == "test_farm"
        assert request.field_conditions["field_size_acres"] == 100
        assert OptimizationType.APPLICATION_EFFICIENCY in request.analysis_types
        assert request.time_horizon_days == 30
    
    def test_request_defaults(self):
        """Test efficiency analysis request defaults."""
        request = EfficiencyAnalysisRequest(
            equipment_id="test_equipment",
            farm_id="test_farm",
            field_conditions={}
        )
        
        assert request.weather_conditions is None
        assert request.operational_parameters is None
        assert request.analysis_types is None
        assert request.time_horizon_days == 30


class TestOptimizationTypes:
    """Test suite for optimization types enum."""
    
    def test_optimization_type_values(self):
        """Test optimization type enum values."""
        assert OptimizationType.APPLICATION_EFFICIENCY == "application_efficiency"
        assert OptimizationType.TIMING_OPTIMIZATION == "timing_optimization"
        assert OptimizationType.ROUTE_OPTIMIZATION == "route_optimization"
        assert OptimizationType.MAINTENANCE_OPTIMIZATION == "maintenance_optimization"
        assert OptimizationType.FUEL_OPTIMIZATION == "fuel_optimization"
        assert OptimizationType.LABOR_OPTIMIZATION == "labor_optimization"


class TestEfficiencyMetrics:
    """Test suite for efficiency metrics enum."""
    
    def test_efficiency_metric_values(self):
        """Test efficiency metric enum values."""
        assert EfficiencyMetric.APPLICATION_ACCURACY == "application_accuracy"
        assert EfficiencyMetric.COVERAGE_UNIFORMITY == "coverage_uniformity"
        assert EfficiencyMetric.SPEED_EFFICIENCY == "speed_efficiency"
        assert EfficiencyMetric.FUEL_EFFICIENCY == "fuel_efficiency"
        assert EfficiencyMetric.LABOR_EFFICIENCY == "labor_efficiency"
        assert EfficiencyMetric.MAINTENANCE_EFFICIENCY == "maintenance_efficiency"
        assert EfficiencyMetric.OVERALL_EFFICIENCY == "overall_efficiency"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
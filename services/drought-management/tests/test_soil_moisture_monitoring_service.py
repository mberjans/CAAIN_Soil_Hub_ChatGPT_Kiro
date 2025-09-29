"""
Comprehensive tests for Soil Moisture Monitoring Service

Tests for soil moisture tracking, evapotranspiration calculations,
moisture deficit predictions, and irrigation recommendations.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from src.services.soil_moisture_monitoring_service import (
    SoilMoistureMonitoringService,
    WaterBalanceModel,
    EvapotranspirationModel,
    CropCoefficientModel,
    MockWeatherService,
    MockCropService,
    MockFieldService
)
from src.models.drought_models import (
    SoilMoistureStatus,
    SoilMoistureLevel,
    DroughtRiskLevel
)

class TestSoilMoistureMonitoringService:
    """Test suite for SoilMoistureMonitoringService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return SoilMoistureMonitoringService()
    
    @pytest.fixture
    def field_id(self):
        """Create test field ID."""
        return uuid4()
    
    @pytest.fixture
    def soil_characteristics(self):
        """Create test soil characteristics."""
        return {
            "soil_type": "clay_loam",
            "field_capacity": 0.35,
            "wilting_point": 0.15,
            "bulk_density": 1.3,
            "monitoring_depth": 100,
            "saturation_point": 0.45
        }
    
    @pytest.fixture
    def mock_weather_data(self):
        """Create mock weather data."""
        return {
            "temperature": 25.0,
            "humidity": 60.0,
            "precipitation": 0.0,
            "wind_speed": 2.0,
            "solar_radiation": 20.0
        }
    
    @pytest.fixture
    def mock_crop_data(self):
        """Create mock crop data."""
        return {
            "crop_type": "corn",
            "growth_stage": "vegetative",
            "planting_date": datetime.utcnow() - timedelta(days=30),
            "expected_harvest": datetime.utcnow() + timedelta(days=90)
        }
    
    @pytest.mark.asyncio
    async def test_initialize_service(self, service):
        """Test service initialization."""
        await service.initialize()
        assert service.initialized is True
        assert service.weather_service is not None
        assert service.crop_service is not None
        assert service.field_service is not None
        assert len(service.prediction_models) > 0
    
    @pytest.mark.asyncio
    async def test_cleanup_service(self, service):
        """Test service cleanup."""
        await service.initialize()
        await service.cleanup()
        assert service.initialized is False
    
    @pytest.mark.asyncio
    async def test_setup_field_monitoring(self, service, field_id, soil_characteristics):
        """Test field monitoring setup."""
        await service.initialize()
        
        config = await service.setup_field_monitoring(field_id, soil_characteristics)
        
        assert config["field_id"] == field_id
        assert config["soil_characteristics"] == soil_characteristics
        assert "alert_thresholds" in config
        assert "monitoring_depth_cm" in config
        assert str(field_id) in service.monitoring_configs
    
    @pytest.mark.asyncio
    async def test_get_current_moisture_status(self, service, field_id, soil_characteristics):
        """Test getting current moisture status."""
        await service.initialize()
        await service.setup_field_monitoring(field_id, soil_characteristics)
        
        status = await service.get_current_moisture_status(field_id)
        
        assert isinstance(status, SoilMoistureStatus)
        assert status.field_id == field_id
        assert 0 <= status.surface_moisture_percent <= 100
        assert 0 <= status.deep_moisture_percent <= 100
        assert status.available_water_capacity >= 0
        assert isinstance(status.moisture_level, SoilMoistureLevel)
        assert isinstance(status.irrigation_recommendation, str)
    
    @pytest.mark.asyncio
    async def test_predict_moisture_deficit(self, service, field_id, soil_characteristics):
        """Test moisture deficit prediction."""
        await service.initialize()
        await service.setup_field_monitoring(field_id, soil_characteristics)
        
        prediction = await service.predict_moisture_deficit(field_id, 7)
        
        assert "field_id" in prediction
        assert "prediction_period" in prediction
        assert "deficit_predictions" in prediction
        assert "overall_risk" in prediction
        assert len(prediction["deficit_predictions"]) == 7
        
        for day_prediction in prediction["deficit_predictions"]:
            assert "date" in day_prediction
            assert "predicted_moisture" in day_prediction
            assert "deficit" in day_prediction
            assert "risk_level" in day_prediction
    
    @pytest.mark.asyncio
    async def test_calculate_evapotranspiration(self, service, field_id, soil_characteristics):
        """Test evapotranspiration calculation."""
        await service.initialize()
        await service.setup_field_monitoring(field_id, soil_characteristics)
        
        et_result = await service.calculate_evapotranspiration(field_id, datetime.utcnow())
        
        assert "field_id" in et_result
        assert "date" in et_result
        assert "reference_et_mm" in et_result
        assert "crop_coefficient" in et_result
        assert "crop_et_mm" in et_result
        assert "soil_evaporation_mm" in et_result
        assert "total_et_mm" in et_result
        assert "weather_data" in et_result
        assert "crop_data" in et_result
        
        # Validate ET values are reasonable
        assert et_result["reference_et_mm"] >= 0
        assert 0 <= et_result["crop_coefficient"] <= 2.0
        assert et_result["crop_et_mm"] >= 0
        assert et_result["soil_evaporation_mm"] >= 0
        assert et_result["total_et_mm"] >= 0
    
    @pytest.mark.asyncio
    async def test_get_irrigation_recommendations(self, service, field_id, soil_characteristics):
        """Test irrigation recommendations."""
        await service.initialize()
        await service.setup_field_monitoring(field_id, soil_characteristics)
        
        recommendations = await service.get_irrigation_recommendations(field_id)
        
        assert "recommendation" in recommendations
        assert "priority" in recommendations
        assert "irrigation_depth_mm" in recommendations
        assert "irrigation_depth_inches" in recommendations
        assert "timing" in recommendations
        assert "frequency" in recommendations
        
        # Validate irrigation depth is reasonable
        assert recommendations["irrigation_depth_mm"] >= 0
        assert recommendations["irrigation_depth_inches"] >= 0
    
    @pytest.mark.asyncio
    async def test_get_moisture_alerts(self, service, field_id, soil_characteristics):
        """Test moisture alerts generation."""
        await service.initialize()
        await service.setup_field_monitoring(field_id, soil_characteristics)
        
        alerts = await service.get_moisture_alerts(field_id)
        
        assert isinstance(alerts, list)
        
        for alert in alerts:
            assert "type" in alert
            assert "severity" in alert
            assert "message" in alert
            assert "recommendation" in alert
            assert "timestamp" in alert
            assert alert["severity"] in ["low", "medium", "high"]
    
    @pytest.mark.asyncio
    async def test_moisture_level_determination(self, service):
        """Test moisture level determination logic."""
        # Test different moisture level scenarios
        test_cases = [
            (5, 10, SoilMoistureLevel.VERY_DRY),     # Very low moisture (avg 7.5)
            (15, 25, SoilMoistureLevel.DRY),         # Dry (avg 20)
            (25, 35, SoilMoistureLevel.ADEQUATE),    # Adequate (avg 30)
            (35, 45, SoilMoistureLevel.MOIST),        # Moist (avg 40)
            (50, 60, SoilMoistureLevel.SATURATED)    # Saturated (avg 55)
        ]
        
        for surface_moisture, deep_moisture, expected_level in test_cases:
            level = service._determine_moisture_level(surface_moisture, deep_moisture)
            assert level == expected_level
    
    @pytest.mark.asyncio
    async def test_available_water_capacity_calculation(self, service, soil_characteristics):
        """Test available water capacity calculation."""
        moisture_content = 0.25  # 25% moisture
        awc = service._calculate_available_water_capacity(moisture_content, soil_characteristics)
        
        # Should be positive for moisture above wilting point
        assert awc > 0
        
        # Test with moisture below wilting point
        low_moisture = 0.10  # 10% moisture (below wilting point)
        awc_low = service._calculate_available_water_capacity(low_moisture, soil_characteristics)
        assert awc_low == 0  # Should be 0 for moisture below wilting point
    
    @pytest.mark.asyncio
    async def test_irrigation_recommendation_generation(self, service, field_id, soil_characteristics):
        """Test irrigation recommendation generation."""
        await service.initialize()
        await service.setup_field_monitoring(field_id, soil_characteristics)
        
        # Test different moisture scenarios
        moisture_scenarios = [
            (15.0, "Immediate irrigation required - critical moisture level"),
            (25.0, "Consider irrigation - low moisture level"),
            (45.0, "No irrigation needed - adequate moisture level")
        ]
        
        for moisture_percent, expected_recommendation in moisture_scenarios:
            moisture_data = {
                "surface_moisture_percent": moisture_percent,
                "deep_moisture_percent": moisture_percent * 1.2,
                "available_water_capacity": 1.5,
                "timestamp": datetime.utcnow()
            }
            
            config = service.monitoring_configs[str(field_id)]
            recommendation = await service._generate_irrigation_recommendation(
                field_id, moisture_data, config
            )
            
            assert expected_recommendation in recommendation
    
    @pytest.mark.asyncio
    async def test_days_until_critical_calculation(self, service, field_id, soil_characteristics):
        """Test days until critical moisture calculation."""
        await service.initialize()
        await service.setup_field_monitoring(field_id, soil_characteristics)
        
        # Test with moisture above critical threshold
        moisture_data = {
            "surface_moisture_percent": 35.0,
            "deep_moisture_percent": 40.0,
            "available_water_capacity": 2.0,
            "timestamp": datetime.utcnow()
        }
        
        config = service.monitoring_configs[str(field_id)]
        days_until_critical = await service._calculate_days_until_critical(
            field_id, moisture_data, config
        )
        
        assert days_until_critical is not None
        assert days_until_critical >= 0
        
        # Test with moisture at or below critical threshold
        critical_moisture_data = {
            "surface_moisture_percent": 15.0,
            "deep_moisture_percent": 18.0,
            "available_water_capacity": 0.5,
            "timestamp": datetime.utcnow()
        }
        
        days_critical = await service._calculate_days_until_critical(
            field_id, critical_moisture_data, config
        )
        
        assert days_critical == 0  # Should be 0 for critical moisture


class TestWaterBalanceModel:
    """Test suite for WaterBalanceModel."""
    
    @pytest.fixture
    def model(self):
        """Create model instance for testing."""
        soil_characteristics = {
            "field_capacity": 0.35,
            "wilting_point": 0.15,
            "bulk_density": 1.3
        }
        return WaterBalanceModel(soil_characteristics)
    
    @pytest.fixture
    def mock_current_status(self):
        """Create mock current moisture status."""
        return SoilMoistureStatus(
            field_id=uuid4(),
            assessment_date=datetime.utcnow(),
            surface_moisture_percent=30.0,
            deep_moisture_percent=35.0,
            available_water_capacity=1.5,
            moisture_level=SoilMoistureLevel.ADEQUATE,
            irrigation_recommendation="No irrigation needed",
            days_until_critical=5
        )
    
    @pytest.fixture
    def mock_weather_forecast(self):
        """Create mock weather forecast."""
        return {
            "daily_forecast": [
                {
                    "date": datetime.utcnow() + timedelta(days=i),
                    "precipitation": 0.0 if i % 3 == 0 else 2.0,
                    "temperature": 25.0 + i
                }
                for i in range(7)
            ]
        }
    
    @pytest.fixture
    def mock_crop_requirements(self):
        """Create mock crop requirements."""
        return {
            "daily_water_requirement_mm": 5.0,
            "total_requirement_mm": 35.0
        }
    
    @pytest.fixture
    def mock_config(self):
        """Create mock configuration."""
        return {
            "field_capacity": 0.35,
            "wilting_point": 0.15,
            "bulk_density": 1.3
        }
    
    @pytest.mark.asyncio
    async def test_water_balance_prediction(self, model, mock_current_status, 
                                         mock_weather_forecast, mock_crop_requirements, mock_config):
        """Test water balance model prediction."""
        prediction = await model.predict(
            mock_current_status, mock_weather_forecast, mock_crop_requirements, mock_config
        )
        
        assert "field_id" in prediction
        assert "prediction_period" in prediction
        assert "daily_predictions" in prediction
        assert len(prediction["daily_predictions"]) == 7
        
        for day_prediction in prediction["daily_predictions"]:
            assert "date" in day_prediction
            assert "predicted_moisture" in day_prediction
            assert "precipitation" in day_prediction
            assert "crop_et" in day_prediction
            assert "moisture_change" in day_prediction
            
            # Validate moisture values are reasonable
            assert 0 <= day_prediction["predicted_moisture"] <= 100
    
    @pytest.mark.asyncio
    async def test_model_with_different_soil_types(self):
        """Test model with different soil characteristics."""
        # Sandy soil
        sandy_soil = {
            "field_capacity": 0.20,
            "wilting_point": 0.08,
            "bulk_density": 1.5
        }
        sandy_model = WaterBalanceModel(sandy_soil)
        
        # Clay soil
        clay_soil = {
            "field_capacity": 0.45,
            "wilting_point": 0.25,
            "bulk_density": 1.1
        }
        clay_model = WaterBalanceModel(clay_soil)
        
        # Both models should initialize successfully
        assert sandy_model.soil_characteristics == sandy_soil
        assert clay_model.soil_characteristics == clay_soil


class TestEvapotranspirationModel:
    """Test suite for EvapotranspirationModel."""
    
    @pytest.fixture
    def model(self):
        """Create model instance for testing."""
        return EvapotranspirationModel()
    
    @pytest.fixture
    def mock_weather_data(self):
        """Create mock weather data."""
        return {
            "temperature": 25.0,
            "humidity": 60.0,
            "wind_speed": 2.0,
            "solar_radiation": 20.0
        }
    
    @pytest.fixture
    def mock_crop_data(self):
        """Create mock crop data."""
        return {
            "crop_type": "corn",
            "growth_stage": "vegetative"
        }
    
    @pytest.mark.asyncio
    async def test_et_calculation(self, model, mock_weather_data, mock_crop_data):
        """Test evapotranspiration calculation."""
        et = await model.calculate_et(mock_weather_data, mock_crop_data)
        
        assert isinstance(et, float)
        assert et >= 0  # ET should be non-negative
    
    @pytest.mark.asyncio
    async def test_et_with_different_weather_conditions(self, model, mock_crop_data):
        """Test ET calculation with different weather conditions."""
        # Hot, dry conditions
        hot_dry_weather = {
            "temperature": 35.0,
            "humidity": 30.0,
            "wind_speed": 5.0,
            "solar_radiation": 25.0
        }
        
        # Cool, humid conditions
        cool_humid_weather = {
            "temperature": 15.0,
            "humidity": 80.0,
            "wind_speed": 1.0,
            "solar_radiation": 10.0
        }
        
        et_hot_dry = await model.calculate_et(hot_dry_weather, mock_crop_data)
        et_cool_humid = await model.calculate_et(cool_humid_weather, mock_crop_data)
        
        # Hot, dry conditions should result in higher ET
        assert et_hot_dry > et_cool_humid


class TestCropCoefficientModel:
    """Test suite for CropCoefficientModel."""
    
    @pytest.fixture
    def model(self):
        """Create model instance for testing."""
        return CropCoefficientModel()
    
    @pytest.mark.asyncio
    async def test_crop_coefficient_lookup(self, model):
        """Test crop coefficient lookup."""
        # Test corn coefficients
        corn_kc_initial = await model.get_crop_coefficient("corn", "initial")
        corn_kc_mid = await model.get_crop_coefficient("corn", "mid_season")
        
        assert corn_kc_initial == 0.4
        assert corn_kc_mid == 1.0
        
        # Test soybean coefficients
        soybean_kc_initial = await model.get_crop_coefficient("soybean", "initial")
        soybean_kc_mid = await model.get_crop_coefficient("soybean", "mid_season")
        
        assert soybean_kc_initial == 0.4
        assert soybean_kc_mid == 1.0
    
    @pytest.mark.asyncio
    async def test_unknown_crop_coefficient(self, model):
        """Test crop coefficient for unknown crop."""
        unknown_kc = await model.get_crop_coefficient("unknown_crop", "vegetative")
        assert unknown_kc == 0.7  # Default value
    
    @pytest.mark.asyncio
    async def test_unknown_growth_stage(self, model):
        """Test crop coefficient for unknown growth stage."""
        unknown_stage_kc = await model.get_crop_coefficient("corn", "unknown_stage")
        assert unknown_stage_kc == 0.7  # Default value


class TestMockServices:
    """Test suite for mock services."""
    
    @pytest.fixture
    def mock_weather_service(self):
        """Create mock weather service."""
        return MockWeatherService()
    
    @pytest.fixture
    def mock_crop_service(self):
        """Create mock crop service."""
        return MockCropService()
    
    @pytest.fixture
    def mock_field_service(self):
        """Create mock field service."""
        return MockFieldService()
    
    @pytest.mark.asyncio
    async def test_mock_weather_service(self, mock_weather_service):
        """Test mock weather service."""
        field_id = uuid4()
        
        # Test forecast
        forecast = await mock_weather_service.get_forecast(field_id, 7)
        assert forecast["field_id"] == field_id
        assert forecast["forecast_days"] == 7
        assert len(forecast["daily_forecast"]) == 7
        
        # Test weather data
        weather_data = await mock_weather_service.get_weather_data(field_id, datetime.utcnow())
        assert weather_data["field_id"] == field_id
        assert "temperature" in weather_data
        assert "humidity" in weather_data
        assert "precipitation" in weather_data
    
    @pytest.mark.asyncio
    async def test_mock_crop_service(self, mock_crop_service):
        """Test mock crop service."""
        field_id = uuid4()
        
        # Test water requirements
        requirements = await mock_crop_service.get_water_requirements(field_id, 7)
        assert requirements["field_id"] == field_id
        assert requirements["crop_type"] == "corn"
        assert requirements["daily_water_requirement_mm"] == 5.0
        
        # Test crop data
        crop_data = await mock_crop_service.get_crop_data(field_id, datetime.utcnow())
        assert crop_data["field_id"] == field_id
        assert crop_data["crop_type"] == "corn"
        assert "growth_stage" in crop_data
    
    @pytest.mark.asyncio
    async def test_mock_field_service(self, mock_field_service):
        """Test mock field service."""
        field_id = uuid4()
        
        characteristics = await mock_field_service.get_field_characteristics(field_id)
        assert characteristics["field_id"] == field_id
        assert characteristics["soil_type"] == "clay_loam"
        assert "field_capacity" in characteristics
        assert "wilting_point" in characteristics


class TestIntegrationScenarios:
    """Integration tests for complete workflows."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return SoilMoistureMonitoringService()
    
    @pytest.fixture
    def field_id(self):
        """Create test field ID."""
        return uuid4()
    
    @pytest.fixture
    def soil_characteristics(self):
        """Create test soil characteristics."""
        return {
            "soil_type": "clay_loam",
            "field_capacity": 0.35,
            "wilting_point": 0.15,
            "bulk_density": 1.3,
            "monitoring_depth": 100,
            "saturation_point": 0.45
        }
    
    @pytest.mark.asyncio
    async def test_complete_monitoring_workflow(self, service, field_id, soil_characteristics):
        """Test complete soil moisture monitoring workflow."""
        # Initialize service
        await service.initialize()
        
        # Setup field monitoring
        config = await service.setup_field_monitoring(field_id, soil_characteristics)
        assert config is not None
        
        # Get current moisture status
        status = await service.get_current_moisture_status(field_id)
        assert isinstance(status, SoilMoistureStatus)
        
        # Predict moisture deficit
        prediction = await service.predict_moisture_deficit(field_id, 7)
        assert "deficit_predictions" in prediction
        
        # Calculate evapotranspiration
        et_result = await service.calculate_evapotranspiration(field_id, datetime.utcnow())
        assert "total_et_mm" in et_result
        
        # Get irrigation recommendations
        irrigation_recs = await service.get_irrigation_recommendations(field_id)
        assert "recommendation" in irrigation_recs
        
        # Get moisture alerts
        alerts = await service.get_moisture_alerts(field_id)
        assert isinstance(alerts, list)
        
        # Cleanup
        await service.cleanup()
        assert service.initialized is False
    
    @pytest.mark.asyncio
    async def test_drought_stress_scenario(self, service, field_id, soil_characteristics):
        """Test drought stress scenario."""
        await service.initialize()
        await service.setup_field_monitoring(field_id, soil_characteristics)
        
        # Simulate drought conditions by modifying the mock data
        with patch.object(service, '_collect_current_moisture_data') as mock_collect:
            mock_collect.return_value = {
                "surface_moisture_percent": 15.0,  # Critical moisture
                "deep_moisture_percent": 18.0,
                "available_water_capacity": 0.3,
                "soil_temperature": 28.0,
                "timestamp": datetime.utcnow()
            }
            
            # Get status under drought conditions
            status = await service.get_current_moisture_status(field_id)
            assert status.surface_moisture_percent == 15.0
            assert status.moisture_level == SoilMoistureLevel.VERY_DRY
            
            # Check for alerts
            alerts = await service.get_moisture_alerts(field_id)
            critical_alerts = [alert for alert in alerts if alert["type"] == "critical_moisture"]
            assert len(critical_alerts) > 0
            
            # Check irrigation recommendations
            irrigation_recs = await service.get_irrigation_recommendations(field_id)
            assert "immediate" in irrigation_recs["recommendation"].lower() or "critical" in irrigation_recs["recommendation"].lower()
    
    @pytest.mark.asyncio
    async def test_adequate_moisture_scenario(self, service, field_id, soil_characteristics):
        """Test adequate moisture scenario."""
        await service.initialize()
        await service.setup_field_monitoring(field_id, soil_characteristics)
        
        # Simulate adequate moisture conditions
        with patch.object(service, '_collect_current_moisture_data') as mock_collect:
            mock_collect.return_value = {
                "surface_moisture_percent": 40.0,  # Adequate moisture
                "deep_moisture_percent": 45.0,
                "available_water_capacity": 2.5,
                "soil_temperature": 22.0,
                "timestamp": datetime.utcnow()
            }
            
            # Get status under adequate conditions
            status = await service.get_current_moisture_status(field_id)
            assert status.surface_moisture_percent == 40.0
            assert status.moisture_level in [SoilMoistureLevel.ADEQUATE, SoilMoistureLevel.MOIST]
            
            # Check for alerts (should be minimal)
            alerts = await service.get_moisture_alerts(field_id)
            critical_alerts = [alert for alert in alerts if alert["severity"] == "high"]
            assert len(critical_alerts) == 0
            
            # Check irrigation recommendations
            irrigation_recs = await service.get_irrigation_recommendations(field_id)
            assert "no irrigation" in irrigation_recs["recommendation"].lower() or "adequate" in irrigation_recs["recommendation"].lower()


# Performance tests
class TestPerformance:
    """Performance tests for soil moisture monitoring service."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return SoilMoistureMonitoringService()
    
    @pytest.fixture
    def field_id(self):
        """Create test field ID."""
        return uuid4()
    
    @pytest.fixture
    def soil_characteristics(self):
        """Create test soil characteristics."""
        return {
            "soil_type": "clay_loam",
            "field_capacity": 0.35,
            "wilting_point": 0.15,
            "bulk_density": 1.3,
            "monitoring_depth": 100
        }
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_response_time_requirements(self, service, field_id, soil_characteristics):
        """Test that response times meet requirements."""
        import time
        
        await service.initialize()
        await service.setup_field_monitoring(field_id, soil_characteristics)
        
        # Test moisture status response time
        start_time = time.time()
        await service.get_current_moisture_status(field_id)
        elapsed = time.time() - start_time
        assert elapsed < 2.0, f"Moisture status response time {elapsed}s exceeds 2s requirement"
        
        # Test deficit prediction response time
        start_time = time.time()
        await service.predict_moisture_deficit(field_id, 7)
        elapsed = time.time() - start_time
        assert elapsed < 5.0, f"Deficit prediction response time {elapsed}s exceeds 5s requirement"
        
        # Test ET calculation response time
        start_time = time.time()
        await service.calculate_evapotranspiration(field_id, datetime.utcnow())
        elapsed = time.time() - start_time
        assert elapsed < 3.0, f"ET calculation response time {elapsed}s exceeds 3s requirement"
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_concurrent_requests(self, service, soil_characteristics):
        """Test handling of concurrent requests."""
        field_ids = [uuid4() for _ in range(5)]
        
        await service.initialize()
        
        # Setup multiple fields concurrently
        setup_tasks = [
            service.setup_field_monitoring(field_id, soil_characteristics)
            for field_id in field_ids
        ]
        await asyncio.gather(*setup_tasks)
        
        # Make concurrent requests
        status_tasks = [
            service.get_current_moisture_status(field_id)
            for field_id in field_ids
        ]
        
        start_time = time.time()
        results = await asyncio.gather(*status_tasks)
        elapsed = time.time() - start_time
        
        assert len(results) == 5
        assert elapsed < 10.0, f"Concurrent requests took {elapsed}s, should be under 10s"


# Agricultural validation tests
class TestAgriculturalValidation:
    """Agricultural validation tests for soil moisture monitoring."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return SoilMoistureMonitoringService()
    
    @pytest.mark.asyncio
    async def test_corn_belt_soil_moisture_accuracy(self, service):
        """Test soil moisture accuracy for corn belt conditions."""
        field_id = uuid4()
        corn_belt_soil = {
            "soil_type": "clay_loam",
            "field_capacity": 0.35,
            "wilting_point": 0.15,
            "bulk_density": 1.3,
            "monitoring_depth": 100
        }
        
        await service.initialize()
        await service.setup_field_monitoring(field_id, corn_belt_soil)
        
        status = await service.get_current_moisture_status(field_id)
        
        # Validate moisture levels are agriculturally reasonable
        assert 10 <= status.surface_moisture_percent <= 80
        assert 10 <= status.deep_moisture_percent <= 80
        assert status.available_water_capacity >= 0
        
        # Validate moisture level classification
        assert isinstance(status.moisture_level, SoilMoistureLevel)
    
    @pytest.mark.asyncio
    async def test_evapotranspiration_calculation_accuracy(self, service):
        """Test ET calculation accuracy for agricultural conditions."""
        field_id = uuid4()
        soil_characteristics = {
            "soil_type": "clay_loam",
            "field_capacity": 0.35,
            "wilting_point": 0.15,
            "bulk_density": 1.3
        }
        
        await service.initialize()
        await service.setup_field_monitoring(field_id, soil_characteristics)
        
        et_result = await service.calculate_evapotranspiration(field_id, datetime.utcnow())
        
        # Validate ET values are agriculturally reasonable
        assert 0 <= et_result["reference_et_mm"] <= 15  # Daily ET should be reasonable
        assert 0.3 <= et_result["crop_coefficient"] <= 1.2  # Kc should be reasonable
        assert 0 <= et_result["crop_et_mm"] <= 15  # Crop ET should be reasonable
        assert 0 <= et_result["soil_evaporation_mm"] <= 5  # Soil evaporation should be reasonable
    
    @pytest.mark.asyncio
    async def test_irrigation_recommendation_accuracy(self, service):
        """Test irrigation recommendation accuracy."""
        field_id = uuid4()
        soil_characteristics = {
            "soil_type": "clay_loam",
            "field_capacity": 0.35,
            "wilting_point": 0.15,
            "bulk_density": 1.3
        }
        
        await service.initialize()
        await service.setup_field_monitoring(field_id, soil_characteristics)
        
        irrigation_recs = await service.get_irrigation_recommendations(field_id)
        
        # Validate irrigation recommendations are reasonable
        assert irrigation_recs["irrigation_depth_mm"] >= 0
        assert irrigation_recs["irrigation_depth_inches"] >= 0
        assert irrigation_recs["priority"] in ["low", "medium", "high"]
        assert irrigation_recs["timing"] in ["Early morning or evening", "As needed based on soil moisture monitoring"]
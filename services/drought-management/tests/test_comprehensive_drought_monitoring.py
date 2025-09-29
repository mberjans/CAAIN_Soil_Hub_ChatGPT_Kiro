"""
Comprehensive Tests for Drought Monitoring and Early Warning System

Tests for the enhanced DroughtMonitoringService with drought indices,
NOAA integration, predictive alerts, and comprehensive monitoring capabilities.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from src.services.drought_monitoring_service import (
    DroughtMonitoringService,
    DroughtIndicesCalculator,
    NOAADroughtProvider,
    ComprehensiveAlertSystem,
    NotificationService
)
from src.models.drought_models import (
    DroughtMonitoringRequest,
    DroughtMonitoringResponse,
    DroughtRiskLevel
)


class TestDroughtMonitoringService:
    """Comprehensive test suite for drought monitoring service."""

    @pytest.fixture
    def service(self):
        return DroughtMonitoringService()

    @pytest.fixture
    def mock_farm_location_id(self):
        return uuid4()

    @pytest.fixture
    def mock_field_id(self):
        return uuid4()

    @pytest.fixture
    def mock_monitoring_request(self, mock_farm_location_id, mock_field_id):
        return DroughtMonitoringRequest(
            farm_location_id=mock_farm_location_id,
            field_ids=[mock_field_id],
            monitoring_frequency="daily",
            alert_thresholds={
                "soil_moisture_low": 30.0,
                "soil_moisture_critical": 20.0,
                "temperature_high": 35.0,
                "drought_risk_high": 0.7
            },
            notification_preferences={
                "enabled_channels": ["email", "push"],
                "email": "farmer@example.com",
                "phone": "+1234567890"
            },
            integration_services=["weather", "soil", "satellite"]
        )

    @pytest.mark.asyncio
    async def test_service_initialization(self, service):
        """Test comprehensive service initialization."""
        with patch.object(service, 'drought_indices_calculator') as mock_calc, \
             patch.object(service, 'noaa_provider') as mock_noaa, \
             patch.object(service, 'alert_system') as mock_alert:
            
            mock_calc.initialize = AsyncMock()
            mock_noaa.initialize = AsyncMock()
            mock_alert.initialize = AsyncMock()
            
            await service.initialize()
            
            assert service.initialized is True
            mock_calc.initialize.assert_called_once()
            mock_noaa.initialize.assert_called_once()
            mock_alert.initialize.assert_called_once()

    @pytest.mark.asyncio
    async def test_drought_indices_calculation(self, service, mock_farm_location_id, mock_field_id):
        """Test comprehensive drought indices calculation."""
        with patch.object(service, '_get_historical_weather_data') as mock_weather, \
             patch.object(service, '_get_soil_moisture_data') as mock_soil, \
             patch.object(service, 'drought_indices_calculator') as mock_calc, \
             patch.object(service, '_calculate_vegetation_health_index') as mock_vhi, \
             patch.object(service, '_assess_overall_drought_severity') as mock_severity:
            
            # Mock data
            mock_weather.return_value = {
                "precipitation": [10.5, 8.2, 12.1, 5.8, 15.3, 7.9, 9.4, 11.2],
                "temperature": [22.5, 24.1, 26.8, 28.3, 25.9, 23.7, 21.4, 19.8],
                "potential_evapotranspiration": [4.2, 4.8, 5.1, 5.6, 4.9, 4.3, 3.8, 3.2]
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
            mock_vhi.return_value = 0.75
            mock_severity.return_value = "moderate"
            
            # Test calculation
            result = await service.calculate_drought_indices(mock_farm_location_id, mock_field_id)
            
            # Verify results
            assert "spi" in result
            assert "pdsi" in result
            assert "spei" in result
            assert "vegetation_health_index" in result
            assert "overall_drought_severity" in result
            assert result["field_id"] == mock_field_id
            assert result["spi"]["3_month"] == -1.2
            assert result["pdsi"] == -1.4
            assert result["overall_drought_severity"] == "moderate"

    @pytest.mark.asyncio
    async def test_noaa_drought_data_integration(self, service, mock_farm_location_id):
        """Test NOAA drought monitor data integration."""
        with patch.object(service, '_get_farm_coordinates') as mock_coords, \
             patch.object(service, 'noaa_provider') as mock_noaa:
            
            mock_coords.return_value = {"latitude": 40.7128, "longitude": -74.0060}
            mock_noaa.get_drought_monitor_data = AsyncMock(return_value={
                "drought_category": "D1 - Moderate Drought",
                "drought_intensity": 0.3,
                "affected_area_percent": 15.2,
                "drought_start_date": "2024-01-15",
                "drought_duration_weeks": 8,
                "confidence_level": 0.85,
                "last_updated": datetime.utcnow()
            })
            
            result = await service.get_noaa_drought_data(mock_farm_location_id)
            
            assert result["farm_location_id"] == mock_farm_location_id
            assert result["noaa_drought_category"] == "D1 - Moderate Drought"
            assert result["drought_intensity"] == 0.3
            assert result["data_source"] == "NOAA Drought Monitor"

    @pytest.mark.asyncio
    async def test_predictive_alerts_generation(self, service, mock_farm_location_id):
        """Test predictive alert generation."""
        with patch.object(service, 'calculate_drought_indices') as mock_indices, \
             patch.object(service, '_get_weather_forecast') as mock_forecast, \
             patch.object(service, '_analyze_drought_trends') as mock_trends, \
             patch.object(service, '_analyze_weather_patterns') as mock_weather, \
             patch.object(service, '_analyze_soil_moisture_trends') as mock_soil, \
             patch.object(service, '_prioritize_alerts') as mock_prioritize:
            
            # Mock data
            mock_indices.return_value = {
                "spi": {"3_month": -1.5},
                "pdsi": -1.4,
                "spei": {"3_month": -1.3},
                "vegetation_health_index": 0.75
            }
            mock_forecast.return_value = {
                "precipitation_forecast": [0.0, 2.5, 0.0, 0.0, 8.2, 0.0, 0.0],
                "temperature_forecast": [28.5, 30.2, 32.1, 29.8, 26.4, 24.7, 22.9],
                "humidity_forecast": [45.0, 52.0, 38.0, 41.0, 68.0, 72.0, 75.0]
            }
            mock_trends.return_value = [{
                "type": "drought_trend_warning",
                "severity": "high",
                "message": "3-month SPI indicates severe drought conditions: -1.50",
                "recommendation": "Implement immediate drought mitigation measures",
                "timestamp": datetime.utcnow()
            }]
            mock_weather.return_value = [{
                "type": "low_precipitation_forecast",
                "severity": "medium",
                "message": "Low precipitation forecast: 1.5mm/day average",
                "recommendation": "Monitor soil moisture closely and prepare irrigation",
                "timestamp": datetime.utcnow()
            }]
            mock_soil.return_value = [{
                "type": "soil_moisture_declining",
                "severity": "medium",
                "message": "Soil moisture levels declining over past week",
                "recommendation": "Consider irrigation or conservation practices",
                "timestamp": datetime.utcnow()
            }]
            mock_prioritize.return_value = [
                {
                    "type": "drought_trend_warning",
                    "severity": "high",
                    "message": "3-month SPI indicates severe drought conditions: -1.50",
                    "recommendation": "Implement immediate drought mitigation measures",
                    "timestamp": datetime.utcnow()
                },
                {
                    "type": "low_precipitation_forecast",
                    "severity": "medium",
                    "message": "Low precipitation forecast: 1.5mm/day average",
                    "recommendation": "Monitor soil moisture closely and prepare irrigation",
                    "timestamp": datetime.utcnow()
                }
            ]
            
            alerts = await service.generate_predictive_alerts(mock_farm_location_id)
            
            assert len(alerts) == 2
            assert alerts[0]["severity"] == "high"
            assert alerts[1]["severity"] == "medium"
            assert "drought_trend_warning" in [alert["type"] for alert in alerts]

    @pytest.mark.asyncio
    async def test_monitoring_dashboard_integration(self, service, mock_farm_location_id):
        """Test comprehensive monitoring dashboard data integration."""
        with patch.object(service, 'get_monitoring_status') as mock_status, \
             patch.object(service, 'get_noaa_drought_data') as mock_noaa, \
             patch.object(service, 'generate_predictive_alerts') as mock_alerts, \
             patch.object(service, '_get_historical_trends') as mock_trends:
            
            # Mock responses
            mock_status.return_value = DroughtMonitoringResponse(
                monitoring_id=uuid4(),
                farm_location_id=mock_farm_location_id,
                status="active",
                active_alerts=[],
                monitoring_data={"test": "data"},
                next_check_time=datetime.utcnow() + timedelta(hours=1)
            )
            mock_noaa.return_value = {
                "noaa_drought_category": "D1 - Moderate Drought",
                "drought_intensity": 0.3
            }
            mock_alerts.return_value = [{
                "type": "test_alert",
                "severity": "medium",
                "message": "Test alert message"
            }]
            mock_trends.return_value = {
                "drought_indices_trend": {"spi_3m": [-0.5, -0.8, -1.2]},
                "soil_moisture_trend": {"surface": [45.0, 42.0, 38.0]},
                "weather_trend": {"precipitation": [5.2, 3.8, 2.1]}
            }
            
            # Test dashboard data collection
            dashboard_data = {
                "farm_location_id": mock_farm_location_id,
                "timestamp": datetime.utcnow(),
                "current_status": await service.get_monitoring_status(mock_farm_location_id),
                "noaa_data": await service.get_noaa_drought_data(mock_farm_location_id),
                "predictive_alerts": await service.generate_predictive_alerts(mock_farm_location_id),
                "summary": {
                    "overall_drought_risk": "moderate",
                    "active_alerts_count": 1,
                    "monitoring_status": "active",
                    "last_data_update": datetime.utcnow()
                }
            }
            
            # Verify dashboard structure
            assert dashboard_data["farm_location_id"] == mock_farm_location_id
            assert "current_status" in dashboard_data
            assert "noaa_data" in dashboard_data
            assert "predictive_alerts" in dashboard_data
            assert "summary" in dashboard_data
            assert dashboard_data["summary"]["active_alerts_count"] == 1

    @pytest.mark.asyncio
    async def test_alert_filtering(self, service, mock_farm_location_id):
        """Test alert filtering by type and severity."""
        with patch.object(service, 'get_monitoring_status') as mock_status:
            mock_status.return_value = DroughtMonitoringResponse(
                monitoring_id=uuid4(),
                farm_location_id=mock_farm_location_id,
                status="warning",
                active_alerts=[
                    {
                        "type": "soil_moisture_low",
                        "severity": "medium",
                        "message": "Low soil moisture",
                        "timestamp": datetime.utcnow()
                    },
                    {
                        "type": "drought_trend_warning",
                        "severity": "high",
                        "message": "Drought trend warning",
                        "timestamp": datetime.utcnow()
                    }
                ],
                monitoring_data={},
                next_check_time=datetime.utcnow() + timedelta(hours=1)
            )
            
            # Test filtering by alert type
            alerts = await service.get_drought_alerts(mock_farm_location_id, "soil_moisture_low")
            assert len(alerts) == 1
            assert alerts[0]["type"] == "soil_moisture_low"
            
            # Test filtering by severity
            alerts = await service.get_drought_alerts(mock_farm_location_id, None)
            high_severity_alerts = [alert for alert in alerts if alert.get("severity") == "high"]
            assert len(high_severity_alerts) == 1
            assert high_severity_alerts[0]["severity"] == "high"


class TestDroughtIndicesCalculator:
    """Test suite for drought indices calculator."""

    @pytest.fixture
    def calculator(self):
        return DroughtIndicesCalculator()

    @pytest.mark.asyncio
    async def test_spi_calculation(self, calculator):
        """Test Standardized Precipitation Index calculation."""
        precipitation_data = [10.5, 8.2, 12.1, 5.8, 15.3, 7.9, 9.4, 11.2]
        periods = [1, 3, 6]
        
        spi_values = await calculator.calculate_spi(precipitation_data, periods)
        
        assert len(spi_values) == 3
        assert all(isinstance(value, float) for value in spi_values)

    @pytest.mark.asyncio
    async def test_pdsi_calculation(self, calculator):
        """Test Palmer Drought Severity Index calculation."""
        precipitation = [10.5, 8.2, 12.1, 5.8, 15.3, 7.9, 9.4, 11.2]
        temperature = [22.5, 24.1, 26.8, 28.3, 25.9, 23.7, 21.4, 19.8]
        available_water_capacity = 2.5
        
        pdsi_value = await calculator.calculate_pdsi(precipitation, temperature, available_water_capacity)
        
        assert isinstance(pdsi_value, float)

    @pytest.mark.asyncio
    async def test_spei_calculation(self, calculator):
        """Test Standardized Precipitation Evapotranspiration Index calculation."""
        precipitation = [10.5, 8.2, 12.1, 5.8, 15.3, 7.9, 9.4, 11.2]
        pet_data = [4.2, 4.8, 5.1, 5.6, 4.9, 4.3, 3.8, 3.2]
        periods = [1, 3, 6]
        
        spei_values = await calculator.calculate_spei(precipitation, pet_data, periods)
        
        assert len(spei_values) == 3
        assert all(isinstance(value, float) for value in spei_values)


class TestNOAADroughtProvider:
    """Test suite for NOAA drought provider."""

    @pytest.fixture
    def provider(self):
        return NOAADroughtProvider()

    @pytest.mark.asyncio
    async def test_noaa_data_retrieval(self, provider):
        """Test NOAA drought monitor data retrieval."""
        latitude = 40.7128
        longitude = -74.0060
        
        data = await provider.get_drought_monitor_data(latitude, longitude)
        
        assert "drought_category" in data
        assert "drought_intensity" in data
        assert "affected_area_percent" in data
        assert "confidence_level" in data
        assert isinstance(data["drought_intensity"], float)
        assert isinstance(data["confidence_level"], float)


class TestComprehensiveAlertSystem:
    """Test suite for comprehensive alert system."""

    @pytest.fixture
    def alert_system(self):
        return ComprehensiveAlertSystem()

    @pytest.fixture
    def mock_farm_location_id(self):
        return uuid4()

    @pytest.mark.asyncio
    async def test_alert_configuration(self, alert_system, mock_farm_location_id):
        """Test alert system configuration."""
        thresholds = {
            "soil_moisture_low": 30.0,
            "soil_moisture_critical": 20.0,
            "drought_risk_high": 0.7
        }
        notification_preferences = {
            "enabled_channels": ["email", "push"],
            "email": "farmer@example.com"
        }
        
        await alert_system.configure_alerts(mock_farm_location_id, thresholds, notification_preferences)
        
        config = alert_system.alert_configs[str(mock_farm_location_id)]
        assert config["thresholds"] == thresholds
        assert config["notification_preferences"] == notification_preferences
        assert "created_at" in config

    @pytest.mark.asyncio
    async def test_alert_sending(self, alert_system, mock_farm_location_id):
        """Test alert sending functionality."""
        with patch.object(alert_system, 'notification_service') as mock_notification:
            mock_notification.send_notification = AsyncMock()
            
            # Configure alerts first
            await alert_system.configure_alerts(
                mock_farm_location_id,
                {"soil_moisture_low": 30.0},
                {"enabled_channels": ["email"]}
            )
            
            # Send alert
            alert = {
                "type": "soil_moisture_low",
                "severity": "medium",
                "message": "Low soil moisture detected",
                "timestamp": datetime.utcnow()
            }
            
            await alert_system.send_alert(mock_farm_location_id, alert)
            
            # Verify alert was added to history
            config = alert_system.alert_configs[str(mock_farm_location_id)]
            assert len(config["alert_history"]) == 1
            assert config["alert_history"][0] == alert
            
            # Verify notification was sent
            mock_notification.send_notification.assert_called_once()


class TestNotificationService:
    """Test suite for notification service."""

    @pytest.fixture
    def notification_service(self):
        return NotificationService()

    @pytest.fixture
    def mock_farm_location_id(self):
        return uuid4()

    @pytest.mark.asyncio
    async def test_notification_channel_selection(self, notification_service):
        """Test notification channel selection based on severity."""
        # Test high severity alert
        high_alert = {"severity": "high", "message": "Critical alert"}
        preferences = {"enabled_channels": ["email", "sms", "push"]}
        
        channels = notification_service._determine_notification_channels(high_alert, preferences)
        assert "email" in channels
        assert "sms" in channels
        assert "push" in channels
        
        # Test medium severity alert
        medium_alert = {"severity": "medium", "message": "Warning alert"}
        channels = notification_service._determine_notification_channels(medium_alert, preferences)
        assert "email" in channels
        assert "push" in channels
        assert "sms" not in channels
        
        # Test low severity alert
        low_alert = {"severity": "low", "message": "Info alert"}
        channels = notification_service._determine_notification_channels(low_alert, preferences)
        assert channels == ["push"]

    @pytest.mark.asyncio
    async def test_notification_sending(self, notification_service, mock_farm_location_id):
        """Test notification sending with multiple channels."""
        with patch.object(notification_service, 'email_service') as mock_email, \
             patch.object(notification_service, 'sms_service') as mock_sms, \
             patch.object(notification_service, 'push_service') as mock_push:
            
            mock_email.send_alert_email = AsyncMock()
            mock_sms.send_alert_sms = AsyncMock()
            mock_push.send_push_notification = AsyncMock()
            
            alert = {
                "severity": "high",
                "message": "Critical drought alert",
                "type": "drought_trend_warning"
            }
            preferences = {"enabled_channels": ["email", "sms", "push"]}
            
            await notification_service.send_notification(mock_farm_location_id, alert, preferences)
            
            # Verify all channels were used for high severity alert
            mock_email.send_alert_email.assert_called_once()
            mock_sms.send_alert_sms.assert_called_once()
            mock_push.send_push_notification.assert_called_once()


# Integration Tests
class TestDroughtMonitoringIntegration:
    """Integration tests for drought monitoring system."""

    @pytest.mark.asyncio
    async def test_end_to_end_monitoring_workflow(self):
        """Test complete monitoring workflow from setup to alerts."""
        service = DroughtMonitoringService()
        farm_location_id = uuid4()
        field_id = uuid4()
        
        # Mock all external dependencies
        with patch.object(service, 'drought_indices_calculator') as mock_calc, \
             patch.object(service, 'noaa_provider') as mock_noaa, \
             patch.object(service, 'alert_system') as mock_alert:
            
            # Initialize service
            mock_calc.initialize = AsyncMock()
            mock_noaa.initialize = AsyncMock()
            mock_alert.initialize = AsyncMock()
            await service.initialize()
            
            # Test monitoring setup
            request = DroughtMonitoringRequest(
                farm_location_id=farm_location_id,
                field_ids=[field_id],
                monitoring_frequency="daily",
                alert_thresholds={"soil_moisture_low": 30.0},
                notification_preferences={"enabled_channels": ["email"]},
                integration_services=["weather", "soil"]
            )
            
            response = await service.setup_monitoring(request)
            assert response.farm_location_id == farm_location_id
            assert response.status == "active"
            
            # Test drought indices calculation
            with patch.object(service, '_get_historical_weather_data') as mock_weather, \
                 patch.object(service, '_get_soil_moisture_data') as mock_soil, \
                 patch.object(service, '_calculate_vegetation_health_index') as mock_vhi, \
                 patch.object(service, '_assess_overall_drought_severity') as mock_severity:
                
                mock_weather.return_value = {
                    "precipitation": [10.5, 8.2, 12.1, 5.8, 15.3, 7.9, 9.4, 11.2],
                    "temperature": [22.5, 24.1, 26.8, 28.3, 25.9, 23.7, 21.4, 19.8],
                    "potential_evapotranspiration": [4.2, 4.8, 5.1, 5.6, 4.9, 4.3, 3.8, 3.2]
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
                mock_vhi.return_value = 0.75
                mock_severity.return_value = "moderate"
                
                indices = await service.calculate_drought_indices(farm_location_id, field_id)
                assert "spi" in indices
                assert "pdsi" in indices
                assert "spei" in indices
                assert indices["overall_drought_severity"] == "moderate"
            
            # Test NOAA data integration
            with patch.object(service, '_get_farm_coordinates') as mock_coords:
                mock_coords.return_value = {"latitude": 40.7128, "longitude": -74.0060}
                mock_noaa.get_drought_monitor_data = AsyncMock(return_value={
                    "drought_category": "D1 - Moderate Drought",
                    "drought_intensity": 0.3,
                    "confidence_level": 0.85
                })
                
                noaa_data = await service.get_noaa_drought_data(farm_location_id)
                assert noaa_data["noaa_drought_category"] == "D1 - Moderate Drought"
            
            # Test predictive alerts
            with patch.object(service, 'calculate_drought_indices') as mock_indices, \
                 patch.object(service, '_get_weather_forecast') as mock_forecast, \
                 patch.object(service, '_analyze_drought_trends') as mock_trends, \
                 patch.object(service, '_analyze_weather_patterns') as mock_weather, \
                 patch.object(service, '_analyze_soil_moisture_trends') as mock_soil, \
                 patch.object(service, '_prioritize_alerts') as mock_prioritize:
                
                mock_indices.return_value = {"spi": {"3_month": -1.5}}
                mock_forecast.return_value = {"precipitation_forecast": [0.0, 2.5, 0.0]}
                mock_trends.return_value = [{"type": "drought_trend_warning", "severity": "high"}]
                mock_weather.return_value = []
                mock_soil.return_value = []
                mock_prioritize.return_value = [{"type": "drought_trend_warning", "severity": "high"}]
                
                alerts = await service.generate_predictive_alerts(farm_location_id)
                assert len(alerts) == 1
                assert alerts[0]["severity"] == "high"


# Performance Tests
class TestDroughtMonitoringPerformance:
    """Performance tests for drought monitoring system."""

    @pytest.mark.asyncio
    async def test_drought_indices_calculation_performance(self):
        """Test performance of drought indices calculation."""
        import time
        
        calculator = DroughtIndicesCalculator()
        await calculator.initialize()
        
        # Large dataset for performance testing
        precipitation_data = [10.5 + i * 0.1 for i in range(1000)]
        pet_data = [4.2 + i * 0.05 for i in range(1000)]
        periods = [1, 3, 6, 12, 24]
        
        start_time = time.time()
        
        spi_values = await calculator.calculate_spi(precipitation_data, periods)
        pdsi_value = await calculator.calculate_pdsi(precipitation_data[:100], precipitation_data[:100], 2.5)
        spei_values = await calculator.calculate_spei(precipitation_data, pet_data, periods)
        
        elapsed_time = time.time() - start_time
        
        # Performance assertion - should complete within reasonable time
        assert elapsed_time < 1.0  # Less than 1 second for all calculations
        assert len(spi_values) == len(periods)
        assert len(spei_values) == len(periods)

    @pytest.mark.asyncio
    async def test_concurrent_monitoring_requests(self):
        """Test system performance under concurrent monitoring requests."""
        service = DroughtMonitoringService()
        farm_location_ids = [uuid4() for _ in range(10)]
        
        with patch.object(service, 'drought_indices_calculator') as mock_calc, \
             patch.object(service, 'noaa_provider') as mock_noaa, \
             patch.object(service, 'alert_system') as mock_alert:
            
            mock_calc.initialize = AsyncMock()
            mock_noaa.initialize = AsyncMock()
            mock_alert.initialize = AsyncMock()
            await service.initialize()
            
            # Mock all external calls
            with patch.object(service, '_get_historical_weather_data') as mock_weather, \
                 patch.object(service, '_get_soil_moisture_data') as mock_soil, \
                 patch.object(service, '_calculate_vegetation_health_index') as mock_vhi, \
                 patch.object(service, '_assess_overall_drought_severity') as mock_severity:
                
                mock_weather.return_value = {"precipitation": [10.5, 8.2, 12.1]}
                mock_soil.return_value = {"available_water_capacity": 2.5}
                mock_calc.calculate_spi = AsyncMock(return_value=[-0.8, -1.2, -1.5, -1.3])
                mock_calc.calculate_pdsi = AsyncMock(return_value=-1.4)
                mock_calc.calculate_spei = AsyncMock(return_value=[-0.9, -1.1, -1.4, -1.2])
                mock_vhi.return_value = 0.75
                mock_severity.return_value = "moderate"
                
                # Test concurrent requests
                import time
                start_time = time.time()
                
                tasks = [
                    service.calculate_drought_indices(farm_id, uuid4())
                    for farm_id in farm_location_ids
                ]
                
                results = await asyncio.gather(*tasks)
                elapsed_time = time.time() - start_time
                
                # Verify all requests completed successfully
                assert len(results) == 10
                assert all("spi" in result for result in results)
                
                # Performance assertion - concurrent requests should be efficient
                assert elapsed_time < 2.0  # Less than 2 seconds for 10 concurrent requests


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
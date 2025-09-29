"""
Tests for Personalized Alert Service

Comprehensive test suite for personalized drought alert configuration,
monitoring, and response management functionality.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, date, timedelta
from uuid import UUID, uuid4
from decimal import Decimal

from ..models.personalized_alert_models import (
    PersonalizedAlertConfig,
    PersonalizedAlertThreshold,
    NotificationPreference,
    EmergencyProtocol,
    PersonalizedAlert,
    AutomatedResponseRecommendation,
    ResponseTracking,
    ResourceMobilization,
    AlertConfigurationRequest,
    AlertConfigurationResponse,
    AlertHistoryResponse,
    ResponseEffectivenessReport,
    AlertSeverity,
    AlertType,
    NotificationChannel,
    ResponseActionType,
    EmergencyProtocolType
)
from ..services.personalized_alert_service import PersonalizedAlertService

class TestPersonalizedAlertService:
    """Test suite for PersonalizedAlertService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return PersonalizedAlertService()
    
    @pytest.fixture
    def mock_alert_config_request(self):
        """Create mock alert configuration request."""
        return AlertConfigurationRequest(
            farm_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            user_id=UUID("123e4567-e89b-12d3-a456-426614174001"),
            crop_types=["corn", "soybeans"],
            current_practices=["no_till", "cover_crops"],
            irrigation_system_type="center_pivot",
            water_source_types=["well", "surface_water"],
            notification_preferences=[
                NotificationPreference(
                    channel=NotificationChannel.EMAIL,
                    enabled=True,
                    severity_levels=[AlertSeverity.HIGH, AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY],
                    frequency_limit=10
                )
            ],
            emergency_contacts=[
                {
                    "name": "John Doe",
                    "phone": "+1234567890",
                    "email": "john@example.com",
                    "role": "farm_manager"
                }
            ]
        )
    
    @pytest.fixture
    def mock_personalized_alert(self):
        """Create mock personalized alert."""
        return PersonalizedAlert(
            alert_id=uuid4(),
            farm_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            user_id=UUID("123e4567-e89b-12d3-a456-426614174001"),
            alert_type=AlertType.DROUGHT_ONSET,
            severity=AlertSeverity.HIGH,
            title="Drought Onset Alert",
            message="Drought conditions detected",
            triggered_threshold=PersonalizedAlertThreshold(
                threshold_id=uuid4(),
                alert_type=AlertType.DROUGHT_ONSET,
                metric_name="drought_index",
                threshold_value=0.5,
                comparison_operator="<",
                severity_level=AlertSeverity.HIGH
            ),
            current_metrics={"drought_index": 0.3},
            notification_channels=[NotificationChannel.EMAIL]
        )
    
    @pytest.mark.asyncio
    async def test_initialize_service(self, service):
        """Test service initialization."""
        await service.initialize()
        
        assert service.initialized is True
        assert service.notification_service is not None
        assert service.drought_monitoring_service is not None
        assert len(service.emergency_protocols) > 0
        
        await service.cleanup()
        assert service.initialized is False
    
    @pytest.mark.asyncio
    async def test_configure_personalized_alerts(self, service, mock_alert_config_request):
        """Test personalized alert configuration."""
        await service.initialize()
        
        response = await service.configure_personalized_alerts(mock_alert_config_request)
        
        assert isinstance(response, AlertConfigurationResponse)
        assert response.farm_id == mock_alert_config_request.farm_id
        assert len(response.configured_thresholds) > 0
        assert len(response.notification_preferences) > 0
        assert len(response.emergency_protocols) > 0
        assert "total_thresholds" in response.configuration_summary
        
        # Verify configuration is stored
        assert str(mock_alert_config_request.farm_id) in service.alert_configs
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_monitor_and_generate_alerts(self, service, mock_alert_config_request):
        """Test farm monitoring and alert generation."""
        await service.initialize()
        
        # Configure alerts first
        await service.configure_personalized_alerts(mock_alert_config_request)
        
        # Mock farm conditions that trigger alerts
        with patch.object(service, '_get_farm_conditions', return_value={
            "soil_moisture_percent": 25.0,
            "drought_index": 0.3,
            "irrigation_efficiency_percent": 65.0
        }):
            alerts = await service.monitor_and_generate_alerts(mock_alert_config_request.farm_id)
            
            assert isinstance(alerts, list)
            # Should generate alerts for exceeded thresholds
            assert len(alerts) > 0
            
            for alert in alerts:
                assert isinstance(alert, PersonalizedAlert)
                assert alert.farm_id == mock_alert_config_request.farm_id
                assert len(alert.automated_responses) > 0
                assert len(alert.emergency_protocols) > 0
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_generate_automated_responses(self, service, mock_personalized_alert):
        """Test automated response generation."""
        await service.initialize()
        
        farm_conditions = {
            "soil_moisture_percent": 25.0,
            "drought_index": 0.3,
            "irrigation_efficiency_percent": 65.0
        }
        
        responses = await service.generate_automated_responses(mock_personalized_alert, farm_conditions)
        
        assert isinstance(responses, list)
        assert len(responses) > 0
        
        for response in responses:
            assert isinstance(response, AutomatedResponseRecommendation)
            assert response.alert_id == mock_personalized_alert.alert_id
            assert response.priority >= 1 and response.priority <= 5
            assert response.estimated_effectiveness >= 0 and response.estimated_effectiveness <= 1
            assert response.implementation_time_hours >= 0
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_activate_emergency_protocol(self, service):
        """Test emergency protocol activation."""
        await service.initialize()
        
        alert_id = uuid4()
        protocol_id = uuid4()
        authorization_details = {"user_id": "test_user", "role": "farm_manager"}
        
        # Mock protocol in service
        service.emergency_protocols[str(protocol_id)] = EmergencyProtocol(
            protocol_id=protocol_id,
            protocol_type=EmergencyProtocolType.WATER_RESTRICTION,
            name="Test Protocol",
            description="Test emergency protocol",
            trigger_conditions=[{"drought_index": "<", "value": 0.2}],
            activation_threshold=AlertSeverity.CRITICAL,
            steps=[
                {"step": 1, "action": "Assess situation", "duration_minutes": 30}
            ],
            estimated_duration_hours=2,
            resource_requirements=["water_monitoring_system"]
        )
        
        result = await service.activate_emergency_protocol(alert_id, protocol_id, authorization_details)
        
        assert isinstance(result, dict)
        assert "protocol_id" in result
        assert "alert_id" in result
        assert "status" in result
        assert result["status"] == "activated"
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_track_response_action(self, service):
        """Test response action tracking."""
        await service.initialize()
        
        alert_id = uuid4()
        recommendation_id = uuid4()
        action_taken = "Applied emergency irrigation"
        action_type = ResponseActionType.IRRIGATION_ADJUSTMENT
        
        tracking = await service.track_response_action(
            alert_id, recommendation_id, action_taken, action_type
        )
        
        assert isinstance(tracking, ResponseTracking)
        assert tracking.alert_id == alert_id
        assert tracking.recommendation_id == recommendation_id
        assert tracking.action_taken == action_taken
        assert tracking.action_type == action_type
        assert tracking.implementation_status == "in_progress"
        assert tracking.start_time is not None
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_mobilize_resources(self, service):
        """Test resource mobilization."""
        await service.initialize()
        
        alert_id = uuid4()
        resource_requirements = [
            {
                "resource_type": "water_tanker",
                "resource_name": "Emergency Water Tanker",
                "quantity_needed": 2.0,
                "unit": "units",
                "urgency_level": AlertSeverity.HIGH,
                "source_location": "Local Water Company",
                "destination_location": "Farm Field A",
                "contact_information": {
                    "phone": "+1234567890",
                    "email": "emergency@watercompany.com"
                }
            }
        ]
        
        mobilizations = await service.mobilize_resources(alert_id, resource_requirements)
        
        assert isinstance(mobilizations, list)
        assert len(mobilizations) == 1
        
        mobilization = mobilizations[0]
        assert isinstance(mobilization, ResourceMobilization)
        assert mobilization.alert_id == alert_id
        assert mobilization.resource_type == "water_tanker"
        assert mobilization.quantity_needed == 2.0
        assert mobilization.status == "requested"
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_get_alert_history(self, service):
        """Test alert history retrieval."""
        await service.initialize()
        
        farm_id = UUID("123e4567-e89b-12d3-a456-426614174000")
        
        response = await service.get_alert_history(farm_id, page=1, page_size=10)
        
        assert isinstance(response, AlertHistoryResponse)
        assert response.farm_id == farm_id
        assert response.page == 1
        assert response.page_size == 10
        assert isinstance(response.alerts, list)
        assert isinstance(response.total_count, int)
        assert isinstance(response.has_next, bool)
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_generate_effectiveness_report(self, service):
        """Test effectiveness report generation."""
        await service.initialize()
        
        farm_id = UUID("123e4567-e89b-12d3-a456-426614174000")
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()
        
        report = await service.generate_effectiveness_report(farm_id, start_date, end_date)
        
        assert isinstance(report, ResponseEffectivenessReport)
        assert report.farm_id == farm_id
        assert report.report_period_start == start_date.date()
        assert report.report_period_end == end_date.date()
        assert isinstance(report.total_alerts, int)
        assert isinstance(report.alerts_with_responses, int)
        assert isinstance(report.average_response_time_hours, float)
        assert isinstance(report.average_effectiveness_rating, float)
        assert isinstance(report.total_cost_incurred, Decimal)
        assert isinstance(report.cost_savings_achieved, Decimal)
        assert isinstance(report.recommendations, list)
        
        await service.cleanup()
    
    def test_evaluate_threshold_condition(self, service):
        """Test threshold condition evaluation."""
        # Test greater than
        assert service._evaluate_threshold_condition(10.0, 5.0, ">") is True
        assert service._evaluate_threshold_condition(3.0, 5.0, ">") is False
        
        # Test less than
        assert service._evaluate_threshold_condition(3.0, 5.0, "<") is True
        assert service._evaluate_threshold_condition(10.0, 5.0, "<") is False
        
        # Test greater than or equal
        assert service._evaluate_threshold_condition(5.0, 5.0, ">=") is True
        assert service._evaluate_threshold_condition(6.0, 5.0, ">=") is True
        assert service._evaluate_threshold_condition(4.0, 5.0, ">=") is False
        
        # Test less than or equal
        assert service._evaluate_threshold_condition(5.0, 5.0, "<=") is True
        assert service._evaluate_threshold_condition(4.0, 5.0, "<=") is True
        assert service._evaluate_threshold_condition(6.0, 5.0, "<=") is False
        
        # Test equality
        assert service._evaluate_threshold_condition(5.0, 5.0, "==") is True
        assert service._evaluate_threshold_condition(4.0, 5.0, "==") is False
        
        # Test inequality
        assert service._evaluate_threshold_condition(4.0, 5.0, "!=") is True
        assert service._evaluate_threshold_condition(5.0, 5.0, "!=") is False
    
    def test_severity_level_higher(self, service):
        """Test severity level comparison."""
        assert service._severity_level_higher(AlertSeverity.HIGH, AlertSeverity.MEDIUM) is True
        assert service._severity_level_higher(AlertSeverity.CRITICAL, AlertSeverity.HIGH) is True
        assert service._severity_level_higher(AlertSeverity.EMERGENCY, AlertSeverity.CRITICAL) is True
        
        assert service._severity_level_higher(AlertSeverity.MEDIUM, AlertSeverity.HIGH) is False
        assert service._severity_level_higher(AlertSeverity.LOW, AlertSeverity.MEDIUM) is False
        assert service._severity_level_higher(AlertSeverity.MEDIUM, AlertSeverity.MEDIUM) is False


class TestPersonalizedAlertModels:
    """Test suite for personalized alert models."""
    
    def test_personalized_alert_threshold_validation(self):
        """Test threshold model validation."""
        # Valid threshold
        threshold = PersonalizedAlertThreshold(
            threshold_id=uuid4(),
            alert_type=AlertType.DROUGHT_ONSET,
            metric_name="drought_index",
            threshold_value=0.5,
            comparison_operator="<",
            severity_level=AlertSeverity.HIGH
        )
        assert threshold.threshold_value == 0.5
        assert threshold.comparison_operator == "<"
        
        # Invalid comparison operator
        with pytest.raises(ValueError):
            PersonalizedAlertThreshold(
                threshold_id=uuid4(),
                alert_type=AlertType.DROUGHT_ONSET,
                metric_name="drought_index",
                threshold_value=0.5,
                comparison_operator="invalid",
                severity_level=AlertSeverity.HIGH
            )
    
    def test_notification_preference_validation(self):
        """Test notification preference model validation."""
        preference = NotificationPreference(
            channel=NotificationChannel.EMAIL,
            enabled=True,
            severity_levels=[AlertSeverity.HIGH, AlertSeverity.CRITICAL],
            frequency_limit=10,
            escalation_delay_minutes=30
        )
        assert preference.channel == NotificationChannel.EMAIL
        assert preference.enabled is True
        assert len(preference.severity_levels) == 2
    
    def test_automated_response_recommendation_validation(self):
        """Test automated response recommendation model validation."""
        recommendation = AutomatedResponseRecommendation(
            recommendation_id=uuid4(),
            alert_id=uuid4(),
            action_type=ResponseActionType.IRRIGATION_ADJUSTMENT,
            action_name="Increase Irrigation",
            description="Increase irrigation frequency",
            priority=1,
            estimated_cost=Decimal("50.00"),
            estimated_effectiveness=0.8,
            implementation_time_hours=2,
            required_resources=["irrigation_system"],
            prerequisites=["water_available"],
            expected_outcome="Improved soil moisture",
            risk_assessment="Low risk"
        )
        assert recommendation.priority == 1
        assert recommendation.estimated_effectiveness == 0.8
        assert recommendation.implementation_time_hours == 2
    
    def test_emergency_protocol_validation(self):
        """Test emergency protocol model validation."""
        protocol = EmergencyProtocol(
            protocol_id=uuid4(),
            protocol_type=EmergencyProtocolType.WATER_RESTRICTION,
            name="Water Restriction Protocol",
            description="Implement water restrictions",
            trigger_conditions=[{"drought_index": "<", "value": 0.2}],
            activation_threshold=AlertSeverity.CRITICAL,
            steps=[
                {"step": 1, "action": "Assess situation", "duration_minutes": 30}
            ],
            estimated_duration_hours=2,
            resource_requirements=["water_monitoring_system"]
        )
        assert protocol.protocol_type == EmergencyProtocolType.WATER_RESTRICTION
        assert protocol.activation_threshold == AlertSeverity.CRITICAL
        assert protocol.estimated_duration_hours == 2


class TestPersonalizedAlertIntegration:
    """Integration tests for personalized alert system."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_alert_workflow(self):
        """Test complete alert workflow from configuration to response."""
        service = PersonalizedAlertService()
        await service.initialize()
        
        # 1. Configure alerts
        config_request = AlertConfigurationRequest(
            farm_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            user_id=UUID("123e4567-e89b-12d3-a456-426614174001"),
            crop_types=["corn"],
            notification_preferences=[
                NotificationPreference(
                    channel=NotificationChannel.EMAIL,
                    enabled=True,
                    severity_levels=[AlertSeverity.HIGH]
                )
            ]
        )
        
        config_response = await service.configure_personalized_alerts(config_request)
        assert config_response.farm_id == config_request.farm_id
        
        # 2. Monitor and generate alerts
        with patch.object(service, '_get_farm_conditions', return_value={
            "soil_moisture_percent": 20.0,  # Below threshold
            "drought_index": 0.3
        }):
            alerts = await service.monitor_and_generate_alerts(config_request.farm_id)
            assert len(alerts) > 0
            
            alert = alerts[0]
            assert alert.severity == AlertSeverity.HIGH
            
            # 3. Generate automated responses
            responses = await service.generate_automated_responses(alert, {
                "soil_moisture_percent": 20.0
            })
            assert len(responses) > 0
            
            # 4. Track response action
            response = responses[0]
            tracking = await service.track_response_action(
                alert.alert_id,
                response.recommendation_id,
                "Applied emergency irrigation",
                response.action_type
            )
            assert tracking.implementation_status == "in_progress"
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_emergency_protocol_activation_workflow(self):
        """Test emergency protocol activation workflow."""
        service = PersonalizedAlertService()
        await service.initialize()
        
        # Create emergency alert
        alert = PersonalizedAlert(
            alert_id=uuid4(),
            farm_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            user_id=UUID("123e4567-e89b-12d3-a456-426614174001"),
            alert_type=AlertType.WATER_SHORTAGE,
            severity=AlertSeverity.EMERGENCY,
            title="Emergency Water Shortage",
            message="Critical water shortage detected",
            triggered_threshold=PersonalizedAlertThreshold(
                threshold_id=uuid4(),
                alert_type=AlertType.WATER_SHORTAGE,
                metric_name="water_availability_percent",
                threshold_value=10.0,
                comparison_operator="<",
                severity_level=AlertSeverity.EMERGENCY
            ),
            current_metrics={"water_availability_percent": 5.0},
            notification_channels=[NotificationChannel.EMAIL]
        )
        
        # Activate emergency protocol
        protocol_id = list(service.emergency_protocols.keys())[0]
        result = await service.activate_emergency_protocol(
            alert.alert_id,
            UUID(protocol_id),
            {"user_id": "test_user", "role": "farm_manager"}
        )
        
        assert result["status"] == "activated"
        assert result["protocol_id"] == UUID(protocol_id)
        
        await service.cleanup()


class TestPersonalizedAlertPerformance:
    """Performance tests for personalized alert system."""
    
    @pytest.mark.asyncio
    async def test_alert_generation_performance(self):
        """Test alert generation performance with multiple thresholds."""
        service = PersonalizedAlertService()
        await service.initialize()
        
        # Create configuration with many thresholds
        config_request = AlertConfigurationRequest(
            farm_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            user_id=UUID("123e4567-e89b-12d3-a456-426614174001"),
            crop_types=["corn", "soybeans", "wheat"],
            notification_preferences=[
                NotificationPreference(
                    channel=NotificationChannel.EMAIL,
                    enabled=True,
                    severity_levels=[AlertSeverity.HIGH, AlertSeverity.CRITICAL]
                )
            ]
        )
        
        await service.configure_personalized_alerts(config_request)
        
        # Test performance with multiple monitoring cycles
        import time
        start_time = time.time()
        
        for _ in range(10):
            with patch.object(service, '_get_farm_conditions', return_value={
                "soil_moisture_percent": 25.0,
                "drought_index": 0.3,
                "irrigation_efficiency_percent": 65.0
            }):
                alerts = await service.monitor_and_generate_alerts(config_request.farm_id)
        
        elapsed_time = time.time() - start_time
        average_time = elapsed_time / 10
        
        # Should complete within reasonable time (less than 1 second per cycle)
        assert average_time < 1.0, f"Average alert generation time {average_time}s exceeds 1s limit"
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_concurrent_alert_processing(self):
        """Test concurrent alert processing for multiple farms."""
        service = PersonalizedAlertService()
        await service.initialize()
        
        # Create configurations for multiple farms
        farm_configs = []
        for i in range(5):
            config_request = AlertConfigurationRequest(
                farm_id=UUID(f"123e4567-e89b-12d3-a456-42661417400{i}"),
                user_id=UUID(f"123e4567-e89b-12d3-a456-42661417400{i}"),
                crop_types=["corn"],
                notification_preferences=[
                    NotificationPreference(
                        channel=NotificationChannel.EMAIL,
                        enabled=True,
                        severity_levels=[AlertSeverity.HIGH]
                    )
                ]
            )
            await service.configure_personalized_alerts(config_request)
            farm_configs.append(config_request)
        
        # Process alerts concurrently
        async def monitor_farm(farm_id):
            with patch.object(service, '_get_farm_conditions', return_value={
                "soil_moisture_percent": 25.0,
                "drought_index": 0.3
            }):
                return await service.monitor_and_generate_alerts(farm_id)
        
        farm_ids = [config.farm_id for config in farm_configs]
        results = await asyncio.gather(*[monitor_farm(farm_id) for farm_id in farm_ids])
        
        # Verify all farms processed successfully
        assert len(results) == 5
        for alerts in results:
            assert isinstance(alerts, list)
        
        await service.cleanup()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
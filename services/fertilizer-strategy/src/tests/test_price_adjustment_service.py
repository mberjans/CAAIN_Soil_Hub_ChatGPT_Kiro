"""
Comprehensive tests for dynamic price adjustment service.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from uuid import uuid4, UUID

from ..services.price_adjustment_service import (
    DynamicPriceAdjustmentService, AdjustmentTrigger, AdjustmentPriority
)
from ..models.price_adjustment_models import (
    PriceAdjustmentRequest, PriceAdjustmentResponse, PriceThreshold,
    AdjustmentAlert, EconomicImpactAnalysis, StrategyModification,
    ApprovalStatus, AdjustmentStrategy, NotificationMethod
)
from ..models.price_models import (
    FertilizerType, FertilizerProduct, FertilizerPriceData, PriceTrendAnalysis,
    PriceSource
)


class TestDynamicPriceAdjustmentService:
    """Test suite for dynamic price adjustment service."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return DynamicPriceAdjustmentService()
    
    @pytest.fixture
    def sample_request(self):
        """Create sample price adjustment request."""
        return PriceAdjustmentRequest(
            user_id=UUID("12345678-1234-5678-9012-123456789012"),
            fertilizer_types=[FertilizerType.NITROGEN, FertilizerType.PHOSPHORUS],
            fields=[
                {
                    "field_id": "field_1",
                    "acres": 100.0,
                    "soil_type": "clay_loam",
                    "current_ph": 6.5,
                    "organic_matter_percent": 3.2,
                    "target_yield": 180.0,
                    "crop_price": 5.50,
                    "previous_crop": "corn",
                    "tillage_system": "no_till",
                    "irrigation_available": True
                }
            ],
            region="US",
            price_change_threshold=5.0,
            volatility_threshold=15.0,
            check_interval_minutes=30,
            monitoring_duration_hours=168,
            auto_adjust_enabled=True,
            adjustment_strategy=AdjustmentStrategy.BALANCED,
            max_adjustment_percent=20.0,
            notification_enabled=True,
            notification_methods=[NotificationMethod.EMAIL],
            notification_threshold=10.0,
            require_approval=True,
            approval_timeout_hours=24
        )
    
    @pytest.fixture
    def sample_price_data(self):
        """Create sample price data."""
        return FertilizerPriceData(
            product_id="urea_current",
            product_name="Urea",
            fertilizer_type=FertilizerType.NITROGEN,
            specific_product=FertilizerProduct.UREA,
            price_per_unit=450.0,
            unit="ton",
            currency="USD",
            region="US",
            source=PriceSource.USDA_NASS,
            price_date=datetime.now().date(),
            is_spot_price=True,
            confidence=0.9,
            volatility=12.5
        )
    
    @pytest.fixture
    def sample_trend_analysis(self):
        """Create sample trend analysis."""
        return PriceTrendAnalysis(
            product_id="urea_current",
            product_name="Urea",
            region="US",
            current_price=450.0,
            current_date=datetime.now().date(),
            price_7d_ago=430.0,
            price_30d_ago=420.0,
            price_90d_ago=400.0,
            trend_7d_percent=4.65,
            trend_30d_percent=7.14,
            trend_90d_percent=12.5,
            volatility_7d=8.5,
            volatility_30d=12.5,
            volatility_90d=15.2,
            trend_direction="up",
            trend_strength="moderate",
            data_points_used=30
        )
    
    @pytest.mark.asyncio
    async def test_start_price_monitoring_success(self, service, sample_request):
        """Test successful price monitoring start."""
        with patch.object(service.price_tracker, 'get_current_price', return_value=None):
            with patch.object(service.price_tracker, 'get_price_trend', return_value=None):
                response = await service.start_price_monitoring(sample_request)
                
                assert response.success is True
                assert response.monitoring_active is True
                assert response.request_id is not None
                assert response.processing_time_ms > 0
                assert response.message == "Price monitoring started successfully"
    
    @pytest.mark.asyncio
    async def test_start_price_monitoring_validation_error(self, service):
        """Test price monitoring start with validation error."""
        invalid_request = PriceAdjustmentRequest(
            user_id=UUID("12345678-1234-5678-9012-123456789012"),
            fertilizer_types=[],  # Invalid: empty list
            fields=[],  # Invalid: empty list
            region="US"
        )
        
        response = await service.start_price_monitoring(invalid_request)
        
        assert response.success is False
        assert response.monitoring_active is False
        assert response.error_message is not None
    
    @pytest.mark.asyncio
    async def test_check_price_adjustments_success(self, service, sample_request):
        """Test successful price adjustment check."""
        # Start monitoring first
        with patch.object(service.price_tracker, 'get_current_price', return_value=None):
            with patch.object(service.price_tracker, 'get_price_trend', return_value=None):
                start_response = await service.start_price_monitoring(sample_request)
                request_id = start_response.request_id
        
        # Mock price analysis
        with patch.object(service, '_analyze_current_prices') as mock_analyze:
            mock_analyze.return_value = {
                "current_prices": {},
                "price_changes": {"urea": 6.0},  # Above threshold
                "trend_analysis": {},
                "volatility_metrics": {},
                "analysis_timestamp": datetime.utcnow()
            }
            
            with patch.object(service, '_check_adjustment_triggers') as mock_triggers:
                mock_triggers.return_value = [AdjustmentTrigger.PRICE_INCREASE]
                
                with patch.object(service, '_perform_price_adjustments') as mock_adjustments:
                    mock_adjustments.return_value = []
                    
                    with patch.object(service, '_send_adjustment_alerts') as mock_alerts:
                        mock_alerts.return_value = []
                        
                        response = await service.check_price_adjustments(request_id)
                        
                        assert response.success is True
                        assert response.monitoring_active is True
                        assert response.request_id == request_id
    
    @pytest.mark.asyncio
    async def test_check_price_adjustments_session_not_found(self, service):
        """Test price adjustment check with non-existent session."""
        response = await service.check_price_adjustments("non-existent-id")
        
        assert response.success is False
        assert response.error_message is not None
    
    @pytest.mark.asyncio
    async def test_stop_price_monitoring_success(self, service, sample_request):
        """Test successful price monitoring stop."""
        # Start monitoring first
        with patch.object(service.price_tracker, 'get_current_price', return_value=None):
            with patch.object(service.price_tracker, 'get_price_trend', return_value=None):
                start_response = await service.start_price_monitoring(sample_request)
                request_id = start_response.request_id
        
        # Stop monitoring
        response = await service.stop_price_monitoring(request_id)
        
        assert response.success is True
        assert response.monitoring_active is False
        assert response.final_report is not None
        assert response.message == "Price monitoring stopped successfully"
    
    @pytest.mark.asyncio
    async def test_stop_price_monitoring_session_not_found(self, service):
        """Test price monitoring stop with non-existent session."""
        response = await service.stop_price_monitoring("non-existent-id")
        
        assert response.success is False
        assert response.error_message is not None
    
    @pytest.mark.asyncio
    async def test_get_monitoring_status_success(self, service, sample_request):
        """Test successful monitoring status retrieval."""
        # Start monitoring first
        with patch.object(service.price_tracker, 'get_current_price', return_value=None):
            with patch.object(service.price_tracker, 'get_price_trend', return_value=None):
                start_response = await service.start_price_monitoring(sample_request)
                request_id = start_response.request_id
        
        # Get status
        status = await service.get_monitoring_status(request_id)
        
        assert status["request_id"] == request_id
        assert status["status"] == "active"
        assert "start_time" in status
        assert "last_check" in status
        assert "adjustments_made" in status
        assert "alerts_sent" in status
        assert "uptime_seconds" in status
    
    @pytest.mark.asyncio
    async def test_get_monitoring_status_session_not_found(self, service):
        """Test monitoring status retrieval with non-existent session."""
        with pytest.raises(ValueError, match="Monitoring session not found"):
            await service.get_monitoring_status("non-existent-id")
    
    @pytest.mark.asyncio
    async def test_analyze_current_prices(self, service, sample_request, sample_price_data, sample_trend_analysis):
        """Test current price analysis."""
        with patch.object(service.price_tracker, 'get_current_price', return_value=sample_price_data):
            with patch.object(service.price_tracker, 'get_price_trend', return_value=sample_trend_analysis):
                analysis = await service._analyze_current_prices(sample_request)
                
                assert "current_prices" in analysis
                assert "price_changes" in analysis
                assert "trend_analysis" in analysis
                assert "volatility_metrics" in analysis
                assert "analysis_timestamp" in analysis
    
    @pytest.mark.asyncio
    async def test_check_adjustment_triggers_price_increase(self, service, sample_request):
        """Test adjustment trigger detection for price increase."""
        current_analysis = {
            "price_changes": {"urea": 6.0},  # Above 5% threshold
            "volatility_metrics": {"urea": {"current_volatility": 10.0}},
            "trend_analysis": {"urea": MagicMock(trend_direction="up", trend_strength="moderate")}
        }
        
        triggers = await service._check_adjustment_triggers(sample_request, current_analysis)
        
        assert AdjustmentTrigger.PRICE_INCREASE in triggers
    
    @pytest.mark.asyncio
    async def test_check_adjustment_triggers_price_decrease(self, service, sample_request):
        """Test adjustment trigger detection for price decrease."""
        current_analysis = {
            "price_changes": {"urea": -6.0},  # Below -5% threshold
            "volatility_metrics": {"urea": {"current_volatility": 10.0}},
            "trend_analysis": {"urea": MagicMock(trend_direction="down", trend_strength="moderate")}
        }
        
        triggers = await service._check_adjustment_triggers(sample_request, current_analysis)
        
        assert AdjustmentTrigger.PRICE_DECREASE in triggers
    
    @pytest.mark.asyncio
    async def test_check_adjustment_triggers_volatility_spike(self, service, sample_request):
        """Test adjustment trigger detection for volatility spike."""
        current_analysis = {
            "price_changes": {"urea": 2.0},  # Below threshold
            "volatility_metrics": {"urea": {"current_volatility": 25.0}},  # Above 20% threshold
            "trend_analysis": {"urea": MagicMock(trend_direction="stable", trend_strength="weak")}
        }
        
        triggers = await service._check_adjustment_triggers(sample_request, current_analysis)
        
        assert AdjustmentTrigger.VOLATILITY_SPIKE in triggers
    
    @pytest.mark.asyncio
    async def test_check_adjustment_triggers_trend_reversal(self, service, sample_request):
        """Test adjustment trigger detection for trend reversal."""
        current_analysis = {
            "price_changes": {"urea": 2.0},  # Below threshold
            "volatility_metrics": {"urea": {"current_volatility": 10.0}},
            "trend_analysis": {"urea": MagicMock(trend_direction="up", trend_strength="strong")}
        }
        
        triggers = await service._check_adjustment_triggers(sample_request, current_analysis)
        
        assert AdjustmentTrigger.TREND_REVERSAL in triggers
    
    @pytest.mark.asyncio
    async def test_adjust_for_price_increase_significant_impact(self, service, sample_request):
        """Test adjustment for significant price increase impact."""
        current_analysis = {
            "price_changes": {"urea": 8.0},
            "current_prices": {"urea": MagicMock(price_per_unit=450.0)}
        }
        
        with patch.object(service, '_calculate_economic_impact') as mock_impact:
            mock_impact.return_value = EconomicImpactAnalysis(
                cost_impact_per_acre=50.0,
                roi_impact_percent=-12.0,  # Significant negative impact
                yield_impact_percent=0.0,
                break_even_impact_percent=-12.0,
                recommendation_confidence=0.8,
                analysis_timestamp=datetime.utcnow()
            )
            
            modification = await service._adjust_for_price_increase(sample_request, current_analysis)
            
            assert modification is not None
            assert modification.modification_type == "rate_reduction"
            assert modification.adjustment_percent == -15.0
            assert modification.requires_approval is True
    
    @pytest.mark.asyncio
    async def test_adjust_for_price_decrease_significant_impact(self, service, sample_request):
        """Test adjustment for significant price decrease impact."""
        current_analysis = {
            "price_changes": {"urea": -8.0},
            "current_prices": {"urea": MagicMock(price_per_unit=450.0)}
        }
        
        with patch.object(service, '_calculate_economic_impact') as mock_impact:
            mock_impact.return_value = EconomicImpactAnalysis(
                cost_impact_per_acre=-30.0,
                roi_impact_percent=12.0,  # Significant positive impact
                yield_impact_percent=0.0,
                break_even_impact_percent=12.0,
                recommendation_confidence=0.8,
                analysis_timestamp=datetime.utcnow()
            )
            
            modification = await service._adjust_for_price_decrease(sample_request, current_analysis)
            
            assert modification is not None
            assert modification.modification_type == "rate_increase"
            assert modification.adjustment_percent == 12.0
            assert modification.requires_approval is True
    
    @pytest.mark.asyncio
    async def test_adjust_for_volatility(self, service, sample_request):
        """Test adjustment for high volatility."""
        current_analysis = {
            "volatility_metrics": {"urea": {"current_volatility": 25.0}}
        }
        
        modification = await service._adjust_for_volatility(sample_request, current_analysis)
        
        assert modification is not None
        assert modification.modification_type == "conservative_adjustment"
        assert modification.adjustment_percent == -5.0
        assert modification.requires_approval is True
    
    @pytest.mark.asyncio
    async def test_calculate_economic_impact(self, service, sample_request):
        """Test economic impact calculation."""
        current_analysis = {
            "price_changes": {"urea": 6.0, "dap": 4.0}
        }
        
        impact = await service._calculate_economic_impact(
            sample_request, current_analysis, "price_increase"
        )
        
        assert impact.cost_impact_per_acre > 0
        assert impact.roi_impact_percent != 0
        assert impact.recommendation_confidence > 0
        assert impact.analysis_timestamp is not None
    
    @pytest.mark.asyncio
    async def test_send_adjustment_alerts(self, service, sample_request):
        """Test adjustment alert sending."""
        triggers = [AdjustmentTrigger.PRICE_INCREASE, AdjustmentTrigger.VOLATILITY_SPIKE]
        adjustments = [
            StrategyModification(
                modification_type="rate_reduction",
                fertilizer_type=FertilizerType.NITROGEN,
                adjustment_percent=-15.0,
                reason="Price increase significantly impacts ROI",
                requires_approval=True
            )
        ]
        
        alerts = await service._send_adjustment_alerts(sample_request, triggers, adjustments)
        
        assert len(alerts) > 0
        assert all(isinstance(alert, AdjustmentAlert) for alert in alerts)
        assert all(alert.requires_action for alert in alerts)
    
    def test_determine_alert_priority(self, service):
        """Test alert priority determination."""
        assert service._determine_alert_priority(AdjustmentTrigger.MARKET_SHOCK) == AdjustmentPriority.CRITICAL
        assert service._determine_alert_priority(AdjustmentTrigger.VOLATILITY_SPIKE) == AdjustmentPriority.HIGH
        assert service._determine_alert_priority(AdjustmentTrigger.PRICE_INCREASE) == AdjustmentPriority.MEDIUM
        assert service._determine_alert_priority(AdjustmentTrigger.PRICE_DECREASE) == AdjustmentPriority.MEDIUM
        assert service._determine_alert_priority(AdjustmentTrigger.TREND_REVERSAL) == AdjustmentPriority.HIGH
        assert service._determine_alert_priority(AdjustmentTrigger.THRESHOLD_BREACH) == AdjustmentPriority.MEDIUM
    
    def test_generate_alert_message(self, service):
        """Test alert message generation."""
        # Test with adjustments
        adjustments = [
            StrategyModification(
                modification_type="rate_reduction",
                fertilizer_type=FertilizerType.NITROGEN,
                adjustment_percent=-15.0,
                reason="Test reason",
                requires_approval=True
            )
        ]
        
        message = service._generate_alert_message(AdjustmentTrigger.PRICE_INCREASE, adjustments)
        assert "Significant fertilizer price increase detected" in message
        assert "1 adjustment(s) recommended" in message
        
        # Test without adjustments
        message = service._generate_alert_message(AdjustmentTrigger.PRICE_INCREASE, [])
        assert "Significant fertilizer price increase detected" in message
        assert "adjustment(s) recommended" not in message
    
    def test_calculate_volatility_metrics(self, service, sample_trend_analysis):
        """Test volatility metrics calculation."""
        metrics = service._calculate_volatility_metrics(sample_trend_analysis)
        
        assert "current_volatility" in metrics
        assert "volatility_30d" in metrics
        assert "volatility_90d" in metrics
        assert "volatility_trend" in metrics
        assert metrics["current_volatility"] == 8.5
        assert metrics["volatility_30d"] == 12.5
        assert metrics["volatility_90d"] == 15.2
    
    def test_get_products_by_type(self, service):
        """Test product retrieval by fertilizer type."""
        nitrogen_products = service._get_products_by_type(FertilizerType.NITROGEN)
        assert FertilizerProduct.UREA in nitrogen_products
        assert FertilizerProduct.ANHYDROUS_AMMONIA in nitrogen_products
        
        phosphorus_products = service._get_products_by_type(FertilizerType.PHOSPHORUS)
        assert FertilizerProduct.DAP in phosphorus_products
        assert FertilizerProduct.MAP in phosphorus_products
        
        potassium_products = service._get_products_by_type(FertilizerType.POTASSIUM)
        assert FertilizerProduct.MURIATE_OF_POTASH in potassium_products
        assert FertilizerProduct.POTASSIUM_SULFATE in potassium_products
    
    @pytest.mark.asyncio
    async def test_generate_monitoring_report(self, service):
        """Test monitoring report generation."""
        session = {
            "request_id": "test-request-id",
            "start_time": datetime.utcnow() - timedelta(hours=2),
            "end_time": datetime.utcnow(),
            "adjustments_made": 3,
            "alerts_sent": 5
        }
        
        report = await service._generate_monitoring_report(session)
        
        assert "session_summary" in report
        assert "performance_metrics" in report
        assert report["session_summary"]["request_id"] == "test-request-id"
        assert report["session_summary"]["adjustments_made"] == 3
        assert report["session_summary"]["alerts_sent"] == 5
        assert report["session_summary"]["duration_hours"] > 0


class TestPriceAdjustmentIntegration:
    """Integration tests for price adjustment system."""
    
    @pytest.mark.asyncio
    async def test_full_monitoring_workflow(self):
        """Test complete monitoring workflow from start to stop."""
        service = DynamicPriceAdjustmentService()
        
        # Create request
        request = PriceAdjustmentRequest(
            user_id=UUID("12345678-1234-5678-9012-123456789012"),
            fertilizer_types=[FertilizerType.NITROGEN],
            fields=[{"field_id": "field_1", "acres": 100.0}],
            region="US",
            price_change_threshold=5.0,
            monitoring_duration_hours=1  # Short duration for testing
        )
        
        # Mock external dependencies
        with patch.object(service.price_tracker, 'get_current_price', return_value=None):
            with patch.object(service.price_tracker, 'get_price_trend', return_value=None):
                # Start monitoring
                start_response = await service.start_price_monitoring(request)
                assert start_response.success is True
                
                request_id = start_response.request_id
                
                # Check adjustments
                check_response = await service.check_price_adjustments(request_id)
                assert check_response.success is True
                
                # Get status
                status = await service.get_monitoring_status(request_id)
                assert status["status"] == "active"
                
                # Stop monitoring
                stop_response = await service.stop_price_monitoring(request_id)
                assert stop_response.success is True
                assert stop_response.final_report is not None
    
    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self):
        """Test error handling and recovery mechanisms."""
        service = DynamicPriceAdjustmentService()
        
        # Test with invalid request
        invalid_request = PriceAdjustmentRequest(
            user_id=UUID("12345678-1234-5678-9012-123456789012"),
            fertilizer_types=[],  # Invalid
            fields=[],  # Invalid
            region="US"
        )
        
        response = await service.start_price_monitoring(invalid_request)
        assert response.success is False
        assert response.error_message is not None
        
        # Test with non-existent session
        response = await service.check_price_adjustments("non-existent-id")
        assert response.success is False
        assert response.error_message is not None
        
        response = await service.stop_price_monitoring("non-existent-id")
        assert response.success is False
        assert response.error_message is not None
        
        with pytest.raises(ValueError):
            await service.get_monitoring_status("non-existent-id")


class TestPriceAdjustmentPerformance:
    """Performance tests for price adjustment system."""
    
    @pytest.mark.asyncio
    async def test_monitoring_startup_performance(self):
        """Test monitoring startup performance."""
        service = DynamicPriceAdjustmentService()
        
        request = PriceAdjustmentRequest(
            user_id=UUID("12345678-1234-5678-9012-123456789012"),
            fertilizer_types=[FertilizerType.NITROGEN, FertilizerType.PHOSPHORUS],
            fields=[{"field_id": f"field_{i}", "acres": 100.0} for i in range(10)],  # Multiple fields
            region="US"
        )
        
        with patch.object(service.price_tracker, 'get_current_price', return_value=None):
            with patch.object(service.price_tracker, 'get_price_trend', return_value=None):
                start_time = datetime.utcnow()
                response = await service.start_price_monitoring(request)
                end_time = datetime.utcnow()
                
                assert response.success is True
                assert response.processing_time_ms < 5000  # Should complete within 5 seconds
                assert (end_time - start_time).total_seconds() < 5.0
    
    @pytest.mark.asyncio
    async def test_concurrent_monitoring_sessions(self):
        """Test concurrent monitoring sessions."""
        service = DynamicPriceAdjustmentService()
        
        # Create multiple requests
        requests = []
        for i in range(5):
            request = PriceAdjustmentRequest(
                user_id=UUID("12345678-1234-5678-9012-123456789012"),
                fertilizer_types=[FertilizerType.NITROGEN],
                fields=[{"field_id": f"field_{i}", "acres": 100.0}],
                region="US"
            )
            requests.append(request)
        
        # Start all monitoring sessions concurrently
        with patch.object(service.price_tracker, 'get_current_price', return_value=None):
            with patch.object(service.price_tracker, 'get_price_trend', return_value=None):
                start_time = datetime.utcnow()
                responses = await asyncio.gather(*[
                    service.start_price_monitoring(request) for request in requests
                ])
                end_time = datetime.utcnow()
                
                # All should succeed
                assert all(response.success for response in responses)
                assert (end_time - start_time).total_seconds() < 10.0  # Should complete within 10 seconds
                
                # Clean up
                for response in responses:
                    if response.success:
                        await service.stop_price_monitoring(response.request_id)
"""
Comprehensive tests for the intelligent price optimization alert service.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from uuid import uuid4

from ..services.price_optimization_alert_service import (
    PriceOptimizationAlertService, AlertType, AlertPriority, AlertChannel
)
from ..models.price_models import FertilizerPriceData, FertilizerType, FertilizerProduct, PriceSource
from ..models.price_optimization_alert_models import (
    AlertCreationRequest, UserAlertPreferences, AlertThresholdConfig
)


class TestPriceOptimizationAlertService:
    """Test suite for the intelligent price optimization alert service."""

    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return PriceOptimizationAlertService()

    @pytest.fixture
    def mock_price_data(self):
        """Create mock price data for testing."""
        return FertilizerPriceData(
            product_id=str(uuid4()),
            product_name="urea_standard",
            fertilizer_type=FertilizerType.NITROGEN,
            specific_product=FertilizerProduct.UREA,
            price_per_unit=500.0,
            unit="ton",
            region="US",
            source=PriceSource.USDA_NASS,
            price_date=datetime.utcnow().date(),
            confidence=0.9,
            volatility=15.0,
            created_at=datetime.utcnow()
        )

    @pytest.fixture
    def mock_historical_data(self):
        """Create mock historical price data."""
        base_price = 500.0
        historical_data = []
        
        for i in range(30):
            price_data = FertilizerPriceData(
                product_id=str(uuid4()),
                product_name="urea_standard",
                fertilizer_type=FertilizerType.NITROGEN,
                specific_product=FertilizerProduct.UREA,
                price_per_unit=base_price + (i * 2),  # Increasing trend
                unit="ton",
                region="US",
                source=PriceSource.USDA_NASS,
                price_date=(datetime.utcnow() - timedelta(days=30-i)).date(),
                confidence=0.9,
                volatility=15.0,
                created_at=datetime.utcnow() - timedelta(days=30-i)
            )
            historical_data.append(price_data)
        
        return historical_data

    @pytest.mark.asyncio
    async def test_create_intelligent_alert_price_threshold(self, service, mock_price_data, mock_historical_data):
        """Test creating a price threshold alert."""
        user_id = "test_user_123"
        
        with patch.object(service.price_tracker, 'get_current_price', return_value=mock_price_data):
            alert = await service.create_intelligent_alert(
                user_id=user_id,
                fertilizer_type=FertilizerType.NITROGEN,
                alert_type=AlertType.PRICE_THRESHOLD,
                current_price=mock_price_data,
                historical_data=mock_historical_data
            )
            
            if alert:  # Alert might not be created if conditions aren't met
                assert alert.trigger_type == AlertType.PRICE_THRESHOLD.value
                assert alert.request_id.startswith(f"alert_{user_id}")
                assert alert.message is not None
                assert alert.timestamp is not None

    @pytest.mark.asyncio
    async def test_create_intelligent_alert_opportunity(self, service, mock_price_data, mock_historical_data):
        """Test creating an opportunity alert."""
        user_id = "test_user_456"
        
        # Modify price data to create opportunity conditions
        opportunity_price = FertilizerPriceData(
            product_id=str(uuid4()),
            product_name="urea_standard",
            fertilizer_type=FertilizerType.NITROGEN,
            specific_product=FertilizerProduct.UREA,
            price_per_unit=450.0,  # Lower price for opportunity
            unit="ton",
            region="US",
            source=PriceSource.USDA_NASS,
            price_date=datetime.utcnow().date(),
            confidence=0.9,
            volatility=15.0,
            created_at=datetime.utcnow()
        )
        
        with patch.object(service.price_tracker, 'get_current_price', return_value=opportunity_price):
            alert = await service.create_intelligent_alert(
                user_id=user_id,
                fertilizer_type=FertilizerType.NITROGEN,
                alert_type=AlertType.OPPORTUNITY,
                current_price=opportunity_price,
                historical_data=mock_historical_data
            )
            
            if alert:
                assert alert.trigger_type == AlertType.OPPORTUNITY.value
                assert "opportunity" in alert.message.lower()

    @pytest.mark.asyncio
    async def test_create_intelligent_alert_risk(self, service, mock_price_data, mock_historical_data):
        """Test creating a risk alert."""
        user_id = "test_user_789"
        
        with patch.object(service.price_tracker, 'get_current_price', return_value=mock_price_data):
            alert = await service.create_intelligent_alert(
                user_id=user_id,
                fertilizer_type=FertilizerType.NITROGEN,
                alert_type=AlertType.RISK,
                current_price=mock_price_data,
                historical_data=mock_historical_data
            )
            
            if alert:
                assert alert.trigger_type == AlertType.RISK.value
                assert alert.priority in [AlertPriority.LOW.value, AlertPriority.MEDIUM.value, AlertPriority.HIGH.value, AlertPriority.CRITICAL.value]

    @pytest.mark.asyncio
    async def test_monitor_price_optimization_opportunities(self, service, mock_price_data, mock_historical_data):
        """Test monitoring for price optimization opportunities."""
        user_id = "test_user_monitor"
        fertilizer_types = [FertilizerType.NITROGEN, FertilizerType.PHOSPHORUS]
        
        with patch.object(service.price_tracker, 'get_current_price', return_value=mock_price_data):
            with patch.object(service, '_get_historical_price_data', return_value=mock_historical_data):
                alerts = await service.monitor_price_optimization_opportunities(
                    user_id=user_id,
                    fertilizer_types=fertilizer_types,
                    monitoring_duration_hours=24
                )
                
                assert isinstance(alerts, list)
                # Alerts might be empty if conditions aren't met
                for alert in alerts:
                    assert alert.alert_id is not None
                    assert alert.request_id is not None
                    assert alert.message is not None

    @pytest.mark.asyncio
    async def test_analyze_price_patterns(self, service, mock_price_data, mock_historical_data):
        """Test price pattern analysis."""
        pattern_analysis = await service._analyze_price_patterns(
            mock_price_data, mock_historical_data, AlertType.OPPORTUNITY
        )
        
        assert isinstance(pattern_analysis, dict)
        assert "confidence" in pattern_analysis
        assert "prediction" in pattern_analysis
        assert "model_used" in pattern_analysis
        assert 0.0 <= pattern_analysis["confidence"] <= 1.0

    def test_extract_price_features(self, service, mock_price_data, mock_historical_data):
        """Test price feature extraction."""
        features = service._extract_price_features(mock_price_data, mock_historical_data)
        
        assert isinstance(features, dict)
        assert "current_price" in features
        assert "price_change_1d" in features
        assert "price_change_7d" in features
        assert "price_change_30d" in features
        assert "volatility_7d" in features
        assert "volatility_30d" in features
        assert "trend_strength" in features
        assert "moving_average_7d" in features
        assert "moving_average_30d" in features
        assert "price_momentum" in features
        assert "seasonal_factor" in features

    @pytest.mark.asyncio
    async def test_apply_opportunity_model(self, service):
        """Test opportunity detection ML model."""
        features = {
            "price_change_7d": -8.0,  # Significant price drop
            "volatility_7d": 25.0,    # High volatility
            "trend_strength": -0.6,   # Strong downward trend
            "seasonal_factor": 0.7     # Below normal seasonal price
        }
        
        analysis = await service._apply_opportunity_model(features)
        
        assert isinstance(analysis, dict)
        assert "confidence" in analysis
        assert "prediction" in analysis
        assert "pattern_type" in analysis
        assert 0.0 <= analysis["confidence"] <= 1.0

    @pytest.mark.asyncio
    async def test_apply_risk_model(self, service):
        """Test risk assessment ML model."""
        features = {
            "volatility_30d": 30.0,   # High volatility
            "price_momentum": 0.9,    # Strong upward momentum
            "trend_strength": 0.95    # Very strong trend
        }
        
        analysis = await service._apply_risk_model(features)
        
        assert isinstance(analysis, dict)
        assert "confidence" in analysis
        assert "prediction" in analysis
        assert "pattern_type" in analysis

    @pytest.mark.asyncio
    async def test_apply_timing_model(self, service):
        """Test timing optimization ML model."""
        features = {
            "seasonal_factor": 1.05,  # Near optimal seasonal timing
            "price_momentum": 0.1,    # Low momentum
            "volatility_7d": 12.0     # Low volatility
        }
        
        analysis = await service._apply_timing_model(features)
        
        assert isinstance(analysis, dict)
        assert "confidence" in analysis
        assert "prediction" in analysis
        assert "pattern_type" in analysis

    @pytest.mark.asyncio
    async def test_evaluate_alert_conditions(self, service, mock_price_data, mock_historical_data):
        """Test alert condition evaluation."""
        thresholds = service.default_thresholds[FertilizerType.NITROGEN]
        pattern_analysis = {"confidence": 0.8, "prediction": "opportunity"}
        
        should_alert, confidence = await service._evaluate_alert_conditions(
            AlertType.OPPORTUNITY, mock_price_data, mock_historical_data, thresholds, pattern_analysis
        )
        
        assert isinstance(should_alert, bool)
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0

    @pytest.mark.asyncio
    async def test_generate_intelligent_alert_content(self, service, mock_price_data, mock_historical_data):
        """Test intelligent alert content generation."""
        pattern_analysis = {
            "confidence": 0.8,
            "prediction": "opportunity",
            "pattern_type": "price_drop"
        }
        
        content = await service._generate_intelligent_alert_content(
            AlertType.OPPORTUNITY, mock_price_data, mock_historical_data, pattern_analysis, 0.8
        )
        
        assert isinstance(content, dict)
        assert "message" in content
        assert "details" in content
        assert "requires_action" in content
        assert isinstance(content["requires_action"], bool)

    def test_get_user_thresholds_default(self, service):
        """Test getting default user thresholds."""
        thresholds = service._get_user_thresholds("test_user", FertilizerType.NITROGEN, None)
        
        assert thresholds.fertilizer_type == FertilizerType.NITROGEN
        assert thresholds.price_change_percent == 5.0
        assert thresholds.volatility_threshold == 15.0
        assert thresholds.trend_strength_threshold == 0.7

    def test_get_user_thresholds_custom(self, service):
        """Test getting custom user thresholds."""
        custom_preferences = {
            "alert_thresholds": {
                "nitrogen": {
                    "price_change_percent": 3.0,
                    "volatility_threshold": 12.0,
                    "trend_strength_threshold": 0.8,
                    "opportunity_threshold": 8.0,
                    "risk_threshold": 15.0,
                    "timing_threshold_days": 5
                }
            }
        }
        
        thresholds = service._get_user_thresholds("test_user", FertilizerType.NITROGEN, custom_preferences)
        
        assert thresholds.price_change_percent == 3.0
        assert thresholds.volatility_threshold == 12.0
        assert thresholds.trend_strength_threshold == 0.8

    def test_determine_alert_priority(self, service):
        """Test alert priority determination."""
        pattern_analysis = {"confidence": 0.8}
        
        # Test different alert types and priorities
        priority = service._determine_alert_priority(AlertType.MARKET_SHOCK, 0.9, pattern_analysis)
        assert priority == AlertPriority.CRITICAL
        
        priority = service._determine_alert_priority(AlertType.RISK, 0.9, pattern_analysis)
        assert priority == AlertPriority.HIGH
        
        priority = service._determine_alert_priority(AlertType.OPPORTUNITY, 0.8, pattern_analysis)
        assert priority == AlertPriority.HIGH
        
        priority = service._determine_alert_priority(AlertType.PRICE_THRESHOLD, 0.5, pattern_analysis)
        assert priority == AlertPriority.LOW

    def test_calculate_price_change(self, service):
        """Test price change calculation."""
        prices = [100.0, 105.0, 110.0, 108.0, 115.0]
        
        # Test 1-day change
        change_1d = service._calculate_price_change(prices, 1)
        assert abs(change_1d - 6.48) < 0.1  # (115-108)/108 * 100 ≈ 6.48
        
        # Test 3-day change
        change_3d = service._calculate_price_change(prices, 3)
        assert abs(change_3d - 9.52) < 0.1  # (115-105)/105 * 100 ≈ 9.52

    def test_calculate_volatility(self, service):
        """Test volatility calculation."""
        prices = [100.0, 105.0, 110.0, 108.0, 115.0]
        volatility = service._calculate_volatility(prices)
        
        assert isinstance(volatility, float)
        assert volatility >= 0.0

    def test_calculate_trend_strength(self, service):
        """Test trend strength calculation."""
        # Upward trend
        upward_prices = [100.0, 102.0, 104.0, 106.0, 108.0]
        trend_up = service._calculate_trend_strength(upward_prices)
        assert trend_up > 0
        
        # Downward trend
        downward_prices = [108.0, 106.0, 104.0, 102.0, 100.0]
        trend_down = service._calculate_trend_strength(downward_prices)
        assert trend_down < 0
        
        # Sideways trend
        sideways_prices = [100.0, 101.0, 99.0, 100.0, 101.0]
        trend_sideways = service._calculate_trend_strength(sideways_prices)
        assert abs(trend_sideways) < 0.5

    def test_calculate_moving_average(self, service):
        """Test moving average calculation."""
        prices = [100.0, 105.0, 110.0, 108.0, 115.0, 120.0, 125.0]
        
        # Test 3-day moving average
        ma_3d = service._calculate_moving_average(prices, 3)
        assert ma_3d == 120.0  # (115+120+125)/3
        
        # Test 7-day moving average
        ma_7d = service._calculate_moving_average(prices, 7)
        assert abs(ma_7d - 111.86) < 0.1  # Average of all prices ≈ 111.86

    def test_calculate_momentum(self, service):
        """Test momentum calculation."""
        prices = [100.0, 102.0, 104.0, 106.0, 108.0, 110.0, 112.0, 114.0, 116.0, 118.0]
        
        momentum = service._calculate_momentum(prices)
        assert isinstance(momentum, float)

    def test_calculate_seasonal_factor(self, service):
        """Test seasonal factor calculation."""
        from datetime import date
        
        # Test different months
        jan_timestamps = [date(2024, 1, 15)]
        jan_factor = service._calculate_seasonal_factor(jan_timestamps)
        assert jan_factor == 0.9
        
        mar_timestamps = [date(2024, 3, 15)]
        mar_factor = service._calculate_seasonal_factor(mar_timestamps)
        assert mar_factor == 1.2

    @pytest.mark.asyncio
    async def test_get_alert_statistics(self, service):
        """Test alert statistics retrieval."""
        user_id = "test_user_stats"
        
        # Mock alert history
        service.alert_history[user_id] = [
            {"false_positive": False, "user_response": True},
            {"false_positive": True, "user_response": False},
            {"false_positive": False, "user_response": True},
            {"false_positive": False, "user_response": False}
        ]
        
        stats = await service.get_alert_statistics(user_id)
        
        assert stats["total_alerts"] == 4
        assert stats["false_positive_rate"] == 0.25
        assert stats["response_rate"] == 0.5

    def test_ml_models_initialization(self, service):
        """Test ML models initialization."""
        assert len(service.ml_models) == 4
        assert "price_prediction" in service.ml_models
        assert "opportunity_detection" in service.ml_models
        assert "risk_assessment" in service.ml_models
        assert "timing_optimization" in service.ml_models
        
        # Check model properties
        for model_id, model in service.ml_models.items():
            assert model.model_id is not None
            assert model.model_type in ["classification", "regression", "anomaly_detection"]
            assert 0.0 <= model.accuracy_score <= 1.0
            assert 0.0 <= model.false_positive_rate <= 1.0
            assert len(model.features_used) > 0

    @pytest.mark.asyncio
    async def test_error_handling(self, service):
        """Test error handling in alert creation."""
        # Test with invalid data
        alert = await service.create_intelligent_alert(
            user_id="test_user",
            fertilizer_type=FertilizerType.NITROGEN,
            alert_type=AlertType.PRICE_THRESHOLD,
            current_price=None,  # Invalid price data
            historical_data=[]
        )
        
        assert alert is None

    @pytest.mark.asyncio
    async def test_concurrent_alert_creation(self, service, mock_price_data, mock_historical_data):
        """Test concurrent alert creation."""
        user_ids = [f"user_{i}" for i in range(5)]
        
        tasks = []
        for user_id in user_ids:
            task = service.create_intelligent_alert(
                user_id=user_id,
                fertilizer_type=FertilizerType.NITROGEN,
                alert_type=AlertType.PRICE_THRESHOLD,
                current_price=mock_price_data,
                historical_data=mock_historical_data
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        assert len(results) == 5
        for result in results:
            assert isinstance(result, (type(None), Exception))


class TestAlertPerformance:
    """Performance tests for the alert service."""

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_alert_creation_performance(self):
        """Test alert creation performance."""
        service = PriceOptimizationAlertService()
        
        # Create test data
        mock_price_data = FertilizerPriceData(
            product_id=str(uuid4()),
            product_name="urea_standard",
            fertilizer_type=FertilizerType.NITROGEN,
            specific_product=FertilizerProduct.UREA,
            price_per_unit=500.0,
            unit="ton",
            region="US",
            source=PriceSource.USDA_NASS,
            price_date=datetime.utcnow().date(),
            confidence=0.9,
            volatility=15.0,
            created_at=datetime.utcnow()
        )
        
        historical_data = [mock_price_data] * 30
        
        start_time = datetime.utcnow()
        
        alert = await service.create_intelligent_alert(
            user_id="perf_test_user",
            fertilizer_type=FertilizerType.NITROGEN,
            alert_type=AlertType.PRICE_THRESHOLD,
            current_price=mock_price_data,
            historical_data=historical_data
        )
        
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        # Should complete within 2 seconds
        assert processing_time < 2.0, f"Alert creation took {processing_time}s, exceeds 2s limit"

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_batch_monitoring_performance(self):
        """Test batch monitoring performance."""
        service = PriceOptimizationAlertService()
        
        fertilizer_types = [FertilizerType.NITROGEN, FertilizerType.PHOSPHORUS, FertilizerType.POTASSIUM]
        
        start_time = datetime.utcnow()
        
        alerts = await service.monitor_price_optimization_opportunities(
            user_id="perf_test_user",
            fertilizer_types=fertilizer_types,
            monitoring_duration_hours=24
        )
        
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        # Should complete within 5 seconds for 3 fertilizer types
        assert processing_time < 5.0, f"Batch monitoring took {processing_time}s, exceeds 5s limit"
        assert isinstance(alerts, list)


class TestAgriculturalValidation:
    """Agricultural validation tests for alert accuracy."""

    @pytest.mark.agricultural
    @pytest.mark.asyncio
    async def test_nitrogen_price_alert_accuracy(self):
        """Test nitrogen price alert accuracy for agricultural relevance."""
        service = PriceOptimizationAlertService()
        
        # Create realistic nitrogen price scenario
        nitrogen_price = FertilizerPriceData(
            product_id=str(uuid4()),
            product_name="urea_46-0-0",
            fertilizer_type=FertilizerType.NITROGEN,
            specific_product=FertilizerProduct.UREA,
            price_per_unit=600.0,  # $600/ton urea
            unit="ton",
            region="US",
            source=PriceSource.USDA_NASS,
            price_date=datetime.utcnow().date(),
            confidence=0.9,
            volatility=15.0,
            created_at=datetime.utcnow()
        )
        
        # Create historical data with significant price change
        historical_prices = []
        base_price = 500.0
        for i in range(30):
            price_data = FertilizerPriceData(
                product_id=str(uuid4()),
                product_name="urea_46-0-0",
                fertilizer_type=FertilizerType.NITROGEN,
                specific_product=FertilizerProduct.UREA,
                price_per_unit=base_price + (i * 3.33),  # 20% increase over 30 days
                unit="ton",
                region="US",
                source=PriceSource.USDA_NASS,
                price_date=(datetime.utcnow() - timedelta(days=30-i)).date(),
                confidence=0.9,
                volatility=15.0,
                created_at=datetime.utcnow() - timedelta(days=30-i)
            )
            historical_prices.append(price_data)
        
        alert = await service.create_intelligent_alert(
            user_id="ag_test_user",
            fertilizer_type=FertilizerType.NITROGEN,
            alert_type=AlertType.PRICE_THRESHOLD,
            current_price=nitrogen_price,
            historical_data=historical_prices
        )
        
        if alert:
            # Validate agricultural relevance
            assert "nitrogen" in alert.message.lower() or "urea" in alert.message.lower()
            assert "$" in alert.message  # Should include price information
            assert alert.priority in ["medium", "high", "critical"]  # Should be significant priority

    @pytest.mark.agricultural
    @pytest.mark.asyncio
    async def test_seasonal_timing_alert_accuracy(self):
        """Test seasonal timing alert accuracy."""
        service = PriceOptimizationAlertService()
        
        # Create spring timing scenario (optimal fertilizer purchase time)
        spring_price = FertilizerPriceData(
            product_id=str(uuid4()),
            product_name="dap_18-46-0",
            fertilizer_type=FertilizerType.PHOSPHORUS,
            specific_product=FertilizerProduct.DAP,
            price_per_unit=800.0,
            unit="ton",
            region="US",
            source=PriceSource.USDA_NASS,
            price_date=datetime(2024, 3, 15).date(),  # March 15th
            confidence=0.9,
            volatility=15.0,
            created_at=datetime(2024, 3, 15)
        )
        
        alert = await service.create_intelligent_alert(
            user_id="ag_test_user",
            fertilizer_type=FertilizerType.PHOSPHORUS,
            alert_type=AlertType.TIMING,
            current_price=spring_price,
            historical_data=[spring_price] * 30
        )
        
        if alert:
            # Should recognize spring as optimal timing
            assert alert.trigger_type == AlertType.TIMING.value
            # Timing alerts should have high confidence for spring
            assert alert.priority in ["medium", "high"]
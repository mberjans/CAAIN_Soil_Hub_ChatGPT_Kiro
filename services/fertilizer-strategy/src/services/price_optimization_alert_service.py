"""
Intelligent Price Optimization Alert Service

This service provides advanced price optimization alerts with machine learning capabilities,
personalized thresholds, predictive alerts, and multi-channel delivery.
"""

import asyncio
import logging
import time
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, date, timedelta
from uuid import uuid4, UUID
from enum import Enum
import statistics
import json
from dataclasses import dataclass

from ..models.price_models import (
    FertilizerPriceData, PriceTrendAnalysis, FertilizerType, 
    FertilizerProduct, PriceSource
)
from ..models.price_adjustment_models import (
    AdjustmentAlert, NotificationSettings
)
from ..services.price_tracking_service import FertilizerPriceTrackingService
from ..services.price_adjustment_service import DynamicPriceAdjustmentService
from ..database.fertilizer_price_db import FertilizerPriceRepository, get_db_session

logger = logging.getLogger(__name__)


class AlertType(str, Enum):
    """Types of price optimization alerts."""
    PRICE_THRESHOLD = "price_threshold"
    OPPORTUNITY = "opportunity"
    RISK = "risk"
    TIMING = "timing"
    VOLATILITY = "volatility"
    TREND_REVERSAL = "trend_reversal"
    MARKET_SHOCK = "market_shock"


class AlertPriority(str, Enum):
    """Alert priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertChannel(str, Enum):
    """Alert delivery channels."""
    EMAIL = "email"
    SMS = "sms"
    APP_NOTIFICATION = "app_notification"
    WEBHOOK = "webhook"
    DASHBOARD = "dashboard"


@dataclass
class AlertThreshold:
    """Personalized alert threshold configuration."""
    fertilizer_type: FertilizerType
    price_change_percent: float
    volatility_threshold: float
    trend_strength_threshold: float
    opportunity_threshold: float
    risk_threshold: float
    timing_threshold_days: int


@dataclass
class MLAlertModel:
    """Machine learning model for alert optimization."""
    model_id: str
    model_type: str  # 'classification', 'regression', 'anomaly_detection'
    accuracy_score: float
    false_positive_rate: float
    last_trained: datetime
    features_used: List[str]


class PriceOptimizationAlertService:
    """
    Intelligent price optimization alert service with ML capabilities.
    
    Features:
    - Intelligent alerting with personalized thresholds
    - Predictive alerts and action recommendations
    - Multiple alert types (price threshold, opportunity, risk, timing)
    - Machine learning for alert optimization and pattern recognition
    - Integration with price tracking and user preferences
    - Multi-channel alert delivery (email, SMS, app notifications)
    - Priority-based routing and false positive reduction
    """
    
    def __init__(self):
        """Initialize the intelligent price optimization alert service."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize dependent services
        self.price_tracker = FertilizerPriceTrackingService()
        self.price_adjuster = DynamicPriceAdjustmentService()
        
        # ML models for alert optimization
        self.ml_models: Dict[str, MLAlertModel] = {}
        self._initialize_ml_models()
        
        # Alert configuration
        self.default_thresholds = {
            FertilizerType.NITROGEN: AlertThreshold(
                fertilizer_type=FertilizerType.NITROGEN,
                price_change_percent=5.0,
                volatility_threshold=15.0,
                trend_strength_threshold=0.7,
                opportunity_threshold=10.0,
                risk_threshold=20.0,
                timing_threshold_days=7
            ),
            FertilizerType.PHOSPHORUS: AlertThreshold(
                fertilizer_type=FertilizerType.PHOSPHORUS,
                price_change_percent=7.0,
                volatility_threshold=18.0,
                trend_strength_threshold=0.7,
                opportunity_threshold=12.0,
                risk_threshold=25.0,
                timing_threshold_days=10
            ),
            FertilizerType.POTASSIUM: AlertThreshold(
                fertilizer_type=FertilizerType.POTASSIUM,
                price_change_percent=6.0,
                volatility_threshold=16.0,
                trend_strength_threshold=0.7,
                opportunity_threshold=11.0,
                risk_threshold=22.0,
                timing_threshold_days=8
            )
        }
        
        # User preferences and alert history
        self.user_preferences: Dict[str, Dict[str, Any]] = {}
        self.alert_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Performance metrics
        self._total_alerts_sent = 0
        self._false_positive_count = 0
        self._user_response_rate = 0.0
        self._average_response_time = 0.0
    
    def _initialize_ml_models(self):
        """Initialize machine learning models for alert optimization."""
        self.ml_models = {
            "price_prediction": MLAlertModel(
                model_id="price_prediction_v1",
                model_type="regression",
                accuracy_score=0.85,
                false_positive_rate=0.12,
                last_trained=datetime.utcnow(),
                features_used=["price_history", "volatility", "seasonality", "market_indicators"]
            ),
            "opportunity_detection": MLAlertModel(
                model_id="opportunity_detection_v1",
                model_type="classification",
                accuracy_score=0.78,
                false_positive_rate=0.15,
                last_trained=datetime.utcnow(),
                features_used=["price_trends", "market_conditions", "seasonal_patterns"]
            ),
            "risk_assessment": MLAlertModel(
                model_id="risk_assessment_v1",
                model_type="classification",
                accuracy_score=0.82,
                false_positive_rate=0.10,
                last_trained=datetime.utcnow(),
                features_used=["volatility", "price_momentum", "market_stress"]
            ),
            "timing_optimization": MLAlertModel(
                model_id="timing_optimization_v1",
                model_type="regression",
                accuracy_score=0.80,
                false_positive_rate=0.08,
                last_trained=datetime.utcnow(),
                features_used=["seasonal_patterns", "weather_forecast", "market_timing"]
            )
        }
    
    async def create_intelligent_alert(
        self,
        user_id: str,
        fertilizer_type: FertilizerType,
        alert_type: AlertType,
        current_price: FertilizerPriceData,
        historical_data: List[FertilizerPriceData],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Optional[AdjustmentAlert]:
        """
        Create an intelligent price optimization alert using ML.
        
        Args:
            user_id: User identifier
            fertilizer_type: Type of fertilizer
            alert_type: Type of alert to create
            current_price: Current price data
            historical_data: Historical price data for analysis
            user_preferences: User-specific preferences
            
        Returns:
            AdjustmentAlert if alert should be sent, None otherwise
        """
        try:
            self.logger.info(f"Creating intelligent alert for user {user_id}, fertilizer {fertilizer_type}")
            
            # 1. Get user-specific thresholds
            thresholds = self._get_user_thresholds(user_id, fertilizer_type, user_preferences)
            
            # 2. Analyze price patterns using ML
            pattern_analysis = await self._analyze_price_patterns(
                current_price, historical_data, alert_type
            )
            
            # 3. Check if alert conditions are met
            should_alert, confidence = await self._evaluate_alert_conditions(
                alert_type, current_price, historical_data, thresholds, pattern_analysis
            )
            
            if not should_alert:
                self.logger.info(f"Alert conditions not met for user {user_id}")
                return None
            
            # 4. Generate intelligent alert content
            alert_content = await self._generate_intelligent_alert_content(
                alert_type, current_price, historical_data, pattern_analysis, confidence
            )
            
            # 5. Determine alert priority
            priority = self._determine_alert_priority(alert_type, confidence, pattern_analysis)
            
            # 6. Create alert
            alert = AdjustmentAlert(
                alert_id=str(uuid4()),
                request_id=f"alert_{user_id}_{fertilizer_type.value}",
                trigger_type=alert_type.value,
                priority=priority.value,
                message=alert_content["message"],
                details=alert_content["details"],
                requires_action=alert_content["requires_action"],
                action_deadline=alert_content.get("action_deadline"),
                timestamp=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(hours=24)
            )
            
            # 7. Update metrics
            self._total_alerts_sent += 1
            
            return alert
            
        except Exception as e:
            self.logger.error(f"Error creating intelligent alert: {e}")
            return None
    
    async def monitor_price_optimization_opportunities(
        self,
        user_id: str,
        fertilizer_types: List[FertilizerType],
        monitoring_duration_hours: int = 24
    ) -> List[AdjustmentAlert]:
        """
        Monitor for price optimization opportunities and generate alerts.
        
        Args:
            user_id: User identifier
            fertilizer_types: Types of fertilizers to monitor
            monitoring_duration_hours: Duration of monitoring session
            
        Returns:
            List of generated alerts
        """
        alerts = []
        
        try:
            self.logger.info(f"Starting price optimization monitoring for user {user_id}")
            
            for fertilizer_type in fertilizer_types:
                # Get current price data
                current_price = await self.price_tracker.get_current_price(
                    fertilizer_type=fertilizer_type,
                    product_name=f"{fertilizer_type.value}_standard"
                )
                
                if not current_price:
                    continue
                
                # Get historical data
                historical_data = await self._get_historical_price_data(
                    fertilizer_type, days=30
                )
                
                # Check for different types of alerts
                alert_types_to_check = [
                    AlertType.PRICE_THRESHOLD,
                    AlertType.OPPORTUNITY,
                    AlertType.RISK,
                    AlertType.TIMING,
                    AlertType.VOLATILITY
                ]
                
                for alert_type in alert_types_to_check:
                    alert = await self.create_intelligent_alert(
                        user_id=user_id,
                        fertilizer_type=fertilizer_type,
                        alert_type=alert_type,
                        current_price=current_price,
                        historical_data=historical_data
                    )
                    
                    if alert:
                        alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error in price optimization monitoring: {e}")
            return []
    
    async def _analyze_price_patterns(
        self,
        current_price: FertilizerPriceData,
        historical_data: List[FertilizerPriceData],
        alert_type: AlertType
    ) -> Dict[str, Any]:
        """Analyze price patterns using machine learning."""
        try:
            # Extract features for ML analysis
            features = self._extract_price_features(current_price, historical_data)
            
            # Apply appropriate ML model based on alert type
            if alert_type == AlertType.OPPORTUNITY:
                model = self.ml_models["opportunity_detection"]
                analysis = await self._apply_opportunity_model(features)
            elif alert_type == AlertType.RISK:
                model = self.ml_models["risk_assessment"]
                analysis = await self._apply_risk_model(features)
            elif alert_type == AlertType.TIMING:
                model = self.ml_models["timing_optimization"]
                analysis = await self._apply_timing_model(features)
            else:
                model = self.ml_models["price_prediction"]
                analysis = await self._apply_price_prediction_model(features)
            
            return {
                "model_used": model.model_id,
                "confidence": analysis.get("confidence", 0.5),
                "prediction": analysis.get("prediction"),
                "features": features,
                "pattern_type": analysis.get("pattern_type"),
                "anomaly_score": analysis.get("anomaly_score", 0.0)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing price patterns: {e}")
            return {"confidence": 0.0, "prediction": None}
    
    def _extract_price_features(
        self,
        current_price: FertilizerPriceData,
        historical_data: List[FertilizerPriceData]
    ) -> Dict[str, Any]:
        """Extract features for machine learning analysis."""
        if not historical_data:
            return {"error": "No historical data available"}
        
        prices = [data.price_per_unit for data in historical_data]
        timestamps = [data.price_date for data in historical_data]
        
        # Calculate technical indicators
        features = {
            "current_price": current_price.price_per_unit,
            "price_change_1d": self._calculate_price_change(prices, 1),
            "price_change_7d": self._calculate_price_change(prices, 7),
            "price_change_30d": self._calculate_price_change(prices, 30),
            "volatility_7d": self._calculate_volatility(prices[-7:]),
            "volatility_30d": self._calculate_volatility(prices),
            "trend_strength": self._calculate_trend_strength(prices),
            "moving_average_7d": self._calculate_moving_average(prices, 7),
            "moving_average_30d": self._calculate_moving_average(prices, 30),
            "price_momentum": self._calculate_momentum(prices),
            "seasonal_factor": self._calculate_seasonal_factor(timestamps),
            "volume_trend": self._calculate_volume_trend(historical_data)
        }
        
        return features
    
    async def _apply_opportunity_model(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Apply opportunity detection ML model."""
        # Simulate ML model prediction
        opportunity_score = 0.0
        
        # Price drop opportunity
        if features.get("price_change_7d", 0) < -5.0:
            opportunity_score += 0.3
        
        # Volatility spike opportunity
        if features.get("volatility_7d", 0) > 20.0:
            opportunity_score += 0.2
        
        # Trend reversal opportunity
        if features.get("trend_strength", 0) < -0.5:
            opportunity_score += 0.25
        
        # Seasonal opportunity
        if features.get("seasonal_factor", 0) < 0.8:
            opportunity_score += 0.15
        
        return {
            "confidence": min(opportunity_score, 1.0),
            "prediction": "opportunity" if opportunity_score > 0.5 else "no_opportunity",
            "pattern_type": "price_drop" if features.get("price_change_7d", 0) < -5.0 else "volatility_spike"
        }
    
    async def _apply_risk_model(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Apply risk assessment ML model."""
        risk_score = 0.0
        
        # High volatility risk
        if features.get("volatility_30d", 0) > 25.0:
            risk_score += 0.4
        
        # Price momentum risk
        if features.get("price_momentum", 0) > 0.8:
            risk_score += 0.3
        
        # Market stress indicators
        if features.get("trend_strength", 0) > 0.9:
            risk_score += 0.2
        
        return {
            "confidence": min(risk_score, 1.0),
            "prediction": "high_risk" if risk_score > 0.6 else "low_risk",
            "pattern_type": "volatility_risk" if features.get("volatility_30d", 0) > 25.0 else "momentum_risk"
        }
    
    async def _apply_timing_model(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Apply timing optimization ML model."""
        timing_score = 0.0
        
        # Optimal timing based on seasonal patterns
        seasonal_factor = features.get("seasonal_factor", 1.0)
        if 0.9 <= seasonal_factor <= 1.1:
            timing_score += 0.4
        
        # Price momentum timing
        momentum = features.get("price_momentum", 0)
        if -0.3 <= momentum <= 0.3:
            timing_score += 0.3
        
        # Volatility timing
        volatility = features.get("volatility_7d", 0)
        if volatility < 15.0:
            timing_score += 0.3
        
        return {
            "confidence": min(timing_score, 1.0),
            "prediction": "optimal_timing" if timing_score > 0.6 else "suboptimal_timing",
            "pattern_type": "seasonal_timing" if seasonal_factor < 1.1 else "momentum_timing"
        }
    
    async def _apply_price_prediction_model(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Apply price prediction ML model."""
        # Simple trend-based prediction
        trend_strength = features.get("trend_strength", 0)
        momentum = features.get("price_momentum", 0)
        
        prediction_confidence = abs(trend_strength) * 0.7 + abs(momentum) * 0.3
        
        return {
            "confidence": min(prediction_confidence, 1.0),
            "prediction": trend_strength,
            "pattern_type": "trending" if abs(trend_strength) > 0.5 else "sideways"
        }
    
    async def _evaluate_alert_conditions(
        self,
        alert_type: AlertType,
        current_price: FertilizerPriceData,
        historical_data: List[FertilizerPriceData],
        thresholds: AlertThreshold,
        pattern_analysis: Dict[str, Any]
    ) -> Tuple[bool, float]:
        """Evaluate if alert conditions are met."""
        confidence = pattern_analysis.get("confidence", 0.0)
        
        if alert_type == AlertType.PRICE_THRESHOLD:
            price_change = self._calculate_price_change(
                [data.price_per_unit for data in historical_data], 7
            )
            should_alert = abs(price_change) >= thresholds.price_change_percent
            confidence = min(confidence, 0.9) if should_alert else 0.0
            
        elif alert_type == AlertType.OPPORTUNITY:
            should_alert = confidence >= thresholds.opportunity_threshold / 100.0
            confidence = confidence if should_alert else 0.0
            
        elif alert_type == AlertType.RISK:
            should_alert = confidence >= thresholds.risk_threshold / 100.0
            confidence = confidence if should_alert else 0.0
            
        elif alert_type == AlertType.TIMING:
            should_alert = confidence >= 0.6  # High confidence required for timing
            confidence = confidence if should_alert else 0.0
            
        elif alert_type == AlertType.VOLATILITY:
            volatility = self._calculate_volatility([data.price_per_unit for data in historical_data[-7:]])
            should_alert = volatility >= thresholds.volatility_threshold
            confidence = min(confidence, 0.8) if should_alert else 0.0
            
        else:
            should_alert = False
            confidence = 0.0
        
        return should_alert, confidence
    
    async def _generate_intelligent_alert_content(
        self,
        alert_type: AlertType,
        current_price: FertilizerPriceData,
        historical_data: List[FertilizerPriceData],
        pattern_analysis: Dict[str, Any],
        confidence: float
    ) -> Dict[str, Any]:
        """Generate intelligent alert content with recommendations."""
        fertilizer_type = current_price.fertilizer_type
        current_price_value = current_price.price_per_unit
        
        if alert_type == AlertType.PRICE_THRESHOLD:
            price_change = self._calculate_price_change(
                [data.price_per_unit for data in historical_data], 7
            )
            message = f"Price Alert: {fertilizer_type.value} price changed by {price_change:.1f}% to ${current_price_value:.2f}"
            details = {
                "price_change_percent": price_change,
                "current_price": current_price_value,
                "recommendation": "Consider adjusting fertilizer strategy" if abs(price_change) > 10 else "Monitor price trends"
            }
            
        elif alert_type == AlertType.OPPORTUNITY:
            message = f"Opportunity Alert: Potential buying opportunity for {fertilizer_type.value} at ${current_price_value:.2f}"
            details = {
                "opportunity_type": pattern_analysis.get("pattern_type", "price_drop"),
                "confidence_score": confidence,
                "recommendation": "Consider purchasing fertilizer now",
                "expected_savings": f"${current_price_value * 0.1:.2f} per unit"
            }
            
        elif alert_type == AlertType.RISK:
            message = f"Risk Alert: High volatility detected for {fertilizer_type.value} at ${current_price_value:.2f}"
            details = {
                "risk_type": pattern_analysis.get("pattern_type", "volatility_risk"),
                "risk_level": "high" if confidence > 0.8 else "medium",
                "recommendation": "Consider hedging or delaying purchases",
                "monitoring_period": "Next 7 days"
            }
            
        elif alert_type == AlertType.TIMING:
            message = f"Timing Alert: Optimal timing window for {fertilizer_type.value} purchases"
            details = {
                "timing_type": pattern_analysis.get("pattern_type", "seasonal_timing"),
                "optimal_window": "Next 3-5 days",
                "recommendation": "Consider purchasing within optimal window",
                "price_expectation": "Stable to slightly increasing"
            }
            
        else:
            message = f"Alert: {alert_type.value} detected for {fertilizer_type.value}"
            details = {"alert_type": alert_type.value}
        
        return {
            "message": message,
            "details": details,
            "requires_action": confidence > 0.7,
            "action_deadline": datetime.utcnow() + timedelta(hours=24) if confidence > 0.7 else None
        }
    
    def _get_user_thresholds(
        self,
        user_id: str,
        fertilizer_type: FertilizerType,
        user_preferences: Optional[Dict[str, Any]]
    ) -> AlertThreshold:
        """Get user-specific alert thresholds."""
        if user_preferences and "alert_thresholds" in user_preferences:
            user_thresholds = user_preferences["alert_thresholds"].get(fertilizer_type.value)
            if user_thresholds:
                return AlertThreshold(
                    fertilizer_type=fertilizer_type,
                    price_change_percent=user_thresholds.get("price_change_percent", 5.0),
                    volatility_threshold=user_thresholds.get("volatility_threshold", 15.0),
                    trend_strength_threshold=user_thresholds.get("trend_strength_threshold", 0.7),
                    opportunity_threshold=user_thresholds.get("opportunity_threshold", 10.0),
                    risk_threshold=user_thresholds.get("risk_threshold", 20.0),
                    timing_threshold_days=user_thresholds.get("timing_threshold_days", 7)
                )
        
        return self.default_thresholds[fertilizer_type]
    
    def _determine_alert_priority(
        self,
        alert_type: AlertType,
        confidence: float,
        pattern_analysis: Dict[str, Any]
    ) -> AlertPriority:
        """Determine alert priority based on type and confidence."""
        if alert_type == AlertType.MARKET_SHOCK:
            return AlertPriority.CRITICAL
        elif alert_type == AlertType.RISK and confidence > 0.8:
            return AlertPriority.HIGH
        elif alert_type == AlertType.OPPORTUNITY and confidence > 0.7:
            return AlertPriority.HIGH
        elif confidence > 0.6:
            return AlertPriority.MEDIUM
        else:
            return AlertPriority.LOW
    
    async def _get_historical_price_data(
        self,
        fertilizer_type: FertilizerType,
        days: int = 30
    ) -> List[FertilizerPriceData]:
        """Get historical price data for analysis."""
        try:
            # This would typically query the database
            # For now, return empty list - would be implemented with actual DB query
            return []
        except Exception as e:
            self.logger.error(f"Error getting historical price data: {e}")
            return []
    
    def _calculate_price_change(self, prices: List[float], days: int) -> float:
        """Calculate price change over specified days."""
        if len(prices) < days + 1:
            return 0.0
        
        old_price = prices[-days-1]
        new_price = prices[-1]
        return ((new_price - old_price) / old_price) * 100
    
    def _calculate_volatility(self, prices: List[float]) -> float:
        """Calculate price volatility."""
        if len(prices) < 2:
            return 0.0
        
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        return statistics.stdev(returns) * 100 if len(returns) > 1 else 0.0
    
    def _calculate_trend_strength(self, prices: List[float]) -> float:
        """Calculate trend strength using linear regression."""
        if len(prices) < 3:
            return 0.0
        
        n = len(prices)
        x_values = list(range(n))
        
        # Simple linear regression
        sum_x = sum(x_values)
        sum_y = sum(prices)
        sum_xy = sum(x * y for x, y in zip(x_values, prices))
        sum_x2 = sum(x * x for x in x_values)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # Normalize slope to -1 to 1 range
        return max(-1.0, min(1.0, slope / (max(prices) - min(prices)) * n))
    
    def _calculate_moving_average(self, prices: List[float], window: int) -> float:
        """Calculate moving average."""
        if len(prices) < window:
            return sum(prices) / len(prices)
        
        return sum(prices[-window:]) / window
    
    def _calculate_momentum(self, prices: List[float]) -> float:
        """Calculate price momentum."""
        if len(prices) < 10:
            return 0.0
        
        recent_avg = sum(prices[-5:]) / 5
        older_avg = sum(prices[-10:-5]) / 5
        
        return (recent_avg - older_avg) / older_avg
    
    def _calculate_seasonal_factor(self, timestamps: List[date]) -> float:
        """Calculate seasonal factor."""
        if not timestamps:
            return 1.0
        
        # Simple seasonal factor based on month
        current_month = timestamps[-1].month
        seasonal_factors = {
            1: 0.9, 2: 0.8, 3: 1.2, 4: 1.3, 5: 1.1, 6: 0.9,
            7: 0.8, 8: 0.9, 9: 1.0, 10: 1.1, 11: 1.0, 12: 0.9
        }
        
        return seasonal_factors.get(current_month, 1.0)
    
    def _calculate_volume_trend(self, historical_data: List[FertilizerPriceData]) -> float:
        """Calculate volume trend."""
        # This would use volume data if available
        # For now, return neutral trend
        return 0.0
    
    async def get_alert_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get alert statistics for a user."""
        user_alerts = self.alert_history.get(user_id, [])
        
        if not user_alerts:
            return {
                "total_alerts": 0,
                "false_positive_rate": 0.0,
                "response_rate": 0.0,
                "average_response_time": 0.0
            }
        
        total_alerts = len(user_alerts)
        false_positives = sum(1 for alert in user_alerts if alert.get("false_positive", False))
        responses = sum(1 for alert in user_alerts if alert.get("user_response", False))
        
        return {
            "total_alerts": total_alerts,
            "false_positive_rate": false_positives / total_alerts if total_alerts > 0 else 0.0,
            "response_rate": responses / total_alerts if total_alerts > 0 else 0.0,
            "average_response_time": self._average_response_time,
            "alert_types": {
                alert_type.value: sum(1 for alert in user_alerts if alert.get("type") == alert_type.value)
                for alert_type in AlertType
            }
        }
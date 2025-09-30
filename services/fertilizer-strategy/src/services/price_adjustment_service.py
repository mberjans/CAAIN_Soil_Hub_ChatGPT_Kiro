"""
Comprehensive dynamic price adjustment service for fertilizer strategy optimization.

This service provides real-time price monitoring, automatic strategy adjustments,
threshold-based alerts, and economic impact assessment for fertilizer strategies.
"""

import asyncio
import logging
import time
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, date, timedelta
from uuid import uuid4, UUID
from enum import Enum
import statistics

from ..models.price_models import (
    FertilizerPriceData, PriceTrendAnalysis, FertilizerType, 
    FertilizerProduct, PriceSource
)
from ..models.price_adjustment_models import (
    PriceAdjustmentRequest, PriceAdjustmentResponse, AdjustmentStrategy,
    PriceThreshold, AdjustmentAlert, EconomicImpactAnalysis,
    StrategyModification, ApprovalWorkflow, NotificationSettings
)
from ..services.price_tracking_service import FertilizerPriceTrackingService
from ..services.commodity_price_service import CommodityPriceService
from ..services.roi_optimizer import FertilizerROIOptimizer
from ..services.yield_goal_optimization_service import YieldGoalOptimizationService
from ..database.fertilizer_price_db import FertilizerPriceRepository, get_db_session

logger = logging.getLogger(__name__)


class AdjustmentTrigger(str, Enum):
    """Types of price adjustment triggers."""
    PRICE_INCREASE = "price_increase"
    PRICE_DECREASE = "price_decrease"
    VOLATILITY_SPIKE = "volatility_spike"
    TREND_REVERSAL = "trend_reversal"
    THRESHOLD_BREACH = "threshold_breach"
    MARKET_SHOCK = "market_shock"


class AdjustmentPriority(str, Enum):
    """Priority levels for adjustments."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DynamicPriceAdjustmentService:
    """
    Comprehensive dynamic price adjustment service.
    
    Features:
    - Real-time price monitoring and analysis
    - Automatic strategy adjustments based on price changes
    - Threshold-based alerts and notifications
    - Economic impact assessment and optimization
    - Automated approval workflows
    - Integration with existing optimization services
    """
    
    def __init__(self):
        """Initialize the dynamic price adjustment service."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize dependent services
        self.price_tracker = FertilizerPriceTrackingService()
        self.commodity_service = CommodityPriceService()
        self.roi_optimizer = FertilizerROIOptimizer()
        self.yield_optimizer = YieldGoalOptimizationService()
        
        # Configuration parameters
        self.default_thresholds = {
            FertilizerType.NITROGEN: {
                "price_change_percent": 5.0,  # 5% price change triggers adjustment
                "volatility_threshold": 15.0,  # 15% volatility threshold
                "trend_strength_threshold": 0.7  # Strong trend threshold
            },
            FertilizerType.PHOSPHORUS: {
                "price_change_percent": 7.0,
                "volatility_threshold": 18.0,
                "trend_strength_threshold": 0.7
            },
            FertilizerType.POTASSIUM: {
                "price_change_percent": 6.0,
                "volatility_threshold": 16.0,
                "trend_strength_threshold": 0.7
            }
        }
        
        # Active monitoring sessions
        self._monitoring_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Alert history for deduplication
        self._alert_history: Dict[str, datetime] = {}
        
        # Performance metrics
        self._adjustment_count = 0
        self._successful_adjustments = 0
        self._average_processing_time = 0.0
    
    async def start_price_monitoring(
        self,
        request: PriceAdjustmentRequest
    ) -> PriceAdjustmentResponse:
        """
        Start comprehensive price monitoring for dynamic adjustments.
        
        Args:
            request: Price adjustment request with monitoring parameters
            
        Returns:
            PriceAdjustmentResponse with monitoring status and initial analysis
        """
        start_time = time.time()
        request_id = str(uuid4())
        
        try:
            self.logger.info(f"Starting price monitoring: {request_id}")
            
            # Validate request
            await self._validate_adjustment_request(request)
            
            # Initialize monitoring session
            session_data = {
                "request_id": request_id,
                "request": request,
                "start_time": datetime.utcnow(),
                "last_check": datetime.utcnow(),
                "adjustments_made": 0,
                "alerts_sent": 0,
                "status": "active"
            }
            
            self._monitoring_sessions[request_id] = session_data
            
            # Perform initial price analysis
            initial_analysis = await self._perform_initial_price_analysis(request)
            
            # Set up monitoring thresholds
            thresholds = await self._setup_monitoring_thresholds(request, initial_analysis)
            
            # Start background monitoring task
            monitoring_task = asyncio.create_task(
                self._background_price_monitoring(request_id, request, thresholds)
            )
            
            session_data["monitoring_task"] = monitoring_task
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000
            
            response = PriceAdjustmentResponse(
                request_id=request_id,
                success=True,
                monitoring_active=True,
                initial_analysis=initial_analysis,
                thresholds=thresholds,
                processing_time_ms=processing_time,
                message="Price monitoring started successfully"
            )
            
            self.logger.info(f"Price monitoring started: {request_id}")
            return response
            
        except Exception as e:
            self.logger.error(f"Error starting price monitoring: {e}")
            return PriceAdjustmentResponse(
                request_id=request_id,
                success=False,
                monitoring_active=False,
                processing_time_ms=(time.time() - start_time) * 1000,
                error_message=str(e)
            )
    
    async def check_price_adjustments(
        self,
        request_id: str,
        force_check: bool = False
    ) -> PriceAdjustmentResponse:
        """
        Check for price adjustments and trigger strategy modifications.
        
        Args:
            request_id: Monitoring session ID
            force_check: Force check even if recent check was performed
            
        Returns:
            PriceAdjustmentResponse with adjustment results
        """
        start_time = time.time()
        
        try:
            # Get monitoring session
            if request_id not in self._monitoring_sessions:
                raise ValueError(f"Monitoring session not found: {request_id}")
            
            session = self._monitoring_sessions[request_id]
            request = session["request"]
            
            # Check if recent check was performed (unless forced)
            if not force_check:
                last_check = session["last_check"]
                if (datetime.utcnow() - last_check).seconds < 300:  # 5 minutes
                    return PriceAdjustmentResponse(
                        request_id=request_id,
                        success=True,
                        monitoring_active=True,
                        message="Recent check already performed"
                    )
            
            # Update last check time
            session["last_check"] = datetime.utcnow()
            
            # Perform price analysis
            current_analysis = await self._analyze_current_prices(request)
            
            # Check for adjustment triggers
            triggers = await self._check_adjustment_triggers(request, current_analysis)
            
            # Perform adjustments if triggers found
            adjustments_made = []
            if triggers:
                adjustments_made = await self._perform_price_adjustments(
                    request, current_analysis, triggers
                )
                session["adjustments_made"] += len(adjustments_made)
            
            # Send alerts if needed
            alerts_sent = await self._send_adjustment_alerts(request, triggers, adjustments_made)
            session["alerts_sent"] += len(alerts_sent)
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000
            
            response = PriceAdjustmentResponse(
                request_id=request_id,
                success=True,
                monitoring_active=True,
                current_analysis=current_analysis,
                triggers_detected=triggers,
                adjustments_made=adjustments_made,
                alerts_sent=alerts_sent,
                processing_time_ms=processing_time
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error checking price adjustments: {e}")
            return PriceAdjustmentResponse(
                request_id=request_id,
                success=False,
                processing_time_ms=(time.time() - start_time) * 1000,
                error_message=str(e)
            )
    
    async def stop_price_monitoring(self, request_id: str) -> PriceAdjustmentResponse:
        """
        Stop price monitoring session.
        
        Args:
            request_id: Monitoring session ID
            
        Returns:
            PriceAdjustmentResponse with stop status
        """
        try:
            if request_id not in self._monitoring_sessions:
                raise ValueError(f"Monitoring session not found: {request_id}")
            
            session = self._monitoring_sessions[request_id]
            
            # Cancel monitoring task
            if "monitoring_task" in session:
                session["monitoring_task"].cancel()
            
            # Update session status
            session["status"] = "stopped"
            session["end_time"] = datetime.utcnow()
            
            # Generate final report
            final_report = await self._generate_monitoring_report(session)
            
            # Remove from active sessions
            del self._monitoring_sessions[request_id]
            
            return PriceAdjustmentResponse(
                request_id=request_id,
                success=True,
                monitoring_active=False,
                final_report=final_report,
                message="Price monitoring stopped successfully"
            )
            
        except Exception as e:
            self.logger.error(f"Error stopping price monitoring: {e}")
            return PriceAdjustmentResponse(
                request_id=request_id,
                success=False,
                error_message=str(e)
            )
    
    async def get_monitoring_status(self, request_id: str) -> Dict[str, Any]:
        """
        Get current monitoring session status.
        
        Args:
            request_id: Monitoring session ID
            
        Returns:
            Dictionary with monitoring status information
        """
        if request_id not in self._monitoring_sessions:
            raise ValueError(f"Monitoring session not found: {request_id}")
        
        session = self._monitoring_sessions[request_id]
        
        return {
            "request_id": request_id,
            "status": session["status"],
            "start_time": session["start_time"],
            "last_check": session["last_check"],
            "adjustments_made": session["adjustments_made"],
            "alerts_sent": session["alerts_sent"],
            "uptime_seconds": (datetime.utcnow() - session["start_time"]).total_seconds()
        }
    
    async def _validate_adjustment_request(self, request: PriceAdjustmentRequest):
        """Validate price adjustment request."""
        if not request.fertilizer_types:
            raise ValueError("At least one fertilizer type must be specified")
        
        if not request.fields:
            raise ValueError("At least one field must be specified")
        
        if request.price_change_threshold <= 0:
            raise ValueError("Price change threshold must be positive")
        
        if request.monitoring_duration_hours <= 0:
            raise ValueError("Monitoring duration must be positive")
    
    async def _perform_initial_price_analysis(
        self,
        request: PriceAdjustmentRequest
    ) -> Dict[str, Any]:
        """Perform initial price analysis for baseline."""
        try:
            analysis = {
                "baseline_prices": {},
                "price_trends": {},
                "market_conditions": {},
                "analysis_timestamp": datetime.utcnow()
            }
            
            # Get current prices for all fertilizer types
            for fertilizer_type in request.fertilizer_types:
                products = self._get_products_by_type(fertilizer_type)
                
                for product in products:
                    price_data = await self.price_tracker.get_current_price(
                        product, request.region
                    )
                    
                    if price_data:
                        analysis["baseline_prices"][product.value] = price_data
                        
                        # Get trend analysis
                        trend = await self.price_tracker.get_price_trend(
                            product, request.region
                        )
                        if trend:
                            analysis["price_trends"][product.value] = trend
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error performing initial price analysis: {e}")
            raise
    
    async def _setup_monitoring_thresholds(
        self,
        request: PriceAdjustmentRequest,
        initial_analysis: Dict[str, Any]
    ) -> List[PriceThreshold]:
        """Set up monitoring thresholds based on request and analysis."""
        thresholds = []
        
        for fertilizer_type in request.fertilizer_types:
            # Get default thresholds for this fertilizer type
            default_thresholds = self.default_thresholds.get(
                fertilizer_type, self.default_thresholds[FertilizerType.NITROGEN]
            )
            
            # Create threshold based on request parameters
            threshold = PriceThreshold(
                fertilizer_type=fertilizer_type,
                price_change_percent=request.price_change_threshold,
                volatility_threshold=default_thresholds["volatility_threshold"],
                trend_strength_threshold=default_thresholds["trend_strength_threshold"],
                check_interval_minutes=request.check_interval_minutes,
                alert_enabled=True,
                auto_adjust_enabled=request.auto_adjust_enabled
            )
            
            thresholds.append(threshold)
        
        return thresholds
    
    async def _background_price_monitoring(
        self,
        request_id: str,
        request: PriceAdjustmentRequest,
        thresholds: List[PriceThreshold]
    ):
        """Background task for continuous price monitoring."""
        try:
            self.logger.info(f"Starting background monitoring for {request_id}")
            
            check_interval = min(
                threshold.check_interval_minutes for threshold in thresholds
            ) * 60  # Convert to seconds
            
            while request_id in self._monitoring_sessions:
                try:
                    # Check for adjustments
                    await self.check_price_adjustments(request_id)
                    
                    # Wait for next check
                    await asyncio.sleep(check_interval)
                    
                except asyncio.CancelledError:
                    self.logger.info(f"Background monitoring cancelled for {request_id}")
                    break
                except Exception as e:
                    self.logger.error(f"Error in background monitoring: {e}")
                    await asyncio.sleep(check_interval)  # Continue monitoring
            
        except Exception as e:
            self.logger.error(f"Background monitoring failed for {request_id}: {e}")
    
    async def _analyze_current_prices(
        self,
        request: PriceAdjustmentRequest
    ) -> Dict[str, Any]:
        """Analyze current prices and trends."""
        try:
            analysis = {
                "current_prices": {},
                "price_changes": {},
                "trend_analysis": {},
                "volatility_metrics": {},
                "analysis_timestamp": datetime.utcnow()
            }
            
            # Get current prices and compare with baseline
            for fertilizer_type in request.fertilizer_types:
                products = self._get_products_by_type(fertilizer_type)
                
                for product in products:
                    # Get current price
                    current_price = await self.price_tracker.get_current_price(
                        product, request.region
                    )
                    
                    if current_price:
                        analysis["current_prices"][product.value] = current_price
                        
                        # Calculate price change if baseline exists
                        if hasattr(request, 'baseline_prices') and product.value in request.baseline_prices:
                            baseline_price = request.baseline_prices[product.value]
                            price_change = (
                                (current_price.price_per_unit - baseline_price.price_per_unit) /
                                baseline_price.price_per_unit * 100
                            )
                            analysis["price_changes"][product.value] = price_change
                        
                        # Get trend analysis
                        trend = await self.price_tracker.get_price_trend(
                            product, request.region
                        )
                        if trend:
                            analysis["trend_analysis"][product.value] = trend
                            
                            # Calculate volatility metrics
                            volatility = self._calculate_volatility_metrics(trend)
                            analysis["volatility_metrics"][product.value] = volatility
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing current prices: {e}")
            raise
    
    async def _check_adjustment_triggers(
        self,
        request: PriceAdjustmentRequest,
        current_analysis: Dict[str, Any]
    ) -> List[AdjustmentTrigger]:
        """Check for price adjustment triggers."""
        triggers = []
        
        try:
            # Check price change triggers
            for product, price_change in current_analysis.get("price_changes", {}).items():
                if abs(price_change) >= request.price_change_threshold:
                    if price_change > 0:
                        triggers.append(AdjustmentTrigger.PRICE_INCREASE)
                    else:
                        triggers.append(AdjustmentTrigger.PRICE_DECREASE)
            
            # Check volatility triggers
            for product, volatility in current_analysis.get("volatility_metrics", {}).items():
                if volatility.get("current_volatility", 0) > 20.0:  # 20% volatility threshold
                    triggers.append(AdjustmentTrigger.VOLATILITY_SPIKE)
            
            # Check trend reversal triggers
            for product, trend in current_analysis.get("trend_analysis", {}).items():
                if trend.trend_strength == "strong" and trend.trend_direction in ["up", "down"]:
                    triggers.append(AdjustmentTrigger.TREND_REVERSAL)
            
            return list(set(triggers))  # Remove duplicates
            
        except Exception as e:
            self.logger.error(f"Error checking adjustment triggers: {e}")
            return []
    
    async def _perform_price_adjustments(
        self,
        request: PriceAdjustmentRequest,
        current_analysis: Dict[str, Any],
        triggers: List[AdjustmentTrigger]
    ) -> List[StrategyModification]:
        """Perform strategy adjustments based on price changes."""
        modifications = []
        
        try:
            for trigger in triggers:
                if trigger == AdjustmentTrigger.PRICE_INCREASE:
                    modification = await self._adjust_for_price_increase(
                        request, current_analysis
                    )
                elif trigger == AdjustmentTrigger.PRICE_DECREASE:
                    modification = await self._adjust_for_price_decrease(
                        request, current_analysis
                    )
                elif trigger == AdjustmentTrigger.VOLATILITY_SPIKE:
                    modification = await self._adjust_for_volatility(
                        request, current_analysis
                    )
                else:
                    modification = await self._adjust_for_trend_change(
                        request, current_analysis, trigger
                    )
                
                if modification:
                    modifications.append(modification)
            
            return modifications
            
        except Exception as e:
            self.logger.error(f"Error performing price adjustments: {e}")
            return []
    
    async def _adjust_for_price_increase(
        self,
        request: PriceAdjustmentRequest,
        current_analysis: Dict[str, Any]
    ) -> Optional[StrategyModification]:
        """Adjust strategy for price increases."""
        try:
            # Analyze economic impact of price increases
            impact_analysis = await self._calculate_economic_impact(
                request, current_analysis, "price_increase"
            )
            
            # Determine adjustment strategy
            if impact_analysis.roi_impact_percent < -10:  # Significant ROI impact
                # Recommend reducing fertilizer rates or switching products
                modification = StrategyModification(
                    modification_type="rate_reduction",
                    fertilizer_type=request.fertilizer_types[0],  # Primary type
                    adjustment_percent=-15.0,  # 15% reduction
                    reason="Price increase significantly impacts ROI",
                    economic_impact=impact_analysis,
                    requires_approval=True
                )
            elif impact_analysis.roi_impact_percent < -5:  # Moderate ROI impact
                # Recommend minor adjustments
                modification = StrategyModification(
                    modification_type="rate_adjustment",
                    fertilizer_type=request.fertilizer_types[0],
                    adjustment_percent=-8.0,  # 8% reduction
                    reason="Price increase moderately impacts ROI",
                    economic_impact=impact_analysis,
                    requires_approval=False
                )
            else:
                # No significant impact, continue monitoring
                return None
            
            return modification
            
        except Exception as e:
            self.logger.error(f"Error adjusting for price increase: {e}")
            return None
    
    async def _adjust_for_price_decrease(
        self,
        request: PriceAdjustmentRequest,
        current_analysis: Dict[str, Any]
    ) -> Optional[StrategyModification]:
        """Adjust strategy for price decreases."""
        try:
            # Analyze economic impact of price decreases
            impact_analysis = await self._calculate_economic_impact(
                request, current_analysis, "price_decrease"
            )
            
            # Determine adjustment strategy
            if impact_analysis.roi_impact_percent > 10:  # Significant ROI improvement
                # Recommend increasing fertilizer rates
                modification = StrategyModification(
                    modification_type="rate_increase",
                    fertilizer_type=request.fertilizer_types[0],
                    adjustment_percent=12.0,  # 12% increase
                    reason="Price decrease significantly improves ROI",
                    economic_impact=impact_analysis,
                    requires_approval=True
                )
            elif impact_analysis.roi_impact_percent > 5:  # Moderate ROI improvement
                # Recommend minor increases
                modification = StrategyModification(
                    modification_type="rate_adjustment",
                    fertilizer_type=request.fertilizer_types[0],
                    adjustment_percent=6.0,  # 6% increase
                    reason="Price decrease moderately improves ROI",
                    economic_impact=impact_analysis,
                    requires_approval=False
                )
            else:
                # No significant impact, continue monitoring
                return None
            
            return modification
            
        except Exception as e:
            self.logger.error(f"Error adjusting for price decrease: {e}")
            return None
    
    async def _adjust_for_volatility(
        self,
        request: PriceAdjustmentRequest,
        current_analysis: Dict[str, Any]
    ) -> Optional[StrategyModification]:
        """Adjust strategy for high volatility."""
        try:
            # Recommend conservative approach during high volatility
            modification = StrategyModification(
                modification_type="conservative_adjustment",
                fertilizer_type=request.fertilizer_types[0],
                adjustment_percent=-5.0,  # 5% reduction for safety
                reason="High market volatility requires conservative approach",
                economic_impact=None,  # Will be calculated
                requires_approval=True
            )
            
            return modification
            
        except Exception as e:
            self.logger.error(f"Error adjusting for volatility: {e}")
            return None
    
    async def _adjust_for_trend_change(
        self,
        request: PriceAdjustmentRequest,
        current_analysis: Dict[str, Any],
        trigger: AdjustmentTrigger
    ) -> Optional[StrategyModification]:
        """Adjust strategy for trend changes."""
        try:
            # Analyze trend and recommend appropriate action
            trend_analysis = current_analysis.get("trend_analysis", {})
            
            if not trend_analysis:
                return None
            
            # Get the strongest trend
            strongest_trend = max(
                trend_analysis.values(),
                key=lambda t: abs(t.trend_7d_percent or 0)
            )
            
            if strongest_trend.trend_direction == "up":
                # Upward trend - consider increasing rates
                modification = StrategyModification(
                    modification_type="trend_adjustment",
                    fertilizer_type=request.fertilizer_types[0],
                    adjustment_percent=8.0,
                    reason=f"Strong upward trend detected: {strongest_trend.trend_7d_percent:.1f}%",
                    economic_impact=None,
                    requires_approval=True
                )
            elif strongest_trend.trend_direction == "down":
                # Downward trend - consider decreasing rates
                modification = StrategyModification(
                    modification_type="trend_adjustment",
                    fertilizer_type=request.fertilizer_types[0],
                    adjustment_percent=-8.0,
                    reason=f"Strong downward trend detected: {strongest_trend.trend_7d_percent:.1f}%",
                    economic_impact=None,
                    requires_approval=True
                )
            else:
                return None
            
            return modification
            
        except Exception as e:
            self.logger.error(f"Error adjusting for trend change: {e}")
            return None
    
    async def _calculate_economic_impact(
        self,
        request: PriceAdjustmentRequest,
        current_analysis: Dict[str, Any],
        change_type: str
    ) -> EconomicImpactAnalysis:
        """Calculate economic impact of price changes."""
        try:
            # This would integrate with ROI optimizer and yield optimizer
            # For now, return a basic analysis
            
            total_cost_impact = 0.0
            roi_impact_percent = 0.0
            
            # Calculate cost impact based on price changes
            for product, price_change in current_analysis.get("price_changes", {}).items():
                # Estimate cost impact based on typical usage
                estimated_usage = 100.0  # lbs per acre (example)
                cost_per_acre = estimated_usage * (price_change / 100) * 0.5  # Simplified calculation
                total_cost_impact += cost_per_acre
            
            # Calculate ROI impact
            if total_cost_impact != 0:
                roi_impact_percent = (total_cost_impact / 1000) * 100  # Simplified ROI calculation
            
            return EconomicImpactAnalysis(
                cost_impact_per_acre=total_cost_impact,
                roi_impact_percent=roi_impact_percent,
                yield_impact_percent=0.0,  # Would be calculated by yield optimizer
                break_even_impact_percent=roi_impact_percent,
                recommendation_confidence=0.8,
                analysis_timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating economic impact: {e}")
            # Return default analysis
            return EconomicImpactAnalysis(
                cost_impact_per_acre=0.0,
                roi_impact_percent=0.0,
                yield_impact_percent=0.0,
                break_even_impact_percent=0.0,
                recommendation_confidence=0.0,
                analysis_timestamp=datetime.utcnow()
            )
    
    async def _send_adjustment_alerts(
        self,
        request: PriceAdjustmentRequest,
        triggers: List[AdjustmentTrigger],
        adjustments: List[StrategyModification]
    ) -> List[AdjustmentAlert]:
        """Send alerts for price adjustments."""
        alerts = []
        
        try:
            for trigger in triggers:
                # Check if we've already sent an alert for this trigger recently
                alert_key = f"{request.request_id}_{trigger.value}"
                if alert_key in self._alert_history:
                    last_alert = self._alert_history[alert_key]
                    if (datetime.utcnow() - last_alert).seconds < 3600:  # 1 hour cooldown
                        continue
                
                # Create alert
                alert = AdjustmentAlert(
                    alert_id=str(uuid4()),
                    request_id=request.request_id,
                    trigger_type=trigger,
                    priority=self._determine_alert_priority(trigger),
                    message=self._generate_alert_message(trigger, adjustments),
                    timestamp=datetime.utcnow(),
                    requires_action=True
                )
                
                alerts.append(alert)
                self._alert_history[alert_key] = datetime.utcnow()
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error sending adjustment alerts: {e}")
            return []
    
    def _determine_alert_priority(self, trigger: AdjustmentTrigger) -> AdjustmentPriority:
        """Determine alert priority based on trigger type."""
        priority_mapping = {
            AdjustmentTrigger.MARKET_SHOCK: AdjustmentPriority.CRITICAL,
            AdjustmentTrigger.VOLATILITY_SPIKE: AdjustmentPriority.HIGH,
            AdjustmentTrigger.PRICE_INCREASE: AdjustmentPriority.MEDIUM,
            AdjustmentTrigger.PRICE_DECREASE: AdjustmentPriority.MEDIUM,
            AdjustmentTrigger.TREND_REVERSAL: AdjustmentPriority.HIGH,
            AdjustmentTrigger.THRESHOLD_BREACH: AdjustmentPriority.MEDIUM
        }
        
        return priority_mapping.get(trigger, AdjustmentPriority.LOW)
    
    def _generate_alert_message(
        self,
        trigger: AdjustmentTrigger,
        adjustments: List[StrategyModification]
    ) -> str:
        """Generate alert message based on trigger and adjustments."""
        messages = {
            AdjustmentTrigger.PRICE_INCREASE: "Significant fertilizer price increase detected. Consider reducing application rates.",
            AdjustmentTrigger.PRICE_DECREASE: "Fertilizer price decrease detected. Opportunity to optimize application rates.",
            AdjustmentTrigger.VOLATILITY_SPIKE: "High market volatility detected. Recommend conservative approach.",
            AdjustmentTrigger.TREND_REVERSAL: "Strong price trend reversal detected. Strategy adjustment recommended.",
            AdjustmentTrigger.THRESHOLD_BREACH: "Price threshold breached. Automatic adjustment triggered.",
            AdjustmentTrigger.MARKET_SHOCK: "Market shock detected. Immediate strategy review required."
        }
        
        base_message = messages.get(trigger, "Price adjustment trigger detected.")
        
        if adjustments:
            adjustment_summary = f" {len(adjustments)} adjustment(s) recommended."
            return base_message + adjustment_summary
        
        return base_message
    
    def _calculate_volatility_metrics(self, trend: PriceTrendAnalysis) -> Dict[str, float]:
        """Calculate volatility metrics from trend analysis."""
        return {
            "current_volatility": trend.volatility_7d or 0.0,
            "volatility_30d": trend.volatility_30d or 0.0,
            "volatility_90d": trend.volatility_90d or 0.0,
            "volatility_trend": "increasing" if (trend.volatility_7d or 0) > (trend.volatility_30d or 0) else "decreasing"
        }
    
    def _get_products_by_type(self, fertilizer_type: FertilizerType) -> List[FertilizerProduct]:
        """Get products by fertilizer type."""
        type_mapping = {
            FertilizerType.NITROGEN: [
                FertilizerProduct.UREA,
                FertilizerProduct.ANHYDROUS_AMMONIA,
                FertilizerProduct.AMMONIUM_NITRATE,
                FertilizerProduct.UAN
            ],
            FertilizerType.PHOSPHORUS: [
                FertilizerProduct.DAP,
                FertilizerProduct.MAP,
                FertilizerProduct.TRIPLE_SUPERPHOSPHATE
            ],
            FertilizerType.POTASSIUM: [
                FertilizerProduct.MURIATE_OF_POTASH,
                FertilizerProduct.POTASSIUM_SULFATE
            ]
        }
        
        return type_mapping.get(fertilizer_type, [])
    
    async def _generate_monitoring_report(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final monitoring report."""
        return {
            "session_summary": {
                "request_id": session["request_id"],
                "start_time": session["start_time"],
                "end_time": session.get("end_time", datetime.utcnow()),
                "duration_hours": (session.get("end_time", datetime.utcnow()) - session["start_time"]).total_seconds() / 3600,
                "adjustments_made": session["adjustments_made"],
                "alerts_sent": session["alerts_sent"]
            },
            "performance_metrics": {
                "average_processing_time_ms": self._average_processing_time,
                "success_rate": (self._successful_adjustments / max(self._adjustment_count, 1)) * 100
            }
        }
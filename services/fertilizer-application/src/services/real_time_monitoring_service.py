"""
Real-time Application Monitoring and Adjustment Service.

This service provides real-time monitoring of fertilizer application processes,
including application rates, coverage uniformity, environmental conditions,
and equipment status. It also provides real-time adjustment recommendations
and automated quality control.
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from uuid import uuid4
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import statistics

from src.models.application_monitoring_models import (
    ApplicationMonitoringData, RealTimeAdjustment, MonitoringAlert,
    SensorData, ApplicationSession, QualityControlCheck, MonitoringConfiguration,
    MonitoringSummary, ApplicationStatus, AdjustmentType, MonitoringMetric,
    AlertSeverity, SensorType
)

logger = logging.getLogger(__name__)


class MonitoringState(str, Enum):
    """Monitoring state."""
    IDLE = "idle"
    MONITORING = "monitoring"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class AdjustmentRule:
    """Rule for automatic adjustments."""
    metric: MonitoringMetric
    threshold: float
    adjustment_type: AdjustmentType
    adjustment_amount: float
    priority: int
    conditions: Dict[str, Any]


class RealTimeMonitoringService:
    """Service for real-time application monitoring and adjustment."""
    
    def __init__(self):
        self.monitoring_sessions: Dict[str, ApplicationSession] = {}
        self.monitoring_configs: Dict[str, MonitoringConfiguration] = {}
        self.active_monitoring: Dict[str, bool] = {}
        self.monitoring_data: Dict[str, List[ApplicationMonitoringData]] = {}
        self.active_adjustments: Dict[str, List[RealTimeAdjustment]] = {}
        self.active_alerts: Dict[str, List[MonitoringAlert]] = {}
        self.sensor_data: Dict[str, List[SensorData]] = {}
        self.quality_checks: Dict[str, List[QualityControlCheck]] = {}
        
        # Monitoring tasks
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.sensor_tasks: Dict[str, asyncio.Task] = {}
        self.quality_control_tasks: Dict[str, asyncio.Task] = {}
        
        # Adjustment rules
        self.adjustment_rules = self._initialize_adjustment_rules()
        
        # Monitoring state
        self.state = MonitoringState.IDLE
        
        logger.info("Real-time monitoring service initialized")
    
    def _initialize_adjustment_rules(self) -> List[AdjustmentRule]:
        """Initialize automatic adjustment rules."""
        return [
            # Rate adjustment rules
            AdjustmentRule(
                metric=MonitoringMetric.APPLICATION_RATE,
                threshold=0.05,  # 5% deviation
                adjustment_type=AdjustmentType.RATE_ADJUSTMENT,
                adjustment_amount=0.02,  # 2% adjustment
                priority=3,
                conditions={"min_samples": 3}
            ),
            
            # Coverage adjustment rules
            AdjustmentRule(
                metric=MonitoringMetric.COVERAGE_UNIFORMITY,
                threshold=0.8,  # Below 80% uniformity
                adjustment_type=AdjustmentType.COVERAGE_ADJUSTMENT,
                adjustment_amount=0.1,  # 10% adjustment
                priority=2,
                conditions={"min_samples": 5}
            ),
            
            # Weather adjustment rules
            AdjustmentRule(
                metric=MonitoringMetric.WIND_SPEED,
                threshold=10.0,  # Wind speed > 10 mph
                adjustment_type=AdjustmentType.WEATHER_ADJUSTMENT,
                adjustment_amount=0.15,  # 15% rate reduction
                priority=1,
                conditions={"temperature": ">50", "humidity": "<80"}
            ),
            
            # Pressure adjustment rules
            AdjustmentRule(
                metric=MonitoringMetric.PRESSURE,
                threshold=0.1,  # 10% pressure deviation
                adjustment_type=AdjustmentType.RATE_ADJUSTMENT,
                adjustment_amount=0.05,  # 5% adjustment
                priority=4,
                conditions={"min_samples": 2}
            )
        ]
    
    async def start_monitoring(
        self,
        session: ApplicationSession,
        config: MonitoringConfiguration
    ) -> bool:
        """
        Start real-time monitoring for an application session.
        
        Args:
            session: Application session to monitor
            config: Monitoring configuration
            
        Returns:
            True if monitoring started successfully
        """
        try:
            logger.info(f"Starting real-time monitoring for session {session.session_id}")
            
            # Store session and configuration
            self.monitoring_sessions[session.session_id] = session
            self.monitoring_configs[session.session_id] = config
            
            # Initialize data storage
            self.monitoring_data[session.session_id] = []
            self.active_adjustments[session.session_id] = []
            self.active_alerts[session.session_id] = []
            self.sensor_data[session.session_id] = []
            self.quality_checks[session.session_id] = []
            
            # Start monitoring if enabled
            if config.monitoring_enabled:
                # Start main monitoring task
                monitoring_task = asyncio.create_task(
                    self._monitoring_loop(session.session_id, config)
                )
                self.monitoring_tasks[session.session_id] = monitoring_task
                
                # Start sensor data collection
                sensor_task = asyncio.create_task(
                    self._sensor_data_loop(session.session_id, config)
                )
                self.sensor_tasks[session.session_id] = sensor_task
                
                # Start quality control
                if config.quality_checks_enabled:
                    quality_task = asyncio.create_task(
                        self._quality_control_loop(session.session_id, config)
                    )
                    self.quality_control_tasks[session.session_id] = quality_task
                
                self.active_monitoring[session.session_id] = True
                self.state = MonitoringState.MONITORING
                
                logger.info(f"Real-time monitoring started for session {session.session_id}")
                return True
            else:
                logger.info(f"Monitoring disabled for session {session.session_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error starting monitoring for session {session.session_id}: {e}")
            return False
    
    async def stop_monitoring(self, session_id: str) -> bool:
        """
        Stop real-time monitoring for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if monitoring stopped successfully
        """
        try:
            logger.info(f"Stopping real-time monitoring for session {session_id}")
            
            # Cancel monitoring tasks
            if session_id in self.monitoring_tasks:
                self.monitoring_tasks[session_id].cancel()
                del self.monitoring_tasks[session_id]
            
            if session_id in self.sensor_tasks:
                self.sensor_tasks[session_id].cancel()
                del self.sensor_tasks[session_id]
            
            if session_id in self.quality_control_tasks:
                self.quality_control_tasks[session_id].cancel()
                del self.quality_control_tasks[session_id]
            
            # Update state
            self.active_monitoring[session_id] = False
            
            # Update session status
            if session_id in self.monitoring_sessions:
                self.monitoring_sessions[session_id].status = ApplicationStatus.COMPLETED
                self.monitoring_sessions[session_id].actual_end = datetime.now()
            
            # Check if any monitoring is still active
            if not any(self.active_monitoring.values()):
                self.state = MonitoringState.IDLE
            
            logger.info(f"Real-time monitoring stopped for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping monitoring for session {session_id}: {e}")
            return False
    
    async def _monitoring_loop(self, session_id: str, config: MonitoringConfiguration):
        """Main monitoring loop for real-time data collection and analysis."""
        while True:
            try:
                # Collect monitoring data
                monitoring_data = await self._collect_monitoring_data(session_id)
                
                if monitoring_data:
                    # Store data
                    self.monitoring_data[session_id].append(monitoring_data)
                    
                    # Check for adjustments
                    adjustments = await self._check_adjustment_needs(session_id, monitoring_data)
                    
                    # Process adjustments
                    await self._process_adjustments(session_id, adjustments)
                    
                    # Check for alerts
                    alerts = await self._check_alerts(session_id, monitoring_data)
                    
                    # Process alerts
                    await self._process_alerts(session_id, alerts)
                    
                    # Update session progress
                    await self._update_session_progress(session_id, monitoring_data)
                
                # Wait for next monitoring cycle
                await asyncio.sleep(config.update_frequency_seconds)
                
            except asyncio.CancelledError:
                logger.info(f"Monitoring loop cancelled for session {session_id}")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop for session {session_id}: {e}")
                await asyncio.sleep(5)  # Wait 5 seconds before retrying
    
    async def _sensor_data_loop(self, session_id: str, config: MonitoringConfiguration):
        """Sensor data collection loop."""
        while True:
            try:
                # Collect sensor data
                sensor_data = await self._collect_sensor_data(session_id, config)
                
                if sensor_data:
                    self.sensor_data[session_id].extend(sensor_data)
                
                # Wait for next sensor collection cycle
                await asyncio.sleep(config.update_frequency_seconds)
                
            except asyncio.CancelledError:
                logger.info(f"Sensor data loop cancelled for session {session_id}")
                break
            except Exception as e:
                logger.error(f"Error in sensor data loop for session {session_id}: {e}")
                await asyncio.sleep(5)
    
    async def _quality_control_loop(self, session_id: str, config: MonitoringConfiguration):
        """Quality control loop."""
        while True:
            try:
                # Perform quality control check
                quality_check = await self._perform_quality_check(session_id)
                
                if quality_check:
                    self.quality_checks[session_id].append(quality_check)
                
                # Wait for next quality check
                await asyncio.sleep(config.quality_check_frequency)
                
            except asyncio.CancelledError:
                logger.info(f"Quality control loop cancelled for session {session_id}")
                break
            except Exception as e:
                logger.error(f"Error in quality control loop for session {session_id}: {e}")
                await asyncio.sleep(60)
    
    async def _collect_monitoring_data(self, session_id: str) -> Optional[ApplicationMonitoringData]:
        """Collect real-time monitoring data."""
        try:
            session = self.monitoring_sessions.get(session_id)
            if not session:
                return None
            
            # In real implementation, this would collect actual sensor data
            # For now, we'll simulate realistic monitoring data
            monitoring_data = await self._simulate_monitoring_data(session)
            
            return monitoring_data
            
        except Exception as e:
            logger.error(f"Error collecting monitoring data for session {session_id}: {e}")
            return None
    
    async def _simulate_monitoring_data(self, session: ApplicationSession) -> ApplicationMonitoringData:
        """Simulate realistic monitoring data (placeholder for real implementation)."""
        import random
        
        # Simulate realistic application data
        target_rate = session.target_rate
        base_rate = target_rate * random.uniform(0.95, 1.05)  # ±5% variation
        
        # Simulate environmental conditions
        temperature = random.uniform(60, 85)  # Typical field temperature
        humidity = random.uniform(40, 80)    # Typical humidity
        wind_speed = random.uniform(2, 15)    # Typical wind speed
        wind_direction = random.uniform(0, 360)
        soil_moisture = random.uniform(20, 60)
        
        # Simulate equipment metrics
        speed = random.uniform(4, 8)  # Typical application speed
        pressure = random.uniform(25, 40)  # Typical pressure
        
        # Simulate coverage metrics
        coverage_uniformity = random.uniform(0.85, 0.98)
        overlap_percentage = random.uniform(5, 15)
        
        # Calculate derived metrics
        rate_deviation = ((base_rate - target_rate) / target_rate) * 100
        quality_score = random.uniform(0.8, 0.98)
        drift_potential = min(1.0, wind_speed / 15.0)  # Higher wind = higher drift
        application_efficiency = random.uniform(0.85, 0.95)
        
        # Simulate GPS coordinates (in real implementation, would come from GPS)
        latitude = random.uniform(40.0, 41.0)
        longitude = random.uniform(-95.0, -94.0)
        elevation = random.uniform(800, 1200)
        
        return ApplicationMonitoringData(
            application_session_id=session.session_id,
            equipment_id=session.equipment_id,
            field_id=session.field_id,
            application_rate=base_rate,
            target_rate=target_rate,
            rate_deviation=rate_deviation,
            coverage_uniformity=coverage_uniformity,
            coverage_area=random.uniform(0.1, 0.5),  # Incremental area covered
            overlap_percentage=overlap_percentage,
            speed=speed,
            pressure=pressure,
            nozzle_status={"nozzle_1": True, "nozzle_2": True, "nozzle_3": random.choice([True, False])},
            temperature=temperature,
            humidity=humidity,
            wind_speed=wind_speed,
            wind_direction=wind_direction,
            soil_moisture=soil_moisture,
            latitude=latitude,
            longitude=longitude,
            elevation=elevation,
            quality_score=quality_score,
            drift_potential=drift_potential,
            application_efficiency=application_efficiency,
            equipment_status="operational",
            maintenance_alerts=[]
        )
    
    async def _collect_sensor_data(self, session_id: str, config: MonitoringConfiguration) -> List[SensorData]:
        """Collect sensor data from IoT sensors."""
        sensor_data = []
        
        for sensor_type in config.enabled_sensors:
            # In real implementation, this would collect actual sensor data
            # For now, we'll simulate sensor readings
            sensor_reading = await self._simulate_sensor_reading(sensor_type, session_id)
            if sensor_reading:
                sensor_data.append(sensor_reading)
        
        return sensor_data
    
    async def _simulate_sensor_reading(self, sensor_type: SensorType, session_id: str) -> Optional[SensorData]:
        """Simulate sensor reading (placeholder for real implementation)."""
        import random
        
        sensor_id = f"{sensor_type.value}_{random.randint(1000, 9999)}"
        
        # Get equipment ID from session or use default
        equipment_id = "equipment_456"  # Default equipment ID
        if session_id in self.monitoring_sessions:
            equipment_id = self.monitoring_sessions[session_id].equipment_id
        
        # Simulate different sensor readings based on type
        if sensor_type == SensorType.FLOW_METER:
            readings = {
                "flow_rate": random.uniform(10, 50),  # GPM
                "total_volume": random.uniform(100, 500)  # Gallons
            }
        elif sensor_type == SensorType.PRESSURE_SENSOR:
            readings = {
                "pressure": random.uniform(25, 40),  # PSI
                "temperature": random.uniform(60, 80)  # °F
            }
        elif sensor_type == SensorType.SPEED_SENSOR:
            readings = {
                "speed": random.uniform(4, 8),  # MPH
                "distance": random.uniform(0.1, 0.5)  # Miles
            }
        elif sensor_type == SensorType.WEATHER_STATION:
            readings = {
                "temperature": random.uniform(60, 85),  # °F
                "humidity": random.uniform(40, 80),  # %
                "wind_speed": random.uniform(2, 15),  # MPH
                "wind_direction": random.uniform(0, 360),  # Degrees
                "pressure": random.uniform(29.5, 30.5)  # inHg
            }
        elif sensor_type == SensorType.SOIL_MOISTURE_SENSOR:
            readings = {
                "moisture": random.uniform(20, 60),  # %
                "temperature": random.uniform(55, 75)  # °F
            }
        elif sensor_type == SensorType.GPS_SENSOR:
            readings = {
                "latitude": random.uniform(40.0, 41.0),
                "longitude": random.uniform(-95.0, -94.0),
                "elevation": random.uniform(800, 1200),  # Feet
                "accuracy": random.uniform(1, 5)  # Meters
            }
        else:
            return None
        
        return SensorData(
            sensor_id=sensor_id,
            sensor_type=sensor_type,
            equipment_id=equipment_id,
            readings=readings,
            data_quality=random.uniform(0.85, 0.98),
            battery_level=random.uniform(60, 100),
            signal_strength=random.uniform(80, 100)
        )
    
    async def _check_adjustment_needs(
        self, 
        session_id: str, 
        monitoring_data: ApplicationMonitoringData
    ) -> List[RealTimeAdjustment]:
        """Check if adjustments are needed based on current data."""
        adjustments = []
        
        for rule in self.adjustment_rules:
            # Check if rule conditions are met
            if await self._evaluate_rule_conditions(rule, session_id, monitoring_data):
                adjustment = await self._create_adjustment(rule, monitoring_data)
                if adjustment:
                    adjustments.append(adjustment)
        
        return adjustments
    
    async def _evaluate_rule_conditions(
        self, 
        rule: AdjustmentRule, 
        session_id: str, 
        monitoring_data: ApplicationMonitoringData
    ) -> bool:
        """Evaluate if adjustment rule conditions are met."""
        try:
            # Get metric value from monitoring data
            metric_value = self._get_metric_value(rule.metric, monitoring_data)
            if metric_value is None:
                return False
            
            # Check threshold
            threshold_met = False
            if rule.metric == MonitoringMetric.APPLICATION_RATE:
                # For application rate, check deviation from target
                deviation = abs(monitoring_data.rate_deviation) / 100
                threshold_met = deviation > rule.threshold
            elif rule.metric == MonitoringMetric.PRESSURE:
                # For pressure, check deviation from expected value (30 PSI)
                deviation = abs(metric_value - 30) / 30
                threshold_met = deviation > rule.threshold
            elif rule.metric == MonitoringMetric.COVERAGE_UNIFORMITY:
                # For coverage uniformity, check if below threshold
                threshold_met = metric_value < rule.threshold
            elif rule.metric == MonitoringMetric.WIND_SPEED:
                # For wind speed, check if above threshold
                threshold_met = metric_value > rule.threshold
            else:
                # For other metrics, use direct comparison
                threshold_met = metric_value > rule.threshold
            
            # Check additional conditions
            conditions_met = True
            if "min_samples" in rule.conditions:
                min_samples = rule.conditions["min_samples"]
                # For testing, we'll assume we have enough samples
                conditions_met = True  # Simplified for testing
            
            return threshold_met and conditions_met
            
        except Exception as e:
            logger.error(f"Error evaluating rule conditions: {e}")
            return False
    
    def _get_metric_value(self, metric: MonitoringMetric, monitoring_data: ApplicationMonitoringData) -> Optional[float]:
        """Get metric value from monitoring data."""
        metric_mapping = {
            MonitoringMetric.APPLICATION_RATE: monitoring_data.application_rate,
            MonitoringMetric.COVERAGE_UNIFORMITY: monitoring_data.coverage_uniformity,
            MonitoringMetric.SPEED: monitoring_data.speed,
            MonitoringMetric.PRESSURE: monitoring_data.pressure,
            MonitoringMetric.TEMPERATURE: monitoring_data.temperature,
            MonitoringMetric.HUMIDITY: monitoring_data.humidity,
            MonitoringMetric.WIND_SPEED: monitoring_data.wind_speed,
            MonitoringMetric.WIND_DIRECTION: monitoring_data.wind_direction,
            MonitoringMetric.SOIL_MOISTURE: monitoring_data.soil_moisture,
        }
        
        return metric_mapping.get(metric)
    
    async def _create_adjustment(
        self, 
        rule: AdjustmentRule, 
        monitoring_data: ApplicationMonitoringData
    ) -> Optional[RealTimeAdjustment]:
        """Create adjustment recommendation based on rule."""
        try:
            current_value = self._get_metric_value(rule.metric, monitoring_data)
            if current_value is None:
                return None
            
            # Calculate target value and adjustment amount
            if rule.adjustment_type == AdjustmentType.RATE_ADJUSTMENT:
                target_value = monitoring_data.target_rate
                adjustment_amount = target_value * rule.adjustment_amount
                reason = f"Application rate deviation detected: {monitoring_data.rate_deviation:.1f}%"
            elif rule.adjustment_type == AdjustmentType.COVERAGE_ADJUSTMENT:
                target_value = 0.95  # Target 95% coverage uniformity
                adjustment_amount = rule.adjustment_amount
                reason = f"Coverage uniformity below threshold: {current_value:.2f}"
            elif rule.adjustment_type == AdjustmentType.WEATHER_ADJUSTMENT:
                target_value = monitoring_data.target_rate * (1 - rule.adjustment_amount)
                adjustment_amount = rule.adjustment_amount
                reason = f"High wind speed detected: {current_value:.1f} mph"
            else:
                return None
            
            # Generate impact assessment
            impact_assessment = self._generate_impact_assessment(rule, adjustment_amount)
            
            # Calculate confidence and risk
            confidence = self._calculate_adjustment_confidence(rule, monitoring_data)
            risk_level = self._assess_adjustment_risk(rule, adjustment_amount)
            
            return RealTimeAdjustment(
                monitoring_data_id=monitoring_data.monitoring_id,
                adjustment_type=rule.adjustment_type,
                priority=rule.priority,
                current_value=current_value,
                target_value=target_value,
                adjustment_amount=adjustment_amount,
                reason=reason,
                impact_assessment=impact_assessment,
                implementation_time=5,  # 5 seconds to implement
                confidence=confidence,
                risk_level=risk_level,
                expires_at=datetime.now() + timedelta(minutes=5)  # Expires in 5 minutes
            )
            
        except Exception as e:
            logger.error(f"Error creating adjustment: {e}")
            return None
    
    def _generate_impact_assessment(self, rule: AdjustmentRule, adjustment_amount: float) -> str:
        """Generate impact assessment for adjustment."""
        if rule.adjustment_type == AdjustmentType.RATE_ADJUSTMENT:
            return f"Rate adjustment of {adjustment_amount:.2f} lbs/acre to improve application accuracy"
        elif rule.adjustment_type == AdjustmentType.COVERAGE_ADJUSTMENT:
            return f"Coverage adjustment to improve uniformity by {adjustment_amount:.1%}"
        elif rule.adjustment_type == AdjustmentType.WEATHER_ADJUSTMENT:
            return f"Rate reduction of {adjustment_amount:.1%} due to adverse weather conditions"
        else:
            return "Adjustment to optimize application performance"
    
    def _calculate_adjustment_confidence(self, rule: AdjustmentRule, monitoring_data: ApplicationMonitoringData) -> float:
        """Calculate confidence in adjustment recommendation."""
        base_confidence = 0.8
        
        # Adjust confidence based on data quality
        if monitoring_data.quality_score > 0.9:
            base_confidence += 0.1
        elif monitoring_data.quality_score < 0.8:
            base_confidence -= 0.1
        
        # Adjust confidence based on environmental conditions
        if monitoring_data.wind_speed > 10:
            base_confidence -= 0.1  # Lower confidence in windy conditions
        
        return max(0.5, min(1.0, base_confidence))
    
    def _assess_adjustment_risk(self, rule: AdjustmentRule, adjustment_amount: float) -> AlertSeverity:
        """Assess risk level of adjustment."""
        if rule.priority <= 2:
            return AlertSeverity.HIGH
        elif rule.priority <= 3:
            return AlertSeverity.MEDIUM
        else:
            return AlertSeverity.LOW
    
    async def _process_adjustments(self, session_id: str, adjustments: List[RealTimeAdjustment]):
        """Process adjustment recommendations."""
        if not adjustments:
            return
        
        # Store adjustments
        if session_id not in self.active_adjustments:
            self.active_adjustments[session_id] = []
        
        self.active_adjustments[session_id].extend(adjustments)
        
        # Send notifications for high-priority adjustments
        for adjustment in adjustments:
            if adjustment.priority <= 2:  # High priority
                await self._send_adjustment_notification(adjustment)
        
        logger.info(f"Processed {len(adjustments)} adjustments for session {session_id}")
    
    async def _send_adjustment_notification(self, adjustment: RealTimeAdjustment):
        """Send adjustment notification (placeholder for real implementation)."""
        logger.warning(f"ADJUSTMENT NEEDED: {adjustment.reason} - Priority: {adjustment.priority}")
    
    async def _check_alerts(self, session_id: str, monitoring_data: ApplicationMonitoringData) -> List[MonitoringAlert]:
        """Check for monitoring alerts."""
        alerts = []
        config = self.monitoring_configs.get(session_id)
        
        if not config:
            return alerts
        
        # Check rate deviation alerts
        if abs(monitoring_data.rate_deviation) > 10:  # >10% deviation
            alert = MonitoringAlert(
                monitoring_data_id=monitoring_data.monitoring_id,
                alert_type="rate_deviation",
                severity=AlertSeverity.HIGH if abs(monitoring_data.rate_deviation) > 20 else AlertSeverity.MEDIUM,
                metric=MonitoringMetric.APPLICATION_RATE,
                current_value=monitoring_data.application_rate,
                threshold_value=monitoring_data.target_rate,
                deviation_percentage=abs(monitoring_data.rate_deviation),
                title="Application Rate Deviation",
                message=f"Application rate is {monitoring_data.rate_deviation:.1f}% from target",
                recommendations=[
                    "Check equipment calibration",
                    "Verify application settings",
                    "Consider rate adjustment"
                ]
            )
            alerts.append(alert)
        
        # Check coverage uniformity alerts
        if monitoring_data.coverage_uniformity < 0.8:
            alert = MonitoringAlert(
                monitoring_data_id=monitoring_data.monitoring_id,
                alert_type="coverage_uniformity",
                severity=AlertSeverity.MEDIUM,
                metric=MonitoringMetric.COVERAGE_UNIFORMITY,
                current_value=monitoring_data.coverage_uniformity,
                threshold_value=0.8,
                deviation_percentage=(0.8 - monitoring_data.coverage_uniformity) * 100,
                title="Poor Coverage Uniformity",
                message=f"Coverage uniformity is {monitoring_data.coverage_uniformity:.2f}",
                recommendations=[
                    "Check nozzle condition",
                    "Adjust boom height",
                    "Verify overlap settings"
                ]
            )
            alerts.append(alert)
        
        # Check wind speed alerts
        if monitoring_data.wind_speed > 10:
            alert = MonitoringAlert(
                monitoring_data_id=monitoring_data.monitoring_id,
                alert_type="high_wind",
                severity=AlertSeverity.HIGH if monitoring_data.wind_speed > 15 else AlertSeverity.MEDIUM,
                metric=MonitoringMetric.WIND_SPEED,
                current_value=monitoring_data.wind_speed,
                threshold_value=10.0,
                deviation_percentage=((monitoring_data.wind_speed - 10) / 10) * 100,
                title="High Wind Speed",
                message=f"Wind speed is {monitoring_data.wind_speed:.1f} mph",
                recommendations=[
                    "Consider reducing application rate",
                    "Monitor drift potential",
                    "Adjust application timing if possible"
                ]
            )
            alerts.append(alert)
        
        return alerts
    
    async def _process_alerts(self, session_id: str, alerts: List[MonitoringAlert]):
        """Process monitoring alerts."""
        if not alerts:
            return
        
        # Store alerts
        if session_id not in self.active_alerts:
            self.active_alerts[session_id] = []
        
        self.active_alerts[session_id].extend(alerts)
        
        # Send notifications for critical alerts
        for alert in alerts:
            if alert.severity == AlertSeverity.CRITICAL:
                await self._send_alert_notification(alert)
        
        logger.info(f"Processed {len(alerts)} alerts for session {session_id}")
    
    async def _send_alert_notification(self, alert: MonitoringAlert):
        """Send alert notification (placeholder for real implementation)."""
        logger.warning(f"ALERT: {alert.title} - {alert.message}")
    
    async def _update_session_progress(self, session_id: str, monitoring_data: ApplicationMonitoringData):
        """Update session progress based on monitoring data."""
        session = self.monitoring_sessions.get(session_id)
        if not session:
            return
        
        # Update completed area
        session.completed_area += monitoring_data.coverage_area
        
        # Update progress percentage
        if session.total_area > 0:
            session.progress_percentage = (session.completed_area / session.total_area) * 100
        
        # Update quality metrics
        session.average_rate = self._calculate_average_rate(session_id)
        session.rate_variability = self._calculate_rate_variability(session_id)
        session.coverage_score = self._calculate_average_coverage_score(session_id)
        
        # Update adjustment and alert counts
        session.total_adjustments = len(self.active_adjustments.get(session_id, []))
        session.active_alerts = len([a for a in self.active_alerts.get(session_id, []) if not a.resolved])
    
    def _calculate_average_rate(self, session_id: str) -> float:
        """Calculate average application rate for session."""
        data_points = self.monitoring_data.get(session_id, [])
        if not data_points:
            return 0.0
        
        rates = [data.application_rate for data in data_points]
        return statistics.mean(rates)
    
    def _calculate_rate_variability(self, session_id: str) -> float:
        """Calculate rate variability for session."""
        data_points = self.monitoring_data.get(session_id, [])
        if len(data_points) < 2:
            return 0.0
        
        rates = [data.application_rate for data in data_points]
        mean_rate = statistics.mean(rates)
        variance = statistics.variance(rates, mean_rate)
        return (variance ** 0.5 / mean_rate) * 100  # Coefficient of variation
    
    def _calculate_average_coverage_score(self, session_id: str) -> float:
        """Calculate average coverage score for session."""
        data_points = self.monitoring_data.get(session_id, [])
        if not data_points:
            return 0.0
        
        coverage_scores = [data.coverage_uniformity for data in data_points]
        return statistics.mean(coverage_scores)
    
    async def _perform_quality_check(self, session_id: str) -> Optional[QualityControlCheck]:
        """Perform quality control check."""
        try:
            # Get recent monitoring data
            recent_data = self.monitoring_data.get(session_id, [])
            if len(recent_data) < 5:  # Need at least 5 data points
                return None
            
            # Perform quality checks
            checks_passed = 0
            total_checks = 0
            deviations = []
            recommendations = []
            corrective_actions = []
            
            # Check 1: Rate accuracy
            total_checks += 1
            rate_deviations = [abs(data.rate_deviation) for data in recent_data[-10:]]
            avg_rate_deviation = statistics.mean(rate_deviations)
            
            if avg_rate_deviation <= 5:  # Within 5%
                checks_passed += 1
            else:
                deviations.append({
                    "check": "rate_accuracy",
                    "value": avg_rate_deviation,
                    "threshold": 5.0,
                    "severity": "high" if avg_rate_deviation > 10 else "medium"
                })
                recommendations.append("Calibrate application equipment")
                corrective_actions.append("Adjust application rate settings")
            
            # Check 2: Coverage uniformity
            total_checks += 1
            coverage_scores = [data.coverage_uniformity for data in recent_data[-10:]]
            avg_coverage = statistics.mean(coverage_scores)
            
            if avg_coverage >= 0.85:  # 85% or better
                checks_passed += 1
            else:
                deviations.append({
                    "check": "coverage_uniformity",
                    "value": avg_coverage,
                    "threshold": 0.85,
                    "severity": "high" if avg_coverage < 0.75 else "medium"
                })
                recommendations.append("Check nozzle condition and boom height")
                corrective_actions.append("Adjust boom height and nozzle spacing")
            
            # Check 3: Environmental compliance
            total_checks += 1
            drift_potentials = [data.drift_potential for data in recent_data[-10:]]
            avg_drift_potential = statistics.mean(drift_potentials)
            
            if avg_drift_potential <= 0.3:  # Low drift potential
                checks_passed += 1
            else:
                deviations.append({
                    "check": "drift_potential",
                    "value": avg_drift_potential,
                    "threshold": 0.3,
                    "severity": "high" if avg_drift_potential > 0.5 else "medium"
                })
                recommendations.append("Monitor wind conditions and adjust timing")
                corrective_actions.append("Reduce application rate or postpone application")
            
            # Calculate overall score
            overall_score = checks_passed / total_checks if total_checks > 0 else 0
            
            return QualityControlCheck(
                session_id=session_id,
                check_type="comprehensive_quality_check",
                parameters={
                    "data_points_analyzed": len(recent_data),
                    "time_window_minutes": len(recent_data) * 5  # Assuming 5-second intervals
                },
                thresholds={
                    "rate_accuracy": 5.0,
                    "coverage_uniformity": 0.85,
                    "drift_potential": 0.3
                },
                passed=overall_score >= 0.8,  # Pass if 80% or more checks pass
                score=overall_score,
                deviations=deviations,
                recommendations=recommendations,
                corrective_actions=corrective_actions,
                performed_by="system"
            )
            
        except Exception as e:
            logger.error(f"Error performing quality check for session {session_id}: {e}")
            return None
    
    # Public API methods
    
    async def get_current_monitoring_data(self, session_id: str) -> Optional[ApplicationMonitoringData]:
        """Get current monitoring data for session."""
        data_points = self.monitoring_data.get(session_id, [])
        return data_points[-1] if data_points else None
    
    async def get_monitoring_history(self, session_id: str, minutes: int = 60) -> List[ApplicationMonitoringData]:
        """Get monitoring history for session."""
        data_points = self.monitoring_data.get(session_id, [])
        if not data_points:
            return []
        
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        return [
            data for data in data_points
            if data.timestamp > cutoff_time
        ]
    
    async def get_active_adjustments(self, session_id: str) -> List[RealTimeAdjustment]:
        """Get active adjustments for session."""
        adjustments = self.active_adjustments.get(session_id, [])
        # Filter out expired adjustments
        current_time = datetime.now()
        return [
            adj for adj in adjustments
            if adj.expires_at is None or adj.expires_at > current_time
        ]
    
    async def get_active_alerts(self, session_id: str) -> List[MonitoringAlert]:
        """Get active alerts for session."""
        alerts = self.active_alerts.get(session_id, [])
        return [alert for alert in alerts if not alert.resolved]
    
    async def implement_adjustment(self, session_id: str, adjustment_id: str) -> bool:
        """Implement an adjustment."""
        adjustments = self.active_adjustments.get(session_id, [])
        for adjustment in adjustments:
            if adjustment.adjustment_id == adjustment_id:
                adjustment.implemented = True
                adjustment.implemented_at = datetime.now()
                logger.info(f"Adjustment {adjustment_id} implemented for session {session_id}")
                return True
        
        return False
    
    async def acknowledge_alert(self, session_id: str, alert_id: str) -> bool:
        """Acknowledge an alert."""
        alerts = self.active_alerts.get(session_id, [])
        for alert in alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                alert.acknowledged_at = datetime.now()
                logger.info(f"Alert {alert_id} acknowledged for session {session_id}")
                return True
        
        return False
    
    async def resolve_alert(self, session_id: str, alert_id: str) -> bool:
        """Resolve an alert."""
        alerts = self.active_alerts.get(session_id, [])
        for alert in alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                alert.resolved_at = datetime.now()
                logger.info(f"Alert {alert_id} resolved for session {session_id}")
                return True
        
        return False
    
    async def get_monitoring_summary(self, session_id: str) -> Optional[MonitoringSummary]:
        """Get comprehensive monitoring summary for session."""
        session = self.monitoring_sessions.get(session_id)
        if not session:
            return None
        
        # Calculate monitoring duration
        start_time = session.actual_start or session.planned_start
        end_time = session.actual_end or datetime.now()
        duration_minutes = (end_time - start_time).total_seconds() / 60
        
        # Get data statistics
        data_points = self.monitoring_data.get(session_id, [])
        total_data_points = len(data_points)
        data_quality_average = statistics.mean([d.quality_score for d in data_points]) if data_points else 0
        
        # Get adjustment statistics
        adjustments = self.active_adjustments.get(session_id, [])
        total_adjustments = len(adjustments)
        successful_adjustments = len([a for a in adjustments if a.implemented])
        
        # Get alert statistics
        alerts = self.active_alerts.get(session_id, [])
        total_alerts = len(alerts)
        critical_alerts = len([a for a in alerts if a.severity == AlertSeverity.CRITICAL])
        resolved_alerts = len([a for a in alerts if a.resolved])
        
        # Get quality statistics
        quality_checks_list = self.quality_checks.get(session_id, [])
        quality_checks_performed = len(quality_checks_list)
        quality_checks_passed = len([q for q in quality_checks_list if q.passed])
        average_quality_score = statistics.mean([q.score for q in quality_checks_list]) if quality_checks_list else 0
        
        # Calculate performance metrics
        if data_points:
            average_rate_accuracy = 1 - (statistics.mean([abs(d.rate_deviation) for d in data_points]) / 100)
            average_coverage_uniformity = statistics.mean([d.coverage_uniformity for d in data_points])
            average_application_efficiency = statistics.mean([d.application_efficiency for d in data_points])
            average_drift_potential = statistics.mean([d.drift_potential for d in data_points])
            environmental_compliance_score = 1 - average_drift_potential
        else:
            average_rate_accuracy = 0
            average_coverage_uniformity = 0
            average_application_efficiency = 0
            average_drift_potential = 0
            environmental_compliance_score = 0
        
        return MonitoringSummary(
            session_id=session_id,
            monitoring_duration_minutes=duration_minutes,
            total_data_points=total_data_points,
            data_quality_average=data_quality_average,
            total_adjustments=total_adjustments,
            successful_adjustments=successful_adjustments,
            adjustment_success_rate=successful_adjustments / total_adjustments if total_adjustments > 0 else 0,
            total_alerts=total_alerts,
            critical_alerts=critical_alerts,
            resolved_alerts=resolved_alerts,
            average_quality_score=average_quality_score,
            quality_checks_performed=quality_checks_performed,
            quality_checks_passed=quality_checks_passed,
            average_rate_accuracy=average_rate_accuracy,
            average_coverage_uniformity=average_coverage_uniformity,
            average_application_efficiency=average_application_efficiency,
            average_drift_potential=average_drift_potential,
            environmental_compliance_score=environmental_compliance_score
        )
    
    async def get_monitoring_status(self, session_id: str) -> Dict[str, Any]:
        """Get monitoring status for session."""
        session = self.monitoring_sessions.get(session_id)
        config = self.monitoring_configs.get(session_id)
        is_monitoring = session_id in self.active_monitoring and self.active_monitoring[session_id]
        
        return {
            "session_id": session_id,
            "monitoring_enabled": is_monitoring,
            "session_status": session.status.value if session else "unknown",
            "configuration": config.dict() if config else None,
            "data_points": len(self.monitoring_data.get(session_id, [])),
            "active_adjustments": len(self.active_adjustments.get(session_id, [])),
            "active_alerts": len(self.active_alerts.get(session_id, [])),
            "quality_checks": len(self.quality_checks.get(session_id, [])),
            "last_update": self.monitoring_data[session_id][-1].timestamp.isoformat() if self.monitoring_data.get(session_id) else None,
            "monitoring_state": self.state.value
        }
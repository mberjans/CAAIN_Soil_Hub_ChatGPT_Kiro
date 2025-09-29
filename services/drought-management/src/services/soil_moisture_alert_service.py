"""
Soil Moisture Alert Service

Advanced alert system for soil moisture monitoring with intelligent
alert generation, escalation, and notification management.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from uuid import UUID
from enum import Enum

logger = logging.getLogger(__name__)

class AlertSeverity(str, Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(str, Enum):
    """Types of soil moisture alerts."""
    LOW_MOISTURE = "low_moisture"
    CRITICAL_MOISTURE = "critical_moisture"
    DROUGHT_STRESS = "drought_stress"
    IRRIGATION_NEEDED = "irrigation_needed"
    OVER_IRRIGATION = "over_irrigation"
    MOISTURE_TREND = "moisture_trend"
    WEATHER_ALERT = "weather_alert"
    SENSOR_FAILURE = "sensor_failure"

class AlertStatus(str, Enum):
    """Alert status states."""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"

class SoilMoistureAlert:
    """Soil moisture alert model."""
    
    def __init__(self, alert_id: UUID, field_id: UUID, alert_type: AlertType, 
                 severity: AlertSeverity, message: str, recommendation: str,
                 threshold_value: float, current_value: float, **kwargs):
        self.alert_id = alert_id
        self.field_id = field_id
        self.alert_type = alert_type
        self.severity = severity
        self.message = message
        self.recommendation = recommendation
        self.threshold_value = threshold_value
        self.current_value = current_value
        self.status = AlertStatus.ACTIVE
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.acknowledged_at = None
        self.resolved_at = None
        self.escalation_level = 0
        self.notification_sent = False
        self.metadata = kwargs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary."""
        return {
            "alert_id": str(self.alert_id),
            "field_id": str(self.field_id),
            "alert_type": self.alert_type.value,
            "severity": self.severity.value,
            "message": self.message,
            "recommendation": self.recommendation,
            "threshold_value": self.threshold_value,
            "current_value": self.current_value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "escalation_level": self.escalation_level,
            "notification_sent": self.notification_sent,
            "metadata": self.metadata
        }

class SoilMoistureAlertService:
    """Advanced soil moisture alert service."""
    
    def __init__(self):
        self.active_alerts = {}  # field_id -> List[SoilMoistureAlert]
        self.alert_history = []
        self.alert_rules = {}
        self.escalation_rules = {}
        self.notification_service = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize the alert service."""
        try:
            logger.info("Initializing Soil Moisture Alert Service...")
            
            # Initialize notification service
            self.notification_service = NotificationService()
            await self.notification_service.initialize()
            
            # Load default alert rules
            await self._load_default_alert_rules()
            
            # Load escalation rules
            await self._load_escalation_rules()
            
            self.initialized = True
            logger.info("Soil Moisture Alert Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Soil Moisture Alert Service: {str(e)}")
            raise
    
    async def cleanup(self):
        """Clean up alert service resources."""
        try:
            logger.info("Cleaning up Soil Moisture Alert Service...")
            
            if self.notification_service:
                await self.notification_service.cleanup()
            
            self.initialized = False
            logger.info("Soil Moisture Alert Service cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
    
    async def evaluate_moisture_alerts(self, field_id: UUID, moisture_data: Dict[str, Any], 
                                     field_config: Dict[str, Any]) -> List[SoilMoistureAlert]:
        """
        Evaluate soil moisture data and generate alerts.
        
        Args:
            field_id: Field identifier
            moisture_data: Current moisture data
            field_config: Field monitoring configuration
            
        Returns:
            List of generated alerts
        """
        try:
            logger.info(f"Evaluating moisture alerts for field: {field_id}")
            
            alerts = []
            surface_moisture = moisture_data.get("surface_moisture_percent", 0)
            deep_moisture = moisture_data.get("deep_moisture_percent", 0)
            available_water = moisture_data.get("available_water_capacity", 0)
            
            # Get alert thresholds
            thresholds = field_config.get("alert_thresholds", {})
            
            # Check low moisture alerts
            low_threshold = thresholds.get("low_moisture", 30.0)
            if surface_moisture < low_threshold:
                alert = await self._create_moisture_alert(
                    field_id, AlertType.LOW_MOISTURE, AlertSeverity.MEDIUM,
                    f"Low soil moisture: {surface_moisture:.1f}%",
                    "Consider irrigation or conservation practices",
                    low_threshold, surface_moisture
                )
                alerts.append(alert)
            
            # Check critical moisture alerts
            critical_threshold = thresholds.get("critical_moisture", 20.0)
            if surface_moisture < critical_threshold:
                alert = await self._create_moisture_alert(
                    field_id, AlertType.CRITICAL_MOISTURE, AlertSeverity.HIGH,
                    f"Critical soil moisture: {surface_moisture:.1f}%",
                    "Immediate irrigation required",
                    critical_threshold, surface_moisture
                )
                alerts.append(alert)
            
            # Check drought stress alerts
            if available_water < 0.5:  # Less than 0.5 inches available water
                alert = await self._create_moisture_alert(
                    field_id, AlertType.DROUGHT_STRESS, AlertSeverity.HIGH,
                    f"Drought stress conditions: {available_water:.2f} inches available water",
                    "Implement drought mitigation measures immediately",
                    0.5, available_water
                )
                alerts.append(alert)
            
            # Check irrigation needed alerts
            if surface_moisture < thresholds.get("irrigation_threshold", 25.0):
                alert = await self._create_moisture_alert(
                    field_id, AlertType.IRRIGATION_NEEDED, AlertSeverity.MEDIUM,
                    f"Irrigation recommended: {surface_moisture:.1f}% moisture",
                    "Schedule irrigation within 24-48 hours",
                    thresholds.get("irrigation_threshold", 25.0), surface_moisture
                )
                alerts.append(alert)
            
            # Check over-irrigation alerts
            high_threshold = thresholds.get("high_moisture", 80.0)
            if surface_moisture > high_threshold:
                alert = await self._create_moisture_alert(
                    field_id, AlertType.OVER_IRRIGATION, AlertSeverity.MEDIUM,
                    f"Excessive soil moisture: {surface_moisture:.1f}%",
                    "Reduce irrigation frequency and check drainage",
                    high_threshold, surface_moisture
                )
                alerts.append(alert)
            
            # Check moisture trend alerts
            trend = moisture_data.get("trend", "stable")
            if trend == "rapid_decline" and surface_moisture < 35.0:
                alert = await self._create_moisture_alert(
                    field_id, AlertType.MOISTURE_TREND, AlertSeverity.MEDIUM,
                    f"Rapid moisture decline detected: {surface_moisture:.1f}%",
                    "Monitor closely and prepare for irrigation",
                    35.0, surface_moisture,
                    trend_data=moisture_data.get("trend_data", {})
                )
                alerts.append(alert)
            
            # Store alerts
            await self._store_alerts(field_id, alerts)
            
            # Send notifications for new alerts
            await self._send_alert_notifications(field_id, alerts)
            
            logger.info(f"Generated {len(alerts)} alerts for field: {field_id}")
            return alerts
            
        except Exception as e:
            logger.error(f"Error evaluating moisture alerts: {str(e)}")
            raise
    
    async def get_active_alerts(self, field_id: UUID, alert_type: Optional[AlertType] = None) -> List[SoilMoistureAlert]:
        """Get active alerts for a field."""
        try:
            field_alerts = self.active_alerts.get(str(field_id), [])
            
            if alert_type:
                field_alerts = [alert for alert in field_alerts if alert.alert_type == alert_type]
            
            return field_alerts
            
        except Exception as e:
            logger.error(f"Error getting active alerts: {str(e)}")
            raise
    
    async def acknowledge_alert(self, alert_id: UUID, user_id: UUID, notes: Optional[str] = None) -> bool:
        """Acknowledge an alert."""
        try:
            alert = await self._find_alert_by_id(alert_id)
            if not alert:
                return False
            
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.utcnow()
            alert.updated_at = datetime.utcnow()
            
            if notes:
                alert.metadata["acknowledgment_notes"] = notes
                alert.metadata["acknowledged_by"] = str(user_id)
            
            logger.info(f"Alert {alert_id} acknowledged by user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error acknowledging alert: {str(e)}")
            return False
    
    async def resolve_alert(self, alert_id: UUID, user_id: UUID, resolution_notes: Optional[str] = None) -> bool:
        """Resolve an alert."""
        try:
            alert = await self._find_alert_by_id(alert_id)
            if not alert:
                return False
            
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.utcnow()
            alert.updated_at = datetime.utcnow()
            
            if resolution_notes:
                alert.metadata["resolution_notes"] = resolution_notes
                alert.metadata["resolved_by"] = str(user_id)
            
            # Remove from active alerts
            await self._remove_from_active_alerts(alert)
            
            # Add to history
            self.alert_history.append(alert)
            
            logger.info(f"Alert {alert_id} resolved by user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error resolving alert: {str(e)}")
            return False
    
    async def escalate_alert(self, alert_id: UUID) -> bool:
        """Escalate an alert to the next level."""
        try:
            alert = await self._find_alert_by_id(alert_id)
            if not alert:
                return False
            
            # Check if alert can be escalated
            max_escalation = self.escalation_rules.get(alert.alert_type.value, {}).get("max_level", 3)
            if alert.escalation_level >= max_escalation:
                return False
            
            # Increment escalation level
            alert.escalation_level += 1
            alert.updated_at = datetime.utcnow()
            
            # Update severity if needed
            escalation_rules = self.escalation_rules.get(alert.alert_type.value, {})
            severity_levels = escalation_rules.get("severity_levels", [])
            if alert.escalation_level < len(severity_levels):
                alert.severity = AlertSeverity(severity_levels[alert.escalation_level])
            
            # Send escalation notification
            await self._send_escalation_notification(alert)
            
            logger.info(f"Alert {alert_id} escalated to level {alert.escalation_level}")
            return True
            
        except Exception as e:
            logger.error(f"Error escalating alert: {str(e)}")
            return False
    
    async def get_alert_statistics(self, field_id: UUID, days: int = 30) -> Dict[str, Any]:
        """Get alert statistics for a field."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get alerts from history and active alerts
            all_alerts = []
            
            # Add active alerts
            field_alerts = self.active_alerts.get(str(field_id), [])
            all_alerts.extend(field_alerts)
            
            # Add historical alerts
            historical_alerts = [
                alert for alert in self.alert_history
                if str(alert.field_id) == str(field_id) and alert.created_at >= cutoff_date
            ]
            all_alerts.extend(historical_alerts)
            
            # Calculate statistics
            total_alerts = len(all_alerts)
            active_alerts = len([alert for alert in all_alerts if alert.status == AlertStatus.ACTIVE])
            resolved_alerts = len([alert for alert in all_alerts if alert.status == AlertStatus.RESOLVED])
            
            # Count by severity
            severity_counts = {}
            for severity in AlertSeverity:
                severity_counts[severity.value] = len([
                    alert for alert in all_alerts if alert.severity == severity
                ])
            
            # Count by type
            type_counts = {}
            for alert_type in AlertType:
                type_counts[alert_type.value] = len([
                    alert for alert in all_alerts if alert.alert_type == alert_type
                ])
            
            # Calculate average resolution time
            resolved_with_times = [
                alert for alert in all_alerts
                if alert.status == AlertStatus.RESOLVED and alert.resolved_at and alert.created_at
            ]
            
            avg_resolution_time = None
            if resolved_with_times:
                resolution_times = [
                    (alert.resolved_at - alert.created_at).total_seconds() / 3600  # hours
                    for alert in resolved_with_times
                ]
                avg_resolution_time = sum(resolution_times) / len(resolution_times)
            
            return {
                "field_id": str(field_id),
                "period_days": days,
                "total_alerts": total_alerts,
                "active_alerts": active_alerts,
                "resolved_alerts": resolved_alerts,
                "severity_breakdown": severity_counts,
                "type_breakdown": type_counts,
                "average_resolution_time_hours": avg_resolution_time,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting alert statistics: {str(e)}")
            raise
    
    # Helper methods
    async def _create_moisture_alert(self, field_id: UUID, alert_type: AlertType, 
                                   severity: AlertSeverity, message: str, recommendation: str,
                                   threshold_value: float, current_value: float, **metadata) -> SoilMoistureAlert:
        """Create a new moisture alert."""
        import uuid
        alert_id = uuid.uuid4()
        
        alert = SoilMoistureAlert(
            alert_id=alert_id,
            field_id=field_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
            recommendation=recommendation,
            threshold_value=threshold_value,
            current_value=current_value,
            **metadata
        )
        
        return alert
    
    async def _store_alerts(self, field_id: UUID, alerts: List[SoilMoistureAlert]):
        """Store alerts in active alerts list."""
        if not alerts:
            return
        
        field_key = str(field_id)
        if field_key not in self.active_alerts:
            self.active_alerts[field_key] = []
        
        self.active_alerts[field_key].extend(alerts)
    
    async def _send_alert_notifications(self, field_id: UUID, alerts: List[SoilMoistureAlert]):
        """Send notifications for new alerts."""
        if not self.notification_service or not alerts:
            return
        
        for alert in alerts:
            try:
                await self.notification_service.send_alert_notification(alert)
                alert.notification_sent = True
            except Exception as e:
                logger.error(f"Error sending notification for alert {alert.alert_id}: {str(e)}")
    
    async def _send_escalation_notification(self, alert: SoilMoistureAlert):
        """Send escalation notification."""
        if not self.notification_service:
            return
        
        try:
            await self.notification_service.send_escalation_notification(alert)
        except Exception as e:
            logger.error(f"Error sending escalation notification for alert {alert.alert_id}: {str(e)}")
    
    async def _find_alert_by_id(self, alert_id: UUID) -> Optional[SoilMoistureAlert]:
        """Find alert by ID in active alerts."""
        for field_alerts in self.active_alerts.values():
            for alert in field_alerts:
                if alert.alert_id == alert_id:
                    return alert
        return None
    
    async def _remove_from_active_alerts(self, alert: SoilMoistureAlert):
        """Remove alert from active alerts."""
        field_key = str(alert.field_id)
        if field_key in self.active_alerts:
            self.active_alerts[field_key] = [
                a for a in self.active_alerts[field_key] if a.alert_id != alert.alert_id
            ]
    
    async def _load_default_alert_rules(self):
        """Load default alert rules."""
        self.alert_rules = {
            "low_moisture": {
                "threshold": 30.0,
                "severity": "medium",
                "message_template": "Low soil moisture: {current_value:.1f}%",
                "recommendation": "Consider irrigation or conservation practices"
            },
            "critical_moisture": {
                "threshold": 20.0,
                "severity": "high",
                "message_template": "Critical soil moisture: {current_value:.1f}%",
                "recommendation": "Immediate irrigation required"
            },
            "drought_stress": {
                "threshold": 0.5,
                "severity": "high",
                "message_template": "Drought stress conditions: {current_value:.2f} inches available water",
                "recommendation": "Implement drought mitigation measures immediately"
            },
            "irrigation_needed": {
                "threshold": 25.0,
                "severity": "medium",
                "message_template": "Irrigation recommended: {current_value:.1f}% moisture",
                "recommendation": "Schedule irrigation within 24-48 hours"
            },
            "over_irrigation": {
                "threshold": 80.0,
                "severity": "medium",
                "message_template": "Excessive soil moisture: {current_value:.1f}%",
                "recommendation": "Reduce irrigation frequency and check drainage"
            }
        }
    
    async def _load_escalation_rules(self):
        """Load escalation rules."""
        self.escalation_rules = {
            "critical_moisture": {
                "max_level": 3,
                "severity_levels": ["high", "critical", "critical"],
                "escalation_intervals_hours": [2, 4, 8]
            },
            "drought_stress": {
                "max_level": 2,
                "severity_levels": ["high", "critical"],
                "escalation_intervals_hours": [1, 2]
            },
            "low_moisture": {
                "max_level": 2,
                "severity_levels": ["medium", "high"],
                "escalation_intervals_hours": [24, 48]
            }
        }


class NotificationService:
    """Notification service for alerts."""
    
    def __init__(self):
        self.initialized = False
    
    async def initialize(self):
        """Initialize notification service."""
        self.initialized = True
        logger.info("Notification service initialized")
    
    async def cleanup(self):
        """Clean up notification service."""
        self.initialized = False
        logger.info("Notification service cleaned up")
    
    async def send_alert_notification(self, alert: SoilMoistureAlert):
        """Send alert notification."""
        # In a real implementation, this would send actual notifications
        # (email, SMS, push notifications, etc.)
        logger.info(f"Sending alert notification: {alert.message}")
        
        # Mock notification sending
        notification_data = {
            "alert_id": str(alert.alert_id),
            "field_id": str(alert.field_id),
            "severity": alert.severity.value,
            "message": alert.message,
            "recommendation": alert.recommendation,
            "timestamp": alert.created_at.isoformat()
        }
        
        # Here you would integrate with actual notification services:
        # - Email service (SendGrid, AWS SES, etc.)
        # - SMS service (Twilio, AWS SNS, etc.)
        # - Push notification service (Firebase, etc.)
        # - Webhook notifications
        
        logger.info(f"Alert notification sent: {notification_data}")
    
    async def send_escalation_notification(self, alert: SoilMoistureAlert):
        """Send escalation notification."""
        logger.info(f"Sending escalation notification for alert {alert.alert_id} to level {alert.escalation_level}")
        
        escalation_data = {
            "alert_id": str(alert.alert_id),
            "field_id": str(alert.field_id),
            "escalation_level": alert.escalation_level,
            "severity": alert.severity.value,
            "message": f"ALERT ESCALATED: {alert.message}",
            "timestamp": alert.updated_at.isoformat()
        }
        
        logger.info(f"Escalation notification sent: {escalation_data}")
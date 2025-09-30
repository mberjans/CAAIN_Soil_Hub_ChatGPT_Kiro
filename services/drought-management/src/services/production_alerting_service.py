"""
Production Alerting Service

Comprehensive alerting system for production monitoring.
Handles system health alerts, performance degradation warnings,
data quality issues, and automated notification management.
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from decimal import Decimal
import json
from enum import Enum
from dataclasses import dataclass

from ..models.production_alerting_models import (
    AlertRule,
    AlertCondition,
    AlertAction,
    AlertNotification,
    AlertChannel,
    AlertTemplate,
    AlertEscalation,
    AlertSuppression,
    AlertMetrics,
    AlertHistory,
    AlertConfiguration,
    AlertResponse,
    AlertStatus,
    AlertSeverity,
    NotificationChannel,
    EscalationPolicy,
    SuppressionRule,
    AlertRuleRequest,
    AlertRuleResponse,
    NotificationRequest,
    NotificationResponse,
    AlertMetricsRequest,
    AlertMetricsResponse
)

logger = logging.getLogger(__name__)

class AlertState(str, Enum):
    """Alert states."""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    ESCALATED = "escalated"

class NotificationStatus(str, Enum):
    """Notification status."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"

@dataclass
class AlertContext:
    """Context information for alerts."""
    service_name: str
    environment: str
    region: str
    timestamp: datetime
    metadata: Dict[str, Any]

class ProductionAlertingService:
    """Service for comprehensive production alerting."""
    
    def __init__(self):
        self.initialized = False
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, AlertHistory] = {}
        self.notification_channels: Dict[str, AlertChannel] = {}
        self.escalation_policies: Dict[str, EscalationPolicy] = {}
        self.suppression_rules: Dict[str, SuppressionRule] = {}
        self.alert_templates: Dict[str, AlertTemplate] = {}
        
        # Service dependencies
        self.database = None
        self.production_monitoring_service = None
        self.notification_service = None
        
    async def initialize(self):
        """Initialize the production alerting service."""
        try:
            logger.info("Initializing Production Alerting Service...")
            
            # Initialize database connection
            self.database = await self._initialize_database()
            
            # Initialize service dependencies
            await self._initialize_service_dependencies()
            
            # Load alert configurations
            await self._load_alert_rules()
            await self._load_notification_channels()
            await self._load_escalation_policies()
            await self._load_suppression_rules()
            await self._load_alert_templates()
            
            # Start alert processing
            await self._start_alert_processing()
            
            self.initialized = True
            logger.info("Production Alerting Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Production Alerting Service: {str(e)}")
            raise
    
    async def cleanup(self):
        """Clean up service resources."""
        try:
            logger.info("Cleaning up Production Alerting Service...")
            
            # Stop alert processing
            await self._stop_alert_processing()
            
            # Close database connections
            if self.database:
                await self.database.close()
            
            logger.info("Production Alerting Service cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during Production Alerting Service cleanup: {str(e)}")
    
    async def _initialize_database(self):
        """Initialize database connection for alerting data."""
        # Database initialization logic
        return None
    
    async def _initialize_service_dependencies(self):
        """Initialize service dependencies."""
        # Initialize service dependencies
        self.production_monitoring_service = None
        self.notification_service = None
    
    async def _load_alert_rules(self):
        """Load alert rules from configuration."""
        # Default alert rules
        self.alert_rules = {
            "high_cpu_usage": AlertRule(
                rule_id="high_cpu_usage",
                name="High CPU Usage",
                description="Alert when CPU usage exceeds threshold",
                conditions=[
                    AlertCondition(
                        metric_name="cpu_usage_percent",
                        operator="greater_than",
                        threshold_value=80.0,
                        evaluation_window_minutes=5
                    )
                ],
                severity=AlertSeverity.HIGH,
                enabled=True,
                cooldown_minutes=15
            ),
            "high_memory_usage": AlertRule(
                rule_id="high_memory_usage",
                name="High Memory Usage",
                description="Alert when memory usage exceeds threshold",
                conditions=[
                    AlertCondition(
                        metric_name="memory_usage_percent",
                        operator="greater_than",
                        threshold_value=85.0,
                        evaluation_window_minutes=5
                    )
                ],
                severity=AlertSeverity.HIGH,
                enabled=True,
                cooldown_minutes=15
            ),
            "high_error_rate": AlertRule(
                rule_id="high_error_rate",
                name="High Error Rate",
                description="Alert when error rate exceeds threshold",
                conditions=[
                    AlertCondition(
                        metric_name="error_rate_percent",
                        operator="greater_than",
                        threshold_value=5.0,
                        evaluation_window_minutes=5
                    )
                ],
                severity=AlertSeverity.CRITICAL,
                enabled=True,
                cooldown_minutes=5
            ),
            "low_user_engagement": AlertRule(
                rule_id="low_user_engagement",
                name="Low User Engagement",
                description="Alert when user engagement drops below threshold",
                conditions=[
                    AlertCondition(
                        metric_name="daily_active_users",
                        operator="less_than",
                        threshold_value=20.0,
                        evaluation_window_minutes=60
                    )
                ],
                severity=AlertSeverity.MEDIUM,
                enabled=True,
                cooldown_minutes=60
            ),
            "low_recommendation_accuracy": AlertRule(
                rule_id="low_recommendation_accuracy",
                name="Low Recommendation Accuracy",
                description="Alert when recommendation accuracy drops below threshold",
                conditions=[
                    AlertCondition(
                        metric_name="recommendation_accuracy_percent",
                        operator="less_than",
                        threshold_value=80.0,
                        evaluation_window_minutes=30
                    )
                ],
                severity=AlertSeverity.HIGH,
                enabled=True,
                cooldown_minutes=30
            ),
            "database_connection_issues": AlertRule(
                rule_id="database_connection_issues",
                name="Database Connection Issues",
                description="Alert when database connection failures exceed threshold",
                conditions=[
                    AlertCondition(
                        metric_name="database_connection_failures",
                        operator="greater_than",
                        threshold_value=5.0,
                        evaluation_window_minutes=10
                    )
                ],
                severity=AlertSeverity.CRITICAL,
                enabled=True,
                cooldown_minutes=10
            )
        }
    
    async def _load_notification_channels(self):
        """Load notification channels."""
        self.notification_channels = {
            "email": AlertChannel(
                channel_id="email",
                channel_type=NotificationChannel.EMAIL,
                name="Email Notifications",
                configuration={
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "username": "alerts@drought-management.com",
                    "password": "encrypted_password",
                    "from_address": "alerts@drought-management.com",
                    "to_addresses": ["admin@drought-management.com", "ops@drought-management.com"]
                },
                enabled=True
            ),
            "slack": AlertChannel(
                channel_id="slack",
                channel_type=NotificationChannel.SLACK,
                name="Slack Notifications",
                configuration={
                    "webhook_url": "https://hooks.slack.com/services/...",
                    "channel": "#alerts",
                    "username": "Drought Management Alerts"
                },
                enabled=True
            ),
            "webhook": AlertChannel(
                channel_id="webhook",
                channel_type=NotificationChannel.WEBHOOK,
                name="Webhook Notifications",
                configuration={
                    "webhook_url": "https://monitoring.example.com/webhook",
                    "headers": {"Authorization": "Bearer token"},
                    "timeout_seconds": 30
                },
                enabled=True
            )
        }
    
    async def _load_escalation_policies(self):
        """Load escalation policies."""
        self.escalation_policies = {
            "critical_alerts": EscalationPolicy(
                policy_id="critical_alerts",
                name="Critical Alerts Escalation",
                description="Escalation policy for critical alerts",
                escalation_steps=[
                    {
                        "step": 1,
                        "delay_minutes": 0,
                        "channels": ["slack"],
                        "message_template": "critical_alert_template"
                    },
                    {
                        "step": 2,
                        "delay_minutes": 15,
                        "channels": ["email", "slack"],
                        "message_template": "critical_alert_escalation_template"
                    },
                    {
                        "step": 3,
                        "delay_minutes": 30,
                        "channels": ["email", "webhook"],
                        "message_template": "critical_alert_final_template"
                    }
                ],
                max_escalation_steps=3
            ),
            "high_alerts": EscalationPolicy(
                policy_id="high_alerts",
                name="High Priority Alerts Escalation",
                description="Escalation policy for high priority alerts",
                escalation_steps=[
                    {
                        "step": 1,
                        "delay_minutes": 0,
                        "channels": ["slack"],
                        "message_template": "high_alert_template"
                    },
                    {
                        "step": 2,
                        "delay_minutes": 30,
                        "channels": ["email"],
                        "message_template": "high_alert_escalation_template"
                    }
                ],
                max_escalation_steps=2
            )
        }
    
    async def _load_suppression_rules(self):
        """Load suppression rules."""
        self.suppression_rules = {
            "maintenance_window": SuppressionRule(
                rule_id="maintenance_window",
                name="Maintenance Window Suppression",
                description="Suppress alerts during maintenance windows",
                conditions={
                    "time_range": "02:00-04:00",
                    "days_of_week": ["sunday"],
                    "alert_types": ["high_cpu_usage", "high_memory_usage"]
                },
                enabled=True
            ),
            "weekend_suppression": SuppressionRule(
                rule_id="weekend_suppression",
                name="Weekend Suppression",
                description="Suppress non-critical alerts on weekends",
                conditions={
                    "days_of_week": ["saturday", "sunday"],
                    "alert_severities": ["low", "medium"]
                },
                enabled=True
            )
        }
    
    async def _load_alert_templates(self):
        """Load alert templates."""
        self.alert_templates = {
            "critical_alert_template": AlertTemplate(
                template_id="critical_alert_template",
                name="Critical Alert Template",
                subject="🚨 CRITICAL ALERT: {alert_name}",
                body="""
                **CRITICAL ALERT TRIGGERED**
                
                Alert: {alert_name}
                Severity: {severity}
                Time: {timestamp}
                Service: {service_name}
                
                Description: {description}
                
                Current Value: {current_value}
                Threshold: {threshold_value}
                
                Please investigate immediately.
                """,
                channel_type=NotificationChannel.SLACK
            ),
            "high_alert_template": AlertTemplate(
                template_id="high_alert_template",
                name="High Alert Template",
                subject="⚠️ HIGH PRIORITY ALERT: {alert_name}",
                body="""
                **HIGH PRIORITY ALERT**
                
                Alert: {alert_name}
                Severity: {severity}
                Time: {timestamp}
                
                Description: {description}
                
                Current Value: {current_value}
                Threshold: {threshold_value}
                
                Please review and take appropriate action.
                """,
                channel_type=NotificationChannel.SLACK
            ),
            "email_alert_template": AlertTemplate(
                template_id="email_alert_template",
                name="Email Alert Template",
                subject="Alert: {alert_name} - {severity}",
                body="""
                <h2>Alert Notification</h2>
                
                <p><strong>Alert:</strong> {alert_name}</p>
                <p><strong>Severity:</strong> {severity}</p>
                <p><strong>Time:</strong> {timestamp}</p>
                <p><strong>Service:</strong> {service_name}</p>
                
                <p><strong>Description:</strong> {description}</p>
                
                <p><strong>Current Value:</strong> {current_value}</p>
                <p><strong>Threshold:</strong> {threshold_value}</p>
                
                <p>Please investigate and take appropriate action.</p>
                """,
                channel_type=NotificationChannel.EMAIL
            )
        }
    
    async def _start_alert_processing(self):
        """Start alert processing loop."""
        # Start background task for alert processing
        asyncio.create_task(self._alert_processing_loop())
        logger.info("Started alert processing loop")
    
    async def _stop_alert_processing(self):
        """Stop alert processing loop."""
        # Stop background task
        logger.info("Stopped alert processing loop")
    
    async def _alert_processing_loop(self):
        """Main alert processing loop."""
        while True:
            try:
                # Process alerts every 30 seconds
                await self._process_alerts()
                await asyncio.sleep(30)
            except Exception as e:
                logger.error(f"Error in alert processing loop: {str(e)}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _process_alerts(self):
        """Process all active alert rules."""
        try:
            for rule_id, rule in self.alert_rules.items():
                if not rule.enabled:
                    continue
                
                # Check if rule is in cooldown
                if await self._is_rule_in_cooldown(rule_id):
                    continue
                
                # Evaluate rule conditions
                if await self._evaluate_rule_conditions(rule):
                    await self._trigger_alert(rule)
                    
        except Exception as e:
            logger.error(f"Error processing alerts: {str(e)}")
    
    async def _is_rule_in_cooldown(self, rule_id: str) -> bool:
        """Check if alert rule is in cooldown period."""
        # Check if there's a recent alert for this rule
        recent_alerts = [
            alert for alert in self.active_alerts.values()
            if (alert.rule_id == rule_id and 
                alert.status == AlertStatus.ACTIVE and
                datetime.utcnow() - alert.triggered_at < timedelta(minutes=15))  # Default cooldown
        ]
        return len(recent_alerts) > 0
    
    async def _evaluate_rule_conditions(self, rule: AlertRule) -> bool:
        """Evaluate alert rule conditions."""
        try:
            # This would integrate with the production monitoring service
            # For now, simulate condition evaluation
            
            for condition in rule.conditions:
                # Simulate metric value retrieval
                current_value = await self._get_current_metric_value(condition.metric_name)
                
                # Evaluate condition
                condition_met = False
                if condition.operator == "greater_than" and current_value > condition.threshold_value:
                    condition_met = True
                elif condition.operator == "less_than" and current_value < condition.threshold_value:
                    condition_met = True
                elif condition.operator == "equals" and current_value == condition.threshold_value:
                    condition_met = True
                
                if not condition_met:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error evaluating rule conditions: {str(e)}")
            return False
    
    async def _get_current_metric_value(self, metric_name: str) -> float:
        """Get current metric value."""
        # This would integrate with the production monitoring service
        # For now, simulate metric values
        import random
        
        simulated_values = {
            "cpu_usage_percent": random.uniform(20, 90),
            "memory_usage_percent": random.uniform(30, 95),
            "error_rate_percent": random.uniform(0, 10),
            "daily_active_users": random.uniform(10, 100),
            "recommendation_accuracy_percent": random.uniform(70, 95),
            "database_connection_failures": random.uniform(0, 10)
        }
        
        return simulated_values.get(metric_name, 0.0)
    
    async def _trigger_alert(self, rule: AlertRule):
        """Trigger an alert for a rule."""
        try:
            # Create alert history entry
            alert_id = str(uuid4())
            alert_history = AlertHistory(
                alert_id=alert_id,
                rule_id=rule.rule_id,
                alert_name=rule.name,
                severity=rule.severity,
                status=AlertStatus.ACTIVE,
                triggered_at=datetime.utcnow(),
                description=rule.description,
                conditions_met=rule.conditions,
                current_values=await self._get_current_values_for_rule(rule),
                acknowledged=False,
                resolved=False
            )
            
            # Store alert
            self.active_alerts[alert_id] = alert_history
            
            # Check suppression rules
            if await self._is_alert_suppressed(alert_history):
                alert_history.status = AlertStatus.SUPPRESSED
                logger.info(f"Alert {alert_id} suppressed by suppression rule")
                return
            
            # Send notifications
            await self._send_alert_notifications(alert_history)
            
            # Start escalation if configured
            await self._start_escalation(alert_history)
            
            logger.info(f"Alert triggered: {rule.name} (ID: {alert_id})")
            
        except Exception as e:
            logger.error(f"Error triggering alert: {str(e)}")
    
    async def _get_current_values_for_rule(self, rule: AlertRule) -> Dict[str, float]:
        """Get current values for all metrics in a rule."""
        values = {}
        for condition in rule.conditions:
            values[condition.metric_name] = await self._get_current_metric_value(condition.metric_name)
        return values
    
    async def _is_alert_suppressed(self, alert: AlertHistory) -> bool:
        """Check if alert should be suppressed."""
        try:
            current_time = datetime.utcnow()
            day_of_week = current_time.strftime('%A').lower()
            hour = current_time.hour
            
            for rule_id, suppression_rule in self.suppression_rules.items():
                if not suppression_rule.enabled:
                    continue
                
                conditions = suppression_rule.conditions
                
                # Check day of week suppression
                if "days_of_week" in conditions:
                    if day_of_week in conditions["days_of_week"]:
                        # Check if alert type matches
                        if "alert_types" in conditions:
                            if alert.rule_id in conditions["alert_types"]:
                                return True
                        # Check if severity matches
                        elif "alert_severities" in conditions:
                            if alert.severity.value in conditions["alert_severities"]:
                                return True
                
                # Check time range suppression
                if "time_range" in conditions:
                    time_range = conditions["time_range"]
                    start_hour, end_hour = map(int, time_range.split('-'))
                    if start_hour <= hour <= end_hour:
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking alert suppression: {str(e)}")
            return False
    
    async def _send_alert_notifications(self, alert: AlertHistory):
        """Send alert notifications."""
        try:
            # Determine notification channels based on severity
            channels = self._get_notification_channels_for_severity(alert.severity)
            
            for channel_id in channels:
                channel = self.notification_channels.get(channel_id)
                if not channel or not channel.enabled:
                    continue
                
                # Get appropriate template
                template = self._get_template_for_channel(channel.channel_type, alert.severity)
                
                # Format notification
                notification = await self._format_notification(alert, template, channel)
                
                # Send notification
                await self._send_notification(notification, channel)
                
        except Exception as e:
            logger.error(f"Error sending alert notifications: {str(e)}")
    
    def _get_notification_channels_for_severity(self, severity: AlertSeverity) -> List[str]:
        """Get notification channels for alert severity."""
        channel_mapping = {
            AlertSeverity.CRITICAL: ["slack", "email", "webhook"],
            AlertSeverity.HIGH: ["slack", "email"],
            AlertSeverity.MEDIUM: ["slack"],
            AlertSeverity.LOW: ["slack"]
        }
        return channel_mapping.get(severity, ["slack"])
    
    def _get_template_for_channel(self, channel_type: NotificationChannel, severity: AlertSeverity) -> AlertTemplate:
        """Get appropriate template for channel and severity."""
        if channel_type == NotificationChannel.EMAIL:
            return self.alert_templates["email_alert_template"]
        elif severity == AlertSeverity.CRITICAL:
            return self.alert_templates["critical_alert_template"]
        else:
            return self.alert_templates["high_alert_template"]
    
    async def _format_notification(self, alert: AlertHistory, template: AlertTemplate, channel: AlertChannel) -> AlertNotification:
        """Format alert notification."""
        # Format template variables
        template_vars = {
            "alert_name": alert.alert_name,
            "severity": alert.severity.value,
            "timestamp": alert.triggered_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "service_name": "Drought Management Service",
            "description": alert.description,
            "current_value": alert.current_values.get(list(alert.current_values.keys())[0], 0),
            "threshold_value": alert.conditions_met[0].threshold_value if alert.conditions_met else 0
        }
        
        # Format subject and body
        subject = template.subject.format(**template_vars)
        body = template.body.format(**template_vars)
        
        return AlertNotification(
            notification_id=str(uuid4()),
            alert_id=alert.alert_id,
            channel_id=channel.channel_id,
            channel_type=channel.channel_type,
            subject=subject,
            body=body,
            status=NotificationStatus.PENDING,
            created_at=datetime.utcnow()
        )
    
    async def _send_notification(self, notification: AlertNotification, channel: AlertChannel):
        """Send notification through channel."""
        try:
            # This would integrate with actual notification services
            # For now, simulate sending
            
            logger.info(f"Sending notification via {channel.channel_type.value}: {notification.subject}")
            
            # Simulate sending delay
            await asyncio.sleep(0.1)
            
            # Mark as sent
            notification.status = NotificationStatus.SENT
            
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            notification.status = NotificationStatus.FAILED
    
    async def _start_escalation(self, alert: AlertHistory):
        """Start escalation process for alert."""
        try:
            # Get escalation policy for severity
            policy_id = self._get_escalation_policy_for_severity(alert.severity)
            if not policy_id:
                return
            
            policy = self.escalation_policies.get(policy_id)
            if not policy:
                return
            
            # Schedule escalation steps
            for step in policy.escalation_steps:
                delay_seconds = step["delay_minutes"] * 60
                asyncio.create_task(self._execute_escalation_step(alert, step, delay_seconds))
                
        except Exception as e:
            logger.error(f"Error starting escalation: {str(e)}")
    
    def _get_escalation_policy_for_severity(self, severity: AlertSeverity) -> Optional[str]:
        """Get escalation policy for alert severity."""
        policy_mapping = {
            AlertSeverity.CRITICAL: "critical_alerts",
            AlertSeverity.HIGH: "high_alerts",
            AlertSeverity.MEDIUM: "high_alerts",
            AlertSeverity.LOW: None
        }
        return policy_mapping.get(severity)
    
    async def _execute_escalation_step(self, alert: AlertHistory, step: Dict[str, Any], delay_seconds: int):
        """Execute escalation step after delay."""
        try:
            # Wait for delay
            await asyncio.sleep(delay_seconds)
            
            # Check if alert is still active
            if alert.status != AlertStatus.ACTIVE:
                return
            
            # Send escalated notifications
            channels = step["channels"]
            template_id = step["message_template"]
            
            for channel_id in channels:
                channel = self.notification_channels.get(channel_id)
                if not channel or not channel.enabled:
                    continue
                
                template = self.alert_templates.get(template_id)
                if not template:
                    continue
                
                notification = await self._format_notification(alert, template, channel)
                await self._send_notification(notification, channel)
            
            logger.info(f"Executed escalation step {step['step']} for alert {alert.alert_id}")
            
        except Exception as e:
            logger.error(f"Error executing escalation step: {str(e)}")
    
    # Public API methods
    async def create_alert_rule(self, rule_request: AlertRuleRequest) -> AlertRuleResponse:
        """Create a new alert rule."""
        try:
            logger.info(f"Creating alert rule: {rule_request.name}")
            
            # Validate rule
            if not await self._validate_alert_rule(rule_request):
                return AlertRuleResponse(
                    success=False,
                    rule_id=None,
                    errors=["Invalid alert rule configuration"]
                )
            
            # Create rule
            rule_id = str(uuid4())
            rule = AlertRule(
                rule_id=rule_id,
                name=rule_request.name,
                description=rule_request.description,
                conditions=rule_request.conditions,
                severity=rule_request.severity,
                enabled=rule_request.enabled,
                cooldown_minutes=rule_request.cooldown_minutes
            )
            
            # Store rule
            self.alert_rules[rule_id] = rule
            
            logger.info(f"Alert rule created: {rule_id}")
            return AlertRuleResponse(
                success=True,
                rule_id=rule_id,
                errors=[]
            )
            
        except Exception as e:
            logger.error(f"Error creating alert rule: {str(e)}")
            return AlertRuleResponse(
                success=False,
                rule_id=None,
                errors=[str(e)]
            )
    
    async def _validate_alert_rule(self, rule_request: AlertRuleRequest) -> bool:
        """Validate alert rule configuration."""
        try:
            # Check required fields
            if not rule_request.name or not rule_request.conditions:
                return False
            
            # Validate conditions
            for condition in rule_request.conditions:
                if not condition.metric_name or not condition.operator:
                    return False
                if condition.threshold_value is None:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating alert rule: {str(e)}")
            return False
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert."""
        try:
            alert = self.active_alerts.get(alert_id)
            if not alert:
                return False
            
            alert.acknowledged = True
            alert.acknowledged_by = acknowledged_by
            alert.acknowledged_at = datetime.utcnow()
            
            logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
            return True
            
        except Exception as e:
            logger.error(f"Error acknowledging alert: {str(e)}")
            return False
    
    async def resolve_alert(self, alert_id: str, resolved_by: str) -> bool:
        """Resolve an alert."""
        try:
            alert = self.active_alerts.get(alert_id)
            if not alert:
                return False
            
            alert.resolved = True
            alert.resolved_by = resolved_by
            alert.resolved_at = datetime.utcnow()
            alert.status = AlertStatus.RESOLVED
            
            logger.info(f"Alert {alert_id} resolved by {resolved_by}")
            return True
            
        except Exception as e:
            logger.error(f"Error resolving alert: {str(e)}")
            return False
    
    async def get_active_alerts(self) -> List[AlertHistory]:
        """Get all active alerts."""
        return [
            alert for alert in self.active_alerts.values()
            if alert.status == AlertStatus.ACTIVE
        ]
    
    async def get_alert_metrics(self, request: AlertMetricsRequest) -> AlertMetricsResponse:
        """Get alert metrics."""
        try:
            # Calculate metrics
            total_alerts = len(self.active_alerts)
            active_alerts = len([a for a in self.active_alerts.values() if a.status == AlertStatus.ACTIVE])
            acknowledged_alerts = len([a for a in self.active_alerts.values() if a.acknowledged])
            resolved_alerts = len([a for a in self.active_alerts.values() if a.resolved])
            
            # Calculate by severity
            severity_counts = {}
            for alert in self.active_alerts.values():
                severity = alert.severity.value
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # Calculate by rule
            rule_counts = {}
            for alert in self.active_alerts.values():
                rule_id = alert.rule_id
                rule_counts[rule_id] = rule_counts.get(rule_id, 0) + 1
            
            metrics = AlertMetrics(
                total_alerts=total_alerts,
                active_alerts=active_alerts,
                acknowledged_alerts=acknowledged_alerts,
                resolved_alerts=resolved_alerts,
                severity_distribution=severity_counts,
                rule_distribution=rule_counts,
                generated_at=datetime.utcnow()
            )
            
            return AlertMetricsResponse(
                metrics=metrics,
                success=True,
                errors=[]
            )
            
        except Exception as e:
            logger.error(f"Error getting alert metrics: {str(e)}")
            return AlertMetricsResponse(
                metrics=None,
                success=False,
                errors=[str(e)]
            )
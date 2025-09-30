"""
Production Monitoring Service

Comprehensive production monitoring system for drought management service.
Monitors system performance, user engagement, recommendation effectiveness,
and provides real-time health metrics and alerting capabilities.
"""

import logging
import asyncio
import time
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from uuid import UUID, uuid4
from decimal import Decimal
import statistics
from collections import defaultdict, deque
from enum import Enum
import json
import psutil
import sys
from dataclasses import dataclass, asdict

from ..models.production_monitoring_models import (
    SystemPerformanceMetrics,
    UserEngagementMetrics,
    RecommendationEffectivenessMetrics,
    ProductionHealthStatus,
    AlertConfiguration,
    ProductionAlert,
    PerformanceThreshold,
    MonitoringConfiguration,
    SystemResourceUsage,
    ServiceHealthStatus,
    DatabaseHealthStatus,
    ExternalServiceHealthStatus,
    ProductionMonitoringReport,
    RealTimeMetrics,
    HistoricalMetrics,
    PerformanceTrend,
    UserActivityMetrics,
    RecommendationMetrics,
    AgriculturalImpactMetrics
)

logger = logging.getLogger(__name__)

class AlertSeverity(str, Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class MetricType(str, Enum):
    """Types of metrics being monitored."""
    SYSTEM_PERFORMANCE = "system_performance"
    USER_ENGAGEMENT = "user_engagement"
    RECOMMENDATION_EFFECTIVENESS = "recommendation_effectiveness"
    AGRICULTURAL_IMPACT = "agricultural_impact"
    DATABASE_HEALTH = "database_health"
    EXTERNAL_SERVICE_HEALTH = "external_service_health"

@dataclass
class MetricSnapshot:
    """Snapshot of a metric at a specific point in time."""
    metric_name: str
    metric_type: MetricType
    value: float
    timestamp: datetime
    metadata: Dict[str, Any] = None

class ProductionMonitoringService:
    """Service for comprehensive production monitoring and analytics."""
    
    def __init__(self):
        self.initialized = False
        self.metrics_buffer: deque = deque(maxlen=10000)  # Circular buffer for recent metrics
        self.alert_configurations: Dict[str, AlertConfiguration] = {}
        self.performance_thresholds: Dict[str, PerformanceThreshold] = {}
        self.monitoring_config: MonitoringConfiguration = None
        self.health_status: ProductionHealthStatus = None
        self.metrics_collection_active = False
        self.collection_task: Optional[asyncio.Task] = None
        
        # Service dependencies
        self.database = None
        self.drought_assessment_service = None
        self.monitoring_dashboard_service = None
        self.alert_service = None
        
    async def initialize(self):
        """Initialize the production monitoring service."""
        try:
            logger.info("Initializing Production Monitoring Service...")
            
            # Initialize database connection
            self.database = await self._initialize_database()
            
            # Initialize monitoring configuration
            await self._load_monitoring_configuration()
            
            # Initialize alert configurations
            await self._load_alert_configurations()
            
            # Initialize performance thresholds
            await self._load_performance_thresholds()
            
            # Initialize service dependencies
            await self._initialize_service_dependencies()
            
            # Start metrics collection
            await self._start_metrics_collection()
            
            self.initialized = True
            logger.info("Production Monitoring Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Production Monitoring Service: {str(e)}")
            raise
    
    async def cleanup(self):
        """Clean up service resources."""
        try:
            logger.info("Cleaning up Production Monitoring Service...")
            
            # Stop metrics collection
            await self._stop_metrics_collection()
            
            # Close database connections
            if self.database:
                await self.database.close()
            
            logger.info("Production Monitoring Service cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during Production Monitoring Service cleanup: {str(e)}")
    
    async def _initialize_database(self):
        """Initialize database connection for monitoring data."""
        # Database initialization logic
        return None
    
    async def _load_monitoring_configuration(self):
        """Load monitoring configuration."""
        self.monitoring_config = MonitoringConfiguration(
            collection_interval_seconds=60,
            retention_days=90,
            alert_cooldown_minutes=15,
            metrics_buffer_size=10000,
            enable_real_time_alerts=True,
            enable_performance_tracking=True,
            enable_user_engagement_tracking=True,
            enable_recommendation_tracking=True,
            enable_agricultural_impact_tracking=True
        )
    
    async def _load_alert_configurations(self):
        """Load alert configurations."""
        self.alert_configurations = {
            "high_response_time": AlertConfiguration(
                alert_id="high_response_time",
                metric_name="average_response_time_ms",
                threshold_value=3000.0,
                comparison_operator="greater_than",
                severity=AlertSeverity.HIGH,
                enabled=True,
                cooldown_minutes=15
            ),
            "low_user_engagement": AlertConfiguration(
                alert_id="low_user_engagement",
                metric_name="daily_active_users",
                threshold_value=10.0,
                comparison_operator="less_than",
                severity=AlertSeverity.MEDIUM,
                enabled=True,
                cooldown_minutes=60
            ),
            "high_error_rate": AlertConfiguration(
                alert_id="high_error_rate",
                metric_name="error_rate_percent",
                threshold_value=5.0,
                comparison_operator="greater_than",
                severity=AlertSeverity.CRITICAL,
                enabled=True,
                cooldown_minutes=5
            ),
            "low_recommendation_accuracy": AlertConfiguration(
                alert_id="low_recommendation_accuracy",
                metric_name="recommendation_accuracy_percent",
                threshold_value=80.0,
                comparison_operator="less_than",
                severity=AlertSeverity.HIGH,
                enabled=True,
                cooldown_minutes=30
            ),
            "database_connection_issues": AlertConfiguration(
                alert_id="database_connection_issues",
                metric_name="database_connection_failures",
                threshold_value=5.0,
                comparison_operator="greater_than",
                severity=AlertSeverity.CRITICAL,
                enabled=True,
                cooldown_minutes=10
            )
        }
    
    async def _load_performance_thresholds(self):
        """Load performance thresholds."""
        self.performance_thresholds = {
            "response_time": PerformanceThreshold(
                metric_name="response_time_ms",
                warning_threshold=2000.0,
                critical_threshold=5000.0,
                target_value=1000.0
            ),
            "cpu_usage": PerformanceThreshold(
                metric_name="cpu_usage_percent",
                warning_threshold=70.0,
                critical_threshold=90.0,
                target_value=50.0
            ),
            "memory_usage": PerformanceThreshold(
                metric_name="memory_usage_percent",
                warning_threshold=80.0,
                critical_threshold=95.0,
                target_value=60.0
            ),
            "disk_usage": PerformanceThreshold(
                metric_name="disk_usage_percent",
                warning_threshold=85.0,
                critical_threshold=95.0,
                target_value=70.0
            )
        }
    
    async def _initialize_service_dependencies(self):
        """Initialize service dependencies."""
        # Initialize service dependencies
        self.drought_assessment_service = None
        self.monitoring_dashboard_service = None
        self.alert_service = None
    
    async def _start_metrics_collection(self):
        """Start continuous metrics collection."""
        if self.metrics_collection_active:
            return
        
        self.metrics_collection_active = True
        self.collection_task = asyncio.create_task(self._collect_metrics_continuously())
        logger.info("Started continuous metrics collection")
    
    async def _stop_metrics_collection(self):
        """Stop continuous metrics collection."""
        if not self.metrics_collection_active:
            return
        
        self.metrics_collection_active = False
        if self.collection_task:
            self.collection_task.cancel()
            try:
                await self.collection_task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped continuous metrics collection")
    
    async def _collect_metrics_continuously(self):
        """Continuously collect metrics."""
        while self.metrics_collection_active:
            try:
                # Collect system performance metrics
                await self._collect_system_performance_metrics()
                
                # Collect user engagement metrics
                await self._collect_user_engagement_metrics()
                
                # Collect recommendation effectiveness metrics
                await self._collect_recommendation_effectiveness_metrics()
                
                # Collect agricultural impact metrics
                await self._collect_agricultural_impact_metrics()
                
                # Check for alerts
                await self._check_alerts()
                
                # Wait for next collection interval
                await asyncio.sleep(self.monitoring_config.collection_interval_seconds)
                
            except Exception as e:
                logger.error(f"Error during metrics collection: {str(e)}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _collect_system_performance_metrics(self):
        """Collect system performance metrics."""
        try:
            timestamp = datetime.utcnow()
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self._add_metric_snapshot("cpu_usage_percent", MetricType.SYSTEM_PERFORMANCE, cpu_percent, timestamp)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self._add_metric_snapshot("memory_usage_percent", MetricType.SYSTEM_PERFORMANCE, memory.percent, timestamp)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self._add_metric_snapshot("disk_usage_percent", MetricType.SYSTEM_PERFORMANCE, disk_percent, timestamp)
            
            # Network I/O
            network = psutil.net_io_counters()
            self._add_metric_snapshot("network_bytes_sent", MetricType.SYSTEM_PERFORMANCE, network.bytes_sent, timestamp)
            self._add_metric_snapshot("network_bytes_received", MetricType.SYSTEM_PERFORMANCE, network.bytes_recv, timestamp)
            
            # Process count
            process_count = len(psutil.pids())
            self._add_metric_snapshot("process_count", MetricType.SYSTEM_PERFORMANCE, process_count, timestamp)
            
            # Python memory usage
            import gc
            gc.collect()
            python_memory = sys.getsizeof(gc.get_objects())
            self._add_metric_snapshot("python_memory_bytes", MetricType.SYSTEM_PERFORMANCE, python_memory, timestamp)
            
        except Exception as e:
            logger.error(f"Error collecting system performance metrics: {str(e)}")
    
    async def _collect_user_engagement_metrics(self):
        """Collect user engagement metrics."""
        try:
            timestamp = datetime.utcnow()
            
            # Simulate user engagement metrics collection
            # In production, this would query actual user activity data
            
            # Daily active users (simulated)
            daily_active_users = await self._get_daily_active_users()
            self._add_metric_snapshot("daily_active_users", MetricType.USER_ENGAGEMENT, daily_active_users, timestamp)
            
            # Session duration (simulated)
            avg_session_duration = await self._get_average_session_duration()
            self._add_metric_snapshot("avg_session_duration_minutes", MetricType.USER_ENGAGEMENT, avg_session_duration, timestamp)
            
            # API requests per minute
            requests_per_minute = await self._get_requests_per_minute()
            self._add_metric_snapshot("requests_per_minute", MetricType.USER_ENGAGEMENT, requests_per_minute, timestamp)
            
            # Feature usage
            feature_usage = await self._get_feature_usage_stats()
            for feature, usage_count in feature_usage.items():
                self._add_metric_snapshot(f"feature_usage_{feature}", MetricType.USER_ENGAGEMENT, usage_count, timestamp)
            
        except Exception as e:
            logger.error(f"Error collecting user engagement metrics: {str(e)}")
    
    async def _collect_recommendation_effectiveness_metrics(self):
        """Collect recommendation effectiveness metrics."""
        try:
            timestamp = datetime.utcnow()
            
            # Recommendation accuracy (simulated)
            recommendation_accuracy = await self._get_recommendation_accuracy()
            self._add_metric_snapshot("recommendation_accuracy_percent", MetricType.RECOMMENDATION_EFFECTIVENESS, recommendation_accuracy, timestamp)
            
            # Recommendations per day
            recommendations_per_day = await self._get_recommendations_per_day()
            self._add_metric_snapshot("recommendations_per_day", MetricType.RECOMMENDATION_EFFECTIVENESS, recommendations_per_day, timestamp)
            
            # User satisfaction score
            user_satisfaction = await self._get_user_satisfaction_score()
            self._add_metric_snapshot("user_satisfaction_score", MetricType.RECOMMENDATION_EFFECTIVENESS, user_satisfaction, timestamp)
            
            # Implementation rate
            implementation_rate = await self._get_recommendation_implementation_rate()
            self._add_metric_snapshot("recommendation_implementation_rate", MetricType.RECOMMENDATION_EFFECTIVENESS, implementation_rate, timestamp)
            
        except Exception as e:
            logger.error(f"Error collecting recommendation effectiveness metrics: {str(e)}")
    
    async def _collect_agricultural_impact_metrics(self):
        """Collect agricultural impact metrics."""
        try:
            timestamp = datetime.utcnow()
            
            # Water savings achieved
            water_savings = await self._get_total_water_savings()
            self._add_metric_snapshot("total_water_savings_gallons", MetricType.AGRICULTURAL_IMPACT, water_savings, timestamp)
            
            # Farms using conservation practices
            farms_with_conservation = await self._get_farms_with_conservation_practices()
            self._add_metric_snapshot("farms_with_conservation_practices", MetricType.AGRICULTURAL_IMPACT, farms_with_conservation, timestamp)
            
            # Drought risk reduction
            drought_risk_reduction = await self._get_drought_risk_reduction()
            self._add_metric_snapshot("drought_risk_reduction_percent", MetricType.AGRICULTURAL_IMPACT, drought_risk_reduction, timestamp)
            
            # Cost savings achieved
            cost_savings = await self._get_total_cost_savings()
            self._add_metric_snapshot("total_cost_savings_dollars", MetricType.AGRICULTURAL_IMPACT, cost_savings, timestamp)
            
        except Exception as e:
            logger.error(f"Error collecting agricultural impact metrics: {str(e)}")
    
    def _add_metric_snapshot(self, metric_name: str, metric_type: MetricType, value: float, timestamp: datetime, metadata: Dict[str, Any] = None):
        """Add a metric snapshot to the buffer."""
        snapshot = MetricSnapshot(
            metric_name=metric_name,
            metric_type=metric_type,
            value=value,
            timestamp=timestamp,
            metadata=metadata or {}
        )
        self.metrics_buffer.append(snapshot)
    
    async def _check_alerts(self):
        """Check for alert conditions."""
        try:
            for alert_id, alert_config in self.alert_configurations.items():
                if not alert_config.enabled:
                    continue
                
                # Get recent metric values
                recent_values = self._get_recent_metric_values(alert_config.metric_name, minutes=5)
                if not recent_values:
                    continue
                
                # Calculate average value
                avg_value = statistics.mean(recent_values)
                
                # Check threshold
                alert_triggered = False
                if alert_config.comparison_operator == "greater_than" and avg_value > alert_config.threshold_value:
                    alert_triggered = True
                elif alert_config.comparison_operator == "less_than" and avg_value < alert_config.threshold_value:
                    alert_triggered = True
                
                if alert_triggered:
                    await self._trigger_alert(alert_config, avg_value)
                    
        except Exception as e:
            logger.error(f"Error checking alerts: {str(e)}")
    
    def _get_recent_metric_values(self, metric_name: str, minutes: int = 5) -> List[float]:
        """Get recent metric values for a specific metric."""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        values = []
        
        for snapshot in self.metrics_buffer:
            if (snapshot.metric_name == metric_name and 
                snapshot.timestamp >= cutoff_time):
                values.append(snapshot.value)
        
        return values
    
    async def _trigger_alert(self, alert_config: AlertConfiguration, current_value: float):
        """Trigger an alert."""
        try:
            alert = ProductionAlert(
                alert_id=uuid4(),
                alert_type=alert_config.alert_id,
                severity=alert_config.severity.value,
                message=f"{alert_config.metric_name} is {current_value:.2f} (threshold: {alert_config.threshold_value})",
                metric_name=alert_config.metric_name,
                current_value=current_value,
                threshold_value=alert_config.threshold_value,
                triggered_at=datetime.utcnow(),
                acknowledged=False
            )
            
            # Store alert
            await self._store_alert(alert)
            
            # Send notification (if configured)
            await self._send_alert_notification(alert)
            
            logger.warning(f"Alert triggered: {alert_config.alert_id} - {alert.message}")
            
        except Exception as e:
            logger.error(f"Error triggering alert: {str(e)}")
    
    async def _store_alert(self, alert: ProductionAlert):
        """Store alert in database."""
        # Database storage logic
        pass
    
    async def _send_alert_notification(self, alert: ProductionAlert):
        """Send alert notification."""
        # Notification logic (email, Slack, etc.)
        pass
    
    # Simulated data collection methods (in production, these would query actual data)
    async def _get_daily_active_users(self) -> float:
        """Get daily active users count."""
        # Simulate daily active users
        import random
        return random.uniform(50, 200)
    
    async def _get_average_session_duration(self) -> float:
        """Get average session duration in minutes."""
        import random
        return random.uniform(15, 45)
    
    async def _get_requests_per_minute(self) -> float:
        """Get requests per minute."""
        import random
        return random.uniform(10, 100)
    
    async def _get_feature_usage_stats(self) -> Dict[str, float]:
        """Get feature usage statistics."""
        import random
        return {
            "drought_assessment": random.uniform(20, 80),
            "water_savings": random.uniform(15, 60),
            "irrigation_optimization": random.uniform(10, 50),
            "soil_monitoring": random.uniform(25, 70)
        }
    
    async def _get_recommendation_accuracy(self) -> float:
        """Get recommendation accuracy percentage."""
        import random
        return random.uniform(75, 95)
    
    async def _get_recommendations_per_day(self) -> float:
        """Get recommendations generated per day."""
        import random
        return random.uniform(100, 500)
    
    async def _get_user_satisfaction_score(self) -> float:
        """Get user satisfaction score."""
        import random
        return random.uniform(3.5, 4.8)
    
    async def _get_recommendation_implementation_rate(self) -> float:
        """Get recommendation implementation rate."""
        import random
        return random.uniform(60, 85)
    
    async def _get_total_water_savings(self) -> float:
        """Get total water savings in gallons."""
        import random
        return random.uniform(10000, 100000)
    
    async def _get_farms_with_conservation_practices(self) -> float:
        """Get number of farms using conservation practices."""
        import random
        return random.uniform(50, 150)
    
    async def _get_drought_risk_reduction(self) -> float:
        """Get drought risk reduction percentage."""
        import random
        return random.uniform(15, 40)
    
    async def _get_total_cost_savings(self) -> float:
        """Get total cost savings in dollars."""
        import random
        return random.uniform(50000, 500000)
    
    # Public API methods
    async def get_system_performance_metrics(self, time_range_hours: int = 24) -> SystemPerformanceMetrics:
        """Get system performance metrics."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=time_range_hours)
            
            # Filter metrics by time range and type
            performance_metrics = [
                snapshot for snapshot in self.metrics_buffer
                if (snapshot.metric_type == MetricType.SYSTEM_PERFORMANCE and 
                    snapshot.timestamp >= cutoff_time)
            ]
            
            # Calculate metrics
            cpu_values = [m.value for m in performance_metrics if m.metric_name == "cpu_usage_percent"]
            memory_values = [m.value for m in performance_metrics if m.metric_name == "memory_usage_percent"]
            disk_values = [m.value for m in performance_metrics if m.metric_name == "disk_usage_percent"]
            
            return SystemPerformanceMetrics(
                cpu_usage_percent=statistics.mean(cpu_values) if cpu_values else 0.0,
                memory_usage_percent=statistics.mean(memory_values) if memory_values else 0.0,
                disk_usage_percent=statistics.mean(disk_values) if disk_values else 0.0,
                network_bytes_sent=sum(m.value for m in performance_metrics if m.metric_name == "network_bytes_sent"),
                network_bytes_received=sum(m.value for m in performance_metrics if m.metric_name == "network_bytes_received"),
                process_count=statistics.mean([m.value for m in performance_metrics if m.metric_name == "process_count"]) if performance_metrics else 0.0,
                python_memory_bytes=statistics.mean([m.value for m in performance_metrics if m.metric_name == "python_memory_bytes"]) if performance_metrics else 0.0,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error getting system performance metrics: {str(e)}")
            raise
    
    async def get_user_engagement_metrics(self, time_range_hours: int = 24) -> UserEngagementMetrics:
        """Get user engagement metrics."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=time_range_hours)
            
            # Filter metrics by time range and type
            engagement_metrics = [
                snapshot for snapshot in self.metrics_buffer
                if (snapshot.metric_type == MetricType.USER_ENGAGEMENT and 
                    snapshot.timestamp >= cutoff_time)
            ]
            
            # Calculate metrics
            daily_users = [m.value for m in engagement_metrics if m.metric_name == "daily_active_users"]
            session_duration = [m.value for m in engagement_metrics if m.metric_name == "avg_session_duration_minutes"]
            requests_per_minute = [m.value for m in engagement_metrics if m.metric_name == "requests_per_minute"]
            
            return UserEngagementMetrics(
                daily_active_users=statistics.mean(daily_users) if daily_users else 0.0,
                avg_session_duration_minutes=statistics.mean(session_duration) if session_duration else 0.0,
                requests_per_minute=statistics.mean(requests_per_minute) if requests_per_minute else 0.0,
                feature_usage_stats=self._get_latest_feature_usage(),
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error getting user engagement metrics: {str(e)}")
            raise
    
    async def get_recommendation_effectiveness_metrics(self, time_range_hours: int = 24) -> RecommendationEffectivenessMetrics:
        """Get recommendation effectiveness metrics."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=time_range_hours)
            
            # Filter metrics by time range and type
            effectiveness_metrics = [
                snapshot for snapshot in self.metrics_buffer
                if (snapshot.metric_type == MetricType.RECOMMENDATION_EFFECTIVENESS and 
                    snapshot.timestamp >= cutoff_time)
            ]
            
            # Calculate metrics
            accuracy = [m.value for m in effectiveness_metrics if m.metric_name == "recommendation_accuracy_percent"]
            recommendations_per_day = [m.value for m in effectiveness_metrics if m.metric_name == "recommendations_per_day"]
            satisfaction = [m.value for m in effectiveness_metrics if m.metric_name == "user_satisfaction_score"]
            implementation_rate = [m.value for m in effectiveness_metrics if m.metric_name == "recommendation_implementation_rate"]
            
            return RecommendationEffectivenessMetrics(
                recommendation_accuracy_percent=statistics.mean(accuracy) if accuracy else 0.0,
                recommendations_per_day=statistics.mean(recommendations_per_day) if recommendations_per_day else 0.0,
                user_satisfaction_score=statistics.mean(satisfaction) if satisfaction else 0.0,
                implementation_rate_percent=statistics.mean(implementation_rate) if implementation_rate else 0.0,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error getting recommendation effectiveness metrics: {str(e)}")
            raise
    
    async def get_agricultural_impact_metrics(self, time_range_hours: int = 24) -> AgriculturalImpactMetrics:
        """Get agricultural impact metrics."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=time_range_hours)
            
            # Filter metrics by time range and type
            impact_metrics = [
                snapshot for snapshot in self.metrics_buffer
                if (snapshot.metric_type == MetricType.AGRICULTURAL_IMPACT and 
                    snapshot.timestamp >= cutoff_time)
            ]
            
            # Calculate metrics
            water_savings = [m.value for m in impact_metrics if m.metric_name == "total_water_savings_gallons"]
            farms_with_conservation = [m.value for m in impact_metrics if m.metric_name == "farms_with_conservation_practices"]
            drought_reduction = [m.value for m in impact_metrics if m.metric_name == "drought_risk_reduction_percent"]
            cost_savings = [m.value for m in impact_metrics if m.metric_name == "total_cost_savings_dollars"]
            
            return AgriculturalImpactMetrics(
                total_water_savings_gallons=statistics.mean(water_savings) if water_savings else 0.0,
                farms_with_conservation_practices=int(statistics.mean(farms_with_conservation)) if farms_with_conservation else 0,
                drought_risk_reduction_percent=statistics.mean(drought_reduction) if drought_reduction else 0.0,
                total_cost_savings_dollars=statistics.mean(cost_savings) if cost_savings else 0.0,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error getting agricultural impact metrics: {str(e)}")
            raise
    
    def _get_latest_feature_usage(self) -> Dict[str, float]:
        """Get latest feature usage statistics."""
        feature_usage = {}
        for snapshot in reversed(self.metrics_buffer):
            if snapshot.metric_name.startswith("feature_usage_"):
                feature_name = snapshot.metric_name.replace("feature_usage_", "")
                if feature_name not in feature_usage:
                    feature_usage[feature_name] = snapshot.value
        return feature_usage
    
    async def get_production_health_status(self) -> ProductionHealthStatus:
        """Get overall production health status."""
        try:
            # Get current metrics
            system_metrics = await self.get_system_performance_metrics(time_range_hours=1)
            user_metrics = await self.get_user_engagement_metrics(time_range_hours=1)
            recommendation_metrics = await self.get_recommendation_effectiveness_metrics(time_range_hours=1)
            
            # Determine overall health
            health_score = self._calculate_health_score(system_metrics, user_metrics, recommendation_metrics)
            
            # Get active alerts
            active_alerts = await self._get_active_alerts()
            
            return ProductionHealthStatus(
                overall_health_score=health_score,
                system_performance=system_metrics,
                user_engagement=user_metrics,
                recommendation_effectiveness=recommendation_metrics,
                active_alerts=active_alerts,
                last_updated=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error getting production health status: {str(e)}")
            raise
    
    def _calculate_health_score(self, system_metrics: SystemPerformanceMetrics, 
                               user_metrics: UserEngagementMetrics, 
                               recommendation_metrics: RecommendationEffectivenessMetrics) -> float:
        """Calculate overall health score."""
        try:
            # System performance score (0-100)
            cpu_score = max(0, 100 - system_metrics.cpu_usage_percent)
            memory_score = max(0, 100 - system_metrics.memory_usage_percent)
            disk_score = max(0, 100 - system_metrics.disk_usage_percent)
            system_score = (cpu_score + memory_score + disk_score) / 3
            
            # User engagement score (0-100)
            user_score = min(100, (user_metrics.daily_active_users / 100) * 100)
            
            # Recommendation effectiveness score (0-100)
            recommendation_score = recommendation_metrics.recommendation_accuracy_percent
            
            # Weighted average
            overall_score = (system_score * 0.4 + user_score * 0.3 + recommendation_score * 0.3)
            return min(100, max(0, overall_score))
            
        except Exception as e:
            logger.error(f"Error calculating health score: {str(e)}")
            return 50.0  # Default score
    
    async def _get_active_alerts(self) -> List[ProductionAlert]:
        """Get active alerts."""
        # In production, this would query the database for active alerts
        return []
    
    async def get_real_time_metrics(self) -> RealTimeMetrics:
        """Get real-time metrics."""
        try:
            # Get latest metrics from buffer
            latest_metrics = {}
            for snapshot in reversed(self.metrics_buffer):
                if snapshot.metric_name not in latest_metrics:
                    latest_metrics[snapshot.metric_name] = snapshot.value
            
            return RealTimeMetrics(
                metrics=latest_metrics,
                timestamp=datetime.utcnow(),
                collection_active=self.metrics_collection_active
            )
            
        except Exception as e:
            logger.error(f"Error getting real-time metrics: {str(e)}")
            raise
    
    async def get_historical_metrics(self, metric_name: str, hours: int = 24) -> HistoricalMetrics:
        """Get historical metrics for a specific metric."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            # Filter metrics by name and time range
            historical_data = [
                snapshot for snapshot in self.metrics_buffer
                if (snapshot.metric_name == metric_name and 
                    snapshot.timestamp >= cutoff_time)
            ]
            
            # Sort by timestamp
            historical_data.sort(key=lambda x: x.timestamp)
            
            # Extract data points
            data_points = [
                {
                    "timestamp": snapshot.timestamp.isoformat(),
                    "value": snapshot.value
                }
                for snapshot in historical_data
            ]
            
            return HistoricalMetrics(
                metric_name=metric_name,
                data_points=data_points,
                time_range_hours=hours,
                total_points=len(data_points)
            )
            
        except Exception as e:
            logger.error(f"Error getting historical metrics: {str(e)}")
            raise
    
    async def generate_production_report(self, start_date: datetime, end_date: datetime) -> ProductionMonitoringReport:
        """Generate comprehensive production monitoring report."""
        try:
            logger.info(f"Generating production report from {start_date} to {end_date}")
            
            # Get metrics for the time period
            system_metrics = await self.get_system_performance_metrics(time_range_hours=24)
            user_metrics = await self.get_user_engagement_metrics(time_range_hours=24)
            recommendation_metrics = await self.get_recommendation_effectiveness_metrics(time_range_hours=24)
            agricultural_metrics = await self.get_agricultural_impact_metrics(time_range_hours=24)
            
            # Calculate trends
            trends = await self._calculate_performance_trends(start_date, end_date)
            
            # Generate report
            report = ProductionMonitoringReport(
                report_id=uuid4(),
                start_date=start_date,
                end_date=end_date,
                generated_at=datetime.utcnow(),
                system_performance=system_metrics,
                user_engagement=user_metrics,
                recommendation_effectiveness=recommendation_metrics,
                agricultural_impact=agricultural_metrics,
                performance_trends=trends,
                summary=self._generate_report_summary(system_metrics, user_metrics, recommendation_metrics, agricultural_metrics)
            )
            
            logger.info("Production report generated successfully")
            return report
            
        except Exception as e:
            logger.error(f"Error generating production report: {str(e)}")
            raise
    
    async def _calculate_performance_trends(self, start_date: datetime, end_date: datetime) -> List[PerformanceTrend]:
        """Calculate performance trends for the time period."""
        trends = []
        
        # Calculate trends for key metrics
        key_metrics = [
            "cpu_usage_percent",
            "memory_usage_percent", 
            "daily_active_users",
            "recommendation_accuracy_percent",
            "total_water_savings_gallons"
        ]
        
        for metric_name in key_metrics:
            trend = await self._calculate_metric_trend(metric_name, start_date, end_date)
            if trend:
                trends.append(trend)
        
        return trends
    
    async def _calculate_metric_trend(self, metric_name: str, start_date: datetime, end_date: datetime) -> Optional[PerformanceTrend]:
        """Calculate trend for a specific metric."""
        try:
            # Filter metrics by name and time range
            metric_data = [
                snapshot for snapshot in self.metrics_buffer
                if (snapshot.metric_name == metric_name and 
                    start_date <= snapshot.timestamp <= end_date)
            ]
            
            if len(metric_data) < 2:
                return None
            
            # Sort by timestamp
            metric_data.sort(key=lambda x: x.timestamp)
            
            # Calculate trend
            values = [snapshot.value for snapshot in metric_data]
            first_value = values[0]
            last_value = values[-1]
            
            if first_value == 0:
                change_percent = 0
            else:
                change_percent = ((last_value - first_value) / first_value) * 100
            
            # Determine trend direction
            if change_percent > 5:
                trend_direction = "increasing"
            elif change_percent < -5:
                trend_direction = "decreasing"
            else:
                trend_direction = "stable"
            
            return PerformanceTrend(
                metric_name=metric_name,
                trend_direction=trend_direction,
                change_percent=change_percent,
                first_value=first_value,
                last_value=last_value,
                data_points=len(values)
            )
            
        except Exception as e:
            logger.error(f"Error calculating trend for {metric_name}: {str(e)}")
            return None
    
    def _generate_report_summary(self, system_metrics: SystemPerformanceMetrics, 
                                user_metrics: UserEngagementMetrics,
                                recommendation_metrics: RecommendationEffectivenessMetrics,
                                agricultural_metrics: AgriculturalImpactMetrics) -> Dict[str, Any]:
        """Generate report summary."""
        return {
            "overall_health": "Good" if system_metrics.cpu_usage_percent < 70 else "Warning",
            "key_highlights": [
                f"System CPU usage: {system_metrics.cpu_usage_percent:.1f}%",
                f"Daily active users: {user_metrics.daily_active_users:.0f}",
                f"Recommendation accuracy: {recommendation_metrics.recommendation_accuracy_percent:.1f}%",
                f"Water savings: {agricultural_metrics.total_water_savings_gallons:.0f} gallons"
            ],
            "recommendations": [
                "Monitor CPU usage closely",
                "Continue user engagement initiatives",
                "Maintain recommendation quality",
                "Track agricultural impact metrics"
            ]
        }
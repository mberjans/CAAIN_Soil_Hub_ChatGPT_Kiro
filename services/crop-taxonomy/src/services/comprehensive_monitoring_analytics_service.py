"""
Comprehensive Monitoring and Analytics Service

This service provides comprehensive monitoring and analytics infrastructure for variety recommendations
as specified in TICKET-005_crop-variety-recommendations-15.2.

Features:
- Application performance monitoring
- Error tracking and analysis
- User behavior analytics
- Recommendation accuracy metrics
- User satisfaction tracking
- System performance metrics
- Business metrics and KPIs
- Automated alerting
- Real-time dashboards
- Regular reporting
"""

import asyncio
import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
import statistics
import psutil
import threading
from enum import Enum
import uuid

# Database imports
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Redis imports
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class MetricType(Enum):
    """Types of metrics."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    PERCENTAGE = "percentage"


@dataclass
class SystemHealthMetrics:
    """System health metrics."""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    network_io_bytes: int
    active_connections: int
    response_time_ms: float
    error_rate: float
    timestamp: datetime


@dataclass
class UserEngagementMetrics:
    """User engagement metrics."""
    active_users: int
    new_users: int
    returning_users: int
    session_duration_minutes: float
    recommendations_requested: int
    recommendations_accepted: int
    recommendations_rejected: int
    user_satisfaction_score: float
    timestamp: datetime


@dataclass
class RecommendationEffectivenessMetrics:
    """Recommendation effectiveness metrics."""
    total_recommendations: int
    successful_recommendations: int
    failed_recommendations: int
    average_confidence_score: float
    average_response_time_ms: float
    cache_hit_rate: float
    expert_validation_rate: float
    farmer_feedback_score: float
    timestamp: datetime


@dataclass
class BusinessMetrics:
    """Business metrics and KPIs."""
    total_revenue_impact: float
    cost_savings_estimated: float
    environmental_impact_score: float
    user_retention_rate: float
    market_penetration: float
    customer_acquisition_cost: float
    lifetime_value: float
    timestamp: datetime


@dataclass
class Alert:
    """Alert definition."""
    id: str
    level: AlertLevel
    title: str
    message: str
    metric_name: str
    threshold_value: float
    current_value: float
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class DashboardData:
    """Dashboard data structure."""
    system_health: SystemHealthMetrics
    user_engagement: UserEngagementMetrics
    recommendation_effectiveness: RecommendationEffectivenessMetrics
    business_metrics: BusinessMetrics
    alerts: List[Alert]
    timestamp: datetime


class ComprehensiveMonitoringAnalyticsService:
    """Comprehensive monitoring and analytics service for variety recommendations."""
    
    def __init__(self, database_url: str = None, redis_url: str = "redis://localhost:6379"):
        """Initialize the comprehensive monitoring and analytics service."""
        self.database_url = database_url
        self.redis_url = redis_url
        
        # Metrics storage
        self.system_health_metrics: deque = deque(maxlen=1000)
        self.user_engagement_metrics: deque = deque(maxlen=1000)
        self.recommendation_effectiveness_metrics: deque = deque(maxlen=1000)
        self.business_metrics: deque = deque(maxlen=1000)
        self.alerts: List[Alert] = []
        
        # Performance thresholds
        self.thresholds = {
            "response_time_warning_ms": 2000.0,
            "response_time_critical_ms": 5000.0,
            "error_rate_warning": 0.05,  # 5%
            "error_rate_critical": 0.10,  # 10%
            "cpu_warning_percent": 80.0,
            "cpu_critical_percent": 95.0,
            "memory_warning_percent": 85.0,
            "memory_critical_percent": 95.0,
            "user_satisfaction_warning": 0.80,  # 80%
            "user_satisfaction_critical": 0.70,  # 70%
            "recommendation_confidence_warning": 0.80,  # 80%
            "recommendation_confidence_critical": 0.70,  # 70%
        }
        
        # Database connection for metrics
        self.db_engine = None
        self.db_session = None
        if database_url:
            self._initialize_database()
        
        # Redis connection for metrics
        self.redis_client = None
        if REDIS_AVAILABLE:
            self._initialize_redis()
        
        # Background monitoring
        self.monitoring_active = False
        self.monitoring_task = None
        
        # Thread safety
        self.lock = threading.Lock()
        
        logger.info("Comprehensive monitoring and analytics service initialized")
    
    def _initialize_database(self):
        """Initialize database connection for metrics collection."""
        try:
            self.db_engine = create_engine(self.database_url, echo=False)
            self.db_session = sessionmaker(bind=self.db_engine)
            logger.info("Database connection initialized for monitoring analytics")
        except Exception as e:
            logger.warning(f"Failed to initialize database connection: {e}")
    
    def _initialize_redis(self):
        """Initialize Redis connection for metrics collection."""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            logger.info("Redis connection initialized for monitoring analytics")
        except Exception as e:
            logger.warning(f"Failed to initialize Redis connection: {e}")
    
    def start_monitoring(self, interval_seconds: int = 30):
        """Start background monitoring."""
        if self.monitoring_active:
            logger.warning("Monitoring is already active")
            return
        
        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(
            self._monitoring_loop(interval_seconds)
        )
        logger.info(f"Background monitoring started (interval: {interval_seconds}s)")
    
    def stop_monitoring(self):
        """Stop background monitoring."""
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
        logger.info("Background monitoring stopped")
    
    async def _monitoring_loop(self, interval_seconds: int):
        """Background monitoring loop."""
        while self.monitoring_active:
            try:
                # Collect all metrics
                await self._collect_system_health_metrics()
                await self._collect_user_engagement_metrics()
                await self._collect_recommendation_effectiveness_metrics()
                await self._collect_business_metrics()
                
                # Check for alerts
                await self._check_alerts()
                
                # Wait for next interval
                await asyncio.sleep(interval_seconds)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval_seconds)
    
    async def _collect_system_health_metrics(self):
        """Collect system health metrics."""
        try:
            # CPU and memory metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network I/O
            network_io = psutil.net_io_counters()
            network_bytes = network_io.bytes_sent + network_io.bytes_recv
            
            # Get response time and error rate from recent operations
            response_time_ms, error_rate = await self._get_recent_performance_metrics()
            
            # Get active connections
            active_connections = await self._get_active_connections()
            
            metrics = SystemHealthMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / (1024 * 1024),
                memory_available_mb=memory.available / (1024 * 1024),
                disk_usage_percent=disk.percent,
                network_io_bytes=network_bytes,
                active_connections=active_connections,
                response_time_ms=response_time_ms,
                error_rate=error_rate,
                timestamp=datetime.utcnow()
            )
            
            with self.lock:
                self.system_health_metrics.append(metrics)
            
        except Exception as e:
            logger.error(f"Failed to collect system health metrics: {e}")
    
    async def _collect_user_engagement_metrics(self):
        """Collect user engagement metrics."""
        try:
            # Get user engagement data from database
            engagement_data = await self._get_user_engagement_data()
            
            metrics = UserEngagementMetrics(
                active_users=engagement_data.get('active_users', 0),
                new_users=engagement_data.get('new_users', 0),
                returning_users=engagement_data.get('returning_users', 0),
                session_duration_minutes=engagement_data.get('session_duration_minutes', 0.0),
                recommendations_requested=engagement_data.get('recommendations_requested', 0),
                recommendations_accepted=engagement_data.get('recommendations_accepted', 0),
                recommendations_rejected=engagement_data.get('recommendations_rejected', 0),
                user_satisfaction_score=engagement_data.get('user_satisfaction_score', 0.0),
                timestamp=datetime.utcnow()
            )
            
            with self.lock:
                self.user_engagement_metrics.append(metrics)
            
        except Exception as e:
            logger.error(f"Failed to collect user engagement metrics: {e}")
    
    async def _collect_recommendation_effectiveness_metrics(self):
        """Collect recommendation effectiveness metrics."""
        try:
            # Get recommendation effectiveness data
            effectiveness_data = await self._get_recommendation_effectiveness_data()
            
            metrics = RecommendationEffectivenessMetrics(
                total_recommendations=effectiveness_data.get('total_recommendations', 0),
                successful_recommendations=effectiveness_data.get('successful_recommendations', 0),
                failed_recommendations=effectiveness_data.get('failed_recommendations', 0),
                average_confidence_score=effectiveness_data.get('average_confidence_score', 0.0),
                average_response_time_ms=effectiveness_data.get('average_response_time_ms', 0.0),
                cache_hit_rate=effectiveness_data.get('cache_hit_rate', 0.0),
                expert_validation_rate=effectiveness_data.get('expert_validation_rate', 0.0),
                farmer_feedback_score=effectiveness_data.get('farmer_feedback_score', 0.0),
                timestamp=datetime.utcnow()
            )
            
            with self.lock:
                self.recommendation_effectiveness_metrics.append(metrics)
            
        except Exception as e:
            logger.error(f"Failed to collect recommendation effectiveness metrics: {e}")
    
    async def _collect_business_metrics(self):
        """Collect business metrics."""
        try:
            # Get business metrics data
            business_data = await self._get_business_metrics_data()
            
            metrics = BusinessMetrics(
                total_revenue_impact=business_data.get('total_revenue_impact', 0.0),
                cost_savings_estimated=business_data.get('cost_savings_estimated', 0.0),
                environmental_impact_score=business_data.get('environmental_impact_score', 0.0),
                user_retention_rate=business_data.get('user_retention_rate', 0.0),
                market_penetration=business_data.get('market_penetration', 0.0),
                customer_acquisition_cost=business_data.get('customer_acquisition_cost', 0.0),
                lifetime_value=business_data.get('lifetime_value', 0.0),
                timestamp=datetime.utcnow()
            )
            
            with self.lock:
                self.business_metrics.append(metrics)
            
        except Exception as e:
            logger.error(f"Failed to collect business metrics: {e}")
    
    async def _get_recent_performance_metrics(self) -> Tuple[float, float]:
        """Get recent performance metrics."""
        try:
            if not self.db_session:
                return 0.0, 0.0
            
            with self.db_session() as session:
                # Get recent performance data
                result = session.execute(text("""
                    SELECT 
                        AVG(execution_time_ms) as avg_response_time,
                        COUNT(CASE WHEN success = false THEN 1 END)::float / COUNT(*) as error_rate
                    FROM performance_metrics 
                    WHERE timestamp > NOW() - INTERVAL '5 minutes'
                """)).fetchone()
                
                if result:
                    return result[0] or 0.0, result[1] or 0.0
        except Exception:
            pass
        
        return 0.0, 0.0
    
    async def _get_active_connections(self) -> int:
        """Get number of active connections."""
        try:
            if not self.db_session:
                return 0
            
            with self.db_session() as session:
                pool_status = session.bind.pool.status()
                return pool_status.get('checkedout', 0)
        except Exception:
            return 0
    
    async def _get_user_engagement_data(self) -> Dict[str, Any]:
        """Get user engagement data from database."""
        try:
            if not self.db_session:
                return {}
            
            with self.db_session() as session:
                # Get user engagement metrics
                result = session.execute(text("""
                    SELECT 
                        COUNT(DISTINCT user_id) as active_users,
                        COUNT(CASE WHEN created_at > NOW() - INTERVAL '24 hours' THEN 1 END) as new_users,
                        AVG(session_duration_minutes) as avg_session_duration,
                        COUNT(CASE WHEN action_type = 'recommendation_request' THEN 1 END) as recommendations_requested,
                        COUNT(CASE WHEN action_type = 'recommendation_accepted' THEN 1 END) as recommendations_accepted,
                        COUNT(CASE WHEN action_type = 'recommendation_rejected' THEN 1 END) as recommendations_rejected,
                        AVG(satisfaction_score) as avg_satisfaction
                    FROM user_interactions 
                    WHERE timestamp > NOW() - INTERVAL '1 hour'
                """)).fetchone()
                
                if result:
                    return {
                        'active_users': result[0] or 0,
                        'new_users': result[1] or 0,
                        'returning_users': (result[0] or 0) - (result[1] or 0),
                        'session_duration_minutes': result[2] or 0.0,
                        'recommendations_requested': result[3] or 0,
                        'recommendations_accepted': result[4] or 0,
                        'recommendations_rejected': result[5] or 0,
                        'user_satisfaction_score': result[6] or 0.0
                    }
        except Exception:
            pass
        
        return {}
    
    async def _get_recommendation_effectiveness_data(self) -> Dict[str, Any]:
        """Get recommendation effectiveness data."""
        try:
            if not self.db_session:
                return {}
            
            with self.db_session() as session:
                # Get recommendation effectiveness metrics
                result = session.execute(text("""
                    SELECT 
                        COUNT(*) as total_recommendations,
                        COUNT(CASE WHEN success = true THEN 1 END) as successful_recommendations,
                        COUNT(CASE WHEN success = false THEN 1 END) as failed_recommendations,
                        AVG(confidence_score) as avg_confidence,
                        AVG(response_time_ms) as avg_response_time,
                        AVG(CASE WHEN cache_hit THEN 1.0 ELSE 0.0 END) as cache_hit_rate,
                        AVG(CASE WHEN expert_validated THEN 1.0 ELSE 0.0 END) as expert_validation_rate,
                        AVG(farmer_feedback_score) as avg_farmer_feedback
                    FROM recommendation_analytics 
                    WHERE timestamp > NOW() - INTERVAL '1 hour'
                """)).fetchone()
                
                if result:
                    return {
                        'total_recommendations': result[0] or 0,
                        'successful_recommendations': result[1] or 0,
                        'failed_recommendations': result[2] or 0,
                        'average_confidence_score': result[3] or 0.0,
                        'average_response_time_ms': result[4] or 0.0,
                        'cache_hit_rate': result[5] or 0.0,
                        'expert_validation_rate': result[6] or 0.0,
                        'farmer_feedback_score': result[7] or 0.0
                    }
        except Exception:
            pass
        
        return {}
    
    async def _get_business_metrics_data(self) -> Dict[str, Any]:
        """Get business metrics data."""
        try:
            if not self.db_session:
                return {}
            
            with self.db_session() as session:
                # Get business metrics
                result = session.execute(text("""
                    SELECT 
                        SUM(revenue_impact) as total_revenue_impact,
                        SUM(cost_savings) as total_cost_savings,
                        AVG(environmental_score) as avg_environmental_score,
                        AVG(retention_rate) as avg_retention_rate,
                        COUNT(DISTINCT user_id) as total_users,
                        AVG(acquisition_cost) as avg_acquisition_cost,
                        AVG(lifetime_value) as avg_lifetime_value
                    FROM business_metrics 
                    WHERE timestamp > NOW() - INTERVAL '24 hours'
                """)).fetchone()
                
                if result:
                    return {
                        'total_revenue_impact': result[0] or 0.0,
                        'cost_savings_estimated': result[1] or 0.0,
                        'environmental_impact_score': result[2] or 0.0,
                        'user_retention_rate': result[3] or 0.0,
                        'market_penetration': (result[4] or 0) / 10000.0,  # Assuming 10k target market
                        'customer_acquisition_cost': result[5] or 0.0,
                        'lifetime_value': result[6] or 0.0
                    }
        except Exception:
            pass
        
        return {}
    
    async def _check_alerts(self):
        """Check for alert conditions."""
        try:
            with self.lock:
                # Get latest metrics
                if not self.system_health_metrics:
                    return
                
                latest_system = self.system_health_metrics[-1]
                latest_user = self.user_engagement_metrics[-1] if self.user_engagement_metrics else None
                latest_recommendation = self.recommendation_effectiveness_metrics[-1] if self.recommendation_effectiveness_metrics else None
                
                # Check system health alerts
                await self._check_system_health_alerts(latest_system)
                
                # Check user engagement alerts
                if latest_user:
                    await self._check_user_engagement_alerts(latest_user)
                
                # Check recommendation effectiveness alerts
                if latest_recommendation:
                    await self._check_recommendation_effectiveness_alerts(latest_recommendation)
                
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
    
    async def _check_system_health_alerts(self, metrics: SystemHealthMetrics):
        """Check system health alerts."""
        # CPU alerts
        if metrics.cpu_percent > self.thresholds["cpu_critical_percent"]:
            await self._create_alert(
                AlertLevel.CRITICAL,
                "High CPU Usage",
                f"CPU usage is {metrics.cpu_percent:.1f}%, exceeding critical threshold of {self.thresholds['cpu_critical_percent']}%",
                "cpu_percent",
                self.thresholds["cpu_critical_percent"],
                metrics.cpu_percent
            )
        elif metrics.cpu_percent > self.thresholds["cpu_warning_percent"]:
            await self._create_alert(
                AlertLevel.WARNING,
                "High CPU Usage",
                f"CPU usage is {metrics.cpu_percent:.1f}%, exceeding warning threshold of {self.thresholds['cpu_warning_percent']}%",
                "cpu_percent",
                self.thresholds["cpu_warning_percent"],
                metrics.cpu_percent
            )
        
        # Memory alerts
        if metrics.memory_percent > self.thresholds["memory_critical_percent"]:
            await self._create_alert(
                AlertLevel.CRITICAL,
                "High Memory Usage",
                f"Memory usage is {metrics.memory_percent:.1f}%, exceeding critical threshold of {self.thresholds['memory_critical_percent']}%",
                "memory_percent",
                self.thresholds["memory_critical_percent"],
                metrics.memory_percent
            )
        elif metrics.memory_percent > self.thresholds["memory_warning_percent"]:
            await self._create_alert(
                AlertLevel.WARNING,
                "High Memory Usage",
                f"Memory usage is {metrics.memory_percent:.1f}%, exceeding warning threshold of {self.thresholds['memory_warning_percent']}%",
                "memory_percent",
                self.thresholds["memory_warning_percent"],
                metrics.memory_percent
            )
        
        # Response time alerts
        if metrics.response_time_ms > self.thresholds["response_time_critical_ms"]:
            await self._create_alert(
                AlertLevel.CRITICAL,
                "Slow Response Time",
                f"Response time is {metrics.response_time_ms:.1f}ms, exceeding critical threshold of {self.thresholds['response_time_critical_ms']}ms",
                "response_time_ms",
                self.thresholds["response_time_critical_ms"],
                metrics.response_time_ms
            )
        elif metrics.response_time_ms > self.thresholds["response_time_warning_ms"]:
            await self._create_alert(
                AlertLevel.WARNING,
                "Slow Response Time",
                f"Response time is {metrics.response_time_ms:.1f}ms, exceeding warning threshold of {self.thresholds['response_time_warning_ms']}ms",
                "response_time_ms",
                self.thresholds["response_time_warning_ms"],
                metrics.response_time_ms
            )
        
        # Error rate alerts
        if metrics.error_rate > self.thresholds["error_rate_critical"]:
            await self._create_alert(
                AlertLevel.CRITICAL,
                "High Error Rate",
                f"Error rate is {metrics.error_rate:.2%}, exceeding critical threshold of {self.thresholds['error_rate_critical']:.2%}",
                "error_rate",
                self.thresholds["error_rate_critical"],
                metrics.error_rate
            )
        elif metrics.error_rate > self.thresholds["error_rate_warning"]:
            await self._create_alert(
                AlertLevel.WARNING,
                "High Error Rate",
                f"Error rate is {metrics.error_rate:.2%}, exceeding warning threshold of {self.thresholds['error_rate_warning']:.2%}",
                "error_rate",
                self.thresholds["error_rate_warning"],
                metrics.error_rate
            )
    
    async def _check_user_engagement_alerts(self, metrics: UserEngagementMetrics):
        """Check user engagement alerts."""
        # User satisfaction alerts
        if metrics.user_satisfaction_score < self.thresholds["user_satisfaction_critical"]:
            await self._create_alert(
                AlertLevel.CRITICAL,
                "Low User Satisfaction",
                f"User satisfaction score is {metrics.user_satisfaction_score:.2f}, below critical threshold of {self.thresholds['user_satisfaction_critical']:.2f}",
                "user_satisfaction_score",
                self.thresholds["user_satisfaction_critical"],
                metrics.user_satisfaction_score
            )
        elif metrics.user_satisfaction_score < self.thresholds["user_satisfaction_warning"]:
            await self._create_alert(
                AlertLevel.WARNING,
                "Low User Satisfaction",
                f"User satisfaction score is {metrics.user_satisfaction_score:.2f}, below warning threshold of {self.thresholds['user_satisfaction_warning']:.2f}",
                "user_satisfaction_score",
                self.thresholds["user_satisfaction_warning"],
                metrics.user_satisfaction_score
            )
    
    async def _check_recommendation_effectiveness_alerts(self, metrics: RecommendationEffectivenessMetrics):
        """Check recommendation effectiveness alerts."""
        # Recommendation confidence alerts
        if metrics.average_confidence_score < self.thresholds["recommendation_confidence_critical"]:
            await self._create_alert(
                AlertLevel.CRITICAL,
                "Low Recommendation Confidence",
                f"Average recommendation confidence is {metrics.average_confidence_score:.2f}, below critical threshold of {self.thresholds['recommendation_confidence_critical']:.2f}",
                "recommendation_confidence",
                self.thresholds["recommendation_confidence_critical"],
                metrics.average_confidence_score
            )
        elif metrics.average_confidence_score < self.thresholds["recommendation_confidence_warning"]:
            await self._create_alert(
                AlertLevel.WARNING,
                "Low Recommendation Confidence",
                f"Average recommendation confidence is {metrics.average_confidence_score:.2f}, below warning threshold of {self.thresholds['recommendation_confidence_warning']:.2f}",
                "recommendation_confidence",
                self.thresholds["recommendation_confidence_warning"],
                metrics.average_confidence_score
            )
    
    async def _create_alert(self, level: AlertLevel, title: str, message: str, 
                          metric_name: str, threshold_value: float, current_value: float):
        """Create a new alert."""
        alert_id = str(uuid.uuid4())
        
        # Check if similar alert already exists and is unresolved
        with self.lock:
            for existing_alert in self.alerts:
                if (existing_alert.metric_name == metric_name and 
                    existing_alert.level == level and 
                    not existing_alert.resolved):
                    return  # Don't create duplicate alerts
        
        alert = Alert(
            id=alert_id,
            level=level,
            title=title,
            message=message,
            metric_name=metric_name,
            threshold_value=threshold_value,
            current_value=current_value,
            timestamp=datetime.utcnow()
        )
        
        with self.lock:
            self.alerts.append(alert)
        
        # Log the alert
        if level == AlertLevel.CRITICAL:
            logger.critical(f"CRITICAL ALERT: {title} - {message}")
        elif level == AlertLevel.WARNING:
            logger.warning(f"WARNING ALERT: {title} - {message}")
        else:
            logger.info(f"INFO ALERT: {title} - {message}")
        
        # Send alert to external systems (Prometheus, Slack, etc.)
        await self._send_alert_notification(alert)
    
    async def _send_alert_notification(self, alert: Alert):
        """Send alert notification to external systems."""
        try:
            # Send to Prometheus Alertmanager if available
            if self.redis_client:
                alert_data = {
                    "id": alert.id,
                    "level": alert.level.value,
                    "title": alert.title,
                    "message": alert.message,
                    "metric_name": alert.metric_name,
                    "threshold_value": alert.threshold_value,
                    "current_value": alert.current_value,
                    "timestamp": alert.timestamp.isoformat()
                }
                await self.redis_client.lpush("alerts", json.dumps(alert_data))
            
            # TODO: Add Slack, email, or other notification methods
        except Exception as e:
            logger.error(f"Failed to send alert notification: {e}")
    
    def get_dashboard_data(self) -> DashboardData:
        """Get current dashboard data."""
        with self.lock:
            latest_system = self.system_health_metrics[-1] if self.system_health_metrics else None
            latest_user = self.user_engagement_metrics[-1] if self.user_engagement_metrics else None
            latest_recommendation = self.recommendation_effectiveness_metrics[-1] if self.recommendation_effectiveness_metrics else None
            latest_business = self.business_metrics[-1] if self.business_metrics else None
            
            # Get unresolved alerts
            unresolved_alerts = [alert for alert in self.alerts if not alert.resolved]
            
            return DashboardData(
                system_health=latest_system,
                user_engagement=latest_user,
                recommendation_effectiveness=latest_recommendation,
                business_metrics=latest_business,
                alerts=unresolved_alerts,
                timestamp=datetime.utcnow()
            )
    
    def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get metrics summary for specified time period."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        with self.lock:
            # Filter metrics by time period
            recent_system = [m for m in self.system_health_metrics if m.timestamp > cutoff_time]
            recent_user = [m for m in self.user_engagement_metrics if m.timestamp > cutoff_time]
            recent_recommendation = [m for m in self.recommendation_effectiveness_metrics if m.timestamp > cutoff_time]
            recent_business = [m for m in self.business_metrics if m.timestamp > cutoff_time]
            
            summary = {
                "period_hours": hours,
                "timestamp": datetime.utcnow().isoformat(),
                "system_health": {
                    "avg_cpu_percent": statistics.mean([m.cpu_percent for m in recent_system]) if recent_system else 0,
                    "avg_memory_percent": statistics.mean([m.memory_percent for m in recent_system]) if recent_system else 0,
                    "avg_response_time_ms": statistics.mean([m.response_time_ms for m in recent_system]) if recent_system else 0,
                    "avg_error_rate": statistics.mean([m.error_rate for m in recent_system]) if recent_system else 0,
                    "data_points": len(recent_system)
                },
                "user_engagement": {
                    "avg_active_users": statistics.mean([m.active_users for m in recent_user]) if recent_user else 0,
                    "avg_new_users": statistics.mean([m.new_users for m in recent_user]) if recent_user else 0,
                    "avg_session_duration_minutes": statistics.mean([m.session_duration_minutes for m in recent_user]) if recent_user else 0,
                    "avg_satisfaction_score": statistics.mean([m.user_satisfaction_score for m in recent_user]) if recent_user else 0,
                    "data_points": len(recent_user)
                },
                "recommendation_effectiveness": {
                    "total_recommendations": sum([m.total_recommendations for m in recent_recommendation]) if recent_recommendation else 0,
                    "avg_confidence_score": statistics.mean([m.average_confidence_score for m in recent_recommendation]) if recent_recommendation else 0,
                    "avg_response_time_ms": statistics.mean([m.average_response_time_ms for m in recent_recommendation]) if recent_recommendation else 0,
                    "avg_cache_hit_rate": statistics.mean([m.cache_hit_rate for m in recent_recommendation]) if recent_recommendation else 0,
                    "data_points": len(recent_recommendation)
                },
                "business_metrics": {
                    "total_revenue_impact": sum([m.total_revenue_impact for m in recent_business]) if recent_business else 0,
                    "total_cost_savings": sum([m.cost_savings_estimated for m in recent_business]) if recent_business else 0,
                    "avg_environmental_score": statistics.mean([m.environmental_impact_score for m in recent_business]) if recent_business else 0,
                    "avg_retention_rate": statistics.mean([m.user_retention_rate for m in recent_business]) if recent_business else 0,
                    "data_points": len(recent_business)
                },
                "alerts": {
                    "total_alerts": len(self.alerts),
                    "unresolved_alerts": len([a for a in self.alerts if not a.resolved]),
                    "critical_alerts": len([a for a in self.alerts if a.level == AlertLevel.CRITICAL and not a.resolved]),
                    "warning_alerts": len([a for a in self.alerts if a.level == AlertLevel.WARNING and not a.resolved])
                }
            }
            
            return summary
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert."""
        with self.lock:
            for alert in self.alerts:
                if alert.id == alert_id:
                    alert.resolved = True
                    alert.resolved_at = datetime.utcnow()
                    logger.info(f"Alert {alert_id} resolved: {alert.title}")
                    return True
        return False
    
    async def export_metrics(self, format: str = "json") -> Union[str, Dict[str, Any]]:
        """Export metrics in specified format."""
        with self.lock:
            data = {
                "export_timestamp": datetime.utcnow().isoformat(),
                "system_health_metrics": [
                    {
                        "cpu_percent": m.cpu_percent,
                        "memory_percent": m.memory_percent,
                        "memory_used_mb": m.memory_used_mb,
                        "memory_available_mb": m.memory_available_mb,
                        "disk_usage_percent": m.disk_usage_percent,
                        "network_io_bytes": m.network_io_bytes,
                        "active_connections": m.active_connections,
                        "response_time_ms": m.response_time_ms,
                        "error_rate": m.error_rate,
                        "timestamp": m.timestamp.isoformat()
                    }
                    for m in self.system_health_metrics
                ],
                "user_engagement_metrics": [
                    {
                        "active_users": m.active_users,
                        "new_users": m.new_users,
                        "returning_users": m.returning_users,
                        "session_duration_minutes": m.session_duration_minutes,
                        "recommendations_requested": m.recommendations_requested,
                        "recommendations_accepted": m.recommendations_accepted,
                        "recommendations_rejected": m.recommendations_rejected,
                        "user_satisfaction_score": m.user_satisfaction_score,
                        "timestamp": m.timestamp.isoformat()
                    }
                    for m in self.user_engagement_metrics
                ],
                "recommendation_effectiveness_metrics": [
                    {
                        "total_recommendations": m.total_recommendations,
                        "successful_recommendations": m.successful_recommendations,
                        "failed_recommendations": m.failed_recommendations,
                        "average_confidence_score": m.average_confidence_score,
                        "average_response_time_ms": m.average_response_time_ms,
                        "cache_hit_rate": m.cache_hit_rate,
                        "expert_validation_rate": m.expert_validation_rate,
                        "farmer_feedback_score": m.farmer_feedback_score,
                        "timestamp": m.timestamp.isoformat()
                    }
                    for m in self.recommendation_effectiveness_metrics
                ],
                "business_metrics": [
                    {
                        "total_revenue_impact": m.total_revenue_impact,
                        "cost_savings_estimated": m.cost_savings_estimated,
                        "environmental_impact_score": m.environmental_impact_score,
                        "user_retention_rate": m.user_retention_rate,
                        "market_penetration": m.market_penetration,
                        "customer_acquisition_cost": m.customer_acquisition_cost,
                        "lifetime_value": m.lifetime_value,
                        "timestamp": m.timestamp.isoformat()
                    }
                    for m in self.business_metrics
                ],
                "alerts": [
                    {
                        "id": a.id,
                        "level": a.level.value,
                        "title": a.title,
                        "message": a.message,
                        "metric_name": a.metric_name,
                        "threshold_value": a.threshold_value,
                        "current_value": a.current_value,
                        "timestamp": a.timestamp.isoformat(),
                        "resolved": a.resolved,
                        "resolved_at": a.resolved_at.isoformat() if a.resolved_at else None
                    }
                    for a in self.alerts
                ],
                "metrics_summary": self.get_metrics_summary()
            }
        
        if format == "json":
            return data
        elif format == "csv":
            # Convert to CSV format (simplified)
            csv_data = "timestamp,cpu_percent,memory_percent,response_time_ms,error_rate,active_users,user_satisfaction_score\n"
            for m in self.system_health_metrics:
                csv_data += f"{m.timestamp.isoformat()},{m.cpu_percent},{m.memory_percent},{m.response_time_ms},{m.error_rate},{m.active_connections},{0.0}\n"
            return csv_data
        else:
            raise ValueError(f"Unsupported export format: {format}")


# Singleton instance for global access
comprehensive_monitoring_analytics: Optional[ComprehensiveMonitoringAnalyticsService] = None


def get_comprehensive_monitoring_analytics(
    database_url: str = None, 
    redis_url: str = "redis://localhost:6379"
) -> ComprehensiveMonitoringAnalyticsService:
    """Get or create the global comprehensive monitoring analytics instance."""
    global comprehensive_monitoring_analytics
    
    if comprehensive_monitoring_analytics is None:
        comprehensive_monitoring_analytics = ComprehensiveMonitoringAnalyticsService(
            database_url, redis_url
        )
    
    return comprehensive_monitoring_analytics
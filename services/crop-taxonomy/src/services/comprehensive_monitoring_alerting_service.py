"""
Comprehensive Monitoring and Alerting System for Crop Variety Recommendations

This service provides comprehensive monitoring, alerting, and analytics for the crop variety
recommendation system, including performance metrics, recommendation accuracy tracking,
user engagement monitoring, and agricultural outcome metrics.

Author: AI Coding Agent
Date: 2024
"""

import asyncio
import logging
import time
import uuid
from collections import deque
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import json
import threading
from concurrent.futures import ThreadPoolExecutor

# Prometheus metrics
try:
    from prometheus_client import Counter, Histogram, Gauge, Summary, CollectorRegistry, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logging.warning("Prometheus client not available. Metrics will be stored locally only.")

# Redis for caching and pub/sub
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logging.warning("Redis not available. Caching and pub/sub features disabled.")

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class MetricType(Enum):
    """Types of metrics collected."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class Alert:
    """Alert data structure."""
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
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class MetricData:
    """Metric data structure."""
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE


@dataclass
class RecommendationMetrics:
    """Metrics specific to crop variety recommendations."""
    request_id: str
    crop_type: str
    region: str
    response_time_ms: float
    confidence_score: float
    number_of_recommendations: int
    user_satisfaction: Optional[float] = None
    agricultural_outcome: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SystemHealthMetrics:
    """System health metrics."""
    cpu_usage_percent: float
    memory_usage_percent: float
    disk_usage_percent: float
    active_connections: int
    error_rate: float
    response_time_p95: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


class ComprehensiveMonitoringAlertingService:
    """
    Comprehensive monitoring and alerting service for crop variety recommendations.
    
    Features:
    - Real-time metrics collection and monitoring
    - Intelligent alerting with agricultural context
    - Performance tracking and optimization insights
    - User engagement and satisfaction monitoring
    - Agricultural outcome tracking and analysis
    - Integration with Prometheus, Grafana, and external alerting systems
    """
    
    def __init__(self, 
                 database_url: Optional[str] = None,
                 redis_url: str = "redis://localhost:6379",
                 prometheus_port: int = 8000):
        """Initialize the comprehensive monitoring and alerting service."""
        self.database_url = database_url
        self.redis_url = redis_url
        self.prometheus_port = prometheus_port
        
        # Metrics storage
        self.recommendation_metrics: deque = deque(maxlen=10000)
        self.system_health_metrics: deque = deque(maxlen=1000)
        self.user_engagement_metrics: deque = deque(maxlen=5000)
        self.agricultural_outcome_metrics: deque = deque(maxlen=2000)
        self.alerts: List[Alert] = []
        
        # Performance thresholds for agricultural systems
        self.thresholds = {
            # Response time thresholds (agricultural operations are time-sensitive)
            "response_time_warning_ms": 2000.0,  # 2 seconds
            "response_time_critical_ms": 5000.0,  # 5 seconds
            
            # Error rate thresholds
            "error_rate_warning": 0.05,  # 5%
            "error_rate_critical": 0.10,  # 10%
            
            # System resource thresholds
            "cpu_warning_percent": 80.0,
            "cpu_critical_percent": 95.0,
            "memory_warning_percent": 85.0,
            "memory_critical_percent": 95.0,
            "disk_warning_percent": 90.0,
            "disk_critical_percent": 95.0,
            
            # Agricultural-specific thresholds
            "recommendation_confidence_warning": 0.80,  # 80%
            "recommendation_confidence_critical": 0.70,  # 70%
            "user_satisfaction_warning": 0.80,  # 80%
            "user_satisfaction_critical": 0.70,  # 70%
            "agricultural_success_rate_warning": 0.75,  # 75%
            "agricultural_success_rate_critical": 0.65,  # 65%
            
            # Data quality thresholds
            "data_freshness_warning_hours": 24,  # 24 hours
            "data_freshness_critical_hours": 48,  # 48 hours
            "api_availability_warning": 0.95,  # 95%
            "api_availability_critical": 0.90,  # 90%
        }
        
        # Initialize Prometheus metrics
        if PROMETHEUS_AVAILABLE:
            self._initialize_prometheus_metrics()
        
        # Initialize Redis connection
        self.redis_client = None
        if REDIS_AVAILABLE:
            self._initialize_redis()
        
        # Database connection for metrics persistence
        self.db_engine = None
        self.db_session = None
        if database_url:
            self._initialize_database()
        
        # Background monitoring
        self.monitoring_active = False
        self.monitoring_task = None
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Alert notification channels
        self.alert_channels = {
            "email": [],
            "slack": [],
            "webhook": [],
            "sms": []
        }
        
        logger.info("Comprehensive monitoring and alerting service initialized")
    
    def _initialize_prometheus_metrics(self):
        """Initialize Prometheus metrics collectors."""
        self.registry = CollectorRegistry()
        
        # Recommendation-specific metrics
        self.recommendation_counter = Counter(
            'crop_variety_recommendations_total',
            'Total number of crop variety recommendations generated',
            ['crop_type', 'region', 'status'],
            registry=self.registry
        )
        
        self.recommendation_response_time = Histogram(
            'crop_variety_recommendation_duration_seconds',
            'Time spent generating crop variety recommendations',
            ['crop_type', 'region'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
            registry=self.registry
        )
        
        self.recommendation_confidence = Histogram(
            'crop_variety_recommendation_confidence',
            'Confidence scores for crop variety recommendations',
            ['crop_type', 'region'],
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            registry=self.registry
        )
        
        self.user_satisfaction = Histogram(
            'crop_variety_user_satisfaction',
            'User satisfaction scores for recommendations',
            ['crop_type', 'region'],
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            registry=self.registry
        )
        
        # System health metrics
        self.system_cpu_usage = Gauge(
            'system_cpu_usage_percent',
            'System CPU usage percentage',
            registry=self.registry
        )
        
        self.system_memory_usage = Gauge(
            'system_memory_usage_percent',
            'System memory usage percentage',
            registry=self.registry
        )
        
        self.system_disk_usage = Gauge(
            'system_disk_usage_percent',
            'System disk usage percentage',
            registry=self.registry
        )
        
        self.active_connections = Gauge(
            'system_active_connections',
            'Number of active connections',
            registry=self.registry
        )
        
        # Agricultural outcome metrics
        self.agricultural_success_rate = Gauge(
            'agricultural_success_rate',
            'Rate of successful agricultural outcomes',
            ['crop_type', 'region'],
            registry=self.registry
        )
        
        # Data quality metrics
        self.data_freshness = Gauge(
            'data_freshness_hours',
            'Age of data in hours',
            ['data_source'],
            registry=self.registry
        )
        
        self.api_availability = Gauge(
            'external_api_availability',
            'External API availability percentage',
            ['api_name'],
            registry=self.registry
        )
        
        logger.info("Prometheus metrics initialized")
    
    def _initialize_redis(self):
        """Initialize Redis connection for caching and pub/sub."""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            logger.info("Redis connection initialized")
        except Exception as e:
            logger.warning(f"Redis initialization failed: {e}")
            self.redis_client = None
    
    def _initialize_database(self):
        """Initialize database connection for metrics persistence."""
        try:
            from sqlalchemy import create_engine, text
            from sqlalchemy.orm import sessionmaker
            
            self.db_engine = create_engine(self.database_url)
            Session = sessionmaker(bind=self.db_engine)
            self.db_session = Session()
            
            # Create metrics tables if they don't exist
            self._create_metrics_tables()
            
            logger.info("Database connection initialized")
        except Exception as e:
            logger.warning(f"Database initialization failed: {e}")
            self.db_engine = None
            self.db_session = None
    
    def _create_metrics_tables(self):
        """Create database tables for metrics storage."""
        if not self.db_engine:
            return
        
        create_tables_sql = """
        CREATE TABLE IF NOT EXISTS recommendation_metrics (
            id SERIAL PRIMARY KEY,
            request_id VARCHAR(255) NOT NULL,
            crop_type VARCHAR(100) NOT NULL,
            region VARCHAR(100) NOT NULL,
            response_time_ms DECIMAL(10,2) NOT NULL,
            confidence_score DECIMAL(5,3) NOT NULL,
            number_of_recommendations INTEGER NOT NULL,
            user_satisfaction DECIMAL(5,3),
            agricultural_outcome VARCHAR(100),
            timestamp TIMESTAMP DEFAULT NOW()
        );
        
        CREATE TABLE IF NOT EXISTS system_health_metrics (
            id SERIAL PRIMARY KEY,
            cpu_usage_percent DECIMAL(5,2) NOT NULL,
            memory_usage_percent DECIMAL(5,2) NOT NULL,
            disk_usage_percent DECIMAL(5,2) NOT NULL,
            active_connections INTEGER NOT NULL,
            error_rate DECIMAL(5,3) NOT NULL,
            response_time_p95 DECIMAL(10,2) NOT NULL,
            timestamp TIMESTAMP DEFAULT NOW()
        );
        
        CREATE TABLE IF NOT EXISTS alerts (
            id VARCHAR(255) PRIMARY KEY,
            level VARCHAR(20) NOT NULL,
            title VARCHAR(255) NOT NULL,
            message TEXT NOT NULL,
            metric_name VARCHAR(100) NOT NULL,
            threshold_value DECIMAL(10,3) NOT NULL,
            current_value DECIMAL(10,3) NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            resolved BOOLEAN DEFAULT FALSE,
            resolved_at TIMESTAMP,
            tags JSONB
        );
        
        CREATE INDEX IF NOT EXISTS idx_recommendation_metrics_timestamp ON recommendation_metrics(timestamp);
        CREATE INDEX IF NOT EXISTS idx_recommendation_metrics_crop_type ON recommendation_metrics(crop_type);
        CREATE INDEX IF NOT EXISTS idx_system_health_metrics_timestamp ON system_health_metrics(timestamp);
        CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp);
        CREATE INDEX IF NOT EXISTS idx_alerts_resolved ON alerts(resolved);
        """
        
        try:
            with self.db_engine.connect() as conn:
                conn.execute(text(create_tables_sql))
                conn.commit()
            logger.info("Metrics tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create metrics tables: {e}")
    
    async def start_monitoring(self):
        """Start background monitoring tasks."""
        if self.monitoring_active:
            logger.warning("Monitoring is already active")
            return
        
        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Background monitoring started")
    
    async def stop_monitoring(self):
        """Stop background monitoring tasks."""
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Background monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                # Collect system health metrics
                await self._collect_system_health_metrics()
                
                # Check thresholds and generate alerts
                await self._check_thresholds_and_alert()
                
                # Clean up old metrics and alerts
                await self._cleanup_old_data()
                
                # Wait before next iteration
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _collect_system_health_metrics(self):
        """Collect system health metrics."""
        try:
            import psutil
            
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Calculate error rate from recent metrics
            error_rate = await self._calculate_error_rate()
            
            # Calculate P95 response time
            response_time_p95 = await self._calculate_response_time_p95()
            
            # Count active connections (simplified)
            active_connections = len(psutil.net_connections())
            
            health_metrics = SystemHealthMetrics(
                cpu_usage_percent=cpu_percent,
                memory_usage_percent=memory.percent,
                disk_usage_percent=disk.percent,
                active_connections=active_connections,
                error_rate=error_rate,
                response_time_p95=response_time_p95
            )
            
            with self.lock:
                self.system_health_metrics.append(health_metrics)
            
            # Update Prometheus metrics
            if PROMETHEUS_AVAILABLE:
                self.system_cpu_usage.set(cpu_percent)
                self.system_memory_usage.set(memory.percent)
                self.system_disk_usage.set(disk.percent)
                self.active_connections.set(active_connections)
            
            # Store in database
            await self._store_system_health_metrics(health_metrics)
            
        except Exception as e:
            logger.error(f"Error collecting system health metrics: {e}")
    
    async def _calculate_error_rate(self) -> float:
        """Calculate error rate from recent metrics."""
        try:
            with self.lock:
                recent_metrics = list(self.recommendation_metrics)[-100:]  # Last 100 requests
            
            if not recent_metrics:
                return 0.0
            
            error_count = sum(1 for m in recent_metrics if m.confidence_score < 0.5)
            return error_count / len(recent_metrics)
            
        except Exception as e:
            logger.error(f"Error calculating error rate: {e}")
            return 0.0
    
    async def _calculate_response_time_p95(self) -> float:
        """Calculate 95th percentile response time."""
        try:
            with self.lock:
                recent_metrics = list(self.recommendation_metrics)[-100:]  # Last 100 requests
            
            if not recent_metrics:
                return 0.0
            
            response_times = [m.response_time_ms for m in recent_metrics]
            response_times.sort()
            
            p95_index = int(len(response_times) * 0.95)
            return response_times[p95_index] if p95_index < len(response_times) else response_times[-1]
            
        except Exception as e:
            logger.error(f"Error calculating P95 response time: {e}")
            return 0.0
    
    async def _check_thresholds_and_alert(self):
        """Check thresholds and generate alerts."""
        try:
            # Get latest system health metrics
            with self.lock:
                if not self.system_health_metrics:
                    return
                latest_health = self.system_health_metrics[-1]
            
            # Check system resource thresholds
            await self._check_system_resource_thresholds(latest_health)
            
            # Check recommendation quality thresholds
            await self._check_recommendation_quality_thresholds()
            
            # Check data quality thresholds
            await self._check_data_quality_thresholds()
            
        except Exception as e:
            logger.error(f"Error checking thresholds: {e}")
    
    async def _check_system_resource_thresholds(self, health_metrics: SystemHealthMetrics):
        """Check system resource thresholds."""
        # CPU usage
        if health_metrics.cpu_usage_percent >= self.thresholds["cpu_critical_percent"]:
            await self._create_alert(
                AlertLevel.CRITICAL,
                "High CPU Usage",
                f"CPU usage is {health_metrics.cpu_usage_percent:.1f}%, exceeding critical threshold of {self.thresholds['cpu_critical_percent']}%",
                "cpu_usage_percent",
                self.thresholds["cpu_critical_percent"],
                health_metrics.cpu_usage_percent
            )
        elif health_metrics.cpu_usage_percent >= self.thresholds["cpu_warning_percent"]:
            await self._create_alert(
                AlertLevel.WARNING,
                "Elevated CPU Usage",
                f"CPU usage is {health_metrics.cpu_usage_percent:.1f}%, exceeding warning threshold of {self.thresholds['cpu_warning_percent']}%",
                "cpu_usage_percent",
                self.thresholds["cpu_warning_percent"],
                health_metrics.cpu_usage_percent
            )
        
        # Memory usage
        if health_metrics.memory_usage_percent >= self.thresholds["memory_critical_percent"]:
            await self._create_alert(
                AlertLevel.CRITICAL,
                "High Memory Usage",
                f"Memory usage is {health_metrics.memory_usage_percent:.1f}%, exceeding critical threshold of {self.thresholds['memory_critical_percent']}%",
                "memory_usage_percent",
                self.thresholds["memory_critical_percent"],
                health_metrics.memory_usage_percent
            )
        elif health_metrics.memory_usage_percent >= self.thresholds["memory_warning_percent"]:
            await self._create_alert(
                AlertLevel.WARNING,
                "Elevated Memory Usage",
                f"Memory usage is {health_metrics.memory_usage_percent:.1f}%, exceeding warning threshold of {self.thresholds['memory_warning_percent']}%",
                "memory_usage_percent",
                self.thresholds["memory_warning_percent"],
                health_metrics.memory_usage_percent
            )
        
        # Disk usage
        if health_metrics.disk_usage_percent >= self.thresholds["disk_critical_percent"]:
            await self._create_alert(
                AlertLevel.CRITICAL,
                "High Disk Usage",
                f"Disk usage is {health_metrics.disk_usage_percent:.1f}%, exceeding critical threshold of {self.thresholds['disk_critical_percent']}%",
                "disk_usage_percent",
                self.thresholds["disk_critical_percent"],
                health_metrics.disk_usage_percent
            )
        elif health_metrics.disk_usage_percent >= self.thresholds["disk_warning_percent"]:
            await self._create_alert(
                AlertLevel.WARNING,
                "Elevated Disk Usage",
                f"Disk usage is {health_metrics.disk_usage_percent:.1f}%, exceeding warning threshold of {self.thresholds['disk_warning_percent']}%",
                "disk_usage_percent",
                self.thresholds["disk_warning_percent"],
                health_metrics.disk_usage_percent
            )
        
        # Response time
        if health_metrics.response_time_p95 >= self.thresholds["response_time_critical_ms"]:
            await self._create_alert(
                AlertLevel.CRITICAL,
                "Slow Response Time",
                f"P95 response time is {health_metrics.response_time_p95:.1f}ms, exceeding critical threshold of {self.thresholds['response_time_critical_ms']}ms",
                "response_time_p95",
                self.thresholds["response_time_critical_ms"],
                health_metrics.response_time_p95
            )
        elif health_metrics.response_time_p95 >= self.thresholds["response_time_warning_ms"]:
            await self._create_alert(
                AlertLevel.WARNING,
                "Elevated Response Time",
                f"P95 response time is {health_metrics.response_time_p95:.1f}ms, exceeding warning threshold of {self.thresholds['response_time_warning_ms']}ms",
                "response_time_p95",
                self.thresholds["response_time_warning_ms"],
                health_metrics.response_time_p95
            )
        
        # Error rate
        if health_metrics.error_rate >= self.thresholds["error_rate_critical"]:
            await self._create_alert(
                AlertLevel.CRITICAL,
                "High Error Rate",
                f"Error rate is {health_metrics.error_rate:.1%}, exceeding critical threshold of {self.thresholds['error_rate_critical']:.1%}",
                "error_rate",
                self.thresholds["error_rate_critical"],
                health_metrics.error_rate
            )
        elif health_metrics.error_rate >= self.thresholds["error_rate_warning"]:
            await self._create_alert(
                AlertLevel.WARNING,
                "Elevated Error Rate",
                f"Error rate is {health_metrics.error_rate:.1%}, exceeding warning threshold of {self.thresholds['error_rate_warning']:.1%}",
                "error_rate",
                self.thresholds["error_rate_warning"],
                health_metrics.error_rate
            )
    
    async def _check_recommendation_quality_thresholds(self):
        """Check recommendation quality thresholds."""
        try:
            with self.lock:
                recent_metrics = list(self.recommendation_metrics)[-50:]  # Last 50 recommendations
            
            if not recent_metrics:
                return
            
            # Calculate average confidence score
            avg_confidence = sum(m.confidence_score for m in recent_metrics) / len(recent_metrics)
            
            if avg_confidence <= self.thresholds["recommendation_confidence_critical"]:
                await self._create_alert(
                    AlertLevel.CRITICAL,
                    "Low Recommendation Confidence",
                    f"Average recommendation confidence is {avg_confidence:.1%}, below critical threshold of {self.thresholds['recommendation_confidence_critical']:.1%}",
                    "recommendation_confidence",
                    self.thresholds["recommendation_confidence_critical"],
                    avg_confidence
                )
            elif avg_confidence <= self.thresholds["recommendation_confidence_warning"]:
                await self._create_alert(
                    AlertLevel.WARNING,
                    "Reduced Recommendation Confidence",
                    f"Average recommendation confidence is {avg_confidence:.1%}, below warning threshold of {self.thresholds['recommendation_confidence_warning']:.1%}",
                    "recommendation_confidence",
                    self.thresholds["recommendation_confidence_warning"],
                    avg_confidence
                )
            
            # Check user satisfaction if available
            satisfaction_metrics = [m for m in recent_metrics if m.user_satisfaction is not None]
            if satisfaction_metrics:
                avg_satisfaction = sum(m.user_satisfaction for m in satisfaction_metrics) / len(satisfaction_metrics)
                
                if avg_satisfaction <= self.thresholds["user_satisfaction_critical"]:
                    await self._create_alert(
                        AlertLevel.CRITICAL,
                        "Low User Satisfaction",
                        f"Average user satisfaction is {avg_satisfaction:.1%}, below critical threshold of {self.thresholds['user_satisfaction_critical']:.1%}",
                        "user_satisfaction",
                        self.thresholds["user_satisfaction_critical"],
                        avg_satisfaction
                    )
                elif avg_satisfaction <= self.thresholds["user_satisfaction_warning"]:
                    await self._create_alert(
                        AlertLevel.WARNING,
                        "Reduced User Satisfaction",
                        f"Average user satisfaction is {avg_satisfaction:.1%}, below warning threshold of {self.thresholds['user_satisfaction_warning']:.1%}",
                        "user_satisfaction",
                        self.thresholds["user_satisfaction_warning"],
                        avg_satisfaction
                    )
        
        except Exception as e:
            logger.error(f"Error checking recommendation quality thresholds: {e}")
    
    async def _check_data_quality_thresholds(self):
        """Check data quality thresholds."""
        try:
            # Check data freshness (simplified - in production, check actual data sources)
            current_time = datetime.utcnow()
            
            # Simulate data freshness check
            data_freshness_hours = 12  # Assume data is 12 hours old
            
            if data_freshness_hours >= self.thresholds["data_freshness_critical_hours"]:
                await self._create_alert(
                    AlertLevel.CRITICAL,
                    "Stale Data",
                    f"Data is {data_freshness_hours} hours old, exceeding critical threshold of {self.thresholds['data_freshness_critical_hours']} hours",
                    "data_freshness_hours",
                    self.thresholds["data_freshness_critical_hours"],
                    data_freshness_hours
                )
            elif data_freshness_hours >= self.thresholds["data_freshness_warning_hours"]:
                await self._create_alert(
                    AlertLevel.WARNING,
                    "Aging Data",
                    f"Data is {data_freshness_hours} hours old, exceeding warning threshold of {self.thresholds['data_freshness_warning_hours']} hours",
                    "data_freshness_hours",
                    self.thresholds["data_freshness_warning_hours"],
                    data_freshness_hours
                )
        
        except Exception as e:
            logger.error(f"Error checking data quality thresholds: {e}")
    
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
        
        # Send alert to external systems
        await self._send_alert_notification(alert)
        
        # Store alert in database
        await self._store_alert(alert)
    
    async def _send_alert_notification(self, alert: Alert):
        """Send alert notification to external systems."""
        try:
            # Send to Redis pub/sub for real-time notifications
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
                
                await self.redis_client.publish("afas_alerts", json.dumps(alert_data))
            
            # Send to webhook endpoints
            for webhook_url in self.alert_channels["webhook"]:
                try:
                    import aiohttp
                    async with aiohttp.ClientSession() as session:
                        await session.post(webhook_url, json={
                            "alert": alert_data,
                            "service": "crop_variety_recommendations"
                        })
                except Exception as e:
                    logger.error(f"Failed to send webhook alert: {e}")
            
            # Send to Slack (if configured)
            for slack_webhook in self.alert_channels["slack"]:
                try:
                    import aiohttp
                    slack_message = {
                        "text": f"🚨 *{alert.title}*",
                        "attachments": [{
                            "color": "danger" if alert.level == AlertLevel.CRITICAL else "warning",
                            "fields": [
                                {"title": "Message", "value": alert.message, "short": False},
                                {"title": "Metric", "value": alert.metric_name, "short": True},
                                {"title": "Current Value", "value": str(alert.current_value), "short": True},
                                {"title": "Threshold", "value": str(alert.threshold_value), "short": True}
                            ]
                        }]
                    }
                    
                    async with aiohttp.ClientSession() as session:
                        await session.post(slack_webhook, json=slack_message)
                except Exception as e:
                    logger.error(f"Failed to send Slack alert: {e}")
        
        except Exception as e:
            logger.error(f"Error sending alert notification: {e}")
    
    async def _store_alert(self, alert: Alert):
        """Store alert in database."""
        if not self.db_session:
            return
        
        try:
            from sqlalchemy import text
            
            insert_sql = """
            INSERT INTO alerts (id, level, title, message, metric_name, threshold_value, current_value, timestamp, tags)
            VALUES (:id, :level, :title, :message, :metric_name, :threshold_value, :current_value, :timestamp, :tags)
            """
            
            self.db_session.execute(text(insert_sql), {
                "id": alert.id,
                "level": alert.level.value,
                "title": alert.title,
                "message": alert.message,
                "metric_name": alert.metric_name,
                "threshold_value": alert.threshold_value,
                "current_value": alert.current_value,
                "timestamp": alert.timestamp,
                "tags": json.dumps(alert.tags)
            })
            self.db_session.commit()
            
        except Exception as e:
            logger.error(f"Error storing alert: {e}")
            self.db_session.rollback()
    
    async def _store_system_health_metrics(self, health_metrics: SystemHealthMetrics):
        """Store system health metrics in database."""
        if not self.db_session:
            return
        
        try:
            from sqlalchemy import text
            
            insert_sql = """
            INSERT INTO system_health_metrics (cpu_usage_percent, memory_usage_percent, disk_usage_percent, 
                                              active_connections, error_rate, response_time_p95)
            VALUES (:cpu, :memory, :disk, :connections, :error_rate, :response_time)
            """
            
            self.db_session.execute(text(insert_sql), {
                "cpu": health_metrics.cpu_usage_percent,
                "memory": health_metrics.memory_usage_percent,
                "disk": health_metrics.disk_usage_percent,
                "connections": health_metrics.active_connections,
                "error_rate": health_metrics.error_rate,
                "response_time": health_metrics.response_time_p95
            })
            self.db_session.commit()
            
        except Exception as e:
            logger.error(f"Error storing system health metrics: {e}")
            self.db_session.rollback()
    
    async def _cleanup_old_data(self):
        """Clean up old metrics and resolved alerts."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=30)
            
            # Clean up old alerts
            with self.lock:
                self.alerts = [alert for alert in self.alerts 
                             if not (alert.resolved and alert.resolved_at and alert.resolved_at < cutoff_time)]
            
            # Clean up old metrics in database
            if self.db_session:
                from sqlalchemy import text
                
                cleanup_sql = """
                DELETE FROM recommendation_metrics WHERE timestamp < :cutoff_time;
                DELETE FROM system_health_metrics WHERE timestamp < :cutoff_time;
                DELETE FROM alerts WHERE resolved = true AND resolved_at < :cutoff_time;
                """
                
                self.db_session.execute(text(cleanup_sql), {"cutoff_time": cutoff_time})
                self.db_session.commit()
        
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
    
    async def record_recommendation_metrics(self, metrics: RecommendationMetrics):
        """Record metrics for a crop variety recommendation."""
        try:
            with self.lock:
                self.recommendation_metrics.append(metrics)
            
            # Update Prometheus metrics
            if PROMETHEUS_AVAILABLE:
                self.recommendation_counter.labels(
                    crop_type=metrics.crop_type,
                    region=metrics.region,
                    status="success" if metrics.confidence_score > 0.5 else "error"
                ).inc()
                
                self.recommendation_response_time.labels(
                    crop_type=metrics.crop_type,
                    region=metrics.region
                ).observe(metrics.response_time_ms / 1000.0)
                
                self.recommendation_confidence.labels(
                    crop_type=metrics.crop_type,
                    region=metrics.region
                ).observe(metrics.confidence_score)
                
                if metrics.user_satisfaction is not None:
                    self.user_satisfaction.labels(
                        crop_type=metrics.crop_type,
                        region=metrics.region
                    ).observe(metrics.user_satisfaction)
            
            # Store in database
            await self._store_recommendation_metrics(metrics)
            
            logger.debug(f"Recorded recommendation metrics for {metrics.crop_type} in {metrics.region}")
            
        except Exception as e:
            logger.error(f"Error recording recommendation metrics: {e}")
    
    async def _store_recommendation_metrics(self, metrics: RecommendationMetrics):
        """Store recommendation metrics in database."""
        if not self.db_session:
            return
        
        try:
            from sqlalchemy import text
            
            insert_sql = """
            INSERT INTO recommendation_metrics (request_id, crop_type, region, response_time_ms, 
                                              confidence_score, number_of_recommendations, 
                                              user_satisfaction, agricultural_outcome)
            VALUES (:request_id, :crop_type, :region, :response_time_ms, :confidence_score, 
                   :number_of_recommendations, :user_satisfaction, :agricultural_outcome)
            """
            
            self.db_session.execute(text(insert_sql), {
                "request_id": metrics.request_id,
                "crop_type": metrics.crop_type,
                "region": metrics.region,
                "response_time_ms": metrics.response_time_ms,
                "confidence_score": metrics.confidence_score,
                "number_of_recommendations": metrics.number_of_recommendations,
                "user_satisfaction": metrics.user_satisfaction,
                "agricultural_outcome": metrics.agricultural_outcome
            })
            self.db_session.commit()
            
        except Exception as e:
            logger.error(f"Error storing recommendation metrics: {e}")
            self.db_session.rollback()
    
    async def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of current metrics."""
        try:
            with self.lock:
                recent_recommendations = list(self.recommendation_metrics)[-100:]
                recent_health = list(self.system_health_metrics)[-10:]
                active_alerts = [alert for alert in self.alerts if not alert.resolved]
            
            summary = {
                "timestamp": datetime.utcnow().isoformat(),
                "recommendation_metrics": {
                    "total_recommendations": len(self.recommendation_metrics),
                    "recent_recommendations": len(recent_recommendations),
                    "average_confidence": sum(m.confidence_score for m in recent_recommendations) / len(recent_recommendations) if recent_recommendations else 0,
                    "average_response_time_ms": sum(m.response_time_ms for m in recent_recommendations) / len(recent_recommendations) if recent_recommendations else 0,
                    "crop_types": list(set(m.crop_type for m in recent_recommendations)),
                    "regions": list(set(m.region for m in recent_recommendations))
                },
                "system_health": {
                    "current_cpu_percent": recent_health[-1].cpu_usage_percent if recent_health else 0,
                    "current_memory_percent": recent_health[-1].memory_usage_percent if recent_health else 0,
                    "current_disk_percent": recent_health[-1].disk_usage_percent if recent_health else 0,
                    "current_error_rate": recent_health[-1].error_rate if recent_health else 0,
                    "current_response_time_p95": recent_health[-1].response_time_p95 if recent_health else 0
                },
                "alerts": {
                    "total_alerts": len(self.alerts),
                    "active_alerts": len(active_alerts),
                    "critical_alerts": len([a for a in active_alerts if a.level == AlertLevel.CRITICAL]),
                    "warning_alerts": len([a for a in active_alerts if a.level == AlertLevel.WARNING]),
                    "recent_alerts": [{
                        "id": alert.id,
                        "level": alert.level.value,
                        "title": alert.title,
                        "timestamp": alert.timestamp.isoformat()
                    } for alert in active_alerts[-10:]]
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting metrics summary: {e}")
            return {"error": str(e)}
    
    async def get_prometheus_metrics(self) -> str:
        """Get Prometheus metrics in text format."""
        if not PROMETHEUS_AVAILABLE:
            return "# Prometheus client not available\n"
        
        try:
            return generate_latest(self.registry).decode('utf-8')
        except Exception as e:
            logger.error(f"Error generating Prometheus metrics: {e}")
            return f"# Error generating metrics: {e}\n"
    
    def add_alert_channel(self, channel_type: str, endpoint: str):
        """Add an alert notification channel."""
        if channel_type in self.alert_channels:
            self.alert_channels[channel_type].append(endpoint)
            logger.info(f"Added {channel_type} alert channel: {endpoint}")
        else:
            logger.warning(f"Unknown alert channel type: {channel_type}")
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert."""
        try:
            with self.lock:
                for alert in self.alerts:
                    if alert.id == alert_id:
                        alert.resolved = True
                        alert.resolved_at = datetime.utcnow()
                        
                        # Update in database
                        if self.db_session:
                            from sqlalchemy import text
                            update_sql = "UPDATE alerts SET resolved = true, resolved_at = :resolved_at WHERE id = :alert_id"
                            self.db_session.execute(text(update_sql), {
                                "resolved_at": alert.resolved_at,
                                "alert_id": alert_id
                            })
                            self.db_session.commit()
                        
                        logger.info(f"Alert {alert_id} resolved")
                        return True
            
            logger.warning(f"Alert {alert_id} not found")
            return False
            
        except Exception as e:
            logger.error(f"Error resolving alert: {e}")
            return False


# Global instance
comprehensive_monitoring_service = ComprehensiveMonitoringAlertingService()


async def get_monitoring_service() -> ComprehensiveMonitoringAlertingService:
    """Get the global monitoring service instance."""
    return comprehensive_monitoring_service
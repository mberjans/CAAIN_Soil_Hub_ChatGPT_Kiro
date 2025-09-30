"""
Production Monitoring Service for Location Services
TICKET-008_farm-location-input-15.2: Implement production monitoring and optimization

This service provides comprehensive monitoring, analytics, and optimization for location services
including location accuracy monitoring, service performance, user experience metrics, and
automated optimization recommendations.
"""

import asyncio
import logging
import time
import threading
from collections import deque
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics
import psutil
import redis
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

class MonitoringLevel(str, Enum):
    """Monitoring level enumeration."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    ERROR = "error"

class LocationAccuracyLevel(str, Enum):
    """Location accuracy level enumeration."""
    HIGH = "high"  # < 10 meters
    MEDIUM = "medium"  # 10-100 meters
    LOW = "low"  # > 100 meters
    UNKNOWN = "unknown"

@dataclass
class LocationAccuracyMetrics:
    """Location accuracy metrics data structure."""
    timestamp: datetime
    location_id: str
    expected_coordinates: Tuple[float, float]
    actual_coordinates: Tuple[float, float]
    accuracy_meters: float
    accuracy_level: LocationAccuracyLevel
    validation_method: str
    confidence_score: float
    processing_time_ms: float
    user_feedback: Optional[float] = None  # User satisfaction rating

@dataclass
class ServicePerformanceMetrics:
    """Service performance metrics data structure."""
    timestamp: datetime
    service_name: str
    endpoint: str
    response_time_ms: float
    status_code: int
    error_type: Optional[str] = None
    cpu_usage_percent: float = 0.0
    memory_usage_percent: float = 0.0
    active_connections: int = 0
    cache_hit_rate: float = 0.0

@dataclass
class UserExperienceMetrics:
    """User experience metrics data structure."""
    timestamp: datetime
    user_id: str
    session_id: str
    action_type: str  # location_input, geocoding, validation, etc.
    success: bool
    time_to_complete_ms: float
    user_satisfaction: Optional[float] = None
    error_message: Optional[str] = None
    retry_count: int = 0

@dataclass
class OptimizationRecommendation:
    """Optimization recommendation data structure."""
    recommendation_id: str
    category: str  # performance, accuracy, user_experience, cost
    priority: MonitoringLevel
    title: str
    description: str
    current_value: float
    target_value: float
    potential_improvement_percent: float
    implementation_effort: str  # low, medium, high
    estimated_impact: str
    created_at: datetime
    status: str = "pending"  # pending, in_progress, completed, dismissed

@dataclass
class Alert:
    """Alert data structure."""
    alert_id: str
    level: MonitoringLevel
    category: str
    title: str
    message: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class LocationProductionMonitoringService:
    """
    Comprehensive production monitoring service for location services.
    
    Provides monitoring, analytics, and optimization for:
    - Location accuracy and validation
    - Service performance and reliability
    - User experience and satisfaction
    - Automated optimization recommendations
    """
    
    def __init__(self, database_url: str = None, redis_url: str = "redis://localhost:6379"):
        """Initialize the production monitoring service."""
        self.database_url = database_url
        self.redis_url = redis_url
        
        # Metrics storage (using deque for efficient rolling window)
        self.location_accuracy_metrics: deque = deque(maxlen=10000)
        self.service_performance_metrics: deque = deque(maxlen=10000)
        self.user_experience_metrics: deque = deque(maxlen=10000)
        self.optimization_recommendations: List[OptimizationRecommendation] = []
        self.active_alerts: List[Alert] = []
        
        # Performance thresholds
        self.thresholds = {
            # Location accuracy thresholds
            "location_accuracy_warning_meters": 50.0,
            "location_accuracy_critical_meters": 200.0,
            "location_confidence_warning": 0.80,
            "location_confidence_critical": 0.60,
            
            # Service performance thresholds
            "response_time_warning_ms": 2000.0,
            "response_time_critical_ms": 5000.0,
            "error_rate_warning": 0.05,  # 5%
            "error_rate_critical": 0.10,  # 10%
            "cpu_warning_percent": 80.0,
            "cpu_critical_percent": 95.0,
            "memory_warning_percent": 85.0,
            "memory_critical_percent": 95.0,
            
            # User experience thresholds
            "user_satisfaction_warning": 0.80,  # 80%
            "user_satisfaction_critical": 0.70,  # 70%
            "retry_rate_warning": 0.10,  # 10%
            "retry_rate_critical": 0.20,  # 20%
            
            # Cache performance thresholds
            "cache_hit_rate_warning": 0.70,  # 70%
            "cache_hit_rate_critical": 0.50,  # 50%
        }
        
        # Database connection for metrics persistence
        self.db_engine = None
        self.db_session = None
        if database_url:
            self._initialize_database()
        
        # Redis connection for real-time metrics
        self.redis_client = None
        try:
            self.redis_client = redis.from_url(redis_url)
            self.redis_client.ping()
            logger.info("Redis connection established for monitoring")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            self.redis_client = None
        
        # Background monitoring
        self.monitoring_active = False
        self.monitoring_task = None
        
        # Thread safety
        self.lock = threading.Lock()
        
        logger.info("Location production monitoring service initialized")
    
    def _initialize_database(self):
        """Initialize database connection for metrics collection."""
        try:
            self.db_engine = create_engine(self.database_url)
            self.db_session = sessionmaker(bind=self.db_engine)()
            logger.info("Database connection established for monitoring")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            self.db_engine = None
            self.db_session = None
    
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
        """Background monitoring loop."""
        while self.monitoring_active:
            try:
                # Collect system metrics
                await self._collect_system_metrics()
                
                # Analyze metrics and generate alerts
                await self._analyze_metrics()
                
                # Generate optimization recommendations
                await self._generate_optimization_recommendations()
                
                # Persist metrics to database
                await self._persist_metrics()
                
                # Wait before next iteration
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _collect_system_metrics(self):
        """Collect system-level metrics."""
        try:
            # CPU and memory usage
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Store in Redis for real-time access
            if self.redis_client:
                await self._store_redis_metrics({
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory_percent,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    async def _store_redis_metrics(self, metrics: Dict[str, Any]):
        """Store metrics in Redis for real-time access."""
        try:
            if self.redis_client:
                key = f"location_monitoring:{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
                self.redis_client.setex(key, 3600, json.dumps(metrics))  # 1 hour TTL
        except Exception as e:
            logger.error(f"Error storing Redis metrics: {e}")
    
    async def record_location_accuracy(
        self,
        location_id: str,
        expected_coordinates: Tuple[float, float],
        actual_coordinates: Tuple[float, float],
        validation_method: str,
        processing_time_ms: float,
        user_feedback: Optional[float] = None
    ):
        """Record location accuracy metrics."""
        try:
            # Calculate accuracy
            accuracy_meters = self._calculate_distance(
                expected_coordinates, actual_coordinates
            )
            
            # Determine accuracy level
            if accuracy_meters < 10:
                accuracy_level = LocationAccuracyLevel.HIGH
            elif accuracy_meters < 100:
                accuracy_level = LocationAccuracyLevel.MEDIUM
            else:
                accuracy_level = LocationAccuracyLevel.LOW
            
            # Calculate confidence score based on accuracy
            confidence_score = max(0.0, 1.0 - (accuracy_meters / 1000.0))
            
            # Create metrics record
            metrics = LocationAccuracyMetrics(
                timestamp=datetime.utcnow(),
                location_id=location_id,
                expected_coordinates=expected_coordinates,
                actual_coordinates=actual_coordinates,
                accuracy_meters=accuracy_meters,
                accuracy_level=accuracy_level,
                validation_method=validation_method,
                confidence_score=confidence_score,
                processing_time_ms=processing_time_ms,
                user_feedback=user_feedback
            )
            
            # Store metrics
            with self.lock:
                self.location_accuracy_metrics.append(metrics)
            
            # Check for alerts
            await self._check_location_accuracy_alerts(metrics)
            
            logger.debug(f"Recorded location accuracy: {accuracy_meters:.2f}m for {location_id}")
            
        except Exception as e:
            logger.error(f"Error recording location accuracy: {e}")
    
    async def record_service_performance(
        self,
        service_name: str,
        endpoint: str,
        response_time_ms: float,
        status_code: int,
        error_type: Optional[str] = None,
        cache_hit_rate: float = 0.0
    ):
        """Record service performance metrics."""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            
            # Create metrics record
            metrics = ServicePerformanceMetrics(
                timestamp=datetime.utcnow(),
                service_name=service_name,
                endpoint=endpoint,
                response_time_ms=response_time_ms,
                status_code=status_code,
                error_type=error_type,
                cpu_usage_percent=cpu_percent,
                memory_usage_percent=memory_percent,
                cache_hit_rate=cache_hit_rate
            )
            
            # Store metrics
            with self.lock:
                self.service_performance_metrics.append(metrics)
            
            # Check for alerts
            await self._check_service_performance_alerts(metrics)
            
            logger.debug(f"Recorded service performance: {response_time_ms:.2f}ms for {service_name}/{endpoint}")
            
        except Exception as e:
            logger.error(f"Error recording service performance: {e}")
    
    async def record_user_experience(
        self,
        user_id: str,
        session_id: str,
        action_type: str,
        success: bool,
        time_to_complete_ms: float,
        user_satisfaction: Optional[float] = None,
        error_message: Optional[str] = None,
        retry_count: int = 0
    ):
        """Record user experience metrics."""
        try:
            # Create metrics record
            metrics = UserExperienceMetrics(
                timestamp=datetime.utcnow(),
                user_id=user_id,
                session_id=session_id,
                action_type=action_type,
                success=success,
                time_to_complete_ms=time_to_complete_ms,
                user_satisfaction=user_satisfaction,
                error_message=error_message,
                retry_count=retry_count
            )
            
            # Store metrics
            with self.lock:
                self.user_experience_metrics.append(metrics)
            
            # Check for alerts
            await self._check_user_experience_alerts(metrics)
            
            logger.debug(f"Recorded user experience: {action_type} - {'success' if success else 'failure'}")
            
        except Exception as e:
            logger.error(f"Error recording user experience: {e}")
    
    def _calculate_distance(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """Calculate distance between two coordinates in meters using Haversine formula."""
        import math
        
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth's radius in meters
        r = 6371000
        return c * r
    
    async def _check_location_accuracy_alerts(self, metrics: LocationAccuracyMetrics):
        """Check for location accuracy alerts."""
        alerts = []
        
        # Check accuracy thresholds
        if metrics.accuracy_meters > self.thresholds["location_accuracy_critical_meters"]:
            alerts.append(Alert(
                alert_id=f"location_accuracy_critical_{metrics.location_id}_{int(time.time())}",
                level=MonitoringLevel.CRITICAL,
                category="location_accuracy",
                title="Critical Location Accuracy Issue",
                message=f"Location accuracy {metrics.accuracy_meters:.2f}m exceeds critical threshold",
                timestamp=datetime.utcnow(),
                metadata={
                    "location_id": metrics.location_id,
                    "accuracy_meters": metrics.accuracy_meters,
                    "threshold": self.thresholds["location_accuracy_critical_meters"]
                }
            ))
        elif metrics.accuracy_meters > self.thresholds["location_accuracy_warning_meters"]:
            alerts.append(Alert(
                alert_id=f"location_accuracy_warning_{metrics.location_id}_{int(time.time())}",
                level=MonitoringLevel.WARNING,
                category="location_accuracy",
                title="Location Accuracy Warning",
                message=f"Location accuracy {metrics.accuracy_meters:.2f}m exceeds warning threshold",
                timestamp=datetime.utcnow(),
                metadata={
                    "location_id": metrics.location_id,
                    "accuracy_meters": metrics.accuracy_meters,
                    "threshold": self.thresholds["location_accuracy_warning_meters"]
                }
            ))
        
        # Check confidence thresholds
        if metrics.confidence_score < self.thresholds["location_confidence_critical"]:
            alerts.append(Alert(
                alert_id=f"location_confidence_critical_{metrics.location_id}_{int(time.time())}",
                level=MonitoringLevel.CRITICAL,
                category="location_confidence",
                title="Critical Location Confidence Issue",
                message=f"Location confidence {metrics.confidence_score:.2f} below critical threshold",
                timestamp=datetime.utcnow(),
                metadata={
                    "location_id": metrics.location_id,
                    "confidence_score": metrics.confidence_score,
                    "threshold": self.thresholds["location_confidence_critical"]
                }
            ))
        
        # Add alerts
        for alert in alerts:
            await self._add_alert(alert)
    
    async def _check_service_performance_alerts(self, metrics: ServicePerformanceMetrics):
        """Check for service performance alerts."""
        alerts = []
        
        # Check response time thresholds
        if metrics.response_time_ms > self.thresholds["response_time_critical_ms"]:
            alerts.append(Alert(
                alert_id=f"response_time_critical_{metrics.service_name}_{int(time.time())}",
                level=MonitoringLevel.CRITICAL,
                category="service_performance",
                title="Critical Response Time Issue",
                message=f"Response time {metrics.response_time_ms:.2f}ms exceeds critical threshold",
                timestamp=datetime.utcnow(),
                metadata={
                    "service_name": metrics.service_name,
                    "endpoint": metrics.endpoint,
                    "response_time_ms": metrics.response_time_ms,
                    "threshold": self.thresholds["response_time_critical_ms"]
                }
            ))
        elif metrics.response_time_ms > self.thresholds["response_time_warning_ms"]:
            alerts.append(Alert(
                alert_id=f"response_time_warning_{metrics.service_name}_{int(time.time())}",
                level=MonitoringLevel.WARNING,
                category="service_performance",
                title="Response Time Warning",
                message=f"Response time {metrics.response_time_ms:.2f}ms exceeds warning threshold",
                timestamp=datetime.utcnow(),
                metadata={
                    "service_name": metrics.service_name,
                    "endpoint": metrics.endpoint,
                    "response_time_ms": metrics.response_time_ms,
                    "threshold": self.thresholds["response_time_warning_ms"]
                }
            ))
        
        # Check CPU usage
        if metrics.cpu_usage_percent > self.thresholds["cpu_critical_percent"]:
            alerts.append(Alert(
                alert_id=f"cpu_critical_{metrics.service_name}_{int(time.time())}",
                level=MonitoringLevel.CRITICAL,
                category="system_resources",
                title="Critical CPU Usage",
                message=f"CPU usage {metrics.cpu_usage_percent:.1f}% exceeds critical threshold",
                timestamp=datetime.utcnow(),
                metadata={
                    "service_name": metrics.service_name,
                    "cpu_usage_percent": metrics.cpu_usage_percent,
                    "threshold": self.thresholds["cpu_critical_percent"]
                }
            ))
        
        # Check memory usage
        if metrics.memory_usage_percent > self.thresholds["memory_critical_percent"]:
            alerts.append(Alert(
                alert_id=f"memory_critical_{metrics.service_name}_{int(time.time())}",
                level=MonitoringLevel.CRITICAL,
                category="system_resources",
                title="Critical Memory Usage",
                message=f"Memory usage {metrics.memory_usage_percent:.1f}% exceeds critical threshold",
                timestamp=datetime.utcnow(),
                metadata={
                    "service_name": metrics.service_name,
                    "memory_usage_percent": metrics.memory_usage_percent,
                    "threshold": self.thresholds["memory_critical_percent"]
                }
            ))
        
        # Add alerts
        for alert in alerts:
            await self._add_alert(alert)
    
    async def _check_user_experience_alerts(self, metrics: UserExperienceMetrics):
        """Check for user experience alerts."""
        alerts = []
        
        # Check user satisfaction
        if metrics.user_satisfaction is not None:
            if metrics.user_satisfaction < self.thresholds["user_satisfaction_critical"]:
                alerts.append(Alert(
                    alert_id=f"user_satisfaction_critical_{metrics.user_id}_{int(time.time())}",
                    level=MonitoringLevel.CRITICAL,
                    category="user_experience",
                    title="Critical User Satisfaction Issue",
                    message=f"User satisfaction {metrics.user_satisfaction:.2f} below critical threshold",
                    timestamp=datetime.utcnow(),
                    metadata={
                        "user_id": metrics.user_id,
                        "action_type": metrics.action_type,
                        "user_satisfaction": metrics.user_satisfaction,
                        "threshold": self.thresholds["user_satisfaction_critical"]
                    }
                ))
        
        # Check retry rate
        if metrics.retry_count > 3:  # More than 3 retries indicates issues
            alerts.append(Alert(
                alert_id=f"high_retry_rate_{metrics.user_id}_{int(time.time())}",
                level=MonitoringLevel.WARNING,
                category="user_experience",
                title="High Retry Rate Detected",
                message=f"User {metrics.user_id} required {metrics.retry_count} retries for {metrics.action_type}",
                timestamp=datetime.utcnow(),
                metadata={
                    "user_id": metrics.user_id,
                    "action_type": metrics.action_type,
                    "retry_count": metrics.retry_count
                }
            ))
        
        # Add alerts
        for alert in alerts:
            await self._add_alert(alert)
    
    async def _add_alert(self, alert: Alert):
        """Add alert to active alerts list."""
        with self.lock:
            self.active_alerts.append(alert)
        
        # Log alert
        logger.warning(f"ALERT [{alert.level.upper()}] {alert.title}: {alert.message}")
        
        # Store in Redis for real-time access
        if self.redis_client:
            try:
                alert_data = {
                    "alert_id": alert.alert_id,
                    "level": alert.level,
                    "category": alert.category,
                    "title": alert.title,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat(),
                    "metadata": alert.metadata
                }
                self.redis_client.lpush("location_monitoring_alerts", json.dumps(alert_data))
                self.redis_client.ltrim("location_monitoring_alerts", 0, 999)  # Keep last 1000 alerts
            except Exception as e:
                logger.error(f"Error storing alert in Redis: {e}")
    
    async def _analyze_metrics(self):
        """Analyze collected metrics for patterns and trends."""
        try:
            with self.lock:
                # Analyze location accuracy trends
                if len(self.location_accuracy_metrics) > 10:
                    recent_accuracy = list(self.location_accuracy_metrics)[-10:]
                    avg_accuracy = statistics.mean([m.accuracy_meters for m in recent_accuracy])
                    
                    if avg_accuracy > self.thresholds["location_accuracy_warning_meters"]:
                        await self._add_alert(Alert(
                            alert_id=f"accuracy_trend_warning_{int(time.time())}",
                            level=MonitoringLevel.WARNING,
                            category="location_accuracy",
                            title="Location Accuracy Trend Warning",
                            message=f"Average location accuracy {avg_accuracy:.2f}m trending above warning threshold",
                            timestamp=datetime.utcnow(),
                            metadata={"avg_accuracy": avg_accuracy}
                        ))
                
                # Analyze service performance trends
                if len(self.service_performance_metrics) > 10:
                    recent_performance = list(self.service_performance_metrics)[-10:]
                    avg_response_time = statistics.mean([m.response_time_ms for m in recent_performance])
                    error_rate = sum(1 for m in recent_performance if m.status_code >= 400) / len(recent_performance)
                    
                    if avg_response_time > self.thresholds["response_time_warning_ms"]:
                        await self._add_alert(Alert(
                            alert_id=f"response_time_trend_warning_{int(time.time())}",
                            level=MonitoringLevel.WARNING,
                            category="service_performance",
                            title="Response Time Trend Warning",
                            message=f"Average response time {avg_response_time:.2f}ms trending above warning threshold",
                            timestamp=datetime.utcnow(),
                            metadata={"avg_response_time": avg_response_time}
                        ))
                    
                    if error_rate > self.thresholds["error_rate_warning"]:
                        await self._add_alert(Alert(
                            alert_id=f"error_rate_trend_warning_{int(time.time())}",
                            level=MonitoringLevel.WARNING,
                            category="service_performance",
                            title="Error Rate Trend Warning",
                            message=f"Error rate {error_rate:.2%} trending above warning threshold",
                            timestamp=datetime.utcnow(),
                            metadata={"error_rate": error_rate}
                        ))
                
        except Exception as e:
            logger.error(f"Error analyzing metrics: {e}")
    
    async def _generate_optimization_recommendations(self):
        """Generate optimization recommendations based on metrics analysis."""
        try:
            recommendations = []
            
            with self.lock:
                # Analyze location accuracy for optimization opportunities
                if len(self.location_accuracy_metrics) > 50:
                    recent_accuracy = list(self.location_accuracy_metrics)[-50:]
                    avg_accuracy = statistics.mean([m.accuracy_meters for m in recent_accuracy])
                    
                    if avg_accuracy > 25:  # If average accuracy is poor
                        recommendations.append(OptimizationRecommendation(
                            recommendation_id=f"accuracy_optimization_{int(time.time())}",
                            category="accuracy",
                            priority=MonitoringLevel.WARNING,
                            title="Improve Location Accuracy",
                            description=f"Average location accuracy is {avg_accuracy:.2f}m. Consider implementing additional validation methods or improving GPS processing.",
                            current_value=avg_accuracy,
                            target_value=15.0,
                            potential_improvement_percent=40.0,
                            implementation_effort="medium",
                            estimated_impact="High user satisfaction improvement",
                            created_at=datetime.utcnow()
                        ))
                
                # Analyze service performance for optimization opportunities
                if len(self.service_performance_metrics) > 50:
                    recent_performance = list(self.service_performance_metrics)[-50:]
                    avg_response_time = statistics.mean([m.response_time_ms for m in recent_performance])
                    avg_cache_hit_rate = statistics.mean([m.cache_hit_rate for m in recent_performance])
                    
                    if avg_response_time > 1500:  # If response time is slow
                        recommendations.append(OptimizationRecommendation(
                            recommendation_id=f"performance_optimization_{int(time.time())}",
                            category="performance",
                            priority=MonitoringLevel.WARNING,
                            title="Optimize Service Performance",
                            description=f"Average response time is {avg_response_time:.2f}ms. Consider implementing caching, database optimization, or async processing.",
                            current_value=avg_response_time,
                            target_value=800.0,
                            potential_improvement_percent=47.0,
                            implementation_effort="high",
                            estimated_impact="Significant performance improvement",
                            created_at=datetime.utcnow()
                        ))
                    
                    if avg_cache_hit_rate < 0.6:  # If cache hit rate is low
                        recommendations.append(OptimizationRecommendation(
                            recommendation_id=f"cache_optimization_{int(time.time())}",
                            category="performance",
                            priority=MonitoringLevel.INFO,
                            title="Improve Cache Hit Rate",
                            description=f"Cache hit rate is {avg_cache_hit_rate:.2%}. Consider expanding cache coverage or optimizing cache keys.",
                            current_value=avg_cache_hit_rate,
                            target_value=0.8,
                            potential_improvement_percent=33.0,
                            implementation_effort="low",
                            estimated_impact="Reduced database load and faster responses",
                            created_at=datetime.utcnow()
                        ))
                
                # Analyze user experience for optimization opportunities
                if len(self.user_experience_metrics) > 50:
                    recent_ux = list(self.user_experience_metrics)[-50:]
                    success_rate = sum(1 for m in recent_ux if m.success) / len(recent_ux)
                    avg_satisfaction = statistics.mean([m.user_satisfaction for m in recent_ux if m.user_satisfaction is not None])
                    
                    if success_rate < 0.9:  # If success rate is low
                        recommendations.append(OptimizationRecommendation(
                            recommendation_id=f"ux_optimization_{int(time.time())}",
                            category="user_experience",
                            priority=MonitoringLevel.WARNING,
                            title="Improve User Success Rate",
                            description=f"User success rate is {success_rate:.2%}. Consider improving error handling, validation, or user guidance.",
                            current_value=success_rate,
                            target_value=0.95,
                            potential_improvement_percent=5.6,
                            implementation_effort="medium",
                            estimated_impact="Better user retention and satisfaction",
                            created_at=datetime.utcnow()
                        ))
            
            # Add new recommendations
            for rec in recommendations:
                if not any(existing.recommendation_id == rec.recommendation_id for existing in self.optimization_recommendations):
                    self.optimization_recommendations.append(rec)
                    logger.info(f"Generated optimization recommendation: {rec.title}")
            
        except Exception as e:
            logger.error(f"Error generating optimization recommendations: {e}")
    
    async def _persist_metrics(self):
        """Persist metrics to database."""
        if not self.db_session:
            return
        
        try:
            # This would implement database persistence
            # For now, we'll just log that persistence would happen
            logger.debug("Metrics persistence would occur here")
            
        except Exception as e:
            logger.error(f"Error persisting metrics: {e}")
    
    async def get_monitoring_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive monitoring dashboard data."""
        try:
            with self.lock:
                # Calculate current metrics
                current_time = datetime.utcnow()
                last_hour = current_time - timedelta(hours=1)
                
                # Location accuracy metrics
                recent_accuracy = [m for m in self.location_accuracy_metrics if m.timestamp > last_hour]
                avg_accuracy = statistics.mean([m.accuracy_meters for m in recent_accuracy]) if recent_accuracy else 0
                accuracy_distribution = {
                    "high": sum(1 for m in recent_accuracy if m.accuracy_level == LocationAccuracyLevel.HIGH),
                    "medium": sum(1 for m in recent_accuracy if m.accuracy_level == LocationAccuracyLevel.MEDIUM),
                    "low": sum(1 for m in recent_accuracy if m.accuracy_level == LocationAccuracyLevel.LOW)
                }
                
                # Service performance metrics
                recent_performance = [m for m in self.service_performance_metrics if m.timestamp > last_hour]
                avg_response_time = statistics.mean([m.response_time_ms for m in recent_performance]) if recent_performance else 0
                error_rate = sum(1 for m in recent_performance if m.status_code >= 400) / len(recent_performance) if recent_performance else 0
                avg_cache_hit_rate = statistics.mean([m.cache_hit_rate for m in recent_performance]) if recent_performance else 0
                
                # User experience metrics
                recent_ux = [m for m in self.user_experience_metrics if m.timestamp > last_hour]
                success_rate = sum(1 for m in recent_ux if m.success) / len(recent_ux) if recent_ux else 0
                avg_satisfaction = statistics.mean([m.user_satisfaction for m in recent_ux if m.user_satisfaction is not None]) if recent_ux else 0
                
                # Active alerts
                active_alerts = [alert for alert in self.active_alerts if not alert.resolved]
                
                # Recent optimization recommendations
                recent_recommendations = [rec for rec in self.optimization_recommendations if rec.created_at > last_hour]
                
                return {
                    "timestamp": current_time.isoformat(),
                    "location_accuracy": {
                        "average_accuracy_meters": avg_accuracy,
                        "accuracy_distribution": accuracy_distribution,
                        "total_validations": len(recent_accuracy)
                    },
                    "service_performance": {
                        "average_response_time_ms": avg_response_time,
                        "error_rate": error_rate,
                        "cache_hit_rate": avg_cache_hit_rate,
                        "total_requests": len(recent_performance)
                    },
                    "user_experience": {
                        "success_rate": success_rate,
                        "average_satisfaction": avg_satisfaction,
                        "total_actions": len(recent_ux)
                    },
                    "alerts": {
                        "active_count": len(active_alerts),
                        "critical_count": sum(1 for a in active_alerts if a.level == MonitoringLevel.CRITICAL),
                        "warning_count": sum(1 for a in active_alerts if a.level == MonitoringLevel.WARNING),
                        "recent_alerts": [
                            {
                                "level": alert.level,
                                "title": alert.title,
                                "message": alert.message,
                                "timestamp": alert.timestamp.isoformat()
                            } for alert in active_alerts[-10:]  # Last 10 alerts
                        ]
                    },
                    "optimization_recommendations": {
                        "total_count": len(self.optimization_recommendations),
                        "pending_count": sum(1 for r in self.optimization_recommendations if r.status == "pending"),
                        "recent_recommendations": [
                            {
                                "category": rec.category,
                                "priority": rec.priority,
                                "title": rec.title,
                                "description": rec.description,
                                "potential_improvement_percent": rec.potential_improvement_percent,
                                "created_at": rec.created_at.isoformat()
                            } for rec in recent_recommendations[-5:]  # Last 5 recommendations
                        ]
                    }
                }
                
        except Exception as e:
            logger.error(f"Error getting monitoring dashboard data: {e}")
            return {"error": str(e)}
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert."""
        try:
            with self.lock:
                for alert in self.active_alerts:
                    if alert.alert_id == alert_id:
                        alert.resolved = True
                        alert.resolved_at = datetime.utcnow()
                        logger.info(f"Resolved alert: {alert.title}")
                        return True
            return False
        except Exception as e:
            logger.error(f"Error resolving alert: {e}")
            return False
    
    async def update_recommendation_status(self, recommendation_id: str, status: str) -> bool:
        """Update optimization recommendation status."""
        try:
            with self.lock:
                for rec in self.optimization_recommendations:
                    if rec.recommendation_id == recommendation_id:
                        rec.status = status
                        logger.info(f"Updated recommendation status: {rec.title} -> {status}")
                        return True
            return False
        except Exception as e:
            logger.error(f"Error updating recommendation status: {e}")
            return False
    
    def get_thresholds(self) -> Dict[str, float]:
        """Get current monitoring thresholds."""
        return self.thresholds.copy()
    
    def update_thresholds(self, new_thresholds: Dict[str, float]):
        """Update monitoring thresholds."""
        with self.lock:
            self.thresholds.update(new_thresholds)
        logger.info("Updated monitoring thresholds")
    
    async def cleanup_old_metrics(self, days_to_keep: int = 30):
        """Clean up old metrics to prevent memory issues."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=days_to_keep)
            
            with self.lock:
                # Clean up location accuracy metrics
                self.location_accuracy_metrics = deque(
                    [m for m in self.location_accuracy_metrics if m.timestamp > cutoff_time],
                    maxlen=10000
                )
                
                # Clean up service performance metrics
                self.service_performance_metrics = deque(
                    [m for m in self.service_performance_metrics if m.timestamp > cutoff_time],
                    maxlen=10000
                )
                
                # Clean up user experience metrics
                self.user_experience_metrics = deque(
                    [m for m in self.user_experience_metrics if m.timestamp > cutoff_time],
                    maxlen=10000
                )
                
                # Clean up old alerts
                self.active_alerts = [a for a in self.active_alerts if a.timestamp > cutoff_time]
            
            logger.info(f"Cleaned up metrics older than {days_to_keep} days")
            
        except Exception as e:
            logger.error(f"Error cleaning up old metrics: {e}")
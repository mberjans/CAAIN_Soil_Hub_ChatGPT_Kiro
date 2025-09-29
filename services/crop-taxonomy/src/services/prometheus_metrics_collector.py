"""
Prometheus Metrics Collector for Variety Recommendations

This service provides comprehensive Prometheus metrics collection for the variety recommendations system.
Integrates with the existing monitoring infrastructure and provides agricultural-specific metrics.

TICKET-005_crop-variety-recommendations-15.2: Implement comprehensive monitoring and analytics
"""

import time
import logging
from typing import Dict, Any, Optional
from prometheus_client import (
    Counter, Histogram, Gauge, Summary, Info,
    CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
)
from datetime import datetime, timedelta
import threading

logger = logging.getLogger(__name__)


class VarietyRecommendationsMetricsCollector:
    """Prometheus metrics collector for variety recommendations system."""
    
    def __init__(self):
        """Initialize the metrics collector."""
        self.registry = CollectorRegistry()
        self._initialize_metrics()
        self.lock = threading.Lock()
        
        logger.info("Variety recommendations Prometheus metrics collector initialized")
    
    def _initialize_metrics(self):
        """Initialize all Prometheus metrics."""
        
        # System Health Metrics
        self.cpu_percent = Gauge(
            'variety_recommendations_cpu_percent',
            'CPU usage percentage',
            registry=self.registry
        )
        
        self.memory_percent = Gauge(
            'variety_recommendations_memory_percent',
            'Memory usage percentage',
            registry=self.registry
        )
        
        self.memory_used_mb = Gauge(
            'variety_recommendations_memory_used_mb',
            'Memory used in MB',
            registry=self.registry
        )
        
        self.disk_usage_percent = Gauge(
            'variety_recommendations_disk_usage_percent',
            'Disk usage percentage',
            registry=self.registry
        )
        
        self.active_connections = Gauge(
            'variety_recommendations_active_connections',
            'Number of active database connections',
            registry=self.registry
        )
        
        # Performance Metrics
        self.response_time_ms = Histogram(
            'variety_recommendations_response_time_ms',
            'Response time in milliseconds',
            buckets=[100, 250, 500, 1000, 2000, 5000, 10000],
            registry=self.registry
        )
        
        self.error_rate = Gauge(
            'variety_recommendations_error_rate',
            'Error rate percentage',
            registry=self.registry
        )
        
        self.request_count = Counter(
            'variety_recommendations_requests_total',
            'Total number of requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        
        # User Engagement Metrics
        self.active_users = Gauge(
            'variety_recommendations_active_users',
            'Number of active users',
            registry=self.registry
        )
        
        self.new_users = Gauge(
            'variety_recommendations_new_users',
            'Number of new users',
            registry=self.registry
        )
        
        self.returning_users = Gauge(
            'variety_recommendations_returning_users',
            'Number of returning users',
            registry=self.registry
        )
        
        self.session_duration_minutes = Histogram(
            'variety_recommendations_session_duration_minutes',
            'User session duration in minutes',
            buckets=[1, 5, 10, 30, 60, 120, 300],
            registry=self.registry
        )
        
        self.user_satisfaction_score = Gauge(
            'variety_recommendations_user_satisfaction_score',
            'User satisfaction score (0-1)',
            registry=self.registry
        )
        
        # Recommendation Effectiveness Metrics
        self.total_recommendations = Counter(
            'variety_recommendations_total_recommendations',
            'Total number of recommendations generated',
            ['crop_type', 'region'],
            registry=self.registry
        )
        
        self.successful_recommendations = Counter(
            'variety_recommendations_successful_recommendations',
            'Number of successful recommendations',
            ['crop_type', 'region'],
            registry=self.registry
        )
        
        self.failed_recommendations = Counter(
            'variety_recommendations_failed_recommendations',
            'Number of failed recommendations',
            ['crop_type', 'region', 'error_type'],
            registry=self.registry
        )
        
        self.confidence_score = Histogram(
            'variety_recommendations_confidence_score',
            'Recommendation confidence score',
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            registry=self.registry
        )
        
        self.cache_hit_rate = Gauge(
            'variety_recommendations_cache_hit_rate',
            'Cache hit rate percentage',
            registry=self.registry
        )
        
        self.expert_validation_rate = Gauge(
            'variety_recommendations_expert_validation_rate',
            'Expert validation rate percentage',
            registry=self.registry
        )
        
        self.farmer_feedback_score = Gauge(
            'variety_recommendations_farmer_feedback_score',
            'Farmer feedback score (0-1)',
            registry=self.registry
        )
        
        # Business Metrics
        self.revenue_impact = Gauge(
            'variety_recommendations_revenue_impact',
            'Total revenue impact in USD',
            registry=self.registry
        )
        
        self.cost_savings = Gauge(
            'variety_recommendations_cost_savings',
            'Estimated cost savings in USD',
            registry=self.registry
        )
        
        self.environmental_impact_score = Gauge(
            'variety_recommendations_environmental_impact_score',
            'Environmental impact score (0-1)',
            registry=self.registry
        )
        
        self.user_retention_rate = Gauge(
            'variety_recommendations_user_retention_rate',
            'User retention rate percentage',
            registry=self.registry
        )
        
        self.market_penetration = Gauge(
            'variety_recommendations_market_penetration',
            'Market penetration percentage',
            registry=self.registry
        )
        
        # Alert Metrics
        self.alerts_total = Gauge(
            'variety_recommendations_alerts_total',
            'Total number of alerts',
            ['level'],
            registry=self.registry
        )
        
        self.alerts_critical = Gauge(
            'variety_recommendations_alerts_critical',
            'Number of critical alerts',
            registry=self.registry
        )
        
        self.alerts_warning = Gauge(
            'variety_recommendations_alerts_warning',
            'Number of warning alerts',
            registry=self.registry
        )
        
        self.alerts_info = Gauge(
            'variety_recommendations_alerts_info',
            'Number of info alerts',
            registry=self.registry
        )
        
        # Agricultural-Specific Metrics
        self.crop_variety_searches = Counter(
            'variety_recommendations_crop_variety_searches_total',
            'Total crop variety searches',
            ['crop_type', 'search_type'],
            registry=self.registry
        )
        
        self.climate_zone_detections = Counter(
            'variety_recommendations_climate_zone_detections_total',
            'Total climate zone detections',
            ['zone_type', 'confidence_level'],
            registry=self.registry
        )
        
        self.soil_analysis_requests = Counter(
            'variety_recommendations_soil_analysis_requests_total',
            'Total soil analysis requests',
            ['analysis_type'],
            registry=self.registry
        )
        
        self.recommendation_acceptance_rate = Gauge(
            'variety_recommendations_acceptance_rate',
            'Recommendation acceptance rate percentage',
            registry=self.registry
        )
        
        # Data Quality Metrics
        self.data_freshness_hours = Gauge(
            'variety_recommendations_data_freshness_hours',
            'Data freshness in hours',
            ['data_source'],
            registry=self.registry
        )
        
        self.external_api_success_rate = Gauge(
            'variety_recommendations_external_api_success_rate',
            'External API success rate percentage',
            ['api_name'],
            registry=self.registry
        )
        
        # System Info
        self.system_info = Info(
            'variety_recommendations_system_info',
            'System information',
            registry=self.registry
        )
        
        # Set system info
        self.system_info.info({
            'version': '1.0.0',
            'service': 'variety-recommendations',
            'environment': 'production'
        })
    
    def update_system_health_metrics(self, metrics: Dict[str, Any]):
        """Update system health metrics."""
        with self.lock:
            self.cpu_percent.set(metrics.get('cpu_percent', 0))
            self.memory_percent.set(metrics.get('memory_percent', 0))
            self.memory_used_mb.set(metrics.get('memory_used_mb', 0))
            self.disk_usage_percent.set(metrics.get('disk_usage_percent', 0))
            self.active_connections.set(metrics.get('active_connections', 0))
            self.response_time_ms.observe(metrics.get('response_time_ms', 0))
            self.error_rate.set(metrics.get('error_rate', 0))
    
    def update_user_engagement_metrics(self, metrics: Dict[str, Any]):
        """Update user engagement metrics."""
        with self.lock:
            self.active_users.set(metrics.get('active_users', 0))
            self.new_users.set(metrics.get('new_users', 0))
            self.returning_users.set(metrics.get('returning_users', 0))
            self.session_duration_minutes.observe(metrics.get('session_duration_minutes', 0))
            self.user_satisfaction_score.set(metrics.get('user_satisfaction_score', 0))
    
    def update_recommendation_effectiveness_metrics(self, metrics: Dict[str, Any]):
        """Update recommendation effectiveness metrics."""
        with self.lock:
            # Update counters
            crop_type = metrics.get('crop_type', 'unknown')
            region = metrics.get('region', 'unknown')
            
            if metrics.get('total_recommendations', 0) > 0:
                self.total_recommendations.labels(
                    crop_type=crop_type,
                    region=region
                ).inc(metrics['total_recommendations'])
            
            if metrics.get('successful_recommendations', 0) > 0:
                self.successful_recommendations.labels(
                    crop_type=crop_type,
                    region=region
                ).inc(metrics['successful_recommendations'])
            
            if metrics.get('failed_recommendations', 0) > 0:
                error_type = metrics.get('error_type', 'unknown')
                self.failed_recommendations.labels(
                    crop_type=crop_type,
                    region=region,
                    error_type=error_type
                ).inc(metrics['failed_recommendations'])
            
            # Update gauges and histograms
            self.confidence_score.observe(metrics.get('average_confidence_score', 0))
            self.cache_hit_rate.set(metrics.get('cache_hit_rate', 0))
            self.expert_validation_rate.set(metrics.get('expert_validation_rate', 0))
            self.farmer_feedback_score.set(metrics.get('farmer_feedback_score', 0))
    
    def update_business_metrics(self, metrics: Dict[str, Any]):
        """Update business metrics."""
        with self.lock:
            self.revenue_impact.set(metrics.get('total_revenue_impact', 0))
            self.cost_savings.set(metrics.get('cost_savings_estimated', 0))
            self.environmental_impact_score.set(metrics.get('environmental_impact_score', 0))
            self.user_retention_rate.set(metrics.get('user_retention_rate', 0))
            self.market_penetration.set(metrics.get('market_penetration', 0))
    
    def update_alert_metrics(self, alerts: Dict[str, Any]):
        """Update alert metrics."""
        with self.lock:
            self.alerts_total.labels(level='critical').set(alerts.get('critical_alerts', 0))
            self.alerts_total.labels(level='warning').set(alerts.get('warning_alerts', 0))
            self.alerts_total.labels(level='info').set(alerts.get('info_alerts', 0))
            
            self.alerts_critical.set(alerts.get('critical_alerts', 0))
            self.alerts_warning.set(alerts.get('warning_alerts', 0))
            self.alerts_info.set(alerts.get('info_alerts', 0))
    
    def record_request(self, method: str, endpoint: str, status: str, duration_ms: float):
        """Record a request metric."""
        with self.lock:
            self.request_count.labels(
                method=method,
                endpoint=endpoint,
                status=status
            ).inc()
            
            self.response_time_ms.observe(duration_ms)
    
    def record_crop_variety_search(self, crop_type: str, search_type: str):
        """Record a crop variety search."""
        with self.lock:
            self.crop_variety_searches.labels(
                crop_type=crop_type,
                search_type=search_type
            ).inc()
    
    def record_climate_zone_detection(self, zone_type: str, confidence_level: str):
        """Record a climate zone detection."""
        with self.lock:
            self.climate_zone_detections.labels(
                zone_type=zone_type,
                confidence_level=confidence_level
            ).inc()
    
    def record_soil_analysis_request(self, analysis_type: str):
        """Record a soil analysis request."""
        with self.lock:
            self.soil_analysis_requests.labels(
                analysis_type=analysis_type
            ).inc()
    
    def update_data_freshness(self, data_source: str, freshness_hours: float):
        """Update data freshness metric."""
        with self.lock:
            self.data_freshness_hours.labels(
                data_source=data_source
            ).set(freshness_hours)
    
    def update_external_api_success_rate(self, api_name: str, success_rate: float):
        """Update external API success rate."""
        with self.lock:
            self.external_api_success_rate.labels(
                api_name=api_name
            ).set(success_rate)
    
    def update_recommendation_acceptance_rate(self, acceptance_rate: float):
        """Update recommendation acceptance rate."""
        with self.lock:
            self.recommendation_acceptance_rate.set(acceptance_rate)
    
    def get_metrics(self) -> str:
        """Get metrics in Prometheus format."""
        return generate_latest(self.registry).decode('utf-8')
    
    def get_content_type(self) -> str:
        """Get content type for metrics response."""
        return CONTENT_TYPE_LATEST


# Singleton instance for global access
metrics_collector: Optional[VarietyRecommendationsMetricsCollector] = None


def get_metrics_collector() -> VarietyRecommendationsMetricsCollector:
    """Get or create the global metrics collector instance."""
    global metrics_collector
    
    if metrics_collector is None:
        metrics_collector = VarietyRecommendationsMetricsCollector()
    
    return metrics_collector


# Context manager for request timing
class RequestTimer:
    """Context manager for timing requests."""
    
    def __init__(self, method: str, endpoint: str):
        self.method = method
        self.endpoint = endpoint
        self.start_time = None
        self.metrics_collector = get_metrics_collector()
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration_ms = (time.time() - self.start_time) * 1000
            status = 'success' if exc_type is None else 'error'
            
            self.metrics_collector.record_request(
                method=self.method,
                endpoint=self.endpoint,
                status=status,
                duration_ms=duration_ms
            )


# Decorator for automatic metrics collection
def collect_metrics(operation_name: str, crop_type: str = 'unknown', region: str = 'unknown'):
    """Decorator for automatic metrics collection."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            metrics_collector = get_metrics_collector()
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                # Record successful operation
                metrics_collector.update_recommendation_effectiveness_metrics({
                    'total_recommendations': 1,
                    'successful_recommendations': 1,
                    'crop_type': crop_type,
                    'region': region,
                    'average_confidence_score': kwargs.get('confidence_score', 0.8)
                })
                
                return result
                
            except Exception as e:
                # Record failed operation
                metrics_collector.update_recommendation_effectiveness_metrics({
                    'total_recommendations': 1,
                    'failed_recommendations': 1,
                    'crop_type': crop_type,
                    'region': region,
                    'error_type': type(e).__name__
                })
                raise
            
            finally:
                duration_ms = (time.time() - start_time) * 1000
                metrics_collector.response_time_ms.observe(duration_ms)
        
        return wrapper
    return decorator
"""
Prometheus Metrics Collector for Location Services
TICKET-008_farm-location-input-15.2: Implement production monitoring and optimization

This service provides Prometheus-compatible metrics collection for location services
including location accuracy, service performance, user experience, and business metrics.
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import threading
from contextlib import asynccontextmanager
from functools import wraps

try:
    from prometheus_client import (
        Counter, Histogram, Gauge, Summary, Info,
        CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Prometheus client not available. Install with: pip install prometheus-client")

logger = logging.getLogger(__name__)

class MetricType(str, Enum):
    """Metric type enumeration."""
    COUNTER = "counter"
    HISTOGRAM = "histogram"
    GAUGE = "gauge"
    SUMMARY = "summary"
    INFO = "info"

@dataclass
class MetricConfig:
    """Metric configuration data structure."""
    name: str
    description: str
    metric_type: MetricType
    labels: List[str] = None
    buckets: List[float] = None  # For histogram
    registry: Optional[CollectorRegistry] = None

class LocationPrometheusMetricsCollector:
    """
    Prometheus metrics collector for location services.
    
    Provides comprehensive metrics collection including:
    - Location accuracy metrics
    - Service performance metrics
    - User experience metrics
    - Business metrics
    - System resource metrics
    """
    
    def __init__(self, registry: Optional[CollectorRegistry] = None):
        """Initialize the Prometheus metrics collector."""
        if not PROMETHEUS_AVAILABLE:
            raise ImportError("Prometheus client not available. Install with: pip install prometheus-client")
        
        self.registry = registry or CollectorRegistry()
        self.metrics: Dict[str, Any] = {}
        self.lock = threading.Lock()
        
        # Initialize metrics
        self._initialize_metrics()
        
        logger.info("Location Prometheus metrics collector initialized")
    
    def _initialize_metrics(self):
        """Initialize all Prometheus metrics."""
        try:
            # Location accuracy metrics
            self.metrics["location_accuracy_meters"] = Histogram(
                "location_accuracy_meters",
                "Location accuracy in meters",
                ["validation_method", "accuracy_level"],
                buckets=[1, 5, 10, 25, 50, 100, 250, 500, 1000],
                registry=self.registry
            )
            
            self.metrics["location_validation_total"] = Counter(
                "location_validation_total",
                "Total number of location validations",
                ["validation_method", "result"],
                registry=self.registry
            )
            
            self.metrics["location_confidence_score"] = Histogram(
                "location_confidence_score",
                "Location confidence score (0-1)",
                ["validation_method"],
                buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                registry=self.registry
            )
            
            # Service performance metrics
            self.metrics["location_service_request_duration_seconds"] = Histogram(
                "location_service_request_duration_seconds",
                "Request duration for location services",
                ["service_name", "endpoint", "method"],
                buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 25.0, 50.0],
                registry=self.registry
            )
            
            self.metrics["location_service_requests_total"] = Counter(
                "location_service_requests_total",
                "Total number of location service requests",
                ["service_name", "endpoint", "method", "status_code"],
                registry=self.registry
            )
            
            self.metrics["location_service_active_connections"] = Gauge(
                "location_service_active_connections",
                "Number of active connections to location services",
                ["service_name"],
                registry=self.registry
            )
            
            # Cache performance metrics
            self.metrics["location_cache_hits_total"] = Counter(
                "location_cache_hits_total",
                "Total number of location cache hits",
                ["cache_type", "service_name"],
                registry=self.registry
            )
            
            self.metrics["location_cache_misses_total"] = Counter(
                "location_cache_misses_total",
                "Total number of location cache misses",
                ["cache_type", "service_name"],
                registry=self.registry
            )
            
            self.metrics["location_cache_hit_rate"] = Gauge(
                "location_cache_hit_rate",
                "Location cache hit rate (0-1)",
                ["cache_type", "service_name"],
                registry=self.registry
            )
            
            # User experience metrics
            self.metrics["location_user_actions_total"] = Counter(
                "location_user_actions_total",
                "Total number of user actions",
                ["action_type", "result"],
                registry=self.registry
            )
            
            self.metrics["location_user_satisfaction"] = Histogram(
                "location_user_satisfaction",
                "User satisfaction rating (0-1)",
                ["action_type"],
                buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                registry=self.registry
            )
            
            self.metrics["location_user_session_duration_seconds"] = Histogram(
                "location_user_session_duration_seconds",
                "User session duration for location services",
                ["user_type"],
                buckets=[30, 60, 300, 600, 1800, 3600, 7200],
                registry=self.registry
            )
            
            # Business metrics
            self.metrics["location_business_revenue_impact"] = Gauge(
                "location_business_revenue_impact",
                "Revenue impact from location services (USD)",
                ["period"],
                registry=self.registry
            )
            
            self.metrics["location_business_cost_savings"] = Gauge(
                "location_business_cost_savings",
                "Cost savings from location services (USD)",
                ["period"],
                registry=self.registry
            )
            
            self.metrics["location_business_user_growth"] = Gauge(
                "location_business_user_growth",
                "User growth rate for location services (percentage)",
                ["period"],
                registry=self.registry
            )
            
            # System resource metrics
            self.metrics["location_system_cpu_usage_percent"] = Gauge(
                "location_system_cpu_usage_percent",
                "CPU usage percentage for location services",
                ["service_name"],
                registry=self.registry
            )
            
            self.metrics["location_system_memory_usage_percent"] = Gauge(
                "location_system_memory_usage_percent",
                "Memory usage percentage for location services",
                ["service_name"],
                registry=self.registry
            )
            
            self.metrics["location_system_disk_usage_percent"] = Gauge(
                "location_system_disk_usage_percent",
                "Disk usage percentage for location services",
                ["service_name"],
                registry=self.registry
            )
            
            # Error and alert metrics
            self.metrics["location_errors_total"] = Counter(
                "location_errors_total",
                "Total number of location service errors",
                ["error_type", "service_name", "severity"],
                registry=self.registry
            )
            
            self.metrics["location_alerts_active"] = Gauge(
                "location_alerts_active",
                "Number of active alerts for location services",
                ["alert_level", "category"],
                registry=self.registry
            )
            
            # Geocoding specific metrics
            self.metrics["geocoding_requests_total"] = Counter(
                "geocoding_requests_total",
                "Total number of geocoding requests",
                ["provider", "result"],
                registry=self.registry
            )
            
            self.metrics["geocoding_response_time_seconds"] = Histogram(
                "geocoding_response_time_seconds",
                "Geocoding response time",
                ["provider"],
                buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
                registry=self.registry
            )
            
            # GPS specific metrics
            self.metrics["gps_accuracy_meters"] = Histogram(
                "gps_accuracy_meters",
                "GPS accuracy in meters",
                ["device_type", "environment"],
                buckets=[1, 3, 5, 10, 20, 50, 100],
                registry=self.registry
            )
            
            self.metrics["gps_fix_time_seconds"] = Histogram(
                "gps_fix_time_seconds",
                "Time to get GPS fix",
                ["device_type", "environment"],
                buckets=[1, 3, 5, 10, 30, 60, 120],
                registry=self.registry
            )
            
            logger.info("Initialized Prometheus metrics for location services")
            
        except Exception as e:
            logger.error(f"Error initializing Prometheus metrics: {e}")
            raise
    
    def record_location_accuracy(
        self,
        accuracy_meters: float,
        validation_method: str,
        accuracy_level: str,
        confidence_score: float
    ):
        """Record location accuracy metrics."""
        try:
            with self.lock:
                self.metrics["location_accuracy_meters"].labels(
                    validation_method=validation_method,
                    accuracy_level=accuracy_level
                ).observe(accuracy_meters)
                
                self.metrics["location_confidence_score"].labels(
                    validation_method=validation_method
                ).observe(confidence_score)
                
        except Exception as e:
            logger.error(f"Error recording location accuracy metrics: {e}")
    
    def record_location_validation(
        self,
        validation_method: str,
        result: str
    ):
        """Record location validation metrics."""
        try:
            with self.lock:
                self.metrics["location_validation_total"].labels(
                    validation_method=validation_method,
                    result=result
                ).inc()
                
        except Exception as e:
            logger.error(f"Error recording location validation metrics: {e}")
    
    def record_service_request(
        self,
        service_name: str,
        endpoint: str,
        method: str,
        status_code: int,
        duration_seconds: float
    ):
        """Record service request metrics."""
        try:
            with self.lock:
                self.metrics["location_service_request_duration_seconds"].labels(
                    service_name=service_name,
                    endpoint=endpoint,
                    method=method
                ).observe(duration_seconds)
                
                self.metrics["location_service_requests_total"].labels(
                    service_name=service_name,
                    endpoint=endpoint,
                    method=method,
                    status_code=str(status_code)
                ).inc()
                
        except Exception as e:
            logger.error(f"Error recording service request metrics: {e}")
    
    def record_cache_metrics(
        self,
        cache_type: str,
        service_name: str,
        hit: bool
    ):
        """Record cache performance metrics."""
        try:
            with self.lock:
                if hit:
                    self.metrics["location_cache_hits_total"].labels(
                        cache_type=cache_type,
                        service_name=service_name
                    ).inc()
                else:
                    self.metrics["location_cache_misses_total"].labels(
                        cache_type=cache_type,
                        service_name=service_name
                    ).inc()
                
                # Calculate and update hit rate
                hits = self.metrics["location_cache_hits_total"].labels(
                    cache_type=cache_type,
                    service_name=service_name
                )._value._value
                
                misses = self.metrics["location_cache_misses_total"].labels(
                    cache_type=cache_type,
                    service_name=service_name
                )._value._value
                
                total = hits + misses
                hit_rate = hits / total if total > 0 else 0
                
                self.metrics["location_cache_hit_rate"].labels(
                    cache_type=cache_type,
                    service_name=service_name
                ).set(hit_rate)
                
        except Exception as e:
            logger.error(f"Error recording cache metrics: {e}")
    
    def record_user_action(
        self,
        action_type: str,
        result: str,
        satisfaction: Optional[float] = None,
        session_duration_seconds: Optional[float] = None,
        user_type: str = "regular"
    ):
        """Record user action metrics."""
        try:
            with self.lock:
                self.metrics["location_user_actions_total"].labels(
                    action_type=action_type,
                    result=result
                ).inc()
                
                if satisfaction is not None:
                    self.metrics["location_user_satisfaction"].labels(
                        action_type=action_type
                    ).observe(satisfaction)
                
                if session_duration_seconds is not None:
                    self.metrics["location_user_session_duration_seconds"].labels(
                        user_type=user_type
                    ).observe(session_duration_seconds)
                
        except Exception as e:
            logger.error(f"Error recording user action metrics: {e}")
    
    def record_business_metric(
        self,
        metric_name: str,
        value: float,
        period: str = "monthly"
    ):
        """Record business metrics."""
        try:
            with self.lock:
                if metric_name == "revenue_impact":
                    self.metrics["location_business_revenue_impact"].labels(
                        period=period
                    ).set(value)
                elif metric_name == "cost_savings":
                    self.metrics["location_business_cost_savings"].labels(
                        period=period
                    ).set(value)
                elif metric_name == "user_growth":
                    self.metrics["location_business_user_growth"].labels(
                        period=period
                    ).set(value)
                
        except Exception as e:
            logger.error(f"Error recording business metric: {e}")
    
    def record_system_resource(
        self,
        service_name: str,
        cpu_percent: float,
        memory_percent: float,
        disk_percent: Optional[float] = None
    ):
        """Record system resource metrics."""
        try:
            with self.lock:
                self.metrics["location_system_cpu_usage_percent"].labels(
                    service_name=service_name
                ).set(cpu_percent)
                
                self.metrics["location_system_memory_usage_percent"].labels(
                    service_name=service_name
                ).set(memory_percent)
                
                if disk_percent is not None:
                    self.metrics["location_system_disk_usage_percent"].labels(
                        service_name=service_name
                    ).set(disk_percent)
                
        except Exception as e:
            logger.error(f"Error recording system resource metrics: {e}")
    
    def record_error(
        self,
        error_type: str,
        service_name: str,
        severity: str = "warning"
    ):
        """Record error metrics."""
        try:
            with self.lock:
                self.metrics["location_errors_total"].labels(
                    error_type=error_type,
                    service_name=service_name,
                    severity=severity
                ).inc()
                
        except Exception as e:
            logger.error(f"Error recording error metrics: {e}")
    
    def record_alert(
        self,
        alert_level: str,
        category: str,
        active: bool
    ):
        """Record alert metrics."""
        try:
            with self.lock:
                if active:
                    self.metrics["location_alerts_active"].labels(
                        alert_level=alert_level,
                        category=category
                    ).inc()
                else:
                    self.metrics["location_alerts_active"].labels(
                        alert_level=alert_level,
                        category=category
                    ).dec()
                
        except Exception as e:
            logger.error(f"Error recording alert metrics: {e}")
    
    def record_geocoding_request(
        self,
        provider: str,
        result: str,
        response_time_seconds: float
    ):
        """Record geocoding metrics."""
        try:
            with self.lock:
                self.metrics["geocoding_requests_total"].labels(
                    provider=provider,
                    result=result
                ).inc()
                
                self.metrics["geocoding_response_time_seconds"].labels(
                    provider=provider
                ).observe(response_time_seconds)
                
        except Exception as e:
            logger.error(f"Error recording geocoding metrics: {e}")
    
    def record_gps_metrics(
        self,
        accuracy_meters: float,
        fix_time_seconds: float,
        device_type: str = "mobile",
        environment: str = "outdoor"
    ):
        """Record GPS metrics."""
        try:
            with self.lock:
                self.metrics["gps_accuracy_meters"].labels(
                    device_type=device_type,
                    environment=environment
                ).observe(accuracy_meters)
                
                self.metrics["gps_fix_time_seconds"].labels(
                    device_type=device_type,
                    environment=environment
                ).observe(fix_time_seconds)
                
        except Exception as e:
            logger.error(f"Error recording GPS metrics: {e}")
    
    def get_metrics(self) -> str:
        """Get metrics in Prometheus format."""
        try:
            return generate_latest(self.registry)
        except Exception as e:
            logger.error(f"Error generating metrics: {e}")
            return ""
    
    def get_metrics_content_type(self) -> str:
        """Get content type for metrics endpoint."""
        return CONTENT_TYPE_LATEST
    
    @asynccontextmanager
    async def request_timer(self, service_name: str, endpoint: str, method: str):
        """Context manager for timing requests."""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.record_service_request(service_name, endpoint, method, 200, duration)
    
    def request_timer_decorator(self, service_name: str, endpoint: str, method: str = "GET"):
        """Decorator for timing requests."""
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    self.record_service_request(service_name, endpoint, method, 200, time.time() - start_time)
                    return result
                except Exception as e:
                    self.record_service_request(service_name, endpoint, method, 500, time.time() - start_time)
                    self.record_error(str(type(e).__name__), service_name, "error")
                    raise
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    self.record_service_request(service_name, endpoint, method, 200, time.time() - start_time)
                    return result
                except Exception as e:
                    self.record_service_request(service_name, endpoint, method, 500, time.time() - start_time)
                    self.record_error(str(type(e).__name__), service_name, "error")
                    raise
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
    
    def get_metric_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics."""
        try:
            summary = {}
            
            for metric_name, metric in self.metrics.items():
                if hasattr(metric, '_metrics'):
                    # Counter, Histogram, Gauge, Summary
                    summary[metric_name] = {
                        "type": metric._type,
                        "description": metric._documentation,
                        "labels": list(metric._labelnames) if hasattr(metric, '_labelnames') else [],
                        "samples": len(metric._metrics) if hasattr(metric, '_metrics') else 0
                    }
                else:
                    # Info
                    summary[metric_name] = {
                        "type": "info",
                        "description": metric._documentation,
                        "labels": list(metric._labelnames) if hasattr(metric, '_labelnames') else []
                    }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting metric summary: {e}")
            return {}
    
    def reset_metrics(self):
        """Reset all metrics (useful for testing)."""
        try:
            with self.lock:
                for metric in self.metrics.values():
                    if hasattr(metric, 'clear'):
                        metric.clear()
                    elif hasattr(metric, '_metrics'):
                        metric._metrics.clear()
            
            logger.info("Reset all Prometheus metrics")
            
        except Exception as e:
            logger.error(f"Error resetting metrics: {e}")
    
    def get_registry(self) -> CollectorRegistry:
        """Get the Prometheus registry."""
        return self.registry
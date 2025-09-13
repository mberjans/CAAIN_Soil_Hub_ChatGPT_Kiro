"""
Prometheus Metrics Configuration for AFAS
Defines agricultural-specific metrics for monitoring system performance and business impact.
"""

from prometheus_client import Counter, Histogram, Gauge, Summary, Info
from typing import Dict, Any, Optional
import time
from functools import wraps
from datetime import datetime


# System Performance Metrics
http_requests_total = Counter(
    'afas_http_requests_total',
    'Total HTTP requests processed',
    ['service', 'method', 'endpoint', 'status_code']
)

http_request_duration_seconds = Histogram(
    'afas_http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['service', 'method', 'endpoint'],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# Agricultural-Specific Metrics
questions_asked_total = Counter(
    'afas_questions_asked_total',
    'Total agricultural questions asked',
    ['question_type', 'region', 'user_type']
)

recommendations_generated_total = Counter(
    'afas_recommendations_generated_total',
    'Total recommendations generated',
    ['question_type', 'confidence_level', 'region']
)

recommendations_accepted_total = Counter(
    'afas_recommendations_accepted_total',
    'Total recommendations accepted by farmers',
    ['question_type', 'confidence_level', 'region']
)

recommendation_confidence_score = Histogram(
    'afas_recommendation_confidence_score',
    'Distribution of recommendation confidence scores',
    ['question_type', 'region'],
    buckets=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)

recommendation_processing_time = Histogram(
    'afas_recommendation_processing_time_seconds',
    'Time taken to generate recommendations',
    ['question_type', 'complexity'],
    buckets=[0.5, 1.0, 2.0, 3.0, 5.0, 10.0, 30.0]
)

# Question Classification Metrics
question_classification_total = Counter(
    'afas_question_classification_total',
    'Total question classifications attempted',
    ['service']
)

question_classification_correct_total = Counter(
    'afas_question_classification_correct_total',
    'Total correct question classifications',
    ['service', 'question_type']
)

question_classification_confidence = Histogram(
    'afas_question_classification_confidence',
    'Question classification confidence scores',
    ['question_type'],
    buckets=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)

# Data Quality Metrics
external_api_requests_total = Counter(
    'afas_external_api_requests_total',
    'Total external API requests',
    ['api_name', 'endpoint']
)

external_api_errors_total = Counter(
    'afas_external_api_errors_total',
    'Total external API errors',
    ['api_name', 'error_type']
)

external_api_success_total = Counter(
    'afas_external_api_success_total',
    'Total successful external API calls',
    ['api_name', 'endpoint']
)

external_data_age_hours = Gauge(
    'afas_external_data_age_hours',
    'Age of external data in hours',
    ['source', 'data_type']
)

weather_data_latency_minutes = Gauge(
    'afas_weather_data_latency_minutes',
    'Weather data latency in minutes',
    ['weather_source', 'location_type']
)

# Database Performance Metrics
database_query_duration_seconds = Histogram(
    'afas_database_query_duration_seconds',
    'Database query duration in seconds',
    ['database', 'operation', 'table'],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
)

database_connections_active = Gauge(
    'afas_database_connections_active',
    'Active database connections',
    ['database', 'service']
)

database_connection_errors_total = Counter(
    'afas_database_connection_errors_total',
    'Total database connection errors',
    ['database', 'error_type']
)

# User Engagement Metrics
user_sessions_total = Counter(
    'afas_user_sessions_total',
    'Total user sessions',
    ['user_type', 'region']
)

user_session_duration_seconds = Histogram(
    'afas_user_session_duration_seconds',
    'User session duration in seconds',
    ['user_type'],
    buckets=[60, 300, 600, 1800, 3600, 7200]  # 1min to 2hours
)

returning_users_total = Counter(
    'afas_returning_users_total',
    'Total returning users',
    ['time_period']  # daily, weekly, monthly
)

total_users_total = Counter(
    'afas_total_users_total',
    'Total users (new + returning)',
    ['time_period']
)

# Agricultural Business Metrics
crop_recommendation_accuracy = Gauge(
    'afas_crop_recommendation_accuracy',
    'Crop recommendation accuracy score',
    ['region', 'crop_type', 'validation_method']
)

fertilizer_rate_recommended = Histogram(
    'afas_fertilizer_rate_recommended',
    'Fertilizer rates recommended (lbs/acre)',
    ['nutrient_type', 'crop_type', 'region'],
    buckets=[0, 25, 50, 75, 100, 150, 200, 300]
)

fertilizer_reduction_percent = Histogram(
    'afas_fertilizer_reduction_percent',
    'Percentage reduction in fertilizer use',
    ['nutrient_type', 'region'],
    buckets=[0, 5, 10, 15, 20, 25, 30, 40, 50]
)

estimated_cost_savings_dollars = Counter(
    'afas_estimated_cost_savings_dollars',
    'Estimated cost savings for farmers in dollars',
    ['region', 'farm_size_category']
)

environmental_impact_score = Gauge(
    'afas_environmental_impact_score',
    'Environmental impact score (0-100, higher is better)',
    ['region', 'practice_type']
)

# Expert Validation Metrics
expert_validation_total = Counter(
    'afas_expert_validation_total',
    'Total expert validations performed',
    ['validation_type', 'expert_type']
)

expert_validation_passed_total = Counter(
    'afas_expert_validation_passed_total',
    'Total expert validations that passed',
    ['validation_type', 'expert_type']
)

# Soil Test Metrics
soil_tests_complete_total = Counter(
    'afas_soil_tests_complete_total',
    'Total complete soil tests processed',
    ['completeness_level', 'region']  # complete, partial, minimal
)

soil_test_age_days = Histogram(
    'afas_soil_test_age_days',
    'Age of soil tests in days',
    ['region'],
    buckets=[30, 90, 180, 365, 730, 1095]  # 1 month to 3 years
)

# Error and Alert Metrics
errors_total = Counter(
    'afas_errors_total',
    'Total errors by severity',
    ['service', 'severity', 'error_type']
)

alerts_fired_total = Counter(
    'afas_alerts_fired_total',
    'Total alerts fired',
    ['alert_name', 'severity']
)

# System Resource Metrics
memory_usage_bytes = Gauge(
    'afas_memory_usage_bytes',
    'Memory usage in bytes',
    ['service']
)

cpu_usage_percent = Gauge(
    'afas_cpu_usage_percent',
    'CPU usage percentage',
    ['service']
)

# Service Information
service_info = Info(
    'afas_service_info',
    'Service information',
    ['service', 'version', 'environment']
)


class MetricsCollector:
    """Utility class for collecting and managing AFAS metrics."""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
    
    def record_http_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics."""
        http_requests_total.labels(
            service=self.service_name,
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()
        
        http_request_duration_seconds.labels(
            service=self.service_name,
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    def record_question_asked(self, question_type: str, region: str = "unknown", user_type: str = "farmer"):
        """Record when a question is asked."""
        questions_asked_total.labels(
            question_type=question_type,
            region=region,
            user_type=user_type
        ).inc()
    
    def record_recommendation_generated(
        self,
        question_type: str,
        confidence_score: float,
        processing_time: float,
        region: str = "unknown"
    ):
        """Record recommendation generation metrics."""
        confidence_level = self._get_confidence_level(confidence_score)
        
        recommendations_generated_total.labels(
            question_type=question_type,
            confidence_level=confidence_level,
            region=region
        ).inc()
        
        recommendation_confidence_score.labels(
            question_type=question_type,
            region=region
        ).observe(confidence_score)
        
        complexity = "simple" if processing_time < 1.0 else "complex"
        recommendation_processing_time.labels(
            question_type=question_type,
            complexity=complexity
        ).observe(processing_time)
    
    def record_recommendation_accepted(
        self,
        question_type: str,
        confidence_score: float,
        region: str = "unknown"
    ):
        """Record when a recommendation is accepted."""
        confidence_level = self._get_confidence_level(confidence_score)
        
        recommendations_accepted_total.labels(
            question_type=question_type,
            confidence_level=confidence_level,
            region=region
        ).inc()
    
    def record_external_api_call(
        self,
        api_name: str,
        endpoint: str,
        success: bool,
        error_type: Optional[str] = None
    ):
        """Record external API call metrics."""
        external_api_requests_total.labels(
            api_name=api_name,
            endpoint=endpoint
        ).inc()
        
        if success:
            external_api_success_total.labels(
                api_name=api_name,
                endpoint=endpoint
            ).inc()
        else:
            external_api_errors_total.labels(
                api_name=api_name,
                error_type=error_type or "unknown"
            ).inc()
    
    def record_database_query(self, database: str, operation: str, table: str, duration: float):
        """Record database query metrics."""
        database_query_duration_seconds.labels(
            database=database,
            operation=operation,
            table=table
        ).observe(duration)
    
    def update_data_freshness(self, source: str, data_type: str, age_hours: float):
        """Update data freshness metrics."""
        external_data_age_hours.labels(
            source=source,
            data_type=data_type
        ).set(age_hours)
    
    def record_user_session(self, user_type: str, duration_seconds: float, region: str = "unknown"):
        """Record user session metrics."""
        user_sessions_total.labels(
            user_type=user_type,
            region=region
        ).inc()
        
        user_session_duration_seconds.labels(
            user_type=user_type
        ).observe(duration_seconds)
    
    def record_error(self, severity: str, error_type: str):
        """Record error metrics."""
        errors_total.labels(
            service=self.service_name,
            severity=severity,
            error_type=error_type
        ).inc()
    
    def record_agricultural_metric(
        self,
        metric_type: str,
        value: float,
        labels: Dict[str, str]
    ):
        """Record agricultural-specific metrics."""
        if metric_type == "crop_accuracy":
            crop_recommendation_accuracy.labels(**labels).set(value)
        elif metric_type == "fertilizer_rate":
            fertilizer_rate_recommended.labels(**labels).observe(value)
        elif metric_type == "cost_savings":
            estimated_cost_savings_dollars.labels(**labels).inc(value)
        elif metric_type == "environmental_score":
            environmental_impact_score.labels(**labels).set(value)
    
    @staticmethod
    def _get_confidence_level(confidence_score: float) -> str:
        """Convert confidence score to categorical level."""
        if confidence_score < 0.7:
            return 'low'
        elif confidence_score < 0.85:
            return 'medium'
        else:
            return 'high'


# Decorators for automatic metrics collection
def track_agricultural_function(question_type: str = None, region: str = "unknown"):
    """Decorator to automatically track agricultural function performance."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                processing_time = time.time() - start_time
                
                # Extract confidence score if present
                confidence_score = 0.0
                if isinstance(result, dict) and 'confidence_score' in result:
                    confidence_score = result['confidence_score']
                
                # Record metrics
                collector = MetricsCollector("agricultural_function")
                collector.record_recommendation_generated(
                    question_type=question_type or func.__name__,
                    confidence_score=confidence_score,
                    processing_time=processing_time,
                    region=region
                )
                
                return result
                
            except Exception as e:
                collector = MetricsCollector("agricultural_function")
                collector.record_error("error", type(e).__name__)
                raise
        
        return wrapper
    return decorator


def track_http_requests(service_name: str):
    """Decorator to automatically track HTTP request metrics."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Extract request info (this would need to be adapted based on framework)
                method = getattr(args[0], 'method', 'GET') if args else 'GET'
                endpoint = func.__name__
                status_code = 200
                
                collector = MetricsCollector(service_name)
                collector.record_http_request(method, endpoint, status_code, duration)
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                collector = MetricsCollector(service_name)
                collector.record_http_request('GET', func.__name__, 500, duration)
                raise
        
        return wrapper
    return decorator


# Context manager for tracking operations
class MetricsContext:
    """Context manager for tracking operation metrics."""
    
    def __init__(self, operation_name: str, service_name: str, **labels):
        self.operation_name = operation_name
        self.service_name = service_name
        self.labels = labels
        self.start_time = None
        self.collector = MetricsCollector(service_name)
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        if exc_type:
            self.collector.record_error("error", exc_type.__name__)
        
        # Record operation duration (could be extended based on operation type)
        if hasattr(self.collector, f'record_{self.operation_name}'):
            getattr(self.collector, f'record_{self.operation_name}')(duration, **self.labels)
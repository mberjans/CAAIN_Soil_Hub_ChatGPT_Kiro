"""
Enhanced Logging Configuration for AFAS
Provides structured logging with agricultural-specific context and metrics integration.
"""

import structlog
import logging
import logging.handlers
import sys
import os
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path
import json


class AgriculturalLogProcessor:
    """Custom processor for agricultural-specific log enrichment."""
    
    def __call__(self, logger, method_name, event_dict):
        """Add agricultural context to log entries."""
        # Add timestamp in ISO format
        event_dict['timestamp'] = datetime.utcnow().isoformat()
        
        # Add agricultural context if present
        if 'agricultural_context' in event_dict:
            event_dict['is_agricultural'] = True
            
        # Add confidence score context
        if 'confidence_score' in event_dict:
            confidence = event_dict['confidence_score']
            if confidence < 0.7:
                event_dict['confidence_level'] = 'low'
            elif confidence < 0.85:
                event_dict['confidence_level'] = 'medium'
            else:
                event_dict['confidence_level'] = 'high'
        
        return event_dict


def setup_logging(
    service_name: str,
    log_level: str = "INFO",
    log_dir: str = "logs",
    enable_file_logging: bool = True,
    enable_metrics: bool = True
) -> None:
    """
    Set up comprehensive logging for AFAS services.
    
    Args:
        service_name: Name of the service for log identification
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_dir: Directory for log files
        enable_file_logging: Whether to enable file-based logging
        enable_metrics: Whether to enable metrics logging
    """
    # Create log directory
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper())
    )
    
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        AgriculturalLogProcessor(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    # Add JSON renderer for structured logging
    if enable_file_logging:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Set up file logging with rotation
    if enable_file_logging:
        setup_file_logging(service_name, log_path, log_level)
    
    # Set up metrics logging
    if enable_metrics:
        setup_metrics_logging(service_name, log_path)


def setup_file_logging(service_name: str, log_path: Path, log_level: str) -> None:
    """Set up rotating file handlers for different log types."""
    
    # Main application log
    app_handler = logging.handlers.RotatingFileHandler(
        log_path / f"{service_name}.log",
        maxBytes=50 * 1024 * 1024,  # 50MB
        backupCount=10
    )
    app_handler.setLevel(getattr(logging, log_level.upper()))
    
    # Error log
    error_handler = logging.handlers.RotatingFileHandler(
        log_path / f"{service_name}_errors.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    
    # Agricultural decisions log
    agricultural_handler = logging.handlers.RotatingFileHandler(
        log_path / f"{service_name}_agricultural.log",
        maxBytes=100 * 1024 * 1024,  # 100MB
        backupCount=20
    )
    agricultural_handler.setLevel(logging.INFO)
    
    # Add handlers to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(app_handler)
    root_logger.addHandler(error_handler)
    
    # Set up agricultural logger
    agricultural_logger = logging.getLogger("agricultural_decisions")
    agricultural_logger.addHandler(agricultural_handler)
    agricultural_logger.setLevel(logging.INFO)


def setup_metrics_logging(service_name: str, log_path: Path) -> None:
    """Set up metrics logging for Prometheus integration."""
    
    metrics_handler = logging.handlers.RotatingFileHandler(
        log_path / f"{service_name}_metrics.log",
        maxBytes=20 * 1024 * 1024,  # 20MB
        backupCount=5
    )
    metrics_handler.setLevel(logging.INFO)
    
    # Create metrics logger
    metrics_logger = logging.getLogger("metrics")
    metrics_logger.addHandler(metrics_handler)
    metrics_logger.setLevel(logging.INFO)


# Agricultural-specific logging functions
def log_agricultural_decision(
    decision_type: str,
    input_data: Dict[str, Any],
    output_data: Dict[str, Any],
    confidence_score: float,
    processing_time: float,
    agricultural_sources: Optional[list] = None,
    expert_validated: bool = False
) -> None:
    """
    Log agricultural decisions for audit, improvement, and compliance.
    
    Args:
        decision_type: Type of agricultural decision (crop_selection, fertilizer_rate, etc.)
        input_data: Input parameters used for decision
        output_data: Generated recommendations/decisions
        confidence_score: Confidence level of the decision (0.0-1.0)
        processing_time: Time taken to process in seconds
        agricultural_sources: List of agricultural sources/references used
        expert_validated: Whether the decision was validated by an expert
    """
    logger = structlog.get_logger("agricultural_decisions")
    
    # Sanitize input data for privacy
    sanitized_input = sanitize_farm_data(input_data)
    
    logger.info(
        "agricultural_decision_made",
        decision_type=decision_type,
        input_summary=sanitized_input,
        output_summary={
            'primary_recommendation': output_data.get('primary_recommendation'),
            'confidence_score': confidence_score,
            'alternatives_count': len(output_data.get('alternatives', [])),
            'economic_impact': output_data.get('economic_impact'),
            'environmental_impact': output_data.get('environmental_impact')
        },
        confidence_score=confidence_score,
        confidence_level=get_confidence_level(confidence_score),
        processing_time_seconds=processing_time,
        agricultural_sources=agricultural_sources or [],
        expert_validated=expert_validated,
        agricultural_context=True,
        timestamp=datetime.utcnow().isoformat()
    )


def log_performance_metric(
    metric_name: str,
    metric_value: float,
    metric_type: str = "gauge",
    labels: Optional[Dict[str, str]] = None,
    service_name: Optional[str] = None
) -> None:
    """
    Log performance metrics for Prometheus collection.
    
    Args:
        metric_name: Name of the metric
        metric_value: Value of the metric
        metric_type: Type of metric (counter, gauge, histogram)
        labels: Additional labels for the metric
        service_name: Service generating the metric
    """
    logger = structlog.get_logger("metrics")
    
    logger.info(
        "performance_metric",
        metric_name=metric_name,
        metric_value=metric_value,
        metric_type=metric_type,
        labels=labels or {},
        service_name=service_name,
        timestamp=datetime.utcnow().isoformat()
    )


def log_user_interaction(
    user_id: str,
    interaction_type: str,
    question_type: Optional[str] = None,
    session_duration: Optional[float] = None,
    recommendation_accepted: Optional[bool] = None,
    feedback_score: Optional[int] = None
) -> None:
    """
    Log user interactions for engagement analysis.
    
    Args:
        user_id: Anonymized user identifier
        interaction_type: Type of interaction (question_asked, recommendation_viewed, etc.)
        question_type: Type of agricultural question
        session_duration: Duration of user session in seconds
        recommendation_accepted: Whether user accepted the recommendation
        feedback_score: User feedback score (1-5)
    """
    logger = structlog.get_logger("user_interactions")
    
    logger.info(
        "user_interaction",
        user_id=hash_user_id(user_id),  # Hash for privacy
        interaction_type=interaction_type,
        question_type=question_type,
        session_duration_seconds=session_duration,
        recommendation_accepted=recommendation_accepted,
        feedback_score=feedback_score,
        timestamp=datetime.utcnow().isoformat()
    )


def log_data_quality_issue(
    data_source: str,
    issue_type: str,
    issue_description: str,
    severity: str = "warning",
    affected_recommendations: Optional[int] = None
) -> None:
    """
    Log data quality issues for monitoring and improvement.
    
    Args:
        data_source: Source of the data issue (weather_api, soil_db, etc.)
        issue_type: Type of issue (stale_data, api_error, validation_failure)
        issue_description: Detailed description of the issue
        severity: Severity level (info, warning, error, critical)
        affected_recommendations: Number of recommendations potentially affected
    """
    logger = structlog.get_logger("data_quality")
    
    log_method = getattr(logger, severity.lower(), logger.warning)
    
    log_method(
        "data_quality_issue",
        data_source=data_source,
        issue_type=issue_type,
        issue_description=issue_description,
        severity=severity,
        affected_recommendations=affected_recommendations,
        timestamp=datetime.utcnow().isoformat()
    )


def log_external_api_call(
    api_name: str,
    endpoint: str,
    response_time: float,
    status_code: int,
    success: bool,
    error_message: Optional[str] = None
) -> None:
    """
    Log external API calls for monitoring and reliability tracking.
    
    Args:
        api_name: Name of the external API
        endpoint: API endpoint called
        response_time: Response time in seconds
        status_code: HTTP status code
        success: Whether the call was successful
        error_message: Error message if call failed
    """
    logger = structlog.get_logger("external_apis")
    
    logger.info(
        "external_api_call",
        api_name=api_name,
        endpoint=endpoint,
        response_time_seconds=response_time,
        status_code=status_code,
        success=success,
        error_message=error_message,
        timestamp=datetime.utcnow().isoformat()
    )


# Utility functions
def sanitize_farm_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove or hash sensitive farm data for logging."""
    sanitized = {}
    
    for key, value in data.items():
        if key in ['farmer_name', 'email', 'phone', 'address']:
            continue  # Skip personal information
        elif key in ['latitude', 'longitude']:
            # Round coordinates to protect exact location
            if isinstance(value, (int, float)):
                sanitized[key] = round(float(value), 2)
        elif key == 'farm_id':
            sanitized[key] = hash(str(value)) % 10000  # Hash farm ID
        else:
            sanitized[key] = value
    
    return sanitized


def hash_user_id(user_id: str) -> str:
    """Create a consistent hash of user ID for privacy."""
    return str(hash(user_id) % 100000)


def get_confidence_level(confidence_score: float) -> str:
    """Convert confidence score to categorical level."""
    if confidence_score < 0.7:
        return 'low'
    elif confidence_score < 0.85:
        return 'medium'
    else:
        return 'high'


# Context managers for structured logging
class LoggingContext:
    """Context manager for adding consistent context to logs."""
    
    def __init__(self, **context):
        self.context = context
        self.logger = None
    
    def __enter__(self):
        self.logger = structlog.get_logger().bind(**self.context)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.logger.error(
                "exception_in_context",
                exception_type=exc_type.__name__,
                exception_message=str(exc_val)
            )


# Decorators for automatic logging
def log_agricultural_function(func):
    """Decorator to automatically log agricultural function calls."""
    def wrapper(*args, **kwargs):
        start_time = datetime.utcnow()
        
        try:
            result = func(*args, **kwargs)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Extract confidence score if present in result
            confidence_score = None
            if isinstance(result, dict) and 'confidence_score' in result:
                confidence_score = result['confidence_score']
            
            log_agricultural_decision(
                decision_type=func.__name__,
                input_data={'args_count': len(args), 'kwargs_keys': list(kwargs.keys())},
                output_data={'result_type': type(result).__name__},
                confidence_score=confidence_score or 0.0,
                processing_time=processing_time
            )
            
            return result
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            logger = structlog.get_logger("agricultural_decisions")
            logger.error(
                "agricultural_function_error",
                function_name=func.__name__,
                error_type=type(e).__name__,
                error_message=str(e),
                processing_time_seconds=processing_time
            )
            raise
    
    return wrapper
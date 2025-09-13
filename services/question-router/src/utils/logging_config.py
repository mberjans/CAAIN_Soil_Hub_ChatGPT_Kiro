"""
Logging Configuration for Question Router

Structured logging setup for agricultural decision tracking.
"""

import structlog
import logging
import sys
from typing import Any, Dict


def setup_logging(service_name: str = "question-router", log_level: str = "INFO") -> None:
    """
    Set up structured logging for the question router service.
    
    Args:
        service_name: Name of the service for log identification
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper())
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def log_question_classification(
    question_text: str,
    classification_result: Dict[str, Any],
    processing_time: float
) -> None:
    """
    Log question classification for audit and improvement.
    
    Args:
        question_text: Original question text (truncated for privacy)
        classification_result: Classification result details
        processing_time: Time taken to process in seconds
    """
    logger = structlog.get_logger("question_classification")
    
    # Truncate question text for privacy
    truncated_question = question_text[:100] + "..." if len(question_text) > 100 else question_text
    
    logger.info(
        "question_classified",
        question_preview=truncated_question,
        question_type=classification_result.get("question_type"),
        confidence_score=classification_result.get("confidence_score"),
        processing_time_seconds=processing_time,
        has_alternatives=len(classification_result.get("alternative_types", [])) > 0
    )


def log_routing_decision(
    question_type: str,
    routing_decision: Dict[str, Any],
    request_id: str
) -> None:
    """
    Log routing decisions for monitoring and optimization.
    
    Args:
        question_type: Classified question type
        routing_decision: Routing decision details
        request_id: Unique request identifier
    """
    logger = structlog.get_logger("question_routing")
    
    logger.info(
        "question_routed",
        request_id=request_id,
        question_type=question_type,
        primary_service=routing_decision.get("primary_service"),
        secondary_services=routing_decision.get("secondary_services"),
        processing_priority=routing_decision.get("processing_priority"),
        estimated_time=routing_decision.get("estimated_processing_time")
    )
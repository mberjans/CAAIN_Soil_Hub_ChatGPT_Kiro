"""
Monitoring Integration Service for Crop Variety Recommendations

This service provides seamless integration between the comprehensive monitoring system
and the existing crop variety recommendation services, ensuring all operations are
properly tracked and monitored.

Author: AI Coding Agent
Date: 2024
"""

import asyncio
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from functools import wraps
import inspect

from .comprehensive_monitoring_alerting_service import (
    ComprehensiveMonitoringAlertingService,
    RecommendationMetrics,
    get_monitoring_service
)

logger = logging.getLogger(__name__)


class MonitoringIntegrationService:
    """
    Service for integrating monitoring with crop variety recommendation operations.
    
    Features:
    - Automatic metrics collection for all recommendation operations
    - Performance tracking and optimization insights
    - Error monitoring and alerting
    - User engagement tracking
    - Agricultural outcome monitoring
    """
    
    def __init__(self):
        """Initialize the monitoring integration service."""
        self.monitoring_service = None
        self.integration_active = False
        
        # Performance tracking
        self.operation_times: Dict[str, List[float]] = {}
        self.error_counts: Dict[str, int] = {}
        
        logger.info("Monitoring integration service initialized")
    
    async def initialize(self):
        """Initialize the monitoring service connection."""
        try:
            self.monitoring_service = await get_monitoring_service()
            self.integration_active = True
            
            # Start monitoring if not already started
            if not self.monitoring_service.monitoring_active:
                await self.monitoring_service.start_monitoring()
            
            logger.info("Monitoring integration service connected")
            
        except Exception as e:
            logger.error(f"Failed to initialize monitoring integration: {e}")
            self.integration_active = False
    
    def monitor_recommendation_operation(self, 
                                       operation_name: str,
                                       crop_type: str = "unknown",
                                       region: str = "unknown"):
        """
        Decorator for monitoring crop variety recommendation operations.
        
        Args:
            operation_name: Name of the operation being monitored
            crop_type: Type of crop for the recommendation
            region: Geographic region for the recommendation
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                if not self.integration_active:
                    return await func(*args, **kwargs)
                
                request_id = str(uuid.uuid4())
                start_time = time.time()
                
                try:
                    # Execute the original function
                    result = await func(*args, **kwargs)
                    
                    # Calculate execution time
                    execution_time_ms = (time.time() - start_time) * 1000
                    
                    # Extract metrics from result
                    confidence_score = self._extract_confidence_score(result)
                    number_of_recommendations = self._extract_recommendation_count(result)
                    
                    # Record metrics
                    await self._record_operation_metrics(
                        request_id=request_id,
                        operation_name=operation_name,
                        crop_type=crop_type,
                        region=region,
                        execution_time_ms=execution_time_ms,
                        confidence_score=confidence_score,
                        number_of_recommendations=number_of_recommendations,
                        success=True
                    )
                    
                    return result
                    
                except Exception as e:
                    # Calculate execution time for failed operations
                    execution_time_ms = (time.time() - start_time) * 1000
                    
                    # Record error metrics
                    await self._record_operation_metrics(
                        request_id=request_id,
                        operation_name=operation_name,
                        crop_type=crop_type,
                        region=region,
                        execution_time_ms=execution_time_ms,
                        confidence_score=0.0,
                        number_of_recommendations=0,
                        success=False,
                        error=str(e)
                    )
                    
                    # Re-raise the exception
                    raise
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                if not self.integration_active:
                    return func(*args, **kwargs)
                
                request_id = str(uuid.uuid4())
                start_time = time.time()
                
                try:
                    # Execute the original function
                    result = func(*args, **kwargs)
                    
                    # Calculate execution time
                    execution_time_ms = (time.time() - start_time) * 1000
                    
                    # Extract metrics from result
                    confidence_score = self._extract_confidence_score(result)
                    number_of_recommendations = self._extract_recommendation_count(result)
                    
                    # Record metrics (async call in sync context)
                    asyncio.create_task(self._record_operation_metrics(
                        request_id=request_id,
                        operation_name=operation_name,
                        crop_type=crop_type,
                        region=region,
                        execution_time_ms=execution_time_ms,
                        confidence_score=confidence_score,
                        number_of_recommendations=number_of_recommendations,
                        success=True
                    ))
                    
                    return result
                    
                except Exception as e:
                    # Calculate execution time for failed operations
                    execution_time_ms = (time.time() - start_time) * 1000
                    
                    # Record error metrics (async call in sync context)
                    asyncio.create_task(self._record_operation_metrics(
                        request_id=request_id,
                        operation_name=operation_name,
                        crop_type=crop_type,
                        region=region,
                        execution_time_ms=execution_time_ms,
                        confidence_score=0.0,
                        number_of_recommendations=0,
                        success=False,
                        error=str(e)
                    ))
                    
                    # Re-raise the exception
                    raise
            
            # Return appropriate wrapper based on function type
            if inspect.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator
    
    def _extract_confidence_score(self, result: Any) -> float:
        """Extract confidence score from operation result."""
        try:
            if isinstance(result, dict):
                # Try common confidence score fields
                for field in ['confidence_score', 'confidence', 'score', 'quality_score']:
                    if field in result and isinstance(result[field], (int, float)):
                        return float(result[field])
                
                # Try nested confidence scores
                if 'recommendations' in result and isinstance(result['recommendations'], list):
                    if result['recommendations']:
                        first_rec = result['recommendations'][0]
                        if isinstance(first_rec, dict):
                            for field in ['confidence_score', 'confidence', 'score']:
                                if field in first_rec and isinstance(first_rec[field], (int, float)):
                                    return float(first_rec[field])
            
            elif hasattr(result, 'confidence_score'):
                return float(result.confidence_score)
            elif hasattr(result, 'confidence'):
                return float(result.confidence)
            
            # Default confidence score
            return 0.8
            
        except Exception as e:
            logger.debug(f"Could not extract confidence score: {e}")
            return 0.5  # Default to medium confidence
    
    def _extract_recommendation_count(self, result: Any) -> int:
        """Extract number of recommendations from operation result."""
        try:
            if isinstance(result, list):
                return len(result)
            elif isinstance(result, dict):
                # Try common recommendation count fields
                for field in ['recommendations', 'results', 'varieties', 'crops']:
                    if field in result and isinstance(result[field], list):
                        return len(result[field])
                
                # Try count fields
                for field in ['count', 'total', 'number_of_recommendations']:
                    if field in result and isinstance(result[field], int):
                        return result[field]
            
            elif hasattr(result, '__len__'):
                return len(result)
            
            # Default count
            return 1
            
        except Exception as e:
            logger.debug(f"Could not extract recommendation count: {e}")
            return 1
    
    async def _record_operation_metrics(self,
                                     request_id: str,
                                     operation_name: str,
                                     crop_type: str,
                                     region: str,
                                     execution_time_ms: float,
                                     confidence_score: float,
                                     number_of_recommendations: int,
                                     success: bool,
                                     error: Optional[str] = None):
        """Record metrics for an operation."""
        try:
            if not self.monitoring_service:
                return
            
            # Create recommendation metrics
            metrics = RecommendationMetrics(
                request_id=request_id,
                crop_type=crop_type,
                region=region,
                response_time_ms=execution_time_ms,
                confidence_score=confidence_score,
                number_of_recommendations=number_of_recommendations
            )
            
            # Record metrics
            await self.monitoring_service.record_recommendation_metrics(metrics)
            
            # Track operation times
            if operation_name not in self.operation_times:
                self.operation_times[operation_name] = []
            self.operation_times[operation_name].append(execution_time_ms)
            
            # Keep only last 100 operation times
            if len(self.operation_times[operation_name]) > 100:
                self.operation_times[operation_name] = self.operation_times[operation_name][-100:]
            
            # Track error counts
            if not success:
                if operation_name not in self.error_counts:
                    self.error_counts[operation_name] = 0
                self.error_counts[operation_name] += 1
                
                logger.warning(f"Operation {operation_name} failed: {error}")
            
            logger.debug(f"Recorded metrics for {operation_name}: {execution_time_ms:.2f}ms, confidence: {confidence_score:.2f}")
            
        except Exception as e:
            logger.error(f"Error recording operation metrics: {e}")
    
    async def record_user_feedback(self,
                                 request_id: str,
                                 crop_type: str,
                                 region: str,
                                 satisfaction_score: float,
                                 feedback_text: Optional[str] = None):
        """Record user feedback for a recommendation."""
        try:
            if not self.monitoring_service:
                return
            
            # Find the original metrics for this request
            with self.monitoring_service.lock:
                for metrics in self.monitoring_service.recommendation_metrics:
                    if metrics.request_id == request_id:
                        # Update the metrics with user satisfaction
                        metrics.user_satisfaction = satisfaction_score
                        
                        # Update in database if available
                        if self.monitoring_service.db_session:
                            from sqlalchemy import text
                            update_sql = """
                            UPDATE recommendation_metrics 
                            SET user_satisfaction = :satisfaction 
                            WHERE request_id = :request_id
                            """
                            self.monitoring_service.db_session.execute(text(update_sql), {
                                "satisfaction": satisfaction_score,
                                "request_id": request_id
                            })
                            self.monitoring_service.db_session.commit()
                        
                        logger.info(f"Recorded user feedback for {request_id}: {satisfaction_score}")
                        break
            
        except Exception as e:
            logger.error(f"Error recording user feedback: {e}")
    
    async def record_agricultural_outcome(self,
                                        request_id: str,
                                        crop_type: str,
                                        region: str,
                                        outcome: str,
                                        yield_improvement: Optional[float] = None,
                                        cost_savings: Optional[float] = None):
        """Record agricultural outcome for a recommendation."""
        try:
            if not self.monitoring_service:
                return
            
            # Find the original metrics for this request
            with self.monitoring_service.lock:
                for metrics in self.monitoring_service.recommendation_metrics:
                    if metrics.request_id == request_id:
                        # Update the metrics with agricultural outcome
                        metrics.agricultural_outcome = outcome
                        
                        # Update in database if available
                        if self.monitoring_service.db_session:
                            from sqlalchemy import text
                            update_sql = """
                            UPDATE recommendation_metrics 
                            SET agricultural_outcome = :outcome 
                            WHERE request_id = :request_id
                            """
                            self.monitoring_service.db_session.execute(text(update_sql), {
                                "outcome": outcome,
                                "request_id": request_id
                            })
                            self.monitoring_service.db_session.commit()
                        
                        logger.info(f"Recorded agricultural outcome for {request_id}: {outcome}")
                        break
            
        except Exception as e:
            logger.error(f"Error recording agricultural outcome: {e}")
    
    async def get_operation_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for all operations."""
        try:
            summary = {}
            
            for operation_name, times in self.operation_times.items():
                if times:
                    summary[operation_name] = {
                        "count": len(times),
                        "average_time_ms": sum(times) / len(times),
                        "min_time_ms": min(times),
                        "max_time_ms": max(times),
                        "p95_time_ms": sorted(times)[int(len(times) * 0.95)] if len(times) > 1 else times[0],
                        "error_count": self.error_counts.get(operation_name, 0),
                        "error_rate": self.error_counts.get(operation_name, 0) / len(times) if times else 0
                    }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting operation performance summary: {e}")
            return {"error": str(e)}
    
    async def get_monitoring_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive monitoring dashboard data."""
        try:
            if not self.monitoring_service:
                return {"error": "Monitoring service not available"}
            
            # Get metrics summary
            metrics_summary = await self.monitoring_service.get_metrics_summary()
            
            # Get operation performance summary
            performance_summary = await self.get_operation_performance_summary()
            
            # Combine data
            dashboard_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "metrics_summary": metrics_summary,
                "performance_summary": performance_summary,
                "integration_status": {
                    "active": self.integration_active,
                    "monitoring_service_available": self.monitoring_service is not None,
                    "monitoring_active": self.monitoring_service.monitoring_active if self.monitoring_service else False
                }
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error getting monitoring dashboard data: {e}")
            return {"error": str(e)}


# Global instance
monitoring_integration_service = MonitoringIntegrationService()


async def get_monitoring_integration_service() -> MonitoringIntegrationService:
    """Get the global monitoring integration service instance."""
    return monitoring_integration_service


# Convenience decorators for common operations
def monitor_variety_recommendation(crop_type: str = "unknown", region: str = "unknown"):
    """Decorator for monitoring variety recommendation operations."""
    async def decorator_wrapper():
        service = await get_monitoring_integration_service()
        return service.monitor_recommendation_operation(
            "variety_recommendation",
            crop_type=crop_type,
            region=region
        )
    return decorator_wrapper


def monitor_crop_selection(crop_type: str = "unknown", region: str = "unknown"):
    """Decorator for monitoring crop selection operations."""
    async def decorator_wrapper():
        service = await get_monitoring_integration_service()
        return service.monitor_recommendation_operation(
            "crop_selection",
            crop_type=crop_type,
            region=region
        )
    return decorator_wrapper


def monitor_personalization(crop_type: str = "unknown", region: str = "unknown"):
    """Decorator for monitoring personalization operations."""
    async def decorator_wrapper():
        service = await get_monitoring_integration_service()
        return service.monitor_recommendation_operation(
            "personalization",
            crop_type=crop_type,
            region=region
        )
    return decorator_wrapper
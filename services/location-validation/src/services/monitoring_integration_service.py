"""
Monitoring Integration Service for Location Services
TICKET-008_farm-location-input-15.2: Implement production monitoring and optimization

This service integrates the production monitoring system with existing location services
to provide seamless monitoring, analytics, and optimization capabilities.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import threading
from functools import wraps

from .production_monitoring_service import LocationProductionMonitoringService
from .production_analytics_service import LocationProductionAnalyticsService
from .prometheus_metrics_collector import LocationPrometheusMetricsCollector

logger = logging.getLogger(__name__)

@dataclass
class ServiceIntegration:
    """Service integration configuration."""
    service_name: str
    endpoints: List[str]
    monitoring_enabled: bool = True
    analytics_enabled: bool = True
    prometheus_enabled: bool = True
    custom_metrics: Dict[str, Callable] = None

class LocationMonitoringIntegrationService:
    """
    Integration service for location services monitoring.
    
    Provides seamless integration between:
    - Existing location services
    - Production monitoring system
    - Analytics and reporting
    - Prometheus metrics collection
    """
    
    def __init__(
        self,
        database_url: str = None,
        redis_url: str = "redis://localhost:6379"
    ):
        """Initialize the monitoring integration service."""
        self.database_url = database_url
        self.redis_url = redis_url
        
        # Initialize monitoring services
        self.monitoring_service = LocationProductionMonitoringService(database_url, redis_url)
        self.analytics_service = LocationProductionAnalyticsService(database_url, redis_url)
        
        # Initialize Prometheus metrics collector
        try:
            self.prometheus_collector = LocationPrometheusMetricsCollector()
            self.prometheus_enabled = True
        except ImportError:
            logger.warning("Prometheus client not available. Prometheus metrics disabled.")
            self.prometheus_collector = None
            self.prometheus_enabled = False
        
        # Service integrations
        self.integrations: Dict[str, ServiceIntegration] = {}
        
        # Background tasks
        self.integration_active = False
        self.integration_task = None
        
        # Thread safety
        self.lock = threading.Lock()
        
        logger.info("Location monitoring integration service initialized")
    
    async def start_integration(self):
        """Start monitoring integration for all services."""
        if self.integration_active:
            logger.warning("Integration is already active")
            return
        
        self.integration_active = True
        
        # Start monitoring service
        await self.monitoring_service.start_monitoring()
        
        # Start integration task
        self.integration_task = asyncio.create_task(self._integration_loop())
        
        logger.info("Monitoring integration started")
    
    async def stop_integration(self):
        """Stop monitoring integration."""
        if not self.integration_active:
            return
        
        self.integration_active = False
        
        # Stop monitoring service
        await self.monitoring_service.stop_monitoring()
        
        # Stop integration task
        if self.integration_task:
            self.integration_task.cancel()
            try:
                await self.integration_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Monitoring integration stopped")
    
    async def _integration_loop(self):
        """Background integration loop."""
        while self.integration_active:
            try:
                # Sync metrics between services
                await self._sync_metrics()
                
                # Update Prometheus metrics
                if self.prometheus_enabled:
                    await self._update_prometheus_metrics()
                
                # Generate periodic analytics
                await self._generate_periodic_analytics()
                
                # Wait before next iteration
                await asyncio.sleep(60)  # Run every minute
                
            except Exception as e:
                logger.error(f"Error in integration loop: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _sync_metrics(self):
        """Sync metrics between monitoring and analytics services."""
        try:
            # This would sync metrics between the services
            # For now, we'll just log that sync would happen
            logger.debug("Metrics sync would occur here")
            
        except Exception as e:
            logger.error(f"Error syncing metrics: {e}")
    
    async def _update_prometheus_metrics(self):
        """Update Prometheus metrics from monitoring data."""
        try:
            if not self.prometheus_enabled:
                return
            
            # Get recent metrics from monitoring service
            dashboard_data = await self.monitoring_service.get_monitoring_dashboard_data()
            
            # Update Prometheus metrics
            if "location_accuracy" in dashboard_data:
                accuracy_data = dashboard_data["location_accuracy"]
                self.prometheus_collector.record_location_accuracy(
                    accuracy_data.get("average_accuracy_meters", 0),
                    "comprehensive",
                    "medium",  # This would be calculated based on actual data
                    accuracy_data.get("average_accuracy_meters", 0) / 100.0  # Convert to confidence score
                )
            
            if "service_performance" in dashboard_data:
                perf_data = dashboard_data["service_performance"]
                self.prometheus_collector.record_service_request(
                    "location_validation",
                    "/api/v1/locations/validate",
                    "POST",
                    200,
                    perf_data.get("average_response_time_ms", 0) / 1000.0
                )
            
            if "user_experience" in dashboard_data:
                ux_data = dashboard_data["user_experience"]
                self.prometheus_collector.record_user_action(
                    "location_input",
                    "success" if ux_data.get("success_rate", 0) > 0.9 else "failure",
                    ux_data.get("average_satisfaction", 0)
                )
            
            logger.debug("Updated Prometheus metrics")
            
        except Exception as e:
            logger.error(f"Error updating Prometheus metrics: {e}")
    
    async def _generate_periodic_analytics(self):
        """Generate periodic analytics reports."""
        try:
            # Generate daily analytics if it's a new day
            current_time = datetime.utcnow()
            if current_time.hour == 0 and current_time.minute < 5:  # Within first 5 minutes of day
                end_date = current_time
                start_date = end_date - timedelta(days=1)
                
                # Generate daily reports
                await self.analytics_service.generate_accuracy_report(start_date, end_date)
                await self.analytics_service.generate_performance_report(start_date, end_date)
                await self.analytics_service.generate_user_experience_report(start_date, end_date)
                
                logger.info("Generated daily analytics reports")
            
        except Exception as e:
            logger.error(f"Error generating periodic analytics: {e}")
    
    def register_service(
        self,
        service_name: str,
        endpoints: List[str],
        monitoring_enabled: bool = True,
        analytics_enabled: bool = True,
        prometheus_enabled: bool = True,
        custom_metrics: Dict[str, Callable] = None
    ):
        """Register a service for monitoring integration."""
        try:
            integration = ServiceIntegration(
                service_name=service_name,
                endpoints=endpoints,
                monitoring_enabled=monitoring_enabled,
                analytics_enabled=analytics_enabled,
                prometheus_enabled=prometheus_enabled,
                custom_metrics=custom_metrics or {}
            )
            
            with self.lock:
                self.integrations[service_name] = integration
            
            logger.info(f"Registered service for monitoring: {service_name}")
            
        except Exception as e:
            logger.error(f"Error registering service {service_name}: {e}")
    
    def unregister_service(self, service_name: str):
        """Unregister a service from monitoring integration."""
        try:
            with self.lock:
                if service_name in self.integrations:
                    del self.integrations[service_name]
                    logger.info(f"Unregistered service from monitoring: {service_name}")
                else:
                    logger.warning(f"Service {service_name} not found in integrations")
                    
        except Exception as e:
            logger.error(f"Error unregistering service {service_name}: {e}")
    
    def create_monitoring_decorator(self, service_name: str, endpoint: str):
        """Create a monitoring decorator for service endpoints."""
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                success = True
                error_type = None
                
                try:
                    result = await func(*args, **kwargs)
                    
                    # Record success metrics
                    await self._record_endpoint_metrics(
                        service_name, endpoint, "POST", 200,
                        time.time() - start_time, success, error_type
                    )
                    
                    return result
                    
                except Exception as e:
                    success = False
                    error_type = str(type(e).__name__)
                    
                    # Record error metrics
                    await self._record_endpoint_metrics(
                        service_name, endpoint, "POST", 500,
                        time.time() - start_time, success, error_type
                    )
                    
                    raise
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                success = True
                error_type = None
                
                try:
                    result = func(*args, **kwargs)
                    
                    # Record success metrics
                    asyncio.create_task(self._record_endpoint_metrics(
                        service_name, endpoint, "POST", 200,
                        time.time() - start_time, success, error_type
                    ))
                    
                    return result
                    
                except Exception as e:
                    success = False
                    error_type = str(type(e).__name__)
                    
                    # Record error metrics
                    asyncio.create_task(self._record_endpoint_metrics(
                        service_name, endpoint, "POST", 500,
                        time.time() - start_time, success, error_type
                    ))
                    
                    raise
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
    
    async def _record_endpoint_metrics(
        self,
        service_name: str,
        endpoint: str,
        method: str,
        status_code: int,
        response_time_ms: float,
        success: bool,
        error_type: Optional[str] = None
    ):
        """Record metrics for an endpoint call."""
        try:
            # Record in monitoring service
            await self.monitoring_service.record_service_performance(
                service_name=service_name,
                endpoint=endpoint,
                response_time_ms=response_time_ms,
                status_code=status_code,
                error_type=error_type
            )
            
            # Record in Prometheus if enabled
            if self.prometheus_enabled:
                self.prometheus_collector.record_service_request(
                    service_name, endpoint, method, status_code, response_time_ms / 1000.0
                )
                
                if not success and error_type:
                    self.prometheus_collector.record_error(error_type, service_name, "error")
            
        except Exception as e:
            logger.error(f"Error recording endpoint metrics: {e}")
    
    async def record_location_accuracy_with_monitoring(
        self,
        location_id: str,
        expected_coordinates: tuple,
        actual_coordinates: tuple,
        validation_method: str,
        processing_time_ms: float,
        user_feedback: Optional[float] = None
    ):
        """Record location accuracy with full monitoring integration."""
        try:
            # Record in monitoring service
            await self.monitoring_service.record_location_accuracy(
                location_id=location_id,
                expected_coordinates=expected_coordinates,
                actual_coordinates=actual_coordinates,
                validation_method=validation_method,
                processing_time_ms=processing_time_ms,
                user_feedback=user_feedback
            )
            
            # Calculate accuracy for Prometheus
            if self.prometheus_enabled:
                accuracy_meters = self._calculate_distance(expected_coordinates, actual_coordinates)
                accuracy_level = "high" if accuracy_meters < 10 else "medium" if accuracy_meters < 100 else "low"
                confidence_score = max(0.0, 1.0 - (accuracy_meters / 1000.0))
                
                self.prometheus_collector.record_location_accuracy(
                    accuracy_meters, validation_method, accuracy_level, confidence_score
                )
            
        except Exception as e:
            logger.error(f"Error recording location accuracy with monitoring: {e}")
    
    async def record_user_experience_with_monitoring(
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
        """Record user experience with full monitoring integration."""
        try:
            # Record in monitoring service
            await self.monitoring_service.record_user_experience(
                user_id=user_id,
                session_id=session_id,
                action_type=action_type,
                success=success,
                time_to_complete_ms=time_to_complete_ms,
                user_satisfaction=user_satisfaction,
                error_message=error_message,
                retry_count=retry_count
            )
            
            # Record in Prometheus if enabled
            if self.prometheus_enabled:
                self.prometheus_collector.record_user_action(
                    action_type=action_type,
                    result="success" if success else "failure",
                    satisfaction=user_satisfaction
                )
            
        except Exception as e:
            logger.error(f"Error recording user experience with monitoring: {e}")
    
    def _calculate_distance(self, coord1: tuple, coord2: tuple) -> float:
        """Calculate distance between two coordinates in meters."""
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
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get integration service status."""
        try:
            return {
                "integration_active": self.integration_active,
                "monitoring_active": self.monitoring_service.monitoring_active,
                "prometheus_enabled": self.prometheus_enabled,
                "registered_services": list(self.integrations.keys()),
                "service_count": len(self.integrations),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting integration status: {e}")
            return {"error": str(e)}
    
    async def get_combined_dashboard_data(self) -> Dict[str, Any]:
        """Get combined dashboard data from all monitoring services."""
        try:
            # Get data from all services
            monitoring_data = await self.monitoring_service.get_monitoring_dashboard_data()
            analytics_data = await self.analytics_service.get_analytics_dashboard_data()
            
            # Combine data
            combined_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "monitoring": monitoring_data,
                "analytics": analytics_data,
                "integration_status": await self.get_integration_status(),
                "prometheus_metrics": self.prometheus_collector.get_metric_summary() if self.prometheus_enabled else None
            }
            
            return combined_data
            
        except Exception as e:
            logger.error(f"Error getting combined dashboard data: {e}")
            return {"error": str(e)}
    
    def get_prometheus_metrics(self) -> str:
        """Get Prometheus metrics in text format."""
        if self.prometheus_enabled:
            return self.prometheus_collector.get_metrics()
        else:
            return "# Prometheus metrics not available\n"
    
    def get_prometheus_content_type(self) -> str:
        """Get Prometheus metrics content type."""
        if self.prometheus_enabled:
            return self.prometheus_collector.get_metrics_content_type()
        else:
            return "text/plain"
    
    async def generate_comprehensive_report(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate comprehensive monitoring and analytics report."""
        try:
            logger.info(f"Generating comprehensive report from {start_date} to {end_date}")
            
            # Generate all types of reports
            accuracy_report = await self.analytics_service.generate_accuracy_report(start_date, end_date)
            performance_report = await self.analytics_service.generate_performance_report(start_date, end_date)
            ux_report = await self.analytics_service.generate_user_experience_report(start_date, end_date)
            
            # Get current monitoring data
            monitoring_data = await self.monitoring_service.get_monitoring_dashboard_data()
            
            # Get business metrics
            business_metrics = await self.analytics_service.calculate_business_metrics(start_date, end_date)
            
            # Combine into comprehensive report
            comprehensive_report = {
                "report_id": f"comprehensive_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}",
                "report_type": "comprehensive_monitoring_analytics",
                "period": "custom",
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "generated_at": datetime.utcnow().isoformat(),
                "reports": {
                    "accuracy": accuracy_report,
                    "performance": performance_report,
                    "user_experience": ux_report
                },
                "current_monitoring": monitoring_data,
                "business_metrics": business_metrics,
                "integration_status": await self.get_integration_status(),
                "summary": {
                    "total_reports": 3,
                    "monitoring_active": self.monitoring_service.monitoring_active,
                    "prometheus_enabled": self.prometheus_enabled,
                    "registered_services": len(self.integrations)
                }
            }
            
            logger.info(f"Generated comprehensive report: {comprehensive_report['report_id']}")
            return comprehensive_report
            
        except Exception as e:
            logger.error(f"Error generating comprehensive report: {e}")
            raise
    
    async def cleanup_all_data(self, days_to_keep: int = 30):
        """Clean up data from all monitoring services."""
        try:
            # Clean up monitoring service data
            await self.monitoring_service.cleanup_old_metrics(days_to_keep)
            
            # Clean up analytics service data
            await self.analytics_service.cleanup_old_data(days_to_keep)
            
            logger.info(f"Cleaned up all monitoring data older than {days_to_keep} days")
            
        except Exception as e:
            logger.error(f"Error cleaning up all data: {e}")
    
    def get_service_integrations(self) -> Dict[str, Any]:
        """Get information about registered service integrations."""
        try:
            integrations_info = {}
            
            for service_name, integration in self.integrations.items():
                integrations_info[service_name] = {
                    "service_name": integration.service_name,
                    "endpoints": integration.endpoints,
                    "monitoring_enabled": integration.monitoring_enabled,
                    "analytics_enabled": integration.analytics_enabled,
                    "prometheus_enabled": integration.prometheus_enabled,
                    "custom_metrics_count": len(integration.custom_metrics) if integration.custom_metrics else 0
                }
            
            return integrations_info
            
        except Exception as e:
            logger.error(f"Error getting service integrations: {e}")
            return {}
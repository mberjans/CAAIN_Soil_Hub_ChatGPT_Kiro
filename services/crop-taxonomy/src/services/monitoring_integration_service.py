"""
Monitoring Integration Service

This service integrates the comprehensive monitoring and analytics system with the existing
Prometheus/Grafana infrastructure for TICKET-005_crop-variety-recommendations-15.2.

Features:
- Prometheus metrics integration
- Grafana dashboard updates
- Alertmanager configuration
- Data synchronization
- Performance optimization
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import aiohttp
import requests
from pathlib import Path

logger = logging.getLogger(__name__)


class MonitoringIntegrationService:
    """Service for integrating monitoring with Prometheus/Grafana infrastructure."""
    
    def __init__(
        self,
        prometheus_url: str = "http://localhost:9090",
        grafana_url: str = "http://localhost:3001",
        alertmanager_url: str = "http://localhost:9093",
        grafana_api_key: str = None
    ):
        """Initialize the monitoring integration service."""
        self.prometheus_url = prometheus_url
        self.grafana_url = grafana_url
        self.alertmanager_url = alertmanager_url
        self.grafana_api_key = grafana_api_key
        
        # Service endpoints
        self.prometheus_api = f"{prometheus_url}/api/v1"
        self.grafana_api = f"{grafana_url}/api"
        self.alertmanager_api = f"{alertmanager_url}/api/v1"
        
        # Integration status
        self.integration_active = False
        self.sync_task = None
        
        logger.info("Monitoring integration service initialized")
    
    async def start_integration(self, sync_interval_seconds: int = 60):
        """Start integration with monitoring infrastructure."""
        if self.integration_active:
            logger.warning("Integration is already active")
            return
        
        self.integration_active = True
        self.sync_task = asyncio.create_task(
            self._integration_loop(sync_interval_seconds)
        )
        
        logger.info(f"Monitoring integration started (sync interval: {sync_interval_seconds}s)")
    
    async def stop_integration(self):
        """Stop integration with monitoring infrastructure."""
        if not self.integration_active:
            return
        
        self.integration_active = False
        if self.sync_task:
            self.sync_task.cancel()
        
        logger.info("Monitoring integration stopped")
    
    async def _integration_loop(self, sync_interval_seconds: int):
        """Main integration loop."""
        while self.integration_active:
            try:
                # Sync metrics with Prometheus
                await self._sync_metrics_with_prometheus()
                
                # Update Grafana dashboards
                await self._update_grafana_dashboards()
                
                # Sync alerts with Alertmanager
                await self._sync_alerts_with_alertmanager()
                
                # Wait for next sync
                await asyncio.sleep(sync_interval_seconds)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in integration loop: {e}")
                await asyncio.sleep(sync_interval_seconds)
    
    async def _sync_metrics_with_prometheus(self):
        """Sync metrics with Prometheus."""
        try:
            # Get metrics from comprehensive monitoring service
            from .comprehensive_monitoring_analytics_service import get_comprehensive_monitoring_analytics
            
            monitoring_service = get_comprehensive_monitoring_analytics()
            dashboard_data = monitoring_service.get_dashboard_data()
            
            # Convert to Prometheus format
            prometheus_metrics = self._convert_to_prometheus_metrics(dashboard_data)
            
            # Push metrics to Prometheus (if using Pushgateway)
            await self._push_metrics_to_prometheus(prometheus_metrics)
            
            logger.debug("Metrics synced with Prometheus")
            
        except Exception as e:
            logger.error(f"Error syncing metrics with Prometheus: {e}")
    
    def _convert_to_prometheus_metrics(self, dashboard_data) -> str:
        """Convert dashboard data to Prometheus metrics format."""
        metrics_lines = []
        
        # System health metrics
        if dashboard_data.system_health:
            sh = dashboard_data.system_health
            metrics_lines.append(f"variety_recommendations_cpu_percent {sh.cpu_percent}")
            metrics_lines.append(f"variety_recommendations_memory_percent {sh.memory_percent}")
            metrics_lines.append(f"variety_recommendations_memory_used_mb {sh.memory_used_mb}")
            metrics_lines.append(f"variety_recommendations_disk_usage_percent {sh.disk_usage_percent}")
            metrics_lines.append(f"variety_recommendations_active_connections {sh.active_connections}")
            metrics_lines.append(f"variety_recommendations_response_time_ms {sh.response_time_ms}")
            metrics_lines.append(f"variety_recommendations_error_rate {sh.error_rate}")
        
        # User engagement metrics
        if dashboard_data.user_engagement:
            ue = dashboard_data.user_engagement
            metrics_lines.append(f"variety_recommendations_active_users {ue.active_users}")
            metrics_lines.append(f"variety_recommendations_new_users {ue.new_users}")
            metrics_lines.append(f"variety_recommendations_returning_users {ue.returning_users}")
            metrics_lines.append(f"variety_recommendations_session_duration_minutes {ue.session_duration_minutes}")
            metrics_lines.append(f"variety_recommendations_user_satisfaction_score {ue.user_satisfaction_score}")
        
        # Recommendation effectiveness metrics
        if dashboard_data.recommendation_effectiveness:
            re = dashboard_data.recommendation_effectiveness
            metrics_lines.append(f"variety_recommendations_total_recommendations {re.total_recommendations}")
            metrics_lines.append(f"variety_recommendations_successful_recommendations {re.successful_recommendations}")
            metrics_lines.append(f"variety_recommendations_failed_recommendations {re.failed_recommendations}")
            metrics_lines.append(f"variety_recommendations_confidence_score {re.average_confidence_score}")
            metrics_lines.append(f"variety_recommendations_cache_hit_rate {re.cache_hit_rate}")
            metrics_lines.append(f"variety_recommendations_expert_validation_rate {re.expert_validation_rate}")
            metrics_lines.append(f"variety_recommendations_farmer_feedback_score {re.farmer_feedback_score}")
        
        # Business metrics
        if dashboard_data.business_metrics:
            bm = dashboard_data.business_metrics
            metrics_lines.append(f"variety_recommendations_revenue_impact {bm.total_revenue_impact}")
            metrics_lines.append(f"variety_recommendations_cost_savings {bm.cost_savings_estimated}")
            metrics_lines.append(f"variety_recommendations_environmental_impact_score {bm.environmental_impact_score}")
            metrics_lines.append(f"variety_recommendations_user_retention_rate {bm.user_retention_rate}")
            metrics_lines.append(f"variety_recommendations_market_penetration {bm.market_penetration}")
        
        # Alert metrics
        critical_alerts = len([a for a in dashboard_data.alerts if a.level.value == "critical"])
        warning_alerts = len([a for a in dashboard_data.alerts if a.level.value == "warning"])
        info_alerts = len([a for a in dashboard_data.alerts if a.level.value == "info"])
        
        metrics_lines.append(f"variety_recommendations_alerts_total{{level=\"critical\"}} {critical_alerts}")
        metrics_lines.append(f"variety_recommendations_alerts_total{{level=\"warning\"}} {warning_alerts}")
        metrics_lines.append(f"variety_recommendations_alerts_total{{level=\"info\"}} {info_alerts}")
        metrics_lines.append(f"variety_recommendations_alerts_critical {critical_alerts}")
        metrics_lines.append(f"variety_recommendations_alerts_warning {warning_alerts}")
        metrics_lines.append(f"variety_recommendations_alerts_info {info_alerts}")
        
        return "\n".join(metrics_lines)
    
    async def _push_metrics_to_prometheus(self, metrics: str):
        """Push metrics to Prometheus Pushgateway."""
        try:
            pushgateway_url = f"{self.prometheus_url.replace('9090', '9091')}/metrics/job/variety_recommendations"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    pushgateway_url,
                    data=metrics,
                    headers={"Content-Type": "text/plain"}
                ) as response:
                    if response.status == 200:
                        logger.debug("Metrics pushed to Prometheus Pushgateway")
                    else:
                        logger.warning(f"Failed to push metrics to Prometheus: {response.status}")
        
        except Exception as e:
            logger.error(f"Error pushing metrics to Prometheus: {e}")
    
    async def _update_grafana_dashboards(self):
        """Update Grafana dashboards with new data."""
        try:
            if not self.grafana_api_key:
                logger.warning("Grafana API key not configured, skipping dashboard updates")
                return
            
            # Update variety recommendations dashboard
            await self._update_variety_recommendations_dashboard()
            
            logger.debug("Grafana dashboards updated")
            
        except Exception as e:
            logger.error(f"Error updating Grafana dashboards: {e}")
    
    async def _update_variety_recommendations_dashboard(self):
        """Update the variety recommendations dashboard."""
        try:
            dashboard_uid = "variety-recommendations-monitoring"
            
            # Get current dashboard
            headers = {
                "Authorization": f"Bearer {self.grafana_api_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                # Get dashboard
                async with session.get(
                    f"{self.grafana_api}/dashboards/uid/{dashboard_uid}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        dashboard_data = await response.json()
                        
                        # Update dashboard with latest data
                        updated_dashboard = self._update_dashboard_data(dashboard_data)
                        
                        # Save updated dashboard
                        async with session.post(
                            f"{self.grafana_api}/dashboards/db",
                            json=updated_dashboard,
                            headers=headers
                        ) as save_response:
                            if save_response.status == 200:
                                logger.debug("Variety recommendations dashboard updated")
                            else:
                                logger.warning(f"Failed to save dashboard: {save_response.status}")
                    else:
                        logger.warning(f"Failed to get dashboard: {response.status}")
        
        except Exception as e:
            logger.error(f"Error updating variety recommendations dashboard: {e}")
    
    def _update_dashboard_data(self, dashboard_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update dashboard data with latest metrics."""
        # Add timestamp to dashboard
        dashboard_data["time"] = {
            "from": "now-1h",
            "to": "now"
        }
        
        # Update dashboard title with timestamp
        dashboard_data["title"] = f"Variety Recommendations Monitoring - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
        
        return dashboard_data
    
    async def _sync_alerts_with_alertmanager(self):
        """Sync alerts with Alertmanager."""
        try:
            # Get alerts from comprehensive monitoring service
            from .comprehensive_monitoring_analytics_service import get_comprehensive_monitoring_analytics
            
            monitoring_service = get_comprehensive_monitoring_analytics()
            dashboard_data = monitoring_service.get_dashboard_data()
            
            # Convert alerts to Alertmanager format
            alertmanager_alerts = self._convert_to_alertmanager_alerts(dashboard_data.alerts)
            
            # Send alerts to Alertmanager
            await self._send_alerts_to_alertmanager(alertmanager_alerts)
            
            logger.debug("Alerts synced with Alertmanager")
            
        except Exception as e:
            logger.error(f"Error syncing alerts with Alertmanager: {e}")
    
    def _convert_to_alertmanager_alerts(self, alerts: List) -> List[Dict[str, Any]]:
        """Convert alerts to Alertmanager format."""
        alertmanager_alerts = []
        
        for alert in alerts:
            alertmanager_alert = {
                "labels": {
                    "alertname": alert.title,
                    "severity": alert.level.value,
                    "service": "variety-recommendations",
                    "metric_name": alert.metric_name
                },
                "annotations": {
                    "summary": alert.title,
                    "description": alert.message,
                    "threshold_value": str(alert.threshold_value),
                    "current_value": str(alert.current_value)
                },
                "startsAt": alert.timestamp.isoformat() + "Z",
                "generatorURL": f"{self.prometheus_url}/graph?g0.expr={alert.metric_name}"
            }
            
            alertmanager_alerts.append(alertmanager_alert)
        
        return alertmanager_alerts
    
    async def _send_alerts_to_alertmanager(self, alerts: List[Dict[str, Any]]):
        """Send alerts to Alertmanager."""
        try:
            if not alerts:
                return
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.alertmanager_api}/alerts",
                    json=alerts,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        logger.debug(f"Sent {len(alerts)} alerts to Alertmanager")
                    else:
                        logger.warning(f"Failed to send alerts to Alertmanager: {response.status}")
        
        except Exception as e:
            logger.error(f"Error sending alerts to Alertmanager: {e}")
    
    async def test_integration(self) -> Dict[str, Any]:
        """Test integration with monitoring infrastructure."""
        results = {
            "prometheus": {"status": "unknown", "error": None},
            "grafana": {"status": "unknown", "error": None},
            "alertmanager": {"status": "unknown", "error": None},
            "overall": "unknown"
        }
        
        # Test Prometheus connection
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.prometheus_api}/query?query=up") as response:
                    if response.status == 200:
                        results["prometheus"]["status"] = "healthy"
                    else:
                        results["prometheus"]["status"] = "unhealthy"
                        results["prometheus"]["error"] = f"HTTP {response.status}"
        except Exception as e:
            results["prometheus"]["status"] = "unhealthy"
            results["prometheus"]["error"] = str(e)
        
        # Test Grafana connection
        try:
            if self.grafana_api_key:
                headers = {"Authorization": f"Bearer {self.grafana_api_key}"}
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.grafana_api}/health", headers=headers) as response:
                        if response.status == 200:
                            results["grafana"]["status"] = "healthy"
                        else:
                            results["grafana"]["status"] = "unhealthy"
                            results["grafana"]["error"] = f"HTTP {response.status}"
            else:
                results["grafana"]["status"] = "not_configured"
                results["grafana"]["error"] = "API key not provided"
        except Exception as e:
            results["grafana"]["status"] = "unhealthy"
            results["grafana"]["error"] = str(e)
        
        # Test Alertmanager connection
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.alertmanager_api}/status") as response:
                    if response.status == 200:
                        results["alertmanager"]["status"] = "healthy"
                    else:
                        results["alertmanager"]["status"] = "unhealthy"
                        results["alertmanager"]["error"] = f"HTTP {response.status}"
        except Exception as e:
            results["alertmanager"]["status"] = "unhealthy"
            results["alertmanager"]["error"] = str(e)
        
        # Determine overall status
        all_healthy = all(
            results[service]["status"] in ["healthy", "not_configured"]
            for service in ["prometheus", "grafana", "alertmanager"]
        )
        
        results["overall"] = "healthy" if all_healthy else "unhealthy"
        
        return results
    
    async def setup_monitoring_infrastructure(self):
        """Setup monitoring infrastructure components."""
        try:
            # Create Prometheus configuration for variety recommendations
            await self._setup_prometheus_config()
            
            # Create Grafana dashboard
            await self._setup_grafana_dashboard()
            
            # Create Alertmanager configuration
            await self._setup_alertmanager_config()
            
            logger.info("Monitoring infrastructure setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up monitoring infrastructure: {e}")
            raise
    
    async def _setup_prometheus_config(self):
        """Setup Prometheus configuration for variety recommendations."""
        config = {
            "scrape_configs": [
                {
                    "job_name": "variety-recommendations",
                    "static_configs": [
                        {
                            "targets": ["localhost:8000"]
                        }
                    ],
                    "metrics_path": "/metrics",
                    "scrape_interval": "30s"
                }
            ],
            "rule_files": [
                "rules/variety_recommendations_alerts.yml"
            ],
            "alerting": {
                "alertmanagers": [
                    {
                        "static_configs": [
                            {
                                "targets": ["localhost:9093"]
                            }
                        ]
                    }
                ]
            }
        }
        
        # Save configuration
        config_path = Path("infrastructure/monitoring/prometheus-variety-recommendations.yml")
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            import yaml
            yaml.dump(config, f, default_flow_style=False)
        
        logger.info("Prometheus configuration created")
    
    async def _setup_grafana_dashboard(self):
        """Setup Grafana dashboard for variety recommendations."""
        # Dashboard configuration is already created in the infrastructure/monitoring directory
        logger.info("Grafana dashboard configuration available")
    
    async def _setup_alertmanager_config(self):
        """Setup Alertmanager configuration for variety recommendations."""
        config = {
            "global": {
                "smtp_smarthost": "localhost:587",
                "smtp_from": "alerts@caain-soil-hub.ca"
            },
            "route": {
                "group_by": ["alertname"],
                "group_wait": "10s",
                "group_interval": "10s",
                "repeat_interval": "1h",
                "receiver": "variety-recommendations-alerts"
            },
            "receivers": [
                {
                    "name": "variety-recommendations-alerts",
                    "email_configs": [
                        {
                            "to": "admin@caain-soil-hub.ca",
                            "subject": "Variety Recommendations Alert: {{ .GroupLabels.alertname }}",
                            "body": "Alert: {{ .GroupLabels.alertname }}\nDescription: {{ .CommonAnnotations.description }}"
                        }
                    ]
                }
            ]
        }
        
        # Save configuration
        config_path = Path("infrastructure/monitoring/alertmanager-variety-recommendations.yml")
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            import yaml
            yaml.dump(config, f, default_flow_style=False)
        
        logger.info("Alertmanager configuration created")


# Singleton instance for global access
monitoring_integration: Optional[MonitoringIntegrationService] = None


def get_monitoring_integration(
    prometheus_url: str = "http://localhost:9090",
    grafana_url: str = "http://localhost:3001",
    alertmanager_url: str = "http://localhost:9093",
    grafana_api_key: str = None
) -> MonitoringIntegrationService:
    """Get or create the global monitoring integration instance."""
    global monitoring_integration
    
    if monitoring_integration is None:
        monitoring_integration = MonitoringIntegrationService(
            prometheus_url, grafana_url, alertmanager_url, grafana_api_key
        )
    
    return monitoring_integration
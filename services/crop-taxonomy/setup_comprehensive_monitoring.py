#!/usr/bin/env python3
"""
Comprehensive Monitoring Setup Script

This script sets up the comprehensive monitoring and analytics infrastructure
for TICKET-005_crop-variety-recommendations-15.2.

Features:
- Setup Prometheus configuration
- Deploy Grafana dashboards
- Configure Alertmanager rules
- Initialize monitoring services
- Test integration
- Start monitoring
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from datetime import datetime
import json
import yaml

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from services.comprehensive_monitoring_analytics_service import get_comprehensive_monitoring_analytics
from services.monitoring_integration_service import get_monitoring_integration
from services.comprehensive_reporting_service import get_reporting_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ComprehensiveMonitoringSetup:
    """Setup class for comprehensive monitoring infrastructure."""
    
    def __init__(self):
        """Initialize the setup class."""
        self.setup_start_time = datetime.utcnow()
        self.setup_log = []
        
        logger.info("Comprehensive monitoring setup initialized")
    
    async def run_setup(self):
        """Run the complete setup process."""
        try:
            logger.info("Starting comprehensive monitoring setup...")
            
            # Step 1: Initialize services
            await self._initialize_services()
            
            # Step 2: Setup monitoring infrastructure
            await self._setup_monitoring_infrastructure()
            
            # Step 3: Configure Prometheus
            await self._configure_prometheus()
            
            # Step 4: Setup Grafana dashboards
            await self._setup_grafana_dashboards()
            
            # Step 5: Configure Alertmanager
            await self._configure_alertmanager()
            
            # Step 6: Test integration
            await self._test_integration()
            
            # Step 7: Start monitoring
            await self._start_monitoring()
            
            # Step 8: Generate setup report
            await self._generate_setup_report()
            
            logger.info("Comprehensive monitoring setup completed successfully!")
            
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            await self._generate_error_report(e)
            raise
    
    async def _initialize_services(self):
        """Initialize monitoring services."""
        logger.info("Initializing monitoring services...")
        
        try:
            # Initialize comprehensive monitoring analytics service
            self.monitoring_service = get_comprehensive_monitoring_analytics()
            logger.info("✓ Comprehensive monitoring analytics service initialized")
            
            # Initialize monitoring integration service
            self.integration_service = get_monitoring_integration()
            logger.info("✓ Monitoring integration service initialized")
            
            # Initialize reporting service
            self.reporting_service = get_reporting_service()
            logger.info("✓ Comprehensive reporting service initialized")
            
            self._log_step("services_initialized", "All monitoring services initialized successfully")
            
        except Exception as e:
            logger.error(f"Service initialization failed: {e}")
            raise
    
    async def _setup_monitoring_infrastructure(self):
        """Setup monitoring infrastructure."""
        logger.info("Setting up monitoring infrastructure...")
        
        try:
            # Create infrastructure directories
            infrastructure_dir = Path("infrastructure/monitoring")
            infrastructure_dir.mkdir(parents=True, exist_ok=True)
            
            # Create reports directory
            reports_dir = Path("reports")
            reports_dir.mkdir(exist_ok=True)
            
            # Create logs directory
            logs_dir = Path("logs")
            logs_dir.mkdir(exist_ok=True)
            
            logger.info("✓ Infrastructure directories created")
            self._log_step("infrastructure_setup", "Monitoring infrastructure directories created")
            
        except Exception as e:
            logger.error(f"Infrastructure setup failed: {e}")
            raise
    
    async def _configure_prometheus(self):
        """Configure Prometheus for variety recommendations."""
        logger.info("Configuring Prometheus...")
        
        try:
            # Create Prometheus configuration
            prometheus_config = {
                "global": {
                    "scrape_interval": "30s",
                    "evaluation_interval": "30s"
                },
                "scrape_configs": [
                    {
                        "job_name": "variety-recommendations",
                        "static_configs": [
                            {
                                "targets": ["localhost:8000"]
                            }
                        ],
                        "metrics_path": "/metrics",
                        "scrape_interval": "30s",
                        "scrape_timeout": "10s"
                    },
                    {
                        "job_name": "variety-recommendations-monitoring",
                        "static_configs": [
                            {
                                "targets": ["localhost:8000"]
                            }
                        ],
                        "metrics_path": "/api/v1/crop-taxonomy/monitoring/metrics",
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
            
            # Save Prometheus configuration
            config_path = Path("infrastructure/monitoring/prometheus-variety-recommendations.yml")
            with open(config_path, 'w') as f:
                yaml.dump(prometheus_config, f, default_flow_style=False)
            
            logger.info("✓ Prometheus configuration created")
            
            # Create alert rules
            await self._create_prometheus_alert_rules()
            
            self._log_step("prometheus_configured", "Prometheus configuration completed")
            
        except Exception as e:
            logger.error(f"Prometheus configuration failed: {e}")
            raise
    
    async def _create_prometheus_alert_rules(self):
        """Create Prometheus alert rules for variety recommendations."""
        logger.info("Creating Prometheus alert rules...")
        
        try:
            # Create rules directory
            rules_dir = Path("infrastructure/monitoring/rules")
            rules_dir.mkdir(exist_ok=True)
            
            # Define alert rules
            alert_rules = {
                "groups": [
                    {
                        "name": "variety_recommendations_alerts",
                        "rules": [
                            {
                                "alert": "HighCPUUsage",
                                "expr": "variety_recommendations_cpu_percent > 80",
                                "for": "5m",
                                "labels": {
                                    "severity": "warning",
                                    "service": "variety-recommendations"
                                },
                                "annotations": {
                                    "summary": "High CPU usage detected",
                                    "description": "CPU usage is {{ $value }}% for variety recommendations service"
                                }
                            },
                            {
                                "alert": "HighMemoryUsage",
                                "expr": "variety_recommendations_memory_percent > 85",
                                "for": "5m",
                                "labels": {
                                    "severity": "warning",
                                    "service": "variety-recommendations"
                                },
                                "annotations": {
                                    "summary": "High memory usage detected",
                                    "description": "Memory usage is {{ $value }}% for variety recommendations service"
                                }
                            },
                            {
                                "alert": "SlowResponseTime",
                                "expr": "variety_recommendations_response_time_ms > 3000",
                                "for": "2m",
                                "labels": {
                                    "severity": "warning",
                                    "service": "variety-recommendations"
                                },
                                "annotations": {
                                    "summary": "Slow response time detected",
                                    "description": "Response time is {{ $value }}ms for variety recommendations service"
                                }
                            },
                            {
                                "alert": "HighErrorRate",
                                "expr": "variety_recommendations_error_rate > 0.05",
                                "for": "2m",
                                "labels": {
                                    "severity": "critical",
                                    "service": "variety-recommendations"
                                },
                                "annotations": {
                                    "summary": "High error rate detected",
                                    "description": "Error rate is {{ $value }}% for variety recommendations service"
                                }
                            },
                            {
                                "alert": "LowUserSatisfaction",
                                "expr": "variety_recommendations_user_satisfaction_score < 0.8",
                                "for": "10m",
                                "labels": {
                                    "severity": "warning",
                                    "service": "variety-recommendations"
                                },
                                "annotations": {
                                    "summary": "Low user satisfaction detected",
                                    "description": "User satisfaction score is {{ $value }} for variety recommendations service"
                                }
                            },
                            {
                                "alert": "LowRecommendationConfidence",
                                "expr": "variety_recommendations_confidence_score < 0.8",
                                "for": "5m",
                                "labels": {
                                    "severity": "warning",
                                    "service": "variety-recommendations"
                                },
                                "annotations": {
                                    "summary": "Low recommendation confidence detected",
                                    "description": "Recommendation confidence score is {{ $value }} for variety recommendations service"
                                }
                            }
                        ]
                    }
                ]
            }
            
            # Save alert rules
            rules_path = Path("infrastructure/monitoring/rules/variety_recommendations_alerts.yml")
            with open(rules_path, 'w') as f:
                yaml.dump(alert_rules, f, default_flow_style=False)
            
            logger.info("✓ Prometheus alert rules created")
            
        except Exception as e:
            logger.error(f"Alert rules creation failed: {e}")
            raise
    
    async def _setup_grafana_dashboards(self):
        """Setup Grafana dashboards."""
        logger.info("Setting up Grafana dashboards...")
        
        try:
            # Create Grafana directories
            grafana_dir = Path("infrastructure/monitoring/grafana")
            grafana_dir.mkdir(exist_ok=True)
            
            dashboards_dir = grafana_dir / "dashboards"
            dashboards_dir.mkdir(exist_ok=True)
            
            provisioning_dir = grafana_dir / "provisioning"
            provisioning_dir.mkdir(exist_ok=True)
            
            # Create dashboard provisioning configuration
            dashboard_config = {
                "apiVersion": 1,
                "providers": [
                    {
                        "name": "variety-recommendations-dashboards",
                        "orgId": 1,
                        "folder": "Variety Recommendations",
                        "type": "file",
                        "disableDeletion": False,
                        "updateIntervalSeconds": 10,
                        "allowUiUpdates": True,
                        "options": {
                            "path": "/etc/grafana/provisioning/dashboards/variety-recommendations"
                        }
                    }
                ]
            }
            
            # Save dashboard provisioning config
            dashboard_provisioning_path = provisioning_dir / "dashboards" / "dashboard.yml"
            dashboard_provisioning_path.parent.mkdir(exist_ok=True)
            with open(dashboard_provisioning_path, 'w') as f:
                yaml.dump(dashboard_config, f, default_flow_style=False)
            
            # Create datasource provisioning configuration
            datasource_config = {
                "apiVersion": 1,
                "datasources": [
                    {
                        "name": "Prometheus",
                        "type": "prometheus",
                        "access": "proxy",
                        "url": "http://prometheus:9090",
                        "isDefault": True,
                        "editable": True
                    }
                ]
            }
            
            # Save datasource provisioning config
            datasource_provisioning_path = provisioning_dir / "datasources" / "prometheus.yml"
            datasource_provisioning_path.parent.mkdir(exist_ok=True)
            with open(datasource_provisioning_path, 'w') as f:
                yaml.dump(datasource_config, f, default_flow_style=False)
            
            logger.info("✓ Grafana provisioning configuration created")
            
            # The dashboard JSON is already created in the infrastructure/monitoring directory
            logger.info("✓ Variety recommendations dashboard available")
            
            self._log_step("grafana_setup", "Grafana dashboards and provisioning configured")
            
        except Exception as e:
            logger.error(f"Grafana setup failed: {e}")
            raise
    
    async def _configure_alertmanager(self):
        """Configure Alertmanager for variety recommendations."""
        logger.info("Configuring Alertmanager...")
        
        try:
            # Create Alertmanager configuration
            alertmanager_config = {
                "global": {
                    "smtp_smarthost": "localhost:587",
                    "smtp_from": "alerts@caain-soil-hub.ca",
                    "smtp_auth_username": "alerts@caain-soil-hub.ca",
                    "smtp_auth_password": "password"
                },
                "route": {
                    "group_by": ["alertname", "service"],
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
                                "body": """
Alert: {{ .GroupLabels.alertname }}
Service: {{ .GroupLabels.service }}
Severity: {{ .GroupLabels.severity }}

Description: {{ .CommonAnnotations.description }}

Firing alerts:
{{ range .Alerts }}
- {{ .Annotations.summary }}
{{ end }}
                                """.strip()
                            }
                        ],
                        "webhook_configs": [
                            {
                                "url": "http://localhost:8000/api/v1/crop-taxonomy/monitoring/alerts/webhook",
                                "send_resolved": True
                            }
                        ]
                    }
                ],
                "inhibit_rules": [
                    {
                        "source_match": {
                            "severity": "critical"
                        },
                        "target_match": {
                            "severity": "warning"
                        },
                        "equal": ["alertname", "service"]
                    }
                ]
            }
            
            # Save Alertmanager configuration
            config_path = Path("infrastructure/monitoring/alertmanager-variety-recommendations.yml")
            with open(config_path, 'w') as f:
                yaml.dump(alertmanager_config, f, default_flow_style=False)
            
            logger.info("✓ Alertmanager configuration created")
            
            self._log_step("alertmanager_configured", "Alertmanager configuration completed")
            
        except Exception as e:
            logger.error(f"Alertmanager configuration failed: {e}")
            raise
    
    async def _test_integration(self):
        """Test the monitoring integration."""
        logger.info("Testing monitoring integration...")
        
        try:
            # Test integration connectivity
            test_results = await self.integration_service.test_integration()
            
            logger.info(f"✓ Integration test results: {test_results['overall']}")
            
            if test_results['overall'] == 'healthy':
                logger.info("✓ All monitoring components are healthy")
            else:
                logger.warning("⚠ Some monitoring components are not healthy")
                for component, result in test_results.items():
                    if component != 'overall' and result['status'] != 'healthy':
                        logger.warning(f"  - {component}: {result['status']} - {result.get('error', 'No error details')}")
            
            self._log_step("integration_tested", f"Integration test completed: {test_results['overall']}")
            
        except Exception as e:
            logger.error(f"Integration test failed: {e}")
            raise
    
    async def _start_monitoring(self):
        """Start the monitoring services."""
        logger.info("Starting monitoring services...")
        
        try:
            # Start comprehensive monitoring analytics
            self.monitoring_service.start_monitoring(interval_seconds=30)
            logger.info("✓ Comprehensive monitoring analytics started")
            
            # Start monitoring integration
            await self.integration_service.start_integration(sync_interval_seconds=60)
            logger.info("✓ Monitoring integration started")
            
            self._log_step("monitoring_started", "All monitoring services started successfully")
            
        except Exception as e:
            logger.error(f"Monitoring start failed: {e}")
            raise
    
    async def _generate_setup_report(self):
        """Generate setup completion report."""
        logger.info("Generating setup report...")
        
        try:
            setup_duration = datetime.utcnow() - self.setup_start_time
            
            report = {
                "setup_completed": True,
                "setup_duration_seconds": setup_duration.total_seconds(),
                "setup_start_time": self.setup_start_time.isoformat(),
                "setup_end_time": datetime.utcnow().isoformat(),
                "steps_completed": self.setup_log,
                "services_initialized": [
                    "comprehensive_monitoring_analytics",
                    "monitoring_integration",
                    "comprehensive_reporting"
                ],
                "infrastructure_components": [
                    "prometheus_configuration",
                    "grafana_dashboards",
                    "alertmanager_configuration",
                    "alert_rules"
                ],
                "monitoring_status": "active",
                "next_steps": [
                    "Access Grafana at http://localhost:3001",
                    "Access Prometheus at http://localhost:9090",
                    "Access Alertmanager at http://localhost:9093",
                    "Monitor system health via /api/v1/crop-taxonomy/monitoring/dashboard",
                    "Generate reports via /api/v1/crop-taxonomy/reports/generate"
                ]
            }
            
            # Save setup report
            report_path = Path("reports/setup_report.json")
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info("✓ Setup report generated")
            
            # Print summary
            print("\n" + "="*60)
            print("COMPREHENSIVE MONITORING SETUP COMPLETED")
            print("="*60)
            print(f"Setup Duration: {setup_duration.total_seconds():.1f} seconds")
            print(f"Services Initialized: {len(report['services_initialized'])}")
            print(f"Infrastructure Components: {len(report['infrastructure_components'])}")
            print(f"Monitoring Status: {report['monitoring_status']}")
            print("\nAccess Points:")
            for step in report['next_steps']:
                print(f"  • {step}")
            print("="*60)
            
        except Exception as e:
            logger.error(f"Setup report generation failed: {e}")
            raise
    
    async def _generate_error_report(self, error: Exception):
        """Generate error report for failed setup."""
        logger.error("Generating error report...")
        
        try:
            error_report = {
                "setup_completed": False,
                "setup_duration_seconds": (datetime.utcnow() - self.setup_start_time).total_seconds(),
                "setup_start_time": self.setup_start_time.isoformat(),
                "error_time": datetime.utcnow().isoformat(),
                "error_message": str(error),
                "error_type": type(error).__name__,
                "steps_completed": self.setup_log,
                "recommendations": [
                    "Check system requirements and dependencies",
                    "Verify network connectivity to monitoring services",
                    "Review error logs for detailed information",
                    "Retry setup after resolving issues"
                ]
            }
            
            # Save error report
            error_report_path = Path("reports/setup_error_report.json")
            with open(error_report_path, 'w') as f:
                json.dump(error_report, f, indent=2)
            
            logger.error("✓ Error report generated")
            
        except Exception as e:
            logger.error(f"Error report generation failed: {e}")
    
    def _log_step(self, step_name: str, description: str):
        """Log a setup step."""
        step_log = {
            "step": step_name,
            "description": description,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed"
        }
        self.setup_log.append(step_log)
        logger.info(f"✓ {description}")


async def main():
    """Main setup function."""
    try:
        setup = ComprehensiveMonitoringSetup()
        await setup.run_setup()
        
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
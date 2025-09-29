#!/usr/bin/env python3
"""
Monitoring and Alerting Setup for CAAIN Soil Hub Crop Taxonomy Service
Configures comprehensive monitoring, metrics, and alerting systems
"""

import os
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess


class MonitoringSetup:
    """Sets up comprehensive monitoring and alerting for the service."""
    
    def __init__(self):
        self.service_path = Path(__file__).parent
        self.monitoring_config = {
            'metrics': {},
            'alerts': {},
            'dashboards': {},
            'health_checks': {}
        }
    
    def setup_prometheus_config(self) -> bool:
        """Set up Prometheus configuration for metrics collection."""
        print("📊 Setting up Prometheus configuration...")
        
        prometheus_config = {
            'global': {
                'scrape_interval': '15s',
                'evaluation_interval': '15s'
            },
            'rule_files': [
                'alert_rules.yml'
            ],
            'scrape_configs': [
                {
                    'job_name': 'crop-taxonomy-service',
                    'static_configs': [
                        {
                            'targets': ['crop-taxonomy:8000']
                        }
                    ],
                    'metrics_path': '/metrics',
                    'scrape_interval': '10s'
                },
                {
                    'job_name': 'postgres-exporter',
                    'static_configs': [
                        {
                            'targets': ['postgres-exporter:9187']
                        }
                    ]
                },
                {
                    'job_name': 'redis-exporter',
                    'static_configs': [
                        {
                            'targets': ['redis-exporter:9121']
                        }
                    ]
                },
                {
                    'job_name': 'nginx-exporter',
                    'static_configs': [
                        {
                            'targets': ['nginx-exporter:9113']
                        }
                    ]
                }
            ],
            'alerting': {
                'alertmanagers': [
                    {
                        'static_configs': [
                            {
                                'targets': ['alertmanager:9093']
                            }
                        ]
                    }
                ]
            }
        }
        
        # Write Prometheus configuration
        prometheus_config_path = self.service_path / "prometheus.yml"
        with open(prometheus_config_path, 'w') as f:
            yaml.dump(prometheus_config, f, default_flow_style=False)
        
        print("✅ Prometheus configuration created")
        return True
    
    def setup_alert_rules(self) -> bool:
        """Set up alerting rules for the service."""
        print("🚨 Setting up alerting rules...")
        
        alert_rules = {
            'groups': [
                {
                    'name': 'crop-taxonomy-service',
                    'rules': [
                        {
                            'alert': 'ServiceDown',
                            'expr': 'up{job="crop-taxonomy-service"} == 0',
                            'for': '1m',
                            'labels': {
                                'severity': 'critical'
                            },
                            'annotations': {
                                'summary': 'Crop Taxonomy Service is down',
                                'description': 'The crop taxonomy service has been down for more than 1 minute.'
                            }
                        },
                        {
                            'alert': 'HighErrorRate',
                            'expr': 'rate(http_requests_total{status=~"5.."}[5m]) > 0.1',
                            'for': '2m',
                            'labels': {
                                'severity': 'warning'
                            },
                            'annotations': {
                                'summary': 'High error rate detected',
                                'description': 'Error rate is above 10% for more than 2 minutes.'
                            }
                        },
                        {
                            'alert': 'HighResponseTime',
                            'expr': 'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 5',
                            'for': '3m',
                            'labels': {
                                'severity': 'warning'
                            },
                            'annotations': {
                                'summary': 'High response time detected',
                                'description': '95th percentile response time is above 5 seconds.'
                            }
                        },
                        {
                            'alert': 'HighCPUUsage',
                            'expr': '100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80',
                            'for': '5m',
                            'labels': {
                                'severity': 'warning'
                            },
                            'annotations': {
                                'summary': 'High CPU usage detected',
                                'description': 'CPU usage is above 80% for more than 5 minutes.'
                            }
                        },
                        {
                            'alert': 'HighMemoryUsage',
                            'expr': '(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85',
                            'for': '5m',
                            'labels': {
                                'severity': 'warning'
                            },
                            'annotations': {
                                'summary': 'High memory usage detected',
                                'description': 'Memory usage is above 85% for more than 5 minutes.'
                            }
                        },
                        {
                            'alert': 'DatabaseConnectionFailure',
                            'expr': 'pg_up == 0',
                            'for': '1m',
                            'labels': {
                                'severity': 'critical'
                            },
                            'annotations': {
                                'summary': 'Database connection failure',
                                'description': 'Cannot connect to PostgreSQL database.'
                            }
                        },
                        {
                            'alert': 'RedisConnectionFailure',
                            'expr': 'redis_up == 0',
                            'for': '1m',
                            'labels': {
                                'severity': 'critical'
                            },
                            'annotations': {
                                'summary': 'Redis connection failure',
                                'description': 'Cannot connect to Redis cache.'
                            }
                        },
                        {
                            'alert': 'DiskSpaceLow',
                            'expr': '(1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100 > 90',
                            'for': '5m',
                            'labels': {
                                'severity': 'critical'
                            },
                            'annotations': {
                                'summary': 'Disk space is running low',
                                'description': 'Disk usage is above 90% for more than 5 minutes.'
                            }
                        }
                    ]
                }
            ]
        }
        
        # Write alert rules
        alert_rules_path = self.service_path / "alert_rules.yml"
        with open(alert_rules_path, 'w') as f:
            yaml.dump(alert_rules, f, default_flow_style=False)
        
        print("✅ Alert rules configured")
        return True
    
    def setup_grafana_dashboards(self) -> bool:
        """Set up Grafana dashboards for monitoring."""
        print("📈 Setting up Grafana dashboards...")
        
        # Service overview dashboard
        service_dashboard = {
            'dashboard': {
                'id': None,
                'title': 'CAAIN Crop Taxonomy Service Overview',
                'tags': ['caain', 'crop-taxonomy', 'agriculture'],
                'timezone': 'browser',
                'panels': [
                    {
                        'id': 1,
                        'title': 'Service Status',
                        'type': 'stat',
                        'targets': [
                            {
                                'expr': 'up{job="crop-taxonomy-service"}',
                                'legendFormat': 'Service Up'
                            }
                        ],
                        'fieldConfig': {
                            'defaults': {
                                'color': {
                                    'mode': 'thresholds'
                                },
                                'thresholds': {
                                    'steps': [
                                        {'color': 'red', 'value': 0},
                                        {'color': 'green', 'value': 1}
                                    ]
                                }
                            }
                        },
                        'gridPos': {'h': 8, 'w': 12, 'x': 0, 'y': 0}
                    },
                    {
                        'id': 2,
                        'title': 'Request Rate',
                        'type': 'graph',
                        'targets': [
                            {
                                'expr': 'rate(http_requests_total[5m])',
                                'legendFormat': '{{method}} {{endpoint}}'
                            }
                        ],
                        'gridPos': {'h': 8, 'w': 12, 'x': 12, 'y': 0}
                    },
                    {
                        'id': 3,
                        'title': 'Response Time',
                        'type': 'graph',
                        'targets': [
                            {
                                'expr': 'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))',
                                'legendFormat': '95th percentile'
                            },
                            {
                                'expr': 'histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))',
                                'legendFormat': '50th percentile'
                            }
                        ],
                        'gridPos': {'h': 8, 'w': 24, 'x': 0, 'y': 8}
                    },
                    {
                        'id': 4,
                        'title': 'Error Rate',
                        'type': 'graph',
                        'targets': [
                            {
                                'expr': 'rate(http_requests_total{status=~"5.."}[5m])',
                                'legendFormat': '5xx errors'
                            },
                            {
                                'expr': 'rate(http_requests_total{status=~"4.."}[5m])',
                                'legendFormat': '4xx errors'
                            }
                        ],
                        'gridPos': {'h': 8, 'w': 12, 'x': 0, 'y': 16}
                    },
                    {
                        'id': 5,
                        'title': 'Database Connections',
                        'type': 'graph',
                        'targets': [
                            {
                                'expr': 'pg_stat_database_numbackends',
                                'legendFormat': 'Active connections'
                            }
                        ],
                        'gridPos': {'h': 8, 'w': 12, 'x': 12, 'y': 16}
                    }
                ],
                'time': {
                    'from': 'now-1h',
                    'to': 'now'
                },
                'refresh': '30s'
            }
        }
        
        # Write dashboard configuration
        dashboard_path = self.service_path / "grafana-dashboard.json"
        with open(dashboard_path, 'w') as f:
            json.dump(service_dashboard, f, indent=2)
        
        print("✅ Grafana dashboard configured")
        return True
    
    def setup_health_checks(self) -> bool:
        """Set up comprehensive health checks."""
        print("🏥 Setting up health checks...")
        
        health_check_config = {
            'health_checks': [
                {
                    'name': 'service_health',
                    'endpoint': '/api/v1/health',
                    'interval': 30,
                    'timeout': 10,
                    'retries': 3,
                    'expected_status': 200
                },
                {
                    'name': 'database_health',
                    'endpoint': '/api/v1/health/database',
                    'interval': 60,
                    'timeout': 15,
                    'retries': 2,
                    'expected_status': 200
                },
                {
                    'name': 'redis_health',
                    'endpoint': '/api/v1/health/redis',
                    'interval': 60,
                    'timeout': 10,
                    'retries': 2,
                    'expected_status': 200
                },
                {
                    'name': 'external_apis',
                    'endpoint': '/api/v1/health/external',
                    'interval': 300,
                    'timeout': 30,
                    'retries': 1,
                    'expected_status': 200
                }
            ],
            'alerting': {
                'webhook_url': None,  # Configure in production
                'email': None,        # Configure in production
                'slack': None         # Configure in production
            }
        }
        
        # Write health check configuration
        health_config_path = self.service_path / "health-checks.yml"
        with open(health_config_path, 'w') as f:
            yaml.dump(health_check_config, f, default_flow_style=False)
        
        print("✅ Health checks configured")
        return True
    
    def setup_logging_config(self) -> bool:
        """Set up structured logging configuration."""
        print("📝 Setting up logging configuration...")
        
        logging_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
                },
                'detailed': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s'
                },
                'json': {
                    'format': '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': 'INFO',
                    'formatter': 'standard',
                    'stream': 'ext://sys.stdout'
                },
                'file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': 'DEBUG',
                    'formatter': 'detailed',
                    'filename': '/app/logs/app.log',
                    'maxBytes': 10485760,  # 10MB
                    'backupCount': 5
                },
                'error_file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': 'ERROR',
                    'formatter': 'detailed',
                    'filename': '/app/logs/error.log',
                    'maxBytes': 10485760,  # 10MB
                    'backupCount': 5
                }
            },
            'loggers': {
                '': {
                    'handlers': ['console', 'file'],
                    'level': 'INFO',
                    'propagate': False
                },
                'uvicorn.error': {
                    'handlers': ['console', 'error_file'],
                    'level': 'ERROR',
                    'propagate': False
                },
                'uvicorn.access': {
                    'handlers': ['file'],
                    'level': 'INFO',
                    'propagate': False
                }
            }
        }
        
        # Write logging configuration
        logging_config_path = self.service_path / "logging.conf"
        with open(logging_config_path, 'w') as f:
            import configparser
            config = configparser.ConfigParser()
            # Convert dict to configparser format
            config.read_dict(logging_config)
            config.write(open(logging_config_path, 'w'))
        
        print("✅ Logging configuration created")
        return True
    
    def setup_monitoring_docker_compose(self) -> bool:
        """Set up Docker Compose for monitoring stack."""
        print("🐳 Setting up monitoring Docker Compose...")
        
        monitoring_compose = {
            'version': '3.8',
            'services': {
                'prometheus': {
                    'image': 'prom/prometheus:latest',
                    'container_name': 'caain-prometheus',
                    'ports': ['9090:9090'],
                    'volumes': [
                        './prometheus.yml:/etc/prometheus/prometheus.yml',
                        './alert_rules.yml:/etc/prometheus/alert_rules.yml',
                        'prometheus_data:/prometheus'
                    ],
                    'command': [
                        '--config.file=/etc/prometheus/prometheus.yml',
                        '--storage.tsdb.path=/prometheus',
                        '--web.console.libraries=/etc/prometheus/console_libraries',
                        '--web.console.templates=/etc/prometheus/consoles',
                        '--storage.tsdb.retention.time=200h',
                        '--web.enable-lifecycle'
                    ],
                    'networks': ['caain-network']
                },
                'grafana': {
                    'image': 'grafana/grafana:latest',
                    'container_name': 'caain-grafana',
                    'ports': ['3000:3000'],
                    'environment': [
                        'GF_SECURITY_ADMIN_PASSWORD=admin',
                        'GF_USERS_ALLOW_SIGN_UP=false'
                    ],
                    'volumes': [
                        'grafana_data:/var/lib/grafana',
                        './grafana-dashboard.json:/var/lib/grafana/dashboards/crop-taxonomy.json'
                    ],
                    'networks': ['caain-network']
                },
                'alertmanager': {
                    'image': 'prom/alertmanager:latest',
                    'container_name': 'caain-alertmanager',
                    'ports': ['9093:9093'],
                    'volumes': [
                        './alertmanager.yml:/etc/alertmanager/alertmanager.yml'
                    ],
                    'networks': ['caain-network']
                },
                'postgres-exporter': {
                    'image': 'prometheuscommunity/postgres-exporter:latest',
                    'container_name': 'caain-postgres-exporter',
                    'environment': [
                        'DATA_SOURCE_NAME=postgresql://caain_user:secure_password@postgres:5432/crop_taxonomy?sslmode=disable'
                    ],
                    'ports': ['9187:9187'],
                    'networks': ['caain-network']
                },
                'redis-exporter': {
                    'image': 'oliver006/redis_exporter:latest',
                    'container_name': 'caain-redis-exporter',
                    'environment': [
                        'REDIS_ADDR=redis://redis:6379',
                        'REDIS_PASSWORD=redis_password'
                    ],
                    'ports': ['9121:9121'],
                    'networks': ['caain-network']
                }
            },
            'volumes': {
                'prometheus_data': {},
                'grafana_data': {}
            },
            'networks': {
                'caain-network': {
                    'external': True
                }
            }
        }
        
        # Write monitoring Docker Compose
        monitoring_compose_path = self.service_path / "docker-compose.monitoring.yml"
        with open(monitoring_compose_path, 'w') as f:
            yaml.dump(monitoring_compose, f, default_flow_style=False)
        
        print("✅ Monitoring Docker Compose configured")
        return True
    
    def setup_alertmanager_config(self) -> bool:
        """Set up Alertmanager configuration."""
        print("🚨 Setting up Alertmanager configuration...")
        
        alertmanager_config = {
            'global': {
                'smtp_smarthost': 'localhost:587',
                'smtp_from': 'alerts@caain-soil-hub.ca'
            },
            'route': {
                'group_by': ['alertname'],
                'group_wait': '10s',
                'group_interval': '10s',
                'repeat_interval': '1h',
                'receiver': 'web.hook'
            },
            'receivers': [
                {
                    'name': 'web.hook',
                    'webhook_configs': [
                        {
                            'url': 'http://localhost:5001/'
                        }
                    ]
                }
            ]
        }
        
        # Write Alertmanager configuration
        alertmanager_config_path = self.service_path / "alertmanager.yml"
        with open(alertmanager_config_path, 'w') as f:
            yaml.dump(alertmanager_config, f, default_flow_style=False)
        
        print("✅ Alertmanager configuration created")
        return True
    
    def setup_monitoring(self) -> bool:
        """Set up complete monitoring infrastructure."""
        print("🔧 Setting up comprehensive monitoring infrastructure...")
        print("=" * 60)
        
        setup_functions = [
            self.setup_prometheus_config,
            self.setup_alert_rules,
            self.setup_grafana_dashboards,
            self.setup_health_checks,
            self.setup_logging_config,
            self.setup_monitoring_docker_compose,
            self.setup_alertmanager_config
        ]
        
        success_count = 0
        for setup_func in setup_functions:
            try:
                if setup_func():
                    success_count += 1
            except Exception as e:
                print(f"❌ Error in {setup_func.__name__}: {e}")
        
        print("\n" + "=" * 60)
        print("📊 MONITORING SETUP SUMMARY")
        print("=" * 60)
        print(f"Successfully configured: {success_count}/{len(setup_functions)} components")
        
        if success_count == len(setup_functions):
            print("✅ All monitoring components configured successfully!")
            print("\n🚀 Next steps:")
            print("  1. Start monitoring stack: docker-compose -f docker-compose.monitoring.yml up -d")
            print("  2. Access Grafana: http://localhost:3000 (admin/admin)")
            print("  3. Access Prometheus: http://localhost:9090")
            print("  4. Configure alerting webhooks and email notifications")
            return True
        else:
            print("❌ Some monitoring components failed to configure")
            return False


def main():
    """Main monitoring setup function."""
    setup = MonitoringSetup()
    success = setup.setup_monitoring()
    
    if not success:
        print("\n❌ Monitoring setup failed!")
        sys.exit(1)
    else:
        print("\n✅ Monitoring setup completed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
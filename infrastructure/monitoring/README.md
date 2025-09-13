# AFAS Monitoring Infrastructure

This directory contains the complete monitoring and logging infrastructure for the Autonomous Farm Advisory System (AFAS). The monitoring stack is designed specifically for agricultural systems with focus on recommendation accuracy, data quality, and farmer impact metrics.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AFAS Services │───▶│   Prometheus    │───▶│    Grafana      │
│                 │    │   (Metrics)     │    │  (Dashboards)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Log Files     │───▶│      Loki       │───▶│   Log Queries   │
│  (Structured)   │    │ (Log Aggregation)│    │   & Alerts      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   Promtail      │    │  Alertmanager   │
│ (Log Collection)│    │ (Notifications) │
└─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### 1. Setup Monitoring Stack

```bash
cd infrastructure/monitoring
./setup-monitoring.sh
```

This will:
- Start Prometheus, Grafana, Loki, and Alertmanager
- Configure database exporters
- Set up log collection
- Create monitoring dashboards

### 2. Integrate with Services

```bash
# Add metrics to all AFAS services
./integrate-monitoring.py

# Restart services to enable metrics
cd ../../
./start-all.sh
```

### 3. Access Monitoring

- **Grafana Dashboards**: http://localhost:3001 (admin / afas_admin_2024)
- **Prometheus Metrics**: http://localhost:9090
- **Alertmanager**: http://localhost:9093
- **Loki Logs**: http://localhost:3100

## 📊 Key Dashboards

### 1. AFAS Overview Dashboard
- System health and performance
- Agricultural recommendation metrics
- Question classification accuracy
- Data freshness indicators

### 2. Agricultural Metrics Dashboard
- Farmer engagement metrics
- Recommendation confidence by question type
- Expert validation success rates
- Business impact measurements

## 🔍 Monitoring Components

### Prometheus (Metrics Collection)
- **Port**: 9090
- **Purpose**: Collects metrics from all AFAS services
- **Retention**: 30 days
- **Config**: `prometheus.yml`

**Key Metrics Collected**:
- HTTP request metrics (response time, status codes)
- Agricultural recommendation metrics (confidence, accuracy)
- Question classification metrics
- Database performance metrics
- External API reliability metrics

### Grafana (Visualization)
- **Port**: 3001
- **Purpose**: Visualizes metrics and creates dashboards
- **Login**: admin / afas_admin_2024
- **Dashboards**: Auto-provisioned from `grafana/dashboards/`

**Pre-configured Dashboards**:
- AFAS System Overview
- Agricultural Metrics & Business Intelligence
- Database Performance
- External API Monitoring

### Loki (Log Aggregation)
- **Port**: 3100
- **Purpose**: Aggregates and indexes log data
- **Retention**: 7 days (configurable)
- **Config**: `loki-config.yml`

**Log Types Collected**:
- Application logs (structured JSON)
- Agricultural decision logs
- Error logs
- Performance metrics logs
- User interaction logs

### Alertmanager (Notifications)
- **Port**: 9093
- **Purpose**: Handles alert routing and notifications
- **Config**: `alertmanager.yml`

**Alert Categories**:
- Critical agricultural accuracy issues
- Performance degradation
- Data quality problems
- Business metric anomalies

## 🌾 Agricultural-Specific Monitoring

### Agricultural Decision Tracking
```python
from shared.utils.logging_config import log_agricultural_decision

log_agricultural_decision(
    decision_type="crop_selection",
    input_data={"soil_ph": 6.2, "region": "midwest"},
    output_data={"primary_recommendation": "corn", "confidence_score": 0.87},
    confidence_score=0.87,
    processing_time=1.2,
    agricultural_sources=["Iowa State Extension"],
    expert_validated=True
)
```

### Performance Metrics
```python
from shared.utils.metrics import MetricsCollector

collector = MetricsCollector("recommendation-engine")
collector.record_recommendation_generated(
    question_type="fertilizer_rate",
    confidence_score=0.92,
    processing_time=2.1,
    region="midwest"
)
```

### Data Quality Monitoring
```python
from shared.utils.logging_config import log_data_quality_issue

log_data_quality_issue(
    data_source="weather_api",
    issue_type="stale_data",
    issue_description="Weather data is 6 hours old",
    severity="warning",
    affected_recommendations=15
)
```

## 🚨 Alert Configuration

### Critical Agricultural Alerts
- **Low Recommendation Confidence**: < 70% confidence
- **Question Classification Failure**: < 85% accuracy
- **Stale Agricultural Data**: > 24 hours old
- **System Down During Critical Season**: Any core service failure

### Performance Alerts
- **Slow Recommendations**: > 3 seconds response time
- **High Error Rate**: > 5% error rate
- **Database Issues**: Connection failures or slow queries

### Business Alerts
- **Low User Engagement**: < 10 questions/hour
- **Poor Recommendation Acceptance**: < 60% acceptance rate
- **Data Quality Issues**: External API failures

## 📈 Key Performance Indicators (KPIs)

### Technical KPIs
- **Response Time**: < 3 seconds for recommendations
- **Uptime**: > 99.5%
- **Error Rate**: < 1%
- **Data Freshness**: < 1 hour for critical data

### Agricultural KPIs
- **Recommendation Confidence**: > 80% average
- **Question Classification Accuracy**: > 90%
- **Expert Validation Rate**: > 95%
- **Data Source Reliability**: > 98%

### Business KPIs
- **User Engagement**: Questions per user per session
- **Recommendation Acceptance**: % of recommendations accepted
- **Return User Rate**: % of users returning within 30 days
- **Cost Savings**: Estimated farmer cost savings

## 🔧 Configuration

### Environment Variables
```bash
# Monitoring configuration
PROMETHEUS_RETENTION_DAYS=30
GRAFANA_ADMIN_PASSWORD=afas_admin_2024
LOKI_RETENTION_HOURS=168
ALERTMANAGER_SMTP_HOST=localhost:587

# Service-specific monitoring
ENABLE_METRICS=true
LOG_LEVEL=INFO
METRICS_PORT=8080
```

### Service Integration
Each AFAS service should include:

```python
# In main.py
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from shared.utils.metrics import MetricsCollector
from shared.utils.logging_config import setup_logging

# Initialize monitoring
metrics_collector = MetricsCollector("service-name")
setup_logging("service-name")

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
```

## 🛠️ Maintenance

### Log Rotation
Logs are automatically rotated:
- **Application logs**: 50MB max, 10 backups
- **Error logs**: 10MB max, 5 backups
- **Agricultural logs**: 100MB max, 20 backups

### Data Retention
- **Prometheus metrics**: 30 days
- **Loki logs**: 7 days
- **Grafana dashboards**: Persistent

### Backup
```bash
# Backup Grafana dashboards
docker exec afas-grafana grafana-cli admin export-dashboard > backup-dashboards.json

# Backup Prometheus data
docker exec afas-prometheus tar -czf /tmp/prometheus-backup.tar.gz /prometheus
docker cp afas-prometheus:/tmp/prometheus-backup.tar.gz ./backups/
```

## 🐛 Troubleshooting

### Common Issues

#### Services Not Appearing in Prometheus
1. Check service `/metrics` endpoint: `curl http://localhost:8000/metrics`
2. Verify Prometheus config: `docker logs afas-prometheus`
3. Check network connectivity between containers

#### Grafana Dashboards Not Loading
1. Check Grafana logs: `docker logs afas-grafana`
2. Verify dashboard provisioning: `docker exec afas-grafana ls /etc/grafana/provisioning/dashboards`
3. Check datasource configuration

#### Alerts Not Firing
1. Check Alertmanager config: `docker logs afas-alertmanager`
2. Verify alert rules: http://localhost:9090/alerts
3. Test notification channels

#### Logs Not Appearing in Loki
1. Check Promtail logs: `docker logs afas-promtail`
2. Verify log file permissions: `ls -la ../../logs/`
3. Check Loki ingestion: `curl http://localhost:3100/metrics`

### Performance Tuning

#### High Memory Usage
```yaml
# In docker-compose.monitoring.yml
services:
  prometheus:
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

#### Slow Queries
```yaml
# Increase query timeout
query_range:
  max_concurrent: 20
  timeout: 300s
```

## 📚 Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Loki Documentation](https://grafana.com/docs/loki/)
- [Agricultural Monitoring Best Practices](./docs/agricultural-monitoring-guide.md)

## 🤝 Contributing

When adding new metrics or dashboards:

1. Follow agricultural naming conventions
2. Include confidence scores for agricultural decisions
3. Add appropriate alerts for critical metrics
4. Document business impact in dashboard descriptions
5. Test with real agricultural data

## 📞 Support

For monitoring issues:
- Check logs: `docker-compose -f docker-compose.monitoring.yml logs`
- Restart stack: `docker-compose -f docker-compose.monitoring.yml restart`
- Reset data: `docker-compose -f docker-compose.monitoring.yml down -v`
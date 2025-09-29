# Comprehensive Monitoring and Analytics System

## Overview

This document describes the comprehensive monitoring and analytics infrastructure implemented for TICKET-005_crop-variety-recommendations-15.2. The system provides real-time monitoring, analytics, alerting, and reporting capabilities for the variety recommendations service.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Variety Recommendations Service              │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Application   │  │   Performance   │  │   Business      │ │
│  │   Monitoring    │  │   Monitoring    │  │   Analytics     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   User          │  │   Recommendation│  │   System        │ │
│  │   Engagement    │  │   Effectiveness │  │   Health        │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Monitoring Infrastructure                    │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Prometheus    │  │     Grafana     │  │  Alertmanager    │ │
│  │   (Metrics)     │  │  (Dashboards)   │  │   (Alerts)       │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Reporting System                             │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Daily         │  │   Weekly        │  │   Monthly        │ │
│  │   Reports       │  │   Reports       │  │   Reports        │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Comprehensive Monitoring Analytics Service

**File**: `src/services/comprehensive_monitoring_analytics_service.py`

**Features**:
- Real-time system health monitoring
- User engagement analytics
- Recommendation effectiveness metrics
- Business metrics and KPIs
- Automated alerting system
- Performance threshold monitoring

**Key Metrics**:
- System Health: CPU, memory, response time, error rate
- User Engagement: active users, satisfaction, session duration
- Recommendation Effectiveness: confidence scores, success rates, cache hit rates
- Business Metrics: revenue impact, cost savings, environmental impact

### 2. Prometheus Metrics Collector

**File**: `src/services/prometheus_metrics_collector.py`

**Features**:
- Prometheus-compatible metrics collection
- Agricultural-specific metrics
- Real-time metrics export
- Context managers for request timing
- Decorators for automatic metrics collection

**Metrics Exported**:
- `variety_recommendations_cpu_percent`
- `variety_recommendations_memory_percent`
- `variety_recommendations_response_time_ms`
- `variety_recommendations_error_rate`
- `variety_recommendations_active_users`
- `variety_recommendations_user_satisfaction_score`
- `variety_recommendations_confidence_score`
- `variety_recommendations_revenue_impact`

### 3. Monitoring Integration Service

**File**: `src/services/monitoring_integration_service.py`

**Features**:
- Integration with Prometheus/Grafana infrastructure
- Real-time metrics synchronization
- Alert forwarding to Alertmanager
- Dashboard updates
- Infrastructure health checks

### 4. Comprehensive Reporting Service

**File**: `src/services/comprehensive_reporting_service.py`

**Features**:
- Automated report generation (daily, weekly, monthly, quarterly, yearly)
- Multiple output formats (JSON, HTML, PDF, CSV, Markdown)
- Executive summaries and insights
- Trend analysis and forecasting
- Agricultural impact assessment

## API Endpoints

### Monitoring Analytics

- `GET /api/v1/crop-taxonomy/monitoring/dashboard` - Real-time dashboard data
- `GET /api/v1/crop-taxonomy/monitoring/metrics-summary` - Metrics summary
- `GET /api/v1/crop-taxonomy/monitoring/alerts` - System alerts
- `POST /api/v1/crop-taxonomy/monitoring/alerts/{alert_id}/resolve` - Resolve alerts
- `GET /api/v1/crop-taxonomy/monitoring/export` - Export metrics
- `POST /api/v1/crop-taxonomy/monitoring/start` - Start monitoring
- `POST /api/v1/crop-taxonomy/monitoring/stop` - Stop monitoring
- `GET /api/v1/crop-taxonomy/monitoring/health` - Health check

### Reporting

- `POST /api/v1/crop-taxonomy/reports/generate` - Generate reports
- `GET /api/v1/crop-taxonomy/reports/list` - List reports
- `GET /api/v1/crop-taxonomy/reports/{report_id}` - Get report details
- `GET /api/v1/crop-taxonomy/reports/{report_id}/download` - Download report
- `DELETE /api/v1/crop-taxonomy/reports/{report_id}` - Delete report
- `POST /api/v1/crop-taxonomy/reports/schedule` - Schedule reports
- `GET /api/v1/crop-taxonomy/reports/schedules` - List schedules
- `DELETE /api/v1/crop-taxonomy/reports/schedules/{schedule_id}` - Delete schedule
- `GET /api/v1/crop-taxonomy/reports/health` - Health check

### Monitoring Integration

- `POST /api/v1/crop-taxonomy/monitoring-integration/start` - Start integration
- `POST /api/v1/crop-taxonomy/monitoring-integration/stop` - Stop integration
- `GET /api/v1/crop-taxonomy/monitoring-integration/status` - Integration status
- `GET /api/v1/crop-taxonomy/monitoring-integration/test` - Test connectivity
- `POST /api/v1/crop-taxonomy/monitoring-integration/setup` - Setup infrastructure
- `POST /api/v1/crop-taxonomy/monitoring-integration/sync-metrics` - Sync metrics
- `POST /api/v1/crop-taxonomy/monitoring-integration/sync-alerts` - Sync alerts
- `GET /api/v1/crop-taxonomy/monitoring-integration/config` - Get configuration
- `PUT /api/v1/crop-taxonomy/monitoring-integration/config` - Update configuration
- `GET /api/v1/crop-taxonomy/monitoring-integration/health` - Health check

## Setup and Installation

### 1. Prerequisites

- Python 3.11+
- Prometheus (port 9090)
- Grafana (port 3001)
- Alertmanager (port 9093)
- Redis (port 6379)
- PostgreSQL database

### 2. Installation

```bash
# Navigate to the crop-taxonomy service directory
cd services/crop-taxonomy

# Install dependencies
pip install -r requirements.txt

# Run the comprehensive monitoring setup
python setup_comprehensive_monitoring.py
```

### 3. Configuration

The monitoring system can be configured through environment variables:

```bash
# Database configuration
export DATABASE_URL="postgresql://user:password@localhost:5432/crop_taxonomy"

# Redis configuration
export REDIS_URL="redis://localhost:6379"

# Monitoring infrastructure
export PROMETHEUS_URL="http://localhost:9090"
export GRAFANA_URL="http://localhost:3001"
export ALERTMANAGER_URL="http://localhost:9093"
export GRAFANA_API_KEY="your_grafana_api_key"
```

### 4. Starting the Service

```bash
# Start the crop-taxonomy service with monitoring
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

## Usage

### Starting Monitoring

```bash
# Start comprehensive monitoring
curl -X POST "http://localhost:8000/api/v1/crop-taxonomy/monitoring/start"

# Start monitoring integration
curl -X POST "http://localhost:8000/api/v1/crop-taxonomy/monitoring-integration/start"
```

### Viewing Dashboard

```bash
# Get real-time dashboard data
curl "http://localhost:8000/api/v1/crop-taxonomy/monitoring/dashboard"
```

### Generating Reports

```bash
# Generate daily report
curl -X POST "http://localhost:8000/api/v1/crop-taxonomy/reports/generate?report_type=daily&format=json"

# Generate weekly HTML report
curl -X POST "http://localhost:8000/api/v1/crop-taxonomy/reports/generate?report_type=weekly&format=html"
```

### Managing Alerts

```bash
# Get active alerts
curl "http://localhost:8000/api/v1/crop-taxonomy/monitoring/alerts"

# Resolve an alert
curl -X POST "http://localhost:8000/api/v1/crop-taxonomy/monitoring/alerts/{alert_id}/resolve"
```

## Monitoring Dashboards

### Grafana Dashboards

The system includes pre-configured Grafana dashboards:

1. **Variety Recommendations Monitoring** (`variety_recommendations_monitoring.json`)
   - System resource usage (CPU, memory, disk)
   - Performance metrics (response time, error rate)
   - User engagement metrics
   - Recommendation effectiveness
   - Business impact metrics
   - System alerts

### Access Points

- **Grafana**: http://localhost:3001 (admin / afas_admin_2024)
- **Prometheus**: http://localhost:9090
- **Alertmanager**: http://localhost:9093

## Alerting

### Alert Rules

The system includes comprehensive alert rules for:

- **System Health**: High CPU/memory usage, slow response times
- **Performance**: High error rates, slow response times
- **User Experience**: Low user satisfaction, low engagement
- **Recommendation Quality**: Low confidence scores, high failure rates
- **Business Metrics**: Revenue impact, cost savings

### Alert Levels

- **Critical**: System down, high error rates, critical performance issues
- **Warning**: Performance degradation, low satisfaction scores
- **Info**: General notifications, status updates

### Alert Channels

- Email notifications
- Webhook integrations
- Slack notifications (configurable)
- Custom webhook endpoints

## Reporting

### Report Types

1. **Daily Reports**
   - System health summary
   - User engagement metrics
   - Recommendation effectiveness
   - Business metrics
   - Active alerts

2. **Weekly Reports**
   - All daily report content
   - Trend analysis
   - Agricultural impact assessment
   - Performance trends

3. **Monthly Reports**
   - Comprehensive analysis
   - Executive summary
   - Competitive analysis
   - Future outlook
   - Strategic recommendations

4. **Quarterly Reports**
   - Strategic analysis
   - Business intelligence
   - Market analysis
   - Technology roadmap

5. **Yearly Reports**
   - Annual achievements
   - Long-term trends
   - Strategic planning
   - Future initiatives

### Report Formats

- **JSON**: Machine-readable format for integration
- **HTML**: Web-friendly format with charts and styling
- **PDF**: Professional format for presentations
- **CSV**: Data format for analysis
- **Markdown**: Documentation format

## Performance Targets

### Response Time Requirements

- Simple queries: < 1 second
- Complex recommendations: < 3 seconds
- Image analysis: < 10 seconds
- Bulk processing: < 30 seconds

### Reliability Requirements

- System uptime: >99.5%
- Data freshness: <1 hour for critical data
- Error rate: <1%
- Agricultural accuracy: >80% confidence

### Monitoring Thresholds

- CPU usage warning: 80%
- CPU usage critical: 95%
- Memory usage warning: 85%
- Memory usage critical: 95%
- Response time warning: 2 seconds
- Response time critical: 5 seconds
- Error rate warning: 5%
- Error rate critical: 10%

## Agricultural-Specific Features

### Decision Audit Trail

Every agricultural recommendation is logged with:
- Input parameters (sanitized for privacy)
- Output recommendations and confidence scores
- Processing time and data sources used
- Expert validation status
- Agricultural reasoning and sources

### Farmer Impact Tracking

- Cost savings estimates
- Fertilizer reduction percentages
- Environmental impact scores
- Recommendation acceptance rates

### Seasonal Awareness

- Higher alert sensitivity during planting/harvest seasons
- Seasonal rate limiting for API calls
- Critical period system availability monitoring

## Security and Privacy

### Data Protection

- Farm location data rounded to protect exact coordinates
- Personal information excluded from logs
- User IDs hashed for privacy
- Secure authentication for Grafana access

### Alert Security

- Agricultural expert notifications for critical issues
- Secure email and Slack integration
- Alert suppression to prevent spam
- Escalation procedures for critical periods

## Troubleshooting

### Common Issues

1. **Monitoring Not Starting**
   - Check database connectivity
   - Verify Redis connection
   - Check service dependencies

2. **Metrics Not Appearing**
   - Verify Prometheus configuration
   - Check metrics endpoint accessibility
   - Review service logs

3. **Alerts Not Firing**
   - Check Alertmanager configuration
   - Verify alert rules
   - Test webhook endpoints

4. **Reports Not Generating**
   - Check report directory permissions
   - Verify data availability
   - Review service logs

### Health Checks

```bash
# Check monitoring service health
curl "http://localhost:8000/api/v1/crop-taxonomy/monitoring/health"

# Check integration health
curl "http://localhost:8000/api/v1/crop-taxonomy/monitoring-integration/health"

# Check reporting service health
curl "http://localhost:8000/api/v1/crop-taxonomy/reports/health"
```

### Logs

Monitor logs for troubleshooting:

```bash
# Application logs
tail -f logs/application.log

# Error logs
tail -f logs/error.log

# Monitoring logs
tail -f logs/monitoring.log
```

## Maintenance

### Regular Maintenance Tasks

1. **Daily**
   - Review alert notifications
   - Check system health metrics
   - Monitor user engagement

2. **Weekly**
   - Review performance trends
   - Analyze recommendation effectiveness
   - Update monitoring thresholds

3. **Monthly**
   - Generate comprehensive reports
   - Review and update alert rules
   - Performance optimization

4. **Quarterly**
   - Strategic analysis and planning
   - Infrastructure capacity planning
   - Technology roadmap updates

### Backup and Recovery

- Daily automated backups of metrics data
- Configuration backup procedures
- Disaster recovery testing
- Data retention policies

## Future Enhancements

### Planned Features

1. **Advanced Analytics**
   - Machine learning for anomaly detection
   - Predictive analytics for system performance
   - Automated optimization recommendations

2. **Enhanced Reporting**
   - Interactive dashboards
   - Custom report builder
   - Automated report distribution

3. **Integration Improvements**
   - Additional monitoring tools integration
   - Cloud-native monitoring support
   - Advanced alerting capabilities

4. **Agricultural Enhancements**
   - Seasonal monitoring patterns
   - Crop-specific metrics
   - Regional performance analysis

## Support

For technical support and questions:

- **Documentation**: This document and API documentation
- **Logs**: Check application and monitoring logs
- **Health Checks**: Use provided health check endpoints
- **Community**: CAAIN Soil Hub development team

## Conclusion

The comprehensive monitoring and analytics system provides robust monitoring, alerting, and reporting capabilities for the variety recommendations service. It integrates seamlessly with existing Prometheus/Grafana infrastructure while adding agricultural-specific monitoring and analytics features.

The system is designed to be:
- **Comprehensive**: Covers all aspects of system monitoring
- **Real-time**: Provides immediate visibility into system health
- **Agricultural-focused**: Includes domain-specific metrics and insights
- **Scalable**: Can handle growing user base and data volume
- **Maintainable**: Easy to configure, monitor, and troubleshoot

This implementation fulfills all requirements for TICKET-005_crop-variety-recommendations-15.2 and provides a solid foundation for ongoing monitoring and analytics needs.
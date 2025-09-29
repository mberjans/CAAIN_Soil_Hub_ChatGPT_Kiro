# Comprehensive Monitoring and Alerting System for Crop Variety Recommendations

This document describes the comprehensive monitoring and alerting system implemented for the crop variety recommendations service. The system provides real-time monitoring, performance tracking, alerting, and analytics specifically designed for agricultural applications.

## 🎯 Overview

The monitoring system is designed to ensure:
- **Agricultural Accuracy**: Monitor recommendation quality and confidence scores
- **System Reliability**: Track system health, performance, and availability
- **User Experience**: Monitor user satisfaction and engagement metrics
- **Business Impact**: Track agricultural outcomes and farmer success rates
- **Data Quality**: Ensure external data sources are fresh and reliable

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AFAS Services │───▶│   Prometheus    │───▶│    Grafana      │
│                 │    │   (Metrics)     │    │  (Dashboards)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       │
         │              ┌─────────────────┐              │
         │              │  Alertmanager   │              │
         │              │   (Alerting)    │              │
         │              └─────────────────┘              │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      Redis      │    │   PostgreSQL    │    │      Loki       │
│   (Caching)     │    │   (Storage)     │    │   (Logging)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📊 Key Metrics Monitored

### Agricultural Metrics
- **Recommendation Confidence**: Quality scores for crop variety recommendations
- **User Satisfaction**: Farmer feedback and satisfaction ratings
- **Agricultural Success Rate**: Actual outcomes and yield improvements
- **Recommendation Accuracy**: Success rate of recommendations in practice

### Performance Metrics
- **Response Time**: P50, P95, P99 response times for recommendations
- **Throughput**: Number of recommendations generated per minute
- **Error Rate**: Percentage of failed recommendation requests
- **System Resources**: CPU, memory, disk usage

### Data Quality Metrics
- **Data Freshness**: Age of external data sources (weather, soil, market)
- **API Availability**: External service uptime and reliability
- **Data Validation**: Success rate of data validation processes

### Business Metrics
- **Recommendation Volume**: Number of recommendations per hour/day
- **User Engagement**: Active users and session duration
- **Cost Savings**: Estimated farmer cost savings from recommendations

## 🚨 Alerting Rules

### Critical Alerts (Immediate Response)
- Recommendation confidence < 70%
- System down during critical agricultural seasons
- Database connection failures
- Stale agricultural data > 48 hours
- High error rate > 10%

### Warning Alerts (30-minute Response)
- Recommendation confidence < 80%
- Response time > 2 seconds
- External API failure rate > 5%
- Low user satisfaction < 80%
- System resource usage > 80%

### Info Alerts (Monitoring Only)
- Data quality issues
- Performance degradation trends
- Business metric anomalies

## 🛠️ Setup and Installation

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- Redis (optional but recommended)
- PostgreSQL (optional but recommended)

### Quick Start

1. **Clone and Navigate**
   ```bash
   cd services/crop-taxonomy
   ```

2. **Set Environment Variables**
   ```bash
   export DATABASE_URL="postgresql://user:pass@localhost:5432/crop_variety_monitoring"
   export REDIS_URL="redis://localhost:6379"
   export MONITORING_WEBHOOK_URL="http://your-webhook-endpoint"
   export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
   ```

3. **Start Monitoring Stack**
   ```bash
   docker-compose -f docker-compose.monitoring.yml up -d
   ```

4. **Initialize Monitoring Service**
   ```bash
   python setup_monitoring.py
   ```

5. **Access Dashboards**
   - Grafana: http://localhost:3000 (admin/admin123)
   - Prometheus: http://localhost:9090
   - Alertmanager: http://localhost:9093

### Manual Setup

1. **Install Dependencies**
   ```bash
   pip install prometheus-client redis psutil aiohttp
   ```

2. **Initialize Services**
   ```python
   from services.comprehensive_monitoring_alerting_service import get_monitoring_service
   from services.monitoring_integration_service import get_monitoring_integration_service
   
   async def setup():
       monitoring_service = await get_monitoring_service()
       integration_service = await get_monitoring_integration_service()
       
       await integration_service.initialize()
       await monitoring_service.start_monitoring()
   ```

## 📈 Dashboards

### Crop Variety Monitoring Dashboard
- **Location**: Grafana → Dashboards → Crop Variety Recommendations Monitoring
- **Key Panels**:
  - Recommendation rate by crop type
  - P95 response time trends
  - System resource usage
  - User satisfaction scores
  - Agricultural success rates
  - Active alerts

### System Health Dashboard
- **Location**: Grafana → Dashboards → System Health
- **Key Panels**:
  - CPU, memory, disk usage
  - Active connections
  - Error rates
  - Service availability

### Agricultural Metrics Dashboard
- **Location**: Grafana → Dashboards → Agricultural Metrics
- **Key Panels**:
  - Recommendation confidence trends
  - User satisfaction by region
  - Agricultural outcome tracking
  - Data freshness monitoring

## 🔧 Configuration

### Monitoring Service Configuration

```python
# Customize thresholds
thresholds = {
    "response_time_warning_ms": 2000.0,
    "response_time_critical_ms": 5000.0,
    "recommendation_confidence_warning": 0.80,
    "recommendation_confidence_critical": 0.70,
    "user_satisfaction_warning": 0.80,
    "user_satisfaction_critical": 0.70,
    "agricultural_success_rate_warning": 0.75,
    "agricultural_success_rate_critical": 0.65,
}
```

### Alert Channel Configuration

```python
# Add custom alert channels
monitoring_service.add_alert_channel("webhook", "https://your-webhook.com/alerts")
monitoring_service.add_alert_channel("slack", "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK")
monitoring_service.add_alert_channel("email", "alerts@yourcompany.com")
```

## 🔌 API Integration

### Monitoring Endpoints

```bash
# Health check
GET /api/v1/monitoring/health

# Metrics summary
GET /api/v1/monitoring/metrics/summary

# Prometheus metrics
GET /api/v1/monitoring/metrics/prometheus

# Active alerts
GET /api/v1/monitoring/alerts

# Performance summary
GET /api/v1/monitoring/performance

# Dashboard data
GET /api/v1/monitoring/dashboard
```

### Recording User Feedback

```bash
POST /api/v1/monitoring/feedback
{
  "request_id": "req-123",
  "satisfaction_score": 0.85,
  "feedback_text": "Great recommendations!",
  "crop_type": "corn",
  "region": "midwest"
}
```

### Recording Agricultural Outcomes

```bash
POST /api/v1/monitoring/outcomes
{
  "request_id": "req-123",
  "outcome": "success",
  "yield_improvement": 15.5,
  "cost_savings": 250.0,
  "crop_type": "corn",
  "region": "midwest"
}
```

## 🧪 Testing

### Unit Tests
```bash
python -m pytest tests/test_monitoring_service.py -v
```

### Integration Tests
```bash
python -m pytest tests/test_monitoring_integration.py -v
```

### Load Testing
```bash
python tests/load_test_monitoring.py
```

## 📋 Monitoring Checklist

### Daily Checks
- [ ] Review active alerts in Grafana
- [ ] Check system resource usage
- [ ] Verify data freshness
- [ ] Monitor recommendation confidence scores

### Weekly Checks
- [ ] Review performance trends
- [ ] Analyze user satisfaction trends
- [ ] Check agricultural outcome metrics
- [ ] Review alert effectiveness

### Monthly Checks
- [ ] Update alert thresholds based on trends
- [ ] Review and optimize dashboard layouts
- [ ] Analyze cost savings and ROI
- [ ] Update runbooks and documentation

## 🚀 Advanced Features

### Custom Metrics
```python
# Add custom agricultural metrics
from prometheus_client import Counter, Histogram

yield_improvement = Histogram('agricultural_yield_improvement_percent', 
                             'Yield improvement from recommendations',
                             ['crop_type', 'region'])

cost_savings = Counter('agricultural_cost_savings_total',
                      'Total cost savings from recommendations',
                      ['crop_type', 'region'])
```

### Machine Learning Integration
```python
# Predict recommendation success
from sklearn.ensemble import RandomForestClassifier

class RecommendationSuccessPredictor:
    def predict_success(self, features):
        # Predict likelihood of agricultural success
        return self.model.predict_proba(features)
```

### Automated Scaling
```python
# Auto-scale based on metrics
class AutoScaler:
    async def check_scaling_conditions(self):
        cpu_usage = await self.get_cpu_usage()
        if cpu_usage > 80:
            await self.scale_up()
```

## 🔍 Troubleshooting

### Common Issues

1. **Prometheus Not Scraping Metrics**
   - Check service is running on correct port
   - Verify metrics endpoint is accessible
   - Check Prometheus configuration

2. **Alerts Not Firing**
   - Verify alert rules are loaded
   - Check Alertmanager configuration
   - Test alert channels manually

3. **High Memory Usage**
   - Check metrics retention settings
   - Review alert rule complexity
   - Optimize query performance

4. **Missing Agricultural Metrics**
   - Verify monitoring integration is active
   - Check service initialization
   - Review API endpoint configuration

### Debug Commands

```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Test alert rules
curl http://localhost:9090/api/v1/rules

# Check Alertmanager status
curl http://localhost:9093/api/v1/status

# View recent alerts
curl http://localhost:9093/api/v1/alerts
```

## 📚 Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Alertmanager Documentation](https://prometheus.io/docs/alerting/latest/alertmanager/)
- [Agricultural Monitoring Best Practices](https://docs.afas.com/monitoring/agricultural-best-practices)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit a pull request

## 📄 License

This monitoring system is part of the AFAS (Autonomous Farm Advisory System) project and follows the same licensing terms.

---

For questions or support, contact the monitoring team at monitoring@afas.local or create an issue in the repository.
# CAAIN Soil Hub - Administrator Guide

## Table of Contents
1. [System Overview](#system-overview)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Monitoring](#monitoring)
5. [Maintenance](#maintenance)
6. [Security](#security)
7. [Troubleshooting](#troubleshooting)

## System Overview

### Architecture
The CAAIN Soil Hub Crop Taxonomy Service is built as a microservice architecture with the following components:

- **FastAPI Application**: Main service application
- **PostgreSQL Database**: Primary data storage
- **Redis Cache**: Caching layer for performance
- **Nginx**: Reverse proxy and load balancer
- **Monitoring Stack**: Prometheus, Grafana, Alertmanager

### Service Dependencies
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose
- Nginx (for production)

## Installation

### Prerequisites
```bash
# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Production Installation

1. **Clone Repository**
```bash
git clone https://github.com/caain-soil-hub/crop-taxonomy-service.git
cd crop-taxonomy-service
```

2. **Configure Environment**
```bash
cp .env.production .env
# Edit .env with production values
nano .env
```

3. **Deploy with Docker Compose**
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f crop-taxonomy
```

4. **Initialize Database**
```bash
# Run database migrations
docker-compose exec crop-taxonomy python -m alembic upgrade head

# Load initial data
docker-compose exec crop-taxonomy python scripts/load_initial_data.py
```

### Verification
```bash
# Check service health
curl http://localhost:8000/api/v1/health

# Check database connection
curl http://localhost:8000/api/v1/health/database

# Check Redis connection
curl http://localhost:8000/api/v1/health/redis
```

## Configuration

### Environment Variables

#### Core Settings
```bash
# Application
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
SECRET_KEY=your-super-secret-key

# Database
DATABASE_URL=postgresql://user:password@postgres:5432/crop_taxonomy
POSTGRES_USER=caain_user
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=crop_taxonomy

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_PASSWORD=redis_password
```

#### Security Settings
```bash
# CORS
CORS_ORIGINS=["https://caain-soil-hub.ca"]
ALLOWED_HOSTS=["caain-soil-hub.ca"]

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_BURST=100
```

#### External Services
```bash
# API Keys
USDA_API_KEY=your-usda-api-key
WEATHER_API_KEY=your-weather-api-key
SOIL_DATA_API_KEY=your-soil-data-api-key
```

### Nginx Configuration

#### SSL/TLS Setup
```bash
# Generate SSL certificates (Let's Encrypt)
sudo certbot --nginx -d caain-soil-hub.ca

# Or use custom certificates
cp your-cert.pem /etc/nginx/ssl/cert.pem
cp your-key.pem /etc/nginx/ssl/key.pem
```

#### Security Headers
```nginx
# Add to nginx.conf
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=63072000" always;
```

### Database Configuration

#### Performance Tuning
```sql
-- PostgreSQL configuration optimizations
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
SELECT pg_reload_conf();
```

#### Index Optimization
```bash
# Apply performance indexes
docker-compose exec crop-taxonomy python scripts/apply_performance_optimizations.py
```

## Monitoring

### Prometheus Metrics
The service exposes metrics at `/metrics` endpoint:

- **HTTP Metrics**: Request rate, response time, error rate
- **Database Metrics**: Connection pool, query performance
- **Cache Metrics**: Hit rate, memory usage
- **Business Metrics**: Recommendation accuracy, user engagement

### Grafana Dashboards
Access Grafana at `http://localhost:3000` (admin/admin):

1. **Service Overview**: Overall health and performance
2. **Database Performance**: Query times, connections
3. **Cache Performance**: Hit rates, memory usage
4. **Business Metrics**: Agricultural data quality

### Alerting Rules
Configured alerts include:

- Service down
- High error rate (>10%)
- High response time (>5s)
- Database connection failures
- High CPU/Memory usage
- Disk space low

### Health Checks
```bash
# Service health
curl http://localhost:8000/api/v1/health

# Database health
curl http://localhost:8000/api/v1/health/database

# Redis health
curl http://localhost:8000/api/v1/health/redis

# External APIs health
curl http://localhost:8000/api/v1/health/external
```

## Maintenance

### Regular Tasks

#### Daily
- Monitor service health and performance
- Check error logs for issues
- Verify backup completion

#### Weekly
- Review performance metrics
- Update security patches
- Clean up old log files

#### Monthly
- Database maintenance and optimization
- Security audit
- Capacity planning review

### Backup Procedures

#### Database Backup
```bash
# Automated daily backup (configured in cron)
docker-compose exec postgres pg_dump -U caain_user crop_taxonomy > backup_$(date +%Y%m%d).sql

# Restore from backup
docker-compose exec -T postgres psql -U caain_user crop_taxonomy < backup_20240101.sql
```

#### Configuration Backup
```bash
# Backup configuration files
tar -czf config_backup_$(date +%Y%m%d).tar.gz \
  docker-compose.yml \
  nginx.conf \
  .env \
  prometheus.yml \
  alert_rules.yml
```

### Updates and Deployments

#### Rolling Updates
```bash
# Update service
docker-compose pull crop-taxonomy
docker-compose up -d crop-taxonomy

# Verify update
docker-compose ps
curl http://localhost:8000/api/v1/health
```

#### Database Migrations
```bash
# Run migrations
docker-compose exec crop-taxonomy python -m alembic upgrade head

# Rollback if needed
docker-compose exec crop-taxonomy python -m alembic downgrade -1
```

### Log Management

#### Log Rotation
```bash
# Configure logrotate
sudo nano /etc/logrotate.d/caain-soil-hub

# Log rotation configuration
/var/log/caain-soil-hub/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        docker-compose restart crop-taxonomy
    endscript
}
```

#### Log Analysis
```bash
# View recent errors
docker-compose logs --tail=100 crop-taxonomy | grep ERROR

# Monitor logs in real-time
docker-compose logs -f crop-taxonomy

# Search logs
docker-compose logs crop-taxonomy | grep "specific_error"
```

## Security

### Security Hardening

#### Container Security
```bash
# Run security audit
docker-compose exec crop-taxonomy python security-audit.py

# Update base images
docker-compose pull
docker-compose up -d
```

#### Network Security
```bash
# Configure firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

#### Access Control
```bash
# Restrict database access
# Edit postgresql.conf
listen_addresses = 'localhost'

# Edit pg_hba.conf
host    crop_taxonomy    caain_user    127.0.0.1/32    md5
```

### Security Monitoring

#### Vulnerability Scanning
```bash
# Scan Docker images
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image caain-soil-hub/crop-taxonomy:latest

# Scan dependencies
docker-compose exec crop-taxonomy safety check
```

#### Intrusion Detection
```bash
# Monitor failed login attempts
grep "Failed password" /var/log/auth.log

# Monitor suspicious network activity
netstat -tuln | grep LISTEN
```

### Incident Response

#### Security Incident Checklist
1. **Identify**: Determine scope and impact
2. **Contain**: Isolate affected systems
3. **Eradicate**: Remove threats and vulnerabilities
4. **Recover**: Restore normal operations
5. **Learn**: Document lessons learned

#### Emergency Procedures
```bash
# Emergency shutdown
docker-compose down

# Emergency restore
docker-compose down
docker-compose up -d postgres
# Restore database from backup
docker-compose up -d
```

## Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check logs
docker-compose logs crop-taxonomy

# Check configuration
docker-compose config

# Check resources
docker stats
```

#### Database Connection Issues
```bash
# Test database connectivity
docker-compose exec crop-taxonomy python -c "
import psycopg2
conn = psycopg2.connect('postgresql://caain_user:secure_password@postgres:5432/crop_taxonomy')
print('Database connection successful')
"

# Check database status
docker-compose exec postgres pg_isready -U caain_user
```

#### Performance Issues
```bash
# Check resource usage
docker stats

# Check database performance
docker-compose exec postgres psql -U caain_user -d crop_taxonomy -c "
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
"

# Check cache performance
docker-compose exec redis redis-cli info stats
```

#### Memory Issues
```bash
# Check memory usage
free -h
docker stats --no-stream

# Clear Redis cache if needed
docker-compose exec redis redis-cli FLUSHALL
```

### Debugging Tools

#### Service Debugging
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
docker-compose restart crop-taxonomy

# Access service shell
docker-compose exec crop-taxonomy bash

# Check service configuration
docker-compose exec crop-taxonomy python -c "
from src.config import get_settings
print(get_settings())
"
```

#### Database Debugging
```bash
# Access database
docker-compose exec postgres psql -U caain_user crop_taxonomy

# Check slow queries
docker-compose exec postgres psql -U caain_user crop_taxonomy -c "
SELECT query, mean_time, calls 
FROM pg_stat_statements 
WHERE mean_time > 1000;
"
```

### Recovery Procedures

#### Service Recovery
```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart crop-taxonomy

# Rebuild service
docker-compose build crop-taxonomy
docker-compose up -d crop-taxonomy
```

#### Data Recovery
```bash
# Restore from backup
docker-compose exec -T postgres psql -U caain_user crop_taxonomy < backup.sql

# Rebuild indexes
docker-compose exec crop-taxonomy python scripts/rebuild_indexes.py
```

### Support Contacts

#### Internal Support
- **System Administrator**: admin@caain-soil-hub.ca
- **Database Administrator**: dba@caain-soil-hub.ca
- **Security Team**: security@caain-soil-hub.ca

#### External Support
- **Docker Support**: https://docs.docker.com/support/
- **PostgreSQL Support**: https://www.postgresql.org/support/
- **Redis Support**: https://redis.io/support/

---

**Version**: 1.0.0  
**Last Updated**: January 2024  
**License**: Agricultural Research License
# Deployment Guide - Crop Variety Recommendations

## Overview

This guide covers deployment strategies, environments, and operational procedures for the crop variety recommendations system. It includes production deployment, staging environments, monitoring, and maintenance procedures.

## Deployment Architecture

### 1. Environment Strategy

```
┌─────────────────────────────────────────────────────────────────┐
│                        Production                                │
│                    (High Availability)                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │   Load      │  │   App        │  │   Database  │  │  Cache  │ │
│  │ Balancer    │  │  Servers     │  │  Cluster    │  │ Cluster │ │
│  │   (HA)      │  │   (3+)       │  │   (HA)      │  │  (HA)   │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Staging                                 │
│                    (Pre-Production)                              │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │   Load      │  │   App        │  │   Database  │  │  Cache  │ │
│  │ Balancer    │  │  Servers     │  │   (HA)      │  │ Cluster │ │
│  │             │  │   (2)        │  │             │  │         │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Development                                 │
│                    (Local/CI)                                    │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │   Docker    │  │   App        │  │   Database  │  │  Cache  │ │
│  │ Compose     │  │ Container    │  │ Container   │  │Container│ │
│  │             │  │              │  │             │  │         │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Infrastructure Components

| Component | Production | Staging | Development |
|-----------|------------|---------|-------------|
| **Application Servers** | 3+ instances | 2 instances | 1 instance |
| **Database** | PostgreSQL HA Cluster | PostgreSQL HA | PostgreSQL Single |
| **Cache** | Redis Cluster | Redis Cluster | Redis Single |
| **Load Balancer** | HAProxy/Nginx HA | HAProxy | Nginx |
| **Monitoring** | Prometheus + Grafana | Prometheus + Grafana | Local tools |
| **Logging** | ELK Stack | ELK Stack | Local files |

## Environment Configuration

### 1. Environment Variables

**Production (.env.production):**
```bash
# Application Configuration
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8001

# Database Configuration
DATABASE_URL=postgresql://prod_user:secure_password@db-cluster.internal:5432/variety_recommendations_prod
DB_HOST=db-cluster.internal
DB_PORT=5432
DB_NAME=variety_recommendations_prod
DB_USER=prod_user
DB_PASSWORD=secure_password
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30

# Redis Configuration
REDIS_URL=redis://redis-cluster.internal:6379
REDIS_HOST=redis-cluster.internal
REDIS_PORT=6379
REDIS_PASSWORD=redis_secure_password
REDIS_DB=0
REDIS_POOL_SIZE=20

# External Services
CLIMATE_SERVICE_URL=https://climate-service.internal:8003
SOIL_SERVICE_URL=https://soil-service.internal:8004
MARKET_SERVICE_URL=https://market-service.internal:8005

# Security
SECRET_KEY=production_secret_key_here
JWT_SECRET_KEY=jwt_production_secret
API_KEY_ENCRYPTION_KEY=api_key_encryption_key_here

# CORS Configuration
CORS_ORIGINS=https://app.caain-soil-hub.com,https://admin.caain-soil-hub.com

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_BURST=200

# Monitoring
PROMETHEUS_ENABLED=True
PROMETHEUS_PORT=9090
HEALTH_CHECK_INTERVAL=30

# External APIs
USDA_API_KEY=production_usda_api_key
WEATHER_API_KEY=production_weather_api_key
MARKET_DATA_API_KEY=production_market_api_key
```

**Staging (.env.staging):**
```bash
# Application Configuration
ENVIRONMENT=staging
DEBUG=False
LOG_LEVEL=DEBUG
API_HOST=0.0.0.0
API_PORT=8001

# Database Configuration
DATABASE_URL=postgresql://staging_user:staging_password@staging-db.internal:5432/variety_recommendations_staging
DB_HOST=staging-db.internal
DB_PORT=5432
DB_NAME=variety_recommendations_staging
DB_USER=staging_user
DB_PASSWORD=staging_password

# Redis Configuration
REDIS_URL=redis://staging-redis.internal:6379
REDIS_HOST=staging-redis.internal
REDIS_PORT=6379
REDIS_PASSWORD=staging_redis_password

# External Services
CLIMATE_SERVICE_URL=http://staging-climate-service.internal:8003
SOIL_SERVICE_URL=http://staging-soil-service.internal:8004
MARKET_SERVICE_URL=http://staging-market-service.internal:8005

# Security
SECRET_KEY=staging_secret_key_here
JWT_SECRET_KEY=jwt_staging_secret
API_KEY_ENCRYPTION_KEY=staging_api_key_encryption_key

# CORS Configuration
CORS_ORIGINS=https://staging-app.caain-soil-hub.com

# Rate Limiting
RATE_LIMIT_PER_MINUTE=1000
RATE_LIMIT_BURST=2000

# External APIs (staging keys)
USDA_API_KEY=staging_usda_api_key
WEATHER_API_KEY=staging_weather_api_key
MARKET_DATA_API_KEY=staging_market_api_key
```

### 2. Docker Configuration

**Dockerfile:**
```dockerfile
# Multi-stage build for production optimization
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Run application
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

**docker-compose.yml (Development):**
```yaml
version: '3.8'

services:
  variety-recommendations:
    build: .
    ports:
      - "8001:8001"
    environment:
      - ENVIRONMENT=development
      - DATABASE_URL=postgresql://variety_dev:password@db:5432/variety_recommendations_dev
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - .:/app
      - /app/__pycache__
    command: python -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=variety_recommendations_dev
      - POSTGRES_USER=variety_dev
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## Kubernetes Deployment

### 1. Namespace and ConfigMap

**namespace.yaml:**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: variety-recommendations
  labels:
    name: variety-recommendations
```

**configmap.yaml:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: variety-recommendations-config
  namespace: variety-recommendations
data:
  ENVIRONMENT: "production"
  DEBUG: "False"
  LOG_LEVEL: "INFO"
  API_HOST: "0.0.0.0"
  API_PORT: "8001"
  DB_POOL_SIZE: "20"
  DB_MAX_OVERFLOW: "30"
  REDIS_POOL_SIZE: "20"
  RATE_LIMIT_PER_MINUTE: "100"
  RATE_LIMIT_BURST: "200"
  PROMETHEUS_ENABLED: "True"
  PROMETHEUS_PORT: "9090"
```

**secret.yaml:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: variety-recommendations-secrets
  namespace: variety-recommendations
type: Opaque
data:
  DATABASE_URL: <base64-encoded-database-url>
  REDIS_URL: <base64-encoded-redis-url>
  SECRET_KEY: <base64-encoded-secret-key>
  JWT_SECRET_KEY: <base64-encoded-jwt-secret>
  API_KEY_ENCRYPTION_KEY: <base64-encoded-api-key-encryption-key>
  USDA_API_KEY: <base64-encoded-usda-api-key>
  WEATHER_API_KEY: <base64-encoded-weather-api-key>
  MARKET_DATA_API_KEY: <base64-encoded-market-api-key>
```

### 2. Deployment Configuration

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: variety-recommendations
  namespace: variety-recommendations
  labels:
    app: variety-recommendations
spec:
  replicas: 3
  selector:
    matchLabels:
      app: variety-recommendations
  template:
    metadata:
      labels:
        app: variety-recommendations
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "9090"
        prometheus.io/path: "/metrics"
    spec:
      containers:
      - name: variety-recommendations
        image: variety-recommendations:latest
        ports:
        - containerPort: 8001
          name: http
        - containerPort: 9090
          name: metrics
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: variety-recommendations-secrets
              key: DATABASE_URL
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: variety-recommendations-secrets
              key: REDIS_URL
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: variety-recommendations-secrets
              key: SECRET_KEY
        envFrom:
        - configMapRef:
            name: variety-recommendations-config
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8001
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        startupProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 10
      imagePullSecrets:
      - name: registry-secret
```

**service.yaml:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: variety-recommendations-service
  namespace: variety-recommendations
  labels:
    app: variety-recommendations
spec:
  selector:
    app: variety-recommendations
  ports:
  - name: http
    port: 80
    targetPort: 8001
    protocol: TCP
  - name: metrics
    port: 9090
    targetPort: 9090
    protocol: TCP
  type: ClusterIP
```

**ingress.yaml:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: variety-recommendations-ingress
  namespace: variety-recommendations
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.caain-soil-hub.com
    secretName: variety-recommendations-tls
  rules:
  - host: api.caain-soil-hub.com
    http:
      paths:
      - path: /api/v1/varieties
        pathType: Prefix
        backend:
          service:
            name: variety-recommendations-service
            port:
              number: 80
```

### 3. Horizontal Pod Autoscaler

**hpa.yaml:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: variety-recommendations-hpa
  namespace: variety-recommendations
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: variety-recommendations
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
      - type: Pods
        value: 2
        periodSeconds: 60
      selectPolicy: Max
```

## Database Deployment

### 1. PostgreSQL High Availability

**postgresql-ha.yaml:**
```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: variety-recommendations-db
  namespace: variety-recommendations
spec:
  instances: 3
  
  postgresql:
    parameters:
      max_connections: "200"
      shared_buffers: "256MB"
      effective_cache_size: "1GB"
      work_mem: "4MB"
      maintenance_work_mem: "64MB"
      checkpoint_completion_target: "0.9"
      wal_buffers: "16MB"
      default_statistics_target: "100"
      random_page_cost: "1.1"
      effective_io_concurrency: "200"
      max_worker_processes: "8"
      max_parallel_workers_per_gather: "4"
      max_parallel_workers: "8"
      max_parallel_maintenance_workers: "4"
  
  bootstrap:
    initdb:
      database: variety_recommendations_prod
      owner: variety_user
      secret:
        name: variety-recommendations-db-credentials
  
  storage:
    size: 100Gi
    storageClass: fast-ssd
  
  monitoring:
    enabled: true
  
  backup:
    barmanObjectStore:
      destinationPath: "s3://variety-recommendations-backups"
      s3Credentials:
        accessKeyId:
          name: backup-credentials
          key: ACCESS_KEY_ID
        secretAccessKey:
          name: backup-credentials
          key: SECRET_ACCESS_KEY
      wal:
        retention: "7d"
      data:
        retention: "30d"
```

### 2. Database Migrations

**migration-job.yaml:**
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: variety-recommendations-migration
  namespace: variety-recommendations
spec:
  template:
    spec:
      containers:
      - name: migration
        image: variety-recommendations:latest
        command: ["python", "-m", "alembic", "upgrade", "head"]
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: variety-recommendations-secrets
              key: DATABASE_URL
      restartPolicy: Never
  backoffLimit: 3
```

## Redis Deployment

### 1. Redis Cluster

**redis-cluster.yaml:**
```yaml
apiVersion: redis.redis.opstreelabs.in/v1beta1
kind: RedisCluster
metadata:
  name: variety-recommendations-redis
  namespace: variety-recommendations
spec:
  clusterSize: 6
  clusterVersion: v7
  persistenceEnabled: true
  resources:
    requests:
      memory: "512Mi"
      cpu: "250m"
    limits:
      memory: "1Gi"
      cpu: "500m"
  storage:
    volumeClaimTemplate:
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 10Gi
        storageClassName: fast-ssd
  redisExporter:
    enabled: true
    image: oliver006/redis_exporter:latest
    port: 9121
```

## Monitoring and Observability

### 1. Prometheus Configuration

**prometheus-config.yaml:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: variety-recommendations
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
    
    rule_files:
      - "variety_recommendations_rules.yml"
    
    scrape_configs:
      - job_name: 'variety-recommendations'
        static_configs:
          - targets: ['variety-recommendations-service:9090']
        scrape_interval: 10s
        metrics_path: /metrics
      
      - job_name: 'postgresql'
        static_configs:
          - targets: ['postgres-exporter:9187']
      
      - job_name: 'redis'
        static_configs:
          - targets: ['redis-exporter:9121']
      
      - job_name: 'kubernetes-pods'
        kubernetes_sd_configs:
          - role: pod
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
            action: keep
            regex: true
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
            action: replace
            target_label: __metrics_path__
            regex: (.+)
```

### 2. Grafana Dashboards

**grafana-dashboard.yaml:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: variety-recommendations-dashboard
  namespace: variety-recommendations
data:
  dashboard.json: |
    {
      "dashboard": {
        "title": "Variety Recommendations Service",
        "panels": [
          {
            "title": "Request Rate",
            "type": "graph",
            "targets": [
              {
                "expr": "rate(http_requests_total[5m])",
                "legendFormat": "{{method}} {{endpoint}}"
              }
            ]
          },
          {
            "title": "Response Time",
            "type": "graph",
            "targets": [
              {
                "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
                "legendFormat": "95th percentile"
              }
            ]
          },
          {
            "title": "Error Rate",
            "type": "graph",
            "targets": [
              {
                "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
                "legendFormat": "5xx errors"
              }
            ]
          },
          {
            "title": "Database Connections",
            "type": "graph",
            "targets": [
              {
                "expr": "pg_stat_database_numbackends",
                "legendFormat": "Active connections"
              }
            ]
          },
          {
            "title": "Redis Memory Usage",
            "type": "graph",
            "targets": [
              {
                "expr": "redis_memory_used_bytes",
                "legendFormat": "Memory used"
              }
            ]
          }
        ]
      }
    }
```

## CI/CD Pipeline

### 1. GitHub Actions Workflow

**.github/workflows/deploy.yml:**
```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]
  workflow_dispatch:

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}/variety-recommendations

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov
    
    - name: Run tests
      run: pytest tests/ -v --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v3
    
    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=sha,prefix={{branch}}-
          type=raw,value=latest,enable={{is_default_branch}}
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}

  deploy-staging:
    needs: build-and-push
    runs-on: ubuntu-latest
    environment: staging
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v3
    
    - name: Configure kubectl
      uses: azure/k8s-set-context@v3
      with:
        method: kubeconfig
        kubeconfig: ${{ secrets.KUBE_CONFIG_STAGING }}
    
    - name: Deploy to staging
      run: |
        kubectl set image deployment/variety-recommendations \
          variety-recommendations=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} \
          -n variety-recommendations-staging
        kubectl rollout status deployment/variety-recommendations -n variety-recommendations-staging

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v3
    
    - name: Configure kubectl
      uses: azure/k8s-set-context@v3
      with:
        method: kubeconfig
        kubeconfig: ${{ secrets.KUBE_CONFIG_PRODUCTION }}
    
    - name: Deploy to production
      run: |
        kubectl set image deployment/variety-recommendations \
          variety-recommendations=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} \
          -n variety-recommendations
        kubectl rollout status deployment/variety-recommendations -n variety-recommendations
    
    - name: Run smoke tests
      run: |
        kubectl run smoke-test --image=curlimages/curl:latest \
          --rm -i --restart=Never -- \
          curl -f http://variety-recommendations-service/api/v1/varieties/health
```

### 2. Deployment Scripts

**scripts/deploy.sh:**
```bash
#!/bin/bash
set -e

# Configuration
NAMESPACE=${1:-variety-recommendations}
ENVIRONMENT=${2:-staging}
IMAGE_TAG=${3:-latest}

echo "Deploying to $ENVIRONMENT environment..."

# Validate environment
if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    echo "Error: Environment must be 'staging' or 'production'"
    exit 1
fi

# Set namespace based on environment
if [[ "$ENVIRONMENT" == "staging" ]]; then
    NAMESPACE="variety-recommendations-staging"
fi

# Check if kubectl is configured
if ! kubectl cluster-info > /dev/null 2>&1; then
    echo "Error: kubectl is not configured or cluster is not accessible"
    exit 1
fi

# Create namespace if it doesn't exist
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Apply configurations
echo "Applying configurations..."
kubectl apply -f k8s/configmap.yaml -n $NAMESPACE
kubectl apply -f k8s/secret.yaml -n $NAMESPACE

# Run database migrations
echo "Running database migrations..."
kubectl apply -f k8s/migration-job.yaml -n $NAMESPACE
kubectl wait --for=condition=complete job/variety-recommendations-migration -n $NAMESPACE --timeout=300s

# Deploy application
echo "Deploying application..."
kubectl set image deployment/variety-recommendations \
    variety-recommendations=variety-recommendations:$IMAGE_TAG \
    -n $NAMESPACE

# Wait for rollout to complete
echo "Waiting for rollout to complete..."
kubectl rollout status deployment/variety-recommendations -n $NAMESPACE --timeout=600s

# Run health checks
echo "Running health checks..."
kubectl run health-check --image=curlimages/curl:latest \
    --rm -i --restart=Never -n $NAMESPACE -- \
    curl -f http://variety-recommendations-service/health

echo "Deployment completed successfully!"
```

## Backup and Recovery

### 1. Database Backup

**backup-job.yaml:**
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: variety-recommendations-backup
  namespace: variety-recommendations
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:13
            command:
            - /bin/bash
            - -c
            - |
              pg_dump $DATABASE_URL > /backup/variety_recommendations_$(date +%Y%m%d_%H%M%S).sql
              gzip /backup/variety_recommendations_$(date +%Y%m%d_%H%M%S).sql
              aws s3 cp /backup/variety_recommendations_$(date +%Y%m%d_%H%M%S).sql.gz s3://variety-recommendations-backups/
            env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: variety-recommendations-secrets
                  key: DATABASE_URL
            - name: AWS_ACCESS_KEY_ID
              valueFrom:
                secretKeyRef:
                  name: backup-credentials
                  key: ACCESS_KEY_ID
            - name: AWS_SECRET_ACCESS_KEY
              valueFrom:
                secretKeyRef:
                  name: backup-credentials
                  key: SECRET_ACCESS_KEY
            volumeMounts:
            - name: backup-storage
              mountPath: /backup
          volumes:
          - name: backup-storage
            emptyDir: {}
          restartPolicy: OnFailure
```

### 2. Disaster Recovery Plan

**disaster-recovery.md:**
```markdown
# Disaster Recovery Plan

## Recovery Time Objectives (RTO)
- Critical Services: 4 hours
- Full System: 8 hours

## Recovery Point Objectives (RPO)
- Data Loss: 1 hour maximum

## Recovery Procedures

### 1. Database Recovery
1. Restore from latest backup
2. Apply transaction logs if available
3. Verify data integrity
4. Update connection strings

### 2. Application Recovery
1. Deploy from latest image
2. Restore configuration
3. Verify service health
4. Update DNS/load balancer

### 3. Cache Recovery
1. Clear Redis cache
2. Warm cache with critical data
3. Monitor cache hit rates

## Testing Procedures
- Monthly disaster recovery drills
- Quarterly full system recovery tests
- Annual business continuity review
```

## Security Considerations

### 1. Network Security

**network-policies.yaml:**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: variety-recommendations-netpol
  namespace: variety-recommendations
spec:
  podSelector:
    matchLabels:
      app: variety-recommendations
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8001
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: variety-recommendations
    ports:
    - protocol: TCP
      port: 5432  # PostgreSQL
    - protocol: TCP
      port: 6379  # Redis
  - to: []
    ports:
    - protocol: TCP
      port: 443   # HTTPS
    - protocol: TCP
      port: 80    # HTTP
```

### 2. Pod Security

**pod-security-policy.yaml:**
```yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: variety-recommendations-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
```

## Performance Optimization

### 1. Resource Optimization

**resource-limits.yaml:**
```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: variety-recommendations-limits
  namespace: variety-recommendations
spec:
  limits:
  - default:
      memory: "1Gi"
      cpu: "500m"
    defaultRequest:
      memory: "512Mi"
      cpu: "250m"
    type: Container
```

### 2. Monitoring and Alerting

**alerts.yaml:**
```yaml
groups:
- name: variety-recommendations
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value }} errors per second"
  
  - alert: HighResponseTime
    expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High response time detected"
      description: "95th percentile response time is {{ $value }} seconds"
  
  - alert: DatabaseConnectionHigh
    expr: pg_stat_database_numbackends > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High database connection count"
      description: "Database has {{ $value }} active connections"
```

## Maintenance Procedures

### 1. Rolling Updates

```bash
# Update application with zero downtime
kubectl set image deployment/variety-recommendations \
  variety-recommendations=variety-recommendations:v1.2.0 \
  -n variety-recommendations

# Monitor rollout
kubectl rollout status deployment/variety-recommendations -n variety-recommendations

# Rollback if needed
kubectl rollout undo deployment/variety-recommendations -n variety-recommendations
```

### 2. Database Maintenance

```bash
# Run database maintenance
kubectl exec -it deployment/variety-recommendations-db -n variety-recommendations -- \
  psql -U variety_user -d variety_recommendations_prod -c "VACUUM ANALYZE;"

# Check database size
kubectl exec -it deployment/variety-recommendations-db -n variety-recommendations -- \
  psql -U variety_user -d variety_recommendations_prod -c \
  "SELECT pg_size_pretty(pg_database_size('variety_recommendations_prod'));"
```

### 3. Cache Maintenance

```bash
# Clear Redis cache
kubectl exec -it deployment/variety-recommendations-redis -n variety-recommendations -- \
  redis-cli FLUSHDB

# Check Redis memory usage
kubectl exec -it deployment/variety-recommendations-redis -n variety-recommendations -- \
  redis-cli INFO memory
```

## Troubleshooting

### Common Deployment Issues

1. **Pod Startup Failures**
   ```bash
   # Check pod logs
   kubectl logs deployment/variety-recommendations -n variety-recommendations
   
   # Check pod events
   kubectl describe pod -l app=variety-recommendations -n variety-recommendations
   ```

2. **Database Connection Issues**
   ```bash
   # Test database connectivity
   kubectl run db-test --image=postgres:13 --rm -it --restart=Never -- \
     psql $DATABASE_URL -c "SELECT 1;"
   ```

3. **Redis Connection Issues**
   ```bash
   # Test Redis connectivity
   kubectl run redis-test --image=redis:6 --rm -it --restart=Never -- \
     redis-cli -h variety-recommendations-redis ping
   ```

4. **Performance Issues**
   ```bash
   # Check resource usage
   kubectl top pods -n variety-recommendations
   
   # Check HPA status
   kubectl get hpa -n variety-recommendations
   ```

This comprehensive deployment guide ensures reliable, scalable, and maintainable deployment of the crop variety recommendations system across all environments.
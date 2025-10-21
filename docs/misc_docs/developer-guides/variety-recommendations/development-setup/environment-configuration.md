# Environment Configuration Guide

## Overview

This guide covers environment configuration for the crop variety recommendations system, including development, staging, and production environments.

## Environment Types

### 1. Development Environment

**Purpose**: Local development and testing
**Database**: Local PostgreSQL instance
**Cache**: Local Redis instance
**External Services**: Mock services or development APIs

**Configuration**:
```bash
# .env.development
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=DEBUG
API_HOST=0.0.0.0
API_PORT=8001

# Database
DATABASE_URL=postgresql://variety_dev:password@localhost:5432/variety_recommendations_dev
DB_HOST=localhost
DB_PORT=5432
DB_NAME=variety_recommendations_dev
DB_USER=variety_dev
DB_PASSWORD=password

# Redis
REDIS_URL=redis://localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379

# External Services (Development URLs)
CLIMATE_SERVICE_URL=http://localhost:8003
SOIL_SERVICE_URL=http://localhost:8004
MARKET_SERVICE_URL=http://localhost:8005

# Security (Development keys)
SECRET_KEY=dev_secret_key_here
JWT_SECRET_KEY=dev_jwt_secret
API_KEY_ENCRYPTION_KEY=dev_api_key_encryption_key

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Rate Limiting (Higher limits for development)
RATE_LIMIT_PER_MINUTE=1000
RATE_LIMIT_BURST=2000

# External APIs (Development keys)
USDA_API_KEY=dev_usda_api_key
WEATHER_API_KEY=dev_weather_api_key
MARKET_DATA_API_KEY=dev_market_api_key
```

### 2. Staging Environment

**Purpose**: Pre-production testing and validation
**Database**: Staging PostgreSQL cluster
**Cache**: Staging Redis cluster
**External Services**: Staging service instances

**Configuration**:
```bash
# .env.staging
ENVIRONMENT=staging
DEBUG=False
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8001

# Database
DATABASE_URL=postgresql://staging_user:staging_password@staging-db.internal:5432/variety_recommendations_staging
DB_HOST=staging-db.internal
DB_PORT=5432
DB_NAME=variety_recommendations_staging
DB_USER=staging_user
DB_PASSWORD=staging_password

# Redis
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
JWT_SECRET_KEY=staging_jwt_secret
API_KEY_ENCRYPTION_KEY=staging_api_key_encryption_key

# CORS
CORS_ORIGINS=https://staging-app.caain-soil-hub.com

# Rate Limiting
RATE_LIMIT_PER_MINUTE=500
RATE_LIMIT_BURST=1000

# External APIs (Staging keys)
USDA_API_KEY=staging_usda_api_key
WEATHER_API_KEY=staging_weather_api_key
MARKET_DATA_API_KEY=staging_market_api_key
```

### 3. Production Environment

**Purpose**: Live production system
**Database**: Production PostgreSQL HA cluster
**Cache**: Production Redis cluster
**External Services**: Production service instances

**Configuration**:
```bash
# .env.production
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=WARNING
API_HOST=0.0.0.0
API_PORT=8001

# Database
DATABASE_URL=postgresql://prod_user:secure_password@db-cluster.internal:5432/variety_recommendations_prod
DB_HOST=db-cluster.internal
DB_PORT=5432
DB_NAME=variety_recommendations_prod
DB_USER=prod_user
DB_PASSWORD=secure_password

# Redis
REDIS_URL=redis://redis-cluster.internal:6379
REDIS_HOST=redis-cluster.internal
REDIS_PORT=6379
REDIS_PASSWORD=redis_secure_password

# External Services
CLIMATE_SERVICE_URL=https://climate-service.internal:8003
SOIL_SERVICE_URL=https://soil-service.internal:8004
MARKET_SERVICE_URL=https://market-service.internal:8005

# Security
SECRET_KEY=production_secret_key_here
JWT_SECRET_KEY=jwt_production_secret
API_KEY_ENCRYPTION_KEY=api_key_encryption_key_here

# CORS
CORS_ORIGINS=https://app.caain-soil-hub.com,https://admin.caain-soil-hub.com

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_BURST=200

# External APIs (Production keys)
USDA_API_KEY=production_usda_api_key
WEATHER_API_KEY=production_weather_api_key
MARKET_DATA_API_KEY=production_market_api_key
```

## Configuration Management

### 1. Environment Variables

**Required Variables**:
- `ENVIRONMENT`: Environment type (development/staging/production)
- `DATABASE_URL`: Database connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: Application secret key
- `JWT_SECRET_KEY`: JWT signing key

**Optional Variables**:
- `DEBUG`: Enable debug mode
- `LOG_LEVEL`: Logging level
- `API_HOST`: API host address
- `API_PORT`: API port number
- `CORS_ORIGINS`: CORS allowed origins

### 2. Configuration Validation

```python
from pydantic import BaseSettings, validator
from typing import List, Optional

class Settings(BaseSettings):
    environment: str
    debug: bool = False
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8001
    
    # Database
    database_url: str
    db_host: str
    db_port: int = 5432
    db_name: str
    db_user: str
    db_password: str
    
    # Redis
    redis_url: str
    redis_host: str
    redis_port: int = 6379
    redis_password: Optional[str] = None
    
    # External Services
    climate_service_url: str
    soil_service_url: str
    market_service_url: str
    
    # Security
    secret_key: str
    jwt_secret_key: str
    api_key_encryption_key: str
    
    # CORS
    cors_origins: List[str] = []
    
    # Rate Limiting
    rate_limit_per_minute: int = 100
    rate_limit_burst: int = 200
    
    # External APIs
    usda_api_key: str
    weather_api_key: str
    market_data_api_key: str
    
    @validator('environment')
    def validate_environment(cls, v):
        if v not in ['development', 'staging', 'production']:
            raise ValueError('Environment must be development, staging, or production')
        return v
    
    @validator('log_level')
    def validate_log_level(cls, v):
        if v not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            raise ValueError('Invalid log level')
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Usage
settings = Settings()
```

### 3. Environment-Specific Settings

```python
class EnvironmentSettings:
    def __init__(self, environment: str):
        self.environment = environment
        self.settings = self._load_settings()
    
    def _load_settings(self) -> dict:
        """Load environment-specific settings."""
        base_settings = {
            'development': {
                'debug': True,
                'log_level': 'DEBUG',
                'rate_limit_per_minute': 1000,
                'cors_origins': ['http://localhost:3000', 'http://localhost:3001']
            },
            'staging': {
                'debug': False,
                'log_level': 'INFO',
                'rate_limit_per_minute': 500,
                'cors_origins': ['https://staging-app.caain-soil-hub.com']
            },
            'production': {
                'debug': False,
                'log_level': 'WARNING',
                'rate_limit_per_minute': 100,
                'cors_origins': ['https://app.caain-soil-hub.com', 'https://admin.caain-soil-hub.com']
            }
        }
        
        return base_settings.get(self.environment, base_settings['development'])
    
    def get_setting(self, key: str, default=None):
        """Get environment-specific setting."""
        return self.settings.get(key, default)
```

## Security Configuration

### 1. Secret Management

**Development**:
```bash
# Use simple environment variables
export SECRET_KEY="dev_secret_key_here"
export JWT_SECRET_KEY="dev_jwt_secret"
export API_KEY_ENCRYPTION_KEY="dev_api_key_encryption_key"
```

**Staging/Production**:
```bash
# Use secure secret management
# AWS Secrets Manager
aws secretsmanager get-secret-value --secret-id variety-recommendations/secrets

# HashiCorp Vault
vault kv get -field=secret_key variety-recommendations/secrets

# Kubernetes Secrets
kubectl create secret generic variety-recommendations-secrets \
  --from-literal=secret-key=production_secret_key_here \
  --from-literal=jwt-secret-key=jwt_production_secret \
  --from-literal=api-key-encryption-key=api_key_encryption_key_here
```

### 2. SSL/TLS Configuration

**Development**:
```python
# No SSL required for local development
ssl_context = None
```

**Staging/Production**:
```python
import ssl

# SSL context for HTTPS
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain('cert.pem', 'key.pem')
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
```

### 3. CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

def configure_cors(app, settings):
    """Configure CORS based on environment."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
```

## Database Configuration

### 1. Connection Pooling

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

def create_database_engine(database_url: str, environment: str):
    """Create database engine with environment-specific configuration."""
    pool_config = {
        'development': {
            'pool_size': 5,
            'max_overflow': 10,
            'pool_pre_ping': True,
            'pool_recycle': 3600
        },
        'staging': {
            'pool_size': 10,
            'max_overflow': 20,
            'pool_pre_ping': True,
            'pool_recycle': 3600
        },
        'production': {
            'pool_size': 20,
            'max_overflow': 30,
            'pool_pre_ping': True,
            'pool_recycle': 3600
        }
    }
    
    config = pool_config.get(environment, pool_config['development'])
    
    return create_engine(
        database_url,
        poolclass=QueuePool,
        **config
    )
```

### 2. Database URLs

**Development**:
```bash
DATABASE_URL=postgresql://variety_dev:password@localhost:5432/variety_recommendations_dev
```

**Staging**:
```bash
DATABASE_URL=postgresql://staging_user:staging_password@staging-db.internal:5432/variety_recommendations_staging
```

**Production**:
```bash
DATABASE_URL=postgresql://prod_user:secure_password@db-cluster.internal:5432/variety_recommendations_prod
```

## Redis Configuration

### 1. Connection Configuration

```python
import redis

def create_redis_client(redis_url: str, environment: str):
    """Create Redis client with environment-specific configuration."""
    config = {
        'development': {
            'decode_responses': True,
            'socket_connect_timeout': 5,
            'socket_timeout': 5,
            'retry_on_timeout': True
        },
        'staging': {
            'decode_responses': True,
            'socket_connect_timeout': 10,
            'socket_timeout': 10,
            'retry_on_timeout': True,
            'health_check_interval': 30
        },
        'production': {
            'decode_responses': True,
            'socket_connect_timeout': 10,
            'socket_timeout': 10,
            'retry_on_timeout': True,
            'health_check_interval': 30,
            'max_connections': 20
        }
    }
    
    client_config = config.get(environment, config['development'])
    
    return redis.from_url(redis_url, **client_config)
```

### 2. Redis URLs

**Development**:
```bash
REDIS_URL=redis://localhost:6379
```

**Staging**:
```bash
REDIS_URL=redis://staging-redis.internal:6379
```

**Production**:
```bash
REDIS_URL=redis://redis-cluster.internal:6379
```

## Logging Configuration

### 1. Environment-Specific Logging

```python
import logging
import sys
from pathlib import Path

def configure_logging(environment: str, log_level: str):
    """Configure logging based on environment."""
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging format
    if environment == 'development':
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        handlers = [
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_dir / "variety_service_dev.log")
        ]
    else:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d"
        handlers = [
            logging.FileHandler(log_dir / f"variety_service_{environment}.log"),
            logging.FileHandler(log_dir / "variety_service_error.log", level=logging.ERROR)
        ]
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=handlers
    )
    
    # Set specific loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
```

### 2. Structured Logging

```python
import structlog

def configure_structured_logging(environment: str):
    """Configure structured logging for production."""
    
    if environment == 'production':
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
```

## Monitoring Configuration

### 1. Metrics Configuration

```python
from prometheus_client import Counter, Histogram, Gauge

# Metrics
http_requests_total = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
http_request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
active_connections = Gauge('active_connections', 'Active database connections')
cache_hit_rate = Gauge('cache_hit_rate', 'Cache hit rate')

def configure_metrics(environment: str):
    """Configure metrics based on environment."""
    
    if environment == 'production':
        # Enable metrics endpoint
        from prometheus_client import start_http_server
        start_http_server(9090)
```

### 2. Health Checks

```python
from fastapi import FastAPI

def configure_health_checks(app: FastAPI, environment: str):
    """Configure health checks based on environment."""
    
    @app.get("/health")
    async def health_check():
        """Basic health check."""
        return {"status": "healthy", "environment": environment}
    
    @app.get("/ready")
    async def readiness_check():
        """Readiness check for Kubernetes."""
        # Check database connection
        # Check Redis connection
        # Check external services
        return {"status": "ready", "environment": environment}
    
    if environment == 'production':
        @app.get("/metrics")
        async def metrics():
            """Prometheus metrics endpoint."""
            from prometheus_client import generate_latest
            return Response(generate_latest(), media_type="text/plain")
```

## Deployment Configuration

### 1. Docker Configuration

**Development Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
```

**Production Dockerfile**:
```dockerfile
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim as production

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser

EXPOSE 8001
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### 2. Kubernetes Configuration

**ConfigMap**:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: variety-recommendations-config
data:
  ENVIRONMENT: "production"
  DEBUG: "False"
  LOG_LEVEL: "WARNING"
  API_HOST: "0.0.0.0"
  API_PORT: "8001"
```

**Secret**:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: variety-recommendations-secrets
type: Opaque
data:
  DATABASE_URL: <base64-encoded-database-url>
  REDIS_URL: <base64-encoded-redis-url>
  SECRET_KEY: <base64-encoded-secret-key>
  JWT_SECRET_KEY: <base64-encoded-jwt-secret>
  API_KEY_ENCRYPTION_KEY: <base64-encoded-api-key-encryption-key>
```

## Best Practices

### 1. Environment Separation

- Use separate configuration files for each environment
- Never commit production secrets to version control
- Use environment-specific database instances
- Implement proper secret management

### 2. Configuration Validation

- Validate all configuration values at startup
- Use type hints and Pydantic models
- Implement proper error handling
- Log configuration issues

### 3. Security

- Use strong, unique secrets for each environment
- Implement proper access controls
- Use HTTPS in staging and production
- Regular secret rotation

### 4. Monitoring

- Configure appropriate logging levels
- Implement health checks
- Set up metrics collection
- Monitor configuration changes

### 5. Maintenance

- Document all configuration options
- Version control configuration files
- Regular configuration audits
- Automated configuration validation
"""
Production Configuration for CAAIN Soil Hub Crop Taxonomy Service
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, validator


class ProductionSettings(BaseSettings):
    """Production configuration settings."""
    
    # Application
    environment: str = "production"
    debug: bool = False
    log_level: str = "INFO"
    secret_key: str
    
    # Database
    database_url: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    
    # Redis
    redis_url: str
    redis_password: Optional[str] = None
    
    # API
    api_v1_str: str = "/api/v1"
    project_name: str = "CAAIN Soil Hub - Crop Taxonomy Service"
    version: str = "1.0.0"
    
    # Security
    cors_origins: List[str] = []
    allowed_hosts: List[str] = []
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_burst: int = 100
    
    # Monitoring
    sentry_dsn: Optional[str] = None
    prometheus_enabled: bool = True
    prometheus_port: int = 9090
    
    # External Services
    usda_api_key: Optional[str] = None
    weather_api_key: Optional[str] = None
    soil_data_api_key: Optional[str] = None
    
    # File Storage
    upload_max_size: int = 10485760  # 10MB
    upload_allowed_extensions: List[str] = ["jpg", "jpeg", "png", "pdf", "csv"]
    
    # Cache
    cache_ttl_seconds: int = 3600
    cache_max_size: int = 1000
    
    # Agricultural Data
    agricultural_data_enabled: bool = True
    trial_data_enabled: bool = True
    market_data_enabled: bool = True
    
    # Performance
    max_workers: int = 4
    worker_timeout: int = 30
    keepalive_timeout: int = 5
    
    # Backup
    backup_enabled: bool = True
    backup_schedule: str = "0 2 * * *"
    backup_retention_days: int = 30
    
    # SSL/TLS
    ssl_enabled: bool = True
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None
    
    @validator('cors_origins', pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(',')]
        return v
    
    @validator('allowed_hosts', pre=True)
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(',')]
        return v
    
    @validator('upload_allowed_extensions', pre=True)
    def parse_upload_extensions(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(',')]
        return v
    
    class Config:
        env_file = ".env.production"
        case_sensitive = False


# Security configuration
class SecurityConfig:
    """Security-related configuration."""
    
    # Password requirements
    MIN_PASSWORD_LENGTH = 12
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_NUMBERS = True
    REQUIRE_SPECIAL_CHARS = True
    
    # Session security
    SESSION_TIMEOUT_MINUTES = 30
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15
    
    # API security
    API_KEY_LENGTH = 32
    JWT_EXPIRATION_HOURS = 24
    
    # File upload security
    MAX_FILE_SIZE_MB = 10
    SCAN_UPLOADS_FOR_MALWARE = True
    
    # Network security
    ENABLE_RATE_LIMITING = True
    ENABLE_DDOS_PROTECTION = True
    BLOCK_SUSPICIOUS_IPS = True


# Performance configuration
class PerformanceConfig:
    """Performance optimization settings."""
    
    # Database
    DB_POOL_SIZE = 20
    DB_MAX_OVERFLOW = 30
    DB_POOL_TIMEOUT = 30
    DB_POOL_RECYCLE = 3600
    
    # Redis
    REDIS_POOL_SIZE = 10
    REDIS_MAX_CONNECTIONS = 20
    
    # Caching
    CACHE_DEFAULT_TTL = 3600
    CACHE_MAX_ENTRIES = 10000
    
    # API
    API_TIMEOUT_SECONDS = 30
    MAX_CONCURRENT_REQUESTS = 100
    
    # File processing
    MAX_CONCURRENT_UPLOADS = 5
    CHUNK_SIZE_BYTES = 8192


# Monitoring configuration
class MonitoringConfig:
    """Monitoring and observability settings."""
    
    # Metrics
    METRICS_ENABLED = True
    METRICS_PORT = 9090
    METRICS_PATH = "/metrics"
    
    # Logging
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE_PATH = "/app/logs/app.log"
    LOG_MAX_SIZE_MB = 100
    LOG_BACKUP_COUNT = 5
    
    # Health checks
    HEALTH_CHECK_INTERVAL = 30
    HEALTH_CHECK_TIMEOUT = 10
    
    # Alerting
    ALERT_WEBHOOK_URL = None
    ALERT_THRESHOLDS = {
        "cpu_usage_percent": 80,
        "memory_usage_percent": 85,
        "disk_usage_percent": 90,
        "response_time_ms": 5000,
        "error_rate_percent": 5
    }


# Get production settings instance
def get_production_settings() -> ProductionSettings:
    """Get production settings instance."""
    return ProductionSettings()


# Export configurations
__all__ = [
    "ProductionSettings",
    "SecurityConfig", 
    "PerformanceConfig",
    "MonitoringConfig",
    "get_production_settings"
]
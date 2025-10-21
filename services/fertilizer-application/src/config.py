"""
Configuration settings for the Fertilizer Application Service.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Service configuration
    service_name: str = "fertilizer-application"
    version: str = "1.0.0"
    port: int = 8008
    
    # Database configuration
    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/afas")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # External service URLs
    crop_taxonomy_url: str = os.getenv("CROP_TAXONOMY_URL", "http://localhost:8003")
    soil_management_url: str = os.getenv("SOIL_MANAGEMENT_URL", "http://localhost:8004")
    economic_analysis_url: str = os.getenv("ECONOMIC_ANALYSIS_URL", "http://localhost:8005")
    weather_service_url: str = os.getenv("WEATHER_SERVICE_URL", "http://localhost:8006")
    
    # Fertilizer application specific settings
    default_application_rate_unit: str = "lbs/acre"
    default_cost_unit: str = "USD"
    max_field_size_acres: float = 10000.0
    min_field_size_acres: float = 0.1
    
    # Equipment assessment settings
    equipment_assessment_timeout: int = 30  # seconds
    cost_analysis_timeout: int = 45  # seconds
    
    # Logging configuration
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


# Global settings instance
settings = Settings()
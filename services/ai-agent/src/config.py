"""
Configuration management for AFAS AI Agent Service
"""

import os
from typing import Optional, List
from pydantic import BaseSettings, validator
import logging

logger = logging.getLogger(__name__)


class AIAgentConfig(BaseSettings):
    """Configuration for AI Agent Service."""
    
    # Service Configuration
    port: int = 8002
    debug: bool = False
    
    # OpenRouter Configuration
    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    
    # LLM Service Configuration
    max_conversation_length: int = 20
    context_window_tokens: int = 4000
    enable_streaming: bool = True
    cache_responses: bool = True
    cache_ttl_seconds: int = 3600
    
    # Model Configuration (optional overrides)
    explanation_model: Optional[str] = "anthropic/claude-3-sonnet"
    classification_model: Optional[str] = "openai/gpt-4-turbo"
    conversation_model: Optional[str] = "anthropic/claude-3-sonnet"
    bulk_model: Optional[str] = "openai/gpt-3.5-turbo"
    fallback_model: Optional[str] = "meta-llama/llama-3-8b-instruct"
    
    # Database Configuration
    database_url: Optional[str] = None
    redis_url: Optional[str] = "redis://localhost:6379/0"
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Security Configuration
    api_key_header: str = "X-API-Key"
    cors_origins: List[str] = ["*"]
    rate_limit_requests_per_minute: int = 100
    
    # Monitoring Configuration
    enable_metrics: bool = True
    metrics_port: int = 9090
    
    class Config:
        env_prefix = ""
        case_sensitive = False
        env_file = ".env"
    
    @validator('openrouter_api_key')
    def validate_openrouter_api_key(cls, v):
        if not v:
            raise ValueError('OpenRouter API key is required')
        if not v.startswith('sk-or-'):
            logger.warning('OpenRouter API key format appears invalid')
        return v
    
    @validator('log_level')
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of: {valid_levels}')
        return v.upper()
    
    @validator('cors_origins', pre=True)
    def validate_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v


def get_config() -> AIAgentConfig:
    """Get configuration from environment variables."""
    try:
        config = AIAgentConfig()
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, config.log_level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        
        logger.info("AI Agent configuration loaded successfully")
        return config
        
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise


# Global configuration instance
config = get_config()
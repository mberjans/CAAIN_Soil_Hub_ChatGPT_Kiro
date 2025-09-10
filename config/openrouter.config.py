"""
OpenRouter Configuration for AFAS Python Services

This configuration manages LLM integration through OpenRouter,
providing unified access to multiple LLM providers.
"""

import os
from typing import Dict, Optional
from pydantic import BaseSettings, validator
import logging

logger = logging.getLogger(__name__)


class OpenRouterConfig(BaseSettings):
    """OpenRouter configuration with validation and defaults."""
    
    # Base configuration
    api_key: str
    base_url: str = "https://openrouter.ai/api/v1"
    
    # Default model settings
    default_model: str = "anthropic/claude-3-sonnet"
    
    # Model preferences for different use cases
    explanation_model: str = "anthropic/claude-3-sonnet"
    classification_model: str = "openai/gpt-4-turbo"
    conversation_model: str = "anthropic/claude-3-sonnet"
    bulk_model: str = "openai/gpt-3.5-turbo"
    fallback_model: str = "meta-llama/llama-3-8b-instruct"
    
    # Request configuration
    timeout: int = 30
    max_retries: int = 3
    retry_delay: int = 1
    
    class Config:
        env_prefix = "OPENROUTER_"
        case_sensitive = False
        
    @validator('api_key')
    def validate_api_key(cls, v):
        if not v:
            raise ValueError('OpenRouter API key is required')
        if not v.startswith('sk-or-'):
            logger.warning('OpenRouter API key format appears invalid')
        return v
    
    @validator('base_url')
    def validate_base_url(cls, v):
        if not v.startswith('https://'):
            raise ValueError('Base URL must use HTTPS')
        return v


# Model configurations
MODEL_CONFIGS = {
    # Agricultural explanations - prioritize reasoning and accuracy
    "explanation": {
        "model": "anthropic/claude-3-sonnet",
        "temperature": 0.3,
        "max_tokens": 2000,
        "top_p": 0.9,
    },
    
    # Question classification - fast and accurate
    "classification": {
        "model": "openai/gpt-4-turbo",
        "temperature": 0.1,
        "max_tokens": 100,
        "top_p": 0.8,
    },
    
    # Conversational responses - balanced performance
    "conversation": {
        "model": "anthropic/claude-3-sonnet",
        "temperature": 0.4,
        "max_tokens": 1500,
        "top_p": 0.9,
    },
    
    # High-volume tasks - cost-effective
    "bulk": {
        "model": "openai/gpt-3.5-turbo",
        "temperature": 0.2,
        "max_tokens": 1000,
        "top_p": 0.8,
    },
    
    # Fallback model - reliable and available
    "fallback": {
        "model": "meta-llama/llama-3-8b-instruct",
        "temperature": 0.3,
        "max_tokens": 1500,
        "top_p": 0.9,
    }
}

# Rate limits (requests per minute)
RATE_LIMITS = {
    "anthropic/claude-3-sonnet": 50,
    "openai/gpt-4-turbo": 100,
    "openai/gpt-3.5-turbo": 200,
    "meta-llama/llama-3-8b-instruct": 150
}

# Cost tracking (approximate costs per 1K tokens)
COSTS = {
    "anthropic/claude-3-sonnet": {"input": 0.003, "output": 0.015},
    "openai/gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "openai/gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    "meta-llama/llama-3-8b-instruct": {"input": 0.0002, "output": 0.0002}
}

# Agricultural-specific prompt templates
PROMPTS = {
    "system_prompt": """You are an expert agricultural advisor with deep knowledge of farming practices, soil science, crop management, and sustainable agriculture.

Your responses should:
- Be accurate and based on scientific evidence
- Use clear, farmer-friendly language
- Include specific, actionable recommendations
- Consider regional variations and local conditions
- Emphasize safety and environmental responsibility
- Acknowledge uncertainty when appropriate

Always cite relevant agricultural sources and extension guidelines when making recommendations.""",
    
    "explanation_prompt": """Explain the following agricultural recommendation in clear, practical terms that a farmer can understand and implement:

Recommendation: {recommendation}
Context: {context}
Confidence: {confidence}

Provide:
1. Clear explanation of the recommendation
2. Why this recommendation is appropriate
3. Specific implementation steps
4. Potential risks or considerations
5. Expected outcomes and timeline""",
    
    "classification_prompt": """Classify the following farmer question into one of the 20 AFAS question categories:

Question: {question}

Categories:
1. Crop Selection
2. Soil Fertility
3. Crop Rotation
4. Nutrient Deficiency Detection
5. Fertilizer Type Selection
6. Fertilizer Application Method
7. Fertilizer Timing
8. Environmental Impact
9. Cover Crops
10. Soil pH Management
11. Micronutrients
12. Precision Agriculture ROI
13. Drought Management
14. Early Deficiency Detection
15. Tillage Practices
16. Cost-Effective Fertilizer Strategy
17. Weather Impact Analysis
18. Testing Integration
19. Sustainable Yield Optimization
20. Government Programs

Return only the category number and name."""
}


def get_openrouter_config() -> OpenRouterConfig:
    """Get validated OpenRouter configuration from environment variables."""
    try:
        config = OpenRouterConfig()
        logger.info("OpenRouter configuration loaded successfully")
        return config
    except Exception as e:
        logger.error(f"Failed to load OpenRouter configuration: {e}")
        raise


def get_model_config(use_case: str) -> Dict:
    """Get model configuration for specific use case."""
    if use_case not in MODEL_CONFIGS:
        logger.warning(f"Unknown use case '{use_case}', using default")
        use_case = "conversation"
    
    config = MODEL_CONFIGS[use_case].copy()
    
    # Override with environment-specific model if available
    openrouter_config = get_openrouter_config()
    model_attr = f"{use_case}_model"
    if hasattr(openrouter_config, model_attr):
        config["model"] = getattr(openrouter_config, model_attr)
    
    return config


def get_rate_limit(model: str) -> int:
    """Get rate limit for specific model."""
    return RATE_LIMITS.get(model, 50)  # Default to 50 requests per minute


def get_cost_estimate(model: str, input_tokens: int, output_tokens: int) -> float:
    """Estimate cost for model usage."""
    if model not in COSTS:
        return 0.0
    
    cost_config = COSTS[model]
    input_cost = (input_tokens / 1000) * cost_config["input"]
    output_cost = (output_tokens / 1000) * cost_config["output"]
    
    return input_cost + output_cost


# Initialize configuration on import
try:
    openrouter_config = get_openrouter_config()
except Exception as e:
    logger.error(f"Failed to initialize OpenRouter configuration: {e}")
    openrouter_config = None
#!/usr/bin/env python3
"""
Startup script for AFAS AI Agent Service with OpenRouter integration
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import uvicorn
from dotenv import load_dotenv

from src.config import get_config
from src.services.llm_service import create_llm_service

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


async def startup_checks():
    """Perform startup health checks."""
    try:
        config = get_config()
        
        # Check OpenRouter API key
        if not config.openrouter_api_key:
            logger.error("OPENROUTER_API_KEY not set!")
            return False
        
        if not config.openrouter_api_key.startswith('sk-or-'):
            logger.warning("OpenRouter API key format appears invalid")
        
        # Test LLM service initialization
        logger.info("Testing LLM service initialization...")
        llm_service = create_llm_service()
        
        # Test OpenRouter connectivity
        async with llm_service:
            health = await llm_service.get_service_health()
            
            if health["status"] != "healthy":
                logger.error(f"LLM service health check failed: {health}")
                return False
            
            logger.info("✅ OpenRouter connectivity verified")
            logger.info(f"✅ Available models: {health['openrouter_status'].get('available_models', 'Unknown')}")
        
        return True
        
    except Exception as e:
        logger.error(f"Startup checks failed: {e}")
        return False


def main():
    """Main startup function."""
    print("🌾 Starting AFAS AI Agent Service with OpenRouter Integration")
    print("=" * 60)
    
    # Load configuration
    try:
        config = get_config()
        logger.info(f"Configuration loaded successfully")
        logger.info(f"Service will run on port {config.port}")
        logger.info(f"Debug mode: {config.debug}")
        logger.info(f"Streaming enabled: {config.enable_streaming}")
        logger.info(f"Response caching: {config.cache_responses}")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)
    
    # Run startup checks
    print("\n🔍 Running startup checks...")
    try:
        checks_passed = asyncio.run(startup_checks())
        if not checks_passed:
            logger.error("Startup checks failed. Exiting.")
            sys.exit(1)
        print("✅ All startup checks passed")
    except KeyboardInterrupt:
        print("\n⏹️  Startup interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Startup checks failed: {e}")
        sys.exit(1)
    
    # Start the service
    print(f"\n🚀 Starting AI Agent Service on port {config.port}")
    print(f"📖 API Documentation: http://localhost:{config.port}/docs")
    print(f"🏥 Health Check: http://localhost:{config.port}/health")
    print("Press Ctrl+C to stop the service")
    
    try:
        uvicorn.run(
            "src.main:app",
            host="0.0.0.0",
            port=config.port,
            reload=config.debug,
            log_level="debug" if config.debug else "info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n⏹️  Service stopped by user")
    except Exception as e:
        logger.error(f"Service failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Startup script for the Fertilizer Application Service.
"""

import os
import sys
import uvicorn
import logging
from pathlib import Path

# Add the src directory to the Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    """Main function to start the fertilizer application service."""
    try:
        logger.info("Starting AFAS Fertilizer Application Service...")
        
        # Get configuration from environment variables
        host = os.getenv("FERTILIZER_APPLICATION_HOST", "0.0.0.0")
        port = int(os.getenv("FERTILIZER_APPLICATION_PORT", "8008"))
        reload = os.getenv("FERTILIZER_APPLICATION_RELOAD", "false").lower() == "true"
        log_level = os.getenv("FERTILIZER_APPLICATION_LOG_LEVEL", "info").lower()
        
        logger.info(f"Service configuration:")
        logger.info(f"  Host: {host}")
        logger.info(f"  Port: {port}")
        logger.info(f"  Reload: {reload}")
        logger.info(f"  Log Level: {log_level}")
        
        # Start the service
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=reload,
            log_level=log_level,
            access_log=True
        )
        
    except KeyboardInterrupt:
        logger.info("Service stopped by user")
    except Exception as e:
        logger.error(f"Failed to start service: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
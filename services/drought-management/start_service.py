#!/usr/bin/env python3
"""
Drought Management Service Startup Script

This script starts the drought management microservice with proper
configuration and environment setup.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Add the src directory to the Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment():
    """Check if required environment variables are set."""
    required_vars = [
        "DROUGHT_MANAGEMENT_PORT",
        "DATABASE_URL",
        "WEATHER_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.warning(f"Missing environment variables: {missing_vars}")
        logger.info("Using default values for missing variables")
    
    return len(missing_vars) == 0

def install_dependencies():
    """Install required dependencies if needed."""
    requirements_file = current_dir / "requirements.txt"
    if requirements_file.exists():
        try:
            logger.info("Installing dependencies...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ])
            logger.info("Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install dependencies: {e}")
            return False
    return True

def start_service():
    """Start the drought management service."""
    try:
        logger.info("Starting Drought Management Service...")
        
        # Set default environment variables if not set
        os.environ.setdefault("DROUGHT_MANAGEMENT_PORT", "8007")
        os.environ.setdefault("DATABASE_URL", "postgresql://localhost:5432/afas_drought")
        os.environ.setdefault("WEATHER_API_KEY", "demo_key")
        
        # Import and run the FastAPI app
        from src.main import app
        import uvicorn
        
        port = int(os.getenv("DROUGHT_MANAGEMENT_PORT", 8007))
        host = os.getenv("DROUGHT_MANAGEMENT_HOST", "0.0.0.0")
        
        logger.info(f"Starting service on {host}:{port}")
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=True,
            log_level="info"
        )
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.info("Make sure all dependencies are installed")
        return False
    except Exception as e:
        logger.error(f"Failed to start service: {e}")
        return False
    
    return True

def main():
    """Main function to start the drought management service."""
    logger.info("=== AFAS Drought Management Service Startup ===")
    
    # Check environment
    env_ok = check_environment()
    
    # Install dependencies
    deps_ok = install_dependencies()
    
    if not deps_ok:
        logger.error("Failed to install dependencies. Exiting.")
        sys.exit(1)
    
    # Start the service
    if start_service():
        logger.info("Service started successfully")
    else:
        logger.error("Failed to start service")
        sys.exit(1)

if __name__ == "__main__":
    main()
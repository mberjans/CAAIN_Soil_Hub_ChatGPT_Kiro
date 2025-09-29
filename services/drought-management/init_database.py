#!/usr/bin/env python3
"""
Database initialization script for Drought Management Service.

This script creates the database tables and initializes the drought management database.
Run this script before starting the service for the first time.
"""

import asyncio
import os
import sys
from pathlib import Path
import logging

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent / "src"))

from database.drought_db import DroughtServiceDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def initialize_database():
    """Initialize the drought management database."""
    try:
        # Get database URL from environment or use default
        database_url = os.getenv(
            "DATABASE_URL", 
            "postgresql://localhost:5432/afas_drought"
        )
        
        logger.info(f"Initializing drought management database: {database_url}")
        
        # Create database instance
        db = DroughtServiceDatabase(database_url)
        
        # Initialize database (creates tables)
        await db.initialize()
        
        # Test database health
        health_status = await db.health_check()
        if health_status:
            logger.info("✅ Database initialization successful!")
            logger.info("✅ All tables created successfully!")
            logger.info("✅ Database health check passed!")
        else:
            logger.error("❌ Database health check failed!")
            return False
        
        # Clean up
        await db.cleanup()
        
        logger.info("🎉 Drought Management Database is ready!")
        logger.info("📋 Created tables:")
        logger.info("   - drought_assessments")
        logger.info("   - conservation_practices")
        logger.info("   - drought_monitoring")
        logger.info("   - monitoring_data_points")
        logger.info("   - water_savings")
        logger.info("   - drought_alerts")
        logger.info("   - field_characteristics")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        logger.error("Please check your database connection and try again.")
        return False

async def main():
    """Main function."""
    logger.info("🚀 Starting Drought Management Database Initialization...")
    
    success = await initialize_database()
    
    if success:
        logger.info("✅ Database initialization completed successfully!")
        logger.info("🚀 You can now start the drought management service.")
        sys.exit(0)
    else:
        logger.error("❌ Database initialization failed!")
        logger.error("Please check the error messages above and try again.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
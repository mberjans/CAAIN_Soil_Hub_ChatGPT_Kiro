#!/usr/bin/env python3
"""
Database deployment script for Cover Crop Benefit Tracking System.

This script deploys the benefit tracking database schema to PostgreSQL.
Run this script to set up the benefit tracking tables, indexes, and triggers.

Usage:
    python deploy_benefit_tracking_schema.py
    
Environment Variables:
    DATABASE_URL: PostgreSQL connection string
    POSTGRES_HOST: Database host (default: localhost)
    POSTGRES_PORT: Database port (default: 5432)
    POSTGRES_DB: Database name (default: caain_soil_hub)
    POSTGRES_USER: Database user
    POSTGRES_PASSWORD: Database password
"""

import os
import sys
import asyncio
import asyncpg
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def get_database_connection():
    """Get database connection from environment variables."""
    # Try DATABASE_URL first
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return await asyncpg.connect(database_url)
    
    # Build connection from individual components
    host = os.getenv('POSTGRES_HOST', 'localhost')
    port = int(os.getenv('POSTGRES_PORT', '5432'))
    database = os.getenv('POSTGRES_DB', 'caain_soil_hub')
    user = os.getenv('POSTGRES_USER')
    password = os.getenv('POSTGRES_PASSWORD')
    
    if not user or not password:
        raise ValueError(
            "Database credentials not found. Please set DATABASE_URL or "
            "POSTGRES_USER and POSTGRES_PASSWORD environment variables."
        )
    
    return await asyncpg.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )


async def deploy_schema():
    """Deploy the benefit tracking database schema."""
    try:
        # Get database connection
        logger.info("Connecting to database...")
        conn = await get_database_connection()
        logger.info("✅ Connected to database")
        
        # Read schema file
        schema_path = Path(__file__).parent.parent.parent / "databases" / "postgresql" / "benefit_tracking_schema.sql"
        
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        
        logger.info(f"Reading schema from: {schema_path}")
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Execute schema deployment
        logger.info("Deploying benefit tracking schema...")
        await conn.execute(schema_sql)
        logger.info("✅ Schema deployed successfully")
        
        # Verify tables were created
        logger.info("Verifying table creation...")
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'benefit_%'
            ORDER BY table_name;
        """)
        
        created_tables = [table['table_name'] for table in tables]
        expected_tables = [
            'benefit_quantification_entries',
            'benefit_measurement_records', 
            'benefit_tracking_fields',
            'benefit_validation_protocols'
        ]
        
        logger.info(f"Created tables: {created_tables}")
        
        # Check if all expected tables exist
        missing_tables = set(expected_tables) - set(created_tables)
        if missing_tables:
            logger.warning(f"Missing expected tables: {missing_tables}")
        else:
            logger.info("✅ All expected tables created successfully")
        
        # Check indexes
        logger.info("Verifying indexes...")
        indexes = await conn.fetch("""
            SELECT indexname, tablename 
            FROM pg_indexes 
            WHERE tablename LIKE 'benefit_%'
            ORDER BY tablename, indexname;
        """)
        
        logger.info(f"Created indexes: {len(indexes)} indexes")
        for idx in indexes:
            logger.info(f"  - {idx['tablename']}.{idx['indexname']}")
        
        await conn.close()
        logger.info("✅ Database deployment completed successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Schema deployment failed: {e}")
        return False


async def check_schema_status():
    """Check if the benefit tracking schema is already deployed."""
    try:
        conn = await get_database_connection()
        
        # Check if benefit tracking tables exist
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'benefit_%';
        """)
        
        await conn.close()
        
        if tables:
            logger.info(f"Found {len(tables)} existing benefit tracking tables:")
            for table in tables:
                logger.info(f"  - {table['table_name']}")
            return True
        else:
            logger.info("No existing benefit tracking tables found")
            return False
            
    except Exception as e:
        logger.error(f"Error checking schema status: {e}")
        return False


async def main():
    """Main deployment function."""
    logger.info("=== Cover Crop Benefit Tracking Schema Deployment ===")
    
    # Check current schema status
    logger.info("Checking current schema status...")
    schema_exists = await check_schema_status()
    
    if schema_exists:
        response = input("\nBenefit tracking tables already exist. Redeploy? (y/N): ")
        if response.lower() != 'y':
            logger.info("Deployment cancelled")
            return
    
    # Deploy schema
    success = await deploy_schema()
    
    if success:
        logger.info("\n🎯 DEPLOYMENT SUCCESSFUL!")
        logger.info("The benefit tracking system is now ready for use.")
        logger.info("\nNext steps:")
        logger.info("1. Test the API endpoints at /api/v1/cover-crops/benefits/")
        logger.info("2. Use /select-with-benefit-tracking for enhanced recommendations")
        logger.info("3. Monitor analytics at /benefits/analytics")
    else:
        logger.error("\n❌ DEPLOYMENT FAILED!")
        logger.error("Please check the error messages above and retry.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
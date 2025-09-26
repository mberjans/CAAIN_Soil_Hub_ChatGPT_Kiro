#!/usr/bin/env python3
"""
Climate Zone Database Migration Runner
TICKET-001_climate-zone-detection-4.3
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging
import sys
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_database_if_not_exists():
    """Create the AFAS database if it doesn't exist."""
    try:
        # Connect to default postgres database
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user=os.getenv("USER"),  # Use current user
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        with conn.cursor() as cursor:
            # Check if database exists
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'afas_db'")
            if not cursor.fetchone():
                logger.info("Creating AFAS database...")
                cursor.execute("CREATE DATABASE afas_db")
                logger.info("✅ AFAS database created successfully")
            else:
                logger.info("✅ AFAS database already exists")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create database: {e}")
        return False

def run_migration():
    """Run the climate zone enhancement migration."""
    try:
        # Connect to AFAS database
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user=os.getenv("USER"),
            database="afas_db"
        )
        
        migration_file = "002_climate_zone_enhancement.sql" 
        migration_path = os.path.join(os.path.dirname(__file__), migration_file)
        
        if not os.path.exists(migration_path):
            raise FileNotFoundError(f"Migration file not found: {migration_path}")
        
        logger.info(f"Running climate zone migration: {migration_file}")
        
        with conn.cursor() as cursor:
            # Enable UUID extension if not already enabled
            cursor.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
            conn.commit()
            
            # Read and execute migration
            with open(migration_path, 'r') as f:
                migration_sql = f.read()
            
            cursor.execute(migration_sql)
            conn.commit()
            
            logger.info("✅ Climate zone migration completed successfully")
            
            # Verify tables were created
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('climate_zone_data', 'historical_climate_patterns', 'climate_zone_cache')
                ORDER BY table_name
            """)
            
            tables = cursor.fetchall()
            logger.info(f"Created tables: {[table[0] for table in tables]}")
            
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False

def main():
    """Main function."""
    logger.info("🌡️ Starting Climate Zone Database Migration")
    logger.info("=" * 50)
    
    # Create database if needed
    if not create_database_if_not_exists():
        sys.exit(1)
    
    # Run migration
    if not run_migration():
        sys.exit(1)
    
    logger.info("=" * 50)
    logger.info("🎉 Climate Zone Migration Complete!")

if __name__ == "__main__":
    main()
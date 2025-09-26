#!/usr/bin/env python3
"""
Complete Database Setup for Climate Zone Migration
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
            user=os.getenv("USER"),
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

def create_base_tables():
    """Create essential base tables needed for climate zone migration."""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432", 
            user=os.getenv("USER"),
            database="afas_db"
        )
        
        with conn.cursor() as cursor:
            # Enable UUID extension
            cursor.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
            
            # Create users table (referenced by other tables)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create farms table (referenced by climate zone migration)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS farms (
                    farm_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                    farm_name VARCHAR(100) NOT NULL,
                    farm_size_acres DECIMAL(10,2),
                    state VARCHAR(50),
                    county VARCHAR(100),
                    usda_hardiness_zone VARCHAR(10),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create farm_locations table (referenced by climate zone migration)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS farm_locations (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                    name VARCHAR(100) NOT NULL,
                    latitude DECIMAL(10, 8) NOT NULL,
                    longitude DECIMAL(11, 8) NOT NULL,
                    address TEXT,
                    county VARCHAR(100),
                    state VARCHAR(50),
                    climate_zone VARCHAR(20),
                    source VARCHAR(20) NOT NULL CHECK (source IN ('gps', 'address', 'map', 'current')),
                    verified BOOLEAN DEFAULT FALSE,
                    accuracy_meters INTEGER,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    
                    -- Constraints
                    CONSTRAINT valid_latitude CHECK (latitude >= -90 AND latitude <= 90),
                    CONSTRAINT valid_longitude CHECK (longitude >= -180 AND longitude <= 180)
                )
            """)
            
            # Create weather_data table (referenced by climate zone migration)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS weather_data (
                    weather_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    location_id UUID REFERENCES farm_locations(id) ON DELETE CASCADE,
                    date DATE NOT NULL,
                    temperature_f DECIMAL(5,2),
                    humidity DECIMAL(5,2),
                    precipitation_inches DECIMAL(6,3),
                    wind_speed_mph DECIMAL(5,2),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            logger.info("✅ Base tables created successfully")
            
            # Verify tables exist
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('users', 'farms', 'farm_locations', 'weather_data')
                ORDER BY table_name
            """)
            
            tables = cursor.fetchall()
            logger.info(f"Base tables created: {[table[0] for table in tables]}")
            
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create base tables: {e}")
        return False

def run_climate_migration():
    """Run the climate zone enhancement migration."""
    try:
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
            # Read and execute migration
            with open(migration_path, 'r') as f:
                migration_sql = f.read()
            
            cursor.execute(migration_sql)
            conn.commit()
            
            logger.info("✅ Climate zone migration completed successfully")
            
            # Verify new tables were created
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('climate_zone_data', 'historical_climate_patterns', 'climate_zone_cache')
                ORDER BY table_name
            """)
            
            tables = cursor.fetchall()
            logger.info(f"Climate zone tables created: {[table[0] for table in tables]}")
            
            # Check if views were created
            cursor.execute("""
                SELECT table_name FROM information_schema.views 
                WHERE table_schema = 'public' 
                AND table_name IN ('farms_with_climate', 'farm_locations_with_climate', 'climate_zone_summary')
                ORDER BY table_name
            """)
            
            views = cursor.fetchall()
            logger.info(f"Climate zone views created: {[view[0] for view in views]}")
            
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Climate migration failed: {e}")
        return False

def main():
    """Main function."""
    logger.info("🌡️ Starting Complete Climate Zone Database Setup")
    logger.info("=" * 55)
    
    # Create database if needed
    if not create_database_if_not_exists():
        sys.exit(1)
    
    # Create base tables
    if not create_base_tables():
        sys.exit(1)
    
    # Run climate zone migration
    if not run_climate_migration():
        sys.exit(1)
    
    logger.info("=" * 55)
    logger.info("🎉 Complete Climate Zone Database Setup Finished!")

if __name__ == "__main__":
    main()
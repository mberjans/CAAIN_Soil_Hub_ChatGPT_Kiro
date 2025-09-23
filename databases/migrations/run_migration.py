#!/usr/bin/env python3
"""
Database Migration Runner for Farm Location Input Feature
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024
"""

import os
import sys
import argparse
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from pathlib import Path
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MigrationRunner:
    """Database migration runner for farm location tables."""
    
    def __init__(self, database_url: str):
        """Initialize migration runner with database connection."""
        self.database_url = database_url
        self.migration_dir = Path(__file__).parent
        
    def connect(self):
        """Create database connection."""
        try:
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            return conn
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def run_migration(self, migration_file: str):
        """Run a specific migration file."""
        migration_path = self.migration_dir / migration_file
        
        if not migration_path.exists():
            raise FileNotFoundError(f"Migration file not found: {migration_path}")
        
        logger.info(f"Running migration: {migration_file}")
        
        with self.connect() as conn:
            with conn.cursor() as cursor:
                try:
                    # Read migration file
                    with open(migration_path, 'r') as f:
                        migration_sql = f.read()
                    
                    # Execute migration
                    cursor.execute(migration_sql)
                    
                    logger.info(f"Migration {migration_file} completed successfully")
                    
                except psycopg2.Error as e:
                    logger.error(f"Migration {migration_file} failed: {e}")
                    raise
    
    def create_farm_location_tables(self):
        """Create farm location tables."""
        self.run_migration('001_create_farm_location_tables.sql')
    
    def rollback_farm_location_tables(self):
        """Rollback farm location tables (WARNING: Deletes all data)."""
        logger.warning("WARNING: This will permanently delete all farm location data!")
        response = input("Are you sure you want to continue? (yes/no): ")
        
        if response.lower() != 'yes':
            logger.info("Rollback cancelled")
            return
        
        self.run_migration('001_rollback_farm_location_tables.sql')
    
    def check_tables_exist(self):
        """Check if farm location tables exist."""
        with self.connect() as conn:
            with conn.cursor() as cursor:
                # Check for farm_locations table
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'farm_locations'
                    )
                """)
                farm_locations_exists = cursor.fetchone()[0]
                
                # Check for farm_fields table
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'farm_fields'
                    )
                """)
                farm_fields_exists = cursor.fetchone()[0]
                
                # Check for geocoding_cache table
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'geocoding_cache'
                    )
                """)
                geocoding_cache_exists = cursor.fetchone()[0]
                
                logger.info(f"Table status:")
                logger.info(f"  farm_locations: {'EXISTS' if farm_locations_exists else 'NOT EXISTS'}")
                logger.info(f"  farm_fields: {'EXISTS' if farm_fields_exists else 'NOT EXISTS'}")
                logger.info(f"  geocoding_cache: {'EXISTS' if geocoding_cache_exists else 'NOT EXISTS'}")
                
                return farm_locations_exists and farm_fields_exists and geocoding_cache_exists
    
    def validate_schema(self):
        """Validate that the schema is correctly created."""
        with self.connect() as conn:
            with conn.cursor() as cursor:
                try:
                    # Test farm_locations table structure
                    cursor.execute("""
                        SELECT column_name, data_type, is_nullable 
                        FROM information_schema.columns 
                        WHERE table_name = 'farm_locations' 
                        ORDER BY ordinal_position
                    """)
                    farm_locations_columns = cursor.fetchall()
                    
                    # Test farm_fields table structure
                    cursor.execute("""
                        SELECT column_name, data_type, is_nullable 
                        FROM information_schema.columns 
                        WHERE table_name = 'farm_fields' 
                        ORDER BY ordinal_position
                    """)
                    farm_fields_columns = cursor.fetchall()
                    
                    # Test geocoding_cache table structure
                    cursor.execute("""
                        SELECT column_name, data_type, is_nullable 
                        FROM information_schema.columns 
                        WHERE table_name = 'geocoding_cache' 
                        ORDER BY ordinal_position
                    """)
                    geocoding_cache_columns = cursor.fetchall()
                    
                    logger.info("Schema validation successful")
                    logger.info(f"farm_locations has {len(farm_locations_columns)} columns")
                    logger.info(f"farm_fields has {len(farm_fields_columns)} columns")
                    logger.info(f"geocoding_cache has {len(geocoding_cache_columns)} columns")
                    
                    return True
                    
                except psycopg2.Error as e:
                    logger.error(f"Schema validation failed: {e}")
                    return False


def main():
    """Main function for command line interface."""
    parser = argparse.ArgumentParser(description='Farm Location Database Migration Runner')
    parser.add_argument('--database-url', required=True, help='PostgreSQL database URL')
    parser.add_argument('--action', choices=['create', 'rollback', 'check', 'validate'], 
                       required=True, help='Migration action to perform')
    
    args = parser.parse_args()
    
    try:
        runner = MigrationRunner(args.database_url)
        
        if args.action == 'create':
            runner.create_farm_location_tables()
            logger.info("Farm location tables created successfully")
            
        elif args.action == 'rollback':
            runner.rollback_farm_location_tables()
            logger.info("Farm location tables rolled back successfully")
            
        elif args.action == 'check':
            exists = runner.check_tables_exist()
            if exists:
                logger.info("All farm location tables exist")
            else:
                logger.warning("Some farm location tables are missing")
                sys.exit(1)
                
        elif args.action == 'validate':
            valid = runner.validate_schema()
            if valid:
                logger.info("Schema validation passed")
            else:
                logger.error("Schema validation failed")
                sys.exit(1)
    
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
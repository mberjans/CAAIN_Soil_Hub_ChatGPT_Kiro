#!/usr/bin/env python3
"""
Database Migration Runner for Enhanced Crop Varieties
TICKET-005_crop-variety-recommendations-1.1
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_database_url():
    """Get database connection URL from environment or defaults."""
    host = os.getenv('POSTGRES_HOST', 'localhost')
    port = os.getenv('POSTGRES_PORT', '5432')
    db = os.getenv('POSTGRES_DB', 'afas_db')
    user = os.getenv('POSTGRES_USER', 'afas_user')
    password = os.getenv('POSTGRES_PASSWORD', 'afas_password_2024')
    
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"

def run_migration():
    """Run the enhanced crop varieties migration."""
    migration_file = "databases/migrations/005_expand_enhanced_crop_varieties.sql"
    
    if not Path(migration_file).exists():
        logger.error(f"Migration file not found: {migration_file}")
        return False
    
    try:
        # Connect to database
        database_url = get_database_url()
        logger.info(f"Connecting to database: {database_url.split('@')[1] if '@' in database_url else 'localhost'}")
        
        conn = psycopg2.connect(database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        with conn.cursor() as cursor:
            # Read migration file
            with open(migration_file, 'r') as f:
                migration_sql = f.read()
            
            # Execute migration
            logger.info("Running enhanced crop varieties migration...")
            cursor.execute(migration_sql)
            
            logger.info("✅ Enhanced crop varieties migration completed successfully")
            
        conn.close()
        return True
        
    except psycopg2.Error as e:
        logger.error(f"❌ Migration failed: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
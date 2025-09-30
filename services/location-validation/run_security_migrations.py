#!/usr/bin/env python3
"""
Run Security Migrations
CAAIN Soil Hub - Location Validation Service

Script to run security database migrations for location data protection.
"""

import os
import sys
import logging
from pathlib import Path

# Add the src directory to the Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from database.security_migrations import run_security_migrations

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run security migrations."""
    logger.info("Starting location security migrations...")
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL environment variable not set")
        logger.info("Please set DATABASE_URL to your PostgreSQL connection string")
        logger.info("Example: postgresql://user:password@localhost/location_validation")
        sys.exit(1)
    
    logger.info(f"Using database: {database_url.split('@')[1] if '@' in database_url else 'local'}")
    
    try:
        # Run security migrations
        success = run_security_migrations(database_url)
        
        if success:
            logger.info("Security migrations completed successfully!")
            logger.info("Security features are now available:")
            logger.info("  - Location data encryption")
            logger.info("  - Access control and audit logging")
            logger.info("  - Privacy protection and anonymization")
            logger.info("  - GDPR compliance features")
            logger.info("  - Security monitoring and anomaly detection")
        else:
            logger.error("Security migrations failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Migration error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
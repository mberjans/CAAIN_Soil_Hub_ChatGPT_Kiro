"""Performance optimization setup for the crop filtering system."""
import logging
import os
from typing import Optional

from .database_optimizer import DatabaseOptimizer
from .crop_taxonomy_service import crop_taxonomy_service

logger = logging.getLogger(__name__)

def setup_performance_optimizations(database_url: Optional[str] = None):
    """Setup all performance optimizations for the crop filtering system."""
    
    logger.info("Starting performance optimization setup for crop filtering system...")
    
    # Initialize database connection if URL is provided or available in environment
    if database_url is None:
        database_url = os.getenv("DATABASE_URL")
    
    if database_url is None:
        logger.warning("No database URL provided; skipping database performance optimizations.")
        return
    
    try:
        # Initialize and run database optimizations
        from .database.crop_taxonomy_db import CropTaxonomyDatabase
        db = CropTaxonomyDatabase(database_url)
        
        # Check if database connection is available
        if not db.test_connection():
            logger.error("Unable to connect to database; skipping database performance optimizations.")
            return
            
        optimizer = DatabaseOptimizer(db)
        optimizer.run_all_optimizations()
        
        logger.info("Database performance optimizations completed successfully.")
        
    except ImportError:
        logger.warning("Database module not available; skipping database performance optimizations.")
    except Exception as e:
        logger.error(f"Error during database optimization setup: {e}")
    
    # The caching and performance monitoring are already initialized in the services
    logger.info("Performance optimization setup completed.")


def run_performance_report():
    """Generate and return a performance report."""
    from .performance_monitor import performance_monitor
    return performance_monitor.generate_performance_report()


def get_bottleneck_operations(threshold_ms: float = 100.0):
    """Get operations that are considered bottlenecks based on execution time."""
    from .performance_monitor import performance_monitor
    return performance_monitor.get_bottleneck_operations(threshold_ms)


# Run initial setup when module is imported
setup_performance_optimizations()
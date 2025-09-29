"""
Database Initialization Script for Expert Validation System

This script initializes the database tables and sample data for the
agricultural expert validation and field testing system.
"""

import asyncio
import logging
from pathlib import Path
import sys

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from expert_validation_db import ExpertValidationDB

logger = logging.getLogger(__name__)


async def initialize_expert_validation_database():
    """Initialize expert validation database tables and sample data."""
    try:
        logger.info("Initializing Expert Validation Database...")
        
        # Create database instance
        db = ExpertValidationDB()
        
        # Create tables
        await db.create_expert_validation_tables()
        logger.info("Expert validation tables created successfully")
        
        # Initialize expert panel with sample data
        await db.initialize_expert_panel()
        logger.info("Expert panel initialized with sample data")
        
        # Create initial metrics record
        from models.expert_validation_models import ValidationMetrics
        initial_metrics = ValidationMetrics(
            total_validations=0,
            expert_approval_rate=0.0,
            recommendation_accuracy=0.0,
            farmer_satisfaction=0.0,
            average_review_time_hours=0.0,
            field_test_success_rate=0.0,
            expert_panel_size=5,  # Based on sample data
            active_field_tests=0,
            validation_period_days=30
        )
        await db.save_validation_metrics(initial_metrics)
        logger.info("Initial validation metrics created")
        
        logger.info("Expert Validation Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize expert validation database: {e}")
        raise


async def main():
    """Main function to run database initialization."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    await initialize_expert_validation_database()


if __name__ == "__main__":
    asyncio.run(main())
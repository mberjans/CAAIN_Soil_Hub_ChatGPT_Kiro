"""
Database package for Fertilizer Type Selection

Database models, configuration, and utilities for fertilizer type selection service.
"""

from .config import (
    get_db_session,
    get_db,
    create_tables,
    drop_tables,
    init_database,
    get_database_manager,
    DatabaseManager
)

from .fertilizer_schema import (
    Base,
    FertilizerProduct,
    FertilizerRecommendation,
    FertilizerComparison,
    FertilizerSelectionSession,
    EquipmentCompatibility,
    FertilizerPriceHistory
)

from .seed_data import (
    seed_fertilizer_products,
    seed_equipment_compatibility
)

__all__ = [
    # Configuration
    "get_db_session",
    "get_db",
    "create_tables",
    "drop_tables",
    "init_database",
    "get_database_manager",
    "DatabaseManager",
    
    # Schema
    "Base",
    "FertilizerProduct",
    "FertilizerRecommendation",
    "FertilizerComparison",
    "FertilizerSelectionSession",
    "EquipmentCompatibility",
    "FertilizerPriceHistory",
    
    # Seed data
    "seed_fertilizer_products",
    "seed_equipment_compatibility"
]
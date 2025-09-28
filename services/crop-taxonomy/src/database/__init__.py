"""
Database access layer for the crop taxonomy service.

This module provides database integration for the comprehensive crop taxonomy system,
connecting the service layer to the PostgreSQL database with full SQLAlchemy ORM support.

Version: 1.0
Author: Agricultural AI Systems
Date: 2024
"""

from .crop_taxonomy_db import CropTaxonomyDatabase, crop_taxonomy_db

__all__ = ['CropTaxonomyDatabase', 'crop_taxonomy_db']
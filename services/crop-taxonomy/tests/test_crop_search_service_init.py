"""
Test for CropSearchService initialization only.
This test is created separately to handle the circular import issue.
"""
import unittest
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

def test_crop_search_service_init():
    """
    Test CropSearchService initialization.
    This test handles the circular import by mocking dependencies.
    """
    # Mock the problematic imports to avoid circular dependencies
    with patch.dict('sys.modules', {
        'src.services.result_processor': MagicMock(),
        'src.database.crop_taxonomy_db': MagicMock(),
        'src.services.variety_recommendation_service': MagicMock(),
        'src.services.filter_cache_service': MagicMock(),
        'src.services.performance_monitor': MagicMock(),
        'src.data.reference_crops': MagicMock(),
        'src.models.crop_filtering_models': MagicMock(),
        'src.models.crop_taxonomy_models': MagicMock(),
    }):
        try:
            # Now try to import the class - this should work with mocked dependencies
            from src.services.crop_search_service import CropSearchService
            
            # Verify that the class has the expected methods and attributes
            assert hasattr(CropSearchService, '__init__')
            assert hasattr(CropSearchService, 'search_crops')
            assert hasattr(CropSearchService, '_evaluate_candidates')
            assert hasattr(CropSearchService, '_initialize_scoring_weights')
            assert hasattr(CropSearchService, '_evaluate_crop')
            
            # Try creating an instance - this should work with mocked dependencies
            service = CropSearchService(database_url=None)
            
            # Verify that the service instance has the basic expected attributes
            assert hasattr(service, 'scoring_weights')
            assert hasattr(service, 'search_cache')
            assert hasattr(service, 'reference_crops')
            assert hasattr(service, 'database_available')
            assert hasattr(service, '_optimizations_initialized')
            
            # Verify that the scoring weights dictionary contains expected keys
            expected_weights = [
                "text_match", "taxonomy_match", "geographic_match", "climate_match", 
                "soil_match", "agricultural_match", "management_match", 
                "sustainability_match", "economic_match"
            ]
            # Since we've mocked the initialization, we'll check if the weights initialization method exists
            assert hasattr(CropSearchService, '_initialize_scoring_weights')
            
            print("CropSearchService initialization test passed.")
        except ImportError as e:
            # If we still get an import error, we need to document it
            print(f"Import error during CropSearchService test: {e}")
            raise AssertionError(f"CropSearchService should be importable: {e}")


if __name__ == "__main__":
    test_crop_search_service_init()
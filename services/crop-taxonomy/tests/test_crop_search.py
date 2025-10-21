"""
Unit tests for CropSearchService and its _apply_pest_resistance_filters method.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.filtering_models import Base, CropFilteringAttributes
from src.services.crop_search_service import CropSearchService
from src.schemas.crop_schemas import CropFilterRequest, PestResistanceFilter
from uuid import uuid4, UUID


def test_apply_pest_resistance_filters_with_matching_pests():
    """Test _apply_pest_resistance_filters method with matching pest traits."""
    # Create a mock database session
    db_session = Mock(spec=Session)
    
    # Create service instance
    service = CropSearchService(db_session)
    
    # Create pest resistance filters
    pest_filters = [
        PestResistanceFilter(pest_name="corn_borer", min_resistance_level="resistant"),
        PestResistanceFilter(pest_name="aphids", min_resistance_level="moderate")
    ]
    
    # Create crop filter request
    filter_request = CropFilterRequest(
        crop_type="corn",
        pest_resistance=pest_filters,
        page=1,
        page_size=20
    )
    
    # Create a mock query object
    mock_query = Mock()
    mock_query.filter.return_value = mock_query  # Return the same mock for chaining
    
    # Call the method under test
    result_query = service._apply_pest_resistance_filters(mock_query, filter_request)
    
    # Verify that filter was called twice (once for each pest)
    assert mock_query.filter.call_count == 2
    
    # Verify the filter calls were made with the correct parameters
    calls = mock_query.filter.call_args_list
    
    # First call should filter for corn_borer with resistant level
    pest_resistance_call = calls[0][0][0]
    assert "crop_filtering_attributes.c" in str(pest_resistance_call) or "pest_resistance_traits" in str(pest_resistance_call)
    
    # Second call should filter for aphids with moderate level
    aphids_resistance_call = calls[1][0][0]
    assert "crop_filtering_attributes.c" in str(aphids_resistance_call) or "pest_resistance_traits" in str(aphids_resistance_call)


def test_apply_pest_resistance_filters_with_no_pests():
    """Test _apply_pest_resistance_filters method when no pest filters are provided."""
    # Create a mock database session
    db_session = Mock(spec=Session)
    
    # Create service instance
    service = CropSearchService(db_session)
    
    # Create crop filter request with no pest resistance filters
    filter_request = CropFilterRequest(
        crop_type="corn",
        page=1,
        page_size=20
    )
    
    # Create a mock query object
    mock_query = Mock()
    
    # Call the method under test
    result_query = service._apply_pest_resistance_filters(mock_query, filter_request)
    
    # Verify that filter was not called (no pest filters to apply)
    mock_query.filter.assert_not_called()
    
    # Should return the same query object
    assert result_query == mock_query


def test_apply_pest_resistance_filters_with_various_resistance_levels():
    """Test _apply_pest_resistance_filters with different resistance levels."""
    # Create a mock database session
    db_session = Mock(spec=Session)
    
    # Create service instance
    service = CropSearchService(db_session)
    
    # Test with susceptible level (should match susceptible, moderate, or resistant)
    pest_filters = [
        PestResistanceFilter(pest_name="rootworm", min_resistance_level="susceptible")
    ]
    
    filter_request = CropFilterRequest(
        crop_type="corn",
        pest_resistance=pest_filters,
        page=1,
        page_size=20
    )
    
    # Create a mock query object
    mock_query = Mock()
    mock_query.filter.return_value = mock_query  # Return the same mock for chaining
    
    # Call the method under test
    result_query = service._apply_pest_resistance_filters(mock_query, filter_request)
    
    # Verify that filter was called once
    assert mock_query.filter.call_count == 1


def test_get_resistance_levels():
    """Test _get_resistance_levels helper method."""
    # Create a mock database session
    db_session = Mock(spec=Session)
    
    # Create service instance
    service = CropSearchService(db_session)
    
    # Test susceptible level (should return all levels)
    levels = service._get_resistance_levels("susceptible")
    assert set(levels) == {"susceptible", "moderate", "resistant"}
    
    # Test moderate level (should return moderate and resistant)
    levels = service._get_resistance_levels("moderate")
    assert set(levels) == {"moderate", "resistant"}
    
    # Test resistant level (should return only resistant)
    levels = service._get_resistance_levels("resistant")
    assert set(levels) == {"resistant"}
    
    # Test unknown level (should return resistant as default)
    levels = service._get_resistance_levels("unknown")
    assert levels == ["resistant"]


def test_crop_search_service_init():
    """Test initialization of CropSearchService."""
    db_session = Mock(spec=Session)
    service = CropSearchService(db_session)
    
    assert service.db == db_session


if __name__ == "__main__":
    pytest.main([__file__])
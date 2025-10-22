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
from src.schemas.crop_schemas import CropFilterRequest, PestResistanceFilter, DiseaseResistanceFilter
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


def test_apply_disease_resistance_filters_with_matching_diseases():
    """Test _apply_disease_resistance_filters method with matching disease traits."""
    # Create a mock database session
    db_session = Mock(spec=Session)
    
    # Create service instance
    service = CropSearchService(db_session)
    
    # Create disease resistance filters
    disease_filters = [
        DiseaseResistanceFilter(disease_name="rust", min_resistance_level="resistant"),
        DiseaseResistanceFilter(disease_name="blight", min_resistance_level="moderate")
    ]
    
    # Create crop filter request
    filter_request = CropFilterRequest(
        crop_type="corn",
        disease_resistance=disease_filters,
        page=1,
        page_size=20
    )
    
    # Create a mock query object
    mock_query = Mock()
    mock_query.filter.return_value = mock_query  # Return the same mock for chaining
    
    # Call the method under test
    result_query = service._apply_disease_resistance_filters(mock_query, filter_request)
    
    # Verify that filter was called twice (once for each disease)
    assert mock_query.filter.call_count == 2
    
    # Verify the filter calls were made with the correct parameters
    calls = mock_query.filter.call_args_list
    
    # First call should filter for rust with resistant level
    disease_resistance_call = calls[0][0][0]
    assert "disease_resistance_traits" in str(disease_resistance_call)
    
    # Second call should filter for blight with moderate level
    blight_resistance_call = calls[1][0][0]
    assert "disease_resistance_traits" in str(blight_resistance_call)

def test_apply_disease_resistance_filters_with_no_diseases():
    """Test _apply_disease_resistance_filters method when no disease filters are provided."""
    # Create a mock database session
    db_session = Mock(spec=Session)
    
    # Create service instance
    service = CropSearchService(db_session)
    
    # Create crop filter request with no disease resistance filters
    filter_request = CropFilterRequest(
        crop_type="corn",
        page=1,
        page_size=20
    )
    
    # Create a mock query object
    mock_query = Mock()
    
    # Call the method under test
    result_query = service._apply_disease_resistance_filters(mock_query, filter_request)
    
    # Verify that filter was not called (no disease filters to apply)
    mock_query.filter.assert_not_called()
    
    # Should return the same query object
    assert result_query == mock_query

def test_apply_disease_resistance_filters_with_various_resistance_levels():
    """Test _apply_disease_resistance_filters with different resistance levels."""
    # Create a mock database session
    db_session = Mock(spec=Session)
    
    # Create service instance
    service = CropSearchService(db_session)
    
    # Test with susceptible level (should match susceptible, moderate, or resistant)
    disease_filters = [
        DiseaseResistanceFilter(disease_name="smut", min_resistance_level="susceptible")
    ]
    
    filter_request = CropFilterRequest(
        crop_type="corn",
        disease_resistance=disease_filters,
        page=1,
        page_size=20
    )
    
    # Create a mock query object
    mock_query = Mock()
    mock_query.filter.return_value = mock_query  # Return the same mock for chaining
    
    # Call the method under test
    result_query = service._apply_disease_resistance_filters(mock_query, filter_request)
    
    # Verify that filter was called once
    assert mock_query.filter.call_count == 1

    assert mock_query.filter.call_count == 1


def test_apply_market_class_filters_with_market_class():
    """Test _apply_market_class_filters method with market class filter."""
    # Create a mock database session
    db_session = Mock(spec=Session)
    
    # Create service instance
    service = CropSearchService(db_session)
    
    # Create market class filter
    from src.schemas.crop_schemas import MarketClassFilter
    market_filter = MarketClassFilter(market_class="yellow_dent")
    
    # Create crop filter request
    filter_request = CropFilterRequest(
        crop_type="corn",
        market_class=market_filter,
        page=1,
        page_size=20
    )
    
    # Create a mock query object
    mock_query = Mock()
    mock_query.filter.return_value = mock_query  # Return the same mock for chaining
    
    # Call the method under test
    result_query = service._apply_market_class_filters(mock_query, filter_request)
    
    # Verify that filter was called once for market_class
    mock_query.filter.assert_called_once()


def test_apply_market_class_filters_with_organic_certified():
    """Test _apply_market_class_filters method with organic certification filter."""
    # Create a mock database session
    db_session = Mock(spec=Session)
    
    # Create service instance
    service = CropSearchService(db_session)
    
    # Create market class filter with organic certification
    from src.schemas.crop_schemas import MarketClassFilter
    market_filter = MarketClassFilter(organic_certified=True)
    
    # Create crop filter request
    filter_request = CropFilterRequest(
        crop_type="corn",
        market_class=market_filter,
        page=1,
        page_size=20
    )
    
    # Create a mock query object
    mock_query = Mock()
    mock_query.filter.return_value = mock_query  # Return the same mock for chaining
    
    # Call the method under test
    result_query = service._apply_market_class_filters(mock_query, filter_request)
    
    # Verify that filter was called once for organic_certified
    mock_query.filter.assert_called_once()


def test_apply_market_class_filters_with_non_gmo():
    """Test _apply_market_class_filters method with non-GMO filter."""
    # Create a mock database session
    db_session = Mock(spec=Session)
    
    # Create service instance
    service = CropSearchService(db_session)
    
    # Create market class filter with non-GMO
    from src.schemas.crop_schemas import MarketClassFilter
    market_filter = MarketClassFilter(non_gmo=False)
    
    # Create crop filter request
    filter_request = CropFilterRequest(
        crop_type="corn",
        market_class=market_filter,
        page=1,
        page_size=20
    )
    
    # Create a mock query object
    mock_query = Mock()
    mock_query.filter.return_value = mock_query  # Return the same mock for chaining
    
    # Call the method under test
    result_query = service._apply_market_class_filters(mock_query, filter_request)
    
    # Verify that filter was called once for non_gmo
    mock_query.filter.assert_called_once()


def test_apply_market_class_filters_with_all_filters():
    """Test _apply_market_class_filters method with all market class filters."""
    # Create a mock database session
    db_session = Mock(spec=Session)
    
    # Create service instance
    service = CropSearchService(db_session)
    
    # Create market class filter with all options
    from src.schemas.crop_schemas import MarketClassFilter
    market_filter = MarketClassFilter(
        market_class="white_corn",
        organic_certified=True,
        non_gmo=True
    )
    
    # Create crop filter request
    filter_request = CropFilterRequest(
        crop_type="corn",
        market_class=market_filter,
        page=1,
        page_size=20
    )
    
    # Create a mock query object
    mock_query = Mock()
    mock_query.filter.return_value = mock_query  # Return the same mock for chaining
    
    # Call the method under test
    result_query = service._apply_market_class_filters(mock_query, filter_request)
    
    # Verify that filter was called 3 times (once for each market class filter)
    assert mock_query.filter.call_count == 3


def test_apply_market_class_filters_with_no_filters():
    """Test _apply_market_class_filters method when no market class filters are provided."""
    # Create a mock database session
    db_session = Mock(spec=Session)
    
    # Create service instance
    service = CropSearchService(db_session)
    
    # Create crop filter request with no market class filters
    filter_request = CropFilterRequest(
        crop_type="corn",
        page=1,
        page_size=20
    )
    
    # Create a mock query object
    mock_query = Mock()
    
    # Call the method under test
    result_query = service._apply_market_class_filters(mock_query, filter_request)
    
    # Verify that filter was not called (no market class filters to apply)
    mock_query.filter.assert_not_called()
    
    # Should return the same query object
    assert result_query == mock_query


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


def test_apply_performance_filters_with_min_yield_stability():
    """Test _apply_performance_filters method with min yield stability filter."""
    # Create a mock database session
    db_session = Mock(spec=Session)

    # Create service instance
    service = CropSearchService(db_session)

    # Create crop filter request with min_yield_stability
    filter_request = CropFilterRequest(
        crop_type="corn",
        min_yield_stability=80,
        page=1,
        page_size=20
    )

    # Create a mock query object
    mock_query = Mock()
    mock_query.filter.return_value = mock_query  # Return the same mock for chaining

    # Call the method under test
    result_query = service._apply_performance_filters(mock_query, filter_request)

    # Verify that filter was called once
    mock_query.filter.assert_called_once()

    # Verify the filter call was made with the correct parameter
    call_args = mock_query.filter.call_args_list[0][0][0]
    assert "yield_stability_score" in str(call_args)


def test_apply_performance_filters_with_min_drought_tolerance():
    """Test _apply_performance_filters method with min drought tolerance filter."""
    # Create a mock database session
    db_session = Mock(spec=Session)

    # Create service instance
    service = CropSearchService(db_session)

    # Create crop filter request with min_drought_tolerance
    filter_request = CropFilterRequest(
        crop_type="corn",
        min_drought_tolerance=75,
        page=1,
        page_size=20
    )

    # Create a mock query object
    mock_query = Mock()
    mock_query.filter.return_value = mock_query  # Return the same mock for chaining

    # Call the method under test
    result_query = service._apply_performance_filters(mock_query, filter_request)

    # Verify that filter was called once
    mock_query.filter.assert_called_once()

    # Verify the filter call was made with the correct parameter
    call_args = mock_query.filter.call_args_list[0][0][0]
    assert "drought_tolerance_score" in str(call_args)


def test_apply_performance_filters_with_both_filters():
    """Test _apply_performance_filters method with both min yield stability and drought tolerance filters."""
    # Create a mock database session
    db_session = Mock(spec=Session)

    # Create service instance
    service = CropSearchService(db_session)

    # Create crop filter request with both performance filters
    filter_request = CropFilterRequest(
        crop_type="corn",
        min_yield_stability=85,
        min_drought_tolerance=70,
        page=1,
        page_size=20
    )

    # Create a mock query object
    mock_query = Mock()
    mock_query.filter.return_value = mock_query  # Return the same mock for chaining

    # Call the method under test
    result_query = service._apply_performance_filters(mock_query, filter_request)

    # Verify that filter was called twice (once for each performance filter)
    assert mock_query.filter.call_count == 2

    # Verify the filter calls were made with the correct parameters
    calls = mock_query.filter.call_args_list

    # First call should filter for yield_stability_score
    first_call = calls[0][0][0]
    assert "yield_stability_score" in str(first_call)

    # Second call should filter for drought_tolerance_score
    second_call = calls[1][0][0]
    assert "drought_tolerance_score" in str(second_call)


def test_apply_performance_filters_with_no_filters():
    """Test _apply_performance_filters method when no performance filters are provided."""
    # Create a mock database session
    db_session = Mock(spec=Session)

    # Create service instance
    service = CropSearchService(db_session)

    # Create crop filter request with no performance filters
    filter_request = CropFilterRequest(
        crop_type="corn",
        page=1,
        page_size=20
    )

    # Create a mock query object
    mock_query = Mock()

    # Call the method under test
    result_query = service._apply_performance_filters(mock_query, filter_request)

    # Verify that filter was not called (no performance filters to apply)
    mock_query.filter.assert_not_called()

    # Should return the same query object
    assert result_query == mock_query


def test_apply_performance_filters_with_boundary_values():
    """Test _apply_performance_filters method with boundary values (0 and 100)."""
    # Create a mock database session
    db_session = Mock(spec=Session)

    # Create service instance
    service = CropSearchService(db_session)

    # Test with minimum boundary values (0)
    filter_request = CropFilterRequest(
        crop_type="corn",
        min_yield_stability=0,
        min_drought_tolerance=0,
        page=1,
        page_size=20
    )

    # Create a mock query object
    mock_query = Mock()
    mock_query.filter.return_value = mock_query  # Return the same mock for chaining

    # Call the method under test
    result_query = service._apply_performance_filters(mock_query, filter_request)

    # Note: If min_yield_stability is 0 or min_drought_tolerance is 0,
    # they are falsy and won't trigger the filter (based on the implementation)
    # This is intentional behavior to skip zero values
    mock_query.filter.assert_not_called()

    # Now test with maximum boundary values (100)
    filter_request_max = CropFilterRequest(
        crop_type="corn",
        min_yield_stability=100,
        min_drought_tolerance=100,
        page=1,
        page_size=20
    )

    # Create a new mock query object
    mock_query_max = Mock()
    mock_query_max.filter.return_value = mock_query_max

    # Call the method under test
    result_query_max = service._apply_performance_filters(mock_query_max, filter_request_max)

    # Verify that filter was called twice (once for each performance filter)
    assert mock_query_max.filter.call_count == 2


def test_apply_performance_filters_with_yield_stability_only_mid_range():
    """Test _apply_performance_filters with mid-range yield stability value."""
    # Create a mock database session
    db_session = Mock(spec=Session)

    # Create service instance
    service = CropSearchService(db_session)

    # Create crop filter request with mid-range value
    filter_request = CropFilterRequest(
        crop_type="wheat",
        min_yield_stability=50,
        page=1,
        page_size=20
    )

    # Create a mock query object
    mock_query = Mock()
    mock_query.filter.return_value = mock_query

    # Call the method under test
    result_query = service._apply_performance_filters(mock_query, filter_request)

    # Verify that filter was called once
    mock_query.filter.assert_called_once()

    # Verify the result query is the same as the mock (after chaining)
    assert result_query == mock_query


def test_apply_performance_filters_with_drought_tolerance_only_mid_range():
    """Test _apply_performance_filters with mid-range drought tolerance value."""
    # Create a mock database session
    db_session = Mock(spec=Session)

    # Create service instance
    service = CropSearchService(db_session)

    # Create crop filter request with mid-range value
    filter_request = CropFilterRequest(
        crop_type="wheat",
        min_drought_tolerance=60,
        page=1,
        page_size=20
    )

    # Create a mock query object
    mock_query = Mock()
    mock_query.filter.return_value = mock_query

    # Call the method under test
    result_query = service._apply_performance_filters(mock_query, filter_request)

    # Verify that filter was called once
    mock_query.filter.assert_called_once()

    # Verify the result query is the same as the mock (after chaining)
    assert result_query == mock_query


@pytest.mark.asyncio
async def test_search_performance():
    """Test that search_varieties meets performance requirement of <2s for complex queries."""
    import time
    from unittest.mock import Mock, MagicMock
    
    # Create a mock database session
    db_session = Mock(spec=Session)
    
    # Create service instance
    service = CropSearchService(db_session)
    
    # Create mock result objects that simulate CropFilteringAttributes
    import uuid
    mock_result_1 = Mock()
    mock_result_1.variety_id = uuid.uuid4()  # Use valid UUID
    mock_result_1.yield_stability_score = 85
    mock_result_1.drought_tolerance_score = 90
    mock_result_1.pest_resistance_traits = {"corn_borer": "resistant"}
    mock_result_1.disease_resistance_traits = {"gray_leaf_spot": "moderate"}
    mock_result_1.market_class_filters = {"market_class": "dent"}
    
    mock_result_2 = Mock()
    mock_result_2.variety_id = uuid.uuid4()  # Use valid UUID
    mock_result_2.yield_stability_score = 78
    mock_result_2.drought_tolerance_score = 82
    mock_result_2.pest_resistance_traits = {"rootworm": "resistant"}
    mock_result_2.disease_resistance_traits = {"gray_leaf_spot": "resistant"}
    mock_result_2.market_class_filters = {"market_class": "dent"}
    
    # Mock the database query chain to simulate complex query execution
    mock_query_result = Mock()
    mock_query_result.count.return_value = 150  # Simulate finding 150 results
    mock_query_result.offset.return_value = mock_query_result
    mock_query_result.limit.return_value = mock_query_result
    mock_query_result.all.return_value = [mock_result_1, mock_result_2]  # Return mock results
    # Ensure all filter operations return the same mock object
    mock_query_result.filter.return_value = mock_query_result
    mock_query_result.order_by.return_value = mock_query_result
    
    # Mock the database query method chain
    db_session.query.return_value = mock_query_result
    
    # Mock the commit method to avoid database operations
    db_session.commit = Mock()
    
    # Mock the filter combination query specifically
    def mock_query_side_effect(model):
        if hasattr(model, '__name__') and model.__name__ == 'FilterCombination':
            # Return a different mock for FilterCombination queries
            filter_combo_mock = Mock()
            filter_combo_mock.filter.return_value = filter_combo_mock
            filter_combo_mock.first.return_value = None  # No existing combination found
            return filter_combo_mock
        else:
            # Return the regular mock for other queries
            return mock_query_result
    
    db_session.query.side_effect = mock_query_side_effect
    
    # Mock the add method for adding new FilterCombination objects
    db_session.add = Mock()
    
    # Create a complex filter request to test performance
    complex_filter_request = CropFilterRequest(
        crop_type="corn",
        maturity_days_min=90,
        maturity_days_max=120,
        pest_resistance=[
            {"pest_name": "corn_borer", "min_resistance_level": "moderate"},
            {"pest_name": "rootworm", "min_resistance_level": "resistant"}
        ],
        disease_resistance=[
            {"disease_name": "gray_leaf_spot", "min_resistance_level": "moderate"}
        ],
        market_class={
            "market_class": "dent",
            "organic_certified": True,
            "non_gmo": True
        },
        min_yield_stability=75,
        min_drought_tolerance=80,
        sort_by="yield_stability",
        sort_order="desc",
        page=1,
        page_size=20
    )
    
    # Record start time
    start_time = time.time()
    
    # Execute the search
    result = await service.search_varieties(complex_filter_request)
    
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    
    # Verify performance requirement: response time should be < 2 seconds
    assert elapsed_time < 2.0, f"Search took {elapsed_time:.3f}s, which exceeds the 2s requirement"
    
    # Verify that the result has the expected structure
    assert hasattr(result, 'search_time_ms')
    assert result.search_time_ms < 2000, f"Reported search time {result.search_time_ms}ms exceeds 2000ms requirement"
    
    # Verify that database operations were called
    db_session.query.assert_called()
    db_session.commit.assert_called()


if __name__ == "__main__":
    pytest.main([__file__])

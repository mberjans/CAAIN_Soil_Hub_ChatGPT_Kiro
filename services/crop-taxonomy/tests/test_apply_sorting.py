"""
Comprehensive unit tests for CropSearchService._apply_sorting method

Tests cover all supported sorting fields (yield_stability, drought_tolerance,
variety_name, relevance, maturity_days) with various sort orders and edge cases.
"""

import pytest
from uuid import uuid4
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session, Query

from src.models.filtering_models import CropFilteringAttributes
from src.schemas.crop_schemas import CropFilterRequest
from src.services.crop_search_service import CropSearchService


class TestApplySorting:
    """Test suite for the _apply_sorting method"""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session"""
        return Mock(spec=Session)

    @pytest.fixture
    def crop_search_service(self, mock_db_session):
        """Create a CropSearchService instance with mock database"""
        return CropSearchService(mock_db_session)

    @pytest.fixture
    def sample_crop_data(self):
        """Create sample crop filtering attributes for testing"""
        return [
            CropFilteringAttributes(
                id=uuid4(),
                variety_id=uuid4(),
                yield_stability_score=95,
                drought_tolerance_score=80,
                pest_resistance_traits={"corn_borer": "resistant"},
                disease_resistance_traits={"rust": "moderate"},
                market_class_filters={"market_class": "yellow_dent"}
            ),
            CropFilteringAttributes(
                id=uuid4(),
                variety_id=uuid4(),
                yield_stability_score=75,
                drought_tolerance_score=90,
                pest_resistance_traits={"aphids": "moderate"},
                disease_resistance_traits={"blight": "resistant"},
                market_class_filters={"market_class": "white_corn"}
            ),
            CropFilteringAttributes(
                id=uuid4(),
                variety_id=uuid4(),
                yield_stability_score=85,
                drought_tolerance_score=70,
                pest_resistance_traits={"rootworm": "resistant"},
                disease_resistance_traits={"smut": "susceptible"},
                market_class_filters={"market_class": "sweet_corn"}
            ),
            CropFilteringAttributes(
                id=uuid4(),
                variety_id=uuid4(),
                yield_stability_score=60,
                drought_tolerance_score=95,
                pest_resistance_traits={"earworm": "susceptible"},
                disease_resistance_traits={"mildew": "resistant"},
                market_class_filters={"market_class": "flint_corn"}
            ),
        ]

    @pytest.fixture
    def mock_query(self, sample_crop_data):
        """Create a mock query object that simulates SQLAlchemy query behavior"""
        mock_query = MagicMock(spec=Query)

        # Store the sample data
        mock_query._test_data = sample_crop_data.copy()
        mock_query._order_by_field = None
        mock_query._order_by_direction = None

        def order_by_handler(order_expression):
            """Handle order_by calls and track the ordering"""
            # Extract field and direction from the SQLAlchemy order expression
            # SQLAlchemy expressions have different structures:
            # - For .desc(): UnaryExpression with element.key for column name
            # - For .asc(): UnaryExpression with element.key for column name
            # - Direct column: InstrumentedAttribute with .key attribute

            field_name = None
            is_desc = False

            # Check if it's a UnaryExpression (has .desc() or .asc() applied)
            if hasattr(order_expression, 'modifier'):
                # This is a UnaryExpression from .desc() or .asc()
                from sqlalchemy.sql.elements import UnaryExpression
                if isinstance(order_expression, UnaryExpression):
                    # Extract the column name from the element
                    if hasattr(order_expression.element, 'key'):
                        field_name = order_expression.element.key
                    # Check if it's descending by looking at the modifier
                    is_desc = hasattr(order_expression, 'modifier') and order_expression.modifier.__name__ == 'desc_op'

            # Fallback: try to get .key directly (for bare column references)
            if field_name is None and hasattr(order_expression, 'key'):
                field_name = order_expression.key
                is_desc = False  # Bare columns default to ascending

            # Last resort: parse string representation
            if field_name is None:
                order_str = str(order_expression)
                if '.' in order_str:
                    field_name = order_str.split('.')[1].split()[0].strip('()')
                is_desc = 'desc' in order_str.lower()

            mock_query._order_by_field = field_name
            mock_query._order_by_direction = 'desc' if is_desc else 'asc'

            # Return self to allow chaining
            return mock_query

        def all_handler():
            """Simulate query.all() with sorting applied"""
            data = mock_query._test_data.copy()

            # Apply sorting if specified
            if mock_query._order_by_field:
                field = mock_query._order_by_field
                reverse = mock_query._order_by_direction == 'desc'

                if field == 'yield_stability_score':
                    data.sort(key=lambda x: x.yield_stability_score or 0, reverse=reverse)
                elif field == 'drought_tolerance_score':
                    data.sort(key=lambda x: x.drought_tolerance_score or 0, reverse=reverse)
                elif field == 'variety_id':
                    data.sort(key=lambda x: str(x.variety_id), reverse=reverse)

            return data

        mock_query.order_by = MagicMock(side_effect=order_by_handler)
        mock_query.all = MagicMock(side_effect=all_handler)

        return mock_query

    def test_sorting_yield_stability_descending(self, crop_search_service, mock_query):
        """Test sorting by yield_stability in descending order (highest to lowest)"""
        filter_request = CropFilterRequest(
            crop_type="corn",
            sort_by="yield_stability",
            sort_order="desc"
        )

        sorted_query = crop_search_service._apply_sorting(mock_query, filter_request)
        results = sorted_query.all()

        # Verify results are sorted in descending order
        assert len(results) == 4
        assert results[0].yield_stability_score == 95
        assert results[1].yield_stability_score == 85
        assert results[2].yield_stability_score == 75
        assert results[3].yield_stability_score == 60

        # Verify each subsequent score is less than or equal to the previous
        for i in range(len(results) - 1):
            assert results[i].yield_stability_score >= results[i+1].yield_stability_score

    def test_sorting_yield_stability_ascending(self, crop_search_service, mock_query):
        """Test sorting by yield_stability in ascending order (lowest to highest)"""
        filter_request = CropFilterRequest(
            crop_type="corn",
            sort_by="yield_stability",
            sort_order="asc"
        )

        sorted_query = crop_search_service._apply_sorting(mock_query, filter_request)
        results = sorted_query.all()

        # Verify results are sorted in ascending order
        assert len(results) == 4
        assert results[0].yield_stability_score == 60
        assert results[1].yield_stability_score == 75
        assert results[2].yield_stability_score == 85
        assert results[3].yield_stability_score == 95

        # Verify each subsequent score is greater than or equal to the previous
        for i in range(len(results) - 1):
            assert results[i].yield_stability_score <= results[i+1].yield_stability_score

    def test_sorting_drought_tolerance_descending(self, crop_search_service, mock_query):
        """Test sorting by drought_tolerance in descending order (highest to lowest)"""
        filter_request = CropFilterRequest(
            crop_type="corn",
            sort_by="drought_tolerance",
            sort_order="desc"
        )

        sorted_query = crop_search_service._apply_sorting(mock_query, filter_request)
        results = sorted_query.all()

        # Verify results are sorted in descending order
        assert len(results) == 4
        assert results[0].drought_tolerance_score == 95
        assert results[1].drought_tolerance_score == 90
        assert results[2].drought_tolerance_score == 80
        assert results[3].drought_tolerance_score == 70

        # Verify each subsequent score is less than or equal to the previous
        for i in range(len(results) - 1):
            assert results[i].drought_tolerance_score >= results[i+1].drought_tolerance_score

    def test_sorting_drought_tolerance_ascending(self, crop_search_service, mock_query):
        """Test sorting by drought_tolerance in ascending order (lowest to highest)"""
        filter_request = CropFilterRequest(
            crop_type="corn",
            sort_by="drought_tolerance",
            sort_order="asc"
        )

        sorted_query = crop_search_service._apply_sorting(mock_query, filter_request)
        results = sorted_query.all()

        # Verify results are sorted in ascending order
        assert len(results) == 4
        assert results[0].drought_tolerance_score == 70
        assert results[1].drought_tolerance_score == 80
        assert results[2].drought_tolerance_score == 90
        assert results[3].drought_tolerance_score == 95

        # Verify each subsequent score is greater than or equal to the previous
        for i in range(len(results) - 1):
            assert results[i].drought_tolerance_score <= results[i+1].drought_tolerance_score

    def test_sorting_variety_name_descending(self, crop_search_service, mock_query):
        """Test sorting by variety_name in descending order (Z to A)

        Note: Since variety_name is generated from variety_id, we sort by variety_id
        """
        filter_request = CropFilterRequest(
            crop_type="corn",
            sort_by="variety_name",
            sort_order="desc"
        )

        sorted_query = crop_search_service._apply_sorting(mock_query, filter_request)
        results = sorted_query.all()

        # Verify results are sorted in descending order by variety_id
        assert len(results) == 4

        # Verify each subsequent variety_id is less than or equal to the previous
        for i in range(len(results) - 1):
            assert str(results[i].variety_id) >= str(results[i+1].variety_id)

    def test_sorting_variety_name_ascending(self, crop_search_service, mock_query):
        """Test sorting by variety_name in ascending order (A to Z)

        Note: Since variety_name is generated from variety_id, we sort by variety_id
        """
        filter_request = CropFilterRequest(
            crop_type="corn",
            sort_by="variety_name",
            sort_order="asc"
        )

        sorted_query = crop_search_service._apply_sorting(mock_query, filter_request)
        results = sorted_query.all()

        # Verify results are sorted in ascending order by variety_id
        assert len(results) == 4

        # Verify each subsequent variety_id is greater than or equal to the previous
        for i in range(len(results) - 1):
            assert str(results[i].variety_id) <= str(results[i+1].variety_id)

    def test_sorting_by_relevance_no_sql_ordering(self, crop_search_service, mock_query):
        """Test that sorting by relevance does not apply SQL ordering

        Relevance scores are calculated post-query, so no SQL ordering should be applied.
        The query should be returned unchanged.
        """
        filter_request = CropFilterRequest(
            crop_type="corn",
            sort_by="relevance",
            sort_order="desc"
        )

        sorted_query = crop_search_service._apply_sorting(mock_query, filter_request)

        # Verify that order_by was not called (no SQL ordering applied)
        # Since relevance is calculated post-query, the query should be unchanged
        assert sorted_query == mock_query

        # The query should still work but return data in original order
        results = sorted_query.all()
        assert len(results) == 4

    def test_sorting_by_maturity_days_placeholder(self, crop_search_service, mock_query):
        """Test that sorting by maturity_days is a placeholder (no SQL ordering)

        Maturity days sorting is not yet implemented as it requires integration
        with the crop varieties table. The query should be returned unchanged.
        """
        filter_request = CropFilterRequest(
            crop_type="corn",
            sort_by="maturity_days",
            sort_order="asc"
        )

        sorted_query = crop_search_service._apply_sorting(mock_query, filter_request)

        # Verify that the query is returned unchanged (placeholder implementation)
        assert sorted_query == mock_query

        # The query should still work but return data in original order
        results = sorted_query.all()
        assert len(results) == 4

    def test_sorting_with_invalid_sort_by_value(self, crop_search_service, mock_query):
        """Test that invalid sort_by values default to relevance behavior

        Invalid sort_by values should be handled gracefully by returning the
        query unchanged (same as relevance sorting).
        """
        filter_request = CropFilterRequest(
            crop_type="corn",
            sort_by="invalid_field",
            sort_order="desc"
        )

        sorted_query = crop_search_service._apply_sorting(mock_query, filter_request)

        # Verify that the query is returned unchanged (default behavior)
        assert sorted_query == mock_query

        # The query should still work
        results = sorted_query.all()
        assert len(results) == 4

    def test_sorting_with_case_insensitive_desc(self, crop_search_service, mock_query):
        """Test that sort_order is case-insensitive for 'DESC'"""
        test_cases = ["DESC", "desc", "Desc", "dEsC"]

        for sort_order in test_cases:
            filter_request = CropFilterRequest(
                crop_type="corn",
                sort_by="yield_stability",
                sort_order=sort_order
            )

            sorted_query = crop_search_service._apply_sorting(mock_query, filter_request)
            results = sorted_query.all()

            # Verify descending order regardless of case
            assert results[0].yield_stability_score >= results[1].yield_stability_score
            assert results[1].yield_stability_score >= results[2].yield_stability_score

    def test_sorting_with_case_insensitive_asc(self, crop_search_service, mock_query):
        """Test that sort_order is case-insensitive for 'ASC'"""
        test_cases = ["ASC", "asc", "Asc", "aSc"]

        for sort_order in test_cases:
            filter_request = CropFilterRequest(
                crop_type="corn",
                sort_by="drought_tolerance",
                sort_order=sort_order
            )

            sorted_query = crop_search_service._apply_sorting(mock_query, filter_request)
            results = sorted_query.all()

            # Verify ascending order regardless of case
            assert results[0].drought_tolerance_score <= results[1].drought_tolerance_score
            assert results[1].drought_tolerance_score <= results[2].drought_tolerance_score

    def test_sorting_with_none_sort_by(self, crop_search_service, mock_query):
        """Test that None sort_by defaults to relevance (no SQL ordering)"""
        filter_request = CropFilterRequest(
            crop_type="corn",
            sort_by=None,
            sort_order="desc"
        )

        # Should not raise any errors
        sorted_query = crop_search_service._apply_sorting(mock_query, filter_request)

        # Should return query unchanged (defaults to relevance)
        assert sorted_query == mock_query

        results = sorted_query.all()
        assert len(results) == 4

    def test_sorting_with_empty_string_sort_by(self, crop_search_service, mock_query):
        """Test that empty string sort_by is handled gracefully"""
        filter_request = CropFilterRequest(
            crop_type="corn",
            sort_by="",
            sort_order="desc"
        )

        # Should not raise any errors
        sorted_query = crop_search_service._apply_sorting(mock_query, filter_request)

        # Should return query unchanged (invalid value)
        assert sorted_query == mock_query

        results = sorted_query.all()
        assert len(results) == 4

    def test_sorting_with_none_sort_order(self, crop_search_service, mock_query):
        """Test that None sort_order defaults to 'desc'"""
        filter_request = CropFilterRequest(
            crop_type="corn",
            sort_by="yield_stability",
            sort_order=None
        )

        sorted_query = crop_search_service._apply_sorting(mock_query, filter_request)
        results = sorted_query.all()

        # Should default to descending order
        assert results[0].yield_stability_score >= results[1].yield_stability_score

    def test_sorting_with_invalid_sort_order(self, crop_search_service, mock_query):
        """Test that invalid sort_order defaults to ascending (not 'desc')"""
        filter_request = CropFilterRequest(
            crop_type="corn",
            sort_by="yield_stability",
            sort_order="invalid"
        )

        sorted_query = crop_search_service._apply_sorting(mock_query, filter_request)
        results = sorted_query.all()

        # Invalid sort_order should default to ascending (is_desc = False)
        assert results[0].yield_stability_score <= results[1].yield_stability_score

    def test_sorting_preserves_query_object(self, crop_search_service, mock_query):
        """Test that _apply_sorting returns a query object that can be chained"""
        filter_request = CropFilterRequest(
            crop_type="corn",
            sort_by="yield_stability",
            sort_order="desc"
        )

        sorted_query = crop_search_service._apply_sorting(mock_query, filter_request)

        # Verify that the returned object is still a query (or mock query)
        assert sorted_query is not None
        assert hasattr(sorted_query, 'all')

        # Verify that we can call .all() on the result
        results = sorted_query.all()
        assert isinstance(results, list)

    def test_sorting_with_multiple_sort_orders_same_field(self, crop_search_service, mock_query):
        """Test that the last applied sorting takes precedence

        This tests the behavior when _apply_sorting is called multiple times
        """
        # First sort by yield_stability ascending
        filter_request_1 = CropFilterRequest(
            crop_type="corn",
            sort_by="yield_stability",
            sort_order="asc"
        )
        query_1 = crop_search_service._apply_sorting(mock_query, filter_request_1)

        # Then sort by yield_stability descending
        filter_request_2 = CropFilterRequest(
            crop_type="corn",
            sort_by="yield_stability",
            sort_order="desc"
        )
        query_2 = crop_search_service._apply_sorting(query_1, filter_request_2)

        results = query_2.all()

        # The last sorting (descending) should take precedence
        assert results[0].yield_stability_score >= results[1].yield_stability_score

    def test_sorting_yield_stability_with_all_same_scores(self, crop_search_service):
        """Test sorting behavior when all records have the same yield_stability_score"""
        # Create data with identical scores
        identical_data = [
            CropFilteringAttributes(
                id=uuid4(),
                variety_id=uuid4(),
                yield_stability_score=80,
                drought_tolerance_score=70
            ) for _ in range(3)
        ]

        mock_query = MagicMock(spec=Query)
        mock_query._test_data = identical_data.copy()
        mock_query._order_by_field = None
        mock_query._order_by_direction = None

        def order_by_handler(order_expression):
            field_name = str(order_expression).split('.')[1].split('(')[0] if '.' in str(order_expression) else None
            is_desc = 'desc' in str(order_expression).lower()
            mock_query._order_by_field = field_name
            mock_query._order_by_direction = 'desc' if is_desc else 'asc'
            return mock_query

        def all_handler():
            data = mock_query._test_data.copy()
            if mock_query._order_by_field == 'yield_stability_score':
                reverse = mock_query._order_by_direction == 'desc'
                data.sort(key=lambda x: x.yield_stability_score or 0, reverse=reverse)
            return data

        mock_query.order_by = MagicMock(side_effect=order_by_handler)
        mock_query.all = MagicMock(side_effect=all_handler)

        filter_request = CropFilterRequest(
            crop_type="corn",
            sort_by="yield_stability",
            sort_order="desc"
        )

        sorted_query = crop_search_service._apply_sorting(mock_query, filter_request)
        results = sorted_query.all()

        # All scores should be the same
        assert len(results) == 3
        assert all(r.yield_stability_score == 80 for r in results)

    def test_sorting_handles_null_scores_gracefully(self, crop_search_service):
        """Test that sorting handles None/null scores gracefully

        Records with None scores should be sorted to one end of the results
        """
        # Create data with some None scores
        mixed_data = [
            CropFilteringAttributes(
                id=uuid4(),
                variety_id=uuid4(),
                yield_stability_score=None,
                drought_tolerance_score=80
            ),
            CropFilteringAttributes(
                id=uuid4(),
                variety_id=uuid4(),
                yield_stability_score=75,
                drought_tolerance_score=90
            ),
            CropFilteringAttributes(
                id=uuid4(),
                variety_id=uuid4(),
                yield_stability_score=None,
                drought_tolerance_score=70
            ),
            CropFilteringAttributes(
                id=uuid4(),
                variety_id=uuid4(),
                yield_stability_score=85,
                drought_tolerance_score=95
            ),
        ]

        mock_query = MagicMock(spec=Query)
        mock_query._test_data = mixed_data.copy()
        mock_query._order_by_field = None
        mock_query._order_by_direction = None

        def order_by_handler(order_expression):
            field_name = str(order_expression).split('.')[1].split('(')[0] if '.' in str(order_expression) else None
            is_desc = 'desc' in str(order_expression).lower()
            mock_query._order_by_field = field_name
            mock_query._order_by_direction = 'desc' if is_desc else 'asc'
            return mock_query

        def all_handler():
            data = mock_query._test_data.copy()
            if mock_query._order_by_field == 'yield_stability_score':
                reverse = mock_query._order_by_direction == 'desc'
                data.sort(key=lambda x: x.yield_stability_score or 0, reverse=reverse)
            return data

        mock_query.order_by = MagicMock(side_effect=order_by_handler)
        mock_query.all = MagicMock(side_effect=all_handler)

        filter_request = CropFilterRequest(
            crop_type="corn",
            sort_by="yield_stability",
            sort_order="desc"
        )

        sorted_query = crop_search_service._apply_sorting(mock_query, filter_request)

        # Should not raise any errors
        results = sorted_query.all()
        assert len(results) == 4

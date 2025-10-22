"""
Comprehensive unit tests for CropSearchService methods:
- _build_variety_result
- _calculate_relevance
- _log_filter_combination

These tests verify that variety results are correctly built with proper relevance
scoring and filter combination logging for optimization tracking.
"""

import pytest
import hashlib
import json
from uuid import uuid4, UUID
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.orm import Session

from src.models.filtering_models import CropFilteringAttributes, FilterCombination
from src.schemas.crop_schemas import CropFilterRequest, PestResistanceFilter, VarietyResult
from src.services.crop_search_service import CropSearchService


class TestBuildVarietyResult:
    """Test suite for the _build_variety_result method"""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session"""
        return Mock(spec=Session)

    @pytest.fixture
    def crop_search_service(self, mock_db_session):
        """Create a CropSearchService instance with mock database"""
        return CropSearchService(mock_db_session)

    def test_build_variety_result_with_all_fields(self, crop_search_service):
        """Test _build_variety_result with complete CropFilteringAttributes data"""
        # Create test data
        variety_id = uuid4()
        result = CropFilteringAttributes(
            id=uuid4(),
            variety_id=variety_id,
            yield_stability_score=90,
            drought_tolerance_score=85,
            pest_resistance_traits={"corn_borer": "resistant", "aphids": "moderate"},
            disease_resistance_traits={"rust": "resistant", "blight": "moderate"},
            market_class_filters={"market_class": "yellow_dent", "organic_certified": True}
        )

        filter_request = CropFilterRequest(
            crop_type="corn",
            page=1,
            page_size=20
        )

        # Call the method
        variety_result = crop_search_service._build_variety_result(result, filter_request)

        # Assertions
        assert variety_result is not None
        assert hasattr(variety_result, 'variety_id')
        assert variety_result.variety_id == variety_id
        assert variety_result.variety_name == f"Variety {str(variety_id)[:8]}"
        assert variety_result.maturity_days == 100  # Placeholder value
        assert variety_result.yield_potential == 180.0  # Placeholder value
        assert variety_result.pest_resistance_summary == {"corn_borer": "resistant", "aphids": "moderate"}
        assert variety_result.disease_resistance_summary == {"rust": "resistant", "blight": "moderate"}
        assert variety_result.market_class == "yellow_dent"
        assert 0 <= variety_result.relevance_score <= 1.0

    def test_build_variety_result_with_minimal_fields(self, crop_search_service):
        """Test _build_variety_result with minimal CropFilteringAttributes data"""
        variety_id = uuid4()
        result = CropFilteringAttributes(
            id=uuid4(),
            variety_id=variety_id,
            yield_stability_score=None,
            drought_tolerance_score=None,
            pest_resistance_traits=None,
            disease_resistance_traits=None,
            market_class_filters=None
        )

        filter_request = CropFilterRequest(
            crop_type="corn",
            page=1,
            page_size=20
        )

        # Call the method
        variety_result = crop_search_service._build_variety_result(result, filter_request)

        # Assertions
        assert variety_result is not None
        assert hasattr(variety_result, 'variety_id')
        assert variety_result.variety_id == variety_id
        assert variety_result.variety_name == f"Variety {str(variety_id)[:8]}"
        assert variety_result.pest_resistance_summary == {}
        assert variety_result.disease_resistance_summary == {}
        assert variety_result.market_class is None
        assert variety_result.relevance_score == 0.5  # Base score only

    def test_build_variety_result_with_empty_dicts(self, crop_search_service):
        """Test _build_variety_result handles empty dictionaries gracefully"""
        variety_id = uuid4()
        result = CropFilteringAttributes(
            id=uuid4(),
            variety_id=variety_id,
            yield_stability_score=75,
            drought_tolerance_score=80,
            pest_resistance_traits={},
            disease_resistance_traits={},
            market_class_filters={}
        )

        filter_request = CropFilterRequest(
            crop_type="corn",
            page=1,
            page_size=20
        )

        # Call the method
        variety_result = crop_search_service._build_variety_result(result, filter_request)

        # Assertions
        assert variety_result.pest_resistance_summary == {}
        assert variety_result.disease_resistance_summary == {}
        assert variety_result.market_class is None

    def test_build_variety_result_with_no_market_class_key(self, crop_search_service):
        """Test _build_variety_result when market_class_filters exists but has no market_class key"""
        variety_id = uuid4()
        result = CropFilteringAttributes(
            id=uuid4(),
            variety_id=variety_id,
            yield_stability_score=80,
            drought_tolerance_score=70,
            pest_resistance_traits={"rootworm": "resistant"},
            disease_resistance_traits={"smut": "moderate"},
            market_class_filters={"organic_certified": True, "non_gmo": False}
        )

        filter_request = CropFilterRequest(
            crop_type="corn",
            page=1,
            page_size=20
        )

        # Call the method
        variety_result = crop_search_service._build_variety_result(result, filter_request)

        # Assertions
        assert variety_result.market_class is None

    def test_build_variety_result_calls_calculate_relevance(self, crop_search_service):
        """Test that _build_variety_result calls _calculate_relevance"""
        variety_id = uuid4()
        result = CropFilteringAttributes(
            id=uuid4(),
            variety_id=variety_id,
            yield_stability_score=95,
            drought_tolerance_score=90,
            pest_resistance_traits={"corn_borer": "resistant"},
            disease_resistance_traits={"rust": "resistant"},
            market_class_filters={"market_class": "white_corn"}
        )

        filter_request = CropFilterRequest(
            crop_type="corn",
            page=1,
            page_size=20
        )

        # Mock _calculate_relevance to verify it's called
        with patch.object(crop_search_service, '_calculate_relevance', return_value=0.85) as mock_calc:
            variety_result = crop_search_service._build_variety_result(result, filter_request)

            # Verify _calculate_relevance was called with correct arguments
            mock_calc.assert_called_once_with(result, filter_request)
            assert variety_result.relevance_score == 0.85

    def test_build_variety_result_variety_name_generation(self, crop_search_service):
        """Test that variety_name is generated correctly from variety_id"""
        variety_id = uuid4()
        result = CropFilteringAttributes(
            id=uuid4(),
            variety_id=variety_id,
            yield_stability_score=80,
            drought_tolerance_score=75
        )

        filter_request = CropFilterRequest(
            crop_type="corn",
            page=1,
            page_size=20
        )

        # Call the method
        variety_result = crop_search_service._build_variety_result(result, filter_request)

        # Verify variety_name format
        expected_name = f"Variety {str(variety_id)[:8]}"
        assert variety_result.variety_name == expected_name
        assert len(variety_result.variety_name) == len("Variety ") + 8


class TestCalculateRelevance:
    """Test suite for the _calculate_relevance method"""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session"""
        return Mock(spec=Session)

    @pytest.fixture
    def crop_search_service(self, mock_db_session):
        """Create a CropSearchService instance with mock database"""
        return CropSearchService(mock_db_session)

    def test_calculate_relevance_base_score_only(self, crop_search_service):
        """Test relevance calculation with no performance scores (base score only)"""
        result = CropFilteringAttributes(
            id=uuid4(),
            variety_id=uuid4(),
            yield_stability_score=None,
            drought_tolerance_score=None
        )

        filter_request = CropFilterRequest(
            crop_type="corn",
            page=1,
            page_size=20
        )

        # Call the method
        relevance = crop_search_service._calculate_relevance(result, filter_request)

        # Should return base score of 0.5
        assert relevance == 0.5

    def test_calculate_relevance_with_yield_stability_only(self, crop_search_service):
        """Test relevance calculation with only yield_stability_score"""
        result = CropFilteringAttributes(
            id=uuid4(),
            variety_id=uuid4(),
            yield_stability_score=80,  # 80/100 = 0.8, boost = 0.8 * 0.25 = 0.2
            drought_tolerance_score=None
        )

        filter_request = CropFilterRequest(
            crop_type="corn",
            page=1,
            page_size=20
        )

        # Call the method
        relevance = crop_search_service._calculate_relevance(result, filter_request)

        # Expected: 0.5 (base) + 0.2 (yield boost) = 0.7
        assert relevance == 0.7

    def test_calculate_relevance_with_drought_tolerance_only(self, crop_search_service):
        """Test relevance calculation with only drought_tolerance_score"""
        result = CropFilteringAttributes(
            id=uuid4(),
            variety_id=uuid4(),
            yield_stability_score=None,
            drought_tolerance_score=60  # 60/100 = 0.6, boost = 0.6 * 0.25 = 0.15
        )

        filter_request = CropFilterRequest(
            crop_type="corn",
            page=1,
            page_size=20
        )

        # Call the method
        relevance = crop_search_service._calculate_relevance(result, filter_request)

        # Expected: 0.5 (base) + 0.15 (drought boost) = 0.65
        assert relevance == 0.65

    def test_calculate_relevance_with_both_scores(self, crop_search_service):
        """Test relevance calculation with both performance scores"""
        result = CropFilteringAttributes(
            id=uuid4(),
            variety_id=uuid4(),
            yield_stability_score=100,  # 100/100 = 1.0, boost = 1.0 * 0.25 = 0.25
            drought_tolerance_score=100  # 100/100 = 1.0, boost = 1.0 * 0.25 = 0.25
        )

        filter_request = CropFilterRequest(
            crop_type="corn",
            page=1,
            page_size=20
        )

        # Call the method
        relevance = crop_search_service._calculate_relevance(result, filter_request)

        # Expected: 0.5 (base) + 0.25 (yield) + 0.25 (drought) = 1.0 (capped)
        assert relevance == 1.0

    def test_calculate_relevance_capped_at_one(self, crop_search_service):
        """Test that relevance score is capped at 1.0"""
        result = CropFilteringAttributes(
            id=uuid4(),
            variety_id=uuid4(),
            yield_stability_score=100,
            drought_tolerance_score=100
        )

        filter_request = CropFilterRequest(
            crop_type="corn",
            page=1,
            page_size=20
        )

        # Call the method
        relevance = crop_search_service._calculate_relevance(result, filter_request)

        # Should be capped at 1.0
        assert relevance == 1.0
        assert relevance <= 1.0

    def test_calculate_relevance_with_zero_scores(self, crop_search_service):
        """Test relevance calculation with zero performance scores"""
        result = CropFilteringAttributes(
            id=uuid4(),
            variety_id=uuid4(),
            yield_stability_score=0,
            drought_tolerance_score=0
        )

        filter_request = CropFilterRequest(
            crop_type="corn",
            page=1,
            page_size=20
        )

        # Call the method
        relevance = crop_search_service._calculate_relevance(result, filter_request)

        # Expected: 0.5 (base) + 0 + 0 = 0.5
        # Note: Zero is falsy, so it won't add any boost
        assert relevance == 0.5

    def test_calculate_relevance_with_partial_scores(self, crop_search_service):
        """Test relevance calculation with various partial scores"""
        test_cases = [
            # (yield_score, drought_score, expected_relevance)
            (50, 50, 0.5 + (50/100)*0.25 + (50/100)*0.25),  # 0.75
            (25, 75, 0.5 + (25/100)*0.25 + (75/100)*0.25),  # 0.75
            (90, 10, 0.5 + (90/100)*0.25 + (10/100)*0.25),  # 0.75
            (100, 0, 0.5 + (100/100)*0.25),  # 0.75 (0 is falsy)
        ]

        for yield_score, drought_score, expected in test_cases:
            result = CropFilteringAttributes(
                id=uuid4(),
                variety_id=uuid4(),
                yield_stability_score=yield_score if yield_score > 0 else None,
                drought_tolerance_score=drought_score if drought_score > 0 else None
            )

            filter_request = CropFilterRequest(
                crop_type="corn",
                page=1,
                page_size=20
            )

            relevance = crop_search_service._calculate_relevance(result, filter_request)

            # Use pytest.approx for floating point comparison
            assert relevance == pytest.approx(expected, rel=1e-9)

    def test_calculate_relevance_always_returns_valid_range(self, crop_search_service):
        """Test that relevance score is always between 0 and 1"""
        # Test with various combinations
        test_scores = [
            (None, None),
            (0, 0),
            (50, 50),
            (100, 100),
            (25, 75),
            (90, 10),
        ]

        for yield_score, drought_score in test_scores:
            result = CropFilteringAttributes(
                id=uuid4(),
                variety_id=uuid4(),
                yield_stability_score=yield_score,
                drought_tolerance_score=drought_score
            )

            filter_request = CropFilterRequest(
                crop_type="corn",
                page=1,
                page_size=20
            )

            relevance = crop_search_service._calculate_relevance(result, filter_request)

            # Verify it's in valid range
            assert 0 <= relevance <= 1.0, f"Relevance {relevance} out of range for scores {yield_score}, {drought_score}"


class TestLogFilterCombination:
    """Test suite for the _log_filter_combination method"""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session with proper query behavior"""
        mock_session = Mock(spec=Session)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        return mock_session

    @pytest.fixture
    def crop_search_service(self, mock_db_session):
        """Create a CropSearchService instance with mock database"""
        return CropSearchService(mock_db_session)

    def test_log_filter_combination_creates_new_entry(self, crop_search_service, mock_db_session):
        """Test that _log_filter_combination creates a new FilterCombination entry"""
        filter_request = CropFilterRequest(
            crop_type="corn",
            min_yield_stability=80,
            page=1,
            page_size=20
        )

        # Mock that no existing combination is found
        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        # Call the method
        crop_search_service._log_filter_combination(filter_request, result_count=15, response_time_ms=250)

        # Verify query was called to check for existing combination
        mock_db_session.query.assert_called_once()
        # Verify the argument is a FilterCombination class (regardless of module path)
        call_args = mock_db_session.query.call_args[0][0]
        assert call_args.__name__ == 'FilterCombination'

        # Verify a new FilterCombination was added
        mock_db_session.add.assert_called_once()
        added_combo = mock_db_session.add.call_args[0][0]

        # Verify it's a FilterCombination object (check attributes instead of isinstance)
        assert hasattr(added_combo, 'combination_hash')
        assert hasattr(added_combo, 'usage_count')
        assert hasattr(added_combo, 'filters')
        assert added_combo.usage_count == 1
        assert added_combo.avg_result_count == 15
        assert added_combo.avg_response_time_ms == 250
        assert added_combo.combination_hash is not None

        # Verify commit was called
        mock_db_session.commit.assert_called_once()

    def test_log_filter_combination_updates_existing_entry(self, crop_search_service, mock_db_session):
        """Test that _log_filter_combination updates an existing FilterCombination"""
        filter_request = CropFilterRequest(
            crop_type="corn",
            min_yield_stability=80,
            page=1,
            page_size=20
        )

        # Create a mock existing combination
        existing_combo = FilterCombination(
            id=uuid4(),
            combination_hash="test_hash_123",
            filters={"crop_type": "corn", "min_yield_stability": 80},
            usage_count=5,
            avg_result_count=20,
            avg_response_time_ms=300
        )

        # Mock that an existing combination is found
        mock_db_session.query.return_value.filter.return_value.first.return_value = existing_combo

        # Call the method
        crop_search_service._log_filter_combination(filter_request, result_count=10, response_time_ms=200)

        # Verify usage_count was incremented
        assert existing_combo.usage_count == 6

        # Verify averages were updated
        # avg_result_count = (20 + 10) // 2 = 15
        assert existing_combo.avg_result_count == 15

        # avg_response_time_ms = (300 + 200) // 2 = 250
        assert existing_combo.avg_response_time_ms == 250

        # Verify no new entry was added
        mock_db_session.add.assert_not_called()

        # Verify commit was called
        mock_db_session.commit.assert_called_once()

    def test_log_filter_combination_excludes_pagination_and_sorting(self, crop_search_service, mock_db_session):
        """Test that pagination and sorting parameters are excluded from filter hash"""
        filter_request = CropFilterRequest(
            crop_type="corn",
            min_yield_stability=80,
            page=5,  # Should be excluded
            page_size=50,  # Should be excluded
            sort_by="yield_stability",  # Should be excluded
            sort_order="desc"  # Should be excluded
        )

        # Mock that no existing combination is found
        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        # Call the method
        crop_search_service._log_filter_combination(filter_request, result_count=15, response_time_ms=250)

        # Get the added FilterCombination
        added_combo = mock_db_session.add.call_args[0][0]

        # Verify the filters dict doesn't include pagination/sorting
        assert 'page' not in added_combo.filters
        assert 'page_size' not in added_combo.filters
        assert 'sort_by' not in added_combo.filters
        assert 'sort_order' not in added_combo.filters

        # Verify it does include the actual filters
        assert 'crop_type' in added_combo.filters
        assert 'min_yield_stability' in added_combo.filters

    def test_log_filter_combination_generates_consistent_hash(self, crop_search_service, mock_db_session):
        """Test that the same filters generate the same hash"""
        filter_request_1 = CropFilterRequest(
            crop_type="corn",
            min_yield_stability=80,
            page=1,
            page_size=20
        )

        filter_request_2 = CropFilterRequest(
            crop_type="corn",
            min_yield_stability=80,
            page=10,  # Different pagination
            page_size=50  # Different pagination
        )

        # Mock that no existing combination is found
        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        # Call the method with first request
        crop_search_service._log_filter_combination(filter_request_1, result_count=15, response_time_ms=250)
        combo_1 = mock_db_session.add.call_args[0][0]
        hash_1 = combo_1.combination_hash

        # Reset mocks
        mock_db_session.reset_mock()
        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        # Call the method with second request
        crop_search_service._log_filter_combination(filter_request_2, result_count=20, response_time_ms=300)
        combo_2 = mock_db_session.add.call_args[0][0]
        hash_2 = combo_2.combination_hash

        # Both should generate the same hash (pagination excluded)
        assert hash_1 == hash_2

    def test_log_filter_combination_with_complex_filters(self, crop_search_service, mock_db_session):
        """Test _log_filter_combination with complex filter combinations"""
        from src.schemas.crop_schemas import PestResistanceFilter, DiseaseResistanceFilter, MarketClassFilter

        filter_request = CropFilterRequest(
            crop_type="corn",
            min_yield_stability=85,
            min_drought_tolerance=70,
            pest_resistance=[
                PestResistanceFilter(pest_name="corn_borer", min_resistance_level="resistant")
            ],
            disease_resistance=[
                DiseaseResistanceFilter(disease_name="rust", min_resistance_level="moderate")
            ],
            market_class=MarketClassFilter(market_class="yellow_dent", organic_certified=True),
            page=1,
            page_size=20
        )

        # Mock that no existing combination is found
        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        # Call the method
        crop_search_service._log_filter_combination(filter_request, result_count=8, response_time_ms=500)

        # Get the added FilterCombination
        added_combo = mock_db_session.add.call_args[0][0]

        # Verify complex filters are included
        assert 'crop_type' in added_combo.filters
        assert 'min_yield_stability' in added_combo.filters
        assert 'min_drought_tolerance' in added_combo.filters
        assert 'pest_resistance' in added_combo.filters
        assert 'disease_resistance' in added_combo.filters
        assert 'market_class' in added_combo.filters

        # Verify the hash is generated
        assert len(added_combo.combination_hash) == 64  # SHA256 hex digest length

    def test_log_filter_combination_excludes_none_values(self, crop_search_service, mock_db_session):
        """Test that None values are excluded from the filter combination"""
        filter_request = CropFilterRequest(
            crop_type="corn",
            min_yield_stability=None,  # Should be excluded
            min_drought_tolerance=80,
            page=1,
            page_size=20
        )

        # Mock that no existing combination is found
        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        # Call the method
        crop_search_service._log_filter_combination(filter_request, result_count=15, response_time_ms=250)

        # Get the added FilterCombination
        added_combo = mock_db_session.add.call_args[0][0]

        # Verify None values are excluded
        assert 'min_yield_stability' not in added_combo.filters
        assert 'min_drought_tolerance' in added_combo.filters

    def test_log_filter_combination_average_calculation_with_multiple_updates(self, crop_search_service, mock_db_session):
        """Test that averages are calculated correctly over multiple updates"""
        filter_request = CropFilterRequest(
            crop_type="corn",
            min_yield_stability=80,
            page=1,
            page_size=20
        )

        # Create a mock existing combination with initial values
        existing_combo = FilterCombination(
            id=uuid4(),
            combination_hash="test_hash_123",
            filters={"crop_type": "corn", "min_yield_stability": 80},
            usage_count=1,
            avg_result_count=30,
            avg_response_time_ms=400
        )

        # Mock that an existing combination is found
        mock_db_session.query.return_value.filter.return_value.first.return_value = existing_combo

        # First update: result_count=20, response_time=200
        crop_search_service._log_filter_combination(filter_request, result_count=20, response_time_ms=200)

        # Verify first update
        assert existing_combo.usage_count == 2
        assert existing_combo.avg_result_count == (30 + 20) // 2  # 25
        assert existing_combo.avg_response_time_ms == (400 + 200) // 2  # 300

        # Second update: result_count=10, response_time=100
        crop_search_service._log_filter_combination(filter_request, result_count=10, response_time_ms=100)

        # Verify second update
        assert existing_combo.usage_count == 3
        assert existing_combo.avg_result_count == (25 + 10) // 2  # 17
        assert existing_combo.avg_response_time_ms == (300 + 100) // 2  # 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

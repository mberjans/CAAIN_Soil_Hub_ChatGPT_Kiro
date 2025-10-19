"""
Comprehensive unit tests for fertilizer comparison service.

Tests cover:
- Weighted scoring algorithm
- TOPSIS method
- AHP analysis
- Trade-off analysis
- Edge cases and error handling
- Input validation
"""

import pytest
import asyncio
from uuid import uuid4
from datetime import datetime

from ..services.comparison_service import FertilizerComparisonService
from ..models.comparison_models import (
    ComparisonRequest, FertilizerOption, ScoringCriteria, NutrientContent,
    ScoringMethod, ScoringDimension, ComparisonCategory
)


class TestFertilizerComparisonService:
    """Test suite for FertilizerComparisonService."""

    @pytest.fixture
    def comparison_service(self):
        """Create comparison service instance."""
        return FertilizerComparisonService()

    @pytest.fixture
    def sample_fertilizers(self):
        """Create sample fertilizers for testing."""
        return [
            FertilizerOption(
                fertilizer_id="urea-46-0-0",
                fertilizer_name="Urea 46-0-0",
                fertilizer_type="synthetic",
                category=ComparisonCategory.SYNTHETIC,
                nutrient_content=NutrientContent(
                    nitrogen=46.0,
                    phosphorus=0.0,
                    potassium=0.0
                ),
                price_per_unit=400.0,
                unit_type="ton",
                application_rate=0.5,
                organic_certified=False,
                slow_release=False,
                greenhouse_gas_emission_factor=1.3,
                runoff_potential=0.6,
                leaching_potential=0.7,
                application_method="broadcast",
                equipment_required=["spreader"],
                application_complexity=0.3,
                storage_requirements="standard",
                regional_availability=0.9,
                soil_health_benefit=0.3
            ),
            FertilizerOption(
                fertilizer_id="dap-18-46-0",
                fertilizer_name="DAP 18-46-0",
                fertilizer_type="synthetic",
                category=ComparisonCategory.SYNTHETIC,
                nutrient_content=NutrientContent(
                    nitrogen=18.0,
                    phosphorus=46.0,
                    potassium=0.0
                ),
                price_per_unit=500.0,
                unit_type="ton",
                application_rate=0.4,
                organic_certified=False,
                slow_release=False,
                greenhouse_gas_emission_factor=1.2,
                runoff_potential=0.5,
                leaching_potential=0.4,
                application_method="broadcast",
                equipment_required=["spreader"],
                application_complexity=0.3,
                storage_requirements="standard",
                regional_availability=0.9,
                soil_health_benefit=0.3
            ),
            FertilizerOption(
                fertilizer_id="compost-2-1-1",
                fertilizer_name="Premium Compost 2-1-1",
                fertilizer_type="organic",
                category=ComparisonCategory.ORGANIC,
                nutrient_content=NutrientContent(
                    nitrogen=2.0,
                    phosphorus=1.0,
                    potassium=1.0,
                    calcium=2.0,
                    magnesium=0.5,
                    sulfur=0.3
                ),
                price_per_unit=35.0,
                unit_type="ton",
                application_rate=5.0,
                organic_certified=True,
                slow_release=True,
                greenhouse_gas_emission_factor=0.5,
                runoff_potential=0.2,
                leaching_potential=0.2,
                application_method="broadcast",
                equipment_required=["spreader", "loader"],
                application_complexity=0.5,
                storage_requirements="covered",
                regional_availability=0.7,
                soil_health_benefit=0.9
            )
        ]

    @pytest.fixture
    def default_criteria(self):
        """Create default scoring criteria."""
        return [
            ScoringCriteria(
                dimension=ScoringDimension.NUTRIENT_VALUE,
                weight=0.30,
                maximize=True,
                preference_function="linear"
            ),
            ScoringCriteria(
                dimension=ScoringDimension.COST_EFFECTIVENESS,
                weight=0.25,
                maximize=True,
                preference_function="linear"
            ),
            ScoringCriteria(
                dimension=ScoringDimension.ENVIRONMENTAL_IMPACT,
                weight=0.20,
                maximize=True,
                preference_function="linear"
            ),
            ScoringCriteria(
                dimension=ScoringDimension.APPLICATION_CONVENIENCE,
                weight=0.15,
                maximize=True,
                preference_function="linear"
            ),
            ScoringCriteria(
                dimension=ScoringDimension.SOIL_HEALTH_IMPACT,
                weight=0.10,
                maximize=True,
                preference_function="linear"
            )
        ]

    @pytest.mark.asyncio
    async def test_weighted_scoring_comparison(
        self, comparison_service, sample_fertilizers, default_criteria
    ):
        """Test weighted scoring comparison."""
        request = ComparisonRequest(
            fertilizers=sample_fertilizers,
            scoring_criteria=default_criteria,
            scoring_method=ScoringMethod.WEIGHTED_SCORING,
            normalize_scores=True,
            include_trade_off_analysis=True
        )

        result = await comparison_service.compare_fertilizers(request)

        # Assertions
        assert result is not None
        assert result.comparison_id == request.comparison_id
        assert result.scoring_method == ScoringMethod.WEIGHTED_SCORING
        assert len(result.fertilizer_scores) == 3

        # Check rankings
        assert result.fertilizer_scores[0].rank == 1
        assert result.fertilizer_scores[1].rank == 2
        assert result.fertilizer_scores[2].rank == 3

        # Check scores are in descending order
        scores = [f.total_score for f in result.fertilizer_scores]
        assert scores == sorted(scores, reverse=True)

        # Check dimension scores exist
        for fertilizer_score in result.fertilizer_scores:
            assert len(fertilizer_score.dimension_scores) == len(default_criteria)
            for dim_score in fertilizer_score.dimension_scores:
                assert 0 <= dim_score.normalized_score <= 100
                assert dim_score.explanation is not None

        # Check comparison matrix
        assert result.comparison_matrix is not None
        assert len(result.comparison_matrix.fertilizer_ids) == 3
        assert len(result.comparison_matrix.score_matrix) == 3
        assert len(result.comparison_matrix.score_matrix[0]) == 5  # 5 dimensions

        # Check trade-off analysis
        assert len(result.trade_off_analyses) > 0
        for trade_off in result.trade_off_analyses:
            assert trade_off.trade_off_summary is not None
            assert trade_off.recommendation is not None

        # Check recommendations
        assert result.top_recommendation is not None
        assert result.recommendation_explanation is not None

        # Check insights
        assert len(result.cost_efficiency_insights) > 0
        assert len(result.environmental_insights) > 0
        assert len(result.application_insights) > 0

    @pytest.mark.asyncio
    async def test_topsis_analysis(
        self, comparison_service, sample_fertilizers, default_criteria
    ):
        """Test TOPSIS analysis."""
        request = ComparisonRequest(
            fertilizers=sample_fertilizers,
            scoring_criteria=default_criteria,
            scoring_method=ScoringMethod.TOPSIS
        )

        result = await comparison_service.topsis_analysis(request)

        # Assertions
        assert result is not None
        assert len(result.topsis_scores) == 3

        # Check TOPSIS scores
        for topsis_score in result.topsis_scores:
            assert 0 <= topsis_score.relative_closeness <= 1
            assert topsis_score.positive_ideal_distance >= 0
            assert topsis_score.negative_ideal_distance >= 0
            assert topsis_score.rank >= 1

        # Check rankings are unique
        ranks = [score.rank for score in result.topsis_scores]
        assert len(ranks) == len(set(ranks))

        # Check ideal solutions
        assert result.positive_ideal_solution is not None
        assert result.negative_ideal_solution is not None
        assert len(result.positive_ideal_solution) == len(default_criteria)
        assert len(result.negative_ideal_solution) == len(default_criteria)

        # Check matrices
        assert len(result.decision_matrix) == 3
        assert len(result.weighted_normalized_matrix) == 3

        # Check recommendation
        assert result.top_recommendation is not None
        assert 0 <= result.recommendation_confidence <= 1

    @pytest.mark.asyncio
    async def test_ahp_analysis(
        self, comparison_service, sample_fertilizers, default_criteria
    ):
        """Test AHP analysis."""
        request = ComparisonRequest(
            fertilizers=sample_fertilizers,
            scoring_criteria=default_criteria,
            scoring_method=ScoringMethod.AHP
        )

        result = await comparison_service.ahp_analysis(request)

        # Assertions
        assert result is not None
        assert len(result.ahp_scores) == 3

        # Check AHP scores
        total_priority = 0.0
        for ahp_score in result.ahp_scores:
            assert 0 <= ahp_score.priority_vector <= 1
            assert ahp_score.consistency_ratio >= 0
            assert ahp_score.rank >= 1
            assert len(ahp_score.pairwise_scores) == len(default_criteria)
            total_priority += ahp_score.priority_vector

        # Priority vectors should sum to approximately 1
        assert 0.95 <= total_priority <= 1.05

        # Check consistency
        assert result.overall_consistency_ratio >= 0
        # Consistency ratio should ideally be < 0.1 for acceptable consistency

        # Check pairwise matrices
        assert len(result.pairwise_matrices) == len(default_criteria)

        # Check recommendation
        assert result.top_recommendation is not None
        assert 0 <= result.recommendation_confidence <= 1

    @pytest.mark.asyncio
    async def test_nutrient_value_scoring(
        self, comparison_service, sample_fertilizers
    ):
        """Test nutrient value score calculation."""
        # Test high NPK content
        urea = sample_fertilizers[0]
        urea_score = comparison_service._calculate_nutrient_value_score(urea)
        assert 0 <= urea_score <= 10

        # Test organic with multiple nutrients
        compost = sample_fertilizers[2]
        compost_score = comparison_service._calculate_nutrient_value_score(compost)
        assert 0 <= compost_score <= 10

        # Compost should get bonus for slow release
        assert compost.slow_release is True

    @pytest.mark.asyncio
    async def test_cost_effectiveness_scoring(
        self, comparison_service, sample_fertilizers
    ):
        """Test cost-effectiveness score calculation."""
        for fertilizer in sample_fertilizers:
            score = comparison_service._calculate_cost_effectiveness_score(fertilizer)
            assert 0 <= score <= 10

        # Higher total nutrients should generally give better cost effectiveness
        # (assuming similar prices)

    @pytest.mark.asyncio
    async def test_environmental_impact_scoring(
        self, comparison_service, sample_fertilizers
    ):
        """Test environmental impact score calculation."""
        # Organic compost should score higher (lower impact)
        compost = sample_fertilizers[2]
        compost_score = comparison_service._calculate_environmental_impact_score(compost)

        # Synthetic urea should score lower (higher impact)
        urea = sample_fertilizers[0]
        urea_score = comparison_service._calculate_environmental_impact_score(urea)

        assert compost_score > urea_score
        assert 0 <= compost_score <= 10
        assert 0 <= urea_score <= 10

    @pytest.mark.asyncio
    async def test_application_convenience_scoring(
        self, comparison_service, sample_fertilizers
    ):
        """Test application convenience score calculation."""
        for fertilizer in sample_fertilizers:
            score = comparison_service._calculate_application_convenience_score(fertilizer)
            assert 0 <= score <= 10

        # Fertilizers with fewer equipment requirements should score higher

    @pytest.mark.asyncio
    async def test_invalid_request_validation(
        self, comparison_service, default_criteria
    ):
        """Test validation of invalid requests."""
        # Test with too few fertilizers
        with pytest.raises(ValueError, match="At least 2 fertilizers are required"):
            request = ComparisonRequest(
                fertilizers=[],
                scoring_criteria=default_criteria
            )
            await comparison_service.compare_fertilizers(request)

        # Test with invalid criteria weights (not summing to 1.0)
        invalid_criteria = [
            ScoringCriteria(
                dimension=ScoringDimension.NUTRIENT_VALUE,
                weight=0.5,
                maximize=True
            ),
            ScoringCriteria(
                dimension=ScoringDimension.COST_EFFECTIVENESS,
                weight=0.3,
                maximize=True
            )
        ]

        with pytest.raises(ValueError, match="weights must sum to 1.0"):
            ComparisonRequest(
                fertilizers=[
                    FertilizerOption(
                        fertilizer_id="test1",
                        fertilizer_name="Test 1",
                        fertilizer_type="synthetic",
                        category=ComparisonCategory.SYNTHETIC,
                        nutrient_content=NutrientContent(),
                        price_per_unit=100.0,
                        unit_type="ton",
                        application_rate=1.0,
                        application_method="broadcast"
                    ),
                    FertilizerOption(
                        fertilizer_id="test2",
                        fertilizer_name="Test 2",
                        fertilizer_type="synthetic",
                        category=ComparisonCategory.SYNTHETIC,
                        nutrient_content=NutrientContent(),
                        price_per_unit=100.0,
                        unit_type="ton",
                        application_rate=1.0,
                        application_method="broadcast"
                    )
                ],
                scoring_criteria=invalid_criteria
            )

    @pytest.mark.asyncio
    async def test_strengths_weaknesses_identification(
        self, comparison_service, sample_fertilizers
    ):
        """Test identification of strengths and weaknesses."""
        from ..models.comparison_models import DimensionScore

        # Create sample dimension scores
        high_scores = [
            DimensionScore(
                dimension=ScoringDimension.NUTRIENT_VALUE,
                raw_score=9.0,
                normalized_score=90.0,
                weight=0.3,
                weighted_score=27.0,
                explanation="High nutrient content"
            ),
            DimensionScore(
                dimension=ScoringDimension.COST_EFFECTIVENESS,
                raw_score=4.0,
                normalized_score=40.0,
                weight=0.25,
                weighted_score=10.0,
                explanation="Moderate cost"
            )
        ]

        fertilizer = sample_fertilizers[0]
        strengths, weaknesses = comparison_service._identify_strengths_weaknesses(
            high_scores, fertilizer
        )

        # Should identify high nutrient content as strength
        assert len(strengths) > 0
        # Should identify low cost-effectiveness as weakness
        assert len(weaknesses) > 0

    @pytest.mark.asyncio
    async def test_trade_off_analysis_generation(
        self, comparison_service, sample_fertilizers, default_criteria
    ):
        """Test trade-off analysis generation."""
        request = ComparisonRequest(
            fertilizers=sample_fertilizers,
            scoring_criteria=default_criteria,
            include_trade_off_analysis=True
        )

        result = await comparison_service.compare_fertilizers(request)

        trade_offs = result.trade_off_analyses
        assert len(trade_offs) > 0

        for trade_off in trade_offs:
            assert trade_off.fertilizer_1_id in [f.fertilizer_id for f in sample_fertilizers]
            assert trade_off.fertilizer_2_id in [f.fertilizer_id for f in sample_fertilizers]
            assert trade_off.trade_off_summary is not None
            assert trade_off.recommendation is not None

    @pytest.mark.asyncio
    async def test_comparison_matrix_creation(
        self, comparison_service, sample_fertilizers, default_criteria
    ):
        """Test comparison matrix creation."""
        dimension_scores = comparison_service._calculate_all_dimension_scores(
            sample_fertilizers, default_criteria
        )

        matrix = comparison_service._create_comparison_matrix(
            sample_fertilizers, dimension_scores, default_criteria
        )

        assert len(matrix.fertilizer_ids) == 3
        assert len(matrix.fertilizer_names) == 3
        assert len(matrix.dimensions) == 5
        assert len(matrix.score_matrix) == 3
        assert len(matrix.score_matrix[0]) == 5
        assert len(matrix.normalized_matrix) == 3
        assert len(matrix.dimension_averages) == 5
        assert len(matrix.dimension_std_devs) == 5

    @pytest.mark.asyncio
    async def test_budget_constraint_filtering(
        self, comparison_service, sample_fertilizers, default_criteria
    ):
        """Test budget constraint consideration."""
        request = ComparisonRequest(
            fertilizers=sample_fertilizers,
            scoring_criteria=default_criteria,
            budget_constraint=150.0,  # $150 per acre budget
            field_size_acres=100.0
        )

        result = await comparison_service.compare_fertilizers(request)

        # Check that cost insights mention budget constraint
        assert any("budget" in insight.lower() for insight in result.cost_efficiency_insights)

    @pytest.mark.asyncio
    async def test_get_available_criteria(self, comparison_service):
        """Test getting available criteria."""
        criteria = comparison_service.get_available_criteria()

        assert len(criteria) > 0

        # Check each criterion has required fields
        for criterion in criteria:
            assert criterion.dimension is not None
            assert criterion.display_name is not None
            assert criterion.description is not None
            assert 0 <= criterion.default_weight <= 1
            assert criterion.maximize is not None
            assert criterion.factors_considered is not None

        # Check default weights sum to approximately 1.0
        total_weight = sum(c.default_weight for c in criteria)
        assert 0.95 <= total_weight <= 1.05

    @pytest.mark.asyncio
    async def test_equal_scores_ranking(
        self, comparison_service, default_criteria
    ):
        """Test ranking when fertilizers have equal scores."""
        # Create identical fertilizers
        identical_fertilizers = [
            FertilizerOption(
                fertilizer_id=f"fert-{i}",
                fertilizer_name=f"Fertilizer {i}",
                fertilizer_type="synthetic",
                category=ComparisonCategory.SYNTHETIC,
                nutrient_content=NutrientContent(
                    nitrogen=20.0,
                    phosphorus=20.0,
                    potassium=20.0
                ),
                price_per_unit=300.0,
                unit_type="ton",
                application_rate=1.0,
                organic_certified=False,
                slow_release=False,
                greenhouse_gas_emission_factor=1.0,
                runoff_potential=0.5,
                leaching_potential=0.5,
                application_method="broadcast",
                equipment_required=["spreader"],
                application_complexity=0.5,
                storage_requirements="standard",
                regional_availability=0.8,
                soil_health_benefit=0.5
            )
            for i in range(3)
        ]

        request = ComparisonRequest(
            fertilizers=identical_fertilizers,
            scoring_criteria=default_criteria
        )

        result = await comparison_service.compare_fertilizers(request)

        # All should have ranks assigned (even if tied)
        ranks = [score.rank for score in result.fertilizer_scores]
        assert all(rank >= 1 for rank in ranks)

    @pytest.mark.asyncio
    async def test_processing_time_recorded(
        self, comparison_service, sample_fertilizers, default_criteria
    ):
        """Test that processing time is recorded."""
        request = ComparisonRequest(
            fertilizers=sample_fertilizers,
            scoring_criteria=default_criteria
        )

        result = await comparison_service.compare_fertilizers(request)

        assert result.processing_time_ms > 0
        assert result.processing_time_ms < 10000  # Should complete in under 10 seconds

    @pytest.mark.asyncio
    async def test_normalize_scores_option(
        self, comparison_service, sample_fertilizers, default_criteria
    ):
        """Test normalize_scores option."""
        # Test with normalization
        request_normalized = ComparisonRequest(
            fertilizers=sample_fertilizers,
            scoring_criteria=default_criteria,
            normalize_scores=True
        )

        result_normalized = await comparison_service.compare_fertilizers(request_normalized)

        # Check scores are in 0-100 range
        for fertilizer_score in result_normalized.fertilizer_scores:
            for dim_score in fertilizer_score.dimension_scores:
                assert 0 <= dim_score.normalized_score <= 100

        # Test without normalization
        request_raw = ComparisonRequest(
            fertilizers=sample_fertilizers,
            scoring_criteria=default_criteria,
            normalize_scores=False
        )

        result_raw = await comparison_service.compare_fertilizers(request_raw)

        # Check scores are in 0-10 range
        for fertilizer_score in result_raw.fertilizer_scores:
            for dim_score in fertilizer_score.dimension_scores:
                assert 0 <= dim_score.raw_score <= 10

    @pytest.mark.asyncio
    async def test_organic_vs_synthetic_comparison(
        self, comparison_service, sample_fertilizers, default_criteria
    ):
        """Test comparison between organic and synthetic fertilizers."""
        request = ComparisonRequest(
            fertilizers=sample_fertilizers,
            scoring_criteria=default_criteria,
            environmental_priority=0.8  # High environmental priority
        )

        result = await comparison_service.compare_fertilizers(request)

        # Find organic and synthetic fertilizers
        organic_scores = [
            score for score in result.fertilizer_scores
            if score.fertilizer_id == "compost-2-1-1"
        ]
        synthetic_scores = [
            score for score in result.fertilizer_scores
            if score.fertilizer_id in ["urea-46-0-0", "dap-18-46-0"]
        ]

        assert len(organic_scores) == 1
        assert len(synthetic_scores) == 2

        # Organic should score higher on environmental impact
        organic_env_score = next(
            (d.normalized_score for d in organic_scores[0].dimension_scores
             if d.dimension == ScoringDimension.ENVIRONMENTAL_IMPACT),
            0
        )

        for synth_score in synthetic_scores:
            synth_env_score = next(
                (d.normalized_score for d in synth_score.dimension_scores
                 if d.dimension == ScoringDimension.ENVIRONMENTAL_IMPACT),
                0
            )
            assert organic_env_score > synth_env_score


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

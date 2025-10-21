"""
Comprehensive Unit Tests for Fertilizer Type Selection Service

Tests core service logic for fertilizer type selection including:
- Recommendation generation
- Priority validation and normalization
- Constraint validation
- Scoring algorithms
- Cost analysis
- Environmental impact assessment

Implements TICKET-023_fertilizer-type-selection-11.1
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, date

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ..services.fertilizer_type_selection_service import FertilizerTypeSelectionService
from ..models.fertilizer_models import FarmerPriorities, FarmerConstraints


class TestFertilizerTypeSelectionService:
    """Test FertilizerTypeSelectionService class."""

    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return FertilizerTypeSelectionService()

    @pytest.fixture
    def basic_priorities(self):
        """Basic farmer priorities for testing."""
        return FarmerPriorities(
            cost_effectiveness=0.8,
            soil_health=0.6,
            quick_results=0.5,
            environmental_impact=0.4,
            ease_of_application=0.5,
            long_term_benefits=0.6
        )

    @pytest.fixture
    def basic_constraints(self):
        """Basic farmer constraints for testing."""
        return FarmerConstraints(
            budget_per_acre=100.0,
            farm_size_acres=160.0,
            available_equipment=["broadcast_spreader"],
            organic_preference=False,
            environmental_concerns=False
        )


class TestRecommendationGeneration:
    """Test recommendation generation methods."""

    @pytest.fixture
    def service(self):
        return FertilizerTypeSelectionService()

    @pytest.fixture
    def priorities(self):
        return FarmerPriorities(
            cost_effectiveness=0.8,
            soil_health=0.7,
            quick_results=0.5,
            environmental_impact=0.6,
            ease_of_application=0.5,
            long_term_benefits=0.7
        )

    @pytest.fixture
    def constraints(self):
        return FarmerConstraints(
            budget_per_acre=120.0,
            farm_size_acres=160.0,
            available_equipment=["broadcast_spreader", "field_sprayer"],
            organic_preference=False,
            environmental_concerns=True
        )

    @pytest.mark.asyncio
    async def test_get_fertilizer_type_recommendations_basic(self, service, priorities, constraints):
        """Test basic recommendation generation."""
        recommendations = await service.get_fertilizer_type_recommendations(
            priorities=priorities,
            constraints=constraints
        )

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert len(recommendations) <= 5

        # Verify recommendation structure
        for rec in recommendations:
            assert "id" in rec
            assert "name" in rec
            assert "type" in rec
            assert "suitability_score" in rec
            assert 0 <= rec["suitability_score"] <= 1

    @pytest.mark.asyncio
    async def test_organic_preference_filtering(self, service, priorities):
        """Test that organic preference properly filters recommendations."""
        constraints = FarmerConstraints(
            budget_per_acre=200.0,
            farm_size_acres=80.0,
            available_equipment=["manure_spreader"],
            organic_preference=True,
            environmental_concerns=True
        )

        recommendations = await service.get_fertilizer_type_recommendations(
            priorities=priorities,
            constraints=constraints
        )

        # Should only return organic options
        for rec in recommendations:
            details = rec.get("details", {})
            assert details.get("organic_certified", False) is True

    @pytest.mark.asyncio
    async def test_recommendations_sorted_by_score(self, service, priorities, constraints):
        """Test that recommendations are sorted by suitability score."""
        recommendations = await service.get_fertilizer_type_recommendations(
            priorities=priorities,
            constraints=constraints
        )

        if len(recommendations) > 1:
            scores = [r["suitability_score"] for r in recommendations]
            assert scores == sorted(scores, reverse=True)

    @pytest.mark.asyncio
    async def test_minimum_score_threshold(self, service, priorities, constraints):
        """Test that only fertilizers above minimum threshold are included."""
        recommendations = await service.get_fertilizer_type_recommendations(
            priorities=priorities,
            constraints=constraints
        )

        # All recommendations should be above 0.3 threshold
        for rec in recommendations:
            assert rec["suitability_score"] > 0.3


class TestScoringAlgorithms:
    """Test fertilizer scoring algorithms."""

    @pytest.fixture
    def service(self):
        return FertilizerTypeSelectionService()

    def test_calculate_fertilizer_score_cost_priority(self, service):
        """Test scoring with high cost effectiveness priority."""
        fertilizer = {
            "product_id": "test_1",
            "name": "Test Fertilizer",
            "cost_per_unit": 50,
            "soil_health_score": 0.5,
            "environmental_impact_score": 0.5,
            "equipment_requirements": ["broadcast_spreader"]
        }

        priorities = FarmerPriorities(
            cost_effectiveness=1.0,
            soil_health=0.0,
            quick_results=0.0,
            environmental_impact=0.0,
            ease_of_application=0.0,
            long_term_benefits=0.0
        )

        constraints = FarmerConstraints(
            budget_per_acre=100.0,
            farm_size_acres=160.0,
            available_equipment=["broadcast_spreader"]
        )

        score = service._calculate_fertilizer_score(
            fertilizer, priorities, constraints, None, None
        )

        assert 0 <= score <= 1
        # Should get high score for low cost
        assert score > 0.5

    def test_calculate_fertilizer_score_soil_health_priority(self, service):
        """Test scoring with high soil health priority."""
        fertilizer = {
            "product_id": "organic_1",
            "name": "Organic Fertilizer",
            "cost_per_unit": 100,
            "soil_health_score": 0.95,
            "environmental_impact_score": 0.9,
            "equipment_requirements": ["manure_spreader"]
        }

        priorities = FarmerPriorities(
            cost_effectiveness=0.0,
            soil_health=1.0,
            quick_results=0.0,
            environmental_impact=0.0,
            ease_of_application=0.0,
            long_term_benefits=0.0
        )

        constraints = FarmerConstraints(
            budget_per_acre=200.0,
            farm_size_acres=80.0,
            available_equipment=["manure_spreader"]
        )

        score = service._calculate_fertilizer_score(
            fertilizer, priorities, constraints, None, None
        )

        assert score > 0.8  # Should get very high score

    def test_score_normalization(self, service):
        """Test that scores are properly normalized to 0-1 range."""
        fertilizer = {
            "product_id": "test",
            "cost_per_unit": 75,
            "soil_health_score": 0.7,
            "environmental_impact_score": 0.6,
            "equipment_requirements": []
        }

        # Very high priorities (sum > 1)
        priorities = FarmerPriorities(
            cost_effectiveness=0.9,
            soil_health=0.9,
            quick_results=0.9,
            environmental_impact=0.9,
            ease_of_application=0.9,
            long_term_benefits=0.9
        )

        constraints = FarmerConstraints(
            budget_per_acre=100.0,
            farm_size_acres=160.0,
            available_equipment=["broadcast_spreader"]
        )

        score = service._calculate_fertilizer_score(
            fertilizer, priorities, constraints, None, None
        )

        # Should still be normalized to 0-1
        assert 0 <= score <= 1


class TestCostEvaluation:
    """Test cost effectiveness evaluation methods."""

    @pytest.fixture
    def service(self):
        return FertilizerTypeSelectionService()

    def test_evaluate_cost_effectiveness_within_budget(self, service):
        """Test cost evaluation for fertilizer within budget."""
        fertilizer = {"cost_per_unit": 50}
        budget_per_acre = 100.0

        score = service._evaluate_cost_effectiveness(fertilizer, budget_per_acre)

        assert score == 1.0  # Within 50% of budget

    def test_evaluate_cost_effectiveness_at_budget(self, service):
        """Test cost evaluation for fertilizer at budget limit."""
        fertilizer = {"cost_per_unit": 100}
        budget_per_acre = 100.0

        score = service._evaluate_cost_effectiveness(fertilizer, budget_per_acre)

        assert score == 0.7  # At budget

    def test_evaluate_cost_effectiveness_over_budget(self, service):
        """Test cost evaluation for fertilizer over budget."""
        fertilizer = {"cost_per_unit": 200}
        budget_per_acre = 100.0

        score = service._evaluate_cost_effectiveness(fertilizer, budget_per_acre)

        assert score == 0.2  # Over budget

    def test_evaluate_cost_effectiveness_no_budget(self, service):
        """Test cost evaluation when no budget specified."""
        fertilizer = {"cost_per_unit": 100}
        budget_per_acre = None

        score = service._evaluate_cost_effectiveness(fertilizer, budget_per_acre)

        assert score == 0.5  # Default score


class TestApplicationEaseEvaluation:
    """Test application ease evaluation methods."""

    @pytest.fixture
    def service(self):
        return FertilizerTypeSelectionService()

    def test_evaluate_application_ease_compatible_equipment(self, service):
        """Test application ease with compatible equipment."""
        fertilizer = {"equipment_requirements": ["broadcast_spreader"]}
        available_equipment = ["broadcast_spreader", "field_sprayer"]

        score = service._evaluate_application_ease(fertilizer, available_equipment)

        assert score == 1.0  # Compatible equipment

    def test_evaluate_application_ease_incompatible_equipment(self, service):
        """Test application ease with incompatible equipment."""
        fertilizer = {"equipment_requirements": ["injection_system"]}
        available_equipment = ["broadcast_spreader"]

        score = service._evaluate_application_ease(fertilizer, available_equipment)

        assert score == 0.3  # Incompatible equipment

    def test_evaluate_application_ease_no_requirements(self, service):
        """Test application ease when no specific equipment required."""
        fertilizer = {"equipment_requirements": []}
        available_equipment = ["broadcast_spreader"]

        score = service._evaluate_application_ease(fertilizer, available_equipment)

        assert score == 0.8  # Default for flexible application


class TestConfidenceCalculation:
    """Test confidence score calculation."""

    @pytest.fixture
    def service(self):
        return FertilizerTypeSelectionService()

    def test_calculate_confidence_no_recommendations(self, service):
        """Test confidence calculation with no recommendations."""
        recommendations = []

        confidence = service.calculate_overall_confidence(recommendations)

        assert confidence == 0.0

    def test_calculate_confidence_high_scores(self, service):
        """Test confidence with high suitability scores."""
        recommendations = [
            {"suitability_score": 0.9},
            {"suitability_score": 0.88},
            {"suitability_score": 0.85}
        ]

        confidence = service.calculate_overall_confidence(recommendations)

        assert confidence > 0.8

    def test_calculate_confidence_low_scores(self, service):
        """Test confidence with low suitability scores."""
        recommendations = [
            {"suitability_score": 0.4},
            {"suitability_score": 0.35},
            {"suitability_score": 0.32}
        ]

        confidence = service.calculate_overall_confidence(recommendations)

        assert confidence < 0.5

    def test_calculate_confidence_single_recommendation(self, service):
        """Test confidence with only one recommendation."""
        recommendations = [{"suitability_score": 0.8}]

        confidence = service.calculate_overall_confidence(recommendations)

        # Should have adjustment for single recommendation
        assert 0 < confidence <= 1


class TestPriorityValidation:
    """Test priority validation methods."""

    @pytest.fixture
    def service(self):
        return FertilizerTypeSelectionService()

    def test_validate_priorities_all_zero(self, service):
        """Test validation fails when all priorities are zero."""
        priorities = FarmerPriorities(
            cost_effectiveness=0.0,
            soil_health=0.0,
            quick_results=0.0,
            environmental_impact=0.0,
            ease_of_application=0.0,
            long_term_benefits=0.0
        )

        result = service._validate_priorities(priorities)

        assert result["is_valid"] is False
        assert len(result["errors"]) > 0

    def test_validate_priorities_valid_range(self, service):
        """Test validation passes with valid priorities."""
        priorities = FarmerPriorities(
            cost_effectiveness=0.8,
            soil_health=0.7,
            quick_results=0.5,
            environmental_impact=0.6,
            ease_of_application=0.5,
            long_term_benefits=0.7
        )

        result = service._validate_priorities(priorities)

        assert result["is_valid"] is True
        assert len(result["errors"]) == 0

    def test_validate_priorities_warnings_for_low_sum(self, service):
        """Test validation provides warnings for very low priority sum."""
        priorities = FarmerPriorities(
            cost_effectiveness=0.1,
            soil_health=0.1,
            quick_results=0.0,
            environmental_impact=0.0,
            ease_of_application=0.0,
            long_term_benefits=0.0
        )

        result = service._validate_priorities(priorities)

        assert result["is_valid"] is True
        assert len(result["warnings"]) > 0


class TestConstraintValidation:
    """Test constraint validation methods."""

    @pytest.fixture
    def service(self):
        return FertilizerTypeSelectionService()

    def test_validate_constraints_valid(self, service):
        """Test validation passes with valid constraints."""
        constraints = FarmerConstraints(
            budget_per_acre=100.0,
            farm_size_acres=160.0,
            available_equipment=["broadcast_spreader"]
        )

        result = service._validate_constraints(constraints)

        assert result["is_valid"] is True

    def test_validate_constraints_no_equipment(self, service):
        """Test validation fails with no available equipment."""
        constraints = FarmerConstraints(
            budget_per_acre=100.0,
            farm_size_acres=160.0,
            available_equipment=[]
        )

        result = service._validate_constraints(constraints)

        assert result["is_valid"] is False
        assert len(result["errors"]) > 0

    def test_validate_constraints_budget_consistency(self, service):
        """Test validation checks budget consistency."""
        constraints = FarmerConstraints(
            budget_per_acre=100.0,
            total_budget=20000.0,  # Inconsistent with 100/acre * 160 acres
            farm_size_acres=160.0,
            available_equipment=["broadcast_spreader"]
        )

        result = service._validate_constraints(constraints)

        # Should have warning about budget inconsistency
        assert len(result["warnings"]) > 0


class TestComparisonMethods:
    """Test fertilizer comparison methods."""

    @pytest.fixture
    def service(self):
        return FertilizerTypeSelectionService()

    @pytest.mark.asyncio
    async def test_compare_fertilizer_options(self, service):
        """Test comparing multiple fertilizer options."""
        fertilizer_ids = ["urea_46_0_0", "ammonium_sulfate_21_0_0"]
        comparison_criteria = ["cost_effectiveness", "soil_health_impact"]
        farm_context = {"farm_size_acres": 160, "budget_per_acre": 100}

        results = await service.compare_fertilizer_options(
            fertilizer_ids, comparison_criteria, farm_context
        )

        assert isinstance(results, list)
        assert len(results) == 2

        for result in results:
            assert "fertilizer_id" in result
            assert "scores" in result
            assert "overall_score" in result

    def test_get_comparison_recommendation(self, service):
        """Test getting recommendation from comparison results."""
        comparison_results = [
            {"name": "Fertilizer A", "overall_score": 0.8},
            {"name": "Fertilizer B", "overall_score": 0.6}
        ]

        recommendation = service.get_comparison_recommendation(comparison_results)

        assert isinstance(recommendation, str)
        assert "Fertilizer A" in recommendation


class TestCostAnalysis:
    """Test cost analysis methods."""

    @pytest.fixture
    def service(self):
        return FertilizerTypeSelectionService()

    def test_generate_cost_analysis(self, service):
        """Test cost analysis generation."""
        recommendations = [
            {
                "id": "fert_1",
                "details": {"cost_per_unit": 100}
            },
            {
                "id": "fert_2",
                "details": {"cost_per_unit": 150}
            }
        ]

        constraints = FarmerConstraints(
            budget_per_acre=120.0,
            farm_size_acres=160.0,
            available_equipment=["broadcast_spreader"]
        )

        analysis = service.generate_cost_analysis(recommendations, constraints)

        assert "average_cost_per_acre" in analysis
        assert "total_farm_cost" in analysis
        assert "cost_range" in analysis
        assert "budget_analysis" in analysis

    def test_cost_analysis_empty_recommendations(self, service):
        """Test cost analysis with no recommendations."""
        recommendations = []
        constraints = FarmerConstraints(
            budget_per_acre=100.0,
            farm_size_acres=160.0,
            available_equipment=["broadcast_spreader"]
        )

        analysis = service.generate_cost_analysis(recommendations, constraints)

        assert analysis["average_cost_per_acre"] == 0
        assert analysis["total_farm_cost"] == 0


class TestEnvironmentalImpact:
    """Test environmental impact assessment."""

    @pytest.fixture
    def service(self):
        return FertilizerTypeSelectionService()

    @pytest.mark.asyncio
    async def test_assess_environmental_impact(self, service):
        """Test environmental impact assessment."""
        recommendations = [
            {"details": {"environmental_impact_score": 0.8}},
            {"details": {"environmental_impact_score": 0.7}}
        ]

        field_conditions = {
            "soil": {"ph": 6.5},
            "crop": {"type": "corn"}
        }

        impact = await service.assess_environmental_impact_for_recommendations(
            recommendations, field_conditions
        )

        assert "overall_impact" in impact
        assert "risks" in impact
        assert "mitigation_strategies" in impact


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

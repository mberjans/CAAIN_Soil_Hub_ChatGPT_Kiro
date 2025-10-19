"""
Comprehensive Fertilizer Comparison and Scoring Service.

This service provides multi-criteria decision analysis for fertilizer selection including:
- Weighted scoring for multi-dimensional comparison
- TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution)
- AHP (Analytic Hierarchy Process) analysis
- Trade-off analysis and decision support
- Cost-effectiveness and environmental impact scoring
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from uuid import uuid4
import warnings
warnings.filterwarnings('ignore')

from ..models.comparison_models import (
    ComparisonRequest, ComparisonResult, FertilizerOption, ScoringCriteria,
    FertilizerScore, DimensionScore, TOPSISScore, TOPSISResult, AHPScore,
    AHPResult, TradeOffAnalysis, ComparisonMatrix, SensitivityAnalysis,
    ScoringMethod, ScoringDimension, AvailableCriteria
)

logger = logging.getLogger(__name__)


class FertilizerComparisonService:
    """Comprehensive fertilizer comparison and scoring service."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.scoring_methods = {
            ScoringMethod.WEIGHTED_SCORING: self._weighted_scoring_analysis,
            ScoringMethod.TOPSIS: self._topsis_analysis,
            ScoringMethod.AHP: self._ahp_analysis
        }

    async def compare_fertilizers(self, request: ComparisonRequest) -> ComparisonResult:
        """
        Perform comprehensive multi-criteria fertilizer comparison.

        Args:
            request: Comparison request with fertilizers and scoring criteria

        Returns:
            ComparisonResult with scores, rankings, and recommendations
        """
        start_time = datetime.utcnow()

        try:
            self.logger.info(f"Starting fertilizer comparison {request.comparison_id}")

            # Validate request
            self._validate_comparison_request(request)

            # Calculate dimension scores for all fertilizers
            dimension_scores_by_fertilizer = self._calculate_all_dimension_scores(
                request.fertilizers, request.scoring_criteria
            )

            # Perform scoring based on selected method
            scoring_method = self.scoring_methods.get(request.scoring_method)
            if not scoring_method:
                raise ValueError(f"Unsupported scoring method: {request.scoring_method}")

            fertilizer_scores = await scoring_method(
                request.fertilizers,
                dimension_scores_by_fertilizer,
                request.scoring_criteria,
                request
            )

            # Rank fertilizers
            fertilizer_scores = self._rank_fertilizers(fertilizer_scores)

            # Create comparison matrix
            comparison_matrix = self._create_comparison_matrix(
                request.fertilizers, dimension_scores_by_fertilizer, request.scoring_criteria
            )

            # Perform trade-off analysis
            trade_off_analyses = []
            if request.include_trade_off_analysis:
                trade_off_analyses = self._perform_trade_off_analysis(
                    fertilizer_scores, request.fertilizers
                )

            # Generate recommendations
            top_recommendation, recommendation_explanation, alternative_recommendations = \
                self._generate_recommendations(fertilizer_scores, request)

            # Generate insights
            cost_insights = self._generate_cost_insights(fertilizer_scores, request)
            environmental_insights = self._generate_environmental_insights(
                fertilizer_scores, request.fertilizers
            )
            application_insights = self._generate_application_insights(
                fertilizer_scores, request.fertilizers
            )

            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            # Create result
            result = ComparisonResult(
                comparison_id=request.comparison_id,
                field_id=request.field_id,
                user_id=request.user_id,
                scoring_method=request.scoring_method,
                fertilizer_scores=fertilizer_scores,
                comparison_matrix=comparison_matrix,
                trade_off_analyses=trade_off_analyses,
                top_recommendation=top_recommendation,
                recommendation_explanation=recommendation_explanation,
                alternative_recommendations=alternative_recommendations,
                cost_efficiency_insights=cost_insights,
                environmental_insights=environmental_insights,
                application_insights=application_insights,
                processing_time_ms=processing_time
            )

            self.logger.info(f"Fertilizer comparison {request.comparison_id} completed")
            return result

        except Exception as e:
            self.logger.error(f"Error in fertilizer comparison: {str(e)}")
            raise

    async def topsis_analysis(
        self, request: ComparisonRequest
    ) -> TOPSISResult:
        """
        Perform TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution) analysis.

        Args:
            request: Comparison request with fertilizers and criteria

        Returns:
            TOPSISResult with TOPSIS-specific scores and analysis
        """
        start_time = datetime.utcnow()

        try:
            self.logger.info(f"Starting TOPSIS analysis for comparison {request.comparison_id}")

            # Calculate dimension scores
            dimension_scores_by_fertilizer = self._calculate_all_dimension_scores(
                request.fertilizers, request.scoring_criteria
            )

            # Build decision matrix
            decision_matrix = self._build_decision_matrix(
                dimension_scores_by_fertilizer, request.scoring_criteria
            )

            # Normalize decision matrix
            normalized_matrix = self._normalize_matrix(decision_matrix)

            # Apply weights
            weighted_normalized_matrix = self._apply_weights(
                normalized_matrix, request.scoring_criteria
            )

            # Determine ideal solutions
            positive_ideal, negative_ideal = self._determine_ideal_solutions(
                weighted_normalized_matrix, request.scoring_criteria
            )

            # Calculate distances
            topsis_scores = self._calculate_topsis_scores(
                weighted_normalized_matrix, positive_ideal, negative_ideal,
                request.fertilizers, dimension_scores_by_fertilizer, request.scoring_criteria
            )

            # Rank by relative closeness
            topsis_scores = sorted(
                topsis_scores, key=lambda x: x.relative_closeness, reverse=True
            )
            for rank, score in enumerate(topsis_scores, start=1):
                score.rank = rank

            # Determine recommendation confidence
            if len(topsis_scores) >= 2:
                confidence = topsis_scores[0].relative_closeness - topsis_scores[1].relative_closeness
                confidence = min(1.0, confidence * 2)  # Scale to 0-1
            else:
                confidence = 1.0

            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            result = TOPSISResult(
                comparison_id=request.comparison_id,
                topsis_scores=topsis_scores,
                positive_ideal_solution={
                    criterion.dimension.value: val
                    for criterion, val in zip(request.scoring_criteria, positive_ideal)
                },
                negative_ideal_solution={
                    criterion.dimension.value: val
                    for criterion, val in zip(request.scoring_criteria, negative_ideal)
                },
                decision_matrix=decision_matrix,
                weighted_normalized_matrix=weighted_normalized_matrix,
                top_recommendation=topsis_scores[0].fertilizer_name,
                recommendation_confidence=confidence,
                processing_time_ms=processing_time
            )

            self.logger.info(f"TOPSIS analysis completed for comparison {request.comparison_id}")
            return result

        except Exception as e:
            self.logger.error(f"Error in TOPSIS analysis: {str(e)}")
            raise

    async def ahp_analysis(
        self, request: ComparisonRequest
    ) -> AHPResult:
        """
        Perform AHP (Analytic Hierarchy Process) analysis.

        Args:
            request: Comparison request with fertilizers and criteria

        Returns:
            AHPResult with AHP-specific scores and consistency analysis
        """
        start_time = datetime.utcnow()

        try:
            self.logger.info(f"Starting AHP analysis for comparison {request.comparison_id}")

            # Calculate dimension scores
            dimension_scores_by_fertilizer = self._calculate_all_dimension_scores(
                request.fertilizers, request.scoring_criteria
            )

            # Build pairwise comparison matrices for each criterion
            pairwise_matrices = self._build_pairwise_matrices(
                request.fertilizers, dimension_scores_by_fertilizer, request.scoring_criteria
            )

            # Calculate priority vectors
            ahp_scores = self._calculate_ahp_scores(
                pairwise_matrices, request.fertilizers, request.scoring_criteria
            )

            # Calculate consistency ratios
            overall_cr = self._calculate_overall_consistency(pairwise_matrices)
            consistency_acceptable = overall_cr < 0.1

            # Rank fertilizers
            ahp_scores = sorted(ahp_scores, key=lambda x: x.priority_vector, reverse=True)
            for rank, score in enumerate(ahp_scores, start=1):
                score.rank = rank

            # Determine recommendation confidence
            if len(ahp_scores) >= 2:
                confidence = (ahp_scores[0].priority_vector - ahp_scores[1].priority_vector) / \
                           ahp_scores[0].priority_vector
                confidence = min(1.0, max(0.0, confidence))
            else:
                confidence = 1.0

            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            result = AHPResult(
                comparison_id=request.comparison_id,
                ahp_scores=ahp_scores,
                pairwise_matrices={
                    criterion.dimension.value: matrix.tolist()
                    for criterion, matrix in zip(request.scoring_criteria, pairwise_matrices.values())
                },
                overall_consistency_ratio=overall_cr,
                consistency_acceptable=consistency_acceptable,
                top_recommendation=ahp_scores[0].fertilizer_name,
                recommendation_confidence=confidence,
                processing_time_ms=processing_time
            )

            self.logger.info(f"AHP analysis completed for comparison {request.comparison_id}")
            return result

        except Exception as e:
            self.logger.error(f"Error in AHP analysis: {str(e)}")
            raise

    def get_available_criteria(self) -> List[AvailableCriteria]:
        """
        Get list of available scoring criteria with descriptions.

        Returns:
            List of AvailableCriteria with metadata
        """
        criteria = [
            AvailableCriteria(
                dimension=ScoringDimension.NUTRIENT_VALUE,
                display_name="Nutrient Value",
                description="Total nutrient content and availability (N-P-K plus micronutrients)",
                default_weight=0.30,
                maximize=True,
                measurement_unit="percentage",
                typical_range="0-100%",
                factors_considered=[
                    "N-P-K content",
                    "Micronutrient content",
                    "Nutrient availability",
                    "Release pattern"
                ]
            ),
            AvailableCriteria(
                dimension=ScoringDimension.COST_EFFECTIVENESS,
                display_name="Cost Effectiveness",
                description="Cost per unit of nutrient delivered to the crop",
                default_weight=0.25,
                maximize=True,
                measurement_unit="$/lb nutrient",
                typical_range="$0.10-$2.00/lb",
                factors_considered=[
                    "Price per unit",
                    "Application rate",
                    "Nutrient content",
                    "Utilization efficiency"
                ]
            ),
            AvailableCriteria(
                dimension=ScoringDimension.ENVIRONMENTAL_IMPACT,
                display_name="Environmental Impact",
                description="Environmental footprint including emissions, runoff, and leaching",
                default_weight=0.20,
                maximize=False,  # Minimize environmental impact
                measurement_unit="impact score",
                typical_range="0-10",
                factors_considered=[
                    "GHG emissions",
                    "Runoff potential",
                    "Leaching potential",
                    "Organic certification"
                ]
            ),
            AvailableCriteria(
                dimension=ScoringDimension.APPLICATION_CONVENIENCE,
                display_name="Application Convenience",
                description="Ease of application and equipment requirements",
                default_weight=0.15,
                maximize=True,
                measurement_unit="convenience score",
                typical_range="0-10",
                factors_considered=[
                    "Application complexity",
                    "Equipment requirements",
                    "Storage requirements",
                    "Handling safety"
                ]
            ),
            AvailableCriteria(
                dimension=ScoringDimension.AVAILABILITY,
                display_name="Regional Availability",
                description="Product availability in the region",
                default_weight=0.05,
                maximize=True,
                measurement_unit="availability score",
                typical_range="0-1",
                factors_considered=[
                    "Regional distribution",
                    "Seasonal availability",
                    "Supply consistency"
                ]
            ),
            AvailableCriteria(
                dimension=ScoringDimension.SOIL_HEALTH_IMPACT,
                display_name="Soil Health Impact",
                description="Long-term impact on soil health and biology",
                default_weight=0.05,
                maximize=True,
                measurement_unit="impact score",
                typical_range="0-10",
                factors_considered=[
                    "Organic matter contribution",
                    "Microbial activity impact",
                    "Soil structure impact",
                    "pH buffering"
                ]
            )
        ]
        return criteria

    # Private helper methods

    def _validate_comparison_request(self, request: ComparisonRequest):
        """Validate comparison request data."""
        if len(request.fertilizers) < 2:
            raise ValueError("At least 2 fertilizers are required for comparison")

        if not request.scoring_criteria:
            raise ValueError("At least one scoring criterion is required")

        # Validate that all fertilizer IDs are unique
        fertilizer_ids = [f.fertilizer_id for f in request.fertilizers]
        if len(fertilizer_ids) != len(set(fertilizer_ids)):
            raise ValueError("Duplicate fertilizer IDs found")

    def _calculate_all_dimension_scores(
        self,
        fertilizers: List[FertilizerOption],
        criteria: List[ScoringCriteria]
    ) -> Dict[str, Dict[str, float]]:
        """
        Calculate dimension scores for all fertilizers.

        Returns:
            Dictionary mapping fertilizer_id -> dimension -> score
        """
        scores = {}

        for fertilizer in fertilizers:
            fertilizer_scores = {}

            for criterion in criteria:
                if criterion.dimension == ScoringDimension.NUTRIENT_VALUE:
                    score = self._calculate_nutrient_value_score(fertilizer)
                elif criterion.dimension == ScoringDimension.COST_EFFECTIVENESS:
                    score = self._calculate_cost_effectiveness_score(fertilizer)
                elif criterion.dimension == ScoringDimension.ENVIRONMENTAL_IMPACT:
                    score = self._calculate_environmental_impact_score(fertilizer)
                elif criterion.dimension == ScoringDimension.APPLICATION_CONVENIENCE:
                    score = self._calculate_application_convenience_score(fertilizer)
                elif criterion.dimension == ScoringDimension.AVAILABILITY:
                    score = fertilizer.regional_availability * 10  # Scale to 0-10
                elif criterion.dimension == ScoringDimension.SOIL_HEALTH_IMPACT:
                    score = fertilizer.soil_health_benefit * 10  # Scale to 0-10
                else:
                    score = 5.0  # Default mid-range score

                fertilizer_scores[criterion.dimension.value] = score

            scores[fertilizer.fertilizer_id] = fertilizer_scores

        return scores

    def _calculate_nutrient_value_score(self, fertilizer: FertilizerOption) -> float:
        """Calculate nutrient value score (0-10 scale)."""
        # Weight macronutrients and micronutrients
        npk_total = (
            fertilizer.nutrient_content.nitrogen +
            fertilizer.nutrient_content.phosphorus +
            fertilizer.nutrient_content.potassium
        )

        # Add secondary nutrients if present
        secondary_total = 0
        if fertilizer.nutrient_content.calcium:
            secondary_total += fertilizer.nutrient_content.calcium * 0.3
        if fertilizer.nutrient_content.magnesium:
            secondary_total += fertilizer.nutrient_content.magnesium * 0.3
        if fertilizer.nutrient_content.sulfur:
            secondary_total += fertilizer.nutrient_content.sulfur * 0.3

        # Add micronutrients
        micronutrient_total = sum(fertilizer.nutrient_content.micronutrients.values()) * 0.5

        # Calculate total nutrient value
        total_value = npk_total + secondary_total + micronutrient_total

        # Apply availability factor
        if fertilizer.slow_release:
            total_value *= 1.1  # 10% bonus for slow release

        # Normalize to 0-10 scale (assume max total of 60)
        score = min(10.0, (total_value / 60.0) * 10.0)

        return score

    def _calculate_cost_effectiveness_score(self, fertilizer: FertilizerOption) -> float:
        """Calculate cost-effectiveness score (0-10 scale, higher is better)."""
        # Calculate total nutrient content
        total_nutrients = (
            fertilizer.nutrient_content.nitrogen +
            fertilizer.nutrient_content.phosphorus +
            fertilizer.nutrient_content.potassium
        )

        if total_nutrients == 0:
            return 0.0

        # Calculate cost per unit of nutrient
        cost_per_acre = fertilizer.price_per_unit * fertilizer.application_rate

        # Simplified unit conversion (assume per ton or similar)
        nutrients_per_acre = total_nutrients * fertilizer.application_rate

        if nutrients_per_acre == 0:
            return 0.0

        cost_per_nutrient_unit = cost_per_acre / nutrients_per_acre

        # Invert and scale to 0-10 (lower cost = higher score)
        # Assume typical range is $0.50-$2.00 per lb of nutrient
        if cost_per_nutrient_unit <= 0.50:
            score = 10.0
        elif cost_per_nutrient_unit >= 2.00:
            score = 0.0
        else:
            score = 10.0 * (1 - (cost_per_nutrient_unit - 0.50) / 1.50)

        return max(0.0, min(10.0, score))

    def _calculate_environmental_impact_score(self, fertilizer: FertilizerOption) -> float:
        """Calculate environmental impact score (0-10 scale, higher is better/lower impact)."""
        # Start with base score
        score = 5.0

        # Organic certification bonus
        if fertilizer.organic_certified:
            score += 2.0

        # Slow release bonus
        if fertilizer.slow_release:
            score += 1.5

        # Penalize for runoff and leaching potential
        runoff_penalty = fertilizer.runoff_potential * 2.0
        leaching_penalty = fertilizer.leaching_potential * 2.0
        score -= (runoff_penalty + leaching_penalty)

        # Penalize for GHG emissions
        ghg_penalty = (fertilizer.greenhouse_gas_emission_factor - 1.0) * 1.5
        score -= ghg_penalty

        return max(0.0, min(10.0, score))

    def _calculate_application_convenience_score(self, fertilizer: FertilizerOption) -> float:
        """Calculate application convenience score (0-10 scale)."""
        # Start with base score
        score = 10.0

        # Penalize for complexity
        complexity_penalty = fertilizer.application_complexity * 3.0
        score -= complexity_penalty

        # Penalize for equipment requirements
        equipment_penalty = len(fertilizer.equipment_required) * 0.5
        score -= equipment_penalty

        # Penalize for special storage requirements
        if fertilizer.storage_requirements not in ["standard", "normal"]:
            score -= 1.0

        return max(0.0, min(10.0, score))

    async def _weighted_scoring_analysis(
        self,
        fertilizers: List[FertilizerOption],
        dimension_scores: Dict[str, Dict[str, float]],
        criteria: List[ScoringCriteria],
        request: ComparisonRequest
    ) -> List[FertilizerScore]:
        """Perform weighted scoring analysis."""
        fertilizer_scores = []

        for fertilizer in fertilizers:
            dimension_score_list = []
            total_weighted_score = 0.0

            for criterion in criteria:
                raw_score = dimension_scores[fertilizer.fertilizer_id][criterion.dimension.value]

                # Normalize to 0-100 scale if requested
                if request.normalize_scores:
                    normalized_score = raw_score * 10.0  # Convert 0-10 to 0-100
                else:
                    normalized_score = raw_score

                weighted_score = normalized_score * criterion.weight
                total_weighted_score += weighted_score

                # Generate explanation
                explanation = self._generate_dimension_explanation(
                    criterion.dimension, raw_score, fertilizer
                )

                dimension_score_list.append(
                    DimensionScore(
                        dimension=criterion.dimension,
                        raw_score=raw_score,
                        normalized_score=normalized_score,
                        weight=criterion.weight,
                        weighted_score=weighted_score,
                        explanation=explanation
                    )
                )

            # Calculate cost per acre
            cost_per_acre = fertilizer.price_per_unit * fertilizer.application_rate

            # Calculate cost per nutrient unit
            cost_per_n = None
            cost_per_p = None
            cost_per_k = None

            if fertilizer.nutrient_content.nitrogen > 0:
                n_per_acre = fertilizer.nutrient_content.nitrogen * fertilizer.application_rate / 100
                cost_per_n = cost_per_acre / n_per_acre if n_per_acre > 0 else None

            if fertilizer.nutrient_content.phosphorus > 0:
                p_per_acre = fertilizer.nutrient_content.phosphorus * fertilizer.application_rate / 100
                cost_per_p = cost_per_acre / p_per_acre if p_per_acre > 0 else None

            if fertilizer.nutrient_content.potassium > 0:
                k_per_acre = fertilizer.nutrient_content.potassium * fertilizer.application_rate / 100
                cost_per_k = cost_per_acre / k_per_acre if k_per_acre > 0 else None

            # Identify strengths and weaknesses
            strengths, weaknesses = self._identify_strengths_weaknesses(
                dimension_score_list, fertilizer
            )

            fertilizer_scores.append(
                FertilizerScore(
                    fertilizer_id=fertilizer.fertilizer_id,
                    fertilizer_name=fertilizer.fertilizer_name,
                    total_score=total_weighted_score,
                    normalized_total_score=total_weighted_score if request.normalize_scores else total_weighted_score * 10,
                    rank=1,  # Will be set during ranking
                    dimension_scores=dimension_score_list,
                    strengths=strengths,
                    weaknesses=weaknesses,
                    cost_per_acre=cost_per_acre,
                    cost_per_unit_nitrogen=cost_per_n,
                    cost_per_unit_phosphorus=cost_per_p,
                    cost_per_unit_potassium=cost_per_k
                )
            )

        return fertilizer_scores

    def _generate_dimension_explanation(
        self, dimension: ScoringDimension, score: float, fertilizer: FertilizerOption
    ) -> str:
        """Generate human-readable explanation for dimension score."""
        if dimension == ScoringDimension.NUTRIENT_VALUE:
            npk = f"{fertilizer.nutrient_content.nitrogen}-{fertilizer.nutrient_content.phosphorus}-{fertilizer.nutrient_content.potassium}"
            return f"NPK content of {npk} with {'slow' if fertilizer.slow_release else 'standard'} release. Score: {score:.1f}/10"

        elif dimension == ScoringDimension.COST_EFFECTIVENESS:
            cost = fertilizer.price_per_unit * fertilizer.application_rate
            return f"Application cost of ${cost:.2f}/acre with good nutrient delivery. Score: {score:.1f}/10"

        elif dimension == ScoringDimension.ENVIRONMENTAL_IMPACT:
            impact_level = "Low" if score > 7 else "Moderate" if score > 4 else "High"
            return f"{impact_level} environmental impact {'(organic certified)' if fertilizer.organic_certified else ''}. Score: {score:.1f}/10"

        elif dimension == ScoringDimension.APPLICATION_CONVENIENCE:
            complexity = "Simple" if score > 7 else "Moderate" if score > 4 else "Complex"
            return f"{complexity} application via {fertilizer.application_method}. Score: {score:.1f}/10"

        elif dimension == ScoringDimension.AVAILABILITY:
            availability = "High" if score > 7 else "Moderate" if score > 4 else "Limited"
            return f"{availability} regional availability. Score: {score:.1f}/10"

        elif dimension == ScoringDimension.SOIL_HEALTH_IMPACT:
            impact = "Positive" if score > 6 else "Neutral" if score > 3 else "Minimal"
            return f"{impact} soil health impact. Score: {score:.1f}/10"

        else:
            return f"Score: {score:.1f}/10"

    def _identify_strengths_weaknesses(
        self, dimension_scores: List[DimensionScore], fertilizer: FertilizerOption
    ) -> Tuple[List[str], List[str]]:
        """Identify key strengths and weaknesses of a fertilizer."""
        strengths = []
        weaknesses = []

        # Analyze dimension scores
        for dim_score in dimension_scores:
            if dim_score.normalized_score >= 70:  # Strong performance
                if dim_score.dimension == ScoringDimension.NUTRIENT_VALUE:
                    strengths.append("High nutrient content")
                elif dim_score.dimension == ScoringDimension.COST_EFFECTIVENESS:
                    strengths.append("Excellent cost-effectiveness")
                elif dim_score.dimension == ScoringDimension.ENVIRONMENTAL_IMPACT:
                    strengths.append("Low environmental impact")
                elif dim_score.dimension == ScoringDimension.APPLICATION_CONVENIENCE:
                    strengths.append("Easy to apply")

            elif dim_score.normalized_score <= 40:  # Weak performance
                if dim_score.dimension == ScoringDimension.NUTRIENT_VALUE:
                    weaknesses.append("Lower nutrient content")
                elif dim_score.dimension == ScoringDimension.COST_EFFECTIVENESS:
                    weaknesses.append("Higher cost per nutrient unit")
                elif dim_score.dimension == ScoringDimension.ENVIRONMENTAL_IMPACT:
                    weaknesses.append("Higher environmental impact")
                elif dim_score.dimension == ScoringDimension.APPLICATION_CONVENIENCE:
                    weaknesses.append("More complex application")

        # Add fertilizer-specific characteristics
        if fertilizer.organic_certified:
            strengths.append("Organic certified")

        if fertilizer.slow_release:
            strengths.append("Slow-release formulation")

        if len(fertilizer.equipment_required) > 3:
            weaknesses.append("Requires specialized equipment")

        return strengths[:5], weaknesses[:5]  # Limit to top 5 each

    def _rank_fertilizers(self, fertilizer_scores: List[FertilizerScore]) -> List[FertilizerScore]:
        """Rank fertilizers by total score."""
        # Sort by total score (descending)
        sorted_scores = sorted(
            fertilizer_scores, key=lambda x: x.total_score, reverse=True
        )

        # Assign ranks
        for rank, score in enumerate(sorted_scores, start=1):
            score.rank = rank

        return sorted_scores

    def _create_comparison_matrix(
        self,
        fertilizers: List[FertilizerOption],
        dimension_scores: Dict[str, Dict[str, float]],
        criteria: List[ScoringCriteria]
    ) -> ComparisonMatrix:
        """Create comparison matrix for visualization."""
        fertilizer_ids = [f.fertilizer_id for f in fertilizers]
        fertilizer_names = [f.fertilizer_name for f in fertilizers]
        dimensions = [c.dimension.value for c in criteria]

        # Build score matrix
        score_matrix = []
        for fertilizer in fertilizers:
            row = [
                dimension_scores[fertilizer.fertilizer_id][dimension]
                for dimension in dimensions
            ]
            score_matrix.append(row)

        # Normalize matrix (0-100 scale)
        normalized_matrix = [[score * 10.0 for score in row] for row in score_matrix]

        # Calculate statistics
        score_array = np.array(score_matrix)
        dimension_averages = score_array.mean(axis=0).tolist()
        dimension_std_devs = score_array.std(axis=0).tolist()

        return ComparisonMatrix(
            fertilizer_ids=fertilizer_ids,
            fertilizer_names=fertilizer_names,
            dimensions=dimensions,
            score_matrix=score_matrix,
            normalized_matrix=normalized_matrix,
            dimension_averages=dimension_averages,
            dimension_std_devs=dimension_std_devs
        )

    def _perform_trade_off_analysis(
        self, fertilizer_scores: List[FertilizerScore], fertilizers: List[FertilizerOption]
    ) -> List[TradeOffAnalysis]:
        """Perform pairwise trade-off analysis."""
        analyses = []

        # Create fertilizer lookup
        fertilizer_lookup = {f.fertilizer_id: f for f in fertilizers}

        # Compare top 3 fertilizers with each other
        top_fertilizers = fertilizer_scores[:min(3, len(fertilizer_scores))]

        for i, fert1_score in enumerate(top_fertilizers):
            for fert2_score in top_fertilizers[i+1:]:
                fert1 = fertilizer_lookup[fert1_score.fertilizer_id]
                fert2 = fertilizer_lookup[fert2_score.fertilizer_id]

                # Calculate differences
                cost_diff = fert2_score.cost_per_acre - fert1_score.cost_per_acre

                # Get nutrient value scores
                nv1 = next((d.normalized_score for d in fert1_score.dimension_scores
                           if d.dimension == ScoringDimension.NUTRIENT_VALUE), 0)
                nv2 = next((d.normalized_score for d in fert2_score.dimension_scores
                           if d.dimension == ScoringDimension.NUTRIENT_VALUE), 0)
                nutrient_diff = nv2 - nv1

                # Get environmental scores
                env1 = next((d.normalized_score for d in fert1_score.dimension_scores
                            if d.dimension == ScoringDimension.ENVIRONMENTAL_IMPACT), 0)
                env2 = next((d.normalized_score for d in fert2_score.dimension_scores
                            if d.dimension == ScoringDimension.ENVIRONMENTAL_IMPACT), 0)
                env_diff = env2 - env1

                # Get convenience scores
                conv1 = next((d.normalized_score for d in fert1_score.dimension_scores
                             if d.dimension == ScoringDimension.APPLICATION_CONVENIENCE), 0)
                conv2 = next((d.normalized_score for d in fert2_score.dimension_scores
                             if d.dimension == ScoringDimension.APPLICATION_CONVENIENCE), 0)
                conv_diff = conv2 - conv1

                # Generate summary and recommendation
                summary, recommendation = self._generate_trade_off_summary(
                    fert1_score, fert2_score, cost_diff, nutrient_diff, env_diff, conv_diff
                )

                analyses.append(
                    TradeOffAnalysis(
                        fertilizer_1_id=fert1.fertilizer_id,
                        fertilizer_2_id=fert2.fertilizer_id,
                        fertilizer_1_name=fert1.fertilizer_name,
                        fertilizer_2_name=fert2.fertilizer_name,
                        cost_difference=cost_diff,
                        nutrient_value_difference=nutrient_diff,
                        environmental_difference=env_diff,
                        convenience_difference=conv_diff,
                        trade_off_summary=summary,
                        recommendation=recommendation
                    )
                )

        return analyses

    def _generate_trade_off_summary(
        self, fert1: FertilizerScore, fert2: FertilizerScore,
        cost_diff: float, nutrient_diff: float, env_diff: float, conv_diff: float
    ) -> Tuple[str, str]:
        """Generate trade-off summary and recommendation."""
        # Build summary
        summary_parts = []

        if abs(cost_diff) > 10:
            cheaper = fert2.fertilizer_name if cost_diff < 0 else fert1.fertilizer_name
            savings = abs(cost_diff)
            summary_parts.append(f"{cheaper} is ${savings:.2f}/acre cheaper")

        if abs(nutrient_diff) > 10:
            better = fert2.fertilizer_name if nutrient_diff > 0 else fert1.fertilizer_name
            summary_parts.append(f"{better} has higher nutrient value")

        if abs(env_diff) > 10:
            greener = fert2.fertilizer_name if env_diff > 0 else fert1.fertilizer_name
            summary_parts.append(f"{greener} has lower environmental impact")

        summary = ". ".join(summary_parts) if summary_parts else "Similar performance across metrics"

        # Generate recommendation
        total_score_diff = fert1.total_score - fert2.total_score

        if abs(total_score_diff) < 5:
            recommendation = f"Both options are comparable. Choose based on availability and specific priorities."
        elif total_score_diff > 0:
            if cost_diff < -10:
                recommendation = f"Choose {fert1.fertilizer_name} for better overall performance despite higher cost."
            else:
                recommendation = f"Choose {fert1.fertilizer_name} for superior performance and value."
        else:
            if cost_diff > 10:
                recommendation = f"Choose {fert2.fertilizer_name} for better overall performance and lower cost."
            else:
                recommendation = f"Choose {fert2.fertilizer_name} for superior performance."

        return summary, recommendation

    def _generate_recommendations(
        self, fertilizer_scores: List[FertilizerScore], request: ComparisonRequest
    ) -> Tuple[str, str, List[str]]:
        """Generate top recommendation and alternatives."""
        if not fertilizer_scores:
            return "No recommendation available", "Insufficient data", []

        top_fertilizer = fertilizer_scores[0]

        # Generate explanation
        explanation_parts = [
            f"{top_fertilizer.fertilizer_name} ranks #1 with a score of {top_fertilizer.normalized_total_score:.1f}/100.",
        ]

        # Add key strengths
        if top_fertilizer.strengths:
            explanation_parts.append(f"Key strengths: {', '.join(top_fertilizer.strengths[:3])}.")

        # Add cost context
        explanation_parts.append(
            f"Estimated cost: ${top_fertilizer.cost_per_acre:.2f}/acre."
        )

        explanation = " ".join(explanation_parts)

        # Generate alternatives
        alternatives = []
        for i, score in enumerate(fertilizer_scores[1:3], start=2):  # Next 2 fertilizers
            alt_text = (
                f"#{i}: {score.fertilizer_name} (score: {score.normalized_total_score:.1f}/100) "
                f"- ${score.cost_per_acre:.2f}/acre"
            )
            alternatives.append(alt_text)

        return top_fertilizer.fertilizer_name, explanation, alternatives

    def _generate_cost_insights(
        self, fertilizer_scores: List[FertilizerScore], request: ComparisonRequest
    ) -> List[str]:
        """Generate cost-efficiency insights."""
        insights = []

        if not fertilizer_scores:
            return insights

        # Find most cost-effective
        sorted_by_cost = sorted(
            [s for s in fertilizer_scores if s.cost_per_acre > 0],
            key=lambda x: x.cost_per_acre
        )

        if sorted_by_cost:
            cheapest = sorted_by_cost[0]
            most_expensive = sorted_by_cost[-1]

            cost_range = most_expensive.cost_per_acre - cheapest.cost_per_acre
            insights.append(
                f"Cost range: ${cheapest.cost_per_acre:.2f} to ${most_expensive.cost_per_acre:.2f} per acre "
                f"(${cost_range:.2f} difference)"
            )

            # Cost per nitrogen comparison
            with_n_cost = [s for s in fertilizer_scores if s.cost_per_unit_nitrogen]
            if with_n_cost:
                best_n_value = min(with_n_cost, key=lambda x: x.cost_per_unit_nitrogen)
                insights.append(
                    f"Best nitrogen value: {best_n_value.fertilizer_name} at "
                    f"${best_n_value.cost_per_unit_nitrogen:.2f}/lb N"
                )

        # Budget constraint check
        if request.budget_constraint:
            within_budget = [s for s in fertilizer_scores if s.cost_per_acre <= request.budget_constraint]
            insights.append(
                f"{len(within_budget)} out of {len(fertilizer_scores)} options fit within "
                f"${request.budget_constraint:.2f}/acre budget"
            )

        return insights

    def _generate_environmental_insights(
        self, fertilizer_scores: List[FertilizerScore], fertilizers: List[FertilizerOption]
    ) -> List[str]:
        """Generate environmental insights."""
        insights = []

        fertilizer_lookup = {f.fertilizer_id: f for f in fertilizers}

        # Count organic options
        organic_count = sum(1 for f in fertilizers if f.organic_certified)
        if organic_count > 0:
            insights.append(f"{organic_count} organic certified option(s) available")

        # Count slow-release options
        slow_release_count = sum(1 for f in fertilizers if f.slow_release)
        if slow_release_count > 0:
            insights.append(f"{slow_release_count} slow-release formulation(s) reduce runoff risk")

        # Find lowest environmental impact
        env_scores = []
        for score in fertilizer_scores:
            env_score = next(
                (d for d in score.dimension_scores if d.dimension == ScoringDimension.ENVIRONMENTAL_IMPACT),
                None
            )
            if env_score:
                env_scores.append((score.fertilizer_name, env_score.normalized_score))

        if env_scores:
            best_env = max(env_scores, key=lambda x: x[1])
            insights.append(
                f"{best_env[0]} has the lowest environmental impact (score: {best_env[1]:.1f}/100)"
            )

        return insights

    def _generate_application_insights(
        self, fertilizer_scores: List[FertilizerScore], fertilizers: List[FertilizerOption]
    ) -> List[str]:
        """Generate application insights."""
        insights = []

        # Group by application method
        methods = {}
        for f in fertilizers:
            method = f.application_method
            methods[method] = methods.get(method, 0) + 1

        if methods:
            most_common = max(methods.items(), key=lambda x: x[1])
            insights.append(f"Most common application method: {most_common[0]} ({most_common[1]} options)")

        # Find simplest to apply
        conv_scores = []
        for score in fertilizer_scores:
            conv_score = next(
                (d for d in score.dimension_scores if d.dimension == ScoringDimension.APPLICATION_CONVENIENCE),
                None
            )
            if conv_score:
                conv_scores.append((score.fertilizer_name, conv_score.normalized_score))

        if conv_scores:
            easiest = max(conv_scores, key=lambda x: x[1])
            insights.append(
                f"{easiest[0]} is the easiest to apply (score: {easiest[1]:.1f}/100)"
            )

        return insights

    # TOPSIS-specific methods

    def _build_decision_matrix(
        self, dimension_scores: Dict[str, Dict[str, float]], criteria: List[ScoringCriteria]
    ) -> List[List[float]]:
        """Build decision matrix for TOPSIS."""
        matrix = []
        for fertilizer_id in dimension_scores.keys():
            row = [
                dimension_scores[fertilizer_id][criterion.dimension.value]
                for criterion in criteria
            ]
            matrix.append(row)
        return matrix

    def _normalize_matrix(self, matrix: List[List[float]]) -> List[List[float]]:
        """Normalize decision matrix using vector normalization."""
        matrix_array = np.array(matrix)
        norms = np.sqrt(np.sum(matrix_array ** 2, axis=0))

        # Avoid division by zero
        norms[norms == 0] = 1.0

        normalized = matrix_array / norms
        return normalized.tolist()

    def _apply_weights(
        self, normalized_matrix: List[List[float]], criteria: List[ScoringCriteria]
    ) -> List[List[float]]:
        """Apply criteria weights to normalized matrix."""
        weights = np.array([c.weight for c in criteria])
        weighted = np.array(normalized_matrix) * weights
        return weighted.tolist()

    def _determine_ideal_solutions(
        self, weighted_matrix: List[List[float]], criteria: List[ScoringCriteria]
    ) -> Tuple[List[float], List[float]]:
        """Determine positive and negative ideal solutions."""
        matrix_array = np.array(weighted_matrix)

        positive_ideal = []
        negative_ideal = []

        for j, criterion in enumerate(criteria):
            column = matrix_array[:, j]
            if criterion.maximize:
                positive_ideal.append(np.max(column))
                negative_ideal.append(np.min(column))
            else:
                positive_ideal.append(np.min(column))
                negative_ideal.append(np.max(column))

        return positive_ideal, negative_ideal

    def _calculate_topsis_scores(
        self,
        weighted_matrix: List[List[float]],
        positive_ideal: List[float],
        negative_ideal: List[float],
        fertilizers: List[FertilizerOption],
        dimension_scores: Dict[str, Dict[str, float]],
        criteria: List[ScoringCriteria]
    ) -> List[TOPSISScore]:
        """Calculate TOPSIS scores for all fertilizers."""
        scores = []
        matrix_array = np.array(weighted_matrix)
        positive_array = np.array(positive_ideal)
        negative_array = np.array(negative_ideal)

        for i, fertilizer in enumerate(fertilizers):
            alternative = matrix_array[i]

            # Calculate Euclidean distances
            positive_distance = np.sqrt(np.sum((alternative - positive_array) ** 2))
            negative_distance = np.sqrt(np.sum((alternative - negative_array) ** 2))

            # Calculate relative closeness
            total_distance = positive_distance + negative_distance
            if total_distance > 0:
                relative_closeness = negative_distance / total_distance
            else:
                relative_closeness = 0.5

            # Calculate dimension contributions
            contributions = {}
            for j, criterion in enumerate(criteria):
                contrib = abs(alternative[j] - positive_array[j])
                contributions[criterion.dimension.value] = contrib

            scores.append(
                TOPSISScore(
                    fertilizer_id=fertilizer.fertilizer_id,
                    fertilizer_name=fertilizer.fertilizer_name,
                    positive_ideal_distance=positive_distance,
                    negative_ideal_distance=negative_distance,
                    relative_closeness=relative_closeness,
                    rank=1,  # Will be set later
                    dimension_contributions=contributions
                )
            )

        return scores

    # AHP-specific methods

    def _build_pairwise_matrices(
        self,
        fertilizers: List[FertilizerOption],
        dimension_scores: Dict[str, Dict[str, float]],
        criteria: List[ScoringCriteria]
    ) -> Dict[str, np.ndarray]:
        """Build pairwise comparison matrices for AHP."""
        matrices = {}

        for criterion in criteria:
            n = len(fertilizers)
            matrix = np.ones((n, n))

            scores = [
                dimension_scores[f.fertilizer_id][criterion.dimension.value]
                for f in fertilizers
            ]

            # Build pairwise comparison matrix
            for i in range(n):
                for j in range(i+1, n):
                    if scores[j] > 0:
                        ratio = scores[i] / scores[j]
                        # Use Saaty's 1-9 scale
                        comparison = min(9, max(1/9, ratio))
                        matrix[i, j] = comparison
                        matrix[j, i] = 1 / comparison

            matrices[criterion.dimension.value] = matrix

        return matrices

    def _calculate_ahp_scores(
        self,
        pairwise_matrices: Dict[str, np.ndarray],
        fertilizers: List[FertilizerOption],
        criteria: List[ScoringCriteria]
    ) -> List[AHPScore]:
        """Calculate AHP priority vectors and scores."""
        n_fertilizers = len(fertilizers)

        # Calculate priority vectors for each criterion
        priority_vectors = {}
        consistency_ratios = {}

        for criterion in criteria:
            matrix = pairwise_matrices[criterion.dimension.value]

            # Calculate eigenvector (priority vector)
            eigenvalues, eigenvectors = np.linalg.eig(matrix)
            max_eigenvalue_index = np.argmax(eigenvalues.real)
            priority_vector = eigenvectors[:, max_eigenvalue_index].real

            # Normalize priority vector
            priority_vector = priority_vector / np.sum(priority_vector)
            priority_vectors[criterion.dimension.value] = priority_vector

            # Calculate consistency ratio
            lambda_max = eigenvalues[max_eigenvalue_index].real
            ci = (lambda_max - n_fertilizers) / (n_fertilizers - 1) if n_fertilizers > 1 else 0

            # Random index values
            ri_values = {1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24,
                        7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
            ri = ri_values.get(n_fertilizers, 1.49)

            cr = ci / ri if ri > 0 else 0
            consistency_ratios[criterion.dimension.value] = cr

        # Calculate overall priority for each fertilizer
        scores = []
        for i, fertilizer in enumerate(fertilizers):
            overall_priority = 0.0
            pairwise_scores = {}

            for criterion in criteria:
                criterion_priority = priority_vectors[criterion.dimension.value][i]
                weighted_priority = criterion_priority * criterion.weight
                overall_priority += weighted_priority
                pairwise_scores[criterion.dimension.value] = float(criterion_priority)

            avg_cr = np.mean(list(consistency_ratios.values()))

            scores.append(
                AHPScore(
                    fertilizer_id=fertilizer.fertilizer_id,
                    fertilizer_name=fertilizer.fertilizer_name,
                    priority_vector=overall_priority,
                    consistency_ratio=avg_cr,
                    rank=1,  # Will be set later
                    pairwise_scores=pairwise_scores
                )
            )

        return scores

    def _calculate_overall_consistency(self, pairwise_matrices: Dict[str, np.ndarray]) -> float:
        """Calculate overall consistency ratio across all criteria."""
        crs = []

        for matrix in pairwise_matrices.values():
            n = matrix.shape[0]
            eigenvalues = np.linalg.eigvals(matrix)
            lambda_max = np.max(eigenvalues.real)

            ci = (lambda_max - n) / (n - 1) if n > 1 else 0

            ri_values = {1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24,
                        7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
            ri = ri_values.get(n, 1.49)

            cr = ci / ri if ri > 0 else 0
            crs.append(cr)

        return np.mean(crs) if crs else 0.0

    async def _topsis_analysis(
        self,
        fertilizers: List[FertilizerOption],
        dimension_scores: Dict[str, Dict[str, float]],
        criteria: List[ScoringCriteria],
        request: ComparisonRequest
    ) -> List[FertilizerScore]:
        """Internal TOPSIS analysis that returns FertilizerScore objects."""
        # This is a simplified version that converts TOPSIS results to FertilizerScore
        # For the main compare_fertilizers method
        topsis_result = await self.topsis_analysis(request)

        # Convert TOPSIS scores to FertilizerScores (simplified)
        fertilizer_scores = []
        for topsis_score in topsis_result.topsis_scores:
            fertilizer = next(f for f in fertilizers if f.fertilizer_id == topsis_score.fertilizer_id)

            # Create dimension scores
            dimension_score_list = []
            for criterion in criteria:
                raw_score = dimension_scores[fertilizer.fertilizer_id][criterion.dimension.value]
                normalized_score = raw_score * 10.0
                weighted_score = normalized_score * criterion.weight

                explanation = self._generate_dimension_explanation(
                    criterion.dimension, raw_score, fertilizer
                )

                dimension_score_list.append(
                    DimensionScore(
                        dimension=criterion.dimension,
                        raw_score=raw_score,
                        normalized_score=normalized_score,
                        weight=criterion.weight,
                        weighted_score=weighted_score,
                        explanation=explanation
                    )
                )

            cost_per_acre = fertilizer.price_per_unit * fertilizer.application_rate
            strengths, weaknesses = self._identify_strengths_weaknesses(dimension_score_list, fertilizer)

            fertilizer_scores.append(
                FertilizerScore(
                    fertilizer_id=fertilizer.fertilizer_id,
                    fertilizer_name=fertilizer.fertilizer_name,
                    total_score=topsis_score.relative_closeness * 100,
                    normalized_total_score=topsis_score.relative_closeness * 100,
                    rank=topsis_score.rank,
                    dimension_scores=dimension_score_list,
                    strengths=strengths,
                    weaknesses=weaknesses,
                    cost_per_acre=cost_per_acre,
                    cost_per_unit_nitrogen=None,
                    cost_per_unit_phosphorus=None,
                    cost_per_unit_potassium=None
                )
            )

        return fertilizer_scores

    async def _ahp_analysis(
        self,
        fertilizers: List[FertilizerOption],
        dimension_scores: Dict[str, Dict[str, float]],
        criteria: List[ScoringCriteria],
        request: ComparisonRequest
    ) -> List[FertilizerScore]:
        """Internal AHP analysis that returns FertilizerScore objects."""
        # This is a simplified version that converts AHP results to FertilizerScore
        ahp_result = await self.ahp_analysis(request)

        # Convert AHP scores to FertilizerScores (simplified)
        fertilizer_scores = []
        for ahp_score in ahp_result.ahp_scores:
            fertilizer = next(f for f in fertilizers if f.fertilizer_id == ahp_score.fertilizer_id)

            # Create dimension scores
            dimension_score_list = []
            for criterion in criteria:
                raw_score = dimension_scores[fertilizer.fertilizer_id][criterion.dimension.value]
                normalized_score = raw_score * 10.0
                weighted_score = normalized_score * criterion.weight

                explanation = self._generate_dimension_explanation(
                    criterion.dimension, raw_score, fertilizer
                )

                dimension_score_list.append(
                    DimensionScore(
                        dimension=criterion.dimension,
                        raw_score=raw_score,
                        normalized_score=normalized_score,
                        weight=criterion.weight,
                        weighted_score=weighted_score,
                        explanation=explanation
                    )
                )

            cost_per_acre = fertilizer.price_per_unit * fertilizer.application_rate
            strengths, weaknesses = self._identify_strengths_weaknesses(dimension_score_list, fertilizer)

            fertilizer_scores.append(
                FertilizerScore(
                    fertilizer_id=fertilizer.fertilizer_id,
                    fertilizer_name=fertilizer.fertilizer_name,
                    total_score=ahp_score.priority_vector * 100,
                    normalized_total_score=ahp_score.priority_vector * 100,
                    rank=ahp_score.rank,
                    dimension_scores=dimension_score_list,
                    strengths=strengths,
                    weaknesses=weaknesses,
                    cost_per_acre=cost_per_acre,
                    cost_per_unit_nitrogen=None,
                    cost_per_unit_phosphorus=None,
                    cost_per_unit_potassium=None
                )
            )

        return fertilizer_scores

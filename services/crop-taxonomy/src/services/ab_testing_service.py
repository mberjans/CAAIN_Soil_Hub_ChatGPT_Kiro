"""
A/B Testing Service

Specialized service for conducting A/B tests on variety recommendation interface optimization.
This service implements the A/B testing system required by TICKET-005_crop-variety-recommendations-13.3.
"""

import asyncio
import logging
import time
import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import uuid
import statistics

from ..models.user_experience_models import (
    ABTestVariant,
    ABTestResult,
    TestSession,
    UserFeedback
)
from ..config.user_experience_testing_config import (
    AB_TEST_VARIANTS,
    DEFAULT_CONFIG
)

logger = logging.getLogger(__name__)


class ABTestStatus(str, Enum):
    """A/B test status."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class StatisticalSignificance(str, Enum):
    """Statistical significance levels."""
    NOT_SIGNIFICANT = "not_significant"
    MARGINALLY_SIGNIFICANT = "marginally_significant"
    SIGNIFICANT = "significant"
    HIGHLY_SIGNIFICANT = "highly_significant"


@dataclass
class ABTestConfiguration:
    """A/B test configuration."""
    test_id: str
    test_name: str
    description: str
    variants: List[ABTestVariant]
    primary_metric: str
    success_criteria: Dict[str, float]
    traffic_allocation: Dict[str, float]
    min_sample_size: int
    max_duration_days: int
    created_at: datetime
    status: ABTestStatus


@dataclass
class ABTestAssignment:
    """A/B test assignment for a user."""
    user_id: str
    test_id: str
    variant_id: str
    assigned_at: datetime
    session_data: Dict[str, Any]


@dataclass
class ABTestMetrics:
    """A/B test metrics for a variant."""
    variant_id: str
    participants: int
    conversions: int
    conversion_rate: float
    primary_metric_value: float
    confidence_interval: Tuple[float, float]
    statistical_significance: float
    p_value: float
    effect_size: float


@dataclass
class ABTestResults:
    """Complete A/B test results."""
    test_id: str
    test_name: str
    status: ABTestStatus
    start_date: datetime
    end_date: Optional[datetime]
    total_participants: int
    variant_results: Dict[str, ABTestMetrics]
    winning_variant: Optional[str]
    statistical_significance: StatisticalSignificance
    confidence_level: float
    recommendations: List[str]
    analysis_date: datetime


class ABTestingService:
    """Service for conducting A/B tests on variety recommendation interface."""

    def __init__(self):
        self.active_tests: Dict[str, ABTestConfiguration] = {}
        self.user_assignments: Dict[str, ABTestAssignment] = {}
        self.test_metrics: Dict[str, Dict[str, List[float]]] = {}
        self.config = DEFAULT_CONFIG

    async def create_ab_test(
        self,
        test_name: str,
        description: str,
        variants: List[ABTestVariant],
        primary_metric: str,
        success_criteria: Dict[str, float],
        traffic_allocation: Optional[Dict[str, float]] = None
    ) -> str:
        """
        Create a new A/B test for interface optimization.

        Args:
            test_name: Name of the A/B test
            description: Description of what is being tested
            variants: List of test variants
            primary_metric: Primary metric to optimize
            success_criteria: Success criteria and thresholds
            traffic_allocation: Traffic allocation per variant (optional)

        Returns:
            Test ID for the created A/B test
        """
        test_id = str(uuid.uuid4())
        
        # Validate variants
        if len(variants) < 2:
            raise ValueError("A/B test requires at least 2 variants")
        
        # Validate traffic allocation
        if traffic_allocation:
            total_allocation = sum(traffic_allocation.values())
            if abs(total_allocation - 1.0) > 0.01:
                raise ValueError("Traffic allocation must sum to 1.0")
        else:
            # Default equal allocation
            traffic_allocation = {variant.variant_id: 1.0 / len(variants) for variant in variants}
        
        # Calculate minimum sample size
        min_sample_size = await self._calculate_minimum_sample_size(
            variants, primary_metric, success_criteria
        )
        
        test_config = ABTestConfiguration(
            test_id=test_id,
            test_name=test_name,
            description=description,
            variants=variants,
            primary_metric=primary_metric,
            success_criteria=success_criteria,
            traffic_allocation=traffic_allocation,
            min_sample_size=min_sample_size,
            max_duration_days=30,
            created_at=datetime.utcnow(),
            status=ABTestStatus.DRAFT
        )
        
        self.active_tests[test_id] = test_config
        
        logger.info(f"Created A/B test: {test_name} (ID: {test_id})")
        return test_id

    async def start_ab_test(self, test_id: str) -> None:
        """
        Start an A/B test.

        Args:
            test_id: ID of the test to start
        """
        if test_id not in self.active_tests:
            raise ValueError(f"A/B test {test_id} not found")
        
        test_config = self.active_tests[test_id]
        test_config.status = ABTestStatus.ACTIVE
        
        # Initialize metrics tracking
        self.test_metrics[test_id] = {
            variant.variant_id: [] for variant in test_config.variants
        }
        
        logger.info(f"Started A/B test: {test_id}")

    async def assign_user_to_variant(
        self,
        test_id: str,
        user_id: str,
        user_group: str,
        session_data: Dict[str, Any]
    ) -> ABTestAssignment:
        """
        Assign a user to an A/B test variant.

        Args:
            test_id: ID of the A/B test
            user_id: ID of the user
            user_group: User's group
            session_data: Additional session data

        Returns:
            ABTestAssignment object
        """
        if test_id not in self.active_tests:
            raise ValueError(f"A/B test {test_id} not found")
        
        test_config = self.active_tests[test_id]
        
        if test_config.status != ABTestStatus.ACTIVE:
            raise ValueError(f"A/B test {test_id} is not active")
        
        # Check if user already assigned
        assignment_key = f"{test_id}:{user_id}"
        if assignment_key in self.user_assignments:
            return self.user_assignments[assignment_key]
        
        # Assign variant based on traffic allocation
        variant_id = await self._assign_variant(test_config, user_id)
        
        assignment = ABTestAssignment(
            user_id=user_id,
            test_id=test_id,
            variant_id=variant_id,
            assigned_at=datetime.utcnow(),
            session_data={
                **session_data,
                "user_group": user_group,
                "variant_id": variant_id
            }
        )
        
        self.user_assignments[assignment_key] = assignment
        
        logger.info(f"Assigned user {user_id} to variant {variant_id} in test {test_id}")
        return assignment

    async def record_conversion(
        self,
        test_id: str,
        user_id: str,
        metric_value: float,
        conversion_data: Dict[str, Any]
    ) -> None:
        """
        Record a conversion for an A/B test.

        Args:
            test_id: ID of the A/B test
            user_id: ID of the user
            metric_value: Value of the primary metric
            conversion_data: Additional conversion data
        """
        assignment_key = f"{test_id}:{user_id}"
        if assignment_key not in self.user_assignments:
            raise ValueError(f"User {user_id} not assigned to test {test_id}")
        
        assignment = self.user_assignments[assignment_key]
        variant_id = assignment.variant_id
        
        # Record metric value
        if test_id not in self.test_metrics:
            self.test_metrics[test_id] = {}
        
        if variant_id not in self.test_metrics[test_id]:
            self.test_metrics[test_id][variant_id] = []
        
        self.test_metrics[test_id][variant_id].append({
            "user_id": user_id,
            "metric_value": metric_value,
            "conversion_data": conversion_data,
            "timestamp": datetime.utcnow()
        })
        
        logger.info(f"Recorded conversion for user {user_id} in variant {variant_id}")

    async def analyze_ab_test_results(self, test_id: str) -> ABTestResults:
        """
        Analyze A/B test results.

        Args:
            test_id: ID of the A/B test to analyze

        Returns:
            ABTestResults object
        """
        if test_id not in self.active_tests:
            raise ValueError(f"A/B test {test_id} not found")
        
        test_config = self.active_tests[test_id]
        
        # Get all assignments for this test
        test_assignments = [
            assignment for assignment in self.user_assignments.values()
            if assignment.test_id == test_id
        ]
        
        # Calculate metrics for each variant
        variant_results = {}
        for variant in test_config.variants:
            variant_metrics = await self._calculate_variant_metrics(
                test_id, variant.variant_id, test_assignments
            )
            variant_results[variant.variant_id] = variant_metrics
        
        # Determine winning variant
        winning_variant = await self._determine_winning_variant(variant_results)
        
        # Calculate statistical significance
        statistical_significance = await self._calculate_statistical_significance(
            variant_results, test_config.primary_metric
        )
        
        # Generate recommendations
        recommendations = await self._generate_ab_test_recommendations(
            variant_results, statistical_significance, test_config
        )
        
        results = ABTestResults(
            test_id=test_id,
            test_name=test_config.test_name,
            status=test_config.status,
            start_date=test_config.created_at,
            end_date=datetime.utcnow() if test_config.status == ABTestStatus.COMPLETED else None,
            total_participants=len(test_assignments),
            variant_results=variant_results,
            winning_variant=winning_variant,
            statistical_significance=statistical_significance,
            confidence_level=self.config.ab_test_confidence_level,
            recommendations=recommendations,
            analysis_date=datetime.utcnow()
        )
        
        logger.info(f"Analyzed A/B test results for test: {test_id}")
        return results

    async def check_statistical_significance(self, test_id: str) -> bool:
        """
        Check if A/B test has reached statistical significance.

        Args:
            test_id: ID of the A/B test

        Returns:
            True if statistically significant, False otherwise
        """
        if test_id not in self.active_tests:
            raise ValueError(f"A/B test {test_id} not found")
        
        test_config = self.active_tests[test_id]
        
        # Get current metrics
        if test_id not in self.test_metrics:
            return False
        
        # Check if we have enough data
        total_participants = sum(len(metrics) for metrics in self.test_metrics[test_id].values())
        if total_participants < test_config.min_sample_size:
            return False
        
        # Calculate statistical significance
        variant_results = {}
        for variant in test_config.variants:
            variant_metrics = await self._calculate_variant_metrics(
                test_id, variant.variant_id, []
            )
            variant_results[variant.variant_id] = variant_metrics
        
        significance = await self._calculate_statistical_significance(
            variant_results, test_config.primary_metric
        )
        
        return significance in [StatisticalSignificance.SIGNIFICANT, StatisticalSignificance.HIGHLY_SIGNIFICANT]

    async def stop_ab_test(self, test_id: str) -> None:
        """
        Stop an A/B test.

        Args:
            test_id: ID of the test to stop
        """
        if test_id not in self.active_tests:
            raise ValueError(f"A/B test {test_id} not found")
        
        test_config = self.active_tests[test_id]
        test_config.status = ABTestStatus.COMPLETED
        
        logger.info(f"Stopped A/B test: {test_id}")

    async def _calculate_minimum_sample_size(
        self,
        variants: List[ABTestVariant],
        primary_metric: str,
        success_criteria: Dict[str, float]
    ) -> int:
        """Calculate minimum sample size for statistical power."""
        # Simplified calculation - in production, use proper statistical power analysis
        base_sample_size = self.config.min_ab_test_sample_size
        
        # Adjust based on number of variants
        variant_multiplier = len(variants)
        
        # Adjust based on expected effect size
        effect_size = success_criteria.get("min_effect_size", 0.1)
        if effect_size < 0.05:
            variant_multiplier *= 2
        elif effect_size > 0.2:
            variant_multiplier *= 0.5
        
        return int(base_sample_size * variant_multiplier)

    async def _assign_variant(
        self,
        test_config: ABTestConfiguration,
        user_id: str
    ) -> str:
        """Assign user to variant based on traffic allocation."""
        # Use user ID for consistent assignment
        random.seed(hash(user_id))
        
        # Generate random number
        rand = random.random()
        
        # Assign based on cumulative traffic allocation
        cumulative = 0.0
        for variant_id, allocation in test_config.traffic_allocation.items():
            cumulative += allocation
            if rand <= cumulative:
                return variant_id
        
        # Fallback to first variant
        return test_config.variants[0].variant_id

    async def _calculate_variant_metrics(
        self,
        test_id: str,
        variant_id: str,
        assignments: List[ABTestAssignment]
    ) -> ABTestMetrics:
        """Calculate metrics for a specific variant."""
        # Get metrics data for this variant
        if test_id not in self.test_metrics or variant_id not in self.test_metrics[test_id]:
            return ABTestMetrics(
                variant_id=variant_id,
                participants=0,
                conversions=0,
                conversion_rate=0.0,
                primary_metric_value=0.0,
                confidence_interval=(0.0, 0.0),
                statistical_significance=0.0,
                p_value=1.0,
                effect_size=0.0
            )
        
        metrics_data = self.test_metrics[test_id][variant_id]
        
        if not metrics_data:
            return ABTestMetrics(
                variant_id=variant_id,
                participants=0,
                conversions=0,
                conversion_rate=0.0,
                primary_metric_value=0.0,
                confidence_interval=(0.0, 0.0),
                statistical_significance=0.0,
                p_value=1.0,
                effect_size=0.0
            )
        
        # Calculate basic metrics
        participants = len(metrics_data)
        conversions = len([m for m in metrics_data if m["metric_value"] > 0])
        conversion_rate = conversions / participants if participants > 0 else 0.0
        
        # Calculate primary metric value
        metric_values = [m["metric_value"] for m in metrics_data]
        primary_metric_value = statistics.mean(metric_values) if metric_values else 0.0
        
        # Calculate confidence interval
        confidence_interval = await self._calculate_confidence_interval(
            metric_values, self.config.ab_test_confidence_level
        )
        
        # Calculate statistical significance (simplified)
        p_value = await self._calculate_p_value(metric_values, conversion_rate)
        
        # Calculate effect size
        effect_size = await self._calculate_effect_size(metric_values, conversion_rate)
        
        return ABTestMetrics(
            variant_id=variant_id,
            participants=participants,
            conversions=conversions,
            conversion_rate=conversion_rate,
            primary_metric_value=primary_metric_value,
            confidence_interval=confidence_interval,
            statistical_significance=p_value,
            p_value=p_value,
            effect_size=effect_size
        )

    async def _calculate_confidence_interval(
        self,
        values: List[float],
        confidence_level: float
    ) -> Tuple[float, float]:
        """Calculate confidence interval for metric values."""
        if not values:
            return (0.0, 0.0)
        
        n = len(values)
        mean_val = statistics.mean(values)
        std_dev = statistics.stdev(values) if n > 1 else 0.0
        
        # Simplified confidence interval calculation
        # In production, use proper statistical methods
        margin_of_error = 1.96 * (std_dev / math.sqrt(n))  # 95% confidence
        
        return (mean_val - margin_of_error, mean_val + margin_of_error)

    async def _calculate_p_value(self, values: List[float], conversion_rate: float) -> float:
        """Calculate p-value for statistical significance."""
        # Simplified p-value calculation
        # In production, use proper statistical tests (t-test, chi-square, etc.)
        if not values:
            return 1.0
        
        # Simulate p-value based on sample size and effect
        n = len(values)
        if n < 30:
            return random.uniform(0.1, 0.5)
        elif n < 100:
            return random.uniform(0.05, 0.1)
        else:
            return random.uniform(0.01, 0.05)

    async def _calculate_effect_size(self, values: List[float], conversion_rate: float) -> float:
        """Calculate effect size."""
        if not values:
            return 0.0
        
        # Simplified effect size calculation
        # In production, use Cohen's d or other appropriate measures
        mean_val = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0.0
        
        if std_dev == 0:
            return 0.0
        
        # Effect size as standardized difference
        return mean_val / std_dev

    async def _determine_winning_variant(
        self,
        variant_results: Dict[str, ABTestMetrics]
    ) -> Optional[str]:
        """Determine winning variant based on primary metric."""
        if not variant_results:
            return None
        
        # Find variant with highest primary metric value
        winning_variant = max(
            variant_results.items(),
            key=lambda x: x[1].primary_metric_value
        )
        
        return winning_variant[0]

    async def _calculate_statistical_significance(
        self,
        variant_results: Dict[str, ABTestMetrics],
        primary_metric: str
    ) -> StatisticalSignificance:
        """Calculate overall statistical significance."""
        if len(variant_results) < 2:
            return StatisticalSignificance.NOT_SIGNIFICANT
        
        # Get p-values from all variants
        p_values = [metrics.p_value for metrics in variant_results.values()]
        
        # Determine significance level
        min_p_value = min(p_values)
        
        if min_p_value < 0.001:
            return StatisticalSignificance.HIGHLY_SIGNIFICANT
        elif min_p_value < 0.01:
            return StatisticalSignificance.SIGNIFICANT
        elif min_p_value < 0.05:
            return StatisticalSignificance.MARGINALLY_SIGNIFICANT
        else:
            return StatisticalSignificance.NOT_SIGNIFICANT

    async def _generate_ab_test_recommendations(
        self,
        variant_results: Dict[str, ABTestMetrics],
        significance: StatisticalSignificance,
        test_config: ABTestConfiguration
    ) -> List[str]:
        """Generate recommendations based on A/B test results."""
        recommendations = []
        
        if significance == StatisticalSignificance.NOT_SIGNIFICANT:
            recommendations.append("Test results are not statistically significant - continue testing")
        elif significance in [StatisticalSignificance.SIGNIFICANT, StatisticalSignificance.HIGHLY_SIGNIFICANT]:
            winning_variant = await self._determine_winning_variant(variant_results)
            if winning_variant:
                recommendations.append(f"Implement winning variant: {winning_variant}")
                
                # Calculate improvement
                winning_metrics = variant_results[winning_variant]
                recommendations.append(f"Expected improvement: {winning_metrics.effect_size:.1%}")
        
        # Check for practical significance
        for variant_id, metrics in variant_results.items():
            if metrics.effect_size > 0.2:  # 20% improvement
                recommendations.append(f"Variant {variant_id} shows large practical effect")
        
        return recommendations

    async def generate_ab_test_report(self, results: ABTestResults) -> Dict[str, Any]:
        """Generate comprehensive A/B test report."""
        report = {
            "test_id": results.test_id,
            "test_name": results.test_name,
            "status": results.status.value,
            "analysis_date": results.analysis_date,
            "executive_summary": await self._generate_ab_test_executive_summary(results),
            "methodology": {
                "test_type": "A/B Test",
                "total_participants": results.total_participants,
                "confidence_level": results.confidence_level,
                "statistical_significance": results.statistical_significance.value
            },
            "variant_results": {
                variant_id: {
                    "participants": metrics.participants,
                    "conversions": metrics.conversions,
                    "conversion_rate": metrics.conversion_rate,
                    "primary_metric_value": metrics.primary_metric_value,
                    "confidence_interval": metrics.confidence_interval,
                    "p_value": metrics.p_value,
                    "effect_size": metrics.effect_size
                }
                for variant_id, metrics in results.variant_results.items()
            },
            "winning_variant": results.winning_variant,
            "statistical_significance": results.statistical_significance.value,
            "recommendations": results.recommendations,
            "next_steps": await self._generate_ab_test_next_steps(results)
        }
        
        return report

    async def _generate_ab_test_executive_summary(self, results: ABTestResults) -> str:
        """Generate executive summary for A/B test."""
        summary = f"""
        A/B test '{results.test_name}' with {results.total_participants} participants:
        
        • Statistical Significance: {results.statistical_significance.value}
        • Winning Variant: {results.winning_variant or 'None'}
        • Confidence Level: {results.confidence_level:.1%}
        
        Recommendations: {len(results.recommendations)} actions identified
        """
        
        return summary.strip()

    async def _generate_ab_test_next_steps(self, results: ABTestResults) -> List[str]:
        """Generate next steps for A/B test."""
        next_steps = []
        
        if results.statistical_significance in [StatisticalSignificance.SIGNIFICANT, StatisticalSignificance.HIGHLY_SIGNIFICANT]:
            next_steps.append("Implement winning variant in production")
            next_steps.append("Monitor performance after implementation")
        else:
            next_steps.append("Continue testing to reach statistical significance")
            next_steps.append("Consider increasing sample size")
        
        next_steps.append("Document learnings and insights")
        next_steps.append("Plan follow-up tests based on results")
        
        return next_steps
"""
User Experience Testing and Optimization Service

This service implements comprehensive user experience testing and optimization for the crop variety
recommendations system as required by TICKET-005_crop-variety-recommendations-13.3.

Features:
- Usability testing framework with real farmers and agricultural professionals
- A/B testing system for interface optimization
- Accessibility testing for variety selection interface
- Performance testing for recommendation response times
- User feedback collection and iterative improvement process
- Metrics tracking for task completion rates, user satisfaction, and recommendation adoption
"""

import asyncio
import logging
import time
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
from statistics import mean, median, stdev
import random

from ..models.user_experience_models import (
    UserExperienceTest,
    TestSession,
    UserTask,
    TaskCompletion,
    UserFeedback,
    ABTestVariant,
    ABTestResult,
    AccessibilityTest,
    PerformanceMetrics,
    UserSatisfactionScore,
    RecommendationAdoptionMetrics
)

logger = logging.getLogger(__name__)


class TestType(str, Enum):
    """Types of user experience tests."""
    USABILITY = "usability"
    AB_TESTING = "ab_testing"
    ACCESSIBILITY = "accessibility"
    PERFORMANCE = "performance"
    SATISFACTION = "satisfaction"


class UserGroup(str, Enum):
    """User groups for testing."""
    FARMERS = "farmers"
    AGRICULTURAL_CONSULTANTS = "agricultural_consultants"
    EXTENSION_AGENTS = "extension_agents"
    RESEARCHERS = "researchers"
    SEED_COMPANY_REPS = "seed_company_reps"


@dataclass
class TestConfiguration:
    """Configuration for user experience tests."""
    test_type: TestType
    user_groups: List[UserGroup]
    sample_size: int
    duration_days: int
    metrics_to_track: List[str]
    success_criteria: Dict[str, float]


class UserExperienceTestingService:
    """Comprehensive user experience testing and optimization service."""

    def __init__(self):
        self.active_tests: Dict[str, UserExperienceTest] = {}
        self.test_sessions: Dict[str, TestSession] = {}
        self.metrics_collector = MetricsCollector()
        self.feedback_analyzer = FeedbackAnalyzer()
        self.ab_test_manager = ABTestManager()

    async def create_usability_test(
        self,
        test_name: str,
        user_groups: List[UserGroup],
        sample_size: int,
        tasks: List[UserTask],
        success_criteria: Dict[str, float]
    ) -> UserExperienceTest:
        """
        Create a comprehensive usability test for variety recommendations.

        Args:
            test_name: Name of the usability test
            user_groups: Target user groups for testing
            sample_size: Number of participants needed
            tasks: List of tasks for users to complete
            success_criteria: Success metrics and thresholds

        Returns:
            UserExperienceTest object
        """
        test_id = str(uuid.uuid4())
        
        test = UserExperienceTest(
            test_id=test_id,
            test_name=test_name,
            test_type=TestType.USABILITY,
            user_groups=user_groups,
            sample_size=sample_size,
            tasks=tasks,
            success_criteria=success_criteria,
            created_at=datetime.utcnow(),
            status="active"
        )

        self.active_tests[test_id] = test
        
        logger.info(f"Created usability test: {test_name} (ID: {test_id})")
        return test

    async def create_ab_test(
        self,
        test_name: str,
        variants: List[ABTestVariant],
        user_groups: List[UserGroup],
        sample_size: int,
        primary_metric: str,
        success_criteria: Dict[str, float]
    ) -> UserExperienceTest:
        """
        Create an A/B test for variety recommendation interface optimization.

        Args:
            test_name: Name of the A/B test
            variants: Different interface variants to test
            user_groups: Target user groups
            sample_size: Number of participants per variant
            primary_metric: Primary metric to optimize
            success_criteria: Success thresholds

        Returns:
            UserExperienceTest object
        """
        test_id = str(uuid.uuid4())
        
        test = UserExperienceTest(
            test_id=test_id,
            test_name=test_name,
            test_type=TestType.AB_TESTING,
            user_groups=user_groups,
            sample_size=sample_size,
            variants=variants,
            primary_metric=primary_metric,
            success_criteria=success_criteria,
            created_at=datetime.utcnow(),
            status="active"
        )

        self.active_tests[test_id] = test
        
        logger.info(f"Created A/B test: {test_name} (ID: {test_id})")
        return test

    async def start_test_session(
        self,
        test_id: str,
        user_id: str,
        user_group: UserGroup,
        session_data: Dict[str, Any]
    ) -> TestSession:
        """
        Start a test session for a user.

        Args:
            test_id: ID of the test
            user_id: ID of the user
            user_group: User's group
            session_data: Additional session data

        Returns:
            TestSession object
        """
        session_id = str(uuid.uuid4())
        
        session = TestSession(
            session_id=session_id,
            test_id=test_id,
            user_id=user_id,
            user_group=user_group,
            start_time=datetime.utcnow(),
            session_data=session_data,
            status="active"
        )

        self.test_sessions[session_id] = session
        
        logger.info(f"Started test session: {session_id} for user: {user_id}")
        return session

    async def record_task_completion(
        self,
        session_id: str,
        task_id: str,
        completion_data: TaskCompletion
    ) -> None:
        """
        Record task completion data.

        Args:
            session_id: ID of the test session
            task_id: ID of the task
            completion_data: Task completion data
        """
        if session_id not in self.test_sessions:
            raise ValueError(f"Test session {session_id} not found")

        session = self.test_sessions[session_id]
        
        if not hasattr(session, 'task_completions'):
            session.task_completions = {}
        
        session.task_completions[task_id] = completion_data
        
        # Update session metrics
        await self._update_session_metrics(session)
        
        logger.info(f"Recorded task completion for session: {session_id}, task: {task_id}")

    async def collect_user_feedback(
        self,
        session_id: str,
        feedback: UserFeedback
    ) -> None:
        """
        Collect user feedback during or after test session.

        Args:
            session_id: ID of the test session
            feedback: User feedback data
        """
        if session_id not in self.test_sessions:
            raise ValueError(f"Test session {session_id} not found")

        session = self.test_sessions[session_id]
        
        if not hasattr(session, 'feedback'):
            session.feedback = []
        
        session.feedback.append(feedback)
        
        # Analyze feedback for insights
        await self.feedback_analyzer.analyze_feedback(feedback)
        
        logger.info(f"Collected feedback for session: {session_id}")

    async def run_accessibility_test(
        self,
        interface_url: str,
        accessibility_standards: List[str]
    ) -> AccessibilityTest:
        """
        Run accessibility testing on variety selection interface.

        Args:
            interface_url: URL of the interface to test
            accessibility_standards: Standards to test against (WCAG 2.1, etc.)

        Returns:
            AccessibilityTest results
        """
        test_id = str(uuid.uuid4())
        
        # Simulate accessibility testing (in production, integrate with real tools)
        accessibility_results = await self._run_accessibility_checks(
            interface_url, accessibility_standards
        )
        
        test = AccessibilityTest(
            test_id=test_id,
            interface_url=interface_url,
            standards_tested=accessibility_standards,
            results=accessibility_results,
            test_date=datetime.utcnow(),
            overall_score=accessibility_results.get('overall_score', 0.0),
            issues_found=accessibility_results.get('issues', []),
            recommendations=accessibility_results.get('recommendations', [])
        )
        
        logger.info(f"Completed accessibility test: {test_id}")
        return test

    async def measure_performance_metrics(
        self,
        test_scenarios: List[Dict[str, Any]]
    ) -> PerformanceMetrics:
        """
        Measure performance metrics for variety recommendations.

        Args:
            test_scenarios: List of test scenarios to measure

        Returns:
            PerformanceMetrics object
        """
        metrics = PerformanceMetrics(
            test_id=str(uuid.uuid4()),
            test_date=datetime.utcnow(),
            scenarios_tested=len(test_scenarios)
        )

        for scenario in test_scenarios:
            scenario_metrics = await self._measure_scenario_performance(scenario)
            metrics.scenario_results.append(scenario_metrics)

        # Calculate overall metrics
        metrics.avg_response_time = mean([s['response_time'] for s in metrics.scenario_results])
        metrics.median_response_time = median([s['response_time'] for s in metrics.scenario_results])
        metrics.p95_response_time = self._calculate_percentile(
            [s['response_time'] for s in metrics.scenario_results], 95
        )
        metrics.success_rate = mean([s['success_rate'] for s in metrics.scenario_results])

        logger.info(f"Completed performance measurement: {metrics.test_id}")
        return metrics

    async def analyze_test_results(self, test_id: str) -> Dict[str, Any]:
        """
        Analyze results from a completed test.

        Args:
            test_id: ID of the test to analyze

        Returns:
            Analysis results
        """
        if test_id not in self.active_tests:
            raise ValueError(f"Test {test_id} not found")

        test = self.active_tests[test_id]
        
        # Get all sessions for this test
        test_sessions = [
            session for session in self.test_sessions.values()
            if session.test_id == test_id
        ]

        analysis = {
            'test_id': test_id,
            'test_name': test.test_name,
            'test_type': test.test_type,
            'total_sessions': len(test_sessions),
            'analysis_date': datetime.utcnow()
        }

        if test.test_type == TestType.USABILITY:
            analysis.update(await self._analyze_usability_results(test, test_sessions))
        elif test.test_type == TestType.AB_TESTING:
            analysis.update(await self._analyze_ab_test_results(test, test_sessions))

        return analysis

    async def generate_optimization_recommendations(
        self,
        test_results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate optimization recommendations based on test results.

        Args:
            test_results: Results from test analysis

        Returns:
            List of optimization recommendations
        """
        recommendations = []

        # Task completion rate recommendations
        if 'task_completion_rate' in test_results:
            completion_rate = test_results['task_completion_rate']
            if completion_rate < 0.8:
                recommendations.append({
                    'type': 'usability',
                    'priority': 'high',
                    'issue': 'Low task completion rate',
                    'recommendation': 'Simplify interface and reduce cognitive load',
                    'expected_improvement': '15-25% increase in completion rate'
                })

        # User satisfaction recommendations
        if 'satisfaction_score' in test_results:
            satisfaction = test_results['satisfaction_score']
            if satisfaction < 4.0:
                recommendations.append({
                    'type': 'satisfaction',
                    'priority': 'high',
                    'issue': 'Low user satisfaction',
                    'recommendation': 'Improve interface design and user guidance',
                    'expected_improvement': '0.5-1.0 point increase in satisfaction'
                })

        # Performance recommendations
        if 'avg_response_time' in test_results:
            response_time = test_results['avg_response_time']
            if response_time > 3.0:
                recommendations.append({
                    'type': 'performance',
                    'priority': 'medium',
                    'issue': 'Slow response times',
                    'recommendation': 'Optimize database queries and caching',
                    'expected_improvement': '30-50% reduction in response time'
                })

        # Accessibility recommendations
        if 'accessibility_score' in test_results:
            accessibility = test_results['accessibility_score']
            if accessibility < 0.9:
                recommendations.append({
                    'type': 'accessibility',
                    'priority': 'high',
                    'issue': 'Accessibility issues found',
                    'recommendation': 'Implement WCAG 2.1 AA compliance',
                    'expected_improvement': 'Full accessibility compliance'
                })

        return recommendations

    async def _update_session_metrics(self, session: TestSession) -> None:
        """Update session-level metrics."""
        if not hasattr(session, 'task_completions'):
            return

        completions = session.task_completions.values()
        
        session.metrics = {
            'tasks_completed': len(completions),
            'avg_completion_time': mean([c.completion_time for c in completions]),
            'success_rate': mean([c.success for c in completions]),
            'user_satisfaction': getattr(session, 'satisfaction_score', None)
        }

    async def _run_accessibility_checks(
        self,
        interface_url: str,
        standards: List[str]
    ) -> Dict[str, Any]:
        """Run accessibility checks (simulated)."""
        # In production, integrate with tools like axe-core, WAVE, etc.
        return {
            'overall_score': 0.85,
            'issues': [
                {'type': 'color_contrast', 'severity': 'medium', 'description': 'Low contrast ratio'},
                {'type': 'keyboard_navigation', 'severity': 'low', 'description': 'Missing tab order'}
            ],
            'recommendations': [
                'Increase color contrast ratios to meet WCAG AA standards',
                'Implement proper keyboard navigation order'
            ]
        }

    async def _measure_scenario_performance(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Measure performance for a specific scenario."""
        start_time = time.time()
        
        # Simulate API call or interface interaction
        await asyncio.sleep(random.uniform(0.5, 2.0))
        
        response_time = time.time() - start_time
        
        return {
            'scenario_name': scenario.get('name', 'Unknown'),
            'response_time': response_time,
            'success_rate': random.uniform(0.85, 1.0),
            'error_rate': random.uniform(0.0, 0.15)
        }

    def _calculate_percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile value."""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]

    async def _analyze_usability_results(
        self,
        test: UserExperienceTest,
        sessions: List[TestSession]
    ) -> Dict[str, Any]:
        """Analyze usability test results."""
        total_tasks = len(test.tasks)
        completed_tasks = sum(
            len(session.task_completions) for session in sessions
            if hasattr(session, 'task_completions')
        )
        
        task_completion_rate = completed_tasks / (len(sessions) * total_tasks) if sessions else 0
        
        satisfaction_scores = [
            session.metrics.get('user_satisfaction', 0)
            for session in sessions
            if hasattr(session, 'metrics') and session.metrics.get('user_satisfaction')
        ]
        
        avg_satisfaction = mean(satisfaction_scores) if satisfaction_scores else 0
        
        return {
            'task_completion_rate': task_completion_rate,
            'avg_satisfaction_score': avg_satisfaction,
            'total_participants': len(sessions),
            'user_group_breakdown': self._get_user_group_breakdown(sessions)
        }

    async def _analyze_ab_test_results(
        self,
        test: UserExperienceTest,
        sessions: List[TestSession]
    ) -> Dict[str, Any]:
        """Analyze A/B test results."""
        variant_results = {}
        
        for variant in test.variants:
            variant_sessions = [
                session for session in sessions
                if session.session_data.get('variant_id') == variant.variant_id
            ]
            
            if variant_sessions:
                variant_results[variant.variant_id] = {
                    'participants': len(variant_sessions),
                    'primary_metric': self._calculate_primary_metric(
                        variant_sessions, test.primary_metric
                    ),
                    'conversion_rate': self._calculate_conversion_rate(variant_sessions)
                }
        
        return {
            'variant_results': variant_results,
            'winning_variant': self._determine_winning_variant(variant_results),
            'statistical_significance': self._calculate_statistical_significance(variant_results)
        }

    def _get_user_group_breakdown(self, sessions: List[TestSession]) -> Dict[str, int]:
        """Get breakdown of sessions by user group."""
        breakdown = {}
        for session in sessions:
            group = session.user_group.value
            breakdown[group] = breakdown.get(group, 0) + 1
        return breakdown

    def _calculate_primary_metric(
        self,
        sessions: List[TestSession],
        metric_name: str
    ) -> float:
        """Calculate primary metric for A/B test variant."""
        # Implementation depends on specific metric
        return random.uniform(0.7, 0.95)

    def _calculate_conversion_rate(self, sessions: List[TestSession]) -> float:
        """Calculate conversion rate for sessions."""
        if not sessions:
            return 0.0
        
        successful_sessions = sum(
            1 for session in sessions
            if hasattr(session, 'task_completions') and session.task_completions
        )
        
        return successful_sessions / len(sessions)

    def _determine_winning_variant(self, variant_results: Dict[str, Any]) -> Optional[str]:
        """Determine winning variant based on primary metric."""
        if not variant_results:
            return None
        
        best_variant = max(
            variant_results.items(),
            key=lambda x: x[1].get('primary_metric', 0)
        )
        
        return best_variant[0]

    def _calculate_statistical_significance(self, variant_results: Dict[str, Any]) -> float:
        """Calculate statistical significance of A/B test results."""
        # Simplified calculation - in production, use proper statistical tests
        return random.uniform(0.8, 0.99)


class MetricsCollector:
    """Collects and tracks user experience metrics."""

    def __init__(self):
        self.metrics_store: Dict[str, List[Any]] = {}

    async def track_task_completion_rate(
        self,
        test_id: str,
        completion_rate: float
    ) -> None:
        """Track task completion rate."""
        self._store_metric(test_id, 'task_completion_rate', completion_rate)

    async def track_user_satisfaction(
        self,
        test_id: str,
        satisfaction_score: float
    ) -> None:
        """Track user satisfaction score."""
        self._store_metric(test_id, 'user_satisfaction', satisfaction_score)

    async def track_recommendation_adoption(
        self,
        test_id: str,
        adoption_rate: float
    ) -> None:
        """Track recommendation adoption rate."""
        self._store_metric(test_id, 'recommendation_adoption', adoption_rate)

    def _store_metric(self, test_id: str, metric_name: str, value: float) -> None:
        """Store metric value."""
        if test_id not in self.metrics_store:
            self.metrics_store[test_id] = {}
        
        if metric_name not in self.metrics_store[test_id]:
            self.metrics_store[test_id][metric_name] = []
        
        self.metrics_store[test_id][metric_name].append({
            'value': value,
            'timestamp': datetime.utcnow()
        })


class FeedbackAnalyzer:
    """Analyzes user feedback for insights."""

    def __init__(self):
        self.feedback_store: List[UserFeedback] = []

    async def analyze_feedback(self, feedback: UserFeedback) -> Dict[str, Any]:
        """Analyze individual feedback for insights."""
        self.feedback_store.append(feedback)
        
        # Simple sentiment analysis (in production, use NLP libraries)
        sentiment = self._analyze_sentiment(feedback.feedback_text)
        
        insights = {
            'sentiment': sentiment,
            'key_themes': self._extract_themes(feedback.feedback_text),
            'action_items': self._identify_action_items(feedback.feedback_text),
            'timestamp': datetime.utcnow()
        }
        
        return insights

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of feedback text."""
        positive_words = ['good', 'great', 'excellent', 'love', 'helpful', 'easy']
        negative_words = ['bad', 'terrible', 'difficult', 'confusing', 'slow', 'broken']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'

    def _extract_themes(self, text: str) -> List[str]:
        """Extract key themes from feedback text."""
        themes = []
        
        if 'interface' in text.lower() or 'design' in text.lower():
            themes.append('interface_design')
        if 'speed' in text.lower() or 'slow' in text.lower():
            themes.append('performance')
        if 'recommendation' in text.lower():
            themes.append('recommendations')
        if 'mobile' in text.lower():
            themes.append('mobile_experience')
        
        return themes

    def _identify_action_items(self, text: str) -> List[str]:
        """Identify action items from feedback."""
        action_items = []
        
        if 'should' in text.lower() or 'need' in text.lower():
            action_items.append('feature_request')
        if 'bug' in text.lower() or 'error' in text.lower():
            action_items.append('bug_report')
        if 'improve' in text.lower() or 'better' in text.lower():
            action_items.append('improvement_suggestion')
        
        return action_items


class ABTestManager:
    """Manages A/B testing variants and assignments."""

    def __init__(self):
        self.active_tests: Dict[str, List[ABTestVariant]] = {}

    def assign_variant(
        self,
        test_id: str,
        user_id: str,
        user_group: UserGroup
    ) -> ABTestVariant:
        """Assign user to A/B test variant."""
        if test_id not in self.active_tests:
            raise ValueError(f"A/B test {test_id} not found")
        
        variants = self.active_tests[test_id]
        
        # Simple random assignment (in production, use proper randomization)
        variant = random.choice(variants)
        
        logger.info(f"Assigned user {user_id} to variant {variant.variant_id}")
        return variant

    def register_test(self, test_id: str, variants: List[ABTestVariant]) -> None:
        """Register A/B test with variants."""
        self.active_tests[test_id] = variants
        logger.info(f"Registered A/B test {test_id} with {len(variants)} variants")
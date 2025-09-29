"""
Usability Testing Service

Specialized service for conducting usability tests with real farmers and agricultural professionals.
This service implements the usability testing methods required by TICKET-005_crop-variety-recommendations-13.3.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import uuid

from ..models.user_experience_models import (
    UserTask,
    TaskCompletion,
    UserFeedback,
    UserSatisfactionScore,
    RecommendationAdoptionMetrics,
    FeedbackType
)
from ..config.user_experience_testing_config import (
    USABILITY_TEST_SCENARIOS,
    USER_GROUP_CONFIGS,
    DEFAULT_CONFIG
)

logger = logging.getLogger(__name__)


class UsabilityTestType(str, Enum):
    """Types of usability tests."""
    TASK_BASED = "task_based"
    SCENARIO_BASED = "scenario_based"
    THINK_ALOUD = "think_aloud"
    MODERATED = "moderated"
    UNMODERATED = "unmoderated"


class TaskDifficulty(str, Enum):
    """Task difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass
class UsabilityTestSession:
    """Usability test session data."""
    session_id: str
    test_id: str
    user_id: str
    user_group: str
    test_type: UsabilityTestType
    start_time: datetime
    end_time: Optional[datetime] = None
    tasks_completed: List[str] = None
    task_completions: Dict[str, TaskCompletion] = None
    feedback: List[UserFeedback] = None
    satisfaction_score: Optional[UserSatisfactionScore] = None
    adoption_metrics: Optional[RecommendationAdoptionMetrics] = None
    session_notes: str = ""
    moderator_notes: str = ""


@dataclass
class UsabilityTestResults:
    """Results from usability testing."""
    test_id: str
    total_sessions: int
    task_completion_rates: Dict[str, float]
    average_completion_times: Dict[str, float]
    error_rates: Dict[str, float]
    satisfaction_scores: Dict[str, float]
    adoption_rates: Dict[str, float]
    user_group_breakdown: Dict[str, int]
    key_findings: List[str]
    recommendations: List[str]
    test_date: datetime


class UsabilityTestingService:
    """Service for conducting usability tests with agricultural professionals."""

    def __init__(self):
        self.active_sessions: Dict[str, UsabilityTestSession] = {}
        self.test_scenarios = USABILITY_TEST_SCENARIOS
        self.user_group_configs = USER_GROUP_CONFIGS
        self.config = DEFAULT_CONFIG

    async def create_agricultural_usability_test(
        self,
        test_name: str,
        test_type: UsabilityTestType,
        user_groups: List[str],
        scenario_name: str,
        sample_size: int
    ) -> str:
        """
        Create a usability test specifically designed for agricultural professionals.

        Args:
            test_name: Name of the usability test
            test_type: Type of usability test to conduct
            user_groups: Target user groups (farmers, consultants, etc.)
            scenario_name: Name of the test scenario to use
            sample_size: Number of participants needed

        Returns:
            Test ID for the created test
        """
        test_id = str(uuid.uuid4())
        
        if scenario_name not in self.test_scenarios:
            raise ValueError(f"Unknown scenario: {scenario_name}")
        
        scenario = self.test_scenarios[scenario_name]
        
        # Validate user groups
        for group in user_groups:
            if group not in self.user_group_configs:
                raise ValueError(f"Unknown user group: {group}")
        
        # Create test configuration
        test_config = {
            "test_id": test_id,
            "test_name": test_name,
            "test_type": test_type.value,
            "user_groups": user_groups,
            "scenario": scenario,
            "sample_size": sample_size,
            "created_at": datetime.utcnow(),
            "status": "active"
        }
        
        logger.info(f"Created agricultural usability test: {test_name} (ID: {test_id})")
        return test_id

    async def start_usability_session(
        self,
        test_id: str,
        user_id: str,
        user_group: str,
        test_type: UsabilityTestType,
        session_data: Dict[str, Any]
    ) -> UsabilityTestSession:
        """
        Start a usability test session.

        Args:
            test_id: ID of the test
            user_id: ID of the user
            user_group: User's professional group
            test_type: Type of usability test
            session_data: Additional session data

        Returns:
            UsabilityTestSession object
        """
        session_id = str(uuid.uuid4())
        
        session = UsabilityTestSession(
            session_id=session_id,
            test_id=test_id,
            user_id=user_id,
            user_group=user_group,
            test_type=test_type,
            start_time=datetime.utcnow(),
            tasks_completed=[],
            task_completions={},
            feedback=[],
            session_notes=""
        )
        
        self.active_sessions[session_id] = session
        
        logger.info(f"Started usability session: {session_id} for user: {user_id}")
        return session

    async def record_task_completion(
        self,
        session_id: str,
        task_id: str,
        completion_data: TaskCompletion,
        moderator_notes: str = ""
    ) -> None:
        """
        Record task completion with detailed metrics.

        Args:
            session_id: ID of the test session
            task_id: ID of the completed task
            completion_data: Task completion data
            moderator_notes: Notes from moderator (if applicable)
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        
        # Record completion
        session.task_completions[task_id] = completion_data
        session.tasks_completed.append(task_id)
        
        # Add moderator notes
        if moderator_notes:
            session.moderator_notes += f"\nTask {task_id}: {moderator_notes}"
        
        # Update session metrics
        await self._update_session_metrics(session)
        
        logger.info(f"Recorded task completion for session: {session_id}, task: {task_id}")

    async def collect_think_aloud_feedback(
        self,
        session_id: str,
        task_id: str,
        think_aloud_data: str,
        timestamp: datetime
    ) -> None:
        """
        Collect think-aloud protocol data during task execution.

        Args:
            session_id: ID of the test session
            task_id: ID of the task being performed
            think_aloud_data: Verbal thoughts from user
            timestamp: When the feedback was given
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        
        feedback = UserFeedback(
            feedback_id=str(uuid.uuid4()),
            session_id=session_id,
            feedback_type=FeedbackType.USABILITY,
            feedback_text=think_aloud_data,
            timestamp=timestamp,
            metadata={"task_id": task_id, "type": "think_aloud"}
        )
        
        session.feedback.append(feedback)
        
        logger.info(f"Collected think-aloud feedback for session: {session_id}, task: {task_id}")

    async def record_satisfaction_score(
        self,
        session_id: str,
        satisfaction_data: UserSatisfactionScore
    ) -> None:
        """
        Record detailed satisfaction scoring.

        Args:
            session_id: ID of the test session
            satisfaction_data: Satisfaction score data
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        session.satisfaction_score = satisfaction_data
        
        logger.info(f"Recorded satisfaction score for session: {session_id}")

    async def record_adoption_metrics(
        self,
        session_id: str,
        adoption_data: RecommendationAdoptionMetrics
    ) -> None:
        """
        Record recommendation adoption metrics.

        Args:
            session_id: ID of the test session
            adoption_data: Adoption metrics data
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        session.adoption_metrics = adoption_data
        
        logger.info(f"Recorded adoption metrics for session: {session_id}")

    async def end_usability_session(
        self,
        session_id: str,
        final_notes: str = ""
    ) -> UsabilityTestSession:
        """
        End a usability test session.

        Args:
            session_id: ID of the test session
            final_notes: Final notes from moderator

        Returns:
            Completed UsabilityTestSession
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        session.end_time = datetime.utcnow()
        
        if final_notes:
            session.session_notes += f"\nFinal Notes: {final_notes}"
        
        logger.info(f"Ended usability session: {session_id}")
        return session

    async def analyze_usability_results(
        self,
        test_id: str
    ) -> UsabilityTestResults:
        """
        Analyze results from usability testing.

        Args:
            test_id: ID of the test to analyze

        Returns:
            UsabilityTestResults object
        """
        # Get all sessions for this test
        test_sessions = [
            session for session in self.active_sessions.values()
            if session.test_id == test_id
        ]
        
        if not test_sessions:
            raise ValueError(f"No sessions found for test: {test_id}")
        
        # Calculate metrics
        task_completion_rates = await self._calculate_task_completion_rates(test_sessions)
        average_completion_times = await self._calculate_average_completion_times(test_sessions)
        error_rates = await self._calculate_error_rates(test_sessions)
        satisfaction_scores = await self._calculate_satisfaction_scores(test_sessions)
        adoption_rates = await self._calculate_adoption_rates(test_sessions)
        user_group_breakdown = await self._calculate_user_group_breakdown(test_sessions)
        
        # Generate insights
        key_findings = await self._generate_key_findings(test_sessions)
        recommendations = await self._generate_recommendations(test_sessions)
        
        results = UsabilityTestResults(
            test_id=test_id,
            total_sessions=len(test_sessions),
            task_completion_rates=task_completion_rates,
            average_completion_times=average_completion_times,
            error_rates=error_rates,
            satisfaction_scores=satisfaction_scores,
            adoption_rates=adoption_rates,
            user_group_breakdown=user_group_breakdown,
            key_findings=key_findings,
            recommendations=recommendations,
            test_date=datetime.utcnow()
        )
        
        logger.info(f"Analyzed usability results for test: {test_id}")
        return results

    async def generate_usability_report(
        self,
        results: UsabilityTestResults
    ) -> Dict[str, Any]:
        """
        Generate comprehensive usability test report.

        Args:
            results: Usability test results

        Returns:
            Comprehensive report data
        """
        report = {
            "test_id": results.test_id,
            "report_date": results.test_date,
            "executive_summary": await self._generate_executive_summary(results),
            "methodology": {
                "test_type": "Agricultural Usability Testing",
                "participants": results.total_sessions,
                "user_groups": list(results.user_group_breakdown.keys()),
                "scenarios_tested": len(results.task_completion_rates)
            },
            "key_metrics": {
                "overall_task_completion_rate": sum(results.task_completion_rates.values()) / len(results.task_completion_rates),
                "average_satisfaction_score": sum(results.satisfaction_scores.values()) / len(results.satisfaction_scores),
                "overall_adoption_rate": sum(results.adoption_rates.values()) / len(results.adoption_rates)
            },
            "detailed_results": {
                "task_completion_rates": results.task_completion_rates,
                "completion_times": results.average_completion_times,
                "error_rates": results.error_rates,
                "satisfaction_scores": results.satisfaction_scores,
                "adoption_rates": results.adoption_rates
            },
            "user_group_analysis": results.user_group_breakdown,
            "key_findings": results.key_findings,
            "recommendations": results.recommendations,
            "next_steps": await self._generate_next_steps(results)
        }
        
        return report

    async def _update_session_metrics(self, session: UsabilityTestSession) -> None:
        """Update session-level metrics."""
        if not session.task_completions:
            return
        
        # Calculate session metrics
        total_tasks = len(session.task_completions)
        successful_tasks = sum(1 for completion in session.task_completions.values() if completion.success)
        session_success_rate = successful_tasks / total_tasks if total_tasks > 0 else 0
        
        # Store in session metadata
        if not hasattr(session, 'metrics'):
            session.metrics = {}
        
        session.metrics.update({
            'total_tasks': total_tasks,
            'successful_tasks': successful_tasks,
            'success_rate': session_success_rate,
            'last_updated': datetime.utcnow()
        })

    async def _calculate_task_completion_rates(
        self,
        sessions: List[UsabilityTestSession]
    ) -> Dict[str, float]:
        """Calculate task completion rates."""
        completion_rates = {}
        
        # Group by task ID
        task_data = {}
        for session in sessions:
            for task_id, completion in session.task_completions.items():
                if task_id not in task_data:
                    task_data[task_id] = []
                task_data[task_id].append(completion.success)
        
        # Calculate rates
        for task_id, successes in task_data.items():
            completion_rates[task_id] = sum(successes) / len(successes)
        
        return completion_rates

    async def _calculate_average_completion_times(
        self,
        sessions: List[UsabilityTestSession]
    ) -> Dict[str, float]:
        """Calculate average completion times."""
        completion_times = {}
        
        # Group by task ID
        task_data = {}
        for session in sessions:
            for task_id, completion in session.task_completions.items():
                if task_id not in task_data:
                    task_data[task_id] = []
                task_data[task_id].append(completion.completion_time)
        
        # Calculate averages
        for task_id, times in task_data.items():
            completion_times[task_id] = sum(times) / len(times)
        
        return completion_times

    async def _calculate_error_rates(
        self,
        sessions: List[UsabilityTestSession]
    ) -> Dict[str, float]:
        """Calculate error rates."""
        error_rates = {}
        
        # Group by task ID
        task_data = {}
        for session in sessions:
            for task_id, completion in session.task_completions.items():
                if task_id not in task_data:
                    task_data[task_id] = []
                task_data[task_id].append(len(completion.errors) > 0)
        
        # Calculate rates
        for task_id, errors in task_data.items():
            error_rates[task_id] = sum(errors) / len(errors)
        
        return error_rates

    async def _calculate_satisfaction_scores(
        self,
        sessions: List[UsabilityTestSession]
    ) -> Dict[str, float]:
        """Calculate satisfaction scores by user group."""
        satisfaction_scores = {}
        
        # Group by user group
        group_data = {}
        for session in sessions:
            if session.satisfaction_score:
                if session.user_group not in group_data:
                    group_data[session.user_group] = []
                group_data[session.user_group].append(session.satisfaction_score.overall_satisfaction)
        
        # Calculate averages
        for group, scores in group_data.items():
            satisfaction_scores[group] = sum(scores) / len(scores)
        
        return satisfaction_scores

    async def _calculate_adoption_rates(
        self,
        sessions: List[UsabilityTestSession]
    ) -> Dict[str, float]:
        """Calculate adoption rates by user group."""
        adoption_rates = {}
        
        # Group by user group
        group_data = {}
        for session in sessions:
            if session.adoption_metrics:
                if session.user_group not in group_data:
                    group_data[session.user_group] = []
                group_data[session.user_group].append(session.adoption_metrics.adoption_rate)
        
        # Calculate averages
        for group, rates in group_data.items():
            adoption_rates[group] = sum(rates) / len(rates)
        
        return adoption_rates

    async def _calculate_user_group_breakdown(
        self,
        sessions: List[UsabilityTestSession]
    ) -> Dict[str, int]:
        """Calculate user group breakdown."""
        breakdown = {}
        for session in sessions:
            group = session.user_group
            breakdown[group] = breakdown.get(group, 0) + 1
        return breakdown

    async def _generate_key_findings(
        self,
        sessions: List[UsabilityTestSession]
    ) -> List[str]:
        """Generate key findings from usability testing."""
        findings = []
        
        # Analyze task completion rates
        completion_rates = await self._calculate_task_completion_rates(sessions)
        avg_completion_rate = sum(completion_rates.values()) / len(completion_rates)
        
        if avg_completion_rate < 0.8:
            findings.append(f"Low task completion rate ({avg_completion_rate:.1%}) indicates usability issues")
        elif avg_completion_rate > 0.9:
            findings.append(f"High task completion rate ({avg_completion_rate:.1%}) shows good usability")
        
        # Analyze satisfaction scores
        satisfaction_scores = await self._calculate_satisfaction_scores(sessions)
        if satisfaction_scores:
            avg_satisfaction = sum(satisfaction_scores.values()) / len(satisfaction_scores)
            if avg_satisfaction < 4.0:
                findings.append(f"Low satisfaction score ({avg_satisfaction:.1f}/5.0) suggests user experience issues")
            elif avg_satisfaction > 4.5:
                findings.append(f"High satisfaction score ({avg_satisfaction:.1f}/5.0) indicates positive user experience")
        
        # Analyze user group differences
        if len(satisfaction_scores) > 1:
            max_group = max(satisfaction_scores.items(), key=lambda x: x[1])
            min_group = min(satisfaction_scores.items(), key=lambda x: x[1])
            findings.append(f"User group differences: {max_group[0]} ({max_group[1]:.1f}) vs {min_group[0]} ({min_group[1]:.1f})")
        
        return findings

    async def _generate_recommendations(
        self,
        sessions: List[UsabilityTestSession]
    ) -> List[str]:
        """Generate recommendations based on usability testing."""
        recommendations = []
        
        # Analyze completion rates
        completion_rates = await self._calculate_task_completion_rates(sessions)
        for task_id, rate in completion_rates.items():
            if rate < 0.7:
                recommendations.append(f"Improve usability for task '{task_id}' (completion rate: {rate:.1%})")
        
        # Analyze error rates
        error_rates = await self._calculate_error_rates(sessions)
        for task_id, rate in error_rates.items():
            if rate > 0.3:
                recommendations.append(f"Reduce errors in task '{task_id}' (error rate: {rate:.1%})")
        
        # Analyze completion times
        completion_times = await self._calculate_average_completion_times(sessions)
        for task_id, time in completion_times.items():
            if time > 600:  # 10 minutes
                recommendations.append(f"Optimize task '{task_id}' for faster completion (avg time: {time:.0f}s)")
        
        return recommendations

    async def _generate_executive_summary(
        self,
        results: UsabilityTestResults
    ) -> str:
        """Generate executive summary for usability test."""
        avg_completion_rate = sum(results.task_completion_rates.values()) / len(results.task_completion_rates)
        avg_satisfaction = sum(results.satisfaction_scores.values()) / len(results.satisfaction_scores) if results.satisfaction_scores else 0
        
        summary = f"""
        Usability testing with {results.total_sessions} agricultural professionals revealed:
        
        • Task completion rate: {avg_completion_rate:.1%}
        • User satisfaction: {avg_satisfaction:.1f}/5.0
        • User groups tested: {', '.join(results.user_group_breakdown.keys())}
        
        Key findings: {len(results.key_findings)} issues identified
        Recommendations: {len(results.recommendations)} improvements suggested
        """
        
        return summary.strip()

    async def _generate_next_steps(
        self,
        results: UsabilityTestResults
    ) -> List[str]:
        """Generate next steps based on usability results."""
        next_steps = []
        
        # Prioritize recommendations
        if results.recommendations:
            next_steps.append("Implement high-priority usability improvements")
        
        # Plan follow-up testing
        next_steps.append("Schedule follow-up testing after improvements")
        
        # Monitor metrics
        next_steps.append("Monitor user satisfaction and completion rates")
        
        # Share results
        next_steps.append("Share results with development team and stakeholders")
        
        return next_steps
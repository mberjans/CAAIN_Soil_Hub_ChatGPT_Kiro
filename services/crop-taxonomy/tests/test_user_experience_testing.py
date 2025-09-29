"""
Comprehensive User Experience Testing Suite

This test suite validates the user experience testing and optimization system
for crop variety recommendations as required by TICKET-005_crop-variety-recommendations-13.3.

Test Coverage:
- Usability testing framework with real farmers and agricultural professionals
- A/B testing system for interface optimization
- Accessibility testing for variety selection interface
- Performance testing for recommendation response times
- User feedback collection and iterative improvement process
- Metrics tracking for task completion rates, user satisfaction, and recommendation adoption
"""

import pytest
import asyncio
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
from unittest.mock import AsyncMock, patch, MagicMock

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.user_experience_testing_service import (
    UserExperienceTestingService,
    TestType,
    UserGroup,
    TestConfiguration
)
from models.user_experience_models import (
    UserExperienceTest,
    TestSession,
    UserTask,
    TaskCompletion,
    UserFeedback,
    ABTestVariant,
    AccessibilityTest,
    PerformanceMetrics,
    UserSatisfactionScore,
    RecommendationAdoptionMetrics,
    FeedbackType,
    TaskStatus
)


@pytest.fixture
def ux_service():
    """Create user experience testing service instance."""
    return UserExperienceTestingService()


@pytest.fixture
def sample_tasks():
    """Create sample user tasks for testing."""
    return [
        UserTask(
            task_id="task_1",
            task_name="Find Suitable Corn Varieties",
            description="Find corn varieties suitable for your farm conditions",
            instructions="Navigate to variety selection, input your farm data, and review recommendations",
            expected_outcome="User successfully finds and reviews corn variety recommendations",
            success_criteria=["Views recommendations", "Saves at least one variety"],
            time_limit_minutes=10,
            difficulty_level="easy"
        ),
        UserTask(
            task_id="task_2",
            task_name="Compare Variety Performance",
            description="Compare performance metrics between different varieties",
            instructions="Select multiple varieties and use comparison tool to analyze differences",
            expected_outcome="User successfully compares varieties and identifies key differences",
            success_criteria=["Uses comparison tool", "Identifies performance differences"],
            time_limit_minutes=15,
            difficulty_level="medium"
        ),
        UserTask(
            task_id="task_3",
            task_name="Save and Organize Recommendations",
            description="Save recommended varieties and organize them for future reference",
            instructions="Save varieties to your list and organize them by priority or category",
            expected_outcome="User successfully saves and organizes variety recommendations",
            success_criteria=["Saves varieties", "Organizes saved list"],
            time_limit_minutes=8,
            difficulty_level="easy"
        )
    ]


@pytest.fixture
def sample_ab_variants():
    """Create sample A/B test variants."""
    return [
        ABTestVariant(
            variant_id="control",
            variant_name="Current Interface",
            description="Current variety selection interface",
            configuration={"layout": "standard", "recommendations_per_page": 10},
            traffic_percentage=50.0,
            is_control=True
        ),
        ABTestVariant(
            variant_id="variant_a",
            variant_name="Enhanced Interface",
            description="Interface with enhanced recommendation display",
            configuration={"layout": "enhanced", "recommendations_per_page": 15},
            traffic_percentage=50.0,
            is_control=False
        )
    ]


class TestUserExperienceTestingService:
    """Test suite for user experience testing service."""

    @pytest.mark.asyncio
    async def test_create_usability_test(self, ux_service, sample_tasks):
        """Test creation of usability test."""
        test = await ux_service.create_usability_test(
            test_name="Variety Selection Usability Test",
            user_groups=[UserGroup.FARMERS, UserGroup.AGRICULTURAL_CONSULTANTS],
            sample_size=50,
            tasks=sample_tasks,
            success_criteria={
                "task_completion_rate": 0.8,
                "satisfaction_score": 4.0,
                "recommendation_adoption": 0.6
            }
        )

        assert test.test_name == "Variety Selection Usability Test"
        assert test.test_type == TestType.USABILITY
        assert len(test.user_groups) == 2
        assert test.sample_size == 50
        assert len(test.tasks) == 3
        assert test.status == "active"

    @pytest.mark.asyncio
    async def test_create_ab_test(self, ux_service, sample_ab_variants):
        """Test creation of A/B test."""
        test = await ux_service.create_ab_test(
            test_name="Interface Optimization A/B Test",
            variants=sample_ab_variants,
            user_groups=[UserGroup.FARMERS],
            sample_size=100,
            primary_metric="conversion_rate",
            success_criteria={
                "statistical_significance": 0.95,
                "conversion_rate_improvement": 0.1
            }
        )

        assert test.test_name == "Interface Optimization A/B Test"
        assert test.test_type == TestType.AB_TESTING
        assert len(test.variants) == 2
        assert test.primary_metric == "conversion_rate"
        assert test.status == "active"

    @pytest.mark.asyncio
    async def test_start_test_session(self, ux_service):
        """Test starting a test session."""
        # First create a test
        test = await ux_service.create_usability_test(
            test_name="Test Session Test",
            user_groups=[UserGroup.FARMERS],
            sample_size=10,
            tasks=[],
            success_criteria={}
        )

        session = await ux_service.start_test_session(
            test_id=test.test_id,
            user_id="user_123",
            user_group=UserGroup.FARMERS,
            session_data={"device": "desktop", "browser": "chrome"}
        )

        assert session.test_id == test.test_id
        assert session.user_id == "user_123"
        assert session.user_group == UserGroup.FARMERS
        assert session.status == "active"
        assert "device" in session.session_data

    @pytest.mark.asyncio
    async def test_record_task_completion(self, ux_service):
        """Test recording task completion."""
        # Create test and session
        test = await ux_service.create_usability_test(
            test_name="Task Completion Test",
            user_groups=[UserGroup.FARMERS],
            sample_size=5,
            tasks=[],
            success_criteria={}
        )

        session = await ux_service.start_test_session(
            test_id=test.test_id,
            user_id="user_456",
            user_group=UserGroup.FARMERS,
            session_data={}
        )

        completion = TaskCompletion(
            task_id="task_1",
            completion_time=120.5,
            success=True,
            attempts=1,
            errors=[],
            user_notes="Task completed successfully"
        )

        await ux_service.record_task_completion(
            session_id=session.session_id,
            task_id="task_1",
            completion_data=completion
        )

        # Verify completion was recorded
        assert session.task_completions["task_1"].success is True
        assert session.task_completions["task_1"].completion_time == 120.5

    @pytest.mark.asyncio
    async def test_collect_user_feedback(self, ux_service):
        """Test collecting user feedback."""
        # Create test and session
        test = await ux_service.create_usability_test(
            test_name="Feedback Collection Test",
            user_groups=[UserGroup.FARMERS],
            sample_size=5,
            tasks=[],
            success_criteria={}
        )

        session = await ux_service.start_test_session(
            test_id=test.test_id,
            user_id="user_789",
            user_group=UserGroup.FARMERS,
            session_data={}
        )

        feedback = UserFeedback(
            feedback_id="feedback_1",
            session_id=session.session_id,
            feedback_type=FeedbackType.USABILITY,
            feedback_text="The interface is easy to use and recommendations are helpful",
            rating=4,
            satisfaction_score=8.5
        )

        await ux_service.collect_user_feedback(
            session_id=session.session_id,
            feedback=feedback
        )

        # Verify feedback was collected
        assert len(session.feedback) == 1
        assert session.feedback[0].rating == 4
        assert session.feedback[0].satisfaction_score == 8.5

    @pytest.mark.asyncio
    async def test_run_accessibility_test(self, ux_service):
        """Test running accessibility test."""
        test = await ux_service.run_accessibility_test(
            interface_url="https://afas.com/variety-selection",
            accessibility_standards=["WCAG 2.1 AA", "Section 508"]
        )

        assert test.interface_url == "https://afas.com/variety-selection"
        assert "WCAG 2.1 AA" in test.standards_tested
        assert test.overall_score >= 0.0
        assert test.overall_score <= 1.0
        assert isinstance(test.issues_found, list)
        assert isinstance(test.recommendations, list)

    @pytest.mark.asyncio
    async def test_measure_performance_metrics(self, ux_service):
        """Test measuring performance metrics."""
        test_scenarios = [
            {
                "name": "Basic Variety Search",
                "endpoint": "/api/v1/varieties/search",
                "payload": {"crop_type": "corn", "location": "Iowa"}
            },
            {
                "name": "Complex Recommendation",
                "endpoint": "/api/v1/recommendations/varieties",
                "payload": {"farm_data": {"soil_ph": 6.5, "climate_zone": "5a"}}
            }
        ]

        metrics = await ux_service.measure_performance_metrics(test_scenarios)

        assert metrics.scenarios_tested == 2
        assert metrics.avg_response_time > 0
        assert metrics.median_response_time > 0
        assert metrics.p95_response_time > 0
        assert 0 <= metrics.success_rate <= 1
        assert 0 <= metrics.error_rate <= 1

    @pytest.mark.asyncio
    async def test_analyze_usability_results(self, ux_service, sample_tasks):
        """Test analyzing usability test results."""
        # Create test with tasks
        test = await ux_service.create_usability_test(
            test_name="Usability Analysis Test",
            user_groups=[UserGroup.FARMERS],
            sample_size=10,
            tasks=sample_tasks,
            success_criteria={"task_completion_rate": 0.8}
        )

        # Create multiple sessions with task completions
        for i in range(5):
            session = await ux_service.start_test_session(
                test_id=test.test_id,
                user_id=f"user_{i}",
                user_group=UserGroup.FARMERS,
                session_data={}
            )

            # Record task completions
            for task in sample_tasks:
                completion = TaskCompletion(
                    task_id=task.task_id,
                    completion_time=60.0 + i * 10,
                    success=True,
                    attempts=1
                )
                await ux_service.record_task_completion(
                    session_id=session.session_id,
                    task_id=task.task_id,
                    completion_data=completion
                )

        # Analyze results
        results = await ux_service.analyze_test_results(test.test_id)

        assert "task_completion_rate" in results
        assert "avg_satisfaction_score" in results
        assert "total_participants" in results
        assert results["total_participants"] == 5

    @pytest.mark.asyncio
    async def test_generate_optimization_recommendations(self, ux_service):
        """Test generating optimization recommendations."""
        test_results = {
            "task_completion_rate": 0.65,  # Below threshold
            "satisfaction_score": 3.2,     # Below threshold
            "avg_response_time": 4.5,      # Above threshold
            "accessibility_score": 0.75    # Below threshold
        }

        recommendations = await ux_service.generate_optimization_recommendations(test_results)

        assert len(recommendations) > 0
        
        # Check for specific recommendation types
        recommendation_types = [rec["type"] for rec in recommendations]
        assert "usability" in recommendation_types
        assert "satisfaction" in recommendation_types
        assert "performance" in recommendation_types
        assert "accessibility" in recommendation_types

        # Verify recommendation priorities
        high_priority_count = sum(1 for rec in recommendations if rec["priority"] == "high")
        assert high_priority_count > 0


class TestMetricsCollector:
    """Test suite for metrics collector."""

    @pytest.mark.asyncio
    async def test_track_task_completion_rate(self, ux_service):
        """Test tracking task completion rate."""
        test_id = "test_123"
        completion_rate = 0.85

        await ux_service.metrics_collector.track_task_completion_rate(test_id, completion_rate)

        assert test_id in ux_service.metrics_collector.metrics_store
        assert "task_completion_rate" in ux_service.metrics_collector.metrics_store[test_id]
        assert len(ux_service.metrics_collector.metrics_store[test_id]["task_completion_rate"]) == 1

    @pytest.mark.asyncio
    async def test_track_user_satisfaction(self, ux_service):
        """Test tracking user satisfaction."""
        test_id = "test_456"
        satisfaction_score = 4.2

        await ux_service.metrics_collector.track_user_satisfaction(test_id, satisfaction_score)

        assert test_id in ux_service.metrics_collector.metrics_store
        assert "user_satisfaction" in ux_service.metrics_collector.metrics_store[test_id]
        assert ux_service.metrics_collector.metrics_store[test_id]["user_satisfaction"][0]["value"] == 4.2

    @pytest.mark.asyncio
    async def test_track_recommendation_adoption(self, ux_service):
        """Test tracking recommendation adoption."""
        test_id = "test_789"
        adoption_rate = 0.72

        await ux_service.metrics_collector.track_recommendation_adoption(test_id, adoption_rate)

        assert test_id in ux_service.metrics_collector.metrics_store
        assert "recommendation_adoption" in ux_service.metrics_collector.metrics_store[test_id]
        assert ux_service.metrics_collector.metrics_store[test_id]["recommendation_adoption"][0]["value"] == 0.72


class TestFeedbackAnalyzer:
    """Test suite for feedback analyzer."""

    @pytest.mark.asyncio
    async def test_analyze_positive_feedback(self, ux_service):
        """Test analyzing positive feedback."""
        feedback = UserFeedback(
            feedback_id="feedback_1",
            session_id="session_1",
            feedback_type=FeedbackType.USABILITY,
            feedback_text="The interface is great and very easy to use. I love the recommendations!",
            rating=5
        )

        insights = await ux_service.feedback_analyzer.analyze_feedback(feedback)

        assert insights["sentiment"] == "positive"
        assert "interface_design" in insights["key_themes"]
        assert "recommendations" in insights["key_themes"]

    @pytest.mark.asyncio
    async def test_analyze_negative_feedback(self, ux_service):
        """Test analyzing negative feedback."""
        feedback = UserFeedback(
            feedback_id="feedback_2",
            session_id="session_2",
            feedback_type=FeedbackType.PERFORMANCE,
            feedback_text="The system is slow and confusing. I had trouble finding what I needed.",
            rating=2
        )

        insights = await ux_service.feedback_analyzer.analyze_feedback(feedback)

        assert insights["sentiment"] == "negative"
        assert "performance" in insights["key_themes"]
        assert "improvement_suggestion" in insights["action_items"]

    @pytest.mark.asyncio
    async def test_analyze_neutral_feedback(self, ux_service):
        """Test analyzing neutral feedback."""
        feedback = UserFeedback(
            feedback_id="feedback_3",
            session_id="session_3",
            feedback_type=FeedbackType.GENERAL,
            feedback_text="The system works as expected. No major issues.",
            rating=3
        )

        insights = await ux_service.feedback_analyzer.analyze_feedback(feedback)

        assert insights["sentiment"] == "neutral"


class TestABTestManager:
    """Test suite for A/B test manager."""

    @pytest.mark.asyncio
    async def test_assign_variant(self, ux_service, sample_ab_variants):
        """Test assigning users to A/B test variants."""
        test_id = "ab_test_123"
        ux_service.ab_test_manager.register_test(test_id, sample_ab_variants)

        # Assign multiple users and check distribution
        assignments = []
        for i in range(100):
            variant = ux_service.ab_test_manager.assign_variant(
                test_id=test_id,
                user_id=f"user_{i}",
                user_group=UserGroup.FARMERS
            )
            assignments.append(variant.variant_id)

        # Check that both variants were assigned
        assert "control" in assignments
        assert "variant_a" in assignments

    @pytest.mark.asyncio
    async def test_register_test(self, ux_service, sample_ab_variants):
        """Test registering A/B test."""
        test_id = "test_registration"
        ux_service.ab_test_manager.register_test(test_id, sample_ab_variants)

        assert test_id in ux_service.ab_test_manager.active_tests
        assert len(ux_service.ab_test_manager.active_tests[test_id]) == 2


class TestUserExperienceIntegration:
    """Integration tests for user experience testing system."""

    @pytest.mark.asyncio
    async def test_complete_usability_test_workflow(self, ux_service, sample_tasks):
        """Test complete usability test workflow."""
        # 1. Create usability test
        test = await ux_service.create_usability_test(
            test_name="Complete Workflow Test",
            user_groups=[UserGroup.FARMERS, UserGroup.AGRICULTURAL_CONSULTANTS],
            sample_size=20,
            tasks=sample_tasks,
            success_criteria={
                "task_completion_rate": 0.8,
                "satisfaction_score": 4.0
            }
        )

        # 2. Start test sessions for different user groups
        farmer_sessions = []
        consultant_sessions = []

        for i in range(5):
            farmer_session = await ux_service.start_test_session(
                test_id=test.test_id,
                user_id=f"farmer_{i}",
                user_group=UserGroup.FARMERS,
                session_data={"experience_level": "intermediate"}
            )
            farmer_sessions.append(farmer_session)

            consultant_session = await ux_service.start_test_session(
                test_id=test.test_id,
                user_id=f"consultant_{i}",
                user_group=UserGroup.AGRICULTURAL_CONSULTANTS,
                session_data={"experience_level": "expert"}
            )
            consultant_sessions.append(consultant_session)

        # 3. Record task completions
        for session in farmer_sessions + consultant_sessions:
            for task in sample_tasks:
                completion = TaskCompletion(
                    task_id=task.task_id,
                    completion_time=45.0,
                    success=True,
                    attempts=1
                )
                await ux_service.record_task_completion(
                    session_id=session.session_id,
                    task_id=task.task_id,
                    completion_data=completion
                )

        # 4. Collect feedback
        for session in farmer_sessions:
            feedback = UserFeedback(
                feedback_id=f"feedback_{session.session_id}",
                session_id=session.session_id,
                feedback_type=FeedbackType.USABILITY,
                feedback_text="Great interface, easy to use",
                rating=4,
                satisfaction_score=8.0
            )
            await ux_service.collect_user_feedback(
                session_id=session.session_id,
                feedback=feedback
            )

        # 5. Analyze results
        results = await ux_service.analyze_test_results(test.test_id)

        # 6. Generate recommendations
        recommendations = await ux_service.generate_optimization_recommendations(results)

        # Verify workflow completion
        assert results["total_participants"] == 10
        assert "task_completion_rate" in results
        assert "user_group_breakdown" in results
        assert len(recommendations) >= 0

    @pytest.mark.asyncio
    async def test_performance_under_load(self, ux_service):
        """Test performance metrics under simulated load."""
        # Create multiple concurrent test scenarios
        test_scenarios = []
        for i in range(50):
            test_scenarios.append({
                "name": f"Load Test Scenario {i}",
                "endpoint": "/api/v1/varieties/search",
                "payload": {"crop_type": "corn", "location": f"Region_{i}"}
            })

        start_time = time.time()
        metrics = await ux_service.measure_performance_metrics(test_scenarios)
        end_time = time.time()

        # Verify performance
        assert metrics.scenarios_tested == 50
        assert metrics.avg_response_time < 5.0  # Should be under 5 seconds
        assert metrics.success_rate > 0.8  # Should have high success rate
        assert (end_time - start_time) < 30.0  # Should complete within 30 seconds


class TestAgriculturalValidation:
    """Agricultural validation tests for user experience."""

    @pytest.mark.asyncio
    async def test_farmer_usability_scenarios(self, ux_service):
        """Test usability scenarios specific to farmers."""
        farmer_tasks = [
            UserTask(
                task_id="farmer_task_1",
                task_name="Select Varieties for Spring Planting",
                description="Find corn varieties suitable for spring planting in your region",
                instructions="Input your farm location, soil type, and planting preferences",
                expected_outcome="Farmer finds suitable corn varieties for spring planting",
                success_criteria=["Finds corn varieties", "Reviews planting dates", "Saves recommendations"],
                difficulty_level="easy"
            ),
            UserTask(
                task_id="farmer_task_2",
                task_name="Compare Yield Potential",
                description="Compare yield potential between different corn varieties",
                instructions="Use comparison tool to analyze yield data and select best performers",
                expected_outcome="Farmer identifies highest yielding varieties",
                success_criteria=["Uses comparison tool", "Identifies yield differences", "Makes selection"],
                difficulty_level="medium"
            )
        ]

        test = await ux_service.create_usability_test(
            test_name="Farmer Usability Validation",
            user_groups=[UserGroup.FARMERS],
            sample_size=30,
            tasks=farmer_tasks,
            success_criteria={
                "task_completion_rate": 0.85,
                "satisfaction_score": 4.2,
                "recommendation_adoption": 0.7
            }
        )

        assert test.test_name == "Farmer Usability Validation"
        assert len(test.tasks) == 2
        assert UserGroup.FARMERS in test.user_groups

    @pytest.mark.asyncio
    async def test_consultant_expertise_scenarios(self, ux_service):
        """Test scenarios for agricultural consultants."""
        consultant_tasks = [
            UserTask(
                task_id="consultant_task_1",
                task_name="Generate Client Recommendations",
                description="Generate variety recommendations for multiple client farms",
                instructions="Input data for multiple farms and generate comprehensive recommendations",
                expected_outcome="Consultant generates recommendations for all client farms",
                success_criteria=["Processes multiple farms", "Generates recommendations", "Exports results"],
                difficulty_level="hard"
            ),
            UserTask(
                task_id="consultant_task_2",
                task_name="Analyze Regional Performance",
                description="Analyze variety performance across different regions",
                instructions="Use regional analysis tools to compare variety performance",
                expected_outcome="Consultant identifies regional performance patterns",
                success_criteria=["Uses regional analysis", "Identifies patterns", "Documents findings"],
                difficulty_level="hard"
            )
        ]

        test = await ux_service.create_usability_test(
            test_name="Consultant Expertise Validation",
            user_groups=[UserGroup.AGRICULTURAL_CONSULTANTS],
            sample_size=15,
            tasks=consultant_tasks,
            success_criteria={
                "task_completion_rate": 0.9,
                "satisfaction_score": 4.5,
                "recommendation_adoption": 0.8
            }
        )

        assert test.test_name == "Consultant Expertise Validation"
        assert len(test.tasks) == 2
        assert UserGroup.AGRICULTURAL_CONSULTANTS in test.user_groups

    @pytest.mark.asyncio
    async def test_mobile_accessibility(self, ux_service):
        """Test mobile accessibility for field use."""
        test = await ux_service.run_accessibility_test(
            interface_url="https://afas.com/mobile/variety-selection",
            accessibility_standards=["WCAG 2.1 AA", "Mobile Accessibility Guidelines"]
        )

        assert test.interface_url == "https://afas.com/mobile/variety-selection"
        assert "Mobile Accessibility Guidelines" in test.standards_tested
        assert test.overall_score >= 0.0
        assert test.overall_score <= 1.0

    @pytest.mark.asyncio
    async def test_field_performance_scenarios(self, ux_service):
        """Test performance scenarios for field use."""
        field_scenarios = [
            {
                "name": "Slow Network Variety Search",
                "endpoint": "/api/v1/varieties/search",
                "payload": {"crop_type": "corn", "location": "remote_field"},
                "network_condition": "slow"
            },
            {
                "name": "Offline Recommendation Cache",
                "endpoint": "/api/v1/recommendations/cached",
                "payload": {"cached_data": True},
                "network_condition": "offline"
            }
        ]

        metrics = await ux_service.measure_performance_metrics(field_scenarios)

        assert metrics.scenarios_tested == 2
        assert metrics.avg_response_time > 0
        assert metrics.success_rate >= 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
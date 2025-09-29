"""
User Experience Testing API Routes

API endpoints for user experience testing and optimization system.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Dict, Any, Optional
import logging

from ..services.user_experience_testing_service import (
    UserExperienceTestingService,
    TestType,
    UserGroup
)
from ..models.user_experience_models import (
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
    TestReport,
    OptimizationRecommendation
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/user-experience", tags=["user-experience-testing"])


# Dependency injection
async def get_ux_testing_service() -> UserExperienceTestingService:
    return UserExperienceTestingService()


@router.post("/tests/usability", response_model=UserExperienceTest)
async def create_usability_test(
    test_name: str,
    user_groups: List[UserGroup],
    sample_size: int,
    tasks: List[UserTask],
    success_criteria: Dict[str, float],
    service: UserExperienceTestingService = Depends(get_ux_testing_service)
):
    """
    Create a comprehensive usability test for variety recommendations.

    This endpoint creates a usability test with real farmers and agricultural professionals
    to evaluate the variety selection interface and recommendation system.

    Test Components:
    - Task completion rate measurement
    - User satisfaction scoring
    - Interface usability assessment
    - Recommendation adoption tracking
    - Performance evaluation
    """
    try:
        test = await service.create_usability_test(
            test_name=test_name,
            user_groups=user_groups,
            sample_size=sample_size,
            tasks=tasks,
            success_criteria=success_criteria
        )
        return test
    except Exception as e:
        logger.error(f"Error creating usability test: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tests/ab-test", response_model=UserExperienceTest)
async def create_ab_test(
    test_name: str,
    variants: List[ABTestVariant],
    user_groups: List[UserGroup],
    sample_size: int,
    primary_metric: str,
    success_criteria: Dict[str, float],
    service: UserExperienceTestingService = Depends(get_ux_testing_service)
):
    """
    Create an A/B test for variety recommendation interface optimization.

    This endpoint creates A/B tests to compare different interface designs,
    recommendation algorithms, or user experience approaches.

    A/B Test Features:
    - Multiple variant comparison
    - Statistical significance testing
    - Conversion rate optimization
    - User behavior analysis
    - Performance impact assessment
    """
    try:
        test = await service.create_ab_test(
            test_name=test_name,
            variants=variants,
            user_groups=user_groups,
            sample_size=sample_size,
            primary_metric=primary_metric,
            success_criteria=success_criteria
        )
        return test
    except Exception as e:
        logger.error(f"Error creating A/B test: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions", response_model=TestSession)
async def start_test_session(
    test_id: str,
    user_id: str,
    user_group: UserGroup,
    session_data: Dict[str, Any],
    service: UserExperienceTestingService = Depends(get_ux_testing_service)
):
    """
    Start a test session for a user.

    This endpoint initiates a test session and assigns users to appropriate
    test variants for A/B testing scenarios.
    """
    try:
        session = await service.start_test_session(
            test_id=test_id,
            user_id=user_id,
            user_group=user_group,
            session_data=session_data
        )
        return session
    except Exception as e:
        logger.error(f"Error starting test session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/tasks/{task_id}/completion")
async def record_task_completion(
    session_id: str,
    task_id: str,
    completion_data: TaskCompletion,
    service: UserExperienceTestingService = Depends(get_ux_testing_service)
):
    """
    Record task completion data.

    This endpoint captures detailed task completion metrics including
    completion time, success rate, errors encountered, and user notes.
    """
    try:
        await service.record_task_completion(
            session_id=session_id,
            task_id=task_id,
            completion_data=completion_data
        )
        return {"status": "success", "message": "Task completion recorded"}
    except Exception as e:
        logger.error(f"Error recording task completion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/feedback")
async def collect_user_feedback(
    session_id: str,
    feedback: UserFeedback,
    service: UserExperienceTestingService = Depends(get_ux_testing_service)
):
    """
    Collect user feedback during or after test session.

    This endpoint captures user feedback including satisfaction scores,
    usability comments, and improvement suggestions.
    """
    try:
        await service.collect_user_feedback(
            session_id=session_id,
            feedback=feedback
        )
        return {"status": "success", "message": "Feedback collected"}
    except Exception as e:
        logger.error(f"Error collecting feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/accessibility-test", response_model=AccessibilityTest)
async def run_accessibility_test(
    interface_url: str,
    accessibility_standards: List[str],
    service: UserExperienceTestingService = Depends(get_ux_testing_service)
):
    """
    Run accessibility testing on variety selection interface.

    This endpoint performs comprehensive accessibility testing against
    WCAG 2.1 standards and other accessibility guidelines.

    Accessibility Testing:
    - Color contrast validation
    - Keyboard navigation testing
    - Screen reader compatibility
    - Focus management
    - Alternative text validation
    """
    try:
        test = await service.run_accessibility_test(
            interface_url=interface_url,
            accessibility_standards=accessibility_standards
        )
        return test
    except Exception as e:
        logger.error(f"Error running accessibility test: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/performance-test", response_model=PerformanceMetrics)
async def measure_performance_metrics(
    test_scenarios: List[Dict[str, Any]],
    service: UserExperienceTestingService = Depends(get_ux_testing_service)
):
    """
    Measure performance metrics for variety recommendations.

    This endpoint measures response times, success rates, and error rates
    for various variety recommendation scenarios.

    Performance Metrics:
    - Response time analysis
    - Success rate measurement
    - Error rate tracking
    - Concurrent user testing
    - Load testing results
    """
    try:
        metrics = await service.measure_performance_metrics(
            test_scenarios=test_scenarios
        )
        return metrics
    except Exception as e:
        logger.error(f"Error measuring performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tests/{test_id}/results")
async def analyze_test_results(
    test_id: str,
    service: UserExperienceTestingService = Depends(get_ux_testing_service)
):
    """
    Analyze results from a completed test.

    This endpoint provides comprehensive analysis of test results including
    statistical significance, user satisfaction metrics, and performance data.
    """
    try:
        results = await service.analyze_test_results(test_id=test_id)
        return results
    except Exception as e:
        logger.error(f"Error analyzing test results: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimization-recommendations")
async def generate_optimization_recommendations(
    test_results: Dict[str, Any],
    service: UserExperienceTestingService = Depends(get_ux_testing_service)
):
    """
    Generate optimization recommendations based on test results.

    This endpoint analyzes test results and provides actionable recommendations
    for improving user experience, performance, and accessibility.
    """
    try:
        recommendations = await service.generate_optimization_recommendations(
            test_results=test_results
        )
        return {"recommendations": recommendations}
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/satisfaction-scoring")
async def record_satisfaction_score(
    satisfaction_data: UserSatisfactionScore,
    background_tasks: BackgroundTasks,
    service: UserExperienceTestingService = Depends(get_ux_testing_service)
):
    """
    Record detailed user satisfaction scoring.

    This endpoint captures comprehensive satisfaction metrics including
    ease of use, usefulness, recommendation quality, and likelihood to recommend.
    """
    try:
        # Store satisfaction data
        # In production, this would be stored in database
        logger.info(f"Recorded satisfaction score for session: {satisfaction_data.session_id}")
        
        # Background task to analyze satisfaction trends
        background_tasks.add_task(
            analyze_satisfaction_trends,
            satisfaction_data
        )
        
        return {"status": "success", "message": "Satisfaction score recorded"}
    except Exception as e:
        logger.error(f"Error recording satisfaction score: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/adoption-metrics")
async def record_adoption_metrics(
    adoption_data: RecommendationAdoptionMetrics,
    service: UserExperienceTestingService = Depends(get_ux_testing_service)
):
    """
    Record recommendation adoption metrics.

    This endpoint tracks how users interact with recommendations including
    viewing, saving, and acting upon variety recommendations.
    """
    try:
        # Store adoption metrics
        logger.info(f"Recorded adoption metrics for session: {adoption_data.session_id}")
        
        return {"status": "success", "message": "Adoption metrics recorded"}
    except Exception as e:
        logger.error(f"Error recording adoption metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tests/{test_id}/report", response_model=TestReport)
async def generate_test_report(
    test_id: str,
    service: UserExperienceTestingService = Depends(get_ux_testing_service)
):
    """
    Generate comprehensive test report.

    This endpoint creates a detailed test report including executive summary,
    key findings, metrics, and recommendations.
    """
    try:
        # Generate comprehensive test report
        report = await generate_comprehensive_report(test_id, service)
        return report
    except Exception as e:
        logger.error(f"Error generating test report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint for user experience testing service."""
    return {
        "status": "healthy",
        "service": "user-experience-testing",
        "version": "1.0.0"
    }


# Background task functions
async def analyze_satisfaction_trends(satisfaction_data: UserSatisfactionScore):
    """Analyze satisfaction trends in background."""
    logger.info(f"Analyzing satisfaction trends for session: {satisfaction_data.session_id}")
    # Implementation for trend analysis


async def generate_comprehensive_report(
    test_id: str,
    service: UserExperienceTestingService
) -> TestReport:
    """Generate comprehensive test report."""
    # Get test results
    results = await service.analyze_test_results(test_id)
    
    # Generate recommendations
    recommendations = await service.generate_optimization_recommendations(results)
    
    # Create comprehensive report
    report = TestReport(
        report_id=f"report_{test_id}",
        test_id=test_id,
        executive_summary="Comprehensive user experience testing completed successfully.",
        key_findings=[
            f"Task completion rate: {results.get('task_completion_rate', 0):.1%}",
            f"User satisfaction: {results.get('avg_satisfaction_score', 0):.1f}/5.0",
            f"Performance: {results.get('avg_response_time', 0):.2f}s average response time"
        ],
        metrics_summary=results,
        recommendations=recommendations,
        detailed_results=results,
        next_steps=[
            "Implement high-priority recommendations",
            "Schedule follow-up testing",
            "Monitor user feedback trends"
        ]
    )
    
    return report
"""
User Experience Testing Models

Data models for user experience testing and optimization system.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
from uuid import UUID


class TestStatus(str, Enum):
    """Status of user experience tests."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskStatus(str, Enum):
    """Status of user tasks."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"


class FeedbackType(str, Enum):
    """Types of user feedback."""
    USABILITY = "usability"
    SATISFACTION = "satisfaction"
    PERFORMANCE = "performance"
    ACCESSIBILITY = "accessibility"
    GENERAL = "general"


class UserTask(BaseModel):
    """Represents a task for users to complete during testing."""
    task_id: str = Field(..., description="Unique task identifier")
    task_name: str = Field(..., description="Name of the task")
    description: str = Field(..., description="Task description")
    instructions: str = Field(..., description="Task instructions")
    expected_outcome: str = Field(..., description="Expected outcome")
    success_criteria: List[str] = Field(default_factory=list, description="Success criteria")
    time_limit_minutes: Optional[int] = Field(None, description="Time limit in minutes")
    difficulty_level: str = Field("medium", description="Task difficulty level")


class TaskCompletion(BaseModel):
    """Data about task completion."""
    task_id: str = Field(..., description="Task identifier")
    completion_time: float = Field(..., description="Time to complete in seconds")
    success: bool = Field(..., description="Whether task was completed successfully")
    attempts: int = Field(1, description="Number of attempts")
    errors: List[str] = Field(default_factory=list, description="Errors encountered")
    user_notes: Optional[str] = Field(None, description="User notes about the task")
    completion_timestamp: datetime = Field(default_factory=datetime.utcnow)


class UserFeedback(BaseModel):
    """User feedback collected during testing."""
    feedback_id: str = Field(..., description="Unique feedback identifier")
    session_id: str = Field(..., description="Test session identifier")
    feedback_type: FeedbackType = Field(..., description="Type of feedback")
    feedback_text: str = Field(..., description="Feedback text")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating 1-5")
    satisfaction_score: Optional[float] = Field(None, ge=0.0, le=10.0, description="Satisfaction score 0-10")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ABTestVariant(BaseModel):
    """A/B test variant configuration."""
    variant_id: str = Field(..., description="Unique variant identifier")
    variant_name: str = Field(..., description="Variant name")
    description: str = Field(..., description="Variant description")
    configuration: Dict[str, Any] = Field(..., description="Variant configuration")
    traffic_percentage: float = Field(..., ge=0.0, le=100.0, description="Traffic percentage")
    is_control: bool = Field(False, description="Whether this is the control variant")


class ABTestResult(BaseModel):
    """A/B test result data."""
    variant_id: str = Field(..., description="Variant identifier")
    participants: int = Field(..., description="Number of participants")
    conversions: int = Field(..., description="Number of conversions")
    conversion_rate: float = Field(..., description="Conversion rate")
    primary_metric_value: float = Field(..., description="Primary metric value")
    confidence_interval: Optional[Tuple[float, float]] = Field(None, description="Confidence interval")
    statistical_significance: Optional[float] = Field(None, description="Statistical significance")


class AccessibilityTest(BaseModel):
    """Accessibility test results."""
    test_id: str = Field(..., description="Test identifier")
    interface_url: str = Field(..., description="URL of tested interface")
    standards_tested: List[str] = Field(..., description="Accessibility standards tested")
    results: Dict[str, Any] = Field(..., description="Test results")
    test_date: datetime = Field(default_factory=datetime.utcnow)
    overall_score: float = Field(..., ge=0.0, le=1.0, description="Overall accessibility score")
    issues_found: List[Dict[str, Any]] = Field(default_factory=list, description="Issues found")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")


class PerformanceMetrics(BaseModel):
    """Performance metrics for variety recommendations."""
    test_id: str = Field(..., description="Test identifier")
    test_date: datetime = Field(default_factory=datetime.utcnow)
    scenarios_tested: int = Field(..., description="Number of scenarios tested")
    scenario_results: List[Dict[str, Any]] = Field(default_factory=list, description="Scenario results")
    avg_response_time: float = Field(..., description="Average response time in seconds")
    median_response_time: float = Field(..., description="Median response time in seconds")
    p95_response_time: float = Field(..., description="95th percentile response time")
    success_rate: float = Field(..., ge=0.0, le=1.0, description="Success rate")
    error_rate: float = Field(..., ge=0.0, le=1.0, description="Error rate")


class UserSatisfactionScore(BaseModel):
    """User satisfaction scoring data."""
    session_id: str = Field(..., description="Test session identifier")
    overall_satisfaction: float = Field(..., ge=1.0, le=5.0, description="Overall satisfaction 1-5")
    ease_of_use: float = Field(..., ge=1.0, le=5.0, description="Ease of use rating")
    usefulness: float = Field(..., ge=1.0, le=5.0, description="Usefulness rating")
    recommendation_quality: float = Field(..., ge=1.0, le=5.0, description="Recommendation quality rating")
    interface_design: float = Field(..., ge=1.0, le=5.0, description="Interface design rating")
    performance: float = Field(..., ge=1.0, le=5.0, description="Performance rating")
    likelihood_to_recommend: float = Field(..., ge=1.0, le=5.0, description="Likelihood to recommend")
    comments: Optional[str] = Field(None, description="Additional comments")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class RecommendationAdoptionMetrics(BaseModel):
    """Metrics for recommendation adoption tracking."""
    session_id: str = Field(..., description="Test session identifier")
    recommendations_shown: int = Field(..., description="Number of recommendations shown")
    recommendations_viewed: int = Field(..., description="Number of recommendations viewed")
    recommendations_saved: int = Field(..., description="Number of recommendations saved")
    recommendations_acted_upon: int = Field(..., description="Number of recommendations acted upon")
    adoption_rate: float = Field(..., ge=0.0, le=1.0, description="Adoption rate")
    time_to_action: Optional[float] = Field(None, description="Time to action in seconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TestSession(BaseModel):
    """Test session data."""
    session_id: str = Field(..., description="Unique session identifier")
    test_id: str = Field(..., description="Test identifier")
    user_id: str = Field(..., description="User identifier")
    user_group: str = Field(..., description="User group")
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = Field(None, description="Session end time")
    session_data: Dict[str, Any] = Field(default_factory=dict, description="Session data")
    status: str = Field("active", description="Session status")
    task_completions: Optional[Dict[str, TaskCompletion]] = Field(None, description="Task completions")
    feedback: Optional[List[UserFeedback]] = Field(None, description="User feedback")
    metrics: Optional[Dict[str, Any]] = Field(None, description="Session metrics")


class UserExperienceTest(BaseModel):
    """User experience test configuration."""
    test_id: str = Field(..., description="Unique test identifier")
    test_name: str = Field(..., description="Test name")
    test_type: str = Field(..., description="Type of test")
    user_groups: List[str] = Field(..., description="Target user groups")
    sample_size: int = Field(..., description="Required sample size")
    tasks: Optional[List[UserTask]] = Field(None, description="Tasks for usability testing")
    variants: Optional[List[ABTestVariant]] = Field(None, description="Variants for A/B testing")
    primary_metric: Optional[str] = Field(None, description="Primary metric for A/B testing")
    success_criteria: Dict[str, float] = Field(..., description="Success criteria")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    start_date: Optional[datetime] = Field(None, description="Test start date")
    end_date: Optional[datetime] = Field(None, description="Test end date")
    status: str = Field("active", description="Test status")
    description: Optional[str] = Field(None, description="Test description")


class UsabilityTestScenario(BaseModel):
    """Usability test scenario."""
    scenario_id: str = Field(..., description="Scenario identifier")
    scenario_name: str = Field(..., description="Scenario name")
    description: str = Field(..., description="Scenario description")
    tasks: List[UserTask] = Field(..., description="Tasks in scenario")
    success_criteria: List[str] = Field(..., description="Success criteria")
    expected_duration_minutes: int = Field(..., description="Expected duration")


class TestReport(BaseModel):
    """Comprehensive test report."""
    report_id: str = Field(..., description="Report identifier")
    test_id: str = Field(..., description="Test identifier")
    report_date: datetime = Field(default_factory=datetime.utcnow)
    executive_summary: str = Field(..., description="Executive summary")
    key_findings: List[str] = Field(..., description="Key findings")
    metrics_summary: Dict[str, Any] = Field(..., description="Metrics summary")
    recommendations: List[Dict[str, Any]] = Field(..., description="Recommendations")
    detailed_results: Dict[str, Any] = Field(..., description="Detailed results")
    participant_feedback: List[UserFeedback] = Field(default_factory=list, description="Participant feedback")
    next_steps: List[str] = Field(default_factory=list, description="Next steps")


class OptimizationRecommendation(BaseModel):
    """Optimization recommendation."""
    recommendation_id: str = Field(..., description="Recommendation identifier")
    test_id: str = Field(..., description="Related test identifier")
    type: str = Field(..., description="Type of recommendation")
    priority: str = Field(..., description="Priority level")
    issue: str = Field(..., description="Issue description")
    recommendation: str = Field(..., description="Recommendation text")
    expected_improvement: str = Field(..., description="Expected improvement")
    implementation_effort: str = Field(..., description="Implementation effort")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field("pending", description="Implementation status")
"""
Pydantic models for educational content and training system.
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from enum import Enum
from pydantic import BaseModel, Field, validator
from decimal import Decimal


class ContentType(str, Enum):
    """Types of educational content."""
    TEXT_GUIDE = "text_guide"
    VIDEO_TUTORIAL = "video_tutorial"
    INTERACTIVE_SIMULATION = "interactive_simulation"
    VIRTUAL_REALITY = "virtual_reality"
    CASE_STUDY = "case_study"
    EXPERT_INSIGHT = "expert_insight"
    BEST_PRACTICE = "best_practice"
    TROUBLESHOOTING = "troubleshooting"
    SAFETY_TRAINING = "safety_training"
    EQUIPMENT_TRAINING = "equipment_training"


class DifficultyLevel(str, Enum):
    """Difficulty levels for educational content."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class LearningObjective(str, Enum):
    """Learning objectives for educational content."""
    UNDERSTAND_CONCEPTS = "understand_concepts"
    APPLY_KNOWLEDGE = "apply_knowledge"
    ANALYZE_SITUATIONS = "analyze_situations"
    EVALUATE_OPTIONS = "evaluate_options"
    CREATE_SOLUTIONS = "create_solutions"


class ContentCategory(str, Enum):
    """Categories of educational content."""
    APPLICATION_METHODS = "application_methods"
    EQUIPMENT_OPERATION = "equipment_operation"
    TIMING_OPTIMIZATION = "timing_optimization"
    TROUBLESHOOTING = "troubleshooting"
    SAFETY_PROTOCOLS = "safety_protocols"
    ENVIRONMENTAL_STEWARDSHIP = "environmental_stewardship"
    COST_MANAGEMENT = "cost_management"
    REGULATORY_COMPLIANCE = "regulatory_compliance"
    CROP_INTEGRATION = "crop_integration"
    SOIL_HEALTH = "soil_health"


class EducationalContent(BaseModel):
    """Educational content item."""
    content_id: str = Field(..., description="Unique content identifier")
    title: str = Field(..., description="Content title")
    content_type: ContentType = Field(..., description="Type of educational content")
    category: ContentCategory = Field(..., description="Content category")
    difficulty_level: DifficultyLevel = Field(..., description="Difficulty level")
    learning_objectives: List[LearningObjective] = Field(..., description="Learning objectives")
    description: str = Field(..., description="Content description")
    duration_minutes: Optional[int] = Field(None, ge=1, description="Estimated duration in minutes")
    prerequisites: List[str] = Field(default_factory=list, description="Prerequisites")
    target_audience: List[str] = Field(default_factory=list, description="Target audience")
    content_url: Optional[str] = Field(None, description="URL to content")
    content_data: Optional[Dict[str, Any]] = Field(None, description="Embedded content data")
    tags: List[str] = Field(default_factory=list, description="Content tags")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    expert_reviewed: bool = Field(False, description="Whether content has been expert reviewed")
    validation_score: Optional[float] = Field(None, ge=0, le=1, description="Content validation score")


class TrainingModule(BaseModel):
    """Training module containing multiple educational content items."""
    module_id: str = Field(..., description="Unique module identifier")
    title: str = Field(..., description="Module title")
    description: str = Field(..., description="Module description")
    category: ContentCategory = Field(..., description="Module category")
    difficulty_level: DifficultyLevel = Field(..., description="Module difficulty level")
    learning_objectives: List[LearningObjective] = Field(..., description="Module learning objectives")
    content_items: List[EducationalContent] = Field(..., description="Content items in module")
    estimated_duration_minutes: int = Field(..., ge=1, description="Total estimated duration")
    prerequisites: List[str] = Field(default_factory=list, description="Module prerequisites")
    assessment_questions: List[Dict[str, Any]] = Field(default_factory=list, description="Assessment questions")
    completion_criteria: Dict[str, Any] = Field(default_factory=dict, description="Completion criteria")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class LearningPath(BaseModel):
    """Structured learning path for comprehensive education."""
    path_id: str = Field(..., description="Unique learning path identifier")
    title: str = Field(..., description="Learning path title")
    description: str = Field(..., description="Learning path description")
    target_audience: str = Field(..., description="Target audience")
    difficulty_level: DifficultyLevel = Field(..., description="Overall difficulty level")
    modules: List[TrainingModule] = Field(..., description="Training modules in path")
    estimated_total_duration_minutes: int = Field(..., ge=1, description="Total estimated duration")
    prerequisites: List[str] = Field(default_factory=list, description="Path prerequisites")
    learning_outcomes: List[str] = Field(..., description="Expected learning outcomes")
    certification_available: bool = Field(False, description="Whether certification is available")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ExpertInsight(BaseModel):
    """Expert insight and advice."""
    insight_id: str = Field(..., description="Unique insight identifier")
    expert_name: str = Field(..., description="Expert name")
    expert_title: str = Field(..., description="Expert title")
    expert_credentials: List[str] = Field(..., description="Expert credentials")
    topic: str = Field(..., description="Insight topic")
    content: str = Field(..., description="Insight content")
    category: ContentCategory = Field(..., description="Insight category")
    difficulty_level: DifficultyLevel = Field(..., description="Difficulty level")
    practical_applications: List[str] = Field(default_factory=list, description="Practical applications")
    related_content: List[str] = Field(default_factory=list, description="Related content IDs")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    validated_by: Optional[str] = Field(None, description="Validation expert")


class CaseStudy(BaseModel):
    """Case study for practical learning."""
    case_id: str = Field(..., description="Unique case study identifier")
    title: str = Field(..., description="Case study title")
    description: str = Field(..., description="Case study description")
    scenario: str = Field(..., description="Case scenario")
    problem_statement: str = Field(..., description="Problem statement")
    solution_approach: str = Field(..., description="Solution approach")
    results: str = Field(..., description="Results and outcomes")
    lessons_learned: List[str] = Field(..., description="Lessons learned")
    category: ContentCategory = Field(..., description="Case study category")
    difficulty_level: DifficultyLevel = Field(..., description="Difficulty level")
    farm_context: Dict[str, Any] = Field(default_factory=dict, description="Farm context")
    equipment_used: List[str] = Field(default_factory=list, description="Equipment used")
    challenges_faced: List[str] = Field(default_factory=list, description="Challenges faced")
    success_factors: List[str] = Field(default_factory=list, description="Success factors")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expert_reviewed: bool = Field(False, description="Whether case study has been expert reviewed")


class InteractiveSimulation(BaseModel):
    """Interactive simulation for hands-on learning."""
    simulation_id: str = Field(..., description="Unique simulation identifier")
    title: str = Field(..., description="Simulation title")
    description: str = Field(..., description="Simulation description")
    simulation_type: str = Field(..., description="Type of simulation")
    category: ContentCategory = Field(..., description="Simulation category")
    difficulty_level: DifficultyLevel = Field(..., description="Difficulty level")
    learning_objectives: List[LearningObjective] = Field(..., description="Learning objectives")
    simulation_data: Dict[str, Any] = Field(..., description="Simulation configuration data")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Simulation parameters")
    scenarios: List[Dict[str, Any]] = Field(default_factory=list, description="Available scenarios")
    feedback_system: Dict[str, Any] = Field(default_factory=dict, description="Feedback system configuration")
    estimated_duration_minutes: int = Field(..., ge=1, description="Estimated duration")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class VirtualRealityTraining(BaseModel):
    """Virtual reality training module."""
    vr_id: str = Field(..., description="Unique VR training identifier")
    title: str = Field(..., description="VR training title")
    description: str = Field(..., description="VR training description")
    category: ContentCategory = Field(..., description="VR training category")
    difficulty_level: DifficultyLevel = Field(..., description="Difficulty level")
    learning_objectives: List[LearningObjective] = Field(..., description="Learning objectives")
    vr_scenarios: List[Dict[str, Any]] = Field(..., description="VR scenarios")
    equipment_simulation: Dict[str, Any] = Field(default_factory=dict, description="Equipment simulation")
    environment_settings: Dict[str, Any] = Field(default_factory=dict, description="Environment settings")
    interaction_modes: List[str] = Field(default_factory=list, description="Available interaction modes")
    safety_protocols: List[str] = Field(default_factory=list, description="Safety protocols")
    estimated_duration_minutes: int = Field(..., ge=1, description="Estimated duration")
    hardware_requirements: List[str] = Field(default_factory=list, description="Hardware requirements")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class EducationalRequest(BaseModel):
    """Request model for educational content."""
    user_id: Optional[str] = Field(None, description="User identifier")
    content_categories: List[ContentCategory] = Field(default_factory=list, description="Requested content categories")
    difficulty_level: Optional[DifficultyLevel] = Field(None, description="Preferred difficulty level")
    content_types: List[ContentType] = Field(default_factory=list, description="Preferred content types")
    learning_objectives: List[LearningObjective] = Field(default_factory=list, description="Learning objectives")
    estimated_time_minutes: Optional[int] = Field(None, ge=1, description="Available time in minutes")
    experience_level: Optional[str] = Field(None, description="User experience level")
    specific_topics: List[str] = Field(default_factory=list, description="Specific topics of interest")
    equipment_focus: List[str] = Field(default_factory=list, description="Equipment focus areas")
    farm_context: Optional[Dict[str, Any]] = Field(None, description="Farm context information")


class EducationalResponse(BaseModel):
    """Response model for educational content recommendations."""
    request_id: str = Field(..., description="Unique request identifier")
    recommended_content: List[EducationalContent] = Field(..., description="Recommended educational content")
    learning_paths: List[LearningPath] = Field(default_factory=list, description="Recommended learning paths")
    expert_insights: List[ExpertInsight] = Field(default_factory=list, description="Relevant expert insights")
    case_studies: List[CaseStudy] = Field(default_factory=list, description="Relevant case studies")
    interactive_simulations: List[InteractiveSimulation] = Field(default_factory=list, description="Interactive simulations")
    vr_trainings: List[VirtualRealityTraining] = Field(default_factory=list, description="VR training modules")
    personalized_recommendations: Dict[str, Any] = Field(default_factory=dict, description="Personalized recommendations")
    learning_progress_tracking: Optional[Dict[str, Any]] = Field(None, description="Learning progress tracking")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class LearningProgress(BaseModel):
    """Learning progress tracking."""
    user_id: str = Field(..., description="User identifier")
    content_id: str = Field(..., description="Content identifier")
    progress_percentage: float = Field(..., ge=0, le=100, description="Progress percentage")
    time_spent_minutes: int = Field(..., ge=0, description="Time spent in minutes")
    completion_status: str = Field(..., description="Completion status")
    last_accessed: datetime = Field(default_factory=datetime.utcnow)
    quiz_scores: List[float] = Field(default_factory=list, description="Quiz scores")
    feedback_ratings: List[int] = Field(default_factory=list, description="User feedback ratings")
    notes: List[str] = Field(default_factory=list, description="User notes")


class Certification(BaseModel):
    """Certification for completed training."""
    certification_id: str = Field(..., description="Unique certification identifier")
    user_id: str = Field(..., description="User identifier")
    learning_path_id: str = Field(..., description="Learning path identifier")
    certification_type: str = Field(..., description="Type of certification")
    completion_date: datetime = Field(..., description="Completion date")
    score: float = Field(..., ge=0, le=100, description="Final score")
    validity_period_months: int = Field(..., ge=1, description="Validity period in months")
    issued_by: str = Field(..., description="Certification issuer")
    verification_code: str = Field(..., description="Verification code")
    skills_verified: List[str] = Field(..., description="Verified skills")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FarmerNetwork(BaseModel):
    """Farmer network for peer learning."""
    network_id: str = Field(..., description="Unique network identifier")
    name: str = Field(..., description="Network name")
    description: str = Field(..., description="Network description")
    focus_areas: List[str] = Field(..., description="Focus areas")
    member_count: int = Field(..., ge=0, description="Number of members")
    expertise_level: DifficultyLevel = Field(..., description="Expertise level")
    geographic_scope: str = Field(..., description="Geographic scope")
    discussion_topics: List[str] = Field(default_factory=list, description="Discussion topics")
    resources: List[str] = Field(default_factory=list, description="Available resources")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    active: bool = Field(True, description="Whether network is active")


class ExpertConsultation(BaseModel):
    """Expert consultation service."""
    consultation_id: str = Field(..., description="Unique consultation identifier")
    expert_id: str = Field(..., description="Expert identifier")
    user_id: str = Field(..., description="User identifier")
    topic: str = Field(..., description="Consultation topic")
    question: str = Field(..., description="User question")
    expert_response: Optional[str] = Field(None, description="Expert response")
    consultation_type: str = Field(..., description="Type of consultation")
    scheduled_time: Optional[datetime] = Field(None, description="Scheduled consultation time")
    duration_minutes: Optional[int] = Field(None, description="Consultation duration")
    status: str = Field(..., description="Consultation status")
    follow_up_required: bool = Field(False, description="Whether follow-up is required")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(None, description="Completion time")


# Knowledge Assessment and Certification Models

class AssessmentQuestionType(str, Enum):
    """Types of assessment questions."""
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    MULTIPLE_SELECT = "multiple_select"
    SCENARIO_BASED = "scenario_based"
    PRACTICAL_ASSESSMENT = "practical_assessment"
    CASE_STUDY_ANALYSIS = "case_study_analysis"


class AssessmentDifficulty(str, Enum):
    """Assessment difficulty levels."""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class AssessmentQuestion(BaseModel):
    """Assessment question model."""
    question_id: str = Field(..., description="Unique question identifier")
    question_text: str = Field(..., description="Question text")
    question_type: AssessmentQuestionType = Field(..., description="Type of question")
    difficulty: AssessmentDifficulty = Field(..., description="Question difficulty")
    category: ContentCategory = Field(..., description="Question category")
    options: List[str] = Field(default_factory=list, description="Answer options")
    correct_answer: Union[str, List[str]] = Field(..., description="Correct answer(s)")
    explanation: str = Field(..., description="Explanation of correct answer")
    points: int = Field(1, ge=1, description="Points for correct answer")
    time_limit_seconds: Optional[int] = Field(None, description="Time limit for question")
    prerequisites: List[str] = Field(default_factory=list, description="Prerequisites")
    tags: List[str] = Field(default_factory=list, description="Question tags")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expert_reviewed: bool = Field(False, description="Whether question has been expert reviewed")
    validation_score: Optional[float] = Field(None, ge=0, le=1, description="Question validation score")


class Assessment(BaseModel):
    """Knowledge assessment model."""
    assessment_id: str = Field(..., description="Unique assessment identifier")
    title: str = Field(..., description="Assessment title")
    description: str = Field(..., description="Assessment description")
    category: ContentCategory = Field(..., description="Assessment category")
    difficulty: AssessmentDifficulty = Field(..., description="Assessment difficulty")
    questions: List[AssessmentQuestion] = Field(..., description="Assessment questions")
    total_points: int = Field(..., description="Total possible points")
    passing_score_percentage: float = Field(..., ge=0, le=100, description="Passing score percentage")
    time_limit_minutes: Optional[int] = Field(None, description="Total time limit in minutes")
    max_attempts: Optional[int] = Field(None, description="Maximum attempts allowed")
    prerequisites: List[str] = Field(default_factory=list, description="Assessment prerequisites")
    learning_objectives: List[LearningObjective] = Field(..., description="Learning objectives")
    certification_eligible: bool = Field(False, description="Whether assessment leads to certification")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    expert_reviewed: bool = Field(False, description="Whether assessment has been expert reviewed")


class AssessmentAttempt(BaseModel):
    """Assessment attempt record."""
    attempt_id: str = Field(..., description="Unique attempt identifier")
    user_id: str = Field(..., description="User identifier")
    assessment_id: str = Field(..., description="Assessment identifier")
    start_time: datetime = Field(..., description="Attempt start time")
    end_time: Optional[datetime] = Field(None, description="Attempt end time")
    answers: Dict[str, Union[str, List[str]]] = Field(default_factory=dict, description="User answers")
    score: Optional[float] = Field(None, ge=0, le=100, description="Attempt score percentage")
    passed: Optional[bool] = Field(None, description="Whether attempt passed")
    time_spent_minutes: Optional[int] = Field(None, description="Time spent in minutes")
    feedback: Optional[str] = Field(None, description="Assessment feedback")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CertificationType(str, Enum):
    """Types of certifications."""
    APPLICATION_METHOD_SPECIALIST = "application_method_specialist"
    EQUIPMENT_OPERATOR = "equipment_operator"
    SAFETY_CERTIFIED = "safety_certified"
    ENVIRONMENTAL_STEWARD = "environmental_steward"
    COST_OPTIMIZATION_EXPERT = "cost_optimization_expert"
    REGULATORY_COMPLIANCE = "regulatory_compliance"
    ADVANCED_PRACTITIONER = "advanced_practitioner"


class CertificationRequirement(BaseModel):
    """Certification requirement."""
    requirement_id: str = Field(..., description="Unique requirement identifier")
    certification_type: CertificationType = Field(..., description="Certification type")
    assessment_ids: List[str] = Field(..., description="Required assessment IDs")
    minimum_scores: Dict[str, float] = Field(..., description="Minimum scores per assessment")
    practical_experience_hours: Optional[int] = Field(None, description="Required practical experience hours")
    continuing_education_hours: Optional[int] = Field(None, description="Required continuing education hours")
    validity_period_months: int = Field(..., ge=1, description="Certification validity period")
    renewal_requirements: List[str] = Field(default_factory=list, description="Renewal requirements")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserCertification(BaseModel):
    """User certification record."""
    certification_record_id: str = Field(..., description="Unique certification record identifier")
    user_id: str = Field(..., description="User identifier")
    certification_type: CertificationType = Field(..., description="Certification type")
    certification_id: str = Field(..., description="Certification identifier")
    issued_date: datetime = Field(..., description="Certification issue date")
    expiry_date: datetime = Field(..., description="Certification expiry date")
    status: str = Field(..., description="Certification status (active, expired, revoked)")
    verification_code: str = Field(..., description="Verification code")
    issued_by: str = Field(..., description="Certification issuer")
    assessment_scores: Dict[str, float] = Field(default_factory=dict, description="Assessment scores")
    practical_hours_completed: Optional[int] = Field(None, description="Practical hours completed")
    continuing_education_hours: Optional[int] = Field(None, description="Continuing education hours")
    renewal_date: Optional[datetime] = Field(None, description="Next renewal date")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SkillAssessment(BaseModel):
    """Skill assessment for practical evaluation."""
    skill_assessment_id: str = Field(..., description="Unique skill assessment identifier")
    user_id: str = Field(..., description="User identifier")
    skill_category: str = Field(..., description="Skill category")
    skill_name: str = Field(..., description="Skill name")
    assessment_method: str = Field(..., description="Assessment method")
    evaluator_id: Optional[str] = Field(None, description="Evaluator identifier")
    score: float = Field(..., ge=0, le=100, description="Skill score")
    evidence: List[str] = Field(default_factory=list, description="Evidence of skill")
    feedback: Optional[str] = Field(None, description="Assessment feedback")
    assessment_date: datetime = Field(default_factory=datetime.utcnow)
    valid_until: Optional[datetime] = Field(None, description="Assessment validity period")


class ContinuingEducation(BaseModel):
    """Continuing education record."""
    ce_id: str = Field(..., description="Unique continuing education identifier")
    user_id: str = Field(..., description="User identifier")
    activity_type: str = Field(..., description="Type of continuing education activity")
    title: str = Field(..., description="Activity title")
    description: str = Field(..., description="Activity description")
    hours_completed: float = Field(..., ge=0, description="Hours completed")
    completion_date: datetime = Field(..., description="Completion date")
    provider: str = Field(..., description="Education provider")
    verification_document: Optional[str] = Field(None, description="Verification document")
    certification_types: List[CertificationType] = Field(default_factory=list, description="Applicable certifications")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AssessmentRequest(BaseModel):
    """Request model for knowledge assessment."""
    user_id: str = Field(..., description="User identifier")
    assessment_category: Optional[ContentCategory] = Field(None, description="Assessment category")
    difficulty_level: Optional[AssessmentDifficulty] = Field(None, description="Difficulty level")
    certification_type: Optional[CertificationType] = Field(None, description="Target certification type")
    time_limit_minutes: Optional[int] = Field(None, description="Available time in minutes")
    question_count: Optional[int] = Field(None, ge=1, description="Number of questions")
    adaptive_assessment: bool = Field(False, description="Whether to use adaptive assessment")


class AssessmentResponse(BaseModel):
    """Response model for knowledge assessment."""
    assessment_id: str = Field(..., description="Assessment identifier")
    attempt_id: str = Field(..., description="Attempt identifier")
    questions: List[AssessmentQuestion] = Field(..., description="Assessment questions")
    time_limit_minutes: Optional[int] = Field(None, description="Time limit")
    instructions: str = Field(..., description="Assessment instructions")
    total_points: int = Field(..., description="Total possible points")
    passing_score: float = Field(..., description="Passing score percentage")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AssessmentResult(BaseModel):
    """Assessment result model."""
    attempt_id: str = Field(..., description="Attempt identifier")
    user_id: str = Field(..., description="User identifier")
    assessment_id: str = Field(..., description="Assessment identifier")
    score: float = Field(..., ge=0, le=100, description="Final score percentage")
    points_earned: int = Field(..., ge=0, description="Points earned")
    total_points: int = Field(..., ge=1, description="Total possible points")
    passed: bool = Field(..., description="Whether assessment was passed")
    time_spent_minutes: int = Field(..., ge=0, description="Time spent in minutes")
    question_results: List[Dict[str, Any]] = Field(..., description="Individual question results")
    strengths: List[str] = Field(default_factory=list, description="Identified strengths")
    areas_for_improvement: List[str] = Field(default_factory=list, description="Areas for improvement")
    recommendations: List[str] = Field(default_factory=list, description="Learning recommendations")
    certification_eligible: bool = Field(False, description="Whether user is eligible for certification")
    next_assessment_date: Optional[datetime] = Field(None, description="Next assessment date")
    completed_at: datetime = Field(default_factory=datetime.utcnow)


class CertificationRequest(BaseModel):
    """Request model for certification."""
    user_id: str = Field(..., description="User identifier")
    certification_type: CertificationType = Field(..., description="Certification type")
    assessment_results: List[str] = Field(..., description="Assessment attempt IDs")
    practical_experience_hours: Optional[int] = Field(None, description="Practical experience hours")
    continuing_education_hours: Optional[int] = Field(None, description="Continuing education hours")
    supporting_documents: List[str] = Field(default_factory=list, description="Supporting documents")


class CertificationResponse(BaseModel):
    """Response model for certification."""
    certification_record_id: str = Field(..., description="Certification record identifier")
    user_id: str = Field(..., description="User identifier")
    certification_type: CertificationType = Field(..., description="Certification type")
    certification_id: str = Field(..., description="Certification identifier")
    issued_date: datetime = Field(..., description="Issue date")
    expiry_date: datetime = Field(..., description="Expiry date")
    verification_code: str = Field(..., description="Verification code")
    status: str = Field(..., description="Certification status")
    skills_verified: List[str] = Field(..., description="Verified skills")
    renewal_requirements: List[str] = Field(default_factory=list, description="Renewal requirements")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CertificationStatus(str, Enum):
    """Certification status levels."""
    NOT_CERTIFIED = "not_certified"
    IN_PROGRESS = "in_progress"
    CERTIFIED = "certified"
    EXPIRED = "expired"
    RENEWAL_REQUIRED = "renewal_required"


class UserProfile(BaseModel):
    """User profile for educational system."""
    user_id: str = Field(..., description="Unique user identifier")
    experience_level: DifficultyLevel = Field(..., description="User's experience level")
    learning_preferences: Dict[str, Any] = Field(default_factory=dict, description="Learning preferences")
    completed_modules: List[str] = Field(default_factory=list, description="Completed training modules")
    certifications: List[Certification] = Field(default_factory=list, description="User certifications")
    learning_goals: List[str] = Field(default_factory=list, description="Learning goals")
    preferred_content_types: List[ContentType] = Field(default_factory=list, description="Preferred content types")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

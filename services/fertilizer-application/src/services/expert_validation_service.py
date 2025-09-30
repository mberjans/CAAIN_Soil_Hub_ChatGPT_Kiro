"""
Agricultural Expert Validation Service for TICKET-023_fertilizer-application-method-11.2.

This service implements comprehensive agricultural expert validation and field testing
for fertilizer application method recommendations, including:
- Expert panel management and review processes
- Method recommendation validation against agricultural best practices
- Application guidance validation by equipment specialists and agronomists
- Field testing coordination with pilot farms
- Outcome tracking and effectiveness measurement
- Performance metrics tracking (>90% accuracy, >95% expert approval, >85% farmer satisfaction)
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, Tuple, Union
from uuid import uuid4
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta, date
import json
import statistics

from src.models.application_models import (
    ApplicationRequest, ApplicationResponse, ApplicationMethod,
    FieldConditions, CropRequirements, FertilizerSpecification,
    ApplicationMethodType, FertilizerForm, EquipmentType, EquipmentSpecification
)

logger = logging.getLogger(__name__)


class ExpertType(str, Enum):
    """Types of agricultural experts."""
    FERTILIZER_SPECIALIST = "fertilizer_specialist"
    EXTENSION_AGENT = "extension_agent"
    EQUIPMENT_SPECIALIST = "equipment_specialist"
    AGRONOMIST = "agronomist"
    SOIL_SCIENTIST = "soil_scientist"
    CROP_CONSULTANT = "crop_consultant"
    FARM_MANAGER = "farm_manager"


class ValidationStatus(str, Enum):
    """Status of validation processes."""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_REVISION = "requires_revision"
    FIELD_TESTING = "field_testing"
    COMPLETED = "completed"


class FieldTestStatus(str, Enum):
    """Status of field testing."""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    DATA_COLLECTION = "data_collection"
    ANALYSIS = "analysis"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ExpertProfile:
    """Profile of an agricultural expert."""
    expert_id: str
    name: str
    expert_type: ExpertType
    credentials: str
    specialization: List[str]
    experience_years: int
    certifications: List[str]
    contact_info: Dict[str, str]
    availability: Dict[str, Any]
    rating: float
    review_count: int
    created_at: datetime
    updated_at: datetime


@dataclass
class ValidationRequest:
    """Request for expert validation."""
    request_id: str
    application_request: ApplicationRequest
    application_response: ApplicationResponse
    validation_type: str
    priority: str
    assigned_experts: List[str]
    deadline: datetime
    created_at: datetime
    status: ValidationStatus


@dataclass
class ExpertReview:
    """Expert review of a recommendation."""
    review_id: str
    expert_id: str
    validation_request_id: str
    recommendation_score: float  # 0-10 scale
    accuracy_score: float  # 0-10 scale
    feasibility_score: float  # 0-10 scale
    safety_score: float  # 0-10 scale
    cost_effectiveness_score: float  # 0-10 scale
    overall_approval: bool
    comments: str
    suggestions: List[str]
    concerns: List[str]
    alternative_recommendations: List[Dict[str, Any]]
    review_date: datetime
    confidence_level: float  # 0-1 scale


@dataclass
class FieldTestPlan:
    """Plan for field testing a recommendation."""
    test_id: str
    validation_request_id: str
    farm_id: str
    field_id: str
    test_design: Dict[str, Any]
    implementation_plan: Dict[str, Any]
    data_collection_plan: Dict[str, Any]
    success_criteria: Dict[str, Any]
    timeline: Dict[str, datetime]
    budget: float
    status: FieldTestStatus
    created_at: datetime


@dataclass
class FieldTestResult:
    """Results from field testing."""
    result_id: str
    test_id: str
    implementation_success: bool
    yield_impact: float
    cost_savings: float
    farmer_satisfaction: float
    environmental_impact: Dict[str, Any]
    lessons_learned: List[str]
    recommendations: List[str]
    data_collected: Dict[str, Any]
    completion_date: datetime


@dataclass
class ValidationMetrics:
    """Metrics for validation performance."""
    total_validations: int
    expert_approval_rate: float
    farmer_satisfaction_rate: float
    recommendation_accuracy: float
    field_test_success_rate: float
    average_review_time: float
    expert_consensus_rate: float
    validation_period: Tuple[datetime, datetime]


class ExpertValidationService:
    """Service for agricultural expert validation and field testing."""

    def __init__(self):
        """Initialize the expert validation service."""
        self.logger = logging.getLogger(__name__)
        self.expert_database: Dict[str, ExpertProfile] = {}
        self.validation_requests: Dict[str, ValidationRequest] = {}
        self.expert_reviews: Dict[str, ExpertReview] = {}
        self.field_test_plans: Dict[str, FieldTestPlan] = {}
        self.field_test_results: Dict[str, FieldTestResult] = {}
        self.validation_metrics: List[ValidationMetrics] = []
        
        # Initialize with sample expert panel
        self._initialize_expert_panel()

    def _initialize_expert_panel(self):
        """Initialize the expert panel with sample experts."""
        experts = [
            ExpertProfile(
                expert_id="exp_001",
                name="Dr. Sarah Johnson",
                expert_type=ExpertType.FERTILIZER_SPECIALIST,
                credentials="PhD Soil Science, CCA Certified",
                specialization=["nitrogen management", "precision agriculture", "soil health"],
                experience_years=15,
                certifications=["CCA", "CPSS", "CPAg"],
                contact_info={"email": "sarah.johnson@university.edu", "phone": "+1-555-0101"},
                availability={"monday": True, "tuesday": True, "wednesday": False, "thursday": True, "friday": True},
                rating=4.8,
                review_count=127,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            ExpertProfile(
                expert_id="exp_002",
                name="Mike Rodriguez",
                expert_type=ExpertType.EXTENSION_AGENT,
                credentials="MS Agronomy, Extension Specialist",
                specialization=["crop production", "fertilizer application", "equipment"],
                experience_years=12,
                certifications=["CCA", "CPAg"],
                contact_info={"email": "mike.rodriguez@extension.edu", "phone": "+1-555-0102"},
                availability={"monday": True, "tuesday": True, "wednesday": True, "thursday": True, "friday": False},
                rating=4.6,
                review_count=89,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            ExpertProfile(
                expert_id="exp_003",
                name="Jennifer Chen",
                expert_type=ExpertType.EQUIPMENT_SPECIALIST,
                credentials="BS Agricultural Engineering, Equipment Specialist",
                specialization=["application equipment", "precision technology", "calibration"],
                experience_years=8,
                certifications=["CPAg"],
                contact_info={"email": "jennifer.chen@equipment.com", "phone": "+1-555-0103"},
                availability={"monday": False, "tuesday": True, "wednesday": True, "thursday": True, "friday": True},
                rating=4.7,
                review_count=56,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            ExpertProfile(
                expert_id="exp_004",
                name="Dr. Robert Thompson",
                expert_type=ExpertType.AGRONOMIST,
                credentials="PhD Agronomy, Research Scientist",
                specialization=["crop physiology", "nutrient cycling", "sustainable agriculture"],
                experience_years=20,
                certifications=["CCA", "CPSS", "CPAg"],
                contact_info={"email": "robert.thompson@research.org", "phone": "+1-555-0104"},
                availability={"monday": True, "tuesday": False, "wednesday": True, "thursday": True, "friday": True},
                rating=4.9,
                review_count=203,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        
        for expert in experts:
            self.expert_database[expert.expert_id] = expert

    async def submit_for_expert_validation(
        self,
        application_request: ApplicationRequest,
        application_response: ApplicationResponse,
        validation_type: str = "method_recommendation",
        priority: str = "normal"
    ) -> str:
        """
        Submit a recommendation for expert validation.
        
        Args:
            application_request: Original application request
            application_response: Generated application response
            validation_type: Type of validation needed
            priority: Priority level (low, normal, high, urgent)
            
        Returns:
            Validation request ID
        """
        try:
            request_id = str(uuid4())
            
            # Select appropriate experts based on validation type
            assigned_experts = await self._select_experts_for_validation(validation_type)
            
            # Calculate deadline based on priority
            deadline = self._calculate_deadline(priority)
            
            validation_request = ValidationRequest(
                request_id=request_id,
                application_request=application_request,
                application_response=application_response,
                validation_type=validation_type,
                priority=priority,
                assigned_experts=assigned_experts,
                deadline=deadline,
                created_at=datetime.now(),
                status=ValidationStatus.PENDING
            )
            
            self.validation_requests[request_id] = validation_request
            
            # Notify assigned experts
            await self._notify_experts(assigned_experts, validation_request)
            
            self.logger.info(f"Validation request {request_id} submitted for expert review")
            return request_id
            
        except Exception as e:
            self.logger.error(f"Error submitting validation request: {e}")
            raise

    async def _select_experts_for_validation(self, validation_type: str) -> List[str]:
        """Select appropriate experts for validation type."""
        expert_selection = {
            "method_recommendation": [ExpertType.FERTILIZER_SPECIALIST, ExpertType.AGRONOMIST],
            "equipment_compatibility": [ExpertType.EQUIPMENT_SPECIALIST, ExpertType.EXTENSION_AGENT],
            "application_guidance": [ExpertType.EXTENSION_AGENT, ExpertType.FERTILIZER_SPECIALIST],
            "cost_analysis": [ExpertType.AGRONOMIST, ExpertType.EXTENSION_AGENT],
            "safety_protocols": [ExpertType.EQUIPMENT_SPECIALIST, ExpertType.FERTILIZER_SPECIALIST]
        }
        
        required_types = expert_selection.get(validation_type, [ExpertType.AGRONOMIST])
        
        selected_experts = []
        for expert_id, expert in self.expert_database.items():
            if expert.expert_type in required_types and expert.rating >= 4.5:
                selected_experts.append(expert_id)
        
        # Return top 2-3 experts based on rating and availability
        return sorted(selected_experts, key=lambda x: self.expert_database[x].rating, reverse=True)[:3]

    def _calculate_deadline(self, priority: str) -> datetime:
        """Calculate deadline based on priority."""
        priority_days = {
            "urgent": 1,
            "high": 3,
            "normal": 7,
            "low": 14
        }
        
        days = priority_days.get(priority, 7)
        return datetime.now() + timedelta(days=days)

    async def _notify_experts(self, expert_ids: List[str], validation_request: ValidationRequest):
        """Notify experts about new validation request."""
        for expert_id in expert_ids:
            expert = self.expert_database[expert_id]
            self.logger.info(f"Notified expert {expert.name} about validation request {validation_request.request_id}")

    async def submit_expert_review(
        self,
        validation_request_id: str,
        expert_id: str,
        recommendation_score: float,
        accuracy_score: float,
        feasibility_score: float,
        safety_score: float,
        cost_effectiveness_score: float,
        overall_approval: bool,
        comments: str,
        suggestions: List[str] = None,
        concerns: List[str] = None,
        alternative_recommendations: List[Dict[str, Any]] = None,
        confidence_level: float = 0.8
    ) -> str:
        """
        Submit expert review for a validation request.
        
        Args:
            validation_request_id: ID of validation request
            expert_id: ID of reviewing expert
            recommendation_score: Score for recommendation quality (0-10)
            accuracy_score: Score for accuracy (0-10)
            feasibility_score: Score for feasibility (0-10)
            safety_score: Score for safety (0-10)
            cost_effectiveness_score: Score for cost effectiveness (0-10)
            overall_approval: Whether expert approves the recommendation
            comments: General comments
            suggestions: List of improvement suggestions
            concerns: List of concerns
            alternative_recommendations: Alternative recommendations
            confidence_level: Expert's confidence in the review (0-1)
            
        Returns:
            Review ID
        """
        try:
            review_id = str(uuid4())
            
            expert_review = ExpertReview(
                review_id=review_id,
                expert_id=expert_id,
                validation_request_id=validation_request_id,
                recommendation_score=recommendation_score,
                accuracy_score=accuracy_score,
                feasibility_score=feasibility_score,
                safety_score=safety_score,
                cost_effectiveness_score=cost_effectiveness_score,
                overall_approval=overall_approval,
                comments=comments,
                suggestions=suggestions or [],
                concerns=concerns or [],
                alternative_recommendations=alternative_recommendations or [],
                review_date=datetime.now(),
                confidence_level=confidence_level
            )
            
            self.expert_reviews[review_id] = expert_review
            
            # Update validation request status
            if validation_request_id in self.validation_requests:
                validation_request = self.validation_requests[validation_request_id]
                validation_request.status = ValidationStatus.IN_REVIEW
            
            self.logger.info(f"Expert review {review_id} submitted by expert {expert_id}")
            return review_id
            
        except Exception as e:
            self.logger.error(f"Error submitting expert review: {e}")
            raise

    async def get_validation_summary(self, validation_request_id: str) -> Dict[str, Any]:
        """Get summary of validation results for a request."""
        try:
            if validation_request_id not in self.validation_requests:
                raise ValueError(f"Validation request {validation_request_id} not found")
            
            validation_request = self.validation_requests[validation_request_id]
            
            # Get all reviews for this request
            reviews = [
                review for review in self.expert_reviews.values()
                if review.validation_request_id == validation_request_id
            ]
            
            if not reviews:
                return {
                    "validation_request_id": validation_request_id,
                    "status": validation_request.status.value,
                    "reviews_received": 0,
                    "consensus": "pending"
                }
            
            # Calculate consensus metrics
            approval_rate = sum(1 for review in reviews if review.overall_approval) / len(reviews)
            avg_recommendation_score = statistics.mean([review.recommendation_score for review in reviews])
            avg_accuracy_score = statistics.mean([review.accuracy_score for review in reviews])
            avg_feasibility_score = statistics.mean([review.feasibility_score for review in reviews])
            avg_safety_score = statistics.mean([review.safety_score for review in reviews])
            avg_cost_score = statistics.mean([review.cost_effectiveness_score for review in reviews])
            avg_confidence = statistics.mean([review.confidence_level for review in reviews])
            
            # Determine consensus
            consensus = "approved" if approval_rate >= 0.8 else "requires_revision" if approval_rate >= 0.5 else "rejected"
            
            return {
                "validation_request_id": validation_request_id,
                "status": validation_request.status.value,
                "reviews_received": len(reviews),
                "consensus": consensus,
                "approval_rate": approval_rate,
                "average_scores": {
                    "recommendation": avg_recommendation_score,
                    "accuracy": avg_accuracy_score,
                    "feasibility": avg_feasibility_score,
                    "safety": avg_safety_score,
                    "cost_effectiveness": avg_cost_score,
                    "confidence": avg_confidence
                },
                "expert_reviews": [
                    {
                        "expert_id": review.expert_id,
                        "expert_name": self.expert_database[review.expert_id].name,
                        "overall_approval": review.overall_approval,
                        "recommendation_score": review.recommendation_score,
                        "comments": review.comments,
                        "suggestions": review.suggestions,
                        "concerns": review.concerns
                    }
                    for review in reviews
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting validation summary: {e}")
            raise

    async def create_field_test_plan(
        self,
        validation_request_id: str,
        farm_id: str,
        field_id: str,
        test_design: Dict[str, Any],
        implementation_plan: Dict[str, Any],
        data_collection_plan: Dict[str, Any],
        success_criteria: Dict[str, Any],
        timeline: Dict[str, datetime],
        budget: float
    ) -> str:
        """
        Create a field test plan for validated recommendations.
        
        Args:
            validation_request_id: ID of validation request
            farm_id: ID of participating farm
            field_id: ID of test field
            test_design: Design of the field test
            implementation_plan: Plan for implementing the test
            data_collection_plan: Plan for collecting data
            success_criteria: Criteria for success
            timeline: Timeline for the test
            budget: Budget for the test
            
        Returns:
            Test plan ID
        """
        try:
            test_id = str(uuid4())
            
            field_test_plan = FieldTestPlan(
                test_id=test_id,
                validation_request_id=validation_request_id,
                farm_id=farm_id,
                field_id=field_id,
                test_design=test_design,
                implementation_plan=implementation_plan,
                data_collection_plan=data_collection_plan,
                success_criteria=success_criteria,
                timeline=timeline,
                budget=budget,
                status=FieldTestStatus.PLANNED,
                created_at=datetime.now()
            )
            
            self.field_test_plans[test_id] = field_test_plan
            
            # Update validation request status
            if validation_request_id in self.validation_requests:
                validation_request = self.validation_requests[validation_request_id]
                validation_request.status = ValidationStatus.FIELD_TESTING
            
            self.logger.info(f"Field test plan {test_id} created for validation request {validation_request_id}")
            return test_id
            
        except Exception as e:
            self.logger.error(f"Error creating field test plan: {e}")
            raise

    async def submit_field_test_result(
        self,
        test_id: str,
        implementation_success: bool,
        yield_impact: float,
        cost_savings: float,
        farmer_satisfaction: float,
        environmental_impact: Dict[str, Any],
        lessons_learned: List[str],
        recommendations: List[str],
        data_collected: Dict[str, Any]
    ) -> str:
        """
        Submit results from field testing.
        
        Args:
            test_id: ID of field test
            implementation_success: Whether implementation was successful
            yield_impact: Impact on yield (percentage change)
            cost_savings: Cost savings achieved
            farmer_satisfaction: Farmer satisfaction score (0-10)
            environmental_impact: Environmental impact assessment
            lessons_learned: Lessons learned from the test
            recommendations: Recommendations based on results
            data_collected: Data collected during the test
            
        Returns:
            Result ID
        """
        try:
            result_id = str(uuid4())
            
            field_test_result = FieldTestResult(
                result_id=result_id,
                test_id=test_id,
                implementation_success=implementation_success,
                yield_impact=yield_impact,
                cost_savings=cost_savings,
                farmer_satisfaction=farmer_satisfaction,
                environmental_impact=environmental_impact,
                lessons_learned=lessons_learned,
                recommendations=recommendations,
                data_collected=data_collected,
                completion_date=datetime.now()
            )
            
            self.field_test_results[result_id] = field_test_result
            
            # Update field test plan status
            if test_id in self.field_test_plans:
                field_test_plan = self.field_test_plans[test_id]
                field_test_plan.status = FieldTestStatus.COMPLETED
            
            # Update validation request status
            validation_request_id = field_test_plan.validation_request_id
            if validation_request_id in self.validation_requests:
                validation_request = self.validation_requests[validation_request_id]
                validation_request.status = ValidationStatus.COMPLETED
            
            self.logger.info(f"Field test result {result_id} submitted for test {test_id}")
            return result_id
            
        except Exception as e:
            self.logger.error(f"Error submitting field test result: {e}")
            raise

    async def calculate_validation_metrics(self, start_date: datetime, end_date: datetime) -> ValidationMetrics:
        """
        Calculate validation performance metrics for a period.
        
        Args:
            start_date: Start date for metrics calculation
            end_date: End date for metrics calculation
            
        Returns:
            Validation metrics
        """
        try:
            # Filter validation requests by date range
            period_requests = [
                req for req in self.validation_requests.values()
                if start_date <= req.created_at <= end_date
            ]
            
            total_validations = len(period_requests)
            
            if total_validations == 0:
                return ValidationMetrics(
                    total_validations=0,
                    expert_approval_rate=0.0,
                    farmer_satisfaction_rate=0.0,
                    recommendation_accuracy=0.0,
                    field_test_success_rate=0.0,
                    average_review_time=0.0,
                    expert_consensus_rate=0.0,
                    validation_period=(start_date, end_date)
                )
            
            # Calculate expert approval rate
            approved_requests = 0
            total_reviews = 0
            review_times = []
            
            for request in period_requests:
                reviews = [
                    review for review in self.expert_reviews.values()
                    if review.validation_request_id == request.request_id
                ]
                
                if reviews:
                    total_reviews += len(reviews)
                    approval_count = sum(1 for review in reviews if review.overall_approval)
                    if approval_count / len(reviews) >= 0.8:  # 80% expert approval threshold
                        approved_requests += 1
                    
                    # Calculate review time
                    review_times.append((max(review.review_date for review in reviews) - request.created_at).total_seconds())
            
            expert_approval_rate = approved_requests / total_validations if total_validations > 0 else 0.0
            
            # Calculate farmer satisfaction rate
            field_test_results = [
                result for result in self.field_test_results.values()
                if start_date <= result.completion_date <= end_date
            ]
            
            satisfied_farmers = sum(1 for result in field_test_results if result.farmer_satisfaction >= 7.0)  # 7/10 threshold
            farmer_satisfaction_rate = satisfied_farmers / len(field_test_results) if field_test_results else 0.0
            
            # Calculate recommendation accuracy
            accurate_recommendations = sum(1 for result in field_test_results if result.implementation_success)
            recommendation_accuracy = accurate_recommendations / len(field_test_results) if field_test_results else 0.0
            
            # Calculate field test success rate
            successful_tests = sum(1 for result in field_test_results if result.implementation_success)
            field_test_success_rate = successful_tests / len(field_test_results) if field_test_results else 0.0
            
            # Calculate average review time
            average_review_time = statistics.mean(review_times) if review_times else 0.0
            
            # Calculate expert consensus rate
            consensus_requests = 0
            for request in period_requests:
                reviews = [
                    review for review in self.expert_reviews.values()
                    if review.validation_request_id == request.request_id
                ]
                if len(reviews) >= 2:
                    approval_rate = sum(1 for review in reviews if review.overall_approval) / len(reviews)
                    if approval_rate >= 0.8 or approval_rate <= 0.2:  # Strong consensus either way
                        consensus_requests += 1
            
            expert_consensus_rate = consensus_requests / total_validations if total_validations > 0 else 0.0
            
            metrics = ValidationMetrics(
                total_validations=total_validations,
                expert_approval_rate=expert_approval_rate,
                farmer_satisfaction_rate=farmer_satisfaction_rate,
                recommendation_accuracy=recommendation_accuracy,
                field_test_success_rate=field_test_success_rate,
                average_review_time=average_review_time,
                expert_consensus_rate=expert_consensus_rate,
                validation_period=(start_date, end_date)
            )
            
            self.validation_metrics.append(metrics)
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating validation metrics: {e}")
            raise

    async def get_expert_panel(self) -> List[Dict[str, Any]]:
        """Get list of expert panel members."""
        return [
            {
                "expert_id": expert.expert_id,
                "name": expert.name,
                "expert_type": expert.expert_type.value,
                "credentials": expert.credentials,
                "specialization": expert.specialization,
                "experience_years": expert.experience_years,
                "certifications": expert.certifications,
                "rating": expert.rating,
                "review_count": expert.review_count,
                "availability": expert.availability
            }
            for expert in self.expert_database.values()
        ]

    async def add_expert_to_panel(
        self,
        name: str,
        expert_type: ExpertType,
        credentials: str,
        specialization: List[str],
        experience_years: int,
        certifications: List[str],
        contact_info: Dict[str, str],
        availability: Dict[str, Any]
    ) -> str:
        """Add a new expert to the panel."""
        expert_id = str(uuid4())
        
        expert_profile = ExpertProfile(
            expert_id=expert_id,
            name=name,
            expert_type=expert_type,
            credentials=credentials,
            specialization=specialization,
            experience_years=experience_years,
            certifications=certifications,
            contact_info=contact_info,
            availability=availability,
            rating=5.0,  # New experts start with perfect rating
            review_count=0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.expert_database[expert_id] = expert_profile
        self.logger.info(f"Added new expert {name} to panel with ID {expert_id}")
        return expert_id

    async def get_validation_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive validation dashboard data."""
        try:
            # Get recent metrics (last 30 days)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            recent_metrics = await self.calculate_validation_metrics(start_date, end_date)
            
            # Get pending validations
            pending_validations = [
                req for req in self.validation_requests.values()
                if req.status == ValidationStatus.PENDING
            ]
            
            # Get active field tests
            active_field_tests = [
                test for test in self.field_test_plans.values()
                if test.status in [FieldTestStatus.PLANNED, FieldTestStatus.IN_PROGRESS, FieldTestStatus.DATA_COLLECTION]
            ]
            
            # Get expert workload
            expert_workload = {}
            for expert_id, expert in self.expert_database.items():
                active_reviews = len([
                    review for review in self.expert_reviews.values()
                    if review.expert_id == expert_id and 
                    self.validation_requests[review.validation_request_id].status == ValidationStatus.IN_REVIEW
                ])
                expert_workload[expert_id] = {
                    "name": expert.name,
                    "active_reviews": active_reviews,
                    "rating": expert.rating,
                    "availability": expert.availability
                }
            
            return {
                "recent_metrics": {
                    "total_validations": recent_metrics.total_validations,
                    "expert_approval_rate": recent_metrics.expert_approval_rate,
                    "farmer_satisfaction_rate": recent_metrics.farmer_satisfaction_rate,
                    "recommendation_accuracy": recent_metrics.recommendation_accuracy,
                    "field_test_success_rate": recent_metrics.field_test_success_rate,
                    "average_review_time": recent_metrics.average_review_time,
                    "expert_consensus_rate": recent_metrics.expert_consensus_rate
                },
                "pending_validations": len(pending_validations),
                "active_field_tests": len(active_field_tests),
                "expert_panel_size": len(self.expert_database),
                "expert_workload": expert_workload,
                "performance_targets": {
                    "expert_approval_target": 0.95,
                    "farmer_satisfaction_target": 0.85,
                    "recommendation_accuracy_target": 0.90
                },
                "targets_met": {
                    "expert_approval": recent_metrics.expert_approval_rate >= 0.95,
                    "farmer_satisfaction": recent_metrics.farmer_satisfaction_rate >= 0.85,
                    "recommendation_accuracy": recent_metrics.recommendation_accuracy >= 0.90
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting validation dashboard: {e}")
            raise
"""
Agricultural Expert Validation Service for Drought Management

This service implements comprehensive agricultural expert validation and field testing
for drought management recommendations, fulfilling TICKET-014_drought-management-13.2.

Features:
- Expert panel management with drought specialists and extension agents
- Recommendation accuracy assessment and practice effectiveness review
- Field testing framework with real farm pilot testing
- Outcome tracking and farmer satisfaction monitoring
- Metrics tracking for >90% recommendation accuracy, >95% expert approval, >85% farmer satisfaction
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID, uuid4
from enum import Enum
from dataclasses import dataclass
from decimal import Decimal
import json

from ..models.drought_models import (
    DroughtAssessmentRequest, DroughtAssessmentResponse,
    ConservationPractice, WaterSavingsPotential
)
from ..database.drought_db import DroughtManagementDB

logger = logging.getLogger(__name__)


class ValidationStatus(str, Enum):
    """Status of expert validation process."""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_REVISION = "requires_revision"
    EXPERT_REVIEW_REQUIRED = "expert_review_required"


class ExpertType(str, Enum):
    """Types of agricultural experts."""
    DROUGHT_SPECIALIST = "drought_specialist"
    EXTENSION_AGENT = "extension_agent"
    CONSERVATION_PROFESSIONAL = "conservation_professional"
    IRRIGATION_SPECIALIST = "irrigation_specialist"
    SOIL_SCIENTIST = "soil_scientist"
    CROP_SPECIALIST = "crop_specialist"


class ValidationCriteria(str, Enum):
    """Validation criteria for drought management recommendations."""
    AGRICULTURAL_SOUNDNESS = "agricultural_soundness"
    REGIONAL_APPLICABILITY = "regional_applicability"
    ECONOMIC_FEASIBILITY = "economic_feasibility"
    ENVIRONMENTAL_IMPACT = "environmental_impact"
    PRACTICALITY = "practicality"
    SAFETY = "safety"
    EFFECTIVENESS = "effectiveness"


@dataclass
class ExpertProfile:
    """Profile of an agricultural expert."""
    expert_id: UUID
    name: str
    credentials: str
    expertise_areas: List[ExpertType]
    regions: List[str]
    years_experience: int
    certifications: List[str]
    contact_info: Dict[str, str]
    availability_status: str
    review_count: int
    approval_rate: float
    average_review_time_hours: float
    created_at: datetime
    last_active: datetime


@dataclass
class ValidationRequest:
    """Request for expert validation of drought management recommendations."""
    validation_id: UUID
    recommendation_id: UUID
    farm_location: Dict[str, Any]
    field_conditions: Dict[str, Any]
    drought_assessment: DroughtAssessmentResponse
    conservation_recommendations: List[ConservationPractice]
    water_savings_estimates: List[WaterSavingsPotential]
    validation_criteria: List[ValidationCriteria]
    priority_level: str
    requested_expert_types: List[ExpertType]
    created_at: datetime
    deadline: datetime


@dataclass
class ExpertReview:
    """Expert review of drought management recommendations."""
    review_id: UUID
    validation_id: UUID
    expert_id: UUID
    expert_type: ExpertType
    review_status: ValidationStatus
    criteria_scores: Dict[ValidationCriteria, float]
    overall_score: float
    comments: str
    recommendations: List[str]
    concerns: List[str]
    approval_status: bool
    review_time_hours: float
    submitted_at: datetime


@dataclass
class FieldTestResult:
    """Results from field testing of drought management practices."""
    test_id: UUID
    farm_id: UUID
    field_id: UUID
    practice_implemented: str
    implementation_date: datetime
    baseline_conditions: Dict[str, Any]
    monitoring_data: Dict[str, Any]
    outcome_metrics: Dict[str, float]
    farmer_feedback: Dict[str, Any]
    expert_observations: List[str]
    effectiveness_score: float
    farmer_satisfaction_score: float
    test_duration_days: int
    completed_at: datetime


@dataclass
class ValidationMetrics:
    """Metrics for validation system performance."""
    total_validations: int
    expert_approval_rate: float
    recommendation_accuracy: float
    farmer_satisfaction: float
    average_review_time_hours: float
    field_test_success_rate: float
    expert_panel_size: int
    active_field_tests: int
    validation_period_days: int


class ExpertValidationService:
    """Service for agricultural expert validation and field testing."""
    
    def __init__(self):
        self.db = DroughtManagementDB()
        self.expert_panel: Dict[UUID, ExpertProfile] = {}
        self.validation_queue: List[ValidationRequest] = []
        self.field_tests: Dict[UUID, FieldTestResult] = {}
        self.metrics = ValidationMetrics(
            total_validations=0,
            expert_approval_rate=0.0,
            recommendation_accuracy=0.0,
            farmer_satisfaction=0.0,
            average_review_time_hours=0.0,
            field_test_success_rate=0.0,
            expert_panel_size=0,
            active_field_tests=0,
            validation_period_days=0
        )
        
    async def initialize(self):
        """Initialize the expert validation service."""
        try:
            logger.info("Initializing Expert Validation Service...")
            
            # Load expert panel
            await self._load_expert_panel()
            
            # Load active field tests
            await self._load_active_field_tests()
            
            # Calculate current metrics
            await self._calculate_metrics()
            
            logger.info("Expert Validation Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Expert Validation Service: {e}")
            raise
    
    async def _load_expert_panel(self):
        """Load expert panel from database."""
        try:
            experts_data = await self.db.get_expert_panel()
            
            for expert_data in experts_data:
                expert = ExpertProfile(
                    expert_id=expert_data['expert_id'],
                    name=expert_data['name'],
                    credentials=expert_data['credentials'],
                    expertise_areas=[ExpertType(area) for area in expert_data['expertise_areas']],
                    regions=expert_data['regions'],
                    years_experience=expert_data['years_experience'],
                    certifications=expert_data['certifications'],
                    contact_info=expert_data['contact_info'],
                    availability_status=expert_data['availability_status'],
                    review_count=expert_data['review_count'],
                    approval_rate=expert_data['approval_rate'],
                    average_review_time_hours=expert_data['average_review_time_hours'],
                    created_at=expert_data['created_at'],
                    last_active=expert_data['last_active']
                )
                self.expert_panel[expert.expert_id] = expert
            
            self.metrics.expert_panel_size = len(self.expert_panel)
            logger.info(f"Loaded {len(self.expert_panel)} experts to panel")
            
        except Exception as e:
            logger.error(f"Failed to load expert panel: {e}")
            raise
    
    async def _load_active_field_tests(self):
        """Load active field tests from database."""
        try:
            field_tests_data = await self.db.get_active_field_tests()
            
            for test_data in field_tests_data:
                field_test = FieldTestResult(
                    test_id=test_data['test_id'],
                    farm_id=test_data['farm_id'],
                    field_id=test_data['field_id'],
                    practice_implemented=test_data['practice_implemented'],
                    implementation_date=test_data['implementation_date'],
                    baseline_conditions=test_data['baseline_conditions'],
                    monitoring_data=test_data['monitoring_data'],
                    outcome_metrics=test_data['outcome_metrics'],
                    farmer_feedback=test_data['farmer_feedback'],
                    expert_observations=test_data['expert_observations'],
                    effectiveness_score=test_data['effectiveness_score'],
                    farmer_satisfaction_score=test_data['farmer_satisfaction_score'],
                    test_duration_days=test_data['test_duration_days'],
                    completed_at=test_data['completed_at']
                )
                self.field_tests[field_test.test_id] = field_test
            
            self.metrics.active_field_tests = len(self.field_tests)
            logger.info(f"Loaded {len(self.field_tests)} active field tests")
            
        except Exception as e:
            logger.error(f"Failed to load active field tests: {e}")
            raise
    
    async def _calculate_metrics(self):
        """Calculate current validation metrics."""
        try:
            metrics_data = await self.db.get_validation_metrics()
            
            self.metrics.total_validations = metrics_data.get('total_validations', 0)
            self.metrics.expert_approval_rate = metrics_data.get('expert_approval_rate', 0.0)
            self.metrics.recommendation_accuracy = metrics_data.get('recommendation_accuracy', 0.0)
            self.metrics.farmer_satisfaction = metrics_data.get('farmer_satisfaction', 0.0)
            self.metrics.average_review_time_hours = metrics_data.get('average_review_time_hours', 0.0)
            self.metrics.field_test_success_rate = metrics_data.get('field_test_success_rate', 0.0)
            
            logger.info("Validation metrics calculated successfully")
            
        except Exception as e:
            logger.error(f"Failed to calculate metrics: {e}")
            raise
    
    async def submit_for_validation(
        self,
        recommendation_id: UUID,
        farm_location: Dict[str, Any],
        field_conditions: Dict[str, Any],
        drought_assessment: DroughtAssessmentResponse,
        conservation_recommendations: List[ConservationPractice],
        water_savings_estimates: List[WaterSavingsPotential],
        priority_level: str = "normal"
    ) -> ValidationRequest:
        """
        Submit drought management recommendations for expert validation.
        
        Args:
            recommendation_id: Unique identifier for the recommendation
            farm_location: Farm location data
            field_conditions: Field condition data
            drought_assessment: Drought assessment results
            conservation_recommendations: Conservation practice recommendations
            water_savings_estimates: Water savings estimates
            priority_level: Priority level (low, normal, high, critical)
            
        Returns:
            ValidationRequest object
        """
        try:
            validation_id = uuid4()
            
            # Determine validation criteria based on recommendation complexity
            validation_criteria = self._determine_validation_criteria(
                conservation_recommendations, water_savings_estimates
            )
            
            # Determine required expert types
            requested_expert_types = self._determine_required_experts(
                farm_location, field_conditions, conservation_recommendations
            )
            
            # Set deadline based on priority
            deadline_hours = self._get_deadline_hours(priority_level)
            deadline = datetime.utcnow() + timedelta(hours=deadline_hours)
            
            validation_request = ValidationRequest(
                validation_id=validation_id,
                recommendation_id=recommendation_id,
                farm_location=farm_location,
                field_conditions=field_conditions,
                drought_assessment=drought_assessment,
                conservation_recommendations=conservation_recommendations,
                water_savings_estimates=water_savings_estimates,
                validation_criteria=validation_criteria,
                priority_level=priority_level,
                requested_expert_types=requested_expert_types,
                created_at=datetime.utcnow(),
                deadline=deadline
            )
            
            # Save to database
            await self.db.save_validation_request(validation_request)
            
            # Add to validation queue
            self.validation_queue.append(validation_request)
            
            # Assign experts
            await self._assign_experts(validation_request)
            
            logger.info(f"Validation request {validation_id} submitted successfully")
            return validation_request
            
        except Exception as e:
            logger.error(f"Failed to submit validation request: {e}")
            raise
    
    def _determine_validation_criteria(
        self,
        conservation_recommendations: List[ConservationPractice],
        water_savings_estimates: List[WaterSavingsPotential]
    ) -> List[ValidationCriteria]:
        """Determine validation criteria based on recommendation complexity."""
        criteria = [ValidationCriteria.AGRICULTURAL_SOUNDNESS, ValidationCriteria.SAFETY]
        
        # Add regional applicability for location-specific recommendations
        if any(rec.region_specific for rec in conservation_recommendations):
            criteria.append(ValidationCriteria.REGIONAL_APPLICABILITY)
        
        # Add economic feasibility for high-cost recommendations
        if any(rec.estimated_cost > 1000 for rec in conservation_recommendations):
            criteria.append(ValidationCriteria.ECONOMIC_FEASIBILITY)
        
        # Add environmental impact for practices affecting water quality
        if any(rec.environmental_impact_high for rec in conservation_recommendations):
            criteria.append(ValidationCriteria.ENVIRONMENTAL_IMPACT)
        
        # Add practicality for complex implementation
        if any(rec.implementation_complexity == "high" for rec in conservation_recommendations):
            criteria.append(ValidationCriteria.PRACTICALITY)
        
        # Add effectiveness for novel or experimental practices
        if any(rec.effectiveness_uncertainty > 0.3 for rec in conservation_recommendations):
            criteria.append(ValidationCriteria.EFFECTIVENESS)
        
        return criteria
    
    def _determine_required_experts(
        self,
        farm_location: Dict[str, Any],
        field_conditions: Dict[str, Any],
        conservation_recommendations: List[ConservationPractice]
    ) -> List[ExpertType]:
        """Determine required expert types based on recommendations."""
        expert_types = [ExpertType.DROUGHT_SPECIALIST]
        
        # Add extension agent for regional recommendations
        if farm_location.get('state'):
            expert_types.append(ExpertType.EXTENSION_AGENT)
        
        # Add conservation professional for conservation practices
        if any(rec.category == "conservation" for rec in conservation_recommendations):
            expert_types.append(ExpertType.CONSERVATION_PROFESSIONAL)
        
        # Add irrigation specialist for irrigation-related recommendations
        if any(rec.category == "irrigation" for rec in conservation_recommendations):
            expert_types.append(ExpertType.IRRIGATION_SPECIALIST)
        
        # Add soil scientist for soil-related practices
        if any(rec.category == "soil_management" for rec in conservation_recommendations):
            expert_types.append(ExpertType.SOIL_SCIENTIST)
        
        # Add crop specialist for crop-specific recommendations
        if field_conditions.get('crop_type'):
            expert_types.append(ExpertType.CROP_SPECIALIST)
        
        return list(set(expert_types))  # Remove duplicates
    
    def _get_deadline_hours(self, priority_level: str) -> int:
        """Get deadline hours based on priority level."""
        deadline_map = {
            "low": 168,      # 1 week
            "normal": 72,     # 3 days
            "high": 24,       # 1 day
            "critical": 8     # 8 hours
        }
        return deadline_map.get(priority_level, 72)
    
    async def _assign_experts(self, validation_request: ValidationRequest):
        """Assign experts to validation request."""
        try:
            assigned_experts = []
            
            for expert_type in validation_request.requested_expert_types:
                # Find available experts of the required type
                available_experts = [
                    expert for expert in self.expert_panel.values()
                    if expert_type in expert.expertise_areas
                    and expert.availability_status == "available"
                    and validation_request.farm_location.get('state') in expert.regions
                ]
                
                if available_experts:
                    # Select expert with highest approval rate and lowest current workload
                    selected_expert = max(
                        available_experts,
                        key=lambda e: (e.approval_rate, -e.review_count)
                    )
                    assigned_experts.append(selected_expert.expert_id)
                    
                    # Update expert availability
                    selected_expert.availability_status = "assigned"
                    selected_expert.review_count += 1
                else:
                    logger.warning(f"No available {expert_type} expert found for validation {validation_request.validation_id}")
            
            # Save expert assignments
            await self.db.assign_experts_to_validation(
                validation_request.validation_id, assigned_experts
            )
            
            logger.info(f"Assigned {len(assigned_experts)} experts to validation {validation_request.validation_id}")
            
        except Exception as e:
            logger.error(f"Failed to assign experts: {e}")
            raise
    
    async def submit_expert_review(
        self,
        validation_id: UUID,
        expert_id: UUID,
        criteria_scores: Dict[ValidationCriteria, float],
        overall_score: float,
        comments: str,
        recommendations: List[str],
        concerns: List[str],
        approval_status: bool,
        review_time_hours: float
    ) -> ExpertReview:
        """
        Submit expert review for validation request.
        
        Args:
            validation_id: Validation request ID
            expert_id: Expert ID
            criteria_scores: Scores for each validation criteria
            overall_score: Overall validation score
            comments: Expert comments
            recommendations: Expert recommendations
            concerns: Expert concerns
            approval_status: Whether recommendation is approved
            review_time_hours: Time taken for review
            
        Returns:
            ExpertReview object
        """
        try:
            review_id = uuid4()
            
            expert_review = ExpertReview(
                review_id=review_id,
                validation_id=validation_id,
                expert_id=expert_id,
                expert_type=self.expert_panel[expert_id].expertise_areas[0],  # Primary expertise
                review_status=ValidationStatus.APPROVED if approval_status else ValidationStatus.REJECTED,
                criteria_scores=criteria_scores,
                overall_score=overall_score,
                comments=comments,
                recommendations=recommendations,
                concerns=concerns,
                approval_status=approval_status,
                review_time_hours=review_time_hours,
                submitted_at=datetime.utcnow()
            )
            
            # Save review to database
            await self.db.save_expert_review(expert_review)
            
            # Update expert profile
            expert = self.expert_panel[expert_id]
            expert.availability_status = "available"
            expert.last_active = datetime.utcnow()
            
            # Update metrics
            await self._update_validation_metrics()
            
            logger.info(f"Expert review {review_id} submitted successfully")
            return expert_review
            
        except Exception as e:
            logger.error(f"Failed to submit expert review: {e}")
            raise
    
    async def start_field_test(
        self,
        farm_id: UUID,
        field_id: UUID,
        practice_implemented: str,
        baseline_conditions: Dict[str, Any],
        test_duration_days: int = 90
    ) -> FieldTestResult:
        """
        Start field test for drought management practice.
        
        Args:
            farm_id: Farm ID
            field_id: Field ID
            practice_implemented: Practice being tested
            baseline_conditions: Baseline field conditions
            test_duration_days: Test duration in days
            
        Returns:
            FieldTestResult object
        """
        try:
            test_id = uuid4()
            
            field_test = FieldTestResult(
                test_id=test_id,
                farm_id=farm_id,
                field_id=field_id,
                practice_implemented=practice_implemented,
                implementation_date=datetime.utcnow(),
                baseline_conditions=baseline_conditions,
                monitoring_data={},
                outcome_metrics={},
                farmer_feedback={},
                expert_observations=[],
                effectiveness_score=0.0,
                farmer_satisfaction_score=0.0,
                test_duration_days=test_duration_days,
                completed_at=datetime.utcnow() + timedelta(days=test_duration_days)
            )
            
            # Save field test to database
            await self.db.save_field_test(field_test)
            
            # Add to active field tests
            self.field_tests[test_id] = field_test
            self.metrics.active_field_tests = len(self.field_tests)
            
            logger.info(f"Field test {test_id} started successfully")
            return field_test
            
        except Exception as e:
            logger.error(f"Failed to start field test: {e}")
            raise
    
    async def update_field_test_monitoring(
        self,
        test_id: UUID,
        monitoring_data: Dict[str, Any],
        expert_observations: List[str]
    ):
        """Update field test monitoring data."""
        try:
            if test_id in self.field_tests:
                field_test = self.field_tests[test_id]
                field_test.monitoring_data.update(monitoring_data)
                field_test.expert_observations.extend(expert_observations)
                
                # Save updated data
                await self.db.update_field_test_monitoring(test_id, monitoring_data, expert_observations)
                
                logger.info(f"Field test {test_id} monitoring data updated")
            else:
                logger.warning(f"Field test {test_id} not found")
                
        except Exception as e:
            logger.error(f"Failed to update field test monitoring: {e}")
            raise
    
    async def complete_field_test(
        self,
        test_id: UUID,
        outcome_metrics: Dict[str, float],
        farmer_feedback: Dict[str, Any],
        effectiveness_score: float,
        farmer_satisfaction_score: float
    ):
        """Complete field test with final results."""
        try:
            if test_id in self.field_tests:
                field_test = self.field_tests[test_id]
                field_test.outcome_metrics = outcome_metrics
                field_test.farmer_feedback = farmer_feedback
                field_test.effectiveness_score = effectiveness_score
                field_test.farmer_satisfaction_score = farmer_satisfaction_score
                field_test.completed_at = datetime.utcnow()
                
                # Save completed test
                await self.db.complete_field_test(field_test)
                
                # Remove from active tests
                del self.field_tests[test_id]
                self.metrics.active_field_tests = len(self.field_tests)
                
                # Update metrics
                await self._update_validation_metrics()
                
                logger.info(f"Field test {test_id} completed successfully")
            else:
                logger.warning(f"Field test {test_id} not found")
                
        except Exception as e:
            logger.error(f"Failed to complete field test: {e}")
            raise
    
    async def _update_validation_metrics(self):
        """Update validation metrics based on current data."""
        try:
            # Calculate expert approval rate
            reviews_data = await self.db.get_recent_reviews(days=30)
            if reviews_data:
                approved_reviews = sum(1 for review in reviews_data if review['approval_status'])
                self.metrics.expert_approval_rate = approved_reviews / len(reviews_data)
            
            # Calculate farmer satisfaction
            completed_tests = await self.db.get_completed_field_tests(days=30)
            if completed_tests:
                satisfaction_scores = [test['farmer_satisfaction_score'] for test in completed_tests]
                self.metrics.farmer_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores)
            
            # Calculate average review time
            if reviews_data:
                review_times = [review['review_time_hours'] for review in reviews_data]
                self.metrics.average_review_time_hours = sum(review_times) / len(review_times)
            
            # Calculate field test success rate
            if completed_tests:
                successful_tests = sum(1 for test in completed_tests if test['effectiveness_score'] > 0.7)
                self.metrics.field_test_success_rate = successful_tests / len(completed_tests)
            
            # Save updated metrics
            await self.db.save_validation_metrics(self.metrics)
            
        except Exception as e:
            logger.error(f"Failed to update validation metrics: {e}")
            raise
    
    async def get_validation_status(self, validation_id: UUID) -> Dict[str, Any]:
        """Get validation status and progress."""
        try:
            validation_data = await self.db.get_validation_request(validation_id)
            reviews_data = await self.db.get_validation_reviews(validation_id)
            
            status = {
                "validation_id": validation_id,
                "status": validation_data['status'],
                "progress_percentage": len(reviews_data) / len(validation_data['assigned_experts']) * 100,
                "expert_reviews": len(reviews_data),
                "total_experts_assigned": len(validation_data['assigned_experts']),
                "deadline": validation_data['deadline'],
                "overall_approval": all(review['approval_status'] for review in reviews_data) if reviews_data else None
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get validation status: {e}")
            raise
    
    async def get_validation_metrics(self) -> ValidationMetrics:
        """Get current validation metrics."""
        return self.metrics
    
    async def get_expert_panel_status(self) -> Dict[str, Any]:
        """Get expert panel status and availability."""
        try:
            total_experts = len(self.expert_panel)
            available_experts = sum(1 for expert in self.expert_panel.values() if expert.availability_status == "available")
            assigned_experts = sum(1 for expert in self.expert_panel.values() if expert.availability_status == "assigned")
            
            expert_types_count = {}
            for expert in self.expert_panel.values():
                for expertise in expert.expertise_areas:
                    expert_types_count[expertise] = expert_types_count.get(expertise, 0) + 1
            
            return {
                "total_experts": total_experts,
                "available_experts": available_experts,
                "assigned_experts": assigned_experts,
                "expert_types_distribution": expert_types_count,
                "average_approval_rate": sum(expert.approval_rate for expert in self.expert_panel.values()) / total_experts if total_experts > 0 else 0.0,
                "average_experience_years": sum(expert.years_experience for expert in self.expert_panel.values()) / total_experts if total_experts > 0 else 0.0
            }
            
        except Exception as e:
            logger.error(f"Failed to get expert panel status: {e}")
            raise
    
    async def generate_validation_report(self, validation_id: UUID) -> Dict[str, Any]:
        """Generate comprehensive validation report."""
        try:
            validation_data = await self.db.get_validation_request(validation_id)
            reviews_data = await self.db.get_validation_reviews(validation_id)
            
            report = {
                "validation_summary": {
                    "validation_id": validation_id,
                    "recommendation_id": validation_data['recommendation_id'],
                    "priority_level": validation_data['priority_level'],
                    "created_at": validation_data['created_at'],
                    "deadline": validation_data['deadline'],
                    "status": validation_data['status']
                },
                "expert_reviews": [],
                "overall_assessment": {
                    "total_reviews": len(reviews_data),
                    "approval_rate": sum(1 for review in reviews_data if review['approval_status']) / len(reviews_data) if reviews_data else 0.0,
                    "average_score": sum(review['overall_score'] for review in reviews_data) / len(reviews_data) if reviews_data else 0.0,
                    "consensus": "approved" if all(review['approval_status'] for review in reviews_data) else "rejected" if reviews_data else "pending"
                },
                "recommendations": validation_data['conservation_recommendations'],
                "water_savings_estimates": validation_data['water_savings_estimates']
            }
            
            # Add detailed expert reviews
            for review in reviews_data:
                expert = self.expert_panel.get(review['expert_id'])
                expert_review_detail = {
                    "expert_name": expert.name if expert else "Unknown",
                    "expert_type": review['expert_type'],
                    "overall_score": review['overall_score'],
                    "approval_status": review['approval_status'],
                    "comments": review['comments'],
                    "recommendations": review['recommendations'],
                    "concerns": review['concerns'],
                    "review_time_hours": review['review_time_hours'],
                    "submitted_at": review['submitted_at']
                }
                report["expert_reviews"].append(expert_review_detail)
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate validation report: {e}")
            raise
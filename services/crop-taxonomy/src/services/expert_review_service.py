"""
Expert Review Management Service

This service manages the expert review process for agricultural validation,
including expert panel management, review workflows, and quality assurance.

Author: AI Assistant
Date: 2024-12-28
Version: 1.0
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID, uuid4
from enum import Enum

from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession

from services.agricultural_validation_service import ExpertReviewer, ExpertReview, ExpertReviewStatus
from database.recommendation_management_db import RecommendationManagementDB

logger = logging.getLogger(__name__)


class ReviewPriority(str, Enum):
    """Priority levels for expert reviews."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ReviewAssignmentStatus(str, Enum):
    """Status of review assignments."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class ReviewAssignment(BaseModel):
    """Expert review assignment."""
    assignment_id: UUID = Field(default_factory=uuid4)
    validation_id: UUID = Field(..., description="Validation ID to review")
    reviewer_id: UUID = Field(..., description="Assigned expert reviewer")
    priority: ReviewPriority = Field(default=ReviewPriority.NORMAL)
    status: ReviewAssignmentStatus = Field(default=ReviewAssignmentStatus.PENDING)
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    due_date: datetime = Field(..., description="Review due date")
    completed_at: Optional[datetime] = None
    review_notes: Optional[str] = None
    escalation_reason: Optional[str] = None
    created_by: UUID = Field(..., description="User who created the assignment")


class ExpertReviewWorkflow(BaseModel):
    """Expert review workflow configuration."""
    workflow_id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., description="Workflow name")
    description: str = Field(..., description="Workflow description")
    region: str = Field(..., description="Applicable region")
    crop_types: List[str] = Field(..., description="Applicable crop types")
    required_specializations: List[str] = Field(..., description="Required expert specializations")
    review_criteria: Dict[str, Any] = Field(..., description="Review criteria and weights")
    auto_assignment_rules: Dict[str, Any] = Field(..., description="Auto-assignment rules")
    escalation_rules: Dict[str, Any] = Field(..., description="Escalation rules")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ExpertReviewService:
    """
    Expert review management service for agricultural validation.
    
    This service provides:
    - Expert panel management
    - Review assignment and workflow
    - Quality assurance and monitoring
    - Performance tracking and reporting
    """

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.db_manager = RecommendationManagementDB(db_session)
        
        # Review configuration
        self.review_timeouts = {
            ReviewPriority.LOW: timedelta(days=14),
            ReviewPriority.NORMAL: timedelta(days=7),
            ReviewPriority.HIGH: timedelta(days=3),
            ReviewPriority.URGENT: timedelta(hours=24)
        }
        
        # Quality thresholds
        self.quality_thresholds = {
            "minimum_expert_score": 0.7,
            "minimum_agricultural_soundness": 0.8,
            "minimum_regional_applicability": 0.7,
            "minimum_economic_feasibility": 0.6,
            "minimum_farmer_practicality": 0.7
        }

    async def create_expert_reviewer(
        self,
        name: str,
        credentials: str,
        specialization: List[str],
        region: str,
        institution: str,
        contact_email: str
    ) -> ExpertReviewer:
        """Create a new expert reviewer profile."""
        try:
            reviewer = ExpertReviewer(
                name=name,
                credentials=credentials,
                specialization=specialization,
                region=region,
                institution=institution,
                contact_email=contact_email
            )
            
            await self.db_manager.store_expert_reviewer(reviewer)
            logger.info(f"Created expert reviewer: {reviewer.reviewer_id}")
            
            return reviewer
            
        except Exception as e:
            logger.error(f"Failed to create expert reviewer: {e}")
            raise

    async def get_expert_reviewers(
        self,
        region: Optional[str] = None,
        crop_type: Optional[str] = None,
        specialization: Optional[List[str]] = None,
        active_only: bool = True
    ) -> List[ExpertReviewer]:
        """Get expert reviewers matching criteria."""
        try:
            reviewers = await self.db_manager.get_expert_reviewers(
                region=region,
                crop_type=crop_type,
                specialization=specialization,
                active_only=active_only
            )
            return reviewers
        except Exception as e:
            logger.error(f"Failed to get expert reviewers: {e}")
            return []

    async def assign_expert_review(
        self,
        validation_id: UUID,
        region: str,
        crop_type: str,
        priority: ReviewPriority = ReviewPriority.NORMAL,
        assigned_by: UUID = None
    ) -> ReviewAssignment:
        """Assign expert review for a validation."""
        try:
            # Find suitable reviewers
            suitable_reviewers = await self._find_suitable_reviewers(
                region=region,
                crop_type=crop_type,
                priority=priority
            )
            
            if not suitable_reviewers:
                raise ValueError(f"No suitable expert reviewers found for region {region} and crop {crop_type}")
            
            # Select best reviewer (least busy, highest rating)
            selected_reviewer = await self._select_best_reviewer(suitable_reviewers)
            
            # Calculate due date
            due_date = datetime.utcnow() + self.review_timeouts[priority]
            
            # Create assignment
            assignment = ReviewAssignment(
                validation_id=validation_id,
                reviewer_id=selected_reviewer.reviewer_id,
                priority=priority,
                due_date=due_date,
                created_by=assigned_by or uuid4()
            )
            
            # Store assignment
            await self.db_manager.store_review_assignment(assignment)
            
            # Update reviewer workload
            await self._update_reviewer_workload(selected_reviewer.reviewer_id, 1)
            
            logger.info(f"Assigned expert review {assignment.assignment_id} to reviewer {selected_reviewer.reviewer_id}")
            
            return assignment
            
        except Exception as e:
            logger.error(f"Failed to assign expert review: {e}")
            raise

    async def _find_suitable_reviewers(
        self,
        region: str,
        crop_type: str,
        priority: ReviewPriority
    ) -> List[ExpertReviewer]:
        """Find suitable expert reviewers for assignment."""
        try:
            # Get reviewers with matching region and crop specialization
            reviewers = await self.db_manager.get_expert_reviewers(
                region=region,
                crop_type=crop_type,
                active_only=True
            )
            
            # Filter by availability and workload
            suitable_reviewers = []
            for reviewer in reviewers:
                if await self._is_reviewer_available(reviewer, priority):
                    suitable_reviewers.append(reviewer)
            
            return suitable_reviewers
            
        except Exception as e:
            logger.error(f"Failed to find suitable reviewers: {e}")
            return []

    async def _select_best_reviewer(self, reviewers: List[ExpertReviewer]) -> ExpertReviewer:
        """Select the best reviewer from available options."""
        if not reviewers:
            raise ValueError("No reviewers available")
        
        # Score reviewers based on multiple factors
        scored_reviewers = []
        for reviewer in reviewers:
            score = await self._calculate_reviewer_score(reviewer)
            scored_reviewers.append((reviewer, score))
        
        # Sort by score (highest first)
        scored_reviewers.sort(key=lambda x: x[1], reverse=True)
        
        return scored_reviewers[0][0]

    async def _calculate_reviewer_score(self, reviewer: ExpertReviewer) -> float:
        """Calculate reviewer score for assignment."""
        score = 0.0
        
        # Base score from average rating
        score += reviewer.average_rating * 0.4
        
        # Experience bonus (more reviews = higher score)
        experience_score = min(reviewer.review_count / 100, 1.0)  # Cap at 100 reviews
        score += experience_score * 0.3
        
        # Availability bonus (less recent activity = higher availability)
        if reviewer.last_review_at:
            days_since_last_review = (datetime.utcnow() - reviewer.last_review_at).days
            availability_score = min(days_since_last_review / 30, 1.0)  # Cap at 30 days
            score += availability_score * 0.3
        else:
            score += 0.3  # New reviewer bonus
        
        return score

    async def _is_reviewer_available(self, reviewer: ExpertReviewer, priority: ReviewPriority) -> bool:
        """Check if reviewer is available for assignment."""
        try:
            # Check current workload
            current_assignments = await self.db_manager.get_reviewer_assignments(
                reviewer_id=reviewer.reviewer_id,
                status_filter=[ReviewAssignmentStatus.PENDING, ReviewAssignmentStatus.IN_PROGRESS]
            )
            
            # Limit concurrent assignments based on priority
            max_assignments = {
                ReviewPriority.LOW: 5,
                ReviewPriority.NORMAL: 3,
                ReviewPriority.HIGH: 2,
                ReviewPriority.URGENT: 1
            }
            
            if len(current_assignments) >= max_assignments[priority]:
                return False
            
            # Check for recent reviews (avoid overloading)
            if reviewer.last_review_at:
                hours_since_last_review = (datetime.utcnow() - reviewer.last_review_at).total_seconds() / 3600
                if hours_since_last_review < 24:  # Minimum 24 hours between reviews
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check reviewer availability: {e}")
            return False

    async def _update_reviewer_workload(self, reviewer_id: UUID, workload_change: int) -> None:
        """Update reviewer workload tracking."""
        try:
            await self.db_manager.update_reviewer_workload(reviewer_id, workload_change)
        except Exception as e:
            logger.error(f"Failed to update reviewer workload: {e}")

    async def submit_expert_review(
        self,
        assignment_id: UUID,
        reviewer_id: UUID,
        review_data: Dict[str, Any]
    ) -> ExpertReview:
        """Submit expert review results."""
        try:
            # Get assignment
            assignment = await self.db_manager.get_review_assignment(assignment_id)
            if not assignment:
                raise ValueError(f"Review assignment {assignment_id} not found")
            
            if assignment.reviewer_id != reviewer_id:
                raise ValueError("Reviewer ID does not match assignment")
            
            if assignment.status != ReviewAssignmentStatus.IN_PROGRESS:
                raise ValueError(f"Assignment status {assignment.status} does not allow review submission")
            
            # Create expert review
            expert_review = ExpertReview(
                validation_id=assignment.validation_id,
                reviewer_id=reviewer_id,
                status=ExpertReviewStatus.APPROVED if review_data.get("overall_approval") else ExpertReviewStatus.REJECTED,
                review_score=review_data.get("overall_score", 0.0),
                agricultural_soundness=review_data.get("agricultural_soundness", 0.0),
                regional_applicability=review_data.get("regional_applicability", 0.0),
                economic_feasibility=review_data.get("economic_feasibility", 0.0),
                farmer_practicality=review_data.get("farmer_practicality", 0.0),
                comments=review_data.get("comments", ""),
                recommendations=review_data.get("recommendations", []),
                concerns=review_data.get("concerns", []),
                approval_conditions=review_data.get("approval_conditions", [])
            )
            
            # Validate review quality
            quality_check = await self._validate_review_quality(expert_review)
            if not quality_check["passed"]:
                expert_review.status = ExpertReviewStatus.NEEDS_REVISION
                expert_review.comments += f"\n\nQuality Issues: {quality_check['issues']}"
            
            # Store review
            await self.db_manager.store_expert_review(expert_review)
            
            # Update assignment
            assignment.status = ReviewAssignmentStatus.COMPLETED
            assignment.completed_at = datetime.utcnow()
            assignment.review_notes = expert_review.comments
            await self.db_manager.update_review_assignment(assignment)
            
            # Update reviewer statistics
            await self._update_reviewer_statistics(reviewer_id, expert_review)
            
            logger.info(f"Expert review submitted for assignment {assignment_id}")
            
            return expert_review
            
        except Exception as e:
            logger.error(f"Failed to submit expert review: {e}")
            raise

    async def _validate_review_quality(self, review: ExpertReview) -> Dict[str, Any]:
        """Validate expert review quality."""
        issues = []
        
        # Check minimum scores
        if review.agricultural_soundness < self.quality_thresholds["minimum_agricultural_soundness"]:
            issues.append("Agricultural soundness score too low")
        
        if review.regional_applicability < self.quality_thresholds["minimum_regional_applicability"]:
            issues.append("Regional applicability score too low")
        
        if review.economic_feasibility < self.quality_thresholds["minimum_economic_feasibility"]:
            issues.append("Economic feasibility score too low")
        
        if review.farmer_practicality < self.quality_thresholds["minimum_farmer_practicality"]:
            issues.append("Farmer practicality score too low")
        
        # Check comment quality
        if len(review.comments.strip()) < 50:
            issues.append("Review comments too brief")
        
        # Check for specific recommendations
        if not review.recommendations:
            issues.append("No specific recommendations provided")
        
        return {
            "passed": len(issues) == 0,
            "issues": "; ".join(issues)
        }

    async def _update_reviewer_statistics(self, reviewer_id: UUID, review: ExpertReview) -> None:
        """Update reviewer statistics after review submission."""
        try:
            # Update review count
            await self.db_manager.increment_reviewer_review_count(reviewer_id)
            
            # Update average rating (simplified calculation)
            await self.db_manager.update_reviewer_average_rating(reviewer_id, review.review_score)
            
            # Update last review timestamp
            await self.db_manager.update_reviewer_last_review(reviewer_id, datetime.utcnow())
            
        except Exception as e:
            logger.error(f"Failed to update reviewer statistics: {e}")

    async def get_reviewer_performance(
        self,
        reviewer_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get reviewer performance metrics."""
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=90)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Get reviewer reviews in period
            reviews = await self.db_manager.get_reviewer_reviews(
                reviewer_id=reviewer_id,
                start_date=start_date,
                end_date=end_date
            )
            
            if not reviews:
                return {
                    "review_count": 0,
                    "average_score": 0.0,
                    "completion_rate": 0.0,
                    "on_time_rate": 0.0,
                    "quality_score": 0.0
                }
            
            # Calculate metrics
            total_reviews = len(reviews)
            approved_reviews = len([r for r in reviews if r.status == ExpertReviewStatus.APPROVED])
            on_time_reviews = len([r for r in reviews if r.created_at <= r.created_at + timedelta(days=7)])
            
            average_score = sum(r.review_score for r in reviews) / total_reviews
            completion_rate = approved_reviews / total_reviews
            on_time_rate = on_time_reviews / total_reviews
            
            # Calculate quality score
            quality_scores = []
            for review in reviews:
                quality_check = await self._validate_review_quality(review)
                quality_scores.append(1.0 if quality_check["passed"] else 0.0)
            
            quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
            
            return {
                "review_count": total_reviews,
                "average_score": average_score,
                "completion_rate": completion_rate,
                "on_time_rate": on_time_rate,
                "quality_score": quality_score,
                "period_start": start_date,
                "period_end": end_date
            }
            
        except Exception as e:
            logger.error(f"Failed to get reviewer performance: {e}")
            return {}

    async def escalate_overdue_reviews(self) -> List[ReviewAssignment]:
        """Escalate overdue reviews."""
        try:
            overdue_assignments = await self.db_manager.get_overdue_review_assignments()
            escalated_assignments = []
            
            for assignment in overdue_assignments:
                # Update status to overdue
                assignment.status = ReviewAssignmentStatus.OVERDUE
                assignment.escalation_reason = "Review overdue"
                await self.db_manager.update_review_assignment(assignment)
                
                # Try to reassign if high priority
                if assignment.priority in [ReviewPriority.HIGH, ReviewPriority.URGENT]:
                    try:
                        new_assignment = await self.assign_expert_review(
                            validation_id=assignment.validation_id,
                            region="unknown",  # Would need to get from validation
                            crop_type="unknown",  # Would need to get from validation
                            priority=ReviewPriority.HIGH
                        )
                        escalated_assignments.append(new_assignment)
                    except Exception as e:
                        logger.error(f"Failed to reassign overdue review {assignment.assignment_id}: {e}")
                
                escalated_assignments.append(assignment)
            
            logger.info(f"Escalated {len(escalated_assignments)} overdue reviews")
            return escalated_assignments
            
        except Exception as e:
            logger.error(f"Failed to escalate overdue reviews: {e}")
            return []

    async def get_expert_review_workflow(
        self,
        region: str,
        crop_type: str
    ) -> Optional[ExpertReviewWorkflow]:
        """Get expert review workflow for region and crop."""
        try:
            workflows = await self.db_manager.get_expert_review_workflows(
                region=region,
                crop_type=crop_type,
                active_only=True
            )
            
            if workflows:
                return workflows[0]  # Return first matching workflow
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get expert review workflow: {e}")
            return None

    async def create_expert_review_workflow(
        self,
        name: str,
        description: str,
        region: str,
        crop_types: List[str],
        required_specializations: List[str],
        review_criteria: Dict[str, Any],
        auto_assignment_rules: Dict[str, Any],
        escalation_rules: Dict[str, Any]
    ) -> ExpertReviewWorkflow:
        """Create a new expert review workflow."""
        try:
            workflow = ExpertReviewWorkflow(
                name=name,
                description=description,
                region=region,
                crop_types=crop_types,
                required_specializations=required_specializations,
                review_criteria=review_criteria,
                auto_assignment_rules=auto_assignment_rules,
                escalation_rules=escalation_rules
            )
            
            await self.db_manager.store_expert_review_workflow(workflow)
            logger.info(f"Created expert review workflow: {workflow.workflow_id}")
            
            return workflow
            
        except Exception as e:
            logger.error(f"Failed to create expert review workflow: {e}")
            raise
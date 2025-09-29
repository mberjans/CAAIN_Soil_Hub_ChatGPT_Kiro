"""
Validation Management Database Operations

This module provides database operations for agricultural validation,
expert review management, and metrics tracking.

Author: AI Assistant
Date: 2024-12-28
Version: 1.0
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import selectinload

from ..models.validation_models import (
    ValidationResult, ValidationStatus, ExpertReviewStatus,
    ExpertReviewer, ExpertReview, ReviewAssignment, ReviewAssignmentStatus,
    ValidationMetricsReport, MetricsPeriod
)
from ..models.crop_variety_models import VarietyRecommendation

logger = logging.getLogger(__name__)


class ValidationManagementDB:
    """
    Database operations for validation management.
    
    This class provides:
    - Validation result storage and retrieval
    - Expert reviewer management
    - Review assignment tracking
    - Metrics and reporting data
    """

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def store_validation_result(self, validation_result: ValidationResult) -> None:
        """Store validation result in database."""
        try:
            # Convert validation result to database record
            validation_record = {
                "validation_id": validation_result.validation_id,
                "status": validation_result.status.value,
                "overall_score": validation_result.overall_score,
                "issues": json.dumps([{
                    "severity": issue.severity.value,
                    "category": issue.category,
                    "message": issue.message,
                    "recommendation_id": str(issue.recommendation_id) if issue.recommendation_id else None,
                    "variety_id": str(issue.variety_id) if issue.variety_id else None,
                    "details": issue.details,
                    "suggested_action": issue.suggested_action
                } for issue in validation_result.issues]),
                "expert_review_required": validation_result.expert_review_required,
                "validation_timestamp": validation_result.validation_timestamp,
                "validation_duration_ms": validation_result.validation_duration_ms,
                "regional_context": json.dumps(validation_result.regional_context),
                "crop_context": json.dumps(validation_result.crop_context),
                "expert_review_status": validation_result.expert_review_status.value if validation_result.expert_review_status else None,
                "expert_feedback": validation_result.expert_feedback,
                "expert_reviewer_id": str(validation_result.expert_reviewer_id) if validation_result.expert_reviewer_id else None,
                "expert_review_timestamp": validation_result.expert_review_timestamp,
                "created_at": datetime.utcnow()
            }
            
            # Insert into database
            query = """
                INSERT INTO validation_results (
                    validation_id, status, overall_score, issues, expert_review_required,
                    validation_timestamp, validation_duration_ms, regional_context,
                    crop_context, expert_review_status, expert_feedback,
                    expert_reviewer_id, expert_review_timestamp, created_at
                ) VALUES (
                    :validation_id, :status, :overall_score, :issues, :expert_review_required,
                    :validation_timestamp, :validation_duration_ms, :regional_context,
                    :crop_context, :expert_review_status, :expert_feedback,
                    :expert_reviewer_id, :expert_review_timestamp, :created_at
                )
            """
            
            await self.db_session.execute(query, validation_record)
            await self.db_session.commit()
            
            logger.info(f"Stored validation result: {validation_result.validation_id}")
            
        except Exception as e:
            logger.error(f"Failed to store validation result: {e}")
            await self.db_session.rollback()
            raise

    async def get_validation_results(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status_filter: Optional[List[ValidationStatus]] = None
    ) -> List[ValidationResult]:
        """Get validation results with optional filtering."""
        try:
            query = """
                SELECT * FROM validation_results
                WHERE 1=1
            """
            params = {}
            
            if start_date:
                query += " AND validation_timestamp >= :start_date"
                params["start_date"] = start_date
            
            if end_date:
                query += " AND validation_timestamp <= :end_date"
                params["end_date"] = end_date
            
            if status_filter:
                status_values = [status.value for status in status_filter]
                query += " AND status IN :status_filter"
                params["status_filter"] = status_values
            
            query += " ORDER BY validation_timestamp DESC"
            
            result = await self.db_session.execute(query, params)
            rows = result.fetchall()
            
            validation_results = []
            for row in rows:
                # Convert database row to ValidationResult object
                validation_result = ValidationResult(
                    validation_id=row.validation_id,
                    status=ValidationStatus(row.status),
                    overall_score=row.overall_score,
                    issues=[],  # Would need to parse JSON
                    expert_review_required=row.expert_review_required,
                    validation_timestamp=row.validation_timestamp,
                    validation_duration_ms=row.validation_duration_ms,
                    regional_context=json.loads(row.regional_context),
                    crop_context=json.loads(row.crop_context),
                    expert_review_status=ExpertReviewStatus(row.expert_review_status) if row.expert_review_status else None,
                    expert_feedback=row.expert_feedback,
                    expert_reviewer_id=UUID(row.expert_reviewer_id) if row.expert_reviewer_id else None,
                    expert_review_timestamp=row.expert_review_timestamp
                )
                validation_results.append(validation_result)
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Failed to get validation results: {e}")
            return []

    async def store_expert_reviewer(self, reviewer: ExpertReviewer) -> None:
        """Store expert reviewer in database."""
        try:
            reviewer_record = {
                "reviewer_id": reviewer.reviewer_id,
                "name": reviewer.name,
                "credentials": reviewer.credentials,
                "specialization": json.dumps(reviewer.specialization),
                "region": reviewer.region,
                "institution": reviewer.institution,
                "contact_email": reviewer.contact_email,
                "is_active": reviewer.is_active,
                "review_count": reviewer.review_count,
                "average_rating": reviewer.average_rating,
                "created_at": reviewer.created_at,
                "last_review_at": reviewer.last_review_at
            }
            
            query = """
                INSERT INTO expert_reviewers (
                    reviewer_id, name, credentials, specialization, region,
                    institution, contact_email, is_active, review_count,
                    average_rating, created_at, last_review_at
                ) VALUES (
                    :reviewer_id, :name, :credentials, :specialization, :region,
                    :institution, :contact_email, :is_active, :review_count,
                    :average_rating, :created_at, :last_review_at
                )
            """
            
            await self.db_session.execute(query, reviewer_record)
            await self.db_session.commit()
            
            logger.info(f"Stored expert reviewer: {reviewer.reviewer_id}")
            
        except Exception as e:
            logger.error(f"Failed to store expert reviewer: {e}")
            await self.db_session.rollback()
            raise

    async def get_expert_reviewers(
        self,
        region: Optional[str] = None,
        crop_type: Optional[str] = None,
        specialization: Optional[List[str]] = None,
        active_only: bool = True
    ) -> List[ExpertReviewer]:
        """Get expert reviewers with optional filtering."""
        try:
            query = """
                SELECT * FROM expert_reviewers
                WHERE 1=1
            """
            params = {}
            
            if active_only:
                query += " AND is_active = true"
            
            if region:
                query += " AND region = :region"
                params["region"] = region
            
            if crop_type and specialization:
                # Check if any specialization matches crop type
                specialization_condition = " OR ".join([f"specialization LIKE :spec_{i}" for i in range(len(specialization))])
                query += f" AND ({specialization_condition})"
                for i, spec in enumerate(specialization):
                    params[f"spec_{i}"] = f"%{spec}%"
            
            query += " ORDER BY average_rating DESC, review_count DESC"
            
            result = await self.db_session.execute(query, params)
            rows = result.fetchall()
            
            reviewers = []
            for row in rows:
                reviewer = ExpertReviewer(
                    reviewer_id=row.reviewer_id,
                    name=row.name,
                    credentials=row.credentials,
                    specialization=json.loads(row.specialization),
                    region=row.region,
                    institution=row.institution,
                    contact_email=row.contact_email,
                    is_active=row.is_active,
                    review_count=row.review_count,
                    average_rating=row.average_rating,
                    created_at=row.created_at,
                    last_review_at=row.last_review_at
                )
                reviewers.append(reviewer)
            
            return reviewers
            
        except Exception as e:
            logger.error(f"Failed to get expert reviewers: {e}")
            return []

    async def store_expert_review(self, review: ExpertReview) -> None:
        """Store expert review in database."""
        try:
            review_record = {
                "review_id": review.review_id,
                "validation_id": review.validation_id,
                "reviewer_id": review.reviewer_id,
                "status": review.status.value,
                "review_score": review.review_score,
                "agricultural_soundness": review.agricultural_soundness,
                "regional_applicability": review.regional_applicability,
                "economic_feasibility": review.economic_feasibility,
                "farmer_practicality": review.farmer_practicality,
                "comments": review.comments,
                "recommendations": json.dumps(review.recommendations),
                "concerns": json.dumps(review.concerns),
                "approval_conditions": json.dumps(review.approval_conditions),
                "created_at": review.created_at,
                "updated_at": review.updated_at
            }
            
            query = """
                INSERT INTO expert_reviews (
                    review_id, validation_id, reviewer_id, status, review_score,
                    agricultural_soundness, regional_applicability, economic_feasibility,
                    farmer_practicality, comments, recommendations, concerns,
                    approval_conditions, created_at, updated_at
                ) VALUES (
                    :review_id, :validation_id, :reviewer_id, :status, :review_score,
                    :agricultural_soundness, :regional_applicability, :economic_feasibility,
                    :farmer_practicality, :comments, :recommendations, :concerns,
                    :approval_conditions, :created_at, :updated_at
                )
            """
            
            await self.db_session.execute(query, review_record)
            await self.db_session.commit()
            
            logger.info(f"Stored expert review: {review.review_id}")
            
        except Exception as e:
            logger.error(f"Failed to store expert review: {e}")
            await self.db_session.rollback()
            raise

    async def get_expert_reviews(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status_filter: Optional[List[ExpertReviewStatus]] = None,
        reviewer_id: Optional[UUID] = None
    ) -> List[ExpertReview]:
        """Get expert reviews with optional filtering."""
        try:
            query = """
                SELECT * FROM expert_reviews
                WHERE 1=1
            """
            params = {}
            
            if start_date:
                query += " AND created_at >= :start_date"
                params["start_date"] = start_date
            
            if end_date:
                query += " AND created_at <= :end_date"
                params["end_date"] = end_date
            
            if status_filter:
                status_values = [status.value for status in status_filter]
                query += " AND status IN :status_filter"
                params["status_filter"] = status_values
            
            if reviewer_id:
                query += " AND reviewer_id = :reviewer_id"
                params["reviewer_id"] = reviewer_id
            
            query += " ORDER BY created_at DESC"
            
            result = await self.db_session.execute(query, params)
            rows = result.fetchall()
            
            reviews = []
            for row in rows:
                review = ExpertReview(
                    review_id=row.review_id,
                    validation_id=row.validation_id,
                    reviewer_id=row.reviewer_id,
                    status=ExpertReviewStatus(row.status),
                    review_score=row.review_score,
                    agricultural_soundness=row.agricultural_soundness,
                    regional_applicability=row.regional_applicability,
                    economic_feasibility=row.economic_feasibility,
                    farmer_practicality=row.farmer_practicality,
                    comments=row.comments,
                    recommendations=json.loads(row.recommendations),
                    concerns=json.loads(row.concerns),
                    approval_conditions=json.loads(row.approval_conditions),
                    created_at=row.created_at,
                    updated_at=row.updated_at
                )
                reviews.append(review)
            
            return reviews
            
        except Exception as e:
            logger.error(f"Failed to get expert reviews: {e}")
            return []

    async def store_review_assignment(self, assignment: ReviewAssignment) -> None:
        """Store review assignment in database."""
        try:
            assignment_record = {
                "assignment_id": assignment.assignment_id,
                "validation_id": assignment.validation_id,
                "reviewer_id": assignment.reviewer_id,
                "priority": assignment.priority.value,
                "status": assignment.status.value,
                "assigned_at": assignment.assigned_at,
                "due_date": assignment.due_date,
                "completed_at": assignment.completed_at,
                "review_notes": assignment.review_notes,
                "escalation_reason": assignment.escalation_reason,
                "created_by": assignment.created_by
            }
            
            query = """
                INSERT INTO review_assignments (
                    assignment_id, validation_id, reviewer_id, priority, status,
                    assigned_at, due_date, completed_at, review_notes,
                    escalation_reason, created_by
                ) VALUES (
                    :assignment_id, :validation_id, :reviewer_id, :priority, :status,
                    :assigned_at, :due_date, :completed_at, :review_notes,
                    :escalation_reason, :created_by
                )
            """
            
            await self.db_session.execute(query, assignment_record)
            await self.db_session.commit()
            
            logger.info(f"Stored review assignment: {assignment.assignment_id}")
            
        except Exception as e:
            logger.error(f"Failed to store review assignment: {e}")
            await self.db_session.rollback()
            raise

    async def get_review_assignment(self, assignment_id: UUID) -> Optional[ReviewAssignment]:
        """Get review assignment by ID."""
        try:
            query = """
                SELECT * FROM review_assignments
                WHERE assignment_id = :assignment_id
            """
            
            result = await self.db_session.execute(query, {"assignment_id": assignment_id})
            row = result.fetchone()
            
            if row:
                assignment = ReviewAssignment(
                    assignment_id=row.assignment_id,
                    validation_id=row.validation_id,
                    reviewer_id=row.reviewer_id,
                    priority=row.priority,
                    status=row.status,
                    assigned_at=row.assigned_at,
                    due_date=row.due_date,
                    completed_at=row.completed_at,
                    review_notes=row.review_notes,
                    escalation_reason=row.escalation_reason,
                    created_by=row.created_by
                )
                return assignment
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get review assignment: {e}")
            return None

    async def get_review_assignment_by_validation_id(self, validation_id: UUID) -> Optional[ReviewAssignment]:
        """Get review assignment by validation ID."""
        try:
            query = """
                SELECT * FROM review_assignments
                WHERE validation_id = :validation_id
                ORDER BY assigned_at DESC
                LIMIT 1
            """
            
            result = await self.db_session.execute(query, {"validation_id": validation_id})
            row = result.fetchone()
            
            if row:
                assignment = ReviewAssignment(
                    assignment_id=row.assignment_id,
                    validation_id=row.validation_id,
                    reviewer_id=row.reviewer_id,
                    priority=row.priority,
                    status=row.status,
                    assigned_at=row.assigned_at,
                    due_date=row.due_date,
                    completed_at=row.completed_at,
                    review_notes=row.review_notes,
                    escalation_reason=row.escalation_reason,
                    created_by=row.created_by
                )
                return assignment
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get review assignment by validation ID: {e}")
            return None

    async def get_reviewer_assignments(
        self,
        reviewer_id: UUID,
        status_filter: Optional[List[ReviewAssignmentStatus]] = None
    ) -> List[ReviewAssignment]:
        """Get reviewer assignments with optional status filtering."""
        try:
            query = """
                SELECT * FROM review_assignments
                WHERE reviewer_id = :reviewer_id
            """
            params = {"reviewer_id": reviewer_id}
            
            if status_filter:
                status_values = [status.value for status in status_filter]
                query += " AND status IN :status_filter"
                params["status_filter"] = status_values
            
            query += " ORDER BY assigned_at DESC"
            
            result = await self.db_session.execute(query, params)
            rows = result.fetchall()
            
            assignments = []
            for row in rows:
                assignment = ReviewAssignment(
                    assignment_id=row.assignment_id,
                    validation_id=row.validation_id,
                    reviewer_id=row.reviewer_id,
                    priority=row.priority,
                    status=row.status,
                    assigned_at=row.assigned_at,
                    due_date=row.due_date,
                    completed_at=row.completed_at,
                    review_notes=row.review_notes,
                    escalation_reason=row.escalation_reason,
                    created_by=row.created_by
                )
                assignments.append(assignment)
            
            return assignments
            
        except Exception as e:
            logger.error(f"Failed to get reviewer assignments: {e}")
            return []

    async def get_overdue_review_assignments(self) -> List[ReviewAssignment]:
        """Get overdue review assignments."""
        try:
            query = """
                SELECT * FROM review_assignments
                WHERE status IN ('pending', 'assigned', 'in_progress')
                AND due_date < :current_time
                ORDER BY due_date ASC
            """
            
            result = await self.db_session.execute(query, {"current_time": datetime.utcnow()})
            rows = result.fetchall()
            
            assignments = []
            for row in rows:
                assignment = ReviewAssignment(
                    assignment_id=row.assignment_id,
                    validation_id=row.validation_id,
                    reviewer_id=row.reviewer_id,
                    priority=row.priority,
                    status=row.status,
                    assigned_at=row.assigned_at,
                    due_date=row.due_date,
                    completed_at=row.completed_at,
                    review_notes=row.review_notes,
                    escalation_reason=row.escalation_reason,
                    created_by=row.created_by
                )
                assignments.append(assignment)
            
            return assignments
            
        except Exception as e:
            logger.error(f"Failed to get overdue review assignments: {e}")
            return []

    async def update_review_assignment(self, assignment: ReviewAssignment) -> None:
        """Update review assignment."""
        try:
            query = """
                UPDATE review_assignments
                SET status = :status, completed_at = :completed_at,
                    review_notes = :review_notes, escalation_reason = :escalation_reason
                WHERE assignment_id = :assignment_id
            """
            
            params = {
                "assignment_id": assignment.assignment_id,
                "status": assignment.status.value,
                "completed_at": assignment.completed_at,
                "review_notes": assignment.review_notes,
                "escalation_reason": assignment.escalation_reason
            }
            
            await self.db_session.execute(query, params)
            await self.db_session.commit()
            
            logger.info(f"Updated review assignment: {assignment.assignment_id}")
            
        except Exception as e:
            logger.error(f"Failed to update review assignment: {e}")
            await self.db_session.rollback()
            raise

    async def store_farmer_feedback(
        self,
        recommendation_id: UUID,
        farmer_id: UUID,
        satisfaction_score: float,
        feedback: Optional[str] = None
    ) -> None:
        """Store farmer feedback."""
        try:
            feedback_record = {
                "feedback_id": UUID(),
                "recommendation_id": recommendation_id,
                "farmer_id": farmer_id,
                "satisfaction_score": satisfaction_score,
                "feedback": feedback,
                "created_at": datetime.utcnow()
            }
            
            query = """
                INSERT INTO farmer_feedback (
                    feedback_id, recommendation_id, farmer_id, satisfaction_score,
                    feedback, created_at
                ) VALUES (
                    :feedback_id, :recommendation_id, :farmer_id, :satisfaction_score,
                    :feedback, :created_at
                )
            """
            
            await self.db_session.execute(query, feedback_record)
            await self.db_session.commit()
            
            logger.info(f"Stored farmer feedback for recommendation: {recommendation_id}")
            
        except Exception as e:
            logger.error(f"Failed to store farmer feedback: {e}")
            await self.db_session.rollback()
            raise

    async def get_farmer_feedback(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        farmer_id: Optional[UUID] = None
    ) -> List[Dict[str, Any]]:
        """Get farmer feedback with optional filtering."""
        try:
            query = """
                SELECT * FROM farmer_feedback
                WHERE 1=1
            """
            params = {}
            
            if start_date:
                query += " AND created_at >= :start_date"
                params["start_date"] = start_date
            
            if end_date:
                query += " AND created_at <= :end_date"
                params["end_date"] = end_date
            
            if farmer_id:
                query += " AND farmer_id = :farmer_id"
                params["farmer_id"] = farmer_id
            
            query += " ORDER BY created_at DESC"
            
            result = await self.db_session.execute(query, params)
            rows = result.fetchall()
            
            feedback_list = []
            for row in rows:
                feedback = {
                    "feedback_id": row.feedback_id,
                    "recommendation_id": row.recommendation_id,
                    "farmer_id": row.farmer_id,
                    "satisfaction_score": row.satisfaction_score,
                    "feedback": row.feedback,
                    "created_at": row.created_at
                }
                feedback_list.append(feedback)
            
            return feedback_list
            
        except Exception as e:
            logger.error(f"Failed to get farmer feedback: {e}")
            return []

    async def store_metrics_report(self, report: ValidationMetricsReport) -> None:
        """Store validation metrics report."""
        try:
            report_record = {
                "report_id": report.report_id,
                "period_start": report.period_start,
                "period_end": report.period_end,
                "period_type": report.period_type.value,
                "total_validations": report.total_validations,
                "successful_validations": report.successful_validations,
                "failed_validations": report.failed_validations,
                "validation_success_rate": report.validation_success_rate,
                "average_validation_score": report.average_validation_score,
                "average_validation_duration_ms": report.average_validation_duration_ms,
                "expert_reviews_required": report.expert_reviews_required,
                "expert_reviews_completed": report.expert_reviews_completed,
                "expert_reviews_pending": report.expert_reviews_pending,
                "expert_reviews_overdue": report.expert_reviews_overdue,
                "expert_review_completion_rate": report.expert_review_completion_rate,
                "average_expert_score": report.average_expert_score,
                "average_expert_review_duration_hours": report.average_expert_review_duration_hours,
                "agricultural_soundness_score": report.agricultural_soundness_score,
                "regional_applicability_score": report.regional_applicability_score,
                "economic_feasibility_score": report.economic_feasibility_score,
                "farmer_practicality_score": report.farmer_practicality_score,
                "regional_coverage": json.dumps(report.regional_coverage),
                "crop_coverage": json.dumps(report.crop_coverage),
                "farmer_feedback_count": report.farmer_feedback_count,
                "average_farmer_satisfaction": report.average_farmer_satisfaction,
                "farmer_satisfaction_distribution": json.dumps(report.farmer_satisfaction_distribution),
                "validation_trend": report.validation_trend,
                "expert_review_trend": report.expert_review_trend,
                "farmer_satisfaction_trend": report.farmer_satisfaction_trend,
                "common_validation_issues": json.dumps(report.common_validation_issues),
                "expert_concerns": json.dumps(report.expert_concerns),
                "farmer_complaints": json.dumps(report.farmer_complaints),
                "improvement_recommendations": json.dumps(report.improvement_recommendations),
                "generated_at": report.generated_at
            }
            
            query = """
                INSERT INTO validation_metrics_reports (
                    report_id, period_start, period_end, period_type,
                    total_validations, successful_validations, failed_validations,
                    validation_success_rate, average_validation_score, average_validation_duration_ms,
                    expert_reviews_required, expert_reviews_completed, expert_reviews_pending,
                    expert_reviews_overdue, expert_review_completion_rate, average_expert_score,
                    average_expert_review_duration_hours, agricultural_soundness_score,
                    regional_applicability_score, economic_feasibility_score, farmer_practicality_score,
                    regional_coverage, crop_coverage, farmer_feedback_count,
                    average_farmer_satisfaction, farmer_satisfaction_distribution,
                    validation_trend, expert_review_trend, farmer_satisfaction_trend,
                    common_validation_issues, expert_concerns, farmer_complaints,
                    improvement_recommendations, generated_at
                ) VALUES (
                    :report_id, :period_start, :period_end, :period_type,
                    :total_validations, :successful_validations, :failed_validations,
                    :validation_success_rate, :average_validation_score, :average_validation_duration_ms,
                    :expert_reviews_required, :expert_reviews_completed, :expert_reviews_pending,
                    :expert_reviews_overdue, :expert_review_completion_rate, :average_expert_score,
                    :average_expert_review_duration_hours, :agricultural_soundness_score,
                    :regional_applicability_score, :economic_feasibility_score, :farmer_practicality_score,
                    :regional_coverage, :crop_coverage, :farmer_feedback_count,
                    :average_farmer_satisfaction, :farmer_satisfaction_distribution,
                    :validation_trend, :expert_review_trend, :farmer_satisfaction_trend,
                    :common_validation_issues, :expert_concerns, :farmer_complaints,
                    :improvement_recommendations, :generated_at
                )
            """
            
            await self.db_session.execute(query, report_record)
            await self.db_session.commit()
            
            logger.info(f"Stored validation metrics report: {report.report_id}")
            
        except Exception as e:
            logger.error(f"Failed to store validation metrics report: {e}")
            await self.db_session.rollback()
            raise

    async def update_reviewer_statistics(
        self,
        reviewer_id: UUID,
        review_count_increment: int = 1,
        new_average_rating: Optional[float] = None,
        last_review_time: Optional[datetime] = None
    ) -> None:
        """Update reviewer statistics."""
        try:
            query = """
                UPDATE expert_reviewers
                SET review_count = review_count + :increment,
                    average_rating = :average_rating,
                    last_review_at = :last_review_at
                WHERE reviewer_id = :reviewer_id
            """
            
            params = {
                "reviewer_id": reviewer_id,
                "increment": review_count_increment,
                "average_rating": new_average_rating or 0.0,
                "last_review_at": last_review_time or datetime.utcnow()
            }
            
            await self.db_session.execute(query, params)
            await self.db_session.commit()
            
            logger.info(f"Updated reviewer statistics: {reviewer_id}")
            
        except Exception as e:
            logger.error(f"Failed to update reviewer statistics: {e}")
            await self.db_session.rollback()
            raise

    async def increment_reviewer_review_count(self, reviewer_id: UUID) -> None:
        """Increment reviewer review count."""
        await self.update_reviewer_statistics(reviewer_id, review_count_increment=1)

    async def update_reviewer_average_rating(self, reviewer_id: UUID, new_rating: float) -> None:
        """Update reviewer average rating."""
        await self.update_reviewer_statistics(reviewer_id, new_average_rating=new_rating)

    async def update_reviewer_last_review(self, reviewer_id: UUID, last_review_time: datetime) -> None:
        """Update reviewer last review timestamp."""
        await self.update_reviewer_statistics(reviewer_id, last_review_time=last_review_time)
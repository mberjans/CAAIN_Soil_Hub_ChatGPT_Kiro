"""
Validation Metrics and Reporting Service

This service tracks and reports on agricultural validation performance,
expert review metrics, and farmer satisfaction scores.

Author: AI Assistant
Date: 2024-12-28
Version: 1.0
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from services.agricultural_validation_service import ValidationResult, ValidationStatus, ExpertReviewStatus
from database.recommendation_management_db import RecommendationManagementDB

logger = logging.getLogger(__name__)


class MetricsPeriod(str, Enum):
    """Metrics reporting periods."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class ValidationMetricsReport(BaseModel):
    """Comprehensive validation metrics report."""
    report_id: UUID = Field(default_factory=UUID)
    period_start: datetime = Field(..., description="Report period start")
    period_end: datetime = Field(..., description="Report period end")
    period_type: MetricsPeriod = Field(..., description="Report period type")
    
    # Validation metrics
    total_validations: int = Field(default=0, description="Total validations performed")
    successful_validations: int = Field(default=0, description="Successful validations")
    failed_validations: int = Field(default=0, description="Failed validations")
    validation_success_rate: float = Field(default=0.0, description="Validation success rate")
    average_validation_score: float = Field(default=0.0, description="Average validation score")
    average_validation_duration_ms: float = Field(default=0.0, description="Average validation duration")
    
    # Expert review metrics
    expert_reviews_required: int = Field(default=0, description="Expert reviews required")
    expert_reviews_completed: int = Field(default=0, description="Expert reviews completed")
    expert_reviews_pending: int = Field(default=0, description="Expert reviews pending")
    expert_reviews_overdue: int = Field(default=0, description="Expert reviews overdue")
    expert_review_completion_rate: float = Field(default=0.0, description="Expert review completion rate")
    average_expert_score: float = Field(default=0.0, description="Average expert review score")
    average_expert_review_duration_hours: float = Field(default=0.0, description="Average expert review duration")
    
    # Quality metrics
    agricultural_soundness_score: float = Field(default=0.0, description="Average agricultural soundness score")
    regional_applicability_score: float = Field(default=0.0, description="Average regional applicability score")
    economic_feasibility_score: float = Field(default=0.0, description="Average economic feasibility score")
    farmer_practicality_score: float = Field(default=0.0, description="Average farmer practicality score")
    
    # Regional and crop coverage
    regional_coverage: Dict[str, int] = Field(default_factory=dict, description="Validations by region")
    crop_coverage: Dict[str, int] = Field(default_factory=dict, description="Validations by crop type")
    
    # Farmer satisfaction
    farmer_feedback_count: int = Field(default=0, description="Number of farmer feedback responses")
    average_farmer_satisfaction: float = Field(default=0.0, description="Average farmer satisfaction score")
    farmer_satisfaction_distribution: Dict[str, int] = Field(default_factory=dict, description="Satisfaction score distribution")
    
    # Performance trends
    validation_trend: str = Field(default="stable", description="Validation performance trend")
    expert_review_trend: str = Field(default="stable", description="Expert review performance trend")
    farmer_satisfaction_trend: str = Field(default="stable", description="Farmer satisfaction trend")
    
    # Issues and concerns
    common_validation_issues: List[Dict[str, Any]] = Field(default_factory=list, description="Most common validation issues")
    expert_concerns: List[Dict[str, Any]] = Field(default_factory=list, description="Common expert concerns")
    farmer_complaints: List[Dict[str, Any]] = Field(default_factory=list, description="Common farmer complaints")
    
    # Recommendations
    improvement_recommendations: List[str] = Field(default_factory=list, description="System improvement recommendations")
    
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class ValidationMetricsService:
    """
    Validation metrics and reporting service.
    
    This service provides:
    - Comprehensive metrics tracking
    - Performance reporting and analytics
    - Trend analysis and forecasting
    - Quality assurance monitoring
    - Improvement recommendations
    """

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.db_manager = RecommendationManagementDB(db_session)
        
        # Performance thresholds
        self.performance_thresholds = {
            "validation_success_rate": 0.95,
            "expert_review_completion_rate": 0.90,
            "average_farmer_satisfaction": 0.85,
            "average_validation_score": 0.80,
            "average_expert_score": 0.85
        }
        
        # Trend analysis parameters
        self.trend_analysis_periods = {
            MetricsPeriod.DAILY: 7,  # 7 days for daily trend
            MetricsPeriod.WEEKLY: 4,  # 4 weeks for weekly trend
            MetricsPeriod.MONTHLY: 3,  # 3 months for monthly trend
            MetricsPeriod.QUARTERLY: 4,  # 4 quarters for quarterly trend
            MetricsPeriod.YEARLY: 2  # 2 years for yearly trend
        }

    async def generate_metrics_report(
        self,
        period_start: datetime,
        period_end: datetime,
        period_type: MetricsPeriod = MetricsPeriod.MONTHLY
    ) -> ValidationMetricsReport:
        """Generate comprehensive validation metrics report."""
        try:
            logger.info(f"Generating validation metrics report for period {period_start} to {period_end}")
            
            # Initialize report
            report = ValidationMetricsReport(
                period_start=period_start,
                period_end=period_end,
                period_type=period_type
            )
            
            # Gather validation metrics
            await self._gather_validation_metrics(report)
            
            # Gather expert review metrics
            await self._gather_expert_review_metrics(report)
            
            # Gather quality metrics
            await self._gather_quality_metrics(report)
            
            # Gather regional and crop coverage
            await self._gather_coverage_metrics(report)
            
            # Gather farmer satisfaction metrics
            await self._gather_farmer_satisfaction_metrics(report)
            
            # Analyze trends
            await self._analyze_trends(report)
            
            # Identify issues and concerns
            await self._identify_issues_and_concerns(report)
            
            # Generate improvement recommendations
            await self._generate_improvement_recommendations(report)
            
            # Store report
            await self.db_manager.store_metrics_report(report)
            
            logger.info(f"Generated validation metrics report: {report.report_id}")
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate metrics report: {e}")
            raise

    async def _gather_validation_metrics(self, report: ValidationMetricsReport) -> None:
        """Gather validation performance metrics."""
        try:
            # Get validation results for period
            validations = await self.db_manager.get_validation_results(
                start_date=report.period_start,
                end_date=report.period_end
            )
            
            if not validations:
                return
            
            report.total_validations = len(validations)
            report.successful_validations = len([v for v in validations if v.status == ValidationStatus.COMPLETED])
            report.failed_validations = len([v for v in validations if v.status == ValidationStatus.FAILED])
            
            if report.total_validations > 0:
                report.validation_success_rate = report.successful_validations / report.total_validations
            
            # Calculate average scores
            completed_validations = [v for v in validations if v.status == ValidationStatus.COMPLETED]
            if completed_validations:
                report.average_validation_score = sum(v.overall_score for v in completed_validations) / len(completed_validations)
                report.average_validation_duration_ms = sum(v.validation_duration_ms for v in completed_validations) / len(completed_validations)
            
        except Exception as e:
            logger.error(f"Failed to gather validation metrics: {e}")

    async def _gather_expert_review_metrics(self, report: ValidationMetricsReport) -> None:
        """Gather expert review performance metrics."""
        try:
            # Get expert reviews for period
            expert_reviews = await self.db_manager.get_expert_reviews(
                start_date=report.period_start,
                end_date=report.period_end
            )
            
            if not expert_reviews:
                return
            
            report.expert_reviews_required = len(expert_reviews)
            report.expert_reviews_completed = len([r for r in expert_reviews if r.status == ExpertReviewStatus.APPROVED])
            report.expert_reviews_pending = len([r for r in expert_reviews if r.status == ExpertReviewStatus.PENDING])
            report.expert_reviews_overdue = len([r for r in expert_reviews if r.status == ExpertReviewStatus.NEEDS_REVISION])
            
            if report.expert_reviews_required > 0:
                report.expert_review_completion_rate = report.expert_reviews_completed / report.expert_reviews_required
            
            # Calculate average expert score
            completed_reviews = [r for r in expert_reviews if r.status == ExpertReviewStatus.APPROVED]
            if completed_reviews:
                report.average_expert_score = sum(r.review_score for r in completed_reviews) / len(completed_reviews)
                
                # Calculate average review duration
                review_durations = []
                for review in completed_reviews:
                    # Get assignment to calculate duration
                    assignment = await self.db_manager.get_review_assignment_by_validation_id(review.validation_id)
                    if assignment and assignment.assigned_at and review.updated_at:
                        duration_hours = (review.updated_at - assignment.assigned_at).total_seconds() / 3600
                        review_durations.append(duration_hours)
                
                if review_durations:
                    report.average_expert_review_duration_hours = sum(review_durations) / len(review_durations)
            
        except Exception as e:
            logger.error(f"Failed to gather expert review metrics: {e}")

    async def _gather_quality_metrics(self, report: ValidationMetricsReport) -> None:
        """Gather quality assessment metrics."""
        try:
            # Get expert reviews for quality metrics
            expert_reviews = await self.db_manager.get_expert_reviews(
                start_date=report.period_start,
                end_date=report.period_end,
                status_filter=[ExpertReviewStatus.APPROVED]
            )
            
            if not expert_reviews:
                return
            
            # Calculate average quality scores
            report.agricultural_soundness_score = sum(r.agricultural_soundness for r in expert_reviews) / len(expert_reviews)
            report.regional_applicability_score = sum(r.regional_applicability for r in expert_reviews) / len(expert_reviews)
            report.economic_feasibility_score = sum(r.economic_feasibility for r in expert_reviews) / len(expert_reviews)
            report.farmer_practicality_score = sum(r.farmer_practicality for r in expert_reviews) / len(expert_reviews)
            
        except Exception as e:
            logger.error(f"Failed to gather quality metrics: {e}")

    async def _gather_coverage_metrics(self, report: ValidationMetricsReport) -> None:
        """Gather regional and crop coverage metrics."""
        try:
            # Get validation results for coverage analysis
            validations = await self.db_manager.get_validation_results(
                start_date=report.period_start,
                end_date=report.period_end
            )
            
            if not validations:
                return
            
            # Count by region and crop
            regional_counts = {}
            crop_counts = {}
            
            for validation in validations:
                # Extract region from regional context
                region = validation.regional_context.get("region", "unknown")
                regional_counts[region] = regional_counts.get(region, 0) + 1
                
                # Extract crop from crop context
                crop_type = validation.crop_context.get("crop_type", "unknown")
                crop_counts[crop_type] = crop_counts.get(crop_type, 0) + 1
            
            report.regional_coverage = regional_counts
            report.crop_coverage = crop_counts
            
        except Exception as e:
            logger.error(f"Failed to gather coverage metrics: {e}")

    async def _gather_farmer_satisfaction_metrics(self, report: ValidationMetricsReport) -> None:
        """Gather farmer satisfaction metrics."""
        try:
            # Get farmer feedback for period
            farmer_feedback = await self.db_manager.get_farmer_feedback(
                start_date=report.period_start,
                end_date=report.period_end
            )
            
            if not farmer_feedback:
                return
            
            report.farmer_feedback_count = len(farmer_feedback)
            
            # Calculate average satisfaction
            satisfaction_scores = [f.satisfaction_score for f in farmer_feedback]
            report.average_farmer_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores)
            
            # Calculate satisfaction distribution
            distribution = {"excellent": 0, "good": 0, "fair": 0, "poor": 0}
            for score in satisfaction_scores:
                if score >= 0.9:
                    distribution["excellent"] += 1
                elif score >= 0.7:
                    distribution["good"] += 1
                elif score >= 0.5:
                    distribution["fair"] += 1
                else:
                    distribution["poor"] += 1
            
            report.farmer_satisfaction_distribution = distribution
            
        except Exception as e:
            logger.error(f"Failed to gather farmer satisfaction metrics: {e}")

    async def _analyze_trends(self, report: ValidationMetricsReport) -> None:
        """Analyze performance trends."""
        try:
            # Get historical data for trend analysis
            historical_periods = self.trend_analysis_periods[report.period_type]
            historical_start = report.period_start - timedelta(days=historical_periods * 30)  # Approximate
            
            # Get historical validation metrics
            historical_validations = await self.db_manager.get_validation_results(
                start_date=historical_start,
                end_date=report.period_start
            )
            
            if historical_validations:
                historical_success_rate = len([v for v in historical_validations if v.status == ValidationStatus.COMPLETED]) / len(historical_validations)
                report.validation_trend = self._calculate_trend(report.validation_success_rate, historical_success_rate)
            
            # Get historical expert review metrics
            historical_reviews = await self.db_manager.get_expert_reviews(
                start_date=historical_start,
                end_date=report.period_start,
                status_filter=[ExpertReviewStatus.APPROVED]
            )
            
            if historical_reviews:
                historical_completion_rate = len(historical_reviews) / max(len(historical_reviews), 1)
                report.expert_review_trend = self._calculate_trend(report.expert_review_completion_rate, historical_completion_rate)
            
            # Get historical farmer satisfaction
            historical_feedback = await self.db_manager.get_farmer_feedback(
                start_date=historical_start,
                end_date=report.period_start
            )
            
            if historical_feedback:
                historical_satisfaction = sum(f.satisfaction_score for f in historical_feedback) / len(historical_feedback)
                report.farmer_satisfaction_trend = self._calculate_trend(report.average_farmer_satisfaction, historical_satisfaction)
            
        except Exception as e:
            logger.error(f"Failed to analyze trends: {e}")

    def _calculate_trend(self, current_value: float, historical_value: float) -> str:
        """Calculate trend direction."""
        if current_value > historical_value * 1.05:  # 5% improvement
            return "improving"
        elif current_value < historical_value * 0.95:  # 5% decline
            return "declining"
        else:
            return "stable"

    async def _identify_issues_and_concerns(self, report: ValidationMetricsReport) -> None:
        """Identify common issues and concerns."""
        try:
            # Get validation issues for period
            validations = await self.db_manager.get_validation_results(
                start_date=report.period_start,
                end_date=report.period_end
            )
            
            # Count common validation issues
            issue_counts = {}
            for validation in validations:
                for issue in validation.issues:
                    category = issue.category
                    issue_counts[category] = issue_counts.get(category, 0) + 1
            
            # Get top issues
            sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
            report.common_validation_issues = [
                {"category": category, "count": count, "percentage": count / report.total_validations * 100}
                for category, count in sorted_issues[:10]
            ]
            
            # Get expert concerns
            expert_reviews = await self.db_manager.get_expert_reviews(
                start_date=report.period_start,
                end_date=report.period_end
            )
            
            concern_counts = {}
            for review in expert_reviews:
                for concern in review.concerns:
                    concern_counts[concern] = concern_counts.get(concern, 0) + 1
            
            sorted_concerns = sorted(concern_counts.items(), key=lambda x: x[1], reverse=True)
            report.expert_concerns = [
                {"concern": concern, "count": count}
                for concern, count in sorted_concerns[:10]
            ]
            
            # Get farmer complaints
            farmer_feedback = await self.db_manager.get_farmer_feedback(
                start_date=report.period_start,
                end_date=report.period_end
            )
            
            complaint_counts = {}
            for feedback in farmer_feedback:
                if feedback.satisfaction_score < 0.5 and feedback.feedback:
                    # Simple keyword extraction for complaints
                    words = feedback.feedback.lower().split()
                    for word in words:
                        if word in ["problem", "issue", "wrong", "bad", "poor", "terrible"]:
                            complaint_counts[word] = complaint_counts.get(word, 0) + 1
            
            sorted_complaints = sorted(complaint_counts.items(), key=lambda x: x[1], reverse=True)
            report.farmer_complaints = [
                {"keyword": keyword, "count": count}
                for keyword, count in sorted_complaints[:10]
            ]
            
        except Exception as e:
            logger.error(f"Failed to identify issues and concerns: {e}")

    async def _generate_improvement_recommendations(self, report: ValidationMetricsReport) -> None:
        """Generate improvement recommendations based on metrics."""
        recommendations = []
        
        # Validation performance recommendations
        if report.validation_success_rate < self.performance_thresholds["validation_success_rate"]:
            recommendations.append("Improve validation algorithm accuracy and error handling")
        
        if report.average_validation_score < self.performance_thresholds["average_validation_score"]:
            recommendations.append("Enhance validation criteria and scoring algorithms")
        
        # Expert review recommendations
        if report.expert_review_completion_rate < self.performance_thresholds["expert_review_completion_rate"]:
            recommendations.append("Optimize expert reviewer assignment and workload management")
        
        if report.average_expert_review_duration_hours > 168:  # More than 1 week
            recommendations.append("Streamline expert review process and reduce review complexity")
        
        # Quality recommendations
        if report.agricultural_soundness_score < 0.8:
            recommendations.append("Strengthen agricultural validation criteria and expert knowledge base")
        
        if report.regional_applicability_score < 0.7:
            recommendations.append("Improve regional data integration and validation")
        
        # Farmer satisfaction recommendations
        if report.average_farmer_satisfaction < self.performance_thresholds["average_farmer_satisfaction"]:
            recommendations.append("Enhance recommendation quality and farmer communication")
        
        # Coverage recommendations
        if len(report.regional_coverage) < 5:
            recommendations.append("Expand regional coverage and validation capabilities")
        
        if len(report.crop_coverage) < 10:
            recommendations.append("Increase crop variety coverage and validation")
        
        # Trend-based recommendations
        if report.validation_trend == "declining":
            recommendations.append("Investigate and address declining validation performance")
        
        if report.expert_review_trend == "declining":
            recommendations.append("Address expert reviewer workload and satisfaction issues")
        
        if report.farmer_satisfaction_trend == "declining":
            recommendations.append("Implement farmer feedback improvements and quality enhancements")
        
        report.improvement_recommendations = recommendations

    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time validation metrics."""
        try:
            # Get metrics for last 24 hours
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=24)
            
            # Quick metrics calculation
            validations = await self.db_manager.get_validation_results(start_time, end_time)
            expert_reviews = await self.db_manager.get_expert_reviews(start_time, end_time)
            farmer_feedback = await self.db_manager.get_farmer_feedback(start_time, end_time)
            
            return {
                "timestamp": end_time,
                "validations_last_24h": len(validations),
                "expert_reviews_last_24h": len(expert_reviews),
                "farmer_feedback_last_24h": len(farmer_feedback),
                "system_status": "operational" if len(validations) > 0 else "idle",
                "average_validation_score": sum(v.overall_score for v in validations) / len(validations) if validations else 0.0,
                "pending_expert_reviews": len([r for r in expert_reviews if r.status == ExpertReviewStatus.PENDING])
            }
            
        except Exception as e:
            logger.error(f"Failed to get real-time metrics: {e}")
            return {}

    async def get_performance_alerts(self) -> List[Dict[str, Any]]:
        """Get performance alerts based on thresholds."""
        alerts = []
        
        try:
            # Get recent metrics
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=7)
            
            report = await self.generate_metrics_report(start_time, end_time, MetricsPeriod.WEEKLY)
            
            # Check thresholds
            if report.validation_success_rate < self.performance_thresholds["validation_success_rate"]:
                alerts.append({
                    "type": "validation_performance",
                    "severity": "warning",
                    "message": f"Validation success rate ({report.validation_success_rate:.2%}) below threshold ({self.performance_thresholds['validation_success_rate']:.2%})",
                    "recommendation": "Review validation algorithms and error handling"
                })
            
            if report.expert_review_completion_rate < self.performance_thresholds["expert_review_completion_rate"]:
                alerts.append({
                    "type": "expert_review_performance",
                    "severity": "warning",
                    "message": f"Expert review completion rate ({report.expert_review_completion_rate:.2%}) below threshold ({self.performance_thresholds['expert_review_completion_rate']:.2%})",
                    "recommendation": "Optimize expert reviewer assignment and workload"
                })
            
            if report.average_farmer_satisfaction < self.performance_thresholds["average_farmer_satisfaction"]:
                alerts.append({
                    "type": "farmer_satisfaction",
                    "severity": "critical",
                    "message": f"Farmer satisfaction ({report.average_farmer_satisfaction:.2%}) below threshold ({self.performance_thresholds['average_farmer_satisfaction']:.2%})",
                    "recommendation": "Immediate action required to improve recommendation quality"
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to get performance alerts: {e}")
            return []
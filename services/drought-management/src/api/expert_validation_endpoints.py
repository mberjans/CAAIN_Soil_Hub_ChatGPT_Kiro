"""
API Endpoints for Expert Validation System

This module provides REST API endpoints for the agricultural expert validation
and field testing system for drought management recommendations.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Query, Path, Body
from fastapi.responses import JSONResponse

from ..services.expert_validation_service import ExpertValidationService
from ..models.expert_validation_models import (
    ValidationRequest, ExpertReview, FieldTestResult, ValidationMetrics,
    ExpertAssignmentRequest, FieldTestRequest, FieldTestUpdateRequest,
    FieldTestCompletionRequest, ValidationReport, ExpertPanelStatus,
    ValidationStatusResponse, ExpertReviewSubmission, FieldTestMonitoringData,
    ValidationMetricsResponse, ValidationCriteria, ExpertType
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/expert-validation", tags=["expert-validation"])

# Dependency injection
async def get_expert_validation_service() -> ExpertValidationService:
    """Get expert validation service instance."""
    return ExpertValidationService()


@router.post("/submit-validation", response_model=Dict[str, Any])
async def submit_for_validation(
    recommendation_id: UUID = Body(..., description="Recommendation ID to validate"),
    farm_location: Dict[str, Any] = Body(..., description="Farm location data"),
    field_conditions: Dict[str, Any] = Body(..., description="Field condition data"),
    drought_assessment: Dict[str, Any] = Body(..., description="Drought assessment results"),
    conservation_recommendations: List[Dict[str, Any]] = Body(..., description="Conservation recommendations"),
    water_savings_estimates: List[Dict[str, Any]] = Body(..., description="Water savings estimates"),
    priority_level: str = Body(default="normal", description="Priority level (low, normal, high, critical)"),
    service: ExpertValidationService = Depends(get_expert_validation_service)
):
    """
    Submit drought management recommendations for expert validation.
    
    This endpoint submits recommendations to the expert validation system for
    agricultural expert review and field testing.
    
    **Agricultural Use Cases:**
    - Validate drought management recommendations against expert knowledge
    - Ensure recommendations are regionally appropriate and economically feasible
    - Verify safety and effectiveness of conservation practices
    - Coordinate field testing with real farms for validation
    """
    try:
        # Convert dict data to proper model objects
        from ..models.drought_models import DroughtAssessmentResponse, ConservationRecommendation, WaterSavingsEstimate
        
        drought_assessment_obj = DroughtAssessmentResponse(**drought_assessment)
        conservation_recs = [ConservationRecommendation(**rec) for rec in conservation_recommendations]
        water_savings = [WaterSavingsEstimate(**est) for est in water_savings_estimates]
        
        validation_request = await service.submit_for_validation(
            recommendation_id=recommendation_id,
            farm_location=farm_location,
            field_conditions=field_conditions,
            drought_assessment=drought_assessment_obj,
            conservation_recommendations=conservation_recs,
            water_savings_estimates=water_savings,
            priority_level=priority_level
        )
        
        return {
            "validation_id": str(validation_request.validation_id),
            "status": "submitted",
            "message": "Validation request submitted successfully",
            "deadline": validation_request.deadline.isoformat(),
            "assigned_experts": len(validation_request.requested_expert_types),
            "validation_criteria": [criteria.value for criteria in validation_request.validation_criteria]
        }
        
    except Exception as e:
        logger.error(f"Failed to submit validation request: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit validation request: {str(e)}")


@router.post("/submit-expert-review", response_model=Dict[str, Any])
async def submit_expert_review(
    review_data: ExpertReviewSubmission = Body(..., description="Expert review data"),
    service: ExpertValidationService = Depends(get_expert_validation_service)
):
    """
    Submit expert review for validation request.
    
    This endpoint allows agricultural experts to submit their reviews of
    drought management recommendations.
    
    **Expert Review Process:**
    - Experts evaluate recommendations against multiple criteria
    - Provide detailed comments and recommendations
    - Score effectiveness and safety of practices
    - Approve or reject recommendations based on expert knowledge
    """
    try:
        expert_review = await service.submit_expert_review(
            validation_id=review_data.validation_id,
            expert_id=review_data.expert_id,
            criteria_scores=review_data.criteria_scores,
            overall_score=review_data.overall_score,
            comments=review_data.comments,
            recommendations=review_data.recommendations,
            concerns=review_data.concerns,
            approval_status=review_data.approval_status,
            review_time_hours=review_data.review_time_hours
        )
        
        return {
            "review_id": str(expert_review.review_id),
            "status": "submitted",
            "message": "Expert review submitted successfully",
            "approval_status": expert_review.approval_status,
            "overall_score": expert_review.overall_score,
            "submitted_at": expert_review.submitted_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to submit expert review: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit expert review: {str(e)}")


@router.get("/validation-status/{validation_id}", response_model=ValidationStatusResponse)
async def get_validation_status(
    validation_id: UUID = Path(..., description="Validation request ID"),
    service: ExpertValidationService = Depends(get_expert_validation_service)
):
    """
    Get validation status and progress.
    
    This endpoint provides real-time status of validation requests,
    including progress tracking and expert review status.
    """
    try:
        status_data = await service.get_validation_status(validation_id)
        
        return ValidationStatusResponse(
            validation_id=validation_id,
            status=status_data['status'],
            progress_percentage=status_data['progress_percentage'],
            expert_reviews=status_data['expert_reviews'],
            total_experts_assigned=status_data['total_experts_assigned'],
            deadline=status_data['deadline'],
            overall_approval=status_data['overall_approval']
        )
        
    except Exception as e:
        logger.error(f"Failed to get validation status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get validation status: {str(e)}")


@router.post("/start-field-test", response_model=Dict[str, Any])
async def start_field_test(
    test_request: FieldTestRequest = Body(..., description="Field test request data"),
    service: ExpertValidationService = Depends(get_expert_validation_service)
):
    """
    Start field test for drought management practice.
    
    This endpoint initiates field testing of drought management practices
    with real farms for validation and outcome tracking.
    
    **Field Testing Process:**
    - Establish baseline conditions before practice implementation
    - Monitor practice effectiveness over time
    - Collect farmer feedback and expert observations
    - Track water savings and crop response metrics
    """
    try:
        field_test = await service.start_field_test(
            farm_id=test_request.farm_id,
            field_id=test_request.field_id,
            practice_implemented=test_request.practice_implemented,
            baseline_conditions=test_request.baseline_conditions,
            test_duration_days=test_request.test_duration_days
        )
        
        return {
            "test_id": str(field_test.test_id),
            "status": "started",
            "message": "Field test started successfully",
            "implementation_date": field_test.implementation_date.isoformat(),
            "expected_completion": field_test.completed_at.isoformat(),
            "test_duration_days": field_test.test_duration_days
        }
        
    except Exception as e:
        logger.error(f"Failed to start field test: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start field test: {str(e)}")


@router.put("/update-field-test-monitoring", response_model=Dict[str, Any])
async def update_field_test_monitoring(
    test_id: UUID = Body(..., description="Field test ID"),
    monitoring_data: Dict[str, Any] = Body(..., description="Monitoring data"),
    expert_observations: List[str] = Body(default_factory=list, description="Expert observations"),
    service: ExpertValidationService = Depends(get_expert_validation_service)
):
    """
    Update field test monitoring data.
    
    This endpoint allows updating monitoring data during field tests,
    including soil moisture, crop health, and expert observations.
    """
    try:
        await service.update_field_test_monitoring(
            test_id=test_id,
            monitoring_data=monitoring_data,
            expert_observations=expert_observations
        )
        
        return {
            "test_id": str(test_id),
            "status": "updated",
            "message": "Field test monitoring data updated successfully",
            "updated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to update field test monitoring: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update field test monitoring: {str(e)}")


@router.put("/complete-field-test", response_model=Dict[str, Any])
async def complete_field_test(
    completion_data: FieldTestCompletionRequest = Body(..., description="Field test completion data"),
    service: ExpertValidationService = Depends(get_expert_validation_service)
):
    """
    Complete field test with final results.
    
    This endpoint completes field tests with final outcome metrics,
    farmer feedback, and effectiveness scores.
    """
    try:
        await service.complete_field_test(
            test_id=completion_data.test_id,
            outcome_metrics=completion_data.outcome_metrics,
            farmer_feedback=completion_data.farmer_feedback,
            effectiveness_score=completion_data.effectiveness_score,
            farmer_satisfaction_score=completion_data.farmer_satisfaction_score
        )
        
        return {
            "test_id": str(completion_data.test_id),
            "status": "completed",
            "message": "Field test completed successfully",
            "effectiveness_score": completion_data.effectiveness_score,
            "farmer_satisfaction_score": completion_data.farmer_satisfaction_score,
            "completed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to complete field test: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to complete field test: {str(e)}")


@router.get("/validation-metrics", response_model=ValidationMetricsResponse)
async def get_validation_metrics(
    period_days: int = Query(default=30, ge=1, le=365, description="Metrics period in days"),
    service: ExpertValidationService = Depends(get_expert_validation_service)
):
    """
    Get validation system performance metrics.
    
    This endpoint provides comprehensive metrics on validation system performance,
    including expert approval rates, farmer satisfaction, and field test success rates.
    
    **Key Metrics:**
    - Expert approval rate (target: >95%)
    - Recommendation accuracy (target: >90%)
    - Farmer satisfaction (target: >85%)
    - Field test success rate
    - Average review time
    """
    try:
        metrics = await service.get_validation_metrics()
        
        # Calculate trend analysis
        trend_analysis = {
            "expert_approval_trend": "stable",  # Would calculate from historical data
            "farmer_satisfaction_trend": "improving",
            "review_time_trend": "decreasing"
        }
        
        # Performance targets
        performance_targets = {
            "expert_approval_rate": 0.95,
            "recommendation_accuracy": 0.90,
            "farmer_satisfaction": 0.85,
            "average_review_time_hours": 48.0,
            "field_test_success_rate": 0.80
        }
        
        return ValidationMetricsResponse(
            metrics=metrics,
            period_start=datetime.utcnow() - timedelta(days=period_days),
            period_end=datetime.utcnow(),
            trend_analysis=trend_analysis,
            performance_targets=performance_targets
        )
        
    except Exception as e:
        logger.error(f"Failed to get validation metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get validation metrics: {str(e)}")


@router.get("/expert-panel-status", response_model=ExpertPanelStatus)
async def get_expert_panel_status(
    service: ExpertValidationService = Depends(get_expert_validation_service)
):
    """
    Get expert panel status and availability.
    
    This endpoint provides information about the expert panel,
    including availability, expertise distribution, and performance metrics.
    """
    try:
        panel_status = await service.get_expert_panel_status()
        
        return ExpertPanelStatus(
            total_experts=panel_status['total_experts'],
            available_experts=panel_status['available_experts'],
            assigned_experts=panel_status['assigned_experts'],
            expert_types_distribution=panel_status['expert_types_distribution'],
            average_approval_rate=panel_status['average_approval_rate'],
            average_experience_years=panel_status['average_experience_years']
        )
        
    except Exception as e:
        logger.error(f"Failed to get expert panel status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get expert panel status: {str(e)}")


@router.get("/validation-report/{validation_id}", response_model=ValidationReport)
async def generate_validation_report(
    validation_id: UUID = Path(..., description="Validation request ID"),
    service: ExpertValidationService = Depends(get_expert_validation_service)
):
    """
    Generate comprehensive validation report.
    
    This endpoint generates detailed validation reports including
    expert reviews, overall assessment, and recommendations.
    """
    try:
        report_data = await service.generate_validation_report(validation_id)
        
        return ValidationReport(
            validation_id=validation_id,
            recommendation_id=report_data['validation_summary']['recommendation_id'],
            validation_summary=report_data['validation_summary'],
            expert_reviews=report_data['expert_reviews'],
            overall_assessment=report_data['overall_assessment'],
            recommendations=report_data['recommendations'],
            water_savings_estimates=report_data['water_savings_estimates']
        )
        
    except Exception as e:
        logger.error(f"Failed to generate validation report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate validation report: {str(e)}")


@router.get("/field-tests/active", response_model=List[Dict[str, Any]])
async def get_active_field_tests(
    farm_id: Optional[UUID] = Query(None, description="Filter by farm ID"),
    service: ExpertValidationService = Depends(get_expert_validation_service)
):
    """
    Get active field tests.
    
    This endpoint retrieves all active field tests, optionally filtered by farm ID.
    """
    try:
        # This would be implemented in the service
        active_tests = []
        for test_id, field_test in service.field_tests.items():
            if farm_id is None or field_test.farm_id == farm_id:
                test_data = {
                    "test_id": str(field_test.test_id),
                    "farm_id": str(field_test.farm_id),
                    "field_id": str(field_test.field_id),
                    "practice_implemented": field_test.practice_implemented,
                    "implementation_date": field_test.implementation_date.isoformat(),
                    "test_duration_days": field_test.test_duration_days,
                    "expected_completion": field_test.completed_at.isoformat()
                }
                active_tests.append(test_data)
        
        return active_tests
        
    except Exception as e:
        logger.error(f"Failed to get active field tests: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get active field tests: {str(e)}")


@router.get("/validation-criteria", response_model=List[Dict[str, str]])
async def get_validation_criteria():
    """
    Get available validation criteria.
    
    This endpoint returns all available validation criteria for drought management recommendations.
    """
    criteria = [
        {
            "criteria": criteria.value,
            "description": _get_criteria_description(criteria)
        }
        for criteria in ValidationCriteria
    ]
    return criteria


@router.get("/expert-types", response_model=List[Dict[str, str]])
async def get_expert_types():
    """
    Get available expert types.
    
    This endpoint returns all available expert types in the validation system.
    """
    expert_types = [
        {
            "expert_type": expert_type.value,
            "description": _get_expert_type_description(expert_type)
        }
        for expert_type in ExpertType
    ]
    return expert_types


@router.get("/health")
async def health_check():
    """Health check endpoint for expert validation service."""
    return {
        "status": "healthy",
        "service": "expert-validation",
        "timestamp": datetime.utcnow().isoformat()
    }


def _get_criteria_description(criteria: ValidationCriteria) -> str:
    """Get description for validation criteria."""
    descriptions = {
        ValidationCriteria.AGRICULTURAL_SOUNDNESS: "Validates recommendations against agricultural science and best practices",
        ValidationCriteria.REGIONAL_APPLICABILITY: "Ensures recommendations are appropriate for the specific region and climate",
        ValidationCriteria.ECONOMIC_FEASIBILITY: "Evaluates cost-effectiveness and economic viability of recommendations",
        ValidationCriteria.ENVIRONMENTAL_IMPACT: "Assesses environmental benefits and potential negative impacts",
        ValidationCriteria.PRACTICALITY: "Evaluates ease of implementation and practical considerations",
        ValidationCriteria.SAFETY: "Ensures recommendations are safe for crops, soil, and environment",
        ValidationCriteria.EFFECTIVENESS: "Validates expected effectiveness and water savings potential"
    }
    return descriptions.get(criteria, "Validation criteria")


def _get_expert_type_description(expert_type: ExpertType) -> str:
    """Get description for expert type."""
    descriptions = {
        ExpertType.DROUGHT_SPECIALIST: "Expert in drought management and water conservation practices",
        ExpertType.EXTENSION_AGENT: "University extension agent with regional agricultural expertise",
        ExpertType.CONSERVATION_PROFESSIONAL: "Professional specializing in conservation practices and soil health",
        ExpertType.IRRIGATION_SPECIALIST: "Expert in irrigation systems and water management",
        ExpertType.SOIL_SCIENTIST: "Scientist specializing in soil properties and management",
        ExpertType.CROP_SPECIALIST: "Expert in specific crop types and their management requirements"
    }
    return descriptions.get(expert_type, "Agricultural expert")
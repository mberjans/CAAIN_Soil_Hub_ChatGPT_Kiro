"""
API Routes for Agricultural Expert Validation and Field Testing.
Implements TICKET-023_fertilizer-application-method-11.2 endpoints.
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel, Field

from src.services.expert_validation_service import (
    ExpertValidationService, ExpertType, ValidationStatus, FieldTestStatus,
    ExpertProfile, ValidationRequest, ExpertReview, FieldTestPlan, FieldTestResult
)
from src.models.application_models import (
    ApplicationRequest, ApplicationResponse, ApplicationMethod,
    FieldConditions, CropRequirements, FertilizerSpecification,
    ApplicationMethodType, FertilizerForm, EquipmentType, EquipmentSpecification
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/expert-validation", tags=["expert-validation"])

# Global service instance
expert_validation_service: ExpertValidationService = None


async def get_expert_validation_service() -> ExpertValidationService:
    """Dependency to get expert validation service instance."""
    global expert_validation_service
    if expert_validation_service is None:
        expert_validation_service = ExpertValidationService()
    return expert_validation_service


# Request/Response Models
class ValidationSubmissionRequest(BaseModel):
    """Request model for submitting recommendations for expert validation."""
    application_request: ApplicationRequest
    application_response: ApplicationResponse
    validation_type: str = Field(default="method_recommendation", description="Type of validation needed")
    priority: str = Field(default="normal", description="Priority level (low, normal, high, urgent)")


class ValidationSubmissionResponse(BaseModel):
    """Response model for validation submission."""
    validation_request_id: str
    status: str
    assigned_experts: List[str]
    deadline: datetime
    message: str


class ExpertReviewSubmissionRequest(BaseModel):
    """Request model for submitting expert review."""
    validation_request_id: str
    expert_id: str
    recommendation_score: float = Field(ge=0, le=10, description="Score for recommendation quality (0-10)")
    accuracy_score: float = Field(ge=0, le=10, description="Score for accuracy (0-10)")
    feasibility_score: float = Field(ge=0, le=10, description="Score for feasibility (0-10)")
    safety_score: float = Field(ge=0, le=10, description="Score for safety (0-10)")
    cost_effectiveness_score: float = Field(ge=0, le=10, description="Score for cost effectiveness (0-10)")
    overall_approval: bool = Field(description="Whether expert approves the recommendation")
    comments: str = Field(description="General comments")
    suggestions: List[str] = Field(default=[], description="List of improvement suggestions")
    concerns: List[str] = Field(default=[], description="List of concerns")
    alternative_recommendations: List[Dict[str, Any]] = Field(default=[], description="Alternative recommendations")
    confidence_level: float = Field(default=0.8, ge=0, le=1, description="Expert's confidence in the review (0-1)")


class ExpertReviewSubmissionResponse(BaseModel):
    """Response model for expert review submission."""
    review_id: str
    status: str
    message: str


class FieldTestPlanRequest(BaseModel):
    """Request model for creating field test plan."""
    validation_request_id: str
    farm_id: str
    field_id: str
    test_design: Dict[str, Any]
    implementation_plan: Dict[str, Any]
    data_collection_plan: Dict[str, Any]
    success_criteria: Dict[str, Any]
    timeline: Dict[str, str]  # Will be converted to datetime
    budget: float


class FieldTestPlanResponse(BaseModel):
    """Response model for field test plan creation."""
    test_id: str
    status: str
    message: str


class FieldTestResultRequest(BaseModel):
    """Request model for submitting field test results."""
    test_id: str
    implementation_success: bool
    yield_impact: float
    cost_savings: float
    farmer_satisfaction: float = Field(ge=0, le=10, description="Farmer satisfaction score (0-10)")
    environmental_impact: Dict[str, Any]
    lessons_learned: List[str]
    recommendations: List[str]
    data_collected: Dict[str, Any]


class FieldTestResultResponse(BaseModel):
    """Response model for field test result submission."""
    result_id: str
    status: str
    message: str


class ExpertProfileRequest(BaseModel):
    """Request model for adding expert to panel."""
    name: str
    expert_type: ExpertType
    credentials: str
    specialization: List[str]
    experience_years: int
    certifications: List[str]
    contact_info: Dict[str, str]
    availability: Dict[str, Any]


class ExpertProfileResponse(BaseModel):
    """Response model for expert profile."""
    expert_id: str
    name: str
    expert_type: str
    credentials: str
    specialization: List[str]
    experience_years: int
    certifications: List[str]
    rating: float
    review_count: int
    availability: Dict[str, Any]


# API Endpoints

@router.post("/submit-validation", response_model=ValidationSubmissionResponse)
async def submit_for_expert_validation(
    request: ValidationSubmissionRequest,
    service: ExpertValidationService = Depends(get_expert_validation_service)
):
    """
    Submit a fertilizer application recommendation for expert validation.
    
    This endpoint allows submission of application recommendations to the expert panel
    for validation against agricultural best practices. The system will automatically
    select appropriate experts based on the validation type and notify them for review.
    
    Agricultural Use Cases:
    - Validate new fertilizer application methods
    - Review equipment compatibility assessments
    - Validate application guidance and safety protocols
    - Review cost-effectiveness analyses
    """
    try:
        validation_request_id = await service.submit_for_expert_validation(
            application_request=request.application_request,
            application_response=request.application_response,
            validation_type=request.validation_type,
            priority=request.priority
        )
        
        validation_request = service.validation_requests[validation_request_id]
        
        return ValidationSubmissionResponse(
            validation_request_id=validation_request_id,
            status=validation_request.status.value,
            assigned_experts=validation_request.assigned_experts,
            deadline=validation_request.deadline,
            message=f"Validation request submitted successfully. Assigned to {len(validation_request.assigned_experts)} experts."
        )
        
    except Exception as e:
        logger.error(f"Error submitting validation request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit-expert-review", response_model=ExpertReviewSubmissionResponse)
async def submit_expert_review(
    request: ExpertReviewSubmissionRequest,
    service: ExpertValidationService = Depends(get_expert_validation_service)
):
    """
    Submit expert review for a validation request.
    
    This endpoint allows agricultural experts to submit their reviews of fertilizer
    application recommendations, including scores for various criteria and overall
    approval status.
    
    Expert Review Criteria:
    - Recommendation Quality: Technical accuracy and appropriateness
    - Accuracy: Alignment with agricultural best practices
    - Feasibility: Practical implementation considerations
    - Safety: Safety protocols and risk assessment
    - Cost Effectiveness: Economic viability and ROI
    """
    try:
        review_id = await service.submit_expert_review(
            validation_request_id=request.validation_request_id,
            expert_id=request.expert_id,
            recommendation_score=request.recommendation_score,
            accuracy_score=request.accuracy_score,
            feasibility_score=request.feasibility_score,
            safety_score=request.safety_score,
            cost_effectiveness_score=request.cost_effectiveness_score,
            overall_approval=request.overall_approval,
            comments=request.comments,
            suggestions=request.suggestions,
            concerns=request.concerns,
            alternative_recommendations=request.alternative_recommendations,
            confidence_level=request.confidence_level
        )
        
        return ExpertReviewSubmissionResponse(
            review_id=review_id,
            status="submitted",
            message="Expert review submitted successfully."
        )
        
    except Exception as e:
        logger.error(f"Error submitting expert review: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/validation-summary/{validation_request_id}")
async def get_validation_summary(
    validation_request_id: str,
    service: ExpertValidationService = Depends(get_expert_validation_service)
):
    """
    Get summary of validation results for a specific request.
    
    This endpoint provides a comprehensive summary of expert validation results,
    including consensus metrics, individual expert reviews, and overall status.
    """
    try:
        summary = await service.get_validation_summary(validation_request_id)
        return summary
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting validation summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-field-test-plan", response_model=FieldTestPlanResponse)
async def create_field_test_plan(
    request: FieldTestPlanRequest,
    service: ExpertValidationService = Depends(get_expert_validation_service)
):
    """
    Create a field test plan for validated recommendations.
    
    This endpoint creates a comprehensive field test plan for recommendations that
    have passed expert validation, including test design, implementation plan,
    data collection strategy, and success criteria.
    
    Field Testing Components:
    - Test Design: Experimental design and control groups
    - Implementation Plan: Step-by-step implementation procedures
    - Data Collection: Metrics and data collection protocols
    - Success Criteria: Measurable success indicators
    - Timeline: Project schedule and milestones
    """
    try:
        # Convert timeline strings to datetime objects
        timeline_datetime = {}
        for key, value in request.timeline.items():
            timeline_datetime[key] = datetime.fromisoformat(value)
        
        test_id = await service.create_field_test_plan(
            validation_request_id=request.validation_request_id,
            farm_id=request.farm_id,
            field_id=request.field_id,
            test_design=request.test_design,
            implementation_plan=request.implementation_plan,
            data_collection_plan=request.data_collection_plan,
            success_criteria=request.success_criteria,
            timeline=timeline_datetime,
            budget=request.budget
        )
        
        field_test_plan = service.field_test_plans[test_id]
        
        return FieldTestPlanResponse(
            test_id=test_id,
            status=field_test_plan.status.value,
            message=f"Field test plan created successfully for farm {request.farm_id}, field {request.field_id}."
        )
        
    except Exception as e:
        logger.error(f"Error creating field test plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit-field-test-result", response_model=FieldTestResultResponse)
async def submit_field_test_result(
    request: FieldTestResultRequest,
    service: ExpertValidationService = Depends(get_expert_validation_service)
):
    """
    Submit results from field testing.
    
    This endpoint allows submission of comprehensive field test results, including
    implementation success, yield impact, cost savings, farmer satisfaction,
    environmental impact, and lessons learned.
    
    Field Test Metrics:
    - Implementation Success: Whether the test was successfully implemented
    - Yield Impact: Measured impact on crop yield
    - Cost Savings: Economic benefits achieved
    - Farmer Satisfaction: Farmer feedback and satisfaction scores
    - Environmental Impact: Environmental benefits and impacts
    - Lessons Learned: Key insights and recommendations
    """
    try:
        result_id = await service.submit_field_test_result(
            test_id=request.test_id,
            implementation_success=request.implementation_success,
            yield_impact=request.yield_impact,
            cost_savings=request.cost_savings,
            farmer_satisfaction=request.farmer_satisfaction,
            environmental_impact=request.environmental_impact,
            lessons_learned=request.lessons_learned,
            recommendations=request.recommendations,
            data_collected=request.data_collected
        )
        
        return FieldTestResultResponse(
            result_id=result_id,
            status="submitted",
            message="Field test results submitted successfully."
        )
        
    except Exception as e:
        logger.error(f"Error submitting field test result: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/validation-metrics")
async def get_validation_metrics(
    start_date: str = Query(description="Start date for metrics (YYYY-MM-DD)"),
    end_date: str = Query(description="End date for metrics (YYYY-MM-DD)"),
    service: ExpertValidationService = Depends(get_expert_validation_service)
):
    """
    Get validation performance metrics for a specified period.
    
    This endpoint provides comprehensive validation performance metrics including
    expert approval rates, farmer satisfaction rates, recommendation accuracy,
    field test success rates, and other key performance indicators.
    
    Performance Targets:
    - Expert Approval Rate: >95%
    - Farmer Satisfaction Rate: >85%
    - Recommendation Accuracy: >90%
    """
    try:
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        
        metrics = await service.calculate_validation_metrics(start_dt, end_dt)
        
        return {
            "validation_period": {
                "start_date": metrics.validation_period[0].isoformat(),
                "end_date": metrics.validation_period[1].isoformat()
            },
            "total_validations": metrics.total_validations,
            "expert_approval_rate": metrics.expert_approval_rate,
            "farmer_satisfaction_rate": metrics.farmer_satisfaction_rate,
            "recommendation_accuracy": metrics.recommendation_accuracy,
            "field_test_success_rate": metrics.field_test_success_rate,
            "average_review_time_hours": metrics.average_review_time / 3600,  # Convert to hours
            "expert_consensus_rate": metrics.expert_consensus_rate,
            "performance_targets": {
                "expert_approval_target": 0.95,
                "farmer_satisfaction_target": 0.85,
                "recommendation_accuracy_target": 0.90
            },
            "targets_met": {
                "expert_approval": metrics.expert_approval_rate >= 0.95,
                "farmer_satisfaction": metrics.farmer_satisfaction_rate >= 0.85,
                "recommendation_accuracy": metrics.recommendation_accuracy >= 0.90
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")
    except Exception as e:
        logger.error(f"Error getting validation metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/expert-panel")
async def get_expert_panel(
    service: ExpertValidationService = Depends(get_expert_validation_service)
):
    """
    Get list of expert panel members.
    
    This endpoint provides information about all members of the agricultural expert
    panel, including their credentials, specializations, experience, and availability.
    """
    try:
        expert_panel = await service.get_expert_panel()
        return {
            "expert_panel": expert_panel,
            "total_experts": len(expert_panel),
            "expert_types": list(set(expert["expert_type"] for expert in expert_panel))
        }
        
    except Exception as e:
        logger.error(f"Error getting expert panel: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add-expert", response_model=ExpertProfileResponse)
async def add_expert_to_panel(
    request: ExpertProfileRequest,
    service: ExpertValidationService = Depends(get_expert_validation_service)
):
    """
    Add a new expert to the validation panel.
    
    This endpoint allows addition of new agricultural experts to the validation panel,
    including their credentials, specializations, and availability.
    """
    try:
        expert_id = await service.add_expert_to_panel(
            name=request.name,
            expert_type=request.expert_type,
            credentials=request.credentials,
            specialization=request.specialization,
            experience_years=request.experience_years,
            certifications=request.certifications,
            contact_info=request.contact_info,
            availability=request.availability
        )
        
        expert = service.expert_database[expert_id]
        
        return ExpertProfileResponse(
            expert_id=expert.expert_id,
            name=expert.name,
            expert_type=expert.expert_type.value,
            credentials=expert.credentials,
            specialization=expert.specialization,
            experience_years=expert.experience_years,
            certifications=expert.certifications,
            rating=expert.rating,
            review_count=expert.review_count,
            availability=expert.availability
        )
        
    except Exception as e:
        logger.error(f"Error adding expert to panel: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/validation-dashboard")
async def get_validation_dashboard(
    service: ExpertValidationService = Depends(get_expert_validation_service)
):
    """
    Get comprehensive validation dashboard data.
    
    This endpoint provides a comprehensive dashboard view of the validation system,
    including recent performance metrics, pending validations, active field tests,
    expert workload, and performance against targets.
    """
    try:
        dashboard_data = await service.get_validation_dashboard()
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Error getting validation dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint for expert validation service."""
    return {
        "status": "healthy",
        "service": "expert-validation",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0"
    }
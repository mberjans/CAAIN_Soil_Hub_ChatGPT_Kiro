"""
API Routes for Knowledge Assessment and Certification System.

This module provides REST API endpoints for knowledge assessment creation,
submission, scoring, and certification management for fertilizer application methods.
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, Union
from uuid import uuid4
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from pydantic import BaseModel, Field

from src.models.educational_models import (
    AssessmentRequest, AssessmentResponse, AssessmentResult,
    CertificationRequest, CertificationResponse, CertificationType,
    AssessmentDifficulty, ContentCategory, UserCertification
)
from src.services.knowledge_assessment_service import KnowledgeAssessmentService
from src.services.certification_service import CertificationService, CertificationStatus

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/knowledge-assessment", tags=["knowledge-assessment"])

# Global service instances
assessment_service: KnowledgeAssessmentService = None
certification_service: CertificationService = None


async def get_assessment_service() -> KnowledgeAssessmentService:
    """Dependency to get knowledge assessment service instance."""
    global assessment_service
    if assessment_service is None:
        assessment_service = KnowledgeAssessmentService()
    return assessment_service


async def get_certification_service() -> CertificationService:
    """Dependency to get certification service instance."""
    global certification_service
    if certification_service is None:
        certification_service = CertificationService()
    return certification_service


@router.post("/create", response_model=AssessmentResponse)
async def create_assessment(
    request: AssessmentRequest,
    service: KnowledgeAssessmentService = Depends(get_assessment_service)
):
    """
    Create a knowledge assessment based on user requirements.

    This endpoint generates a customized assessment based on:
    - Assessment category (application methods, equipment operation, safety, etc.)
    - Difficulty level (basic, intermediate, advanced, expert)
    - Certification type (if targeting specific certification)
    - Time constraints and question count preferences

    Agricultural Use Cases:
    - Pre-certification assessment for fertilizer application specialists
    - Skill evaluation for equipment operators
    - Safety certification preparation
    - Environmental stewardship knowledge testing
    """
    try:
        result = await service.create_assessment(request)
        return result
    except Exception as e:
        logger.error(f"Error creating assessment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit/{attempt_id}", response_model=AssessmentResult)
async def submit_assessment(
    attempt_id: str = Path(..., description="Assessment attempt identifier"),
    answers: Dict[str, Union[str, List[str]]] = Field(..., description="User answers to assessment questions"),
    service: KnowledgeAssessmentService = Depends(get_assessment_service)
):
    """
    Submit assessment answers and receive detailed results.

    This endpoint processes user answers and provides:
    - Detailed scoring with individual question results
    - Personalized feedback on strengths and areas for improvement
    - Learning recommendations based on performance
    - Certification eligibility status (if applicable)

    Agricultural Use Cases:
    - Immediate feedback on fertilizer application knowledge
    - Identification of knowledge gaps for targeted learning
    - Preparation for certification exams
    - Skill assessment for professional development
    """
    try:
        result = await service.submit_assessment(attempt_id, answers)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error submitting assessment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{user_id}", response_model=List[AssessmentResult])
async def get_assessment_history(
    user_id: str = Path(..., description="User identifier"),
    limit: int = Query(10, ge=1, le=50, description="Number of assessments to retrieve"),
    service: KnowledgeAssessmentService = Depends(get_assessment_service)
):
    """
    Get user's assessment history with performance tracking.

    This endpoint provides:
    - Historical assessment results and scores
    - Progress tracking over time
    - Performance trends by category
    - Certification preparation status

    Agricultural Use Cases:
    - Track learning progress over time
    - Monitor skill development in fertilizer application
    - Prepare certification portfolios
    - Identify recurring knowledge gaps
    """
    try:
        results = await service.get_user_assessment_history(user_id, limit)
        return results
    except Exception as e:
        logger.error(f"Error retrieving assessment history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/certification-requirements/{certification_type}")
async def get_certification_requirements(
    certification_type: CertificationType = Path(..., description="Certification type"),
    service: KnowledgeAssessmentService = Depends(get_assessment_service)
):
    """
    Get certification requirements for a specific certification type.

    This endpoint provides detailed information about:
    - Required assessments and minimum scores
    - Practical experience hour requirements
    - Continuing education requirements
    - Validity periods and renewal requirements

    Agricultural Use Cases:
    - Understanding certification prerequisites
    - Planning certification pathway
    - Tracking progress toward certification goals
    - Compliance with professional standards
    """
    try:
        requirements = await service.get_certification_requirements(certification_type)
        return requirements
    except Exception as e:
        logger.error(f"Error retrieving certification requirements: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/certification-eligibility/{user_id}/{certification_type}")
async def check_certification_eligibility(
    user_id: str = Path(..., description="User identifier"),
    certification_type: CertificationType = Path(..., description="Certification type"),
    service: KnowledgeAssessmentService = Depends(get_assessment_service)
):
    """
    Check if user is eligible for a specific certification.

    This endpoint evaluates:
    - Assessment score requirements
    - Practical experience hours
    - Continuing education credits
    - Any missing requirements

    Agricultural Use Cases:
    - Pre-application eligibility check
    - Gap analysis for certification preparation
    - Professional development planning
    - Compliance verification
    """
    try:
        eligibility = await service.check_certification_eligibility(user_id, certification_type)
        return eligibility
    except Exception as e:
        logger.error(f"Error checking certification eligibility: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Certification Management Endpoints

@router.post("/certification/issue", response_model=CertificationResponse)
async def issue_certification(
    request: CertificationRequest,
    service: CertificationService = Depends(get_certification_service)
):
    """
    Issue a certification to a qualified user.

    This endpoint:
    - Validates all certification requirements
    - Generates unique certification ID and verification code
    - Creates certification record with validity period
    - Provides digital certification credentials

    Agricultural Use Cases:
    - Professional certification for fertilizer application specialists
    - Equipment operator certification
    - Safety certification for chemical handling
    - Environmental stewardship certification
    """
    try:
        result = await service.issue_certification(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error issuing certification: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/certification/user/{user_id}", response_model=List[UserCertification])
async def get_user_certifications(
    user_id: str = Path(..., description="User identifier"),
    status: Optional[CertificationStatus] = Query(None, description="Filter by certification status"),
    service: CertificationService = Depends(get_certification_service)
):
    """
    Get user's certifications with optional status filtering.

    This endpoint provides:
    - Complete certification history
    - Current active certifications
    - Expired or revoked certifications
    - Renewal status and requirements

    Agricultural Use Cases:
    - Professional credential verification
    - Certification portfolio management
    - Renewal tracking and planning
    - Compliance documentation
    """
    try:
        certifications = await service.get_user_certifications(user_id, status)
        return certifications
    except Exception as e:
        logger.error(f"Error retrieving user certifications: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/certification/verify/{verification_code}", response_model=UserCertification)
async def verify_certification(
    verification_code: str = Path(..., description="Certification verification code"),
    service: CertificationService = Depends(get_certification_service)
):
    """
    Verify a certification using its verification code.

    This endpoint provides:
    - Certification authenticity verification
    - Current status and validity
    - Issued skills and competencies
    - Expiry date and renewal information

    Agricultural Use Cases:
    - Employer verification of employee certifications
    - Regulatory compliance checking
    - Professional credential validation
    - Audit and inspection support
    """
    try:
        certification = await service.verify_certification(verification_code)
        if not certification:
            raise HTTPException(status_code=404, detail="Certification not found or invalid verification code")
        return certification
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying certification: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/certification/renew/{certification_record_id}")
async def renew_certification(
    certification_record_id: str = Path(..., description="Certification record identifier"),
    renewal_data: Dict[str, Any] = Field(..., description="Renewal data including continuing education hours"),
    service: CertificationService = Depends(get_certification_service)
):
    """
    Renew an existing certification.

    This endpoint:
    - Validates renewal requirements
    - Updates certification validity period
    - Records continuing education credits
    - Issues renewed certification

    Agricultural Use Cases:
    - Maintaining professional certifications
    - Continuing education credit tracking
    - Regulatory compliance maintenance
    - Professional development documentation
    """
    try:
        renewed_certification = await service.renew_certification(certification_record_id, renewal_data)
        return renewed_certification
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error renewing certification: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/certification/revoke/{certification_record_id}")
async def revoke_certification(
    certification_record_id: str = Path(..., description="Certification record identifier"),
    reason: str = Query(..., description="Reason for revocation"),
    service: CertificationService = Depends(get_certification_service)
):
    """
    Revoke a certification.

    This endpoint:
    - Updates certification status to revoked
    - Records revocation reason
    - Maintains audit trail
    - Notifies relevant parties

    Agricultural Use Cases:
    - Disciplinary action for safety violations
    - Compliance enforcement
    - Professional misconduct handling
    - Regulatory requirement enforcement
    """
    try:
        success = await service.revoke_certification(certification_record_id, reason)
        if success:
            return {"message": "Certification revoked successfully", "certification_id": certification_record_id}
        else:
            raise HTTPException(status_code=400, detail="Failed to revoke certification")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error revoking certification: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/certification/expiring")
async def get_expiring_certifications(
    days_ahead: int = Query(30, ge=1, le=365, description="Days ahead to check for expiring certifications"),
    service: CertificationService = Depends(get_certification_service)
):
    """
    Get certifications expiring within specified days.

    This endpoint provides:
    - List of certifications nearing expiry
    - Renewal requirements for each certification
    - Contact information for renewal process
    - Automated renewal reminders

    Agricultural Use Cases:
    - Proactive certification management
    - Renewal reminder systems
    - Compliance monitoring
    - Professional development planning
    """
    try:
        expiring_certifications = await service.get_expiring_certifications(days_ahead)
        return {
            "expiring_certifications": expiring_certifications,
            "days_ahead": days_ahead,
            "count": len(expiring_certifications)
        }
    except Exception as e:
        logger.error(f"Error retrieving expiring certifications: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/certification/statistics")
async def get_certification_statistics(
    certification_type: Optional[CertificationType] = Query(None, description="Filter by certification type"),
    service: CertificationService = Depends(get_certification_service)
):
    """
    Get certification statistics and analytics.

    This endpoint provides:
    - Total certifications issued
    - Active vs expired certifications
    - Certification type distribution
    - Renewal rates and trends

    Agricultural Use Cases:
    - Program effectiveness analysis
    - Industry certification trends
    - Compliance monitoring
    - Professional development insights
    """
    try:
        statistics = await service.get_certification_statistics(certification_type)
        return statistics
    except Exception as e:
        logger.error(f"Error retrieving certification statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint for knowledge assessment service monitoring."""
    return {
        "status": "healthy",
        "service": "knowledge-assessment",
        "timestamp": datetime.utcnow().isoformat(),
        "features": [
            "assessment_creation",
            "assessment_scoring",
            "certification_issuance",
            "certification_verification",
            "certification_renewal"
        ]
    }

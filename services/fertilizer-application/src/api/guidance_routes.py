"""
API Routes for fertilizer application guidance and best practices.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from datetime import date

from src.models.application_models import (
    GuidanceRequest, GuidanceResponse, ApplicationGuidance,
    ApplicationMethod, FieldConditions
)
from src.services.guidance_service import GuidanceService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/guidance", tags=["guidance"])

# Global service instance
guidance_service: GuidanceService = None


async def get_guidance_service() -> GuidanceService:
    """Dependency to get guidance service instance."""
    global guidance_service
    if guidance_service is None:
        guidance_service = GuidanceService()
    return guidance_service


@router.post("/application-guidance", response_model=GuidanceResponse)
async def get_application_guidance(
    request: GuidanceRequest,
    service: GuidanceService = Depends(get_guidance_service)
):
    """
    Get comprehensive application guidance for fertilizer application.
    
    This endpoint provides detailed, step-by-step guidance for fertilizer
    application including pre-application preparation, application procedures,
    safety precautions, calibration instructions, and troubleshooting tips.
    
    **Guidance includes:**
    - Pre-application checklist and preparation steps
    - Step-by-step application instructions
    - Safety precautions and PPE requirements
    - Equipment calibration procedures
    - Troubleshooting common issues
    - Post-application tasks and monitoring
    - Video tutorials and interactive guides
    - Expert consultation recommendations
    - Regulatory compliance checking
    - Educational content and best practices
    
    **Agricultural Context:**
    - Method-specific best practices
    - Weather condition considerations
    - Field condition adaptations
    - Crop growth stage timing
    - Equipment-specific guidance
    - Experience-level adaptation
    """
    try:
        logger.info(f"Providing application guidance for method: {request.application_method.method_type}")
        
        response = await service.provide_application_guidance(request)
        
        logger.info("Application guidance provided successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error providing application guidance: {e}")
        raise HTTPException(status_code=500, detail=f"Application guidance failed: {str(e)}")


@router.get("/best-practices/{method_type}")
async def get_best_practices(
    method_type: str,
    service: GuidanceService = Depends(get_guidance_service)
):
    """
    Get best practices for a specific application method.
    
    This endpoint provides educational content and best practices
    for the specified fertilizer application method.
    """
    try:
        logger.info(f"Getting best practices for method: {method_type}")
        
        # Get educational content for the method
        educational_content = await service._get_educational_content(
            ApplicationMethod(method_id="temp", method_type=method_type), 
            None
        )
        
        return {
            "method_type": method_type,
            "best_practices": educational_content.get("best_practices", {}),
            "safety_guidelines": educational_content.get("safety_guidelines", {}),
            "environmental_stewardship": educational_content.get("environmental_stewardship", {})
        }
        
    except Exception as e:
        logger.error(f"Error getting best practices: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get best practices: {str(e)}")


@router.get("/video-tutorials/{method_type}")
async def get_video_tutorials(
    method_type: str,
    experience_level: Optional[str] = Query(None, description="Operator experience level"),
    service: GuidanceService = Depends(get_guidance_service)
):
    """
    Get video tutorials for a specific application method.
    
    This endpoint provides relevant video tutorials based on the
    application method and operator experience level.
    """
    try:
        logger.info(f"Getting video tutorials for method: {method_type}, experience: {experience_level}")
        
        tutorials = await service._get_relevant_video_tutorials(
            ApplicationMethod(method_id="temp", method_type=method_type),
            experience_level
        )
        
        return {
            "method_type": method_type,
            "experience_level": experience_level,
            "tutorials": tutorials or []
        }
        
    except Exception as e:
        logger.error(f"Error getting video tutorials: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get video tutorials: {str(e)}")


@router.get("/expert-consultation/{method_type}")
async def get_expert_consultation(
    method_type: str,
    field_size_acres: Optional[float] = Query(None, description="Field size in acres"),
    service: GuidanceService = Depends(get_guidance_service)
):
    """
    Get expert consultation recommendations for a specific application method.
    
    This endpoint provides contact information for relevant experts
    based on the application method and field conditions.
    """
    try:
        logger.info(f"Getting expert consultation for method: {method_type}")
        
        # Create field conditions if provided
        field_conditions = None
        if field_size_acres:
            field_conditions = FieldConditions(
                field_size_acres=field_size_acres,
                soil_type="unknown",
                slope_percent=0.0,
                drainage_class="unknown",
                irrigation_available=False,
                field_shape="unknown",
                access_roads=[]
            )
        
        experts = await service._get_expert_consultation_recommendations(
            ApplicationMethod(method_id="temp", method_type=method_type),
            field_conditions or FieldConditions(
                field_size_acres=50.0,
                soil_type="unknown",
                slope_percent=0.0,
                drainage_class="unknown",
                irrigation_available=False,
                field_shape="unknown",
                access_roads=[]
            )
        )
        
        return {
            "method_type": method_type,
            "field_size_acres": field_size_acres,
            "expert_recommendations": experts or []
        }
        
    except Exception as e:
        logger.error(f"Error getting expert consultation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get expert consultation: {str(e)}")


@router.get("/regulatory-compliance/{method_type}")
async def get_regulatory_compliance(
    method_type: str,
    field_size_acres: Optional[float] = Query(None, description="Field size in acres"),
    service: GuidanceService = Depends(get_guidance_service)
):
    """
    Check regulatory compliance for a specific application method.
    
    This endpoint provides compliance checking and regulatory
    requirements for the specified application method.
    """
    try:
        logger.info(f"Checking regulatory compliance for method: {method_type}")
        
        # Create field conditions if provided
        field_conditions = FieldConditions(
            field_size_acres=field_size_acres or 50.0,
            soil_type="unknown",
            slope_percent=0.0,
            drainage_class="unknown",
            irrigation_available=False,
            field_shape="unknown",
            access_roads=[]
        )
        
        compliance = await service._check_regulatory_compliance(
            ApplicationMethod(method_id="temp", method_type=method_type),
            field_conditions
        )
        
        return {
            "method_type": method_type,
            "field_size_acres": field_size_acres,
            "compliance_status": compliance
        }
        
    except Exception as e:
        logger.error(f"Error checking regulatory compliance: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to check compliance: {str(e)}")


@router.get("/interactive-guides/{method_type}")
async def get_interactive_guides(
    method_type: str,
    service: GuidanceService = Depends(get_guidance_service)
):
    """
    Get interactive guides for a specific application method.
    
    This endpoint provides interactive tools and calculators
    for the specified application method.
    """
    try:
        logger.info(f"Getting interactive guides for method: {method_type}")
        
        guides = service._get_interactive_guides(
            ApplicationMethod(method_id="temp", method_type=method_type)
        )
        
        return {
            "method_type": method_type,
            "interactive_guides": guides or []
        }
        
    except Exception as e:
        logger.error(f"Error getting interactive guides: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get interactive guides: {str(e)}")


@router.get("/equipment-maintenance/{method_type}")
async def get_equipment_maintenance(
    method_type: str,
    service: GuidanceService = Depends(get_guidance_service)
):
    """
    Get equipment maintenance schedule for a specific application method.
    
    This endpoint provides maintenance schedules and requirements
    for equipment used in the specified application method.
    """
    try:
        logger.info(f"Getting equipment maintenance for method: {method_type}")
        
        maintenance = service._get_equipment_maintenance_schedule(
            ApplicationMethod(method_id="temp", method_type=method_type)
        )
        
        return {
            "method_type": method_type,
            "maintenance_schedule": maintenance or {}
        }
        
    except Exception as e:
        logger.error(f"Error getting equipment maintenance: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get maintenance schedule: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for guidance service monitoring."""
    return {"status": "healthy", "service": "guidance", "features": "comprehensive"}
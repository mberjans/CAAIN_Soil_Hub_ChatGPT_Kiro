"""
API Routes for fertilizer application guidance and best practices.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from datetime import date

from ..models.application_models import (
    GuidanceRequest, GuidanceResponse, ApplicationGuidance,
    ApplicationMethod, FieldConditions
)
from ..services.guidance_service import GuidanceService

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
    
    **Agricultural Context:**
    - Method-specific best practices
    - Weather condition considerations
    - Field condition adaptations
    - Crop growth stage timing
    - Equipment-specific guidance
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
    
    Returns comprehensive best practices and guidelines for the specified
    application method, including preparation, application, and follow-up
    procedures based on agricultural research and expert recommendations.
    
    **Best Practices include:**
    - Preparation procedures
    - Application techniques
    - Safety guidelines
    - Quality control measures
    - Troubleshooting tips
    - Post-application monitoring
    """
    try:
        logger.info(f"Retrieving best practices for method: {method_type}")
        
        # Get method-specific guidance from service
        method_guidance = await service._get_method_guidance(
            ApplicationMethod(
                method_id="temp",
                method_type=method_type,
                recommended_equipment=None,
                application_rate=0,
                rate_unit="lbs/acre",
                application_timing="flexible",
                efficiency_score=0.8,
                cost_per_acre=20.0,
                labor_requirements="medium",
                environmental_impact="low",
                pros=[],
                cons=[]
            )
        )
        
        best_practices = {
            "method_type": method_type,
            "pre_application": method_guidance["pre_application"],
            "application": method_guidance["application"],
            "post_application": method_guidance["post_application"],
            "safety": method_guidance["safety"],
            "calibration": method_guidance["calibration"],
            "troubleshooting": method_guidance["troubleshooting"]
        }
        
        logger.info(f"Retrieved best practices for {method_type}")
        return best_practices
        
    except Exception as e:
        logger.error(f"Error retrieving best practices: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve best practices: {str(e)}")


@router.get("/safety-guidelines/{method_type}")
async def get_safety_guidelines(method_type: str):
    """
    Get safety guidelines for a specific application method.
    
    Returns comprehensive safety guidelines including personal protective
    equipment requirements, handling procedures, and emergency protocols
    for the specified application method.
    
    **Safety Guidelines include:**
    - Personal protective equipment (PPE) requirements
    - Chemical handling procedures
    - Equipment safety checks
    - Emergency response protocols
    - Environmental protection measures
    - Health monitoring recommendations
    """
    try:
        logger.info(f"Retrieving safety guidelines for method: {method_type}")
        
        # This would typically query safety database
        # For now, return sample safety guidelines
        safety_guidelines = {
            "method_type": method_type,
            "ppe_requirements": [
                "Chemical-resistant gloves",
                "Safety glasses or goggles",
                "Long-sleeved shirt and pants",
                "Closed-toe shoes",
                "Respirator (if handling dust)"
            ],
            "handling_procedures": [
                "Read and follow product label instructions",
                "Avoid skin contact with fertilizer",
                "Wash hands thoroughly after handling",
                "Keep fertilizer away from water sources",
                "Store fertilizer in secure, dry location"
            ],
            "equipment_safety": [
                "Inspect equipment before use",
                "Check all safety guards and shields",
                "Test emergency stop functions",
                "Verify proper equipment operation",
                "Follow manufacturer safety guidelines"
            ],
            "emergency_protocols": [
                "Have emergency contact information readily available",
                "Know location of nearest medical facility",
                "Keep first aid kit accessible",
                "Know proper cleanup procedures for spills",
                "Have emergency shower/eye wash available"
            ],
            "environmental_protection": [
                "Avoid application near water sources",
                "Follow buffer zone requirements",
                "Monitor weather conditions",
                "Prevent fertilizer runoff",
                "Follow environmental regulations"
            ]
        }
        
        logger.info(f"Retrieved safety guidelines for {method_type}")
        return safety_guidelines
        
    except Exception as e:
        logger.error(f"Error retrieving safety guidelines: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve safety guidelines: {str(e)}")


@router.get("/calibration-guide/{method_type}")
async def get_calibration_guide(method_type: str):
    """
    Get calibration guide for a specific application method.
    
    Returns detailed calibration procedures and instructions for the
    specified application method, including equipment setup, rate
    calculations, and verification procedures.
    
    **Calibration Guide includes:**
    - Equipment setup procedures
    - Rate calculation methods
    - Calibration verification steps
    - Troubleshooting calibration issues
    - Documentation requirements
    """
    try:
        logger.info(f"Retrieving calibration guide for method: {method_type}")
        
        # This would typically query calibration database
        # For now, return sample calibration guide
        calibration_guide = {
            "method_type": method_type,
            "equipment_setup": [
                "Check equipment condition and cleanliness",
                "Verify all settings and adjustments",
                "Test equipment operation",
                "Check for worn or damaged parts",
                "Ensure proper equipment configuration"
            ],
            "rate_calculation": [
                "Measure application width accurately",
                "Collect fertilizer from known area",
                "Weigh collected fertilizer",
                "Calculate actual application rate",
                "Compare with target rate"
            ],
            "verification_steps": [
                "Repeat calibration process",
                "Verify consistency of results",
                "Adjust settings if needed",
                "Document calibration results",
                "Test in field conditions"
            ],
            "troubleshooting": [
                "Check for equipment wear or damage",
                "Verify fertilizer flow and distribution",
                "Check ground speed consistency",
                "Verify equipment settings",
                "Consult manufacturer if needed"
            ],
            "documentation": [
                "Record calibration date and time",
                "Document equipment settings",
                "Record application rate achieved",
                "Note any adjustments made",
                "Keep calibration records"
            ]
        }
        
        logger.info(f"Retrieved calibration guide for {method_type}")
        return calibration_guide
        
    except Exception as e:
        logger.error(f"Error retrieving calibration guide: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve calibration guide: {str(e)}")


@router.get("/weather-advisories")
async def get_weather_advisories(
    method_type: str = Query(..., description="Application method type"),
    temperature: Optional[float] = Query(None, description="Current temperature in Celsius"),
    humidity: Optional[float] = Query(None, description="Current humidity percentage"),
    wind_speed: Optional[float] = Query(None, description="Current wind speed in km/h"),
    precipitation: Optional[float] = Query(None, description="Current precipitation in mm")
):
    """
    Get weather advisories for fertilizer application.
    
    Returns weather-related advisories and recommendations for fertilizer
    application based on current weather conditions and the selected
    application method.
    
    **Weather Considerations:**
    - Temperature effects on application
    - Humidity impact on fertilizer performance
    - Wind speed limitations
    - Precipitation timing
    - Optimal application windows
    """
    try:
        logger.info(f"Generating weather advisories for method: {method_type}")
        
        advisories = []
        
        # Temperature advisories
        if temperature is not None:
            if temperature > 30:
                advisories.append("High temperature - avoid application during peak heat hours")
            elif temperature < 5:
                advisories.append("Low temperature - ensure fertilizer is properly dissolved")
            elif 15 <= temperature <= 25:
                advisories.append("Optimal temperature conditions for application")
        
        # Humidity advisories
        if humidity is not None:
            if humidity > 80:
                advisories.append("High humidity - monitor for condensation issues")
            elif humidity < 30:
                advisories.append("Low humidity - increased risk of leaf burn with foliar application")
            elif 40 <= humidity <= 70:
                advisories.append("Optimal humidity conditions for application")
        
        # Wind advisories
        if wind_speed is not None:
            if wind_speed > 15:
                advisories.append("High wind conditions - postpone application")
            elif wind_speed > 10:
                advisories.append("Moderate wind - monitor application quality closely")
            elif wind_speed <= 10:
                advisories.append("Good wind conditions for application")
        
        # Precipitation advisories
        if precipitation is not None:
            if precipitation > 0:
                advisories.append("Precipitation detected - postpone application until conditions improve")
            else:
                advisories.append("No precipitation - good conditions for application")
        
        # Method-specific advisories
        if method_type.lower() == "foliar":
            if temperature and temperature > 25:
                advisories.append("High temperature - risk of leaf burn with foliar application")
            if humidity and humidity < 30:
                advisories.append("Low humidity - increased risk of leaf burn")
        
        elif method_type.lower() == "broadcast":
            if wind_speed and wind_speed > 8:
                advisories.append("Wind conditions may affect broadcast pattern uniformity")
        
        weather_advisories = {
            "method_type": method_type,
            "current_conditions": {
                "temperature": temperature,
                "humidity": humidity,
                "wind_speed": wind_speed,
                "precipitation": precipitation
            },
            "advisories": advisories,
            "recommendation": "Proceed with application" if not advisories else "Consider postponing application"
        }
        
        logger.info(f"Generated weather advisories for {method_type}")
        return weather_advisories
        
    except Exception as e:
        logger.error(f"Error generating weather advisories: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate weather advisories: {str(e)}")


@router.get("/timing-recommendations/{method_type}")
async def get_timing_recommendations(
    method_type: str,
    crop_stage: Optional[str] = Query(None, description="Crop growth stage"),
    field_size: Optional[float] = Query(None, description="Field size in acres")
):
    """
    Get timing recommendations for fertilizer application.
    
    Returns timing recommendations and optimal application windows for
    the specified application method, considering crop growth stage
    and field characteristics.
    
    **Timing Considerations:**
    - Crop growth stage requirements
    - Field size and application time
    - Weather timing windows
    - Equipment availability
    - Labor scheduling
    """
    try:
        logger.info(f"Retrieving timing recommendations for method: {method_type}")
        
        # Base timing recommendations
        timing_recommendations = [
            "Apply during early morning or late evening for best results",
            "Avoid application during hot, sunny conditions",
            "Ensure adequate soil moisture for nutrient uptake"
        ]
        
        # Method-specific timing
        if method_type.lower() == "foliar":
            timing_recommendations.extend([
                "Apply when leaves are dry but humidity is moderate",
                "Avoid application during hot, sunny conditions",
                "Apply during early morning or late evening"
            ])
        
        elif method_type.lower() == "broadcast":
            timing_recommendations.extend([
                "Apply when wind conditions are calm",
                "Avoid application during peak wind hours",
                "Consider field size for application timing"
            ])
        
        elif method_type.lower() == "sidedress":
            timing_recommendations.extend([
                "Apply when crop is at appropriate growth stage",
                "Ensure soil moisture is adequate for uptake",
                "Time application with crop development"
            ])
        
        # Crop stage specific timing
        if crop_stage:
            if crop_stage.lower() == "emergence":
                timing_recommendations.append("Apply at or before planting for best results")
            elif crop_stage.lower() == "vegetative":
                timing_recommendations.append("Apply during early to mid-vegetative stage")
            elif crop_stage.lower() == "reproductive":
                timing_recommendations.append("Apply before reproductive stage begins")
        
        # Field size considerations
        if field_size:
            if field_size > 100:
                timing_recommendations.append("Large field - plan for extended application time")
            elif field_size < 10:
                timing_recommendations.append("Small field - can be completed quickly")
        
        recommendations = {
            "method_type": method_type,
            "crop_stage": crop_stage,
            "field_size": field_size,
            "timing_recommendations": timing_recommendations,
            "optimal_windows": [
                "Early morning (6 AM - 10 AM)",
                "Late evening (6 PM - 8 PM)"
            ],
            "avoid_windows": [
                "Midday (10 AM - 4 PM)",
                "Peak wind hours",
                "During precipitation"
            ]
        }
        
        logger.info(f"Retrieved timing recommendations for {method_type}")
        return recommendations
        
    except Exception as e:
        logger.error(f"Error retrieving timing recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve timing recommendations: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for guidance service."""
    return {
        "service": "fertilizer-application-guidance",
        "status": "healthy",
        "endpoints": [
            "application_guidance",
            "best_practices",
            "safety_guidelines",
            "calibration_guide",
            "weather_advisories",
            "timing_recommendations"
        ]
    }
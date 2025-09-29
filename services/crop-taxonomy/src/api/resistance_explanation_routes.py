"""
Resistance Explanation API Routes

FastAPI routes for resistance recommendation explanations and educational content.
Provides comprehensive resistance-specific explanations, educational content,
and stewardship guidelines for crop variety recommendations.

TICKET-005_crop-variety-recommendations-10.3: Add comprehensive resistance recommendation explanations and education
"""

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from typing import List, Optional, Dict, Any
import logging
from uuid import UUID
from pydantic import BaseModel, Field

from services.resistance_explanation_service import ResistanceExplanationService
from models.resistance_explanation_models import (
    ResistanceExplanationRequest,
    ResistanceExplanationResponse,
    EducationalContentRequest,
    EducationalContentResponse,
    StewardshipGuidelinesRequest,
    StewardshipGuidelinesResponse,
    MechanismExplanationRequest,
    MechanismExplanationResponse,
    ComplianceRequirementsRequest,
    ComplianceRequirementsResponse,
    DurabilityAssessmentRequest,
    DurabilityAssessmentResponse,
    ResistanceType
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/resistance-explanations", tags=["resistance-explanations"])

# Service instance
resistance_explanation_service = ResistanceExplanationService()




@router.post("/generate", response_model=ResistanceExplanationResponse)
async def generate_resistance_explanation(
    request: ResistanceExplanationRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate comprehensive resistance explanation for a variety recommendation.
    
    This endpoint provides:
    - Resistance mechanism explanations
    - Educational content and training materials
    - Stewardship guidelines and compliance requirements
    - Management recommendations and best practices
    - Durability assessment and sustainability information
    - Regulatory compliance and documentation requirements
    
    **Agricultural Use Cases:**
    - Understanding resistance mechanisms and limitations
    - Developing resistance management strategies
    - Ensuring regulatory compliance and stewardship
    - Training farmers and agricultural professionals
    - Implementing sustainable resistance management practices
    """
    try:
        logger.info(f"Generating resistance explanation for variety: {request.variety_data.get('variety_name', 'Unknown')}")
        
        # Generate comprehensive resistance explanation
        explanation = await resistance_explanation_service.generate_resistance_explanation(
            variety_data=request.variety_data,
            pest_resistance_data=request.pest_resistance_data,
            context=request.context,
            explanation_options=request.explanation_options
        )
        
        # Log explanation generation completion
        logger.info(f"Completed resistance explanation generation: {explanation['explanation_id']}")
        
        return ResistanceExplanationResponse(**explanation)
        
    except Exception as e:
        logger.error(f"Error generating resistance explanation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Resistance explanation generation failed: {str(e)}"
        )


@router.post("/educational-content")
async def generate_educational_content(
    request: EducationalContentRequest
):
    """
    Generate educational content for resistance management.
    
    **Parameters:**
    - **resistance_traits**: List of resistance traits to explain
    - **context**: Farm and environmental context
    - **education_level**: Education level (basic, intermediate, advanced)
    - **include_mechanisms**: Include mechanism explanations
    - **include_management**: Include management guidance
    - **include_compliance**: Include compliance information
    
    **Returns:**
    Educational content including:
    - Resistance mechanism explanations
    - Management principles and best practices
    - Stewardship guidelines and compliance requirements
    - Training materials and resources
    - Monitoring and documentation requirements
    """
    try:
        logger.info(f"Generating educational content for {len(request.resistance_traits)} resistance traits")
        
        # Generate educational content
        educational_content = resistance_explanation_service._generate_educational_content(
            resistance_traits=request.resistance_traits,
            context=request.context
        )
        
        # Filter content based on request options
        filtered_content = {}
        
        if request.include_mechanisms:
            filtered_content["mechanism_explanations"] = educational_content.get("trait_specific_education", {})
        
        if request.include_management:
            filtered_content["management_principles"] = educational_content.get("resistance_management_principles", {})
            filtered_content["stewardship_practices"] = educational_content.get("stewardship_best_practices", {})
        
        if request.include_compliance:
            filtered_content["compliance_requirements"] = educational_content.get("trait_specific_education", {})
        
        filtered_content["durability_factors"] = educational_content.get("durability_factors", {})
        
        return {
            "educational_content": filtered_content,
            "education_level": request.education_level,
            "content_sections": list(filtered_content.keys()),
            "generated_at": resistance_explanation_service._get_current_timestamp()
        }
        
    except Exception as e:
        logger.error(f"Error generating educational content: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Educational content generation failed: {str(e)}"
        )


@router.post("/stewardship-guidelines")
async def generate_stewardship_guidelines(
    request: StewardshipGuidelinesRequest
):
    """
    Generate stewardship guidelines for resistance management.
    
    **Parameters:**
    - **resistance_traits**: List of resistance traits
    - **context**: Farm and environmental context
    - **compliance_level**: Compliance level (basic, intermediate, advanced)
    - **include_refuge_requirements**: Include refuge requirements
    - **include_monitoring**: Include monitoring requirements
    - **include_documentation**: Include documentation requirements
    
    **Returns:**
    Stewardship guidelines including:
    - Refuge requirements and compliance
    - Monitoring schedules and requirements
    - Documentation and record keeping
    - Compliance checklists and verification
    - Regulatory requirements and restrictions
    """
    try:
        logger.info(f"Generating stewardship guidelines for {len(request.resistance_traits)} resistance traits")
        
        # Generate stewardship guidelines
        stewardship_guidelines = resistance_explanation_service._generate_stewardship_guidelines(
            resistance_traits=request.resistance_traits,
            context=request.context
        )
        
        # Filter guidelines based on request options
        filtered_guidelines = {}
        
        if request.include_refuge_requirements:
            filtered_guidelines["refuge_requirements"] = stewardship_guidelines.get("refuge_requirements", {})
        
        if request.include_monitoring:
            filtered_guidelines["monitoring_requirements"] = stewardship_guidelines.get("monitoring_requirements", [])
        
        if request.include_documentation:
            filtered_guidelines["documentation_requirements"] = stewardship_guidelines.get("documentation_requirements", [])
        
        filtered_guidelines["compliance_checklist"] = stewardship_guidelines.get("compliance_checklist", [])
        
        return {
            "stewardship_guidelines": filtered_guidelines,
            "compliance_level": request.compliance_level,
            "guideline_sections": list(filtered_guidelines.keys()),
            "generated_at": resistance_explanation_service._get_current_timestamp()
        }
        
    except Exception as e:
        logger.error(f"Error generating stewardship guidelines: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Stewardship guidelines generation failed: {str(e)}"
        )


@router.get("/mechanism-explanations")
async def get_resistance_mechanism_explanations(
    resistance_type: str = Query(..., description="Type of resistance (bt_toxin, herbicide_tolerance, disease_resistance, insect_resistance)"),
    include_details: bool = Query(True, description="Include detailed explanations")
):
    """
    Get detailed explanations of resistance mechanisms.
    
    **Parameters:**
    - **resistance_type**: Type of resistance mechanism
    - **include_details**: Include detailed explanations
    
    **Returns:**
    Mechanism explanations including:
    - Mechanism description and process
    - Target organisms and effectiveness
    - Durability and resistance risk
    - Management strategies and requirements
    """
    try:
        logger.info(f"Retrieving mechanism explanations for resistance type: {resistance_type}")
        
        # Get resistance knowledge base
        resistance_knowledge = resistance_explanation_service.resistance_knowledge_base
        
        if resistance_type not in resistance_knowledge:
            raise HTTPException(
                status_code=404,
                detail=f"Resistance type '{resistance_type}' not found"
            )
        
        knowledge = resistance_knowledge[resistance_type]
        
        response = {
            "resistance_type": resistance_type,
            "mechanism": knowledge["mechanism"],
            "description": knowledge["description"],
            "durability": knowledge["durability"],
            "resistance_risk": knowledge["resistance_risk"],
            "management_strategy": knowledge["management_strategy"]
        }
        
        if include_details:
            # Add additional details based on resistance type
            if resistance_type == "bt_toxin":
                response["target_pests"] = knowledge.get("target_pests", [])
                response["refuge_requirements"] = "Required for resistance management"
                response["monitoring_requirements"] = ["Pest population monitoring", "Resistance development tracking"]
            
            elif resistance_type == "herbicide_tolerance":
                response["target_herbicides"] = knowledge.get("target_herbicides", [])
                response["rotation_requirements"] = "Required for resistance management"
                response["monitoring_requirements"] = ["Weed population monitoring", "Resistance development tracking"]
            
            elif resistance_type == "disease_resistance":
                response["target_diseases"] = knowledge.get("target_diseases", [])
                response["durability_factors"] = ["Pathogen evolution", "Environmental conditions", "Management practices"]
                response["monitoring_requirements"] = ["Disease incidence monitoring", "Pathogen population tracking"]
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving mechanism explanations: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve mechanism explanations: {str(e)}"
        )


@router.get("/compliance-requirements")
async def get_compliance_requirements(
    resistance_traits: List[str] = Query(..., description="List of resistance traits"),
    region: str = Query("US", description="Geographic region for compliance requirements")
):
    """
    Get compliance requirements for resistance traits.
    
    **Parameters:**
    - **resistance_traits**: List of resistance traits
    - **region**: Geographic region for compliance requirements
    
    **Returns:**
    Compliance requirements including:
    - USDA requirements and regulations
    - EPA requirements and restrictions
    - State-specific requirements
    - Label requirements and restrictions
    - Documentation and reporting requirements
    """
    try:
        logger.info(f"Retrieving compliance requirements for {len(resistance_traits)} traits in region: {region}")
        
        # Generate compliance requirements
        compliance_requirements = resistance_explanation_service._generate_compliance_requirements(
            resistance_traits=[{"type": trait} for trait in resistance_traits],
            context={"region": region}
        )
        
        return {
            "resistance_traits": resistance_traits,
            "region": region,
            "compliance_requirements": compliance_requirements,
            "generated_at": resistance_explanation_service._get_current_timestamp()
        }
        
    except Exception as e:
        logger.error(f"Error retrieving compliance requirements: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve compliance requirements: {str(e)}"
        )


@router.get("/durability-assessment")
async def get_durability_assessment(
    resistance_traits: List[str] = Query(..., description="List of resistance traits"),
    context: Optional[str] = Query(None, description="Environmental context as JSON string")
):
    """
    Get durability assessment for resistance traits.
    
    **Parameters:**
    - **resistance_traits**: List of resistance traits
    - **context**: Environmental context
    
    **Returns:**
    Durability assessment including:
    - Overall durability rating
    - Durability factors and influences
    - Durability timeline and projections
    - Sustainability score and metrics
    - Management recommendations for durability
    """
    try:
        logger.info(f"Generating durability assessment for {len(resistance_traits)} traits")
        
        # Parse context if provided
        parsed_context = {}
        if context:
            try:
                import json
                parsed_context = json.loads(context)
            except json.JSONDecodeError:
                logger.warning("Invalid JSON context provided, using empty context")
        
        # Generate durability assessment
        durability_assessment = resistance_explanation_service._generate_durability_assessment(
            resistance_traits=[{"type": trait} for trait in resistance_traits],
            context=parsed_context
        )
        
        return {
            "resistance_traits": resistance_traits,
            "durability_assessment": durability_assessment,
            "generated_at": resistance_explanation_service._get_current_timestamp()
        }
        
    except Exception as e:
        logger.error(f"Error generating durability assessment: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Durability assessment generation failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for service monitoring."""
    return {
        "status": "healthy",
        "service": "resistance-explanations",
        "version": "1.0.0",
        "features": [
            "resistance_mechanism_explanations",
            "educational_content_generation",
            "stewardship_guidelines",
            "compliance_requirements",
            "durability_assessment"
        ]
    }


# Add helper method to service for timestamp generation
def _get_current_timestamp(self) -> str:
    """Get current timestamp in ISO format."""
    from datetime import datetime
    return datetime.utcnow().isoformat()

# Add the method to the service class
ResistanceExplanationService._get_current_timestamp = _get_current_timestamp
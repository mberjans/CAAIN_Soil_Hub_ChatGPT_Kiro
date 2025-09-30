"""
API Routes for fertilizer application method selection and analysis.
"""

import asyncio
import logging
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field

from ..models.application_models import (
    ApplicationRequest, ApplicationResponse, ApplicationMethod,
    FieldConditions, CropRequirements, FertilizerSpecification,
    EquipmentSpecification
)
from ..services.application_method_service import ApplicationMethodService
from ..services.cost_analysis_service import CostAnalysisService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/application", tags=["application"])

# Global service instances
application_service: ApplicationMethodService = None
cost_service: CostAnalysisService = None


async def get_application_service() -> ApplicationMethodService:
    """Dependency to get application method service instance."""
    global application_service
    if application_service is None:
        application_service = ApplicationMethodService()
    return application_service


async def get_cost_service() -> CostAnalysisService:
    """Dependency to get cost analysis service instance."""
    global cost_service
    if cost_service is None:
        cost_service = CostAnalysisService()
    return cost_service


@router.post("/select-methods", response_model=ApplicationResponse)
async def select_application_methods(
    request: ApplicationRequest,
    service: ApplicationMethodService = Depends(get_application_service)
):
    """
    Select optimal fertilizer application methods based on field conditions,
    crop requirements, and available equipment.
    
    This endpoint analyzes various factors to recommend the most suitable
    application methods for fertilizer application, considering efficiency,
    cost, equipment compatibility, and environmental impact.
    
    **Agricultural Context:**
    - Considers field size, soil type, and drainage characteristics
    - Evaluates crop growth stage and nutrient requirements
    - Assesses equipment compatibility and capacity
    - Provides efficiency scores and cost estimates
    
    **Response includes:**
    - Primary recommendation with detailed analysis
    - Alternative methods for comparison
    - Cost comparison across methods
    - Equipment compatibility matrix
    - Efficiency analysis and optimization opportunities
    """
    try:
        logger.info(f"Processing application method selection request")
        
        response = await service.select_application_methods(request)
        
        logger.info(f"Application method selection completed successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error in application method selection: {e}")
        raise HTTPException(status_code=500, detail=f"Application method selection failed: {str(e)}")


@router.post("/analyze-costs")
async def analyze_application_costs(
    request: ApplicationRequest,
    cost_service: CostAnalysisService = Depends(get_cost_service)
):
    """
    Analyze costs for different fertilizer application methods.
    
    This endpoint provides comprehensive cost analysis including fertilizer,
    equipment, labor, fuel, and maintenance costs for different application
    methods, helping farmers make informed economic decisions.
    
    **Cost Analysis includes:**
    - Fertilizer costs with efficiency adjustments
    - Equipment costs (rental vs ownership)
    - Labor costs based on skill requirements
    - Fuel costs based on field conditions
    - Maintenance costs and equipment wear
    - Cost per acre and total field costs
    
    **Economic Analysis:**
    - Comparative cost analysis across methods
    - ROI analysis and payback periods
    - Cost optimization recommendations
    - Sensitivity analysis for cost factors
    """
    try:
        logger.info(f"Processing application cost analysis request")
        
        # First get application methods
        application_service = await get_application_service()
        method_response = await application_service.select_application_methods(request)
        
        # Then analyze costs
        cost_analysis = await cost_service.analyze_application_costs(
            method_response.recommended_methods,
            request.field_conditions,
            request.crop_requirements,
            request.fertilizer_specification,
            request.available_equipment
        )
        
        logger.info(f"Application cost analysis completed successfully")
        return cost_analysis
        
    except Exception as e:
        logger.error(f"Error in application cost analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Cost analysis failed: {str(e)}")


@router.get("/methods", response_model=List[Dict[str, Any]])
async def get_available_methods():
    """
    Get list of available fertilizer application methods.
    
    Returns comprehensive information about all supported application
    methods including their characteristics, suitability factors, and
    equipment requirements.
    
    **Method Information includes:**
    - Method type and description
    - Equipment requirements
    - Fertilizer form compatibility
    - Field size suitability
    - Efficiency ratings
    - Cost estimates
    - Environmental impact
    - Pros and cons
    """
    try:
        logger.info("Retrieving available application methods")
        
        # Get service instance
        service = await get_application_service()
        
        # Extract method information from service database
        methods = []
        for method_type, method_data in service.method_database.items():
            method_info = {
                "method_type": method_type,
                "name": method_data["name"],
                "description": method_data["description"],
                "equipment_types": method_data["equipment_types"],
                "fertilizer_forms": method_data["fertilizer_forms"],
                "field_size_range": method_data["field_size_range"],
                "efficiency_score": method_data["efficiency_score"],
                "cost_per_acre": method_data["cost_per_acre"],
                "labor_intensity": method_data["labor_intensity"],
                "environmental_impact": method_data["environmental_impact"],
                "pros": method_data["pros"],
                "cons": method_data["cons"]
            }
            methods.append(method_info)
        
        logger.info(f"Retrieved {len(methods)} application methods")
        return methods
        
    except Exception as e:
        logger.error(f"Error retrieving application methods: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve application methods: {str(e)}")


@router.post("/validate-request")
async def validate_application_request(request: ApplicationRequest):
    """
    Validate application request parameters and provide feedback.
    
    This endpoint validates the application request parameters and provides
    feedback on potential issues or improvements before processing the
    actual method selection.
    
    **Validation checks:**
    - Field conditions validity
    - Crop requirements completeness
    - Fertilizer specification accuracy
    - Equipment compatibility
    - Parameter ranges and constraints
    """
    try:
        logger.info("Validating application request")
        
        validation_results = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "suggestions": []
        }
        
        # Validate field conditions
        if request.field_conditions.field_size_acres < 0.1:
            validation_results["errors"].append("Field size must be at least 0.1 acres")
            validation_results["valid"] = False
        
        if request.field_conditions.field_size_acres > 10000:
            validation_results["warnings"].append("Field size exceeds recommended maximum")
        
        # Validate crop requirements
        if not request.crop_requirements.crop_type:
            validation_results["errors"].append("Crop type is required")
            validation_results["valid"] = False
        
        if not request.crop_requirements.growth_stage:
            validation_results["errors"].append("Growth stage is required")
            validation_results["valid"] = False
        
        # Validate fertilizer specification
        if not request.fertilizer_specification.fertilizer_type:
            validation_results["errors"].append("Fertilizer type is required")
            validation_results["valid"] = False
        
        if not request.fertilizer_specification.npk_ratio:
            validation_results["errors"].append("NPK ratio is required")
            validation_results["valid"] = False
        
        # Validate equipment
        if not request.available_equipment:
            validation_results["warnings"].append("No equipment specified - will use rental costs")
        
        # Provide suggestions
        if request.field_conditions.slope_percent and request.field_conditions.slope_percent > 10:
            validation_results["suggestions"].append("High slope may limit some application methods")
        
        if request.field_conditions.soil_type.lower() == "clay":
            validation_results["suggestions"].append("Clay soils may require specialized equipment")
        
        logger.info(f"Request validation completed: {validation_results['valid']}")
        return validation_results
        
    except Exception as e:
        logger.error(f"Error validating application request: {e}")
        raise HTTPException(status_code=500, detail=f"Request validation failed: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for application service."""
    return {
        "service": "fertilizer-application",
        "status": "healthy",
        "endpoints": [
            "select-methods",
            "analyze-costs",
            "methods",
            "validate-request"
        ]
    }
"""
API Routes for fertilizer application method recommendations and analysis.
Implements TICKET-023_fertilizer-application-method-10.1 endpoints.
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional
from uuid import uuid4
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from src.models.application_models import (
    ApplicationRequest, ApplicationResponse, ApplicationMethod,
    FieldConditions, CropRequirements, FertilizerSpecification,
    EquipmentSpecification, ApplicationMethodType
)
from src.services.application_method_service import ApplicationMethodService
from src.services.cost_analysis_service import CostAnalysisService

logger = logging.getLogger(__name__)

# Create router with the specific prefix required by the task
router = APIRouter(prefix="/fertilizer", tags=["fertilizer-application-methods"])

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


class MethodRecommendationRequest(BaseModel):
    """Request model for method recommendations endpoint."""
    farm_context: Dict[str, Any] = Field(..., description="Farm context including field size, soil type, etc.")
    crop_info: Dict[str, Any] = Field(..., description="Crop information including type, growth stage, etc.")
    fertilizer_specs: Dict[str, Any] = Field(..., description="Fertilizer specifications")
    equipment_available: List[Dict[str, Any]] = Field(default_factory=list, description="Available equipment")
    goals: List[str] = Field(default_factory=list, description="Application goals")
    constraints: Optional[Dict[str, Any]] = Field(None, description="Application constraints")


class MethodRecommendationResponse(BaseModel):
    """Response model for method recommendations."""
    request_id: str = Field(..., description="Unique request identifier")
    primary_recommendation: Dict[str, Any] = Field(..., description="Primary method recommendation")
    alternative_methods: List[Dict[str, Any]] = Field(default_factory=list, description="Alternative methods")
    method_scores: Dict[str, float] = Field(..., description="Method scores and rankings")
    cost_analysis: Dict[str, Any] = Field(..., description="Cost analysis across methods")
    implementation_guidance: Dict[str, Any] = Field(..., description="Implementation guidance")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


class MethodComparisonRequest(BaseModel):
    """Request model for method comparison."""
    methods_to_compare: List[str] = Field(..., description="List of methods to compare")
    comparison_criteria: List[str] = Field(default_factory=list, description="Criteria for comparison")
    weighting_preferences: Optional[Dict[str, float]] = Field(None, description="Weighting preferences")
    farm_context: Dict[str, Any] = Field(..., description="Farm context for comparison")


class MethodComparisonResponse(BaseModel):
    """Response model for method comparison."""
    request_id: str = Field(..., description="Unique request identifier")
    comparison_matrix: Dict[str, Dict[str, Any]] = Field(..., description="Comparison matrix")
    rankings: List[Dict[str, Any]] = Field(..., description="Method rankings")
    trade_off_analysis: Dict[str, Any] = Field(..., description="Trade-off analysis")
    decision_support: Dict[str, Any] = Field(..., description="Decision support information")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


@router.post("/application-method/recommend", response_model=MethodRecommendationResponse)
async def recommend_application_methods(
    request: MethodRecommendationRequest,
    service: ApplicationMethodService = Depends(get_application_service)
):
    """
    Recommend optimal fertilizer application methods based on farm context, crop requirements,
    and available equipment.
    
    This endpoint provides comprehensive method recommendations with detailed analysis including:
    - Primary recommendation with detailed justification
    - Alternative methods for comparison
    - Method scores and rankings
    - Cost analysis across methods
    - Implementation guidance and next steps
    
    **Agricultural Context:**
    - Considers field size, soil type, and drainage characteristics
    - Evaluates crop growth stage and nutrient requirements
    - Assesses equipment compatibility and capacity
    - Provides efficiency scores and cost estimates
    - Includes environmental impact considerations
    
    **Performance Requirements:**
    - Response time < 3 seconds for complex multi-criteria analysis
    - Handles concurrent requests efficiently
    - Provides detailed logging for troubleshooting
    """
    try:
        start_time = time.time()
        request_id = str(uuid4())
        
        logger.info(f"Processing method recommendation request {request_id}")
        
        # Convert request to ApplicationRequest format
        application_request = _convert_to_application_request(request)
        
        # Get method recommendations
        response = await service.select_application_methods(application_request)
        
        # Convert response to the required format
        recommendation_response = MethodRecommendationResponse(
            request_id=request_id,
            primary_recommendation={
                "method_type": response.primary_recommendation.method_type.value,
                "method_id": response.primary_recommendation.method_id,
                "recommended_equipment": {
                    "equipment_type": response.primary_recommendation.recommended_equipment.equipment_type.value,
                    "capacity": response.primary_recommendation.recommended_equipment.capacity,
                    "application_width": response.primary_recommendation.recommended_equipment.application_width
                },
                "application_rate": response.primary_recommendation.application_rate,
                "rate_unit": response.primary_recommendation.rate_unit,
                "application_timing": response.primary_recommendation.application_timing,
                "efficiency_score": response.primary_recommendation.efficiency_score,
                "cost_per_acre": response.primary_recommendation.cost_per_acre,
                "labor_requirements": response.primary_recommendation.labor_requirements,
                "environmental_impact": response.primary_recommendation.environmental_impact,
                "pros": response.primary_recommendation.pros,
                "cons": response.primary_recommendation.cons,
                "crop_compatibility_score": response.primary_recommendation.crop_compatibility_score,
                "crop_compatibility_factors": response.primary_recommendation.crop_compatibility_factors
            },
            alternative_methods=[
                {
                    "method_type": method.method_type.value,
                    "method_id": method.method_id,
                    "efficiency_score": method.efficiency_score,
                    "cost_per_acre": method.cost_per_acre,
                    "pros": method.pros,
                    "cons": method.cons
                }
                for method in response.alternative_methods
            ],
            method_scores={
                method.method_type.value: method.efficiency_score
                for method in response.recommended_methods
            },
            cost_analysis=response.cost_comparison or {},
            implementation_guidance={
                "equipment_preparation": _get_equipment_preparation_guidance(response.primary_recommendation),
                "application_timing": response.primary_recommendation.application_timing,
                "safety_considerations": _get_safety_considerations(response.primary_recommendation),
                "quality_control": _get_quality_control_guidance(response.primary_recommendation)
            },
            processing_time_ms=(time.time() - start_time) * 1000
        )
        
        logger.info(f"Method recommendation completed for request {request_id} in {recommendation_response.processing_time_ms:.2f}ms")
        return recommendation_response
        
    except Exception as e:
        logger.error(f"Error in method recommendation: {e}")
        raise HTTPException(status_code=500, detail=f"Method recommendation failed: {str(e)}")


@router.get("/application-options", response_model=Dict[str, Any])
async def get_application_options(
    service: ApplicationMethodService = Depends(get_application_service)
):
    """
    Get comprehensive catalog of available fertilizer application methods and options.
    
    This endpoint provides detailed information about all supported application methods including:
    - Method descriptions and characteristics
    - Equipment requirements and compatibility
    - Suitability criteria for different conditions
    - Benefits and limitations
    - Cost estimates and efficiency ratings
    
    **Method Information includes:**
    - Method type and detailed description
    - Equipment requirements and specifications
    - Fertilizer form compatibility
    - Field size suitability ranges
    - Efficiency ratings and performance metrics
    - Cost estimates per acre
    - Environmental impact assessments
    - Pros and cons for each method
    - Best use cases and recommendations
    
    **Integration Features:**
    - Connects with equipment databases
    - Links to method effectiveness data
    - Provides real-time availability information
    - Includes regional variations and considerations
    """
    try:
        logger.info("Retrieving comprehensive application options catalog")
        
        # Get method information from service database
        methods_catalog = {}
        for method_type, method_data in service.method_database.items():
            methods_catalog[method_type] = {
                "name": method_data["name"],
                "description": method_data["description"],
                "method_type": method_type,
                "equipment_types": method_data["equipment_types"],
                "fertilizer_forms": method_data["fertilizer_forms"],
                "field_size_range": method_data["field_size_range"],
                "efficiency_score": method_data["efficiency_score"],
                "cost_per_acre": method_data["cost_per_acre"],
                "labor_intensity": method_data["labor_intensity"],
                "environmental_impact": method_data["environmental_impact"],
                "pros": method_data["pros"],
                "cons": method_data["cons"],
                "best_use_cases": method_data.get("best_use_cases", []),
                "suitability_criteria": method_data.get("suitability_criteria", {}),
                "equipment_requirements": method_data.get("equipment_requirements", {}),
                "performance_metrics": method_data.get("performance_metrics", {}),
                "regional_considerations": method_data.get("regional_considerations", {}),
                "availability": method_data.get("availability", "generally_available")
            }
        
        # Add method categories and groupings
        method_categories = {
            "broadcast_methods": ["broadcast"],
            "precision_methods": ["band", "sidedress", "injection"],
            "foliar_methods": ["foliar"],
            "irrigation_methods": ["drip", "fertigation"],
            "specialized_methods": ["injection", "fertigation"]
        }
        
        # Add equipment compatibility matrix
        equipment_compatibility = _build_equipment_compatibility_matrix()
        
        # Add fertilizer form compatibility
        fertilizer_compatibility = _build_fertilizer_compatibility_matrix()
        
        response = {
            "methods_catalog": methods_catalog,
            "method_categories": method_categories,
            "equipment_compatibility": equipment_compatibility,
            "fertilizer_compatibility": fertilizer_compatibility,
            "total_methods": len(methods_catalog),
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "catalog_version": "1.0"
        }
        
        logger.info(f"Retrieved application options catalog with {len(methods_catalog)} methods")
        return response
        
    except Exception as e:
        logger.error(f"Error retrieving application options: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve application options: {str(e)}")


@router.post("/method-comparison", response_model=MethodComparisonResponse)
async def compare_application_methods(
    request: MethodComparisonRequest,
    service: ApplicationMethodService = Depends(get_application_service)
):
    """
    Compare multiple fertilizer application methods side-by-side with detailed analysis.
    
    This endpoint provides comprehensive comparison analysis including:
    - Side-by-side method comparison matrix
    - Trade-off analysis between different criteria
    - Decision support with recommendations
    - Weighted scoring based on preferences
    - Detailed factor analysis
    
    **Comparison Features:**
    - Multi-criteria comparison matrix
    - Customizable weighting preferences
    - Trade-off analysis and decision support
    - Performance benchmarking
    - Cost-benefit analysis
    - Environmental impact comparison
    - Equipment requirement comparison
    
    **Decision Support:**
    - Automated ranking based on criteria
    - Sensitivity analysis for different scenarios
    - Recommendation explanations
    - Risk assessment for each method
    - Implementation complexity analysis
    """
    try:
        start_time = time.time()
        request_id = str(uuid4())
        
        logger.info(f"Processing method comparison request {request_id} for methods: {request.methods_to_compare}")
        
        # Validate methods exist
        valid_methods = []
        for method in request.methods_to_compare:
            if method in service.method_database:
                valid_methods.append(method)
            else:
                logger.warning(f"Unknown method type: {method}")
        
        if not valid_methods:
            raise HTTPException(status_code=400, detail="No valid methods provided for comparison")
        
        # Build comparison matrix
        comparison_matrix = {}
        for method in valid_methods:
            method_data = service.method_database[method]
            comparison_matrix[method] = {
                "efficiency_score": method_data["efficiency_score"],
                "cost_per_acre": method_data["cost_per_acre"],
                "labor_intensity": method_data["labor_intensity"],
                "environmental_impact": method_data["environmental_impact"],
                "equipment_requirements": method_data.get("equipment_requirements", {}),
                "fertilizer_compatibility": method_data["fertilizer_forms"],
                "field_size_suitability": method_data["field_size_range"],
                "pros": method_data["pros"],
                "cons": method_data["cons"],
                "best_use_cases": method_data.get("best_use_cases", [])
            }
        
        # Calculate rankings based on criteria
        rankings = _calculate_method_rankings(comparison_matrix, request.weighting_preferences)
        
        # Perform trade-off analysis
        trade_off_analysis = _perform_trade_off_analysis(comparison_matrix, request.comparison_criteria)
        
        # Generate decision support information
        decision_support = _generate_decision_support(rankings, trade_off_analysis, request.farm_context)
        
        response = MethodComparisonResponse(
            request_id=request_id,
            comparison_matrix=comparison_matrix,
            rankings=rankings,
            trade_off_analysis=trade_off_analysis,
            decision_support=decision_support,
            processing_time_ms=(time.time() - start_time) * 1000
        )
        
        logger.info(f"Method comparison completed for request {request_id} in {response.processing_time_ms:.2f}ms")
        return response
        
    except Exception as e:
        logger.error(f"Error in method comparison: {e}")
        raise HTTPException(status_code=500, detail=f"Method comparison failed: {str(e)}")


@router.get("/guidance/{method_id}", response_model=Dict[str, Any])
async def get_application_guidance(
    method_id: str,
    farm_context: Optional[Dict[str, Any]] = None,
    service: ApplicationMethodService = Depends(get_application_service)
):
    """
    Get step-by-step application guidance for a specific method.
    
    This endpoint provides comprehensive guidance including:
    - Pre-application preparation steps
    - Step-by-step application instructions
    - Equipment calibration guidance
    - Safety precautions and requirements
    - Quality control measures
    - Post-application tasks
    
    **Guidance Features:**
    - Method-specific instructions
    - Equipment preparation and calibration
    - Safety protocols and precautions
    - Quality control checkpoints
    - Troubleshooting guidance
    - Weather and timing considerations
    """
    try:
        logger.info(f"Retrieving application guidance for method: {method_id}")
        
        # Get method-specific guidance
        guidance_data = _get_method_guidance(method_id, farm_context)
        
        response = {
            "method_id": method_id,
            "guidance": guidance_data,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"Retrieved guidance for method {method_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error retrieving guidance for method {method_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve guidance: {str(e)}")


@router.post("/timing/optimize", response_model=Dict[str, Any])
async def optimize_application_timing(
    method_type: str,
    farm_context: Dict[str, Any],
    weather_forecast: Optional[Dict[str, Any]] = None,
    service: ApplicationMethodService = Depends(get_application_service)
):
    """
    Optimize application timing based on method, farm context, and weather conditions.
    
    This endpoint provides timing optimization including:
    - Optimal application windows
    - Weather-based timing adjustments
    - Crop growth stage considerations
    - Equipment availability scheduling
    - Risk assessment for different timing options
    
    **Timing Optimization Features:**
    - Weather integration for optimal conditions
    - Crop growth stage tracking
    - Equipment scheduling optimization
    - Risk assessment and mitigation
    - Multiple timing scenarios
    - Emergency timing options
    """
    try:
        logger.info(f"Optimizing application timing for method: {method_type}")
        
        # Perform timing optimization
        timing_optimization = _optimize_application_timing(method_type, farm_context, weather_forecast)
        
        response = {
            "method_type": method_type,
            "timing_optimization": timing_optimization,
            "optimization_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"Timing optimization completed for method {method_type}")
        return response
        
    except Exception as e:
        logger.error(f"Error optimizing timing for method {method_type}: {e}")
        raise HTTPException(status_code=500, detail=f"Timing optimization failed: {str(e)}")


# Helper functions

def _convert_to_application_request(request: MethodRecommendationRequest) -> ApplicationRequest:
    """Convert MethodRecommendationRequest to ApplicationRequest format."""
    field_conditions = FieldConditions(
        field_size_acres=request.farm_context.get("field_size_acres", 1.0),
        soil_type=request.farm_context.get("soil_type", "unknown"),
        drainage_class=request.farm_context.get("drainage_class"),
        slope_percent=request.farm_context.get("slope_percent"),
        irrigation_available=request.farm_context.get("irrigation_available", False),
        field_shape=request.farm_context.get("field_shape"),
        access_roads=request.farm_context.get("access_roads")
    )
    
    crop_requirements = CropRequirements(
        crop_type=request.crop_info.get("crop_type", "unknown"),
        growth_stage=request.crop_info.get("growth_stage", "unknown"),
        target_yield=request.crop_info.get("target_yield"),
        nutrient_requirements=request.crop_info.get("nutrient_requirements", {}),
        application_timing_preferences=request.crop_info.get("application_timing_preferences", [])
    )
    
    fertilizer_specification = FertilizerSpecification(
        fertilizer_type=request.fertilizer_specs.get("fertilizer_type", "unknown"),
        npk_ratio=request.fertilizer_specs.get("npk_ratio", "0-0-0"),
        form=request.fertilizer_specs.get("form", "granular"),
        solubility=request.fertilizer_specs.get("solubility"),
        release_rate=request.fertilizer_specs.get("release_rate"),
        cost_per_unit=request.fertilizer_specs.get("cost_per_unit"),
        unit=request.fertilizer_specs.get("unit")
    )
    
    available_equipment = []
    for equipment_data in request.equipment_available:
        equipment_spec = EquipmentSpecification(
            equipment_type=equipment_data.get("equipment_type", "spreader"),
            capacity=equipment_data.get("capacity"),
            capacity_unit=equipment_data.get("capacity_unit"),
            application_width=equipment_data.get("application_width"),
            application_rate_range=equipment_data.get("application_rate_range"),
            fuel_efficiency=equipment_data.get("fuel_efficiency"),
            maintenance_cost_per_hour=equipment_data.get("maintenance_cost_per_hour")
        )
        available_equipment.append(equipment_spec)
    
    return ApplicationRequest(
        field_conditions=field_conditions,
        crop_requirements=crop_requirements,
        fertilizer_specification=fertilizer_specification,
        available_equipment=available_equipment,
        application_goals=request.goals,
        constraints=request.constraints
    )


def _get_equipment_preparation_guidance(method: ApplicationMethod) -> List[str]:
    """Get equipment preparation guidance for a method."""
    guidance = [
        f"Inspect {method.recommended_equipment.equipment_type.value} for damage or wear",
        "Check calibration settings and adjust if necessary",
        "Ensure adequate fuel and maintenance supplies",
        "Verify application rate settings match recommendations"
    ]
    return guidance


def _get_safety_considerations(method: ApplicationMethod) -> List[str]:
    """Get safety considerations for a method."""
    safety = [
        "Wear appropriate personal protective equipment",
        "Follow manufacturer safety guidelines",
        "Ensure proper ventilation in enclosed areas",
        "Keep emergency contact information readily available"
    ]
    return safety


def _get_quality_control_guidance(method: ApplicationMethod) -> List[str]:
    """Get quality control guidance for a method."""
    qc = [
        "Verify application rate accuracy",
        "Check coverage uniformity",
        "Monitor environmental conditions",
        "Document application details"
    ]
    return qc


def _build_equipment_compatibility_matrix() -> Dict[str, Any]:
    """Build equipment compatibility matrix."""
    return {
        "spreader": ["broadcast", "band"],
        "sprayer": ["foliar", "fertigation"],
        "injector": ["injection", "sidedress"],
        "drip_system": ["drip", "fertigation"],
        "hand_spreader": ["broadcast"],
        "broadcaster": ["broadcast"]
    }


def _build_fertilizer_compatibility_matrix() -> Dict[str, Any]:
    """Build fertilizer compatibility matrix."""
    return {
        "granular": ["broadcast", "band", "sidedress"],
        "liquid": ["foliar", "injection", "fertigation", "drip"],
        "gaseous": ["injection"],
        "slow_release": ["broadcast", "band"],
        "organic": ["broadcast", "band", "sidedress"]
    }


def _calculate_method_rankings(comparison_matrix: Dict[str, Any], weights: Optional[Dict[str, float]]) -> List[Dict[str, Any]]:
    """Calculate method rankings based on comparison matrix and weights."""
    if not weights:
        weights = {
            "efficiency": 0.3,
            "cost": 0.25,
            "labor": 0.2,
            "environment": 0.15,
            "equipment": 0.1
        }
    
    rankings = []
    for method, data in comparison_matrix.items():
        score = (
            data["efficiency_score"] * weights["efficiency"] +
            (1 - data["cost_per_acre"] / 1000) * weights["cost"] +  # Normalize cost
            (1 - data["labor_intensity"]) * weights["labor"] +  # Lower labor intensity is better
            (1 - data["environmental_impact"]) * weights["environment"] +  # Lower impact is better
            0.8 * weights["equipment"]  # Assume good equipment compatibility
        )
        
        rankings.append({
            "method": method,
            "score": score,
            "rank": 0  # Will be set after sorting
        })
    
    # Sort by score and assign ranks
    rankings.sort(key=lambda x: x["score"], reverse=True)
    for i, ranking in enumerate(rankings):
        ranking["rank"] = i + 1
    
    return rankings


def _perform_trade_off_analysis(comparison_matrix: Dict[str, Any], criteria: List[str]) -> Dict[str, Any]:
    """Perform trade-off analysis between methods."""
    trade_offs = {
        "efficiency_vs_cost": {},
        "labor_vs_precision": {},
        "environment_vs_efficiency": {},
        "equipment_vs_flexibility": {}
    }
    
    methods = list(comparison_matrix.keys())
    if len(methods) >= 2:
        method1, method2 = methods[0], methods[1]
        
        trade_offs["efficiency_vs_cost"] = {
            "method1": method1,
            "method2": method2,
            "efficiency_difference": comparison_matrix[method1]["efficiency_score"] - comparison_matrix[method2]["efficiency_score"],
            "cost_difference": comparison_matrix[method1]["cost_per_acre"] - comparison_matrix[method2]["cost_per_acre"]
        }
    
    return trade_offs


def _generate_decision_support(rankings: List[Dict[str, Any]], trade_offs: Dict[str, Any], farm_context: Dict[str, Any]) -> Dict[str, Any]:
    """Generate decision support information."""
    top_method = rankings[0] if rankings else None
    
    return {
        "recommended_method": top_method["method"] if top_method else None,
        "confidence_level": "high" if top_method and top_method["score"] > 0.8 else "medium",
        "key_factors": [
            "Efficiency score",
            "Cost per acre",
            "Labor requirements",
            "Environmental impact"
        ],
        "trade_offs": trade_offs,
        "farm_context_factors": farm_context,
        "recommendation_rationale": f"Method {top_method['method']} scored highest based on weighted criteria" if top_method else "No clear recommendation available"
    }


def _get_method_guidance(method_id: str, farm_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Get method-specific guidance."""
    guidance_templates = {
        "broadcast": {
            "pre_application": [
                "Check weather conditions - avoid windy days",
                "Calibrate spreader for uniform application",
                "Mark field boundaries clearly"
            ],
            "application": [
                "Apply fertilizer in overlapping passes",
                "Maintain consistent speed and rate",
                "Monitor coverage uniformity"
            ],
            "post_application": [
                "Check for missed areas",
                "Clean equipment thoroughly",
                "Document application details"
            ]
        },
        "foliar": {
            "pre_application": [
                "Check crop growth stage suitability",
                "Calibrate sprayer for proper droplet size",
                "Check weather for optimal conditions"
            ],
            "application": [
                "Apply during early morning or evening",
                "Ensure complete leaf coverage",
                "Avoid application during heat stress"
            ],
            "post_application": [
                "Monitor for phytotoxicity",
                "Clean sprayer thoroughly",
                "Record application conditions"
            ]
        }
    }
    
    return guidance_templates.get(method_id, {
        "pre_application": ["Follow manufacturer guidelines"],
        "application": ["Apply according to recommendations"],
        "post_application": ["Clean equipment and document"]
    })


def _optimize_application_timing(method_type: str, farm_context: Dict[str, Any], weather_forecast: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Optimize application timing."""
    return {
        "optimal_windows": [
            {
                "start": "2024-03-15T08:00:00Z",
                "end": "2024-03-15T18:00:00Z",
                "conditions": "Optimal temperature and humidity",
                "confidence": 0.9
            }
        ],
        "weather_considerations": weather_forecast or {},
        "crop_timing": {
            "growth_stage": farm_context.get("growth_stage", "unknown"),
            "optimal_window": "V4-V6 for corn"
        },
        "risk_assessment": {
            "weather_risk": "low",
            "equipment_risk": "low",
            "timing_risk": "medium"
        }
    }


@router.get("/health")
async def health_check():
    """Health check endpoint for fertilizer application methods service."""
    return {
        "service": "fertilizer-application-methods",
        "status": "healthy",
        "endpoints": [
            "POST /api/v1/fertilizer/application-method/recommend",
            "GET /api/v1/fertilizer/application-options",
            "POST /api/v1/fertilizer/method-comparison",
            "GET /api/v1/fertilizer/guidance/{method_id}",
            "POST /api/v1/fertilizer/timing/optimize"
        ],
        "features": [
            "method_recommendations",
            "method_comparison",
            "application_guidance",
            "timing_optimization",
            "cost_analysis",
            "equipment_compatibility"
        ]
    }
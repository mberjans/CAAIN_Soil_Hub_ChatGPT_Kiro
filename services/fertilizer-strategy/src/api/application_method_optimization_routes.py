"""
Application Method Optimization API Routes

This module provides comprehensive API endpoints for fertilizer application method optimization,
including method selection, efficiency optimization, and cost-benefit analysis.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from typing import List, Dict, Optional, Any
import logging
import asyncio

from ..models.application_method_optimization_models import (
    ApplicationMethodOptimizationRequest,
    ApplicationMethodOptimizationResult,
    ApplicationMethodComparisonRequest,
    ApplicationMethodComparisonResult,
    ApplicationMethodSummary,
    ApplicationMethod,
    FertilizerForm,
    EquipmentType,
    SoilCondition,
    ApplicationConstraints
)
from ..services.application_method_optimization_service import ApplicationMethodOptimizer

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/fertilizer/application-methods", tags=["application-method-optimization"])

# Initialize service
application_method_optimizer = ApplicationMethodOptimizer()


@router.post("/optimize", response_model=ApplicationMethodOptimizationResult)
async def optimize_application_methods(
    request: ApplicationMethodOptimizationRequest,
    background_tasks: BackgroundTasks
):
    """
    Optimize fertilizer application methods based on field conditions and objectives.
    
    This endpoint provides comprehensive application method optimization considering:
    - Method selection optimization based on field conditions
    - Efficiency optimization for nutrient use and application uniformity
    - Cost-benefit analysis including equipment, labor, and fertilizer costs
    - Environmental impact assessment and risk analysis
    - Multi-objective optimization (yield, cost, efficiency, environment)
    - Constraint handling for equipment, labor, and field conditions
    
    **Agricultural Use Cases:**
    - Select optimal application method for specific field conditions
    - Optimize fertilizer efficiency and reduce nutrient losses
    - Balance cost-effectiveness with environmental impact
    - Plan equipment and labor requirements
    - Assess feasibility under various constraints
    
    **Request Parameters:**
    - field_id: Field identifier
    - crop_type: Crop type (corn, soybean, wheat, etc.)
    - fertilizer_requirements: Fertilizer requirements by type (lbs/acre)
    - soil_characteristics: Soil type, pH, organic matter, CEC
    - constraints: Equipment availability, labor, budget, soil conditions
    - optimization_objectives: Yield, cost, efficiency, environmental optimization
    
    **Response:**
    - recommendations: Ranked list of application method recommendations
    - best_method: Best overall application method
    - performance_metrics: Yield impact, costs, efficiency, environmental scores
    - method_comparison: Detailed comparison of all methods
    - key_insights: Key insights from optimization analysis
    - implementation_notes: Implementation guidance and considerations
    """
    try:
        logger.info(f"Received application method optimization request for field {request.field_id}")
        
        result = await application_method_optimizer.optimize_application_methods(request)
        
        logger.info(f"Application method optimization completed for field {request.field_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error in application method optimization: {e}")
        raise HTTPException(status_code=500, detail=f"Application method optimization failed: {str(e)}")


@router.post("/compare", response_model=ApplicationMethodComparisonResult)
async def compare_application_methods(
    request: ApplicationMethodComparisonRequest
):
    """
    Compare specific fertilizer application methods.
    
    This endpoint provides detailed comparison of specific application methods
    for side-by-side analysis and decision making.
    
    **Agricultural Use Cases:**
    - Compare specific methods of interest
    - Evaluate trade-offs between different approaches
    - Make informed decisions between alternatives
    - Assess relative performance across multiple criteria
    
    **Request Parameters:**
    - methods_to_compare: List of specific methods to compare
    - field_characteristics: Field and crop information
    - constraints: Application constraints and limitations
    - comparison_criteria: Which aspects to compare (yield, cost, efficiency, environment)
    
    **Response:**
    - method_comparisons: Detailed comparison of each method
    - comparative_analysis: Side-by-side comparison metrics
    - rankings: Method rankings across different criteria
    - key_differences: Key differences between methods
    - trade_off_analysis: Trade-off analysis between competing objectives
    """
    try:
        logger.info(f"Received application method comparison request for {len(request.methods_to_compare)} methods")
        
        result = await application_method_optimizer.compare_application_methods(request)
        
        logger.info(f"Application method comparison completed")
        return result
        
    except Exception as e:
        logger.error(f"Error in application method comparison: {e}")
        raise HTTPException(status_code=500, detail=f"Application method comparison failed: {str(e)}")


@router.get("/summary/{optimization_id}", response_model=ApplicationMethodSummary)
async def get_application_method_summary(
    optimization_id: str,
    field_id: str = Query(..., description="Field identifier"),
    crop_type: str = Query(..., description="Crop type")
):
    """
    Get summary of application method optimization results.
    
    This endpoint provides a concise summary of optimization results
    for quick reference and decision making.
    
    **Agricultural Use Cases:**
    - Quick reference to optimization results
    - Summary for reporting and documentation
    - Key insights for decision making
    - Implementation guidance
    
    **Response:**
    - best_method: Best application method recommendation
    - performance_summary: Key performance metrics
    - recommendations: Primary recommendation and alternatives
    - key_benefits: Key benefits of recommended method
    - key_risks: Key risks and considerations
    - implementation_notes: Implementation guidance
    """
    try:
        logger.info(f"Retrieving application method summary for optimization {optimization_id}")
        
        summary = await application_method_optimizer.get_application_method_summary(
            optimization_id, field_id, crop_type
        )
        
        logger.info(f"Application method summary retrieved for optimization {optimization_id}")
        return summary
        
    except Exception as e:
        logger.error(f"Error retrieving application method summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve summary: {str(e)}")


@router.get("/methods", response_model=List[Dict[str, Any]])
async def get_available_application_methods():
    """
    Get list of available fertilizer application methods with characteristics.
    
    This endpoint provides information about all available application methods
    including their characteristics, requirements, and typical use cases.
    
    **Agricultural Use Cases:**
    - Understand available application options
    - Learn about method characteristics
    - Plan equipment and resource requirements
    - Make informed method selections
    
    **Response:**
    - List of application methods with detailed characteristics
    - Equipment requirements for each method
    - Typical use cases and applications
    - Efficiency and cost characteristics
    """
    try:
        logger.info("Retrieving available application methods")
        
        methods_info = [
            {
                "method": ApplicationMethod.BROADCAST.value,
                "name": "Broadcast",
                "description": "Surface application of fertilizer across the field",
                "equipment_required": [EquipmentType.BROADCASTER.value],
                "typical_use": "Pre-plant or early season application",
                "efficiency": "Moderate",
                "cost": "Low",
                "environmental_impact": "Moderate"
            },
            {
                "method": ApplicationMethod.BROADCAST_INCORPORATED.value,
                "name": "Broadcast Incorporated",
                "description": "Surface application followed by incorporation into soil",
                "equipment_required": [EquipmentType.BROADCASTER.value, EquipmentType.CONVENTIONAL_TILLAGE.value],
                "typical_use": "Pre-plant application with tillage",
                "efficiency": "Good",
                "cost": "Moderate",
                "environmental_impact": "Moderate"
            },
            {
                "method": ApplicationMethod.BANDED.value,
                "name": "Banded",
                "description": "Placement of fertilizer in bands near seed or plant roots",
                "equipment_required": [EquipmentType.PLANTER_MOUNTED.value],
                "typical_use": "At planting or early season",
                "efficiency": "High",
                "cost": "Moderate",
                "environmental_impact": "Low"
            },
            {
                "method": ApplicationMethod.SIDE_DRESS.value,
                "name": "Side Dress",
                "description": "Application of fertilizer to the side of growing plants",
                "equipment_required": [EquipmentType.SIDE_DRESS_BAR.value],
                "typical_use": "Early to mid-season application",
                "efficiency": "High",
                "cost": "Moderate-High",
                "environmental_impact": "Low"
            },
            {
                "method": ApplicationMethod.FOLIAR.value,
                "name": "Foliar",
                "description": "Application of fertilizer directly to plant leaves",
                "equipment_required": [EquipmentType.SPRAYER.value],
                "typical_use": "Mid to late season application",
                "efficiency": "Very High",
                "cost": "High",
                "environmental_impact": "Very Low"
            },
            {
                "method": ApplicationMethod.FERTIGATION.value,
                "name": "Fertigation",
                "description": "Application of fertilizer through irrigation system",
                "equipment_required": [EquipmentType.IRRIGATION_SYSTEM.value],
                "typical_use": "Throughout growing season",
                "efficiency": "High",
                "cost": "Low",
                "environmental_impact": "Low"
            },
            {
                "method": ApplicationMethod.INJECTION.value,
                "name": "Injection",
                "description": "Direct injection of fertilizer into soil",
                "equipment_required": [EquipmentType.INJECTION_SYSTEM.value],
                "typical_use": "Pre-plant or early season",
                "efficiency": "Very High",
                "cost": "High",
                "environmental_impact": "Very Low"
            },
            {
                "method": ApplicationMethod.STRIP_TILL.value,
                "name": "Strip Till",
                "description": "Tillage and fertilizer application in strips",
                "equipment_required": [EquipmentType.STRIP_TILL_TOOLBAR.value],
                "typical_use": "Pre-plant application",
                "efficiency": "Good",
                "cost": "High",
                "environmental_impact": "Moderate"
            },
            {
                "method": ApplicationMethod.NO_TILL.value,
                "name": "No Till",
                "description": "Application without soil disturbance",
                "equipment_required": [EquipmentType.PLANTER_MOUNTED.value],
                "typical_use": "At planting or early season",
                "efficiency": "Good",
                "cost": "Low",
                "environmental_impact": "Very Low"
            },
            {
                "method": ApplicationMethod.CONVENTIONAL_TILL.value,
                "name": "Conventional Till",
                "description": "Application with conventional tillage",
                "equipment_required": [EquipmentType.CONVENTIONAL_TILLAGE.value],
                "typical_use": "Pre-plant application",
                "efficiency": "Good",
                "cost": "Moderate",
                "environmental_impact": "High"
            }
        ]
        
        logger.info(f"Retrieved {len(methods_info)} application methods")
        return methods_info
        
    except Exception as e:
        logger.error(f"Error retrieving application methods: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve application methods: {str(e)}")


@router.get("/fertilizer-forms", response_model=List[Dict[str, Any]])
async def get_available_fertilizer_forms():
    """
    Get list of available fertilizer forms for application methods.
    
    This endpoint provides information about fertilizer forms
    and their compatibility with different application methods.
    
    **Agricultural Use Cases:**
    - Understand fertilizer form options
    - Plan fertilizer procurement
    - Match forms to application methods
    - Optimize fertilizer handling and storage
    
    **Response:**
    - List of fertilizer forms with characteristics
    - Compatibility with application methods
    - Handling and storage requirements
    - Cost and efficiency considerations
    """
    try:
        logger.info("Retrieving available fertilizer forms")
        
        forms_info = [
            {
                "form": FertilizerForm.GRANULAR.value,
                "name": "Granular",
                "description": "Solid fertilizer in granular form",
                "compatible_methods": [
                    ApplicationMethod.BROADCAST.value,
                    ApplicationMethod.BROADCAST_INCORPORATED.value,
                    ApplicationMethod.BANDED.value,
                    ApplicationMethod.SIDE_DRESS.value,
                    ApplicationMethod.STRIP_TILL.value,
                    ApplicationMethod.NO_TILL.value,
                    ApplicationMethod.CONVENTIONAL_TILL.value
                ],
                "handling": "Easy to handle and store",
                "cost": "Low to Moderate",
                "efficiency": "Good"
            },
            {
                "form": FertilizerForm.LIQUID.value,
                "name": "Liquid",
                "description": "Liquid fertilizer solution or suspension",
                "compatible_methods": [
                    ApplicationMethod.FOLIAR.value,
                    ApplicationMethod.FERTIGATION.value,
                    ApplicationMethod.INJECTION.value,
                    ApplicationMethod.SIDE_DRESS.value
                ],
                "handling": "Requires specialized equipment",
                "cost": "Moderate to High",
                "efficiency": "High"
            },
            {
                "form": FertilizerForm.GASEOUS.value,
                "name": "Gaseous",
                "description": "Gaseous fertilizer (e.g., anhydrous ammonia)",
                "compatible_methods": [
                    ApplicationMethod.INJECTION.value,
                    ApplicationMethod.SIDE_DRESS.value
                ],
                "handling": "Requires specialized equipment and safety measures",
                "cost": "Low",
                "efficiency": "Very High"
            },
            {
                "form": FertilizerForm.SLURRY.value,
                "name": "Slurry",
                "description": "Thick liquid fertilizer mixture",
                "compatible_methods": [
                    ApplicationMethod.INJECTION.value,
                    ApplicationMethod.SIDE_DRESS.value
                ],
                "handling": "Requires specialized equipment",
                "cost": "Moderate",
                "efficiency": "High"
            },
            {
                "form": FertilizerForm.POWDER.value,
                "name": "Powder",
                "description": "Fine powder fertilizer",
                "compatible_methods": [
                    ApplicationMethod.BROADCAST.value,
                    ApplicationMethod.FOLIAR.value
                ],
                "handling": "Requires careful handling to avoid dust",
                "cost": "Moderate",
                "efficiency": "Good"
            }
        ]
        
        logger.info(f"Retrieved {len(forms_info)} fertilizer forms")
        return forms_info
        
    except Exception as e:
        logger.error(f"Error retrieving fertilizer forms: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve fertilizer forms: {str(e)}")


@router.get("/equipment-types", response_model=List[Dict[str, Any]])
async def get_available_equipment_types():
    """
    Get list of available equipment types for application methods.
    
    This endpoint provides information about equipment types
    required for different application methods.
    
    **Agricultural Use Cases:**
    - Plan equipment requirements
    - Assess equipment compatibility
    - Budget for equipment needs
    - Optimize equipment utilization
    
    **Response:**
    - List of equipment types with characteristics
    - Compatibility with application methods
    - Cost and maintenance requirements
    - Performance characteristics
    """
    try:
        logger.info("Retrieving available equipment types")
        
        equipment_info = [
            {
                "equipment_type": EquipmentType.BROADCASTER.value,
                "name": "Broadcaster",
                "description": "Equipment for broadcasting fertilizer across field surface",
                "compatible_methods": [
                    ApplicationMethod.BROADCAST.value,
                    ApplicationMethod.BROADCAST_INCORPORATED.value
                ],
                "cost_range": "Low to Moderate",
                "maintenance": "Low",
                "efficiency": "Moderate"
            },
            {
                "equipment_type": EquipmentType.PLANTER_MOUNTED.value,
                "name": "Planter Mounted",
                "description": "Fertilizer application equipment mounted on planter",
                "compatible_methods": [
                    ApplicationMethod.BANDED.value,
                    ApplicationMethod.NO_TILL.value
                ],
                "cost_range": "Moderate",
                "maintenance": "Moderate",
                "efficiency": "High"
            },
            {
                "equipment_type": EquipmentType.SIDE_DRESS_BAR.value,
                "name": "Side Dress Bar",
                "description": "Equipment for side-dressing fertilizer to growing plants",
                "compatible_methods": [
                    ApplicationMethod.SIDE_DRESS.value
                ],
                "cost_range": "Moderate to High",
                "maintenance": "Moderate",
                "efficiency": "High"
            },
            {
                "equipment_type": EquipmentType.SPRAYER.value,
                "name": "Sprayer",
                "description": "Equipment for foliar application of liquid fertilizers",
                "compatible_methods": [
                    ApplicationMethod.FOLIAR.value
                ],
                "cost_range": "High",
                "maintenance": "High",
                "efficiency": "Very High"
            },
            {
                "equipment_type": EquipmentType.IRRIGATION_SYSTEM.value,
                "name": "Irrigation System",
                "description": "Irrigation system for fertigation",
                "compatible_methods": [
                    ApplicationMethod.FERTIGATION.value
                ],
                "cost_range": "Very High",
                "maintenance": "High",
                "efficiency": "High"
            },
            {
                "equipment_type": EquipmentType.INJECTION_SYSTEM.value,
                "name": "Injection System",
                "description": "Equipment for injecting fertilizer into soil",
                "compatible_methods": [
                    ApplicationMethod.INJECTION.value
                ],
                "cost_range": "Very High",
                "maintenance": "High",
                "efficiency": "Very High"
            },
            {
                "equipment_type": EquipmentType.STRIP_TILL_TOOLBAR.value,
                "name": "Strip Till Toolbar",
                "description": "Equipment for strip tillage and fertilizer application",
                "compatible_methods": [
                    ApplicationMethod.STRIP_TILL.value
                ],
                "cost_range": "High",
                "maintenance": "High",
                "efficiency": "Good"
            },
            {
                "equipment_type": EquipmentType.CONVENTIONAL_TILLAGE.value,
                "name": "Conventional Tillage",
                "description": "Equipment for conventional tillage operations",
                "compatible_methods": [
                    ApplicationMethod.CONVENTIONAL_TILL.value,
                    ApplicationMethod.BROADCAST_INCORPORATED.value
                ],
                "cost_range": "Moderate to High",
                "maintenance": "Moderate",
                "efficiency": "Good"
            }
        ]
        
        logger.info(f"Retrieved {len(equipment_info)} equipment types")
        return equipment_info
        
    except Exception as e:
        logger.error(f"Error retrieving equipment types: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve equipment types: {str(e)}")


@router.get("/soil-conditions", response_model=List[Dict[str, Any]])
async def get_soil_condition_compatibility():
    """
    Get soil condition compatibility with application methods.
    
    This endpoint provides information about how different soil conditions
    affect the feasibility and effectiveness of application methods.
    
    **Agricultural Use Cases:**
    - Assess method feasibility under current soil conditions
    - Plan application timing based on soil conditions
    - Optimize method selection for soil type
    - Minimize soil disturbance and compaction
    
    **Response:**
    - Soil condition types and characteristics
    - Compatible application methods for each condition
    - Efficiency impacts of soil conditions
    - Recommendations for soil condition management
    """
    try:
        logger.info("Retrieving soil condition compatibility")
        
        soil_conditions_info = [
            {
                "condition": SoilCondition.DRY.value,
                "name": "Dry",
                "description": "Soil with low moisture content",
                "compatible_methods": [
                    ApplicationMethod.BROADCAST.value,
                    ApplicationMethod.BANDED.value,
                    ApplicationMethod.SIDE_DRESS.value,
                    ApplicationMethod.FOLIAR.value,
                    ApplicationMethod.FERTIGATION.value,
                    ApplicationMethod.INJECTION.value
                ],
                "efficiency_impact": "Moderate",
                "recommendations": ["Consider irrigation", "Use methods that minimize dust"]
            },
            {
                "condition": SoilCondition.MOIST.value,
                "name": "Moist",
                "description": "Soil with optimal moisture content",
                "compatible_methods": [
                    ApplicationMethod.BROADCAST.value,
                    ApplicationMethod.BROADCAST_INCORPORATED.value,
                    ApplicationMethod.BANDED.value,
                    ApplicationMethod.SIDE_DRESS.value,
                    ApplicationMethod.FOLIAR.value,
                    ApplicationMethod.FERTIGATION.value,
                    ApplicationMethod.INJECTION.value,
                    ApplicationMethod.STRIP_TILL.value
                ],
                "efficiency_impact": "Optimal",
                "recommendations": ["Best conditions for most methods", "Optimal timing for application"]
            },
            {
                "condition": SoilCondition.WET.value,
                "name": "Wet",
                "description": "Soil with high moisture content",
                "compatible_methods": [
                    ApplicationMethod.FOLIAR.value,
                    ApplicationMethod.FERTIGATION.value,
                    ApplicationMethod.INJECTION.value
                ],
                "efficiency_impact": "Reduced",
                "recommendations": ["Avoid soil disturbance", "Use methods that don't require soil contact"]
            },
            {
                "condition": SoilCondition.FROZEN.value,
                "name": "Frozen",
                "description": "Soil that is frozen",
                "compatible_methods": [
                    ApplicationMethod.FOLIAR.value
                ],
                "efficiency_impact": "Very Reduced",
                "recommendations": ["Wait for thaw", "Use only foliar methods if necessary"]
            },
            {
                "condition": SoilCondition.COMPACTED.value,
                "name": "Compacted",
                "description": "Soil with reduced pore space",
                "compatible_methods": [
                    ApplicationMethod.BROADCAST_INCORPORATED.value,
                    ApplicationMethod.STRIP_TILL.value,
                    ApplicationMethod.CONVENTIONAL_TILL.value
                ],
                "efficiency_impact": "Reduced",
                "recommendations": ["Consider tillage to reduce compaction", "Use methods that improve soil structure"]
            },
            {
                "condition": SoilCondition.LOOSE.value,
                "name": "Loose",
                "description": "Soil with good structure and pore space",
                "compatible_methods": [
                    ApplicationMethod.BROADCAST.value,
                    ApplicationMethod.BANDED.value,
                    ApplicationMethod.SIDE_DRESS.value,
                    ApplicationMethod.FOLIAR.value,
                    ApplicationMethod.FERTIGATION.value,
                    ApplicationMethod.INJECTION.value,
                    ApplicationMethod.NO_TILL.value
                ],
                "efficiency_impact": "Optimal",
                "recommendations": ["Excellent conditions for most methods", "Consider conservation tillage"]
            }
        ]
        
        logger.info(f"Retrieved {len(soil_conditions_info)} soil conditions")
        return soil_conditions_info
        
    except Exception as e:
        logger.error(f"Error retrieving soil conditions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve soil conditions: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for application method optimization service."""
    return {
        "service": "application-method-optimization",
        "status": "healthy",
        "version": "1.0.0",
        "features": [
            "method_selection_optimization",
            "efficiency_optimization",
            "cost_benefit_analysis",
            "environmental_impact_assessment",
            "multi_objective_optimization",
            "constraint_handling",
            "method_comparison",
            "equipment_compatibility",
            "soil_condition_analysis",
            "fertilizer_form_optimization"
        ]
    }
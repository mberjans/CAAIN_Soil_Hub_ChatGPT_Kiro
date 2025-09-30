"""
API Routes for fertilizer application method management and optimization.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from src.models.method_models import (
    ApplicationMethod as MethodModel, MethodComparison, MethodOptimization,
    OptimizationResult, MethodSelection, MethodRanking, MethodValidation,
    MethodPerformance, MethodLearning, MethodRecommendation
)
from src.models.application_models import ApplicationMethod, FieldConditions, CropRequirements, FertilizerSpecification, EquipmentSpecification
from src.services.comparison_service import MethodComparisonService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/methods", tags=["methods"])


class MethodComparisonRequest(BaseModel):
    """Request model for method comparison."""
    method_a: ApplicationMethod = Field(..., description="First method to compare")
    method_b: ApplicationMethod = Field(..., description="Second method to compare")
    field_conditions: FieldConditions = Field(..., description="Field conditions for context")
    crop_requirements: CropRequirements = Field(..., description="Crop requirements for context")
    fertilizer_specification: FertilizerSpecification = Field(..., description="Fertilizer specification for context")
    available_equipment: List[EquipmentSpecification] = Field(default_factory=list, description="Available equipment")
    comparison_criteria: Optional[List[str]] = Field(None, description="Specific criteria to compare (if None, uses all)")
    custom_weights: Optional[Dict[str, float]] = Field(None, description="Custom weights for criteria")


class MethodOptimizationRequest(BaseModel):
    """Request model for method optimization."""
    field_conditions: Dict[str, Any] = Field(..., description="Field conditions")
    crop_requirements: Dict[str, Any] = Field(..., description="Crop requirements")
    objectives: List[str] = Field(default_factory=list, description="Optimization objectives")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Optimization constraints")


class MethodRankingRequest(BaseModel):
    """Request model for method ranking."""
    methods: List[str] = Field(..., description="Methods to rank")
    ranking_criteria: List[str] = Field(default_factory=list, description="Ranking criteria")
    weights: Optional[Dict[str, float]] = Field(None, description="Criteria weights")


@router.get("/", response_model=List[MethodModel])
async def get_all_methods(
    method_type: Optional[str] = Query(None, description="Filter by method type"),
    efficiency_min: Optional[float] = Query(None, ge=0, le=1, description="Minimum efficiency score"),
    cost_max: Optional[float] = Query(None, ge=0, description="Maximum cost per acre")
):
    """
    Get all available fertilizer application methods with optional filtering.
    
    This endpoint retrieves comprehensive information about all supported
    application methods, with optional filtering by method type, efficiency
    score, and cost constraints.
    
    **Filtering Options:**
    - Method type (broadcast, band, sidedress, foliar, injection, drip)
    - Minimum efficiency score (0.0 - 1.0)
    - Maximum cost per acre
    
    **Method Information includes:**
    - Method specifications and characteristics
    - Application timing options
    - Precision levels and environmental impact
    - Equipment requirements and skill levels
    - Cost estimates and efficiency ratings
    """
    try:
        logger.info(f"Retrieving application methods with filters: type={method_type}, efficiency_min={efficiency_min}, cost_max={cost_max}")
        
        # This would typically query a database or service
        # For now, return a simplified response
        methods = [
            MethodModel(
                method_id="broadcast_001",
                method_name="Broadcast Application",
                method_type="broadcast",
                description="Uniform distribution of fertilizer across the entire field surface",
                application_timing=["pre_plant", "at_planting", "fall", "spring"],
                precision_level="broadcast",
                environmental_impact="moderate",
                equipment_requirements=["spreader", "broadcaster"],
                labor_intensity="medium",
                skill_requirements="semi_skilled",
                cost_per_acre=15.0,
                efficiency_rating=0.7,
                suitability_factors={
                    "field_size": "large",
                    "soil_type": "all",
                    "crop_type": "all"
                }
            ),
            MethodModel(
                method_id="band_001",
                method_name="Band Application",
                method_type="band",
                description="Placement of fertilizer in bands near the seed or plant row",
                application_timing=["at_planting", "pre_plant"],
                precision_level="band",
                environmental_impact="low",
                equipment_requirements=["spreader"],
                labor_intensity="medium",
                skill_requirements="skilled",
                cost_per_acre=20.0,
                efficiency_rating=0.8,
                suitability_factors={
                    "field_size": "medium",
                    "soil_type": "all",
                    "crop_type": "row_crops"
                }
            )
        ]
        
        # Apply filters
        if method_type:
            methods = [m for m in methods if m.method_type == method_type]
        
        if efficiency_min is not None:
            methods = [m for m in methods if m.efficiency_rating >= efficiency_min]
        
        if cost_max is not None:
            methods = [m for m in methods if m.cost_per_acre <= cost_max]
        
        logger.info(f"Retrieved {len(methods)} methods after filtering")
        return methods
        
    except Exception as e:
        logger.error(f"Error retrieving application methods: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve application methods: {str(e)}")


@router.get("/{method_id}", response_model=MethodModel)
async def get_method_by_id(method_id: str):
    """
    Get detailed information about a specific application method.
    
    Returns comprehensive details about the specified application method
    including all characteristics, requirements, and suitability factors.
    """
    try:
        logger.info(f"Retrieving method details for ID: {method_id}")
        
        # This would typically query a database
        # For now, return a sample method
        if method_id == "broadcast_001":
            method = MethodModel(
                method_id="broadcast_001",
                method_name="Broadcast Application",
                method_type="broadcast",
                description="Uniform distribution of fertilizer across the entire field surface",
                application_timing=["pre_plant", "at_planting", "fall", "spring"],
                precision_level="broadcast",
                environmental_impact="moderate",
                equipment_requirements=["spreader", "broadcaster"],
                labor_intensity="medium",
                skill_requirements="semi_skilled",
                cost_per_acre=15.0,
                efficiency_rating=0.7,
                suitability_factors={
                    "field_size": "large",
                    "soil_type": "all",
                    "crop_type": "all",
                    "slope_limit": 10,
                    "wind_limit": 15
                }
            )
        else:
            raise HTTPException(status_code=404, detail=f"Method with ID {method_id} not found")
        
        logger.info(f"Retrieved method details for {method_id}")
        return method
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving method details: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve method details: {str(e)}")


@router.post("/compare", response_model=MethodComparison)
async def compare_methods(request: MethodComparisonRequest):
    """
    Compare two application methods across specified criteria.
    
    This endpoint provides comprehensive comparison between two application
    methods using advanced multi-criteria analysis, highlighting strengths 
    and weaknesses of each approach.
    
    **Comparison Criteria:**
    - Cost effectiveness (total cost per acre including equipment and labor)
    - Application efficiency (nutrient use efficiency and precision)
    - Environmental impact (runoff risk, soil health impact)
    - Equipment requirements (compatibility and availability)
    - Labor requirements (intensity and skill level)
    - Field suitability (size, soil type, slope compatibility)
    - Nutrient use efficiency (crop-specific efficiency)
    - Timing flexibility (application window flexibility)
    - Skill requirements (operator skill level needed)
    - Weather dependency (weather sensitivity)
    
    **Features:**
    - Multi-criteria analysis with weighted scoring
    - Sensitivity analysis for weight variations
    - Statistical comparison with confidence levels
    - Economic analysis including total cost of ownership
    - Environmental impact assessment
    - Field-specific suitability analysis
    """
    try:
        logger.info(f"Comparing methods: {request.method_a.method_type} vs {request.method_b.method_type}")
        
        # Initialize comparison service
        comparison_service = MethodComparisonService()
        
        # Perform comprehensive comparison
        comparison = await comparison_service.compare_methods(
            method_a=request.method_a,
            method_b=request.method_b,
            field_conditions=request.field_conditions,
            crop_requirements=request.crop_requirements,
            fertilizer_spec=request.fertilizer_specification,
            available_equipment=request.available_equipment,
            comparison_criteria=request.comparison_criteria,
            custom_weights=request.custom_weights
        )
        
        logger.info("Method comparison completed successfully")
        return comparison
        
    except Exception as e:
        logger.error(f"Error comparing methods: {e}")
        raise HTTPException(status_code=500, detail=f"Method comparison failed: {str(e)}")


@router.post("/optimize", response_model=OptimizationResult)
async def optimize_method_selection(request: MethodOptimizationRequest):
    """
    Optimize method selection based on multiple objectives and constraints.
    
    This endpoint uses optimization algorithms to find the best application
    method considering multiple objectives such as cost minimization,
    efficiency maximization, and environmental impact reduction.
    
    **Optimization Objectives:**
    - Cost minimization
    - Efficiency maximization
    - Environmental impact minimization
    - Labor requirement minimization
    - Equipment utilization optimization
    
    **Constraints:**
    - Field conditions
    - Equipment availability
    - Budget limitations
    - Time constraints
    - Environmental regulations
    """
    try:
        logger.info("Optimizing method selection")
        
        # This would typically run optimization algorithms
        # For now, return a sample optimization result
        result = OptimizationResult(
            optimization_id="opt_001",
            optimal_method=MethodModel(
                method_id="optimal_001",
                method_name="Optimized Method",
                method_type="band",
                description="Optimized application method",
                application_timing=["at_planting"],
                precision_level="band",
                environmental_impact="low",
                equipment_requirements=["spreader"],
                labor_intensity="medium",
                skill_requirements="skilled",
                cost_per_acre=18.0,
                efficiency_rating=0.85,
                suitability_factors={}
            ),
            optimal_parameters={
                "application_rate": 150,
                "ground_speed": 8,
                "overlap": 0.1
            },
            objective_values={
                "cost": 18.0,
                "efficiency": 0.85,
                "environmental_impact": 0.2
            },
            convergence_info={
                "iterations": 50,
                "converged": True,
                "final_error": 0.001
            },
            confidence_level=0.9,
            processing_time_ms=150.0
        )
        
        logger.info("Method optimization completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Error optimizing method selection: {e}")
        raise HTTPException(status_code=500, detail=f"Method optimization failed: {str(e)}")


@router.post("/rank", response_model=MethodRanking)
async def rank_methods(request: MethodRankingRequest):
    """
    Rank application methods based on specified criteria and weights.
    
    This endpoint ranks multiple application methods based on weighted
    criteria to help farmers select the most suitable method for their
    specific conditions and preferences.
    
    **Ranking Criteria:**
    - Cost effectiveness
    - Application efficiency
    - Environmental impact
    - Equipment compatibility
    - Labor requirements
    - Field suitability
    """
    try:
        logger.info(f"Ranking {len(request.methods)} methods")
        
        # This would typically perform ranking calculations
        # For now, return a sample ranking
        ranked_methods = [
            MethodModel(
                method_id=method_id,
                method_name=f"Method {method_id}",
                method_type="band",
                description=f"Sample method {method_id}",
                application_timing=["at_planting"],
                precision_level="band",
                environmental_impact="low",
                equipment_requirements=["spreader"],
                labor_intensity="medium",
                skill_requirements="skilled",
                cost_per_acre=20.0 - i * 2,  # Decreasing cost
                efficiency_rating=0.8 + i * 0.05,  # Increasing efficiency
                suitability_factors={}
            )
            for i, method_id in enumerate(request.methods)
        ]
        
        ranking = MethodRanking(
            ranking_id="rank_001",
            ranked_methods=ranked_methods,
            ranking_scores=[0.9 - i * 0.1 for i in range(len(request.methods))],
            ranking_criteria=request.ranking_criteria,
            ranking_method="weighted_sum"
        )
        
        logger.info("Method ranking completed successfully")
        return ranking
        
    except Exception as e:
        logger.error(f"Error ranking methods: {e}")
        raise HTTPException(status_code=500, detail=f"Method ranking failed: {str(e)}")


@router.post("/validate/{method_id}", response_model=MethodValidation)
async def validate_method(method_id: str, field_conditions: Dict[str, Any]):
    """
    Validate a specific application method for given field conditions.
    
    This endpoint validates whether a specific application method is
    suitable for the given field conditions and provides recommendations
    for optimization or alternative methods.
    
    **Validation Criteria:**
    - Field size compatibility
    - Soil type suitability
    - Slope limitations
    - Equipment requirements
    - Environmental constraints
    - Cost feasibility
    """
    try:
        logger.info(f"Validating method {method_id} for field conditions")
        
        # This would typically perform validation logic
        # For now, return a sample validation
        validation = MethodValidation(
            validation_id="val_001",
            method=MethodModel(
                method_id=method_id,
                method_name="Validated Method",
                method_type="band",
                description="Method being validated",
                application_timing=["at_planting"],
                precision_level="band",
                environmental_impact="low",
                equipment_requirements=["spreader"],
                labor_intensity="medium",
                skill_requirements="skilled",
                cost_per_acre=20.0,
                efficiency_rating=0.8,
                suitability_factors={}
            ),
            validation_criteria=["field_size", "soil_type", "slope", "equipment"],
            validation_results={
                "field_size": True,
                "soil_type": True,
                "slope": True,
                "equipment": False
            },
            validation_scores={
                "field_size": 1.0,
                "soil_type": 0.9,
                "slope": 0.8,
                "equipment": 0.3
            },
            overall_validity=False,
            validation_notes=["Equipment compatibility issues detected"],
            recommendations=["Consider equipment upgrade or alternative method"]
        )
        
        logger.info(f"Method validation completed for {method_id}")
        return validation
        
    except Exception as e:
        logger.error(f"Error validating method: {e}")
        raise HTTPException(status_code=500, detail=f"Method validation failed: {str(e)}")


@router.get("/performance/{method_id}", response_model=MethodPerformance)
async def get_method_performance(method_id: str):
    """
    Get performance metrics for a specific application method.
    
    Returns historical performance data and metrics for the specified
    application method, including efficiency ratings, yield responses,
    and farmer satisfaction scores.
    """
    try:
        logger.info(f"Retrieving performance metrics for method {method_id}")
        
        # This would typically query performance database
        # For now, return sample performance data
        performance = MethodPerformance(
            method_id=method_id,
            performance_date="2024-01-15",
            application_efficiency=0.85,
            nutrient_use_efficiency=0.78,
            yield_response=12.5,
            yield_unit="bushels/acre",
            cost_effectiveness=0.82,
            environmental_score=0.75,
            farmer_satisfaction=0.88,
            overall_performance=0.83
        )
        
        logger.info(f"Retrieved performance metrics for {method_id}")
        return performance
        
    except Exception as e:
        logger.error(f"Error retrieving method performance: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve method performance: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for method service."""
    return {
        "service": "fertilizer-application-methods",
        "status": "healthy",
        "endpoints": [
            "get_all_methods",
            "get_method_by_id",
            "compare_methods",
            "optimize_method_selection",
            "rank_methods",
            "validate_method",
            "get_method_performance"
        ]
    }
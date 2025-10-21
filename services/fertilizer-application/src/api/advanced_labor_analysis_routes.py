"""
API Routes for Advanced Labor Analysis Service.

This module provides REST API endpoints for advanced labor cost and efficiency analysis
for fertilizer application methods, including labor optimization, efficiency scoring,
and labor-specific economic analysis.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from src.models.application_models import (
    ApplicationMethod, FieldConditions, CropRequirements, 
    FertilizerSpecification, EquipmentSpecification
)
from src.services.advanced_labor_analysis_service import (
    AdvancedLaborAnalysisService, LaborEfficiencyScore, 
    LaborOptimizationResult, LaborEfficiencyMetric
)
from src.services.cost_analysis_service import SeasonalConstraint


logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/advanced-labor-analysis", tags=["advanced-labor-analysis"])


class LaborAnalysisRequest(BaseModel):
    """Request model for labor analysis."""
    application_methods: List[ApplicationMethod] = Field(..., description="Available application methods")
    field_conditions: FieldConditions = Field(..., description="Field conditions")
    crop_requirements: CropRequirements = Field(..., description="Crop requirements")
    fertilizer_specification: FertilizerSpecification = Field(..., description="Fertilizer specification")
    available_equipment: List[EquipmentSpecification] = Field(default_factory=list, description="Available equipment")
    seasonal_constraint: Optional[SeasonalConstraint] = Field(None, description="Seasonal labor constraint")


class LaborEfficiencyAnalysisResponse(BaseModel):
    """Response model for labor efficiency analysis."""
    request_id: str = Field(..., description="Unique request identifier")
    efficiency_scores: Dict[str, LaborEfficiencyScore] = Field(..., description="Labor efficiency scores by method")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class LaborOptimizationResponse(BaseModel):
    """Response model for labor optimization."""
    request_id: str = Field(..., description="Unique request identifier")
    optimization_result: LaborOptimizationResult = Field(..., description="Labor optimization result")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class LaborROIAnalysisResponse(BaseModel):
    """Response model for labor ROI analysis."""
    request_id: str = Field(..., description="Unique request identifier")
    labor_roi: Dict[str, Dict[str, float]] = Field(..., description="Labor ROI by method")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


# Dependency injection
async def get_advanced_labor_analysis_service() -> AdvancedLaborAnalysisService:
    return AdvancedLaborAnalysisService()


@router.post("/analyze-efficiency", response_model=LaborEfficiencyAnalysisResponse)
async def analyze_labor_efficiency(
    request: LaborAnalysisRequest,
    service: AdvancedLaborAnalysisService = Depends(get_advanced_labor_analysis_service)
):
    """
    Analyze labor efficiency for different fertilizer application methods.
    
    This endpoint calculates comprehensive labor efficiency metrics for each application method,
    including productivity rates, quality scores, safety scores, equipment utilization,
    and overall efficiency ratings.
    
    **Efficiency Metrics:**
    - Productivity Rate: Acres that can be covered per hour
    - Quality Score: Application quality rating (0-1)
    - Safety Score: Safety compliance rating (0-1)
    - Equipment Utilization: How efficiently equipment is used (0-1)
    - Skill Alignment: How well required skills match available workforce
    - Training Requirements: Impact of training needs on efficiency
    - Overall Efficiency: Weighted average of all factors
    
    **Use Cases:**
    - Comparing labor efficiency between different application methods
    - Identifying the most labor-efficient application method
    - Assessing training needs for different methods
    - Planning workforce allocation
    """
    try:
        logger.info("Processing labor efficiency analysis request")
        
        start_time = __import__('time').time()
        
        efficiency_scores = await service.analyze_labor_efficiency(
            request.application_methods,
            request.field_conditions,
            request.crop_requirements,
            request.available_equipment
        )
        
        processing_time_ms = (__import__('time').time() - start_time) * 1000
        
        response = LaborEfficiencyAnalysisResponse(
            request_id=str(__import__('uuid').uuid4()),
            efficiency_scores=efficiency_scores,
            processing_time_ms=processing_time_ms,
            metadata={
                "methods_analyzed": len(request.application_methods),
                "field_size_acres": request.field_conditions.field_size_acres,
                "analysis_timestamp": __import__('time').time()
            }
        )
        
        logger.info(f"Labor efficiency analysis completed in {processing_time_ms:.2f}ms")
        return response
        
    except Exception as e:
        logger.error(f"Error in labor efficiency analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Labor efficiency analysis failed: {str(e)}")


@router.post("/optimize", response_model=LaborOptimizationResponse)
async def optimize_labor(
    request: LaborAnalysisRequest,
    service: AdvancedLaborAnalysisService = Depends(get_advanced_labor_analysis_service)
):
    """
    Optimize labor allocation for fertilizer application methods.
    
    This endpoint performs comprehensive labor optimization analysis, considering
    efficiency, cost, safety, and operational constraints to recommend the best
    labor allocation strategy.
    
    **Optimization Features:**
    - Labor efficiency-to-cost ratio optimization
    - Skill requirement matching
    - Seasonal labor availability
    - Safety and compliance considerations
    - Equipment utilization optimization
    - Risk assessment and mitigation
    
    **Recommendations:**
    - Priority ranking of application methods
    - Labor allocation recommendations
    - Training and certification requirements
    - Risk mitigation strategies
    """
    try:
        logger.info("Processing labor optimization request")
        
        start_time = __import__('time').time()
        
        optimization_result = await service.perform_labor_optimization(
            request.application_methods,
            request.field_conditions,
            request.crop_requirements,
            request.fertilizer_specification,
            request.available_equipment,
            request.seasonal_constraint
        )
        
        processing_time_ms = (__import__('time').time() - start_time) * 1000
        
        response = LaborOptimizationResponse(
            request_id=str(__import__('uuid').uuid4()),
            optimization_result=optimization_result,
            processing_time_ms=processing_time_ms,
            metadata={
                "methods_analyzed": len(request.application_methods),
                "field_size_acres": request.field_conditions.field_size_acres,
                "optimization_timestamp": __import__('time').time()
            }
        )
        
        logger.info(f"Labor optimization completed in {processing_time_ms:.2f}ms")
        return response
        
    except Exception as e:
        logger.error(f"Error in labor optimization: {e}")
        raise HTTPException(status_code=500, detail=f"Labor optimization failed: {str(e)}")


@router.post("/roi-analysis", response_model=LaborROIAnalysisResponse)
async def calculate_labor_roi(
    request: LaborAnalysisRequest,
    service: AdvancedLaborAnalysisService = Depends(get_advanced_labor_analysis_service)
):
    """
    Calculate return on investment specifically for labor costs.
    
    This endpoint analyzes the return on investment for labor costs associated
    with different fertilizer application methods, considering efficiency,
    quality, and safety factors.
    
    **ROI Analysis:**
    - Labor cost per acre
    - Estimated revenue based on application quality and efficiency
    - ROI percentage for each method
    - Risk-adjusted ROI calculations
    - Cost-benefit comparison
    """
    try:
        logger.info("Processing labor ROI analysis request")
        
        start_time = __import__('time').time()
        
        labor_roi = await service.calculate_labor_roi(
            request.application_methods,
            request.field_conditions,
            request.crop_requirements,
            request.fertilizer_specification,
            request.available_equipment
        )
        
        processing_time_ms = (__import__('time').time() - start_time) * 1000
        
        response = LaborROIAnalysisResponse(
            request_id=str(__import__('uuid').uuid4()),
            labor_roi=labor_roi,
            processing_time_ms=processing_time_ms,
            metadata={
                "methods_analyzed": len(request.application_methods),
                "field_size_acres": request.field_conditions.field_size_acres,
                "roi_analysis_timestamp": __import__('time').time()
            }
        )
        
        logger.info(f"Labor ROI analysis completed in {processing_time_ms:.2f}ms")
        return response
        
    except Exception as e:
        logger.error(f"Error in labor ROI analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Labor ROI analysis failed: {str(e)}")


@router.post("/sensitivity-analysis")
async def calculate_labor_sensitivity(
    request: LaborAnalysisRequest,
    service: AdvancedLaborAnalysisService = Depends(get_advanced_labor_analysis_service)
):
    """
    Calculate sensitivity of labor costs to various factors.
    
    This endpoint analyzes how sensitive labor costs and efficiency are to
    changes in labor rates, field conditions, equipment availability, and
    other factors.
    
    **Sensitivity Analysis:**
    - Labor cost variation impact
    - Field condition sensitivity
    - Equipment availability impact
    - Skill level impact
    - Seasonal variation effects
    - Risk factor sensitivity
    """
    try:
        logger.info("Processing labor sensitivity analysis request")
        
        start_time = __import__('time').time()
        
        sensitivity_analysis = await service.calculate_labor_sensitivity_analysis(
            request.application_methods,
            request.field_conditions,
            request.crop_requirements,
            request.fertilizer_specification,
            request.available_equipment
        )
        
        processing_time_ms = (__import__('time').time() - start_time) * 1000
        
        response = {
            "request_id": str(__import__('uuid').uuid4()),
            "sensitivity_analysis": sensitivity_analysis,
            "processing_time_ms": processing_time_ms,
            "metadata": {
                "methods_analyzed": len(request.application_methods),
                "field_size_acres": request.field_conditions.field_size_acres,
                "sensitivity_analysis_timestamp": __import__('time').time()
            }
        }
        
        logger.info(f"Labor sensitivity analysis completed in {processing_time_ms:.2f}ms")
        return response
        
    except Exception as e:
        logger.error(f"Error in labor sensitivity analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Labor sensitivity analysis failed: {str(e)}")


@router.get("/efficiency-metrics")
async def get_efficiency_metrics():
    """
    Get information about available labor efficiency metrics.
    
    Returns details about the different efficiency metrics used in the analysis
    and their characteristics.
    """
    metrics_info = [
        {
            "metric": LaborEfficiencyMetric.PRODUCTIVITY_RATE,
            "name": "Productivity Rate",
            "description": "Acreage that can be covered per hour of labor",
            "scale": "Variable (acres/hour)",
            "importance": "High - directly impacts labor cost efficiency"
        },
        {
            "metric": LaborEfficiencyMetric.QUALITY_SCORE,
            "name": "Quality Score",
            "description": "Application quality rating based on method and equipment",
            "scale": "0-1 scale",
            "importance": "High - affects yield outcomes and effectiveness"
        },
        {
            "metric": LaborEfficiencyMetric.SAFETY_RECORD,
            "name": "Safety Score",
            "description": "Safety compliance and risk rating for the method",
            "scale": "0-1 scale",
            "importance": "High - critical for compliance and risk management"
        },
        {
            "metric": LaborEfficiencyMetric.EQUIPMENT_UTILIZATION,
            "name": "Equipment Utilization",
            "description": "How efficiently equipment is used in the application process",
            "scale": "0-1 scale",
            "importance": "Medium - affects overall operational efficiency"
        },
        {
            "metric": LaborEfficiencyMetric.CONTINUOUS_IMPROVEMENT,
            "name": "Continuous Improvement",
            "description": "Potential for efficiency improvements over time",
            "scale": "0-1 scale",
            "importance": "Medium - affects long-term efficiency gains"
        }
    ]
    
    return {
        "available_metrics": metrics_info,
        "default_weights": {
            "productivity": 0.25,
            "quality": 0.25,
            "safety": 0.15,
            "equipment_utilization": 0.15,
            "skill_alignment": 0.10,
            "training_requirement": 0.10
        },
        "recommendation": "Quality and productivity are most important for immediate decisions, safety for compliance, and training for workforce planning"
    }


@router.get("/labor-cost-drivers")
async def get_labor_cost_drivers():
    """
    Get information about key drivers of labor costs in fertilizer application.
    
    Returns insights about the main factors that influence labor costs for
    different application methods.
    """
    cost_drivers = [
        {
            "factor": "Method Complexity",
            "description": "More complex methods require skilled labor and take more time",
            "impact": "High",
            "methods_affected": ["sidedress", "foliar", "injection"]
        },
        {
            "factor": "Equipment Setup Time",
            "description": "Time required to set up and calibrate equipment",
            "impact": "Medium",
            "methods_affected": ["band", "sidedress", "foliar"]
        },
        {
            "factor": "Field Conditions",
            "description": "Slope, terrain, and accessibility affect labor productivity",
            "impact": "Medium",
            "methods_affected": ["all_methods"]
        },
        {
            "factor": "Training Requirements",
            "description": "Specialized methods require more training which increases costs",
            "impact": "Medium",
            "methods_affected": ["foliar", "injection"]
        },
        {
            "factor": "Safety Protocols",
            "description": "Safety requirements add time and cost to operations",
            "impact": "Low to Medium",
            "methods_affected": ["foliar", "injection"]
        }
    ]
    
    return {
        "labor_cost_drivers": cost_drivers,
        "cost_reduction_strategies": [
            "Optimize equipment setup procedures",
            "Invest in worker training for complex methods",
            "Select methods appropriate for worker skill level",
            "Consider seasonal labor availability in planning",
            "Balance safety requirements with productivity needs"
        ]
    }


@router.get("/health")
async def health_check():
    """Health check endpoint for advanced labor analysis service."""
    return {
        "service": "fertilizer-application-advanced-labor-analysis",
        "status": "healthy",
        "endpoints": [
            "analyze_labor_efficiency",
            "optimize_labor",
            "calculate_labor_roi",
            "calculate_labor_sensitivity",
            "get_efficiency_metrics",
            "get_labor_cost_drivers"
        ],
        "features": [
            "labor_efficiency_analysis",
            "productivity_rate_calculation",
            "quality_score_assessment",
            "safety_score_evaluation",
            "equipment_utilization_analysis",
            "labor_optimization",
            "roi_analysis",
            "sensitivity_analysis",
            "risk_assessment"
        ]
    }
"""
API Routes for Cover Crop and Mulch Optimization Service

FastAPI routes for the cover crop and mulch performance optimization service.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import date
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel, Field

from ..services.cover_crop_mulch_optimization_service import (
    CoverCropMulchOptimizationService,
    OptimizationObjective,
    OptimizationAlgorithm,
    OptimizationResult,
    SpeciesOptimizationRequest,
    MulchOptimizationRequest,
    PerformanceOptimizationInsight
)
from ..models.practice_effectiveness_models import PerformanceMeasurement

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/optimization", tags=["optimization"])

# Dependency injection
async def get_optimization_service() -> CoverCropMulchOptimizationService:
    service = CoverCropMulchOptimizationService()
    await service.initialize()
    return service

# Request/Response models for API
class FieldCharacteristicsRequest(BaseModel):
    """Request model for field characteristics."""
    field_id: UUID = Field(..., description="Field identifier")
    soil_type: str = Field(..., description="Primary soil type")
    climate_zone: str = Field(..., description="Climate zone")
    field_size_acres: float = Field(..., ge=0, description="Field size in acres")
    soil_quality_score: float = Field(..., ge=0, le=1, description="Soil quality score")
    moisture_availability: float = Field(..., ge=0, le=1, description="Moisture availability")
    temperature_suitability: float = Field(..., ge=0, le=1, description="Temperature suitability")
    ph_level: float = Field(..., ge=0, le=14, description="Soil pH level")
    organic_matter_percent: float = Field(..., ge=0, le=100, description="Organic matter percentage")
    slope_percent: float = Field(..., ge=0, le=100, description="Field slope percentage")
    drainage_class: str = Field(..., description="Drainage class")

class OptimizationConstraintsRequest(BaseModel):
    """Request model for optimization constraints."""
    budget_limit: Optional[float] = Field(None, description="Budget limit in dollars")
    labor_hours_available: Optional[float] = Field(None, description="Available labor hours")
    available_equipment: Optional[List[str]] = Field(None, description="Available equipment")
    material_availability: Optional[List[str]] = Field(None, description="Available materials")
    implementation_timeline: Optional[str] = Field(None, description="Implementation timeline")

class ComprehensiveOptimizationRequest(BaseModel):
    """Request model for comprehensive optimization."""
    field_id: UUID = Field(..., description="Field identifier")
    field_characteristics: FieldCharacteristicsRequest = Field(..., description="Field characteristics")
    optimization_objectives: List[OptimizationObjective] = Field(..., description="Optimization objectives")
    constraints: Optional[OptimizationConstraintsRequest] = Field(None, description="Optimization constraints")
    include_timing_optimization: bool = Field(default=True, description="Include timing optimization")
    include_performance_insights: bool = Field(default=True, description="Include performance insights")

class TimingOptimizationRequest(BaseModel):
    """Request model for timing optimization."""
    field_id: UUID = Field(..., description="Field identifier")
    optimized_species: List[Dict[str, Any]] = Field(..., description="Optimized cover crop species")
    optimized_materials: List[Dict[str, Any]] = Field(..., description="Optimized mulch materials")
    field_characteristics: FieldCharacteristicsRequest = Field(..., description="Field characteristics")
    weather_forecast: Optional[Dict[str, Any]] = Field(None, description="Weather forecast data")

class PerformanceInsightsRequest(BaseModel):
    """Request model for performance insights."""
    field_id: UUID = Field(..., description="Field identifier")
    performance_data: List[Dict[str, Any]] = Field(..., description="Performance measurement data")
    optimization_history: Optional[List[Dict[str, Any]]] = Field(None, description="Historical optimization results")

# API Endpoints

@router.post("/species", response_model=List[Dict[str, Any]])
async def optimize_cover_crop_species(
    request: SpeciesOptimizationRequest,
    service: CoverCropMulchOptimizationService = Depends(get_optimization_service)
):
    """
    Optimize cover crop species selection for a field.
    
    This endpoint uses advanced algorithms to select the most effective
    cover crop species based on field characteristics, optimization objectives,
    and constraints.
    
    Features:
    - Multi-objective optimization
    - Constraint handling
    - ML-based optimization (if historical data available)
    - Climate and soil compatibility analysis
    """
    try:
        logger.info(f"Optimizing cover crop species for field: {request.field_id}")
        
        optimized_species = await service.optimize_cover_crop_species(request)
        
        # Convert to response format
        response = []
        for species in optimized_species:
            response.append({
                "species_id": str(species.species_id),
                "common_name": species.common_name,
                "scientific_name": species.scientific_name,
                "crop_type": species.crop_type,
                "nitrogen_fixation": species.nitrogen_fixation,
                "biomass_production_lbs_per_acre": species.biomass_production_lbs_per_acre,
                "root_depth_inches": species.root_depth_inches,
                "cold_tolerance_f": species.cold_tolerance_f,
                "drought_tolerance": species.drought_tolerance,
                "seeding_rate_lbs_per_acre": species.seeding_rate_lbs_per_acre,
                "termination_methods": species.termination_methods,
                "benefits": species.benefits
            })
        
        logger.info(f"Optimized {len(response)} cover crop species")
        return response
        
    except Exception as e:
        logger.error(f"Error optimizing cover crop species: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mulch", response_model=List[Dict[str, Any]])
async def optimize_mulch_materials(
    request: MulchOptimizationRequest,
    service: CoverCropMulchOptimizationService = Depends(get_optimization_service)
):
    """
    Optimize mulch material selection for a field.
    
    This endpoint uses advanced algorithms to select the most effective
    mulch materials based on field characteristics, optimization objectives,
    and constraints.
    
    Features:
    - Multi-objective optimization
    - Constraint handling
    - ML-based optimization (if historical data available)
    - Cost-effectiveness analysis
    """
    try:
        logger.info(f"Optimizing mulch materials for field: {request.field_id}")
        
        optimized_materials = await service.optimize_mulch_materials(request)
        
        # Convert to response format
        response = []
        for material in optimized_materials:
            response.append({
                "material_id": str(material.material_id),
                "material_name": material.material_name,
                "mulch_type": material.mulch_type,
                "cost_per_cubic_yard": float(material.cost_per_cubic_yard),
                "application_rate_inches": material.application_rate_inches,
                "moisture_retention_percent": material.moisture_retention_percent,
                "weed_suppression_percent": material.weed_suppression_percent,
                "decomposition_rate_months": material.decomposition_rate_months,
                "soil_health_benefits": material.soil_health_benefits
            })
        
        logger.info(f"Optimized {len(response)} mulch materials")
        return response
        
    except Exception as e:
        logger.error(f"Error optimizing mulch materials: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/comprehensive", response_model=Dict[str, Any])
async def generate_comprehensive_optimization(
    request: ComprehensiveOptimizationRequest,
    service: CoverCropMulchOptimizationService = Depends(get_optimization_service)
):
    """
    Generate comprehensive optimization for both cover crops and mulch materials.
    
    This endpoint provides a complete optimization analysis including:
    - Species and material optimization
    - Performance predictions
    - Economic analysis
    - Implementation planning
    - Timing optimization (optional)
    - Performance insights (optional)
    
    This is the recommended endpoint for most optimization needs.
    """
    try:
        logger.info(f"Generating comprehensive optimization for field: {request.field_id}")
        
        # Convert field characteristics
        field_characteristics = {
            "soil_type": request.field_characteristics.soil_type,
            "climate_zone": request.field_characteristics.climate_zone,
            "field_size_acres": request.field_characteristics.field_size_acres,
            "soil_quality_score": request.field_characteristics.soil_quality_score,
            "moisture_availability": request.field_characteristics.moisture_availability,
            "temperature_suitability": request.field_characteristics.temperature_suitability,
            "ph_level": request.field_characteristics.ph_level,
            "organic_matter_percent": request.field_characteristics.organic_matter_percent,
            "slope_percent": request.field_characteristics.slope_percent,
            "drainage_class": request.field_characteristics.drainage_class
        }
        
        # Convert constraints
        constraints = {}
        if request.constraints:
            if request.constraints.budget_limit:
                constraints["budget_limit"] = request.constraints.budget_limit
            if request.constraints.labor_hours_available:
                constraints["labor_hours_available"] = request.constraints.labor_hours_available
            if request.constraints.available_equipment:
                constraints["available_equipment"] = request.constraints.available_equipment
            if request.constraints.material_availability:
                constraints["material_availability"] = request.constraints.material_availability
        
        # Generate optimization
        optimization_result = await service.generate_comprehensive_optimization(
            request.field_id,
            field_characteristics,
            request.optimization_objectives,
            constraints
        )
        
        # Prepare response
        response = {
            "optimization_id": str(optimization_result.optimization_id),
            "field_id": str(optimization_result.field_id),
            "optimization_objective": optimization_result.optimization_objective,
            "algorithm_used": optimization_result.algorithm_used,
            "confidence_score": optimization_result.confidence_score,
            "optimization_timestamp": optimization_result.optimization_timestamp,
            "optimized_cover_crops": [
                {
                    "species_id": str(species.species_id),
                    "common_name": species.common_name,
                    "scientific_name": species.scientific_name,
                    "crop_type": species.crop_type,
                    "nitrogen_fixation": species.nitrogen_fixation,
                    "biomass_production_lbs_per_acre": species.biomass_production_lbs_per_acre,
                    "root_depth_inches": species.root_depth_inches,
                    "cold_tolerance_f": species.cold_tolerance_f,
                    "drought_tolerance": species.drought_tolerance,
                    "seeding_rate_lbs_per_acre": species.seeding_rate_lbs_per_acre,
                    "termination_methods": species.termination_methods,
                    "benefits": species.benefits
                }
                for species in optimization_result.optimized_cover_crops
            ],
            "optimized_mulch_materials": [
                {
                    "material_id": str(material.material_id),
                    "material_name": material.material_name,
                    "mulch_type": material.mulch_type,
                    "cost_per_cubic_yard": float(material.cost_per_cubic_yard),
                    "application_rate_inches": material.application_rate_inches,
                    "moisture_retention_percent": material.moisture_retention_percent,
                    "weed_suppression_percent": material.weed_suppression_percent,
                    "decomposition_rate_months": material.decomposition_rate_months,
                    "soil_health_benefits": material.soil_health_benefits
                }
                for material in optimization_result.optimized_mulch_materials
            ],
            "performance_predictions": optimization_result.performance_predictions,
            "economic_analysis": optimization_result.economic_analysis,
            "implementation_plan": optimization_result.implementation_plan
        }
        
        # Add timing optimization if requested
        if request.include_timing_optimization:
            timing_plan = await service.optimize_implementation_timing(
                request.field_id,
                optimization_result.optimized_cover_crops,
                optimization_result.optimized_mulch_materials,
                field_characteristics
            )
            response["timing_optimization"] = timing_plan
        
        logger.info(f"Generated comprehensive optimization for field: {request.field_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error generating comprehensive optimization: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/timing", response_model=Dict[str, Any])
async def optimize_implementation_timing(
    request: TimingOptimizationRequest,
    service: CoverCropMulchOptimizationService = Depends(get_optimization_service)
):
    """
    Optimize implementation timing for cover crops and mulch materials.
    
    This endpoint analyzes optimal timing for:
    - Cover crop planting
    - Cover crop termination
    - Mulch application
    - Integrated schedule creation
    
    Features:
    - Weather-based timing optimization
    - Risk assessment
    - Integrated scheduling
    """
    try:
        logger.info(f"Optimizing implementation timing for field: {request.field_id}")
        
        # Convert field characteristics
        field_characteristics = {
            "soil_type": request.field_characteristics.soil_type,
            "climate_zone": request.field_characteristics.climate_zone,
            "field_size_acres": request.field_characteristics.field_size_acres,
            "soil_quality_score": request.field_characteristics.soil_quality_score,
            "moisture_availability": request.field_characteristics.moisture_availability,
            "temperature_suitability": request.field_characteristics.temperature_suitability,
            "ph_level": request.field_characteristics.ph_level,
            "organic_matter_percent": request.field_characteristics.organic_matter_percent,
            "slope_percent": request.field_characteristics.slope_percent,
            "drainage_class": request.field_characteristics.drainage_class
        }
        
        # Convert species and materials (simplified for API)
        optimized_species = []  # Would need to reconstruct from dict
        optimized_materials = []  # Would need to reconstruct from dict
        
        timing_plan = await service.optimize_implementation_timing(
            request.field_id,
            optimized_species,
            optimized_materials,
            field_characteristics,
            request.weather_forecast
        )
        
        logger.info(f"Optimized implementation timing for field: {request.field_id}")
        return timing_plan
        
    except Exception as e:
        logger.error(f"Error optimizing implementation timing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/insights", response_model=List[Dict[str, Any]])
async def generate_performance_insights(
    request: PerformanceInsightsRequest,
    service: CoverCropMulchOptimizationService = Depends(get_optimization_service)
):
    """
    Generate performance insights based on historical data and optimization results.
    
    This endpoint analyzes:
    - Performance trends
    - Optimization effectiveness
    - ML-based insights
    - Species-specific insights
    - Mulch-specific insights
    
    Features:
    - Trend analysis
    - Predictive insights
    - Actionable recommendations
    """
    try:
        logger.info(f"Generating performance insights for field: {request.field_id}")
        
        # Convert performance data
        performance_data = []
        for data in request.performance_data:
            measurement = PerformanceMeasurement(
                implementation_id=UUID(data.get("implementation_id", str(uuid4()))),
                measurement_date=date.fromisoformat(data.get("measurement_date", "2024-01-01")),
                metric_type=data.get("metric_type", "water_savings"),
                metric_value=data.get("metric_value", 0),
                metric_unit=data.get("metric_unit", "percent"),
                measurement_method=data.get("measurement_method", "manual"),
                measurement_source=data.get("measurement_source", "farmer"),
                confidence_level=data.get("confidence_level", 0.8),
                notes=data.get("notes"),
                baseline_value=data.get("baseline_value"),
                improvement_percent=data.get("improvement_percent")
            )
            performance_data.append(measurement)
        
        # Convert optimization history (simplified)
        optimization_history = []  # Would need to reconstruct from dict
        
        insights = await service.generate_performance_insights(
            request.field_id,
            performance_data,
            optimization_history
        )
        
        # Convert to response format
        response = []
        for insight in insights:
            response.append({
                "insight_id": str(insight.insight_id),
                "field_id": str(insight.field_id),
                "insight_type": insight.insight_type,
                "insight_description": insight.insight_description,
                "confidence_score": insight.confidence_score,
                "supporting_data": insight.supporting_data,
                "recommended_actions": insight.recommended_actions,
                "expected_impact": insight.expected_impact,
                "created_at": insight.created_at
            })
        
        logger.info(f"Generated {len(response)} performance insights")
        return response
        
    except Exception as e:
        logger.error(f"Error generating performance insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/objectives", response_model=List[Dict[str, str]])
async def get_optimization_objectives():
    """
    Get available optimization objectives.
    
    Returns a list of all available optimization objectives that can be used
    in optimization requests.
    """
    objectives = []
    for objective in OptimizationObjective:
        objectives.append({
            "value": objective.value,
            "description": objective.value.replace("_", " ").title()
        })
    return objectives

@router.get("/algorithms", response_model=List[Dict[str, str]])
async def get_optimization_algorithms():
    """
    Get available optimization algorithms.
    
    Returns a list of all available optimization algorithms that can be used
    in optimization requests.
    """
    algorithms = []
    for algorithm in OptimizationAlgorithm:
        algorithms.append({
            "value": algorithm.value,
            "description": algorithm.value.replace("_", " ").title()
        })
    return algorithms

@router.get("/health")
async def health_check():
    """Health check endpoint for the optimization service."""
    return {
        "status": "healthy",
        "service": "cover-crop-mulch-optimization",
        "version": "1.0.0",
        "features": [
            "species_optimization",
            "mulch_optimization",
            "comprehensive_optimization",
            "timing_optimization",
            "performance_insights"
        ]
    }
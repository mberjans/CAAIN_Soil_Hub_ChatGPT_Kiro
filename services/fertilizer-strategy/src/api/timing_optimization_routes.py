"""
Timing Optimization API Routes

This module provides FastAPI routes for fertilizer timing optimization,
including weather integration, crop growth stage analysis, and multi-objective optimization.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from typing import List, Dict, Optional, Any
import logging
import asyncio

from ..models.timing_optimization_models import (
    TimingOptimizationRequest,
    TimingOptimizationResult,
    ApplicationTiming,
    SplitApplicationPlan,
    WeatherWindow,
    TimingOptimizationSummary,
    EquipmentAvailability,
    LaborAvailability
)
from ..services.timing_optimization_service import FertilizerTimingOptimizer

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/timing-optimization", tags=["timing-optimization"])

# Dependency injection
async def get_timing_optimizer() -> FertilizerTimingOptimizer:
    """Get timing optimization service instance."""
    return FertilizerTimingOptimizer()


@router.post("/optimize", response_model=TimingOptimizationResult)
async def optimize_fertilizer_timing(
    request: TimingOptimizationRequest,
    background_tasks: BackgroundTasks,
    optimizer: FertilizerTimingOptimizer = Depends(get_timing_optimizer)
):
    """
    Optimize fertilizer application timing with comprehensive analysis.
    
    This endpoint provides advanced timing optimization considering:
    - Crop growth stages and critical timing windows
    - Weather conditions and forecast integration
    - Soil conditions and temperature requirements
    - Equipment and labor availability constraints
    - Risk assessment and mitigation strategies
    - Economic analysis and ROI calculations
    
    Agricultural Use Cases:
    - Optimal nitrogen application timing for corn (planting vs side-dress)
    - Phosphorus and potassium timing for root development
    - Split application planning for risk reduction
    - Weather-dependent application scheduling
    - Equipment and labor resource optimization
    - Cost-effective timing strategies
    """
    try:
        logger.info(f"Starting timing optimization for request {request.request_id}")
        
        # Perform timing optimization
        result = await optimizer.optimize_timing(request)
        
        # Log optimization results
        logger.info(f"Timing optimization completed: {len(result.optimal_timings)} timings, "
                   f"score: {result.overall_timing_score:.2f}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in timing optimization: {e}")
        raise HTTPException(status_code=500, detail=f"Timing optimization failed: {str(e)}")


@router.post("/quick-optimize", response_model=TimingOptimizationResult)
async def quick_timing_optimization(
    request: TimingOptimizationRequest,
    optimizer: FertilizerTimingOptimizer = Depends(get_timing_optimizer)
):
    """
    Quick timing optimization with minimal input parameters.
    
    Provides rapid timing optimization for common scenarios with default parameters.
    Useful for quick assessments and preliminary planning.
    
    Agricultural Use Cases:
    - Quick timing assessment for field planning
    - Preliminary optimization before detailed analysis
    - Rapid response to changing conditions
    - Mobile field application support
    """
    try:
        result = await optimizer.optimize_timing(request)
        
        logger.info(f"Quick timing optimization completed for field {request.field_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error in quick timing optimization: {e}")
        raise HTTPException(status_code=500, detail=f"Quick timing optimization failed: {str(e)}")


@router.post("/weather-windows", response_model=List[WeatherWindow])
async def get_weather_windows(
    request: TimingOptimizationRequest,
    optimizer: FertilizerTimingOptimizer = Depends(get_timing_optimizer)
):
    """
    Get available weather windows for fertilizer application.
    
    Analyzes weather conditions over a specified period to identify
    optimal application windows based on temperature, precipitation,
    wind speed, and soil moisture conditions.
    
    Agricultural Use Cases:
    - Weather window planning for application scheduling
    - Risk assessment for application timing
    - Flexible scheduling based on weather conditions
    - Emergency application planning
    """
    try:
        weather_windows = await optimizer._analyze_weather_windows(request)
        
        logger.info(f"Retrieved {len(weather_windows)} weather windows")
        return weather_windows
        
    except Exception as e:
        logger.error(f"Error retrieving weather windows: {e}")
        raise HTTPException(status_code=500, detail=f"Weather window analysis failed: {str(e)}")


@router.post("/crop-stages", response_model=Dict[str, str])
async def get_crop_growth_stages(
    request: TimingOptimizationRequest,
    optimizer: FertilizerTimingOptimizer = Depends(get_timing_optimizer)
):
    """
    Get predicted crop growth stages based on planting date.
    
    Provides growth stage timeline for planning fertilizer applications
    at optimal crop development phases.
    
    Agricultural Use Cases:
    - Growth stage planning for fertilizer applications
    - Timing optimization based on crop development
    - Application scheduling around critical growth stages
    - Crop development monitoring and planning
    """
    try:
        crop_stages = await optimizer._determine_crop_growth_stages(request)
        
        # Convert to string format for API response
        stage_timeline = {
            stage.value: date.strftime("%Y-%m-%d")
            for date, stage in crop_stages.items()
        }
        
        logger.info(f"Retrieved growth stages for {request.crop_type}")
        return stage_timeline
        
    except Exception as e:
        logger.error(f"Error retrieving crop growth stages: {e}")
        raise HTTPException(status_code=500, detail=f"Growth stage analysis failed: {str(e)}")


@router.post("/split-applications", response_model=List[SplitApplicationPlan])
async def optimize_split_applications(
    request: TimingOptimizationRequest,
    optimizer: FertilizerTimingOptimizer = Depends(get_timing_optimizer)
):
    """
    Optimize split application plans for risk reduction.
    
    Analyzes fertilizer requirements and generates optimal split application
    strategies to reduce timing risk and improve application efficiency.
    
    Agricultural Use Cases:
    - Nitrogen split application planning for corn
    - Risk reduction through multiple application passes
    - Equipment and labor optimization for split applications
    - Weather risk mitigation strategies
    """
    try:
        logger.info(f"Optimizing split applications for request {request.request_id}")
        
        # Perform full timing optimization
        result = await optimizer.optimize_timing(request)
        
        logger.info(f"Generated {len(result.split_plans)} split application plans")
        return result.split_plans
        
    except Exception as e:
        logger.error(f"Error optimizing split applications: {e}")
        raise HTTPException(status_code=500, detail=f"Split application optimization failed: {str(e)}")


@router.get("/timing-summary/{request_id}", response_model=TimingOptimizationSummary)
async def get_timing_summary(
    request_id: str,
    optimizer: FertilizerTimingOptimizer = Depends(get_timing_optimizer)
):
    """
    Get summary of timing optimization results.
    
    Provides high-level summary of timing optimization including
    risk assessment, cost analysis, and key recommendations.
    
    Agricultural Use Cases:
    - Quick overview of timing optimization results
    - Risk assessment summary for decision making
    - Cost and efficiency analysis
    - Key insights and recommendations
    """
    try:
        # This would typically retrieve from database or cache
        # For now, return mock summary
        summary = TimingOptimizationSummary(
            total_applications=3,
            applications_by_month={"April": 1, "May": 1, "June": 1},
            risk_level="moderate",
            cost_efficiency_score=0.85,
            weather_dependency_score=0.7,
            flexibility_score=0.8,
            primary_risks=["Weather variability", "Equipment availability"],
            optimization_opportunities=["Split applications", "Flexible scheduling"],
            critical_timing_windows=["V4-V6 growth stage", "Pre-rainfall applications"]
        )
        
        logger.info(f"Retrieved timing summary for request {request_id}")
        return summary
        
    except Exception as e:
        logger.error(f"Error retrieving timing summary: {e}")
        raise HTTPException(status_code=500, detail=f"Timing summary retrieval failed: {str(e)}")


@router.get("/equipment-availability/{field_id}", response_model=List[EquipmentAvailability])
async def get_equipment_availability(
    field_id: str,
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)")
):
    """
    Get equipment availability for timing optimization.
    
    Retrieves available equipment and capacity for fertilizer application
    within the specified date range.
    
    Agricultural Use Cases:
    - Equipment scheduling for fertilizer applications
    - Capacity planning for application timing
    - Resource optimization and allocation
    - Equipment availability constraints
    """
    try:
        from datetime import datetime, timedelta
        
        # Mock equipment availability data
        # In production, this would integrate with equipment management system
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        equipment_list = [
            EquipmentAvailability(
                equipment_type="broadcast_spreader",
                available_dates=[start_dt + timedelta(days=i) for i in range(0, 30, 3)],
                capacity_per_day=100.0,
                cost_per_acre=5.0,
                efficiency_factor=0.9
            ),
            EquipmentAvailability(
                equipment_type="side_dress_applicator",
                available_dates=[start_dt + timedelta(days=i) for i in range(1, 30, 4)],
                capacity_per_day=80.0,
                cost_per_acre=7.0,
                efficiency_factor=0.85
            )
        ]
        
        logger.info(f"Retrieved equipment availability for field {field_id}")
        return equipment_list
        
    except Exception as e:
        logger.error(f"Error retrieving equipment availability: {e}")
        raise HTTPException(status_code=500, detail=f"Equipment availability retrieval failed: {str(e)}")


@router.get("/labor-availability/{field_id}", response_model=List[LaborAvailability])
async def get_labor_availability(
    field_id: str,
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)")
):
    """
    Get labor availability for timing optimization.
    
    Retrieves available labor resources and capacity for fertilizer application
    within the specified date range.
    
    Agricultural Use Cases:
    - Labor scheduling for fertilizer applications
    - Workforce planning and allocation
    - Labor cost optimization
    - Resource constraint analysis
    """
    try:
        from datetime import datetime, timedelta
        
        # Mock labor availability data
        # In production, this would integrate with labor management system
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        labor_list = [
            LaborAvailability(
                labor_type="application_operator",
                available_dates=[start_dt + timedelta(days=i) for i in range(0, 30, 2)],
                hours_per_day=10,
                cost_per_hour=25.0,
                skill_level="expert"
            ),
            LaborAvailability(
                labor_type="equipment_technician",
                available_dates=[start_dt + timedelta(days=i) for i in range(1, 30, 3)],
                hours_per_day=8,
                cost_per_hour=30.0,
                skill_level="expert"
            )
        ]
        
        logger.info(f"Retrieved labor availability for field {field_id}")
        return labor_list
        
    except Exception as e:
        logger.error(f"Error retrieving labor availability: {e}")
        raise HTTPException(status_code=500, detail=f"Labor availability retrieval failed: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for timing optimization service."""
    return {
        "service": "timing-optimization",
        "status": "healthy",
        "features": [
            "weather_integration",
            "crop_growth_stage_analysis",
            "multi_objective_optimization",
            "split_application_planning",
            "risk_assessment",
            "equipment_constraint_integration",
            "labor_availability_analysis",
            "economic_optimization",
            "timing_recommendations"
        ]
    }
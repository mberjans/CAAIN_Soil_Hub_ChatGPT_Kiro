"""
Drought Management API Routes

FastAPI router for drought assessment, moisture conservation,
and monitoring endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, date
from uuid import UUID

from ..models.drought_models import (
    DroughtAssessmentRequest,
    DroughtAssessmentResponse,
    ConservationPracticeRequest,
    ConservationPracticeResponse,
    DroughtMonitoringRequest,
    DroughtMonitoringResponse,
    WaterSavingsRequest,
    WaterSavingsResponse,
    DroughtRiskAssessment,
    SoilMoistureStatus
)
from ..models.soil_assessment_models import (
    SoilAssessmentRequest,
    SoilAssessmentResponse,
    PracticeRecommendationResponse,
    SoilHealthTrendResponse
)

logger = logging.getLogger(__name__)

# Create main router
router = APIRouter(prefix="/api/v1/drought", tags=["drought-management"])

# Service dependencies (will be injected)
async def get_drought_assessment_service():
    """Get drought assessment service instance."""
    from ..services.drought_assessment_service import DroughtAssessmentService
    return DroughtAssessmentService()

async def get_moisture_conservation_service():
    """Get moisture conservation service instance."""
    from ..services.moisture_conservation_service import MoistureConservationService
    return MoistureConservationService()

async def get_drought_monitoring_service():
    """Get drought monitoring service instance."""
    from ..services.drought_monitoring_service import DroughtMonitoringService
    return DroughtMonitoringService()

async def get_water_savings_calculator():
    """Get water savings calculator instance."""
    from ..services.water_savings_calculator import WaterSavingsCalculator
    return WaterSavingsCalculator()

async def get_soil_assessment_service():
    """Get soil assessment service instance."""
    from ..services.soil_assessment_service import SoilManagementAssessmentService
    return SoilManagementAssessmentService()

# Drought Assessment Endpoints
@router.post("/assess", response_model=DroughtAssessmentResponse)
async def assess_drought_risk(
    request: DroughtAssessmentRequest,
    service: DroughtAssessmentService = Depends(get_drought_assessment_service)
):
    """
    Assess drought risk for a specific farm location and crop plan.
    
    This endpoint evaluates drought probability and impact based on:
    - Historical weather data
    - Current soil moisture conditions
    - Weather forecasts
    - Crop water requirements
    - Field characteristics
    
    Returns comprehensive drought risk assessment with recommendations.
    """
    try:
        logger.info(f"Assessing drought risk for location: {request.farm_location_id}")
        assessment = await service.assess_drought_risk(request)
        return assessment
    except Exception as e:
        logger.error(f"Error assessing drought risk: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Drought assessment failed: {str(e)}")

@router.get("/risk-assessment/{farm_location_id}", response_model=DroughtRiskAssessment)
async def get_drought_risk_assessment(
    farm_location_id: UUID,
    assessment_date: Optional[date] = Query(None, description="Assessment date (defaults to today)"),
    service: DroughtAssessmentService = Depends(get_drought_assessment_service)
):
    """
    Get current drought risk assessment for a farm location.
    
    Retrieves the most recent drought risk assessment or creates a new one
    if no recent assessment exists.
    """
    try:
        logger.info(f"Getting drought risk assessment for farm: {farm_location_id}")
        assessment = await service.get_current_drought_risk(farm_location_id, assessment_date)
        return assessment
    except Exception as e:
        logger.error(f"Error getting drought risk assessment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get drought risk assessment: {str(e)}")

# Moisture Conservation Endpoints
@router.post("/conservation/recommendations", response_model=List[ConservationPracticeResponse])
async def get_conservation_recommendations(
    request: ConservationPracticeRequest,
    service: MoistureConservationService = Depends(get_moisture_conservation_service)
):
    """
    Get moisture conservation practice recommendations.
    
    Recommends conservation practices based on:
    - Field characteristics (soil type, slope, drainage)
    - Current moisture conditions
    - Drought risk level
    - Crop requirements
    - Equipment availability
    
    Returns prioritized list of conservation practices with implementation details.
    """
    try:
        logger.info(f"Getting conservation recommendations for field: {request.field_id}")
        recommendations = await service.get_conservation_recommendations(request)
        return recommendations
    except Exception as e:
        logger.error(f"Error getting conservation recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get conservation recommendations: {str(e)}")

@router.post("/conservation/calculate-benefits", response_model=Dict[str, Any])
async def calculate_conservation_benefits(
    practices: List[ConservationPracticeRequest],
    field_id: UUID = Body(..., description="Field ID for benefit calculation"),
    service: MoistureConservationService = Depends(get_moisture_conservation_service)
):
    """
    Calculate benefits of implementing conservation practices.
    
    Calculates:
    - Water savings potential
    - Soil health improvements
    - Cost-benefit analysis
    - Implementation timeline
    - Equipment requirements
    """
    try:
        logger.info(f"Calculating conservation benefits for field: {field_id}")
        benefits = await service.calculate_conservation_benefits(field_id, practices)
        return benefits
    except Exception as e:
        logger.error(f"Error calculating conservation benefits: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate conservation benefits: {str(e)}")

# Drought Monitoring Endpoints
@router.post("/monitor/setup", response_model=DroughtMonitoringResponse)
async def setup_drought_monitoring(
    request: DroughtMonitoringRequest,
    service: DroughtMonitoringService = Depends(get_drought_monitoring_service)
):
    """
    Set up drought monitoring for a farm location.
    
    Configures monitoring parameters:
    - Soil moisture thresholds
    - Weather alert conditions
    - Crop stress indicators
    - Notification preferences
    
    Returns monitoring configuration and initial status.
    """
    try:
        logger.info(f"Setting up drought monitoring for farm: {request.farm_location_id}")
        monitoring = await service.setup_monitoring(request)
        return monitoring
    except Exception as e:
        logger.error(f"Error setting up drought monitoring: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to setup drought monitoring: {str(e)}")

@router.get("/monitor/status/{farm_location_id}", response_model=DroughtMonitoringResponse)
async def get_monitoring_status(
    farm_location_id: UUID,
    service: DroughtMonitoringService = Depends(get_drought_monitoring_service)
):
    """
    Get current drought monitoring status for a farm location.
    
    Returns:
    - Current soil moisture levels
    - Weather conditions
    - Drought risk indicators
    - Active alerts and recommendations
    """
    try:
        logger.info(f"Getting monitoring status for farm: {farm_location_id}")
        status = await service.get_monitoring_status(farm_location_id)
        return status
    except Exception as e:
        logger.error(f"Error getting monitoring status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get monitoring status: {str(e)}")

# Water Savings Endpoints
@router.post("/water-savings/calculate", response_model=WaterSavingsResponse)
async def calculate_water_savings(
    request: WaterSavingsRequest,
    calculator: WaterSavingsCalculator = Depends(get_water_savings_calculator)
):
    """
    Calculate potential water savings from conservation practices.
    
    Calculates water savings based on:
    - Current water usage patterns
    - Proposed conservation practices
    - Field characteristics
    - Weather conditions
    - Crop water requirements
    
    Returns detailed water savings analysis with cost-benefit information.
    """
    try:
        logger.info(f"Calculating water savings for field: {request.field_id}")
        savings = await calculator.calculate_water_savings(request)
        return savings
    except Exception as e:
        logger.error(f"Error calculating water savings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate water savings: {str(e)}")

@router.get("/water-savings/history/{field_id}", response_model=List[WaterSavingsResponse])
async def get_water_savings_history(
    field_id: UUID,
    start_date: Optional[date] = Query(None, description="Start date for history"),
    end_date: Optional[date] = Query(None, description="End date for history"),
    calculator: WaterSavingsCalculator = Depends(get_water_savings_calculator)
):
    """
    Get historical water savings data for a field.
    
    Returns water savings history with:
    - Monthly water usage
    - Conservation practice effectiveness
    - Cost savings
    - Performance trends
    """
    try:
        logger.info(f"Getting water savings history for field: {field_id}")
        history = await calculator.get_water_savings_history(field_id, start_date, end_date)
        return history
    except Exception as e:
        logger.error(f"Error getting water savings history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get water savings history: {str(e)}")

# Soil Moisture Endpoints
@router.get("/soil-moisture/{field_id}", response_model=SoilMoistureStatus)
async def get_soil_moisture_status(
    field_id: UUID,
    depth_cm: Optional[int] = Query(30, description="Soil depth in centimeters"),
    service: DroughtAssessmentService = Depends(get_drought_assessment_service)
):
    """
    Get current soil moisture status for a field.
    
    Returns soil moisture information:
    - Current moisture levels by depth
    - Available water capacity
    - Moisture trends
    - Irrigation recommendations
    """
    try:
        logger.info(f"Getting soil moisture status for field: {field_id}")
        status = await service.get_soil_moisture_status(field_id, depth_cm)
        return status
    except Exception as e:
        logger.error(f"Error getting soil moisture status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get soil moisture status: {str(e)}")

# Soil Assessment Endpoints
@router.post("/soil-assessment", response_model=SoilAssessmentResponse)
async def assess_soil_management_practices(
    request: SoilAssessmentRequest,
    service: SoilManagementAssessmentService = Depends(get_soil_assessment_service)
):
    """
    Assess current soil management practices and provide comprehensive evaluation.
    
    This endpoint evaluates soil management practices including:
    - Tillage practices and soil disturbance
    - Cover crop usage and effectiveness
    - Organic matter management
    - Soil compaction levels
    - Drainage conditions
    
    Returns comprehensive soil health score with improvement recommendations.
    """
    try:
        logger.info(f"Assessing soil management practices for field: {request.field_id}")
        assessment = await service.assess_current_practices(request)
        return assessment
    except Exception as e:
        logger.error(f"Error assessing soil management practices: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Soil assessment failed: {str(e)}")

@router.get("/soil-assessment/{field_id}/recommendations", response_model=PracticeRecommendationResponse)
async def get_soil_practice_recommendations(
    field_id: UUID,
    priority_level: Optional[str] = Query("high", description="Priority level filter"),
    service: SoilManagementAssessmentService = Depends(get_soil_assessment_service)
):
    """
    Get soil management practice recommendations for a field.
    
    Returns prioritized recommendations based on:
    - Current soil health score
    - Limiting factors
    - Improvement potential
    - Implementation feasibility
    - Cost-benefit analysis
    """
    try:
        logger.info(f"Getting soil practice recommendations for field: {field_id}")
        # Create a basic request for the field
        request = SoilAssessmentRequest(
            field_id=field_id,
            farm_location_id=field_id,  # Using field_id as placeholder
            tillage_practices={},
            cover_crop_practices={},
            organic_matter_data={},
            compaction_data={},
            drainage_data={}
        )
        assessment = await service.assess_current_practices(request)
        
        # Extract recommendations from assessment
        recommendations = []
        for opportunity in assessment.improvement_opportunities:
            if priority_level == "all" or opportunity.priority.lower() == priority_level.lower():
                recommendations.append({
                    "category": opportunity.category,
                    "priority": opportunity.priority,
                    "description": opportunity.description,
                    "potential_impact": opportunity.potential_impact,
                    "implementation_cost": opportunity.implementation_cost,
                    "water_savings_potential": opportunity.water_savings_potential
                })
        
        return PracticeRecommendationResponse(
            field_id=field_id,
            practice_scores=[
                {
                    "practice_name": "Tillage Practices",
                    "current_score": assessment.tillage_assessment.overall_score,
                    "target_score": 85.0,
                    "improvement_potential": 85.0 - assessment.tillage_assessment.overall_score,
                    "priority_level": "high" if assessment.tillage_assessment.overall_score < 70 else "medium",
                    "water_savings_potential": 15.0
                },
                {
                    "practice_name": "Cover Crops",
                    "current_score": assessment.cover_crop_assessment.overall_score,
                    "target_score": 80.0,
                    "improvement_potential": 80.0 - assessment.cover_crop_assessment.overall_score,
                    "priority_level": "high" if assessment.cover_crop_assessment.overall_score < 60 else "medium",
                    "water_savings_potential": 20.0
                },
                {
                    "practice_name": "Organic Matter",
                    "current_score": assessment.organic_matter_assessment.overall_score,
                    "target_score": 85.0,
                    "improvement_potential": 85.0 - assessment.organic_matter_assessment.overall_score,
                    "priority_level": "high" if assessment.organic_matter_assessment.overall_score < 70 else "medium",
                    "water_savings_potential": 25.0
                }
            ],
            top_priorities=[opp.category for opp in assessment.improvement_opportunities[:3]],
            implementation_plan={
                "immediate": [opp.category for opp in assessment.improvement_opportunities if opp.category in ["Tillage Practices", "Cover Crops"]],
                "short_term": [opp.category for opp in assessment.improvement_opportunities if opp.category in ["Organic Matter", "Soil Compaction"]],
                "long_term": [opp.category for opp in assessment.improvement_opportunities if opp.category in ["Drainage"]]
            },
            expected_benefits={
                "water_savings": sum(opp.water_savings_potential for opp in assessment.improvement_opportunities),
                "soil_health_improvement": assessment.soil_health_score.improvement_potential,
                "cost_savings": sum(float(opp.implementation_cost) for opp in assessment.improvement_opportunities)
            },
            cost_benefit_analysis={
                "total_implementation_cost": sum(float(opp.implementation_cost) for opp in assessment.improvement_opportunities),
                "annual_water_savings": sum(opp.water_savings_potential for opp in assessment.improvement_opportunities),
                "payback_period_years": 2.5
            }
        )
    except Exception as e:
        logger.error(f"Error getting soil practice recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get soil practice recommendations: {str(e)}")

@router.get("/soil-assessment/{field_id}/trends", response_model=SoilHealthTrendResponse)
async def get_soil_health_trends(
    field_id: UUID,
    months_back: int = Query(12, ge=1, le=60, description="Number of months to look back"),
    service: SoilManagementAssessmentService = Depends(get_soil_assessment_service)
):
    """
    Get soil health trends and historical data for a field.
    
    Returns trend analysis including:
    - Historical soil health scores
    - Improvement rate over time
    - Projected future scores
    - Trend-based recommendations
    """
    try:
        logger.info(f"Getting soil health trends for field: {field_id}")
        
        # Placeholder implementation - in real system, this would query historical data
        assessment_history = [
            {
                "date": "2024-01-01",
                "overall_score": 65.0,
                "tillage_score": 60.0,
                "cover_crop_score": 40.0,
                "organic_matter_score": 70.0,
                "compaction_score": 80.0,
                "drainage_score": 75.0
            },
            {
                "date": "2024-06-01",
                "overall_score": 72.0,
                "tillage_score": 65.0,
                "cover_crop_score": 55.0,
                "organic_matter_score": 75.0,
                "compaction_score": 85.0,
                "drainage_score": 80.0
            }
        ]
        
        trend_analysis = {
            "overall_trend": "improving",
            "improvement_rate": 7.0,  # points per 6 months
            "strongest_area": "drainage",
            "weakest_area": "cover_crops",
            "consistency": "moderate"
        }
        
        projected_scores = {
            "overall_score": 78.0,
            "tillage_score": 70.0,
            "cover_crop_score": 65.0,
            "organic_matter_score": 80.0,
            "compaction_score": 88.0,
            "drainage_score": 85.0
        }
        
        recommendations = [
            "Continue improving cover crop management",
            "Maintain current drainage practices",
            "Consider reducing tillage intensity",
            "Focus on organic matter building practices"
        ]
        
        return SoilHealthTrendResponse(
            field_id=field_id,
            assessment_history=assessment_history,
            trend_analysis=trend_analysis,
            improvement_rate=7.0,
            projected_scores=projected_scores,
            recommendations=recommendations
        )
    except Exception as e:
        logger.error(f"Error getting soil health trends: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get soil health trends: {str(e)}")

# Utility Endpoints
@router.get("/practices", response_model=List[Dict[str, Any]])
async def get_available_practices():
    """
    Get list of available conservation practices.
    
    Returns comprehensive list of moisture conservation practices
    with descriptions, benefits, and implementation requirements.
    """
    try:
        from ..services.moisture_conservation_service import MoistureConservationService
        service = MoistureConservationService()
        practices = await service.get_available_practices()
        return practices
    except Exception as e:
        logger.error(f"Error getting available practices: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get available practices: {str(e)}")

@router.get("/alerts/{farm_location_id}", response_model=List[Dict[str, Any]])
async def get_drought_alerts(
    farm_location_id: UUID,
    alert_type: Optional[str] = Query(None, description="Filter by alert type"),
    service: DroughtMonitoringService = Depends(get_drought_monitoring_service)
):
    """
    Get active drought alerts for a farm location.
    
    Returns current alerts including:
    - Soil moisture alerts
    - Weather alerts
    - Crop stress alerts
    - Irrigation recommendations
    """
    try:
        logger.info(f"Getting drought alerts for farm: {farm_location_id}")
        alerts = await service.get_drought_alerts(farm_location_id, alert_type)
        return alerts
    except Exception as e:
        logger.error(f"Error getting drought alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get drought alerts: {str(e)}")
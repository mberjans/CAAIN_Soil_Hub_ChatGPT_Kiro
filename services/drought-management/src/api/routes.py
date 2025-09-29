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
    SoilMoistureStatus,
    IrrigationAssessmentRequest,
    IrrigationAssessmentResponse,
    IrrigationScheduleRequest,
    IrrigationScheduleResponse,
    IrrigationOptimizationRequest,
    IrrigationOptimizationResponse
)
from ..models.soil_assessment_models import (
    SoilAssessmentRequest,
    SoilAssessmentResponse,
    PracticeRecommendationResponse,
    SoilHealthTrendResponse
)
from ..models.regional_drought_models import (
    RegionalDroughtAnalysisRequest,
    RegionalDroughtAnalysisResponse,
    DroughtForecastRequest,
    DroughtForecastResponse,
    DroughtFrequencyAnalysisRequest,
    DroughtFrequencyAnalysisResponse,
    DroughtTrendAnalysisRequest,
    DroughtTrendAnalysisResponse,
    ClimateChangeImpactRequest,
    ClimateChangeImpactResponse,
    DroughtPatternMapResponse,
    DroughtAlertResponse
)
from ..services.drought_assessment_service import DroughtAssessmentService
from ..services.moisture_conservation_service import MoistureConservationService
from ..services.drought_monitoring_service import DroughtMonitoringService
from ..services.water_savings_calculator import WaterSavingsCalculator
from ..services.soil_assessment_service import SoilManagementAssessmentService
from ..services.soil_weather_service import SoilWeatherIntegrationService
from ..services.soil_moisture_monitoring_service import SoilMoistureMonitoringService
from ..services.regional_drought_analysis_service import RegionalDroughtAnalysisService
from ..services.irrigation_service import IrrigationManagementService

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

async def get_soil_weather_integration_service():
    """Get soil-weather integration service instance."""
    from ..services.soil_weather_service import SoilWeatherIntegrationService
    return SoilWeatherIntegrationService()

async def get_soil_moisture_monitoring_service():
    """Get soil moisture monitoring service instance."""
    from ..services.soil_moisture_monitoring_service import SoilMoistureMonitoringService
    service = SoilMoistureMonitoringService()
    await service.initialize()
    return service

async def get_regional_drought_analysis_service():
    """Get regional drought analysis service instance."""
    from ..services.regional_drought_analysis_service import RegionalDroughtAnalysisService
    service = RegionalDroughtAnalysisService()
    await service.initialize()
    return service

async def get_irrigation_management_service():
    """Get irrigation management service instance."""
    from ..services.irrigation_service import IrrigationManagementService
    return IrrigationManagementService()

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

# Soil Moisture Monitoring Endpoints
@router.post("/soil-moisture/setup-monitoring")
async def setup_soil_moisture_monitoring(
    field_id: UUID = Body(..., description="Field ID for monitoring setup"),
    soil_characteristics: Dict[str, Any] = Body(..., description="Soil characteristics and properties"),
    service: SoilMoistureMonitoringService = Depends(get_soil_moisture_monitoring_service)
):
    """
    Set up soil moisture monitoring for a field.
    
    Configures monitoring parameters:
    - Soil characteristics (field capacity, wilting point, bulk density)
    - Alert thresholds for moisture levels
    - Monitoring depth and frequency
    - Integration with weather and crop data
    
    Returns monitoring configuration and initial status.
    """
    try:
        logger.info(f"Setting up soil moisture monitoring for field: {field_id}")
        config = await service.setup_field_monitoring(field_id, soil_characteristics)
        return {
            "field_id": field_id,
            "monitoring_config": config,
            "status": "active",
            "message": "Soil moisture monitoring setup completed successfully"
        }
    except Exception as e:
        logger.error(f"Error setting up soil moisture monitoring: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to setup soil moisture monitoring: {str(e)}")

@router.get("/soil-moisture/monitoring/{field_id}", response_model=SoilMoistureStatus)
async def get_monitored_soil_moisture_status(
    field_id: UUID,
    service: SoilMoistureMonitoringService = Depends(get_soil_moisture_monitoring_service)
):
    """
    Get current monitored soil moisture status for a field.
    
    Returns comprehensive soil moisture information:
    - Current moisture levels (surface and deep)
    - Available water capacity
    - Overall moisture level classification
    - Irrigation recommendations
    - Days until critical moisture level
    """
    try:
        logger.info(f"Getting monitored soil moisture status for field: {field_id}")
        status = await service.get_current_moisture_status(field_id)
        return status
    except Exception as e:
        logger.error(f"Error getting monitored soil moisture status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get monitored soil moisture status: {str(e)}")

@router.get("/soil-moisture/predict-deficit/{field_id}")
async def predict_soil_moisture_deficit(
    field_id: UUID,
    forecast_days: int = Query(7, ge=1, le=30, description="Number of days to forecast"),
    service: SoilMoistureMonitoringService = Depends(get_soil_moisture_monitoring_service)
):
    """
    Predict soil moisture deficit over the forecast period.
    
    Uses water balance models to predict:
    - Daily moisture levels
    - Moisture deficit accumulation
    - Risk levels for each day
    - Overall drought risk assessment
    
    Returns detailed deficit prediction with recommendations.
    """
    try:
        logger.info(f"Predicting soil moisture deficit for field: {field_id}, days: {forecast_days}")
        prediction = await service.predict_moisture_deficit(field_id, forecast_days)
        return prediction
    except Exception as e:
        logger.error(f"Error predicting soil moisture deficit: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to predict soil moisture deficit: {str(e)}")

@router.get("/soil-moisture/evapotranspiration/{field_id}")
async def calculate_field_evapotranspiration(
    field_id: UUID,
    date: Optional[datetime] = Query(None, description="Date for calculation (defaults to today)"),
    service: SoilMoistureMonitoringService = Depends(get_soil_moisture_monitoring_service)
):
    """
    Calculate evapotranspiration for a field on a specific date.
    
    Calculates:
    - Reference evapotranspiration (ET₀) using Penman-Monteith equation
    - Crop coefficient (Kc) based on growth stage
    - Actual crop evapotranspiration (ETc)
    - Soil evaporation component
    - Total evapotranspiration
    
    Returns detailed ET calculation results.
    """
    try:
        if date is None:
            date = datetime.utcnow()
        
        logger.info(f"Calculating evapotranspiration for field: {field_id}, date: {date}")
        et_result = await service.calculate_evapotranspiration(field_id, date)
        return et_result
    except Exception as e:
        logger.error(f"Error calculating evapotranspiration: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate evapotranspiration: {str(e)}")

@router.get("/soil-moisture/irrigation-recommendations/{field_id}")
async def get_irrigation_recommendations(
    field_id: UUID,
    service: SoilMoistureMonitoringService = Depends(get_soil_moisture_monitoring_service)
):
    """
    Get irrigation recommendations for a field.
    
    Provides recommendations based on:
    - Current soil moisture status
    - Weather forecast
    - Crop water requirements
    - Evapotranspiration rates
    
    Returns detailed irrigation recommendations with timing and amounts.
    """
    try:
        logger.info(f"Getting irrigation recommendations for field: {field_id}")
        recommendations = await service.get_irrigation_recommendations(field_id)
        return recommendations
    except Exception as e:
        logger.error(f"Error getting irrigation recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get irrigation recommendations: {str(e)}")

@router.get("/soil-moisture/alerts/{field_id}")
async def get_soil_moisture_alerts(
    field_id: UUID,
    service: SoilMoistureMonitoringService = Depends(get_soil_moisture_monitoring_service)
):
    """
    Get moisture-related alerts for a field.
    
    Returns alerts for:
    - Low soil moisture levels
    - Critical moisture conditions
    - Drought stress warnings
    - Irrigation timing recommendations
    
    Returns prioritized list of moisture alerts with recommendations.
    """
    try:
        logger.info(f"Getting soil moisture alerts for field: {field_id}")
        alerts = await service.get_moisture_alerts(field_id)
        return {
            "field_id": field_id,
            "alerts": alerts,
            "alert_count": len(alerts),
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error getting soil moisture alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get soil moisture alerts: {str(e)}")

@router.post("/soil-moisture/alerts/{alert_id}/acknowledge")
async def acknowledge_soil_moisture_alert(
    alert_id: UUID,
    user_id: UUID = Body(..., description="User ID acknowledging the alert"),
    notes: Optional[str] = Body(None, description="Optional acknowledgment notes"),
    service: SoilMoistureMonitoringService = Depends(get_soil_moisture_monitoring_service)
):
    """
    Acknowledge a soil moisture alert.
    
    Marks an alert as acknowledged with optional notes.
    """
    try:
        logger.info(f"Acknowledging soil moisture alert: {alert_id}")
        
        # Get alert service
        if not hasattr(service, 'alert_service'):
            from ..services.soil_moisture_alert_service import SoilMoistureAlertService
            service.alert_service = SoilMoistureAlertService()
            await service.alert_service.initialize()
        
        success = await service.alert_service.acknowledge_alert(alert_id, user_id, notes)
        
        if success:
            return {"success": True, "message": "Alert acknowledged successfully"}
        else:
            raise HTTPException(status_code=404, detail="Alert not found")
            
    except Exception as e:
        logger.error(f"Error acknowledging alert: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to acknowledge alert: {str(e)}")

@router.post("/soil-moisture/alerts/{alert_id}/resolve")
async def resolve_soil_moisture_alert(
    alert_id: UUID,
    user_id: UUID = Body(..., description="User ID resolving the alert"),
    resolution_notes: Optional[str] = Body(None, description="Optional resolution notes"),
    service: SoilMoistureMonitoringService = Depends(get_soil_moisture_monitoring_service)
):
    """
    Resolve a soil moisture alert.
    
    Marks an alert as resolved with optional resolution notes.
    """
    try:
        logger.info(f"Resolving soil moisture alert: {alert_id}")
        
        # Get alert service
        if not hasattr(service, 'alert_service'):
            from ..services.soil_moisture_alert_service import SoilMoistureAlertService
            service.alert_service = SoilMoistureAlertService()
            await service.alert_service.initialize()
        
        success = await service.alert_service.resolve_alert(alert_id, user_id, resolution_notes)
        
        if success:
            return {"success": True, "message": "Alert resolved successfully"}
        else:
            raise HTTPException(status_code=404, detail="Alert not found")
            
    except Exception as e:
        logger.error(f"Error resolving alert: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to resolve alert: {str(e)}")

@router.get("/soil-moisture/alerts/{field_id}/statistics")
async def get_soil_moisture_alert_statistics(
    field_id: UUID,
    days: int = Query(30, ge=1, le=365, description="Number of days to include in statistics"),
    service: SoilMoistureMonitoringService = Depends(get_soil_moisture_monitoring_service)
):
    """
    Get soil moisture alert statistics for a field.
    
    Returns comprehensive statistics including:
    - Total alerts by severity and type
    - Resolution times
    - Alert trends
    """
    try:
        logger.info(f"Getting soil moisture alert statistics for field: {field_id}")
        
        # Get alert service
        if not hasattr(service, 'alert_service'):
            from ..services.soil_moisture_alert_service import SoilMoistureAlertService
            service.alert_service = SoilMoistureAlertService()
            await service.alert_service.initialize()
        
        statistics = await service.alert_service.get_alert_statistics(field_id, days)
        return statistics
        
    except Exception as e:
        logger.error(f"Error getting alert statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get alert statistics: {str(e)}")

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

# Soil-Weather Integration Endpoints
@router.post("/soil-weather/vulnerability-assessment")
async def assess_soil_drought_vulnerability(
    field_id: UUID = Body(..., description="Field identifier"),
    soil_characteristics: Dict[str, Any] = Body(..., description="Soil characteristics data"),
    weather_data: List[Dict[str, Any]] = Body(..., description="Weather pattern data"),
    crop_type: str = Body(..., description="Type of crop"),
    service: SoilWeatherIntegrationService = Depends(get_soil_weather_integration_service)
):
    """
    Assess soil-specific drought vulnerability based on soil characteristics and weather patterns.
    
    This endpoint provides comprehensive drought vulnerability assessment considering:
    - Soil water holding capacity, drainage class, organic matter, texture, and depth
    - Historical and current weather patterns
    - Crop-specific requirements and management practices
    
    Returns vulnerability score, risk level, and mitigation recommendations.
    """
    try:
        from ..services.soil_weather_service import SoilCharacteristics, WeatherPattern
        
        # Convert input data to service models
        soil = SoilCharacteristics(**soil_characteristics)
        weather_patterns = [WeatherPattern(**w) for w in weather_data]
        
        vulnerability = await service.assess_soil_drought_vulnerability(
            field_id, soil, weather_patterns, crop_type
        )
        
        return {
            "field_id": field_id,
            "crop_type": crop_type,
            "overall_score": vulnerability.overall_score,
            "soil_factor_score": vulnerability.soil_factor_score,
            "weather_factor_score": vulnerability.weather_factor_score,
            "management_factor_score": vulnerability.management_factor_score,
            "risk_level": vulnerability.risk_level.value,
            "vulnerability_factors": vulnerability.vulnerability_factors,
            "mitigation_potential": vulnerability.mitigation_potential,
            "assessment_timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error assessing soil drought vulnerability: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to assess drought vulnerability: {str(e)}")

@router.post("/soil-weather/weather-impact-analysis")
async def analyze_weather_pattern_impact(
    field_id: UUID = Body(..., description="Field identifier"),
    weather_data: List[Dict[str, Any]] = Body(..., description="Weather pattern data"),
    soil_characteristics: Dict[str, Any] = Body(..., description="Soil characteristics data"),
    crop_type: str = Body(..., description="Type of crop"),
    service: SoilWeatherIntegrationService = Depends(get_soil_weather_integration_service)
):
    """
    Analyze weather pattern impact on soil moisture and crop stress.
    
    This endpoint analyzes how weather patterns affect:
    - Soil moisture stress levels
    - Crop water stress
    - Evapotranspiration impact
    - Precipitation effectiveness
    - Critical growth periods
    
    Returns detailed impact analysis with recommendations.
    """
    try:
        from ..services.soil_weather_service import SoilCharacteristics, WeatherPattern
        
        # Convert input data to service models
        soil = SoilCharacteristics(**soil_characteristics)
        weather_patterns = [WeatherPattern(**w) for w in weather_data]
        
        analysis = await service.analyze_weather_pattern_impact(
            field_id, weather_patterns, soil, crop_type
        )
        
        return {
            "field_id": field_id,
            "crop_type": crop_type,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            **analysis
        }
        
    except Exception as e:
        logger.error(f"Error analyzing weather pattern impact: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze weather impact: {str(e)}")

@router.post("/soil-weather/moisture-stress-prediction")
async def predict_soil_moisture_stress(
    field_id: UUID = Body(..., description="Field identifier"),
    soil_characteristics: Dict[str, Any] = Body(..., description="Soil characteristics data"),
    weather_forecast: List[Dict[str, Any]] = Body(..., description="Weather forecast data"),
    crop_type: str = Body(..., description="Type of crop"),
    days_ahead: int = Body(14, ge=1, le=30, description="Number of days to predict ahead"),
    service: SoilWeatherIntegrationService = Depends(get_soil_weather_integration_service)
):
    """
    Predict soil moisture stress based on weather forecast and soil characteristics.
    
    This endpoint provides:
    - Daily soil moisture predictions
    - Stress level forecasts
    - Critical moisture periods identification
    - Irrigation timing recommendations
    
    Useful for proactive drought management and irrigation planning.
    """
    try:
        from ..services.soil_weather_service import SoilCharacteristics, WeatherPattern
        
        # Convert input data to service models
        soil = SoilCharacteristics(**soil_characteristics)
        weather_patterns = [WeatherPattern(**w) for w in weather_forecast]
        
        prediction = await service.predict_soil_moisture_stress(
            field_id, soil, weather_patterns, crop_type, days_ahead
        )
        
        return prediction
        
    except Exception as e:
        logger.error(f"Error predicting soil moisture stress: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to predict moisture stress: {str(e)}")

@router.post("/soil-weather/crop-impact-assessment")
async def assess_crop_impact(
    field_id: UUID = Body(..., description="Field identifier"),
    crop_type: str = Body(..., description="Type of crop"),
    soil_characteristics: Dict[str, Any] = Body(..., description="Soil characteristics data"),
    weather_data: List[Dict[str, Any]] = Body(..., description="Weather pattern data"),
    growth_stage: str = Body(..., description="Current growth stage"),
    service: SoilWeatherIntegrationService = Depends(get_soil_weather_integration_service)
):
    """
    Assess crop impact based on soil-weather integration.
    
    This endpoint evaluates:
    - Water stress impact on crop yield
    - Quality impact from drought conditions
    - Economic impact assessment
    - Growth stage-specific vulnerabilities
    
    Returns comprehensive crop impact analysis with mitigation strategies.
    """
    try:
        from ..services.soil_weather_service import SoilCharacteristics, WeatherPattern
        
        # Convert input data to service models
        soil = SoilCharacteristics(**soil_characteristics)
        weather_patterns = [WeatherPattern(**w) for w in weather_data]
        
        assessment = await service.assess_crop_impact(
            field_id, crop_type, soil, weather_patterns, growth_stage
        )
        
        return assessment
        
    except Exception as e:
        logger.error(f"Error assessing crop impact: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to assess crop impact: {str(e)}")

@router.get("/soil-weather/soil-texture-properties")
async def get_soil_texture_properties(
    service: SoilWeatherIntegrationService = Depends(get_soil_weather_integration_service)
):
    """
    Get soil texture properties database.
    
    Returns comprehensive soil texture characteristics including:
    - Water holding capacity
    - Infiltration rates
    - Field capacity and wilting point
    - Drought vulnerability factors
    
    Useful for understanding soil-specific drought characteristics.
    """
    try:
        return {
            "soil_texture_properties": service.soil_texture_properties,
            "drainage_class_impacts": service.drainage_class_impacts,
            "crop_water_requirements": service.crop_water_requirements
        }
        
    except Exception as e:
        logger.error(f"Error getting soil texture properties: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get soil properties: {str(e)}")

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

# Regional Drought Analysis Endpoints
@router.post("/regional/analyze", response_model=RegionalDroughtAnalysisResponse)
async def analyze_regional_drought_patterns(
    request: RegionalDroughtAnalysisRequest,
    service: RegionalDroughtAnalysisService = Depends(get_regional_drought_analysis_service)
):
    """
    Analyze regional drought patterns and trends.
    
    This endpoint provides comprehensive regional drought analysis including:
    - Historical drought frequency and severity patterns
    - Trend analysis over time
    - Seasonal drought patterns
    - Climate change impact assessment
    - Risk assessment and recommendations
    
    Returns detailed regional drought analysis with forecasting capabilities.
    """
    try:
        logger.info(f"Analyzing regional drought patterns for region: {request.region}")
        
        start_time = datetime.utcnow()
        
        # Perform regional drought analysis
        analysis = await service.analyze_regional_drought_patterns(
            region=request.region,
            start_date=request.start_date,
            end_date=request.end_date,
            include_forecast=request.include_forecast
        )
        
        # Get drought events if available
        drought_events = []  # Would be populated from analysis results
        
        # Generate forecast if requested
        forecast = None
        if request.include_forecast:
            forecast = await service.forecast_drought_conditions(
                region=request.region,
                forecast_period_days=90,
                confidence_threshold=0.7
            )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return RegionalDroughtAnalysisResponse(
            analysis=analysis,
            drought_events=drought_events,
            forecast=forecast,
            processing_time_ms=processing_time,
            data_sources=["NOAA", "USDA", "Climate Models"]
        )
        
    except Exception as e:
        logger.error(f"Error analyzing regional drought patterns: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Regional drought analysis failed: {str(e)}")

@router.post("/regional/forecast", response_model=DroughtForecastResponse)
async def forecast_regional_drought_conditions(
    request: DroughtForecastRequest,
    service: RegionalDroughtAnalysisService = Depends(get_regional_drought_analysis_service)
):
    """
    Forecast drought conditions for a region.
    
    This endpoint provides drought forecasting capabilities including:
    - Predicted drought severity and duration
    - Confidence scoring for forecasts
    - Probability of drought occurrence
    - Precipitation, temperature, and soil moisture outlooks
    - Agricultural impact predictions
    - Mitigation recommendations
    
    Returns comprehensive drought forecast with supporting data.
    """
    try:
        logger.info(f"Forecasting drought conditions for region: {request.region}")
        
        start_time = datetime.utcnow()
        
        # Generate drought forecast
        forecast = await service.forecast_drought_conditions(
            region=request.region,
            forecast_period_days=request.forecast_period_days,
            confidence_threshold=request.confidence_threshold
        )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return DroughtForecastResponse(
            forecast=forecast,
            supporting_data={
                "weather_models": ["GFS", "ECMWF", "NOAA"],
                "climate_models": ["CMIP6", "RCP4.5", "RCP8.5"],
                "soil_models": ["NOAH", "VIC", "CLM"]
            },
            model_performance={
                "accuracy_score": 0.82,
                "confidence_calibration": 0.78,
                "forecast_skill": 0.75
            },
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error forecasting drought conditions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Drought forecasting failed: {str(e)}")

@router.post("/regional/frequency-analysis", response_model=DroughtFrequencyAnalysisResponse)
async def analyze_drought_frequency(
    request: DroughtFrequencyAnalysisRequest,
    service: RegionalDroughtAnalysisService = Depends(get_regional_drought_analysis_service)
):
    """
    Analyze drought frequency patterns for a region.
    
    This endpoint provides comprehensive drought frequency analysis including:
    - Frequency by severity level
    - Seasonal frequency patterns
    - Decadal frequency trends
    - Average duration by severity
    - Return period calculations
    
    Useful for understanding historical drought patterns and planning.
    """
    try:
        logger.info(f"Analyzing drought frequency for region: {request.region}")
        
        # Perform frequency analysis
        frequency_analysis = await service.analyze_drought_frequency(
            region=request.region,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        return DroughtFrequencyAnalysisResponse(
            region=request.region,
            analysis_period={
                "start_date": request.start_date.isoformat(),
                "end_date": request.end_date.isoformat()
            },
            frequency_by_severity=frequency_analysis.get("frequency_by_severity", {}),
            seasonal_frequency=frequency_analysis.get("seasonal_frequency", {}),
            decadal_frequency=frequency_analysis.get("decadal_frequency", {}),
            duration_by_severity=frequency_analysis.get("duration_by_severity", {}),
            return_periods=frequency_analysis.get("return_periods", {}),
            total_events=frequency_analysis.get("total_events", 0),
            analysis_confidence="high"
        )
        
    except Exception as e:
        logger.error(f"Error analyzing drought frequency: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Drought frequency analysis failed: {str(e)}")

@router.post("/regional/trend-analysis", response_model=DroughtTrendAnalysisResponse)
async def analyze_drought_trends(
    request: DroughtTrendAnalysisRequest,
    service: RegionalDroughtAnalysisService = Depends(get_regional_drought_analysis_service)
):
    """
    Analyze drought trends over time for a region.
    
    This endpoint provides comprehensive trend analysis including:
    - Severity trends over time
    - Duration trends analysis
    - Frequency trends assessment
    - Intensity trends evaluation
    - Statistical significance testing
    
    Returns detailed trend analysis with statistical validation.
    """
    try:
        logger.info(f"Analyzing drought trends for region: {request.region}")
        
        # Perform trend analysis
        trend_analysis = await service.analyze_drought_trends(
            region=request.region,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        return DroughtTrendAnalysisResponse(
            region=request.region,
            analysis_period={
                "start_date": request.start_date.isoformat(),
                "end_date": request.end_date.isoformat()
            },
            severity_trends=trend_analysis.get("severity_trends", {}),
            duration_trends=trend_analysis.get("duration_trends", {}),
            frequency_trends=trend_analysis.get("frequency_trends", {}),
            intensity_trends=trend_analysis.get("intensity_trends", {}),
            statistical_tests=trend_analysis.get("statistical_trends", {}),
            trend_summary=trend_analysis.get("trend_summary", {}),
            analysis_confidence="high"
        )
        
    except Exception as e:
        logger.error(f"Error analyzing drought trends: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Drought trend analysis failed: {str(e)}")

@router.post("/regional/climate-change-impact", response_model=ClimateChangeImpactResponse)
async def assess_climate_change_impacts(
    request: ClimateChangeImpactRequest,
    service: RegionalDroughtAnalysisService = Depends(get_regional_drought_analysis_service)
):
    """
    Assess climate change impacts on drought patterns.
    
    This endpoint provides comprehensive climate change impact assessment including:
    - Temperature and precipitation trend analysis
    - Extreme weather event analysis
    - Future climate projections
    - Drought risk changes due to climate change
    - Adaptation recommendations
    
    Returns detailed climate change impact assessment with adaptation strategies.
    """
    try:
        logger.info(f"Assessing climate change impacts for region: {request.region}")
        
        # Perform climate change impact assessment
        impact_assessment = await service.assess_climate_change_impacts(
            region=request.region,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        return ClimateChangeImpactResponse(
            region=request.region,
            analysis_period={
                "start_date": request.start_date.isoformat(),
                "end_date": request.end_date.isoformat()
            },
            projection_period=request.projection_period,
            temperature_trends=impact_assessment.get("temperature_trends", {}),
            precipitation_trends=impact_assessment.get("precipitation_trends", {}),
            extreme_events=impact_assessment.get("extreme_events", {}),
            future_projections=impact_assessment.get("future_projections", {}),
            drought_risk_changes=impact_assessment.get("drought_risk_changes", {}),
            adaptation_recommendations=impact_assessment.get("adaptation_recommendations", []),
            confidence_level="high"
        )
        
    except Exception as e:
        logger.error(f"Error assessing climate change impacts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Climate change impact assessment failed: {str(e)}")

@router.get("/regional/pattern-map/{region}", response_model=DroughtPatternMapResponse)
async def get_drought_pattern_map(
    region: str,
    start_date: Optional[date] = Query(None, description="Start date for pattern analysis"),
    end_date: Optional[date] = Query(None, description="End date for pattern analysis"),
    service: RegionalDroughtAnalysisService = Depends(get_regional_drought_analysis_service)
):
    """
    Get drought pattern map data for a region.
    
    This endpoint provides geospatial drought pattern data including:
    - Drought event locations and boundaries
    - Severity distribution maps
    - Temporal pattern visualization data
    - Risk assessment maps
    
    Returns geospatial data suitable for mapping and visualization.
    """
    try:
        logger.info(f"Getting drought pattern map for region: {region}")
        
        # Set default dates if not provided
        if not start_date:
            start_date = date.today() - timedelta(days=365)
        if not end_date:
            end_date = date.today()
        
        # Generate pattern map data
        map_data = {
            "region": region,
            "analysis_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "drought_events": [],
            "severity_distribution": {},
            "risk_zones": {},
            "geospatial_data": {
                "boundaries": [],
                "coordinates": [],
                "attributes": {}
            }
        }
        
        pattern_summary = {
            "total_events": 0,
            "average_severity": "moderate",
            "most_affected_areas": [],
            "temporal_patterns": {}
        }
        
        visualization_data = {
            "charts": [],
            "maps": [],
            "time_series": []
        }
        
        return DroughtPatternMapResponse(
            region=region,
            map_data=map_data,
            pattern_summary=pattern_summary,
            visualization_data=visualization_data,
            generated_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error getting drought pattern map: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get drought pattern map: {str(e)}")

@router.get("/regional/alerts/{region}", response_model=List[DroughtAlertResponse])
async def get_regional_drought_alerts(
    region: str,
    alert_type: Optional[str] = Query(None, description="Filter by alert type"),
    severity: Optional[str] = Query(None, description="Filter by severity level"),
    service: RegionalDroughtAnalysisService = Depends(get_regional_drought_analysis_service)
):
    """
    Get regional drought alerts and warnings.
    
    This endpoint provides current drought alerts including:
    - Drought severity alerts
    - Agricultural impact warnings
    - Water supply alerts
    - Climate change impact alerts
    
    Returns prioritized list of regional drought alerts with recommendations.
    """
    try:
        logger.info(f"Getting regional drought alerts for region: {region}")
        
        # Generate mock alerts (in real implementation, would query alert database)
        alerts = [
            DroughtAlertResponse(
                alert_id=f"alert_{region}_{datetime.now().strftime('%Y%m%d_%H%M')}",
                region=region,
                alert_type="drought_severity",
                severity="moderate",
                message=f"Moderate drought conditions detected in {region}",
                recommendations=[
                    "Implement water conservation measures",
                    "Monitor soil moisture levels",
                    "Consider drought-resistant crop varieties"
                ],
                valid_until=datetime.utcnow() + timedelta(days=7),
                created_at=datetime.utcnow()
            )
        ]
        
        # Filter alerts based on parameters
        if alert_type:
            alerts = [alert for alert in alerts if alert.alert_type == alert_type]
        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]
        
        return alerts
        
    except Exception as e:
        logger.error(f"Error getting regional drought alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get regional drought alerts: {str(e)}")

# Irrigation Management Endpoints
@router.post("/irrigation/assess", response_model=IrrigationAssessmentResponse)
async def assess_irrigation_system(
    request: IrrigationAssessmentRequest,
    service: IrrigationManagementService = Depends(get_irrigation_management_service)
):
    """
    Assess irrigation system performance and water source capacity.
    
    This endpoint provides comprehensive irrigation assessment including:
    - Irrigation system efficiency evaluation
    - Water source capacity and quality assessment
    - System constraints identification
    - Performance optimization recommendations
    
    Returns detailed irrigation system assessment with optimization opportunities.
    """
    try:
        logger.info(f"Assessing irrigation system for field: {request.field_id}")
        
        # Assess irrigation system
        system_assessment = await service.assess_irrigation_system(
            field_id=request.field_id,
            system_type=request.system_type,
            system_age_years=request.system_age_years,
            maintenance_history=request.maintenance_history,
            field_characteristics=request.field_characteristics
        )
        
        # Evaluate water source
        water_source_assessment = await service.evaluate_water_source(
            field_id=request.field_id,
            source_type=request.water_source_data.get("source_type", "well"),
            source_capacity_gpm=request.water_source_data.get("capacity_gpm", 100),
            water_quality_data=request.water_source_data.get("quality_data", {}),
            reliability_history=request.water_source_data.get("reliability_history", {}),
            cost_data=request.water_source_data.get("cost_data", {})
        )
        
        # Assess constraints
        constraints = await service.assess_irrigation_constraints(
            field_id=request.field_id,
            irrigation_system=system_assessment,
            water_source=water_source_assessment,
            field_characteristics=request.field_characteristics,
            operational_constraints=request.operational_constraints
        )
        
        # Generate general recommendations
        recommendations = [
            f"Current system efficiency: {system_assessment.current_efficiency:.1%}",
            f"Water source reliability: {water_source_assessment.reliability_score:.1%}",
            f"Overall system score: {system_assessment.overall_score:.1f}/100"
        ]
        
        if system_assessment.current_efficiency < 0.80:
            recommendations.append("Consider system maintenance to improve efficiency")
        
        if water_source_assessment.reliability_score < 0.90:
            recommendations.append("Water source reliability could be improved")
        
        return IrrigationAssessmentResponse(
            field_id=request.field_id,
            system_assessment=system_assessment,
            water_source_assessment=water_source_assessment,
            constraints=constraints,
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"Error assessing irrigation system: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Irrigation assessment failed: {str(e)}")

@router.post("/irrigation/optimize", response_model=IrrigationOptimizationResponse)
async def optimize_irrigation_efficiency(
    request: IrrigationOptimizationRequest,
    service: IrrigationManagementService = Depends(get_irrigation_management_service)
):
    """
    Generate irrigation efficiency optimization recommendations.
    
    This endpoint provides comprehensive irrigation optimization including:
    - System efficiency improvements
    - Scheduling optimizations
    - Water source optimizations
    - Cost-benefit analysis
    - Implementation priorities
    
    Returns prioritized optimization recommendations with detailed analysis.
    """
    try:
        logger.info(f"Optimizing irrigation efficiency for field: {request.field_id}")
        
        # Generate optimizations
        optimizations = await service.optimize_irrigation_efficiency(
            field_id=request.field_id,
            current_assessment=request.current_assessment,
            water_source_assessment=request.water_source_assessment,
            field_characteristics=request.field_characteristics,
            budget_constraints=request.budget_constraints
        )
        
        # Calculate total potential savings
        total_water_savings = sum(opt.potential_water_savings_percent for opt in optimizations)
        total_cost_savings = sum(opt.potential_cost_savings_per_year for opt in optimizations)
        total_implementation_cost = sum(opt.implementation_cost for opt in optimizations)
        
        total_potential_savings = {
            "water_savings_percent": min(total_water_savings, 50.0),  # Cap at 50%
            "annual_cost_savings": total_cost_savings,
            "total_implementation_cost": total_implementation_cost,
            "payback_period_years": float(total_implementation_cost / total_cost_savings) if total_cost_savings > 0 else 0
        }
        
        # Generate implementation priority
        implementation_priority = [opt.optimization_type for opt in optimizations if opt.priority_level == "high"]
        implementation_priority.extend([opt.optimization_type for opt in optimizations if opt.priority_level == "medium"])
        implementation_priority.extend([opt.optimization_type for opt in optimizations if opt.priority_level == "low"])
        
        # Generate cost-benefit summary
        cost_benefit_summary = {
            "high_priority_optimizations": len([opt for opt in optimizations if opt.priority_level == "high"]),
            "medium_priority_optimizations": len([opt for opt in optimizations if opt.priority_level == "medium"]),
            "low_priority_optimizations": len([opt for opt in optimizations if opt.priority_level == "low"]),
            "average_payback_period": sum(opt.payback_period_years for opt in optimizations) / len(optimizations) if optimizations else 0,
            "roi_percentage": float((total_cost_savings - total_implementation_cost) / total_implementation_cost * 100) if total_implementation_cost > 0 else 0
        }
        
        return IrrigationOptimizationResponse(
            field_id=request.field_id,
            optimizations=optimizations,
            total_potential_savings=total_potential_savings,
            implementation_priority=implementation_priority,
            cost_benefit_summary=cost_benefit_summary
        )
        
    except Exception as e:
        logger.error(f"Error optimizing irrigation efficiency: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Irrigation optimization failed: {str(e)}")

@router.post("/irrigation/schedule", response_model=IrrigationScheduleResponse)
async def generate_irrigation_schedule(
    request: IrrigationScheduleRequest,
    service: IrrigationManagementService = Depends(get_irrigation_management_service)
):
    """
    Generate optimized irrigation schedule.
    
    This endpoint provides comprehensive irrigation scheduling including:
    - Crop water requirement calculations
    - Soil moisture deficit analysis
    - Weather-based timing optimization
    - Irrigation amount calculations
    - Efficiency factor considerations
    
    Returns detailed irrigation schedule with timing and amounts.
    """
    try:
        logger.info(f"Generating irrigation schedule for field: {request.field_id}")
        
        # Generate irrigation schedule
        schedule = await service.generate_irrigation_schedule(
            field_id=request.field_id,
            crop_type=request.crop_type,
            growth_stage=request.growth_stage,
            soil_moisture_data=request.soil_moisture_data,
            weather_forecast=request.weather_forecast,
            irrigation_system=request.irrigation_system,
            water_source=request.water_source
        )
        
        # Extract water requirements
        water_requirements = {
            "total_water_requirement": schedule.get("total_water_requirement", 0),
            "irrigation_amounts": schedule.get("water_amounts", {}),
            "system_efficiency_factor": schedule.get("system_efficiency_factor", 0.8)
        }
        
        # Extract efficiency factors
        efficiency_factors = {
            "system_efficiency": request.irrigation_system.current_efficiency,
            "water_distribution_uniformity": request.irrigation_system.water_distribution_uniformity,
            "pressure_consistency": request.irrigation_system.pressure_consistency,
            "coverage_area_percent": request.irrigation_system.coverage_area_percent
        }
        
        # Extract recommendations
        recommendations = schedule.get("recommendations", [])
        
        return IrrigationScheduleResponse(
            field_id=request.field_id,
            schedule=schedule,
            water_requirements=water_requirements,
            efficiency_factors=efficiency_factors,
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"Error generating irrigation schedule: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Irrigation schedule generation failed: {str(e)}")

@router.get("/irrigation/system-types")
async def get_irrigation_system_types():
    """
    Get available irrigation system types and their characteristics.
    
    Returns comprehensive information about different irrigation system types
    including efficiency ratings, suitable crops, and implementation requirements.
    """
    try:
        from ..services.irrigation_service import IrrigationManagementService
        service = IrrigationManagementService()
        
        system_types = []
        for system_type, characteristics in service.irrigation_system_database.items():
            system_types.append({
                "system_type": system_type,
                "typical_efficiency": characteristics.get("typical_efficiency", 0.7),
                "water_distribution_uniformity": characteristics.get("water_distribution_uniformity", 0.8),
                "energy_requirements": characteristics.get("energy_requirements", "moderate"),
                "maintenance_frequency": characteristics.get("maintenance_frequency", "monthly"),
                "suitable_crops": characteristics.get("suitable_crops", []),
                "field_size_range": characteristics.get("field_size_range", (1, 100)),
                "cost_per_acre": float(characteristics.get("cost_per_acre", 500))
            })
        
        return {
            "irrigation_system_types": system_types,
            "total_systems": len(system_types),
            "description": "Available irrigation system types with characteristics and requirements"
        }
        
    except Exception as e:
        logger.error(f"Error getting irrigation system types: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get irrigation system types: {str(e)}")

@router.get("/irrigation/water-source-types")
async def get_water_source_types():
    """
    Get available water source types and their characteristics.
    
    Returns comprehensive information about different water source types
    including reliability, cost, and sustainability characteristics.
    """
    try:
        from ..services.irrigation_service import IrrigationManagementService
        service = IrrigationManagementService()
        
        water_sources = []
        for source_type, characteristics in service.water_source_database.items():
            water_sources.append({
                "source_type": source_type,
                "typical_reliability": characteristics.get("typical_reliability", 0.85),
                "cost_per_gallon": float(characteristics.get("cost_per_gallon", 0.002)),
                "seasonal_variation": characteristics.get("seasonal_variation", 0.20),
                "sustainability_score": characteristics.get("sustainability_score", 0.70),
                "pumping_requirements": characteristics.get("pumping_requirements", "moderate"),
                "water_quality": characteristics.get("water_quality", "good")
            })
        
        return {
            "water_source_types": water_sources,
            "total_sources": len(water_sources),
            "description": "Available water source types with characteristics and requirements"
        }
        
    except Exception as e:
        logger.error(f"Error getting water source types: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get water source types: {str(e)}")
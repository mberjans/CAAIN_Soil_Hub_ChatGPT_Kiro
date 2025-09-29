"""
Drought Management API Routes

FastAPI router for drought assessment, moisture conservation,
and monitoring endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import List, Optional, Dict, Any
import logging
import uuid
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
from ..models.water_source_models import WaterSourceAnalysisRequest
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
from ..models.practice_effectiveness_models import (
    PracticeEffectivenessRequest,
    PracticeEffectivenessResponse,
    PracticeImplementation,
    PerformanceMeasurement,
    EffectivenessValidation,
    PracticeEffectivenessReport,
    AdaptiveRecommendation,
    RegionalEffectivenessAnalysis,
    PerformanceMetric,
    ValidationStatus
)
from ..models.tillage_models import (
    TillageOptimizationRequest,
    TillageOptimizationResponse,
    TillageSystemAssessment,
    EquipmentRecommendation,
    TransitionPlan
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
from ..services.practice_effectiveness_service import PracticeEffectivenessService
from ..services.cover_management_service import (
    CoverManagementService,
    CoverManagementRequest,
    CoverManagementResponse,
    CoverCropSpecies,
    MulchMaterial
)
from .optimization_routes import router as optimization_router
from .diversification_routes import router as diversification_router

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
    calculator = WaterSavingsCalculator()
    await calculator.initialize()
    return calculator

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

async def get_practice_effectiveness_service():
    """Get practice effectiveness service instance."""
    from ..services.practice_effectiveness_service import PracticeEffectivenessService
    service = PracticeEffectivenessService()
    await service.initialize()
    return service

async def get_cover_management_service():
    """Get cover management service instance."""
    from ..services.cover_management_service import CoverManagementService
    service = CoverManagementService()
    await service.initialize()
    return service

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

# Practice Effectiveness Tracking Endpoints

@router.post("/practice-effectiveness/track-implementation", response_model=PracticeImplementation)
async def track_practice_implementation(
    practice_id: UUID = Body(..., description="ID of the conservation practice"),
    field_id: UUID = Body(..., description="Field where practice is implemented"),
    farmer_id: UUID = Body(..., description="Farmer implementing the practice"),
    start_date: date = Body(..., description="Implementation start date"),
    implementation_notes: Optional[str] = Body(None, description="Implementation notes"),
    service: PracticeEffectivenessService = Depends(get_practice_effectiveness_service)
):
    """
    Start tracking a new conservation practice implementation.
    
    This endpoint initiates tracking for conservation practice effectiveness including:
    - Practice implementation monitoring
    - Performance measurement collection
    - Effectiveness validation
    - Adaptive recommendations
    
    Returns practice implementation tracking object with unique ID.
    """
    try:
        logger.info(f"Starting practice implementation tracking: {practice_id}")
        implementation = await service.track_practice_implementation(
            practice_id=practice_id,
            field_id=field_id,
            farmer_id=farmer_id,
            start_date=start_date,
            implementation_notes=implementation_notes
        )
        return implementation
    except Exception as e:
        logger.error(f"Error tracking practice implementation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to track practice implementation: {str(e)}")

@router.post("/practice-effectiveness/record-measurement", response_model=PerformanceMeasurement)
async def record_performance_measurement(
    implementation_id: UUID = Body(..., description="ID of the practice implementation"),
    metric_type: PerformanceMetric = Body(..., description="Type of metric being measured"),
    metric_value: float = Body(..., description="Measured value"),
    metric_unit: str = Body(..., description="Unit of measurement"),
    measurement_method: str = Body(..., description="Method used for measurement"),
    measurement_source: str = Body(..., description="Source of measurement"),
    confidence_level: float = Body(0.8, ge=0, le=1, description="Confidence in measurement accuracy"),
    notes: Optional[str] = Body(None, description="Additional notes about the measurement"),
    service: PracticeEffectivenessService = Depends(get_practice_effectiveness_service)
):
    """
    Record a performance measurement for a practice implementation.
    
    This endpoint records performance measurements including:
    - Water savings achieved
    - Soil health improvements
    - Cost effectiveness metrics
    - Yield impact measurements
    - Environmental benefits
    - Farmer satisfaction scores
    
    Returns performance measurement object with calculated improvements.
    """
    try:
        logger.info(f"Recording performance measurement for implementation: {implementation_id}")
        from decimal import Decimal
        
        measurement = await service.record_performance_measurement(
            implementation_id=implementation_id,
            metric_type=metric_type,
            metric_value=Decimal(str(metric_value)),
            metric_unit=metric_unit,
            measurement_method=measurement_method,
            measurement_source=measurement_source,
            confidence_level=confidence_level,
            notes=notes
        )
        return measurement
    except Exception as e:
        logger.error(f"Error recording performance measurement: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to record performance measurement: {str(e)}")

@router.post("/practice-effectiveness/validate", response_model=EffectivenessValidation)
async def validate_practice_effectiveness(
    implementation_id: UUID = Body(..., description="ID of the practice implementation"),
    validator_type: str = Body(..., description="Type of validator (expert, algorithm, farmer)"),
    validator_id: Optional[UUID] = Body(None, description="ID of the validator"),
    validation_notes: Optional[str] = Body(None, description="Validation notes"),
    service: PracticeEffectivenessService = Depends(get_practice_effectiveness_service)
):
    """
    Validate the effectiveness of a practice implementation.
    
    This endpoint validates practice effectiveness including:
    - Overall effectiveness scoring (0-10 scale)
    - Water savings validation
    - Soil health improvement assessment
    - Cost effectiveness rating
    - Farmer satisfaction evaluation
    - Improvement recommendations
    
    Returns comprehensive validation results with recommendations.
    """
    try:
        logger.info(f"Validating practice effectiveness for implementation: {implementation_id}")
        validation = await service.validate_practice_effectiveness(
            implementation_id=implementation_id,
            validator_type=validator_type,
            validator_id=validator_id,
            validation_notes=validation_notes
        )
        return validation
    except Exception as e:
        logger.error(f"Error validating practice effectiveness: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to validate practice effectiveness: {str(e)}")

@router.post("/practice-effectiveness/generate-report", response_model=PracticeEffectivenessReport)
async def generate_effectiveness_report(
    implementation_id: UUID = Body(..., description="ID of the practice implementation"),
    report_period_start: date = Body(..., description="Report period start date"),
    report_period_end: date = Body(..., description="Report period end date"),
    service: PracticeEffectivenessService = Depends(get_practice_effectiveness_service)
):
    """
    Generate a comprehensive effectiveness report for a practice implementation.
    
    This endpoint generates detailed effectiveness reports including:
    - Overall effectiveness score and trends
    - Water savings summary and analysis
    - Soil health impact assessment
    - Cost-benefit analysis
    - Challenge identification and success factors
    - Improvement recommendations and next steps
    
    Returns comprehensive effectiveness report with actionable insights.
    """
    try:
        logger.info(f"Generating effectiveness report for implementation: {implementation_id}")
        report = await service.generate_effectiveness_report(
            implementation_id=implementation_id,
            report_period_start=report_period_start,
            report_period_end=report_period_end
        )
        return report
    except Exception as e:
        logger.error(f"Error generating effectiveness report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate effectiveness report: {str(e)}")

@router.post("/practice-effectiveness/adaptive-recommendations", response_model=List[AdaptiveRecommendation])
async def generate_adaptive_recommendations(
    implementation_id: UUID = Body(..., description="ID of the practice implementation"),
    service: PracticeEffectivenessService = Depends(get_practice_effectiveness_service)
):
    """
    Generate adaptive recommendations based on effectiveness data.
    
    This endpoint provides adaptive recommendations including:
    - Performance pattern analysis
    - Machine learning-based optimization insights
    - Implementation adjustments
    - Resource optimization recommendations
    - Timeline and priority guidance
    
    Returns prioritized adaptive recommendations with confidence scores.
    """
    try:
        logger.info(f"Generating adaptive recommendations for implementation: {implementation_id}")
        recommendations = await service.generate_adaptive_recommendations(implementation_id)
        return recommendations
    except Exception as e:
        logger.error(f"Error generating adaptive recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate adaptive recommendations: {str(e)}")

@router.post("/practice-effectiveness/get-data", response_model=PracticeEffectivenessResponse)
async def get_practice_effectiveness_data(
    request: PracticeEffectivenessRequest,
    service: PracticeEffectivenessService = Depends(get_practice_effectiveness_service)
):
    """
    Get comprehensive practice effectiveness data for a field.
    
    This endpoint retrieves comprehensive effectiveness data including:
    - All practice implementations for the field
    - Performance measurements and trends
    - Effectiveness validations and scores
    - Generated reports and insights
    - Adaptive recommendations
    - Overall effectiveness summary
    
    Returns complete effectiveness tracking data with analysis.
    """
    try:
        logger.info(f"Getting practice effectiveness data for field: {request.field_id}")
        response = await service.get_practice_effectiveness_data(request)
        return response
    except Exception as e:
        logger.error(f"Error getting practice effectiveness data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get practice effectiveness data: {str(e)}")

@router.post("/practice-effectiveness/regional-analysis", response_model=RegionalEffectivenessAnalysis)
async def generate_regional_effectiveness_analysis(
    region: str = Body(..., description="Geographic region for analysis"),
    analysis_period_start: date = Body(..., description="Analysis period start date"),
    analysis_period_end: date = Body(..., description="Analysis period end date"),
    service: PracticeEffectivenessService = Depends(get_practice_effectiveness_service)
):
    """
    Generate regional effectiveness analysis for conservation practices.
    
    This endpoint provides regional effectiveness analysis including:
    - Practice types analyzed in the region
    - Average effectiveness scores
    - Most effective practices identification
    - Regional challenges and success factors
    - Optimization opportunities
    - Cross-farm learning insights
    
    Returns comprehensive regional effectiveness analysis with recommendations.
    """
    try:
        logger.info(f"Generating regional effectiveness analysis for region: {region}")
        analysis = await service.generate_regional_effectiveness_analysis(
            region=region,
            analysis_period_start=analysis_period_start,
            analysis_period_end=analysis_period_end
        )
        return analysis
    except Exception as e:
        logger.error(f"Error generating regional effectiveness analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate regional effectiveness analysis: {str(e)}")

@router.get("/practice-effectiveness/metrics")
async def get_available_performance_metrics():
    """
    Get available performance metrics for practice effectiveness tracking.
    
    Returns comprehensive list of performance metrics including:
    - Water savings measurements
    - Soil health indicators
    - Cost effectiveness metrics
    - Yield impact measurements
    - Environmental benefits
    - Farmer satisfaction indicators
    
    Useful for understanding what metrics can be tracked and measured.
    """
    try:
        metrics = [
            {
                "metric_type": PerformanceMetric.WATER_SAVINGS.value,
                "description": "Water savings achieved through conservation practices",
                "unit_examples": ["gallons", "acre-inches", "percent"],
                "measurement_methods": ["irrigation records", "soil moisture sensors", "water meters"]
            },
            {
                "metric_type": PerformanceMetric.SOIL_HEALTH.value,
                "description": "Soil health improvements from conservation practices",
                "unit_examples": ["organic matter percent", "soil structure score", "infiltration rate"],
                "measurement_methods": ["soil tests", "visual assessment", "penetration tests"]
            },
            {
                "metric_type": PerformanceMetric.COST_EFFECTIVENESS.value,
                "description": "Cost effectiveness of conservation practice implementation",
                "unit_examples": ["dollars per acre", "cost per unit saved", "ROI percent"],
                "measurement_methods": ["financial records", "cost tracking", "benefit analysis"]
            },
            {
                "metric_type": PerformanceMetric.YIELD_IMPACT.value,
                "description": "Crop yield impact from conservation practices",
                "unit_examples": ["bushels per acre", "tons per acre", "yield percent change"],
                "measurement_methods": ["harvest records", "yield monitors", "field measurements"]
            },
            {
                "metric_type": PerformanceMetric.ENVIRONMENTAL_BENEFIT.value,
                "description": "Environmental benefits from conservation practices",
                "unit_examples": ["carbon sequestered", "erosion reduced", "biodiversity score"],
                "measurement_methods": ["environmental monitoring", "soil sampling", "wildlife surveys"]
            },
            {
                "metric_type": PerformanceMetric.FARMER_SATISFACTION.value,
                "description": "Farmer satisfaction with conservation practice implementation",
                "unit_examples": ["satisfaction score", "recommendation rating", "adoption likelihood"],
                "measurement_methods": ["surveys", "interviews", "feedback forms"]
            }
        ]
        
        return {
            "available_metrics": metrics,
            "total_metrics": len(metrics),
            "description": "Comprehensive list of performance metrics for conservation practice effectiveness tracking"
        }
    except Exception as e:
        logger.error(f"Error getting available performance metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get available performance metrics: {str(e)}")

@router.get("/practice-effectiveness/health")
async def practice_effectiveness_health():
    """Health check endpoint for practice effectiveness tracking service."""
    return {
        "status": "healthy",
        "service": "practice-effectiveness-tracking",
        "timestamp": datetime.utcnow().isoformat(),
        "features": [
            "practice_implementation_tracking",
            "performance_measurement_collection",
            "effectiveness_validation",
            "adaptive_recommendations",
            "regional_effectiveness_analysis",
            "comprehensive_reporting"
        ]
    }

# Water Source Analysis Endpoints

@router.post("/water-source-analysis")
async def analyze_water_sources(request: WaterSourceAnalysisRequest):
    """
    Perform comprehensive water source and availability analysis.
    
    This endpoint provides detailed analysis of water sources including:
    - Water source evaluation and assessment
    - Availability forecasting
    - Water budget planning
    - Drought contingency planning
    - Alternative source identification
    - Usage optimization recommendations
    
    Agricultural Use Cases:
    - Farm water resource planning and management
    - Drought preparedness and contingency planning
    - Water source diversification strategies
    - Cost optimization for water usage
    - Sustainability assessment of water sources
    """
    try:
        from ..services.water_source_analysis_service import WaterSourceAnalysisService
        
        service = WaterSourceAnalysisService()
        await service.initialize()
        
        try:
            analysis_response = await service.analyze_water_sources(request)
            
            logger.info(f"Water source analysis completed for farm: {request.farm_location_id}")
            
            return {
                "success": True,
                "analysis_id": str(uuid.uuid4()),
                "farm_location_id": str(request.farm_location_id),
                "field_id": str(request.field_id),
                "analysis_date": analysis_response.analysis_date.isoformat(),
                "overall_reliability_score": analysis_response.overall_reliability_score,
                "source_count": len(analysis_response.source_assessments),
                "recommendations_count": len(analysis_response.recommendations),
                "analysis_summary": {
                    "total_available_capacity_gpm": analysis_response.water_budget_plan.total_available_capacity_gpm,
                    "daily_requirement_gallons": analysis_response.water_budget_plan.daily_requirement_gallons,
                    "capacity_utilization_percent": analysis_response.water_budget_plan.capacity_utilization_percent,
                    "annual_cost_estimate": float(analysis_response.water_budget_plan.annual_cost_estimate),
                    "potential_savings_percent": analysis_response.usage_optimization.savings_percent
                },
                "source_assessments": [
                    {
                        "source_type": assessment.source_type.value,
                        "available_capacity_gpm": assessment.available_capacity_gpm,
                        "water_quality_score": assessment.water_quality_score,
                        "reliability_score": assessment.reliability_score,
                        "cost_per_gallon": float(assessment.cost_per_gallon),
                        "seasonal_variation_percent": assessment.seasonal_variation_percent,
                        "sustainability_score": assessment.sustainability_score,
                        "regulatory_compliance": assessment.regulatory_compliance
                    }
                    for assessment in analysis_response.source_assessments
                ],
                "availability_forecast": {
                    "forecast_period_days": analysis_response.availability_forecast.forecast_period_days,
                    "confidence_score": analysis_response.availability_forecast.confidence_score,
                    "last_updated": analysis_response.availability_forecast.last_updated.isoformat(),
                    "forecast_summary": {
                        "avg_daily_capacity_gpm": sum(
                            day["total_available_capacity_gpm"] 
                            for day in analysis_response.availability_forecast.forecast_data
                        ) / len(analysis_response.availability_forecast.forecast_data)
                    }
                },
                "water_budget_plan": {
                    "total_available_capacity_gpm": analysis_response.water_budget_plan.total_available_capacity_gpm,
                    "daily_requirement_gallons": analysis_response.water_budget_plan.daily_requirement_gallons,
                    "capacity_utilization_percent": analysis_response.water_budget_plan.capacity_utilization_percent,
                    "annual_cost_estimate": float(analysis_response.water_budget_plan.annual_cost_estimate),
                    "seasonal_budget": analysis_response.water_budget_plan.seasonal_budget
                },
                "drought_contingency_plan": {
                    "reliable_sources": [source.value for source in analysis_response.drought_contingency_plan.reliable_sources],
                    "alternative_sources": [source.value for source in analysis_response.drought_contingency_plan.alternative_sources],
                    "contingency_scenarios": analysis_response.drought_contingency_plan.contingency_scenarios,
                    "emergency_contacts": analysis_response.drought_contingency_plan.emergency_contacts
                },
                "alternative_sources": [
                    {
                        "source_type": alt.source_type.value,
                        "description": alt.description,
                        "feasibility_score": alt.feasibility_score,
                        "estimated_cost_per_gallon": float(alt.estimated_cost_per_gallon),
                        "implementation_timeline_days": alt.implementation_timeline_days,
                        "required_infrastructure": alt.required_infrastructure,
                        "sustainability_score": alt.sustainability_score
                    }
                    for alt in analysis_response.alternative_sources
                ],
                "usage_optimization": {
                    "optimization_plan": analysis_response.usage_optimization.optimization_plan,
                    "total_daily_cost": analysis_response.usage_optimization.total_daily_cost,
                    "potential_savings_per_day": analysis_response.usage_optimization.potential_savings_per_day,
                    "savings_percent": analysis_response.usage_optimization.savings_percent,
                    "optimization_factors": analysis_response.usage_optimization.optimization_factors
                },
                "recommendations": analysis_response.recommendations
            }
            
        finally:
            await service.cleanup()
            
    except Exception as e:
        logger.error(f"Error analyzing water sources: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze water sources: {str(e)}")

@router.get("/water-source-analysis/source-types")
async def get_water_source_analysis_types():
    """
    Get comprehensive water source types and their characteristics for analysis.
    
    Returns detailed information about different water source types including
    reliability factors, quality concerns, cost factors, and sustainability scores.
    """
    try:
        from ..services.water_source_analysis_service import WaterSourceAnalysisService
        
        service = WaterSourceAnalysisService()
        
        source_types = []
        for source_type, characteristics in service.water_source_database.items():
            source_types.append({
                "source_type": source_type,
                "description": characteristics.get("description", ""),
                "typical_depth_range": characteristics.get("typical_depth_range", (0, 0)),
                "reliability_factors": characteristics.get("reliability_factors", []),
                "quality_concerns": characteristics.get("quality_concerns", []),
                "seasonal_variation": characteristics.get("seasonal_variation", 0.2),
                "cost_factors": characteristics.get("cost_factors", []),
                "sustainability_score": characteristics.get("sustainability_score", 0.5),
                "regulatory_requirements": characteristics.get("regulatory_requirements", []),
                "drought_resilience": characteristics.get("drought_resilience", 0.5)
            })
        
        return {
            "water_source_types": source_types,
            "total_sources": len(source_types),
            "description": "Comprehensive water source types with analysis characteristics"
        }
        
    except Exception as e:
        logger.error(f"Error getting water source analysis types: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get water source analysis types: {str(e)}")

@router.get("/water-source-analysis/health")
async def water_source_analysis_health():
    """Health check endpoint for water source analysis service."""
    return {
        "status": "healthy",
        "service": "water-source-analysis",
        "timestamp": datetime.utcnow().isoformat(),
        "features": [
            "water_source_evaluation",
            "availability_forecasting", 
            "water_budget_planning",
            "drought_contingency_planning",
            "alternative_source_identification",
            "usage_optimization"
        ]
    }

# Tillage Optimization Endpoints

@router.post("/tillage-optimization/optimize", response_model=TillageOptimizationResponse)
async def optimize_tillage_system(request: TillageOptimizationRequest):
    """
    Optimize tillage system for drought management and water conservation.
    
    This endpoint provides comprehensive tillage system optimization including:
    - Assessment of current tillage practices
    - Evaluation of alternative tillage systems
    - Equipment recommendations with cost analysis
    - Transition planning for system changes
    - Water conservation and soil health impact analysis
    - Economic analysis and ROI calculations
    
    Agricultural Benefits:
    - Water conservation through reduced soil disturbance
    - Improved soil health and organic matter accumulation
    - Erosion control and soil structure preservation
    - Reduced fuel consumption and labor requirements
    - Enhanced drought resilience
    """
    try:
        from ..services.tillage_service import TillageOptimizationService
        
        service = TillageOptimizationService()
        result = await service.optimize_tillage_system(request)
        
        logger.info(f"Tillage optimization completed for field {request.field_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error in tillage optimization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Tillage optimization failed: {str(e)}")

@router.get("/tillage-optimization/systems")
async def get_tillage_systems():
    """
    Get available tillage systems and their characteristics.
    
    Returns comprehensive information about different tillage systems
    including water conservation potential, soil health benefits,
    equipment requirements, and implementation considerations.
    """
    try:
        from ..models.tillage_models import TillageSystem
        
        systems = []
        for system in TillageSystem:
            systems.append({
                "system": system.value,
                "name": system.value.replace("_", " ").title(),
                "description": _get_tillage_system_description(system),
                "water_conservation_potential": _get_water_conservation_potential(system),
                "soil_health_benefits": _get_soil_health_benefits(system),
                "equipment_requirements": _get_equipment_requirements(system),
                "implementation_considerations": _get_implementation_considerations(system)
            })
        
        return {
            "tillage_systems": systems,
            "total_systems": len(systems),
            "description": "Comprehensive tillage systems for drought management"
        }
        
    except Exception as e:
        logger.error(f"Error getting tillage systems: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get tillage systems: {str(e)}")

@router.get("/tillage-optimization/equipment")
async def get_tillage_equipment():
    """
    Get available tillage equipment and specifications.
    
    Returns detailed information about tillage equipment including
    cost estimates, fuel consumption, labor requirements, and
    compatibility with different soil types and field conditions.
    """
    try:
        from ..models.tillage_models import TillageEquipment
        
        equipment = []
        for eq_type in TillageEquipment:
            equipment.append({
                "equipment_type": eq_type.value,
                "name": eq_type.value.replace("_", " ").title(),
                "description": _get_equipment_description(eq_type),
                "typical_cost_range": _get_equipment_cost_range(eq_type),
                "fuel_consumption": _get_fuel_consumption(eq_type),
                "labor_requirements": _get_labor_requirements(eq_type),
                "soil_compatibility": _get_soil_compatibility(eq_type),
                "maintenance_requirements": _get_maintenance_requirements(eq_type)
            })
        
        return {
            "tillage_equipment": equipment,
            "total_equipment": len(equipment),
            "description": "Comprehensive tillage equipment database"
        }
        
    except Exception as e:
        logger.error(f"Error getting tillage equipment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get tillage equipment: {str(e)}")

@router.get("/tillage-optimization/transition-guide")
async def get_transition_guide(
    current_system: str = Query(..., description="Current tillage system"),
    target_system: str = Query(..., description="Target tillage system")
):
    """
    Get transition guide between tillage systems.
    
    Provides step-by-step guidance for transitioning from one
    tillage system to another, including timeline, equipment needs,
    cost estimates, and risk mitigation strategies.
    """
    try:
        from ..models.tillage_models import TillageSystem, TillageOptimizationValidator
        
        # Validate systems
        try:
            current = TillageSystem(current_system)
            target = TillageSystem(target_system)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid tillage system")
        
        validator = TillageOptimizationValidator()
        difficulty = validator.calculate_transition_difficulty(current, target)
        
        transition_guide = {
            "current_system": current.value,
            "target_system": target.value,
            "transition_difficulty": difficulty,
            "estimated_duration_years": _get_transition_duration(difficulty),
            "phases": _get_transition_phases(current, target),
            "equipment_needs": _get_transition_equipment_needs(current, target),
            "cost_estimates": _get_transition_cost_estimates(current, target),
            "risk_factors": _get_transition_risks(current, target),
            "success_factors": _get_success_factors(current, target),
            "monitoring_metrics": _get_monitoring_metrics(target)
        }
        
        return transition_guide
        
    except Exception as e:
        logger.error(f"Error getting transition guide: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get transition guide: {str(e)}")

@router.get("/tillage-optimization/health")
async def tillage_optimization_health():
    """Health check endpoint for tillage optimization service."""
    return {
        "status": "healthy",
        "service": "tillage-optimization",
        "timestamp": datetime.utcnow().isoformat(),
        "features": [
            "tillage_system_assessment",
            "equipment_recommendations",
            "transition_planning",
            "water_conservation_analysis",
            "soil_health_optimization",
            "economic_analysis",
            "drought_resilience_planning"
        ]
    }

# Helper functions for tillage optimization endpoints

def _get_tillage_system_description(system):
    """Get description for tillage system."""
    descriptions = {
        TillageSystem.NO_TILL: "Complete elimination of tillage operations, planting directly into undisturbed soil",
        TillageSystem.STRIP_TILL: "Tillage only in narrow strips where seeds will be planted",
        TillageSystem.VERTICAL_TILL: "Minimal soil disturbance using vertical tillage tools",
        TillageSystem.REDUCED_TILL: "Reduced frequency and intensity of tillage operations",
        TillageSystem.MINIMUM_TILL: "Minimal tillage required for seedbed preparation",
        TillageSystem.CONVENTIONAL: "Traditional intensive tillage with moldboard plow"
    }
    return descriptions.get(system, "Tillage system description not available")

def _get_water_conservation_potential(system):
    """Get water conservation potential for tillage system."""
    potential = {
        TillageSystem.NO_TILL: "Excellent (90-95%)",
        TillageSystem.STRIP_TILL: "Very Good (80-85%)",
        TillageSystem.VERTICAL_TILL: "Good (70-75%)",
        TillageSystem.REDUCED_TILL: "Moderate (60-65%)",
        TillageSystem.MINIMUM_TILL: "Fair (50-55%)",
        TillageSystem.CONVENTIONAL: "Poor (30-35%)"
    }
    return potential.get(system, "Unknown")

def _get_soil_health_benefits(system):
    """Get soil health benefits for tillage system."""
    benefits = {
        TillageSystem.NO_TILL: ["Preserves soil structure", "Increases organic matter", "Enhances biological activity"],
        TillageSystem.STRIP_TILL: ["Balanced soil disturbance", "Maintains soil structure", "Supports biological activity"],
        TillageSystem.VERTICAL_TILL: ["Minimal soil disturbance", "Preserves soil layers", "Reduces compaction"],
        TillageSystem.REDUCED_TILL: ["Moderate soil health benefits", "Gradual improvement", "Reduced erosion"],
        TillageSystem.MINIMUM_TILL: ["Some soil health benefits", "Limited disturbance", "Basic erosion control"],
        TillageSystem.CONVENTIONAL: ["Limited soil health benefits", "High disturbance", "Erosion risk"]
    }
    return benefits.get(system, [])

def _get_equipment_requirements(system):
    """Get equipment requirements for tillage system."""
    requirements = {
        TillageSystem.NO_TILL: ["No-till drill", "Herbicide application equipment", "Cover crop seeder"],
        TillageSystem.STRIP_TILL: ["Strip-till implement", "No-till drill", "Fertilizer applicator"],
        TillageSystem.VERTICAL_TILL: ["Vertical tillage tool", "Seed drill", "Fertilizer spreader"],
        TillageSystem.REDUCED_TILL: ["Chisel plow", "Field cultivator", "Seed drill"],
        TillageSystem.MINIMUM_TILL: ["Disk harrow", "Field cultivator", "Seed drill"],
        TillageSystem.CONVENTIONAL: ["Moldboard plow", "Disk harrow", "Field cultivator", "Seed drill"]
    }
    return requirements.get(system, [])

def _get_implementation_considerations(system):
    """Get implementation considerations for tillage system."""
    considerations = {
        TillageSystem.NO_TILL: ["Requires good soil drainage", "May need gradual transition", "Weed management strategy needed"],
        TillageSystem.STRIP_TILL: ["Precise equipment setup required", "Timing critical", "Soil condition dependent"],
        TillageSystem.VERTICAL_TILL: ["Equipment calibration important", "Soil moisture dependent", "Depth control critical"],
        TillageSystem.REDUCED_TILL: ["Easier transition", "Flexible timing", "Moderate equipment needs"],
        TillageSystem.MINIMUM_TILL: ["Simple implementation", "Standard equipment", "Flexible approach"],
        TillageSystem.CONVENTIONAL: ["Traditional approach", "Well-established practices", "High equipment needs"]
    }
    return considerations.get(system, [])

def _get_equipment_description(eq_type):
    """Get description for equipment type."""
    descriptions = {
        TillageEquipment.NO_TILL_DRILL: "Specialized drill for planting into undisturbed soil",
        TillageEquipment.STRIP_TILL_IMPLEMENT: "Equipment for tillage in narrow strips",
        TillageEquipment.CHISEL_PLOW: "Deep tillage tool for soil loosening",
        TillageEquipment.MOLDBOARD_PLOW: "Traditional plow for complete soil inversion",
        TillageEquipment.DISK_HARROW: "Shallow tillage tool for seedbed preparation",
        TillageEquipment.FIELD_CULTIVATOR: "Multi-purpose tillage tool",
        TillageEquipment.VERTICAL_TILLAGE_TOOL: "Minimal disturbance tillage tool",
        TillageEquipment.ROTARY_HOE: "Shallow cultivation tool",
        TillageEquipment.ROW_CULTIVATOR: "Inter-row cultivation equipment"
    }
    return descriptions.get(eq_type, "Equipment description not available")

def _get_equipment_cost_range(eq_type):
    """Get cost range for equipment type."""
    cost_ranges = {
        TillageEquipment.NO_TILL_DRILL: "$70,000 - $90,000",
        TillageEquipment.STRIP_TILL_IMPLEMENT: "$60,000 - $80,000",
        TillageEquipment.CHISEL_PLOW: "$30,000 - $50,000",
        TillageEquipment.MOLDBOARD_PLOW: "$20,000 - $35,000",
        TillageEquipment.DISK_HARROW: "$15,000 - $25,000",
        TillageEquipment.FIELD_CULTIVATOR: "$25,000 - $40,000",
        TillageEquipment.VERTICAL_TILLAGE_TOOL: "$40,000 - $60,000",
        TillageEquipment.ROTARY_HOE: "$10,000 - $20,000",
        TillageEquipment.ROW_CULTIVATOR: "$15,000 - $30,000"
    }
    return cost_ranges.get(eq_type, "Cost range not available")

def _get_fuel_consumption(eq_type):
    """Get fuel consumption for equipment type."""
    fuel_consumption = {
        TillageEquipment.NO_TILL_DRILL: "0.5-0.7 gallons/acre",
        TillageEquipment.STRIP_TILL_IMPLEMENT: "0.8-1.0 gallons/acre",
        TillageEquipment.CHISEL_PLOW: "1.2-1.5 gallons/acre",
        TillageEquipment.MOLDBOARD_PLOW: "2.0-2.5 gallons/acre",
        TillageEquipment.DISK_HARROW: "1.5-2.0 gallons/acre",
        TillageEquipment.FIELD_CULTIVATOR: "1.0-1.3 gallons/acre",
        TillageEquipment.VERTICAL_TILLAGE_TOOL: "1.0-1.2 gallons/acre",
        TillageEquipment.ROTARY_HOE: "0.8-1.0 gallons/acre",
        TillageEquipment.ROW_CULTIVATOR: "0.5-0.7 gallons/acre"
    }
    return fuel_consumption.get(eq_type, "Fuel consumption not available")

def _get_labor_requirements(eq_type):
    """Get labor requirements for equipment type."""
    labor_requirements = {
        TillageEquipment.NO_TILL_DRILL: "0.3-0.5 hours/acre",
        TillageEquipment.STRIP_TILL_IMPLEMENT: "0.5-0.7 hours/acre",
        TillageEquipment.CHISEL_PLOW: "0.7-1.0 hours/acre",
        TillageEquipment.MOLDBOARD_PLOW: "1.0-1.3 hours/acre",
        TillageEquipment.DISK_HARROW: "0.8-1.0 hours/acre",
        TillageEquipment.FIELD_CULTIVATOR: "0.6-0.8 hours/acre",
        TillageEquipment.VERTICAL_TILLAGE_TOOL: "0.6-0.8 hours/acre",
        TillageEquipment.ROTARY_HOE: "0.4-0.6 hours/acre",
        TillageEquipment.ROW_CULTIVATOR: "0.3-0.5 hours/acre"
    }
    return labor_requirements.get(eq_type, "Labor requirements not available")

def _get_soil_compatibility(eq_type):
    """Get soil compatibility for equipment type."""
    soil_compatibility = {
        TillageEquipment.NO_TILL_DRILL: ["Loam", "Sandy loam", "Silt loam"],
        TillageEquipment.STRIP_TILL_IMPLEMENT: ["Clay loam", "Loam", "Sandy loam"],
        TillageEquipment.CHISEL_PLOW: ["Clay", "Clay loam", "Loam"],
        TillageEquipment.MOLDBOARD_PLOW: ["Clay", "Clay loam", "Loam"],
        TillageEquipment.DISK_HARROW: ["Sandy loam", "Loam", "Silt loam"],
        TillageEquipment.FIELD_CULTIVATOR: ["All soil types"],
        TillageEquipment.VERTICAL_TILLAGE_TOOL: ["Loam", "Sandy loam", "Silt loam"],
        TillageEquipment.ROTARY_HOE: ["All soil types"],
        TillageEquipment.ROW_CULTIVATOR: ["All soil types"]
    }
    return soil_compatibility.get(eq_type, [])

def _get_maintenance_requirements(eq_type):
    """Get maintenance requirements for equipment type."""
    maintenance = {
        TillageEquipment.NO_TILL_DRILL: "High - precision components",
        TillageEquipment.STRIP_TILL_IMPLEMENT: "Medium-High - precision setup",
        TillageEquipment.CHISEL_PLOW: "Medium - wear parts",
        TillageEquipment.MOLDBOARD_PLOW: "Medium - wear parts",
        TillageEquipment.DISK_HARROW: "Medium - disk maintenance",
        TillageEquipment.FIELD_CULTIVATOR: "Low-Medium - standard maintenance",
        TillageEquipment.VERTICAL_TILLAGE_TOOL: "Medium - precision components",
        TillageEquipment.ROTARY_HOE: "Low - simple design",
        TillageEquipment.ROW_CULTIVATOR: "Low-Medium - standard maintenance"
    }
    return maintenance.get(eq_type, "Maintenance requirements not available")

def _get_transition_duration(difficulty):
    """Get transition duration based on difficulty."""
    durations = {
        "low": 1,
        "medium": 2,
        "high": 3
    }
    return durations.get(difficulty, 2)

def _get_transition_phases(current, target):
    """Get transition phases."""
    phases = [
        {
            "phase": "Planning",
            "duration_months": 3,
            "description": "Assessment and planning phase",
            "activities": ["Soil testing", "Equipment evaluation", "Strategy development"]
        },
        {
            "phase": "Preparation", 
            "duration_months": 6,
            "description": "Preparation and equipment acquisition",
            "activities": ["Equipment purchase", "Staff training", "Field preparation"]
        },
        {
            "phase": "Implementation",
            "duration_months": 12,
            "description": "Initial implementation and monitoring",
            "activities": ["System implementation", "Performance monitoring", "Adjustments"]
        },
        {
            "phase": "Optimization",
            "duration_months": 12,
            "description": "System optimization and refinement",
            "activities": ["Performance optimization", "Practice refinement", "Long-term planning"]
        }
    ]
    return phases

def _get_transition_equipment_needs(current, target):
    """Get equipment needs for transition."""
    if target == TillageSystem.NO_TILL:
        return ["No-till drill", "Herbicide application equipment", "Cover crop seeder"]
    elif target == TillageSystem.STRIP_TILL:
        return ["Strip-till implement", "No-till drill", "Fertilizer applicator"]
    else:
        return ["Appropriate tillage equipment", "Seed drill", "Fertilizer spreader"]

def _get_transition_cost_estimates(current, target):
    """Get cost estimates for transition."""
    if target == TillageSystem.NO_TILL:
        return {
            "equipment": "$70,000 - $90,000",
            "training": "$2,000 - $5,000",
            "soil_testing": "$500 - $1,000",
            "total": "$72,500 - $96,000"
        }
    elif target == TillageSystem.STRIP_TILL:
        return {
            "equipment": "$60,000 - $80,000",
            "training": "$1,500 - $3,000",
            "soil_testing": "$500 - $1,000",
            "total": "$62,000 - $84,000"
        }
    else:
        return {
            "equipment": "$30,000 - $50,000",
            "training": "$1,000 - $2,000",
            "soil_testing": "$500 - $1,000",
            "total": "$31,500 - $53,000"
        }

def _get_transition_risks(current, target):
    """Get transition risks."""
    return [
        {
            "risk": "Yield reduction",
            "probability": "Medium",
            "impact": "Medium",
            "mitigation": "Gradual transition and proper soil preparation"
        },
        {
            "risk": "Equipment failure",
            "probability": "Low",
            "impact": "High",
            "mitigation": "Equipment maintenance and backup plans"
        },
        {
            "risk": "Weed pressure",
            "probability": "High",
            "impact": "Medium",
            "mitigation": "Integrated weed management strategy"
        }
    ]

def _get_success_factors(current, target):
    """Get success factors for transition."""
    return [
        "Proper soil preparation and drainage",
        "Appropriate equipment selection and calibration",
        "Integrated pest management strategy",
        "Gradual implementation approach",
        "Regular monitoring and adjustment",
        "Staff training and education"
    ]

def _get_monitoring_metrics(target):
    """Get monitoring metrics for target system."""
    return [
        "Soil moisture retention",
        "Soil organic matter content",
        "Erosion indicators",
        "Fuel consumption",
        "Labor efficiency",
        "Crop yield and quality",
        "Weed pressure",
        "Soil compaction levels"
    ]


# Tillage Transition Planning Endpoints

@router.post("/tillage-transition-planning/comprehensive-plan")
async def create_comprehensive_transition_plan(
    current_system: str = Query(..., description="Current tillage system"),
    target_system: str = Query(..., description="Target tillage system"),
    field_conditions: TillageOptimizationRequest = Body(..., description="Field conditions and constraints"),
    transition_preferences: Dict[str, Any] = Body(default_factory=dict, description="Transition preferences")
):
    """
    Create comprehensive multi-year tillage transition plan.
    
    This endpoint provides comprehensive transition planning including:
    - Multi-year timeline with detailed phases
    - Practice adaptation recommendations
    - Troubleshooting support system
    - Success monitoring framework
    - Educational resources and training
    - Expert consultation planning
    - Peer networking opportunities
    - Extension services integration
    - Equipment dealer coordination
    
    Agricultural Benefits:
    - Structured approach to tillage system transition
    - Risk mitigation and success optimization
    - Access to expert knowledge and peer experience
    - Integration with local extension services
    - Comprehensive support throughout transition process
    """
    try:
        from ..models.tillage_models import TillageSystem
        from ..services.tillage_transition_planning_service import TillageTransitionPlanningService
        
        # Validate tillage systems
        try:
            current = TillageSystem(current_system)
            target = TillageSystem(target_system)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid tillage system")
        
        # Create transition planning service
        service = TillageTransitionPlanningService()
        
        # Generate comprehensive transition plan
        transition_plan = await service.create_comprehensive_transition_plan(
            current, target, field_conditions, transition_preferences
        )
        
        logger.info(f"Comprehensive transition plan created: {transition_plan['plan_id']}")
        return transition_plan
        
    except Exception as e:
        logger.error(f"Error creating transition plan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transition planning failed: {str(e)}")


@router.get("/tillage-transition-planning/feasibility-assessment")
async def assess_transition_feasibility(
    current_system: str = Query(..., description="Current tillage system"),
    target_system: str = Query(..., description="Target tillage system"),
    soil_type: str = Query(..., description="Primary soil type"),
    field_size_acres: float = Query(..., description="Field size in acres"),
    slope_percent: float = Query(..., description="Field slope percentage"),
    organic_matter_percent: float = Query(..., description="Soil organic matter percentage")
):
    """
    Assess feasibility of tillage system transition.
    
    Provides detailed feasibility assessment including:
    - Feasibility score and level
    - Key factors affecting feasibility
    - Potential challenges and recommendations
    - Transition difficulty assessment
    
    Agricultural Use Cases:
    - Pre-transition planning and decision making
    - Risk assessment and mitigation planning
    - Resource allocation and timeline planning
    """
    try:
        from ..models.tillage_models import TillageSystem, TillageOptimizationRequest
        from ..services.tillage_transition_planning_service import TillageTransitionPlanningService
        
        # Validate tillage systems
        try:
            current = TillageSystem(current_system)
            target = TillageSystem(target_system)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid tillage system")
        
        # Create field conditions object
        field_conditions = TillageOptimizationRequest(
            field_id=uuid4(),
            current_tillage_system=current,
            soil_type=soil_type,
            soil_texture=f"{soil_type} soil",
            field_size_acres=field_size_acres,
            slope_percent=slope_percent,
            drainage_class="moderate",
            organic_matter_percent=organic_matter_percent,
            compaction_level="moderate",
            crop_rotation=["corn", "soybean"],
            water_conservation_priority=8.0,
            soil_health_priority=7.0,
            labor_availability=6.0
        )
        
        # Create service and assess feasibility
        service = TillageTransitionPlanningService()
        feasibility_assessment = await service._assess_transition_feasibility(
            current, target, field_conditions
        )
        
        return {
            "current_system": current_system,
            "target_system": target_system,
            "feasibility_assessment": feasibility_assessment,
            "recommendation": "Proceed with transition" if feasibility_assessment["feasibility_score"] >= 70 else "Consider gradual approach or alternative systems"
        }
        
    except Exception as e:
        logger.error(f"Error assessing feasibility: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Feasibility assessment failed: {str(e)}")


@router.get("/tillage-transition-planning/troubleshooting-guide")
async def get_troubleshooting_guide(
    tillage_system: str = Query(..., description="Tillage system for troubleshooting")
):
    """
    Get troubleshooting guide for specific tillage system.
    
    Provides comprehensive troubleshooting support including:
    - Common issues and symptoms
    - Diagnostic procedures
    - Solution strategies
    - Prevention methods
    - Expert contacts
    - Emergency procedures
    
    Agricultural Use Cases:
    - Problem diagnosis and resolution
    - Preventive maintenance planning
    - Emergency response procedures
    - Expert consultation coordination
    """
    try:
        from ..models.tillage_models import TillageSystem
        from ..services.tillage_transition_planning_service import TillageTransitionPlanningService
        
        # Validate tillage system
        try:
            system = TillageSystem(tillage_system)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid tillage system")
        
        # Create service and get troubleshooting guide
        service = TillageTransitionPlanningService()
        
        # Get troubleshooting database
        troubleshooting_data = service.troubleshooting_database.get(system, {})
        
        # Get expert contacts
        expert_contacts = service.expert_contacts.get(system, [])
        
        # Get educational resources
        educational_resources = service.educational_resources.get(system, [])
        
        return {
            "tillage_system": tillage_system,
            "common_issues": troubleshooting_data,
            "expert_contacts": expert_contacts,
            "educational_resources": educational_resources,
            "prevention_strategies": [
                "Regular monitoring and assessment",
                "Proactive maintenance",
                "Proper equipment calibration",
                "Integrated management approach"
            ],
            "emergency_contacts": [
                {"name": "Extension Specialist", "phone": "1-800-EXTENSION"},
                {"name": "Equipment Dealer", "phone": "Local dealer contact"},
                {"name": "Emergency Services", "phone": "911"}
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting troubleshooting guide: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Troubleshooting guide failed: {str(e)}")


@router.get("/tillage-transition-planning/educational-resources")
async def get_educational_resources(
    tillage_system: str = Query(..., description="Tillage system for educational resources")
):
    """
    Get educational resources for tillage system transition.
    
    Provides comprehensive educational support including:
    - Learning modules and courses
    - Training schedules and opportunities
    - Certification programs
    - Online resources and materials
    - Workshop recommendations
    - Peer learning opportunities
    
    Agricultural Use Cases:
    - Farmer education and training
    - Skill development and certification
    - Knowledge transfer and best practices
    - Continuous learning and improvement
    """
    try:
        from ..models.tillage_models import TillageSystem
        from ..services.tillage_transition_planning_service import TillageTransitionPlanningService
        
        # Validate tillage system
        try:
            system = TillageSystem(tillage_system)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid tillage system")
        
        # Create service and get educational resources
        service = TillageTransitionPlanningService()
        
        educational_resources = service.educational_resources.get(system, [])
        expert_contacts = service.expert_contacts.get(system, [])
        peer_contacts = service.peer_network_contacts.get(system, [])
        
        return {
            "tillage_system": tillage_system,
            "learning_modules": educational_resources,
            "training_opportunities": [
                "Extension workshops",
                "Equipment dealer training",
                "Online courses",
                "Field days and demonstrations"
            ],
            "certification_programs": [
                "Conservation Agriculture Certification",
                "Soil Health Specialist",
                "Precision Agriculture Certification"
            ],
            "online_resources": [
                "Extension websites",
                "Research publications",
                "Video tutorials",
                "Interactive tools"
            ],
            "workshop_recommendations": [
                f"{system.value.title()} System Workshop",
                "Cover Crop Management",
                "Soil Health Assessment",
                "Equipment Operation and Maintenance"
            ],
            "peer_learning_opportunities": [
                "Study groups",
                "Mentorship programs",
                "Peer-to-peer exchanges",
                "Farmer networks"
            ],
            "expert_contacts": expert_contacts,
            "peer_contacts": peer_contacts
        }
        
    except Exception as e:
        logger.error(f"Error getting educational resources: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Educational resources failed: {str(e)}")


@router.get("/tillage-transition-planning/support-network")
async def get_support_network(
    tillage_system: str = Query(..., description="Tillage system for support network"),
    location: str = Query(None, description="Geographic location for local contacts")
):
    """
    Get comprehensive support network for tillage transition.
    
    Provides access to support network including:
    - Extension service contacts
    - Expert consultants and specialists
    - Peer farmers and mentors
    - Equipment dealers and suppliers
    - Educational institutions
    - Government programs and services
    
    Agricultural Use Cases:
    - Building support network for transition
    - Accessing local expertise and resources
    - Connecting with peer farmers
    - Coordinating with service providers
    """
    try:
        from ..models.tillage_models import TillageSystem
        from ..services.tillage_transition_planning_service import TillageTransitionPlanningService
        
        # Validate tillage system
        try:
            system = TillageSystem(tillage_system)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid tillage system")
        
        # Create service and get support network
        service = TillageTransitionPlanningService()
        
        expert_contacts = service.expert_contacts.get(system, [])
        peer_contacts = service.peer_network_contacts.get(system, [])
        
        return {
            "tillage_system": tillage_system,
            "location": location,
            "extension_services": [
                {"name": "Local Extension Office", "services": ["Technical assistance", "Soil testing", "Educational programs"]},
                {"name": "State Extension Specialist", "services": ["Expert consultation", "Research updates", "Training programs"]}
            ],
            "expert_consultants": expert_contacts,
            "peer_farmers": peer_contacts,
            "equipment_dealers": [
                {"name": "Local Equipment Dealer", "specialty": system.value, "services": ["Sales", "Service", "Training"]}
            ],
            "educational_institutions": [
                {"name": "Land Grant University", "services": ["Research", "Extension", "Education"]},
                {"name": "Community College", "services": ["Technical training", "Certification programs"]}
            ],
            "government_programs": [
                {"name": "NRCS", "services": ["Technical assistance", "Cost share programs"]},
                {"name": "FSA", "services": ["Program enrollment", "Financial assistance"]}
            ],
            "professional_organizations": [
                {"name": "Conservation Tillage Association", "services": ["Networking", "Education", "Advocacy"]},
                {"name": "Soil Health Partnership", "services": ["Research", "Demonstration", "Education"]}
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting support network: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Support network failed: {str(e)}")


@router.get("/tillage-transition-planning/monitoring-framework")
async def get_monitoring_framework(
    tillage_system: str = Query(..., description="Tillage system for monitoring framework")
):
    """
    Get success monitoring framework for tillage transition.
    
    Provides comprehensive monitoring framework including:
    - Key performance indicators (KPIs)
    - Monitoring schedule and frequency
    - Data collection methods
    - Benchmarking criteria
    - Reporting templates
    - Success thresholds
    
    Agricultural Use Cases:
    - Performance tracking and evaluation
    - Success measurement and validation
    - Continuous improvement planning
    - Documentation and reporting
    """
    try:
        from ..models.tillage_models import TillageSystem
        from ..services.tillage_transition_planning_service import TillageTransitionPlanningService
        
        # Validate tillage system
        try:
            system = TillageSystem(tillage_system)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid tillage system")
        
        # Create service and get monitoring framework
        service = TillageTransitionPlanningService()
        
        return {
            "tillage_system": tillage_system,
            "key_performance_indicators": [
                "Soil moisture retention percentage",
                "Soil organic matter content",
                "Erosion reduction percentage",
                "Fuel consumption per acre",
                "Labor efficiency improvement",
                "Crop yield maintenance/improvement",
                "Weed control effectiveness",
                "Soil compaction reduction"
            ],
            "monitoring_schedule": {
                "soil_health": "Annual",
                "soil_moisture": "Monthly during growing season",
                "crop_performance": "Seasonal",
                "equipment_efficiency": "Per operation",
                "economic_metrics": "Annual"
            },
            "data_collection_methods": [
                "Soil testing and analysis",
                "Visual assessment and scoring",
                "Yield monitoring and measurement",
                "Fuel consumption tracking",
                "Labor hour documentation",
                "Equipment performance monitoring"
            ],
            "benchmarking_criteria": {
                "regional_averages": "County/state level comparisons",
                "historical_performance": "Farm-specific baseline",
                "industry_standards": "Best practice benchmarks"
            },
            "reporting_templates": [
                "Monthly progress report",
                "Seasonal assessment",
                "Annual summary report",
                "Transition milestone report"
            ],
            "success_thresholds": {
                "soil_health_improvement": ">10% increase in organic matter",
                "water_conservation": ">20% reduction in irrigation needs",
                "fuel_savings": ">30% reduction in fuel consumption",
                "yield_maintenance": ">95% of baseline yield",
                "erosion_reduction": ">50% reduction in soil loss"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting monitoring framework: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Monitoring framework failed: {str(e)}")


@router.get("/tillage-transition-planning/health")
async def tillage_transition_planning_health():
    """Health check endpoint for tillage transition planning service."""
    try:
        return {
            "status": "healthy",
            "service": "tillage-transition-planning",
            "timestamp": datetime.utcnow(),
            "features": [
                "comprehensive_transition_planning",
                "feasibility_assessment",
                "troubleshooting_support",
                "educational_resources",
                "support_network",
                "monitoring_framework"
            ],
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        raise HTTPException(status_code=500, detail="Service health check failed")

# Include optimization routes
router.include_router(optimization_router)

# Include diversification routes
router.include_router(diversification_router)


# Cover Management Endpoints
@router.post("/cover-management/recommendations", response_model=CoverManagementResponse)
async def get_cover_management_recommendations(
    request: CoverManagementRequest,
    service: CoverManagementService = Depends(get_cover_management_service)
):
    """
    Get comprehensive cover management recommendations for a field.
    
    This endpoint provides cover crop and mulching recommendations based on:
    - Field characteristics and soil type
    - Climate zone and weather patterns
    - Management goals and budget constraints
    - Available equipment and resources
    
    Agricultural Benefits:
    - Improved soil health and organic matter
    - Enhanced moisture conservation and drought resilience
    - Weed suppression and pest management
    - Erosion control and nutrient cycling
    """
    try:
        logger.info(f"Getting cover management recommendations for field: {request.field_id}")
        
        response = await service.get_cover_management_recommendations(request)
        
        logger.info(f"Generated cover management recommendations for field: {request.field_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error getting cover management recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cover management recommendations failed: {str(e)}")


@router.post("/cover-management/biomass-calculation")
async def calculate_biomass_production(
    field_id: UUID = Body(..., description="Field identifier"),
    cover_crop_species: str = Body(..., description="Cover crop species name"),
    field_conditions: Dict[str, Any] = Body(..., description="Field conditions and characteristics"),
    service: CoverManagementService = Depends(get_cover_management_service)
):
    """
    Calculate expected biomass production for cover crop species.
    
    This endpoint calculates biomass production based on:
    - Cover crop species characteristics
    - Field soil quality and conditions
    - Moisture availability and temperature suitability
    - Expected nitrogen contribution and organic matter addition
    """
    try:
        logger.info(f"Calculating biomass production for {cover_crop_species} in field: {field_id}")
        
        # Find the cover crop species
        cover_crop = None
        for species in service.cover_crop_database:
            if species.common_name.lower() == cover_crop_species.lower():
                cover_crop = species
                break
        
        if not cover_crop:
            raise HTTPException(status_code=404, detail=f"Cover crop species '{cover_crop_species}' not found")
        
        biomass_analysis = await service.calculate_biomass_production(cover_crop, field_conditions)
        
        logger.info(f"Biomass calculation completed for {cover_crop_species}")
        return biomass_analysis
        
    except Exception as e:
        logger.error(f"Error calculating biomass production: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Biomass calculation failed: {str(e)}")


@router.post("/cover-management/moisture-conservation-assessment")
async def assess_moisture_conservation(
    mulch_materials: List[str] = Body(..., description="List of mulch material names"),
    field_conditions: Dict[str, Any] = Body(..., description="Field conditions and characteristics"),
    service: CoverManagementService = Depends(get_cover_management_service)
):
    """
    Assess moisture conservation benefits of mulching strategies.
    
    This endpoint evaluates:
    - Moisture retention capabilities of mulch materials
    - Weed suppression effectiveness
    - Cost-benefit analysis and ROI estimates
    - Water savings potential and irrigation reduction
    """
    try:
        logger.info("Assessing moisture conservation benefits")
        
        # Find the mulch materials
        materials = []
        for material_name in mulch_materials:
            material = None
            for mulch in service.mulch_database:
                if mulch.material_name.lower() == material_name.lower():
                    material = mulch
                    break
            
            if not material:
                raise HTTPException(status_code=404, detail=f"Mulch material '{material_name}' not found")
            
            materials.append(material)
        
        conservation_analysis = await service.assess_moisture_conservation(materials, field_conditions)
        
        logger.info("Moisture conservation assessment completed")
        return conservation_analysis
        
    except Exception as e:
        logger.error(f"Error assessing moisture conservation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Moisture conservation assessment failed: {str(e)}")


@router.get("/cover-management/species")
async def get_cover_crop_species(
    crop_type: Optional[str] = Query(None, description="Filter by cover crop type"),
    nitrogen_fixation: Optional[bool] = Query(None, description="Filter by nitrogen fixation capability"),
    service: CoverManagementService = Depends(get_cover_management_service)
):
    """
    Get available cover crop species with filtering options.
    
    Returns comprehensive information about cover crop species including:
    - Species characteristics and growth habits
    - Seeding rates and management requirements
    - Benefits and suitability for different conditions
    - Termination methods and timing recommendations
    """
    try:
        logger.info("Getting cover crop species information")
        
        species_list = []
        for species in service.cover_crop_database:
            # Apply filters
            if crop_type and species.crop_type.value != crop_type.lower():
                continue
            if nitrogen_fixation is not None and species.nitrogen_fixation != nitrogen_fixation:
                continue
            
            species_info = {
                "species_id": species.species_id,
                "common_name": species.common_name,
                "scientific_name": species.scientific_name,
                "crop_type": species.crop_type.value,
                "nitrogen_fixation": species.nitrogen_fixation,
                "biomass_production_lbs_per_acre": species.biomass_production_lbs_per_acre,
                "root_depth_inches": species.root_depth_inches,
                "cold_tolerance_f": species.cold_tolerance_f,
                "drought_tolerance": species.drought_tolerance,
                "seeding_rate_lbs_per_acre": species.seeding_rate_lbs_per_acre,
                "termination_methods": species.termination_methods,
                "benefits": species.benefits
            }
            species_list.append(species_info)
        
        logger.info(f"Returned {len(species_list)} cover crop species")
        return {
            "species": species_list,
            "total_count": len(species_list),
            "filters_applied": {
                "crop_type": crop_type,
                "nitrogen_fixation": nitrogen_fixation
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting cover crop species: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cover crop species retrieval failed: {str(e)}")


@router.get("/cover-management/mulch-materials")
async def get_mulch_materials(
    mulch_type: Optional[str] = Query(None, description="Filter by mulch type"),
    max_cost_per_cubic_yard: Optional[float] = Query(None, description="Maximum cost filter"),
    service: CoverManagementService = Depends(get_cover_management_service)
):
    """
    Get available mulch materials with filtering options.
    
    Returns comprehensive information about mulch materials including:
    - Material characteristics and properties
    - Cost and application requirements
    - Moisture retention and weed suppression capabilities
    - Soil health benefits and decomposition rates
    """
    try:
        logger.info("Getting mulch materials information")
        
        materials_list = []
        for material in service.mulch_database:
            # Apply filters
            if mulch_type and material.mulch_type.value != mulch_type.lower():
                continue
            if max_cost_per_cubic_yard and float(material.cost_per_cubic_yard) > max_cost_per_cubic_yard:
                continue
            
            material_info = {
                "material_id": material.material_id,
                "material_name": material.material_name,
                "mulch_type": material.mulch_type.value,
                "cost_per_cubic_yard": float(material.cost_per_cubic_yard),
                "application_rate_inches": material.application_rate_inches,
                "moisture_retention_percent": material.moisture_retention_percent,
                "weed_suppression_percent": material.weed_suppression_percent,
                "decomposition_rate_months": material.decomposition_rate_months,
                "soil_health_benefits": material.soil_health_benefits
            }
            materials_list.append(material_info)
        
        logger.info(f"Returned {len(materials_list)} mulch materials")
        return {
            "materials": materials_list,
            "total_count": len(materials_list),
            "filters_applied": {
                "mulch_type": mulch_type,
                "max_cost_per_cubic_yard": max_cost_per_cubic_yard
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting mulch materials: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Mulch materials retrieval failed: {str(e)}")


@router.get("/cover-management/health")
async def cover_management_health():
    """Health check endpoint for cover management service."""
    try:
        return {
            "status": "healthy",
            "service": "cover-management",
            "timestamp": datetime.utcnow(),
            "features": [
                "cover_crop_recommendations",
                "mulching_strategies",
                "biomass_calculations",
                "moisture_conservation_assessment",
                "species_database",
                "materials_database",
                "implementation_planning",
                "cost_analysis"
            ],
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        raise HTTPException(status_code=500, detail="Service health check failed")

# Include optimization routes
router.include_router(optimization_router)

# Include diversification routes
router.include_router(diversification_router)
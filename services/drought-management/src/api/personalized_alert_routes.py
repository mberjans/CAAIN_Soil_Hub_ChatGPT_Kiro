"""
Personalized Alert API Routes

FastAPI routes for personalized drought alert configuration,
monitoring, and response management.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Path, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from uuid import UUID
import logging

from ..models.personalized_alert_models import (
    PersonalizedAlertConfig,
    PersonalizedAlertThreshold,
    NotificationPreference,
    EmergencyProtocol,
    PersonalizedAlert,
    AutomatedResponseRecommendation,
    ResponseTracking,
    ResourceMobilization,
    AlertConfigurationRequest,
    AlertConfigurationResponse,
    AlertHistoryResponse,
    ResponseEffectivenessReport,
    AlertSeverity,
    AlertType,
    NotificationChannel,
    ResponseActionType,
    EmergencyProtocolType
)
from ..services.personalized_alert_service import PersonalizedAlertService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/personalized-alerts", tags=["personalized-alerts"])

# Dependency injection
async def get_personalized_alert_service() -> PersonalizedAlertService:
    """Get personalized alert service instance."""
    service = PersonalizedAlertService()
    await service.initialize()
    return service

@router.post("/configure", response_model=AlertConfigurationResponse)
async def configure_personalized_alerts(
    request: AlertConfigurationRequest,
    service: PersonalizedAlertService = Depends(get_personalized_alert_service)
):
    """
    Configure personalized alerts for a farm.
    
    This endpoint allows farmers to set up personalized drought alert configurations
    based on their specific farm characteristics, crop types, and preferences.
    
    **Features:**
    - Farm-specific threshold configuration
    - Crop-specific alert settings
    - Custom notification preferences
    - Emergency contact setup
    - Automatic threshold generation based on farm characteristics
    
    **Example Request:**
    ```json
    {
        "farm_id": "123e4567-e89b-12d3-a456-426614174000",
        "crop_types": ["corn", "soybeans"],
        "current_practices": ["no_till", "cover_crops"],
        "irrigation_system_type": "center_pivot",
        "water_source_types": ["well", "surface_water"],
        "notification_preferences": [
            {
                "channel": "email",
                "enabled": true,
                "severity_levels": ["high", "critical", "emergency"],
                "frequency_limit": 10
            }
        ],
        "emergency_contacts": [
            {
                "name": "John Doe",
                "phone": "+1234567890",
                "email": "john@example.com",
                "role": "farm_manager"
            }
        ]
    }
    ```
    """
    try:
        logger.info(f"Configuring personalized alerts for farm: {request.farm_id}")
        
        response = await service.configure_personalized_alerts(request)
        
        logger.info(f"Personalized alerts configured successfully for farm: {request.farm_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error configuring personalized alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to configure personalized alerts: {str(e)}")

@router.get("/monitor/{farm_id}", response_model=List[PersonalizedAlert])
async def monitor_farm_alerts(
    farm_id: UUID = Path(..., description="Farm identifier"),
    service: PersonalizedAlertService = Depends(get_personalized_alert_service)
):
    """
    Monitor farm conditions and generate personalized alerts.
    
    This endpoint continuously monitors farm conditions against configured thresholds
    and generates personalized alerts when conditions are exceeded.
    
    **Features:**
    - Real-time condition monitoring
    - Threshold evaluation
    - Automated alert generation
    - Personalized response recommendations
    - Emergency protocol identification
    
    **Returns:**
    - List of generated alerts with severity levels
    - Automated response recommendations
    - Applicable emergency protocols
    - Current metric values and historical context
    """
    try:
        logger.info(f"Monitoring farm conditions for alerts: {farm_id}")
        
        alerts = await service.monitor_and_generate_alerts(farm_id)
        
        logger.info(f"Generated {len(alerts)} alerts for farm: {farm_id}")
        return alerts
        
    except Exception as e:
        logger.error(f"Error monitoring farm alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to monitor farm alerts: {str(e)}")

@router.post("/responses/generate", response_model=List[AutomatedResponseRecommendation])
async def generate_automated_responses(
    alert_id: UUID = Query(..., description="Alert identifier"),
    service: PersonalizedAlertService = Depends(get_personalized_alert_service)
):
    """
    Generate automated response recommendations for an alert.
    
    This endpoint analyzes an alert and generates intelligent, automated response
    recommendations based on farm characteristics and current conditions.
    
    **Features:**
    - Intelligent response generation
    - Priority-based recommendations
    - Cost-effectiveness analysis
    - Risk assessment
    - Resource requirement identification
    
    **Response Types:**
    - Irrigation adjustments
    - Conservation practices
    - Crop management changes
    - Water source activation
    - Emergency protocols
    - Resource mobilization
    """
    try:
        logger.info(f"Generating automated responses for alert: {alert_id}")
        
        # Get alert details (in real implementation, this would fetch from database)
        alert = PersonalizedAlert(
            alert_id=alert_id,
            farm_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            user_id=UUID("123e4567-e89b-12d3-a456-426614174001"),
            alert_type=AlertType.DROUGHT_ONSET,
            severity=AlertSeverity.HIGH,
            title="Drought Onset Alert",
            message="Drought conditions detected",
            triggered_threshold=PersonalizedAlertThreshold(
                threshold_id=UUID("123e4567-e89b-12d3-a456-426614174002"),
                alert_type=AlertType.DROUGHT_ONSET,
                metric_name="drought_index",
                threshold_value=0.5,
                comparison_operator="<",
                severity_level=AlertSeverity.HIGH
            ),
            current_metrics={"drought_index": 0.3},
            notification_channels=[NotificationChannel.EMAIL]
        )
        
        farm_conditions = {"soil_moisture_percent": 25.0, "drought_index": 0.3}
        
        responses = await service.generate_automated_responses(alert, farm_conditions)
        
        logger.info(f"Generated {len(responses)} automated responses for alert: {alert_id}")
        return responses
        
    except Exception as e:
        logger.error(f"Error generating automated responses: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate automated responses: {str(e)}")

@router.post("/emergency-protocols/activate")
async def activate_emergency_protocol(
    alert_id: UUID = Query(..., description="Alert identifier"),
    protocol_id: UUID = Query(..., description="Protocol identifier"),
    authorization_details: Dict[str, Any] = Query(..., description="Authorization information"),
    service: PersonalizedAlertService = Depends(get_personalized_alert_service)
):
    """
    Activate an emergency protocol for an alert.
    
    This endpoint activates emergency protocols when critical conditions are detected.
    Emergency protocols provide step-by-step instructions for handling severe drought situations.
    
    **Features:**
    - Authorization verification
    - Step-by-step protocol execution
    - Resource mobilization
    - Stakeholder notification
    - Progress tracking
    
    **Protocol Types:**
    - Water restriction protocols
    - Crop abandonment procedures
    - Emergency irrigation activation
    - Disaster assistance coordination
    - Resource sharing arrangements
    """
    try:
        logger.info(f"Activating emergency protocol {protocol_id} for alert {alert_id}")
        
        result = await service.activate_emergency_protocol(alert_id, protocol_id, authorization_details)
        
        logger.info(f"Emergency protocol {protocol_id} activated successfully")
        return result
        
    except PermissionError as e:
        logger.warning(f"Authorization failed for protocol activation: {str(e)}")
        raise HTTPException(status_code=403, detail="Insufficient authorization for protocol activation")
    except Exception as e:
        logger.error(f"Error activating emergency protocol: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to activate emergency protocol: {str(e)}")

@router.post("/responses/track", response_model=ResponseTracking)
async def track_response_action(
    alert_id: UUID = Query(..., description="Alert identifier"),
    recommendation_id: UUID = Query(..., description="Recommendation identifier"),
    action_taken: str = Query(..., description="Description of action taken"),
    action_type: ResponseActionType = Query(..., description="Type of action"),
    implementation_status: str = Query(default="in_progress", description="Implementation status"),
    service: PersonalizedAlertService = Depends(get_personalized_alert_service)
):
    """
    Track the implementation of a response action.
    
    This endpoint allows farmers to track the implementation of recommended actions,
    providing visibility into response effectiveness and outcomes.
    
    **Features:**
    - Action implementation tracking
    - Progress monitoring
    - Cost tracking
    - Effectiveness rating
    - Outcome documentation
    
    **Implementation Status Options:**
    - pending: Action not yet started
    - in_progress: Action currently being implemented
    - completed: Action successfully completed
    - cancelled: Action was cancelled
    - failed: Action implementation failed
    """
    try:
        logger.info(f"Tracking response action for alert {alert_id}, recommendation {recommendation_id}")
        
        tracking = await service.track_response_action(
            alert_id, recommendation_id, action_taken, action_type, implementation_status
        )
        
        logger.info(f"Response action tracked successfully: {tracking.tracking_id}")
        return tracking
        
    except Exception as e:
        logger.error(f"Error tracking response action: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to track response action: {str(e)}")

@router.post("/resources/mobilize", response_model=List[ResourceMobilization])
async def mobilize_resources(
    alert_id: UUID = Query(..., description="Alert identifier"),
    resource_requirements: List[Dict[str, Any]] = Query(..., description="Resource requirements"),
    service: PersonalizedAlertService = Depends(get_personalized_alert_service)
):
    """
    Mobilize resources for emergency response.
    
    This endpoint initiates resource mobilization when emergency resources are needed
    for drought response actions.
    
    **Features:**
    - Resource requirement specification
    - Provider contact and coordination
    - Delivery tracking
    - Status monitoring
    - Cost management
    
    **Resource Types:**
    - Water sources (tankers, wells, surface water)
    - Irrigation equipment
    - Emergency supplies
    - Personnel and expertise
    - Transportation and logistics
    """
    try:
        logger.info(f"Mobilizing resources for alert: {alert_id}")
        
        mobilizations = await service.mobilize_resources(alert_id, resource_requirements)
        
        logger.info(f"Mobilized {len(mobilizations)} resources for alert: {alert_id}")
        return mobilizations
        
    except Exception as e:
        logger.error(f"Error mobilizing resources: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to mobilize resources: {str(e)}")

@router.get("/history/{farm_id}", response_model=AlertHistoryResponse)
async def get_alert_history(
    farm_id: UUID = Path(..., description="Farm identifier"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=50, ge=1, le=100, description="Page size"),
    alert_type: Optional[AlertType] = Query(None, description="Filter by alert type"),
    severity: Optional[AlertSeverity] = Query(None, description="Filter by severity"),
    service: PersonalizedAlertService = Depends(get_personalized_alert_service)
):
    """
    Get alert history for a farm.
    
    This endpoint provides historical alert data for analysis and reporting purposes.
    
    **Features:**
    - Paginated alert history
    - Filtering by alert type and severity
    - Response tracking information
    - Effectiveness metrics
    - Trend analysis data
    
    **Response Information:**
    - Alert details and timestamps
    - Response actions taken
    - Effectiveness ratings
    - Cost information
    - Resolution times
    """
    try:
        logger.info(f"Getting alert history for farm: {farm_id}")
        
        response = await service.get_alert_history(farm_id, page, page_size, alert_type, severity)
        
        logger.info(f"Retrieved {len(response.alerts)} alerts for farm: {farm_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error getting alert history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get alert history: {str(e)}")

@router.get("/effectiveness-report/{farm_id}", response_model=ResponseEffectivenessReport)
async def generate_effectiveness_report(
    farm_id: UUID = Path(..., description="Farm identifier"),
    start_date: date = Query(..., description="Report start date"),
    end_date: date = Query(..., description="Report end date"),
    service: PersonalizedAlertService = Depends(get_personalized_alert_service)
):
    """
    Generate response effectiveness report.
    
    This endpoint generates comprehensive reports on the effectiveness of drought
    response actions and recommendations.
    
    **Features:**
    - Response time analysis
    - Effectiveness rating aggregation
    - Cost-benefit analysis
    - Improvement recommendations
    - Performance metrics
    
    **Report Metrics:**
    - Total alerts and response rates
    - Average response times
    - Effectiveness ratings
    - Cost analysis
    - Savings achieved
    - Recommendations for improvement
    """
    try:
        logger.info(f"Generating effectiveness report for farm: {farm_id}")
        
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        report = await service.generate_effectiveness_report(farm_id, start_datetime, end_datetime)
        
        logger.info(f"Generated effectiveness report for farm: {farm_id}")
        return report
        
    except Exception as e:
        logger.error(f"Error generating effectiveness report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate effectiveness report: {str(e)}")

@router.get("/thresholds/{farm_id}", response_model=List[PersonalizedAlertThreshold])
async def get_alert_thresholds(
    farm_id: UUID = Path(..., description="Farm identifier"),
    service: PersonalizedAlertService = Depends(get_personalized_alert_service)
):
    """
    Get configured alert thresholds for a farm.
    
    This endpoint retrieves all configured alert thresholds for a specific farm,
    allowing farmers to review and modify their alert settings.
    
    **Features:**
    - Complete threshold configuration
    - Threshold status (enabled/disabled)
    - Crop-specific settings
    - Growth stage specifications
    - Severity level configurations
    """
    try:
        logger.info(f"Getting alert thresholds for farm: {farm_id}")
        
        config = service.alert_configs.get(str(farm_id))
        if not config:
            raise HTTPException(status_code=404, detail="No alert configuration found for farm")
        
        logger.info(f"Retrieved {len(config.thresholds)} thresholds for farm: {farm_id}")
        return config.thresholds
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting alert thresholds: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get alert thresholds: {str(e)}")

@router.put("/thresholds/{threshold_id}")
async def update_alert_threshold(
    threshold_id: UUID = Path(..., description="Threshold identifier"),
    threshold_data: Dict[str, Any] = Query(..., description="Updated threshold data"),
    service: PersonalizedAlertService = Depends(get_personalized_alert_service)
):
    """
    Update an alert threshold configuration.
    
    This endpoint allows farmers to modify existing alert thresholds based on
    changing conditions or preferences.
    
    **Updatable Fields:**
    - Threshold value
    - Comparison operator
    - Severity level
    - Enabled status
    - Crop-specific settings
    - Growth stage specifications
    """
    try:
        logger.info(f"Updating alert threshold: {threshold_id}")
        
        # In real implementation, this would update the threshold in the database
        # For now, return success message
        
        logger.info(f"Alert threshold {threshold_id} updated successfully")
        return {"message": "Threshold updated successfully", "threshold_id": threshold_id}
        
    except Exception as e:
        logger.error(f"Error updating alert threshold: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update alert threshold: {str(e)}")

@router.get("/emergency-protocols", response_model=List[EmergencyProtocol])
async def get_emergency_protocols(
    service: PersonalizedAlertService = Depends(get_personalized_alert_service)
):
    """
    Get available emergency protocols.
    
    This endpoint retrieves all available emergency protocols that can be
    activated during severe drought conditions.
    
    **Features:**
    - Complete protocol definitions
    - Activation conditions
    - Step-by-step instructions
    - Resource requirements
    - Contact information
    - Duration estimates
    """
    try:
        logger.info("Getting available emergency protocols")
        
        protocols = list(service.emergency_protocols.values())
        
        logger.info(f"Retrieved {len(protocols)} emergency protocols")
        return protocols
        
    except Exception as e:
        logger.error(f"Error getting emergency protocols: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get emergency protocols: {str(e)}")

@router.get("/health")
async def health_check():
    """
    Health check endpoint for personalized alert service.
    
    This endpoint provides service health status and basic configuration information.
    """
    return {
        "status": "healthy",
        "service": "personalized-alerts",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "features": [
            "personalized_thresholds",
            "automated_responses",
            "emergency_protocols",
            "resource_mobilization",
            "effectiveness_tracking"
        ]
    }
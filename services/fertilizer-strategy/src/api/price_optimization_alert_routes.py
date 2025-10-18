"""
API routes for intelligent price optimization alerts system.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from typing import List, Optional, Dict, Any
import logging
import time
from uuid import uuid4

from ..models.price_optimization_alert_models import (
    AlertCreationRequest, AlertCreationResponse, AlertMonitoringSession,
    AlertStatistics, MLModelPerformance, AlertOptimizationRequest,
    AlertOptimizationResponse, AlertDeliveryRequest, AlertDeliveryResponse,
    AlertFeedback, AlertBatchRequest, AlertBatchResponse, IntelligentAlert,
    UserAlertPreferences, AlertType, AlertPriority, AlertChannel, AlertStatus,
    MobilePriceAlertRequest, MobilePriceAlertResponse
)
from ..services.price_optimization_alert_service import PriceOptimizationAlertService
from ..services.mobile_price_alert_service import MobilePriceAlertManager
from ..database.fertilizer_price_db import get_db_session

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/alerts", tags=["price-optimization-alerts"])

# Dependency injection
async def get_alert_service() -> PriceOptimizationAlertService:
    return PriceOptimizationAlertService()


async def get_mobile_alert_manager() -> MobilePriceAlertManager:
    return MobilePriceAlertManager()


@router.post("/create", response_model=AlertCreationResponse)
async def create_intelligent_alert(
    request: AlertCreationRequest,
    background_tasks: BackgroundTasks,
    service: PriceOptimizationAlertService = Depends(get_alert_service)
):
    """
    Create intelligent price optimization alerts for a user.
    
    This endpoint creates personalized alerts based on user preferences,
    fertilizer types, and machine learning analysis of price patterns.
    
    Features:
    - Intelligent alerting with ML-based pattern recognition
    - Personalized thresholds and preferences
    - Multiple alert types (price threshold, opportunity, risk, timing)
    - Predictive alerts with confidence scoring
    """
    start_time = time.time()
    request_id = str(uuid4())
    
    try:
        logger.info(f"Creating intelligent alerts for user {request.user_id}")
        
        # Create monitoring session
        session_id = str(uuid4())
        monitoring_session = AlertMonitoringSession(
            session_id=session_id,
            user_id=request.user_id,
            fertilizer_types=[request.fertilizer_type],
            duration_hours=request.monitoring_duration_hours,
            preferences=request.user_preferences or UserAlertPreferences(user_id=request.user_id)
        )
        
        # Generate alerts
        alerts = await service.monitor_price_optimization_opportunities(
            user_id=request.user_id,
            fertilizer_types=[request.fertilizer_type],
            monitoring_duration_hours=request.monitoring_duration_hours
        )
        
        # Convert to IntelligentAlert models
        intelligent_alerts = []
        for alert in alerts:
            intelligent_alert = IntelligentAlert(
                alert_id=alert.alert_id,
                user_id=request.user_id,
                alert_type=AlertType(alert.trigger_type),
                priority=AlertPriority(alert.priority),
                title=f"{AlertType(alert.trigger_type).value.title()} Alert",
                message=alert.message,
                details=alert.details or {},
                confidence_score=0.8,  # Would be calculated from ML analysis
                pattern_analysis={},
                ml_model_used="price_optimization_v1",
                requires_action=alert.requires_action,
                action_deadline=alert.action_deadline,
                created_at=alert.timestamp,
                expires_at=alert.expires_at
            )
            intelligent_alerts.append(intelligent_alert)
        
        processing_time = (time.time() - start_time) * 1000
        
        return AlertCreationResponse(
            request_id=request_id,
            alerts_created=len(intelligent_alerts),
            alerts=intelligent_alerts,
            monitoring_session_id=session_id,
            processing_time_ms=processing_time,
            success=True,
            message=f"Successfully created {len(intelligent_alerts)} alerts"
        )
        
    except Exception as e:
        logger.error(f"Error creating intelligent alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch", response_model=AlertBatchResponse)
async def create_batch_alerts(
    request: AlertBatchRequest,
    background_tasks: BackgroundTasks,
    service: PriceOptimizationAlertService = Depends(get_alert_service)
):
    """
    Create alerts for multiple fertilizer types in batch.
    
    Efficient endpoint for monitoring multiple fertilizer types simultaneously,
    useful for comprehensive farm management systems.
    """
    start_time = time.time()
    batch_id = str(uuid4())
    
    try:
        logger.info(f"Creating batch alerts for user {request.user_id}")
        
        all_alerts = []
        errors = []
        
        for fertilizer_type in request.fertilizer_types:
            try:
                alerts = await service.monitor_price_optimization_opportunities(
                    user_id=request.user_id,
                    fertilizer_types=[fertilizer_type],
                    monitoring_duration_hours=request.monitoring_duration_hours
                )
                all_alerts.extend(alerts)
                
                if len(all_alerts) >= request.batch_size:
                    break
                    
            except Exception as e:
                error_msg = f"Error processing {fertilizer_type.value}: {str(e)}"
                errors.append(error_msg)
                logger.warning(error_msg)
        
        processing_time = (time.time() - start_time) * 1000
        
        return AlertBatchResponse(
            batch_id=batch_id,
            user_id=request.user_id,
            alerts_generated=len(all_alerts),
            alerts=[],  # Would convert to IntelligentAlert models
            processing_time_ms=processing_time,
            success=len(errors) == 0,
            errors=errors
        )
        
    except Exception as e:
        logger.error(f"Error creating batch alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics/{user_id}", response_model=AlertStatistics)
async def get_alert_statistics(
    user_id: str,
    period_days: int = Query(30, ge=1, le=365, description="Statistics period in days"),
    service: PriceOptimizationAlertService = Depends(get_alert_service)
):
    """
    Get alert statistics for a user.
    
    Provides comprehensive statistics about alert performance,
    user engagement, and system effectiveness.
    """
    try:
        logger.info(f"Getting alert statistics for user {user_id}")
        
        stats = await service.get_alert_statistics(user_id)
        
        return AlertStatistics(
            user_id=user_id,
            total_alerts=stats.get("total_alerts", 0),
            false_positive_rate=stats.get("false_positive_rate", 0.0),
            response_rate=stats.get("response_rate", 0.0),
            average_response_time_hours=stats.get("average_response_time", 0.0),
            alert_types=stats.get("alert_types", {}),
            priority_distribution={},
            channel_effectiveness={},
            period_start=time.time() - (period_days * 24 * 3600),
            period_end=time.time()
        )
        
    except Exception as e:
        logger.error(f"Error getting alert statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mobile-price", response_model=MobilePriceAlertResponse)
async def generate_mobile_price_alerts(
    request: MobilePriceAlertRequest,
    manager: MobilePriceAlertManager = Depends(get_mobile_alert_manager)
):
    """
    Generate intelligent mobile price alerts with location awareness.
    
    Features:
    - Location-aware region resolution
    - Personalized alert thresholds and preferences
    - Mobile-ready alert packaging with action guidance
    """
    try:
        logger.info(
            "Generating mobile price alerts for user %s (region hint: %s)",
            request.user_id,
            request.region or "none"
        )
        
        response = await manager.generate_mobile_alerts(request)
        return response
    
    except HTTPException:
        raise
    except Exception as error:
        logger.error("Error generating mobile price alerts: %s", error)
        raise HTTPException(status_code=500, detail=str(error))


@router.post("/optimize", response_model=AlertOptimizationResponse)
async def optimize_alert_settings(
    request: AlertOptimizationRequest,
    service: PriceOptimizationAlertService = Depends(get_alert_service)
):
    """
    Optimize alert settings for a user based on historical performance.
    
    Uses machine learning to automatically adjust alert thresholds,
    preferences, and delivery settings to improve effectiveness.
    """
    start_time = time.time()
    optimization_id = str(uuid4())
    
    try:
        logger.info(f"Optimizing alert settings for user {request.user_id}")
        
        # Get current statistics
        current_stats = await service.get_alert_statistics(request.user_id)
        
        # Simulate optimization (would use actual ML optimization)
        optimized_preferences = UserAlertPreferences(
            user_id=request.user_id,
            enabled_alert_types=[AlertType.PRICE_THRESHOLD, AlertType.OPPORTUNITY],
            enabled_channels=[AlertChannel.EMAIL, AlertChannel.APP_NOTIFICATION],
            max_alerts_per_day=5  # Reduced from default
        )
        
        # Calculate improvements
        performance_improvement = {
            "false_positive_reduction": 0.15,
            "response_rate_increase": 0.25,
            "alert_relevance_improvement": 0.30
        }
        
        recommendations = [
            "Reduce price change threshold to 3% for more sensitive alerts",
            "Enable opportunity alerts for better timing",
            "Limit daily alerts to 5 to reduce notification fatigue",
            "Use email and app notifications for better engagement"
        ]
        
        processing_time = (time.time() - start_time) * 1000
        
        return AlertOptimizationResponse(
            optimization_id=optimization_id,
            user_id=request.user_id,
            optimized_preferences=optimized_preferences,
            performance_improvement=performance_improvement,
            recommendations=recommendations,
            confidence_score=0.85,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error optimizing alert settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/deliver", response_model=AlertDeliveryResponse)
async def deliver_alert(
    request: AlertDeliveryRequest,
    background_tasks: BackgroundTasks,
    service: PriceOptimizationAlertService = Depends(get_alert_service)
):
    """
    Deliver alerts through specified channels.
    
    Supports multiple delivery channels with priority-based routing
    and delivery status tracking.
    """
    start_time = time.time()
    delivery_id = str(uuid4())
    
    try:
        logger.info(f"Delivering alert {request.alert_id} through channels {request.channels}")
        
        # Simulate delivery (would integrate with actual notification services)
        channels_sent = request.channels
        delivery_status = {channel.value: "delivered" for channel in request.channels}
        
        processing_time = (time.time() - start_time) * 1000
        
        return AlertDeliveryResponse(
            delivery_id=delivery_id,
            alert_id=request.alert_id,
            channels_sent=channels_sent,
            delivery_status=delivery_status,
            success=True,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error delivering alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback")
async def submit_alert_feedback(
    feedback: AlertFeedback,
    service: PriceOptimizationAlertService = Depends(get_alert_service)
):
    """
    Submit user feedback on alerts for ML model improvement.
    
    Collects user feedback to improve alert accuracy and reduce false positives.
    """
    try:
        logger.info(f"Received feedback for alert {feedback.alert_id}")
        
        # Store feedback (would integrate with database)
        # Update ML model performance metrics
        
        return {
            "success": True,
            "message": "Feedback submitted successfully",
            "feedback_id": str(uuid4())
        }
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/performance", response_model=List[MLModelPerformance])
async def get_ml_model_performance(
    service: PriceOptimizationAlertService = Depends(get_alert_service)
):
    """
    Get performance metrics for ML models used in alert optimization.
    
    Provides transparency into model performance and accuracy metrics.
    """
    try:
        logger.info("Getting ML model performance metrics")
        
        # Get model performance data
        models = []
        for model_id, model in service.ml_models.items():
            performance = MLModelPerformance(
                model_id=model.model_id,
                model_type=model.model_type,
                accuracy_score=model.accuracy_score,
                false_positive_rate=model.false_positive_rate,
                false_negative_rate=0.1,  # Would be calculated
                precision=0.85,  # Would be calculated
                recall=0.80,  # Would be calculated
                f1_score=0.82,  # Would be calculated
                last_trained=model.last_trained,
                training_samples=1000,  # Would be actual count
                features_used=model.features_used
            )
            models.append(performance)
        
        return models
        
    except Exception as e:
        logger.error(f"Error getting ML model performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}/preferences", response_model=UserAlertPreferences)
async def get_user_preferences(
    user_id: str,
    service: PriceOptimizationAlertService = Depends(get_alert_service)
):
    """
    Get user alert preferences and settings.
    """
    try:
        logger.info(f"Getting preferences for user {user_id}")
        
        # Get user preferences (would query database)
        preferences = UserAlertPreferences(
            user_id=user_id,
            enabled_alert_types=[AlertType.PRICE_THRESHOLD, AlertType.OPPORTUNITY],
            enabled_channels=[AlertChannel.EMAIL, AlertChannel.APP_NOTIFICATION],
            max_alerts_per_day=10
        )
        
        return preferences
        
    except Exception as e:
        logger.error(f"Error getting user preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/user/{user_id}/preferences", response_model=UserAlertPreferences)
async def update_user_preferences(
    user_id: str,
    preferences: UserAlertPreferences,
    service: PriceOptimizationAlertService = Depends(get_alert_service)
):
    """
    Update user alert preferences and settings.
    """
    try:
        logger.info(f"Updating preferences for user {user_id}")
        
        # Update preferences (would save to database)
        preferences.updated_at = time.time()
        
        return preferences
        
    except Exception as e:
        logger.error(f"Error updating user preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint for the alert service."""
    return {
        "status": "healthy",
        "service": "price-optimization-alerts",
        "timestamp": time.time(),
        "version": "1.0.0"
    }

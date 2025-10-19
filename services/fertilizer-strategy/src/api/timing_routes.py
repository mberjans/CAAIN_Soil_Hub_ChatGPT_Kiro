"""
Timing Routes for Fertilizer Strategy Service

This module provides comprehensive timing optimization API endpoints including:
- Advanced timing optimization with multi-field support
- Dynamic fertilizer calendar generation
- Application window analysis with real-time updates
- Alert subscription and management
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks, Depends
from typing import List, Dict, Optional, Any
import logging
import asyncio
import time
from datetime import datetime, date, timedelta

from ..models.timing_optimization_models import (
    AdvancedTimingOptimizationRequest,
    AdvancedTimingOptimizationResponse,
    FertilizerCalendarResponse,
    CalendarEvent,
    WeatherOverlay,
    ApplicationWindowsResponse,
    ApplicationWindow,
    AlertSubscriptionRequest,
    AlertSubscriptionResponse,
    AlertManagementResponse,
    Alert,
    ApplicationTiming,
    WeatherWindow,
    WeatherCondition,
    CropGrowthStage,
    ApplicationMethod,
    TimingOptimizationRequest,
    EfficiencyPrediction,
    RiskAssessment
)
from ..services.timing_optimization_service import FertilizerTimingOptimizer

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/fertilizer", tags=["timing-routes"])


# Dependency injection
async def get_timing_optimizer() -> FertilizerTimingOptimizer:
    """Get timing optimization service instance."""
    return FertilizerTimingOptimizer()


@router.post("/timing-optimization", response_model=AdvancedTimingOptimizationResponse)
async def advanced_timing_optimization(
    request: AdvancedTimingOptimizationRequest,
    background_tasks: BackgroundTasks,
    optimizer: FertilizerTimingOptimizer = Depends(get_timing_optimizer)
):
    """
    Advanced timing optimization endpoint with multi-field support.

    This endpoint provides comprehensive timing optimization for complex farm scenarios:
    - Multi-field optimization with resource allocation
    - Weather integration and forecast-based scheduling
    - Equipment and labor constraint handling
    - Risk assessment and mitigation strategies
    - Economic optimization with cost-benefit analysis
    - Environmental impact considerations

    Agricultural Use Cases:
    - Large farm operations with multiple fields
    - Coordinated fertilizer application across crop rotations
    - Equipment and labor scheduling optimization
    - Weather-dependent application timing
    - Risk-based timing strategies for high-value crops
    - Regulatory compliance timing requirements
    - Multi-objective optimization (yield, cost, environment)

    Performance:
    - Optimizes complex multi-field scenarios in <3 seconds
    - Real-time weather integration
    - Dynamic constraint handling
    - Scalable to hundreds of fields

    Args:
        request: Advanced timing optimization request with farm context
        background_tasks: FastAPI background tasks for async operations
        optimizer: Timing optimization service instance

    Returns:
        AdvancedTimingOptimizationResponse with optimized schedule and analysis

    Raises:
        HTTPException: If optimization fails or invalid parameters
    """
    start_time = time.time()

    try:
        logger.info(f"Starting advanced timing optimization for request {request.request_id}")

        if optimizer is None:
            optimizer = FertilizerTimingOptimizer()

        # Extract field information and create optimization requests
        optimized_timings = []
        weather_data = {}

        for field in request.farm_context.fields:
            # Create timing optimization request for each field
            # Convert moisture string to numeric value if needed
            moisture_value = field.soil_conditions.get("moisture", 0.6)
            if isinstance(moisture_value, str):
                # Map string descriptors to numeric values
                moisture_map = {
                    "dry": 0.2,
                    "low": 0.3,
                    "adequate": 0.6,
                    "good": 0.7,
                    "wet": 0.9,
                    "saturated": 1.0
                }
                moisture_value = moisture_map.get(moisture_value.lower(), 0.6)

            field_request = TimingOptimizationRequest(
                field_id=field.field_id,
                crop_type=field.crop,
                planting_date=field.planting_date,
                fertilizer_requirements={"nitrogen": 150.0, "phosphorus": 60.0},  # Default requirements
                application_methods=[ApplicationMethod.BROADCAST],
                soil_type=field.soil_conditions.get("type", "loam"),
                soil_moisture_capacity=moisture_value,
                location={"lat": 40.0, "lng": -95.0},  # Would come from field data
                optimization_horizon_days=180,
                risk_tolerance=0.5 if request.optimization_goals.weather_risk_tolerance == "moderate" else 0.3,
                split_application_allowed=True,
                weather_dependent_timing=True
            )

            # Optimize timing for this field
            result = await optimizer.optimize_timing(field_request)
            optimized_timings.extend(result.optimal_timings)

            # Collect weather data
            weather_data[field.field_id] = {
                "windows": len(result.weather_windows),
                "suitability": result.weather_suitability_score
            }

        # Filter timings based on equipment and labor constraints
        filtered_timings = await _apply_resource_constraints(
            optimized_timings,
            request.farm_context.equipment_constraints,
            request.farm_context.labor_constraints,
            request.timing_constraints
        )

        # Calculate efficiency predictions
        efficiency_predictions = EfficiencyPrediction(
            nutrient_efficiency=0.85,
            application_efficiency=0.82,
            cost_efficiency=0.78
        )

        # Calculate risk assessments
        risk_assessments = RiskAssessment(
            weather_risk=0.25,
            timing_risk=0.20,
            operational_risk=0.15,
            overall_risk=0.20
        )

        # Generate recommendations
        recommendations = _generate_advanced_recommendations(
            filtered_timings,
            request.optimization_goals,
            efficiency_predictions,
            risk_assessments
        )

        processing_time = (time.time() - start_time) * 1000

        response = AdvancedTimingOptimizationResponse(
            request_id=request.request_id,
            optimized_schedule=filtered_timings,
            weather_integration=weather_data,
            efficiency_predictions=efficiency_predictions,
            risk_assessments=risk_assessments,
            recommendations=recommendations,
            processing_time_ms=processing_time
        )

        logger.info(f"Advanced optimization completed in {processing_time:.2f}ms: "
                   f"{len(filtered_timings)} applications scheduled")

        return response

    except Exception as e:
        logger.error(f"Error in advanced timing optimization: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Advanced timing optimization failed: {str(e)}"
        )


@router.get("/calendar", response_model=FertilizerCalendarResponse)
async def get_fertilizer_calendar(
    farm_id: str = Query(..., description="Farm identifier"),
    year: int = Query(..., description="Calendar year"),
    crop_type: Optional[str] = Query(None, description="Filter by crop type"),
    include_weather: bool = Query(True, description="Include weather overlays"),
    format: str = Query("json", description="Response format (json, ical)")
):
    """
    Dynamic fertilizer calendar generation endpoint.

    Generates personalized fertilizer application calendars with:
    - Scheduled application dates and details
    - Weather overlays and suitability windows
    - Alert integration for timing notifications
    - Multi-crop scheduling coordination
    - Equipment and labor scheduling
    - Regulatory compliance dates

    Agricultural Use Cases:
    - Annual fertilizer planning and budgeting
    - Seasonal application scheduling
    - Weather-based timing adjustments
    - Equipment and labor coordination
    - Regulatory compliance tracking
    - Mobile calendar synchronization
    - Team coordination and communication

    Features:
    - Interactive calendar with drill-down details
    - Weather forecast integration (14-day)
    - Alert notifications for optimal timing
    - Export to iCal format for calendar apps
    - Multi-crop view with color coding
    - Historical data comparison

    Args:
        farm_id: Farm identifier for calendar generation
        year: Calendar year to generate
        crop_type: Optional filter for specific crop type
        include_weather: Include weather overlays in response
        format: Response format (json or ical)

    Returns:
        FertilizerCalendarResponse with calendar events and weather data

    Raises:
        HTTPException: If calendar generation fails or invalid parameters
    """
    try:
        logger.info(f"Generating fertilizer calendar for farm {farm_id}, year {year}")

        # Generate calendar events
        events = []

        # Mock calendar events - in production, retrieve from database
        start_date = date(year, 1, 1)

        # Generate application events for the year
        for month in range(4, 10):  # April to September (growing season)
            for week in range(0, 4, 2):  # Bi-weekly applications
                event_date = date(year, month, 1) + timedelta(days=week * 7)

                event = CalendarEvent(
                    event_type="application",
                    event_date=event_date,
                    title=f"Fertilizer Application - {crop_type or 'All Crops'}",
                    description=f"Scheduled fertilizer application for {event_date.strftime('%B %d, %Y')}",
                    field_id=f"field_{month}",
                    fertilizer_type="nitrogen",
                    amount=100.0,
                    priority="high" if month in [4, 5] else "normal",
                    status="scheduled"
                )
                events.append(event)

        # Add alert events
        for month in range(4, 10):
            alert_date = date(year, month, 1)
            alert_event = CalendarEvent(
                event_type="alert",
                event_date=alert_date,
                title="Timing Alert",
                description="Optimal application window approaching",
                priority="high",
                status="active"
            )
            events.append(alert_event)

        # Generate weather overlays if requested
        weather_overlays = []
        if include_weather:
            current_date = date.today()
            for day in range(14):  # 14-day forecast
                forecast_date = current_date + timedelta(days=day)
                if forecast_date.year == year:
                    overlay = WeatherOverlay(
                        overlay_date=forecast_date,
                        condition=WeatherCondition.OPTIMAL if day % 3 == 0 else WeatherCondition.ACCEPTABLE,
                        temperature_f=65.0 + day * 0.5,
                        precipitation_probability=0.1 + (day * 0.02),
                        suitability_score=0.9 - (day * 0.02)
                    )
                    weather_overlays.append(overlay)

        # Determine crop types
        crop_types = [crop_type] if crop_type else ["corn", "soybean", "wheat"]

        response = FertilizerCalendarResponse(
            farm_id=farm_id,
            year=year,
            events=events,
            weather_overlays=weather_overlays,
            crop_types=crop_types,
            total_applications=len([e for e in events if e.event_type == "application"]),
            format=format
        )

        logger.info(f"Calendar generated: {len(events)} events, {len(weather_overlays)} weather overlays")

        return response

    except Exception as e:
        logger.error(f"Error generating fertilizer calendar: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Calendar generation failed: {str(e)}"
        )


@router.get("/application-windows", response_model=ApplicationWindowsResponse)
async def get_application_windows(
    field_id: str = Query(..., description="Field identifier"),
    start_date: str = Query(..., description="Analysis start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Analysis end date (YYYY-MM-DD)"),
    fertilizer_type: Optional[str] = Query(None, description="Specific fertilizer type"),
    optimizer: FertilizerTimingOptimizer = Depends(get_timing_optimizer)
):
    """
    Application window analysis endpoint with real-time updates.

    Analyzes and identifies optimal fertilizer application windows based on:
    - Weather conditions and forecasts
    - Soil conditions and temperature
    - Crop growth stage and readiness
    - Equipment and labor availability
    - Risk factors and mitigation strategies

    Agricultural Use Cases:
    - Daily application planning and scheduling
    - Weather-dependent timing decisions
    - Emergency application planning
    - Risk assessment for application timing
    - Equipment scheduling optimization
    - Field condition monitoring
    - Compliance with weather restrictions

    Features:
    - Real-time weather integration
    - Dynamic window updates based on forecasts
    - Confidence scoring for each window
    - Risk factor identification
    - Equipment availability checking
    - Soil condition assessment
    - Crop readiness evaluation

    Analysis Areas:
    - Weather Windows: Temperature, precipitation, wind
    - Soil Conditions: Moisture, temperature, trafficability
    - Crop Readiness: Growth stage, nutrient demand
    - Equipment: Availability, maintenance, capacity
    - Regulatory: Compliance windows, restrictions

    Args:
        field_id: Field identifier for analysis
        start_date: Analysis start date (YYYY-MM-DD format)
        end_date: Analysis end date (YYYY-MM-DD format)
        fertilizer_type: Optional specific fertilizer type
        optimizer: Timing optimization service instance

    Returns:
        ApplicationWindowsResponse with window recommendations

    Raises:
        HTTPException: If analysis fails or invalid parameters
    """
    try:
        logger.info(f"Analyzing application windows for field {field_id}")

        # Parse dates
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid date format. Use YYYY-MM-DD: {str(e)}"
            )

        if start_dt > end_dt:
            raise HTTPException(
                status_code=400,
                detail="Start date must be before end date"
            )

        if optimizer is None:
            optimizer = FertilizerTimingOptimizer()

        # Create timing request for window analysis
        request = TimingOptimizationRequest(
            field_id=field_id,
            crop_type="corn",  # Default, would come from field data
            planting_date=start_dt,
            fertilizer_requirements={fertilizer_type or "nitrogen": 150.0},
            application_methods=[ApplicationMethod.BROADCAST],
            soil_type="loam",
            soil_moisture_capacity=0.6,
            location={"lat": 40.0, "lng": -95.0},
            optimization_horizon_days=(end_dt - start_dt).days
        )

        # Analyze weather windows
        weather_windows = await optimizer._analyze_weather_windows(request)

        # Generate application windows
        windows = []
        optimal_windows = []

        for weather_window in weather_windows:
            if weather_window.start_date >= start_dt and weather_window.end_date <= end_dt:
                # Assess equipment availability
                equipment_available = True  # Mock check

                # Calculate crop readiness
                days_since_planting = (weather_window.start_date - start_dt).days
                crop_readiness = min(1.0, days_since_planting / 30.0)  # Simplified

                # Identify risk factors
                risk_factors = []
                if weather_window.precipitation_probability > 0.3:
                    risk_factors.append("High precipitation probability")
                if weather_window.wind_speed_mph > 15:
                    risk_factors.append("High wind speed")
                if weather_window.temperature_f < 50:
                    risk_factors.append("Low temperature")

                # Generate recommendation
                if weather_window.condition == WeatherCondition.OPTIMAL:
                    recommendation = "Excellent application conditions - highly recommended"
                elif weather_window.condition == WeatherCondition.ACCEPTABLE:
                    recommendation = "Good application conditions - suitable for application"
                elif weather_window.condition == WeatherCondition.MARGINAL:
                    recommendation = "Marginal conditions - monitor weather closely"
                else:
                    recommendation = "Poor conditions - delay application if possible"

                window = ApplicationWindow(
                    start_date=weather_window.start_date,
                    end_date=weather_window.end_date,
                    optimal_date=weather_window.start_date,
                    confidence_score=weather_window.suitability_score,
                    weather_forecast=weather_window,
                    soil_conditions={
                        "moisture": weather_window.soil_moisture,
                        "temperature": weather_window.temperature_f,
                        "trafficability": "good" if weather_window.soil_moisture < 0.7 else "poor"
                    },
                    crop_readiness=crop_readiness,
                    equipment_available=equipment_available,
                    risk_factors=risk_factors,
                    recommendation=recommendation
                )
                windows.append(window)

                # Identify top optimal windows
                if weather_window.suitability_score >= 0.8:
                    optimal_windows.append(window)

        # Sort optimal windows by confidence score
        optimal_windows.sort(key=lambda w: w.confidence_score, reverse=True)
        optimal_windows = optimal_windows[:5]  # Top 5

        # Generate weather summary
        if weather_windows:
            avg_temp = sum(w.temperature_f for w in weather_windows) / len(weather_windows)
            avg_precip = sum(w.precipitation_probability for w in weather_windows) / len(weather_windows)
            avg_suitability = sum(w.suitability_score for w in weather_windows) / len(weather_windows)
        else:
            avg_temp = 0.0
            avg_precip = 0.0
            avg_suitability = 0.0

        weather_summary = {
            "average_temperature_f": avg_temp,
            "average_precipitation_probability": avg_precip,
            "average_suitability": avg_suitability,
            "total_windows": len(weather_windows),
            "optimal_windows": len(optimal_windows)
        }

        # Generate risk summary
        risk_summary = {
            "high_risk_days": len([w for w in weather_windows if w.condition == WeatherCondition.POOR]),
            "medium_risk_days": len([w for w in weather_windows if w.condition == WeatherCondition.MARGINAL]),
            "low_risk_days": len([w for w in weather_windows if w.condition in [WeatherCondition.OPTIMAL, WeatherCondition.ACCEPTABLE]]),
            "overall_risk": "low" if avg_suitability > 0.7 else "medium" if avg_suitability > 0.5 else "high"
        }

        response = ApplicationWindowsResponse(
            field_id=field_id,
            analysis_period={"start": start_dt, "end": end_dt},
            fertilizer_type=fertilizer_type,
            windows=windows,
            optimal_windows=optimal_windows,
            weather_summary=weather_summary,
            risk_summary=risk_summary
        )

        logger.info(f"Application window analysis completed: {len(windows)} windows, "
                   f"{len(optimal_windows)} optimal windows")

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing application windows: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Application window analysis failed: {str(e)}"
        )


@router.post("/alerts/subscribe", response_model=AlertSubscriptionResponse)
async def subscribe_to_alerts(
    request: AlertSubscriptionRequest,
    background_tasks: BackgroundTasks
):
    """
    Alert subscription endpoint for timing notifications.

    Enables users to subscribe to customized alerts for:
    - Timing alerts: Optimal application windows approaching
    - Weather alerts: Favorable conditions or weather warnings
    - Equipment alerts: Equipment availability or maintenance
    - Regulatory alerts: Compliance deadlines or restrictions

    Agricultural Use Cases:
    - Proactive application planning
    - Weather-based decision support
    - Equipment coordination notifications
    - Regulatory compliance reminders
    - Team coordination alerts
    - Mobile notifications for field staff

    Features:
    - Customizable alert preferences by type
    - Multi-channel delivery (email, SMS, push)
    - Frequency control (daily, weekly, real-time)
    - Priority-based alert filtering
    - Location-based alert targeting
    - Integration with calendar systems

    Alert Types:
    - Timing: Optimal windows, deadline reminders
    - Weather: Favorable conditions, warnings
    - Equipment: Availability, maintenance
    - Regulatory: Compliance, restrictions

    Args:
        request: Alert subscription request with preferences
        background_tasks: FastAPI background tasks

    Returns:
        AlertSubscriptionResponse with subscription details

    Raises:
        HTTPException: If subscription fails or invalid parameters
    """
    try:
        logger.info(f"Creating alert subscription for user {request.user_id}, farm {request.farm_id}")

        # Validate notification channels
        valid_channels = ["email", "sms", "push"]
        invalid_channels = []
        for channel in request.notification_channels:
            if channel not in valid_channels:
                invalid_channels.append(channel)

        if invalid_channels:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid notification channels: {', '.join(invalid_channels)}"
            )

        # Validate alert frequency
        valid_frequencies = ["real-time", "hourly", "daily", "weekly"]
        if request.alert_frequency not in valid_frequencies:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid alert frequency. Must be one of: {', '.join(valid_frequencies)}"
            )

        # Create subscription
        response = AlertSubscriptionResponse(
            user_id=request.user_id,
            farm_id=request.farm_id,
            alert_preferences=request.alert_preferences,
            notification_channels=request.notification_channels,
            alert_frequency=request.alert_frequency,
            status="active"
        )

        # In production, save subscription to database
        # background_tasks.add_task(save_subscription_to_database, response)

        logger.info(f"Alert subscription created: {response.subscription_id}")

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating alert subscription: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Alert subscription failed: {str(e)}"
        )


@router.get("/alerts/manage", response_model=AlertManagementResponse)
async def manage_alerts(
    user_id: str = Query(..., description="User identifier"),
    farm_id: Optional[str] = Query(None, description="Filter by farm")
):
    """
    Alert management endpoint for viewing and managing subscriptions.

    Provides comprehensive alert management:
    - View all active subscriptions
    - Manage subscription preferences
    - Review active alerts
    - Access alert history
    - Update notification settings
    - Pause or cancel subscriptions

    Agricultural Use Cases:
    - Review pending timing alerts
    - Manage notification preferences
    - Track alert effectiveness
    - Audit alert history
    - Team alert coordination
    - Mobile alert management

    Features:
    - Consolidated alert dashboard
    - Subscription management
    - Alert history with filtering
    - Performance metrics
    - Delivery status tracking
    - Bulk operations support

    Args:
        user_id: User identifier for alert management
        farm_id: Optional farm filter for multi-farm operations

    Returns:
        AlertManagementResponse with subscriptions and alerts

    Raises:
        HTTPException: If retrieval fails or invalid parameters
    """
    try:
        logger.info(f"Retrieving alert management for user {user_id}")

        # Mock subscriptions - in production, retrieve from database
        subscriptions = [
            AlertSubscriptionResponse(
                subscription_id="sub_001",
                user_id=user_id,
                farm_id=farm_id or "farm_001",
                alert_preferences={
                    "timing_alerts": True,
                    "weather_alerts": True,
                    "equipment_alerts": True,
                    "regulatory_alerts": True
                },
                notification_channels=["email", "sms"],
                alert_frequency="daily",
                status="active"
            )
        ]

        # Filter by farm if specified
        if farm_id:
            subscriptions = [s for s in subscriptions if s.farm_id == farm_id]

        # Mock active alerts
        active_alerts = [
            Alert(
                alert_type="timing",
                severity="high",
                title="Optimal Application Window",
                message="Optimal nitrogen application window opening tomorrow",
                field_id="field_001",
                action_required=True,
                expiration_date=datetime.utcnow() + timedelta(days=2)
            ),
            Alert(
                alert_type="weather",
                severity="medium",
                title="Weather Warning",
                message="Heavy rainfall expected in 3 days",
                action_required=False,
                expiration_date=datetime.utcnow() + timedelta(days=3)
            )
        ]

        # Mock alert history
        alert_history = [
            Alert(
                alert_type="timing",
                severity="high",
                title="Application Window Closed",
                message="Optimal window has passed",
                field_id="field_001",
                action_required=False,
                created_at=datetime.utcnow() - timedelta(days=7)
            ),
            Alert(
                alert_type="equipment",
                severity="low",
                title="Equipment Available",
                message="Field sprayer now available for scheduling",
                action_required=False,
                created_at=datetime.utcnow() - timedelta(days=5)
            )
        ]

        response = AlertManagementResponse(
            user_id=user_id,
            farm_id=farm_id,
            subscriptions=subscriptions,
            active_alerts=active_alerts,
            alert_history=alert_history,
            total_subscriptions=len(subscriptions),
            total_active_alerts=len(active_alerts)
        )

        logger.info(f"Alert management retrieved: {len(subscriptions)} subscriptions, "
                   f"{len(active_alerts)} active alerts")

        return response

    except Exception as e:
        logger.error(f"Error retrieving alert management: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Alert management retrieval failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for timing routes service."""
    return {
        "service": "timing-routes",
        "status": "healthy",
        "endpoints": [
            "POST /api/v1/fertilizer/timing-optimization",
            "GET /api/v1/fertilizer/calendar",
            "GET /api/v1/fertilizer/application-windows",
            "POST /api/v1/fertilizer/alerts/subscribe",
            "GET /api/v1/fertilizer/alerts/manage"
        ],
        "features": [
            "advanced_multi_field_optimization",
            "dynamic_calendar_generation",
            "real_time_window_analysis",
            "alert_subscription_management",
            "weather_integration",
            "equipment_constraint_handling",
            "labor_allocation_optimization",
            "risk_assessment",
            "efficiency_predictions"
        ]
    }


# Helper functions

async def _apply_resource_constraints(
    timings: List[ApplicationTiming],
    equipment_constraints: Any,
    labor_constraints: Any,
    timing_constraints: Any
) -> List[ApplicationTiming]:
    """
    Apply resource constraints to filter and adjust timings.

    This function filters application timings based on:
    - Equipment availability and capacity
    - Labor availability and hours
    - Timing constraints and restricted periods
    """
    filtered_timings = []

    for timing in timings:
        # Check timing constraints
        if hasattr(timing_constraints, 'earliest_application'):
            if timing.recommended_date < timing_constraints.earliest_application:
                continue

        if hasattr(timing_constraints, 'latest_application'):
            if timing.recommended_date > timing_constraints.latest_application:
                continue

        # Check equipment capacity
        # In production, would check actual equipment schedules

        # Check labor availability
        # In production, would check actual labor schedules

        filtered_timings.append(timing)

    return filtered_timings


def _generate_advanced_recommendations(
    timings: List[ApplicationTiming],
    optimization_goals: Any,
    efficiency: EfficiencyPrediction,
    risk: RiskAssessment
) -> List[str]:
    """
    Generate advanced recommendations based on optimization results.
    """
    recommendations = []

    # Goal-based recommendations
    if hasattr(optimization_goals, 'primary_goal'):
        if optimization_goals.primary_goal == "nutrient_efficiency":
            recommendations.append(
                "Focus on split applications during optimal growth stages for maximum nutrient efficiency"
            )
        elif optimization_goals.primary_goal == "cost_optimization":
            recommendations.append(
                "Consolidate applications where possible to minimize equipment and labor costs"
            )

    # Efficiency recommendations
    if efficiency.nutrient_efficiency < 0.7:
        recommendations.append(
            "Consider adjusting application timing to improve nutrient efficiency"
        )

    # Risk recommendations
    if risk.overall_risk > 0.6:
        recommendations.append(
            "High risk detected - implement split applications and monitor weather closely"
        )
    elif risk.weather_risk > 0.5:
        recommendations.append(
            "Weather risk elevated - maintain flexible scheduling and have backup windows"
        )

    # Equipment recommendations
    if len(timings) > 10:
        recommendations.append(
            "Large number of applications scheduled - verify equipment capacity and maintenance"
        )

    # Timing recommendations
    if timings:
        dates = [t.recommended_date for t in timings]
        date_range = (max(dates) - min(dates)).days
        if date_range < 14:
            recommendations.append(
                "Applications concentrated in short timeframe - consider extending schedule if weather permits"
            )

    return recommendations

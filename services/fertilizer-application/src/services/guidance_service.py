"""
Guidance Service for fertilizer application guidance and best practices.
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional
from uuid import uuid4
from datetime import datetime, date

from ..models.application_models import (
    GuidanceRequest, GuidanceResponse, ApplicationGuidance,
    ApplicationMethod, FieldConditions
)

logger = logging.getLogger(__name__)


class GuidanceService:
    """Service for providing comprehensive application guidance and best practices."""
    
    def __init__(self):
        self.guidance_database = {}
        self._initialize_guidance_database()
    
    def _initialize_guidance_database(self):
        """Initialize guidance database with best practices and instructions."""
        self.guidance_database = {
            "broadcast": {
                "pre_application": [
                    "Calibrate spreader according to manufacturer specifications",
                    "Check spread pattern uniformity across boom width",
                    "Ensure fertilizer is dry and free-flowing",
                    "Check weather conditions - avoid windy conditions",
                    "Verify field boundaries and obstacles",
                    "Test equipment operation in non-crop area"
                ],
                "application": [
                    "Maintain consistent ground speed throughout application",
                    "Overlap spread pattern by 10-15% for uniform coverage",
                    "Monitor application rate continuously",
                    "Avoid application during peak wind hours (10 AM - 4 PM)",
                    "Keep fertilizer hopper at least 1/3 full for consistent flow",
                    "Make parallel passes with minimal overlap"
                ],
                "post_application": [
                    "Clean spreader thoroughly after application",
                    "Record application details (rate, date, weather, field)",
                    "Monitor crop response for 7-14 days",
                    "Check for any missed areas or double applications",
                    "Store remaining fertilizer properly",
                    "Schedule next application if needed"
                ],
                "safety": [
                    "Wear appropriate personal protective equipment (PPE)",
                    "Avoid skin contact with fertilizer",
                    "Ensure good ventilation in enclosed areas",
                    "Keep fertilizer away from water sources",
                    "Follow manufacturer safety guidelines",
                    "Have emergency contact information readily available"
                ],
                "calibration": [
                    "Measure spread width accurately",
                    "Collect fertilizer from known area for weight measurement",
                    "Calculate actual application rate",
                    "Adjust settings to achieve target rate",
                    "Repeat calibration until within 5% of target",
                    "Document calibration results"
                ],
                "troubleshooting": [
                    "Uneven spread pattern: Check for clogged outlets or worn parts",
                    "Rate too high: Reduce gate opening or increase speed",
                    "Rate too low: Increase gate opening or decrease speed",
                    "Poor flow: Check for moisture or clumping in fertilizer",
                    "Equipment vibration: Check for loose bolts or worn bearings",
                    "Inconsistent application: Verify ground speed and calibration"
                ]
            },
            "band": {
                "pre_application": [
                    "Calibrate banding equipment for precise placement",
                    "Check band width and depth settings",
                    "Ensure fertilizer is compatible with banding equipment",
                    "Verify soil conditions are suitable for banding",
                    "Check for rocks or debris that could damage equipment",
                    "Test equipment operation in non-crop area"
                ],
                "application": [
                    "Maintain consistent depth throughout application",
                    "Keep bands parallel and evenly spaced",
                    "Monitor band width and fertilizer placement",
                    "Avoid placing bands too close to seed (minimum 2 inches)",
                    "Maintain steady ground speed for uniform application",
                    "Check band quality periodically during application"
                ],
                "post_application": [
                    "Inspect band placement and quality",
                    "Record application details and band placement",
                    "Monitor crop emergence and early growth",
                    "Check for fertilizer burn on seedlings",
                    "Clean equipment thoroughly",
                    "Schedule follow-up applications if needed"
                ],
                "safety": [
                    "Wear appropriate PPE including gloves and eye protection",
                    "Avoid breathing fertilizer dust",
                    "Keep fertilizer away from water sources",
                    "Follow equipment manufacturer safety guidelines",
                    "Ensure good ventilation in enclosed areas",
                    "Have emergency contact information available"
                ],
                "calibration": [
                    "Measure band width and depth accurately",
                    "Collect fertilizer from known band length",
                    "Calculate actual application rate per band",
                    "Adjust settings to achieve target rate",
                    "Verify band placement depth",
                    "Document calibration results"
                ],
                "troubleshooting": [
                    "Bands too wide: Adjust banding equipment settings",
                    "Bands too deep: Raise banding equipment",
                    "Uneven band placement: Check for equipment wear or misalignment",
                    "Fertilizer burn: Increase distance from seed or reduce rate",
                    "Poor band quality: Check fertilizer flow and equipment condition",
                    "Inconsistent depth: Verify ground contact and equipment settings"
                ]
            },
            "sidedress": {
                "pre_application": [
                    "Calibrate sidedress equipment for precise placement",
                    "Check crop growth stage and timing requirements",
                    "Ensure fertilizer is compatible with injection equipment",
                    "Verify soil moisture conditions are adequate",
                    "Check for crop damage from previous operations",
                    "Test equipment operation in non-crop area"
                ],
                "application": [
                    "Place fertilizer 4-6 inches from crop row",
                    "Maintain consistent injection depth (4-6 inches)",
                    "Monitor crop condition during application",
                    "Avoid application during hot, dry conditions",
                    "Maintain steady ground speed for uniform placement",
                    "Check injection quality periodically"
                ],
                "post_application": [
                    "Inspect injection placement and quality",
                    "Monitor crop response for signs of stress",
                    "Record application details and crop stage",
                    "Check for fertilizer burn on crop roots",
                    "Clean equipment thoroughly",
                    "Schedule follow-up monitoring"
                ],
                "safety": [
                    "Wear appropriate PPE including gloves and eye protection",
                    "Avoid skin contact with liquid fertilizers",
                    "Keep fertilizer away from water sources",
                    "Follow equipment manufacturer safety guidelines",
                    "Ensure good ventilation in enclosed areas",
                    "Have emergency contact information available"
                ],
                "calibration": [
                    "Measure injection depth and distance from row",
                    "Collect fertilizer from known injection points",
                    "Calculate actual application rate",
                    "Adjust settings to achieve target rate",
                    "Verify injection depth consistency",
                    "Document calibration results"
                ],
                "troubleshooting": [
                    "Injection too shallow: Lower injection equipment",
                    "Injection too deep: Raise injection equipment",
                    "Too close to crop: Adjust injection position",
                    "Fertilizer burn: Increase distance from crop or reduce rate",
                    "Poor injection quality: Check equipment condition and settings",
                    "Inconsistent placement: Verify ground contact and speed"
                ]
            },
            "foliar": {
                "pre_application": [
                    "Calibrate sprayer for precise application rate",
                    "Check nozzle condition and spray pattern",
                    "Ensure fertilizer is compatible with foliar application",
                    "Verify crop growth stage is appropriate",
                    "Check weather conditions (temperature, humidity, wind)",
                    "Test equipment operation in non-crop area"
                ],
                "application": [
                    "Apply during early morning or late evening",
                    "Maintain consistent spray pressure",
                    "Ensure complete leaf coverage without runoff",
                    "Monitor crop condition during application",
                    "Avoid application during hot, sunny conditions",
                    "Maintain steady ground speed for uniform coverage"
                ],
                "post_application": [
                    "Monitor crop response for 3-7 days",
                    "Check for leaf burn or phytotoxicity",
                    "Record application details and weather conditions",
                    "Clean sprayer thoroughly",
                    "Schedule follow-up applications if needed",
                    "Monitor for pest or disease issues"
                ],
                "safety": [
                    "Wear appropriate PPE including respirator and eye protection",
                    "Avoid skin contact with fertilizer solutions",
                    "Keep fertilizer away from water sources",
                    "Follow equipment manufacturer safety guidelines",
                    "Ensure good ventilation in enclosed areas",
                    "Have emergency contact information available"
                ],
                "calibration": [
                    "Measure spray width and application rate",
                    "Collect spray solution from known area",
                    "Calculate actual application rate",
                    "Adjust settings to achieve target rate",
                    "Verify spray pattern uniformity",
                    "Document calibration results"
                ],
                "troubleshooting": [
                    "Poor coverage: Check nozzle condition and spray pattern",
                    "Leaf burn: Reduce application rate or avoid hot conditions",
                    "Runoff: Reduce application rate or improve coverage",
                    "Inconsistent application: Check spray pressure and ground speed",
                    "Equipment issues: Check for clogged nozzles or worn parts",
                    "Weather problems: Reschedule application for better conditions"
                ]
            },
            "injection": {
                "pre_application": [
                    "Calibrate injection equipment for precise rate",
                    "Check injection depth and spacing settings",
                    "Ensure fertilizer is compatible with injection system",
                    "Verify soil conditions are suitable for injection",
                    "Check for rocks or debris that could damage equipment",
                    "Test equipment operation in non-crop area"
                ],
                "application": [
                    "Maintain consistent injection depth",
                    "Keep injection points evenly spaced",
                    "Monitor injection rate and pressure",
                    "Avoid injection during wet soil conditions",
                    "Maintain steady ground speed for uniform placement",
                    "Check injection quality periodically"
                ],
                "post_application": [
                    "Inspect injection placement and quality",
                    "Monitor soil conditions and crop response",
                    "Record application details and injection depth",
                    "Check for soil compaction from injection",
                    "Clean equipment thoroughly",
                    "Schedule follow-up monitoring"
                ],
                "safety": [
                    "Wear appropriate PPE including gloves and eye protection",
                    "Avoid skin contact with liquid fertilizers",
                    "Keep fertilizer away from water sources",
                    "Follow equipment manufacturer safety guidelines",
                    "Ensure good ventilation in enclosed areas",
                    "Have emergency contact information available"
                ],
                "calibration": [
                    "Measure injection depth and spacing",
                    "Collect fertilizer from known injection points",
                    "Calculate actual application rate",
                    "Adjust settings to achieve target rate",
                    "Verify injection depth consistency",
                    "Document calibration results"
                ],
                "troubleshooting": [
                    "Injection too shallow: Lower injection equipment",
                    "Injection too deep: Raise injection equipment",
                    "Uneven spacing: Check equipment alignment and wear",
                    "Poor injection quality: Check equipment condition and settings",
                    "Soil compaction: Reduce injection depth or pressure",
                    "Inconsistent rate: Verify ground speed and equipment settings"
                ]
            },
            "drip": {
                "pre_application": [
                    "Check drip system pressure and flow rates",
                    "Ensure fertilizer is compatible with drip irrigation",
                    "Verify system is clean and free of blockages",
                    "Check emitter spacing and flow rates",
                    "Test fertilizer injection system",
                    "Verify system coverage and uniformity"
                ],
                "application": [
                    "Inject fertilizer during irrigation cycle",
                    "Maintain consistent injection rate",
                    "Monitor system pressure and flow",
                    "Ensure uniform distribution across field",
                    "Avoid over-application or system overload",
                    "Monitor crop response during application"
                ],
                "post_application": [
                    "Flush system with clean water",
                    "Monitor crop response for 3-7 days",
                    "Record application details and system performance",
                    "Check for any system issues or blockages",
                    "Schedule next application if needed",
                    "Monitor for pest or disease issues"
                ],
                "safety": [
                    "Wear appropriate PPE including gloves and eye protection",
                    "Avoid skin contact with fertilizer solutions",
                    "Keep fertilizer away from water sources",
                    "Follow equipment manufacturer safety guidelines",
                    "Ensure good ventilation in enclosed areas",
                    "Have emergency contact information available"
                ],
                "calibration": [
                    "Measure system flow rates and pressure",
                    "Calculate actual application rate",
                    "Adjust injection rate to achieve target",
                    "Verify uniform distribution across field",
                    "Check emitter flow rates",
                    "Document calibration results"
                ],
                "troubleshooting": [
                    "Poor flow: Check for blockages or pressure issues",
                    "Uneven distribution: Check emitter spacing and flow rates",
                    "System overload: Reduce injection rate or increase flow",
                    "Blockages: Clean system and check filtration",
                    "Pressure problems: Check pump and system components",
                    "Inconsistent application: Verify injection rate and timing"
                ]
            }
        }
    
    async def provide_application_guidance(
        self, 
        request: GuidanceRequest
    ) -> GuidanceResponse:
        """
        Provide comprehensive application guidance for the selected method.
        
        Args:
            request: Guidance request with application method, field conditions, and context
            
        Returns:
            GuidanceResponse with detailed guidance and instructions
        """
        start_time = time.time()
        request_id = str(uuid4())
        
        try:
            logger.info(f"Providing application guidance for request {request_id}")
            
            # Get method-specific guidance
            method_guidance = await self._get_method_guidance(request.application_method)
            
            # Generate weather advisories
            weather_advisories = await self._generate_weather_advisories(
                request.weather_conditions, request.application_method
            )
            
            # Generate equipment preparation steps
            equipment_preparation = await self._generate_equipment_preparation(
                request.application_method, request.field_conditions
            )
            
            # Generate quality control measures
            quality_control_measures = await self._generate_quality_control_measures(
                request.application_method, request.field_conditions
            )
            
            # Create comprehensive guidance
            guidance = ApplicationGuidance(
                guidance_id=f"guidance_{request_id}",
                pre_application_checklist=method_guidance["pre_application"],
                application_instructions=method_guidance["application"],
                safety_precautions=method_guidance["safety"],
                calibration_instructions=method_guidance["calibration"],
                troubleshooting_tips=method_guidance["troubleshooting"],
                post_application_tasks=method_guidance["post_application"],
                optimal_conditions=self._determine_optimal_conditions(
                    request.application_method, request.field_conditions, request.weather_conditions
                ),
                timing_recommendations=self._generate_timing_recommendations(
                    request.application_method, request.field_conditions, request.application_date
                )
            )
            
            processing_time_ms = (time.time() - start_time) * 1000
            
            response = GuidanceResponse(
                request_id=request_id,
                guidance=guidance,
                weather_advisories=weather_advisories,
                equipment_preparation=equipment_preparation,
                quality_control_measures=quality_control_measures,
                processing_time_ms=processing_time_ms
            )
            
            logger.info(f"Application guidance provided in {processing_time_ms:.2f}ms")
            return response
            
        except Exception as e:
            logger.error(f"Error providing application guidance: {e}")
            raise
    
    async def _get_method_guidance(self, application_method: ApplicationMethod) -> Dict[str, List[str]]:
        """Get method-specific guidance from database."""
        method_type = application_method.method_type.lower()
        
        if method_type in self.guidance_database:
            return self.guidance_database[method_type]
        else:
            # Return generic guidance if method not found
            return {
                "pre_application": [
                    "Calibrate equipment according to manufacturer specifications",
                    "Check weather conditions before application",
                    "Verify field conditions are suitable",
                    "Test equipment operation in non-crop area"
                ],
                "application": [
                    "Maintain consistent application rate",
                    "Monitor equipment performance",
                    "Follow safety guidelines",
                    "Record application details"
                ],
                "post_application": [
                    "Clean equipment thoroughly",
                    "Monitor crop response",
                    "Record application details",
                    "Schedule follow-up if needed"
                ],
                "safety": [
                    "Wear appropriate personal protective equipment",
                    "Follow manufacturer safety guidelines",
                    "Keep fertilizer away from water sources",
                    "Have emergency contact information available"
                ],
                "calibration": [
                    "Measure application rate accurately",
                    "Adjust settings to achieve target rate",
                    "Verify calibration results",
                    "Document calibration process"
                ],
                "troubleshooting": [
                    "Check equipment condition regularly",
                    "Monitor application quality",
                    "Address issues promptly",
                    "Consult manufacturer if needed"
                ]
            }
    
    async def _generate_weather_advisories(
        self, 
        weather_conditions: Optional[Dict[str, Any]], 
        application_method: ApplicationMethod
    ) -> Optional[List[str]]:
        """Generate weather-related advisories."""
        if not weather_conditions:
            return None
        
        advisories = []
        
        # Check wind conditions
        wind_speed = weather_conditions.get("wind_speed_kmh", 0)
        if wind_speed > 15:  # High wind
            advisories.append("High wind conditions detected - consider postponing application")
        elif wind_speed > 10:  # Moderate wind
            advisories.append("Moderate wind conditions - monitor application quality closely")
        
        # Check temperature conditions
        temperature = weather_conditions.get("temperature_celsius", 20)
        if temperature > 30:  # Hot conditions
            advisories.append("Hot conditions - avoid application during peak heat hours")
        elif temperature < 5:  # Cold conditions
            advisories.append("Cold conditions - ensure fertilizer is properly dissolved")
        
        # Check humidity conditions
        humidity = weather_conditions.get("humidity_percent", 50)
        if humidity > 80:  # High humidity
            advisories.append("High humidity - monitor for condensation issues")
        
        # Check precipitation
        precipitation = weather_conditions.get("precipitation_mm", 0)
        if precipitation > 0:
            advisories.append("Precipitation detected - postpone application until conditions improve")
        
        # Method-specific weather advisories
        method_type = application_method.method_type.lower()
        if method_type == "foliar":
            if temperature > 25:
                advisories.append("High temperature - risk of leaf burn with foliar application")
            if humidity < 30:
                advisories.append("Low humidity - increased risk of leaf burn")
        
        elif method_type == "broadcast":
            if wind_speed > 8:
                advisories.append("Wind conditions may affect broadcast pattern uniformity")
        
        return advisories if advisories else None
    
    async def _generate_equipment_preparation(
        self, 
        application_method: ApplicationMethod, 
        field_conditions: FieldConditions
    ) -> Optional[List[str]]:
        """Generate equipment preparation steps."""
        preparation_steps = []
        
        method_type = application_method.method_type.lower()
        
        # General equipment preparation
        preparation_steps.extend([
            "Inspect equipment for wear and damage",
            "Check all safety systems and guards",
            "Verify fuel and fluid levels",
            "Test all controls and functions"
        ])
        
        # Method-specific preparation
        if method_type == "sprayer":
            preparation_steps.extend([
                "Check nozzle condition and spray pattern",
                "Verify spray pressure and flow rates",
                "Test agitation system",
                "Check filtration system"
            ])
        
        elif method_type == "spreader":
            preparation_steps.extend([
                "Check spread pattern uniformity",
                "Verify gate opening and flow rates",
                "Test ground speed and application rate",
                "Check for worn or damaged parts"
            ])
        
        elif method_type == "injector":
            preparation_steps.extend([
                "Check injection depth and spacing",
                "Verify injection rate and pressure",
                "Test injection system operation",
                "Check for blockages or leaks"
            ])
        
        # Field-specific preparation
        if field_conditions.slope_percent and field_conditions.slope_percent > 5:
            preparation_steps.append("Check equipment stability on slopes")
        
        if field_conditions.soil_type.lower() == "clay":
            preparation_steps.append("Verify equipment can handle heavy soil conditions")
        
        return preparation_steps
    
    async def _generate_quality_control_measures(
        self, 
        application_method: ApplicationMethod, 
        field_conditions: FieldConditions
    ) -> Optional[List[str]]:
        """Generate quality control measures."""
        quality_measures = []
        
        method_type = application_method.method_type.lower()
        
        # General quality control measures
        quality_measures.extend([
            "Monitor application rate continuously",
            "Check for uniform coverage",
            "Verify equipment calibration",
            "Record application details"
        ])
        
        # Method-specific quality control
        if method_type == "broadcast":
            quality_measures.extend([
                "Check spread pattern uniformity",
                "Verify overlap between passes",
                "Monitor ground speed consistency",
                "Check for missed areas"
            ])
        
        elif method_type == "band":
            quality_measures.extend([
                "Verify band width and depth",
                "Check band placement accuracy",
                "Monitor band quality",
                "Verify distance from seed"
            ])
        
        elif method_type == "foliar":
            quality_measures.extend([
                "Check spray coverage",
                "Monitor for leaf burn",
                "Verify application rate",
                "Check for runoff"
            ])
        
        elif method_type == "injection":
            quality_measures.extend([
                "Verify injection depth",
                "Check injection spacing",
                "Monitor injection rate",
                "Verify soil conditions"
            ])
        
        # Field-specific quality control
        if field_conditions.field_size_acres > 100:
            quality_measures.append("Increase monitoring frequency for large fields")
        
        if field_conditions.irrigation_available:
            quality_measures.append("Coordinate with irrigation schedule")
        
        return quality_measures
    
    def _determine_optimal_conditions(
        self, 
        application_method: ApplicationMethod, 
        field_conditions: FieldConditions,
        weather_conditions: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Determine optimal application conditions."""
        method_type = application_method.method_type.lower()
        
        optimal_conditions = {
            "temperature_range": "15-25°C",
            "humidity_range": "40-70%",
            "wind_speed_max": "10 km/h",
            "soil_moisture": "Field capacity",
            "soil_temperature": "10-15°C"
        }
        
        # Method-specific optimal conditions
        if method_type == "foliar":
            optimal_conditions.update({
                "temperature_range": "18-25°C",
                "humidity_range": "50-80%",
                "wind_speed_max": "8 km/h",
                "application_time": "Early morning or late evening"
            })
        
        elif method_type == "broadcast":
            optimal_conditions.update({
                "wind_speed_max": "12 km/h",
                "application_time": "Early morning or late evening"
            })
        
        elif method_type == "injection":
            optimal_conditions.update({
                "soil_moisture": "Moist but not wet",
                "soil_temperature": "8-12°C"
            })
        
        # Field-specific adjustments
        if field_conditions.slope_percent and field_conditions.slope_percent > 5:
            optimal_conditions["wind_speed_max"] = "8 km/h"
        
        if field_conditions.soil_type.lower() == "clay":
            optimal_conditions["soil_moisture"] = "Slightly dry"
        
        return optimal_conditions
    
    def _generate_timing_recommendations(
        self, 
        application_method: ApplicationMethod, 
        field_conditions: FieldConditions,
        application_date: Optional[date]
    ) -> Optional[str]:
        """Generate timing recommendations."""
        method_type = application_method.method_type.lower()
        
        timing_recommendations = []
        
        # General timing recommendations
        timing_recommendations.append("Apply during early morning or late evening for best results")
        
        # Method-specific timing
        if method_type == "foliar":
            timing_recommendations.append("Avoid application during hot, sunny conditions")
            timing_recommendations.append("Apply when leaves are dry but humidity is moderate")
        
        elif method_type == "broadcast":
            timing_recommendations.append("Apply when wind conditions are calm")
            timing_recommendations.append("Avoid application during peak wind hours")
        
        elif method_type == "sidedress":
            timing_recommendations.append("Apply when crop is at appropriate growth stage")
            timing_recommendations.append("Ensure soil moisture is adequate for uptake")
        
        elif method_type == "injection":
            timing_recommendations.append("Apply when soil conditions are suitable for injection")
            timing_recommendations.append("Avoid application during wet soil conditions")
        
        # Field-specific timing
        if field_conditions.irrigation_available:
            timing_recommendations.append("Coordinate with irrigation schedule if possible")
        
        if application_date:
            timing_recommendations.append(f"Planned application date: {application_date}")
        
        return "; ".join(timing_recommendations)
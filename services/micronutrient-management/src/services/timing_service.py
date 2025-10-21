"""
Timing Service for Micronutrient Management

This service provides logic for timing recommendations considering crop growth stages,
nutrient uptake patterns, weather conditions, and compatibility with other inputs.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
import random

from ..schemas.micronutrient_schemas import (
    TimingRecommendationRequest,
    TimingRecommendation,
    TimingRecommendationType,
    ApplicationMethod,
    WeatherCondition,
    GrowthStage,
    MicronutrientType,
    FieldCondition
)


class TimingService:
    """
    Service class for determining optimal timing for micronutrient applications.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = logging.getLogger(__name__)

    async def get_optimal_timing(self, request: TimingRecommendationRequest) -> TimingRecommendation:
        """
        Determine the optimal timing for micronutrient application.
        
        Args:
            request: TimingRecommendationRequest containing crop type, growth stage,
                    nutrient uptake pattern, weather, nutrient type, application method,
                    and field conditions
            
        Returns:
            TimingRecommendation with the recommended timing and details
        """
        try:
            # Determine the best timing type
            recommended_timing = self._determine_timing_type(request)
            
            # Calculate optimal application window
            optimal_window_start, optimal_window_end = self._calculate_optimal_window(
                request, recommended_timing
            )
            
            # Generate reason for the timing recommendation
            reason = self._generate_reason(recommended_timing, request)
            
            # Get weather considerations
            weather_considerations = self._get_weather_considerations(request)
            
            # Get compatibility notes
            compatibility_notes = self._get_compatibility_notes(request)
            
            # Calculate expected efficacy
            expected_efficacy = self._calculate_expected_efficacy(request)
            
            recommendation = TimingRecommendation(
                timing=recommended_timing,
                optimal_window_start=optimal_window_start,
                optimal_window_end=optimal_window_end,
                reason=reason,
                weather_considerations=weather_considerations,
                compatibility_notes=compatibility_notes,
                expected_efficacy=expected_efficacy
            )
            
            self.logger.info(f"Generated timing recommendation: {recommended_timing}")
            return recommendation
            
        except Exception as e:
            self.logger.error(f"Error generating timing recommendation: {str(e)}")
            raise

    def _determine_timing_type(self, request: TimingRecommendationRequest) -> TimingRecommendationType:
        """
        Determine the optimal timing type based on input factors.
        """
        # Primary factor: growth stage and nutrient uptake pattern
        growth_stage = request.growth_stage.lower() if request.growth_stage else ""
        
        # Critical growth stages need immediate or short-term timing
        critical_stages = ["critical uptake", "critical", "floring", "flowering", "fruiting", 
                          "grain filling", "tasseling", "silking"]
        if any(stage in growth_stage for stage in critical_stages):
            return TimingRecommendationType.SHORT_TERM
            
        # High demand periods
        high_demand_stages = ["vegetative", "vegetative growth", "early reproductive"]
        if any(stage in growth_stage for stage in high_demand_stages):
            return TimingRecommendationType.SHORT_TERM
            
        # Early season - can plan ahead
        early_stages = ["seedling", "germination", "emergence", "early season"]
        if any(stage in growth_stage for stage in early_stages):
            return TimingRecommendationType.MEDIUM_TERM
            
        # Late season - seasonal planning
        late_stages = ["maturity", "harvest", "post harvest"]
        if any(stage in growth_stage for stage in late_stages):
            return TimingRecommendationType.SEASONAL
            
        # If nutrient deficiency is critical
        critical_nutrients = ["IRON", "ZINC", "MANGANESE", "BORON"]
        if request.nutrient_type in critical_nutrients and "critical" in request.nutrient_uptake_pattern.lower():
            return TimingRecommendationType.IMMEDIATE
            
        # Default based on application method
        if request.application_method in [ApplicationMethod.FOLIAR_APPLICATION, ApplicationMethod.FERTIGATION]:
            # These methods can be more responsive to immediate needs
            return TimingRecommendationType.SHORT_TERM
        elif request.application_method in [ApplicationMethod.SEED_TREATMENT]:
            # Seed treatment timing is more constrained
            return TimingRecommendationType.MEDIUM_TERM
        else:
            # For soil applications, can plan ahead more
            return TimingRecommendationType.LONG_TERM

    def _calculate_optimal_window(self, request: TimingRecommendationRequest, timing_type: TimingRecommendationType) -> tuple:
        """
        Calculate the optimal time window for application.
        """
        current_date = datetime.now()
        
        # Define time windows based on timing type
        time_windows = {
            TimingRecommendationType.IMMEDIATE: (current_date, current_date + timedelta(hours=24)),
            TimingRecommendationType.SHORT_TERM: (current_date, current_date + timedelta(days=14)),
            TimingRecommendationType.MEDIUM_TERM: (current_date + timedelta(days=7), current_date + timedelta(days=28)),
            TimingRecommendationType.LONG_TERM: (current_date + timedelta(days=14), current_date + timedelta(days=60)),
            TimingRecommendationType.SEASONAL: (current_date + timedelta(days=30), current_date + timedelta(days=180))
        }
        
        return time_windows.get(timing_type, (current_date, current_date + timedelta(days=7)))

    def _generate_reason(self, timing_type: TimingRecommendationType, request: TimingRecommendationRequest) -> str:
        """
        Generate a human-readable reason for the timing recommendation.
        """
        reasons = []
        
        # Reason based on growth stage
        if request.growth_stage:
            reasons.append(f"crop in {request.growth_stage} growth stage")
            
        # Reason based on nutrient uptake pattern
        reasons.append(f"based on {request.nutrient_uptake_pattern} nutrient uptake pattern")
        
        # Reason based on weather conditions
        reasons.append(f"considering {request.weather_conditions.value} weather conditions")
        
        # Reason based on application method
        reasons.append(f"with {request.application_method.value} application method")
        
        # Reason based on nutrient type
        reasons.append(f"for {request.nutrient_type.value} nutrient")
        
        return f"{timing_type.value} timing recommended because: {', '.join(reasons)}."

    def _get_weather_considerations(self, request: TimingRecommendationRequest) -> List[str]:
        """
        Get weather-related considerations for timing.
        """
        considerations = []
        
        # Weather considerations based on application method
        if request.application_method == ApplicationMethod.FOLIAR_APPLICATION:
            if request.weather_conditions == WeatherCondition.RAIN:
                considerations.append("Avoid rainy conditions as foliar spray will be washed off")
            elif request.weather_conditions == WeatherCondition.WINDY:
                considerations.append("Avoid windy conditions to prevent drift during foliar application")
            elif request.weather_conditions == WeatherCondition.HOT:
                considerations.append("Avoid applying during hot conditions to prevent leaf burn")
            
        elif request.application_method == ApplicationMethod.FERTIGATION:
            if request.weather_conditions == WeatherCondition.CLEAR:
                considerations.append("Clear weather is ideal for fertigation as nutrients will be efficiently delivered")
            elif request.weather_conditions == WeatherCondition.RAIN:
                considerations.append("Rain may dilute nutrients or cause runoff during fertigation")
                
        elif request.application_method == ApplicationMethod.SOIL_APPLICATION:
            if request.field_conditions.moisture in ["dry", "very dry"]:
                considerations.append("Dry soil conditions may reduce nutrient availability; irrigation after application would be beneficial")
            elif request.field_conditions.moisture == "saturated":
                considerations.append("Wet conditions may lead to nutrient runoff, wait for field to dry")
                
        # General weather considerations
        if request.weather_conditions == WeatherCondition.RAIN:
            considerations.append("Rain within 24 hours may wash away nutrients, consider timing accordingly")
        elif request.weather_conditions == WeatherCondition.WINDY:
            considerations.append("High wind conditions can cause drift, avoid application during windy periods")
            
        return considerations

    def _get_compatibility_notes(self, request: TimingRecommendationRequest) -> List[str]:
        """
        Get notes about compatibility with other inputs.
        """
        notes = []
        
        # Compatibility with other pesticides/herbicides
        if request.application_method in [ApplicationMethod.FOLIAR_APPLICATION]:
            notes.append("Check compatibility with other foliar products to avoid phytotoxicity")
            notes.append("Consider tank mixing compatibility if applying with other products")
            
        # Compatibility with growth stage
        if request.growth_stage and "flowering" in request.growth_stage.lower():
            notes.append("Avoid application during peak flowering to protect pollinators")
            
        # Compatibility with nutrient interactions
        if request.nutrient_type in [MicronutrientType.IRON, MicronutrientType.ZINC, MicronutrientType.COPPER, MicronutrientType.MANGANESE]:
            notes.append("Avoid applying with phosphorus as it can form insoluble complexes")
            notes.append("These micronutrients can interact with each other, consider separate applications")
            
        # Seasonal compatibility
        if request.growth_stage and "harvest" in request.growth_stage.lower():
            notes.append("Consider pre-harvest interval requirements before harvest")
            
        return notes

    def _calculate_expected_efficacy(self, request: TimingRecommendationRequest) -> float:
        """
        Calculate the expected efficacy of the application at this timing.
        """
        base_efficacy = 0.7  # Base efficacy
        
        # Adjust for growth stage
        growth_stage = request.growth_stage.lower() if request.growth_stage else ""
        if any(stage in growth_stage for stage in ["critical uptake", "critical", "floring", "flowering"]):
            base_efficacy += 0.15  # Higher efficacy during critical periods
            
        # Adjust for weather conditions
        if request.weather_conditions == WeatherCondition.CLEAR:
            base_efficacy += 0.1  # Optimal weather
        elif request.weather_conditions in [WeatherCondition.RAIN, WeatherCondition.WINDY]:
            base_efficacy -= 0.15  # Reduced efficacy due to weather
            
        # Adjust for application method
        if request.application_method == ApplicationMethod.FOLIAR_APPLICATION and request.nutrient_type in ["IRON", "MANGANESE", "ZINC"]:
            base_efficacy += 0.1  # Foliar is more efficient for these nutrients
            
        # Adjust for field conditions
        if request.field_conditions.moisture in ["adequate", "good"]:
            base_efficacy += 0.05
        elif request.field_conditions.moisture in ["dry", "saturated"]:
            base_efficacy -= 0.1
            
        # Ensure efficacy is between 0 and 1
        return max(0.0, min(1.0, base_efficacy))

    async def get_seasonal_timing_recommendations(self, crop_type: str, nutrient_type: MicronutrientType) -> List[Dict[str, Any]]:
        """
        Get seasonal timing recommendations for specific crop and nutrient combinations.
        """
        # Define seasonal timing patterns based on crop and nutrient type
        seasonal_recommendations = []
        
        # Example seasonal patterns for corn
        if crop_type.lower() == "corn":
            if nutrient_type in [MicronutrientType.ZINC, MicronutrientType.MANGANESE]:
                seasonal_recommendations.extend([
                    {
                        "timing": "Pre-planting",
                        "application_method": ApplicationMethod.SOIL_APPLICATION,
                        "growth_stage": "Pre-emergence",
                        "reason": "Soil application before planting for maximum availability during early growth"
                    },
                    {
                        "timing": "V4-V6 growth stage",
                        "application_method": ApplicationMethod.FOLIAR_APPLICATION,
                        "growth_stage": "Vegetative (V4-V6)",
                        "reason": "Critical uptake period for zinc and manganese in corn"
                    },
                    {
                        "timing": "V8-V12 growth stage",
                        "application_method": ApplicationMethod.FERTIGATION,
                        "growth_stage": "Vegetative (V8-V12)",
                        "reason": "Supporting rapid growth period with continuous nutrient supply"
                    }
                ])
            elif nutrient_type == MicronutrientType.BORON:
                seasonal_recommendations.extend([
                    {
                        "timing": "Tasseling stage",
                        "application_method": ApplicationMethod.FOLIAR_APPLICATION,
                        "growth_stage": "Tasseling/Silking",
                        "reason": "Critical for pollination and kernel development in corn"
                    }
                ])
        
        # Example seasonal patterns for soybeans
        elif crop_type.lower() == "soybean" or crop_type.lower() == "soy beans":
            if nutrient_type == MicronutrientType.MANGANESE:
                seasonal_recommendations.extend([
                    {
                        "timing": "VE-V2 growth stage",
                        "application_method": ApplicationMethod.FOLIAR_APPLICATION,
                        "growth_stage": "Early Vegetative (VE-V2)",
                        "reason": "Critical for chlorophyll production and photosynthesis in soybeans"
                    },
                    {
                        "timing": "R1-R2 growth stage",
                        "application_method": ApplicationMethod.FOLIAR_APPLICATION,
                        "growth_stage": "Beginning Bloom (R1-R2)",
                        "reason": "Supporting reproductive growth period"
                    }
                ])
            elif nutrient_type == MicronutrientType.IRON:
                seasonal_recommendations.extend([
                    {
                        "timing": "VE-V1 growth stage",
                        "application_method": ApplicationMethod.FOLIAR_APPLICATION,
                        "growth_stage": "Early Vegetative (VE-V1)",
                        "reason": "Preventing chlorosis during early growth when iron availability is limited"
                    }
                ])
        
        return seasonal_recommendations
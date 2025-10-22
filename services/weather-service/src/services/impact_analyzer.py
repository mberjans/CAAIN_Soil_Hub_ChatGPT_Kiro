#!/usr/bin/env python3
"""
Weather Impact Analyzer
Weather Impact Analysis Service
Version: 1.0
Date: October 2025
"""

from typing import Dict, Any, Optional
from src.schemas.weather_schemas import WeatherData


class WeatherImpactAnalyzer:
    """Analyze weather data for agricultural impact."""
    
    def __init__(self):
        """Initialize the weather impact analyzer."""
        # Define crop-specific thresholds
        self.crop_thresholds = {
            "corn": {
                "min_temp": 10,  # Minimum planting temperature (C)
                "max_temp": 35,  # Maximum planting temperature (C)
                "opt_temp_min": 15,  # Optimal planting temperature range (C)
                "opt_temp_max": 25,
                "max_wind": 30,  # Maximum wind speed for planting (km/h)
                "max_precip": 5.0,  # Maximum precipitation for planting (mm)
                "min_humidity": 40,  # Minimum humidity for planting (%)
                "max_humidity": 80,  # Maximum humidity for planting (%)
            },
            "soybean": {
                "min_temp": 13,
                "max_temp": 35,
                "opt_temp_min": 18,
                "opt_temp_max": 28,
                "max_wind": 25,
                "max_precip": 3.0,
                "min_humidity": 45,
                "max_humidity": 75,
            },
            "wheat": {
                "min_temp": 4,
                "max_temp": 25,
                "opt_temp_min": 10,
                "opt_temp_max": 20,
                "max_wind": 20,
                "max_precip": 2.0,
                "min_humidity": 50,
                "max_humidity": 85,
            }
        }
    
    def analyze_planting_conditions(self, weather_data: WeatherData, crop_type: str) -> Dict[str, Any]:
        """Analyze weather conditions for planting suitability.
        
        Args:
            weather_data: Weather data to analyze
            crop_type: Type of crop (corn, soybean, wheat)
            
        Returns:
            Dictionary with planting suitability analysis
        """
        if crop_type not in self.crop_thresholds:
            raise ValueError(f"Unsupported crop type: {crop_type}")
        
        thresholds = self.crop_thresholds[crop_type]
        factors = {}
        suitable = True
        
        # Temperature analysis
        if weather_data.temperature_c is not None:
            temp_suitable = (
                thresholds["min_temp"] <= weather_data.temperature_c <= thresholds["max_temp"]
            )
            factors["temperature"] = {
                "value": weather_data.temperature_c,
                "suitable": temp_suitable,
                "optimal_range": f"{thresholds['opt_temp_min']}-{thresholds['opt_temp_max']}°C"
            }
            if not temp_suitable:
                suitable = False
        
        # Wind analysis
        if weather_data.wind_speed_kmh is not None:
            wind_suitable = weather_data.wind_speed_kmh <= thresholds["max_wind"]
            factors["wind"] = {
                "value": weather_data.wind_speed_kmh,
                "suitable": wind_suitable,
                "max_allowed": f"{thresholds['max_wind']} km/h"
            }
            if not wind_suitable:
                suitable = False
        
        # Precipitation analysis
        if weather_data.precipitation_mm is not None:
            precip_suitable = weather_data.precipitation_mm <= thresholds["max_precip"]
            factors["precipitation"] = {
                "value": weather_data.precipitation_mm,
                "suitable": precip_suitable,
                "max_allowed": f"{thresholds['max_precip']} mm"
            }
            if not precip_suitable:
                suitable = False
        
        # Humidity analysis
        if weather_data.humidity_percent is not None:
            humidity_suitable = (
                thresholds["min_humidity"] <= weather_data.humidity_percent <= thresholds["max_humidity"]
            )
            factors["humidity"] = {
                "value": weather_data.humidity_percent,
                "suitable": humidity_suitable,
                "optimal_range": f"{thresholds['min_humidity']}-{thresholds['max_humidity']}%"
            }
            if not humidity_suitable:
                suitable = False
        
        # Overall suitability
        suitability = "GOOD" if suitable else "POOR"
        if suitable and all(f.get("suitable", True) for f in factors.values()):
            suitability = "EXCELLENT"
        elif not suitable and sum(1 for f in factors.values() if not f.get("suitable", True)) > 2:
            suitability = "VERY_POOR"
        
        return {
            "crop_type": crop_type,
            "suitability": suitability,
            "factors": factors,
            "recommendation": self._generate_recommendation(suitability, factors, crop_type)
        }
    
    def estimate_soil_temperature(self, weather_data: WeatherData, 
                                depth_cm: int = 10, 
                                hours_since_rain: Optional[float] = None) -> float:
        """Estimate soil temperature based on air temperature and other factors.
        
        Args:
            weather_data: Weather data to use for estimation
            depth_cm: Soil depth in centimeters (default: 10cm)
            hours_since_rain: Hours since last rainfall (optional)
            
        Returns:
            Estimated soil temperature in Celsius
        """
        if weather_data.temperature_c is None:
            raise ValueError("Air temperature is required to estimate soil temperature")
        
        # Simple estimation model
        # Soil temperature is typically 2-5°C cooler than air temperature
        # at 10cm depth, adjusted for other factors
        base_difference = 3.0  # Base difference between air and soil temp
        
        # Adjust for depth (deeper soil changes less)
        depth_factor = max(0.5, min(1.0, depth_cm / 10.0))
        
        # Adjust for recent rainfall (wet soil is cooler)
        rain_factor = 0.0
        if hours_since_rain is not None and hours_since_rain < 24:
            rain_factor = min(2.0, 24.0 / max(1.0, hours_since_rain))
        
        # Adjust for solar radiation if available
        solar_factor = 0.0
        if weather_data.solar_radiation is not None:
            # More solar radiation means warmer soil (up to a point)
            solar_factor = min(1.0, weather_data.solar_radiation / 500.0)
        
        estimated_temp = (
            weather_data.temperature_c - 
            (base_difference * depth_factor) - 
            rain_factor + 
            (solar_factor * 0.5)
        )
        
        return round(estimated_temp, 1)
    
    def _generate_recommendation(self, suitability: str, factors: Dict[str, Any], crop_type: str) -> str:
        """Generate planting recommendation based on suitability analysis.
        
        Args:
            suitability: Overall suitability rating
            factors: Individual factor analysis
            crop_type: Type of crop
            
        Returns:
            Recommendation string
        """
        if suitability == "EXCELLENT":
            return f"Excellent conditions for {crop_type} planting. Proceed with planting operations."
        elif suitability == "GOOD":
            return f"Good conditions for {crop_type} planting. Minor concerns noted."
        elif suitability == "POOR":
            poor_factors = [k for k, v in factors.items() if not v.get("suitable", True)]
            return f"Poor conditions for {crop_type} planting due to: {', '.join(poor_factors)}. Consider delaying planting."
        else:  # VERY_POOR
            poor_factors = [k for k, v in factors.items() if not v.get("suitable", True)]
            return f"Very poor conditions for {crop_type} planting due to: {', '.join(poor_factors)}. Strongly recommend delaying planting."
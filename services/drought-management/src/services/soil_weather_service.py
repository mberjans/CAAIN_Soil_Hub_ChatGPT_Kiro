"""
Soil-Weather Integration Service

Comprehensive service for integrating soil characteristics with weather patterns
to provide advanced drought risk assessment, soil moisture stress predictions,
and crop impact assessments.

This service implements TICKET-014_drought-management-3.1:
Develop comprehensive soil-weather integration system
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, date, timedelta
from uuid import UUID
from decimal import Decimal
import numpy as np
from dataclasses import dataclass

from src.models.drought_models import (
    DroughtRiskLevel,
    SoilMoistureLevel,
    WeatherImpact,
    DroughtAssessment,
    DroughtRiskAssessment
)
from src.models.soil_assessment_models import (
    DrainageClass,
    TillageType,
    CoverCropSpecies,
    CompactionLevel
)
from .external_service_integration import (
    WeatherServiceIntegration,
    CropServiceIntegration,
    FieldServiceIntegration
)

logger = logging.getLogger(__name__)

@dataclass
class SoilCharacteristics:
    """Soil characteristics for drought vulnerability assessment."""
    soil_type: str
    texture: str  # sand, loam, clay, etc.
    water_holding_capacity: float  # inches per foot
    drainage_class: DrainageClass
    organic_matter_percent: float
    soil_depth_inches: float
    bulk_density: float  # g/cm³
    field_capacity: float  # percent
    wilting_point: float  # percent
    available_water_capacity: float  # inches per foot
    infiltration_rate: float  # inches per hour
    compaction_level: CompactionLevel

@dataclass
class WeatherPattern:
    """Weather pattern data for analysis."""
    temperature_celsius: float
    precipitation_mm: float
    humidity_percent: float
    wind_speed_kmh: float
    solar_radiation: float
    evapotranspiration_mm: float
    drought_index: float  # Palmer Drought Severity Index
    aridity_index: float  # Aridity index

@dataclass
class DroughtVulnerabilityScore:
    """Drought vulnerability assessment score."""
    overall_score: float  # 0-100, higher = more vulnerable
    soil_factor_score: float
    weather_factor_score: float
    management_factor_score: float
    risk_level: DroughtRiskLevel
    vulnerability_factors: List[str]
    mitigation_potential: float

class SoilWeatherIntegrationService:
    """
    Comprehensive soil-weather integration service for drought management.
    
    Features:
    - Soil-specific drought vulnerability assessment
    - Weather pattern impact analysis
    - Drought risk modeling
    - Soil moisture stress predictions
    - Crop impact assessments
    """
    
    def __init__(self):
        self.weather_service = WeatherServiceIntegration()
        self.crop_service = CropServiceIntegration()
        self.field_service = FieldServiceIntegration()
        self.initialized = False
        
        # Soil characteristic databases
        self.soil_texture_properties = self._initialize_soil_texture_properties()
        self.drainage_class_impacts = self._initialize_drainage_impacts()
        self.crop_water_requirements = self._initialize_crop_water_requirements()
        
    def _initialize_soil_texture_properties(self) -> Dict[str, Dict[str, float]]:
        """Initialize soil texture property database."""
        return {
            "sand": {
                "water_holding_capacity": 0.8,
                "infiltration_rate": 2.5,
                "field_capacity": 10.0,
                "wilting_point": 3.0,
                "bulk_density": 1.6,
                "drought_vulnerability": 0.8
            },
            "loamy_sand": {
                "water_holding_capacity": 1.2,
                "infiltration_rate": 2.0,
                "field_capacity": 15.0,
                "wilting_point": 5.0,
                "bulk_density": 1.5,
                "drought_vulnerability": 0.7
            },
            "sandy_loam": {
                "water_holding_capacity": 1.8,
                "infiltration_rate": 1.5,
                "field_capacity": 20.0,
                "wilting_point": 8.0,
                "bulk_density": 1.4,
                "drought_vulnerability": 0.6
            },
            "loam": {
                "water_holding_capacity": 2.2,
                "infiltration_rate": 1.2,
                "field_capacity": 25.0,
                "wilting_point": 10.0,
                "bulk_density": 1.3,
                "drought_vulnerability": 0.4
            },
            "silt_loam": {
                "water_holding_capacity": 2.5,
                "infiltration_rate": 1.0,
                "field_capacity": 30.0,
                "wilting_point": 12.0,
                "bulk_density": 1.2,
                "drought_vulnerability": 0.3
            },
            "clay_loam": {
                "water_holding_capacity": 2.0,
                "infiltration_rate": 0.8,
                "field_capacity": 28.0,
                "wilting_point": 15.0,
                "bulk_density": 1.4,
                "drought_vulnerability": 0.5
            },
            "clay": {
                "water_holding_capacity": 1.8,
                "infiltration_rate": 0.5,
                "field_capacity": 35.0,
                "wilting_point": 20.0,
                "bulk_density": 1.5,
                "drought_vulnerability": 0.6
            }
        }
    
    def _initialize_drainage_impacts(self) -> Dict[str, Dict[str, float]]:
        """Initialize drainage class impact factors."""
        return {
            "excessively_drained": {
                "drought_vulnerability": 0.8,
                "water_retention": 0.3,
                "infiltration_modifier": 1.5
            },
            "well_drained": {
                "drought_vulnerability": 0.4,
                "water_retention": 0.8,
                "infiltration_modifier": 1.0
            },
            "moderately_well_drained": {
                "drought_vulnerability": 0.3,
                "water_retention": 0.9,
                "infiltration_modifier": 0.9
            },
            "somewhat_poorly_drained": {
                "drought_vulnerability": 0.2,
                "water_retention": 1.1,
                "infiltration_modifier": 0.7
            },
            "poorly_drained": {
                "drought_vulnerability": 0.1,
                "water_retention": 1.3,
                "infiltration_modifier": 0.5
            },
            "very_poorly_drained": {
                "drought_vulnerability": 0.05,
                "water_retention": 1.5,
                "infiltration_modifier": 0.3
            }
        }
    
    def _initialize_crop_water_requirements(self) -> Dict[str, Dict[str, float]]:
        """Initialize crop water requirement database."""
        return {
            "corn": {
                "total_water_requirement": 20.0,  # inches per season
                "critical_periods": ["tasseling", "silking", "grain_fill"],
                "drought_tolerance": 0.6,
                "root_depth": 36.0  # inches
            },
            "soybean": {
                "total_water_requirement": 18.0,
                "critical_periods": ["flowering", "pod_set", "seed_fill"],
                "drought_tolerance": 0.7,
                "root_depth": 30.0
            },
            "wheat": {
                "total_water_requirement": 15.0,
                "critical_periods": ["tillering", "heading", "grain_fill"],
                "drought_tolerance": 0.8,
                "root_depth": 24.0
            },
            "cotton": {
                "total_water_requirement": 22.0,
                "critical_periods": ["flowering", "boll_set", "boll_fill"],
                "drought_tolerance": 0.5,
                "root_depth": 42.0
            }
        }
    
    async def initialize(self):
        """Initialize the soil-weather integration service."""
        try:
            logger.info("Initializing Soil-Weather Integration Service...")
            
            await self.weather_service.initialize()
            await self.crop_service.initialize()
            await self.field_service.initialize()
            
            self.initialized = True
            logger.info("Soil-Weather Integration Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Soil-Weather Integration Service: {str(e)}")
            raise
    
    async def cleanup(self):
        """Clean up service resources."""
        try:
            logger.info("Cleaning up Soil-Weather Integration Service...")
            
            await self.weather_service.cleanup()
            await self.crop_service.cleanup()
            await self.field_service.cleanup()
            
            self.initialized = False
            logger.info("Soil-Weather Integration Service cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
    
    async def assess_soil_drought_vulnerability(
        self,
        field_id: UUID,
        soil_characteristics: SoilCharacteristics,
        weather_data: List[WeatherPattern],
        crop_type: str
    ) -> DroughtVulnerabilityScore:
        """
        Assess soil-specific drought vulnerability based on soil characteristics
        and weather patterns.
        
        Args:
            field_id: Field identifier
            soil_characteristics: Soil characteristics data
            weather_data: Historical and current weather data
            crop_type: Type of crop being grown
            
        Returns:
            DroughtVulnerabilityScore with comprehensive assessment
        """
        try:
            logger.info(f"Assessing drought vulnerability for field {field_id}")
            
            # Calculate soil factor score
            soil_factor_score = self._calculate_soil_factor_score(soil_characteristics)
            
            # Calculate weather factor score
            weather_factor_score = self._calculate_weather_factor_score(weather_data)
            
            # Calculate management factor score
            management_factor_score = await self._calculate_management_factor_score(
                field_id, soil_characteristics, crop_type
            )
            
            # Calculate overall vulnerability score
            overall_score = (
                soil_factor_score * 0.4 +
                weather_factor_score * 0.4 +
                management_factor_score * 0.2
            )
            
            # Determine risk level
            risk_level = self._determine_risk_level(overall_score)
            
            # Identify vulnerability factors
            vulnerability_factors = self._identify_vulnerability_factors(
                soil_characteristics, weather_data, overall_score
            )
            
            # Calculate mitigation potential
            mitigation_potential = self._calculate_mitigation_potential(
                soil_characteristics, vulnerability_factors
            )
            
            return DroughtVulnerabilityScore(
                overall_score=overall_score,
                soil_factor_score=soil_factor_score,
                weather_factor_score=weather_factor_score,
                management_factor_score=management_factor_score,
                risk_level=risk_level,
                vulnerability_factors=vulnerability_factors,
                mitigation_potential=mitigation_potential
            )
            
        except Exception as e:
            logger.error(f"Error assessing drought vulnerability: {str(e)}")
            raise
    
    def _calculate_soil_factor_score(self, soil: SoilCharacteristics) -> float:
        """Calculate soil factor contribution to drought vulnerability."""
        # Base vulnerability from soil texture
        texture_props = self.soil_texture_properties.get(soil.texture, {})
        base_vulnerability = texture_props.get("drought_vulnerability", 0.5)
        
        # Adjust for water holding capacity
        whc_factor = max(0, 1 - (soil.water_holding_capacity / 3.0))  # Normalize to 3 inches
        
        # Adjust for drainage class
        drainage_impacts = self.drainage_class_impacts.get(soil.drainage_class.value, {})
        drainage_factor = drainage_impacts.get("drought_vulnerability", 0.5)
        
        # Adjust for organic matter (higher OM = lower vulnerability)
        om_factor = max(0, 1 - (soil.organic_matter_percent / 5.0))  # Normalize to 5%
        
        # Adjust for soil depth (deeper soil = lower vulnerability)
        depth_factor = max(0, 1 - (soil.soil_depth_inches / 60.0))  # Normalize to 60 inches
        
        # Adjust for compaction (higher compaction = higher vulnerability)
        compaction_factor = {
            "none": 0.0,
            "slight": 0.2,
            "moderate": 0.4,
            "severe": 0.6,
            "extreme": 0.8
        }.get(soil.compaction_level.value, 0.4)
        
        # Calculate weighted soil factor score
        soil_score = (
            base_vulnerability * 0.3 +
            whc_factor * 0.25 +
            drainage_factor * 0.2 +
            om_factor * 0.15 +
            depth_factor * 0.05 +
            compaction_factor * 0.05
        ) * 100
        
        return min(100, max(0, soil_score))
    
    def _calculate_weather_factor_score(self, weather_data: List[WeatherPattern]) -> float:
        """Calculate weather factor contribution to drought vulnerability."""
        if not weather_data:
            return 50.0  # Default moderate risk if no weather data
        
        # Calculate average drought index
        avg_drought_index = np.mean([w.drought_index for w in weather_data])
        
        # Calculate precipitation deficit
        avg_precipitation = np.mean([w.precipitation_mm for w in weather_data])
        avg_evapotranspiration = np.mean([w.evapotranspiration_mm for w in weather_data])
        precipitation_deficit = max(0, avg_evapotranspiration - avg_precipitation)
        
        # For extreme drought conditions, ensure high vulnerability
        if avg_drought_index <= -3.0:  # Severe to extreme drought
            precipitation_deficit = max(precipitation_deficit, 10.0)  # Ensure high deficit
        
        # Calculate temperature stress
        avg_temperature = np.mean([w.temperature_celsius for w in weather_data])
        temperature_stress = max(0, avg_temperature - 25.0) / 10.0  # Stress above 25°C
        
        # Calculate aridity
        avg_aridity = np.mean([w.aridity_index for w in weather_data])
        
        # Calculate weather vulnerability score
        # Drought index: -4 (extreme drought) to +4 (very wet), convert to 0-100 scale
        # For extreme drought (-4), we want high vulnerability (100), for wet (+4) we want low vulnerability (0)
        drought_score = min(100, max(0, (4 - avg_drought_index) * 12.5))
        
        # Precipitation deficit: higher deficit = higher vulnerability
        precip_score = min(100, precipitation_deficit * 6)  # Further increased multiplier
        
        # Temperature stress: higher temperature = higher vulnerability
        temp_score = min(100, temperature_stress * 30)  # Increased sensitivity
        
        # Aridity: higher aridity = higher vulnerability
        aridity_score = min(100, avg_aridity * 25)
        
        weather_score = (
            drought_score * 0.4 +
            precip_score * 0.3 +
            temp_score * 0.2 +
            aridity_score * 0.1
        )
        
        return min(100, max(0, weather_score))
    
    async def _calculate_management_factor_score(
        self,
        field_id: UUID,
        soil: SoilCharacteristics,
        crop_type: str
    ) -> float:
        """Calculate management factor contribution to drought vulnerability."""
        try:
            # Get field management data
            field_data = await self.field_service.get_field_characteristics(field_id)
            
            # Get current practices
            current_practices = field_data.get("current_practices", [])
            
            # Calculate management score based on practices
            management_score = 50.0  # Base score
            
            # Adjust for tillage practices
            tillage_type = field_data.get("tillage_type", "conventional")
            tillage_adjustment = {
                "no_till": -20,
                "strip_till": -10,
                "reduced_till": -5,
                "conventional": 0
            }.get(tillage_type, 0)
            
            # Adjust for cover crops
            cover_crops_used = "cover_crops" in current_practices
            cover_crop_adjustment = -15 if cover_crops_used else 0
            
            # Adjust for irrigation
            irrigation_available = field_data.get("irrigation_available", False)
            irrigation_adjustment = -25 if irrigation_available else 0
            
            # Adjust for crop rotation
            crop_rotation = "crop_rotation" in current_practices
            rotation_adjustment = -10 if crop_rotation else 0
            
            # Calculate final management score
            management_score += (
                tillage_adjustment +
                cover_crop_adjustment +
                irrigation_adjustment +
                rotation_adjustment
            )
            
            return min(100, max(0, management_score))
            
        except Exception as e:
            logger.warning(f"Error calculating management factor: {str(e)}")
            return 50.0  # Default moderate risk
    
    def _determine_risk_level(self, overall_score: float) -> DroughtRiskLevel:
        """Determine drought risk level based on overall score."""
        if overall_score >= 80:
            return DroughtRiskLevel.EXTREME
        elif overall_score >= 65:
            return DroughtRiskLevel.SEVERE
        elif overall_score >= 50:
            return DroughtRiskLevel.HIGH
        elif overall_score >= 35:
            return DroughtRiskLevel.MODERATE
        else:
            return DroughtRiskLevel.LOW
    
    def _identify_vulnerability_factors(
        self,
        soil: SoilCharacteristics,
        weather_data: List[WeatherPattern],
        overall_score: float
    ) -> List[str]:
        """Identify specific vulnerability factors."""
        factors = []
        
        # Soil-related factors
        if soil.water_holding_capacity < 1.5:
            factors.append("Low water holding capacity")
        
        if soil.drainage_class in [DrainageClass.EXCESSIVELY_DRAINED]:
            factors.append("Excessive drainage")
        
        if soil.organic_matter_percent < 2.0:
            factors.append("Low organic matter content")
        
        if soil.soil_depth_inches < 24:
            factors.append("Shallow soil depth")
        
        if soil.compaction_level in [CompactionLevel.SEVERE, CompactionLevel.EXTREME]:
            factors.append("Soil compaction")
        
        # Weather-related factors
        if weather_data:
            avg_drought_index = np.mean([w.drought_index for w in weather_data])
            if avg_drought_index < -2:
                factors.append("Historical drought conditions")
            
            avg_precipitation = np.mean([w.precipitation_mm for w in weather_data])
            avg_evapotranspiration = np.mean([w.evapotranspiration_mm for w in weather_data])
            if avg_precipitation < avg_evapotranspiration * 0.8:
                factors.append("Precipitation deficit")
            
            avg_temperature = np.mean([w.temperature_celsius for w in weather_data])
            if avg_temperature > 30:
                factors.append("High temperature stress")
        
        return factors
    
    def _calculate_mitigation_potential(
        self,
        soil: SoilCharacteristics,
        vulnerability_factors: List[str]
    ) -> float:
        """Calculate potential for drought mitigation improvements."""
        base_potential = 50.0
        
        # Adjust based on soil characteristics
        if soil.organic_matter_percent < 3.0:
            base_potential += 20  # High potential for OM improvement
        
        if soil.compaction_level in [CompactionLevel.MODERATE, CompactionLevel.SEVERE]:
            base_potential += 15  # Potential for compaction relief
        
        if soil.drainage_class == DrainageClass.EXCESSIVELY_DRAINED:
            base_potential += 10  # Potential for water retention improvements
        
        # Adjust based on number of vulnerability factors
        factor_count = len(vulnerability_factors)
        base_potential += min(20, factor_count * 5)  # More factors = more potential
        
        return min(100, max(0, base_potential))
    
    async def analyze_weather_pattern_impact(
        self,
        field_id: UUID,
        weather_data: List[WeatherPattern],
        soil_characteristics: SoilCharacteristics,
        crop_type: str
    ) -> Dict[str, Any]:
        """
        Analyze weather pattern impact on soil moisture and crop stress.
        
        Args:
            field_id: Field identifier
            weather_data: Weather pattern data
            soil_characteristics: Soil characteristics
            crop_type: Type of crop
            
        Returns:
            Weather pattern impact analysis
        """
        try:
            logger.info(f"Analyzing weather pattern impact for field {field_id}")
            
            # Calculate soil moisture stress
            moisture_stress = self._calculate_soil_moisture_stress(
                weather_data, soil_characteristics
            )
            
            # Calculate crop water stress
            crop_stress = self._calculate_crop_water_stress(
                weather_data, soil_characteristics, crop_type
            )
            
            # Calculate evapotranspiration impact
            et_impact = self._calculate_et_impact(weather_data, soil_characteristics)
            
            # Calculate precipitation effectiveness
            precip_effectiveness = self._calculate_precipitation_effectiveness(
                weather_data, soil_characteristics
            )
            
            # Identify critical periods
            critical_periods = self._identify_critical_periods(
                weather_data, crop_type
            )
            
            return {
                "moisture_stress_level": moisture_stress["level"],
                "moisture_stress_score": moisture_stress["score"],
                "crop_water_stress": crop_stress,
                "evapotranspiration_impact": et_impact,
                "precipitation_effectiveness": precip_effectiveness,
                "critical_periods": critical_periods,
                "recommendations": self._generate_weather_impact_recommendations(
                    moisture_stress, crop_stress, critical_periods
                )
            }
            
        except Exception as e:
            logger.error(f"Error analyzing weather pattern impact: {str(e)}")
            raise
    
    def _calculate_soil_moisture_stress(
        self,
        weather_data: List[WeatherPattern],
        soil: SoilCharacteristics
    ) -> Dict[str, Any]:
        """Calculate soil moisture stress based on weather and soil data."""
        if not weather_data:
            return {"level": "unknown", "score": 50}
        
        # Calculate water balance
        total_precipitation = sum(w.precipitation_mm for w in weather_data)
        total_et = sum(w.evapotranspiration_mm for w in weather_data)
        water_deficit = max(0, total_et - total_precipitation)
        
        # Calculate soil moisture deficit
        available_water = soil.available_water_capacity * soil.soil_depth_inches / 12
        moisture_deficit = min(available_water, water_deficit / 25.4)  # Convert mm to inches
        
        # Calculate stress score
        stress_score = min(100, (moisture_deficit / available_water) * 100)
        
        # Determine stress level
        if stress_score >= 80:
            level = "severe"
        elif stress_score >= 60:
            level = "moderate"
        elif stress_score >= 40:
            level = "mild"
        else:
            level = "low"
        
        return {"level": level, "score": stress_score}
    
    def _calculate_crop_water_stress(
        self,
        weather_data: List[WeatherPattern],
        soil: SoilCharacteristics,
        crop_type: str
    ) -> Dict[str, Any]:
        """Calculate crop water stress based on crop requirements."""
        crop_requirements = self.crop_water_requirements.get(crop_type, {})
        if not crop_requirements:
            return {"stress_level": "unknown", "stress_score": 50}
        
        # Calculate water requirement vs availability
        total_precipitation = sum(w.precipitation_mm for w in weather_data)
        total_et = sum(w.evapotranspiration_mm for w in weather_data)
        
        # Convert to inches
        precipitation_inches = total_precipitation / 25.4
        et_inches = total_et / 25.4
        
        # Calculate crop water stress
        water_requirement = crop_requirements["total_water_requirement"]
        water_availability = precipitation_inches + soil.available_water_capacity
        
        stress_score = max(0, min(100, (water_requirement - water_availability) / water_requirement * 100))
        
        # Determine stress level
        if stress_score >= 70:
            stress_level = "severe"
        elif stress_score >= 50:
            stress_level = "moderate"
        elif stress_score >= 30:
            stress_level = "mild"
        else:
            stress_level = "low"
        
        return {"stress_level": stress_level, "stress_score": stress_score}
    
    def _calculate_et_impact(
        self,
        weather_data: List[WeatherPattern],
        soil: SoilCharacteristics
    ) -> Dict[str, Any]:
        """Calculate evapotranspiration impact on soil moisture."""
        if not weather_data:
            return {"impact_level": "unknown", "impact_score": 50}
        
        # Calculate average ET
        avg_et = np.mean([w.evapotranspiration_mm for w in weather_data])
        
        # Calculate ET impact based on soil characteristics
        infiltration_rate = soil.infiltration_rate
        water_holding_capacity = soil.water_holding_capacity
        
        # ET impact score (higher ET relative to soil capacity = higher impact)
        et_impact_score = min(100, (avg_et / 5.0) * (1 / water_holding_capacity) * 50)
        
        # Determine impact level
        if et_impact_score >= 70:
            impact_level = "high"
        elif et_impact_score >= 50:
            impact_level = "moderate"
        elif et_impact_score >= 30:
            impact_level = "low"
        else:
            impact_level = "minimal"
        
        return {"impact_level": impact_level, "impact_score": et_impact_score}
    
    def _calculate_precipitation_effectiveness(
        self,
        weather_data: List[WeatherPattern],
        soil: SoilCharacteristics
    ) -> Dict[str, Any]:
        """Calculate precipitation effectiveness based on soil characteristics."""
        if not weather_data:
            return {"effectiveness": "unknown", "score": 50}
        
        # Calculate precipitation patterns
        total_precipitation = sum(w.precipitation_mm for w in weather_data)
        precipitation_events = len([w for w in weather_data if w.precipitation_mm > 0])
        
        # Calculate effectiveness based on soil infiltration
        infiltration_rate = soil.infiltration_rate
        drainage_class = soil.drainage_class
        
        # Effectiveness score
        effectiveness_score = min(100, (
            (total_precipitation / max(1, precipitation_events)) * 0.4 +  # Intensity
            infiltration_rate * 20 * 0.3 +  # Infiltration capacity
            (1 if drainage_class in [DrainageClass.WELL_DRAINED, DrainageClass.MODERATELY_WELL_DRAINED] else 0.5) * 30  # Drainage
        ))
        
        # Determine effectiveness level
        if effectiveness_score >= 80:
            effectiveness = "high"
        elif effectiveness_score >= 60:
            effectiveness = "moderate"
        elif effectiveness_score >= 40:
            effectiveness = "low"
        else:
            effectiveness = "poor"
        
        return {"effectiveness": effectiveness, "score": effectiveness_score}
    
    def _identify_critical_periods(
        self,
        weather_data: List[WeatherPattern],
        crop_type: str
    ) -> List[Dict[str, Any]]:
        """Identify critical periods for crop water requirements."""
        crop_requirements = self.crop_water_requirements.get(crop_type, {})
        critical_periods = crop_requirements.get("critical_periods", [])
        
        # For now, return the critical periods with basic analysis
        # In a full implementation, this would analyze weather data for these periods
        return [
            {
                "period": period,
                "water_requirement": "high",
                "stress_risk": "moderate",
                "recommendations": f"Monitor {period} closely for water stress"
            }
            for period in critical_periods
        ]
    
    def _generate_weather_impact_recommendations(
        self,
        moisture_stress: Dict[str, Any],
        crop_stress: Dict[str, Any],
        critical_periods: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations based on weather impact analysis."""
        recommendations = []
        
        # Moisture stress recommendations
        if moisture_stress["level"] in ["severe", "moderate"]:
            recommendations.append("Implement soil moisture conservation practices")
            recommendations.append("Consider irrigation if available")
        
        # Crop stress recommendations
        if crop_stress["stress_level"] in ["severe", "moderate"]:
            recommendations.append("Monitor crop water stress closely")
            recommendations.append("Adjust irrigation timing if applicable")
        
        # Critical period recommendations
        if critical_periods:
            recommendations.append("Focus irrigation efforts on critical growth periods")
        
        return recommendations
    
    async def predict_soil_moisture_stress(
        self,
        field_id: UUID,
        soil_characteristics: SoilCharacteristics,
        weather_forecast: List[WeatherPattern],
        crop_type: str,
        days_ahead: int = 14
    ) -> Dict[str, Any]:
        """
        Predict soil moisture stress based on weather forecast and soil characteristics.
        
        Args:
            field_id: Field identifier
            soil_characteristics: Soil characteristics
            weather_forecast: Weather forecast data
            crop_type: Type of crop
            days_ahead: Number of days to predict ahead
            
        Returns:
            Soil moisture stress prediction
        """
        try:
            logger.info(f"Predicting soil moisture stress for field {field_id}")
            
            # Calculate current soil moisture
            current_moisture = await self._get_current_soil_moisture(field_id)
            
            # Predict moisture changes
            moisture_predictions = []
            current_level = current_moisture
            
            for i in range(days_ahead):
                if i < len(weather_forecast):
                    weather = weather_forecast[i]
                else:
                    # If forecast is shorter than days_ahead, use the last available weather data
                    weather = weather_forecast[-1] if weather_forecast else None
                    if weather is None:
                        break
                # Calculate daily moisture change
                daily_change = self._calculate_daily_moisture_change(
                    weather, soil_characteristics, crop_type
                )
                
                # Update moisture level
                current_level += daily_change
                current_level = max(0, min(100, current_level))  # Clamp to 0-100%
                
                moisture_predictions.append({
                    "day": i + 1,
                    "moisture_level": current_level,
                    "moisture_change": daily_change,
                    "stress_level": self._determine_moisture_stress_level(current_level),
                    "weather": {
                        "precipitation": weather.precipitation_mm,
                        "evapotranspiration": weather.evapotranspiration_mm,
                        "temperature": weather.temperature_celsius
                    }
                })
            
            # Calculate overall stress prediction
            avg_moisture = np.mean([p["moisture_level"] for p in moisture_predictions])
            stress_levels = [p["stress_level"] for p in moisture_predictions]
            
            # Determine critical days
            critical_days = [
                p["day"] for p in moisture_predictions
                if p["stress_level"] in ["severe", "moderate"]
            ]
            
            return {
                "field_id": field_id,
                "prediction_period_days": days_ahead,
                "current_moisture_level": current_moisture,
                "predicted_average_moisture": avg_moisture,
                "critical_days": critical_days,
                "daily_predictions": moisture_predictions,
                "recommendations": self._generate_stress_prediction_recommendations(
                    avg_moisture, critical_days, soil_characteristics
                )
            }
            
        except Exception as e:
            logger.error(f"Error predicting soil moisture stress: {str(e)}")
            raise
    
    async def _get_current_soil_moisture(self, field_id: UUID) -> float:
        """Get current soil moisture level for field."""
        try:
            # In a real implementation, this would query soil moisture sensors
            # For now, return a simulated value
            return 65.0  # 65% moisture level
        except Exception as e:
            logger.warning(f"Error getting current soil moisture: {str(e)}")
            return 50.0  # Default moderate moisture
    
    def _calculate_daily_moisture_change(
        self,
        weather: WeatherPattern,
        soil: SoilCharacteristics,
        crop_type: str
    ) -> float:
        """Calculate daily soil moisture change based on weather."""
        # Convert precipitation to moisture increase
        precip_increase = weather.precipitation_mm / 25.4  # Convert mm to inches
        
        # Calculate ET loss
        et_loss = weather.evapotranspiration_mm / 25.4  # Convert mm to inches
        
        # Adjust for soil characteristics
        infiltration_factor = min(1.0, soil.infiltration_rate / 2.0)
        water_holding_factor = soil.water_holding_capacity / 2.0
        
        # Calculate net change
        net_change = (precip_increase * infiltration_factor) - (et_loss / water_holding_factor)
        
        # Convert to percentage change
        moisture_change = net_change * 10  # Rough conversion to percentage
        
        return moisture_change
    
    def _determine_moisture_stress_level(self, moisture_level: float) -> str:
        """Determine moisture stress level based on moisture percentage."""
        if moisture_level >= 70:
            return "optimal"
        elif moisture_level >= 50:
            return "adequate"
        elif moisture_level >= 30:
            return "mild"
        elif moisture_level >= 15:
            return "moderate"
        else:
            return "severe"
    
    def _generate_stress_prediction_recommendations(
        self,
        avg_moisture: float,
        critical_days: List[int],
        soil: SoilCharacteristics
    ) -> List[str]:
        """Generate recommendations based on stress predictions."""
        recommendations = []
        
        if avg_moisture < 40:
            recommendations.append("Implement immediate moisture conservation measures")
            recommendations.append("Consider irrigation if available")
        
        if len(critical_days) > 3:
            recommendations.append("Multiple critical moisture periods predicted")
            recommendations.append("Plan irrigation schedule for critical days")
        
        if soil.water_holding_capacity < 1.5:
            recommendations.append("Low water holding capacity - monitor closely")
            recommendations.append("Consider soil amendments to improve water retention")
        
        return recommendations
    
    async def assess_crop_impact(
        self,
        field_id: UUID,
        crop_type: str,
        soil_characteristics: SoilCharacteristics,
        weather_data: List[WeatherPattern],
        growth_stage: str
    ) -> Dict[str, Any]:
        """
        Assess crop impact based on soil-weather integration.
        
        Args:
            field_id: Field identifier
            crop_type: Type of crop
            soil_characteristics: Soil characteristics
            weather_data: Weather data
            growth_stage: Current growth stage
            
        Returns:
            Crop impact assessment
        """
        try:
            logger.info(f"Assessing crop impact for {crop_type} in field {field_id}")
            
            # Get crop requirements
            crop_requirements = self.crop_water_requirements.get(crop_type, {})
            
            # Calculate water stress impact
            water_stress = self._calculate_crop_water_stress(
                weather_data, soil_characteristics, crop_type
            )
            
            # Calculate yield impact
            yield_impact = self._calculate_yield_impact(
                water_stress, crop_requirements, growth_stage
            )
            
            # Calculate quality impact
            quality_impact = self._calculate_quality_impact(
                water_stress, crop_type, growth_stage
            )
            
            # Calculate economic impact
            economic_impact = self._calculate_economic_impact(
                yield_impact, quality_impact, crop_type
            )
            
            return {
                "field_id": field_id,
                "crop_type": crop_type,
                "growth_stage": growth_stage,
                "water_stress": water_stress,
                "yield_impact": yield_impact,
                "quality_impact": quality_impact,
                "economic_impact": economic_impact,
                "recommendations": self._generate_crop_impact_recommendations(
                    water_stress, yield_impact, quality_impact
                )
            }
            
        except Exception as e:
            logger.error(f"Error assessing crop impact: {str(e)}")
            raise
    
    def _calculate_yield_impact(
        self,
        water_stress: Dict[str, Any],
        crop_requirements: Dict[str, Any],
        growth_stage: str
    ) -> Dict[str, Any]:
        """Calculate potential yield impact from water stress."""
        stress_score = water_stress["stress_score"]
        
        # Yield reduction factors by growth stage
        stage_sensitivity = {
            "emergence": 0.3,
            "vegetative": 0.5,
            "flowering": 0.8,
            "fruiting": 0.7,
            "maturity": 0.4
        }
        
        sensitivity = stage_sensitivity.get(growth_stage, 0.5)
        
        # Calculate yield reduction
        yield_reduction = (stress_score / 100) * sensitivity * 100
        
        # Determine impact level
        if yield_reduction >= 30:
            impact_level = "severe"
        elif yield_reduction >= 15:
            impact_level = "moderate"
        elif yield_reduction >= 5:
            impact_level = "mild"
        else:
            impact_level = "minimal"
        
        return {
            "impact_level": impact_level,
            "yield_reduction_percent": yield_reduction,
            "sensitivity_factor": sensitivity
        }
    
    def _calculate_quality_impact(
        self,
        water_stress: Dict[str, Any],
        crop_type: str,
        growth_stage: str
    ) -> Dict[str, Any]:
        """Calculate potential quality impact from water stress."""
        stress_score = water_stress["stress_score"]
        
        # Quality impact varies by crop type
        quality_sensitivity = {
            "corn": 0.6,
            "soybean": 0.7,
            "wheat": 0.5,
            "cotton": 0.8
        }
        
        sensitivity = quality_sensitivity.get(crop_type, 0.6)
        
        # Calculate quality reduction
        quality_reduction = (stress_score / 100) * sensitivity * 100
        
        return {
            "impact_level": "severe" if quality_reduction >= 20 else "moderate" if quality_reduction >= 10 else "mild",
            "quality_reduction_percent": quality_reduction,
            "sensitivity_factor": sensitivity
        }
    
    def _calculate_economic_impact(
        self,
        yield_impact: Dict[str, Any],
        quality_impact: Dict[str, Any],
        crop_type: str
    ) -> Dict[str, Any]:
        """Calculate economic impact from yield and quality impacts."""
        # Base crop prices (per bushel/unit)
        crop_prices = {
            "corn": 5.50,
            "soybean": 12.00,
            "wheat": 6.00,
            "cotton": 0.70
        }
        
        base_price = crop_prices.get(crop_type, 5.00)
        
        # Calculate revenue impact
        yield_reduction = yield_impact["yield_reduction_percent"]
        quality_reduction = quality_impact["quality_reduction_percent"]
        
        # Revenue reduction combines yield and quality impacts
        revenue_reduction = yield_reduction + (quality_reduction * 0.5)
        
        # Calculate economic impact
        economic_impact = revenue_reduction * base_price / 100
        
        return {
            "revenue_reduction_percent": revenue_reduction,
            "economic_impact_per_acre": economic_impact,
            "impact_level": "severe" if revenue_reduction >= 25 else "moderate" if revenue_reduction >= 15 else "mild"
        }
    
    def _generate_crop_impact_recommendations(
        self,
        water_stress: Dict[str, Any],
        yield_impact: Dict[str, Any],
        quality_impact: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on crop impact assessment."""
        recommendations = []
        
        # Water stress recommendations
        if water_stress["stress_level"] in ["severe", "moderate"]:
            recommendations.append("Implement immediate water management strategies")
            recommendations.append("Monitor crop water status daily")
        
        # Yield impact recommendations
        if yield_impact["impact_level"] in ["severe", "moderate"]:
            recommendations.append("Consider yield protection measures")
            recommendations.append("Evaluate irrigation options")
        
        # Quality impact recommendations
        if quality_impact["impact_level"] in ["severe", "moderate"]:
            recommendations.append("Focus on quality preservation")
            recommendations.append("Consider harvest timing adjustments")
        
        return recommendations
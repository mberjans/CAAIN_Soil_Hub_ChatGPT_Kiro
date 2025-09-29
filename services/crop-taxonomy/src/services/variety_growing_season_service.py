"""
Variety Growing Season Analysis Service

Comprehensive service for analyzing growing seasons by variety, including
phenology modeling, critical growth stage timing, and season risk assessment.

TICKET-005_crop-variety-recommendations-8.2 Implementation:
- Growing degree day calculations with variety-specific parameters
- Phenology modeling and critical growth stage timing
- Season length requirements analysis
- Temperature sensitivity analysis
- Photoperiod response analysis
- Integration with weather service, climate zone detection, and variety characteristics
- Growing season calendars, critical date predictions, and risk assessments
"""

import asyncio
import logging
import math
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
import json

try:
    from ..models.growing_season_models import (
        GrowingSeasonAnalysis,
        GrowingSeasonAnalysisRequest,
        GrowingSeasonAnalysisResponse,
        VarietyPhenologyProfile,
        PhenologyStage,
        GrowingDegreeDayParameters,
        SeasonLengthAnalysis,
        TemperatureSensitivityAnalysis,
        PhotoperiodAnalysis,
        CriticalDatePrediction,
        GrowingSeasonCalendar,
        SeasonRiskAssessment,
        GrowthStage,
        TemperatureSensitivity,
        PhotoperiodResponse,
        SeasonRiskLevel,
        PhenologyModelType,
        GrowingSeasonModelsValidator
    )
    from ..models.crop_variety_models import EnhancedCropVariety
except ImportError:
    from models.growing_season_models import (
        GrowingSeasonAnalysis,
        GrowingSeasonAnalysisRequest,
        GrowingSeasonAnalysisResponse,
        VarietyPhenologyProfile,
        PhenologyStage,
        GrowingDegreeDayParameters,
        SeasonLengthAnalysis,
        TemperatureSensitivityAnalysis,
        PhotoperiodAnalysis,
        CriticalDatePrediction,
        GrowingSeasonCalendar,
        SeasonRiskAssessment,
        GrowthStage,
        TemperatureSensitivity,
        PhotoperiodResponse,
        SeasonRiskLevel,
        PhenologyModelType,
        GrowingSeasonModelsValidator
    )
    from models.crop_variety_models import EnhancedCropVariety

logger = logging.getLogger(__name__)


@dataclass
class WeatherDataPoint:
    """Weather data point for calculations."""
    date: date
    temperature_c: float
    precipitation_mm: float
    day_length_hours: float
    solar_radiation: Optional[float] = None


class VarietyGrowingSeasonService:
    """
    Comprehensive service for variety-specific growing season analysis.
    
    Provides detailed analysis of growing seasons including phenology modeling,
    critical growth stage timing, season length requirements, temperature sensitivity,
    photoperiod response, and risk assessment.
    """
    
    def __init__(self):
        """Initialize the growing season service."""
        self.phenology_database = self._build_phenology_database()
        self.climate_data_cache = {}
        self.weather_data_cache = {}
        
        # Initialize external service connections
        self._initialize_external_services()
    
    def _initialize_external_services(self):
        """Initialize connections to external services."""
        try:
            # Import weather service from data-integration
            import sys
            import os
            data_integration_path = os.path.join(
                os.path.dirname(__file__), '..', '..', '..', '..', 'data-integration', 'src'
            )
            if data_integration_path not in sys.path:
                sys.path.append(data_integration_path)
            
            from services.weather_service import WeatherService
            self.weather_service = WeatherService()
            logger.info("Weather service connected successfully")
        except ImportError as e:
            logger.warning(f"Weather service not available: {e}")
            self.weather_service = None
        
        try:
            # Import climate zone service
            from services.coordinate_climate_detector import CoordinateClimateDetector
            self.climate_detector = CoordinateClimateDetector()
            logger.info("Climate detector connected successfully")
        except ImportError as e:
            logger.warning(f"Climate detector not available: {e}")
            self.climate_detector = None
    
    def _build_phenology_database(self) -> Dict[str, Dict[str, Any]]:
        """Build database of crop phenology characteristics."""
        return {
            "corn": {
                "stages": [
                    {"name": "emergence", "code": "VE", "gdd": 0, "days": 7, "description": "Seedling emergence"},
                    {"name": "vegetative", "code": "V6", "gdd": 475, "days": 30, "description": "6-leaf stage"},
                    {"name": "vegetative", "code": "V12", "gdd": 950, "days": 50, "description": "12-leaf stage"},
                    {"name": "flowering", "code": "R1", "gdd": 1250, "days": 65, "description": "Silking"},
                    {"name": "fruiting", "code": "R3", "gdd": 1500, "days": 80, "description": "Milk stage"},
                    {"name": "maturity", "code": "R6", "gdd": 2500, "days": 120, "description": "Physiological maturity"}
                ],
                "gdd_base_temp": 10.0,
                "total_gdd": 2500,
                "temperature_sensitivity": "sensitive",
                "photoperiod_response": "day_neutral",
                "heat_stress_threshold": 35.0,
                "cold_stress_threshold": 5.0
            },
            "soybean": {
                "stages": [
                    {"name": "emergence", "code": "VE", "gdd": 0, "days": 7, "description": "Seedling emergence"},
                    {"name": "vegetative", "code": "V3", "gdd": 200, "days": 20, "description": "3rd trifoliate"},
                    {"name": "vegetative", "code": "V6", "gdd": 400, "days": 35, "description": "6th trifoliate"},
                    {"name": "flowering", "code": "R1", "gdd": 600, "days": 45, "description": "Beginning bloom"},
                    {"name": "fruiting", "code": "R3", "gdd": 900, "days": 65, "description": "Beginning pod"},
                    {"name": "maturity", "code": "R8", "gdd": 2200, "days": 110, "description": "Full maturity"}
                ],
                "gdd_base_temp": 10.0,
                "total_gdd": 2200,
                "temperature_sensitivity": "moderate",
                "photoperiod_response": "short_day",
                "heat_stress_threshold": 32.0,
                "cold_stress_threshold": 8.0
            },
            "wheat": {
                "stages": [
                    {"name": "emergence", "code": "GS10", "gdd": 0, "days": 7, "description": "Seedling emergence"},
                    {"name": "vegetative", "code": "GS21", "gdd": 200, "days": 25, "description": "Tillering"},
                    {"name": "vegetative", "code": "GS30", "gdd": 500, "days": 45, "description": "Stem elongation"},
                    {"name": "flowering", "code": "GS60", "gdd": 800, "days": 70, "description": "Flowering"},
                    {"name": "fruiting", "code": "GS75", "gdd": 1200, "days": 90, "description": "Grain filling"},
                    {"name": "maturity", "code": "GS92", "gdd": 2000, "days": 120, "description": "Maturity"}
                ],
                "gdd_base_temp": 0.0,
                "total_gdd": 2000,
                "temperature_sensitivity": "tolerant",
                "photoperiod_response": "long_day",
                "heat_stress_threshold": 30.0,
                "cold_stress_threshold": -5.0
            },
            "tomato": {
                "stages": [
                    {"name": "emergence", "code": "VE", "gdd": 0, "days": 7, "description": "Seedling emergence"},
                    {"name": "vegetative", "code": "V4", "gdd": 200, "days": 25, "description": "4-leaf stage"},
                    {"name": "flowering", "code": "F1", "gdd": 600, "days": 45, "description": "First flower"},
                    {"name": "fruiting", "code": "F3", "gdd": 1000, "days": 65, "description": "Fruit set"},
                    {"name": "maturity", "code": "H1", "gdd": 2000, "days": 85, "description": "First harvest"}
                ],
                "gdd_base_temp": 10.0,
                "total_gdd": 2000,
                "temperature_sensitivity": "very_sensitive",
                "photoperiod_response": "day_neutral",
                "heat_stress_threshold": 30.0,
                "cold_stress_threshold": 10.0
            }
        }
    
    async def analyze_growing_season(
        self,
        request: GrowingSeasonAnalysisRequest
    ) -> GrowingSeasonAnalysisResponse:
        """
        Perform comprehensive growing season analysis for a variety.
        
        Args:
            request: Growing season analysis request
            
        Returns:
            Complete growing season analysis response
        """
        start_time = datetime.utcnow()
        logger.info(f"Starting growing season analysis for variety {request.variety_id}")
        
        try:
            # Get variety phenology profile
            phenology_profile = await self._get_variety_phenology_profile(
                request.variety_id, request.variety_name, request.crop_name
            )
            
            # Perform season length analysis
            season_length_analysis = await self._analyze_season_length(
                phenology_profile, request.location
            )
            
            # Perform temperature sensitivity analysis
            temperature_analysis = await self._analyze_temperature_sensitivity(
                phenology_profile, request.location
            )
            
            # Perform photoperiod analysis
            photoperiod_analysis = await self._analyze_photoperiod_response(
                phenology_profile, request.location
            )
            
            # Generate growing season calendar
            growing_calendar = await self._generate_growing_calendar(
                phenology_profile, request.location, request.planting_date
            )
            
            # Perform risk assessment
            risk_assessment = await self._assess_growing_season_risks(
                phenology_profile, request.location, season_length_analysis,
                temperature_analysis, photoperiod_analysis
            )
            
            # Calculate overall suitability score
            suitability_score = self._calculate_suitability_score(
                season_length_analysis, temperature_analysis, risk_assessment
            )
            
            # Generate key recommendations
            key_recommendations = self._generate_key_recommendations(
                season_length_analysis, temperature_analysis, photoperiod_analysis, risk_assessment
            )
            
            # Generate warnings
            warnings = self._generate_warnings(
                season_length_analysis, temperature_analysis, risk_assessment
            )
            
            # Calculate success probability
            success_probability = self._calculate_success_probability(
                suitability_score, risk_assessment
            )
            
            # Create comprehensive analysis
            analysis = GrowingSeasonAnalysis(
                variety_id=request.variety_id,
                variety_name=request.variety_name or request.variety_id,
                crop_name=request.crop_name,
                location=request.location,
                phenology_profile=phenology_profile,
                season_length_analysis=season_length_analysis,
                temperature_analysis=temperature_analysis,
                photoperiod_analysis=photoperiod_analysis,
                growing_calendar=growing_calendar,
                risk_assessment=risk_assessment,
                suitability_score=suitability_score,
                key_recommendations=key_recommendations,
                warnings=warnings,
                success_probability=success_probability
            )
            
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return GrowingSeasonAnalysisResponse(
                analysis=analysis,
                processing_time_ms=processing_time,
                data_sources=self._get_data_sources_used(),
                confidence_score=self._calculate_confidence_score(analysis)
            )
            
        except Exception as e:
            logger.error(f"Error in growing season analysis: {e}")
            raise
    
    async def _get_variety_phenology_profile(
        self,
        variety_id: str,
        variety_name: Optional[str],
        crop_name: str
    ) -> VarietyPhenologyProfile:
        """Get or create phenology profile for a variety."""
        
        # Try to get variety-specific data from database
        variety_data = await self._get_variety_data(variety_id, variety_name, crop_name)
        
        # Get base crop phenology data
        crop_phenology = self.phenology_database.get(crop_name.lower())
        if not crop_phenology:
            raise ValueError(f"No phenology data available for crop: {crop_name}")
        
        # Create phenology stages
        stages = []
        for stage_data in crop_phenology["stages"]:
            stage = PhenologyStage(
                stage_name=GrowthStage(stage_data["name"]),
                stage_code=stage_data["code"],
                gdd_requirement=stage_data.get("gdd"),
                days_from_planting=stage_data.get("days"),
                description=stage_data["description"]
            )
            stages.append(stage)
        
        # Create GDD parameters
        gdd_params = GrowingDegreeDayParameters(
            base_temperature_c=crop_phenology["gdd_base_temp"],
            variety_adjustment_factor=variety_data.get("gdd_adjustment_factor", 1.0)
        )
        
        # Create phenology profile
        profile = VarietyPhenologyProfile(
            variety_id=variety_id,
            variety_name=variety_name or variety_id,
            crop_name=crop_name,
            phenology_model_type=PhenologyModelType.THERMAL_TIME,
            gdd_parameters=gdd_params,
            stages=stages,
            total_gdd_requirement=crop_phenology["total_gdd"],
            days_to_maturity=max(stage.days_from_planting or 0 for stage in stages),
            temperature_sensitivity=TemperatureSensitivity(crop_phenology["temperature_sensitivity"]),
            photoperiod_response=PhotoperiodResponse(crop_phenology["photoperiod_response"]),
            heat_stress_threshold_c=crop_phenology.get("heat_stress_threshold"),
            cold_stress_threshold_c=crop_phenology.get("cold_stress_threshold")
        )
        
        return profile
    
    async def _get_variety_data(
        self,
        variety_id: str,
        variety_name: Optional[str],
        crop_name: str
    ) -> Dict[str, Any]:
        """Get variety-specific data from database or external sources."""
        
        # This would typically query a database or external API
        # For now, return default data
        return {
            "gdd_adjustment_factor": 1.0,
            "maturity_adjustment_days": 0,
            "stress_tolerances": [],
            "special_characteristics": []
        }
    
    async def _analyze_season_length(
        self,
        phenology_profile: VarietyPhenologyProfile,
        location: Dict[str, Any]
    ) -> SeasonLengthAnalysis:
        """Analyze season length requirements for the variety."""
        
        # Get climate data for location
        climate_data = await self._get_climate_data(location)
        
        # Calculate minimum season length
        min_season_length = phenology_profile.days_to_maturity + 30  # Buffer for establishment
        optimal_season_length = phenology_profile.days_to_maturity + 60  # Optimal with buffer
        
        # Get frost-free period
        frost_free_period = climate_data.get("frost_free_days", min_season_length)
        
        # Assess season length sufficiency
        if frost_free_period >= optimal_season_length:
            sufficiency = "excellent"
        elif frost_free_period >= min_season_length:
            sufficiency = "adequate"
        else:
            sufficiency = "insufficient"
        
        # Identify risk factors
        risk_factors = []
        if frost_free_period < min_season_length:
            risk_factors.append("Insufficient frost-free period")
        if climate_data.get("growing_degree_days", 0) < phenology_profile.total_gdd_requirement:
            risk_factors.append("Insufficient heat units")
        
        return SeasonLengthAnalysis(
            minimum_season_length_days=min_season_length,
            optimal_season_length_days=optimal_season_length,
            frost_free_period_required_days=min_season_length,
            heat_unit_requirement=phenology_profile.total_gdd_requirement,
            season_length_sufficiency=sufficiency,
            risk_factors=risk_factors
        )
    
    async def _analyze_temperature_sensitivity(
        self,
        phenology_profile: VarietyPhenologyProfile,
        location: Dict[str, Any]
    ) -> TemperatureSensitivityAnalysis:
        """Analyze temperature sensitivity for the variety."""
        
        # Get climate data
        climate_data = await self._get_climate_data(location)
        
        # Define optimal temperature ranges based on crop type
        optimal_ranges = {
            TemperatureSensitivity.VERY_SENSITIVE: (20.0, 25.0),
            TemperatureSensitivity.SENSITIVE: (18.0, 28.0),
            TemperatureSensitivity.MODERATE: (15.0, 30.0),
            TemperatureSensitivity.TOLERANT: (10.0, 35.0),
            TemperatureSensitivity.VERY_TOLERANT: (5.0, 40.0)
        }
        
        optimal_range = optimal_ranges.get(phenology_profile.temperature_sensitivity, (15.0, 30.0))
        
        # Calculate temperature adaptation score
        avg_temp = climate_data.get("average_temperature", 20.0)
        temp_score = self._calculate_temperature_score(avg_temp, optimal_range)
        
        # Generate stress tolerance notes
        stress_notes = []
        if phenology_profile.heat_stress_threshold_c:
            stress_notes.append(f"Heat stress threshold: {phenology_profile.heat_stress_threshold_c}°C")
        if phenology_profile.cold_stress_threshold_c:
            stress_notes.append(f"Cold stress threshold: {phenology_profile.cold_stress_threshold_c}°C")
        
        return TemperatureSensitivityAnalysis(
            optimal_temperature_range_c=optimal_range,
            minimum_growth_temperature_c=optimal_range[0] - 5.0,
            maximum_growth_temperature_c=optimal_range[1] + 5.0,
            heat_stress_threshold_c=phenology_profile.heat_stress_threshold_c,
            cold_stress_threshold_c=phenology_profile.cold_stress_threshold_c,
            temperature_adaptation_score=temp_score,
            stress_tolerance_notes=stress_notes
        )
    
    async def _analyze_photoperiod_response(
        self,
        phenology_profile: VarietyPhenologyProfile,
        location: Dict[str, Any]
    ) -> PhotoperiodAnalysis:
        """Analyze photoperiod response for the variety."""
        
        # Get location latitude
        latitude = location.get("latitude", 40.0)
        
        # Calculate day length at location
        max_day_length = self._calculate_max_day_length(latitude)
        min_day_length = self._calculate_min_day_length(latitude)
        
        # Determine photoperiod sensitivity
        sensitivity_levels = {
            PhotoperiodResponse.SHORT_DAY: "high",
            PhotoperiodResponse.LONG_DAY: "high",
            PhotoperiodResponse.DAY_NEUTRAL: "low",
            PhotoperiodResponse.INTERMEDIATE: "moderate"
        }
        
        sensitivity = sensitivity_levels.get(phenology_profile.photoperiod_response, "low")
        
        # Generate photoperiod notes
        notes = []
        if phenology_profile.photoperiod_response == PhotoperiodResponse.SHORT_DAY:
            notes.append("Requires short days for flowering")
        elif phenology_profile.photoperiod_response == PhotoperiodResponse.LONG_DAY:
            notes.append("Requires long days for flowering")
        else:
            notes.append("Day length has minimal effect on flowering")
        
        return PhotoperiodAnalysis(
            photoperiod_response_type=phenology_profile.photoperiod_response,
            day_length_sensitivity=sensitivity,
            adaptation_latitude_range=self._get_optimal_latitude_range(phenology_profile.photoperiod_response),
            photoperiod_notes=notes
        )
    
    async def _generate_growing_calendar(
        self,
        phenology_profile: VarietyPhenologyProfile,
        location: Dict[str, Any],
        planting_date: Optional[date]
    ) -> GrowingSeasonCalendar:
        """Generate comprehensive growing season calendar."""
        
        # Determine planting date
        if not planting_date:
            planting_date = await self._calculate_optimal_planting_date(phenology_profile, location)
        
        # Generate critical dates
        critical_dates = await self._predict_critical_dates(phenology_profile, planting_date, location)
        
        # Generate growth stage timeline
        growth_stages = self._generate_growth_stage_timeline(phenology_profile, planting_date)
        
        # Generate management windows
        management_windows = self._generate_management_windows(phenology_profile, planting_date)
        
        # Generate risk periods
        risk_periods = self._generate_risk_periods(phenology_profile, planting_date, location)
        
        # Generate harvest window
        harvest_window = self._generate_harvest_window(phenology_profile, planting_date)
        
        # Generate season summary
        season_summary = self._generate_season_summary(phenology_profile, critical_dates)
        
        return GrowingSeasonCalendar(
            variety_id=phenology_profile.variety_id,
            variety_name=phenology_profile.variety_name,
            crop_name=phenology_profile.crop_name,
            location=location,
            planting_date=planting_date,
            critical_dates=critical_dates,
            growth_stages=growth_stages,
            management_windows=management_windows,
            risk_periods=risk_periods,
            harvest_window=harvest_window,
            season_summary=season_summary
        )
    
    async def _assess_growing_season_risks(
        self,
        phenology_profile: VarietyPhenologyProfile,
        location: Dict[str, Any],
        season_length_analysis: SeasonLengthAnalysis,
        temperature_analysis: TemperatureSensitivityAnalysis,
        photoperiod_analysis: PhotoperiodAnalysis
    ) -> SeasonRiskAssessment:
        """Assess growing season risks for the variety."""
        
        risks = []
        mitigation_strategies = []
        contingency_plans = []
        
        # Assess season length risks
        if season_length_analysis.season_length_sufficiency == "insufficient":
            risks.append({
                "risk_type": "season_length",
                "severity": "high",
                "description": "Insufficient growing season length",
                "probability": 0.8
            })
            mitigation_strategies.append({
                "strategy": "early_planting",
                "description": "Plant as early as soil conditions allow",
                "effectiveness": 0.7
            })
            contingency_plans.append({
                "plan": "variety_substitution",
                "description": "Consider shorter-season variety",
                "trigger": "late_spring_conditions"
            })
        
        # Assess temperature risks
        if temperature_analysis.temperature_adaptation_score < 0.6:
            risks.append({
                "risk_type": "temperature",
                "severity": "moderate",
                "description": "Suboptimal temperature conditions",
                "probability": 0.6
            })
            mitigation_strategies.append({
                "strategy": "microclimate_management",
                "description": "Use row covers or shade structures",
                "effectiveness": 0.5
            })
        
        # Assess photoperiod risks
        if photoperiod_analysis.day_length_sensitivity == "high":
            risks.append({
                "risk_type": "photoperiod",
                "severity": "moderate",
                "description": "Day length may affect flowering",
                "probability": 0.4
            })
        
        # Calculate overall risk level
        if not risks:
            risk_level = SeasonRiskLevel.LOW
            risk_score = 0.2
        elif len(risks) == 1 and risks[0]["severity"] == "moderate":
            risk_level = SeasonRiskLevel.MODERATE
            risk_score = 0.4
        elif any(r["severity"] == "high" for r in risks):
            risk_level = SeasonRiskLevel.HIGH
            risk_score = 0.7
        else:
            risk_level = SeasonRiskLevel.MODERATE
            risk_score = 0.5
        
        return SeasonRiskAssessment(
            overall_risk_level=risk_level,
            risk_score=risk_score,
            identified_risks=risks,
            mitigation_strategies=mitigation_strategies,
            contingency_plans=contingency_plans,
            monitoring_recommendations=[
                "Monitor soil temperature before planting",
                "Track growing degree day accumulation",
                "Watch for stress symptoms during critical stages"
            ]
        )
    
    # Helper methods for calculations
    
    async def _get_climate_data(self, location: Dict[str, Any]) -> Dict[str, Any]:
        """Get climate data for location."""
        cache_key = f"{location.get('latitude', 0)}_{location.get('longitude', 0)}"
        
        if cache_key in self.climate_data_cache:
            return self.climate_data_cache[cache_key]
        
        # Try to get from climate detector
        if self.climate_detector:
            try:
                climate_data = await self.climate_detector.detect_climate_zone(
                    location.get("latitude", 40.0),
                    location.get("longitude", -95.0)
                )
                self.climate_data_cache[cache_key] = climate_data
                return climate_data
            except Exception as e:
                logger.warning(f"Could not get climate data: {e}")
        
        # Fallback to default data
        default_data = {
            "frost_free_days": 180,
            "growing_degree_days": 2500,
            "average_temperature": 20.0,
            "climate_zone": "6a"
        }
        self.climate_data_cache[cache_key] = default_data
        return default_data
    
    def _calculate_temperature_score(self, avg_temp: float, optimal_range: Tuple[float, float]) -> float:
        """Calculate temperature adaptation score."""
        min_temp, max_temp = optimal_range
        if min_temp <= avg_temp <= max_temp:
            return 1.0
        elif avg_temp < min_temp:
            return max(0.0, 1.0 - (min_temp - avg_temp) / 10.0)
        else:
            return max(0.0, 1.0 - (avg_temp - max_temp) / 10.0)
    
    def _calculate_max_day_length(self, latitude: float) -> float:
        """Calculate maximum day length at latitude."""
        # Simplified calculation for summer solstice
        declination = 23.45  # degrees
        hour_angle = math.acos(-math.tan(math.radians(latitude)) * math.tan(math.radians(declination)))
        return 24 * hour_angle / math.pi
    
    def _calculate_min_day_length(self, latitude: float) -> float:
        """Calculate minimum day length at latitude."""
        # Simplified calculation for winter solstice
        declination = -23.45  # degrees
        hour_angle = math.acos(-math.tan(math.radians(latitude)) * math.tan(math.radians(declination)))
        return 24 * hour_angle / math.pi
    
    def _get_optimal_latitude_range(self, photoperiod_response: PhotoperiodResponse) -> Tuple[float, float]:
        """Get optimal latitude range for photoperiod response."""
        ranges = {
            PhotoperiodResponse.SHORT_DAY: (25.0, 45.0),  # Lower latitudes
            PhotoperiodResponse.LONG_DAY: (35.0, 60.0),   # Higher latitudes
            PhotoperiodResponse.DAY_NEUTRAL: (20.0, 50.0),  # Wide range
            PhotoperiodResponse.INTERMEDIATE: (30.0, 50.0)  # Moderate range
        }
        return ranges.get(photoperiod_response, (20.0, 50.0))
    
    async def _calculate_optimal_planting_date(
        self,
        phenology_profile: VarietyPhenologyProfile,
        location: Dict[str, Any]
    ) -> date:
        """Calculate optimal planting date."""
        # This would integrate with the planting date service
        # For now, use a simplified calculation
        climate_data = await self._get_climate_data(location)
        last_frost_date = climate_data.get("last_frost_date", date(2024, 4, 15))
        
        # Adjust based on crop frost tolerance
        if phenology_profile.temperature_sensitivity == TemperatureSensitivity.VERY_SENSITIVE:
            return last_frost_date + timedelta(days=14)
        elif phenology_profile.temperature_sensitivity == TemperatureSensitivity.SENSITIVE:
            return last_frost_date + timedelta(days=7)
        else:
            return last_frost_date
    
    async def _predict_critical_dates(
        self,
        phenology_profile: VarietyPhenologyProfile,
        planting_date: date,
        location: Dict[str, Any]
    ) -> List[CriticalDatePrediction]:
        """Predict critical dates for the growing season."""
        critical_dates = []
        
        for stage in phenology_profile.stages:
            if stage.days_from_planting:
                predicted_date = planting_date + timedelta(days=stage.days_from_planting)
                critical_dates.append(CriticalDatePrediction(
                    date_type=f"{stage.stage_code} - {stage.description}",
                    predicted_date=predicted_date,
                    confidence_level=0.8,
                    factors_affecting_date=["Temperature", "Moisture", "Day length"],
                    management_recommendations=[f"Monitor for {stage.description}"]
                ))
        
        return critical_dates
    
    def _generate_growth_stage_timeline(
        self,
        phenology_profile: VarietyPhenologyProfile,
        planting_date: date
    ) -> List[Dict[str, Any]]:
        """Generate growth stage timeline."""
        timeline = []
        
        for stage in phenology_profile.stages:
            if stage.days_from_planting:
                stage_date = planting_date + timedelta(days=stage.days_from_planting)
                timeline.append({
                    "stage": stage.stage_code,
                    "description": stage.description,
                    "date": stage_date.isoformat(),
                    "days_from_planting": stage.days_from_planting,
                    "gdd_requirement": stage.gdd_requirement
                })
        
        return timeline
    
    def _generate_management_windows(
        self,
        phenology_profile: VarietyPhenologyProfile,
        planting_date: date
    ) -> List[Dict[str, Any]]:
        """Generate management windows."""
        windows = []
        
        # Pre-planting window
        windows.append({
            "window_type": "pre_planting",
            "start_date": (planting_date - timedelta(days=14)).isoformat(),
            "end_date": planting_date.isoformat(),
            "activities": ["Soil preparation", "Fertilizer application", "Seed treatment"],
            "priority": "high"
        })
        
        # Early season window
        windows.append({
            "window_type": "early_season",
            "start_date": planting_date.isoformat(),
            "end_date": (planting_date + timedelta(days=30)).isoformat(),
            "activities": ["Weed control", "Pest monitoring", "Irrigation"],
            "priority": "high"
        })
        
        return windows
    
    def _generate_risk_periods(
        self,
        phenology_profile: VarietyPhenologyProfile,
        planting_date: date,
        location: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate risk periods."""
        risk_periods = []
        
        # Early season frost risk
        risk_periods.append({
            "risk_type": "frost",
            "start_date": planting_date.isoformat(),
            "end_date": (planting_date + timedelta(days=30)).isoformat(),
            "severity": "moderate",
            "description": "Early season frost risk"
        })
        
        # Heat stress risk during flowering
        flowering_stage = next((s for s in phenology_profile.stages if s.stage_name == GrowthStage.FLOWERING), None)
        if flowering_stage and flowering_stage.days_from_planting:
            flowering_date = planting_date + timedelta(days=flowering_stage.days_from_planting)
            risk_periods.append({
                "risk_type": "heat_stress",
                "start_date": flowering_date.isoformat(),
                "end_date": (flowering_date + timedelta(days=14)).isoformat(),
                "severity": "moderate",
                "description": "Heat stress during flowering"
            })
        
        return risk_periods
    
    def _generate_harvest_window(
        self,
        phenology_profile: VarietyPhenologyProfile,
        planting_date: date
    ) -> Dict[str, Any]:
        """Generate harvest window information."""
        maturity_stage = next((s for s in phenology_profile.stages if s.stage_name == GrowthStage.MATURITY), None)
        
        if maturity_stage and maturity_stage.days_from_planting:
            harvest_date = planting_date + timedelta(days=maturity_stage.days_from_planting)
            return {
                "optimal_harvest_date": harvest_date.isoformat(),
                "harvest_window_start": (harvest_date - timedelta(days=7)).isoformat(),
                "harvest_window_end": (harvest_date + timedelta(days=14)).isoformat(),
                "harvest_considerations": ["Monitor moisture content", "Check maturity indicators"]
            }
        
        return {"harvest_window": "Not available"}
    
    def _generate_season_summary(
        self,
        phenology_profile: VarietyPhenologyProfile,
        critical_dates: List[CriticalDatePrediction]
    ) -> Dict[str, Any]:
        """Generate season summary."""
        return {
            "total_growing_days": phenology_profile.days_to_maturity,
            "total_gdd_requirement": phenology_profile.total_gdd_requirement,
            "critical_stages": len(critical_dates),
            "temperature_sensitivity": phenology_profile.temperature_sensitivity.value,
            "photoperiod_response": phenology_profile.photoperiod_response.value
        }
    
    def _calculate_suitability_score(
        self,
        season_length_analysis: SeasonLengthAnalysis,
        temperature_analysis: TemperatureSensitivityAnalysis,
        risk_assessment: SeasonRiskAssessment
    ) -> float:
        """Calculate overall suitability score."""
        season_score = 1.0 if season_length_analysis.season_length_sufficiency == "excellent" else 0.7
        temp_score = temperature_analysis.temperature_adaptation_score
        risk_score = 1.0 - risk_assessment.risk_score
        
        return (season_score + temp_score + risk_score) / 3.0
    
    def _generate_key_recommendations(
        self,
        season_length_analysis: SeasonLengthAnalysis,
        temperature_analysis: TemperatureSensitivityAnalysis,
        photoperiod_analysis: PhotoperiodAnalysis,
        risk_assessment: SeasonRiskAssessment
    ) -> List[str]:
        """Generate key recommendations."""
        recommendations = []
        
        if season_length_analysis.season_length_sufficiency == "insufficient":
            recommendations.append("Consider shorter-season variety or early planting")
        
        if temperature_analysis.temperature_adaptation_score < 0.7:
            recommendations.append("Monitor temperature conditions closely")
        
        if risk_assessment.overall_risk_level in [SeasonRiskLevel.HIGH, SeasonRiskLevel.CRITICAL]:
            recommendations.append("Implement risk mitigation strategies")
        
        return recommendations
    
    def _generate_warnings(
        self,
        season_length_analysis: SeasonLengthAnalysis,
        temperature_analysis: TemperatureSensitivityAnalysis,
        risk_assessment: SeasonRiskAssessment
    ) -> List[str]:
        """Generate warnings."""
        warnings = []
        
        for risk_factor in season_length_analysis.risk_factors:
            warnings.append(f"Season length risk: {risk_factor}")
        
        if temperature_analysis.temperature_adaptation_score < 0.5:
            warnings.append("Temperature conditions may be suboptimal")
        
        if risk_assessment.overall_risk_level == SeasonRiskLevel.CRITICAL:
            warnings.append("High risk of crop failure")
        
        return warnings
    
    def _calculate_success_probability(
        self,
        suitability_score: float,
        risk_assessment: SeasonRiskAssessment
    ) -> float:
        """Calculate success probability."""
        base_probability = suitability_score
        risk_adjustment = 1.0 - risk_assessment.risk_score
        return min(1.0, base_probability * risk_adjustment)
    
    def _get_data_sources_used(self) -> List[str]:
        """Get list of data sources used."""
        sources = ["phenology_database", "climate_estimates"]
        if self.weather_service:
            sources.append("weather_service")
        if self.climate_detector:
            sources.append("climate_detector")
        return sources
    
    def _calculate_confidence_score(self, analysis: GrowingSeasonAnalysis) -> float:
        """Calculate overall confidence score."""
        # Base confidence on data availability and analysis completeness
        base_confidence = 0.8
        
        # Adjust based on data sources
        if self.weather_service and self.climate_detector:
            base_confidence += 0.1
        
        # Adjust based on variety data availability
        if analysis.phenology_profile.variety_name != analysis.phenology_profile.variety_id:
            base_confidence += 0.05
        
        return min(1.0, base_confidence)


# Create singleton instance
variety_growing_season_service = VarietyGrowingSeasonService()
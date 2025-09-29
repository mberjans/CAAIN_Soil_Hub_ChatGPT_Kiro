"""
Growing Season Analysis Models

Comprehensive data models for variety-specific growing season analysis,
phenology modeling, and critical growth stage timing calculations.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union, Tuple
from datetime import date, datetime, timedelta
from enum import Enum
from uuid import UUID
import math


# ============================================================================
# GROWING SEASON ENUMERATIONS
# ============================================================================

class GrowthStage(str, Enum):
    """Critical growth stages for phenology modeling."""
    EMERGENCE = "emergence"
    VEGETATIVE = "vegetative"
    FLOWERING = "flowering"
    FRUITING = "fruiting"
    MATURITY = "maturity"
    HARVEST = "harvest"


class TemperatureSensitivity(str, Enum):
    """Temperature sensitivity levels for varieties."""
    VERY_SENSITIVE = "very_sensitive"
    SENSITIVE = "sensitive"
    MODERATE = "moderate"
    TOLERANT = "tolerant"
    VERY_TOLERANT = "very_tolerant"


class PhotoperiodResponse(str, Enum):
    """Photoperiod response types."""
    SHORT_DAY = "short_day"
    LONG_DAY = "long_day"
    DAY_NEUTRAL = "day_neutral"
    INTERMEDIATE = "intermediate"


class SeasonRiskLevel(str, Enum):
    """Risk levels for growing season challenges."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class PhenologyModelType(str, Enum):
    """Types of phenology models."""
    THERMAL_TIME = "thermal_time"
    PHOTOPERIOD_THERMAL = "photoperiod_thermal"
    DEVELOPMENTAL_STAGE = "developmental_stage"
    HYBRID = "hybrid"


# ============================================================================
# CORE GROWING SEASON MODELS
# ============================================================================

class GrowingDegreeDayParameters(BaseModel):
    """Parameters for growing degree day calculations."""
    
    base_temperature_c: float = Field(10.0, description="Base temperature in Celsius")
    upper_threshold_c: Optional[float] = Field(None, description="Upper threshold temperature")
    method: str = Field("single_sine", description="GDD calculation method")
    variety_adjustment_factor: float = Field(1.0, ge=0.5, le=2.0, description="Variety-specific adjustment factor")


class PhenologyStage(BaseModel):
    """Individual phenology stage information."""
    
    stage_name: GrowthStage = Field(..., description="Growth stage name")
    stage_code: str = Field(..., description="Stage code (e.g., V6, R1)")
    gdd_requirement: Optional[int] = Field(None, description="GDD requirement to reach stage")
    days_from_planting: Optional[int] = Field(None, description="Days from planting to reach stage")
    critical_temperature_min_c: Optional[float] = Field(None, description="Minimum temperature for stage")
    critical_temperature_max_c: Optional[float] = Field(None, description="Maximum temperature for stage")
    photoperiod_requirement_hours: Optional[float] = Field(None, description="Required day length in hours")
    water_requirement_mm: Optional[float] = Field(None, description="Water requirement in mm")
    description: str = Field(..., description="Stage description")
    management_notes: List[str] = Field(default_factory=list, description="Management recommendations")


class VarietyPhenologyProfile(BaseModel):
    """Complete phenology profile for a variety."""
    
    variety_id: str = Field(..., description="Variety identifier")
    variety_name: str = Field(..., description="Variety name")
    crop_name: str = Field(..., description="Crop name")
    phenology_model_type: PhenologyModelType = Field(PhenologyModelType.THERMAL_TIME, description="Model type")
    gdd_parameters: GrowingDegreeDayParameters = Field(default_factory=GrowingDegreeDayParameters)
    stages: List[PhenologyStage] = Field(..., description="Growth stages")
    total_gdd_requirement: int = Field(..., description="Total GDD requirement")
    days_to_maturity: int = Field(..., description="Days to physiological maturity")
    temperature_sensitivity: TemperatureSensitivity = Field(TemperatureSensitivity.MODERATE)
    photoperiod_response: PhotoperiodResponse = Field(PhotoperiodResponse.DAY_NEUTRAL)
    chilling_requirement_hours: Optional[int] = Field(None, description="Chilling requirement for dormancy")
    heat_stress_threshold_c: Optional[float] = Field(None, description="Heat stress threshold")
    cold_stress_threshold_c: Optional[float] = Field(None, description="Cold stress threshold")


class SeasonLengthAnalysis(BaseModel):
    """Analysis of season length requirements."""
    
    minimum_season_length_days: int = Field(..., description="Minimum season length required")
    optimal_season_length_days: int = Field(..., description="Optimal season length")
    maximum_season_length_days: Optional[int] = Field(None, description="Maximum beneficial season length")
    frost_free_period_required_days: int = Field(..., description="Required frost-free period")
    heat_unit_requirement: int = Field(..., description="Total heat unit requirement")
    season_length_sufficiency: str = Field(..., description="Assessment of season length sufficiency")
    risk_factors: List[str] = Field(default_factory=list, description="Identified risk factors")


class TemperatureSensitivityAnalysis(BaseModel):
    """Analysis of temperature sensitivity."""
    
    optimal_temperature_range_c: Tuple[float, float] = Field(..., description="Optimal temperature range")
    minimum_growth_temperature_c: float = Field(..., description="Minimum temperature for growth")
    maximum_growth_temperature_c: float = Field(..., description="Maximum temperature for growth")
    heat_stress_threshold_c: Optional[float] = Field(None, description="Heat stress threshold")
    cold_stress_threshold_c: Optional[float] = Field(None, description="Cold stress threshold")
    temperature_adaptation_score: float = Field(..., ge=0.0, le=1.0, description="Temperature adaptation score")
    stress_tolerance_notes: List[str] = Field(default_factory=list, description="Stress tolerance notes")


class PhotoperiodAnalysis(BaseModel):
    """Analysis of photoperiod response."""
    
    photoperiod_response_type: PhotoperiodResponse = Field(..., description="Photoperiod response type")
    critical_day_length_hours: Optional[float] = Field(None, description="Critical day length")
    day_length_sensitivity: str = Field(..., description="Day length sensitivity level")
    flowering_response_days: Optional[int] = Field(None, description="Days to flowering under optimal conditions")
    adaptation_latitude_range: Optional[Tuple[float, float]] = Field(None, description="Optimal latitude range")
    photoperiod_notes: List[str] = Field(default_factory=list, description="Photoperiod-related notes")


class CriticalDatePrediction(BaseModel):
    """Prediction for critical dates in the growing season."""
    
    date_type: str = Field(..., description="Type of critical date")
    predicted_date: date = Field(..., description="Predicted date")
    confidence_level: float = Field(..., ge=0.0, le=1.0, description="Prediction confidence")
    earliest_possible_date: Optional[date] = Field(None, description="Earliest possible date")
    latest_possible_date: Optional[date] = Field(None, description="Latest possible date")
    factors_affecting_date: List[str] = Field(default_factory=list, description="Factors affecting timing")
    management_recommendations: List[str] = Field(default_factory=list, description="Management recommendations")


class GrowingSeasonCalendar(BaseModel):
    """Complete growing season calendar for a variety."""
    
    variety_id: str = Field(..., description="Variety identifier")
    variety_name: str = Field(..., description="Variety name")
    crop_name: str = Field(..., description="Crop name")
    location: Dict[str, Any] = Field(..., description="Location information")
    planting_date: date = Field(..., description="Recommended planting date")
    critical_dates: List[CriticalDatePrediction] = Field(..., description="Critical dates")
    growth_stages: List[Dict[str, Any]] = Field(..., description="Growth stage timeline")
    management_windows: List[Dict[str, Any]] = Field(..., description="Management windows")
    risk_periods: List[Dict[str, Any]] = Field(..., description="High-risk periods")
    harvest_window: Dict[str, Any] = Field(..., description="Harvest window information")
    season_summary: Dict[str, Any] = Field(..., description="Season summary")


class SeasonRiskAssessment(BaseModel):
    """Assessment of growing season risks."""
    
    overall_risk_level: SeasonRiskLevel = Field(..., description="Overall risk level")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Risk score (0-1)")
    identified_risks: List[Dict[str, Any]] = Field(..., description="Identified risks")
    mitigation_strategies: List[Dict[str, Any]] = Field(..., description="Mitigation strategies")
    contingency_plans: List[Dict[str, Any]] = Field(..., description="Contingency plans")
    monitoring_recommendations: List[str] = Field(..., description="Monitoring recommendations")


class GrowingSeasonAnalysis(BaseModel):
    """Comprehensive growing season analysis for a variety."""
    
    variety_id: str = Field(..., description="Variety identifier")
    variety_name: str = Field(..., description="Variety name")
    crop_name: str = Field(..., description="Crop name")
    location: Dict[str, Any] = Field(..., description="Location information")
    analysis_date: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")
    
    # Core analyses
    phenology_profile: VarietyPhenologyProfile = Field(..., description="Phenology profile")
    season_length_analysis: SeasonLengthAnalysis = Field(..., description="Season length analysis")
    temperature_analysis: TemperatureSensitivityAnalysis = Field(..., description="Temperature analysis")
    photoperiod_analysis: PhotoperiodAnalysis = Field(..., description="Photoperiod analysis")
    
    # Predictions and calendars
    growing_calendar: GrowingSeasonCalendar = Field(..., description="Growing season calendar")
    risk_assessment: SeasonRiskAssessment = Field(..., description="Risk assessment")
    
    # Summary metrics
    suitability_score: float = Field(..., ge=0.0, le=1.0, description="Overall suitability score")
    key_recommendations: List[str] = Field(..., description="Key recommendations")
    warnings: List[str] = Field(default_factory=list, description="Important warnings")
    success_probability: float = Field(..., ge=0.0, le=1.0, description="Success probability")


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class GrowingSeasonAnalysisRequest(BaseModel):
    """Request model for growing season analysis."""
    
    variety_id: str = Field(..., description="Variety identifier")
    variety_name: Optional[str] = Field(None, description="Variety name")
    crop_name: str = Field(..., description="Crop name")
    location: Dict[str, Any] = Field(..., description="Location data")
    planting_date: Optional[date] = Field(None, description="Target planting date")
    analysis_options: Dict[str, Any] = Field(default_factory=dict, description="Analysis options")


class GrowingSeasonAnalysisResponse(BaseModel):
    """Response model for growing season analysis."""
    
    analysis: GrowingSeasonAnalysis = Field(..., description="Complete analysis")
    processing_time_ms: float = Field(..., description="Processing time")
    data_sources: List[str] = Field(..., description="Data sources used")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Overall confidence")


class PhenologyPredictionRequest(BaseModel):
    """Request model for phenology predictions."""
    
    variety_id: str = Field(..., description="Variety identifier")
    planting_date: date = Field(..., description="Planting date")
    location: Dict[str, Any] = Field(..., description="Location data")
    weather_data: Optional[Dict[str, Any]] = Field(None, description="Weather data")
    prediction_options: Dict[str, Any] = Field(default_factory=dict, description="Prediction options")


class PhenologyPredictionResponse(BaseModel):
    """Response model for phenology predictions."""
    
    variety_id: str = Field(..., description="Variety identifier")
    planting_date: date = Field(..., description="Planting date")
    predicted_stages: List[Dict[str, Any]] = Field(..., description="Predicted growth stages")
    critical_dates: List[CriticalDatePrediction] = Field(..., description="Critical dates")
    confidence_scores: Dict[str, float] = Field(..., description="Confidence scores")
    processing_time_ms: float = Field(..., description="Processing time")


# ============================================================================
# VALIDATION METHODS
# ============================================================================

class GrowingSeasonModelsValidator:
    """Validation methods for growing season models."""
    
    @staticmethod
    def validate_temperature_range(min_temp: float, max_temp: float) -> bool:
        """Validate temperature range is logical."""
        return min_temp < max_temp and -50 <= min_temp <= 50 and -30 <= max_temp <= 60
    
    @staticmethod
    def validate_gdd_parameters(gdd_params: GrowingDegreeDayParameters) -> bool:
        """Validate GDD parameters."""
        if gdd_params.base_temperature_c < -10 or gdd_params.base_temperature_c > 30:
            return False
        if gdd_params.upper_threshold_c and gdd_params.upper_threshold_c <= gdd_params.base_temperature_c:
            return False
        return True
    
    @staticmethod
    def validate_phenology_stages(stages: List[PhenologyStage]) -> bool:
        """Validate phenology stages are logical."""
        if not stages:
            return False
        
        # Check for required stages
        required_stages = {GrowthStage.EMERGENCE, GrowthStage.MATURITY}
        stage_names = {stage.stage_name for stage in stages}
        if not required_stages.issubset(stage_names):
            return False
        
        # Check GDD progression
        gdd_stages = [stage for stage in stages if stage.gdd_requirement is not None]
        if len(gdd_stages) > 1:
            gdd_values = [stage.gdd_requirement for stage in gdd_stages]
            return gdd_values == sorted(gdd_values)
        
        return True
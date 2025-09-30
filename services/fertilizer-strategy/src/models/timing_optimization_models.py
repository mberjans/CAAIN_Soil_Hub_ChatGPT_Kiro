"""
Timing Optimization Models for Fertilizer Strategy Service

This module contains Pydantic models for fertilizer timing optimization,
including weather integration, crop growth stages, and application timing.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional, Any, Union
from datetime import datetime, date
from enum import Enum
import uuid


class CropGrowthStage(str, Enum):
    """Crop growth stages for timing optimization."""
    PLANTING = "planting"
    EMERGENCE = "emergence"
    V2 = "v2"  # 2-leaf stage
    V4 = "v4"  # 4-leaf stage
    V6 = "v6"  # 6-leaf stage
    V8 = "v8"  # 8-leaf stage
    V10 = "v10"  # 10-leaf stage
    V12 = "v12"  # 12-leaf stage
    VT = "vt"  # Tasseling
    R1 = "r1"  # Silking
    R2 = "r2"  # Blister
    R3 = "r3"  # Milk
    R4 = "r4"  # Dough
    R5 = "r5"  # Dent
    R6 = "r6"  # Physiological maturity
    HARVEST = "harvest"


class ApplicationMethod(str, Enum):
    """Fertilizer application methods."""
    BROADCAST = "broadcast"
    BROADCAST_INCORPORATED = "broadcast_incorporated"
    BANDED = "banded"
    SIDE_DRESS = "side_dress"
    FOLIAR = "foliar"
    FERTIGATION = "fertigation"
    INJECTION = "injection"


class WeatherCondition(str, Enum):
    """Weather conditions affecting application timing."""
    OPTIMAL = "optimal"
    ACCEPTABLE = "acceptable"
    MARGINAL = "marginal"
    POOR = "poor"
    UNACCEPTABLE = "unacceptable"


class TimingConstraintType(str, Enum):
    """Types of timing constraints."""
    WEATHER_WINDOW = "weather_window"
    EQUIPMENT_AVAILABILITY = "equipment_availability"
    LABOR_AVAILABILITY = "labor_availability"
    SOIL_CONDITIONS = "soil_conditions"
    CROP_STAGE = "crop_stage"
    REGULATORY = "regulatory"


class FertilizerType(str, Enum):
    """Fertilizer types for timing optimization."""
    NITROGEN = "nitrogen"
    PHOSPHORUS = "phosphorus"
    POTASSIUM = "potassium"
    COMPLETE = "complete"
    MICRONUTRIENTS = "micronutrients"
    ORGANIC = "organic"
    LIQUID = "liquid"
    GRANULAR = "granular"


class TimingOptimizationRequest(BaseModel):
    """Request model for fertilizer timing optimization."""
    
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique request identifier")
    
    # Field and crop information
    field_id: str = Field(..., description="Field identifier")
    crop_type: str = Field(..., description="Crop type (corn, soybean, wheat, etc.)")
    planting_date: date = Field(..., description="Expected planting date")
    expected_harvest_date: Optional[date] = Field(None, description="Expected harvest date")
    
    # Fertilizer requirements
    fertilizer_requirements: Dict[str, float] = Field(..., description="Fertilizer requirements by type (lbs/acre)")
    application_methods: List[ApplicationMethod] = Field(..., description="Preferred application methods")
    
    # Field characteristics
    soil_type: str = Field(..., description="Soil type")
    soil_moisture_capacity: float = Field(..., ge=0.0, le=1.0, description="Soil moisture capacity (0-1)")
    drainage_class: str = Field(default="moderate", description="Drainage class")
    slope_percent: float = Field(default=0.0, ge=0.0, le=100.0, description="Field slope percentage")
    
    # Weather and environmental factors
    weather_data_source: str = Field(default="noaa", description="Weather data source")
    location: Dict[str, float] = Field(..., description="Field location (lat, lng)")
    
    # Constraints
    equipment_availability: Dict[str, List[str]] = Field(default_factory=dict, description="Equipment availability by date")
    labor_availability: Dict[str, int] = Field(default_factory=dict, description="Labor availability by date")
    budget_constraints: Optional[Dict[str, float]] = Field(None, description="Budget constraints")
    
    # Optimization preferences
    optimization_horizon_days: int = Field(default=365, ge=30, le=730, description="Optimization horizon in days")
    risk_tolerance: float = Field(default=0.5, ge=0.0, le=1.0, description="Risk tolerance (0=conservative, 1=aggressive)")
    prioritize_yield: bool = Field(default=True, description="Prioritize yield optimization")
    prioritize_cost: bool = Field(default=False, description="Prioritize cost optimization")
    
    # Advanced options
    split_application_allowed: bool = Field(default=True, description="Allow split applications")
    weather_dependent_timing: bool = Field(default=True, description="Consider weather for timing")
    soil_temperature_threshold: float = Field(default=50.0, description="Minimum soil temperature for application (°F)")
    
    @field_validator('fertilizer_requirements')
    @classmethod
    def validate_fertilizer_requirements(cls, v):
        """Validate fertilizer requirements."""
        if not v:
            raise ValueError("At least one fertilizer requirement must be specified")
        
        for fertilizer_type, amount in v.items():
            if amount < 0:
                raise ValueError(f"Fertilizer amount for {fertilizer_type} must be non-negative")
        
        return v
    
    @field_validator('location')
    @classmethod
    def validate_location(cls, v):
        """Validate location coordinates."""
        if 'lat' not in v or 'lng' not in v:
            raise ValueError("Location must contain 'lat' and 'lng'")
        
        if not (-90 <= v['lat'] <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        
        if not (-180 <= v['lng'] <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        
        return v


class WeatherWindow(BaseModel):
    """Weather window for fertilizer application."""
    
    start_date: date = Field(..., description="Window start date")
    end_date: date = Field(..., description="Window end date")
    condition: WeatherCondition = Field(..., description="Weather condition")
    temperature_f: float = Field(..., description="Average temperature (°F)")
    precipitation_probability: float = Field(..., ge=0.0, le=1.0, description="Precipitation probability")
    wind_speed_mph: float = Field(..., ge=0.0, description="Wind speed (mph)")
    soil_moisture: float = Field(..., ge=0.0, le=1.0, description="Soil moisture level")
    suitability_score: float = Field(..., ge=0.0, le=1.0, description="Application suitability score")


class ApplicationTiming(BaseModel):
    """Optimal application timing recommendation."""
    
    fertilizer_type: str = Field(..., description="Fertilizer type")
    application_method: ApplicationMethod = Field(..., description="Application method")
    recommended_date: date = Field(..., description="Recommended application date")
    application_window: WeatherWindow = Field(..., description="Optimal weather window")
    crop_stage: CropGrowthStage = Field(..., description="Target crop growth stage")
    amount_lbs_per_acre: float = Field(..., ge=0.0, description="Application amount (lbs/acre)")
    
    # Timing factors
    timing_score: float = Field(..., ge=0.0, le=1.0, description="Timing optimization score")
    weather_score: float = Field(..., ge=0.0, le=1.0, description="Weather suitability score")
    crop_score: float = Field(..., ge=0.0, le=1.0, description="Crop stage suitability score")
    soil_score: float = Field(..., ge=0.0, le=1.0, description="Soil condition score")
    
    # Risk factors
    weather_risk: float = Field(..., ge=0.0, le=1.0, description="Weather-related risk")
    timing_risk: float = Field(..., ge=0.0, le=1.0, description="Timing-related risk")
    equipment_risk: float = Field(..., ge=0.0, le=1.0, description="Equipment availability risk")
    
    # Economic factors
    estimated_cost_per_acre: float = Field(..., ge=0.0, description="Estimated cost per acre")
    yield_impact_percent: float = Field(default=0.0, description="Expected yield impact (%)")
    
    # Alternative timings
    alternative_dates: List[date] = Field(default_factory=list, description="Alternative application dates")
    backup_window: Optional[WeatherWindow] = Field(None, description="Backup weather window")


class SplitApplicationPlan(BaseModel):
    """Split application plan for fertilizers."""
    
    fertilizer_type: str = Field(..., description="Fertilizer type")
    total_amount_lbs_per_acre: float = Field(..., ge=0.0, description="Total amount (lbs/acre)")
    
    # Split applications
    applications: List[ApplicationTiming] = Field(..., description="Individual applications")
    
    # Plan characteristics
    split_ratio: List[float] = Field(..., description="Split ratios for each application")
    total_timing_score: float = Field(..., ge=0.0, le=1.0, description="Overall timing score")
    risk_reduction_percent: float = Field(default=0.0, description="Risk reduction percentage")
    cost_impact_percent: float = Field(default=0.0, description="Cost impact percentage")


class TimingOptimizationResult(BaseModel):
    """Result model for fertilizer timing optimization."""
    
    request_id: str = Field(..., description="Request identifier")
    optimization_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Optimization identifier")
    
    # Optimization results
    optimal_timings: List[ApplicationTiming] = Field(..., description="Optimal application timings")
    split_plans: List[SplitApplicationPlan] = Field(default_factory=list, description="Split application plans")
    
    # Weather analysis
    weather_windows: List[WeatherWindow] = Field(..., description="Available weather windows")
    weather_forecast_days: int = Field(default=14, description="Weather forecast horizon")
    
    # Optimization metrics
    overall_timing_score: float = Field(..., ge=0.0, le=1.0, description="Overall timing optimization score")
    weather_suitability_score: float = Field(..., ge=0.0, le=1.0, description="Weather suitability score")
    crop_stage_alignment_score: float = Field(..., ge=0.0, le=1.0, description="Crop stage alignment score")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Overall risk score")
    
    # Economic analysis
    total_estimated_cost: float = Field(..., ge=0.0, description="Total estimated cost")
    cost_per_acre: float = Field(..., ge=0.0, description="Cost per acre")
    expected_yield_impact: float = Field(default=0.0, description="Expected yield impact (%)")
    roi_estimate: float = Field(default=0.0, description="Estimated ROI")
    
    # Recommendations
    recommendations: List[str] = Field(..., description="Timing recommendations")
    risk_mitigation_strategies: List[str] = Field(default_factory=list, description="Risk mitigation strategies")
    alternative_strategies: List[str] = Field(default_factory=list, description="Alternative strategies")
    
    # Metadata
    optimization_method: str = Field(default="multi_objective", description="Optimization method used")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in optimization results")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")


class TimingConstraint(BaseModel):
    """Timing constraint for optimization."""
    
    constraint_type: TimingConstraintType = Field(..., description="Type of constraint")
    description: str = Field(..., description="Constraint description")
    start_date: Optional[date] = Field(None, description="Constraint start date")
    end_date: Optional[date] = Field(None, description="Constraint end date")
    severity: float = Field(default=0.5, ge=0.0, le=1.0, description="Constraint severity (0=soft, 1=hard)")
    impact_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Impact on optimization score")


class EquipmentAvailability(BaseModel):
    """Equipment availability for timing optimization."""
    
    equipment_type: str = Field(..., description="Type of equipment")
    available_dates: List[date] = Field(..., description="Available dates")
    capacity_per_day: float = Field(..., ge=0.0, description="Capacity per day (acres)")
    cost_per_acre: float = Field(default=0.0, ge=0.0, description="Cost per acre")
    efficiency_factor: float = Field(default=1.0, ge=0.0, le=1.0, description="Efficiency factor")


class LaborAvailability(BaseModel):
    """Labor availability for timing optimization."""
    
    labor_type: str = Field(..., description="Type of labor")
    available_dates: List[date] = Field(..., description="Available dates")
    hours_per_day: int = Field(..., ge=0, le=24, description="Hours per day")
    cost_per_hour: float = Field(default=0.0, ge=0.0, description="Cost per hour")
    skill_level: str = Field(default="standard", description="Skill level")


class TimingOptimizationSummary(BaseModel):
    """Summary of timing optimization results."""
    
    total_applications: int = Field(..., description="Total number of applications")
    applications_by_month: Dict[str, int] = Field(..., description="Applications by month")
    risk_level: str = Field(..., description="Overall risk level")
    cost_efficiency_score: float = Field(..., ge=0.0, le=1.0, description="Cost efficiency score")
    weather_dependency_score: float = Field(..., ge=0.0, le=1.0, description="Weather dependency score")
    flexibility_score: float = Field(..., ge=0.0, le=1.0, description="Schedule flexibility score")
    
    # Key insights
    primary_risks: List[str] = Field(..., description="Primary risk factors")
    optimization_opportunities: List[str] = Field(..., description="Optimization opportunities")
    critical_timing_windows: List[str] = Field(..., description="Critical timing windows")
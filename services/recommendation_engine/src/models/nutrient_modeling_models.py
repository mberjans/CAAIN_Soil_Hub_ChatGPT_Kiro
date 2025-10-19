"""
Nutrient Modeling Data Models

Pydantic models for nutrient uptake and loss modeling in fertilizer timing optimization.
Supports comprehensive modeling of nutrient fate, uptake curves, and loss predictions.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum


class CropType(str, Enum):
    """Major crop types with distinct nutrient uptake patterns."""
    CORN = "corn"
    SOYBEAN = "soybean"
    WHEAT = "wheat"
    COTTON = "cotton"
    RICE = "rice"
    POTATO = "potato"
    TOMATO = "tomato"
    ALFALFA = "alfalfa"


class GrowthStage(str, Enum):
    """Standardized crop growth stages."""
    # Corn growth stages (V-stages and R-stages)
    VE = "VE"  # Emergence
    V1 = "V1"  # First leaf
    V3 = "V3"  # Three leaves
    V6 = "V6"  # Six leaves
    V9 = "V9"  # Nine leaves
    V12 = "V12"  # Twelve leaves
    VT = "VT"  # Tasseling
    R1 = "R1"  # Silking
    R2 = "R2"  # Blister
    R3 = "R3"  # Milk
    R4 = "R4"  # Dough
    R5 = "R5"  # Dent
    R6 = "R6"  # Physiological maturity

    # Generic stages (applicable to multiple crops)
    EMERGENCE = "emergence"
    VEGETATIVE_EARLY = "vegetative_early"
    VEGETATIVE_MID = "vegetative_mid"
    VEGETATIVE_LATE = "vegetative_late"
    REPRODUCTIVE_EARLY = "reproductive_early"
    REPRODUCTIVE_MID = "reproductive_mid"
    REPRODUCTIVE_LATE = "reproductive_late"
    MATURITY = "maturity"


class NutrientType(str, Enum):
    """Nutrient types for modeling."""
    NITROGEN = "nitrogen"
    PHOSPHORUS = "phosphorus"
    POTASSIUM = "potassium"
    SULFUR = "sulfur"


class LossType(str, Enum):
    """Types of nutrient loss pathways."""
    LEACHING = "leaching"
    VOLATILIZATION = "volatilization"
    IMMOBILIZATION = "immobilization"
    DENITRIFICATION = "denitrification"
    RUNOFF = "runoff"


class SoilTexture(str, Enum):
    """Soil texture classifications."""
    SAND = "sand"
    LOAMY_SAND = "loamy_sand"
    SANDY_LOAM = "sandy_loam"
    LOAM = "loam"
    SILT_LOAM = "silt_loam"
    SILT = "silt"
    SANDY_CLAY_LOAM = "sandy_clay_loam"
    CLAY_LOAM = "clay_loam"
    SILTY_CLAY_LOAM = "silty_clay_loam"
    SANDY_CLAY = "sandy_clay"
    SILTY_CLAY = "silty_clay"
    CLAY = "clay"


class DrainageClass(str, Enum):
    """Soil drainage classifications."""
    VERY_POORLY_DRAINED = "very_poorly_drained"
    POORLY_DRAINED = "poorly_drained"
    SOMEWHAT_POORLY_DRAINED = "somewhat_poorly_drained"
    MODERATELY_WELL_DRAINED = "moderately_well_drained"
    WELL_DRAINED = "well_drained"
    SOMEWHAT_EXCESSIVELY_DRAINED = "somewhat_excessively_drained"
    EXCESSIVELY_DRAINED = "excessively_drained"


class FertilizerFormulation(str, Enum):
    """Fertilizer formulations affecting volatilization."""
    UREA = "urea"
    ANHYDROUS_AMMONIA = "anhydrous_ammonia"
    UAN_SOLUTION = "uan_solution"
    AMMONIUM_NITRATE = "ammonium_nitrate"
    AMMONIUM_SULFATE = "ammonium_sulfate"
    DAP = "dap"  # Diammonium phosphate
    MAP = "map"  # Monoammonium phosphate"
    ORGANIC = "organic"
    SLOW_RELEASE = "slow_release"


class ApplicationMethodType(str, Enum):
    """Fertilizer application methods."""
    BROADCAST = "broadcast"
    INCORPORATED = "incorporated"
    INJECTED = "injected"
    BANDED = "banded"
    FERTIGATION = "fertigation"
    FOLIAR = "foliar"


class SoilCharacteristics(BaseModel):
    """Soil physical and chemical characteristics for nutrient modeling."""

    texture: SoilTexture = Field(..., description="Soil texture class")
    drainage_class: DrainageClass = Field(..., description="Soil drainage classification")

    # Soil composition
    sand_percent: float = Field(..., ge=0.0, le=100.0, description="Sand percentage")
    silt_percent: float = Field(..., ge=0.0, le=100.0, description="Silt percentage")
    clay_percent: float = Field(..., ge=0.0, le=100.0, description="Clay percentage")

    # Soil properties
    organic_matter_percent: float = Field(..., ge=0.0, le=15.0, description="Organic matter content (%)")
    cec_meq_per_100g: float = Field(..., ge=1.0, le=50.0, description="Cation Exchange Capacity (meq/100g)")
    ph: float = Field(..., ge=4.0, le=9.0, description="Soil pH")
    bulk_density_g_cm3: Optional[float] = Field(None, ge=1.0, le=2.0, description="Bulk density (g/cm³)")

    # Moisture characteristics
    field_capacity_percent: Optional[float] = Field(None, ge=10.0, le=60.0, description="Field capacity (%)")
    wilting_point_percent: Optional[float] = Field(None, ge=5.0, le=30.0, description="Wilting point (%)")
    current_moisture_percent: Optional[float] = Field(None, ge=0.0, le=100.0, description="Current soil moisture (%)")

    @validator('clay_percent')
    def validate_texture_sum(cls, v, values):
        """Ensure sand + silt + clay = 100%."""
        if 'sand_percent' in values and 'silt_percent' in values:
            total = values['sand_percent'] + values['silt_percent'] + v
            if not (99.0 <= total <= 101.0):
                raise ValueError(f"Sand + Silt + Clay must equal 100%, got {total}%")
        return v


class WeatherConditions(BaseModel):
    """Weather conditions affecting nutrient dynamics."""

    # Temperature data
    temperature_f: float = Field(..., ge=-20.0, le=120.0, description="Temperature (°F)")
    temperature_c: Optional[float] = Field(None, description="Temperature (°C) - auto-calculated")

    # Humidity and precipitation
    relative_humidity_percent: float = Field(..., ge=0.0, le=100.0, description="Relative humidity (%)")
    rainfall_inches: float = Field(..., ge=0.0, le=20.0, description="Recent rainfall (inches)")
    rainfall_intensity: Optional[str] = Field(None, description="Rainfall intensity (light, moderate, heavy)")

    # Wind and evaporation
    wind_speed_mph: Optional[float] = Field(None, ge=0.0, le=100.0, description="Wind speed (mph)")
    evapotranspiration_inches: Optional[float] = Field(None, ge=0.0, le=1.0, description="Daily ET (inches)")

    # Time periods
    days_since_rain: Optional[int] = Field(None, ge=0, le=365, description="Days since last significant rain")
    days_to_next_rain: Optional[int] = Field(None, ge=0, le=30, description="Days until next predicted rain")

    @validator('temperature_c', always=True)
    def calculate_celsius(cls, v, values):
        """Auto-calculate Celsius from Fahrenheit if not provided."""
        if v is None and 'temperature_f' in values:
            return (values['temperature_f'] - 32.0) * 5.0 / 9.0
        return v


class CropNutrientRequirements(BaseModel):
    """Crop-specific nutrient requirements and growth parameters."""

    crop_type: CropType = Field(..., description="Crop type")
    growth_stage: GrowthStage = Field(..., description="Current growth stage")
    yield_goal_bu_acre: Optional[float] = Field(None, gt=0, description="Yield goal (bu/acre)")
    variety: Optional[str] = Field(None, description="Crop variety")

    # Total nutrient needs for target yield
    total_n_needed_lbs_acre: Optional[float] = Field(None, ge=0.0, le=500.0, description="Total N needed (lbs/acre)")
    total_p2o5_needed_lbs_acre: Optional[float] = Field(None, ge=0.0, le=200.0, description="Total P2O5 needed (lbs/acre)")
    total_k2o_needed_lbs_acre: Optional[float] = Field(None, ge=0.0, le=300.0, description="Total K2O needed (lbs/acre)")

    # Days in growth cycle
    days_after_planting: Optional[int] = Field(None, ge=0, le=365, description="Days after planting")
    total_growing_days: Optional[int] = Field(None, ge=30, le=365, description="Total growing season days")


class ApplicationDetails(BaseModel):
    """Fertilizer application details."""

    application_method: ApplicationMethodType = Field(..., description="Application method")
    fertilizer_formulation: FertilizerFormulation = Field(..., description="Fertilizer formulation")

    # Application timing
    application_date: Optional[date] = Field(None, description="Application date")
    hours_since_application: Optional[float] = Field(None, ge=0.0, description="Hours since application")

    # Application details
    incorporation_depth_inches: Optional[float] = Field(None, ge=0.0, le=12.0, description="Incorporation depth")
    hours_until_incorporation: Optional[float] = Field(None, ge=0.0, le=168.0, description="Hours until incorporation")

    # Application rates
    n_applied_lbs_acre: float = Field(..., ge=0.0, le=400.0, description="N applied (lbs/acre)")
    p2o5_applied_lbs_acre: Optional[float] = Field(None, ge=0.0, le=200.0, description="P2O5 applied (lbs/acre)")
    k2o_applied_lbs_acre: Optional[float] = Field(None, ge=0.0, le=300.0, description="K2O applied (lbs/acre)")


class NutrientUptakeRequest(BaseModel):
    """Request for nutrient uptake and loss predictions."""

    request_id: str = Field(..., description="Unique request identifier")

    # Core inputs
    crop_requirements: CropNutrientRequirements = Field(..., description="Crop requirements")
    soil_characteristics: SoilCharacteristics = Field(..., description="Soil characteristics")
    weather_conditions: WeatherConditions = Field(..., description="Weather conditions")
    application_details: ApplicationDetails = Field(..., description="Application details")

    # Optional context
    previous_applications: Optional[List[ApplicationDetails]] = Field(None, description="Previous applications this season")
    residue_cn_ratio: Optional[float] = Field(None, ge=10.0, le=100.0, description="Crop residue C:N ratio")
    microbial_activity_level: Optional[str] = Field(None, description="Microbial activity (low, medium, high)")


class UptakeCurvePoint(BaseModel):
    """Single point on a nutrient uptake curve."""

    growth_stage: GrowthStage = Field(..., description="Growth stage")
    days_after_planting: int = Field(..., ge=0, description="Days after planting")
    cumulative_uptake_percent: float = Field(..., ge=0.0, le=100.0, description="Cumulative uptake (%)")
    daily_uptake_rate_lbs_acre: float = Field(..., ge=0.0, description="Daily uptake rate (lbs/acre/day)")


class NutrientUptakeCurve(BaseModel):
    """Complete nutrient uptake curve for a crop."""

    nutrient_type: NutrientType = Field(..., description="Nutrient type")
    crop_type: CropType = Field(..., description="Crop type")
    uptake_points: List[UptakeCurvePoint] = Field(..., description="Uptake curve points")
    peak_uptake_stage: GrowthStage = Field(..., description="Growth stage with peak uptake")
    peak_uptake_rate_lbs_acre_day: float = Field(..., ge=0.0, description="Peak daily uptake (lbs/acre/day)")
    total_uptake_lbs_acre: float = Field(..., ge=0.0, description="Total seasonal uptake (lbs/acre)")


class LossPrediction(BaseModel):
    """Prediction of nutrient loss via specific pathway."""

    loss_type: LossType = Field(..., description="Type of nutrient loss")
    nutrient_type: NutrientType = Field(..., description="Nutrient affected")

    # Loss amounts
    loss_amount_lbs_acre: float = Field(..., ge=0.0, description="Predicted loss (lbs/acre)")
    loss_percent: float = Field(..., ge=0.0, le=100.0, description="Loss as % of applied")

    # Risk assessment
    risk_level: str = Field(..., description="Risk level (low, moderate, high, very_high)")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Prediction confidence")

    # Contributing factors
    primary_factors: List[str] = Field(..., description="Primary factors driving loss")
    secondary_factors: List[str] = Field(default=[], description="Secondary contributing factors")

    # Time-based predictions
    loss_timeline_days: Optional[int] = Field(None, ge=1, le=90, description="Days over which loss occurs")
    peak_loss_period_days: Optional[str] = Field(None, description="Period of peak loss (e.g., '1-3 days')")

    # Mitigation
    mitigation_recommendations: List[str] = Field(default=[], description="Recommendations to reduce loss")
    mitigation_potential_percent: Optional[float] = Field(None, ge=0.0, le=100.0, description="Potential loss reduction (%)")


class NutrientEfficiencyAnalysis(BaseModel):
    """Overall nutrient use efficiency analysis."""

    nutrient_type: NutrientType = Field(..., description="Nutrient analyzed")

    # Applied amounts
    applied_lbs_acre: float = Field(..., ge=0.0, description="Total applied (lbs/acre)")

    # Uptake and losses
    crop_uptake_lbs_acre: float = Field(..., ge=0.0, description="Crop uptake (lbs/acre)")
    total_losses_lbs_acre: float = Field(..., ge=0.0, description="Total losses (lbs/acre)")
    remaining_in_soil_lbs_acre: float = Field(..., ge=0.0, description="Remaining in soil (lbs/acre)")

    # Efficiency metrics
    uptake_efficiency_percent: float = Field(..., ge=0.0, le=100.0, description="Uptake efficiency (%)")
    recovery_efficiency_percent: float = Field(..., ge=0.0, le=100.0, description="Recovery efficiency (%)")
    agronomic_efficiency: Optional[float] = Field(None, description="Agronomic efficiency (bu yield/lb N)")

    # Loss breakdown
    loss_breakdown: Dict[str, float] = Field(..., description="Loss by pathway (lbs/acre)")
    loss_breakdown_percent: Dict[str, float] = Field(..., description="Loss by pathway (%)")


class NutrientFatePrediction(BaseModel):
    """Comprehensive nutrient fate prediction."""

    request_id: str = Field(..., description="Original request ID")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")

    # Uptake predictions
    uptake_curves: List[NutrientUptakeCurve] = Field(..., description="Nutrient uptake curves")
    current_uptake_stage: GrowthStage = Field(..., description="Current uptake stage")
    expected_uptake_next_30_days_lbs_acre: Dict[str, float] = Field(..., description="Expected uptake by nutrient")

    # Loss predictions
    loss_predictions: List[LossPrediction] = Field(..., description="All loss predictions")
    total_loss_risk: str = Field(..., description="Overall loss risk (low, moderate, high, very_high)")

    # Efficiency analysis
    efficiency_analyses: List[NutrientEfficiencyAnalysis] = Field(..., description="Efficiency by nutrient")
    overall_efficiency_score: float = Field(..., ge=0.0, le=1.0, description="Overall efficiency score")

    # Recommendations
    optimization_recommendations: List[str] = Field(..., description="Timing/application optimization recommendations")
    monitoring_recommendations: List[str] = Field(default=[], description="Monitoring recommendations")

    # Confidence
    overall_confidence: float = Field(..., ge=0.0, le=1.0, description="Overall prediction confidence")
    confidence_factors: Dict[str, float] = Field(..., description="Confidence breakdown by factor")

    # Agricultural context
    agricultural_sources: List[str] = Field(default=[], description="Supporting agricultural sources")
    assumptions: List[str] = Field(default=[], description="Key modeling assumptions")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }


class LeachingModelInputs(BaseModel):
    """Specific inputs for leaching model."""

    soil_characteristics: SoilCharacteristics = Field(..., description="Soil characteristics")
    weather_conditions: WeatherConditions = Field(..., description="Weather conditions")
    nutrient_type: NutrientType = Field(..., description="Nutrient to model")
    applied_amount_lbs_acre: float = Field(..., ge=0.0, description="Applied amount (lbs/acre)")
    days_since_application: float = Field(..., ge=0.0, description="Days since application")


class VolatilizationModelInputs(BaseModel):
    """Specific inputs for volatilization model."""

    fertilizer_formulation: FertilizerFormulation = Field(..., description="Fertilizer formulation")
    application_method: ApplicationMethodType = Field(..., description="Application method")
    weather_conditions: WeatherConditions = Field(..., description="Weather conditions")
    soil_characteristics: SoilCharacteristics = Field(..., description="Soil characteristics")
    applied_n_lbs_acre: float = Field(..., ge=0.0, description="Applied N (lbs/acre)")
    hours_since_application: float = Field(..., ge=0.0, description="Hours since application")
    hours_until_incorporation_or_rain: Optional[float] = Field(None, description="Hours until incorporation/rain")


class ImmobilizationModelInputs(BaseModel):
    """Specific inputs for immobilization model."""

    soil_characteristics: SoilCharacteristics = Field(..., description="Soil characteristics")
    weather_conditions: WeatherConditions = Field(..., description="Weather conditions")
    residue_cn_ratio: float = Field(..., ge=10.0, le=100.0, description="Crop residue C:N ratio")
    residue_amount_tons_acre: Optional[float] = Field(None, ge=0.0, le=20.0, description="Residue amount (tons/acre)")
    applied_n_lbs_acre: float = Field(..., ge=0.0, description="Applied N (lbs/acre)")
    microbial_activity_level: str = Field(..., description="Microbial activity (low, medium, high)")

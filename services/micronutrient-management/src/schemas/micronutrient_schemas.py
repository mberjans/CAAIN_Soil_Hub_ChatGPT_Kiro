from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime, date
from typing import Dict, Any

class MicronutrientType(str, Enum):
    BORON = "Boron"
    COPPER = "Copper"
    IRON = "Iron"
    MANGANESE = "Manganese"
    MOLYBDENUM = "Molybdenum"
    ZINC = "Zinc"
    CHLORINE = "Chlorine"
    NICKEL = "Nickel"

class ApplicationMethod(str, Enum):
    SOIL_APPLICATION = "Soil Application"
    FOLIAR_APPLICATION = "Foliar Application" 
    SEED_TREATMENT = "Seed Treatment"
    FERTIGATION = "Fertigation"
    BROADCAST = "Broadcast"
    BANDED = "Banded"

class WeatherCondition(str, Enum):
    CLEAR = "Clear"
    RAIN = "Rain"
    WINDY = "Windy"
    HOT = "Hot"
    COLD = "Cold"

class GrowthStage(str, Enum):
    SEEDLING = "Seedling"
    VEGETATIVE = "Vegetative"
    FLORING = "Flowering"
    FRUITING = "Fruiting"
    MATURITY = "Maturity"

class TimingRecommendationType(str, Enum):
    IMMEDIATE = "Immediate"
    SHORT_TERM = "Short-term (1-2 weeks)"
    MEDIUM_TERM = "Medium-term (2-4 weeks)"
    LONG_TERM = "Long-term (1-2 months)"
    SEASONAL = "Seasonal Application"

class MicronutrientLevel(BaseModel):
    nutrient_type: MicronutrientType = Field(..., description="Type of micronutrient")
    level_ppm: float = Field(..., ge=0, description="Current level in parts per million (ppm)")
    unit: str = Field("ppm", description="Unit of measurement for the level")

class RecommendationPriority(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    OPTIMAL = "Optimal"

class EquipmentAvailability(BaseModel):
    sprayer: bool = Field(default=False, description="Whether sprayer equipment is available for foliar applications")
    fertilizer_applicator: bool = Field(default=False, description="Whether fertilizer application equipment is available for soil applications")
    irrigation_system: bool = Field(default=False, description="Whether irrigation system is available for fertigation")
    seeding_equipment: bool = Field(default=False, description="Whether seeding equipment is available for seed treatment")

class FieldCondition(BaseModel):
    moisture: str = Field(..., description="Current field moisture level (dry, adequate, wet)")
    temperature: float = Field(..., description="Current field temperature in Fahrenheit")
    weather_forecast: List[Dict[str, Any]] = Field(default_factory=list, description="Weather forecast for the next few days")
    soil_compaction: Optional[bool] = Field(None, description="Whether soil compaction is present")

class ApplicationMethodRequest(BaseModel):
    crop_type: str = Field(..., description="Type of crop being grown")
    growth_stage: Optional[str] = Field(None, description="Current growth stage of the crop")
    deficiency_severity: RecommendationPriority = Field(..., description="Severity of nutrient deficiency (Critical, High, Medium, etc.)")
    equipment_availability: EquipmentAvailability = Field(..., description="Available equipment for application")
    field_conditions: FieldCondition = Field(..., description="Current field conditions")
    nutrient_type: MicronutrientType = Field(..., description="Type of micronutrient being applied")
    recommended_amount: float = Field(..., ge=0, description="Amount of nutrient to apply")

class ApplicationMethodRecommendation(BaseModel):
    method: ApplicationMethod = Field(..., description="Recommended application method")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence score for the recommendation (0-1)")
    timing_recommendation: TimingRecommendationType = Field(..., description="Recommended timing for application")
    reason: str = Field(..., description="Reason for choosing this application method")
    equipment_required: List[str] = Field(..., description="Equipment required for this application method")
    field_conditions_suitable: bool = Field(..., description="Whether current field conditions are suitable for this method")
    alternative_methods: List[ApplicationMethod] = Field(default_factory=list, description="Alternative application methods")

class TimingRecommendationRequest(BaseModel):
    crop_type: str = Field(..., description="Type of crop being grown")
    growth_stage: Optional[str] = Field(None, description="Current growth stage of the crop")
    nutrient_uptake_pattern: str = Field(..., description="Nutrient uptake pattern for the specific nutrient and crop")
    weather_conditions: WeatherCondition = Field(..., description="Current weather conditions")
    nutrient_type: MicronutrientType = Field(..., description="Type of micronutrient being applied")
    application_method: ApplicationMethod = Field(..., description="Planned application method")
    field_conditions: FieldCondition = Field(..., description="Current field conditions")

class TimingRecommendation(BaseModel):
    timing: TimingRecommendationType = Field(..., description="Recommended timing for application")
    optimal_window_start: Optional[datetime] = Field(None, description="Optimal start time for application window")
    optimal_window_end: Optional[datetime] = Field(None, description="Optimal end time for application window")
    reason: str = Field(..., description="Reason for choosing this timing")
    weather_considerations: List[str] = Field(default_factory=list, description="Weather considerations for timing")
    compatibility_notes: List[str] = Field(default_factory=list, description="Notes about compatibility with other inputs")
    expected_efficacy: float = Field(..., ge=0, le=1, description="Expected efficacy of application at this timing (0-1)")

class MicronutrientRecommendation(BaseModel):
    nutrient_type: MicronutrientType = Field(..., description="Type of micronutrient")
    priority: RecommendationPriority = Field(..., description="Priority level for the recommendation")
    recommended_amount: Optional[float] = Field(None, ge=0, description="Recommended amount to apply")
    unit: Optional[str] = Field(None, description="Unit of measurement for the recommended amount (e.g., kg/ha, lb/acre)")
    application_method: Optional[str] = Field(None, description="Suggested application method (e.g., foliar, soil)")
    justification: str = Field(..., description="Explanation for the recommendation")
    crop_impact: Optional[str] = Field(None, description="Expected impact on crop health/yield")

class MicronutrientRecommendationRequest(BaseModel):
    farm_location_id: str = Field(..., description="ID of the farm location")
    crop_type: str = Field(..., description="Type of crop being grown")
    growth_stage: Optional[str] = Field(None, description="Current growth stage of the crop")
    soil_type: str = Field(..., description="Soil type (e.g., sandy, clay, loam)")
    soil_ph: float = Field(..., ge=0, le=14, description="Current soil pH")
    organic_matter_percent: float = Field(..., ge=0, le=100, description="Organic matter percentage in soil")
    current_micronutrient_levels: List[MicronutrientLevel] = Field(..., description="Current levels of micronutrients in the soil")
    yield_goal_bushels_per_acre: Optional[float] = Field(None, ge=0, description="Target yield goal in bushels per acre")

class MicronutrientRecommendationResponse(BaseModel):
    request_id: str = Field(..., description="Unique ID for the recommendation request")
    recommendations: List[MicronutrientRecommendation] = Field(..., description="List of micronutrient recommendations")
    overall_status: str = Field(..., description="Overall status of micronutrient levels (e.g., 'Deficient', 'Optimal', 'Excess')")
    warnings: List[str] = Field(default_factory=list, description="List of warnings or alerts")
    metadata: dict = Field(default_factory=dict, description="Additional metadata about the recommendation")

class CropDetails(BaseModel):
    crop_type: str = Field(..., description="Type of crop being grown")
    expected_market_price_per_unit: float = Field(..., description="Expected market price per unit of yield")
    yield_unit: str = Field(default="bushels", description="Unit of yield (e.g., bushels, tons)")


class MicronutrientApplicationDetails(BaseModel):
    micronutrient_type: MicronutrientType = Field(..., description="Type of micronutrient being applied")
    application_rate_per_acre: float = Field(..., ge=0, description="Application rate per acre")
    cost_per_unit: float = Field(..., ge=0, description="Cost per unit of micronutrient")
    total_acres_applied: float = Field(..., ge=0, description="Total acres being treated")


class PredictedYieldResponse(BaseModel):
    predicted_yield_per_acre: float = Field(..., description="Predicted yield per acre with application")
    baseline_yield_per_acre: float = Field(..., description="Baseline yield per acre without application")


class FarmContext(BaseModel):
    farm_location_id: str = Field(..., description="ID of the farm location")


class EconomicReturnPredictionRequest(BaseModel):
    farm_context: FarmContext = Field(..., description="Contextual information about the farm")
    micronutrient_application: MicronutrientApplicationDetails = Field(..., description="Details about the micronutrient application")
    predicted_yield_response: PredictedYieldResponse = Field(..., description="Predicted yield response data")
    crop_details: CropDetails = Field(..., description="Details about the crop")


class YieldPredictionRequest(BaseModel):
    farm_context: FarmContext = Field(..., description="Contextual information about the farm")
    crop_details: CropDetails = Field(..., description="Detailed information about the crop being grown")
    micronutrient_application: MicronutrientApplicationDetails = Field(..., description="Details about the micronutrient application")


class YieldPredictionResponse(BaseModel):
    predicted_yield_per_acre: float = Field(..., description="Predicted yield per acre with application")
    predicted_total_yield: float = Field(..., description="Total predicted yield")
    baseline_yield_per_acre: float = Field(..., description="Baseline yield per acre without application")
    yield_increase_percent: float = Field(..., description="Percentage yield increase due to application")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence score of the prediction (0-1)")
    explanation: str = Field(..., description="Human-readable explanation of the prediction")


class EconomicReturnPredictionResponse(BaseModel):
    total_micronutrient_cost: float = Field(..., description="Total cost of the micronutrient application")
    additional_revenue_from_yield_increase: float = Field(..., description="Additional revenue from yield increase")
    net_economic_return: float = Field(..., description="Net economic return (revenue - cost)")
    roi_percentage: float = Field(..., description="Return on investment as a percentage")
    break_even_yield_increase_per_acre: float = Field(..., description="Break-even yield increase required per acre")
    explanation: str = Field(..., description="Human-readable explanation of the economic analysis")


class ApplicationMethodAndTimingResponse(BaseModel):
    request_id: str = Field(..., description="Unique ID for the request")
    application_method: ApplicationMethodRecommendation = Field(..., description="Recommended application method")
    timing: TimingRecommendation = Field(..., description="Recommended timing for application")
    economic_efficiency: float = Field(..., ge=0, le=1, description="Economic efficiency score of the recommendation (0-1)")
    risk_assessment: str = Field(..., description="Risk assessment for the application")
    notes: List[str] = Field(default_factory=list, description="Additional notes and considerations")
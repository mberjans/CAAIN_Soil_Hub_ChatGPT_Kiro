"""
Drought Management Data Models

Pydantic models for drought assessment, conservation practices,
and monitoring data structures.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal
from enum import Enum

# Enums for type safety
class DroughtRiskLevel(str, Enum):
    """Drought risk levels."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"
    EXTREME = "extreme"

class SoilMoistureLevel(str, Enum):
    """Soil moisture levels."""
    VERY_DRY = "very_dry"
    DRY = "dry"
    ADEQUATE = "adequate"
    MOIST = "moist"
    SATURATED = "saturated"

class ConservationPracticeType(str, Enum):
    """Types of conservation practices."""
    COVER_CROPS = "cover_crops"
    NO_TILL = "no_till"
    MULCHING = "mulching"
    IRRIGATION_EFFICIENCY = "irrigation_efficiency"
    SOIL_AMENDMENTS = "soil_amendments"
    WATER_HARVESTING = "water_harvesting"
    CROP_ROTATION = "crop_rotation"
    TERRAIN_MODIFICATION = "terrain_modification"

class SoilHealthImpact(str, Enum):
    """Soil health impact levels."""
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    HIGHLY_POSITIVE = "highly_positive"

class EquipmentRequirement(BaseModel):
    """Equipment requirement for conservation practices."""
    equipment_type: str = Field(..., description="Type of equipment required")
    equipment_name: str = Field(..., description="Specific equipment name")
    availability: bool = Field(..., description="Whether equipment is available")
    rental_cost_per_day: Optional[Decimal] = Field(None, description="Daily rental cost")
    purchase_cost: Optional[Decimal] = Field(None, description="Purchase cost")

class ConservationPractice(BaseModel):
    """Conservation practice model."""
    practice_id: UUID = Field(..., description="Unique practice identifier")
    practice_name: str = Field(..., description="Name of the conservation practice")
    practice_type: ConservationPracticeType = Field(..., description="Type of conservation practice")
    description: str = Field(..., description="Detailed description of the practice")
    implementation_cost: Decimal = Field(..., description="Implementation cost per acre")
    water_savings_percent: float = Field(..., ge=0, le=100, description="Percentage of water savings")
    soil_health_impact: SoilHealthImpact = Field(..., description="Impact on soil health")
    equipment_requirements: List[EquipmentRequirement] = Field(default_factory=list)
    implementation_time_days: int = Field(..., ge=1, description="Days required for implementation")
    maintenance_cost_per_year: Decimal = Field(..., description="Annual maintenance cost per acre")
    effectiveness_rating: float = Field(..., ge=0, le=10, description="Effectiveness rating (0-10)")
    
    @validator('water_savings_percent')
    def validate_water_savings(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Water savings percentage must be between 0 and 100')
        return v

class WeatherImpact(BaseModel):
    """Weather impact assessment."""
    temperature_impact: str = Field(..., description="Temperature impact assessment")
    precipitation_impact: str = Field(..., description="Precipitation impact assessment")
    humidity_impact: str = Field(..., description="Humidity impact assessment")
    wind_impact: str = Field(..., description="Wind impact assessment")
    forecast_confidence: float = Field(..., ge=0, le=1, description="Forecast confidence level")
    risk_factors: List[str] = Field(default_factory=list, description="Identified risk factors")

class SoilMoistureStatus(BaseModel):
    """Soil moisture status model."""
    field_id: UUID = Field(..., description="Field identifier")
    assessment_date: datetime = Field(default_factory=datetime.utcnow)
    surface_moisture_percent: float = Field(..., ge=0, le=100, description="Surface moisture percentage")
    deep_moisture_percent: float = Field(..., ge=0, le=100, description="Deep soil moisture percentage")
    available_water_capacity: float = Field(..., ge=0, description="Available water capacity in inches")
    moisture_level: SoilMoistureLevel = Field(..., description="Overall moisture level")
    irrigation_recommendation: str = Field(..., description="Irrigation recommendation")
    days_until_critical: Optional[int] = Field(None, description="Days until critical moisture level")
    
    @validator('surface_moisture_percent', 'deep_moisture_percent')
    def validate_moisture_percent(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Moisture percentage must be between 0 and 100')
        return v

class RecommendedAction(BaseModel):
    """Recommended action for drought management."""
    action_id: UUID = Field(..., description="Unique action identifier")
    action_type: str = Field(..., description="Type of recommended action")
    priority: str = Field(..., description="Priority level (high, medium, low)")
    description: str = Field(..., description="Detailed action description")
    implementation_timeline: str = Field(..., description="Implementation timeline")
    expected_benefit: str = Field(..., description="Expected benefit description")
    cost_estimate: Decimal = Field(..., description="Estimated cost")
    resources_required: List[str] = Field(default_factory=list, description="Required resources")

class WaterSavingsPotential(BaseModel):
    """Water savings potential assessment."""
    current_water_usage: Decimal = Field(..., description="Current water usage per acre")
    potential_savings: Decimal = Field(..., description="Potential water savings per acre")
    savings_percentage: float = Field(..., ge=0, le=100, description="Percentage of water savings")
    cost_savings_per_year: Decimal = Field(..., description="Annual cost savings")
    implementation_cost: Decimal = Field(..., description="Implementation cost")
    payback_period_years: float = Field(..., description="Payback period in years")
    
    @validator('savings_percentage')
    def validate_savings_percentage(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Savings percentage must be between 0 and 100')
        return v

class DroughtAssessment(BaseModel):
    """Comprehensive drought assessment model."""
    assessment_id: UUID = Field(..., description="Unique assessment identifier")
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    assessment_date: datetime = Field(default_factory=datetime.utcnow)
    drought_risk_level: DroughtRiskLevel = Field(..., description="Overall drought risk level")
    soil_moisture_status: SoilMoistureStatus = Field(..., description="Current soil moisture status")
    weather_forecast_impact: WeatherImpact = Field(..., description="Weather forecast impact")
    current_practices: List[ConservationPractice] = Field(default_factory=list)
    recommended_actions: List[RecommendedAction] = Field(default_factory=list)
    water_savings_potential: WaterSavingsPotential = Field(..., description="Water savings potential")
    confidence_score: float = Field(..., ge=0, le=1, description="Assessment confidence score")
    
    @validator('confidence_score')
    def validate_confidence_score(cls, v):
        if v < 0 or v > 1:
            raise ValueError('Confidence score must be between 0 and 1')
        return v

class DroughtRiskAssessment(BaseModel):
    """Drought risk assessment model."""
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    assessment_date: date = Field(default_factory=date.today)
    risk_level: DroughtRiskLevel = Field(..., description="Current drought risk level")
    risk_factors: List[str] = Field(default_factory=list, description="Identified risk factors")
    mitigation_strategies: List[str] = Field(default_factory=list, description="Recommended mitigation strategies")
    monitoring_recommendations: List[str] = Field(default_factory=list, description="Monitoring recommendations")
    next_assessment_date: date = Field(..., description="Recommended next assessment date")

# Request Models
class DroughtAssessmentRequest(BaseModel):
    """Request model for drought assessment."""
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    field_id: Optional[UUID] = Field(None, description="Specific field identifier")
    crop_type: str = Field(..., description="Type of crop")
    growth_stage: str = Field(..., description="Current growth stage")
    soil_type: str = Field(..., description="Soil type")
    irrigation_available: bool = Field(False, description="Whether irrigation is available")
    include_forecast: bool = Field(True, description="Include weather forecast analysis")
    assessment_depth_days: int = Field(30, ge=1, le=365, description="Assessment depth in days")

class ConservationPracticeRequest(BaseModel):
    """Request model for conservation practice recommendations."""
    field_id: UUID = Field(..., description="Field identifier")
    soil_type: str = Field(..., description="Soil type")
    slope_percent: float = Field(..., ge=0, le=100, description="Field slope percentage")
    drainage_class: str = Field(..., description="Drainage classification")
    current_practices: List[str] = Field(default_factory=list, description="Current conservation practices")
    available_equipment: List[str] = Field(default_factory=list, description="Available equipment")
    budget_constraint: Optional[Decimal] = Field(None, description="Budget constraint per acre")
    implementation_timeline: str = Field("immediate", description="Implementation timeline preference")

class DroughtMonitoringRequest(BaseModel):
    """Request model for drought monitoring setup."""
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    field_ids: List[UUID] = Field(..., description="Field identifiers to monitor")
    monitoring_frequency: str = Field("daily", description="Monitoring frequency")
    alert_thresholds: Dict[str, float] = Field(default_factory=dict, description="Alert thresholds")
    notification_preferences: Dict[str, Any] = Field(default_factory=dict, description="Notification preferences")
    integration_services: List[str] = Field(default_factory=list, description="External service integrations")

class WaterSavingsRequest(BaseModel):
    """Request model for water savings calculation."""
    field_id: UUID = Field(..., description="Field identifier")
    current_water_usage: Decimal = Field(..., description="Current water usage per acre")
    proposed_practices: List[ConservationPractice] = Field(..., description="Proposed conservation practices")
    implementation_timeline: str = Field(..., description="Implementation timeline")
    cost_constraints: Optional[Decimal] = Field(None, description="Cost constraints")
    effectiveness_assumptions: Dict[str, float] = Field(default_factory=dict, description="Effectiveness assumptions")

# Response Models
class DroughtAssessmentResponse(BaseModel):
    """Response model for drought assessment."""
    assessment: DroughtAssessment = Field(..., description="Complete drought assessment")
    recommendations: List[RecommendedAction] = Field(..., description="Prioritized recommendations")
    next_steps: List[str] = Field(..., description="Recommended next steps")
    monitoring_schedule: Dict[str, Any] = Field(..., description="Recommended monitoring schedule")

class ConservationPracticeResponse(BaseModel):
    """Response model for conservation practice recommendations."""
    practice: ConservationPractice = Field(..., description="Conservation practice details")
    implementation_plan: Dict[str, Any] = Field(..., description="Implementation plan")
    expected_benefits: Dict[str, Any] = Field(..., description="Expected benefits")
    cost_benefit_analysis: Dict[str, Any] = Field(..., description="Cost-benefit analysis")

class DroughtMonitoringResponse(BaseModel):
    """Response model for drought monitoring."""
    monitoring_id: UUID = Field(..., description="Monitoring configuration identifier")
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    status: str = Field(..., description="Current monitoring status")
    active_alerts: List[Dict[str, Any]] = Field(default_factory=list, description="Active alerts")
    monitoring_data: Dict[str, Any] = Field(..., description="Current monitoring data")
    next_check_time: datetime = Field(..., description="Next scheduled check time")

class WaterSavingsResponse(BaseModel):
    """Response model for water savings calculation."""
    field_id: UUID = Field(..., description="Field identifier")
    current_usage: Decimal = Field(..., description="Current water usage")
    projected_savings: Decimal = Field(..., description="Projected water savings")
    savings_percentage: float = Field(..., description="Percentage of savings")
    cost_benefit_analysis: Dict[str, Any] = Field(..., description="Cost-benefit analysis")
    implementation_timeline: Dict[str, Any] = Field(..., description="Implementation timeline")
    monitoring_recommendations: List[str] = Field(..., description="Monitoring recommendations")

# Irrigation Management Models
class IrrigationSystemType(str, Enum):
    """Types of irrigation systems."""
    SPRINKLER = "sprinkler"
    DRIP = "drip"
    FLOOD = "flood"
    CENTER_PIVOT = "center_pivot"
    LINEAR_MOVE = "linear_move"
    HAND_MOVE = "hand_move"
    MICRO_SPRAY = "micro_spray"
    SUB_SURFACE = "sub_surface"

class WaterSourceType(str, Enum):
    """Types of water sources."""
    WELL = "well"
    SURFACE_WATER = "surface_water"
    MUNICIPAL = "municipal"
    RECYCLED = "recycled"
    RAINWATER = "rainwater"
    SPRING = "spring"

class IrrigationEfficiencyLevel(str, Enum):
    """Irrigation efficiency levels."""
    LOW = "low"  # < 60%
    MODERATE = "moderate"  # 60-80%
    HIGH = "high"  # 80-90%
    EXCELLENT = "excellent"  # > 90%

class IrrigationSystemAssessment(BaseModel):
    """Assessment of irrigation system performance."""
    system_type: IrrigationSystemType = Field(..., description="Type of irrigation system")
    current_efficiency: float = Field(..., ge=0, le=1, description="Current system efficiency")
    efficiency_level: IrrigationEfficiencyLevel = Field(..., description="Efficiency level classification")
    water_distribution_uniformity: float = Field(..., ge=0, le=1, description="Water distribution uniformity")
    pressure_consistency: float = Field(..., ge=0, le=1, description="Pressure consistency across field")
    coverage_area_percent: float = Field(..., ge=0, le=100, description="Coverage area percentage")
    maintenance_status: str = Field(..., description="Current maintenance status")
    age_years: int = Field(..., ge=0, description="Age of irrigation system in years")
    estimated_water_loss_percent: float = Field(..., ge=0, le=100, description="Estimated water loss percentage")
    energy_efficiency_score: float = Field(..., ge=0, le=1, description="Energy efficiency score")
    overall_score: float = Field(..., ge=0, le=100, description="Overall system score")

class WaterSourceAssessment(BaseModel):
    """Assessment of water source capacity and quality."""
    source_type: WaterSourceType = Field(..., description="Type of water source")
    available_capacity_gpm: float = Field(..., ge=0, description="Available capacity in gallons per minute")
    water_quality_score: float = Field(..., ge=0, le=1, description="Water quality score")
    reliability_score: float = Field(..., ge=0, le=1, description="Reliability score")
    cost_per_gallon: Decimal = Field(..., description="Cost per gallon of water")
    seasonal_variation_percent: float = Field(..., ge=0, le=100, description="Seasonal variation percentage")
    sustainability_score: float = Field(..., ge=0, le=1, description="Sustainability score")
    regulatory_compliance: bool = Field(..., description="Regulatory compliance status")
    pumping_capacity_gpm: float = Field(..., ge=0, description="Effective pumping capacity")
    storage_capacity_gallons: float = Field(..., ge=0, description="Storage capacity in gallons")

class IrrigationConstraint(BaseModel):
    """Constraint affecting irrigation operations."""
    constraint_type: str = Field(..., description="Type of constraint")
    description: str = Field(..., description="Constraint description")
    impact_level: str = Field(..., description="Impact level (low, medium, high, critical)")
    mitigation_options: List[str] = Field(..., description="Available mitigation options")
    cost_impact: Decimal = Field(..., description="Cost impact of constraint")
    timeline_impact_days: int = Field(..., ge=0, description="Timeline impact in days")

class IrrigationOptimization(BaseModel):
    """Irrigation optimization recommendations."""
    optimization_type: str = Field(..., description="Type of optimization")
    description: str = Field(..., description="Optimization description")
    potential_water_savings_percent: float = Field(..., ge=0, le=100, description="Potential water savings percentage")
    potential_cost_savings_per_year: Decimal = Field(..., description="Potential annual cost savings")
    implementation_cost: Decimal = Field(..., description="Implementation cost")
    payback_period_years: float = Field(..., ge=0, description="Payback period in years")
    implementation_timeline_days: int = Field(..., ge=0, description="Implementation timeline in days")
    priority_level: str = Field(..., description="Priority level (high, medium, low)")
    equipment_requirements: List[EquipmentRequirement] = Field(default_factory=list, description="Required equipment")

# Irrigation Management Request Models
class IrrigationAssessmentRequest(BaseModel):
    """Request model for irrigation system assessment."""
    field_id: UUID = Field(..., description="Field identifier")
    system_type: IrrigationSystemType = Field(..., description="Type of irrigation system")
    system_age_years: int = Field(..., ge=0, description="Age of irrigation system")
    maintenance_history: Dict[str, Any] = Field(default_factory=dict, description="Maintenance history data")
    field_characteristics: Dict[str, Any] = Field(..., description="Field characteristics")
    water_source_data: Dict[str, Any] = Field(..., description="Water source information")
    operational_constraints: Dict[str, Any] = Field(default_factory=dict, description="Operational constraints")

class IrrigationScheduleRequest(BaseModel):
    """Request model for irrigation schedule generation."""
    field_id: UUID = Field(..., description="Field identifier")
    crop_type: str = Field(..., description="Type of crop")
    growth_stage: str = Field(..., description="Current growth stage")
    soil_moisture_data: Dict[str, Any] = Field(..., description="Current soil moisture data")
    weather_forecast: List[Dict[str, Any]] = Field(..., description="Weather forecast data")
    irrigation_system: IrrigationSystemAssessment = Field(..., description="Irrigation system assessment")
    water_source: WaterSourceAssessment = Field(..., description="Water source assessment")

class IrrigationOptimizationRequest(BaseModel):
    """Request model for irrigation optimization."""
    field_id: UUID = Field(..., description="Field identifier")
    current_assessment: IrrigationSystemAssessment = Field(..., description="Current irrigation assessment")
    water_source_assessment: WaterSourceAssessment = Field(..., description="Water source assessment")
    field_characteristics: Dict[str, Any] = Field(..., description="Field characteristics")
    budget_constraints: Optional[Decimal] = Field(None, description="Budget constraints")
    optimization_goals: List[str] = Field(default_factory=list, description="Optimization goals")

# Irrigation Management Response Models
class IrrigationAssessmentResponse(BaseModel):
    """Response model for irrigation system assessment."""
    field_id: UUID = Field(..., description="Field identifier")
    system_assessment: IrrigationSystemAssessment = Field(..., description="System assessment results")
    water_source_assessment: WaterSourceAssessment = Field(..., description="Water source assessment results")
    constraints: List[IrrigationConstraint] = Field(..., description="Identified constraints")
    recommendations: List[str] = Field(..., description="General recommendations")
    assessment_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Assessment timestamp")

class IrrigationOptimizationResponse(BaseModel):
    """Response model for irrigation optimization."""
    field_id: UUID = Field(..., description="Field identifier")
    optimizations: List[IrrigationOptimization] = Field(..., description="Optimization recommendations")
    total_potential_savings: Dict[str, Any] = Field(..., description="Total potential savings")
    implementation_priority: List[str] = Field(..., description="Implementation priority order")
    cost_benefit_summary: Dict[str, Any] = Field(..., description="Cost-benefit summary")
    optimization_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Optimization timestamp")

class IrrigationScheduleResponse(BaseModel):
    """Response model for irrigation schedule."""
    field_id: UUID = Field(..., description="Field identifier")
    schedule: Dict[str, Any] = Field(..., description="Irrigation schedule")
    water_requirements: Dict[str, Any] = Field(..., description="Water requirements")
    efficiency_factors: Dict[str, Any] = Field(..., description="Efficiency factors")
    recommendations: List[str] = Field(..., description="Schedule recommendations")
    schedule_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Schedule timestamp")
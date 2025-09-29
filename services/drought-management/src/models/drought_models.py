"""
Drought Management Data Models

Pydantic models for drought assessment, conservation practices,
and monitoring data structures.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from uuid import UUID, uuid4
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
    
    @field_validator('water_savings_percent')
    @classmethod
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
    
    @field_validator('surface_moisture_percent', 'deep_moisture_percent')
    @classmethod
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
    
    @field_validator('savings_percentage')
    @classmethod
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
    
    @field_validator('confidence_score')
    @classmethod
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

# New models for TICKET-014_drought-management-12.1 endpoints

class AssessmentType(str, Enum):
    """Types of drought assessment."""
    COMPREHENSIVE = "comprehensive"
    QUICK = "quick"
    EMERGENCY = "emergency"

class AssessmentGoal(str, Enum):
    """Assessment goals."""
    WATER_CONSERVATION = "water_conservation"
    COST_REDUCTION = "cost_reduction"
    SOIL_HEALTH = "soil_health"
    YIELD_OPTIMIZATION = "yield_optimization"
    SUSTAINABILITY = "sustainability"

class ComprehensiveDroughtAssessmentRequest(BaseModel):
    """Request model for comprehensive drought assessment endpoint."""
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    assessment_type: AssessmentType = Field(..., description="Type of assessment to perform")
    field_ids: Optional[List[UUID]] = Field(None, description="Specific field identifiers (if None, all fields)")
    crop_types: List[str] = Field(..., description="Types of crops to assess")
    growth_stages: List[str] = Field(..., description="Current growth stages")
    soil_types: List[str] = Field(..., description="Soil types in fields")
    irrigation_available: bool = Field(False, description="Whether irrigation is available")
    include_weather_forecast: bool = Field(True, description="Include weather forecast analysis")
    include_soil_analysis: bool = Field(True, description="Include detailed soil analysis")
    include_economic_analysis: bool = Field(True, description="Include economic impact analysis")
    assessment_depth_days: int = Field(30, ge=1, le=365, description="Assessment depth in days")
    assessment_goals: List[AssessmentGoal] = Field(..., description="Primary assessment goals")
    budget_constraints: Optional[Decimal] = Field(None, description="Budget constraints for recommendations")
    implementation_timeline: str = Field("immediate", description="Preferred implementation timeline")

class DetailedRecommendation(BaseModel):
    """Detailed recommendation with implementation guidance."""
    recommendation_id: UUID = Field(..., description="Unique recommendation identifier")
    practice_name: str = Field(..., description="Name of the recommended practice")
    practice_type: ConservationPracticeType = Field(..., description="Type of conservation practice")
    priority_score: float = Field(..., ge=0, le=10, description="Priority score (0-10)")
    implementation_timeline: Dict[str, Any] = Field(..., description="Detailed implementation timeline")
    cost_benefit_analysis: Dict[str, Any] = Field(..., description="Comprehensive cost-benefit analysis")
    expected_outcomes: Dict[str, Any] = Field(..., description="Expected outcomes and benefits")
    implementation_guide: Dict[str, Any] = Field(..., description="Step-by-step implementation guide")
    equipment_requirements: List[EquipmentRequirement] = Field(default_factory=list)
    resource_requirements: List[str] = Field(default_factory=list, description="Required resources")
    risk_assessment: Dict[str, Any] = Field(..., description="Risk assessment for implementation")
    monitoring_requirements: List[str] = Field(default_factory=list, description="Monitoring requirements")
    success_metrics: List[str] = Field(default_factory=list, description="Success measurement metrics")

class ComprehensiveDroughtAssessmentResponse(BaseModel):
    """Response model for comprehensive drought assessment."""
    assessment_id: UUID = Field(..., description="Unique assessment identifier")
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    assessment_date: datetime = Field(default_factory=datetime.utcnow)
    assessment_type: AssessmentType = Field(..., description="Type of assessment performed")
    overall_drought_risk: DroughtRiskLevel = Field(..., description="Overall drought risk level")
    field_assessments: List[DroughtAssessment] = Field(..., description="Individual field assessments")
    comprehensive_recommendations: List[DetailedRecommendation] = Field(..., description="Comprehensive recommendations")
    water_savings_potential: WaterSavingsPotential = Field(..., description="Overall water savings potential")
    economic_impact_analysis: Dict[str, Any] = Field(..., description="Economic impact analysis")
    implementation_roadmap: Dict[str, Any] = Field(..., description="Implementation roadmap")
    monitoring_strategy: Dict[str, Any] = Field(..., description="Monitoring strategy")
    next_assessment_date: date = Field(..., description="Recommended next assessment date")
    confidence_score: float = Field(..., ge=0, le=1, description="Overall assessment confidence")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")

class DetailedRecommendationsResponse(BaseModel):
    """Response model for detailed recommendations endpoint."""
    assessment_id: UUID = Field(..., description="Assessment identifier")
    recommendations: List[DetailedRecommendation] = Field(..., description="Detailed recommendations")
    implementation_priority: Dict[str, Any] = Field(..., description="Implementation priority matrix")
    resource_allocation: Dict[str, Any] = Field(..., description="Resource allocation recommendations")
    timeline_optimization: Dict[str, Any] = Field(..., description="Timeline optimization suggestions")
    risk_mitigation_strategies: List[str] = Field(..., description="Risk mitigation strategies")
    success_tracking_plan: Dict[str, Any] = Field(..., description="Success tracking plan")
    expert_insights: List[str] = Field(default_factory=list, description="Expert insights and tips")

class WaterSavingsAnalysisResponse(BaseModel):
    """Response model for water savings analysis endpoint."""
    assessment_id: UUID = Field(..., description="Assessment identifier")
    field_savings_analysis: List[Dict[str, Any]] = Field(..., description="Field-specific savings analysis")
    cumulative_savings: Dict[str, Any] = Field(..., description="Cumulative savings across all fields")
    practice_contributions: Dict[str, Any] = Field(..., description="Contribution of each practice to savings")
    uncertainty_analysis: Dict[str, Any] = Field(..., description="Uncertainty ranges and confidence intervals")
    validation_data: Dict[str, Any] = Field(..., description="Validation data and sources")
    savings_projections: Dict[str, Any] = Field(..., description="Future savings projections")
    cost_benefit_summary: Dict[str, Any] = Field(..., description="Cost-benefit summary")
    implementation_impact: Dict[str, Any] = Field(..., description="Implementation impact on savings")

class AlertSubscriptionRequest(BaseModel):
    """Request model for drought alert subscription."""
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    field_ids: List[UUID] = Field(..., description="Field identifiers to monitor")
    alert_types: List[str] = Field(..., description="Types of alerts to subscribe to")
    threshold_settings: Dict[str, float] = Field(..., description="Alert threshold settings")
    notification_channels: List[str] = Field(..., description="Notification channels (email, sms, push)")
    notification_frequency: str = Field("immediate", description="Notification frequency preference")
    escalation_rules: Dict[str, Any] = Field(default_factory=dict, description="Alert escalation rules")
    custom_triggers: List[Dict[str, Any]] = Field(default_factory=list, description="Custom alert triggers")

class AlertSubscriptionResponse(BaseModel):
    """Response model for drought alert subscription."""
    subscription_id: UUID = Field(..., description="Unique subscription identifier")
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    subscription_status: str = Field(..., description="Subscription status")
    active_alerts: List[Dict[str, Any]] = Field(default_factory=list, description="Currently active alerts")
    alert_history: List[Dict[str, Any]] = Field(default_factory=list, description="Recent alert history")
    notification_preferences: Dict[str, Any] = Field(..., description="Current notification preferences")
    next_check_time: datetime = Field(..., description="Next scheduled check time")
    subscription_health: Dict[str, Any] = Field(..., description="Subscription health status")

# Models for TICKET-014_drought-management-12.2 Advanced API Endpoints

class PracticeComparisonRequest(BaseModel):
    """Request model for practice comparison."""
    field_id: UUID = Field(..., description="Field identifier for comparison")
    practices_to_compare: List[UUID] = Field(..., min_length=2, max_length=5, description="Practice IDs to compare")
    comparison_criteria: List[str] = Field(default=["water_savings", "cost_effectiveness", "soil_health"], description="Criteria for comparison")
    time_horizon_years: int = Field(default=3, ge=1, le=10, description="Time horizon for comparison in years")
    include_risk_assessment: bool = Field(default=True, description="Include risk assessment in comparison")

class PracticeComparisonResult(BaseModel):
    """Individual practice comparison result."""
    practice_id: UUID = Field(..., description="Practice identifier")
    practice_name: str = Field(..., description="Practice name")
    water_savings_percent: float = Field(..., description="Expected water savings percentage")
    implementation_cost_per_acre: Decimal = Field(..., description="Implementation cost per acre")
    annual_maintenance_cost: Decimal = Field(..., description="Annual maintenance cost per acre")
    soil_health_impact_score: float = Field(..., ge=0, le=10, description="Soil health impact score")
    effectiveness_rating: float = Field(..., ge=0, le=10, description="Overall effectiveness rating")
    risk_level: DroughtRiskLevel = Field(..., description="Associated risk level")
    payback_period_years: Optional[float] = Field(None, description="Payback period in years")
    total_benefit_score: float = Field(..., ge=0, le=10, description="Total benefit score")

class PracticeComparisonResponse(BaseModel):
    """Response model for practice comparison."""
    comparison_id: UUID = Field(default_factory=uuid4, description="Unique comparison identifier")
    field_id: UUID = Field(..., description="Field identifier")
    comparison_date: datetime = Field(default_factory=datetime.utcnow, description="Comparison date")
    practices_compared: List[PracticeComparisonResult] = Field(..., description="Comparison results")
    recommended_practice: Optional[UUID] = Field(None, description="Recommended practice ID")
    recommendation_reason: str = Field(..., description="Reason for recommendation")
    decision_matrix: Dict[str, Dict[str, float]] = Field(..., description="Decision matrix for comparison")
    trade_off_analysis: Dict[str, Any] = Field(..., description="Trade-off analysis between practices")

class DashboardDataRequest(BaseModel):
    """Request model for monitoring dashboard data."""
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    include_field_details: bool = Field(default=True, description="Include individual field details")
    time_range_days: int = Field(default=30, ge=1, le=365, description="Time range for data in days")
    include_forecasts: bool = Field(default=True, description="Include forecast data")
    include_alerts: bool = Field(default=True, description="Include alert information")

class DashboardFieldData(BaseModel):
    """Dashboard data for individual field."""
    field_id: UUID = Field(..., description="Field identifier")
    field_name: str = Field(..., description="Field name")
    current_drought_index: float = Field(..., description="Current drought index")
    soil_moisture_percent: float = Field(..., ge=0, le=100, description="Current soil moisture percentage")
    moisture_trend: str = Field(..., description="Moisture trend (increasing/decreasing/stable)")
    irrigation_recommendation: str = Field(..., description="Current irrigation recommendation")
    days_until_critical: Optional[int] = Field(None, description="Days until critical moisture level")
    last_irrigation_date: Optional[date] = Field(None, description="Last irrigation date")
    water_savings_this_month: Decimal = Field(..., description="Water savings this month")

class DashboardAlert(BaseModel):
    """Dashboard alert information."""
    alert_id: UUID = Field(..., description="Alert identifier")
    alert_type: str = Field(..., description="Type of alert")
    severity: str = Field(..., description="Alert severity")
    message: str = Field(..., description="Alert message")
    field_id: Optional[UUID] = Field(None, description="Associated field ID")
    created_at: datetime = Field(..., description="Alert creation time")
    acknowledged: bool = Field(default=False, description="Whether alert is acknowledged")

class DashboardTrendData(BaseModel):
    """Trend data for dashboard."""
    metric_name: str = Field(..., description="Metric name")
    current_value: float = Field(..., description="Current value")
    previous_value: float = Field(..., description="Previous period value")
    change_percent: float = Field(..., description="Percentage change")
    trend_direction: str = Field(..., description="Trend direction (up/down/stable)")
    data_points: List[Dict[str, Any]] = Field(..., description="Historical data points")

class MonitoringDashboardResponse(BaseModel):
    """Response model for monitoring dashboard data."""
    dashboard_id: UUID = Field(default_factory=uuid4, description="Unique dashboard identifier")
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Dashboard generation time")
    overall_drought_status: DroughtRiskLevel = Field(..., description="Overall farm drought status")
    fields_data: List[DashboardFieldData] = Field(..., description="Individual field data")
    alerts: List[DashboardAlert] = Field(default_factory=list, description="Active alerts")
    trends: List[DashboardTrendData] = Field(..., description="Trend analysis data")
    forecast_summary: Dict[str, Any] = Field(..., description="Weather forecast summary")
    recommendations: List[str] = Field(..., description="General recommendations")

class ScenarioPlanningRequest(BaseModel):
    """Request model for scenario planning."""
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    scenario_name: str = Field(..., description="Name of the scenario")
    scenario_description: str = Field(..., description="Description of the scenario")
    time_horizon_months: int = Field(default=12, ge=1, le=60, description="Planning horizon in months")
    practices_to_evaluate: List[UUID] = Field(..., description="Practices to evaluate in scenario")
    weather_scenarios: List[str] = Field(default=["normal", "drought", "wet"], description="Weather scenarios to evaluate")
    include_economic_analysis: bool = Field(default=True, description="Include economic analysis")
    include_risk_assessment: bool = Field(default=True, description="Include risk assessment")

class ScenarioOutcome(BaseModel):
    """Outcome for a specific scenario."""
    scenario_name: str = Field(..., description="Scenario name")
    weather_condition: str = Field(..., description="Weather condition")
    practice_combination: List[str] = Field(..., description="Practices in this scenario")
    expected_water_savings: Decimal = Field(..., description="Expected water savings")
    expected_yield_impact: float = Field(..., description="Expected yield impact percentage")
    implementation_cost: Decimal = Field(..., description="Total implementation cost")
    net_benefit: Decimal = Field(..., description="Net benefit over time horizon")
    risk_score: float = Field(..., ge=0, le=10, description="Risk score for scenario")
    success_probability: float = Field(..., ge=0, le=1, description="Probability of success")

class ScenarioPlanningResponse(BaseModel):
    """Response model for scenario planning."""
    scenario_analysis_id: UUID = Field(default_factory=uuid4, description="Unique scenario analysis identifier")
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    analysis_date: datetime = Field(default_factory=datetime.utcnow, description="Analysis date")
    scenario_name: str = Field(..., description="Scenario name")
    time_horizon_months: int = Field(..., description="Planning horizon")
    scenarios_evaluated: List[ScenarioOutcome] = Field(..., description="Evaluated scenarios")
    recommended_scenario: Optional[str] = Field(None, description="Recommended scenario name")
    recommendation_reason: str = Field(..., description="Reason for recommendation")
    risk_assessment: Dict[str, Any] = Field(..., description="Overall risk assessment")
    economic_summary: Dict[str, Any] = Field(..., description="Economic analysis summary")
    implementation_timeline: List[Dict[str, Any]] = Field(..., description="Recommended implementation timeline")
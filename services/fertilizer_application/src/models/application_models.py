"""
Pydantic models for fertilizer application data.
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from enum import Enum
from pydantic import BaseModel, Field, validator
from decimal import Decimal

# Import equipment models for type hints
from src.models.equipment_models import EquipmentSuitability


class ApplicationMethodType(str, Enum):
    """Types of fertilizer application methods."""
    BROADCAST = "broadcast"
    BAND = "band"
    SIDEDRESS = "sidedress"
    FOLIAR = "foliar"
    INJECTION = "injection"
    DRIP = "drip"
    FERTIGATION = "fertigation"


class FertilizerForm(str, Enum):
    """Types of fertilizer forms."""
    GRANULAR = "granular"
    LIQUID = "liquid"
    GASEOUS = "gaseous"
    SLOW_RELEASE = "slow_release"
    ORGANIC = "organic"


class EquipmentType(str, Enum):
    """Types of application equipment."""
    SPREADER = "spreader"
    SPRAYER = "sprayer"
    INJECTOR = "injector"
    DRIP_SYSTEM = "drip_system"
    HAND_SPREADER = "hand_spreader"
    BROADCASTER = "broadcaster"


class FieldConditions(BaseModel):
    """Field conditions for application assessment."""
    field_size_acres: float = Field(..., ge=0.1, le=10000.0, description="Field size in acres")
    soil_type: str = Field(..., description="Primary soil type")
    drainage_class: Optional[str] = Field(None, description="Soil drainage classification")
    drainage_assessment: Optional[Dict[str, Any]] = Field(None, description="Detailed drainage assessment")
    slope_percent: Optional[float] = Field(None, ge=0, le=100, description="Field slope percentage")
    irrigation_available: bool = Field(False, description="Whether irrigation is available")
    field_shape: Optional[str] = Field(None, description="Field shape (rectangular, irregular, etc.)")
    access_roads: Optional[List[str]] = Field(None, description="Available access roads")


class CropRequirements(BaseModel):
    """Crop-specific fertilizer requirements."""
    crop_type: str = Field(..., description="Type of crop")
    growth_stage: str = Field(..., description="Current growth stage")
    target_yield: Optional[float] = Field(None, description="Target yield per acre")
    yield_goal_bushels_per_acre: Optional[float] = Field(None, description="Yield goal in bushels per acre")
    nutrient_requirements: Dict[str, float] = Field(default_factory=dict, description="Nutrient requirements")
    application_timing_preferences: List[str] = Field(default_factory=list, description="Preferred application timings")
    timing_requirements: Optional[Dict[str, Any]] = Field(None, description="Detailed timing requirements")


class FertilizerSpecification(BaseModel):
    """Fertilizer product specification."""
    fertilizer_type: str = Field(..., description="Type of fertilizer")
    npk_ratio: str = Field(..., description="NPK ratio (e.g., '10-10-10')")
    form: FertilizerForm = Field(..., description="Physical form of fertilizer")
    solubility: Optional[float] = Field(None, ge=0, le=100, description="Solubility percentage")
    release_rate: Optional[str] = Field(None, description="Release rate (immediate, slow, controlled)")
    cost_per_unit: Optional[float] = Field(None, ge=0, description="Cost per unit")
    unit: Optional[str] = Field(None, description="Unit of measurement")


class EquipmentSpecification(BaseModel):
    """Equipment specification for application."""
    equipment_type: EquipmentType = Field(..., description="Type of equipment")
    capacity: Optional[float] = Field(None, description="Equipment capacity")
    capacity_unit: Optional[str] = Field(None, description="Capacity unit")
    application_width: Optional[float] = Field(None, description="Application width in feet")
    application_rate_range: Optional[Dict[str, float]] = Field(None, description="Rate range (min, max)")
    fuel_efficiency: Optional[float] = Field(None, description="Fuel efficiency rating")
    maintenance_cost_per_hour: Optional[float] = Field(None, description="Maintenance cost per hour")


class ApplicationRequest(BaseModel):
    """Request model for fertilizer application method selection."""
    field_conditions: FieldConditions = Field(..., description="Field conditions")
    crop_requirements: CropRequirements = Field(..., description="Crop requirements")
    fertilizer_specification: FertilizerSpecification = Field(..., description="Fertilizer specification")
    available_equipment: List[EquipmentSpecification] = Field(default_factory=list, description="Available equipment")
    application_goals: List[str] = Field(default_factory=list, description="Application goals")
    constraints: Optional[Dict[str, Any]] = Field(None, description="Application constraints")
    budget_limit: Optional[float] = Field(None, ge=0, description="Budget limit")


class ApplicationMethod(BaseModel):
    """Fertilizer application method recommendation."""
    method_id: str = Field(..., description="Unique method identifier")
    method_type: ApplicationMethodType = Field(..., description="Type of application method")
    recommended_equipment: EquipmentSpecification = Field(..., description="Recommended equipment")
    application_rate: float = Field(..., ge=0, description="Recommended application rate")
    rate_unit: str = Field(..., description="Application rate unit")
    application_timing: str = Field(..., description="Recommended application timing")
    efficiency_score: float = Field(..., ge=0, le=1, description="Application efficiency score")
    cost_per_acre: Optional[float] = Field(None, ge=0, description="Cost per acre")
    labor_requirements: Optional[str] = Field(None, description="Labor requirements")
    environmental_impact: Optional[str] = Field(None, description="Environmental impact assessment")
    pros: List[str] = Field(default_factory=list, description="Advantages of this method")
    cons: List[str] = Field(default_factory=list, description="Disadvantages of this method")
    # Enhanced crop integration fields
    crop_compatibility_score: Optional[float] = Field(None, ge=0, le=1, description="Crop compatibility score")
    crop_compatibility_factors: Optional[List[str]] = Field(None, description="Crop compatibility factors")


class ApplicationResponse(BaseModel):
    """Response model for fertilizer application recommendations."""
    request_id: str = Field(..., description="Unique request identifier")
    recommended_methods: List[ApplicationMethod] = Field(..., description="Recommended application methods")
    primary_recommendation: ApplicationMethod = Field(..., description="Primary recommendation")
    alternative_methods: List[ApplicationMethod] = Field(default_factory=list, description="Alternative methods")
    cost_comparison: Optional[Dict[str, float]] = Field(None, description="Cost comparison across methods")
    efficiency_analysis: Optional[Dict[str, Any]] = Field(None, description="Efficiency analysis")
    equipment_compatibility: Optional[Dict[str, bool]] = Field(None, description="Equipment compatibility matrix")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class EquipmentAssessmentRequest(BaseModel):
    """Request model for equipment assessment."""
    farm_size_acres: float = Field(..., ge=0.1, le=10000.0, description="Total farm size in acres")
    field_count: int = Field(..., ge=1, description="Number of fields")
    average_field_size: float = Field(..., ge=0.1, description="Average field size in acres")
    current_equipment: List[EquipmentSpecification] = Field(default_factory=list, description="Current equipment inventory")
    budget_constraints: Optional[float] = Field(None, ge=0, description="Equipment budget")
    labor_availability: Optional[str] = Field(None, description="Labor availability level")
    maintenance_capability: Optional[str] = Field(None, description="Maintenance capability level")
    # Enhanced farm assessment fields
    field_layouts: Optional[List[Dict[str, Any]]] = Field(None, description="Field layout information")
    storage_facilities: Optional[List[Dict[str, Any]]] = Field(None, description="Storage facility information")
    access_roads: Optional[List[Dict[str, Any]]] = Field(None, description="Access road information")
    labor_details: Optional[Dict[str, Any]] = Field(None, description="Detailed labor information")
    environmental_goals: Optional[List[str]] = Field(None, description="Environmental goals and constraints")


class EquipmentAssessment(BaseModel):
    """Equipment assessment result."""
    equipment_id: str = Field(..., description="Equipment identifier")
    equipment_type: EquipmentType = Field(..., description="Type of equipment")
    suitability_score: float = Field(..., ge=0, le=1, description="Suitability score for farm")
    capacity_adequacy: str = Field(..., description="Capacity adequacy assessment")
    efficiency_rating: float = Field(..., ge=0, le=1, description="Efficiency rating")
    cost_effectiveness: float = Field(..., ge=0, le=1, description="Cost effectiveness rating")
    upgrade_recommendations: List[str] = Field(default_factory=list, description="Upgrade recommendations")
    maintenance_requirements: Optional[str] = Field(None, description="Maintenance requirements")
    replacement_timeline: Optional[str] = Field(None, description="Recommended replacement timeline")


class EquipmentAssessmentResponse(BaseModel):
    """Response model for equipment assessment."""
    request_id: str = Field(..., description="Unique request identifier")
    farm_assessment: Dict[str, Any] = Field(..., description="Overall farm assessment")
    equipment_assessments: List[IndividualEquipmentAssessment] = Field(..., description="Individual equipment assessments")
    upgrade_priorities: List[str] = Field(default_factory=list, description="Upgrade priorities")
    capacity_analysis: Dict[str, Any] = Field(default_factory=dict, description="Capacity analysis")
    cost_benefit_analysis: Optional[Dict[str, Any]] = Field(None, description="Cost-benefit analysis")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional assessment metadata")
    # Enhanced comprehensive assessment fields
    comprehensive_farm_assessment: Optional[Dict[str, Any]] = Field(None, description="Comprehensive farm assessment")
    field_layout_analysis: Optional[List[Dict[str, Any]]] = Field(None, description="Field layout analysis")
    storage_facility_assessment: Optional[List[Dict[str, Any]]] = Field(None, description="Storage facility assessment")
    labor_analysis: Optional[Dict[str, Any]] = Field(None, description="Labor analysis")
    environmental_assessment: Optional[List[Dict[str, Any]]] = Field(None, description="Environmental assessment")
    operational_efficiency_score: Optional[float] = Field(None, ge=0, le=1, description="Overall operational efficiency score")
    optimization_recommendations: Optional[List[str]] = Field(None, description="Optimization recommendations")
    implementation_priorities: Optional[List[str]] = Field(None, description="Implementation priorities")


class GuidanceRequest(BaseModel):
    """Request model for application guidance."""
    application_method: ApplicationMethod = Field(..., description="Selected application method")
    field_conditions: FieldConditions = Field(..., description="Field conditions")
    weather_conditions: Optional[Dict[str, Any]] = Field(None, description="Current weather conditions")
    application_date: Optional[date] = Field(None, description="Planned application date")
    experience_level: Optional[str] = Field(None, description="Operator experience level")


class ApplicationGuidance(BaseModel):
    """Application guidance and instructions."""
    guidance_id: str = Field(..., description="Guidance identifier")
    pre_application_checklist: List[str] = Field(default_factory=list, description="Pre-application checklist")
    application_instructions: List[str] = Field(default_factory=list, description="Step-by-step instructions")
    safety_precautions: List[str] = Field(default_factory=list, description="Safety precautions")
    calibration_instructions: Optional[List[str]] = Field(None, description="Equipment calibration instructions")
    troubleshooting_tips: List[str] = Field(default_factory=list, description="Troubleshooting tips")
    post_application_tasks: List[str] = Field(default_factory=list, description="Post-application tasks")
    optimal_conditions: Dict[str, Any] = Field(default_factory=dict, description="Optimal application conditions")
    timing_recommendations: Optional[str] = Field(None, description="Timing recommendations")


class GuidanceResponse(BaseModel):
    """Response model for comprehensive application guidance."""
    request_id: str = Field(..., description="Unique request identifier")
    guidance: ApplicationGuidance = Field(..., description="Application guidance")
    weather_advisories: Optional[List[str]] = Field(None, description="Weather-related advisories")
    equipment_preparation: Optional[List[str]] = Field(None, description="Equipment preparation steps")
    quality_control_measures: Optional[List[str]] = Field(None, description="Quality control measures")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    
    # Enhanced comprehensive guidance features
    video_tutorials: Optional[List[Dict[str, Any]]] = Field(None, description="Relevant video tutorials")
    expert_recommendations: Optional[List[Dict[str, Any]]] = Field(None, description="Expert consultation recommendations")
    compliance_check: Optional[Dict[str, Any]] = Field(None, description="Regulatory compliance status")
    educational_content: Optional[Dict[str, Any]] = Field(None, description="Educational content and best practices")
    interactive_guides: Optional[List[Dict[str, Any]]] = Field(None, description="Interactive guides and tools")
    maintenance_schedule: Optional[Dict[str, List[str]]] = Field(None, description="Equipment maintenance schedule")


# Advanced Application Management Models for TICKET-023_fertilizer-application-method-10.2

class ApplicationPlanRequest(BaseModel):
    """Request model for application planning."""
    user_id: str = Field(..., description="User identifier")
    farm_id: str = Field(..., description="Farm identifier")
    fields: List[Dict[str, Any]] = Field(..., description="List of fields to plan applications for")
    season: str = Field(..., description="Growing season (spring, summer, fall, winter)")
    planning_horizon_days: int = Field(default=90, ge=1, le=365, description="Planning horizon in days")
    objectives: List[str] = Field(default=["yield_optimization"], description="Planning objectives")
    constraints: Optional[Dict[str, Any]] = Field(None, description="Planning constraints")
    preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences")


class ApplicationPlan(BaseModel):
    """Individual application plan for a field."""
    field_id: str = Field(..., description="Field identifier")
    field_name: str = Field(..., description="Field name")
    crop_type: str = Field(..., description="Crop type")
    growth_stage: str = Field(..., description="Current growth stage")
    planned_date: date = Field(..., description="Planned application date")
    application_method: ApplicationMethodType = Field(..., description="Application method")
    fertilizer_type: str = Field(..., description="Fertilizer type")
    application_rate: float = Field(..., description="Application rate per acre")
    total_amount: float = Field(..., description="Total fertilizer amount needed")
    equipment_required: List[str] = Field(..., description="Required equipment")
    labor_hours: float = Field(..., description="Estimated labor hours")
    cost_estimate: float = Field(..., description="Estimated cost")
    weather_window: Optional[Dict[str, Any]] = Field(None, description="Optimal weather window")
    notes: Optional[str] = Field(None, description="Additional notes")


class ApplicationPlanResponse(BaseModel):
    """Response model for application planning."""
    request_id: str = Field(..., description="Unique request identifier")
    plan_id: str = Field(..., description="Plan identifier")
    farm_name: str = Field(..., description="Farm name")
    season: str = Field(..., description="Season")
    planning_horizon_days: int = Field(..., description="Planning horizon")
    total_fields: int = Field(..., description="Total number of fields planned")
    application_plans: List[ApplicationPlan] = Field(..., description="Individual field plans")
    resource_summary: Dict[str, Any] = Field(..., description="Resource requirements summary")
    cost_summary: Dict[str, Any] = Field(..., description="Cost summary")
    timeline: List[Dict[str, Any]] = Field(..., description="Application timeline")
    optimization_recommendations: Optional[List[str]] = Field(None, description="Optimization recommendations")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


class ApplicationMonitorRequest(BaseModel):
    """Request model for application monitoring."""
    user_id: str = Field(..., description="User identifier")
    farm_id: str = Field(..., description="Farm identifier")
    field_ids: Optional[List[str]] = Field(None, description="Specific field IDs to monitor")
    include_historical: bool = Field(default=True, description="Include historical data")
    time_range_days: int = Field(default=30, ge=1, le=365, description="Time range for data")


class ApplicationStatus(BaseModel):
    """Current application status for a field."""
    field_id: str = Field(..., description="Field identifier")
    field_name: str = Field(..., description="Field name")
    crop_type: str = Field(..., description="Crop type")
    current_status: str = Field(..., description="Current application status")
    last_application_date: Optional[date] = Field(None, description="Last application date")
    next_scheduled_date: Optional[date] = Field(None, description="Next scheduled application")
    progress_percentage: float = Field(..., ge=0, le=100, description="Application progress percentage")
    quality_metrics: Optional[Dict[str, Any]] = Field(None, description="Application quality metrics")
    equipment_status: Optional[Dict[str, Any]] = Field(None, description="Equipment status")
    weather_conditions: Optional[Dict[str, Any]] = Field(None, description="Current weather conditions")
    alerts: Optional[List[str]] = Field(None, description="Active alerts")


class ApplicationMonitorResponse(BaseModel):
    """Response model for application monitoring."""
    request_id: str = Field(..., description="Unique request identifier")
    farm_name: str = Field(..., description="Farm name")
    monitoring_timestamp: datetime = Field(..., description="Monitoring timestamp")
    total_fields: int = Field(..., description="Total fields being monitored")
    active_applications: int = Field(..., description="Number of active applications")
    completed_applications: int = Field(..., description="Number of completed applications")
    field_statuses: List[ApplicationStatus] = Field(..., description="Field application statuses")
    farm_summary: Dict[str, Any] = Field(..., description="Farm-wide summary")
    alerts_summary: Dict[str, Any] = Field(..., description="Summary of alerts")
    recommendations: Optional[List[str]] = Field(None, description="Recommendations")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


class OptimizationRequest(BaseModel):
    """Request model for real-time optimization."""
    user_id: str = Field(..., description="User identifier")
    farm_id: str = Field(..., description="Farm identifier")
    field_id: str = Field(..., description="Field identifier")
    current_conditions: Dict[str, Any] = Field(..., description="Current field conditions")
    weather_update: Optional[Dict[str, Any]] = Field(None, description="Latest weather data")
    equipment_status: Optional[Dict[str, Any]] = Field(None, description="Current equipment status")
    optimization_goals: List[str] = Field(default=["efficiency"], description="Optimization goals")
    constraints: Optional[Dict[str, Any]] = Field(None, description="Optimization constraints")


class OptimizationRecommendation(BaseModel):
    """Individual optimization recommendation."""
    recommendation_type: str = Field(..., description="Type of recommendation")
    priority: str = Field(..., description="Priority level (high, medium, low)")
    description: str = Field(..., description="Recommendation description")
    expected_benefit: str = Field(..., description="Expected benefit")
    implementation_effort: str = Field(..., description="Implementation effort required")
    cost_impact: Optional[float] = Field(None, description="Cost impact")
    timeline: Optional[str] = Field(None, description="Implementation timeline")
    supporting_data: Optional[Dict[str, Any]] = Field(None, description="Supporting data")


class OptimizationResponse(BaseModel):
    """Response model for real-time optimization."""
    request_id: str = Field(..., description="Unique request identifier")
    field_id: str = Field(..., description="Field identifier")
    field_name: str = Field(..., description="Field name")
    optimization_timestamp: datetime = Field(..., description="Optimization timestamp")
    current_conditions_summary: Dict[str, Any] = Field(..., description="Current conditions summary")
    optimization_score: float = Field(..., ge=0, le=100, description="Overall optimization score")
    recommendations: List[OptimizationRecommendation] = Field(..., description="Optimization recommendations")
    performance_predictions: Optional[Dict[str, Any]] = Field(None, description="Performance predictions")
    risk_assessment: Optional[Dict[str, Any]] = Field(None, description="Risk assessment")
    next_optimization_due: Optional[datetime] = Field(None, description="Next optimization due")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
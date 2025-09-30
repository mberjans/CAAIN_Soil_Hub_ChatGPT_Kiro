"""
Pydantic models for fertilizer application data.
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from enum import Enum
from pydantic import BaseModel, Field, validator
from decimal import Decimal

# Import equipment models for type hints
from src.models.equipment_models import IndividualEquipmentAssessment


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
    slope_percent: Optional[float] = Field(None, ge=0, le=100, description="Field slope percentage")
    irrigation_available: bool = Field(False, description="Whether irrigation is available")
    field_shape: Optional[str] = Field(None, description="Field shape (rectangular, irregular, etc.)")
    access_roads: Optional[List[str]] = Field(None, description="Available access roads")


class CropRequirements(BaseModel):
    """Crop-specific fertilizer requirements."""
    crop_type: str = Field(..., description="Type of crop")
    growth_stage: str = Field(..., description="Current growth stage")
    target_yield: Optional[float] = Field(None, description="Target yield per acre")
    nutrient_requirements: Dict[str, float] = Field(default_factory=dict, description="Nutrient requirements")
    application_timing_preferences: List[str] = Field(default_factory=list, description="Preferred application timings")


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
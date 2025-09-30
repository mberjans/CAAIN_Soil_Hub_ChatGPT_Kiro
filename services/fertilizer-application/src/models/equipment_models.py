"""
Pydantic models for equipment assessment and management.
"""

from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, validator
from decimal import Decimal


class EquipmentCategory(str, Enum):
    """Equipment categories."""
    SPREADING = "spreading"
    SPRAYING = "spraying"
    INJECTION = "injection"
    IRRIGATION = "irrigation"
    HANDLING = "handling"
    STORAGE = "storage"


class EquipmentStatus(str, Enum):
    """Equipment status."""
    OPERATIONAL = "operational"
    MAINTENANCE_REQUIRED = "maintenance_required"
    OUT_OF_SERVICE = "out_of_service"
    RETIRED = "retired"


class MaintenanceLevel(str, Enum):
    """Maintenance complexity levels."""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    PROFESSIONAL = "professional"


class Equipment(BaseModel):
    """Base equipment model."""
    equipment_id: str = Field(..., description="Unique equipment identifier")
    name: str = Field(..., description="Equipment name")
    category: EquipmentCategory = Field(..., description="Equipment category")
    manufacturer: Optional[str] = Field(None, description="Manufacturer name")
    model: Optional[str] = Field(None, description="Model number")
    year: Optional[int] = Field(None, ge=1900, description="Manufacturing year")
    capacity: Optional[float] = Field(None, ge=0, description="Equipment capacity")
    capacity_unit: Optional[str] = Field(None, description="Capacity unit")
    status: EquipmentStatus = Field(EquipmentStatus.OPERATIONAL, description="Current status")
    purchase_date: Optional[str] = Field(None, description="Purchase date")
    purchase_price: Optional[float] = Field(None, ge=0, description="Purchase price")
    current_value: Optional[float] = Field(None, ge=0, description="Current estimated value")
    maintenance_level: MaintenanceLevel = Field(MaintenanceLevel.BASIC, description="Required maintenance level")


class SpreaderEquipment(Equipment):
    """Spreader equipment specification."""
    hopper_capacity: Optional[float] = Field(None, ge=0, description="Hopper capacity")
    capacity_unit: str = Field("cubic_feet", description="Capacity unit")
    spread_width: Optional[float] = Field(None, ge=0, description="Maximum spread width in feet")
    application_rate_range: Optional[Dict[str, float]] = Field(None, description="Rate range (min, max)")
    rate_unit: str = Field("lbs/acre", description="Application rate unit")
    ground_speed_range: Optional[Dict[str, float]] = Field(None, description="Ground speed range (min, max)")
    speed_unit: str = Field("mph", description="Speed unit")
    power_source: Optional[str] = Field(None, description="Power source (PTO, hydraulic, electric)")
    calibration_method: Optional[str] = Field(None, description="Calibration method")


class SprayerEquipment(Equipment):
    """Sprayer equipment specification."""
    tank_capacity: Optional[float] = Field(None, ge=0, description="Tank capacity")
    capacity_unit: str = Field("gallons", description="Capacity unit")
    boom_width: Optional[float] = Field(None, ge=0, description="Boom width in feet")
    nozzle_count: Optional[int] = Field(None, ge=0, description="Number of nozzles")
    pressure_range: Optional[Dict[str, float]] = Field(None, description="Pressure range (min, max)")
    pressure_unit: str = Field("psi", description="Pressure unit")
    flow_rate_range: Optional[Dict[str, float]] = Field(None, description="Flow rate range (min, max)")
    flow_unit: str = Field("gpm", description="Flow rate unit")
    agitation_system: Optional[str] = Field(None, description="Agitation system type")
    filtration_system: Optional[str] = Field(None, description="Filtration system")


class InjectionEquipment(Equipment):
    """Injection equipment specification."""
    injection_rate_range: Optional[Dict[str, float]] = Field(None, description="Injection rate range (min, max)")
    rate_unit: str = Field("gph", description="Injection rate unit")
    injection_depth_range: Optional[Dict[str, float]] = Field(None, description="Injection depth range (min, max)")
    depth_unit: str = Field("inches", description="Depth unit")
    injection_points: Optional[int] = Field(None, ge=0, description="Number of injection points")
    pressure_requirement: Optional[float] = Field(None, ge=0, description="Required pressure")
    pressure_unit: str = Field("psi", description="Pressure unit")
    flow_capacity: Optional[float] = Field(None, ge=0, description="Flow capacity")
    flow_unit: str = Field("gpm", description="Flow unit")


class DripSystemEquipment(Equipment):
    """Drip irrigation system specification."""
    system_capacity: Optional[float] = Field(None, ge=0, description="System capacity")
    capacity_unit: str = Field("acres", description="Capacity unit")
    emitter_spacing: Optional[float] = Field(None, ge=0, description="Emitter spacing in inches")
    emitter_flow_rate: Optional[float] = Field(None, ge=0, description="Emitter flow rate")
    flow_unit: str = Field("gph", description="Flow unit")
    operating_pressure: Optional[float] = Field(None, ge=0, description="Operating pressure")
    pressure_unit: str = Field("psi", description="Pressure unit")
    filtration_requirements: Optional[str] = Field(None, description="Filtration requirements")
    fertigation_capability: bool = Field(False, description="Fertigation capability")


class EquipmentInventory(BaseModel):
    """Farm equipment inventory."""
    farm_id: str = Field(..., description="Farm identifier")
    equipment_list: List[Equipment] = Field(default_factory=list, description="List of equipment")
    total_equipment_value: Optional[float] = Field(None, ge=0, description="Total equipment value")
    last_updated: Optional[str] = Field(None, description="Last inventory update date")


class EquipmentCompatibility(BaseModel):
    """Equipment compatibility assessment."""
    equipment_id: str = Field(..., description="Equipment identifier")
    fertilizer_types: List[str] = Field(default_factory=list, description="Compatible fertilizer types")
    application_methods: List[str] = Field(default_factory=list, description="Compatible application methods")
    field_size_range: Optional[Dict[str, float]] = Field(None, description="Suitable field size range")
    soil_types: List[str] = Field(default_factory=list, description="Compatible soil types")
    weather_conditions: List[str] = Field(default_factory=list, description="Suitable weather conditions")
    compatibility_score: float = Field(..., ge=0, le=1, description="Overall compatibility score")


class EquipmentEfficiency(BaseModel):
    """Equipment efficiency metrics."""
    equipment_id: str = Field(..., description="Equipment identifier")
    application_efficiency: float = Field(..., ge=0, le=1, description="Application efficiency")
    fuel_efficiency: Optional[float] = Field(None, ge=0, description="Fuel efficiency rating")
    labor_efficiency: Optional[float] = Field(None, ge=0, le=1, description="Labor efficiency rating")
    maintenance_efficiency: Optional[float] = Field(None, ge=0, le=1, description="Maintenance efficiency")
    overall_efficiency: float = Field(..., ge=0, le=1, description="Overall efficiency score")
    efficiency_factors: Dict[str, Any] = Field(default_factory=dict, description="Factors affecting efficiency")


class EquipmentUpgrade(BaseModel):
    """Equipment upgrade recommendation."""
    current_equipment_id: str = Field(..., description="Current equipment identifier")
    recommended_upgrade: Equipment = Field(..., description="Recommended upgrade")
    upgrade_priority: str = Field(..., description="Upgrade priority (high, medium, low)")
    estimated_cost: Optional[float] = Field(None, ge=0, description="Estimated upgrade cost")
    expected_benefits: List[str] = Field(default_factory=list, description="Expected benefits")
    payback_period: Optional[float] = Field(None, ge=0, description="Payback period in years")
    justification: str = Field(..., description="Upgrade justification")


class IndividualEquipmentAssessment(BaseModel):
    """Individual equipment assessment."""
    equipment_id: str = Field(..., description="Equipment identifier")
    equipment_type: EquipmentCategory = Field(..., description="Equipment category")
    suitability_score: float = Field(..., ge=0, le=1, description="Suitability score for farm operations")
    capacity_adequacy: str = Field(..., description="Capacity adequacy (insufficient, adequate, excessive, unknown)")
    efficiency_rating: float = Field(..., ge=0, le=1, description="Equipment efficiency rating")
    cost_effectiveness: float = Field(..., ge=0, le=1, description="Cost effectiveness rating")
    upgrade_recommendations: List[str] = Field(default_factory=list, description="Upgrade recommendations")
    maintenance_requirements: List[str] = Field(default_factory=list, description="Maintenance requirements")
    replacement_timeline: str = Field(..., description="Replacement timeline recommendation")


class EquipmentAssessment(BaseModel):
    """Comprehensive equipment assessment."""
    farm_id: str = Field(..., description="Farm identifier")
    assessment_date: str = Field(..., description="Assessment date")
    equipment_inventory: EquipmentInventory = Field(..., description="Equipment inventory")
    compatibility_assessments: List[EquipmentCompatibility] = Field(default_factory=list, description="Compatibility assessments")
    efficiency_assessments: List[EquipmentEfficiency] = Field(default_factory=list, description="Efficiency assessments")
    upgrade_recommendations: List[EquipmentUpgrade] = Field(default_factory=list, description="Upgrade recommendations")
    capacity_analysis: Dict[str, Any] = Field(default_factory=dict, description="Capacity analysis")
    cost_benefit_analysis: Optional[Dict[str, Any]] = Field(None, description="Cost-benefit analysis")
    maintenance_schedule: Optional[Dict[str, Any]] = Field(None, description="Maintenance schedule")
    overall_score: float = Field(..., ge=0, le=1, description="Overall assessment score")


class EquipmentMaintenance(BaseModel):
    """Equipment maintenance record."""
    maintenance_id: str = Field(..., description="Maintenance record identifier")
    equipment_id: str = Field(..., description="Equipment identifier")
    maintenance_type: str = Field(..., description="Type of maintenance")
    maintenance_date: str = Field(..., description="Maintenance date")
    maintenance_hours: Optional[float] = Field(None, ge=0, description="Maintenance hours")
    cost: Optional[float] = Field(None, ge=0, description="Maintenance cost")
    description: Optional[str] = Field(None, description="Maintenance description")
    next_maintenance_date: Optional[str] = Field(None, description="Next scheduled maintenance")
    maintenance_provider: Optional[str] = Field(None, description="Maintenance provider")


class EquipmentPerformance(BaseModel):
    """Equipment performance metrics."""
    equipment_id: str = Field(..., description="Equipment identifier")
    performance_date: str = Field(..., description="Performance measurement date")
    application_accuracy: Optional[float] = Field(None, ge=0, le=1, description="Application accuracy")
    coverage_uniformity: Optional[float] = Field(None, ge=0, le=1, description="Coverage uniformity")
    fuel_consumption: Optional[float] = Field(None, ge=0, description="Fuel consumption")
    fuel_unit: str = Field("gallons/hour", description="Fuel consumption unit")
    downtime_hours: Optional[float] = Field(None, ge=0, description="Downtime hours")
    maintenance_cost: Optional[float] = Field(None, ge=0, description="Maintenance cost")
    performance_score: float = Field(..., ge=0, le=1, description="Overall performance score")


class FieldLayoutAnalysis(BaseModel):
    """Field layout analysis for farm operations."""
    field_id: str = Field(..., description="Field identifier")
    field_shape: str = Field(..., description="Field shape (rectangular, irregular, etc.)")
    field_size_acres: float = Field(..., ge=0.1, description="Field size in acres")
    access_points: int = Field(..., ge=1, description="Number of access points")
    access_road_length: Optional[float] = Field(None, ge=0, description="Total access road length in feet")
    field_efficiency_score: float = Field(..., ge=0, le=1, description="Field operational efficiency score")
    turning_radius_requirements: Optional[float] = Field(None, ge=0, description="Minimum turning radius required")
    operational_constraints: List[str] = Field(default_factory=list, description="Operational constraints")
    optimization_opportunities: List[str] = Field(default_factory=list, description="Optimization opportunities")


class StorageFacilityAssessment(BaseModel):
    """Storage facility assessment."""
    facility_id: str = Field(..., description="Facility identifier")
    facility_type: str = Field(..., description="Type of storage facility")
    capacity_tons: Optional[float] = Field(None, ge=0, description="Storage capacity in tons")
    location_efficiency: float = Field(..., ge=0, le=1, description="Location efficiency score")
    handling_equipment_compatibility: List[str] = Field(default_factory=list, description="Compatible handling equipment")
    access_quality: str = Field(..., description="Access quality (excellent, good, fair, poor)")
    environmental_conditions: Dict[str, Any] = Field(default_factory=dict, description="Environmental conditions")
    maintenance_requirements: List[str] = Field(default_factory=list, description="Maintenance requirements")
    upgrade_recommendations: List[str] = Field(default_factory=list, description="Upgrade recommendations")


class LaborAnalysis(BaseModel):
    """Labor analysis for farm operations."""
    farm_id: str = Field(..., description="Farm identifier")
    total_labor_hours_available: float = Field(..., ge=0, description="Total labor hours available per season")
    skilled_labor_percentage: float = Field(..., ge=0, le=100, description="Percentage of skilled labor")
    labor_efficiency_score: float = Field(..., ge=0, le=1, description="Labor efficiency score")
    skill_requirements: Dict[str, str] = Field(default_factory=dict, description="Skill requirements by equipment type")
    training_needs: List[str] = Field(default_factory=list, description="Training needs identified")
    labor_cost_per_hour: Optional[float] = Field(None, ge=0, description="Labor cost per hour")
    seasonal_availability: Dict[str, float] = Field(default_factory=dict, description="Seasonal labor availability")


class EnvironmentalAssessment(BaseModel):
    """Environmental assessment for equipment and operations."""
    equipment_id: str = Field(..., description="Equipment identifier")
    fuel_efficiency_rating: float = Field(..., ge=0, le=1, description="Fuel efficiency rating")
    emissions_factor: Optional[float] = Field(None, ge=0, description="Emissions factor")
    noise_level: Optional[float] = Field(None, ge=0, description="Noise level in decibels")
    environmental_impact_score: float = Field(..., ge=0, le=1, description="Environmental impact score")
    sustainability_metrics: Dict[str, Any] = Field(default_factory=dict, description="Sustainability metrics")
    compliance_status: List[str] = Field(default_factory=list, description="Environmental compliance status")
    improvement_recommendations: List[str] = Field(default_factory=list, description="Environmental improvement recommendations")


class ComprehensiveFarmAssessment(BaseModel):
    """Comprehensive farm assessment including all aspects."""
    farm_id: str = Field(..., description="Farm identifier")
    assessment_date: str = Field(..., description="Assessment date")
    farm_size_analysis: Dict[str, Any] = Field(..., description="Farm size analysis")
    field_layout_analysis: List[FieldLayoutAnalysis] = Field(default_factory=list, description="Field layout analysis")
    storage_facility_assessment: List[StorageFacilityAssessment] = Field(default_factory=list, description="Storage facility assessment")
    labor_analysis: LaborAnalysis = Field(..., description="Labor analysis")
    environmental_assessment: List[EnvironmentalAssessment] = Field(default_factory=list, description="Environmental assessment")
    operational_efficiency_score: float = Field(..., ge=0, le=1, description="Overall operational efficiency score")
    optimization_recommendations: List[str] = Field(default_factory=list, description="Optimization recommendations")
    implementation_priorities: List[str] = Field(default_factory=list, description="Implementation priorities")
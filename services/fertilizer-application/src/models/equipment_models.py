from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID
from enum import Enum

class EquipmentCategory(str, Enum):
    """Categories of equipment."""
    SPREADING = "spreading"
    SPRAYING = "spraying"
    INJECTION = "injection"
    IRRIGATION = "irrigation"
    HANDLING = "handling"
    STORAGE = "storage"

class EquipmentStatus(str, Enum):
    """Status of equipment."""
    OPERATIONAL = "operational"
    MAINTENANCE = "maintenance"
    REPLACEMENT = "replacement"
    OUT_OF_SERVICE = "out_of_service"

class MaintenanceLevel(str, Enum):
    """Maintenance level categories."""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    PROFESSIONAL = "professional"

class EquipmentItem(BaseModel):
    """Represents a piece of farm equipment."""
    equipment_id: UUID = Field(..., description="Unique identifier for the equipment.")
    name: str = Field(..., description="Name of the equipment (e.g., 'Broadcast Spreader', 'No-Till Planter').")
    type: str = Field(..., description="Type of equipment (e.g., 'Spreader', 'Sprayer', 'Planter').")
    capacity_unit: str = Field(..., description="Unit of capacity (e.g., 'gallons', 'tons', 'rows').")
    capacity_value: float = Field(..., description="Numerical value of the capacity.")
    working_width_meters: Optional[float] = Field(None, description="Working width of the equipment in meters.")
    power_requirement_hp: Optional[int] = Field(None, description="Horsepower requirement for the equipment.")
    cost_usd: Optional[float] = Field(None, description="Estimated cost of the equipment in USD.")
    maintenance_cost_annual_usd: Optional[float] = Field(None, description="Estimated annual maintenance cost in USD.")
    is_available: bool = Field(True, description="Whether the equipment is currently available for use.")

class EquipmentInventory(BaseModel):
    """Equipment inventory management."""
    inventory_id: UUID = Field(..., description="Unique identifier for the inventory.")
    equipment_items: List[EquipmentItem] = Field(default_factory=list, description="List of equipment items.")
    last_updated: Optional[str] = Field(None, description="Last inventory update timestamp.")
    total_value_usd: float = Field(0.0, description="Total value of equipment inventory in USD.")

class EquipmentCompatibility(BaseModel):
    """Equipment compatibility assessment."""
    equipment_id: UUID = Field(..., description="Unique identifier for the equipment.")
    compatible_methods: List[str] = Field(default_factory=list, description="Compatible application methods.")
    compatibility_score: float = Field(..., ge=0, le=1, description="Compatibility score (0=not compatible, 1=fully compatible).")
    compatibility_notes: List[str] = Field(default_factory=list, description="Notes about compatibility.")
    limiting_factors: List[str] = Field(default_factory=list, description="Factors limiting compatibility.")

class EquipmentEfficiency(BaseModel):
    """Equipment efficiency metrics."""
    equipment_id: UUID = Field(..., description="Unique identifier for the equipment.")
    efficiency_metrics: Dict[str, float] = Field(default_factory=dict, description="Efficiency metrics (application_rate, accuracy, etc.).")
    overall_efficiency_score: float = Field(..., ge=0, le=1, description="Overall efficiency score.")
    benchmark_comparisons: Optional[Dict[str, float]] = Field(None, description="Comparisons to industry benchmarks.")
    improvement_recommendations: List[str] = Field(default_factory=list, description="Recommendations for improving efficiency.")

class EquipmentUpgrade(BaseModel):
    """Equipment upgrade information."""
    upgrade_id: UUID = Field(..., description="Unique identifier for the upgrade.")
    current_equipment_id: Optional[UUID] = Field(None, description="ID of current equipment being upgraded.")
    upgrade_type: str = Field(..., description="Type of upgrade (replacement, modification, etc.).")
    recommended_equipment: Optional[EquipmentItem] = Field(None, description="Recommended new equipment.")
    cost_benefit_analysis: Optional[Dict[str, Any]] = Field(None, description="Cost-benefit analysis of upgrade.")
    implementation_timeline: Optional[str] = Field(None, description="Timeline for implementation.")

class EquipmentAssessment(BaseModel):
    """Equipment assessment result."""
    assessment_id: UUID = Field(..., description="Unique identifier for the assessment.")
    equipment_id: UUID = Field(..., description="Equipment being assessed.")
    assessment_results: Dict[str, Any] = Field(default_factory=dict, description="Assessment results.")
    risk_factors: List[str] = Field(default_factory=list, description="Identified risk factors.")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations based on assessment.")
    next_assessment_date: Optional[str] = Field(None, description="Date for next assessment.")

class EquipmentMaintenance(BaseModel):
    """Equipment maintenance schedule and records."""
    maintenance_id: UUID = Field(..., description="Unique identifier for the maintenance record.")
    equipment_id: UUID = Field(..., description="Equipment ID for maintenance.")
    maintenance_type: str = Field(..., description="Type of maintenance (preventive, corrective, etc.).")
    scheduled_date: Optional[str] = Field(None, description="Scheduled date for maintenance.")
    completed_date: Optional[str] = Field(None, description="Date when maintenance was completed.")
    cost: Optional[float] = Field(None, description="Cost of maintenance.")
    maintenance_notes: List[str] = Field(default_factory=list, description="Notes about maintenance.")

class FertilizerFormulation(str, Enum):
    """Types of fertilizer formulations."""
    GRANULAR = "granular"
    LIQUID = "liquid"
    GASEOUS = "gaseous"
    SLOW_RELEASE = "slow_release"
    ORGANIC = "organic"

class ApplicationMethodType(str, Enum):
    """Types of fertilizer application methods."""
    BROADCAST = "broadcast"
    BAND = "band"
    SIDEDRESS = "sidedress"
    FOLIAR = "foliar"
    INJECTION = "injection"
    DRIP = "drip"
    FERTIGATION = "fertigation"

class CompatibilityMatrix(BaseModel):
    """Compatibility matrix for equipment and application methods."""
    matrix_id: UUID = Field(..., description="Unique identifier for the matrix.")
    equipment_id: UUID = Field(..., description="Equipment ID in the matrix.")
    method_compatibility: Dict[str, float] = Field(default_factory=dict, description="Compatibility scores for different methods.")
    fertilizer_compatibility: Dict[str, float] = Field(default_factory=dict, description="Compatibility scores for different fertilizers.")
    overall_compatibility_score: float = Field(..., ge=0, le=1, description="Overall compatibility score.")
    usage_restrictions: List[str] = Field(default_factory=list, description="Usage restrictions and limitations.")

class EquipmentRecommendation(BaseModel):
    """Equipment recommendation."""
    recommendation_id: UUID = Field(..., description="Unique identifier for the recommendation.")
    equipment_id: UUID = Field(..., description="Recommended equipment ID.")
    recommendation_reason: str = Field(..., description="Reason for the recommendation.")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence score in the recommendation.")
    expected_benefits: List[str] = Field(default_factory=list, description="Expected benefits from the recommendation.")
    implementation_notes: List[str] = Field(default_factory=list, description="Implementation notes and requirements.")

class FarmInfrastructure(BaseModel):
    """Represents the overall farm infrastructure relevant to fertilizer application."""
    farm_location_id: UUID = Field(..., description="Unique identifier for the farm location.")
    total_acres: float = Field(..., gt=0, description="Total acreage of the farm.")
    field_layout_complexity: float = Field(..., ge=0, le=1, description="Complexity of field layouts (0=simple, 1=complex).")
    access_road_quality: float = Field(..., ge=0, le=1, description="Quality of access roads (0=poor, 1=excellent).")
    storage_capacity_tons: Optional[float] = Field(None, description="Fertilizer storage capacity in tons.")
    labor_availability_score: float = Field(..., ge=0, le=1, description="Score for labor availability (0=low, 1=high).")
    existing_equipment: List[EquipmentItem] = Field(default_factory=list, description="List of existing farm equipment.")

class EquipmentSuitability(BaseModel):
    """Represents the suitability of a specific equipment item for a task."""
    equipment_id: UUID = Field(..., description="Unique identifier for the equipment.")
    suitability_score: float = Field(..., ge=0, le=1, description="Overall suitability score (0=unsuitable, 1=highly suitable).")
    reasons: List[str] = Field(default_factory=list, description="Reasons for the suitability score.")
    compatibility_issues: List[str] = Field(default_factory=list, description="Identified compatibility issues.")

class EquipmentUpgradeRecommendation(BaseModel):
    """Represents a recommendation for equipment upgrade or acquisition."""
    recommendation_id: UUID = Field(..., description="Unique identifier for the recommendation.")
    equipment_name: str = Field(..., description="Name of the recommended equipment.")
    type: str = Field(..., description="Type of recommended equipment.")
    justification: str = Field(..., description="Justification for the recommendation.")
    estimated_cost_usd: float = Field(..., description="Estimated cost of the recommended equipment.")
    expected_benefits: List[str] = Field(default_factory=list, description="Expected benefits from the upgrade.")
    roi_estimate: Optional[float] = Field(None, description="Estimated Return on Investment.")

class EquipmentAssessmentResult(BaseModel):
    """Comprehensive result of an equipment and farm infrastructure assessment."""
    farm_location_id: UUID = Field(..., description="Unique identifier for the farm location.")
    overall_assessment_score: float = Field(..., ge=0, le=1, description="Overall score for equipment and infrastructure.")
    equipment_suitability: List[EquipmentSuitability] = Field(default_factory=list, description="Suitability of existing equipment.")
    upgrade_recommendations: List[EquipmentUpgradeRecommendation] = Field(default_factory=list, description="Recommendations for equipment upgrades.")
    identified_gaps: List[str] = Field(default_factory=list, description="Identified gaps in current equipment or infrastructure.")
    efficiency_opportunities: List[str] = Field(default_factory=list, description="Opportunities for efficiency improvements.")

class IndividualEquipmentAssessment(BaseModel):
    """Represents an assessment of a single piece of equipment."""
    equipment_id: UUID = Field(..., description="Unique identifier for the equipment.")
    efficiency_score: float = Field(..., ge=0, le=1, description="Efficiency score of the equipment (0=low, 1=high).")
    maintenance_status: str = Field(..., description="Current maintenance status (e.g., 'good', 'needs_service').")
    compatibility_score: float = Field(..., ge=0, le=1, description="Compatibility score with current application methods.")
    notes: Optional[str] = Field(None, description="Additional notes on the equipment assessment.")

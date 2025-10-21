from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID

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

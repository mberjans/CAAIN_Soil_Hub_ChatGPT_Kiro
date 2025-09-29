"""
Farm Infrastructure Assessment Models

Data models for farm equipment inventory, capacity assessment,
and infrastructure upgrade recommendations.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal
from enum import Enum


class EquipmentCategory(str, Enum):
    """Categories of farm equipment."""
    TILLAGE = "tillage"
    PLANTING = "planting"
    IRRIGATION = "irrigation"
    STORAGE = "storage"
    HARVESTING = "harvesting"
    TRANSPORT = "transport"
    MAINTENANCE = "maintenance"
    OTHER = "other"


class EquipmentCondition(str, Enum):
    """Equipment condition levels."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


class EquipmentOwnershipType(str, Enum):
    """Equipment ownership types."""
    OWNED = "owned"
    LEASED = "leased"
    RENTED = "rented"
    SHARED = "shared"
    CUSTOM_HIRE = "custom_hire"


class CapacityLevel(str, Enum):
    """Capacity assessment levels."""
    UNDERUTILIZED = "underutilized"
    ADEQUATE = "adequate"
    OPTIMAL = "optimal"
    OVERUTILIZED = "overutilized"
    INSUFFICIENT = "insufficient"


class UpgradePriority(str, Enum):
    """Upgrade priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EquipmentSpecification(BaseModel):
    """Detailed equipment specifications."""
    model: str = Field(..., description="Equipment model")
    manufacturer: str = Field(..., description="Equipment manufacturer")
    year_manufactured: Optional[int] = Field(None, ge=1900, le=2030, description="Year manufactured")
    horsepower: Optional[float] = Field(None, ge=0, description="Horsepower rating")
    capacity: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Capacity specifications")
    dimensions: Optional[Dict[str, float]] = Field(default_factory=dict, description="Equipment dimensions")
    weight: Optional[float] = Field(None, ge=0, description="Equipment weight")
    fuel_type: Optional[str] = Field(None, description="Fuel type")
    fuel_capacity: Optional[float] = Field(None, ge=0, description="Fuel capacity")
    maintenance_schedule: Optional[str] = Field(None, description="Recommended maintenance schedule")


class EquipmentInventory(BaseModel):
    """Individual equipment inventory item."""
    equipment_id: UUID = Field(..., description="Unique equipment identifier")
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    equipment_name: str = Field(..., description="Equipment name")
    equipment_category: EquipmentCategory = Field(..., description="Equipment category")
    specifications: EquipmentSpecification = Field(..., description="Equipment specifications")
    ownership_type: EquipmentOwnershipType = Field(..., description="Ownership type")
    condition: EquipmentCondition = Field(..., description="Current condition")
    acquisition_date: Optional[date] = Field(None, description="Date of acquisition")
    purchase_price: Optional[Decimal] = Field(None, ge=0, description="Purchase price")
    current_value: Optional[Decimal] = Field(None, ge=0, description="Current estimated value")
    annual_maintenance_cost: Optional[Decimal] = Field(None, ge=0, description="Annual maintenance cost")
    utilization_rate: Optional[float] = Field(None, ge=0, le=1, description="Current utilization rate")
    field_compatibility: List[UUID] = Field(default_factory=list, description="Compatible field IDs")
    notes: Optional[str] = Field(None, description="Additional notes")
    last_maintenance_date: Optional[date] = Field(None, description="Last maintenance date")
    next_maintenance_due: Optional[date] = Field(None, description="Next maintenance due date")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('utilization_rate')
    @classmethod
    def validate_utilization_rate(cls, v):
        if v is not None and (v < 0 or v > 1):
            raise ValueError('Utilization rate must be between 0 and 1')
        return v


class CapacityAssessment(BaseModel):
    """Equipment capacity assessment."""
    assessment_id: UUID = Field(..., description="Unique assessment identifier")
    equipment_id: UUID = Field(..., description="Equipment identifier")
    field_id: Optional[UUID] = Field(None, description="Field identifier")
    assessment_date: datetime = Field(default_factory=datetime.utcnow)
    
    # Capacity metrics
    current_capacity: float = Field(..., ge=0, description="Current capacity")
    required_capacity: float = Field(..., ge=0, description="Required capacity")
    capacity_level: CapacityLevel = Field(..., description="Capacity level assessment")
    capacity_utilization_percent: float = Field(..., ge=0, le=100, description="Capacity utilization percentage")
    
    # Performance metrics
    efficiency_score: float = Field(..., ge=0, le=1, description="Efficiency score")
    productivity_score: float = Field(..., ge=0, le=1, description="Productivity score")
    reliability_score: float = Field(..., ge=0, le=1, description="Reliability score")
    
    # Constraints and limitations
    operational_constraints: List[str] = Field(default_factory=list, description="Operational constraints")
    maintenance_requirements: List[str] = Field(default_factory=list, description="Maintenance requirements")
    upgrade_potential: str = Field(..., description="Upgrade potential assessment")
    
    # Recommendations
    capacity_recommendations: List[str] = Field(default_factory=list, description="Capacity recommendations")
    optimization_opportunities: List[str] = Field(default_factory=list, description="Optimization opportunities")
    
    @field_validator('capacity_utilization_percent')
    @classmethod
    def validate_capacity_utilization(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Capacity utilization percentage must be between 0 and 100')
        return v


class UpgradeRecommendation(BaseModel):
    """Equipment upgrade recommendation."""
    recommendation_id: UUID = Field(..., description="Unique recommendation identifier")
    equipment_id: Optional[UUID] = Field(None, description="Equipment identifier")
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    recommendation_type: str = Field(..., description="Type of recommendation")
    title: str = Field(..., description="Recommendation title")
    description: str = Field(..., description="Detailed description")
    priority: UpgradePriority = Field(..., description="Priority level")
    
    # Financial analysis
    estimated_cost: Decimal = Field(..., ge=0, description="Estimated cost")
    annual_savings: Optional[Decimal] = Field(None, ge=0, description="Annual cost savings")
    payback_period_years: Optional[float] = Field(None, ge=0, description="Payback period in years")
    roi_percentage: Optional[float] = Field(None, description="Return on investment percentage")
    
    # Implementation details
    implementation_timeline_days: int = Field(..., ge=0, description="Implementation timeline in days")
    required_resources: List[str] = Field(default_factory=list, description="Required resources")
    dependencies: List[str] = Field(default_factory=list, description="Implementation dependencies")
    
    # Benefits
    expected_benefits: List[str] = Field(default_factory=list, description="Expected benefits")
    capacity_improvement: Optional[float] = Field(None, ge=0, description="Capacity improvement percentage")
    efficiency_improvement: Optional[float] = Field(None, ge=0, description="Efficiency improvement percentage")
    maintenance_reduction: Optional[float] = Field(None, ge=0, description="Maintenance cost reduction percentage")
    
    # Risk assessment
    implementation_risks: List[str] = Field(default_factory=list, description="Implementation risks")
    mitigation_strategies: List[str] = Field(default_factory=list, description="Risk mitigation strategies")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class FarmInfrastructureAssessment(BaseModel):
    """Comprehensive farm infrastructure assessment."""
    assessment_id: UUID = Field(..., description="Unique assessment identifier")
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    assessment_date: datetime = Field(default_factory=datetime.utcnow)
    
    # Farm characteristics
    total_acres: float = Field(..., ge=0, description="Total farm acres")
    field_count: int = Field(..., ge=0, description="Number of fields")
    average_field_size: float = Field(..., ge=0, description="Average field size in acres")
    field_layout_complexity: str = Field(..., description="Field layout complexity rating")
    
    # Equipment inventory summary
    equipment_inventory: List[EquipmentInventory] = Field(default_factory=list)
    total_equipment_value: Decimal = Field(..., ge=0, description="Total equipment value")
    equipment_age_distribution: Dict[str, int] = Field(default_factory=dict, description="Equipment age distribution")
    condition_distribution: Dict[EquipmentCondition, int] = Field(default_factory=dict, description="Condition distribution")
    
    # Capacity assessments
    capacity_assessments: List[CapacityAssessment] = Field(default_factory=list)
    overall_capacity_score: float = Field(..., ge=0, le=1, description="Overall capacity score")
    capacity_bottlenecks: List[str] = Field(default_factory=list, description="Identified capacity bottlenecks")
    
    # Upgrade recommendations
    upgrade_recommendations: List[UpgradeRecommendation] = Field(default_factory=list)
    total_upgrade_cost: Decimal = Field(..., ge=0, description="Total upgrade cost")
    total_annual_savings: Decimal = Field(..., ge=0, description="Total annual savings")
    overall_roi: Optional[float] = Field(None, description="Overall return on investment")
    
    # Assessment summary
    strengths: List[str] = Field(default_factory=list, description="Infrastructure strengths")
    weaknesses: List[str] = Field(default_factory=list, description="Infrastructure weaknesses")
    opportunities: List[str] = Field(default_factory=list, description="Improvement opportunities")
    threats: List[str] = Field(default_factory=list, description="Potential threats")
    
    # Recommendations
    immediate_actions: List[str] = Field(default_factory=list, description="Immediate action items")
    short_term_goals: List[str] = Field(default_factory=list, description="Short-term goals (1-2 years)")
    long_term_goals: List[str] = Field(default_factory=list, description="Long-term goals (3-5 years)")
    
    # Assessment metadata
    assessor: Optional[str] = Field(None, description="Assessment conducted by")
    assessment_method: str = Field(..., description="Assessment method used")
    confidence_score: float = Field(..., ge=0, le=1, description="Assessment confidence score")
    next_assessment_due: Optional[date] = Field(None, description="Next assessment due date")


# Request Models
class EquipmentInventoryRequest(BaseModel):
    """Request model for equipment inventory operations."""
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    equipment_category: Optional[EquipmentCategory] = Field(None, description="Filter by equipment category")
    condition: Optional[EquipmentCondition] = Field(None, description="Filter by equipment condition")
    ownership_type: Optional[EquipmentOwnershipType] = Field(None, description="Filter by ownership type")
    include_specifications: bool = Field(True, description="Include detailed specifications")
    include_assessments: bool = Field(False, description="Include capacity assessments")


class CapacityAssessmentRequest(BaseModel):
    """Request model for capacity assessment."""
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    equipment_ids: Optional[List[UUID]] = Field(None, description="Specific equipment IDs to assess")
    field_ids: Optional[List[UUID]] = Field(None, description="Specific field IDs to assess")
    assessment_depth: str = Field("standard", description="Assessment depth (basic, standard, comprehensive)")
    include_recommendations: bool = Field(True, description="Include upgrade recommendations")
    cost_analysis: bool = Field(True, description="Include cost-benefit analysis")


class InfrastructureAssessmentRequest(BaseModel):
    """Request model for comprehensive infrastructure assessment."""
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    assessment_scope: str = Field("comprehensive", description="Assessment scope (basic, standard, comprehensive)")
    include_equipment_inventory: bool = Field(True, description="Include equipment inventory")
    include_capacity_assessment: bool = Field(True, description="Include capacity assessment")
    include_upgrade_recommendations: bool = Field(True, description="Include upgrade recommendations")
    budget_constraints: Optional[Decimal] = Field(None, ge=0, description="Budget constraints")
    timeline_preferences: Optional[str] = Field(None, description="Implementation timeline preferences")
    priority_focus: Optional[List[str]] = Field(None, description="Priority focus areas")


# Response Models
class EquipmentInventoryResponse(BaseModel):
    """Response model for equipment inventory queries."""
    request_id: UUID = Field(..., description="Unique request identifier")
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    equipment_inventory: List[EquipmentInventory] = Field(..., description="Equipment inventory")
    inventory_summary: Dict[str, Any] = Field(..., description="Inventory summary")
    total_count: int = Field(..., description="Total equipment count")
    total_value: Decimal = Field(..., description="Total equipment value")
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class CapacityAssessmentResponse(BaseModel):
    """Response model for capacity assessment."""
    request_id: UUID = Field(..., description="Unique request identifier")
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    capacity_assessments: List[CapacityAssessment] = Field(..., description="Capacity assessments")
    overall_capacity_score: float = Field(..., description="Overall capacity score")
    capacity_summary: Dict[str, Any] = Field(..., description="Capacity summary")
    recommendations: List[str] = Field(default_factory=list, description="Capacity recommendations")
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class UpgradeRecommendationResponse(BaseModel):
    """Response model for upgrade recommendations."""
    request_id: UUID = Field(..., description="Unique request identifier")
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    upgrade_recommendations: List[UpgradeRecommendation] = Field(..., description="Upgrade recommendations")
    total_investment_required: Decimal = Field(..., description="Total investment required")
    total_annual_savings: Decimal = Field(..., description="Total annual savings")
    overall_roi: Optional[float] = Field(None, description="Overall return on investment")
    implementation_priority: List[str] = Field(default_factory=list, description="Implementation priority order")
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class InfrastructureAssessmentResponse(BaseModel):
    """Response model for comprehensive infrastructure assessment."""
    request_id: UUID = Field(..., description="Unique request identifier")
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    assessment: FarmInfrastructureAssessment = Field(..., description="Complete infrastructure assessment")
    executive_summary: Dict[str, Any] = Field(..., description="Executive summary")
    key_findings: List[str] = Field(default_factory=list, description="Key findings")
    action_plan: Dict[str, Any] = Field(..., description="Action plan")
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# Equipment Management Models
class EquipmentMaintenanceRecord(BaseModel):
    """Equipment maintenance record."""
    maintenance_id: UUID = Field(..., description="Unique maintenance identifier")
    equipment_id: UUID = Field(..., description="Equipment identifier")
    maintenance_date: date = Field(..., description="Maintenance date")
    maintenance_type: str = Field(..., description="Type of maintenance")
    description: str = Field(..., description="Maintenance description")
    cost: Decimal = Field(..., ge=0, description="Maintenance cost")
    performed_by: str = Field(..., description="Who performed maintenance")
    next_maintenance_due: Optional[date] = Field(None, description="Next maintenance due date")
    notes: Optional[str] = Field(None, description="Additional notes")


class EquipmentUtilizationRecord(BaseModel):
    """Equipment utilization tracking record."""
    utilization_id: UUID = Field(..., description="Unique utilization identifier")
    equipment_id: UUID = Field(..., description="Equipment identifier")
    field_id: Optional[UUID] = Field(None, description="Field identifier")
    utilization_date: date = Field(..., description="Utilization date")
    hours_used: float = Field(..., ge=0, description="Hours used")
    acres_covered: Optional[float] = Field(None, ge=0, description="Acres covered")
    fuel_consumed: Optional[float] = Field(None, ge=0, description="Fuel consumed")
    efficiency_rating: Optional[float] = Field(None, ge=0, le=1, description="Efficiency rating")
    notes: Optional[str] = Field(None, description="Additional notes")


class EquipmentPerformanceMetrics(BaseModel):
    """Equipment performance metrics."""
    metrics_id: UUID = Field(..., description="Unique metrics identifier")
    equipment_id: UUID = Field(..., description="Equipment identifier")
    calculation_period_start: date = Field(..., description="Calculation period start")
    calculation_period_end: date = Field(..., description="Calculation period end")
    
    # Utilization metrics
    total_hours_used: float = Field(..., ge=0, description="Total hours used")
    utilization_rate: float = Field(..., ge=0, le=1, description="Utilization rate")
    availability_rate: float = Field(..., ge=0, le=1, description="Availability rate")
    
    # Performance metrics
    efficiency_score: float = Field(..., ge=0, le=1, description="Efficiency score")
    productivity_score: float = Field(..., ge=0, le=1, description="Productivity score")
    reliability_score: float = Field(..., ge=0, le=1, description="Reliability score")
    
    # Cost metrics
    total_operating_cost: Decimal = Field(..., ge=0, description="Total operating cost")
    cost_per_hour: Decimal = Field(..., ge=0, description="Cost per hour")
    cost_per_acre: Optional[Decimal] = Field(None, ge=0, description="Cost per acre")
    
    # Maintenance metrics
    maintenance_cost: Decimal = Field(..., ge=0, description="Maintenance cost")
    downtime_hours: float = Field(..., ge=0, description="Downtime hours")
    maintenance_frequency: float = Field(..., ge=0, description="Maintenance frequency")
    
    calculated_at: datetime = Field(default_factory=datetime.utcnow)
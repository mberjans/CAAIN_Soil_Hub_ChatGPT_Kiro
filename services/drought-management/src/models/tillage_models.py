"""
Tillage Optimization Data Models

Pydantic models for tillage practice optimization,
assessment, and transition planning for drought management.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal
from enum import Enum

# Enums for tillage optimization
class TillageSystem(str, Enum):
    """Tillage system classifications."""
    NO_TILL = "no_till"
    STRIP_TILL = "strip_till"
    REDUCED_TILL = "reduced_till"
    VERTICAL_TILL = "vertical_till"
    CONVENTIONAL = "conventional"
    MINIMUM_TILL = "minimum_till"

class TillageEquipment(str, Enum):
    """Tillage equipment types."""
    NO_TILL_DRILL = "no_till_drill"
    STRIP_TILL_IMPLEMENT = "strip_till_implement"
    CHISEL_PLOW = "chisel_plow"
    MOLDBOARD_PLOW = "moldboard_plow"
    DISK_HARROW = "disk_harrow"
    FIELD_CULTIVATOR = "field_cultivator"
    VERTICAL_TILLAGE_TOOL = "vertical_tillage_tool"
    ROTARY_HOE = "rotary_hoe"
    ROW_CULTIVATOR = "row_cultivator"

class TransitionPhase(str, Enum):
    """Tillage transition phases."""
    PLANNING = "planning"
    PREPARATION = "preparation"
    IMPLEMENTATION = "implementation"
    ADAPTATION = "adaptation"
    OPTIMIZATION = "optimization"
    MAINTENANCE = "maintenance"

class SoilType(str, Enum):
    """Soil types for tillage optimization."""
    CLAY = "clay"
    CLAY_LOAM = "clay_loam"
    LOAM = "loam"
    SANDY_LOAM = "sandy_loam"
    SANDY_CLAY_LOAM = "sandy_clay_loam"
    SILT_LOAM = "silt_loam"
    SAND = "sand"
    SILT = "silt"

class CropType(str, Enum):
    """Crop types for tillage compatibility."""
    CORN = "corn"
    SOYBEAN = "soybean"
    WHEAT = "wheat"
    COTTON = "cotton"
    SORGHUM = "sorghum"
    SUNFLOWER = "sunflower"
    CANOLA = "canola"
    BARLEY = "barley"
    OATS = "oats"
    RYE = "rye"

# Core tillage optimization models
class TillageOptimizationRequest(BaseModel):
    """Request model for tillage optimization."""
    field_id: UUID = Field(..., description="Unique field identifier")
    current_tillage_system: TillageSystem = Field(..., description="Current tillage system")
    soil_type: SoilType = Field(..., description="Primary soil type")
    soil_texture: str = Field(..., description="Detailed soil texture description")
    field_size_acres: float = Field(..., ge=0.1, le=10000, description="Field size in acres")
    slope_percent: float = Field(..., ge=0, le=45, description="Field slope percentage")
    drainage_class: str = Field(..., description="Soil drainage classification")
    organic_matter_percent: float = Field(..., ge=0, le=20, description="Soil organic matter percentage")
    compaction_level: str = Field(..., description="Current soil compaction level")
    crop_rotation: List[CropType] = Field(..., description="Planned crop rotation")
    equipment_available: List[TillageEquipment] = Field(default_factory=list, description="Available tillage equipment")
    irrigation_available: bool = Field(default=False, description="Irrigation availability")
    cover_crop_usage: bool = Field(default=False, description="Cover crop usage intention")
    water_conservation_priority: float = Field(..., ge=0, le=10, description="Water conservation priority (1-10)")
    soil_health_priority: float = Field(..., ge=0, le=10, description="Soil health priority (1-10)")
    labor_availability: float = Field(..., ge=0, le=10, description="Labor availability (1-10)")
    budget_constraints: Optional[Decimal] = Field(None, description="Budget constraints for equipment")

class TillageSystemAssessment(BaseModel):
    """Assessment of a specific tillage system."""
    tillage_system: TillageSystem = Field(..., description="Tillage system type")
    water_conservation_score: float = Field(..., ge=0, le=100, description="Water conservation effectiveness score")
    soil_health_score: float = Field(..., ge=0, le=100, description="Soil health improvement score")
    erosion_control_score: float = Field(..., ge=0, le=100, description="Erosion control effectiveness score")
    fuel_efficiency_score: float = Field(..., ge=0, le=100, description="Fuel efficiency score")
    labor_efficiency_score: float = Field(..., ge=0, le=100, description="Labor efficiency score")
    equipment_cost_score: float = Field(..., ge=0, le=100, description="Equipment cost effectiveness score")
    crop_yield_potential: float = Field(..., ge=0, le=100, description="Crop yield potential score")
    overall_score: float = Field(..., ge=0, le=100, description="Overall system score")
    compatibility_score: float = Field(..., ge=0, le=100, description="Compatibility with field conditions")
    transition_difficulty: str = Field(..., description="Transition difficulty level")
    benefits: List[str] = Field(default_factory=list, description="Key benefits of this system")
    challenges: List[str] = Field(default_factory=list, description="Potential challenges")
    recommendations: List[str] = Field(default_factory=list, description="Implementation recommendations")

class EquipmentRecommendation(BaseModel):
    """Equipment recommendation for tillage system."""
    equipment_type: TillageEquipment = Field(..., description="Recommended equipment type")
    equipment_name: str = Field(..., description="Specific equipment name/model")
    estimated_cost: Decimal = Field(..., description="Estimated equipment cost")
    cost_per_acre: Decimal = Field(..., description="Cost per acre")
    fuel_consumption: float = Field(..., description="Fuel consumption per acre")
    labor_hours_per_acre: float = Field(..., description="Labor hours required per acre")
    maintenance_cost_per_year: Decimal = Field(..., description="Annual maintenance cost")
    lifespan_years: int = Field(..., description="Expected equipment lifespan")
    compatibility_score: float = Field(..., ge=0, le=100, description="Compatibility with field conditions")
    priority_level: str = Field(..., description="Priority level for acquisition")

class TransitionPlan(BaseModel):
    """Multi-year transition plan for tillage system change."""
    target_system: TillageSystem = Field(..., description="Target tillage system")
    transition_duration_years: int = Field(..., ge=1, le=5, description="Transition duration in years")
    phases: List[Dict[str, Any]] = Field(..., description="Transition phases with timelines")
    equipment_acquisition_plan: List[EquipmentRecommendation] = Field(default_factory=list, description="Equipment acquisition timeline")
    cost_breakdown: Dict[str, Decimal] = Field(default_factory=dict, description="Cost breakdown by category")
    risk_assessment: Dict[str, Any] = Field(default_factory=dict, description="Risk assessment and mitigation")
    success_metrics: List[str] = Field(default_factory=list, description="Success metrics to track")
    timeline: List[Dict[str, Any]] = Field(default_factory=list, description="Detailed implementation timeline")

class TillageOptimizationResponse(BaseModel):
    """Response model for tillage optimization."""
    request_id: str = Field(..., description="Unique request identifier")
    field_id: UUID = Field(..., description="Field identifier")
    current_system_assessment: TillageSystemAssessment = Field(..., description="Current system assessment")
    recommended_systems: List[TillageSystemAssessment] = Field(..., description="Recommended tillage systems")
    optimal_system: TillageSystemAssessment = Field(..., description="Optimal tillage system recommendation")
    equipment_recommendations: List[EquipmentRecommendation] = Field(default_factory=list, description="Equipment recommendations")
    transition_plan: Optional[TransitionPlan] = Field(None, description="Transition plan if system change recommended")
    water_savings_potential: Dict[str, float] = Field(default_factory=dict, description="Water savings potential")
    soil_health_improvements: Dict[str, float] = Field(default_factory=dict, description="Soil health improvement potential")
    economic_analysis: Dict[str, Any] = Field(default_factory=dict, description="Economic analysis and ROI")
    implementation_priority: str = Field(..., description="Implementation priority level")
    confidence_score: float = Field(..., ge=0, le=100, description="Recommendation confidence score")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Response creation timestamp")

class TillagePracticeComparison(BaseModel):
    """Comparison between different tillage practices."""
    practice_name: str = Field(..., description="Tillage practice name")
    water_conservation: float = Field(..., ge=0, le=100, description="Water conservation score")
    soil_health: float = Field(..., ge=0, le=100, description="Soil health score")
    erosion_control: float = Field(..., ge=0, le=100, description="Erosion control score")
    fuel_efficiency: float = Field(..., ge=0, le=100, description="Fuel efficiency score")
    labor_requirements: float = Field(..., ge=0, le=100, description="Labor efficiency score")
    equipment_costs: float = Field(..., ge=0, le=100, description="Equipment cost score")
    crop_yield: float = Field(..., ge=0, le=100, description="Crop yield potential")
    overall_score: float = Field(..., ge=0, le=100, description="Overall practice score")
    pros: List[str] = Field(default_factory=list, description="Advantages")
    cons: List[str] = Field(default_factory=list, description="Disadvantages")
    best_for: List[str] = Field(default_factory=list, description="Best suited for")

class TillageMonitoringMetrics(BaseModel):
    """Metrics for monitoring tillage practice effectiveness."""
    field_id: UUID = Field(..., description="Field identifier")
    tillage_system: TillageSystem = Field(..., description="Current tillage system")
    measurement_date: date = Field(..., description="Measurement date")
    soil_moisture_percent: float = Field(..., ge=0, le=100, description="Soil moisture percentage")
    soil_temperature_celsius: float = Field(..., description="Soil temperature")
    infiltration_rate_inches_per_hour: float = Field(..., ge=0, description="Water infiltration rate")
    soil_compaction_psi: float = Field(..., ge=0, description="Soil compaction in PSI")
    organic_matter_percent: float = Field(..., ge=0, le=20, description="Soil organic matter percentage")
    erosion_indicators: Dict[str, Any] = Field(default_factory=dict, description="Erosion indicators")
    crop_yield_bushels_per_acre: Optional[float] = Field(None, description="Crop yield")
    fuel_consumption_gallons_per_acre: float = Field(..., ge=0, description="Fuel consumption")
    labor_hours_per_acre: float = Field(..., ge=0, description="Labor hours")
    cost_per_acre: Decimal = Field(..., description="Total cost per acre")

class TillageEffectivenessReport(BaseModel):
    """Report on tillage practice effectiveness over time."""
    field_id: UUID = Field(..., description="Field identifier")
    report_period_start: date = Field(..., description="Report period start date")
    report_period_end: date = Field(..., description="Report period end date")
    tillage_system: TillageSystem = Field(..., description="Tillage system used")
    metrics_summary: Dict[str, float] = Field(..., description="Summary of key metrics")
    trends: Dict[str, str] = Field(default_factory=dict, description="Trend analysis")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for improvement")
    success_indicators: List[str] = Field(default_factory=list, description="Success indicators")
    areas_for_improvement: List[str] = Field(default_factory=list, description="Areas needing improvement")
    next_monitoring_date: date = Field(..., description="Next recommended monitoring date")

# Validation methods
class TillageOptimizationValidator:
    """Validator for tillage optimization data."""
    
    @staticmethod
    def validate_field_conditions(request: TillageOptimizationRequest) -> List[str]:
        """Validate field conditions for tillage optimization."""
        issues = []
        
        if request.slope_percent > 15 and request.current_tillage_system == TillageSystem.CONVENTIONAL:
            issues.append("High slope may require conservation tillage for erosion control")
        
        if request.soil_type in [SoilType.CLAY, SoilType.CLAY_LOAM] and request.current_tillage_system == TillageSystem.NO_TILL:
            issues.append("Heavy clay soils may require gradual transition to no-till")
        
        if request.organic_matter_percent < 2.0 and request.current_tillage_system == TillageSystem.NO_TILL:
            issues.append("Low organic matter may limit no-till success")
        
        return issues
    
    @staticmethod
    def validate_equipment_compatibility(equipment: TillageEquipment, soil_type: SoilType) -> bool:
        """Validate equipment compatibility with soil type."""
        compatibility_matrix = {
            TillageEquipment.NO_TILL_DRILL: [SoilType.LOAM, SoilType.SANDY_LOAM, SoilType.SILT_LOAM],
            TillageEquipment.STRIP_TILL_IMPLEMENT: [SoilType.CLAY_LOAM, SoilType.LOAM, SoilType.SANDY_LOAM],
            TillageEquipment.CHISEL_PLOW: [SoilType.CLAY, SoilType.CLAY_LOAM, SoilType.LOAM],
            TillageEquipment.MOLDBOARD_PLOW: [SoilType.CLAY, SoilType.CLAY_LOAM, SoilType.LOAM],
            TillageEquipment.DISK_HARROW: [SoilType.SANDY_LOAM, SoilType.LOAM, SoilType.SILT_LOAM],
            TillageEquipment.VERTICAL_TILLAGE_TOOL: [SoilType.LOAM, SoilType.SANDY_LOAM, SoilType.SILT_LOAM]
        }
        
        return soil_type in compatibility_matrix.get(equipment, [])
    
    @staticmethod
    def calculate_transition_difficulty(current: TillageSystem, target: TillageSystem) -> str:
        """Calculate transition difficulty between tillage systems."""
        difficulty_matrix = {
            TillageSystem.CONVENTIONAL: {
                TillageSystem.REDUCED_TILL: "low",
                TillageSystem.STRIP_TILL: "medium",
                TillageSystem.NO_TILL: "high"
            },
            TillageSystem.REDUCED_TILL: {
                TillageSystem.STRIP_TILL: "low",
                TillageSystem.NO_TILL: "medium"
            },
            TillageSystem.STRIP_TILL: {
                TillageSystem.NO_TILL: "low"
            }
        }
        
        return difficulty_matrix.get(current, {}).get(target, "high")
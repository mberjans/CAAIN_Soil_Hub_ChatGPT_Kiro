"""
Crop Rotation Planning Data Models
Comprehensive data models for crop rotation planning and field history management.
"""

from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from pydantic import BaseModel, Field, validator
import uuid


class RotationGoalType(Enum):
    """Types of rotation goals."""
    SOIL_HEALTH = "soil_health"
    PROFIT_MAXIMIZATION = "profit_maximization"
    PEST_MANAGEMENT = "pest_management"
    DISEASE_MANAGEMENT = "disease_management"
    SUSTAINABILITY = "sustainability"
    RISK_REDUCTION = "risk_reduction"
    LABOR_OPTIMIZATION = "labor_optimization"
    EQUIPMENT_UTILIZATION = "equipment_utilization"


class ConstraintType(Enum):
    """Types of rotation constraints."""
    REQUIRED_CROP = "required_crop"
    EXCLUDED_CROP = "excluded_crop"
    SEQUENCE_RULE = "sequence_rule"
    TIMING_CONSTRAINT = "timing_constraint"
    EQUIPMENT_LIMITATION = "equipment_limitation"
    LABOR_CONSTRAINT = "labor_constraint"
    MARKET_CONTRACT = "market_contract"
    REGULATORY = "regulatory"


class RotationBenefitType(Enum):
    """Types of rotation benefits."""
    NITROGEN_FIXATION = "nitrogen_fixation"
    PEST_BREAK = "pest_break"
    DISEASE_BREAK = "disease_break"
    SOIL_STRUCTURE = "soil_structure"
    ORGANIC_MATTER = "organic_matter"
    EROSION_CONTROL = "erosion_control"
    WATER_RETENTION = "water_retention"
    BIODIVERSITY = "biodiversity"
    ECONOMIC = "economic"


@dataclass
class FieldHistoryRecord:
    """Single year field history record."""
    year: int
    crop_name: str
    variety: Optional[str] = None
    planting_date: Optional[date] = None
    harvest_date: Optional[date] = None
    yield_amount: Optional[float] = None
    yield_units: str = "bu/acre"
    
    # Management practices
    tillage_type: Optional[str] = None
    fertilizer_applications: List[Dict] = field(default_factory=list)
    pesticide_applications: List[Dict] = field(default_factory=list)
    irrigation_used: bool = False
    cover_crop: Optional[str] = None
    
    # Performance metrics
    gross_revenue: Optional[float] = None
    total_costs: Optional[float] = None
    net_profit: Optional[float] = None
    
    # Soil and environmental data
    soil_test_results: Optional[Dict] = None
    pest_pressure: Optional[Dict] = None
    disease_incidents: Optional[Dict] = None
    weather_impacts: Optional[Dict] = None
    
    # Notes and observations
    notes: Optional[str] = None
    photos: List[str] = field(default_factory=list)
    documents: List[str] = field(default_factory=list)


@dataclass
class FieldProfile:
    """Complete field profile with history and characteristics."""
    field_id: str
    field_name: str
    farm_id: str
    
    # Physical characteristics
    size_acres: float
    soil_type: Optional[str] = None
    drainage_class: Optional[str] = None
    slope_percent: Optional[float] = None
    irrigation_available: bool = False
    
    # Location and climate
    coordinates: Optional[tuple] = None
    climate_zone: Optional[str] = None
    elevation_ft: Optional[float] = None
    
    # Field history
    history: List[FieldHistoryRecord] = field(default_factory=list)
    
    # Current status
    current_crop: Optional[str] = None
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def get_history_years(self) -> List[int]:
        """Get list of years with history data."""
        return sorted([record.year for record in self.history])
    
    def get_crop_sequence(self, years: int = 5) -> List[str]:
        """Get recent crop sequence."""
        recent_history = sorted(
            [r for r in self.history if r.year >= (datetime.now().year - years)],
            key=lambda x: x.year
        )
        return [record.crop_name for record in recent_history]
    
    def get_average_yield(self, crop_name: str) -> Optional[float]:
        """Get average yield for a specific crop."""
        yields = [
            r.yield_amount for r in self.history 
            if r.crop_name == crop_name and r.yield_amount is not None
        ]
        return sum(yields) / len(yields) if yields else None


@dataclass
class RotationGoal:
    """Rotation planning goal with priority and targets."""
    goal_id: str
    goal_type: RotationGoalType
    priority: int  # 1-10, higher is more important
    weight: float  # 0.0-1.0, relative importance
    
    # Goal-specific targets
    target_value: Optional[float] = None
    target_units: Optional[str] = None
    target_timeframe: int = 5  # years
    
    # Goal description and constraints
    description: str = ""
    constraints: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    
    # Measurement and tracking
    baseline_value: Optional[float] = None
    current_value: Optional[float] = None
    progress_tracking: List[Dict] = field(default_factory=list)


@dataclass
class RotationConstraint:
    """Rotation planning constraint."""
    constraint_id: str
    constraint_type: ConstraintType
    field_id: Optional[str] = None  # None for farm-wide constraints
    
    # Constraint definition
    description: str = ""
    is_hard_constraint: bool = True  # False for soft constraints
    violation_penalty: float = 1.0
    
    # Constraint parameters
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Temporal aspects
    applies_to_years: Optional[List[int]] = None
    seasonal_restrictions: Optional[Dict] = None
    
    # Flexibility and alternatives
    can_be_relaxed: bool = False
    relaxation_cost: Optional[float] = None
    alternatives: List[str] = field(default_factory=list)


@dataclass
class CropRotationPlan:
    """Multi-year crop rotation plan for a field."""
    plan_id: str
    field_id: str
    farm_id: str
    
    # Plan metadata
    plan_name: str
    created_date: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    version: int = 1
    
    # Rotation schedule
    rotation_years: Dict[int, str] = field(default_factory=dict)  # year -> crop_name
    rotation_details: Dict[int, Dict] = field(default_factory=dict)  # year -> details
    
    # Plan parameters
    planning_horizon: int = 5  # years
    start_year: int = field(default_factory=lambda: datetime.now().year)
    
    # Goals and constraints used
    goals: List[RotationGoal] = field(default_factory=list)
    constraints: List[RotationConstraint] = field(default_factory=list)
    
    # Plan evaluation
    overall_score: Optional[float] = None
    benefit_scores: Dict[str, float] = field(default_factory=dict)
    risk_scores: Dict[str, float] = field(default_factory=dict)
    economic_projections: Optional[Dict] = None
    
    # Plan status
    is_active: bool = True
    implementation_status: Dict[int, str] = field(default_factory=dict)
    actual_vs_planned: Dict[int, Dict] = field(default_factory=dict)
    
    def get_crop_sequence(self) -> List[str]:
        """Get ordered crop sequence."""
        years = sorted(self.rotation_years.keys())
        return [self.rotation_years[year] for year in years]
    
    def get_year_details(self, year: int) -> Optional[Dict]:
        """Get detailed plan for specific year."""
        return self.rotation_details.get(year)
    
    def update_implementation_status(self, year: int, status: str, actual_data: Dict = None):
        """Update implementation status for a year."""
        self.implementation_status[year] = status
        if actual_data:
            self.actual_vs_planned[year] = actual_data


@dataclass
class RotationBenefit:
    """Quantified rotation benefit."""
    benefit_id: str
    benefit_type: RotationBenefitType
    field_id: str
    
    # Benefit quantification
    estimated_value: float
    value_units: str
    confidence_level: float  # 0.0-1.0
    
    # Temporal aspects
    realization_year: int
    duration_years: int = 1
    cumulative_effect: bool = False
    
    # Benefit details
    description: str = ""
    calculation_method: str = ""
    supporting_research: List[str] = field(default_factory=list)
    
    # Economic impact
    economic_value: Optional[float] = None
    cost_savings: Optional[float] = None
    revenue_increase: Optional[float] = None
    
    # Risk and uncertainty
    risk_factors: List[str] = field(default_factory=list)
    sensitivity_analysis: Optional[Dict] = None


@dataclass
class RotationAnalysis:
    """Comprehensive rotation analysis results."""
    analysis_id: str
    plan_id: str
    analysis_date: datetime = field(default_factory=datetime.utcnow)
    
    # Overall assessment
    overall_score: float
    recommendation_confidence: float
    
    # Benefit analysis
    total_benefits: List[RotationBenefit] = field(default_factory=list)
    benefit_summary: Dict[str, float] = field(default_factory=dict)
    
    # Risk analysis
    risk_factors: List[Dict] = field(default_factory=list)
    risk_mitigation: List[str] = field(default_factory=list)
    
    # Economic analysis
    economic_summary: Dict[str, float] = field(default_factory=dict)
    profitability_projection: Dict[int, float] = field(default_factory=dict)
    break_even_analysis: Optional[Dict] = None
    
    # Sustainability metrics
    sustainability_score: float = 0.0
    environmental_impact: Dict[str, float] = field(default_factory=dict)
    
    # Comparison with alternatives
    alternative_scenarios: List[Dict] = field(default_factory=list)
    sensitivity_analysis: Dict[str, Dict] = field(default_factory=dict)
    
    # Recommendations and insights
    key_insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


# Pydantic models for API requests/responses

class FieldHistoryRequest(BaseModel):
    """Request model for field history input."""
    year: int = Field(..., ge=1900, le=2100)
    crop_name: str = Field(..., min_length=1, max_length=100)
    variety: Optional[str] = Field(None, max_length=100)
    planting_date: Optional[date] = None
    harvest_date: Optional[date] = None
    yield_amount: Optional[float] = Field(None, ge=0)
    yield_units: str = Field("bu/acre", max_length=20)
    
    # Management practices
    tillage_type: Optional[str] = Field(None, max_length=50)
    fertilizer_applications: List[Dict] = Field(default_factory=list)
    pesticide_applications: List[Dict] = Field(default_factory=list)
    irrigation_used: bool = False
    cover_crop: Optional[str] = Field(None, max_length=100)
    
    # Performance metrics
    gross_revenue: Optional[float] = Field(None, ge=0)
    total_costs: Optional[float] = Field(None, ge=0)
    net_profit: Optional[float] = None
    
    # Additional data
    soil_test_results: Optional[Dict] = None
    notes: Optional[str] = Field(None, max_length=1000)
    
    @validator('harvest_date')
    def validate_harvest_after_planting(cls, v, values):
        if v and 'planting_date' in values and values['planting_date']:
            if v <= values['planting_date']:
                raise ValueError('Harvest date must be after planting date')
        return v


class RotationGoalRequest(BaseModel):
    """Request model for rotation goal setting."""
    goal_type: RotationGoalType
    priority: int = Field(..., ge=1, le=10)
    weight: float = Field(..., ge=0.0, le=1.0)
    target_value: Optional[float] = Field(None, ge=0)
    target_units: Optional[str] = Field(None, max_length=20)
    target_timeframe: int = Field(5, ge=1, le=20)
    description: str = Field("", max_length=500)
    constraints: List[str] = Field(default_factory=list)


class RotationConstraintRequest(BaseModel):
    """Request model for rotation constraints."""
    constraint_type: ConstraintType
    field_id: Optional[str] = None
    description: str = Field(..., min_length=1, max_length=500)
    is_hard_constraint: bool = True
    violation_penalty: float = Field(1.0, ge=0.0, le=10.0)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    applies_to_years: Optional[List[int]] = None
    can_be_relaxed: bool = False


class RotationPlanRequest(BaseModel):
    """Request model for rotation plan generation."""
    field_id: str
    plan_name: str = Field(..., min_length=1, max_length=100)
    planning_horizon: int = Field(5, ge=1, le=20)
    start_year: int = Field(..., ge=2020, le=2050)
    
    goals: List[RotationGoalRequest] = Field(default_factory=list)
    constraints: List[RotationConstraintRequest] = Field(default_factory=list)
    
    # Planning preferences
    preferred_crops: List[str] = Field(default_factory=list)
    excluded_crops: List[str] = Field(default_factory=list)
    risk_tolerance: float = Field(0.5, ge=0.0, le=1.0)
    
    # Economic parameters
    include_economic_analysis: bool = True
    discount_rate: float = Field(0.05, ge=0.0, le=0.2)
    
    @validator('goals')
    def validate_goal_weights(cls, v):
        if v:
            total_weight = sum(goal.weight for goal in v)
            if abs(total_weight - 1.0) > 0.01:
                raise ValueError('Goal weights must sum to 1.0')
        return v


class RotationPlanResponse(BaseModel):
    """Response model for rotation plans."""
    plan_id: str
    field_id: str
    plan_name: str
    created_date: datetime
    
    rotation_schedule: Dict[int, str]  # year -> crop_name
    rotation_details: Dict[int, Dict]  # year -> detailed plan
    
    overall_score: float
    benefit_scores: Dict[str, float]
    economic_projections: Dict[str, float]
    
    key_insights: List[str]
    recommendations: List[str]
    warnings: List[str]


class RotationPlanUpdateRequest(BaseModel):
    """Request model for updating rotation plans (partial updates supported)."""
    plan_name: Optional[str] = Field(None, min_length=1, max_length=100)
    planning_horizon: Optional[int] = Field(None, ge=1, le=20)
    
    # Rotation schedule updates
    rotation_years: Optional[Dict[int, str]] = None  # year -> crop_name
    rotation_details: Optional[Dict[int, Dict]] = None  # year -> details
    
    # Goals and constraints updates
    goals: Optional[List[RotationGoalRequest]] = None
    constraints: Optional[List[RotationConstraintRequest]] = None
    
    # Plan evaluation updates
    overall_score: Optional[float] = Field(None, ge=0.0, le=10.0) 
    benefit_scores: Optional[Dict[str, float]] = None
    risk_scores: Optional[Dict[str, float]] = None
    economic_projections: Optional[Dict] = None
    
    # Status updates
    is_active: Optional[bool] = None
    implementation_status: Optional[Dict[int, str]] = None
    actual_vs_planned: Optional[Dict[int, Dict]] = None
    
    @validator('goals')
    def validate_goal_weights(cls, v):
        if v:
            total_weight = sum(goal.weight for goal in v)
            if abs(total_weight - 1.0) > 0.01:
                raise ValueError('Goal weights must sum to 1.0')
        return v
    
    @validator('rotation_years')
    def validate_rotation_years(cls, v):
        if v:
            for year, crop in v.items():
                if year < 2020 or year > 2050:
                    raise ValueError(f'Year {year} must be between 2020 and 2050')
                if not crop or len(crop.strip()) == 0:
                    raise ValueError(f'Crop name for year {year} cannot be empty')
        return v


class RotationAnalysisResponse(BaseModel):
    """Response model for rotation analysis."""
    analysis_id: str
    plan_id: str
    analysis_date: datetime
    
    overall_score: float
    recommendation_confidence: float
    
    benefit_summary: Dict[str, float]
    economic_summary: Dict[str, float]
    sustainability_score: float
    
    key_insights: List[str]
    recommendations: List[str]
    risk_factors: List[str]
    
    alternative_scenarios: List[Dict]
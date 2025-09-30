"""
Application Method Optimization Models for Fertilizer Strategy Service

This module contains Pydantic models for comprehensive fertilizer application method optimization,
including method selection, efficiency optimization, and cost-benefit analysis.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional, Any, Union
from datetime import datetime, date
from enum import Enum
import uuid


class ApplicationMethod(str, Enum):
    """Fertilizer application methods with detailed characteristics."""
    BROADCAST = "broadcast"
    BROADCAST_INCORPORATED = "broadcast_incorporated"
    BANDED = "banded"
    SIDE_DRESS = "side_dress"
    FOLIAR = "foliar"
    FERTIGATION = "fertigation"
    INJECTION = "injection"
    STRIP_TILL = "strip_till"
    NO_TILL = "no_till"
    CONVENTIONAL_TILL = "conventional_till"


class FertilizerForm(str, Enum):
    """Fertilizer forms for application method optimization."""
    GRANULAR = "granular"
    LIQUID = "liquid"
    GASEOUS = "gaseous"
    SLURRY = "slurry"
    POWDER = "powder"


class EquipmentType(str, Enum):
    """Equipment types for application method optimization."""
    BROADCASTER = "broadcaster"
    PLANTER_MOUNTED = "planter_mounted"
    SIDE_DRESS_BAR = "side_dress_bar"
    SPRAYER = "sprayer"
    IRRIGATION_SYSTEM = "irrigation_system"
    INJECTION_SYSTEM = "injection_system"
    STRIP_TILL_TOOLBAR = "strip_till_toolbar"
    CONVENTIONAL_TILLAGE = "conventional_tillage"


class SoilCondition(str, Enum):
    """Soil conditions affecting application method selection."""
    DRY = "dry"
    MOIST = "moist"
    WET = "wet"
    FROZEN = "frozen"
    COMPACTED = "compacted"
    LOOSE = "loose"


class ApplicationEfficiency(BaseModel):
    """Application efficiency metrics for different methods."""
    nutrient_use_efficiency: float = Field(..., ge=0.0, le=1.0, description="Nutrient use efficiency (0-1)")
    application_uniformity: float = Field(..., ge=0.0, le=1.0, description="Application uniformity (0-1)")
    volatilization_loss: float = Field(..., ge=0.0, le=1.0, description="Volatilization loss (0-1)")
    leaching_loss: float = Field(..., ge=0.0, le=1.0, description="Leaching loss (0-1)")
    runoff_loss: float = Field(..., ge=0.0, le=1.0, description="Runoff loss (0-1)")
    denitrification_loss: float = Field(..., ge=0.0, le=1.0, description="Denitrification loss (0-1)")
    overall_efficiency: float = Field(..., ge=0.0, le=1.0, description="Overall efficiency score (0-1)")


class ApplicationCosts(BaseModel):
    """Cost breakdown for application methods."""
    fertilizer_cost_per_acre: float = Field(..., ge=0.0, description="Fertilizer cost per acre ($)")
    application_cost_per_acre: float = Field(..., ge=0.0, description="Application cost per acre ($)")
    equipment_cost_per_acre: float = Field(..., ge=0.0, description="Equipment cost per acre ($)")
    labor_cost_per_acre: float = Field(..., ge=0.0, description="Labor cost per acre ($)")
    fuel_cost_per_acre: float = Field(..., ge=0.0, description="Fuel cost per acre ($)")
    total_cost_per_acre: float = Field(..., ge=0.0, description="Total cost per acre ($)")


class ApplicationConstraints(BaseModel):
    """Constraints for application method selection."""
    available_equipment: List[EquipmentType] = Field(..., description="Available equipment types")
    labor_availability: float = Field(..., ge=0.0, le=1.0, description="Labor availability (0-1)")
    time_constraints: Dict[str, Any] = Field(default_factory=dict, description="Time constraints")
    budget_constraints: float = Field(..., ge=0.0, description="Budget constraints ($/acre)")
    soil_conditions: SoilCondition = Field(..., description="Current soil conditions")
    weather_forecast: Dict[str, Any] = Field(default_factory=dict, description="Weather forecast")
    field_accessibility: float = Field(..., ge=0.0, le=1.0, description="Field accessibility (0-1)")


class ApplicationMethodOptimizationRequest(BaseModel):
    """Request model for application method optimization."""
    
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique request identifier")
    
    # Field and crop information
    field_id: str = Field(..., description="Field identifier")
    crop_type: str = Field(..., description="Crop type (corn, soybean, wheat, etc.)")
    field_size_acres: float = Field(..., gt=0.0, description="Field size in acres")
    
    # Fertilizer requirements
    fertilizer_requirements: Dict[str, float] = Field(..., description="Fertilizer requirements by type (lbs/acre)")
    fertilizer_forms: List[FertilizerForm] = Field(..., description="Available fertilizer forms")
    
    # Field characteristics
    soil_type: str = Field(..., description="Soil type")
    soil_ph: float = Field(..., ge=4.0, le=9.0, description="Soil pH")
    organic_matter_percent: float = Field(..., ge=0.0, le=20.0, description="Organic matter percentage")
    cation_exchange_capacity: float = Field(..., ge=0.0, description="Cation exchange capacity (meq/100g)")
    drainage_class: str = Field(default="moderate", description="Drainage class")
    slope_percent: float = Field(default=0.0, ge=0.0, le=100.0, description="Field slope percentage")
    
    # Application constraints
    constraints: ApplicationConstraints = Field(..., description="Application constraints")
    
    # Optimization objectives
    optimize_for_yield: bool = Field(default=True, description="Optimize for yield maximization")
    optimize_for_cost: bool = Field(default=True, description="Optimize for cost minimization")
    optimize_for_efficiency: bool = Field(default=True, description="Optimize for efficiency maximization")
    optimize_for_environment: bool = Field(default=False, description="Optimize for environmental impact")
    
    # Additional preferences
    preferred_methods: List[ApplicationMethod] = Field(default_factory=list, description="Preferred application methods")
    avoid_methods: List[ApplicationMethod] = Field(default_factory=list, description="Methods to avoid")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Request creation timestamp")


class ApplicationMethodRecommendation(BaseModel):
    """Individual application method recommendation."""
    
    method: ApplicationMethod = Field(..., description="Recommended application method")
    fertilizer_form: FertilizerForm = Field(..., description="Recommended fertilizer form")
    equipment_type: EquipmentType = Field(..., description="Required equipment type")
    
    # Efficiency metrics
    efficiency: ApplicationEfficiency = Field(..., description="Application efficiency metrics")
    
    # Cost analysis
    costs: ApplicationCosts = Field(..., description="Cost breakdown")
    
    # Performance metrics
    expected_yield_impact: float = Field(..., description="Expected yield impact (bu/acre)")
    nutrient_availability: float = Field(..., ge=0.0, le=1.0, description="Nutrient availability (0-1)")
    application_timing: str = Field(..., description="Optimal application timing")
    
    # Environmental impact
    environmental_score: float = Field(..., ge=0.0, le=1.0, description="Environmental impact score (0-1)")
    runoff_risk: float = Field(..., ge=0.0, le=1.0, description="Runoff risk (0-1)")
    volatilization_risk: float = Field(..., ge=0.0, le=1.0, description="Volatilization risk (0-1)")
    
    # Constraints and feasibility
    feasibility_score: float = Field(..., ge=0.0, le=1.0, description="Feasibility score (0-1)")
    constraint_violations: List[str] = Field(default_factory=list, description="Constraint violations")
    
    # Overall scoring
    overall_score: float = Field(..., ge=0.0, le=1.0, description="Overall recommendation score (0-1)")
    ranking: int = Field(..., ge=1, description="Ranking among all methods")


class ApplicationMethodOptimizationResult(BaseModel):
    """Result model for application method optimization."""
    
    request_id: str = Field(..., description="Request identifier")
    optimization_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Optimization identifier")
    
    # Recommendations
    recommendations: List[ApplicationMethodRecommendation] = Field(..., description="Method recommendations")
    best_method: ApplicationMethodRecommendation = Field(..., description="Best overall method")
    
    # Optimization summary
    optimization_objectives: Dict[str, bool] = Field(..., description="Optimization objectives used")
    total_methods_evaluated: int = Field(..., description="Total methods evaluated")
    feasible_methods: int = Field(..., description="Number of feasible methods")
    
    # Performance metrics
    best_yield_impact: float = Field(..., description="Best yield impact (bu/acre)")
    lowest_cost_per_acre: float = Field(..., description="Lowest cost per acre ($)")
    highest_efficiency: float = Field(..., description="Highest efficiency score")
    best_environmental_score: float = Field(..., description="Best environmental score")
    
    # Analysis details
    method_comparison: Dict[str, Dict[str, Any]] = Field(..., description="Detailed method comparison")
    sensitivity_analysis: Dict[str, Any] = Field(default_factory=dict, description="Sensitivity analysis results")
    
    # Recommendations summary
    key_insights: List[str] = Field(..., description="Key insights from optimization")
    implementation_notes: List[str] = Field(..., description="Implementation notes and considerations")
    
    # Metadata
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Result creation timestamp")


class ApplicationMethodComparisonRequest(BaseModel):
    """Request model for comparing specific application methods."""
    
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique request identifier")
    
    # Methods to compare
    methods_to_compare: List[ApplicationMethod] = Field(..., description="Methods to compare")
    
    # Field and crop information (same as optimization request)
    field_id: str = Field(..., description="Field identifier")
    crop_type: str = Field(..., description="Crop type")
    field_size_acres: float = Field(..., gt=0.0, description="Field size in acres")
    fertilizer_requirements: Dict[str, float] = Field(..., description="Fertilizer requirements")
    soil_type: str = Field(..., description="Soil type")
    soil_ph: float = Field(..., ge=4.0, le=9.0, description="Soil pH")
    
    # Constraints
    constraints: ApplicationConstraints = Field(..., description="Application constraints")
    
    # Comparison criteria
    compare_yield_impact: bool = Field(default=True, description="Compare yield impact")
    compare_costs: bool = Field(default=True, description="Compare costs")
    compare_efficiency: bool = Field(default=True, description="Compare efficiency")
    compare_environmental_impact: bool = Field(default=True, description="Compare environmental impact")


class ApplicationMethodComparisonResult(BaseModel):
    """Result model for application method comparison."""
    
    request_id: str = Field(..., description="Request identifier")
    comparison_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Comparison identifier")
    
    # Comparison results
    method_comparisons: List[ApplicationMethodRecommendation] = Field(..., description="Method comparisons")
    
    # Comparative analysis
    yield_comparison: Dict[str, float] = Field(..., description="Yield impact comparison")
    cost_comparison: Dict[str, float] = Field(..., description="Cost comparison")
    efficiency_comparison: Dict[str, float] = Field(..., description="Efficiency comparison")
    environmental_comparison: Dict[str, float] = Field(..., description="Environmental comparison")
    
    # Ranking
    method_rankings: Dict[str, int] = Field(..., description="Method rankings")
    best_method_overall: ApplicationMethod = Field(..., description="Best method overall")
    
    # Analysis summary
    key_differences: List[str] = Field(..., description="Key differences between methods")
    trade_off_analysis: Dict[str, Any] = Field(..., description="Trade-off analysis")
    
    # Metadata
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Result creation timestamp")


class ApplicationMethodEfficiencyAnalysis(BaseModel):
    """Detailed efficiency analysis for application methods."""
    
    method: ApplicationMethod = Field(..., description="Application method")
    
    # Nutrient efficiency
    nitrogen_efficiency: float = Field(..., ge=0.0, le=1.0, description="Nitrogen use efficiency")
    phosphorus_efficiency: float = Field(..., ge=0.0, le=1.0, description="Phosphorus use efficiency")
    potassium_efficiency: float = Field(..., ge=0.0, le=1.0, description="Potassium use efficiency")
    
    # Loss mechanisms
    volatilization_loss_percent: float = Field(..., ge=0.0, le=100.0, description="Volatilization loss percentage")
    leaching_loss_percent: float = Field(..., ge=0.0, le=100.0, description="Leaching loss percentage")
    runoff_loss_percent: float = Field(..., ge=0.0, le=100.0, description="Runoff loss percentage")
    denitrification_loss_percent: float = Field(..., ge=0.0, le=100.0, description="Denitrification loss percentage")
    
    # Application quality
    uniformity_coefficient: float = Field(..., ge=0.0, le=1.0, description="Application uniformity coefficient")
    placement_accuracy: float = Field(..., ge=0.0, le=1.0, description="Placement accuracy")
    timing_flexibility: float = Field(..., ge=0.0, le=1.0, description="Timing flexibility")
    
    # Environmental factors
    soil_disturbance: float = Field(..., ge=0.0, le=1.0, description="Soil disturbance level")
    erosion_risk: float = Field(..., ge=0.0, le=1.0, description="Erosion risk")
    compaction_risk: float = Field(..., ge=0.0, le=1.0, description="Compaction risk")


class ApplicationMethodCostAnalysis(BaseModel):
    """Detailed cost analysis for application methods."""
    
    method: ApplicationMethod = Field(..., description="Application method")
    
    # Direct costs
    fertilizer_cost_per_acre: float = Field(..., ge=0.0, description="Fertilizer cost per acre")
    application_cost_per_acre: float = Field(..., ge=0.0, description="Application cost per acre")
    equipment_cost_per_acre: float = Field(..., ge=0.0, description="Equipment cost per acre")
    labor_cost_per_acre: float = Field(..., ge=0.0, description="Labor cost per acre")
    fuel_cost_per_acre: float = Field(..., ge=0.0, description="Fuel cost per acre")
    
    # Indirect costs
    equipment_depreciation_per_acre: float = Field(..., ge=0.0, description="Equipment depreciation per acre")
    maintenance_cost_per_acre: float = Field(..., ge=0.0, description="Maintenance cost per acre")
    insurance_cost_per_acre: float = Field(..., ge=0.0, description="Insurance cost per acre")
    
    # Total costs
    total_direct_cost_per_acre: float = Field(..., ge=0.0, description="Total direct cost per acre")
    total_indirect_cost_per_acre: float = Field(..., ge=0.0, description="Total indirect cost per acre")
    total_cost_per_acre: float = Field(..., ge=0.0, description="Total cost per acre")
    
    # Cost efficiency
    cost_per_unit_nutrient: float = Field(..., ge=0.0, description="Cost per unit nutrient applied")
    cost_per_bushel_yield: float = Field(..., ge=0.0, description="Cost per bushel yield")
    return_on_investment: float = Field(..., description="Return on investment")


class ApplicationMethodSummary(BaseModel):
    """Summary of application method optimization results."""
    
    optimization_id: str = Field(..., description="Optimization identifier")
    field_id: str = Field(..., description="Field identifier")
    crop_type: str = Field(..., description="Crop type")
    
    # Best method summary
    best_method: ApplicationMethod = Field(..., description="Best application method")
    best_method_score: float = Field(..., ge=0.0, le=1.0, description="Best method score")
    
    # Performance summary
    expected_yield_impact: float = Field(..., description="Expected yield impact")
    total_cost_per_acre: float = Field(..., ge=0.0, description="Total cost per acre")
    efficiency_score: float = Field(..., ge=0.0, le=1.0, description="Efficiency score")
    environmental_score: float = Field(..., ge=0.0, le=1.0, description="Environmental score")
    
    # Recommendations
    primary_recommendation: str = Field(..., description="Primary recommendation")
    alternative_methods: List[ApplicationMethod] = Field(..., description="Alternative methods")
    implementation_priority: str = Field(..., description="Implementation priority")
    
    # Key insights
    key_benefits: List[str] = Field(..., description="Key benefits")
    key_risks: List[str] = Field(..., description="Key risks")
    optimization_notes: List[str] = Field(..., description="Optimization notes")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Summary creation timestamp")
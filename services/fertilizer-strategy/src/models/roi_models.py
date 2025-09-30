"""
ROI Optimization Models for Fertilizer Strategy Optimization Service.

This module contains Pydantic models for fertilizer ROI optimization,
including request/response schemas and data validation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date
from enum import Enum
from decimal import Decimal


class OptimizationMethod(str, Enum):
    """Optimization methods available for ROI calculation."""
    LINEAR_PROGRAMMING = "linear_programming"
    QUADRATIC_PROGRAMMING = "quadratic_programming"
    GENETIC_ALGORITHM = "genetic_algorithm"
    GRADIENT_DESCENT = "gradient_descent"


class RiskTolerance(str, Enum):
    """Risk tolerance levels for optimization."""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class NutrientType(str, Enum):
    """Types of nutrients for optimization."""
    NITROGEN = "N"
    PHOSPHORUS = "P"
    POTASSIUM = "K"
    MICRONUTRIENTS = "micronutrients"


class FertilizerProduct(BaseModel):
    """Fertilizer product information for optimization."""
    product_id: str = Field(..., description="Unique product identifier")
    product_name: str = Field(..., description="Product name")
    nutrient_content: Dict[str, float] = Field(..., description="Nutrient content percentages")
    price_per_unit: float = Field(..., ge=0, description="Price per unit")
    unit: str = Field(..., description="Unit of measurement (ton, lb, etc.)")
    application_method: str = Field(..., description="Application method")
    availability: bool = Field(default=True, description="Product availability")


class FieldData(BaseModel):
    """Field-specific data for optimization."""
    field_id: str = Field(..., description="Unique field identifier")
    acres: float = Field(..., gt=0, description="Field size in acres")
    soil_tests: Dict[str, float] = Field(..., description="Soil test results")
    crop_plan: Dict[str, Any] = Field(..., description="Crop planting plan")
    historical_yield: Optional[float] = Field(None, description="Historical yield data")
    target_yield: float = Field(..., gt=0, description="Target yield per acre")
    crop_price: float = Field(..., gt=0, description="Expected crop price per unit")


class BudgetConstraint(BaseModel):
    """Detailed budget constraint configuration."""
    total_budget_limit: Optional[float] = Field(None, description="Total budget limit across all fields")
    per_field_budget_limit: Optional[float] = Field(None, description="Maximum budget per field")
    per_acre_budget_limit: Optional[float] = Field(None, description="Maximum budget per acre")
    nutrient_budget_allocation: Dict[str, float] = Field(default_factory=dict, description="Budget allocation by nutrient type")
    product_budget_allocation: Dict[str, float] = Field(default_factory=dict, description="Budget allocation by product")
    seasonal_budget_allocation: Dict[str, float] = Field(default_factory=dict, description="Budget allocation by season")
    priority_field_budget_multiplier: Dict[str, float] = Field(default_factory=dict, description="Budget multiplier for priority fields")
    budget_flexibility_percentage: float = Field(default=10.0, ge=0, le=50, description="Budget flexibility percentage for constraint relaxation")
    allow_budget_reallocation: bool = Field(default=True, description="Allow budget reallocation between fields")
    budget_utilization_target: float = Field(default=95.0, ge=80, le=100, description="Target budget utilization percentage")


class TimingConstraint(BaseModel):
    """Timing constraints for fertilizer application."""
    application_windows: List[Dict[str, Any]] = Field(default_factory=list, description="Available application windows")
    equipment_availability: Dict[str, List[str]] = Field(default_factory=dict, description="Equipment availability by date")
    labor_availability: Dict[str, int] = Field(default_factory=dict, description="Labor availability by date")
    weather_dependent_timing: bool = Field(default=True, description="Consider weather for timing")
    minimum_application_interval_days: int = Field(default=7, ge=1, description="Minimum days between applications")


class OptimizationConstraints(BaseModel):
    """Comprehensive constraints for optimization."""
    # Nutrient rate constraints
    max_nitrogen_rate: Optional[float] = Field(None, description="Maximum nitrogen rate per acre")
    max_phosphorus_rate: Optional[float] = Field(None, description="Maximum phosphorus rate per acre")
    max_potassium_rate: Optional[float] = Field(None, description="Maximum potassium rate per acre")
    max_micronutrient_rate: Optional[float] = Field(None, description="Maximum micronutrient rate per acre")
    
    # Budget constraints (enhanced)
    budget_constraint: Optional[BudgetConstraint] = Field(None, description="Detailed budget constraint configuration")
    budget_limit: Optional[float] = Field(None, description="Total budget limit (legacy field)")
    max_per_acre_cost: Optional[float] = Field(None, description="Maximum cost per acre")
    
    # Timing constraints
    timing_constraints: Optional[TimingConstraint] = Field(None, description="Timing constraints for application")
    
    # Environmental constraints
    environmental_limits: Dict[str, Any] = Field(default_factory=dict, description="Environmental constraints")
    max_environmental_impact_score: Optional[float] = Field(None, description="Maximum environmental impact score")
    
    # Equipment constraints
    equipment_limitations: List[str] = Field(default_factory=list, description="Available equipment")
    equipment_capacity_constraints: Dict[str, float] = Field(default_factory=dict, description="Equipment capacity constraints")
    
    # Labor constraints
    labor_availability: Optional[int] = Field(None, description="Available labor hours")
    max_labor_cost_per_hour: Optional[float] = Field(None, description="Maximum labor cost per hour")
    
    # Risk constraints
    max_risk_score: Optional[float] = Field(None, description="Maximum acceptable risk score")
    risk_tolerance_level: Optional[str] = Field(None, description="Risk tolerance level")
    
    # Multi-objective constraints
    min_roi_threshold: Optional[float] = Field(None, description="Minimum ROI threshold")
    min_yield_target: Optional[float] = Field(None, description="Minimum yield target")
    max_cost_per_unit_yield: Optional[float] = Field(None, description="Maximum cost per unit yield")


class OptimizationGoals(BaseModel):
    """Optimization goals and priorities."""
    primary_goal: str = Field(default="profit_maximization", description="Primary optimization goal")
    yield_priority: float = Field(default=0.8, ge=0, le=1, description="Yield priority weight")
    cost_priority: float = Field(default=0.7, ge=0, le=1, description="Cost priority weight")
    environmental_priority: float = Field(default=0.6, ge=0, le=1, description="Environmental priority weight")
    risk_tolerance: RiskTolerance = Field(default=RiskTolerance.MODERATE, description="Risk tolerance level")


class ROIOptimizationRequest(BaseModel):
    """Request model for ROI optimization."""
    farm_context: Dict[str, Any] = Field(..., description="Farm context data")
    fields: List[FieldData] = Field(..., min_length=1, description="Field data for optimization")
    fertilizer_products: List[FertilizerProduct] = Field(..., min_length=1, description="Available fertilizer products")
    constraints: OptimizationConstraints = Field(..., description="Optimization constraints")
    goals: OptimizationGoals = Field(..., description="Optimization goals")
    optimization_method: OptimizationMethod = Field(default=OptimizationMethod.LINEAR_PROGRAMMING, description="Optimization method")
    include_sensitivity_analysis: bool = Field(default=True, description="Include sensitivity analysis")
    include_risk_assessment: bool = Field(default=True, description="Include risk assessment")

    @field_validator('fields')
    @classmethod
    def validate_fields(cls, v):
        """Validate field data."""
        if not v:
            raise ValueError("At least one field is required")
        return v

    @field_validator('fertilizer_products')
    @classmethod
    def validate_fertilizer_products(cls, v):
        """Validate fertilizer products."""
        if not v:
            raise ValueError("At least one fertilizer product is required")
        return v


class NutrientRecommendation(BaseModel):
    """Nutrient recommendation for a specific field."""
    field_id: str = Field(..., description="Field identifier")
    nutrient_type: NutrientType = Field(..., description="Type of nutrient")
    recommended_rate: float = Field(..., ge=0, description="Recommended application rate")
    unit: str = Field(..., description="Unit of measurement")
    product_recommendations: List[Dict[str, Any]] = Field(..., description="Product recommendations")
    expected_yield_response: float = Field(..., description="Expected yield response")
    cost_per_acre: float = Field(..., ge=0, description="Cost per acre")


class OptimizationResult(BaseModel):
    """Result of ROI optimization."""
    optimization_id: str = Field(..., description="Unique optimization identifier")
    total_expected_revenue: float = Field(..., description="Total expected revenue")
    total_fertilizer_cost: float = Field(..., description="Total fertilizer cost")
    net_profit: float = Field(..., description="Net profit")
    roi_percentage: float = Field(..., description="Return on investment percentage")
    break_even_yield: float = Field(..., description="Break-even yield per acre")
    marginal_return_rate: float = Field(..., description="Marginal return rate")
    risk_adjusted_return: float = Field(..., description="Risk-adjusted return")
    nutrient_recommendations: List[NutrientRecommendation] = Field(..., description="Nutrient recommendations")
    optimization_metadata: Dict[str, Any] = Field(default_factory=dict, description="Optimization metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")


class SensitivityAnalysis(BaseModel):
    """Sensitivity analysis results."""
    parameter: str = Field(..., description="Parameter analyzed")
    base_value: float = Field(..., description="Base parameter value")
    sensitivity_range: List[float] = Field(..., description="Sensitivity range")
    roi_impact: List[float] = Field(..., description="ROI impact for each value")
    critical_threshold: Optional[float] = Field(None, description="Critical threshold value")
    risk_level: str = Field(..., description="Risk level assessment")


class RiskAssessment(BaseModel):
    """Risk assessment results."""
    overall_risk_score: float = Field(..., ge=0, le=1, description="Overall risk score")
    risk_factors: List[Dict[str, Any]] = Field(..., description="Identified risk factors")
    mitigation_strategies: List[str] = Field(..., description="Recommended mitigation strategies")
    confidence_level: float = Field(..., ge=0, le=1, description="Confidence level in optimization")
    scenario_analysis: Dict[str, Any] = Field(default_factory=dict, description="Scenario analysis results")


class ROIOptimizationResponse(BaseModel):
    """Response model for ROI optimization."""
    optimization_result: OptimizationResult = Field(..., description="Optimization result")
    sensitivity_analysis: Optional[List[SensitivityAnalysis]] = Field(None, description="Sensitivity analysis")
    risk_assessment: Optional[RiskAssessment] = Field(None, description="Risk assessment")
    alternative_scenarios: List[Dict[str, Any]] = Field(default_factory=list, description="Alternative scenarios")
    recommendations: List[str] = Field(default_factory=list, description="General recommendations")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


class MarginalReturnAnalysis(BaseModel):
    """Marginal return analysis for fertilizer applications."""
    nutrient_type: NutrientType = Field(..., description="Nutrient type")
    application_rate: float = Field(..., description="Application rate")
    marginal_yield_response: float = Field(..., description="Marginal yield response")
    marginal_cost: float = Field(..., description="Marginal cost")
    marginal_return: float = Field(..., description="Marginal return")
    optimal_rate: float = Field(..., description="Optimal application rate")
    diminishing_returns_threshold: float = Field(..., description="Diminishing returns threshold")


class YieldResponseCurve(BaseModel):
    """Yield response curve data."""
    nutrient_type: NutrientType = Field(..., description="Nutrient type")
    rates: List[float] = Field(..., description="Application rates")
    yields: List[float] = Field(..., description="Corresponding yields")
    curve_type: str = Field(..., description="Type of response curve")
    r_squared: float = Field(..., description="Model fit quality")
    optimal_rate: float = Field(..., description="Optimal application rate")


class BreakEvenAnalysis(BaseModel):
    """Break-even analysis results."""
    break_even_yield: float = Field(..., description="Break-even yield per acre")
    break_even_price: float = Field(..., description="Break-even crop price")
    break_even_cost: float = Field(..., description="Break-even fertilizer cost")
    safety_margin: float = Field(..., description="Safety margin percentage")
    probability_of_profitability: float = Field(..., description="Probability of profitability")
    risk_factors: List[str] = Field(..., description="Risk factors affecting break-even")


class BudgetAllocationResult(BaseModel):
    """Budget allocation optimization result."""
    field_id: str = Field(..., description="Field identifier")
    allocated_budget: float = Field(..., description="Allocated budget for this field")
    budget_utilization_percentage: float = Field(..., description="Budget utilization percentage")
    nutrient_allocation: Dict[str, float] = Field(..., description="Budget allocation by nutrient")
    product_allocation: Dict[str, float] = Field(..., description="Budget allocation by product")
    expected_roi: float = Field(..., description="Expected ROI for this allocation")
    priority_score: float = Field(..., description="Field priority score")
    constraint_violations: List[str] = Field(default_factory=list, description="Constraint violations")


class ParetoFrontierPoint(BaseModel):
    """Pareto frontier analysis point."""
    scenario_id: str = Field(..., description="Scenario identifier")
    total_cost: float = Field(..., description="Total cost")
    total_revenue: float = Field(..., description="Total revenue")
    roi_percentage: float = Field(..., description="ROI percentage")
    environmental_score: float = Field(..., description="Environmental impact score")
    risk_score: float = Field(..., description="Risk score")
    yield_target_achievement: float = Field(..., description="Yield target achievement percentage")
    budget_utilization: float = Field(..., description="Budget utilization percentage")
    trade_off_description: str = Field(..., description="Description of trade-offs")


class ConstraintRelaxationAnalysis(BaseModel):
    """Constraint relaxation analysis results."""
    constraint_type: str = Field(..., description="Type of constraint relaxed")
    original_value: float = Field(..., description="Original constraint value")
    relaxed_value: float = Field(..., description="Relaxed constraint value")
    relaxation_impact: Dict[str, float] = Field(..., description="Impact of relaxation on objectives")
    cost_of_relaxation: float = Field(..., description="Cost of relaxing this constraint")
    benefit_of_relaxation: float = Field(..., description="Benefit of relaxing this constraint")
    recommendation: str = Field(..., description="Recommendation for constraint relaxation")


class MultiObjectiveOptimizationResult(BaseModel):
    """Multi-objective optimization result."""
    optimization_id: str = Field(..., description="Unique optimization identifier")
    pareto_frontier: List[ParetoFrontierPoint] = Field(..., description="Pareto frontier points")
    recommended_scenario: ParetoFrontierPoint = Field(..., description="Recommended scenario")
    budget_allocations: List[BudgetAllocationResult] = Field(..., description="Budget allocation results")
    constraint_relaxation_analysis: List[ConstraintRelaxationAnalysis] = Field(default_factory=list, description="Constraint relaxation analysis")
    trade_off_analysis: Dict[str, Any] = Field(default_factory=dict, description="Trade-off analysis between objectives")
    optimization_metadata: Dict[str, Any] = Field(default_factory=dict, description="Optimization metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")


class OptimizationSummary(BaseModel):
    """Summary of optimization results."""
    total_fields_optimized: int = Field(..., description="Number of fields optimized")
    total_acres: float = Field(..., description="Total acres optimized")
    average_roi: float = Field(..., description="Average ROI across fields")
    total_investment: float = Field(..., description="Total fertilizer investment")
    expected_return: float = Field(..., description="Expected return")
    risk_level: str = Field(..., description="Overall risk level")
    optimization_method_used: str = Field(..., description="Optimization method used")
    processing_time_ms: float = Field(..., description="Total processing time")
    budget_utilization_percentage: Optional[float] = Field(None, description="Budget utilization percentage")
    constraint_violations_count: int = Field(default=0, description="Number of constraint violations")
    pareto_frontier_size: Optional[int] = Field(None, description="Number of Pareto frontier points")
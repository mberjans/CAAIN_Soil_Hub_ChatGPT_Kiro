"""
Enhanced models for comprehensive break-even analysis.

This module provides advanced data models for break-even analysis including:
- Stochastic modeling results
- Scenario analysis data
- Sensitivity analysis results
- Risk assessment models
- Monte Carlo simulation results
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
from uuid import UUID


class ScenarioType(str, Enum):
    """Types of break-even scenarios."""
    OPTIMISTIC = "optimistic"
    REALISTIC = "realistic"
    PESSIMISTIC = "pessimistic"
    STRESS_TEST = "stress_test"


class RiskLevel(str, Enum):
    """Risk levels for break-even analysis."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DistributionType(str, Enum):
    """Types of probability distributions."""
    NORMAL = "normal"
    LOGNORMAL = "lognormal"
    TRIANGULAR = "triangular"
    UNIFORM = "uniform"


class CostStructure(BaseModel):
    """Detailed cost structure for break-even analysis."""
    fixed_costs: float = Field(..., description="Fixed costs per operation")
    variable_costs: float = Field(..., description="Variable costs per acre")
    fertilizer_costs: float = Field(..., description="Total fertilizer costs")
    application_costs: float = Field(..., description="Application costs (labor, equipment)")
    opportunity_costs: float = Field(..., description="Opportunity costs")
    total_costs: float = Field(..., description="Total costs")
    
    @validator('total_costs')
    def validate_total_costs(cls, v, values):
        """Validate that total costs match sum of components."""
        if 'fixed_costs' in values and 'variable_costs' in values and 'fertilizer_costs' in values and 'application_costs' in values and 'opportunity_costs' in values:
            expected_total = (values['fixed_costs'] + values['variable_costs'] + 
                            values['fertilizer_costs'] + values['application_costs'] + 
                            values['opportunity_costs'])
            if abs(v - expected_total) > 0.01:
                raise ValueError(f"Total costs {v} does not match sum of components {expected_total}")
        return v


class YieldResponseCurve(BaseModel):
    """Yield response curve parameters."""
    base_yield: float = Field(..., description="Base yield without fertilizer")
    max_yield: float = Field(..., description="Maximum achievable yield")
    response_rate: float = Field(..., description="Response rate parameter")
    plateau_yield: float = Field(..., description="Yield at plateau")
    diminishing_returns_factor: float = Field(..., description="Diminishing returns factor")
    
    @validator('max_yield')
    def validate_max_yield(cls, v, values):
        """Validate that max yield is greater than base yield."""
        if 'base_yield' in values and v <= values['base_yield']:
            raise ValueError("Max yield must be greater than base yield")
        return v


class PriceDistribution(BaseModel):
    """Price distribution parameters for stochastic modeling."""
    mean_price: float = Field(..., description="Mean price")
    std_deviation: float = Field(..., description="Standard deviation")
    min_price: float = Field(..., description="Minimum price")
    max_price: float = Field(..., description="Maximum price")
    distribution_type: DistributionType = Field(..., description="Type of distribution")
    
    @validator('std_deviation')
    def validate_std_deviation(cls, v):
        """Validate that standard deviation is positive."""
        if v <= 0:
            raise ValueError("Standard deviation must be positive")
        return v
    
    @validator('max_price')
    def validate_max_price(cls, v, values):
        """Validate that max price is greater than min price."""
        if 'min_price' in values and v <= values['min_price']:
            raise ValueError("Max price must be greater than min price")
        return v


class BreakEvenScenario(BaseModel):
    """Individual break-even scenario."""
    scenario_id: str = Field(..., description="Unique scenario identifier")
    scenario_type: ScenarioType = Field(..., description="Type of scenario")
    crop_price: float = Field(..., description="Crop price for scenario")
    fertilizer_price: float = Field(..., description="Fertilizer price for scenario")
    expected_yield: float = Field(..., description="Expected yield for scenario")
    break_even_yield: float = Field(..., description="Break-even yield per acre")
    break_even_price: float = Field(..., description="Break-even price per unit")
    break_even_cost: float = Field(..., description="Break-even cost per acre")
    probability: float = Field(..., ge=0.0, le=1.0, description="Probability of scenario")
    risk_level: RiskLevel = Field(..., description="Risk level for scenario")
    safety_margin: float = Field(..., description="Safety margin percentage")
    
    @validator('break_even_yield')
    def validate_break_even_yield(cls, v):
        """Validate that break-even yield is positive."""
        if v < 0:
            raise ValueError("Break-even yield must be positive")
        return v


class SensitivityAnalysis(BaseModel):
    """Sensitivity analysis results."""
    variable_name: str = Field(..., description="Name of the variable analyzed")
    base_value: float = Field(..., description="Base value of the variable")
    sensitivity_range: Tuple[float, float] = Field(..., description="Range of sensitivity analysis")
    break_even_impact: Dict[str, Dict[str, float]] = Field(..., description="Impact on break-even metrics")
    elasticity: float = Field(..., description="Elasticity coefficient")
    
    @validator('elasticity')
    def validate_elasticity(cls, v):
        """Validate elasticity is a reasonable value."""
        if abs(v) > 10:
            raise ValueError("Elasticity value seems unrealistic")
        return v


class MonteCarloResult(BaseModel):
    """Monte Carlo simulation results."""
    simulation_id: str = Field(..., description="Unique simulation identifier")
    iterations: int = Field(..., ge=1000, description="Number of Monte Carlo iterations")
    break_even_probabilities: Dict[str, float] = Field(..., description="Break-even probabilities")
    confidence_intervals: Dict[str, Tuple[float, float]] = Field(..., description="Confidence intervals")
    risk_metrics: Dict[str, float] = Field(..., description="Risk metrics")
    probability_distributions: Dict[str, List[float]] = Field(..., description="Probability distributions")
    
    @validator('iterations')
    def validate_iterations(cls, v):
        """Validate that iterations is reasonable."""
        if v < 1000:
            raise ValueError("Minimum 1000 iterations required for reliable results")
        return v


class RiskAssessment(BaseModel):
    """Risk assessment results."""
    overall_risk_level: RiskLevel = Field(..., description="Overall risk level")
    risk_score: int = Field(..., ge=0, le=10, description="Risk score (0-10)")
    risk_factors: List[str] = Field(..., description="Identified risk factors")
    risk_mitigation_recommendations: List[str] = Field(..., description="Risk mitigation recommendations")
    
    @validator('risk_score')
    def validate_risk_score(cls, v):
        """Validate risk score is in valid range."""
        if not 0 <= v <= 10:
            raise ValueError("Risk score must be between 0 and 10")
        return v


class BreakEvenAnalysisRequest(BaseModel):
    """Request model for comprehensive break-even analysis."""
    fields: List[Dict[str, Any]] = Field(..., description="Field data for analysis")
    products: List[Dict[str, Any]] = Field(..., description="Fertilizer products")
    optimization_method: str = Field(default="linear_programming", description="Optimization method")
    budget_constraints: Optional[Dict[str, Any]] = Field(None, description="Budget constraints")
    farm_context: Optional[Dict[str, Any]] = Field(None, description="Farm context data")
    include_stochastic: bool = Field(default=True, description="Include Monte Carlo simulation")
    include_scenarios: bool = Field(default=True, description="Include scenario analysis")
    include_sensitivity: bool = Field(default=True, description="Include sensitivity analysis")
    monte_carlo_iterations: int = Field(default=10000, ge=1000, le=100000, description="Monte Carlo iterations")
    
    @validator('monte_carlo_iterations')
    def validate_iterations(cls, v):
        """Validate Monte Carlo iterations."""
        if v < 1000:
            raise ValueError("Minimum 1000 iterations required")
        if v > 100000:
            raise ValueError("Maximum 100000 iterations allowed for performance")
        return v


class ComprehensiveBreakEvenAnalysis(BaseModel):
    """Comprehensive break-even analysis results."""
    analysis_id: str = Field(..., description="Unique analysis identifier")
    timestamp: datetime = Field(..., description="Analysis timestamp")
    basic_analysis: Dict[str, Any] = Field(..., description="Basic break-even analysis")
    cost_structure: CostStructure = Field(..., description="Detailed cost structure")
    field_summary: Dict[str, Any] = Field(..., description="Field summary")
    product_summary: Dict[str, Any] = Field(..., description="Product summary")
    stochastic_analysis: Optional[MonteCarloResult] = Field(None, description="Monte Carlo results")
    scenario_analysis: Optional[List[BreakEvenScenario]] = Field(None, description="Scenario analysis")
    sensitivity_analysis: Optional[List[SensitivityAnalysis]] = Field(None, description="Sensitivity analysis")
    risk_assessment: RiskAssessment = Field(..., description="Risk assessment")
    recommendations: List[str] = Field(..., description="Actionable recommendations")
    
    @validator('recommendations')
    def validate_recommendations(cls, v):
        """Validate that recommendations are provided."""
        if not v:
            raise ValueError("At least one recommendation must be provided")
        return v


class BreakEvenSummary(BaseModel):
    """Summary of break-even analysis for quick reference."""
    analysis_id: str = Field(..., description="Analysis identifier")
    break_even_yield_per_acre: float = Field(..., description="Break-even yield per acre")
    break_even_price_per_unit: float = Field(..., description="Break-even price per unit")
    safety_margin_percentage: float = Field(..., description="Safety margin percentage")
    probability_of_profitability: float = Field(..., ge=0.0, le=1.0, description="Probability of profitability")
    overall_risk_level: RiskLevel = Field(..., description="Overall risk level")
    key_recommendations: List[str] = Field(..., description="Key recommendations")
    
    @validator('probability_of_profitability')
    def validate_probability(cls, v):
        """Validate probability is in valid range."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Probability must be between 0 and 1")
        return v


class BreakEvenComparison(BaseModel):
    """Comparison of multiple break-even analyses."""
    comparison_id: str = Field(..., description="Unique comparison identifier")
    analyses: List[BreakEvenSummary] = Field(..., description="Analyses being compared")
    comparison_metrics: Dict[str, Any] = Field(..., description="Comparison metrics")
    best_scenario: str = Field(..., description="Best scenario identifier")
    worst_scenario: str = Field(..., description="Worst scenario identifier")
    
    @validator('analyses')
    def validate_analyses(cls, v):
        """Validate that at least two analyses are provided."""
        if len(v) < 2:
            raise ValueError("At least two analyses required for comparison")
        return v


class BreakEvenAlert(BaseModel):
    """Alert for break-even analysis results."""
    alert_id: str = Field(..., description="Unique alert identifier")
    alert_type: str = Field(..., description="Type of alert")
    severity: str = Field(..., description="Alert severity")
    message: str = Field(..., description="Alert message")
    analysis_id: str = Field(..., description="Related analysis identifier")
    timestamp: datetime = Field(..., description="Alert timestamp")
    actionable: bool = Field(default=True, description="Whether alert requires action")
    
    @validator('severity')
    def validate_severity(cls, v):
        """Validate severity level."""
        valid_severities = ['low', 'medium', 'high', 'critical']
        if v.lower() not in valid_severities:
            raise ValueError(f"Severity must be one of: {valid_severities}")
        return v.lower()
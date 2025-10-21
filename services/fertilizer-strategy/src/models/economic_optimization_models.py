"""
Pydantic models for economic optimization and scenario modeling.

These models structure the input and output for economic optimization services,
including scenario modeling, multi-objective optimization, risk assessment,
sensitivity analysis, and Monte Carlo simulation.
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any, Tuple, Union
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator

# Economic Optimization Request Models
class EconomicOptimizationRequest(BaseModel):
    """Request model for economic optimization analysis."""
    
    analysis_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique analysis identifier")
    farm_context: Dict[str, Any] = Field(..., description="Farm context data")
    crop_context: Dict[str, Any] = Field(..., description="Crop context data")
    fertilizer_requirements: List[Dict[str, Any]] = Field(..., description="Fertilizer requirements")
    # Format: [{"product": "urea", "type": "nitrogen", "rate_lbs_per_acre": 150.0, "application_method": "broadcast"}]
    
    field_size_acres: float = Field(..., gt=0, description="Field size in acres")
    expected_yield_bu_per_acre: float = Field(..., gt=0, description="Expected yield in bushels per acre")
    crop_price_per_bu: float = Field(..., gt=0, description="Expected crop price per bushel")
    
    primary_objective: str = Field(default="profit_maximization", description="Primary optimization objective")
    secondary_objectives: Optional[List[str]] = Field(None, description="Secondary optimization objectives")
    objective_weights: Optional[Dict[str, float]] = Field(None, description="Weights for optimization objectives")
    
    budget_limit: Optional[float] = Field(None, description="Budget limit for optimization")
    risk_tolerance: Optional[str] = Field("moderate", description="Risk tolerance level")
    environmental_constraints: Optional[Dict[str, Any]] = Field(None, description="Environmental constraints")
    
    custom_scenarios: Optional[List[Dict[str, Any]]] = Field(None, description="Custom scenario definitions")
    analysis_horizon_days: int = Field(default=365, ge=30, le=1095, description="Analysis horizon in days")
    
    # Scenario analysis parameters
    include_scenario_analysis: bool = Field(default=True, description="Include scenario analysis")
    include_risk_assessment: bool = Field(default=True, description="Include risk assessment")
    include_sensitivity_analysis: bool = Field(default=True, description="Include sensitivity analysis")
    include_monte_carlo_simulation: bool = Field(default=True, description="Include Monte Carlo simulation")
    
    # Economic parameters
    discount_rate: float = Field(default=0.05, ge=0, le=0.2, description="Discount rate for economic analysis")
    inflation_rate: float = Field(default=0.03, ge=0, le=0.1, description="Inflation rate for cost projections")
    
    # Multi-objective optimization parameters
    yield_priority: float = Field(default=0.8, ge=0, le=1, description="Yield optimization priority")
    cost_priority: float = Field(default=0.7, ge=0, le=1, description="Cost optimization priority")
    environmental_priority: float = Field(default=0.6, ge=0, le=1, description="Environmental optimization priority")
    risk_priority: float = Field(default=0.5, ge=0, le=1, description="Risk optimization priority")
    
    # Constraints
    max_fertilizer_rate: Optional[float] = Field(None, description="Maximum fertilizer rate constraint")
    min_yield_target: Optional[float] = Field(None, description="Minimum yield target constraint")
    max_cost_per_unit_yield: Optional[float] = Field(None, description="Maximum cost per unit yield constraint")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="User who created the analysis")

# Scenario Modeling Models
class ScenarioType(str, Enum):
    """Types of economic scenarios."""
    BULL_MARKET = "bull_market"
    BEAR_MARKET = "bear_market"
    VOLATILE_MARKET = "volatile_market"
    SEASONAL_PATTERNS = "seasonal_patterns"
    SUPPLY_DISRUPTION = "supply_disruption"
    BASELINE = "baseline"
    CUSTOM = "custom"

class MarketCondition(str, Enum):
    """Market conditions for scenarios."""
    BULL_MARKET = "bull_market"
    BEAR_MARKET = "bear_market"
    VOLATILE = "volatile"
    STABLE = "stable"
    SEASONAL = "seasonal"
    SUPPLY_DISRUPTION = "supply_disruption"
    CUSTOM = "custom"

class RiskLevel(str, Enum):
    """Risk levels for scenarios."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class EconomicScenarioMetrics(BaseModel):
    """Metrics for economic scenarios."""
    
    total_fertilizer_cost: float = Field(..., description="Total fertilizer cost")
    total_crop_revenue: float = Field(..., description="Total crop revenue")
    net_profit: float = Field(..., description="Net profit")
    profit_margin_percent: float = Field(..., description="Profit margin percentage")
    roi_percent: float = Field(..., description="Return on investment percentage")
    break_even_yield: float = Field(..., description="Break-even yield per acre")
    marginal_return_rate: float = Field(..., description="Marginal return rate")
    risk_adjusted_return: float = Field(..., description="Risk-adjusted return")
    economic_impact_score: float = Field(..., ge=0, le=1, description="Economic impact score")

class EconomicScenario(BaseModel):
    """Model for individual economic scenario."""
    
    scenario_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique scenario identifier")
    scenario_name: str = Field(..., description="Name of the scenario")
    scenario_type: ScenarioType = Field(..., description="Type of scenario")
    market_condition: MarketCondition = Field(..., description="Market condition")
    
    # Price data
    fertilizer_prices: Dict[str, Dict[str, Any]] = Field(..., description="Fertilizer prices by product")
    # Format: {"urea": {"price_per_unit": 450.0, "unit": "ton", "source": "USDA NASS"}}
    crop_prices: Dict[str, float] = Field(..., description="Crop prices by type")
    
    # Scenario metrics
    scenario_metrics: EconomicScenarioMetrics = Field(..., description="Scenario financial metrics")
    
    # Probability and risk
    probability_distribution: Dict[str, Any] = Field(..., description="Probability distribution")
    risk_assessment: Dict[str, Any] = Field(..., description="Risk assessment")
    
    # Scenario details
    description: str = Field(..., description="Description of the scenario")
    assumptions: Dict[str, Any] = Field(default_factory=dict, description="Scenario assumptions")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Multi-Objective Optimization Models
class MultiObjectiveOptimization(BaseModel):
    """Model for multi-objective optimization results."""
    
    optimization_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique optimization identifier")
    scenario_id: str = Field(..., description="Scenario identifier")
    
    # Optimization results
    base_optimization: Optional[Dict[str, Any]] = Field(None, description="Base optimization results")
    weighted_optimization: Optional[Dict[str, Any]] = Field(None, description="Weighted optimization results")
    constraint_optimization: Optional[Dict[str, Any]] = Field(None, description="Constraint optimization results")
    risk_adjusted_optimization: Optional[Dict[str, Any]] = Field(None, description="Risk-adjusted optimization results")
    
    # Objectives and constraints
    objectives: Dict[str, Any] = Field(..., description="Optimization objectives")
    constraints: Dict[str, Any] = Field(..., description="Optimization constraints")
    
    # Optimization methods
    optimization_methods: List[str] = Field(..., description="Optimization methods used")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Risk Assessment Models
class RiskAssessment(BaseModel):
    """Model for risk assessment results."""
    
    assessment_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique assessment identifier")
    scenario_id: str = Field(..., description="Scenario identifier")
    
    # Overall risk score
    overall_risk_score: float = Field(..., ge=0, le=1, description="Overall risk score")
    risk_level: RiskLevel = Field(..., description="Overall risk level")
    
    # Individual risk factors
    individual_risks: Dict[str, float] = Field(..., description="Individual risk factors")
    # Format: {"price_volatility": 0.3, "yield_variability": 0.2, ...}
    
    # Mitigation strategies
    mitigation_strategies: List[str] = Field(..., description="Risk mitigation strategies")
    
    # Confidence intervals
    confidence_intervals: Dict[str, Dict[str, float]] = Field(..., description="Confidence intervals")
    # Format: {"0.95": {"lower": 0.8, "upper": 0.9}}
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Sensitivity Analysis Models
class SensitivityAnalysis(BaseModel):
    """Model for sensitivity analysis results."""
    
    analysis_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique analysis identifier")
    
    # Parameter variations
    parameter_variations: Dict[str, List[float]] = Field(..., description="Parameter variations tested")
    # Format: {"fertilizer_price": [-20, -10, -5, 0, 5, 10, 20]}
    
    # Sensitivity results
    sensitivity_results: Dict[str, List[Dict[str, Any]]] = Field(..., description="Sensitivity results")
    # Format: {"fertilizer_price": [{"variation_percent": -20, "results": {...}}]}
    
    # Critical parameters
    critical_parameters: List[str] = Field(..., description="Critical parameters identified")
    
    # Recommendations
    recommendations: List[str] = Field(..., description="Sensitivity analysis recommendations")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Monte Carlo Simulation Models
class MonteCarloSimulation(BaseModel):
    """Model for Monte Carlo simulation results."""
    
    simulation_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique simulation identifier")
    iterations: int = Field(..., description="Number of iterations")
    confidence_levels: List[float] = Field(..., description="Confidence levels used")
    
    # Scenario results
    scenario_results: List[Dict[str, Any]] = Field(..., description="Results for each scenario")
    # Format: [{"scenario_id": "...", "scenario_name": "...", "mean_profit": ..., "median_profit": ...}]
    
    # Overall statistics
    overall_statistics: Dict[str, Any] = Field(..., description="Overall simulation statistics")
    # Format: {"overall_mean_profit": ..., "overall_median_profit": ..., ...}
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Scenario Modeling Models
class ScenarioModeling(BaseModel):
    """Model for scenario modeling results."""
    
    modeling_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique modeling identifier")
    scenarios: List[EconomicScenario] = Field(..., description="Generated scenarios")
    scenario_probabilities: Dict[str, float] = Field(..., description="Scenario probabilities")
    # Format: {"scenario_id": probability}
    
    # Scenario comparison
    scenario_comparison: Dict[str, Dict[str, Any]] = Field(..., description="Scenario comparison data")
    
    # Recommendations
    recommendations: List[str] = Field(..., description="Scenario modeling recommendations")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Budget Allocation Models
class BudgetAllocation(BaseModel):
    """Model for budget allocation results."""
    
    allocation_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique allocation identifier")
    optimization_id: str = Field(..., description="Optimization identifier")
    
    # Budget information
    total_budget: float = Field(..., description="Total budget allocated")
    field_size_acres: float = Field(..., description="Field size in acres")
    
    # Allocation breakdown
    allocation_breakdown: Dict[str, float] = Field(..., description="Budget allocation breakdown")
    # Format: {"yield_potential": 3600.0, "cost_efficiency": 3000.0, ...}
    
    # Per-acre allocation
    per_acre_allocation: float = Field(..., description="Per-acre allocation")
    budget_utilization: float = Field(..., ge=0, le=1, description="Budget utilization ratio")
    remaining_budget: float = Field(..., description="Remaining budget")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Investment Prioritization Models
class InvestmentPrioritization(BaseModel):
    """Model for investment prioritization results."""
    
    priority_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique priority identifier")
    optimization_id: str = Field(..., description="Optimization identifier")
    
    # Priority scoring
    priority_score: float = Field(..., ge=0, le=1, description="Priority score")
    priority_level: str = Field(..., description="Priority level (high|medium|low|defer)")
    
    # Investment recommendations
    investment_recommendations: List[str] = Field(..., description="Investment recommendations")
    
    # Financial metrics
    risk_adjusted_return: float = Field(..., description="Risk-adjusted return")
    
    # Timing information
    payback_period: Dict[str, Any] = Field(..., description="Payback period information")
    # Format: {"years": 3, "months": 6, "confidence": 0.8}
    
    # Opportunity cost
    opportunity_cost: Dict[str, Any] = Field(..., description="Opportunity cost analysis")
    # Format: {"alternative_investment": "...", "cost_of_delay": ..., "forgone_returns": ...}
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ROI Analysis Models
class ROIAnalysis(BaseModel):
    """Model for ROI analysis results."""
    
    analysis_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique analysis identifier")
    investment_options: List[Dict[str, Any]] = Field(..., description="Investment options analyzed")
    
    # ROI metrics
    roi_percentages: Dict[str, float] = Field(..., description="ROI percentages by investment")
    # Format: {"investment_id": roi_percentage}
    
    # Break-even analysis
    break_even_analysis: Dict[str, Any] = Field(..., description="Break-even analysis")
    
    # Risk assessment
    risk_adjusted_rois: Dict[str, float] = Field(..., description="Risk-adjusted ROIs")
    
    # Recommendations
    recommendations: List[str] = Field(..., description="ROI analysis recommendations")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Break Even Analysis Models
class BreakEvenAnalysis(BaseModel):
    """Model for break-even analysis results."""
    
    analysis_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique analysis identifier")
    
    # Break-even metrics
    break_even_yield: float = Field(..., description="Break-even yield per acre")
    break_even_price: float = Field(..., description="Break-even crop price")
    break_even_cost: float = Field(..., description="Break-even fertilizer cost")
    
    # Safety margin
    safety_margin: float = Field(..., description="Safety margin percentage")
    probability_of_profitability: float = Field(..., ge=0, le=1, description="Probability of profitability")
    
    # Risk factors
    risk_factors: List[str] = Field(..., description="Risk factors affecting break-even")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Payback Period Models
class PaybackPeriod(BaseModel):
    """Model for payback period analysis."""
    
    years: int = Field(..., description="Payback period in years")
    months: int = Field(..., ge=0, le=11, description="Additional months in payback period")
    confidence: float = Field(..., ge=0, le=1, description="Confidence in payback period estimate")

# Opportunity Cost Models
class OpportunityCost(BaseModel):
    """Model for opportunity cost analysis."""
    
    alternative_investment: str = Field(..., description="Alternative investment option")
    cost_of_delay: float = Field(..., description="Cost of delaying investment")
    forgone_returns: float = Field(..., description="Returns foregone by choosing this investment")

# Economic Impact Models
class EconomicImpact(BaseModel):
    """Model for economic impact assessment."""
    
    impact_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique impact identifier")
    
    # Impact metrics
    total_economic_impact: float = Field(..., description="Total economic impact")
    per_acre_impact: float = Field(..., description="Per-acre economic impact")
    
    # Impact components
    impact_components: Dict[str, float] = Field(..., description="Economic impact components")
    # Format: {"revenue_increase": ..., "cost_reduction": ..., "risk_mitigation": ...}
    
    # Confidence and uncertainty
    confidence_level: float = Field(..., ge=0, le=1, description="Confidence in impact assessment")
    uncertainty_range: Dict[str, float] = Field(..., description="Uncertainty range for impact")
    # Format: {"lower_bound": ..., "upper_bound": ...}
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Constraint Relaxation Models
class ConstraintRelaxation(BaseModel):
    """Model for constraint relaxation analysis."""
    
    relaxation_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique relaxation identifier")
    
    # Constraint information
    constraint_type: str = Field(..., description="Type of constraint relaxed")
    original_value: float = Field(..., description="Original constraint value")
    relaxed_value: float = Field(..., description="Relaxed constraint value")
    
    # Impact analysis
    relaxation_impact: Dict[str, float] = Field(..., description="Impact of relaxation on objectives")
    # Format: {"objective": impact_value}
    
    # Cost-benefit
    cost_of_relaxation: float = Field(..., description="Cost of relaxing this constraint")
    benefit_of_relaxation: float = Field(..., description="Benefit of relaxing this constraint")
    
    # Recommendation
    recommendation: str = Field(..., description="Recommendation for constraint relaxation")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Pareto Frontier Models
class ParetoFrontierPoint(BaseModel):
    """Model for Pareto frontier analysis point."""
    
    point_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique point identifier")
    
    # Objective values
    total_cost: float = Field(..., description="Total cost")
    total_revenue: float = Field(..., description="Total revenue")
    roi_percentage: float = Field(..., description="ROI percentage")
    
    # Environmental and risk metrics
    environmental_score: float = Field(..., description="Environmental impact score")
    risk_score: float = Field(..., description="Risk score")
    
    # Achievement metrics
    yield_target_achievement: float = Field(..., description="Yield target achievement percentage")
    budget_utilization: float = Field(..., description="Budget utilization percentage")
    
    # Description
    trade_off_description: str = Field(..., description="Description of trade-offs")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ParetoFrontier(BaseModel):
    """Model for Pareto frontier analysis."""
    
    frontier_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique frontier identifier")
    points: List[ParetoFrontierPoint] = Field(..., description="Pareto frontier points")
    
    # Recommended point
    recommended_point: ParetoFrontierPoint = Field(..., description="Recommended Pareto frontier point")
    
    # Analysis
    trade_off_analysis: Dict[str, Any] = Field(..., description="Trade-off analysis between objectives")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Trade Off Analysis Models
class TradeOffAnalysis(BaseModel):
    """Model for trade-off analysis results."""
    
    analysis_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique analysis identifier")
    
    # Trade-off matrix
    trade_off_matrix: Dict[str, Dict[str, float]] = Field(..., description="Trade-off matrix")
    # Format: {"objective1": {"objective2": trade_off_value}}
    
    # Dominant solutions
    dominant_solutions: List[Dict[str, Any]] = Field(..., description="Dominant solution sets")
    
    # Compromise solutions
    compromise_solutions: List[Dict[str, Any]] = Field(..., description="Compromise solution sets")
    
    # Recommendations
    recommendations: List[str] = Field(..., description="Trade-off analysis recommendations")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Economic Optimization Response Models
class EconomicOptimizationResponse(BaseModel):
    """Response model for economic optimization analysis."""
    
    analysis_id: str = Field(..., description="Analysis identifier")
    
    # Scenario modeling
    scenarios: List[EconomicScenario] = Field(..., description="Generated economic scenarios")
    
    # Optimization results
    optimization_results: List[MultiObjectiveOptimization] = Field(..., description="Optimization results")
    
    # Risk assessments
    risk_assessments: List[RiskAssessment] = Field(..., description="Risk assessments")
    
    # Sensitivity analysis
    sensitivity_analysis: SensitivityAnalysis = Field(..., description="Sensitivity analysis")
    
    # Monte Carlo simulation
    monte_carlo_simulation: MonteCarloSimulation = Field(..., description="Monte Carlo simulation results")
    
    # Budget allocations
    budget_allocations: List[BudgetAllocation] = Field(..., description="Budget allocation recommendations")
    
    # Investment priorities
    investment_priorities: List[InvestmentPrioritization] = Field(..., description="Investment prioritization")
    
    # Recommendations
    recommendations: List[str] = Field(..., description="Economic optimization recommendations")
    
    # Performance metrics
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('scenarios')
    @classmethod
    def validate_scenarios(cls, v):
        """Validate scenarios list."""
        if not v:
            raise ValueError("At least one scenario is required")
        return v

    @field_validator('optimization_results')
    @classmethod
    def validate_optimization_results(cls, v):
        """Validate optimization results list."""
        if not v:
            raise ValueError("At least one optimization result is required")
        return v

    @field_validator('risk_assessments')
    @classmethod
    def validate_risk_assessments(cls, v):
        """Validate risk assessments list."""
        if not v:
            raise ValueError("At least one risk assessment is required")
        return v

    @field_validator('budget_allocations')
    @classmethod
    def validate_budget_allocations(cls, v):
        """Validate budget allocations list."""
        if not v:
            raise ValueError("At least one budget allocation is required")
        return v

    @field_validator('investment_priorities')
    @classmethod
    def validate_investment_priorities(cls, v):
        """Validate investment priorities list."""
        if not v:
            raise ValueError("At least one investment priority is required")
        return v

    @model_validator(mode='after')
    def validate_response_consistency(self):
        """Validate consistency across response components."""
        # Ensure all scenario IDs match
        scenario_ids = {s.scenario_id for s in self.scenarios}
        optimization_scenario_ids = {o.scenario_id for o in self.optimization_results}
        risk_scenario_ids = {r.scenario_id for r in self.risk_assessments}
        
        # Check that all optimization results have matching scenarios
        if not optimization_scenario_ids.issubset(scenario_ids):
            raise ValueError("Some optimization results reference non-existent scenarios")
            
        # Check that all risk assessments have matching scenarios
        if not risk_scenario_ids.issubset(scenario_ids):
            raise ValueError("Some risk assessments reference non-existent scenarios")
            
        return self
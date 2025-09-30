"""
Pydantic models for comprehensive price scenario modeling system.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any, Tuple, Union
from datetime import datetime, date
from enum import Enum
import uuid


class ScenarioType(str, Enum):
    """Types of price scenarios."""
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


class PriceScenarioModelingRequest(BaseModel):
    """Request model for comprehensive price scenario modeling."""
    
    # Analysis configuration
    analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique analysis identifier")
    analysis_name: Optional[str] = Field(None, description="Name for the analysis")
    
    # Farm and field data
    farm_id: Optional[str] = Field(None, description="Farm identifier")
    field_id: Optional[str] = Field(None, description="Field identifier")
    field_size_acres: float = Field(..., gt=0, description="Field size in acres")
    region: Optional[str] = Field("US", description="Geographic region")
    
    # Crop and yield data
    crop_type: str = Field(..., description="Type of crop")
    expected_yield_bu_per_acre: float = Field(..., gt=0, description="Expected yield in bushels per acre")
    crop_price_per_bu: float = Field(..., gt=0, description="Expected crop price per bushel")
    
    # Fertilizer requirements
    fertilizer_requirements: List[Dict[str, Any]] = Field(..., description="Fertilizer requirements")
    # Format: [{"product": "urea", "type": "nitrogen", "rate_lbs_per_acre": 100, "application_method": "broadcast"}]
    
    # Analysis parameters
    analysis_horizon_days: int = Field(default=365, ge=30, le=1095, description="Analysis horizon in days")
    confidence_level: float = Field(default=0.95, ge=0.5, le=0.99, description="Confidence level for analysis")
    
    # Scenario parameters
    scenarios: Optional[List[ScenarioType]] = Field(None, description="Scenarios to analyze")
    custom_scenarios: Optional[List[Dict[str, Any]]] = Field(None, description="Custom scenario definitions")
    
    # Monte Carlo parameters
    monte_carlo_iterations: Optional[int] = Field(10000, ge=1000, le=100000, description="Number of Monte Carlo iterations")
    
    # Stochastic modeling parameters
    stochastic_model_type: Optional[str] = Field("geometric_brownian_motion", description="Type of stochastic model")
    
    # Sensitivity analysis parameters
    sensitivity_price_changes: Optional[List[float]] = Field(None, description="Price change percentages for sensitivity analysis")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="User who created the analysis")


class PriceForecast(BaseModel):
    """Model for individual price forecast."""
    
    product_name: str = Field(..., description="Name of the fertilizer product")
    current_price: float = Field(..., gt=0, description="Current price per unit")
    forecasted_price: float = Field(..., gt=0, description="Forecasted price per unit")
    price_change_percent: float = Field(..., description="Price change percentage")
    confidence_level: float = Field(..., ge=0.0, le=1.0, description="Confidence level for forecast")
    forecast_horizon_days: int = Field(..., gt=0, description="Forecast horizon in days")
    volatility_factor: float = Field(..., ge=0.0, description="Volatility factor for the forecast")


class PriceScenario(BaseModel):
    """Model for individual price scenario."""
    
    scenario_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique scenario identifier")
    scenario_name: str = Field(..., description="Name of the scenario")
    scenario_type: ScenarioType = Field(..., description="Type of scenario")
    market_condition: MarketCondition = Field(..., description="Market condition")
    
    # Price forecasts
    price_forecasts: List[PriceForecast] = Field(..., description="Price forecasts for products")
    
    # Scenario metrics
    scenario_metrics: Dict[str, Any] = Field(..., description="Scenario financial metrics")
    
    # Probability and risk
    probability_distribution: 'ProbabilityDistribution' = Field(..., description="Probability distribution")
    risk_assessment: 'RiskAssessment' = Field(..., description="Risk assessment")
    
    # Scenario details
    description: str = Field(..., description="Description of the scenario")
    assumptions: Dict[str, Any] = Field(default_factory=dict, description="Scenario assumptions")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ProbabilityDistribution(BaseModel):
    """Model for probability distribution."""
    
    mean_probability: float = Field(..., ge=0.0, le=1.0, description="Mean probability")
    standard_deviation: float = Field(..., ge=0.0, description="Standard deviation")
    confidence_intervals: Dict[str, float] = Field(..., description="Confidence intervals")


class RiskAssessment(BaseModel):
    """Model for risk assessment."""
    
    overall_risk_level: RiskLevel = Field(..., description="Overall risk level")
    price_volatility_risk: float = Field(..., ge=0.0, le=1.0, description="Price volatility risk")
    supply_chain_risk: float = Field(..., ge=0.0, le=1.0, description="Supply chain risk")
    market_demand_risk: float = Field(..., ge=0.0, le=1.0, description="Market demand risk")
    economic_risk: float = Field(..., ge=0.0, le=1.0, description="Economic risk")
    risk_factors: List[str] = Field(default_factory=list, description="List of risk factors")


class MonteCarloSimulation(BaseModel):
    """Model for Monte Carlo simulation results."""
    
    simulation_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique simulation identifier")
    iterations: int = Field(..., description="Number of iterations")
    confidence_levels: List[float] = Field(..., description="Confidence levels used")
    scenario_results: List[Dict[str, Any]] = Field(..., description="Results for each scenario")
    overall_statistics: Dict[str, Any] = Field(..., description="Overall simulation statistics")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class StochasticModel(BaseModel):
    """Model for stochastic modeling results."""
    
    model_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique model identifier")
    model_type: str = Field(..., description="Type of stochastic model")
    scenarios: List[Dict[str, Any]] = Field(..., description="Stochastic results for each scenario")
    model_parameters: Dict[str, Any] = Field(..., description="Model parameters")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SensitivityAnalysis(BaseModel):
    """Model for sensitivity analysis results."""
    
    analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique analysis identifier")
    price_change_percentages: List[float] = Field(..., description="Price change percentages tested")
    scenario_results: List[Dict[str, Any]] = Field(..., description="Sensitivity results for each scenario")
    sensitivity_metrics: Dict[str, Any] = Field(..., description="Overall sensitivity metrics")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DecisionTreeNode(BaseModel):
    """Model for decision tree node."""
    
    node_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique node identifier")
    node_type: str = Field(..., description="Type of node (root, scenario, action)")
    decision_criteria: str = Field(..., description="Decision criteria")
    description: str = Field(..., description="Node description")
    expected_value: Optional[float] = Field(None, description="Expected value")
    probability: Optional[float] = Field(None, ge=0.0, le=1.0, description="Probability")
    risk_level: Optional[RiskLevel] = Field(None, description="Risk level")
    children: List['DecisionTreeNode'] = Field(default_factory=list, description="Child nodes")


class SeasonalPattern(BaseModel):
    """Model for seasonal price patterns."""
    
    pattern_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique pattern identifier")
    season: str = Field(..., description="Season (spring, summer, fall, winter)")
    price_multiplier: float = Field(..., gt=0, description="Price multiplier for season")
    demand_factor: float = Field(..., gt=0, description="Demand factor for season")
    supply_factor: float = Field(..., gt=0, description="Supply factor for season")
    description: str = Field(..., description="Description of seasonal pattern")


class SupplyDisruptionScenario(BaseModel):
    """Model for supply disruption scenarios."""
    
    disruption_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique disruption identifier")
    disruption_type: str = Field(..., description="Type of disruption")
    severity: str = Field(..., description="Severity level (low, medium, high, critical)")
    duration_days: int = Field(..., gt=0, description="Expected duration in days")
    price_impact_multiplier: float = Field(..., gt=0, description="Price impact multiplier")
    affected_products: List[str] = Field(..., description="Products affected by disruption")
    probability: float = Field(..., ge=0.0, le=1.0, description="Probability of disruption")
    description: str = Field(..., description="Description of disruption scenario")


class PriceScenarioModelingResponse(BaseModel):
    """Response model for comprehensive price scenario modeling."""
    
    analysis_id: str = Field(..., description="Analysis identifier")
    scenarios: List[PriceScenario] = Field(..., description="Generated scenarios")
    monte_carlo_simulation: MonteCarloSimulation = Field(..., description="Monte Carlo simulation results")
    stochastic_model: StochasticModel = Field(..., description="Stochastic modeling results")
    sensitivity_analysis: SensitivityAnalysis = Field(..., description="Sensitivity analysis results")
    decision_tree: DecisionTreeNode = Field(..., description="Decision tree for scenario planning")
    recommendations: List[str] = Field(..., description="Generated recommendations")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Update forward references
PriceScenario.model_rebuild()
DecisionTreeNode.model_rebuild()
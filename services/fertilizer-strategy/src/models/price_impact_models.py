"""
Pydantic models for advanced price impact analysis system.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, date
from enum import Enum
import uuid


class AnalysisType(str, Enum):
    """Types of price impact analysis."""
    SENSITIVITY = "sensitivity"
    SCENARIO = "scenario"
    RISK_ASSESSMENT = "risk_assessment"
    PROFITABILITY_IMPACT = "profitability_impact"
    TIMING_OPTIMIZATION = "timing_optimization"


class ScenarioType(str, Enum):
    """Types of price scenarios."""
    BASELINE = "baseline"
    OPTIMISTIC = "optimistic"
    PESSIMISTIC = "pessimistic"
    VOLATILE = "volatile"
    CUSTOM = "custom"


class RiskLevel(str, Enum):
    """Risk levels for price impact analysis."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PriceImpactAnalysisRequest(BaseModel):
    """Request model for price impact analysis."""
    
    # Analysis configuration
    analysis_type: AnalysisType = Field(..., description="Type of analysis to perform")
    analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique analysis identifier")
    
    # Farm and field data
    farm_id: Optional[str] = Field(None, description="Farm identifier")
    field_id: Optional[str] = Field(None, description="Field identifier")
    field_size_acres: float = Field(..., gt=0, description="Field size in acres")
    
    # Crop and yield data
    crop_type: str = Field(..., description="Type of crop")
    expected_yield_bu_per_acre: float = Field(..., gt=0, description="Expected yield in bushels per acre")
    crop_price_per_bu: float = Field(..., gt=0, description="Expected crop price per bushel")
    
    # Fertilizer requirements
    fertilizer_requirements: List[Dict[str, Any]] = Field(..., description="Fertilizer requirements")
    # Format: [{"product": "urea", "rate_lbs_per_acre": 100, "application_method": "broadcast"}]
    
    # Analysis parameters
    analysis_horizon_days: int = Field(default=365, ge=30, le=1095, description="Analysis horizon in days")
    confidence_level: float = Field(default=0.95, ge=0.5, le=0.99, description="Confidence level for analysis")
    
    # Scenario parameters (for scenario analysis)
    scenarios: Optional[List[ScenarioType]] = Field(None, description="Scenarios to analyze")
    custom_scenarios: Optional[List[Dict[str, Any]]] = Field(None, description="Custom scenario definitions")
    
    # Sensitivity parameters
    price_change_percentages: Optional[List[float]] = Field(None, description="Price change percentages for sensitivity analysis")
    
    # Risk parameters
    volatility_threshold: Optional[float] = Field(None, description="Volatility threshold for risk assessment")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="User who created the analysis")


class PriceImpactScenario(BaseModel):
    """Model for individual price impact scenario."""
    
    scenario_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    scenario_name: str = Field(..., description="Name of the scenario")
    scenario_type: ScenarioType = Field(..., description="Type of scenario")
    
    # Price assumptions
    fertilizer_price_multiplier: float = Field(..., description="Multiplier for fertilizer prices")
    crop_price_multiplier: float = Field(..., description="Multiplier for crop prices")
    
    # Probability and risk
    probability: float = Field(..., ge=0.0, le=1.0, description="Probability of scenario occurring")
    risk_level: RiskLevel = Field(..., description="Risk level of scenario")
    
    # Scenario description
    description: str = Field(..., description="Description of the scenario")
    assumptions: Dict[str, Any] = Field(default_factory=dict, description="Scenario assumptions")


class PriceImpactMetrics(BaseModel):
    """Model for price impact metrics."""
    
    # Financial metrics
    total_fertilizer_cost: float = Field(..., description="Total fertilizer cost")
    total_crop_revenue: float = Field(..., description="Total crop revenue")
    net_profit: float = Field(..., description="Net profit")
    profit_margin_percent: float = Field(..., description="Profit margin percentage")
    
    # Cost per unit metrics
    fertilizer_cost_per_acre: float = Field(..., description="Fertilizer cost per acre")
    fertilizer_cost_per_bu: float = Field(..., description="Fertilizer cost per bushel")
    crop_revenue_per_acre: float = Field(..., description="Crop revenue per acre")
    
    # Impact metrics
    price_impact_percent: float = Field(..., description="Price impact percentage")
    profitability_change_percent: float = Field(..., description="Change in profitability percentage")
    
    # Risk metrics
    value_at_risk: Optional[float] = Field(None, description="Value at Risk (VaR)")
    expected_shortfall: Optional[float] = Field(None, description="Expected Shortfall")
    volatility_impact: Optional[float] = Field(None, description="Volatility impact on profitability")


class SensitivityAnalysisResult(BaseModel):
    """Model for sensitivity analysis results."""
    
    parameter_name: str = Field(..., description="Parameter being analyzed")
    parameter_values: List[float] = Field(..., description="Values of the parameter")
    impact_values: List[float] = Field(..., description="Impact on profitability for each value")
    
    # Sensitivity metrics
    elasticity: float = Field(..., description="Price elasticity of profitability")
    sensitivity_score: float = Field(..., description="Overall sensitivity score")
    critical_threshold: Optional[float] = Field(None, description="Critical threshold value")
    
    # Analysis metadata
    analysis_date: datetime = Field(default_factory=datetime.utcnow)


class RiskAssessmentResult(BaseModel):
    """Model for risk assessment results."""
    
    overall_risk_level: RiskLevel = Field(..., description="Overall risk level")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Overall risk score")
    
    # Risk factors
    price_volatility_risk: float = Field(..., description="Price volatility risk score")
    market_timing_risk: float = Field(..., description="Market timing risk score")
    supply_chain_risk: float = Field(..., description="Supply chain risk score")
    weather_risk: float = Field(..., description="Weather-related risk score")
    
    # Risk mitigation
    recommended_actions: List[str] = Field(..., description="Recommended risk mitigation actions")
    hedging_recommendations: List[str] = Field(default_factory=list, description="Hedging recommendations")
    
    # Analysis metadata
    analysis_date: datetime = Field(default_factory=datetime.utcnow)


class PriceImpactAnalysisResult(BaseModel):
    """Model for comprehensive price impact analysis results."""
    
    analysis_id: str = Field(..., description="Analysis identifier")
    analysis_type: AnalysisType = Field(..., description="Type of analysis performed")
    analysis_date: datetime = Field(default_factory=datetime.utcnow)
    
    # Baseline scenario
    baseline_metrics: PriceImpactMetrics = Field(..., description="Baseline scenario metrics")
    
    # Scenario results
    scenarios: List[Dict[str, Any]] = Field(default_factory=list, description="Scenario analysis results")
    
    # Sensitivity analysis
    sensitivity_results: Optional[List[SensitivityAnalysisResult]] = Field(None, description="Sensitivity analysis results")
    
    # Risk assessment
    risk_assessment: Optional[RiskAssessmentResult] = Field(None, description="Risk assessment results")
    
    # Recommendations
    recommendations: List[str] = Field(default_factory=list, description="Strategic recommendations")
    optimal_timing: Optional[str] = Field(None, description="Optimal timing recommendation")
    
    # Analysis metadata
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Analysis confidence score")
    data_quality_score: float = Field(..., ge=0.0, le=1.0, description="Data quality score")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


class PriceImpactAnalysisResponse(BaseModel):
    """Response model for price impact analysis."""
    
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    success: bool = Field(..., description="Whether analysis was successful")
    
    # Results
    analysis_result: Optional[PriceImpactAnalysisResult] = Field(None, description="Analysis results")
    
    # Error information
    error_message: Optional[str] = Field(None, description="Error message if analysis failed")
    error_code: Optional[str] = Field(None, description="Error code if analysis failed")
    
    # Metadata
    processing_time_ms: float = Field(..., description="Total processing time")
    data_sources_used: List[str] = Field(default_factory=list, description="Data sources used")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PriceImpactPrediction(BaseModel):
    """Model for price impact predictions."""
    
    prediction_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    prediction_date: datetime = Field(default_factory=datetime.utcnow)
    
    # Prediction parameters
    prediction_horizon_days: int = Field(..., description="Prediction horizon in days")
    confidence_interval: Tuple[float, float] = Field(..., description="Confidence interval")
    
    # Predicted values
    predicted_fertilizer_price: float = Field(..., description="Predicted fertilizer price")
    predicted_crop_price: float = Field(..., description="Predicted crop price")
    predicted_profitability: float = Field(..., description="Predicted profitability")
    
    # Prediction quality
    prediction_accuracy: Optional[float] = Field(None, description="Prediction accuracy score")
    model_confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence score")
    
    # Model information
    model_version: str = Field(..., description="Model version used")
    features_used: List[str] = Field(..., description="Features used in prediction")


class MarketIntelligenceInsight(BaseModel):
    """Model for market intelligence insights."""
    
    insight_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    insight_type: str = Field(..., description="Type of insight")
    insight_date: datetime = Field(default_factory=datetime.utcnow)
    
    # Insight content
    title: str = Field(..., description="Insight title")
    description: str = Field(..., description="Insight description")
    impact_level: str = Field(..., description="Impact level (low/medium/high)")
    
    # Market factors
    affected_products: List[str] = Field(default_factory=list, description="Products affected")
    affected_regions: List[str] = Field(default_factory=list, description="Regions affected")
    
    # Recommendations
    recommended_actions: List[str] = Field(default_factory=list, description="Recommended actions")
    risk_factors: List[str] = Field(default_factory=list, description="Risk factors")
    
    # Metadata
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Insight confidence score")
    source: str = Field(..., description="Source of the insight")


class PriceImpactAnalysisSummary(BaseModel):
    """Model for price impact analysis summary."""
    
    summary_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    summary_date: datetime = Field(default_factory=datetime.utcnow)
    
    # Summary statistics
    total_analyses: int = Field(..., description="Total number of analyses")
    average_profitability_impact: float = Field(..., description="Average profitability impact")
    most_volatile_product: str = Field(..., description="Most volatile fertilizer product")
    highest_risk_scenario: str = Field(..., description="Highest risk scenario")
    
    # Key insights
    key_insights: List[str] = Field(..., description="Key insights from analyses")
    market_trends: List[str] = Field(default_factory=list, description="Market trends identified")
    
    # Recommendations
    strategic_recommendations: List[str] = Field(..., description="Strategic recommendations")
    risk_mitigation_strategies: List[str] = Field(default_factory=list, description="Risk mitigation strategies")
    
    # Data quality
    data_coverage_percent: float = Field(..., description="Data coverage percentage")
    analysis_confidence: float = Field(..., description="Overall analysis confidence")


@field_validator('fertilizer_requirements')
@classmethod
def validate_fertilizer_requirements(cls, v):
    """Validate fertilizer requirements format."""
    if not v:
        raise ValueError('Fertilizer requirements cannot be empty')
    
    for req in v:
        required_fields = ['product', 'rate_lbs_per_acre']
        for field in required_fields:
            if field not in req:
                raise ValueError(f'Missing required field: {field}')
        
        if req['rate_lbs_per_acre'] <= 0:
            raise ValueError('Fertilizer rate must be positive')
    
    return v


@field_validator('price_change_percentages')
@classmethod
def validate_price_change_percentages(cls, v):
    """Validate price change percentages."""
    if v is not None:
        for pct in v:
            if abs(pct) > 100:
                raise ValueError('Price change percentages must be between -100% and 100%')
    return v
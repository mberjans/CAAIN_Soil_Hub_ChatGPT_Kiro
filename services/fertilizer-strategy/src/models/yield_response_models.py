"""
Data models for sophisticated yield-fertilizer response curves.

This module provides data models for yield response analysis including:
- Nutrient response curves with multiple mathematical models
- Interaction effects between nutrients
- Optimal rate calculations with confidence intervals
- Economic threshold analysis
- Model validation and comparison
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator
from uuid import UUID, uuid4


class ResponseModelType(str, Enum):
    """Types of response curve models."""
    MITSCHERLICH_BAULE = "mitscherlich_baule"
    QUADRATIC_PLATEAU = "quadratic_plateau"
    LINEAR_PLATEAU = "linear_plateau"
    EXPONENTIAL = "exponential"


class InteractionType(str, Enum):
    """Types of nutrient interactions."""
    SYNERGISTIC = "synergistic"
    ANTAGONISTIC = "antagonistic"
    ADDITIVE = "additive"


class SignificanceLevel(str, Enum):
    """Significance levels for interactions."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class NutrientResponseData(BaseModel):
    """Individual nutrient response data point."""
    field_id: UUID = Field(..., description="Field identifier")
    year: int = Field(..., ge=1900, le=2030, description="Year of data")
    nutrient_rates: Dict[str, float] = Field(..., description="Nutrient application rates")
    yield_per_acre: float = Field(..., ge=0.0, description="Yield per acre")
    crop_type: str = Field(..., description="Type of crop")
    variety: Optional[str] = Field(None, description="Crop variety")
    soil_conditions: Optional[Dict[str, Any]] = Field(None, description="Soil conditions")
    weather_conditions: Optional[Dict[str, Any]] = Field(None, description="Weather conditions")
    management_practices: Optional[Dict[str, Any]] = Field(None, description="Management practices")
    notes: Optional[str] = Field(None, description="Additional notes")


class YieldResponseRequest(BaseModel):
    """Request for yield response analysis."""
    field_id: UUID = Field(..., description="Field identifier")
    crop_type: str = Field(..., description="Type of crop")
    nutrients: List[str] = Field(..., min_length=1, description="Nutrients to analyze")
    response_data: List[NutrientResponseData] = Field(..., min_length=3, description="Response data points")
    economic_parameters: Dict[str, Any] = Field(..., description="Economic parameters for optimization")
    analysis_preferences: Optional[Dict[str, Any]] = Field(None, description="Analysis preferences")
    
    @field_validator('nutrients')
    @classmethod
    def validate_nutrients(cls, v):
        """Validate nutrient list."""
        if len(v) == 0:
            raise ValueError("At least one nutrient must be specified")
        return v
    
    @field_validator('response_data')
    @classmethod
    def validate_response_data(cls, v):
        """Validate response data."""
        if len(v) < 3:
            raise ValueError("At least 3 data points required for curve fitting")
        return v


class CurveFitResult(BaseModel):
    """Result of curve fitting for a single model."""
    model_type: ResponseModelType = Field(..., description="Type of model fitted")
    parameters: List[float] = Field(..., description="Fitted model parameters")
    parameter_errors: List[float] = Field(..., description="Standard errors of parameters")
    r_squared: float = Field(..., ge=0.0, le=1.0, description="R-squared value")
    covariance_matrix: List[List[float]] = Field(..., description="Parameter covariance matrix")


class YieldResponseCurve(BaseModel):
    """Fitted yield response curve for a nutrient."""
    nutrient: str = Field(..., description="Nutrient name")
    model_type: ResponseModelType = Field(..., description="Type of fitted model")
    parameters: List[float] = Field(..., description="Model parameters")
    r_squared: float = Field(..., ge=0.0, le=1.0, description="Model R-squared")
    rmse: float = Field(..., ge=0.0, description="Root mean square error")
    mse: float = Field(..., ge=0.0, description="Mean square error")
    data_points: List[Tuple[float, float]] = Field(..., description="Original data points (rate, yield)")
    predicted_curve: List[Tuple[float, float]] = Field(..., description="Predicted curve points")
    max_yield: float = Field(..., ge=0.0, description="Maximum yield for this nutrient")
    response_range: Tuple[float, float] = Field(..., description="Typical response range")


class InteractionEffect(BaseModel):
    """Nutrient interaction effect analysis."""
    nutrient1: str = Field(..., description="First nutrient")
    nutrient2: str = Field(..., description="Second nutrient")
    interaction_strength: float = Field(..., description="Strength of interaction (-1 to 1)")
    interaction_type: InteractionType = Field(..., description="Type of interaction")
    significance: SignificanceLevel = Field(..., description="Significance level")
    expected_interaction: float = Field(..., description="Expected interaction strength")
    deviation_from_expected: float = Field(..., description="Deviation from expected")


class OptimalRateAnalysis(BaseModel):
    """Analysis of optimal nutrient application rates."""
    nutrient: str = Field(..., description="Nutrient name")
    economic_optimal_rate: float = Field(..., ge=0.0, description="Economic optimal rate")
    max_yield_rate: float = Field(..., ge=0.0, description="Rate for maximum yield")
    target_yield_rate: float = Field(..., ge=0.0, description="Rate for target yield (95% of max)")
    economic_optimal_yield: float = Field(..., ge=0.0, description="Yield at economic optimal rate")
    max_yield: float = Field(..., ge=0.0, description="Maximum achievable yield")
    target_yield: float = Field(..., ge=0.0, description="Target yield (95% of max)")
    marginal_revenue_at_optimal: float = Field(..., description="Marginal revenue at optimal rate")
    marginal_cost_at_optimal: float = Field(..., description="Marginal cost at optimal rate")


class EconomicThreshold(BaseModel):
    """Economic thresholds for nutrient application."""
    nutrient: str = Field(..., description="Nutrient name")
    break_even_rate: float = Field(..., ge=0.0, description="Break-even application rate")
    minimum_profitable_rate: float = Field(..., ge=0.0, description="Minimum profitable rate")
    maximum_profitable_rate: float = Field(..., ge=0.0, description="Maximum profitable rate")
    fertilizer_price: float = Field(..., ge=0.0, description="Fertilizer price per unit")
    crop_price: float = Field(..., ge=0.0, description="Crop price per unit")
    price_ratio: float = Field(..., ge=0.0, description="Crop to fertilizer price ratio")


class ModelValidation(BaseModel):
    """Model validation results."""
    is_valid: bool = Field(..., description="Whether model is valid")
    quality_score: float = Field(..., ge=0.0, le=1.0, description="Overall quality score")
    issues: List[str] = Field(default_factory=list, description="Critical issues")
    warnings: List[str] = Field(default_factory=list, description="Warnings")
    data_points: int = Field(..., ge=0, description="Number of data points")
    nutrient_coverage: int = Field(..., ge=0, description="Number of nutrients covered")
    validation_metrics: Optional[Dict[str, float]] = Field(None, description="Additional validation metrics")


class ConfidenceInterval(BaseModel):
    """Confidence interval for a response curve point."""
    x_value: float = Field(..., ge=0.0, description="Nutrient rate")
    predicted_yield: float = Field(..., ge=0.0, description="Predicted yield")
    lower_bound: float = Field(..., ge=0.0, description="Lower confidence bound")
    upper_bound: float = Field(..., ge=0.0, description="Upper confidence bound")
    confidence_level: float = Field(..., ge=0.0, le=1.0, description="Confidence level")
    margin_of_error: float = Field(..., ge=0.0, description="Margin of error")


class ResponseCurveComparison(BaseModel):
    """Comparison of different response curve models."""
    model_performance: Dict[str, List[Dict[str, Any]]] = Field(..., description="Performance by model type")
    model_averages: Dict[str, Dict[str, float]] = Field(..., description="Average performance by model")
    best_performing_model: ResponseModelType = Field(..., description="Best performing model")
    comparison_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Comparison timestamp")


class YieldResponseAnalysis(BaseModel):
    """Comprehensive yield response analysis result."""
    analysis_id: UUID = Field(default_factory=uuid4, description="Analysis identifier")
    field_id: UUID = Field(..., description="Field identifier")
    crop_type: str = Field(..., description="Type of crop")
    nutrient_curves: Dict[str, YieldResponseCurve] = Field(..., description="Fitted response curves")
    interaction_effects: List[InteractionEffect] = Field(..., description="Nutrient interaction effects")
    optimal_rates: Dict[str, OptimalRateAnalysis] = Field(..., description="Optimal rate analysis")
    economic_thresholds: Dict[str, EconomicThreshold] = Field(..., description="Economic thresholds")
    model_validations: Dict[str, ModelValidation] = Field(..., description="Model validation results")
    model_comparison: ResponseCurveComparison = Field(..., description="Model comparison")
    confidence_intervals: Dict[str, List[ConfidenceInterval]] = Field(..., description="Confidence intervals")
    validation_result: ModelValidation = Field(..., description="Overall validation result")
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class YieldResponseSummary(BaseModel):
    """Summary of yield response analysis."""
    analysis_id: UUID = Field(..., description="Analysis identifier")
    field_id: UUID = Field(..., description="Field identifier")
    crop_type: str = Field(..., description="Type of crop")
    nutrients_analyzed: List[str] = Field(..., description="Nutrients analyzed")
    best_models: Dict[str, ResponseModelType] = Field(..., description="Best model for each nutrient")
    overall_quality_score: float = Field(..., ge=0.0, le=1.0, description="Overall analysis quality")
    key_recommendations: List[str] = Field(..., description="Key recommendations")
    analysis_timestamp: datetime = Field(..., description="Analysis timestamp")


class YieldResponseComparison(BaseModel):
    """Comparison of yield response analyses."""
    analysis_ids: List[UUID] = Field(..., min_length=2, description="Analysis identifiers to compare")
    comparison_metrics: Dict[str, Any] = Field(..., description="Comparison metrics")
    differences: Dict[str, Any] = Field(..., description="Key differences")
    recommendations: List[str] = Field(..., description="Comparison-based recommendations")
    comparison_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Comparison timestamp")


class YieldResponseOptimization(BaseModel):
    """Yield response optimization result."""
    optimization_id: UUID = Field(default_factory=uuid4, description="Optimization identifier")
    field_id: UUID = Field(..., description="Field identifier")
    crop_type: str = Field(..., description="Type of crop")
    optimization_objective: str = Field(..., description="Optimization objective")
    constraints: Dict[str, Any] = Field(..., description="Optimization constraints")
    optimal_solution: Dict[str, float] = Field(..., description="Optimal nutrient rates")
    expected_yield: float = Field(..., ge=0.0, description="Expected yield at optimal rates")
    expected_profit: float = Field(..., description="Expected profit at optimal rates")
    sensitivity_analysis: Dict[str, Any] = Field(..., description="Sensitivity analysis results")
    optimization_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Optimization timestamp")


class YieldResponseScenario(BaseModel):
    """Yield response scenario analysis."""
    scenario_id: UUID = Field(default_factory=uuid4, description="Scenario identifier")
    scenario_name: str = Field(..., description="Scenario name")
    scenario_description: str = Field(..., description="Scenario description")
    nutrient_rates: Dict[str, float] = Field(..., description="Nutrient rates for scenario")
    expected_yield: float = Field(..., ge=0.0, description="Expected yield")
    expected_profit: float = Field(..., description="Expected profit")
    risk_factors: List[str] = Field(default_factory=list, description="Risk factors")
    probability_of_success: float = Field(..., ge=0.0, le=1.0, description="Probability of success")
    scenario_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Scenario timestamp")


class YieldResponseReport(BaseModel):
    """Comprehensive yield response report."""
    report_id: UUID = Field(default_factory=uuid4, description="Report identifier")
    field_id: UUID = Field(..., description="Field identifier")
    crop_type: str = Field(..., description="Type of crop")
    analysis: YieldResponseAnalysis = Field(..., description="Main analysis")
    summary: YieldResponseSummary = Field(..., description="Analysis summary")
    scenarios: List[YieldResponseScenario] = Field(default_factory=list, description="Scenario analyses")
    recommendations: List[str] = Field(..., description="Final recommendations")
    report_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Report timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
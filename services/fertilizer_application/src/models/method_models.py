"""
Pydantic models for fertilizer application methods and optimization.
"""

from typing import List, Optional, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, validator
from decimal import Decimal


class ApplicationTiming(str, Enum):
    """Application timing options."""
    PRE_PLANT = "pre_plant"
    AT_PLANTING = "at_planting"
    POST_EMERGENCE = "post_emergence"
    SIDEDRESS = "sidedress"
    TOPDRESS = "topdress"
    FOLIAR = "foliar"
    FALL = "fall"
    SPRING = "spring"
    SUMMER = "summer"


class ApplicationPrecision(str, Enum):
    """Application precision levels."""
    BROADCAST = "broadcast"
    BAND = "band"
    PRECISION = "precision"
    VARIABLE_RATE = "variable_rate"
    SPOT_TREATMENT = "spot_treatment"


class EnvironmentalImpact(str, Enum):
    """Environmental impact levels."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class ApplicationMethod(BaseModel):
    """Detailed application method specification."""
    method_id: str = Field(..., description="Unique method identifier")
    method_name: str = Field(..., description="Method name")
    method_type: str = Field(..., description="Method type")
    description: str = Field(..., description="Method description")
    application_timing: List[ApplicationTiming] = Field(default_factory=list, description="Suitable application timings")
    precision_level: ApplicationPrecision = Field(..., description="Precision level")
    environmental_impact: EnvironmentalImpact = Field(..., description="Environmental impact level")
    equipment_requirements: List[str] = Field(default_factory=list, description="Required equipment types")
    labor_intensity: str = Field(..., description="Labor intensity (low, medium, high)")
    skill_requirements: str = Field(..., description="Required skill level")
    cost_per_acre: Optional[float] = Field(None, ge=0, description="Estimated cost per acre")
    efficiency_rating: float = Field(..., ge=0, le=1, description="Application efficiency rating")
    suitability_factors: Dict[str, Any] = Field(default_factory=dict, description="Suitability factors")


class MethodComparison(BaseModel):
    """Comparison between application methods."""
    method_a: ApplicationMethod = Field(..., description="First method for comparison")
    method_b: ApplicationMethod = Field(..., description="Second method for comparison")
    comparison_criteria: List[str] = Field(default_factory=list, description="Comparison criteria")
    method_a_scores: Dict[str, float] = Field(default_factory=dict, description="Scores for method A")
    method_b_scores: Dict[str, float] = Field(default_factory=dict, description="Scores for method B")
    winner_by_criteria: Dict[str, str] = Field(default_factory=dict, description="Winner by each criteria")
    overall_winner: Optional[str] = Field(None, description="Overall winner")
    recommendation: str = Field(..., description="Recommendation summary")


class MethodOptimization(BaseModel):
    """Method optimization parameters."""
    optimization_id: str = Field(..., description="Optimization identifier")
    target_objectives: List[str] = Field(default_factory=list, description="Optimization objectives")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Optimization constraints")
    variables: Dict[str, Any] = Field(default_factory=dict, description="Optimization variables")
    optimization_algorithm: Optional[str] = Field(None, description="Optimization algorithm used")
    convergence_criteria: Optional[Dict[str, float]] = Field(None, description="Convergence criteria")
    max_iterations: Optional[int] = Field(None, ge=1, description="Maximum iterations")
    tolerance: Optional[float] = Field(None, ge=0, description="Convergence tolerance")


class OptimizationResult(BaseModel):
    """Optimization result."""
    optimization_id: str = Field(..., description="Optimization identifier")
    optimal_method: ApplicationMethod = Field(..., description="Optimal method found")
    optimal_parameters: Dict[str, Any] = Field(default_factory=dict, description="Optimal parameters")
    objective_values: Dict[str, float] = Field(default_factory=dict, description="Objective function values")
    convergence_info: Dict[str, Any] = Field(default_factory=dict, description="Convergence information")
    sensitivity_analysis: Optional[Dict[str, Any]] = Field(None, description="Sensitivity analysis results")
    confidence_level: Optional[float] = Field(None, ge=0, le=1, description="Confidence level")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


class MethodSelection(BaseModel):
    """Method selection criteria and weights."""
    selection_id: str = Field(..., description="Selection identifier")
    criteria_weights: Dict[str, float] = Field(default_factory=dict, description="Criteria weights")
    minimum_thresholds: Dict[str, float] = Field(default_factory=dict, description="Minimum thresholds")
    maximum_thresholds: Dict[str, float] = Field(default_factory=dict, description="Maximum thresholds")
    preference_functions: Dict[str, str] = Field(default_factory=dict, description="Preference functions")
    decision_rule: str = Field(..., description="Decision rule (weighted_sum, topsis, electre)")
    normalization_method: Optional[str] = Field(None, description="Normalization method")


class MethodRanking(BaseModel):
    """Method ranking result."""
    ranking_id: str = Field(..., description="Ranking identifier")
    ranked_methods: List[ApplicationMethod] = Field(default_factory=list, description="Ranked methods")
    ranking_scores: List[float] = Field(default_factory=list, description="Ranking scores")
    ranking_criteria: List[str] = Field(default_factory=list, description="Ranking criteria")
    ranking_method: str = Field(..., description="Ranking method used")
    confidence_intervals: Optional[List[Dict[str, float]]] = Field(None, description="Confidence intervals")
    sensitivity_analysis: Optional[Dict[str, Any]] = Field(None, description="Sensitivity analysis")


class MethodValidation(BaseModel):
    """Method validation result."""
    validation_id: str = Field(..., description="Validation identifier")
    method: ApplicationMethod = Field(..., description="Method being validated")
    validation_criteria: List[str] = Field(default_factory=list, description="Validation criteria")
    validation_results: Dict[str, bool] = Field(default_factory=dict, description="Validation results")
    validation_scores: Dict[str, float] = Field(default_factory=dict, description="Validation scores")
    overall_validity: bool = Field(..., description="Overall validity")
    validation_notes: List[str] = Field(default_factory=list, description="Validation notes")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")


class MethodPerformance(BaseModel):
    """Method performance metrics."""
    method_id: str = Field(..., description="Method identifier")
    performance_date: str = Field(..., description="Performance measurement date")
    application_efficiency: float = Field(..., ge=0, le=1, description="Application efficiency")
    nutrient_use_efficiency: Optional[float] = Field(None, ge=0, le=1, description="Nutrient use efficiency")
    yield_response: Optional[float] = Field(None, description="Yield response")
    yield_unit: str = Field("bushels/acre", description="Yield unit")
    cost_effectiveness: Optional[float] = Field(None, ge=0, description="Cost effectiveness")
    environmental_score: Optional[float] = Field(None, ge=0, le=1, description="Environmental score")
    farmer_satisfaction: Optional[float] = Field(None, ge=0, le=1, description="Farmer satisfaction rating")
    overall_performance: float = Field(..., ge=0, le=1, description="Overall performance score")


class MethodLearning(BaseModel):
    """Method learning and adaptation."""
    learning_id: str = Field(..., description="Learning identifier")
    method_id: str = Field(..., description="Method identifier")
    learning_data: Dict[str, Any] = Field(default_factory=dict, description="Learning data")
    performance_history: List[MethodPerformance] = Field(default_factory=list, description="Performance history")
    adaptation_rules: List[str] = Field(default_factory=list, description="Adaptation rules")
    learning_algorithm: Optional[str] = Field(None, description="Learning algorithm")
    model_accuracy: Optional[float] = Field(None, ge=0, le=1, description="Model accuracy")
    last_updated: str = Field(..., description="Last update date")
    next_learning_cycle: Optional[str] = Field(None, description="Next learning cycle date")


class MethodRecommendation(BaseModel):
    """Comprehensive method recommendation."""
    recommendation_id: str = Field(..., description="Recommendation identifier")
    recommended_method: ApplicationMethod = Field(..., description="Recommended method")
    alternative_methods: List[ApplicationMethod] = Field(default_factory=list, description="Alternative methods")
    recommendation_reasoning: str = Field(..., description="Reasoning for recommendation")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence score")
    implementation_guidance: List[str] = Field(default_factory=list, description="Implementation guidance")
    risk_assessment: Optional[Dict[str, Any]] = Field(None, description="Risk assessment")
    success_probability: Optional[float] = Field(None, ge=0, le=1, description="Success probability")
    expected_benefits: List[str] = Field(default_factory=list, description="Expected benefits")
    potential_challenges: List[str] = Field(default_factory=list, description="Potential challenges")
    monitoring_metrics: List[str] = Field(default_factory=list, description="Monitoring metrics")
"""
Data models for fertilizer comparison and scoring service.

This module provides Pydantic models for:
- Comparison requests and responses
- Fertilizer options and scoring criteria
- Multi-criteria decision analysis (TOPSIS, AHP, Weighted Scoring)
- Trade-off analysis and recommendations
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field, validator
from decimal import Decimal


class ScoringMethod(str, Enum):
    """Scoring methods for fertilizer comparison."""
    WEIGHTED_SCORING = "weighted_scoring"
    TOPSIS = "topsis"
    AHP = "ahp"
    FUZZY_LOGIC = "fuzzy_logic"


class ComparisonCategory(str, Enum):
    """Categories for fertilizer comparison."""
    ALL = "all"
    ORGANIC = "organic"
    SYNTHETIC = "synthetic"
    SLOW_RELEASE = "slow_release"
    FAST_RELEASE = "fast_release"
    LIQUID = "liquid"
    GRANULAR = "granular"


class ScoringDimension(str, Enum):
    """Dimensions for multi-criteria scoring."""
    NUTRIENT_VALUE = "nutrient_value"
    COST_EFFECTIVENESS = "cost_effectiveness"
    ENVIRONMENTAL_IMPACT = "environmental_impact"
    APPLICATION_CONVENIENCE = "application_convenience"
    AVAILABILITY = "availability"
    SOIL_HEALTH_IMPACT = "soil_health_impact"
    RELEASE_PATTERN = "release_pattern"


class NutrientContent(BaseModel):
    """Model for fertilizer nutrient content."""
    nitrogen: float = Field(default=0.0, ge=0.0, le=100.0, description="N content percentage")
    phosphorus: float = Field(default=0.0, ge=0.0, le=100.0, description="P content percentage")
    potassium: float = Field(default=0.0, ge=0.0, le=100.0, description="K content percentage")
    calcium: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="Ca content percentage")
    magnesium: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="Mg content percentage")
    sulfur: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="S content percentage")
    micronutrients: Dict[str, float] = Field(default_factory=dict, description="Micronutrient content")

    @validator('nitrogen', 'phosphorus', 'potassium')
    def validate_total_npk(cls, v, values):
        """Validate that total NPK doesn't exceed 100%."""
        total = v + values.get('phosphorus', 0) + values.get('potassium', 0)
        if total > 100:
            raise ValueError("Total N-P-K content cannot exceed 100%")
        return v


class FertilizerOption(BaseModel):
    """Model representing a fertilizer option to compare."""
    fertilizer_id: str = Field(..., description="Unique fertilizer identifier")
    fertilizer_name: str = Field(..., description="Fertilizer product name")
    fertilizer_type: str = Field(..., description="Type of fertilizer (organic, synthetic, etc.)")
    category: ComparisonCategory = Field(..., description="Fertilizer category")

    # Nutrient content
    nutrient_content: NutrientContent = Field(..., description="Nutrient content analysis")

    # Cost information
    price_per_unit: float = Field(..., ge=0.0, description="Price per unit (ton, bag, gallon)")
    unit_type: str = Field(..., description="Unit type (ton, 50lb bag, gallon)")
    application_rate: float = Field(..., ge=0.0, description="Recommended application rate per acre")

    # Environmental characteristics
    organic_certified: bool = Field(default=False, description="Organic certification status")
    slow_release: bool = Field(default=False, description="Slow release formulation")
    greenhouse_gas_emission_factor: float = Field(default=1.0, ge=0.0, description="GHG emission factor")
    runoff_potential: float = Field(default=0.5, ge=0.0, le=1.0, description="Runoff potential (0-1)")
    leaching_potential: float = Field(default=0.5, ge=0.0, le=1.0, description="Leaching potential (0-1)")

    # Application characteristics
    application_method: str = Field(..., description="Application method (broadcast, injection, etc.)")
    equipment_required: List[str] = Field(default_factory=list, description="Required equipment")
    application_complexity: float = Field(default=0.5, ge=0.0, le=1.0, description="Application complexity (0-1)")
    storage_requirements: str = Field(default="standard", description="Storage requirements")

    # Availability and soil health
    regional_availability: float = Field(default=0.8, ge=0.0, le=1.0, description="Regional availability (0-1)")
    soil_health_benefit: float = Field(default=0.5, ge=0.0, le=1.0, description="Soil health benefit (0-1)")

    # Additional metadata
    manufacturer: Optional[str] = Field(None, description="Manufacturer name")
    product_url: Optional[str] = Field(None, description="Product information URL")
    notes: Optional[str] = Field(None, description="Additional notes")


class ScoringCriteria(BaseModel):
    """Model for scoring criteria and weights."""
    dimension: ScoringDimension = Field(..., description="Scoring dimension")
    weight: float = Field(..., ge=0.0, le=1.0, description="Weight for this criterion (0-1)")
    maximize: bool = Field(default=True, description="Whether to maximize this criterion")
    threshold: Optional[float] = Field(None, description="Minimum acceptable value")
    preference_function: str = Field(default="linear", description="Preference function type")

    @validator('preference_function')
    def validate_preference_function(cls, v):
        """Validate preference function."""
        valid_functions = ["linear", "v_shape", "u_shape", "level", "gaussian"]
        if v not in valid_functions:
            raise ValueError(f"Invalid preference function: {v}. Must be one of {valid_functions}")
        return v


class ComparisonRequest(BaseModel):
    """Request model for fertilizer comparison."""
    comparison_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique comparison identifier")
    field_id: Optional[UUID] = Field(None, description="Field identifier for context")
    user_id: Optional[UUID] = Field(None, description="User identifier")

    # Fertilizers to compare
    fertilizers: List[FertilizerOption] = Field(..., description="List of fertilizers to compare")

    # Scoring configuration
    scoring_method: ScoringMethod = Field(default=ScoringMethod.WEIGHTED_SCORING, description="Scoring method")
    scoring_criteria: List[ScoringCriteria] = Field(..., description="Scoring criteria and weights")

    # Context and constraints
    crop_type: Optional[str] = Field(None, description="Crop type for context")
    field_size_acres: Optional[float] = Field(None, ge=0.0, description="Field size in acres")
    budget_constraint: Optional[float] = Field(None, ge=0.0, description="Budget constraint per acre")
    environmental_priority: float = Field(default=0.5, ge=0.0, le=1.0, description="Environmental priority (0-1)")

    # Comparison options
    include_trade_off_analysis: bool = Field(default=True, description="Include trade-off analysis")
    include_sensitivity_analysis: bool = Field(default=False, description="Include sensitivity analysis")
    normalize_scores: bool = Field(default=True, description="Normalize scores to 0-100 scale")

    @validator('fertilizers')
    def validate_fertilizers(cls, v):
        """Validate fertilizer list."""
        if len(v) < 2:
            raise ValueError("At least 2 fertilizers are required for comparison")
        if len(v) > 10:
            raise ValueError("Maximum 10 fertilizers can be compared at once")
        return v

    @validator('scoring_criteria')
    def validate_scoring_criteria(cls, v):
        """Validate scoring criteria weights sum to 1.0."""
        if not v:
            raise ValueError("At least one scoring criterion is required")
        total_weight = sum(criterion.weight for criterion in v)
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"Scoring criteria weights must sum to 1.0, got {total_weight}")
        return v


class DimensionScore(BaseModel):
    """Model for individual dimension score."""
    dimension: ScoringDimension = Field(..., description="Scoring dimension")
    raw_score: float = Field(..., description="Raw score value")
    normalized_score: float = Field(..., ge=0.0, le=100.0, description="Normalized score (0-100)")
    weight: float = Field(..., ge=0.0, le=1.0, description="Weight for this dimension")
    weighted_score: float = Field(..., description="Weighted score")
    explanation: str = Field(..., description="Score explanation")


class FertilizerScore(BaseModel):
    """Model for fertilizer scoring results."""
    fertilizer_id: str = Field(..., description="Fertilizer identifier")
    fertilizer_name: str = Field(..., description="Fertilizer name")

    # Overall scores
    total_score: float = Field(..., description="Total weighted score")
    normalized_total_score: float = Field(..., ge=0.0, le=100.0, description="Normalized total score (0-100)")
    rank: int = Field(..., ge=1, description="Ranking (1=best)")

    # Dimension scores
    dimension_scores: List[DimensionScore] = Field(..., description="Scores by dimension")

    # Strengths and weaknesses
    strengths: List[str] = Field(default_factory=list, description="Key strengths")
    weaknesses: List[str] = Field(default_factory=list, description="Key weaknesses")

    # Cost analysis
    cost_per_acre: float = Field(..., ge=0.0, description="Cost per acre")
    cost_per_unit_nitrogen: Optional[float] = Field(None, description="Cost per lb of N")
    cost_per_unit_phosphorus: Optional[float] = Field(None, description="Cost per lb of P")
    cost_per_unit_potassium: Optional[float] = Field(None, description="Cost per lb of K")


class TOPSISScore(BaseModel):
    """Model for TOPSIS method scores."""
    fertilizer_id: str = Field(..., description="Fertilizer identifier")
    fertilizer_name: str = Field(..., description="Fertilizer name")

    # TOPSIS specific scores
    positive_ideal_distance: float = Field(..., ge=0.0, description="Distance from positive ideal solution")
    negative_ideal_distance: float = Field(..., ge=0.0, description="Distance from negative ideal solution")
    relative_closeness: float = Field(..., ge=0.0, le=1.0, description="Relative closeness coefficient")
    rank: int = Field(..., ge=1, description="Ranking (1=best)")

    # Dimension contributions
    dimension_contributions: Dict[str, float] = Field(..., description="Contribution by dimension")


class AHPScore(BaseModel):
    """Model for AHP method scores."""
    fertilizer_id: str = Field(..., description="Fertilizer identifier")
    fertilizer_name: str = Field(..., description="Fertilizer name")

    # AHP specific scores
    priority_vector: float = Field(..., ge=0.0, le=1.0, description="Priority vector value")
    consistency_ratio: float = Field(..., ge=0.0, description="Consistency ratio")
    rank: int = Field(..., ge=1, description="Ranking (1=best)")

    # Pairwise comparison results
    pairwise_scores: Dict[str, float] = Field(..., description="Pairwise comparison scores")


class TradeOffAnalysis(BaseModel):
    """Model for trade-off analysis between fertilizers."""
    fertilizer_1_id: str = Field(..., description="First fertilizer ID")
    fertilizer_2_id: str = Field(..., description="Second fertilizer ID")
    fertilizer_1_name: str = Field(..., description="First fertilizer name")
    fertilizer_2_name: str = Field(..., description="Second fertilizer name")

    # Trade-offs
    cost_difference: float = Field(..., description="Cost difference per acre")
    nutrient_value_difference: float = Field(..., description="Nutrient value difference")
    environmental_difference: float = Field(..., description="Environmental impact difference")
    convenience_difference: float = Field(..., description="Application convenience difference")

    # Summary
    trade_off_summary: str = Field(..., description="Trade-off summary")
    recommendation: str = Field(..., description="Recommendation based on trade-offs")


class ComparisonMatrix(BaseModel):
    """Model for comparison matrix visualization."""
    fertilizer_ids: List[str] = Field(..., description="List of fertilizer IDs")
    fertilizer_names: List[str] = Field(..., description="List of fertilizer names")
    dimensions: List[str] = Field(..., description="List of dimensions")

    # Matrix data (rows=fertilizers, columns=dimensions)
    score_matrix: List[List[float]] = Field(..., description="Score matrix")
    normalized_matrix: List[List[float]] = Field(..., description="Normalized score matrix")

    # Summary statistics
    dimension_averages: List[float] = Field(..., description="Average scores by dimension")
    dimension_std_devs: List[float] = Field(..., description="Standard deviations by dimension")


class SensitivityAnalysis(BaseModel):
    """Model for sensitivity analysis results."""
    base_case_ranking: List[str] = Field(..., description="Base case fertilizer ranking")

    # Weight sensitivity
    weight_sensitivity: Dict[str, List[Dict[str, Any]]] = Field(
        default_factory=dict,
        description="Ranking changes with weight variations"
    )

    # Threshold analysis
    threshold_changes: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Critical threshold values"
    )

    # Robustness score
    ranking_stability: float = Field(..., ge=0.0, le=1.0, description="Ranking stability score")


class ComparisonResult(BaseModel):
    """Main result model for fertilizer comparison."""
    comparison_id: str = Field(..., description="Unique comparison identifier")
    field_id: Optional[UUID] = Field(None, description="Field identifier")
    user_id: Optional[UUID] = Field(None, description="User identifier")

    # Scoring method used
    scoring_method: ScoringMethod = Field(..., description="Scoring method used")

    # Results
    fertilizer_scores: List[FertilizerScore] = Field(..., description="Fertilizer scores and rankings")
    comparison_matrix: ComparisonMatrix = Field(..., description="Comparison matrix")

    # Trade-off analysis
    trade_off_analyses: List[TradeOffAnalysis] = Field(
        default_factory=list,
        description="Trade-off analyses"
    )

    # Recommendations
    top_recommendation: str = Field(..., description="Top fertilizer recommendation")
    recommendation_explanation: str = Field(..., description="Explanation for recommendation")
    alternative_recommendations: List[str] = Field(
        default_factory=list,
        description="Alternative recommendations"
    )

    # Context-specific insights
    cost_efficiency_insights: List[str] = Field(default_factory=list, description="Cost efficiency insights")
    environmental_insights: List[str] = Field(default_factory=list, description="Environmental insights")
    application_insights: List[str] = Field(default_factory=list, description="Application insights")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Comparison timestamp")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    model_version: str = Field(default="1.0", description="Model version")


class TOPSISResult(BaseModel):
    """Specific result model for TOPSIS method."""
    comparison_id: str = Field(..., description="Unique comparison identifier")

    # TOPSIS scores
    topsis_scores: List[TOPSISScore] = Field(..., description="TOPSIS method scores")

    # Ideal solutions
    positive_ideal_solution: Dict[str, float] = Field(..., description="Positive ideal solution")
    negative_ideal_solution: Dict[str, float] = Field(..., description="Negative ideal solution")

    # Additional analysis
    decision_matrix: List[List[float]] = Field(..., description="Decision matrix")
    weighted_normalized_matrix: List[List[float]] = Field(..., description="Weighted normalized matrix")

    # Recommendation
    top_recommendation: str = Field(..., description="Top fertilizer by TOPSIS")
    recommendation_confidence: float = Field(..., ge=0.0, le=1.0, description="Recommendation confidence")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


class AHPResult(BaseModel):
    """Specific result model for AHP method."""
    comparison_id: str = Field(..., description="Unique comparison identifier")

    # AHP scores
    ahp_scores: List[AHPScore] = Field(..., description="AHP method scores")

    # Pairwise comparison matrices
    pairwise_matrices: Dict[str, List[List[float]]] = Field(..., description="Pairwise comparison matrices")

    # Consistency analysis
    overall_consistency_ratio: float = Field(..., ge=0.0, description="Overall consistency ratio")
    consistency_acceptable: bool = Field(..., description="Whether consistency is acceptable (<0.1)")

    # Recommendation
    top_recommendation: str = Field(..., description="Top fertilizer by AHP")
    recommendation_confidence: float = Field(..., ge=0.0, le=1.0, description="Recommendation confidence")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


class AvailableCriteria(BaseModel):
    """Model for available scoring criteria information."""
    dimension: ScoringDimension = Field(..., description="Scoring dimension")
    display_name: str = Field(..., description="Display name for dimension")
    description: str = Field(..., description="Dimension description")
    default_weight: float = Field(..., ge=0.0, le=1.0, description="Default weight")
    maximize: bool = Field(..., description="Whether to maximize this criterion")
    measurement_unit: Optional[str] = Field(None, description="Unit of measurement")
    typical_range: Optional[str] = Field(None, description="Typical value range")
    factors_considered: List[str] = Field(default_factory=list, description="Factors considered in scoring")

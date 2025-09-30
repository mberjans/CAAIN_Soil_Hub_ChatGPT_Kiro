"""
Data models for multi-nutrient optimization API.

This module provides Pydantic models for:
- API request and response models
- Nutrient optimization data structures
- Alternative strategy models
- Interaction analysis models
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, date
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field, validator


class OptimizationObjective(str, Enum):
    """Optimization objectives for API requests."""
    MAXIMIZE_PROFIT = "maximize_profit"
    MINIMIZE_COST = "minimize_cost"
    MAXIMIZE_YIELD = "maximize_yield"
    BALANCED = "balanced"


class InteractionModel(str, Enum):
    """Interaction models for optimization."""
    RESPONSE_SURFACE = "response_surface"
    MACHINE_LEARNING = "machine_learning"
    LINEAR = "linear"


class SoilTestModel(BaseModel):
    """Soil test data model for API requests."""
    nutrient: str = Field(..., description="Nutrient type")
    test_value: float = Field(..., ge=0.0, description="Soil test value")
    test_unit: str = Field(..., description="Unit of measurement")
    test_method: str = Field(..., description="Testing method used")
    test_date: date = Field(..., description="Date of soil test")
    confidence_level: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence in test result")
    
    @validator('nutrient')
    def validate_nutrient(cls, v):
        valid_nutrients = [
            "nitrogen", "phosphorus", "potassium", "calcium", "magnesium",
            "sulfur", "zinc", "iron", "manganese", "copper", "boron", "molybdenum"
        ]
        if v.lower() not in valid_nutrients:
            raise ValueError(f"Invalid nutrient type: {v}")
        return v.lower()


class CropRequirementModel(BaseModel):
    """Crop nutrient requirement model for API requests."""
    nutrient: str = Field(..., description="Nutrient type")
    minimum_requirement: float = Field(..., ge=0.0, description="Minimum nutrient requirement")
    optimal_range_min: float = Field(..., ge=0.0, description="Minimum of optimal range")
    optimal_range_max: float = Field(..., ge=0.0, description="Maximum of optimal range")
    maximum_tolerance: float = Field(..., ge=0.0, description="Maximum nutrient tolerance")
    uptake_efficiency: float = Field(default=0.7, ge=0.0, le=1.0, description="Nutrient uptake efficiency")
    critical_stage: Optional[str] = Field(None, description="Critical growth stage for nutrient")
    
    @validator('nutrient')
    def validate_nutrient(cls, v):
        valid_nutrients = [
            "nitrogen", "phosphorus", "potassium", "calcium", "magnesium",
            "sulfur", "zinc", "iron", "manganese", "copper", "boron", "molybdenum"
        ]
        if v.lower() not in valid_nutrients:
            raise ValueError(f"Invalid nutrient type: {v}")
        return v.lower()
    
    @validator('optimal_range_max')
    def validate_optimal_range(cls, v, values):
        if 'optimal_range_min' in values and v < values['optimal_range_min']:
            raise ValueError('optimal_range_max must be greater than optimal_range_min')
        return v


class EnvironmentalLimitModel(BaseModel):
    """Environmental limit model for API requests."""
    nutrient: str = Field(..., description="Nutrient type")
    max_application_rate: float = Field(..., ge=0.0, description="Maximum application rate")
    application_unit: str = Field(..., description="Unit for application rate")
    environmental_risk: str = Field(..., description="Environmental risk level")
    regulatory_limit: Optional[float] = Field(None, ge=0.0, description="Regulatory application limit")
    seasonal_limit: Optional[float] = Field(None, ge=0.0, description="Seasonal application limit")
    
    @validator('nutrient')
    def validate_nutrient(cls, v):
        valid_nutrients = [
            "nitrogen", "phosphorus", "potassium", "calcium", "magnesium",
            "sulfur", "zinc", "iron", "manganese", "copper", "boron", "molybdenum"
        ]
        if v.lower() not in valid_nutrients:
            raise ValueError(f"Invalid nutrient type: {v}")
        return v.lower()


class OptimizationRequestModel(BaseModel):
    """Request model for multi-nutrient optimization."""
    field_id: UUID = Field(..., description="Field identifier")
    crop_type: str = Field(..., description="Type of crop")
    target_yield: float = Field(..., ge=0.0, description="Target yield per acre")
    yield_unit: str = Field(default="bushels", description="Unit for yield")
    
    # Soil test data
    soil_tests: List[SoilTestModel] = Field(..., description="Soil test results")
    
    # Crop requirements
    crop_requirements: List[CropRequirementModel] = Field(..., description="Crop nutrient requirements")
    
    # Environmental limits
    environmental_limits: List[EnvironmentalLimitModel] = Field(default_factory=list, description="Environmental limits")
    
    # Optimization parameters
    optimization_objective: OptimizationObjective = Field(default=OptimizationObjective.BALANCED, description="Optimization objective")
    budget_constraint: Optional[float] = Field(None, ge=0.0, description="Budget constraint in dollars per acre")
    risk_tolerance: float = Field(default=0.5, ge=0.0, le=1.0, description="Risk tolerance level")
    
    # Additional parameters
    field_size_acres: float = Field(..., ge=0.0, description="Field size in acres")
    soil_type: str = Field(..., description="Soil type classification")
    ph_level: float = Field(..., ge=0.0, le=14.0, description="Soil pH level")
    organic_matter_percent: float = Field(default=2.0, ge=0.0, le=20.0, description="Organic matter percentage")
    
    # Interaction modeling
    include_interactions: bool = Field(default=True, description="Include nutrient interactions")
    interaction_model: InteractionModel = Field(default=InteractionModel.RESPONSE_SURFACE, description="Interaction model type")
    
    @validator('soil_tests')
    def validate_soil_tests(cls, v):
        if not v:
            raise ValueError("At least one soil test is required")
        return v
    
    @validator('crop_requirements')
    def validate_crop_requirements(cls, v):
        if not v:
            raise ValueError("At least one crop requirement is required")
        return v


class AlternativeStrategyModel(BaseModel):
    """Alternative strategy model for optimization results."""
    strategy: str = Field(..., description="Strategy name")
    description: str = Field(..., description="Strategy description")
    rates: Dict[str, float] = Field(..., description="Nutrient application rates")
    expected_yield: float = Field(..., ge=0.0, description="Expected yield")
    cost: float = Field(..., ge=0.0, description="Total cost")


class OptimizationResponseModel(BaseModel):
    """Response model for multi-nutrient optimization."""
    optimization_id: str = Field(..., description="Unique optimization identifier")
    field_id: UUID = Field(..., description="Field identifier")
    crop_type: str = Field(..., description="Crop type")
    
    # Optimization results
    optimal_nutrient_rates: Dict[str, float] = Field(..., description="Optimal nutrient application rates")
    expected_yield: float = Field(..., description="Expected yield with optimal rates")
    yield_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in yield prediction")
    
    # Economic analysis
    total_cost: float = Field(..., description="Total fertilizer cost per acre")
    expected_revenue: float = Field(..., description="Expected revenue per acre")
    net_profit: float = Field(..., description="Net profit per acre")
    roi_percentage: float = Field(..., description="Return on investment percentage")
    
    # Optimization details
    optimization_method: str = Field(..., description="Optimization method used")
    convergence_status: str = Field(..., description="Optimization convergence status")
    iterations_required: int = Field(..., description="Number of iterations required")
    optimization_time_seconds: float = Field(..., description="Time taken for optimization")
    
    # Interaction analysis
    nutrient_interactions: List[Dict[str, Any]] = Field(default_factory=list, description="Detected interactions")
    interaction_effects: Dict[str, float] = Field(default_factory=dict, description="Quantified interaction effects")
    
    # Risk assessment
    risk_factors: List[str] = Field(default_factory=list, description="Identified risk factors")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Overall risk score")
    
    # Recommendations
    recommendations: List[str] = Field(default_factory=list, description="Optimization recommendations")
    alternative_strategies: List[AlternativeStrategyModel] = Field(default_factory=list, description="Alternative strategies")
    
    # Metadata
    created_at: datetime = Field(..., description="Optimization timestamp")
    model_version: str = Field(..., description="Model version used")


class InteractionAnalysisModel(BaseModel):
    """Model for nutrient interaction analysis."""
    crop_type: str = Field(..., description="Crop type")
    soil_ph: float = Field(..., ge=0.0, le=14.0, description="Soil pH level")
    soil_type: str = Field(..., description="Soil type classification")
    relevant_interactions: List[Dict[str, Any]] = Field(..., description="Relevant nutrient interactions")
    recommendations: List[str] = Field(..., description="Recommendations based on interactions")
    analysis_timestamp: datetime = Field(..., description="Analysis timestamp")


class OptimizationComparisonModel(BaseModel):
    """Model for comparing optimization strategies."""
    strategy_name: str = Field(..., description="Strategy name")
    nutrient_rates: Dict[str, float] = Field(..., description="Nutrient application rates")
    expected_yield: float = Field(..., ge=0.0, description="Expected yield")
    total_cost: float = Field(..., ge=0.0, description="Total cost")
    net_profit: float = Field(..., description="Net profit")
    roi_percentage: float = Field(..., description="ROI percentage")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Risk score")
    advantages: List[str] = Field(..., description="Strategy advantages")
    disadvantages: List[str] = Field(..., description="Strategy disadvantages")


class OptimizationSummaryModel(BaseModel):
    """Summary model for optimization results."""
    field_id: UUID = Field(..., description="Field identifier")
    crop_type: str = Field(..., description="Crop type")
    optimization_count: int = Field(..., description="Number of optimizations performed")
    best_strategy: str = Field(..., description="Best performing strategy")
    average_yield: float = Field(..., description="Average expected yield")
    average_cost: float = Field(..., description="Average cost")
    average_roi: float = Field(..., description="Average ROI")
    last_optimization: datetime = Field(..., description="Last optimization timestamp")
    recommendations: List[str] = Field(..., description="Summary recommendations")
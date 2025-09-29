"""
Crop Diversification and Risk Management Data Models

Pydantic models for crop diversification planning, risk assessment,
and portfolio optimization for drought resilience.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union, Tuple
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal
from enum import Enum

# Enums for type safety
class RiskLevel(str, Enum):
    """Risk levels for diversification strategies."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"

class DiversificationStrategy(str, Enum):
    """Types of diversification strategies."""
    CROP_ROTATION = "crop_rotation"
    INTERCROPPING = "intercropping"
    AGROFORESTRY = "agroforestry"
    TEMPORAL_DIVERSIFICATION = "temporal_diversification"
    SPATIAL_DIVERSIFICATION = "spatial_diversification"
    MARKET_DIVERSIFICATION = "market_diversification"

class CropCategory(str, Enum):
    """Crop categories for diversification analysis."""
    GRAINS = "grains"
    LEGUMES = "legumes"
    OILSEEDS = "oilseeds"
    FORAGE = "forage"
    VEGETABLES = "vegetables"
    FRUITS = "fruits"
    SPECIALTY = "specialty"
    COVER_CROPS = "cover_crops"

class MarketRiskType(str, Enum):
    """Types of market risks."""
    PRICE_VOLATILITY = "price_volatility"
    DEMAND_FLUCTUATION = "demand_fluctuation"
    SUPPLY_CHAIN_DISRUPTION = "supply_chain_disruption"
    WEATHER_IMPACT = "weather_impact"
    POLICY_CHANGES = "policy_changes"

class DroughtToleranceLevel(str, Enum):
    """Drought tolerance levels."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"

class CropRiskProfile(BaseModel):
    """Risk profile for individual crops."""
    crop_id: UUID = Field(..., description="Unique crop identifier")
    crop_name: str = Field(..., description="Name of the crop")
    crop_category: CropCategory = Field(..., description="Category of the crop")
    drought_tolerance: DroughtToleranceLevel = Field(..., description="Drought tolerance level")
    water_requirement_mm: float = Field(..., ge=0, description="Water requirement in mm per season")
    yield_stability_score: float = Field(..., ge=0, le=1, description="Yield stability score (0-1)")
    market_price_volatility: float = Field(..., ge=0, le=1, description="Market price volatility (0-1)")
    disease_susceptibility: float = Field(..., ge=0, le=1, description="Disease susceptibility score (0-1)")
    pest_susceptibility: float = Field(..., ge=0, le=1, description="Pest susceptibility score (0-1)")
    soil_health_contribution: float = Field(..., ge=0, le=1, description="Soil health contribution score (0-1)")
    nitrogen_fixation: bool = Field(default=False, description="Whether crop fixes nitrogen")
    root_depth_cm: float = Field(..., ge=0, description="Average root depth in cm")
    maturity_days: int = Field(..., ge=1, description="Days to maturity")
    
    @field_validator('yield_stability_score', 'market_price_volatility', 'disease_susceptibility', 'pest_susceptibility', 'soil_health_contribution')
    @classmethod
    def validate_score(cls, v):
        if v < 0 or v > 1:
            raise ValueError('Score must be between 0 and 1')
        return v

class DiversificationPortfolio(BaseModel):
    """Crop diversification portfolio."""
    portfolio_id: UUID = Field(..., description="Unique portfolio identifier")
    farm_id: UUID = Field(..., description="Farm identifier")
    portfolio_name: str = Field(..., description="Name of the portfolio")
    crops: List[CropRiskProfile] = Field(..., description="Crops in the portfolio")
    total_acres: float = Field(..., ge=0, description="Total acres in portfolio")
    crop_allocation: Dict[str, float] = Field(..., description="Allocation percentage per crop")
    diversification_index: float = Field(..., ge=0, le=1, description="Diversification index (0-1)")
    risk_score: float = Field(..., ge=0, le=1, description="Overall risk score (0-1)")
    expected_yield: float = Field(..., ge=0, description="Expected yield per acre")
    expected_revenue: Decimal = Field(..., ge=0, description="Expected revenue per acre")
    water_efficiency_score: float = Field(..., ge=0, le=1, description="Water efficiency score")
    soil_health_score: float = Field(..., ge=0, le=1, description="Soil health improvement score")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('crop_allocation')
    @classmethod
    def validate_allocation(cls, v):
        total_allocation = sum(v.values())
        if abs(total_allocation - 100.0) > 0.01:  # Allow small floating point errors
            raise ValueError('Crop allocation percentages must sum to 100%')
        return v

class MarketRiskAssessment(BaseModel):
    """Market risk assessment for crops."""
    crop_id: UUID = Field(..., description="Crop identifier")
    risk_types: List[MarketRiskType] = Field(..., description="Types of market risks")
    price_volatility_score: float = Field(..., ge=0, le=1, description="Price volatility score")
    demand_stability_score: float = Field(..., ge=0, le=1, description="Demand stability score")
    supply_chain_risk_score: float = Field(..., ge=0, le=1, description="Supply chain risk score")
    weather_sensitivity_score: float = Field(..., ge=0, le=1, description="Weather sensitivity score")
    policy_risk_score: float = Field(..., ge=0, le=1, description="Policy risk score")
    overall_market_risk: float = Field(..., ge=0, le=1, description="Overall market risk score")
    risk_mitigation_strategies: List[str] = Field(default_factory=list, description="Risk mitigation strategies")
    
    @field_validator('price_volatility_score', 'demand_stability_score', 'supply_chain_risk_score', 'weather_sensitivity_score', 'policy_risk_score', 'overall_market_risk')
    @classmethod
    def validate_risk_score(cls, v):
        if v < 0 or v > 1:
            raise ValueError('Risk score must be between 0 and 1')
        return v

class DiversificationRecommendation(BaseModel):
    """Diversification recommendation."""
    recommendation_id: UUID = Field(..., description="Unique recommendation identifier")
    farm_id: UUID = Field(..., description="Farm identifier")
    strategy_type: DiversificationStrategy = Field(..., description="Type of diversification strategy")
    recommended_portfolio: DiversificationPortfolio = Field(..., description="Recommended crop portfolio")
    risk_reduction_percent: float = Field(..., ge=0, le=100, description="Risk reduction percentage")
    yield_stability_improvement: float = Field(..., ge=0, le=100, description="Yield stability improvement percentage")
    water_savings_percent: float = Field(..., ge=0, le=100, description="Water savings percentage")
    soil_health_improvement: float = Field(..., ge=0, le=100, description="Soil health improvement percentage")
    implementation_cost: Decimal = Field(..., ge=0, description="Implementation cost per acre")
    expected_roi_percent: float = Field(..., description="Expected ROI percentage")
    payback_period_years: float = Field(..., ge=0, description="Payback period in years")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in recommendation")
    implementation_timeline: str = Field(..., description="Implementation timeline")
    monitoring_recommendations: List[str] = Field(default_factory=list, description="Monitoring recommendations")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('risk_reduction_percent', 'yield_stability_improvement', 'water_savings_percent', 'soil_health_improvement')
    @classmethod
    def validate_percentage(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Percentage must be between 0 and 100')
        return v

class DiversificationRequest(BaseModel):
    """Request for diversification analysis."""
    farm_id: UUID = Field(..., description="Farm identifier")
    field_ids: List[UUID] = Field(..., description="Field identifiers")
    total_acres: float = Field(..., ge=0, description="Total acres to diversify")
    current_crops: List[str] = Field(default_factory=list, description="Current crops grown")
    risk_tolerance: RiskLevel = Field(..., description="Farmer's risk tolerance")
    diversification_goals: List[str] = Field(..., description="Diversification goals")
    budget_constraints: Optional[Decimal] = Field(None, description="Budget constraints")
    equipment_available: List[str] = Field(default_factory=list, description="Available equipment")
    irrigation_capacity: Optional[float] = Field(None, description="Irrigation capacity in mm")
    soil_types: List[str] = Field(default_factory=list, description="Soil types on farm")
    climate_zone: Optional[str] = Field(None, description="Climate zone")
    market_preferences: List[str] = Field(default_factory=list, description="Market preferences")
    sustainability_goals: List[str] = Field(default_factory=list, description="Sustainability goals")
    
    @field_validator('total_acres')
    @classmethod
    def validate_acres(cls, v):
        if v <= 0:
            raise ValueError('Total acres must be greater than 0')
        return v

class DiversificationResponse(BaseModel):
    """Response for diversification analysis."""
    request_id: UUID = Field(..., description="Request identifier")
    farm_id: UUID = Field(..., description="Farm identifier")
    analysis_date: datetime = Field(default_factory=datetime.utcnow)
    current_risk_assessment: Dict[str, Any] = Field(..., description="Current risk assessment")
    diversification_recommendations: List[DiversificationRecommendation] = Field(..., description="Diversification recommendations")
    risk_comparison: Dict[str, float] = Field(..., description="Risk comparison metrics")
    economic_analysis: Dict[str, Any] = Field(..., description="Economic analysis")
    implementation_priority: List[str] = Field(..., description="Implementation priority order")
    monitoring_plan: Dict[str, Any] = Field(..., description="Monitoring plan")
    next_review_date: date = Field(..., description="Next review date")
    confidence_score: float = Field(..., ge=0, le=1, description="Overall confidence score")

class CropCompatibilityMatrix(BaseModel):
    """Crop compatibility matrix for diversification."""
    crop_pairs: Dict[Tuple[str, str], float] = Field(..., description="Compatibility scores for crop pairs")
    rotation_benefits: Dict[str, Dict[str, float]] = Field(..., description="Rotation benefits between crops")
    intercropping_potential: Dict[Tuple[str, str], float] = Field(..., description="Intercropping potential scores")
    soil_health_benefits: Dict[str, float] = Field(..., description="Soil health benefits per crop")
    pest_disease_interactions: Dict[Tuple[str, str], str] = Field(..., description="Pest/disease interactions")
    
    @field_validator('crop_pairs', 'rotation_benefits', 'intercropping_potential', 'soil_health_benefits')
    @classmethod
    def validate_scores(cls, v):
        for key, value in v.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, (int, float)) and (sub_value < 0 or sub_value > 1):
                        raise ValueError('Compatibility scores must be between 0 and 1')
            elif isinstance(value, (int, float)) and (value < 0 or value > 1):
                raise ValueError('Compatibility scores must be between 0 and 1')
        return v

class RiskMitigationStrategy(BaseModel):
    """Risk mitigation strategy."""
    strategy_id: UUID = Field(..., description="Unique strategy identifier")
    strategy_name: str = Field(..., description="Name of the strategy")
    strategy_type: str = Field(..., description="Type of strategy")
    description: str = Field(..., description="Description of the strategy")
    risk_types_mitigated: List[str] = Field(..., description="Types of risks mitigated")
    implementation_cost: Decimal = Field(..., ge=0, description="Implementation cost")
    effectiveness_score: float = Field(..., ge=0, le=1, description="Effectiveness score")
    implementation_timeline: str = Field(..., description="Implementation timeline")
    maintenance_requirements: List[str] = Field(default_factory=list, description="Maintenance requirements")
    expected_benefits: List[str] = Field(..., description="Expected benefits")
    
    @field_validator('effectiveness_score')
    @classmethod
    def validate_effectiveness(cls, v):
        if v < 0 or v > 1:
            raise ValueError('Effectiveness score must be between 0 and 1')
        return v
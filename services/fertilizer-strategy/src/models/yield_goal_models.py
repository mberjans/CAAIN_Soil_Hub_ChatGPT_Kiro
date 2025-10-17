"""
Data models for comprehensive yield goal management.

This module provides data models for yield goal setting including:
- Historical yield analysis
- Potential yield assessment
- Goal feasibility analysis
- Risk assessment for yield goals
- Integration with soil, weather, and management data
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, date
from enum import Enum
from pydantic import BaseModel, Field, validator
from uuid import UUID


class YieldGoalType(str, Enum):
    """Types of yield goals."""
    CONSERVATIVE = "conservative"
    REALISTIC = "realistic"
    OPTIMISTIC = "optimistic"
    STRETCH = "stretch"


class YieldTrendDirection(str, Enum):
    """Direction of yield trends."""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"


class YieldRiskLevel(str, Enum):
    """Risk levels for yield goals."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SoilCharacteristic(BaseModel):
    """Soil characteristics affecting yield potential."""
    soil_type: str = Field(..., description="Soil type classification")
    ph_level: float = Field(..., ge=0.0, le=14.0, description="Soil pH level")
    organic_matter_percent: float = Field(..., ge=0.0, le=20.0, description="Organic matter percentage")
    cation_exchange_capacity: float = Field(..., ge=0.0, description="CEC in meq/100g")
    drainage_class: str = Field(..., description="Soil drainage classification")
    slope_percent: float = Field(..., ge=0.0, le=100.0, description="Field slope percentage")
    water_holding_capacity: float = Field(..., ge=0.0, description="Water holding capacity")


class WeatherPattern(BaseModel):
    """Weather patterns affecting yield potential."""
    growing_season_precipitation: float = Field(..., description="Growing season precipitation (inches)")
    growing_degree_days: float = Field(..., description="Growing degree days")
    drought_stress_days: int = Field(..., ge=0, description="Days of drought stress")
    heat_stress_days: int = Field(..., ge=0, description="Days of heat stress")
    frost_risk_days: int = Field(..., ge=0, description="Days with frost risk")
    optimal_growing_days: int = Field(..., ge=0, description="Optimal growing days")


class ManagementPractice(BaseModel):
    """Management practices affecting yield potential."""
    tillage_system: str = Field(..., description="Tillage system used")
    irrigation_available: bool = Field(default=False, description="Irrigation availability")
    precision_agriculture: bool = Field(default=False, description="Precision agriculture adoption")
    cover_crop_usage: bool = Field(default=False, description="Cover crop usage")
    crop_rotation: str = Field(..., description="Crop rotation system")
    planting_date: Optional[date] = Field(None, description="Planting date")
    harvest_date: Optional[date] = Field(None, description="Harvest date")


class HistoricalYieldData(BaseModel):
    """Historical yield data for analysis."""
    year: int = Field(..., ge=1900, le=2030, description="Year of yield data")
    yield_per_acre: float = Field(..., ge=0.0, description="Yield per acre")
    crop_type: str = Field(..., description="Type of crop")
    variety: Optional[str] = Field(None, description="Crop variety")
    soil_conditions: Optional[SoilCharacteristic] = Field(None, description="Soil conditions")
    weather_conditions: Optional[WeatherPattern] = Field(None, description="Weather conditions")
    management_practices: Optional[ManagementPractice] = Field(None, description="Management practices")
    notes: Optional[str] = Field(None, description="Additional notes")


class YieldTrendAnalysis(BaseModel):
    """Analysis of yield trends over time."""
    trend_direction: YieldTrendDirection = Field(..., description="Overall trend direction")
    trend_slope: float = Field(..., description="Slope of yield trend (bu/acre/year)")
    r_squared: float = Field(..., ge=0.0, le=1.0, description="R-squared value of trend")
    volatility: float = Field(..., ge=0.0, description="Yield volatility (standard deviation)")
    average_yield: float = Field(..., ge=0.0, description="Average yield over period")
    min_yield: float = Field(..., ge=0.0, description="Minimum yield in period")
    max_yield: float = Field(..., ge=0.0, description="Maximum yield in period")
    trend_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in trend analysis")


class PotentialYieldAssessment(BaseModel):
    """Assessment of potential yield based on various factors."""
    soil_potential: float = Field(..., ge=0.0, description="Soil-based yield potential")
    weather_potential: float = Field(..., ge=0.0, description="Weather-based yield potential")
    management_potential: float = Field(..., ge=0.0, description="Management-based yield potential")
    variety_potential: float = Field(..., ge=0.0, description="Variety-based yield potential")
    combined_potential: float = Field(..., ge=0.0, description="Combined yield potential")
    limiting_factors: List[str] = Field(default_factory=list, description="Factors limiting yield")
    improvement_opportunities: List[str] = Field(default_factory=list, description="Opportunities for improvement")


class YieldGoalRecommendation(BaseModel):
    """Yield goal recommendation with analysis."""
    goal_type: YieldGoalType = Field(..., description="Type of yield goal")
    recommended_yield: float = Field(..., ge=0.0, description="Recommended yield goal")
    confidence_level: float = Field(..., ge=0.0, le=1.0, description="Confidence in recommendation")
    achievement_probability: float = Field(..., ge=0.0, le=1.0, description="Probability of achieving goal")
    risk_level: YieldRiskLevel = Field(..., description="Risk level of goal")
    rationale: str = Field(..., description="Rationale for recommendation")
    supporting_factors: List[str] = Field(default_factory=list, description="Factors supporting goal")
    risk_factors: List[str] = Field(default_factory=list, description="Risk factors for goal")


class YieldGoalRequest(BaseModel):
    """Request for yield goal analysis."""
    field_id: UUID = Field(..., description="Field identifier")
    crop_type: str = Field(..., description="Type of crop")
    variety: Optional[str] = Field(None, description="Crop variety")
    target_year: int = Field(..., ge=2024, le=2030, description="Target year for goal")
    historical_yields: List[HistoricalYieldData] = Field(..., description="Historical yield data")
    soil_characteristics: SoilCharacteristic = Field(..., description="Current soil characteristics")
    weather_patterns: Optional[WeatherPattern] = Field(None, description="Expected weather patterns")
    management_practices: ManagementPractice = Field(..., description="Planned management practices")
    goal_preference: YieldGoalType = Field(default=YieldGoalType.REALISTIC, description="Preferred goal type")
    risk_tolerance: YieldRiskLevel = Field(default=YieldRiskLevel.MEDIUM, description="Risk tolerance level")


class YieldGoalAnalysis(BaseModel):
    """Comprehensive yield goal analysis."""
    analysis_id: UUID = Field(..., description="Unique analysis identifier")
    field_id: UUID = Field(..., description="Field identifier")
    crop_type: str = Field(..., description="Type of crop")
    analysis_date: datetime = Field(default_factory=datetime.utcnow, description="Analysis date")
    
    # Historical analysis
    historical_trend: YieldTrendAnalysis = Field(..., description="Historical yield trend analysis")
    
    # Potential assessment
    potential_assessment: PotentialYieldAssessment = Field(..., description="Yield potential assessment")
    
    # Goal recommendations
    goal_recommendations: List[YieldGoalRecommendation] = Field(..., description="Yield goal recommendations")
    
    # Risk assessment
    overall_risk_level: YieldRiskLevel = Field(..., description="Overall risk level")
    risk_factors: List[str] = Field(default_factory=list, description="Key risk factors")
    mitigation_strategies: List[str] = Field(default_factory=list, description="Risk mitigation strategies")
    
    # Supporting data
    supporting_data: Dict[str, Any] = Field(default_factory=dict, description="Additional supporting data")
    
    # Metadata
    analysis_confidence: float = Field(..., ge=0.0, le=1.0, description="Overall analysis confidence")
    data_quality_score: float = Field(..., ge=0.0, le=1.0, description="Quality score of input data")


class YieldGoalUpdateRequest(BaseModel):
    """Request to update yield goal."""
    field_id: UUID = Field(..., description="Field identifier")
    new_yield_goal: float = Field(..., ge=0.0, description="New yield goal")
    goal_type: YieldGoalType = Field(..., description="Type of yield goal")
    rationale: str = Field(..., description="Rationale for goal update")
    updated_by: str = Field(..., description="User updating the goal")


class YieldGoalResponse(BaseModel):
    """Response for yield goal operations."""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    analysis: Optional[YieldGoalAnalysis] = Field(None, description="Yield goal analysis")
    recommendations: Optional[List[YieldGoalRecommendation]] = Field(None, description="Goal recommendations")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class YieldGoalValidationResult(BaseModel):
    """Result of yield goal validation."""
    is_valid: bool = Field(..., description="Whether goal is valid")
    validation_score: float = Field(..., ge=0.0, le=1.0, description="Validation score")
    issues: List[str] = Field(default_factory=list, description="Validation issues")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    recommendations: List[str] = Field(default_factory=list, description="Improvement recommendations")


class YieldGoalComparison(BaseModel):
    """Comparison of different yield goals."""
    conservative_goal: YieldGoalRecommendation = Field(..., description="Conservative goal recommendation")
    realistic_goal: YieldGoalRecommendation = Field(..., description="Realistic goal recommendation")
    optimistic_goal: YieldGoalRecommendation = Field(..., description="Optimistic goal recommendation")
    stretch_goal: YieldGoalRecommendation = Field(..., description="Stretch goal recommendation")
    
    # Comparison metrics
    goal_range: float = Field(..., description="Range between min and max goals")
    risk_progression: Dict[str, YieldRiskLevel] = Field(..., description="Risk level for each goal type")
    achievement_probabilities: Dict[str, float] = Field(..., description="Achievement probability for each goal")


class YieldGoalDatabase(BaseModel):
    """Database model for storing yield goals."""
    id: UUID = Field(..., description="Unique identifier")
    field_id: UUID = Field(..., description="Field identifier")
    crop_type: str = Field(..., description="Type of crop")
    variety: Optional[str] = Field(None, description="Crop variety")
    yield_goal: float = Field(..., ge=0.0, description="Yield goal")
    goal_type: YieldGoalType = Field(..., description="Type of yield goal")
    target_year: int = Field(..., description="Target year")
    analysis_id: UUID = Field(..., description="Analysis identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    created_by: str = Field(..., description="User who created the goal")
    is_active: bool = Field(default=True, description="Whether goal is active")
    notes: Optional[str] = Field(None, description="Additional notes")
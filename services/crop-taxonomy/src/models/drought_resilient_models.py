"""
Drought-Resilient Crop Models

Pydantic models for drought-tolerant crop variety recommendations,
water use efficiency analysis, and drought risk assessment.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union, Tuple
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal
from enum import Enum


# ============================================================================
# DROUGHT RESILIENCE ENUMERATIONS
# ============================================================================

class DroughtToleranceLevel(str, Enum):
    """Drought tolerance levels."""
    POOR = "poor"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"

class WaterUseEfficiencyLevel(str, Enum):
    """Water use efficiency levels."""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"

class DroughtRiskLevel(str, Enum):
    """Drought risk levels."""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"

class StressRecoveryLevel(str, Enum):
    """Stress recovery ability levels."""
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"

class RootDepthCategory(str, Enum):
    """Root depth categories."""
    SHALLOW = "shallow"      # < 2 feet
    MODERATE = "moderate"    # 2-4 feet
    DEEP = "deep"           # 4-6 feet
    VERY_DEEP = "very_deep" # > 6 feet


# ============================================================================
# DROUGHT TOLERANCE PROFILES
# ============================================================================

class DroughtToleranceProfile(BaseModel):
    """Comprehensive drought tolerance profile for a crop variety."""
    
    variety_id: UUID = Field(..., description="Variety identifier")
    variety_name: str = Field(..., description="Variety name")
    
    # Primary drought tolerance metrics
    drought_tolerance_level: DroughtToleranceLevel = Field(..., description="Overall drought tolerance level")
    drought_tolerance_score: float = Field(..., ge=0.0, le=1.0, description="Drought tolerance score (0-1)")
    
    # Water use efficiency
    water_use_efficiency: WaterUseEfficiencyLevel = Field(..., description="Water use efficiency level")
    water_use_efficiency_score: float = Field(..., ge=0.0, le=1.0, description="Water efficiency score (0-1)")
    
    # Root system characteristics
    root_depth_category: RootDepthCategory = Field(..., description="Root depth category")
    root_depth_feet: Optional[float] = Field(None, ge=0.0, description="Average root depth in feet")
    root_density_rating: Optional[float] = Field(None, ge=0.0, le=10.0, description="Root density rating (0-10)")
    
    # Stress response characteristics
    stress_recovery_level: StressRecoveryLevel = Field(..., description="Stress recovery ability")
    stress_recovery_score: float = Field(..., ge=0.0, le=1.0, description="Stress recovery score (0-1)")
    
    # Physiological adaptations
    stomatal_control_efficiency: Optional[float] = Field(None, ge=0.0, le=1.0, description="Stomatal control efficiency")
    osmotic_adjustment_capacity: Optional[float] = Field(None, ge=0.0, le=1.0, description="Osmotic adjustment capacity")
    leaf_wax_coating_rating: Optional[float] = Field(None, ge=0.0, le=10.0, description="Leaf wax coating rating")
    
    # Yield stability under stress
    yield_stability_drought: Optional[float] = Field(None, ge=0.0, le=1.0, description="Yield stability under drought")
    yield_reduction_threshold: Optional[float] = Field(None, ge=0.0, le=1.0, description="Yield reduction threshold")
    
    # Regional adaptation
    adapted_drought_regions: List[str] = Field(default_factory=list, description="Drought-prone regions where adapted")
    drought_performance_data: List[Dict[str, Any]] = Field(default_factory=list, description="Performance data in drought conditions")
    
    # Management requirements
    irrigation_requirements: Optional[str] = Field(None, description="Irrigation requirements under drought")
    drought_management_practices: List[str] = Field(default_factory=list, description="Recommended drought management practices")
    
    @field_validator('drought_tolerance_score')
    @classmethod
    def validate_drought_tolerance_score(cls, v):
        if v < 0 or v > 1:
            raise ValueError('Drought tolerance score must be between 0 and 1')
        return v


class WaterUseEfficiencyProfile(BaseModel):
    """Water use efficiency profile for crop varieties."""
    
    variety_id: UUID = Field(..., description="Variety identifier")
    variety_name: str = Field(..., description="Variety name")
    
    # Water use metrics
    water_use_efficiency_level: WaterUseEfficiencyLevel = Field(..., description="Water use efficiency level")
    water_use_efficiency_score: float = Field(..., ge=0.0, le=1.0, description="Water efficiency score (0-1)")
    
    # Water consumption data
    water_consumption_per_acre: Optional[float] = Field(None, ge=0.0, description="Water consumption per acre (gallons)")
    water_consumption_per_bushel: Optional[float] = Field(None, ge=0.0, description="Water consumption per bushel (gallons)")
    
    # Efficiency comparisons
    efficiency_vs_standard: Optional[float] = Field(None, description="Efficiency compared to standard varieties (%)")
    efficiency_vs_region: Optional[float] = Field(None, description="Efficiency compared to regional average (%)")
    
    # Water-saving potential
    potential_water_savings: Optional[float] = Field(None, ge=0.0, description="Potential water savings per acre (gallons)")
    water_savings_percentage: Optional[float] = Field(None, ge=0.0, le=100.0, description="Water savings percentage")
    
    # Irrigation efficiency
    irrigation_efficiency_rating: Optional[float] = Field(None, ge=0.0, le=10.0, description="Irrigation efficiency rating")
    optimal_irrigation_methods: List[str] = Field(default_factory=list, description="Optimal irrigation methods")
    
    # Seasonal water use patterns
    peak_water_demand_period: Optional[str] = Field(None, description="Peak water demand period")
    water_critical_stages: List[str] = Field(default_factory=list, description="Water-critical growth stages")
    
    @field_validator('water_use_efficiency_score')
    @classmethod
    def validate_water_efficiency_score(cls, v):
        if v < 0 or v > 1:
            raise ValueError('Water use efficiency score must be between 0 and 1')
        return v


# ============================================================================
# DROUGHT RESILIENCE SCORING
# ============================================================================

class DroughtResilienceScore(BaseModel):
    """Comprehensive drought resilience scoring for crop varieties."""
    
    variety_id: UUID = Field(..., description="Variety identifier")
    variety_name: str = Field(..., description="Variety name")
    
    # Overall resilience score
    overall_resilience_score: float = Field(..., ge=0.0, le=1.0, description="Overall drought resilience score")
    resilience_level: DroughtToleranceLevel = Field(..., description="Overall resilience level")
    
    # Component scores
    drought_tolerance_score: float = Field(..., ge=0.0, le=1.0, description="Drought tolerance component score")
    water_efficiency_score: float = Field(..., ge=0.0, le=1.0, description="Water efficiency component score")
    stress_recovery_score: float = Field(..., ge=0.0, le=1.0, description="Stress recovery component score")
    yield_stability_score: float = Field(..., ge=0.0, le=1.0, description="Yield stability component score")
    
    # Weighted contributions
    component_weights: Dict[str, float] = Field(default_factory=dict, description="Weights for each component")
    weighted_contributions: Dict[str, float] = Field(default_factory=dict, description="Weighted contribution of each component")
    
    # Confidence and reliability
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in resilience score")
    data_quality_score: float = Field(..., ge=0.0, le=1.0, description="Quality of underlying data")
    reliability_indicators: Dict[str, str] = Field(default_factory=dict, description="Reliability indicators")
    
    # Risk assessment
    drought_risk_level: DroughtRiskLevel = Field(..., description="Recommended drought risk level")
    risk_mitigation_potential: float = Field(..., ge=0.0, le=1.0, description="Risk mitigation potential")
    
    # Economic implications
    drought_premium: Optional[float] = Field(None, description="Additional cost for drought tolerance")
    water_cost_savings: Optional[float] = Field(None, description="Potential water cost savings per acre")
    economic_viability_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Economic viability score")
    
    @field_validator('overall_resilience_score')
    @classmethod
    def validate_overall_score(cls, v):
        if v < 0 or v > 1:
            raise ValueError('Overall resilience score must be between 0 and 1')
        return v


# ============================================================================
# DROUGHT RECOMMENDATION REQUESTS AND RESPONSES
# ============================================================================

class DroughtRecommendationRequest(BaseModel):
    """Request for drought-resilient crop recommendations."""
    
    request_id: str = Field(..., description="Unique request identifier")
    location: Dict[str, Any] = Field(..., description="Location data including coordinates, climate zone, soil type")
    
    # Drought context
    drought_risk_level: Optional[DroughtRiskLevel] = Field(None, description="Known drought risk level")
    current_drought_conditions: Optional[Dict[str, Any]] = Field(None, description="Current drought conditions")
    historical_drought_frequency: Optional[float] = Field(None, ge=0.0, le=1.0, description="Historical drought frequency")
    
    # Crop preferences
    crop_type: Optional[str] = Field(None, description="Preferred crop type")
    crop_category: Optional[str] = Field(None, description="Preferred crop category")
    maturity_preference: Optional[str] = Field(None, description="Maturity preference (early, medium, late)")
    
    # Management constraints
    irrigation_available: Optional[bool] = Field(None, description="Irrigation availability")
    water_limitations: Optional[Dict[str, Any]] = Field(None, description="Water limitations and constraints")
    management_complexity_preference: Optional[str] = Field(None, description="Management complexity preference")
    
    # Economic considerations
    budget_constraints: Optional[Dict[str, Any]] = Field(None, description="Budget constraints")
    market_preferences: Optional[List[str]] = Field(default_factory=list, description="Market preferences")
    risk_tolerance: Optional[str] = Field(None, description="Risk tolerance level")
    
    # Farmer preferences
    farmer_preferences: Optional[Dict[str, Any]] = Field(None, description="Farmer-specific preferences")
    experience_level: Optional[str] = Field(None, description="Farmer experience level")
    equipment_available: Optional[List[str]] = Field(default_factory=list, description="Available equipment")
    
    # Analysis options
    include_alternative_crops: bool = Field(default=True, description="Include alternative crop recommendations")
    include_diversification_strategies: bool = Field(default=True, description="Include diversification strategies")
    include_water_conservation_analysis: bool = Field(default=True, description="Include water conservation analysis")
    
    @field_validator('request_id')
    @classmethod
    def validate_request_id(cls, v):
        if not v or not v.strip():
            raise ValueError("Request ID cannot be empty")
        return v.strip()


class DroughtRecommendationResponse(BaseModel):
    """Response containing drought-resilient crop recommendations."""
    
    request_id: str = Field(..., description="Original request identifier")
    location: Dict[str, Any] = Field(..., description="Location data used for recommendations")
    
    # Drought risk assessment
    drought_risk_assessment: DroughtRiskAssessment = Field(..., description="Drought risk assessment")
    
    # Main recommendations
    recommended_varieties: List[Any] = Field(default_factory=list, description="Recommended drought-resilient varieties")
    alternative_crops: List[AlternativeCropRecommendation] = Field(default_factory=list, description="Alternative crop recommendations")
    
    # Strategic recommendations
    diversification_strategies: List[DiversificationStrategy] = Field(default_factory=list, description="Diversification strategies")
    water_conservation_potential: Optional[WaterConservationPotential] = Field(None, description="Water conservation potential")
    
    # Analysis results
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Overall confidence score")
    data_sources: List[str] = Field(default_factory=list, description="Data sources used")
    limitations: List[str] = Field(default_factory=list, description="Analysis limitations")
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
    processing_time_ms: Optional[float] = Field(None, description="Processing time in milliseconds")
    error_message: Optional[str] = Field(None, description="Error message if generation failed")
    
    class Config:
        json_encoders = {
            datetime: lambda value: value.isoformat(),
            date: lambda value: value.isoformat()
        }


# ============================================================================
# ALTERNATIVE CROP RECOMMENDATIONS
# ============================================================================

class AlternativeCropRecommendation(BaseModel):
    """Recommendation for alternative drought-tolerant crops."""
    
    crop_name: str = Field(..., description="Alternative crop name")
    scientific_name: str = Field(..., description="Scientific name")
    
    # Drought characteristics
    drought_tolerance_level: DroughtToleranceLevel = Field(..., description="Drought tolerance level")
    water_use_efficiency: WaterUseEfficiencyLevel = Field(..., description="Water use efficiency level")
    
    # Performance characteristics
    yield_potential: str = Field(..., description="Yield potential (low, moderate, high)")
    market_demand: str = Field(..., description="Market demand (low, moderate, high)")
    management_complexity: str = Field(..., description="Management complexity (low, moderate, high)")
    
    # Suitability analysis
    suitability_score: float = Field(..., ge=0.0, le=1.0, description="Suitability score for location")
    advantages: List[str] = Field(default_factory=list, description="Key advantages")
    considerations: List[str] = Field(default_factory=list, description="Important considerations")
    
    # Transition requirements
    transition_requirements: List[str] = Field(default_factory=list, description="Requirements for transition")
    equipment_needs: List[str] = Field(default_factory=list, description="Equipment requirements")
    market_access_requirements: List[str] = Field(default_factory=list, description="Market access requirements")
    
    # Economic analysis
    seed_cost_range: Optional[Tuple[float, float]] = Field(None, description="Seed cost range per acre")
    expected_revenue_range: Optional[Tuple[float, float]] = Field(None, description="Expected revenue range per acre")
    break_even_analysis: Optional[Dict[str, Any]] = Field(None, description="Break-even analysis")
    
    # Risk assessment
    production_risks: List[str] = Field(default_factory=list, description="Production risks")
    market_risks: List[str] = Field(default_factory=list, description="Market risks")
    mitigation_strategies: List[str] = Field(default_factory=list, description="Risk mitigation strategies")


# ============================================================================
# DIVERSIFICATION STRATEGIES
# ============================================================================

class DiversificationStrategy(BaseModel):
    """Diversification strategy for drought risk management."""
    
    strategy_type: str = Field(..., description="Type of diversification strategy")
    description: str = Field(..., description="Strategy description")
    
    # Implementation details
    implementation_steps: List[str] = Field(..., description="Steps to implement strategy")
    timeline: Optional[str] = Field(None, description="Implementation timeline")
    resource_requirements: List[str] = Field(default_factory=list, description="Resource requirements")
    
    # Expected outcomes
    expected_benefits: List[str] = Field(..., description="Expected benefits")
    risk_reduction_potential: float = Field(..., ge=0.0, le=1.0, description="Risk reduction potential")
    implementation_difficulty: str = Field(..., description="Implementation difficulty level")
    
    # Economic considerations
    implementation_cost: Optional[float] = Field(None, description="Implementation cost per acre")
    expected_return: Optional[float] = Field(None, description="Expected return on investment")
    payback_period: Optional[str] = Field(None, description="Payback period")
    
    # Risk factors
    implementation_risks: List[str] = Field(default_factory=list, description="Implementation risks")
    success_factors: List[str] = Field(default_factory=list, description="Success factors")
    
    # Monitoring and evaluation
    key_performance_indicators: List[str] = Field(default_factory=list, description="Key performance indicators")
    monitoring_requirements: List[str] = Field(default_factory=list, description="Monitoring requirements")


# ============================================================================
# DROUGHT RISK ASSESSMENT
# ============================================================================

class DroughtRiskAssessment(BaseModel):
    """Comprehensive drought risk assessment."""
    
    location: Dict[str, Any] = Field(..., description="Location data")
    overall_risk_level: DroughtRiskLevel = Field(..., description="Overall drought risk level")
    
    # Risk factors
    risk_factors: Dict[str, Any] = Field(..., description="Individual risk factors and scores")
    risk_factor_weights: Dict[str, float] = Field(default_factory=dict, description="Weights for risk factors")
    
    # Historical analysis
    historical_drought_frequency: Optional[float] = Field(None, description="Historical drought frequency")
    historical_drought_severity: Optional[str] = Field(None, description="Historical drought severity")
    drought_trends: Optional[Dict[str, Any]] = Field(None, description="Drought trend analysis")
    
    # Current conditions
    current_soil_moisture: Optional[float] = Field(None, description="Current soil moisture level")
    current_precipitation_deficit: Optional[float] = Field(None, description="Current precipitation deficit")
    current_drought_index: Optional[float] = Field(None, description="Current drought index")
    
    # Forecast analysis
    short_term_forecast: Optional[Dict[str, Any]] = Field(None, description="Short-term drought forecast")
    seasonal_forecast: Optional[Dict[str, Any]] = Field(None, description="Seasonal drought forecast")
    long_term_climate_trends: Optional[Dict[str, Any]] = Field(None, description="Long-term climate trends")
    
    # Confidence and reliability
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Assessment confidence score")
    data_quality_score: float = Field(..., ge=0.0, le=1.0, description="Data quality score")
    assessment_date: datetime = Field(default_factory=datetime.utcnow, description="Assessment date")
    
    # Recommendations
    risk_mitigation_priorities: List[str] = Field(default_factory=list, description="Risk mitigation priorities")
    monitoring_recommendations: List[str] = Field(default_factory=list, description="Monitoring recommendations")


# ============================================================================
# WATER CONSERVATION POTENTIAL
# ============================================================================

class WaterConservationPotential(BaseModel):
    """Water conservation potential analysis."""
    
    variety_based_savings: float = Field(..., ge=0.0, description="Water savings from variety selection (gallons/acre)")
    alternative_crop_savings: float = Field(..., ge=0.0, description="Water savings from alternative crops (gallons/acre)")
    total_potential_savings: float = Field(..., ge=0.0, description="Total potential water savings (gallons/acre)")
    
    # Savings analysis
    savings_percentage: float = Field(..., ge=0.0, le=100.0, description="Percentage of water savings")
    baseline_water_use: Optional[float] = Field(None, description="Baseline water use (gallons/acre)")
    optimized_water_use: Optional[float] = Field(None, description="Optimized water use (gallons/acre)")
    
    # Implementation details
    implementation_timeline: str = Field(..., description="Implementation timeline")
    implementation_cost: Optional[float] = Field(None, description="Implementation cost per acre")
    cost_benefit_ratio: Optional[float] = Field(None, description="Cost-benefit ratio")
    
    # Economic impact
    water_cost_savings: Optional[float] = Field(None, description="Water cost savings per acre")
    total_economic_benefit: Optional[float] = Field(None, description="Total economic benefit per acre")
    payback_period: Optional[str] = Field(None, description="Payback period")
    
    # Risk factors
    implementation_risks: List[str] = Field(default_factory=list, description="Implementation risks")
    success_probability: Optional[float] = Field(None, ge=0.0, le=1.0, description="Success probability")
    
    # Monitoring requirements
    monitoring_requirements: List[str] = Field(default_factory=list, description="Monitoring requirements")
    performance_indicators: List[str] = Field(default_factory=list, description="Performance indicators")


# ============================================================================
# DROUGHT MANAGEMENT PRACTICES
# ============================================================================

class DroughtManagementPractice(BaseModel):
    """Drought management practice recommendation."""
    
    practice_name: str = Field(..., description="Practice name")
    practice_type: str = Field(..., description="Practice type (cultural, irrigation, soil, etc.)")
    description: str = Field(..., description="Practice description")
    
    # Implementation details
    implementation_steps: List[str] = Field(..., description="Implementation steps")
    timing_requirements: List[str] = Field(default_factory=list, description="Timing requirements")
    equipment_needs: List[str] = Field(default_factory=list, description="Equipment needs")
    
    # Effectiveness
    water_savings_potential: Optional[float] = Field(None, description="Water savings potential (gallons/acre)")
    effectiveness_rating: Optional[float] = Field(None, ge=0.0, le=10.0, description="Effectiveness rating (0-10)")
    applicability_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Applicability score for location")
    
    # Cost analysis
    implementation_cost: Optional[float] = Field(None, description="Implementation cost per acre")
    maintenance_cost: Optional[float] = Field(None, description="Annual maintenance cost per acre")
    cost_effectiveness: Optional[str] = Field(None, description="Cost effectiveness rating")
    
    # Risk factors
    implementation_risks: List[str] = Field(default_factory=list, description="Implementation risks")
    success_factors: List[str] = Field(default_factory=list, description="Success factors")
    
    # Monitoring and evaluation
    monitoring_requirements: List[str] = Field(default_factory=list, description="Monitoring requirements")
    performance_indicators: List[str] = Field(default_factory=list, description="Performance indicators")
    evaluation_timeline: Optional[str] = Field(None, description="Evaluation timeline")


# ============================================================================
# DROUGHT MONITORING AND ALERTS
# ============================================================================

class DroughtAlert(BaseModel):
    """Drought alert or warning."""
    
    alert_id: UUID = Field(default_factory=UUID, description="Alert identifier")
    alert_type: str = Field(..., description="Alert type (warning, watch, advisory)")
    severity_level: str = Field(..., description="Severity level (low, moderate, high, severe)")
    
    # Alert details
    title: str = Field(..., description="Alert title")
    description: str = Field(..., description="Alert description")
    affected_area: str = Field(..., description="Affected area")
    
    # Timing
    issued_at: datetime = Field(default_factory=datetime.utcnow, description="Alert issue time")
    valid_until: Optional[datetime] = Field(None, description="Alert validity period")
    
    # Recommendations
    immediate_actions: List[str] = Field(default_factory=list, description="Immediate actions required")
    monitoring_recommendations: List[str] = Field(default_factory=list, description="Monitoring recommendations")
    
    # Data sources
    data_sources: List[str] = Field(default_factory=list, description="Data sources")
    confidence_level: float = Field(..., ge=0.0, le=1.0, description="Confidence level")


class DroughtMonitoringData(BaseModel):
    """Drought monitoring data point."""
    
    location: Dict[str, Any] = Field(..., description="Location data")
    measurement_date: datetime = Field(..., description="Measurement date")
    
    # Soil moisture data
    soil_moisture_surface: Optional[float] = Field(None, description="Surface soil moisture (%)")
    soil_moisture_deep: Optional[float] = Field(None, description="Deep soil moisture (%)")
    soil_moisture_index: Optional[float] = Field(None, description="Soil moisture index")
    
    # Precipitation data
    precipitation_current: Optional[float] = Field(None, description="Current precipitation (inches)")
    precipitation_deficit: Optional[float] = Field(None, description="Precipitation deficit (inches)")
    precipitation_percentile: Optional[float] = Field(None, description="Precipitation percentile")
    
    # Drought indices
    palmer_drought_index: Optional[float] = Field(None, description="Palmer Drought Index")
    standardized_precipitation_index: Optional[float] = Field(None, description="Standardized Precipitation Index")
    crop_moisture_index: Optional[float] = Field(None, description="Crop Moisture Index")
    
    # Vegetation health
    vegetation_health_index: Optional[float] = Field(None, description="Vegetation Health Index")
    crop_condition_rating: Optional[str] = Field(None, description="Crop condition rating")
    
    # Data quality
    data_quality_score: float = Field(default=0.8, ge=0.0, le=1.0, description="Data quality score")
    data_sources: List[str] = Field(default_factory=list, description="Data sources")
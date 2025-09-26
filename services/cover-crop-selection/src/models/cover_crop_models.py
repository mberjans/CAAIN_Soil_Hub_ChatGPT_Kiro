"""
Cover Crop Data Models

Pydantic models for cover crop selection, species data, and recommendations.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import date, datetime
from enum import Enum


class CoverCropType(str, Enum):
    """Cover crop functional types."""
    LEGUME = "legume"
    GRASS = "grass"
    BRASSICA = "brassica"
    FORB = "forb"
    MIXTURE = "mixture"


class GrowingSeason(str, Enum):
    """Cover crop growing seasons."""
    WINTER = "winter"
    SUMMER = "summer"
    SPRING = "spring"
    FALL = "fall"
    YEAR_ROUND = "year_round"


class SoilBenefit(str, Enum):
    """Primary soil benefits from cover crops."""
    NITROGEN_FIXATION = "nitrogen_fixation"
    EROSION_CONTROL = "erosion_control"
    ORGANIC_MATTER = "organic_matter"
    COMPACTION_RELIEF = "compaction_relief"
    WEED_SUPPRESSION = "weed_suppression"
    PEST_MANAGEMENT = "pest_management"
    PEST_SUPPRESSION = "pest_suppression"
    NUTRIENT_SCAVENGING = "nutrient_scavenging"
    SOIL_STRUCTURE = "soil_structure"
    BIOMASS_PRODUCTION = "biomass_production"
    HEAT_TOLERANCE = "heat_tolerance"
    SALT_TOLERANCE = "salt_tolerance"
    POLLINATOR_HABITAT = "pollinator_habitat"
    PHOSPHORUS_MOBILIZATION = "phosphorus_mobilization"


class CoverCropSpecies(BaseModel):
    """Individual cover crop species data."""
    
    species_id: str = Field(..., description="Unique species identifier")
    common_name: str = Field(..., description="Common name")
    scientific_name: str = Field(..., description="Scientific name")
    cover_crop_type: CoverCropType = Field(..., description="Functional type")
    
    # Climate requirements
    hardiness_zones: List[str] = Field(..., description="USDA hardiness zones")
    min_temp_f: Optional[float] = Field(None, description="Minimum temperature tolerance (°F)")
    max_temp_f: Optional[float] = Field(None, description="Maximum temperature tolerance (°F)")
    growing_season: GrowingSeason = Field(..., description="Primary growing season")
    
    # Soil requirements
    ph_range: Dict[str, float] = Field(..., description="pH tolerance range")
    drainage_tolerance: List[str] = Field(..., description="Drainage class tolerance")
    salt_tolerance: Optional[str] = Field(None, description="Salt tolerance level")
    
    # Growth characteristics
    seeding_rate_lbs_acre: Dict[str, float] = Field(..., description="Seeding rates by method")
    planting_depth_inches: float = Field(..., ge=0.0, description="Planting depth in inches")
    days_to_establishment: int = Field(..., ge=1, description="Days to establishment")
    biomass_production: str = Field(..., description="Biomass production level")
    
    # Soil benefits
    primary_benefits: List[SoilBenefit] = Field(..., description="Primary soil benefits")
    nitrogen_fixation_lbs_acre: Optional[float] = Field(None, ge=0, description="Nitrogen fixation potential")
    root_depth_feet: Optional[float] = Field(None, ge=0, description="Root depth in feet")
    
    # Agronomic considerations
    termination_methods: List[str] = Field(..., description="Termination options")
    cash_crop_compatibility: List[str] = Field(..., description="Compatible cash crops")
    potential_issues: Optional[List[str]] = Field(None, description="Potential problems")
    
    # Economic data
    seed_cost_per_acre: Optional[float] = Field(None, ge=0, description="Seed cost estimate")
    establishment_cost_per_acre: Optional[float] = Field(None, ge=0, description="Total establishment cost")
    
    @validator('ph_range')
    def validate_ph_range(cls, v):
        """Validate pH range."""
        if 'min' not in v or 'max' not in v:
            raise ValueError("pH range must include 'min' and 'max' values")
        if not (3.0 <= v['min'] <= 10.0) or not (3.0 <= v['max'] <= 10.0):
            raise ValueError("pH values must be between 3.0 and 10.0")
        if v['min'] >= v['max']:
            raise ValueError("Minimum pH must be less than maximum pH")
        return v


class SoilConditions(BaseModel):
    """Current soil conditions for cover crop selection."""
    
    ph: float = Field(..., ge=3.0, le=10.0, description="Current soil pH")
    organic_matter_percent: float = Field(..., ge=0.0, le=15.0, description="Organic matter percentage")
    drainage_class: str = Field(..., description="Soil drainage classification")
    texture: Optional[str] = Field(None, description="Soil texture class")
    compaction_issues: bool = Field(default=False, description="Soil compaction present")
    erosion_risk: str = Field(default="low", description="Erosion risk level")
    nitrogen_status: Optional[str] = Field(None, description="Nitrogen availability")
    previous_cover_crop: Optional[str] = Field(None, description="Previous cover crop")


class ClimateData(BaseModel):
    """Climate data for cover crop selection."""
    
    hardiness_zone: str = Field(..., description="USDA hardiness zone")
    average_annual_precipitation: Optional[float] = Field(None, ge=0, description="Annual precipitation (inches)")
    growing_season_length: Optional[int] = Field(None, ge=0, le=365, description="Growing season days")
    last_frost_date: Optional[date] = Field(None, description="Average last frost date")
    first_frost_date: Optional[date] = Field(None, description="Average first frost date")
    drought_risk: Optional[str] = Field(None, description="Drought risk level")
    heat_stress_risk: Optional[str] = Field(None, description="Heat stress risk")


class FarmerGoalCategory(str, Enum):
    """High-level farmer goal categories for cover crop selection."""
    SOIL_HEALTH = "soil_health"
    NUTRIENT_MANAGEMENT = "nutrient_management"
    EROSION_CONTROL = "erosion_control"
    WEED_MANAGEMENT = "weed_management"
    WATER_MANAGEMENT = "water_management"
    PEST_DISEASE_CONTROL = "pest_disease_control"
    CARBON_SEQUESTRATION = "carbon_sequestration"
    ECONOMIC_OPTIMIZATION = "economic_optimization"
    BIODIVERSITY_ENHANCEMENT = "biodiversity_enhancement"


class GoalPriority(str, Enum):
    """Priority levels for farmer goals."""
    CRITICAL = "critical"  # Must achieve - highest weight
    HIGH = "high"         # Very important - high weight
    MEDIUM = "medium"     # Important - moderate weight
    LOW = "low"          # Nice to have - low weight


class SpecificGoal(BaseModel):
    """Specific goal within a farmer's cover crop objectives."""
    
    goal_id: str = Field(..., description="Unique goal identifier")
    category: FarmerGoalCategory = Field(..., description="Goal category")
    priority: GoalPriority = Field(..., description="Goal priority level")
    weight: float = Field(..., ge=0.0, le=1.0, description="Goal weight (0-1)")
    
    # Goal specifics
    target_benefit: SoilBenefit = Field(..., description="Target soil benefit")
    quantitative_target: Optional[float] = Field(None, description="Quantitative target if applicable")
    target_unit: Optional[str] = Field(None, description="Unit for quantitative target")
    
    # Constraints and preferences
    acceptable_cost_range: Optional[Dict[str, float]] = Field(None, description="Min/max cost per acre")
    management_complexity_limit: Optional[str] = Field(None, description="Maximum management complexity")
    timing_constraints: Optional[Dict[str, Any]] = Field(None, description="Timing restrictions")
    
    # Success criteria
    success_metrics: List[str] = Field(default_factory=list, description="How to measure goal achievement")
    minimum_achievement_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Minimum achievement level")


class GoalBasedObjectives(BaseModel):
    """Enhanced goal-based farmer objectives for cover crop selection."""
    
    # Goal structure
    specific_goals: List[SpecificGoal] = Field(..., min_items=1, description="Specific farmer goals")
    goal_synergies: Optional[Dict[str, List[str]]] = Field(None, description="Goals that work well together")
    goal_conflicts: Optional[Dict[str, List[str]]] = Field(None, description="Potentially conflicting goals")
    
    # Overall preferences
    primary_focus: FarmerGoalCategory = Field(..., description="Primary focus area")
    secondary_focus: Optional[FarmerGoalCategory] = Field(None, description="Secondary focus area")
    overall_strategy: str = Field(default="balanced", description="Overall strategy (aggressive, balanced, conservative)")
    
    # Constraints
    total_budget_per_acre: Optional[float] = Field(None, ge=0, description="Total budget per acre")
    management_capacity: str = Field(default="moderate", description="Management capacity (low, moderate, high)")
    risk_tolerance: str = Field(default="moderate", description="Risk tolerance (low, moderate, high)")
    
    # Integration preferences
    cash_crop_integration: Optional[str] = Field(None, description="Cash crop to integrate with")
    rotation_system_goals: Optional[List[str]] = Field(None, description="Rotation system specific goals")
    multi_year_planning: bool = Field(default=False, description="Multi-year goal planning")
    
    @validator('specific_goals')
    def validate_goal_weights(cls, v):
        """Validate that goal weights sum to reasonable range."""
        total_weight = sum(goal.weight for goal in v)
        if total_weight > 1.5:  # Allow some flexibility beyond perfect 1.0
            raise ValueError("Total goal weights should not exceed 1.5")
        if total_weight < 0.3:
            raise ValueError("Total goal weights should be at least 0.3")
        return v


class GoalAchievementMetrics(BaseModel):
    """Metrics for tracking goal achievement in cover crop recommendations."""
    
    goal_id: str = Field(..., description="Associated goal identifier")
    predicted_achievement_score: float = Field(..., ge=0.0, le=1.0, description="Predicted achievement (0-1)")
    confidence_level: float = Field(..., ge=0.0, le=1.0, description="Confidence in prediction")
    
    # Quantitative predictions
    quantitative_prediction: Optional[float] = Field(None, description="Quantitative benefit prediction")
    prediction_range: Optional[Dict[str, float]] = Field(None, description="Min/max prediction range")
    
    # Contributing factors
    primary_contributing_factors: List[str] = Field(..., description="Main factors contributing to achievement")
    limiting_factors: Optional[List[str]] = Field(None, description="Factors that may limit achievement")
    enhancement_opportunities: Optional[List[str]] = Field(None, description="Ways to enhance achievement")
    
    # Success monitoring
    monitoring_indicators: List[str] = Field(..., description="Key indicators to monitor")
    measurement_timeline: Optional[Dict[str, str]] = Field(None, description="When to measure indicators")


class GoalBasedSpeciesRecommendation(BaseModel):
    """Individual cover crop species recommendation optimized for specific farmer goals."""
    
    # Base recommendation
    species: CoverCropSpecies = Field(..., description="Recommended species")
    suitability_score: float = Field(..., ge=0.0, le=1.0, description="Overall suitability score")
    
    # Goal-specific scoring
    goal_achievement_scores: List[GoalAchievementMetrics] = Field(..., description="Goal-specific achievement metrics")
    overall_goal_alignment: float = Field(..., ge=0.0, le=1.0, description="Overall goal alignment score")
    goal_synergy_score: float = Field(..., ge=0.0, le=1.0, description="How well goals work together")
    
    # Optimized recommendations
    goal_optimized_seeding_rate: float = Field(..., ge=0, description="Seeding rate optimized for goals")
    goal_optimized_planting_date: date = Field(..., description="Planting date optimized for goals")
    goal_optimized_termination: str = Field(..., description="Termination method optimized for goals")
    
    # Goal-specific benefits and trade-offs
    goal_specific_benefits: Dict[str, List[str]] = Field(..., description="Benefits by goal category")
    potential_goal_trade_offs: Optional[List[str]] = Field(None, description="Potential trade-offs between goals")
    goal_enhancement_strategies: List[str] = Field(..., description="Strategies to enhance goal achievement")
    
    # Economic analysis with goal context
    goal_based_cost_benefit: Optional[Dict[str, Any]] = Field(None, description="Cost-benefit analysis by goal")
    goal_based_roi_estimate: Optional[float] = Field(None, description="ROI estimate considering goal priorities")
    
    # Management guidance
    goal_focused_management_notes: List[str] = Field(..., description="Management notes focused on goal achievement")
    goal_monitoring_plan: List[str] = Field(..., description="Monitoring plan for goal achievement")
    goal_adjustment_recommendations: Optional[List[str]] = Field(None, description="Potential goal adjustments")


class GoalBasedRecommendation(BaseModel):
    """Complete goal-based cover crop recommendation response."""
    
    # Request tracking
    request_id: str = Field(..., description="Unique request identifier")
    farmer_goals: GoalBasedObjectives = Field(..., description="Farmer's goal-based objectives")
    
    # Recommended species
    recommended_species: List[CoverCropSpecies] = Field(..., description="List of recommended cover crop species")
    
    # Aggregate goal analysis
    goal_achievement_scores: Dict[str, float] = Field(..., description="Achievement scores by goal category")
    optimized_seeding_rates: Dict[str, float] = Field(..., description="Optimized seeding rates by species ID")
    
    # Management guidance
    goal_focused_management: Dict[str, Dict[str, List[str]]] = Field(..., description="Management practices by goal category")
    
    # Economic analysis
    cost_benefit_analysis: Dict[str, Any] = Field(..., description="Overall cost-benefit analysis")
    goal_synergy_analysis: Dict[str, Any] = Field(..., description="Analysis of goal synergies and conflicts")
    
    # Overall confidence
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Overall confidence in recommendations")
    
    # Individual detailed recommendations (optional for detailed analysis)
    individual_recommendations: Optional[List[GoalBasedSpeciesRecommendation]] = Field(None, description="Detailed individual species recommendations")


class CoverCropObjectives(BaseModel):
    """Farmer objectives for cover crop selection."""
    
    primary_goals: List[SoilBenefit] = Field(..., description="Primary objectives")
    nitrogen_needs: bool = Field(default=False, description="Need nitrogen fixation")
    erosion_control_priority: bool = Field(default=False, description="Erosion control priority")
    organic_matter_goal: bool = Field(default=False, description="Organic matter improvement")
    weed_suppression_needed: bool = Field(default=False, description="Weed suppression needed")
    cash_crop_integration: Optional[str] = Field(None, description="Cash crop to integrate with")
    budget_per_acre: Optional[float] = Field(None, ge=0, description="Budget per acre")
    management_intensity: str = Field(default="moderate", description="Management intensity preference")


class CoverCropSelectionRequest(BaseModel):
    """Request for cover crop selection."""
    
    request_id: str = Field(..., description="Unique request identifier")
    location: Dict[str, Any] = Field(..., description="Location data with coordinates")
    soil_conditions: SoilConditions = Field(..., description="Current soil conditions")
    climate_data: Optional[ClimateData] = Field(None, description="Climate information")
    objectives: CoverCropObjectives = Field(..., description="Cover crop objectives")
    planting_window: Dict[str, date] = Field(..., description="Planting date range")
    field_size_acres: float = Field(..., gt=0, description="Field size in acres")
    farming_system: str = Field(default="conventional", description="Farming system type")
    equipment_constraints: Optional[List[str]] = Field(None, description="Equipment limitations")


class CoverCropRecommendation(BaseModel):
    """Individual cover crop recommendation."""
    
    species: CoverCropSpecies = Field(..., description="Recommended species")
    suitability_score: float = Field(..., ge=0.0, le=1.0, description="Suitability score")
    confidence_level: float = Field(..., ge=0.0, le=1.0, description="Confidence in recommendation")
    
    # Specific recommendations
    seeding_rate_recommendation: float = Field(..., ge=0, description="Recommended seeding rate (lbs/acre)")
    planting_date_recommendation: date = Field(..., description="Recommended planting date")
    termination_recommendation: str = Field(..., description="Recommended termination method")
    
    # Expected benefits
    expected_benefits: List[str] = Field(..., description="Expected benefits for this field")
    nitrogen_contribution: Optional[float] = Field(None, description="Expected N contribution (lbs/acre)")
    soil_improvement_score: float = Field(..., ge=0.0, le=1.0, description="Soil improvement potential")
    
    # Economic analysis
    cost_per_acre: Optional[float] = Field(None, ge=0, description="Estimated cost per acre")
    roi_estimate: Optional[float] = Field(None, description="ROI estimate percentage")
    
    # Implementation guidance
    management_notes: List[str] = Field(..., description="Management recommendations")
    potential_challenges: Optional[List[str]] = Field(None, description="Potential challenges")
    success_indicators: List[str] = Field(..., description="Success indicators to monitor")


class CoverCropMixture(BaseModel):
    """Cover crop mixture recommendation."""
    
    mixture_id: str = Field(..., description="Mixture identifier")
    mixture_name: str = Field(..., description="Mixture name")
    species_list: List[Dict[str, Any]] = Field(..., description="Species with seeding rates")
    total_seeding_rate: float = Field(..., ge=0, description="Total seeding rate (lbs/acre)")
    mixture_benefits: List[str] = Field(..., description="Combined benefits")
    complexity_level: str = Field(..., description="Management complexity")


class CoverCropSelectionResponse(BaseModel):
    """Response containing cover crop recommendations."""
    
    request_id: str = Field(..., description="Original request identifier")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
    
    # Recommendations
    single_species_recommendations: List[CoverCropRecommendation] = Field(
        ..., description="Single species recommendations"
    )
    mixture_recommendations: Optional[List[CoverCropMixture]] = Field(
        None, description="Mixture recommendations"
    )
    
    # Analysis
    field_assessment: Dict[str, Any] = Field(..., description="Field condition analysis")
    climate_suitability: Dict[str, Any] = Field(..., description="Climate compatibility analysis")
    seasonal_considerations: List[str] = Field(..., description="Seasonal timing notes")
    
    # Guidance
    implementation_timeline: List[Dict[str, Any]] = Field(..., description="Implementation timeline")
    monitoring_recommendations: List[str] = Field(..., description="Monitoring guidelines")
    follow_up_actions: Optional[List[str]] = Field(None, description="Follow-up recommendations")
    
    # Metadata
    overall_confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence score")
    data_sources: List[str] = Field(..., description="Data sources used")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }


class SpeciesLookupRequest(BaseModel):
    """Request for cover crop species information."""
    
    species_name: Optional[str] = Field(None, description="Species name to lookup")
    cover_crop_type: Optional[CoverCropType] = Field(None, description="Filter by type")
    hardiness_zone: Optional[str] = Field(None, description="Filter by hardiness zone")
    growing_season: Optional[GrowingSeason] = Field(None, description="Filter by season")
    primary_benefit: Optional[SoilBenefit] = Field(None, description="Filter by benefit")


class SpeciesLookupResponse(BaseModel):
    """Response with cover crop species information."""
    
    species_count: int = Field(..., description="Number of species returned")
    species_list: List[CoverCropSpecies] = Field(..., description="Matching species")
    filter_summary: Dict[str, Any] = Field(..., description="Applied filters summary")


# New models for main crop and rotation integration

class MainCropRotationPlan(BaseModel):
    """Represents a main crop rotation sequence."""
    
    rotation_id: str = Field(..., description="Unique rotation identifier")
    rotation_name: str = Field(..., description="Rotation system name")
    sequence: List[str] = Field(..., description="Crop sequence in rotation")
    duration_years: int = Field(..., ge=1, le=10, description="Rotation cycle length in years")
    region_suitability: List[str] = Field(..., description="Suitable regions/zones")
    
    # Rotation characteristics
    primary_benefits: List[str] = Field(..., description="Main rotation benefits")
    sustainability_rating: float = Field(..., ge=0.0, le=10.0, description="Sustainability score out of 10")
    complexity_level: str = Field(..., description="Management complexity (simple, moderate, complex)")
    
    # Economic data
    economic_performance: str = Field(..., description="Economic performance rating")
    risk_level: str = Field(default="moderate", description="Risk assessment")
    
    # Timing information
    typical_planting_dates: Dict[str, Dict[str, str]] = Field(..., description="Typical planting dates by crop")
    harvest_windows: Dict[str, Dict[str, str]] = Field(..., description="Harvest timing by crop")


class CoverCropRotationIntegration(BaseModel):
    """Links cover crops to rotation positions."""
    
    integration_id: str = Field(..., description="Unique integration identifier")
    rotation_plan: MainCropRotationPlan = Field(..., description="Associated rotation plan")
    cover_crop_positions: List[Dict[str, Any]] = Field(..., description="Cover crop integration points")
    
    # Integration analysis
    nitrogen_cycling_benefits: Dict[str, float] = Field(..., description="N cycling benefits by position")
    pest_management_benefits: List[str] = Field(..., description="Pest management advantages")
    soil_health_improvements: List[str] = Field(..., description="Soil health benefits")
    
    # Compatibility scores
    compatibility_scores: Dict[str, float] = Field(..., description="Compatibility scores by position")
    risk_factors: List[str] = Field(default_factory=list, description="Potential risks or challenges")
    
    # Economic impact
    estimated_cost_impact: float = Field(default=0.0, description="Cost impact per acre")
    estimated_benefit_value: float = Field(default=0.0, description="Estimated benefits value per acre")


class CropTimingWindow(BaseModel):
    """Represents planting/harvest timing constraints."""
    
    window_id: str = Field(..., description="Unique timing window identifier")
    crop_name: str = Field(..., description="Crop name")
    window_type: str = Field(..., description="Window type (planting, harvest, termination)")
    
    # Timing constraints
    earliest_date: Optional[date] = Field(None, description="Earliest allowable date")
    optimal_start: date = Field(..., description="Optimal window start")
    optimal_end: date = Field(..., description="Optimal window end")
    latest_date: Optional[date] = Field(None, description="Latest allowable date")
    
    # Context information
    region: Optional[str] = Field(None, description="Geographic region")
    climate_zone: Optional[str] = Field(None, description="Climate zone")
    soil_conditions: Optional[str] = Field(None, description="Specific soil requirements")
    
    # Flexibility and constraints
    flexibility_days: int = Field(default=14, description="Flexibility in days")
    critical_factors: List[str] = Field(default_factory=list, description="Critical timing factors")
    weather_dependencies: List[str] = Field(default_factory=list, description="Weather-dependent factors")
    
    @validator('optimal_start', 'optimal_end')
    def validate_dates(cls, v):
        """Validate date fields."""
        if v and v.year < 2020:
            raise ValueError("Dates should be reasonable agricultural planning dates")
        return v


class RotationBenefitAnalysis(BaseModel):
    """Analyzes benefits of cover crops in rotation."""
    
    analysis_id: str = Field(..., description="Unique analysis identifier")
    rotation_plan: MainCropRotationPlan = Field(..., description="Analyzed rotation")
    cover_crop_integration: CoverCropRotationIntegration = Field(..., description="Integration plan")
    
    # Quantified benefits
    nitrogen_fixation_value: float = Field(default=0.0, ge=0.0, description="N fixation value (lbs N/acre)")
    erosion_prevention_value: float = Field(default=0.0, ge=0.0, description="Erosion prevention value ($)")
    organic_matter_improvement: float = Field(default=0.0, ge=0.0, description="OM improvement percentage")
    weed_suppression_value: float = Field(default=0.0, ge=0.0, description="Weed suppression value ($)")
    
    # Pest and disease management
    pest_pressure_reduction: Dict[str, float] = Field(default_factory=dict, description="Pest reduction by type")
    disease_break_effectiveness: Dict[str, float] = Field(default_factory=dict, description="Disease break effectiveness")
    beneficial_insect_support: float = Field(default=0.0, ge=0.0, le=1.0, description="Beneficial insect support score")
    
    # Long-term impacts
    soil_health_trajectory: Dict[str, float] = Field(default_factory=dict, description="Soil health trends")
    yield_impact_projections: Dict[str, float] = Field(default_factory=dict, description="Yield impact by crop")
    sustainability_improvements: List[str] = Field(default_factory=list, description="Sustainability benefits")
    
    # Economic analysis
    total_benefit_value: float = Field(default=0.0, description="Total benefit value per acre")
    cost_benefit_ratio: float = Field(default=1.0, ge=0.0, description="Benefit-to-cost ratio")
    payback_period_years: Optional[float] = Field(None, description="Investment payback period")
    
    # Risk assessment
    implementation_risks: List[str] = Field(default_factory=list, description="Implementation risks")
    mitigation_strategies: List[str] = Field(default_factory=list, description="Risk mitigation strategies")
    confidence_level: float = Field(default=0.7, ge=0.0, le=1.0, description="Analysis confidence level")
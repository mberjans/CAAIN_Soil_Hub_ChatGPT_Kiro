"""
Fertilizer Type Selection Data Models

Pydantic models for fertilizer type selection, comparison, and recommendations.
Implements data structures for US-006: Fertilizer Type Selection.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import date, datetime
from enum import Enum
from decimal import Decimal


class FertilizerType(str, Enum):
    """Types of fertilizers available."""
    ORGANIC = "organic"
    SYNTHETIC = "synthetic"
    SLOW_RELEASE = "slow_release"
    LIQUID = "liquid"
    GRANULAR = "granular"
    FOLIAR = "foliar"


class ReleasePattern(str, Enum):
    """Nutrient release patterns."""
    IMMEDIATE = "immediate"
    SLOW = "slow"
    CONTROLLED = "controlled"
    ORGANIC_BREAKDOWN = "organic_breakdown"


class ApplicationMethod(str, Enum):
    """Fertilizer application methods."""
    BROADCAST = "broadcast"
    BANDED = "banded"
    FOLIAR_SPRAY = "foliar_spray"
    FERTIGATION = "fertigation"
    INJECTION = "injection"
    INCORPORATION = "incorporation"


class FarmerPriority(str, Enum):
    """Farmer priority categories."""
    COST_EFFECTIVENESS = "cost_effectiveness"
    SOIL_HEALTH = "soil_health"
    QUICK_RESULTS = "quick_results"
    ENVIRONMENTAL_IMPACT = "environmental_impact"
    EASE_OF_APPLICATION = "ease_of_application"
    LONG_TERM_BENEFITS = "long_term_benefits"


class NutrientContent(BaseModel):
    """Nutrient content information."""
    nitrogen_percent: float = Field(..., ge=0.0, le=50.0, description="Nitrogen content (%)")
    phosphorus_p2o5_percent: float = Field(..., ge=0.0, le=50.0, description="Phosphorus as P2O5 (%)")
    potassium_k2o_percent: float = Field(..., ge=0.0, le=50.0, description="Potassium as K2O (%)")
    calcium_percent: Optional[float] = Field(None, ge=0.0, le=30.0, description="Calcium content (%)")
    magnesium_percent: Optional[float] = Field(None, ge=0.0, le=15.0, description="Magnesium content (%)")
    sulfur_percent: Optional[float] = Field(None, ge=0.0, le=20.0, description="Sulfur content (%)")


class MicronutrientContent(BaseModel):
    """Micronutrient content information."""
    iron_percent: Optional[float] = Field(None, ge=0.0, le=10.0, description="Iron content (%)")
    manganese_percent: Optional[float] = Field(None, ge=0.0, le=5.0, description="Manganese content (%)")
    zinc_percent: Optional[float] = Field(None, ge=0.0, le=5.0, description="Zinc content (%)")
    copper_percent: Optional[float] = Field(None, ge=0.0, le=2.0, description="Copper content (%)")
    boron_percent: Optional[float] = Field(None, ge=0.0, le=1.0, description="Boron content (%)")
    molybdenum_percent: Optional[float] = Field(None, ge=0.0, le=0.1, description="Molybdenum content (%)")


class FertilizerProduct(BaseModel):
    """Individual fertilizer product information."""
    product_id: str = Field(..., description="Unique product identifier")
    name: str = Field(..., description="Product name")
    manufacturer: Optional[str] = Field(None, description="Manufacturer name")
    fertilizer_type: FertilizerType = Field(..., description="Type of fertilizer")
    release_pattern: ReleasePattern = Field(..., description="Nutrient release pattern")
    
    # Nutrient content
    nutrient_content: NutrientContent = Field(..., description="Primary nutrient content")
    micronutrients: Optional[MicronutrientContent] = Field(None, description="Micronutrient content")
    
    # Cost and availability
    cost_per_unit: float = Field(..., gt=0, description="Cost per unit ($/ton or $/gallon)")
    unit_size: float = Field(..., gt=0, description="Unit size (lbs or gallons)")
    unit_type: str = Field(..., description="Unit type (ton, bag, gallon)")
    
    # Application information
    application_methods: List[ApplicationMethod] = Field(..., description="Compatible application methods")
    equipment_requirements: List[str] = Field(..., description="Required equipment")
    application_rate_range: Dict[str, float] = Field(..., description="Application rate range (lbs/acre)")
    
    # Characteristics
    organic_certified: bool = Field(default=False, description="Organic certification status")
    slow_release: bool = Field(default=False, description="Slow release formulation")
    water_soluble: bool = Field(default=False, description="Water soluble")
    
    # Impact scores (0-1 scale)
    environmental_impact_score: float = Field(..., ge=0.0, le=1.0, description="Environmental impact (0=high impact, 1=low impact)")
    soil_health_score: float = Field(..., ge=0.0, le=1.0, description="Soil health benefit (0=no benefit, 1=high benefit)")
    
    # Benefits and limitations
    soil_health_benefits: List[str] = Field(default=[], description="Soil health benefits")
    pros: List[str] = Field(..., description="Product advantages")
    cons: List[str] = Field(..., description="Product limitations")
    application_notes: List[str] = Field(default=[], description="Application guidance")
    
    # Storage and handling
    storage_requirements: Optional[str] = Field(None, description="Storage requirements")
    shelf_life_months: Optional[int] = Field(None, ge=0, description="Shelf life in months")
    safety_considerations: List[str] = Field(default=[], description="Safety considerations")


class FarmerPriorities(BaseModel):
    """Farmer priorities for fertilizer selection."""
    cost_effectiveness: float = Field(..., ge=0.0, le=1.0, description="Cost effectiveness priority (0-1)")
    soil_health: float = Field(..., ge=0.0, le=1.0, description="Soil health priority (0-1)")
    quick_results: float = Field(..., ge=0.0, le=1.0, description="Quick results priority (0-1)")
    environmental_impact: float = Field(..., ge=0.0, le=1.0, description="Environmental impact priority (0-1)")
    ease_of_application: float = Field(..., ge=0.0, le=1.0, description="Ease of application priority (0-1)")
    long_term_benefits: float = Field(..., ge=0.0, le=1.0, description="Long-term benefits priority (0-1)")
    
    @validator('*', pre=True)
    def validate_priority_sum(cls, v, values):
        """Ensure priorities are reasonable (don't need to sum to 1.0)."""
        if isinstance(v, (int, float)) and (v < 0 or v > 1):
            raise ValueError("Priority values must be between 0 and 1")
        return v


class FarmerConstraints(BaseModel):
    """Farmer constraints and limitations."""
    budget_per_acre: Optional[float] = Field(None, gt=0, description="Budget per acre ($)")
    total_budget: Optional[float] = Field(None, gt=0, description="Total fertilizer budget ($)")
    farm_size_acres: float = Field(..., gt=0, description="Farm size in acres")
    
    # Equipment constraints
    available_equipment: List[str] = Field(..., description="Available equipment")
    equipment_limitations: Optional[List[str]] = Field(None, description="Equipment limitations")
    
    # Operational constraints
    application_window_days: Optional[int] = Field(None, gt=0, description="Available application window (days)")
    labor_availability: Optional[str] = Field(None, description="Labor availability (high, medium, low)")
    storage_capacity: Optional[str] = Field(None, description="Storage capacity limitations")
    
    # Preferences
    organic_preference: bool = Field(default=False, description="Preference for organic fertilizers")
    environmental_concerns: bool = Field(default=False, description="Environmental concerns priority")
    soil_health_focus: bool = Field(default=False, description="Soil health focus")
    
    # Regulatory constraints
    organic_certification_required: bool = Field(default=False, description="Organic certification required")
    nutrient_management_plan: bool = Field(default=False, description="Under nutrient management plan")
    water_quality_restrictions: bool = Field(default=False, description="Water quality restrictions apply")


class SoilHealthStatus(BaseModel):
    """Current soil health status."""
    organic_matter_percent: float = Field(..., ge=0.0, le=15.0, description="Organic matter content (%)")
    soil_health_score: Optional[float] = Field(None, ge=0.0, le=10.0, description="Overall soil health score (0-10)")
    compaction_issues: bool = Field(default=False, description="Soil compaction issues present")
    erosion_risk: Optional[str] = Field(None, description="Erosion risk level (low, medium, high)")
    biological_activity: Optional[str] = Field(None, description="Biological activity level (low, medium, high)")
    nutrient_cycling_efficiency: Optional[float] = Field(None, ge=0.0, le=1.0, description="Nutrient cycling efficiency")


class CostAnalysis(BaseModel):
    """Cost analysis for fertilizer options."""
    cost_per_acre: float = Field(..., description="Cost per acre ($)")
    cost_per_nutrient_unit: Dict[str, float] = Field(..., description="Cost per nutrient unit ($/lb)")
    total_farm_cost: float = Field(..., description="Total cost for entire farm ($)")
    application_cost: float = Field(..., description="Application cost per acre ($)")
    total_cost_including_application: float = Field(..., description="Total cost including application ($)")
    
    # Economic analysis
    roi_estimate_percent: Optional[float] = Field(None, description="Estimated ROI (%)")
    payback_period_years: Optional[float] = Field(None, description="Payback period (years)")
    break_even_yield_increase: Optional[float] = Field(None, description="Break-even yield increase (%)")


class EnvironmentalImpact(BaseModel):
    """Environmental impact assessment."""
    carbon_footprint_score: float = Field(..., ge=0.0, le=1.0, description="Carbon footprint (0=high, 1=low)")
    water_quality_impact: float = Field(..., ge=0.0, le=1.0, description="Water quality impact (0=high risk, 1=low risk)")
    soil_health_impact: float = Field(..., ge=0.0, le=1.0, description="Soil health impact (0=negative, 1=positive)")
    biodiversity_impact: float = Field(..., ge=0.0, le=1.0, description="Biodiversity impact (0=negative, 1=positive)")
    
    # Specific impacts
    runoff_risk: str = Field(..., description="Runoff risk level (low, medium, high)")
    leaching_potential: str = Field(..., description="Leaching potential (low, medium, high)")
    volatilization_risk: str = Field(..., description="Volatilization risk (low, medium, high)")
    
    # Mitigation strategies
    mitigation_strategies: List[str] = Field(default=[], description="Environmental mitigation strategies")
    best_practices: List[str] = Field(default=[], description="Environmental best practices")


class FertilizerRecommendation(BaseModel):
    """Individual fertilizer recommendation."""
    product: FertilizerProduct = Field(..., description="Recommended fertilizer product")
    suitability_score: float = Field(..., ge=0.0, le=1.0, description="Overall suitability score")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in recommendation")
    
    # Application details
    recommended_rate_lbs_per_acre: float = Field(..., gt=0, description="Recommended application rate (lbs/acre)")
    application_timing: str = Field(..., description="Recommended application timing")
    application_method: ApplicationMethod = Field(..., description="Recommended application method")
    
    # Analysis
    cost_analysis: CostAnalysis = Field(..., description="Cost analysis")
    environmental_impact: EnvironmentalImpact = Field(..., description="Environmental impact assessment")
    
    # Farmer-specific pros and cons
    pros_for_farmer: List[str] = Field(..., description="Advantages for this specific farmer")
    cons_for_farmer: List[str] = Field(..., description="Disadvantages for this specific farmer")
    
    # Implementation guidance
    equipment_needed: List[str] = Field(..., description="Required equipment")
    implementation_steps: List[str] = Field(..., description="Implementation steps")
    monitoring_recommendations: List[str] = Field(default=[], description="Monitoring recommendations")
    
    # Supporting information
    agricultural_sources: List[str] = Field(..., description="Supporting agricultural sources")
    expert_notes: Optional[str] = Field(None, description="Expert notes and considerations")


class FertilizerTypeSelectionRequest(BaseModel):
    """Request for fertilizer type selection recommendations."""
    request_id: str = Field(..., description="Unique request identifier")
    
    # Farmer input
    priorities: FarmerPriorities = Field(..., description="Farmer priorities")
    constraints: FarmerConstraints = Field(..., description="Farmer constraints")
    
    # Context data
    soil_data: Optional[Dict[str, Any]] = Field(None, description="Soil test data")
    crop_data: Optional[Dict[str, Any]] = Field(None, description="Crop information")
    farm_profile: Optional[Dict[str, Any]] = Field(None, description="Farm profile")
    soil_health_status: Optional[SoilHealthStatus] = Field(None, description="Current soil health status")
    
    # Additional context
    current_fertilizer_program: Optional[Dict[str, Any]] = Field(None, description="Current fertilizer program")
    performance_goals: Optional[Dict[str, Any]] = Field(None, description="Performance goals")
    sustainability_goals: Optional[List[str]] = Field(None, description="Sustainability goals")


class ComparisonSummary(BaseModel):
    """Summary of fertilizer type comparison."""
    top_recommendation: str = Field(..., description="Top recommended fertilizer type")
    key_differentiators: List[str] = Field(..., description="Key differentiating factors")
    trade_offs: Dict[str, str] = Field(..., description="Key trade-offs between options")
    decision_factors: List[str] = Field(..., description="Most important decision factors")


class FertilizerTypeSelectionResponse(BaseModel):
    """Response for fertilizer type selection recommendations."""
    request_id: str = Field(..., description="Original request identifier")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
    
    # Recommendations
    recommendations: List[FertilizerRecommendation] = Field(..., description="Fertilizer recommendations")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Overall confidence score")
    
    # Analysis summaries
    comparison_summary: ComparisonSummary = Field(..., description="Comparison summary")
    cost_analysis: Dict[str, Any] = Field(..., description="Overall cost analysis")
    environmental_impact: Dict[str, Any] = Field(..., description="Environmental impact summary")
    
    # Implementation guidance
    implementation_guidance: List[str] = Field(..., description="Implementation guidance")
    timing_recommendations: List[str] = Field(default=[], description="Timing recommendations")
    monitoring_plan: Optional[List[str]] = Field(None, description="Monitoring plan")
    
    # Additional information
    warnings: Optional[List[str]] = Field(None, description="Important warnings")
    next_steps: Optional[List[str]] = Field(None, description="Recommended next steps")
    follow_up_questions: Optional[List[str]] = Field(None, description="Follow-up questions")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }


class FertilizerComparisonRequest(BaseModel):
    """Request for comparing specific fertilizer options."""
    request_id: str = Field(..., description="Unique request identifier")
    fertilizer_ids: List[str] = Field(..., min_items=2, description="Fertilizer product IDs to compare")
    comparison_criteria: List[str] = Field(..., description="Criteria for comparison")
    farm_context: Dict[str, Any] = Field(..., description="Farm context for comparison")


class ComparisonResult(BaseModel):
    """Result of fertilizer comparison."""
    fertilizer_id: str = Field(..., description="Fertilizer product ID")
    scores: Dict[str, float] = Field(..., description="Scores for each comparison criterion")
    overall_score: float = Field(..., ge=0.0, le=1.0, description="Overall comparison score")
    strengths: List[str] = Field(..., description="Strengths of this option")
    weaknesses: List[str] = Field(..., description="Weaknesses of this option")


class FertilizerComparisonResponse(BaseModel):
    """Response for fertilizer comparison."""
    request_id: str = Field(..., description="Original request identifier")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
    
    comparison_results: List[ComparisonResult] = Field(..., description="Comparison results")
    recommendation: str = Field(..., description="Overall recommendation")
    decision_factors: List[str] = Field(..., description="Key decision factors")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }
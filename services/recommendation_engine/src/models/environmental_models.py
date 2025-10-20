"""
Environmental Impact Assessment Data Models

Pydantic models for environmental impact assessment including carbon footprint,
water quality impact, soil health effects, biodiversity impact, and lifecycle analysis.
Implements comprehensive environmental assessment for fertilizer selection.

Agricultural References:
- IPCC (2019): Refinement to the 2006 IPCC Guidelines for National Greenhouse Gas Inventories
- Bouwman et al. (2002): Emissions of N2O and NO from fertilized fields
- Galloway et al. (2008): Transformation of the Nitrogen Cycle
- Carpenter et al. (2008): Nonpoint pollution of surface waters with phosphorus and nitrogen
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


class FertilizerCategory(str, Enum):
    """Categories of fertilizers for environmental assessment."""
    SYNTHETIC_NITROGEN = "synthetic_nitrogen"
    SYNTHETIC_PHOSPHORUS = "synthetic_phosphorus"
    SYNTHETIC_POTASSIUM = "synthetic_potassium"
    ORGANIC_ANIMAL_MANURE = "organic_animal_manure"
    ORGANIC_COMPOST = "organic_compost"
    ORGANIC_GREEN_MANURE = "organic_green_manure"
    SLOW_RELEASE_COATED = "slow_release_coated"
    SLOW_RELEASE_POLYMER = "slow_release_polymer"
    BIOFERTILIZER = "biofertilizer"


class ImpactCategory(str, Enum):
    """Environmental impact categories."""
    GREENHOUSE_GAS = "greenhouse_gas"
    WATER_POLLUTION = "water_pollution"
    SOIL_ACIDIFICATION = "soil_acidification"
    EUTROPHICATION = "eutrophication"
    BIODIVERSITY = "biodiversity"
    ENERGY_USE = "energy_use"
    RESOURCE_DEPLETION = "resource_depletion"


class SeverityLevel(str, Enum):
    """Severity levels for environmental impacts."""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class LifecycleStage(str, Enum):
    """Stages in fertilizer lifecycle."""
    RAW_MATERIAL_EXTRACTION = "raw_material_extraction"
    MANUFACTURING = "manufacturing"
    PACKAGING = "packaging"
    TRANSPORTATION = "transportation"
    STORAGE = "storage"
    APPLICATION = "application"
    IN_FIELD_TRANSFORMATION = "in_field_transformation"
    END_OF_LIFE = "end_of_life"


class CarbonFootprint(BaseModel):
    """
    Carbon footprint assessment for fertilizer.

    Based on IPCC guidelines and agricultural research on GHG emissions
    from fertilizer production and use.
    """
    # Production emissions
    production_emissions_kg_co2e_per_kg: float = Field(
        ..., ge=0.0, description="CO2 equivalent emissions from production (kg CO2e/kg fertilizer)"
    )

    # Transportation emissions
    transport_emissions_kg_co2e_per_kg: Optional[float] = Field(
        None, ge=0.0, description="Emissions from transportation (kg CO2e/kg fertilizer)"
    )
    transport_distance_km: Optional[float] = Field(
        None, ge=0.0, description="Transportation distance (km)"
    )

    # Application emissions
    application_emissions_kg_co2e_per_acre: float = Field(
        ..., ge=0.0, description="Emissions from application equipment (kg CO2e/acre)"
    )

    # N2O emissions (major contributor for nitrogen fertilizers)
    n2o_emissions_kg_co2e_per_kg_n: float = Field(
        ..., ge=0.0, description="N2O emissions from applied nitrogen (kg CO2e/kg N)"
    )
    n2o_emission_factor: float = Field(
        ..., ge=0.0, le=0.10, description="N2O emission factor (default 0.01 = 1% of applied N)"
    )

    # Carbon sequestration potential (negative emissions for organic amendments)
    carbon_sequestration_kg_co2e_per_kg: Optional[float] = Field(
        None, description="Carbon sequestration potential (negative value = CO2 removal)"
    )

    # Total lifecycle emissions
    total_emissions_kg_co2e_per_kg: float = Field(
        ..., ge=0.0, description="Total lifecycle emissions (kg CO2e/kg fertilizer)"
    )
    total_emissions_kg_co2e_per_acre: float = Field(
        ..., ge=0.0, description="Total emissions per acre (kg CO2e/acre)"
    )

    # Impact rating
    carbon_impact_score: float = Field(
        ..., ge=0.0, le=100.0, description="Carbon impact score (0=worst, 100=best)"
    )
    severity_level: SeverityLevel = Field(..., description="Overall severity level")

    # Contributing factors
    primary_emission_sources: List[str] = Field(..., description="Primary emission sources")
    mitigation_potential_percent: float = Field(
        ..., ge=0.0, le=100.0, description="Potential emission reduction (%)"
    )


class WaterQualityImpact(BaseModel):
    """
    Water quality impact assessment.

    Based on research on nutrient runoff, leaching, and water pollution from
    agricultural fertilizers (Carpenter et al., 2008; Galloway et al., 2008).
    """
    # Nitrogen impacts
    nitrate_leaching_risk_score: float = Field(
        ..., ge=0.0, le=1.0, description="Nitrate leaching risk (0=low, 1=high)"
    )
    nitrate_leaching_potential_lbs_n_per_acre: float = Field(
        ..., ge=0.0, description="Potential nitrate leaching (lbs N/acre)"
    )

    # Phosphorus impacts
    phosphorus_runoff_risk_score: float = Field(
        ..., ge=0.0, le=1.0, description="P runoff risk (0=low, 1=high)"
    )
    phosphorus_runoff_potential_lbs_p2o5_per_acre: float = Field(
        ..., ge=0.0, description="Potential P runoff (lbs P2O5/acre)"
    )

    # Eutrophication potential
    eutrophication_potential_score: float = Field(
        ..., ge=0.0, le=10.0, description="Eutrophication potential score (0-10)"
    )

    # Groundwater contamination risk
    groundwater_contamination_risk: SeverityLevel = Field(
        ..., description="Groundwater contamination risk level"
    )

    # Surface water pollution risk
    surface_water_pollution_risk: SeverityLevel = Field(
        ..., description="Surface water pollution risk level"
    )

    # Water quality impact score
    water_quality_impact_score: float = Field(
        ..., ge=0.0, le=100.0, description="Water quality impact score (0=worst, 100=best)"
    )

    # Risk factors
    primary_risk_factors: List[str] = Field(..., description="Primary water quality risk factors")
    secondary_risk_factors: List[str] = Field(default=[], description="Secondary risk factors")

    # Vulnerable water bodies
    distance_to_surface_water_m: Optional[float] = Field(
        None, ge=0.0, description="Distance to nearest surface water (m)"
    )
    in_wellhead_protection_area: bool = Field(
        default=False, description="Within wellhead protection area"
    )


class SoilHealthImpact(BaseModel):
    """
    Soil health impact assessment.

    Evaluates effects on soil pH, salinity, organic matter, microbial activity,
    and long-term soil degradation.
    """
    # Soil acidification
    acidification_potential: float = Field(
        ..., description="Acidification potential (negative = acidifying, positive = alkalizing)"
    )
    ph_change_estimate: float = Field(
        ..., ge=-2.0, le=2.0, description="Estimated pH change over time"
    )
    lime_requirement_lbs_per_acre: Optional[float] = Field(
        None, ge=0.0, description="Lime needed to neutralize acidification (lbs/acre)"
    )

    # Salinity impact
    salt_index: float = Field(
        ..., ge=0.0, description="Salt index (relative salinity impact)"
    )
    soil_salinity_risk: SeverityLevel = Field(..., description="Soil salinity risk level")

    # Organic matter effects
    organic_matter_contribution_lbs_per_acre: float = Field(
        ..., ge=0.0, description="Organic matter added (lbs/acre)"
    )
    organic_matter_effect: str = Field(
        ..., description="Effect on soil organic matter (positive, neutral, negative)"
    )

    # Microbial activity
    microbial_activity_impact: str = Field(
        ..., description="Impact on soil microbiome (beneficial, neutral, harmful)"
    )
    microbial_impact_score: float = Field(
        ..., ge=0.0, le=10.0, description="Microbial impact score (0=harmful, 10=very beneficial)"
    )

    # Soil structure
    soil_structure_effect: str = Field(
        ..., description="Effect on soil structure (improves, neutral, degrades)"
    )
    aggregation_impact: Optional[str] = Field(
        None, description="Impact on soil aggregation"
    )

    # Long-term degradation risk
    long_term_degradation_risk: SeverityLevel = Field(
        ..., description="Long-term soil degradation risk"
    )

    # Overall soil health score
    soil_health_impact_score: float = Field(
        ..., ge=0.0, le=100.0, description="Soil health impact score (0=worst, 100=best)"
    )

    # Key impacts
    positive_impacts: List[str] = Field(default=[], description="Positive soil health impacts")
    negative_impacts: List[str] = Field(default=[], description="Negative soil health impacts")


class BiodiversityImpact(BaseModel):
    """
    Biodiversity impact assessment.

    Evaluates effects on beneficial insects, soil organisms, pollinators,
    and aquatic ecosystems.
    """
    # Beneficial insect impacts
    beneficial_insect_impact: str = Field(
        ..., description="Impact on beneficial insects (positive, neutral, negative)"
    )
    pollinator_safety_score: float = Field(
        ..., ge=0.0, le=10.0, description="Pollinator safety score (0=harmful, 10=safe)"
    )

    # Soil organism impacts
    earthworm_impact: str = Field(
        ..., description="Impact on earthworms (beneficial, neutral, harmful)"
    )
    beneficial_microbe_impact: str = Field(
        ..., description="Impact on beneficial microbes (beneficial, neutral, harmful)"
    )
    soil_fauna_impact_score: float = Field(
        ..., ge=0.0, le=10.0, description="Soil fauna impact score (0=harmful, 10=beneficial)"
    )

    # Aquatic ecosystem impacts
    aquatic_toxicity_score: float = Field(
        ..., ge=0.0, le=10.0, description="Aquatic toxicity (0=highly toxic, 10=safe)"
    )
    fish_impact: SeverityLevel = Field(..., description="Impact on fish populations")
    aquatic_invertebrate_impact: SeverityLevel = Field(
        ..., description="Impact on aquatic invertebrates"
    )

    # Habitat effects
    habitat_disruption_risk: SeverityLevel = Field(
        ..., description="Risk of habitat disruption"
    )

    # Overall biodiversity score
    biodiversity_impact_score: float = Field(
        ..., ge=0.0, le=100.0, description="Biodiversity impact score (0=worst, 100=best)"
    )

    # Specific concerns
    species_of_concern: List[str] = Field(default=[], description="Species particularly at risk")
    protective_measures_needed: List[str] = Field(
        default=[], description="Protective measures needed"
    )


class LifecycleImpact(BaseModel):
    """Impact at a specific lifecycle stage."""
    stage: LifecycleStage = Field(..., description="Lifecycle stage")
    stage_name: str = Field(..., description="Human-readable stage name")

    # Emissions and impacts
    co2e_emissions_kg: float = Field(..., ge=0.0, description="CO2e emissions (kg)")
    energy_use_mj: float = Field(..., ge=0.0, description="Energy use (MJ)")
    water_use_liters: Optional[float] = Field(None, ge=0.0, description="Water use (liters)")

    # Resource use
    non_renewable_resources: List[str] = Field(default=[], description="Non-renewable resources used")

    # Percentage of total impact
    percent_of_total_impact: float = Field(
        ..., ge=0.0, le=100.0, description="Percentage of total lifecycle impact"
    )

    # Key contributors
    key_impact_contributors: List[str] = Field(..., description="Key contributors to impact")


class LifecycleAssessment(BaseModel):
    """
    Comprehensive lifecycle assessment (LCA) for fertilizer.

    Cradle-to-grave analysis from raw material extraction through application
    and field transformations.
    """
    fertilizer_name: str = Field(..., description="Fertilizer product name")
    fertilizer_category: FertilizerCategory = Field(..., description="Fertilizer category")
    functional_unit: str = Field(
        default="per kg of fertilizer applied", description="LCA functional unit"
    )

    # Lifecycle stages
    lifecycle_impacts: List[LifecycleImpact] = Field(..., description="Impacts by lifecycle stage")

    # Total impacts
    total_co2e_kg: float = Field(..., ge=0.0, description="Total lifecycle CO2e emissions (kg)")
    total_energy_mj: float = Field(..., ge=0.0, description="Total lifecycle energy use (MJ)")
    total_water_liters: Optional[float] = Field(
        None, ge=0.0, description="Total lifecycle water use (liters)"
    )

    # Dominant stages
    dominant_impact_stage: LifecycleStage = Field(
        ..., description="Lifecycle stage with highest impact"
    )
    dominant_stage_percent: float = Field(
        ..., ge=0.0, le=100.0, description="Percentage of impact from dominant stage"
    )

    # Improvement opportunities
    improvement_opportunities: List[str] = Field(
        ..., description="Opportunities to reduce lifecycle impact"
    )

    # LCA methodology
    methodology_standard: str = Field(
        default="ISO 14040:2006", description="LCA methodology standard"
    )
    data_quality_score: float = Field(
        ..., ge=0.0, le=10.0, description="Data quality score (0=poor, 10=excellent)"
    )
    uncertainty_range_percent: Optional[float] = Field(
        None, ge=0.0, description="Uncertainty range as percentage"
    )


class EnvironmentalScore(BaseModel):
    """
    Aggregated environmental scoring system.

    Multi-criteria scoring that combines all environmental impact categories
    into an overall sustainability rating (0-100 scale).
    """
    # Individual category scores (0-100, higher = better for environment)
    carbon_footprint_score: float = Field(
        ..., ge=0.0, le=100.0, description="Carbon footprint score"
    )
    water_quality_score: float = Field(
        ..., ge=0.0, le=100.0, description="Water quality score"
    )
    soil_health_score: float = Field(
        ..., ge=0.0, le=100.0, description="Soil health score"
    )
    biodiversity_score: float = Field(
        ..., ge=0.0, le=100.0, description="Biodiversity score"
    )

    # Weighted overall score
    overall_environmental_score: float = Field(
        ..., ge=0.0, le=100.0, description="Overall environmental score (weighted average)"
    )

    # Weighting factors used
    weighting_scheme: Dict[str, float] = Field(
        ..., description="Weighting factors for each category"
    )

    # Rating category
    environmental_rating: str = Field(
        ..., description="Overall rating (Excellent, Good, Fair, Poor, Very Poor)"
    )

    # Strongest and weakest areas
    strongest_area: str = Field(..., description="Best performing environmental area")
    weakest_area: str = Field(..., description="Poorest performing environmental area")

    # Comparative ranking
    percentile_rank: Optional[float] = Field(
        None, ge=0.0, le=100.0, description="Percentile rank compared to other fertilizers"
    )

    # Certification potential
    organic_certification_eligible: bool = Field(
        default=False, description="Eligible for organic certification"
    )
    sustainability_certification_potential: List[str] = Field(
        default=[], description="Potential sustainability certifications"
    )


class MitigationRecommendation(BaseModel):
    """
    Recommendation to reduce environmental impact.

    Specific, actionable recommendations to minimize environmental harm
    while maintaining agronomic effectiveness.
    """
    recommendation_id: str = Field(..., description="Unique recommendation ID")
    category: ImpactCategory = Field(..., description="Impact category addressed")
    priority: str = Field(..., description="Priority level (High, Medium, Low)")

    # Recommendation details
    recommendation: str = Field(..., description="Specific recommendation")
    rationale: str = Field(..., description="Why this recommendation is effective")

    # Expected benefits
    impact_reduction_percent: float = Field(
        ..., ge=0.0, le=100.0, description="Expected impact reduction (%)"
    )
    environmental_benefit: str = Field(..., description="Expected environmental benefit")

    # Implementation details
    implementation_difficulty: str = Field(
        ..., description="Implementation difficulty (Easy, Moderate, Difficult)"
    )
    cost_implication: str = Field(
        ..., description="Cost implication (Cost savings, Neutral, Additional cost)"
    )
    equipment_needed: List[str] = Field(default=[], description="Equipment or resources needed")

    # Agronomic considerations
    agronomic_trade_offs: List[str] = Field(
        default=[], description="Potential agronomic trade-offs"
    )
    effectiveness_conditions: List[str] = Field(
        default=[], description="Conditions for maximum effectiveness"
    )

    # Supporting information
    research_support: List[str] = Field(
        default=[], description="Supporting research or guidelines"
    )


class EnvironmentalImpactData(BaseModel):
    """
    Comprehensive environmental impact assessment data.

    Complete environmental assessment combining carbon footprint, water quality,
    soil health, biodiversity, and lifecycle impacts.
    """
    assessment_id: str = Field(..., description="Unique assessment ID")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Assessment timestamp")

    # Fertilizer information
    fertilizer_name: str = Field(..., description="Fertilizer product name")
    fertilizer_type: str = Field(..., description="Fertilizer type")
    fertilizer_category: FertilizerCategory = Field(..., description="Fertilizer category")

    # Application context
    application_rate_lbs_per_acre: float = Field(..., gt=0.0, description="Application rate (lbs/acre)")
    farm_acreage: Optional[float] = Field(None, gt=0.0, description="Farm size (acres)")

    # Detailed impact assessments
    carbon_footprint: CarbonFootprint = Field(..., description="Carbon footprint assessment")
    water_quality_impact: WaterQualityImpact = Field(..., description="Water quality impact")
    soil_health_impact: SoilHealthImpact = Field(..., description="Soil health impact")
    biodiversity_impact: BiodiversityImpact = Field(..., description="Biodiversity impact")

    # Lifecycle assessment (optional, may not be available for all products)
    lifecycle_assessment: Optional[LifecycleAssessment] = Field(
        None, description="Lifecycle assessment"
    )

    # Overall environmental score
    environmental_score: EnvironmentalScore = Field(..., description="Overall environmental score")

    # Mitigation recommendations
    mitigation_recommendations: List[MitigationRecommendation] = Field(
        ..., description="Recommendations to reduce impact"
    )

    # Regulatory compliance
    regulatory_compliance: Dict[str, Any] = Field(
        default={}, description="Regulatory compliance status"
    )

    # Comparative analysis
    relative_to_alternatives: Optional[str] = Field(
        None, description="Comparison to alternative fertilizers"
    )

    # Data quality and confidence
    assessment_confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence in assessment (0-1)"
    )
    data_sources: List[str] = Field(..., description="Data sources used")
    limitations: List[str] = Field(default=[], description="Assessment limitations")

    # Agricultural sources
    agricultural_sources: List[str] = Field(
        default=[], description="Supporting agricultural research"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EnvironmentalComparisonResult(BaseModel):
    """
    Result of comparing environmental impacts across multiple fertilizer options.

    Provides side-by-side comparison to help farmers choose the most
    environmentally friendly option.
    """
    comparison_id: str = Field(..., description="Unique comparison ID")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Comparison timestamp")

    # Fertilizers compared
    fertilizer_assessments: List[EnvironmentalImpactData] = Field(
        ..., min_items=2, description="Environmental assessments for each fertilizer"
    )

    # Rankings
    carbon_footprint_ranking: List[str] = Field(
        ..., description="Fertilizers ranked by carbon footprint (best to worst)"
    )
    water_quality_ranking: List[str] = Field(
        ..., description="Fertilizers ranked by water quality impact (best to worst)"
    )
    soil_health_ranking: List[str] = Field(
        ..., description="Fertilizers ranked by soil health impact (best to worst)"
    )
    biodiversity_ranking: List[str] = Field(
        ..., description="Fertilizers ranked by biodiversity impact (best to worst)"
    )
    overall_ranking: List[str] = Field(
        ..., description="Fertilizers ranked by overall environmental score (best to worst)"
    )

    # Best choice
    recommended_fertilizer: str = Field(
        ..., description="Most environmentally friendly option"
    )
    recommendation_rationale: str = Field(
        ..., description="Why this fertilizer is recommended"
    )

    # Key differences
    key_differentiators: List[str] = Field(
        ..., description="Key environmental differences between options"
    )

    # Trade-offs
    environmental_trade_offs: Dict[str, str] = Field(
        ..., description="Trade-offs between environmental factors"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

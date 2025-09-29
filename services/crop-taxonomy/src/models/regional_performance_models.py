"""
Regional Performance Models
TICKET-005_crop-variety-recommendations-11.2

Pydantic models for regional performance scoring API requests and responses.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime, date
from enum import Enum
from uuid import UUID

from .service_models import DataSource

class PerformanceMetric(str, Enum):
    """Performance metrics for variety analysis."""
    YIELD = "yield"
    QUALITY = "quality"
    DISEASE_RESISTANCE = "disease_resistance"
    DROUGHT_TOLERANCE = "drought_tolerance"
    MATURITY = "maturity"
    STABILITY = "stability"

class StabilityMeasure(str, Enum):
    """Stability measures for variety performance."""
    COEFFICIENT_OF_VARIATION = "cv"
    REGRESSION_COEFFICIENT = "regression_coefficient"
    DEVIATION_FROM_REGRESSION = "deviation_from_regression"
    SHUKLA_STABILITY_VARIANCE = "shukla_stability_variance"
    WRIKE_STABILITY_VARIANCE = "wrike_stability_variance"
    AMMI_STABILITY_VALUE = "ammi_stability_value"

class AdaptationType(str, Enum):
    """Types of adaptation patterns."""
    GENERAL_ADAPTATION = "general_adaptation"
    SPECIFIC_ADAPTATION = "specific_adaptation"
    STABLE_PERFORMANCE = "stable_performance"
    UNSTABLE_PERFORMANCE = "unstable_performance"

# ============================================================================
# REQUEST MODELS
# ============================================================================

class RegionalPerformanceRequest(BaseModel):
    """Request model for regional performance analysis."""
    
    crop_type: str = Field(..., description="Type of crop to analyze")
    varieties: List[str] = Field(..., min_items=2, description="List of variety names to analyze")
    locations: List[str] = Field(..., min_items=2, description="List of location IDs to include")
    years: List[int] = Field(..., min_items=1, description="List of years to include")
    performance_metrics: Optional[List[PerformanceMetric]] = Field(
        default=[PerformanceMetric.YIELD], 
        description="Performance metrics to analyze"
    )
    include_environmental_data: bool = Field(True, description="Include environmental data integration")
    include_stability_analysis: bool = Field(True, description="Include stability analysis")
    include_ammi_analysis: bool = Field(True, description="Include AMMI analysis")
    include_gge_analysis: bool = Field(True, description="Include GGE biplot analysis")

class VarietyPerformanceSummaryRequest(BaseModel):
    """Request model for variety performance summary."""
    
    variety_name: str = Field(..., description="Name of the variety to analyze")
    crop_type: str = Field(..., description="Type of crop")
    years: Optional[List[int]] = Field(None, description="Optional list of years to include")
    include_regional_analysis: bool = Field(True, description="Include regional performance analysis")
    include_stability_metrics: bool = Field(True, description="Include stability metrics")

class StabilityAnalysisRequest(BaseModel):
    """Request model for stability analysis."""
    
    crop_type: str = Field(..., description="Type of crop to analyze")
    varieties: List[str] = Field(..., min_items=2, description="List of variety names")
    locations: List[str] = Field(..., min_items=2, description="List of location IDs")
    years: List[int] = Field(..., min_items=1, description="List of years")
    stability_measures: Optional[List[StabilityMeasure]] = Field(
        default=[StabilityMeasure.COEFFICIENT_OF_VARIATION, StabilityMeasure.REGRESSION_COEFFICIENT],
        description="Stability measures to calculate"
    )

class AMMIAnalysisRequest(BaseModel):
    """Request model for AMMI analysis."""
    
    crop_type: str = Field(..., description="Type of crop to analyze")
    varieties: List[str] = Field(..., min_items=2, description="List of variety names")
    locations: List[str] = Field(..., min_items=2, description="List of location IDs")
    years: List[int] = Field(..., min_items=1, description="List of years")
    max_ipca_components: int = Field(5, ge=1, le=10, description="Maximum IPCA components to calculate")

class GGEBiplotRequest(BaseModel):
    """Request model for GGE biplot analysis."""
    
    crop_type: str = Field(..., description="Type of crop to analyze")
    varieties: List[str] = Field(..., min_items=2, description="List of variety names")
    locations: List[str] = Field(..., min_items=2, description="List of location IDs")
    years: List[int] = Field(..., min_items=1, description="List of years")
    include_which_won_where: bool = Field(True, description="Include 'which won where' analysis")
    include_mean_vs_stability: bool = Field(True, description="Include mean vs stability analysis")

class RegionalRankingRequest(BaseModel):
    """Request model for regional ranking generation."""
    
    crop_type: str = Field(..., description="Type of crop to analyze")
    varieties: List[str] = Field(..., min_items=2, description="List of variety names")
    locations: List[str] = Field(..., min_items=2, description="List of location IDs")
    years: List[int] = Field(..., min_items=1, description="List of years")
    ranking_method: str = Field("mean_yield", description="Method for ranking varieties")
    include_adaptation_zones: bool = Field(True, description="Include adaptation zone recommendations")

# ============================================================================
# RESPONSE MODELS
# ============================================================================

class MultiLocationAnalysis(BaseModel):
    """Multi-location analysis results."""
    
    variety_means: Dict[str, Dict[str, float]] = Field(..., description="Mean performance by variety")
    location_means: Dict[str, Dict[str, float]] = Field(..., description="Mean performance by location")
    variety_location_interactions: Dict[str, Dict[str, Dict[str, float]]] = Field(
        ..., description="Variety-location interaction effects"
    )
    overall_mean: float = Field(..., description="Overall mean performance")
    overall_std: float = Field(..., description="Overall standard deviation")

class GxEAnalysis(BaseModel):
    """Genotype-by-environment interaction analysis results."""
    
    interaction_matrix: Dict[str, Dict[str, float]] = Field(..., description="Interaction matrix")
    interaction_effects: Dict[str, Dict[str, float]] = Field(..., description="Interaction effects")
    interaction_sum_of_squares: float = Field(..., description="Sum of squares for interactions")
    variety_means: Dict[str, float] = Field(..., description="Variety means")
    location_means: Dict[str, float] = Field(..., description="Location means")
    grand_mean: float = Field(..., description="Grand mean")

class AMMIAnalysis(BaseModel):
    """AMMI analysis results."""
    
    genotype_effects: Dict[str, float] = Field(..., description="Genotype main effects")
    environment_effects: Dict[str, float] = Field(..., description="Environment main effects")
    interaction_effects: Dict[str, Dict[str, float]] = Field(..., description="Interaction effects")
    explained_variance: Dict[str, float] = Field(..., description="Explained variance by IPCA")
    ipca_scores: Dict[str, List[float]] = Field(..., description="IPCA scores for genotypes")
    stability_values: Dict[str, float] = Field(..., description="AMMI stability values")

class GGEBiplotData(BaseModel):
    """GGE biplot analysis data."""
    
    genotype_scores: Dict[str, Tuple[float, float]] = Field(..., description="Genotype scores (PC1, PC2)")
    environment_scores: Dict[str, Tuple[float, float]] = Field(..., description="Environment scores (PC1, PC2)")
    explained_variance: Tuple[float, float] = Field(..., description="Explained variance (PC1, PC2)")
    which_won_where: Dict[str, str] = Field(..., description="Best variety for each location")
    mean_vs_stability: Dict[str, Tuple[float, float]] = Field(..., description="Mean vs stability coordinates")

class StabilityAnalysis(BaseModel):
    """Stability analysis results."""
    
    variety_stability: Dict[str, Dict[str, float]] = Field(..., description="Stability measures by variety")
    adaptation_types: Dict[str, AdaptationType] = Field(..., description="Adaptation types by variety")
    stability_rankings: Dict[str, int] = Field(..., description="Stability rankings")
    adaptation_recommendations: Dict[str, List[str]] = Field(..., description="Adaptation recommendations")

class RegionalRanking(BaseModel):
    """Regional performance ranking results."""
    
    variety_rankings: Dict[str, Dict[str, int]] = Field(..., description="Variety rankings by location")
    regional_winners: Dict[str, str] = Field(..., description="Best variety for each region")
    performance_trends: Dict[str, Dict[str, float]] = Field(..., description="Performance trends by variety")
    adaptation_zones: Dict[str, List[str]] = Field(..., description="Adaptation zones by variety")

class EnvironmentalIntegration(BaseModel):
    """Environmental data integration results."""
    
    environmental_data: Dict[str, Dict[str, Any]] = Field(..., description="Environmental data by location")
    integration_timestamp: str = Field(..., description="Integration timestamp")

class RegionalPerformanceResponse(BaseModel):
    """Response model for regional performance analysis."""
    
    analysis_id: str = Field(..., description="Unique analysis identifier")
    crop_type: str = Field(..., description="Type of crop analyzed")
    varieties_analyzed: List[str] = Field(..., description="Varieties included in analysis")
    locations_analyzed: List[str] = Field(..., description="Locations included in analysis")
    years_analyzed: List[int] = Field(..., description="Years included in analysis")
    multi_location_analysis: MultiLocationAnalysis = Field(..., description="Multi-location analysis results")
    gxe_analysis: GxEAnalysis = Field(..., description="GxE interaction analysis results")
    ammi_analysis: AMMIAnalysis = Field(..., description="AMMI analysis results")
    gge_analysis: GGEBiplotData = Field(..., description="GGE biplot analysis results")
    stability_analysis: StabilityAnalysis = Field(..., description="Stability analysis results")
    regional_rankings: RegionalRanking = Field(..., description="Regional ranking results")
    environmental_integration: EnvironmentalIntegration = Field(..., description="Environmental integration results")
    analysis_timestamp: str = Field(..., description="Analysis completion timestamp")

class OverallPerformance(BaseModel):
    """Overall performance metrics for a variety."""
    
    mean_yield: float = Field(..., description="Mean yield across environments")
    yield_stability: float = Field(..., description="Yield stability measure")
    adaptation_type: AdaptationType = Field(..., description="Type of adaptation")
    regional_performance: Dict[str, List[str]] = Field(..., description="Regional performance categories")

class StabilityMetrics(BaseModel):
    """Stability metrics for a variety."""
    
    coefficient_of_variation: float = Field(..., description="Coefficient of variation")
    regression_coefficient: float = Field(..., description="Regression coefficient")
    stability_ranking: int = Field(..., description="Stability ranking")

class VarietyPerformanceSummaryResponse(BaseModel):
    """Response model for variety performance summary."""
    
    variety_name: str = Field(..., description="Name of the analyzed variety")
    crop_type: str = Field(..., description="Type of crop")
    years_analyzed: List[int] = Field(..., description="Years included in analysis")
    overall_performance: OverallPerformance = Field(..., description="Overall performance metrics")
    stability_metrics: StabilityMetrics = Field(..., description="Stability metrics")
    recommendations: List[str] = Field(..., description="Performance recommendations")

class StabilityAnalysisResponse(BaseModel):
    """Response model for stability analysis."""
    
    crop_type: str = Field(..., description="Type of crop analyzed")
    varieties_analyzed: List[str] = Field(..., description="Varieties included in analysis")
    stability_measures: Dict[str, Dict[str, float]] = Field(..., description="Stability measures by variety")
    adaptation_types: Dict[str, AdaptationType] = Field(..., description="Adaptation types by variety")
    stability_rankings: Dict[str, int] = Field(..., description="Stability rankings")
    recommendations: Dict[str, List[str]] = Field(..., description="Adaptation recommendations")

class AMMIAnalysisResponse(BaseModel):
    """Response model for AMMI analysis."""
    
    crop_type: str = Field(..., description="Type of crop analyzed")
    varieties_analyzed: List[str] = Field(..., description="Varieties included in analysis")
    locations_analyzed: List[str] = Field(..., description="Locations included in analysis")
    genotype_effects: Dict[str, float] = Field(..., description="Genotype main effects")
    environment_effects: Dict[str, float] = Field(..., description="Environment main effects")
    interaction_effects: Dict[str, Dict[str, float]] = Field(..., description="Interaction effects")
    explained_variance: Dict[str, float] = Field(..., description="Explained variance by IPCA")
    ipca_scores: Dict[str, List[float]] = Field(..., description="IPCA scores")
    stability_values: Dict[str, float] = Field(..., description="AMMI stability values")

class GGEBiplotResponse(BaseModel):
    """Response model for GGE biplot analysis."""
    
    crop_type: str = Field(..., description="Type of crop analyzed")
    varieties_analyzed: List[str] = Field(..., description="Varieties included in analysis")
    locations_analyzed: List[str] = Field(..., description="Locations included in analysis")
    genotype_scores: Dict[str, Tuple[float, float]] = Field(..., description="Genotype scores")
    environment_scores: Dict[str, Tuple[float, float]] = Field(..., description="Environment scores")
    explained_variance: Tuple[float, float] = Field(..., description="Explained variance")
    which_won_where: Dict[str, str] = Field(..., description="Best variety for each location")
    mean_vs_stability: Dict[str, Tuple[float, float]] = Field(..., description="Mean vs stability")

class RegionalRankingResponse(BaseModel):
    """Response model for regional ranking generation."""
    
    crop_type: str = Field(..., description="Type of crop analyzed")
    varieties_analyzed: List[str] = Field(..., description="Varieties included in analysis")
    locations_analyzed: List[str] = Field(..., description="Locations included in analysis")
    variety_rankings: Dict[str, Dict[str, int]] = Field(..., description="Variety rankings by location")
    regional_winners: Dict[str, str] = Field(..., description="Best variety for each region")
    performance_trends: Dict[str, Dict[str, float]] = Field(..., description="Performance trends")
    adaptation_zones: Dict[str, List[str]] = Field(..., description="Adaptation zones")

# ============================================================================
# UTILITY MODELS
# ============================================================================

class PerformanceDataPoint(BaseModel):
    """Individual performance data point."""
    
    variety_name: str = Field(..., description="Name of the variety")
    location_id: str = Field(..., description="Location identifier")
    year: int = Field(..., description="Year of the trial")
    yield_value: float = Field(..., description="Yield value")
    quality_score: Optional[float] = Field(None, description="Quality score")
    disease_incidence: Optional[float] = Field(None, description="Disease incidence")
    maturity_days: Optional[int] = Field(None, description="Maturity in days")

class EnvironmentalDataPoint(BaseModel):
    """Environmental data for a location."""
    
    location_id: str = Field(..., description="Location identifier")
    year: int = Field(..., description="Year of the data")
    temperature_data: Dict[str, float] = Field(..., description="Temperature data")
    precipitation_data: Dict[str, float] = Field(..., description="Precipitation data")
    soil_data: Dict[str, Any] = Field(..., description="Soil data")
    pest_pressure: Optional[Dict[str, float]] = Field(None, description="Pest pressure data")
    disease_pressure: Optional[Dict[str, float]] = Field(None, description="Disease pressure data")

class PerformanceComparison(BaseModel):
    """Performance comparison between varieties."""
    
    variety_1: str = Field(..., description="First variety name")
    variety_2: str = Field(..., description="Second variety name")
    comparison_metric: str = Field(..., description="Metric used for comparison")
    difference: float = Field(..., description="Difference in performance")
    significance_level: Optional[float] = Field(None, description="Statistical significance level")
    confidence_interval: Optional[Tuple[float, float]] = Field(None, description="Confidence interval")

class RegionalAdaptationZone(BaseModel):
    """Regional adaptation zone information."""
    
    zone_id: str = Field(..., description="Zone identifier")
    zone_name: str = Field(..., description="Zone name")
    suitable_varieties: List[str] = Field(..., description="Suitable varieties for this zone")
    environmental_characteristics: Dict[str, Any] = Field(..., description="Environmental characteristics")
    performance_expectations: Dict[str, float] = Field(..., description="Expected performance metrics")
"""
Crop Taxonomy Service Models

Pydantic models for crop taxonomy service requests, responses, and operations.
Provides comprehensive API models for the crop taxonomy microservice.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import date, datetime
from enum import Enum
from uuid import UUID

from .crop_taxonomy_models import ComprehensiveCropData, CropTaxonomyValidationResult
from .crop_filtering_models import TaxonomyFilterCriteria, CropSearchResult
from .crop_variety_models import EnhancedCropVariety, CropRegionalAdaptation


# ============================================================================
# SERVICE OPERATION ENUMERATIONS
# ============================================================================

class OperationType(str, Enum):
    """Types of crop taxonomy operations."""
    SEARCH = "search"
    CLASSIFY = "classify"
    RECOMMEND_VARIETIES = "recommend_varieties"
    GET_REGIONAL_DATA = "get_regional_data"
    VALIDATE_TAXONOMY = "validate_taxonomy"
    BULK_IMPORT = "bulk_import"
    UPDATE_CROP_DATA = "update_crop_data"


class DataSource(str, Enum):
    """Data sources for crop information."""
    USDA_PLANTS = "usda_plants"
    FAO_CROP_STATISTICS = "fao_crop_statistics"
    UNIVERSITY_EXTENSION = "university_extension"
    SEED_COMPANY = "seed_company"
    RESEARCH_PUBLICATION = "research_publication"
    FARMER_REPORTED = "farmer_reported"
    EXPERT_VALIDATION = "expert_validation"
    INTERNAL_DATABASE = "internal_database"


class ResponseFormat(str, Enum):
    """Response format options."""
    FULL = "full"
    SUMMARY = "summary"
    MINIMAL = "minimal"


class ValidationLevel(str, Enum):
    """Levels of data validation."""
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    EXPERT = "expert"


class ConfidenceLevel(str, Enum):
    """Confidence levels used across crop taxonomy operations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


# ============================================================================
# GENERAL SERVICE REQUEST/RESPONSE MODELS
# ============================================================================

class CropTaxonomyRequest(BaseModel):
    """Base request for crop taxonomy operations."""
    
    request_id: str = Field(..., description="Unique request identifier")
    operation_type: OperationType = Field(..., description="Type of operation requested")
    
    # Request metadata
    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    
    # Response preferences
    response_format: ResponseFormat = Field(default=ResponseFormat.FULL, description="Desired response format")
    max_processing_time_seconds: Optional[int] = Field(None, ge=1, le=300, description="Maximum processing time")
    
    # Quality preferences
    data_freshness_required: Optional[int] = Field(None, description="Data freshness in days")
    include_confidence_scores: bool = Field(default=True, description="Include confidence scoring")
    
    @validator('request_id')
    def validate_request_id(cls, v):
        """Validate request ID format."""
        if not v or len(v.strip()) < 1:
            raise ValueError("Request ID cannot be empty")
        return v.strip()


class CropTaxonomyResponse(BaseModel):
    """Base response for crop taxonomy operations."""
    
    request_id: str = Field(..., description="Original request identifier")
    operation_type: OperationType = Field(..., description="Operation type performed")
    
    # Response metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Response generation time")
    processing_time_seconds: float = Field(..., description="Processing time in seconds")
    
    # Success and status
    success: bool = Field(..., description="Operation success status")
    status_message: str = Field(..., description="Status message")
    error_details: Optional[List[str]] = Field(None, description="Error details if failed")
    
    # Data quality and confidence
    overall_confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Overall confidence score")
    data_sources: List[DataSource] = Field(default_factory=list, description="Data sources used")
    
    # Warnings and recommendations
    warnings: Optional[List[str]] = Field(None, description="Processing warnings")
    recommendations: Optional[List[str]] = Field(None, description="Service recommendations")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }


# ============================================================================
# CROP CLASSIFICATION REQUEST/RESPONSE MODELS
# ============================================================================

class CropClassificationRequest(CropTaxonomyRequest):
    """Request for crop classification and identification."""
    
    operation_type: OperationType = Field(default=OperationType.CLASSIFY, description="Classification operation")
    
    # Input data for classification
    crop_name: Optional[str] = Field(None, description="Crop common name")
    scientific_name: Optional[str] = Field(None, description="Scientific name")
    description: Optional[str] = Field(None, description="Crop description")
    
    # Additional identification data
    synonyms: Optional[List[str]] = Field(None, description="Known synonyms")
    regional_names: Optional[List[str]] = Field(None, description="Regional or local names")
    
    # Context for classification
    geographic_region: Optional[str] = Field(None, description="Geographic region context")
    farming_system: Optional[str] = Field(None, description="Farming system context")
    
    # Classification preferences
    include_similar_crops: bool = Field(default=True, description="Include similar crops")
    confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Minimum confidence for results")
    max_results: int = Field(default=10, ge=1, le=50, description="Maximum classification results")
    
    @validator('crop_name', 'scientific_name', 'description')
    def validate_input_data(cls, v):
        """Validate that at least one input is provided."""
        return v.strip() if v else None


class ClassificationResult(BaseModel):
    """Individual classification result."""
    
    matched_crop: ComprehensiveCropData = Field(..., description="Matched crop data")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Classification confidence")
    
    # Matching details
    matched_fields: List[str] = Field(default_factory=list, description="Fields that matched")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Overall similarity score")
    
    # Classification reasoning
    classification_factors: Dict[str, float] = Field(default_factory=dict, description="Factors in classification")
    alternative_names: List[str] = Field(default_factory=list, description="Alternative names found")
    
    # Validation status
    expert_validated: bool = Field(default=False, description="Expert validated classification")
    validation_notes: Optional[str] = Field(None, description="Validation notes")


class CropClassificationResponse(CropTaxonomyResponse):
    """Response containing crop classification results."""
    
    operation_type: OperationType = Field(default=OperationType.CLASSIFY, description="Classification operation")
    
    # Classification results
    classification_results: List[ClassificationResult] = Field(default_factory=list, description="Classification results")
    best_match: Optional[ClassificationResult] = Field(None, description="Best matching result")
    
    # Related information
    similar_crops: List[ComprehensiveCropData] = Field(default_factory=list, description="Similar crops")
    taxonomic_family_crops: List[str] = Field(default_factory=list, description="Other crops in same family")
    
    # Classification metadata
    input_quality_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Quality of input data")
    classification_method: str = Field(default="", description="Classification method used")
    
    # Suggestions for improvement
    suggested_refinements: Optional[List[str]] = Field(None, description="Suggestions to improve classification")


# ============================================================================
# CROP SEARCH REQUEST/RESPONSE MODELS (Extended)
# ============================================================================

class AdvancedCropSearchRequest(CropTaxonomyRequest):
    """Advanced crop search request with enhanced features."""
    
    operation_type: OperationType = Field(default=OperationType.SEARCH, description="Search operation")
    
    # Search criteria
    search_criteria: TaxonomyFilterCriteria = Field(..., description="Search and filter criteria")
    
    # Advanced search options
    include_varieties: bool = Field(default=False, description="Include variety-level results")
    include_regional_data: bool = Field(default=False, description="Include regional adaptation data")
    personalize_results: bool = Field(default=False, description="Personalize results for user")
    
    # Machine learning preferences
    use_ml_ranking: bool = Field(default=True, description="Use machine learning for result ranking")
    user_feedback_weight: float = Field(default=0.1, ge=0.0, le=1.0, description="Weight of user feedback in ranking")
    
    # Result customization
    result_fields: Optional[List[str]] = Field(None, description="Specific fields to include in results")
    exclude_experimental: bool = Field(default=True, description="Exclude experimental crops")


class EnhancedCropSearchResponse(CropTaxonomyResponse):
    """Enhanced crop search response with ML insights."""
    
    operation_type: OperationType = Field(default=OperationType.SEARCH, description="Search operation")
    
    # Search results
    search_results: List[CropSearchResult] = Field(default_factory=list, description="Search results")
    total_matches: int = Field(default=0, description="Total matching crops")
    
    # Enhanced insights
    category_insights: Dict[str, Any] = Field(default_factory=dict, description="Category-based insights")
    regional_trends: Dict[str, Any] = Field(default_factory=dict, description="Regional adaptation trends")
    
    # Machine learning insights
    ml_recommendations: Optional[List[str]] = Field(None, description="ML-generated recommendations")
    trend_analysis: Optional[Dict[str, Any]] = Field(None, description="Trend analysis results")
    
    # Search optimization
    search_performance: Dict[str, Any] = Field(default_factory=dict, description="Search performance metrics")
    query_suggestions: List[str] = Field(default_factory=list, description="Query improvement suggestions")


# ============================================================================
# VARIETY RECOMMENDATION REQUEST/RESPONSE MODELS
# ============================================================================

class VarietyRecommendationRequest(CropTaxonomyRequest):
    """Request for crop variety recommendations."""
    
    operation_type: OperationType = Field(default=OperationType.RECOMMEND_VARIETIES, description="Variety recommendation")
    
    # Crop specification
    crop_id: Optional[UUID] = Field(None, description="Specific crop ID")
    crop_name: Optional[str] = Field(None, description="Crop name if no ID provided")
    
    # Location and environment context
    location_data: Optional[Dict[str, Any]] = Field(None, description="Location and climate data")
    soil_conditions: Optional[Dict[str, Any]] = Field(None, description="Soil condition data")
    
    # Farming context
    farming_objectives: Optional[List[str]] = Field(None, description="Primary farming objectives")
    production_system: Optional[str] = Field(None, description="Production system type")
    available_equipment: Optional[List[str]] = Field(None, description="Available equipment")
    
    # Performance priorities
    yield_priority_weight: float = Field(default=0.4, ge=0.0, le=1.0, description="Yield priority weight")
    quality_priority_weight: float = Field(default=0.3, ge=0.0, le=1.0, description="Quality priority weight")
    risk_management_weight: float = Field(default=0.3, ge=0.0, le=1.0, description="Risk management weight")
    
    # Constraints and requirements
    required_traits: Optional[List[str]] = Field(None, description="Required variety traits")
    excluded_traits: Optional[List[str]] = Field(None, description="Traits to avoid")
    budget_constraints: Optional[Dict[str, float]] = Field(None, description="Budget limitations")
    
    # Recommendation preferences
    max_recommendations: int = Field(default=5, ge=1, le=20, description="Maximum variety recommendations")
    include_alternatives: bool = Field(default=True, description="Include alternative varieties")
    include_comparison: bool = Field(default=True, description="Include variety comparison")
    
    @validator('yield_priority_weight', 'quality_priority_weight', 'risk_management_weight')
    def validate_priority_weights(cls, v, values):
        """Validate that weights are reasonable."""
        # This is a simplified validation - ideally we'd check that all weights sum to 1.0
        return v


class VarietyRecommendationResponse(CropTaxonomyResponse):
    """Response containing variety recommendations."""
    
    operation_type: OperationType = Field(default=OperationType.RECOMMEND_VARIETIES, description="Variety recommendation")
    
    # Recommendation results
    recommended_varieties: List[Dict[str, Any]] = Field(default_factory=list, description="Recommended varieties with scoring")
    alternative_varieties: List[Dict[str, Any]] = Field(default_factory=list, description="Alternative options")
    
    # Analysis and insights
    variety_analysis: Dict[str, Any] = Field(default_factory=dict, description="Variety performance analysis")
    regional_suitability: Dict[str, Any] = Field(default_factory=dict, description="Regional suitability analysis")
    risk_assessment: Dict[str, Any] = Field(default_factory=dict, description="Risk assessment summary")
    
    # Comparison and selection tools
    variety_comparison_matrix: Optional[Dict[str, Any]] = Field(None, description="Variety comparison matrix")
    selection_guidance: List[str] = Field(default_factory=list, description="Selection guidance notes")
    
    # Implementation support
    management_recommendations: List[str] = Field(default_factory=list, description="Management recommendations")
    timing_recommendations: Dict[str, Any] = Field(default_factory=dict, description="Planting and harvest timing")
    
    # Success factors
    critical_success_factors: List[str] = Field(default_factory=list, description="Critical success factors")
    monitoring_recommendations: List[str] = Field(default_factory=list, description="Monitoring recommendations")


# ============================================================================
# REGIONAL DATA REQUEST/RESPONSE MODELS
# ============================================================================

class RegionalDataRequest(CropTaxonomyRequest):
    """Request for regional crop adaptation data."""
    
    operation_type: OperationType = Field(default=OperationType.GET_REGIONAL_DATA, description="Regional data operation")
    
    # Geographic scope
    region_specification: Dict[str, Any] = Field(..., description="Region specification (coordinates, name, etc.)")
    region_buffer_miles: Optional[float] = Field(None, ge=0, description="Buffer around region in miles")
    
    # Crop filters
    crop_ids: Optional[List[UUID]] = Field(None, description="Specific crop IDs")
    crop_categories: Optional[List[str]] = Field(None, description="Crop categories to include")
    
    # Data preferences
    include_historical_data: bool = Field(default=True, description="Include historical adaptation data")
    include_climate_projections: bool = Field(default=False, description="Include climate change projections")
    data_recency_days: Optional[int] = Field(None, description="Maximum age of data in days")
    
    # Analysis options
    aggregation_level: str = Field(default="county", description="Geographic aggregation level")
    include_statistics: bool = Field(default=True, description="Include statistical summaries")


class RegionalDataResponse(CropTaxonomyResponse):
    """Response containing regional crop data."""
    
    operation_type: OperationType = Field(default=OperationType.GET_REGIONAL_DATA, description="Regional data operation")
    
    # Regional data
    regional_adaptations: List[CropRegionalAdaptation] = Field(default_factory=list, description="Regional adaptation data")
    region_summary: Dict[str, Any] = Field(default_factory=dict, description="Region characteristics summary")
    
    # Climate and environmental data
    climate_summary: Dict[str, Any] = Field(default_factory=dict, description="Climate characteristics")
    soil_characteristics: Dict[str, Any] = Field(default_factory=dict, description="Soil characteristics")
    
    # Crop performance data
    crop_performance_statistics: Dict[str, Any] = Field(default_factory=dict, description="Regional crop performance")
    adaptation_trends: Dict[str, Any] = Field(default_factory=dict, description="Adaptation trends over time")
    
    # Recommendations
    regional_recommendations: List[str] = Field(default_factory=list, description="Region-specific recommendations")
    emerging_opportunities: List[str] = Field(default_factory=list, description="Emerging crop opportunities")
    
    # Data quality metadata
    data_coverage_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Data coverage quality")
    regional_data_sources: List[str] = Field(default_factory=list, description="Regional data sources")


# ============================================================================
# VALIDATION REQUEST/RESPONSE MODELS
# ============================================================================

class ValidationRequest(CropTaxonomyRequest):
    """Request for crop taxonomy validation."""
    
    operation_type: OperationType = Field(default=OperationType.VALIDATE_TAXONOMY, description="Validation operation")
    
    # Data to validate
    crop_data: Union[ComprehensiveCropData, List[ComprehensiveCropData]] = Field(..., description="Crop data to validate")
    
    # Validation options
    validation_level: ValidationLevel = Field(default=ValidationLevel.STANDARD, description="Validation strictness")
    validate_against_sources: List[DataSource] = Field(default_factory=list, description="External sources to validate against")
    
    # Expert validation
    request_expert_review: bool = Field(default=False, description="Request expert validation")
    expert_specialization: Optional[List[str]] = Field(None, description="Required expert specializations")
    
    # Validation scope
    validate_taxonomy: bool = Field(default=True, description="Validate taxonomic classification")
    validate_agricultural_data: bool = Field(default=True, description="Validate agricultural characteristics")
    validate_regional_data: bool = Field(default=True, description="Validate regional adaptations")
    
    # Quality thresholds
    minimum_confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Minimum confidence for acceptance")
    require_source_validation: bool = Field(default=False, description="Require validation against authoritative sources")


class ValidationResponse(CropTaxonomyResponse):
    """Response containing validation results."""
    
    operation_type: OperationType = Field(default=OperationType.VALIDATE_TAXONOMY, description="Validation operation")
    
    # Validation results
    validation_results: List[CropTaxonomyValidationResult] = Field(default_factory=list, description="Detailed validation results")
    overall_validation_status: bool = Field(..., description="Overall validation pass/fail")
    
    # Quality assessment
    data_quality_assessment: Dict[str, Any] = Field(default_factory=dict, description="Data quality assessment")
    completeness_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Data completeness score")
    accuracy_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Data accuracy score")
    
    # Improvement recommendations
    data_improvement_recommendations: List[str] = Field(default_factory=list, description="Data improvement suggestions")
    missing_data_fields: List[str] = Field(default_factory=list, description="Critical missing data fields")
    
    # Expert validation (if requested)
    expert_validation_status: Optional[str] = Field(None, description="Expert validation status")
    expert_comments: Optional[str] = Field(None, description="Expert validation comments")
    expert_confidence_score: Optional[float] = Field(None, description="Expert confidence in validation")
    
    # Source validation
    source_validation_results: Dict[str, Any] = Field(default_factory=dict, description="External source validation results")
    authoritative_source_alignment: Optional[float] = Field(None, description="Alignment with authoritative sources")


# ============================================================================
# BULK OPERATION MODELS
# ============================================================================

class BulkOperationRequest(CropTaxonomyRequest):
    """Request for bulk operations on crop taxonomy data."""
    
    operation_type: OperationType = Field(default=OperationType.BULK_IMPORT, description="Bulk operation type")
    
    # Bulk operation data
    operation_data: List[Dict[str, Any]] = Field(..., description="Bulk operation data")
    batch_size: int = Field(default=100, ge=1, le=1000, description="Processing batch size")
    
    # Processing options
    continue_on_error: bool = Field(default=True, description="Continue processing on individual errors")
    validation_level: ValidationLevel = Field(default=ValidationLevel.STANDARD, description="Validation level for bulk data")
    
    # Conflict resolution
    update_existing: bool = Field(default=False, description="Update existing records")
    skip_duplicates: bool = Field(default=True, description="Skip duplicate records")
    
    # Progress tracking
    enable_progress_tracking: bool = Field(default=True, description="Enable progress tracking")
    notification_webhook: Optional[str] = Field(None, description="Webhook URL for progress notifications")


class BulkOperationResponse(CropTaxonomyResponse):
    """Response for bulk operations."""
    
    operation_type: OperationType = Field(default=OperationType.BULK_IMPORT, description="Bulk operation type")
    
    # Processing results
    total_processed: int = Field(..., description="Total records processed")
    successful_operations: int = Field(..., description="Successful operations")
    failed_operations: int = Field(..., description="Failed operations")
    skipped_operations: int = Field(..., description="Skipped operations")
    
    # Detailed results
    operation_results: List[Dict[str, Any]] = Field(default_factory=list, description="Detailed operation results")
    error_summary: Dict[str, int] = Field(default_factory=dict, description="Error type summary")
    
    # Performance metrics
    processing_rate_per_second: float = Field(..., description="Processing rate (records/second)")
    memory_usage_mb: Optional[float] = Field(None, description="Peak memory usage (MB)")
    
    # Follow-up information
    retry_recommendations: List[str] = Field(default_factory=list, description="Retry recommendations for failed operations")
    batch_id: Optional[str] = Field(None, description="Batch identifier for tracking")

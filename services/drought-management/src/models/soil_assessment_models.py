"""
Soil Assessment Data Models

Pydantic models for soil management practice assessment,
scoring, and improvement recommendations.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal
from enum import Enum

# Enums for soil assessment
class TillageType(str, Enum):
    """Types of tillage practices."""
    NO_TILL = "no_till"
    STRIP_TILL = "strip_till"
    REDUCED_TILL = "reduced_till"
    CONVENTIONAL = "conventional"

class CoverCropSpecies(str, Enum):
    """Common cover crop species."""
    CEREAL_RYE = "cereal_rye"
    WINTER_WHEAT = "winter_wheat"
    OATS = "oats"
    CRIMSON_CLOVER = "crimson_clover"
    RED_CLOVER = "red_clover"
    WHITE_CLOVER = "white_clover"
    ANNUAL_RYEGRASS = "annual_ryegrass"
    RADISH = "radish"
    TURNIP = "turnip"
    BUCKWHEAT = "buckwheat"
    SORGHUM_SUDAN = "sorghum_sudan"

class CompactionLevel(str, Enum):
    """Soil compaction levels."""
    NONE = "none"
    SLIGHT = "slight"
    MODERATE = "moderate"
    SEVERE = "severe"
    EXTREME = "extreme"

class DrainageClass(str, Enum):
    """Soil drainage classifications."""
    EXCESSIVELY_DRAINED = "excessively_drained"
    WELL_DRAINED = "well_drained"
    MODERATELY_WELL_DRAINED = "moderately_well_drained"
    SOMEWHAT_POORLY_DRAINED = "somewhat_poorly_drained"
    POORLY_DRAINED = "poorly_drained"
    VERY_POORLY_DRAINED = "very_poorly_drained"

class SurfaceDrainage(str, Enum):
    """Surface drainage conditions."""
    EXCELLENT = "excellent"
    GOOD = "good"
    ADEQUATE = "adequate"
    POOR = "poor"
    VERY_POOR = "very_poor"

class SubsurfaceDrainage(str, Enum):
    """Subsurface drainage conditions."""
    TILE_DRAINED = "tile_drained"
    NATURAL_DRAINAGE = "natural_drainage"
    SOME_DRAINAGE = "some_drainage"
    LIMITED_DRAINAGE = "limited_drainage"
    NONE = "none"

class PriorityLevel(str, Enum):
    """Priority levels for improvements."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class SoilHealthGrade(str, Enum):
    """Soil health grade levels."""
    A_PLUS = "A+"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"

# Core assessment models
class TillagePracticeAssessment(BaseModel):
    """Assessment of tillage practices."""
    tillage_type: TillageType = Field(..., description="Type of tillage practice")
    tillage_frequency: int = Field(..., ge=0, le=12, description="Tillage frequency per year")
    tillage_depth: float = Field(..., ge=0, le=24, description="Average tillage depth in inches")
    equipment_type: str = Field(..., description="Type of tillage equipment used")
    intensity_score: float = Field(..., ge=0, le=100, description="Tillage intensity score")
    disturbance_score: float = Field(..., ge=0, le=100, description="Soil disturbance score")
    moisture_retention_score: float = Field(..., ge=0, le=100, description="Moisture retention score")
    overall_score: float = Field(..., ge=0, le=100, description="Overall tillage practice score")
    improvement_recommendations: List[str] = Field(default_factory=list, description="Improvement recommendations")

class CoverCropAssessment(BaseModel):
    """Assessment of cover crop usage."""
    cover_crops_used: bool = Field(..., description="Whether cover crops are used")
    species: List[str] = Field(default_factory=list, description="Cover crop species used")
    planting_timing: str = Field(..., description="Cover crop planting timing")
    termination_timing: str = Field(..., description="Cover crop termination timing")
    biomass_production: float = Field(..., ge=0, description="Biomass production in lbs per acre")
    implementation_score: float = Field(..., ge=0, le=100, description="Implementation score")
    biomass_score: float = Field(..., ge=0, le=100, description="Biomass production score")
    soil_health_score: float = Field(..., ge=0, le=100, description="Soil health benefits score")
    overall_score: float = Field(..., ge=0, le=100, description="Overall cover crop score")
    improvement_recommendations: List[str] = Field(default_factory=list, description="Improvement recommendations")

class OrganicMatterAssessment(BaseModel):
    """Assessment of organic matter management."""
    current_om_percent: float = Field(..., ge=0, le=20, description="Current organic matter percentage")
    target_om_percent: float = Field(..., ge=0, le=20, description="Target organic matter percentage")
    management_practices: List[str] = Field(default_factory=list, description="Organic matter management practices")
    manure_applications: int = Field(..., ge=0, description="Manure applications per year")
    compost_applications: int = Field(..., ge=0, description="Compost applications per year")
    om_level_score: float = Field(..., ge=0, le=100, description="Organic matter level score")
    management_score: float = Field(..., ge=0, le=100, description="Management practices score")
    improvement_score: float = Field(..., ge=0, le=100, description="Improvement potential score")
    overall_score: float = Field(..., ge=0, le=100, description="Overall organic matter score")
    improvement_recommendations: List[str] = Field(default_factory=list, description="Improvement recommendations")

class SoilCompactionAssessment(BaseModel):
    """Assessment of soil compaction."""
    compaction_level: CompactionLevel = Field(..., description="Current compaction level")
    bulk_density: float = Field(..., ge=0, le=3, description="Bulk density in g/cm³")
    penetration_resistance: float = Field(..., ge=0, description="Penetration resistance in PSI")
    management_practices: List[str] = Field(default_factory=list, description="Compaction management practices")
    severity_score: float = Field(..., ge=0, le=100, description="Compaction severity score")
    management_score: float = Field(..., ge=0, le=100, description="Management practices score")
    improvement_score: float = Field(..., ge=0, le=100, description="Improvement potential score")
    overall_score: float = Field(..., ge=0, le=100, description="Overall compaction score")
    improvement_recommendations: List[str] = Field(default_factory=list, description="Improvement recommendations")

class DrainageAssessment(BaseModel):
    """Assessment of drainage conditions."""
    drainage_class: DrainageClass = Field(..., description="Soil drainage class")
    surface_drainage: SurfaceDrainage = Field(..., description="Surface drainage condition")
    subsurface_drainage: SubsurfaceDrainage = Field(..., description="Subsurface drainage condition")
    management_practices: List[str] = Field(default_factory=list, description="Drainage management practices")
    drainage_class_score: float = Field(..., ge=0, le=100, description="Drainage class score")
    surface_drainage_score: float = Field(..., ge=0, le=100, description="Surface drainage score")
    subsurface_drainage_score: float = Field(..., ge=0, le=100, description="Subsurface drainage score")
    management_score: float = Field(..., ge=0, le=100, description="Management practices score")
    overall_score: float = Field(..., ge=0, le=100, description="Overall drainage score")
    improvement_recommendations: List[str] = Field(default_factory=list, description="Improvement recommendations")

class SoilHealthScore(BaseModel):
    """Overall soil health scoring."""
    overall_score: float = Field(..., ge=0, le=100, description="Overall soil health score")
    tillage_score: float = Field(..., ge=0, le=100, description="Tillage practices score")
    cover_crop_score: float = Field(..., ge=0, le=100, description="Cover crop score")
    organic_matter_score: float = Field(..., ge=0, le=100, description="Organic matter score")
    compaction_score: float = Field(..., ge=0, le=100, description="Compaction score")
    drainage_score: float = Field(..., ge=0, le=100, description="Drainage score")
    moisture_retention_score: float = Field(..., ge=0, le=100, description="Moisture retention score")
    limiting_factors: List[str] = Field(default_factory=list, description="Limiting factors")
    strengths: List[str] = Field(default_factory=list, description="Strengths")
    improvement_potential: float = Field(..., ge=0, le=100, description="Improvement potential")

class ImprovementOpportunity(BaseModel):
    """Improvement opportunity model."""
    category: str = Field(..., description="Category of improvement")
    priority: PriorityLevel = Field(..., description="Priority level")
    description: str = Field(..., description="Description of improvement opportunity")
    potential_impact: float = Field(..., ge=0, le=100, description="Potential impact score")
    implementation_cost: Decimal = Field(..., description="Implementation cost per acre")
    water_savings_potential: float = Field(..., ge=0, description="Water savings potential percentage")
    timeline: str = Field(..., description="Implementation timeline")
    resources_required: List[str] = Field(default_factory=list, description="Required resources")

class AssessmentReport(BaseModel):
    """Comprehensive assessment report."""
    field_id: UUID = Field(..., description="Field identifier")
    assessment_date: datetime = Field(default_factory=datetime.utcnow, description="Assessment date")
    overall_soil_health_score: float = Field(..., ge=0, le=100, description="Overall soil health score")
    soil_health_grade: SoilHealthGrade = Field(..., description="Soil health grade")
    improvement_opportunities_count: int = Field(..., ge=0, description="Number of improvement opportunities")
    total_water_savings_potential: float = Field(..., ge=0, description="Total water savings potential")
    recommendations_summary: str = Field(..., description="Summary of recommendations")
    implementation_timeline: Dict[str, Any] = Field(..., description="Implementation timeline")
    next_assessment_date: datetime = Field(..., description="Recommended next assessment date")
    confidence_level: float = Field(..., ge=0, le=1, description="Assessment confidence level")

# Request models
class SoilAssessmentRequest(BaseModel):
    """Request model for soil assessment."""
    field_id: UUID = Field(..., description="Field identifier")
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    tillage_practices: Dict[str, Any] = Field(..., description="Current tillage practices")
    cover_crop_practices: Dict[str, Any] = Field(..., description="Current cover crop practices")
    organic_matter_data: Dict[str, Any] = Field(..., description="Organic matter data")
    compaction_data: Dict[str, Any] = Field(..., description="Soil compaction data")
    drainage_data: Dict[str, Any] = Field(..., description="Drainage data")
    include_recommendations: bool = Field(True, description="Include improvement recommendations")
    assessment_depth_months: int = Field(12, ge=1, le=60, description="Assessment depth in months")

class PracticeScore(BaseModel):
    """Individual practice score model."""
    practice_name: str = Field(..., description="Name of the practice")
    current_score: float = Field(..., ge=0, le=100, description="Current practice score")
    target_score: float = Field(..., ge=0, le=100, description="Target practice score")
    improvement_potential: float = Field(..., ge=0, le=100, description="Improvement potential")
    priority_level: PriorityLevel = Field(..., description="Priority level for improvement")
    water_savings_potential: float = Field(..., ge=0, description="Water savings potential")

# Response models
class SoilAssessmentResponse(BaseModel):
    """Response model for soil assessment."""
    field_id: UUID = Field(..., description="Field identifier")
    assessment_date: datetime = Field(default_factory=datetime.utcnow, description="Assessment date")
    soil_health_score: SoilHealthScore = Field(..., description="Overall soil health score")
    tillage_assessment: TillagePracticeAssessment = Field(..., description="Tillage practice assessment")
    cover_crop_assessment: CoverCropAssessment = Field(..., description="Cover crop assessment")
    organic_matter_assessment: OrganicMatterAssessment = Field(..., description="Organic matter assessment")
    compaction_assessment: SoilCompactionAssessment = Field(..., description="Compaction assessment")
    drainage_assessment: DrainageAssessment = Field(..., description="Drainage assessment")
    improvement_opportunities: List[ImprovementOpportunity] = Field(default_factory=list, description="Improvement opportunities")
    assessment_report: AssessmentReport = Field(..., description="Assessment report")
    confidence_score: float = Field(..., ge=0, le=1, description="Assessment confidence score")

class PracticeRecommendationResponse(BaseModel):
    """Response model for practice recommendations."""
    field_id: UUID = Field(..., description="Field identifier")
    practice_scores: List[PracticeScore] = Field(..., description="Individual practice scores")
    top_priorities: List[str] = Field(..., description="Top priority improvements")
    implementation_plan: Dict[str, Any] = Field(..., description="Implementation plan")
    expected_benefits: Dict[str, Any] = Field(..., description="Expected benefits")
    cost_benefit_analysis: Dict[str, Any] = Field(..., description="Cost-benefit analysis")

class SoilHealthTrendResponse(BaseModel):
    """Response model for soil health trends."""
    field_id: UUID = Field(..., description="Field identifier")
    assessment_history: List[Dict[str, Any]] = Field(..., description="Historical assessment data")
    trend_analysis: Dict[str, Any] = Field(..., description="Trend analysis results")
    improvement_rate: float = Field(..., description="Rate of improvement")
    projected_scores: Dict[str, float] = Field(..., description="Projected future scores")
    recommendations: List[str] = Field(default_factory=list, description="Trend-based recommendations")

# Validation methods
class SoilAssessmentValidator:
    """Validator for soil assessment data."""
    
    @staticmethod
    def validate_tillage_data(data: Dict[str, Any]) -> bool:
        """Validate tillage practice data."""
        required_fields = ['tillage_type', 'frequency_per_year', 'average_depth_inches']
        return all(field in data for field in required_fields)
    
    @staticmethod
    def validate_cover_crop_data(data: Dict[str, Any]) -> bool:
        """Validate cover crop data."""
        if not data.get('cover_crops_used', False):
            return True
        
        required_fields = ['species', 'planting_timing', 'termination_timing']
        return all(field in data for field in required_fields)
    
    @staticmethod
    def validate_organic_matter_data(data: Dict[str, Any]) -> bool:
        """Validate organic matter data."""
        required_fields = ['current_om_percent']
        return all(field in data for field in required_fields)
    
    @staticmethod
    def validate_compaction_data(data: Dict[str, Any]) -> bool:
        """Validate compaction data."""
        required_fields = ['compaction_level']
        return all(field in data for field in required_fields)
    
    @staticmethod
    def validate_drainage_data(data: Dict[str, Any]) -> bool:
        """Validate drainage data."""
        required_fields = ['drainage_class']
        return all(field in data for field in required_fields)
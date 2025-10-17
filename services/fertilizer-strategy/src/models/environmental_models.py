"""
Environmental and Regulatory Compliance Models for Fertilizer Strategy Optimization.

This module defines data models for environmental impact assessment,
regulatory compliance tracking, and sustainability optimization.
"""

from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, validator


class RegulationType(str, Enum):
    """Types of agricultural regulations."""
    FEDERAL = "federal"
    STATE = "state"
    LOCAL = "local"
    ORGANIC_CERTIFICATION = "organic_certification"
    CONSERVATION_PROGRAM = "conservation_program"


class ComplianceStatus(str, Enum):
    """Compliance status levels."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    AT_RISK = "at_risk"
    REQUIRES_REVIEW = "requires_review"
    PENDING_VERIFICATION = "pending_verification"


class EnvironmentalImpactLevel(str, Enum):
    """Environmental impact severity levels."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class RegulatoryRule(BaseModel):
    """Model for regulatory rules and requirements."""
    
    rule_id: str = Field(..., description="Unique identifier for the regulation")
    regulation_type: RegulationType = Field(..., description="Type of regulation")
    jurisdiction: str = Field(..., description="Federal, state, or local jurisdiction")
    title: str = Field(..., description="Human-readable title of the regulation")
    description: str = Field(..., description="Detailed description of the regulation")
    
    # Application restrictions
    max_application_rate: Optional[Decimal] = Field(None, description="Maximum application rate (lbs/acre)")
    application_timing_restrictions: Optional[List[str]] = Field(None, description="Restricted application periods")
    buffer_zone_requirements: Optional[Decimal] = Field(None, description="Required buffer zone distance (feet)")
    
    # Environmental requirements
    soil_conditions: Optional[List[str]] = Field(None, description="Applicable soil conditions")
    weather_restrictions: Optional[List[str]] = Field(None, description="Weather-based restrictions")
    water_body_protection: Optional[bool] = Field(None, description="Water body protection requirements")
    
    # Record keeping requirements
    record_keeping_required: bool = Field(False, description="Whether records must be kept")
    reporting_requirements: Optional[List[str]] = Field(None, description="Required reporting")
    
    # Effective dates
    effective_date: date = Field(..., description="Date regulation becomes effective")
    expiration_date: Optional[date] = Field(None, description="Date regulation expires")
    
    # Metadata
    source_url: Optional[str] = Field(None, description="Source URL for regulation")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ComplianceAssessment(BaseModel):
    """Model for compliance assessment results."""
    
    assessment_id: UUID = Field(default_factory=uuid4, description="Unique assessment identifier")
    field_id: UUID = Field(..., description="Field being assessed")
    user_id: UUID = Field(..., description="User requesting assessment")
    
    # Assessment details
    assessment_date: datetime = Field(default_factory=datetime.utcnow)
    regulation_type: RegulationType = Field(..., description="Type of regulation assessed")
    jurisdiction: str = Field(..., description="Jurisdiction of regulation")
    
    # Compliance results
    overall_status: ComplianceStatus = Field(..., description="Overall compliance status")
    compliance_score: float = Field(..., ge=0.0, le=1.0, description="Compliance score (0-1)")
    
    # Detailed results
    applicable_rules: List[RegulatoryRule] = Field(..., description="Rules that apply to this field")
    violations: List[Dict[str, Any]] = Field(default_factory=list, description="Compliance violations")
    recommendations: List[str] = Field(default_factory=list, description="Compliance recommendations")
    
    # Risk assessment
    risk_level: EnvironmentalImpactLevel = Field(..., description="Environmental risk level")
    risk_factors: List[str] = Field(default_factory=list, description="Identified risk factors")
    
    # Documentation
    supporting_documents: Optional[List[str]] = Field(None, description="Supporting documentation")
    notes: Optional[str] = Field(None, description="Additional notes")


class EnvironmentalImpactAssessment(BaseModel):
    """Model for environmental impact assessment."""
    
    assessment_id: UUID = Field(default_factory=uuid4, description="Unique assessment identifier")
    field_id: UUID = Field(..., description="Field being assessed")
    fertilizer_plan_id: UUID = Field(..., description="Fertilizer application plan")
    
    # Impact metrics
    nutrient_runoff_risk: EnvironmentalImpactLevel = Field(..., description="Nutrient runoff risk")
    groundwater_contamination_risk: EnvironmentalImpactLevel = Field(..., description="Groundwater contamination risk")
    air_quality_impact: EnvironmentalImpactLevel = Field(..., description="Air quality impact")
    soil_health_impact: EnvironmentalImpactLevel = Field(..., description="Soil health impact")
    
    # Quantified impacts
    estimated_nitrogen_loss: Optional[Decimal] = Field(None, description="Estimated N loss (lbs/acre)")
    estimated_phosphorus_loss: Optional[Decimal] = Field(None, description="Estimated P loss (lbs/acre)")
    carbon_footprint: Optional[Decimal] = Field(None, description="Carbon footprint (kg CO2/acre)")
    
    # Mitigation measures
    recommended_mitigation: List[str] = Field(default_factory=list, description="Recommended mitigation measures")
    buffer_zone_recommendations: Optional[Decimal] = Field(None, description="Recommended buffer zone (feet)")
    
    # Assessment metadata
    assessment_date: datetime = Field(default_factory=datetime.utcnow)
    assessment_method: str = Field(..., description="Method used for assessment")
    confidence_level: float = Field(..., ge=0.0, le=1.0, description="Assessment confidence")


class SustainabilityMetrics(BaseModel):
    """Model for sustainability performance metrics."""
    
    field_id: UUID = Field(..., description="Field identifier")
    assessment_period: str = Field(..., description="Assessment period (e.g., '2024')")
    
    # Nutrient efficiency metrics
    nitrogen_use_efficiency: Optional[float] = Field(None, ge=0.0, le=1.0, description="N use efficiency (0-1)")
    phosphorus_use_efficiency: Optional[float] = Field(None, ge=0.0, le=1.0, description="P use efficiency (0-1)")
    potassium_use_efficiency: Optional[float] = Field(None, ge=0.0, le=1.0, description="K use efficiency (0-1)")
    
    # Environmental metrics
    soil_organic_matter_change: Optional[Decimal] = Field(None, description="Change in soil OM (%)")
    erosion_reduction: Optional[float] = Field(None, ge=0.0, le=1.0, description="Erosion reduction (0-1)")
    water_quality_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Water quality score (0-1)")
    
    # Economic sustainability
    cost_per_unit_yield: Optional[Decimal] = Field(None, description="Cost per unit yield")
    profitability_index: Optional[float] = Field(None, description="Profitability index")
    
    # Overall sustainability score
    sustainability_score: float = Field(..., ge=0.0, le=1.0, description="Overall sustainability score (0-1)")
    
    # Metadata
    calculated_date: datetime = Field(default_factory=datetime.utcnow)
    data_sources: List[str] = Field(default_factory=list, description="Data sources used")


class ComplianceRequest(BaseModel):
    """Request model for compliance assessment."""
    
    field_id: UUID = Field(..., description="Field to assess")
    regulation_types: Optional[List[RegulationType]] = Field(None, description="Specific regulation types to check")
    jurisdiction: Optional[str] = Field(None, description="Specific jurisdiction to check")
    include_environmental_assessment: bool = Field(True, description="Include environmental impact assessment")
    include_sustainability_metrics: bool = Field(True, description="Include sustainability metrics")


class ComplianceResponse(BaseModel):
    """Response model for compliance assessment."""
    
    assessment_id: UUID = Field(..., description="Assessment identifier")
    field_id: UUID = Field(..., description="Field assessed")
    
    # Compliance results
    compliance_assessment: ComplianceAssessment = Field(..., description="Compliance assessment results")
    environmental_assessment: Optional[EnvironmentalImpactAssessment] = Field(None, description="Environmental impact assessment")
    sustainability_metrics: Optional[SustainabilityMetrics] = Field(None, description="Sustainability metrics")
    
    # Summary
    overall_compliance_status: ComplianceStatus = Field(..., description="Overall compliance status")
    critical_issues: List[str] = Field(default_factory=list, description="Critical compliance issues")
    recommendations: List[str] = Field(default_factory=list, description="Priority recommendations")
    
    # Metadata
    assessment_date: datetime = Field(default_factory=datetime.utcnow)
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


class RegulatoryUpdate(BaseModel):
    """Model for regulatory updates and changes."""
    
    update_id: UUID = Field(default_factory=uuid4, description="Unique update identifier")
    regulation_id: str = Field(..., description="Regulation being updated")
    update_type: str = Field(..., description="Type of update (new, modified, repealed)")
    
    # Update details
    title: str = Field(..., description="Update title")
    description: str = Field(..., description="Detailed description of changes")
    effective_date: date = Field(..., description="Date changes become effective")
    
    # Impact assessment
    affected_fields: Optional[List[UUID]] = Field(None, description="Fields potentially affected")
    compliance_impact: str = Field(..., description="Impact on compliance status")
    
    # Notification
    notification_sent: bool = Field(False, description="Whether notification was sent")
    notification_date: Optional[datetime] = Field(None, description="Date notification was sent")
    
    # Metadata
    source_url: Optional[str] = Field(None, description="Source URL for update")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ComplianceReport(BaseModel):
    """Model for compliance reporting."""
    
    report_id: UUID = Field(default_factory=uuid4, description="Unique report identifier")
    farm_id: UUID = Field(..., description="Farm identifier")
    report_period: str = Field(..., description="Reporting period (e.g., '2024-Q1')")
    
    # Report contents
    total_fields_assessed: int = Field(..., description="Total number of fields assessed")
    compliance_summary: Dict[str, int] = Field(..., description="Summary of compliance status counts")
    environmental_summary: Dict[str, int] = Field(..., description="Summary of environmental impact levels")
    
    # Key findings
    critical_violations: List[Dict[str, Any]] = Field(default_factory=list, description="Critical violations found")
    improvement_areas: List[str] = Field(default_factory=list, description="Areas needing improvement")
    best_practices: List[str] = Field(default_factory=list, description="Best practices identified")
    
    # Recommendations
    priority_actions: List[str] = Field(default_factory=list, description="Priority actions needed")
    long_term_goals: List[str] = Field(default_factory=list, description="Long-term sustainability goals")
    
    # Metadata
    generated_date: datetime = Field(default_factory=datetime.utcnow)
    generated_by: str = Field(..., description="System or user that generated report")
    report_format: str = Field(default="pdf", description="Report format (pdf, html, json)")


# Validation methods
class ComplianceValidator:
    """Validator for compliance-related data."""
    
    @staticmethod
    def validate_application_rate(rate: Decimal, regulation: RegulatoryRule) -> bool:
        """Validate application rate against regulation limits."""
        if regulation.max_application_rate is None:
            return True
        return rate <= regulation.max_application_rate
    
    @staticmethod
    def validate_buffer_zone(distance: Decimal, regulation: RegulatoryRule) -> bool:
        """Validate buffer zone distance against requirements."""
        if regulation.buffer_zone_requirements is None:
            return True
        return distance >= regulation.buffer_zone_requirements
    
    @staticmethod
    def validate_timing_restrictions(application_date: date, regulation: RegulatoryRule) -> bool:
        """Validate application timing against restrictions."""
        if not regulation.application_timing_restrictions:
            return True
        
        # Check if application date falls within restricted periods
        for restriction in regulation.application_timing_restrictions:
            # This would need more sophisticated parsing in production
            if "winter" in restriction.lower() and application_date.month in [12, 1, 2]:
                return False
            if "spring" in restriction.lower() and application_date.month in [3, 4, 5]:
                return False
        
        return True


# Additional models for sustainability optimization

class OptimizationObjective(BaseModel):
    """Model for optimization objectives."""
    name: str = Field(..., description="Objective name")
    weight: float = Field(..., ge=0.0, le=1.0, description="Objective weight (0-1)")
    target_value: Optional[float] = Field(None, description="Target value for objective")
    minimize: bool = Field(True, description="Whether to minimize this objective")


class OptimizationConstraint(BaseModel):
    """Model for optimization constraints."""
    name: str = Field(..., description="Constraint name")
    constraint_type: str = Field(..., description="Constraint type (eq, ineq, bound)")
    value: float = Field(..., description="Constraint value")
    field: Optional[str] = Field(None, description="Field this constraint applies to")


class SustainabilityOptimizationRequest(BaseModel):
    """Request model for sustainability optimization."""
    field_id: UUID = Field(..., description="Field identifier")
    field_data: Dict[str, Any] = Field(..., description="Field characteristics and soil data")
    fertilizer_options: List[Dict[str, Any]] = Field(..., description="Available fertilizer options")
    optimization_objectives: Optional[List[OptimizationObjective]] = Field(None, description="Custom optimization objectives")
    constraints: Optional[List[OptimizationConstraint]] = Field(None, description="Custom optimization constraints")
    optimization_method: str = Field("genetic_algorithm", description="Optimization algorithm to use")
    include_trade_off_analysis: bool = Field(True, description="Include trade-off analysis")


class SustainabilityOptimizationResult(BaseModel):
    """Result model for sustainability optimization."""
    optimization_id: UUID = Field(default_factory=uuid4, description="Unique optimization identifier")
    field_id: UUID = Field(..., description="Field identifier")
    optimization_objectives: List[OptimizationObjective] = Field(..., description="Optimization objectives used")
    optimal_fertilizer_rates: Dict[str, float] = Field(..., description="Optimal fertilizer application rates")
    environmental_impact: EnvironmentalImpactAssessment = Field(..., description="Environmental impact assessment")
    sustainability_metrics: SustainabilityMetrics = Field(..., description="Sustainability metrics")
    optimization_score: float = Field(..., ge=0.0, le=1.0, description="Overall optimization score")
    trade_off_analysis: Dict[str, Any] = Field(default_factory=dict, description="Trade-off analysis results")
    recommendations: List[str] = Field(default_factory=list, description="Optimization recommendations")
    confidence_level: float = Field(..., ge=0.0, le=1.0, description="Optimization confidence level")
    optimization_method: str = Field(..., description="Optimization method used")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    optimization_date: datetime = Field(default_factory=datetime.utcnow, description="Optimization date")


class ScenarioComparisonRequest(BaseModel):
    """Request model for scenario comparison."""
    field_id: UUID = Field(..., description="Field identifier")
    scenarios: List[Dict[str, Any]] = Field(..., description="Optimization scenarios to compare")


class ScenarioComparisonResult(BaseModel):
    """Result model for scenario comparison."""
    comparison_id: UUID = Field(default_factory=uuid4, description="Unique comparison identifier")
    field_id: UUID = Field(..., description="Field identifier")
    scenarios: List[Dict[str, Any]] = Field(..., description="Comparison results for each scenario")
    ranked_scenarios: List[Dict[str, Any]] = Field(..., description="Scenarios ranked by optimization score")
    best_scenario: Optional[Dict[str, Any]] = Field(None, description="Best performing scenario")
    comparison_summary: Dict[str, Any] = Field(..., description="Summary statistics")
    comparison_date: datetime = Field(default_factory=datetime.utcnow, description="Comparison date")


class CarbonFootprintAnalysis(BaseModel):
    """Model for carbon footprint analysis."""
    analysis_id: UUID = Field(default_factory=uuid4, description="Unique analysis identifier")
    field_id: UUID = Field(..., description="Field identifier")
    fertilizer_rates: Dict[str, float] = Field(..., description="Fertilizer application rates")
    
    # Carbon footprint components
    fertilizer_production_emissions: Decimal = Field(..., description="CO2 emissions from fertilizer production (kg CO2/acre)")
    application_emissions: Decimal = Field(..., description="CO2 emissions from application (kg CO2/acre)")
    transportation_emissions: Decimal = Field(..., description="CO2 emissions from transportation (kg CO2/acre)")
    total_carbon_footprint: Decimal = Field(..., description="Total carbon footprint (kg CO2/acre)")
    
    # Carbon sequestration potential
    soil_carbon_sequestration: Optional[Decimal] = Field(None, description="Potential soil carbon sequestration (kg CO2/acre)")
    net_carbon_balance: Optional[Decimal] = Field(None, description="Net carbon balance (kg CO2/acre)")
    
    # Analysis metadata
    analysis_date: datetime = Field(default_factory=datetime.utcnow, description="Analysis date")
    analysis_method: str = Field(..., description="Method used for analysis")
    confidence_level: float = Field(..., ge=0.0, le=1.0, description="Analysis confidence level")


class WaterQualityImpact(BaseModel):
    """Model for water quality impact assessment."""
    assessment_id: UUID = Field(default_factory=uuid4, description="Unique assessment identifier")
    field_id: UUID = Field(..., description="Field identifier")
    fertilizer_rates: Dict[str, float] = Field(..., description="Fertilizer application rates")
    
    # Water quality metrics
    nitrogen_leaching_risk: EnvironmentalImpactLevel = Field(..., description="Nitrogen leaching risk level")
    phosphorus_runoff_risk: EnvironmentalImpactLevel = Field(..., description="Phosphorus runoff risk level")
    groundwater_contamination_risk: EnvironmentalImpactLevel = Field(..., description="Groundwater contamination risk")
    
    # Quantified impacts
    estimated_nitrate_leaching: Optional[Decimal] = Field(None, description="Estimated nitrate leaching (lbs/acre)")
    estimated_phosphorus_runoff: Optional[Decimal] = Field(None, description="Estimated phosphorus runoff (lbs/acre)")
    water_quality_index: float = Field(..., ge=0.0, le=1.0, description="Overall water quality index")
    
    # Mitigation measures
    recommended_buffer_strips: Optional[Decimal] = Field(None, description="Recommended buffer strip width (feet)")
    recommended_cover_crops: List[str] = Field(default_factory=list, description="Recommended cover crops")
    recommended_timing_adjustments: List[str] = Field(default_factory=list, description="Recommended timing adjustments")
    
    # Assessment metadata
    assessment_date: datetime = Field(default_factory=datetime.utcnow, description="Assessment date")
    assessment_method: str = Field(..., description="Method used for assessment")
    confidence_level: float = Field(..., ge=0.0, le=1.0, description="Assessment confidence level")


class SoilHealthAssessment(BaseModel):
    """Model for soil health assessment."""
    assessment_id: UUID = Field(default_factory=uuid4, description="Unique assessment identifier")
    field_id: UUID = Field(..., description="Field identifier")
    fertilizer_rates: Dict[str, float] = Field(..., description="Fertilizer application rates")
    
    # Soil health indicators
    organic_matter_change: Decimal = Field(..., description="Change in soil organic matter (%)")
    microbial_activity_score: float = Field(..., ge=0.0, le=1.0, description="Microbial activity score")
    soil_structure_score: float = Field(..., ge=0.0, le=1.0, description="Soil structure score")
    nutrient_cycling_score: float = Field(..., ge=0.0, le=1.0, description="Nutrient cycling score")
    
    # Overall soil health
    overall_soil_health_score: float = Field(..., ge=0.0, le=1.0, description="Overall soil health score")
    soil_health_trend: str = Field(..., description="Soil health trend (improving, stable, declining)")
    
    # Recommendations
    soil_health_recommendations: List[str] = Field(default_factory=list, description="Soil health improvement recommendations")
    
    # Assessment metadata
    assessment_date: datetime = Field(default_factory=datetime.utcnow, description="Assessment date")
    assessment_method: str = Field(..., description="Method used for assessment")
    confidence_level: float = Field(..., ge=0.0, le=1.0, description="Assessment confidence level")
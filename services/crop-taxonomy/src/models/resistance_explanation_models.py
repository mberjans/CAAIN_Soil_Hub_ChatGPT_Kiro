"""
Resistance Explanation Models

Pydantic models for resistance recommendation explanations and educational content.
Provides data models for comprehensive resistance-specific explanations, educational content,
and stewardship guidelines for crop variety recommendations.

TICKET-005_crop-variety-recommendations-10.3: Add comprehensive resistance recommendation explanations and education
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


class ResistanceType(str, Enum):
    """Types of pest resistance mechanisms."""
    BT_TOXIN = "bt_toxin"
    HERBICIDE_TOLERANCE = "herbicide_tolerance"
    DISEASE_RESISTANCE = "disease_resistance"
    INSECT_RESISTANCE = "insect_resistance"
    NEMATODE_RESISTANCE = "nematode_resistance"
    DROUGHT_TOLERANCE = "drought_tolerance"
    HEAT_TOLERANCE = "heat_tolerance"
    COLD_TOLERANCE = "cold_tolerance"


class ResistanceMechanism(str, Enum):
    """Specific resistance mechanisms."""
    PROTEIN_INHIBITION = "protein_inhibition"
    METABOLIC_DETOXIFICATION = "metabolic_detoxification"
    STRUCTURAL_MODIFICATION = "structural_modification"
    PHYSIOLOGICAL_ADAPTATION = "physiological_adaptation"
    BEHAVIORAL_MODIFICATION = "behavioral_modification"


class StewardshipLevel(str, Enum):
    """Stewardship compliance levels."""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class EducationLevel(str, Enum):
    """Education level for content generation."""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ComplianceLevel(str, Enum):
    """Compliance level for requirements."""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ResistanceTrait(BaseModel):
    """Model for resistance trait information."""
    
    type: ResistanceType = Field(..., description="Type of resistance mechanism")
    trait_name: str = Field(..., description="Name of the resistance trait")
    variety_id: Optional[str] = Field(None, description="Variety identifier")
    variety_name: Optional[str] = Field(None, description="Variety name")
    target_organisms: List[str] = Field(default_factory=list, description="Target organisms")
    mechanism: str = Field(..., description="Resistance mechanism description")
    efficacy: str = Field(default="Unknown", description="Efficacy level")
    
    @validator('target_organisms')
    def validate_target_organisms(cls, v):
        """Validate target organisms list."""
        if not isinstance(v, list):
            return []
        return [str(org) for org in v if org]


class MechanismExplanation(BaseModel):
    """Model for resistance mechanism explanation."""
    
    mechanism: str = Field(..., description="Mechanism type")
    description: str = Field(..., description="Detailed mechanism description")
    target_organisms: List[str] = Field(default_factory=list, description="Target organisms")
    durability: str = Field(..., description="Resistance durability assessment")
    resistance_risk: str = Field(..., description="Resistance development risk")
    management_strategy: str = Field(..., description="Management strategy")


class PestPressureAnalysis(BaseModel):
    """Model for pest pressure analysis."""
    
    current_pest_pressure: str = Field(..., description="Current pest pressure level")
    historical_trends: List[str] = Field(default_factory=list, description="Historical trends")
    resistance_development: str = Field(..., description="Resistance development status")
    management_implications: List[str] = Field(default_factory=list, description="Management implications")
    monitoring_recommendations: List[str] = Field(default_factory=list, description="Monitoring recommendations")


class ResistanceEffectiveness(BaseModel):
    """Model for resistance effectiveness assessment."""
    
    overall_effectiveness: str = Field(..., description="Overall effectiveness rating")
    target_pest_coverage: int = Field(..., description="Number of target pests covered")
    resistance_durability: str = Field(..., description="Resistance durability")
    management_requirements: List[str] = Field(default_factory=list, description="Management requirements")


class RiskAssessment(BaseModel):
    """Model for resistance risk assessment."""
    
    resistance_development_risk: str = Field(..., description="Resistance development risk level")
    environmental_risks: List[str] = Field(default_factory=list, description="Environmental risks")
    economic_risks: List[str] = Field(default_factory=list, description="Economic risks")
    regulatory_risks: List[str] = Field(default_factory=list, description="Regulatory risks")
    mitigation_strategies: List[str] = Field(default_factory=list, description="Mitigation strategies")


class EducationalContent(BaseModel):
    """Model for educational content."""
    
    title: str = Field(..., description="Content title")
    content: List[str] = Field(..., description="Content items")
    
    @validator('content')
    def validate_content(cls, v):
        """Validate content list."""
        if not isinstance(v, list):
            return []
        return [str(item) for item in v if item]


class TraitSpecificEducation(BaseModel):
    """Model for trait-specific educational content."""
    
    mechanism_explanation: str = Field(..., description="Mechanism explanation")
    management_guidance: str = Field(..., description="Management guidance")
    monitoring_requirements: List[str] = Field(default_factory=list, description="Monitoring requirements")
    compliance_requirements: List[str] = Field(default_factory=list, description="Compliance requirements")


class RefugeRequirements(BaseModel):
    """Model for refuge requirements."""
    
    structured_refuge: Optional[str] = Field(None, description="Structured refuge requirements")
    in_field_refuge: Optional[str] = Field(None, description="In-field refuge requirements")
    seed_blend: Optional[str] = Field(None, description="Seed blend requirements")


class StewardshipGuidelines(BaseModel):
    """Model for stewardship guidelines."""
    
    refuge_requirements: Dict[str, RefugeRequirements] = Field(default_factory=dict, description="Refuge requirements")
    monitoring_requirements: List[str] = Field(default_factory=list, description="Monitoring requirements")
    documentation_requirements: List[str] = Field(default_factory=list, description="Documentation requirements")
    compliance_checklist: List[str] = Field(default_factory=list, description="Compliance checklist")


class ManagementRecommendations(BaseModel):
    """Model for management recommendations."""
    
    immediate_actions: List[str] = Field(default_factory=list, description="Immediate actions")
    seasonal_management: List[str] = Field(default_factory=list, description="Seasonal management")
    long_term_strategy: List[str] = Field(default_factory=list, description="Long-term strategy")
    monitoring_schedule: List[str] = Field(default_factory=list, description="Monitoring schedule")
    record_keeping: List[str] = Field(default_factory=list, description="Record keeping requirements")


class DurabilityAssessment(BaseModel):
    """Model for durability assessment."""
    
    overall_durability: str = Field(..., description="Overall durability rating")
    durability_factors: List[str] = Field(default_factory=list, description="Durability factors")
    durability_timeline: Dict[str, str] = Field(default_factory=dict, description="Durability timeline")
    sustainability_score: float = Field(..., ge=0.0, le=1.0, description="Sustainability score")
    
    @validator('sustainability_score')
    def validate_sustainability_score(cls, v):
        """Validate sustainability score range."""
        if not isinstance(v, (int, float)):
            return 0.0
        return max(0.0, min(1.0, float(v)))


class ComplianceRequirements(BaseModel):
    """Model for compliance requirements."""
    
    usda_requirements: List[str] = Field(default_factory=list, description="USDA requirements")
    epa_requirements: List[str] = Field(default_factory=list, description="EPA requirements")
    state_requirements: List[str] = Field(default_factory=list, description="State requirements")
    label_requirements: List[str] = Field(default_factory=list, description="Label requirements")
    documentation_requirements: List[str] = Field(default_factory=list, description="Documentation requirements")


class ExplanationSections(BaseModel):
    """Model for explanation sections."""
    
    mechanism_explanations: Dict[str, MechanismExplanation] = Field(default_factory=dict, description="Mechanism explanations")
    pest_pressure_analysis: PestPressureAnalysis = Field(..., description="Pest pressure analysis")
    resistance_effectiveness: Dict[str, ResistanceEffectiveness] = Field(default_factory=dict, description="Resistance effectiveness")
    risk_assessment: RiskAssessment = Field(..., description="Risk assessment")


class ResistanceExplanationRequest(BaseModel):
    """Request model for resistance explanation generation."""
    
    variety_data: Dict[str, Any] = Field(..., description="Variety information and characteristics")
    pest_resistance_data: Dict[str, Any] = Field(..., description="Pest resistance analysis results")
    context: Dict[str, Any] = Field(..., description="Farm and environmental context")
    explanation_options: Optional[Dict[str, Any]] = Field(None, description="Options for explanation generation")
    include_educational_content: bool = Field(True, description="Include educational content")
    include_stewardship_guidelines: bool = Field(True, description="Include stewardship guidelines")
    include_compliance_requirements: bool = Field(True, description="Include compliance requirements")


class ResistanceExplanationResponse(BaseModel):
    """Response model for resistance explanation generation."""
    
    explanation_id: str = Field(..., description="Unique explanation identifier")
    variety_id: Optional[str] = Field(None, description="Variety identifier")
    variety_name: Optional[str] = Field(None, description="Variety name")
    resistance_traits: List[ResistanceTrait] = Field(..., description="Resistance traits identified")
    explanation_sections: ExplanationSections = Field(..., description="Detailed explanation sections")
    educational_content: Dict[str, EducationalContent] = Field(default_factory=dict, description="Educational content")
    stewardship_guidelines: StewardshipGuidelines = Field(..., description="Stewardship guidelines")
    management_recommendations: ManagementRecommendations = Field(..., description="Management recommendations")
    durability_assessment: DurabilityAssessment = Field(..., description="Durability assessment")
    compliance_requirements: ComplianceRequirements = Field(..., description="Compliance requirements")
    generated_at: str = Field(..., description="Generation timestamp")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    
    @validator('confidence_score')
    def validate_confidence_score(cls, v):
        """Validate confidence score range."""
        if not isinstance(v, (int, float)):
            return 0.0
        return max(0.0, min(1.0, float(v)))


class EducationalContentRequest(BaseModel):
    """Request model for educational content generation."""
    
    resistance_traits: List[ResistanceTrait] = Field(..., description="Resistance traits to explain")
    context: Dict[str, Any] = Field(..., description="Farm and environmental context")
    education_level: EducationLevel = Field(EducationLevel.INTERMEDIATE, description="Education level")
    include_mechanisms: bool = Field(True, description="Include mechanism explanations")
    include_management: bool = Field(True, description="Include management guidance")
    include_compliance: bool = Field(True, description="Include compliance information")


class EducationalContentResponse(BaseModel):
    """Response model for educational content generation."""
    
    educational_content: Dict[str, Any] = Field(..., description="Educational content")
    education_level: EducationLevel = Field(..., description="Education level")
    content_sections: List[str] = Field(..., description="Content sections")
    generated_at: str = Field(..., description="Generation timestamp")


class StewardshipGuidelinesRequest(BaseModel):
    """Request model for stewardship guidelines generation."""
    
    resistance_traits: List[ResistanceTrait] = Field(..., description="Resistance traits")
    context: Dict[str, Any] = Field(..., description="Farm and environmental context")
    compliance_level: ComplianceLevel = Field(ComplianceLevel.INTERMEDIATE, description="Compliance level")
    include_refuge_requirements: bool = Field(True, description="Include refuge requirements")
    include_monitoring: bool = Field(True, description="Include monitoring requirements")
    include_documentation: bool = Field(True, description="Include documentation requirements")


class StewardshipGuidelinesResponse(BaseModel):
    """Response model for stewardship guidelines generation."""
    
    stewardship_guidelines: Dict[str, Any] = Field(..., description="Stewardship guidelines")
    compliance_level: ComplianceLevel = Field(..., description="Compliance level")
    guideline_sections: List[str] = Field(..., description="Guideline sections")
    generated_at: str = Field(..., description="Generation timestamp")


class MechanismExplanationRequest(BaseModel):
    """Request model for mechanism explanation."""
    
    resistance_type: ResistanceType = Field(..., description="Type of resistance")
    include_details: bool = Field(True, description="Include detailed explanations")


class MechanismExplanationResponse(BaseModel):
    """Response model for mechanism explanation."""
    
    resistance_type: ResistanceType = Field(..., description="Type of resistance")
    mechanism: str = Field(..., description="Mechanism type")
    description: str = Field(..., description="Detailed description")
    durability: str = Field(..., description="Durability assessment")
    resistance_risk: str = Field(..., description="Resistance development risk")
    management_strategy: str = Field(..., description="Management strategy")
    target_organisms: Optional[List[str]] = Field(None, description="Target organisms")
    refuge_requirements: Optional[str] = Field(None, description="Refuge requirements")
    monitoring_requirements: Optional[List[str]] = Field(None, description="Monitoring requirements")


class ComplianceRequirementsRequest(BaseModel):
    """Request model for compliance requirements."""
    
    resistance_traits: List[str] = Field(..., description="List of resistance traits")
    region: str = Field("US", description="Geographic region")


class ComplianceRequirementsResponse(BaseModel):
    """Response model for compliance requirements."""
    
    resistance_traits: List[str] = Field(..., description="Resistance traits")
    region: str = Field(..., description="Geographic region")
    compliance_requirements: ComplianceRequirements = Field(..., description="Compliance requirements")
    generated_at: str = Field(..., description="Generation timestamp")


class DurabilityAssessmentRequest(BaseModel):
    """Request model for durability assessment."""
    
    resistance_traits: List[str] = Field(..., description="List of resistance traits")
    context: Dict[str, Any] = Field(default_factory=dict, description="Environmental context")


class DurabilityAssessmentResponse(BaseModel):
    """Response model for durability assessment."""
    
    resistance_traits: List[str] = Field(..., description="Resistance traits")
    durability_assessment: DurabilityAssessment = Field(..., description="Durability assessment")
    generated_at: str = Field(..., description="Generation timestamp")


class ResistanceExplanationValidator:
    """Validator for resistance explanation models."""
    
    @staticmethod
    def validate_resistance_traits(traits: List[Dict[str, Any]]) -> List[ResistanceTrait]:
        """Validate and convert resistance traits."""
        validated_traits = []
        
        for trait_data in traits:
            try:
                trait = ResistanceTrait(**trait_data)
                validated_traits.append(trait)
            except Exception as e:
                # Log validation error and skip invalid trait
                continue
        
        return validated_traits
    
    @staticmethod
    def validate_explanation_request(request_data: Dict[str, Any]) -> ResistanceExplanationRequest:
        """Validate resistance explanation request."""
        try:
            return ResistanceExplanationRequest(**request_data)
        except Exception as e:
            raise ValueError(f"Invalid resistance explanation request: {str(e)}")
    
    @staticmethod
    def validate_educational_content_request(request_data: Dict[str, Any]) -> EducationalContentRequest:
        """Validate educational content request."""
        try:
            return EducationalContentRequest(**request_data)
        except Exception as e:
            raise ValueError(f"Invalid educational content request: {str(e)}")
    
    @staticmethod
    def validate_stewardship_guidelines_request(request_data: Dict[str, Any]) -> StewardshipGuidelinesRequest:
        """Validate stewardship guidelines request."""
        try:
            return StewardshipGuidelinesRequest(**request_data)
        except Exception as e:
            raise ValueError(f"Invalid stewardship guidelines request: {str(e)}")
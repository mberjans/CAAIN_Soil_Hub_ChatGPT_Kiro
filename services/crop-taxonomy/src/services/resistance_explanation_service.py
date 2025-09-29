"""
Resistance Recommendation Explanations and Education Service

This service provides comprehensive resistance-specific educational content and explanations
for crop variety recommendations, focusing on resistance mechanisms, management education,
and stewardship guidelines.

TICKET-005_crop-variety-recommendations-10.3: Add comprehensive resistance recommendation explanations and education
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum
import json

logger = logging.getLogger(__name__)


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


class ResistanceExplanationService:
    """
    Service for generating comprehensive resistance-specific explanations and educational content.
    
    This service provides:
    - Resistance mechanism explanations
    - Resistance management education
    - Stewardship guidelines and compliance
    - Durability and sustainability information
    - Best practices and recommendations
    - Regulatory requirements and compliance
    """
    
    def __init__(self):
        """Initialize the resistance explanation service."""
        self.resistance_knowledge_base = self._initialize_resistance_knowledge()
        self.educational_content = self._initialize_educational_content()
        self.stewardship_guidelines = self._initialize_stewardship_guidelines()
        self.regulatory_requirements = self._initialize_regulatory_requirements()
        
    def _initialize_resistance_knowledge(self) -> Dict[str, Any]:
        """Initialize comprehensive resistance knowledge base."""
        return {
            "bt_toxin": {
                "mechanism": "Protein inhibition",
                "description": "Bacillus thuringiensis (Bt) toxins bind to specific receptors in insect gut, causing cell lysis and death",
                "target_pests": ["corn_borer", "corn_rootworm", "cotton_bollworm"],
                "durability": "High when properly managed with refuge requirements",
                "resistance_risk": "Medium - requires refuge compliance",
                "management_strategy": "Refuge requirements, resistance monitoring, rotation"
            },
            "herbicide_tolerance": {
                "mechanism": "Metabolic detoxification",
                "description": "Enhanced enzyme activity breaks down herbicides before they can cause damage",
                "target_herbicides": ["glyphosate", "glufosinate", "2,4-D", "dicamba"],
                "durability": "Variable - depends on herbicide and management",
                "resistance_risk": "High - requires integrated weed management",
                "management_strategy": "Herbicide rotation, tank mixing, cultural practices"
            },
            "disease_resistance": {
                "mechanism": "Structural modification",
                "description": "Genetic modifications prevent pathogen attachment or infection",
                "target_diseases": ["rust", "blight", "mildew", "smut"],
                "durability": "Medium to High - depends on pathogen evolution",
                "resistance_risk": "Low to Medium - pathogen adaptation possible",
                "management_strategy": "Variety rotation, fungicide integration, monitoring"
            },
            "insect_resistance": {
                "mechanism": "Protein inhibition",
                "description": "Toxic proteins target specific insect species while preserving beneficial insects",
                "target_insects": ["aphids", "thrips", "whiteflies", "beetles"],
                "durability": "High with proper management",
                "resistance_risk": "Medium - requires resistance management",
                "management_strategy": "Refuge requirements, monitoring, biological control"
            }
        }
    
    def _initialize_educational_content(self) -> Dict[str, Any]:
        """Initialize educational content for resistance management."""
        return {
            "resistance_management_principles": {
                "title": "Resistance Management Principles",
                "content": [
                    "Understand the resistance mechanism and its limitations",
                    "Implement integrated pest management (IPM) strategies",
                    "Monitor pest populations and resistance development",
                    "Rotate resistance traits and management practices",
                    "Maintain refuge requirements for Bt crops",
                    "Use economic thresholds for treatment decisions",
                    "Document management practices and outcomes"
                ]
            },
            "stewardship_best_practices": {
                "title": "Stewardship Best Practices",
                "content": [
                    "Follow label instructions and regulatory requirements",
                    "Implement refuge requirements for Bt crops",
                    "Rotate crops and resistance traits",
                    "Monitor fields regularly for pest pressure",
                    "Use multiple modes of action when possible",
                    "Maintain detailed records of management practices",
                    "Participate in resistance monitoring programs"
                ]
            },
            "durability_factors": {
                "title": "Resistance Durability Factors",
                "content": [
                    "Genetic diversity in pest populations",
                    "Refuge compliance and effectiveness",
                    "Management practice diversity",
                    "Environmental conditions and selection pressure",
                    "Pest biology and reproduction rates",
                    "Economic factors affecting management decisions"
                ]
            }
        }
    
    def _initialize_stewardship_guidelines(self) -> Dict[str, Any]:
        """Initialize stewardship guidelines and compliance requirements."""
        return {
            "bt_crops": {
                "refuge_requirements": {
                    "corn": {
                        "structured_refuge": "20% of corn acres within 0.5 miles",
                        "in_field_refuge": "5% of field area",
                        "seed_blend": "5% non-Bt seed mixed with Bt seed"
                    },
                    "cotton": {
                        "structured_refuge": "20% of cotton acres within 0.5 miles",
                        "in_field_refuge": "5% of field area"
                    }
                },
                "compliance_monitoring": [
                    "Annual refuge compliance verification",
                    "Pest population monitoring",
                    "Resistance development tracking",
                    "Management practice documentation"
                ]
            },
            "herbicide_tolerant_crops": {
                "resistance_management": {
                    "herbicide_rotation": "Rotate herbicide modes of action",
                    "tank_mixing": "Use multiple herbicides when possible",
                    "cultural_practices": "Implement crop rotation and tillage",
                    "monitoring": "Regular weed population assessment"
                },
                "compliance_requirements": [
                    "Follow herbicide label instructions",
                    "Implement resistance management plans",
                    "Document herbicide applications",
                    "Participate in resistance monitoring"
                ]
            }
        }
    
    def _initialize_regulatory_requirements(self) -> Dict[str, Any]:
        """Initialize regulatory requirements and compliance information."""
        return {
            "usda_requirements": {
                "bt_crops": [
                    "Refuge compliance verification",
                    "Resistance monitoring participation",
                    "Management plan documentation",
                    "Annual compliance reporting"
                ],
                "herbicide_tolerant_crops": [
                    "Label compliance",
                    "Resistance management implementation",
                    "Application record keeping",
                    "Environmental protection measures"
                ]
            },
            "epa_requirements": {
                "pesticide_resistance": [
                    "Resistance management plan development",
                    "Monitoring and reporting requirements",
                    "Label compliance and restrictions",
                    "Environmental impact assessment"
                ]
            },
            "state_requirements": {
                "variable_by_state": [
                    "Check state-specific regulations",
                    "Comply with local restrictions",
                    "Participate in state monitoring programs",
                    "Follow state extension recommendations"
                ]
            }
        }
    
    async def generate_resistance_explanation(
        self,
        variety_data: Dict[str, Any],
        pest_resistance_data: Dict[str, Any],
        context: Dict[str, Any],
        explanation_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive resistance explanation for a variety recommendation.
        
        Args:
            variety_data: Variety information and characteristics
            pest_resistance_data: Pest resistance analysis results
            context: Farm and environmental context
            explanation_options: Options for explanation generation
            
        Returns:
            Comprehensive resistance explanation with educational content
        """
        try:
            explanation_id = f"resistance_explanation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Extract resistance traits
            resistance_traits = self._extract_resistance_traits(variety_data)
            
            # Generate explanation sections
            explanation_sections = await self._generate_explanation_sections(
                resistance_traits, pest_resistance_data, context
            )
            
            # Generate educational content
            educational_content = self._generate_educational_content(
                resistance_traits, context
            )
            
            # Generate stewardship guidelines
            stewardship_guidelines = self._generate_stewardship_guidelines(
                resistance_traits, context
            )
            
            # Generate management recommendations
            management_recommendations = self._generate_management_recommendations(
                resistance_traits, pest_resistance_data, context
            )
            
            # Generate durability assessment
            durability_assessment = self._generate_durability_assessment(
                resistance_traits, context
            )
            
            # Generate compliance requirements
            compliance_requirements = self._generate_compliance_requirements(
                resistance_traits, context
            )
            
            return {
                "explanation_id": explanation_id,
                "variety_id": variety_data.get("variety_id"),
                "variety_name": variety_data.get("variety_name"),
                "resistance_traits": resistance_traits,
                "explanation_sections": explanation_sections,
                "educational_content": educational_content,
                "stewardship_guidelines": stewardship_guidelines,
                "management_recommendations": management_recommendations,
                "durability_assessment": durability_assessment,
                "compliance_requirements": compliance_requirements,
                "generated_at": datetime.utcnow().isoformat(),
                "confidence_score": self._calculate_confidence_score(
                    resistance_traits, pest_resistance_data
                )
            }
            
        except Exception as e:
            logger.error(f"Error generating resistance explanation: {e}")
            raise
    
    def _extract_resistance_traits(self, variety_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract resistance traits from variety data."""
        resistance_traits = []
        
        # Extract Bt traits
        bt_traits = variety_data.get("bt_traits", [])
        for trait in bt_traits:
            resistance_traits.append({
                "type": ResistanceType.BT_TOXIN,
                "trait_name": trait.get("name"),
                "target_pests": trait.get("target_pests", []),
                "mechanism": trait.get("mechanism"),
                "efficacy": trait.get("efficacy", "High")
            })
        
        # Extract herbicide tolerance traits
        herbicide_traits = variety_data.get("herbicide_tolerance", [])
        for trait in herbicide_traits:
            resistance_traits.append({
                "type": ResistanceType.HERBICIDE_TOLERANCE,
                "trait_name": trait.get("name"),
                "target_herbicides": trait.get("target_herbicides", []),
                "mechanism": trait.get("mechanism"),
                "efficacy": trait.get("efficacy", "High")
            })
        
        # Extract disease resistance traits
        disease_traits = variety_data.get("disease_resistance", [])
        for trait in disease_traits:
            resistance_traits.append({
                "type": ResistanceType.DISEASE_RESISTANCE,
                "trait_name": trait.get("name"),
                "target_diseases": trait.get("target_diseases", []),
                "mechanism": trait.get("mechanism"),
                "efficacy": trait.get("efficacy", "Medium")
            })
        
        return resistance_traits
    
    async def _generate_explanation_sections(
        self,
        resistance_traits: List[Dict[str, Any]],
        pest_resistance_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate detailed explanation sections."""
        sections = {}
        
        # Resistance mechanism explanations
        sections["mechanism_explanations"] = self._explain_resistance_mechanisms(resistance_traits)
        
        # Pest pressure analysis
        sections["pest_pressure_analysis"] = self._analyze_pest_pressure(
            pest_resistance_data, context
        )
        
        # Resistance effectiveness
        sections["resistance_effectiveness"] = self._assess_resistance_effectiveness(
            resistance_traits, pest_resistance_data
        )
        
        # Risk assessment
        sections["risk_assessment"] = self._assess_resistance_risks(
            resistance_traits, context
        )
        
        return sections
    
    def _explain_resistance_mechanisms(self, resistance_traits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Explain resistance mechanisms for each trait."""
        explanations = {}
        
        for trait in resistance_traits:
            trait_type = trait["type"]
            trait_name = trait["trait_name"]
            
            if trait_type in self.resistance_knowledge_base:
                knowledge = self.resistance_knowledge_base[trait_type]
                
                explanations[trait_name] = {
                    "mechanism": knowledge["mechanism"],
                    "description": knowledge["description"],
                    "target_organisms": knowledge.get(f"target_{trait_type.split('_')[0]}s", []),
                    "durability": knowledge["durability"],
                    "resistance_risk": knowledge["resistance_risk"],
                    "management_strategy": knowledge["management_strategy"]
                }
        
        return explanations
    
    def _analyze_pest_pressure(
        self,
        pest_resistance_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze regional pest pressure and resistance implications."""
        regional_pressure = pest_resistance_data.get("regional_pressure", {})
        
        return {
            "current_pest_pressure": regional_pressure.get("current_pressure", "Unknown"),
            "historical_trends": regional_pressure.get("historical_trends", []),
            "resistance_development": regional_pressure.get("resistance_development", "Unknown"),
            "management_implications": self._derive_management_implications(regional_pressure),
            "monitoring_recommendations": self._generate_monitoring_recommendations(regional_pressure)
        }
    
    def _assess_resistance_effectiveness(
        self,
        resistance_traits: List[Dict[str, Any]],
        pest_resistance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess effectiveness of resistance traits against current pest pressure."""
        effectiveness_scores = {}
        
        for trait in resistance_traits:
            trait_name = trait["trait_name"]
            trait_type = trait["type"]
            
            # Get pest pressure for this trait type
            relevant_pests = self._get_relevant_pests(trait_type, pest_resistance_data)
            
            effectiveness_scores[trait_name] = {
                "overall_effectiveness": trait.get("efficacy", "Unknown"),
                "target_pest_coverage": len(relevant_pests),
                "resistance_durability": self._assess_trait_durability(trait),
                "management_requirements": self._get_management_requirements(trait_type)
            }
        
        return effectiveness_scores
    
    def _assess_resistance_risks(
        self,
        resistance_traits: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess risks associated with resistance traits."""
        risks = {
            "resistance_development_risk": "Medium",
            "environmental_risks": [],
            "economic_risks": [],
            "regulatory_risks": [],
            "mitigation_strategies": []
        }
        
        for trait in resistance_traits:
            trait_type = trait["type"]
            
            if trait_type == ResistanceType.BT_TOXIN:
                risks["resistance_development_risk"] = "Medium"
                risks["environmental_risks"].append("Non-target organism effects")
                risks["mitigation_strategies"].append("Refuge requirements")
            
            elif trait_type == ResistanceType.HERBICIDE_TOLERANCE:
                risks["resistance_development_risk"] = "High"
                risks["environmental_risks"].append("Herbicide drift")
                risks["economic_risks"].append("Increased herbicide costs")
                risks["mitigation_strategies"].append("Herbicide rotation")
        
        return risks
    
    def _generate_educational_content(
        self,
        resistance_traits: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate educational content for resistance management."""
        content = {
            "resistance_management_principles": self.educational_content["resistance_management_principles"],
            "stewardship_best_practices": self.educational_content["stewardship_best_practices"],
            "durability_factors": self.educational_content["durability_factors"],
            "trait_specific_education": {}
        }
        
        # Generate trait-specific educational content
        for trait in resistance_traits:
            trait_type = trait["type"]
            trait_name = trait["trait_name"]
            
            content["trait_specific_education"][trait_name] = {
                "mechanism_explanation": self._get_mechanism_explanation(trait_type),
                "management_guidance": self._get_management_guidance(trait_type),
                "monitoring_requirements": self._get_monitoring_requirements(trait_type),
                "compliance_requirements": self._get_compliance_requirements(trait_type)
            }
        
        return content
    
    def _generate_stewardship_guidelines(
        self,
        resistance_traits: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate stewardship guidelines for resistance traits."""
        guidelines = {
            "refuge_requirements": {},
            "monitoring_requirements": [],
            "documentation_requirements": [],
            "compliance_checklist": []
        }
        
        for trait in resistance_traits:
            trait_type = trait["type"]
            
            if trait_type == ResistanceType.BT_TOXIN:
                guidelines["refuge_requirements"] = self.stewardship_guidelines["bt_crops"]["refuge_requirements"]
                guidelines["monitoring_requirements"].extend(
                    self.stewardship_guidelines["bt_crops"]["compliance_monitoring"]
                )
            
            elif trait_type == ResistanceType.HERBICIDE_TOLERANCE:
                guidelines["monitoring_requirements"].extend(
                    self.stewardship_guidelines["herbicide_tolerant_crops"]["resistance_management"]
                )
                guidelines["compliance_checklist"].extend(
                    self.stewardship_guidelines["herbicide_tolerant_crops"]["compliance_requirements"]
                )
        
        return guidelines
    
    def _generate_management_recommendations(
        self,
        resistance_traits: List[Dict[str, Any]],
        pest_resistance_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate management recommendations for resistance traits."""
        recommendations = {
            "immediate_actions": [],
            "seasonal_management": [],
            "long_term_strategy": [],
            "monitoring_schedule": [],
            "record_keeping": []
        }
        
        for trait in resistance_traits:
            trait_type = trait["type"]
            
            if trait_type == ResistanceType.BT_TOXIN:
                recommendations["immediate_actions"].append("Verify refuge compliance")
                recommendations["seasonal_management"].append("Monitor pest populations")
                recommendations["long_term_strategy"].append("Rotate Bt traits")
            
            elif trait_type == ResistanceType.HERBICIDE_TOLERANCE:
                recommendations["immediate_actions"].append("Develop herbicide rotation plan")
                recommendations["seasonal_management"].append("Monitor weed populations")
                recommendations["long_term_strategy"].append("Implement integrated weed management")
        
        return recommendations
    
    def _generate_durability_assessment(
        self,
        resistance_traits: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate durability assessment for resistance traits."""
        assessment = {
            "overall_durability": "Medium",
            "durability_factors": [],
            "durability_timeline": {},
            "sustainability_score": 0.0
        }
        
        durability_scores = []
        
        for trait in resistance_traits:
            trait_type = trait["type"]
            trait_name = trait["trait_name"]
            
            if trait_type in self.resistance_knowledge_base:
                knowledge = self.resistance_knowledge_base[trait_type]
                durability = knowledge["durability"]
                
                assessment["durability_timeline"][trait_name] = durability
                durability_scores.append(self._score_durability(durability))
        
        if durability_scores:
            assessment["overall_durability"] = self._calculate_overall_durability(durability_scores)
            assessment["sustainability_score"] = sum(durability_scores) / len(durability_scores)
        
        return assessment
    
    def _generate_compliance_requirements(
        self,
        resistance_traits: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate compliance requirements for resistance traits."""
        requirements = {
            "usda_requirements": [],
            "epa_requirements": [],
            "state_requirements": [],
            "label_requirements": [],
            "documentation_requirements": []
        }
        
        for trait in resistance_traits:
            trait_type = trait["type"]
            
            if trait_type == ResistanceType.BT_TOXIN:
                requirements["usda_requirements"].extend(
                    self.regulatory_requirements["usda_requirements"]["bt_crops"]
                )
            
            elif trait_type == ResistanceType.HERBICIDE_TOLERANCE:
                requirements["usda_requirements"].extend(
                    self.regulatory_requirements["usda_requirements"]["herbicide_tolerant_crops"]
                )
                requirements["epa_requirements"].extend(
                    self.regulatory_requirements["epa_requirements"]["pesticide_resistance"]
                )
        
        # Add state-specific requirements
        requirements["state_requirements"].extend(
            self.regulatory_requirements["state_requirements"]["variable_by_state"]
        )
        
        return requirements
    
    def _calculate_confidence_score(
        self,
        resistance_traits: List[Dict[str, Any]],
        pest_resistance_data: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for resistance explanation."""
        base_confidence = 0.7
        
        # Adjust based on trait data completeness
        trait_completeness = len(resistance_traits) / 3.0  # Normalize to 0-1
        completeness_bonus = trait_completeness * 0.2
        
        # Adjust based on pest resistance data quality
        data_quality = pest_resistance_data.get("data_quality_score", 0.5)
        quality_bonus = data_quality * 0.1
        
        final_confidence = min(base_confidence + completeness_bonus + quality_bonus, 1.0)
        return round(final_confidence, 2)
    
    # Helper methods
    def _derive_management_implications(self, regional_pressure: Dict[str, Any]) -> List[str]:
        """Derive management implications from pest pressure data."""
        implications = []
        
        if regional_pressure.get("current_pressure") == "High":
            implications.append("Increased monitoring frequency required")
            implications.append("Consider additional management tactics")
        
        if regional_pressure.get("resistance_development") == "Detected":
            implications.append("Resistance management critical")
            implications.append("Implement refuge requirements")
        
        return implications
    
    def _generate_monitoring_recommendations(self, regional_pressure: Dict[str, Any]) -> List[str]:
        """Generate monitoring recommendations based on pest pressure."""
        recommendations = []
        
        recommendations.append("Weekly pest population monitoring")
        recommendations.append("Resistance development tracking")
        recommendations.append("Refuge compliance verification")
        
        if regional_pressure.get("current_pressure") == "High":
            recommendations.append("Increased monitoring frequency")
            recommendations.append("Early warning system implementation")
        
        return recommendations
    
    def _get_relevant_pests(self, trait_type: ResistanceType, pest_resistance_data: Dict[str, Any]) -> List[str]:
        """Get relevant pests for a specific resistance trait type."""
        if trait_type not in self.resistance_knowledge_base:
            return []
        
        knowledge = self.resistance_knowledge_base[trait_type]
        return knowledge.get(f"target_{trait_type.value.split('_')[0]}s", [])
    
    def _assess_trait_durability(self, trait: Dict[str, Any]) -> str:
        """Assess durability of a specific resistance trait."""
        trait_type = trait["type"]
        
        if trait_type in self.resistance_knowledge_base:
            return self.resistance_knowledge_base[trait_type]["durability"]
        
        return "Unknown"
    
    def _get_management_requirements(self, trait_type: ResistanceType) -> List[str]:
        """Get management requirements for a specific trait type."""
        if trait_type in self.resistance_knowledge_base:
            strategy = self.resistance_knowledge_base[trait_type]["management_strategy"]
            return strategy.split(", ")
        
        return []
    
    def _get_mechanism_explanation(self, trait_type: ResistanceType) -> str:
        """Get mechanism explanation for a trait type."""
        if trait_type in self.resistance_knowledge_base:
            return self.resistance_knowledge_base[trait_type]["description"]
        
        return "Mechanism explanation not available"
    
    def _get_management_guidance(self, trait_type: ResistanceType) -> str:
        """Get management guidance for a trait type."""
        if trait_type in self.resistance_knowledge_base:
            return self.resistance_knowledge_base[trait_type]["management_strategy"]
        
        return "Management guidance not available"
    
    def _get_monitoring_requirements(self, trait_type: ResistanceType) -> List[str]:
        """Get monitoring requirements for a trait type."""
        requirements = ["Regular pest population monitoring"]
        
        if trait_type == ResistanceType.BT_TOXIN:
            requirements.append("Refuge compliance monitoring")
            requirements.append("Resistance development tracking")
        
        return requirements
    
    def _get_compliance_requirements(self, trait_type: ResistanceType) -> List[str]:
        """Get compliance requirements for a trait type."""
        requirements = ["Follow label instructions"]
        
        if trait_type == ResistanceType.BT_TOXIN:
            requirements.append("Maintain refuge requirements")
            requirements.append("Document management practices")
        
        return requirements
    
    def _score_durability(self, durability: str) -> float:
        """Score durability on a 0-1 scale."""
        durability_scores = {
            "High": 0.9,
            "Medium": 0.6,
            "Low": 0.3,
            "Unknown": 0.5
        }
        
        return durability_scores.get(durability, 0.5)
    
    def _calculate_overall_durability(self, scores: List[float]) -> str:
        """Calculate overall durability from individual scores."""
        if not scores:
            return "Unknown"
        
        average_score = sum(scores) / len(scores)
        
        if average_score >= 0.8:
            return "High"
        elif average_score >= 0.6:
            return "Medium"
        else:
            return "Low"
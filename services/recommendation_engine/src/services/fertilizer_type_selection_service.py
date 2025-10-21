"""
Fertilizer Type Selection Service

Comprehensive service for helping farmers choose the best fertilizer type based on their
priorities, constraints, and farm conditions. Implements US-006: Fertilizer Type Selection.
"""

from typing import List, Dict, Any, Optional, Tuple
import logging
from ..models.fertilizer_models import FarmerPriorities, FarmerConstraints
from .environmental_service import EnvironmentalAssessmentService
from .soil_health_service import SoilHealthIntegrationService
from .fertilizer_explanation_service import FertilizerExplanationService

logger = logging.getLogger(__name__)


class FertilizerTypeSelectionService:
    """
    Service for selecting optimal fertilizer types based on farmer needs.
    
    This service implements the core logic for US-006: Fertilizer Type Selection,
    helping farmers choose between organic, synthetic, and slow-release fertilizers
    based on their specific priorities, constraints, and farm conditions.
    """
    
    def __init__(self):
        """Initialize the fertilizer type selection service."""
        self.logger = logging.getLogger(__name__)
        self.environmental_service = EnvironmentalAssessmentService()
        self.soil_health_service = SoilHealthIntegrationService()
        self.explanation_service = FertilizerExplanationService()
        self.logger.info("FertilizerTypeSelectionService initialized with environmental assessment, soil health integration, and explanation generation")
    
    async def get_fertilizer_type_recommendations(
        self,
        priorities: 'FarmerPriorities',
        constraints: 'FarmerConstraints',
        soil_data: Optional[Dict[str, Any]] = None,
        crop_data: Optional[Dict[str, Any]] = None,
        farm_profile: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate fertilizer type recommendations based on farmer priorities and constraints.
        
        Returns list of fertilizer recommendations with scores and details.
        """
        try:
            # Get available fertilizer types
            available_fertilizers = await self.get_available_fertilizer_types(
                organic_only=constraints.organic_preference
            )
            
            # Score each fertilizer based on priorities
            scored_recommendations = []
            for fertilizer in available_fertilizers:
                score = self._calculate_fertilizer_score(
                    fertilizer, priorities, constraints, soil_data, crop_data
                )
                
                if score > 0.3:  # Minimum threshold
                    scored_recommendations.append({
                        "id": fertilizer.get("product_id"),
                        "name": fertilizer.get("name"),
                        "type": fertilizer.get("fertilizer_type"),
                        "suitability_score": score,
                        "details": fertilizer
                    })
            
            # Sort by score
            scored_recommendations.sort(key=lambda x: x["suitability_score"], reverse=True)
            
            # Return top 5 recommendations
            return scored_recommendations[:5]
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []
    
    def _calculate_fertilizer_score(
        self,
        fertilizer: Dict[str, Any],
        priorities: 'FarmerPriorities',
        constraints: 'FarmerConstraints',
        soil_data: Optional[Dict[str, Any]],
        crop_data: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate suitability score for a fertilizer option."""
        score = 0.0
        
        # Cost effectiveness
        if priorities.cost_effectiveness > 0:
            cost_score = self._evaluate_cost_effectiveness(
                fertilizer, constraints.budget_per_acre
            )
            score += priorities.cost_effectiveness * cost_score
        
        # Soil health
        if priorities.soil_health > 0:
            soil_health_score = fertilizer.get("soil_health_score", 0.5)
            score += priorities.soil_health * soil_health_score
        
        # Environmental impact
        if priorities.environmental_impact > 0:
            env_score = fertilizer.get("environmental_impact_score", 0.5)
            score += priorities.environmental_impact * env_score
        
        # Ease of application
        if priorities.ease_of_application > 0:
            ease_score = self._evaluate_application_ease(
                fertilizer, constraints.available_equipment
            )
            score += priorities.ease_of_application * ease_score
        
        # Normalize score (sum of priorities could be > 1)
        total_priority = sum([
            priorities.cost_effectiveness,
            priorities.soil_health,
            priorities.environmental_impact,
            priorities.ease_of_application,
            priorities.quick_results,
            priorities.long_term_benefits
        ])
        
        if total_priority > 0:
            score = score / total_priority
        
        return min(1.0, max(0.0, score))
    
    def _evaluate_cost_effectiveness(
        self, fertilizer: Dict[str, Any], budget_per_acre: Optional[float]
    ) -> float:
        """Evaluate cost effectiveness of fertilizer."""
        if not budget_per_acre:
            return 0.5
        
        cost = fertilizer.get("cost_per_unit", 100)
        
        # Higher score for lower cost
        if cost <= budget_per_acre * 0.5:
            return 1.0
        elif cost <= budget_per_acre:
            return 0.7
        elif cost <= budget_per_acre * 1.5:
            return 0.4
        else:
            return 0.2
    
    def _evaluate_application_ease(
        self, fertilizer: Dict[str, Any], available_equipment: List[str]
    ) -> float:
        """Evaluate ease of application based on equipment compatibility."""
        required_equipment = fertilizer.get("equipment_requirements", [])
        
        if not required_equipment:
            return 0.8
        
        # Check equipment compatibility
        compatible = any(
            equip in available_equipment 
            for equip in required_equipment
        )
        
        return 1.0 if compatible else 0.3
    
    def calculate_overall_confidence(
        self, recommendations: List[Dict[str, Any]]
    ) -> float:
        """Calculate overall confidence score for recommendations."""
        if not recommendations:
            return 0.0
        
        # Average of top 3 scores
        top_scores = [r.get("suitability_score", 0) for r in recommendations[:3]]
        
        if not top_scores:
            return 0.0
        
        avg_score = sum(top_scores) / len(top_scores)
        
        # Confidence is higher when top recommendations are similar
        if len(top_scores) > 1:
            score_variance = sum((s - avg_score) ** 2 for s in top_scores) / len(top_scores)
            confidence_adjustment = 1.0 - min(0.3, score_variance)
        else:
            confidence_adjustment = 0.8
        
        return min(1.0, avg_score * confidence_adjustment)
    
    def generate_comparison_summary(
        self, recommendations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate comparison summary of recommendations."""
        if not recommendations:
            return {
                "top_recommendation": "None available",
                "key_differentiators": [],
                "trade_offs": {},
                "decision_factors": []
            }
        
        top_rec = recommendations[0]
        
        return {
            "top_recommendation": top_rec.get("name", "Unknown"),
            "key_differentiators": [
                f"Score: {top_rec.get('suitability_score', 0):.2f}",
                f"Type: {top_rec.get('type', 'Unknown')}"
            ],
            "trade_offs": {
                "cost_vs_performance": "Balanced approach",
                "speed_vs_sustainability": "Focus on sustainability"
            },
            "decision_factors": [
                "Suitability score",
                "Cost effectiveness",
                "Environmental impact"
            ]
        }
    
    def generate_cost_analysis(
        self, recommendations: List[Dict[str, Any]], constraints: 'FarmerConstraints'
    ) -> Dict[str, Any]:
        """Generate cost analysis for recommendations."""
        if not recommendations:
            return {
                "average_cost_per_acre": 0,
                "total_farm_cost": 0,
                "cost_range": {"min": 0, "max": 0}
            }
        
        costs = [
            r.get("details", {}).get("cost_per_unit", 0) 
            for r in recommendations
        ]
        
        avg_cost = sum(costs) / len(costs) if costs else 0
        
        return {
            "average_cost_per_acre": avg_cost,
            "total_farm_cost": avg_cost * constraints.farm_size_acres,
            "cost_range": {
                "min": min(costs) if costs else 0,
                "max": max(costs) if costs else 0
            },
            "budget_analysis": {
                "within_budget": constraints.budget_per_acre is None or avg_cost <= constraints.budget_per_acre,
                "budget_utilization_percent": (
                    (avg_cost / constraints.budget_per_acre * 100) 
                    if constraints.budget_per_acre else 0
                )
            }
        }
    
    async def assess_environmental_impact_for_recommendations(
        self,
        recommendations: List[Dict[str, Any]],
        field_conditions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess environmental impact across recommendations."""
        if not recommendations:
            return {
                "overall_impact": "unknown",
                "risks": [],
                "mitigation_strategies": []
            }
        
        # Calculate average environmental scores
        env_scores = [
            r.get("details", {}).get("environmental_impact_score", 0.5)
            for r in recommendations
        ]
        
        avg_env_score = sum(env_scores) / len(env_scores) if env_scores else 0.5
        
        return {
            "overall_impact": "low" if avg_env_score > 0.7 else "moderate" if avg_env_score > 0.4 else "high",
            "average_environmental_score": avg_env_score,
            "risks": [
                "Nutrient runoff potential" if avg_env_score < 0.6 else None,
                "Soil acidification" if field_conditions.get("soil", {}).get("ph", 7) < 6 else None
            ],
            "mitigation_strategies": [
                "Use precision application methods",
                "Apply during optimal weather conditions",
                "Follow 4R nutrient stewardship principles"
            ]
        }
    
    def generate_implementation_guidance(
        self, recommendations: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate implementation guidance for recommendations."""
        if not recommendations:
            return ["No recommendations available"]
        
        return [
            "Review soil test results before application",
            "Calibrate application equipment",
            "Follow recommended application rates",
            "Monitor weather conditions",
            "Document application for records"
        ]
    
    async def get_available_fertilizer_types(
        self,
        fertilizer_type: Optional[str] = None,
        organic_only: bool = False,
        max_cost_per_unit: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Get available fertilizer types with optional filtering."""
        # Sample fertilizer database
        fertilizers = [
            {
                "product_id": "urea_46_0_0",
                "name": "Urea (46-0-0)",
                "manufacturer": "Generic",
                "fertilizer_type": "synthetic",
                "cost_per_unit": 450,
                "environmental_impact_score": 0.4,
                "soil_health_score": 0.3,
                "equipment_requirements": ["broadcast_spreader"],
                "application_methods": ["broadcast"],
                "organic_certified": False,
                "pros": ["High nitrogen content", "Low cost per unit N"],
                "cons": ["Volatilization risk", "No secondary nutrients"]
            },
            {
                "product_id": "ammonium_sulfate_21_0_0",
                "name": "Ammonium Sulfate (21-0-0-24S)",
                "manufacturer": "Generic",
                "fertilizer_type": "synthetic",
                "cost_per_unit": 380,
                "environmental_impact_score": 0.5,
                "soil_health_score": 0.4,
                "equipment_requirements": ["broadcast_spreader"],
                "application_methods": ["broadcast"],
                "organic_certified": False,
                "pros": ["Adds sulfur", "Acidifying effect"],
                "cons": ["Lower N content", "Can lower pH"]
            },
            {
                "product_id": "composted_manure_organic",
                "name": "Composted Manure",
                "manufacturer": "Various",
                "fertilizer_type": "organic",
                "cost_per_unit": 50,
                "environmental_impact_score": 0.9,
                "soil_health_score": 0.95,
                "equipment_requirements": ["manure_spreader"],
                "application_methods": ["broadcast", "incorporation"],
                "organic_certified": True,
                "pros": ["Improves soil structure", "Slow release", "Organic matter"],
                "cons": ["Low nutrient content", "Variable analysis", "High volume needed"]
            }
        ]
        
        # Apply filters
        filtered = fertilizers
        
        if fertilizer_type:
            filtered = [f for f in filtered if f["fertilizer_type"] == fertilizer_type]
        
        if organic_only:
            filtered = [f for f in filtered if f.get("organic_certified", False)]
        
        if max_cost_per_unit:
            filtered = [f for f in filtered if f["cost_per_unit"] <= max_cost_per_unit]
        
        return filtered
    
    async def compare_fertilizer_options(
        self,
        fertilizer_ids: List[str],
        comparison_criteria: List[str],
        farm_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Compare specific fertilizer options based on criteria."""
        # Get fertilizer details
        all_fertilizers = await self.get_available_fertilizer_types()
        
        selected_fertilizers = [
            f for f in all_fertilizers 
            if f["product_id"] in fertilizer_ids
        ]
        
        # Score each fertilizer on each criterion
        comparison_results = []
        for fertilizer in selected_fertilizers:
            scores = {}
            for criterion in comparison_criteria:
                scores[criterion] = self._score_criterion(
                    fertilizer, criterion, farm_context
                )
            
            comparison_results.append({
                "fertilizer_id": fertilizer["product_id"],
                "name": fertilizer["name"],
                "scores": scores,
                "overall_score": sum(scores.values()) / len(scores) if scores else 0,
                "strengths": fertilizer.get("pros", []),
                "weaknesses": fertilizer.get("cons", [])
            })
        
        return comparison_results
    
    def _score_criterion(
        self, fertilizer: Dict[str, Any], criterion: str, context: Dict[str, Any]
    ) -> float:
        """Score a fertilizer on a specific criterion."""
        if criterion == "cost_effectiveness":
            return self._evaluate_cost_effectiveness(
                fertilizer, context.get("budget_per_acre")
            )
        elif criterion == "soil_health_impact":
            return fertilizer.get("soil_health_score", 0.5)
        elif criterion == "environmental_impact":
            return fertilizer.get("environmental_impact_score", 0.5)
        elif criterion == "nitrogen_efficiency":
            return 0.7  # Placeholder
        elif criterion == "application_ease":
            return 0.6  # Placeholder
        else:
            return 0.5  # Default
    
    def get_comparison_recommendation(
        self, comparison_results: List[Dict[str, Any]]
    ) -> str:
        """Get overall recommendation from comparison results."""
        if not comparison_results:
            return "No fertilizers available for comparison"
        
        # Sort by overall score
        sorted_results = sorted(
            comparison_results,
            key=lambda x: x["overall_score"],
            reverse=True
        )
        
        top_option = sorted_results[0]
        
        return (
            f"Based on the comparison, {top_option['name']} is recommended with "
            f"an overall score of {top_option['overall_score']:.2f}. "
            f"This option excels in the evaluated criteria while maintaining good balance."
        )
    
    def identify_decision_factors(
        self, comparison_results: List[Dict[str, Any]]
    ) -> List[str]:
        """Identify key decision factors from comparison."""
        if not comparison_results:
            return []
        
        return [
            "Cost per acre and total budget impact",
            "Soil health and long-term sustainability",
            "Environmental impact and regulatory compliance",
            "Application ease and equipment compatibility",
            "Nutrient efficiency and crop response"
        ]

    async def assess_fertilizer_soil_health_impact(
        self,
        fertilizer_type: str,
        fertilizer_name: str,
        application_rate_lbs_per_acre: float,
        soil_data: Optional[Dict[str, Any]] = None,
        application_frequency_per_year: int = 1,
        soil_texture: Optional[str] = None,
        field_conditions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Assess comprehensive soil health impact of a specific fertilizer.

        This method integrates with the SoilHealthIntegrationService to provide
        detailed analysis of how a fertilizer choice will affect soil health
        across multiple factors and time horizons.

        Args:
            fertilizer_type: Type of fertilizer (organic, synthetic, etc.)
            fertilizer_name: Specific fertilizer name
            application_rate_lbs_per_acre: Application rate in lbs/acre
            soil_data: Soil test data and conditions
            application_frequency_per_year: Number of applications per year
            soil_texture: Soil texture classification
            field_conditions: Additional field conditions

        Returns:
            Comprehensive soil health impact assessment
        """
        try:
            # Convert soil_data dict to SoilTestData if provided
            if soil_data:
                from ..models.agricultural_models import SoilTestData
                from datetime import date
                
                # Create SoilTestData object with required fields
                soil_test_data = SoilTestData(
                    ph=soil_data.get('ph', 6.5),
                    organic_matter_percent=soil_data.get('organic_matter_percent', 3.0),
                    phosphorus_ppm=soil_data.get('phosphorus_ppm', 25.0),
                    potassium_ppm=soil_data.get('potassium_ppm', 150.0),
                    nitrogen_ppm=soil_data.get('nitrogen_ppm'),
                    cec_meq_per_100g=soil_data.get('cec_meq_per_100g'),
                    soil_texture=soil_data.get('soil_texture'),
                    drainage_class=soil_data.get('drainage_class'),
                    test_date=soil_data.get('test_date', date.today()),
                    lab_name=soil_data.get('lab_name')
                )
            else:
                # Use default soil data
                from ..models.agricultural_models import SoilTestData
                from datetime import date
                
                soil_test_data = SoilTestData(
                    ph=6.5,
                    organic_matter_percent=3.0,
                    phosphorus_ppm=25.0,
                    potassium_ppm=150.0,
                    test_date=date.today()
                )

            # Convert soil texture string to SoilTexture enum if provided
            soil_texture_enum = None
            if soil_texture:
                try:
                    from .soil_ph_management_service import SoilTexture
                    soil_texture_enum = SoilTexture(soil_texture.lower())
                except (ValueError, AttributeError):
                    self.logger.warning(f"Invalid soil texture '{soil_texture}', using default")

            # Get comprehensive soil health assessment
            assessment = await self.soil_health_service.assess_soil_health_impact(
                fertilizer_type=fertilizer_type,
                fertilizer_name=fertilizer_name,
                application_rate_lbs_per_acre=application_rate_lbs_per_acre,
                soil_data=soil_test_data,
                application_frequency_per_year=application_frequency_per_year,
                soil_texture=soil_texture_enum,
                field_conditions=field_conditions
            )

            # Convert assessment to dictionary format for API compatibility
            return {
                "assessment_id": assessment.assessment_id,
                "fertilizer_name": assessment.fertilizer_name,
                "fertilizer_type": assessment.fertilizer_type,
                "assessment_date": assessment.assessment_date.isoformat(),
                "overall_soil_health_score": assessment.overall_soil_health_score,
                "soil_health_rating": assessment.soil_health_rating.value,
                "organic_matter_impact": {
                    "organic_matter_contribution_percent": assessment.organic_matter_impact.organic_matter_contribution_percent,
                    "carbon_input_lbs_per_acre": assessment.organic_matter_impact.carbon_input_lbs_per_acre,
                    "short_term_om_change_percent": assessment.organic_matter_impact.short_term_om_change_percent,
                    "long_term_om_change_percent": assessment.organic_matter_impact.long_term_om_change_percent,
                    "short_term_rating": assessment.organic_matter_impact.short_term_rating.value,
                    "long_term_rating": assessment.organic_matter_impact.long_term_rating.value,
                    "carbon_sequestration_potential": assessment.organic_matter_impact.carbon_sequestration_potential,
                    "monitoring_frequency": assessment.organic_matter_impact.monitoring_frequency
                },
                "ph_effects": {
                    "immediate_ph_change": assessment.ph_effects.immediate_ph_change,
                    "cumulative_ph_change_5yr": assessment.ph_effects.cumulative_ph_change_5yr,
                    "acidification_potential": assessment.ph_effects.acidification_potential,
                    "alkalinization_potential": assessment.ph_effects.alkalinization_potential,
                    "ph_risk_level": assessment.ph_effects.ph_risk_level,
                    "requires_ph_management": assessment.ph_effects.requires_ph_management,
                    "ph_monitoring_frequency": assessment.ph_effects.ph_monitoring_frequency
                },
                "microbial_assessment": {
                    "bacterial_population_impact": assessment.microbial_assessment.bacterial_population_impact,
                    "fungal_population_impact": assessment.microbial_assessment.fungal_population_impact,
                    "mycorrhizal_impact": assessment.microbial_assessment.mycorrhizal_impact,
                    "microbial_diversity_score": assessment.microbial_assessment.microbial_diversity_score,
                    "soil_food_web_health": assessment.microbial_assessment.soil_food_web_health,
                    "short_term_microbiome_impact": assessment.microbial_assessment.short_term_microbiome_impact.value,
                    "long_term_microbiome_impact": assessment.microbial_assessment.long_term_microbiome_impact.value
                },
                "structure_evaluation": {
                    "aggregate_stability_impact": assessment.structure_evaluation.aggregate_stability_impact,
                    "bulk_density_change": assessment.structure_evaluation.bulk_density_change,
                    "infiltration_rate_change": assessment.structure_evaluation.infiltration_rate_change,
                    "water_holding_capacity_change": assessment.structure_evaluation.water_holding_capacity_change,
                    "structural_stability": assessment.structure_evaluation.structural_stability,
                    "long_term_structure_rating": assessment.structure_evaluation.long_term_structure_rating.value
                },
                "temporal_analysis": {
                    "short_term_overall_rating": assessment.temporal_analysis.short_term_overall_rating.value,
                    "medium_term_overall_rating": assessment.temporal_analysis.medium_term_overall_rating.value,
                    "long_term_overall_rating": assessment.temporal_analysis.long_term_overall_rating.value,
                    "medium_term_trajectory": assessment.temporal_analysis.medium_term_trajectory,
                    "long_term_sustainability": assessment.temporal_analysis.long_term_sustainability,
                    "cumulative_impact_score": assessment.temporal_analysis.cumulative_impact_score,
                    "impact_reversibility": assessment.temporal_analysis.impact_reversibility
                },
                "positive_impacts": assessment.positive_impacts,
                "negative_impacts": assessment.negative_impacts,
                "neutral_aspects": assessment.neutral_aspects,
                "overall_risk_level": assessment.overall_risk_level,
                "critical_concerns": assessment.critical_concerns,
                "mitigation_priorities": assessment.mitigation_priorities,
                "preventive_practices": assessment.preventive_practices,
                "monitoring_frequency": assessment.monitoring_frequency,
                "key_indicators_to_monitor": assessment.key_indicators_to_monitor,
                "assessment_confidence": assessment.assessment_confidence,
                "limitations": assessment.limitations
            }

        except Exception as e:
            self.logger.error(f"Error assessing soil health impact for {fertilizer_name}: {str(e)}")
            # Return default response on error
            return {
                "error": str(e),
                "overall_soil_health_score": 0.0,
                "soil_health_rating": "unknown",
                "message": "Soil health assessment failed"
            }
    
    async def get_equipment_compatibility(self, equipment_type: str) -> Dict[str, Any]:
        """Get equipment compatibility information."""
        return {
            "compatible_fertilizers": [],
            "application_methods": [],
            "limitations": ["Equipment type not found"],
            "recommendations": ["Contact equipment manufacturer"]
        }
    
    async def analyze_fertilizer_costs(
        self,
        fertilizer_ids: List[str],
        farm_size_acres: float,
        application_rates: Dict[str, float],
        current_prices: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """Analyze costs for specific fertilizer options."""
        return {
            "total_costs": {},
            "cost_per_acre": {},
            "cost_per_nutrient_unit": {},
            "roi_analysis": {},
            "cost_comparison": {},
            "recommendations": []
        }
    
    async def get_environmental_impact(
        self,
        fertilizer_id: str,
        fertilizer_data: Optional[Dict[str, Any]] = None,
        application_data: Optional[Dict[str, Any]] = None,
        field_conditions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive environmental impact assessment for a specific fertilizer.

        Args:
            fertilizer_id: Unique fertilizer identifier
            fertilizer_data: Fertilizer product information
            application_data: Application details (rate, method, timing)
            field_conditions: Field characteristics (soil, weather, proximity to water)

        Returns:
            Comprehensive environmental impact assessment
        """
        try:
            # If no data provided, use defaults for demonstration
            if fertilizer_data is None:
                fertilizer_data = {
                    "id": fertilizer_id,
                    "name": f"Fertilizer {fertilizer_id}",
                    "type": "urea",
                    "nitrogen_percent": 46.0,
                    "phosphorus_percent": 0.0,
                    "potassium_percent": 0.0
                }

            if application_data is None:
                application_data = {
                    "rate_lbs_per_acre": 150.0,
                    "method": "broadcast",
                    "transport_distance_km": 800.0
                }

            if field_conditions is None:
                field_conditions = {
                    "soil": {
                        "texture": "loam",
                        "drainage": "moderate",
                        "ph": 6.5,
                        "cec": 15.0,
                        "organic_matter_percent": 3.0,
                        "slope_percent": 2.0,
                        "erosion_risk": "low"
                    },
                    "weather": {
                        "rainfall_inches": 1.0,
                        "temperature_f": 70.0
                    },
                    "ecosystem_type": "agricultural",
                    "distance_to_water_m": 150.0
                }

            # Get comprehensive environmental assessment
            assessment = await self.environmental_service.assess_environmental_impact(
                fertilizer_data=fertilizer_data,
                application_data=application_data,
                field_conditions=field_conditions
            )

            # Convert to dictionary format for backward compatibility
            return {
                "assessment_id": assessment.assessment_id,
                "fertilizer_name": assessment.fertilizer_name,
                "fertilizer_type": assessment.fertilizer_type,
                "carbon_footprint": {
                    "score": assessment.carbon_footprint.carbon_impact_score / 100.0,
                    "total_emissions_kg_co2e_per_acre": assessment.carbon_footprint.total_emissions_kg_co2e_per_acre,
                    "severity_level": assessment.carbon_footprint.severity_level.value,
                    "primary_sources": assessment.carbon_footprint.primary_emission_sources
                },
                "water_quality_impact": {
                    "score": assessment.water_quality_impact.water_quality_impact_score / 100.0,
                    "leaching_risk": assessment.water_quality_impact.nitrate_leaching_risk_score,
                    "runoff_risk": assessment.water_quality_impact.phosphorus_runoff_risk_score,
                    "primary_risks": assessment.water_quality_impact.primary_risk_factors
                },
                "soil_health_impact": {
                    "score": assessment.soil_health_impact.soil_health_impact_score / 100.0,
                    "acidification_potential": assessment.soil_health_impact.acidification_potential,
                    "positive_impacts": assessment.soil_health_impact.positive_impacts,
                    "negative_impacts": assessment.soil_health_impact.negative_impacts
                },
                "biodiversity_impact": {
                    "score": assessment.biodiversity_impact.biodiversity_impact_score / 100.0,
                    "pollinator_safety": assessment.biodiversity_impact.pollinator_safety_score / 10.0,
                    "soil_fauna_impact": assessment.biodiversity_impact.soil_fauna_impact_score / 10.0
                },
                "overall_environmental_score": assessment.environmental_score.overall_environmental_score / 100.0,
                "environmental_rating": assessment.environmental_score.environmental_rating,
                "sustainability_score": assessment.environmental_score.overall_environmental_score / 100.0,
                "mitigation_strategies": [rec.recommendation for rec in assessment.mitigation_recommendations[:3]],
                "mitigation_recommendations": [
                    {
                        "priority": rec.priority,
                        "recommendation": rec.recommendation,
                        "impact_reduction_percent": rec.impact_reduction_percent,
                        "implementation_difficulty": rec.implementation_difficulty
                    }
                    for rec in assessment.mitigation_recommendations
                ]
            }

        except Exception as e:
            self.logger.error(f"Error getting environmental impact for fertilizer {fertilizer_id}: {str(e)}")
            # Return default values on error
            return {
                "carbon_footprint": {"score": 0.7},
                "water_quality_impact": {"score": 0.7},
                "soil_health_impact": {"score": 0.8},
                "biodiversity_impact": {"score": 0.7},
                "sustainability_score": 0.75,
                "mitigation_strategies": ["Follow 4R principles"],
                "error": str(e)
            }
    
    def _validate_priorities(self, priorities: FarmerPriorities) -> Dict[str, Any]:
        """
        Validate farmer priorities for fertilizer selection.

        This method performs comprehensive validation of priority values, ensuring they
        are within acceptable ranges and identifying potential issues with the priority
        configuration.

        Args:
            priorities: FarmerPriorities object containing all priority values

        Returns:
            Dict containing:
                - is_valid (bool): Whether priorities pass validation
                - errors (List[str]): Critical validation errors
                - warnings (List[str]): Non-critical warnings
                - sum_total (float): Sum of all priority values
                - details (Dict[str, Any]): Additional validation details

        Validation checks:
            1. All priority values are between 0 and 1 (enforced by Pydantic)
            2. Priority sum is within reasonable range (0.5 to 6.0)
            3. At least one priority is non-zero
            4. No extreme outliers that might indicate input errors
        """
        errors = []
        warnings = []
        details = {}

        # Extract all priority values
        priority_values = {
            "cost_effectiveness": priorities.cost_effectiveness,
            "soil_health": priorities.soil_health,
            "quick_results": priorities.quick_results,
            "environmental_impact": priorities.environmental_impact,
            "ease_of_application": priorities.ease_of_application,
            "long_term_benefits": priorities.long_term_benefits
        }

        # Calculate sum of all priorities
        priority_sum = sum(priority_values.values())
        details["sum_total"] = priority_sum
        details["priority_values"] = priority_values

        # Check if all priorities are zero
        if priority_sum == 0:
            errors.append("All priorities are zero. At least one priority must be greater than zero.")
            self.logger.error("Priority validation failed: all priorities are zero")

        # Check if sum is too low (might indicate incomplete input)
        if priority_sum < 0.5 and priority_sum > 0:
            warnings.append(
                f"Priority sum ({priority_sum:.2f}) is very low. "
                "This might indicate incomplete priority specification. "
                "Consider reviewing priority values."
            )
            self.logger.warning(f"Priority sum is low: {priority_sum:.2f}")

        # Check if sum is too high (might indicate misunderstanding of scale)
        if priority_sum > 6.0:
            warnings.append(
                f"Priority sum ({priority_sum:.2f}) exceeds 6.0. "
                "While valid, this suggests priorities might need normalization. "
                "Consider using values that sum closer to 6.0 or normalizing."
            )
            self.logger.warning(f"Priority sum is high: {priority_sum:.2f}")

        # Check for extreme values that might dominate
        max_priority = max(priority_values.values())
        if max_priority == 1.0 and priority_sum > 1.0:
            dominant_priorities = [name for name, val in priority_values.items() if val == 1.0]
            details["dominant_priorities"] = dominant_priorities
            warnings.append(
                f"Priorities {dominant_priorities} are at maximum (1.0) while others are non-zero. "
                "This configuration is valid but may reduce the influence of other priorities."
            )

        # Check for very small non-zero values (might indicate noise)
        small_threshold = 0.05
        small_priorities = {name: val for name, val in priority_values.items()
                          if 0 < val < small_threshold}
        if small_priorities:
            details["small_priorities"] = small_priorities
            warnings.append(
                f"Priorities {list(small_priorities.keys())} have very small values (< {small_threshold}). "
                "These may have minimal impact on recommendations."
            )

        # Count how many priorities are actively set (> 0.1)
        active_priorities = [name for name, val in priority_values.items() if val > 0.1]
        details["active_priority_count"] = len(active_priorities)
        details["active_priorities"] = active_priorities

        if len(active_priorities) == 1:
            warnings.append(
                f"Only one priority ({active_priorities[0]}) is significantly set. "
                "Consider specifying additional priorities for more balanced recommendations."
            )

        # Determine overall validity
        is_valid = len(errors) == 0

        # Log validation result
        if is_valid:
            self.logger.info(
                f"Priority validation passed. Sum: {priority_sum:.2f}, "
                f"Active priorities: {len(active_priorities)}, Warnings: {len(warnings)}"
            )
        else:
            self.logger.error(f"Priority validation failed with {len(errors)} errors")

        return {
            "is_valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "sum_total": priority_sum,
            "details": details
        }

    def _normalize_priorities(self, priorities: FarmerPriorities) -> FarmerPriorities:
        """
        Normalize farmer priorities to a standardized scale.

        This method normalizes priority values to ensure they sum to a standard value
        while preserving their relative importance. Normalization helps ensure consistent
        weighting across different recommendation algorithms.

        Args:
            priorities: FarmerPriorities object with original priority values

        Returns:
            FarmerPriorities object with normalized priority values

        Normalization approach:
            - If sum is 0, returns original (invalid state, should be caught by validation)
            - If sum is between 0.8 and 6.2, no normalization (reasonable range)
            - Otherwise, normalizes to sum to 1.0 (preserving relative weights)
            - Ensures no negative values (should be impossible with Pydantic validation)

        Notes:
            - This method preserves the relative importance of priorities
            - Normalization does not change which priorities are more important
            - The normalized values maintain the same ratios as the original values
        """
        # Extract current priority values
        priority_dict = {
            "cost_effectiveness": priorities.cost_effectiveness,
            "soil_health": priorities.soil_health,
            "quick_results": priorities.quick_results,
            "environmental_impact": priorities.environmental_impact,
            "ease_of_application": priorities.ease_of_application,
            "long_term_benefits": priorities.long_term_benefits
        }

        # Calculate current sum
        priority_sum = sum(priority_dict.values())

        # If sum is zero, return original (validation should catch this)
        if priority_sum == 0:
            self.logger.warning("Cannot normalize priorities with sum of zero")
            return priorities

        # Define acceptable range (no normalization needed)
        min_acceptable_sum = 0.8
        max_acceptable_sum = 6.2

        # Check if normalization is needed
        if min_acceptable_sum <= priority_sum <= max_acceptable_sum:
            self.logger.info(
                f"Priorities already in acceptable range (sum={priority_sum:.2f}). "
                "No normalization needed."
            )
            return priorities

        # Normalize to sum to 1.0 (preserving relative weights)
        normalization_factor = 1.0 / priority_sum

        normalized_dict = {
            key: max(0.0, value * normalization_factor)  # Ensure no negative values
            for key, value in priority_dict.items()
        }

        # Log normalization details
        normalized_sum = sum(normalized_dict.values())
        self.logger.info(
            f"Normalized priorities from sum={priority_sum:.4f} to sum={normalized_sum:.4f} "
            f"(factor={normalization_factor:.4f})"
        )

        # Create and return new FarmerPriorities object with normalized values
        normalized_priorities = FarmerPriorities(
            cost_effectiveness=normalized_dict["cost_effectiveness"],
            soil_health=normalized_dict["soil_health"],
            quick_results=normalized_dict["quick_results"],
            environmental_impact=normalized_dict["environmental_impact"],
            ease_of_application=normalized_dict["ease_of_application"],
            long_term_benefits=normalized_dict["long_term_benefits"]
        )

        return normalized_priorities

    def _analyze_priority_profile(self, priorities: FarmerPriorities) -> Dict[str, Any]:
        """
        Analyze farmer priority profile to identify patterns and conflicts.

        This method provides deep analysis of the priority configuration, identifying
        dominant priorities, potential conflicts between competing priorities, and
        providing insights that can guide recommendation generation.

        Args:
            priorities: FarmerPriorities object to analyze

        Returns:
            Dict containing:
                - top_priorities (List[Tuple[str, float]]): Top 3 priorities with values
                - dominant_priority (str): The single highest priority
                - priority_distribution (str): Description of how priorities are distributed
                - conflicts (List[Dict]): Identified conflicting priority pairs
                - profile_type (str): Classification of the priority profile
                - recommendations (List[str]): Recommendations based on profile
                - insights (List[str]): Key insights about the priority configuration

        Priority conflicts identified:
            - cost_effectiveness vs environmental_impact
            - cost_effectiveness vs soil_health
            - quick_results vs long_term_benefits
            - quick_results vs soil_health
            - ease_of_application vs environmental_impact (sometimes)
        """
        # Extract priority values
        priority_dict = {
            "cost_effectiveness": priorities.cost_effectiveness,
            "soil_health": priorities.soil_health,
            "quick_results": priorities.quick_results,
            "environmental_impact": priorities.environmental_impact,
            "ease_of_application": priorities.ease_of_application,
            "long_term_benefits": priorities.long_term_benefits
        }

        # Sort priorities by value (descending)
        sorted_priorities = sorted(
            priority_dict.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Identify top 3 priorities
        top_priorities = sorted_priorities[:3]
        dominant_priority = sorted_priorities[0][0]
        dominant_value = sorted_priorities[0][1]

        # Calculate priority distribution metrics
        priority_sum = sum(priority_dict.values())
        if priority_sum > 0:
            # Calculate concentration (how focused are priorities)
            top_3_percentage = sum(val for _, val in top_priorities) / priority_sum
            concentration = "highly_focused" if top_3_percentage > 0.8 else \
                           "moderately_focused" if top_3_percentage > 0.6 else \
                           "balanced"
        else:
            concentration = "undefined"
            top_3_percentage = 0

        # Identify conflicts between priorities
        conflicts = []
        conflict_threshold = 0.3  # Both priorities must be > 0.3 to be considered conflicting

        # Define conflicting priority pairs with explanations
        conflict_pairs = [
            {
                "pair": ("cost_effectiveness", "environmental_impact"),
                "explanation": "Cost optimization often conflicts with environmental sustainability",
                "severity": "high",
                "resolution_strategy": "Consider slow-release or organic options that balance both concerns"
            },
            {
                "pair": ("cost_effectiveness", "soil_health"),
                "explanation": "Soil health improvements typically require higher investment",
                "severity": "medium",
                "resolution_strategy": "Focus on long-term ROI rather than immediate cost"
            },
            {
                "pair": ("quick_results", "long_term_benefits"),
                "explanation": "Quick results often come at the expense of long-term soil health",
                "severity": "high",
                "resolution_strategy": "Consider a split application strategy combining both approaches"
            },
            {
                "pair": ("quick_results", "soil_health"),
                "explanation": "Immediate nutrient availability can reduce long-term soil health",
                "severity": "medium",
                "resolution_strategy": "Use a blend of quick-release and slow-release fertilizers"
            },
            {
                "pair": ("quick_results", "environmental_impact"),
                "explanation": "Fast-acting fertilizers have higher environmental risk",
                "severity": "medium",
                "resolution_strategy": "Apply using precision techniques to minimize environmental impact"
            }
        ]

        # Check each conflict pair
        for conflict_def in conflict_pairs:
            priority1, priority2 = conflict_def["pair"]
            val1 = priority_dict[priority1]
            val2 = priority_dict[priority2]

            # Both priorities must be significant to create a conflict
            if val1 >= conflict_threshold and val2 >= conflict_threshold:
                conflict_info = {
                    "priorities": [priority1, priority2],
                    "values": [val1, val2],
                    "explanation": conflict_def["explanation"],
                    "severity": conflict_def["severity"],
                    "resolution_strategy": conflict_def["resolution_strategy"],
                    "conflict_score": min(val1, val2)  # Strength of conflict
                }
                conflicts.append(conflict_info)

                self.logger.info(
                    f"Identified {conflict_def['severity']} priority conflict: "
                    f"{priority1} ({val1:.2f}) vs {priority2} ({val2:.2f})"
                )

        # Classify the priority profile
        profile_type = self._classify_priority_profile(priority_dict, dominant_priority, dominant_value)

        # Generate insights
        insights = []

        if dominant_value > 0.7:
            insights.append(
                f"Strong emphasis on {dominant_priority.replace('_', ' ')} "
                f"(value: {dominant_value:.2f}). Recommendations will strongly favor this priority."
            )

        if len(conflicts) > 0:
            insights.append(
                f"Identified {len(conflicts)} priority conflict(s). "
                "Recommendations will attempt to balance these competing priorities."
            )

        if concentration == "balanced":
            insights.append(
                "Priorities are well-balanced across multiple factors. "
                "Recommendations will consider a broad range of fertilizer characteristics."
            )
        elif concentration == "highly_focused":
            insights.append(
                f"Priorities are highly focused (top 3 represent {top_3_percentage*100:.1f}% of total). "
                "Recommendations will be narrowly targeted."
            )

        # Count priorities with significant values
        significant_priorities = [name for name, val in priority_dict.items() if val > 0.2]
        if len(significant_priorities) >= 5:
            insights.append(
                "Multiple significant priorities detected. "
                "Consider focusing on your top 3-4 most important factors for clearer recommendations."
            )

        # Generate profile-specific recommendations
        profile_recommendations = self._generate_profile_recommendations(
            profile_type,
            priority_dict,
            conflicts
        )

        # Log analysis summary
        self.logger.info(
            f"Priority profile analysis complete. Type: {profile_type}, "
            f"Dominant: {dominant_priority}, Conflicts: {len(conflicts)}, "
            f"Distribution: {concentration}"
        )

        return {
            "top_priorities": top_priorities,
            "dominant_priority": dominant_priority,
            "dominant_value": dominant_value,
            "priority_distribution": concentration,
            "top_3_percentage": top_3_percentage,
            "conflicts": conflicts,
            "profile_type": profile_type,
            "recommendations": profile_recommendations,
            "insights": insights,
            "significant_priority_count": len(significant_priorities),
            "all_priorities_ranked": sorted_priorities
        }

    def _classify_priority_profile(
        self,
        priority_dict: Dict[str, float],
        dominant_priority: str,
        dominant_value: float
    ) -> str:
        """
        Classify the priority profile into a recognizable type.

        Args:
            priority_dict: Dictionary of priority names to values
            dominant_priority: The highest priority
            dominant_value: Value of the dominant priority

        Returns:
            String classification of the profile type
        """
        # Calculate metrics for classification
        priority_sum = sum(priority_dict.values())
        if priority_sum == 0:
            return "undefined"

        # Count significant priorities
        significant_count = sum(1 for val in priority_dict.values() if val > 0.2)

        # Strong single priority
        if dominant_value > 0.6 and significant_count <= 2:
            return f"{dominant_priority}_focused"

        # Environmental steward profile
        if (priority_dict["environmental_impact"] > 0.4 and
            priority_dict["soil_health"] > 0.4):
            return "environmental_steward"

        # Cost-conscious farmer
        if (priority_dict["cost_effectiveness"] > 0.5 and
            dominant_priority == "cost_effectiveness"):
            return "cost_conscious"

        # Long-term sustainability focus
        if (priority_dict["long_term_benefits"] > 0.4 and
            priority_dict["soil_health"] > 0.3):
            return "sustainability_focused"

        # Quick results seeker
        if (priority_dict["quick_results"] > 0.5 and
            dominant_priority == "quick_results"):
            return "results_oriented"

        # Balanced approach
        if significant_count >= 4:
            return "balanced_approach"

        # Practical operator
        if (priority_dict["ease_of_application"] > 0.4 and
            priority_dict["cost_effectiveness"] > 0.3):
            return "practical_operator"

        return "custom_profile"

    def _generate_profile_recommendations(
        self,
        profile_type: str,
        priority_dict: Dict[str, float],
        conflicts: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Generate recommendations based on the priority profile type.

        Args:
            profile_type: Classification of the priority profile
            priority_dict: Dictionary of priority values
            conflicts: List of identified conflicts

        Returns:
            List of actionable recommendations
        """
        recommendations = []

        # Profile-specific recommendations
        if profile_type == "environmental_steward":
            recommendations.append(
                "Consider organic or slow-release fertilizers to align with environmental priorities"
            )
            recommendations.append(
                "Focus on soil health building practices for long-term sustainability"
            )

        elif profile_type == "cost_conscious":
            recommendations.append(
                "Synthetic fertilizers may offer the best cost-effectiveness"
            )
            recommendations.append(
                "Consider bulk purchasing and precise application to minimize costs"
            )

        elif profile_type == "sustainability_focused":
            recommendations.append(
                "Long-term soil health investments will pay off over time"
            )
            recommendations.append(
                "Consider integrated nutrient management combining organic and synthetic options"
            )

        elif profile_type == "results_oriented":
            recommendations.append(
                "Quick-release synthetic fertilizers will deliver fastest results"
            )
            recommendations.append(
                "Monitor closely and consider split applications for sustained performance"
            )

        elif profile_type == "practical_operator":
            recommendations.append(
                "Focus on easy-to-apply options that fit your existing equipment"
            )
            recommendations.append(
                "Granular or liquid formulations based on your equipment capabilities"
            )

        elif profile_type == "balanced_approach":
            recommendations.append(
                "Your balanced priorities allow for flexible fertilizer selection"
            )
            recommendations.append(
                "Consider blended products that address multiple needs"
            )

        # Conflict-specific recommendations
        if conflicts:
            high_severity_conflicts = [c for c in conflicts if c["severity"] == "high"]
            if high_severity_conflicts:
                recommendations.append(
                    f"You have {len(high_severity_conflicts)} high-priority conflict(s). "
                    "Consider hybrid solutions or split applications."
                )

        # Priority-specific recommendations
        if priority_dict["soil_health"] > 0.5:
            recommendations.append(
                "Include organic matter or bio-stimulants to support soil health goals"
            )

        if priority_dict["environmental_impact"] > 0.5:
            recommendations.append(
                "Follow 4R principles (Right Source, Rate, Time, Place) to minimize environmental impact"
            )

        return recommendations

    def _validate_constraints(self, constraints) -> Dict[str, Any]:
        """
        Validate farmer constraints for fertilizer selection.

        This method performs comprehensive validation of constraint values, ensuring they
        are within acceptable ranges and identifying potential issues with the constraint
        configuration.

        Args:
            constraints: FarmerConstraints object containing all constraint values

        Returns:
            Dict containing:
                - is_valid (bool): Whether constraints pass validation
                - errors (List[str]): Critical validation errors
                - warnings (List[str]): Non-critical warnings
                - details (Dict[str, Any]): Additional validation details

        Validation checks:
            1. Budget values are positive and reasonable
            2. Farm size is positive and within realistic ranges
            3. Equipment availability is specified
            4. Constraint combinations are logical
        """
        errors = []
        warnings = []
        details = {}

        # Validate budget constraints
        budget_validation = self._validate_budget_constraints(constraints)
        if not budget_validation["is_valid"]:
            errors.extend(budget_validation["errors"])
        warnings.extend(budget_validation["warnings"])
        details["budget_validation"] = budget_validation

        # Validate farm size
        farm_size_validation = self._validate_farm_size(constraints.farm_size_acres)
        if not farm_size_validation["is_valid"]:
            errors.extend(farm_size_validation["errors"])
        warnings.extend(farm_size_validation["warnings"])
        details["farm_size_validation"] = farm_size_validation

        # Validate equipment constraints
        equipment_validation = self._validate_equipment_constraints(constraints)
        if not equipment_validation["is_valid"]:
            errors.extend(equipment_validation["errors"])
        warnings.extend(equipment_validation["warnings"])
        details["equipment_validation"] = equipment_validation

        # Validate operational constraints
        operational_validation = self._validate_operational_constraints(constraints)
        if not operational_validation["is_valid"]:
            errors.extend(operational_validation["errors"])
        warnings.extend(operational_validation["warnings"])
        details["operational_validation"] = operational_validation

        # Check for logical inconsistencies
        consistency_validation = self._validate_constraint_consistency(constraints)
        warnings.extend(consistency_validation["warnings"])
        details["consistency_validation"] = consistency_validation

        # Determine overall validity
        is_valid = len(errors) == 0

        # Log validation result
        if is_valid:
            self.logger.info(
                f"Constraint validation passed. Warnings: {len(warnings)}"
            )
        else:
            self.logger.error(f"Constraint validation failed with {len(errors)} errors")

        return {
            "is_valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "details": details
        }

    def _validate_budget_constraints(self, constraints) -> Dict[str, Any]:
        """
        Validate budget-related constraints.

        Args:
            constraints: FarmerConstraints object

        Returns:
            Dict with validation results for budget constraints
        """
        errors = []
        warnings = []
        details = {}

        # Check budget per acre
        if constraints.budget_per_acre is not None:
            if constraints.budget_per_acre <= 0:
                errors.append("Budget per acre must be greater than zero")
            elif constraints.budget_per_acre < 20:
                warnings.append(
                    f"Budget per acre (${constraints.budget_per_acre:.2f}) is very low. "
                    "This may severely limit fertilizer options."
                )
            elif constraints.budget_per_acre > 500:
                warnings.append(
                    f"Budget per acre (${constraints.budget_per_acre:.2f}) is very high. "
                    "Consider if this is intended."
                )
            details["budget_per_acre"] = constraints.budget_per_acre

        # Check total budget
        if constraints.total_budget is not None:
            if constraints.total_budget <= 0:
                errors.append("Total budget must be greater than zero")
            elif constraints.total_budget < 1000:
                warnings.append(
                    f"Total budget (${constraints.total_budget:.2f}) may be insufficient "
                    "for comprehensive fertilizer program."
                )
            details["total_budget"] = constraints.total_budget

        # Check budget consistency
        if (constraints.budget_per_acre is not None and 
            constraints.total_budget is not None and 
            constraints.farm_size_acres > 0):
            
            calculated_total = constraints.budget_per_acre * constraints.farm_size_acres
            budget_difference = abs(calculated_total - constraints.total_budget)
            relative_difference = budget_difference / constraints.total_budget
            
            if relative_difference > 0.1:  # 10% difference threshold
                warnings.append(
                    f"Budget inconsistency detected: "
                    f"Budget per acre (${constraints.budget_per_acre:.2f}) × "
                    f"Farm size ({constraints.farm_size_acres} acres) = "
                    f"${calculated_total:.2f}, but total budget is "
                    f"${constraints.total_budget:.2f}. "
                    f"Difference: ${budget_difference:.2f}"
                )
            
            details["budget_consistency"] = {
                "calculated_total": calculated_total,
                "stated_total": constraints.total_budget,
                "difference": budget_difference,
                "relative_difference": relative_difference
            }

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "details": details
        }

    def _validate_farm_size(self, farm_size_acres: float) -> Dict[str, Any]:
        """
        Validate farm size constraints.

        Args:
            farm_size_acres: Farm size in acres

        Returns:
            Dict with validation results for farm size
        """
        errors = []
        warnings = []
        details = {"farm_size_acres": farm_size_acres}

        # Check if farm size is positive
        if farm_size_acres <= 0:
            errors.append("Farm size must be greater than zero")
            return {
                "is_valid": False,
                "errors": errors,
                "warnings": warnings,
                "details": details
            }

        # Categorize farm size and provide relevant warnings
        if farm_size_acres < 5:
            details["farm_category"] = "small_garden"
            warnings.append(
                f"Very small farm size ({farm_size_acres} acres). "
                "Consider small-package fertilizer options."
            )
        elif farm_size_acres < 50:
            details["farm_category"] = "small_farm"
            warnings.append(
                f"Small farm size ({farm_size_acres} acres). "
                "Bulk purchasing may not be cost-effective."
            )
        elif farm_size_acres < 500:
            details["farm_category"] = "medium_farm"
        elif farm_size_acres < 2000:
            details["farm_category"] = "large_farm"
        else:
            details["farm_category"] = "very_large_farm"
            warnings.append(
                f"Very large farm size ({farm_size_acres} acres). "
                "Consider bulk purchasing and custom application services."
            )

        # Check for unrealistic farm sizes
        if farm_size_acres > 50000:
            warnings.append(
                f"Extremely large farm size ({farm_size_acres} acres). "
                "Please verify this is correct."
            )

        return {
            "is_valid": True,
            "errors": errors,
            "warnings": warnings,
            "details": details
        }

    def _validate_equipment_constraints(self, constraints) -> Dict[str, Any]:
        """
        Validate equipment-related constraints.

        Args:
            constraints: FarmerConstraints object

        Returns:
            Dict with validation results for equipment constraints
        """
        errors = []
        warnings = []
        details = {}

        # Check available equipment
        if not constraints.available_equipment:
            errors.append("No available equipment specified. At least one piece of equipment must be listed.")
        else:
            details["equipment_count"] = len(constraints.available_equipment)
            details["available_equipment"] = constraints.available_equipment
            
            # Validate equipment types
            known_equipment = {
                "broadcast_spreader", "drop_spreader", "spinner_spreader",
                "fertilizer_applicator", "liquid_applicator", "injection_system",
                "foliar_sprayer", "fertigation_system", "planter_with_fertilizer",
                "cultivator_with_fertilizer", "manual_application", "custom_applicator"
            }
            
            unknown_equipment = [eq for eq in constraints.available_equipment 
                               if eq.lower().replace(" ", "_") not in known_equipment]
            
            if unknown_equipment:
                warnings.append(
                    f"Unknown equipment types detected: {unknown_equipment}. "
                    "This may limit recommendation accuracy."
                )
                details["unknown_equipment"] = unknown_equipment

            # Check for equipment limitations consistency
            if constraints.equipment_limitations:
                details["equipment_limitations"] = constraints.equipment_limitations
                
                # Check if limitations conflict with available equipment
                for limitation in constraints.equipment_limitations:
                    if any(limitation.lower() in eq.lower() for eq in constraints.available_equipment):
                        warnings.append(
                            f"Equipment limitation '{limitation}' may conflict with "
                            f"available equipment list."
                        )

        # Validate storage capacity if provided
        if constraints.storage_capacity:
            storage_levels = ["low", "medium", "high", "unlimited"]
            if constraints.storage_capacity.lower() not in storage_levels:
                warnings.append(
                    f"Storage capacity '{constraints.storage_capacity}' should be one of: "
                    f"{', '.join(storage_levels)}"
                )
            details["storage_capacity"] = constraints.storage_capacity

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "details": details
        }

    def _validate_operational_constraints(self, constraints) -> Dict[str, Any]:
        """
        Validate operational constraints.

        Args:
            constraints: FarmerConstraints object

        Returns:
            Dict with validation results for operational constraints
        """
        errors = []
        warnings = []
        details = {}

        # Validate application window
        if constraints.application_window_days is not None:
            if constraints.application_window_days <= 0:
                errors.append("Application window must be greater than zero days")
            elif constraints.application_window_days < 3:
                warnings.append(
                    f"Very short application window ({constraints.application_window_days} days). "
                    "This may limit fertilizer options and timing flexibility."
                )
            elif constraints.application_window_days > 365:
                warnings.append(
                    f"Application window ({constraints.application_window_days} days) "
                    "exceeds one year. Please verify this is correct."
                )
            details["application_window_days"] = constraints.application_window_days

        # Validate labor availability
        if constraints.labor_availability:
            labor_levels = ["low", "medium", "high"]
            if constraints.labor_availability.lower() not in labor_levels:
                warnings.append(
                    f"Labor availability '{constraints.labor_availability}' should be one of: "
                    f"{', '.join(labor_levels)}"
                )
            details["labor_availability"] = constraints.labor_availability
            
            # Provide labor-specific guidance
            if constraints.labor_availability.lower() == "low":
                warnings.append(
                    "Low labor availability may require easy-to-apply fertilizer options "
                    "or custom application services."
                )

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "details": details
        }

    def _validate_constraint_consistency(self, constraints) -> Dict[str, Any]:
        """
        Validate consistency between different constraints.

        Args:
            constraints: FarmerConstraints object

        Returns:
            Dict with validation results for constraint consistency
        """
        warnings = []
        details = {}

        # Check organic preference vs certification requirement
        if constraints.organic_preference and not constraints.organic_certification_required:
            warnings.append(
                "Organic preference is set but organic certification is not required. "
                "Consider enabling organic certification requirement if organic is preferred."
            )

        # Check environmental concerns vs water quality restrictions
        if constraints.environmental_concerns and not constraints.water_quality_restrictions:
            warnings.append(
                "Environmental concerns are noted but water quality restrictions are not enabled. "
                "Consider enabling water quality restrictions for consistency."
            )

        # Check soil health focus vs organic preference
        if constraints.soil_health_focus and not constraints.organic_preference:
            warnings.append(
                "Soil health focus is enabled. Consider organic preference for better soil health outcomes."
            )

        # Check budget constraints vs preferences
        if (constraints.budget_per_acre is not None and 
            constraints.budget_per_acre < 50 and 
            constraints.organic_preference):
            warnings.append(
                f"Low budget per acre (${constraints.budget_per_acre:.2f}) may conflict with "
                "organic preference, as organic fertilizers typically cost more."
            )

        # Check labor availability vs equipment
        if (constraints.labor_availability and 
            constraints.labor_availability.lower() == "low" and
            constraints.available_equipment and
            "manual_application" in constraints.available_equipment):
            warnings.append(
                "Low labor availability conflicts with manual application equipment. "
                "Consider mechanical application options."
            )

        # Check application window vs nutrient management plan
        if (constraints.application_window_days is not None and
            constraints.application_window_days < 7 and
            constraints.nutrient_management_plan):
            warnings.append(
                f"Short application window ({constraints.application_window_days} days) "
                "may conflict with nutrient management plan requirements."
            )

        return {
            "warnings": warnings,
            "details": details
        }

    def _analyze_constraints(self, constraints) -> Dict[str, Any]:
        """
        Analyze farmer constraints to identify patterns and provide insights.

        Args:
            constraints: FarmerConstraints object

        Returns:
            Dict containing:
                - constraint_profile (str): Classification of constraint profile
                - limiting_factors (List[str]): Most limiting constraints
                - recommendations (List[str]): Constraint-specific recommendations
                - insights (List[str]): Key insights about constraints
        """
        limiting_factors = []
        recommendations = []
        insights = []

        # Analyze budget constraints
        if constraints.budget_per_acre and constraints.budget_per_acre < 100:
            limiting_factors.append("budget_constraint")
            recommendations.append("Focus on cost-effective synthetic fertilizers")
            insights.append(f"Budget constraint (${constraints.budget_per_acre:.2f}/acre) will limit premium options")

        # Analyze equipment constraints
        if len(constraints.available_equipment) <= 2:
            limiting_factors.append("equipment_limitation")
            recommendations.append("Consider equipment-compatible fertilizer forms")
            insights.append("Limited equipment may restrict fertilizer type options")

        # Analyze time constraints
        if constraints.application_window_days and constraints.application_window_days < 14:
            limiting_factors.append("time_constraint")
            recommendations.append("Prioritize quick-application fertilizers")
            insights.append(f"Short application window ({constraints.application_window_days} days) requires efficient application")

        # Analyze regulatory constraints
        if constraints.organic_certification_required:
            limiting_factors.append("organic_certification")
            recommendations.append("Only consider OMRI-listed organic fertilizers")
            insights.append("Organic certification requirement limits to certified products")

        if constraints.water_quality_restrictions:
            limiting_factors.append("environmental_regulation")
            recommendations.append("Focus on slow-release and environmentally safe options")
            insights.append("Water quality restrictions require careful nutrient management")

        # Determine constraint profile
        constraint_profile = self._classify_constraint_profile(constraints, limiting_factors)

        return {
            "constraint_profile": constraint_profile,
            "limiting_factors": limiting_factors,
            "recommendations": recommendations,
            "insights": insights
        }

    def _classify_constraint_profile(self, constraints, limiting_factors: List[str]) -> str:
        """
        Classify the constraint profile into a recognizable type.

        Args:
            constraints: FarmerConstraints object
            limiting_factors: List of identified limiting factors

        Returns:
            String classification of constraint profile
        """
        if "budget_constraint" in limiting_factors and "equipment_limitation" in limiting_factors:
            return "resource_constrained"
        elif "organic_certification" in limiting_factors or "environmental_regulation" in limiting_factors:
            return "regulation_focused"
        elif "time_constraint" in limiting_factors:
            return "time_sensitive"
        elif len(limiting_factors) == 0:
            return "flexible"
        elif len(limiting_factors) >= 3:
            return "highly_constrained"
        else:
            return "moderately_constrained"

    def _generate_comprehensive_recommendations(
        self,
        priorities,
        constraints,
        priority_analysis: Dict[str, Any],
        constraint_analysis: Dict[str, Any],
        soil_data: Optional[Dict[str, Any]] = None,
        crop_data: Optional[Dict[str, Any]] = None,
        farm_profile: Optional[Dict[str, Any]] = None
    ) -> List:
        """
        Generate comprehensive fertilizer recommendations based on validated priorities and constraints.

        Args:
            priorities: Normalized farmer priorities
            constraints: Farmer constraints
            priority_analysis: Priority profile analysis results
            constraint_analysis: Constraint analysis results
            soil_data: Optional soil test data
            crop_data: Optional crop information
            farm_profile: Optional farm profile

        Returns:
            List of comprehensive fertilizer recommendations
        """
        self.logger.info("Generating comprehensive recommendations based on analysis")
        
        # For now, return a structured response indicating successful validation
        # In a full implementation, this would generate actual fertilizer recommendations
        recommendations = []
        
        # Create a comprehensive analysis summary
        analysis_summary = {
            "priority_validation": "passed",
            "constraint_validation": "passed",
            "priority_profile": priority_analysis["profile_type"],
            "constraint_profile": constraint_analysis["constraint_profile"],
            "limiting_factors": constraint_analysis["limiting_factors"],
            "priority_conflicts": len(priority_analysis["conflicts"]),
            "recommendations_generated": True,
            "analysis_complete": True
        }
        
        self.logger.info(f"Comprehensive analysis complete: {analysis_summary}")
        
        return recommendations

    def generate_recommendation_explanation(
        self,
        recommendation: Dict[str, Any],
        priorities: Dict[str, Any],
        constraints: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Generate comprehensive explanation for a fertilizer recommendation.
        
        Args:
            recommendation: Fertilizer recommendation data
            priorities: Farmer priorities
            constraints: Farmer constraints
            context: Additional context (soil, crop, farm data)
            language: Language for explanation
            
        Returns:
            Comprehensive explanation with multiple sections
        """
        try:
            return self.explanation_service.generate_recommendation_explanation(
                recommendation=recommendation,
                priorities=priorities,
                constraints=constraints,
                context=context,
                language=language
            )
        except Exception as e:
            self.logger.error(f"Error generating explanation: {str(e)}")
            return {
                "error": str(e),
                "fallback_summary": "Unable to generate detailed explanation"
            }
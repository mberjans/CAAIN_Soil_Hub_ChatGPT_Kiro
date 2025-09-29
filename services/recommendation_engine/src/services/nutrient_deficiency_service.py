"""
Nutrient Deficiency Service

Provides nutrient deficiency detection and correction recommendations.
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np

try:
    from ..models.agricultural_models import (
        RecommendationRequest,
        RecommendationItem
    )
except ImportError:
    from models.agricultural_models import (
        RecommendationRequest,
        RecommendationItem
    )


class NutrientDeficiencyService:
    """Service for nutrient deficiency detection and correction."""
    
    def __init__(self):
        """Initialize nutrient deficiency service."""
        self.deficiency_thresholds = self._build_deficiency_thresholds()
        self.deficiency_symptoms = self._build_deficiency_symptoms()
        self.correction_strategies = self._build_correction_strategies()
    
    def _build_deficiency_thresholds(self) -> Dict[str, Dict[str, Any]]:
        """Build nutrient deficiency threshold database."""
        return {
            "nitrogen": {
                "soil_test_critical": 10,  # ppm nitrate-N
                "tissue_test_critical": {
                    "corn": {"V6": 2.8, "VT": 2.5, "R1": 2.0},  # % N in tissue
                    "soybean": {"V3": 4.5, "R1": 4.0, "R3": 3.5}
                },
                "visual_symptoms": [
                    "yellowing_lower_leaves",
                    "stunted_growth",
                    "pale_green_color",
                    "reduced_tillering"
                ]
            },
            "phosphorus": {
                "soil_test_critical": 15,  # ppm Mehlich-3
                "tissue_test_critical": {
                    "corn": {"V6": 0.25, "VT": 0.20, "R1": 0.18},
                    "soybean": {"V3": 0.30, "R1": 0.25, "R3": 0.20}
                },
                "visual_symptoms": [
                    "purple_leaf_coloration",
                    "delayed_maturity",
                    "poor_root_development",
                    "reduced_tillering"
                ]
            },
            "potassium": {
                "soil_test_critical": 120,  # ppm Mehlich-3
                "tissue_test_critical": {
                    "corn": {"V6": 1.5, "VT": 1.2, "R1": 1.0},
                    "soybean": {"V3": 1.8, "R1": 1.5, "R3": 1.2}
                },
                "visual_symptoms": [
                    "leaf_edge_burn",
                    "yellowing_between_veins",
                    "weak_stalks",
                    "increased_lodging"
                ]
            },
            "sulfur": {
                "soil_test_critical": 8,  # ppm sulfate-S
                "tissue_test_critical": {
                    "corn": {"V6": 0.15, "VT": 0.12, "R1": 0.10},
                    "soybean": {"V3": 0.20, "R1": 0.18, "R3": 0.15}
                },
                "visual_symptoms": [
                    "yellowing_young_leaves",
                    "stunted_growth",
                    "delayed_maturity",
                    "reduced_protein"
                ]
            },
            "iron": {
                "soil_test_critical": 2.5,  # ppm DTPA-extractable
                "tissue_test_critical": {
                    "corn": {"V6": 20, "VT": 18, "R1": 15},  # ppm in tissue
                    "soybean": {"V3": 50, "R1": 45, "R3": 40}
                },
                "visual_symptoms": [
                    "interveinal_chlorosis",
                    "yellowing_young_leaves",
                    "white_striping",
                    "stunted_growth"
                ],
                "ph_related": True
            },
            "zinc": {
                "soil_test_critical": 0.8,  # ppm DTPA-extractable
                "tissue_test_critical": {
                    "corn": {"V6": 15, "VT": 12, "R1": 10},
                    "soybean": {"V3": 20, "R1": 18, "R3": 15}
                },
                "visual_symptoms": [
                    "white_bud_syndrome",
                    "shortened_internodes",
                    "bronzing_leaves",
                    "delayed_maturity"
                ]
            },
            "manganese": {
                "soil_test_critical": 2.0,  # ppm DTPA-extractable
                "tissue_test_critical": {
                    "corn": {"V6": 15, "VT": 12, "R1": 10},
                    "soybean": {"V3": 20, "R1": 18, "R3": 15}
                },
                "visual_symptoms": [
                    "interveinal_chlorosis",
                    "brown_spots_leaves",
                    "reduced_growth",
                    "poor_grain_fill"
                ],
                "ph_related": True
            }
        }
    
    def _build_deficiency_symptoms(self) -> Dict[str, Dict[str, Any]]:
        """Build visual deficiency symptom database."""
        return {
            "early_detection_signs": {
                "nitrogen": {
                    "description": "Lower leaves turn yellow first, progressing upward",
                    "timing": "V4-V6 growth stage",
                    "severity_indicators": ["leaf_color_intensity", "growth_rate", "plant_height"]
                },
                "phosphorus": {
                    "description": "Purple or reddish coloration, especially on leaf edges",
                    "timing": "Early vegetative growth",
                    "severity_indicators": ["color_intensity", "root_development", "tillering"]
                },
                "potassium": {
                    "description": "Yellowing and browning of leaf edges (firing)",
                    "timing": "Mid to late vegetative growth",
                    "severity_indicators": ["leaf_edge_damage", "stalk_strength", "lodging_risk"]
                }
            },
            "field_patterns": {
                "uniform_deficiency": "Soil-related deficiency affecting entire field",
                "patchy_deficiency": "Variable soil conditions or compaction issues",
                "low_areas": "Waterlogged conditions affecting nutrient availability",
                "high_ph_areas": "Micronutrient deficiencies in alkaline soils"
            }
        }
    
    def _build_correction_strategies(self) -> Dict[str, Dict[str, Any]]:
        """Build nutrient deficiency correction strategies."""
        return {
            "nitrogen": {
                "soil_application": {
                    "sources": ["urea", "anhydrous_ammonia", "uan_solution"],
                    "rates": {"corn": 30, "soybean": 0},  # lbs N per acre for correction
                    "timing": "immediate_sidedress",
                    "efficiency": 0.8
                },
                "foliar_application": {
                    "sources": ["urea", "uan_solution"],
                    "rates": {"corn": 10, "soybean": 5},  # lbs N per acre
                    "timing": "V6_to_VT",
                    "efficiency": 0.6
                }
            },
            "phosphorus": {
                "soil_application": {
                    "sources": ["dap", "map", "tsp"],
                    "rates": {"corn": 40, "soybean": 30},  # lbs P2O5 per acre
                    "timing": "fall_or_spring",
                    "efficiency": 0.7
                },
                "starter_application": {
                    "sources": ["liquid_starter", "pop_up"],
                    "rates": {"corn": 15, "soybean": 10},
                    "timing": "at_planting",
                    "efficiency": 0.9
                }
            },
            "potassium": {
                "soil_application": {
                    "sources": ["muriate_of_potash", "sulfate_of_potash"],
                    "rates": {"corn": 60, "soybean": 40},  # lbs K2O per acre
                    "timing": "fall_preferred",
                    "efficiency": 0.8
                },
                "foliar_application": {
                    "sources": ["potassium_chloride", "potassium_sulfate"],
                    "rates": {"corn": 5, "soybean": 3},
                    "timing": "R1_to_R3",
                    "efficiency": 0.5
                }
            },
            "micronutrients": {
                "soil_application": {
                    "sources": ["chelated_micronutrients", "sulfate_forms"],
                    "rates": {"zinc": 5, "iron": 10, "manganese": 8},  # lbs per acre
                    "timing": "spring_application",
                    "efficiency": 0.6
                },
                "foliar_application": {
                    "sources": ["chelated_forms", "sulfate_solutions"],
                    "rates": {"zinc": 0.5, "iron": 1.0, "manganese": 0.8},  # lbs per acre
                    "timing": "V6_to_VT",
                    "efficiency": 0.8
                },
                "seed_treatment": {
                    "sources": ["zinc_sulfate", "chelated_zinc"],
                    "rates": {"zinc": 0.25},  # oz per cwt seed
                    "timing": "at_planting",
                    "efficiency": 0.7
                }
            }
        }
    
    async def get_deficiency_recommendations(
        self, 
        request: RecommendationRequest
    ) -> List[RecommendationItem]:
        """Generate nutrient deficiency detection and correction recommendations (Question 4)."""
        recommendations = []
        
        # Analyze soil test data for deficiencies
        if request.soil_data:
            soil_deficiencies = self._analyze_soil_test_deficiencies(request.soil_data)
            for nutrient, severity in soil_deficiencies.items():
                correction_rec = self._create_deficiency_correction_recommendation(
                    nutrient, severity, request
                )
                recommendations.append(correction_rec)
        
        # Add monitoring and detection recommendations
        monitoring_rec = self._create_monitoring_recommendation(request)
        recommendations.append(monitoring_rec)
        
        # Add tissue testing recommendation
        tissue_rec = self._create_tissue_testing_recommendation(request)
        recommendations.append(tissue_rec)
        
        return recommendations
    
    def _analyze_soil_test_deficiencies(self, soil_data) -> Dict[str, str]:
        """Analyze soil test data to identify nutrient deficiencies."""
        deficiencies = {}
        
        # Check nitrogen
        if soil_data.nitrogen_ppm and soil_data.nitrogen_ppm < self.deficiency_thresholds["nitrogen"]["soil_test_critical"]:
            deficiencies["nitrogen"] = "moderate" if soil_data.nitrogen_ppm > 5 else "severe"
        
        # Check phosphorus
        if soil_data.phosphorus_ppm and soil_data.phosphorus_ppm < self.deficiency_thresholds["phosphorus"]["soil_test_critical"]:
            deficiencies["phosphorus"] = "moderate" if soil_data.phosphorus_ppm > 10 else "severe"
        
        # Check potassium
        if soil_data.potassium_ppm and soil_data.potassium_ppm < self.deficiency_thresholds["potassium"]["soil_test_critical"]:
            deficiencies["potassium"] = "moderate" if soil_data.potassium_ppm > 80 else "severe"
        
        # Check for pH-related micronutrient deficiencies
        if soil_data.ph:
            if soil_data.ph > 7.5:
                deficiencies["iron"] = "likely"
                deficiencies["manganese"] = "likely"
                deficiencies["zinc"] = "possible"
            elif soil_data.ph < 5.5:
                deficiencies["manganese"] = "possible"
        
        return deficiencies
    
    def _create_deficiency_correction_recommendation(
        self, 
        nutrient: str, 
        severity: str, 
        request: RecommendationRequest
    ) -> RecommendationItem:
        """Create nutrient deficiency correction recommendation."""
        
        crop_name = request.crop_data.crop_name.lower() if request.crop_data else "corn"
        correction_strategy = self.correction_strategies.get(nutrient, {})
        
        # Determine correction approach based on severity and timing
        if severity == "severe" or nutrient in ["nitrogen", "phosphorus", "potassium"]:
            # Use soil application for major nutrients or severe deficiencies
            approach = "soil_application"
            strategy = correction_strategy.get("soil_application", {})
        else:
            # Use foliar application for micronutrients or moderate deficiencies
            approach = "foliar_application"
            strategy = correction_strategy.get("foliar_application", {})
        
        if not strategy:
            strategy = {"sources": ["appropriate_fertilizer"], "rates": {crop_name: 20}, "timing": "as_needed"}
        
        rate = strategy.get("rates", {}).get(crop_name, 20)
        sources = strategy.get("sources", ["appropriate_fertilizer"])
        timing = strategy.get("timing", "as_needed")
        
        # Calculate cost estimate
        cost_estimate = self._estimate_correction_cost(nutrient, rate, approach)
        
        return RecommendationItem(
            recommendation_type="nutrient_deficiency_correction",
            title=f"{nutrient.title()} Deficiency Correction",
            description=f"Soil test indicates {severity} {nutrient} deficiency. "
                       f"Apply {rate} lbs/acre of {nutrient} using {approach.replace('_', ' ')}.",
            priority=1 if severity == "severe" else 2,
            confidence_score=0.85 if severity == "severe" else 0.75,
            implementation_steps=[
                f"Select appropriate {nutrient} source: {', '.join(sources)}",
                f"Apply {rate} lbs/acre according to {timing.replace('_', ' ')} timing",
                "Calibrate application equipment for accurate rates",
                "Monitor crop response within 2-3 weeks",
                "Consider follow-up applications if needed"
            ],
            expected_outcomes=[
                f"Correction of {nutrient} deficiency symptoms",
                "Improved crop growth and vigor",
                "Enhanced yield potential",
                "Better nutrient use efficiency"
            ],
            cost_estimate=cost_estimate,
            roi_estimate=200.0 if severity == "severe" else 150.0,
            timing=timing.replace("_", " "),
            agricultural_sources=[
                f"{nutrient.title()} Deficiency Management",
                "Nutrient Correction Guidelines",
                "Fertilizer Application Recommendations"
            ]
        )
    
    def _create_monitoring_recommendation(self, request: RecommendationRequest) -> RecommendationItem:
        """Create nutrient deficiency monitoring recommendation."""
        
        return RecommendationItem(
            recommendation_type="deficiency_monitoring",
            title="Nutrient Deficiency Monitoring Program",
            description="Establish systematic monitoring to detect nutrient deficiencies early "
                       "when correction is most effective and economical.",
            priority=2,
            confidence_score=0.9,
            implementation_steps=[
                "Conduct weekly field scouting during growing season",
                "Learn to identify early deficiency symptoms",
                "Take photos and GPS coordinates of problem areas",
                "Compare affected and healthy plants side-by-side",
                "Document weather conditions and growth stages"
            ],
            expected_outcomes=[
                "Early detection of nutrient problems",
                "Timely correction before yield loss",
                "Better understanding of field variability",
                "Improved nutrient management decisions"
            ],
            cost_estimate=0.0,  # Labor cost only
            timing="Weekly during growing season",
            agricultural_sources=[
                "Nutrient Deficiency Identification Guide",
                "Field Scouting Best Practices",
                "Visual Symptom Recognition"
            ]
        )
    
    def _create_tissue_testing_recommendation(self, request: RecommendationRequest) -> RecommendationItem:
        """Create tissue testing recommendation."""
        
        crop_name = request.crop_data.crop_name if request.crop_data else "corn"
        
        # Determine optimal sampling timing
        sampling_timing = "V6 growth stage" if crop_name.lower() == "corn" else "V3-V4 growth stage"
        
        return RecommendationItem(
            recommendation_type="tissue_testing",
            title="Plant Tissue Testing Program",
            description="Implement tissue testing to confirm nutrient deficiencies and "
                       "monitor nutrient uptake during critical growth periods.",
            priority=2,
            confidence_score=0.88,
            implementation_steps=[
                f"Collect tissue samples at {sampling_timing}",
                "Sample from both affected and normal areas",
                "Submit samples to certified laboratory",
                "Request complete nutrient analysis",
                "Compare results to sufficiency ranges"
            ],
            expected_outcomes=[
                "Confirmation of suspected deficiencies",
                "Quantification of nutrient status",
                "Guidance for corrective applications",
                "Validation of soil test interpretations"
            ],
            cost_estimate=35.0,  # Per sample
            roi_estimate=300.0,
            timing=sampling_timing,
            agricultural_sources=[
                "Plant Tissue Testing Guidelines",
                "Tissue Test Interpretation",
                "Nutrient Sufficiency Ranges"
            ]
        )
    
    def _estimate_correction_cost(self, nutrient: str, rate: float, approach: str) -> float:
        """Estimate cost of nutrient deficiency correction."""
        
        # Cost estimates per pound of nutrient (approximate)
        nutrient_costs = {
            "nitrogen": 0.45,  # $ per lb N
            "phosphorus": 0.65,  # $ per lb P2O5
            "potassium": 0.35,  # $ per lb K2O
            "sulfur": 0.25,    # $ per lb S
            "zinc": 2.50,      # $ per lb Zn
            "iron": 1.80,      # $ per lb Fe
            "manganese": 2.20  # $ per lb Mn
        }
        
        base_cost = rate * nutrient_costs.get(nutrient, 1.0)
        
        # Add application cost
        if approach == "foliar_application":
            application_cost = 12.0  # $ per acre for foliar application
        else:
            application_cost = 8.0   # $ per acre for soil application
        
        return base_cost + application_cost
    
    def get_deficiency_probability(
        self, 
        nutrient: str, 
        soil_data, 
        crop_type: str = "corn"
    ) -> Tuple[float, str]:
        """
        Calculate probability of nutrient deficiency based on soil test data.
        
        Returns:
            Tuple of (probability, risk_level)
        """
        
        if nutrient not in self.deficiency_thresholds:
            return 0.0, "unknown"
        
        threshold_data = self.deficiency_thresholds[nutrient]
        critical_level = threshold_data["soil_test_critical"]
        
        # Get soil test value for the nutrient
        soil_value = None
        if nutrient == "nitrogen" and soil_data.nitrogen_ppm:
            soil_value = soil_data.nitrogen_ppm
        elif nutrient == "phosphorus" and soil_data.phosphorus_ppm:
            soil_value = soil_data.phosphorus_ppm
        elif nutrient == "potassium" and soil_data.potassium_ppm:
            soil_value = soil_data.potassium_ppm
        
        if soil_value is None:
            return 0.5, "unknown"  # No data available
        
        # Calculate deficiency probability
        if soil_value <= critical_level * 0.5:
            probability = 0.9
            risk_level = "high"
        elif soil_value <= critical_level * 0.75:
            probability = 0.7
            risk_level = "moderate_high"
        elif soil_value <= critical_level:
            probability = 0.5
            risk_level = "moderate"
        elif soil_value <= critical_level * 1.5:
            probability = 0.2
            risk_level = "low"
        else:
            probability = 0.05
            risk_level = "very_low"
        
        # Adjust for pH-related micronutrients
        if nutrient in ["iron", "manganese", "zinc"] and soil_data.ph:
            if threshold_data.get("ph_related"):
                if soil_data.ph > 7.5:
                    probability = min(1.0, probability * 1.5)
                    if risk_level in ["low", "very_low"]:
                        risk_level = "moderate"
        
        return probability, risk_level
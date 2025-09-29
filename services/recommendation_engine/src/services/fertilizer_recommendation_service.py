"""
Fertilizer Recommendation Service

Provides fertilizer strategy, type selection, and application timing recommendations.
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from datetime import datetime, date

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


class FertilizerRecommendationService:
    """Service for fertilizer recommendations and nutrient management."""
    
    def __init__(self):
        """Initialize fertilizer recommendation service."""
        self.nutrient_requirements = self._build_nutrient_requirements()
        self.fertilizer_types = self._build_fertilizer_database()
        self.application_guidelines = self._build_application_guidelines()
    
    def _build_nutrient_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Build crop nutrient requirement database."""
        return {
            "corn": {
                "nitrogen_lbs_per_bu": 1.2,  # lbs N per bushel yield
                "phosphorus_lbs_per_bu": 0.37,  # lbs P2O5 per bushel
                "potassium_lbs_per_bu": 0.27,  # lbs K2O per bushel
                "base_n_requirement": 120,  # Base N requirement lbs/acre
                "legume_credit": 40,  # N credit from previous legume
                "manure_efficiency": 0.5,  # Available N from manure
                "split_application": True,
                "critical_growth_stages": ["V6", "VT", "R1"]
            },
            "soybean": {
                "nitrogen_lbs_per_bu": 0.0,  # Nitrogen fixing
                "phosphorus_lbs_per_bu": 0.8,
                "potassium_lbs_per_bu": 1.4,
                "base_n_requirement": 0,
                "nitrogen_fixation": 60,  # lbs N fixed per acre
                "split_application": False,
                "critical_growth_stages": ["V3", "R1", "R3"]
            },
            "wheat": {
                "nitrogen_lbs_per_bu": 2.4,
                "phosphorus_lbs_per_bu": 0.6,
                "potassium_lbs_per_bu": 0.4,
                "base_n_requirement": 100,
                "split_application": True,
                "critical_growth_stages": ["tillering", "jointing", "heading"]
            }
        }
    
    def _build_fertilizer_database(self) -> Dict[str, Dict[str, Any]]:
        """Build fertilizer type database with characteristics."""
        return {
            "urea": {
                "nitrogen_percent": 46,
                "phosphorus_percent": 0,
                "potassium_percent": 0,
                "cost_per_ton": 420.0,
                "release_rate": "quick",
                "volatilization_risk": "high",
                "leaching_risk": "medium",
                "application_methods": ["broadcast", "banded", "injected"],
                "best_conditions": "cool, moist conditions"
            },
            "anhydrous_ammonia": {
                "nitrogen_percent": 82,
                "phosphorus_percent": 0,
                "potassium_percent": 0,
                "cost_per_ton": 520.0,
                "release_rate": "quick",
                "volatilization_risk": "low",
                "leaching_risk": "medium",
                "application_methods": ["injected"],
                "best_conditions": "fall or early spring application"
            },
            "dap": {
                "nitrogen_percent": 18,
                "phosphorus_percent": 46,
                "potassium_percent": 0,
                "cost_per_ton": 580.0,
                "release_rate": "medium",
                "volatilization_risk": "low",
                "leaching_risk": "low",
                "application_methods": ["broadcast", "banded", "starter"],
                "best_conditions": "at planting or fall application"
            },
            "potash": {
                "nitrogen_percent": 0,
                "phosphorus_percent": 0,
                "potassium_percent": 60,
                "cost_per_ton": 380.0,
                "release_rate": "quick",
                "volatilization_risk": "none",
                "leaching_risk": "low",
                "application_methods": ["broadcast", "banded"],
                "best_conditions": "fall or spring application"
            },
            "compost": {
                "nitrogen_percent": 1.5,
                "phosphorus_percent": 1.0,
                "potassium_percent": 1.0,
                "cost_per_ton": 45.0,
                "release_rate": "slow",
                "volatilization_risk": "none",
                "leaching_risk": "very_low",
                "application_methods": ["broadcast", "incorporated"],
                "best_conditions": "fall application preferred",
                "organic_matter_benefit": True,
                "soil_biology_benefit": True
            }
        }
    
    def _build_application_guidelines(self) -> Dict[str, Any]:
        """Build fertilizer application timing and method guidelines."""
        return {
            "nitrogen": {
                "fall_application": {
                    "conditions": "soil_temp_below_50F",
                    "inhibitor_recommended": True,
                    "max_rate_percent": 50
                },
                "spring_preplant": {
                    "timing": "2_weeks_before_planting",
                    "max_rate_percent": 70
                },
                "sidedress": {
                    "timing": "V6_growth_stage",
                    "max_rate_percent": 50
                }
            },
            "phosphorus": {
                "fall_application": {"preferred": True},
                "spring_application": {"acceptable": True},
                "starter_application": {"rate_limit_lbs": 20}
            },
            "potassium": {
                "fall_application": {"preferred": True},
                "spring_application": {"acceptable": True}
            }
        }
    
    async def get_fertilizer_strategy_recommendations(
        self, 
        request: RecommendationRequest
    ) -> List[RecommendationItem]:
        """Generate comprehensive fertilizer strategy recommendations."""
        recommendations = []
        
        if not request.crop_data or not request.crop_data.crop_name:
            return self._get_general_fertilizer_recommendations(request)
        
        crop_name = request.crop_data.crop_name.lower()
        if crop_name not in self.nutrient_requirements:
            return self._get_general_fertilizer_recommendations(request)
        
        crop_reqs = self.nutrient_requirements[crop_name]
        
        # Calculate nutrient needs
        nutrient_needs = self._calculate_nutrient_needs(request, crop_reqs)
        
        # Generate nitrogen recommendation
        if nutrient_needs["nitrogen"] > 0:
            n_rec = self._create_nitrogen_recommendation(nutrient_needs, request)
            recommendations.append(n_rec)
        
        # Generate phosphorus recommendation
        p_rec = self._create_phosphorus_recommendation(nutrient_needs, request)
        if p_rec:
            recommendations.append(p_rec)
        
        # Generate potassium recommendation
        k_rec = self._create_potassium_recommendation(nutrient_needs, request)
        if k_rec:
            recommendations.append(k_rec)
        
        return recommendations
    
    async def get_fertilizer_type_recommendations(
        self, 
        request: RecommendationRequest
    ) -> List[RecommendationItem]:
        """Generate fertilizer type selection recommendations (Question 5)."""
        recommendations = []
        
        # Analyze farm conditions to recommend fertilizer types
        organic_rec = self._evaluate_organic_fertilizers(request)
        synthetic_rec = self._evaluate_synthetic_fertilizers(request)
        slow_release_rec = self._evaluate_slow_release_fertilizers(request)
        
        # Rank recommendations by suitability
        all_recs = [organic_rec, synthetic_rec, slow_release_rec]
        all_recs.sort(key=lambda x: x.confidence_score, reverse=True)
        
        return all_recs
    
    async def get_timing_recommendations(
        self, 
        request: RecommendationRequest
    ) -> List[RecommendationItem]:
        """Generate fertilizer application timing recommendations."""
        recommendations = []
        
        if not request.crop_data:
            return recommendations
        
        crop_name = request.crop_data.crop_name.lower()
        if crop_name not in self.nutrient_requirements:
            return recommendations
        
        crop_reqs = self.nutrient_requirements[crop_name]
        
        # Generate timing recommendations based on crop and nutrients
        if crop_reqs.get("split_application"):
            timing_rec = self._create_split_application_recommendation(request, crop_reqs)
            recommendations.append(timing_rec)
        
        return recommendations
    
    def _calculate_nutrient_needs(
        self, 
        request: RecommendationRequest, 
        crop_reqs: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate nutrient needs based on yield goal and soil test."""
        
        yield_goal = request.crop_data.yield_goal or 150  # Default yield goal
        
        # Calculate base nutrient needs
        nitrogen_need = crop_reqs.get("base_n_requirement", 0)
        if crop_reqs.get("nitrogen_lbs_per_bu"):
            nitrogen_need = yield_goal * crop_reqs["nitrogen_lbs_per_bu"]
        
        phosphorus_need = yield_goal * crop_reqs.get("phosphorus_lbs_per_bu", 0)
        potassium_need = yield_goal * crop_reqs.get("potassium_lbs_per_bu", 0)
        
        # Apply soil test credits
        if request.soil_data:
            # Nitrogen credits
            if request.crop_data.previous_crop == "soybean":
                nitrogen_need -= crop_reqs.get("legume_credit", 0)
            
            if request.soil_data.nitrogen_ppm:
                # Credit for soil nitrate (2 lbs N per ppm)
                nitrogen_need -= request.soil_data.nitrogen_ppm * 2
            
            # Phosphorus credits (maintenance vs buildup)
            if request.soil_data.phosphorus_ppm:
                if request.soil_data.phosphorus_ppm >= 30:  # Adequate P
                    phosphorus_need = min(phosphorus_need, yield_goal * 0.3)  # Maintenance only
                elif request.soil_data.phosphorus_ppm < 15:  # Low P
                    phosphorus_need *= 1.5  # Buildup application
            
            # Potassium credits
            if request.soil_data.potassium_ppm:
                if request.soil_data.potassium_ppm >= 200:  # Adequate K
                    potassium_need = min(potassium_need, yield_goal * 0.5)  # Maintenance
                elif request.soil_data.potassium_ppm < 120:  # Low K
                    potassium_need *= 1.3  # Buildup application
        
        return {
            "nitrogen": max(0, nitrogen_need),
            "phosphorus": max(0, phosphorus_need),
            "potassium": max(0, potassium_need)
        }
    
    def _create_nitrogen_recommendation(
        self, 
        nutrient_needs: Dict[str, float], 
        request: RecommendationRequest
    ) -> RecommendationItem:
        """Create nitrogen fertilizer recommendation."""
        
        n_rate = nutrient_needs["nitrogen"]
        
        # Recommend nitrogen source based on conditions
        if request.farm_profile and request.farm_profile.farm_size_acres > 200:
            recommended_source = "anhydrous_ammonia"
            source_data = self.fertilizer_types["anhydrous_ammonia"]
        else:
            recommended_source = "urea"
            source_data = self.fertilizer_types["urea"]
        
        # Calculate application rate and cost
        product_rate = n_rate / (source_data["nitrogen_percent"] / 100)
        cost_per_acre = (product_rate / 2000) * source_data["cost_per_ton"]
        
        # Generate application timing
        timing_strategy = "Split application: 60% pre-plant, 40% side-dress at V6 stage"
        if not self.nutrient_requirements.get(request.crop_data.crop_name.lower(), {}).get("split_application"):
            timing_strategy = "Single pre-plant application"
        
        return RecommendationItem(
            recommendation_type="nitrogen_fertilizer",
            title=f"Nitrogen Application - {n_rate:.0f} lbs N/acre",
            description=f"Apply {n_rate:.0f} lbs N/acre using {recommended_source.replace('_', ' ')} "
                       f"({product_rate:.0f} lbs/acre product rate). {timing_strategy}",
            priority=1,
            confidence_score=0.88,
            implementation_steps=[
                f"Purchase {recommended_source.replace('_', ' ')} fertilizer",
                "Calibrate application equipment for accurate rates",
                "Apply according to timing recommendations",
                "Monitor crop response and adjust future applications"
            ],
            expected_outcomes=[
                f"Adequate nitrogen supply for {request.crop_data.yield_goal or 150} bu/acre yield goal",
                "Improved crop vigor and color",
                "Optimized grain protein content",
                "Efficient nutrient use and minimal losses"
            ],
            cost_estimate=cost_per_acre,
            roi_estimate=300.0,  # Typical N fertilizer ROI
            timing="Pre-plant and/or side-dress application",
            agricultural_sources=[
                "University Extension Nitrogen Guidelines",
                "4R Nutrient Stewardship Principles",
                "Regional Fertilizer Recommendations"
            ]
        )
    
    def _create_phosphorus_recommendation(
        self, 
        nutrient_needs: Dict[str, float], 
        request: RecommendationRequest
    ) -> Optional[RecommendationItem]:
        """Create phosphorus fertilizer recommendation."""
        
        p_rate = nutrient_needs["phosphorus"]
        if p_rate <= 0:
            return None
        
        # Determine recommendation type based on soil test
        rec_type = "maintenance"
        if request.soil_data and request.soil_data.phosphorus_ppm:
            if request.soil_data.phosphorus_ppm < 15:
                rec_type = "buildup"
            elif request.soil_data.phosphorus_ppm > 50:
                rec_type = "none_needed"
                return None
        
        source_data = self.fertilizer_types["dap"]
        product_rate = p_rate / (source_data["phosphorus_percent"] / 100)
        cost_per_acre = (product_rate / 2000) * source_data["cost_per_ton"]
        
        return RecommendationItem(
            recommendation_type="phosphorus_fertilizer",
            title=f"Phosphorus Application - {p_rate:.0f} lbs P2O5/acre",
            description=f"Apply {p_rate:.0f} lbs P2O5/acre using DAP (18-46-0) "
                       f"for {rec_type} phosphorus management.",
            priority=2,
            confidence_score=0.85,
            implementation_steps=[
                "Apply DAP fertilizer at planting or fall",
                "Consider banding for improved efficiency",
                "Incorporate if broadcasting",
                "Retest soil in 2-3 years"
            ],
            expected_outcomes=[
                "Adequate phosphorus for root development",
                "Improved early season vigor",
                "Enhanced grain fill and yield",
                "Maintained soil phosphorus levels"
            ],
            cost_estimate=cost_per_acre,
            timing="Fall or at planting",
            agricultural_sources=[
                "Soil Test Phosphorus Interpretation",
                "University Extension P Guidelines"
            ]
        )
    
    def _create_potassium_recommendation(
        self, 
        nutrient_needs: Dict[str, float], 
        request: RecommendationRequest
    ) -> Optional[RecommendationItem]:
        """Create potassium fertilizer recommendation."""
        
        k_rate = nutrient_needs["potassium"]
        if k_rate <= 0:
            return None
        
        source_data = self.fertilizer_types["potash"]
        product_rate = k_rate / (source_data["potassium_percent"] / 100)
        cost_per_acre = (product_rate / 2000) * source_data["cost_per_ton"]
        
        return RecommendationItem(
            recommendation_type="potassium_fertilizer",
            title=f"Potassium Application - {k_rate:.0f} lbs K2O/acre",
            description=f"Apply {k_rate:.0f} lbs K2O/acre using muriate of potash "
                       f"to maintain adequate potassium levels.",
            priority=2,
            confidence_score=0.83,
            implementation_steps=[
                "Apply potash fertilizer in fall or spring",
                "Broadcast and incorporate if possible",
                "Consider split application for high rates",
                "Monitor soil test levels annually"
            ],
            expected_outcomes=[
                "Improved drought tolerance",
                "Enhanced disease resistance",
                "Better grain quality and test weight",
                "Maintained soil potassium levels"
            ],
            cost_estimate=cost_per_acre,
            timing="Fall preferred, spring acceptable",
            agricultural_sources=[
                "Soil Test Potassium Interpretation",
                "University Extension K Guidelines"
            ]
        )
    
    def _evaluate_organic_fertilizers(self, request: RecommendationRequest) -> RecommendationItem:
        """Evaluate organic fertilizer suitability."""
        
        # Calculate suitability score
        suitability_score = 0.6  # Base score
        
        # Factors favoring organic fertilizers
        if request.farm_profile:
            if request.farm_profile.organic_certified:
                suitability_score += 0.3
            if request.farm_profile.farm_size_acres < 100:  # Smaller farms
                suitability_score += 0.1
        
        if request.soil_data:
            if request.soil_data.organic_matter_percent and request.soil_data.organic_matter_percent < 3.0:
                suitability_score += 0.2  # Low OM benefits from organic
        
        suitability_score = min(1.0, suitability_score)
        
        return RecommendationItem(
            recommendation_type="fertilizer_type",
            title="Organic Fertilizer Strategy",
            description="Organic fertilizers provide slow-release nutrients and improve soil health "
                       "through enhanced organic matter and biological activity.",
            priority=1 if suitability_score > 0.8 else 2,
            confidence_score=suitability_score,
            implementation_steps=[
                "Source quality compost or aged manure",
                "Test organic materials for nutrient content",
                "Apply in fall for spring crop benefit",
                "Supplement with approved organic sources as needed"
            ],
            expected_outcomes=[
                "Improved soil organic matter",
                "Enhanced soil biology and structure",
                "Slow-release nutrient availability",
                "Reduced environmental impact"
            ],
            cost_estimate=65.0,  # Typically higher per unit nutrient
            timing="Fall application preferred",
            agricultural_sources=[
                "Organic Fertilizer Guidelines",
                "Compost Application Recommendations"
            ]
        )
    
    def _evaluate_synthetic_fertilizers(self, request: RecommendationRequest) -> RecommendationItem:
        """Evaluate synthetic fertilizer suitability."""
        
        suitability_score = 0.8  # Generally high suitability
        
        # Factors favoring synthetic fertilizers
        if request.farm_profile:
            if request.farm_profile.farm_size_acres > 200:  # Larger farms
                suitability_score += 0.1
        
        return RecommendationItem(
            recommendation_type="fertilizer_type",
            title="Synthetic Fertilizer Strategy",
            description="Synthetic fertilizers provide precise nutrient control and immediate availability "
                       "for optimal crop response and yield maximization.",
            priority=1,
            confidence_score=suitability_score,
            implementation_steps=[
                "Select appropriate NPK analysis for crop needs",
                "Calibrate equipment for accurate application",
                "Time applications for crop uptake periods",
                "Consider split applications for nitrogen"
            ],
            expected_outcomes=[
                "Precise nutrient delivery",
                "Immediate crop response",
                "Predictable yield response",
                "Cost-effective nutrient supply"
            ],
            cost_estimate=45.0,  # Lower cost per unit nutrient
            timing="Based on crop growth stage requirements",
            agricultural_sources=[
                "University Extension Fertilizer Guidelines",
                "4R Nutrient Stewardship Principles"
            ]
        )
    
    def _evaluate_slow_release_fertilizers(self, request: RecommendationRequest) -> RecommendationItem:
        """Evaluate slow-release fertilizer suitability."""
        
        suitability_score = 0.7  # Moderate base suitability
        
        # Factors favoring slow-release
        if request.location and request.location.latitude > 40:  # Northern climates
            suitability_score += 0.1
        
        if request.soil_data:
            if request.soil_data.soil_texture and "sand" in request.soil_data.soil_texture.lower():
                suitability_score += 0.2  # Sandy soils benefit from slow release
        
        return RecommendationItem(
            recommendation_type="fertilizer_type",
            title="Slow-Release Fertilizer Strategy",
            description="Slow-release fertilizers reduce application frequency and environmental losses "
                       "while providing extended nutrient availability.",
            priority=2,
            confidence_score=min(1.0, suitability_score),
            implementation_steps=[
                "Select appropriate slow-release technology",
                "Apply at higher rates for season-long supply",
                "Reduce application frequency",
                "Monitor crop response throughout season"
            ],
            expected_outcomes=[
                "Reduced application labor",
                "Lower environmental losses",
                "Extended nutrient availability",
                "Improved nutrient use efficiency"
            ],
            cost_estimate=75.0,  # Higher upfront cost
            timing="Single application at planting",
            agricultural_sources=[
                "Slow-Release Fertilizer Research",
                "Enhanced Efficiency Fertilizer Guidelines"
            ]
        )
    
    def _create_split_application_recommendation(
        self, 
        request: RecommendationRequest, 
        crop_reqs: Dict[str, Any]
    ) -> RecommendationItem:
        """Create split application timing recommendation."""
        
        critical_stages = crop_reqs.get("critical_growth_stages", [])
        
        return RecommendationItem(
            recommendation_type="application_timing",
            title="Split Application Strategy",
            description=f"Split nitrogen applications to match crop uptake patterns "
                       f"and reduce losses. Critical stages: {', '.join(critical_stages)}",
            priority=1,
            confidence_score=0.87,
            implementation_steps=[
                "Apply 60% of nitrogen pre-plant or at planting",
                f"Apply remaining 40% at {critical_stages[0] if critical_stages else 'V6'} growth stage",
                "Monitor weather conditions for application timing",
                "Adjust rates based on crop appearance and soil conditions"
            ],
            expected_outcomes=[
                "Improved nitrogen use efficiency",
                "Reduced environmental losses",
                "Better synchronization with crop needs",
                "Potential for yield optimization"
            ],
            timing="Pre-plant and mid-season applications",
            agricultural_sources=[
                "Nitrogen Timing Research",
                "4R Nutrient Stewardship Guidelines"
            ]
        )
    
    def _get_general_fertilizer_recommendations(
        self, 
        request: RecommendationRequest
    ) -> List[RecommendationItem]:
        """Get general fertilizer recommendations when crop-specific data unavailable."""
        
        recommendations = []
        
        # General soil fertility recommendation
        general_rec = RecommendationItem(
            recommendation_type="general_fertilizer",
            title="Soil Test-Based Fertilizer Program",
            description="Develop a fertilizer program based on soil test results and crop requirements. "
                       "Focus on maintaining adequate nutrient levels for optimal crop production.",
            priority=1,
            confidence_score=0.75,
            implementation_steps=[
                "Obtain comprehensive soil test including NPK and pH",
                "Identify primary crops and yield goals",
                "Calculate nutrient removal rates for crop rotation",
                "Develop annual fertilizer application plan"
            ],
            expected_outcomes=[
                "Balanced soil fertility",
                "Optimized crop yields",
                "Efficient nutrient use",
                "Sustainable soil management"
            ],
            timing="Based on crop calendar and soil test results",
            agricultural_sources=[
                "General Fertilizer Recommendations",
                "Soil Test Interpretation Guidelines"
            ]
        )
        
        recommendations.append(general_rec)
        return recommendations
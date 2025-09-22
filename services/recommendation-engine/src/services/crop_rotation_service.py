"""
Crop Rotation Service

Provides crop rotation planning and optimization recommendations.
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


class CropRotationService:
    """Service for crop rotation planning and recommendations."""
    
    def __init__(self):
        """Initialize crop rotation service."""
        self.rotation_benefits = self._build_rotation_benefits()
        self.crop_compatibility = self._build_crop_compatibility()
        self.rotation_systems = self._build_rotation_systems()
        self.pest_disease_cycles = self._build_pest_disease_cycles()
    
    def _build_rotation_benefits(self) -> Dict[str, Dict[str, Any]]:
        """Build crop rotation benefit database."""
        return {
            "nitrogen_fixation": {
                "legume_crops": ["soybean", "alfalfa", "clover", "peas"],
                "nitrogen_contribution": {
                    "soybean": 40,      # lbs N per acre for following crop
                    "alfalfa": 120,     # lbs N per acre (multi-year)
                    "red_clover": 80,   # lbs N per acre
                    "field_peas": 60    # lbs N per acre
                },
                "duration_years": 1  # Benefit duration
            },
            "soil_health": {
                "organic_matter_builders": ["corn", "wheat", "cover_crops"],
                "structure_improvers": ["alfalfa", "grasses", "deep_rooted_crops"],
                "compaction_breakers": ["alfalfa", "radishes", "deep_rooted_crops"],
                "erosion_controllers": ["small_grains", "cover_crops", "perennials"]
            },
            "pest_management": {
                "pest_cycle_breakers": {
                    "corn_rootworm": ["soybean", "wheat", "alfalfa"],
                    "soybean_cyst_nematode": ["corn", "wheat", "non_host_crops"],
                    "white_mold": ["corn", "wheat", "grasses"],
                    "take_all": ["broadleaf_crops", "fallow"]
                },
                "beneficial_habitat": ["diverse_rotations", "cover_crops", "field_borders"]
            },
            "weed_management": {
                "herbicide_resistance_management": "crop_diversity",
                "competitive_crops": ["wheat", "rye", "alfalfa"],
                "cultivation_opportunities": ["row_crops", "corn", "soybean"],
                "smothering_crops": ["buckwheat", "sorghum_sudan"]
            }
        }
    
    def _build_crop_compatibility(self) -> Dict[str, Dict[str, Any]]:
        """Build crop compatibility matrix."""
        return {
            "corn": {
                "excellent_predecessors": ["soybean", "alfalfa"],
                "good_predecessors": ["wheat", "oats"],
                "poor_predecessors": ["corn", "sorghum"],
                "nitrogen_benefit_from": ["soybean", "alfalfa", "clover"],
                "pest_pressure_from": ["corn", "sorghum"],
                "disease_carryover_from": ["corn", "sorghum"]
            },
            "soybean": {
                "excellent_predecessors": ["corn", "wheat"],
                "good_predecessors": ["oats", "barley"],
                "poor_predecessors": ["soybean", "other_legumes"],
                "pest_pressure_from": ["soybean", "dry_beans"],
                "disease_carryover_from": ["soybean", "other_legumes"],
                "allelopathy_issues": ["wheat_residue", "rye_residue"]
            },
            "wheat": {
                "excellent_predecessors": ["soybean", "corn"],
                "good_predecessors": ["oats", "fallow"],
                "poor_predecessors": ["wheat", "barley"],
                "pest_pressure_from": ["wheat", "barley", "rye"],
                "disease_carryover_from": ["wheat", "other_cereals"]
            }
        }
    
    def _build_rotation_systems(self) -> Dict[str, Dict[str, Any]]:
        """Build proven rotation system database."""
        return {
            "corn_soybean": {
                "sequence": ["corn", "soybean"],
                "duration_years": 2,
                "region_suitability": ["midwest", "great_plains"],
                "benefits": [
                    "nitrogen_fixation_benefit",
                    "pest_cycle_disruption",
                    "herbicide_resistance_management",
                    "risk_diversification"
                ],
                "challenges": [
                    "limited_diversity",
                    "similar_planting_timing",
                    "equipment_specialization"
                ],
                "economic_performance": "excellent",
                "sustainability_rating": 7.5  # out of 10
            },
            "corn_soybean_wheat": {
                "sequence": ["corn", "soybean", "wheat"],
                "duration_years": 3,
                "region_suitability": ["midwest", "eastern_corn_belt"],
                "benefits": [
                    "increased_diversity",
                    "extended_harvest_window",
                    "soil_erosion_control",
                    "weed_management_improvement"
                ],
                "challenges": [
                    "wheat_marketing",
                    "additional_equipment_needs",
                    "harvest_timing_conflicts"
                ],
                "economic_performance": "good",
                "sustainability_rating": 8.5
            },
            "continuous_corn": {
                "sequence": ["corn"],
                "duration_years": 1,
                "region_suitability": ["high_productivity_soils"],
                "benefits": [
                    "equipment_specialization",
                    "simplified_management",
                    "consistent_marketing"
                ],
                "challenges": [
                    "increased_pest_pressure",
                    "soil_health_decline",
                    "higher_input_costs",
                    "yield_penalty"
                ],
                "economic_performance": "variable",
                "sustainability_rating": 4.0,
                "yield_penalty_percent": 10
            },
            "extended_rotation": {
                "sequence": ["corn", "soybean", "wheat", "alfalfa", "alfalfa"],
                "duration_years": 5,
                "region_suitability": ["diverse_farming_systems"],
                "benefits": [
                    "maximum_diversity",
                    "soil_health_building",
                    "nitrogen_fixation",
                    "pest_disease_suppression"
                ],
                "challenges": [
                    "complex_management",
                    "diverse_equipment_needs",
                    "market_diversification"
                ],
                "economic_performance": "good_long_term",
                "sustainability_rating": 9.5
            }
        }
    
    def _build_pest_disease_cycles(self) -> Dict[str, Dict[str, Any]]:
        """Build pest and disease cycle database."""
        return {
            "corn_rootworm": {
                "host_crops": ["corn"],
                "cycle_length_years": 1,
                "break_crops": ["soybean", "wheat", "alfalfa"],
                "economic_threshold": "high",
                "management_strategy": "rotation_primary"
            },
            "soybean_cyst_nematode": {
                "host_crops": ["soybean", "dry_beans"],
                "cycle_length_years": 3,
                "break_crops": ["corn", "wheat", "alfalfa"],
                "economic_threshold": "moderate",
                "management_strategy": "rotation_and_resistance"
            },
            "white_mold": {
                "host_crops": ["soybean", "dry_beans", "sunflower"],
                "cycle_length_years": 2,
                "break_crops": ["corn", "wheat", "grasses"],
                "economic_threshold": "moderate",
                "management_strategy": "rotation_and_fungicide"
            },
            "take_all": {
                "host_crops": ["wheat", "barley", "oats"],
                "cycle_length_years": 2,
                "break_crops": ["corn", "soybean", "broadleaf_crops"],
                "economic_threshold": "high",
                "management_strategy": "rotation_required"
            }
        }
    
    async def get_rotation_recommendations(
        self, 
        request: RecommendationRequest
    ) -> List[RecommendationItem]:
        """Generate crop rotation recommendations (Question 3)."""
        recommendations = []
        
        # Analyze current rotation if provided
        current_rotation = self._analyze_current_rotation(request)
        
        # Generate rotation system recommendations
        rotation_systems = self._evaluate_rotation_systems(request)
        
        for system_name, system_data in rotation_systems.items():
            rotation_rec = self._create_rotation_recommendation(
                system_name, system_data, request
            )
            recommendations.append(rotation_rec)
        
        # Add specific improvement recommendations
        improvement_recs = self._get_rotation_improvements(request, current_rotation)
        recommendations.extend(improvement_recs)
        
        # Sort by suitability score
        recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
        
        return recommendations[:3]  # Return top 3 recommendations
    
    def _analyze_current_rotation(self, request: RecommendationRequest) -> Dict[str, Any]:
        """Analyze current crop rotation if provided."""
        
        current_rotation = {
            "crops": [],
            "duration": 1,
            "diversity_score": 0.0,
            "sustainability_issues": []
        }
        
        if request.crop_data and request.crop_data.rotation_history:
            rotation_history = request.crop_data.rotation_history
            current_rotation["crops"] = rotation_history
            current_rotation["duration"] = len(set(rotation_history))
            
            # Calculate diversity score
            unique_crops = len(set(rotation_history))
            total_crops = len(rotation_history)
            current_rotation["diversity_score"] = unique_crops / total_crops if total_crops > 0 else 0
            
            # Identify sustainability issues
            if unique_crops == 1:
                current_rotation["sustainability_issues"].append("monoculture")
            if "corn" in rotation_history and rotation_history.count("corn") / len(rotation_history) > 0.6:
                current_rotation["sustainability_issues"].append("corn_heavy")
            if len(set(rotation_history)) < 2:
                current_rotation["sustainability_issues"].append("low_diversity")
        
        return current_rotation
    
    def _evaluate_rotation_systems(self, request: RecommendationRequest) -> Dict[str, Dict[str, Any]]:
        """Evaluate rotation systems for farm conditions."""
        
        evaluated_systems = {}
        
        for system_name, system_data in self.rotation_systems.items():
            suitability_score = self._calculate_rotation_suitability(system_data, request)
            
            if suitability_score > 0.5:  # Only recommend suitable systems
                system_copy = system_data.copy()
                system_copy["suitability_score"] = suitability_score
                evaluated_systems[system_name] = system_copy
        
        return evaluated_systems
    
    def _calculate_rotation_suitability(
        self, 
        system_data: Dict[str, Any], 
        request: RecommendationRequest
    ) -> float:
        """Calculate suitability score for rotation system."""
        
        score = 0.7  # Base score
        
        # Farm size considerations
        if request.farm_profile:
            farm_size = request.farm_profile.farm_size_acres
            
            # Larger farms can handle more complex rotations
            if system_data["duration_years"] > 2 and farm_size > 500:
                score += 0.1
            elif system_data["duration_years"] == 2 and farm_size < 200:
                score += 0.1
        
        # Equipment considerations
        if request.farm_profile and request.farm_profile.equipment_available:
            equipment = request.farm_profile.equipment_available
            
            # Simple rotations better for limited equipment
            if len(equipment) < 3 and system_data["duration_years"] <= 2:
                score += 0.1
            elif len(equipment) >= 5 and system_data["duration_years"] > 2:
                score += 0.1
        
        # Soil health considerations
        if request.soil_data:
            if (request.soil_data.organic_matter_percent and 
                request.soil_data.organic_matter_percent < 3.0):
                # Low OM benefits from diverse rotations
                if system_data["sustainability_rating"] > 8.0:
                    score += 0.15
        
        # Economic performance adjustment
        if system_data["economic_performance"] == "excellent":
            score += 0.1
        elif system_data["economic_performance"] == "good":
            score += 0.05
        
        return min(1.0, score)
    
    def _create_rotation_recommendation(
        self, 
        system_name: str, 
        system_data: Dict[str, Any], 
        request: RecommendationRequest
    ) -> RecommendationItem:
        """Create rotation system recommendation."""
        
        sequence = system_data["sequence"]
        duration = system_data["duration_years"]
        benefits = system_data["benefits"]
        challenges = system_data.get("challenges", [])
        
        # Calculate economic impact
        economic_impact = self._estimate_rotation_economics(system_data, request)
        
        return RecommendationItem(
            recommendation_type="crop_rotation",
            title=f"{system_name.replace('_', ' ').title()} Rotation",
            description=f"Implement {duration}-year rotation: {' → '.join(sequence)}. "
                       f"This system provides {', '.join(benefits[:3])} and is well-suited to your farm conditions.",
            priority=1 if system_data["suitability_score"] > 0.8 else 2,
            confidence_score=system_data["suitability_score"],
            implementation_steps=[
                f"Plan {duration}-year rotation cycle: {' → '.join(sequence)}",
                "Adjust field sizes to accommodate rotation",
                "Plan equipment needs for all crops in rotation",
                "Develop marketing strategies for all crops",
                "Monitor and document rotation benefits"
            ],
            expected_outcomes=[
                f"Improved soil health and sustainability (rating: {system_data['sustainability_rating']}/10)",
                "Reduced pest and disease pressure",
                "Enhanced nutrient cycling and efficiency",
                "Diversified income streams and risk management",
                f"Economic performance: {system_data['economic_performance']}"
            ],
            cost_estimate=economic_impact.get("implementation_cost", 0.0),
            roi_estimate=economic_impact.get("roi_percent", 120.0),
            timing="Plan for next crop year, implement gradually",
            agricultural_sources=[
                "Crop Rotation Research and Guidelines",
                "Sustainable Agriculture Rotation Systems",
                "Regional Rotation Performance Data"
            ]
        )
    
    def _get_rotation_improvements(
        self, 
        request: RecommendationRequest, 
        current_rotation: Dict[str, Any]
    ) -> List[RecommendationItem]:
        """Get specific rotation improvement recommendations."""
        
        improvements = []
        
        # Check for monoculture issues
        if "monoculture" in current_rotation.get("sustainability_issues", []):
            diversity_rec = self._create_diversity_recommendation(request)
            improvements.append(diversity_rec)
        
        # Check for nitrogen management opportunities
        if self._needs_nitrogen_management_improvement(request, current_rotation):
            nitrogen_rec = self._create_nitrogen_management_recommendation(request)
            improvements.append(nitrogen_rec)
        
        # Check for pest management opportunities
        pest_rec = self._create_pest_management_recommendation(request, current_rotation)
        if pest_rec:
            improvements.append(pest_rec)
        
        return improvements
    
    def _create_diversity_recommendation(self, request: RecommendationRequest) -> RecommendationItem:
        """Create crop diversity improvement recommendation."""
        
        return RecommendationItem(
            recommendation_type="rotation_diversity",
            title="Increase Crop Diversity",
            description="Add crop diversity to break pest cycles, improve soil health, "
                       "and reduce production risks associated with monoculture systems.",
            priority=1,
            confidence_score=0.9,
            implementation_steps=[
                "Identify suitable alternative crops for your region",
                "Start with small acreage to gain experience",
                "Develop marketing channels for new crops",
                "Acquire necessary equipment or custom services",
                "Plan 3-4 year rotation cycle"
            ],
            expected_outcomes=[
                "Reduced pest and disease pressure",
                "Improved soil biological diversity",
                "Enhanced nutrient cycling",
                "Diversified income and risk reduction",
                "Better long-term sustainability"
            ],
            cost_estimate=50.0,  # Planning and transition costs
            roi_estimate=180.0,
            timing="Plan for gradual implementation over 2-3 years",
            agricultural_sources=[
                "Crop Diversification Benefits",
                "Alternative Crop Selection Guide",
                "Rotation Planning Resources"
            ]
        )
    
    def _needs_nitrogen_management_improvement(
        self, 
        request: RecommendationRequest, 
        current_rotation: Dict[str, Any]
    ) -> bool:
        """Check if rotation needs nitrogen management improvement."""
        
        # Check if rotation includes nitrogen-fixing crops
        rotation_crops = current_rotation.get("crops", [])
        legume_crops = self.rotation_benefits["nitrogen_fixation"]["legume_crops"]
        
        has_legumes = any(crop in legume_crops for crop in rotation_crops)
        
        # If no legumes and high nitrogen-demanding crops, recommend improvement
        if not has_legumes and ("corn" in rotation_crops or "wheat" in rotation_crops):
            return True
        
        return False
    
    def _create_nitrogen_management_recommendation(self, request: RecommendationRequest) -> RecommendationItem:
        """Create nitrogen management improvement recommendation."""
        
        return RecommendationItem(
            recommendation_type="nitrogen_management",
            title="Integrate Nitrogen-Fixing Crops",
            description="Include legume crops in rotation to reduce nitrogen fertilizer costs "
                       "and improve soil nitrogen availability for subsequent crops.",
            priority=2,
            confidence_score=0.85,
            implementation_steps=[
                "Add soybean to corn rotation for 40 lbs N/acre credit",
                "Consider red clover or alfalfa for longer rotations",
                "Plan nitrogen application reductions for crops following legumes",
                "Monitor soil nitrogen levels and crop response",
                "Calculate fertilizer cost savings"
            ],
            expected_outcomes=[
                "Reduced nitrogen fertilizer costs (40-80 lbs N/acre savings)",
                "Improved soil nitrogen cycling",
                "Enhanced soil biological activity",
                "Better soil structure from legume root systems",
                "Estimated savings: $25-40 per acre"
            ],
            cost_estimate=-30.0,  # Cost savings
            roi_estimate=250.0,
            timing="Integrate into next rotation cycle",
            agricultural_sources=[
                "Nitrogen Fixation Benefits",
                "Legume Crop Integration Guide",
                "Nitrogen Credit Calculations"
            ]
        )
    
    def _create_pest_management_recommendation(
        self, 
        request: RecommendationRequest, 
        current_rotation: Dict[str, Any]
    ) -> Optional[RecommendationItem]:
        """Create pest management improvement recommendation."""
        
        # Identify potential pest issues based on current rotation
        rotation_crops = current_rotation.get("crops", [])
        
        pest_issues = []
        if rotation_crops.count("corn") > 1:
            pest_issues.append("corn_rootworm")
        if rotation_crops.count("soybean") > 1:
            pest_issues.append("soybean_cyst_nematode")
        
        if not pest_issues:
            return None
        
        return RecommendationItem(
            recommendation_type="pest_management",
            title="Rotation-Based Pest Management",
            description=f"Modify rotation to break pest cycles for: {', '.join(pest_issues)}. "
                       f"Strategic crop rotation is the most effective and economical pest management tool.",
            priority=1,
            confidence_score=0.88,
            implementation_steps=[
                "Identify specific pest pressure in your fields",
                "Plan rotation to break pest life cycles",
                "Include non-host crops for problem pests",
                "Monitor pest populations and damage levels",
                "Reduce reliance on chemical pest control"
            ],
            expected_outcomes=[
                "Significant reduction in pest pressure",
                "Lower pesticide costs and applications",
                "Reduced development of pest resistance",
                "Improved beneficial insect populations",
                "More sustainable pest management"
            ],
            cost_estimate=0.0,  # Management change only
            roi_estimate=200.0,
            timing="Implement in next rotation cycle",
            agricultural_sources=[
                "Integrated Pest Management Guidelines",
                "Rotation-Based Pest Control",
                "Pest Life Cycle Management"
            ]
        )
    
    def _estimate_rotation_economics(
        self, 
        system_data: Dict[str, Any], 
        request: RecommendationRequest
    ) -> Dict[str, float]:
        """Estimate economic impact of rotation system."""
        
        # Base implementation costs
        implementation_cost = 0.0
        
        # Additional equipment or infrastructure costs
        if system_data["duration_years"] > 2:
            implementation_cost += 25.0  # Additional planning and management
        
        # ROI estimation based on system performance
        roi_mapping = {
            "excellent": 150.0,
            "good": 120.0,
            "good_long_term": 140.0,
            "variable": 100.0
        }
        
        roi_percent = roi_mapping.get(system_data.get("economic_performance", "good"), 120.0)
        
        # Adjust for sustainability benefits
        sustainability_bonus = (system_data.get("sustainability_rating", 7.0) - 7.0) * 10
        roi_percent += sustainability_bonus
        
        return {
            "implementation_cost": implementation_cost,
            "roi_percent": roi_percent
        }
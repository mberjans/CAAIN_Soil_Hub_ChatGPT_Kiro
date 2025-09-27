"""
TICKET-005_crop-type-filtering-3.3: Preference-Based Recommendation Enhancement Engine

This module provides intelligent crop type and filter recommendations based on:
- Farm characteristics and constraints
- Similar farmer preferences
- Preference optimization algorithms
- Conflict resolution mechanisms
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import logging
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


class RecommendationType(Enum):
    """Types of recommendations the engine can provide"""
    CROP_SUGGESTION = "crop_suggestion"
    FILTER_RECOMMENDATION = "filter_recommendation"
    PREFERENCE_OPTIMIZATION = "preference_optimization"
    CONFLICT_RESOLUTION = "conflict_resolution"


@dataclass
class FarmCharacteristics:
    """Farm characteristics used for recommendations"""
    location: str
    climate_zone: str
    soil_type: str
    farm_size_acres: float
    precipitation_annual: float
    temperature_range: Tuple[float, float]
    soil_ph: Optional[float] = None
    irrigation_available: bool = False
    organic_certification: bool = False
    equipment_capabilities: List[str] = None
    
    def __post_init__(self):
        if self.equipment_capabilities is None:
            self.equipment_capabilities = []


@dataclass
class FarmerProfile:
    """Farmer profile for similarity matching"""
    farmer_id: str
    experience_years: int
    farm_characteristics: FarmCharacteristics
    crop_preferences: Dict[str, float]  # crop_type -> preference_score
    filter_usage_patterns: Dict[str, int]  # filter_type -> usage_count
    success_metrics: Dict[str, float]  # metric_name -> score


@dataclass
class RecommendationResult:
    """Result from the recommendation engine"""
    recommendation_type: RecommendationType
    suggestions: List[Dict[str, Any]]
    confidence_score: float
    reasoning: str
    conflicts_detected: List[str] = None
    
    def __post_init__(self):
        if self.conflicts_detected is None:
            self.conflicts_detected = []


class PreferenceRecommendationEngine:
    """
    Intelligent recommendation engine for crop preferences and filtering
    """
    
    def __init__(self):
        self.farmer_profiles: Dict[str, FarmerProfile] = {}
        self.crop_compatibility_matrix: Dict[str, Dict[str, float]] = {}
        self.filter_effectiveness_scores: Dict[str, float] = {}
        self._initialize_compatibility_matrix()
        self._initialize_filter_scores()
    
    def _initialize_compatibility_matrix(self):
        """Initialize crop compatibility matrix based on agricultural knowledge"""
        # Crop compatibility scores (0.0 to 1.0)
        compatibility_data = {
            "grains": {
                "corn": 0.9, "wheat": 0.8, "rice": 0.7, "barley": 0.8, "oats": 0.8,
                "soybeans": 0.9, "sorghum": 0.7
            },
            "oilseeds": {
                "soybeans": 0.9, "sunflower": 0.8, "canola": 0.8, "safflower": 0.7
            },
            "forage": {
                "alfalfa": 0.9, "clover": 0.8, "timothy": 0.7, "brome": 0.7
            },
            "vegetables": {
                "tomatoes": 0.8, "potatoes": 0.8, "onions": 0.7, "carrots": 0.7,
                "lettuce": 0.6, "peppers": 0.7
            },
            "fruits": {
                "apples": 0.8, "grapes": 0.8, "berries": 0.7, "citrus": 0.6
            },
            "specialty": {
                "hemp": 0.6, "hops": 0.7, "herbs": 0.6, "flowers": 0.5
            }
        }
        
        for category, crops in compatibility_data.items():
            self.crop_compatibility_matrix[category] = crops
    
    def _initialize_filter_scores(self):
        """Initialize filter effectiveness scores"""
        self.filter_effectiveness_scores = {
            "climate_zone": 0.9,
            "soil_type": 0.8,
            "precipitation": 0.8,
            "temperature": 0.7,
            "farm_size": 0.6,
            "irrigation": 0.7,
            "organic": 0.5,
            "equipment": 0.6
        }
    
    def register_farmer_profile(self, profile: FarmerProfile):
        """Register a farmer profile for similarity matching"""
        self.farmer_profiles[profile.farmer_id] = profile
        logger.info(f"Registered farmer profile: {profile.farmer_id}")
    
    def suggest_crop_types(self, farm_characteristics: FarmCharacteristics, 
                          max_suggestions: int = 5) -> RecommendationResult:
        """
        Suggest crop types based on farm characteristics
        """
        suggestions = []
        reasoning_parts = []
        
        # Climate zone based suggestions
        climate_crops = self._get_crops_for_climate(farm_characteristics.climate_zone)
        reasoning_parts.append(f"Climate zone {farm_characteristics.climate_zone} compatibility")
        
        # Soil type based suggestions
        soil_crops = self._get_crops_for_soil(farm_characteristics.soil_type)
        reasoning_parts.append(f"Soil type {farm_characteristics.soil_type} suitability")
        
        # Farm size considerations
        size_appropriate_crops = self._get_crops_for_farm_size(farm_characteristics.farm_size_acres)
        reasoning_parts.append(f"Farm size {farm_characteristics.farm_size_acres} acres optimization")
        
        # Combine and score suggestions
        crop_scores = defaultdict(float)
        
        for crop in climate_crops:
            crop_scores[crop] += 0.4
        for crop in soil_crops:
            crop_scores[crop] += 0.3
        for crop in size_appropriate_crops:
            crop_scores[crop] += 0.3
        
        # Sort by score and take top suggestions
        sorted_crops = sorted(crop_scores.items(), key=lambda x: x[1], reverse=True)
        
        for crop, score in sorted_crops[:max_suggestions]:
            suggestions.append({
                "crop_type": crop,
                "suitability_score": round(score, 2),
                "reasons": self._get_crop_reasons(crop, farm_characteristics)
            })
        
        confidence = min(1.0, len(sorted_crops) / max_suggestions * 0.8)
        reasoning = "Based on " + ", ".join(reasoning_parts)
        
        return RecommendationResult(
            recommendation_type=RecommendationType.CROP_SUGGESTION,
            suggestions=suggestions,
            confidence_score=confidence,
            reasoning=reasoning
        )
    
    def recommend_filters_by_similarity(self, farm_characteristics: FarmCharacteristics,
                                      max_recommendations: int = 3) -> RecommendationResult:
        """
        Recommend filters based on similar farmers
        """
        similar_farmers = self._find_similar_farmers(farm_characteristics)
        
        if not similar_farmers:
            return RecommendationResult(
                recommendation_type=RecommendationType.FILTER_RECOMMENDATION,
                suggestions=[],
                confidence_score=0.0,
                reasoning="No similar farmers found for comparison"
            )
        
        # Aggregate filter usage patterns from similar farmers
        filter_usage_aggregated = defaultdict(float)
        total_farmers = len(similar_farmers)
        
        for farmer_id, similarity_score in similar_farmers:
            farmer = self.farmer_profiles[farmer_id]
            for filter_type, usage_count in farmer.filter_usage_patterns.items():
                filter_usage_aggregated[filter_type] += usage_count * similarity_score
        
        # Normalize and create recommendations
        suggestions = []
        sorted_filters = sorted(filter_usage_aggregated.items(), 
                              key=lambda x: x[1], reverse=True)
        
        for filter_type, aggregated_usage in sorted_filters[:max_recommendations]:
            effectiveness = self.filter_effectiveness_scores.get(filter_type, 0.5)
            suggestions.append({
                "filter_type": filter_type,
                "usage_frequency": round(aggregated_usage / total_farmers, 2),
                "effectiveness_score": effectiveness,
                "similar_farmers_count": total_farmers
            })
        
        confidence = min(1.0, total_farmers / 10.0)  # More farmers = higher confidence
        reasoning = f"Based on filter usage patterns from {total_farmers} similar farmers"
        
        return RecommendationResult(
            recommendation_type=RecommendationType.FILTER_RECOMMENDATION,
            suggestions=suggestions,
            confidence_score=confidence,
            reasoning=reasoning
        )
    
    def optimize_preferences(self, current_preferences: Dict[str, float],
                           farm_characteristics: FarmCharacteristics) -> RecommendationResult:
        """
        Suggest preference optimizations
        """
        suggestions = []
        conflicts = []
        
        # Check for preference-farm characteristic mismatches
        climate_suitable_crops = self._get_crops_for_climate(farm_characteristics.climate_zone)
        
        for crop, preference_score in current_preferences.items():
            if preference_score > 0.7 and crop not in climate_suitable_crops:
                conflicts.append(f"High preference for {crop} conflicts with climate zone {farm_characteristics.climate_zone}")
                suggestions.append({
                    "optimization_type": "climate_mismatch",
                    "crop": crop,
                    "current_preference": preference_score,
                    "recommended_preference": max(0.3, preference_score - 0.4),
                    "reason": f"Low climate suitability in zone {farm_characteristics.climate_zone}"
                })
        
        # Check for soil type mismatches
        soil_suitable_crops = self._get_crops_for_soil(farm_characteristics.soil_type)
        
        for crop, preference_score in current_preferences.items():
            if preference_score > 0.7 and crop not in soil_suitable_crops:
                if not any(s["crop"] == crop for s in suggestions):  # Avoid duplicates
                    conflicts.append(f"High preference for {crop} conflicts with soil type {farm_characteristics.soil_type}")
                    suggestions.append({
                        "optimization_type": "soil_mismatch",
                        "crop": crop,
                        "current_preference": preference_score,
                        "recommended_preference": max(0.3, preference_score - 0.3),
                        "reason": f"Poor soil suitability for {farm_characteristics.soil_type}"
                    })
        
        # Suggest increasing preferences for highly suitable crops
        for crop in climate_suitable_crops[:3]:  # Top 3 climate-suitable crops
            if crop not in current_preferences or current_preferences[crop] < 0.6:
                suggestions.append({
                    "optimization_type": "opportunity",
                    "crop": crop,
                    "current_preference": current_preferences.get(crop, 0.0),
                    "recommended_preference": 0.8,
                    "reason": f"High suitability for your farm characteristics"
                })
        
        confidence = min(1.0, len(suggestions) / 5.0)
        reasoning = "Analysis of preference-farm characteristic alignment"
        
        return RecommendationResult(
            recommendation_type=RecommendationType.PREFERENCE_OPTIMIZATION,
            suggestions=suggestions,
            confidence_score=confidence,
            reasoning=reasoning,
            conflicts_detected=conflicts
        )
    
    def resolve_preference_conflicts(self, preferences: Dict[str, float],
                                   farm_characteristics: FarmCharacteristics) -> RecommendationResult:
        """
        Identify and resolve preference conflicts
        """
        conflicts = []
        resolutions = []
        
        # Check for mutually exclusive crop preferences
        exclusive_pairs = [
            ("corn", "soybeans"),  # Rotation consideration
            ("organic", "conventional"),  # Management style
            ("high_water", "drought_tolerant")  # Water requirements
        ]
        
        for crop1, crop2 in exclusive_pairs:
            pref1 = preferences.get(crop1, 0.0)
            pref2 = preferences.get(crop2, 0.0)
            
            if pref1 > 0.7 and pref2 > 0.7:
                conflicts.append(f"High preferences for both {crop1} and {crop2} may be conflicting")
                
                # Suggest resolution based on farm characteristics
                if farm_characteristics.irrigation_available and crop1 == "high_water":
                    recommended_crop = crop1
                    reduce_crop = crop2
                elif not farm_characteristics.irrigation_available and crop2 == "drought_tolerant":
                    recommended_crop = crop2
                    reduce_crop = crop1
                else:
                    # Default to the one with higher current preference
                    recommended_crop = crop1 if pref1 > pref2 else crop2
                    reduce_crop = crop2 if pref1 > pref2 else crop1
                
                resolutions.append({
                    "conflict_type": "mutually_exclusive",
                    "crops_involved": [crop1, crop2],
                    "recommended_action": f"Maintain high preference for {recommended_crop}, reduce {reduce_crop}",
                    "recommended_preferences": {
                        recommended_crop: max(pref1, pref2),
                        reduce_crop: min(0.4, min(pref1, pref2))
                    }
                })
        
        # Check for resource constraint conflicts
        high_input_crops = ["corn", "vegetables", "fruits"]
        high_preference_input_crops = [crop for crop in high_input_crops 
                                     if preferences.get(crop, 0.0) > 0.7]
        
        if len(high_preference_input_crops) > 2 and farm_characteristics.farm_size_acres < 100:
            conflicts.append("Multiple high-input crops selected for small farm size")
            resolutions.append({
                "conflict_type": "resource_constraint",
                "issue": "Too many high-input crops for farm size",
                "recommended_action": "Focus on 1-2 primary high-input crops",
                "suggested_crops": high_preference_input_crops[:2]
            })
        
        confidence = 1.0 if conflicts else 0.8  # High confidence if conflicts found
        reasoning = f"Analyzed {len(preferences)} preferences for conflicts"
        
        return RecommendationResult(
            recommendation_type=RecommendationType.CONFLICT_RESOLUTION,
            suggestions=resolutions,
            confidence_score=confidence,
            reasoning=reasoning,
            conflicts_detected=conflicts
        )
    
    def _find_similar_farmers(self, farm_characteristics: FarmCharacteristics, 
                            max_similar: int = 10) -> List[Tuple[str, float]]:
        """Find farmers with similar characteristics"""
        similarities = []
        
        for farmer_id, farmer_profile in self.farmer_profiles.items():
            similarity = self._calculate_farm_similarity(
                farm_characteristics, 
                farmer_profile.farm_characteristics
            )
            if similarity > 0.3:  # Minimum similarity threshold
                similarities.append((farmer_id, similarity))
        
        # Sort by similarity and return top matches
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:max_similar]
    
    def _calculate_farm_similarity(self, farm1: FarmCharacteristics, 
                                 farm2: FarmCharacteristics) -> float:
        """Calculate similarity score between two farms"""
        similarity_score = 0.0
        total_weight = 0.0
        
        # Climate zone similarity (weight: 0.3)
        if farm1.climate_zone == farm2.climate_zone:
            similarity_score += 0.3
        total_weight += 0.3
        
        # Soil type similarity (weight: 0.25)
        if farm1.soil_type == farm2.soil_type:
            similarity_score += 0.25
        total_weight += 0.25
        
        # Farm size similarity (weight: 0.2)
        size_ratio = min(farm1.farm_size_acres, farm2.farm_size_acres) / max(farm1.farm_size_acres, farm2.farm_size_acres)
        similarity_score += 0.2 * size_ratio
        total_weight += 0.2
        
        # Precipitation similarity (weight: 0.15)
        if farm1.precipitation_annual > 0 and farm2.precipitation_annual > 0:
            precip_ratio = min(farm1.precipitation_annual, farm2.precipitation_annual) / max(farm1.precipitation_annual, farm2.precipitation_annual)
            similarity_score += 0.15 * precip_ratio
        total_weight += 0.15
        
        # Irrigation similarity (weight: 0.1)
        if farm1.irrigation_available == farm2.irrigation_available:
            similarity_score += 0.1
        total_weight += 0.1
        
        return similarity_score / total_weight if total_weight > 0 else 0.0
    
    def _get_crops_for_climate(self, climate_zone: str) -> List[str]:
        """Get suitable crops for a climate zone"""
        climate_crop_mapping = {
            "zone_3": ["wheat", "barley", "oats", "canola", "peas"],
            "zone_4": ["corn", "soybeans", "wheat", "barley", "alfalfa"],
            "zone_5": ["corn", "soybeans", "wheat", "sunflower", "potatoes"],
            "zone_6": ["corn", "soybeans", "cotton", "sorghum", "rice"],
            "zone_7": ["corn", "soybeans", "cotton", "peanuts", "vegetables"],
            "zone_8": ["rice", "cotton", "citrus", "vegetables", "sugarcane"],
            "zone_9": ["citrus", "vegetables", "rice", "tropical_fruits"],
            "zone_10": ["tropical_fruits", "vegetables", "sugarcane", "palm"]
        }
        return climate_crop_mapping.get(climate_zone.lower(), ["corn", "soybeans", "wheat"])
    
    def _get_crops_for_soil(self, soil_type: str) -> List[str]:
        """Get suitable crops for a soil type"""
        soil_crop_mapping = {
            "clay": ["rice", "wheat", "barley", "alfalfa"],
            "loam": ["corn", "soybeans", "wheat", "vegetables"],
            "sandy": ["potatoes", "carrots", "peanuts", "watermelons"],
            "silt": ["corn", "soybeans", "vegetables", "fruits"],
            "peat": ["vegetables", "berries", "specialty_crops"],
            "rocky": ["grapes", "olives", "herbs", "livestock_forage"]
        }
        return soil_crop_mapping.get(soil_type.lower(), ["corn", "soybeans"])
    
    def _get_crops_for_farm_size(self, farm_size_acres: float) -> List[str]:
        """Get appropriate crops for farm size"""
        if farm_size_acres < 10:
            return ["vegetables", "herbs", "berries", "flowers"]
        elif farm_size_acres < 50:
            return ["vegetables", "fruits", "specialty_crops", "organic_grains"]
        elif farm_size_acres < 200:
            return ["corn", "soybeans", "wheat", "vegetables", "fruits"]
        else:
            return ["corn", "soybeans", "wheat", "cotton", "rice", "sorghum"]
    
    def _get_crop_reasons(self, crop: str, farm_characteristics: FarmCharacteristics) -> List[str]:
        """Get reasons why a crop is suitable for the farm"""
        reasons = []
        
        # Climate suitability
        if crop in self._get_crops_for_climate(farm_characteristics.climate_zone):
            reasons.append(f"Well-suited for {farm_characteristics.climate_zone}")
        
        # Soil suitability
        if crop in self._get_crops_for_soil(farm_characteristics.soil_type):
            reasons.append(f"Thrives in {farm_characteristics.soil_type} soil")
        
        # Farm size appropriateness
        if crop in self._get_crops_for_farm_size(farm_characteristics.farm_size_acres):
            reasons.append(f"Appropriate for {farm_characteristics.farm_size_acres}-acre operation")
        
        # Special considerations
        if farm_characteristics.irrigation_available and crop in ["rice", "vegetables", "fruits"]:
            reasons.append("Benefits from available irrigation")
        
        if farm_characteristics.organic_certification and crop in ["vegetables", "fruits", "herbs"]:
            reasons.append("High value in organic markets")
        
        return reasons if reasons else ["General agricultural suitability"]


# Global instance for use throughout the application
preference_recommendation_engine = PreferenceRecommendationEngine()
"""
Crop Recommendation Service

Provides crop selection and variety recommendations based on soil and climate data.
"""

from typing import List, Dict, Any, Tuple
import numpy as np
try:
    from ..models.agricultural_models import (
        RecommendationRequest,
        RecommendationItem,
        ConfidenceFactors
    )
except ImportError:
    from models.agricultural_models import (
        RecommendationRequest,
        RecommendationItem,
        ConfidenceFactors
    )


class CropRecommendationService:
    """Service for crop selection and variety recommendations."""
    
    def __init__(self):
        """Initialize crop recommendation service with crop database."""
        self.crop_database = self._build_crop_database()
        self.suitability_matrix = self._build_suitability_matrix()
    
    def _build_crop_database(self) -> Dict[str, Dict[str, Any]]:
        """Build crop characteristics database."""
        return {
            "corn": {
                "optimal_ph_range": (6.0, 6.8),
                "minimum_ph": 5.5,
                "maximum_ph": 7.5,
                "optimal_om_range": (3.0, 5.0),
                "phosphorus_requirement": "medium_high",
                "potassium_requirement": "high",
                "nitrogen_requirement": "high",
                "drainage_requirement": "well_drained",
                "climate_zones": ["3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b"],
                "growing_degree_days": 2500,
                "typical_yield_range": (120, 200),  # bu/acre
                "economic_viability_min_acres": 50
            },
            "soybean": {
                "optimal_ph_range": (6.0, 7.0),
                "minimum_ph": 5.8,
                "maximum_ph": 7.5,
                "optimal_om_range": (2.5, 4.5),
                "phosphorus_requirement": "medium",
                "potassium_requirement": "medium_high",
                "nitrogen_requirement": "low",  # Nitrogen fixing
                "drainage_requirement": "well_drained",
                "climate_zones": ["3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b"],
                "growing_degree_days": 2200,
                "typical_yield_range": (40, 70),  # bu/acre
                "economic_viability_min_acres": 30
            },
            "wheat": {
                "optimal_ph_range": (6.0, 7.0),
                "minimum_ph": 5.5,
                "maximum_ph": 8.0,
                "optimal_om_range": (2.0, 4.0),
                "phosphorus_requirement": "medium",
                "potassium_requirement": "medium",
                "nitrogen_requirement": "medium_high",
                "drainage_requirement": "well_drained",
                "climate_zones": ["2a", "2b", "3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b"],
                "growing_degree_days": 2000,
                "typical_yield_range": (50, 80),  # bu/acre
                "economic_viability_min_acres": 40
            }
        }
    
    def _build_suitability_matrix(self) -> Dict[str, Dict[str, float]]:
        """Build suitability scoring matrix for different conditions."""
        return {
            "ph_suitability": {
                "optimal": 1.0,
                "acceptable": 0.8,
                "marginal": 0.6,
                "poor": 0.3
            },
            "nutrient_suitability": {
                "high": 1.0,
                "medium": 0.8,
                "low": 0.5,
                "very_low": 0.2
            },
            "climate_suitability": {
                "optimal": 1.0,
                "good": 0.9,
                "acceptable": 0.7,
                "marginal": 0.5
            }
        }
    
    async def get_crop_recommendations(self, request: RecommendationRequest) -> List[RecommendationItem]:
        """
        Generate crop recommendations based on farm conditions.
        
        Args:
            request: Recommendation request with farm data
            
        Returns:
            List of crop recommendations sorted by suitability
        """
        recommendations = []
        
        for crop_name, crop_data in self.crop_database.items():
            suitability_score = self._calculate_crop_suitability(
                crop_name, crop_data, request
            )
            
            if suitability_score > 0.5:  # Only recommend suitable crops
                recommendation = self._create_crop_recommendation(
                    crop_name, crop_data, suitability_score, request
                )
                recommendations.append(recommendation)
        
        # Sort by suitability score (descending)
        recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
        
        return recommendations
    
    def _calculate_crop_suitability(
        self, 
        crop_name: str, 
        crop_data: Dict[str, Any], 
        request: RecommendationRequest
    ) -> float:
        """Calculate overall suitability score for a crop."""
        
        scores = []
        
        # pH suitability
        if request.soil_data and request.soil_data.ph:
            ph_score = self._calculate_ph_suitability(
                request.soil_data.ph, crop_data
            )
            scores.append(ph_score)
        
        # Nutrient suitability
        if request.soil_data:
            nutrient_score = self._calculate_nutrient_suitability(
                request.soil_data, crop_data
            )
            scores.append(nutrient_score)
        
        # Farm size suitability
        if request.farm_profile:
            size_score = self._calculate_size_suitability(
                request.farm_profile.farm_size_acres, crop_data
            )
            scores.append(size_score)
        
        # Climate suitability (placeholder - would integrate with weather data)
        climate_score = 0.8  # Default good climate score
        scores.append(climate_score)
        
        # Return weighted average
        if scores:
            return sum(scores) / len(scores)
        else:
            return 0.5  # Default moderate suitability
    
    def _calculate_ph_suitability(self, soil_ph: float, crop_data: Dict[str, Any]) -> float:
        """Calculate pH suitability score."""
        optimal_min, optimal_max = crop_data["optimal_ph_range"]
        
        if optimal_min <= soil_ph <= optimal_max:
            return 1.0  # Optimal
        elif crop_data["minimum_ph"] <= soil_ph <= crop_data["maximum_ph"]:
            # Calculate distance from optimal range
            if soil_ph < optimal_min:
                distance = optimal_min - soil_ph
            else:
                distance = soil_ph - optimal_max
            
            # Linear decrease from optimal
            max_distance = max(
                optimal_min - crop_data["minimum_ph"],
                crop_data["maximum_ph"] - optimal_max
            )
            return max(0.6, 1.0 - (distance / max_distance) * 0.4)
        else:
            return 0.3  # Poor suitability
    
    def _calculate_nutrient_suitability(
        self, 
        soil_data, 
        crop_data: Dict[str, Any]
    ) -> float:
        """Calculate nutrient suitability score."""
        scores = []
        
        # Phosphorus suitability
        if soil_data.phosphorus_ppm:
            p_score = self._get_nutrient_score(
                soil_data.phosphorus_ppm, 
                crop_data["phosphorus_requirement"],
                nutrient_type="phosphorus"
            )
            scores.append(p_score)
        
        # Potassium suitability
        if soil_data.potassium_ppm:
            k_score = self._get_nutrient_score(
                soil_data.potassium_ppm,
                crop_data["potassium_requirement"],
                nutrient_type="potassium"
            )
            scores.append(k_score)
        
        return sum(scores) / len(scores) if scores else 0.7
    
    def _get_nutrient_score(
        self, 
        nutrient_level: float, 
        requirement: str, 
        nutrient_type: str
    ) -> float:
        """Get nutrient adequacy score."""
        
        # Define nutrient level thresholds (ppm)
        thresholds = {
            "phosphorus": {"low": 15, "medium": 30, "high": 50},
            "potassium": {"low": 120, "medium": 200, "high": 300}
        }
        
        if nutrient_type not in thresholds:
            return 0.7  # Default score
        
        thresh = thresholds[nutrient_type]
        
        # Determine nutrient level category
        if nutrient_level >= thresh["high"]:
            level_category = "high"
        elif nutrient_level >= thresh["medium"]:
            level_category = "medium"
        else:
            level_category = "low"
        
        # Score based on requirement vs availability
        requirement_scores = {
            ("high", "high"): 1.0,
            ("high", "medium"): 0.7,
            ("high", "low"): 0.4,
            ("medium_high", "high"): 1.0,
            ("medium_high", "medium"): 0.8,
            ("medium_high", "low"): 0.5,
            ("medium", "high"): 1.0,
            ("medium", "medium"): 0.9,
            ("medium", "low"): 0.6,
            ("low", "high"): 1.0,
            ("low", "medium"): 1.0,
            ("low", "low"): 0.8
        }
        
        return requirement_scores.get((requirement, level_category), 0.7)
    
    def _calculate_size_suitability(self, farm_size: float, crop_data: Dict[str, Any]) -> float:
        """Calculate farm size suitability."""
        min_viable_size = crop_data.get("economic_viability_min_acres", 20)
        
        if farm_size >= min_viable_size * 2:
            return 1.0  # Excellent size
        elif farm_size >= min_viable_size:
            return 0.8  # Good size
        elif farm_size >= min_viable_size * 0.5:
            return 0.6  # Marginal size
        else:
            return 0.4  # Small but possible
    
    def _create_crop_recommendation(
        self,
        crop_name: str,
        crop_data: Dict[str, Any],
        suitability_score: float,
        request: RecommendationRequest
    ) -> RecommendationItem:
        """Create a crop recommendation item."""
        
        # Generate description based on suitability factors
        description_parts = [
            f"{crop_name.title()} is {'highly' if suitability_score > 0.8 else 'moderately' if suitability_score > 0.6 else 'marginally'} suitable for your farm conditions."
        ]
        
        if request.soil_data:
            if request.soil_data.ph:
                ph_status = self._get_ph_status(request.soil_data.ph, crop_data)
                description_parts.append(f"Soil pH of {request.soil_data.ph} is {ph_status} for {crop_name}.")
        
        # Implementation steps
        implementation_steps = [
            f"Verify soil conditions meet {crop_name} requirements",
            f"Select appropriate {crop_name} variety for your region",
            "Plan planting schedule based on local frost dates",
            "Prepare seedbed and planting equipment",
            "Consider crop insurance options"
        ]
        
        # Expected outcomes
        yield_min, yield_max = crop_data["typical_yield_range"]
        expected_outcomes = [
            f"Expected yield range: {yield_min}-{yield_max} bu/acre",
            "Improved soil health through crop rotation",
            "Diversified income stream",
            "Enhanced farm sustainability"
        ]
        
        return RecommendationItem(
            recommendation_type="crop_selection",
            title=f"Grow {crop_name.title()}",
            description=" ".join(description_parts),
            priority=1 if suitability_score > 0.8 else 2 if suitability_score > 0.6 else 3,
            confidence_score=suitability_score,
            implementation_steps=implementation_steps,
            expected_outcomes=expected_outcomes,
            timing="Plan for next growing season",
            agricultural_sources=[
                "USDA Crop Production Guidelines",
                "State University Extension Services",
                "Regional Crop Variety Trials"
            ]
        )
    
    def _get_ph_status(self, soil_ph: float, crop_data: Dict[str, Any]) -> str:
        """Get pH status description."""
        optimal_min, optimal_max = crop_data["optimal_ph_range"]
        
        if optimal_min <= soil_ph <= optimal_max:
            return "optimal"
        elif crop_data["minimum_ph"] <= soil_ph <= crop_data["maximum_ph"]:
            return "acceptable"
        else:
            return "suboptimal"
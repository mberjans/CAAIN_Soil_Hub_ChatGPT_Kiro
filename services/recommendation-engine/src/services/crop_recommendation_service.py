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
        # Import climate service for auto-detection if needed
        try:
            from .climate_integration_service import climate_integration_service
            self.climate_service = climate_integration_service
        except ImportError:
            try:
                from services.climate_integration_service import climate_integration_service
                self.climate_service = climate_integration_service
            except ImportError:
                self.climate_service = None
    
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
        # Enhance location data with climate zone if missing
        await self._ensure_climate_zone_data(request)
        
        recommendations = []
        
        # Pre-filter crops based on climate zone compatibility
        filtered_crops = self._filter_crops_by_climate_zone(request.location)
        
        for crop_name, crop_data in filtered_crops.items():
            suitability_score = self._calculate_crop_suitability(
                crop_name, crop_data, request
            )
            
            if suitability_score > 0.5:  # Only recommend suitable crops
                recommendation = self._create_crop_recommendation(
                    crop_name, crop_data, suitability_score, request
                )
                recommendations.append(recommendation)
        
        # Add climate zone mismatch warnings for excluded crops
        excluded_crops = self._get_excluded_crops_by_climate(request.location)
        if excluded_crops:
            # Log excluded crops for potential warning generation
            pass  # Warnings will be handled by the main recommendation engine
        
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
        
        # Climate suitability (integrated with climate zone detection)
        climate_score = self._calculate_climate_zone_suitability(
            request.location, crop_data
        )
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
        
        # Add climate zone compatibility information
        if request.location:
            climate_compatibility = self._get_climate_compatibility_description(
                request.location, crop_data, crop_name
            )
            if climate_compatibility:
                description_parts.append(climate_compatibility)
        
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
    
    def _calculate_climate_zone_suitability(self, location_data, crop_data: Dict[str, Any]) -> float:
        """
        Calculate climate zone suitability score for a crop.
        
        Args:
            location_data: Location data with climate zone information
            crop_data: Crop characteristics including compatible climate zones
            
        Returns:
            Suitability score between 0.0 and 1.0
        """
        if not location_data or not crop_data.get("climate_zones"):
            return 0.7  # Default moderate score when no climate data available
        
        # Get the farm's climate zone
        farm_climate_zone = getattr(location_data, 'climate_zone', None)
        
        if not farm_climate_zone:
            return 0.7  # Default moderate score without climate zone
        
        compatible_zones = crop_data["climate_zones"]
        
        # Perfect match - crop is explicitly compatible with this zone
        if farm_climate_zone in compatible_zones:
            return 1.0
        
        # Check for adjacent/similar zones
        adjacent_score = self._calculate_adjacent_zone_compatibility(farm_climate_zone, compatible_zones)
        if adjacent_score > 0:
            return adjacent_score
        
        # No compatibility found
        return 0.3
    
    def _calculate_adjacent_zone_compatibility(self, farm_zone: str, compatible_zones: List[str]) -> float:
        """
        Calculate compatibility score for adjacent climate zones.
        
        Args:
            farm_zone: Farm's USDA climate zone (e.g., "6a")
            compatible_zones: List of crop-compatible zones
            
        Returns:
            Compatibility score (0.0 for incompatible, 0.8 for adjacent)
        """
        if not farm_zone or not compatible_zones:
            return 0.0
        
        try:
            # Extract zone number and subzone from farm zone (e.g., "6a" -> 6, "a")
            farm_num = int(farm_zone[0]) if farm_zone[0].isdigit() else 0
            farm_sub = farm_zone[1:].lower() if len(farm_zone) > 1 else ""
            
            for compatible_zone in compatible_zones:
                if not compatible_zone:
                    continue
                    
                comp_num = int(compatible_zone[0]) if compatible_zone[0].isdigit() else 0
                comp_sub = compatible_zone[1:].lower() if len(compatible_zone) > 1 else ""
                
                # Adjacent zone numbers (within 1 zone)
                if abs(farm_num - comp_num) == 1:
                    return 0.8  # Good compatibility for adjacent zones
                
                # Same zone number but different subzone (e.g., 6a vs 6b)
                if farm_num == comp_num and farm_sub != comp_sub:
                    return 0.9  # Very good compatibility for same zone different subzone
            
            return 0.0  # No adjacent compatibility found
            
        except (ValueError, IndexError):
            return 0.0  # Error parsing zone data
    
    def _filter_crops_by_climate_zone(self, location_data) -> Dict[str, Dict[str, Any]]:
        """
        Filter crop database to include only climate-compatible crops.
        
        Args:
            location_data: Location data with climate zone information
            
        Returns:
            Filtered crop database containing compatible and borderline compatible crops
        """
        if not location_data:
            return self.crop_database  # Return all crops if no location data
        
        farm_climate_zone = getattr(location_data, 'climate_zone', None)
        
        if not farm_climate_zone:
            return self.crop_database  # Return all crops if no climate zone
        
        filtered_crops = {}
        
        for crop_name, crop_data in self.crop_database.items():
            compatibility_score = self._calculate_climate_zone_suitability(location_data, crop_data)
            
            # Include crops with reasonable compatibility (>= 0.5)
            # This includes perfect matches (1.0), adjacent zones (0.8-0.9), and marginal but possible (0.7)
            if compatibility_score >= 0.5:
                filtered_crops[crop_name] = crop_data
        
        return filtered_crops
    
    def _get_excluded_crops_by_climate(self, location_data) -> List[str]:
        """
        Get list of crops excluded due to climate zone incompatibility.
        
        Args:
            location_data: Location data with climate zone information
            
        Returns:
            List of crop names that were excluded
        """
        if not location_data:
            return []
        
        farm_climate_zone = getattr(location_data, 'climate_zone', None)
        
        if not farm_climate_zone:
            return []
        
        excluded_crops = []
        
        for crop_name, crop_data in self.crop_database.items():
            compatibility_score = self._calculate_climate_zone_suitability(location_data, crop_data)
            
            # Crops with very low compatibility are excluded
            if compatibility_score < 0.5:
                excluded_crops.append(crop_name)
        
        return excluded_crops
    
    async def _ensure_climate_zone_data(self, request: RecommendationRequest) -> None:
        """
        Ensure location data includes climate zone information, fetch if missing.
        
        Args:
            request: Recommendation request to enhance with climate data
        """
        if not request.location or not self.climate_service:
            return
        
        # Check if climate zone data is already available
        if hasattr(request.location, 'climate_zone') and request.location.climate_zone:
            return
        
        try:
            # Detect climate zone using coordinates
            climate_data = await self.climate_service.detect_climate_zone(
                latitude=request.location.latitude,
                longitude=request.location.longitude,
                elevation_ft=getattr(request.location, 'elevation_ft', None)
            )
            
            if climate_data:
                # Enhance location data with climate zone information
                enhanced_location_dict = self.climate_service.enhance_location_with_climate(
                    request.location.dict(), climate_data
                )
                
                # Update request location with enhanced data
                for key, value in enhanced_location_dict.items():
                    if hasattr(request.location, key):
                        setattr(request.location, key, value)
                        
        except Exception as e:
            # Log error but continue without climate zone data
            pass  # Fail gracefully, recommendations will use default climate scoring
    
    def _get_climate_compatibility_description(self, location_data, crop_data: Dict[str, Any], crop_name: str) -> str:
        """
        Generate climate compatibility description for recommendation.
        
        Args:
            location_data: Location data with climate zone information
            crop_data: Crop characteristics
            crop_name: Name of the crop
            
        Returns:
            Climate compatibility description string
        """
        farm_climate_zone = getattr(location_data, 'climate_zone', None)
        
        if not farm_climate_zone or not crop_data.get("climate_zones"):
            return ""
        
        compatible_zones = crop_data["climate_zones"]
        compatibility_score = self._calculate_climate_zone_suitability(location_data, crop_data)
        
        if farm_climate_zone in compatible_zones:
            return f"Climate Zone {farm_climate_zone} is optimal for {crop_name} production."
        elif compatibility_score >= 0.8:
            return f"Climate Zone {farm_climate_zone} is well-suited for {crop_name}, being adjacent to optimal zones {', '.join(compatible_zones[:3])}."
        elif compatibility_score >= 0.5:
            return f"Climate Zone {farm_climate_zone} is marginal for {crop_name}. Consider heat/cold tolerant varieties and monitor seasonal conditions."
        else:
            return f"Climate Zone {farm_climate_zone} may present challenges for {crop_name}. Optimal zones are {', '.join(compatible_zones[:3])}."
    
    def _get_ph_status(self, soil_ph: float, crop_data: Dict[str, Any]) -> str:
        """Get pH status description."""
        optimal_min, optimal_max = crop_data["optimal_ph_range"]
        
        if optimal_min <= soil_ph <= optimal_max:
            return "optimal"
        elif crop_data["minimum_ph"] <= soil_ph <= crop_data["maximum_ph"]:
            return "acceptable"
        else:
            return "suboptimal"
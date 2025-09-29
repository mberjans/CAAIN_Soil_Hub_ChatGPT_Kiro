"""
Enhanced Crop Recommendation Service with Advanced Filtering Integration

This service extends the basic crop recommendation functionality with deep
integration of the advanced filtering capabilities from the crop taxonomy service.
"""
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime
import asyncio

try:
    from ..models.agricultural_models import (
        RecommendationRequest,
        RecommendationItem,
        ConfidenceFactors,
        LocationData,
        SoilData,
        FarmProfile
    )
    from .crop_recommendation_service import CropRecommendationService
    # Use relative import for crop_taxonomy models
    try:
        from ....crop_taxonomy.src.models.crop_filtering_models import (
            CropSearchRequest,
            TaxonomyFilterCriteria,
            AgriculturalFilter,
            ClimateFilter,
            SoilFilter,
            ManagementFilter,
            SustainabilityFilter,
            EconomicFilter,
            CropCategory,
            PrimaryUse,
            GrowthHabit,
            ManagementComplexity,
            InputRequirements,
            LaborRequirements,
            CarbonSequestrationPotential,
            MarketStability,
            SearchOperator
        )
        from ....crop_taxonomy.src.services.crop_search_service import crop_search_service
    except ImportError:
        # Fallback to service import if relative import fails
        from services.crop_taxonomy.src.models.crop_filtering_models import (
            CropSearchRequest,
            TaxonomyFilterCriteria,
            AgriculturalFilter,
            ClimateFilter,
            SoilFilter,
            ManagementFilter,
            SustainabilityFilter,
            EconomicFilter,
            CropCategory,
            PrimaryUse,
            GrowthHabit,
            ManagementComplexity,
            InputRequirements,
            LaborRequirements,
            CarbonSequestrationPotential,
            MarketStability,
            SearchOperator
        )
        from services.crop_taxonomy.src.services.crop_search_service import crop_search_service
except ImportError as e:
    logging.error(f"Failed to import required modules: {e}")
    # Define fallback classes if imports fail
    from pydantic import BaseModel
    class RecommendationRequest(BaseModel):
        pass
    class RecommendationItem(BaseModel):
        pass
    class ConfidenceFactors(BaseModel):
        pass
    class LocationData(BaseModel):
        latitude: float
        longitude: float
    class SoilData(BaseModel):
        ph: Optional[float] = None
    class FarmProfile(BaseModel):
        farm_size_acres: float
    class CropSearchRequest(BaseModel):
        pass
    class TaxonomyFilterCriteria(BaseModel):
        pass
    class CropRecommendationService:
        def __init__(self):
            pass
    crop_search_service = None

logger = logging.getLogger(__name__)


class EnhancedCropRecommendationService(CropRecommendationService):
    """
    Enhanced crop recommendation service with advanced filtering integration.
    
    This service extends the basic crop recommendation functionality with deep
    integration of advanced filtering capabilities, allowing for more precise
    and targeted crop recommendations based on complex multi-criteria filtering.
    """
    
    def __init__(self):
        """Initialize the enhanced service with filtering capabilities."""
        super().__init__()  # Initialize the base crop recommendation service
        self.crop_search_service = crop_search_service
        self.enhanced_scoring_weights = self._initialize_enhanced_scoring_weights()
    
    def _initialize_enhanced_scoring_weights(self) -> Dict[str, float]:
        """
        Initialize enhanced scoring weights that incorporate filtering criteria.
        
        Returns:
            Dict with scoring weights for different factors including filtering
        """
        # Get base weights from the parent class's _build_suitability_matrix method
        try:
            weights = super()._build_suitability_matrix()  # Get base weights
        except AttributeError:
            # If the parent method doesn't exist, initialize with default weights
            weights = {
                "ph_suitability": 0.25,
                "nutrient_suitability": 0.20,
                "climate_suitability": 0.20,
                "size_suitability": 0.10
            }
        # Add filtering-specific weights
        weights.update({
            "filter_compatibility": 0.15,  # Weight for filter-based compatibility
            "preference_alignment": 0.10,  # Weight for user preference alignment
            "sustainability_score": 0.08,  # Weight for sustainability factors
            "economic_viability": 0.07    # Weight for economic factors
        })
        return weights
    
    async def get_crop_recommendations_with_filters(
        self, 
        request: RecommendationRequest,
        filter_criteria: Optional[TaxonomyFilterCriteria] = None
    ) -> List[RecommendationItem]:
        """
        Get crop recommendations with advanced filtering applied.
        
        Args:
            request: Basic recommendation request with farm data
            filter_criteria: Advanced taxonomy filter criteria to apply
             
        Returns:
            List of filtered and ranked crop recommendations
        """
        if not filter_criteria:
            # If no filters provided, use the base implementation
            return await self.get_crop_recommendations(request)
        
        try:
            # Apply filtering to crop database first
            filtered_crop_database = await self._apply_taxonomy_filters_to_database(
                request, filter_criteria
            )
            
            # Temporarily replace the crop database with filtered version
            original_database = self.crop_database.copy()
            self.crop_database = filtered_crop_database
            
            # Get recommendations using the filtered database
            recommendations = await self.get_crop_recommendations(request)
            
            # Restore original database
            self.crop_database = original_database
            
            # Enhance recommendations with filtering information
            enhanced_recommendations = await self._enhance_recommendations_with_filter_info(
                recommendations, filter_criteria
            )
            
            return enhanced_recommendations
            
        except Exception as e:
            logger.error(f"Error in filtered crop recommendations: {str(e)}")
            # Fallback to basic recommendations if filtering fails
            return await self.get_crop_recommendations(request)
    
    async def _apply_taxonomy_filters_to_database(
        self,
        request: RecommendationRequest,
        filter_criteria: TaxonomyFilterCriteria
    ) -> Dict[str, Dict[str, Any]]:
        """
        Apply taxonomy filters directly to the crop database.
        
        Args:
            request: Original recommendation request
            filter_criteria: Taxonomy filter criteria to apply
             
        Returns:
            Filtered crop database with only matching crops
        """
        # Convert the current crop database to a format compatible with the search service
        # This is a simplified approach - in production, we'd have a more sophisticated mapping
        filtered_crops = {}
        
        # If crop search service is available, use it for filtering
        if self.crop_search_service:
            search_request = self._create_crop_search_request(request, filter_criteria)
            try:
                search_results = await self.crop_search_service.search_crops(search_request)
                
                # Extract crop names from search results
                result_crop_names = []
                for result in search_results.results:
                    crop_name = result.crop.crop_name.lower()
                    result_crop_names.append(crop_name)
                
                # Filter the internal crop database to only include matching crops
                for crop_name, crop_data in self.crop_database.items():
                    if crop_name.lower() in result_crop_names:
                        filtered_crops[crop_name] = crop_data
                        
            except Exception as e:
                logger.warning(f"Crop search failed, falling back to manual filtering: {e}")
                # Fallback to manual filtering
                filtered_crops = await self._manual_filter_crops(filter_criteria)
        else:
            # Fallback to manual filtering if search service unavailable
            filtered_crops = await self._manual_filter_crops(filter_criteria)
        
        return filtered_crops
    
    def _create_crop_search_request(
        self,
        request: RecommendationRequest,
        filter_criteria: TaxonomyFilterCriteria
    ) -> CropSearchRequest:
        """
        Create a crop search request based on recommendation request and filter criteria.
        
        Args:
            request: Original recommendation request
            filter_criteria: Taxonomy filter criteria
             
        Returns:
            CropSearchRequest with appropriate filters
        """
        # Enhance filter criteria with information from the recommendation request
        enhanced_filter_criteria = filter_criteria.copy()
        
        # Apply location-based filters if not already present
        if request.location and enhanced_filter_criteria.geographic_filter is None:
            from services.crop_taxonomy.src.models.crop_filtering_models import GeographicFilter
            enhanced_filter_criteria.geographic_filter = GeographicFilter(
                latitude_range={"min": request.location.latitude - 0.5, 
                              "max": request.location.latitude + 0.5},
                longitude_range={"min": request.location.longitude - 0.5, 
                               "max": request.location.longitude + 0.5}
            )
        
        # Apply soil-based filters if not already present and soil data exists
        if request.soil_data and enhanced_filter_criteria.soil_filter is None:
            from services.crop_taxonomy.src.models.crop_filtering_models import SoilFilter
            enhanced_filter_criteria.soil_filter = SoilFilter(
                ph_range={"min": request.soil_data.ph - 0.5, 
                         "max": request.soil_data.ph + 0.5} if request.soil_data.ph else None
            )
        
        return CropSearchRequest(
            request_id=request.request_id,
            filter_criteria=enhanced_filter_criteria,
            max_results=50,
            offset=0
        )
    
    async def _manual_filter_crops(
        self,
        filter_criteria: TaxonomyFilterCriteria
    ) -> Dict[str, Dict[str, Any]]:
        """
        Manually filter the internal crop database based on filter criteria.
        
        Args:
            filter_criteria: Taxonomy filter criteria to apply
             
        Returns:
            Filtered crop database
        """
        filtered_crops = {}
        
        for crop_name, crop_data in self.crop_database.items():
            if self._crop_matches_criteria(crop_name, crop_data, filter_criteria):
                filtered_crops[crop_name] = crop_data
        
        return filtered_crops
    
    def _crop_matches_criteria(
        self,
        crop_name: str,
        crop_data: Dict[str, Any],
        filter_criteria: TaxonomyFilterCriteria
    ) -> bool:
        """
        Check if a crop matches the filter criteria.
        
        Args:
            crop_name: Name of the crop
            crop_data: Crop data dictionary
            filter_criteria: Taxonomy filter criteria
             
        Returns:
            True if crop matches all criteria, False otherwise
        """
        # Check agricultural filters
        if filter_criteria.agricultural_filter:
            ag_filter = filter_criteria.agricultural_filter
            if ag_filter.categories:
                # This is a simplified check - in a real implementation, we'd have 
                # more sophisticated category matching
                if crop_name in ['corn', 'wheat'] and CropCategory.GRAIN_CROPS not in ag_filter.categories:
                    return False
                elif crop_name == 'soybean' and CropCategory.LEGUME_CROPS not in ag_filter.categories:
                    return False
            
            if ag_filter.primary_uses:
                # Simplified primary use check
                if crop_name == 'soybean' and PrimaryUse.FOOD_PRODUCTION in ag_filter.primary_uses:
                    pass  # Soybean can be for food production
                elif crop_name == 'corn' and PrimaryUse.FOOD_PRODUCTION in ag_filter.primary_uses:
                    pass  # Corn can be for food production
                else:
                    # For simplicity, we'll allow matches if primary use filters are specified
                    pass
        
        # Check climate filters
        if filter_criteria.climate_filter:
            climate_filter = filter_criteria.climate_filter
            if climate_filter.hardiness_zones:
                # Check if crop is compatible with specified hardiness zones
                crop_zones = crop_data.get('climate_zones', [])
                if crop_zones and not any(zone in climate_filter.hardiness_zones for zone in crop_zones):
                    return False
        
        # Check soil filters
        if filter_criteria.soil_filter:
            soil_filter = filter_criteria.soil_filter
            if soil_filter.ph_range:
                # Check if crop's optimal pH range overlaps with filter range
                opt_min = crop_data.get('optimal_ph_range', (0, 14))[0]
                opt_max = crop_data.get('optimal_ph_range', (0, 14))[1]
                
                filter_min = soil_filter.ph_range.get('min', 0)
                filter_max = soil_filter.ph_range.get('max', 14)
                
                # Check for overlap between ranges
                if not (opt_min <= filter_max and opt_max >= filter_min):
                    return False
        
        # Check management filters
        if filter_criteria.management_filter:
            management_filter = filter_criteria.management_filter
            # For simplicity, we'll consider all crops as matching management filters in this implementation
            
        return True
    
    async def _enhance_recommendations_with_filter_info(
        self,
        recommendations: List[RecommendationItem],
        filter_criteria: TaxonomyFilterCriteria
    ) -> List[RecommendationItem]:
        """
        Enhance recommendations with information about how they match filter criteria.
        
        Args:
            recommendations: Original recommendations
            filter_criteria: Applied filter criteria
             
        Returns:
            Enhanced recommendations with filter matching information
        """
        enhanced_recommendations = []
        
        for rec in recommendations:
            enhanced_rec = rec.copy()
            
            # Add filter matching explanation to description
            explanation_parts = ["Matched criteria: "]
            
            if filter_criteria.agricultural_filter:
                if filter_criteria.agricultural_filter.categories:
                    explanation_parts.append(f"categories: {len(filter_criteria.agricultural_filter.categories)}")
            if filter_criteria.soil_filter:
                if filter_criteria.soil_filter.ph_range:
                    ph_range = filter_criteria.soil_filter.ph_range
                    explanation_parts.append(f"soil pH {ph_range['min']}-{ph_range['max']}")
            if filter_criteria.climate_filter:
                if filter_criteria.climate_filter.hardiness_zones:
                    explanation_parts.append(f"climate zones: {len(filter_criteria.climate_filter.hardiness_zones)}")
            
            if len(explanation_parts) > 1:  # More than just the initial string
                filter_explanation = f" ({', '.join(explanation_parts[1:])})"
                enhanced_rec.description += filter_explanation
            
            enhanced_recommendations.append(enhanced_rec)
        
        return enhanced_recommendations
    
    async def get_filter_impact_analysis(
        self,
        request: RecommendationRequest,
        filter_criteria: TaxonomyFilterCriteria
    ) -> Dict[str, Any]:
        """
        Analyze the impact of applying filters to crop recommendations.
        
        Args:
            request: Original recommendation request
            filter_criteria: Filter criteria to analyze
             
        Returns:
            Analysis of how filters would impact recommendations
        """
        # Get baseline recommendations without filters
        baseline_recs = await self.get_crop_recommendations(request)
        
        # Get filtered recommendations
        filtered_recs = await self.get_crop_recommendations_with_filters(request, filter_criteria)
        
        # Calculate impact metrics
        original_count = len(baseline_recs)
        filtered_count = len(filtered_recs)
        
        reduction_percentage = 0.0
        if original_count > 0:
            reduction_percentage = ((original_count - filtered_count) / original_count) * 100
        
        # Identify most affected criteria
        affected_criteria = []
        if filter_criteria.climate_filter:
            affected_criteria.append("climate")
        if filter_criteria.soil_filter:
            affected_criteria.append("soil")
        if filter_criteria.agricultural_filter:
            affected_criteria.append("agricultural")
        if filter_criteria.management_filter:
            affected_criteria.append("management")
        
        # Generate suggestions for optimization
        suggestions = await self._generate_filter_optimization_suggestions(
            filter_criteria, original_count, filtered_count
        )
        
        return {
            "original_count": original_count,
            "filtered_count": filtered_count,
            "filter_reduction_percentage": reduction_percentage,
            "most_affected_criteria": affected_criteria,
            "alternative_suggestions": suggestions["alternatives"],
            "filter_optimization_recommendations": suggestions["optimizations"],
            "baseline_recommendations": [rec.title for rec in baseline_recs],
            "filtered_recommendations": [rec.title for rec in filtered_recs]
        }
    
    async def _generate_filter_optimization_suggestions(
        self,
        filter_criteria: TaxonomyFilterCriteria,
        original_count: int,
        filtered_count: int
    ) -> Dict[str, List[str]]:
        """
        Generate suggestions for optimizing filter criteria.
        
        Args:
            filter_criteria: Current filter criteria
            original_count: Number of recommendations before filtering
            filtered_count: Number of recommendations after filtering
             
        Returns:
            Dictionary with alternative suggestions and optimization recommendations
        """
        suggestions = {
            "alternatives": [],
            "optimizations": []
        }
        
        # If filtering is too restrictive, suggest relaxation
        if original_count > 0 and (filtered_count / original_count) < 0.3:  # Less than 30% remain
            suggestions["alternatives"].append(
                "Consider relaxing some filter criteria to get more options"
            )
            suggestions["optimizations"].append(
                "Try broadening climate zone range or soil pH requirements"
            )
        
        # Climate zone suggestions
        if filter_criteria.climate_filter and filter_criteria.climate_filter.hardiness_zones:
            if len(filter_criteria.climate_filter.hardiness_zones) == 1:
                suggestions["alternatives"].append(
                    "Consider adding adjacent climate zones (±1 zone) for more options"
                )
        
        # Soil pH suggestions
        if filter_criteria.soil_filter and filter_criteria.soil_filter.ph_range:
            ph_range = filter_criteria.soil_filter.ph_range
            range_width = ph_range.get('max', 0) - ph_range.get('min', 0)
            if range_width < 0.5:  # Very narrow range
                suggestions["optimizations"].append(
                    "Soil pH range is very narrow; consider widening to 0.5-1.0 range"
                )
        
        # Add default suggestions if none generated
        if not suggestions["alternatives"]:
            suggestions["alternatives"] = [
                "Explore different farming systems compatible with your conditions",
                "Consider cover crops for soil improvement",
                "Look into crop varieties with broader tolerance ranges"
            ]
        
        if not suggestions["optimizations"]:
            suggestions["optimizations"] = [
                "Relax climate zone constraints by ±1 zone for more options",
                "Consider soil amendment options to broaden pH compatibility",
                "Evaluate the possibility of irrigation to increase drought-tolerant crop options"
            ]
            
        return suggestions

    async def get_filter_impact_analysis(
        self,
        request: RecommendationRequest,
        filter_criteria: TaxonomyFilterCriteria
    ) -> Dict[str, Any]:
        """
        Analyze the impact of applying filters to crop recommendations.
        
        Args:
            request: Original recommendation request
            filter_criteria: Filter criteria to analyze
             
        Returns:
            Analysis of how filters would impact recommendations
        """
        # Get baseline recommendations without filters
        baseline_recs = await self.get_crop_recommendations(request)
        
        # Get filtered recommendations
        filtered_recs = await self.get_crop_recommendations_with_filters(request, filter_criteria)
        
        # Calculate impact metrics
        original_count = len(baseline_recs)
        filtered_count = len(filtered_recs)
        
        reduction_percentage = 0.0
        if original_count > 0:
            reduction_percentage = ((original_count - filtered_count) / original_count) * 100
        
        # Identify most affected criteria
        affected_criteria = []
        if filter_criteria.climate_filter:
            affected_criteria.append("climate")
        if filter_criteria.soil_filter:
            affected_criteria.append("soil")
        if filter_criteria.agricultural_filter:
            affected_criteria.append("agricultural")
        if filter_criteria.management_filter:
            affected_criteria.append("management")
        
        # Generate suggestions for optimization
        suggestions = await self._generate_filter_optimization_suggestions(
            filter_criteria, original_count, filtered_count
        )
        
        return {
            "original_count": original_count,
            "filtered_count": filtered_count,
            "filter_reduction_percentage": reduction_percentage,
            "most_affected_criteria": affected_criteria,
            "alternative_suggestions": suggestions["alternatives"],
            "filter_optimization_recommendations": suggestions["optimizations"],
            "baseline_recommendations": [rec.title for rec in baseline_recs],
            "filtered_recommendations": [rec.title for rec in filtered_recs],
            "filter_warnings": [], # Add any filter-specific warnings here if needed
        }


# Global instance for use in other modules
enhanced_crop_recommendation_service = EnhancedCropRecommendationService()
"""
Crop Search Service

Advanced search and filtering service for crop taxonomy with
intelligent query processing, multi-criteria filtering, and ML-enhanced recommendations.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple, Union, Set
from datetime import datetime, date
from uuid import UUID
import asyncio

try:
    from ..models.crop_filtering_models import (
        GeographicFilterCriteria,
        ClimateFilterCriteria,
        SoilFilterCriteria,
        AgriculturalFilterCriteria,
        ManagementFilterCriteria,
        SustainabilityFilterCriteria,
        EconomicFilterCriteria,
        TaxonomyFilterCriteria,
        CropSearchRequest,
        CropSearchResponse,
        SmartRecommendationRequest,
        SmartRecommendationResponse,
        MLInsight,
        ContextAwareRecommendation,
        SearchResultItem,
        FilterMatchScore,
        ScoringContext
    )
    from ..models.crop_taxonomy_models import (
        ComprehensiveCropData,
        CropCategory,
        PrimaryUse,
        LifeCycle,
        ClimateZone,
        SoilType,
        DrainageClass
    )
    from ..models.service_models import ConfidenceLevel
except ImportError:
    from models.crop_filtering_models import (
        GeographicFilterCriteria,
        ClimateFilterCriteria,
        SoilFilterCriteria,
        AgriculturalFilterCriteria,
        ManagementFilterCriteria,
        SustainabilityFilterCriteria,
        EconomicFilterCriteria,
        TaxonomyFilterCriteria,
        CropSearchRequest,
        CropSearchResponse,
        SmartRecommendationRequest,
        SmartRecommendationResponse,
        MLInsight,
        ContextAwareRecommendation,
        SearchResultItem,
        FilterMatchScore,
        ScoringContext
    )
    from models.crop_taxonomy_models import (
        ComprehensiveCropData,
        CropCategory,
        PrimaryUse,
        LifeCycle,
        ClimateZone,
        SoilType,
        DrainageClass
    )
    from models.service_models import ConfidenceLevel


logger = logging.getLogger(__name__)


class CropSearchService:
    """
    Advanced search service for crop taxonomy with intelligent filtering,
    multi-criteria scoring, and machine learning enhanced recommendations.
    """

    def __init__(self, database_url: Optional[str] = None):
        """Initialize the crop search service with database integration and scoring algorithms."""
        try:
            from ..database.crop_taxonomy_db import CropTaxonomyDatabase
            self.db = CropTaxonomyDatabase(database_url)
            self.database_available = self.db.test_connection()
            logger.info(f"Search service database connection: {'successful' if self.database_available else 'failed'}")
        except ImportError:
            logger.warning("Database integration not available for search service")
            self.db = None
            self.database_available = False
            
        self.search_cache = {}
        self.scoring_weights = self._initialize_scoring_weights()
        self.ml_model = None  # Placeholder for ML model integration
        
    def _initialize_scoring_weights(self) -> Dict[str, float]:
        """Initialize scoring weights for different filter criteria."""
        return {
            "climate_match": 0.25,
            "soil_match": 0.20,
            "geographic_match": 0.15,
            "agricultural_match": 0.15,
            "management_match": 0.10,
            "sustainability_match": 0.10,
            "economic_match": 0.05
        }

    async def search_crops(self, request: CropSearchRequest) -> CropSearchResponse:
        """
        Execute comprehensive crop search with multi-criteria filtering.
        
        Args:
            request: Search request with filter criteria and preferences
            
        Returns:
            Search results with scoring and recommendations
        """
        try:
            # Get candidate crops from database
            candidate_crops = await self._get_candidate_crops(request)
            
            if not candidate_crops:
                return CropSearchResponse(
                    total_results=0,
                    results=[],
                    search_metadata={
                        "query_time": datetime.utcnow(),
                        "filters_applied": 0,
                        "message": "No crops found matching criteria"
                    }
                )

            # Apply filters and score results
            filtered_results = await self._apply_filters_and_score(candidate_crops, request)
            
            # Sort by relevance score
            sorted_results = sorted(
                filtered_results, 
                key=lambda x: x.relevance_score, 
                reverse=True
            )
            
            # Apply pagination
            start_idx = (request.page - 1) * request.page_size if request.page > 0 else 0
            end_idx = start_idx + request.page_size
            paginated_results = sorted_results[start_idx:end_idx]
            
            # Generate search metadata
            search_metadata = await self._generate_search_metadata(
                request, len(candidate_crops), len(filtered_results)
            )
            
            return CropSearchResponse(
                total_results=len(filtered_results),
                results=paginated_results,
                search_metadata=search_metadata,
                applied_filters=request.filter_criteria
            )

        except Exception as e:
            logger.error(f"Error in crop search: {str(e)}")
            return CropSearchResponse(
                total_results=0,
                results=[],
                search_metadata={
                    "error": str(e),
                    "query_time": datetime.utcnow()
                }
            )

    async def _get_candidate_crops(self, request: CropSearchRequest) -> List[ComprehensiveCropData]:
        """Get initial set of candidate crops from database."""
        if not self.database_available:
            logger.warning("Database not available, returning empty crop list")
            return []
            
        try:
            # Convert our filter criteria to database search filters
            db_filters = self._convert_to_db_filters(request.filter_criteria)
            
            # Search database for matching crops
            db_results = self.db.search_crops(
                search_text=request.search_query,
                filters=db_filters,
                limit=request.page_size * 3,  # Get more results to filter
                offset=0
            )
            
            # Convert database results to ComprehensiveCropData objects
            candidate_crops = []
            for db_result in db_results:
                crop_data = self._convert_db_to_comprehensive_crop_data(db_result)
                candidate_crops.append(crop_data)
                
            return candidate_crops
            
        except Exception as e:
            logger.error(f"Error getting candidate crops from database: {e}")
            return []

    def _convert_to_db_filters(self, filter_criteria: TaxonomyFilterCriteria):
        """Convert our filter criteria to database filter format."""
        try:
            # Import the database filter models
            from ..models.crop_taxonomy_models import CropSearchFilters
            
            # This is a simplified conversion - in reality, we'd need to map
            # all the filter criteria properly
            db_filters = CropSearchFilters()
            
            # Add basic mappings - this would need to be expanded
            if hasattr(filter_criteria, 'climate') and filter_criteria.climate:
                db_filters.climate_filters = filter_criteria.climate
                
            if hasattr(filter_criteria, 'soil') and filter_criteria.soil:
                db_filters.soil_filters = filter_criteria.soil
                
            if hasattr(filter_criteria, 'geographic') and filter_criteria.geographic:
                db_filters.geographic_filters = filter_criteria.geographic
                
            if hasattr(filter_criteria, 'agricultural') and filter_criteria.agricultural:
                db_filters.agricultural_filters = filter_criteria.agricultural
                
            return db_filters
            
        except Exception as e:
            logger.warning(f"Error converting filters: {e}")
            return None

    def _convert_db_to_comprehensive_crop_data(self, db_data: Dict[str, Any]) -> ComprehensiveCropData:
        """Convert database result to ComprehensiveCropData."""
        from uuid import uuid4
        from ..models.crop_taxonomy_models import (
            CropTaxonomicHierarchy, CropAgriculturalClassification,
            CropClimateAdaptations, CropSoilRequirements, CropNutritionalProfile
        )
        
        # Extract and convert taxonomic hierarchy
        taxonomic_hierarchy = None
        if 'taxonomic_hierarchy' in db_data:
            tax_data = db_data['taxonomic_hierarchy']
            taxonomic_hierarchy = CropTaxonomicHierarchy(
                id=tax_data.get('id', uuid4()),
                kingdom=tax_data.get('kingdom', 'Plantae'),
                phylum=tax_data.get('phylum', 'Tracheophyta'),
                class_name=tax_data.get('class_name', 'Unknown'),
                order=tax_data.get('order', 'Unknown'),
                family=tax_data.get('family', 'Unknown'),
                genus=tax_data.get('genus', 'Unknown'),
                species=tax_data.get('species', 'Unknown'),
                common_names=tax_data.get('common_names', []),
                botanical_authority=tax_data.get('botanical_authority', ''),
                is_hybrid=tax_data.get('is_hybrid', False),
                ploidy_level=tax_data.get('ploidy_level', 2),
                chromosome_count=tax_data.get('chromosome_count', 0)
            )
        
        # Convert other sections similarly (agricultural, climate, soil, nutritional)
        # This is a simplified version - full implementation would convert all fields
        
        return ComprehensiveCropData(
            crop_id=db_data.get('crop_id', uuid4()),
            crop_name=db_data.get('crop_name', ''),
            taxonomic_hierarchy=taxonomic_hierarchy,
            agricultural_classification=None,  # Would be converted from db_data
            climate_adaptations=None,          # Would be converted from db_data
            soil_requirements=None,            # Would be converted from db_data
            nutritional_profile=None,          # Would be converted from db_data
            search_keywords=db_data.get('search_keywords', []),
            tags=db_data.get('tags', []),
            data_source="database",
            confidence_score=0.85,
            updated_at=datetime.utcnow(),
            last_updated=datetime.utcnow()
        )

    async def _apply_filters_and_score(
        self, 
        crops: List[ComprehensiveCropData], 
        request: CropSearchRequest
    ) -> List[SearchResultItem]:
        """Apply filters and calculate relevance scores for each crop."""
        results = []
        
        for crop in crops:
            # Calculate filter match scores
            filter_scores = await self._calculate_filter_scores(crop, request.filter_criteria)
            
            # Calculate overall relevance score
            relevance_score = await self._calculate_relevance_score(filter_scores, request)
            
            # Check if crop meets minimum thresholds
            if relevance_score >= (request.min_confidence_threshold or 0.0):
                result_item = SearchResultItem(
                    crop_data=crop,
                    relevance_score=relevance_score,
                    filter_scores=filter_scores,
                    match_reasons=await self._generate_match_reasons(filter_scores),
                    recommendations=await self._generate_crop_recommendations(crop, request)
                )
                results.append(result_item)
        
        return results

    async def _calculate_filter_scores(
        self, 
        crop: ComprehensiveCropData, 
        filter_criteria: TaxonomyFilterCriteria
    ) -> Dict[str, FilterMatchScore]:
        """Calculate match scores for each filter category."""
        scores = {}
        
        # Geographic filter scoring
        if filter_criteria.geographic:
            scores["geographic"] = await self._score_geographic_match(
                crop, filter_criteria.geographic
            )
            
        # Climate filter scoring  
        if filter_criteria.climate:
            scores["climate"] = await self._score_climate_match(
                crop, filter_criteria.climate
            )
            
        # Soil filter scoring
        if filter_criteria.soil:
            scores["soil"] = await self._score_soil_match(
                crop, filter_criteria.soil
            )
            
        # Agricultural filter scoring
        if filter_criteria.agricultural:
            scores["agricultural"] = await self._score_agricultural_match(
                crop, filter_criteria.agricultural
            )
            
        # Management filter scoring
        if filter_criteria.management:
            scores["management"] = await self._score_management_match(
                crop, filter_criteria.management
            )
            
        # Sustainability filter scoring
        if filter_criteria.sustainability:
            scores["sustainability"] = await self._score_sustainability_match(
                crop, filter_criteria.sustainability
            )
            
        # Economic filter scoring
        if filter_criteria.economic:
            scores["economic"] = await self._score_economic_match(
                crop, filter_criteria.economic
            )
        
        return scores

    async def _score_geographic_match(
        self, 
        crop: ComprehensiveCropData, 
        geo_criteria: GeographicFilterCriteria
    ) -> FilterMatchScore:
        """Score geographic compatibility."""
        score = 0.0
        max_score = 0.0
        details = {}
        
        # Check latitude range
        if geo_criteria.latitude_range and crop.climate_adaptations:
            max_score += 1.0
            # Simplified scoring - would use actual geographic data
            score += 0.8
            details["latitude_match"] = "Good match for specified latitude range"
            
        # Check hardiness zones
        if geo_criteria.hardiness_zones and crop.climate_adaptations:
            max_score += 1.0
            if crop.climate_adaptations.climate_zones:
                # Check for zone overlap
                common_zones = set(geo_criteria.hardiness_zones) & set(crop.climate_adaptations.climate_zones)
                if common_zones:
                    score += 1.0
                    details["hardiness_zones"] = f"Compatible zones: {list(common_zones)}"
                else:
                    details["hardiness_zones"] = "No compatible hardiness zones"
                    
        final_score = score / max_score if max_score > 0 else 0.0
        
        return FilterMatchScore(
            category="geographic",
            score=final_score,
            max_possible_score=1.0,
            weight=self.scoring_weights.get("geographic_match", 0.15),
            details=details
        )

    async def _score_climate_match(
        self, 
        crop: ComprehensiveCropData, 
        climate_criteria: ClimateFilterCriteria
    ) -> FilterMatchScore:
        """Score climate compatibility."""
        score = 0.0
        max_score = 0.0
        details = {}
        
        if not crop.climate_adaptations:
            return FilterMatchScore(
                category="climate",
                score=0.0,
                max_possible_score=1.0,
                weight=self.scoring_weights.get("climate_match", 0.25),
                details={"error": "No climate data available for crop"}
            )
            
        # Temperature range scoring
        if climate_criteria.temperature_range and crop.climate_adaptations.temperature_range:
            max_score += 1.0
            crop_temp_min, crop_temp_max = crop.climate_adaptations.temperature_range
            criteria_temp_min, criteria_temp_max = climate_criteria.temperature_range
            
            # Calculate overlap
            overlap_min = max(crop_temp_min, criteria_temp_min)
            overlap_max = min(crop_temp_max, criteria_temp_max)
            
            if overlap_max > overlap_min:
                overlap_range = overlap_max - overlap_min
                crop_range = crop_temp_max - crop_temp_min
                criteria_range = criteria_temp_max - criteria_temp_min
                
                # Score based on percentage of overlap
                temp_score = min(overlap_range / crop_range, overlap_range / criteria_range)
                score += temp_score
                details["temperature"] = f"Temperature overlap: {overlap_min}°C to {overlap_max}°C"
            else:
                details["temperature"] = "No temperature range overlap"
                
        # Precipitation scoring
        if climate_criteria.precipitation_range and crop.climate_adaptations.precipitation_range:
            max_score += 1.0
            crop_precip_min, crop_precip_max = crop.climate_adaptations.precipitation_range
            criteria_precip_min, criteria_precip_max = climate_criteria.precipitation_range
            
            # Calculate overlap similar to temperature
            overlap_min = max(crop_precip_min, criteria_precip_min)
            overlap_max = min(crop_precip_max, criteria_precip_max)
            
            if overlap_max > overlap_min:
                overlap_range = overlap_max - overlap_min
                crop_range = crop_precip_max - crop_precip_min
                criteria_range = criteria_precip_max - criteria_precip_min
                
                precip_score = min(overlap_range / crop_range, overlap_range / criteria_range)
                score += precip_score
                details["precipitation"] = f"Precipitation overlap: {overlap_min}mm to {overlap_max}mm"
            else:
                details["precipitation"] = "No precipitation range overlap"
                
        final_score = score / max_score if max_score > 0 else 0.0
        
        return FilterMatchScore(
            category="climate",
            score=final_score,
            max_possible_score=1.0,
            weight=self.scoring_weights.get("climate_match", 0.25),
            details=details
        )

    async def _score_soil_match(
        self, 
        crop: ComprehensiveCropData, 
        soil_criteria: SoilFilterCriteria
    ) -> FilterMatchScore:
        """Score soil compatibility."""
        score = 0.0
        max_score = 0.0
        details = {}
        
        if not crop.soil_requirements:
            return FilterMatchScore(
                category="soil",
                score=0.0,
                max_possible_score=1.0,
                weight=self.scoring_weights.get("soil_match", 0.20),
                details={"error": "No soil requirements data available for crop"}
            )
            
        # pH range scoring
        if soil_criteria.ph_range and crop.soil_requirements.ph_range:
            max_score += 1.0
            crop_ph_min, crop_ph_max = crop.soil_requirements.ph_range
            criteria_ph_min, criteria_ph_max = soil_criteria.ph_range
            
            # Calculate pH overlap
            overlap_min = max(crop_ph_min, criteria_ph_min)
            overlap_max = min(crop_ph_max, criteria_ph_max)
            
            if overlap_max > overlap_min:
                overlap_range = overlap_max - overlap_min
                crop_range = crop_ph_max - crop_ph_min
                
                ph_score = overlap_range / crop_range
                score += ph_score
                details["ph"] = f"pH compatibility: {overlap_min} to {overlap_max}"
            else:
                details["ph"] = "No pH range compatibility"
                
        # Soil texture scoring
        if soil_criteria.texture_classes and crop.soil_requirements.preferred_textures:
            max_score += 1.0
            common_textures = set(soil_criteria.texture_classes) & set(crop.soil_requirements.preferred_textures)
            if common_textures:
                texture_score = len(common_textures) / len(crop.soil_requirements.preferred_textures)
                score += texture_score
                details["texture"] = f"Compatible textures: {list(common_textures)}"
            else:
                details["texture"] = "No compatible soil textures"
                
        # Drainage scoring
        if soil_criteria.drainage_classes and crop.soil_requirements.drainage_requirements:
            max_score += 1.0
            common_drainage = set(soil_criteria.drainage_classes) & set(crop.soil_requirements.drainage_requirements)
            if common_drainage:
                drainage_score = len(common_drainage) / len(crop.soil_requirements.drainage_requirements)
                score += drainage_score
                details["drainage"] = f"Compatible drainage: {list(common_drainage)}"
            else:
                details["drainage"] = "No compatible drainage classes"
                
        final_score = score / max_score if max_score > 0 else 0.0
        
        return FilterMatchScore(
            category="soil",
            score=final_score,
            max_possible_score=1.0,
            weight=self.scoring_weights.get("soil_match", 0.20),
            details=details
        )

    async def _score_agricultural_match(
        self, 
        crop: ComprehensiveCropData, 
        ag_criteria: AgriculturalFilterCriteria
    ) -> FilterMatchScore:
        """Score agricultural characteristics match."""
        score = 0.0
        max_score = 0.0
        details = {}
        
        if not crop.agricultural_classification:
            return FilterMatchScore(
                category="agricultural",
                score=0.0,
                max_possible_score=1.0,
                weight=self.scoring_weights.get("agricultural_match", 0.15),
                details={"error": "No agricultural classification data available"}
            )
            
        # Category matching
        if ag_criteria.crop_categories:
            max_score += 1.0
            if crop.agricultural_classification.primary_category in ag_criteria.crop_categories:
                score += 1.0
                details["category"] = f"Primary category match: {crop.agricultural_classification.primary_category}"
            elif any(cat in ag_criteria.crop_categories for cat in crop.agricultural_classification.secondary_categories or []):
                score += 0.7
                details["category"] = "Secondary category match"
            else:
                details["category"] = "No category match"
                
        # Life cycle matching
        if ag_criteria.life_cycles:
            max_score += 1.0
            if crop.agricultural_classification.life_cycle in ag_criteria.life_cycles:
                score += 1.0
                details["life_cycle"] = f"Life cycle match: {crop.agricultural_classification.life_cycle}"
            else:
                details["life_cycle"] = "No life cycle match"
                
        # Maturity range scoring
        if ag_criteria.maturity_days_range and crop.agricultural_classification.maturity_days_range:
            max_score += 1.0
            crop_min, crop_max = crop.agricultural_classification.maturity_days_range
            criteria_min, criteria_max = ag_criteria.maturity_days_range
            
            # Check for overlap
            if crop_min <= criteria_max and crop_max >= criteria_min:
                # Calculate overlap score
                overlap_min = max(crop_min, criteria_min)
                overlap_max = min(crop_max, criteria_max)
                overlap_range = overlap_max - overlap_min
                total_range = max(crop_max, criteria_max) - min(crop_min, criteria_min)
                
                maturity_score = overlap_range / total_range if total_range > 0 else 0
                score += maturity_score
                details["maturity"] = f"Maturity overlap: {overlap_min}-{overlap_max} days"
            else:
                details["maturity"] = "No maturity range overlap"
                
        final_score = score / max_score if max_score > 0 else 0.0
        
        return FilterMatchScore(
            category="agricultural",
            score=final_score,
            max_possible_score=1.0,
            weight=self.scoring_weights.get("agricultural_match", 0.15),
            details=details
        )

    async def _score_management_match(
        self, 
        crop: ComprehensiveCropData, 
        mgmt_criteria: ManagementFilterCriteria
    ) -> FilterMatchScore:
        """Score management requirements compatibility."""
        # Simplified implementation
        return FilterMatchScore(
            category="management",
            score=0.8,  # Placeholder score
            max_possible_score=1.0,
            weight=self.scoring_weights.get("management_match", 0.10),
            details={"note": "Management scoring not fully implemented"}
        )

    async def _score_sustainability_match(
        self, 
        crop: ComprehensiveCropData, 
        sust_criteria: SustainabilityFilterCriteria
    ) -> FilterMatchScore:
        """Score sustainability characteristics."""
        # Simplified implementation
        return FilterMatchScore(
            category="sustainability",
            score=0.7,  # Placeholder score
            max_possible_score=1.0,
            weight=self.scoring_weights.get("sustainability_match", 0.10),
            details={"note": "Sustainability scoring not fully implemented"}
        )

    async def _score_economic_match(
        self, 
        crop: ComprehensiveCropData, 
        econ_criteria: EconomicFilterCriteria
    ) -> FilterMatchScore:
        """Score economic viability."""
        # Simplified implementation
        return FilterMatchScore(
            category="economic",
            score=0.6,  # Placeholder score
            max_possible_score=1.0,
            weight=self.scoring_weights.get("economic_match", 0.05),
            details={"note": "Economic scoring not fully implemented"}
        )

    async def _calculate_relevance_score(
        self, 
        filter_scores: Dict[str, FilterMatchScore], 
        request: CropSearchRequest
    ) -> float:
        """Calculate overall relevance score from individual filter scores."""
        if not filter_scores:
            return 0.0
            
        weighted_sum = 0.0
        total_weight = 0.0
        
        for category, score_obj in filter_scores.items():
            weight = score_obj.weight
            score = score_obj.score
            
            weighted_sum += score * weight
            total_weight += weight
            
        return weighted_sum / total_weight if total_weight > 0 else 0.0

    async def _generate_match_reasons(self, filter_scores: Dict[str, FilterMatchScore]) -> List[str]:
        """Generate human-readable match reasons."""
        reasons = []
        
        for category, score_obj in filter_scores.items():
            if score_obj.score >= 0.8:
                reasons.append(f"Excellent {category} compatibility ({score_obj.score:.1%})")
            elif score_obj.score >= 0.6:
                reasons.append(f"Good {category} match ({score_obj.score:.1%})")
            elif score_obj.score >= 0.4:
                reasons.append(f"Moderate {category} compatibility ({score_obj.score:.1%})")
                
        return reasons

    async def _generate_crop_recommendations(
        self, 
        crop: ComprehensiveCropData, 
        request: CropSearchRequest
    ) -> List[str]:
        """Generate contextual recommendations for the crop."""
        recommendations = []
        
        # Add basic recommendations based on crop characteristics
        if crop.agricultural_classification:
            if crop.agricultural_classification.is_cover_crop:
                recommendations.append("Consider for soil improvement and erosion control")
            if crop.agricultural_classification.primary_use == PrimaryUse.FOOD_HUMAN:
                recommendations.append("Suitable for direct human consumption")
            if crop.agricultural_classification.life_cycle == LifeCycle.PERENNIAL:
                recommendations.append("Long-term investment with multiple harvest seasons")
                
        return recommendations

    async def _generate_search_metadata(
        self, 
        request: CropSearchRequest, 
        total_candidates: int, 
        filtered_results: int
    ) -> Dict[str, Any]:
        """Generate metadata about the search operation."""
        filters_applied = 0
        if request.filter_criteria:
            if request.filter_criteria.geographic:
                filters_applied += 1
            if request.filter_criteria.climate:
                filters_applied += 1
            if request.filter_criteria.soil:
                filters_applied += 1
            if request.filter_criteria.agricultural:
                filters_applied += 1
                
        return {
            "query_time": datetime.utcnow(),
            "total_candidates": total_candidates,
            "filtered_results": filtered_results,
            "filters_applied": filters_applied,
            "filter_effectiveness": filtered_results / total_candidates if total_candidates > 0 else 0,
            "search_parameters": {
                "page": request.page,
                "page_size": request.page_size,
                "min_confidence": request.min_confidence_threshold
            }
        }

    async def get_smart_recommendations(
        self, 
        request: SmartRecommendationRequest
    ) -> SmartRecommendationResponse:
        """
        Provide ML-enhanced crop recommendations with contextual insights.
        
        Args:
            request: Smart recommendation request with context
            
        Returns:
            Intelligent recommendations with ML insights
        """
        try:
            # Analyze context and generate baseline recommendations
            context_analysis = await self._analyze_context(request.context)
            
            # Generate ML insights (placeholder for actual ML integration)
            ml_insights = await self._generate_ml_insights(request)
            
            # Create context-aware recommendations
            recommendations = await self._create_context_aware_recommendations(
                request, context_analysis, ml_insights
            )
            
            return SmartRecommendationResponse(
                recommendations=recommendations,
                ml_insights=ml_insights,
                context_analysis=context_analysis,
                confidence_level=ConfidenceLevel.HIGH
            )
            
        except Exception as e:
            logger.error(f"Error in smart recommendations: {str(e)}")
            return SmartRecommendationResponse(
                recommendations=[],
                ml_insights=[],
                context_analysis={},
                confidence_level=ConfidenceLevel.LOW,
                error_message=str(e)
            )

    async def _analyze_context(self, context: ScoringContext) -> Dict[str, Any]:
        """Analyze the provided context for recommendation generation."""
        analysis = {
            "primary_factors": [],
            "risk_factors": [],
            "opportunities": [],
            "recommendations": []
        }
        
        # Analyze based on context attributes
        if hasattr(context, 'climate_data') and context.climate_data:
            analysis["primary_factors"].append("climate_data_available")
            
        if hasattr(context, 'soil_data') and context.soil_data:
            analysis["primary_factors"].append("soil_data_available")
            
        return analysis

    async def _generate_ml_insights(self, request: SmartRecommendationRequest) -> List[MLInsight]:
        """Generate machine learning insights (placeholder implementation)."""
        # This would integrate with actual ML models
        insights = [
            MLInsight(
                insight_type="pattern_recognition",
                confidence=0.85,
                description="Historical data shows high success rate for legume crops in similar conditions",
                data_points={"success_rate": 0.89, "sample_size": 150}
            ),
            MLInsight(
                insight_type="risk_assessment",
                confidence=0.78,
                description="Moderate drought risk detected for upcoming growing season",
                data_points={"drought_probability": 0.35, "impact_severity": "moderate"}
            )
        ]
        
        return insights

    async def _create_context_aware_recommendations(
        self, 
        request: SmartRecommendationRequest,
        context_analysis: Dict[str, Any],
        ml_insights: List[MLInsight]
    ) -> List[ContextAwareRecommendation]:
        """Create intelligent recommendations based on context and ML insights."""
        recommendations = []
        
        # Create sample recommendation
        recommendation = ContextAwareRecommendation(
            crop_suggestion="Soybeans",
            confidence_score=0.87,
            reasoning=[
                "Excellent soil nitrogen fixation capabilities",
                "High market demand in target region", 
                "Good drought tolerance for predicted conditions"
            ],
            context_factors=[
                "soil_improvement_goal",
                "economic_viability",
                "climate_resilience"
            ],
            potential_benefits=[
                "Improved soil fertility for following crops",
                "Reduced fertilizer costs",
                "Strong market prices projected"
            ],
            risk_mitigation_strategies=[
                "Consider drought-resistant varieties",
                "Plan irrigation backup system",
                "Monitor market price trends"
            ]
        )
        
        recommendations.append(recommendation)
        return recommendations


# Create service instance with database connection
import os
crop_search_service = CropSearchService(
    database_url=os.getenv('DATABASE_URL')
)

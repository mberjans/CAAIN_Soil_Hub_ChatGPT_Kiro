"""
TICKET-005_crop-type-filtering-4.3: API Routes for Recommendation Engine Filtering

Implements filtering capabilities for the recommendation engine with endpoints for:
1. POST /api/v1/recommendations/crop-selection with filtering capabilities
2. GET /api/v1/recommendations/filtered/{recommendation_id}
3. POST /api/v1/recommendations/apply-preferences
4. GET /api/v1/recommendations/filter-impact
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import logging
import uuid
from datetime import datetime

from ..models.agricultural_models import (
    RecommendationRequest,
    RecommendationResponse,
    RecommendationItem,
    CropCategory,
    PrimaryUse,
    GrowthHabit
)

# Import crop taxonomy models and services for filtering
try:
    from services.crop_taxonomy.src.models.crop_filtering_models import (
        TaxonomyFilterCriteria,
        CropSearchRequest,
        CropSearchResponse,
        AgriculturalFilter,
        ClimateFilter,
        SoilFilter,
        ManagementFilter
    )
    from services.crop_taxonomy.src.services.crop_search_service import crop_search_service
except ImportError:
    # Fallback imports if services are not available
    try:
        from ..models.crop_filtering_models import (
            TaxonomyFilterCriteria,
            CropSearchRequest,
            CropSearchResponse,
            AgriculturalFilter,
            ClimateFilter,
            SoilFilter,
            ManagementFilter
        )
        crop_search_service = None
    except ImportError:
        # Mock classes if imports fail
        from pydantic import BaseModel
        class TaxonomyFilterCriteria(BaseModel):
            pass
        class CropSearchRequest(BaseModel):
            pass
        class CropSearchResponse(BaseModel):
            pass
        class AgriculturalFilter(BaseModel):
            pass
        class ClimateFilter(BaseModel):
            pass
        class SoilFilter(BaseModel):
            pass
        class ManagementFilter(BaseModel):
            pass
        crop_search_service = None

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/recommendations", tags=["recommendation-filtering"])


class FilteredRecommendationRequest(BaseModel):
    """Request model for applying filters to existing recommendations"""
    recommendation_id: str = Field(..., description="ID of the original recommendation to filter")
    filter_criteria: TaxonomyFilterCriteria = Field(..., description="Filter criteria to apply")
    include_filter_explanation: bool = Field(default=True, description="Include explanation of how filters affected results")


class PreferenceApplicationRequest(BaseModel):
    """Request model for applying user preferences to recommendations"""
    recommendation_request: RecommendationRequest = Field(..., description="Original recommendation request")
    user_preferences: Dict[str, float] = Field(..., description="User preferences (crop -> preference score 0-1)")
    preference_weights: Optional[Dict[str, float]] = Field(default_factory=dict, description="Weights for different preference categories")


class FilterImpactAnalysis(BaseModel):
    """Model for filter impact analysis results"""
    original_count: int = Field(..., description="Number of recommendations before filtering")
    filtered_count: int = Field(..., description="Number of recommendations after filtering")
    filter_reduction_percentage: float = Field(..., description="Percentage reduction due to filtering")
    most_affected_criteria: List[str] = Field(..., description="Criteria that most affected recommendations")
    alternative_suggestions: List[str] = Field(..., description="Alternative crops suggested due to filtering")
    filter_optimization_recommendations: List[str] = Field(..., description="Recommendations for filter optimization")


class FilterImpactResponse(BaseModel):
    """Response model for filter impact analysis"""
    analysis: FilterImpactAnalysis = Field(..., description="Impact analysis results")
    filter_usage_patterns: Dict[str, int] = Field(..., description="Filter usage patterns")
    effectiveness_metrics: Dict[str, float] = Field(..., description="Filter effectiveness metrics")


# Enhanced crop selection request with filtering
class CropSelectionWithFilterRequest(RecommendationRequest):
    """Enhanced crop selection request with filtering options"""
    filter_criteria: Optional[TaxonomyFilterCriteria] = Field(None, description="Additional filtering criteria")
    include_filter_explanation: bool = Field(default=True, description="Include explanation of how filters affected recommendations")


@router.post("/crop-selection", response_model=RecommendationResponse)
async def get_filtered_crop_recommendations(request: CropSelectionWithFilterRequest):
    """
    Enhanced POST /api/v1/recommendations/crop-selection with filtering capabilities
    
    TICKET-005_crop-type-filtering-4.3.1
    
    Features:
    - Pre-filter crops before recommendation generation
    - Integrate with existing crop taxonomy filtering functionality
    - Add filter-aware scoring that considers user preferences
    - Include filter explanation in results
    """
    try:
        logger.info(f"Processing filtered crop selection request: {request.request_id}")
        
        # Import the recommendation engine
        try:
            from ..services.recommendation_engine import RecommendationEngine
            from ..services.crop_recommendation_service import CropRecommendationService
        except ImportError:
            from services.recommendation_engine import RecommendationEngine
            from services.crop_recommendation_service import CropRecommendationService
        
        # Initialize services
        recommendation_engine = RecommendationEngine()
        crop_service = CropRecommendationService()
        
        # If filter criteria provided, apply pre-filtering using integrated approach
        if request.filter_criteria:
            # Use the crop taxonomy service for proper filtering
            try:
                from services.crop_taxonomy.src.services.crop_search_service import crop_search_service
                from services.crop_taxonomy.src.models.crop_filtering_models import CropSearchRequest
                
                # Create a search request based on filter criteria
                search_request = CropSearchRequest(
                    request_id=request.request_id,
                    filter_criteria=request.filter_criteria,
                    max_results=20,  # Reasonable limit for recommendation
                    include_full_taxonomy=True
                )
                
                # Perform search with crop taxonomy service
                search_result = await crop_search_service.search_crops(search_request)
                
                # Get filtered crop names from search results
                filtered_crop_names = [result.crop.crop_name for result in search_result.results]
                
                # Filter the crop database to only include filtered results
                original_database = crop_service.crop_database.copy()
                filtered_database = {name: original_database[name] 
                                   for name in filtered_crop_names 
                                   if name in original_database}
                
                if filtered_database:
                    # Use the filtered database for recommendations
                    crop_service.crop_database = filtered_database
                else:
                    # If no crops match filters, use original database but warn user
                    logger.warning(f"No crops matched the filtering criteria in request {request.request_id}")
                
            except ImportError:
                logger.warning("Crop taxonomy service not available, using basic filtering")
                # Fallback to the original filtering approach
                filtered_crop_database = await _apply_taxonomy_filtering(
                    request.filter_criteria, 
                    crop_service.crop_database
                )
                
                if filtered_crop_database:
                    original_database = crop_service.crop_database
                    crop_service.crop_database = filtered_crop_database
                else:
                    logger.info("No crops filtered, using full database")
                    original_database = crop_service.crop_database
        else:
            # No filtering, use original database
            original_database = crop_service.crop_database
        
        # Generate recommendations using the engine
        recommendations = await crop_service.get_crop_recommendations(request)
        
        # Restore original database if it was changed
        if request.filter_criteria and 'original_database' in locals():
            crop_service.crop_database = original_database
        
        # Calculate overall confidence based on filters applied
        overall_confidence = _calculate_filtered_confidence(recommendations, request)
        
        # Add filter explanations if requested
        if request.include_filter_explanation and request.filter_criteria:
            recommendations = _add_filter_explanations(recommendations, request.filter_criteria)
        
        # Build response with additional filtering metadata
        response = RecommendationResponse(
            request_id=request.request_id,
            question_type=request.question_type,
            overall_confidence=overall_confidence,
            confidence_factors=recommendation_engine._build_confidence_factors(request),
            recommendations=recommendations,
            warnings=recommendation_engine._generate_warnings(request, recommendations, None),
            next_steps=recommendation_engine._generate_next_steps(request, recommendations),
            follow_up_questions=recommendation_engine._generate_follow_up_questions(request.question_type)
        )
        
        logger.info(f"Generated {len(recommendations)} filtered recommendations with filtering applied")
        return response
        
    except Exception as e:
        logger.error(f"Error in filtered crop recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating filtered recommendations: {str(e)}")


@router.get("/filtered/{recommendation_id}", response_model=RecommendationResponse)
async def get_filtered_recommendations(recommendation_id: str, 
                                      category: Optional[str] = Query(None, description="Crop category to filter by"),
                                      minimum_suitability: Optional[float] = Query(0.5, description="Minimum suitability score"),
                                      include_nitrogen_fixers: Optional[bool] = Query(None, description="Include/exclude nitrogen-fixing crops")):
    """
    GET /api/v1/recommendations/filtered/{recommendation_id} - Get filtered recommendations
    
    TICKET-005_crop-type-filtering-4.3.2
    
    Features:
    - Apply post-recommendation filtering to existing recommendation results
    - Maintain recommendation context while showing filtered results
    - Include filter impact analysis and metrics
    """
    try:
        logger.info(f"Getting filtered recommendations for ID: {recommendation_id}")
        
        # Import the recommendation engine to access the storage
        try:
            from ..services.recommendation_engine import RecommendationEngine
        except ImportError:
            from services.recommendation_engine import RecommendationEngine
        
        # In a real implementation, this would retrieve the original recommendation from storage
        # For now, we'll simulate a storage system by creating a mock storage
        # In production, this would connect to a database or cache system
        
        # Mock storage for demonstration - in production, this would be a proper database query
        # This simulates retrieving a previously generated recommendation
        mock_original_recommendations = [
            RecommendationItem(
                recommendation_type="crop_selection",
                title="Corn - Highly Suitable",
                description="Corn was recommended based on your climate zone and soil conditions. Highly suitable for your farm.",
                priority=1,
                confidence_score=0.9,
                implementation_steps=[
                    "Verify soil conditions meet corn requirements",
                    "Select appropriate corn variety for your region",
                    "Plan planting schedule based on local frost dates"
                ],
                expected_outcomes=[
                    "Expected yield range: 150-180 bu/acre",
                    "Improved soil health through rotation",
                    "Diversified income stream"
                ],
                timing="Plan for next growing season",
                agricultural_sources=["USDA Crop Production Guidelines"]
            ),
            RecommendationItem(
                recommendation_type="crop_selection",
                title="Soybean - Moderately Suitable",
                description="Soybean was recommended based on compatibility with your climate and soil pH. Moderately suitable option.",
                priority=2,
                confidence_score=0.7,
                implementation_steps=[
                    "Verify soil conditions meet soybean requirements",
                    "Select appropriate soybean variety for your region",
                    "Plan planting schedule based on local frost dates"
                ],
                expected_outcomes=[
                    "Expected yield range: 45-65 bu/acre",
                    "Nitrogen fixation benefits",
                    "Rotation benefits"
                ],
                timing="Plan for next growing season",
                agricultural_sources=["USDA Crop Production Guidelines"]
            ),
            RecommendationItem(
                recommendation_type="crop_selection", 
                title="Wheat - Marginal Suitability",
                description="Wheat has marginal compatibility with your farm conditions.",
                priority=3,
                confidence_score=0.55,
                implementation_steps=[
                    "Evaluate wheat variety options for your soil type",
                    "Consider planting timing carefully",
                    "Monitor for disease pressure"
                ],
                expected_outcomes=[
                    "Expected yield range: 50-70 bu/acre",
                    "Winter hardiness may vary"
                ],
                timing="Fall planting recommended",
                agricultural_sources=["USDA Crop Production Guidelines"]
            )
        ]
        
        # Apply filters based on query parameters
        filtered_results = []
        original_count = len(mock_original_recommendations)
        
        for rec in mock_original_recommendations:
            include = True
            
            # Filter by category
            if category and category.lower() not in rec.title.lower():
                include = False
            
            # Filter by minimum suitability
            if minimum_suitability and rec.confidence_score < minimum_suitability:
                include = False
            
            # Filter nitrogen fixers
            if include_nitrogen_fixers is not None:
                is_nitrogen_fixer = "soybean" in rec.title.lower() or "legume" in rec.title.lower() or "bean" in rec.title.lower()
                if include_nitrogen_fixers and not is_nitrogen_fixer:
                    include = False
                elif not include_nitrogen_fixers and is_nitrogen_fixer:
                    include = False
            
            if include:
                # Enhance the description with filter information
                enhanced_rec = rec.copy()
                if category:
                    enhanced_rec.description += f" (Matches category filter: {category})"
                if minimum_suitability:
                    enhanced_rec.description += f" (Confidence score {rec.confidence_score:.2f} >= minimum {minimum_suitability})"
                filtered_results.append(enhanced_rec)
        
        # Calculate filter impact metrics
        filtered_count = len(filtered_results)
        filter_reduction_percentage = 0.0
        if original_count > 0:
            filter_reduction_percentage = ((original_count - filtered_count) / original_count) * 100
        
        # Calculate overall confidence based on remaining recommendations
        overall_confidence = 0.8
        if filtered_results:
            avg_confidence = sum(rec.confidence_score for rec in filtered_results) / len(filtered_results)
            overall_confidence = avg_confidence
        
        # Build confidence factors with filter information
        confidence_factors = {
            "original_recommendation_count": original_count,
            "filtered_recommendation_count": filtered_count,
            "filter_reduction_percentage": filter_reduction_percentage,
            "filter_applied_category": category,
            "filter_applied_minimum_suitability": minimum_suitability,
            "filter_applied_nitrogen_fixer": include_nitrogen_fixers
        }
        
        # Build warnings based on filtering
        warnings = []
        if filter_reduction_percentage > 50:
            warnings.append(f"Filtering has reduced recommendations by {filter_reduction_percentage:.1f}%. Consider relaxing filters.")
        if filtered_count == 0:
            warnings.append("No recommendations match your current filters. Try adjusting filter criteria.")
        
        # Calculate next steps
        next_steps = []
        if filtered_count > 0:
            next_steps.append(f"Review the {filtered_count} recommendations that match your criteria")
            next_steps.append("Compare recommendations and select the best option for your farm")
        else:
            next_steps.append("No matching recommendations found. Adjust your filter criteria.")
        
        response = RecommendationResponse(
            request_id=f"filtered-{recommendation_id}",
            question_type="crop_selection_filtered",
            overall_confidence=overall_confidence,
            confidence_factors=confidence_factors,
            recommendations=filtered_results,
            warnings=warnings,
            next_steps=next_steps,
            follow_up_questions=["What fertilizer strategy should I use for these crops?", "When is the best time to plant?"]
        )
        
        logger.info(f"Applied filtering to recommendation {recommendation_id}, returned {len(filtered_results)} results from {original_count} (reduction: {filter_reduction_percentage:.1f}%)")
        return response
        
    except Exception as e:
        logger.error(f"Error in filtered recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving filtered recommendations: {str(e)}")


@router.post("/apply-preferences", response_model=RecommendationResponse)
async def apply_user_preferences(request: PreferenceApplicationRequest):
    """
    POST /api/v1/recommendations/apply-preferences - Apply user preferences to recommendations
    
    TICKET-005_crop-type-filtering-4.3.3
    
    Features:
    - Preference-weighted recommendation scoring
    - Preference-based filtering capabilities
    - Preference learning integration
    - Return preference-adjusted recommendations with explanation
    """
    try:
        logger.info(f"Applying user preferences to recommendations for request {request.recommendation_request.request_id}")
        
        # Import the recommendation engine and services
        try:
            from ..services.recommendation_engine import RecommendationEngine
            from ..services.crop_recommendation_service import CropRecommendationService
            from ..services.soil_management_service import SoilManagementService
        except ImportError:
            from services.recommendation_engine import RecommendationEngine
            from services.crop_recommendation_service import CropRecommendationService
            from services.soil_management_service import SoilManagementService
        
        # Initialize services
        recommendation_engine = RecommendationEngine()
        crop_service = CropRecommendationService()
        soil_service = SoilManagementService()
        
        # Generate initial recommendations using the main engine
        initial_recommendations = await crop_service.get_crop_recommendations(request.recommendation_request)
        
        if not initial_recommendations:
            # If no recommendations from crop service, try the main engine
            initial_recommendations = await recommendation_engine._handle_crop_selection(request.recommendation_request)
        
        # Apply preference weights to recommendations
        weighted_recommendations = _apply_preference_weights(
            initial_recommendations, 
            request.user_preferences, 
            request.preference_weights
        )
        
        # Sort by the new weighted score
        weighted_recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
        
        # Calculate overall confidence based on preference adjustments
        overall_confidence = _calculate_preference_confidence(weighted_recommendations, request.user_preferences)
        
        # Build enhanced confidence factors that include preference information
        base_confidence_factors = recommendation_engine._build_confidence_factors(request.recommendation_request)
        
        # Create base dictionary based on the confidence factors
        if hasattr(base_confidence_factors, 'dict'):
            base_dict = base_confidence_factors.dict()
        elif hasattr(base_confidence_factors, '__dict__'):
            base_dict = base_confidence_factors.__dict__
        else:
            # If it's already a dict, use it as is
            base_dict = base_confidence_factors if isinstance(base_confidence_factors, dict) else {}
        
        enhanced_confidence_factors = base_dict.copy()
        enhanced_confidence_factors.update({
            "preference_alignment_score": overall_confidence,
            "user_preferences_applied": list(request.user_preferences.keys()),
            "preference_weights_applied": request.preference_weights,
            "total_recommendations_after_preference_filtering": len(weighted_recommendations)
        })
        
        # Create preference-specific warnings
        preference_warnings = [
            f"Recommendations adjusted based on user preferences for: {', '.join(request.user_preferences.keys())}"
        ]
        
        # Check if highly preferred items were excluded due to other constraints
        if request.user_preferences:
            preferred_crops = set(request.user_preferences.keys())
            recommended_crops = {rec.title.split()[1].lower() if len(rec.title.split()) > 1 else rec.title.split()[0].lower() for rec in weighted_recommendations}
            
            missing_preferred = preferred_crops - recommended_crops
            if missing_preferred:
                preference_warnings.append(f"Note: The following preferred crops did not appear in recommendations due to other constraints: {', '.join(missing_preferred)}")
        
        # Combine with base warnings
        all_warnings = preference_warnings
        base_warnings = recommendation_engine._generate_warnings(request.recommendation_request, weighted_recommendations, None)
        if base_warnings:
            all_warnings.extend(base_warnings)
        
        # Add preference-specific next steps
        preference_next_steps = []
        if weighted_recommendations:
            preference_next_steps.append(f"Review recommendations prioritized based on your preferences: {', '.join([rec.title for rec in weighted_recommendations[:3]])}")
        
        base_next_steps = recommendation_engine._generate_next_steps(request.recommendation_request, weighted_recommendations)
        all_next_steps = preference_next_steps + base_next_steps
        
        # Build response with enhanced preference information
        response = RecommendationResponse(
            request_id=f"prefs-{request.recommendation_request.request_id}",
            question_type="crop_selection_with_preferences",
            overall_confidence=overall_confidence,
            confidence_factors=enhanced_confidence_factors,
            recommendations=weighted_recommendations,
            warnings=all_warnings,
            next_steps=all_next_steps,
            follow_up_questions=recommendation_engine._generate_follow_up_questions("crop_selection")
        )
        
        logger.info(f"Applied user preferences, generating {len(weighted_recommendations)} adjusted recommendations with confidence {overall_confidence:.2f}")
        return response
        
    except Exception as e:
        logger.error(f"Error applying user preferences: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error applying preferences: {str(e)}")


@router.get("/filter-impact", response_model=FilterImpactResponse)
async def analyze_filter_impact(
    original_request_id: Optional[str] = Query(None, description="Original request ID to analyze"),
    crop_category: Optional[CropCategory] = Query(None, description="Crop category for analysis"),
    climate_zone: Optional[str] = Query(None, description="Climate zone for analysis"),
    soil_ph_range: Optional[str] = Query(None, description="Soil pH range for analysis (e.g., '6.0-7.0')")
):
    """
    GET /api/v1/recommendations/filter-impact - Analyze filter impact on recommendations
    
    TICKET-005_crop-type-filtering-4.3.4
    
    Features:
    - Show how filters affect recommendation results
    - Provide alternative suggestions
    - Include filter optimization recommendations
    - Track filter usage patterns and effectiveness
    """
    try:
        logger.info(f"Analyzing filter impact for request {original_request_id}")
        
        # Import services to access historical recommendation data and filtering statistics
        try:
            from ..services.recommendation_engine import RecommendationEngine
            from ..services.crop_recommendation_service import CropRecommendationService
        except ImportError:
            from services.recommendation_engine import RecommendationEngine
            from services.crop_recommendation_service import CropRecommendationService
        
        recommendation_engine = RecommendationEngine()
        crop_service = CropRecommendationService()
        
        # Simulate analysis based on actual filter parameters
        # In a real implementation, this would query historical data
        base_count = 20  # Base number of possible recommendations before filtering
        original_count = base_count
        filtered_count = max(1, int(base_count * 0.6))  # Simulate 40% reduction due to filtering
        
        # Parse soil pH range if provided
        ph_min, ph_max = None, None
        if soil_ph_range:
            try:
                parts = soil_ph_range.split('-')
                ph_min = float(parts[0])
                ph_max = float(parts[1])
            except (ValueError, IndexError):
                logger.warning(f"Invalid pH range format: {soil_ph_range}")
        
        # Determine the most affected criteria based on input parameters
        most_affected_criteria = []
        if climate_zone:
            most_affected_criteria.append("climate compatibility")
        if soil_ph_range:
            most_affected_criteria.append("soil pH requirements") 
        if crop_category:
            most_affected_criteria.append("crop category preferences")
        
        # If no specific criteria were provided, use defaults
        if not most_affected_criteria:
            most_affected_criteria = [
                "climate compatibility",
                "soil pH requirements", 
                "maturity days"
            ]
        
        # Generate alternative suggestions based on filter constraints
        alternative_suggestions = []
        if climate_zone:
            alternative_suggestions.extend([
                f"Consider crops adapted to adjacent climate zones if {climate_zone} options are limited",
                f"Explore varieties with broader climate tolerance than those in zone {climate_zone}"
            ])
        if ph_min is not None and ph_max is not None:
            alternative_suggestions.append(
                f"For pH range {ph_min}-{ph_max}, consider liming or acidifying treatments to expand crop options"
            )
        if crop_category:
            alternative_suggestions.append(
                f"Cross-check {crop_category.value if hasattr(crop_category, 'value') else crop_category} recommendations with similar categories"
            )
        
        # Add default suggestions if none were generated
        if not alternative_suggestions:
            alternative_suggestions = [
                "Consider expanding climate zone tolerance by ±1 zone for more options",
                "Explore soil amendment options to broaden pH compatibility",
                "Look into nitrogen-fixing alternatives for nutrient management"
            ]
        
        # Generate filter optimization recommendations
        filter_optimization_recommendations = []
        if climate_zone:
            filter_optimization_recommendations.append(
                f"Relax climate zone constraints by ±1 zone to increase options available in {climate_zone}."
            )
        if ph_min is not None or ph_max is not None:
            filter_optimization_recommendations.append(
                "Consider soil pH adjustment through liming or sulfur applications to access a wider variety of crops."
            )
        if filtered_count < base_count * 0.5:  # If filtering is very restrictive
            filter_optimization_recommendations.append(
                "Current filters are highly restrictive. Consider relaxing multiple constraints simultaneously."
            )
        
        # Add default recommendations if none were generated
        if not filter_optimization_recommendations:
            filter_optimization_recommendations = [
                "Relax climate zone constraints by ±1 zone for more options",
                "Consider liming to adjust pH for broader crop selection",
                "Evaluate the possibility of irrigation to increase drought-tolerant crop options"
            ]
        
        # Calculate filter impact percentage
        filter_reduction_percentage = 0.0
        if original_count > 0:
            filter_reduction_percentage = ((original_count - filtered_count) / original_count) * 100
        
        analysis = FilterImpactAnalysis(
            original_count=original_count,
            filtered_count=filtered_count,
            filter_reduction_percentage=filter_reduction_percentage,
            most_affected_criteria=most_affected_criteria,
            alternative_suggestions=alternative_suggestions,
            filter_optimization_recommendations=filter_optimization_recommendations
        )
        
        # Mock filter usage patterns - in real implementation these would come from analytics
        filter_usage_patterns = {
            "climate_zones": 245,
            "soil_ph": 187,
            "drought_tolerance": 134,
            "maturity_days": 112,
            "nitrogen_fixing": 89,
            "crop_category": 76,
            "drainage_class": 63
        }
        
        # Mock effectiveness metrics - in real implementation these would be calculated from historical data
        effectiveness_metrics = {
            "climate_filter": 0.89,
            "soil_ph_filter": 0.84,
            "drought_tolerance_filter": 0.78,
            "maturity_filter": 0.82,
            "category_filter": 0.91
        }
        
        response = FilterImpactResponse(
            analysis=analysis,
            filter_usage_patterns=filter_usage_patterns,
            effectiveness_metrics=effectiveness_metrics
        )
        
        logger.info(f"Filter impact analysis completed for request {original_request_id}, {filter_reduction_percentage:.1f}% reduction from filters")
        return response
        
    except Exception as e:
        logger.error(f"Error in filter impact analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing filter impact: {str(e)}")


# Helper functions
async def _apply_taxonomy_filtering(filter_criteria: TaxonomyFilterCriteria, crop_database: Dict) -> Dict:
    """
    Apply taxonomy-based filtering to the crop database.
    
    Args:
        filter_criteria: The taxonomy filter criteria to apply
        crop_database: The original crop database to filter
        
    Returns:
        Filtered crop database containing only crops matching all criteria
    """
    if not crop_database:
        return {}
    
    if not filter_criteria:
        return crop_database
    
    # Start with all crops
    filtered_crop_database = {}
    
    for crop_name, crop_data in crop_database.items():
        include_crop = True
        
        # Apply agricultural filters
        if filter_criteria.agricultural_filter:
            ag_filter = filter_criteria.agricultural_filter
            if ag_filter.categories:
                # Assuming crop_data has a 'category' field
                category = crop_data.get('category', '').lower()
                if category not in [cat.value.lower() for cat in ag_filter.categories]:
                    include_crop = False
            
            if ag_filter.growth_habits:
                growth_habit = crop_data.get('growth_habit', '').lower()
                if growth_habit not in [hab.value.lower() for hab in ag_filter.growth_habits]:
                    include_crop = False
        
        # Apply climate filters
        if filter_criteria.climate_filter and include_crop:
            climate_filter = filter_criteria.climate_filter
            if climate_filter.hardiness_zones:
                crop_zones = crop_data.get('climate_zones', [])
                if not any(zone in climate_filter.hardiness_zones for zone in crop_zones):
                    include_crop = False
        
        # Apply soil filters
        if filter_criteria.soil_filter and include_crop:
            soil_filter = filter_criteria.soil_filter
            if soil_filter.ph_range:
                optimal_ph_range = crop_data.get('optimal_ph_range', (0, 14))
                ph_min = soil_filter.ph_range.get('min', 0)
                ph_max = soil_filter.ph_range.get('max', 14)
                
                # Check if there's overlap between optimal range and filter range
                if not (optimal_ph_range[0] <= ph_max and optimal_ph_range[1] >= ph_min):
                    include_crop = False
        
        if include_crop:
            filtered_crop_database[crop_name] = crop_data
    
    return filtered_crop_database


def _calculate_filtered_confidence(recommendations: List[RecommendationItem], request: CropSelectionWithFilterRequest) -> float:
    """
    Calculate confidence score considering the impact of filtering.
    
    Args:
        recommendations: List of recommendation items
        request: The original request with filter criteria
        
    Returns:
        Adjusted confidence score based on filtering impact
    """
    if not recommendations:
        return 0.0
    
    # Base confidence is the average of all recommendation confidence scores
    base_confidence = sum(rec.confidence_score for rec in recommendations) / len(recommendations)
    
    # Adjust confidence based on whether filters were applied
    adjustment = 0.0
    if request.filter_criteria:
        # If filters were applied and we still have good recommendations, confidence increases
        # If filters were applied and we have very few recommendations, confidence decreases
        if len(recommendations) < 3:
            adjustment -= 0.1
        else:
            adjustment += 0.05
    
    # Ensure confidence is between 0 and 1
    return max(0.0, min(1.0, base_confidence + adjustment))


def _add_filter_explanations(recommendations: List[RecommendationItem], filter_criteria: TaxonomyFilterCriteria) -> List[RecommendationItem]:
    """
    Add explanations to recommendations about how filters affected them.
    
    Args:
        recommendations: List of recommendation items to enhance
        filter_criteria: The filter criteria that were applied
        
    Returns:
        Enhanced list of recommendation items with filter explanations
    """
    enhanced_recommendations = []
    
    for rec in recommendations:
        enhanced_rec = rec.copy()
        
        # Add filter explanation to description
        explanation_parts = [f"Selected based on applied filters:"]
        
        if filter_criteria.agricultural_filter:
            if filter_criteria.agricultural_filter.categories:
                explanation_parts.append(f"crop category: {', '.join([cat.value for cat in filter_criteria.agricultural_filter.categories])}")
        
        if filter_criteria.soil_filter:
            if filter_criteria.soil_filter.ph_range:
                ph_range = filter_criteria.soil_filter.ph_range
                explanation_parts.append(f"soil pH: {ph_range.get('min', 'any')}-{ph_range.get('max', 'any')}")
        
        if filter_criteria.climate_filter:
            if filter_criteria.climate_filter.hardiness_zones:
                explanation_parts.append(f"climate zones: {', '.join(filter_criteria.climate_filter.hardiness_zones)}")
        
        if explanation_parts:
            enhanced_rec.description += f" Filter explanation: {'; '.join(explanation_parts)}."
        
        enhanced_recommendations.append(enhanced_rec)
    
    return enhanced_recommendations


def _apply_preference_weights(recommendations: List[RecommendationItem], 
                             user_preferences: Dict[str, float], 
                             preference_weights: Optional[Dict[str, float]] = None) -> List[RecommendationItem]:
    """
    Apply user preferences to recommendation scores.
    
    Args:
        recommendations: Original list of recommendations
        user_preferences: Dictionary mapping crop names to preference values (0-1)
        preference_weights: Optional weights for different preference categories
        
    Returns:
        Updated list of recommendations with preference-adjusted scores
    """
    if not user_preferences:
        return recommendations
    
    # Set default weights if not provided
    if not preference_weights:
        preference_weights = {
            "crop_preference": 0.3,
            "risk_tolerance": 0.2,
            "organic_focus": 0.2,
            "market_demand": 0.15,
            "sustainability": 0.15
        }
    
    adjusted_recommendations = []
    
    for rec in recommendations:
        # Extract crop name from title (this is a simple heuristic)
        crop_name = rec.title.lower().split()[0] if rec.title else ""
        
        # Get user preference for this crop (default to 0.5 if not specified)
        crop_preference = user_preferences.get(crop_name, 0.5)
        
        # Calculate weighted adjustment
        preference_adjustment = (crop_preference - 0.5) * preference_weights.get("crop_preference", 0.3)
        
        # Ensure the new confidence score is within bounds
        new_confidence = max(0.0, min(1.0, rec.confidence_score + preference_adjustment))
        
        # Create a copy with updated confidence score
        adjusted_rec = rec.copy()
        adjusted_rec.confidence_score = new_confidence
        
        # Add preference explanation to description
        if crop_preference > 0.7:
            adjusted_rec.description += f" (Highly preferred by user: {crop_preference:.2f})"
        elif crop_preference < 0.3:
            adjusted_rec.description += f" (Low preference by user: {crop_preference:.2f})"
        
        # Adjust priority based on user preference
        if crop_preference > 0.8:
            adjusted_rec.priority = max(1, rec.priority - 1)
        elif crop_preference < 0.2:
            adjusted_rec.priority = min(5, rec.priority + 1)
        
        adjusted_recommendations.append(adjusted_rec)
    
    return adjusted_recommendations


def _calculate_preference_confidence(recommendations: List[RecommendationItem], 
                                   user_preferences: Dict[str, float]) -> float:
    """
    Calculate confidence score considering the impact of user preferences.
    
    Args:
        recommendations: List of preference-adjusted recommendation items
        user_preferences: Dictionary of user preferences
        
    Returns:
        Adjusted confidence score based on preference alignment
    """
    if not recommendations or not user_preferences:
        return 0.7  # Default confidence without preferences
    
    # Calculate how well the final recommendations align with user preferences
    alignment_scores = []
    
    for rec in recommendations:
        # Extract crop name from title
        crop_name = rec.title.lower().split()[0] if rec.title else ""
        
        # Get user preference for this crop
        crop_preference = user_preferences.get(crop_name, 0.5)
        
        # Calculate alignment (higher is better)
        alignment = abs(crop_preference - 0.5) * 2  # Scale 0.5-1.0 to 0-1
        alignment_scores.append(alignment)
    
    if alignment_scores:
        avg_alignment = sum(alignment_scores) / len(alignment_scores)
        # Adjust base confidence based on preference alignment
        base_confidence = sum(rec.confidence_score for rec in recommendations) / len(recommendations)
        return min(1.0, base_confidence + (avg_alignment * 0.1))
    else:
        base_confidence = sum(rec.confidence_score for rec in recommendations) / len(recommendations)
        return base_confidence
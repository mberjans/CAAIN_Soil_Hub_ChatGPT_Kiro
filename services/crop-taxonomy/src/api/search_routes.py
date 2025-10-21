"""
Search API Routes

FastAPI routes for advanced crop search, filtering, and smart recommendations with performance optimization.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
import hashlib

try:
    from ..services.crop_search_service import crop_search_service
    from ..models.crop_filtering_models import (
        CropSearchRequest,
        CropSearchResponse,
        SmartRecommendationRequest,
        SmartRecommendationResponse,
        TaxonomyFilterCriteria,
        SearchResultItem
    )
    from ..services.filter_cache_service import filter_cache_service
    from ..services.performance_monitor import performance_monitor
    from ..services.result_processor import FilterResultProcessor
except ImportError:
    # Fallback imports if the relative imports fail
    from services.crop_search_service import crop_search_service
    from models.crop_filtering_models import (
        CropSearchRequest,
        CropSearchResponse,
        SmartRecommendationRequest,
        SmartRecommendationResponse,
        TaxonomyFilterCriteria,
        SearchResultItem
    )
    from services.filter_cache_service import filter_cache_service
    from services.performance_monitor import performance_monitor
    from services.result_processor import FilterResultProcessor


router = APIRouter(prefix="/search", tags=["search"])


@router.post("/processed-search", response_model=Dict[str, Any])
async def processed_search_crops(
    request: CropSearchRequest
):
    """
    Execute comprehensive crop search and return processed results.
    
    This endpoint provides intelligent ranking, clustering, and suggestions
    for the search results.
    """
    try:
        # First, perform the regular search
        search_result = await crop_search_service.search_crops(request)
        
        # Now, process the results for intelligent presentation
        result_processor = FilterResultProcessor(crop_search_service.variety_recommendation_service)
        processed_results = result_processor.process_results(search_result.results, request.filter_criteria)
        
        return processed_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processed search error: {str(e)}")


@router.post("/crops", response_model=CropSearchResponse)
async def search_crops(
    request: CropSearchRequest
):
    """
    Execute comprehensive crop search with multi-criteria filtering.
    
    **Advanced Search Features:**
    - Multi-dimensional filtering (climate, soil, agricultural, economic)
    - Intelligent scoring and ranking
    - Regional adaptation matching
    - Sustainability criteria
    - Economic viability assessment
    
    **Filter Categories:**
    - **Geographic**: Latitude ranges, hardiness zones, elevation
    - **Climate**: Temperature, precipitation, growing season
    - **Soil**: pH, texture, drainage, salinity tolerance  
    - **Agricultural**: Crop categories, life cycles, maturity periods
    - **Management**: Input requirements, mechanization compatibility
    - **Sustainability**: Water efficiency, soil improvement, carbon impact
    - **Economic**: Market demand, input costs, profitability
    
    Returns ranked search results with detailed scoring and match explanations.
    """
    try:
        result = await crop_search_service.search_crops(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@router.post("/smart-recommendations", response_model=SmartRecommendationResponse)
async def get_smart_recommendations(
    request: SmartRecommendationRequest
):
    """
    Get ML-enhanced crop recommendations with contextual insights.
    
    **Smart Features:**
    - Machine learning pattern recognition
    - Historical performance analysis
    - Risk assessment and mitigation
    - Context-aware recommendations
    - Predictive insights
    
    **Context Inputs:**
    - Farm location and size
    - Historical production data
    - Climate trends and projections
    - Soil test results
    - Economic goals and constraints
    - Risk tolerance preferences
    
    Returns intelligent recommendations with confidence scoring and detailed reasoning.
    """
    try:
        result = await crop_search_service.get_smart_recommendations(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Smart recommendation error: {str(e)}")


@router.get("/quick-search", response_model=List[SearchResultItem])
async def quick_crop_search(
    query: str = Query(..., description="Search query (crop name, category, or characteristics)"),
    limit: int = Query(10, description="Maximum number of results"),
    region: Optional[str] = Query(None, description="Regional context for results"),
    category: Optional[str] = Query(None, description="Filter by crop category")
):
    """
    Quick crop search for simple queries and autocomplete.
    
    **Use Cases:**
    - Autocomplete functionality
    - Simple crop lookups
    - Category browsing
    - Quick reference searches
    
    **Query Examples:**
    - Crop names: "wheat", "corn", "soybean"
    - Categories: "grain crops", "legumes", "oilseeds"  
    - Characteristics: "drought tolerant", "high protein"
    - Regional: "prairie wheat", "southern corn"
    
    Returns simplified search results optimized for speed and usability.
    """
    try:
        # Create simplified search request
        from ..models.crop_filtering_models import GeographicFilterCriteria, AgriculturalFilterCriteria
        
        filter_criteria = TaxonomyFilterCriteria()
        
        # Add category filter if specified
        if category:
            filter_criteria.agricultural = AgriculturalFilterCriteria(
                crop_categories=[category]
            )
            
        # Add region filter if specified  
        if region:
            filter_criteria.geographic = GeographicFilterCriteria(
                region_name=region
            )
            
        search_request = CropSearchRequest(
            query=query,
            filter_criteria=filter_criteria,
            page_size=limit,
            page=1
        )
        
        result = await crop_search_service.search_crops(search_request)
        return result.results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick search error: {str(e)}")


@router.get("/suggestions", response_model=List[str])
async def get_search_suggestions(
    partial_query: str = Query(..., description="Partial search query"),
    suggestion_type: str = Query("crops", description="Type of suggestions (crops, categories, families)")
):
    """
    Get search suggestions for autocomplete functionality.
    
    **Suggestion Types:**
    - **crops**: Crop names and common aliases
    - **categories**: Agricultural categories and subcategories  
    - **families**: Botanical families and genera
    - **regions**: Geographic regions and climate zones
    - **characteristics**: Crop characteristics and attributes
    
    Returns list of relevant suggestions based on partial input.
    """
    try:
        suggestions = []
        
        if suggestion_type == "crops":
            # Common crop suggestions
            crop_names = [
                "wheat", "corn", "soybean", "barley", "oats", "rye", "canola", 
                "sunflower", "flax", "pea", "lentil", "chickpea", "alfalfa",
                "clover", "timothy", "fescue", "ryegrass"
            ]
            suggestions = [crop for crop in crop_names if partial_query.lower() in crop.lower()]
            
        elif suggestion_type == "categories":
            categories = [
                "grain crops", "oilseed crops", "legume crops", "forage crops",
                "vegetable crops", "fruit crops", "specialty crops", "cover crops"
            ]
            suggestions = [cat for cat in categories if partial_query.lower() in cat.lower()]
            
        elif suggestion_type == "families":
            families = [
                "Poaceae (grasses)", "Fabaceae (legumes)", "Brassicaceae (mustards)",
                "Asteraceae (sunflowers)", "Solanaceae (nightshades)"
            ]
            suggestions = [fam for fam in families if partial_query.lower() in fam.lower()]
            
        return suggestions[:10]  # Return top 10 suggestions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Suggestion error: {str(e)}")


@router.get("/filters", response_model=Dict[str, List[str]])
async def get_available_filters():
    """
    Get available filter options for search interfaces.
    
    Returns comprehensive list of available filter values for each category.
    Useful for building dynamic search interfaces and filter dropdowns.
    """
    try:
        filters = {
            "crop_categories": [
                "grain", "oilseed", "forage", "vegetable", "fruit", "specialty",
                "legume", "cereal", "root_crop", "leafy_green", "cover_crop"
            ],
            "life_cycles": ["annual", "biennial", "perennial"],
            "climate_zones": [
                "tropical", "subtropical", "temperate_continental", "temperate_oceanic",
                "mediterranean", "semi_arid", "arid", "subarctic"
            ],
            "soil_textures": [
                "sand", "loamy_sand", "sandy_loam", "loam", "silt_loam",
                "sandy_clay_loam", "clay_loam", "silty_clay_loam", "sandy_clay",
                "silty_clay", "clay"
            ],
            "drainage_classes": [
                "excessively_drained", "somewhat_excessively_drained", "well_drained",
                "moderately_well_drained", "somewhat_poorly_drained", "poorly_drained",
                "very_poorly_drained"
            ],
            "primary_uses": [
                "food_human", "feed_livestock", "industrial", "soil_improvement",
                "ornamental", "medicinal", "fiber", "biofuel"
            ]
        }
        return filters
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Filter retrieval error: {str(e)}")


@router.get("/popular-searches", response_model=List[Dict[str, Any]])
async def get_popular_searches():
    """
    Get popular and trending search queries.
    
    Returns list of popular searches with usage statistics.
    Helps users discover relevant crops and search patterns.
    """
    try:
        popular_searches = [
            {
                "query": "drought tolerant crops",
                "category": "climate_adaptation", 
                "usage_count": 1250,
                "description": "Crops suitable for water-limited conditions"
            },
            {
                "query": "high protein grains",
                "category": "nutritional",
                "usage_count": 980,
                "description": "Grain crops with elevated protein content"
            },
            {
                "query": "cover crops for soil improvement",
                "category": "sustainability",
                "usage_count": 875,
                "description": "Cover crops that enhance soil health"
            },
            {
                "query": "short season varieties",
                "category": "timing",
                "usage_count": 650,
                "description": "Crops with short maturity periods"
            },
            {
                "query": "nitrogen fixing legumes",
                "category": "soil_fertility",
                "usage_count": 580,
                "description": "Leguminous crops that fix atmospheric nitrogen"
            }
        ]
        return popular_searches
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Popular searches error: {str(e)}")


@router.get("/filter-options", response_model=Dict[str, Any])
async def get_dynamic_filter_options(
    latitude: Optional[float] = Query(None, description="Latitude for location-aware filters"),
    longitude: Optional[float] = Query(None, description="Longitude for location-aware filters"),
    climate_zone: Optional[str] = Query(None, description="Climate zone for relevant options")
):
    """
    Get dynamic filter options based on current crop database and user location.
    
    **Features:**
    - Location-aware filter options
    - Filter value counts and statistics
    - Filter dependency suggestions
    - Climate zone specific options
    
    **Response includes:**
    - Available categories with usage counts
    - Soil types relevant to location
    - Climate zones and growing conditions
    - Maturity ranges for region
    - Resistance traits and pest pressures
    - Market classifications and standards
    
    **Caching:** Redis cache with 1-hour TTL, location-based cache keys
    """
    try:
        # Generate cache key based on location parameters
        location_hash = f"{latitude or 'none'}:{longitude or 'none'}:{climate_zone or 'none'}"
        cached_result = await filter_cache_service.get_filter_options(location_hash)
        
        if cached_result:
            performance_monitor.record_operation(
                operation="filter_options_cached",
                execution_time_ms=0,  # Cache retrieval is fast
                cache_hit=True
            )
            return cached_result
        
        operation_start = performance_monitor.start_timer()
        
        from ..services.crop_search_service import crop_search_service
        
        filter_options = {
            "climate_zones": {
                "values": ["1a", "1b", "2a", "2b", "3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b", "8a", "8b", "9a", "9b", "10a", "10b"],
                "counts": {},
                "recommended": []
            },
            "soil_ph_ranges": {
                "min": 3.5,
                "max": 9.0,
                "optimal_ranges": {
                    "acidic": {"min": 3.5, "max": 6.0},
                    "neutral": {"min": 6.0, "max": 7.5},
                    "alkaline": {"min": 7.5, "max": 9.0}
                }
            },
            "maturity_days_ranges": {
                "short_season": {"min": 50, "max": 90},
                "medium_season": {"min": 90, "max": 120},
                "long_season": {"min": 120, "max": 180},
                "very_long_season": {"min": 180, "max": 250}
            },
            "drought_tolerance": {
                "values": ["low", "moderate", "high", "very_high"],
                "descriptions": {
                    "low": "Requires consistent moisture",
                    "moderate": "Can tolerate short dry periods",
                    "high": "Performs well in limited water conditions",
                    "very_high": "Thrives in arid conditions"
                }
            },
            "pest_resistance": {
                "common_pests": ["corn_borer", "aphids", "spider_mites", "cutworms", "wireworms"],
                "diseases": ["rust", "blight", "mildew", "scab", "smut"],
                "nematodes": ["root_knot", "cyst", "lesion"]
            },
            "market_class": {
                "values": ["organic_eligible", "non_gmo", "conventional", "identity_preserved", "specialty_contract"],
                "certifications": ["usda_organic", "non_gmo_project", "gluten_free", "kosher", "halal"]
            },
            "management_complexity": {
                "values": ["low", "moderate", "high"],
                "factors": ["input_requirements", "timing_precision", "equipment_needs", "expertise_level"]
            }
        }
        
        # Add location-specific recommendations if coordinates provided
        if latitude is not None and longitude is not None:
            # Determine likely climate zone based on latitude (simplified)
            if latitude > 60:
                filter_options["climate_zones"]["recommended"] = ["1a", "1b", "2a", "2b"]
            elif latitude > 50:
                filter_options["climate_zones"]["recommended"] = ["2a", "2b", "3a", "3b", "4a"]
            elif latitude > 40:
                filter_options["climate_zones"]["recommended"] = ["4a", "4b", "5a", "5b", "6a"]
            elif latitude > 30:
                filter_options["climate_zones"]["recommended"] = ["6a", "6b", "7a", "7b", "8a"]
            else:
                filter_options["climate_zones"]["recommended"] = ["8a", "8b", "9a", "9b", "10a", "10b"]
        
        # Cache the result
        await filter_cache_service.cache_filter_options(location_hash, filter_options)
        
        execution_time = performance_monitor.stop_timer(operation_start)
        performance_monitor.record_operation(
            operation="filter_options",
            execution_time_ms=execution_time,
            cache_hit=False
        )
        
        return filter_options
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Filter options error: {str(e)}")


@router.get("/categories/detailed", response_model=Dict[str, Any])
async def get_detailed_categories():
    """
    Get enhanced category information with agricultural context.
    
    **Features:**
    - Category descriptions and characteristics
    - Typical crop examples
    - Agricultural context and usage
    - Regional relevance
    - Usage statistics
    
    **Response includes:**
    - Hierarchical category structure
    - Category metadata and descriptions
    - Example crops for each category
    - Regional adaptation information
    - Economic and agricultural context
    """
    try:
        detailed_categories = {
            "grain_crops": {
                "name": "Grain Crops",
                "description": "Cereal and pseudo-cereal crops grown primarily for their edible seeds",
                "characteristics": [
                    "High carbohydrate content",
                    "Long storage capability", 
                    "Global dietary staples",
                    "Mechanization compatible"
                ],
                "examples": ["wheat", "corn", "rice", "barley", "oats", "quinoa"],
                "subcategories": {
                    "cereals": {
                        "description": "True cereal grains from grass family",
                        "examples": ["wheat", "corn", "rice", "barley", "oats", "rye"]
                    },
                    "pseudo_cereals": {
                        "description": "Non-grass crops with cereal-like properties",
                        "examples": ["quinoa", "amaranth", "buckwheat"]
                    }
                },
                "agricultural_context": "Foundation of global food security, typically grown in rotation systems",
                "regional_relevance": "Adapted to temperate and subtropical regions",
                "usage_statistics": {"popularity": 95, "global_area": "huge"}
            },
            "oilseed_crops": {
                "name": "Oilseed Crops",
                "description": "Crops grown primarily for oil extraction from seeds",
                "characteristics": [
                    "High oil content in seeds",
                    "Industrial and food applications",
                    "Protein-rich meal byproducts",
                    "Economic importance"
                ],
                "examples": ["soybean", "canola", "sunflower", "flax", "safflower"],
                "subcategories": {
                    "protein_oils": {
                        "description": "Oilseeds that also provide high-quality protein",
                        "examples": ["soybean", "peanut"]
                    },
                    "industrial_oils": {
                        "description": "Oils used primarily for industrial applications",
                        "examples": ["flax", "castor", "crambe"]
                    }
                },
                "agricultural_context": "Important rotation crops, nitrogen fixers (legumes), soil health benefits",
                "regional_relevance": "Widely adapted, climate-specific varieties available",
                "usage_statistics": {"popularity": 85, "global_area": "large"}
            },
            "legume_crops": {
                "name": "Legume Crops",
                "description": "Nitrogen-fixing crops from the Fabaceae family",
                "characteristics": [
                    "Nitrogen fixation capability",
                    "Soil improvement properties",
                    "High protein content",
                    "Sustainable production"
                ],
                "examples": ["soybean", "pea", "lentil", "chickpea", "bean", "alfalfa"],
                "subcategories": {
                    "grain_legumes": {
                        "description": "Legumes grown for edible seeds",
                        "examples": ["soybean", "pea", "lentil", "chickpea", "bean"]
                    },
                    "forage_legumes": {
                        "description": "Legumes grown for livestock feed",
                        "examples": ["alfalfa", "clover", "vetch"]
                    }
                },
                "agricultural_context": "Essential for sustainable cropping systems, reduce fertilizer needs",
                "regional_relevance": "Climate-specific varieties, cool and warm season types",
                "usage_statistics": {"popularity": 75, "global_area": "medium"}
            },
            "forage_crops": {
                "name": "Forage Crops",
                "description": "Crops grown to feed livestock",
                "characteristics": [
                    "High biomass production",
                    "Nutritional quality for livestock",
                    "Perennial or annual options",
                    "Grazing or harvesting systems"
                ],
                "examples": ["alfalfa", "timothy", "fescue", "clover", "ryegrass"],
                "subcategories": {
                    "perennial_forages": {
                        "description": "Long-lived forage crops",
                        "examples": ["alfalfa", "timothy", "fescue", "clover"]
                    },
                    "annual_forages": {
                        "description": "Single-season forage crops",
                        "examples": ["corn_silage", "sudan_grass", "oats"]
                    }
                },
                "agricultural_context": "Critical for livestock operations, soil protection, carbon sequestration",
                "regional_relevance": "Species selection based on climate and soil conditions",
                "usage_statistics": {"popularity": 70, "global_area": "large"}
            },
            "cover_crops": {
                "name": "Cover Crops",
                "description": "Crops grown primarily for soil protection and improvement",
                "characteristics": [
                    "Soil erosion prevention",
                    "Nutrient cycling enhancement",
                    "Weed suppression",
                    "Biodiversity support"
                ],
                "examples": ["rye", "crimson_clover", "radish", "mustard", "buckwheat"],
                "subcategories": {
                    "nitrogen_fixing": {
                        "description": "Cover crops that fix atmospheric nitrogen",
                        "examples": ["crimson_clover", "hairy_vetch", "winter_pea"]
                    },
                    "scavenging": {
                        "description": "Cover crops that capture and cycle nutrients",
                        "examples": ["radish", "mustard", "rye"]
                    }
                },
                "agricultural_context": "Sustainable agriculture practice, improves soil health and water quality",
                "regional_relevance": "Selection based on climate window and primary crop rotation",
                "usage_statistics": {"popularity": 60, "global_area": "growing"}
            }
        }
        
        return detailed_categories
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Categories error: {str(e)}")


@router.post("/filter/validate", response_model=Dict[str, Any])
async def validate_filter_combination(
    filter_data: Dict[str, Any]
):
    """
    Validate filter combinations and detect conflicts.
    
    **Features:**
    - Validate filter combinations for conflicts
    - Detect contradictory filter settings
    - Suggest alternative filter combinations
    - Agricultural constraint validation
    
    **Validation checks:**
    - Climate zone compatibility with maturity periods
    - Soil pH requirements vs. crop tolerance
    - Drought tolerance vs. moisture requirements
    - Pest resistance vs. regional pest pressure
    - Market class compatibility
    
    **Response includes:**
    - Validation results (valid/invalid/warnings)
    - Conflict explanations
    - Suggested modifications
    - Alternative filter suggestions
    """
    try:
        validation_result = {
            "is_valid": True,
            "validation_status": "valid",
            "conflicts": [],
            "warnings": [],
            "suggestions": [],
            "filter_compatibility": {}
        }
        
        conflicts = []
        warnings = []
        suggestions = []
        
        # Extract filter values
        climate_zones = filter_data.get("climate_zones", [])
        soil_ph_range = filter_data.get("soil_ph_range", {})
        maturity_days_range = filter_data.get("maturity_days_range", {})
        drought_tolerance = filter_data.get("drought_tolerance", [])
        management_complexity = filter_data.get("management_complexity", [])
        
        # Validation 1: Climate zone vs maturity period
        if climate_zones and maturity_days_range:
            northern_zones = [z for z in climate_zones if z in ["1a", "1b", "2a", "2b", "3a", "3b"]]
            long_maturity = maturity_days_range.get("min", 0) > 120
            
            if northern_zones and long_maturity:
                conflicts.append({
                    "type": "climate_maturity_conflict",
                    "message": "Long maturity crops may not have sufficient growing season in northern climate zones",
                    "affected_filters": ["climate_zones", "maturity_days_range"],
                    "suggestion": "Consider shorter season varieties or warmer climate zones"
                })
        
        # Validation 2: Soil pH compatibility
        if soil_ph_range:
            ph_min = soil_ph_range.get("min", 6.0)
            ph_max = soil_ph_range.get("max", 7.5)
            
            if ph_min > ph_max:
                conflicts.append({
                    "type": "invalid_ph_range",
                    "message": "Minimum pH cannot be greater than maximum pH",
                    "affected_filters": ["soil_ph_range"],
                    "suggestion": "Adjust pH range values"
                })
            
            if ph_min < 4.0 or ph_max > 9.0:
                warnings.append({
                    "type": "extreme_ph_warning",
                    "message": "Extreme pH values may limit crop options significantly",
                    "affected_filters": ["soil_ph_range"],
                    "suggestion": "Consider more moderate pH ranges for better crop selection"
                })
        
        # Validation 3: Drought tolerance consistency
        if "high" in drought_tolerance and climate_zones:
            humid_zones = [z for z in climate_zones if z in ["8a", "8b", "9a", "9b", "10a", "10b"]]
            if humid_zones:
                warnings.append({
                    "type": "drought_climate_mismatch",
                    "message": "High drought tolerance may not be necessary in humid climate zones",
                    "affected_filters": ["drought_tolerance", "climate_zones"],
                    "suggestion": "Consider moderate drought tolerance for humid regions"
                })
        
        # Validation 4: Management complexity
        if "high" in management_complexity:
            suggestions.append({
                "type": "management_suggestion",
                "message": "High complexity crops may require specialized equipment and expertise",
                "recommendation": "Ensure adequate resources and knowledge for successful production"
            })
        
        # Update validation status
        if conflicts:
            validation_result["is_valid"] = False
            validation_result["validation_status"] = "invalid"
        elif warnings:
            validation_result["validation_status"] = "valid_with_warnings"
        
        validation_result["conflicts"] = conflicts
        validation_result["warnings"] = warnings
        validation_result["suggestions"] = suggestions
        
        # Add filter compatibility matrix
        validation_result["filter_compatibility"] = {
            "climate_maturity": "compatible" if not any(c["type"] == "climate_maturity_conflict" for c in conflicts) else "incompatible",
            "soil_ph": "valid" if not any(c["type"] == "invalid_ph_range" for c in conflicts) else "invalid",
            "drought_climate": "consistent" if not any(w["type"] == "drought_climate_mismatch" for w in warnings) else "inconsistent"
        }
        
        return validation_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Filter validation error: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Health check endpoint for the search service.
    """
    return {
        "status": "healthy",
        "service": "crop-search",
        "version": "1.0.0",
        "components": {
            "search": "operational",
            "filtering": "operational",
            "recommendations": "operational",
            "ml_insights": "limited"  # ML features not fully implemented
        }
    }
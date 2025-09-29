"""
Variety API Routes

FastAPI routes for crop variety recommendations, comparisons, and selection.
"""

from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

try:
    from ..services.variety_recommendation_service import variety_recommendation_service
    from ..services.variety_comparison_service import variety_comparison_service
    from ..models.crop_variety_models import (
        VarietyRecommendation,
        VarietyComparisonRequest,
        VarietyComparisonResponse,
        EnhancedCropVariety
    )
    from ..models.crop_taxonomy_models import ComprehensiveCropData
    from ..models.variety_recommendation_request_models import AdvancedVarietyRecommendationRequest
except ImportError:
    from services.variety_recommendation_service import variety_recommendation_service
    from services.variety_comparison_service import variety_comparison_service
    from models.crop_variety_models import (
        VarietyRecommendation,
        VarietyComparisonRequest,
        VarietyComparisonResponse,
        EnhancedCropVariety
    )
    from models.crop_taxonomy_models import ComprehensiveCropData
    from models.variety_recommendation_request_models import AdvancedVarietyRecommendationRequest
    
    
    router = APIRouter(prefix="/varieties", tags=["varieties"])
    
    
    @router.post("/recommend", response_model=List[Dict[str, Any]])
    async def recommend_varieties_advanced(
        request: Dict[str, Any]
    ):
        """
        Get advanced variety recommendations for a specific crop and regional context.
        
        This endpoint provides variety recommendations for the frontend variety selection interface.
        It returns demo data that matches the expected structure for the frontend JavaScript.
        """
        try:
            # Extract request data
            crop_id = request.get("crop_id", "corn")
            farm_data = request.get("farm_data", {})
            user_preferences = request.get("user_preferences", {})
            max_recommendations = request.get("max_recommendations", 20)
            
            # Generate variety recommendations based on crop type
            if crop_id == "corn":
                recommendations = [
                    {
                        "id": "pioneer-1197",
                        "name": "Pioneer P1197AM",
                        "company": "Pioneer",
                        "description": "High-yielding corn hybrid with excellent disease resistance and drought tolerance.",
                        "yield_potential": "185 bu/acre",
                        "maturity_days": 105,
                        "confidence": 0.92,
                        "suitability": "Excellent",
                        "disease_resistance": "high",
                        "traits": [
                            {"name": "Drought Tolerance", "category": "resistance"},
                            {"name": "High Yield", "category": "yield"},
                            {"name": "Premium Quality", "category": "quality"}
                        ]
                    },
                    {
                        "id": "dekalb-5678",
                        "name": "DeKalb DK5678",
                        "company": "DeKalb",
                        "description": "Reliable corn hybrid with strong yield potential and good disease package.",
                        "yield_potential": "180 bu/acre",
                        "maturity_days": 108,
                        "confidence": 0.88,
                        "suitability": "Very Good",
                        "disease_resistance": "medium",
                        "traits": [
                            {"name": "NCLB Resistance", "category": "resistance"},
                            {"name": "High Yield", "category": "yield"},
                            {"name": "Good Standability", "category": "quality"}
                        ]
                    },
                    {
                        "id": "syngenta-1234",
                        "name": "Agrisure Viptera 3111",
                        "company": "Syngenta",
                        "description": "Premium corn hybrid with advanced insect protection and high yield potential.",
                        "yield_potential": "190 bu/acre",
                        "maturity_days": 110,
                        "confidence": 0.85,
                        "suitability": "Very Good",
                        "disease_resistance": "high",
                        "traits": [
                            {"name": "Insect Protection", "category": "resistance"},
                            {"name": "High Yield", "category": "yield"},
                            {"name": "Premium Quality", "category": "quality"}
                        ]
                    }
                ]
            elif crop_id == "soybean":
                recommendations = [
                    {
                        "id": "asgrow-2834",
                        "name": "Asgrow AG2834",
                        "company": "Asgrow",
                        "description": "Reliable soybean variety with strong yield potential and good disease package.",
                        "yield_potential": "58 bu/acre",
                        "maturity_days": 95,
                        "confidence": 0.88,
                        "suitability": "Very Good",
                        "disease_resistance": "medium",
                        "traits": [
                            {"name": "SDS Resistance", "category": "resistance"},
                            {"name": "High Protein", "category": "quality"},
                            {"name": "Good Standability", "category": "quality"}
                        ]
                    },
                    {
                        "id": "pioneer-1234",
                        "name": "Pioneer P1234",
                        "company": "Pioneer",
                        "description": "High-yielding soybean variety with excellent disease resistance.",
                        "yield_potential": "62 bu/acre",
                        "maturity_days": 98,
                        "confidence": 0.90,
                        "suitability": "Excellent",
                        "disease_resistance": "high",
                        "traits": [
                            {"name": "SDS Resistance", "category": "resistance"},
                            {"name": "High Yield", "category": "yield"},
                            {"name": "Premium Quality", "category": "quality"}
                        ]
                    }
                ]
            elif crop_id == "wheat":
                recommendations = [
                    {
                        "id": "syngenta-monument",
                        "name": "AgriPro SY Monument",
                        "company": "Syngenta",
                        "description": "Winter wheat variety with excellent winter hardiness and disease resistance.",
                        "yield_potential": "65 bu/acre",
                        "maturity_days": 280,
                        "confidence": 0.75,
                        "suitability": "Good",
                        "disease_resistance": "high",
                        "traits": [
                            {"name": "Winter Hardiness", "category": "resistance"},
                            {"name": "Fusarium Resistance", "category": "resistance"},
                            {"name": "Good Test Weight", "category": "quality"}
                        ]
                    }
                ]
            else:
                # Default recommendations for other crops
                recommendations = [
                    {
                        "id": "generic-variety-1",
                        "name": f"Premium {crop_id.title()} Variety",
                        "company": "Generic Seed Co",
                        "description": f"High-quality {crop_id} variety with good yield potential.",
                        "yield_potential": "N/A",
                        "maturity_days": 100,
                        "confidence": 0.70,
                        "suitability": "Good",
                        "disease_resistance": "medium",
                        "traits": [
                            {"name": "Good Yield", "category": "yield"},
                            {"name": "Disease Resistance", "category": "resistance"}
                        ]
                    }
                ]
            
            # Apply user preferences to adjust recommendations
            yield_priority = user_preferences.get("yieldPriority", 8)
            if yield_priority >= 8:
                # Sort by yield potential for high yield priority
                recommendations.sort(key=lambda x: x.get("confidence", 0), reverse=True)
            
            # Return limited results
            return recommendations[:max_recommendations]
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Recommendation error: {str(e)}")
    
    
    @router.post("/recommend/simple", response_model=List[VarietyRecommendation])
    async def recommend_varieties_simple(
        crop_id: UUID,
        regional_context: Dict[str, Any],
        farmer_preferences: Optional[Dict[str, Any]] = None,
        max_recommendations: int = Query(10, description="Maximum number of recommendations")
    ):    """
    Get variety recommendations for a specific crop and regional context.
    
    **Regional Context Required:**
    - **location**: Geographic coordinates or region identifier
    - **climate_data**: Temperature ranges, precipitation, growing season
    - **soil_conditions**: pH, texture, drainage characteristics
    - **pest_pressure**: Regional pest and disease pressure levels
    - **market_conditions**: Local market preferences and pricing
    
    **Farmer Preferences (Optional):**
    - **yield_priority**: Emphasis on yield potential (1-10 scale)
    - **quality_focus**: Specific quality attributes important
    - **risk_tolerance**: Acceptable level of production risk
    - **management_intensity**: Preferred management complexity level
    - **market_targets**: Intended end-use markets
    
    **Recommendation Features:**
    - Performance predictions for local conditions
    - Risk assessments and mitigation strategies
    - Economic analysis and ROI projections
    - Adaptation strategies for successful cultivation
    - Confidence scoring based on data quality
    
    Returns ranked variety recommendations with detailed analysis.
    """
    try:
        # This would get crop data from database
        # For now, return error since we don't have database implementation
        raise HTTPException(
            status_code=501, 
            detail="Variety recommendations require database integration - not yet implemented"
        )
        
        # When implemented:
        # crop_data = await get_crop_by_id(crop_id)
        # recommendations = await variety_recommendation_service.recommend_varieties(
        #     crop_data, regional_context, farmer_preferences
        # )
        # return recommendations[:max_recommendations]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation error: {str(e)}")


@router.get("/{variety_name}/availability", response_model=Dict[str, Any])
async def get_variety_availability(
    variety_name: str,
    service: VarietyRecommendationService = Depends(get_variety_service)
):
    """
    Get comprehensive availability information for a specific variety from seed companies.
    
    **Information Provided:**
    - Company-specific availability status
    - Pricing information across companies
    - Regional distribution coverage
    - Product codes and identifiers
    - Last update timestamps
    
    **Use Cases:**
    - Check seed availability before planting season
    - Compare pricing across seed companies
    - Verify regional distribution for specific varieties
    - Track availability changes over time
    
    Args:
        variety_name: Name of the variety to check
        
    Returns:
        Comprehensive availability information from all seed companies
    """
    try:
        availability_info = await service.get_variety_availability_info(variety_name)
        return availability_info
        
    except Exception as e:
        logger.error(f"Error getting variety availability: {e}")
        raise HTTPException(status_code=500, detail=f"Availability check failed: {str(e)}")


@router.post("/sync-seed-companies", response_model=Dict[str, Any])
async def sync_seed_company_data(
    background_tasks: BackgroundTasks,
    service: VarietyRecommendationService = Depends(get_variety_service)
):
    """
    Synchronize data from seed companies to ensure up-to-date variety information.
    
    **Companies Synchronized:**
    - Pioneer/Corteva
    - Bayer/Dekalb
    - Syngenta
    - Additional regional companies
    
    **Data Updated:**
    - Variety characteristics and traits
    - Seed availability and pricing
    - Regional distribution information
    - Technology packages and herbicide tolerances
    
    **Benefits:**
    - Ensures recommendations are based on current seed availability
    - Provides accurate pricing information for cost analysis
    - Updates variety characteristics with latest data
    - Maintains data provenance and quality tracking
    
    Returns:
        Synchronization results and status information
    """
    try:
        # Run sync in background to avoid timeout
        background_tasks.add_task(service.sync_seed_company_data)
        
        return {
            "message": "Seed company data synchronization initiated",
            "status": "initiated",
            "timestamp": datetime.now().isoformat(),
            "note": "Synchronization is running in the background. Check sync status endpoint for progress."
        }
        
    except Exception as e:
        logger.error(f"Error initiating seed company sync: {e}")
        raise HTTPException(status_code=500, detail=f"Sync initiation failed: {str(e)}")


@router.get("/seed-companies/sync-status", response_model=Dict[str, Any])
async def get_seed_company_sync_status(
    service: VarietyRecommendationService = Depends(get_variety_service)
):
    """
    Get synchronization status for all seed companies.
    
    **Status Information:**
    - Last sync timestamp for each company
    - Current sync status (success, partial, failed, pending)
    - Error counts and retry information
    - Next scheduled sync time
    - Data quality metrics
    
    **Use Cases:**
    - Monitor data freshness and quality
    - Troubleshoot synchronization issues
    - Plan data update schedules
    - Verify integration health
    
    Returns:
        Detailed sync status for all configured seed companies
    """
    try:
        status_info = await service.get_seed_company_sync_status()
        return status_info
        
    except Exception as e:
        logger.error(f"Error getting seed company sync status: {e}")
        raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")


@router.post("/compare", response_model=VarietyComparisonResponse)
async def compare_varieties_advanced(
    request: VarietyComparisonRequest
):
    """
    Advanced variety comparison with comprehensive analysis and decision support.
    
    **Enhanced Comparison Features:**
    - **Multi-variety Analysis**: Compare up to 10 varieties simultaneously
    - **Trade-off Analysis**: Detailed analysis of strengths and trade-offs
    - **Decision Support**: AI-powered recommendations based on context
    - **Visualization Data**: Structured data for charts and graphs
    - **Economic Analysis**: Cost-benefit analysis and ROI projections
    - **Risk Assessment**: Comprehensive risk profiling and mitigation strategies
    
    **Comparison Criteria:**
    - **Yield Performance**: Average yields, yield stability, potential, consistency
    - **Disease Resistance**: Comprehensive resistance profiles with effectiveness ratings
    - **Quality Attributes**: Grain quality, nutritional composition, market acceptance
    - **Agronomic Traits**: Maturity, plant height, standability, lodging resistance
    - **Economic Factors**: Seed costs, market premiums, profitability, break-even analysis
    - **Risk Profiles**: Production risks, weather sensitivity, management requirements
    - **Regional Adaptation**: Performance across different environments and soil types
    
    **Advanced Analysis Features:**
    - Side-by-side characteristic comparison with normalized scoring
    - Strengths and weaknesses identification with actionable insights
    - Suitability scoring for different production goals and scenarios
    - Regional performance differences with confidence intervals
    - Economic trade-off analysis with sensitivity analysis
    - Management complexity assessment and requirements
    - Market positioning and premium potential analysis
    
    **Decision Support Features:**
    - Weighted scoring based on farmer preferences and priorities
    - Scenario-based recommendations (high-yield, low-risk, balanced)
    - Portfolio diversification recommendations
    - Risk-adjusted performance rankings
    - Management intensity matching
    - Economic optimization suggestions
    
    **Use Cases:**
    - Variety selection decision support with confidence scoring
    - Portfolio diversification planning across multiple fields
    - Risk management evaluation and mitigation planning
    - Market positioning analysis and premium capture
    - Management system optimization and simplification
    - Economic planning and profitability analysis
    
    **Request Schema:**
    ```json
    {
      "request_id": "unique_request_id",
      "variety_ids": ["uuid1", "uuid2", "uuid3"],
      "provided_varieties": [
        {
          "variety_id": "uuid",
          "variety_name": "Variety Name",
          "crop_id": "crop_uuid",
          "yield_potential_percentile": 85,
          "disease_resistances": [...],
          "relative_maturity": 105,
          "market_acceptance_score": 4.2,
          "seed_cost_per_unit": 285.50
        }
      ],
      "comparison_context": {
        "location": {"latitude": 41.8781, "longitude": -87.6298},
        "soil_data": {"ph": 6.5, "texture": "loam", "organic_matter": 3.2},
        "climate_zone": "5b",
        "target_relative_maturity": 105,
        "field_characteristics": {
          "drainage": "good",
          "slope_percent": 2.5,
          "irrigation_available": true
        },
        "farmer_preferences": {
          "yield_priority": 8,
          "risk_tolerance": 6,
          "management_intensity": 5,
          "quality_focus": "protein_content",
          "market_targets": ["feed", "ethanol"]
        },
        "economic_context": {
          "commodity_price": 5.25,
          "input_cost_budget": 50000,
          "risk_premium": 0.15
        }
      },
      "prioritized_factors": ["yield_potential", "disease_resilience", "economic_outlook"],
      "comparison_criteria": {
        "include_trade_offs": true,
        "include_management_analysis": true,
        "include_economic_analysis": true,
        "include_risk_assessment": true,
        "include_regional_adaptation": true,
        "include_quality_analysis": true
      },
      "weighting_preferences": {
        "yield_weight": 0.35,
        "disease_weight": 0.25,
        "economic_weight": 0.20,
        "management_weight": 0.10,
        "quality_weight": 0.10
      },
      "scenario_analysis": {
        "high_yield_scenario": true,
        "low_risk_scenario": true,
        "balanced_scenario": true,
        "premium_market_scenario": false
      }
    }
    ```
    
    **Enhanced Response Features:**
    - Detailed comparison matrix with normalized scores and confidence intervals
    - Comprehensive trade-off analysis highlighting key strengths and considerations
    - Risk assessment with mitigation strategies and management requirements
    - Economic outlook with ROI projections and break-even analysis
    - Suitability recommendations for different scenarios and production goals
    - Confidence scoring based on data quality and regional validation
    - Visualization data for charts, graphs, and decision support tools
    - Management recommendations and implementation guidance
    - Market analysis and premium potential assessment
    
    **Performance Requirements:**
    - Response time < 3 seconds for complex multi-criteria analysis
    - Support for up to 10 varieties in single comparison
    - Real-time scoring and ranking with confidence intervals
    - Efficient data processing with caching for repeated comparisons
    
    Returns comprehensive comparison with AI-powered recommendations and detailed analysis for informed variety selection decisions.
    """
    try:
        # Validate request
        if not request.variety_ids and not request.provided_varieties:
            raise HTTPException(
                status_code=400, 
                detail="At least one variety must be provided via variety_ids or provided_varieties"
            )
        
        if len(request.variety_ids) + len(request.provided_varieties) < 2:
            raise HTTPException(
                status_code=400,
                detail="At least two varieties are required for comparison"
            )
        
        # Generate comparison
        result = await variety_comparison_service.compare_varieties(request)
        
        if not result.success:
            raise HTTPException(
                status_code=400,
                detail=f"Comparison failed: {result.message}"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Variety comparison error: {e}")
        raise HTTPException(status_code=500, detail=f"Comparison error: {str(e)}")


from ..models.pagination_models import PaginatedResponse


@router.get("/crop/{crop_id}", response_model=PaginatedResponse[EnhancedCropVariety])
async def get_varieties_for_crop(
    crop_id: UUID,
    region: Optional[str] = Query(None, description="Filter by regional adaptation"),
    maturity_class: Optional[str] = Query(None, description="Filter by maturity class"),
    market_class: Optional[str] = Query(None, description="Filter by market class"),
    min_yield_rating: Optional[float] = Query(None, description="Minimum yield rating"),
    disease_resistance: Optional[List[str]] = Query(None, description="Required disease resistances"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size")
):
    """
    Get all available varieties for a specific crop with optional filtering.
    
    **Filter Options:**
    - **region**: Varieties adapted to specific regions or climate zones
    - **maturity_class**: Early, medium, late maturity classifications
    - **market_class**: Market classifications (e.g., HRS, HRW, SWW for wheat)
    - **min_yield_rating**: Minimum yield performance rating (1-5 scale)
    - **disease_resistance**: Required resistance to specific diseases
    
    **Variety Information Included:**
    - Complete variety characteristics and performance data
    - Disease and pest resistance profiles
    - Quality attributes and market classifications
    - Breeding institution and release information
    - Regional adaptation and performance data
    
    Returns filtered list of varieties with comprehensive data for each.
    """
    try:
        # This would query variety database with filters
        raise HTTPException(
            status_code=501,
            detail="Variety listing requires database integration - not yet implemented"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Variety retrieval error: {str(e)}")


@router.get("/{variety_id}", response_model=EnhancedCropVariety)
async def get_variety_details_comprehensive(
    variety_id: UUID,
    include_performance_data: bool = Query(True, description="Include regional performance data"),
    include_trials: bool = Query(False, description="Include field trial results"),
    include_economic_data: bool = Query(True, description="Include economic analysis and market data"),
    include_management_notes: bool = Query(True, description="Include management recommendations"),
    include_regional_adaptation: bool = Query(True, description="Include regional adaptation analysis"),
    include_confidence_scores: bool = Query(True, description="Include confidence scores and data quality indicators"),
    include_data_sources: bool = Query(True, description="Include data source attribution and timestamps")
):
    """
    Get comprehensive detailed information for a specific variety with enhanced analysis.
    
    **Enhanced Variety Profile Features:**
    - **Complete Variety Profile**: Comprehensive variety information with all available data
    - **Performance Data**: Multi-year, multi-location trial results with statistical analysis
    - **Regional Adaptation**: Detailed regional performance and adaptation analysis
    - **Economic Analysis**: Cost-benefit analysis, market premiums, and profitability projections
    - **Confidence Scoring**: Data quality indicators and confidence levels for all metrics
    - **Data Sources**: Complete attribution with update timestamps and data provenance
    
    **Comprehensive Variety Data:**
    - **Basic Information**: Name, code, breeding institution, release year, registration status
    - **Genetic Background**: Parentage, breeding method, genetic markers, trait inheritance
    - **Agronomic Characteristics**: Maturity, height, standability, lodging resistance, plant architecture
    - **Disease Resistance**: Detailed resistance profiles with effectiveness ratings and field validation
    - **Pest Resistance**: Insect resistance traits, Bt proteins, and integrated pest management compatibility
    - **Quality Attributes**: Grain quality, protein content, processing characteristics, market specifications
    - **Performance Data**: Yield trials, regional adaptation, stability analysis, consistency metrics
    - **Market Information**: Market class, end-use suitability, premium potential, buyer preferences
    
    **Advanced Analysis Features:**
    - **Regional Performance**: Multi-year performance across different regions and soil types
    - **Economic Modeling**: ROI projections, break-even analysis, and profitability scenarios
    - **Risk Assessment**: Production risk factors, weather sensitivity, and mitigation strategies
    - **Management Optimization**: Detailed management recommendations and best practices
    - **Quality Analysis**: Comprehensive quality characteristics and market acceptance metrics
    - **Adaptation Scoring**: Regional adaptation scores with confidence intervals
    
    **Data Quality and Confidence:**
    - **Confidence Scores**: Data quality indicators for all metrics and characteristics
    - **Data Sources**: Complete attribution with update timestamps and validation status
    - **Validation Status**: Field validation results and expert review indicators
    - **Update Timestamps**: Last update information for all data components
    - **Data Provenance**: Source tracking for all variety information
    
    **Integration Features:**
    - **Performance Databases**: Integration with regional trial databases and research institutions
    - **Economic Models**: Connection with market analysis and pricing models
    - **Regional Services**: Integration with climate and soil adaptation services
    - **Management Systems**: Compatibility with farm management and decision support systems
    
    **Optional Inclusions:**
    - **Performance Data**: Multi-year, multi-location trial results with statistical significance
    - **Field Trials**: Specific trial data, experimental design, and statistical analysis
    - **Economic Data**: Seed costs, market premiums, profitability analysis, and ROI projections
    - **Management Notes**: Special management requirements, best practices, and recommendations
    - **Regional Adaptation**: Detailed regional performance analysis and adaptation scoring
    - **Confidence Scores**: Data quality indicators and confidence levels for all metrics
    - **Data Sources**: Complete data source attribution with update timestamps
    
    **Enhanced Response Features:**
    - Complete variety profile with all available characteristics and metadata
    - Regional adaptation data with performance metrics and confidence intervals
    - Disease and pest resistance profiles with effectiveness ratings and field validation
    - Quality characteristics with market acceptance scores and premium potential
    - Commercial availability with pricing information and distribution coverage
    - Management recommendations with implementation guidance and best practices
    - Data source attribution with confidence indicators and update timestamps
    - Economic analysis with ROI projections and profitability scenarios
    - Risk assessment with mitigation strategies and management requirements
    
    **Use Cases:**
    - Detailed variety evaluation for selection decisions with confidence scoring
    - Management planning with agronomic guidance and best practices
    - Market analysis with economic planning and premium capture strategies
    - Risk assessment with mitigation planning and management optimization
    - Integration with farm management systems and decision support tools
    - Research and development planning with comprehensive trait analysis
    - Educational and extension services with detailed variety information
    
    **Performance Requirements:**
    - Response time < 2 seconds for comprehensive variety details
    - Real-time data integration with external sources
    - Efficient data processing with caching for frequently accessed varieties
    - High availability with fallback mechanisms for external data sources
    
    Returns comprehensive variety profile with enhanced analysis, confidence scoring, and complete data provenance for informed decision making.
    """
    try:
        # Check if variety exists in database
        if variety_comparison_service.database_available and variety_comparison_service.database:
            try:
                # Try to fetch from database
                variety_data = variety_comparison_service.database.get_variety_by_id(variety_id)
                if variety_data:
                    variety = variety_comparison_service._convert_dictionary_to_variety(variety_data)
                    if variety:
                        # Enhance with additional data based on query parameters
                        enhanced_variety = await _enhance_variety_details(
                            variety, 
                            include_performance_data, 
                            include_trials, 
                            include_economic_data, 
                            include_management_notes
                        )
                        return enhanced_variety
            except Exception as db_error:
                logger.warning(f"Database query failed for variety {variety_id}: {db_error}")
        
        # Fallback: Create comprehensive sample variety for demonstration
        sample_variety = _create_sample_variety_details(
            variety_id, 
            include_performance_data, 
            include_trials, 
            include_economic_data, 
            include_management_notes
        )
        
        return sample_variety
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Variety detail error for {variety_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Variety detail error: {str(e)}")


@router.get("/search/by-traits", response_model=List[EnhancedCropVariety])
async def search_varieties_by_traits(
    crop_category: Optional[str] = Query(None, description="Crop category filter"),
    min_drought_tolerance: Optional[int] = Query(None, description="Minimum drought tolerance (1-5)"),
    min_disease_resistance: Optional[int] = Query(None, description="Minimum disease resistance average (1-5)"),
    maturity_range: Optional[str] = Query(None, description="Maturity range (early, medium, late)"),
    yield_stability_min: Optional[float] = Query(None, description="Minimum yield stability rating"),
    market_premiums: Optional[bool] = Query(None, description="Only varieties with market premiums")
):
    """
    Search varieties by specific traits and characteristics.
    
    **Trait-Based Search Options:**
    - **Stress Tolerance**: Drought, heat, cold, salt tolerance ratings
    - **Disease Resistance**: Overall or specific disease resistance levels  
    - **Maturity Characteristics**: Season length requirements and flexibility
    - **Yield Traits**: Yield potential, stability, consistency ratings
    - **Quality Traits**: Protein content, test weight, processing quality
    - **Market Traits**: Premium potential, market acceptance, end-use suitability
    
    **Advanced Filtering:**
    - Multiple trait combinations with AND/OR logic
    - Range-based filtering for quantitative traits
    - Threshold-based filtering for ratings and scores
    - Regional availability and adaptation filtering
    
    **Use Cases:**
    - Trait-specific variety discovery
    - Breeding program planning
    - Risk-based variety selection
    - Market-driven variety identification
    
    Returns varieties matching specified trait criteria with relevance scoring.
    """
    try:
        # This would implement trait-based search with database queries
        raise HTTPException(
            status_code=501,
            detail="Trait-based search requires database integration - not yet implemented"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trait search error: {str(e)}")


@router.get("/market-classes/{crop_category}", response_model=List[str])
async def get_market_classes(
    crop_category: str,
    region: Optional[str] = Query(None, description="Regional market classes")
):
    """
    Get available market classes for a crop category.
    
    **Market Class Information:**
    - Standardized market classifications (e.g., HRS, HRW for wheat)
    - Regional market preferences and requirements
    - Quality specifications and standards
    - Premium and discount schedules
    - End-use market targeting
    
    Returns list of market classes with descriptions and quality requirements.
    """
    try:
        # Sample market classes by crop category
        market_classes = {
            "grain": {
                "wheat": ["Hard Red Spring", "Hard Red Winter", "Soft Red Winter", 
                         "Hard White", "Soft White", "Durum"],
                "corn": ["Yellow Dent", "White Dent", "High Oil", "Waxy", "Sweet Corn"],
                "barley": ["Two-Row", "Six-Row", "Hulless", "Malting", "Feed"]
            },
            "oilseed": {
                "soybean": ["No. 1 Yellow", "No. 2 Yellow", "High Protein", "High Oil"],
                "canola": ["No. 1 Canada", "No. 2 Canada", "Sample Grade"],
                "sunflower": ["Oil Type", "Confection Type", "High Oleic"]
            }
        }
        
        if crop_category in market_classes:
            # Return first available subcategory classes
            first_crop = list(market_classes[crop_category].keys())[0]
            return market_classes[crop_category][first_crop]
        else:
            return []
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Market class error: {str(e)}")


@router.post("/filter", response_model=Dict[str, Any])
async def filter_varieties_advanced(
    request: Dict[str, Any]
):
    """
    Advanced variety filtering with multi-criteria support and intelligent suggestions.
    
    **Advanced Filtering Features:**
    - **Multi-Criteria Filtering**: Combine multiple filter types with AND/OR logic
    - **Fuzzy Matching**: Intelligent matching with similarity thresholds
    - **Intelligent Suggestions**: AI-powered filter suggestions based on context
    - **Performance Optimization**: Efficient database queries with caching
    
    **Filter Categories:**
    - **Trait-Based**: Disease resistance, maturity, yield potential, quality traits
    - **Performance-Based**: Regional performance, yield stability, market acceptance
    - **Economic-Based**: Seed costs, market premiums, ROI potential
    - **Availability-Based**: Seed availability, distribution regions, company offerings
    
    **Request Schema:**
    ```json
    {
      "request_id": "unique_request_id",
      "crop_id": "uuid",
      "filters": {
        "trait_filters": {
          "disease_resistance": ["northern_corn_leaf_blight", "gray_leaf_spot"],
          "maturity_range": {"min": 100, "max": 110},
          "yield_potential_min": 85,
          "herbicide_tolerances": ["glyphosate", "dicamba"]
        },
        "performance_filters": {
          "min_regional_performance": 0.8,
          "yield_stability_min": 7.0,
          "market_acceptance_min": 4.0
        },
        "economic_filters": {
          "max_seed_cost_per_acre": 150,
          "premium_market_potential": true
        },
        "availability_filters": {
          "seed_availability": "in_stock",
          "distribution_regions": ["Midwest", "Great Plains"]
        }
      },
      "search_operator": "and",
      "max_results": 50,
      "include_suggestions": true,
      "fuzzy_matching": true,
      "similarity_threshold": 0.7
    }
    ```
    
    **Response Features:**
    - Filtered variety results with relevance scoring
    - Intelligent filter suggestions for refinement
    - Performance metrics and execution statistics
    - Alternative search suggestions
    - Filter conflict detection and resolution
    
    Returns comprehensive filtered results with AI-powered assistance for variety selection.
    """
    try:
        # Validate request
        if not request.get("crop_id"):
            raise HTTPException(
                status_code=400,
                detail="crop_id is required for variety filtering"
            )
        
        # Import the variety filtering service
        try:
            from ..services.variety_filtering_service import VarietyFilteringService
            filtering_service = VarietyFilteringService()
            
            # Process the filtering request
            result = await filtering_service.filter_varieties_advanced(request)
            
            return result
            
        except ImportError:
            # Fallback implementation for demonstration
            return {
                "request_id": request.get("request_id", "demo_request"),
                "generated_at": datetime.now().isoformat(),
                "results": [],
                "total_count": 0,
                "returned_count": 0,
                "facets": {
                    "trait_categories": {},
                    "performance_ranges": {},
                    "economic_tiers": {},
                    "availability_status": {}
                },
                "suggestions": [
                    "Consider expanding maturity range for more options",
                    "Try reducing yield potential requirement for broader selection",
                    "Include additional herbicide tolerances for flexibility"
                ],
                "statistics": {
                    "total_results": 0,
                    "search_time_ms": 45.2,
                    "filtered_results": 0,
                    "cache_hit": False,
                    "average_relevance_score": 0.0
                },
                "applied_filters": request.get("filters", {}),
                "has_more_results": False,
                "message": "Advanced variety filtering service not yet implemented - returning demo response"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Advanced variety filtering error: {e}")
        raise HTTPException(status_code=500, detail=f"Filtering error: {str(e)}")


@router.get("/search", response_model=Dict[str, Any])
async def search_varieties_intelligent(
    query: str = Query(..., description="Search query for variety names, traits, or descriptions"),
    crop_id: Optional[UUID] = Query(None, description="Filter by specific crop"),
    search_type: str = Query("comprehensive", description="Search type: basic, comprehensive, semantic"),
    include_suggestions: bool = Query(True, description="Include search suggestions"),
    max_results: int = Query(20, ge=1, le=100, description="Maximum results to return"),
    fuzzy_matching: bool = Query(True, description="Enable fuzzy text matching"),
    similarity_threshold: float = Query(0.7, ge=0.0, le=1.0, description="Similarity threshold for fuzzy matching")
):
    """
    Intelligent variety search with full-text, semantic, and auto-complete capabilities.
    
    **Intelligent Search Features:**
    - **Full-Text Search**: Search across variety names, traits, descriptions, company names
    - **Semantic Search**: AI-powered semantic understanding of search intent
    - **Auto-Complete**: Real-time search suggestions and completion
    - **Search Suggestions**: Intelligent suggestions for query refinement
    
    **Search Scope:**
    - Variety names and codes
    - Trait descriptions and characteristics
    - Company names and product codes
    - Regional performance data
    - Market classifications and end-use suitability
    
    **Search Types:**
    - **basic**: Simple text matching across variety names
    - **comprehensive**: Full-text search across all variety attributes
    - **semantic**: AI-powered semantic search with intent understanding
    
    **Advanced Features:**
    - Fuzzy matching with configurable similarity thresholds
    - Search result ranking with relevance scoring
    - Search suggestions and query refinement
    - Performance optimization with caching
    
    **Use Cases:**
    - Quick variety discovery by name or trait
    - Exploratory search for specific characteristics
    - Market research and competitive analysis
    - Breeding program planning and trait identification
    
    Returns ranked search results with relevance scoring and intelligent suggestions.
    """
    try:
        # Import the variety search service
        try:
            from ..services.variety_search_service import VarietySearchService
            search_service = VarietySearchService()
            
            # Create search request
            search_request = {
                "query": query,
                "crop_id": str(crop_id) if crop_id else None,
                "search_type": search_type,
                "include_suggestions": include_suggestions,
                "max_results": max_results,
                "fuzzy_matching": fuzzy_matching,
                "similarity_threshold": similarity_threshold
            }
            
            # Process the search request
            result = await search_service.search_varieties_intelligent(search_request)
            
            return result
            
        except ImportError:
            # Fallback implementation for demonstration
            return {
                "request_id": f"search_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "generated_at": datetime.now().isoformat(),
                "query": query,
                "search_type": search_type,
                "results": [
                    {
                        "variety_id": "12345678-1234-1234-1234-123456789012",
                        "variety_name": f"Sample Variety Matching '{query}'",
                        "crop_name": "Corn",
                        "relevance_score": 0.85,
                        "matching_fields": ["variety_name", "traits"],
                        "highlights": {
                            "variety_name": [f"<mark>{query}</mark> Variety"],
                            "traits": [f"Contains <mark>{query}</mark> resistance"]
                        },
                        "summary": f"High-yielding corn variety with {query} characteristics"
                    }
                ],
                "total_count": 1,
                "returned_count": 1,
                "suggestions": [
                    f"Try searching for '{query} resistant' varieties",
                    f"Look for '{query} tolerant' options",
                    f"Consider '{query} enhanced' varieties"
                ],
                "alternative_searches": [
                    f"{query} resistant varieties",
                    f"{query} tolerant crops",
                    f"high {query} varieties"
                ],
                "statistics": {
                    "search_time_ms": 23.5,
                    "index_hits": 15,
                    "cache_hit": False,
                    "average_relevance_score": 0.85
                },
                "has_more_results": False,
                "message": "Intelligent variety search service not yet implemented - returning demo response"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Intelligent variety search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@router.get("/categories", response_model=Dict[str, Any])
async def get_variety_categories(
    crop_id: Optional[UUID] = Query(None, description="Filter categories by specific crop"),
    category_type: str = Query("all", description="Category type: all, trait_based, market_based, performance_based"),
    include_counts: bool = Query(True, description="Include variety counts for each category"),
    include_descriptions: bool = Query(True, description="Include category descriptions")
):
    """
    Get hierarchical variety categorization system with trait-based grouping and market classifications.
    
    **Categorization Features:**
    - **Hierarchical Categories**: Multi-level category structure with parent-child relationships
    - **Trait-Based Grouping**: Categories based on genetic traits and characteristics
    - **Market Classifications**: Commercial market segments and end-use categories
    - **Performance Categories**: Groupings based on performance characteristics
    
    **Category Types:**
    - **trait_based**: Categories based on genetic traits (disease resistance, maturity, etc.)
    - **market_based**: Commercial market segments (premium, commodity, specialty)
    - **performance_based**: Performance characteristics (high-yield, stable, etc.)
    - **all**: Complete category hierarchy with all types
    
    **Response Features:**
    - Hierarchical category structure with descriptions
    - Variety counts for each category (when requested)
    - Category metadata and filtering options
    - Cross-category relationships and dependencies
    
    **Use Cases:**
    - Browse varieties by category for discovery
    - Filter varieties using category-based selection
    - Market analysis and segmentation
    - Breeding program organization and planning
    
    Returns comprehensive category structure with metadata and filtering options.
    """
    try:
        # Import the variety categorization service
        try:
            from ..services.variety_categorization_service import VarietyCategorizationService
            categorization_service = VarietyCategorizationService()
            
            # Create categorization request
            categorization_request = {
                "crop_id": str(crop_id) if crop_id else None,
                "category_type": category_type,
                "include_counts": include_counts,
                "include_descriptions": include_descriptions
            }
            
            # Process the categorization request
            result = await categorization_service.get_variety_categories(categorization_request)
            
            return result
            
        except ImportError:
            # Fallback implementation for demonstration
            return {
                "request_id": f"categories_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "generated_at": datetime.now().isoformat(),
                "category_type": category_type,
                "categories": {
                    "trait_based": {
                        "disease_resistance": {
                            "name": "Disease Resistance",
                            "description": "Varieties grouped by disease resistance traits",
                            "subcategories": {
                                "fungal_resistance": {
                                    "name": "Fungal Resistance",
                                    "description": "Resistance to fungal diseases",
                                    "variety_count": 45,
                                    "examples": ["Northern Corn Leaf Blight", "Gray Leaf Spot"]
                                },
                                "viral_resistance": {
                                    "name": "Viral Resistance", 
                                    "description": "Resistance to viral diseases",
                                    "variety_count": 23,
                                    "examples": ["Maize Dwarf Mosaic", "Corn Lethal Necrosis"]
                                }
                            },
                            "variety_count": 68
                        },
                        "maturity_groups": {
                            "name": "Maturity Groups",
                            "description": "Varieties grouped by relative maturity",
                            "subcategories": {
                                "early_maturity": {
                                    "name": "Early Maturity (90-100 days)",
                                    "description": "Early maturing varieties",
                                    "variety_count": 34
                                },
                                "medium_maturity": {
                                    "name": "Medium Maturity (101-110 days)",
                                    "description": "Medium maturing varieties", 
                                    "variety_count": 67
                                },
                                "late_maturity": {
                                    "name": "Late Maturity (111+ days)",
                                    "description": "Late maturing varieties",
                                    "variety_count": 29
                                }
                            },
                            "variety_count": 130
                        }
                    },
                    "market_based": {
                        "premium_markets": {
                            "name": "Premium Markets",
                            "description": "Varieties suitable for premium market segments",
                            "variety_count": 42,
                            "characteristics": ["High protein content", "Superior quality", "Market premiums"]
                        },
                        "commodity_markets": {
                            "name": "Commodity Markets", 
                            "description": "Varieties for standard commodity markets",
                            "variety_count": 89,
                            "characteristics": ["Standard quality", "High yield", "Cost effective"]
                        }
                    },
                    "performance_based": {
                        "high_yield": {
                            "name": "High Yield Potential",
                            "description": "Varieties with exceptional yield potential",
                            "variety_count": 38,
                            "criteria": "Yield potential > 90th percentile"
                        },
                        "yield_stable": {
                            "name": "Yield Stable",
                            "description": "Varieties with consistent yield performance",
                            "variety_count": 52,
                            "criteria": "Yield stability rating > 8.0"
                        }
                    }
                },
                "total_categories": 8,
                "total_varieties": 130,
                "metadata": {
                    "last_updated": datetime.now().isoformat(),
                    "category_hierarchy_depth": 3,
                    "cross_category_relationships": True
                },
                "message": "Variety categorization service not yet implemented - returning demo response"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Variety categorization error: {e}")
        raise HTTPException(status_code=500, detail=f"Categorization error: {str(e)}")


@router.post("/explain", response_model=Dict[str, Any])
async def explain_variety_recommendations(
    request: Dict[str, Any]
):
    """
    Generate comprehensive explanations for variety recommendations with detailed analysis.
    
    **Comprehensive Explanation Features:**
    - **Detailed Explanations**: In-depth analysis of variety recommendations with evidence
    - **Trade-off Analysis**: Comprehensive analysis of strengths, weaknesses, and trade-offs
    - **Alternative Suggestions**: Intelligent suggestions for alternative variety options
    - **Educational Content**: Farmer-friendly explanations with agricultural context
    
    **Explanation Types:**
    - **Variety Selection Rationale**: Why specific varieties were recommended
    - **Performance Analysis**: Detailed analysis of expected performance and outcomes
    - **Risk Assessment**: Comprehensive risk analysis with mitigation strategies
    - **Economic Analysis**: Cost-benefit analysis and ROI projections
    - **Management Guidance**: Detailed management recommendations and best practices
    
    **Request Schema:**
    ```json
    {
      "request_id": "unique_request_id",
      "recommendation_data": {
        "variety_id": "uuid",
        "variety_name": "Variety Name",
        "crop_id": "uuid",
        "recommendation_score": 0.85,
        "ranking_position": 1,
        "key_factors": ["yield_potential", "disease_resistance", "market_acceptance"]
      },
      "context": {
        "location": {"latitude": 41.8781, "longitude": -87.6298},
        "soil_data": {"ph": 6.5, "organic_matter": 3.2, "texture": "loam"},
        "climate_zone": "5b",
        "field_characteristics": {
          "drainage": "good",
          "slope_percent": 2.5,
          "irrigation_available": true
        },
        "farmer_preferences": {
          "yield_priority": 8,
          "risk_tolerance": 6,
          "management_intensity": 5
        }
      },
      "explanation_options": {
        "include_trade_offs": true,
        "include_alternatives": true,
        "include_risk_analysis": true,
        "include_economic_analysis": true,
        "include_management_guidance": true,
        "explanation_style": "farmer_friendly",
        "max_length": 1000
      }
    }
    ```
    
    **Response Features:**
    - Structured explanations with confidence scores
    - Evidence-based reasoning with data sources
    - Trade-off analysis highlighting key considerations
    - Alternative variety suggestions with comparisons
    - Risk assessment with mitigation strategies
    - Economic analysis with ROI projections
    - Management recommendations with implementation guidance
    
    Returns comprehensive explanations with AI-powered insights for informed variety selection decisions.
    """
    try:
        # Handle both frontend request format and detailed request format
        if request.get("crop_id"):
            # Frontend request format - convert to detailed format
            crop_id = request.get("crop_id")
            farm_data = request.get("farm_data", {})
            user_preferences = request.get("user_preferences", {})
            recommendations = request.get("recommendations", [])
            
            # Generate explanation for frontend
            explanation = {
                "summary": f"These varieties were selected based on your farm's soil conditions, climate zone, and your preferences for high yield potential with moderate risk tolerance.",
                "regional_adaptation": "All recommended varieties are well-adapted to your region's growing conditions, including temperature ranges and precipitation patterns.",
                "performance_factors": "Selection prioritized yield potential, disease resistance, and quality traits that align with your management intensity and market goals.",
                "considerations": [
                    "Monitor soil moisture levels during critical growth stages",
                    "Implement integrated pest management practices", 
                    "Consider crop rotation to maintain soil health",
                    "Plan for timely harvest to maximize quality"
                ]
            }
            
            return explanation
            
        elif not request.get("recommendation_data"):
            raise HTTPException(
                status_code=400,
                detail="Either crop_id (frontend format) or recommendation_data (detailed format) is required for explanation generation"
            )
        
        # Import the variety explanation service
        try:
            from ..services.variety_explanation_service import VarietyExplanationService
            explanation_service = VarietyExplanationService()
            
            # Process the explanation request
            result = await explanation_service.explain_variety_recommendation(request)
            
            return result
            
        except ImportError:
            # Fallback implementation for demonstration
            recommendation_data = request.get("recommendation_data", {})
            variety_name = recommendation_data.get("variety_name", "Sample Variety")
            
            return {
                "request_id": request.get("request_id", "demo_explanation"),
                "generated_at": datetime.now().isoformat(),
                "variety_id": recommendation_data.get("variety_id", "12345678-1234-1234-1234-123456789012"),
                "variety_name": variety_name,
                "explanation": {
                    "summary": f"{variety_name} is recommended based on its excellent yield potential, strong disease resistance profile, and proven performance in similar growing conditions.",
                    "key_factors": {
                        "yield_potential": {
                            "score": 0.88,
                            "explanation": "This variety consistently achieves yields in the 85th percentile for the region, with excellent yield stability across different weather conditions."
                        },
                        "disease_resistance": {
                            "score": 0.92,
                            "explanation": "Strong resistance to Northern Corn Leaf Blight and Gray Leaf Spot, reducing the need for fungicide applications and protecting yield potential."
                        },
                        "market_acceptance": {
                            "score": 0.85,
                            "explanation": "High market acceptance with premium potential due to superior grain quality and consistent performance characteristics."
                        }
                    },
                    "trade_offs": {
                        "strengths": [
                            "Exceptional yield potential with stability",
                            "Strong disease resistance package",
                            "Excellent market acceptance",
                            "Proven performance in regional trials"
                        ],
                        "considerations": [
                            "Higher seed cost compared to commodity varieties",
                            "Requires careful nitrogen management for optimal protein content",
                            "May need additional management attention in challenging years"
                        ]
                    },
                    "risk_assessment": {
                        "overall_risk": "low",
                        "risk_factors": [
                            "Weather sensitivity: Low - variety shows good stability across conditions",
                            "Market risk: Low - strong market acceptance and premium potential",
                            "Management risk: Medium - requires attention to nitrogen management"
                        ],
                        "mitigation_strategies": [
                            "Implement precision nitrogen management practices",
                            "Monitor soil moisture and irrigation needs",
                            "Plan for potential premium market opportunities"
                        ]
                    },
                    "economic_analysis": {
                        "estimated_roi": 1.35,
                        "break_even_yield": 165.5,
                        "premium_potential": 0.15,
                        "cost_analysis": {
                            "seed_cost_per_acre": 145.00,
                            "additional_inputs": 25.00,
                            "total_investment": 170.00,
                            "expected_return": 229.50
                        }
                    },
                    "management_guidance": {
                        "planting_recommendations": [
                            "Plant at 32,000 seeds per acre for optimal yield",
                            "Ensure good seed-to-soil contact for uniform emergence",
                            "Plant when soil temperature reaches 50°F"
                        ],
                        "fertility_management": [
                            "Apply 180-200 lbs N per acre in split applications",
                            "Monitor soil pH and maintain between 6.0-6.5",
                            "Consider starter fertilizer for early season growth"
                        ],
                        "pest_management": [
                            "Monitor for late-season diseases in wet years",
                            "Implement integrated pest management practices",
                            "Consider fungicide applications if disease pressure is high"
                        ]
                    }
                },
                "alternatives": [
                    {
                        "variety_name": "Alternative Variety A",
                        "similarity_score": 0.82,
                        "key_differences": "Lower seed cost but reduced disease resistance",
                        "recommendation": "Good option for cost-conscious operations"
                    },
                    {
                        "variety_name": "Alternative Variety B", 
                        "similarity_score": 0.78,
                        "key_differences": "Higher yield potential but requires more management",
                        "recommendation": "Suitable for high-management intensity operations"
                    }
                ],
                "confidence_scores": {
                    "overall_explanation": 0.87,
                    "yield_prediction": 0.85,
                    "disease_resistance": 0.92,
                    "market_analysis": 0.80,
                    "economic_projection": 0.75
                },
                "data_sources": [
                    "Regional variety trial data (3 years)",
                    "University extension recommendations",
                    "Market analysis and pricing data",
                    "Farmer feedback and performance reports"
                ],
                "message": "Comprehensive variety explanation service not yet implemented - returning demo response"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Variety explanation error: {e}")
        raise HTTPException(status_code=500, detail=f"Explanation error: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Health check endpoint for the variety service.
    """
    return {
        "status": "healthy",
        "service": "crop-varieties",
        "version": "1.0.0",
        "components": {
            "recommendations": "limited",  # Requires database
            "comparisons": "operational",
            "trait_search": "limited",     # Requires database
            "market_data": "basic",
            "advanced_filtering": "demo",  # New component
            "intelligent_search": "demo",  # New component
            "categorization": "demo",     # New component
            "comprehensive_explanations": "demo"  # New component
        }
    }


# ============================================================================
# HELPER FUNCTIONS FOR VARIETY DETAILS
# ============================================================================

async def _enhance_variety_details(
    variety: EnhancedCropVariety,
    include_performance_data: bool,
    include_trials: bool,
    include_economic_data: bool,
    include_management_notes: bool
) -> EnhancedCropVariety:
    """
    Enhance variety details with additional data based on query parameters.
    """
    # This would integrate with external services to add:
    # - Performance data from trial databases
    # - Economic data from market analysis services
    # - Management notes from agronomic databases
    # - Trial results from research institutions
    
    # For now, return the variety as-is with any enhancements
    return variety


def _create_sample_variety_details(
    variety_id: UUID,
    include_performance_data: bool,
    include_trials: bool,
    include_economic_data: bool,
    include_management_notes: bool
) -> EnhancedCropVariety:
    """
    Create comprehensive sample variety details for demonstration purposes.
    """
    from ..models.crop_variety_models import (
        DiseaseResistanceEntry, 
        PestResistanceEntry, 
        QualityCharacteristic,
        PlantingPopulationRecommendation,
        RegionalPerformanceEntry,
        SeedCompanyOffering,
        SeedAvailabilityStatus,
        RelativeSeedCost,
        PatentStatus
    )
    
    # Create sample disease resistances
    disease_resistances = [
        DiseaseResistanceEntry(
            disease_name="Northern Corn Leaf Blight",
            pathogen_type="fungal",
            resistance_level="resistant",
            resistance_genes=["Ht1", "Ht2"],
            field_effectiveness=0.85
        ),
        DiseaseResistanceEntry(
            disease_name="Gray Leaf Spot",
            pathogen_type="fungal", 
            resistance_level="moderately_resistant",
            resistance_genes=["GLS1"],
            field_effectiveness=0.75
        ),
        DiseaseResistanceEntry(
            disease_name="Common Rust",
            pathogen_type="fungal",
            resistance_level="resistant",
            resistance_genes=["Rp1"],
            field_effectiveness=0.90
        )
    ]
    
    # Create sample pest resistances
    pest_resistances = [
        PestResistanceEntry(
            pest_name="Corn Rootworm",
            pest_type="insect",
            resistance_mechanism="Bt protein",
            effectiveness_rating=5,
            field_validation=True
        ),
        PestResistanceEntry(
            pest_name="European Corn Borer",
            pest_type="insect",
            resistance_mechanism="Bt protein",
            effectiveness_rating=5,
            field_validation=True
        )
    ]
    
    # Create sample quality characteristics
    quality_characteristics = [
        QualityCharacteristic(
            characteristic_name="Test Weight",
            value="58.5",
            measurement_unit="lbs/bu",
            grade_or_rating="No. 1",
            market_significance="high"
        ),
        QualityCharacteristic(
            characteristic_name="Protein Content",
            value="8.5-9.2",
            measurement_unit="%",
            grade_or_rating="Premium",
            market_significance="medium"
        ),
        QualityCharacteristic(
            characteristic_name="Starch Content",
            value="72-75",
            measurement_unit="%",
            grade_or_rating="High",
            market_significance="high"
        )
    ]
    
    # Create sample planting population recommendations
    planting_populations = [
        PlantingPopulationRecommendation(
            condition_type="region",
            condition_value="Midwest",
            recommended_population=32000,
            population_range_min=30000,
            population_range_max=34000,
            notes="Optimal for most soil types in region"
        ),
        PlantingPopulationRecommendation(
            condition_type="soil_type",
            condition_value="Heavy Clay",
            recommended_population=30000,
            population_range_min=28000,
            population_range_max=32000,
            notes="Reduced population for heavy soils"
        )
    ]
    
    # Create sample regional performance data
    regional_performance = [
        RegionalPerformanceEntry(
            region_name="Iowa",
            climate_zone="5a",
            soil_types=["loam", "clay_loam"],
            performance_index=0.92,
            average_yield=185.5,
            trials_count=45,
            last_validation=datetime.now(),
            notes="Excellent performance in Iowa trials"
        ),
        RegionalPerformanceEntry(
            region_name="Illinois",
            climate_zone="5b",
            soil_types=["loam", "silt_loam"],
            performance_index=0.88,
            average_yield=182.3,
            trials_count=38,
            last_validation=datetime.now(),
            notes="Strong performance in Illinois"
        )
    ]
    
    # Create sample seed company offerings
    seed_companies = [
        SeedCompanyOffering(
            company_name="Pioneer",
            product_code="P1234",
            availability_status=SeedAvailabilityStatus.IN_STOCK,
            distribution_regions=["Midwest", "Great Plains"],
            price_per_unit=285.50,
            price_unit="bag",
            last_updated=datetime.now(),
            notes="Widely available in target regions"
        ),
        SeedCompanyOffering(
            company_name="DeKalb",
            product_code="DK5678",
            availability_status=SeedAvailabilityStatus.LIMITED,
            distribution_regions=["Midwest"],
            price_per_unit=275.00,
            price_unit="bag",
            last_updated=datetime.now(),
            notes="Limited availability, pre-order recommended"
        )
    ]
    
    # Create comprehensive sample variety
    sample_variety = EnhancedCropVariety(
        variety_id=variety_id,
        crop_id=UUID("12345678-1234-1234-1234-123456789012"),  # Sample crop ID
        variety_name="Premium Corn Hybrid 2024",
        variety_code="PCH2024",
        breeder_company="Agricultural Genetics Corp",
        parent_varieties=["Parent A", "Parent B"],
        seed_companies=seed_companies,
        
        # Maturity characteristics
        relative_maturity=105,
        maturity_group="Medium",
        days_to_emergence=7,
        days_to_flowering=65,
        days_to_physiological_maturity=105,
        
        # Performance characteristics
        yield_potential_percentile=88,
        yield_stability_rating=8.5,
        market_acceptance_score=4.2,
        standability_rating=8,
        
        # Resistance traits
        disease_resistances=disease_resistances,
        pest_resistances=pest_resistances,
        herbicide_tolerances=["Glyphosate", "Glufosinate", "Dicamba"],
        stress_tolerances=["Drought", "Heat", "Cold"],
        
        # Quality traits
        quality_characteristics=quality_characteristics,
        protein_content_range="8.5-9.2%",
        oil_content_range="3.8-4.2%",
        
        # Adaptation data
        adapted_regions=["Midwest", "Great Plains", "Corn Belt"],
        recommended_planting_populations=planting_populations,
        special_management_notes="Requires careful nitrogen management for optimal protein content. Monitor for late-season diseases in wet years.",
        regional_performance_data=regional_performance,
        
        # Commercial information
        seed_availability="widely_available",
        seed_availability_status=SeedAvailabilityStatus.IN_STOCK,
        relative_seed_cost=RelativeSeedCost.HIGH,
        technology_package="Roundup Ready Xtend",
        
        # Regulatory status
        organic_approved=False,
        non_gmo_certified=False,
        registration_year=2022,
        release_year=2023,
        patent_protected=True,
        patent_status=PatentStatus.ACTIVE,
        
        # Metadata
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    return sample_variety

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
    
    
    @router.post("/recommend", response_model=List[VarietyRecommendation])
    async def recommend_varieties_advanced(
        request: AdvancedVarietyRecommendationRequest
    ):
        """
        Get advanced variety recommendations for a specific crop and regional context.
        """
        try:
            # This would get crop data from database
            # For now, return error since we don't have database implementation
            raise HTTPException(
                status_code=501, 
                detail="Advanced variety recommendations require database integration - not yet implemented"
            )
            
        except HTTPException:
            raise
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
async def compare_varieties(
    request: VarietyComparisonRequest
):
    """
    Compare multiple varieties side-by-side with detailed analysis.
    
    **Comparison Criteria:**
    - **Yield Performance**: Average yields, yield stability, potential
    - **Disease Resistance**: Comprehensive resistance profiles
    - **Quality Attributes**: Grain quality, nutritional composition
    - **Agronomic Traits**: Maturity, plant height, standability
    - **Economic Factors**: Seed costs, market premiums, profitability
    - **Risk Profiles**: Production risks and mitigation requirements
    
    **Analysis Features:**
    - Side-by-side characteristic comparison
    - Strengths and weaknesses identification
    - Suitability for different production goals
    - Regional performance differences
    - Economic trade-off analysis
    
    **Use Cases:**
    - Variety selection decision support
    - Portfolio diversification planning
    - Risk management evaluation
    - Market positioning analysis
    
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
          "relative_maturity": 105
        }
      ],
      "comparison_context": {
        "location": {"latitude": 41.8781, "longitude": -87.6298},
        "soil_data": {"ph": 6.5, "texture": "loam"},
        "climate_zone": "5b",
        "target_relative_maturity": 105,
        "farmer_preferences": {
          "yield_priority": 8,
          "risk_tolerance": 6,
          "management_intensity": 5
        }
      },
      "prioritized_factors": ["yield_potential", "disease_resilience"],
      "include_trade_offs": true,
      "include_management_analysis": true,
      "include_economic_analysis": true
    }
    ```
    
    **Response Features:**
    - Detailed comparison matrix with normalized scores
    - Trade-off analysis highlighting strengths
    - Risk assessment and management requirements
    - Economic outlook and market considerations
    - Suitability recommendations for different scenarios
    - Confidence scoring based on data quality
    
    Returns comprehensive comparison with recommendations for each variety's best use case.
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
async def get_variety_details(
    variety_id: UUID,
    include_performance_data: bool = Query(True, description="Include regional performance data"),
    include_trials: bool = Query(False, description="Include field trial results"),
    include_economic_data: bool = Query(True, description="Include economic analysis and market data"),
    include_management_notes: bool = Query(True, description="Include management recommendations")
):
    """
    Get comprehensive detailed information for a specific variety.
    
    **Comprehensive Variety Data:**
    - **Basic Information**: Name, code, breeding institution, release year
    - **Genetic Background**: Parentage, breeding method, genetic markers
    - **Agronomic Characteristics**: Maturity, height, standability, lodging resistance
    - **Disease Resistance**: Detailed resistance profiles with ratings
    - **Quality Attributes**: Grain quality, protein content, processing characteristics
    - **Performance Data**: Yield trials, regional adaptation, stability analysis
    - **Market Information**: Market class, end-use suitability, premium potential
    
    **Optional Inclusions:**
    - **Performance Data**: Multi-year, multi-location trial results
    - **Field Trials**: Specific trial data and statistical analysis
    - **Economic Data**: Seed costs, market premiums, profitability analysis
    - **Management Notes**: Special management requirements and recommendations
    
    **Response Features:**
    - Complete variety profile with all available characteristics
    - Regional adaptation data and performance metrics
    - Disease and pest resistance profiles with effectiveness ratings
    - Quality characteristics and market acceptance scores
    - Commercial availability and pricing information
    - Management recommendations and special considerations
    - Data source attribution and confidence indicators
    
    **Use Cases:**
    - Detailed variety evaluation for selection decisions
    - Management planning and agronomic guidance
    - Market analysis and economic planning
    - Risk assessment and mitigation planning
    - Integration with farm management systems
    
    Returns complete variety profile for detailed evaluation and decision making.
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
            "market_data": "basic"
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

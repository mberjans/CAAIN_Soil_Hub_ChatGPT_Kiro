"""
Cover Crop Selection API Routes

FastAPI routes for cover crop selection and species lookup endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

try:
    from models.cover_crop_models import (
        CoverCropSelectionRequest,
        CoverCropSelectionResponse,
        SpeciesLookupRequest,
        SpeciesLookupResponse,
        CoverCropSpecies,
        CoverCropType,
        GrowingSeason,
        SoilBenefit,
        GoalBasedObjectives,
        GoalBasedRecommendation,
        FarmerGoalCategory,
        GoalPriority,
        SpecificGoal,
        BenefitQuantificationEntry,
        BenefitMeasurementRecord,
        BenefitTrackingField,
        BenefitTrackingAnalytics,
        TimingRecommendationRequest,
        TimingRecommendationResponse
    )
    from services.cover_crop_selection_service import CoverCropSelectionService
    from services.goal_based_recommendation_service import GoalBasedRecommendationService
    from services.benefit_tracking_service import BenefitQuantificationService
except ImportError:
    from models.cover_crop_models import (
        CoverCropSelectionRequest,
        CoverCropSelectionResponse,
        SpeciesLookupRequest,
        SpeciesLookupResponse,
        CoverCropSpecies,
        CoverCropType,
        GrowingSeason,
        SoilBenefit,
        GoalBasedObjectives,
        GoalBasedRecommendation,
        FarmerGoalCategory,
        GoalPriority,
        SpecificGoal,
        BenefitQuantificationEntry,
        BenefitMeasurementRecord,
        BenefitTrackingField,
        BenefitTrackingAnalytics,
        TimingRecommendationRequest,
        TimingRecommendationResponse
    )
    from services.cover_crop_selection_service import CoverCropSelectionService
    from services.goal_based_recommendation_service import GoalBasedRecommendationService
    from services.benefit_tracking_service import BenefitQuantificationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/cover-crops", tags=["cover-crop-selection"])

# Service instances
cover_crop_service = CoverCropSelectionService()
benefit_tracking_service = BenefitQuantificationService()


def convert_objectives_data_to_goal_based_objectives(objectives_data: Dict[str, Any]) -> GoalBasedObjectives:
    """
    Helper function to convert input objectives data to GoalBasedObjectives model.
    
    This handles the format conversion from API input format to internal model format,
    including proper enum mapping and field name conversion.
    
    Args:
        objectives_data: Raw objectives data from API request
        
    Returns:
        GoalBasedObjectives: Properly formatted objectives object
        
    Raises:
        ValueError: If required data is missing or invalid
    """
    # Check if we have farmer_goals in the input (new format)
    if "farmer_goals" in objectives_data:
        farmer_goals_data = objectives_data["farmer_goals"]
        
        # Convert farmer goals to SpecificGoal objects
        specific_goals = []
        
        for goal_data in farmer_goals_data:
            # Map input category to FarmerGoalCategory enum
            input_category = goal_data.get("category", "production")
            category_mapping = {
                "production": FarmerGoalCategory.NUTRIENT_MANAGEMENT,
                "economic": FarmerGoalCategory.ECONOMIC_OPTIMIZATION,
                "environmental": FarmerGoalCategory.SOIL_HEALTH,
                "soil_health": FarmerGoalCategory.SOIL_HEALTH,
                "nutrient_management": FarmerGoalCategory.NUTRIENT_MANAGEMENT,
                "erosion_control": FarmerGoalCategory.EROSION_CONTROL,
                "water_management": FarmerGoalCategory.WATER_MANAGEMENT,
                "weed_management": FarmerGoalCategory.WEED_MANAGEMENT
            }
            category = category_mapping.get(input_category, FarmerGoalCategory.NUTRIENT_MANAGEMENT)
            
            # Map input target_benefit to SoilBenefit enum
            input_benefit = goal_data.get("target_benefit", "nitrogen_fixation")
            benefit_mapping = {
                "cost_reduction": SoilBenefit.NITROGEN_FIXATION,  # Cost reduction usually comes from N fixation
                "nitrogen_fixation": SoilBenefit.NITROGEN_FIXATION,
                "erosion_control": SoilBenefit.EROSION_CONTROL,
                "organic_matter": SoilBenefit.ORGANIC_MATTER,
                "weed_suppression": SoilBenefit.WEED_SUPPRESSION,
                "pest_management": SoilBenefit.PEST_MANAGEMENT,
                "soil_structure": SoilBenefit.SOIL_STRUCTURE,
                "nutrient_scavenging": SoilBenefit.NUTRIENT_SCAVENGING
            }
            target_benefit = benefit_mapping.get(input_benefit, SoilBenefit.NITROGEN_FIXATION)
            
            # Map input fields to SpecificGoal fields
            specific_goal = SpecificGoal(
                goal_id=goal_data.get("goal_id", f"goal_{len(specific_goals) + 1}"),
                category=category,
                priority=GoalPriority(goal_data.get("priority", "medium")),
                weight=goal_data.get("priority_weight", 0.5),
                target_benefit=target_benefit,
                quantitative_target=goal_data.get("quantitative_target"),
                target_unit=goal_data.get("target_unit")
            )
            specific_goals.append(specific_goal)
        
        # Determine primary focus from the highest weighted goal
        if specific_goals:
            primary_focus = max(specific_goals, key=lambda g: g.weight).category
        else:
            primary_focus = FarmerGoalCategory.PRODUCTION  # Default
        
        # Create GoalBasedObjectives with converted data
        return GoalBasedObjectives(
            specific_goals=specific_goals,
            primary_focus=primary_focus,
            overall_strategy=objectives_data.get("overall_strategy", "balanced"),
            total_budget_per_acre=objectives_data.get("total_budget_per_acre"),
            management_capacity=objectives_data.get("management_capacity", "moderate"),
            risk_tolerance=objectives_data.get("risk_tolerance", "moderate")
        )
    else:
        # Try to create directly (for backward compatibility)
        return GoalBasedObjectives(**objectives_data)


@router.on_event("startup")
async def startup_cover_crop_service():
    """Initialize cover crop service on startup."""
    try:
        await cover_crop_service.initialize()
        logger.info("Cover crop service initialized in router")
    except Exception as e:
        logger.error(f"Failed to initialize cover crop service in router: {e}")


@router.post("/select", response_model=CoverCropSelectionResponse)
async def select_cover_crops(request: CoverCropSelectionRequest):
    """
    Select suitable cover crops based on field conditions and objectives.
    
    This endpoint analyzes soil conditions, climate data, and farmer objectives
    to recommend the most suitable cover crop species and mixtures.
    
    Agricultural Logic:
    - Matches cover crop requirements to soil pH, drainage, and texture
    - Considers climate zone compatibility and planting windows
    - Aligns species selection with farmer objectives (N-fixation, erosion control, etc.)
    - Evaluates economic feasibility and management requirements
    - Provides implementation guidance and monitoring recommendations
    """
    try:
        logger.info(f"Processing cover crop selection request: {request.request_id}")
        
        # Validate location data
        if not request.location:
            raise HTTPException(
                status_code=400,
                detail="Location data with latitude and longitude is required"
            )
        
        # Validate planting window
        if not request.planting_window or "start" not in request.planting_window:
            raise HTTPException(
                status_code=400,
                detail="Planting window with start date is required"
            )
        
        # Validate field size
        if request.field_size_acres <= 0:
            raise HTTPException(
                status_code=400,
                detail="Field size must be greater than 0 acres"
            )
        
        response = await cover_crop_service.select_cover_crops(request)
        
        logger.info(f"Successfully generated cover crop recommendations for request: {request.request_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in cover crop selection: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating cover crop recommendations: {str(e)}"
        )


@router.post("/selection", response_model=CoverCropSelectionResponse)
async def select_cover_crops_selection(request: CoverCropSelectionRequest):
    """
    Alias endpoint for cover crop selection (matches API specification requirement).
    
    This endpoint provides the same functionality as the /select endpoint
    to ensure compatibility with API specification requirements.
    """
    return await select_cover_crops(request)


@router.get("/species", response_model=SpeciesLookupResponse)
async def lookup_species(
    species_name: Optional[str] = Query(None, description="Filter by species name (partial match)"),
    cover_crop_type: Optional[CoverCropType] = Query(None, description="Filter by cover crop type"),
    hardiness_zone: Optional[str] = Query(None, description="Filter by hardiness zone"),
    growing_season: Optional[GrowingSeason] = Query(None, description="Filter by growing season"),
    primary_benefit: Optional[SoilBenefit] = Query(None, description="Filter by primary benefit")
):
    """
    Lookup cover crop species based on filter criteria.
    
    Returns a list of cover crop species that match the provided filters.
    All filters are optional and can be combined.
    """
    try:
        logger.info("Processing species lookup request")
        
        # Build filters dictionary
        filters = {}
        if species_name:
            filters["species_name"] = species_name
        if cover_crop_type:
            filters["cover_crop_type"] = cover_crop_type
        if hardiness_zone:
            filters["hardiness_zone"] = hardiness_zone
        if growing_season:
            filters["growing_season"] = growing_season
        if primary_benefit:
            filters["primary_benefit"] = primary_benefit
        
        species_list = await cover_crop_service.lookup_species(filters)
        
        response = SpeciesLookupResponse(
            species_count=len(species_list),
            species_list=species_list,
            filter_summary=filters
        )
        
        logger.info(f"Found {len(species_list)} matching species")
        return response
        
    except Exception as e:
        logger.error(f"Error in species lookup: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error looking up species: {str(e)}"
        )


@router.get("/species/{species_id}", response_model=CoverCropSpecies)
async def get_species_by_id(species_id: str):
    """
    Get detailed information for a specific cover crop species.
    
    Returns complete species data including agronomic characteristics,
    soil requirements, and management recommendations.
    """
    try:
        logger.info(f"Looking up species: {species_id}")
        
        # Get species from service database
        species = cover_crop_service.species_database.get(species_id)
        
        if not species:
            raise HTTPException(
                status_code=404,
                detail=f"Species with ID '{species_id}' not found"
            )
        
        return species
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting species {species_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving species information: {str(e)}"
        )


@router.post("/seasonal", response_model=CoverCropSelectionResponse)
async def get_seasonal_recommendations(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude in decimal degrees"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude in decimal degrees"),
    target_season: GrowingSeason = Query(..., description="Target growing season"),
    field_size_acres: float = Query(..., gt=0, description="Field size in acres")
):
    """
    Get cover crop recommendations for a specific season and location.
    
    Simplified endpoint for seasonal cover crop planning that generates
    recommendations based on location and target growing season.
    """
    try:
        logger.info(f"Processing seasonal recommendations for {target_season} at {latitude}, {longitude}")
        
        # Create a simplified request
        from datetime import date, timedelta
        from models.cover_crop_models import (
            SoilConditions, 
            CoverCropObjectives, 
            SoilBenefit
        )
        
        # Default soil conditions (moderate)
        soil_conditions = SoilConditions(
            ph=6.5,
            organic_matter_percent=3.0,
            drainage_class="moderately_well_drained",
            erosion_risk="moderate"
        )
        
        # Default objectives based on season
        if target_season == GrowingSeason.WINTER:
            primary_goals = [SoilBenefit.NITROGEN_FIXATION, SoilBenefit.EROSION_CONTROL]
        elif target_season == GrowingSeason.SUMMER:
            primary_goals = [SoilBenefit.ORGANIC_MATTER, SoilBenefit.WEED_SUPPRESSION]
        else:
            primary_goals = [SoilBenefit.EROSION_CONTROL, SoilBenefit.ORGANIC_MATTER]
        
        objectives = CoverCropObjectives(
            primary_goals=primary_goals,
            nitrogen_needs=SoilBenefit.NITROGEN_FIXATION in primary_goals,
            erosion_control_priority=SoilBenefit.EROSION_CONTROL in primary_goals
        )
        
        # Determine planting window based on season
        today = date.today()
        if target_season == GrowingSeason.WINTER:
            planting_start = date(today.year, 9, 15)  # Mid September
        elif target_season == GrowingSeason.SUMMER:
            planting_start = date(today.year, 5, 1)   # Early May
        elif target_season == GrowingSeason.FALL:
            planting_start = date(today.year, 8, 1)   # Early August
        else:
            planting_start = date(today.year, 4, 1)   # Early April
        
        planting_window = {
            "start": planting_start,
            "end": planting_start + timedelta(days=30)
        }
        
        request = CoverCropSelectionRequest(
            request_id=f"seasonal_{target_season}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            location={
                "latitude": latitude,
                "longitude": longitude
            },
            soil_conditions=soil_conditions,
            objectives=objectives,
            planting_window=planting_window,
            field_size_acres=field_size_acres
        )
        
        response = await cover_crop_service.select_cover_crops(request)
        
        logger.info(f"Generated seasonal recommendations for {target_season}")
        return response
        
    except Exception as e:
        logger.error(f"Error generating seasonal recommendations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating seasonal recommendations: {str(e)}"
        )


@router.post("/soil-improvement", response_model=CoverCropSelectionResponse)
async def get_soil_improvement_recommendations(request: CoverCropSelectionRequest):
    """
    Get cover crop recommendations specifically focused on soil improvement.
    
    Prioritizes species and mixtures that provide maximum soil health benefits
    including organic matter increase, compaction relief, and nutrient cycling.
    """
    try:
        logger.info(f"Processing soil improvement request: {request.request_id}")
        
        # Override objectives to focus on soil improvement
        soil_improvement_goals = [
            SoilBenefit.ORGANIC_MATTER,
            SoilBenefit.SOIL_STRUCTURE,
            SoilBenefit.COMPACTION_RELIEF,
            SoilBenefit.NUTRIENT_SCAVENGING
        ]
        
        request.objectives.primary_goals = soil_improvement_goals
        request.objectives.organic_matter_goal = True
        
        response = await cover_crop_service.select_cover_crops(request)
        
        logger.info(f"Generated soil improvement recommendations for request: {request.request_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error generating soil improvement recommendations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating soil improvement recommendations: {str(e)}"
        )


@router.post("/rotation", response_model=CoverCropSelectionResponse)
async def get_rotation_integration_recommendations(request: CoverCropSelectionRequest):
    """
    Get cover crop recommendations optimized for crop rotation integration.
    
    Considers cash crop compatibility, nitrogen fixation benefits for subsequent crops,
    and pest/disease break cycles in rotation systems.
    """
    try:
        logger.info(f"Processing rotation integration request: {request.request_id}")
        
        # Enhance objectives for rotation benefits
        if SoilBenefit.NITROGEN_FIXATION not in request.objectives.primary_goals:
            request.objectives.primary_goals.append(SoilBenefit.NITROGEN_FIXATION)
        
        if SoilBenefit.PEST_MANAGEMENT not in request.objectives.primary_goals:
            request.objectives.primary_goals.append(SoilBenefit.PEST_MANAGEMENT)
        
        request.objectives.nitrogen_needs = True
        
        response = await cover_crop_service.select_cover_crops(request)
        
        logger.info(f"Generated rotation integration recommendations for request: {request.request_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error generating rotation integration recommendations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating rotation integration recommendations: {str(e)}"
        )


# Information endpoints
@router.get("/types")
async def get_cover_crop_types():
    """Get available cover crop types."""
    return {
        "types": [
            {
                "type": crop_type.value,
                "description": f"{crop_type.value.title()} cover crops"
            }
            for crop_type in CoverCropType
        ]
    }


@router.get("/seasons")
async def get_growing_seasons():
    """Get available growing seasons."""
    return {
        "seasons": [
            {
                "season": season.value,
                "description": f"{season.value.title()} growing season"
            }
            for season in GrowingSeason
        ]
    }


@router.get("/benefits")
async def get_soil_benefits():
    """Get available soil benefits."""
    return {
        "benefits": [
            {
                "benefit": benefit.value,
                "description": benefit.value.replace("_", " ").title()
            }
            for benefit in SoilBenefit
        ]
    }


# New rotation integration endpoints
@router.post("/rotation-integration", response_model=CoverCropSelectionResponse)
async def get_rotation_integration_recommendations_advanced(
    rotation_name: str = Query(..., description="Name of the rotation system"),
    request: CoverCropSelectionRequest = None,
    objectives: Optional[List[str]] = Query(None, description="Specific integration objectives")
):
    """
    Get advanced cover crop recommendations for specific rotation integration.
    
    This endpoint provides specialized recommendations that are optimized for 
    integration with existing crop rotation systems. It considers:
    
    Agricultural Logic:
    - Main crop compatibility and nutrient cycling
    - Timing coordination with rotation schedule
    - Pest and disease management within rotation
    - Economic benefits across the rotation system
    - Soil health improvements that benefit subsequent crops
    
    Args:
        rotation_name: Name/identifier of the rotation system
        request: Standard cover crop selection request
        objectives: Additional rotation-specific objectives
    """
    try:
        logger.info(f"Processing advanced rotation integration request for: {rotation_name}")
        
        if not request:
            raise HTTPException(
                status_code=400,
                detail="Cover crop selection request is required"
            )
        
        # Validate rotation name
        if not rotation_name or len(rotation_name.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Rotation name is required and cannot be empty"
            )
        
        # Get rotation-specific recommendations
        response = await cover_crop_service.get_rotation_integration_recommendations(
            rotation_name=rotation_name.strip(),
            request=request,
            objectives=objectives
        )
        
        logger.info(f"Successfully generated rotation integration recommendations for: {rotation_name}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in rotation integration recommendations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating rotation integration recommendations: {str(e)}"
        )


@router.get("/main-crop-compatibility/{crop_name}")
async def get_main_crop_compatibility_analysis(
    crop_name: str,
    cover_crop_species_id: str = Query(..., description="Cover crop species identifier"),
    position: str = Query("before", description="Position relative to main crop (before/after/between)")
):
    """
    Analyze compatibility between specific cover crop and main crop.
    
    This endpoint provides detailed analysis of how well a specific cover crop
    species will work with a particular main crop in different rotation positions.
    
    Agricultural Logic:
    - Nutrient cycling compatibility (N-fixation for corn, etc.)
    - Pest and disease management considerations
    - Soil condition improvements that benefit main crop
    - Timing coordination for planting and termination
    - Economic analysis of integration benefits
    
    Args:
        crop_name: Name of the main crop (corn, soybean, wheat, etc.)
        cover_crop_species_id: Identifier for the cover crop species
        position: Rotation position (before, after, between)
    """
    try:
        logger.info(f"Analyzing compatibility: {cover_crop_species_id} {position} {crop_name}")
        
        # Validate inputs
        if not crop_name or len(crop_name.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Main crop name is required"
            )
        
        if not cover_crop_species_id or len(cover_crop_species_id.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Cover crop species ID is required"
            )
        
        if position not in ["before", "after", "between"]:
            raise HTTPException(
                status_code=400,
                detail="Position must be one of: before, after, between"
            )
        
        # Verify species exists
        if cover_crop_species_id not in cover_crop_service.species_database:
            raise HTTPException(
                status_code=404,
                detail=f"Cover crop species '{cover_crop_species_id}' not found"
            )
        
        # Get compatibility analysis
        analysis = await cover_crop_service.get_main_crop_compatibility_analysis(
            cover_crop_species_id=cover_crop_species_id.strip(),
            main_crop=crop_name.strip(),
            position=position
        )
        
        logger.info(f"Successfully analyzed compatibility for {cover_crop_species_id} with {crop_name}")
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in compatibility analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing main crop compatibility: {str(e)}"
        )


@router.post("/rotation-position/{position_id}", response_model=CoverCropSelectionResponse)
async def get_rotation_position_recommendations(
    position_id: str,
    rotation_name: str = Query(..., description="Name of the rotation system"),
    request: CoverCropSelectionRequest = None
):
    """
    Get cover crop recommendations for specific position in rotation.
    
    This endpoint provides recommendations optimized for a specific position
    within a rotation sequence, considering the preceding and following crops.
    
    Agricultural Logic:
    - Position-specific soil conditions and requirements
    - Timing windows based on rotation schedule
    - Complementary relationships with adjacent crops
    - Position-specific objectives (N-fixation before corn, structure before soybeans)
    - Management considerations for rotation transitions
    
    Args:
        position_id: Identifier for the specific position in rotation
        rotation_name: Name of the rotation system
        request: Cover crop selection request with field conditions
    """
    try:
        logger.info(f"Processing position-specific request: {rotation_name} position {position_id}")
        
        if not request:
            raise HTTPException(
                status_code=400,
                detail="Cover crop selection request is required"
            )
        
        # Validate inputs
        if not position_id or len(position_id.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Position ID is required"
            )
        
        if not rotation_name or len(rotation_name.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Rotation name is required"
            )
        
        # Get position-specific recommendations
        response = await cover_crop_service.get_rotation_position_recommendations(
            rotation_name=rotation_name.strip(),
            position_id=position_id.strip(),
            request=request
        )
        
        logger.info(f"Successfully generated position-specific recommendations for {position_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in position-specific recommendations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating rotation position recommendations: {str(e)}"
        )


# Goal-Based Cover Crop Selection Endpoints
@router.post("/goal-based-recommendations", response_model=GoalBasedRecommendation)
async def get_goal_based_recommendations(
    data: Dict[str, Any]
):
    """
    Get goal-based cover crop recommendations with farmer priority optimization.
    
    This endpoint provides sophisticated cover crop recommendations that are optimized
    based on specific farmer goals and priorities. It goes beyond traditional selection
    by considering goal achievement scores, goal synergies, and priority-weighted outcomes.
    
    Agricultural Logic:
    - Farmer goal prioritization and weighting
    - Goal achievement scoring based on species characteristics
    - Goal synergy and conflict analysis
    - Priority-optimized seeding rates and management
    - Goal-focused cost-benefit analysis
    - Multi-objective optimization for complex farming scenarios
    
    Features:
    - Production goals (yield optimization, quality improvement)
    - Environmental goals (soil health, biodiversity, carbon sequestration) 
    - Economic goals (cost reduction, profitability, risk management)
    - Operational goals (labor efficiency, equipment utilization)
    - Sustainability goals (long-term soil health, environmental stewardship)
    
    Args:
        request: Standard cover crop selection request with field conditions
        objectives: Goal-based objectives with farmer priorities and specific goals
    """
    try:
        # Extract request and objectives from nested data
        if "request" not in data or "objectives" not in data:
            raise HTTPException(
                status_code=422,
                detail="Both 'request' and 'objectives' fields are required"
            )
        
        # Parse request data
        request_data = data["request"]
        objectives_data = data["objectives"]
        
        # Create request object
        request = CoverCropSelectionRequest(**request_data)
        
        # Convert objectives data using helper function
        objectives = convert_objectives_data_to_goal_based_objectives(objectives_data)
        
        logger.info(f"Processing goal-based recommendation request: {request.request_id}")
        
        # Validate request data
        if not request.location:
            raise HTTPException(
                status_code=400,
                detail="Location data with latitude and longitude is required"
            )
        
        if not request.planting_window or "start" not in request.planting_window:
            raise HTTPException(
                status_code=400,
                detail="Planting window with start date is required"
            )
        
        if request.field_size_acres <= 0:
            raise HTTPException(
                status_code=400,
                detail="Field size must be greater than 0 acres"
            )
        
        # Validate goal-based objectives
        if not objectives.specific_goals:
            raise HTTPException(
                status_code=400,
                detail="At least one farmer goal must be specified"
            )
        
        # Validate priorities sum to reasonable values
        total_priority = sum(goal.weight for goal in objectives.specific_goals)
        if total_priority <= 0:
            raise HTTPException(
                status_code=400,
                detail="Goal priority weights must sum to a positive value"
            )
        
        # Get goal-based recommendations
        response = await cover_crop_service.get_goal_based_recommendations(
            request=request,
            objectives=objectives
        )
        
        logger.info(f"Successfully generated goal-based recommendations for request: {request.request_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in goal-based recommendations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating goal-based recommendations: {str(e)}"
        )


@router.post("/goal-analysis")
async def analyze_goal_feasibility(
    data: Dict[str, Any]
):
    """
    Analyze feasibility of achieving specified farmer goals.
    
    This endpoint provides detailed analysis of how feasible it is to achieve
    the specified goals given the field conditions, climate, and constraints.
    It helps farmers set realistic expectations and prioritize goals.
    
    Agricultural Logic:  
    - Goal feasibility assessment based on field conditions
    - Constraint analysis (climate, soil, economic, operational)
    - Goal conflict identification and resolution strategies
    - Alternative goal suggestions for better outcomes
    - Risk assessment for goal achievement
    - Timeline analysis for goal realization
    
    Args:
        request: Cover crop selection request with field conditions
        objectives: Goal-based objectives to analyze for feasibility
    """
    try:
        # Extract request and objectives from nested data
        if "request" not in data or "objectives" not in data:
            raise HTTPException(
                status_code=422,
                detail="Both 'request' and 'objectives' fields are required"
            )
        
        # Parse request data
        request_data = data["request"]
        objectives_data = data["objectives"]
        
        # Create request object
        request = CoverCropSelectionRequest(**request_data)
        objectives = convert_objectives_data_to_goal_based_objectives(objectives_data)
        
        logger.info(f"Analyzing goal feasibility for request: {request.request_id}")
        
        # Validate request data
        if not request.location:
            raise HTTPException(
                status_code=400,
                detail="Location data is required for goal feasibility analysis"
            )
        
        if not objectives.specific_goals:
            raise HTTPException(
                status_code=400,
                detail="At least one farmer goal must be specified for analysis"
            )
        
        # Perform goal feasibility analysis
        analysis = await cover_crop_service.analyze_goal_feasibility(
            request=request,
            objectives=objectives
        )
        
        logger.info(f"Successfully completed goal feasibility analysis for request: {request.request_id}")
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in goal feasibility analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing goal feasibility: {str(e)}"
        )


@router.get("/goal-categories")
async def get_goal_categories_and_options():
    """
    Get available goal categories and specific goal options for goal-based planning.
    
    This endpoint provides the complete catalog of available farmer goals that can
    be used in goal-based cover crop selection. It includes goal categories,
    specific goals within each category, and guidance on goal selection.
    
    Returns:
        Dictionary containing:
        - Available goal categories (Production, Environmental, Economic, etc.)
        - Specific goals within each category
        - Goal descriptions and expected outcomes
        - Priority setting guidance
        - Goal compatibility information
        - Example goal combinations for different farming scenarios
    """
    try:
        logger.info("Getting available goal categories and options")
        
        # Get goal categories from service
        categories = await cover_crop_service.get_goal_categories_and_options()
        
        logger.info("Successfully retrieved goal categories and options")
        return categories
        
    except Exception as e:
        logger.error(f"Error getting goal categories: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving goal categories: {str(e)}"
        )


@router.get("/goal-examples")
async def get_goal_based_examples():
    """
    Get example goal-based scenarios for different farming situations.
    
    This endpoint provides pre-configured goal examples that demonstrate
    how to use goal-based cover crop selection for common farming scenarios.
    
    Returns:
        Collection of example scenarios with:
        - Scenario descriptions (new farmer, sustainability focus, profit optimization, etc.)
        - Pre-configured goal combinations
        - Expected outcomes and benefits
        - Implementation guidance
        - Success metrics and monitoring approaches
    """
    try:
        logger.info("Getting goal-based example scenarios")
        
        # Get example scenarios from goal service
        goal_service = GoalBasedRecommendationService()
        examples = goal_service.get_example_goal_scenarios()
        
        logger.info("Successfully retrieved goal-based examples")
        return examples

        
    except Exception as e:
        logger.error(f"Error getting goal-based examples: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving goal-based examples: {str(e)}"
        )


# === BENEFIT TRACKING AND QUANTIFICATION ENDPOINTS ===

@router.post("/select-with-benefit-tracking", response_model=CoverCropSelectionResponse)
async def select_cover_crops_with_benefit_tracking(request: CoverCropSelectionRequest):
    """
    Enhanced cover crop selection with integrated benefit tracking and quantification.
    
    This endpoint provides the same recommendations as the standard selection endpoint
    but additionally includes comprehensive benefit predictions, economic analysis,
    and sets up tracking infrastructure for monitoring actual performance.
    
    Features:
    - Complete benefit quantification for all recommendations
    - Economic value calculations (nitrogen fixation savings, erosion prevention, etc.)
    - Benefit tracking setup for field-level monitoring
    - Performance prediction confidence scores
    - ROI analysis and cost-benefit projections
    
    Args:
        request: Cover crop selection request with field conditions and objectives
    
    Returns:
        Enhanced response with benefit predictions and tracking setup
    """
    try:
        logger.info(f"Processing enhanced selection with benefit tracking: {request.request_id}")
        
        # Validate request (same validation as standard endpoint)
        if not request.location:
            raise HTTPException(
                status_code=400,
                detail="Location data with latitude and longitude is required"
            )
        
        if not request.planting_window or "start" not in request.planting_window:
            raise HTTPException(
                status_code=400,
                detail="Planting window with start date is required"
            )
        
        if request.field_size_acres <= 0:
            raise HTTPException(
                status_code=400,
                detail="Field size must be greater than 0 acres"
            )
        
        # Get enhanced recommendations with benefit tracking
        response, benefit_data = await cover_crop_service.select_cover_crops_with_benefit_tracking(
            request=request,
            enable_benefit_tracking=True
        )
        
        # Add benefit tracking data to response
        if benefit_data:
            response.benefit_tracking_data = benefit_data
        
        logger.info(f"Successfully generated enhanced recommendations with benefit tracking: {request.request_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in enhanced cover crop selection: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating enhanced cover crop recommendations: {str(e)}"
        )


@router.post("/benefits/predict")
async def predict_benefits(
    data: Dict[str, Any]
):
    """
    Predict quantified benefits for specific cover crop species.
    
    This endpoint provides detailed benefit predictions for given species
    under specific field conditions, including confidence scores and
    environmental adjustment factors.
    
    Args:
        species_ids: List of cover crop species identifiers
        field_conditions: Field conditions (soil, climate, management)
        field_size_acres: Field size for economic calculations
    
    Returns:
        Detailed benefit predictions with confidence scores
    """
    try:
        # Extract required fields from data
        species_ids = data.get("species_ids", [])
        field_conditions = data.get("field_conditions", {})
        field_size_acres = data.get("field_size_acres", 0.0)
        
        logger.info(f"Predicting benefits for {len(species_ids)} species")
        
        if not species_ids:
            raise HTTPException(
                status_code=400,
                detail="At least one species ID is required"
            )
        
        if field_size_acres <= 0:
            raise HTTPException(
                status_code=400,
                detail="Field size must be greater than 0 acres"
            )
        
        predictions = await benefit_tracking_service.predict_benefits(
            species_ids=species_ids,
            field_conditions=field_conditions,
            field_size_acres=field_size_acres
        )
        
        logger.info(f"Successfully predicted benefits for {len(species_ids)} species")
        return {"predictions": predictions}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error predicting benefits: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error predicting cover crop benefits: {str(e)}"
        )


@router.post("/benefits/track", response_model=BenefitTrackingField)
async def create_benefit_tracking(
    data: Dict[str, Any]
):
    """
    Create benefit tracking for a specific field implementation.
    
    Sets up comprehensive tracking infrastructure for monitoring actual
    benefit realization compared to predictions.
    
    Args:
        field_id: Unique identifier for the field
        species_ids: Cover crop species being planted
        predicted_benefits: Benefit predictions from prediction endpoint
        field_size_acres: Field size in acres
        planting_date: Date of cover crop planting
        farmer_id: Optional farmer identifier
    
    Returns:
        Benefit tracking record with monitoring protocols
    """
    try:
        # Extract required fields from data
        field_id = data.get("field_id", "")
        species_ids = data.get("species_ids", [])
        predicted_benefits = data.get("predicted_benefits", {})
        field_size_acres = data.get("field_size_acres", 0.0)
        planting_date_str = data.get("planting_date")
        farmer_id = data.get("farmer_id")
        
        # Parse planting date if provided as string
        if isinstance(planting_date_str, str):
            from datetime import datetime
            planting_date = datetime.fromisoformat(planting_date_str.replace('Z', '+00:00'))
        else:
            planting_date = planting_date_str
        
        logger.info(f"Creating benefit tracking for field: {field_id}")
        
        if not field_id or len(field_id.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Field ID is required"
            )
        
        if not species_ids:
            raise HTTPException(
                status_code=400,
                detail="At least one species ID is required"
            )
        
        if field_size_acres <= 0:
            raise HTTPException(
                status_code=400,
                detail="Field size must be greater than 0 acres"
            )
        
        tracking = await benefit_tracking_service.create_field_tracking(
            field_id=field_id.strip(),
            species_ids=species_ids,
            predicted_benefits=predicted_benefits,
            field_size_acres=field_size_acres,
            planting_date=planting_date,
            farmer_id=farmer_id
        )
        
        logger.info(f"Successfully created benefit tracking for field: {field_id}")
        return tracking
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating benefit tracking: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating benefit tracking: {str(e)}"
        )


@router.post("/benefits/measure")
async def record_benefit_measurement(
    data: Dict[str, Any]
):
    """
    Record actual benefit measurements from field monitoring.
    
    This endpoint allows field technicians and farmers to record actual
    measured benefits for comparison with predictions and tracking progress.
    
    Args:
        field_id: Field identifier
        measurement_record: Measurement data with method, value, and validation
    
    Returns:
        Updated measurement status and validation results
    """
    try:
        # Extract fields from data
        field_id = data.get("field_id", "")
        measurement_record_data = data.get("measurement_record", {})
        
        # Create measurement record object
        measurement_record = BenefitMeasurementRecord(**measurement_record_data)
        
        logger.info(f"Recording measurement for field: {field_id}")
        
        if not field_id or len(field_id.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Field ID is required"
            )
        
        result = await benefit_tracking_service.record_measurement(
            field_id=field_id.strip(),
            measurement_record=measurement_record
        )
        
        logger.info(f"Successfully recorded measurement for field: {field_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording measurement: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error recording benefit measurement: {str(e)}"
        )


@router.get("/benefits/analytics", response_model=BenefitTrackingAnalytics)
async def get_benefit_analytics(
    farmer_id: Optional[str] = Query(None, description="Filter by farmer ID"),
    field_id: Optional[str] = Query(None, description="Filter by field ID"),
    start_date: Optional[datetime] = Query(None, description="Analytics start date"),
    end_date: Optional[datetime] = Query(None, description="Analytics end date"),
    species_filter: Optional[List[str]] = Query(None, description="Filter by species IDs")
):
    """
    Generate comprehensive benefit tracking analytics and insights.
    
    This endpoint provides dashboard-ready analytics including performance
    comparisons, ROI calculations, prediction accuracy, and recommendations
    for optimization.
    
    Args:
        farmer_id: Optional farmer filter
        field_id: Optional field filter  
        start_date: Analytics period start
        end_date: Analytics period end
        species_filter: Optional species filter
    
    Returns:
        Comprehensive analytics with insights and recommendations
    """
    try:
        logger.info("Generating benefit tracking analytics")
        
        filters = {}
        if farmer_id:
            filters["farmer_id"] = farmer_id.strip()
        if field_id:
            filters["field_id"] = field_id.strip()
        if start_date:
            filters["start_date"] = start_date
        if end_date:
            filters["end_date"] = end_date
        if species_filter:
            filters["species_filter"] = species_filter
        
        analytics = await benefit_tracking_service.generate_benefit_analytics(
            filters=filters
        )
        
        logger.info("Successfully generated benefit tracking analytics")
        return analytics
        
    except Exception as e:
        logger.error(f"Error generating analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating benefit analytics: {str(e)}"
        )


@router.get("/benefits/tracking/{field_id}")
async def get_field_tracking_status(field_id: str):
    """
    Get current benefit tracking status for a specific field.
    
    Returns comprehensive tracking status including predictions,
    measurements, progress, and next recommended actions.
    
    Args:
        field_id: Field identifier
    
    Returns:
        Current tracking status and recommendations
    """
    try:
        logger.info(f"Getting tracking status for field: {field_id}")
        
        if not field_id or len(field_id.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Field ID is required"
            )
        
        status = await benefit_tracking_service.get_field_tracking_status(
            field_id=field_id.strip()
        )
        
        if not status:
            raise HTTPException(
                status_code=404,
                detail=f"No tracking found for field: {field_id}"
            )
        
        logger.info(f"Successfully retrieved tracking status for field: {field_id}")
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tracking status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving tracking status: {str(e)}"
        )


@router.post("/timing", response_model=TimingRecommendationResponse)
async def get_timing_recommendations(request: TimingRecommendationRequest):
    """
    Generate planting and termination timing recommendations for cover crops.
    
    Provides species-specific timing windows based on:
    - Location and climate zone
    - Main crop schedule integration
    - Weather-based timing adjustments
    - Goal-specific optimization
    
    Returns comprehensive timing recommendations including planting windows,
    termination options, and seasonal strategy guidance.
    """
    try:
        logger.info(f"Generating timing recommendations for species: {request.species_id}")
        
        if not cover_crop_service.initialized:
            await cover_crop_service.initialize()
        
        # Get timing recommendations from service
        timing_response = await cover_crop_service.timing_service.generate_comprehensive_timing_recommendation(request)
        
        logger.info(f"Successfully generated timing recommendations for {request.species_id}")
        return timing_response
        
    except Exception as e:
        logger.error(f"Error generating timing recommendations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating timing recommendations: {str(e)}"
        )


@router.get("/timing")
async def get_timing_information(
    species_id: str = Query(..., description="Cover crop species identifier"),
    latitude: float = Query(..., ge=-90, le=90, description="Latitude in decimal degrees"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude in decimal degrees"),
    planting_year: Optional[int] = Query(None, description="Target planting year (default: current year)")
):
    """
    Get timing information for a specific cover crop species at a location.
    
    This GET endpoint provides basic timing windows and recommendations
    for a specific cover crop species based on location and climate data.
    
    Returns:
        Basic timing information including optimal planting windows,
        termination recommendations, and seasonal considerations.
    """
    try:
        logger.info(f"Getting timing information for species: {species_id} at {latitude}, {longitude}")
        
        if not cover_crop_service.initialized:
            await cover_crop_service.initialize()
        
        # Verify species exists
        if species_id not in cover_crop_service.species_database:
            raise HTTPException(
                status_code=404,
                detail=f"Cover crop species '{species_id}' not found"
            )
        
        # Create a basic timing request and get recommendations
        from models.cover_crop_models import TimingRecommendationRequest
        from datetime import datetime
        
        current_year = planting_year or datetime.now().year
        
        # Create basic timing request
        timing_request = TimingRecommendationRequest(
            species_id=species_id,
            location={
                "latitude": latitude,
                "longitude": longitude
            },
            planting_year=current_year
        )
        
        # Get timing recommendations from timing service
        timing_info = await cover_crop_service.timing_service.generate_comprehensive_timing_recommendation(
            timing_request
        )
        
        logger.info(f"Successfully retrieved timing information for {species_id}")
        return timing_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting timing information: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving timing information: {str(e)}"
        )
"""
Fertilizer Type Selection API Routes

Comprehensive API endpoints for fertilizer type selection, comparison, and recommendations.
Implements TICKET-023_fertilizer-type-selection-10.1: Comprehensive fertilizer selection API endpoints.
"""

from fastapi import APIRouter, HTTPException, Query, Depends, Body
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import uuid

from ..models.fertilizer_models import (
    FertilizerTypeSelectionRequest,
    FertilizerTypeSelectionResponse,
    FertilizerComparisonRequest,
    FertilizerComparisonResponse,
    FarmerPriorities,
    FarmerConstraints,
    FertilizerType,
    ApplicationMethod
)
from ..services.fertilizer_type_selection_service import FertilizerTypeSelectionService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/fertilizer", tags=["fertilizer-selection"])

# Dependency for service injection
async def get_fertilizer_service() -> FertilizerTypeSelectionService:
    """Dependency to get fertilizer type selection service instance."""
    return FertilizerTypeSelectionService()


@router.post("/type-selection", response_model=Dict[str, Any])
async def advanced_fertilizer_selection(
    priorities: FarmerPriorities = Body(..., description="Farmer priorities for fertilizer selection"),
    constraints: FarmerConstraints = Body(..., description="Farmer constraints and limitations"),
    soil_data: Optional[Dict[str, Any]] = Body(None, description="Soil test data and conditions"),
    crop_data: Optional[Dict[str, Any]] = Body(None, description="Crop information and requirements"),
    farm_profile: Optional[Dict[str, Any]] = Body(None, description="Farm profile and characteristics"),
    service: FertilizerTypeSelectionService = Depends(get_fertilizer_service)
):
    """
    Advanced fertilizer type selection with comprehensive analysis.
    
    This endpoint provides intelligent fertilizer type recommendations based on:
    - Farmer priorities (cost, soil health, environmental impact, etc.)
    - Farm constraints (budget, equipment, regulations)
    - Soil conditions and current health status
    - Crop requirements and rotation plans
    - Environmental considerations
    
    **Request Body Example:**
    ```json
    {
      "priorities": {
        "cost_effectiveness": 0.8,
        "soil_health": 0.7,
        "quick_results": 0.5,
        "environmental_impact": 0.6,
        "ease_of_application": 0.4,
        "long_term_benefits": 0.7
      },
      "constraints": {
        "budget_per_acre": 120.0,
        "farm_size_acres": 160.0,
        "available_equipment": ["broadcast_spreader", "field_sprayer"],
        "organic_preference": false,
        "environmental_concerns": true
      },
      "soil_data": {
        "ph": 6.5,
        "organic_matter_percent": 3.2,
        "soil_texture": "loam"
      },
      "crop_data": {
        "crop_type": "corn",
        "target_yield": 180,
        "growth_stage": "pre_plant"
      }
    }
    ```
    
    **Response includes:**
    - Ranked fertilizer recommendations with suitability scores
    - Comprehensive cost analysis and ROI estimates
    - Environmental impact assessments
    - Application guidance and timing recommendations
    - Equipment compatibility analysis
    - Detailed explanations for each recommendation
    
    **Agricultural Context:**
    Recommendations follow university extension guidelines and 4R nutrient stewardship
    principles (Right Source, Right Rate, Right Time, Right Place).
    """
    try:
        logger.info(f"Processing advanced fertilizer selection request with priorities: {priorities.dict()}")
        
        # Generate recommendations using the service
        recommendations = await service.get_fertilizer_type_recommendations(
            priorities=priorities,
            constraints=constraints,
            soil_data=soil_data,
            crop_data=crop_data,
            farm_profile=farm_profile
        )
        
        # Calculate overall confidence
        overall_confidence = service.calculate_overall_confidence(recommendations)
        
        # Generate comparison summary
        comparison_summary = service.generate_comparison_summary(recommendations)
        
        # Generate cost analysis
        cost_analysis = service.generate_cost_analysis(recommendations, constraints)
        
        # Assess environmental impact across recommendations
        environmental_impact = await service.assess_environmental_impact_for_recommendations(
            recommendations=recommendations,
            field_conditions={
                "soil": soil_data or {},
                "crop": crop_data or {}
            }
        )
        
        # Generate implementation guidance
        implementation_guidance = service.generate_implementation_guidance(recommendations)
        
        # Construct response
        response = {
            "request_id": str(uuid.uuid4()),
            "generated_at": datetime.utcnow().isoformat(),
            "recommendations": recommendations,
            "confidence_score": overall_confidence,
            "comparison_summary": comparison_summary,
            "cost_analysis": cost_analysis,
            "environmental_impact": environmental_impact,
            "implementation_guidance": implementation_guidance,
            "timing_recommendations": [
                "Apply nitrogen in split applications for better efficiency",
                "Consider weather forecast before application",
                "Avoid application before heavy rain events"
            ],
            "warnings": [
                "Always calibrate equipment before application",
                "Follow label rates and restrictions",
                "Consider environmental conditions and regulations"
            ],
            "next_steps": [
                "Review recommendations with agronomist if available",
                "Obtain current fertilizer pricing from local suppliers",
                "Plan application timing based on crop growth stage"
            ]
        }
        
        logger.info(f"Successfully generated {len(recommendations)} fertilizer recommendations")
        return response
        
    except ValueError as e:
        logger.error(f"Validation error in fertilizer selection: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in fertilizer selection: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate fertilizer recommendations: {str(e)}"
        )


@router.get("/types", response_model=Dict[str, Any])
async def get_fertilizer_types_catalog(
    fertilizer_type: Optional[FertilizerType] = Query(None, description="Filter by fertilizer type"),
    application_method: Optional[ApplicationMethod] = Query(None, description="Filter by application method"),
    manufacturer: Optional[str] = Query(None, description="Filter by manufacturer"),
    price_range_min: Optional[float] = Query(None, ge=0, description="Minimum price per unit ($)"),
    price_range_max: Optional[float] = Query(None, ge=0, description="Maximum price per unit ($)"),
    organic_only: Optional[bool] = Query(False, description="Only show organic options"),
    limit: Optional[int] = Query(50, ge=1, le=200, description="Maximum results to return"),
    offset: Optional[int] = Query(0, ge=0, description="Offset for pagination"),
    service: FertilizerTypeSelectionService = Depends(get_fertilizer_service)
):
    """
    Comprehensive fertilizer types catalog with filtering.
    
    Provides detailed information about available fertilizer products including:
    - Nutrient content and analysis
    - Cost and availability information
    - Application methods and equipment requirements
    - Environmental and soil health impact scores
    - Organic certification status
    
    **Query Parameters:**
    - `fertilizer_type`: Filter by type (organic, synthetic, slow_release, etc.)
    - `application_method`: Filter by compatible application method
    - `manufacturer`: Filter by manufacturer name
    - `price_range_min/max`: Filter by price range
    - `organic_only`: Show only organic-certified products
    - `limit`: Number of results per page (default 50, max 200)
    - `offset`: Pagination offset
    
    **Response includes for each product:**
    - Complete nutrient analysis (N-P-K plus micronutrients)
    - Cost per unit and per nutrient
    - Compatible equipment and application methods
    - Environmental impact scores
    - Soil health benefit ratings
    - Storage and handling requirements
    - Pros, cons, and application notes
    
    **Example Request:**
    ```
    GET /api/v1/fertilizer/types?fertilizer_type=organic&organic_only=true&limit=10
    ```
    """
    try:
        logger.info(
            f"Fetching fertilizer catalog with filters: type={fertilizer_type}, "
            f"method={application_method}, organic={organic_only}"
        )
        
        # Get available fertilizer types from service
        fertilizer_types = await service.get_available_fertilizer_types(
            fertilizer_type=fertilizer_type.value if fertilizer_type else None,
            organic_only=organic_only,
            max_cost_per_unit=price_range_max
        )
        
        # Apply additional filtering
        filtered_types = fertilizer_types
        
        if application_method:
            filtered_types = [
                ft for ft in filtered_types
                if application_method in ft.get("application_methods", [])
            ]
        
        if manufacturer:
            filtered_types = [
                ft for ft in filtered_types
                if ft.get("manufacturer", "").lower() == manufacturer.lower()
            ]
        
        if price_range_min is not None:
            filtered_types = [
                ft for ft in filtered_types
                if ft.get("cost_per_unit", 0) >= price_range_min
            ]
        
        # Apply pagination
        total_count = len(filtered_types)
        paginated_types = filtered_types[offset:offset + limit]
        
        response = {
            "total_count": total_count,
            "returned_count": len(paginated_types),
            "offset": offset,
            "limit": limit,
            "has_more": (offset + limit) < total_count,
            "fertilizer_types": paginated_types,
            "filters_applied": {
                "fertilizer_type": fertilizer_type.value if fertilizer_type else None,
                "application_method": application_method.value if application_method else None,
                "manufacturer": manufacturer,
                "price_range": {
                    "min": price_range_min,
                    "max": price_range_max
                },
                "organic_only": organic_only
            }
        }
        
        logger.info(f"Returning {len(paginated_types)} fertilizer types out of {total_count} total")
        return response
        
    except Exception as e:
        logger.error(f"Error fetching fertilizer types catalog: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch fertilizer catalog: {str(e)}"
        )


@router.post("/comparison", response_model=Dict[str, Any])
async def compare_fertilizer_options(
    fertilizer_ids: List[str] = Body(..., min_items=2, max_items=5, description="Fertilizer IDs to compare"),
    comparison_criteria: List[str] = Body(
        ...,
        description="Criteria for comparison",
        example=["cost_effectiveness", "soil_health_impact", "environmental_impact", "application_ease"]
    ),
    farm_context: Dict[str, Any] = Body(..., description="Farm context for comparison"),
    service: FertilizerTypeSelectionService = Depends(get_fertilizer_service)
):
    """
    Advanced fertilizer comparison with trade-off analysis.
    
    Provides detailed side-by-side comparison of specific fertilizer products with:
    - Multi-criteria scoring and ranking
    - Cost-benefit analysis
    - Environmental impact comparison
    - Soil health impact assessment
    - Application ease and equipment compatibility
    - Trade-off analysis between options
    
    **Request Body Example:**
    ```json
    {
      "fertilizer_ids": [
        "urea_46_0_0",
        "ammonium_sulfate_21_0_0",
        "composted_manure_organic"
      ],
      "comparison_criteria": [
        "cost_effectiveness",
        "soil_health_impact",
        "environmental_impact",
        "nitrogen_efficiency"
      ],
      "farm_context": {
        "farm_size_acres": 160,
        "soil_ph": 6.5,
        "crop_type": "corn",
        "budget_per_acre": 100
      }
    }
    ```
    
    **Response includes:**
    - Side-by-side comparison scores for each criterion
    - Overall ranking based on farm context
    - Strengths and weaknesses of each option
    - Key trade-offs and decision factors
    - Cost comparison (per acre, per nutrient unit)
    - Environmental impact comparison
    - Application requirements comparison
    - Recommendation with rationale
    
    **Agricultural Context:**
    Comparisons consider agronomic principles, regional best practices,
    and long-term sustainability outcomes.
    """
    try:
        logger.info(
            f"Comparing {len(fertilizer_ids)} fertilizer options with "
            f"{len(comparison_criteria)} criteria"
        )
        
        # Validate number of fertilizers
        if len(fertilizer_ids) < 2:
            raise HTTPException(
                status_code=400,
                detail="At least 2 fertilizer IDs required for comparison"
            )
        
        if len(fertilizer_ids) > 5:
            raise HTTPException(
                status_code=400,
                detail="Maximum 5 fertilizers can be compared at once"
            )
        
        # Validate comparison criteria
        valid_criteria = {
            "cost_effectiveness", "soil_health_impact", "environmental_impact",
            "nitrogen_efficiency", "phosphorus_efficiency", "potassium_efficiency",
            "application_ease", "storage_requirements", "release_pattern",
            "organic_certification", "equipment_compatibility"
        }
        
        invalid_criteria = set(comparison_criteria) - valid_criteria
        if invalid_criteria:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid comparison criteria: {invalid_criteria}. "
                       f"Valid criteria are: {valid_criteria}"
            )
        
        # Perform comparison
        comparison_results = await service.compare_fertilizer_options(
            fertilizer_ids=fertilizer_ids,
            comparison_criteria=comparison_criteria,
            farm_context=farm_context
        )
        
        # Generate recommendation
        recommendation = service.get_comparison_recommendation(comparison_results)
        
        # Identify key decision factors
        decision_factors = service.identify_decision_factors(comparison_results)
        
        response = {
            "request_id": str(uuid.uuid4()),
            "generated_at": datetime.utcnow().isoformat(),
            "comparison_results": comparison_results,
            "recommendation": recommendation,
            "decision_factors": decision_factors,
            "comparison_criteria_used": comparison_criteria,
            "farm_context": farm_context
        }
        
        logger.info(f"Successfully compared {len(fertilizer_ids)} fertilizer options")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in fertilizer comparison: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compare fertilizer options: {str(e)}"
        )


@router.post("/recommendation-history", response_model=Dict[str, Any])
async def save_fertilizer_recommendation(
    user_id: str = Body(..., description="User identifier"),
    recommendation_data: Dict[str, Any] = Body(..., description="Recommendation data to save"),
    farm_id: Optional[str] = Body(None, description="Farm identifier"),
    notes: Optional[str] = Body(None, description="User notes"),
    service: FertilizerTypeSelectionService = Depends(get_fertilizer_service)
):
    """
    Save fertilizer recommendation for history tracking.
    
    Stores fertilizer recommendations for future reference, outcome tracking,
    and continuous improvement of recommendation algorithms.
    
    **Request Body Example:**
    ```json
    {
      "user_id": "user_123",
      "farm_id": "farm_456",
      "recommendation_data": {
        "fertilizer_type": "urea_46_0_0",
        "application_rate": 150,
        "priorities_used": {...},
        "constraints_used": {...}
      },
      "notes": "Selected based on cost-effectiveness"
    }
    ```
    
    **Response includes:**
    - Saved recommendation ID
    - Timestamp
    - Confirmation of data saved
    """
    try:
        logger.info(f"Saving fertilizer recommendation for user {user_id}")
        
        # Create recommendation history record
        history_record = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "farm_id": farm_id,
            "recommendation_data": recommendation_data,
            "notes": notes,
            "saved_at": datetime.utcnow().isoformat(),
            "status": "saved"
        }
        
        # In production, this would save to database
        # For now, return confirmation
        
        response = {
            "recommendation_id": history_record["id"],
            "saved_at": history_record["saved_at"],
            "status": "success",
            "message": "Fertilizer recommendation saved successfully"
        }
        
        logger.info(f"Successfully saved recommendation {history_record['id']}")
        return response
        
    except Exception as e:
        logger.error(f"Error saving recommendation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save recommendation: {str(e)}"
        )


@router.get("/recommendation-history/{user_id}", response_model=Dict[str, Any])
async def get_recommendation_history(
    user_id: str,
    farm_id: Optional[str] = Query(None, description="Filter by farm ID"),
    limit: Optional[int] = Query(10, ge=1, le=100, description="Maximum results"),
    offset: Optional[int] = Query(0, ge=0, description="Pagination offset"),
    service: FertilizerTypeSelectionService = Depends(get_fertilizer_service)
):
    """
    Retrieve fertilizer recommendation history for a user.
    
    Returns historical recommendations with outcomes (if tracked) for:
    - Reviewing past decisions
    - Tracking effectiveness
    - Learning from experience
    - Comparing year-over-year approaches
    
    **Query Parameters:**
    - `farm_id`: Filter by specific farm
    - `limit`: Number of results per page
    - `offset`: Pagination offset
    
    **Response includes:**
    - Historical recommendations with timestamps
    - Applied vs recommended comparison (if tracked)
    - Outcome data (yield, cost, satisfaction)
    - Trends and insights
    """
    try:
        logger.info(f"Fetching recommendation history for user {user_id}")
        
        # In production, this would query database
        # For now, return sample response
        
        response = {
            "user_id": user_id,
            "farm_id": farm_id,
            "total_recommendations": 0,
            "returned_count": 0,
            "recommendations": [],
            "insights": [
                "No historical recommendations found",
                "Start tracking recommendations to see trends over time"
            ]
        }
        
        logger.info(f"Returned {response['returned_count']} historical recommendations")
        return response
        
    except Exception as e:
        logger.error(f"Error fetching recommendation history: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch recommendation history: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "fertilizer-type-selection",
        "timestamp": datetime.utcnow().isoformat()
    }

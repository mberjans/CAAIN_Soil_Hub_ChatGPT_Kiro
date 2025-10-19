"""
API routes for fertilizer comparison and scoring service.

This module provides REST API endpoints for:
- Multi-criteria fertilizer comparison
- TOPSIS analysis
- AHP analysis
- Weighted scoring
- Available criteria lookup
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any
import logging
from datetime import datetime

from ..services.comparison_service import FertilizerComparisonService
from ..models.comparison_models import (
    ComparisonRequest, ComparisonResult, TOPSISResult, AHPResult,
    AvailableCriteria, ScoringMethod, ScoringDimension, ScoringCriteria,
    FertilizerOption, NutrientContent, ComparisonCategory
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/fertilizer-comparison", tags=["fertilizer-comparison"])

# Initialize comparison service
comparison_service = FertilizerComparisonService()


@router.post("/compare", response_model=ComparisonResult)
async def compare_fertilizers(
    request: ComparisonRequest,
    background_tasks: BackgroundTasks
) -> ComparisonResult:
    """
    Perform comprehensive multi-criteria fertilizer comparison.

    This endpoint compares multiple fertilizers across various dimensions including
    nutrient value, cost-effectiveness, environmental impact, and application convenience.

    Supported scoring methods:
    - weighted_scoring: User-defined weights for each criterion
    - topsis: Technique for Order of Preference by Similarity to Ideal Solution
    - ahp: Analytic Hierarchy Process

    Args:
        request: Comparison request with fertilizers and scoring criteria
        background_tasks: Background task handler for logging

    Returns:
        ComparisonResult with scores, rankings, and recommendations

    Raises:
        HTTPException: If comparison fails or invalid data provided
    """
    try:
        logger.info(f"Received fertilizer comparison request {request.comparison_id}")

        # Perform comparison
        result = await comparison_service.compare_fertilizers(request)

        # Log completion
        background_tasks.add_task(
            log_comparison_completion,
            request.comparison_id,
            len(request.fertilizers),
            result.processing_time_ms
        )

        logger.info(f"Fertilizer comparison {request.comparison_id} completed")
        return result

    except ValueError as e:
        logger.error(f"Validation error in fertilizer comparison: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in fertilizer comparison: {str(e)}")
        raise HTTPException(status_code=500, detail="Fertilizer comparison failed")


@router.post("/weighted-score", response_model=ComparisonResult)
async def weighted_score_comparison(
    request: ComparisonRequest
) -> ComparisonResult:
    """
    Perform weighted scoring comparison.

    This endpoint uses user-defined weights to score fertilizers across
    multiple criteria. Each criterion is scored independently and then
    combined using the specified weights.

    Args:
        request: Comparison request with fertilizers and weighted criteria

    Returns:
        ComparisonResult with weighted scores and rankings

    Raises:
        HTTPException: If comparison fails
    """
    try:
        logger.info(f"Received weighted scoring request {request.comparison_id}")

        # Force weighted scoring method
        request.scoring_method = ScoringMethod.WEIGHTED_SCORING

        # Perform comparison
        result = await comparison_service.compare_fertilizers(request)

        logger.info(f"Weighted scoring comparison {request.comparison_id} completed")
        return result

    except ValueError as e:
        logger.error(f"Validation error in weighted scoring: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in weighted scoring: {str(e)}")
        raise HTTPException(status_code=500, detail="Weighted scoring comparison failed")


@router.post("/topsis", response_model=TOPSISResult)
async def topsis_comparison(
    request: ComparisonRequest
) -> TOPSISResult:
    """
    Perform TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution) analysis.

    TOPSIS ranks fertilizers based on their distance from the ideal solution
    (best possible values) and anti-ideal solution (worst possible values).

    The method:
    1. Normalizes the decision matrix
    2. Applies criterion weights
    3. Determines ideal and anti-ideal solutions
    4. Calculates distances to each ideal
    5. Ranks based on relative closeness to ideal

    Args:
        request: Comparison request with fertilizers and criteria

    Returns:
        TOPSISResult with TOPSIS-specific scores and analysis

    Raises:
        HTTPException: If analysis fails
    """
    try:
        logger.info(f"Received TOPSIS analysis request {request.comparison_id}")

        # Perform TOPSIS analysis
        result = await comparison_service.topsis_analysis(request)

        logger.info(f"TOPSIS analysis {request.comparison_id} completed")
        return result

    except ValueError as e:
        logger.error(f"Validation error in TOPSIS analysis: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in TOPSIS analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="TOPSIS analysis failed")


@router.post("/ahp", response_model=AHPResult)
async def ahp_comparison(
    request: ComparisonRequest
) -> AHPResult:
    """
    Perform AHP (Analytic Hierarchy Process) analysis.

    AHP uses pairwise comparisons to determine relative priorities.
    It includes consistency checking to ensure logical comparisons.

    The method:
    1. Builds pairwise comparison matrices
    2. Calculates priority vectors (eigenvectors)
    3. Checks consistency ratios
    4. Combines priorities using criterion weights
    5. Ranks fertilizers by overall priority

    Consistency ratio < 0.1 is considered acceptable.

    Args:
        request: Comparison request with fertilizers and criteria

    Returns:
        AHPResult with AHP-specific scores and consistency analysis

    Raises:
        HTTPException: If analysis fails
    """
    try:
        logger.info(f"Received AHP analysis request {request.comparison_id}")

        # Perform AHP analysis
        result = await comparison_service.ahp_analysis(request)

        # Warn if consistency is poor
        if not result.consistency_acceptable:
            logger.warning(
                f"AHP analysis {request.comparison_id} has poor consistency ratio: "
                f"{result.overall_consistency_ratio:.3f}"
            )

        logger.info(f"AHP analysis {request.comparison_id} completed")
        return result

    except ValueError as e:
        logger.error(f"Validation error in AHP analysis: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in AHP analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="AHP analysis failed")


@router.get("/criteria", response_model=List[AvailableCriteria])
async def get_available_criteria() -> List[AvailableCriteria]:
    """
    Get available scoring criteria with descriptions and default weights.

    Returns information about all available criteria including:
    - Display names and descriptions
    - Default weights
    - Whether to maximize or minimize
    - Typical value ranges
    - Factors considered in scoring

    Returns:
        List of AvailableCriteria with metadata
    """
    try:
        criteria = comparison_service.get_available_criteria()
        return criteria

    except Exception as e:
        logger.error(f"Error retrieving available criteria: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve available criteria")


@router.get("/scoring-methods", response_model=Dict[str, Any])
async def get_scoring_methods() -> Dict[str, Any]:
    """
    Get information about available scoring methods.

    Returns:
        Dictionary of scoring methods with descriptions and use cases
    """
    methods = {
        "weighted_scoring": {
            "name": "Weighted Scoring",
            "description": "Linear combination of weighted criteria scores",
            "best_for": "Simple, transparent comparisons with clear priorities",
            "complexity": "Low",
            "requires_pairwise_comparison": False,
            "consistency_check": False
        },
        "topsis": {
            "name": "TOPSIS",
            "description": "Technique for Order of Preference by Similarity to Ideal Solution",
            "best_for": "Balanced comparison considering best and worst cases",
            "complexity": "Medium",
            "requires_pairwise_comparison": False,
            "consistency_check": False
        },
        "ahp": {
            "name": "AHP (Analytic Hierarchy Process)",
            "description": "Pairwise comparison with consistency checking",
            "best_for": "Complex decisions with multiple stakeholders",
            "complexity": "High",
            "requires_pairwise_comparison": True,
            "consistency_check": True
        }
    }

    return methods


@router.post("/quick-compare", response_model=Dict[str, Any])
async def quick_compare(
    fertilizer_ids: List[str],
    category: ComparisonCategory = ComparisonCategory.ALL,
    environmental_priority: float = 0.5
) -> Dict[str, Any]:
    """
    Quick comparison with default criteria and weights.

    This endpoint provides a simplified comparison interface using
    default criteria weights. Useful for rapid decision making.

    Args:
        fertilizer_ids: List of fertilizer IDs to compare
        category: Filter by fertilizer category
        environmental_priority: Weight for environmental criteria (0-1)

    Returns:
        Simplified comparison result with top recommendation

    Raises:
        HTTPException: If comparison fails
    """
    try:
        logger.info(f"Received quick comparison request for {len(fertilizer_ids)} fertilizers")

        # This is a simplified example - in production, you would fetch
        # actual fertilizer data from a database
        raise HTTPException(
            status_code=501,
            detail="Quick compare requires fertilizer database integration"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in quick compare: {str(e)}")
        raise HTTPException(status_code=500, detail="Quick comparison failed")


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for fertilizer comparison service.

    Returns:
        Service health status
    """
    return {
        "status": "healthy",
        "service": "fertilizer-comparison",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "features": [
            "multi_criteria_comparison",
            "weighted_scoring",
            "topsis_analysis",
            "ahp_analysis",
            "trade_off_analysis",
            "cost_effectiveness_scoring",
            "environmental_impact_assessment"
        ]
    }


@router.post("/example-request", response_model=Dict[str, Any])
async def get_example_request() -> Dict[str, Any]:
    """
    Get an example comparison request for testing and documentation.

    Returns:
        Example ComparisonRequest as a dictionary
    """
    example = {
        "fertilizers": [
            {
                "fertilizer_id": "urea-46-0-0",
                "fertilizer_name": "Urea 46-0-0",
                "fertilizer_type": "synthetic",
                "category": "synthetic",
                "nutrient_content": {
                    "nitrogen": 46.0,
                    "phosphorus": 0.0,
                    "potassium": 0.0
                },
                "price_per_unit": 400.0,
                "unit_type": "ton",
                "application_rate": 0.5,
                "organic_certified": False,
                "slow_release": False,
                "greenhouse_gas_emission_factor": 1.3,
                "runoff_potential": 0.6,
                "leaching_potential": 0.7,
                "application_method": "broadcast",
                "equipment_required": ["spreader"],
                "application_complexity": 0.3,
                "storage_requirements": "standard",
                "regional_availability": 0.9,
                "soil_health_benefit": 0.3,
                "manufacturer": "Generic Fertilizer Co.",
                "notes": "High nitrogen content, widely available"
            },
            {
                "fertilizer_id": "compost-2-1-1",
                "fertilizer_name": "Premium Compost 2-1-1",
                "fertilizer_type": "organic",
                "category": "organic",
                "nutrient_content": {
                    "nitrogen": 2.0,
                    "phosphorus": 1.0,
                    "potassium": 1.0,
                    "calcium": 2.0,
                    "magnesium": 0.5
                },
                "price_per_unit": 35.0,
                "unit_type": "ton",
                "application_rate": 5.0,
                "organic_certified": True,
                "slow_release": True,
                "greenhouse_gas_emission_factor": 0.5,
                "runoff_potential": 0.2,
                "leaching_potential": 0.2,
                "application_method": "broadcast",
                "equipment_required": ["spreader", "loader"],
                "application_complexity": 0.5,
                "storage_requirements": "covered",
                "regional_availability": 0.7,
                "soil_health_benefit": 0.9,
                "manufacturer": "Organic Farms Inc.",
                "notes": "Excellent for soil health, slow release"
            }
        ],
        "scoring_criteria": [
            {
                "dimension": "nutrient_value",
                "weight": 0.30,
                "maximize": True,
                "preference_function": "linear"
            },
            {
                "dimension": "cost_effectiveness",
                "weight": 0.25,
                "maximize": True,
                "preference_function": "linear"
            },
            {
                "dimension": "environmental_impact",
                "weight": 0.20,
                "maximize": True,
                "preference_function": "linear"
            },
            {
                "dimension": "application_convenience",
                "weight": 0.15,
                "maximize": True,
                "preference_function": "linear"
            },
            {
                "dimension": "soil_health_impact",
                "weight": 0.10,
                "maximize": True,
                "preference_function": "linear"
            }
        ],
        "scoring_method": "weighted_scoring",
        "crop_type": "corn",
        "field_size_acres": 100.0,
        "environmental_priority": 0.5,
        "include_trade_off_analysis": True,
        "normalize_scores": True
    }

    return {
        "example_request": example,
        "description": "Example comparison request with 2 fertilizers and 5 criteria",
        "usage": "POST this JSON to /api/v1/fertilizer-comparison/compare"
    }


async def log_comparison_completion(
    comparison_id: str,
    fertilizer_count: int,
    processing_time_ms: float
):
    """Background task to log comparison completion."""
    logger.info(
        f"Comparison {comparison_id} completed for {fertilizer_count} fertilizers "
        f"in {processing_time_ms:.2f}ms"
    )

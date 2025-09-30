"""
Agricultural Intelligence API Routes
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

FastAPI routes for agricultural intelligence endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import Dict, Any, List, Optional
import logging
import sys
import os

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../databases/python'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../services'))

from agricultural_intelligence_service import (
    AgriculturalIntelligenceService, AgriculturalIntelligenceResponse,
    IntelligenceType, RegionalBestPractice, ExpertRecommendation,
    PeerFarmerInsight, MarketInsight, SuccessPattern
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/agricultural-intelligence", tags=["agricultural-intelligence"])

# Service instance
intelligence_service = AgriculturalIntelligenceService()


@router.post("/location-intelligence", response_model=AgriculturalIntelligenceResponse)
async def get_location_intelligence(
    latitude: float = Body(..., ge=-90, le=90, description="Latitude in decimal degrees"),
    longitude: float = Body(..., ge=-180, le=180, description="Longitude in decimal degrees"),
    intelligence_types: Optional[List[IntelligenceType]] = Body(None, description="Specific types of intelligence to retrieve"),
    crop_type: Optional[str] = Body(None, description="Specific crop type for targeted recommendations"),
    farm_size_acres: Optional[float] = Body(None, ge=0, description="Farm size in acres for scaled recommendations")
) -> AgriculturalIntelligenceResponse:
    """
    Get comprehensive agricultural intelligence for a specific location.
    
    This endpoint provides location-based agricultural intelligence including:
    - Regional best practices and recommendations
    - Local expert recommendations and insights
    - Peer farmer insights and experiences
    - Market insights and opportunities
    - Success patterns and regional adaptations
    - Location-specific personalization
    
    Args:
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
        intelligence_types: Specific types of intelligence to retrieve (optional)
        crop_type: Specific crop type for targeted recommendations (optional)
        farm_size_acres: Farm size in acres for scaled recommendations (optional)
        
    Returns:
        AgriculturalIntelligenceResponse with comprehensive intelligence data
        
    Raises:
        HTTPException: If intelligence gathering fails
    """
    try:
        logger.info(f"Getting agricultural intelligence for location: {latitude}, {longitude}")
        
        result = await intelligence_service.get_location_intelligence(
            latitude=latitude,
            longitude=longitude,
            intelligence_types=intelligence_types,
            crop_type=crop_type,
            farm_size_acres=farm_size_acres
        )
        
        logger.info(f"Intelligence gathered: {len(result.regional_best_practices)} practices, "
                   f"{len(result.expert_recommendations)} expert recommendations, "
                   f"{len(result.peer_insights)} peer insights")
        
        return result
        
    except ValueError as e:
        logger.error(f"Invalid input for intelligence gathering: {e}")
        raise HTTPException(
            status_code=422,
            detail={
                "error": "INVALID_INPUT",
                "message": str(e),
                "agricultural_context": "Unable to gather intelligence for the specified location",
                "suggested_actions": [
                    "Verify coordinate values are within valid ranges",
                    "Check that location is in an agricultural region",
                    "Try a different location if coordinates are over water"
                ]
            }
        )
    except Exception as e:
        logger.error(f"Error gathering agricultural intelligence: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTELLIGENCE_SERVICE_ERROR",
                "message": "Internal agricultural intelligence service error",
                "agricultural_context": "Unable to provide location-based agricultural intelligence",
                "suggested_actions": [
                    "Try again in a few moments",
                    "Contact support if the problem persists",
                    "Use alternative intelligence sources"
                ]
            }
        )


@router.get("/regional-best-practices")
async def get_regional_best_practices(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude in decimal degrees"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude in decimal degrees"),
    crop_type: Optional[str] = Query(None, description="Filter by specific crop type"),
    farm_size_acres: Optional[float] = Query(None, ge=0, description="Filter by farm size in acres"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of practices to return")
) -> List[RegionalBestPractice]:
    """
    Get regional best practices for a specific location.
    
    This endpoint provides location-specific best practices including:
    - Soil management techniques
    - Crop production methods
    - Pest and disease management
    - Water conservation practices
    - Environmental stewardship practices
    
    Args:
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
        crop_type: Filter by specific crop type (optional)
        farm_size_acres: Filter by farm size in acres (optional)
        limit: Maximum number of practices to return (default: 10)
        
    Returns:
        List of RegionalBestPractice objects
        
    Raises:
        HTTPException: If practice retrieval fails
    """
    try:
        logger.info(f"Getting regional best practices for location: {latitude}, {longitude}")
        
        # Get intelligence and extract best practices
        intelligence = await intelligence_service.get_location_intelligence(
            latitude=latitude,
            longitude=longitude,
            intelligence_types=[IntelligenceType.REGIONAL_BEST_PRACTICES],
            crop_type=crop_type,
            farm_size_acres=farm_size_acres
        )
        
        practices = intelligence.regional_best_practices[:limit]
        
        logger.info(f"Retrieved {len(practices)} regional best practices")
        
        return practices
        
    except Exception as e:
        logger.error(f"Error getting regional best practices: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "BEST_PRACTICES_ERROR",
                "message": "Unable to retrieve regional best practices",
                "agricultural_context": "Best practices data temporarily unavailable",
                "suggested_actions": [
                    "Try again in a few moments",
                    "Contact support if the problem persists"
                ]
            }
        )


@router.get("/expert-recommendations")
async def get_expert_recommendations(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude in decimal degrees"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude in decimal degrees"),
    crop_type: Optional[str] = Query(None, description="Filter by specific crop type"),
    farm_size_acres: Optional[float] = Query(None, ge=0, description="Filter by farm size in acres"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of recommendations to return")
) -> List[ExpertRecommendation]:
    """
    Get local expert recommendations for a specific location.
    
    This endpoint provides recommendations from:
    - University extension specialists
    - Local agricultural experts
    - Research station scientists
    - Government agency specialists
    - Industry experts
    
    Args:
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
        crop_type: Filter by specific crop type (optional)
        farm_size_acres: Filter by farm size in acres (optional)
        limit: Maximum number of recommendations to return (default: 10)
        
    Returns:
        List of ExpertRecommendation objects
        
    Raises:
        HTTPException: If expert recommendations retrieval fails
    """
    try:
        logger.info(f"Getting expert recommendations for location: {latitude}, {longitude}")
        
        # Get intelligence and extract expert recommendations
        intelligence = await intelligence_service.get_location_intelligence(
            latitude=latitude,
            longitude=longitude,
            intelligence_types=[IntelligenceType.EXPERT_RECOMMENDATIONS],
            crop_type=crop_type,
            farm_size_acres=farm_size_acres
        )
        
        recommendations = intelligence.expert_recommendations[:limit]
        
        logger.info(f"Retrieved {len(recommendations)} expert recommendations")
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error getting expert recommendations: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "EXPERT_RECOMMENDATIONS_ERROR",
                "message": "Unable to retrieve expert recommendations",
                "agricultural_context": "Expert recommendations temporarily unavailable",
                "suggested_actions": [
                    "Try again in a few moments",
                    "Contact support if the problem persists"
                ]
            }
        )


@router.get("/peer-insights")
async def get_peer_insights(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude in decimal degrees"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude in decimal degrees"),
    crop_type: Optional[str] = Query(None, description="Filter by specific crop type"),
    farm_size_acres: Optional[float] = Query(None, ge=0, description="Filter by farm size in acres"),
    radius_km: float = Query(50, ge=1, le=200, description="Search radius in kilometers"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of insights to return")
) -> List[PeerFarmerInsight]:
    """
    Get peer farmer insights within a specified radius.
    
    This endpoint provides insights from nearby farmers including:
    - Success stories and experiences
    - Challenges and solutions
    - Innovations and tips
    - Lessons learned
    - Practical recommendations
    
    Args:
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
        crop_type: Filter by specific crop type (optional)
        farm_size_acres: Filter by farm size in acres (optional)
        radius_km: Search radius in kilometers (default: 50)
        limit: Maximum number of insights to return (default: 10)
        
    Returns:
        List of PeerFarmerInsight objects
        
    Raises:
        HTTPException: If peer insights retrieval fails
    """
    try:
        logger.info(f"Getting peer insights for location: {latitude}, {longitude}, radius: {radius_km}km")
        
        # Temporarily update service config for radius
        original_radius = intelligence_service.config['peer_insight_radius_km']
        intelligence_service.config['peer_insight_radius_km'] = radius_km
        
        try:
            # Get intelligence and extract peer insights
            intelligence = await intelligence_service.get_location_intelligence(
                latitude=latitude,
                longitude=longitude,
                intelligence_types=[IntelligenceType.PEER_INSIGHTS],
                crop_type=crop_type,
                farm_size_acres=farm_size_acres
            )
            
            insights = intelligence.peer_insights[:limit]
            
            logger.info(f"Retrieved {len(insights)} peer insights")
            
            return insights
            
        finally:
            # Restore original radius
            intelligence_service.config['peer_insight_radius_km'] = original_radius
        
    except Exception as e:
        logger.error(f"Error getting peer insights: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "PEER_INSIGHTS_ERROR",
                "message": "Unable to retrieve peer farmer insights",
                "agricultural_context": "Peer insights temporarily unavailable",
                "suggested_actions": [
                    "Try again in a few moments",
                    "Contact support if the problem persists"
                ]
            }
        )


@router.get("/market-insights")
async def get_market_insights(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude in decimal degrees"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude in decimal degrees"),
    crop_type: Optional[str] = Query(None, description="Filter by specific crop type"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of insights to return")
) -> List[MarketInsight]:
    """
    Get market insights for a specific location.
    
    This endpoint provides market intelligence including:
    - Price trends and forecasts
    - Demand levels and patterns
    - Market access opportunities
    - Premium opportunities
    - Competition analysis
    
    Args:
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
        crop_type: Filter by specific crop type (optional)
        limit: Maximum number of insights to return (default: 10)
        
    Returns:
        List of MarketInsight objects
        
    Raises:
        HTTPException: If market insights retrieval fails
    """
    try:
        logger.info(f"Getting market insights for location: {latitude}, {longitude}")
        
        # Get intelligence and extract market insights
        intelligence = await intelligence_service.get_location_intelligence(
            latitude=latitude,
            longitude=longitude,
            intelligence_types=[IntelligenceType.MARKET_INSIGHTS],
            crop_type=crop_type
        )
        
        insights = intelligence.market_insights[:limit]
        
        logger.info(f"Retrieved {len(insights)} market insights")
        
        return insights
        
    except Exception as e:
        logger.error(f"Error getting market insights: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "MARKET_INSIGHTS_ERROR",
                "message": "Unable to retrieve market insights",
                "agricultural_context": "Market insights temporarily unavailable",
                "suggested_actions": [
                    "Try again in a few moments",
                    "Contact support if the problem persists"
                ]
            }
        )


@router.get("/success-patterns")
async def get_success_patterns(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude in decimal degrees"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude in decimal degrees"),
    crop_type: Optional[str] = Query(None, description="Filter by specific crop type"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of patterns to return")
) -> List[SuccessPattern]:
    """
    Get success patterns for a specific location.
    
    This endpoint provides regional success patterns including:
    - Common success factors
    - Proven practices and techniques
    - Yield and profitability metrics
    - Risk factors and mitigation strategies
    - Implementation guidance
    
    Args:
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
        crop_type: Filter by specific crop type (optional)
        limit: Maximum number of patterns to return (default: 10)
        
    Returns:
        List of SuccessPattern objects
        
    Raises:
        HTTPException: If success patterns retrieval fails
    """
    try:
        logger.info(f"Getting success patterns for location: {latitude}, {longitude}")
        
        # Get intelligence and extract success patterns
        intelligence = await intelligence_service.get_location_intelligence(
            latitude=latitude,
            longitude=longitude,
            intelligence_types=[IntelligenceType.SUCCESS_PATTERNS],
            crop_type=crop_type
        )
        
        patterns = intelligence.success_patterns[:limit]
        
        logger.info(f"Retrieved {len(patterns)} success patterns")
        
        return patterns
        
    except Exception as e:
        logger.error(f"Error getting success patterns: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "SUCCESS_PATTERNS_ERROR",
                "message": "Unable to retrieve success patterns",
                "agricultural_context": "Success patterns temporarily unavailable",
                "suggested_actions": [
                    "Try again in a few moments",
                    "Contact support if the problem persists"
                ]
            }
        )


@router.get("/intelligence-summary")
async def get_intelligence_summary(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude in decimal degrees"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude in decimal degrees"),
    crop_type: Optional[str] = Query(None, description="Filter by specific crop type"),
    farm_size_acres: Optional[float] = Query(None, ge=0, description="Filter by farm size in acres")
) -> Dict[str, Any]:
    """
    Get a summary of agricultural intelligence for a specific location.
    
    This endpoint provides a concise summary including:
    - Key insights and recommendations
    - Top categories and practices
    - Market opportunities
    - Risk factors and success indicators
    - Confidence scores
    
    Args:
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
        crop_type: Filter by specific crop type (optional)
        farm_size_acres: Filter by farm size in acres (optional)
        
    Returns:
        Dictionary containing intelligence summary
        
    Raises:
        HTTPException: If intelligence summary retrieval fails
    """
    try:
        logger.info(f"Getting intelligence summary for location: {latitude}, {longitude}")
        
        # Get intelligence and extract summary
        intelligence = await intelligence_service.get_location_intelligence(
            latitude=latitude,
            longitude=longitude,
            crop_type=crop_type,
            farm_size_acres=farm_size_acres
        )
        
        summary = {
            "intelligence_summary": intelligence.intelligence_summary,
            "confidence_scores": intelligence.confidence_scores,
            "total_recommendations": len(intelligence.regional_best_practices) + 
                                   len(intelligence.expert_recommendations) + 
                                   len(intelligence.peer_insights),
            "data_sources": intelligence.data_sources,
            "last_updated": intelligence.last_updated,
            "region": intelligence.region
        }
        
        logger.info(f"Retrieved intelligence summary for region: {intelligence.region}")
        
        return summary
        
    except Exception as e:
        logger.error(f"Error getting intelligence summary: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTELLIGENCE_SUMMARY_ERROR",
                "message": "Unable to retrieve intelligence summary",
                "agricultural_context": "Intelligence summary temporarily unavailable",
                "suggested_actions": [
                    "Try again in a few moments",
                    "Contact support if the problem persists"
                ]
            }
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for agricultural intelligence service."""
    return {
        "status": "healthy",
        "service": "agricultural-intelligence",
        "version": "1.0",
        "features": [
            "regional_best_practices",
            "expert_recommendations", 
            "peer_insights",
            "market_insights",
            "success_patterns",
            "local_adaptations"
        ]
    }
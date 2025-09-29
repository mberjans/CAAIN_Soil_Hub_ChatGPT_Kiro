"""
Crop Diversification API Routes

API endpoints for crop diversification and risk management functionality.
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from uuid import UUID

from ..models.crop_diversification_models import (
    DiversificationRequest,
    DiversificationResponse,
    DiversificationRecommendation,
    DiversificationPortfolio,
    CropRiskProfile,
    MarketRiskAssessment,
    RiskLevel,
    DiversificationStrategy
)
from services.crop_diversification_service import CropDiversificationService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/diversification", tags=["crop-diversification"])

# Service instance
diversification_service = CropDiversificationService()

@router.on_event("startup")
async def startup_event():
    """Initialize the diversification service on startup."""
    await diversification_service.initialize()

@router.on_event("shutdown")
async def shutdown_event():
    """Clean up the diversification service on shutdown."""
    await diversification_service.cleanup()

@router.post("/analyze", response_model=DiversificationResponse)
async def analyze_diversification_options(request: DiversificationRequest):
    """
    Analyze crop diversification options for drought risk reduction.
    
    This endpoint implements comprehensive diversification analysis including:
    - Current risk assessment
    - Portfolio optimization
    - Market risk analysis
    - Economic impact assessment
    - Implementation recommendations
    
    Agricultural Benefits:
    - Reduces drought risk through crop diversification
    - Improves yield stability across varying weather conditions
    - Enhances soil health through diverse crop rotations
    - Provides market risk mitigation through portfolio approach
    - Optimizes water use efficiency
    """
    try:
        logger.info(f"Processing diversification analysis request for farm: {request.farm_id}")
        
        # Validate request
        if request.total_acres <= 0:
            raise HTTPException(
                status_code=400,
                detail="Total acres must be greater than 0"
            )
        
        if not request.diversification_goals:
            raise HTTPException(
                status_code=400,
                detail="At least one diversification goal must be specified"
            )
        
        # Perform diversification analysis
        response = await diversification_service.analyze_diversification_options(request)
        
        logger.info(f"Diversification analysis completed for farm: {request.farm_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing diversification options: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing diversification options: {str(e)}"
        )

@router.post("/optimize-portfolio", response_model=DiversificationPortfolio)
async def optimize_crop_portfolio(request: DiversificationRequest):
    """
    Optimize crop portfolio for maximum diversification benefits.
    
    This endpoint creates an optimized crop portfolio considering:
    - Drought tolerance and water efficiency
    - Market risk and price volatility
    - Soil health contributions
    - Yield stability and reliability
    - Farm constraints and preferences
    
    Portfolio Optimization Features:
    - Risk-adjusted allocation using portfolio theory
    - Climate zone compatibility assessment
    - Equipment and resource constraint consideration
    - Economic optimization with ROI calculations
    - Sustainability goal integration
    """
    try:
        logger.info(f"Optimizing crop portfolio for farm: {request.farm_id}")
        
        # Validate request
        if request.total_acres <= 0:
            raise HTTPException(
                status_code=400,
                detail="Total acres must be greater than 0"
            )
        
        # Optimize portfolio
        portfolio = await diversification_service.optimize_crop_portfolio(request)
        
        logger.info(f"Portfolio optimization completed for farm: {request.farm_id}")
        return portfolio
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error optimizing crop portfolio: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error optimizing crop portfolio: {str(e)}"
        )

@router.post("/assess-drought-risk-reduction")
async def assess_drought_risk_reduction(portfolio: DiversificationPortfolio):
    """
    Assess drought risk reduction potential of a crop portfolio.
    
    This endpoint evaluates how well a portfolio reduces drought risk through:
    - Water efficiency analysis
    - Yield stability assessment
    - Soil health benefits calculation
    - Temporal risk distribution evaluation
    - Overall drought resilience scoring
    
    Assessment Metrics:
    - Water efficiency score (0-1)
    - Yield stability score (0-1)
    - Soil health improvement score (0-1)
    - Temporal risk distribution score (0-1)
    - Overall drought resilience score (0-1)
    - Risk reduction percentage
    - Specific mitigation recommendations
    """
    try:
        logger.info(f"Assessing drought risk reduction for portfolio: {portfolio.portfolio_id}")
        
        # Assess drought risk reduction
        assessment = await diversification_service.assess_drought_risk_reduction(portfolio)
        
        logger.info(f"Drought risk assessment completed for portfolio: {portfolio.portfolio_id}")
        return assessment
        
    except Exception as e:
        logger.error(f"Error assessing drought risk reduction: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error assessing drought risk reduction: {str(e)}"
        )

@router.get("/crop-risk-profiles", response_model=List[CropRiskProfile])
async def get_crop_risk_profiles(
    category: Optional[str] = Query(None, description="Filter by crop category"),
    drought_tolerance: Optional[str] = Query(None, description="Filter by drought tolerance level"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of crops to return")
):
    """
    Get crop risk profiles for diversification planning.
    
    This endpoint provides detailed risk profiles for available crops including:
    - Drought tolerance levels
    - Water requirements
    - Yield stability scores
    - Market price volatility
    - Disease and pest susceptibility
    - Soil health contributions
    - Nitrogen fixation capabilities
    
    Filtering Options:
    - Crop category (grains, legumes, oilseeds, forage, vegetables, fruits, specialty, cover_crops)
    - Drought tolerance level (low, moderate, high, very_high)
    - Limit number of results returned
    """
    try:
        logger.info("Retrieving crop risk profiles")
        
        # Get available crops
        available_crops = await diversification_service._get_available_crops(
            DiversificationRequest(
                farm_id=UUID("00000000-0000-0000-0000-000000000000"),
                field_ids=[UUID("00000000-0000-0000-0000-000000000000")],
                total_acres=100.0,
                risk_tolerance=RiskLevel.MODERATE,
                diversification_goals=["drought_resilience"]
            )
        )
        
        # Apply filters
        filtered_crops = available_crops
        
        if category:
            filtered_crops = [c for c in filtered_crops if c.crop_category.value == category.lower()]
        
        if drought_tolerance:
            filtered_crops = [c for c in filtered_crops if c.drought_tolerance.value == drought_tolerance.lower()]
        
        # Limit results
        filtered_crops = filtered_crops[:limit]
        
        logger.info(f"Retrieved {len(filtered_crops)} crop risk profiles")
        return filtered_crops
        
    except Exception as e:
        logger.error(f"Error retrieving crop risk profiles: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving crop risk profiles: {str(e)}"
        )

@router.get("/market-risk-assessment/{crop_name}")
async def get_market_risk_assessment(crop_name: str = Path(..., description="Name of the crop")):
    """
    Get market risk assessment for a specific crop.
    
    This endpoint provides detailed market risk analysis including:
    - Price volatility assessment
    - Demand stability evaluation
    - Supply chain risk factors
    - Weather sensitivity analysis
    - Policy risk considerations
    - Risk mitigation strategies
    
    Market Risk Factors:
    - Price volatility (0-1 scale)
    - Demand stability (0-1 scale)
    - Supply chain risk (0-1 scale)
    - Weather sensitivity (0-1 scale)
    - Policy risk (0-1 scale)
    - Overall market risk (0-1 scale)
    """
    try:
        logger.info(f"Retrieving market risk assessment for crop: {crop_name}")
        
        # Get market risk data
        market_risks = diversification_service._build_market_risk_data()
        
        if crop_name.lower() not in market_risks:
            raise HTTPException(
                status_code=404,
                detail=f"Market risk assessment not available for crop: {crop_name}"
            )
        
        assessment = market_risks[crop_name.lower()]
        
        logger.info(f"Retrieved market risk assessment for crop: {crop_name}")
        return assessment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving market risk assessment: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving market risk assessment: {str(e)}"
        )

@router.get("/diversification-strategies", response_model=List[str])
async def get_diversification_strategies(
    farm_size_acres: float = Query(..., ge=1, description="Farm size in acres"),
    num_fields: int = Query(1, ge=1, description="Number of fields"),
    sustainability_goals: List[str] = Query([], description="Sustainability goals")
):
    """
    Get recommended diversification strategies based on farm characteristics.
    
    This endpoint suggests appropriate diversification strategies considering:
    - Farm size and field configuration
    - Sustainability goals and preferences
    - Risk tolerance and constraints
    - Market opportunities and challenges
    
    Available Strategies:
    - Crop rotation: Sequential planting of different crops
    - Intercropping: Growing multiple crops simultaneously
    - Agroforestry: Integrating trees with crops
    - Temporal diversification: Staggered planting and harvesting
    - Spatial diversification: Different crops across fields
    - Market diversification: Multiple market channels
    """
    try:
        logger.info(f"Retrieving diversification strategies for {farm_size_acres} acres")
        
        # Create mock request for strategy generation
        mock_request = DiversificationRequest(
            farm_id=UUID("00000000-0000-0000-0000-000000000000"),
            field_ids=[UUID("00000000-0000-0000-0000-000000000000")] * num_fields,
            total_acres=farm_size_acres,
            risk_tolerance=RiskLevel.MODERATE,
            diversification_goals=["drought_resilience"],
            sustainability_goals=sustainability_goals
        )
        
        # Generate strategies
        strategies = await diversification_service._generate_diversification_strategies(mock_request)
        
        # Convert to string list
        strategy_names = [strategy.value.replace('_', ' ').title() for strategy in strategies]
        
        logger.info(f"Retrieved {len(strategy_names)} diversification strategies")
        return strategy_names
        
    except Exception as e:
        logger.error(f"Error retrieving diversification strategies: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving diversification strategies: {str(e)}"
        )

@router.get("/compatibility-matrix")
async def get_crop_compatibility_matrix():
    """
    Get crop compatibility matrix for diversification planning.
    
    This endpoint provides comprehensive compatibility data including:
    - Crop pair compatibility scores
    - Rotation benefits between crops
    - Intercropping potential scores
    - Soil health benefits per crop
    - Pest and disease interactions
    
    Compatibility Data:
    - Crop pairs: Compatibility scores (0-1) for crop combinations
    - Rotation benefits: Benefits of rotating between crops
    - Intercropping potential: Suitability for simultaneous growing
    - Soil health benefits: Contribution to soil health (0-1)
    - Pest/disease interactions: Beneficial, neutral, or competitive relationships
    """
    try:
        logger.info("Retrieving crop compatibility matrix")
        
        # Get compatibility matrix
        matrix = diversification_service._build_compatibility_matrix()
        
        logger.info("Retrieved crop compatibility matrix")
        return matrix
        
    except Exception as e:
        logger.error(f"Error retrieving compatibility matrix: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving compatibility matrix: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """Health check endpoint for the diversification service."""
    return {
        "status": "healthy",
        "service": "crop-diversification",
        "version": "1.0.0",
        "initialized": diversification_service.initialized
    }

@router.get("/metrics")
async def get_service_metrics():
    """
    Get service performance metrics and statistics.
    
    This endpoint provides service performance data including:
    - Request counts and response times
    - Error rates and success rates
    - Service availability and uptime
    - Resource utilization metrics
    """
    try:
        logger.info("Retrieving service metrics")
        
        # In a real implementation, these would be actual metrics
        metrics = {
            "requests_total": 0,
            "requests_successful": 0,
            "requests_failed": 0,
            "average_response_time_ms": 0,
            "uptime_seconds": 0,
            "memory_usage_mb": 0,
            "cpu_usage_percent": 0
        }
        
        logger.info("Retrieved service metrics")
        return metrics
        
    except Exception as e:
        logger.error(f"Error retrieving service metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving service metrics: {str(e)}"
        )
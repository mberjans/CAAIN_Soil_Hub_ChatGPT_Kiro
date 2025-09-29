"""
Market Intelligence API Endpoints
FastAPI endpoints for market intelligence and pricing analysis.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from ..models.market_intelligence_models import (
    MarketIntelligenceRequest, MarketIntelligenceResponse,
    VarietyMarketPrice, MarketTrend, BasisAnalysis, DemandForecast,
    PremiumDiscountAnalysis, MarketType, QualityGrade, ContractType
)
from ..services.market_intelligence_service import MarketIntelligenceService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/market-intelligence", tags=["market-intelligence"])

# Dependency injection
async def get_market_intelligence_service() -> MarketIntelligenceService:
    return MarketIntelligenceService()


@router.post("/analyze", response_model=MarketIntelligenceResponse)
async def analyze_market_intelligence(
    request: MarketIntelligenceRequest = Body(...),
    service: MarketIntelligenceService = Depends(get_market_intelligence_service)
):
    """
    Analyze market intelligence for specified varieties.
    
    This endpoint provides comprehensive market analysis including:
    - Real-time pricing from multiple market sources
    - Market trends and volatility analysis
    - Basis analysis and patterns
    - Demand forecasting
    - Premium/discount analysis
    - Market opportunities and risk factors
    
    Agricultural Use Cases:
    - Variety selection based on market potential
    - Pricing strategy development
    - Contract timing optimization
    - Market risk assessment
    """
    try:
        result = await service.get_market_intelligence(request)
        return result
    except Exception as e:
        logger.error(f"Error in market intelligence analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/variety/{variety_name}/prices", response_model=List[VarietyMarketPrice])
async def get_variety_prices(
    variety_name: str,
    regions: Optional[List[str]] = Query(None, description="Geographic regions to include"),
    market_types: Optional[List[MarketType]] = Query(None, description="Market types to include"),
    quality_grades: Optional[List[QualityGrade]] = Query(None, description="Quality grades to include"),
    contract_types: Optional[List[ContractType]] = Query(None, description="Contract types to include"),
    service: MarketIntelligenceService = Depends(get_market_intelligence_service)
):
    """
    Get current market prices for a specific variety.
    
    Returns real-time pricing data from multiple market sources
    with filtering options for regions, market types, and quality grades.
    """
    try:
        request = MarketIntelligenceRequest(
            variety_names=[variety_name],
            regions=regions,
            market_types=market_types,
            quality_grades=quality_grades,
            contract_types=contract_types,
            include_trends=False,
            include_basis=False,
            include_demand_forecast=False,
            include_premium_discount=False,
            include_recommendations=False,
            include_executive_summary=False,
            detail_level="basic"
        )
        
        result = await service.get_market_intelligence(request)
        
        if result.reports:
            return result.reports[0].current_prices
        else:
            return []
            
    except Exception as e:
        logger.error(f"Error getting variety prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/variety/{variety_name}/trends", response_model=MarketTrend)
async def get_variety_trends(
    variety_name: str,
    analysis_period: str = Query("30d", description="Analysis period (7d, 30d, 90d, 1y)"),
    service: MarketIntelligenceService = Depends(get_market_intelligence_service)
):
    """
    Get market trend analysis for a specific variety.
    
    Provides trend analysis including:
    - Price trends over multiple time periods
    - Volatility metrics
    - Trend direction and strength
    - Seasonal patterns
    - Market sentiment analysis
    """
    try:
        request = MarketIntelligenceRequest(
            variety_names=[variety_name],
            analysis_period=analysis_period,
            include_trends=True,
            include_basis=False,
            include_demand_forecast=False,
            include_premium_discount=False,
            include_recommendations=False,
            include_executive_summary=False,
            detail_level="standard"
        )
        
        result = await service.get_market_intelligence(request)
        
        if result.reports and result.reports[0].market_trends:
            return result.reports[0].market_trends
        else:
            raise HTTPException(status_code=404, detail="Trend analysis not available")
            
    except Exception as e:
        logger.error(f"Error getting variety trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/variety/{variety_name}/basis", response_model=BasisAnalysis)
async def get_variety_basis(
    variety_name: str,
    location: str = Query("US", description="Location for basis analysis"),
    service: MarketIntelligenceService = Depends(get_market_intelligence_service)
):
    """
    Get basis analysis for a specific variety and location.
    
    Provides basis analysis including:
    - Current basis levels
    - Historical basis averages
    - Basis trends and volatility
    - Location-specific factors
    - Transportation cost components
    """
    try:
        request = MarketIntelligenceRequest(
            variety_names=[variety_name],
            regions=[location],
            include_trends=False,
            include_basis=True,
            include_demand_forecast=False,
            include_premium_discount=False,
            include_recommendations=False,
            include_executive_summary=False,
            detail_level="standard"
        )
        
        result = await service.get_market_intelligence(request)
        
        if result.reports and result.reports[0].basis_analysis:
            return result.reports[0].basis_analysis
        else:
            raise HTTPException(status_code=404, detail="Basis analysis not available")
            
    except Exception as e:
        logger.error(f"Error getting variety basis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/variety/{variety_name}/demand-forecast", response_model=DemandForecast)
async def get_variety_demand_forecast(
    variety_name: str,
    forecast_horizon: int = Query(90, description="Forecast horizon in days"),
    service: MarketIntelligenceService = Depends(get_market_intelligence_service)
):
    """
    Get demand forecast for a specific variety.
    
    Provides demand forecasting including:
    - Short-term and long-term demand projections
    - Demand drivers (domestic, export, feed, industrial)
    - Market segment analysis
    - Quality preferences
    - Premium potential assessment
    """
    try:
        request = MarketIntelligenceRequest(
            variety_names=[variety_name],
            include_trends=False,
            include_basis=False,
            include_demand_forecast=True,
            include_premium_discount=False,
            include_recommendations=False,
            include_executive_summary=False,
            detail_level="standard"
        )
        
        result = await service.get_market_intelligence(request)
        
        if result.reports and result.reports[0].demand_forecast:
            return result.reports[0].demand_forecast
        else:
            raise HTTPException(status_code=404, detail="Demand forecast not available")
            
    except Exception as e:
        logger.error(f"Error getting demand forecast: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/variety/{variety_name}/premiums-discounts", response_model=PremiumDiscountAnalysis)
async def get_variety_premiums_discounts(
    variety_name: str,
    market_location: str = Query("US", description="Market location for analysis"),
    service: MarketIntelligenceService = Depends(get_market_intelligence_service)
):
    """
    Get premium/discount analysis for a specific variety.
    
    Provides premium/discount analysis including:
    - Current premium/discount levels
    - Quality-based premiums (protein, oil, moisture)
    - Market-specific premiums (organic, non-GMO, identity preserved)
    - Contract-based premiums (timing, volume, payment terms)
    - Analysis of premium/discount drivers
    """
    try:
        request = MarketIntelligenceRequest(
            variety_names=[variety_name],
            regions=[market_location],
            include_trends=False,
            include_basis=False,
            include_demand_forecast=False,
            include_premium_discount=True,
            include_recommendations=False,
            include_executive_summary=False,
            detail_level="standard"
        )
        
        result = await service.get_market_intelligence(request)
        
        if result.reports and result.reports[0].premium_discount_analysis:
            return result.reports[0].premium_discount_analysis
        else:
            raise HTTPException(status_code=404, detail="Premium/discount analysis not available")
            
    except Exception as e:
        logger.error(f"Error getting premium/discount analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/crop/{crop_name}/market-overview")
async def get_crop_market_overview(
    crop_name: str,
    regions: Optional[List[str]] = Query(None, description="Geographic regions to include"),
    service: MarketIntelligenceService = Depends(get_market_intelligence_service)
):
    """
    Get market overview for all varieties of a specific crop.
    
    Provides comprehensive market overview including:
    - Price ranges across varieties
    - Market trends and volatility
    - Demand outlook
    - Key market opportunities
    - Risk factors
    """
    try:
        request = MarketIntelligenceRequest(
            crop_names=[crop_name],
            regions=regions,
            include_trends=True,
            include_basis=True,
            include_demand_forecast=True,
            include_premium_discount=True,
            include_recommendations=True,
            include_executive_summary=True,
            detail_level="comprehensive"
        )
        
        result = await service.get_market_intelligence(request)
        
        # Aggregate data across all varieties
        overview = {
            "crop_name": crop_name,
            "analysis_date": result.analysis_date,
            "total_varieties_analyzed": result.total_varieties_analyzed,
            "total_markets_analyzed": result.total_markets_analyzed,
            "price_points_collected": result.price_points_collected,
            "overall_confidence": result.overall_confidence,
            "data_coverage_score": result.data_coverage_score,
            "varieties": []
        }
        
        for report in result.reports:
            variety_overview = {
                "variety_name": report.variety_name,
                "price_range": {
                    "min": float(min([p.price_per_unit for p in report.current_prices])) if report.current_prices else 0,
                    "max": float(max([p.price_per_unit for p in report.current_prices])) if report.current_prices else 0,
                    "avg": float(sum([p.price_per_unit for p in report.current_prices]) / len(report.current_prices)) if report.current_prices else 0
                },
                "market_trend": report.market_trends.trend_direction if report.market_trends else "unknown",
                "market_opportunities": report.market_opportunities,
                "risk_factors": report.risk_factors,
                "confidence": report.confidence
            }
            overview["varieties"].append(variety_overview)
        
        return overview
        
    except Exception as e:
        logger.error(f"Error getting crop market overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint for market intelligence service."""
    return {
        "status": "healthy",
        "service": "market-intelligence",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@router.get("/data-sources")
async def get_data_sources():
    """Get list of available data sources."""
    return {
        "data_sources": [
            {
                "name": "Commodity Exchange",
                "type": "commodity_exchange",
                "description": "CME Group, CBOT futures and options data",
                "update_frequency": "real_time",
                "confidence": 0.9
            },
            {
                "name": "Local Elevator",
                "type": "local_elevator", 
                "description": "Local elevator cash prices and basis",
                "update_frequency": "daily",
                "confidence": 0.8
            },
            {
                "name": "Contract Pricing",
                "type": "contract_pricing",
                "description": "Forward contracts and hedge pricing",
                "update_frequency": "daily",
                "confidence": 0.85
            },
            {
                "name": "Specialty Market",
                "type": "specialty_market",
                "description": "Organic, non-GMO, and specialty market pricing",
                "update_frequency": "weekly",
                "confidence": 0.7
            }
        ]
    }
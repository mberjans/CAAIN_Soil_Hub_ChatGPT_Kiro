"""
API routes for commodity price tracking and analysis.
"""

from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks
from typing import List, Optional, Dict, Any
import logging
from datetime import date

from ..models.commodity_price_models import (
    CommodityPriceData, CommodityTrendAnalysis, FertilizerCropPriceRatio,
    CommodityPriceQueryRequest, CommodityPriceQueryResponse, CommodityMarketIntelligence,
    BasisAnalysis, CommodityType, CommodityContract, CommoditySource
)
from ..services.commodity_price_service import CommodityPriceService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/commodity-prices", tags=["commodity-prices"])

# Dependency injection
async def get_commodity_service() -> CommodityPriceService:
    return CommodityPriceService()


@router.get("/current/{commodity}", response_model=CommodityPriceData)
async def get_current_commodity_price(
    commodity: CommodityType,
    region: str = Query("US", description="Geographic region"),
    contract_type: CommodityContract = Query(CommodityContract.CASH, description="Contract type"),
    max_age_hours: int = Query(24, description="Maximum age of cached data in hours"),
    service: CommodityPriceService = Depends(get_commodity_service)
):
    """
    Get current price for a specific commodity.
    
    This endpoint provides real-time commodity pricing information
    from multiple data sources including CBOT, CME Group, local elevators,
    cash markets, and USDA NASS.
    
    Agricultural Use Cases:
    - Real-time crop price monitoring for marketing decisions
    - Futures market analysis for hedging strategies
    - Cash market price tracking for immediate sales
    - Regional price comparison for optimal marketing locations
    """
    try:
        price_data = await service.get_current_price(commodity, region, contract_type, max_age_hours)
        
        if not price_data:
            raise HTTPException(
                status_code=404,
                detail=f"No price data available for {commodity.value} in {region}"
            )
        
        return price_data
        
    except Exception as e:
        logger.error(f"Error getting current commodity price: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/current", response_model=Dict[str, Optional[CommodityPriceData]])
async def get_current_commodity_prices(
    commodities: List[CommodityType] = Query(..., description="List of commodities"),
    region: str = Query("US", description="Geographic region"),
    contract_type: CommodityContract = Query(CommodityContract.CASH, description="Contract type"),
    max_age_hours: int = Query(24, description="Maximum age of cached data in hours"),
    service: CommodityPriceService = Depends(get_commodity_service)
):
    """
    Get current prices for multiple commodities.
    
    Efficient endpoint for retrieving prices for multiple commodities
    simultaneously, useful for comprehensive market analysis and
    comparison across different crop types.
    
    Agricultural Use Cases:
    - Multi-commodity market overview for farm planning
    - Crop rotation profitability analysis
    - Portfolio diversification assessment
    - Market timing for different crops
    """
    try:
        if len(commodities) > 20:
            raise HTTPException(
                status_code=400,
                detail="Maximum 20 commodities per request"
            )
        
        prices = await service.get_current_prices(commodities, region, contract_type, max_age_hours)
        return prices
        
    except Exception as e:
        logger.error(f"Error getting current commodity prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trend/{commodity}", response_model=CommodityTrendAnalysis)
async def get_commodity_price_trend(
    commodity: CommodityType,
    region: str = Query("US", description="Geographic region"),
    days: int = Query(30, ge=7, le=365, description="Number of days for trend analysis"),
    contract_type: CommodityContract = Query(CommodityContract.CASH, description="Contract type"),
    service: CommodityPriceService = Depends(get_commodity_service)
):
    """
    Get price trend analysis for a commodity.
    
    This endpoint provides comprehensive trend analysis including
    price changes over different time periods, volatility metrics,
    and trend direction indicators for informed decision making.
    
    Agricultural Use Cases:
    - Price trend analysis for marketing timing decisions
    - Volatility assessment for risk management
    - Market direction analysis for strategic planning
    - Historical performance evaluation for crop selection
    """
    try:
        trend_analysis = await service.get_price_trend(commodity, region, days, contract_type)
        
        if not trend_analysis:
            raise HTTPException(
                status_code=404,
                detail=f"Insufficient data for trend analysis of {commodity.value} in {region}"
            )
        
        return trend_analysis
        
    except Exception as e:
        logger.error(f"Error getting commodity price trend: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=CommodityPriceQueryResponse)
async def query_commodity_prices(
    request: CommodityPriceQueryRequest,
    service: CommodityPriceService = Depends(get_commodity_service)
):
    """
    Execute a comprehensive commodity price query with filters and analysis.
    
    This endpoint allows for complex price queries with multiple filters,
    including commodity types, regions, date ranges, and analysis options.
    Ideal for detailed market analysis and reporting.
    
    Agricultural Use Cases:
    - Comprehensive market analysis across multiple commodities
    - Regional price comparison studies
    - Historical price analysis for trend identification
    - Custom reporting for agricultural planning
    """
    try:
        response = await service.query_prices(request)
        return response
        
    except Exception as e:
        logger.error(f"Error executing commodity price query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/basis/{commodity}", response_model=BasisAnalysis)
async def get_basis_analysis(
    commodity: CommodityType,
    region: str = Query("US", description="Geographic region"),
    service: CommodityPriceService = Depends(get_commodity_service)
):
    """
    Get basis analysis for a commodity (cash price - futures price).
    
    This endpoint calculates the basis (difference between local cash price
    and futures price) which is crucial for understanding local market
    conditions and hedging effectiveness.
    
    Agricultural Use Cases:
    - Basis analysis for hedging strategy optimization
    - Local market condition assessment
    - Storage and marketing timing decisions
    - Risk management for price volatility
    """
    try:
        basis_analysis = await service.calculate_basis_analysis(commodity, region)
        
        if not basis_analysis:
            raise HTTPException(
                status_code=404,
                detail=f"Insufficient data for basis analysis of {commodity.value} in {region}"
            )
        
        return basis_analysis
        
    except Exception as e:
        logger.error(f"Error getting basis analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/price-ratios", response_model=List[FertilizerCropPriceRatio])
async def calculate_price_ratios(
    request: Dict[str, Any],
    service: CommodityPriceService = Depends(get_commodity_service)
):
    """
    Calculate fertilizer-to-crop price ratios for profitability analysis.
    
    This endpoint calculates the ratio between fertilizer prices and crop prices
    to assess the economic viability of fertilizer applications and help farmers
    make informed decisions about fertilizer investments.
    
    Agricultural Use Cases:
    - Fertilizer profitability assessment
    - Cost-benefit analysis for fertilizer applications
    - Economic optimization of fertilizer strategies
    - Market timing for fertilizer purchases
    """
    try:
        fertilizer_prices = request.get("fertilizer_prices", {})
        crop_prices = request.get("crop_prices", {})
        region = request.get("region", "US")
        
        ratios = await service.calculate_fertilizer_crop_price_ratios(
            fertilizer_prices, crop_prices, region
        )
        
        return ratios
        
    except Exception as e:
        logger.error(f"Error calculating price ratios: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/commodities", response_model=List[Dict[str, Any]])
async def get_available_commodities():
    """
    Get list of available commodities for price tracking.
    
    This endpoint provides a comprehensive list of all commodities
    that can be tracked, including their types and specifications.
    
    Agricultural Use Cases:
    - Commodity discovery for price tracking
    - System integration and configuration
    - Commodity catalog for user interfaces
    - API documentation and reference
    """
    try:
        commodities = []
        for commodity in CommodityType:
            commodities.append({
                "commodity_id": commodity.value,
                "commodity_name": commodity.value.title(),
                "description": f"{commodity.value.title()} commodity"
            })
        
        return commodities
        
    except Exception as e:
        logger.error(f"Error getting available commodities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/contract-types", response_model=List[Dict[str, Any]])
async def get_contract_types():
    """
    Get list of available contract types.
    
    This endpoint provides contract type categories for filtering
    and organizing price data by contract classification.
    
    Agricultural Use Cases:
    - Contract type-based price filtering
    - Category-based analysis
    - System configuration
    - User interface organization
    """
    try:
        contract_types = []
        for contract_type in CommodityContract:
            contract_types.append({
                "contract_id": contract_type.value,
                "contract_name": contract_type.value.title(),
                "description": f"{contract_type.value.title()} contract type"
            })
        
        return contract_types
        
    except Exception as e:
        logger.error(f"Error getting contract types: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sources", response_model=List[Dict[str, Any]])
async def get_commodity_sources():
    """
    Get list of available commodity price data sources.
    
    This endpoint provides information about all data sources
    used for commodity price tracking, including their reliability
    and update frequency.
    
    Agricultural Use Cases:
    - Data source transparency
    - Reliability assessment
    - Source-specific analysis
    - Quality assurance
    """
    try:
        sources = []
        for source in CommoditySource:
            source_info = {
                "source_id": source.value,
                "source_name": source.value.replace("_", " ").title(),
                "description": f"{source.value.replace('_', ' ').title()} price data source"
            }
            
            # Add specific information for each source
            if source == CommoditySource.CBOT:
                source_info["reliability"] = "High"
                source_info["update_frequency"] = "Real-time"
            elif source == CommoditySource.CME_GROUP:
                source_info["reliability"] = "High"
                source_info["update_frequency"] = "Real-time"
            elif source == CommoditySource.LOCAL_ELEVATOR:
                source_info["reliability"] = "Medium"
                source_info["update_frequency"] = "Daily"
            elif source == CommoditySource.CASH_MARKET:
                source_info["reliability"] = "Medium"
                source_info["update_frequency"] = "Daily"
            elif source == CommoditySource.USDA_NASS:
                source_info["reliability"] = "High"
                source_info["update_frequency"] = "Weekly"
            elif source == CommoditySource.FALLBACK:
                source_info["reliability"] = "Low"
                source_info["update_frequency"] = "Static"
            
            sources.append(source_info)
        
        return sources
        
    except Exception as e:
        logger.error(f"Error getting commodity sources: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market-intelligence/{region}", response_model=CommodityMarketIntelligence)
async def get_market_intelligence(
    region: str,
    service: CommodityPriceService = Depends(get_commodity_service)
):
    """
    Get comprehensive market intelligence report for a region.
    
    This endpoint provides detailed market analysis including price trends,
    correlations between commodities and fertilizers, and strategic
    recommendations for agricultural decision making.
    
    Agricultural Use Cases:
    - Comprehensive market analysis for strategic planning
    - Price correlation analysis for risk management
    - Market intelligence for investment decisions
    - Regional market outlook and recommendations
    """
    try:
        # In production, this would generate a comprehensive market intelligence report
        # For now, return a mock report
        report = CommodityMarketIntelligence(
            report_id=f"market_intelligence_{region}_{date.today()}",
            report_date=date.today(),
            region=region,
            market_summary=f"Market conditions in {region} show moderate volatility with seasonal trends.",
            key_trends=[
                "Corn prices trending upward due to supply concerns",
                "Soybean prices stable with good demand",
                "Wheat prices showing seasonal weakness"
            ],
            price_outlook="Mixed outlook with corn showing strength, soybeans stable, wheat under pressure",
            commodity_analyses={
                "corn": {"trend": "up", "strength": "moderate"},
                "soybean": {"trend": "stable", "strength": "weak"},
                "wheat": {"trend": "down", "strength": "moderate"}
            },
            price_correlations={
                "corn_urea": 0.75,
                "soybean_dap": 0.68,
                "wheat_potash": 0.72
            },
            recommendations=[
                "Consider corn for higher profitability",
                "Monitor soybean basis for marketing opportunities",
                "Evaluate wheat storage vs immediate sale"
            ],
            confidence_score=0.85,
            data_sources=[CommoditySource.CBOT, CommoditySource.USDA_NASS]
        )
        
        return report
        
    except Exception as e:
        logger.error(f"Error getting market intelligence: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint for commodity price service."""
    return {
        "service": "commodity-price-tracking",
        "status": "healthy",
        "features": [
            "real_time_commodity_price_tracking",
            "historical_price_analysis",
            "price_trend_calculation",
            "multi_source_data_integration",
            "regional_price_variations",
            "volatility_analysis",
            "basis_analysis",
            "fertilizer_crop_price_ratios",
            "market_intelligence",
            "caching_and_performance",
            "data_validation",
            "futures_market_integration"
        ]
    }
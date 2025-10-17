"""
API routes for fertilizer price tracking and analysis.
"""

from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks
from typing import List, Optional, Dict, Any
import logging
from datetime import date

from ..models.price_models import (
    FertilizerPriceData, PriceTrendAnalysis, PriceQueryRequest, 
    PriceQueryResponse, PriceUpdateRequest, PriceUpdateResponse,
    FertilizerType, FertilizerProduct, PriceSource
)
from ..services.price_tracking_service import FertilizerPriceTrackingService
from ..services.scheduled_price_updater import get_scheduler

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/fertilizer-prices", tags=["fertilizer-prices"])

# Dependency injection
async def get_price_service() -> FertilizerPriceTrackingService:
    return FertilizerPriceTrackingService()


@router.get("/current/{product}", response_model=FertilizerPriceData)
async def get_current_price(
    product: FertilizerProduct,
    region: str = Query("US", description="Geographic region"),
    max_age_hours: int = Query(24, description="Maximum age of cached data in hours"),
    service: FertilizerPriceTrackingService = Depends(get_price_service)
):
    """
    Get current price for a specific fertilizer product.
    
    This endpoint provides real-time fertilizer pricing information
    from multiple data sources including USDA NASS, commodity exchanges,
    manufacturers, and regional dealers.
    
    Agricultural Use Cases:
    - Real-time fertilizer cost analysis for application planning
    - Market price monitoring for purchasing decisions
    - Regional price comparison for cost optimization
    - Historical price trend analysis for budgeting
    """
    try:
        price_data = await service.get_current_price(product, region, max_age_hours)
        
        if not price_data:
            raise HTTPException(
                status_code=404,
                detail=f"No price data available for {product.value} in {region}"
            )
        
        return price_data
        
    except Exception as e:
        logger.error(f"Error getting current price: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/current", response_model=Dict[str, Optional[FertilizerPriceData]])
async def get_current_prices(
    products: List[FertilizerProduct] = Query(..., description="List of fertilizer products"),
    region: str = Query("US", description="Geographic region"),
    max_age_hours: int = Query(24, description="Maximum age of cached data in hours"),
    service: FertilizerPriceTrackingService = Depends(get_price_service)
):
    """
    Get current prices for multiple fertilizer products.
    
    Efficient endpoint for retrieving prices for multiple products
    simultaneously, useful for comprehensive fertilizer cost analysis
    and comparison across different fertilizer types.
    
    Agricultural Use Cases:
    - Multi-product cost comparison for fertilizer selection
    - Bulk pricing analysis for large-scale operations
    - Market overview for strategic planning
    - Cost-benefit analysis across fertilizer types
    """
    try:
        if len(products) > 20:
            raise HTTPException(
                status_code=400,
                detail="Maximum 20 products per request"
            )
        
        prices = await service.get_current_prices(products, region, max_age_hours)
        return prices
        
    except Exception as e:
        logger.error(f"Error getting current prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trend/{product}", response_model=PriceTrendAnalysis)
async def get_price_trend(
    product: FertilizerProduct,
    region: str = Query("US", description="Geographic region"),
    days: int = Query(30, ge=7, le=365, description="Number of days for trend analysis"),
    service: FertilizerPriceTrackingService = Depends(get_price_service)
):
    """
    Get price trend analysis for a fertilizer product.
    
    This endpoint provides comprehensive trend analysis including
    price changes over different time periods, volatility metrics,
    and trend direction indicators for informed decision making.
    
    Agricultural Use Cases:
    - Price trend analysis for timing fertilizer purchases
    - Volatility assessment for risk management
    - Market direction analysis for strategic planning
    - Historical performance evaluation
    """
    try:
        trend_analysis = await service.get_price_trend(product, region, days)
        
        if not trend_analysis:
            raise HTTPException(
                status_code=404,
                detail=f"Insufficient data for trend analysis of {product.value} in {region}"
            )
        
        return trend_analysis
        
    except Exception as e:
        logger.error(f"Error getting price trend: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=PriceQueryResponse)
async def query_prices(
    request: PriceQueryRequest,
    service: FertilizerPriceTrackingService = Depends(get_price_service)
):
    """
    Execute a comprehensive price query with filters and analysis.
    
    This endpoint allows for complex price queries with multiple filters,
    including product types, regions, date ranges, and analysis options.
    Ideal for detailed market analysis and reporting.
    
    Agricultural Use Cases:
    - Comprehensive market analysis across multiple products
    - Regional price comparison studies
    - Historical price analysis for trend identification
    - Custom reporting for agricultural planning
    """
    try:
        response = await service.query_prices(request)
        return response
        
    except Exception as e:
        logger.error(f"Error executing price query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update/{product}", response_model=PriceUpdateResponse)
async def update_price(
    product: FertilizerProduct,
    region: str = Query("US", description="Geographic region"),
    force_update: bool = Query(False, description="Force update even if recent data exists"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    service: FertilizerPriceTrackingService = Depends(get_price_service)
):
    """
    Update price data for a specific fertilizer product.
    
    This endpoint triggers a fresh price update from external data sources.
    Useful for ensuring the most current pricing information is available
    for critical decision making.
    
    Agricultural Use Cases:
    - Manual price refresh for time-sensitive decisions
    - Data quality assurance and validation
    - Scheduled price updates for automated systems
    - Emergency price verification during market volatility
    """
    try:
        response = await service.update_price(product, region, force_update)
        return response
        
    except Exception as e:
        logger.error(f"Error updating price: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update-all", response_model=Dict[str, PriceUpdateResponse])
async def update_all_prices(
    products: Optional[List[FertilizerProduct]] = Query(None, description="Products to update (all if not specified)"),
    region: str = Query("US", description="Geographic region"),
    force_update: bool = Query(False, description="Force update even if recent data exists"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    service: FertilizerPriceTrackingService = Depends(get_price_service)
):
    """
    Update price data for multiple fertilizer products.
    
    This endpoint triggers price updates for multiple products simultaneously,
    useful for comprehensive market data refresh and system maintenance.
    
    Agricultural Use Cases:
    - Bulk price updates for system maintenance
    - Market data refresh for comprehensive analysis
    - Scheduled updates for automated systems
    - Data synchronization across multiple products
    """
    try:
        if products is None:
            products = list(FertilizerProduct)
        
        if len(products) > 50:
            raise HTTPException(
                status_code=400,
                detail="Maximum 50 products per update request"
            )
        
        results = {}
        for product in products:
            response = await service.update_price(product, region, force_update)
            results[product.value] = response
        
        return results
        
    except Exception as e:
        logger.error(f"Error updating all prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products", response_model=List[Dict[str, Any]])
async def get_available_products():
    """
    Get list of available fertilizer products for price tracking.
    
    This endpoint provides a comprehensive list of all fertilizer products
    that can be tracked, including their types and specifications.
    
    Agricultural Use Cases:
    - Product discovery for price tracking
    - System integration and configuration
    - Product catalog for user interfaces
    - API documentation and reference
    """
    try:
        products = []
        for product in FertilizerProduct:
            products.append({
                "product_id": product.value,
                "product_name": product.value.replace("_", " ").title(),
                "description": f"{product.value.replace('_', ' ').title()} fertilizer product"
            })
        
        return products
        
    except Exception as e:
        logger.error(f"Error getting available products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/types", response_model=List[Dict[str, Any]])
async def get_fertilizer_types():
    """
    Get list of available fertilizer types.
    
    This endpoint provides fertilizer type categories for filtering
    and organizing price data by fertilizer classification.
    
    Agricultural Use Cases:
    - Type-based price filtering
    - Category-based analysis
    - System configuration
    - User interface organization
    """
    try:
        types = []
        for fertilizer_type in FertilizerType:
            types.append({
                "type_id": fertilizer_type.value,
                "type_name": fertilizer_type.value.title(),
                "description": f"{fertilizer_type.value.title()} fertilizer category"
            })
        
        return types
        
    except Exception as e:
        logger.error(f"Error getting fertilizer types: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sources", response_model=List[Dict[str, Any]])
async def get_price_sources():
    """
    Get list of available price data sources.
    
    This endpoint provides information about all data sources
    used for fertilizer price tracking, including their reliability
    and update frequency.
    
    Agricultural Use Cases:
    - Data source transparency
    - Reliability assessment
    - Source-specific analysis
    - Quality assurance
    """
    try:
        sources = []
        for source in PriceSource:
            source_info = {
                "source_id": source.value,
                "source_name": source.value.replace("_", " ").title(),
                "description": f"{source.value.replace('_', ' ').title()} price data source"
            }
            
            # Add specific information for each source
            if source == PriceSource.USDA_NASS:
                source_info["reliability"] = "High"
                source_info["update_frequency"] = "Daily"
            elif source == PriceSource.CME_GROUP:
                source_info["reliability"] = "High"
                source_info["update_frequency"] = "Real-time"
            elif source == PriceSource.MANUFACTURER:
                source_info["reliability"] = "Medium"
                source_info["update_frequency"] = "Weekly"
            elif source == PriceSource.REGIONAL_DEALER:
                source_info["reliability"] = "Medium"
                source_info["update_frequency"] = "Daily"
            elif source == PriceSource.FALLBACK:
                source_info["reliability"] = "Low"
                source_info["update_frequency"] = "Static"
            
            sources.append(source_info)
        
        return sources
        
    except Exception as e:
        logger.error(f"Error getting price sources: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scheduler/status")
async def get_scheduler_status():
    """
    Get current scheduler status and job information.
    
    This endpoint provides information about the scheduled price update jobs,
    including their status, next run times, and configuration.
    
    Agricultural Use Cases:
    - Monitor automated price collection system
    - Verify scheduled updates are running properly
    - Troubleshoot price data freshness issues
    - System administration and maintenance
    """
    try:
        scheduler = await get_scheduler()
        status = scheduler.get_scheduler_status()
        return status
    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scheduler/trigger-update")
async def trigger_manual_update(
    product: Optional[FertilizerProduct] = Query(None, description="Specific product to update (all if not specified)"),
    region: str = Query("US", description="Region for price update")
):
    """
    Trigger a manual price update.
    
    This endpoint allows manual triggering of price updates outside of the
    scheduled intervals, useful for immediate data refresh or testing.
    
    Agricultural Use Cases:
    - Manual price refresh for time-sensitive decisions
    - Testing price update functionality
    - Emergency data refresh during market volatility
    - System maintenance and validation
    """
    try:
        scheduler = await get_scheduler()
        result = await scheduler.trigger_manual_update(product, region)
        return result
    except Exception as e:
        logger.error(f"Error triggering manual update: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint for price tracking service."""
    return {
        "service": "fertilizer-price-tracking",
        "status": "healthy",
        "features": [
            "real_time_price_tracking",
            "historical_price_analysis",
            "price_trend_calculation",
            "multi_source_data_integration",
            "regional_price_variations",
            "volatility_analysis",
            "caching_and_performance",
            "data_validation",
            "scheduled_price_updates",
            "automated_data_collection"
        ]
    }
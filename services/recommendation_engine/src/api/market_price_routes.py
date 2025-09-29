"""
Market Price API Routes
Provides REST endpoints for accessing crop market price data.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any, Optional
from datetime import date, datetime
import asyncio

from ..services.market_price_service import MarketPriceService, PriceTrend


router = APIRouter(prefix="/api/v1/market-prices", tags=["market-prices"])

# Singleton service instance
_market_price_service = None


def get_market_price_service() -> MarketPriceService:
    """Dependency to get market price service instance."""
    global _market_price_service
    if _market_price_service is None:
        _market_price_service = MarketPriceService()
    return _market_price_service


@router.get("/current")
async def get_current_prices(
    crops: List[str] = Query(..., description="List of crop names to get prices for"),
    region: str = Query("US", description="Geographic region for prices"),
    service: MarketPriceService = Depends(get_market_price_service)
) -> Dict[str, Any]:
    """
    Get current market prices for specified crops.
    
    Args:
        crops: List of crop names (corn, soybean, wheat, etc.)
        region: Geographic region (default: US)
        
    Returns:
        Dictionary with crop prices and metadata
    """
    try:
        prices = await service.get_current_prices(crops, region)
        
        return {
            "success": True,
            "data": prices,
            "region": region,
            "timestamp": datetime.now().isoformat(),
            "crops_requested": len(crops),
            "crops_found": len(prices)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching current prices: {str(e)}")


@router.get("/current/{crop_name}")
async def get_current_price(
    crop_name: str,
    region: str = Query("US", description="Geographic region for prices"),
    service: MarketPriceService = Depends(get_market_price_service)
) -> Dict[str, Any]:
    """
    Get current market price for a specific crop.
    
    Args:
        crop_name: Name of the crop
        region: Geographic region (default: US)
        
    Returns:
        Current price data for the crop
    """
    try:
        price = await service.get_current_price(crop_name, region)
        
        if not price:
            raise HTTPException(status_code=404, detail=f"Price not found for crop: {crop_name}")
        
        return {
            "success": True,
            "data": {
                "crop_name": price.crop_name,
                "price_per_unit": price.price_per_unit,
                "unit": price.unit,
                "region": price.region,
                "source": price.source,
                "confidence": price.confidence,
                "volatility": price.volatility,
                "price_date": price.price_date.isoformat(),
                "last_updated": price.created_at.isoformat()
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching price for {crop_name}: {str(e)}")


@router.get("/trends/{crop_name}")
async def get_price_trends(
    crop_name: str,
    region: str = Query("US", description="Geographic region for trends"),
    service: MarketPriceService = Depends(get_market_price_service)
) -> Dict[str, Any]:
    """
    Get price trend analysis for a specific crop.
    
    Args:
        crop_name: Name of the crop
        region: Geographic region (default: US)
        
    Returns:
        Price trend analysis including 7-day and 30-day trends
    """
    try:
        trend = service.get_price_trend(crop_name, region)
        
        if not trend:
            raise HTTPException(status_code=404, detail=f"Trend data not found for crop: {crop_name}")
        
        return {
            "success": True,
            "data": {
                "crop_name": trend.crop_name,
                "current_price": trend.current_price,
                "price_7d_ago": trend.price_7d_ago,
                "price_30d_ago": trend.price_30d_ago,
                "trend_7d_percent": round(trend.trend_7d_percent, 2),
                "trend_30d_percent": round(trend.trend_30d_percent, 2),
                "volatility": round(trend.volatility, 3),
                "trend_direction": trend.trend_direction
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching trends for {crop_name}: {str(e)}")


@router.get("/history/{crop_name}")
async def get_price_history(
    crop_name: str,
    days: int = Query(30, ge=1, le=365, description="Number of days of history to retrieve"),
    region: str = Query("US", description="Geographic region for history"),
    service: MarketPriceService = Depends(get_market_price_service)
) -> Dict[str, Any]:
    """
    Get historical price data for a specific crop.
    
    Args:
        crop_name: Name of the crop
        days: Number of days of history (1-365)
        region: Geographic region (default: US)
        
    Returns:
        Historical price data
    """
    try:
        history = service.cache_manager.get_price_history(crop_name, days)
        
        if not history:
            raise HTTPException(status_code=404, detail=f"No historical data found for crop: {crop_name}")
        
        history_data = [
            {
                "price_per_unit": record.price_per_unit,
                "unit": record.unit,
                "price_date": record.price_date.isoformat(),
                "source": record.source,
                "confidence": record.confidence
            }
            for record in history
        ]
        
        return {
            "success": True,
            "data": {
                "crop_name": crop_name,
                "region": region,
                "days_requested": days,
                "records_found": len(history_data),
                "price_history": history_data
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching history for {crop_name}: {str(e)}")


@router.post("/update")
async def update_prices(
    crops: Optional[List[str]] = None,
    service: MarketPriceService = Depends(get_market_price_service)
) -> Dict[str, Any]:
    """
    Manually trigger price updates for specified crops or all crops.
    
    Args:
        crops: Optional list of specific crops to update (if None, updates all)
        
    Returns:
        Update results for each crop
    """
    try:
        results = await service.update_all_prices(crops)
        
        successful_updates = sum(1 for success in results.values() if success)
        total_attempts = len(results)
        
        return {
            "success": True,
            "data": {
                "update_results": results,
                "successful_updates": successful_updates,
                "total_attempts": total_attempts,
                "success_rate": round(successful_updates / total_attempts * 100, 1) if total_attempts > 0 else 0
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating prices: {str(e)}")


@router.get("/supported-crops")
async def get_supported_crops(
    service: MarketPriceService = Depends(get_market_price_service)
) -> Dict[str, Any]:
    """
    Get list of supported crops for price tracking.
    
    Returns:
        List of supported crop names and their details
    """
    try:
        supported_crops = []
        for crop_name, data in service.fallback_prices.items():
            supported_crops.append({
                "crop_name": crop_name,
                "unit": data["unit"],
                "baseline_price": data["price_per_unit"],
                "volatility": data["volatility"]
            })
        
        return {
            "success": True,
            "data": {
                "supported_crops": supported_crops,
                "total_crops": len(supported_crops)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching supported crops: {str(e)}")


@router.get("/health")
async def health_check(
    service: MarketPriceService = Depends(get_market_price_service)
) -> Dict[str, Any]:
    """
    Health check endpoint for the market price service.
    
    Returns:
        Service health status and basic diagnostics
    """
    try:
        # Test with a sample crop
        test_price = await service.get_current_price("corn")
        price_service_working = test_price is not None
        
        # Check cache connectivity
        cache_working = True
        try:
            service.cache_manager.get_cached_price("corn")
        except Exception:
            cache_working = False
        
        return {
            "success": True,
            "data": {
                "service_status": "healthy" if price_service_working else "degraded",
                "price_service_working": price_service_working,
                "cache_working": cache_working,
                "providers_count": len(service.providers),
                "fallback_crops_count": len(service.fallback_prices)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": {
                "service_status": "unhealthy",
                "price_service_working": False,
                "cache_working": False
            },
            "timestamp": datetime.now().isoformat()
        }
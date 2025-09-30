"""
Commodity price tracking and analysis service.
"""

import asyncio
import logging
import time
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from uuid import uuid4

from ..models.commodity_price_models import (
    CommodityPriceData, CommodityTrendAnalysis, FertilizerCropPriceRatio,
    CommodityPriceQueryRequest, CommodityPriceQueryResponse, CommodityMarketIntelligence,
    BasisAnalysis, CommodityType, CommodityContract, CommoditySource
)
from ..services.commodity_price_providers import CommodityProviderManager
from ..database.commodity_price_db import CommodityPriceDatabase

logger = logging.getLogger(__name__)


class CommodityPriceService:
    """Core commodity price tracking and analysis service."""
    
    def __init__(self):
        self.provider_manager = CommodityProviderManager()
        self.db = CommodityPriceDatabase()
    
    async def get_current_price(
        self, 
        commodity: CommodityType, 
        region: str, 
        contract_type: CommodityContract = CommodityContract.CASH,
        max_age_hours: int = 24
    ) -> Optional[CommodityPriceData]:
        """
        Get current commodity price data.
        
        Args:
            commodity: Type of commodity
            region: Geographic region
            contract_type: Type of contract (cash/futures)
            max_age_hours: Maximum age of cached data
            
        Returns:
            CommodityPriceData or None if not available
        """
        try:
            # Check cache first
            cached_price = await self.db.get_cached_price(commodity, region, contract_type, max_age_hours)
            if cached_price:
                logger.info(f"Cache hit for {commodity.value} in {region}")
                return cached_price
            
            # Fetch from providers
            price_data_list = await self.provider_manager.fetch_price_from_all_sources(
                commodity, region, contract_type
            )
            
            if not price_data_list:
                logger.warning(f"No price data available for {commodity.value} in {region}")
                return None
            
            # Select best price (highest confidence)
            best_price = max(price_data_list, key=lambda p: p.confidence)
            
            # Cache the result
            await self.db.cache_price(best_price)
            
            return best_price
            
        except Exception as e:
            logger.error(f"Error getting current price for {commodity.value}: {e}")
            return None
    
    async def get_current_prices(
        self, 
        commodities: List[CommodityType], 
        region: str,
        contract_type: CommodityContract = CommodityContract.CASH,
        max_age_hours: int = 24
    ) -> Dict[str, Optional[CommodityPriceData]]:
        """Get current prices for multiple commodities."""
        try:
            if len(commodities) > 20:
                raise ValueError("Maximum 20 commodities per request")
            
            tasks = [
                self.get_current_price(commodity, region, contract_type, max_age_hours)
                for commodity in commodities
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            price_dict = {}
            for commodity, result in zip(commodities, results):
                if isinstance(result, Exception):
                    logger.warning(f"Error getting price for {commodity.value}: {result}")
                    price_dict[commodity.value] = None
                else:
                    price_dict[commodity.value] = result
            
            return price_dict
            
        except Exception as e:
            logger.error(f"Error getting current prices: {e}")
            return {}
    
    async def get_price_trend(
        self, 
        commodity: CommodityType, 
        region: str, 
        days: int = 30,
        contract_type: CommodityContract = CommodityContract.CASH
    ) -> Optional[CommodityTrendAnalysis]:
        """Get price trend analysis for a commodity."""
        try:
            # Get historical price data
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            historical_prices = await self.db.get_historical_prices(
                commodity, region, start_date, end_date, contract_type
            )
            
            if len(historical_prices) < 2:
                logger.warning(f"Insufficient data for trend analysis of {commodity.value}")
                return None
            
            # Sort by date
            historical_prices.sort(key=lambda p: p.price_date)
            
            # Calculate trend analysis
            current_price = historical_prices[-1]
            current_date = current_price.price_date
            
            # Calculate historical prices
            price_7d_ago = self._get_price_at_date(historical_prices, current_date - timedelta(days=7))
            price_30d_ago = self._get_price_at_date(historical_prices, current_date - timedelta(days=30))
            price_90d_ago = self._get_price_at_date(historical_prices, current_date - timedelta(days=90))
            price_1y_ago = self._get_price_at_date(historical_prices, current_date - timedelta(days=365))
            
            # Calculate trend percentages
            trend_7d_percent = self._calculate_trend_percent(current_price.price_per_unit, price_7d_ago)
            trend_30d_percent = self._calculate_trend_percent(current_price.price_per_unit, price_30d_ago)
            trend_90d_percent = self._calculate_trend_percent(current_price.price_per_unit, price_90d_ago)
            trend_1y_percent = self._calculate_trend_percent(current_price.price_per_unit, price_1y_ago)
            
            # Calculate volatility
            prices = [p.price_per_unit for p in historical_prices]
            volatility_7d = self._calculate_volatility(prices[-7:]) if len(prices) >= 7 else None
            volatility_30d = self._calculate_volatility(prices[-30:]) if len(prices) >= 30 else None
            volatility_90d = self._calculate_volatility(prices[-90:]) if len(prices) >= 90 else None
            volatility_1y = self._calculate_volatility(prices) if len(prices) >= 365 else None
            
            # Determine trend direction and strength
            trend_direction, trend_strength = self._analyze_trend_strength(trend_30d_percent)
            
            return CommodityTrendAnalysis(
                commodity_id=f"{commodity.value}_trend",
                commodity_name=commodity.value.title(),
                region=region,
                current_price=current_price.price_per_unit,
                current_date=current_date,
                price_7d_ago=price_7d_ago,
                price_30d_ago=price_30d_ago,
                price_90d_ago=price_90d_ago,
                price_1y_ago=price_1y_ago,
                trend_7d_percent=trend_7d_percent,
                trend_30d_percent=trend_30d_percent,
                trend_90d_percent=trend_90d_percent,
                trend_1y_percent=trend_1y_percent,
                volatility_7d=volatility_7d,
                volatility_30d=volatility_30d,
                volatility_90d=volatility_90d,
                volatility_1y=volatility_1y,
                trend_direction=trend_direction,
                trend_strength=trend_strength,
                data_points_used=len(historical_prices)
            )
            
        except Exception as e:
            logger.error(f"Error getting price trend for {commodity.value}: {e}")
            return None
    
    async def calculate_fertilizer_crop_price_ratios(
        self, 
        fertilizer_prices: Dict[str, float],
        crop_prices: Dict[str, float],
        region: str
    ) -> List[FertilizerCropPriceRatio]:
        """Calculate fertilizer-to-crop price ratios."""
        try:
            ratios = []
            
            # Define fertilizer-crop relationships
            fertilizer_crop_mapping = {
                "urea": [CommodityType.CORN, CommodityType.WHEAT],
                "anhydrous_ammonia": [CommodityType.CORN, CommodityType.WHEAT],
                "dap": [CommodityType.CORN, CommodityType.SOYBEAN],
                "map": [CommodityType.CORN, CommodityType.SOYBEAN],
                "muriate_of_potash": [CommodityType.CORN, CommodityType.SOYBEAN, CommodityType.WHEAT],
            }
            
            for fertilizer, price in fertilizer_prices.items():
                if fertilizer in fertilizer_crop_mapping:
                    for crop_type in fertilizer_crop_mapping[fertilizer]:
                        crop_key = crop_type.value
                        if crop_key in crop_prices:
                            crop_price = crop_prices[crop_key]
                            
                            # Calculate ratios
                            price_ratio = price / crop_price
                            inverse_ratio = crop_price / price
                            
                            # Determine profitability indicator
                            profitability = self._assess_profitability(price_ratio, fertilizer, crop_type)
                            
                            ratio = FertilizerCropPriceRatio(
                                ratio_id=f"{fertilizer}_{crop_key}_{region}",
                                fertilizer_product=fertilizer,
                                commodity_type=crop_type,
                                region=region,
                                fertilizer_price=price,
                                fertilizer_unit="ton",
                                crop_price=crop_price,
                                crop_unit="bushel",
                                price_ratio=price_ratio,
                                inverse_ratio=inverse_ratio,
                                ratio_trend="stable",  # Would calculate from historical data
                                profitability_indicator=profitability,
                                analysis_date=date.today(),
                                confidence=0.85
                            )
                            ratios.append(ratio)
            
            return ratios
            
        except Exception as e:
            logger.error(f"Error calculating price ratios: {e}")
            return []
    
    async def calculate_basis_analysis(
        self, 
        commodity: CommodityType, 
        region: str
    ) -> Optional[BasisAnalysis]:
        """Calculate basis analysis (cash price - futures price)."""
        try:
            # Get cash and futures prices
            cash_price_data = await self.get_current_price(commodity, region, CommodityContract.CASH)
            futures_price_data = await self.get_current_price(commodity, region, CommodityContract.FUTURES)
            
            if not cash_price_data or not futures_price_data:
                logger.warning(f"Insufficient data for basis analysis of {commodity.value}")
                return None
            
            cash_price = cash_price_data.price_per_unit
            futures_price = futures_price_data.price_per_unit
            basis_value = cash_price - futures_price
            
            # Analyze basis trend and strength
            basis_trend, basis_strength = self._analyze_basis_strength(basis_value)
            
            return BasisAnalysis(
                basis_id=f"{commodity.value}_basis_{region}",
                commodity_type=commodity,
                region=region,
                cash_price=cash_price,
                futures_price=futures_price,
                basis_value=basis_value,
                basis_trend=basis_trend,
                basis_strength=basis_strength,
                analysis_date=date.today(),
                delivery_location=region
            )
            
        except Exception as e:
            logger.error(f"Error calculating basis analysis: {e}")
            return None
    
    async def query_prices(self, request: CommodityPriceQueryRequest) -> CommodityPriceQueryResponse:
        """Execute comprehensive commodity price query."""
        start_time = time.time()
        query_id = str(uuid4())
        
        try:
            # Get price data
            prices = []
            if request.commodity_types:
                for commodity in request.commodity_types:
                    price_data = await self.get_current_price(commodity, "US")
                    if price_data:
                        prices.append(price_data)
            
            # Get trend analyses if requested
            trend_analyses = []
            if request.include_trend_analysis and request.commodity_types:
                for commodity in request.commodity_types:
                    trend = await self.get_price_trend(commodity, "US", 30)
                    if trend:
                        trend_analyses.append(trend)
            
            # Calculate price ratios if requested
            price_ratios = []
            if request.include_price_ratios:
                # This would integrate with fertilizer price service
                # For now, return empty list
                pass
            
            processing_time_ms = (time.time() - start_time) * 1000
            
            return CommodityPriceQueryResponse(
                query_id=query_id,
                prices=prices,
                trend_analyses=trend_analyses if trend_analyses else None,
                price_ratios=price_ratios if price_ratios else None,
                total_results=len(prices),
                data_sources_used=list(CommoditySource),
                cache_hit_rate=0.8,  # Would calculate actual cache hit rate
                processing_time_ms=processing_time_ms
            )
            
        except Exception as e:
            logger.error(f"Error executing price query: {e}")
            raise
    
    def _get_price_at_date(self, prices: List[CommodityPriceData], target_date: date) -> Optional[float]:
        """Get price at or before target date."""
        for price in reversed(prices):
            if price.price_date <= target_date:
                return price.price_per_unit
        return None
    
    def _calculate_trend_percent(self, current_price: float, historical_price: Optional[float]) -> Optional[float]:
        """Calculate trend percentage."""
        if historical_price is None or historical_price == 0:
            return None
        return ((current_price - historical_price) / historical_price) * 100
    
    def _calculate_volatility(self, prices: List[float]) -> float:
        """Calculate price volatility."""
        if len(prices) < 2:
            return 0.0
        
        import statistics
        mean_price = statistics.mean(prices)
        variance = statistics.variance(prices, mean_price)
        return variance ** 0.5 / mean_price if mean_price > 0 else 0.0
    
    def _analyze_trend_strength(self, trend_percent: Optional[float]) -> tuple[str, str]:
        """Analyze trend direction and strength."""
        if trend_percent is None:
            return "stable", "weak"
        
        if abs(trend_percent) < 2:
            return "stable", "weak"
        elif abs(trend_percent) < 5:
            return "up" if trend_percent > 0 else "down", "moderate"
        else:
            return "up" if trend_percent > 0 else "down", "strong"
    
    def _assess_profitability(self, price_ratio: float, fertilizer: str, crop_type: CommodityType) -> str:
        """Assess profitability based on fertilizer-crop price ratio."""
        # Define typical profitable ratios (would be more sophisticated in production)
        profitable_ratios = {
            "urea": {"corn": 0.1, "wheat": 0.12},
            "anhydrous_ammonia": {"corn": 0.15, "wheat": 0.18},
            "dap": {"corn": 0.08, "soybean": 0.1},
            "map": {"corn": 0.09, "soybean": 0.11},
            "muriate_of_potash": {"corn": 0.06, "soybean": 0.08, "wheat": 0.07},
        }
        
        if fertilizer in profitable_ratios and crop_type.value in profitable_ratios[fertilizer]:
            threshold = profitable_ratios[fertilizer][crop_type.value]
            return "favorable" if price_ratio <= threshold else "unfavorable"
        
        return "neutral"
    
    def _analyze_basis_strength(self, basis_value: float) -> tuple[str, str]:
        """Analyze basis strength."""
        if abs(basis_value) < 0.1:
            return "stable", "weak"
        elif abs(basis_value) < 0.25:
            return "strong" if basis_value > 0 else "weak", "moderate"
        else:
            return "strong" if basis_value > 0 else "weak", "strong"
    
    async def close(self):
        """Close service resources."""
        await self.provider_manager.close_all()
        await self.db.close()
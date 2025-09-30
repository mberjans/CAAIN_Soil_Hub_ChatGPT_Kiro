"""
Database layer for commodity price storage and retrieval.
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
import json

from ..models.commodity_price_models import (
    CommodityPriceData, CommodityType, CommodityContract, CommoditySource
)

logger = logging.getLogger(__name__)


class CommodityPriceDatabase:
    """Database interface for commodity price data."""
    
    def __init__(self):
        self.redis_client = None
        self.postgres_client = None
    
    async def initialize(self):
        """Initialize database connections."""
        try:
            # Initialize Redis for caching
            import redis.asyncio as redis
            self.redis_client = redis.from_url("redis://localhost:6379")
            
            # Initialize PostgreSQL for persistent storage
            # In production, this would use asyncpg or similar
            logger.info("Commodity price database initialized")
            
        except Exception as e:
            logger.error(f"Error initializing commodity price database: {e}")
            raise
    
    async def cache_price(self, price_data: CommodityPriceData, ttl_seconds: int = 86400):
        """Cache commodity price data."""
        try:
            if not self.redis_client:
                await self.initialize()
            
            cache_key = f"commodity_price:{price_data.commodity_type.value}:{price_data.region}:{price_data.contract_type.value}"
            
            await self.redis_client.setex(
                cache_key,
                ttl_seconds,
                price_data.json()
            )
            
            logger.debug(f"Cached price data for {cache_key}")
            
        except Exception as e:
            logger.error(f"Error caching price data: {e}")
    
    async def get_cached_price(
        self, 
        commodity: CommodityType, 
        region: str, 
        contract_type: CommodityContract,
        max_age_hours: int = 24
    ) -> Optional[CommodityPriceData]:
        """Get cached commodity price data."""
        try:
            if not self.redis_client:
                await self.initialize()
            
            cache_key = f"commodity_price:{commodity.value}:{region}:{contract_type.value}"
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                data_dict = json.loads(cached_data)
                return CommodityPriceData(**data_dict)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached price data: {e}")
            return None
    
    async def store_price_data(self, price_data: CommodityPriceData):
        """Store commodity price data in persistent storage."""
        try:
            # In production, this would store in PostgreSQL/TimescaleDB
            # For now, we'll just log the data
            logger.info(f"Storing price data: {price_data.commodity_name} at ${price_data.price_per_unit}/{price_data.unit}")
            
            # Store in cache as well
            await self.cache_price(price_data)
            
        except Exception as e:
            logger.error(f"Error storing price data: {e}")
    
    async def get_historical_prices(
        self, 
        commodity: CommodityType, 
        region: str, 
        start_date: date, 
        end_date: date,
        contract_type: CommodityContract = CommodityContract.CASH
    ) -> List[CommodityPriceData]:
        """Get historical commodity price data."""
        try:
            # In production, this would query PostgreSQL/TimescaleDB
            # For now, return mock historical data
            historical_prices = []
            
            current_date = start_date
            base_price = 4.75  # Mock base price
            
            while current_date <= end_date:
                # Mock price variation
                price_variation = (hash(str(current_date)) % 100) / 1000  # Small random variation
                price = base_price + price_variation
                
                price_data = CommodityPriceData(
                    commodity_id=f"historical_{commodity.value}_{current_date}",
                    commodity_name=f"{commodity.value.title()} (Historical)",
                    commodity_type=commodity,
                    contract_type=contract_type,
                    price_per_unit=price,
                    unit="bushel",
                    region=region,
                    source=CommoditySource.USDA_NASS,
                    price_date=current_date,
                    is_spot_price=True,
                    is_futures_price=False,
                    confidence=0.90,
                    volatility=0.15,
                    market_conditions={"historical_data": True},
                    seasonal_factors={"historical_analysis": True}
                )
                
                historical_prices.append(price_data)
                current_date += timedelta(days=1)
            
            return historical_prices
            
        except Exception as e:
            logger.error(f"Error getting historical prices: {e}")
            return []
    
    async def get_price_statistics(
        self, 
        commodity: CommodityType, 
        region: str, 
        days: int = 30
    ) -> Dict[str, Any]:
        """Get price statistics for a commodity."""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            historical_prices = await self.get_historical_prices(
                commodity, region, start_date, end_date
            )
            
            if not historical_prices:
                return {}
            
            prices = [p.price_per_unit for p in historical_prices]
            
            return {
                "min_price": min(prices),
                "max_price": max(prices),
                "avg_price": sum(prices) / len(prices),
                "price_range": max(prices) - min(prices),
                "data_points": len(prices),
                "period_days": days
            }
            
        except Exception as e:
            logger.error(f"Error getting price statistics: {e}")
            return {}
    
    async def search_prices(
        self, 
        filters: Dict[str, Any]
    ) -> List[CommodityPriceData]:
        """Search commodity prices with filters."""
        try:
            # In production, this would query the database with filters
            # For now, return mock results
            return []
            
        except Exception as e:
            logger.error(f"Error searching prices: {e}")
            return []
    
    async def cleanup_old_data(self, days_to_keep: int = 365):
        """Clean up old price data."""
        try:
            # In production, this would delete old records from the database
            logger.info(f"Cleaning up price data older than {days_to_keep} days")
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
    
    async def close(self):
        """Close database connections."""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            logger.info("Commodity price database connections closed")
            
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")


# Database initialization functions
async def initialize_commodity_database():
    """Initialize commodity price database."""
    db = CommodityPriceDatabase()
    await db.initialize()
    return db


async def shutdown_commodity_database(db: CommodityPriceDatabase):
    """Shutdown commodity price database."""
    await db.close()
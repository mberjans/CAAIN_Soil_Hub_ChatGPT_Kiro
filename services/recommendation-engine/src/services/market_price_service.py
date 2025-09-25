"""
Market Price Service
Provides real-time and cached market prices for agricultural commodities
integrating with multiple data sources like USDA NASS API.
"""

import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta, date
from dataclasses import dataclass, asdict
import logging
import sqlite3

logger = logging.getLogger(__name__)


@dataclass
class CropPrice:
    """Data model for crop price information."""
    crop_name: str
    price_per_unit: float
    unit: str  # bushel, ton, cwt, etc.
    region: str
    source: str
    price_date: date
    confidence: float
    volatility: float
    created_at: datetime


@dataclass
class PriceTrend:
    """Price trend analysis data."""
    crop_name: str
    current_price: float
    price_7d_ago: float
    price_30d_ago: float
    trend_7d_percent: float
    trend_30d_percent: float
    volatility: float
    trend_direction: str  # "up", "down", "stable"


class USDANASSProvider:
    """USDA NASS API provider for crop prices."""
    
    def __init__(self):
        self.base_url = "https://quickstats.nass.usda.gov/api"
        self.api_key = None  # Would be loaded from environment in production
        
    async def fetch_crop_price(self, crop_name: str, region: str = "US") -> Optional[CropPrice]:
        """Fetch current crop price from USDA NASS."""
        try:
            # Mock implementation for development - would use real API in production
            mock_prices = {
                "corn": {"price": 4.35, "unit": "bushel"},
                "soybean": {"price": 12.75, "unit": "bushel"},
                "wheat": {"price": 7.10, "unit": "bushel"},
                "oats": {"price": 3.45, "unit": "bushel"},
                "barley": {"price": 4.75, "unit": "bushel"},
                "alfalfa": {"price": 185.0, "unit": "ton"}
            }
            
            if crop_name.lower() in mock_prices:
                price_data = mock_prices[crop_name.lower()]
                return CropPrice(
                    crop_name=crop_name.lower(),
                    price_per_unit=price_data["price"],
                    unit=price_data["unit"],
                    region=region,
                    source="USDA_NASS_MOCK",
                    price_date=date.today(),
                    confidence=0.85,
                    volatility=0.15,
                    created_at=datetime.now()
                )
            return None
            
        except Exception as e:
            logger.error(f"Error fetching price for {crop_name}: {e}")
            return None


class CMEGroupProvider:
    """CME Group commodity futures provider."""
    
    async def fetch_crop_price(self, crop_name: str, region: str = "US") -> Optional[CropPrice]:
        """Fetch futures price from CME Group."""
        try:
            # Mock implementation - would integrate with real CME API
            futures_prices = {
                "corn": {"price": 4.28, "unit": "bushel"},
                "soybean": {"price": 12.68, "unit": "bushel"},
                "wheat": {"price": 7.02, "unit": "bushel"}
            }
            
            if crop_name.lower() in futures_prices:
                price_data = futures_prices[crop_name.lower()]
                return CropPrice(
                    crop_name=crop_name.lower(),
                    price_per_unit=price_data["price"],
                    unit=price_data["unit"],
                    region=region,
                    source="CME_FUTURES_MOCK",
                    price_date=date.today(),
                    confidence=0.90,
                    volatility=0.18,
                    created_at=datetime.now()
                )
            return None
            
        except Exception as e:
            logger.error(f"Error fetching futures price for {crop_name}: {e}")
            return None


class PriceCacheManager:
    """Manages price data caching and storage."""
    
    def __init__(self, db_path: str = "market_prices.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for price caching."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS crop_prices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    crop_name TEXT NOT NULL,
                    price_per_unit REAL NOT NULL,
                    unit TEXT NOT NULL,
                    region TEXT NOT NULL,
                    source TEXT NOT NULL,
                    price_date DATE NOT NULL,
                    confidence REAL NOT NULL,
                    volatility REAL NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    UNIQUE(crop_name, region, source, price_date)
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_crop_prices_crop_date 
                ON crop_prices(crop_name, price_date)
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    def cache_price(self, price: CropPrice) -> bool:
        """Cache a price record."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO crop_prices 
                (crop_name, price_per_unit, unit, region, source, price_date, 
                 confidence, volatility, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                price.crop_name, price.price_per_unit, price.unit, price.region,
                price.source, price.price_date, price.confidence, price.volatility,
                price.created_at
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error caching price: {e}")
            return False
    
    def get_cached_price(self, crop_name: str, region: str = "US", 
                        max_age_hours: int = 24) -> Optional[CropPrice]:
        """Get cached price if available and fresh."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            
            cursor.execute("""
                SELECT crop_name, price_per_unit, unit, region, source, price_date,
                       confidence, volatility, created_at
                FROM crop_prices 
                WHERE crop_name = ? AND region = ? AND created_at > ?
                ORDER BY created_at DESC LIMIT 1
            """, (crop_name, region, cutoff_time))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return CropPrice(
                    crop_name=row[0],
                    price_per_unit=row[1],
                    unit=row[2],
                    region=row[3],
                    source=row[4],
                    price_date=datetime.strptime(row[5], "%Y-%m-%d").date(),
                    confidence=row[6],
                    volatility=row[7],
                    created_at=datetime.fromisoformat(row[8])
                )
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached price: {e}")
            return None
    
    def get_price_history(self, crop_name: str, days: int = 30) -> List[CropPrice]:
        """Get price history for trend analysis."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = date.today() - timedelta(days=days)
            
            cursor.execute("""
                SELECT crop_name, price_per_unit, unit, region, source, price_date,
                       confidence, volatility, created_at
                FROM crop_prices 
                WHERE crop_name = ? AND price_date >= ?
                ORDER BY price_date DESC
            """, (crop_name, cutoff_date))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                CropPrice(
                    crop_name=row[0],
                    price_per_unit=row[1],
                    unit=row[2],
                    region=row[3],
                    source=row[4],
                    price_date=datetime.strptime(row[5], "%Y-%m-%d").date(),
                    confidence=row[6],
                    volatility=row[7],
                    created_at=datetime.fromisoformat(row[8])
                ) for row in rows
            ]
            
        except Exception as e:
            logger.error(f"Error getting price history: {e}")
            return []


class MarketPriceService:
    """Main service for managing crop market prices."""
    
    def __init__(self):
        self.providers = [
            USDANASSProvider(),
            CMEGroupProvider()
        ]
        self.cache_manager = PriceCacheManager()
        
        # Static fallback prices for resilience
        self.fallback_prices = {
            'corn': {'price_per_unit': 4.25, 'unit': 'bushel', 'volatility': 0.15},
            'soybean': {'price_per_unit': 12.50, 'unit': 'bushel', 'volatility': 0.18},
            'wheat': {'price_per_unit': 6.80, 'unit': 'bushel', 'volatility': 0.22},
            'oats': {'price_per_unit': 3.20, 'unit': 'bushel', 'volatility': 0.25},
            'alfalfa': {'price_per_unit': 180.0, 'unit': 'ton', 'volatility': 0.12},
            'barley': {'price_per_unit': 4.50, 'unit': 'bushel', 'volatility': 0.20}
        }
    
    async def get_current_price(self, crop_name: str, region: str = "US") -> Optional[CropPrice]:
        """Get current price for a crop, using cache first then providers."""
        
        # Try cache first
        cached_price = self.cache_manager.get_cached_price(crop_name, region)
        if cached_price:
            return cached_price
        
        # Try providers
        for provider in self.providers:
            try:
                price = await provider.fetch_crop_price(crop_name, region)
                if price:
                    # Cache the result
                    self.cache_manager.cache_price(price)
                    return price
            except Exception as e:
                logger.warning(f"Provider {provider.__class__.__name__} failed: {e}")
                continue
        
        # Fallback to static prices
        if crop_name.lower() in self.fallback_prices:
            fallback_data = self.fallback_prices[crop_name.lower()]
            return CropPrice(
                crop_name=crop_name.lower(),
                price_per_unit=fallback_data['price_per_unit'],
                unit=fallback_data['unit'],
                region=region,
                source="FALLBACK",
                price_date=date.today(),
                confidence=0.5,  # Lower confidence for fallback
                volatility=fallback_data['volatility'],
                created_at=datetime.now()
            )
        
        return None
    
    async def get_current_prices(self, crop_names: List[str], region: str = "US") -> Dict[str, Dict[str, Any]]:
        """Get current prices for multiple crops."""
        results = {}
        
        # Use asyncio.gather for concurrent price fetching
        tasks = [self.get_current_price(crop_name, region) for crop_name in crop_names]
        prices = await asyncio.gather(*tasks, return_exceptions=True)
        
        for crop_name, price in zip(crop_names, prices):
            if isinstance(price, CropPrice):
                results[crop_name] = {
                    'price_per_unit': price.price_per_unit,
                    'unit': price.unit,
                    'source': price.source,
                    'confidence': price.confidence,
                    'volatility': price.volatility,
                    'last_updated': price.created_at.isoformat()
                }
            elif isinstance(price, Exception):
                logger.error(f"Error fetching price for {crop_name}: {price}")
                # Return fallback if available
                if crop_name.lower() in self.fallback_prices:
                    fallback = self.fallback_prices[crop_name.lower()]
                    results[crop_name] = {
                        'price_per_unit': fallback['price_per_unit'],
                        'unit': fallback['unit'],
                        'source': 'FALLBACK',
                        'confidence': 0.5,
                        'volatility': fallback['volatility'],
                        'last_updated': datetime.now().isoformat()
                    }
        
        return results
    
    def get_price_trend(self, crop_name: str, region: str = "US") -> Optional[PriceTrend]:
        """Get price trend analysis for a crop."""
        history = self.cache_manager.get_price_history(crop_name, days=30)
        
        if not history:
            return None
        
        # Sort by date
        history.sort(key=lambda x: x.price_date, reverse=True)
        
        current_price = history[0].price_per_unit
        
        # Find prices 7 and 30 days ago
        price_7d_ago = current_price
        price_30d_ago = current_price
        
        today = date.today()
        for price_record in history:
            days_ago = (today - price_record.price_date).days
            if 6 <= days_ago <= 8:  # 7 days ago (±1 day tolerance)
                price_7d_ago = price_record.price_per_unit
            elif 28 <= days_ago <= 32:  # 30 days ago (±2 days tolerance)
                price_30d_ago = price_record.price_per_unit
        
        # Calculate trends
        trend_7d_percent = ((current_price - price_7d_ago) / price_7d_ago * 100) if price_7d_ago > 0 else 0
        trend_30d_percent = ((current_price - price_30d_ago) / price_30d_ago * 100) if price_30d_ago > 0 else 0
        
        # Calculate volatility
        prices = [p.price_per_unit for p in history]
        if len(prices) > 1:
            avg_price = sum(prices) / len(prices)
            variance = sum((p - avg_price) ** 2 for p in prices) / len(prices)
            volatility = (variance ** 0.5) / avg_price if avg_price > 0 else 0
        else:
            volatility = 0
        
        # Determine trend direction
        if trend_7d_percent > 2:
            trend_direction = "up"
        elif trend_7d_percent < -2:
            trend_direction = "down"
        else:
            trend_direction = "stable"
        
        return PriceTrend(
            crop_name=crop_name,
            current_price=current_price,
            price_7d_ago=price_7d_ago,
            price_30d_ago=price_30d_ago,
            trend_7d_percent=trend_7d_percent,
            trend_30d_percent=trend_30d_percent,
            volatility=volatility,
            trend_direction=trend_direction
        )
    
    async def update_all_prices(self, crop_names: List[str] = None) -> Dict[str, bool]:
        """Update prices for all or specified crops."""
        if crop_names is None:
            crop_names = list(self.fallback_prices.keys())
        
        results = {}
        for crop_name in crop_names:
            try:
                price = await self.get_current_price(crop_name)
                results[crop_name] = price is not None
            except Exception as e:
                logger.error(f"Error updating price for {crop_name}: {e}")
                results[crop_name] = False
        
        return results
    
    def validate_price(self, price: CropPrice) -> bool:
        """Validate price data for anomalies."""
        if price.price_per_unit <= 0:
            return False
        
        # Check against historical ranges (simplified validation)
        if price.crop_name.lower() in self.fallback_prices:
            baseline = self.fallback_prices[price.crop_name.lower()]['price_per_unit']
            # Flag if price is more than 50% different from baseline
            if abs(price.price_per_unit - baseline) / baseline > 0.5:
                logger.warning(f"Price anomaly detected for {price.crop_name}: {price.price_per_unit}")
                return False
        
        return True
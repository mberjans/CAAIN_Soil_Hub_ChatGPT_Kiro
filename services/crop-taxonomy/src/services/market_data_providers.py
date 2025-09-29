"""
Market Data Providers
Providers for collecting market data from various sources including commodity exchanges,
local elevators, contract pricing, and specialty markets.
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, date, timedelta
from decimal import Decimal

try:
    from ..models.market_intelligence_models import (
        VarietyMarketPrice, MarketType, QualityGrade, ContractType, MarketIntelligenceRequest
    )
    from ..models.crop_variety_models import EnhancedCropVariety
except ImportError:
    from models.market_intelligence_models import (
        VarietyMarketPrice, MarketType, QualityGrade, ContractType, MarketIntelligenceRequest
    )
    from models.crop_variety_models import EnhancedCropVariety

logger = logging.getLogger(__name__)


class BaseMarketProvider:
    """Base class for market data providers."""
    
    def __init__(self):
        self.session = None
        self.base_url = ""
        self.api_key = None
        
    async def get_session(self):
        """Get aiohttp session."""
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """Close aiohttp session."""
        if self.session:
            await self.session.close()
    
    async def get_variety_market_data(
        self, 
        variety: EnhancedCropVariety, 
        request: MarketIntelligenceRequest
    ) -> Optional[Dict[str, Any]]:
        """Get market data for a variety (to be implemented by subclasses)."""
        raise NotImplementedError


class CommodityExchangeProvider(BaseMarketProvider):
    """Provider for commodity exchange data (CME, CBOT, etc.)."""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.cmegroup.com"
        self.market_type = MarketType.COMMODITY_EXCHANGE
        
    async def get_variety_market_data(
        self, 
        variety: EnhancedCropVariety, 
        request: MarketIntelligenceRequest
    ) -> Optional[Dict[str, Any]]:
        """Get commodity exchange data for a variety."""
        try:
            # Mock implementation - would integrate with real CME API
            mock_data = self._get_mock_exchange_data(variety)
            
            return {
                'prices': mock_data.get('prices', []),
                'trends': mock_data.get('trends', []),
                'basis': mock_data.get('basis', []),
                'demand': mock_data.get('demand', []),
                'premiums': mock_data.get('premiums', [])
            }
            
        except Exception as e:
            logger.error(f"Error fetching exchange data for {variety.variety_name}: {e}")
            return None
    
    def _get_mock_exchange_data(self, variety: EnhancedCropVariety) -> Dict[str, Any]:
        """Generate mock exchange data for development."""
        base_prices = {
            'corn': Decimal('4.25'),
            'soybean': Decimal('12.50'),
            'wheat': Decimal('6.80'),
            'oats': Decimal('3.20'),
            'barley': Decimal('4.50')
        }
        
        base_price = base_prices.get(variety.crop_name.lower(), Decimal('5.00'))
        
        # Generate mock prices for different contracts
        prices = []
        for i, contract_type in enumerate([ContractType.CASH_PRICE, ContractType.FUTURES_CONTRACT]):
            price = VarietyMarketPrice(
                variety_id=variety.id if hasattr(variety, 'id') else None,
                variety_name=variety.variety_name,
                crop_name=variety.crop_name,
                price_per_unit=base_price + Decimal(str(i * 0.10)),
                unit="bushel",
                market_type=self.market_type,
                contract_type=contract_type,
                region="US",
                price_date=date.today(),
                source="CME_MOCK",
                confidence=0.9,
                last_updated=datetime.utcnow()
            )
            prices.append(price)
        
        # Generate mock trend data
        trends = [
            {
                'days_ago': 7,
                'price': float(base_price),
                'trend_percent': 2.5,
                'volatility': 0.15,
                'confidence': 0.9
            },
            {
                'days_ago': 30,
                'price': float(base_price - Decimal('0.20')),
                'trend_percent': 5.2,
                'volatility': 0.18,
                'confidence': 0.85
            }
        ]
        
        return {
            'prices': prices,
            'trends': trends,
            'basis': [],
            'demand': [],
            'premiums': []
        }


class LocalElevatorProvider(BaseMarketProvider):
    """Provider for local elevator pricing data."""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.local-elevators.com"  # Mock URL
        self.market_type = MarketType.LOCAL_ELEVATOR
        
    async def get_variety_market_data(
        self, 
        variety: EnhancedCropVariety, 
        request: MarketIntelligenceRequest
    ) -> Optional[Dict[str, Any]]:
        """Get local elevator data for a variety."""
        try:
            # Mock implementation - would integrate with real elevator APIs
            mock_data = self._get_mock_elevator_data(variety, request)
            
            return {
                'prices': mock_data.get('prices', []),
                'trends': mock_data.get('trends', []),
                'basis': mock_data.get('basis', []),
                'demand': mock_data.get('demand', []),
                'premiums': mock_data.get('premiums', [])
            }
            
        except Exception as e:
            logger.error(f"Error fetching elevator data for {variety.variety_name}: {e}")
            return None
    
    def _get_mock_elevator_data(
        self, 
        variety: EnhancedCropVariety, 
        request: MarketIntelligenceRequest
    ) -> Dict[str, Any]:
        """Generate mock elevator data for development."""
        base_prices = {
            'corn': Decimal('4.20'),
            'soybean': Decimal('12.45'),
            'wheat': Decimal('6.75'),
            'oats': Decimal('3.15'),
            'barley': Decimal('4.40')
        }
        
        base_price = base_prices.get(variety.crop_name.lower(), Decimal('5.00'))
        
        # Generate mock prices for different regions
        prices = []
        regions = request.regions or ['US', 'Midwest', 'Great Plains']
        
        for i, region in enumerate(regions[:3]):  # Limit to 3 regions
            # Add regional variation
            regional_adjustment = Decimal(str(i * 0.05))
            price = VarietyMarketPrice(
                variety_id=variety.id if hasattr(variety, 'id') else None,
                variety_name=variety.variety_name,
                crop_name=variety.crop_name,
                price_per_unit=base_price + regional_adjustment,
                unit="bushel",
                market_type=self.market_type,
                contract_type=ContractType.CASH_PRICE,
                region=region,
                price_date=date.today(),
                source="LOCAL_ELEVATOR_MOCK",
                confidence=0.8,
                last_updated=datetime.utcnow(),
                delivery_location=f"{region} Elevator"
            )
            prices.append(price)
        
        # Generate mock basis data
        basis_data = [
            {
                'location': 'Midwest',
                'current_basis': -0.15,
                'historical_avg': -0.20,
                'confidence': 0.8
            },
            {
                'location': 'Great Plains',
                'current_basis': -0.25,
                'historical_avg': -0.30,
                'confidence': 0.75
            }
        ]
        
        return {
            'prices': prices,
            'trends': [],
            'basis': basis_data,
            'demand': [],
            'premiums': []
        }


class ContractPricingProvider(BaseMarketProvider):
    """Provider for contract pricing data."""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.contract-pricing.com"  # Mock URL
        self.market_type = MarketType.CONTRACT_PRICING
        
    async def get_variety_market_data(
        self, 
        variety: EnhancedCropVariety, 
        request: MarketIntelligenceRequest
    ) -> Optional[Dict[str, Any]]:
        """Get contract pricing data for a variety."""
        try:
            # Mock implementation - would integrate with real contract pricing APIs
            mock_data = self._get_mock_contract_data(variety, request)
            
            return {
                'prices': mock_data.get('prices', []),
                'trends': mock_data.get('trends', []),
                'basis': mock_data.get('basis', []),
                'demand': mock_data.get('demand', []),
                'premiums': mock_data.get('premiums', [])
            }
            
        except Exception as e:
            logger.error(f"Error fetching contract data for {variety.variety_name}: {e}")
            return None
    
    def _get_mock_contract_data(
        self, 
        variety: EnhancedCropVariety, 
        request: MarketIntelligenceRequest
    ) -> Dict[str, Any]:
        """Generate mock contract data for development."""
        base_prices = {
            'corn': Decimal('4.30'),
            'soybean': Decimal('12.60'),
            'wheat': Decimal('6.85'),
            'oats': Decimal('3.25'),
            'barley': Decimal('4.55')
        }
        
        base_price = base_prices.get(variety.crop_name.lower(), Decimal('5.00'))
        
        # Generate mock contract prices
        prices = []
        contract_types = [
            ContractType.FORWARD_CONTRACT,
            ContractType.HEDGE_CONTRACT,
            ContractType.PREMIUM_CONTRACT
        ]
        
        for i, contract_type in enumerate(contract_types):
            # Add contract-specific pricing
            contract_adjustment = Decimal(str(i * 0.08))
            price = VarietyMarketPrice(
                variety_id=variety.id if hasattr(variety, 'id') else None,
                variety_name=variety.variety_name,
                crop_name=variety.crop_name,
                price_per_unit=base_price + contract_adjustment,
                unit="bushel",
                market_type=self.market_type,
                contract_type=contract_type,
                region="US",
                price_date=date.today(),
                delivery_date=date.today() + timedelta(days=90),
                source="CONTRACT_PRICING_MOCK",
                confidence=0.85,
                last_updated=datetime.utcnow(),
                payment_terms="Net 30",
                delivery_terms="FOB Farm"
            )
            prices.append(price)
        
        # Generate mock demand data
        demand_data = [
            {
                'demand_type': 'domestic',
                'demand_factor': 1.05,
                'confidence': 0.8
            },
            {
                'demand_type': 'export',
                'demand_factor': 1.15,
                'confidence': 0.75
            }
        ]
        
        return {
            'prices': prices,
            'trends': [],
            'basis': [],
            'demand': demand_data,
            'premiums': []
        }


class SpecialtyMarketProvider(BaseMarketProvider):
    """Provider for specialty market data (organic, non-GMO, etc.)."""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.specialty-markets.com"  # Mock URL
        self.market_type = MarketType.SPECIALTY_MARKET
        
    async def get_variety_market_data(
        self, 
        variety: EnhancedCropVariety, 
        request: MarketIntelligenceRequest
    ) -> Optional[Dict[str, Any]]:
        """Get specialty market data for a variety."""
        try:
            # Mock implementation - would integrate with real specialty market APIs
            mock_data = self._get_mock_specialty_data(variety, request)
            
            return {
                'prices': mock_data.get('prices', []),
                'trends': mock_data.get('trends', []),
                'basis': mock_data.get('basis', []),
                'demand': mock_data.get('demand', []),
                'premiums': mock_data.get('premiums', [])
            }
            
        except Exception as e:
            logger.error(f"Error fetching specialty data for {variety.variety_name}: {e}")
            return None
    
    def _get_mock_specialty_data(
        self, 
        variety: EnhancedCropVariety, 
        request: MarketIntelligenceRequest
    ) -> Dict[str, Any]:
        """Generate mock specialty market data for development."""
        base_prices = {
            'corn': Decimal('4.50'),
            'soybean': Decimal('13.00'),
            'wheat': Decimal('7.20'),
            'oats': Decimal('3.50'),
            'barley': Decimal('4.80')
        }
        
        base_price = base_prices.get(variety.crop_name.lower(), Decimal('5.50'))
        
        # Generate mock specialty market prices
        prices = []
        specialty_markets = [
            (MarketType.ORGANIC_MARKET, Decimal('0.50')),
            (MarketType.SPECIALTY_MARKET, Decimal('0.25')),
            (MarketType.DIRECT_MARKET, Decimal('0.15'))
        ]
        
        for market_type, premium in specialty_markets:
            price = VarietyMarketPrice(
                variety_id=variety.id if hasattr(variety, 'id') else None,
                variety_name=variety.variety_name,
                crop_name=variety.crop_name,
                price_per_unit=base_price + premium,
                unit="bushel",
                market_type=market_type,
                contract_type=ContractType.PREMIUM_CONTRACT,
                region="US",
                price_date=date.today(),
                source="SPECIALTY_MARKET_MOCK",
                confidence=0.7,
                last_updated=datetime.utcnow(),
                premium_discount_amount=premium,
                premium_discount_reason=f"{market_type.value} premium"
            )
            prices.append(price)
        
        # Generate mock premium/discount data
        premium_data = [
            {
                'premium_type': 'organic',
                'premium_amount': 0.50,
                'confidence': 0.8
            },
            {
                'premium_type': 'non_gmo',
                'premium_amount': 0.25,
                'confidence': 0.75
            },
            {
                'premium_type': 'quality',
                'premium_amount': 0.15,
                'confidence': 0.7
            }
        ]
        
        return {
            'prices': prices,
            'trends': [],
            'basis': [],
            'demand': [],
            'premiums': premium_data
        }


class MarketDataAggregator:
    """Aggregator for combining data from multiple market providers."""
    
    def __init__(self):
        self.providers = {
            MarketType.COMMODITY_EXCHANGE: CommodityExchangeProvider(),
            MarketType.LOCAL_ELEVATOR: LocalElevatorProvider(),
            MarketType.CONTRACT_PRICING: ContractPricingProvider(),
            MarketType.SPECIALTY_MARKET: SpecialtyMarketProvider()
        }
    
    async def aggregate_market_data(
        self, 
        variety: EnhancedCropVariety, 
        request: MarketIntelligenceRequest
    ) -> Dict[str, Any]:
        """Aggregate market data from all providers."""
        aggregated_data = {
            'prices': [],
            'trends': [],
            'basis': [],
            'demand': [],
            'premiums': []
        }
        
        # Collect data from all providers concurrently
        tasks = []
        for market_type, provider in self.providers.items():
            if request.market_types and market_type not in request.market_types:
                continue
            tasks.append(provider.get_variety_market_data(variety, request))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate results
        for result in results:
            if isinstance(result, dict):
                for key, values in result.items():
                    if key in aggregated_data and values:
                        aggregated_data[key].extend(values)
        
        return aggregated_data
    
    async def close_all_providers(self):
        """Close all provider sessions."""
        for provider in self.providers.values():
            await provider.close()
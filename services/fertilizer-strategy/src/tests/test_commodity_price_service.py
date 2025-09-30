"""
Comprehensive tests for commodity price service.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from datetime import date, timedelta

from ..services.commodity_price_service import CommodityPriceService
from ..models.commodity_price_models import (
    CommodityPriceData, CommodityTrendAnalysis, FertilizerCropPriceRatio,
    CommodityType, CommodityContract, CommoditySource
)


class TestCommodityPriceService:
    """Comprehensive test suite for commodity price service."""
    
    @pytest.fixture
    def service(self):
        return CommodityPriceService()
    
    @pytest.fixture
    def mock_corn_price(self):
        return CommodityPriceData(
            commodity_id="corn_001",
            commodity_name="Corn",
            commodity_type=CommodityType.CORN,
            contract_type=CommodityContract.CASH,
            price_per_unit=4.75,
            unit="bushel",
            region="US",
            source=CommoditySource.USDA_NASS,
            price_date=date.today(),
            is_spot_price=True,
            is_futures_price=False,
            confidence=0.90,
            volatility=0.15,
            market_conditions={"usda_data": True},
            seasonal_factors={"harvest_season": True}
        )
    
    @pytest.fixture
    def mock_soybean_price(self):
        return CommodityPriceData(
            commodity_id="soybean_001",
            commodity_name="Soybean",
            commodity_type=CommodityType.SOYBEAN,
            contract_type=CommodityContract.CASH,
            price_per_unit=12.30,
            unit="bushel",
            region="US",
            source=CommoditySource.USDA_NASS,
            price_date=date.today(),
            is_spot_price=True,
            is_futures_price=False,
            confidence=0.90,
            volatility=0.18,
            market_conditions={"usda_data": True},
            seasonal_factors={"harvest_season": True}
        )
    
    @pytest.mark.asyncio
    async def test_get_current_price_success(self, service, mock_corn_price):
        """Test successful commodity price retrieval."""
        with patch.object(service.provider_manager, 'fetch_price_from_all_sources', return_value=[mock_corn_price]):
            with patch.object(service.db, 'get_cached_price', return_value=None):
                with patch.object(service.db, 'cache_price', return_value=None):
                    result = await service.get_current_price(CommodityType.CORN, "US")
                    
                    assert result is not None
                    assert result.commodity_type == CommodityType.CORN
                    assert result.price_per_unit == 4.75
                    assert result.unit == "bushel"
                    assert result.confidence == 0.90
    
    @pytest.mark.asyncio
    async def test_get_current_price_cache_hit(self, service, mock_corn_price):
        """Test cache hit scenario."""
        with patch.object(service.db, 'get_cached_price', return_value=mock_corn_price):
            result = await service.get_current_price(CommodityType.CORN, "US")
            
            assert result is not None
            assert result.commodity_id == "corn_001"
            assert result.price_per_unit == 4.75
    
    @pytest.mark.asyncio
    async def test_get_current_price_no_data(self, service):
        """Test scenario when no price data is available."""
        with patch.object(service.provider_manager, 'fetch_price_from_all_sources', return_value=[]):
            with patch.object(service.db, 'get_cached_price', return_value=None):
                result = await service.get_current_price(CommodityType.CORN, "US")
                
                assert result is None
    
    @pytest.mark.asyncio
    async def test_get_current_prices_multiple(self, service, mock_corn_price, mock_soybean_price):
        """Test getting prices for multiple commodities."""
        with patch.object(service, 'get_current_price', side_effect=[mock_corn_price, mock_soybean_price]):
            commodities = [CommodityType.CORN, CommodityType.SOYBEAN]
            results = await service.get_current_prices(commodities, "US")
            
            assert len(results) == 2
            assert "corn" in results
            assert "soybean" in results
            assert results["corn"].price_per_unit == 4.75
            assert results["soybean"].price_per_unit == 12.30
    
    @pytest.mark.asyncio
    async def test_get_current_prices_limit_exceeded(self, service):
        """Test that maximum commodity limit is enforced."""
        commodities = [CommodityType.CORN] * 25  # Exceed limit of 20
        
        with pytest.raises(ValueError, match="Maximum 20 commodities per request"):
            await service.get_current_prices(commodities, "US")
    
    @pytest.mark.asyncio
    async def test_get_price_trend_success(self, service):
        """Test successful price trend analysis."""
        # Mock historical prices
        historical_prices = []
        base_date = date.today() - timedelta(days=30)
        base_price = 4.50
        
        for i in range(31):
            price_data = CommodityPriceData(
                commodity_id=f"corn_historical_{i}",
                commodity_name="Corn (Historical)",
                commodity_type=CommodityType.CORN,
                contract_type=CommodityContract.CASH,
                price_per_unit=base_price + (i * 0.01),  # Gradual price increase
                unit="bushel",
                region="US",
                source=CommoditySource.USDA_NASS,
                price_date=base_date + timedelta(days=i),
                is_spot_price=True,
                is_futures_price=False,
                confidence=0.90,
                volatility=0.15,
                market_conditions={"historical_data": True},
                seasonal_factors={"historical_analysis": True}
            )
            historical_prices.append(price_data)
        
        with patch.object(service.db, 'get_historical_prices', return_value=historical_prices):
            result = await service.get_price_trend(CommodityType.CORN, "US", 30)
            
            assert result is not None
            assert result.commodity_type == CommodityType.CORN
            assert result.current_price == 4.80  # Last price in series
            assert result.trend_direction == "up"  # Should be upward trend
            assert result.data_points_used == 31
    
    @pytest.mark.asyncio
    async def test_get_price_trend_insufficient_data(self, service):
        """Test trend analysis with insufficient data."""
        with patch.object(service.db, 'get_historical_prices', return_value=[]):
            result = await service.get_price_trend(CommodityType.CORN, "US", 30)
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_calculate_fertilizer_crop_price_ratios(self, service):
        """Test fertilizer-crop price ratio calculations."""
        fertilizer_prices = {
            "urea": 450.0,
            "dap": 580.0
        }
        
        crop_prices = {
            "corn": 4.75,
            "soybean": 12.30
        }
        
        result = await service.calculate_fertilizer_crop_price_ratios(
            fertilizer_prices, crop_prices, "US"
        )
        
        assert len(result) > 0
        
        # Check urea-corn ratio
        urea_corn_ratio = next((r for r in result if r.fertilizer_product == "urea" and r.commodity_type == CommodityType.CORN), None)
        assert urea_corn_ratio is not None
        assert urea_corn_ratio.price_ratio == 450.0 / 4.75
        assert urea_corn_ratio.inverse_ratio == 4.75 / 450.0
    
    @pytest.mark.asyncio
    async def test_calculate_basis_analysis_success(self, service, mock_corn_price):
        """Test successful basis analysis calculation."""
        # Create futures price data
        futures_price = CommodityPriceData(
            commodity_id="corn_futures_001",
            commodity_name="Corn Futures",
            commodity_type=CommodityType.CORN,
            contract_type=CommodityContract.FUTURES,
            price_per_unit=4.70,
            unit="bushel",
            region="US",
            source=CommoditySource.CBOT,
            price_date=date.today(),
            is_spot_price=False,
            is_futures_price=True,
            confidence=0.90,
            volatility=0.12,
            market_conditions={"futures_market": True},
            seasonal_factors={"contract_month": "March"}
        )
        
        with patch.object(service, 'get_current_price', side_effect=[mock_corn_price, futures_price]):
            result = await service.calculate_basis_analysis(CommodityType.CORN, "US")
            
            assert result is not None
            assert result.commodity_type == CommodityType.CORN
            assert result.cash_price == 4.75
            assert result.futures_price == 4.70
            assert result.basis_value == 0.05  # 4.75 - 4.70
    
    @pytest.mark.asyncio
    async def test_calculate_basis_analysis_insufficient_data(self, service):
        """Test basis analysis with insufficient data."""
        with patch.object(service, 'get_current_price', return_value=None):
            result = await service.calculate_basis_analysis(CommodityType.CORN, "US")
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_query_prices_success(self, service, mock_corn_price):
        """Test successful price query execution."""
        request_data = {
            "commodity_types": [CommodityType.CORN],
            "include_trend_analysis": True,
            "include_volatility": True,
            "include_price_ratios": False
        }
        
        with patch.object(service, 'get_current_price', return_value=mock_corn_price):
            with patch.object(service, 'get_price_trend', return_value=None):
                result = await service.query_prices(request_data)
                
                assert result is not None
                assert result.query_id is not None
                assert len(result.prices) == 1
                assert result.total_results == 1
                assert result.processing_time_ms > 0
    
    def test_calculate_trend_percent(self, service):
        """Test trend percentage calculation."""
        # Test normal case
        result = service._calculate_trend_percent(5.0, 4.0)
        assert result == 25.0  # (5-4)/4 * 100
        
        # Test negative trend
        result = service._calculate_trend_percent(3.0, 4.0)
        assert result == -25.0  # (3-4)/4 * 100
        
        # Test with None
        result = service._calculate_trend_percent(5.0, None)
        assert result is None
    
    def test_calculate_volatility(self, service):
        """Test volatility calculation."""
        prices = [4.0, 4.5, 4.2, 4.8, 4.1]
        volatility = service._calculate_volatility(prices)
        
        assert volatility > 0
        assert isinstance(volatility, float)
    
    def test_analyze_trend_strength(self, service):
        """Test trend strength analysis."""
        # Test weak trend
        direction, strength = service._analyze_trend_strength(1.5)
        assert direction == "up"
        assert strength == "weak"
        
        # Test moderate trend
        direction, strength = service._analyze_trend_strength(3.0)
        assert direction == "up"
        assert strength == "moderate"
        
        # Test strong trend
        direction, strength = service._analyze_trend_strength(7.0)
        assert direction == "up"
        assert strength == "strong"
        
        # Test stable trend
        direction, strength = service._analyze_trend_strength(0.5)
        assert direction == "stable"
        assert strength == "weak"
    
    def test_assess_profitability(self, service):
        """Test profitability assessment."""
        # Test favorable ratio
        result = service._assess_profitability(0.08, "urea", CommodityType.CORN)
        assert result == "favorable"
        
        # Test unfavorable ratio
        result = service._assess_profitability(0.15, "urea", CommodityType.CORN)
        assert result == "unfavorable"
    
    def test_analyze_basis_strength(self, service):
        """Test basis strength analysis."""
        # Test weak basis
        trend, strength = service._analyze_basis_strength(0.05)
        assert trend == "stable"
        assert strength == "weak"
        
        # Test moderate basis
        trend, strength = service._analyze_basis_strength(0.20)
        assert trend == "strong"
        assert strength == "moderate"
        
        # Test strong basis
        trend, strength = service._analyze_basis_strength(0.30)
        assert trend == "strong"
        assert strength == "strong"


# Agricultural validation tests
class TestAgriculturalValidation:
    """Tests for agricultural accuracy and domain validation."""
    
    @pytest.mark.asyncio
    async def test_corn_belt_price_accuracy(self):
        """Test accuracy for major corn belt commodity prices."""
        service = CommodityPriceService()
        
        # Test corn price in Iowa (major corn belt state)
        with patch.object(service.provider_manager, 'fetch_price_from_all_sources') as mock_fetch:
            mock_price = CommodityPriceData(
                commodity_id="corn_iowa",
                commodity_name="Corn",
                commodity_type=CommodityType.CORN,
                contract_type=CommodityContract.CASH,
                price_per_unit=4.75,
                unit="bushel",
                region="Iowa",
                source=CommoditySource.LOCAL_ELEVATOR,
                price_date=date.today(),
                is_spot_price=True,
                is_futures_price=False,
                confidence=0.90,
                volatility=0.15,
                market_conditions={"local_cash": True},
                seasonal_factors={"harvest_season": True}
            )
            mock_fetch.return_value = [mock_price]
            
            result = await service.get_current_price(CommodityType.CORN, "Iowa")
            
            # Validate price is within reasonable agricultural range
            assert 3.0 <= result.price_per_unit <= 8.0  # Reasonable corn price range
            assert result.unit == "bushel"
            assert result.confidence >= 0.8
    
    @pytest.mark.asyncio
    async def test_soybean_price_validation(self):
        """Test soybean price validation."""
        service = CommodityPriceService()
        
        with patch.object(service.provider_manager, 'fetch_price_from_all_sources') as mock_fetch:
            mock_price = CommodityPriceData(
                commodity_id="soybean_us",
                commodity_name="Soybean",
                commodity_type=CommodityType.SOYBEAN,
                contract_type=CommodityContract.CASH,
                price_per_unit=12.30,
                unit="bushel",
                region="US",
                source=CommoditySource.USDA_NASS,
                price_date=date.today(),
                is_spot_price=True,
                is_futures_price=False,
                confidence=0.92,
                volatility=0.18,
                market_conditions={"usda_data": True},
                seasonal_factors={"harvest_season": True}
            )
            mock_fetch.return_value = [mock_price]
            
            result = await service.get_current_price(CommodityType.SOYBEAN, "US")
            
            # Validate soybean price is within reasonable range
            assert 8.0 <= result.price_per_unit <= 18.0  # Reasonable soybean price range
            assert result.unit == "bushel"
            assert result.confidence >= 0.9
    
    def test_fertilizer_crop_ratio_validation(self):
        """Test fertilizer-crop price ratio validation."""
        service = CommodityPriceService()
        
        # Test urea-corn ratio
        ratio = service._assess_profitability(0.1, "urea", CommodityType.CORN)
        assert ratio in ["favorable", "unfavorable", "neutral"]
        
        # Test DAP-soybean ratio
        ratio = service._assess_profitability(0.08, "dap", CommodityType.SOYBEAN)
        assert ratio in ["favorable", "unfavorable", "neutral"]
    
    @pytest.mark.asyncio
    async def test_price_volatility_agricultural_validation(self):
        """Test that price volatility is agriculturally reasonable."""
        service = CommodityPriceService()
        
        # Mock historical prices with realistic agricultural volatility
        historical_prices = []
        base_date = date.today() - timedelta(days=30)
        base_price = 4.75
        
        for i in range(31):
            # Simulate realistic agricultural price movement (±5% daily max)
            daily_change = (hash(str(base_date + timedelta(days=i))) % 100 - 50) / 1000
            price = base_price * (1 + daily_change)
            
            price_data = CommodityPriceData(
                commodity_id=f"corn_vol_{i}",
                commodity_name="Corn",
                commodity_type=CommodityType.CORN,
                contract_type=CommodityContract.CASH,
                price_per_unit=price,
                unit="bushel",
                region="US",
                source=CommoditySource.USDA_NASS,
                price_date=base_date + timedelta(days=i),
                is_spot_price=True,
                is_futures_price=False,
                confidence=0.90,
                volatility=0.15,
                market_conditions={"historical_data": True},
                seasonal_factors={"historical_analysis": True}
            )
            historical_prices.append(price_data)
        
        with patch.object(service.db, 'get_historical_prices', return_value=historical_prices):
            result = await service.get_price_trend(CommodityType.CORN, "US", 30)
            
            # Validate volatility is within agricultural norms
            assert result.volatility_30d is not None
            assert 0.05 <= result.volatility_30d <= 0.50  # Reasonable agricultural volatility range
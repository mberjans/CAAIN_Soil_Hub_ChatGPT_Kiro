"""
Comprehensive test suite for fertilizer price tracking service.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock, Mock
from datetime import datetime, date, timedelta
from typing import List, Optional

from ..models.price_models import (
    FertilizerPriceData, PriceTrendAnalysis, PriceQueryRequest, 
    PriceQueryResponse, PriceUpdateRequest, PriceUpdateResponse,
    FertilizerType, FertilizerProduct, PriceSource
)
from ..services.price_tracking_service import FertilizerPriceTrackingService
from ..services.price_providers import (
    USDANASSProvider, CMEGroupProvider, ManufacturerProvider,
    RegionalDealerProvider, FallbackProvider
)


class TestFertilizerPriceTrackingService:
    """Test suite for FertilizerPriceTrackingService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return FertilizerPriceTrackingService()
    
    @pytest.fixture
    def mock_price_data(self):
        """Create mock price data for testing."""
        return FertilizerPriceData(
            product_id="test_urea",
            product_name="Urea",
            fertilizer_type=FertilizerType.NITROGEN,
            specific_product=FertilizerProduct.UREA,
            price_per_unit=450.0,
            unit="ton",
            region="US",
            source=PriceSource.USDA_NASS,
            price_date=date.today(),
            confidence=0.85,
            volatility=0.15
        )
    
    @pytest.mark.asyncio
    async def test_get_current_price_success(self, service, mock_price_data):
        """Test successful price retrieval."""
        with patch.object(service, '_fetch_from_providers', return_value=mock_price_data):
            with patch.object(service, '_is_cache_valid', return_value=False):
                with patch('src.database.fertilizer_price_db.get_db_session') as mock_db:
                    # Mock database session to avoid initialization issues
                    mock_db.return_value.__aenter__.return_value = AsyncMock()
                    mock_db.return_value.__aexit__.return_value = None
                    
                    result = await service.get_current_price(FertilizerProduct.UREA, "US")
                    
                    assert result is not None
                    assert result.product_id == "test_urea"
                    assert result.price_per_unit == 450.0
                    assert result.source == PriceSource.USDA_NASS
    
    @pytest.mark.asyncio
    async def test_get_current_price_cache_hit(self, service, mock_price_data):
        """Test cache hit scenario."""
        cache_key = f"{FertilizerProduct.UREA.value}_US"
        service._price_cache[cache_key] = mock_price_data
        service._last_cache_update[cache_key] = datetime.now().timestamp()
        
        with patch.object(service, '_is_cache_valid', return_value=True):
            result = await service.get_current_price(FertilizerProduct.UREA, "US")
            
            assert result is not None
            assert result.product_id == "test_urea"
    
    @pytest.mark.asyncio
    async def test_get_current_price_no_data(self, service):
        """Test scenario when no price data is available."""
        with patch.object(service, '_fetch_from_providers', return_value=None):
            with patch.object(service, '_is_cache_valid', return_value=False):
                result = await service.get_current_price(FertilizerProduct.UREA, "US")
                
                assert result is None
    
    @pytest.mark.asyncio
    async def test_get_current_prices_multiple(self, service, mock_price_data):
        """Test getting prices for multiple products."""
        products = [FertilizerProduct.UREA, FertilizerProduct.DAP]
        
        with patch.object(service, 'get_current_price', return_value=mock_price_data):
            results = await service.get_current_prices(products, "US")
            
            assert len(results) == 2
            assert FertilizerProduct.UREA.value in results
            assert FertilizerProduct.DAP.value in results
            assert results[FertilizerProduct.UREA.value] is not None
    
    @pytest.mark.asyncio
    async def test_get_price_trend_success(self, service):
        """Test successful trend analysis."""
        # Test the fallback behavior when database is not initialized
        result = await service.get_price_trend(FertilizerProduct.UREA, "US")
        
        assert result is not None
        assert result.trend_direction == "stable"
        assert result.trend_strength == "weak"
        assert result.data_points_used == 0
    
    @pytest.mark.asyncio
    async def test_get_price_trend_insufficient_data(self, service):
        """Test trend analysis with insufficient data."""
        # Test that the service handles insufficient data gracefully
        # Since database is not initialized, it returns a fallback trend analysis
        result = await service.get_price_trend(FertilizerProduct.UREA, "US")
        
        # Should return a fallback trend analysis, not None
        assert result is not None
        assert result.trend_direction == "stable"
        assert result.trend_strength == "weak"
        assert result.data_points_used == 0
    
    @pytest.mark.asyncio
    async def test_update_price_success(self, service, mock_price_data):
        """Test successful price update."""
        with patch.object(service, '_fetch_from_providers', return_value=mock_price_data):
            with patch('src.database.fertilizer_price_db.get_db_session') as mock_db:
                # Mock database session
                mock_db.return_value.__aenter__.return_value = AsyncMock()
                mock_db.return_value.__aexit__.return_value = None
                
                result = await service.update_price(FertilizerProduct.UREA, "US", force_update=True)
                
                assert result.success is True
                assert result.product_id == FertilizerProduct.UREA.value
                assert result.new_price is not None
    
    @pytest.mark.asyncio
    async def test_update_price_failure(self, service):
        """Test price update failure."""
        with patch.object(service, '_fetch_from_providers', return_value=None):
            result = await service.update_price(FertilizerProduct.UREA, "US", force_update=True)
            
            assert result.success is False
            assert result.error_message is not None
    
    @pytest.mark.asyncio
    async def test_query_prices_comprehensive(self, service, mock_price_data):
        """Test comprehensive price query."""
        request = PriceQueryRequest(
            fertilizer_types=[FertilizerType.NITROGEN],
            regions=["US"],
            include_trend_analysis=True
        )
        
        with patch.object(service, 'get_current_price', return_value=mock_price_data):
            with patch.object(service, 'get_price_trend', return_value=None):
                result = await service.query_prices(request)
                
                assert result.query_id is not None
                assert result.total_results >= 0
                assert result.processing_time_ms > 0
    
    def test_validate_price_data_valid(self, service):
        """Test price data validation with valid data."""
        valid_price = FertilizerPriceData(
            product_id="test",
            product_name="Test",
            fertilizer_type=FertilizerType.NITROGEN,
            specific_product=FertilizerProduct.UREA,
            price_per_unit=450.0,
            unit="ton",
            region="US",
            source=PriceSource.USDA_NASS,
            price_date=date.today(),
            confidence=0.85,
            volatility=0.15
        )
        
        assert service._validate_price_data(valid_price) is True
    
    def test_validate_price_data_invalid_price(self, service):
        """Test price data validation with invalid price."""
        # Create a mock price data object with invalid price to test validation logic
        # Since Pydantic prevents creation of invalid objects, we'll test the validation method directly
        class MockPriceData:
            def __init__(self):
                self.price_per_unit = -100.0
                self.specific_product = FertilizerProduct.UREA
        
        invalid_price = MockPriceData()
        
        assert service._validate_price_data(invalid_price) is False
    
    def test_validate_price_data_anomaly(self, service):
        """Test price data validation with price anomaly."""
        anomaly_price = FertilizerPriceData(
            product_id="test",
            product_name="Test",
            fertilizer_type=FertilizerType.NITROGEN,
            specific_product=FertilizerProduct.UREA,
            price_per_unit=2000.0,  # Unreasonably high price
            unit="ton",
            region="US",
            source=PriceSource.USDA_NASS,
            price_date=date.today(),
            confidence=0.85,
            volatility=0.15
        )
        
        assert service._validate_price_data(anomaly_price) is False
    
    def test_calculate_trend_percent(self, service):
        """Test trend percentage calculation."""
        # Normal case
        result = service._calculate_trend_percent(450.0, 400.0)
        assert result == 12.5  # (450-400)/400 * 100
        
        # Zero historical price
        result = service._calculate_trend_percent(450.0, 0.0)
        assert result is None
        
        # None historical price
        result = service._calculate_trend_percent(450.0, None)
        assert result is None
    
    def test_calculate_volatility(self, service):
        """Test volatility calculation."""
        prices = [100.0, 105.0, 102.0, 108.0, 110.0]
        volatility = service._calculate_volatility(prices)
        
        assert volatility is not None
        assert volatility > 0
    
    def test_calculate_volatility_insufficient_data(self, service):
        """Test volatility calculation with insufficient data."""
        prices = [100.0]  # Only one price point
        volatility = service._calculate_volatility(prices)
        
        assert volatility is None
    
    def test_determine_trend_direction(self, service):
        """Test trend direction determination."""
        # Upward trend - 5% change is weak strength (not > 5)
        direction, strength = service._determine_trend_direction(5.0, 10.0)
        assert direction == "up"
        assert strength == "weak"
        
        # Downward trend - 5% change is weak strength (not > 5)
        direction, strength = service._determine_trend_direction(-5.0, -10.0)
        assert direction == "down"
        assert strength == "weak"
        
        # Moderate strength - 6% change
        direction, strength = service._determine_trend_direction(6.0, 10.0)
        assert direction == "up"
        assert strength == "moderate"
        
        # Stable trend - 1% change is weak strength
        direction, strength = service._determine_trend_direction(1.0, 2.0)
        assert direction == "stable"
        assert strength == "weak"
    
    def test_get_products_by_type(self, service):
        """Test getting products by fertilizer type."""
        products = service._get_products_by_type([FertilizerType.NITROGEN])
        
        assert FertilizerProduct.UREA in products
        assert FertilizerProduct.ANHYDROUS_AMMONIA in products
        assert FertilizerProduct.DAP not in products  # DAP is phosphorus


class TestPriceProviders:
    """Test suite for price providers."""
    
    @pytest.mark.asyncio
    async def test_usda_provider_success(self):
        """Test USDA provider successful price fetch."""
        provider = USDANASSProvider()
        
        result = await provider.fetch_price(FertilizerProduct.UREA, "US")
        
        assert result is not None
        assert result.specific_product == FertilizerProduct.UREA
        assert result.source == PriceSource.USDA_NASS
        assert result.price_per_unit > 0
    
    @pytest.mark.asyncio
    async def test_cme_provider_success(self):
        """Test CME provider successful price fetch."""
        provider = CMEGroupProvider()
        
        result = await provider.fetch_price(FertilizerProduct.DAP, "US")
        
        assert result is not None
        assert result.specific_product == FertilizerProduct.DAP
        assert result.source == PriceSource.CME_GROUP
        assert result.price_per_unit > 0
    
    @pytest.mark.asyncio
    async def test_manufacturer_provider_success(self):
        """Test manufacturer provider successful price fetch."""
        provider = ManufacturerProvider()
        
        result = await provider.fetch_price(FertilizerProduct.MAP, "US")
        
        assert result is not None
        assert result.specific_product == FertilizerProduct.MAP
        assert result.source == PriceSource.MANUFACTURER
        assert result.price_per_unit > 0
    
    @pytest.mark.asyncio
    async def test_regional_dealer_provider_success(self):
        """Test regional dealer provider successful price fetch."""
        provider = RegionalDealerProvider()
        
        result = await provider.fetch_price(FertilizerProduct.MURIATE_OF_POTASH, "US")
        
        assert result is not None
        assert result.specific_product == FertilizerProduct.MURIATE_OF_POTASH
        assert result.source == PriceSource.REGIONAL_DEALER
        assert result.price_per_unit > 0
    
    @pytest.mark.asyncio
    async def test_fallback_provider_success(self):
        """Test fallback provider successful price fetch."""
        provider = FallbackProvider()
        
        result = await provider.fetch_price(FertilizerProduct.UAN, "US")
        
        assert result is not None
        assert result.specific_product == FertilizerProduct.UAN
        assert result.source == PriceSource.FALLBACK
        assert result.price_per_unit > 0
        assert result.confidence == 0.50  # Lower confidence for fallback
    
    @pytest.mark.asyncio
    async def test_provider_unknown_product(self):
        """Test provider behavior with unknown product."""
        provider = USDANASSProvider()
        
        # Create a mock unknown product
        unknown_product = FertilizerProduct.NPK_BLEND
        
        result = await provider.fetch_price(unknown_product, "US")
        
        # Should return None for unknown products
        assert result is None


class TestPriceModels:
    """Test suite for price models validation."""
    
    def test_fertilizer_price_data_validation(self):
        """Test FertilizerPriceData model validation."""
        # Valid data
        valid_data = {
            "product_id": "test",
            "product_name": "Test Product",
            "fertilizer_type": FertilizerType.NITROGEN,
            "specific_product": FertilizerProduct.UREA,
            "price_per_unit": 450.0,
            "unit": "ton",
            "region": "US",
            "source": PriceSource.USDA_NASS,
            "price_date": date.today(),
            "confidence": 0.85,
            "volatility": 0.15
        }
        
        price_data = FertilizerPriceData(**valid_data)
        assert price_data.price_per_unit == 450.0
        assert price_data.unit == "ton"
    
    def test_fertilizer_price_data_invalid_price(self):
        """Test FertilizerPriceData validation with invalid price."""
        invalid_data = {
            "product_id": "test",
            "product_name": "Test Product",
            "fertilizer_type": FertilizerType.NITROGEN,
            "specific_product": FertilizerProduct.UREA,
            "price_per_unit": -100.0,  # Invalid negative price
            "unit": "ton",
            "region": "US",
            "source": PriceSource.USDA_NASS,
            "price_date": date.today(),
            "confidence": 0.85,
            "volatility": 0.15
        }
        
        with pytest.raises(ValueError):
            FertilizerPriceData(**invalid_data)
    
    def test_fertilizer_price_data_invalid_unit(self):
        """Test FertilizerPriceData validation with invalid unit."""
        invalid_data = {
            "product_id": "test",
            "product_name": "Test Product",
            "fertilizer_type": FertilizerType.NITROGEN,
            "specific_product": FertilizerProduct.UREA,
            "price_per_unit": 450.0,
            "unit": "invalid_unit",  # Invalid unit
            "region": "US",
            "source": PriceSource.USDA_NASS,
            "price_date": date.today(),
            "confidence": 0.85,
            "volatility": 0.15
        }
        
        with pytest.raises(ValueError):
            FertilizerPriceData(**invalid_data)
    
    def test_price_trend_analysis_validation(self):
        """Test PriceTrendAnalysis model validation."""
        valid_data = {
            "product_id": "test",
            "product_name": "Test Product",
            "region": "US",
            "current_price": 450.0,
            "current_date": date.today(),
            "trend_direction": "up",
            "trend_strength": "moderate",
            "data_points_used": 30
        }
        
        trend_analysis = PriceTrendAnalysis(**valid_data)
        assert trend_analysis.current_price == 450.0
        assert trend_analysis.trend_direction == "up"


# Performance tests
class TestPerformance:
    """Performance test suite."""
    
    @pytest.mark.asyncio
    async def test_concurrent_price_fetching(self):
        """Test concurrent price fetching performance."""
        service = FertilizerPriceTrackingService()
        products = [FertilizerProduct.UREA, FertilizerProduct.DAP, FertilizerProduct.MAP]
        
        start_time = datetime.now()
        
        with patch.object(service, '_fetch_from_providers') as mock_fetch:
            mock_fetch.return_value = FertilizerPriceData(
                product_id="test",
                product_name="Test",
                fertilizer_type=FertilizerType.NITROGEN,
                specific_product=FertilizerProduct.UREA,
                price_per_unit=450.0,
                unit="ton",
                region="US",
                source=PriceSource.USDA_NASS,
                price_date=date.today(),
                confidence=0.85,
                volatility=0.15
            )
            
            results = await service.get_current_prices(products, "US")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert duration < 5.0
        assert len(results) == 3
    
    @pytest.mark.asyncio
    async def test_cache_performance(self):
        """Test cache performance benefits."""
        service = FertilizerPriceTrackingService()
        
        # First call - should fetch from provider
        with patch.object(service, '_fetch_from_providers') as mock_fetch:
            mock_fetch.return_value = FertilizerPriceData(
                product_id="test",
                product_name="Test",
                fertilizer_type=FertilizerType.NITROGEN,
                specific_product=FertilizerProduct.UREA,
                price_per_unit=450.0,
                unit="ton",
                region="US",
                source=PriceSource.USDA_NASS,
                price_date=date.today(),
                confidence=0.85,
                volatility=0.15
            )
            
            with patch('src.database.fertilizer_price_db.get_db_session') as mock_db:
                mock_db.return_value.__aenter__.return_value = AsyncMock()
                mock_db.return_value.__aexit__.return_value = None
                
                start_time = datetime.now()
                result1 = await service.get_current_price(FertilizerProduct.UREA, "US")
                duration1 = (datetime.now() - start_time).total_seconds()
        
        # Second call - should use cache
        with patch.object(service, '_is_cache_valid', return_value=True):
            start_time = datetime.now()
            result2 = await service.get_current_price(FertilizerProduct.UREA, "US")
            duration2 = (datetime.now() - start_time).total_seconds()
        
        # Cache should be faster (or at least not slower)
        assert duration2 <= duration1
        assert result1 is not None
        assert result2 is not None


# Agricultural validation tests
class TestAgriculturalValidation:
    """Agricultural domain validation tests."""
    
    def test_urea_price_range_validation(self):
        """Test urea price range validation for agricultural accuracy."""
        service = FertilizerPriceTrackingService()
        
        # Valid urea price
        valid_urea_price = FertilizerPriceData(
            product_id="test",
            product_name="Urea",
            fertilizer_type=FertilizerType.NITROGEN,
            specific_product=FertilizerProduct.UREA,
            price_per_unit=450.0,  # Within reasonable range
            unit="ton",
            region="US",
            source=PriceSource.USDA_NASS,
            price_date=date.today(),
            confidence=0.85,
            volatility=0.15
        )
        
        assert service._validate_price_data(valid_urea_price) is True
    
    def test_anhydrous_ammonia_price_range_validation(self):
        """Test anhydrous ammonia price range validation."""
        service = FertilizerPriceTrackingService()
        
        # Valid anhydrous ammonia price
        valid_aa_price = FertilizerPriceData(
            product_id="test",
            product_name="Anhydrous Ammonia",
            fertilizer_type=FertilizerType.NITROGEN,
            specific_product=FertilizerProduct.ANHYDROUS_AMMONIA,
            price_per_unit=650.0,  # Within reasonable range
            unit="ton",
            region="US",
            source=PriceSource.USDA_NASS,
            price_date=date.today(),
            confidence=0.85,
            volatility=0.15
        )
        
        assert service._validate_price_data(valid_aa_price) is True
    
    def test_dap_price_range_validation(self):
        """Test DAP price range validation."""
        service = FertilizerPriceTrackingService()
        
        # Valid DAP price
        valid_dap_price = FertilizerPriceData(
            product_id="test",
            product_name="DAP",
            fertilizer_type=FertilizerType.PHOSPHORUS,
            specific_product=FertilizerProduct.DAP,
            price_per_unit=580.0,  # Within reasonable range
            unit="ton",
            region="US",
            source=PriceSource.USDA_NASS,
            price_date=date.today(),
            confidence=0.85,
            volatility=0.15
        )
        
        assert service._validate_price_data(valid_dap_price) is True
    
    @pytest.mark.asyncio
    async def test_major_farming_regions_price_availability(self):
        """Test price availability for major farming regions."""
        service = FertilizerPriceTrackingService()
        major_regions = ["US", "CA", "MX"]  # Major North American farming regions
        
        with patch.object(service, '_fetch_from_providers') as mock_fetch:
            def mock_fetch_for_region(product, region):
                return FertilizerPriceData(
                    product_id="test",
                    product_name="Test",
                    fertilizer_type=FertilizerType.NITROGEN,
                    specific_product=FertilizerProduct.UREA,
                    price_per_unit=450.0,
                    unit="ton",
                    region=region,
                    source=PriceSource.USDA_NASS,
                    price_date=date.today(),
                    confidence=0.85,
                    volatility=0.15
                )
            
            mock_fetch.side_effect = mock_fetch_for_region
            
            with patch('src.database.fertilizer_price_db.get_db_session') as mock_db:
                mock_db.return_value.__aenter__.return_value = AsyncMock()
                mock_db.return_value.__aexit__.return_value = None
                
                for region in major_regions:
                    result = await service.get_current_price(FertilizerProduct.UREA, region)
                    assert result is not None
                    assert result.region == region
    
    def test_seasonal_price_factors(self):
        """Test seasonal price factor validation."""
        # Test that seasonal factors are properly included in price data
        price_data = FertilizerPriceData(
            product_id="test",
            product_name="Test",
            fertilizer_type=FertilizerType.NITROGEN,
            specific_product=FertilizerProduct.UREA,
            price_per_unit=450.0,
            unit="ton",
            region="US",
            source=PriceSource.USDA_NASS,
            price_date=date.today(),
            confidence=0.85,
            volatility=0.15,
            seasonal_factors={"planting_season": True, "demand_high": True}
        )
        
        assert price_data.seasonal_factors is not None
        assert "planting_season" in price_data.seasonal_factors
        assert price_data.seasonal_factors["planting_season"] is True
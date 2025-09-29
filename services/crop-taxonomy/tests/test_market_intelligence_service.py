"""
Tests for Market Intelligence Service
Comprehensive test suite for market intelligence and pricing analysis.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, date, timedelta
from decimal import Decimal
from uuid import uuid4

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.market_intelligence_models import (
    MarketIntelligenceRequest, MarketIntelligenceResponse,
    VarietyMarketPrice, MarketTrend, BasisAnalysis, DemandForecast,
    PremiumDiscountAnalysis, MarketType, QualityGrade, ContractType
)
from models.crop_variety_models import EnhancedCropVariety
from services.market_intelligence_service import MarketIntelligenceService, MarketIntelligenceError


class TestMarketIntelligenceService:
    """Test suite for MarketIntelligenceService."""
    
    @pytest.fixture
    def service(self):
        return MarketIntelligenceService()
    
    @pytest.fixture
    def mock_variety(self):
        """Create a mock variety for testing."""
        variety = MagicMock(spec=EnhancedCropVariety)
        variety.id = uuid4()
        variety.variety_name = "Test Variety"
        variety.crop_name = "corn"
        return variety
    
    @pytest.fixture
    def mock_request(self):
        """Create a mock market intelligence request."""
        return MarketIntelligenceRequest(
            variety_names=["Test Variety"],
            regions=["US", "Midwest"],
            market_types=[MarketType.COMMODITY_EXCHANGE, MarketType.LOCAL_ELEVATOR],
            include_trends=True,
            include_basis=True,
            include_demand_forecast=True,
            include_premium_discount=True,
            include_recommendations=True,
            include_executive_summary=True,
            detail_level="standard"
        )
    
    @pytest.fixture
    def mock_market_price(self):
        """Create a mock market price."""
        return VarietyMarketPrice(
            variety_id=uuid4(),
            variety_name="Test Variety",
            crop_name="corn",
            price_per_unit=Decimal('4.25'),
            unit="bushel",
            market_type=MarketType.COMMODITY_EXCHANGE,
            contract_type=ContractType.CASH_PRICE,
            region="US",
            price_date=date.today(),
            source="TEST_SOURCE",
            confidence=0.9,
            last_updated=datetime.utcnow()
        )
    
    @pytest.mark.asyncio
    async def test_get_market_intelligence_success(self, service, mock_request):
        """Test successful market intelligence analysis."""
        with patch.object(service, '_collect_market_data') as mock_collect:
            with patch.object(service, '_generate_market_report') as mock_generate:
                # Mock market data collection
                mock_collect.return_value = [{
                    'variety': MagicMock(),
                    'market_prices': [],
                    'trend_data': [],
                    'basis_data': [],
                    'demand_data': [],
                    'premium_discount_data': []
                }]
                
                # Mock report generation
                from models.market_intelligence_models import MarketIntelligenceReport
                mock_report = MarketIntelligenceReport(
                    variety_name="Test Variety",
                    crop_name="corn",
                    confidence=0.8,
                    data_quality_score=0.8,
                    current_prices=[]
                )
                mock_generate.return_value = mock_report
                
                result = await service.get_market_intelligence(mock_request)
                
                assert isinstance(result, MarketIntelligenceResponse)
                assert result.request_id is not None
                assert len(result.reports) == 1
                assert result.overall_confidence == 0.8
                assert result.data_coverage_score == 0.8
    
    @pytest.mark.asyncio
    async def test_get_market_intelligence_error_handling(self, service, mock_request):
        """Test error handling in market intelligence analysis."""
        with patch.object(service, '_collect_market_data', side_effect=Exception("Test error")):
            with pytest.raises(MarketIntelligenceError):
                await service.get_market_intelligence(mock_request)
    
    @pytest.mark.asyncio
    async def test_collect_market_data(self, service, mock_request, mock_variety, mock_market_price):
        """Test market data collection from providers."""
        with patch.object(service, '_get_varieties_to_analyze', return_value=[mock_variety]):
            with patch.object(service.providers[MarketType.COMMODITY_EXCHANGE], 'get_variety_market_data') as mock_provider:
                mock_provider.return_value = {
                    'prices': [mock_market_price],
                    'trends': [],
                    'basis': [],
                    'demand': [],
                    'premiums': []
                }
                
                result = await service._collect_market_data(mock_request)
                
                assert len(result) == 1
                assert result[0]['variety'] == mock_variety
                assert len(result[0]['market_prices']) >= 1  # Multiple providers may generate multiple prices
    
    @pytest.mark.asyncio
    async def test_generate_market_report(self, service, mock_request, mock_variety, mock_market_price):
        """Test market report generation."""
        variety_data = {
            'variety': mock_variety,
            'market_prices': [mock_market_price],
            'trend_data': [],
            'basis_data': [],
            'demand_data': [],
            'premium_discount_data': []
        }
        
        with patch.object(service.analysis_engine, 'analyze_market_trends', return_value=None):
            with patch.object(service.analysis_engine, 'analyze_basis', return_value=None):
                with patch.object(service.analysis_engine, 'forecast_demand', return_value=None):
                    with patch.object(service.analysis_engine, 'analyze_premiums_discounts', return_value=None):
                        with patch.object(service, '_identify_market_opportunities', return_value=[]):
                            with patch.object(service, '_identify_risk_factors', return_value=[]):
                                with patch.object(service, '_identify_competitive_advantages', return_value=[]):
                                    with patch.object(service, '_generate_recommendations', return_value={'pricing': [], 'timing': [], 'contracts': []}):
                                        with patch.object(service, '_generate_executive_summary', return_value="Test summary"):
                                            with patch.object(service, '_extract_key_insights', return_value=[]):
                                                result = await service._generate_market_report(variety_data, mock_request)
                                                
                                                assert result is not None
                                                assert result.variety_name == "Test Variety"
                                                assert result.crop_name == "corn"
                                                assert result.current_prices == [mock_market_price]
    
    @pytest.mark.asyncio
    async def test_identify_market_opportunities(self, service):
        """Test market opportunity identification."""
        variety_data = {
            'premium_discount_data': [
                {'premium_amount': 0.25},
                {'premium_amount': 0.15}
            ],
            'trend_data': [
                {'days_ago': 15, 'trend_percent': 7.5},
                {'days_ago': 25, 'trend_percent': 5.2}
            ],
            'market_prices': [
                MagicMock(price_per_unit=Decimal('4.00')),
                MagicMock(price_per_unit=Decimal('4.50'))
            ]
        }
        
        opportunities = await service._identify_market_opportunities(variety_data)
        
        assert len(opportunities) > 0
        assert any("Premium pricing opportunity" in opp for opp in opportunities)
        assert any("Strong upward price trend" in opp for opp in opportunities)
        assert any("Significant price variation" in opp for opp in opportunities)
    
    @pytest.mark.asyncio
    async def test_identify_risk_factors(self, service):
        """Test risk factor identification."""
        variety_data = {
            'trend_data': [
                {'volatility': 0.35},
                {'volatility': 0.40}
            ],
            'demand_data': [
                {'confidence': 0.5},
                {'confidence': 0.4}
            ],
            'market_prices': [
                MagicMock(market_type=MarketType.COMMODITY_EXCHANGE),
                MagicMock(market_type=MarketType.LOCAL_ELEVATOR)
            ]
        }
        
        risk_factors = await service._identify_risk_factors(variety_data)
        
        assert len(risk_factors) > 0
        assert any("High price volatility" in risk for risk in risk_factors)
        assert any("Uncertain demand forecast" in risk for risk in risk_factors)
        assert any("Limited market diversity" in risk for risk in risk_factors)
    
    @pytest.mark.asyncio
    async def test_identify_competitive_advantages(self, service):
        """Test competitive advantage identification."""
        variety_data = {
            'premium_discount_data': [
                {'quality_premium': 0.20},
                {'quality_premium': 0.15}
            ],
            'market_prices': [
                MagicMock(confidence=0.9),
                MagicMock(confidence=0.85),
                MagicMock(confidence=0.95)
            ]
        }
        
        advantages = await service._identify_competitive_advantages(variety_data)
        
        assert len(advantages) > 0
        assert any("Quality premium advantage" in adv for adv in advantages)
        assert any("Strong market acceptance" in adv for adv in advantages)
    
    @pytest.mark.asyncio
    async def test_generate_recommendations(self, service):
        """Test recommendation generation."""
        variety_data = {'market_prices': []}
        
        market_trends = MarketTrend(
            variety_name="Test Variety",
            crop_name="corn",
            trend_direction="up",
            trend_strength="strong",
            confidence=0.8
        )
        
        demand_forecast = DemandForecast(
            variety_name="Test Variety",
            crop_name="corn",
            domestic_demand=1.15,
            export_demand=1.25,
            confidence=0.8
        )
        
        basis_analysis = BasisAnalysis(
            variety_name="Test Variety",
            crop_name="corn",
            current_basis=Decimal('0.20'),
            historical_basis_avg=Decimal('0.15'),
            location="US",
            confidence=0.8
        )
        
        recommendations = await service._generate_recommendations(
            variety_data, market_trends, basis_analysis, demand_forecast
        )
        
        assert 'pricing' in recommendations
        assert 'timing' in recommendations
        assert 'contracts' in recommendations
        
        assert any("forward pricing" in rec.lower() for rec in recommendations['pricing'])
        assert any("domestic demand" in rec.lower() for rec in recommendations['timing'])
        assert any("export market" in rec.lower() for rec in recommendations['timing'])
        assert any("basis contracts" in rec.lower() for rec in recommendations['contracts'])
    
    @pytest.mark.asyncio
    async def test_generate_executive_summary(self, service):
        """Test executive summary generation."""
        variety_data = {
            'variety': MagicMock(variety_name="Test Variety", crop_name="corn"),
            'market_prices': [
                MagicMock(price_per_unit=Decimal('4.00')),
                MagicMock(price_per_unit=Decimal('4.50'))
            ]
        }
        
        market_trends = MarketTrend(
            variety_name="Test Variety",
            crop_name="corn",
            trend_direction="up",
            trend_strength="moderate",
            confidence=0.8
        )
        
        opportunities = ["Premium pricing opportunity", "Strong demand"]
        risk_factors = ["High volatility", "Market uncertainty"]
        
        summary = await service._generate_executive_summary(
            variety_data, market_trends, opportunities, risk_factors
        )
        
        assert "Test Variety" in summary
        assert "corn" in summary
        assert "up" in summary
        assert "moderate" in summary
        assert "2 identified" in summary  # opportunities
        assert "2 identified" in summary  # risk factors
        assert "$4.00 - $4.50" in summary  # price range
    
    def test_calculate_report_confidence(self, service):
        """Test report confidence calculation."""
        variety_data = {
            'market_prices': [
                MagicMock(confidence=0.9),
                MagicMock(confidence=0.8),
                MagicMock(confidence=0.7)
            ],
            'trend_data': [
                {'confidence': 0.85},
                {'confidence': 0.75}
            ]
        }
        
        confidence = service._calculate_report_confidence(variety_data)
        
        # Should be average of all confidence scores
        expected_confidence = (0.9 + 0.8 + 0.7 + 0.85 + 0.75) / 5
        assert abs(confidence - expected_confidence) < 0.01
    
    def test_calculate_data_quality(self, service):
        """Test data quality calculation."""
        variety_data = {
            'market_prices': [
                MagicMock(price_per_unit=Decimal('4.00'), price_date=date.today()),
                MagicMock(price_per_unit=Decimal('4.25'), price_date=date.today()),
                MagicMock(price_per_unit=Decimal('4.50'), price_date=date.today() - timedelta(days=5))
            ]
        }
        
        quality = service._calculate_data_quality(variety_data)
        
        # Should consider completeness, recency, and diversity
        assert 0.0 <= quality <= 1.0
        assert quality > 0.5  # Should be reasonable quality with 3 prices
    
    def test_extract_key_insights(self, service):
        """Test key insights extraction."""
        variety_data = {
            'market_prices': [
                MagicMock(price_per_unit=Decimal('4.00')),
                MagicMock(price_per_unit=Decimal('4.50'))
            ],
            'premium_discount_data': [
                {'premium_amount': 0.25},
                {'premium_amount': 0.15}
            ]
        }
        
        market_trends = MarketTrend(
            variety_name="Test Variety",
            crop_name="corn",
            trend_direction="up",
            trend_strength="strong",
            confidence=0.8
        )
        
        insights = service._extract_key_insights(variety_data, market_trends)
        
        assert len(insights) > 0
        assert any("Average market price" in insight for insight in insights)
        assert any("Market trend: up" in insight for insight in insights)
        assert any("Average premium" in insight for insight in insights)
    
    def test_calculate_overall_confidence(self, service):
        """Test overall confidence calculation across reports."""
        reports = [
            MagicMock(confidence=0.8),
            MagicMock(confidence=0.9),
            MagicMock(confidence=0.7)
        ]
        
        confidence = service._calculate_overall_confidence(reports)
        
        expected_confidence = (0.8 + 0.9 + 0.7) / 3
        assert abs(confidence - expected_confidence) < 0.01
    
    def test_calculate_coverage_score(self, service):
        """Test data coverage score calculation."""
        reports = [
            MagicMock(data_quality_score=0.8),
            MagicMock(data_quality_score=0.9),
            MagicMock(data_quality_score=0.7)
        ]
        
        coverage = service._calculate_coverage_score(reports)
        
        expected_coverage = (0.8 + 0.9 + 0.7) / 3
        assert abs(coverage - expected_coverage) < 0.01
    
    def test_count_markets_analyzed(self, service):
        """Test market count calculation."""
        reports = [
            MagicMock(current_prices=[MagicMock(), MagicMock()]),
            MagicMock(current_prices=[MagicMock()]),
            MagicMock(current_prices=[MagicMock(), MagicMock(), MagicMock()])
        ]
        
        count = service._count_markets_analyzed(reports)
        
        assert count == 6  # 2 + 1 + 3
    
    def test_count_price_points(self, service):
        """Test price point count calculation."""
        reports = [
            MagicMock(current_prices=[MagicMock(), MagicMock()]),
            MagicMock(current_prices=[MagicMock()]),
            MagicMock(current_prices=[MagicMock(), MagicMock(), MagicMock()])
        ]
        
        count = service._count_price_points(reports)
        
        assert count == 6  # 2 + 1 + 3


class TestMarketDataCache:
    """Test suite for MarketDataCache."""
    
    @pytest.fixture
    def cache(self):
        from services.market_intelligence_service import MarketDataCache
        return MarketDataCache()
    
    @pytest.mark.asyncio
    async def test_cache_data_and_retrieve(self, cache):
        """Test caching and retrieving data."""
        test_data = {"test": "data"}
        cache_key = "test_key"
        
        # Cache data
        await cache.cache_data(cache_key, test_data)
        
        # Retrieve data
        retrieved_data = await cache.get_cached_data(cache_key)
        
        assert retrieved_data == test_data
    
    @pytest.mark.asyncio
    async def test_cache_expiry(self, cache):
        """Test cache expiry functionality."""
        test_data = {"test": "data"}
        cache_key = "test_key"
        
        # Cache data
        await cache.cache_data(cache_key, test_data)
        
        # Manually expire cache by setting old timestamp
        cache.cache[cache_key] = (test_data, datetime.utcnow().timestamp() - 4000)  # 4000 seconds ago
        
        # Try to retrieve expired data
        retrieved_data = await cache.get_cached_data(cache_key)
        
        assert retrieved_data is None
        assert cache_key not in cache.cache  # Should be cleaned up


class TestMarketAnalysisEngine:
    """Test suite for MarketAnalysisEngine."""
    
    @pytest.fixture
    def engine(self):
        from services.market_intelligence_service import MarketAnalysisEngine
        return MarketAnalysisEngine()
    
    @pytest.fixture
    def mock_variety(self):
        variety = MagicMock(spec=EnhancedCropVariety)
        variety.id = uuid4()
        variety.variety_name = "Test Variety"
        variety.crop_name = "corn"
        return variety
    
    @pytest.mark.asyncio
    async def test_analyze_market_trends(self, engine, mock_variety):
        """Test market trend analysis."""
        trend_data = [
            {'days_ago': 7, 'price': 4.25, 'trend_percent': 2.5},
            {'days_ago': 30, 'price': 4.00, 'trend_percent': 6.25}
        ]
        
        result = await engine.analyze_market_trends(mock_variety, trend_data)
        
        assert isinstance(result, MarketTrend)
        assert result.variety_name == "Test Variety"
        assert result.crop_name == "corn"
        assert result.confidence == 0.8
    
    @pytest.mark.asyncio
    async def test_analyze_basis(self, engine, mock_variety):
        """Test basis analysis."""
        basis_data = [
            {'location': 'US', 'current_basis': -0.15, 'historical_avg': -0.20}
        ]
        
        result = await engine.analyze_basis(mock_variety, basis_data)
        
        assert isinstance(result, BasisAnalysis)
        assert result.variety_name == "Test Variety"
        assert result.crop_name == "corn"
        assert result.current_basis == Decimal('0.25')
        assert result.confidence == 0.8
    
    @pytest.mark.asyncio
    async def test_forecast_demand(self, engine, mock_variety):
        """Test demand forecasting."""
        demand_data = [
            {'demand_type': 'domestic', 'demand_factor': 1.05},
            {'demand_type': 'export', 'demand_factor': 1.15}
        ]
        
        result = await engine.forecast_demand(mock_variety, demand_data)
        
        assert isinstance(result, DemandForecast)
        assert result.variety_name == "Test Variety"
        assert result.crop_name == "corn"
        assert result.confidence == 0.7
    
    @pytest.mark.asyncio
    async def test_analyze_premiums_discounts(self, engine, mock_variety):
        """Test premium/discount analysis."""
        premium_data = [
            {'premium_type': 'organic', 'premium_amount': 0.50},
            {'premium_type': 'quality', 'premium_amount': 0.25}
        ]
        
        result = await engine.analyze_premiums_discounts(mock_variety, premium_data)
        
        assert isinstance(result, PremiumDiscountAnalysis)
        assert result.variety_name == "Test Variety"
        assert result.crop_name == "corn"
        assert result.market_location == "US"
        assert result.confidence == 0.8


@pytest.mark.performance
class TestMarketIntelligencePerformance:
    """Performance tests for market intelligence service."""
    
    @pytest.mark.asyncio
    async def test_response_time_requirement(self):
        """Test that market intelligence analysis completes within acceptable time."""
        import time
        
        service = MarketIntelligenceService()
        request = MarketIntelligenceRequest(
            variety_names=["Test Variety"],
            detail_level="basic"
        )
        
        start_time = time.time()
        
        with patch.object(service, '_collect_market_data', return_value=[]):
            with patch.object(service, '_generate_market_report', return_value=None):
                await service.get_market_intelligence(request)
        
        elapsed = time.time() - start_time
        assert elapsed < 5.0, f"Response time {elapsed}s exceeds 5s requirement"
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling of concurrent market intelligence requests."""
        service = MarketIntelligenceService()
        requests = [
            MarketIntelligenceRequest(variety_names=[f"Variety {i}"], detail_level="basic")
            for i in range(10)
        ]
        
        with patch.object(service, '_collect_market_data', return_value=[]):
            with patch.object(service, '_generate_market_report', return_value=None):
                tasks = [service.get_market_intelligence(req) for req in requests]
                results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All requests should complete successfully
        assert len(results) == 10
        assert all(not isinstance(result, Exception) for result in results)
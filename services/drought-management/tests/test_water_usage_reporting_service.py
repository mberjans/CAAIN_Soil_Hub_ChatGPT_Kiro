"""
Tests for Water Usage Reporting Service

Comprehensive test suite for water usage reporting, analytics, and benchmarking functionality.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from decimal import Decimal

from src.services.water_usage_reporting_service import WaterUsageReportingService
from src.models.water_usage_models import (
    WaterUsageRecord,
    WaterUsageReport,
    WaterUsageSummary,
    WaterSourceType,
    WaterUsageType
)


class TestWaterUsageReportingService:
    """Test suite for WaterUsageReportingService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return WaterUsageReportingService()
    
    @pytest.fixture
    def sample_farm_id(self):
        """Sample farm location ID."""
        return uuid4()
    
    @pytest.fixture
    def sample_field_id(self):
        """Sample field ID."""
        return uuid4()
    
    @pytest.fixture
    def sample_usage_records(self, sample_farm_id, sample_field_id):
        """Sample water usage records for testing."""
        return [
            WaterUsageRecord(
                record_id=uuid4(),
                farm_location_id=sample_farm_id,
                field_id=sample_field_id,
                timestamp=datetime.utcnow() - timedelta(days=i),
                water_source=WaterSourceType.IRRIGATION,
                usage_type=WaterUsageType.CROP_IRRIGATION,
                volume_gallons=Decimal("1000.0"),
                total_cost=Decimal("10.0"),
                efficiency_rating=0.8,
                data_source="test"
            )
            for i in range(30)  # 30 days of data
        ]
    
    @pytest.mark.asyncio
    async def test_initialize_service(self, service):
        """Test service initialization."""
        await service.initialize()
        assert service.initialized is True
        assert len(service.report_templates) > 0
        assert len(service.benchmark_data) > 0
    
    @pytest.mark.asyncio
    async def test_generate_comprehensive_report(self, service, sample_farm_id, sample_field_id, sample_usage_records):
        """Test comprehensive report generation."""
        await service.initialize()
        
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()
        
        with patch.object(service, '_get_usage_data_for_report', return_value=sample_usage_records) as mock_get_data:
            with patch.object(service, '_generate_total_summary', new_callable=AsyncMock) as mock_summary:
                with patch.object(service, '_generate_field_summaries', return_value=[]) as mock_field_summaries:
                    with patch.object(service, '_analyze_usage_trends', return_value={"trend_direction": "stable"}) as mock_trends:
                        with patch.object(service, '_analyze_efficiency', return_value={"overall_efficiency": 0.8}) as mock_efficiency:
                            with patch.object(service, '_analyze_costs', return_value={"total_cost": 300.0}) as mock_costs:
                                with patch.object(service, '_analyze_savings', return_value={"total_savings": 50.0}) as mock_savings:
                                    with patch.object(service, '_generate_recommendations', return_value=["Improve irrigation"]) as mock_recommendations:
                                        with patch.object(service, '_generate_alerts', return_value=[]) as mock_alerts:
                                            with patch.object(service, '_calculate_performance_metrics', return_value={"water_use_efficiency": 0.5}) as mock_metrics:
                                                
                                                mock_summary.return_value = WaterUsageSummary(
                                                    summary_id=uuid4(),
                                                    farm_location_id=sample_farm_id,
                                                    field_id=sample_field_id,
                                                    period_start=start_date,
                                                    period_end=end_date,
                                                    total_volume_gallons=Decimal("30000.0"),
                                                    total_cost=Decimal("300.0"),
                                                    average_daily_usage=Decimal("1000.0"),
                                                    usage_by_source={WaterSourceType.IRRIGATION: Decimal("30000.0")},
                                                    usage_by_type={WaterUsageType.CROP_IRRIGATION: Decimal("30000.0")}
                                                )
                                                
                                                report = await service.generate_comprehensive_report(
                                                    farm_location_id=sample_farm_id,
                                                    start_date=start_date,
                                                    end_date=end_date,
                                                    field_id=sample_field_id,
                                                    report_type="monthly",
                                                    include_benchmarks=True,
                                                    include_recommendations=True
                                                )
                                                
                                                assert report.farm_location_id == sample_farm_id
                                                assert report.report_period_start == start_date
                                                assert report.report_period_end == end_date
                                                assert report.report_type == "monthly"
                                                assert report.total_water_usage is not None
                                                assert report.usage_trends["trend_direction"] == "stable"
                                                assert report.efficiency_analysis["overall_efficiency"] == 0.8
                                                assert report.cost_analysis["total_cost"] == 300.0
                                                assert report.savings_analysis["total_savings"] == 50.0
                                                assert len(report.recommendations) > 0
                                                assert report.performance_metrics["water_use_efficiency"] == 0.5
                                                
                                                mock_get_data.assert_called_once()
                                                mock_summary.assert_called_once()
                                                mock_field_summaries.assert_called_once()
                                                mock_trends.assert_called_once()
                                                mock_efficiency.assert_called_once()
                                                mock_costs.assert_called_once()
                                                mock_savings.assert_called_once()
                                                mock_recommendations.assert_called_once()
                                                mock_alerts.assert_called_once()
                                                mock_metrics.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_trend_analysis(self, service, sample_farm_id, sample_field_id, sample_usage_records):
        """Test trend analysis generation."""
        await service.initialize()
        
        start_date = datetime.utcnow() - timedelta(days=90)
        end_date = datetime.utcnow()
        
        with patch.object(service, '_get_historical_usage_data', return_value=sample_usage_records) as mock_historical:
            with patch.object(service, '_analyze_volume_trends', return_value={"trend_direction": "increasing"}) as mock_volume:
                with patch.object(service, '_analyze_cost_trends', return_value={"trend_direction": "stable"}) as mock_cost:
                    with patch.object(service, '_analyze_efficiency_trends', return_value={"trend_direction": "improving"}) as mock_efficiency:
                        with patch.object(service, '_analyze_seasonal_patterns', return_value={"seasonal_variation": 0.2}) as mock_seasonal:
                            with patch.object(service, '_predict_future_trends', return_value={"predicted_volume": 35000.0}) as mock_future:
                                with patch.object(service, '_identify_anomalies', return_value=[]) as mock_anomalies:
                                    with patch.object(service, '_generate_trend_summary', return_value={"overall_trend": "improving"}) as mock_summary:
                                        
                                        trend_analysis = await service.generate_trend_analysis(
                                            farm_location_id=sample_farm_id,
                                            start_date=start_date,
                                            end_date=end_date,
                                            field_id=sample_field_id,
                                            trend_period="monthly"
                                        )
                                        
                                        assert trend_analysis["analysis_period"]["start_date"] == start_date.isoformat()
                                        assert trend_analysis["analysis_period"]["end_date"] == end_date.isoformat()
                                        assert trend_analysis["analysis_period"]["trend_period"] == "monthly"
                                        assert trend_analysis["volume_trends"]["trend_direction"] == "increasing"
                                        assert trend_analysis["cost_trends"]["trend_direction"] == "stable"
                                        assert trend_analysis["efficiency_trends"]["trend_direction"] == "improving"
                                        assert trend_analysis["seasonal_patterns"]["seasonal_variation"] == 0.2
                                        assert trend_analysis["future_predictions"]["predicted_volume"] == 35000.0
                                        assert trend_analysis["summary"]["overall_trend"] == "improving"
                                        
                                        mock_historical.assert_called_once()
                                        mock_volume.assert_called_once()
                                        mock_cost.assert_called_once()
                                        mock_efficiency.assert_called_once()
                                        mock_seasonal.assert_called_once()
                                        mock_future.assert_called_once()
                                        mock_anomalies.assert_called_once()
                                        mock_summary.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_benchmark_report(self, service, sample_farm_id, sample_field_id):
        """Test benchmark report generation."""
        await service.initialize()
        
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()
        
        with patch.object(service, '_get_farm_performance_data', return_value={"irrigation_efficiency": 0.75}) as mock_farm_data:
            with patch.object(service, '_get_industry_benchmarks', return_value={"irrigation_efficiency": 0.72}) as mock_industry:
                with patch.object(service, '_get_regional_benchmarks', return_value={"irrigation_efficiency": 0.70}) as mock_regional:
                    with patch.object(service, '_get_peer_benchmarks', return_value={"irrigation_efficiency": 0.73}) as mock_peer:
                        with patch.object(service, '_compare_to_benchmarks', return_value={"irrigation_efficiency": {"farm_value": 0.75, "benchmark_value": 0.72, "performance": "above"}}) as mock_compare:
                            with patch.object(service, '_calculate_benchmark_rankings', return_value={"industry_ranking": 75}) as mock_rankings:
                                with patch.object(service, '_identify_benchmark_improvements', return_value=["Improve efficiency"]) as mock_improvements:
                                    with patch.object(service, '_generate_benchmark_summary', return_value={"overall_performance": "above_average"}) as mock_summary:
                                        
                                        benchmark_report = await service.generate_benchmark_report(
                                            farm_location_id=sample_farm_id,
                                            start_date=start_date,
                                            end_date=end_date,
                                            field_id=sample_field_id
                                        )
                                        
                                        assert benchmark_report["benchmark_period"]["start_date"] == start_date.isoformat()
                                        assert benchmark_report["benchmark_period"]["end_date"] == end_date.isoformat()
                                        assert benchmark_report["farm_performance"]["irrigation_efficiency"] == 0.75
                                        assert benchmark_report["industry_comparison"]["irrigation_efficiency"]["performance"] == "above"
                                        assert benchmark_report["rankings"]["industry_ranking"] == 75
                                        assert len(benchmark_report["improvement_opportunities"]) > 0
                                        assert benchmark_report["summary"]["overall_performance"] == "above_average"
                                        
                                        mock_farm_data.assert_called_once()
                                        mock_industry.assert_called_once()
                                        mock_regional.assert_called_once()
                                        mock_peer.assert_called_once()
                                        mock_compare.assert_called()
                                        mock_rankings.assert_called_once()
                                        mock_improvements.assert_called_once()
                                        mock_summary.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_efficiency_report(self, service, sample_farm_id, sample_field_id, sample_usage_records):
        """Test efficiency report generation."""
        await service.initialize()
        
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()
        
        with patch.object(service, '_get_usage_data_for_report', return_value=sample_usage_records) as mock_get_data:
            with patch.object(service, '_calculate_detailed_efficiency_metrics', return_value={"overall_efficiency": 0.78}) as mock_metrics:
                with patch.object(service, '_analyze_source_efficiency', return_value={"irrigation": 0.75}) as mock_source:
                    with patch.object(service, '_analyze_type_efficiency', return_value={"crop_irrigation": 0.75}) as mock_type:
                        with patch.object(service, '_analyze_temporal_efficiency', return_value={"daily_patterns": {}}) as mock_temporal:
                            with patch.object(service, '_identify_efficiency_bottlenecks', return_value=[{"bottleneck_type": "distribution", "severity": "medium"}]) as mock_bottlenecks:
                                with patch.object(service, '_generate_optimization_recommendations', return_value=["Improve distribution"]) as mock_recommendations:
                                    with patch.object(service, '_calculate_potential_improvements', return_value={"efficiency_improvement": 0.1}) as mock_improvements:
                                        with patch.object(service, '_generate_efficiency_summary', return_value={"overall_efficiency": 0.78, "efficiency_grade": "B"}) as mock_summary:
                                            
                                            efficiency_report = await service.generate_efficiency_report(
                                                farm_location_id=sample_farm_id,
                                                start_date=start_date,
                                                end_date=end_date,
                                                field_id=sample_field_id
                                            )
                                            
                                            assert efficiency_report["analysis_period"]["start_date"] == start_date.isoformat()
                                            assert efficiency_report["analysis_period"]["end_date"] == end_date.isoformat()
                                            assert efficiency_report["efficiency_metrics"]["overall_efficiency"] == 0.78
                                            assert efficiency_report["source_efficiency"]["irrigation"] == 0.75
                                            assert efficiency_report["type_efficiency"]["crop_irrigation"] == 0.75
                                            assert len(efficiency_report["bottlenecks"]) > 0
                                            assert len(efficiency_report["optimization_recommendations"]) > 0
                                            assert efficiency_report["potential_improvements"]["efficiency_improvement"] == 0.1
                                            assert efficiency_report["summary"]["efficiency_grade"] == "B"
                                            
                                            mock_get_data.assert_called_once()
                                            mock_metrics.assert_called_once()
                                            mock_source.assert_called_once()
                                            mock_type.assert_called_once()
                                            mock_temporal.assert_called_once()
                                            mock_bottlenecks.assert_called_once()
                                            mock_recommendations.assert_called_once()
                                            mock_improvements.assert_called_once()
                                            mock_summary.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_export_report_data_json(self, service):
        """Test report data export in JSON format."""
        await service.initialize()
        
        # Create a sample report
        report = WaterUsageReport(
            report_id=uuid4(),
            farm_location_id=uuid4(),
            report_period_start=datetime.utcnow() - timedelta(days=30),
            report_period_end=datetime.utcnow(),
            report_type="monthly",
            total_water_usage=WaterUsageSummary(
                summary_id=uuid4(),
                farm_location_id=uuid4(),
                period_start=datetime.utcnow() - timedelta(days=30),
                period_end=datetime.utcnow(),
                total_volume_gallons=Decimal("30000.0"),
                total_cost=Decimal("300.0"),
                average_daily_usage=Decimal("1000.0"),
                usage_by_source={WaterSourceType.IRRIGATION: Decimal("30000.0")},
                usage_by_type={WaterUsageType.CROP_IRRIGATION: Decimal("30000.0")}
            ),
            field_summaries=[],
            usage_trends={"trend_direction": "stable"},
            efficiency_analysis={"overall_efficiency": 0.8},
            cost_analysis={"total_cost": 300.0},
            savings_analysis={"total_savings": 50.0},
            recommendations=["Improve irrigation"],
            alerts_generated=[],
            performance_metrics={"water_use_efficiency": 0.5}
        )
        
        export_data = await service.export_report_data(
            report=report,
            export_format="json",
            include_charts=False
        )
        
        assert export_data["report_id"] == str(report.report_id)
        assert export_data["farm_location_id"] == str(report.farm_location_id)
        assert export_data["report_type"] == "monthly"
        assert export_data["total_usage"]["volume_gallons"] == 30000.0
        assert export_data["total_usage"]["total_cost"] == 300.0
        assert export_data["usage_trends"]["trend_direction"] == "stable"
        assert export_data["efficiency_analysis"]["overall_efficiency"] == 0.8
        assert len(export_data["recommendations"]) > 0
    
    @pytest.mark.asyncio
    async def test_export_report_data_with_charts(self, service):
        """Test report data export with chart data."""
        await service.initialize()
        
        report = WaterUsageReport(
            report_id=uuid4(),
            farm_location_id=uuid4(),
            report_period_start=datetime.utcnow() - timedelta(days=30),
            report_period_end=datetime.utcnow(),
            report_type="monthly",
            total_water_usage=WaterUsageSummary(
                summary_id=uuid4(),
                farm_location_id=uuid4(),
                period_start=datetime.utcnow() - timedelta(days=30),
                period_end=datetime.utcnow(),
                total_volume_gallons=Decimal("30000.0"),
                total_cost=Decimal("300.0"),
                average_daily_usage=Decimal("1000.0"),
                usage_by_source={},
                usage_by_type={}
            ),
            field_summaries=[],
            usage_trends={},
            efficiency_analysis={},
            cost_analysis={},
            savings_analysis={},
            recommendations=[],
            alerts_generated=[],
            performance_metrics={}
        )
        
        with patch.object(service, '_generate_chart_data', return_value={"usage_timeline": {}, "efficiency_trends": {}}) as mock_charts:
            
            export_data = await service.export_report_data(
                report=report,
                export_format="json",
                include_charts=True
            )
            
            assert "charts" in export_data
            assert "usage_timeline" in export_data["charts"]
            assert "efficiency_trends" in export_data["charts"]
            mock_charts.assert_called_once_with(report)
    
    @pytest.mark.asyncio
    async def test_cleanup_service(self, service):
        """Test service cleanup."""
        await service.initialize()
        
        await service.cleanup()
        
        # Service should still be initialized after cleanup
        assert service.initialized is True


class TestWaterUsageReportTemplates:
    """Test suite for report template functionality."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return WaterUsageReportingService()
    
    @pytest.mark.asyncio
    async def test_load_report_templates(self, service):
        """Test report template loading."""
        await service.initialize()
        
        # Check that templates are loaded
        assert "daily" in service.report_templates
        assert "weekly" in service.report_templates
        assert "monthly" in service.report_templates
        assert "annual" in service.report_templates
        
        # Check template structure
        daily_template = service.report_templates["daily"]
        assert "sections" in daily_template
        assert "charts" in daily_template
        assert "summary" in daily_template["sections"]
        assert "trends" in daily_template["sections"]
        
        monthly_template = service.report_templates["monthly"]
        assert "benchmarks" in monthly_template["sections"]
        assert "recommendations" in monthly_template["sections"]
    
    @pytest.mark.asyncio
    async def test_load_benchmark_data(self, service):
        """Test benchmark data loading."""
        await service.initialize()
        
        # Check that benchmark data is loaded
        assert "industry_averages" in service.benchmark_data
        assert "regional_averages" in service.benchmark_data
        
        # Check benchmark data structure
        industry_averages = service.benchmark_data["industry_averages"]
        assert "irrigation_efficiency" in industry_averages
        assert "water_use_efficiency" in industry_averages
        assert "cost_efficiency" in industry_averages
        
        assert industry_averages["irrigation_efficiency"] == 0.75
        assert industry_averages["water_use_efficiency"] == 0.5
        assert industry_averages["cost_efficiency"] == 2.0


class TestWaterUsageAnalytics:
    """Test suite for analytics functionality."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return WaterUsageReportingService()
    
    @pytest.mark.asyncio
    async def test_analyze_usage_trends(self, service, sample_usage_records):
        """Test usage trends analysis."""
        await service.initialize()
        
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()
        
        trends = await service._analyze_usage_trends(sample_usage_records, start_date, end_date)
        
        assert "trend_direction" in trends
        assert "trend_strength" in trends
        assert "seasonal_patterns" in trends
        assert "anomalies" in trends
    
    @pytest.mark.asyncio
    async def test_analyze_efficiency(self, service, sample_usage_records):
        """Test efficiency analysis."""
        await service.initialize()
        
        efficiency = await service._analyze_efficiency(sample_usage_records)
        
        assert "overall_efficiency" in efficiency
        assert "efficiency_trend" in efficiency
        assert "bottlenecks" in efficiency
        assert "optimization_opportunities" in efficiency
    
    @pytest.mark.asyncio
    async def test_analyze_costs(self, service, sample_usage_records):
        """Test cost analysis."""
        await service.initialize()
        
        costs = await service._analyze_costs(sample_usage_records)
        
        assert "total_cost" in costs
        assert "cost_per_gallon" in costs
        assert "cost_trend" in costs
        assert "cost_optimization" in costs
    
    @pytest.mark.asyncio
    async def test_generate_recommendations(self, service, sample_farm_id, sample_usage_records):
        """Test recommendation generation."""
        await service.initialize()
        
        efficiency_analysis = {"overall_efficiency": 0.7}
        cost_analysis = {"total_cost": 500.0}
        
        recommendations = await service._generate_recommendations(
            sample_farm_id, sample_usage_records, efficiency_analysis, cost_analysis
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert all(isinstance(rec, str) for rec in recommendations)


class TestWaterUsagePerformance:
    """Performance tests for water usage reporting."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return WaterUsageReportingService()
    
    @pytest.mark.asyncio
    async def test_large_dataset_report_generation(self, service, sample_farm_id):
        """Test report generation with large dataset."""
        await service.initialize()
        
        # Create large dataset
        large_dataset = [
            WaterUsageRecord(
                record_id=uuid4(),
                farm_location_id=sample_farm_id,
                timestamp=datetime.utcnow() - timedelta(days=i),
                water_source=WaterSourceType.IRRIGATION,
                usage_type=WaterUsageType.CROP_IRRIGATION,
                volume_gallons=Decimal("1000.0"),
                total_cost=Decimal("10.0"),
                efficiency_rating=0.8,
                data_source="performance_test"
            )
            for i in range(1000)  # 1000 records
        ]
        
        start_date = datetime.utcnow() - timedelta(days=365)
        end_date = datetime.utcnow()
        
        with patch.object(service, '_get_usage_data_for_report', return_value=large_dataset):
            with patch.object(service, '_generate_total_summary', new_callable=AsyncMock) as mock_summary:
                with patch.object(service, '_generate_field_summaries', return_value=[]):
                    with patch.object(service, '_analyze_usage_trends', return_value={"trend_direction": "stable"}):
                        with patch.object(service, '_analyze_efficiency', return_value={"overall_efficiency": 0.8}):
                            with patch.object(service, '_analyze_costs', return_value={"total_cost": 10000.0}):
                                with patch.object(service, '_analyze_savings', return_value={"total_savings": 1000.0}):
                                    with patch.object(service, '_generate_recommendations', return_value=["Improve efficiency"]):
                                        with patch.object(service, '_generate_alerts', return_value=[]):
                                            with patch.object(service, '_calculate_performance_metrics', return_value={"water_use_efficiency": 0.5}):
                                                
                                                mock_summary.return_value = WaterUsageSummary(
                                                    summary_id=uuid4(),
                                                    farm_location_id=sample_farm_id,
                                                    period_start=start_date,
                                                    period_end=end_date,
                                                    total_volume_gallons=Decimal("1000000.0"),
                                                    total_cost=Decimal("10000.0"),
                                                    average_daily_usage=Decimal("2739.73"),
                                                    usage_by_source={},
                                                    usage_by_type={}
                                                )
                                                
                                                start_time = datetime.utcnow()
                                                
                                                report = await service.generate_comprehensive_report(
                                                    farm_location_id=sample_farm_id,
                                                    start_date=start_date,
                                                    end_date=end_date,
                                                    report_type="annual"
                                                )
                                                
                                                end_time = datetime.utcnow()
                                                duration = (end_time - start_time).total_seconds()
                                                
                                                assert report.total_water_usage.total_volume_gallons == Decimal("1000000.0")
                                                assert duration < 5.0  # Should complete within 5 seconds
    
    @pytest.mark.asyncio
    async def test_concurrent_report_generation(self, service, sample_farm_id):
        """Test concurrent report generation."""
        await service.initialize()
        
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()
        
        # Generate multiple reports concurrently
        tasks = []
        for i in range(5):
            task = service.generate_comprehensive_report(
                farm_location_id=sample_farm_id,
                start_date=start_date,
                end_date=end_date,
                report_type="monthly"
            )
            tasks.append(task)
        
        start_time = datetime.utcnow()
        reports = await asyncio.gather(*tasks)
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        assert len(reports) == 5
        assert duration < 10.0  # Should complete within 10 seconds
        assert all(report.farm_location_id == sample_farm_id for report in reports)
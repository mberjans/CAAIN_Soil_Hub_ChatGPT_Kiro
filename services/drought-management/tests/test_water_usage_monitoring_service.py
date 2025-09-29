"""
Tests for Water Usage Monitoring Service

Comprehensive test suite for water usage tracking, monitoring, and reporting functionality.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from decimal import Decimal

from src.services.water_usage_monitoring_service import WaterUsageMonitoringService
from src.models.water_usage_models import (
    WaterUsageRecord,
    WaterUsageSummary,
    WaterUsageAlert,
    WaterUsageReport,
    WaterUsageMonitoringConfig,
    WaterUsageRequest,
    WaterUsageResponse,
    WaterUsageEfficiencyMetrics,
    WaterSourceType,
    WaterUsageType,
    MonitoringFrequency
)


class TestWaterUsageMonitoringService:
    """Test suite for WaterUsageMonitoringService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return WaterUsageMonitoringService()
    
    @pytest.fixture
    def sample_farm_id(self):
        """Sample farm location ID."""
        return uuid4()
    
    @pytest.fixture
    def sample_field_id(self):
        """Sample field ID."""
        return uuid4()
    
    @pytest.fixture
    def sample_usage_record(self, sample_farm_id, sample_field_id):
        """Sample water usage record."""
        return WaterUsageRecord(
            record_id=uuid4(),
            farm_location_id=sample_farm_id,
            field_id=sample_field_id,
            timestamp=datetime.utcnow(),
            water_source=WaterSourceType.IRRIGATION,
            usage_type=WaterUsageType.CROP_IRRIGATION,
            volume_gallons=Decimal("1000.0"),
            duration_minutes=60,
            flow_rate_gpm=Decimal("16.67"),
            cost_per_gallon=Decimal("0.01"),
            total_cost=Decimal("10.0"),
            efficiency_rating=0.85,
            notes="Test irrigation event",
            recorded_by="test_user",
            data_source="manual"
        )
    
    @pytest.fixture
    def sample_monitoring_config(self, sample_farm_id):
        """Sample monitoring configuration."""
        return WaterUsageMonitoringConfig(
            config_id=uuid4(),
            farm_location_id=sample_farm_id,
            monitoring_enabled=True,
            monitoring_frequency=MonitoringFrequency.DAILY,
            data_retention_days=365,
            high_usage_threshold_gallons=Decimal("2000.0"),
            high_cost_threshold_dollars=Decimal("50.0"),
            low_efficiency_threshold=0.7,
            email_alerts=True,
            sms_alerts=False,
            alert_recipients=["farmer@example.com"],
            sensor_integration=False,
            api_integration=True,
            manual_entry=True
        )
    
    @pytest.mark.asyncio
    async def test_initialize_service(self, service):
        """Test service initialization."""
        await service.initialize()
        assert service.initialized is True
    
    @pytest.mark.asyncio
    async def test_record_water_usage_success(self, service, sample_farm_id):
        """Test successful water usage recording."""
        await service.initialize()
        
        with patch.object(service, '_store_usage_record', new_callable=AsyncMock) as mock_store:
            with patch.object(service, '_check_usage_alerts', new_callable=AsyncMock) as mock_alerts:
                with patch.object(service, '_update_usage_cache', new_callable=AsyncMock) as mock_cache:
                    
                    record = await service.record_water_usage(
                        farm_location_id=sample_farm_id,
                        water_source=WaterSourceType.IRRIGATION,
                        usage_type=WaterUsageType.CROP_IRRIGATION,
                        volume_gallons=Decimal("1000.0"),
                        duration_minutes=60,
                        cost_per_gallon=Decimal("0.01"),
                        efficiency_rating=0.85,
                        notes="Test irrigation",
                        recorded_by="test_user"
                    )
                    
                    assert record.farm_location_id == sample_farm_id
                    assert record.water_source == WaterSourceType.IRRIGATION
                    assert record.usage_type == WaterUsageType.CROP_IRRIGATION
                    assert record.volume_gallons == Decimal("1000.0")
                    assert record.total_cost == Decimal("10.0")
                    assert record.efficiency_rating == 0.85
                    
                    mock_store.assert_called_once()
                    mock_alerts.assert_called_once()
                    mock_cache.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_record_water_usage_with_alert(self, service, sample_farm_id, sample_monitoring_config):
        """Test water usage recording that triggers alerts."""
        await service.initialize()
        service.monitoring_configs[sample_farm_id] = sample_monitoring_config
        
        with patch.object(service, '_store_usage_record', new_callable=AsyncMock):
            with patch.object(service, '_store_alert', new_callable=AsyncMock) as mock_store_alert:
                with patch.object(service, '_update_usage_cache', new_callable=AsyncMock):
                    
                    # Record usage that exceeds threshold
                    await service.record_water_usage(
                        farm_location_id=sample_farm_id,
                        water_source=WaterSourceType.IRRIGATION,
                        usage_type=WaterUsageType.CROP_IRRIGATION,
                        volume_gallons=Decimal("2500.0"),  # Exceeds 2000 threshold
                        cost_per_gallon=Decimal("0.01")
                    )
                    
                    # Should have triggered high usage alert
                    assert len(service.active_alerts[sample_farm_id]) > 0
                    alert = service.active_alerts[sample_farm_id][0]
                    assert alert.alert_type == "high_usage"
                    assert alert.severity == "high"
                    mock_store_alert.assert_called()
    
    @pytest.mark.asyncio
    async def test_get_water_usage_summary(self, service, sample_farm_id, sample_field_id):
        """Test water usage summary generation."""
        await service.initialize()
        
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()
        
        # Mock usage records
        mock_records = [
            WaterUsageRecord(
                record_id=uuid4(),
                farm_location_id=sample_farm_id,
                field_id=sample_field_id,
                timestamp=start_date + timedelta(days=i),
                water_source=WaterSourceType.IRRIGATION,
                usage_type=WaterUsageType.CROP_IRRIGATION,
                volume_gallons=Decimal("1000.0"),
                total_cost=Decimal("10.0"),
                efficiency_rating=0.8,
                data_source="manual"
            )
            for i in range(10)
        ]
        
        with patch.object(service, '_get_usage_records', return_value=mock_records) as mock_get_records:
            with patch.object(service, '_calculate_water_savings', return_value=Decimal("100.0")):
                
                summary = await service.get_water_usage_summary(
                    farm_location_id=sample_farm_id,
                    start_date=start_date,
                    end_date=end_date,
                    field_id=sample_field_id
                )
                
                assert summary.farm_location_id == sample_farm_id
                assert summary.field_id == sample_field_id
                assert summary.total_volume_gallons == Decimal("10000.0")
                assert summary.total_cost == Decimal("100.0")
                assert summary.average_daily_usage > Decimal("0")
                assert WaterSourceType.IRRIGATION in summary.usage_by_source
                assert WaterUsageType.CROP_IRRIGATION in summary.usage_by_type
                assert summary.efficiency_score == 0.8
                
                mock_get_records.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_water_usage_response(self, service, sample_farm_id):
        """Test comprehensive water usage response."""
        await service.initialize()
        
        request = WaterUsageRequest(
            farm_location_id=sample_farm_id,
            start_date=datetime.utcnow() - timedelta(days=30),
            end_date=datetime.utcnow(),
            include_details=True,
            generate_report=True
        )
        
        with patch.object(service, 'get_water_usage_summary', new_callable=AsyncMock) as mock_summary:
            with patch.object(service, '_get_usage_records', return_value=[]) as mock_records:
                with patch.object(service, '_get_active_alerts', return_value=[]) as mock_alerts:
                    with patch.object(service, '_generate_usage_report', new_callable=AsyncMock) as mock_report:
                        with patch.object(service, '_calculate_data_quality_score', return_value=0.9) as mock_quality:
                            
                            mock_summary.return_value = WaterUsageSummary(
                                summary_id=uuid4(),
                                farm_location_id=sample_farm_id,
                                period_start=request.start_date,
                                period_end=request.end_date,
                                total_volume_gallons=Decimal("5000.0"),
                                total_cost=Decimal("50.0"),
                                average_daily_usage=Decimal("166.67"),
                                usage_by_source={},
                                usage_by_type={}
                            )
                            
                            response = await service.get_water_usage_response(request)
                            
                            assert response.farm_location_id == sample_farm_id
                            assert response.query_period_start == request.start_date
                            assert response.query_period_end == request.end_date
                            assert response.usage_summary is not None
                            assert response.detailed_records is not None
                            assert response.data_quality_score == 0.9
                            assert response.processing_time_ms > 0
                            
                            mock_summary.assert_called_once()
                            mock_records.assert_called_once()
                            mock_alerts.assert_called_once()
                            mock_report.assert_called_once()
                            mock_quality.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_calculate_efficiency_metrics(self, service, sample_farm_id, sample_field_id):
        """Test efficiency metrics calculation."""
        await service.initialize()
        
        # Mock usage records
        mock_records = [
            WaterUsageRecord(
                record_id=uuid4(),
                farm_location_id=sample_farm_id,
                field_id=sample_field_id,
                timestamp=datetime.utcnow() - timedelta(days=i),
                water_source=WaterSourceType.IRRIGATION,
                usage_type=WaterUsageType.CROP_IRRIGATION,
                volume_gallons=Decimal("1000.0"),
                efficiency_rating=0.8,
                data_source="manual"
            )
            for i in range(10)
        ]
        
        with patch.object(service, '_get_usage_records', return_value=mock_records):
            with patch.object(service, '_calculate_irrigation_efficiency', return_value=0.8):
                with patch.object(service, '_calculate_application_efficiency', return_value=0.85):
                    with patch.object(service, '_calculate_distribution_efficiency', return_value=0.75):
                        with patch.object(service, '_calculate_storage_efficiency', return_value=0.9):
                            with patch.object(service, '_calculate_water_use_efficiency', return_value=Decimal("0.5")):
                                with patch.object(service, '_calculate_cost_efficiency', return_value=Decimal("2.0")):
                                    with patch.object(service, '_calculate_environmental_efficiency', return_value=0.7):
                                        with patch.object(service, '_get_industry_average_efficiency', return_value=0.75):
                                            with patch.object(service, '_get_regional_average_efficiency', return_value=0.72):
                                                with patch.object(service, '_calculate_farm_ranking', return_value=15):
                                                    with patch.object(service, '_identify_improvement_opportunities', return_value=["Improve irrigation scheduling"]):
                                                        with patch.object(service, '_get_best_practices', return_value=["Use precision irrigation"]):
                                                            with patch.object(service, '_calculate_target_efficiency', return_value=0.85):
                                                                
                                                                metrics = await service.calculate_efficiency_metrics(
                                                                    farm_location_id=sample_farm_id,
                                                                    field_id=sample_field_id,
                                                                    period_days=30
                                                                )
                                                                
                                                                assert metrics.farm_location_id == sample_farm_id
                                                                assert metrics.field_id == sample_field_id
                                                                assert metrics.overall_efficiency_score > 0
                                                                assert metrics.irrigation_efficiency == 0.8
                                                                assert metrics.water_application_efficiency == 0.85
                                                                assert metrics.distribution_efficiency == 0.75
                                                                assert metrics.storage_efficiency == 0.9
                                                                assert metrics.water_use_efficiency == Decimal("0.5")
                                                                assert metrics.cost_efficiency == Decimal("2.0")
                                                                assert metrics.environmental_efficiency == 0.7
                                                                assert metrics.industry_average == 0.75
                                                                assert metrics.regional_average == 0.72
                                                                assert metrics.farm_ranking == 15
                                                                assert len(metrics.improvement_opportunities) > 0
                                                                assert len(metrics.best_practices) > 0
                                                                assert metrics.target_efficiency == 0.85
    
    @pytest.mark.asyncio
    async def test_configure_monitoring(self, service, sample_monitoring_config):
        """Test monitoring configuration."""
        await service.initialize()
        
        with patch.object(service, '_store_monitoring_config', new_callable=AsyncMock) as mock_store:
            
            updated_config = await service.configure_monitoring(sample_monitoring_config)
            
            assert updated_config.farm_location_id == sample_monitoring_config.farm_location_id
            assert updated_config.monitoring_enabled is True
            assert updated_config.monitoring_frequency == MonitoringFrequency.DAILY
            assert updated_config.high_usage_threshold_gallons == Decimal("2000.0")
            assert updated_config.email_alerts is True
            
            # Check that config is stored in service
            assert sample_monitoring_config.farm_location_id in service.monitoring_configs
            
            mock_store.assert_called_once_with(sample_monitoring_config)
    
    @pytest.mark.asyncio
    async def test_empty_summary_when_no_records(self, service, sample_farm_id):
        """Test empty summary when no usage records exist."""
        await service.initialize()
        
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()
        
        with patch.object(service, '_get_usage_records', return_value=[]):
            
            summary = await service.get_water_usage_summary(
                farm_location_id=sample_farm_id,
                start_date=start_date,
                end_date=end_date
            )
            
            assert summary.farm_location_id == sample_farm_id
            assert summary.total_volume_gallons == Decimal("0")
            assert summary.total_cost == Decimal("0")
            assert summary.average_daily_usage == Decimal("0")
            assert summary.usage_by_source == {}
            assert summary.usage_by_type == {}
    
    @pytest.mark.asyncio
    async def test_cleanup_service(self, service):
        """Test service cleanup."""
        await service.initialize()
        
        await service.cleanup()
        
        # Service should still be initialized after cleanup
        assert service.initialized is True


class TestWaterUsageAlerting:
    """Test suite for water usage alerting functionality."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return WaterUsageMonitoringService()
    
    @pytest.fixture
    def sample_farm_id(self):
        """Sample farm location ID."""
        return uuid4()
    
    @pytest.mark.asyncio
    async def test_high_usage_alert(self, service, sample_farm_id):
        """Test high usage alert generation."""
        await service.initialize()
        
        config = WaterUsageMonitoringConfig(
            config_id=uuid4(),
            farm_location_id=sample_farm_id,
            high_usage_threshold_gallons=Decimal("1000.0")
        )
        service.monitoring_configs[sample_farm_id] = config
        
        record = WaterUsageRecord(
            record_id=uuid4(),
            farm_location_id=sample_farm_id,
            timestamp=datetime.utcnow(),
            water_source=WaterSourceType.IRRIGATION,
            usage_type=WaterUsageType.CROP_IRRIGATION,
            volume_gallons=Decimal("1500.0"),  # Exceeds threshold
            data_source="manual"
        )
        
        with patch.object(service, '_store_alert', new_callable=AsyncMock):
            await service._check_usage_alerts(record)
            
            assert len(service.active_alerts[sample_farm_id]) == 1
            alert = service.active_alerts[sample_farm_id][0]
            assert alert.alert_type == "high_usage"
            assert alert.severity == "high"
            assert alert.threshold_value == Decimal("1000.0")
            assert alert.actual_value == Decimal("1500.0")
    
    @pytest.mark.asyncio
    async def test_high_cost_alert(self, service, sample_farm_id):
        """Test high cost alert generation."""
        await service.initialize()
        
        config = WaterUsageMonitoringConfig(
            config_id=uuid4(),
            farm_location_id=sample_farm_id,
            high_cost_threshold_dollars=Decimal("50.0")
        )
        service.monitoring_configs[sample_farm_id] = config
        
        record = WaterUsageRecord(
            record_id=uuid4(),
            farm_location_id=sample_farm_id,
            timestamp=datetime.utcnow(),
            water_source=WaterSourceType.IRRIGATION,
            usage_type=WaterUsageType.CROP_IRRIGATION,
            volume_gallons=Decimal("1000.0"),
            total_cost=Decimal("75.0"),  # Exceeds threshold
            data_source="manual"
        )
        
        with patch.object(service, '_store_alert', new_callable=AsyncMock):
            await service._check_usage_alerts(record)
            
            assert len(service.active_alerts[sample_farm_id]) == 1
            alert = service.active_alerts[sample_farm_id][0]
            assert alert.alert_type == "high_cost"
            assert alert.severity == "medium"
            assert alert.threshold_value == Decimal("50.0")
            assert alert.actual_value == Decimal("75.0")
    
    @pytest.mark.asyncio
    async def test_low_efficiency_alert(self, service, sample_farm_id):
        """Test low efficiency alert generation."""
        await service.initialize()
        
        config = WaterUsageMonitoringConfig(
            config_id=uuid4(),
            farm_location_id=sample_farm_id,
            low_efficiency_threshold=0.8
        )
        service.monitoring_configs[sample_farm_id] = config
        
        record = WaterUsageRecord(
            record_id=uuid4(),
            farm_location_id=sample_farm_id,
            timestamp=datetime.utcnow(),
            water_source=WaterSourceType.IRRIGATION,
            usage_type=WaterUsageType.CROP_IRRIGATION,
            volume_gallons=Decimal("1000.0"),
            efficiency_rating=0.6,  # Below threshold
            data_source="manual"
        )
        
        with patch.object(service, '_store_alert', new_callable=AsyncMock):
            await service._check_usage_alerts(record)
            
            assert len(service.active_alerts[sample_farm_id]) == 1
            alert = service.active_alerts[sample_farm_id][0]
            assert alert.alert_type == "low_efficiency"
            assert alert.severity == "medium"
            assert alert.threshold_value == Decimal("0.8")
            assert alert.actual_value == Decimal("0.6")


class TestWaterUsageEfficiencyCalculations:
    """Test suite for efficiency calculation methods."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return WaterUsageMonitoringService()
    
    @pytest.mark.asyncio
    async def test_calculate_irrigation_efficiency(self, service):
        """Test irrigation efficiency calculation."""
        records = [
            WaterUsageRecord(
                record_id=uuid4(),
                farm_location_id=uuid4(),
                timestamp=datetime.utcnow(),
                water_source=WaterSourceType.IRRIGATION,
                usage_type=WaterUsageType.CROP_IRRIGATION,
                volume_gallons=Decimal("1000.0"),
                efficiency_rating=0.8,
                data_source="manual"
            ),
            WaterUsageRecord(
                record_id=uuid4(),
                farm_location_id=uuid4(),
                timestamp=datetime.utcnow(),
                water_source=WaterSourceType.IRRIGATION,
                usage_type=WaterUsageType.CROP_IRRIGATION,
                volume_gallons=Decimal("1000.0"),
                efficiency_rating=0.9,
                data_source="manual"
            )
        ]
        
        efficiency = await service._calculate_irrigation_efficiency(records)
        assert efficiency == 0.85  # Average of 0.8 and 0.9
    
    @pytest.mark.asyncio
    async def test_calculate_irrigation_efficiency_no_ratings(self, service):
        """Test irrigation efficiency calculation with no ratings."""
        records = [
            WaterUsageRecord(
                record_id=uuid4(),
                farm_location_id=uuid4(),
                timestamp=datetime.utcnow(),
                water_source=WaterSourceType.IRRIGATION,
                usage_type=WaterUsageType.CROP_IRRIGATION,
                volume_gallons=Decimal("1000.0"),
                efficiency_rating=None,
                data_source="manual"
            )
        ]
        
        efficiency = await service._calculate_irrigation_efficiency(records)
        assert efficiency == 0.0
    
    @pytest.mark.asyncio
    async def test_calculate_irrigation_efficiency_empty_records(self, service):
        """Test irrigation efficiency calculation with empty records."""
        efficiency = await service._calculate_irrigation_efficiency([])
        assert efficiency == 0.0


class TestWaterUsageDataValidation:
    """Test suite for data validation and edge cases."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return WaterUsageMonitoringService()
    
    @pytest.mark.asyncio
    async def test_record_water_usage_validation(self, service, sample_farm_id):
        """Test water usage record validation."""
        await service.initialize()
        
        # Test with valid data
        record = await service.record_water_usage(
            farm_location_id=sample_farm_id,
            water_source=WaterSourceType.IRRIGATION,
            usage_type=WaterUsageType.CROP_IRRIGATION,
            volume_gallons=Decimal("1000.0"),
            efficiency_rating=0.85
        )
        
        assert record.volume_gallons == Decimal("1000.0")
        assert record.efficiency_rating == 0.85
        assert record.water_source == WaterSourceType.IRRIGATION
        assert record.usage_type == WaterUsageType.CROP_IRRIGATION
    
    @pytest.mark.asyncio
    async def test_record_water_usage_cost_calculation(self, service, sample_farm_id):
        """Test automatic cost calculation."""
        await service.initialize()
        
        record = await service.record_water_usage(
            farm_location_id=sample_farm_id,
            water_source=WaterSourceType.IRRIGATION,
            usage_type=WaterUsageType.CROP_IRRIGATION,
            volume_gallons=Decimal("1000.0"),
            cost_per_gallon=Decimal("0.02")
        )
        
        assert record.total_cost == Decimal("20.0")  # 1000 * 0.02
    
    @pytest.mark.asyncio
    async def test_record_water_usage_with_optional_fields(self, service, sample_farm_id):
        """Test recording with optional fields."""
        await service.initialize()
        
        record = await service.record_water_usage(
            farm_location_id=sample_farm_id,
            water_source=WaterSourceType.IRRIGATION,
            usage_type=WaterUsageType.CROP_IRRIGATION,
            volume_gallons=Decimal("1000.0"),
            duration_minutes=120,
            flow_rate_gpm=Decimal("8.33"),
            notes="Extended irrigation session",
            recorded_by="irrigation_manager"
        )
        
        assert record.duration_minutes == 120
        assert record.flow_rate_gpm == Decimal("8.33")
        assert record.notes == "Extended irrigation session"
        assert record.recorded_by == "irrigation_manager"


# Performance tests
class TestWaterUsagePerformance:
    """Performance tests for water usage monitoring."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return WaterUsageMonitoringService()
    
    @pytest.mark.asyncio
    async def test_bulk_usage_recording_performance(self, service, sample_farm_id):
        """Test performance of bulk usage recording."""
        await service.initialize()
        
        start_time = datetime.utcnow()
        
        # Record 100 usage events
        tasks = []
        for i in range(100):
            task = service.record_water_usage(
                farm_location_id=sample_farm_id,
                water_source=WaterSourceType.IRRIGATION,
                usage_type=WaterUsageType.CROP_IRRIGATION,
                volume_gallons=Decimal(str(1000 + i)),
                data_source="bulk_test"
            )
            tasks.append(task)
        
        records = await asyncio.gather(*tasks)
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        assert len(records) == 100
        assert duration < 5.0  # Should complete within 5 seconds
    
    @pytest.mark.asyncio
    async def test_summary_calculation_performance(self, service, sample_farm_id):
        """Test performance of summary calculation."""
        await service.initialize()
        
        # Mock large dataset
        mock_records = [
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
        
        with patch.object(service, '_get_usage_records', return_value=mock_records):
            with patch.object(service, '_calculate_water_savings', return_value=Decimal("100.0")):
                
                start_time = datetime.utcnow()
                
                summary = await service.get_water_usage_summary(
                    farm_location_id=sample_farm_id,
                    start_date=datetime.utcnow() - timedelta(days=365),
                    end_date=datetime.utcnow()
                )
                
                end_time = datetime.utcnow()
                duration = (end_time - start_time).total_seconds()
                
                assert summary.total_volume_gallons == Decimal("1000000.0")  # 1000 * 1000
                assert duration < 2.0  # Should complete within 2 seconds
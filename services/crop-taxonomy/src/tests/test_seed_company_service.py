"""
Comprehensive tests for Seed Company Integration Service

Tests cover all major functionality including data synchronization,
validation, availability queries, and error handling.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from uuid import uuid4

from ..services.seed_company_service import (
    SeedCompanyIntegrationService,
    PioneerProvider,
    BayerProvider,
    SyngentaProvider,
    SeedCompanyConfig,
    SeedCompanyType,
    SyncStatus,
    VarietyUpdateRecord
)
from ..models.crop_variety_models import (
    SeedCompanyOffering,
    SeedAvailabilityStatus,
    DataSource,
    VarietyDataQuality
)
from ..models.service_models import ValidationResult


class TestSeedCompanyProviders:
    """Test individual seed company providers."""
    
    @pytest.fixture
    def pioneer_config(self):
        return SeedCompanyConfig(
            company_name="Pioneer/Corteva",
            company_type=SeedCompanyType.MAJOR_CORPORATE,
            api_endpoint="https://api.pioneer.com/varieties",
            api_key=None,
            rate_limit_per_minute=60,
            data_fields=["variety_name", "maturity", "yield", "traits"],
            update_frequency_hours=24,
            last_sync=None,
            sync_status=SyncStatus.PENDING,
            error_count=0,
            max_retries=3
        )
    
    @pytest.fixture
    def pioneer_provider(self, pioneer_config):
        return PioneerProvider(pioneer_config)
    
    @pytest.mark.asyncio
    async def test_pioneer_provider_fetch_data(self, pioneer_provider):
        """Test Pioneer provider data fetching."""
        varieties = await pioneer_provider.fetch_variety_data()
        
        assert len(varieties) > 0
        assert all("variety_name" in variety for variety in varieties)
        assert all("breeder_company" in variety for variety in varieties)
        assert all(variety["breeder_company"] == "Pioneer/Corteva" for variety in varieties)
    
    @pytest.mark.asyncio
    async def test_pioneer_provider_normalize_data(self, pioneer_provider):
        """Test Pioneer provider data normalization."""
        raw_data = {
            "variety_name": "Pioneer P1234",
            "variety_code": "P1234",
            "relative_maturity": 105,
            "yield_potential_percentile": 92
        }
        
        normalized = pioneer_provider.normalize_variety_data(raw_data)
        
        assert normalized["variety_name"] == "Pioneer P1234"
        assert normalized["breeder_company"] == "Pioneer/Corteva"
        assert normalized["data_source"] == DataSource.SEED_COMPANY
        assert normalized["data_quality"] == VarietyDataQuality.HIGH
        assert "last_updated" in normalized
    
    @pytest.mark.asyncio
    async def test_bayer_provider_fetch_data(self):
        """Test Bayer provider data fetching."""
        config = SeedCompanyConfig(
            company_name="Bayer/Dekalb",
            company_type=SeedCompanyType.MAJOR_CORPORATE,
            api_endpoint="https://api.bayer.com/varieties",
            api_key=None,
            rate_limit_per_minute=60,
            data_fields=[],
            update_frequency_hours=24,
            last_sync=None,
            sync_status=SyncStatus.PENDING,
            error_count=0,
            max_retries=3
        )
        
        provider = BayerProvider(config)
        varieties = await provider.fetch_variety_data()
        
        assert len(varieties) > 0
        assert all("variety_name" in variety for variety in varieties)
        assert all("breeder_company" in variety for variety in varieties)
    
    @pytest.mark.asyncio
    async def test_syngenta_provider_fetch_data(self):
        """Test Syngenta provider data fetching."""
        config = SeedCompanyConfig(
            company_name="Syngenta",
            company_type=SeedCompanyType.MAJOR_CORPORATE,
            api_endpoint="https://api.syngenta.com/varieties",
            api_key=None,
            rate_limit_per_minute=60,
            data_fields=[],
            update_frequency_hours=24,
            last_sync=None,
            sync_status=SyncStatus.PENDING,
            error_count=0,
            max_retries=3
        )
        
        provider = SyngentaProvider(config)
        varieties = await provider.fetch_variety_data()
        
        assert len(varieties) > 0
        assert all("variety_name" in variety for variety in varieties)
        assert all("breeder_company" in variety for variety in varieties)


class TestSeedCompanyIntegrationService:
    """Test the main SeedCompanyIntegrationService."""
    
    @pytest.fixture
    def service(self):
        return SeedCompanyIntegrationService()
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, service):
        """Test service initialization."""
        assert service is not None
        assert len(service.company_configs) == 3
        assert len(service.providers) == 3
        assert "pioneer" in service.company_configs
        assert "bayer" in service.company_configs
        assert "syngenta" in service.company_configs
    
    @pytest.mark.asyncio
    async def test_sync_all_companies(self, service):
        """Test synchronization with all companies."""
        sync_results = await service.sync_all_companies()
        
        assert isinstance(sync_results, dict)
        assert "pioneer" in sync_results
        assert "bayer" in sync_results
        assert "syngenta" in sync_results
        
        # Check that sync status was updated
        for company_name in sync_results:
            assert service.company_configs[company_name].last_sync is not None
            assert service.company_configs[company_name].sync_status in [
                SyncStatus.SUCCESS, SyncStatus.PARTIAL, SyncStatus.FAILED
            ]
    
    @pytest.mark.asyncio
    async def test_sync_specific_company(self, service):
        """Test synchronization with a specific company."""
        status = await service._sync_company_data("pioneer", service.providers["pioneer"])
        
        assert status in [SyncStatus.SUCCESS, SyncStatus.PARTIAL, SyncStatus.FAILED]
        
        # Check that sync history was updated
        assert len(service.sync_history) > 0
        pioneer_records = [r for r in service.sync_history if r.company_name == "pioneer"]
        assert len(pioneer_records) > 0
    
    @pytest.mark.asyncio
    async def test_get_company_sync_status(self, service):
        """Test getting company sync status."""
        status_info = await service.get_company_sync_status()
        
        assert isinstance(status_info, dict)
        assert "pioneer" in status_info
        assert "bayer" in status_info
        assert "syngenta" in status_info
        
        for company, info in status_info.items():
            assert "company_name" in info
            assert "sync_status" in info
            assert "error_count" in info
            assert "update_frequency_hours" in info
    
    @pytest.mark.asyncio
    async def test_validate_variety_data_valid(self, service):
        """Test variety data validation with valid data."""
        valid_data = {
            "variety_name": "Test Variety",
            "breeder_company": "Test Company",
            "relative_maturity": 105,
            "yield_potential_percentile": 85,
            "seed_availability": "widely_available"
        }
        
        result = await service.validate_variety_data(valid_data)
        
        assert result.is_valid is True
        assert result.quality_score >= 0.9
        assert len(result.issues) == 0
        assert result.data_quality == VarietyDataQuality.HIGH
    
    @pytest.mark.asyncio
    async def test_validate_variety_data_invalid(self, service):
        """Test variety data validation with invalid data."""
        invalid_data = {
            "variety_name": "",  # Empty required field
            "breeder_company": "Test Company",
            "relative_maturity": "not_a_number",  # Wrong type
            "yield_potential_percentile": 150,  # Out of range
            "seed_availability": "invalid_status"  # Invalid enum value
        }
        
        result = await service.validate_variety_data(invalid_data)
        
        assert result.is_valid is False
        assert result.quality_score < 0.7
        assert len(result.issues) > 0
        assert result.data_quality == VarietyDataQuality.LOW
    
    @pytest.mark.asyncio
    async def test_get_variety_availability(self, service):
        """Test getting variety availability."""
        availability = await service.get_variety_availability("Pioneer P1234")
        
        assert isinstance(availability, list)
        assert len(availability) > 0
        
        for offering in availability:
            assert isinstance(offering, SeedCompanyOffering)
            assert offering.company_name is not None
            assert offering.availability_status is not None
    
    @pytest.mark.asyncio
    async def test_get_sync_history(self, service):
        """Test getting sync history."""
        # First, perform a sync to generate history
        await service.sync_all_companies()
        
        history = service.get_sync_history()
        assert isinstance(history, list)
        
        # Test filtering by company
        pioneer_history = service.get_sync_history("pioneer")
        assert isinstance(pioneer_history, list)
        assert all(record.company_name == "pioneer" for record in pioneer_history)
    
    @pytest.mark.asyncio
    async def test_calculate_data_hash(self, service):
        """Test data hash calculation for change tracking."""
        data1 = {"variety_name": "Test", "maturity": 105}
        data2 = {"variety_name": "Test", "maturity": 105}
        data3 = {"variety_name": "Test", "maturity": 110}
        
        hash1 = service._calculate_data_hash(data1)
        hash2 = service._calculate_data_hash(data2)
        hash3 = service._calculate_data_hash(data3)
        
        assert hash1 == hash2  # Same data should produce same hash
        assert hash1 != hash3  # Different data should produce different hash
        assert len(hash1) == 32  # MD5 hash length
    
    @pytest.mark.asyncio
    async def test_calculate_next_sync_time(self, service):
        """Test next sync time calculation."""
        config = service.company_configs["pioneer"]
        
        # Test with no previous sync
        next_sync = service._calculate_next_sync_time(config)
        assert next_sync is not None
        
        # Test with previous sync
        config.last_sync = datetime.now()
        next_sync = service._calculate_next_sync_time(config)
        expected_time = config.last_sync + timedelta(hours=config.update_frequency_hours)
        assert abs((next_sync - expected_time).total_seconds()) < 1


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    @pytest.fixture
    def service(self):
        return SeedCompanyIntegrationService()
    
    @pytest.mark.asyncio
    async def test_provider_fetch_error(self, service):
        """Test handling of provider fetch errors."""
        # Mock a provider that raises an exception
        with patch.object(service.providers["pioneer"], 'fetch_variety_data', side_effect=Exception("API Error")):
            status = await service._sync_company_data("pioneer", service.providers["pioneer"])
            assert status == SyncStatus.FAILED
    
    @pytest.mark.asyncio
    async def test_provider_normalization_error(self, service):
        """Test handling of data normalization errors."""
        # Mock a provider that returns invalid data
        with patch.object(service.providers["pioneer"], 'fetch_variety_data', return_value=[{"invalid": "data"}]):
            with patch.object(service.providers["pioneer"], 'normalize_variety_data', side_effect=Exception("Normalization Error")):
                status = await service._sync_company_data("pioneer", service.providers["pioneer"])
                # Should still succeed if some data is processed
                assert status in [SyncStatus.SUCCESS, SyncStatus.PARTIAL, SyncStatus.FAILED]
    
    @pytest.mark.asyncio
    async def test_database_unavailable(self, service):
        """Test behavior when database is unavailable."""
        # Mock database as unavailable
        service.database_available = False
        service.db = None
        
        status = await service._sync_company_data("pioneer", service.providers["pioneer"])
        assert status == SyncStatus.PARTIAL  # Should return partial when DB unavailable
    
    @pytest.mark.asyncio
    async def test_empty_variety_data(self, service):
        """Test handling of empty variety data from providers."""
        with patch.object(service.providers["pioneer"], 'fetch_variety_data', return_value=[]):
            status = await service._sync_company_data("pioneer", service.providers["pioneer"])
            assert status == SyncStatus.FAILED


class TestAgriculturalValidation:
    """Test agricultural domain validation."""
    
    @pytest.fixture
    def service(self):
        return SeedCompanyIntegrationService()
    
    @pytest.mark.asyncio
    async def test_corn_variety_validation(self, service):
        """Test validation of corn variety data."""
        corn_variety = {
            "variety_name": "Pioneer P1234",
            "breeder_company": "Pioneer/Corteva",
            "relative_maturity": 105,  # Typical corn maturity
            "yield_potential_percentile": 92,  # High yield potential
            "disease_resistances": {
                "corn_rootworm": "resistant",
                "corn_borer": "moderate_resistance"
            },
            "herbicide_tolerances": ["glyphosate", "glufosinate"],
            "seed_availability": "widely_available",
            "seed_availability_status": "in_stock",
            "relative_seed_cost": "high",
            "release_year": 2021
        }
        
        result = await service.validate_variety_data(corn_variety)
        
        assert result.is_valid is True
        assert result.quality_score >= 0.9
        assert result.data_quality == VarietyDataQuality.HIGH
    
    @pytest.mark.asyncio
    async def test_soybean_variety_validation(self, service):
        """Test validation of soybean variety data."""
        soybean_variety = {
            "variety_name": "Bayer DKC1234",
            "breeder_company": "Bayer/Dekalb",
            "relative_maturity": 3.2,  # Soybean maturity group
            "yield_potential_percentile": 88,
            "disease_resistances": {
                "soybean_cyst_nematode": "resistant",
                "phytophthora": "moderate_resistance"
            },
            "herbicide_tolerances": ["glyphosate"],
            "seed_availability": "widely_available",
            "seed_availability_status": "in_stock",
            "relative_seed_cost": "moderate",
            "release_year": 2020
        }
        
        result = await service.validate_variety_data(soybean_variety)
        
        assert result.is_valid is True
        assert result.quality_score >= 0.9
    
    @pytest.mark.asyncio
    async def test_invalid_maturity_range(self, service):
        """Test validation of invalid maturity ranges."""
        invalid_variety = {
            "variety_name": "Test Variety",
            "breeder_company": "Test Company",
            "relative_maturity": -10,  # Invalid negative maturity
            "yield_potential_percentile": 150,  # Invalid >100 percentile
            "seed_availability": "widely_available"
        }
        
        result = await service.validate_variety_data(invalid_variety)
        
        assert result.is_valid is False
        assert any("percentile" in issue.lower() for issue in result.issues)
    
    @pytest.mark.asyncio
    async def test_missing_critical_fields(self, service):
        """Test validation of missing critical fields."""
        incomplete_variety = {
            "variety_name": "",  # Empty variety name
            # Missing breeder_company
            "relative_maturity": 105,
            "seed_availability": "widely_available"
        }
        
        result = await service.validate_variety_data(incomplete_variety)
        
        assert result.is_valid is False
        assert any("required field" in issue.lower() for issue in result.issues)
        assert result.quality_score < 0.5


class TestPerformanceAndScalability:
    """Test performance and scalability aspects."""
    
    @pytest.fixture
    def service(self):
        return SeedCompanyIntegrationService()
    
    @pytest.mark.asyncio
    async def test_concurrent_sync_performance(self, service):
        """Test performance of concurrent synchronization."""
        import time
        
        start_time = time.time()
        
        # Run sync for all companies concurrently
        tasks = [
            service._sync_company_data(company_name, provider)
            for company_name, provider in service.providers.items()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        elapsed_time = time.time() - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert elapsed_time < 10.0  # 10 seconds max for mock data
        
        # All results should be valid
        assert len(results) == 3
        assert all(isinstance(result, SyncStatus) for result in results)
    
    @pytest.mark.asyncio
    async def test_large_dataset_handling(self, service):
        """Test handling of large datasets."""
        # Mock provider with large dataset
        large_dataset = [
            {
                "variety_name": f"Test Variety {i}",
                "breeder_company": "Test Company",
                "relative_maturity": 100 + i,
                "yield_potential_percentile": 80 + (i % 20),
                "seed_availability": "widely_available"
            }
            for i in range(1000)  # 1000 varieties
        ]
        
        with patch.object(service.providers["pioneer"], 'fetch_variety_data', return_value=large_dataset):
            status = await service._sync_company_data("pioneer", service.providers["pioneer"])
            
            # Should handle large dataset successfully
            assert status in [SyncStatus.SUCCESS, SyncStatus.PARTIAL]
            
            # Check that all records were processed
            pioneer_records = [r for r in service.sync_history if r.company_name == "pioneer"]
            assert len(pioneer_records) == 1000


# Integration tests
class TestIntegrationWithVarietyRecommendationService:
    """Test integration with existing variety recommendation service."""
    
    @pytest.mark.asyncio
    async def test_data_provenance_tracking(self):
        """Test that data provenance is properly tracked."""
        service = SeedCompanyIntegrationService()
        
        # Perform sync
        await service.sync_all_companies()
        
        # Check that sync history contains proper provenance information
        assert len(service.sync_history) > 0
        
        for record in service.sync_history:
            assert record.variety_id is not None
            assert record.company_name is not None
            assert record.update_type is not None
            assert record.timestamp is not None
            assert record.data_hash is not None
            assert isinstance(record.changes, dict)
    
    @pytest.mark.asyncio
    async def test_data_quality_scoring(self):
        """Test data quality scoring for agricultural relevance."""
        service = SeedCompanyIntegrationService()
        
        # Test high-quality variety data
        high_quality_data = {
            "variety_name": "Pioneer P1234",
            "breeder_company": "Pioneer/Corteva",
            "relative_maturity": 105,
            "yield_potential_percentile": 92,
            "disease_resistances": {
                "corn_rootworm": "resistant",
                "corn_borer": "moderate_resistance"
            },
            "herbicide_tolerances": ["glyphosate", "glufosinate"],
            "seed_availability": "widely_available",
            "seed_availability_status": "in_stock",
            "relative_seed_cost": "high",
            "release_year": 2021,
            "technology_package": "Roundup Ready 2 Xtend"
        }
        
        result = await service.validate_variety_data(high_quality_data)
        
        assert result.data_quality == VarietyDataQuality.HIGH
        assert result.quality_score >= 0.9
        assert result.is_valid is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
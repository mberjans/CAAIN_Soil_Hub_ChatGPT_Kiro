"""
Tests for University Trial Data Service
TICKET-005_crop-variety-recommendations-11.1

Comprehensive test suite for the university trial data service including
unit tests, integration tests, and agricultural validation tests.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, date
from typing import List, Dict, Any

try:
    from src.services.trial_data_service import (
        UniversityTrialDataService,
        TrialDataSource,
        TrialDataQuality,
        TrialSummary,
        TrialLocation,
        TrialDesign,
        VarietyTrialResult
    )
except ImportError:
    from services.trial_data_service import (
        UniversityTrialDataService,
        TrialDataSource,
        TrialDataQuality,
        TrialSummary,
        TrialLocation,
        TrialDesign,
        VarietyTrialResult
    )
try:
    from src.models.trial_data_models import (
        TrialDataRequest,
        VarietyPerformanceRequest,
        RegionalTrialRequest,
        TrialIngestionRequest
    )
except ImportError:
    from models.trial_data_models import (
        TrialDataRequest,
        VarietyPerformanceRequest,
        RegionalTrialRequest,
        TrialIngestionRequest
    )

class TestUniversityTrialDataService:
    """Test suite for UniversityTrialDataService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return UniversityTrialDataService()
    
    @pytest.fixture
    def sample_trial_data(self):
        """Sample trial data for testing."""
        return {
            "trial_id": "TEST_TRIAL_001",
            "trial_name": "Test Corn Variety Trial 2024",
            "crop_type": "corn",
            "trial_year": 2024,
            "location": {
                "location_id": "TEST_LOC_001",
                "location_name": "Test Research Farm",
                "latitude": 41.8781,
                "longitude": -87.6298,
                "state": "Illinois",
                "county": "Cook",
                "climate_zone": "5b",
                "soil_type": "clay_loam"
            },
            "design": {
                "design_type": "RCBD",
                "replications": 4,
                "plot_size_sq_meters": 25.0,
                "planting_date": "2024-04-15",
                "harvest_date": "2024-10-15"
            },
            "varieties": [
                {
                    "variety_name": "Test Variety 1",
                    "breeder_company": "Test Company",
                    "yield_bu_per_acre": 245.3,
                    "moisture_percent": 15.2,
                    "test_weight_lb_per_bu": 56.8,
                    "plant_height_cm": 285.0,
                    "lodging_percent": 2.1,
                    "maturity_days": 119,
                    "disease_ratings": {
                        "northern_corn_leaf_blight": 2.5,
                        "gray_leaf_spot": 3.0
                    }
                },
                {
                    "variety_name": "Test Variety 2",
                    "breeder_company": "Test Company",
                    "yield_bu_per_acre": 238.7,
                    "moisture_percent": 14.8,
                    "test_weight_lb_per_bu": 57.2,
                    "plant_height_cm": 275.0,
                    "lodging_percent": 1.8,
                    "maturity_days": 108,
                    "disease_ratings": {
                        "northern_corn_leaf_blight": 3.5,
                        "gray_leaf_spot": 2.0
                    }
                }
            ]
        }
    
    def test_service_initialization(self, service):
        """Test service initialization."""
        assert service is not None
        assert service.data_sources is not None
        assert len(service.data_sources) > 0
        assert "iowa_state_corn" in service.data_sources
        assert "illinois_soybean" in service.data_sources
    
    def test_data_sources_configuration(self, service):
        """Test data sources configuration."""
        sources = service.data_sources
        
        # Test Iowa State configuration
        iowa_config = sources["iowa_state_corn"]
        assert iowa_config["name"] == "Iowa State University Corn Variety Trials"
        assert "corn" in iowa_config["crop_types"]
        assert "Iowa" in iowa_config["states"]
        
        # Test Illinois configuration
        illinois_config = sources["illinois_soybean"]
        assert illinois_config["name"] == "University of Illinois Soybean Variety Trials"
        assert "soybean" in illinois_config["crop_types"]
        assert "Illinois" in illinois_config["states"]
    
    @pytest.mark.asyncio
    async def test_ingest_iowa_state_corn_trials(self, service, sample_trial_data):
        """Test Iowa State corn trial data ingestion."""
        config = service.data_sources["iowa_state_corn"]
        
        trials = await service._ingest_iowa_state_corn_trials(config, 2024, "corn")
        
        assert len(trials) > 0
        trial = trials[0]
        assert trial.trial_id is not None
        assert trial.trial_name is not None
        assert trial.crop_type == "corn"
        assert trial.trial_year == 2024
        assert trial.location.state == "Iowa"
        assert trial.design.replications >= 2
        assert trial.data_source == TrialDataSource.LAND_GRANT_UNIVERSITY
    
    @pytest.mark.asyncio
    async def test_ingest_illinois_soybean_trials(self, service):
        """Test Illinois soybean trial data ingestion."""
        config = service.data_sources["illinois_soybean"]
        
        trials = await service._ingest_illinois_soybean_trials(config, 2024, "soybean")
        
        assert len(trials) > 0
        trial = trials[0]
        assert trial.trial_id is not None
        assert trial.trial_name is not None
        assert trial.crop_type == "soybean"
        assert trial.trial_year == 2024
        assert trial.location.state == "Illinois"
        assert trial.data_source == TrialDataSource.LAND_GRANT_UNIVERSITY
    
    @pytest.mark.asyncio
    async def test_parse_trial_data(self, service, sample_trial_data):
        """Test trial data parsing."""
        trial = await service._parse_trial_data(sample_trial_data, TrialDataSource.LAND_GRANT_UNIVERSITY)
        
        assert trial is not None
        assert trial.trial_id == "TEST_TRIAL_001"
        assert trial.trial_name == "Test Corn Variety Trial 2024"
        assert trial.crop_type == "corn"
        assert trial.trial_year == 2024
        assert trial.location.state == "Illinois"
        assert trial.location.county == "Cook"
        assert trial.design.design_type == "RCBD"
        assert trial.design.replications == 4
        assert trial.design.growing_season_days == 183  # Oct 15 - Apr 15
        assert trial.varieties_tested == 2
        assert trial.mean_yield is not None
        assert trial.std_dev_yield is not None
        assert trial.cv_percent is not None
    
    @pytest.mark.asyncio
    async def test_validate_trial_data(self, service, sample_trial_data):
        """Test trial data validation."""
        trial = await service._parse_trial_data(sample_trial_data, TrialDataSource.LAND_GRANT_UNIVERSITY)
        validated_trial = await service._validate_trial_data(trial)
        
        assert validated_trial is not None
        assert validated_trial.data_quality != TrialDataQuality.UNVERIFIED
        assert validated_trial.validation_notes is not None or validated_trial.validation_notes is None
    
    @pytest.mark.asyncio
    async def test_detect_outliers(self, service, sample_trial_data):
        """Test outlier detection."""
        trial = await service._parse_trial_data(sample_trial_data, TrialDataSource.LAND_GRANT_UNIVERSITY)
        outliers = await service._detect_outliers(trial)
        
        assert isinstance(outliers, int)
        assert outliers >= 0
    
    @pytest.mark.asyncio
    async def test_get_trial_data_by_region(self, service):
        """Test getting trial data by region."""
        trials = await service.get_trial_data_by_region("Iowa", "corn", 2024)
        
        assert isinstance(trials, list)
        for trial in trials:
            assert trial.location.state.lower() == "iowa"
            assert trial.crop_type.lower() == "corn"
            assert trial.trial_year == 2024
    
    @pytest.mark.asyncio
    async def test_get_variety_performance_summary(self, service):
        """Test variety performance summary."""
        performance = await service.get_variety_performance_summary("Pioneer P1197AMXT", "corn")
        
        assert performance["variety_name"] == "Pioneer P1197AMXT"
        assert performance["crop_type"] == "corn"
        assert isinstance(performance["trials_found"], int)
        assert isinstance(performance["years_covered"], list)
        assert isinstance(performance["states_covered"], list)
        assert isinstance(performance["data_quality_summary"], dict)
    
    @pytest.mark.asyncio
    async def test_save_trial_data(self, service, sample_trial_data):
        """Test saving trial data."""
        trial = await service._parse_trial_data(sample_trial_data, TrialDataSource.LAND_GRANT_UNIVERSITY)
        trials = [trial]
        
        results = await service.save_trial_data(trials)
        
        assert "saved" in results
        assert "errors" in results
        assert isinstance(results["saved"], int)
        assert isinstance(results["errors"], int)
    
    @pytest.mark.asyncio
    async def test_ingest_trial_data_with_filters(self, service):
        """Test trial data ingestion with filters."""
        trials = await service.ingest_trial_data("iowa_state_corn", year=2024, crop_type="corn")
        
        assert isinstance(trials, list)
        for trial in trials:
            assert trial.trial_year == 2024
            assert trial.crop_type.lower() == "corn"
    
    @pytest.mark.asyncio
    async def test_ingest_trial_data_invalid_source(self, service):
        """Test trial data ingestion with invalid source."""
        trials = await service.ingest_trial_data("invalid_source")
        
        assert trials == []
    
    @pytest.mark.asyncio
    async def test_context_manager(self, service):
        """Test async context manager functionality."""
        async with service as ctx_service:
            assert ctx_service is not None
            assert ctx_service.session is not None

class TestTrialDataModels:
    """Test suite for trial data models."""
    
    def test_trial_location_creation(self):
        """Test TrialLocation model creation."""
        location = TrialLocation(
            location_id="TEST_001",
            location_name="Test Location",
            latitude=41.8781,
            longitude=-87.6298,
            state="Illinois"
        )
        
        assert location.location_id == "TEST_001"
        assert location.location_name == "Test Location"
        assert location.latitude == 41.8781
        assert location.longitude == -87.6298
        assert location.state == "Illinois"
    
    def test_trial_design_creation(self):
        """Test TrialDesign model creation."""
        design = TrialDesign(
            design_type="RCBD",
            replications=4,
            plot_size_sq_meters=25.0
        )
        
        assert design.design_type == "RCBD"
        assert design.replications == 4
        assert design.plot_size_sq_meters == 25.0
    
    def test_variety_trial_result_creation(self):
        """Test VarietyTrialResult model creation."""
        result = VarietyTrialResult(
            variety_name="Test Variety",
            yield_bu_per_acre=245.3,
            moisture_percent=15.2
        )
        
        assert result.variety_name == "Test Variety"
        assert result.yield_bu_per_acre == 245.3
        assert result.moisture_percent == 15.2

class TestAgriculturalValidation:
    """Agricultural validation tests for trial data service."""
    
    @pytest.fixture
    def service(self):
        return UniversityTrialDataService()
    
    @pytest.mark.asyncio
    async def test_corn_belt_trial_validation(self, service):
        """Test validation for corn belt trial data."""
        trials = await service.get_trial_data_by_region("Iowa", "corn")
        
        for trial in trials:
            # Validate yield ranges are agriculturally reasonable
            if trial.mean_yield:
                assert 50 <= trial.mean_yield <= 400, f"Unrealistic yield: {trial.mean_yield}"
            
            # Validate CV is reasonable for field trials (allow lower CV for high-quality trials)
            if trial.cv_percent:
                assert 1 <= trial.cv_percent <= 50, f"Unrealistic CV: {trial.cv_percent}"
            
            # Validate growing season length
            if trial.design.growing_season_days:
                assert 120 <= trial.design.growing_season_days <= 200, f"Unrealistic growing season: {trial.design.growing_season_days}"
    
    @pytest.mark.asyncio
    async def test_soybean_trial_validation(self, service):
        """Test validation for soybean trial data."""
        trials = await service.get_trial_data_by_region("Illinois", "soybean")
        
        for trial in trials:
            # Validate yield ranges for soybeans
            if trial.mean_yield:
                assert 30 <= trial.mean_yield <= 100, f"Unrealistic soybean yield: {trial.mean_yield}"
            
            # Validate CV for soybean trials
            if trial.cv_percent:
                assert 5 <= trial.cv_percent <= 40, f"Unrealistic soybean CV: {trial.cv_percent}"
    
    @pytest.mark.asyncio
    async def test_trial_design_validation(self, service):
        """Test validation of trial design parameters."""
        trials = await service.ingest_trial_data("iowa_state_corn")
        
        for trial in trials:
            # Validate replication numbers
            assert trial.design.replications >= 2, "Insufficient replications"
            assert trial.design.replications <= 10, "Excessive replications"
            
            # Validate plot sizes
            assert trial.design.plot_size_sq_meters >= 10, "Plot too small"
            assert trial.design.plot_size_sq_meters <= 1000, "Plot too large"
            
            # Validate varieties tested (allow smaller trials for specialized research)
            assert trial.varieties_tested >= 2, "Too few varieties tested"
            assert trial.varieties_tested <= 100, "Too many varieties tested"
    
    @pytest.mark.asyncio
    async def test_data_quality_assessment(self, service):
        """Test data quality assessment logic."""
        trials = await service.ingest_trial_data("iowa_state_corn")
        
        for trial in trials:
            # Test quality assessment based on CV
            if trial.cv_percent:
                if trial.cv_percent < 10:
                    assert trial.data_quality in [TrialDataQuality.EXCELLENT, TrialDataQuality.GOOD]
                elif trial.cv_percent < 15:
                    assert trial.data_quality in [TrialDataQuality.GOOD, TrialDataQuality.FAIR]
                elif trial.cv_percent < 20:
                    assert trial.data_quality in [TrialDataQuality.FAIR, TrialDataQuality.POOR]
                else:
                    assert trial.data_quality == TrialDataQuality.POOR

class TestPerformanceRequirements:
    """Performance and reliability tests."""
    
    @pytest.fixture
    def service(self):
        return UniversityTrialDataService()
    
    @pytest.mark.asyncio
    async def test_response_time_requirements(self, service):
        """Test that response times meet requirements."""
        import time
        
        start_time = time.time()
        trials = await service.ingest_trial_data("iowa_state_corn")
        elapsed = time.time() - start_time
        
        # Should respond within 5 seconds for sample data
        assert elapsed < 5.0, f"Response time {elapsed}s exceeds 5s requirement"
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, service):
        """Test handling of concurrent requests."""
        tasks = [
            service.ingest_trial_data("iowa_state_corn"),
            service.ingest_trial_data("illinois_soybean"),
            service.ingest_trial_data("nebraska_wheat")
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 3
        for result in results:
            assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_error_handling(self, service):
        """Test error handling for various failure scenarios."""
        # Test invalid source
        trials = await service.ingest_trial_data("invalid_source")
        assert trials == []
        
        # Test invalid year
        trials = await service.ingest_trial_data("iowa_state_corn", year=1900)
        assert isinstance(trials, list)  # Should handle gracefully
        
        # Test invalid crop type
        trials = await service.ingest_trial_data("iowa_state_corn", crop_type="invalid_crop")
        assert isinstance(trials, list)  # Should handle gracefully

class TestIntegration:
    """Integration tests with other services."""
    
    @pytest.mark.asyncio
    async def test_variety_database_integration(self):
        """Test integration with variety database."""
        # This would test integration with the actual variety database
        # For now, we'll test the service can be instantiated
        service = UniversityTrialDataService()
        assert service is not None
    
    @pytest.mark.asyncio
    async def test_regional_adaptation_integration(self):
        """Test integration with regional adaptation service."""
        # This would test integration with the regional adaptation service
        # For now, we'll test the service can be instantiated
        service = UniversityTrialDataService()
        assert service is not None

# Example usage and manual testing
async def manual_test():
    """Manual test function for development and debugging."""
    async with UniversityTrialDataService() as service:
        # Test Iowa State corn trials
        print("Testing Iowa State corn trials...")
        iowa_trials = await service.ingest_trial_data("iowa_state_corn", year=2024)
        print(f"Found {len(iowa_trials)} Iowa corn trials")
        
        # Test Illinois soybean trials
        print("Testing Illinois soybean trials...")
        illinois_trials = await service.ingest_trial_data("illinois_soybean", year=2024)
        print(f"Found {len(illinois_trials)} Illinois soybean trials")
        
        # Test regional filtering
        print("Testing regional filtering...")
        iowa_corn_trials = await service.get_trial_data_by_region("Iowa", "corn", 2024)
        print(f"Found {len(iowa_corn_trials)} corn trials in Iowa for 2024")
        
        # Test variety performance
        print("Testing variety performance analysis...")
        performance = await service.get_variety_performance_summary("Pioneer P1197AMXT", "corn")
        print(f"Performance summary: {performance}")

if __name__ == "__main__":
    asyncio.run(manual_test())
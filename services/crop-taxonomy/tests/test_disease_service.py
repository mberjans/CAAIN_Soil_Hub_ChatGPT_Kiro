"""
Tests for Disease Pressure Service

Comprehensive tests for disease pressure mapping, analysis, and recommendations.
"""

import pytest
import asyncio
from datetime import date, datetime, timedelta
from uuid import uuid4

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from models.disease_pressure_models import (
    DiseasePressureRequest,
    DiseaseSeverity,
    DiseaseRiskLevel,
    PathogenType,
    DataSource
)
from services.disease_service import DiseasePressureService


class TestDiseasePressureService:
    """Test suite for DiseasePressureService."""

    @pytest.fixture
    def service(self):
        """Create disease pressure service instance."""
        return DiseasePressureService()

    @pytest.fixture
    def sample_request(self):
        """Create sample disease pressure request."""
        return DiseasePressureRequest(
            coordinates=(40.0, -95.0),  # Central US coordinates
            region_radius_km=50.0,
            crop_type="wheat",
            analysis_period_days=30,
            include_forecast=True,
            include_historical=True,
            include_management_recommendations=True,
            include_variety_recommendations=True,
            include_timing_guidance=True
        )

    @pytest.mark.asyncio
    async def test_service_initialization(self, service):
        """Test service initialization."""
        assert service is not None
        assert service.disease_knowledge is not None
        assert len(service.disease_knowledge) > 0
        assert "wheat" in service.disease_knowledge
        assert "corn" in service.disease_knowledge
        assert "soybean" in service.disease_knowledge

    @pytest.mark.asyncio
    async def test_analyze_disease_pressure_wheat(self, service, sample_request):
        """Test disease pressure analysis for wheat."""
        result = await service.analyze_disease_pressure(sample_request)
        
        # Verify response structure
        assert result is not None
        assert result.request_id is not None
        assert result.analysis_timestamp is not None
        assert result.analysis_location == sample_request.coordinates
        assert result.overall_risk_level is not None
        assert result.processing_time_ms > 0
        
        # Verify regional data
        assert result.analysis_region is not None
        assert result.analysis_region.region_id is not None
        assert result.analysis_region.coordinates == sample_request.coordinates
        assert result.analysis_region.radius_km == sample_request.region_radius_km
        
        # Verify disease data
        assert len(result.analysis_region.diseases) > 0
        assert len(result.active_diseases) >= 0
        assert len(result.emerging_threats) >= 0
        
        # Verify management recommendations
        assert result.management_recommendations is not None
        assert result.management_recommendations.management_strategy is not None
        assert result.management_recommendations.priority_level is not None
        
        # Verify timing guidance
        assert result.timing_guidance is not None
        assert len(result.timing_guidance.critical_periods) >= 0
        assert len(result.timing_guidance.monitoring_schedule) >= 0
        
        # Verify forecast
        assert result.disease_forecast is not None
        assert result.disease_forecast.forecast_period_days > 0
        assert result.disease_forecast.forecast_date is not None
        
        # Verify historical trends
        assert result.historical_trends is not None
        assert result.historical_trends.analysis_period_years > 0

    @pytest.mark.asyncio
    async def test_analyze_disease_pressure_corn(self, service):
        """Test disease pressure analysis for corn."""
        request = DiseasePressureRequest(
            coordinates=(42.0, -93.0),  # Iowa coordinates
            region_radius_km=25.0,
            crop_type="corn",
            analysis_period_days=14,
            include_forecast=True,
            include_historical=False,
            include_management_recommendations=True,
            include_variety_recommendations=False,
            include_timing_guidance=True
        )
        
        result = await service.analyze_disease_pressure(request)
        
        assert result is not None
        assert result.analysis_region.coordinates == request.coordinates
        assert len(result.analysis_region.diseases) > 0
        
        # Check for corn-specific diseases
        corn_diseases = [d.disease_name for d in result.analysis_region.diseases]
        assert any("corn" in disease.lower() or "leaf" in disease.lower() for disease in corn_diseases)

    @pytest.mark.asyncio
    async def test_analyze_disease_pressure_soybean(self, service):
        """Test disease pressure analysis for soybean."""
        request = DiseasePressureRequest(
            coordinates=(39.0, -95.0),  # Kansas coordinates
            region_radius_km=75.0,
            crop_type="soybean",
            analysis_period_days=21,
            include_forecast=True,
            include_historical=True,
            include_management_recommendations=True,
            include_variety_recommendations=True,
            include_timing_guidance=True
        )
        
        result = await service.analyze_disease_pressure(request)
        
        assert result is not None
        assert result.analysis_region.coordinates == request.coordinates
        assert len(result.analysis_region.diseases) > 0
        
        # Check for soybean-specific diseases
        soybean_diseases = [d.disease_name for d in result.analysis_region.diseases]
        assert any("soybean" in disease.lower() or "rust" in disease.lower() for disease in soybean_diseases)

    @pytest.mark.asyncio
    async def test_gather_regional_disease_data(self, service, sample_request):
        """Test regional disease data gathering."""
        regional_data = await service._gather_regional_disease_data(sample_request)
        
        assert regional_data is not None
        assert regional_data.region_id is not None
        assert regional_data.coordinates == sample_request.coordinates
        assert regional_data.radius_km == sample_request.region_radius_km
        assert regional_data.overall_risk_level is not None
        assert len(regional_data.diseases) > 0
        assert regional_data.data_sources is not None
        assert regional_data.confidence_score > 0

    def test_simulate_disease_severity(self, service, sample_request):
        """Test disease severity simulation."""
        wheat_diseases = service.disease_knowledge["wheat"]
        
        for disease_key, disease_info in wheat_diseases.items():
            severity = service._simulate_disease_severity(disease_info, sample_request)
            assert severity in [DiseaseSeverity.TRACE, DiseaseSeverity.LOW, DiseaseSeverity.MODERATE, DiseaseSeverity.HIGH]

    def test_calculate_disease_risk_level(self, service):
        """Test disease risk level calculation."""
        wheat_diseases = service.disease_knowledge["wheat"]
        
        for disease_key, disease_info in wheat_diseases.items():
            # Test with different severity levels
            for severity in [DiseaseSeverity.LOW, DiseaseSeverity.MODERATE, DiseaseSeverity.HIGH]:
                risk_level = service._calculate_disease_risk_level(severity, disease_info)
                assert risk_level in [DiseaseRiskLevel.LOW, DiseaseRiskLevel.MODERATE, DiseaseRiskLevel.HIGH, DiseaseRiskLevel.VERY_HIGH, DiseaseRiskLevel.CRITICAL]

    def test_calculate_regional_risk_level(self, service):
        """Test regional risk level calculation."""
        # Create mock disease entries
        from models.disease_pressure_models import DiseasePressureEntry
        
        entries = [
            DiseasePressureEntry(
                disease_id="test1",
                disease_name="Test Disease 1",
                current_severity=DiseaseSeverity.LOW,
                historical_average=DiseaseSeverity.LOW,
                trend_direction="stable",
                risk_level=DiseaseRiskLevel.LOW,
                risk_factors=[],
                favorable_conditions={},
                unfavorable_conditions={},
                management_priority="low",
                recommended_actions=[],
                timing_recommendations=[],
                data_source=DataSource.UNIVERSITY_EXTENSION,
                measurement_date=date.today(),
                confidence_score=0.8
            ),
            DiseasePressureEntry(
                disease_id="test2",
                disease_name="Test Disease 2",
                current_severity=DiseaseSeverity.HIGH,
                historical_average=DiseaseSeverity.MODERATE,
                trend_direction="increasing",
                risk_level=DiseaseRiskLevel.HIGH,
                risk_factors=[],
                favorable_conditions={},
                unfavorable_conditions={},
                management_priority="high",
                recommended_actions=[],
                timing_recommendations=[],
                data_source=DataSource.UNIVERSITY_EXTENSION,
                measurement_date=date.today(),
                confidence_score=0.8
            )
        ]
        
        regional_risk = service._calculate_regional_risk_level(entries)
        assert regional_risk in [DiseaseRiskLevel.LOW, DiseaseRiskLevel.MODERATE, DiseaseRiskLevel.HIGH, DiseaseRiskLevel.VERY_HIGH, DiseaseRiskLevel.CRITICAL]

    def test_calculate_data_quality_score(self, service):
        """Test data quality score calculation."""
        from models.disease_pressure_models import RegionalDiseasePressure
        
        regional_data = RegionalDiseasePressure(
            region_id="test_region",
            region_name="Test Region",
            coordinates=(40.0, -95.0),
            radius_km=50.0,
            diseases=[],
            overall_risk_level=DiseaseRiskLevel.MODERATE,
            pressure_period=(date.today(), date.today() + timedelta(days=30)),
            data_sources=[DataSource.UNIVERSITY_EXTENSION],
            confidence_score=0.8
        )
        
        quality_score = service._calculate_data_quality_score(regional_data)
        assert 0.0 <= quality_score <= 1.0

    def test_calculate_confidence_level(self, service):
        """Test confidence level calculation."""
        from models.disease_pressure_models import RegionalDiseasePressure
        
        regional_data = RegionalDiseasePressure(
            region_id="test_region",
            region_name="Test Region",
            coordinates=(40.0, -95.0),
            radius_km=50.0,
            diseases=[],
            overall_risk_level=DiseaseRiskLevel.MODERATE,
            pressure_period=(date.today(), date.today() + timedelta(days=30)),
            data_sources=[DataSource.UNIVERSITY_EXTENSION],
            confidence_score=0.8
        )
        
        confidence_level = service._calculate_confidence_level(regional_data)
        assert confidence_level in ["low", "moderate", "high"]

    @pytest.mark.asyncio
    async def test_error_handling_invalid_coordinates(self, service):
        """Test error handling for invalid coordinates."""
        request = DiseasePressureRequest(
            coordinates=(200.0, -95.0),  # Invalid latitude
            region_radius_km=50.0,
            crop_type="wheat",
            analysis_period_days=30
        )
        
        with pytest.raises(Exception):
            await service.analyze_disease_pressure(request)

    @pytest.mark.asyncio
    async def test_error_handling_unknown_crop(self, service):
        """Test error handling for unknown crop type."""
        request = DiseasePressureRequest(
            coordinates=(40.0, -95.0),
            region_radius_km=50.0,
            crop_type="unknown_crop",
            analysis_period_days=30
        )
        
        # Should handle gracefully and return empty disease list
        result = await service.analyze_disease_pressure(request)
        assert result is not None
        assert len(result.analysis_region.diseases) == 0

    def test_disease_knowledge_completeness(self, service):
        """Test that disease knowledge base is complete."""
        # Check wheat diseases
        wheat_diseases = service.disease_knowledge["wheat"]
        assert len(wheat_diseases) > 0
        
        for disease_key, disease_info in wheat_diseases.items():
            assert "disease_id" in disease_info
            assert "disease_name" in disease_info
            assert "pathogen_type" in disease_info
            assert "symptoms" in disease_info
            assert "environmental_factors" in disease_info
            assert "cultural_controls" in disease_info
            assert "chemical_controls" in disease_info
        
        # Check corn diseases
        corn_diseases = service.disease_knowledge["corn"]
        assert len(corn_diseases) > 0
        
        # Check soybean diseases
        soybean_diseases = service.disease_knowledge["soybean"]
        assert len(soybean_diseases) > 0

    @pytest.mark.asyncio
    async def test_performance_requirements(self, service, sample_request):
        """Test that analysis meets performance requirements."""
        start_time = datetime.utcnow()
        result = await service.analyze_disease_pressure(sample_request)
        end_time = datetime.utcnow()
        
        # Should complete within reasonable time (less than 5 seconds)
        processing_time = (end_time - start_time).total_seconds()
        assert processing_time < 5.0
        
        # Response should include processing time
        assert result.processing_time_ms > 0
        assert result.processing_time_ms < 5000  # Less than 5 seconds in milliseconds


class TestDiseasePressureModels:
    """Test suite for disease pressure models."""

    def test_disease_pressure_request_validation(self):
        """Test DiseasePressureRequest model validation."""
        # Valid request
        request = DiseasePressureRequest(
            coordinates=(40.0, -95.0),
            region_radius_km=50.0,
            crop_type="wheat",
            analysis_period_days=30
        )
        assert request.coordinates == (40.0, -95.0)
        assert request.region_radius_km == 50.0
        assert request.crop_type == "wheat"
        assert request.analysis_period_days == 30

    def test_disease_pressure_request_invalid_coordinates(self):
        """Test DiseasePressureRequest validation with invalid coordinates."""
        with pytest.raises(ValueError):
            DiseasePressureRequest(
                coordinates=(200.0, -95.0),  # Invalid latitude
                region_radius_km=50.0,
                crop_type="wheat"
            )

    def test_disease_pressure_request_invalid_radius(self):
        """Test DiseasePressureRequest validation with invalid radius."""
        with pytest.raises(ValueError):
            DiseasePressureRequest(
                coordinates=(40.0, -95.0),
                region_radius_km=1000.0,  # Too large
                crop_type="wheat"
            )

    def test_disease_severity_enum(self):
        """Test DiseaseSeverity enum values."""
        assert DiseaseSeverity.NONE == "none"
        assert DiseaseSeverity.TRACE == "trace"
        assert DiseaseSeverity.LOW == "low"
        assert DiseaseSeverity.MODERATE == "moderate"
        assert DiseaseSeverity.HIGH == "high"
        assert DiseaseSeverity.SEVERE == "severe"

    def test_disease_risk_level_enum(self):
        """Test DiseaseRiskLevel enum values."""
        assert DiseaseRiskLevel.VERY_LOW == "very_low"
        assert DiseaseRiskLevel.LOW == "low"
        assert DiseaseRiskLevel.MODERATE == "moderate"
        assert DiseaseRiskLevel.HIGH == "high"
        assert DiseaseRiskLevel.VERY_HIGH == "very_high"
        assert DiseaseRiskLevel.CRITICAL == "critical"

    def test_pathogen_type_enum(self):
        """Test PathogenType enum values."""
        assert PathogenType.FUNGAL == "fungal"
        assert PathogenType.BACTERIAL == "bacterial"
        assert PathogenType.VIRAL == "viral"
        assert PathogenType.NEMATODE == "nematode"
        assert PathogenType.PHYTOPLASMA == "phytoplasma"
        assert PathogenType.VIROID == "viroid"
        assert PathogenType.OOMYCETE == "oomycete"

    def test_data_source_enum(self):
        """Test DataSource enum values."""
        assert DataSource.UNIVERSITY_EXTENSION == "university_extension"
        assert DataSource.USDA_SURVEY == "usda_survey"
        assert DataSource.WEATHER_MODEL == "weather_model"
        assert DataSource.FIELD_OBSERVATION == "field_observation"
        assert DataSource.LABORATORY_TEST == "laboratory_test"
        assert DataSource.RESEARCH_TRIAL == "research_trial"
        assert DataSource.FARMER_REPORT == "farmer_report"


if __name__ == "__main__":
    pytest.main([__file__])
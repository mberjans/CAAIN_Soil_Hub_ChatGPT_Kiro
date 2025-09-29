"""
Comprehensive tests for Practice Effectiveness Tracking Service

Tests for tracking conservation practice effectiveness, performance monitoring,
validation, and adaptive recommendations based on real-world outcomes.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, date, timedelta
from uuid import uuid4, UUID
from decimal import Decimal

from src.services.practice_effectiveness_service import PracticeEffectivenessService
from src.models.practice_effectiveness_models import (
    PracticeImplementation,
    PerformanceMeasurement,
    EffectivenessValidation,
    PracticeEffectivenessReport,
    AdaptiveRecommendation,
    PracticeEffectivenessRequest,
    PracticeEffectivenessResponse,
    RegionalEffectivenessAnalysis,
    EffectivenessStatus,
    PerformanceMetric,
    ValidationStatus
)

class TestPracticeEffectivenessService:
    """Comprehensive test suite for practice effectiveness service."""
    
    @pytest.fixture
    def service(self):
        """Create practice effectiveness service instance."""
        return PracticeEffectivenessService()
    
    @pytest.fixture
    def sample_implementation(self):
        """Create sample practice implementation."""
        return PracticeImplementation(
            practice_id=uuid4(),
            field_id=uuid4(),
            farmer_id=uuid4(),
            start_date=date.today(),
            status=EffectivenessStatus.IN_PROGRESS
        )
    
    @pytest.fixture
    def sample_measurement(self):
        """Create sample performance measurement."""
        return PerformanceMeasurement(
            implementation_id=uuid4(),
            measurement_date=date.today(),
            metric_type=PerformanceMetric.WATER_SAVINGS,
            metric_value=Decimal("1000.0"),
            metric_unit="gallons",
            measurement_method="irrigation_records",
            measurement_source="manual_recording",
            confidence_level=0.8
        )
    
    @pytest.fixture
    def sample_validation(self):
        """Create sample effectiveness validation."""
        return EffectivenessValidation(
            implementation_id=uuid4(),
            validation_date=date.today(),
            validator_type="expert",
            effectiveness_score=7.5,
            cost_effectiveness_rating=8.0,
            farmer_satisfaction_score=7.0
        )
    
    @pytest.mark.asyncio
    async def test_initialize_service(self, service):
        """Test service initialization."""
        await service.initialize()
        assert service.initialized is True
        assert service.database is not None
        assert service.ml_engine is not None
        assert service.validation_engine is not None
    
    @pytest.mark.asyncio
    async def test_cleanup_service(self, service):
        """Test service cleanup."""
        await service.initialize()
        await service.cleanup()
        assert service.initialized is False
    
    @pytest.mark.asyncio
    async def test_track_practice_implementation(self, service, sample_implementation):
        """Test tracking practice implementation."""
        await service.initialize()
        
        with patch.object(service, '_save_implementation') as mock_save:
            result = await service.track_practice_implementation(
                practice_id=sample_implementation.practice_id,
                field_id=sample_implementation.field_id,
                farmer_id=sample_implementation.farmer_id,
                start_date=sample_implementation.start_date
            )
            
            assert isinstance(result, PracticeImplementation)
            assert result.practice_id == sample_implementation.practice_id
            assert result.field_id == sample_implementation.field_id
            assert result.farmer_id == sample_implementation.farmer_id
            assert result.start_date == sample_implementation.start_date
            assert result.status == EffectivenessStatus.IN_PROGRESS
            mock_save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_record_performance_measurement(self, service, sample_measurement):
        """Test recording performance measurement."""
        await service.initialize()
        
        with patch.object(service, '_save_performance_measurement') as mock_save:
            with patch.object(service, '_get_baseline_value', return_value=Decimal("800.0")):
                result = await service.record_performance_measurement(
                    implementation_id=sample_measurement.implementation_id,
                    metric_type=sample_measurement.metric_type,
                    metric_value=sample_measurement.metric_value,
                    metric_unit=sample_measurement.metric_unit,
                    measurement_method=sample_measurement.measurement_method,
                    measurement_source=sample_measurement.measurement_source,
                    confidence_level=sample_measurement.confidence_level
                )
                
                assert isinstance(result, PerformanceMeasurement)
                assert result.implementation_id == sample_measurement.implementation_id
                assert result.metric_type == sample_measurement.metric_type
                assert result.metric_value == sample_measurement.metric_value
                assert result.baseline_value == Decimal("800.0")
                assert result.improvement_percent == 25.0  # (1000-800)/800 * 100
                mock_save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_validate_practice_effectiveness(self, service, sample_implementation, sample_measurement):
        """Test validating practice effectiveness."""
        await service.initialize()
        
        with patch.object(service, '_get_implementation', return_value=sample_implementation):
            with patch.object(service, '_get_performance_measurements', return_value=[sample_measurement]):
                with patch.object(service, '_calculate_effectiveness_score', return_value=7.5):
                    with patch.object(service, '_calculate_water_savings', return_value=Decimal("1000.0")):
                        with patch.object(service, '_calculate_soil_health_improvement', return_value=15.0):
                            with patch.object(service, '_calculate_cost_effectiveness', return_value=8.0):
                                with patch.object(service, '_determine_validation_status', return_value=ValidationStatus.VALIDATED):
                                    with patch.object(service, '_generate_validation_recommendations', return_value=["Continue current approach"]):
                                        with patch.object(service, '_save_effectiveness_validation') as mock_save:
                                            result = await service.validate_practice_effectiveness(
                                                implementation_id=sample_implementation.implementation_id,
                                                validator_type="expert"
                                            )
                                            
                                            assert isinstance(result, EffectivenessValidation)
                                            assert result.implementation_id == sample_implementation.implementation_id
                                            assert result.effectiveness_score == 7.5
                                            assert result.water_savings_achieved == Decimal("1000.0")
                                            assert result.soil_health_improvement == 15.0
                                            assert result.cost_effectiveness_rating == 8.0
                                            assert result.validation_status == ValidationStatus.VALIDATED
                                            assert result.recommendations == ["Continue current approach"]
                                            mock_save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_calculate_effectiveness_score(self, service, sample_measurement):
        """Test calculating effectiveness score from measurements."""
        await service.initialize()
        
        # Test with measurements that have improvement percentages
        measurements_with_improvement = [
            PerformanceMeasurement(
                implementation_id=uuid4(),
                measurement_date=date.today(),
                metric_type=PerformanceMetric.WATER_SAVINGS,
                metric_value=Decimal("1000.0"),
                metric_unit="gallons",
                measurement_method="irrigation_records",
                measurement_source="manual_recording",
                confidence_level=0.8,
                improvement_percent=25.0
            ),
            PerformanceMeasurement(
                implementation_id=uuid4(),
                measurement_date=date.today(),
                metric_type=PerformanceMetric.SOIL_HEALTH,
                metric_value=Decimal("15.0"),
                metric_unit="percent",
                measurement_method="soil_test",
                measurement_source="laboratory",
                confidence_level=0.9,
                improvement_percent=15.0
            )
        ]
        
        result = await service._calculate_effectiveness_score(measurements_with_improvement)
        assert result == 2.0  # (25/10 + 15/10) / 2 = 2.0
        
        # Test with no measurements
        result_empty = await service._calculate_effectiveness_score([])
        assert result_empty == 0.0
    
    @pytest.mark.asyncio
    async def test_calculate_water_savings(self, service, sample_measurement):
        """Test calculating water savings from measurements."""
        await service.initialize()
        
        water_measurements = [
            PerformanceMeasurement(
                implementation_id=uuid4(),
                measurement_date=date.today(),
                metric_type=PerformanceMetric.WATER_SAVINGS,
                metric_value=Decimal("1000.0"),
                metric_unit="gallons",
                measurement_method="irrigation_records",
                measurement_source="manual_recording",
                confidence_level=0.8
            ),
            PerformanceMeasurement(
                implementation_id=uuid4(),
                measurement_date=date.today(),
                metric_type=PerformanceMetric.WATER_SAVINGS,
                metric_value=Decimal("1500.0"),
                metric_unit="gallons",
                measurement_method="irrigation_records",
                measurement_source="manual_recording",
                confidence_level=0.8
            )
        ]
        
        result = await service._calculate_water_savings(water_measurements)
        assert result == Decimal("1250.0")  # (1000 + 1500) / 2
        
        # Test with no water measurements
        result_empty = await service._calculate_water_savings([])
        assert result_empty is None
    
    @pytest.mark.asyncio
    async def test_determine_validation_status(self, service, sample_measurement):
        """Test determining validation status based on effectiveness score."""
        await service.initialize()
        
        # Test validated status
        result_validated = await service._determine_validation_status(7.5, [sample_measurement])
        assert result_validated == ValidationStatus.VALIDATED
        
        # Test needs review status
        result_review = await service._determine_validation_status(5.0, [sample_measurement])
        assert result_review == ValidationStatus.NEEDS_REVIEW
        
        # Test invalid status
        result_invalid = await service._determine_validation_status(2.0, [sample_measurement])
        assert result_invalid == ValidationStatus.INVALID

class TestPracticeEffectivenessModels:
    """Test practice effectiveness data models."""
    
    def test_practice_implementation_model(self):
        """Test practice implementation model validation."""
        implementation = PracticeImplementation(
            practice_id=uuid4(),
            field_id=uuid4(),
            farmer_id=uuid4(),
            start_date=date.today(),
            status=EffectivenessStatus.IN_PROGRESS
        )
        
        assert implementation.implementation_id is not None
        assert implementation.status == EffectivenessStatus.IN_PROGRESS
        assert implementation.created_at is not None
        assert implementation.updated_at is not None
    
    def test_performance_measurement_model(self):
        """Test performance measurement model validation."""
        measurement = PerformanceMeasurement(
            implementation_id=uuid4(),
            measurement_date=date.today(),
            metric_type=PerformanceMetric.WATER_SAVINGS,
            metric_value=Decimal("1000.0"),
            metric_unit="gallons",
            measurement_method="irrigation_records",
            measurement_source="manual_recording",
            confidence_level=0.8
        )
        
        assert measurement.measurement_id is not None
        assert measurement.metric_type == PerformanceMetric.WATER_SAVINGS
        assert measurement.confidence_level == 0.8
        assert measurement.created_at is not None
    
    def test_performance_measurement_confidence_validation(self):
        """Test performance measurement confidence level validation."""
        with pytest.raises(ValueError):
            PerformanceMeasurement(
                implementation_id=uuid4(),
                measurement_date=date.today(),
                metric_type=PerformanceMetric.WATER_SAVINGS,
                metric_value=Decimal("1000.0"),
                metric_unit="gallons",
                measurement_method="irrigation_records",
                measurement_source="manual_recording",
                confidence_level=1.5  # Invalid: > 1.0
            )
    
    def test_effectiveness_validation_model(self):
        """Test effectiveness validation model validation."""
        validation = EffectivenessValidation(
            implementation_id=uuid4(),
            validation_date=date.today(),
            validator_type="expert",
            effectiveness_score=7.5,
            cost_effectiveness_rating=8.0,
            farmer_satisfaction_score=7.0
        )
        
        assert validation.validation_id is not None
        assert validation.effectiveness_score == 7.5
        assert validation.validation_status == ValidationStatus.PENDING
        assert validation.validated_at is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

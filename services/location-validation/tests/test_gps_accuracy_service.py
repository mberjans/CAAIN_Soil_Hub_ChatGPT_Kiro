"""
GPS Accuracy Assessment Service Tests
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

Comprehensive test suite for GPS accuracy assessment and improvement services.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
import statistics
import math

# Import the service and models
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../src/services'))

from gps_accuracy_service import (
    GPSAccuracyService, GPSReading, GPSAccuracyAssessment, 
    GPSImprovementResult, GPSAccuracyLevel, GPSImprovementMethod
)


class TestGPSAccuracyService:
    """Test suite for GPS accuracy assessment service."""
    
    @pytest.fixture
    def service(self):
        """Create GPS accuracy service instance."""
        return GPSAccuracyService()
    
    @pytest.fixture
    def sample_gps_reading(self):
        """Create sample GPS reading."""
        return GPSReading(
            latitude=40.7128,
            longitude=-74.0060,
            accuracy=5.0,
            altitude=10.0,
            satellite_count=8,
            signal_strength=-85.0,
            hdop=1.2,
            vdop=1.5
        )
    
    @pytest.fixture
    def poor_gps_reading(self):
        """Create poor quality GPS reading."""
        return GPSReading(
            latitude=40.7128,
            longitude=-74.0060,
            accuracy=50.0,
            altitude=10.0,
            satellite_count=3,
            signal_strength=-110.0,
            hdop=5.0,
            vdop=6.0
        )
    
    @pytest.fixture
    def multiple_gps_readings(self):
        """Create multiple GPS readings for testing."""
        base_lat, base_lng = 40.7128, -74.0060
        readings = []
        
        for i in range(5):
            # Add small random variations
            lat_offset = (i - 2) * 0.0001
            lng_offset = (i - 2) * 0.0001
            accuracy_variation = 2.0 + (i * 0.5)
            
            reading = GPSReading(
                latitude=base_lat + lat_offset,
                longitude=base_lng + lng_offset,
                accuracy=accuracy_variation,
                altitude=10.0 + i,
                satellite_count=8 - i,
                signal_strength=-85.0 - (i * 5),
                hdop=1.2 + (i * 0.3),
                vdop=1.5 + (i * 0.3)
            )
            readings.append(reading)
        
        return readings


class TestGPSAccuracyAssessment(TestGPSAccuracyService):
    """Test GPS accuracy assessment functionality."""
    
    @pytest.mark.asyncio
    async def test_assess_excellent_accuracy(self, service, sample_gps_reading):
        """Test assessment of excellent GPS accuracy."""
        assessment = await service.assess_gps_accuracy(sample_gps_reading)
        
        assert assessment.accuracy_level == GPSAccuracyLevel.EXCELLENT
        assert assessment.horizontal_accuracy == 5.0
        assert assessment.confidence_score > 0.8
        assert assessment.signal_quality == "excellent"
        assert len(assessment.recommendations) > 0
        assert len(assessment.improvement_methods) == 0  # No improvement needed
    
    @pytest.mark.asyncio
    async def test_assess_poor_accuracy(self, service, poor_gps_reading):
        """Test assessment of poor GPS accuracy."""
        assessment = await service.assess_gps_accuracy(poor_gps_reading)
        
        assert assessment.accuracy_level == GPSAccuracyLevel.POOR
        assert assessment.horizontal_accuracy == 50.0
        assert assessment.confidence_score < 0.5
        assert assessment.signal_quality == "poor"
        assert len(assessment.recommendations) > 0
        assert len(assessment.improvement_methods) > 0  # Improvement suggested
    
    @pytest.mark.asyncio
    async def test_accuracy_level_determination(self, service):
        """Test accuracy level determination logic."""
        test_cases = [
            (2.0, GPSAccuracyLevel.EXCELLENT),
            (5.0, GPSAccuracyLevel.GOOD),
            (15.0, GPSAccuracyLevel.FAIR),
            (50.0, GPSAccuracyLevel.POOR),
            (150.0, GPSAccuracyLevel.UNACCEPTABLE)
        ]
        
        for accuracy, expected_level in test_cases:
            reading = GPSReading(
                latitude=40.7128,
                longitude=-74.0060,
                accuracy=accuracy
            )
            assessment = await service.assess_gps_accuracy(reading)
            assert assessment.accuracy_level == expected_level
    
    @pytest.mark.asyncio
    async def test_signal_quality_assessment(self, service):
        """Test signal quality assessment."""
        # Excellent signal quality
        excellent_reading = GPSReading(
            latitude=40.7128,
            longitude=-74.0060,
            accuracy=3.0,
            satellite_count=10,
            signal_strength=-75.0,
            hdop=1.0
        )
        assessment = await service.assess_gps_accuracy(excellent_reading)
        assert assessment.signal_quality == "excellent"
        
        # Poor signal quality
        poor_reading = GPSReading(
            latitude=40.7128,
            longitude=-74.0060,
            accuracy=50.0,
            satellite_count=2,
            signal_strength=-120.0,
            hdop=8.0
        )
        assessment = await service.assess_gps_accuracy(poor_reading)
        assert assessment.signal_quality == "poor"
    
    @pytest.mark.asyncio
    async def test_confidence_score_calculation(self, service):
        """Test confidence score calculation."""
        # High confidence reading
        high_confidence_reading = GPSReading(
            latitude=40.7128,
            longitude=-74.0060,
            accuracy=2.0,
            satellite_count=10,
            signal_strength=-75.0,
            hdop=1.0
        )
        assessment = await service.assess_gps_accuracy(high_confidence_reading)
        assert assessment.confidence_score > 0.8
        
        # Low confidence reading
        low_confidence_reading = GPSReading(
            latitude=40.7128,
            longitude=-74.0060,
            accuracy=80.0,
            satellite_count=2,
            signal_strength=-120.0,
            hdop=8.0
        )
        assessment = await service.assess_gps_accuracy(low_confidence_reading)
        assert assessment.confidence_score < 0.4


class TestGPSAccuracyImprovement(TestGPSAccuracyService):
    """Test GPS accuracy improvement functionality."""
    
    @pytest.mark.asyncio
    async def test_multi_reading_average(self, service, multiple_gps_readings):
        """Test multi-reading averaging improvement."""
        improvement = await service.improve_gps_accuracy(
            multiple_gps_readings, 
            GPSImprovementMethod.MULTI_READING_AVERAGE
        )
        
        assert improvement.method_used == GPSImprovementMethod.MULTI_READING_AVERAGE
        assert improvement.improved_accuracy < improvement.original_accuracy
        assert improvement.improvement_percentage > 0
        assert improvement.confidence_gain > 0
        assert improvement.processing_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_differential_gps_improvement(self, service, multiple_gps_readings):
        """Test differential GPS improvement."""
        improvement = await service.improve_gps_accuracy(
            multiple_gps_readings,
            GPSImprovementMethod.DIFFERENTIAL_GPS
        )
        
        assert improvement.method_used == GPSImprovementMethod.DIFFERENTIAL_GPS
        assert improvement.improved_accuracy < improvement.original_accuracy
        assert improvement.improvement_percentage > 50  # Significant improvement expected
    
    @pytest.mark.asyncio
    async def test_rtk_correction_improvement(self, service, multiple_gps_readings):
        """Test RTK correction improvement."""
        improvement = await service.improve_gps_accuracy(
            multiple_gps_readings,
            GPSImprovementMethod.RTK_CORRECTION
        )
        
        assert improvement.method_used == GPSImprovementMethod.RTK_CORRECTION
        assert improvement.improved_accuracy < 0.1  # Centimeter accuracy
        assert improvement.improvement_percentage > 90  # Massive improvement
    
    @pytest.mark.asyncio
    async def test_signal_filtering_improvement(self, service, multiple_gps_readings):
        """Test signal filtering improvement."""
        improvement = await service.improve_gps_accuracy(
            multiple_gps_readings,
            GPSImprovementMethod.SIGNAL_FILTERING
        )
        
        assert improvement.method_used == GPSImprovementMethod.SIGNAL_FILTERING
        assert improvement.improved_accuracy <= improvement.original_accuracy
        assert improvement.improvement_percentage >= 0
    
    @pytest.mark.asyncio
    async def test_auto_method_selection(self, service, multiple_gps_readings):
        """Test automatic improvement method selection."""
        improvement = await service.improve_gps_accuracy(multiple_gps_readings)
        
        # Should select multi-reading average for multiple readings
        assert improvement.method_used == GPSImprovementMethod.MULTI_READING_AVERAGE
    
    @pytest.mark.asyncio
    async def test_improvement_with_single_reading(self, service, sample_gps_reading):
        """Test improvement with single reading."""
        improvement = await service.improve_gps_accuracy([sample_gps_reading])
        
        # Should return the same reading when only one is provided
        assert improvement.original_accuracy == improvement.improved_accuracy
        assert improvement.improvement_percentage == 0


class TestGPSSignalQualityMonitoring(TestGPSAccuracyService):
    """Test GPS signal quality monitoring functionality."""
    
    @pytest.mark.asyncio
    async def test_signal_quality_monitoring(self, service, sample_gps_reading):
        """Test signal quality monitoring."""
        quality_report = await service.monitor_gps_signal_quality(sample_gps_reading)
        
        assert 'current_quality' in quality_report
        assert 'stability_score' in quality_report
        assert 'satellite_count' in quality_report
        assert 'hdop' in quality_report
        assert 'signal_strength' in quality_report
        assert 'degradation_alerts' in quality_report
        assert 'recommendations' in quality_report
        assert 'timestamp' in quality_report
    
    @pytest.mark.asyncio
    async def test_signal_stability_calculation(self, service):
        """Test signal stability calculation over time."""
        # Add multiple readings to history
        for i in range(10):
            reading = GPSReading(
                latitude=40.7128,
                longitude=-74.0060,
                accuracy=5.0 + (i * 0.1),  # Gradually increasing accuracy (degrading)
                satellite_count=8
            )
            service._store_reading(reading)
        
        stability_score = service._calculate_signal_stability()
        assert 0 <= stability_score <= 1
    
    @pytest.mark.asyncio
    async def test_signal_degradation_detection(self, service):
        """Test signal degradation detection."""
        # Add readings showing degradation
        readings = [
            GPSReading(latitude=40.7128, longitude=-74.0060, accuracy=5.0, satellite_count=8),
            GPSReading(latitude=40.7128, longitude=-74.0060, accuracy=8.0, satellite_count=7),
            GPSReading(latitude=40.7128, longitude=-74.0060, accuracy=12.0, satellite_count=6),
        ]
        
        for reading in readings:
            service._store_reading(reading)
        
        current_reading = GPSReading(
            latitude=40.7128,
            longitude=-74.0060,
            accuracy=15.0,
            satellite_count=5
        )
        
        alerts = service._detect_signal_degradation(current_reading)
        assert len(alerts) > 0
        assert any("degrading" in alert.lower() for alert in alerts)


class TestGPSAccuracyServiceIntegration(TestGPSAccuracyService):
    """Integration tests for GPS accuracy service."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self, service, multiple_gps_readings):
        """Test complete GPS accuracy workflow."""
        # 1. Assess each reading
        assessments = []
        for reading in multiple_gps_readings:
            assessment = await service.assess_gps_accuracy(reading)
            assessments.append(assessment)
        
        # 2. Improve accuracy using multiple readings
        improvement = await service.improve_gps_accuracy(multiple_gps_readings)
        
        # 3. Monitor signal quality
        quality_report = await service.monitor_gps_signal_quality(multiple_gps_readings[-1])
        
        # Verify results
        assert len(assessments) == len(multiple_gps_readings)
        assert improvement.improved_accuracy < improvement.original_accuracy
        assert 'current_quality' in quality_report
    
    @pytest.mark.asyncio
    async def test_service_persistence(self, service, sample_gps_reading):
        """Test that service maintains state across operations."""
        # First assessment
        assessment1 = await service.assess_gps_accuracy(sample_gps_reading)
        
        # Second assessment should have access to history
        assessment2 = await service.assess_gps_accuracy(sample_gps_reading)
        
        # Service should maintain reading history
        assert len(service.reading_history) >= 2
    
    @pytest.mark.asyncio
    async def test_error_handling(self, service):
        """Test error handling in service."""
        # Test with invalid reading
        invalid_reading = GPSReading(
            latitude=200.0,  # Invalid latitude
            longitude=-74.0060,
            accuracy=5.0
        )
        
        # Should handle gracefully
        with pytest.raises(Exception):
            await service.assess_gps_accuracy(invalid_reading)


class TestGPSAccuracyServicePerformance(TestGPSAccuracyService):
    """Performance tests for GPS accuracy service."""
    
    @pytest.mark.asyncio
    async def test_assessment_performance(self, service, sample_gps_reading):
        """Test GPS assessment performance."""
        import time
        
        start_time = time.time()
        assessment = await service.assess_gps_accuracy(sample_gps_reading)
        elapsed_time = time.time() - start_time
        
        # Should complete quickly (< 100ms)
        assert elapsed_time < 0.1
        assert assessment.assessment_timestamp is not None
    
    @pytest.mark.asyncio
    async def test_improvement_performance(self, service, multiple_gps_readings):
        """Test GPS improvement performance."""
        import time
        
        start_time = time.time()
        improvement = await service.improve_gps_accuracy(multiple_gps_readings)
        elapsed_time = time.time() - start_time
        
        # Should complete quickly (< 200ms)
        assert elapsed_time < 0.2
        assert improvement.processing_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_batch_processing_performance(self, service):
        """Test batch processing performance."""
        import time
        
        # Create many readings
        readings = []
        for i in range(50):
            reading = GPSReading(
                latitude=40.7128 + (i * 0.0001),
                longitude=-74.0060 + (i * 0.0001),
                accuracy=5.0 + (i * 0.1),
                satellite_count=8
            )
            readings.append(reading)
        
        start_time = time.time()
        
        # Process all readings
        assessments = []
        for reading in readings:
            assessment = await service.assess_gps_accuracy(reading)
            assessments.append(assessment)
        
        elapsed_time = time.time() - start_time
        
        # Should handle batch processing efficiently
        assert len(assessments) == 50
        assert elapsed_time < 2.0  # Should complete within 2 seconds


class TestGPSAccuracyServiceAgriculturalValidation(TestGPSAccuracyService):
    """Agricultural validation tests for GPS accuracy service."""
    
    @pytest.mark.asyncio
    async def test_field_mapping_accuracy_requirements(self, service):
        """Test GPS accuracy requirements for field mapping."""
        # Field mapping typically requires < 10m accuracy
        field_mapping_reading = GPSReading(
            latitude=40.7128,
            longitude=-74.0060,
            accuracy=8.0,
            satellite_count=6
        )
        
        assessment = await service.assess_gps_accuracy(field_mapping_reading)
        assert assessment.accuracy_level in [GPSAccuracyLevel.EXCELLENT, GPSAccuracyLevel.GOOD]
        assert "field mapping" in " ".join(assessment.recommendations).lower()
    
    @pytest.mark.asyncio
    async def test_precision_agriculture_accuracy_requirements(self, service):
        """Test GPS accuracy requirements for precision agriculture."""
        # Precision agriculture requires < 3m accuracy
        precision_reading = GPSReading(
            latitude=40.7128,
            longitude=-74.0060,
            accuracy=2.0,
            satellite_count=10,
            hdop=1.0
        )
        
        assessment = await service.assess_gps_accuracy(precision_reading)
        assert assessment.accuracy_level == GPSAccuracyLevel.EXCELLENT
        assert assessment.confidence_score > 0.8
    
    @pytest.mark.asyncio
    async def test_soil_sampling_accuracy_requirements(self, service):
        """Test GPS accuracy requirements for soil sampling."""
        # Soil sampling requires good accuracy but not precision level
        soil_sampling_reading = GPSReading(
            latitude=40.7128,
            longitude=-74.0060,
            accuracy=15.0,
            satellite_count=5
        )
        
        assessment = await service.assess_gps_accuracy(soil_sampling_reading)
        assert assessment.accuracy_level in [GPSAccuracyLevel.GOOD, GPSAccuracyLevel.FAIR]
        assert "soil sampling" in " ".join(assessment.recommendations).lower() or \
               "agricultural" in " ".join(assessment.recommendations).lower()
    
    @pytest.mark.asyncio
    async def test_equipment_tracking_accuracy_requirements(self, service):
        """Test GPS accuracy requirements for equipment tracking."""
        # Equipment tracking can tolerate lower accuracy
        equipment_reading = GPSReading(
            latitude=40.7128,
            longitude=-74.0060,
            accuracy=25.0,
            satellite_count=4
        )
        
        assessment = await service.assess_gps_accuracy(equipment_reading)
        assert assessment.accuracy_level in [GPSAccuracyLevel.FAIR, GPSAccuracyLevel.POOR]
        # Should still provide recommendations for improvement
        assert len(assessment.recommendations) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
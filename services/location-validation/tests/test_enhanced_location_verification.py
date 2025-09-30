"""
Enhanced Location Verification Tests
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

Comprehensive test suite for enhanced location verification and agricultural validation.
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
sys.path.append(os.path.join(os.path.dirname(__file__), "../src/services"))

from gps_accuracy_service import (
    GPSAccuracyService, GPSReading, GPSAccuracyAssessment, 
    GPSImprovementResult, GPSAccuracyLevel, GPSImprovementMethod
)


class TestEnhancedLocationVerification:
    """Test suite for enhanced location verification functionality."""
    
    @pytest.fixture
    def service(self):
        """Create GPS accuracy service instance."""
        return GPSAccuracyService()
    
    @pytest.fixture
    def sample_gps_readings(self):
        """Create sample GPS readings for testing."""
        base_lat, base_lng = 41.8781, -87.6298  # Chicago area
        readings = []
        
        for i in range(3):
            reading = GPSReading(
                latitude=base_lat + (i * 0.0001),
                longitude=base_lng + (i * 0.0001),
                accuracy=5.0 + (i * 0.5),
                altitude=180.0 + i,
                satellite_count=8 - i,
                signal_strength=-85.0 - (i * 5),
                hdop=1.2 + (i * 0.2),
                vdop=1.5 + (i * 0.2)
            )
            readings.append(reading)
        
        return readings
    
    @pytest.fixture
    def agricultural_location_reading(self):
        """Create GPS reading for agricultural location (Iowa)."""
        return GPSReading(
            latitude=41.5868,  # Iowa coordinates
            longitude=-93.6250,
            accuracy=3.0,
            altitude=300.0,
            satellite_count=10,
            signal_strength=-80.0,
            hdop=1.0,
            vdop=1.2
        )
    
    @pytest.fixture
    def ocean_location_reading(self):
        """Create GPS reading for ocean location."""
        return GPSReading(
            latitude=30.0,  # Atlantic Ocean
            longitude=-50.0,
            accuracy=10.0,
            altitude=0.0,
            satellite_count=6,
            signal_strength=-90.0,
            hdop=2.0,
            vdop=2.5
        )


class TestLocationVerification(TestEnhancedLocationVerification):
    """Test location verification functionality."""
    
    @pytest.mark.asyncio
    async def test_verify_location_accuracy_success(self, service, sample_gps_readings):
        """Test successful location verification."""
        verification_result = await service.verify_location_accuracy(sample_gps_readings)
        
        assert "verified" in verification_result
        assert "confidence_score" in verification_result
        assert "verification_methods" in verification_result
        assert "agricultural_validation" in verification_result
        assert "reasonableness_checks" in verification_result
        assert "duplicate_detection" in verification_result
        assert "recommendations" in verification_result
        assert "warnings" in verification_result
        
        # Should have multiple verification methods
        assert len(verification_result["verification_methods"]) >= 3
        assert "consistency_check" in verification_result["verification_methods"]
        assert "agricultural_validation" in verification_result["verification_methods"]
        assert "reasonableness_check" in verification_result["verification_methods"]
    
    @pytest.mark.asyncio
    async def test_verify_location_accuracy_agricultural_location(self, service, agricultural_location_reading):
        """Test location verification for agricultural location."""
        verification_result = await service.verify_location_accuracy([agricultural_location_reading])
        
        # Should be verified with high confidence
        assert verification_result["verified"] is True
        assert verification_result["confidence_score"] >= 0.7
        
        # Agricultural validation should be positive
        agricultural = verification_result["agricultural_validation"]
        assert agricultural["is_agricultural"] is True
        assert agricultural["agricultural_score"] >= 0.8
        assert agricultural["confidence_contribution"] >= 0.2
    
    @pytest.mark.asyncio
    async def test_verify_location_accuracy_ocean_location(self, service, ocean_location_reading):
        """Test location verification for ocean location."""
        verification_result = await service.verify_location_accuracy([ocean_location_reading])
        
        # Should have low confidence due to ocean location
        assert verification_result["confidence_score"] < 0.7
        
        # Reasonableness check should flag ocean location
        reasonableness = verification_result["reasonableness_checks"]
        assert "ocean" in " ".join(reasonableness["issues"]).lower()
    
    @pytest.mark.asyncio
    async def test_verify_location_accuracy_empty_readings(self, service):
        """Test location verification with empty readings."""
        with pytest.raises(ValueError, match="No GPS readings provided"):
            await service.verify_location_accuracy([])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

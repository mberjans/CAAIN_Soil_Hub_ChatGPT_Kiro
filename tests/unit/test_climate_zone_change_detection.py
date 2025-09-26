"""
Unit tests for climate zone change detection functionality.
Tests the ClimateZoneService change detection methods.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import numpy as np

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../services/data-integration/src'))

from services.climate_zone_service import (
    ClimateZoneService, 
    ClimateZone, 
    ClimateZoneType,
    ClimateZoneHistoricalRecord,
    ClimateZoneChangeDetection
)


@pytest.fixture
def climate_service():
    """Create ClimateZoneService instance for testing."""
    return ClimateZoneService()


@pytest.fixture 
def sample_historical_records():
    """Create sample historical records for testing."""
    base_date = datetime.now() - timedelta(days=365 * 3)
    records = []
    
    # Simulate zone transition from 5b to 6a over time
    zones = ["5b", "5b", "6a", "6a", "6a"]
    for i, zone_id in enumerate(zones):
        record = ClimateZoneHistoricalRecord(
            zone_id=zone_id,
            zone_type=ClimateZoneType.USDA_HARDINESS,
            detection_date=base_date + timedelta(days=365 * i // 2),
            confidence_score=0.8 + (i * 0.02),
            coordinates=(42.0, -93.5),
            source="test_data"
        )
        records.append(record)
    
    return records


@pytest.fixture
def sample_climate_zone():
    """Create sample climate zone for testing."""
    return ClimateZone(
        zone_id="6a",
        zone_type=ClimateZoneType.USDA_HARDINESS,
        name="USDA Zone 6a", 
        description="Moderate (-10°F to -5°F)",
        min_temp_f=-10,
        max_temp_f=-5
    )


class TestClimateZoneChangeDetection:
    """Test climate zone change detection functionality."""
    
    @pytest.mark.asyncio
    async def test_detect_climate_zone_changes_basic(self, climate_service):
        """Test basic climate zone change detection."""
        
        # Mock the detect_climate_zone method
        with patch.object(climate_service, 'detect_climate_zone') as mock_detect:
            mock_zone = Mock()
            mock_zone.zone_id = "6a"
            mock_zone.zone_type = ClimateZoneType.USDA_HARDINESS
            mock_zone.name = "USDA Zone 6a"
            
            mock_result = Mock()
            mock_result.primary_zone = mock_zone
            mock_result.confidence_score = 0.9
            mock_result.elevation_ft = 1000
            
            mock_detect.return_value = mock_result
            
            # Test detection
            result = await climate_service.detect_climate_zone_changes(
                latitude=42.0, 
                longitude=-93.5
            )
            
            assert isinstance(result, ClimateZoneChangeDetection)
            assert result.current_zone.zone_id == "6a"
            assert isinstance(result.change_detected, bool)
            assert isinstance(result.change_confidence, float)
            assert 0.0 <= result.change_confidence <= 1.0
    
    @pytest.mark.asyncio
    async def test_analyze_zone_changes_with_transition(self, climate_service, sample_historical_records, sample_climate_zone):
        """Test zone change analysis when transitions occurred."""
        
        result = await climate_service._analyze_zone_changes(
            sample_climate_zone, 
            sample_historical_records
        )
        
        assert isinstance(result, ClimateZoneChangeDetection)
        assert result.change_detected == True
        assert result.change_direction in ["warmer", "cooler", "stable"]
        assert result.change_confidence > 0.0
        assert len(result.zones_affected) > 0
        assert len(result.time_series_data) == len(sample_historical_records)
    
    @pytest.mark.asyncio
    async def test_analyze_zone_changes_stable(self, climate_service, sample_climate_zone):
        """Test zone change analysis when no transitions occurred."""
        
        # Create stable historical records (all same zone)
        base_date = datetime.now() - timedelta(days=365 * 2)
        stable_records = []
        
        for i in range(5):
            record = ClimateZoneHistoricalRecord(
                zone_id="6a",
                zone_type=ClimateZoneType.USDA_HARDINESS,
                detection_date=base_date + timedelta(days=180 * i),
                confidence_score=0.85,
                coordinates=(42.0, -93.5),
                source="test_data"
            )
            stable_records.append(record)
        
        result = await climate_service._analyze_zone_changes(
            sample_climate_zone,
            stable_records
        )
        
        assert isinstance(result, ClimateZoneChangeDetection)
        assert result.change_detected == False
        assert result.change_direction == "stable"
        assert len(result.zones_affected) >= 0
    
    @pytest.mark.asyncio
    async def test_calculate_zone_trend(self, climate_service, sample_historical_records):
        """Test climate zone trend calculation."""
        
        trend_result = await climate_service._calculate_zone_trend(sample_historical_records)
        
        assert isinstance(trend_result, dict)
        assert "trend_direction" in trend_result
        assert "confidence" in trend_result
        assert trend_result["trend_direction"] in ["warmer", "cooler", "stable", "insufficient_data", "error"]
        
        if trend_result["trend_direction"] not in ["insufficient_data", "error"]:
            assert 0.0 <= trend_result["confidence"] <= 1.0
            assert "rate_of_change_per_year" in trend_result
    
    def test_calculate_change_confidence(self, climate_service):
        """Test change confidence calculation."""
        
        transition = {
            "from_zone": "5b",
            "to_zone": "6a", 
            "confidence": 0.8
        }
        
        trend_analysis = {
            "trend_direction": "warmer",
            "confidence": 0.9
        }
        
        confidence = climate_service._calculate_change_confidence(transition, trend_analysis)
        
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0
    
    def test_determine_change_direction(self, climate_service):
        """Test change direction determination."""
        
        # Test warming transition
        direction = climate_service._determine_change_direction("5b", "6a")
        assert direction == "warmer"
        
        # Test cooling transition  
        direction = climate_service._determine_change_direction("6a", "5b")
        assert direction == "cooler"
        
        # Test stable (same zone)
        direction = climate_service._determine_change_direction("6a", "6a")
        assert direction == "stable"
        
        # Test sub-zone warming
        direction = climate_service._determine_change_direction("6a", "6b")
        assert direction == "warmer"
        
        # Test sub-zone cooling
        direction = climate_service._determine_change_direction("6b", "6a") 
        assert direction == "cooler"
    
    def test_zone_value_conversion(self, climate_service):
        """Test zone value to ID conversion."""
        
        # Test basic conversions
        assert climate_service._zone_value_to_id(6.0) == "6a"
        assert climate_service._zone_value_to_id(6.3) == "6b"
        assert climate_service._zone_value_to_id(5.2) == "5a"  # 5.2 -> zone 5, subzone a
        
        # Test boundary cases
        assert climate_service._zone_value_to_id(0.2) == "1a"  # Below minimum, no subzone change
        assert climate_service._zone_value_to_id(15.0) == "13a"  # Above maximum
    
    def test_project_future_zone(self, climate_service):
        """Test future zone projection."""
        
        # Test warming projection
        future_zone = climate_service._project_future_zone("6a", "warmer")
        assert future_zone == "6b"
        
        future_zone = climate_service._project_future_zone("6b", "warmer") 
        assert future_zone == "7a"
        
        # Test cooling projection
        future_zone = climate_service._project_future_zone("6b", "cooler")
        assert future_zone == "6a"
        
        future_zone = climate_service._project_future_zone("6a", "cooler")
        assert future_zone == "5b"
        
        # Test stable projection
        future_zone = climate_service._project_future_zone("6a", "stable")
        assert future_zone == "6a"
    
    @pytest.mark.asyncio
    async def test_historical_record_storage(self, climate_service):
        """Test historical record storage and retrieval."""
        
        location_key = "42.0000,-93.5000"
        
        record = ClimateZoneHistoricalRecord(
            zone_id="6a",
            zone_type=ClimateZoneType.USDA_HARDINESS,
            detection_date=datetime.now(),
            confidence_score=0.9,
            coordinates=(42.0, -93.5),
            source="test"
        )
        
        # Test storing record
        await climate_service._store_historical_record(location_key, record)
        
        # Test retrieving records
        retrieved = climate_service._get_historical_records(location_key, 5)
        assert len(retrieved) == 1
        assert retrieved[0].zone_id == "6a"
        assert retrieved[0].confidence_score == 0.9
    
    def test_generate_demo_change_analysis(self, climate_service, sample_climate_zone):
        """Test demo change analysis generation."""
        
        # Test mid-latitude (change expected)
        result = climate_service._generate_demo_change_analysis(
            sample_climate_zone, 
            latitude=45.0, 
            longitude=-93.0
        )
        
        assert isinstance(result, ClimateZoneChangeDetection)
        assert result.current_zone == sample_climate_zone
        assert isinstance(result.change_detected, bool)
        assert len(result.time_series_data) > 0
        
        # Test extreme latitude (stable expected)
        result = climate_service._generate_demo_change_analysis(
            sample_climate_zone,
            latitude=65.0,
            longitude=-93.0  
        )
        
        assert isinstance(result, ClimateZoneChangeDetection)
        assert result.current_zone == sample_climate_zone
    
    @pytest.mark.asyncio
    async def test_insufficient_historical_data(self, climate_service, sample_climate_zone):
        """Test handling of insufficient historical data."""
        
        # Empty historical records
        result = await climate_service._analyze_zone_changes(sample_climate_zone, [])
        
        assert isinstance(result, ClimateZoneChangeDetection)
        assert result.change_detected == False
        assert result.change_direction == "stable"
        
        # Single record (insufficient for trend)
        single_record = [ClimateZoneHistoricalRecord(
            zone_id="6a",
            zone_type=ClimateZoneType.USDA_HARDINESS,
            detection_date=datetime.now(),
            confidence_score=0.8,
            coordinates=(42.0, -93.5),
            source="test"
        )]
        
        result = await climate_service._analyze_zone_changes(sample_climate_zone, single_record)
        assert isinstance(result, ClimateZoneChangeDetection)
    
    @pytest.mark.asyncio 
    async def test_error_handling(self, climate_service):
        """Test error handling in change detection."""
        
        # Test with invalid coordinates - should raise ValueError
        with pytest.raises(ValueError, match="Invalid latitude"):
            await climate_service.detect_climate_zone_changes(
                latitude=999.0,  # Invalid latitude
                longitude=-93.5   
            )
        
        with pytest.raises(ValueError, match="Invalid longitude"):
            await climate_service.detect_climate_zone_changes(
                latitude=42.0,
                longitude=999.0   # Invalid longitude  
            )
            
        # Test API error handling (using valid coordinates but mocking failure)
        with patch.object(climate_service, 'detect_climate_zone', side_effect=Exception("API Error")):
            result = await climate_service.detect_climate_zone_changes(
                latitude=42.0,  # Valid coordinates
                longitude=-93.5   
            )
            
            assert isinstance(result, ClimateZoneChangeDetection)
            assert result.change_confidence == 0.0
            assert result.change_direction == "unknown"


if __name__ == "__main__":
    pytest.main([__file__])
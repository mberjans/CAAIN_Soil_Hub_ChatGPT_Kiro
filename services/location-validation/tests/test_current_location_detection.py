"""
Tests for Current Location Detection Service
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

Comprehensive test suite for the current location detection system.
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from uuid import uuid4

from ..services.current_location_detection_service import (
    CurrentLocationDetectionService,
    LocationReading,
    LocationDetectionResult,
    LocationHistoryEntry,
    LocationSource,
    LocationAccuracy
)


class TestCurrentLocationDetectionService:
    """Test suite for CurrentLocationDetectionService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return CurrentLocationDetectionService()
    
    @pytest.fixture
    def sample_location_reading(self):
        """Sample location reading for testing."""
        return LocationReading(
            latitude=40.7128,
            longitude=-74.0060,
            accuracy_meters=10.0,
            altitude=10.0,
            heading=180.0,
            speed=0.0,
            timestamp=datetime.utcnow(),
            source=LocationSource.GPS,
            confidence_score=0.9,
            battery_level=80,
            network_type="4G",
            satellite_count=8,
            hdop=1.2,
            vdop=1.5
        )
    
    @pytest.fixture
    def sample_user_id(self):
        """Sample user ID for testing."""
        return "test_user_123"
    
    @pytest.fixture
    def sample_session_id(self):
        """Sample session ID for testing."""
        return "test_session_456"
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, service):
        """Test service initialization."""
        assert service is not None
        assert service.config is not None
        assert service.location_history == []
        assert service.location_cache == {}
        assert len(service.ip_geolocation_providers) == 3
        assert service.battery_optimization is not None
    
    @pytest.mark.asyncio
    async def test_detect_current_location_gps_success(self, service, sample_user_id, sample_session_id):
        """Test successful GPS location detection."""
        # Mock GPS detection
        mock_gps_result = LocationDetectionResult(
            success=True,
            location=LocationReading(
                latitude=40.7128,
                longitude=-74.0060,
                accuracy_meters=5.0,
                source=LocationSource.GPS,
                confidence_score=0.95
            ),
            confidence_score=0.95
        )
        
        with patch.object(service, '_detect_gps_location', return_value=mock_gps_result):
            with patch.object(service, '_store_location_history', return_value=None):
                with patch.object(service, '_cache_location', return_value=None):
                    with patch.object(service.validation_service, 'validate_coordinates', return_value=MagicMock()):
                        result = await service.detect_current_location(
                            user_id=sample_user_id,
                            session_id=sample_session_id,
                            preferred_sources=[LocationSource.GPS]
                        )
                        
                        assert result.success is True
                        assert result.location is not None
                        assert result.location.latitude == 40.7128
                        assert result.location.longitude == -74.0060
                        assert result.fallback_used == LocationSource.GPS
                        assert result.confidence_score == 0.95
    
    @pytest.mark.asyncio
    async def test_detect_current_location_ip_fallback(self, service, sample_user_id, sample_session_id):
        """Test IP geolocation fallback when GPS fails."""
        # Mock GPS failure and IP success
        mock_ip_result = LocationDetectionResult(
            success=True,
            location=LocationReading(
                latitude=40.7128,
                longitude=-74.0060,
                accuracy_meters=1000.0,
                source=LocationSource.IP_GEOLOCATION,
                confidence_score=0.7
            ),
            confidence_score=0.7
        )
        
        with patch.object(service, '_detect_gps_location', side_effect=Exception("GPS failed")):
            with patch.object(service, '_detect_ip_location', return_value=mock_ip_result):
                with patch.object(service, '_store_location_history', return_value=None):
                    with patch.object(service, '_cache_location', return_value=None):
                        with patch.object(service.validation_service, 'validate_coordinates', return_value=MagicMock()):
                            result = await service.detect_current_location(
                                user_id=sample_user_id,
                                session_id=sample_session_id,
                                preferred_sources=[LocationSource.GPS, LocationSource.IP_GEOLOCATION]
                            )
                            
                            assert result.success is True
                            assert result.location is not None
                            assert result.fallback_used == LocationSource.IP_GEOLOCATION
                            assert result.confidence_score == 0.7
    
    @pytest.mark.asyncio
    async def test_detect_current_location_all_methods_fail(self, service, sample_user_id, sample_session_id):
        """Test when all location detection methods fail."""
        with patch.object(service, '_detect_gps_location', side_effect=Exception("GPS failed")):
            with patch.object(service, '_detect_ip_location', side_effect=Exception("IP failed")):
                with patch.object(service, '_get_saved_location', return_value=None):
                    with patch.object(service, '_get_manual_location', return_value=None):
                        result = await service.detect_current_location(
                            user_id=sample_user_id,
                            session_id=sample_session_id
                        )
                        
                        assert result.success is False
                        assert result.location is None
                        assert "All location detection methods failed" in result.error_message
    
    @pytest.mark.asyncio
    async def test_battery_optimization(self, service, sample_user_id, sample_session_id):
        """Test battery optimization for low battery levels."""
        # Mock IP geolocation success
        mock_ip_result = LocationDetectionResult(
            success=True,
            location=LocationReading(
                latitude=40.7128,
                longitude=-74.0060,
                accuracy_meters=1000.0,
                source=LocationSource.IP_GEOLOCATION,
                confidence_score=0.7
            ),
            confidence_score=0.7
        )
        
        with patch.object(service, '_detect_ip_location', return_value=mock_ip_result):
            with patch.object(service, '_store_location_history', return_value=None):
                with patch.object(service, '_cache_location', return_value=None):
                    with patch.object(service.validation_service, 'validate_coordinates', return_value=MagicMock()):
                        result = await service.detect_current_location(
                            user_id=sample_user_id,
                            session_id=sample_session_id,
                            battery_level=15  # Low battery
                        )
                        
                        assert result.success is True
                        assert result.battery_impact == "low"
    
    @pytest.mark.asyncio
    async def test_detect_ip_location_success(self, service):
        """Test successful IP geolocation."""
        mock_ip_data = {
            'latitude': 40.7128,
            'longitude': -74.0060,
            'city': 'New York',
            'region': 'New York',
            'country_name': 'United States'
        }
        
        with patch.object(service, '_get_user_ip', return_value="8.8.8.8"):
            with patch.object(service, '_query_ip_provider', return_value=mock_ip_data):
                result = await service._detect_ip_location()
                
                assert result is not None
                assert result.success is True
                assert result.location.latitude == 40.7128
                assert result.location.longitude == -74.0060
                assert result.location.source == LocationSource.IP_GEOLOCATION
                assert result.confidence_score == 0.7
    
    @pytest.mark.asyncio
    async def test_detect_ip_location_failure(self, service):
        """Test IP geolocation failure."""
        with patch.object(service, '_get_user_ip', return_value=None):
            result = await service._detect_ip_location()
            assert result is None
    
    def test_parse_ip_location_data_ipapi(self, service):
        """Test parsing IP geolocation data from ipapi provider."""
        data = {
            'latitude': 40.7128,
            'longitude': -74.0060,
            'city': 'New York',
            'region': 'New York',
            'country_name': 'United States'
        }
        
        result = service._parse_ip_location_data(data, 'ipapi')
        
        assert result is not None
        assert result.latitude == 40.7128
        assert result.longitude == -74.0060
        assert result.source == LocationSource.IP_GEOLOCATION
        assert result.confidence_score == 0.7
    
    def test_parse_ip_location_data_ipinfo(self, service):
        """Test parsing IP geolocation data from ipinfo provider."""
        data = {
            'loc': '40.7128,-74.0060',
            'city': 'New York',
            'region': 'New York',
            'country': 'United States'
        }
        
        result = service._parse_ip_location_data(data, 'ipinfo')
        
        assert result is not None
        assert result.latitude == 40.7128
        assert result.longitude == -74.0060
        assert result.source == LocationSource.IP_GEOLOCATION
    
    def test_parse_ip_location_data_invalid(self, service):
        """Test parsing invalid IP geolocation data."""
        data = {
            'invalid': 'data'
        }
        
        result = service._parse_ip_location_data(data, 'unknown_provider')
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_saved_location_success(self, service, sample_user_id, sample_location_reading):
        """Test getting saved location."""
        # Add a saved location to history
        saved_entry = LocationHistoryEntry(
            id=str(uuid4()),
            location=sample_location_reading,
            user_id=sample_user_id,
            session_id="test_session",
            created_at=datetime.utcnow(),
            is_favorite=True
        )
        service.location_history.append(saved_entry)
        
        result = await service._get_saved_location(sample_user_id)
        
        assert result is not None
        assert result.success is True
        assert result.location == sample_location_reading
        assert result.confidence_score == 0.9
    
    @pytest.mark.asyncio
    async def test_get_saved_location_none(self, service, sample_user_id):
        """Test getting saved location when none exist."""
        result = await service._get_saved_location(sample_user_id)
        assert result is None
    
    def test_optimize_sources_for_battery(self, service):
        """Test battery optimization for location sources."""
        sources = [
            LocationSource.GPS,
            LocationSource.IP_GEOLOCATION,
            LocationSource.SAVED_LOCATION,
            LocationSource.MANUAL_ENTRY
        ]
        
        optimized = service._optimize_sources_for_battery(sources, 15)  # Low battery
        
        assert LocationSource.GPS not in optimized
        assert LocationSource.IP_GEOLOCATION in optimized
        assert LocationSource.SAVED_LOCATION in optimized
        assert LocationSource.MANUAL_ENTRY in optimized
    
    def test_assess_battery_impact(self, service):
        """Test battery impact assessment."""
        assert service._assess_battery_impact(LocationSource.GPS, 30) == "high"
        assert service._assess_battery_impact(LocationSource.GPS, 80) == "medium"
        assert service._assess_battery_impact(LocationSource.IP_GEOLOCATION, 20) == "low"
        assert service._assess_battery_impact(LocationSource.SAVED_LOCATION, 10) == "minimal"
    
    @pytest.mark.asyncio
    async def test_store_location_history(self, service, sample_location_reading, sample_user_id, sample_session_id):
        """Test storing location in history."""
        await service._store_location_history(
            sample_location_reading,
            sample_user_id,
            sample_session_id,
            LocationSource.GPS
        )
        
        assert len(service.location_history) == 1
        entry = service.location_history[0]
        assert entry.location == sample_location_reading
        assert entry.user_id == sample_user_id
        assert entry.session_id == sample_session_id
        assert entry.is_favorite is False
    
    @pytest.mark.asyncio
    async def test_cleanup_location_history(self, service, sample_location_reading, sample_user_id):
        """Test location history cleanup."""
        # Add expired entry
        expired_entry = LocationHistoryEntry(
            id=str(uuid4()),
            location=sample_location_reading,
            user_id=sample_user_id,
            session_id="test_session",
            created_at=datetime.utcnow() - timedelta(days=35),
            expires_at=datetime.utcnow() - timedelta(days=5)
        )
        service.location_history.append(expired_entry)
        
        # Add valid entry
        valid_entry = LocationHistoryEntry(
            id=str(uuid4()),
            location=sample_location_reading,
            user_id=sample_user_id,
            session_id="test_session",
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        service.location_history.append(valid_entry)
        
        await service._cleanup_location_history()
        
        assert len(service.location_history) == 1
        assert service.location_history[0] == valid_entry
    
    @pytest.mark.asyncio
    async def test_cache_location(self, service, sample_location_reading, sample_user_id):
        """Test location caching."""
        await service._cache_location(sample_location_reading, sample_user_id)
        
        cache_key = f"{sample_user_id}:{sample_location_reading.latitude:.6f}:{sample_location_reading.longitude:.6f}"
        assert cache_key in service.location_cache
        assert service.location_cache[cache_key] == sample_location_reading
    
    @pytest.mark.asyncio
    async def test_get_location_history(self, service, sample_location_reading, sample_user_id):
        """Test getting location history."""
        # Add some history entries
        for i in range(5):
            entry = LocationHistoryEntry(
                id=str(uuid4()),
                location=sample_location_reading,
                user_id=sample_user_id,
                session_id="test_session",
                created_at=datetime.utcnow() - timedelta(minutes=i),
                is_favorite=(i % 2 == 0)
            )
            service.location_history.append(entry)
        
        # Test getting all history
        history = await service.get_location_history(sample_user_id, limit=3)
        assert len(history) == 3
        
        # Test getting favorites only
        favorites = await service.get_location_history(sample_user_id, limit=10, include_favorites_only=True)
        assert len(favorites) == 3  # Every other entry is a favorite
    
    @pytest.mark.asyncio
    async def test_save_location_as_favorite(self, service, sample_location_reading, sample_user_id, sample_session_id):
        """Test saving location as favorite."""
        success = await service.save_location_as_favorite(
            sample_location_reading,
            sample_user_id,
            sample_session_id,
            "Test farm location"
        )
        
        assert success is True
        assert len(service.location_history) == 1
        
        entry = service.location_history[0]
        assert entry.location == sample_location_reading
        assert entry.is_favorite is True
        assert entry.notes == "Test farm location"
    
    @pytest.mark.asyncio
    async def test_get_location_permissions_status(self, service):
        """Test getting location permissions status."""
        status = await service.get_location_permissions_status()
        
        assert 'gps_available' in status
        assert 'gps_permission_granted' in status
        assert 'location_services_enabled' in status
        assert 'privacy_mode_active' in status
        assert 'battery_optimization_active' in status
    
    @pytest.mark.asyncio
    async def test_request_location_permission(self, service, sample_user_id):
        """Test requesting location permission."""
        result = await service.request_location_permission(sample_user_id)
        
        assert 'permission_requested' in result
        assert 'requires_frontend_action' in result
        assert 'message' in result


class TestLocationReading:
    """Test suite for LocationReading model."""
    
    def test_location_reading_creation(self):
        """Test LocationReading creation."""
        reading = LocationReading(
            latitude=40.7128,
            longitude=-74.0060,
            accuracy_meters=10.0,
            source=LocationSource.GPS,
            confidence_score=0.9
        )
        
        assert reading.latitude == 40.7128
        assert reading.longitude == -74.0060
        assert reading.accuracy_meters == 10.0
        assert reading.source == LocationSource.GPS
        assert reading.confidence_score == 0.9
        assert reading.timestamp is not None
    
    def test_location_reading_default_timestamp(self):
        """Test that timestamp is set automatically."""
        reading = LocationReading(
            latitude=40.7128,
            longitude=-74.0060
        )
        
        assert reading.timestamp is not None
        assert isinstance(reading.timestamp, datetime)


class TestLocationDetectionResult:
    """Test suite for LocationDetectionResult model."""
    
    def test_location_detection_result_success(self):
        """Test successful LocationDetectionResult."""
        location = LocationReading(
            latitude=40.7128,
            longitude=-74.0060,
            source=LocationSource.GPS
        )
        
        result = LocationDetectionResult(
            success=True,
            location=location,
            fallback_used=LocationSource.GPS,
            confidence_score=0.95,
            detection_time_ms=1500.0,
            battery_impact="medium",
            privacy_level="standard"
        )
        
        assert result.success is True
        assert result.location == location
        assert result.fallback_used == LocationSource.GPS
        assert result.confidence_score == 0.95
        assert result.detection_time_ms == 1500.0
        assert result.battery_impact == "medium"
        assert result.privacy_level == "standard"
    
    def test_location_detection_result_failure(self):
        """Test failed LocationDetectionResult."""
        result = LocationDetectionResult(
            success=False,
            error_message="All methods failed",
            detection_time_ms=5000.0,
            battery_impact="minimal"
        )
        
        assert result.success is False
        assert result.location is None
        assert result.error_message == "All methods failed"
        assert result.detection_time_ms == 5000.0
        assert result.battery_impact == "minimal"


class TestLocationHistoryEntry:
    """Test suite for LocationHistoryEntry model."""
    
    def test_location_history_entry_creation(self):
        """Test LocationHistoryEntry creation."""
        location = LocationReading(
            latitude=40.7128,
            longitude=-74.0060,
            source=LocationSource.GPS
        )
        
        entry = LocationHistoryEntry(
            id="test_id",
            location=location,
            user_id="test_user",
            session_id="test_session",
            created_at=datetime.utcnow(),
            is_favorite=True,
            notes="Test location"
        )
        
        assert entry.id == "test_id"
        assert entry.location == location
        assert entry.user_id == "test_user"
        assert entry.session_id == "test_session"
        assert entry.is_favorite is True
        assert entry.notes == "Test location"


class TestLocationSource:
    """Test suite for LocationSource enum."""
    
    def test_location_source_values(self):
        """Test LocationSource enum values."""
        assert LocationSource.GPS == "gps"
        assert LocationSource.IP_GEOLOCATION == "ip_geolocation"
        assert LocationSource.MANUAL_ENTRY == "manual_entry"
        assert LocationSource.SAVED_LOCATION == "saved_location"
        assert LocationSource.NETWORK_LOCATION == "network_location"
        assert LocationSource.CELL_TOWER == "cell_tower"
        assert LocationSource.WIFI_NETWORK == "wifi_network"


class TestLocationAccuracy:
    """Test suite for LocationAccuracy enum."""
    
    def test_location_accuracy_values(self):
        """Test LocationAccuracy enum values."""
        assert LocationAccuracy.HIGH == "high"
        assert LocationAccuracy.MEDIUM == "medium"
        assert LocationAccuracy.LOW == "low"
        assert LocationAccuracy.VERY_LOW == "very_low"


# Integration tests
class TestCurrentLocationDetectionIntegration:
    """Integration tests for current location detection system."""
    
    @pytest.mark.asyncio
    async def test_full_location_detection_workflow(self):
        """Test complete location detection workflow."""
        service = CurrentLocationDetectionService()
        user_id = "integration_test_user"
        session_id = "integration_test_session"
        
        # Mock successful GPS detection
        mock_gps_result = LocationDetectionResult(
            success=True,
            location=LocationReading(
                latitude=40.7128,
                longitude=-74.0060,
                accuracy_meters=5.0,
                source=LocationSource.GPS,
                confidence_score=0.95
            ),
            confidence_score=0.95
        )
        
        with patch.object(service, '_detect_gps_location', return_value=mock_gps_result):
            with patch.object(service.validation_service, 'validate_coordinates', return_value=MagicMock()):
                # Detect location
                result = await service.detect_current_location(
                    user_id=user_id,
                    session_id=session_id,
                    preferred_sources=[LocationSource.GPS]
                )
                
                assert result.success is True
                
                # Save as favorite
                favorite_success = await service.save_location_as_favorite(
                    result.location,
                    user_id,
                    session_id,
                    "Integration test location"
                )
                
                assert favorite_success is True
                
                # Get history
                history = await service.get_location_history(user_id, limit=5)
                assert len(history) >= 1
                
                # Get favorites
                favorites = await service.get_location_history(user_id, limit=5, include_favorites_only=True)
                assert len(favorites) >= 1
                assert favorites[0].is_favorite is True


# Performance tests
class TestCurrentLocationDetectionPerformance:
    """Performance tests for current location detection system."""
    
    @pytest.mark.asyncio
    async def test_location_detection_performance(self):
        """Test location detection performance."""
        service = CurrentLocationDetectionService()
        
        # Mock fast GPS detection
        mock_gps_result = LocationDetectionResult(
            success=True,
            location=LocationReading(
                latitude=40.7128,
                longitude=-74.0060,
                accuracy_meters=5.0,
                source=LocationSource.GPS,
                confidence_score=0.95
            ),
            confidence_score=0.95
        )
        
        with patch.object(service, '_detect_gps_location', return_value=mock_gps_result):
            with patch.object(service.validation_service, 'validate_coordinates', return_value=MagicMock()):
                start_time = datetime.utcnow()
                
                result = await service.detect_current_location(
                    user_id="perf_test_user",
                    session_id="perf_test_session",
                    preferred_sources=[LocationSource.GPS]
                )
                
                end_time = datetime.utcnow()
                duration = (end_time - start_time).total_seconds()
                
                assert result.success is True
                assert duration < 1.0  # Should complete within 1 second
                assert result.detection_time_ms < 1000  # Should be under 1 second
    
    @pytest.mark.asyncio
    async def test_location_history_performance(self):
        """Test location history performance with large datasets."""
        service = CurrentLocationDetectionService()
        user_id = "perf_test_user"
        
        # Add many history entries
        for i in range(100):
            entry = LocationHistoryEntry(
                id=str(uuid4()),
                location=LocationReading(
                    latitude=40.7128 + (i * 0.001),
                    longitude=-74.0060 + (i * 0.001),
                    source=LocationSource.GPS
                ),
                user_id=user_id,
                session_id="perf_test_session",
                created_at=datetime.utcnow() - timedelta(minutes=i),
                is_favorite=(i % 10 == 0)
            )
            service.location_history.append(entry)
        
        start_time = datetime.utcnow()
        
        # Test getting history
        history = await service.get_location_history(user_id, limit=50)
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        assert len(history) == 50
        assert duration < 0.1  # Should complete within 100ms


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

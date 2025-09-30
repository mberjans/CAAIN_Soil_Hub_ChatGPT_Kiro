"""
Test Mobile Location Features
TICKET-008_farm-location-input-11.2: Add mobile-specific location features and capabilities

Tests for:
- Field boundary recording and management
- Field photo storage with geotagging
- Voice notes for field annotations
- Offline data synchronization
- Enhanced mobile UX features
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from uuid import uuid4, UUID
import base64

from src.services.mobile_location_service import MobileLocationService
from src.models.mobile_location_models import (
    FieldBoundary, FieldPhoto, VoiceNote, OfflineSyncData, DataType
)

class TestMobileLocationService:
    """Test suite for mobile location service."""
    
    @pytest.fixture
    def service(self):
        return MobileLocationService()
    
    @pytest.fixture
    def sample_boundary_data(self):
        return FieldBoundary(
            id=uuid4(),
            user_id=uuid4(),
            field_name="Test Field",
            points=[
                {"latitude": 40.7128, "longitude": -74.0060, "accuracy": 5.0, "timestamp": datetime.utcnow().isoformat()},
                {"latitude": 40.7138, "longitude": -74.0070, "accuracy": 5.0, "timestamp": datetime.utcnow().isoformat()},
                {"latitude": 40.7148, "longitude": -74.0080, "accuracy": 5.0, "timestamp": datetime.utcnow().isoformat()},
                {"latitude": 40.7128, "longitude": -74.0060, "accuracy": 5.0, "timestamp": datetime.utcnow().isoformat()}
            ],
            area_acres=0.5,
            perimeter_meters=200.0,
            point_count=4
        )
    
    @pytest.fixture
    def sample_photo_data(self):
        return FieldPhoto(
            id=uuid4(),
            user_id=uuid4(),
            field_id="test-field-1",
            photo_data=b"fake_image_data",
            latitude=40.7128,
            longitude=-74.0060,
            accuracy=5.0,
            notes="Test field photo",
            file_type="image/jpeg"
        )
    
    @pytest.fixture
    def sample_voice_note_data(self):
        return VoiceNote(
            id=uuid4(),
            user_id=uuid4(),
            field_id="test-field-1",
            audio_data=b"fake_audio_data",
            latitude=40.7128,
            longitude=-74.0060,
            accuracy=5.0,
            duration=30.5,
            notes="Test voice note",
            file_type="audio/webm"
        )

class TestFieldBoundaryManagement(TestMobileLocationService):
    """Test field boundary management functionality."""
    
    @pytest.mark.asyncio
    async def test_save_field_boundary_success(self, service, sample_boundary_data):
        """Test successful field boundary saving."""
        with patch.object(service, 'get_db') as mock_get_db:
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db
            
            result = await service.save_field_boundary(sample_boundary_data)
            
            assert "boundary_id" in result
            assert "area_acres" in result
            assert "perimeter_meters" in result
            assert "point_count" in result
            assert result["point_count"] == 4
            
            # Verify database call
            mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_save_field_boundary_calculates_area(self, service, sample_boundary_data):
        """Test that area and perimeter are calculated correctly."""
        with patch.object(service, 'get_db') as mock_get_db:
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db
            
            result = await service.save_field_boundary(sample_boundary_data)
            
            # Verify area calculation
            assert result["area_acres"] > 0
            assert result["perimeter_meters"] > 0
    
    @pytest.mark.asyncio
    async def test_get_user_field_boundaries(self, service):
        """Test retrieving field boundaries for a user."""
        user_id = uuid4()
        
        with patch.object(service, 'get_db') as mock_get_db:
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db
            
            # Mock database response
            mock_row = {
                'id': uuid4(),
                'field_name': 'Test Field',
                'points': json.dumps([{"latitude": 40.7128, "longitude": -74.0060}]),
                'area_acres': 0.5,
                'perimeter_meters': 200.0,
                'point_count': 4,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            mock_db.fetch.return_value = [mock_row]
            
            boundaries = await service.get_user_field_boundaries(user_id)
            
            assert len(boundaries) == 1
            assert boundaries[0].field_name == "Test Field"
            assert boundaries[0].area_acres == 0.5
    
    def test_calculate_polygon_area(self, service):
        """Test polygon area calculation."""
        points = [
            {"latitude": 40.7128, "longitude": -74.0060},
            {"latitude": 40.7138, "longitude": -74.0060},
            {"latitude": 40.7138, "longitude": -74.0070},
            {"latitude": 40.7128, "longitude": -74.0070},
            {"latitude": 40.7128, "longitude": -74.0060}
        ]
        
        area = service._calculate_polygon_area(points)
        assert area > 0
    
    def test_calculate_polygon_perimeter(self, service):
        """Test polygon perimeter calculation."""
        points = [
            {"latitude": 40.7128, "longitude": -74.0060},
            {"latitude": 40.7138, "longitude": -74.0060},
            {"latitude": 40.7138, "longitude": -74.0070},
            {"latitude": 40.7128, "longitude": -74.0070},
            {"latitude": 40.7128, "longitude": -74.0060}
        ]
        
        perimeter = service._calculate_polygon_perimeter(points)
        assert perimeter > 0
    
    def test_calculate_distance(self, service):
        """Test distance calculation between two points."""
        distance = service._calculate_distance(40.7128, -74.0060, 40.7138, -74.0070)
        assert distance > 0
        assert distance < 1000  # Should be less than 1km for these close points

class TestFieldPhotoManagement(TestMobileLocationService):
    """Test field photo management functionality."""
    
    @pytest.mark.asyncio
    async def test_save_field_photo_success(self, service, sample_photo_data):
        """Test successful field photo saving."""
        with patch.object(service, 'get_db') as mock_get_db:
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db
            
            result = await service.save_field_photo(sample_photo_data)
            
            assert "photo_id" in result
            assert "location" in result
            assert result["location"]["latitude"] == 40.7128
            assert result["location"]["longitude"] == -74.0060
            
            # Verify database call
            mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_user_field_photos(self, service):
        """Test retrieving field photos for a user."""
        user_id = uuid4()
        
        with patch.object(service, 'get_db') as mock_get_db:
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db
            
            # Mock database response
            mock_row = {
                'id': uuid4(),
                'field_id': 'test-field-1',
                'latitude': 40.7128,
                'longitude': -74.0060,
                'accuracy': 5.0,
                'notes': 'Test photo',
                'file_type': 'image/jpeg',
                'captured_at': datetime.utcnow(),
                'created_at': datetime.utcnow()
            }
            mock_db.fetch.return_value = [mock_row]
            
            photos = await service.get_user_field_photos(user_id)
            
            assert len(photos) == 1
            assert photos[0].latitude == 40.7128
            assert photos[0].file_type == "image/jpeg"
    
    @pytest.mark.asyncio
    async def test_get_field_photo_image(self, service):
        """Test retrieving field photo image data."""
        photo_id = uuid4()
        
        with patch.object(service, 'get_db') as mock_get_db:
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db
            
            # Mock database response
            mock_row = {
                'photo_data': b"fake_image_data",
                'file_type': 'image/jpeg'
            }
            mock_db.fetchrow.return_value = mock_row
            
            result = await service.get_field_photo_image(photo_id)
            
            assert result is not None
            assert "image" in result
            assert "content_type" in result
            assert result["content_type"] == "image/jpeg"

class TestVoiceNotesManagement(TestMobileLocationService):
    """Test voice notes management functionality."""
    
    @pytest.mark.asyncio
    async def test_save_voice_note_success(self, service, sample_voice_note_data):
        """Test successful voice note saving."""
        with patch.object(service, 'get_db') as mock_get_db:
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db
            
            result = await service.save_voice_note(sample_voice_note_data)
            
            assert "voice_note_id" in result
            assert "location" in result
            assert "duration" in result
            assert result["location"]["latitude"] == 40.7128
            assert result["duration"] == 30.5
            
            # Verify database call
            mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_user_voice_notes(self, service):
        """Test retrieving voice notes for a user."""
        user_id = uuid4()
        
        with patch.object(service, 'get_db') as mock_get_db:
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db
            
            # Mock database response
            mock_row = {
                'id': uuid4(),
                'field_id': 'test-field-1',
                'latitude': 40.7128,
                'longitude': -74.0060,
                'accuracy': 5.0,
                'duration': 30.5,
                'notes': 'Test voice note',
                'file_type': 'audio/webm',
                'recorded_at': datetime.utcnow(),
                'created_at': datetime.utcnow()
            }
            mock_db.fetch.return_value = [mock_row]
            
            voice_notes = await service.get_user_voice_notes(user_id)
            
            assert len(voice_notes) == 1
            assert voice_notes[0].latitude == 40.7128
            assert voice_notes[0].duration == 30.5
            assert voice_notes[0].file_type == "audio/webm"
    
    @pytest.mark.asyncio
    async def test_get_voice_note_audio(self, service):
        """Test retrieving voice note audio data."""
        voice_note_id = uuid4()
        
        with patch.object(service, 'get_db') as mock_get_db:
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db
            
            # Mock database response
            mock_row = {
                'audio_data': b"fake_audio_data",
                'file_type': 'audio/webm'
            }
            mock_db.fetchrow.return_value = mock_row
            
            result = await service.get_voice_note_audio(voice_note_id)
            
            assert result is not None
            assert "audio" in result
            assert "content_type" in result
            assert result["content_type"] == "audio/webm"

class TestOfflineDataSynchronization(TestMobileLocationService):
    """Test offline data synchronization functionality."""
    
    @pytest.mark.asyncio
    async def test_sync_offline_data_success(self, service):
        """Test successful offline data synchronization."""
        sync_data = [
            OfflineSyncData(
                id=uuid4(),
                user_id=uuid4(),
                data_type=DataType.BOUNDARY,
                data={
                    "id": str(uuid4()),
                    "user_id": str(uuid4()),
                    "field_name": "Test Field",
                    "points": [{"latitude": 40.7128, "longitude": -74.0060}],
                    "area_acres": 0.5,
                    "perimeter_meters": 200.0,
                    "point_count": 4
                }
            )
        ]
        
        with patch.object(service, '_sync_boundary_data') as mock_sync:
            mock_sync.return_value = None
            
            result = await service.sync_offline_data(sync_data)
            
            assert result["synced_items"] == 1
            assert result["failed_items"] == 0
            mock_sync.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_sync_offline_data_with_failures(self, service):
        """Test offline data synchronization with some failures."""
        sync_data = [
            OfflineSyncData(
                id=uuid4(),
                user_id=uuid4(),
                data_type=DataType.BOUNDARY,
                data={"invalid": "data"}
            ),
            OfflineSyncData(
                id=uuid4(),
                user_id=uuid4(),
                data_type=DataType.PHOTO,
                data={
                    "id": str(uuid4()),
                    "user_id": str(uuid4()),
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "photo_data": b"fake_image_data"
                }
            )
        ]
        
        with patch.object(service, '_sync_boundary_data') as mock_sync_boundary, \
             patch.object(service, '_sync_photo_data') as mock_sync_photo:
            
            mock_sync_boundary.side_effect = Exception("Sync failed")
            mock_sync_photo.return_value = None
            
            result = await service.sync_offline_data(sync_data)
            
            assert result["synced_items"] == 1
            assert result["failed_items"] == 1
    
    @pytest.mark.asyncio
    async def test_get_offline_sync_status(self, service):
        """Test getting offline sync status."""
        user_id = uuid4()
        
        with patch.object(service, 'get_db') as mock_get_db:
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db
            
            # Mock database responses
            mock_db.fetchval.side_effect = [5, datetime.utcnow()]  # pending_count, last_sync
            
            result = await service.get_offline_sync_status(user_id)
            
            assert result["user_id"] == str(user_id)
            assert result["pending_items"] == 5
            assert result["status"] == "pending"

class TestFieldMappingSessions(TestMobileLocationService):
    """Test field mapping session management."""
    
    @pytest.mark.asyncio
    async def test_start_field_mapping_session(self, service):
        """Test starting a new field mapping session."""
        user_id = uuid4()
        field_name = "Test Field"
        latitude = 40.7128
        longitude = -74.0060
        
        session_id = await service.start_field_mapping_session(
            user_id, field_name, latitude, longitude
        )
        
        assert isinstance(session_id, UUID)
        assert session_id in service.active_sessions
        
        session = service.active_sessions[session_id]
        assert session.user_id == user_id
        assert session.field_name == field_name
        assert session.start_location == (latitude, longitude)
        assert session.is_active is True
    
    @pytest.mark.asyncio
    async def test_add_mapping_point(self, service):
        """Test adding points to a mapping session."""
        # Start a session first
        user_id = uuid4()
        session_id = await service.start_field_mapping_session(
            user_id, "Test Field", 40.7128, -74.0060
        )
        
        # Add a point
        result = await service.add_mapping_point(
            session_id, 40.7138, -74.0070, accuracy=5.0, altitude=10.0
        )
        
        assert result["point_count"] == 1
        assert result["estimated_area"] == 0  # Not enough points for area calculation
        
        session = service.active_sessions[session_id]
        assert len(session.points) == 1
        assert session.points[0]["latitude"] == 40.7138
        assert session.points[0]["longitude"] == -74.0070
        assert session.points[0]["accuracy"] == 5.0
        assert session.points[0]["altitude"] == 10.0
    
    @pytest.mark.asyncio
    async def test_complete_field_mapping(self, service):
        """Test completing a field mapping session."""
        # Start a session and add enough points
        user_id = uuid4()
        session_id = await service.start_field_mapping_session(
            user_id, "Test Field", 40.7128, -74.0060
        )
        
        # Add points to form a square
        points = [
            (40.7128, -74.0060),
            (40.7138, -74.0060),
            (40.7138, -74.0070),
            (40.7128, -74.0070),
            (40.7128, -74.0060)  # Close the polygon
        ]
        
        for lat, lng in points:
            await service.add_mapping_point(session_id, lat, lng)
        
        with patch.object(service, 'save_field_boundary') as mock_save:
            mock_save.return_value = {
                "boundary_id": uuid4(),
                "area_acres": 0.5,
                "perimeter_meters": 200.0,
                "point_count": 5
            }
            
            result = await service.complete_field_mapping(session_id)
            
            assert "boundary_id" in result
            assert "final_area" in result
            assert "final_perimeter" in result
            assert "point_count" in result
            assert result["point_count"] == 5
            
            # Verify session is no longer active
            assert session_id not in service.active_sessions
    
    @pytest.mark.asyncio
    async def test_complete_field_mapping_insufficient_points(self, service):
        """Test completing a mapping session with insufficient points."""
        user_id = uuid4()
        session_id = await service.start_field_mapping_session(
            user_id, "Test Field", 40.7128, -74.0060
        )
        
        # Add only 2 points (not enough for a polygon)
        await service.add_mapping_point(session_id, 40.7138, -74.0070)
        
        with pytest.raises(ValueError, match="Not enough points"):
            await service.complete_field_mapping(session_id)
    
    @pytest.mark.asyncio
    async def test_add_mapping_point_invalid_session(self, service):
        """Test adding points to an invalid session."""
        invalid_session_id = uuid4()
        
        with pytest.raises(ValueError, match="Invalid or expired mapping session"):
            await service.add_mapping_point(invalid_session_id, 40.7128, -74.0060)

class TestMobileLocationModels:
    """Test mobile location data models."""
    
    def test_field_boundary_validation(self):
        """Test field boundary model validation."""
        # Valid boundary
        boundary = FieldBoundary(
            id=uuid4(),
            user_id=uuid4(),
            field_name="Test Field",
            points=[
                {"latitude": 40.7128, "longitude": -74.0060},
                {"latitude": 40.7138, "longitude": -74.0070},
                {"latitude": 40.7128, "longitude": -74.0060}
            ]
        )
        assert boundary.field_name == "Test Field"
        assert len(boundary.points) == 3
    
    def test_field_boundary_invalid_points(self):
        """Test field boundary validation with invalid points."""
        with pytest.raises(ValueError):
            FieldBoundary(
                id=uuid4(),
                user_id=uuid4(),
                field_name="Test Field",
                points=[
                    {"latitude": 200, "longitude": -74.0060}  # Invalid latitude
                ]
            )
    
    def test_field_photo_validation(self):
        """Test field photo model validation."""
        photo = FieldPhoto(
            id=uuid4(),
            user_id=uuid4(),
            photo_data=b"fake_image_data",
            latitude=40.7128,
            longitude=-74.0060,
            file_type="image/jpeg"
        )
        assert photo.latitude == 40.7128
        assert photo.file_type == "image/jpeg"
    
    def test_field_photo_invalid_file_type(self):
        """Test field photo validation with invalid file type."""
        with pytest.raises(ValueError):
            FieldPhoto(
                id=uuid4(),
                user_id=uuid4(),
                photo_data=b"fake_image_data",
                latitude=40.7128,
                longitude=-74.0060,
                file_type="invalid/type"
            )
    
    def test_voice_note_validation(self):
        """Test voice note model validation."""
        voice_note = VoiceNote(
            id=uuid4(),
            user_id=uuid4(),
            audio_data=b"fake_audio_data",
            latitude=40.7128,
            longitude=-74.0060,
            duration=30.5,
            file_type="audio/webm"
        )
        assert voice_note.latitude == 40.7128
        assert voice_note.duration == 30.5
        assert voice_note.file_type == "audio/webm"
    
    def test_offline_sync_data_validation(self):
        """Test offline sync data model validation."""
        sync_data = OfflineSyncData(
            id=uuid4(),
            user_id=uuid4(),
            data_type=DataType.BOUNDARY,
            data={
                "id": str(uuid4()),
                "user_id": str(uuid4()),
                "field_name": "Test Field",
                "points": [{"latitude": 40.7128, "longitude": -74.0060}]
            }
        )
        assert sync_data.data_type == DataType.BOUNDARY
        assert "field_name" in sync_data.data

class TestMobileLocationIntegration:
    """Integration tests for mobile location features."""
    
    @pytest.mark.asyncio
    async def test_complete_field_mapping_workflow(self):
        """Test complete field mapping workflow from start to finish."""
        service = MobileLocationService()
        
        # Start mapping session
        user_id = uuid4()
        session_id = await service.start_field_mapping_session(
            user_id, "Integration Test Field", 40.7128, -74.0060
        )
        
        # Add points to form a field boundary
        boundary_points = [
            (40.7128, -74.0060),  # Start
            (40.7138, -74.0060),  # East
            (40.7138, -74.0070),  # Southeast
            (40.7128, -74.0070),  # South
            (40.7128, -74.0060)   # Back to start
        ]
        
        for lat, lng in boundary_points:
            result = await service.add_mapping_point(session_id, lat, lng)
            assert result["point_count"] > 0
        
        # Complete the mapping
        with patch.object(service, 'save_field_boundary') as mock_save:
            mock_save.return_value = {
                "boundary_id": uuid4(),
                "area_acres": 0.5,
                "perimeter_meters": 200.0,
                "point_count": 5
            }
            
            result = await service.complete_field_mapping(session_id)
            
            assert result["point_count"] == 5
            assert result["final_area"] > 0
            assert result["final_perimeter"] > 0
            
            # Verify session is cleaned up
            assert session_id not in service.active_sessions
    
    @pytest.mark.asyncio
    async def test_offline_sync_workflow(self):
        """Test offline data synchronization workflow."""
        service = MobileLocationService()
        
        # Create offline sync data
        sync_data = [
            OfflineSyncData(
                id=uuid4(),
                user_id=uuid4(),
                data_type=DataType.BOUNDARY,
                data={
                    "id": str(uuid4()),
                    "user_id": str(uuid4()),
                    "field_name": "Offline Field",
                    "points": [
                        {"latitude": 40.7128, "longitude": -74.0060},
                        {"latitude": 40.7138, "longitude": -74.0070},
                        {"latitude": 40.7128, "longitude": -74.0060}
                    ]
                }
            ),
            OfflineSyncData(
                id=uuid4(),
                user_id=uuid4(),
                data_type=DataType.PHOTO,
                data={
                    "id": str(uuid4()),
                    "user_id": str(uuid4()),
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "photo_data": b"offline_image_data"
                }
            )
        ]
        
        # Mock the sync methods
        with patch.object(service, '_sync_boundary_data') as mock_sync_boundary, \
             patch.object(service, '_sync_photo_data') as mock_sync_photo:
            
            mock_sync_boundary.return_value = None
            mock_sync_photo.return_value = None
            
            result = await service.sync_offline_data(sync_data)
            
            assert result["synced_items"] == 2
            assert result["failed_items"] == 0
            
            # Verify both sync methods were called
            mock_sync_boundary.assert_called_once()
            mock_sync_photo.assert_called_once()

# Performance tests
class TestMobileLocationPerformance:
    """Performance tests for mobile location features."""
    
    @pytest.mark.asyncio
    async def test_large_boundary_performance(self):
        """Test performance with large boundary data."""
        service = MobileLocationService()
        
        # Create a large boundary with many points
        points = []
        for i in range(1000):  # 1000 points
            lat = 40.7128 + (i * 0.0001)
            lng = -74.0060 + (i * 0.0001)
            points.append({
                "latitude": lat,
                "longitude": lng,
                "accuracy": 5.0,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        boundary_data = FieldBoundary(
            id=uuid4(),
            user_id=uuid4(),
            field_name="Large Test Field",
            points=points
        )
        
        # Test area calculation performance
        start_time = datetime.utcnow()
        area = service._calculate_polygon_area(points)
        end_time = datetime.utcnow()
        
        calculation_time = (end_time - start_time).total_seconds()
        assert calculation_time < 1.0  # Should complete within 1 second
        assert area > 0
    
    @pytest.mark.asyncio
    async def test_concurrent_mapping_sessions(self):
        """Test handling multiple concurrent mapping sessions."""
        service = MobileLocationService()
        
        # Start multiple sessions concurrently
        user_id = uuid4()
        session_tasks = []
        
        for i in range(10):  # 10 concurrent sessions
            task = asyncio.create_task(
                service.start_field_mapping_session(
                    user_id, f"Concurrent Field {i}", 40.7128 + i*0.001, -74.0060 + i*0.001
                )
            )
            session_tasks.append(task)
        
        # Wait for all sessions to start
        session_ids = await asyncio.gather(*session_tasks)
        
        # Verify all sessions are active
        assert len(service.active_sessions) == 10
        for session_id in session_ids:
            assert session_id in service.active_sessions
            assert service.active_sessions[session_id].is_active is True
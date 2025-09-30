"""
Mobile Location Data Models
TICKET-008_farm-location-input-11.2: Add mobile-specific location features and capabilities

Data models for:
- Field boundary recording and management
- Field photo storage with geotagging
- Voice notes for field annotations
- Offline data synchronization
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from uuid import UUID
from enum import Enum

class DataType(str, Enum):
    """Types of mobile location data."""
    BOUNDARY = "boundary"
    PHOTO = "photo"
    VOICE_NOTE = "voice_note"

class FieldBoundary(BaseModel):
    """Model for field boundary data recorded from GPS tracking."""
    
    id: UUID = Field(..., description="Unique boundary identifier")
    user_id: UUID = Field(..., description="User who created the boundary")
    field_name: str = Field(..., description="Name of the field")
    points: List[Dict[str, Any]] = Field(..., description="GPS points forming the boundary")
    area_acres: Optional[float] = Field(None, description="Calculated area in acres")
    perimeter_meters: Optional[float] = Field(None, description="Calculated perimeter in meters")
    point_count: Optional[int] = Field(None, description="Number of GPS points")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('points')
    def validate_points(cls, v):
        """Validate that points have required fields."""
        if not v:
            raise ValueError('Points list cannot be empty')
        
        for point in v:
            if 'latitude' not in point or 'longitude' not in point:
                raise ValueError('Each point must have latitude and longitude')
            
            if not (-90 <= point['latitude'] <= 90):
                raise ValueError('Latitude must be between -90 and 90')
            
            if not (-180 <= point['longitude'] <= 180):
                raise ValueError('Longitude must be between -180 and 180')
        
        return v
    
    @validator('area_acres')
    def validate_area(cls, v):
        """Validate area is positive."""
        if v is not None and v < 0:
            raise ValueError('Area must be positive')
        return v
    
    @validator('perimeter_meters')
    def validate_perimeter(cls, v):
        """Validate perimeter is positive."""
        if v is not None and v < 0:
            raise ValueError('Perimeter must be positive')
        return v

class FieldPhoto(BaseModel):
    """Model for field photos with geotagging information."""
    
    id: UUID = Field(..., description="Unique photo identifier")
    user_id: UUID = Field(..., description="User who took the photo")
    field_id: Optional[str] = Field(None, description="Associated field identifier")
    photo_data: bytes = Field(..., description="Binary photo data")
    latitude: float = Field(..., ge=-90, le=90, description="GPS latitude")
    longitude: float = Field(..., ge=-180, le=180, description="GPS longitude")
    accuracy: Optional[float] = Field(None, ge=0, description="GPS accuracy in meters")
    notes: Optional[str] = Field(None, description="Additional notes about the photo")
    file_type: str = Field(default="image/jpeg", description="MIME type of the photo")
    captured_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('file_type')
    def validate_file_type(cls, v):
        """Validate file type is an image."""
        valid_types = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
        if v not in valid_types:
            raise ValueError(f'File type must be one of: {valid_types}')
        return v

class VoiceNote(BaseModel):
    """Model for voice notes with geotagging information."""
    
    id: UUID = Field(..., description="Unique voice note identifier")
    user_id: UUID = Field(..., description="User who recorded the note")
    field_id: Optional[str] = Field(None, description="Associated field identifier")
    audio_data: bytes = Field(..., description="Binary audio data")
    latitude: float = Field(..., ge=-90, le=90, description="GPS latitude")
    longitude: float = Field(..., ge=-180, le=180, description="GPS longitude")
    accuracy: Optional[float] = Field(None, ge=0, description="GPS accuracy in meters")
    duration: Optional[float] = Field(None, ge=0, description="Audio duration in seconds")
    notes: Optional[str] = Field(None, description="Additional notes about the voice note")
    file_type: str = Field(default="audio/webm", description="MIME type of the audio")
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('file_type')
    def validate_file_type(cls, v):
        """Validate file type is audio."""
        valid_types = ['audio/webm', 'audio/mp4', 'audio/wav', 'audio/ogg']
        if v not in valid_types:
            raise ValueError(f'File type must be one of: {valid_types}')
        return v

class OfflineSyncData(BaseModel):
    """Model for offline data synchronization."""
    
    id: UUID = Field(..., description="Unique sync item identifier")
    user_id: UUID = Field(..., description="User who created the data")
    data_type: DataType = Field(..., description="Type of data being synced")
    data: Dict[str, Any] = Field(..., description="The actual data to sync")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    synced_at: Optional[datetime] = Field(None, description="When the data was synced")
    
    @validator('data')
    def validate_data(cls, v, values):
        """Validate data matches the specified type."""
        if 'data_type' not in values:
            return v
        
        data_type = values['data_type']
        
        if data_type == DataType.BOUNDARY:
            # Validate boundary data structure
            required_fields = ['id', 'user_id', 'field_name', 'points']
            for field in required_fields:
                if field not in v:
                    raise ValueError(f'Boundary data must have {field}')
        elif data_type == DataType.PHOTO:
            # Validate photo data structure
            required_fields = ['id', 'user_id', 'latitude', 'longitude', 'photo_data']
            for field in required_fields:
                if field not in v:
                    raise ValueError(f'Photo data must have {field}')
        elif data_type == DataType.VOICE_NOTE:
            # Validate voice note data structure
            required_fields = ['id', 'user_id', 'latitude', 'longitude', 'audio_data']
            for field in required_fields:
                if field not in v:
                    raise ValueError(f'Voice note data must have {field}')
        
        return v

class MappingSessionData(BaseModel):
    """Model for field mapping session data."""
    
    session_id: UUID = Field(..., description="Unique session identifier")
    user_id: UUID = Field(..., description="User conducting the mapping")
    field_name: str = Field(..., description="Name of the field being mapped")
    start_location: Dict[str, float] = Field(..., description="Starting GPS coordinates")
    points: List[Dict[str, Any]] = Field(default_factory=list, description="GPS points collected")
    started_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True, description="Whether the session is still active")
    
    @validator('start_location')
    def validate_start_location(cls, v):
        """Validate start location has latitude and longitude."""
        if 'latitude' not in v or 'longitude' not in v:
            raise ValueError('Start location must have latitude and longitude')
        
        if not (-90 <= v['latitude'] <= 90):
            raise ValueError('Latitude must be between -90 and 90')
        
        if not (-180 <= v['longitude'] <= 180):
            raise ValueError('Longitude must be between -180 and 180')
        
        return v

class MappingPoint(BaseModel):
    """Model for individual mapping points."""
    
    latitude: float = Field(..., ge=-90, le=90, description="GPS latitude")
    longitude: float = Field(..., ge=-180, le=180, description="GPS longitude")
    accuracy: Optional[float] = Field(None, ge=0, description="GPS accuracy in meters")
    altitude: Optional[float] = Field(None, description="GPS altitude in meters")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class DeviceCapabilities(BaseModel):
    """Model for device capability information."""
    
    geolocation: bool = Field(..., description="GPS/geolocation support")
    camera: bool = Field(..., description="Camera access support")
    microphone: bool = Field(..., description="Microphone access support")
    vibration: bool = Field(..., description="Vibration/haptic feedback support")
    service_worker: bool = Field(..., description="Service worker support")
    indexed_db: bool = Field(..., description="IndexedDB support")
    local_storage: bool = Field(..., description="Local storage support")
    offline_storage: bool = Field(..., description="Offline storage capabilities")

class MobileLocationResponse(BaseModel):
    """Standard response model for mobile location operations."""
    
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Human-readable message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional response data")
    error: Optional[str] = Field(None, description="Error message if operation failed")

class SyncStatus(BaseModel):
    """Model for offline synchronization status."""
    
    user_id: UUID = Field(..., description="User identifier")
    pending_items: int = Field(..., ge=0, description="Number of pending sync items")
    last_sync: Optional[datetime] = Field(None, description="Last successful sync time")
    status: str = Field(..., description="Current sync status")
    
    @validator('status')
    def validate_status(cls, v):
        """Validate status is a valid value."""
        valid_statuses = ['pending', 'syncing', 'synced', 'error']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {valid_statuses}')
        return v

class FieldMappingResult(BaseModel):
    """Model for field mapping completion results."""
    
    session_id: UUID = Field(..., description="Completed session identifier")
    boundary_id: UUID = Field(..., description="Created boundary identifier")
    final_area: float = Field(..., ge=0, description="Final calculated area in acres")
    final_perimeter: float = Field(..., ge=0, description="Final calculated perimeter in meters")
    point_count: int = Field(..., ge=3, description="Total number of mapping points")
    mapping_duration: Optional[float] = Field(None, ge=0, description="Mapping duration in seconds")
    accuracy_score: Optional[float] = Field(None, ge=0, le=1, description="Mapping accuracy score")

class MobileLocationStats(BaseModel):
    """Model for mobile location usage statistics."""
    
    user_id: UUID = Field(..., description="User identifier")
    total_boundaries: int = Field(default=0, ge=0, description="Total field boundaries created")
    total_photos: int = Field(default=0, ge=0, description="Total field photos taken")
    total_voice_notes: int = Field(default=0, ge=0, description="Total voice notes recorded")
    total_area_mapped: float = Field(default=0, ge=0, description="Total area mapped in acres")
    last_activity: Optional[datetime] = Field(None, description="Last mobile location activity")
    offline_sync_count: int = Field(default=0, ge=0, description="Number of offline syncs performed")

# Request/Response models for API endpoints
class FieldBoundaryCreateRequest(BaseModel):
    """Request model for creating field boundaries."""
    
    field_name: str = Field(..., min_length=1, max_length=200, description="Name of the field")
    points: List[Dict[str, Any]] = Field(..., min_items=3, description="GPS points forming the boundary")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")

class FieldPhotoCreateRequest(BaseModel):
    """Request model for creating field photos."""
    
    field_id: Optional[str] = Field(None, description="Associated field identifier")
    latitude: float = Field(..., ge=-90, le=90, description="GPS latitude")
    longitude: float = Field(..., ge=-180, le=180, description="GPS longitude")
    accuracy: Optional[float] = Field(None, ge=0, description="GPS accuracy in meters")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")

class VoiceNoteCreateRequest(BaseModel):
    """Request model for creating voice notes."""
    
    field_id: Optional[str] = Field(None, description="Associated field identifier")
    latitude: float = Field(..., ge=-90, le=90, description="GPS latitude")
    longitude: float = Field(..., ge=-180, le=180, description="GPS longitude")
    accuracy: Optional[float] = Field(None, ge=0, description="GPS accuracy in meters")
    duration: Optional[float] = Field(None, ge=0, description="Audio duration in seconds")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")

class MappingSessionCreateRequest(BaseModel):
    """Request model for creating mapping sessions."""
    
    field_name: str = Field(..., min_length=1, max_length=200, description="Name of the field")
    latitude: float = Field(..., ge=-90, le=90, description="Starting GPS latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Starting GPS longitude")

class MappingPointAddRequest(BaseModel):
    """Request model for adding mapping points."""
    
    latitude: float = Field(..., ge=-90, le=90, description="GPS latitude")
    longitude: float = Field(..., ge=-180, le=180, description="GPS longitude")
    accuracy: Optional[float] = Field(None, ge=0, description="GPS accuracy in meters")
    altitude: Optional[float] = Field(None, description="GPS altitude in meters")
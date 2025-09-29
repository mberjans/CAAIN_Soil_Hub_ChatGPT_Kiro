"""
Mobile Field Tracking Data Models

Data models for mobile app integration with field performance tracking,
GPS location services, and offline data synchronization.
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date
from uuid import UUID
from pydantic import BaseModel, Field, validator
from enum import Enum


class SessionStatus(str, Enum):
    """Status of mobile field session."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class SessionType(str, Enum):
    """Type of mobile field session."""
    PERFORMANCE_TRACKING = "performance_tracking"
    FIELD_MAPPING = "field_mapping"
    CROP_MONITORING = "crop_monitoring"
    DATA_COLLECTION = "data_collection"
    PHOTO_DOCUMENTATION = "photo_documentation"


class PhotoFormat(str, Enum):
    """Supported photo formats."""
    JPEG = "JPEG"
    PNG = "PNG"
    HEIC = "HEIC"


class SyncStatus(str, Enum):
    """Offline data sync status."""
    PENDING = "pending"
    SYNCING = "syncing"
    SYNCED = "synced"
    FAILED = "failed"


class GPSReading(BaseModel):
    """GPS reading with accuracy and timestamp."""
    
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")
    altitude: Optional[float] = Field(None, description="Altitude in meters")
    accuracy: float = Field(..., ge=0.0, description="GPS accuracy in meters")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="GPS reading timestamp")
    
    # Additional GPS metadata
    speed: Optional[float] = Field(None, ge=0.0, description="Speed in meters per second")
    heading: Optional[float] = Field(None, ge=0.0, le=360.0, description="Heading in degrees")
    satellite_count: Optional[int] = Field(None, ge=0, description="Number of satellites")
    
    @validator('accuracy')
    def validate_accuracy(cls, v):
        """Validate GPS accuracy is reasonable."""
        if v > 100:  # More than 100 meters accuracy is questionable
            raise ValueError("GPS accuracy too low for reliable field tracking")
        return v


class FieldBoundary(BaseModel):
    """Field boundary with GPS coordinates."""
    
    boundary_id: UUID = Field(default_factory=UUID, description="Unique boundary identifier")
    farmer_id: UUID = Field(..., description="Farmer identifier")
    field_name: str = Field(..., max_length=200, description="Field name")
    boundary_points: List[GPSReading] = Field(..., min_items=3, description="GPS points defining boundary")
    area_acres: Optional[float] = Field(None, ge=0.0, description="Field area in acres")
    
    # Boundary metadata
    boundary_type: str = Field(default="polygon", description="Type of boundary (polygon, rectangle, circle)")
    created_date: datetime = Field(default_factory=datetime.utcnow, description="Boundary creation date")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last boundary update")
    
    @validator('boundary_points')
    def validate_boundary_points(cls, v):
        """Validate boundary has minimum points for polygon."""
        if len(v) < 3:
            raise ValueError("Field boundary must have at least 3 points")
        return v


class FieldLocation(BaseModel):
    """Field location with GPS and boundary information."""
    
    field_id: UUID = Field(default_factory=UUID, description="Field identifier")
    field_name: str = Field(..., max_length=200, description="Field name")
    gps_reading: GPSReading = Field(..., description="Primary GPS reading")
    field_boundary: Optional[FieldBoundary] = Field(None, description="Field boundary")
    field_size_acres: Optional[float] = Field(None, ge=0.0, description="Field size in acres")
    
    # Location metadata
    elevation_meters: Optional[float] = Field(None, description="Field elevation")
    soil_type: Optional[str] = Field(None, description="Primary soil type")
    drainage_class: Optional[str] = Field(None, description="Drainage classification")
    slope_percent: Optional[float] = Field(None, ge=0.0, le=100.0, description="Field slope percentage")
    
    # Access information
    access_road: Optional[str] = Field(None, description="Access road information")
    nearest_town: Optional[str] = Field(None, description="Nearest town or landmark")


class CropPhoto(BaseModel):
    """Crop photo with metadata and GPS location."""
    
    photo_id: UUID = Field(default_factory=UUID, description="Photo identifier")
    photo_data: bytes = Field(..., description="Photo binary data")
    photo_format: PhotoFormat = Field(..., description="Photo format")
    photo_size_bytes: int = Field(..., ge=0, description="Photo size in bytes")
    
    # Photo metadata
    capture_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Photo capture time")
    gps_location: Optional[GPSReading] = Field(None, description="GPS location where photo was taken")
    camera_info: Optional[Dict[str, Any]] = Field(None, description="Camera information")
    
    # Crop-specific metadata
    crop_variety: Optional[str] = Field(None, description="Crop variety in photo")
    growth_stage: Optional[str] = Field(None, description="Crop growth stage")
    photo_purpose: Optional[str] = Field(None, description="Purpose of photo (disease, yield, etc.)")
    
    # Quality indicators
    image_quality_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Image quality score")
    lighting_conditions: Optional[str] = Field(None, description="Lighting conditions")
    weather_conditions: Optional[str] = Field(None, description="Weather conditions")
    
    @validator('photo_size_bytes')
    def validate_photo_size(cls, v):
        """Validate photo size is reasonable."""
        if v > 50 * 1024 * 1024:  # 50MB limit
            raise ValueError("Photo size exceeds maximum limit of 50MB")
        return v


class FieldNote(BaseModel):
    """Field note with optional GPS location."""
    
    note_id: UUID = Field(default_factory=UUID, description="Note identifier")
    note_text: str = Field(..., max_length=2000, description="Note content")
    note_category: Optional[str] = Field(None, description="Note category (observation, issue, reminder)")
    
    # Location and timing
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Note timestamp")
    gps_location: Optional[GPSReading] = Field(None, description="GPS location where note was made")
    
    # Note metadata
    priority: Optional[str] = Field(None, description="Note priority (low, medium, high)")
    tags: List[str] = Field(default_factory=list, description="Note tags")
    related_photos: List[UUID] = Field(default_factory=list, description="Related photo IDs")
    
    # Context information
    weather_conditions: Optional[str] = Field(None, description="Weather conditions")
    field_conditions: Optional[str] = Field(None, description="Field conditions")
    crop_conditions: Optional[str] = Field(None, description="Crop conditions")


class MobileFieldSession(BaseModel):
    """Mobile field tracking session."""
    
    session_id: UUID = Field(default_factory=UUID, description="Session identifier")
    farmer_id: UUID = Field(..., description="Farmer identifier")
    variety_id: UUID = Field(..., description="Variety identifier")
    
    # Session details
    session_type: SessionType = Field(..., description="Type of tracking session")
    field_location: FieldLocation = Field(..., description="Field location information")
    start_time: datetime = Field(default_factory=datetime.utcnow, description="Session start time")
    end_time: Optional[datetime] = Field(None, description="Session end time")
    status: SessionStatus = Field(default=SessionStatus.ACTIVE, description="Session status")
    
    # Data collection
    data_collected: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict, description="Collected data by type")
    photos_collected: List[CropPhoto] = Field(default_factory=list, description="Photos collected during session")
    notes_collected: List[FieldNote] = Field(default_factory=list, description="Notes collected during session")
    
    # Session metadata
    offline_mode: bool = Field(default=False, description="Whether session was conducted offline")
    device_info: Optional[Dict[str, Any]] = Field(None, description="Mobile device information")
    app_version: Optional[str] = Field(None, description="Mobile app version")
    
    # Quality metrics
    data_quality_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall data quality score")
    gps_accuracy_avg: Optional[float] = Field(None, ge=0.0, description="Average GPS accuracy during session")
    
    @validator('end_time')
    def validate_end_time(cls, v, values):
        """Validate end time is after start time."""
        if v and 'start_time' in values and v <= values['start_time']:
            raise ValueError("End time must be after start time")
        return v


class OfflineDataEntry(BaseModel):
    """Offline data entry for synchronization."""
    
    entry_id: UUID = Field(default_factory=UUID, description="Entry identifier")
    session_id: Optional[UUID] = Field(None, description="Associated session ID")
    entry_type: str = Field(..., description="Type of data entry")
    data: Dict[str, Any] = Field(..., description="Data payload")
    
    # Sync information
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Entry creation timestamp")
    sync_status: SyncStatus = Field(default=SyncStatus.PENDING, description="Sync status")
    sync_attempts: int = Field(default=0, ge=0, description="Number of sync attempts")
    last_sync_attempt: Optional[datetime] = Field(None, description="Last sync attempt timestamp")
    
    # Metadata
    farmer_id: UUID = Field(..., description="Farmer identifier")
    device_id: Optional[str] = Field(None, description="Mobile device identifier")
    app_version: Optional[str] = Field(None, description="App version when entry was created")
    
    # Error handling
    sync_errors: List[str] = Field(default_factory=list, description="Sync error messages")
    retry_after: Optional[datetime] = Field(None, description="When to retry sync")


class SyncStatus(BaseModel):
    """Status of offline data synchronization."""
    
    farmer_id: UUID = Field(..., description="Farmer identifier")
    sync_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Sync timestamp")
    
    # Sync metrics
    total_entries: int = Field(..., ge=0, description="Total entries to sync")
    successful_syncs: int = Field(default=0, ge=0, description="Successfully synced entries")
    failed_syncs: int = Field(default=0, ge=0, description="Failed sync entries")
    success_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Sync success rate")
    
    # Error information
    sync_errors: List[str] = Field(default_factory=list, description="Sync error messages")
    retry_entries: List[UUID] = Field(default_factory=list, description="Entries that need retry")
    
    # Performance metrics
    sync_duration_seconds: float = Field(default=0.0, ge=0.0, description="Sync duration in seconds")
    data_size_bytes: int = Field(default=0, ge=0, description="Total data size synced")
    
    @validator('successful_syncs', 'failed_syncs')
    def validate_sync_counts(cls, v, values):
        """Validate sync counts don't exceed total entries."""
        if 'total_entries' in values and v > values['total_entries']:
            raise ValueError("Sync count cannot exceed total entries")
        return v


class MobileFieldTrackingRequest(BaseModel):
    """Request for mobile field tracking operations."""
    
    farmer_id: UUID = Field(..., description="Farmer identifier")
    variety_id: UUID = Field(..., description="Variety identifier")
    field_location: FieldLocation = Field(..., description="Field location")
    session_type: SessionType = Field(default=SessionType.PERFORMANCE_TRACKING, description="Session type")
    
    # Request options
    enable_offline_mode: bool = Field(default=False, description="Enable offline mode")
    auto_sync: bool = Field(default=True, description="Enable automatic sync")
    gps_accuracy_threshold: float = Field(default=10.0, ge=0.0, description="GPS accuracy threshold")
    
    # Request metadata
    request_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Request timestamp")
    device_info: Optional[Dict[str, Any]] = Field(None, description="Mobile device information")


class MobileFieldTrackingResponse(BaseModel):
    """Response for mobile field tracking operations."""
    
    success: bool = Field(..., description="Whether operation was successful")
    session_id: Optional[UUID] = Field(None, description="Created session ID")
    message: Optional[str] = Field(None, description="Response message")
    
    # Session information
    session_status: Optional[SessionStatus] = Field(None, description="Session status")
    offline_mode: bool = Field(default=False, description="Whether session is in offline mode")
    
    # Data collection info
    data_types_available: List[str] = Field(default_factory=list, description="Available data collection types")
    gps_status: str = Field(default="unknown", description="GPS status")
    
    # Error information
    errors: List[str] = Field(default_factory=list, description="Error messages")
    warnings: List[str] = Field(default_factory=list, description="Warning messages")
    
    # Response metadata
    response_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    processing_time_ms: float = Field(default=0.0, ge=0.0, description="Processing time in milliseconds")


class FieldDataCollectionRequest(BaseModel):
    """Request for collecting field data during session."""
    
    session_id: UUID = Field(..., description="Session identifier")
    data_type: str = Field(..., description="Type of data being collected")
    data_value: Any = Field(..., description="Data value")
    
    # Optional context
    gps_reading: Optional[GPSReading] = Field(None, description="GPS reading for location context")
    photo_data: Optional[CropPhoto] = Field(None, description="Associated photo data")
    field_note: Optional[FieldNote] = Field(None, description="Associated field note")
    
    # Collection metadata
    collection_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Collection timestamp")
    collection_method: Optional[str] = Field(None, description="Data collection method")


class FieldDataCollectionResponse(BaseModel):
    """Response for field data collection."""
    
    success: bool = Field(..., description="Whether data collection was successful")
    data_entry_id: Optional[UUID] = Field(None, description="Created data entry ID")
    message: Optional[str] = Field(None, description="Response message")
    
    # Data validation
    data_validated: bool = Field(default=False, description="Whether data passed validation")
    validation_errors: List[str] = Field(default_factory=list, description="Data validation errors")
    
    # GPS validation
    gps_validated: bool = Field(default=False, description="Whether GPS data was validated")
    gps_accuracy: Optional[float] = Field(None, description="GPS accuracy in meters")
    
    # Response metadata
    response_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    processing_time_ms: float = Field(default=0.0, ge=0.0, description="Processing time in milliseconds")


class OfflineSyncRequest(BaseModel):
    """Request for offline data synchronization."""
    
    farmer_id: UUID = Field(..., description="Farmer identifier")
    offline_data: List[OfflineDataEntry] = Field(..., description="Offline data entries to sync")
    
    # Sync options
    force_sync: bool = Field(default=False, description="Force sync even if errors exist")
    validate_data: bool = Field(default=True, description="Validate data before sync")
    retry_failed: bool = Field(default=True, description="Retry previously failed entries")
    
    # Request metadata
    request_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Request timestamp")
    device_info: Optional[Dict[str, Any]] = Field(None, description="Mobile device information")


class OfflineSyncResponse(BaseModel):
    """Response for offline data synchronization."""
    
    success: bool = Field(..., description="Whether sync was successful")
    sync_status: SyncStatus = Field(..., description="Detailed sync status")
    message: Optional[str] = Field(None, description="Response message")
    
    # Sync results
    entries_processed: int = Field(default=0, ge=0, description="Entries processed")
    entries_synced: int = Field(default=0, ge=0, description="Entries successfully synced")
    entries_failed: int = Field(default=0, ge=0, description="Entries that failed to sync")
    
    # Error information
    sync_errors: List[str] = Field(default_factory=list, description="Sync error messages")
    retry_entries: List[UUID] = Field(default_factory=list, description="Entries that need retry")
    
    # Response metadata
    response_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    processing_time_ms: float = Field(default=0.0, ge=0.0, description="Processing time in milliseconds")
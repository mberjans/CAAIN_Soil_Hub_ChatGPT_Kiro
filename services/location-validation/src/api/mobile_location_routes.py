"""
Mobile Location API Routes
TICKET-008_farm-location-input-11.2: Add mobile-specific location features and capabilities

Provides API endpoints for:
- Field boundary recording and management
- Field photo storage with geotagging
- Voice notes for field annotations
- Offline data synchronization
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import List, Optional, Dict, Any
import json
import logging
from datetime import datetime
from uuid import UUID, uuid4
import base64
import io

from ..models import LocationData, FieldBoundary, FieldPhoto, VoiceNote, OfflineSyncData
from ..services.mobile_location_service import MobileLocationService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/mobile", tags=["mobile-location"])

# Dependency injection
async def get_mobile_location_service() -> MobileLocationService:
    return MobileLocationService()

@router.post("/field-boundaries", response_model=Dict[str, Any])
async def save_field_boundary(
    boundary_data: FieldBoundary,
    service: MobileLocationService = Depends(get_mobile_location_service)
):
    """
    Save field boundary data recorded from mobile GPS tracking.
    
    This endpoint handles field boundary data captured through GPS tracking
    while walking around field perimeters on mobile devices.
    """
    try:
        result = await service.save_field_boundary(boundary_data)
        return {
            "success": True,
            "boundary_id": result["boundary_id"],
            "message": "Field boundary saved successfully",
            "area_acres": result["area_acres"],
            "perimeter_meters": result["perimeter_meters"],
            "point_count": result["point_count"]
        }
    except Exception as e:
        logger.error(f"Error saving field boundary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save field boundary: {str(e)}")

@router.get("/field-boundaries/{user_id}", response_model=List[FieldBoundary])
async def get_user_field_boundaries(
    user_id: UUID,
    service: MobileLocationService = Depends(get_mobile_location_service)
):
    """
    Retrieve all field boundaries for a specific user.
    """
    try:
        boundaries = await service.get_user_field_boundaries(user_id)
        return boundaries
    except Exception as e:
        logger.error(f"Error retrieving field boundaries: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve field boundaries: {str(e)}")

@router.post("/field-photos", response_model=Dict[str, Any])
async def save_field_photo(
    photo: UploadFile = File(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    accuracy: Optional[float] = Form(None),
    field_id: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    service: MobileLocationService = Depends(get_mobile_location_service)
):
    """
    Save field photo with geotagging information.
    
    This endpoint handles field photos captured through mobile camera
    with automatic geotagging based on GPS coordinates.
    """
    try:
        # Read photo data
        photo_data = await photo.read()
        
        # Create photo object
        field_photo = FieldPhoto(
            id=uuid4(),
            photo_data=photo_data,
            latitude=latitude,
            longitude=longitude,
            accuracy=accuracy,
            field_id=field_id,
            notes=notes,
            captured_at=datetime.utcnow(),
            file_type=photo.content_type or "image/jpeg"
        )
        
        result = await service.save_field_photo(field_photo)
        return {
            "success": True,
            "photo_id": str(result["photo_id"]),
            "message": "Field photo saved successfully",
            "location": {
                "latitude": latitude,
                "longitude": longitude,
                "accuracy": accuracy
            }
        }
    except Exception as e:
        logger.error(f"Error saving field photo: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save field photo: {str(e)}")

@router.get("/field-photos/{user_id}", response_model=List[FieldPhoto])
async def get_user_field_photos(
    user_id: UUID,
    field_id: Optional[str] = None,
    service: MobileLocationService = Depends(get_mobile_location_service)
):
    """
    Retrieve field photos for a specific user, optionally filtered by field.
    """
    try:
        photos = await service.get_user_field_photos(user_id, field_id)
        return photos
    except Exception as e:
        logger.error(f"Error retrieving field photos: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve field photos: {str(e)}")

@router.get("/field-photos/{photo_id}/image")
async def get_field_photo_image(
    photo_id: UUID,
    service: MobileLocationService = Depends(get_mobile_location_service)
):
    """
    Retrieve the actual image data for a field photo.
    """
    try:
        photo_data = await service.get_field_photo_image(photo_id)
        if not photo_data:
            raise HTTPException(status_code=404, detail="Photo not found")
        
        return {
            "photo_id": str(photo_id),
            "image_data": base64.b64encode(photo_data["image"]).decode('utf-8'),
            "content_type": photo_data["content_type"]
        }
    except Exception as e:
        logger.error(f"Error retrieving field photo image: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve photo image: {str(e)}")

@router.post("/voice-notes", response_model=Dict[str, Any])
async def save_voice_note(
    audio: UploadFile = File(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    accuracy: Optional[float] = Form(None),
    field_id: Optional[str] = Form(None),
    duration: Optional[float] = Form(None),
    notes: Optional[str] = Form(None),
    service: MobileLocationService = Depends(get_mobile_location_service)
):
    """
    Save voice note with geotagging information.
    
    This endpoint handles voice notes recorded through mobile devices
    with automatic geotagging based on GPS coordinates.
    """
    try:
        # Read audio data
        audio_data = await audio.read()
        
        # Create voice note object
        voice_note = VoiceNote(
            id=uuid4(),
            audio_data=audio_data,
            latitude=latitude,
            longitude=longitude,
            accuracy=accuracy,
            field_id=field_id,
            duration=duration,
            notes=notes,
            recorded_at=datetime.utcnow(),
            file_type=audio.content_type or "audio/webm"
        )
        
        result = await service.save_voice_note(voice_note)
        return {
            "success": True,
            "voice_note_id": str(result["voice_note_id"]),
            "message": "Voice note saved successfully",
            "location": {
                "latitude": latitude,
                "longitude": longitude,
                "accuracy": accuracy
            },
            "duration": duration
        }
    except Exception as e:
        logger.error(f"Error saving voice note: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save voice note: {str(e)}")

@router.get("/voice-notes/{user_id}", response_model=List[VoiceNote])
async def get_user_voice_notes(
    user_id: UUID,
    field_id: Optional[str] = None,
    service: MobileLocationService = Depends(get_mobile_location_service)
):
    """
    Retrieve voice notes for a specific user, optionally filtered by field.
    """
    try:
        voice_notes = await service.get_user_voice_notes(user_id, field_id)
        return voice_notes
    except Exception as e:
        logger.error(f"Error retrieving voice notes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve voice notes: {str(e)}")

@router.get("/voice-notes/{voice_note_id}/audio")
async def get_voice_note_audio(
    voice_note_id: UUID,
    service: MobileLocationService = Depends(get_mobile_location_service)
):
    """
    Retrieve the actual audio data for a voice note.
    """
    try:
        audio_data = await service.get_voice_note_audio(voice_note_id)
        if not audio_data:
            raise HTTPException(status_code=404, detail="Voice note not found")
        
        return {
            "voice_note_id": str(voice_note_id),
            "audio_data": base64.b64encode(audio_data["audio"]).decode('utf-8'),
            "content_type": audio_data["content_type"]
        }
    except Exception as e:
        logger.error(f"Error retrieving voice note audio: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve voice note audio: {str(e)}")

@router.post("/offline-sync", response_model=Dict[str, Any])
async def sync_offline_data(
    sync_data: List[OfflineSyncData],
    service: MobileLocationService = Depends(get_mobile_location_service)
):
    """
    Synchronize offline data collected on mobile devices.
    
    This endpoint handles bulk synchronization of field data
    collected while offline on mobile devices.
    """
    try:
        result = await service.sync_offline_data(sync_data)
        return {
            "success": True,
            "synced_items": result["synced_items"],
            "failed_items": result["failed_items"],
            "message": f"Synced {result['synced_items']} items successfully"
        }
    except Exception as e:
        logger.error(f"Error syncing offline data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to sync offline data: {str(e)}")

@router.get("/offline-sync-status/{user_id}", response_model=Dict[str, Any])
async def get_offline_sync_status(
    user_id: UUID,
    service: MobileLocationService = Depends(get_mobile_location_service)
):
    """
    Get the synchronization status for offline data.
    """
    try:
        status = await service.get_offline_sync_status(user_id)
        return status
    except Exception as e:
        logger.error(f"Error getting offline sync status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get sync status: {str(e)}")

@router.post("/field-mapping/start", response_model=Dict[str, Any])
async def start_field_mapping(
    user_id: UUID,
    field_name: str,
    latitude: float,
    longitude: float,
    service: MobileLocationService = Depends(get_mobile_location_service)
):
    """
    Start a new field mapping session.
    """
    try:
        session_id = await service.start_field_mapping_session(
            user_id, field_name, latitude, longitude
        )
        return {
            "success": True,
            "session_id": str(session_id),
            "message": "Field mapping session started"
        }
    except Exception as e:
        logger.error(f"Error starting field mapping: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start field mapping: {str(e)}")

@router.post("/field-mapping/add-point", response_model=Dict[str, Any])
async def add_mapping_point(
    session_id: UUID,
    latitude: float,
    longitude: float,
    accuracy: Optional[float] = None,
    altitude: Optional[float] = None,
    service: MobileLocationService = Depends(get_mobile_location_service)
):
    """
    Add a GPS point to the current field mapping session.
    """
    try:
        result = await service.add_mapping_point(
            session_id, latitude, longitude, accuracy, altitude
        )
        return {
            "success": True,
            "point_count": result["point_count"],
            "estimated_area": result["estimated_area"],
            "message": "Mapping point added successfully"
        }
    except Exception as e:
        logger.error(f"Error adding mapping point: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add mapping point: {str(e)}")

@router.post("/field-mapping/complete", response_model=Dict[str, Any])
async def complete_field_mapping(
    session_id: UUID,
    service: MobileLocationService = Depends(get_mobile_location_service)
):
    """
    Complete the field mapping session and calculate final boundary.
    """
    try:
        result = await service.complete_field_mapping(session_id)
        return {
            "success": True,
            "boundary_id": str(result["boundary_id"]),
            "final_area": result["final_area"],
            "final_perimeter": result["final_perimeter"],
            "point_count": result["point_count"],
            "message": "Field mapping completed successfully"
        }
    except Exception as e:
        logger.error(f"Error completing field mapping: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to complete field mapping: {str(e)}")

@router.get("/device-capabilities", response_model=Dict[str, Any])
async def get_device_capabilities():
    """
    Get information about device capabilities for mobile features.
    """
    capabilities = {
        "geolocation": "geolocation" in navigator,
        "camera": "mediaDevices" in navigator and "getUserMedia" in navigator.mediaDevices,
        "microphone": "mediaDevices" in navigator and "getUserMedia" in navigator.mediaDevices,
        "vibration": "vibrate" in navigator,
        "service_worker": "serviceWorker" in navigator,
        "indexed_db": "indexedDB" in window,
        "local_storage": "localStorage" in window,
        "offline_storage": "indexedDB" in window and "localStorage" in window
    }
    
    return {
        "capabilities": capabilities,
        "supported_features": [k for k, v in capabilities.items() if v],
        "unsupported_features": [k for k, v in capabilities.items() if not v]
    }

@router.get("/health")
async def health_check():
    """Health check endpoint for mobile location service."""
    return {
        "status": "healthy",
        "service": "mobile-location",
        "features": [
            "field-boundary-recording",
            "field-photo-geotagging",
            "voice-notes",
            "offline-sync",
            "field-mapping"
        ]
    }
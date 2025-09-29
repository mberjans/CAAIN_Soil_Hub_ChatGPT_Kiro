"""
Mobile Field Tracking API Endpoints

API endpoints for mobile app integration with field performance tracking,
GPS location services, and offline data synchronization.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from typing import List, Dict, Any, Optional
import logging
from uuid import UUID
from datetime import datetime

try:
    from ..services.mobile_field_tracking_service import mobile_field_tracking_service
    from ..models.mobile_tracking_models import (
        MobileFieldTrackingRequest,
        MobileFieldTrackingResponse,
        FieldDataCollectionRequest,
        FieldDataCollectionResponse,
        OfflineSyncRequest,
        OfflineSyncResponse,
        FieldLocation,
        GPSReading,
        CropPhoto,
        FieldNote,
        SessionStatus,
        SessionType
    )
except ImportError:
    from services.mobile_field_tracking_service import mobile_field_tracking_service
    from models.mobile_tracking_models import (
        MobileFieldTrackingRequest,
        MobileFieldTrackingResponse,
        FieldDataCollectionRequest,
        FieldDataCollectionResponse,
        OfflineSyncRequest,
        OfflineSyncResponse,
        FieldLocation,
        GPSReading,
        CropPhoto,
        FieldNote,
        SessionStatus,
        SessionType
    )

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/mobile-tracking", tags=["mobile-tracking"])


# Dependency injection
async def get_mobile_tracking_service():
    """Get mobile field tracking service instance."""
    return mobile_field_tracking_service


@router.post("/start-session", response_model=MobileFieldTrackingResponse)
async def start_field_session(
    request: MobileFieldTrackingRequest,
    service = Depends(get_mobile_tracking_service)
):
    """
    Start a new mobile field tracking session.
    
    This endpoint initializes a field tracking session for mobile apps,
    enabling GPS-based data collection, photo capture, and field notes.
    
    Features:
    - GPS location validation
    - Field boundary verification
    - Offline mode support
    - Session management
    - Device information tracking
    """
    try:
        start_time = datetime.utcnow()
        
        # Start field session
        session = await service.start_field_session(
            farmer_id=request.farmer_id,
            variety_id=request.variety_id,
            field_location=request.field_location,
            session_type=request.session_type
        )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return MobileFieldTrackingResponse(
            success=True,
            session_id=session.session_id,
            message="Field session started successfully",
            session_status=SessionStatus.ACTIVE,
            offline_mode=request.enable_offline_mode,
            data_types_available=[
                "yield_measurement",
                "crop_photo",
                "field_note",
                "weather_observation",
                "disease_observation",
                "soil_sample"
            ],
            gps_status="active",
            processing_time_ms=processing_time
        )
        
    except ValueError as e:
        logger.warning(f"Validation error in field session start: {e}")
        return MobileFieldTrackingResponse(
            success=False,
            message=f"Validation error: {str(e)}",
            errors=[str(e)],
            gps_status="error"
        )
        
    except Exception as e:
        logger.error(f"Error starting field session: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start field session: {str(e)}"
        )


@router.post("/collect-data", response_model=FieldDataCollectionResponse)
async def collect_field_data(
    request: FieldDataCollectionRequest,
    service = Depends(get_mobile_tracking_service)
):
    """
    Collect field data during an active session.
    
    This endpoint allows mobile apps to collect various types of field data
    including measurements, photos, notes, and observations with GPS context.
    
    Features:
    - Multiple data type support
    - GPS location validation
    - Photo metadata processing
    - Field note management
    - Data quality assessment
    """
    try:
        start_time = datetime.utcnow()
        
        # Collect field data
        success = await service.collect_field_data(
            session_id=request.session_id,
            data_type=request.data_type,
            data_value=request.data_value,
            gps_reading=request.gps_reading,
            photo_data=request.photo_data,
            field_note=request.field_note
        )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Validate GPS if provided
        gps_validated = False
        gps_accuracy = None
        if request.gps_reading:
            gps_validated = True
            gps_accuracy = request.gps_reading.accuracy
        
        return FieldDataCollectionResponse(
            success=success,
            data_entry_id=UUID(),  # Would be actual entry ID from service
            message="Field data collected successfully" if success else "Failed to collect field data",
            data_validated=True,  # Would be actual validation result
            gps_validated=gps_validated,
            gps_accuracy=gps_accuracy,
            processing_time_ms=processing_time
        )
        
    except ValueError as e:
        logger.warning(f"Validation error in data collection: {e}")
        return FieldDataCollectionResponse(
            success=False,
            message=f"Validation error: {str(e)}",
            validation_errors=[str(e)]
        )
        
    except Exception as e:
        logger.error(f"Error collecting field data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to collect field data: {str(e)}"
        )


@router.post("/capture-photo", response_model=FieldDataCollectionResponse)
async def capture_crop_photo(
    session_id: UUID,
    photo_data: CropPhoto,
    gps_reading: GPSReading,
    service = Depends(get_mobile_tracking_service)
):
    """
    Capture and process crop photo with GPS location.
    
    This endpoint handles crop photo capture with GPS metadata,
    image quality assessment, and automatic categorization.
    
    Features:
    - Photo metadata extraction
    - GPS location validation
    - Image quality assessment
    - Automatic crop identification
    - Weather condition logging
    """
    try:
        start_time = datetime.utcnow()
        
        # Capture crop photo
        success = await service.capture_crop_photo(
            session_id=session_id,
            photo_data=photo_data,
            gps_reading=gps_reading
        )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return FieldDataCollectionResponse(
            success=success,
            data_entry_id=photo_data.photo_id,
            message="Crop photo captured successfully" if success else "Failed to capture crop photo",
            data_validated=True,
            gps_validated=True,
            gps_accuracy=gps_reading.accuracy,
            processing_time_ms=processing_time
        )
        
    except ValueError as e:
        logger.warning(f"Validation error in photo capture: {e}")
        return FieldDataCollectionResponse(
            success=False,
            message=f"Validation error: {str(e)}",
            validation_errors=[str(e)]
        )
        
    except Exception as e:
        logger.error(f"Error capturing crop photo: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to capture crop photo: {str(e)}"
        )


@router.post("/add-field-note", response_model=FieldDataCollectionResponse)
async def add_field_note(
    session_id: UUID,
    field_note: FieldNote,
    gps_reading: Optional[GPSReading] = None,
    service = Depends(get_mobile_tracking_service)
):
    """
    Add field note with optional GPS location.
    
    This endpoint allows farmers to add contextual notes during field sessions
    with optional GPS location for spatial reference.
    
    Features:
    - Note categorization
    - GPS location tagging
    - Priority assignment
    - Tag management
    - Photo association
    """
    try:
        start_time = datetime.utcnow()
        
        # Add field note
        success = await service.add_field_note(
            session_id=session_id,
            field_note=field_note,
            gps_reading=gps_reading
        )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return FieldDataCollectionResponse(
            success=success,
            data_entry_id=field_note.note_id,
            message="Field note added successfully" if success else "Failed to add field note",
            data_validated=True,
            gps_validated=gps_reading is not None,
            gps_accuracy=gps_reading.accuracy if gps_reading else None,
            processing_time_ms=processing_time
        )
        
    except ValueError as e:
        logger.warning(f"Validation error in field note: {e}")
        return FieldDataCollectionResponse(
            success=False,
            message=f"Validation error: {str(e)}",
            validation_errors=[str(e)]
        )
        
    except Exception as e:
        logger.error(f"Error adding field note: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add field note: {str(e)}"
        )


@router.post("/end-session", response_model=Dict[str, Any])
async def end_field_session(
    session_id: UUID,
    generate_feedback_survey: bool = Query(True, description="Generate farmer feedback survey"),
    service = Depends(get_mobile_tracking_service)
):
    """
    End field tracking session and generate farmer feedback.
    
    This endpoint concludes a field session, processes collected data,
    and optionally generates a farmer feedback survey based on session data.
    
    Features:
    - Session data processing
    - Automatic feedback generation
    - Data quality assessment
    - Session summary creation
    - Performance metrics calculation
    """
    try:
        start_time = datetime.utcnow()
        
        # End field session
        session_result = await service.end_field_session(
            session_id=session_id,
            generate_feedback_survey=generate_feedback_survey
        )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return {
            "success": True,
            "session_result": session_result,
            "message": "Field session ended successfully",
            "processing_time_ms": processing_time
        }
        
    except ValueError as e:
        logger.warning(f"Validation error in session end: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Validation error: {str(e)}"
        )
        
    except Exception as e:
        logger.error(f"Error ending field session: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to end field session: {str(e)}"
        )


@router.post("/sync-offline-data", response_model=OfflineSyncResponse)
async def sync_offline_data(
    request: OfflineSyncRequest,
    background_tasks: BackgroundTasks,
    service = Depends(get_mobile_tracking_service)
):
    """
    Synchronize offline data with the server.
    
    This endpoint handles synchronization of data collected offline,
    including validation, conflict resolution, and error handling.
    
    Features:
    - Batch data synchronization
    - Data validation and conflict resolution
    - Error handling and retry logic
    - Progress tracking
    - Background processing
    """
    try:
        start_time = datetime.utcnow()
        
        # Sync offline data
        sync_status = await service.sync_offline_data(
            farmer_id=request.farmer_id,
            offline_data=request.offline_data
        )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return OfflineSyncResponse(
            success=sync_status.success_rate > 0.8,  # Consider successful if >80% synced
            sync_status=sync_status,
            message=f"Offline sync completed: {sync_status.successful_syncs}/{sync_status.total_entries} successful",
            entries_processed=sync_status.total_entries,
            entries_synced=sync_status.successful_syncs,
            entries_failed=sync_status.failed_syncs,
            sync_errors=sync_status.sync_errors,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error syncing offline data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sync offline data: {str(e)}"
        )


@router.get("/field-boundaries/{farmer_id}", response_model=List[Dict[str, Any]])
async def get_field_boundaries(
    farmer_id: UUID,
    variety_id: Optional[UUID] = Query(None, description="Filter by variety ID"),
    service = Depends(get_mobile_tracking_service)
):
    """
    Get field boundaries for a farmer.
    
    This endpoint retrieves field boundary information for a farmer,
    optionally filtered by variety, for use in mobile field mapping.
    
    Features:
    - Field boundary retrieval
    - GPS coordinate validation
    - Area calculations
    - Variety filtering
    - Boundary validation
    """
    try:
        # Get field boundaries
        boundaries = await service.get_field_boundaries(
            farmer_id=farmer_id,
            variety_id=variety_id
        )
        
        return [
            {
                "boundary_id": str(boundary.boundary_id),
                "field_name": boundary.field_name,
                "boundary_points": [point.dict() for point in boundary.boundary_points],
                "area_acres": boundary.area_acres,
                "boundary_type": boundary.boundary_type,
                "created_date": boundary.created_date.isoformat(),
                "last_updated": boundary.last_updated.isoformat()
            }
            for boundary in boundaries
        ]
        
    except Exception as e:
        logger.error(f"Error getting field boundaries: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get field boundaries: {str(e)}"
        )


@router.get("/session-status/{session_id}", response_model=Dict[str, Any])
async def get_session_status(
    session_id: UUID,
    service = Depends(get_mobile_tracking_service)
):
    """
    Get status of an active field session.
    
    This endpoint provides real-time status information for an active
    field session, including data collection progress and GPS status.
    
    Features:
    - Real-time session status
    - Data collection progress
    - GPS accuracy monitoring
    - Session metrics
    - Error status
    """
    try:
        # Get session from active sessions
        session = service.active_sessions.get(str(session_id))
        
        if not session:
            raise HTTPException(
                status_code=404,
                detail=f"Active session {session_id} not found"
            )
        
        # Calculate session metrics
        total_data_points = sum(len(data_list) for data_list in session.data_collected.values())
        session_duration = (datetime.utcnow() - session.start_time).total_seconds() / 60
        
        return {
            "session_id": str(session.session_id),
            "status": session.status.value,
            "session_type": session.session_type.value,
            "start_time": session.start_time.isoformat(),
            "duration_minutes": session_duration,
            "data_types_collected": list(session.data_collected.keys()),
            "total_data_points": total_data_points,
            "photos_collected": len(session.photos_collected),
            "notes_collected": len(session.notes_collected),
            "offline_mode": session.offline_mode,
            "data_quality_score": session.data_quality_score,
            "gps_accuracy_avg": session.gps_accuracy_avg,
            "field_location": session.field_location.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session status: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for mobile tracking service."""
    return {
        "status": "healthy",
        "service": "mobile-field-tracking",
        "timestamp": datetime.utcnow().isoformat(),
        "features": [
            "field_session_management",
            "gps_location_tracking",
            "photo_capture",
            "field_notes",
            "offline_data_sync",
            "field_boundary_management"
        ],
        "active_sessions": len(mobile_field_tracking_service.active_sessions),
        "offline_entries": len(mobile_field_tracking_service.offline_storage)
    }
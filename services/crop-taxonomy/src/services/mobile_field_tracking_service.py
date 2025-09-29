"""
Mobile Field Tracking Service

Service for mobile app integration with field performance tracking,
GPS location services, and offline data synchronization.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date
from uuid import UUID
import json
import asyncio
from dataclasses import dataclass
from enum import Enum

try:
    from ..models.farmer_experience_models import (
        FarmerExperienceEntry,
        FieldPerformanceData,
        FarmerFeedbackSurvey
    )
    from ..models.mobile_tracking_models import (
        FieldLocation,
        GPSReading,
        OfflineDataEntry,
        SyncStatus,
        MobileFieldSession,
        FieldBoundary,
        CropPhoto,
        FieldNote
    )
except ImportError:
    from models.farmer_experience_models import (
        FarmerExperienceEntry,
        FieldPerformanceData,
        FarmerFeedbackSurvey
    )
    from models.mobile_tracking_models import (
        FieldLocation,
        GPSReading,
        OfflineDataEntry,
        SyncStatus,
        MobileFieldSession,
        FieldBoundary,
        CropPhoto,
        FieldNote
    )

logger = logging.getLogger(__name__)


class MobileFieldTrackingService:
    """
    Service for mobile field tracking integration with farmer experience collection.
    """

    def __init__(self, database_url: Optional[str] = None):
        """Initialize the mobile field tracking service."""
        try:
            from ..database.crop_taxonomy_db import CropTaxonomyDatabase
            self.db = CropTaxonomyDatabase(database_url)
            self.database_available = self.db.test_connection()
            logger.info(f"Mobile tracking service database connection: {'successful' if self.database_available else 'failed'}")
        except ImportError:
            logger.warning("Database integration not available for mobile tracking service")
            self.db = None
            self.database_available = False
        
        # Initialize offline storage
        self.offline_storage = {}
        self.sync_queue = []
        
        # GPS and location services
        self.gps_accuracy_threshold = 10.0  # meters
        self.location_cache = {}
        
        # Field session management
        self.active_sessions = {}

    async def start_field_session(
        self,
        farmer_id: UUID,
        variety_id: UUID,
        field_location: FieldLocation,
        session_type: str = "performance_tracking"
    ) -> MobileFieldSession:
        """
        Start a new field tracking session for mobile app.
        
        Args:
            farmer_id: Unique identifier for the farmer
            variety_id: Unique identifier for the variety
            field_location: GPS location of the field
            session_type: Type of tracking session
            
        Returns:
            Mobile field session with session ID and initial data
        """
        try:
            # Validate GPS location
            if not await self._validate_gps_location(field_location.gps_reading):
                raise ValueError("Invalid GPS location data")
            
            # Create field session
            session = MobileFieldSession(
                session_id=UUID(),
                farmer_id=farmer_id,
                variety_id=variety_id,
                field_location=field_location,
                session_type=session_type,
                start_time=datetime.utcnow(),
                status="active",
                offline_mode=False,
                data_collected={}
            )
            
            # Store active session
            self.active_sessions[str(session.session_id)] = session
            
            # Initialize field boundary if provided
            if field_location.field_boundary:
                await self._validate_field_boundary(field_location.field_boundary)
            
            logger.info(f"Started field session {session.session_id} for farmer {farmer_id}")
            return session
            
        except Exception as e:
            logger.error(f"Error starting field session: {str(e)}")
            raise

    async def collect_field_data(
        self,
        session_id: UUID,
        data_type: str,
        data_value: Any,
        gps_reading: Optional[GPSReading] = None,
        photo_data: Optional[CropPhoto] = None,
        field_note: Optional[FieldNote] = None
    ) -> bool:
        """
        Collect field data during an active session.
        
        Args:
            session_id: Active session identifier
            data_type: Type of data being collected
            data_value: The data value
            gps_reading: Optional GPS reading for location context
            photo_data: Optional crop photo data
            field_note: Optional field note
            
        Returns:
            Success status of data collection
        """
        try:
            session = self.active_sessions.get(str(session_id))
            if not session:
                raise ValueError(f"Active session {session_id} not found")
            
            # Validate GPS reading if provided
            if gps_reading and not await self._validate_gps_reading(gps_reading):
                logger.warning(f"Invalid GPS reading for session {session_id}")
                return False
            
            # Create data entry
            data_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "data_type": data_type,
                "data_value": data_value,
                "gps_reading": gps_reading.dict() if gps_reading else None,
                "photo_data": photo_data.dict() if photo_data else None,
                "field_note": field_note.dict() if field_note else None,
                "offline_collected": session.offline_mode
            }
            
            # Add to session data
            if data_type not in session.data_collected:
                session.data_collected[data_type] = []
            session.data_collected[data_type].append(data_entry)
            
            # Store in offline storage if in offline mode
            if session.offline_mode:
                await self._store_offline_data(session_id, data_entry)
            
            logger.info(f"Collected {data_type} data for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error collecting field data: {str(e)}")
            return False

    async def end_field_session(
        self,
        session_id: UUID,
        generate_feedback_survey: bool = True
    ) -> Dict[str, Any]:
        """
        End a field tracking session and generate farmer feedback.
        
        Args:
            session_id: Session identifier to end
            generate_feedback_survey: Whether to generate feedback survey
            
        Returns:
            Session summary and generated feedback data
        """
        try:
            session = self.active_sessions.get(str(session_id))
            if not session:
                raise ValueError(f"Active session {session_id} not found")
            
            # Update session end time and status
            session.end_time = datetime.utcnow()
            session.status = "completed"
            
            # Generate session summary
            session_summary = await self._generate_session_summary(session)
            
            # Generate farmer feedback survey if requested
            feedback_survey = None
            field_performance = None
            
            if generate_feedback_survey:
                feedback_survey, field_performance = await self._generate_feedback_from_session(session)
            
            # Store session data
            await self._store_session_data(session)
            
            # Remove from active sessions
            del self.active_sessions[str(session_id)]
            
            return {
                "session_id": session_id,
                "session_summary": session_summary,
                "feedback_survey": feedback_survey.dict() if feedback_survey else None,
                "field_performance": field_performance.dict() if field_performance else None,
                "data_points_collected": sum(len(data_list) for data_list in session.data_collected.values()),
                "session_duration_minutes": (session.end_time - session.start_time).total_seconds() / 60
            }
            
        except Exception as e:
            logger.error(f"Error ending field session: {str(e)}")
            raise

    async def sync_offline_data(
        self,
        farmer_id: UUID,
        offline_data: List[OfflineDataEntry]
    ) -> SyncStatus:
        """
        Synchronize offline data with the server.
        
        Args:
            farmer_id: Farmer identifier
            offline_data: List of offline data entries to sync
            
        Returns:
            Sync status with success/failure details
        """
        try:
            sync_status = SyncStatus(
                farmer_id=farmer_id,
                sync_timestamp=datetime.utcnow(),
                total_entries=len(offline_data),
                successful_syncs=0,
                failed_syncs=0,
                sync_errors=[]
            )
            
            for entry in offline_data:
                try:
                    # Validate offline entry
                    if not await self._validate_offline_entry(entry):
                        sync_status.failed_syncs += 1
                        sync_status.sync_errors.append(f"Invalid entry: {entry.entry_id}")
                        continue
                    
                    # Process entry based on type
                    if entry.entry_type == "field_session":
                        await self._sync_field_session(entry)
                    elif entry.entry_type == "field_data":
                        await self._sync_field_data(entry)
                    elif entry.entry_type == "feedback_survey":
                        await self._sync_feedback_survey(entry)
                    else:
                        sync_status.failed_syncs += 1
                        sync_status.sync_errors.append(f"Unknown entry type: {entry.entry_type}")
                        continue
                    
                    sync_status.successful_syncs += 1
                    
                except Exception as e:
                    sync_status.failed_syncs += 1
                    sync_status.sync_errors.append(f"Sync error for {entry.entry_id}: {str(e)}")
            
            # Calculate sync success rate
            sync_status.success_rate = (
                sync_status.successful_syncs / sync_status.total_entries 
                if sync_status.total_entries > 0 else 0.0
            )
            
            logger.info(f"Offline sync completed for farmer {farmer_id}: {sync_status.successful_syncs}/{sync_status.total_entries} successful")
            return sync_status
            
        except Exception as e:
            logger.error(f"Error syncing offline data: {str(e)}")
            raise

    async def get_field_boundaries(
        self,
        farmer_id: UUID,
        variety_id: Optional[UUID] = None
    ) -> List[FieldBoundary]:
        """
        Get field boundaries for a farmer, optionally filtered by variety.
        
        Args:
            farmer_id: Farmer identifier
            variety_id: Optional variety filter
            
        Returns:
            List of field boundaries
        """
        try:
            # Query field boundaries from database
            boundaries = await self._query_field_boundaries(farmer_id, variety_id)
            
            # Add GPS validation
            validated_boundaries = []
            for boundary in boundaries:
                if await self._validate_field_boundary(boundary):
                    validated_boundaries.append(boundary)
                else:
                    logger.warning(f"Invalid field boundary {boundary.boundary_id}")
            
            return validated_boundaries
            
        except Exception as e:
            logger.error(f"Error getting field boundaries: {str(e)}")
            raise

    async def capture_crop_photo(
        self,
        session_id: UUID,
        photo_data: CropPhoto,
        gps_reading: GPSReading
    ) -> bool:
        """
        Capture and process crop photo with GPS location.
        
        Args:
            session_id: Active session identifier
            photo_data: Crop photo data
            gps_reading: GPS reading for location context
            
        Returns:
            Success status of photo capture
        """
        try:
            # Validate GPS reading
            if not await self._validate_gps_reading(gps_reading):
                logger.warning("Invalid GPS reading for crop photo")
                return False
            
            # Validate photo data
            if not await self._validate_crop_photo(photo_data):
                logger.warning("Invalid crop photo data")
                return False
            
            # Add GPS metadata to photo
            photo_data.gps_location = gps_reading
            photo_data.capture_timestamp = datetime.utcnow()
            
            # Store photo data in session
            success = await self.collect_field_data(
                session_id=session_id,
                data_type="crop_photo",
                data_value=photo_data.dict(),
                gps_reading=gps_reading,
                photo_data=photo_data
            )
            
            if success:
                logger.info(f"Crop photo captured for session {session_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error capturing crop photo: {str(e)}")
            return False

    async def add_field_note(
        self,
        session_id: UUID,
        field_note: FieldNote,
        gps_reading: Optional[GPSReading] = None
    ) -> bool:
        """
        Add a field note with optional GPS location.
        
        Args:
            session_id: Active session identifier
            field_note: Field note data
            gps_reading: Optional GPS reading for location context
            
        Returns:
            Success status of note addition
        """
        try:
            # Validate GPS reading if provided
            if gps_reading and not await self._validate_gps_reading(gps_reading):
                logger.warning("Invalid GPS reading for field note")
                return False
            
            # Add timestamp to note
            field_note.timestamp = datetime.utcnow()
            
            # Store note data in session
            success = await self.collect_field_data(
                session_id=session_id,
                data_type="field_note",
                data_value=field_note.dict(),
                gps_reading=gps_reading,
                field_note=field_note
            )
            
            if success:
                logger.info(f"Field note added for session {session_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error adding field note: {str(e)}")
            return False

    async def _validate_gps_location(self, gps_reading: GPSReading) -> bool:
        """Validate GPS location data."""
        try:
            # Check coordinate ranges
            if not (-90 <= gps_reading.latitude <= 90):
                return False
            if not (-180 <= gps_reading.longitude <= 180):
                return False
            
            # Check accuracy threshold
            if gps_reading.accuracy > self.gps_accuracy_threshold:
                return False
            
            # Check timestamp
            if gps_reading.timestamp > datetime.utcnow():
                return False
            
            return True
            
        except Exception:
            return False

    async def _validate_gps_reading(self, gps_reading: GPSReading) -> bool:
        """Validate GPS reading data."""
        return await self._validate_gps_location(gps_reading)

    async def _validate_field_boundary(self, boundary: FieldBoundary) -> bool:
        """Validate field boundary data."""
        try:
            # Check boundary has at least 3 points (triangle minimum)
            if len(boundary.boundary_points) < 3:
                return False
            
            # Validate each GPS point
            for point in boundary.boundary_points:
                if not await self._validate_gps_location(point):
                    return False
            
            # Check boundary area is reasonable (not too small or too large)
            area = await self._calculate_boundary_area(boundary)
            if area < 0.1 or area > 10000:  # 0.1 to 10,000 acres
                return False
            
            return True
            
        except Exception:
            return False

    async def _validate_crop_photo(self, photo_data: CropPhoto) -> bool:
        """Validate crop photo data."""
        try:
            # Check required fields
            if not photo_data.photo_data or not photo_data.photo_format:
                return False
            
            # Check photo format
            if photo_data.photo_format not in ["JPEG", "PNG", "HEIC"]:
                return False
            
            # Check photo size (basic validation)
            if len(photo_data.photo_data) < 1000:  # Too small
                return False
            if len(photo_data.photo_data) > 50 * 1024 * 1024:  # Too large (50MB)
                return False
            
            return True
            
        except Exception:
            return False

    async def _validate_offline_entry(self, entry: OfflineDataEntry) -> bool:
        """Validate offline data entry."""
        try:
            # Check required fields
            if not entry.entry_id or not entry.entry_type or not entry.data:
                return False
            
            # Check timestamp
            if entry.timestamp > datetime.utcnow():
                return False
            
            # Check data format
            if not isinstance(entry.data, dict):
                return False
            
            return True
            
        except Exception:
            return False

    async def _store_offline_data(self, session_id: UUID, data_entry: Dict[str, Any]) -> None:
        """Store data in offline storage."""
        try:
            offline_entry = OfflineDataEntry(
                entry_id=UUID(),
                session_id=session_id,
                entry_type="field_data",
                data=data_entry,
                timestamp=datetime.utcnow(),
                sync_status="pending"
            )
            
            self.offline_storage[str(offline_entry.entry_id)] = offline_entry
            self.sync_queue.append(offline_entry)
            
        except Exception as e:
            logger.error(f"Error storing offline data: {str(e)}")

    async def _generate_session_summary(self, session: MobileFieldSession) -> Dict[str, Any]:
        """Generate summary of field session data."""
        summary = {
            "session_id": str(session.session_id),
            "farmer_id": str(session.farmer_id),
            "variety_id": str(session.variety_id),
            "session_type": session.session_type,
            "start_time": session.start_time.isoformat(),
            "end_time": session.end_time.isoformat(),
            "duration_minutes": (session.end_time - session.start_time).total_seconds() / 60,
            "data_types_collected": list(session.data_collected.keys()),
            "total_data_points": sum(len(data_list) for data_list in session.data_collected.values()),
            "field_location": session.field_location.dict(),
            "offline_mode": session.offline_mode
        }
        
        return summary

    async def _generate_feedback_from_session(
        self, 
        session: MobileFieldSession
    ) -> Tuple[FarmerFeedbackSurvey, FieldPerformanceData]:
        """Generate farmer feedback survey from session data."""
        try:
            # Extract yield data if available
            yield_data = session.data_collected.get("yield_measurement", [])
            actual_yield = None
            if yield_data:
                # Calculate average yield from measurements
                yields = [entry["data_value"] for entry in yield_data if isinstance(entry["data_value"], (int, float))]
                if yields:
                    actual_yield = sum(yields) / len(yields)
            
            # Extract field performance data
            field_performance = FieldPerformanceData(
                actual_yield=actual_yield,
                field_size_acres=session.field_location.field_size_acres,
                planting_date=session.data_collected.get("planting_date", [{}])[0].get("data_value") if session.data_collected.get("planting_date") else None,
                harvest_date=session.data_collected.get("harvest_date", [{}])[0].get("data_value") if session.data_collected.get("harvest_date") else None,
                soil_type=session.data_collected.get("soil_type", [{}])[0].get("data_value") if session.data_collected.get("soil_type") else None,
                weather_conditions=session.data_collected.get("weather_conditions", [{}])[0].get("data_value") if session.data_collected.get("weather_conditions") else None
            )
            
            # Generate survey based on collected data
            # This would use AI/ML to generate appropriate ratings based on data
            survey = FarmerFeedbackSurvey(
                yield_rating=4.0,  # Placeholder - would be calculated from actual data
                disease_resistance_rating=4.0,  # Placeholder
                management_ease_rating=3.5,  # Placeholder
                overall_satisfaction=4.0,  # Placeholder
                market_performance_rating=3.5,  # Placeholder
                comments="Generated from field session data",
                additional_notes="Data collected via mobile app",
                growing_season=str(session.start_time.year),
                field_conditions=field_performance.weather_conditions
            )
            
            return survey, field_performance
            
        except Exception as e:
            logger.error(f"Error generating feedback from session: {str(e)}")
            raise

    async def _store_session_data(self, session: MobileFieldSession) -> None:
        """Store session data in database."""
        try:
            if not self.database_available:
                return
            
            # Store session data (implementation depends on database schema)
            logger.info(f"Storing session data for session {session.session_id}")
            
        except Exception as e:
            logger.error(f"Error storing session data: {str(e)}")

    async def _sync_field_session(self, entry: OfflineDataEntry) -> None:
        """Sync field session data."""
        try:
            # Process field session data
            logger.info(f"Syncing field session {entry.entry_id}")
            
        except Exception as e:
            logger.error(f"Error syncing field session: {str(e)}")
            raise

    async def _sync_field_data(self, entry: OfflineDataEntry) -> None:
        """Sync field data."""
        try:
            # Process field data
            logger.info(f"Syncing field data {entry.entry_id}")
            
        except Exception as e:
            logger.error(f"Error syncing field data: {str(e)}")
            raise

    async def _sync_feedback_survey(self, entry: OfflineDataEntry) -> None:
        """Sync feedback survey data."""
        try:
            # Process feedback survey data
            logger.info(f"Syncing feedback survey {entry.entry_id}")
            
        except Exception as e:
            logger.error(f"Error syncing feedback survey: {str(e)}")
            raise

    async def _query_field_boundaries(
        self, 
        farmer_id: UUID, 
        variety_id: Optional[UUID]
    ) -> List[FieldBoundary]:
        """Query field boundaries from database."""
        try:
            if not self.database_available:
                return []
            
            # Query field boundaries (implementation depends on database schema)
            logger.info(f"Querying field boundaries for farmer {farmer_id}")
            return []
            
        except Exception as e:
            logger.error(f"Error querying field boundaries: {str(e)}")
            return []

    async def _calculate_boundary_area(self, boundary: FieldBoundary) -> float:
        """Calculate area of field boundary in acres."""
        try:
            # Simplified area calculation using shoelace formula
            # In production, would use proper geospatial calculations
            points = boundary.boundary_points
            if len(points) < 3:
                return 0.0
            
            # Basic area calculation (simplified)
            area = 0.0
            for i in range(len(points)):
                j = (i + 1) % len(points)
                area += points[i].longitude * points[j].latitude
                area -= points[j].longitude * points[i].latitude
            
            area = abs(area) / 2.0
            # Convert to acres (simplified conversion)
            return area * 0.000247105  # Rough conversion from square degrees to acres
            
        except Exception:
            return 0.0


# Create service instance
import os
mobile_field_tracking_service = MobileFieldTrackingService(
    database_url=os.getenv('DATABASE_URL')
)
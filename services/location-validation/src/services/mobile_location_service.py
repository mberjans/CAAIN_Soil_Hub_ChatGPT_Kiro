"""
Mobile Location Service
TICKET-008_farm-location-input-11.2: Add mobile-specific location features and capabilities

Handles business logic for:
- Field boundary recording and management
- Field photo storage with geotagging
- Voice notes for field annotations
- Offline data synchronization
"""

import logging
import json
import math
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from uuid import UUID, uuid4
import asyncio
from dataclasses import dataclass

from ..models import FieldBoundary, FieldPhoto, VoiceNote, OfflineSyncData
from ..database import get_database_connection

logger = logging.getLogger(__name__)

@dataclass
class MappingSession:
    """Represents an active field mapping session."""
    session_id: UUID
    user_id: UUID
    field_name: str
    start_location: Tuple[float, float]
    points: List[Dict[str, Any]]
    started_at: datetime
    is_active: bool = True

class MobileLocationService:
    """Service for handling mobile-specific location features."""
    
    def __init__(self):
        self.active_sessions: Dict[UUID, MappingSession] = {}
        self.db = None
    
    async def get_db(self):
        """Get database connection."""
        if not self.db:
            self.db = await get_database_connection()
        return self.db
    
    # Field Boundary Management
    async def save_field_boundary(self, boundary_data: FieldBoundary) -> Dict[str, Any]:
        """Save field boundary data with area and perimeter calculations."""
        try:
            # Calculate area and perimeter
            area_acres = self._calculate_polygon_area(boundary_data.points)
            perimeter_meters = self._calculate_polygon_perimeter(boundary_data.points)
            
            # Generate boundary ID
            boundary_id = uuid4()
            
            # Save to database
            db = await self.get_db()
            await db.execute("""
                INSERT INTO field_boundaries (
                    id, user_id, field_name, points, area_acres, perimeter_meters,
                    point_count, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """, 
                boundary_id,
                boundary_data.user_id,
                boundary_data.field_name,
                json.dumps(boundary_data.points),
                area_acres,
                perimeter_meters,
                len(boundary_data.points),
                datetime.utcnow(),
                datetime.utcnow()
            )
            
            logger.info(f"Saved field boundary {boundary_id} with {len(boundary_data.points)} points")
            
            return {
                "boundary_id": boundary_id,
                "area_acres": area_acres,
                "perimeter_meters": perimeter_meters,
                "point_count": len(boundary_data.points)
            }
            
        except Exception as e:
            logger.error(f"Error saving field boundary: {e}")
            raise
    
    async def get_user_field_boundaries(self, user_id: UUID) -> List[FieldBoundary]:
        """Retrieve all field boundaries for a user."""
        try:
            db = await self.get_db()
            rows = await db.fetch("""
                SELECT id, field_name, points, area_acres, perimeter_meters,
                       point_count, created_at, updated_at
                FROM field_boundaries
                WHERE user_id = $1
                ORDER BY created_at DESC
            """, user_id)
            
            boundaries = []
            for row in rows:
                boundary = FieldBoundary(
                    id=row['id'],
                    user_id=user_id,
                    field_name=row['field_name'],
                    points=json.loads(row['points']),
                    area_acres=row['area_acres'],
                    perimeter_meters=row['perimeter_meters'],
                    point_count=row['point_count'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
                boundaries.append(boundary)
            
            return boundaries
            
        except Exception as e:
            logger.error(f"Error retrieving field boundaries: {e}")
            raise
    
    # Field Photo Management
    async def save_field_photo(self, field_photo: FieldPhoto) -> Dict[str, Any]:
        """Save field photo with geotagging information."""
        try:
            photo_id = uuid4()
            
            # Save to database
            db = await self.get_db()
            await db.execute("""
                INSERT INTO field_photos (
                    id, user_id, field_id, photo_data, latitude, longitude,
                    accuracy, notes, file_type, captured_at, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            """,
                photo_id,
                field_photo.user_id,
                field_photo.field_id,
                field_photo.photo_data,
                field_photo.latitude,
                field_photo.longitude,
                field_photo.accuracy,
                field_photo.notes,
                field_photo.file_type,
                field_photo.captured_at,
                datetime.utcnow()
            )
            
            logger.info(f"Saved field photo {photo_id} at {field_photo.latitude}, {field_photo.longitude}")
            
            return {
                "photo_id": photo_id,
                "location": {
                    "latitude": field_photo.latitude,
                    "longitude": field_photo.longitude,
                    "accuracy": field_photo.accuracy
                }
            }
            
        except Exception as e:
            logger.error(f"Error saving field photo: {e}")
            raise
    
    async def get_user_field_photos(self, user_id: UUID, field_id: Optional[str] = None) -> List[FieldPhoto]:
        """Retrieve field photos for a user."""
        try:
            db = await self.get_db()
            
            if field_id:
                rows = await db.fetch("""
                    SELECT id, field_id, latitude, longitude, accuracy, notes,
                           file_type, captured_at, created_at
                    FROM field_photos
                    WHERE user_id = $1 AND field_id = $2
                    ORDER BY captured_at DESC
                """, user_id, field_id)
            else:
                rows = await db.fetch("""
                    SELECT id, field_id, latitude, longitude, accuracy, notes,
                           file_type, captured_at, created_at
                    FROM field_photos
                    WHERE user_id = $1
                    ORDER BY captured_at DESC
                """, user_id)
            
            photos = []
            for row in rows:
                photo = FieldPhoto(
                    id=row['id'],
                    user_id=user_id,
                    field_id=row['field_id'],
                    photo_data=b'',  # Don't load image data in list view
                    latitude=row['latitude'],
                    longitude=row['longitude'],
                    accuracy=row['accuracy'],
                    notes=row['notes'],
                    file_type=row['file_type'],
                    captured_at=row['captured_at'],
                    created_at=row['created_at']
                )
                photos.append(photo)
            
            return photos
            
        except Exception as e:
            logger.error(f"Error retrieving field photos: {e}")
            raise
    
    async def get_field_photo_image(self, photo_id: UUID) -> Optional[Dict[str, Any]]:
        """Retrieve the actual image data for a field photo."""
        try:
            db = await self.get_db()
            row = await db.fetchrow("""
                SELECT photo_data, file_type
                FROM field_photos
                WHERE id = $1
            """, photo_id)
            
            if not row:
                return None
            
            return {
                "image": row['photo_data'],
                "content_type": row['file_type']
            }
            
        except Exception as e:
            logger.error(f"Error retrieving field photo image: {e}")
            raise
    
    # Voice Notes Management
    async def save_voice_note(self, voice_note: VoiceNote) -> Dict[str, Any]:
        """Save voice note with geotagging information."""
        try:
            voice_note_id = uuid4()
            
            # Save to database
            db = await self.get_db()
            await db.execute("""
                INSERT INTO voice_notes (
                    id, user_id, field_id, audio_data, latitude, longitude,
                    accuracy, duration, notes, file_type, recorded_at, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            """,
                voice_note_id,
                voice_note.user_id,
                voice_note.field_id,
                voice_note.audio_data,
                voice_note.latitude,
                voice_note.longitude,
                voice_note.accuracy,
                voice_note.duration,
                voice_note.notes,
                voice_note.file_type,
                voice_note.recorded_at,
                datetime.utcnow()
            )
            
            logger.info(f"Saved voice note {voice_note_id} at {voice_note.latitude}, {voice_note.longitude}")
            
            return {
                "voice_note_id": voice_note_id,
                "location": {
                    "latitude": voice_note.latitude,
                    "longitude": voice_note.longitude,
                    "accuracy": voice_note.accuracy
                },
                "duration": voice_note.duration
            }
            
        except Exception as e:
            logger.error(f"Error saving voice note: {e}")
            raise
    
    async def get_user_voice_notes(self, user_id: UUID, field_id: Optional[str] = None) -> List[VoiceNote]:
        """Retrieve voice notes for a user."""
        try:
            db = await self.get_db()
            
            if field_id:
                rows = await db.fetch("""
                    SELECT id, field_id, latitude, longitude, accuracy, duration,
                           notes, file_type, recorded_at, created_at
                    FROM voice_notes
                    WHERE user_id = $1 AND field_id = $2
                    ORDER BY recorded_at DESC
                """, user_id, field_id)
            else:
                rows = await db.fetch("""
                    SELECT id, field_id, latitude, longitude, accuracy, duration,
                           notes, file_type, recorded_at, created_at
                    FROM voice_notes
                    WHERE user_id = $1
                    ORDER BY recorded_at DESC
                """, user_id)
            
            voice_notes = []
            for row in rows:
                voice_note = VoiceNote(
                    id=row['id'],
                    user_id=user_id,
                    field_id=row['field_id'],
                    audio_data=b'',  # Don't load audio data in list view
                    latitude=row['latitude'],
                    longitude=row['longitude'],
                    accuracy=row['accuracy'],
                    duration=row['duration'],
                    notes=row['notes'],
                    file_type=row['file_type'],
                    recorded_at=row['recorded_at'],
                    created_at=row['created_at']
                )
                voice_notes.append(voice_note)
            
            return voice_notes
            
        except Exception as e:
            logger.error(f"Error retrieving voice notes: {e}")
            raise
    
    async def get_voice_note_audio(self, voice_note_id: UUID) -> Optional[Dict[str, Any]]:
        """Retrieve the actual audio data for a voice note."""
        try:
            db = await self.get_db()
            row = await db.fetchrow("""
                SELECT audio_data, file_type
                FROM voice_notes
                WHERE id = $1
            """, voice_note_id)
            
            if not row:
                return None
            
            return {
                "audio": row['audio_data'],
                "content_type": row['file_type']
            }
            
        except Exception as e:
            logger.error(f"Error retrieving voice note audio: {e}")
            raise
    
    # Offline Data Synchronization
    async def sync_offline_data(self, sync_data: List[OfflineSyncData]) -> Dict[str, Any]:
        """Synchronize offline data collected on mobile devices."""
        try:
            synced_items = 0
            failed_items = 0
            
            for item in sync_data:
                try:
                    if item.data_type == "boundary":
                        await self._sync_boundary_data(item.data)
                    elif item.data_type == "photo":
                        await self._sync_photo_data(item.data)
                    elif item.data_type == "voice_note":
                        await self._sync_voice_note_data(item.data)
                    else:
                        logger.warning(f"Unknown data type: {item.data_type}")
                        failed_items += 1
                        continue
                    
                    synced_items += 1
                    
                except Exception as e:
                    logger.error(f"Error syncing item {item.id}: {e}")
                    failed_items += 1
            
            logger.info(f"Synced {synced_items} items, {failed_items} failed")
            
            return {
                "synced_items": synced_items,
                "failed_items": failed_items
            }
            
        except Exception as e:
            logger.error(f"Error syncing offline data: {e}")
            raise
    
    async def get_offline_sync_status(self, user_id: UUID) -> Dict[str, Any]:
        """Get synchronization status for offline data."""
        try:
            db = await self.get_db()
            
            # Count pending sync items
            pending_count = await db.fetchval("""
                SELECT COUNT(*) FROM offline_sync_queue
                WHERE user_id = $1 AND synced_at IS NULL
            """, user_id)
            
            # Get last sync time
            last_sync = await db.fetchval("""
                SELECT MAX(synced_at) FROM offline_sync_queue
                WHERE user_id = $1 AND synced_at IS NOT NULL
            """, user_id)
            
            return {
                "user_id": str(user_id),
                "pending_items": pending_count,
                "last_sync": last_sync,
                "status": "pending" if pending_count > 0 else "synced"
            }
            
        except Exception as e:
            logger.error(f"Error getting offline sync status: {e}")
            raise
    
    # Field Mapping Session Management
    async def start_field_mapping_session(
        self, 
        user_id: UUID, 
        field_name: str, 
        latitude: float, 
        longitude: float
    ) -> UUID:
        """Start a new field mapping session."""
        try:
            session_id = uuid4()
            session = MappingSession(
                session_id=session_id,
                user_id=user_id,
                field_name=field_name,
                start_location=(latitude, longitude),
                points=[],
                started_at=datetime.utcnow()
            )
            
            self.active_sessions[session_id] = session
            
            logger.info(f"Started field mapping session {session_id} for user {user_id}")
            
            return session_id
            
        except Exception as e:
            logger.error(f"Error starting field mapping session: {e}")
            raise
    
    async def add_mapping_point(
        self, 
        session_id: UUID, 
        latitude: float, 
        longitude: float,
        accuracy: Optional[float] = None,
        altitude: Optional[float] = None
    ) -> Dict[str, Any]:
        """Add a GPS point to the current field mapping session."""
        try:
            if session_id not in self.active_sessions:
                raise ValueError("Invalid or expired mapping session")
            
            session = self.active_sessions[session_id]
            
            point = {
                "latitude": latitude,
                "longitude": longitude,
                "accuracy": accuracy,
                "altitude": altitude,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            session.points.append(point)
            
            # Calculate estimated area if we have enough points
            estimated_area = 0
            if len(session.points) > 2:
                estimated_area = self._calculate_polygon_area(session.points)
            
            return {
                "point_count": len(session.points),
                "estimated_area": estimated_area
            }
            
        except Exception as e:
            logger.error(f"Error adding mapping point: {e}")
            raise
    
    async def complete_field_mapping(self, session_id: UUID) -> Dict[str, Any]:
        """Complete the field mapping session and calculate final boundary."""
        try:
            if session_id not in self.active_sessions:
                raise ValueError("Invalid or expired mapping session")
            
            session = self.active_sessions[session_id]
            
            if len(session.points) < 3:
                raise ValueError("Not enough points to create a valid boundary")
            
            # Calculate final area and perimeter
            final_area = self._calculate_polygon_area(session.points)
            final_perimeter = self._calculate_polygon_perimeter(session.points)
            
            # Create boundary data
            boundary_data = FieldBoundary(
                id=uuid4(),
                user_id=session.user_id,
                field_name=session.field_name,
                points=session.points,
                area_acres=final_area,
                perimeter_meters=final_perimeter,
                point_count=len(session.points),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Save boundary
            result = await self.save_field_boundary(boundary_data)
            
            # Mark session as completed
            session.is_active = False
            del self.active_sessions[session_id]
            
            logger.info(f"Completed field mapping session {session_id} with {len(session.points)} points")
            
            return {
                "boundary_id": result["boundary_id"],
                "final_area": final_area,
                "final_perimeter": final_perimeter,
                "point_count": len(session.points)
            }
            
        except Exception as e:
            logger.error(f"Error completing field mapping: {e}")
            raise
    
    # Helper Methods
    def _calculate_polygon_area(self, points: List[Dict[str, Any]]) -> float:
        """Calculate polygon area using the shoelace formula."""
        if len(points) < 3:
            return 0.0
        
        n = len(points)
        area = 0.0
        
        for i in range(n):
            j = (i + 1) % n
            area += points[i]['longitude'] * points[j]['latitude']
            area -= points[j]['longitude'] * points[i]['latitude']
        
        area = abs(area) / 2.0
        
        # Convert from square degrees to acres (approximate)
        # This is a simplified conversion - in production, use proper projection
        meters_per_degree = 111320  # Approximate meters per degree at equator
        square_meters = area * (meters_per_degree ** 2)
        acres = square_meters / 4046.86  # Convert square meters to acres
        
        return acres
    
    def _calculate_polygon_perimeter(self, points: List[Dict[str, Any]]) -> float:
        """Calculate polygon perimeter in meters."""
        if len(points) < 2:
            return 0.0
        
        perimeter = 0.0
        for i in range(len(points)):
            j = (i + 1) % len(points)
            distance = self._calculate_distance(
                points[i]['latitude'], points[i]['longitude'],
                points[j]['latitude'], points[j]['longitude']
            )
            perimeter += distance
        
        return perimeter
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula."""
        R = 6371000  # Earth's radius in meters
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat/2) * math.sin(dlat/2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon/2) * math.sin(dlon/2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    async def _sync_boundary_data(self, data: Dict[str, Any]):
        """Sync boundary data from offline storage."""
        boundary = FieldBoundary(**data)
        await self.save_field_boundary(boundary)
    
    async def _sync_photo_data(self, data: Dict[str, Any]):
        """Sync photo data from offline storage."""
        photo = FieldPhoto(**data)
        await self.save_field_photo(photo)
    
    async def _sync_voice_note_data(self, data: Dict[str, Any]):
        """Sync voice note data from offline storage."""
        voice_note = VoiceNote(**data)
        await self.save_voice_note(voice_note)
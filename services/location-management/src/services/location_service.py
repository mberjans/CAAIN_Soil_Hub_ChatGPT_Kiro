from sqlalchemy.orm import Session
from sqlalchemy import and_
from geoalchemy2.functions import ST_DWithin, ST_GeomFromText
from src.models.location_models import FarmLocation, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LocationService:
    """Service for managing locations with geospatial queries"""
    
    def __init__(self, db_session: Session):
        """Initialize location service with database session"""
        self.db = db_session
    
    def create_location(
        self,
        user_id: UUID,
        name: str,
        latitude: float,
        longitude: float,
        address: Optional[str] = None,
        elevation_meters: Optional[int] = None,
        usda_zone: Optional[str] = None,
        climate_zone: Optional[str] = None,
        county: Optional[str] = None,
        state: Optional[str] = None,
        country: Optional[str] = 'USA',
        total_acres: Optional[float] = None,
        is_primary: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new farm location.
        
        Args:
            user_id: User UUID
            name: Location name
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            address: Optional address string
            elevation_meters: Optional elevation
            usda_zone: Optional USDA hardiness zone
            climate_zone: Optional climate zone
            county: Optional county
            state: Optional state
            country: Optional country (default USA)
            total_acres: Optional total acres
            is_primary: Whether this is primary location
            
        Returns:
            Dictionary with created location details or None if failed
        """
        if not self._validate_gps_coordinates(latitude, longitude):
            logger.warning(f"Invalid GPS coordinates: ({latitude}, {longitude})")
            return None
        
        try:
            point = f"POINT({longitude} {latitude})"
            
            location = FarmLocation(
                user_id=user_id,
                name=name,
                address=address,
                coordinates=ST_GeomFromText(point, 4326),
                elevation_meters=elevation_meters,
                usda_zone=usda_zone,
                climate_zone=climate_zone,
                county=county,
                state=state,
                country=country,
                total_acres=total_acres,
                is_primary=is_primary
            )
            
            self.db.add(location)
            self.db.commit()
            
            logger.info(f"Created location: {name} for user {user_id}")
            
            return {
                'id': str(location.id),
                'user_id': str(location.user_id),
                'name': location.name,
                'latitude': latitude,
                'longitude': longitude,
                'address': location.address
            }
        except Exception as e:
            logger.error(f"Error creating location: {str(e)}")
            self.db.rollback()
            return None
    
    def find_nearby_locations(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 50.0,
        user_id: Optional[UUID] = None
    ) -> List[Dict[str, Any]]:
        """
        Find locations within specified distance using PostGIS ST_DWithin.
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius_km: Search radius in kilometers
            user_id: Optional filter by specific user
            
        Returns:
            List of nearby locations
        """
        if not self._validate_gps_coordinates(latitude, longitude):
            logger.warning(f"Invalid GPS coordinates: ({latitude}, {longitude})")
            return []
        
        try:
            point = f"POINT({longitude} {latitude})"
            
            query = self.db.query(FarmLocation).filter(
                ST_DWithin(
                    FarmLocation.coordinates,
                    ST_GeomFromText(point, 4326),
                    radius_km * 1000
                )
            )
            
            if user_id:
                query = query.filter(FarmLocation.user_id == user_id)
            
            locations = query.all()
            
            results = []
            for loc in locations:
                results.append({
                    'id': str(loc.id),
                    'user_id': str(loc.user_id),
                    'name': loc.name,
                    'latitude': loc.coordinates.x,
                    'longitude': loc.coordinates.y,
                    'address': loc.address
                })
            
            logger.info(f"Found {len(results)} nearby locations")
            return results
        except Exception as e:
            logger.error(f"Error finding nearby locations: {str(e)}")
            return []
    
    def get_user_locations(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get all locations for a user.
        
        Args:
            user_id: User UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of user's locations
        """
        try:
            locations = self.db.query(FarmLocation).filter(
                FarmLocation.user_id == user_id
            ).offset(skip).limit(limit).all()
            
            results = []
            for loc in locations:
                results.append({
                    'id': str(loc.id),
                    'user_id': str(loc.user_id),
                    'name': loc.name,
                    'latitude': loc.coordinates.x,
                    'longitude': loc.coordinates.y,
                    'address': loc.address,
                    'is_primary': loc.is_primary
                })
            
            logger.info(f"Retrieved {len(results)} locations for user {user_id}")
            return results
        except Exception as e:
            logger.error(f"Error retrieving user locations: {str(e)}")
            return []
    
    def _validate_gps_coordinates(self, latitude: float, longitude: float) -> bool:
        """
        Validate GPS coordinates.
        
        Args:
            latitude: Latitude value
            longitude: Longitude value
            
        Returns:
            True if valid, False otherwise
        """
        try:
            lat = float(latitude)
            lon = float(longitude)
            
            if not (-90 <= lat <= 90):
                logger.warning(f"Latitude out of range: {lat}")
                return False
            
            if not (-180 <= lon <= 180):
                logger.warning(f"Longitude out of range: {lon}")
                return False
            
            return True
        except (TypeError, ValueError) as e:
            logger.warning(f"Invalid coordinate types: {str(e)}")
            return False

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from src.schemas.location_schemas import LocationCreate, LocationResponse, NearbySearchRequest
from src.services.location_service import LocationService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/locations", tags=["locations"])


def get_db_session() -> Session:
    """Dependency to get database session"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    db_url = 'postgresql://Mark@localhost:5432/caain_soil_hub'
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


@router.post("/", response_model=dict, status_code=201)
async def create_location(
    location: LocationCreate,
    db_session: Session = Depends(get_db_session)
):
    """Create a new farm location"""
    try:
        service = LocationService(db_session)
        result = service.create_location(
            user_id=UUID('00000000-0000-0000-0000-000000000001'),
            name=location.name,
            latitude=location.latitude,
            longitude=location.longitude,
            address=location.address,
            elevation_meters=location.elevation_meters,
            usda_zone=location.usda_zone,
            climate_zone=location.climate_zone,
            county=location.county,
            state=location.state,
            country=location.country,
            total_acres=location.total_acres
        )
        
        if result:
            return result
        else:
            raise HTTPException(status_code=400, detail="Failed to create location")
    except Exception as e:
        logger.error(f"Error creating location: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/nearby", response_model=list)
async def nearby_locations(
    latitude: float = Query(...),
    longitude: float = Query(...),
    radius_km: float = Query(50.0),
    db_session: Session = Depends(get_db_session)
):
    """Find locations nearby"""
    try:
        service = LocationService(db_session)
        results = service.find_nearby_locations(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km
        )
        return results
    except Exception as e:
        logger.error(f"Error finding nearby locations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{location_id}", response_model=dict)
async def get_location(
    location_id: UUID,
    db_session: Session = Depends(get_db_session)
):
    """Get a specific location by ID"""
    try:
        from src.models.location_models import FarmLocation
        
        location = db_session.query(FarmLocation).filter(
            FarmLocation.id == location_id
        ).first()
        
        if location:
            return {
                'id': str(location.id),
                'user_id': str(location.user_id),
                'name': location.name,
                'latitude': location.coordinates.x,
                'longitude': location.coordinates.y,
                'address': location.address
            }
        else:
            raise HTTPException(status_code=404, detail="Location not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving location: {str(e)}")
        raise HTTPException(status_code=404, detail="Location not found")

#!/usr/bin/env python3
"""
Standalone Planting Date Service for Testing
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime, date
import uvicorn
import sys
import os

# Add the service path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'services', 'recommendation-engine', 'src'))

app = FastAPI(title="Planting Date Service", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class LocationData(BaseModel):
    latitude: float
    longitude: float
    elevation_ft: Optional[float] = 1000
    address: Optional[str] = "Farm Location"
    state: Optional[str] = "Iowa"
    county: Optional[str] = "Story"
    climate_zone: Optional[str] = "5b"
    climate_zone_name: Optional[str] = "USDA Zone 5b"
    temperature_range_f: Optional[Dict[str, float]] = {"min": -15, "max": -10}
    climate_confidence: Optional[float] = 0.85

class PlantingDateRequest(BaseModel):
    crop_name: str
    location: LocationData
    planting_season: str = "spring"

class FrostDateRequest(BaseModel):
    location: LocationData

# Mock planting date service responses
DEFAULT_PLANTING_DATA = {
    "corn": {
        "optimal_date": "2024-05-05",
        "earliest_safe_date": "2024-04-20",
        "latest_safe_date": "2024-05-20",
        "days_to_maturity": 110,
        "frost_considerations": ["Plant after soil temperature reaches 50°F"],
        "climate_warnings": ["Monitor for late spring frost"]
    },
    "soybean": {
        "optimal_date": "2024-05-15",
        "earliest_safe_date": "2024-05-01",
        "latest_safe_date": "2024-06-01",
        "days_to_maturity": 105,
        "frost_considerations": ["Plant after last frost date"],
        "climate_warnings": ["Ensure adequate soil moisture"]
    },
    "wheat": {
        "optimal_date": "2024-09-25",
        "earliest_safe_date": "2024-09-15",
        "latest_safe_date": "2024-10-05",
        "days_to_maturity": 240,
        "frost_considerations": ["Winter wheat - plant for spring harvest"],
        "climate_warnings": ["Ensure good soil drainage for winter survival"]
    },
    "lettuce": {
        "optimal_date": "2024-04-01",
        "earliest_safe_date": "2024-03-15",
        "latest_safe_date": "2024-04-15",
        "days_to_maturity": 65,
        "frost_considerations": ["Cool season crop - tolerates light frost"],
        "climate_warnings": ["Provide shade in hot weather"]
    },
    "tomato": {
        "optimal_date": "2024-05-20",
        "earliest_safe_date": "2024-05-10",
        "latest_safe_date": "2024-06-01",
        "days_to_maturity": 85,
        "frost_considerations": ["Very frost sensitive - plant well after last frost"],
        "climate_warnings": ["Provide consistent water and support"]
    },
    "potato": {
        "optimal_date": "2024-04-15",
        "earliest_safe_date": "2024-04-01",
        "latest_safe_date": "2024-05-01",
        "days_to_maturity": 90,
        "frost_considerations": ["Plant when soil can be worked"],
        "climate_warnings": ["Hill soil as plants grow"]
    }
}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "planting-date", "timestamp": datetime.now()}

@app.post("/api/v1/planting/calculate-dates")
async def calculate_planting_dates(request: PlantingDateRequest):
    """Calculate optimal planting dates for a crop."""
    crop_name = request.crop_name.lower()
    
    if crop_name not in DEFAULT_PLANTING_DATA:
        raise HTTPException(status_code=404, detail=f"Crop '{crop_name}' not found in database")
    
    crop_data = DEFAULT_PLANTING_DATA[crop_name].copy()
    
    # Adjust dates based on climate zone (simplified)
    zone = request.location.climate_zone or "5b"
    zone_num = float(zone[:-1]) if zone and zone[:-1].replace('.', '').isdigit() else 5.0
    
    # Adjust planting dates based on zone (days offset)
    zone_offset = int((zone_num - 5.0) * 7)  # 7 days per zone difference
    
    # Apply zone adjustment to dates
    for date_field in ["optimal_date", "earliest_safe_date", "latest_safe_date"]:
        if crop_data[date_field]:
            try:
                original_date = datetime.fromisoformat(crop_data[date_field])
                adjusted_date = original_date.replace(day=max(1, min(31, original_date.day + zone_offset)))
                crop_data[date_field] = adjusted_date.isoformat()
            except:
                pass
    
    return {
        "success": True,
        "crop_name": crop_name,
        "planting_season": request.planting_season,
        **crop_data,
        "confidence_score": 0.85,
        "location_info": {
            "climate_zone": zone,
            "state": request.location.state
        }
    }

@app.post("/api/v1/planting/frost-dates") 
async def get_frost_dates(request: FrostDateRequest):
    """Get frost date information for a location."""
    zone = request.location.climate_zone or "5b"
    zone_num = float(zone[:-1]) if zone and zone[:-1].replace('.', '').isdigit() else 5.0
    
    # Calculate frost dates based on zone
    # Zone 3: Late May/Early September
    # Zone 5: Mid April/Mid-Late October  
    # Zone 7: Early April/Late October
    
    base_last_frost_day = 105 - int((zone_num - 3) * 10)  # April 15 for Zone 5
    base_first_frost_day = 290 + int((zone_num - 3) * 8)   # October 17 for Zone 5
    
    last_frost = datetime(2024, 1, 1) + timedelta(days=base_last_frost_day)
    first_frost = datetime(2024, 1, 1) + timedelta(days=base_first_frost_day)
    
    growing_season = (first_frost - last_frost).days
    
    return {
        "success": True,
        "last_frost_date": last_frost.date().isoformat(),
        "first_frost_date": first_frost.date().isoformat(), 
        "growing_season_length": growing_season,
        "frost_free_days": growing_season,
        "confidence_level": "estimated",
        "location_info": {
            "climate_zone": zone,
            "state": request.location.state,
            "latitude": request.location.latitude
        }
    }

@app.get("/api/v1/planting/available-crops")
async def get_available_crops():
    """Get list of available crops."""
    crops = []
    for crop_name, data in DEFAULT_PLANTING_DATA.items():
        crops.append({
            "name": crop_name,
            "days_to_maturity": data["days_to_maturity"],
            "season": "spring" if crop_name != "wheat" else "fall"
        })
    
    return crops

if __name__ == "__main__":
    print("Starting Standalone Planting Date Service...")
    print("=" * 50)
    print("Available endpoints:")
    print("  - Health: http://localhost:8001/health")
    print("  - Docs: http://localhost:8001/docs") 
    print("  - Calculate dates: POST http://localhost:8001/api/v1/planting/calculate-dates")
    print("  - Frost dates: POST http://localhost:8001/api/v1/planting/frost-dates")
    print("  - Available crops: GET http://localhost:8001/api/v1/planting/available-crops")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
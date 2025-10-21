from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from uuid import UUID

from ..models.fertilizer_type_models import FertilizerType, FertilizerTypeEnum, FertilizerFormEnum, FertilizerReleaseTypeEnum, EnvironmentalImpactEnum
from ..services.fertilizer_type_service import FertilizerTypeService

router = APIRouter(prefix="/api/v1/fertilizer-types", tags=["fertilizer-types"])

# Dependency injection for FertilizerTypeService
async def get_fertilizer_type_service() -> FertilizerTypeService:
    return FertilizerTypeService()

@router.get("/", response_model=List[FertilizerType])
async def get_all_fertilizer_types(
    service: FertilizerTypeService = Depends(get_fertilizer_type_service)
):
    """Retrieve all available fertilizer types."""
    return service.get_all_fertilizer_types()

@router.get("/{fertilizer_id}", response_model=FertilizerType)
async def get_fertilizer_type_by_id(
    fertilizer_id: UUID,
    service: FertilizerTypeService = Depends(get_fertilizer_type_service)
):
    """Retrieve a specific fertilizer type by its ID."""
    fertilizer = service.get_fertilizer_type_by_id(fertilizer_id)
    if not fertilizer:
        raise HTTPException(status_code=404, detail="Fertilizer type not found")
    return fertilizer

@router.post("/", response_model=FertilizerType, status_code=201)
async def create_fertilizer_type(
    fertilizer_data: FertilizerType,
    service: FertilizerTypeService = Depends(get_fertilizer_type_service)
):
    """Create a new fertilizer type."""
    try:
        return service.create_fertilizer_type(fertilizer_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{fertilizer_id}", response_model=FertilizerType)
async def update_fertilizer_type(
    fertilizer_id: UUID,
    fertilizer_data: FertilizerType,
    service: FertilizerTypeService = Depends(get_fertilizer_type_service)
):
    """Update an existing fertilizer type."""
    try:
        updated_fertilizer = service.update_fertilizer_type(fertilizer_id, fertilizer_data)
        if not updated_fertilizer:
            raise HTTPException(status_code=404, detail="Fertilizer type not found")
        return updated_fertilizer
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{fertilizer_id}", status_code=204)
async def delete_fertilizer_type(
    fertilizer_id: UUID,
    service: FertilizerTypeService = Depends(get_fertilizer_type_service)
):
    """Delete a fertilizer type."""
    if not service.delete_fertilizer_type(fertilizer_id):
        raise HTTPException(status_code=404, detail="Fertilizer type not found")

@router.get("/filter/", response_model=List[FertilizerType])
async def filter_fertilizer_types(
    name: Optional[str] = Query(None, description="Filter by fertilizer name"),
    npk_ratio: Optional[str] = Query(None, description="Filter by NPK ratio (e.g., '10-10-10')"),
    fertilizer_type: Optional[FertilizerTypeEnum] = Query(None, description="Filter by fertilizer type (organic/synthetic)"),
    form: Optional[FertilizerFormEnum] = Query(None, description="Filter by physical form (liquid/granular/gaseous)"),
    release_type: Optional[FertilizerReleaseTypeEnum] = Query(None, description="Filter by release type (quick/slow/controlled)"),
    min_cost: Optional[float] = Query(None, description="Filter by minimum cost per unit"),
    max_cost: Optional[float] = Query(None, description="Filter by maximum cost per unit"),
    environmental_impact_score: Optional[EnvironmentalImpactEnum] = Query(None, description="Filter by environmental impact score"),
    min_ph: Optional[float] = Query(None, description="Filter by minimum suitable pH"),
    max_ph: Optional[float] = Query(None, description="Filter by maximum suitable pH"),
    soil_type: Optional[str] = Query(None, description="Filter by suitable soil type"),
    climate_zone: Optional[str] = Query(None, description="Filter by suitable climate zone"),
    crop_type: Optional[str] = Query(None, description="Filter by suitable crop type"),
    application_method: Optional[str] = Query(None, description="Filter by suitable application method"),
    service: FertilizerTypeService = Depends(get_fertilizer_type_service)
):
    """Filter fertilizer types based on various criteria."""
    return service.filter_fertilizer_types(
        name=name, npk_ratio=npk_ratio, fertilizer_type=fertilizer_type, form=form,
        release_type=release_type, min_cost=min_cost, max_cost=max_cost,
        environmental_impact_score=environmental_impact_score, min_ph=min_ph, max_ph=max_ph,
        soil_type=soil_type, climate_zone=climate_zone, crop_type=crop_type,
        application_method=application_method
    )

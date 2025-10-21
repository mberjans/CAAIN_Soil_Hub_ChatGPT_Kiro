from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database.fertilizer_db import get_db
from ..services.fertilizer_type_service import FertilizerTypeService
from ..schemas.fertilizer_type_schemas import FertilizerTypeCreate, FertilizerTypeUpdate, FertilizerTypeInDB

router = APIRouter()

@router.post("/fertilizer-types/", response_model=FertilizerTypeInDB, status_code=status.HTTP_201_CREATED)
async def create_fertilizer_type_endpoint(
    fertilizer_in: FertilizerTypeCreate,
    db: Session = Depends(get_db)
):
    service = FertilizerTypeService(db)
    try:
        db_fertilizer = service.create_fertilizer_type(fertilizer_in)
        return db_fertilizer
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/fertilizer-types/", response_model=List[FertilizerTypeInDB])
async def get_all_fertilizer_types_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    service = FertilizerTypeService(db)
    fertilizer_types = service.get_all_fertilizer_types(skip=skip, limit=limit)
    return fertilizer_types

@router.get("/fertilizer-types/{fertilizer_type_id}", response_model=FertilizerTypeInDB)
async def get_fertilizer_type_endpoint(
    fertilizer_type_id: int,
    db: Session = Depends(get_db)
):
    service = FertilizerTypeService(db)
    db_fertilizer = service.get_fertilizer_type(fertilizer_type_id)
    if db_fertilizer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fertilizer type not found")
    return db_fertilizer

@router.put("/fertilizer-types/{fertilizer_type_id}", response_model=FertilizerTypeInDB)
async def update_fertilizer_type_endpoint(
    fertilizer_type_id: int,
    fertilizer_in: FertilizerTypeUpdate,
    db: Session = Depends(get_db)
):
    service = FertilizerTypeService(db)
    db_fertilizer = service.update_fertilizer_type(fertilizer_type_id, fertilizer_in)
    if db_fertilizer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fertilizer type not found")
    return db_fertilizer

@router.delete("/fertilizer-types/{fertilizer_type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_fertilizer_type_endpoint(
    fertilizer_type_id: int,
    db: Session = Depends(get_db)
):
    service = FertilizerTypeService(db)
    db_fertilizer = service.delete_fertilizer_type(fertilizer_type_id)
    if db_fertilizer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fertilizer type not found")

@router.post("/fertilizer-types/compare", response_model=List[FertilizerTypeInDB])
async def compare_fertilizer_types_endpoint(
    fertilizer_type_ids: List[int],
    db: Session = Depends(get_db)
):
    service = FertilizerTypeService(db)
    compared_fertilizers = service.compare_fertilizer_types(fertilizer_type_ids)
    if not compared_fertilizers:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No fertilizer types found for comparison")
    return compared_fertilizers
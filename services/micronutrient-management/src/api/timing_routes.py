from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from ..database.micronutrient_db import get_db
from ..schemas.timing_schemas import MicronutrientApplicationTimingCreate, MicronutrientApplicationTimingUpdate, MicronutrientApplicationTimingResponse
from ..services.timing_service import TimingService

router = APIRouter(prefix="/application-timings", tags=["Application Timings"])

@router.post("/", response_model=MicronutrientApplicationTimingResponse, status_code=status.HTTP_201_CREATED)
def create_application_timing(
    timing: MicronutrientApplicationTimingCreate,
    db: Session = Depends(get_db),
    service: TimingService = Depends(TimingService)
):
    return service.create_timing(db=db, timing=timing)

@router.get("/", response_model=List[MicronutrientApplicationTimingResponse])
def read_application_timings(
    micronutrient_id: Optional[UUID] = None,
    crop_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    service: TimingService = Depends(TimingService)
):
    if micronutrient_id and crop_id:
        timings = service.get_timings_by_micronutrient_crop(db, micronutrient_id=micronutrient_id, crop_id=crop_id, skip=skip, limit=limit)
    else:
        timings = service.get_timings(db, skip=skip, limit=limit)
    return timings

@router.get("/{timing_id}", response_model=MicronutrientApplicationTimingResponse)
def read_application_timing(
    timing_id: UUID,
    db: Session = Depends(get_db),
    service: TimingService = Depends(TimingService)
):
    db_timing = service.get_timing(db, timing_id=timing_id)
    if db_timing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application timing not found")
    return db_timing

@router.put("/{timing_id}", response_model=MicronutrientApplicationTimingResponse)
def update_application_timing(
    timing_id: UUID,
    timing: MicronutrientApplicationTimingUpdate,
    db: Session = Depends(get_db),
    service: TimingService = Depends(TimingService)
):
    db_timing = service.update_timing(db, timing_id=timing_id, timing=timing)
    if db_timing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application timing not found")
    return db_timing

@router.delete("/{timing_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application_timing(
    timing_id: UUID,
    db: Session = Depends(get_db),
    service: TimingService = Depends(TimingService)
):
    db_timing = service.delete_timing(db, timing_id=timing_id)
    if db_timing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application timing not found")
    return
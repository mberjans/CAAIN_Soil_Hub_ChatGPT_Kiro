from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..database.micronutrient_db import get_db
from ..schemas.application_schemas import MicronutrientApplicationMethodCreate, MicronutrientApplicationMethodUpdate, MicronutrientApplicationMethodResponse
from ..services.application_method_service import ApplicationMethodService

router = APIRouter(prefix="/application-methods", tags=["Application Methods"])

@router.post("/", response_model=MicronutrientApplicationMethodResponse, status_code=status.HTTP_201_CREATED)
def create_application_method(
    method: MicronutrientApplicationMethodCreate,
    db: Session = Depends(get_db),
    service: ApplicationMethodService = Depends(ApplicationMethodService)
):
    db_method = service.get_method_by_name(db, name=method.name)
    if db_method:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Application method with this name already exists")
    return service.create_method(db=db, method=method)

@router.get("/", response_model=List[MicronutrientApplicationMethodResponse])
def read_application_methods(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    service: ApplicationMethodService = Depends(ApplicationMethodService)
):
    methods = service.get_methods(db, skip=skip, limit=limit)
    return methods

@router.get("/{method_id}", response_model=MicronutrientApplicationMethodResponse)
def read_application_method(
    method_id: UUID,
    db: Session = Depends(get_db),
    service: ApplicationMethodService = Depends(ApplicationMethodService)
):
    db_method = service.get_method(db, method_id=method_id)
    if db_method is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application method not found")
    return db_method

@router.put("/{method_id}", response_model=MicronutrientApplicationMethodResponse)
def update_application_method(
    method_id: UUID,
    method: MicronutrientApplicationMethodUpdate,
    db: Session = Depends(get_db),
    service: ApplicationMethodService = Depends(ApplicationMethodService)
):
    db_method = service.update_method(db, method_id=method_id, method=method)
    if db_method is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application method not found")
    return db_method

@router.delete("/{method_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application_method(
    method_id: UUID,
    db: Session = Depends(get_db),
    service: ApplicationMethodService = Depends(ApplicationMethodService)
):
    db_method = service.delete_method(db, method_id=method_id)
    if db_method is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application method not found")
    return
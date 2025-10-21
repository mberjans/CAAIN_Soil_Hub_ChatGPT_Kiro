from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..database.database import get_db
from ..services.priority_constraint_service import PriorityConstraintService
from ..models.priority_constraint_models import (
    FertilizerPriorityCreate, FertilizerPriorityUpdate, FertilizerPriority,
    FertilizerConstraintCreate, FertilizerConstraintUpdate, FertilizerConstraint
)

router = APIRouter(prefix="/api/v1/fertilizer-type-selection", tags=["fertilizer-type-selection"])

# Dependency to get PriorityConstraintService
def get_priority_constraint_service(db: Session = Depends(get_db)) -> PriorityConstraintService:
    return PriorityConstraintService(db)

# --- Fertilizer Priority Endpoints ---

@router.post("/priorities", response_model=FertilizerPriority, status_code=status.HTTP_201_CREATED)
async def create_priority(
    priority_data: FertilizerPriorityCreate,
    service: PriorityConstraintService = Depends(get_priority_constraint_service)
):
    """Create a new fertilizer priority for a user."""
    return service.create_priority(priority_data)

@router.get("/priorities/{priority_id}", response_model=FertilizerPriority)
async def get_priority(
    priority_id: UUID,
    service: PriorityConstraintService = Depends(get_priority_constraint_service)
):
    """Retrieve a specific fertilizer priority by its ID."""
    priority = service.get_priority(priority_id)
    if not priority:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fertilizer priority not found")
    return priority

@router.get("/priorities/user/{user_id}", response_model=List[FertilizerPriority])
async def get_priorities_by_user(
    user_id: UUID,
    service: PriorityConstraintService = Depends(get_priority_constraint_service)
):
    """Retrieve all fertilizer priorities for a given user."""
    return service.get_priorities_by_user(user_id)

@router.put("/priorities/{priority_id}", response_model=FertilizerPriority)
async def update_priority(
    priority_id: UUID,
    priority_data: FertilizerPriorityUpdate,
    service: PriorityConstraintService = Depends(get_priority_constraint_service)
):
    """Update an existing fertilizer priority."""
    priority = service.update_priority(priority_id, priority_data)
    if not priority:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fertilizer priority not found")
    return priority

@router.delete("/priorities/{priority_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_priority(
    priority_id: UUID,
    service: PriorityConstraintService = Depends(get_priority_constraint_service)
):
    """Delete a fertilizer priority."""
    if not service.delete_priority(priority_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fertilizer priority not found")

# --- Fertilizer Constraint Endpoints ---

@router.post("/constraints", response_model=FertilizerConstraint, status_code=status.HTTP_201_CREATED)
async def create_constraint(
    constraint_data: FertilizerConstraintCreate,
    service: PriorityConstraintService = Depends(get_priority_constraint_service)
):
    """Create a new fertilizer constraint for a user."""
    return service.create_constraint(constraint_data)

@router.get("/constraints/{constraint_id}", response_model=FertilizerConstraint)
async def get_constraint(
    constraint_id: UUID,
    service: PriorityConstraintService = Depends(get_priority_constraint_service)
):
    """Retrieve a specific fertilizer constraint by its ID."""
    constraint = service.get_constraint(constraint_id)
    if not constraint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fertilizer constraint not found")
    return constraint

@router.get("/constraints/user/{user_id}", response_model=List[FertilizerConstraint])
async def get_constraints_by_user(
    user_id: UUID,
    service: PriorityConstraintService = Depends(get_priority_constraint_service)
):
    """Retrieve all fertilizer constraints for a given user."""
    return service.get_constraints_by_user(user_id)

@router.put("/constraints/{constraint_id}", response_model=FertilizerConstraint)
async def update_constraint(
    constraint_id: UUID,
    constraint_data: FertilizerConstraintUpdate,
    service: PriorityConstraintService = Depends(get_priority_constraint_service)
):
    """Update an existing fertilizer constraint."""
    constraint = service.update_constraint(constraint_id, constraint_data)
    if not constraint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fertilizer constraint not found")
    return constraint

@router.delete("/constraints/{constraint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_constraint(
    constraint_id: UUID,
    service: PriorityConstraintService = Depends(get_priority_constraint_service)
):
    """Delete a fertilizer constraint."""
    if not service.delete_constraint(constraint_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fertilizer constraint not found")

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.fertilizer_db import get_db_session
from src.models.priority_constraint_models import Priority, Constraint, PriorityDB, ConstraintDB, PriorityConstraintInput
from src.services.priority_constraint_service import PriorityConstraintService

router = APIRouter(prefix="/api/v1/priority-constraints", tags=["priority-constraints"])

async def get_priority_constraint_service(db: AsyncSession = Depends(get_db_session)) -> PriorityConstraintService:
    return PriorityConstraintService(db)

# --- Priority Endpoints ---

@router.post("/priorities/", response_model=Priority, status_code=status.HTTP_201_CREATED)
async def create_priority_endpoint(
    priority: Priority,
    service: PriorityConstraintService = Depends(get_priority_constraint_service)
):
    """Create a new priority."""
    db_priority = await service.create_priority(priority)
    return Priority(
        priority_id=db_priority.id,
        priority_type=db_priority.priority_type,
        weight=db_priority.weight,
        description=db_priority.description
    )

@router.get("/priorities/{priority_id}", response_model=Priority)
async def get_priority_endpoint(
    priority_id: UUID,
    service: PriorityConstraintService = Depends(get_priority_constraint_service)
):
    """Get a priority by ID."""
    db_priority = await service.get_priority(priority_id)
    if db_priority is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Priority not found")
    return Priority(
        priority_id=db_priority.id,
        priority_type=db_priority.priority_type,
        weight=db_priority.weight,
        description=db_priority.description
    )

@router.get("/priorities/", response_model=List[Priority])
async def get_all_priorities_endpoint(
    service: PriorityConstraintService = Depends(get_priority_constraint_service)
):
    """Get all priorities."""
    db_priorities = await service.get_all_priorities()
    return [
        Priority(
            priority_id=p.id,
            priority_type=p.priority_type,
            weight=p.weight,
            description=p.description
        ) for p in db_priorities
    ]

@router.put("/priorities/{priority_id}", response_model=Priority)
async def update_priority_endpoint(
    priority_id: UUID,
    priority: Priority,
    service: PriorityConstraintService = Depends(get_priority_constraint_service)
):
    """Update an existing priority."""
    db_priority = await service.update_priority(priority_id, priority)
    if db_priority is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Priority not found")
    return Priority(
        priority_id=db_priority.id,
        priority_type=db_priority.priority_type,
        weight=db_priority.weight,
        description=db_priority.description
    )

@router.delete("/priorities/{priority_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_priority_endpoint(
    priority_id: UUID,
    service: PriorityConstraintService = Depends(get_priority_constraint_service)
):
    """Delete a priority."""
    if not await service.delete_priority(priority_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Priority not found")

# --- Constraint Endpoints ---

@router.post("/constraints/", response_model=Constraint, status_code=status.HTTP_201_CREATED)
async def create_constraint_endpoint(
    constraint: Constraint,
    service: PriorityConstraintService = Depends(get_priority_constraint_service)
):
    """Create a new constraint."""
    db_constraint = await service.create_constraint(constraint)
    return Constraint(
        constraint_id=db_constraint.id,
        constraint_type=db_constraint.constraint_type,
        value=db_constraint.value,
        unit=db_constraint.unit,
        description=db_constraint.description
    )

@router.get("/constraints/{constraint_id}", response_model=Constraint)
async def get_constraint_endpoint(
    constraint_id: UUID,
    service: PriorityConstraintService = Depends(get_priority_constraint_service)
):
    """Get a constraint by ID."""
    db_constraint = await service.get_constraint(constraint_id)
    if db_constraint is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Constraint not found")
    return Constraint(
        constraint_id=db_constraint.id,
        constraint_type=db_constraint.constraint_type,
        value=db_constraint.value,
        unit=db_constraint.unit,
        description=db_constraint.description
    )

@router.get("/constraints/", response_model=List[Constraint])
async def get_all_constraints_endpoint(
    service: PriorityConstraintService = Depends(get_priority_constraint_service)
):
    """Get all constraints."""
    db_constraints = await service.get_all_constraints()
    return [
        Constraint(
            constraint_id=c.id,
            constraint_type=c.constraint_type,
            value=c.value,
            unit=c.unit,
            description=c.description
        ) for c in db_constraints
    ]

@router.put("/constraints/{constraint_id}", response_model=Constraint)
async def update_constraint_endpoint(
    constraint_id: UUID,
    constraint: Constraint,
    service: PriorityConstraintService = Depends(get_priority_constraint_service)
):
    """Update an existing constraint."""
    db_constraint = await service.update_constraint(constraint_id, constraint)
    if db_constraint is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Constraint not found")
    return Constraint(
        constraint_id=db_constraint.id,
        constraint_type=db_constraint.constraint_type,
        value=db_constraint.value,
        unit=db_constraint.unit,
        description=db_constraint.description
    )

@router.delete("/constraints/{constraint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_constraint_endpoint(
    constraint_id: UUID,
    service: PriorityConstraintService = Depends(get_priority_constraint_service)
):
    """Delete a constraint."""
    if not await service.delete_constraint(constraint_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Constraint not found")

# --- Combined Endpoint ---

@router.post("/", status_code=status.HTTP_200_OK)
async def submit_priority_constraints(
    data: PriorityConstraintInput,
    service: PriorityConstraintService = Depends(get_priority_constraint_service)
):
    """Submit a combined list of priorities and constraints."""
    created_priorities = []
    for p in data.priorities:
        created_priorities.append(await service.create_priority(p))

    created_constraints = []
    for c in data.constraints:
        created_constraints.append(await service.create_constraint(c))

    return {
        "message": "Priorities and constraints submitted successfully",
        "created_priorities_count": len(created_priorities),
        "created_constraints_count": len(created_constraints)
    }

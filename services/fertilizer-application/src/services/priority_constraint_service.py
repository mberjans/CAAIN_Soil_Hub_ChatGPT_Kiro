from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.models.priority_constraint_models import Priority, Constraint, PriorityDB, ConstraintDB

class PriorityConstraintService:
    """Service for managing priorities and constraints in fertilizer application."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_priority(self, priority: Priority) -> PriorityDB:
        """Creates a new priority in the database."""
        db_priority = PriorityDB(
            id=priority.priority_id,
            priority_type=priority.priority_type.value,
            weight=priority.weight,
            description=priority.description
        )
        self.db.add(db_priority)
        await self.db.commit()
        await self.db.refresh(db_priority)
        return db_priority

    async def get_priority(self, priority_id: UUID) -> Optional[PriorityDB]:
        """Retrieves a priority by ID."""
        result = await self.db.execute(
            select(PriorityDB).filter(PriorityDB.id == priority_id)
        )
        return result.scalars().first()

    async def get_all_priorities(self) -> List[PriorityDB]:
        """Retrieves all priorities."""
        result = await self.db.execute(select(PriorityDB))
        return result.scalars().all()

    async def update_priority(self, priority_id: UUID, priority: Priority) -> Optional[PriorityDB]:
        """Updates an existing priority."""
        db_priority = await self.get_priority(priority_id)
        if db_priority:
            db_priority.priority_type = priority.priority_type.value
            db_priority.weight = priority.weight
            db_priority.description = priority.description
            await self.db.commit()
            await self.db.refresh(db_priority)
        return db_priority

    async def delete_priority(self, priority_id: UUID) -> bool:
        """Deletes a priority."""
        db_priority = await self.get_priority(priority_id)
        if db_priority:
            await self.db.delete(db_priority)
            await self.db.commit()
            return True
        return False

    async def create_constraint(self, constraint: Constraint) -> ConstraintDB:
        """Creates a new constraint in the database."""
        db_constraint = ConstraintDB(
            id=constraint.constraint_id,
            constraint_type=constraint.constraint_type.value,
            value=str(constraint.value),  # Store value as string for flexibility
            unit=constraint.unit,
            description=constraint.description
        )
        self.db.add(db_constraint)
        await self.db.commit()
        await self.db.refresh(db_constraint)
        return db_constraint

    async def get_constraint(self, constraint_id: UUID) -> Optional[ConstraintDB]:
        """Retrieves a constraint by ID."""
        result = await self.db.execute(
            select(ConstraintDB).filter(ConstraintDB.id == constraint_id)
        )
        return result.scalars().first()

    async def get_all_constraints(self) -> List[ConstraintDB]:
        """Retrieves all constraints."""
        result = await self.db.execute(select(ConstraintDB))
        return result.scalars().all()

    async def update_constraint(self, constraint_id: UUID, constraint: Constraint) -> Optional[ConstraintDB]:
        """Updates an existing constraint."""
        db_constraint = await self.get_constraint(constraint_id)
        if db_constraint:
            db_constraint.constraint_type = constraint.constraint_type.value
            db_constraint.value = str(constraint.value)
            db_constraint.unit = constraint.unit
            db_constraint.description = constraint.description
            await self.db.commit()
            await self.db.refresh(db_constraint)
        return db_constraint

    async def delete_constraint(self, constraint_id: UUID) -> bool:
        """Deletes a constraint."""
        db_constraint = await self.get_constraint(constraint_id)
        if db_constraint:
            await self.db.delete(db_constraint)
            await self.db.commit()
            return True
        return False

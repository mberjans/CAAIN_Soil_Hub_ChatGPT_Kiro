from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional

from ..database.database import FertilizerPriorityDB, FertilizerConstraintDB
from ..models.priority_constraint_models import (
    FertilizerPriorityCreate, FertilizerPriorityUpdate, FertilizerPriority,
    FertilizerConstraintCreate, FertilizerConstraintUpdate, FertilizerConstraint
)

class PriorityConstraintService:
    def __init__(self, db: Session):
        self.db = db

    # --- Fertilizer Priorities ---

    def create_priority(self, priority_data: FertilizerPriorityCreate) -> FertilizerPriority:
        db_priority = FertilizerPriorityDB(**priority_data.model_dump())
        self.db.add(db_priority)
        self.db.commit()
        self.db.refresh(db_priority)
        return FertilizerPriority.model_validate(db_priority)

    def get_priority(self, priority_id: UUID) -> Optional[FertilizerPriority]:
        db_priority = self.db.query(FertilizerPriorityDB).filter(FertilizerPriorityDB.priority_id == priority_id).first()
        if db_priority:
            return FertilizerPriority.model_validate(db_priority)
        return None

    def get_priorities_by_user(self, user_id: UUID) -> List[FertilizerPriority]:
        db_priorities = self.db.query(FertilizerPriorityDB).filter(FertilizerPriorityDB.user_id == user_id).all()
        return [FertilizerPriority.model_validate(p) for p in db_priorities]

    def update_priority(self, priority_id: UUID, priority_data: FertilizerPriorityUpdate) -> Optional[FertilizerPriority]:
        db_priority = self.db.query(FertilizerPriorityDB).filter(FertilizerPriorityDB.priority_id == priority_id).first()
        if db_priority:
            for key, value in priority_data.model_dump(exclude_unset=True).items():
                setattr(db_priority, key, value)
            self.db.commit()
            self.db.refresh(db_priority)
            return FertilizerPriority.model_validate(db_priority)
        return None

    def delete_priority(self, priority_id: UUID) -> bool:
        db_priority = self.db.query(FertilizerPriorityDB).filter(FertilizerPriorityDB.priority_id == priority_id).first()
        if db_priority:
            self.db.delete(db_priority)
            self.db.commit()
            return True
        return False

    # --- Fertilizer Constraints ---

    def create_constraint(self, constraint_data: FertilizerConstraintCreate) -> FertilizerConstraint:
        db_constraint = FertilizerConstraintDB(**constraint_data.model_dump())
        self.db.add(db_constraint)
        self.db.commit()
        self.db.refresh(db_constraint)
        return FertilizerConstraint.model_validate(db_constraint)

    def get_constraint(self, constraint_id: UUID) -> Optional[FertilizerConstraint]:
        db_constraint = self.db.query(FertilizerConstraintDB).filter(FertilizerConstraintDB.constraint_id == constraint_id).first()
        if db_constraint:
            return FertilizerConstraint.model_validate(db_constraint)
        return None

    def get_constraints_by_user(self, user_id: UUID) -> List[FertilizerConstraint]:
        db_constraints = self.db.query(FertilizerConstraintDB).filter(FertilizerConstraintDB.user_id == user_id).all()
        return [FertilizerConstraint.model_validate(c) for c in db_constraints]

    def update_constraint(self, constraint_id: UUID, constraint_data: FertilizerConstraintUpdate) -> Optional[FertilizerConstraint]:
        db_constraint = self.db.query(FertilizerConstraintDB).filter(FertilizerConstraintDB.constraint_id == constraint_id).first()
        if db_constraint:
            for key, value in constraint_data.model_dump(exclude_unset=True).items():
                setattr(db_constraint, key, value)
            self.db.commit()
            self.db.refresh(db_constraint)
            return FertilizerConstraint.model_validate(db_constraint)
        return None

    def delete_constraint(self, constraint_id: UUID) -> bool:
        db_constraint = self.db.query(FertilizerConstraintDB).filter(FertilizerConstraintDB.constraint_id == constraint_id).first()
        if db_constraint:
            self.db.delete(db_constraint)
            self.db.commit()
            return True
        return False

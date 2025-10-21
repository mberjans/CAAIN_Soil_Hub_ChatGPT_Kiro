from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from ..models.application_models import MicronutrientApplicationMethod
from ..schemas.application_schemas import MicronutrientApplicationMethodCreate, MicronutrientApplicationMethodUpdate

class ApplicationMethodService:
    def get_method(self, db: Session, method_id: UUID) -> Optional[MicronutrientApplicationMethod]:
        return db.query(MicronutrientApplicationMethod).filter(MicronutrientApplicationMethod.id == method_id).first()

    def get_method_by_name(self, db: Session, name: str) -> Optional[MicronutrientApplicationMethod]:
        return db.query(MicronutrientApplicationMethod).filter(MicronutrientApplicationMethod.name == name).first()

    def get_methods(self, db: Session, skip: int = 0, limit: int = 100) -> List[MicronutrientApplicationMethod]:
        return db.query(MicronutrientApplicationMethod).offset(skip).limit(limit).all()

    def create_method(self, db: Session, method: MicronutrientApplicationMethodCreate) -> MicronutrientApplicationMethod:
        db_method = MicronutrientApplicationMethod(**method.model_dump())
        db.add(db_method)
        db.commit()
        db.refresh(db_method)
        return db_method

    def update_method(self, db: Session, method_id: UUID, method: MicronutrientApplicationMethodUpdate) -> Optional[MicronutrientApplicationMethod]:
        db_method = self.get_method(db, method_id)
        if db_method:
            for key, value in method.model_dump(exclude_unset=True).items():
                setattr(db_method, key, value)
            db.commit()
            db.refresh(db_method)
        return db_method

    def delete_method(self, db: Session, method_id: UUID) -> Optional[MicronutrientApplicationMethod]:
        db_method = self.get_method(db, method_id)
        if db_method:
            db.delete(db_method)
            db.commit()
        return db_method

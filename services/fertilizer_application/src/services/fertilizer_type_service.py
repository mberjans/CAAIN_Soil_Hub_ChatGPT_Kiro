from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from ..models.fertilizer_type_models import FertilizerType, FertilizerTypeEnum, EnvironmentalImpactEnum
from ..schemas.fertilizer_type_schemas import FertilizerTypeCreate, FertilizerTypeUpdate, NPKRatio

class FertilizerTypeService:
    def __init__(self, db: Session):
        self.db = db

    def create_fertilizer_type(self, fertilizer_in: FertilizerTypeCreate) -> FertilizerType:
        try:
            npk_ratio_dict = fertilizer_in.npk_ratio.dict()
            db_fertilizer = FertilizerType(
                name=fertilizer_in.name,
                type=fertilizer_in.type,
                npk_ratio=npk_ratio_dict,
                micronutrients=fertilizer_in.micronutrients,
                cost_per_unit=fertilizer_in.cost_per_unit,
                unit=fertilizer_in.unit,
                environmental_impact_score=fertilizer_in.environmental_impact_score,
                release_rate=fertilizer_in.release_rate,
                organic_certified=fertilizer_in.organic_certified,
                application_methods=fertilizer_in.application_methods,
                description=fertilizer_in.description
            )
            self.db.add(db_fertilizer)
            self.db.commit()
            self.db.refresh(db_fertilizer)
            return db_fertilizer
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Fertilizer type with this name already exists.")

    def get_fertilizer_type(self, fertilizer_type_id: int) -> Optional[FertilizerType]:
        return self.db.query(FertilizerType).filter(FertilizerType.id == fertilizer_type_id).first()

    def get_fertilizer_type_by_name(self, name: str) -> Optional[FertilizerType]:
        return self.db.query(FertilizerType).filter(FertilizerType.name == name).first()

    def get_all_fertilizer_types(self, skip: int = 0, limit: int = 100) -> List[FertilizerType]:
        return self.db.query(FertilizerType).offset(skip).limit(limit).all()

    def update_fertilizer_type(self, fertilizer_type_id: int, fertilizer_in: FertilizerTypeUpdate) -> Optional[FertilizerType]:
        db_fertilizer = self.get_fertilizer_type(fertilizer_type_id)
        if not db_fertilizer:
            return None

        for var, value in fertilizer_in.dict(exclude_unset=True).items():
            if var == "npk_ratio" and value is not None:
                setattr(db_fertilizer, var, value.dict())
            elif var == "type" and value is not None:
                setattr(db_fertilizer, var, FertilizerTypeEnum(value))
            elif var == "environmental_impact_score" and value is not None:
                setattr(db_fertilizer, var, EnvironmentalImpactEnum(value))
            else:
                setattr(db_fertilizer, var, value)

        self.db.commit()
        self.db.refresh(db_fertilizer)
        return db_fertilizer

    def delete_fertilizer_type(self, fertilizer_type_id: int) -> Optional[FertilizerType]:
        db_fertilizer = self.get_fertilizer_type(fertilizer_type_id)
        if not db_fertilizer:
            return None
        self.db.delete(db_fertilizer)
        self.db.commit()
        return db_fertilizer

    def compare_fertilizer_types(self, fertilizer_type_ids: List[int]) -> List[FertilizerType]:
        return self.db.query(FertilizerType).filter(FertilizerType.id.in_(fertilizer_type_ids)).all()
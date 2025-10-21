from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from ..models.timing_models import MicronutrientApplicationTiming
from ..schemas.timing_schemas import MicronutrientApplicationTimingCreate, MicronutrientApplicationTimingUpdate

class TimingService:
    def get_timing(self, db: Session, timing_id: UUID) -> Optional[MicronutrientApplicationTiming]:
        return db.query(MicronutrientApplicationTiming).filter(MicronutrientApplicationTiming.id == timing_id).first()

    def get_timings_by_micronutrient_crop(self, db: Session, micronutrient_id: UUID, crop_id: UUID, skip: int = 0, limit: int = 100) -> List[MicronutrientApplicationTiming]:
        return db.query(MicronutrientApplicationTiming).filter(MicronutrientApplicationTiming.micronutrient_id == micronutrient_id, MicronutrientApplicationTiming.crop_id == crop_id).offset(skip).limit(limit).all()

    def get_timings(self, db: Session, skip: int = 0, limit: int = 100) -> List[MicronutrientApplicationTiming]:
        return db.query(MicronutrientApplicationTiming).offset(skip).limit(limit).all()

    def create_timing(self, db: Session, timing: MicronutrientApplicationTimingCreate) -> MicronutrientApplicationTiming:
        db_timing = MicronutrientApplicationTiming(**timing.model_dump())
        db.add(db_timing)
        db.commit()
        db.refresh(db_timing)
        return db_timing

    def update_timing(self, db: Session, timing_id: UUID, timing: MicronutrientApplicationTimingUpdate) -> Optional[MicronutrientApplicationTiming]:
        db_timing = self.get_timing(db, timing_id)
        if db_timing:
            for key, value in timing.model_dump(exclude_unset=True).items():
                setattr(db_timing, key, value)
            db.commit()
            db.refresh(db_timing)
        return db_timing

    def delete_timing(self, db: Session, timing_id: UUID) -> Optional[MicronutrientApplicationTiming]:
        db_timing = self.get_timing(db, timing_id)
        if db_timing:
            db.delete(db_timing)
            db.commit()
        return db_timing

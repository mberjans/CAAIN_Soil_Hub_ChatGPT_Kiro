from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from uuid import UUID
from ..models.crop_filtering_models import FarmerCropPreference
from ..schemas.preference_schemas import PreferenceCreate, PreferenceUpdate, PreferenceResponse

class FarmerPreferenceManager:
    """Comprehensive farmer preference storage (TICKET-005_crop-type-filtering-3.1)"""

    def __init__(self, db: Session):
        self.db = db

    async def create_preference(self, preference: PreferenceCreate) -> PreferenceResponse:
        """Create new farmer preference"""
        db_preference = FarmerCropPreference(
            user_id=preference.user_id,
            preference_category=preference.preference_category,
            preference_data=preference.preference_data,
            weight=preference.weight
        )
        self.db.add(db_preference)
        self.db.commit()
        self.db.refresh(db_preference)
        return PreferenceResponse.from_orm(db_preference)

    async def get_user_preferences(self, user_id: UUID) -> List[PreferenceResponse]:
        """Get all preferences for a user"""
        preferences = self.db.query(FarmerCropPreference).filter(
            FarmerCropPreference.user_id == user_id
        ).all()
        return [PreferenceResponse.from_orm(p) for p in preferences]

    async def update_preference(self, preference_id: UUID, update: PreferenceUpdate) -> PreferenceResponse:
        """Update existing preference"""
        db_preference = self.db.query(FarmerCropPreference).filter(
            FarmerCropPreference.id == preference_id
        ).first()

        if not db_preference:
            raise ValueError(f"Preference {preference_id} not found")

        if update.preference_data is not None:
            db_preference.preference_data = update.preference_data
        if update.weight is not None:
            db_preference.weight = update.weight

        self.db.commit()
        self.db.refresh(db_preference)
        return PreferenceResponse.from_orm(db_preference)

    async def delete_preference(self, preference_id: UUID) -> bool:
        """Delete preference"""
        result = self.db.query(FarmerCropPreference).filter(
            FarmerCropPreference.id == preference_id
        ).delete()
        self.db.commit()
        return result > 0
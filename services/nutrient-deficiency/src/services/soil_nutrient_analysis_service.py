from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from ..models.soil_nutrient_models import SoilNutrientAnalysis
from ..schemas.soil_nutrient_schemas import SoilNutrientAnalysisCreate, SoilNutrientAnalysisResponse

class SoilNutrientAnalysisService:
    def __init__(self, db: Session):
        self.db = db

    def create_analysis(self, analysis_data: SoilNutrientAnalysisCreate) -> SoilNutrientAnalysis:
        db_analysis = SoilNutrientAnalysis(**analysis_data.model_dump(exclude_unset=True))
        # Handle JSONB fields separately
        if analysis_data.macro_nutrients:
            db_analysis.macro_nutrients = analysis_data.macro_nutrients.model_dump(mode='json')
        if analysis_data.micro_nutrients:
            db_analysis.micro_nutrients = analysis_data.micro_nutrients.model_dump(mode='json')
        if analysis_data.other_properties:
            db_analysis.other_properties = analysis_data.other_properties.model_dump(mode='json')

        self.db.add(db_analysis)
        self.db.commit()
        self.db.refresh(db_analysis)
        return db_analysis

    def get_analysis(self, analysis_id: UUID) -> Optional[SoilNutrientAnalysis]:
        return self.db.query(SoilNutrientAnalysis).filter(SoilNutrientAnalysis.id == analysis_id).first()

    def get_analyses_by_farm(self, farm_id: UUID) -> List[SoilNutrientAnalysis]:
        return self.db.query(SoilNutrientAnalysis).filter(SoilNutrientAnalysis.farm_id == farm_id).all()

    def get_analyses_by_field(self, field_id: UUID) -> List[SoilNutrientAnalysis]:
        return self.db.query(SoilNutrientAnalysis).filter(SoilNutrientAnalysis.field_id == field_id).all()

    def update_analysis(self, analysis_id: UUID, analysis_data: SoilNutrientAnalysisCreate) -> Optional[SoilNutrientAnalysis]:
        db_analysis = self.get_analysis(analysis_id)
        if db_analysis:
            update_data = analysis_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                if key in ["macro_nutrients", "micro_nutrients", "other_properties"] and value is not None:
                    setattr(db_analysis, key, value.model_dump(mode='json'))
                elif key not in ["macro_nutrients", "micro_nutrients", "other_properties"]:
                    setattr(db_analysis, key, value)
            self.db.commit()
            self.db.refresh(db_analysis)
        return db_analysis

    def delete_analysis(self, analysis_id: UUID) -> bool:
        db_analysis = self.get_analysis(analysis_id)
        if db_analysis:
            self.db.delete(db_analysis)
            self.db.commit()
            return True
        return False

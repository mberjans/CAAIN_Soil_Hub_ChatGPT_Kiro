from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..schemas.soil_nutrient_schemas import SoilNutrientAnalysisCreate, SoilNutrientAnalysisResponse
from ..services.soil_nutrient_analysis_service import SoilNutrientAnalysisService
from ..database import get_db

router = APIRouter(prefix="/api/v1/soil-nutrient-analysis", tags=["Soil Nutrient Analysis"])

@router.post("/", response_model=SoilNutrientAnalysisResponse, status_code=status.HTTP_201_CREATED)
def create_soil_nutrient_analysis(
    analysis_data: SoilNutrientAnalysisCreate,
    db: Session = Depends(get_db)
):
    service = SoilNutrientAnalysisService(db)
    try:
        db_analysis = service.create_analysis(analysis_data)
        return SoilNutrientAnalysisResponse.model_validate(db_analysis)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{analysis_id}", response_model=SoilNutrientAnalysisResponse)
def get_soil_nutrient_analysis(
    analysis_id: UUID,
    db: Session = Depends(get_db)
):
    service = SoilNutrientAnalysisService(db)
    db_analysis = service.get_analysis(analysis_id)
    if db_analysis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
    return SoilNutrientAnalysisResponse.model_validate(db_analysis)

@router.get("/farm/{farm_id}", response_model=List[SoilNutrientAnalysisResponse])
def get_soil_nutrient_analyses_by_farm(
    farm_id: UUID,
    db: Session = Depends(get_db)
):
    service = SoilNutrientAnalysisService(db)
    db_analyses = service.get_analyses_by_farm(farm_id)
    return [SoilNutrientAnalysisResponse.model_validate(analysis) for analysis in db_analyses]

@router.get("/field/{field_id}", response_model=List[SoilNutrientAnalysisResponse])
def get_soil_nutrient_analyses_by_field(
    field_id: UUID,
    db: Session = Depends(get_db)
):
    service = SoilNutrientAnalysisService(db)
    db_analyses = service.get_analyses_by_field(field_id)
    return [SoilNutrientAnalysisResponse.model_validate(analysis) for analysis in db_analyses]

@router.put("/{analysis_id}", response_model=SoilNutrientAnalysisResponse)
def update_soil_nutrient_analysis(
    analysis_id: UUID,
    analysis_data: SoilNutrientAnalysisCreate,
    db: Session = Depends(get_db)
):
    service = SoilNutrientAnalysisService(db)
    db_analysis = service.update_analysis(analysis_id, analysis_data)
    if db_analysis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
    return SoilNutrientAnalysisResponse.model_validate(db_analysis)

@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_soil_nutrient_analysis(
    analysis_id: UUID,
    db: Session = Depends(get_db)
):
    service = SoilNutrientAnalysisService(db)
    if not service.delete_analysis(analysis_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
    return

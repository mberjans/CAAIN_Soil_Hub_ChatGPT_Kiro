from fastapi import APIRouter, Depends, Query
from ..models.micronutrient_models import SoilTest, MicronutrientRecommendation
from ..services.micronutrient_service import MicronutrientService

router = APIRouter(
    prefix="/api/v1/micronutrients",
    tags=["micronutrients"],
)

def get_micronutrient_service():
    return MicronutrientService()

@router.get("/")
async def get_micronutrients():
    return {"message": "Micronutrient data will be here"}

@router.post("/soil-test", response_model=list[MicronutrientRecommendation])
async def process_soil_test(
    soil_test: SoilTest,
    crop_name: str = Query(..., description="The name of the crop"),
    service: MicronutrientService = Depends(get_micronutrient_service)
):
    return service.process_soil_test(soil_test, crop_name)

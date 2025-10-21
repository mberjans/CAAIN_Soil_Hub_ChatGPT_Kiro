from fastapi import APIRouter

router = APIRouter(
    prefix="/api/v1/micronutrients",
    tags=["micronutrients"],
)

@router.get("/")
async def get_micronutrients():
    return {"message": "Micronutrient data will be here"}

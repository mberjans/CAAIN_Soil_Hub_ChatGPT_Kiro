from fastapi import FastAPI
from services.nutrient_deficiency.src.api.soil_nutrient_routes import router as soil_nutrient_router
from services.nutrient_deficiency.src.models.soil_nutrient_models import Base
from services.nutrient_deficiency.src.database import engine

app = FastAPI(title="Nutrient Deficiency Detection Test Service")

app.include_router(soil_nutrient_router)

@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)

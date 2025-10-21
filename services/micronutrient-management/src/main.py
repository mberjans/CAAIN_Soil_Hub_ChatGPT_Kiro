from fastapi import FastAPI
from .api.micronutrient_routes import router as micronutrient_router

app = FastAPI(
    title="Micronutrient Management Service",
    description="Service for assessing micronutrient deficiencies and providing recommendations.",
    version="1.0.0",
)

app.include_router(micronutrient_router, prefix="/api/v1/micronutrients")

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Micronutrient Management Service is running. Visit /docs for API documentation."
}
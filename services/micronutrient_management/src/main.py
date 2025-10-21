from fastapi import FastAPI
from .api.micronutrient_routes import router as micronutrient_router

app = FastAPI(
    title="Micronutrient Management Service",
    description="Service for assessing micronutrient toxicity risk and over-application warnings.",
    version="1.0.0",
)

app.include_router(micronutrient_router)

@app.get("/health", tags=["Monitoring"])
async def health_check():
    return {"status": "healthy", "service": "micronutrient-management"}

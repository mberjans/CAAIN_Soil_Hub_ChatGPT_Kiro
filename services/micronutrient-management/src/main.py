from fastapi import FastAPI
from .api.micronutrient_routes import router as micronutrient_router

app = FastAPI(
    title="Micronutrient Management Service",
    description="Service for comprehensive micronutrient budget and cost analysis.",
    version="1.0.0",
)

app.include_router(micronutrient_router, prefix="/api/v1/micronutrients")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "micronutrient-management"}

from fastapi import FastAPI
from .api.micronutrient_routes import router as micronutrient_router

app = FastAPI(
    title="Micronutrient Management Service",
    description="Service for comprehensive prioritized micronutrient recommendations.",
    version="1.0.0",
)

app.include_router(micronutrient_router)

@app.get("/health", tags=["Health Check"])
async def health_check():
    return {"status": "healthy", "service": "micronutrient-management"}

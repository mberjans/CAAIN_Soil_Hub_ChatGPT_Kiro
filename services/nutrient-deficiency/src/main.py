from fastapi import FastAPI
from .api import tissue_test_routes

app = FastAPI(
    title="Nutrient Deficiency Detection Service",
    description="Service for analyzing tissue test results and detecting nutrient deficiencies.",
    version="1.0.0",
)

app.include_router(tissue_test_routes.router)

@app.get("/health", tags=["Monitoring"])
async def health_check():
    return {"status": "healthy", "service": "nutrient-deficiency-detection"}

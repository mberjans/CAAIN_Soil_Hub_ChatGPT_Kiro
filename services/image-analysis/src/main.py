from fastapi import FastAPI
from .api.image_analysis_routes import router as image_analysis_router

app = FastAPI(
    title="Image Analysis Service",
    description="Service for analyzing crop photos for nutrient deficiencies.",
    version="1.0.0",
)

app.include_router(image_analysis_router)

@app.get("/health", tags=["Monitoring"])
async def health_check():
    return {"status": "healthy", "service": "image-analysis"}

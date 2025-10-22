from fastapi import FastAPI
from .api.image_analysis_routes import router as image_analysis_router
from .api import analysis_routes

app = FastAPI(
    title="Image Analysis Service",
    description="Service for analyzing crop photos for nutrient deficiencies.",
    version="1.0.0",
)

# Configure middleware for file upload support
@app.middleware("http")
async def add_file_upload_support(request, call_next):
    """Add multipart form support for file uploads"""
    return await call_next(request)

app.include_router(image_analysis_router)
app.include_router(analysis_routes.router)

@app.get("/health", tags=["Monitoring"])
async def health_check():
    return {"status": "healthy", "service": "image-analysis"}

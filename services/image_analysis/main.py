from fastapi import FastAPI
from .src.api.image_routes import router as image_analysis_router
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CAAIN Soil Hub Image Analysis Service",
    description="Service for analyzing crop photos for nutrient deficiencies.",
    version="0.1.0",
)

app.include_router(image_analysis_router)

@app.on_event("startup")
async def startup_event():
    logger.info("Image Analysis Service starting up...")
    # Placeholder for any startup tasks, e.g., loading global models

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Image Analysis Service shutting down...")
    # Placeholder for any shutdown tasks, e.g., closing database connections

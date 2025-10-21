from fastapi import FastAPI
from .api.application_routes import router as application_router
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Micronutrient Application Service",
    description="Service for recommending optimal micronutrient application methods and timing.",
    version="1.0.0",
)

app.include_router(application_router)

@app.on_event("startup")
async def startup_event():
    logger.info("Micronutrient Application Service started up.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Micronutrient Application Service shutting down.")

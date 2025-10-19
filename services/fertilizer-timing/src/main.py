"""Entry point for the fertilizer timing optimization microservice."""

import logging
import os
from contextlib import asynccontextmanager
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.alert_routes import router as alert_router
from api.calendar_routes import router as calendar_router
from api.explanation_routes import router as explanation_router
from api.timing_routes import router as timing_router
from database.timing_db import initialize_database, shutdown_database

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("fertilizer-timing-main")

SERVICE_NAME = "fertilizer-timing-optimization"
SERVICE_PORT = int(os.getenv("FERTILIZER_TIMING_SERVICE_PORT", "8009"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events for the microservice."""
    logger.info("Starting %s microservice", SERVICE_NAME)
    try:
        await initialize_database()
        yield
    finally:
        await shutdown_database()
        logger.info("%s microservice shutdown complete", SERVICE_NAME)


app = FastAPI(
    title="AFAS Fertilizer Timing Optimization Service",
    description=(
        "Microservice providing fertilizer timing optimization, seasonal calendars, "
        "and alerting integrations."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(timing_router, prefix="/api/v1")
app.include_router(calendar_router, prefix="/api/v1")
app.include_router(alert_router, prefix="/api/v1")
app.include_router(explanation_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint for service monitoring."""
    features: List[str] = []
    features.append("timing_optimization")
    features.append("seasonal_calendar_generation")
    features.append("alerting")
    features.append("weather_integration")

    return {
        "service": SERVICE_NAME,
        "status": "healthy",
        "port": SERVICE_PORT,
        "features": features
    }


__all__ = ["app", "SERVICE_NAME", "SERVICE_PORT"]

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from .api.price_routes import router as price_router
from .api.commodity_price_routes import router as commodity_router
from .database.fertilizer_price_db import initialize_database, shutdown_database
from .database.commodity_price_db import initialize_commodity_database, shutdown_commodity_database
from .services.scheduled_price_updater import start_scheduled_updates, stop_scheduled_updates

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown tasks."""
    # Startup
    logger.info("Starting AFAS Fertilizer Strategy Optimization Service...")
    
    try:
        # Initialize database connections
        await initialize_database()
        await initialize_commodity_database()
        logger.info("Database connections initialized")
        
        # Start scheduled price updates
        await start_scheduled_updates()
        logger.info("Scheduled price updates started")
        
        yield
        
    finally:
        # Shutdown
        logger.info("Shutting down AFAS Fertilizer Strategy Optimization Service...")
        
        # Stop scheduled updates
        await stop_scheduled_updates()
        logger.info("Scheduled price updates stopped")
        
        # Shutdown database
        await shutdown_database()
        await shutdown_commodity_database()
        logger.info("Database connections closed")


app = FastAPI(
    title="AFAS Fertilizer Strategy Optimization Service",
    description="Comprehensive fertilizer price tracking, market analysis, and strategy optimization service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(price_router, prefix="/api/v1", tags=["fertilizer-prices"])
app.include_router(commodity_router, prefix="/api/v1", tags=["commodity-prices"])

@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "service": "fertilizer-strategy-optimization",
        "status": "healthy",
        "version": "1.0.0",
        "features": [
            "real_time_price_tracking",
            "historical_price_analysis",
            "price_volatility_tracking",
            "regional_price_variations",
            "fertilizer_type_tracking",
            "market_intelligence",
            "price_trend_analysis",
            "commodity_price_integration",
            "economic_optimization",
            "strategy_recommendations",
            "commodity_price_tracking",
            "futures_market_integration",
            "basis_analysis",
            "fertilizer_crop_price_ratios"
        ]
    }

@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "message": "AFAS Fertilizer Strategy Optimization Service is running",
        "service": "fertilizer-strategy-optimization",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    port = int(os.getenv("FERTILIZER_STRATEGY_PORT", 8009))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
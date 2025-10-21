from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv
import logging

try:
    from .api.routes import router
    from .api.personalization_routes import router as personalization_router
    from .api.fertilizer_routes import router as fertilizer_router
    from .database import init_database, get_database_manager
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent))
    from api.routes import router
    from api.personalization_routes import router as personalization_router
    from api.fertilizer_routes import router as fertilizer_router
    from database import init_database, get_database_manager

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AFAS Recommendation Engine",
    description="Core agricultural recommendation processing service with expert-validated algorithms",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup."""
    try:
        logger.info("Initializing database...")
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        # Don't fail startup, but log the error
        pass

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)
app.include_router(personalization_router)
app.include_router(fertilizer_router)

@app.get("/health")
async def health_check():
    """Health check endpoint for service monitoring."""
    db_manager = get_database_manager()
    db_healthy = db_manager.health_check()
    
    return {
        "service": "recommendation-engine",
        "status": "healthy" if db_healthy else "degraded",
        "version": "1.0.0",
        "description": "Core agricultural recommendation processing service",
        "database": {
            "status": "healthy" if db_healthy else "unhealthy",
            "connection_info": db_manager.get_connection_info() if db_healthy else None
        }
    }

@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "message": "AFAS Recommendation Engine is running",
        "service": "recommendation-engine", 
        "version": "1.0.0",
        "endpoints": {
            "crop_selection": "/api/v1/recommendations/crop-selection",
            "fertilizer_strategy": "/api/v1/recommendations/fertilizer-strategy",
            "fertilizer_type_selection": "/api/v1/fertilizer/type-selection",
            "fertilizer_comparison": "/api/v1/fertilizer/comparison",
            "soil_management": "/api/v1/recommendations/soil-management",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    port = int(os.getenv("RECOMMENDATION_ENGINE_PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
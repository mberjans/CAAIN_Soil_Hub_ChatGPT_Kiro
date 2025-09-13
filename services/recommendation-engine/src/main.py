from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

try:
    from .api.routes import router
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent))
    from api.routes import router

load_dotenv()

app = FastAPI(
    title="AFAS Recommendation Engine",
    description="Core agricultural recommendation processing service with expert-validated algorithms",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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
app.include_router(router)

@app.get("/health")
async def health_check():
    """Health check endpoint for service monitoring."""
    return {
        "service": "recommendation-engine",
        "status": "healthy",
        "version": "1.0.0",
        "description": "Core agricultural recommendation processing service"
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
            "soil_management": "/api/v1/recommendations/soil-management",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    port = int(os.getenv("RECOMMENDATION_ENGINE_PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
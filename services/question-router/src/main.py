from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Monitoring imports
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

try:
    from .api.routes import router
    from .utils.logging_config import setup_logging
except ImportError:
    # Fallback for direct execution
    sys.path.append(str(Path(__file__).parent))
    from api.routes import router
    from utils.logging_config import setup_logging

# Add shared utilities to path
shared_path = Path(__file__).parent.parent.parent.parent / "shared"
sys.path.append(str(shared_path))

try:
    from utils.metrics import MetricsCollector
    from utils.logging_config import setup_logging as enhanced_setup_logging
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False

load_dotenv()

# Setup logging and monitoring
if MONITORING_AVAILABLE:
    enhanced_setup_logging("question-router", os.getenv("LOG_LEVEL", "INFO"), enable_metrics=True)
    metrics_collector = MetricsCollector("question-router")
else:
    setup_logging("question-router", os.getenv("LOG_LEVEL", "INFO"))
    metrics_collector = None

app = FastAPI(
    title="AFAS Question Router",
    description="Routes farmer questions to appropriate processing pipelines using NLP classification",
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
        "service": "question-router",
        "status": "healthy",
        "version": "1.0.0",
        "description": "Routes farmer questions to appropriate processing pipelines"
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    if MONITORING_AVAILABLE:
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
    else:
        return {"error": "Monitoring not available"}

@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "message": "AFAS Question Router is running",
        "service": "question-router",
        "version": "1.0.0",
        "monitoring_enabled": MONITORING_AVAILABLE,
        "endpoints": {
            "classify": "/api/v1/questions/classify",
            "types": "/api/v1/questions/types",
            "metrics": "/metrics",
            "health": "/health",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    port = int(os.getenv("QUESTION_ROUTER_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
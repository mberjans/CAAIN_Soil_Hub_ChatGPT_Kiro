from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import logging
import asyncio
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from .api.routes import router
from .services.context_manager import initialize_context_manager, shutdown_context_manager

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
    logger.info("Starting AFAS AI Agent Service with context management...")
    
    try:
        # Initialize context manager
        await initialize_context_manager(
            max_contexts_per_user=1000,
            cleanup_interval_hours=6,
            enable_persistence=True
        )
        logger.info("Context management system initialized")
        
        yield
        
    finally:
        # Shutdown
        logger.info("Shutting down AFAS AI Agent Service...")
        await shutdown_context_manager()
        logger.info("Context management system shutdown complete")


app = FastAPI(
    title="AFAS AI Agent Service",
    description="Natural language processing and AI explanation service with OpenRouter LLM integration and context management",
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
app.include_router(router)

@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "service": "ai-agent",
        "status": "healthy",
        "version": "1.0.0",
        "features": [
            "question_classification",
            "conversational_ai",
            "agricultural_explanations",
            "streaming_responses",
            "openrouter_integration",
            "context_management",
            "conversation_continuity",
            "agricultural_context_awareness"
        ]
    }

@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "message": "AFAS AI Agent Service is running",
        "service": "ai-agent",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    port = int(os.getenv("AI_AGENT_PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
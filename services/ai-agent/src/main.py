from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import logging
from dotenv import load_dotenv

from .api.routes import router

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(
    title="AFAS AI Agent Service",
    description="Natural language processing and AI explanation service with OpenRouter LLM integration",
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
            "openrouter_integration"
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
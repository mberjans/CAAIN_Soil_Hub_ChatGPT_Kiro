from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="AFAS ai-agent",
    description="Natural language processing and AI explanation service",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {
        "service": "ai-agent",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    return {"message": "AFAS ai-agent is running"}

if __name__ == "__main__":
    port = int(os.getenv("AI_AGENT_PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
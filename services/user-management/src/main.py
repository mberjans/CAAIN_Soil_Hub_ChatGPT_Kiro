from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="AFAS user-management",
    description="User authentication and profile management service",
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
        "service": "user-management",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    return {"message": "AFAS user-management is running"}

if __name__ == "__main__":
    port = int(os.getenv("USER_MANAGEMENT_PORT", 8005))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
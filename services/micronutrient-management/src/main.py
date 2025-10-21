from fastapi import FastAPI
from contextlib import asynccontextmanager

from ..database.database import init_db
from .api.micronutrient_routes import router as micronutrient_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    await init_db()
    yield
    # Shutdown logic (if any)

app = FastAPI(
    title="Micronutrient Management Service",
    description="Service for generating prioritized micronutrient recommendations",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(micronutrient_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "micronutrient-management"}

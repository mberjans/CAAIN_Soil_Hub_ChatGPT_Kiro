from fastapi import FastAPI
from .api import fertilizer_type_routes
from .database.fertilizer_db import Base, engine
from .models import fertilizer_type_models

# Create database tables
fertilizer_type_models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Fertilizer Application Service",
    description="Manages fertilizer types, application methods, and related guidance.",
    version="1.0.0",
)

app.include_router(fertilizer_type_routes.router, prefix="/api/v1", tags=["Fertilizer Types"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Fertilizer Application Service"}

@app.get("/health", tags=["Health Check"])
async def health_check():
    return {"status": "healthy"}

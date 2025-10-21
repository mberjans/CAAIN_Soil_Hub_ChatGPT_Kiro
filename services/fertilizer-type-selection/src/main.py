from fastapi import FastAPI
from .api.priority_constraint_routes import router as priority_constraint_router
from .database.database import Base, engine

app = FastAPI(title="Fertilizer Type Selection Service")

# Create database tables
@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)

app.include_router(priority_constraint_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "fertilizer-type-selection"}

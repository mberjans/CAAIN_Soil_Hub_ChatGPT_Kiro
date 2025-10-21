from fastapi import FastAPI
from .api.price_routes import router as price_router
from .api.optimization_routes import router as optimization_router

app = FastAPI(title="Fertilizer Optimization Service", version="1.0.0")

# Include the routers
app.include_router(price_router)
app.include_router(optimization_router)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "fertilizer-optimization"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)
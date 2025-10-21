from fastapi import FastAPI
from .api.price_routes import router as price_router

app = FastAPI(title="Fertilizer Optimization Service", version="1.0.0")

# Include the price router
app.include_router(price_router)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "fertilizer-optimization"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)
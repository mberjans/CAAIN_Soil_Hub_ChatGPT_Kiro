from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Micronutrient Management Service")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "micronutrient-management"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8009)

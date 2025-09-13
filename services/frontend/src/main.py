from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import httpx
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AFAS Frontend",
    description="Autonomous Farm Advisory System Web Interface",
    version="1.0.0"
)

# Add CORS middleware for API integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Templates
templates_dir = Path(__file__).parent / "templates"
if templates_dir.exists():
    templates = Jinja2Templates(directory=str(templates_dir))
else:
    templates = None

# Backend service URLs
QUESTION_ROUTER_URL = os.getenv("QUESTION_ROUTER_URL", "http://localhost:8000")
RECOMMENDATION_ENGINE_URL = os.getenv("RECOMMENDATION_ENGINE_URL", "http://localhost:8001")
USER_MANAGEMENT_URL = os.getenv("USER_MANAGEMENT_URL", "http://localhost:8005")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    if templates:
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "title": "AFAS Dashboard"
        })
    else:
        return HTMLResponse("<h1>AFAS Frontend - Dashboard Coming Soon</h1>")

@app.get("/crop-selection", response_class=HTMLResponse)
async def crop_selection_page(request: Request):
    """Crop selection recommendation page"""
    if templates:
        return templates.TemplateResponse("crop_selection.html", {
            "request": request,
            "title": "Crop Selection Recommendations"
        })
    else:
        return HTMLResponse("<h1>Crop Selection - Coming Soon</h1>")

@app.get("/soil-fertility", response_class=HTMLResponse)
async def soil_fertility_page(request: Request):
    """Soil fertility management page"""
    if templates:
        return templates.TemplateResponse("soil_fertility.html", {
            "request": request,
            "title": "Soil Fertility Management"
        })
    else:
        return HTMLResponse("<h1>Soil Fertility - Coming Soon</h1>")

@app.get("/fertilizer-strategy", response_class=HTMLResponse)
async def fertilizer_strategy_page(request: Request):
    """Fertilizer strategy page"""
    if templates:
        return templates.TemplateResponse("fertilizer_strategy.html", {
            "request": request,
            "title": "Fertilizer Strategy"
        })
    else:
        return HTMLResponse("<h1>Fertilizer Strategy - Coming Soon</h1>")

@app.post("/api/ask-question")
async def ask_question(
    question: str = Form(...),
    farm_name: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    farm_size: Optional[float] = Form(None)
):
    """Process farmer questions through the question router"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{QUESTION_ROUTER_URL}/api/v1/questions/classify",
                json={
                    "question": question,
                    "context": {
                        "farm_name": farm_name,
                        "location": location,
                        "farm_size_acres": farm_size
                    }
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Question router error: {response.status_code}")
                raise HTTPException(status_code=500, detail="Failed to process question")
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

@app.post("/api/crop-recommendation")
async def get_crop_recommendation(
    location: str = Form(...),
    soil_ph: float = Form(...),
    organic_matter: float = Form(...),
    phosphorus: int = Form(...),
    potassium: int = Form(...),
    farm_size: float = Form(...),
    irrigation: bool = Form(False)
):
    """Get crop selection recommendations"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{RECOMMENDATION_ENGINE_URL}/api/v1/recommendations/crop-selection",
                json={
                    "location": location,
                    "soil_data": {
                        "ph": soil_ph,
                        "organic_matter_percent": organic_matter,
                        "phosphorus_ppm": phosphorus,
                        "potassium_ppm": potassium
                    },
                    "farm_constraints": {
                        "farm_size_acres": farm_size,
                        "irrigation_available": irrigation
                    }
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Recommendation engine error: {response.status_code}")
                raise HTTPException(status_code=500, detail="Failed to get recommendations")
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "service": "frontend",
        "status": "healthy",
        "version": "1.0.0",
        "backend_services": {
            "question_router": QUESTION_ROUTER_URL,
            "recommendation_engine": RECOMMENDATION_ENGINE_URL,
            "user_management": USER_MANAGEMENT_URL
        }
    }

if __name__ == "__main__":
    port = int(os.getenv("FRONTEND_PORT", 3000))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
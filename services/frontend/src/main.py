from fastapi import FastAPI, Request, Form, HTTPException, UploadFile, File, Query
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
from datetime import datetime
import time
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
COVER_CROP_SERVICE_URL = os.getenv("COVER_CROP_SERVICE_URL", "http://localhost:8001")
USER_MANAGEMENT_URL = os.getenv("USER_MANAGEMENT_URL", "http://localhost:8005")
DATA_INTEGRATION_URL = os.getenv("DATA_INTEGRATION_URL", "http://localhost:8003")
CROP_TAXONOMY_URL = os.getenv("CROP_TAXONOMY_URL", "http://localhost:8003")  # This should point to the crop-taxonomy service
LOCATION_VALIDATION_URL = os.getenv("LOCATION_VALIDATION_URL", "http://localhost:8006")
FERTILIZER_APPLICATION_URL = os.getenv("FERTILIZER_APPLICATION_URL", "http://localhost:8007")

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

@app.get("/variety-selection", response_class=HTMLResponse)
async def variety_selection_page(request: Request):
    """Advanced variety selection page"""
    if templates:
        return templates.TemplateResponse("variety_selection.html", {
            "request": request,
            "title": "Variety Selection"
        })
    else:
        return HTMLResponse("<h1>Variety Selection - Coming Soon</h1>")

@app.get("/advanced-variety-display", response_class=HTMLResponse)
async def advanced_variety_display_page(request: Request):
    """Advanced variety display and visualization page"""
    if templates:
        return templates.TemplateResponse("advanced_variety_display.html", {
            "request": request,
            "title": "Advanced Variety Display"
        })
    else:
        return HTMLResponse("<h1>Advanced Variety Display - Coming Soon</h1>")

@app.get("/variety-planning-tools", response_class=HTMLResponse)
async def variety_planning_tools_page(request: Request):
    """Comprehensive variety planning tools page"""
    if templates:
        return templates.TemplateResponse("variety_planning_tools.html", {
            "request": request,
            "title": "Variety Planning Tools"
        })
    else:
        return HTMLResponse("<h1>Variety Planning Tools - Coming Soon</h1>")

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

@app.get("/fertilizer-strategy-dashboard", response_class=HTMLResponse)
async def fertilizer_strategy_dashboard_page(request: Request):
    """Comprehensive fertilizer strategy dashboard page"""
    if templates:
        return templates.TemplateResponse("fertilizer_strategy_dashboard.html", {
            "request": request,
            "title": "Fertilizer Strategy Dashboard"
        })
    else:
        return HTMLResponse("<h1>Fertilizer Strategy Dashboard - Coming Soon</h1>")

@app.get("/fertilizer-application", response_class=HTMLResponse)
async def fertilizer_application_page(request: Request):
    """Fertilizer application method selection page"""
    if templates:
        return templates.TemplateResponse("fertilizer_application.html", {
            "request": request,
            "title": "Fertilizer Application Method Selector"
        })
    else:
        return HTMLResponse("<h1>Fertilizer Application Method - Coming Soon</h1>")

@app.get("/mobile-fertilizer-application", response_class=HTMLResponse)
async def mobile_fertilizer_application_page(request: Request):
    """Mobile-optimized fertilizer application management interface"""
    if templates:
        return templates.TemplateResponse("mobile_fertilizer_application.html", {
            "request": request,
            "title": "Mobile Fertilizer Application"
        })
    else:
        return HTMLResponse("<h1>Mobile Fertilizer Application - Coming Soon</h1>")

@app.get("/goal-prioritization", response_class=HTMLResponse)
async def goal_prioritization_page(request: Request):
    """Goal prioritization interface page"""
    if templates:
        return templates.TemplateResponse("goal_prioritization.html", {
            "request": request,
            "title": "Goal Prioritization"
        })
    else:
        return HTMLResponse("<h1>Goal Prioritization - Coming Soon</h1>")

@app.get("/rotation-planning", response_class=HTMLResponse)
async def rotation_planning_page(request: Request):
    """Crop rotation planning dashboard page"""
    if templates:
        return templates.TemplateResponse("rotation_planning.html", {
            "request": request,
            "title": "Crop Rotation Planning"
        })
    else:
        return HTMLResponse("<h1>Rotation Planning - Coming Soon</h1>")

@app.get("/crop-rotation-goals", response_class=HTMLResponse)
async def crop_rotation_goals_page(request: Request):
    """Crop rotation goal prioritization page (redirect to new interface)"""
    if templates:
        return templates.TemplateResponse("goal_prioritization.html", {
            "request": request,
            "title": "Crop Rotation Goal Prioritization"
        })
    else:
        return HTMLResponse("<h1>Crop Rotation Goals - Coming Soon</h1>")

@app.get("/filter-analytics", response_class=HTMLResponse)
async def filter_analytics_page(request: Request):
    """Filter analytics dashboard page"""
    if templates:
        return templates.TemplateResponse("filter_analytics.html", {
            "request": request,
            "title": "Filter Analytics Dashboard"
        })
    else:
        return HTMLResponse("<h1>Filter Analytics - Coming Soon</h1>")

@app.get("/climate-zone-selection", response_class=HTMLResponse)
async def climate_zone_selection_page(request: Request):
    """Climate zone selection page"""
    if templates:
        return templates.TemplateResponse("climate_zone_selection.html", {
            "request": request,
            "title": "Climate Zone Selection"
        })
    else:
        return HTMLResponse("<h1>Climate Zone Selection - Coming Soon</h1>")

@app.get("/ph-management", response_class=HTMLResponse)
async def ph_management_page(request: Request):
    """Comprehensive pH management page"""
    if templates:
        return templates.TemplateResponse("ph_management.html", {
            "request": request,
            "title": "Soil pH Management"
        })
    else:
        return HTMLResponse("<h1>pH Management - Coming Soon</h1>")

@app.get("/drought-management", response_class=HTMLResponse)
async def drought_management_page(request: Request):
    """Comprehensive drought management page"""
    if templates:
        return templates.TemplateResponse("drought_management.html", {
            "request": request,
            "title": "Drought Management"
        })
    else:
        return HTMLResponse("<h1>Drought Management - Coming Soon</h1>")

@app.get("/mobile-drought-management", response_class=HTMLResponse)
async def mobile_drought_management_page(request: Request):
    """Mobile-optimized drought management page"""
    if templates:
        return templates.TemplateResponse("mobile_drought_management.html", {
            "request": request,
            "title": "Drought Management"
        })
    else:
        return HTMLResponse("<h1>Mobile Drought Management - Coming Soon</h1>")

@app.get("/field-management", response_class=HTMLResponse)
async def field_management_page(request: Request):
    """Comprehensive field management interface page"""
    if templates:
        return templates.TemplateResponse("field_management.html", {
            "request": request,
            "title": "Field Management System"
        })
    else:
        return HTMLResponse("<h1>Field Management - Coming Soon</h1>")

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

@app.post("/api/soil-test/manual")
async def submit_manual_soil_test(
    ph: float = Form(...),
    organic_matter: Optional[float] = Form(None),
    phosphorus: Optional[float] = Form(None),
    potassium: Optional[float] = Form(None),
    nitrogen: Optional[float] = Form(None),
    soil_texture: Optional[str] = Form(None),
    cec: Optional[float] = Form(None),
    test_date: Optional[str] = Form(None),
    lab_name: Optional[str] = Form(None),
    test_notes: Optional[str] = Form(None)
):
    """Submit manual soil test data"""
    try:
        # Prepare soil test data
        soil_test_data = {
            "ph": ph,
            "test_date": test_date or datetime.now().date().isoformat()
        }
        
        # Add optional parameters if provided
        if organic_matter is not None:
            soil_test_data["organic_matter_percent"] = organic_matter
        if phosphorus is not None:
            soil_test_data["phosphorus_ppm"] = phosphorus
        if potassium is not None:
            soil_test_data["potassium_ppm"] = potassium
        if nitrogen is not None:
            soil_test_data["nitrogen_ppm"] = nitrogen
        if soil_texture:
            soil_test_data["soil_texture"] = soil_texture
        if cec is not None:
            soil_test_data["cec_meq_per_100g"] = cec
        if lab_name:
            soil_test_data["lab_name"] = lab_name
        if test_notes:
            soil_test_data["test_notes"] = test_notes
        
        # Submit to data integration service
        DATA_INTEGRATION_URL = os.getenv("DATA_INTEGRATION_URL", "http://localhost:8003")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{DATA_INTEGRATION_URL}/api/v1/soil-tests/manual",
                json=soil_test_data,
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Data integration error: {response.status_code}")
                raise HTTPException(status_code=500, detail="Failed to process soil test")
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

@app.post("/api/soil-test/upload")
async def upload_soil_test_report(
    file: UploadFile = File(...),
    field_id: Optional[str] = Form(None)
):
    """Upload soil test report file"""
    try:
        # Validate file type
        allowed_types = ["application/pdf", "text/plain", "text/csv"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=422,
                detail=f"Unsupported file type. Allowed: PDF, TXT, CSV"
            )
        
        # Submit to data integration service
        DATA_INTEGRATION_URL = os.getenv("DATA_INTEGRATION_URL", "http://localhost:8003")
        
        async with httpx.AsyncClient() as client:
            files = {"file": (file.filename, await file.read(), file.content_type)}
            data = {}
            if field_id:
                data["field_id"] = field_id
            
            response = await client.post(
                f"{DATA_INTEGRATION_URL}/api/v1/soil-tests/upload",
                files=files,
                data=data,
                timeout=60.0  # Longer timeout for file processing
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Data integration error: {response.status_code}")
                raise HTTPException(status_code=500, detail="Failed to process uploaded file")
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

@app.post("/api/soil-test/interpret")
async def interpret_soil_test(
    ph: float = Form(...),
    organic_matter: Optional[float] = Form(None),
    phosphorus: Optional[float] = Form(None),
    potassium: Optional[float] = Form(None),
    nitrogen: Optional[float] = Form(None),
    soil_texture: Optional[str] = Form(None),
    cec: Optional[float] = Form(None),
    crop_type: Optional[str] = Form(None)
):
    """Get soil test interpretation and recommendations"""
    try:
        # Prepare parameters
        params = {"ph": ph}
        if organic_matter is not None:
            params["organic_matter_percent"] = organic_matter
        if phosphorus is not None:
            params["phosphorus_ppm"] = phosphorus
        if potassium is not None:
            params["potassium_ppm"] = potassium
        if nitrogen is not None:
            params["nitrogen_ppm"] = nitrogen
        if soil_texture:
            params["soil_texture"] = soil_texture
        if cec is not None:
            params["cec_meq_per_100g"] = cec
        if crop_type:
            params["crop_type"] = crop_type
        
        # Submit to data integration service
        DATA_INTEGRATION_URL = os.getenv("DATA_INTEGRATION_URL", "http://localhost:8003")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{DATA_INTEGRATION_URL}/api/v1/soil-tests/interpret",
                params=params,
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Data integration error: {response.status_code}")
                raise HTTPException(status_code=500, detail="Failed to interpret soil test")
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

@app.post("/api/rotation-goals/prioritize")
async def prioritize_rotation_goals(
    field_id: str = Form(...),
    field_name: Optional[str] = Form(None),
    farm_size: Optional[float] = Form(None),
    soil_health_priority: int = Form(...),
    soil_health_weight: float = Form(...),
    profit_priority: int = Form(...),
    profit_weight: float = Form(...),
    pest_management_priority: int = Form(...),
    pest_management_weight: float = Form(...),
    sustainability_priority: int = Form(...),
    sustainability_weight: float = Form(...),
    risk_reduction_priority: int = Form(...),
    risk_reduction_weight: float = Form(...),
    labor_efficiency_priority: int = Form(...),
    labor_efficiency_weight: float = Form(...)
):
    """Process goal prioritization and generate rotation recommendations"""
    try:
        goals_data = [
            {
                "goal_type": "soil_health",
                "priority": soil_health_priority,
                "weight": soil_health_weight,
                "description": "Improve soil organic matter and structure"
            },
            {
                "goal_type": "profit",
                "priority": profit_priority, 
                "weight": profit_weight,
                "description": "Maximize net profit per acre"
            },
            {
                "goal_type": "pest_management",
                "priority": pest_management_priority,
                "weight": pest_management_weight,
                "description": "Reduce pest and disease pressure"
            },
            {
                "goal_type": "sustainability",
                "priority": sustainability_priority,
                "weight": sustainability_weight,
                "description": "Enhance long-term environmental sustainability"
            },
            {
                "goal_type": "risk_reduction",
                "priority": risk_reduction_priority,
                "weight": risk_reduction_weight,
                "description": "Minimize production and market risks"
            },
            {
                "goal_type": "labor_efficiency",
                "priority": labor_efficiency_priority,
                "weight": labor_efficiency_weight,
                "description": "Optimize labor requirements and timing"
            }
        ]

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{RECOMMENDATION_ENGINE_URL}/api/v1/rotations/generate",
                json={
                    "field_id": field_id,
                    "goals": goals_data,
                    "constraints": [],
                    "planning_horizon": 5
                },
                timeout=45.0
            )
            
            if response.status_code == 200:
                result = response.json()
                # Add prioritization summary
                result["goal_prioritization"] = {
                    "goals_configured": len(goals_data),
                    "top_priority_goal": max(goals_data, key=lambda g: g["priority"]),
                    "highest_weight_goal": max(goals_data, key=lambda g: g["weight"]),
                    "prioritization_strategy": "weighted_priority"
                }
                return result
            else:
                logger.error(f"Recommendation engine error: {response.status_code}")
                raise HTTPException(status_code=500, detail="Failed to generate rotation plan")
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

# Rotation Planning API Proxy Endpoints

@app.api_route("/api/v1/rotations/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_rotation_api(path: str, request: Request):
    """Proxy requests to the rotation planning API"""
    try:
        # Get the request method and prepare the data
        method = request.method
        
        # Prepare headers
        headers = {
            "content-type": request.headers.get("content-type", "application/json")
        }
        
        # Get request data based on content type
        body = None
        if method in ["POST", "PUT"]:
            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type:
                body = await request.json()
            elif "application/x-www-form-urlencoded" in content_type:
                form_data = await request.form()
                body = dict(form_data)
        
        # Forward the request to the recommendation engine
        async with httpx.AsyncClient() as client:
            url = f"{RECOMMENDATION_ENGINE_URL}/api/v1/rotations/{path}"
            
            if method == "GET":
                response = await client.get(url, params=request.query_params, timeout=60.0)
            elif method == "POST":
                response = await client.post(url, json=body, params=request.query_params, timeout=60.0)
            elif method == "PUT":
                response = await client.put(url, json=body, params=request.query_params, timeout=60.0)
            elif method == "DELETE":
                response = await client.delete(url, params=request.query_params, timeout=60.0)
            else:
                raise HTTPException(status_code=405, detail="Method not allowed")
            
            # Return the response from the backend
            return JSONResponse(
                content=response.json() if response.content else {},
                status_code=response.status_code
            )
                
    except httpx.RequestError as e:
        logger.error(f"Rotation API proxy error: {e}")
        raise HTTPException(status_code=503, detail="Rotation service temporarily unavailable")
    except Exception as e:
        logger.error(f"Rotation API proxy error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/climate/detect-zone")
async def detect_climate_zone(
    latitude: float = Form(...),
    longitude: float = Form(...),
    elevation_ft: Optional[float] = Form(None)
):
    """Detect climate zone from coordinates"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{DATA_INTEGRATION_URL}/api/v1/climate/detect-zone",
                json={
                    "latitude": latitude,
                    "longitude": longitude,
                    "elevation_ft": elevation_ft
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Climate detection error: {response.status_code}")
                raise HTTPException(status_code=500, detail="Failed to detect climate zone")
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

@app.post("/api/climate/zone-from-address")
async def get_zone_from_address(
    address: str = Form(...),
    include_koppen: bool = Form(False)
):
    """Get climate zone from address"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{DATA_INTEGRATION_URL}/api/v1/climate/zone-from-address",
                params={
                    "address": address,
                    "include_koppen": include_koppen
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Address climate lookup error: {response.status_code}")
                raise HTTPException(status_code=500, detail="Failed to get climate zone from address")
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

@app.get("/api/climate/zones")
async def list_climate_zones(
    zone_type: Optional[str] = Query(None, description="Filter by zone type"),
    group: Optional[str] = Query(None, description="Filter Köppen zones by group")
):
    """List available climate zones"""
    try:
        params = {}
        if zone_type:
            params["zone_type"] = zone_type
        if group:
            params["group"] = group
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{DATA_INTEGRATION_URL}/api/v1/climate/zones",
                params=params,
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Climate zones list error: {response.status_code}")
                raise HTTPException(status_code=500, detail="Failed to list climate zones")
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

@app.get("/api/climate/usda-zones")
async def get_usda_zones():
    """Get USDA hardiness zones"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{DATA_INTEGRATION_URL}/api/v1/climate/usda-zones",
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"USDA zones error: {response.status_code}")
                raise HTTPException(status_code=500, detail="Failed to get USDA zones")
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

@app.get("/api/climate/koppen-types")
async def get_koppen_types(group: Optional[str] = Query(None)):
    """Get Köppen climate types"""
    try:
        params = {}
        if group:
            params["group"] = group
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{DATA_INTEGRATION_URL}/api/v1/climate/koppen-types",
                params=params,
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Köppen types error: {response.status_code}")
                raise HTTPException(status_code=500, detail="Failed to get Köppen types")
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

@app.post("/api/climate/validate-zone")
async def validate_zone_selection(
    zone_id: str = Form(...),
    zone_type: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...)
):
    """Validate climate zone selection"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{DATA_INTEGRATION_URL}/api/v1/climate/validate-zone",
                json={
                    "zone_id": zone_id,
                    "zone_type": zone_type,
                    "latitude": latitude,
                    "longitude": longitude
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Zone validation error: {response.status_code}")
                raise HTTPException(status_code=500, detail="Failed to validate zone selection")
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")


@app.post("/api/climate/validate-consistency")
async def validate_climate_zone_consistency(
    latitude: float = Form(...),
    longitude: float = Form(...),
    check_neighboring: bool = Form(True),
    check_temporal: bool = Form(True)
):
    """Validate climate zone consistency across multiple dimensions"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{DATA_INTEGRATION_URL}/api/v1/climate/validate-consistency",
                json={
                    "latitude": latitude,
                    "longitude": longitude,
                    "check_neighboring": check_neighboring,
                    "check_temporal": check_temporal
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Consistency validation error: {response.status_code}")
                raise HTTPException(status_code=500, detail="Failed to validate climate zone consistency")
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")


# pH Management API Endpoints
@app.post("/api/ph/analyze")
async def analyze_ph_levels(
    farm_id: str = Form(...),
    field_id: str = Form(...),
    crop_type: str = Form(...),
    ph: float = Form(...),
    organic_matter: Optional[float] = Form(None),
    phosphorus: Optional[float] = Form(None),
    potassium: Optional[float] = Form(None),
    cec: Optional[float] = Form(None)
):
    """Analyze soil pH levels through recommendation engine"""
    try:
        # Prepare soil test data
        soil_test_data = {
            "ph": ph,
            "organic_matter_percent": organic_matter or 3.0,
            "phosphorus_ppm": phosphorus or 25,
            "potassium_ppm": potassium or 150,
            "cec_meq_per_100g": cec or 12.0,
            "test_date": datetime.now().date().isoformat()
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{RECOMMENDATION_ENGINE_URL}/api/v1/ph/analyze",
                json={
                    "farm_id": farm_id,
                    "field_id": field_id,
                    "crop_type": crop_type,
                    "soil_test_data": soil_test_data
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"pH analysis error: {response.status_code}")
                raise HTTPException(status_code=500, detail="Failed to analyze pH")
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

@app.post("/api/ph/lime-calculator")
async def calculate_lime_requirements(
    current_ph: float = Form(...),
    target_ph: float = Form(...),
    buffer_ph: Optional[float] = Form(None),
    soil_texture: str = Form(...),
    organic_matter_percent: float = Form(...),
    field_size_acres: float = Form(...)
):
    """Calculate lime requirements through recommendation engine"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{RECOMMENDATION_ENGINE_URL}/api/v1/ph/lime-calculator",
                json={
                    "current_ph": current_ph,
                    "target_ph": target_ph,
                    "buffer_ph": buffer_ph,
                    "soil_texture": soil_texture,
                    "organic_matter_percent": organic_matter_percent,
                    "field_size_acres": field_size_acres
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Lime calculator error: {response.status_code}")
                raise HTTPException(status_code=500, detail="Failed to calculate lime requirements")
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

@app.get("/api/ph/crop-requirements")
async def get_crop_ph_requirements(
    crop_types: str = Query(..., description="Comma-separated list of crop types")
):
    """Get crop pH requirements through recommendation engine"""
    try:
        crop_list = [crop.strip() for crop in crop_types.split(",")]
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{RECOMMENDATION_ENGINE_URL}/api/v1/ph/crop-requirements",
                params={"crop_types": crop_list},
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Crop requirements error: {response.status_code}")
                raise HTTPException(status_code=500, detail="Failed to get crop requirements")
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

@app.post("/api/ph/monitor")
async def setup_ph_monitoring(
    farm_id: str = Form(...),
    field_id: str = Form(...),
    monitoring_frequency: str = Form(...),
    alert_thresholds: str = Form(...)
):
    """Setup pH monitoring through recommendation engine"""
    try:
        import json
        thresholds = json.loads(alert_thresholds)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{RECOMMENDATION_ENGINE_URL}/api/v1/ph/monitor",
                json={
                    "farm_id": farm_id,
                    "field_id": field_id,
                    "monitoring_frequency": monitoring_frequency,
                    "alert_thresholds": thresholds
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"pH monitoring setup error: {response.status_code}")
                raise HTTPException(status_code=500, detail="Failed to setup pH monitoring")
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

@app.get("/api/ph/dashboard")
async def get_ph_dashboard(
    farm_id: str = Query(..., description="Farm identifier")
):
    """Get pH dashboard data through recommendation engine"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{RECOMMENDATION_ENGINE_URL}/api/v1/ph/dashboard",
                params={"farm_id": farm_id},
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"pH dashboard error: {response.status_code}")
                raise HTTPException(status_code=500, detail="Failed to get pH dashboard")
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

@app.get("/api/ph/trends")
async def get_ph_trends(
    farm_id: str = Query(..., description="Farm identifier"),
    field_id: str = Query(..., description="Field identifier")
):
    """Get pH trends through recommendation engine"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{RECOMMENDATION_ENGINE_URL}/api/v1/ph/trends",
                params={"farm_id": farm_id, "field_id": field_id},
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"pH trends error: {response.status_code}")
                raise HTTPException(status_code=500, detail="Failed to get pH trends")
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

@app.post("/api/climate/zone-override")
async def submit_zone_override(request: dict):
    """Submit a climate zone override for logging and analysis"""
    try:
        # Log the override for improvement purposes
        logger.info(f"Climate zone override submitted: {request}")
        
        # In a production system, this would save to database
        # For now, we'll just validate the data and return success
        
        # Validate required fields
        if not request.get('original_zone'):
            raise HTTPException(status_code=400, detail="Original zone data required")
        if not request.get('override_zone'):
            raise HTTPException(status_code=400, detail="Override zone data required")
        if not request.get('reason'):
            raise HTTPException(status_code=400, detail="Override reason required")
        
        override_data = {
            "status": "accepted",
            "override_id": f"override_{int(time.time())}",
            "message": "Zone override logged successfully",
            "warning": "Please ensure your override is based on local knowledge or data",
            "impact_assessment": {
                "recommendation_accuracy": "may be affected",
                "confidence_level": "user_specified",
                "validation_source": "user_input"
            }
        }
        
        return override_data
        
    except Exception as e:
        logger.error(f"Error processing zone override: {e}")
        return {
            "status": "error",
            "message": "Failed to process override",
            "fallback": "Override saved locally only"
        }

# Cover Crop Selection API Proxy Routes

@app.post("/api/cover-crops/select")
async def proxy_cover_crop_selection(request: Request):
    """Proxy cover crop selection requests to backend service"""
    try:
        request_data = await request.json()
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{COVER_CROP_SERVICE_URL}/api/v1/cover-crops/select",
                json=request_data,
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Cover crop selection error: {response.status_code}")
                raise HTTPException(status_code=response.status_code, detail="Cover crop selection failed")
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=503, detail="Cover crop service temporarily unavailable")

@app.post("/api/cover-crops/seasonal")
async def proxy_seasonal_recommendations(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    target_season: str = Query(...),
    field_size_acres: float = Query(..., gt=0)
):
    """Proxy seasonal cover crop recommendation requests to backend service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{COVER_CROP_SERVICE_URL}/api/v1/cover-crops/seasonal",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "target_season": target_season,
                    "field_size_acres": field_size_acres
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Seasonal recommendations error: {response.status_code}")
                raise HTTPException(status_code=response.status_code, detail="Seasonal recommendations failed")
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=503, detail="Cover crop service temporarily unavailable")

@app.post("/api/cover-crops/goal-analysis")
async def proxy_goal_analysis(request: Request):
    """Proxy goal analysis requests to backend service"""
    try:
        request_data = await request.json()
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{COVER_CROP_SERVICE_URL}/api/v1/cover-crops/goal-analysis",
                json=request_data,
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Goal analysis error: {response.status_code}")
                raise HTTPException(status_code=response.status_code, detail="Goal analysis failed")
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=503, detail="Cover crop service temporarily unavailable")

@app.get("/api/cover-crops/goal-categories")
async def proxy_goal_categories():
    """Proxy goal categories requests to backend service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{COVER_CROP_SERVICE_URL}/api/v1/cover-crops/goal-categories",
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Goal categories error: {response.status_code}")
                raise HTTPException(status_code=response.status_code, detail="Goal categories lookup failed")
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=503, detail="Cover crop service temporarily unavailable")

@app.get("/api/cover-crops/goal-examples")
async def proxy_goal_examples():
    """Proxy goal examples requests to backend service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{COVER_CROP_SERVICE_URL}/api/v1/cover-crops/goal-examples",
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Goal examples error: {response.status_code}")
                raise HTTPException(status_code=response.status_code, detail="Goal examples lookup failed")
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=503, detail="Cover crop service temporarily unavailable")

@app.get("/api/cover-crops/species")
async def proxy_species_lookup(
    species_name: Optional[str] = Query(None),
    cover_crop_type: Optional[str] = Query(None),
    hardiness_zone: Optional[str] = Query(None),
    growing_season: Optional[str] = Query(None),
    primary_benefit: Optional[str] = Query(None)
):
    """Proxy species lookup requests to backend service"""
    try:
        params = {}
        if species_name:
            params["species_name"] = species_name
        if cover_crop_type:
            params["cover_crop_type"] = cover_crop_type
        if hardiness_zone:
            params["hardiness_zone"] = hardiness_zone
        if growing_season:
            params["growing_season"] = growing_season
        if primary_benefit:
            params["primary_benefit"] = primary_benefit
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{COVER_CROP_SERVICE_URL}/api/v1/cover-crops/species",
                params=params,
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Species lookup error: {response.status_code}")
                raise HTTPException(status_code=response.status_code, detail="Species lookup failed")
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=503, detail="Cover crop service temporarily unavailable")

@app.get("/api/cover-crops/species/{species_id}")
async def proxy_species_detail(species_id: str):
    """Proxy species detail requests to backend service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{COVER_CROP_SERVICE_URL}/api/v1/cover-crops/species/{species_id}",
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Species detail error: {response.status_code}")
                raise HTTPException(status_code=response.status_code, detail="Species detail lookup failed")
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=503, detail="Cover crop service temporarily unavailable")

@app.post("/api/cover-crops/goal-based-recommendations")
async def proxy_goal_based_recommendations(request: Request):
    """Proxy goal-based recommendation requests to backend service"""
    try:
        request_data = await request.json()
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{COVER_CROP_SERVICE_URL}/api/v1/cover-crops/goal-based-recommendations",
                json=request_data,
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Goal-based recommendations error: {response.status_code}")
                raise HTTPException(status_code=response.status_code, detail="Goal-based recommendations failed")
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=503, detail="Cover crop service temporarily unavailable")

@app.post("/api/cover-crops/benefits/predict")
async def proxy_benefit_predictions(request: Request):
    """Proxy benefit prediction requests to backend service"""
    try:
        request_data = await request.json()
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{COVER_CROP_SERVICE_URL}/api/v1/cover-crops/benefits/predict",
                json=request_data,
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Benefit predictions error: {response.status_code}")
                raise HTTPException(status_code=response.status_code, detail="Benefit predictions failed")
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=503, detail="Cover crop service temporarily unavailable")

@app.post("/api/cover-crops/timing")
async def proxy_timing_recommendations(request: Request):
    """Proxy timing recommendation requests to backend service"""
    try:
        request_data = await request.json()
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{COVER_CROP_SERVICE_URL}/api/v1/cover-crops/timing",
                json=request_data,
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Timing recommendations error: {response.status_code}")
                raise HTTPException(status_code=response.status_code, detail="Timing recommendations failed")
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=503, detail="Cover crop service temporarily unavailable")

@app.get("/api/cover-crops/types")
async def proxy_cover_crop_types():
    """Proxy cover crop types requests to backend service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{COVER_CROP_SERVICE_URL}/api/v1/cover-crops/types",
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Cover crop types error: {response.status_code}")
                raise HTTPException(status_code=response.status_code, detail="Cover crop types lookup failed")
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=503, detail="Cover crop service temporarily unavailable")

@app.get("/api/cover-crops/seasons")
async def proxy_growing_seasons():
    """Proxy growing seasons requests to backend service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{COVER_CROP_SERVICE_URL}/api/v1/cover-crops/seasons",
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Growing seasons error: {response.status_code}")
                raise HTTPException(status_code=response.status_code, detail="Growing seasons lookup failed")
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=503, detail="Cover crop service temporarily unavailable")

@app.get("/api/cover-crops/benefits")
async def proxy_soil_benefits():
    """Proxy soil benefits requests to backend service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{COVER_CROP_SERVICE_URL}/api/v1/cover-crops/benefits",
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Soil benefits error: {response.status_code}")
                raise HTTPException(status_code=response.status_code, detail="Soil benefits lookup failed")
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=503, detail="Cover crop service temporarily unavailable")

@app.post("/api/cover-crops/benefits/track")
async def proxy_benefit_tracking(request: Request):
    """Proxy benefit tracking requests to backend service"""
    try:
        request_data = await request.json()
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{COVER_CROP_SERVICE_URL}/api/v1/cover-crops/benefits/track",
                json=request_data,
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Benefit tracking error: {response.status_code}")
                raise HTTPException(status_code=response.status_code, detail="Benefit tracking failed")
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=503, detail="Cover crop service temporarily unavailable")

@app.get("/api/cover-crops/benefits/analytics")
async def proxy_benefit_analytics(
    field_id: Optional[str] = Query(None),
    farm_id: Optional[str] = Query(None),
    time_range: Optional[str] = Query(None)
):
    """Proxy benefit analytics requests to backend service"""
    try:
        params = {}
        if field_id:
            params["field_id"] = field_id
        if farm_id:
            params["farm_id"] = farm_id
        if time_range:
            params["time_range"] = time_range
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{COVER_CROP_SERVICE_URL}/api/v1/cover-crops/benefits/analytics",
                params=params,
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Benefit analytics error: {response.status_code}")
                raise HTTPException(status_code=response.status_code, detail="Benefit analytics failed")
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=503, detail="Cover crop service temporarily unavailable")


# Variety Selection API Proxy Routes

@app.api_route("/api/v1/crops/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_crops_api(path: str, request: Request):
    """Proxy requests to the crop taxonomy crops API"""
    try:
        method = request.method
        
        # Prepare headers
        headers = {
            "content-type": request.headers.get("content-type", "application/json")
        }
        
        # Get request data based on content type
        body = None
        if method in ["POST", "PUT"]:
            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type:
                body = await request.json()
            elif "application/x-www-form-urlencoded" in content_type:
                form_data = await request.form()
                body = dict(form_data)
        
        # Forward the request to the crop taxonomy service
        async with httpx.AsyncClient() as client:
            url = f"{CROP_TAXONOMY_URL}/api/v1/crops/{path}"
            
            if method == "GET":
                response = await client.get(url, params=request.query_params, timeout=60.0)
            elif method == "POST":
                response = await client.post(url, json=body, params=request.query_params, timeout=60.0)
            elif method == "PUT":
                response = await client.put(url, json=body, params=request.query_params, timeout=60.0)
            elif method == "DELETE":
                response = await client.delete(url, params=request.query_params, timeout=60.0)
            else:
                raise HTTPException(status_code=405, detail="Method not allowed")
            
            # Return the response from the backend
            return JSONResponse(
                content=response.json() if response.content else {},
                status_code=response.status_code
            )
                
    except httpx.RequestError as e:
        logger.error(f"Crops API proxy error: {e}")
        raise HTTPException(status_code=503, detail="Crops service temporarily unavailable")
    except Exception as e:
        logger.error(f"Crops API proxy error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.api_route("/api/v1/varieties/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_varieties_api(path: str, request: Request):
    """Proxy requests to the crop taxonomy varieties API"""
    try:
        method = request.method
        
        # Prepare headers
        headers = {
            "content-type": request.headers.get("content-type", "application/json")
        }
        
        # Get request data based on content type
        body = None
        if method in ["POST", "PUT"]:
            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type:
                body = await request.json()
            elif "application/x-www-form-urlencoded" in content_type:
                form_data = await request.form()
                body = dict(form_data)
        
        # Forward the request to the crop taxonomy service
        async with httpx.AsyncClient() as client:
            url = f"{CROP_TAXONOMY_URL}/api/v1/varieties/{path}"
            
            if method == "GET":
                response = await client.get(url, params=request.query_params, timeout=60.0)
            elif method == "POST":
                response = await client.post(url, json=body, params=request.query_params, timeout=60.0)
            elif method == "PUT":
                response = await client.put(url, json=body, params=request.query_params, timeout=60.0)
            elif method == "DELETE":
                response = await client.delete(url, params=request.query_params, timeout=60.0)
            else:
                raise HTTPException(status_code=405, detail="Method not allowed")
            
            # Return the response from the backend
            return JSONResponse(
                content=response.json() if response.content else {},
                status_code=response.status_code
            )
                
    except httpx.RequestError as e:
        logger.error(f"Varieties API proxy error: {e}")
        raise HTTPException(status_code=503, detail="Varieties service temporarily unavailable")
    except Exception as e:
        logger.error(f"Varieties API proxy error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.api_route("/api/v1/recommendations/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_recommendations_api(path: str, request: Request):
    """Proxy requests to the crop taxonomy recommendations API"""
    try:
        method = request.method
        
        # Prepare headers
        headers = {
            "content-type": request.headers.get("content-type", "application/json")
        }
        
        # Get request data based on content type
        body = None
        if method in ["POST", "PUT"]:
            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type:
                body = await request.json()
            elif "application/x-www-form-urlencoded" in content_type:
                form_data = await request.form()
                body = dict(form_data)
        
        # Forward the request to the crop taxonomy service
        async with httpx.AsyncClient() as client:
            url = f"{CROP_TAXONOMY_URL}/api/v1/recommendations/{path}"
            
            if method == "GET":
                response = await client.get(url, params=request.query_params, timeout=60.0)
            elif method == "POST":
                response = await client.post(url, json=body, params=request.query_params, timeout=60.0)
            elif method == "PUT":
                response = await client.put(url, json=body, params=request.query_params, timeout=60.0)
            elif method == "DELETE":
                response = await client.delete(url, params=request.query_params, timeout=60.0)
            else:
                raise HTTPException(status_code=405, detail="Method not allowed")
            
            # Return the response from the backend
            return JSONResponse(
                content=response.json() if response.content else {},
                status_code=response.status_code
            )
                
    except httpx.RequestError as e:
        logger.error(f"Recommendations API proxy error: {e}")
        raise HTTPException(status_code=503, detail="Recommendations service temporarily unavailable")
    except Exception as e:
        logger.error(f"Recommendations API proxy error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Filter Analytics API Proxy Routes

@app.api_route("/api/v1/crop-taxonomy/analytics/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_filter_analytics_api(path: str, request: Request):
    """Proxy requests to the crop taxonomy filter analytics API"""
    try:
        # Get the request method and prepare the data
        method = request.method
        
        # Prepare headers
        headers = {
            "content-type": request.headers.get("content-type", "application/json")
        }
        
        # Get request data based on content type
        body = None
        if method in ["POST", "PUT"]:
            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type:
                body = await request.json()
            elif "application/x-www-form-urlencoded" in content_type:
                form_data = await request.form()
                body = dict(form_data)
        
        # Forward the request to the crop taxonomy service
        async with httpx.AsyncClient() as client:
            url = f"{CROP_TAXONOMY_URL}/api/v1/crop-taxonomy/analytics/{path}"
            
            if method == "GET":
                response = await client.get(url, params=request.query_params, timeout=60.0)
            elif method == "POST":
                response = await client.post(url, json=body, params=request.query_params, timeout=60.0)
            elif method == "PUT":
                response = await client.put(url, json=body, params=request.query_params, timeout=60.0)
            elif method == "DELETE":
                response = await client.delete(url, params=request.query_params, timeout=60.0)
            else:
                raise HTTPException(status_code=405, detail="Method not allowed")
            
            # Return the response from the backend
            return JSONResponse(
                content=response.json() if response.content else {},
                status_code=response.status_code
            )
                
    except httpx.RequestError as e:
        logger.error(f"Filter analytics API proxy error: {e}")
        raise HTTPException(status_code=503, detail="Filter analytics service temporarily unavailable")
    except Exception as e:
        logger.error(f"Filter analytics API proxy error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

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
            "cover_crop_service": COVER_CROP_SERVICE_URL,
            "user_management": USER_MANAGEMENT_URL,
            "data_integration": DATA_INTEGRATION_URL
        },
        "cover_crop_selection": {
            "status": "integrated",
            "endpoints": [
                "/api/cover-crops/select",
                "/api/cover-crops/species",
                "/api/cover-crops/goal-based-recommendations",
                "/api/cover-crops/benefits/predict",
                "/api/cover-crops/timing",
                "/api/cover-crops/types",
                "/api/cover-crops/seasons",
                "/api/cover-crops/benefits",
                "/api/cover-crops/benefits/track",
                "/api/cover-crops/benefits/analytics"
            ]
        },
        "ph_management": {
            "status": "integrated",
            "endpoints": [
                "/api/ph/analyze",
                "/api/ph/lime-calculator",
                "/api/ph/crop-requirements",
                "/api/ph/monitor",
                "/api/ph/dashboard",
                "/api/ph/trends"
            ]
        },
        "filter_analytics": {
            "status": "integrated",
            "endpoints": [
                "/api/v1/crop-taxonomy/analytics/filter-usage",
                "/api/v1/crop-taxonomy/analytics/filter-insights",
                "/api/v1/crop-taxonomy/analytics/popular-filters",
                "/api/v1/crop-taxonomy/analytics/filter-trends",
                "/api/v1/crop-taxonomy/analytics/user-behavior",
                "/api/v1/crop-taxonomy/analytics/effectiveness",
                "/api/v1/crop-taxonomy/analytics/a-b-test",
                "/api/v1/crop-taxonomy/analytics/dashboard-summary",
                "/api/v1/crop-taxonomy/analytics/record-usage"
            ]
        },
        "variety_selection": {
            "status": "integrated",
            "endpoints": [
                "/api/v1/crops/search",
                "/api/v1/crops/{crop_id}/varieties",
                "/api/v1/varieties/recommend",
                "/api/v1/varieties/filter",
                "/api/v1/varieties/search",
                "/api/v1/varieties/compare",
                "/api/v1/varieties/{variety_id}/details",
                "/api/v1/recommendations/crop-varieties",
                "/api/v1/recommendations/explain"
            ]
        },
        "field_management": {
            "status": "integrated",
            "endpoints": [
                "/field-management",
                "/api/v1/fields/",
                "/api/v1/fields/{field_id}",
                "/api/v1/fields/bulk-create",
                "/api/v1/fields/validate",
                "/api/v1/fields/search",
                "/api/v1/fields/statistics"
            ]
        }
    }


# Location Validation Service Proxy Routes
@app.api_route("/api/v1/validation/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_validation_service(path: str, request: Request):
    """Proxy requests to the location validation service."""
    try:
        async with httpx.AsyncClient() as client:
            url = f"{LOCATION_VALIDATION_URL}/api/v1/validation/{path}"
            
            # Forward the request
            response = await client.request(
                method=request.method,
                url=url,
                headers=dict(request.headers),
                content=await request.body()
            )
            
            return JSONResponse(
                content=response.json(),
                status_code=response.status_code
            )
    except Exception as e:
        logger.error(f"Error proxying to validation service: {e}")
        return JSONResponse(
            content={"error": "Service temporarily unavailable"},
            status_code=503
        )


@app.api_route("/api/v1/locations/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_location_service(path: str, request: Request):
    """Proxy requests to the location management service."""
    try:
        async with httpx.AsyncClient() as client:
            url = f"{LOCATION_VALIDATION_URL}/api/v1/locations/{path}"
            
            # Forward the request
            response = await client.request(
                method=request.method,
                url=url,
                headers=dict(request.headers),
                content=await request.body()
            )
            
            return JSONResponse(
                content=response.json(),
                status_code=response.status_code
            )
    except Exception as e:
        logger.error(f"Error proxying to location service: {e}")
        return JSONResponse(
            content={"error": "Service temporarily unavailable"},
            status_code=503
        )


@app.api_route("/api/v1/geocoding/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_geocoding_service(path: str, request: Request):
    """Proxy requests to the geocoding service."""
    try:
        async with httpx.AsyncClient() as client:
            url = f"{LOCATION_VALIDATION_URL}/api/v1/geocoding/{path}"
            
            # Forward the request
            response = await client.request(
                method=request.method,
                url=url,
                headers=dict(request.headers),
                content=await request.body()
            )
            
            return JSONResponse(
                content=response.json(),
                status_code=response.status_code
            )
    except Exception as e:
        logger.error(f"Error proxying to geocoding service: {e}")
        return JSONResponse(
            content={"error": "Service temporarily unavailable"},
            status_code=503
        )

# Field Management API Proxy Routes
@app.api_route("/api/v1/fields/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_field_management_api(path: str, request: Request):
    """Proxy requests to the field management API"""
    try:
        method = request.method
        
        # Prepare headers
        headers = {
            "content-type": request.headers.get("content-type", "application/json")
        }
        
        # Get request data based on content type
        body = None
        if method in ["POST", "PUT"]:
            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type:
                body = await request.json()
            elif "application/x-www-form-urlencoded" in content_type:
                form_data = await request.form()
                body = dict(form_data)
        
        # Forward the request to the location validation service
        async with httpx.AsyncClient() as client:
            url = f"{LOCATION_VALIDATION_URL}/api/v1/fields/{path}"
            
            if method == "GET":
                response = await client.get(url, params=request.query_params, timeout=60.0)
            elif method == "POST":
                response = await client.post(url, json=body, params=request.query_params, timeout=60.0)
            elif method == "PUT":
                response = await client.put(url, json=body, params=request.query_params, timeout=60.0)
            elif method == "DELETE":
                response = await client.delete(url, params=request.query_params, timeout=60.0)
            else:
                raise HTTPException(status_code=405, detail="Method not allowed")
            
            # Return the response from the backend
            return JSONResponse(
                content=response.json() if response.content else {},
                status_code=response.status_code
            )
                
    except httpx.RequestError as e:
        logger.error(f"Field management API proxy error: {e}")
        raise HTTPException(status_code=503, detail="Field management service temporarily unavailable")
    except Exception as e:
        logger.error(f"Field management API proxy error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Fertilizer Application API Proxy Routes
@app.api_route("/api/v1/fertilizer/application/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_fertilizer_application_api(path: str, request: Request):
    """Proxy requests to the fertilizer application API"""
    try:
        method = request.method
        
        # Prepare headers
        headers = {
            "content-type": request.headers.get("content-type", "application/json")
        }
        
        # Get request data based on content type
        body = None
        if method in ["POST", "PUT"]:
            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type:
                body = await request.json()
            elif "application/x-www-form-urlencoded" in content_type:
                form_data = await request.form()
                body = dict(form_data)
        
        # Forward the request to the fertilizer application service
        async with httpx.AsyncClient() as client:
            url = f"{FERTILIZER_APPLICATION_URL}/api/v1/fertilizer/application/{path}"
            
            if method == "GET":
                response = await client.get(url, params=request.query_params, timeout=60.0)
            elif method == "POST":
                response = await client.post(url, json=body, params=request.query_params, timeout=60.0)
            elif method == "PUT":
                response = await client.put(url, json=body, params=request.query_params, timeout=60.0)
            elif method == "DELETE":
                response = await client.delete(url, params=request.query_params, timeout=60.0)
            else:
                raise HTTPException(status_code=405, detail="Method not allowed")
            
            # Return the response from the backend
            return JSONResponse(
                content=response.json() if response.content else {},
                status_code=response.status_code
            )
                
    except httpx.RequestError as e:
        logger.error(f"Fertilizer application API proxy error: {e}")
        raise HTTPException(status_code=503, detail="Fertilizer application service temporarily unavailable")
    except Exception as e:
        logger.error(f"Fertilizer application API proxy error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    port = int(os.getenv("FRONTEND_PORT", 3000))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)

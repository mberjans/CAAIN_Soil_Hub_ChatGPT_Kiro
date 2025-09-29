"""
Frontend API Routes

FastAPI routes for serving frontend templates and handling dashboard navigation.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

# Initialize router
router = APIRouter()

# Set up templates
template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
templates = Jinja2Templates(directory=template_dir)


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Serve the main dashboard page."""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "title": "Dashboard"
    })


@router.get("/crop-selection", response_class=HTMLResponse)
async def crop_selection(request: Request):
    """Serve the crop selection page."""
    return templates.TemplateResponse("crop_selection.html", {
        "request": request,
        "title": "Crop Selection"
    })


@router.get("/variety-selection", response_class=HTMLResponse)
async def variety_selection(request: Request):
    """Serve the variety selection page."""
    return templates.TemplateResponse("variety_selection.html", {
        "request": request,
        "title": "Variety Selection"
    })


@router.get("/crop-filtering", response_class=HTMLResponse)
async def crop_filtering(request: Request):
    """Serve the crop filtering page."""
    return templates.TemplateResponse("crop_filtering.html", {
        "request": request,
        "title": "Crop Filtering"
    })


@router.get("/filter-analytics", response_class=HTMLResponse)
async def filter_analytics(request: Request):
    """Serve the filter analytics dashboard page."""
    return templates.TemplateResponse("filter_analytics.html", {
        "request": request,
        "title": "Filter Analytics"
    })


@router.get("/soil-fertility", response_class=HTMLResponse)
async def soil_fertility(request: Request):
    """Serve the soil fertility page."""
    return templates.TemplateResponse("soil_fertility.html", {
        "request": request,
        "title": "Soil Fertility"
    })


@router.get("/fertilizer-strategy", response_class=HTMLResponse)
async def fertilizer_strategy(request: Request):
    """Serve the fertilizer strategy page."""
    return templates.TemplateResponse("fertilizer_strategy.html", {
        "request": request,
        "title": "Fertilizer Strategy"
    })


@router.get("/rotation-planning", response_class=HTMLResponse)
async def rotation_planning(request: Request):
    """Serve the rotation planning page."""
    return templates.TemplateResponse("rotation_planning.html", {
        "request": request,
        "title": "Rotation Planning"
    })


@router.get("/cover-crop-selection", response_class=HTMLResponse)
async def cover_crop_selection(request: Request):
    """Serve the cover crop selection page."""
    return templates.TemplateResponse("cover_crop_selection.html", {
        "request": request,
        "title": "Cover Crop Selection"
    })


@router.get("/ph-management", response_class=HTMLResponse)
async def ph_management(request: Request):
    """Serve the pH management page."""
    return templates.TemplateResponse("ph_management.html", {
        "request": request,
        "title": "pH Management"
    })


@router.get("/climate-zone-selection", response_class=HTMLResponse)
async def climate_zone_selection(request: Request):
    """Serve the climate zone selection page."""
    return templates.TemplateResponse("climate_zone_selection.html", {
        "request": request,
        "title": "Climate Zone Selection"
    })


@router.get("/goal-prioritization", response_class=HTMLResponse)
async def goal_prioritization(request: Request):
    """Serve the goal prioritization page."""
    return templates.TemplateResponse("goal_prioritization.html", {
        "request": request,
        "title": "Goal Prioritization"
    })


@router.get("/mobile-crop-filtering", response_class=HTMLResponse)
async def mobile_crop_filtering(request: Request):
    """Serve the mobile crop filtering page."""
    return templates.TemplateResponse("mobile_crop_filtering.html", {
        "request": request,
        "title": "Mobile Crop Filtering"
    })


@router.get("/mobile-deficiency-detection", response_class=HTMLResponse)
async def mobile_deficiency_detection(request: Request):
    """Serve the mobile deficiency detection page."""
    return templates.TemplateResponse("mobile_deficiency_detection.html", {
        "request": request,
        "title": "Deficiency Detection"
    })


@router.get("/mobile-ph-management", response_class=HTMLResponse)
async def mobile_ph_management(request: Request):
    """Serve the mobile pH management page."""
    return templates.TemplateResponse("mobile_ph_management.html", {
        "request": request,
        "title": "pH Management"
    })


@router.get("/mobile-rotation-planning", response_class=HTMLResponse)
async def mobile_rotation_planning(request: Request):
    """Serve the mobile rotation planning page."""
    return templates.TemplateResponse("mobile_rotation_planning.html", {
        "request": request,
        "title": "Rotation Planning"
    })


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "frontend",
        "version": "1.0.0"
    }
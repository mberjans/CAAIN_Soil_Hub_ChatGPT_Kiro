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


@router.get("/variety-comparison", response_class=HTMLResponse)
async def variety_comparison(request: Request):
    """Serve the variety comparison page."""
    return templates.TemplateResponse("variety_comparison.html", {
        "request": request,
        "title": "Variety Comparison"
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


@router.get("/variety-detail/{variety_id}", response_class=HTMLResponse)
async def variety_detail(request: Request, variety_id: str):
    """Serve the variety detail page."""
    # Mock variety data for demonstration
    variety_data = {
        "id": variety_id,
        "name": f"Variety {variety_id}",
        "description": "High-yielding variety with excellent disease resistance and standability",
        "crop_name": "Corn",
        "seed_company": "Pioneer",
        "release_year": 2020,
        "maturity_group": "110",
        "relative_maturity": 110,
        "yield_potential_percentile": 85,
        "yield_stability_rating": 8.2,
        "standability_rating": 8,
        "market_acceptance_score": 4.2,
        "overall_rating": 4.2,
        "review_count": 127,
        "five_star_count": 45,
        "four_star_count": 35,
        "three_star_count": 15,
        "two_star_count": 3,
        "one_star_count": 2,
        "organic_approved": True,
        "non_gmo_certified": False,
        "seed_availability": "widely_available",
        "patent_status": "active",
        "adapted_regions": ["Midwest", "Great Plains", "Northeast"],
        "disease_resistances": [
            {"disease_name": "Northern Corn Leaf Blight", "resistance_level": "High"},
            {"disease_name": "Gray Leaf Spot", "resistance_level": "High"},
            {"disease_name": "Rust", "resistance_level": "Medium"}
        ],
        "pest_resistances": [
            {"pest_name": "Corn Rootworm", "resistance_level": "High"},
            {"pest_name": "European Corn Borer", "resistance_level": "High"}
        ],
        "herbicide_tolerances": ["Roundup Ready", "Liberty Link"],
        "stress_tolerances": ["Drought", "Heat", "Cold"],
        "quality_characteristics": [
            {"trait_name": "Protein Content", "trait_value": "High"},
            {"trait_name": "Oil Content", "trait_value": "Medium"}
        ],
        "regional_performance_data": [
            {"region_name": "Iowa", "climate_zone": "5a", "performance_index": 0.92, "average_yield": 195, "trials_count": 45},
            {"region_name": "Illinois", "climate_zone": "5b", "performance_index": 0.88, "average_yield": 192, "trials_count": 38},
            {"region_name": "Nebraska", "climate_zone": "5a", "performance_index": 0.85, "average_yield": 188, "trials_count": 32}
        ]
    }
    
    return templates.TemplateResponse("variety_detail.html", {
        "request": request,
        "title": f"Variety Details - {variety_data['name']}",
        "variety": variety_data
    })


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "frontend",
        "version": "1.0.0"
    }
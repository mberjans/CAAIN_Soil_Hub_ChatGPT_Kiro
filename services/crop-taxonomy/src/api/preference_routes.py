"""
Preference API Routes

FastAPI routes for managing farmer crop preference profiles and preference learning.
Includes comprehensive farmer preference storage with hierarchical preferences and versioning.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel

try:  # pragma: no cover - support package imports
    from ..services import CropPreferenceService, crop_preference_service
    from ..services.preference_manager import FarmerPreferenceManager, farmer_preference_manager, PreferenceCategory
    from ..models.preference_models import (
        PreferenceProfileResponse,
        PreferenceUpdateRequest,
        PreferenceLearningRequest,
        PreferenceType,
        PreferenceProfile
    )
except ImportError:  # pragma: no cover
    from services import CropPreferenceService, crop_preference_service
    from services.preference_manager import FarmerPreferenceManager, farmer_preference_manager, PreferenceCategory
    from models.preference_models import (
        PreferenceProfileResponse,
        PreferenceUpdateRequest,
        PreferenceLearningRequest,
        PreferenceType,
        PreferenceProfile
    )

router = APIRouter(prefix="/crop-taxonomy", tags=["preferences"])

# Pydantic models for new comprehensive preference endpoints
class FarmerPreferenceRequest(BaseModel):
    preference_category: str
    preference_data: Dict[str, Any]
    weight: float = 1.0

class FarmerPreferenceResponse(BaseModel):
    id: str
    user_id: str
    preference_category: str
    preference_data: Dict[str, Any]
    weight: float
    created_at: str
    updated_at: str
    version: int
    active: bool

class FarmerPreferenceUpdateRequest(BaseModel):
    preference_data: Optional[Dict[str, Any]] = None
    weight: Optional[float] = None
    active: Optional[bool] = None


def _get_preference_service() -> CropPreferenceService:
    service = crop_preference_service
    if service is None:
        service = CropPreferenceService()
    return service


def _get_farmer_preference_manager() -> FarmerPreferenceManager:
    return farmer_preference_manager


@router.get("/preferences/{user_id}", response_model=PreferenceProfileResponse)
async def get_preference_profile(
    user_id: UUID,
    preference_type: Optional[str] = Query(None, description="Preference type filter")
):
    """Retrieve the crop preference profile for a user."""
    service = _get_preference_service()
    target_type = None
    if preference_type:
        try:
            target_type = PreferenceType(preference_type)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid preference_type value")
    try:
        response = await service.get_preference_profile(user_id, target_type)
        return response
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve preferences: {exc}")


@router.put("/preferences/{user_id}", response_model=PreferenceProfileResponse)
async def update_preference_profile(
    user_id: UUID,
    request: PreferenceUpdateRequest
):
    """Create or update a crop preference profile for a user."""
    service = _get_preference_service()
    try:
        profile_payload = request.profile.model_dump()
        profile_payload['user_id'] = user_id
        normalized_profile = PreferenceProfile(**profile_payload)
        normalized_request = PreferenceUpdateRequest(
            profile=normalized_profile,
            replace_existing=request.replace_existing
        )
        response = await service.upsert_preference_profile(normalized_request)
        return response
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to update preferences: {exc}")


@router.post("/preferences/learn", response_model=PreferenceProfileResponse)
async def learn_preferences(
    request: PreferenceLearningRequest
):
    """Apply learning signals to update a user's crop preference profile."""
    service = _get_preference_service()
    try:
        response = await service.learn_preferences(request)
        return response
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to learn preferences: {exc}")


# Comprehensive Farmer Preference Storage API Endpoints

@router.post("/farmer-preferences/{user_id}", response_model=FarmerPreferenceResponse)
async def create_farmer_preference(
    user_id: UUID,
    request: FarmerPreferenceRequest
):
    """Create a new comprehensive farmer preference."""
    manager = _get_farmer_preference_manager()
    try:
        preference = await manager.create_preference(
            user_id=user_id,
            preference_category=request.preference_category,
            preference_data=request.preference_data,
            weight=request.weight
        )
        return FarmerPreferenceResponse(**preference.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create farmer preference: {e}")


@router.get("/farmer-preferences/{user_id}", response_model=List[FarmerPreferenceResponse])
async def get_farmer_preferences(
    user_id: UUID,
    category: Optional[str] = Query(None, description="Filter by preference category"),
    include_inactive: bool = Query(False, description="Include inactive preferences")
):
    """Get all farmer preferences for a user, optionally filtered by category."""
    manager = _get_farmer_preference_manager()
    try:
        preferences = await manager.get_user_preferences(
            user_id=user_id,
            category=category,
            include_inactive=include_inactive
        )
        return [FarmerPreferenceResponse(**pref.to_dict()) for pref in preferences]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve farmer preferences: {e}")


@router.get("/farmer-preferences/preference/{preference_id}", response_model=FarmerPreferenceResponse)
async def get_farmer_preference_by_id(preference_id: UUID):
    """Get a specific farmer preference by ID."""
    manager = _get_farmer_preference_manager()
    try:
        preference = await manager.get_preference_by_id(preference_id)
        if not preference:
            raise HTTPException(status_code=404, detail="Preference not found")
        return FarmerPreferenceResponse(**preference.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve farmer preference: {e}")


@router.put("/farmer-preferences/preference/{preference_id}", response_model=FarmerPreferenceResponse)
async def update_farmer_preference(
    preference_id: UUID,
    request: FarmerPreferenceUpdateRequest
):
    """Update an existing farmer preference."""
    manager = _get_farmer_preference_manager()
    try:
        preference = await manager.update_preference(
            preference_id=preference_id,
            preference_data=request.preference_data,
            weight=request.weight,
            active=request.active
        )
        return FarmerPreferenceResponse(**preference.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update farmer preference: {e}")


@router.delete("/farmer-preferences/preference/{preference_id}")
async def delete_farmer_preference(preference_id: UUID):
    """Soft delete a farmer preference (sets active = False)."""
    manager = _get_farmer_preference_manager()
    try:
        success = await manager.delete_preference(preference_id)
        if not success:
            raise HTTPException(status_code=404, detail="Preference not found")
        return {"message": "Preference deleted successfully", "preference_id": str(preference_id)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete farmer preference: {e}")


@router.get("/farmer-preferences/{user_id}/hierarchy/{category}")
async def get_preference_hierarchy(
    user_id: UUID,
    category: str
):
    """Get preference hierarchy for a category with inheritance logic."""
    manager = _get_farmer_preference_manager()
    try:
        hierarchy = await manager.get_preference_hierarchy(user_id, category)
        return hierarchy
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve preference hierarchy: {e}")


@router.get("/farmer-preferences/preference/{preference_id}/history")
async def get_preference_history(
    preference_id: UUID,
    limit: int = Query(10, ge=1, le=100, description="Maximum number of history entries")
):
    """Get version history for a farmer preference."""
    manager = _get_farmer_preference_manager()
    try:
        history = await manager.get_preference_history(preference_id, limit)
        return {"preference_id": str(preference_id), "history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve preference history: {e}")


@router.get("/farmer-preferences/categories")
async def get_preference_categories():
    """Get all available preference categories."""
    return {
        "categories": PreferenceCategory.all_categories(),
        "descriptions": {
            "crop_types": "Preferred and avoided crop types, interest in new crops",
            "management_style": "Farming management approach (organic, conventional, precision ag, etc.)",
            "risk_tolerance": "Risk level tolerance and diversification preferences",
            "market_focus": "Market orientation (local, commodity, specialty crops, value-added)",
            "sustainability": "Environmental sustainability priorities",
            "labor_requirements": "Labor availability and automation preferences",
            "equipment_preferences": "Existing and planned equipment, sharing preferences",
            "certification_goals": "Certification targets (organic, GMO-free, sustainable)",
            "yield_priorities": "Yield vs quality preferences",
            "economic_factors": "Economic sensitivity and ROI preferences"
        }
    }

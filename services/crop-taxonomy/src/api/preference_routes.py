"""
Preference API Routes

FastAPI routes for managing farmer crop preference profiles and preference learning.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

try:  # pragma: no cover - support package imports
    from ..services import CropPreferenceService, crop_preference_service
    from ..models.preference_models import (
        PreferenceProfileResponse,
        PreferenceUpdateRequest,
        PreferenceLearningRequest,
        PreferenceType,
        PreferenceProfile
    )
except ImportError:  # pragma: no cover
    from services import CropPreferenceService, crop_preference_service
    from models.preference_models import (
        PreferenceProfileResponse,
        PreferenceUpdateRequest,
        PreferenceLearningRequest,
        PreferenceType,
        PreferenceProfile
    )

router = APIRouter(prefix="/crop-taxonomy", tags=["preferences"])


def _get_preference_service() -> CropPreferenceService:
    service = crop_preference_service
    if service is None:
        service = CropPreferenceService()
    return service


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

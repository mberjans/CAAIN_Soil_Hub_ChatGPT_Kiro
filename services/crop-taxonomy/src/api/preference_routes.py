"""
Preference API Routes

FastAPI routes for managing farmer crop preference profiles and preference learning.
Includes comprehensive farmer preference storage with hierarchical preferences and versioning.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel

try:  # pragma: no cover - support package imports
    from ..services import CropPreferenceService, crop_preference_service
    from ..services.preference_manager import FarmerPreferenceManager, farmer_preference_manager, PreferenceCategory
    from ..services.filter_preset_service import FilterPresetService, filter_preset_service
    from ..models.preference_models import (
        PreferenceProfileResponse,
        PreferenceUpdateRequest,
        PreferenceLearningRequest,
        PreferenceType,
        PreferenceProfile
    )
    from ..models.crop_filtering_models import FilterPreset, FilterPresetSummary, TaxonomyFilterCriteria
    from ..services.filter_engine import filter_combination_engine
except ImportError:  # pragma: no cover
    from services import CropPreferenceService, crop_preference_service
    from services.preference_manager import FarmerPreferenceManager, farmer_preference_manager, PreferenceCategory
    from services.filter_preset_service import FilterPresetService, filter_preset_service
    from models.preference_models import (
        PreferenceProfileResponse,
        PreferenceUpdateRequest,
        PreferenceLearningRequest,
        PreferenceType,
        PreferenceProfile
    )
    from models.crop_filtering_models import FilterPreset, FilterPresetSummary, TaxonomyFilterCriteria
    from services.filter_engine import filter_combination_engine

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


# Filter Preset API Endpoints

class FilterPresetRequest(BaseModel):
    """Request model for creating a filter preset."""
    name: str = Field(..., description="Display name for the preset")
    description: Optional[str] = Field(None, description="Detailed description of the preset")
    filter_config: TaxonomyFilterCriteria = Field(..., description="The filter configuration to save")
    is_public: bool = Field(default=False, description="Whether the preset is publicly visible")
    tags: List[str] = Field(default_factory=list, description="Tags for categorizing the preset")


class FilterPresetResponse(BaseModel):
    """Response model for filter preset operations."""
    preset_id: UUID
    name: str
    description: Optional[str]
    user_id: Optional[UUID]
    filter_config: TaxonomyFilterCriteria
    is_public: bool
    tags: List[str]
    usage_count: int
    created_at: str
    updated_at: str


class FilterPresetListResponse(BaseModel):
    """Response model for filter preset list operations."""
    presets: List[FilterPresetResponse]
    total_count: int
    filtered_by_user: Optional[bool] = None
    filtered_by_public: Optional[bool] = None


def _get_filter_preset_service() -> FilterPresetService:
    return filter_preset_service


@router.post("/preferences/filter-presets", response_model=FilterPresetResponse)
async def save_filter_preset(
    request: FilterPresetRequest,
    user_id: Optional[UUID] = Query(None, description="User ID for personal presets")
):
    """Save a filter preset for later use."""
    service = _get_filter_preset_service()
    try:
        preset = await service.save_preset(
            name=request.name,
            description=request.description,
            filter_config=request.filter_config,
            user_id=user_id,
            is_public=request.is_public,
            tags=request.tags
        )
        
        return FilterPresetResponse(
            preset_id=preset.preset_id,
            name=preset.name,
            description=preset.description,
            user_id=preset.user_id,
            filter_config=preset.filter_config,
            is_public=preset.is_public,
            tags=preset.tags,
            usage_count=preset.usage_count,
            created_at=preset.created_at.isoformat(),
            updated_at=preset.updated_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save filter preset: {str(e)}")


@router.get("/preferences/filter-presets", response_model=FilterPresetListResponse)
async def get_saved_filter_presets(
    user_id: Optional[UUID] = Query(None, description="Filter by user ID"),
    is_public: Optional[bool] = Query(None, description="Filter by public/private status"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of presets to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """Get saved filter presets with optional filtering."""
    service = _get_filter_preset_service()
    try:
        # Process tags parameter if provided
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
        
        presets = await service.get_presets(
            user_id=user_id,
            is_public=is_public,
            tags=tag_list,
            limit=limit,
            offset=offset
        )
        
        # Convert to response format
        preset_responses = []
        for preset in presets:
            preset_responses.append(FilterPresetResponse(
                preset_id=preset.preset_id,
                name=preset.name,
                description=preset.description,
                user_id=preset.user_id,
                filter_config=preset.filter_config,
                is_public=preset.is_public,
                tags=preset.tags,
                usage_count=preset.usage_count,
                created_at=preset.created_at.isoformat(),
                updated_at=preset.updated_at.isoformat()
            ))
        
        # Count total presets that match the filter criteria (without pagination)
        all_matching_presets = await service.get_presets(
            user_id=user_id,
            is_public=is_public,
            tags=tag_list,
            limit=10000,  # Use a large limit to get all
            offset=0
        )
        
        return FilterPresetListResponse(
            presets=preset_responses,
            total_count=len(all_matching_presets),
            filtered_by_user=(user_id is not None),
            filtered_by_public=is_public
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve filter presets: {str(e)}")


@router.get("/preferences/filter-presets/{preset_id}", response_model=FilterPresetResponse)
async def get_filter_preset_by_id(preset_id: UUID):
    """Get a specific filter preset by ID."""
    service = _get_filter_preset_service()
    try:
        preset = await service.get_preset_by_id(preset_id)
        if not preset:
            raise HTTPException(status_code=404, detail="Filter preset not found")
        
        # Increment usage count
        await service.increment_usage_count(preset_id)
        
        return FilterPresetResponse(
            preset_id=preset.preset_id,
            name=preset.name,
            description=preset.description,
            user_id=preset.user_id,
            filter_config=preset.filter_config,
            is_public=preset.is_public,
            tags=preset.tags,
            usage_count=preset.usage_count,
            created_at=preset.created_at.isoformat(),
            updated_at=preset.updated_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve filter preset: {str(e)}")


@router.put("/preferences/filter-presets/{preset_id}", response_model=FilterPresetResponse)
async def update_filter_preset(
    preset_id: UUID,
    request: FilterPresetRequest,
    user_id: Optional[UUID] = Query(None, description="User ID for authorization check")
):
    """Update an existing filter preset."""
    service = _get_filter_preset_service()
    try:
        updated_preset = await service.update_preset(
            preset_id=preset_id,
            name=request.name,
            description=request.description,
            filter_config=request.filter_config,
            is_public=request.is_public,
            tags=request.tags,
            user_id=user_id
        )
        
        if not updated_preset:
            raise HTTPException(status_code=404, detail="Filter preset not found")
        
        return FilterPresetResponse(
            preset_id=updated_preset.preset_id,
            name=updated_preset.name,
            description=updated_preset.description,
            user_id=updated_preset.user_id,
            filter_config=updated_preset.filter_config,
            is_public=updated_preset.is_public,
            tags=updated_preset.tags,
            usage_count=updated_preset.usage_count,
            created_at=updated_preset.created_at.isoformat(),
            updated_at=updated_preset.updated_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update filter preset: {str(e)}")


@router.delete("/preferences/filter-presets/{preset_id}")
async def delete_filter_preset(
    preset_id: UUID,
    user_id: Optional[UUID] = Query(None, description="User ID for authorization check")
):
    """Delete a filter preset."""
    service = _get_filter_preset_service()
    try:
        success = await service.delete_preset(preset_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Filter preset not found")
        
        return {"message": "Filter preset deleted successfully", "preset_id": str(preset_id)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete filter preset: {str(e)}")


@router.get("/preferences/filter-presets/preset-summaries")
async def get_filter_preset_summaries():
    """Get summary information for all available filter presets."""
    service = _get_filter_preset_service()
    try:
        # Get all presets (with a reasonable limit)
        all_presets = await service.get_presets(limit=100, offset=0)
        
        summaries = []
        for preset in all_presets:
            summary = FilterPresetSummary(
                key=str(preset.preset_id),
                name=preset.name,
                description=preset.description or f"Filter preset: {preset.name}",
                rationale=["Saved filter configuration", "Reusable for similar searches"]
            )
            summaries.append(summary)
        
        return {"presets": summaries, "total_count": len(summaries)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve filter preset summaries: {str(e)}")

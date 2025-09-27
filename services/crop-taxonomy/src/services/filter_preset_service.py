"""
Filter Preset Service

Service for managing filter presets for crop taxonomy filtering.
Provides functionality to save, retrieve, update, and delete filter presets.
"""

from __future__ import annotations

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4

from ..models.crop_filtering_models import FilterPreset, TaxonomyFilterCriteria

logger = logging.getLogger(__name__)


class FilterPresetService:
    """Service for managing filter presets."""
    
    def __init__(self):
        # In-memory storage for development; in production this would be a database
        self._presets: Dict[str, FilterPreset] = {}
        
    async def save_preset(
        self,
        name: str,
        filter_config: TaxonomyFilterCriteria,
        user_id: Optional[UUID] = None,
        description: Optional[str] = None,
        is_public: bool = False,
        tags: Optional[List[str]] = None
    ) -> FilterPreset:
        """
        Save a filter preset.
        
        Args:
            name: Display name for the preset
            filter_config: The filter configuration to save
            user_id: User who created the preset (None for system presets)
            description: Detailed description of the preset
            is_public: Whether the preset is publicly visible
            tags: Tags for categorizing the preset
        
        Returns:
            The saved FilterPreset object
        """
        preset_id = uuid4()
        
        preset = FilterPreset(
            preset_id=preset_id,
            user_id=user_id,
            name=name,
            description=description,
            filter_config=filter_config,
            is_public=is_public,
            tags=tags or [],
            usage_count=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self._presets[str(preset_id)] = preset
        logger.info(f"Saved filter preset: {preset_id} ({name})")
        
        return preset
    
    async def get_preset_by_id(self, preset_id: UUID) -> Optional[FilterPreset]:
        """
        Get a filter preset by its ID.
        
        Args:
            preset_id: The ID of the preset to retrieve
            
        Returns:
            The FilterPreset object if found, None otherwise
        """
        return self._presets.get(str(preset_id))
    
    async def get_presets(
        self,
        user_id: Optional[UUID] = None,
        is_public: Optional[bool] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[FilterPreset]:
        """
        Get filter presets with optional filtering.
        
        Args:
            user_id: Filter by user ID
            is_public: Filter by public/private status
            tags: Filter by tags (preset must have at least one of these tags)
            limit: Maximum number of presets to return
            offset: Offset for pagination
            
        Returns:
            List of FilterPreset objects
        """
        # Filter presets based on criteria
        filtered_presets = []
        
        for preset in self._presets.values():
            # Apply user filter if specified
            if user_id is not None and preset.user_id != user_id:
                continue
                
            # Apply public/private filter if specified
            if is_public is not None and preset.is_public != is_public:
                continue
                
            # Apply tag filter if specified
            if tags:
                if not any(tag in preset.tags for tag in tags if preset.tags):
                    continue
                    
            filtered_presets.append(preset)
        
        # Apply pagination
        paginated_presets = filtered_presets[offset:offset + limit]
        
        # Sort by creation date (newest first)
        paginated_presets.sort(key=lambda p: p.created_at, reverse=True)
        
        return paginated_presets
    
    async def update_preset(
        self,
        preset_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        filter_config: Optional[TaxonomyFilterCriteria] = None,
        is_public: Optional[bool] = None,
        tags: Optional[List[str]] = None,
        user_id: Optional[UUID] = None  # For authorization
    ) -> Optional[FilterPreset]:
        """
        Update an existing filter preset.
        
        Args:
            preset_id: ID of the preset to update
            name: New name for the preset
            description: New description for the preset
            filter_config: New filter configuration
            is_public: New public status
            tags: New tags
            user_id: User making the update (for authorization check)
            
        Returns:
            Updated FilterPreset object if successful, None if preset not found
        """
        preset = self._presets.get(str(preset_id))
        if not preset:
            return None
        
        # Authorization check - ensure user owns the preset if it's personal
        if preset.user_id and user_id and preset.user_id != user_id:
            # In a real implementation, this would raise an authorization exception
            return None
        
        # Update fields if provided
        if name is not None:
            preset.name = name
        if description is not None:
            preset.description = description
        if filter_config is not None:
            preset.filter_config = filter_config
        if is_public is not None:
            preset.is_public = is_public
        if tags is not None:
            preset.tags = tags
        
        preset.updated_at = datetime.utcnow()
        
        logger.info(f"Updated filter preset: {preset_id} ({preset.name})")
        
        return preset
    
    async def delete_preset(self, preset_id: UUID, user_id: Optional[UUID] = None) -> bool:
        """
        Delete a filter preset.
        
        Args:
            preset_id: ID of the preset to delete
            user_id: User making the deletion (for authorization check)
            
        Returns:
            True if deletion was successful, False if preset not found
        """
        preset = self._presets.get(str(preset_id))
        if not preset:
            return False
        
        # Authorization check - ensure user owns the preset if it's personal
        if preset.user_id and user_id and preset.user_id != user_id:
            # In a real implementation, this would raise an authorization exception
            return False
        
        del self._presets[str(preset_id)]
        logger.info(f"Deleted filter preset: {preset_id}")
        
        return True
    
    async def increment_usage_count(self, preset_id: UUID) -> bool:
        """
        Increment the usage count of a preset.
        
        Args:
            preset_id: ID of the preset to update
            
        Returns:
            True if successful, False if preset not found
        """
        preset = self._presets.get(str(preset_id))
        if not preset:
            return False
        
        preset.usage_count += 1
        return True


# Global instance
filter_preset_service = FilterPresetService()
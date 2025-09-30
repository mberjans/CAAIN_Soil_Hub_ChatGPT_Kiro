"""
Data Governance API Routes
CAAIN Soil Hub - Location Validation Service

API endpoints for comprehensive data governance and user control features.
Provides RESTful interfaces for location data sharing, retention management,
privacy preferences, and legal compliance.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel, Field

from ..services.location_data_governance_service import (
    LocationDataGovernanceService, UserDataControlPreferences,
    DataGovernanceLevel, SharingScope, RetentionPolicy
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/data-governance", tags=["data-governance"])


# Pydantic models for API requests/responses
class UserPreferencesRequest(BaseModel):
    """Request model for user data preferences."""
    data_governance_level: Optional[DataGovernanceLevel] = None
    sharing_scope: Optional[SharingScope] = None
    retention_policy: Optional[RetentionPolicy] = None
    allow_analytics: Optional[bool] = None
    allow_research_sharing: Optional[bool] = None
    allow_consultant_access: Optional[bool] = None
    location_precision_level: Optional[str] = None
    automatic_data_cleanup: Optional[bool] = None
    notification_preferences: Optional[Dict[str, bool]] = None


class UserPreferencesResponse(BaseModel):
    """Response model for user data preferences."""
    user_id: str
    data_governance_level: DataGovernanceLevel
    sharing_scope: SharingScope
    retention_policy: RetentionPolicy
    allow_analytics: bool
    allow_research_sharing: bool
    allow_consultant_access: bool
    location_precision_level: str
    automatic_data_cleanup: bool
    notification_preferences: Dict[str, bool]
    created_at: datetime
    updated_at: datetime


class DataSharingRequestModel(BaseModel):
    """Request model for data sharing."""
    farm_id: Optional[str] = None
    requested_by: str = Field(..., description="User or organization requesting access")
    purpose: str = Field(..., description="Purpose of data sharing")
    data_types: List[str] = Field(default=["farm_location", "field_boundaries"])
    security_level: str = Field(default="sensitive")


class DataSharingResponse(BaseModel):
    """Response model for data sharing requests."""
    request_id: str
    user_id: str
    farm_id: Optional[str]
    requested_by: str
    sharing_purpose: str
    data_types_requested: List[str]
    security_level: str
    requested_at: datetime
    expires_at: datetime
    status: str


class DataDeletionRequest(BaseModel):
    """Request model for data deletion."""
    data_types: Optional[List[str]] = None
    selective: bool = Field(default=False, description="Allow selective deletion")


class DataDeletionResponse(BaseModel):
    """Response model for data deletion."""
    user_id: str
    deletion_timestamp: str
    data_types_deleted: List[str]
    records_deleted: int
    errors: List[str]


class DataExportRequest(BaseModel):
    """Request model for data export."""
    export_format: str = Field(default="json", description="Export format (json, csv, xml)")
    include_metadata: bool = Field(default=True, description="Include metadata in export")


class DataExportResponse(BaseModel):
    """Response model for data export."""
    user_id: str
    export_timestamp: str
    export_format: str
    data: Dict[str, Any]
    user_preferences: Optional[Dict[str, Any]] = None


class GovernanceDashboardResponse(BaseModel):
    """Response model for governance dashboard."""
    user_id: str
    preferences: Optional[Dict[str, Any]]
    sharing_permissions: List[Dict[str, Any]]
    retention_records: List[Dict[str, Any]]
    recent_exports: List[Dict[str, Any]]
    statistics: Dict[str, Any]
    last_updated: str


# Dependency injection
async def get_governance_service() -> LocationDataGovernanceService:
    """Get data governance service instance."""
    # In production, this would get a database session
    from sqlalchemy.orm import Session
    db_session = Session()  # This would be properly injected
    return LocationDataGovernanceService(db_session)


@router.get("/preferences/{user_id}", response_model=UserPreferencesResponse)
async def get_user_preferences(
    user_id: str,
    service: LocationDataGovernanceService = Depends(get_governance_service)
):
    """
    Get user data control preferences.
    
    Returns comprehensive user preferences for data governance including:
    - Data sharing scope and permissions
    - Retention policies
    - Privacy settings
    - Notification preferences
    """
    try:
        preferences = await service.get_user_data_preferences(user_id)
        if not preferences:
            raise HTTPException(status_code=404, detail="User preferences not found")
        
        return UserPreferencesResponse(
            user_id=preferences.user_id,
            data_governance_level=preferences.data_governance_level,
            sharing_scope=preferences.sharing_scope,
            retention_policy=preferences.retention_policy,
            allow_analytics=preferences.allow_analytics,
            allow_research_sharing=preferences.allow_research_sharing,
            allow_consultant_access=preferences.allow_consultant_access,
            location_precision_level=preferences.location_precision_level,
            automatic_data_cleanup=preferences.automatic_data_cleanup,
            notification_preferences=preferences.notification_preferences,
            created_at=preferences.created_at,
            updated_at=preferences.updated_at
        )
        
    except Exception as e:
        logger.error(f"Error getting user preferences: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user preferences: {str(e)}")


@router.put("/preferences/{user_id}", response_model=UserPreferencesResponse)
async def update_user_preferences(
    user_id: str,
    preferences_update: UserPreferencesRequest,
    service: LocationDataGovernanceService = Depends(get_governance_service)
):
    """
    Update user data control preferences.
    
    Allows users to modify their data governance preferences including:
    - Data sharing permissions
    - Retention policies
    - Privacy settings
    - Notification preferences
    """
    try:
        # Convert Pydantic model to dict, excluding None values
        updates = {k: v for k, v in preferences_update.dict().items() if v is not None}
        
        updated_preferences = await service.update_user_data_preferences(user_id, updates)
        
        return UserPreferencesResponse(
            user_id=updated_preferences.user_id,
            data_governance_level=updated_preferences.data_governance_level,
            sharing_scope=updated_preferences.sharing_scope,
            retention_policy=updated_preferences.retention_policy,
            allow_analytics=updated_preferences.allow_analytics,
            allow_research_sharing=updated_preferences.allow_research_sharing,
            allow_consultant_access=updated_preferences.allow_consultant_access,
            location_precision_level=updated_preferences.location_precision_level,
            automatic_data_cleanup=updated_preferences.automatic_data_cleanup,
            notification_preferences=updated_preferences.notification_preferences,
            created_at=updated_preferences.created_at,
            updated_at=updated_preferences.updated_at
        )
        
    except Exception as e:
        logger.error(f"Error updating user preferences: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update user preferences: {str(e)}")


@router.post("/sharing/{user_id}", response_model=DataSharingResponse)
async def create_sharing_request(
    user_id: str,
    sharing_request: DataSharingRequestModel,
    service: LocationDataGovernanceService = Depends(get_governance_service)
):
    """
    Create a data sharing request.
    
    Allows users to request sharing of their location data with:
    - Agricultural consultants
    - Research institutions
    - Other farmers
    - Public agricultural databases
    """
    try:
        sharing_req = await service.manage_location_sharing(
            user_id=user_id,
            farm_id=sharing_request.farm_id,
            sharing_request=sharing_request.dict()
        )
        
        return DataSharingResponse(
            request_id=sharing_req.request_id,
            user_id=sharing_req.user_id,
            farm_id=sharing_req.farm_id,
            requested_by=sharing_req.requested_by,
            sharing_purpose=sharing_req.sharing_purpose,
            data_types_requested=sharing_req.data_types_requested,
            security_level=sharing_req.security_level,
            requested_at=sharing_req.requested_at,
            expires_at=sharing_req.expires_at,
            status=sharing_req.status
        )
        
    except Exception as e:
        logger.error(f"Error creating sharing request: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create sharing request: {str(e)}")


@router.post("/sharing/{user_id}/approve/{request_id}")
async def approve_sharing_request(
    user_id: str,
    request_id: str,
    approval_details: Dict[str, Any] = Body(...),
    service: LocationDataGovernanceService = Depends(get_governance_service)
):
    """
    Approve a data sharing request.
    
    Allows users to approve pending sharing requests with additional details.
    """
    try:
        success = await service.approve_sharing_request(request_id, user_id, approval_details)
        
        if not success:
            raise HTTPException(status_code=404, detail="Sharing request not found or not authorized")
        
        return {"success": True, "message": "Sharing request approved successfully"}
        
    except Exception as e:
        logger.error(f"Error approving sharing request: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to approve sharing request: {str(e)}")


@router.delete("/sharing/{user_id}/revoke/{permission_id}")
async def revoke_data_sharing(
    user_id: str,
    permission_id: str,
    reason: str = Query(..., description="Reason for revoking sharing permission"),
    service: LocationDataGovernanceService = Depends(get_governance_service)
):
    """
    Revoke data sharing permission.
    
    Allows users to revoke previously granted sharing permissions.
    """
    try:
        success = await service.revoke_data_sharing(user_id, permission_id, reason)
        
        if not success:
            raise HTTPException(status_code=404, detail="Sharing permission not found or not authorized")
        
        return {"success": True, "message": "Data sharing permission revoked successfully"}
        
    except Exception as e:
        logger.error(f"Error revoking data sharing: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to revoke data sharing: {str(e)}")


@router.post("/retention/{user_id}")
async def manage_data_retention(
    user_id: str,
    data_type: str = Query(..., description="Type of data to manage retention for"),
    data_id: str = Query(..., description="Unique identifier for the data"),
    retention_policy: Optional[RetentionPolicy] = Query(None, description="Custom retention policy"),
    service: LocationDataGovernanceService = Depends(get_governance_service)
):
    """
    Manage data retention for location information.
    
    Allows users to set custom retention policies for specific data types.
    """
    try:
        retention_record = await service.manage_data_retention(
            user_id=user_id,
            data_type=data_type,
            data_id=data_id,
            retention_policy=retention_policy
        )
        
        return {
            "record_id": retention_record.record_id,
            "user_id": retention_record.user_id,
            "data_type": retention_record.data_type,
            "data_id": retention_record.data_id,
            "retention_policy": retention_record.retention_policy,
            "expires_at": retention_record.expires_at.isoformat(),
            "auto_delete_enabled": retention_record.auto_delete_enabled
        }
        
    except Exception as e:
        logger.error(f"Error managing data retention: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to manage data retention: {str(e)}")


@router.delete("/data/{user_id}", response_model=DataDeletionResponse)
async def delete_user_location_data(
    user_id: str,
    deletion_request: DataDeletionRequest,
    service: LocationDataGovernanceService = Depends(get_governance_service)
):
    """
    Delete user location data.
    
    Allows users to delete their location data based on preferences:
    - Selective deletion by data type
    - Complete data deletion
    - GDPR compliance deletion
    """
    try:
        deletion_summary = await service.delete_user_location_data(
            user_id=user_id,
            data_types=deletion_request.data_types,
            selective=deletion_request.selective
        )
        
        return DataDeletionResponse(
            user_id=deletion_summary['user_id'],
            deletion_timestamp=deletion_summary['deletion_timestamp'],
            data_types_deleted=deletion_summary['data_types_deleted'],
            records_deleted=deletion_summary['records_deleted'],
            errors=deletion_summary['errors']
        )
        
    except Exception as e:
        logger.error(f"Error deleting user location data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete user location data: {str(e)}")


@router.post("/export/{user_id}", response_model=DataExportResponse)
async def export_user_location_data(
    user_id: str,
    export_request: DataExportRequest,
    service: LocationDataGovernanceService = Depends(get_governance_service)
):
    """
    Export user location data for portability.
    
    Provides GDPR-compliant data export functionality:
    - Multiple export formats (JSON, CSV, XML)
    - Complete data portability
    - Metadata inclusion options
    """
    try:
        export_data = await service.export_user_location_data(
            user_id=user_id,
            export_format=export_request.export_format,
            include_metadata=export_request.include_metadata
        )
        
        return DataExportResponse(
            user_id=export_data['user_id'],
            export_timestamp=export_data['export_timestamp'],
            export_format=export_data['export_format'],
            data=export_data['data'],
            user_preferences=export_data.get('user_preferences')
        )
        
    except Exception as e:
        logger.error(f"Error exporting user location data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export user location data: {str(e)}")


@router.get("/dashboard/{user_id}", response_model=GovernanceDashboardResponse)
async def get_data_governance_dashboard(
    user_id: str,
    service: LocationDataGovernanceService = Depends(get_governance_service)
):
    """
    Get comprehensive data governance dashboard.
    
    Provides a complete overview of user's data governance status:
    - Current preferences and settings
    - Active sharing permissions
    - Data retention records
    - Recent exports
    - Governance statistics
    """
    try:
        dashboard = await service.get_data_governance_dashboard(user_id)
        
        return GovernanceDashboardResponse(
            user_id=dashboard['user_id'],
            preferences=dashboard['preferences'],
            sharing_permissions=dashboard['sharing_permissions'],
            retention_records=dashboard['retention_records'],
            recent_exports=dashboard['recent_exports'],
            statistics=dashboard['statistics'],
            last_updated=dashboard['last_updated']
        )
        
    except Exception as e:
        logger.error(f"Error getting governance dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get governance dashboard: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for data governance service."""
    return {
        "status": "healthy",
        "service": "data-governance",
        "timestamp": datetime.utcnow().isoformat(),
        "features": [
            "user_preferences",
            "data_sharing",
            "retention_management",
            "data_deletion",
            "data_export",
            "governance_dashboard"
        ]
    }

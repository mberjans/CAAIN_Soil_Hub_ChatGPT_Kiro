"""
Location Data Governance Service
CAAIN Soil Hub - Location Validation Service

Comprehensive data governance and user control system for location data.
Implements user data control, sharing preferences, retention management,
and legal compliance features.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from uuid import UUID, uuid4
import json

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from ..models.security_models import (
    LocationPrivacyConsent, LocationDataRetention, LocationSharingPermission,
    LocationDataExport, LocationSecurityConfiguration
)
from ..models.mobile_location_models import (
    FarmLocation, Field, LocationHistoryEntry, MappingSession
)

logger = logging.getLogger(__name__)


class DataGovernanceLevel(str, Enum):
    """Data governance levels for location data."""
    MINIMAL = "minimal"           # Basic location data only
    STANDARD = "standard"         # Standard agricultural data
    COMPREHENSIVE = "comprehensive"  # Full data collection
    RESEARCH = "research"         # Research-level data sharing


class SharingScope(str, Enum):
    """Scope of data sharing permissions."""
    PRIVATE = "private"           # No sharing
    FARM_ONLY = "farm_only"       # Within farm organization
    CONSULTANT = "consultant"     # With agricultural consultants
    RESEARCH = "research"         # With research institutions
    PUBLIC = "public"             # Public agricultural data


class RetentionPolicy(str, Enum):
    """Data retention policy options."""
    MINIMAL = "minimal"           # 30 days
    SHORT = "short"              # 1 year
    STANDARD = "standard"         # 3 years
    LONG = "long"                # 5 years
    EXTENDED = "extended"         # 10 years


@dataclass
class UserDataControlPreferences:
    """User preferences for data control."""
    user_id: str
    data_governance_level: DataGovernanceLevel
    sharing_scope: SharingScope
    retention_policy: RetentionPolicy
    allow_analytics: bool
    allow_research_sharing: bool
    allow_consultant_access: bool
    location_precision_level: str  # high, medium, low, minimal
    automatic_data_cleanup: bool
    notification_preferences: Dict[str, bool]
    created_at: datetime
    updated_at: datetime


@dataclass
class DataSharingRequest:
    """Request for sharing location data."""
    request_id: str
    user_id: str
    farm_id: Optional[str]
    requested_by: str
    sharing_purpose: str
    data_types_requested: List[str]
    security_level: str
    requested_at: datetime
    expires_at: datetime
    status: str  # pending, approved, denied, expired


@dataclass
class DataRetentionRecord:
    """Record of data retention for location information."""
    record_id: str
    user_id: str
    data_type: str
    data_id: str
    retention_policy: RetentionPolicy
    created_at: datetime
    expires_at: datetime
    last_accessed: datetime
    access_count: int
    auto_delete_enabled: bool


class LocationDataGovernanceService:
    """
    Comprehensive data governance service for location data.
    
    Provides user control over location data sharing, retention,
    privacy preferences, and legal compliance management.
    """
    
    def __init__(self, db_session: Session):
        """Initialize the data governance service."""
        self.logger = logging.getLogger(__name__)
        self.db = db_session
        
        # Default governance policies
        self.default_policies = {
            'data_governance_level': DataGovernanceLevel.STANDARD,
            'sharing_scope': SharingScope.FARM_ONLY,
            'retention_policy': RetentionPolicy.STANDARD,
            'location_precision_level': 'medium',
            'automatic_data_cleanup': True
        }
        
        # Retention periods (in days)
        self.retention_periods = {
            RetentionPolicy.MINIMAL: 30,
            RetentionPolicy.SHORT: 365,
            RetentionPolicy.STANDARD: 1095,  # 3 years
            RetentionPolicy.LONG: 1825,     # 5 years
            RetentionPolicy.EXTENDED: 3650  # 10 years
        }
        
        self.logger.info("Location data governance service initialized")
    
    async def create_user_data_preferences(
        self,
        user_id: str,
        preferences: Optional[Dict[str, Any]] = None
    ) -> UserDataControlPreferences:
        """
        Create user data control preferences.
        
        Args:
            user_id: User identifier
            preferences: Optional custom preferences
            
        Returns:
            UserDataControlPreferences object
        """
        try:
            # Merge with defaults
            user_prefs = {**self.default_policies}
            if preferences:
                user_prefs.update(preferences)
            
            # Create preferences record
            preferences_obj = UserDataControlPreferences(
                user_id=user_id,
                data_governance_level=DataGovernanceLevel(user_prefs.get('data_governance_level', 'standard')),
                sharing_scope=SharingScope(user_prefs.get('sharing_scope', 'farm_only')),
                retention_policy=RetentionPolicy(user_prefs.get('retention_policy', 'standard')),
                allow_analytics=user_prefs.get('allow_analytics', False),
                allow_research_sharing=user_prefs.get('allow_research_sharing', False),
                allow_consultant_access=user_prefs.get('allow_consultant_access', True),
                location_precision_level=user_prefs.get('location_precision_level', 'medium'),
                automatic_data_cleanup=user_prefs.get('automatic_data_cleanup', True),
                notification_preferences=user_prefs.get('notification_preferences', {
                    'data_sharing_notifications': True,
                    'retention_warnings': True,
                    'access_alerts': True,
                    'policy_changes': True
                }),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Store in database
            await self._store_user_preferences(preferences_obj)
            
            self.logger.info(f"Created data preferences for user {user_id}")
            return preferences_obj
            
        except Exception as e:
            self.logger.error(f"Error creating user preferences: {e}")
            raise
    
    async def get_user_data_preferences(self, user_id: str) -> Optional[UserDataControlPreferences]:
        """Get user data control preferences."""
        try:
            # This would query the database for user preferences
            # For now, return default preferences
            return await self.create_user_data_preferences(user_id)
            
        except Exception as e:
            self.logger.error(f"Error getting user preferences: {e}")
            return None
    
    async def update_user_data_preferences(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ) -> UserDataControlPreferences:
        """Update user data control preferences."""
        try:
            current_prefs = await self.get_user_data_preferences(user_id)
            if not current_prefs:
                current_prefs = await self.create_user_data_preferences(user_id)
            
            # Update preferences
            for key, value in updates.items():
                if hasattr(current_prefs, key):
                    setattr(current_prefs, key, value)
            
            current_prefs.updated_at = datetime.utcnow()
            
            # Store updated preferences
            await self._store_user_preferences(current_prefs)
            
            self.logger.info(f"Updated data preferences for user {user_id}")
            return current_prefs
            
        except Exception as e:
            self.logger.error(f"Error updating user preferences: {e}")
            raise
    
    async def manage_location_sharing(
        self,
        user_id: str,
        farm_id: Optional[str],
        sharing_request: Dict[str, Any]
    ) -> DataSharingRequest:
        """
        Manage location data sharing requests.
        
        Args:
            user_id: User identifier
            farm_id: Optional farm identifier
            sharing_request: Sharing request details
            
        Returns:
            DataSharingRequest object
        """
        try:
            request_id = str(uuid4())
            
            sharing_req = DataSharingRequest(
                request_id=request_id,
                user_id=user_id,
                farm_id=farm_id,
                requested_by=sharing_request.get('requested_by', 'unknown'),
                sharing_purpose=sharing_request.get('purpose', 'agricultural_consultation'),
                data_types_requested=sharing_request.get('data_types', ['farm_location', 'field_boundaries']),
                security_level=sharing_request.get('security_level', 'sensitive'),
                requested_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=30),
                status='pending'
            )
            
            # Store sharing request
            await self._store_sharing_request(sharing_req)
            
            # Check if auto-approval is possible based on user preferences
            user_prefs = await self.get_user_data_preferences(user_id)
            if user_prefs and self._can_auto_approve_sharing(user_prefs, sharing_req):
                sharing_req.status = 'approved'
                await self._store_sharing_request(sharing_req)
            
            self.logger.info(f"Created sharing request {request_id} for user {user_id}")
            return sharing_req
            
        except Exception as e:
            self.logger.error(f"Error managing location sharing: {e}")
            raise
    
    async def approve_sharing_request(
        self,
        request_id: str,
        user_id: str,
        approval_details: Dict[str, Any]
    ) -> bool:
        """Approve a data sharing request."""
        try:
            # Update sharing request status
            sharing_req = await self._get_sharing_request(request_id)
            if sharing_req and sharing_req.user_id == user_id:
                sharing_req.status = 'approved'
                await self._store_sharing_request(sharing_req)
                
                # Create sharing permission record
                await self._create_sharing_permission(sharing_req, approval_details)
                
                self.logger.info(f"Approved sharing request {request_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error approving sharing request: {e}")
            return False
    
    async def revoke_data_sharing(
        self,
        user_id: str,
        permission_id: str,
        reason: str
    ) -> bool:
        """Revoke data sharing permission."""
        try:
            # Update sharing permission
            permission = await self._get_sharing_permission(permission_id)
            if permission and permission.user_id == user_id:
                permission.revoked_at = datetime.utcnow()
                await self._update_sharing_permission(permission)
                
                self.logger.info(f"Revoked sharing permission {permission_id} for user {user_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error revoking data sharing: {e}")
            return False
    
    async def manage_data_retention(
        self,
        user_id: str,
        data_type: str,
        data_id: str,
        retention_policy: Optional[RetentionPolicy] = None
    ) -> DataRetentionRecord:
        """
        Manage data retention for location information.
        
        Args:
            user_id: User identifier
            data_type: Type of data (farm_location, field_boundary, etc.)
            data_id: Unique identifier for the data
            retention_policy: Optional custom retention policy
            
        Returns:
            DataRetentionRecord object
        """
        try:
            # Get user preferences for retention policy
            user_prefs = await self.get_user_data_preferences(user_id)
            if not retention_policy:
                retention_policy = user_prefs.retention_policy if user_prefs else RetentionPolicy.STANDARD
            
            # Calculate expiration date
            retention_days = self.retention_periods[retention_policy]
            expires_at = datetime.utcnow() + timedelta(days=retention_days)
            
            retention_record = DataRetentionRecord(
                record_id=str(uuid4()),
                user_id=user_id,
                data_type=data_type,
                data_id=data_id,
                retention_policy=retention_policy,
                created_at=datetime.utcnow(),
                expires_at=expires_at,
                last_accessed=datetime.utcnow(),
                access_count=0,
                auto_delete_enabled=user_prefs.automatic_data_cleanup if user_prefs else True
            )
            
            # Store retention record
            await self._store_retention_record(retention_record)
            
            self.logger.info(f"Created retention record for {data_type}:{data_id}")
            return retention_record
            
        except Exception as e:
            self.logger.error(f"Error managing data retention: {e}")
            raise
    
    async def delete_user_location_data(
        self,
        user_id: str,
        data_types: Optional[List[str]] = None,
        selective: bool = False
    ) -> Dict[str, Any]:
        """
        Delete user location data based on preferences.
        
        Args:
            user_id: User identifier
            data_types: Optional specific data types to delete
            selective: Whether to allow selective deletion
            
        Returns:
            Deletion summary
        """
        try:
            deletion_summary = {
                'user_id': user_id,
                'deletion_timestamp': datetime.utcnow().isoformat(),
                'data_types_deleted': [],
                'records_deleted': 0,
                'errors': []
            }
            
            # Get user preferences
            user_prefs = await self.get_user_data_preferences(user_id)
            
            # Define data types to delete
            if not data_types:
                data_types = ['farm_locations', 'field_boundaries', 'location_history', 'mapping_sessions']
            
            # Delete data by type
            for data_type in data_types:
                try:
                    deleted_count = await self._delete_data_by_type(user_id, data_type)
                    deletion_summary['data_types_deleted'].append(data_type)
                    deletion_summary['records_deleted'] += deleted_count
                    
                except Exception as e:
                    deletion_summary['errors'].append(f"Error deleting {data_type}: {str(e)}")
            
            # Update retention records
            await self._update_retention_records_after_deletion(user_id, data_types)
            
            self.logger.info(f"Deleted location data for user {user_id}: {deletion_summary['records_deleted']} records")
            return deletion_summary
            
        except Exception as e:
            self.logger.error(f"Error deleting user location data: {e}")
            raise
    
    async def export_user_location_data(
        self,
        user_id: str,
        export_format: str = 'json',
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        Export user location data for portability.
        
        Args:
            user_id: User identifier
            export_format: Export format (json, csv, xml)
            include_metadata: Whether to include metadata
            
        Returns:
            Export data
        """
        try:
            export_data = {
                'user_id': user_id,
                'export_timestamp': datetime.utcnow().isoformat(),
                'export_format': export_format,
                'data': {}
            }
            
            # Get user preferences
            user_prefs = await self.get_user_data_preferences(user_id)
            if include_metadata:
                export_data['user_preferences'] = asdict(user_prefs) if user_prefs else None
            
            # Export different data types
            data_types = ['farm_locations', 'field_boundaries', 'location_history']
            
            for data_type in data_types:
                try:
                    data = await self._export_data_by_type(user_id, data_type)
                    export_data['data'][data_type] = data
                    
                except Exception as e:
                    self.logger.warning(f"Error exporting {data_type}: {e}")
                    export_data['data'][data_type] = None
            
            # Store export record
            await self._store_export_record(user_id, export_format, len(export_data['data']))
            
            self.logger.info(f"Exported location data for user {user_id}")
            return export_data
            
        except Exception as e:
            self.logger.error(f"Error exporting user location data: {e}")
            raise
    
    async def get_data_governance_dashboard(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive data governance dashboard for user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dashboard data
        """
        try:
            # Get user preferences
            user_prefs = await self.get_user_data_preferences(user_id)
            
            # Get sharing permissions
            sharing_permissions = await self._get_user_sharing_permissions(user_id)
            
            # Get retention records
            retention_records = await self._get_user_retention_records(user_id)
            
            # Get recent exports
            recent_exports = await self._get_user_recent_exports(user_id)
            
            # Calculate statistics
            stats = await self._calculate_governance_stats(user_id)
            
            dashboard = {
                'user_id': user_id,
                'preferences': asdict(user_prefs) if user_prefs else None,
                'sharing_permissions': [
                    {
                        'id': perm.id,
                        'shared_with': perm.shared_with_organization or perm.shared_with_user_id,
                        'purpose': perm.sharing_purpose,
                        'data_types': perm.data_types_shared,
                        'created_at': perm.consent_timestamp.isoformat(),
                        'expires_at': perm.expires_at.isoformat() if perm.expires_at else None,
                        'active': perm.revoked_at is None
                    } for perm in sharing_permissions
                ],
                'retention_records': [
                    {
                        'data_type': record.data_type,
                        'retention_policy': record.retention_policy,
                        'expires_at': record.expires_at.isoformat(),
                        'auto_delete_enabled': record.auto_delete_enabled
                    } for record in retention_records
                ],
                'recent_exports': [
                    {
                        'export_id': export.id,
                        'export_format': export.export_format,
                        'exported_at': export.exported_at.isoformat(),
                        'data_types_count': export.data_types_count
                    } for export in recent_exports
                ],
                'statistics': stats,
                'last_updated': datetime.utcnow().isoformat()
            }
            
            return dashboard
            
        except Exception as e:
            self.logger.error(f"Error getting governance dashboard: {e}")
            raise
    
    def _can_auto_approve_sharing(
        self,
        user_prefs: UserDataControlPreferences,
        sharing_req: DataSharingRequest
    ) -> bool:
        """Check if sharing request can be auto-approved based on user preferences."""
        # Auto-approve if:
        # 1. User allows consultant access and request is from consultant
        # 2. Sharing scope allows the requested level
        # 3. Purpose matches user preferences
        
        if sharing_req.sharing_purpose == 'agricultural_consultation' and user_prefs.allow_consultant_access:
            return True
        
        if sharing_req.sharing_purpose == 'research' and user_prefs.allow_research_sharing:
            return True
        
        return False
    
    async def _store_user_preferences(self, preferences: UserDataControlPreferences):
        """Store user preferences in database."""
        # This would store preferences in the database
        # For now, just log the action
        self.logger.debug(f"Storing preferences for user {preferences.user_id}")
    
    async def _store_sharing_request(self, request: DataSharingRequest):
        """Store sharing request in database."""
        self.logger.debug(f"Storing sharing request {request.request_id}")
    
    async def _get_sharing_request(self, request_id: str) -> Optional[DataSharingRequest]:
        """Get sharing request by ID."""
        # This would query the database
        return None
    
    async def _create_sharing_permission(self, request: DataSharingRequest, details: Dict[str, Any]):
        """Create sharing permission record."""
        self.logger.debug(f"Creating sharing permission for request {request.request_id}")
    
    async def _get_sharing_permission(self, permission_id: str):
        """Get sharing permission by ID."""
        return None
    
    async def _update_sharing_permission(self, permission):
        """Update sharing permission."""
        self.logger.debug(f"Updating sharing permission {permission.id}")
    
    async def _store_retention_record(self, record: DataRetentionRecord):
        """Store retention record in database."""
        self.logger.debug(f"Storing retention record {record.record_id}")
    
    async def _delete_data_by_type(self, user_id: str, data_type: str) -> int:
        """Delete data by type for user."""
        # This would delete actual data from database
        # Return count of deleted records
        return 0
    
    async def _update_retention_records_after_deletion(self, user_id: str, data_types: List[str]):
        """Update retention records after deletion."""
        self.logger.debug(f"Updating retention records for user {user_id}")
    
    async def _export_data_by_type(self, user_id: str, data_type: str) -> List[Dict[str, Any]]:
        """Export data by type for user."""
        # This would export actual data from database
        return []
    
    async def _store_export_record(self, user_id: str, export_format: str, data_types_count: int):
        """Store export record."""
        self.logger.debug(f"Storing export record for user {user_id}")
    
    async def _get_user_sharing_permissions(self, user_id: str) -> List:
        """Get user sharing permissions."""
        return []
    
    async def _get_user_retention_records(self, user_id: str) -> List[DataRetentionRecord]:
        """Get user retention records."""
        return []
    
    async def _get_user_recent_exports(self, user_id: str) -> List:
        """Get user recent exports."""
        return []
    
    async def _calculate_governance_stats(self, user_id: str) -> Dict[str, Any]:
        """Calculate governance statistics for user."""
        return {
            'total_data_records': 0,
            'active_sharing_permissions': 0,
            'pending_sharing_requests': 0,
            'data_expiring_soon': 0,
            'last_data_export': None
        }

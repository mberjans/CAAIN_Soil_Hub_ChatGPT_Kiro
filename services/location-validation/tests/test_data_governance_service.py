"""
Test Suite for Location Data Governance Service
CAAIN Soil Hub - Location Validation Service

Comprehensive tests for data governance and user control functionality.
Tests user preferences, data sharing, retention management, and legal compliance.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

from src.services.location_data_governance_service import (
    LocationDataGovernanceService, UserDataControlPreferences,
    DataGovernanceLevel, SharingScope, RetentionPolicy,
    DataSharingRequest, DataRetentionRecord
)


class TestLocationDataGovernanceService:
    """Test suite for LocationDataGovernanceService."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return Mock()
    
    @pytest.fixture
    def governance_service(self, mock_db_session):
        """Governance service instance."""
        return LocationDataGovernanceService(mock_db_session)
    
    @pytest.fixture
    def sample_user_id(self):
        """Sample user ID for testing."""
        return "test-user-123"
    
    @pytest.fixture
    def sample_preferences(self):
        """Sample user preferences."""
        return {
            'data_governance_level': 'standard',
            'sharing_scope': 'farm_only',
            'retention_policy': 'standard',
            'allow_analytics': False,
            'allow_research_sharing': True,
            'allow_consultant_access': True,
            'location_precision_level': 'medium',
            'automatic_data_cleanup': True,
            'notification_preferences': {
                'data_sharing_notifications': True,
                'retention_warnings': True,
                'access_alerts': True,
                'policy_changes': True
            }
        }
    
    @pytest.mark.asyncio
    async def test_create_user_data_preferences(self, governance_service, sample_user_id, sample_preferences):
        """Test creating user data preferences."""
        preferences = await governance_service.create_user_data_preferences(
            sample_user_id, sample_preferences
        )
        
        assert preferences.user_id == sample_user_id
        assert preferences.data_governance_level == DataGovernanceLevel.STANDARD
        assert preferences.sharing_scope == SharingScope.FARM_ONLY
        assert preferences.retention_policy == RetentionPolicy.STANDARD
        assert preferences.allow_analytics is False
        assert preferences.allow_research_sharing is True
        assert preferences.allow_consultant_access is True
        assert preferences.location_precision_level == 'medium'
        assert preferences.automatic_data_cleanup is True
        assert isinstance(preferences.created_at, datetime)
        assert isinstance(preferences.updated_at, datetime)
    
    @pytest.mark.asyncio
    async def test_get_user_data_preferences(self, governance_service, sample_user_id):
        """Test getting user data preferences."""
        preferences = await governance_service.get_user_data_preferences(sample_user_id)
        
        assert preferences is not None
        assert preferences.user_id == sample_user_id
        assert isinstance(preferences.data_governance_level, DataGovernanceLevel)
        assert isinstance(preferences.sharing_scope, SharingScope)
        assert isinstance(preferences.retention_policy, RetentionPolicy)
    
    @pytest.mark.asyncio
    async def test_update_user_data_preferences(self, governance_service, sample_user_id):
        """Test updating user data preferences."""
        updates = {
            'allow_analytics': True,
            'location_precision_level': 'high',
            'automatic_data_cleanup': False
        }
        
        updated_preferences = await governance_service.update_user_data_preferences(
            sample_user_id, updates
        )
        
        assert updated_preferences.user_id == sample_user_id
        assert updated_preferences.allow_analytics is True
        assert updated_preferences.location_precision_level == 'high'
        assert updated_preferences.automatic_data_cleanup is False
        assert updated_preferences.updated_at > updated_preferences.created_at
    
    @pytest.mark.asyncio
    async def test_manage_location_sharing(self, governance_service, sample_user_id):
        """Test managing location data sharing requests."""
        sharing_request = {
            'requested_by': 'agricultural-consultant-456',
            'purpose': 'agricultural_consultation',
            'data_types': ['farm_location', 'field_boundaries'],
            'security_level': 'sensitive'
        }
        
        sharing_req = await governance_service.manage_location_sharing(
            sample_user_id, 'farm-789', sharing_request
        )
        
        assert sharing_req.user_id == sample_user_id
        assert sharing_req.farm_id == 'farm-789'
        assert sharing_req.requested_by == 'agricultural-consultant-456'
        assert sharing_req.sharing_purpose == 'agricultural_consultation'
        assert sharing_req.data_types_requested == ['farm_location', 'field_boundaries']
        assert sharing_req.security_level == 'sensitive'
        assert sharing_req.status in ['pending', 'approved']
        assert isinstance(sharing_req.requested_at, datetime)
        assert isinstance(sharing_req.expires_at, datetime)
    
    @pytest.mark.asyncio
    async def test_auto_approve_sharing_consultant(self, governance_service, sample_user_id):
        """Test auto-approval of consultant sharing requests."""
        # Create preferences that allow consultant access
        await governance_service.create_user_data_preferences(sample_user_id, {
            'allow_consultant_access': True
        })
        
        sharing_request = {
            'requested_by': 'consultant-123',
            'purpose': 'agricultural_consultation',
            'data_types': ['farm_location'],
            'security_level': 'sensitive'
        }
        
        sharing_req = await governance_service.manage_location_sharing(
            sample_user_id, None, sharing_request
        )
        
        # Should be auto-approved due to consultant access permission
        assert sharing_req.status == 'approved'
    
    @pytest.mark.asyncio
    async def test_auto_approve_sharing_research(self, governance_service, sample_user_id):
        """Test auto-approval of research sharing requests."""
        # Create preferences that allow research sharing
        await governance_service.create_user_data_preferences(sample_user_id, {
            'allow_research_sharing': True
        })
        
        sharing_request = {
            'requested_by': 'university-research',
            'purpose': 'research',
            'data_types': ['farm_location', 'field_boundaries'],
            'security_level': 'sensitive'
        }
        
        sharing_req = await governance_service.manage_location_sharing(
            sample_user_id, None, sharing_request
        )
        
        # Should be auto-approved due to research sharing permission
        assert sharing_req.status == 'approved'
    
    @pytest.mark.asyncio
    async def test_manage_data_retention(self, governance_service, sample_user_id):
        """Test managing data retention."""
        retention_record = await governance_service.manage_data_retention(
            sample_user_id, 'farm_location', 'location-123', RetentionPolicy.LONG
        )
        
        assert retention_record.user_id == sample_user_id
        assert retention_record.data_type == 'farm_location'
        assert retention_record.data_id == 'location-123'
        assert retention_record.retention_policy == RetentionPolicy.LONG
        assert isinstance(retention_record.created_at, datetime)
        assert isinstance(retention_record.expires_at, datetime)
        assert retention_record.access_count == 0
        assert retention_record.auto_delete_enabled is True
    
    @pytest.mark.asyncio
    async def test_retention_policy_periods(self, governance_service):
        """Test retention policy periods."""
        retention_periods = governance_service.retention_periods
        
        assert retention_periods[RetentionPolicy.MINIMAL] == 30
        assert retention_periods[RetentionPolicy.SHORT] == 365
        assert retention_periods[RetentionPolicy.STANDARD] == 1095  # 3 years
        assert retention_periods[RetentionPolicy.LONG] == 1825      # 5 years
        assert retention_periods[RetentionPolicy.EXTENDED] == 3650  # 10 years
    
    @pytest.mark.asyncio
    async def test_delete_user_location_data(self, governance_service, sample_user_id):
        """Test deleting user location data."""
        deletion_summary = await governance_service.delete_user_location_data(
            sample_user_id, ['farm_locations', 'field_boundaries'], selective=True
        )
        
        assert deletion_summary['user_id'] == sample_user_id
        assert 'deletion_timestamp' in deletion_summary
        assert 'farm_locations' in deletion_summary['data_types_deleted']
        assert 'field_boundaries' in deletion_summary['data_types_deleted']
        assert deletion_summary['records_deleted'] >= 0
        assert isinstance(deletion_summary['errors'], list)
    
    @pytest.mark.asyncio
    async def test_export_user_location_data(self, governance_service, sample_user_id):
        """Test exporting user location data."""
        export_data = await governance_service.export_user_location_data(
            sample_user_id, 'json', include_metadata=True
        )
        
        assert export_data['user_id'] == sample_user_id
        assert export_data['export_format'] == 'json'
        assert 'export_timestamp' in export_data
        assert 'data' in export_data
        assert 'user_preferences' in export_data
        assert isinstance(export_data['data'], dict)
    
    @pytest.mark.asyncio
    async def test_get_data_governance_dashboard(self, governance_service, sample_user_id):
        """Test getting data governance dashboard."""
        dashboard = await governance_service.get_data_governance_dashboard(sample_user_id)
        
        assert dashboard['user_id'] == sample_user_id
        assert 'preferences' in dashboard
        assert 'sharing_permissions' in dashboard
        assert 'retention_records' in dashboard
        assert 'recent_exports' in dashboard
        assert 'statistics' in dashboard
        assert 'last_updated' in dashboard
        assert isinstance(dashboard['sharing_permissions'], list)
        assert isinstance(dashboard['retention_records'], list)
        assert isinstance(dashboard['recent_exports'], list)
        assert isinstance(dashboard['statistics'], dict)
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_user_id(self, governance_service):
        """Test error handling for invalid user ID."""
        with pytest.raises(Exception):
            await governance_service.create_user_data_preferences(None, {})
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_preferences(self, governance_service, sample_user_id):
        """Test error handling for invalid preferences."""
        with pytest.raises(Exception):
            await governance_service.create_user_data_preferences(
                sample_user_id, {'invalid_field': 'invalid_value'}
            )


class TestDataGovernanceLevels:
    """Test data governance level enums."""
    
    def test_data_governance_level_values(self):
        """Test data governance level enum values."""
        assert DataGovernanceLevel.MINIMAL == "minimal"
        assert DataGovernanceLevel.STANDARD == "standard"
        assert DataGovernanceLevel.COMPREHENSIVE == "comprehensive"
        assert DataGovernanceLevel.RESEARCH == "research"
    
    def test_sharing_scope_values(self):
        """Test sharing scope enum values."""
        assert SharingScope.PRIVATE == "private"
        assert SharingScope.FARM_ONLY == "farm_only"
        assert SharingScope.CONSULTANT == "consultant"
        assert SharingScope.RESEARCH == "research"
        assert SharingScope.PUBLIC == "public"
    
    def test_retention_policy_values(self):
        """Test retention policy enum values."""
        assert RetentionPolicy.MINIMAL == "minimal"
        assert RetentionPolicy.SHORT == "short"
        assert RetentionPolicy.STANDARD == "standard"
        assert RetentionPolicy.LONG == "long"
        assert RetentionPolicy.EXTENDED == "extended"


class TestDataSharingRequest:
    """Test DataSharingRequest dataclass."""
    
    def test_data_sharing_request_creation(self):
        """Test creating a data sharing request."""
        request_id = str(uuid4())
        now = datetime.utcnow()
        
        sharing_req = DataSharingRequest(
            request_id=request_id,
            user_id="user-123",
            farm_id="farm-456",
            requested_by="consultant-789",
            sharing_purpose="agricultural_consultation",
            data_types_requested=["farm_location"],
            security_level="sensitive",
            requested_at=now,
            expires_at=now + timedelta(days=30),
            status="pending"
        )
        
        assert sharing_req.request_id == request_id
        assert sharing_req.user_id == "user-123"
        assert sharing_req.farm_id == "farm-456"
        assert sharing_req.requested_by == "consultant-789"
        assert sharing_req.sharing_purpose == "agricultural_consultation"
        assert sharing_req.data_types_requested == ["farm_location"]
        assert sharing_req.security_level == "sensitive"
        assert sharing_req.status == "pending"


class TestDataRetentionRecord:
    """Test DataRetentionRecord dataclass."""
    
    def test_data_retention_record_creation(self):
        """Test creating a data retention record."""
        record_id = str(uuid4())
        now = datetime.utcnow()
        
        retention_record = DataRetentionRecord(
            record_id=record_id,
            user_id="user-123",
            data_type="farm_location",
            data_id="location-456",
            retention_policy=RetentionPolicy.STANDARD,
            created_at=now,
            expires_at=now + timedelta(days=1095),
            last_accessed=now,
            access_count=0,
            auto_delete_enabled=True
        )
        
        assert retention_record.record_id == record_id
        assert retention_record.user_id == "user-123"
        assert retention_record.data_type == "farm_location"
        assert retention_record.data_id == "location-456"
        assert retention_record.retention_policy == RetentionPolicy.STANDARD
        assert retention_record.access_count == 0
        assert retention_record.auto_delete_enabled is True


class TestUserDataControlPreferences:
    """Test UserDataControlPreferences dataclass."""
    
    def test_user_preferences_creation(self):
        """Test creating user data control preferences."""
        now = datetime.utcnow()
        
        preferences = UserDataControlPreferences(
            user_id="user-123",
            data_governance_level=DataGovernanceLevel.STANDARD,
            sharing_scope=SharingScope.FARM_ONLY,
            retention_policy=RetentionPolicy.STANDARD,
            allow_analytics=False,
            allow_research_sharing=True,
            allow_consultant_access=True,
            location_precision_level="medium",
            automatic_data_cleanup=True,
            notification_preferences={
                'data_sharing_notifications': True,
                'retention_warnings': True,
                'access_alerts': True,
                'policy_changes': True
            },
            created_at=now,
            updated_at=now
        )
        
        assert preferences.user_id == "user-123"
        assert preferences.data_governance_level == DataGovernanceLevel.STANDARD
        assert preferences.sharing_scope == SharingScope.FARM_ONLY
        assert preferences.retention_policy == RetentionPolicy.STANDARD
        assert preferences.allow_analytics is False
        assert preferences.allow_research_sharing is True
        assert preferences.allow_consultant_access is True
        assert preferences.location_precision_level == "medium"
        assert preferences.automatic_data_cleanup is True
        assert len(preferences.notification_preferences) == 4


# Integration tests
class TestDataGovernanceIntegration:
    """Integration tests for data governance functionality."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session for integration tests."""
        return Mock()
    
    @pytest.fixture
    def governance_service(self, mock_db_session):
        """Governance service instance for integration tests."""
        return LocationDataGovernanceService(mock_db_session)
    
    @pytest.mark.asyncio
    async def test_complete_data_governance_workflow(self, governance_service):
        """Test complete data governance workflow."""
        user_id = "integration-test-user"
        
        # 1. Create user preferences
        preferences = await governance_service.create_user_data_preferences(user_id, {
            'allow_consultant_access': True,
            'allow_research_sharing': False,
            'retention_policy': 'long'
        })
        
        assert preferences.user_id == user_id
        assert preferences.allow_consultant_access is True
        assert preferences.allow_research_sharing is False
        
        # 2. Create sharing request (should auto-approve for consultant)
        sharing_request = {
            'requested_by': 'consultant-123',
            'purpose': 'agricultural_consultation',
            'data_types': ['farm_location'],
            'security_level': 'sensitive'
        }
        
        sharing_req = await governance_service.manage_location_sharing(
            user_id, 'farm-456', sharing_request
        )
        
        assert sharing_req.status == 'approved'
        
        # 3. Manage data retention
        retention_record = await governance_service.manage_data_retention(
            user_id, 'farm_location', 'location-789'
        )
        
        assert retention_record.user_id == user_id
        assert retention_record.retention_policy == RetentionPolicy.LONG
        
        # 4. Export data
        export_data = await governance_service.export_user_location_data(user_id)
        
        assert export_data['user_id'] == user_id
        assert 'data' in export_data
        
        # 5. Get dashboard
        dashboard = await governance_service.get_data_governance_dashboard(user_id)
        
        assert dashboard['user_id'] == user_id
        assert dashboard['preferences'] is not None
        
        # 6. Delete data
        deletion_summary = await governance_service.delete_user_location_data(user_id)
        
        assert deletion_summary['user_id'] == user_id
        assert deletion_summary['records_deleted'] >= 0


# Performance tests
class TestDataGovernancePerformance:
    """Performance tests for data governance functionality."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session for performance tests."""
        return Mock()
    
    @pytest.fixture
    def governance_service(self, mock_db_session):
        """Governance service instance for performance tests."""
        return LocationDataGovernanceService(mock_db_session)
    
    @pytest.mark.asyncio
    async def test_concurrent_preferences_creation(self, governance_service):
        """Test concurrent creation of user preferences."""
        user_ids = [f"user-{i}" for i in range(10)]
        
        tasks = [
            governance_service.create_user_data_preferences(user_id)
            for user_id in user_ids
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 10
        for i, preferences in enumerate(results):
            assert preferences.user_id == f"user-{i}"
    
    @pytest.mark.asyncio
    async def test_bulk_sharing_requests(self, governance_service):
        """Test bulk creation of sharing requests."""
        user_id = "bulk-test-user"
        
        # Create user preferences first
        await governance_service.create_user_data_preferences(user_id)
        
        # Create multiple sharing requests
        sharing_requests = [
            {
                'requested_by': f'consultant-{i}',
                'purpose': 'agricultural_consultation',
                'data_types': ['farm_location'],
                'security_level': 'sensitive'
            }
            for i in range(5)
        ]
        
        tasks = [
            governance_service.manage_location_sharing(user_id, f'farm-{i}', req)
            for i, req in enumerate(sharing_requests)
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 5
        for i, sharing_req in enumerate(results):
            assert sharing_req.user_id == user_id
            assert sharing_req.requested_by == f'consultant-{i}'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

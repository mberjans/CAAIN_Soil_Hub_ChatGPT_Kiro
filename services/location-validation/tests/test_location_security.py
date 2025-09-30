"""
Tests for Location Security Service
CAAIN Soil Hub - Location Validation Service

Comprehensive test suite for location data security and privacy features.
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
from typing import Dict, Any

from src.services.location_security_service import (
    LocationSecurityManager,
    LocationEncryptionService,
    LocationAccessControlService,
    LocationPrivacyService,
    LocationSecurityAuditService,
    LocationSecurityContext,
    SecurityLevel,
    AccessType
)


class TestLocationEncryptionService:
    """Test suite for location encryption service."""
    
    @pytest.fixture
    def encryption_service(self):
        """Create encryption service instance."""
        return LocationEncryptionService()
    
    @pytest.fixture
    def sample_location_data(self):
        """Sample location data for testing."""
        return {
            'farm_id': 'farm-123',
            'latitude': 40.7128,
            'longitude': -74.0060,
            'address': '123 Farm Road, New York, NY 10001',
            'postal_code': '10001',
            'elevation_meters': 10.5,
            'boundary': {
                'type': 'Polygon',
                'coordinates': [[[-74.01, 40.71], [-74.00, 40.71], [-74.00, 40.72], [-74.01, 40.72], [-74.01, 40.71]]]
            }
        }
    
    def test_encrypt_sensitive_data(self, encryption_service, sample_location_data):
        """Test encryption of sensitive location data."""
        # Encrypt sensitive data
        encrypted_data = encryption_service.encrypt_location_data(
            sample_location_data, SecurityLevel.SENSITIVE
        )
        
        # Verify encryption metadata
        assert '_encryption_metadata' in encrypted_data
        assert encrypted_data['_encryption_metadata']['security_level'] == 'sensitive'
        assert encrypted_data['_encryption_metadata']['encrypted_fields'] is not None
        
        # Verify sensitive fields are encrypted
        sensitive_fields = ['latitude', 'longitude', 'address', 'postal_code', 'elevation_meters', 'boundary']
        for field in sensitive_fields:
            if field in sample_location_data:
                assert field in encrypted_data
                assert encrypted_data[field] != sample_location_data[field]  # Should be encrypted
    
    def test_decrypt_sensitive_data(self, encryption_service, sample_location_data):
        """Test decryption of sensitive location data."""
        # Encrypt then decrypt
        encrypted_data = encryption_service.encrypt_location_data(
            sample_location_data, SecurityLevel.SENSITIVE
        )
        decrypted_data = encryption_service.decrypt_location_data(encrypted_data)
        
        # Verify decrypted data matches original
        for key, value in sample_location_data.items():
            if key in decrypted_data:
                assert decrypted_data[key] == value
    
    def test_encrypt_highly_sensitive_data(self, encryption_service, sample_location_data):
        """Test encryption of highly sensitive location data."""
        # Add financial data
        sample_location_data['financial_data'] = {
            'annual_revenue': 500000,
            'operating_costs': 300000
        }
        
        # Encrypt highly sensitive data
        encrypted_data = encryption_service.encrypt_location_data(
            sample_location_data, SecurityLevel.HIGHLY_SENSITIVE
        )
        
        # Verify encryption metadata
        assert encrypted_data['_encryption_metadata']['security_level'] == 'highly_sensitive'
        
        # Verify financial data is encrypted
        assert 'financial_data' in encrypted_data
        assert encrypted_data['financial_data'] != sample_location_data['financial_data']
    
    def test_key_rotation(self, encryption_service):
        """Test encryption key rotation."""
        # Rotate keys for sensitive level
        success = encryption_service.rotate_keys(SecurityLevel.SENSITIVE)
        assert success is True
        
        # Verify key version updated
        key_version = encryption_service._get_key_version(SecurityLevel.SENSITIVE)
        assert 'sensitive' in key_version
        assert '2024' in key_version  # Should contain current year
    
    def test_encryption_with_invalid_data(self, encryption_service):
        """Test encryption with invalid data."""
        invalid_data = {
            'latitude': 'invalid',  # Should be float
            'longitude': None
        }
        
        # Should handle invalid data gracefully
        with pytest.raises(Exception):
            encryption_service.encrypt_location_data(invalid_data, SecurityLevel.SENSITIVE)


class TestLocationAccessControlService:
    """Test suite for location access control service."""
    
    @pytest.fixture
    def access_control_service(self):
        """Create access control service instance."""
        return LocationAccessControlService()
    
    @pytest.fixture
    def security_context(self):
        """Create security context for testing."""
        return LocationSecurityContext(
            user_id='user-123',
            farm_id='farm-123',
            access_type=AccessType.READ,
            security_level=SecurityLevel.SENSITIVE,
            consent_given=True
        )
    
    @pytest.mark.asyncio
    async def test_farmer_access_permissions(self, access_control_service, security_context):
        """Test farmer access permissions."""
        # Test farmer access to sensitive data
        has_access, message = await access_control_service.check_access_permission(
            'farmer', security_context
        )
        assert has_access is True
        assert 'granted' in message.lower()
    
    @pytest.mark.asyncio
    async def test_consultant_access_with_consent(self, access_control_service, security_context):
        """Test consultant access with farmer consent."""
        # Test consultant access to sensitive data with consent
        has_access, message = await access_control_service.check_access_permission(
            'consultant', security_context
        )
        assert has_access is True
        assert 'granted' in message.lower()
    
    @pytest.mark.asyncio
    async def test_consultant_access_without_consent(self, access_control_service):
        """Test consultant access without farmer consent."""
        # Create context without consent
        context_no_consent = LocationSecurityContext(
            user_id='user-123',
            farm_id='farm-123',
            access_type=AccessType.READ,
            security_level=SecurityLevel.SENSITIVE,
            consent_given=False
        )
        
        # Test consultant access without consent
        has_access, message = await access_control_service.check_access_permission(
            'consultant', context_no_consent
        )
        assert has_access is False
        assert 'consent' in message.lower()
    
    @pytest.mark.asyncio
    async def test_consultant_access_highly_sensitive(self, access_control_service):
        """Test consultant access to highly sensitive data."""
        # Create context for highly sensitive data
        context_highly_sensitive = LocationSecurityContext(
            user_id='user-123',
            farm_id='farm-123',
            access_type=AccessType.READ,
            security_level=SecurityLevel.HIGHLY_SENSITIVE,
            consent_given=True
        )
        
        # Test consultant access to highly sensitive data
        has_access, message = await access_control_service.check_access_permission(
            'consultant', context_highly_sensitive
        )
        assert has_access is False  # No access to highly sensitive data
    
    @pytest.mark.asyncio
    async def test_admin_access_permissions(self, access_control_service, security_context):
        """Test admin access permissions."""
        # Test admin access to sensitive data
        has_access, message = await access_control_service.check_access_permission(
            'admin', security_context
        )
        assert has_access is True
        assert 'granted' in message.lower()
    
    @pytest.mark.asyncio
    async def test_get_accessible_fields_farmer(self, access_control_service):
        """Test getting accessible fields for farmer."""
        fields = await access_control_service.get_accessible_fields(
            'farmer', SecurityLevel.SENSITIVE
        )
        
        # Farmer should have access to all fields including coordinates
        assert 'latitude' in fields
        assert 'longitude' in fields
        assert 'boundary' in fields
    
    @pytest.mark.asyncio
    async def test_get_accessible_fields_consultant(self, access_control_service):
        """Test getting accessible fields for consultant."""
        fields = await access_control_service.get_accessible_fields(
            'consultant', SecurityLevel.SENSITIVE
        )
        
        # Consultant should have limited access
        assert 'latitude' not in fields
        assert 'longitude' not in fields
        assert 'boundary' not in fields
        assert 'country' in fields
        assert 'state' in fields


class TestLocationPrivacyService:
    """Test suite for location privacy service."""
    
    @pytest.fixture
    def privacy_service(self):
        """Create privacy service instance."""
        return LocationPrivacyService()
    
    @pytest.fixture
    def sample_location_data(self):
        """Sample location data for privacy testing."""
        return {
            'farm_id': 'farm-123',
            'latitude': 40.7128,
            'longitude': -74.0060,
            'address': '123 Farm Road, New York, NY 10001',
            'postal_code': '10001',
            'financial_data': {'revenue': 500000}
        }
    
    def test_anonymize_coordinates(self, privacy_service):
        """Test coordinate anonymization."""
        # Test medium anonymization
        lat, lng = privacy_service.anonymize_coordinates(40.7128, -74.0060, 'medium')
        
        # Should be rounded to 0.1 degree precision
        assert lat == 40.7
        assert lng == -74.0
    
    def test_anonymize_coordinates_high_precision(self, privacy_service):
        """Test coordinate anonymization with high precision."""
        # Test high anonymization
        lat, lng = privacy_service.anonymize_coordinates(40.7128, -74.0060, 'high')
        
        # Should be rounded to 1.0 degree precision
        assert lat == 41.0
        assert lng == -74.0
    
    def test_anonymize_location_data(self, privacy_service, sample_location_data):
        """Test location data anonymization."""
        # Anonymize location data
        anonymized_data = privacy_service.anonymize_location_data(
            sample_location_data, 'medium'
        )
        
        # Verify coordinates are anonymized
        assert anonymized_data['latitude'] == 40.7
        assert anonymized_data['longitude'] == -74.0
        
        # Verify address is anonymized (only city, state)
        assert 'New York, NY' in anonymized_data['address']
        assert '123 Farm Road' not in anonymized_data['address']
        
        # Verify postal code is anonymized
        assert anonymized_data['postal_code'] == '100**'
        
        # Verify financial data is removed
        assert 'financial_data' not in anonymized_data
        
        # Verify privacy metadata
        assert '_privacy_metadata' in anonymized_data
        assert anonymized_data['_privacy_metadata']['anonymized'] is True
    
    def test_check_data_retention_expiry(self, privacy_service):
        """Test data retention expiry check."""
        # Create data with old timestamp
        old_data = {
            'created_at': datetime.utcnow() - timedelta(days=400)  # Over 1 year old
        }
        
        # Check retention for highly sensitive data (1 year retention)
        is_expired = privacy_service.check_data_retention_expiry(
            old_data, SecurityLevel.HIGHLY_SENSITIVE
        )
        assert is_expired is True
        
        # Check retention for sensitive data (2 years retention)
        is_expired = privacy_service.check_data_retention_expiry(
            old_data, SecurityLevel.SENSITIVE
        )
        assert is_expired is False  # Should not be expired yet


class TestLocationSecurityAuditService:
    """Test suite for location security audit service."""
    
    @pytest.fixture
    def audit_service(self):
        """Create audit service instance."""
        return LocationSecurityAuditService()
    
    @pytest.mark.asyncio
    async def test_log_security_event_success(self, audit_service):
        """Test logging successful security event."""
        event_id = await audit_service.log_security_event(
            user_id='user-123',
            action='read',
            resource_type='farm_location',
            resource_id='farm-123',
            security_level=SecurityLevel.SENSITIVE,
            success=True,
            details={'field': 'latitude'}
        )
        
        assert event_id is not None
        assert len(audit_service.audit_logs) == 1
        
        # Verify log entry
        log_entry = audit_service.audit_logs[0]
        assert log_entry.user_id == 'user-123'
        assert log_entry.action == 'read'
        assert log_entry.success is True
    
    @pytest.mark.asyncio
    async def test_log_security_event_failure(self, audit_service):
        """Test logging failed security event."""
        event_id = await audit_service.log_security_event(
            user_id='user-123',
            action='read',
            resource_type='farm_location',
            resource_id='farm-123',
            security_level=SecurityLevel.HIGHLY_SENSITIVE,
            success=False,
            details={'reason': 'insufficient_permissions'}
        )
        
        assert event_id is not None
        
        # Verify log entry
        log_entry = audit_service.audit_logs[0]
        assert log_entry.success is False
        assert 'insufficient_permissions' in log_entry.details['reason']
    
    @pytest.mark.asyncio
    async def test_detect_security_anomalies_excessive_failed_access(self, audit_service):
        """Test detection of excessive failed access attempts."""
        # Log multiple failed access attempts
        for i in range(6):  # More than threshold of 5
            await audit_service.log_security_event(
                user_id='user-123',
                action='read',
                resource_type='farm_location',
                resource_id=f'farm-{i}',
                security_level=SecurityLevel.SENSITIVE,
                success=False,
                details={'reason': 'access_denied'}
            )
        
        # Detect anomalies
        anomalies = await audit_service.detect_security_anomalies('user-123')
        
        # Should detect excessive failed access
        assert len(anomalies) > 0
        failed_access_anomaly = next(
            (a for a in anomalies if a['type'] == 'excessive_failed_access'), None
        )
        assert failed_access_anomaly is not None
        assert failed_access_anomaly['severity'] == 'high'
    
    @pytest.mark.asyncio
    async def test_get_audit_trail_with_filters(self, audit_service):
        """Test getting audit trail with filters."""
        # Log some events
        await audit_service.log_security_event(
            user_id='user-123',
            action='read',
            resource_type='farm_location',
            resource_id='farm-123',
            security_level=SecurityLevel.SENSITIVE,
            success=True,
            details={}
        )
        
        await audit_service.log_security_event(
            user_id='user-456',
            action='write',
            resource_type='farm_location',
            resource_id='farm-456',
            security_level=SecurityLevel.SENSITIVE,
            success=True,
            details={}
        )
        
        # Get audit trail filtered by user
        audit_trail = await audit_service.get_audit_trail(user_id='user-123')
        
        assert len(audit_trail) == 1
        assert audit_trail[0].user_id == 'user-123'


class TestLocationSecurityManager:
    """Test suite for location security manager."""
    
    @pytest.fixture
    def security_manager(self):
        """Create security manager instance."""
        return LocationSecurityManager()
    
    @pytest.fixture
    def sample_location_data(self):
        """Sample location data for testing."""
        return {
            'farm_id': 'farm-123',
            'latitude': 40.7128,
            'longitude': -74.0060,
            'address': '123 Farm Road, New York, NY 10001',
            'postal_code': '10001'
        }
    
    @pytest.fixture
    def security_context(self):
        """Create security context for testing."""
        return LocationSecurityContext(
            user_id='user-123',
            farm_id='farm-123',
            access_type=AccessType.READ,
            security_level=SecurityLevel.SENSITIVE,
            consent_given=True
        )
    
    @pytest.mark.asyncio
    async def test_secure_location_data_farmer(self, security_manager, sample_location_data, security_context):
        """Test securing location data for farmer."""
        # Secure data for farmer
        secured_data = await security_manager.secure_location_data(
            sample_location_data, security_context, 'farmer'
        )
        
        # Verify data is encrypted
        assert '_encryption_metadata' in secured_data
        
        # Verify audit log was created
        assert len(security_manager.audit_service.audit_logs) == 1
        log_entry = security_manager.audit_service.audit_logs[0]
        assert log_entry.success is True
        assert log_entry.action == 'read'
    
    @pytest.mark.asyncio
    async def test_secure_location_data_consultant(self, security_manager, sample_location_data, security_context):
        """Test securing location data for consultant."""
        # Secure data for consultant
        secured_data = await security_manager.secure_location_data(
            sample_location_data, security_context, 'consultant'
        )
        
        # Verify data is anonymized for consultant
        assert '_privacy_metadata' in secured_data
        assert secured_data['_privacy_metadata']['anonymized'] is True
        
        # Verify coordinates are anonymized
        assert secured_data['latitude'] == 40.7
        assert secured_data['longitude'] == -74.0
    
    @pytest.mark.asyncio
    async def test_secure_location_data_access_denied(self, security_manager, sample_location_data):
        """Test securing location data with access denied."""
        # Create context without consent for consultant
        context_no_consent = LocationSecurityContext(
            user_id='user-123',
            farm_id='farm-123',
            access_type=AccessType.READ,
            security_level=SecurityLevel.SENSITIVE,
            consent_given=False
        )
        
        # Should raise PermissionError
        with pytest.raises(PermissionError):
            await security_manager.secure_location_data(
                sample_location_data, context_no_consent, 'consultant'
            )
    
    @pytest.mark.asyncio
    async def test_decrypt_location_data(self, security_manager, sample_location_data, security_context):
        """Test decrypting location data."""
        # First encrypt the data
        encrypted_data = await security_manager.secure_location_data(
            sample_location_data, security_context, 'farmer'
        )
        
        # Then decrypt it
        decrypted_data = await security_manager.decrypt_location_data(
            encrypted_data, security_context, 'farmer'
        )
        
        # Verify decrypted data matches original
        for key, value in sample_location_data.items():
            if key in decrypted_data:
                assert decrypted_data[key] == value
    
    @pytest.mark.asyncio
    async def test_handle_gdpr_access_request(self, security_manager):
        """Test handling GDPR access request."""
        result = await security_manager.handle_gdpr_request('user-123', 'access')
        
        assert result['user_id'] == 'user-123'
        assert 'export_timestamp' in result
        assert 'data_types' in result
    
    @pytest.mark.asyncio
    async def test_handle_gdpr_deletion_request(self, security_manager):
        """Test handling GDPR deletion request."""
        result = await security_manager.handle_gdpr_request('user-123', 'deletion')
        
        assert result['user_id'] == 'user-123'
        assert 'deletion_timestamp' in result
    
    @pytest.mark.asyncio
    async def test_handle_gdpr_portability_request(self, security_manager):
        """Test handling GDPR portability request."""
        result = await security_manager.handle_gdpr_request('user-123', 'portability')
        
        assert result['user_id'] == 'user-123'
        assert 'export_timestamp' in result
        assert result['format'] == 'JSON'


class TestSecurityIntegration:
    """Integration tests for security features."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_security_workflow(self):
        """Test complete security workflow."""
        # Initialize security manager
        security_manager = LocationSecurityManager()
        
        # Sample location data
        location_data = {
            'farm_id': 'farm-123',
            'latitude': 40.7128,
            'longitude': -74.0060,
            'address': '123 Farm Road, New York, NY 10001',
            'financial_data': {'revenue': 500000}
        }
        
        # Create security context
        security_context = LocationSecurityContext(
            user_id='user-123',
            farm_id='farm-123',
            access_type=AccessType.READ,
            security_level=SecurityLevel.HIGHLY_SENSITIVE,
            consent_given=True
        )
        
        # Secure data for farmer
        secured_data = await security_manager.secure_location_data(
            location_data, security_context, 'farmer'
        )
        
        # Verify data is encrypted
        assert '_encryption_metadata' in secured_data
        
        # Decrypt data
        decrypted_data = await security_manager.decrypt_location_data(
            secured_data, security_context, 'farmer'
        )
        
        # Verify decrypted data matches original
        assert decrypted_data['latitude'] == location_data['latitude']
        assert decrypted_data['longitude'] == location_data['longitude']
        assert decrypted_data['financial_data'] == location_data['financial_data']
        
        # Verify audit logs
        assert len(security_manager.audit_service.audit_logs) == 2  # One for encrypt, one for decrypt
    
    @pytest.mark.asyncio
    async def test_security_anomaly_detection_workflow(self):
        """Test security anomaly detection workflow."""
        # Initialize security manager
        security_manager = LocationSecurityManager()
        
        # Simulate suspicious activity
        for i in range(6):  # More than threshold
            await security_manager.audit_service.log_security_event(
                user_id='user-123',
                action='read',
                resource_type='farm_location',
                resource_id=f'farm-{i}',
                security_level=SecurityLevel.HIGHLY_SENSITIVE,
                success=False,
                details={'reason': 'access_denied'}
            )
        
        # Detect anomalies
        anomalies = await security_manager.audit_service.detect_security_anomalies('user-123')
        
        # Verify anomaly detection
        assert len(anomalies) > 0
        assert any(a['type'] == 'excessive_failed_access' for a in anomalies)


# Performance tests
class TestSecurityPerformance:
    """Performance tests for security features."""
    
    @pytest.mark.asyncio
    async def test_encryption_performance(self):
        """Test encryption performance with large datasets."""
        encryption_service = LocationEncryptionService()
        
        # Large location dataset
        large_data = {
            'farm_id': 'farm-123',
            'latitude': 40.7128,
            'longitude': -74.0060,
            'boundary': {
                'type': 'Polygon',
                'coordinates': [[[-74.01, 40.71], [-74.00, 40.71], [-74.00, 40.72], [-74.01, 40.72], [-74.01, 40.71]]]
            },
            'field_data': [
                {'field_id': f'field-{i}', 'latitude': 40.7128 + i*0.001, 'longitude': -74.0060 + i*0.001}
                for i in range(100)  # 100 fields
            ]
        }
        
        import time
        start_time = time.time()
        
        # Encrypt large dataset
        encrypted_data = encryption_service.encrypt_location_data(large_data, SecurityLevel.SENSITIVE)
        
        encryption_time = time.time() - start_time
        
        # Should complete within reasonable time (< 1 second)
        assert encryption_time < 1.0
        
        # Decrypt and verify
        decrypted_data = encryption_service.decrypt_location_data(encrypted_data)
        assert decrypted_data['farm_id'] == large_data['farm_id']
        assert len(decrypted_data['field_data']) == 100


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
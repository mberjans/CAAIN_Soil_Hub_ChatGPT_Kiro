"""
Security Models for Location Validation Service
CAAIN Soil Hub - Location Validation Service

Database models for location data security and privacy features.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()


class LocationSecurityPolicy(Base):
    """Security policies for location data."""
    __tablename__ = 'location_security_policies'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    policy_name = Column(String(100), nullable=False, unique=True)
    security_level = Column(String(20), nullable=False)  # public, internal, sensitive, highly_sensitive
    encryption_required = Column(Boolean, default=True)
    anonymization_level = Column(String(20), default='medium')  # low, medium, high, maximum
    retention_days = Column(Integer, nullable=False)
    access_control_rules = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_security_policies_level', 'security_level'),
        Index('idx_security_policies_name', 'policy_name'),
    )


class LocationAccessLog(Base):
    """Audit log for location data access."""
    __tablename__ = 'location_access_logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(100), nullable=False)
    farm_id = Column(UUID(as_uuid=True), nullable=True)
    field_id = Column(UUID(as_uuid=True), nullable=True)
    action = Column(String(50), nullable=False)  # read, write, delete, export, share
    resource_type = Column(String(50), nullable=False)  # farm_location, field_boundary, etc.
    resource_id = Column(String(100), nullable=False)
    security_level = Column(String(20), nullable=False)
    success = Column(Boolean, nullable=False)
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=func.now())
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_access_logs_user_id', 'user_id'),
        Index('idx_access_logs_timestamp', 'timestamp'),
        Index('idx_access_logs_action', 'action'),
        Index('idx_access_logs_security_level', 'security_level'),
        Index('idx_access_logs_success', 'success'),
        Index('idx_access_logs_user_timestamp', 'user_id', 'timestamp'),
    )


class LocationEncryptionKey(Base):
    """Encryption keys for location data."""
    __tablename__ = 'location_encryption_keys'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key_name = Column(String(100), nullable=False, unique=True)
    security_level = Column(String(20), nullable=False)
    key_version = Column(String(50), nullable=False)
    encrypted_key = Column(Text, nullable=False)  # Encrypted key material
    key_hash = Column(String(64), nullable=False)  # SHA-256 hash of key
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=True)
    rotated_at = Column(DateTime, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_encryption_keys_level', 'security_level'),
        Index('idx_encryption_keys_active', 'is_active'),
        Index('idx_encryption_keys_version', 'key_version'),
    )


class LocationPrivacyConsent(Base):
    """User consent for location data processing."""
    __tablename__ = 'location_privacy_consents'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(100), nullable=False)
    farm_id = Column(UUID(as_uuid=True), nullable=True)
    consent_type = Column(String(50), nullable=False)  # data_processing, data_sharing, analytics
    consent_given = Column(Boolean, nullable=False)
    consent_timestamp = Column(DateTime, default=func.now())
    consent_version = Column(String(20), nullable=False)  # Version of privacy policy
    purpose = Column(Text, nullable=True)  # Specific purpose for consent
    expires_at = Column(DateTime, nullable=True)
    withdrawn_at = Column(DateTime, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_privacy_consents_user_id', 'user_id'),
        Index('idx_privacy_consents_type', 'consent_type'),
        Index('idx_privacy_consents_active', 'consent_given', 'withdrawn_at'),
        Index('idx_privacy_consents_user_type', 'user_id', 'consent_type'),
    )


class LocationDataRetention(Base):
    """Data retention tracking for location information."""
    __tablename__ = 'location_data_retention'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(100), nullable=False)
    farm_id = Column(UUID(as_uuid=True), nullable=True)
    field_id = Column(UUID(as_uuid=True), nullable=True)
    data_type = Column(String(50), nullable=False)  # farm_location, field_boundary, etc.
    security_level = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=func.now())
    retention_expires_at = Column(DateTime, nullable=False)
    is_anonymized = Column(Boolean, default=False)
    anonymization_level = Column(String(20), nullable=True)
    deletion_scheduled_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_data_retention_user_id', 'user_id'),
        Index('idx_data_retention_expires', 'retention_expires_at'),
        Index('idx_data_retention_deletion', 'deletion_scheduled_at'),
        Index('idx_data_retention_type', 'data_type'),
    )


class LocationSecurityAnomaly(Base):
    """Security anomalies detected in location data access."""
    __tablename__ = 'location_security_anomalies'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(100), nullable=False)
    anomaly_type = Column(String(50), nullable=False)  # excessive_failed_access, suspicious_pattern, etc.
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    description = Column(Text, nullable=False)
    detected_at = Column(DateTime, default=func.now())
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)  # Additional anomaly details
    
    # Indexes
    __table_args__ = (
        Index('idx_security_anomalies_user_id', 'user_id'),
        Index('idx_security_anomalies_type', 'anomaly_type'),
        Index('idx_security_anomalies_severity', 'severity'),
        Index('idx_security_anomalies_detected', 'detected_at'),
        Index('idx_security_anomalies_resolved', 'resolved_at'),
    )


class LocationDataExport(Base):
    """Track location data exports for compliance."""
    __tablename__ = 'location_data_exports'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(100), nullable=False)
    export_type = Column(String(50), nullable=False)  # gdpr_access, gdpr_portability, user_request
    export_format = Column(String(20), nullable=False)  # json, csv, xml
    data_types = Column(JSON, nullable=False)  # List of data types exported
    file_path = Column(Text, nullable=True)  # Path to exported file
    file_hash = Column(String(64), nullable=True)  # SHA-256 hash of exported file
    requested_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)
    download_count = Column(Integer, default=0)
    expires_at = Column(DateTime, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_data_exports_user_id', 'user_id'),
        Index('idx_data_exports_type', 'export_type'),
        Index('idx_data_exports_requested', 'requested_at'),
        Index('idx_data_exports_expires', 'expires_at'),
    )


class LocationSharingPermission(Base):
    """Permissions for sharing location data with third parties."""
    __tablename__ = 'location_sharing_permissions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(100), nullable=False)
    farm_id = Column(UUID(as_uuid=True), nullable=True)
    shared_with_user_id = Column(String(100), nullable=True)
    shared_with_organization = Column(String(200), nullable=True)
    sharing_purpose = Column(Text, nullable=False)
    data_types_shared = Column(JSON, nullable=False)  # List of data types
    security_level = Column(String(20), nullable=False)
    consent_given = Column(Boolean, nullable=False)
    consent_timestamp = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    access_log_count = Column(Integer, default=0)
    
    # Indexes
    __table_args__ = (
        Index('idx_sharing_permissions_user_id', 'user_id'),
        Index('idx_sharing_permissions_shared_with', 'shared_with_user_id'),
        Index('idx_sharing_permissions_active', 'consent_given', 'revoked_at'),
        Index('idx_sharing_permissions_expires', 'expires_at'),
    )


class LocationSecurityConfiguration(Base):
    """System-wide security configuration."""
    __tablename__ = 'location_security_configuration'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    config_key = Column(String(100), nullable=False, unique=True)
    config_value = Column(Text, nullable=False)
    config_type = Column(String(20), nullable=False)  # string, integer, boolean, json
    description = Column(Text, nullable=True)
    is_sensitive = Column(Boolean, default=False)  # Whether value should be encrypted
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_security_config_key', 'config_key'),
        Index('idx_security_config_sensitive', 'is_sensitive'),
    )


# Relationships (if needed)
# LocationAccessLog.farm_id -> Farm.id (if Farm model exists)
# LocationAccessLog.field_id -> Field.id (if Field model exists)
# LocationPrivacyConsent.farm_id -> Farm.id (if Farm model exists)
# LocationDataRetention.farm_id -> Farm.id (if Farm model exists)
# LocationDataRetention.field_id -> Field.id (if Field model exists)
# LocationSharingPermission.farm_id -> Farm.id (if Farm model exists)
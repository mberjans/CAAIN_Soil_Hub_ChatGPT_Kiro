"""
Location Security Database Service
CAAIN Soil Hub - Location Validation Service

Database integration service for location security and privacy features.
Handles database operations for security policies, audit logs, and compliance.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
import json
import os

from ..models.security_models import (
    LocationSecurityPolicy,
    LocationAccessLog,
    LocationEncryptionKey,
    LocationPrivacyConsent,
    LocationDataRetention,
    LocationSecurityAnomaly,
    LocationDataExport,
    LocationSharingPermission,
    LocationSecurityConfiguration
)

logger = logging.getLogger(__name__)


class LocationSecurityDatabaseService:
    """Database service for location security operations."""
    
    def __init__(self, database_url: str):
        """Initialize database service."""
        self.database_url = database_url
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.logger = logging.getLogger(__name__)
    
    def get_session(self) -> Session:
        """Get database session."""
        return self.SessionLocal()
    
    async def log_access_event(
        self,
        user_id: str,
        farm_id: Optional[str],
        field_id: Optional[str],
        action: str,
        resource_type: str,
        resource_id: str,
        security_level: str,
        success: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log location data access event."""
        try:
            session = self.get_session()
            
            try:
                access_log = LocationAccessLog(
                    user_id=user_id,
                    farm_id=farm_id,
                    field_id=field_id,
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    security_level=security_level,
                    success=success,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    details=details or {}
                )
                
                session.add(access_log)
                session.commit()
                
                self.logger.info(f"Access event logged: {action} by {user_id} - {'SUCCESS' if success else 'FAILED'}")
                return str(access_log.id)
                
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()
                
        except SQLAlchemyError as e:
            self.logger.error(f"Error logging access event: {e}")
            raise
    
    async def get_access_logs(
        self,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get access logs with optional filters."""
        try:
            session = self.get_session()
            
            try:
                query = session.query(LocationAccessLog)
                
                # Apply filters
                if user_id:
                    query = query.filter(LocationAccessLog.user_id == user_id)
                if resource_id:
                    query = query.filter(LocationAccessLog.resource_id == resource_id)
                if start_date:
                    query = query.filter(LocationAccessLog.timestamp >= start_date)
                if end_date:
                    query = query.filter(LocationAccessLog.timestamp <= end_date)
                
                # Order by timestamp and limit
                query = query.order_by(LocationAccessLog.timestamp.desc()).limit(limit)
                
                logs = query.all()
                
                # Convert to dict format
                result = []
                for log in logs:
                    log_dict = {
                        'id': str(log.id),
                        'user_id': log.user_id,
                        'farm_id': str(log.farm_id) if log.farm_id else None,
                        'field_id': str(log.field_id) if log.field_id else None,
                        'action': log.action,
                        'resource_type': log.resource_type,
                        'resource_id': log.resource_id,
                        'security_level': log.security_level,
                        'success': log.success,
                        'ip_address': log.ip_address,
                        'user_agent': log.user_agent,
                        'details': log.details,
                        'timestamp': log.timestamp.isoformat()
                    }
                    result.append(log_dict)
                
                return result
                
            finally:
                session.close()
                
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting access logs: {e}")
            return []
    
    async def create_privacy_consent(
        self,
        user_id: str,
        farm_id: Optional[str],
        consent_type: str,
        consent_given: bool,
        consent_version: str,
        purpose: Optional[str] = None,
        expires_at: Optional[datetime] = None
    ) -> str:
        """Create privacy consent record."""
        try:
            session = self.get_session()
            
            try:
                consent = LocationPrivacyConsent(
                    user_id=user_id,
                    farm_id=farm_id,
                    consent_type=consent_type,
                    consent_given=consent_given,
                    consent_version=consent_version,
                    purpose=purpose,
                    expires_at=expires_at
                )
                
                session.add(consent)
                session.commit()
                
                self.logger.info(f"Privacy consent created: {consent_type} for {user_id}")
                return str(consent.id)
                
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()
                
        except SQLAlchemyError as e:
            self.logger.error(f"Error creating privacy consent: {e}")
            raise
    
    async def get_privacy_consent(
        self,
        user_id: str,
        consent_type: str,
        farm_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get active privacy consent."""
        try:
            session = self.get_session()
            
            try:
                query = session.query(LocationPrivacyConsent).filter(
                    LocationPrivacyConsent.user_id == user_id,
                    LocationPrivacyConsent.consent_type == consent_type,
                    LocationPrivacyConsent.consent_given == True,
                    LocationPrivacyConsent.withdrawn_at.is_(None)
                )
                
                if farm_id:
                    query = query.filter(LocationPrivacyConsent.farm_id == farm_id)
                
                consent = query.first()
                
                if consent:
                    return {
                        'id': str(consent.id),
                        'user_id': consent.user_id,
                        'farm_id': str(consent.farm_id) if consent.farm_id else None,
                        'consent_type': consent.consent_type,
                        'consent_given': consent.consent_given,
                        'consent_timestamp': consent.consent_timestamp.isoformat(),
                        'consent_version': consent.consent_version,
                        'purpose': consent.purpose,
                        'expires_at': consent.expires_at.isoformat() if consent.expires_at else None
                    }
                
                return None
                
            finally:
                session.close()
                
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting privacy consent: {e}")
            return None
    
    async def create_data_retention_record(
        self,
        user_id: str,
        farm_id: Optional[str],
        field_id: Optional[str],
        data_type: str,
        security_level: str,
        retention_expires_at: datetime
    ) -> str:
        """Create data retention record."""
        try:
            session = self.get_session()
            
            try:
                retention_record = LocationDataRetention(
                    user_id=user_id,
                    farm_id=farm_id,
                    field_id=field_id,
                    data_type=data_type,
                    security_level=security_level,
                    retention_expires_at=retention_expires_at
                )
                
                session.add(retention_record)
                session.commit()
                
                self.logger.info(f"Data retention record created: {data_type} for {user_id}")
                return str(retention_record.id)
                
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()
                
        except SQLAlchemyError as e:
            self.logger.error(f"Error creating data retention record: {e}")
            raise
    
    async def get_expired_data_records(self) -> List[Dict[str, Any]]:
        """Get data records that have exceeded retention period."""
        try:
            session = self.get_session()
            
            try:
                current_time = datetime.utcnow()
                
                expired_records = session.query(LocationDataRetention).filter(
                    LocationDataRetention.retention_expires_at < current_time,
                    LocationDataRetention.deleted_at.is_(None)
                ).all()
                
                result = []
                for record in expired_records:
                    record_dict = {
                        'id': str(record.id),
                        'user_id': record.user_id,
                        'farm_id': str(record.farm_id) if record.farm_id else None,
                        'field_id': str(record.field_id) if record.field_id else None,
                        'data_type': record.data_type,
                        'security_level': record.security_level,
                        'created_at': record.created_at.isoformat(),
                        'retention_expires_at': record.retention_expires_at.isoformat(),
                        'is_anonymized': record.is_anonymized,
                        'anonymization_level': record.anonymization_level
                    }
                    result.append(record_dict)
                
                return result
                
            finally:
                session.close()
                
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting expired data records: {e}")
            return []
    
    async def create_security_anomaly(
        self,
        user_id: str,
        anomaly_type: str,
        severity: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create security anomaly record."""
        try:
            session = self.get_session()
            
            try:
                anomaly = LocationSecurityAnomaly(
                    user_id=user_id,
                    anomaly_type=anomaly_type,
                    severity=severity,
                    description=description,
                    metadata=metadata or {}
                )
                
                session.add(anomaly)
                session.commit()
                
                self.logger.warning(f"Security anomaly created: {anomaly_type} for {user_id} - {severity}")
                return str(anomaly.id)
                
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()
                
        except SQLAlchemyError as e:
            self.logger.error(f"Error creating security anomaly: {e}")
            raise
    
    async def get_security_anomalies(
        self,
        user_id: Optional[str] = None,
        anomaly_type: Optional[str] = None,
        severity: Optional[str] = None,
        resolved: Optional[bool] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get security anomalies with optional filters."""
        try:
            session = self.get_session()
            
            try:
                query = session.query(LocationSecurityAnomaly)
                
                # Apply filters
                if user_id:
                    query = query.filter(LocationSecurityAnomaly.user_id == user_id)
                if anomaly_type:
                    query = query.filter(LocationSecurityAnomaly.anomaly_type == anomaly_type)
                if severity:
                    query = query.filter(LocationSecurityAnomaly.severity == severity)
                if resolved is not None:
                    if resolved:
                        query = query.filter(LocationSecurityAnomaly.resolved_at.isnot(None))
                    else:
                        query = query.filter(LocationSecurityAnomaly.resolved_at.is_(None))
                
                # Order by detection time and limit
                query = query.order_by(LocationSecurityAnomaly.detected_at.desc()).limit(limit)
                
                anomalies = query.all()
                
                # Convert to dict format
                result = []
                for anomaly in anomalies:
                    anomaly_dict = {
                        'id': str(anomaly.id),
                        'user_id': anomaly.user_id,
                        'anomaly_type': anomaly.anomaly_type,
                        'severity': anomaly.severity,
                        'description': anomaly.description,
                        'detected_at': anomaly.detected_at.isoformat(),
                        'resolved_at': anomaly.resolved_at.isoformat() if anomaly.resolved_at else None,
                        'resolution_notes': anomaly.resolution_notes,
                        'metadata': anomaly.metadata
                    }
                    result.append(anomaly_dict)
                
                return result
                
            finally:
                session.close()
                
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting security anomalies: {e}")
            return []
    
    async def create_data_export_record(
        self,
        user_id: str,
        export_type: str,
        export_format: str,
        data_types: List[str],
        file_path: Optional[str] = None,
        expires_at: Optional[datetime] = None
    ) -> str:
        """Create data export record."""
        try:
            session = self.get_session()
            
            try:
                export_record = LocationDataExport(
                    user_id=user_id,
                    export_type=export_type,
                    export_format=export_format,
                    data_types=data_types,
                    file_path=file_path,
                    expires_at=expires_at
                )
                
                session.add(export_record)
                session.commit()
                
                self.logger.info(f"Data export record created: {export_type} for {user_id}")
                return str(export_record.id)
                
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()
                
        except SQLAlchemyError as e:
            self.logger.error(f"Error creating data export record: {e}")
            raise
    
    async def get_security_configuration(self, config_key: str) -> Optional[str]:
        """Get security configuration value."""
        try:
            session = self.get_session()
            
            try:
                config = session.query(LocationSecurityConfiguration).filter(
                    LocationSecurityConfiguration.config_key == config_key
                ).first()
                
                if config:
                    return config.config_value
                
                return None
                
            finally:
                session.close()
                
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting security configuration: {e}")
            return None
    
    async def update_security_configuration(
        self,
        config_key: str,
        config_value: str,
        description: Optional[str] = None
    ) -> bool:
        """Update security configuration."""
        try:
            session = self.get_session()
            
            try:
                config = session.query(LocationSecurityConfiguration).filter(
                    LocationSecurityConfiguration.config_key == config_key
                ).first()
                
                if config:
                    config.config_value = config_value
                    if description:
                        config.description = description
                    config.updated_at = datetime.utcnow()
                else:
                    config = LocationSecurityConfiguration(
                        config_key=config_key,
                        config_value=config_value,
                        config_type='string',
                        description=description or ''
                    )
                    session.add(config)
                
                session.commit()
                
                self.logger.info(f"Security configuration updated: {config_key}")
                return True
                
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()
                
        except SQLAlchemyError as e:
            self.logger.error(f"Error updating security configuration: {e}")
            return False
    
    async def get_security_policy(self, security_level: str) -> Optional[Dict[str, Any]]:
        """Get security policy for security level."""
        try:
            session = self.get_session()
            
            try:
                policy = session.query(LocationSecurityPolicy).filter(
                    LocationSecurityPolicy.security_level == security_level
                ).first()
                
                if policy:
                    return {
                        'id': str(policy.id),
                        'policy_name': policy.policy_name,
                        'security_level': policy.security_level,
                        'encryption_required': policy.encryption_required,
                        'anonymization_level': policy.anonymization_level,
                        'retention_days': policy.retention_days,
                        'access_control_rules': policy.access_control_rules,
                        'created_at': policy.created_at.isoformat(),
                        'updated_at': policy.updated_at.isoformat()
                    }
                
                return None
                
            finally:
                session.close()
                
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting security policy: {e}")
            return None
    
    async def cleanup_expired_data(self) -> int:
        """Clean up expired data records."""
        try:
            session = self.get_session()
            
            try:
                current_time = datetime.utcnow()
                
                # Get expired records
                expired_records = session.query(LocationDataRetention).filter(
                    LocationDataRetention.retention_expires_at < current_time,
                    LocationDataRetention.deleted_at.is_(None)
                ).all()
                
                cleanup_count = 0
                for record in expired_records:
                    # Mark as scheduled for deletion
                    record.deletion_scheduled_at = current_time
                    cleanup_count += 1
                
                session.commit()
                
                self.logger.info(f"Marked {cleanup_count} expired data records for cleanup")
                return cleanup_count
                
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()
                
        except SQLAlchemyError as e:
            self.logger.error(f"Error cleaning up expired data: {e}")
            return 0
    
    async def get_security_statistics(self) -> Dict[str, Any]:
        """Get security statistics for monitoring."""
        try:
            session = self.get_session()
            
            try:
                # Get access log statistics
                total_access_logs = session.query(LocationAccessLog).count()
                failed_access_logs = session.query(LocationAccessLog).filter(
                    LocationAccessLog.success == False
                ).count()
                
                # Get anomaly statistics
                total_anomalies = session.query(LocationSecurityAnomaly).count()
                unresolved_anomalies = session.query(LocationSecurityAnomaly).filter(
                    LocationSecurityAnomaly.resolved_at.is_(None)
                ).count()
                
                # Get consent statistics
                total_consents = session.query(LocationPrivacyConsent).count()
                active_consents = session.query(LocationPrivacyConsent).filter(
                    LocationPrivacyConsent.consent_given == True,
                    LocationPrivacyConsent.withdrawn_at.is_(None)
                ).count()
                
                # Get retention statistics
                expired_records = session.query(LocationDataRetention).filter(
                    LocationDataRetention.retention_expires_at < datetime.utcnow(),
                    LocationDataRetention.deleted_at.is_(None)
                ).count()
                
                return {
                    'access_logs': {
                        'total': total_access_logs,
                        'failed': failed_access_logs,
                        'success_rate': (total_access_logs - failed_access_logs) / total_access_logs if total_access_logs > 0 else 0
                    },
                    'anomalies': {
                        'total': total_anomalies,
                        'unresolved': unresolved_anomalies
                    },
                    'consents': {
                        'total': total_consents,
                        'active': active_consents
                    },
                    'data_retention': {
                        'expired_records': expired_records
                    },
                    'timestamp': datetime.utcnow().isoformat()
                }
                
            finally:
                session.close()
                
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting security statistics: {e}")
            return {}


# Initialize database service
def get_security_database_service() -> LocationSecurityDatabaseService:
    """Get security database service instance."""
    database_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/location_validation")
    return LocationSecurityDatabaseService(database_url)
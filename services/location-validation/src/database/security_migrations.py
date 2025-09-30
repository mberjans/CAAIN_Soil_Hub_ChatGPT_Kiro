"""
Security Database Migrations
CAAIN Soil Hub - Location Validation Service

Database migration scripts for location security and privacy features.
"""

import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import os
from datetime import datetime, timedelta

from ..models.security_models import Base

logger = logging.getLogger(__name__)


class SecurityDatabaseManager:
    """Manager for security database operations and migrations."""
    
    def __init__(self, database_url: str):
        """Initialize database manager."""
        self.database_url = database_url
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.logger = logging.getLogger(__name__)
    
    def create_security_tables(self) -> bool:
        """Create all security-related tables."""
        try:
            # Create all tables defined in security_models
            Base.metadata.create_all(bind=self.engine)
            
            self.logger.info("Security tables created successfully")
            return True
            
        except SQLAlchemyError as e:
            self.logger.error(f"Error creating security tables: {e}")
            return False
    
    def drop_security_tables(self) -> bool:
        """Drop all security-related tables."""
        try:
            Base.metadata.drop_all(bind=self.engine)
            
            self.logger.info("Security tables dropped successfully")
            return True
            
        except SQLAlchemyError as e:
            self.logger.error(f"Error dropping security tables: {e}")
            return False
    
    def initialize_security_data(self) -> bool:
        """Initialize default security configuration and policies."""
        try:
            session = self.SessionLocal()
            
            try:
                # Insert default security policies
                self._insert_default_security_policies(session)
                
                # Insert default security configuration
                self._insert_default_security_config(session)
                
                # Insert default encryption keys
                self._insert_default_encryption_keys(session)
                
                session.commit()
                self.logger.info("Default security data initialized successfully")
                return True
                
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()
                
        except SQLAlchemyError as e:
            self.logger.error(f"Error initializing security data: {e}")
            return False
    
    def _insert_default_security_policies(self, session):
        """Insert default security policies."""
        from ..models.security_models import LocationSecurityPolicy
        
        default_policies = [
            {
                'policy_name': 'public_location_data',
                'security_level': 'public',
                'encryption_required': False,
                'anonymization_level': 'low',
                'retention_days': 1825,  # 5 years
                'access_control_rules': {
                    'farmer': ['read', 'write', 'delete'],
                    'consultant': ['read'],
                    'admin': ['read', 'write', 'delete']
                }
            },
            {
                'policy_name': 'internal_location_data',
                'security_level': 'internal',
                'encryption_required': False,
                'anonymization_level': 'low',
                'retention_days': 1095,  # 3 years
                'access_control_rules': {
                    'farmer': ['read', 'write', 'delete'],
                    'consultant': ['read'],
                    'admin': ['read', 'write', 'delete']
                }
            },
            {
                'policy_name': 'sensitive_location_data',
                'security_level': 'sensitive',
                'encryption_required': True,
                'anonymization_level': 'medium',
                'retention_days': 730,  # 2 years
                'access_control_rules': {
                    'farmer': ['read', 'write', 'delete'],
                    'consultant': ['read'],  # With consent
                    'admin': ['read', 'write', 'delete']
                }
            },
            {
                'policy_name': 'highly_sensitive_location_data',
                'security_level': 'highly_sensitive',
                'encryption_required': True,
                'anonymization_level': 'high',
                'retention_days': 365,  # 1 year
                'access_control_rules': {
                    'farmer': ['read', 'write', 'delete'],
                    'consultant': [],  # No access without explicit consent
                    'admin': ['read', 'write', 'delete']
                }
            }
        ]
        
        for policy_data in default_policies:
            # Check if policy already exists
            existing = session.query(LocationSecurityPolicy).filter_by(
                policy_name=policy_data['policy_name']
            ).first()
            
            if not existing:
                policy = LocationSecurityPolicy(**policy_data)
                session.add(policy)
    
    def _insert_default_security_config(self, session):
        """Insert default security configuration."""
        from ..models.security_models import LocationSecurityConfiguration
        
        default_config = [
            {
                'config_key': 'encryption_algorithm',
                'config_value': 'AES-256-GCM',
                'config_type': 'string',
                'description': 'Encryption algorithm for location data',
                'is_sensitive': False
            },
            {
                'config_key': 'key_rotation_days',
                'config_value': '90',
                'config_type': 'integer',
                'description': 'Days between encryption key rotations',
                'is_sensitive': False
            },
            {
                'config_key': 'failed_access_threshold',
                'config_value': '5',
                'config_type': 'integer',
                'description': 'Number of failed access attempts before alert',
                'is_sensitive': False
            },
            {
                'config_key': 'audit_log_retention_days',
                'config_value': '2555',  # 7 years
                'config_type': 'integer',
                'description': 'Days to retain audit logs',
                'is_sensitive': False
            },
            {
                'config_key': 'anonymization_precision',
                'config_value': '{"low": 0.01, "medium": 0.1, "high": 1.0, "maximum": 10.0}',
                'config_type': 'json',
                'description': 'Coordinate anonymization precision levels',
                'is_sensitive': False
            },
            {
                'config_key': 'gdpr_compliance_enabled',
                'config_value': 'true',
                'config_type': 'boolean',
                'description': 'Enable GDPR compliance features',
                'is_sensitive': False
            },
            {
                'config_key': 'data_export_expiry_days',
                'config_value': '30',
                'config_type': 'integer',
                'description': 'Days before exported data files expire',
                'is_sensitive': False
            },
            {
                'config_key': 'security_monitoring_enabled',
                'config_value': 'true',
                'config_type': 'boolean',
                'description': 'Enable security anomaly monitoring',
                'is_sensitive': False
            }
        ]
        
        for config_data in default_config:
            # Check if config already exists
            existing = session.query(LocationSecurityConfiguration).filter_by(
                config_key=config_data['config_key']
            ).first()
            
            if not existing:
                config = LocationSecurityConfiguration(**config_data)
                session.add(config)
    
    def _insert_default_encryption_keys(self, session):
        """Insert default encryption keys (placeholder)."""
        from ..models.security_models import LocationEncryptionKey
        
        # Note: In production, actual encryption keys would be generated securely
        # This is just a placeholder structure
        default_keys = [
            {
                'key_name': 'sensitive_location_key_v1',
                'security_level': 'sensitive',
                'key_version': 'sensitive_v1_20241201',
                'encrypted_key': 'PLACEHOLDER_ENCRYPTED_KEY_SENSITIVE',
                'key_hash': 'placeholder_hash_sensitive',
                'is_active': True,
                'expires_at': datetime.utcnow() + timedelta(days=90)
            },
            {
                'key_name': 'highly_sensitive_location_key_v1',
                'security_level': 'highly_sensitive',
                'key_version': 'highly_sensitive_v1_20241201',
                'encrypted_key': 'PLACEHOLDER_ENCRYPTED_KEY_HIGHLY_SENSITIVE',
                'key_hash': 'placeholder_hash_highly_sensitive',
                'is_active': True,
                'expires_at': datetime.utcnow() + timedelta(days=90)
            }
        ]
        
        for key_data in default_keys:
            # Check if key already exists
            existing = session.query(LocationEncryptionKey).filter_by(
                key_name=key_data['key_name']
            ).first()
            
            if not existing:
                key = LocationEncryptionKey(**key_data)
                session.add(key)
    
    def run_migration(self, migration_name: str) -> bool:
        """Run a specific migration."""
        try:
            if migration_name == "create_security_tables":
                return self.create_security_tables()
            elif migration_name == "initialize_security_data":
                return self.initialize_security_data()
            elif migration_name == "drop_security_tables":
                return self.drop_security_tables()
            else:
                self.logger.error(f"Unknown migration: {migration_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Migration {migration_name} failed: {e}")
            return False
    
    def check_security_tables_exist(self) -> bool:
        """Check if security tables exist."""
        try:
            session = self.SessionLocal()
            
            # Check if any security tables exist
            result = session.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN (
                    'location_security_policies',
                    'location_access_logs',
                    'location_encryption_keys',
                    'location_privacy_consents',
                    'location_data_retention',
                    'location_security_anomalies',
                    'location_data_exports',
                    'location_sharing_permissions',
                    'location_security_configuration'
                )
            """))
            
            count = result.scalar()
            session.close()
            
            return count > 0
            
        except SQLAlchemyError as e:
            self.logger.error(f"Error checking security tables: {e}")
            return False


def run_security_migrations(database_url: str) -> bool:
    """Run all security migrations."""
    try:
        db_manager = SecurityDatabaseManager(database_url)
        
        # Check if tables already exist
        if db_manager.check_security_tables_exist():
            logger.info("Security tables already exist, skipping creation")
        else:
            # Create security tables
            if not db_manager.create_security_tables():
                logger.error("Failed to create security tables")
                return False
            
            logger.info("Security tables created successfully")
        
        # Initialize default data
        if not db_manager.initialize_security_data():
            logger.error("Failed to initialize security data")
            return False
        
        logger.info("Security migrations completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Security migrations failed: {e}")
        return False


if __name__ == "__main__":
    # Example usage
    database_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/location_validation")
    
    if run_security_migrations(database_url):
        print("Security migrations completed successfully")
    else:
        print("Security migrations failed")
        exit(1)
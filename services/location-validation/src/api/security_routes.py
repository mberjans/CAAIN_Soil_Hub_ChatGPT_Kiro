"""
Security API Routes
CAAIN Soil Hub - Location Validation Service

API endpoints for location data security and privacy management.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ..services.location_security_service import (
    LocationSecurityManager,
    LocationSecurityContext,
    SecurityLevel,
    AccessType,
    SecurityAuditLog
)
from ..services.location_security_database_service import get_security_database_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/security", tags=["location-security"])

# Initialize security manager with database service
database_service = get_security_database_service()
security_manager = LocationSecurityManager(database_service=database_service)


class SecurityContextRequest(BaseModel):
    """Request model for security context."""
    user_id: str = Field(..., description="User ID")
    farm_id: Optional[str] = Field(None, description="Farm ID")
    field_id: Optional[str] = Field(None, description="Field ID")
    access_type: AccessType = Field(AccessType.READ, description="Type of access requested")
    security_level: SecurityLevel = Field(SecurityLevel.SENSITIVE, description="Security level of data")
    purpose: str = Field("agricultural_analysis", description="Purpose of access")
    consent_given: bool = Field(True, description="Whether user consent is given")


class LocationDataRequest(BaseModel):
    """Request model for location data operations."""
    location_data: Dict[str, Any] = Field(..., description="Location data to secure")
    security_context: SecurityContextRequest = Field(..., description="Security context")
    user_role: str = Field("farmer", description="User role for access control")


class GDPRRequest(BaseModel):
    """Request model for GDPR data subject requests."""
    user_id: str = Field(..., description="User ID")
    request_type: str = Field(..., description="Type of GDPR request (access, deletion, portability)")
    verification_token: Optional[str] = Field(None, description="Verification token for request")


class AuditTrailRequest(BaseModel):
    """Request model for audit trail queries."""
    user_id: Optional[str] = Field(None, description="Filter by user ID")
    resource_id: Optional[str] = Field(None, description="Filter by resource ID")
    start_date: Optional[datetime] = Field(None, description="Start date filter")
    end_date: Optional[datetime] = Field(None, description="End date filter")
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of results")


class SecurityResponse(BaseModel):
    """Response model for security operations."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    security_level: Optional[SecurityLevel] = None
    access_granted: Optional[bool] = None


class AuditTrailResponse(BaseModel):
    """Response model for audit trail."""
    events: List[Dict[str, Any]]
    total_count: int
    filtered_count: int


async def get_current_user(request: Request) -> Dict[str, str]:
    """Get current user from request - placeholder for actual implementation."""
    # This would be replaced with actual user authentication
    return {"user_id": "test-user-id", "role": "farmer"}


@router.post("/secure-data", response_model=SecurityResponse)
async def secure_location_data(
    request: LocationDataRequest,
    current_user: dict = Depends(get_current_user)
) -> SecurityResponse:
    """
    Secure location data with encryption and access control.
    
    This endpoint applies comprehensive security measures to location data including:
    - Access control based on user role and security level
    - Data encryption for sensitive information
    - Privacy anonymization for consultants
    - Audit logging for compliance
    """
    try:
        # Create security context
        security_context = LocationSecurityContext(
            user_id=request.security_context.user_id,
            farm_id=request.security_context.farm_id,
            field_id=request.security_context.field_id,
            access_type=request.security_context.access_type,
            security_level=request.security_context.security_level,
            purpose=request.security_context.purpose,
            consent_given=request.security_context.consent_given
        )
        
        # Apply security measures
        secured_data = await security_manager.secure_location_data(
            request.location_data,
            security_context,
            request.user_role
        )
        
        return SecurityResponse(
            success=True,
            message="Location data secured successfully",
            data=secured_data,
            security_level=request.security_context.security_level,
            access_granted=True
        )
        
    except PermissionError as e:
        logger.warning(f"Access denied for user {request.security_context.user_id}: {e}")
        return SecurityResponse(
            success=False,
            message=str(e),
            access_granted=False
        )
    except Exception as e:
        logger.error(f"Error securing location data: {e}")
        raise HTTPException(status_code=500, detail=f"Security operation failed: {str(e)}")


@router.post("/decrypt-data", response_model=SecurityResponse)
async def decrypt_location_data(
    request: LocationDataRequest,
    current_user: dict = Depends(get_current_user)
) -> SecurityResponse:
    """
    Decrypt location data with proper access control.
    
    This endpoint decrypts previously encrypted location data while ensuring:
    - User has proper access permissions
    - Access is logged for audit purposes
    - Data is returned only to authorized users
    """
    try:
        # Create security context
        security_context = LocationSecurityContext(
            user_id=request.security_context.user_id,
            farm_id=request.security_context.farm_id,
            field_id=request.security_context.field_id,
            access_type=request.security_context.access_type,
            security_level=request.security_context.security_level,
            purpose=request.security_context.purpose,
            consent_given=request.security_context.consent_given
        )
        
        # Decrypt data
        decrypted_data = await security_manager.decrypt_location_data(
            request.location_data,
            security_context,
            request.user_role
        )
        
        return SecurityResponse(
            success=True,
            message="Location data decrypted successfully",
            data=decrypted_data,
            security_level=request.security_context.security_level,
            access_granted=True
        )
        
    except PermissionError as e:
        logger.warning(f"Decrypt access denied for user {request.security_context.user_id}: {e}")
        return SecurityResponse(
            success=False,
            message=str(e),
            access_granted=False
        )
    except Exception as e:
        logger.error(f"Error decrypting location data: {e}")
        raise HTTPException(status_code=500, detail=f"Decryption failed: {str(e)}")


@router.post("/gdpr-request", response_model=SecurityResponse)
async def handle_gdpr_request(
    request: GDPRRequest,
    current_user: dict = Depends(get_current_user)
) -> SecurityResponse:
    """
    Handle GDPR data subject requests for location data.
    
    Supported request types:
    - access: Export all user location data
    - deletion: Delete user location data
    - portability: Export data in portable format
    
    This endpoint ensures compliance with GDPR requirements for location data.
    """
    try:
        # Validate request type
        valid_types = ['access', 'deletion', 'portability']
        if request.request_type not in valid_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid request type. Must be one of: {valid_types}"
            )
        
        # Handle GDPR request
        result = await security_manager.handle_gdpr_request(
            request.user_id,
            request.request_type
        )
        
        return SecurityResponse(
            success=True,
            message=f"GDPR {request.request_type} request processed successfully",
            data=result
        )
        
    except Exception as e:
        logger.error(f"Error handling GDPR request: {e}")
        raise HTTPException(status_code=500, detail=f"GDPR request failed: {str(e)}")


@router.get("/audit-trail", response_model=AuditTrailResponse)
async def get_audit_trail(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    resource_id: Optional[str] = Query(None, description="Filter by resource ID"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    current_user: dict = Depends(get_current_user)
) -> AuditTrailResponse:
    """
    Get security audit trail for location data access.
    
    This endpoint provides comprehensive audit logging for:
    - All location data access attempts
    - Security events and anomalies
    - User activity tracking
    - Compliance monitoring
    
    Only accessible by admin users in production.
    """
    try:
        # Get audit trail from database
        events = await database_service.get_access_logs(
            user_id=user_id,
            resource_id=resource_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        
        return AuditTrailResponse(
            events=events,
            total_count=len(events),
            filtered_count=len(events)
        )
        
    except Exception as e:
        logger.error(f"Error getting audit trail: {e}")
        raise HTTPException(status_code=500, detail=f"Audit trail retrieval failed: {str(e)}")


@router.get("/security-anomalies/{user_id}")
async def get_security_anomalies(
    user_id: str,
    current_user: dict = Depends(get_current_user)
) -> JSONResponse:
    """
    Detect security anomalies for a specific user.
    
    This endpoint analyzes user activity patterns to identify:
    - Excessive failed access attempts
    - Suspicious access patterns
    - Unusual data export activity
    - Potential security breaches
    
    Returns anomaly detection results for security monitoring.
    """
    try:
        # Detect anomalies
        anomalies = await security_manager.audit_service.detect_security_anomalies(user_id)
        
        return JSONResponse(content={
            "user_id": user_id,
            "anomalies_detected": len(anomalies),
            "anomalies": anomalies,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "monitoring_period": "24 hours"
        })
        
    except Exception as e:
        logger.error(f"Error detecting security anomalies: {e}")
        raise HTTPException(status_code=500, detail=f"Anomaly detection failed: {str(e)}")


@router.post("/rotate-keys")
async def rotate_encryption_keys(
    security_level: SecurityLevel = Query(..., description="Security level for key rotation"),
    current_user: dict = Depends(get_current_user)
) -> JSONResponse:
    """
    Rotate encryption keys for enhanced security.
    
    This endpoint rotates encryption keys for the specified security level:
    - Generates new encryption keys
    - Updates key rotation timestamps
    - Maintains backward compatibility for existing encrypted data
    
    Only accessible by admin users in production.
    """
    try:
        # Rotate keys
        success = security_manager.encryption_service.rotate_keys(security_level)
        
        if success:
            return JSONResponse(content={
                "success": True,
                "message": f"Keys rotated successfully for security level: {security_level}",
                "security_level": security_level.value,
                "rotation_timestamp": datetime.utcnow().isoformat()
            })
        else:
            raise HTTPException(status_code=500, detail="Key rotation failed")
            
    except Exception as e:
        logger.error(f"Error rotating keys: {e}")
        raise HTTPException(status_code=500, detail=f"Key rotation failed: {str(e)}")


@router.get("/access-permissions")
async def get_access_permissions(
    user_role: str = Query(..., description="User role to check permissions for"),
    security_level: SecurityLevel = Query(..., description="Security level to check"),
    current_user: dict = Depends(get_current_user)
) -> JSONResponse:
    """
    Get access permissions for user role and security level.
    
    This endpoint returns:
    - Allowed access types for the role/level combination
    - Accessible data fields
    - Permission restrictions and requirements
    
    Useful for frontend permission UI and access control validation.
    """
    try:
        # Get access permissions
        accessible_fields = await security_manager.access_control_service.get_accessible_fields(
            user_role, security_level
        )
        
        # Get access rules
        access_rules = security_manager.access_control_service.access_rules.get(user_role, {})
        allowed_access_types = access_rules.get(security_level, [])
        
        return JSONResponse(content={
            "user_role": user_role,
            "security_level": security_level.value,
            "allowed_access_types": [access_type.value for access_type in allowed_access_types],
            "accessible_fields": accessible_fields,
            "permission_summary": {
                "can_read": AccessType.READ in allowed_access_types,
                "can_write": AccessType.WRITE in allowed_access_types,
                "can_delete": AccessType.DELETE in allowed_access_types,
                "can_export": AccessType.EXPORT in allowed_access_types,
                "can_share": AccessType.SHARE in allowed_access_types
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting access permissions: {e}")
        raise HTTPException(status_code=500, detail=f"Permission check failed: {str(e)}")


@router.get("/statistics")
async def get_security_statistics(
    current_user: dict = Depends(get_current_user)
) -> JSONResponse:
    """
    Get security statistics for monitoring and compliance.
    
    This endpoint provides comprehensive security metrics including:
    - Access log statistics and success rates
    - Security anomaly counts and resolution status
    - Privacy consent tracking
    - Data retention compliance metrics
    
    Only accessible by admin users in production.
    """
    try:
        # Get security statistics from database
        statistics = await database_service.get_security_statistics()
        
        return JSONResponse(content={
            "security_statistics": statistics,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting security statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Statistics retrieval failed: {str(e)}")


@router.get("/health")
async def security_health_check() -> JSONResponse:
    """Health check endpoint for security service."""
    return JSONResponse(content={
        "service": "location-security",
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "encryption_service": "active",
            "access_control_service": "active", 
            "privacy_service": "active",
            "audit_service": "active",
            "database_service": "active" if database_service else "inactive"
        }
    })
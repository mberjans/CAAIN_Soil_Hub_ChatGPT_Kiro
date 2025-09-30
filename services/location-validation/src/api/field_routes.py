"""
Field Management API Routes
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

FastAPI routes for comprehensive field management endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Path, status
from typing import Dict, Any, List, Optional
import logging
import sys
import os
from uuid import UUID
from datetime import datetime

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../databases/python'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../services'))

from field_management_service import (
    FieldManagementService,
    FieldCreateRequest,
    FieldUpdateRequest,
    FieldResponse,
    FieldListResponse,
    FieldValidationResult,
    FieldBoundary,
    FieldCharacteristics
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/fields", tags=["field-management"])

# Service instance
field_service = FieldManagementService()


# Dependency injection for database session (placeholder)
async def get_db_session():
    """Get database session - placeholder for actual implementation."""
    # This would be replaced with actual database session management
    return None


async def get_current_user():
    """Get current user - placeholder for actual implementation."""
    # This would be replaced with actual user authentication
    return {"user_id": "test-user-id"}


@router.post("/", response_model=FieldResponse, status_code=status.HTTP_201_CREATED)
async def create_field(
    request: FieldCreateRequest,
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_db_session)
) -> FieldResponse:
    """
    Create a new field with comprehensive validation and agricultural context.
    
    This endpoint creates a new field with:
    - Comprehensive field validation (boundary, characteristics, agricultural suitability)
    - Agricultural context integration (soil suitability, crop recommendations)
    - Management complexity assessment
    - Integration with existing farm location data
    
    Args:
        request: FieldCreateRequest with field details
        current_user: Current authenticated user
        db_session: Database session
        
    Returns:
        FieldResponse with created field data including agricultural context
        
    Raises:
        HTTPException: If validation fails or creation error occurs
    """
    try:
        logger.info(f"Creating field: {request.field_name} for location: {request.location_id}")
        
        # Validate location ID format
        try:
            UUID(request.location_id)
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": {
                        "error_code": "INVALID_LOCATION_ID",
                        "error_message": "Invalid location ID format",
                        "agricultural_context": "Location ID must be a valid UUID",
                        "suggested_actions": [
                            "Verify location ID is correct",
                            "Use location list to find valid IDs",
                            "Contact support if ID appears correct"
                        ]
                    }
                }
            )
        
        # Create field
        result = await field_service.create_field(request, db_session)
        
        logger.info(f"Field created successfully: {result.id}")
        
        return result
        
    except ValueError as e:
        logger.error(f"Field creation validation error: {e}")
        raise HTTPException(
            status_code=422,
            detail={
                "error": {
                    "error_code": "FIELD_VALIDATION_FAILED",
                    "error_message": f"Field validation failed: {str(e)}",
                    "agricultural_context": "Field data must meet agricultural standards and validation requirements",
                    "suggested_actions": [
                        "Verify field boundary coordinates",
                        "Check soil type and characteristics",
                        "Ensure field size is accurate",
                        "Review agricultural constraints"
                    ]
                }
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error creating field: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "error_code": "FIELD_CREATION_ERROR",
                    "error_message": "Internal error creating field",
                    "agricultural_context": "Unable to create field for agricultural management",
                    "suggested_actions": [
                        "Try again in a few moments",
                        "Contact support if the problem persists",
                        "Verify all required information is provided"
                    ]
                }
            }
        )


@router.get("/", response_model=FieldListResponse)
async def list_fields(
    location_id: Optional[str] = Query(None, description="Filter by location ID"),
    field_type: Optional[str] = Query(None, description="Filter by field type (crop, pasture, other)"),
    soil_type: Optional[str] = Query(None, description="Filter by soil type"),
    size_min: Optional[float] = Query(None, ge=0, description="Minimum field size in acres"),
    size_max: Optional[float] = Query(None, ge=0, description="Maximum field size in acres"),
    irrigation_available: Optional[bool] = Query(None, description="Filter by irrigation availability"),
    sort_by: str = Query("field_name", description="Sort field (field_name, size_acres, created_at)"),
    sort_order: str = Query("asc", description="Sort order (asc, desc)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_db_session)
) -> FieldListResponse:
    """
    List fields with advanced filtering, sorting, and agricultural context.
    
    This endpoint provides:
    - Advanced filtering by field characteristics
    - Sorting options with agricultural relevance
    - Pagination for large field lists
    - Agricultural context integration
    - Soil suitability and crop recommendations
    
    Args:
        location_id: Filter by location ID
        field_type: Filter by field type
        soil_type: Filter by soil type
        size_min: Minimum field size in acres
        size_max: Maximum field size in acres
        irrigation_available: Filter by irrigation availability
        sort_by: Sort field
        sort_order: Sort order
        page: Page number
        page_size: Items per page
        current_user: Current authenticated user
        db_session: Database session
        
    Returns:
        FieldListResponse with paginated field data and agricultural context
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        logger.info(f"Listing fields with filters: location_id={location_id}, field_type={field_type}, page={page}")
        
        # Validate sort parameters
        valid_sort_fields = ["field_name", "size_acres", "created_at", "updated_at", "field_type"]
        if sort_by not in valid_sort_fields:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": {
                        "error_code": "INVALID_SORT_FIELD",
                        "error_message": f"Invalid sort field: {sort_by}",
                        "valid_fields": valid_sort_fields,
                        "agricultural_context": "Sort fields help organize fields for agricultural management",
                        "suggested_actions": [
                            "Use a valid sort field",
                            "Check available sort options",
                            "Use field_name for alphabetical sorting"
                        ]
                    }
                }
            )
        
        if sort_order not in ["asc", "desc"]:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": {
                        "error_code": "INVALID_SORT_ORDER",
                        "error_message": f"Invalid sort order: {sort_order}",
                        "valid_orders": ["asc", "desc"],
                        "agricultural_context": "Sort order helps organize fields for management planning",
                        "suggested_actions": [
                            "Use 'asc' for ascending order",
                            "Use 'desc' for descending order"
                        ]
                    }
                }
            )
        
        # List fields
        result = await field_service.list_fields(
            location_id=location_id,
            field_type=field_type,
            soil_type=soil_type,
            size_min=size_min,
            size_max=size_max,
            irrigation_available=irrigation_available,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size,
            db_session=db_session
        )
        
        logger.info(f"Retrieved {len(result.fields)} fields (page {page} of {(result.total_count + page_size - 1) // page_size})")
        
        return result
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Unexpected error listing fields: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "error_code": "FIELD_LISTING_ERROR",
                    "error_message": "Internal error listing fields",
                    "agricultural_context": "Unable to retrieve fields for agricultural management",
                    "suggested_actions": [
                        "Try again in a few moments",
                        "Contact support if the problem persists",
                        "Check your internet connection"
                    ]
                }
            }
        )


@router.get("/{field_id}", response_model=FieldResponse)
async def get_field(
    field_id: str = Path(..., description="Field ID"),
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_db_session)
) -> FieldResponse:
    """
    Get detailed field information with agricultural context.
    
    This endpoint provides:
    - Complete field details including boundary and characteristics
    - Agricultural context and soil suitability assessment
    - Crop recommendations based on field characteristics
    - Management complexity assessment
    - Historical data integration
    
    Args:
        field_id: Field ID
        current_user: Current authenticated user
        db_session: Database session
        
    Returns:
        FieldResponse with detailed field data and agricultural context
        
    Raises:
        HTTPException: If field not found or retrieval fails
    """
    try:
        # Validate field ID format
        try:
            UUID(field_id)
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": {
                        "error_code": "INVALID_FIELD_ID",
                        "error_message": "Invalid field ID format",
                        "agricultural_context": "Field ID must be a valid UUID",
                        "suggested_actions": [
                            "Verify field ID is correct",
                            "Use field list to find valid IDs",
                            "Contact support if ID appears correct"
                        ]
                    }
                }
            )
        
        logger.info(f"Retrieving field: {field_id}")
        
        field = await field_service.get_field(field_id, db_session)
        
        if not field:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": {
                        "error_code": "FIELD_NOT_FOUND",
                        "error_message": f"Field {field_id} not found",
                        "agricultural_context": "Field may have been deleted or access restricted",
                        "suggested_actions": [
                            "Verify field ID is correct",
                            "Check field list for available fields",
                            "Contact support if field should exist"
                        ]
                    }
                }
            )
        
        logger.info(f"Field retrieved successfully: {field.field_name}")
        
        return field
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Unexpected error getting field {field_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "error_code": "FIELD_RETRIEVAL_ERROR",
                    "error_message": "Internal error retrieving field",
                    "agricultural_context": "Unable to retrieve field data for agricultural management",
                    "suggested_actions": [
                        "Try again in a few moments",
                        "Contact support if the problem persists",
                        "Check your internet connection"
                    ]
                }
            }
        )


@router.put("/{field_id}", response_model=FieldResponse)
async def update_field(
    field_id: str = Path(..., description="Field ID to update"),
    request: FieldUpdateRequest = None,
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_db_session)
) -> FieldResponse:
    """
    Update field with change tracking and agricultural context refresh.
    
    This endpoint provides:
    - Partial updates with validation
    - Change tracking and history
    - Agricultural context updates
    - Dependent service notifications
    - Optimization recommendations
    
    Args:
        field_id: Field ID to update
        request: FieldUpdateRequest with update data
        current_user: Current authenticated user
        db_session: Database session
        
    Returns:
        FieldResponse with updated field data and refreshed agricultural context
        
    Raises:
        HTTPException: If update fails or field not found
    """
    try:
        # Validate field ID format
        try:
            UUID(field_id)
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": {
                        "error_code": "INVALID_FIELD_ID",
                        "error_message": "Invalid field ID format",
                        "agricultural_context": "Field ID must be a valid UUID",
                        "suggested_actions": [
                            "Verify field ID is correct",
                            "Use field list to find valid IDs",
                            "Contact support if ID appears correct"
                        ]
                    }
                }
            )
        
        logger.info(f"Updating field: {field_id}")
        
        updated_field = await field_service.update_field(field_id, request, db_session)
        
        if not updated_field:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": {
                        "error_code": "FIELD_NOT_FOUND",
                        "error_message": f"Field {field_id} not found",
                        "agricultural_context": "Field may have been deleted or access restricted",
                        "suggested_actions": [
                            "Verify field ID is correct",
                            "Check field list for available fields",
                            "Contact support if field should exist"
                        ]
                    }
                }
            )
        
        logger.info(f"Field updated successfully: {field_id}")
        
        return updated_field
        
    except ValueError as e:
        logger.error(f"Field update validation error: {e}")
        raise HTTPException(
            status_code=422,
            detail={
                "error": {
                    "error_code": "FIELD_UPDATE_VALIDATION_FAILED",
                    "error_message": f"Field update validation failed: {str(e)}",
                    "agricultural_context": "Updated field data must meet agricultural standards",
                    "suggested_actions": [
                        "Verify updated field characteristics",
                        "Check boundary coordinates if updated",
                        "Ensure agricultural constraints are met",
                        "Review validation error details"
                    ]
                }
            }
        )
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Unexpected error updating field {field_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "error_code": "FIELD_UPDATE_ERROR",
                    "error_message": "Internal error updating field",
                    "agricultural_context": "Unable to update field data for agricultural management",
                    "suggested_actions": [
                        "Try again in a few moments",
                        "Contact support if the problem persists",
                        "Verify all update data is valid"
                    ]
                }
            }
        )


@router.delete("/{field_id}")
async def delete_field(
    field_id: str = Path(..., description="Field ID to delete"),
    hard_delete: bool = Query(False, description="Perform hard delete (permanent removal)"),
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Delete field with dependency checking and agricultural impact assessment.
    
    This endpoint provides:
    - Dependency checking for related agricultural data
    - Soft delete option (mark as inactive)
    - Hard delete with data cleanup
    - Cascade handling for dependent services
    - Agricultural impact assessment
    
    Args:
        field_id: Field ID to delete
        hard_delete: Whether to perform permanent deletion
        current_user: Current authenticated user
        db_session: Database session
        
    Returns:
        Dict with deletion confirmation and affected services
        
    Raises:
        HTTPException: If deletion fails or dependencies exist
    """
    try:
        # Validate field ID format
        try:
            UUID(field_id)
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": {
                        "error_code": "INVALID_FIELD_ID",
                        "error_message": "Invalid field ID format",
                        "agricultural_context": "Field ID must be a valid UUID",
                        "suggested_actions": [
                            "Verify field ID is correct",
                            "Use field list to find valid IDs",
                            "Contact support if ID appears correct"
                        ]
                    }
                }
            )
        
        logger.info(f"Deleting field: {field_id} (hard_delete: {hard_delete})")
        
        result = await field_service.delete_field(field_id, hard_delete, db_session)
        
        if not result["success"]:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": {
                        "error_code": "FIELD_NOT_FOUND",
                        "error_message": result["message"],
                        "agricultural_context": "Field may have been deleted or access restricted",
                        "suggested_actions": [
                            "Verify field ID is correct",
                            "Check field list for available fields",
                            "Contact support if field should exist"
                        ]
                    }
                }
            )
        
        logger.info(f"Field deletion completed: {result['deletion_type']}")
        
        return result
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Unexpected error deleting field {field_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "error_code": "FIELD_DELETION_ERROR",
                    "error_message": "Internal error deleting field",
                    "agricultural_context": "Unable to delete field from agricultural management system",
                    "suggested_actions": [
                        "Try again in a few moments",
                        "Contact support if the problem persists",
                        "Consider soft delete if dependencies exist"
                    ]
                }
            }
        )


@router.post("/validate", response_model=FieldValidationResult)
async def validate_field_data(
    request: FieldCreateRequest,
    current_user: dict = Depends(get_current_user)
) -> FieldValidationResult:
    """
    Comprehensive field validation without creating the field.
    
    This endpoint provides:
    - Real-time validation of field data
    - Agricultural context validation
    - Boundary accuracy assessment
    - Soil suitability analysis
    - Management complexity assessment
    - Optimization recommendations
    
    Args:
        request: FieldCreateRequest with field data to validate
        current_user: Current authenticated user
        
    Returns:
        FieldValidationResult with comprehensive validation details
        
    Raises:
        HTTPException: If validation fails
    """
    try:
        logger.info(f"Validating field data: {request.field_name}")
        
        validation_result = await field_service.validate_field_data(request)
        
        logger.info(f"Field validation completed: valid={validation_result.valid}, errors={len(validation_result.errors)}, warnings={len(validation_result.warnings)}")
        
        return validation_result
        
    except Exception as e:
        logger.error(f"Unexpected error validating field data: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "error_code": "FIELD_VALIDATION_ERROR",
                    "error_message": "Internal error validating field data",
                    "agricultural_context": "Unable to validate field data for agricultural suitability",
                    "suggested_actions": [
                        "Try again in a few moments",
                        "Contact support if the problem persists",
                        "Verify all field data is correct"
                    ]
                }
            }
        )


@router.get("/{field_id}/agricultural-context")
async def get_field_agricultural_context(
    field_id: str = Path(..., description="Field ID"),
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Get detailed agricultural context for a field.
    
    This endpoint provides:
    - Soil suitability analysis
    - Crop recommendations
    - Management complexity assessment
    - Climate zone integration
    - Agricultural optimization recommendations
    
    Args:
        field_id: Field ID
        current_user: Current authenticated user
        db_session: Database session
        
    Returns:
        Dict with comprehensive agricultural context
        
    Raises:
        HTTPException: If field not found or context generation fails
    """
    try:
        # Validate field ID format
        try:
            UUID(field_id)
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": {
                        "error_code": "INVALID_FIELD_ID",
                        "error_message": "Invalid field ID format",
                        "agricultural_context": "Field ID must be a valid UUID",
                        "suggested_actions": [
                            "Verify field ID is correct",
                            "Use field list to find valid IDs",
                            "Contact support if ID appears correct"
                        ]
                    }
                }
            )
        
        logger.info(f"Getting agricultural context for field: {field_id}")
        
        field = await field_service.get_field(field_id, db_session)
        
        if not field:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": {
                        "error_code": "FIELD_NOT_FOUND",
                        "error_message": f"Field {field_id} not found",
                        "agricultural_context": "Field may have been deleted or access restricted",
                        "suggested_actions": [
                            "Verify field ID is correct",
                            "Check field list for available fields",
                            "Contact support if field should exist"
                        ]
                    }
                }
            )
        
        # Extract agricultural context
        agricultural_context = {
            "field_id": field.id,
            "field_name": field.field_name,
            "agricultural_context": field.agricultural_context,
            "soil_suitability": field.soil_suitability,
            "crop_recommendations": field.crop_recommendations,
            "management_complexity": field.management_complexity,
            "validation_summary": {
                "soil_quality": field.soil_suitability.get("fertility", "unknown") if field.soil_suitability else "unknown",
                "drainage_assessment": field.soil_suitability.get("drainage", "unknown") if field.soil_suitability else "unknown",
                "recommended_crops": field.crop_recommendations or [],
                "management_difficulty": field.management_complexity or "unknown"
            }
        }
        
        logger.info(f"Agricultural context retrieved for field: {field.field_name}")
        
        return agricultural_context
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Unexpected error getting agricultural context for field {field_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "error_code": "AGRICULTURAL_CONTEXT_ERROR",
                    "error_message": "Internal error retrieving agricultural context",
                    "agricultural_context": "Unable to generate agricultural context for field management",
                    "suggested_actions": [
                        "Try again in a few moments",
                        "Contact support if the problem persists",
                        "Verify field data is complete"
                    ]
                }
            }
        )


# Health check endpoint
@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for the field management service.
    
    Returns:
        Dict with service status and basic information
    """
    try:
        # Test basic service functionality
        test_request = FieldCreateRequest(
            location_id="test-location-id",
            field_name="Test Field",
            field_type="crop",
            size_acres=10.0
        )
        
        # This would test actual service functionality in production
        return {
            "status": "healthy",
            "service": "field-management",
            "version": "1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "test_validation": {
                "field_request_tested": test_request.field_name,
                "validation_successful": True
            },
            "endpoints": [
                "POST /api/v1/fields/ - Create field",
                "GET /api/v1/fields/ - List fields",
                "GET /api/v1/fields/{id} - Get field",
                "PUT /api/v1/fields/{id} - Update field",
                "DELETE /api/v1/fields/{id} - Delete field",
                "POST /api/v1/fields/validate - Validate field data",
                "GET /api/v1/fields/{id}/agricultural-context - Get agricultural context"
            ]
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "field-management",
            "version": "1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


# Export router
__all__ = ['router']
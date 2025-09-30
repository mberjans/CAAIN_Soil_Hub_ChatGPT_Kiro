"""
Address Validation API Routes
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

FastAPI routes for address validation and standardization endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Path, status
from typing import Dict, Any, List, Optional
import logging
import sys
import os
from datetime import datetime

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../services'))

from address_validation_service import (
    AddressValidationService, AddressValidationResult, AddressComponents,
    AddressValidationIssue, AddressValidationSeverity
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/address-validation", tags=["address-validation"])

# Service instance
address_validation_service = AddressValidationService()


# Pydantic models for API requests/responses
from pydantic import BaseModel, Field, validator

class AddressValidationRequest(BaseModel):
    """Request model for address validation."""
    
    address: str = Field(..., min_length=1, max_length=500, description="Address string to validate")
    include_agricultural_context: bool = Field(True, description="Include agricultural area validation")
    country: str = Field(default="US", description="Country code for validation")
    
    @validator('address')
    def validate_address(cls, v):
        if not v or not v.strip():
            raise ValueError('Address cannot be empty')
        return v.strip()

class AddressComponentsRequest(BaseModel):
    """Request model for validating address components."""
    
    street_number: Optional[str] = Field(None, description="Street number")
    street_name: Optional[str] = Field(None, description="Street name")
    street_type: Optional[str] = Field(None, description="Street type")
    street_direction: Optional[str] = Field(None, description="Street direction")
    unit_number: Optional[str] = Field(None, description="Unit number")
    city: Optional[str] = Field(None, description="City name")
    state: Optional[str] = Field(None, description="State abbreviation")
    postal_code: Optional[str] = Field(None, description="Postal code")
    country: str = Field(default="US", description="Country code")
    
    # Rural address components
    rural_route: Optional[str] = Field(None, description="Rural route number")
    box_number: Optional[str] = Field(None, description="PO Box number")
    highway_contract: Optional[str] = Field(None, description="Highway contract route")
    
    # Agricultural context
    county: Optional[str] = Field(None, description="County name")
    agricultural_district: Optional[str] = Field(None, description="Agricultural district")
    farm_service_agency: Optional[str] = Field(None, description="FSA office information")

class BatchAddressValidationRequest(BaseModel):
    """Request model for batch address validation."""
    
    addresses: List[str] = Field(..., min_items=1, max_items=100, description="List of addresses to validate")
    include_agricultural_context: bool = Field(True, description="Include agricultural area validation")
    country: str = Field(default="US", description="Country code for validation")
    
    @validator('addresses')
    def validate_addresses(cls, v):
        if not v:
            raise ValueError('At least one address is required')
        for addr in v:
            if not addr or not addr.strip():
                raise ValueError('Address cannot be empty')
        return [addr.strip() for addr in v]

class AddressValidationResponse(BaseModel):
    """Response model for address validation."""
    
    valid: bool = Field(..., description="Whether the address is valid")
    standardized_address: Optional[str] = Field(None, description="Standardized address string")
    components: Optional[Dict[str, Any]] = Field(None, description="Parsed address components")
    confidence_score: float = Field(..., description="Validation confidence score")
    
    # Validation details
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    
    # Agricultural context
    agricultural_area_verified: bool = Field(False, description="Whether location is verified agricultural area")
    agricultural_context: Optional[Dict[str, Any]] = Field(None, description="Agricultural context data")
    
    # Data sources
    validation_sources: List[str] = Field(default_factory=list, description="Sources used for validation")
    last_validated: datetime = Field(default_factory=datetime.utcnow, description="Last validation timestamp")

class BatchAddressValidationResponse(BaseModel):
    """Response model for batch address validation."""
    
    results: List[AddressValidationResponse] = Field(..., description="Validation results for each address")
    total_count: int = Field(..., description="Total number of addresses processed")
    success_count: int = Field(..., description="Number of successfully validated addresses")
    failure_count: int = Field(..., description="Number of failed validations")
    processing_time_ms: float = Field(..., description="Total processing time in milliseconds")


@router.post("/validate", response_model=AddressValidationResponse, status_code=status.HTTP_200_OK)
async def validate_address(
    request: AddressValidationRequest
) -> AddressValidationResponse:
    """
    Validate and standardize a single address.
    
    This endpoint provides comprehensive address validation including:
    - Address standardization and parsing
    - Postal code validation
    - USPS address verification (if API key configured)
    - Agricultural area verification
    - Confidence scoring
    
    Args:
        request: AddressValidationRequest with address to validate
        
    Returns:
        AddressValidationResponse with validation results
        
    Raises:
        HTTPException: If validation fails or address is invalid
    """
    try:
        logger.info(f"Validating address: {request.address}")
        
        # Perform address validation
        result = await address_validation_service.validate_and_standardize_address(
            request.address,
            request.include_agricultural_context
        )
        
        # Convert result to response format
        response = AddressValidationResponse(
            valid=result.valid,
            standardized_address=result.standardized_address,
            components=result.components.dict() if result.components else None,
            confidence_score=result.confidence_score,
            warnings=result.warnings,
            errors=result.errors,
            agricultural_area_verified=result.agricultural_area_verified,
            agricultural_context=result.agricultural_context,
            validation_sources=result.validation_sources,
            last_validated=result.last_validated
        )
        
        logger.info(f"Address validation completed: valid={result.valid}, confidence={result.confidence_score:.2f}")
        
        return response
        
    except Exception as e:
        logger.error(f"Address validation error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "error_code": "ADDRESS_VALIDATION_ERROR",
                    "error_message": f"Address validation failed: {str(e)}",
                    "agricultural_context": "Unable to validate address for agricultural location input",
                    "suggested_actions": [
                        "Verify address format is correct",
                        "Try a more complete address",
                        "Use GPS coordinates if address validation fails"
                    ]
                }
            }
        )


@router.post("/validate-components", response_model=AddressValidationResponse, status_code=status.HTTP_200_OK)
async def validate_address_components(
    request: AddressComponentsRequest
) -> AddressValidationResponse:
    """
    Validate pre-parsed address components.
    
    This endpoint validates address components that have already been parsed,
    useful for applications that parse addresses before sending to the validation service.
    
    Args:
        request: AddressComponentsRequest with address components to validate
        
    Returns:
        AddressValidationResponse with validation results
        
    Raises:
        HTTPException: If validation fails
    """
    try:
        logger.info(f"Validating address components: {request.city}, {request.state}")
        
        # Convert request to AddressComponents
        components = AddressComponents(
            street_number=request.street_number,
            street_name=request.street_name,
            street_type=request.street_type,
            street_direction=request.street_direction,
            unit_number=request.unit_number,
            city=request.city,
            state=request.state,
            postal_code=request.postal_code,
            country=request.country,
            rural_route=request.rural_route,
            box_number=request.box_number,
            highway_contract=request.highway_contract,
            county=request.county,
            agricultural_district=request.agricultural_district,
            farm_service_agency=request.farm_service_agency
        )
        
        # Perform validation
        result = await address_validation_service.validate_address_components(components)
        
        # Convert result to response format
        response = AddressValidationResponse(
            valid=result.valid,
            standardized_address=result.standardized_address,
            components=result.components.dict() if result.components else None,
            confidence_score=result.confidence_score,
            warnings=result.warnings,
            errors=result.errors,
            agricultural_area_verified=result.agricultural_area_verified,
            agricultural_context=result.agricultural_context,
            validation_sources=result.validation_sources,
            last_validated=result.last_validated
        )
        
        logger.info(f"Address components validation completed: valid={result.valid}")
        
        return response
        
    except Exception as e:
        logger.error(f"Address components validation error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "error_code": "ADDRESS_COMPONENTS_VALIDATION_ERROR",
                    "error_message": f"Address components validation failed: {str(e)}",
                    "agricultural_context": "Unable to validate address components for agricultural location",
                    "suggested_actions": [
                        "Verify all address components are correct",
                        "Ensure required fields are provided",
                        "Check component format and values"
                    ]
                }
            }
        )


@router.post("/batch-validate", response_model=BatchAddressValidationResponse, status_code=status.HTTP_200_OK)
async def batch_validate_addresses(
    request: BatchAddressValidationRequest
) -> BatchAddressValidationResponse:
    """
    Validate multiple addresses in batch.
    
    This endpoint provides efficient batch processing of multiple addresses,
    useful for bulk address validation operations.
    
    Args:
        request: BatchAddressValidationRequest with addresses to validate
        
    Returns:
        BatchAddressValidationResponse with validation results for all addresses
        
    Raises:
        HTTPException: If batch validation fails
    """
    try:
        logger.info(f"Batch validating {len(request.addresses)} addresses")
        
        start_time = datetime.utcnow()
        
        # Perform batch validation
        results = await address_validation_service.batch_validate_addresses(
            request.addresses,
            request.include_agricultural_context
        )
        
        end_time = datetime.utcnow()
        processing_time_ms = (end_time - start_time).total_seconds() * 1000
        
        # Convert results to response format
        response_results = []
        success_count = 0
        failure_count = 0
        
        for result in results:
            response_result = AddressValidationResponse(
                valid=result.valid,
                standardized_address=result.standardized_address,
                components=result.components.dict() if result.components else None,
                confidence_score=result.confidence_score,
                warnings=result.warnings,
                errors=result.errors,
                agricultural_area_verified=result.agricultural_area_verified,
                agricultural_context=result.agricultural_context,
                validation_sources=result.validation_sources,
                last_validated=result.last_validated
            )
            response_results.append(response_result)
            
            if result.valid:
                success_count += 1
            else:
                failure_count += 1
        
        response = BatchAddressValidationResponse(
            results=response_results,
            total_count=len(request.addresses),
            success_count=success_count,
            failure_count=failure_count,
            processing_time_ms=processing_time_ms
        )
        
        logger.info(f"Batch validation completed: {success_count} successful, {failure_count} failed")
        
        return response
        
    except Exception as e:
        logger.error(f"Batch address validation error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "error_code": "BATCH_ADDRESS_VALIDATION_ERROR",
                    "error_message": f"Batch address validation failed: {str(e)}",
                    "agricultural_context": "Unable to process batch address validation for agricultural locations",
                    "suggested_actions": [
                        "Verify all addresses are properly formatted",
                        "Check that address list is not too large",
                        "Try processing addresses individually if batch fails"
                    ]
                }
            }
        )


@router.get("/postal-code/{postal_code}", response_model=Dict[str, Any])
async def validate_postal_code(
    postal_code: str = Path(..., description="Postal code to validate"),
    country: str = Query("US", description="Country code")
) -> Dict[str, Any]:
    """
    Validate postal code format and lookup information.
    
    This endpoint provides postal code validation and lookup functionality,
    useful for validating postal codes before full address validation.
    
    Args:
        postal_code: Postal code to validate
        country: Country code (US, CA, etc.)
        
    Returns:
        Dict with postal code validation results
        
    Raises:
        HTTPException: If postal code validation fails
    """
    try:
        logger.info(f"Validating postal code: {postal_code} ({country})")
        
        # Use postal validator directly
        postal_validator = address_validation_service.postal_validator
        validation_result = postal_validator.validate_postal_code(postal_code, country)
        
        # Add additional lookup information if valid
        if validation_result.get("valid", False):
            lookup_info = await postal_validator.lookup_postal_code_info(postal_code, country)
            validation_result.update(lookup_info)
        
        logger.info(f"Postal code validation completed: valid={validation_result.get('valid', False)}")
        
        return validation_result
        
    except Exception as e:
        logger.error(f"Postal code validation error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "error_code": "POSTAL_CODE_VALIDATION_ERROR",
                    "error_message": f"Postal code validation failed: {str(e)}",
                    "agricultural_context": "Unable to validate postal code for agricultural location",
                    "suggested_actions": [
                        "Verify postal code format is correct",
                        "Check postal code exists in database",
                        "Use correct country code for postal code"
                    ]
                }
            }
        )


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for the address validation service.
    
    Returns:
        Dict with service status and basic information
    """
    try:
        # Test basic service functionality
        test_result = await address_validation_service.validate_and_standardize_address(
            "123 Main St, Ames, IA 50010"
        )
        
        return {
            "status": "healthy",
            "service": "address-validation",
            "version": "1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "test_validation": {
                "test_address": "123 Main St, Ames, IA 50010",
                "validation_successful": test_result.valid,
                "confidence_score": test_result.confidence_score
            },
            "endpoints": [
                "POST /api/v1/address-validation/validate - Validate single address",
                "POST /api/v1/address-validation/validate-components - Validate address components",
                "POST /api/v1/address-validation/batch-validate - Batch validate addresses",
                "GET /api/v1/address-validation/postal-code/{code} - Validate postal code"
            ],
            "features": [
                "Address standardization",
                "Postal code validation",
                "USPS integration",
                "Agricultural area verification",
                "Batch processing",
                "Confidence scoring"
            ]
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "address-validation",
            "version": "1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


# Export router
__all__ = ['router']
